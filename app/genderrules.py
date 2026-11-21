"""der, die, das from the word itself: the rules that predict a noun's gender from its ending or its word group,
each with how reliable it is and its best-known exceptions.

The noun drill (wordtrain.py, Declensions > Free practice > Nouns) uses this to say after every answer which rule
predicts the noun (or that no rule does, so it has to be learned by heart), and to count which rules the learner
has mastered. The Grammar handbook shows the same table.

The reliability numbers were measured on the app's own dictionary (the 8,500 drill nouns, November 2026); they
are written here as data so the page works without the dictionary too.

Text is bilingual data: every learner-facing string is an (English, Turkish) pair and `text()` picks the app
language. (The handbook in grammar_data.py does the same; see its docstring for why.)
"""
import functools

from . import db, dictionary
from .i18n import lang

ARTICLE = {"m": "der", "f": "die", "n": "das"}

# Word groups, lower case. A compound counts when it ends in one of these with at least 3 letters in front
# ("Spätsommer", "Neuschnee"), so short words that merely end the same way ("Kosten") don't.
DAYS = "montag dienstag mittwoch donnerstag freitag samstag sonnabend sonntag".split()
MONTHS = "januar februar märz april mai juni juli august september oktober november dezember".split()
SEASONS = "frühling sommer herbst winter".split()
WEATHER = "regen schnee wind sturm nebel hagel frost donner blitz föhn orkan taifun hurrikan monsun gewitter".split()
TIMES = "morgen vormittag mittag nachmittag abend".split()

