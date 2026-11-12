"""Every Claude API call the app makes: generation, grading, lookups, and the study coach."""
import json
import os
import re
import sys

import anthropic

from . import db, usage

# Models that accept server-side refusal fallbacks.
FALLBACK_MODELS = {"claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1"}

EXERCISE_TYPES = ["fill_blank", "multiple_choice", "translate_to_german", "translate_to_native",
                  "conjugation", "word_order", "short_answer"]


class AIError(Exception):
    pass


S, I, B = {"type": "string"}, {"type": "integer"}, {"type": "boolean"}


def _obj(props):
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def _arr(items):
    return {"type": "array", "items": items}


def _enum(values):
    return {"type": "string", "enum": list(values)}


def _client():
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise AIError("No Claude API key yet. Add one under Settings.")
    return anthropic.Anthropic(api_key=key)


def _learner(s):
    return (f"The learner studies German at CEFR level {s['level']}. Their native language is "
            f"{s['native_language']}; write translations, instructions and explanations in {s['native_language']}.")


def _web_search_tool(model):
    if model.startswith("claude-haiku"):
        return {"type": "web_search_20250305", "name": "web_search", "max_uses": 5}
    return {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}


def _parse_json(text, texts):
    for candidate in [text] + texts[::-1]:
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, TypeError):
            pass
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    raise AIError("Couldn't read the AI's response. Please try again.")


def call(system, content, schema=None, effort=None, web=False, history=None, max_tokens=16000):
    feature = sys._getframe(1).f_code.co_name  # the helper that called us, e.g. generate_exercises, for the cost meter
    usage.check_budget()
    s = db.get_settings()
    model = s["model"]
    messages = list(history or []) + [{"role": "user", "content": content}]
    output_config = {"effort": effort or s["effort"]}
    if schema:
        output_config["format"] = {"type": "json_schema", "schema": schema}
    kwargs = {"model": model, "max_tokens": max_tokens, "system": system, "output_config": output_config}
    if web and s.get("web_search") == "1":
        kwargs["tools"] = [_web_search_tool(model)]
    client = _client()
    try:
        for _ in range(6):
            if model in FALLBACK_MODELS:
                resp = client.beta.messages.create(
                    messages=messages, betas=["server-side-fallback-2026-07-01"],
                    fallbacks="default", **kwargs)
            else:
                resp = client.messages.create(messages=messages, **kwargs)
            try:
                usage.log_claude(feature, resp)
            except Exception as e:  # the cost meter must never break a feature
                print("usage log failed:", e)
            if resp.stop_reason != "pause_turn":
                break
            messages = messages + [{"role": "assistant", "content": resp.content}]
    except anthropic.AuthenticationError:
        raise AIError("The API key was rejected. Check it under Settings.")
    except anthropic.PermissionDeniedError as e:
        raise AIError(f"Permission denied by the API: {e.message}")
    except anthropic.NotFoundError:
        raise AIError(f"Model '{model}' wasn't found. Pick another model under Settings.")
    except anthropic.RateLimitError:
        raise AIError("Rate limited by the API. Wait a minute and try again.")
    except anthropic.BadRequestError as e:
        raise AIError(f"The API rejected the request: {e.message}")
    except anthropic.APIStatusError as e:
        raise AIError(f"API error {e.status_code}: {e.message}")
    except anthropic.APIConnectionError:
        raise AIError("Couldn't reach the Claude API. Check your internet connection.")

    if resp.stop_reason == "refusal":
        raise AIError("Claude declined this request.")
    if resp.stop_reason == "max_tokens":
        raise AIError("The response was too long and got cut off. Try asking for fewer items.")
    texts = [b.text for b in resp.content if b.type == "text"]
    text = "".join(texts).strip()
    return _parse_json(text, texts) if schema else text


def _chapter_block(title, text):
    # Cached so generating exercises and then cards from the same chapter doesn't pay for the text twice.
    return {"type": "text", "text": f"<chapter title=\"{title}\">\n{text}\n</chapter>",
            "cache_control": {"type": "ephemeral"}}


