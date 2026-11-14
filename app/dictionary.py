"""The offline German dictionary (built by tools/make_dictionary.py from Wiktionary): instant, free look-ups.

lookup("Männer") finds "der Mann, die Männer: man, husband" without any AI call. Inflected forms point to their
dictionary form, and unknown compound nouns are split ("Fußballspieler" = Fußball + der Spieler), so they get their
gender and plural from the last part, the way German works.
"""
import functools
import json
import re
import sqlite3
import threading

from .db import ROOT

PATH = ROOT / "static" / "vendor" / "dict" / "de.sqlite"
ARTICLE = {"m": "der", "f": "die", "n": "das", "pl": "die"}
POS_NAME = {"noun": "noun", "verb": "verb", "adj": "adjective", "adv": "adverb", "prep": "preposition",
            "conj": "conjunction", "pron": "pronoun", "det": "determiner", "article": "article", "num": "number",
            "particle": "particle", "intj": "interjection", "postp": "postposition", "contraction": "contraction"}
_local = threading.local()


def available():
    return PATH.exists()


def _con():
    con = getattr(_local, "con", None)
    if con is None:
        con = sqlite3.connect(f"file:{PATH}?mode=ro", uri=True, check_same_thread=False)
        con.row_factory = sqlite3.Row
        _local.con = con
    return con


def _entry(r, via=None):
    g = (r["gender"] or "").split(",")[0]
    e = {"word": r["word"], "pos": r["pos"], "pos_name": POS_NAME.get(r["pos"], r["pos"]),
         "gender": g, "genders": [x for x in (r["gender"] or "").split(",") if x],
         "article": ARTICLE.get(g, "") if r["pos"] == "noun" else "",
         "plural": r["plural"] or "", "genitive": r["gen"] or "",
         "info": json.loads(r["info"]) if r["info"] else {}, "meanings": json.loads(r["glosses"]),
         "rank": r["rank"]}
    e["short"] = short(e["meanings"])
    if via and via != r["word"]:
        e["form"] = via
    e["forms_text"] = forms_text(e)
    return e


def short(meanings, n=2):
    """The first meanings without Wiktionary's long explanations in brackets, for flashcards and word lists:
    "computer (programmable electronic device that...)" -> "computer"."""
    out = []
    for m in meanings[:n]:
        m = re.sub(r"\s*\([^()]{18,}\)", "", m).strip(" ;,")
        if m and m not in out:
            out.append(m)
    return "; ".join(out)


def forms_text(e):
    i = e["info"]
    if e["pos"] == "verb" and (i.get("praet") or i.get("pp")):
        # Motion verbs often take both (ist gefahren / hat das Auto gefahren): show both, in Wiktionary's order.
        aux = "/".join({"haben": "hat", "sein": "ist"}[a] for a in (i.get("aux") or "haben").split(" / ") if a in ("haben", "sein")) or "hat"
        parts = [p for p in (i.get("pres3") and f"er {i['pres3']}", i.get("praet"), i.get("pp") and f"{aux} {i['pp']}") if p]
        return ", ".join(parts)
    if e["pos"] == "adj" and i.get("comp"):
        return ", ".join(p for p in (i["comp"], i.get("sup")) if p)
    if e["pos"] == "noun" and (e["plural"] or e["genitive"]):
        gen = e["genitive"] and e["gender"] in ("m", "n") and f"des {e['genitive']}"
        return ", ".join(p for p in (gen, e["plural"] and f"die {e['plural']}") if p)
    return ""


def _clean(word):
    return re.sub(r"^[^\wäöüÄÖÜß]+|[^\wäöüÄÖÜß]+$", "", word or "").strip()


def lookup(word, limit=4):
    """Entries for a word as it appears in a text, best match first. [] if nothing is known."""
    if not available():
        return []
    w = _clean(word)
    if not w:
        return []
    rows = _con().execute(
        "SELECT w.*, f.form AS via FROM form f JOIN word w ON w.id = f.word_id WHERE f.form = ? "
        "UNION SELECT w.*, w.word AS via FROM word w WHERE w.word = ? COLLATE NOCASE", (w, w)).fetchall()
    seen, out = set(), []

    def score(r):
        # Same capitalization first (Haus is the noun, haus a verb form), then the more common word
        # (schönen is far more often schön than the rare verb schönen).
        # A capitalized word that is itself a noun entry wins over a noun it's a form of (Lehrerin, not Lehrer).
        return (r["via"] == w, w[:1].isupper() and r["word"] == w, -(r["rank"] or 10 ** 6))
    for r in sorted(rows, key=score, reverse=True):
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(_entry(r, r["via"]))
    if not out and w[:1].isupper():
        c = compound(w)
        if c:
            out.append(c)
    return out[:limit]


