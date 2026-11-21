"""Lining up a lesson's English with its Turkish (the lessons_a1_tr.py / lessons_a2_tr.py / lessons_b1_tr.py shape).

A Turkish entry per lesson: subtitle, words (";"-separated, one per word in the lesson's order), dialogue (one
line per dialogue line), grammar (title, text, examples ";"-separated) and optional hints ("English=Turkish; ...")
for the English hints in brackets at the end of exercise sentences.
"""
from .packs import _items, _rows


def pairs(l, t):
    """(English, Turkish) for every English text in one lesson, matched by position. Raises if they don't line up."""
    en_words = [en for _de, en in _items(l["words"])]
    tr_words = [w.strip() for w in t["words"].replace("\n", " ").split(";")]
    en_lines = [r[2] for r in _rows(l["dialogue"])]
    tr_lines = [x.strip() for x in t["dialogue"].strip().splitlines()]
    title, text, examples = l["grammar"]
    tr_title, tr_text, tr_examples = t["grammar"]
    en_ex = [en for _de, en in _items(examples)]
    tr_ex = [x.strip() for x in tr_examples.split(";")]
    if not (len(en_words) == len(tr_words) and len(en_lines) == len(tr_lines) and len(en_ex) == len(tr_ex)):
        raise ValueError(f"Turkish for {l['id']} doesn't line up with the English")
    out = [(l["subtitle"], t["subtitle"]), (title, tr_title), (text, tr_text)]
    out += list(zip(en_words, tr_words)) + list(zip(en_lines, tr_lines)) + list(zip(en_ex, tr_ex))
    out += [(en.strip(), tr.strip()) for en, tr in _items(t.get("hints") or "")]
    return out


def exact(lessons, tr):
    """{English: Turkish} for a file's lessons (for i18n.EXACT); the first lesson's wording wins."""
    out = {}
    for l in lessons:
        for en, tr_ in pairs(l, tr[l["id"]]):
            out.setdefault(en, tr_)
    return out