# id, gender, how it is recognized, the rule (en, tr), reliability in %, exceptions, examples.
# kind: "end" = one of the endings; "group" = a listed word group; "agent" = verb stem + -er;
# "inf" = a verb's infinitive used as a noun.
# First match wins, so the more specific rules come first.
RULES = [
    {"id": "days", "g": "m", "kind": "group", "words": DAYS, "pct": 100,
     "rule": ("Days of the week are masculine.", "Haftanın günleri erildir."),
     "label": ("Days of the week", "Haftanın günleri"), "ex": ["der Montag", "der Freitag", "der Sonntag"],
     "exceptions": ["das Wochenende"]},
    {"id": "months", "g": "m", "kind": "group", "words": MONTHS, "pct": 100,
     "rule": ("Months are masculine.", "Aylar erildir."),
     "label": ("Months", "Aylar"), "ex": ["der Januar", "der Mai", "der Dezember"], "exceptions": []},
    {"id": "seasons", "g": "m", "kind": "group", "words": SEASONS, "pct": 100,
     "rule": ("Seasons are masculine.", "Mevsimler erildir."),
     "label": ("Seasons", "Mevsimler"), "ex": ["der Frühling", "der Sommer", "der Winter"],
     "exceptions": ["das Frühjahr"]},
    {"id": "weather", "g": "m", "kind": "group", "words": WEATHER, "pct": 95,
     "rule": ("Most weather words are masculine.", "Hava olaylarını anlatan kelimelerin çoğu erildir."),
     "label": ("Weather", "Hava olayları"), "ex": ["der Regen", "der Schnee", "der Wind"],
     "exceptions": ["das Gewitter", "das Eis", "die Wolke"]},
    {"id": "times", "g": "m", "kind": "group", "words": TIMES, "pct": 100,
     "rule": ("Times of day are masculine (but die Nacht).", "Günün bölümleri erildir (ama die Nacht)."),
     "label": ("Times of day", "Günün bölümleri"), "ex": ["der Morgen", "der Mittag", "der Abend"],
     "exceptions": ["die Nacht"]},
    {"id": "chen", "g": "n", "kind": "end", "ends": ("chen", "lein"), "pct": 89,
     "rule": ("Small forms with -chen or -lein are always neuter, even people: das Mädchen.",
              "-chen veya -lein ile yapılan küçültmeler her zaman nötrdür, insanlar bile: das Mädchen."),
     "label": ("-chen, -lein", "-chen, -lein"), "ex": ["das Mädchen", "das Brötchen", "das Fräulein"],
     "exceptions": ["der Kuchen", "der Knochen", "der Drachen"]},
    {"id": "ung", "g": "f", "kind": "end", "ends": ("ung",), "pct": 99,
     "rule": ("Nouns ending in -ung are feminine.", "-ung ile biten isimler dişildir."),
     "label": ("-ung", "-ung"), "ex": ["die Zeitung", "die Wohnung", "die Meinung"],
     "exceptions": ["der Sprung", "der Schwung", "der Ursprung"]},
    {"id": "heit", "g": "f", "kind": "end", "ends": ("heit", "keit"), "pct": 100,
     "rule": ("Nouns ending in -heit and -keit are feminine.", "-heit ve -keit ile biten isimler dişildir."),
     "label": ("-heit, -keit", "-heit, -keit"), "ex": ["die Freiheit", "die Gesundheit", "die Möglichkeit"], "exceptions": []},
    {"id": "schaft", "g": "f", "kind": "end", "ends": ("schaft",), "pct": 100,
     "rule": ("Nouns ending in -schaft are feminine.", "-schaft ile biten isimler dişildir."),
     "label": ("-schaft", "-schaft"), "ex": ["die Freundschaft", "die Mannschaft", "die Wirtschaft"], "exceptions": []},
    {"id": "ion", "g": "f", "kind": "end", "ends": ("ion",), "pct": 98,
     "rule": ("Nouns ending in -ion are feminine.", "-ion ile biten isimler dişildir."),
     "label": ("-ion", "-ion"), "ex": ["die Information", "die Region", "die Lektion"],
     "exceptions": ["das Stadion", "der Spion", "der Champion"]},
    {"id": "taet", "g": "f", "kind": "end", "ends": ("tät",), "pct": 100,
     "rule": ("Nouns ending in -tät are feminine.", "-tät ile biten isimler dişildir."),
     "label": ("-tät", "-tät"), "ex": ["die Universität", "die Qualität", "die Realität"], "exceptions": []},
    {"id": "enz", "g": "f", "kind": "end", "ends": ("enz", "anz"), "pct": 88,
     "rule": ("Nouns ending in -enz and -anz are feminine.", "-enz ve -anz ile biten isimler dişildir."),
     "label": ("-enz, -anz", "-enz, -anz"), "ex": ["die Konferenz", "die Distanz", "die Toleranz"],
     "exceptions": ["der Tanz", "der Schwanz", "der Kranz"]},
    {"id": "ik", "g": "f", "kind": "end", "ends": ("ik",), "pct": 95,
     "rule": ("Nouns ending in -ik are feminine.", "-ik ile biten isimler dişildir."),
     "label": ("-ik", "-ik"), "ex": ["die Musik", "die Politik", "die Technik"],
     "exceptions": ["der Katholik", "der Streik"]},
    {"id": "ismus", "g": "m", "kind": "end", "ends": ("ismus",), "pct": 100,
     "rule": ("Nouns ending in -ismus are masculine.", "-ismus ile biten isimler erildir."),
     "label": ("-ismus", "-ismus"), "ex": ["der Tourismus", "der Journalismus", "der Optimismus"], "exceptions": []},
    {"id": "ling", "g": "m", "kind": "end", "ends": ("ling",), "pct": 94,
     "rule": ("Nouns ending in -ling are masculine.", "-ling ile biten isimler erildir."),
     "label": ("-ling", "-ling"), "ex": ["der Frühling", "der Liebling", "der Flüchtling"],
     "exceptions": ["die Reling", "das Feeling"]},
    {"id": "ist", "g": "m", "kind": "end", "ends": ("ist",), "pct": 98,
     "rule": ("People ending in -ist are masculine (the woman takes -istin).",
              "-ist ile biten kişi isimleri erildir (kadın için -istin)."),
     "label": ("-ist", "-ist"), "ex": ["der Polizist", "der Tourist", "der Journalist"],
     "exceptions": ["die Frist", "die List"]},
    {"id": "or", "g": "m", "kind": "end", "ends": ("or",), "pct": 94,
     "rule": ("Nouns ending in -or are masculine.", "-or ile biten isimler erildir."),
     "label": ("-or", "-or"), "ex": ["der Motor", "der Doktor", "der Professor"],
     "exceptions": ["das Labor", "das Tor", "das Moor"]},
    {"id": "ment", "g": "n", "kind": "end", "ends": ("ment",), "pct": 94,
     "rule": ("Nouns ending in -ment are neuter.", "-ment ile biten isimler nötrdür."),
     "label": ("-ment", "-ment"), "ex": ["das Dokument", "das Instrument", "das Medikament"],
     "exceptions": ["der Moment", "der Zement"]},
    {"id": "um", "g": "n", "kind": "end", "ends": ("um",), "not_ends": ("aum", "tum"), "pct": 96,
     "rule": ("Words from Latin ending in -um are neuter.", "Latinceden gelen ve -um ile biten kelimeler nötrdür."),
     "label": ("-um", "-um"), "ex": ["das Museum", "das Zentrum", "das Studium"],
     "exceptions": ["der Konsum", "der Baum", "der Raum"]},
    {"id": "nis", "g": "n", "kind": "end", "ends": ("nis",), "pct": 67,
     "rule": ("Nouns ending in -nis are mostly neuter.", "-nis ile biten isimler çoğunlukla nötrdür."),
     "label": ("-nis (mostly)", "-nis (çoğunlukla)"), "ex": ["das Ergebnis", "das Erlebnis", "das Zeugnis"],
     "exceptions": ["die Erlaubnis", "die Kenntnis", "die Erkenntnis", "die Wildnis"]},
    {"id": "ei", "g": "f", "kind": "end", "ends": ("erei", "elei", "ei"), "pct": 87,
     "rule": ("Nouns ending in -ei are feminine.", "-ei ile biten isimler dişildir."),
     "label": ("-ei", "-ei"), "ex": ["die Bäckerei", "die Polizei", "die Türkei"],
     "exceptions": ["das Ei", "der Brei", "der Papagei"]},
    {"id": "ie", "g": "f", "kind": "end", "ends": ("ie",), "pct": 92,
     "rule": ("Nouns ending in a stressed -ie are feminine.", "Vurgulu -ie ile biten isimler dişildir."),
     "label": ("-ie", "-ie"), "ex": ["die Familie", "die Biologie", "die Energie"],
     "exceptions": ["das Knie", "das Genie"]},
    {"id": "ur", "g": "f", "kind": "end", "ends": ("ur",), "not_ends": ("eur",), "pct": 90,
     "rule": ("Nouns ending in -ur are usually feminine.", "-ur ile biten isimler genellikle dişildir."),
     "label": ("-ur", "-ur"), "ex": ["die Natur", "die Kultur", "die Temperatur"],
     "exceptions": ["der Flur", "der Schwur", "das Abitur"]},
    {"id": "agent", "g": "m", "kind": "agent", "pct": 97,
     "rule": ("A verb stem + -er is the person (or tool) that does it, and is masculine.",
              "Fiil kökü + -er, o işi yapan kişidir (veya alettir) ve erildir."),
     "label": ("Doer: verb + -er", "Yapan: fiil + -er"), "ex": ["der Lehrer (lehren)", "der Fahrer (fahren)", "der Wecker (wecken)"],
     "exceptions": ["die Leiter", "das Messer", "das Fenster"]},
    {"id": "inf", "g": "n", "kind": "inf", "pct": 100,
     "rule": ("A verb's infinitive used as a noun is neuter.", "İsim olarak kullanılan fiil mastarı nötrdür."),
     "label": ("Infinitive as noun", "İsim olarak mastar"), "ex": ["das Essen", "das Leben", "das Schwimmen"],
     "exceptions": ["der Wagen", "der Laden", "der Garten"]},
    {"id": "e", "g": "f", "kind": "end", "ends": ("e",), "pct": 87,
     "rule": ("Most nouns ending in -e are feminine.", "-e ile biten isimlerin çoğu dişildir."),
     "label": ("-e (most)", "-e (çoğu)"), "ex": ["die Lampe", "die Straße", "die Sprache"],
     "exceptions": ["der Name", "der Käse", "der Kollege", "der Junge", "das Auge", "das Ende"]},
]
RULE_BY_ID = {r["id"]: r for r in RULES}
MASTER_MIN = 6      # answers needed before a rule can count as mastered
MASTER_LAST = 10    # ... of which the last 10 (or all, if fewer) must be at least
MASTER_SHARE = .85  # 85 % right

