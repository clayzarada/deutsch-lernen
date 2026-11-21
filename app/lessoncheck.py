"""Checks the course lessons against the app's own dictionary: noun genders, verbs, and every German word in the
dialogues, examples and exercise answers. Run `python -m app.lessoncheck` for a report; tests/test_levels.py
fails when anything here is reported.
"""
import re

from . import dictionary, lessons, verbs
from .packs import _items, _rows

ARTICLE_GENDER = {"der": {"m"}, "die": {"f", "pl"}, "das": {"n"}}
_TOKEN = re.compile(r"[A-Za-zÄÖÜäöüßıİ]+(?:-[A-Za-zÄÖÜäöüßıİ]+)*")
# Names, places and words the dictionary doesn't list as they are written here.
ALLOW = {
    "Anna", "Ben", "Tom", "Lena", "Mia", "Jonas", "Emre", "Kaya", "Weber", "Sara", "Paul", "Lisa", "Maria", "Eva",
    "Yilmaz", "Brandt", "Novak", "Bauer", "Tim", "Kreta", "Lea", "Jan", "Sophie", "Leon", "Aylin", "Wagner", "Nina",
    "Ali", "Schulz", "Felix", "Clara", "Emma", "Rossi", "Lang", "Demir", "Izmir", "Ankara", "Lukas", "Julia", "Max",
    "Herr", "Frau", "Köln", "Wien", "Hamburg", "Berlin", "München", "Frankfurt", "Mannheim", "Leipzig", "Stuttgart",
    "Portugal", "Ostsee", "Spanien", "Italien", "Polen", "England", "Türkei", "Schweiz", "Österreich",
    "Deutschland", "Opa", "Oma", "Mama", "Mathe", "okay", "Okay", "s", "Zwei-Zimmer-Wohnung", "U-Bahn", "T-Shirt",
    "E-Mail", "Kopfschmerzen", "Apfelkuchen", "Holzboden", "Glasflaschen", "Plastikflaschen", "Mietvertrag",
    "Fluggesellschaft", "Lieblingsfach", "Mittagspause", "Kellnerin", "Mitarbeiterin", "Passantin", "Beamtin",
    "zwanzigste", "zwanzigsten", "möchten",
    # B1 (checked by hand by its author, see tests/test_lessons_b1.py)
    "Bremen", "Roth", "Yılmaz", "Gisela", "Meyer", "Jana", "wiederbekommen", "mitschicken", "Onlinebanking",
    "umweltfreundlich", "abwechslungsreich", "lachendes", "schlafendes",
}
# Nouns the dictionary gets wrong: Student is missing (only Studentin is there), and "das Gehalt" (salary) is
# merged into "der Gehalt" (content).
GENDER_OK = {"Student": "der", "Gehalt": "das"}
NOT_VERBS = {"gern", "morgen", "oben", "unten", "eben", "trotzdem", "zwischen", "gegen", "neben", "hinten", "zusammen",
             "gestern", "selten", "geboren", "gegessen", "getrunken", "gegangen", "gefahren", "gekommen", "geblieben",
             "unterwegs", "wegen", "schüchtern", "modern", "trocken", "offen", "verheiratet"}


def _tokens(text):
    return _TOKEN.findall(text)


def _known(tok):
    if tok in ALLOW or dictionary.known(tok) or dictionary.known(tok.lower()) or dictionary.known(tok.capitalize()):
        return True
    return bool(dictionary.lookup(tok, 1))  # compounds


def _noun_problem(art, noun):
    if noun in lessons.PLURAL_ONLY or noun in ALLOW:
        return None
    if noun in GENDER_OK:
        return None if GENDER_OK[noun] == art else f"gender: {art} {noun} (should be {GENDER_OK[noun]})"
    entries = [e for e in dictionary.lookup(noun, 8) if e["pos"] == "noun" and e["word"] == noun]
    if not entries:
        c = dictionary.compound(noun) if noun[:1].isupper() else None
        entries = [c] if c else []
    if not entries:
        return f"noun not in the dictionary: {art} {noun}"
    genders = {g for e in entries for g in (e.get("genders") or [e["gender"]])}
    if genders and not genders & ARTICLE_GENDER[art]:
        return f"gender: {art} {noun} (dictionary: {', '.join(sorted(genders))})"
    return None


