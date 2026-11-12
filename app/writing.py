"""Writing desk: exam-style writing tasks, marking by Claude, and the history of everything written.
The built-in tasks follow the formats of the Goethe-Zertifikat writing papers (written for this app)."""
import json
import re

from . import ai, db

# id, level, kind, title, task, points, words, minutes
TASKS = [
    ("b1-sport", "B1", "Informal email", "Ein neuer Sport",
     "Sie haben vor kurzem mit einem neuen Sport angefangen. Schreiben Sie Ihrer Freundin Lea eine E-Mail.",
     ["Beschreiben Sie: Welcher Sport ist es und wo trainieren Sie?", "Begründen Sie: Warum gefällt Ihnen dieser Sport?",
      "Machen Sie einen Vorschlag für ein gemeinsames Training."], 80, 20),
    ("b1-forum-sport", "B1", "Forum post", "Jeden Tag Sport?",
     "In einem Internetforum diskutieren Leute über die Frage: „Sollte man jeden Tag Sport machen?“ Schreiben Sie Ihre Meinung.",
     ["Sagen Sie, was Sie davon halten.", "Geben Sie ein Beispiel aus Ihrem Leben.", "Nennen Sie einen Nachteil."], 80, 20),
    ("b1-kurs", "B1", "Short formal message", "Absage für den Kurs",
     "Sie können am Montag nicht zum Deutschkurs kommen. Schreiben Sie Ihrer Kursleiterin, Frau Weber.",
     ["Entschuldigen Sie sich höflich.", "Erklären Sie, warum Sie nicht kommen können.", "Fragen Sie nach den Hausaufgaben."], 40, 15),
    ("b1-wochenende", "B1", "Informal email", "Ein besonderes Wochenende",
     "Ihr Freund Jonas hat Sie gefragt, wie Ihr Wochenende war. Antworten Sie ihm.",
     ["Was haben Sie gemacht und mit wem?", "Was war besonders schön oder nicht so schön?", "Laden Sie Jonas zu etwas ein."], 80, 20),
    ("b2-homeoffice", "B2", "Forum post", "Homeoffice: Fluch oder Segen?",
     "In einem Forum zum Thema Arbeit wird diskutiert, ob Homeoffice die bessere Art zu arbeiten ist. Schreiben Sie einen Beitrag.",
     ["Nennen Sie Vorteile und Nachteile.", "Berichten Sie von eigenen Erfahrungen oder denen von Bekannten.",
      "Formulieren Sie Ihre Meinung und begründen Sie sie."], 150, 30),
    ("b2-beschwerde", "B2", "Formal letter", "Beschwerde beim Fitnessstudio",
     "Ihr Fitnessstudio hat Ihren Kurs dreimal ohne Ankündigung abgesagt. Schreiben Sie eine Beschwerde an die Leitung.",
     ["Beschreiben Sie, was passiert ist.", "Erklären Sie, welche Folgen das für Sie hatte.",
      "Fordern Sie eine Lösung (z. B. eine Erstattung)."], 120, 25),
    ("b2-sprachschule", "B2", "Formal letter", "Anfrage an eine Sprachschule",
     "Sie möchten im Sommer einen Intensivkurs an einer Sprachschule in Leipzig machen. Schreiben Sie an die Schule.",
     ["Stellen Sie sich kurz vor und nennen Sie Ihr Sprachniveau.", "Fragen Sie nach Kurszeiten, Preisen und Unterkunft.",
      "Erkundigen Sie sich nach einem Zertifikat am Ende."], 120, 25),
    ("c1-autofrei", "C1", "Argumentative essay", "Autofreie Innenstädte",
     "Immer mehr Städte überlegen, Autos aus dem Zentrum zu verbannen. Schreiben Sie einen Text, in dem Sie dazu Stellung nehmen.",
     ["Stellen Sie die Situation dar.", "Wägen Sie Argumente dafür und dagegen ab.",
      "Gehen Sie auf mögliche Folgen für Bewohner und Geschäfte ein.", "Kommen Sie zu einem begründeten Schluss."], 230, 60),
    ("c1-lernen", "C1", "Opinion piece", "Lernen mit dem Bildschirm",
     "Eine Zeitschrift sucht Beiträge zur Frage, ob digitales Lernen den Unterricht im Klassenzimmer ersetzen kann.",
     ["Beschreiben Sie, wie sich das Lernen verändert hat.", "Vergleichen Sie digitales Lernen mit Präsenzunterricht.",
      "Begründen Sie Ihre Position mit Beispielen."], 230, 60),
    ("c1-stadt", "C1", "Formal letter", "Brief an die Stadtverwaltung",
     "In Ihrem Viertel soll ein Sportplatz einem Parkhaus weichen. Schreiben Sie an die Stadtverwaltung.",
     ["Erklären Sie, warum der Sportplatz wichtig ist.", "Gehen Sie auf das Argument fehlender Parkplätze ein.",
      "Schlagen Sie eine Alternative vor.", "Bitten Sie um eine Antwort."], 200, 50),
]
TASK = {t[0]: dict(zip(("id", "level", "kind", "title", "task", "points", "words", "minutes"), t)) for t in TASKS}


