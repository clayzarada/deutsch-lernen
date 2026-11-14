"""Two drills that need no AI, in the same question format as the declension drills (so the page shows them the
same way and the skills use the same spaced repetition):

- Nouns: der/die/das and plurals for thousands of nouns from the offline dictionary, most common first.
- Numbers: numbers, clock times, dates, prices and years, read and written.
"""
import random

from . import db, decl, dictionary

# ---------- nouns ----------
LEVELS = {  # name -> (label, highest frequency rank)
    "200": ("The 200 most common nouns", 1500),
    "650": ("The 650 most common", 4000),
    "1900": ("The 1,900 most common", 10000),
    "all": ("All 8,500", 10 ** 6),
}
NEW_AT_ONCE = 12  # unseen nouns come in frequency order, a few at a time


def _pool(level):
    return dictionary.nouns(0, LEVELS.get(level, LEVELS["650"])[1])


def levels():
    return [{"id": k, "label": v[0]} for k, v in LEVELS.items()]


def _plural_pattern(word, pl):
    """How the plural is made, in words: Mann → Männer is 'umlaut + -er', Frau → Frauen is '-en'."""
    if pl == word:
        return "no change"
    if pl.startswith(word):
        return f"-{pl[len(word):]}"
    plain = pl.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("Ä", "A").replace("Ö", "O").replace("Ü", "U")
    if plain != pl and plain.startswith(word):
        return "umlaut" + (f" + -{plain[len(word):]}" if plain != word else " only")
    return "an irregular change"


GENDER_RULES = decl.GENDER_HINTS


def _gender_why(n):
    art = decl.ARTICLE["nom"][n["g"]]
    w = n["word"].lower()
    for ends, hint_art, text in GENDER_RULES:
        if w.endswith(ends):
            return text if hint_art == art else f"An exception to the pattern: {text}"
    return "No reliable ending rule for this one, so learn it with its article."


def _pick(pool, prefix, recent):
    st, now, recent = decl._state(), db.now(), set(recent or ())
    unseen = [n for n in pool if f"{prefix}:{n['word']}" not in st][:NEW_AT_ONCE]
    unseen_set = {n["word"] for n in unseen}
    cands, weights = [], []
    for n in pool:
        k = f"{prefix}:{n['word']}"
        if k not in st and n["word"] not in unseen_set:
            continue
        cands.append(n)
        weights.append(decl._weight(k, st, recent, now))
    if not cands:
        cands, weights = pool[:NEW_AT_ONCE], [1] * min(len(pool), NEW_AT_ONCE)
    return random.choices(cands, weights)[0]


def noun_question(level="650", mode="mix", recent=()):
    pool = _pool(level)
    if not pool:
        raise db.UserError("The dictionary isn't installed in this copy of the app.")
    mode = mode if mode in ("gender", "plural") else random.choice(["gender", "plural"])
    prefix = "ng" if mode == "gender" else "np"
    n = _pick(pool, prefix, recent)
    art = decl.ARTICLE["nom"][n["g"]]
    meaning = n["meaning"]
    if mode == "gender":
        return {"family": "ngender", "label": "Noun genders", "key": f"ng:{n['word']}", "prompt": n["word"],
                "answers": [art], "display": art, "why": f"{art} {n['word']}: {meaning}. {_gender_why(n)}",
                "cue": "", "case": None, "gender": n["g"], "hide_case": True, "kind": "choice",
                "choices": ["der", "die", "das"], "parts": [{"key": f"ng:{n['word']}"}],
                "full": f"{art} {n['word']} ({meaning})"}
    return {"family": "nplural", "label": "Plurals", "key": f"np:{n['word']}", "prompt": "die ___",
            "answers": [n["pl"], "die " + n["pl"]], "display": n["pl"],
            "why": f"{n['word']} → {n['pl']}: {_plural_pattern(n['word'], n['pl'])}. Learn each noun with its plural.",
            "cue": f"{art} {n['word']} ({meaning})", "case": None, "gender": "pl", "hide_case": True, "kind": "text",
            "choices": None, "parts": [{"key": f"np:{n['word']}"}], "full": f"die {n['pl']}"}