EXERCISE_SCHEMA = _obj({"exercises": _arr(_obj({
    "type": _enum(EXERCISE_TYPES), "topic": S, "instructions": S, "prompt": S,
    "options": _arr(S), "answer": S, "explanation": S}))})
CARD_SCHEMA = _obj({"cards": _arr(_obj({
    "type": _enum(["vocab", "cloze", "verb", "phrase"]), "front": S, "back": S, "extra": S,
    "tags": _arr(S)}))})
EXERCISE_RULES = (
    "- topic: a short grammar or vocabulary label in English, e.g. 'Dativ articles', 'Perfekt with sein', "
    "'food vocabulary'. Reuse the same label for the same topic.\n"
    "- fill_blank: mark each gap with ___ (one gap per exercise).\n"
    "- multiple_choice: 3-4 options; answer is the exact text of the correct option. Other types: options = [].\n"
    "- answer: the expected answer. If several answers are fully correct, separate them with ' | '.\n"
    "- explanation: one or two sentences on why the answer is right.")
CARD_RULES = (
    "Card formats:\n"
    "- vocab: front = German with article and plural for nouns ('der Tisch, -e'), back = meaning; "
    "extra = a short German example sentence with its translation.\n"
    "- verb: front = infinitive, back = meaning + principal parts ('gehen - ging - ist gegangen'); "
    "note irregular present forms in extra.\n"
    "- cloze: front = a German sentence with one gap written as ___ plus a hint in brackets, "
    "back = the missing word(s); extra = the full sentence and its translation.\n"
    "- phrase: front = useful German chunk or expression, back = meaning; extra = when to use it.\n"
    "Tags: short topic labels such as 'Dativ', 'food'.")


def generate_exercises(title, text, count, focus):
    s = db.get_settings()
    schema = EXERCISE_SCHEMA
    system = ("You are an experienced teacher of German as a foreign language who writes practice material "
              "that matches a specific textbook chapter. " + _learner(s))
    task = (
        f"Write {count} NEW practice exercises for this chapter. They must practise the chapter's vocabulary and "
        "grammar at the learner's level, in a mix of types similar to what the book uses. Don't copy the book's "
        "own exercises; write fresh items.\n"
        f"{'Focus especially on: ' + focus if focus else ''}\n"
        "Rules:\n" + EXERCISE_RULES)
    data = call(system, [_chapter_block(title, text), {"type": "text", "text": task}], schema)
    return data["exercises"]


def generate_cards(title, text, count, existing_fronts, focus):
    s = db.get_settings()
    system = "You make excellent spaced-repetition flashcards for learners of German. " + _learner(s)
    existing = "\n".join(existing_fronts[:300]) or "(none)"
    task = (
        f"Make {count} flashcards from the most useful vocabulary, phrases and grammar in this chapter.\n"
        f"{'Focus especially on: ' + focus if focus else ''}\n"
        + CARD_RULES + " Prefer words that are actually taught in the chapter.\n"
        f"Don't duplicate these existing cards:\n{existing}")
    data = call(system, [_chapter_block(title, text), {"type": "text", "text": task}], CARD_SCHEMA)
    return data["cards"]


def convert_import(kind, text, chapter_title):
    """Turn material pasted from another tool (e.g. Gemini Notebook) into flashcards or exercises."""
    s = db.get_settings()
    system = "You convert study material from other tools into this German study app's formats. " + _learner(s)
    rules = CARD_RULES if kind == "cards" else "Exercise rules:\n" + EXERCISE_RULES
    task = (
        f"The learner pasted this material, made by another study tool for the chapter '{chapter_title}'. "
        f"Convert ALL of it into {'flashcards' if kind == 'cards' else 'exercises'} for this app. Keep the content "
        "faithful; only fix clear mistakes and fill in missing pieces (articles, plurals, translations, "
        "explanations). Ignore anything that isn't study content.\n" + rules
        + f"\n\n<material>\n{text}\n</material>")
    data = call(system, task, CARD_SCHEMA if kind == "cards" else EXERCISE_SCHEMA)
    return data["cards" if kind == "cards" else "exercises"]


