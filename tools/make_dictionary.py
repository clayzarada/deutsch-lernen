"""Builds the app's offline German dictionary: static/vendor/dict/de.sqlite.

    python tools/make_dictionary.py <kaikki German .jsonl.gz> <de_50k.txt>

Sources (both CC BY-SA; credited in the app's About box and in static/vendor/dict/SOURCES.txt):
- Wiktionary's German entries, as extracted by kaikki.org (https://kaikki.org/dictionary/German/):
  kaikki.org-dictionary-German.jsonl.gz
- How common each word is: de_50k.txt from https://github.com/hermitdave/FrequencyWords (OpenSubtitles 2018).

The result keeps words that are common enough to matter (in the 50,000 most frequent forms) plus every noun with a
known gender, so compounds in textbooks are found too. Each word gets: part of speech, gender, plural, genitive,
key verb/adjective forms, up to four meanings in English, and a frequency rank. Every inflected form points back
to its dictionary form, so "Männer", "ging" or "schönen" are found.
"""
import gzip
import json
import re
import sqlite3
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "static" / "vendor" / "dict" / "de.sqlite"
POS = {"noun", "verb", "adj", "adv", "prep", "conj", "pron", "det", "article", "num", "particle", "intj",
       "postp", "contraction"}
SKIP_SENSE = {"archaic", "obsolete", "rare", "dated", "historical", "nonstandard", "misspelling", "proscribed"}
BAD_FORM_TAGS = {"rare", "obsolete", "archaic", "dated", "poetic", "nonstandard", "dialectal", "colloquial",
                 "table-tags", "inflection-template", "class", "error-unknown-tag", "romanization", "auxiliary"}
GENDER_TAG = {"masculine": "m", "feminine": "f", "neuter": "n"}
# "dative plural of Mann", "first/third-person singular preterite of gehen", "obsolete form of Haus": inflections
INFLECTION = re.compile(r"\b(plurals?|singular|genitive|dative|accusative|nominative|preterite|participle|inflection|"
                        r"inflected|forms?|comparative|superlative|imperative|person|subjunctive|present|past|"
                        r"feminine|masculine|neuter|strong|weak|mixed|degree|spelling|diminutive)\b[^()]{0,60}?\bof\b")


def ranks(path):
    out = {}
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        w = line.split(" ")[0].strip().lower()
        if w and w not in out:
            out[w] = n
    return out


def clean_gloss(g):
    g = re.sub(r"\s+", " ", g).strip()
    g = re.sub(r"^agent noun of \w+[:;,]?\s*", "", g) or g  # "agent noun of lehren: one who teaches" -> the meaning
    return g if len(g) <= 180 else g[:177].rsplit(" ", 1)[0] + "..."


def first_form(forms, want, avoid=()):
    for f in forms:
        tags = set(f.get("tags") or [])
        if tags == want or (want <= tags and not tags & (BAD_FORM_TAGS | set(avoid)) and f.get("source") is None):
            w = f.get("form", "")
            if w and w not in ("-", "—") and not w.startswith("de-"):
                return w
    return ""


def gender_of(e):
    found = []
    for s in e.get("senses") or []:
        for t in s.get("tags") or []:
            if t in GENDER_TAG and GENDER_TAG[t] not in found:
                found.append(GENDER_TAG[t])
    if not found:
        for h in e.get("head_templates") or []:
            if h.get("name", "").startswith("de-noun"):
                g = (h.get("args") or {}).get("1", "").split(",")[0]
                for part in re.split(r"[^mfnp]", g):
                    for c in part:
                        if c in "mfn" and c not in found:
                            found.append(c)
                if g.startswith("p"):
                    found.append("pl")
    if not found and "plural-only" in (e.get("tags") or []):
        found.append("pl")
    return ",".join(found)


