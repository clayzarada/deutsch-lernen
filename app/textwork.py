"""Free practice made from the learner's own textbook text, using the offline dictionary (no AI):

- words(text): the chapter's vocabulary, in the order it appears, with gender, plural and meaning, ready to
  become flashcards.
- gapfills(text, kind, n): real sentences from the chapter with one word blanked out: articles and other
  der/ein-words, adjective endings, or verb forms. Marked by exact match with what the book printed.
"""
import random
import re

from . import dictionary

ENGLISH = {"the", "and", "of", "to", "is", "are", "you", "your", "with", "this", "that", "for", "following", "use",
           "which", "what", "in", "on", "be", "it", "or", "write", "answer", "fill", "complete", "translate"}
GERMAN = {"der", "die", "das", "und", "ist", "ich", "du", "er", "sie", "es", "wir", "ihr", "nicht", "ein", "eine",
          "mit", "zu", "auf", "den", "dem", "des", "von", "sich", "hat", "haben", "sind", "war", "im", "auch", "noch",
          "aber", "wie", "was", "kann", "wird", "nach", "bei", "für", "aus", "um", "mein", "mich", "mir", "man"}
WORD = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
ENDINGS = ("em", "en", "er", "es", "e")
DER_WORDS = ("dies", "jed", "welch", "jen", "manch")
EIN_WORDS = ("ein", "kein", "mein", "dein", "sein", "ihr", "unser", "eur", "Ihr")


def _unhyphen(text):
    """Joins words split over two lines ("Woh-\\nnung"), drops page markers and lines that aren't German
    (textbooks mix English explanations and headings in between the German examples)."""
    text = re.sub(r"--- Seite \d+ ---", "\n", text)
    text = re.sub(r"([a-zäöüß])-\n\s*([a-zäöüß])", r"\1\2", text)
    keep = []
    for line in text.split("\n"):
        ws = [w for w in WORD.findall(line) if len(w) > 1]
        if not ws or sum(dictionary.known(w) or dictionary.known(w.lower()) for w in ws) >= .75 * len(ws):
            keep.append(line)
        else:
            keep.append("")  # a break, so the German around it doesn't join across the English line
    return "\n".join(keep)


def sentences(text):
    """German sentences from a chapter: 4-30 words, no blanks to fill in, not English instructions."""
    text = _unhyphen(text)
    out = []
    for chunk in re.split(r"(?<=[.!?])\s+|\n\s*\n", text):
        s = re.sub(r"\s+", " ", chunk).strip()
        s = re.sub(r"^(\d+[.)]?|[a-h][.)]|[•●▪–-])\s+", "", s)
        s = re.sub(r"^[A-Za-zÄÖÜäöü]+:\s+", "", s)  # "Example: ...", "Beispiel: ..."
        words = WORD.findall(s)
        if not 4 <= len(words) <= 30 or any(c in s for c in "_…/→=") or "..." in s or not s[:1].isupper():
            continue
        low = [w.lower() for w in words]
        if sum(w in ENGLISH for w in low) > 1 or not any(w in GERMAN for w in low):
            continue
        if s[-1] not in ".!?":
            continue
        out.append(s)
    return list(dict.fromkeys(out))


# ---------- chapter vocabulary ----------
SKIP_POS = {"article", "det", "pron", "conj", "prep", "particle", "intj", "contraction", "num", "postp"}


def words(text, known=(), min_rank=150):
    """The chapter's words in order of appearance: [{word, article, plural, pos_name, meaning, forms, example,
    count, rank, have}]. Very common words (rank <= min_rank: sein, haben, und...) are left out, and so are names."""
    sents = sentences(text)
    known = {k.lower() for k in known}
    found, order = {}, []
    for tok in WORD.findall(" ".join(sents)):  # German sentences only: textbooks explain in English too
        if len(tok) < 3 or (tok.isupper() and len(tok) > 1):
            continue
        e = (dictionary.lookup(tok, 1) or [None])[0]
        if not e or e["pos"] in SKIP_POS or e.get("grammar"):
            continue
        if re.search(r"given name|surname|placename|place name|city|country in", e["meanings"][0]):
            continue  # names
        if e["rank"] and e["rank"] <= min_rank:
            continue
        key = (e["word"], e["pos"])
        if key not in found:
            found[key] = {"word": e["word"], "article": e["article"], "plural": e["plural"], "pos": e["pos"],
                          "pos_name": e["pos_name"], "meaning": e.get("short") or dictionary.short(e["meanings"]), "forms": e["forms_text"],
                          "rank": e["rank"], "count": 0, "example": "",
                          "have": e["word"].lower() in known}
            order.append(key)
        w = found[key]
        w["count"] += 1
        if not w["example"]:
            w["example"] = next((s for s in sents if re.search(rf"\b{re.escape(tok)}\b", s) and len(s) <= 180), "")
    return [found[k] for k in order]