SCHEMA = "CREATE TABLE IF NOT EXISTS gender_rule_log(id INTEGER PRIMARY KEY, rule TEXT, word TEXT, correct INTEGER, ts TEXT);"


def text(pair):
    """The app language's half of an (English, Turkish) pair."""
    return pair[1] if lang() == "tr" else pair[0]


@functools.lru_cache(maxsize=1)
def _verbs():
    """Every verb infinitive in the dictionary (lower case), for the -er and infinitive rules."""
    if not dictionary.available():
        return frozenset()
    return frozenset(r[0].lower() for r in dictionary._con().execute("SELECT word FROM word WHERE pos='verb'"))


def _plain(s):
    return s.replace("ä", "a").replace("ö", "o").replace("ü", "u")


def _in_group(w, words):
    return any(w == g or (w.endswith(g) and len(w) - len(g) >= 3) for g in words)


def _is_agent(w):
    if not w.endswith("er") or len(w) < 5:
        return False
    stem, verbs = w[:-2], _verbs()
    return any(c in verbs for c in (stem + "en", stem + "n", _plain(stem) + "en", stem + "ern"))


def _is_inf(w):
    """das Essen, das Schwimmen. (Not compounds: "Kinderwagen" would look like one.)"""
    return w.endswith("n") and len(w) >= 5 and w in _verbs()