def recover_questions(page_text, items):
    """For older mistakes saved without their question: find each item on the page and return its full text.
    items: [{id, exercise, wrong, correct}] -> {id: {question, corrected_sentence}}"""
    s = db.get_settings()
    schema = _obj({"items": _arr(_obj({"id": I, "question": S, "corrected_sentence": S}))})
    system = "You help a German learner's study app reconstruct textbook exercises. " + _learner(s)
    task = (
        "Below is the text of a textbook page and some answers a learner got wrong on it, each with a reference "
        "to the exercise item (e.g. '3.2 item 4'). For each one, find the item on the page and return:\n"
        "- question: the exercise instruction as printed, then on a new line the complete sentence of that item with the gap "
        "the learner got wrong written as ___ (fill any other gaps in the sentence correctly).\n"
        "- corrected_sentence: the same sentence with the correct answer filled in.\n"
        "If you can't find an item, build the most likely sentence from the page's content.\n\n"
        f"<page>\n{page_text}\n</page>\n\n<mistakes>\n{json.dumps(items, ensure_ascii=False)}\n</mistakes>")
    return {r["id"]: r for r in call(system, task, schema, effort="low")["items"]}


def drill_mistakes(mistakes, count):
    """New exercises that target the learner's own past mistakes."""
    s = db.get_settings()
    system = ("You are an experienced teacher of German as a foreign language. You write short, focused drills "
              "that fix a learner's recurring mistakes. " + _learner(s))
    task = (
        f"Here are mistakes this learner made: the original task (question), what they wrote, the correct answer "
        f"and the corrected sentence. Write {count} NEW exercises that practise exactly the rules and words behind "
        "them. Don't reuse the original sentences; make fresh ones of the same exercise type and difficulty. "
        "Every exercise must be fully self-contained: a clear instruction plus a complete sentence, never a lone "
        "word or a reference to the textbook. Spread the "
        "exercises over all the mistakes, and use more items for the topics that appear most often.\n"
        "Exercise rules:\n" + EXERCISE_RULES
        + f"\n\n<mistakes>\n{json.dumps(mistakes, ensure_ascii=False, indent=1)}\n</mistakes>")
    return call(system, task, EXERCISE_SCHEMA)["exercises"]


EPISODE_STYLES = {
    "dialogue": "a natural everyday dialogue between two people that uses the chapter's situations and words",
    "podcast": "a friendly two-host learner podcast: the hosts chat in German about the chapter's topic and "
               "naturally explain or rephrase a few tricky words in simple German",
    "story": "a short story told by one narrator, using the chapter's vocabulary and grammar",
}


def write_episode(title, text, minutes, style, focus):
    s = db.get_settings()
    speakers = 1 if style == "story" else 2
    schema = _obj({
        "title": S, "summary": S,
        "speakers": _arr(_obj({"name": S, "description": S})),
        "turns": _arr(_obj({"speaker": S, "text": S, "translation": S, "style": S})),
        "vocabulary": _arr(_obj({"german": S, "meaning": S})),
        "questions": _arr(_obj({"question": S, "answer": S})),
    })
    system = ("You write German listening practice that will be turned into audio. You write for the ear: "
              "natural spoken German, clear sentences, no stage directions in the text. " + _learner(s))
    task = (
        f"Write {EPISODE_STYLES.get(style, EPISODE_STYLES['dialogue'])}.\n"
        f"Length: about {minutes} minutes spoken, so roughly {minutes * 110} words in total.\n"
        f"{'Focus especially on: ' + focus if focus else ''}\n"
        f"- Exactly {speakers} speaker(s), with simple German first names. Each turn's speaker must be one of them.\n"
        "- Language level must match the learner's level; recycle the chapter's vocabulary and grammar often.\n"
        "- turns: one or a few sentences each. translation: the turn in the learner's language. style: a short "
        "delivery hint in English for the voice actor, e.g. 'cheerful', 'surprised', 'slow and clear'.\n"
        "- title: a short German title. summary: one sentence in the learner's language.\n"
        "- vocabulary: 8-12 useful words or phrases from the episode with meanings.\n"
        "- questions: 4 comprehension questions in German with short answers.")
    return call(system, [_chapter_block(title, text), {"type": "text", "text": task}], schema)