def card_for(w):
    """A flashcard for a word from words()."""
    front = f"{w['article']} {w['word']}".strip()
    extra = "\n".join(x for x in (w["plural"] and f"Plural: die {w['plural']}" if w["pos"] == "noun" else w["forms"],
                                  w["example"]) if x)
    return {"type": "verb" if w["pos"] == "verb" else "vocab", "front": front, "back": w["meaning"], "extra": extra,
            "tags": ["dictionary", w["pos"]]}


# ---------- gap-fills from the book ----------
def _article_gap(tok):
    low = tok.lower()
    if low in ("der", "die", "das", "den", "dem", "des"):
        return tok[0] + "___", [tok, low[1:]]
    for stem in DER_WORDS:
        if low.startswith(stem) and low[len(stem):] in ENDINGS:
            return tok[:len(stem)] + "___", [tok, low[len(stem):]]
    for stem in EIN_WORDS:
        rest = low[len(stem):] if low.startswith(stem.lower()) else None
        if rest is not None and (rest in ENDINGS or rest == ""):
            if stem == "ihr" and rest == "":  # "ihr" alone is usually the pronoun (you all)
                return None
            if stem == "sein" and rest == "":
                continue
            return tok[:len(stem)] + "___", [tok, rest or "-", "(none)", "nothing", "x"] if rest == "" else [tok, rest]
    return None


def _adjective_gap(tok, nxt):
    if not tok.islower() or not nxt or not nxt[:1].isupper():
        return None
    e = (dictionary.lookup(tok, 1) or [None])[0]
    if not e or e["pos"] != "adj" or e["word"] == tok:
        return None
    lemma = e["word"]
    stems = {lemma, lemma[:-1] if lemma.endswith("e") else lemma, re.sub(r"e([lr])$", r"\1", lemma),
             e["info"].get("comp", "")} - {""}
    for end in ENDINGS:
        if tok.endswith(end) and tok[: -len(end)] in stems:
            return tok[: -len(end)] + "___", [end, tok], lemma
    return None


AUX = {"hat", "habe", "hast", "haben", "habt", "hatte", "hatten", "hattest", "ist", "bin", "bist", "sind", "seid",
       "war", "waren", "warst", "wird", "werde", "wirst", "werden", "werdet", "wurde", "wurden", "worden"}


def _verb_gap(tok, sentence_words=()):
    if not tok.islower() or len(tok) < 3:
        return None
    e = (dictionary.lookup(tok, 1) or [None])[0]
    if not e or e["pos"] != "verb" or e["word"] == tok:
        return None
    i = e["info"]
    p = (i.get("praet") or "").split(" ")[0]
    if i.get("pp") and tok == i["pp"] and (tok != i.get("pres3") or AUX & set(sentence_words)):
        tense = "Partizip II"  # (reparieren: "repariert" is also er repariert, so look for haben/sein/werden)
    elif p and tok in {p, p + "st", p + "n", p + "en", p + "t", p + "est"}:
        tense = "Präteritum"
    else:
        tense = "Präsens"
    return "___", [tok], f"{e['word']}, {tense}"


KINDS = {"articles": "Articles and endings: der, ein, mein, dieser...", "adjectives": "Adjective endings",
         "verbs": "Verb forms"}


def gapfills(text, kind="mixed", n=10, seed=None):
    """[{sentence: (before, gap, after), cue, answers, solution, kind}] from real sentences of the chapter."""
    rnd = random.Random(seed)
    pool = {k: [] for k in KINDS}
    for s in sentences(text):
        toks = [(m.group(0), m.start(), m.end()) for m in WORD.finditer(s)]
        for i, (tok, a, b) in enumerate(toks):
            nxt = toks[i + 1][0] if i + 1 < len(toks) else ""
            hit = None
            if (g := _article_gap(tok)) and nxt[:1].isupper():
                hit = ("articles", g[0], g[1], "")
            elif g := _adjective_gap(tok, nxt):
                hit = ("adjectives", g[0], g[1], g[2])
            elif i > 0 and not nxt[:1].isupper() and (g := _verb_gap(tok, [t[0].lower() for t in toks])):
                # (a verb form right before a noun is usually a participle used as an adjective)
                hit = ("verbs", g[0], g[1], g[2])
            if hit:
                k, shown, answers, cue = hit
                pool[k].append({"kind": k, "before": s[:a], "gap": shown, "after": s[b:], "cue": cue,
                                "answers": answers, "solution": tok, "sentence": s})
    kinds = [kind] if kind in KINDS else [k for k in KINDS if pool[k]]
    items, used = [], set()
    for _ in range(n * 4):
        if len(items) >= n or not kinds:
            break
        k = rnd.choice(kinds)
        cands = [x for x in pool[k] if x["sentence"] not in used]
        if not cands:
            kinds.remove(k)
            continue
        x = rnd.choice(cands)
        used.add(x["sentence"])
        items.append(x)
    return {"items": items, "available": {k: len(v) for k, v in pool.items()}}