def main(src, freq_path):
    rank = ranks(freq_path)
    lemmas = {}   # (word, pos) -> row
    form_of = []  # (form, lemma word, pos)
    n = 0
    with gzip.open(src, "rt", encoding="utf-8") as f:
        for line in f:
            n += 1
            e = json.loads(line)
            if e.get("lang_code") != "de" or e.get("pos") not in POS:
                continue
            word, pos = e.get("word", ""), e["pos"]
            if not word or (" " in word.strip() and pos not in ("prep", "conj", "adv")) or re.search(r"[:*_/]", word):
                continue
            senses = e.get("senses") or []
            # A "form of" sense is just an inflection ("plural of Mann") unless its meaning is a real one
            # (Teilnehmer is filed as derived from teilnehmen but means "participant").
            real = [s for s in senses if s.get("glosses") and not INFLECTION.search(s["glosses"][-1][:120])]
            for s in senses:
                for fo in s.get("form_of") or []:
                    if fo.get("word"):
                        form_of.append((word, fo["word"], pos))
            if not real:
                continue
            good = [s for s in real if not set(s.get("tags") or []) & SKIP_SENSE] or real
            glosses = []
            for s in good:
                g = clean_gloss(s["glosses"][-1])
                if g and g not in glosses:
                    glosses.append(g)
                if len(glosses) == 4:
                    break
            forms = e.get("forms") or []
            row = lemmas.get((word, pos))
            if row:  # a second etymology of the same word: add its meanings
                row["glosses"] = (row["glosses"] + [g for g in glosses if g not in row["glosses"]])[:5]
                continue
            info = {}
            gender = plural = gen = ""
            if pos == "noun":
                gender = gender_of(e)
                plural = first_form(forms, {"plural"})
                gen = first_form(forms, {"genitive"})
            elif pos == "verb":
                info = {"pres3": first_form(forms, {"present", "singular", "third-person"}),
                        "praet": first_form(forms, {"past"}), "pp": first_form(forms, {"participle", "past"})}
                aux = [f["form"] for f in forms if f.get("tags") == ["auxiliary"] and f.get("source") is None]
                info["aux"] = " / ".join(dict.fromkeys(aux))
            elif pos == "adj":
                info = {"comp": first_form(forms, {"comparative"}), "sup": first_form(forms, {"superlative"})}
            all_forms = {f.get("form") for f in forms
                         if f.get("form") and " " not in f["form"] and not set(f.get("tags") or []) & BAD_FORM_TAGS
                         and not f["form"].startswith("de-")}
            all_forms.add(word)
            if pos == "noun":  # Wiktionary lists few noun forms: add the dative plural (-n) and genitive
                if plural and not plural.endswith(("n", "s")):
                    all_forms.add(plural + "n")
                all_forms.update(x for x in (plural, gen) if x)
            lemmas[(word, pos)] = {"word": word, "pos": pos, "gender": gender, "plural": plural, "gen": gen,
                                   "info": {k: v for k, v in info.items() if v}, "glosses": glosses,
                                   "forms": all_forms}
    print(f"read {n:,} entries, {len(lemmas):,} words, {len(form_of):,} form-of links")

    # forms that are their own entries ("Männer: plural of Mann") point to their word
    by_word = {}
    for (w, p), row in lemmas.items():
        by_word.setdefault(w, []).append(row)
    for form, lemma, pos in form_of:
        for row in by_word.get(lemma, []):
            if row["pos"] == pos or pos in ("noun", "verb", "adj"):
                row["forms"].add(form)

    # frequency: the best rank of any of a word's forms
    other_pos = {fm.lower() for (w, p), r in lemmas.items() if p != "noun" for fm in r["forms"]}
    other_pos |= {f.lower() for f, _l, p in form_of if p != "noun"}
    for row in lemmas.values():
        row["rank"] = min([rank.get(fm.lower(), 10 ** 6) for fm in row["forms"]] or [10 ** 6])
        # Nouns good for the gender and plural drills: common in their own right (the frequency list is lower
        # case, so "das Ich" would otherwise rank like "ich"), one gender, a plural, not a capitalized other word.
        own = rank.get(row["word"].lower())
        row["drill"] = own if (row["pos"] == "noun" and own and row["gender"] in ("m", "f", "n") and row["plural"]
                               and row["word"][:1].isupper() and row["word"][1:].islower() and len(row["word"]) > 2
                               and row["word"].lower() not in other_pos
                               and not row["word"].endswith("in") or row["word"] in ("Termin", "Benzin", "Magazin", "Medizin", "Kamin")) else None
    keep = [r for r in lemmas.values() if r["rank"] < 10 ** 6 or (r["pos"] == "noun" and r["gender"])]
    print(f"keeping {len(keep):,} words ({sum(1 for r in keep if r['rank'] < 10 ** 6):,} with a frequency rank)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.unlink(missing_ok=True)
    con = sqlite3.connect(OUT)
    con.executescript("""
        CREATE TABLE word(id INTEGER PRIMARY KEY, word TEXT, pos TEXT, gender TEXT, plural TEXT, gen TEXT,
                          info TEXT, glosses TEXT, rank INTEGER, drill INTEGER);
        CREATE TABLE form(form TEXT COLLATE NOCASE, word_id INTEGER);
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
    """)
    keep.sort(key=lambda r: (r["rank"], r["word"]))
    for i, r in enumerate(keep, 1):
        con.execute("INSERT INTO word VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (i, r["word"], r["pos"], r["gender"], r["plural"], r["gen"],
                     json.dumps(r["info"], ensure_ascii=False) if r["info"] else "",
                     json.dumps(r["glosses"], ensure_ascii=False), r["rank"] if r["rank"] < 10 ** 6 else None,
                     r["drill"]))
        con.executemany("INSERT INTO form VALUES(?,?)", [(fm, i) for fm in r["forms"]])
    con.execute("CREATE INDEX form_i ON form(form)")
    con.execute("CREATE INDEX word_i ON word(word COLLATE NOCASE)")
    con.execute("CREATE INDEX drill_i ON word(drill)")
    con.executemany("INSERT INTO meta VALUES(?,?)", [
        ("source", "Wiktionary via kaikki.org (CC BY-SA 4.0); frequency: hermitdave/FrequencyWords (CC BY-SA 4.0)"),
        ("words", str(len(keep)))])
    con.commit()
    con.execute("VACUUM")
    con.close()
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
