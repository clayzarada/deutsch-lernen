"""Word order: build a German sentence by putting word tiles in the right order (Verbs > Free practice > Word order).

Each sentence is a list of chunks in the correct order. The first `lock` chunks are already placed, so the rule being
practised can't be dodged (with "Morgen" fixed in front, the verb has to come next). Sentences where another order is
just as natural list it in `alts`. Each rule is a skill ("wo:v2", ...) in the same spaced-repetition table as the rest.
"""
import random

from . import db, decl
from .i18n import lang

RULES = {
    "v2": ("Verb second", "In a statement the conjugated verb is always the second element. Details follow the order: "
                          "time, manner, place."),
    "inv": ("Something else first", "When something other than the subject comes first, the verb stays in second place and "
                                    "the subject moves right behind it."),
    "bracket": ("Verb bracket", "With a helper verb (haben, sein, werden or a modal verb), the helper is second and the "
                                "infinitive or Partizip II goes to the very end."),
    "sep": ("Separable verbs", "The verb is second; its prefix goes to the very end of the sentence."),
    "sub": ("Verb last", "After weil, dass, wenn, ob or a question word in the middle of a sentence, the conjugated verb "
                         "goes to the end."),
    "quest": ("Questions", "W-questions start with the question word, then the verb. Yes/no questions start with the verb."),
}