def grade_answers(items):
    """items: [{id, type, prompt, options, expected, user}] -> {id: {correct, feedback}}"""
    s = db.get_settings()
    schema = _obj({"results": _arr(_obj({"id": I, "correct": B, "feedback": S}))})
    system = "You grade German exercises fairly and explain mistakes clearly and briefly. " + _learner(s)
    task = (
        "Grade each learner answer. Accept any answer that is genuinely correct German for the task, even if it "
        "differs from the expected answer. Ignore capitalisation and punctuation unless that is what the exercise "
        "tests. feedback: one or two sentences. If wrong, say what the error is and why; if right, confirm "
        "briefly or add a useful nuance.\n\n" + json.dumps(items, ensure_ascii=False))
    data = call(system, task, schema, effort="low")
    return {r["id"]: r for r in data["results"]}


def check_page(image_b64, page_text):
    s = db.get_settings()
    schema = _obj({
        "summary": S,
        "items": _arr(_obj({
            "exercise": S, "question": S, "student_answer": S,
            "verdict": _enum(["correct", "partly", "incorrect", "unclear"]),
            "correction": S, "corrected_sentence": S, "explanation": S, "topic": S}))})
    system = ("You are a German teacher marking a student's textbook page. The student wrote answers on the page "
              "by typing (blue text boxes) and by hand with a pen. " + _learner(s))
    task = (
        "Look at the page image. Find every answer the student wrote and mark it. Ignore exercises the student "
        "hasn't attempted. For each answer give: which exercise/item it belongs to (e.g. '3b'), what the student "
        "wrote, a verdict, the corrected answer, a short explanation, and a short English grammar/vocab topic "
        "label. If handwriting is unreadable, use verdict 'unclear'.\n"
        "question: the full task so it can be understood on its own later: the exercise instruction as printed "
        "(e.g. 'Ergänzen Sie die Possessivartikel.'), then on a new line the complete sentence of this item, with the "
        "gap the student filled written as ___ (keep other gaps' printed text or fill them correctly).\n"
        "corrected_sentence: that same sentence with the correct answer filled in.\n"
        "summary: two or three sentences on overall "
        "performance and what to review.\n\nThe page's printed text, to help you read it:\n" + page_text[:20000])
    content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
               {"type": "text", "text": task}]
    return call(system, content, schema)


def lookup(word, sentence):
    s = db.get_settings()
    schema = _obj({
        "lemma": S, "part_of_speech": S, "article": S, "plural": S, "meaning": S, "forms": S,
        "meaning_in_context": S, "example": S, "example_translation": S, "note": S})
    system = "You are a precise German-learner's dictionary. " + _learner(s)
    task = (f"Word or phrase: {word}\nSentence it appears in: {sentence or '(none)'}\n\n"
            "Give the dictionary form (lemma). article: der/die/das for nouns, otherwise ''. plural: for nouns, "
            "otherwise ''. forms: key forms (verb principal parts, comparative, etc.) or ''. meaning_in_context: what "
            "it means in this sentence, including the grammar of the form used (e.g. 'dative plural'). note: any "
            "trap or tip for learners, or ''.")
    return call(system, task, schema, effort="low")


def explain(text, context):
    s = db.get_settings()
    system = ("You are a patient German tutor. Explain clearly and concisely using short Markdown "
              "(bold, bullet lists). " + _learner(s))
    task = (f"Explain this passage from my textbook: translate it, then explain the important grammar and any "
            f"tricky words.\n\nPassage:\n{text}\n\nSurrounding page text for context:\n{context[:6000]}")
    return call(system, task, effort="low")


