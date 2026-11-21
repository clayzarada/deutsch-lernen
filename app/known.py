"""Which German words the learner knows: the shared base for the progress page and the reading room.

Every word is tracked by its dictionary form ("Männer" and "Mann" are the same word) with a status:
  -1 ignored (names, English words, typos)   0 new   1 seen   2 learning   3 known

Where a status comes from:
- Flashcards decide on their own: a card reviewed at least once makes its word "learning", and a card that has
  grown to an interval of 21 days or more makes it "known". This is read from the cards each time, so it never
  goes stale and needs no hook in the review code.
- Lessons: passing a lesson marks its words "learning".
- Reading: opening a text marks its words "seen"; the learner can mark any word known, learning or ignored.
A word's status is the highest of these, except that the learner's own choice ("user") always wins, so they can
take a word back down to "learning" or ignore it.
"""
import datetime as dt
import functools
import re

from . import db, dictionary

IGNORED, NEW, SEEN, LEARNING, KNOWN = -1, 0, 1, 2, 3
NAMES = {IGNORED: "ignored", NEW: "new", SEEN: "seen", LEARNING: "learning", KNOWN: "known"}
MATURE_DAYS = 21  # a card at this interval or more counts as known (the usual "mature" line in Anki)

SCHEMA = """
CREATE TABLE IF NOT EXISTS known_words(
  lemma TEXT PRIMARY KEY, status INTEGER, source TEXT, seen INTEGER DEFAULT 0, first_seen TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS known_history(date TEXT PRIMARY KEY, known INTEGER, learning INTEGER);
"""

_WORD = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
_ARTICLES = {"der", "die", "das"}
_ready = False


def _family(base, *forms):
    return {f: base for f in (base,) + forms}


# Articles and pronouns are tiny and very common; the dictionary mixes their forms up (it reads "ich" as a form
# of "Ihr"), so they get a fixed table. Lower-case lookup, except formal "Sie" / "Ihnen".
_FUNCTION = {
    **_family("der", "die", "das", "dem", "den", "des"),
    **_family("ein", "eine", "einen", "einem", "einer", "eines"),
    **_family("kein", "keine", "keinen", "keinem", "keiner", "keines"),
    **_family("dieser", "diese", "dieses", "diesen", "diesem"),
    **_family("ich", "mich", "mir", "meiner"), **_family("du", "dich", "dir", "deiner"),
    **_family("er", "ihn", "ihm"), **_family("es"), **_family("sie"), **_family("wir", "uns"),
    **_family("ihr", "euch"),
    **_family("mein", "meine", "meinen", "meinem", "meiner", "meines"),
    **_family("dein", "deine", "deinen", "deinem", "deiner", "deines"),
    **_family("unser", "unsere", "unseren", "unserem", "unserer", "unseres"),
    **_family("euer", "eure", "euren", "eurem", "eurer", "eures"),
}
_FORMAL = {"Sie": "Sie", "Ihnen": "Sie"}


def _init():
    global _ready
    if not _ready:
        with db.connect() as conn:
            conn.executescript(SCHEMA)
        _ready = True


# ---------- words in text ----------

@functools.lru_cache(maxsize=100000)
def lemma(token):
    """The dictionary form a word in running text belongs to, or a lowercase fallback for unknown words."""
    t = (token or "").strip()
    if not t or not _WORD.fullmatch(t):
        return None
    if t in _FORMAL:
        return _FORMAL[t]
    if t.lower() in _FUNCTION:
        return _FUNCTION[t.lower()]
    found, _ = dictionary.lemma_of(t)
    return found or t.lower()


def tokenize(text):
    """Text split into pieces for display: words carry their lemma, everything between them (spaces,
    punctuation, numbers) is kept as it is, so joining every "t" gives back the original text."""
    out, pos = [], 0
    for m in _WORD.finditer(text or ""):
        if m.start() > pos:
            out.append({"t": text[pos:m.start()]})
        out.append({"t": m.group(), "lemma": lemma(m.group())})
        pos = m.end()
    if pos < len(text or ""):
        out.append({"t": text[pos:]})
    return out


def lemmas_in(text):
    return [p["lemma"] for p in tokenize(text) if p.get("lemma")]


# ---------- where statuses come from ----------