# (rule, chunks separated by |, locked chunks, end mark, English, Turkish, other correct orders of the free chunks)
_S = [
    ("v2", "Mein Bruder|wohnt|seit drei Jahren|in Berlin", 1, ".", "My brother has lived in Berlin for three years.", "Erkek kardeşim üç yıldır Berlin'de oturuyor.", ["wohnt in Berlin seit drei Jahren"]),
    ("v2", "Wir|trinken|jeden Morgen|einen Kaffee", 1, ".", "We drink a coffee every morning.", "Her sabah bir kahve içeriz.", []),
    ("v2", "Die Kinder|spielen|heute|im Garten", 1, ".", "The children are playing in the garden today.", "Çocuklar bugün bahçede oynuyor.", []),
    ("v2", "Meine Kollegin|fährt|jeden Tag|mit dem Fahrrad|zur Arbeit", 1, ".", "My colleague cycles to work every day.", "İş arkadaşım her gün işe bisikletle gidiyor.", []),
    ("v2", "Ich|lerne|seit einem Jahr|Deutsch", 1, ".", "I've been learning German for a year.", "Bir yıldır Almanca öğreniyorum.", []),
    ("v2", "Anna|schreibt|ihrer Mutter|eine E-Mail", 1, ".", "Anna is writing her mother an email.", "Anna annesine bir e-posta yazıyor.", []),
    ("v2", "Der Film|beginnt|um halb neun", 1, ".", "The film starts at half past eight.", "Film sekiz buçukta başlıyor.", []),
    ("v2", "Das Restaurant|ist|sonntags|geschlossen", 1, ".", "The restaurant is closed on Sundays.", "Restoran pazar günleri kapalı.", []),
    ("inv", "Morgen|fahre|ich|nach Hamburg", 1, ".", "Tomorrow I'm going to Hamburg.", "Yarın Hamburg'a gidiyorum.", []),
    ("inv", "Am Wochenende|besuchen|wir|unsere Großeltern", 1, ".", "At the weekend we're visiting our grandparents.", "Hafta sonu büyükanne ve büyükbabamızı ziyaret ediyoruz.", []),
    ("inv", "Heute Abend|kocht|mein Mann|eine Suppe", 1, ".", "Tonight my husband is cooking a soup.", "Bu akşam kocam çorba pişiriyor.", []),
    ("inv", "Leider|habe|ich|keine Zeit", 1, ".", "Unfortunately I don't have time.", "Maalesef vaktim yok.", []),
    ("inv", "Im Sommer|ist|es|hier|sehr heiß", 1, ".", "In summer it's very hot here.", "Yazın burası çok sıcak oluyor.", []),
    ("inv", "Deshalb|lerne|ich|jeden Tag|Vokabeln", 1, ".", "That's why I learn vocabulary every day.", "Bu yüzden her gün kelime çalışıyorum.", []),
    ("inv", "Jeden Montag|geht|Lisa|ins Fitnessstudio", 1, ".", "Every Monday Lisa goes to the gym.", "Lisa her pazartesi spor salonuna gidiyor.", []),
    ("inv", "Danach|trinken|wir|einen Tee", 1, ".", "Afterwards we drink a tea.", "Sonra bir çay içiyoruz.", []),
    ("bracket", "Ich|habe|gestern|einen Film|gesehen", 1, ".", "I saw a film yesterday.", "Dün bir film izledim.", []),
    ("bracket", "Wir|müssen|morgen|früh|aufstehen", 1, ".", "We have to get up early tomorrow.", "Yarın erken kalkmamız gerekiyor.", []),
    ("bracket", "Er|ist|letztes Jahr|nach Kanada|geflogen", 1, ".", "He flew to Canada last year.", "Geçen yıl Kanada'ya uçtu.", []),
    ("bracket", "Du|kannst|heute Abend|bei uns|essen", 1, ".", "You can eat at our place tonight.", "Bu akşam bizde yemek yiyebilirsin.", []),
    ("bracket", "Sie|wird|uns|bestimmt|helfen", 1, ".", "She will certainly help us.", "Bize kesinlikle yardım edecek.", []),
    ("bracket", "Gestern|haben|wir|im Park|Fußball|gespielt", 1, ".", "Yesterday we played football in the park.", "Dün parkta futbol oynadık.", []),
    ("bracket", "Ich|möchte|einen Kaffee|bestellen", 1, ".", "I'd like to order a coffee.", "Bir kahve sipariş etmek istiyorum.", []),
    ("bracket", "Mein Vater|hat|mir|ein Fahrrad|geschenkt", 1, ".", "My father gave me a bike.", "Babam bana bir bisiklet hediye etti.", []),
    ("sep", "Der Zug|kommt|um acht Uhr|in München|an", 1, ".", "The train arrives in Munich at eight.", "Tren saat sekizde Münih'e varıyor.", []),
    ("sep", "Ich|rufe|dich|heute Abend|an", 1, ".", "I'll call you tonight.", "Bu akşam seni ararım.", []),
    ("sep", "Wir|kaufen|am Samstag|im Supermarkt|ein", 1, ".", "We go shopping at the supermarket on Saturday.", "Cumartesi süpermarkette alışveriş yapıyoruz.", []),
    ("sep", "Sie|steht|jeden Morgen|um sechs|auf", 1, ".", "She gets up at six every morning.", "Her sabah altıda kalkıyor.", []),
    ("sep", "Wann|fängt|der Kurs|an", 0, "?", "When does the course start?", "Kurs ne zaman başlıyor?", []),
    ("sep", "Er|lädt|alle Freunde|zu seiner Party|ein", 1, ".", "He invites all his friends to his party.", "Bütün arkadaşlarını partisine davet ediyor.", []),
    ("sep", "Am Sonntag|sehen|wir|zusammen|fern", 1, ".", "On Sunday we watch TV together.", "Pazar günü birlikte televizyon izliyoruz.", []),
    ("sep", "Ich|mache|das Fenster|zu", 1, ".", "I'm closing the window.", "Pencereyi kapatıyorum.", []),
    ("sub", "Ich bleibe heute zu Hause,|weil|ich|krank|bin", 1, ".", "I'm staying at home today because I'm ill.", "Bugün evde kalıyorum, çünkü hastayım.", []),
    ("sub", "Ich glaube,|dass|er|morgen|kommt", 1, ".", "I think he's coming tomorrow.", "Sanırım yarın geliyor.", []),
    ("sub", "Wir gehen spazieren,|wenn|das Wetter|schön|ist", 1, ".", "We'll go for a walk if the weather is nice.", "Hava güzel olursa yürüyüşe çıkarız.", []),
    ("sub", "Sie fragt,|ob|wir|heute Abend|Zeit|haben", 1, ".", "She's asking whether we have time tonight.", "Bu akşam vaktimiz olup olmadığını soruyor.", []),
    ("sub", "Er lernt Deutsch,|weil|er|in Wien|arbeiten|möchte", 1, ".", "He's learning German because he wants to work in Vienna.", "Almanca öğreniyor, çünkü Viyana'da çalışmak istiyor.", []),
    ("sub", "Ich weiß nicht,|wann|der Bus|abfährt", 1, ".", "I don't know when the bus leaves.", "Otobüsün ne zaman kalktığını bilmiyorum.", []),
    ("sub", "Weißt du,|dass|Anna|gestern|angerufen|hat", 1, "?", "Do you know that Anna called yesterday?", "Anna'nın dün aradığını biliyor musun?", []),
    ("sub", "Kannst du mir sagen,|wo|der Bahnhof|ist", 1, "?", "Can you tell me where the station is?", "Bana istasyonun nerede olduğunu söyleyebilir misin?", []),
    ("quest", "Wann|kommst|du|nach Hause", 0, "?", "When are you coming home?", "Eve ne zaman geliyorsun?", []),
    ("quest", "Kommst|du|morgen|mit", 0, "?", "Are you coming along tomorrow?", "Yarın sen de geliyor musun?", []),
    ("quest", "Wo|wohnt|deine Schwester", 0, "?", "Where does your sister live?", "Kız kardeşin nerede oturuyor?", []),
    ("quest", "Hast|du|schon|gegessen", 0, "?", "Have you eaten yet?", "Yemek yedin mi?", []),
    ("quest", "Warum|lernst|du|Deutsch", 0, "?", "Why are you learning German?", "Neden Almanca öğreniyorsun?", []),
    ("quest", "Was|machst|du|am Wochenende", 0, "?", "What are you doing at the weekend?", "Hafta sonu ne yapıyorsun?", []),
    ("quest", "Können|Sie|mir|helfen", 0, "?", "Can you help me?", "Bana yardım edebilir misiniz?", []),
    ("quest", "Wie lange|bleibt|ihr|in Rom", 0, "?", "How long are you staying in Rome?", "Roma'da ne kadar kalıyorsunuz?", []),
]
SENTENCES = [{"id": i, "rule": r, "chunks": c.split("|"), "lock": lock, "end": end, "en": en, "tr": tr, "alts": alts}
             for i, (r, c, lock, end, en, tr, alts) in enumerate(_S)]