def decl_reading(brief, topic):
    """A short gap-fill text for one stage of the Declensions course."""
    s = db.get_settings()
    system = "You write short German practice texts for a learner who is drilling declension endings. " + _learner(s)
    task = (
        f"Write a new German text of 90-130 words for this stage of a declension course: {brief['focus']}\n"
        + (f"Topic the learner asked for: {topic}\n" if topic else "Pick an everyday topic.\n")
        + "Use vocabulary at or below the learner's level. Turn 10-14 words or endings that practise this stage into gaps, "
        "written exactly like this: {answer|hint}. For a whole word the hint is its meaning in "
        f"{s['native_language']} (one or two words), e.g. in English 'Ich sehe {{den|the}} Mann.' For an ending, attach the gap to the stem and leave the hint empty, e.g. "
        "'ein klein{es|} Kind'. Each gap must have exactly one correct answer given the rest of the sentence, so make "
        "the gender and case clear from context, and avoid gaps after prepositions that would normally contract "
        "(im, zum, beim). Do not use braces for anything else. This example shows the style and the kind of gaps wanted:\n\n"
        + brief["example"] + "\n\ntitle: a short German title. text: the text with its gaps.")
    return call(system, task, _obj({"title": S, "text": S}), effort="low")


def classify_mistakes(rows, nouns):
    """Which declension skills (keys of the app's rule engine) each mistake is about."""
    system = "You are a precise German grammar analyst. You map learners' mistakes onto a fixed list of declension skills."
    task = (
        "For each mistake below, list the declension skills it shows the learner hasn't mastered, as skill keys. "
        "Use [] when the mistake isn't about declension (verb forms, word order, spelling, vocabulary meaning, tenses...). "
        "At most 4 keys per mistake; pick the exact form the learner got wrong, judged from the question and the "
        "correct answer.\n\nKey formats (case: nom, akk, dat, gen; gender: m, f, n, pl):\n"
        "- def:CASE:GENDER  der/die/das article\n- dies:CASE:GENDER  dieser, jeder, welcher, mancher, alle\n"
        "- ein:CASE:GENDER  ein, kein\n- poss:CASE:GENDER  mein, dein, sein, ihr, unser, euer, Ihr (gender = the thing owned)\n"
        "- adjw:CASE:GENDER adjective ending after a der-word; adjm:CASE:GENDER after an ein-word; adjs:CASE:GENDER with no article\n"
        "- pers:akk:P or pers:dat:P personal pronoun, P one of ich du er sie es wir ihr pl Sie (pl = sie meaning they)\n"
        "- refl:akk:P or refl:dat:P reflexive pronoun, P one of ich du 3 wir ihr (3 = every sich form)\n"
        "- rel:CASE:GENDER relative pronoun\n- wer:CASE  wer, wen, wem, wessen\n"
        "- noun:dat:pl (dative plural -n), noun:gen:m, noun:gen:n (genitive -s/-es), noun:akk:weak, noun:dat:weak, noun:gen:weak (weak nouns like Student)\n"
        "- trig:p:PREP choosing the case after a fixed-case preposition: durch für gegen ohne um aus außer bei mit nach seit von zu "
        "gegenüber wegen trotz während statt innerhalb außerhalb\n"
        "- trig:v:VERB the case a verb takes: helfen danken gehören gefallen antworten glauben folgen gratulieren vertrauen zuhören "
        "schmecken passen sehen kaufen brauchen kennen besuchen haben\n"
        "- trig:w:PREP:wo or trig:w:PREP:wohin two-way prepositions: an auf hinter in neben über unter vor zwischen\n"
        "- gender:NOUN or plural:NOUN only for these nouns: " + ", ".join(nouns) + "\n\n"
        "Example: wrong 'mit seine Schwester', correct 'mit seiner Schwester' -> [\"poss:dat:f\", \"trig:p:mit\"].\n\n"
        f"<mistakes>\n{json.dumps(rows, ensure_ascii=False, indent=1)}\n</mistakes>")
    schema = _obj({"items": _arr(_obj({"id": I, "skills": _arr(S)}))})
    return {r["id"]: r["skills"] for r in call(system, task, schema, effort="low")["items"]}