def noun_progress(level="650"):
    pool = _pool(level)
    st = decl._state()
    out = {}
    for prefix in ("ng", "np"):
        rows = [st.get(f"{prefix}:{n['word']}") for n in pool]
        out[prefix] = {"total": len(pool), "seen": sum(1 for r in rows if r),
                       "solid": sum(1 for r in rows if r and r["box"] >= decl.MASTERED_BOX)}
    return out


# ---------- numbers, times, dates, prices, years ----------
ONES = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf",
        "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn"]
TENS = ["", "", "zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"]
MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November",
          "Dezember"]


def words(n, final=True):
    """German number words: 21 → einundzwanzig, 101 → (ein)hunderteins, 1999 → (ein)tausendneunhundertneunundneunzig."""
    if n < 20:
        w = ONES[n]
        return w if final or n != 1 else "ein"
    if n < 100:
        t, o = divmod(n, 10)
        return (("ein" if o == 1 else ONES[o]) + "und" if o else "") + TENS[t]
    if n < 1000:
        h, r = divmod(n, 100)
        return ("ein" if h == 1 else ONES[h]) + "hundert" + (words(r) if r else "")
    if n < 1_000_000:
        th, r = divmod(n, 1000)
        return ("ein" if th == 1 else words(th, final=False)) + "tausend" + (words(r) if r else "")
    raise ValueError(n)


def _variants(w):
    """Also accept hundert/tausend without ein- (hundertzwei = einhundertzwei)."""
    out = {w}
    for x in ("hundert", "tausend"):
        if w.startswith("ein" + x):
            out.add(w[3:])
    return sorted(out, key=len, reverse=True)


def year_words(y):
    if 1100 <= y < 2000:
        h, r = divmod(y, 100)
        return words(h, False) + "hundert" + (words(r) if r else "")
    return words(y)


def ordinal(n):
    """3 → dritt, 7 → siebt, 20 → zwanzigst (add the ending yourself)."""
    special = {1: "erst", 3: "dritt", 7: "siebt", 8: "acht"}
    if n in special:
        return special[n]
    return words(n) + ("t" if n < 20 else "st")


def clock(h, m):
    """Spoken time for h:m (5-minute steps), the everyday way. Returns all accepted ways."""
    h12 = h % 12 or 12
    nxt = h12 % 12 + 1
    hw = lambda x: "eins" if x == 1 else words(x)
    if m == 0:
        return [f"{'ein' if h12 == 1 else words(h12)} Uhr", hw(h12)]
    table = {5: [f"fünf nach {hw(h12)}"], 10: [f"zehn nach {hw(h12)}"], 15: [f"Viertel nach {hw(h12)}", f"viertel {hw(nxt)}"],
             20: [f"zwanzig nach {hw(h12)}", f"zehn vor halb {hw(nxt)}"], 25: [f"fünf vor halb {hw(nxt)}"],
             30: [f"halb {hw(nxt)}"], 35: [f"fünf nach halb {hw(nxt)}"],
             40: [f"zwanzig vor {hw(nxt)}", f"zehn nach halb {hw(nxt)}"], 45: [f"Viertel vor {hw(nxt)}", f"drei viertel {hw(nxt)}"],
             50: [f"zehn vor {hw(nxt)}"], 55: [f"fünf vor {hw(nxt)}"]}
    return table[m]


def price_words(cents):
    e, c = divmod(cents, 100)
    if e == 0:
        return [f"{words(c)} Cent"]
    base = f"{'ein' if e == 1 else words(e)} Euro"
    if not c:
        return [base]
    return [f"{base} {words(c)}", f"{base} und {words(c)} Cent", f"{base} {words(c)} Cent"]