def _verb_problem(word):
    inf = word[5:] if word.startswith("sich ") else word
    inf = inf.split()[0]
    if inf in verbs._BY_INF or inf in ALLOW:
        return None
    if any(e["pos"] == "verb" and e["word"] == inf for e in dictionary.lookup(inf, 8)):
        return None
    return f"verb not in the dictionary: {word}"


def lesson_problems(l):
    out = []
    for de, _en in _items(l["words"]):
        art, _, rest = de.partition(" ")
        if art in ARTICLE_GENDER and rest[:1].isupper() and " " not in rest:
            p = _noun_problem(art, rest)
        elif re.fullmatch(r"(sich )?[a-zäöü]+(en|ern|eln)( (auf|für|über|an|von))?", de) and de not in NOT_VERBS:
            p = _verb_problem(de)
        else:
            p = None
        if p:
            out.append(p)
    german = [r[1] for r in _rows(l["dialogue"])] + [de for de, _ in _items(l["grammar"][2])] + [de for de, _ in _items(l["words"])]
    for r in _rows(l["exercises"]):
        if len(r) != 4 or r[0].count("___") != 1 or len(set(r[1:])) != 3:
            out.append(f"exercise format: {'|'.join(r)}")
            continue
        german.append(re.sub(r"\([^()]*\)\s*$", "", r[0]).replace("___", r[1]))
    for text in german:
        for tok in _tokens(text):
            if not _known(tok):
                out.append(f"unknown word: {tok} (in: {text})")
    return out


def turkish_problems(l):
    """English texts of one lesson without Turkish (in its *_tr file, or for hints in the app's i18n table)."""
    own = lessons.TURKISH.get(l["id"])
    if own is None:
        return ["no Turkish in the lesson's *_tr file"]
    title, text, examples = l["grammar"]
    texts = [l["subtitle"], title, text] + [en for _de, en in _items(l["words"])] + [r[2] for r in _rows(l["dialogue"])]
    texts += [en for _de, en in _items(examples)]
    out = [f"no Turkish for: {t[:60]}" for t in texts if not own.get(t.strip())]
    for r in _rows(l["exercises"]):
        out += _hint_problem(l, r[0])
    return out


def _hint_problem(l, prompt):
    m = re.search(r"\(([^()]+)\)\s*$", prompt)
    if m and re.search(r"[a-z]{2}", m.group(1)) and m.group(1) != "du" and not dictionary.known(m.group(1)) and lessons.tr_text(l, m.group(1)) == m.group(1):
        return [f"no Turkish for the hint ({m.group(1)})"]
    return []


def problems(turkish_levels=("A1", "A2", "B1")):
    out = []
    for l in lessons.LESSONS:
        out += [f"{l['id']}: {p}" for p in lesson_problems(l)]
        if l["level"] in turkish_levels:
            out += [f"{l['id']}: {p}" for p in turkish_problems(l)]
    for level, text in lessons.TESTS.items():
        for r in _rows(text or ""):
            if len(r) != 4 or r[0].count("___") != 1 or len(set(r[1:])) != 3:
                out.append(f"{level} test item format: {'|'.join(r)}")
                continue
            if level in turkish_levels:
                out += [f"{level} test: {p}" for p in _hint_problem({"id": f"{level}-test"}, r[0])]
            sent = re.sub(r"\([^()]*\)\s*$", "", r[0]).replace("___", r[1])
            out += [f"{level} test: unknown word: {t} (in: {sent})" for t in _tokens(sent) if not _known(t)]
    return out


if __name__ == "__main__":
    found = problems()
    print("\n".join(found) or "No problems found.")
    print(f"{len(found)} problems in {len(lessons.LESSONS)} lessons.")