WRITING_CRITERIA = ["Task completion", "Coherence", "Vocabulary", "Grammar"]


def grade_writing(task, text, level, words):
    """Marks a piece of writing the way the Goethe-Zertifikat writing paper does."""
    s = db.get_settings()
    system = ("You are an experienced, fair examiner for the Goethe-Zertifikat writing paper and a supportive German "
              "teacher. " + _learner(s))
    brief = (f"Title: {task.get('title') or 'Free writing'}\nType: {task.get('kind') or 'any'}\n"
             f"Task: {task.get('task') or 'The learner chose their own topic.'}\n"
             + ("Points to cover:\n" + "\n".join(f"- {p}" for p in task["points"]) + "\n" if task.get("points") else "")
             + (f"Target length: about {task['words']} words\n" if task.get("words") else ""))
    task_text = (
        f"Mark this text as a {level} exam answer. It has {words} words.\n\n<task>\n{brief}</task>\n\n"
        f"<text>\n{text}\n</text>\n\n"
        "criteria: exactly these four, in this order, each scored 0-5 for the target level with one or two sentences "
        f"of comment in {s['native_language']}: " + ", ".join(WRITING_CRITERIA) + ". Task completion covers every point "
        "of the task, the right register (du/Sie, greeting and closing) and length.\n"
        "overall: 0-100. passes: whether this would pass the writing paper at this level (roughly 60 or more).\n"
        "verdict: one encouraging sentence on how it went.\n"
        "corrections: every real error, at most 20, most important first. original = the exact text copied character "
        "for character from the learner's text (a few words, enough to be unique); corrected = the fixed version of "
        "that same span; explanation = one short sentence in the learner's language; topic = a short grammar label like "
        "'Dativ articles' or 'verb position'; category = grammar, vocabulary, spelling, word_order or style. Don't "
        "list style suggestions unless they matter at this level.\n"
        "improved: the whole text corrected and lightly improved, keeping the learner's ideas and level.\n"
        "tips: two or three concrete things to do better next time.")
    crit = _obj({"name": _enum(WRITING_CRITERIA), "score": I, "comment": S})
    corr = _obj({"original": S, "corrected": S, "explanation": S, "topic": S,
                 "category": _enum(["grammar", "vocabulary", "spelling", "word_order", "style"])})
    schema = _obj({"overall": I, "passes": B, "verdict": S, "criteria": _arr(crit), "corrections": _arr(corr),
                   "improved": S, "tips": _arr(S)})
    return call(system, task_text, schema, effort="medium")


def writing_task(level, topic):
    """A new exam-style writing task."""
    s = db.get_settings()
    system = "You write exam-style German writing tasks in the format of the Goethe-Zertifikat. " + _learner(s)
    task = (f"Write one new writing task for level {level}" + (f" about: {topic}" if topic else "") + ". "
            "Choose a format that fits the level (B1: informal email, forum post, short formal message; B2: forum post, "
            "formal letter; C1: argumentative essay, opinion piece, formal letter). The task and points are in German, "
            "addressing the learner with Sie. kind is the format in English. words is the target length "
            "(B1 40-80, B2 100-150, C1 200-250); minutes is the exam time for it.")
    schema = _obj({"title": S, "kind": S, "task": S, "points": _arr(S), "words": I, "minutes": I})
    return call(system, task, schema, effort="low")


# ---------- Study coach ----------

PLAN_KINDS = ["reader", "practice", "flashcards", "mistakes", "declensions", "video", "listening", "speaking", "writing", "other"]

COACH_SYSTEM = (
    "You are the learner's personal German study coach. You see their data from their study app: a PDF reader "
    "where they read and do textbook exercises, AI-generated practice sets, and flashcards with spaced repetition. "
    "You plan their study by combining that app with outside resources (videos, podcasts, speaking and writing "
    "practice). Be concrete and measurable, encouraging but honest. Base decisions on the data: work through the "
    "current chapter in order, target weak topics, keep the flashcard backlog under control, and balance input "
    "(reading, listening) with output (speaking, writing). Never invent URLs. Only give a URL if it is in the "
    "learner's resource list or you found it with web search in this conversation.")