def _card_words(front):
    """The German words a flashcard teaches, from its front. Pattern cards ("helfen + ?") and long sentences
    teach grammar more than words, so only the first few words count."""
    f = re.sub(r"\s*[·(|].*$", "", front or "").strip()  # "gehen · to go", "der Mann (Männer)" -> the word part
    if "+" in f or "___" in f:
        return []
    toks = [t for t in _WORD.findall(f)]
    if toks and toks[0].lower() in _ARTICLES and len(toks) > 1:
        toks = toks[1:]
    return [x for x in (lemma(t) for t in toks[:4]) if x]


def _from_cards():
    best = {}
    for c in db.q("SELECT front, type, interval, reps, due FROM cards WHERE type IN ('vocab', 'verb', 'phrase')"):
        st = KNOWN if (c["interval"] or 0) >= MATURE_DAYS else LEARNING if (c["reps"] or c["due"]) else SEEN
        for w in _card_words(c["front"]):
            if st > best.get(w, NEW):
                best[w] = st
    return best


def _rows():
    _init()
    return {r["lemma"]: r for r in db.q("SELECT * FROM known_words")}


def statuses(lemmas=None):
    """{lemma: status} for the given lemmas (every tracked word if None). Untracked words are NEW."""
    rows, cards = _rows(), _from_cards()
    keys = set(lemmas) if lemmas is not None else set(rows) | set(cards)
    out = {}
    for w in keys:
        r = rows.get(w)
        if r and r["source"] == "user":
            out[w] = r["status"]
        else:
            out[w] = max(r["status"] if r else NEW, cards.get(w, NEW))
    return out


def mark(lemmas, status, source="user"):
    """Set a status. Only "user" can lower one; lessons and reading only ever raise it."""
    _init()
    now = db.now()
    rows = _rows()
    for w in {x for x in lemmas if x}:
        r = rows.get(w)
        if r and source != "user" and (r["source"] == "user" or r["status"] >= status):
            continue
        db.ex("INSERT INTO known_words(lemma, status, source, first_seen, updated_at) VALUES(?,?,?,?,?) "
              "ON CONFLICT(lemma) DO UPDATE SET status=excluded.status, source=excluded.source, "
              "updated_at=excluded.updated_at", (w, status, source, now, now))


def saw(lemmas):
    """The learner met these words in a text: count it, and new words become "seen"."""
    _init()
    now = db.now()
    for w in {x for x in lemmas if x}:
        db.ex("INSERT INTO known_words(lemma, status, source, seen, first_seen, updated_at) VALUES(?,?,'reading',1,?,?) "
              "ON CONFLICT(lemma) DO UPDATE SET seen = seen + 1, "
              "status = CASE WHEN source != 'user' AND status < ? THEN ? ELSE status END",
              (w, SEEN, now, now, SEEN, SEEN))


# ---------- summaries ----------

def counts():
    """How many words are known / learning / seen. Also keeps one snapshot per day for the progress graph."""
    s = statuses()
    out = {"known": sum(v == KNOWN for v in s.values()), "learning": sum(v == LEARNING for v in s.values()),
           "seen": sum(v == SEEN for v in s.values())}
    db.ex("INSERT INTO known_history(date, known, learning) VALUES(?,?,?) ON CONFLICT(date) DO UPDATE SET "
          "known=excluded.known, learning=excluded.learning", (db.today(), out["known"], out["learning"]))
    return out


def history(days=180):
    _init()
    since = (db.study_date() - dt.timedelta(days=days)).isoformat()
    return db.q("SELECT date, known, learning FROM known_history WHERE date >= ? ORDER BY date", (since,))


def coverage(text):
    """How much of a text the learner can already read: the share of its running words that are known or
    being learned (95%+ is comfortable reading, under 85% is hard work), and the new words in it."""
    words = lemmas_in(text)
    if not words:
        return {"words": 0, "known_pct": 100, "unknown": []}
    s = statuses(set(words))
    ok = sum(1 for w in words if s.get(w, NEW) >= LEARNING or s.get(w) == IGNORED)
    unknown = sorted({w for w in words if NEW <= s.get(w, NEW) < LEARNING})
    return {"words": len(words), "known_pct": round(100 * ok / len(words)), "unknown": unknown}