def tasks():
    return list(TASK.values())


def word_count(text):
    return len(re.findall(r"[\wÄÖÜäöüß'-]+", text or ""))


def _sentence_with(text, snippet):
    """The sentence of the text that contains snippet, for the Mistake Book."""
    i = text.find(snippet)
    if i < 0:
        return ""
    start = max(text.rfind(c, 0, i) for c in ".!?\n") + 1
    ends = [j for j in (text.find(c, i + len(snippet)) for c in ".!?\n") if j >= 0]
    end = (min(ends) + 1) if ends else len(text)
    return text[start:end].strip()


def grade(body):
    text = (body.get("text") or "").strip()
    words = word_count(text)
    if words < 15:
        raise db.UserError("Write at least a few sentences (15 words or more) before checking.")
    task = {k: body.get(k) for k in ("task_id", "title", "kind", "task", "points", "words", "level")}
    level = task.get("level") or db.get_settings()["level"]
    result = ai.grade_writing(task, text, level, words)
    # keep only corrections that really appear in the text, in order
    seen, corrections = set(), []
    for c in result["corrections"]:
        o = (c.get("original") or "").strip()
        if o and o in text and o != (c.get("corrected") or "").strip() and o not in seen:
            seen.add(o)
            corrections.append(c)
    result["corrections"] = corrections
    wid = db.ex("INSERT INTO writings(created_at, date, task_id, title, kind, level, task, text, words, seconds, score, result) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (db.now(), db.today(), task.get("task_id"), task.get("title") or "My own topic", task.get("kind"), level,
                 json.dumps(task, ensure_ascii=False), text, words, int(body.get("seconds") or 0), result["overall"],
                 json.dumps(result, ensure_ascii=False)))
    items = []
    for c in corrections:
        if c.get("category") == "style":
            continue
        sentence = _sentence_with(text, c["original"])
        items.append({"topic": c.get("topic", ""), "wrong": c["original"], "correct": c["corrected"],
                      "explanation": c.get("explanation", ""), "context": f"Writing: {task.get('title') or 'own topic'}",
                      "question": f"Correct the mistake in this sentence:\n\n{sentence}" if sentence else "",
                      "full_correct": sentence.replace(c["original"], c["corrected"], 1) if sentence else ""})
    db.add_mistakes("writing", items)
    return get(wid) | {"new_mistakes": len(items)}


def get(wid):
    w = db.q1("SELECT * FROM writings WHERE id=?", (wid,))
    if not w:
        raise db.UserError("That piece of writing doesn't exist.")
    w["task"] = json.loads(w["task"])
    w["result"] = json.loads(w["result"])
    return w


def history():
    return db.q("SELECT id, created_at, task_id, title, kind, level, words, score FROM writings ORDER BY id DESC LIMIT 60")


def recent_for_coach():
    out = []
    for w in db.q("SELECT date, title, level, words, score, result FROM writings ORDER BY id DESC LIMIT 5"):
        r = json.loads(w["result"])
        out.append({"date": w["date"], "task": w["title"], "level": w["level"], "words": w["words"], "score": w["score"],
                    "criteria": {c["name"]: c["score"] for c in r.get("criteria", [])}, "passes": r.get("passes")})
    return out