def make_plan(context, minutes, note):
    s = db.get_settings()
    block = _obj({
        "kind": _enum(PLAN_KINDS), "title": S, "instructions": S, "why": S, "minutes": I,
        "target_pages": I, "target_questions": I, "target_cards": I,
        "book_id": I, "chapter_id": I, "start_page": I, "media_id": I, "url": S, "search_query": S})
    schema = _obj({"summary": S, "blocks": _arr(block), "learner_profile": S})
    web = s.get("web_search") == "1"
    task = (
        f"Make today's study plan. Time available: about {minutes} minutes.\n"
        f"{'Note from the learner: ' + note if note else ''}\n\n"
        "Rules for blocks:\n"
        "- 3-6 blocks in order; minutes must add up to roughly the time available.\n"
        "- reader: reading and doing exercises in the textbook inside the app. Set book_id, chapter_id, start_page "
        "and give target_pages and target_questions (questions answered on the page and checked).\n"
        "- practice: AI practice set for a chapter. Set book_id/chapter_id and target_questions.\n"
        "- flashcards: review in the app; set target_cards (cover due cards first).\n"
        "- mistakes: when the mistake_book shows a topic the learner keeps getting wrong, a short block where they "
        "open the Mistakes page and drill that topic. Name the topic in the title; set target_questions.\n"
        "- writing: the app's Writing desk. Put the exact task in instructions (in German, the way an exam task is "
        "written: situation, 3-4 points to cover, target number of words for the learner's level). Claude marks it "
        "like the Goethe writing paper and its corrections go to the Mistake Book. writing_desk shows recent scores.\n"
        "- declensions: the Declensions page. It has a guided course (declension_course: planets unlocked in order, "
        "each with a briefing, charts, a drill, a reading, flashcards and a checkpoint) and free rule-based drills. "
        "Declensions need daily repetition until they are automatic, so include a block of 10-20 minutes most days: "
        "tell the learner which steps of the current planet to do (or to take its checkpoint), and once the course is "
        "finished, to drill the weakest areas in declension_trainer. Set target_questions at about 3 per minute.\n"
        "- listening with the app's own audio: if listening_library has an episode that fits (same chapter, few "
        "listens), make a listening block with its media_id and tell the learner how to use it (listen without "
        "the transcript first, then with it, then shadow). If a chapter has no episode yet, you may tell them to "
        "make one on the Listening page (choose dialogue, podcast or story).\n"
        "- video / listening / speaking / other: outside activities. Give clear instructions on what to do "
        "and how to do it actively (e.g. shadow 5 sentences, write down 8 new words, record yourself).\n"
        + ("- For video/listening, search the web for one specific real video or episode that matches the topic and "
           "the learner's level, and put its URL in url.\n" if web else
           "- For video/listening, use a resource from the learner's list in url if one fits; otherwise url = ''.\n")
        + "- If url is empty, put a good search query in search_query (in German where useful); else search_query = ''.\n"
        "- Unused numeric fields = 0, unused strings = ''.\n"
        "- why: one sentence linking the block to the learner's data.\n"
        "summary: two or three sentences on the focus of today.\n"
        "learner_profile: your updated running notes about this learner (strengths, weaknesses, habits, what to "
        "focus on next). Keep what is still true from the old notes. Max 150 words.\n\n"
        f"Learner data:\n{json.dumps(context, ensure_ascii=False, indent=1)}")
    return call(COACH_SYSTEM + " " + _learner(s), task, schema, effort="medium", web=True)


def coach_reply(context, history, message):
    s = db.get_settings()
    system = (COACH_SYSTEM + " " + _learner(s) + " Reply conversationally in short Markdown. The learner can "
              "generate a structured daily plan with the 'Plan my day' button on the Today page; suggest it when "
              f"useful.\n\nCurrent learner data:\n{json.dumps(context, ensure_ascii=False)}")
    return call(system, message, history=history, effort="medium", web=True)