NUM_SKILLS = {
    "num:read:1": ("Numbers 0–100: word to digits", "read", (0, 100)),
    "num:write:1": ("Numbers 0–100: write them out", "write", (0, 100)),
    "num:read:2": ("Big numbers: word to digits", "read", (100, 99999)),
    "num:write:2": ("Big numbers: write them out", "write", (100, 9999)),
    "time:say": ("Clock times, everyday", "time", None),
    "time:read": ("Clock times: words to digits", "timeread", None),
    "time:official": ("Clock times, official (14:30)", "official", None),
    "date:am": ("Dates: am dritten Mai", "dateam", None),
    "date:der": ("Dates: der dritte Mai", "dateder", None),
    "price": ("Prices", "price", None),
    "year": ("Years", "year", None),
}
NUM_GROUPS = {"numbers": ["num:read:1", "num:write:1", "num:read:2", "num:write:2"],
              "times": ["time:say", "time:read", "time:official"], "dates": ["date:am", "date:der"],
              "prices": ["price"], "years": ["year"]}


def _nq(key, prompt, answers, display, why, cue="", full=None, speak=None):
    return {"family": "numbers", "label": NUM_SKILLS[key][0], "key": key, "prompt": prompt, "answers": answers,
            "display": display, "why": why, "instr": cue, "cue": "", "case": None, "gender": None, "hide_case": True,
            "kind": "text", "choices": None, "parts": [{"key": key}], "full": full or display, "speak": speak}


def _skewed(lo, hi):
    """Mostly the tricky ones: 13-19, -und- numbers, round hundreds and thousands mixed in."""
    if hi <= 100:
        return random.choice([random.randint(0, 20), random.randint(21, 99), random.randint(21, 99), random.randint(13, 19)])
    return random.choice([random.randint(lo, 999), random.randint(1000, hi), random.randint(1, 9) * 1000 + random.randint(1, 99),
                          random.randint(1, 9) * 100 + random.randint(1, 20)])