def _matches(r, w):
    kind = r["kind"]
    if kind == "group":
        return _in_group(w, r["words"])
    if kind == "end":
        return w.endswith(r["ends"]) and len(w) > min(len(e) for e in r["ends"]) + 1 and not w.endswith(r.get("not_ends", ()))
    if kind == "agent":
        return _is_agent(w)
    if kind == "inf":
        return _is_inf(w)
    return False


def predict(word):
    """The rule that predicts this noun's gender, or None when no rule does. (The rule may still be wrong for
    this noun: compare its "g" with the real gender to see whether the noun is an exception.)"""
    w = (word or "").strip().lower()
    for r in RULES:
        if _matches(r, w):
            return r
    return None


def explain(word, gender):
    """What the drill shows after an answer: (rule id or None, does the noun follow it, sentence)."""
    g = (gender or "").split(",")[0]
    art = ARTICLE.get(g, "")
    r = predict(word)
    if not r:
        return None, None, text(("No rule predicts this one: learn it by heart, together with its article.",
                                 "Bunu öngören bir kural yok: artikeliyle birlikte ezberleyin."))
    if r["g"] == g:
        return r["id"], True, text(("Rule: ", "Kural: ")) + text(r["rule"])
    return r["id"], False, text(("Exception! The rule says {}, but it is {} {}. ", "İstisna! Kural {} der, ama doğrusu {} {}. ")).format(
        ARTICLE[r["g"]], art, word) + text(("Rule: ", "Kural: ")) + text(r["rule"])


def _init():
    with db.connect() as conn:
        conn.executescript(SCHEMA)


def record(rule_id, word, correct):
    """Count one der/die/das answer toward its rule (None = a noun no rule predicts)."""
    _init()
    rid = rule_id if rule_id in RULE_BY_ID else "none"
    db.ex("INSERT INTO gender_rule_log(rule, word, correct, ts) VALUES(?,?,?,?)", (rid, word, int(bool(correct)), db.now()))


def progress():
    """Each rule with how often it came up, how much of it is right lately, and whether it counts as mastered."""
    _init()
    rows = db.q("SELECT rule, correct FROM gender_rule_log ORDER BY id")
    by = {}
    for r in rows:
        by.setdefault(r["rule"], []).append(r["correct"])
    out = []
    for r in RULES:
        log = by.get(r["id"], [])
        last = log[-MASTER_LAST:]
        out.append({"id": r["id"], "gender": r["g"], "article": ARTICLE[r["g"]], "label": text(r["label"]),
                    "rule": text(r["rule"]), "pct": r["pct"], "examples": r["ex"], "exceptions": r["exceptions"],
                    "answered": len(log), "recent_right": sum(last), "recent": len(last),
                    "mastered": len(log) >= MASTER_MIN and sum(last) >= MASTER_SHARE * len(last)})
    none = by.get("none", [])
    return {"rules": out, "mastered": sum(1 for r in out if r["mastered"]), "total": len(out),
            "by_heart": {"answered": len(none), "right": sum(none)}}


def nouns_for(rule_id, pool):
    """The nouns in the pool that this rule covers (exceptions included, they're part of learning the rule)."""
    r = RULE_BY_ID.get(rule_id)
    if not r:
        return pool
    return [n for n in pool if predict(n["word"]) is r]