KEYS = [f"wo:{r}" for r in RULES]


def _norm(chunks):
    return decl.norm(" ".join(chunks))


# The first word of a question would give the answer away with its capital letter, so its tile is lower-case.
# (Nouns and Sie keep their capital wherever they stand.)
_LOWER_OK = {"wann", "kommst", "wo", "hast", "warum", "was", "können", "wie"}


def _tile(text, first):
    if first and text.split()[0].lower() in _LOWER_OK:
        return text[:1].lower() + text[1:]
    return text


def next_sentence(rules=None, recent=()):
    rules = [r for r in (rules or []) if r in RULES] or list(RULES)
    pool = [s for s in SENTENCES if s["rule"] in rules and s["id"] not in set(recent or ())] or \
           [s for s in SENTENCES if s["rule"] in rules]
    st, now = decl._state(), db.now()
    weights = [decl._weight(f"wo:{s['rule']}", st, set(), now) for s in pool]
    s = random.choices(pool, weights)[0]
    free = list(range(s["lock"], len(s["chunks"])))
    for _ in range(10):  # never hand out the tiles already in the right order
        random.shuffle(free)
        if free != sorted(free) or len(free) < 2:
            break
    label, why = RULES[s["rule"]]
    return {"id": s["id"], "rule": s["rule"], "label": label, "why": why, "end": s["end"],
            "meaning": s["tr"] if lang() == "tr" else s["en"],
            "locked": s["chunks"][:s["lock"]],
            "tiles": [{"i": i, "text": _tile(s["chunks"][i], i == 0)} for i in free]}


def check(sid, order):
    """order: tile indexes in the learner's order. Updates the rule's skill and logs the answer."""
    s = SENTENCES[int(sid)]
    given = [s["chunks"][int(i)] for i in order]
    want = s["chunks"][s["lock"]:]
    ok_orders = [_norm(want)] + [decl.norm(a) for a in s["alts"]]
    right = len(given) == len(want) and _norm(given) in ok_orders
    decl.update_skill(f"wo:{s['rule']}", right, False)
    db.ex("INSERT INTO answers(source, topic, correct, ts, date) VALUES('verbs','Verbs: word order',?,?,?)",
          (int(right), db.now(), db.today()))
    return {"correct": right, "solution": " ".join(s["chunks"]) + s["end"], "why": RULES[s["rule"]][1]}


def progress():
    st = decl._state()
    return [{"rule": r, "label": RULES[r][0], "box": st.get(f"wo:{r}", {}).get("box", 0)} for r in RULES]