def number_question(groups=None, recent=()):
    keys = [k for g in (groups or NUM_GROUPS) if g in NUM_GROUPS for k in NUM_GROUPS[g]] or list(NUM_SKILLS)
    st, now, rec = decl._state(), db.now(), set(recent or ())
    key = random.choices(keys, [decl._weight(k, st, rec, now) if k not in rec else .2 for k in keys])[0]
    kind, rng = NUM_SKILLS[key][1], NUM_SKILLS[key][2]
    if kind in ("read", "write"):
        n = _skewed(*rng)
        w = words(n)
        why = ("Numbers 21–99 say the ones first: einundzwanzig = one-and-twenty. Write them as one word."
               if 20 < n % 100 < 100 else "Write numbers as one word, however long.")
        if n in (16, 17) or n % 100 in (16, 17):
            why = "Careful: sechzehn and siebzehn drop letters (not sechszehn, siebenzehn)."
        if kind == "read":
            return _nq(key, w, [str(n), f"{n:,}".replace(",", ".")], str(n), why, "Write it in digits", f"{w} = {n}", speak=w)
        return _nq(key, f"{n:,}".replace(",", "."), _variants(w), w, why, "Write it out in words", f"{n} = {w}", speak=w)
    if kind in ("time", "timeread"):
        h, m = random.randint(1, 12), random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        says = clock(h, m)
        why = {0: "Full hours: the number, then Uhr (vier Uhr). One o'clock is ein Uhr.",
               30: "halb vier = half to four: halb points to the coming hour.",
               15: "Viertel nach drei = quarter past three. In parts of Germany: viertel vier.",
               45: "Viertel vor vier = quarter to four. In parts of Germany: drei viertel vier."}.get(
            m, "nach = past, vor = to. Around the half hour Germans count from halb: fünf vor halb vier = 3:25.")
        digital = f"{h}:{m:02d}"
        if kind == "time":
            return _nq(key, digital, says, says[0], why, "Say it the everyday way", f"{digital} = {says[0]}", speak=says[0])
        return _nq(key, says[0], [digital, f"{h + 12}:{m:02d}", f"{h:02d}:{m:02d}", f"{h}.{m:02d}"], digital, why,
                   "Write the time in digits", f"{says[0]} = {digital}", speak=says[0])
    if kind == "official":
        h, m = random.randint(0, 23), random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, random.randint(1, 59)])
        hw = "ein" if h == 1 else words(h)
        say = f"{hw} Uhr" + (f" {words(m)}" if m else "")
        return _nq(key, f"{h}:{m:02d} Uhr", [say], say, "Official times (timetables, the news) use the 24-hour clock: "
                   "the hour, then Uhr, then the minutes.", "Say it the official way", f"{h}:{m:02d} = {say}", speak=say)
    if kind in ("dateam", "dateder"):
        d, mo = random.randint(1, 31), random.randint(1, 12)
        o = ordinal(d)
        if kind == "dateam":
            say = f"am {o}en {MONTHS[mo - 1]}"
            return _nq(key, f"am {d}. {MONTHS[mo - 1]}", [say], say,
                       "am + date takes the dative: am dritten, am zwanzigsten. 1st-19th add -t-, 20th and up add -st-.",
                       "Write the date out (Ich komme ...)", f"am {d}. {MONTHS[mo - 1]} = {say}", speak=say)
        say = f"der {o}e {MONTHS[mo - 1]}"
        return _nq(key, f"Heute ist der {d}. {MONTHS[mo - 1]}.", [say, f"heute ist der {o}e {MONTHS[mo - 1]}"], say,
                   "After der in the nominative the ordinal ends in -e: der dritte, der zwanzigste. Special: erste, dritte, siebte, achte.",
                   "Write the date out", f"der {d}. {MONTHS[mo - 1]} = {say}", speak=say)
    if kind == "price":
        cents = random.choice([random.randint(1, 99), random.randint(1, 30) * 100 + random.randint(1, 99),
                               random.randint(1, 50) * 100 + random.choice([50, 90, 99, 0]), random.randint(100, 999) * 100])
        shown = f"{cents // 100},{cents % 100:02d} €" if cents >= 100 else f"0,{cents:02d} €"
        says = price_words(cents)
        return _nq(key, shown, says, says[0], "Prices: euros, then the cents, usually without saying Cent: drei Euro fünfzig. "
                   "The comma is the decimal point in German.", "Say the price", f"{shown} = {says[0]}", speak=says[0])
    y = random.choice([random.randint(1900, 1999), random.randint(2000, 2039), random.randint(1500, 1899)])
    say = year_words(y)
    return _nq(key, str(y), _variants(say), say, "Years before 2000 are said in hundreds: neunzehnhundertneunundneunzig. "
               "From 2000 on: zweitausend...", "Say the year", f"{y} = {say}", speak=say)


def numbers_progress():
    st = decl._state()
    return [{"key": k, "label": v[0], "box": (st.get(k) or {}).get("box", 0)} for k, v in NUM_SKILLS.items()]


# ---------- marking ----------
def grade(q, answer, ms=None):
    """Mark like the declension drills (case and spacing don't matter; umlauts may be typed as ae/oe/ue)."""
    given = decl.norm(answer).replace("-", "")
    right = given in {decl.norm(a).replace("-", "") for a in q["answers"]}
    if q["family"] == "numbers" and not right:  # spaces inside number words don't matter: drei und zwanzig
        right = given.replace(" ", "") in {decl.norm(a).replace(" ", "").replace("-", "") for a in q["answers"]}
    fast = bool(right and ms is not None and ms <= decl.speed_limit_ms(q))
    for part in q["parts"]:
        decl.update_skill(part["key"], right, fast, ms)
    topic = {"ngender": "Nouns: genders", "nplural": "Nouns: plurals", "numbers": "Numbers, times and dates"}[q["family"]]
    db.ex("INSERT INTO answers(source, topic, correct, ts, date) VALUES('declension',?,?,?,?)",
          (topic, int(right), db.now(), db.today()))
    return {"correct": right, "fast": fast, "wrong_parts": [] if right else [q["key"]]}