def compound(w):
    """An unknown capitalized word read as a compound noun: its last part decides gender and plural."""
    for i in range(1, len(w) - 3):
        head = w[i:].capitalize()
        r = _con().execute("SELECT * FROM word WHERE word = ? AND pos = 'noun' AND gender != '' ORDER BY rank LIMIT 1",
                           (head,)).fetchone()
        if r:
            e = _entry(r)
            first = w[:i]
            joint = first.rstrip("s") if first.endswith("s") and len(first) > 3 else first
            e.update(word=w, form=None, compound=[first, head],
                     plural=(w[:i] + e["plural"].lower()) if e["plural"] else "",
                     genitive=(w[:i] + e["genitive"].lower()) if e["genitive"] else "",
                     meanings=[f"compound: {first} + {e['article']} {head} ({e['meanings'][0]})"] + [])
            first_e = lookup(joint, 1) or lookup(first, 1)
            if first_e:
                e["meanings"].append(f"{first}: {first_e[0]['meanings'][0]}")
            e["forms_text"] = forms_text(e)
            return e
    return None


def nouns(min_rank=0, max_rank=3000, limit=None):
    """Common nouns with a known gender and plural, most frequent first: for the gender and plural drills."""
    if not available():
        return []
    q = "SELECT word, gender, plural, glosses, drill AS rank FROM word WHERE drill > ? AND drill <= ? ORDER BY drill"
    rows = _con().execute(q + (f" LIMIT {int(limit)}" if limit else ""), (min_rank, max_rank)).fetchall()
    return [{"word": r["word"], "g": r["gender"], "pl": r["plural"], "meaning": json.loads(r["glosses"])[0],
             "rank": r["rank"]} for r in rows]


@functools.lru_cache(maxsize=50000)
def known(word):
    """Is this a German word form the dictionary knows? (fast; used to tell German lines from English ones)"""
    if not available():
        return False
    return _con().execute("SELECT 1 FROM form WHERE form = ? LIMIT 1", (word,)).fetchone() is not None


def lemma_of(token):
    """(dictionary form, part of speech) for a word in running text, or (None, None)."""
    found = lookup(token, 1)
    return (found[0]["word"], found[0]["pos"]) if found else (None, None)


# ---------- small grammar words, explained from the app's own grammar tables ----------
_CASE = {"nom": "nominative", "akk": "accusative", "dat": "dative", "gen": "genitive"}
_GEN = {"m": "masculine", "f": "feminine", "n": "neuter", "pl": "plural"}
_GRAMMAR = None


def _grammar_table():
    """form -> {title: [(case, gender)]}: der, dem, einem, meinen, diesem, ihm, mir, denen..."""
    from . import decl
    t = {}

    def add(form, title, case, g):
        t.setdefault(form.lower(), {}).setdefault(title, []).append((case, g))
    for c in decl.CASES:
        for g in decl.GENDERS:
            add(decl.ARTICLE[c][g], "definite article (der, die, das)", c, g)
            add(decl.RELATIVE[c][g], "relative pronoun (who, which, that)", c, g)
            for w in ("dies", "jed", "welch", "jen", "manch"):
                if not (w == "jed" and g == "pl"):
                    add(w + decl.DIES_END[c][g], f"{w}er (der-word)", c, g)
            for w, title in (("ein", "indefinite article (a, an)"), ("kein", "kein (no, not a)")):
                if not (w == "ein" and g == "pl"):
                    add(w + decl.EIN_END[c][g], title, c, g)
            for owner, eng, w in decl.OWNERS:
                stem = "eur" if w == "euer" and decl.EIN_END[c][g] else w
                add(stem + decl.EIN_END[c][g], f"{w} (possessive: {eng})", c, g)
    for p, (label, nom, akk, dat) in decl.PERSONS.items():
        for c, form in (("nom", nom), ("akk", akk), ("dat", dat)):
            add(form, f"personal pronoun {label}", c, "")
    for c, form in decl.WER.items():
        add(form, "wer (question word: who)", c, "")
    return t


def _describe(pairs):
    by_case = {}
    for c, g in pairs:
        by_case.setdefault(c, []).append(_GEN.get(g, ""))
    parts = []
    for c in ("nom", "akk", "dat", "gen"):
        if c in by_case:
            gs = [g for g in dict.fromkeys(by_case[c]) if g]
            parts.append(_CASE[c] + (f" ({', '.join(gs)})" if gs else ""))
    return "; ".join(parts)


def grammar_word(word):
    """An entry explaining a small grammar word by its case and gender, or None."""
    global _GRAMMAR
    if _GRAMMAR is None:
        _GRAMMAR = _grammar_table()
    readings = _GRAMMAR.get(_clean(word).lower())
    if not readings:
        return None
    meanings = [f"{title}: {_describe(pairs)}" for title, pairs in readings.items()]
    return {"word": _clean(word), "pos": "grammar", "pos_name": "grammar word", "gender": "", "genders": [],
            "article": "", "plural": "", "genitive": "", "info": {}, "meanings": meanings, "rank": None,
            "forms_text": "", "grammar": True}


def explain(word, limit=4):
    """What the reader shows for a word: the grammar reading for small grammar words, then dictionary entries."""
    g = grammar_word(word)
    entries = lookup(word, limit)
    if g:
        entries = [g] + [e for e in entries if e["pos"] not in ("article", "det", "pron")][: limit - 1]
    return entries
