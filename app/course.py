"""The Declensions journey: a fixed course of stages ("planets"), each with a lesson, a chart to fill in, a drill,
a reading with gaps, flashcards and a checkpoint. Questions come from the rule engine in decl.py; this module holds
the course content, decides what each stage asks, and tracks which steps are done."""
import random
import re

from . import db, decl, i18n

CASES = decl.CASES


def K(family, cases=CASES):
    return [k for k in decl.KEYS[family] if decl.key_case(k) in cases]


def T(prefix, case=None):
    return [k for k, v in decl.TRIGGERS.items() if k.startswith(prefix) and (case is None or v[1] == case)]


def G(mode, keys, w=1.0):
    return {"mode": mode, "keys": keys, "w": w}


THE, DEM = "the", "this / every / which"

# Lesson blocks: ("p", text) ("h", heading) ("rule", text) ("tip", text) ("ex", [(german, english), ...])
# ("table", table id, cases to show or None, column indexes to show or None). **bold** marks the endings.
STAGES = [
    {
        "id": "nom", "planet": "Nomina Prime", "title": "Nominativ", "hue": 205, "ring": False,
        "blurb": "The subject. Where every noun starts: der, die, das.",
        "lesson": [
            ("p", "Every German noun phrase wears a small badge that says what job it does in the sentence. That badge is "
                  "the **case**, and it shows up as an ending on the article. There are only four cases, and you will take "
                  "them one planet at a time."),
            ("h", "The nominative is the subject"),
            ("p", "The nominative marks **who or what does the action**. It is also the form you find in the dictionary. "
                  "Ask *wer?* (who?) or *was?* (what?) to find it."),
            ("ex", [("**Der** Hund schläft.", "The dog is sleeping."), ("**Die** Frau liest.", "The woman is reading."),
                    ("**Das** Kind spielt.", "The child is playing."), ("**Die** Kinder spielen.", "The children are playing.")]),
            ("table", "def", ["nom"], None),
            ("rule", "After **sein**, **werden** and **bleiben** the noun is nominative too, because it is the same thing as "
                     "the subject: *Das ist **der** Lehrer.*"),
            ("h", "The key idea: signal endings"),
            ("p", "Look at the last letter of each article: de**r**, di**e**, da**s**, di**e**. Those four letters, "
                  "**-r, -e, -s, -e**, are the nominative signals. Other words carry the same signals:"),
            ("table", "dies", ["nom"], None),
            ("p", "*jeder* (every), *welcher* (which) and *mancher* (some) work exactly like *dieser*. Learn the signals "
                  "once and you get all of these words for free. Every later planet is just a new row of signals."),
            ("tip", "The signals only help if you know the noun's gender. Always learn a noun with its article: not "
                    "*Tisch*, but *der Tisch*. Endings help: -ung, -heit, -keit, -schaft, -ion are *die*; -chen and -lein "
                    "are *das*."),
        ],
        "tables": [("def", ["nom"], None), ("dies", ["nom"], None)],
        "pool": lambda: [G("plain", K("def", ["nom"]), 3), G("plain", K("dies", ["nom"]), 2),
                         G("dsent", K("def", ["nom"]) + K("dies", ["nom"]), 3), G("plain", decl.KEYS["gender"], 2),
                         G("plain", ["wer:nom"], .4)],
        "reading": ("Meine Straße",
                    "Das ist meine Straße. {Der|the|def:nom:m} Supermarkt ist klein, aber {die|the|def:nom:f} Apotheke ist groß. "
                    "{Das|the|def:nom:n} Café neben der Apotheke ist neu. {Die|the|def:nom:pl} Nachbarn sind nett. "
                    "{Dieser|this|dies:nom:m} Park hier ist sehr ruhig, und {diese|this|dies:nom:f} Bank ist mein Lieblingsplatz. "
                    "{Dieses|this|dies:nom:n} Haus gehört meiner Tante. {Welcher|which|dies:nom:m} Bus fährt zum Bahnhof? "
                    "{Jede|every|dies:nom:f} Linie fährt dorthin. {Die|the|def:nom:pl} Kinder spielen draußen, und "
                    "{der|the|def:nom:m} Hund schläft."),
        "cards": [
            ("Nominativ: the — masculine / feminine / neuter / plural", "der · die · das · die", ""),
            ("Nominativ: dieser — masculine / feminine / neuter / plural", "dieser · diese · dieses · diese", "Signals: -r, -e, -s, -e"),
            ("When do you use the nominative?", "For the subject (who or what does it), and after sein, werden, bleiben.",
             "Der Mann ist der Lehrer."),
            ("Question words for the nominative", "wer? (people) · was? (things)", ""),
            ("jeder, welcher, mancher: which endings do they take?", "The same as dieser: jeder, jede, jedes · welcher, welche, welches", ""),
            ("Nouns ending in -ung, -heit, -keit, -schaft, -ion: which gender?", "die (feminine)", "die Wohnung, die Freiheit, die Nation"),
            ("Nouns ending in -chen or -lein: which gender?", "das (neuter)", "das Mädchen, das Brötchen"),
        ],
    },
    {
        "id": "akk", "planet": "Akkusaturn", "title": "Akkusativ", "hue": 22, "ring": True,
        "blurb": "The direct object. Only one thing changes: der becomes den.",
        "lesson": [
            ("p", "The accusative marks the **direct object**: the person or thing the action is done to. Ask *wen?* "
                  "(whom?) or *was?* (what?)."),
            ("ex", [("Ich sehe **den** Hund.", "I see the dog."), ("Ich sehe **die** Frau.", "I see the woman."),
                    ("Ich sehe **das** Kind.", "I see the child."), ("Ich sehe **die** Kinder.", "I see the children.")]),
            ("rule", "Good news: in the accusative **only the masculine changes**. *der* becomes *de**n***. Feminine, neuter "
                     "and plural look exactly like the nominative."),
            ("table", "def", ["nom", "akk"], None),
            ("p", "The signal **-n** appears on every masculine der-word: *dieser* becomes *diese**n***, *jeder* becomes "
                  "*jede**n***, *welcher* becomes *welche**n***."),
            ("h", "Prepositions that always take the accusative"),
            ("p", "After these five the noun is accusative, every time, whatever the verb is doing:"),
            ("rule", "**durch** (through) · **für** (for) · **gegen** (against) · **ohne** (without) · **um** (around)"),
            ("ex", [("Das Geschenk ist für **den** Lehrer.", "The present is for the teacher."),
                    ("Wir gehen durch **den** Park.", "We walk through the park.")]),
            ("h", "Pronouns change too"),
            ("table", "pers", None, [0, 1]),
            ("tip", "The -n shows up in the pronoun as well: de**n** Mann → ih**n**. And notice *sie*, *es* and *sie* don't "
                    "change at all, just like *die*, *das* and *die*."),
        ],
        "tables": [("def", ["nom", "akk"], None), ("dies", ["akk"], None), ("pers", None, [1])],
        "pool": lambda: [G("plain", K("def", ["akk"]), 3), G("plain", K("dies", ["akk"]), 2), G("plain", K("pers", ["akk"]), 3),
                         G("plain", T("trig:p:", "akk") + T("trig:v:", "akk"), 2), G("plain", ["wer:akk"], .4),
                         G("dsent", K("def", ["akk"]) + K("dies", ["akk"]), 4)],
        "reading": ("Am Samstag",
                    "Am Samstag gehe ich einkaufen. Ich brauche {den|the|def:akk:m} Rucksack und {die|the|def:akk:f} Tasche. "
                    "Im Supermarkt kaufe ich {das|the|def:akk:n} Brot und {die|the|def:akk:pl} Äpfel. Dann sehe ich Anna. "
                    "Ich kenne {sie|her|pers:akk:sie} schon lange. Sie fragt {mich|me|pers:akk:ich}: „Hast du "
                    "{den|the|def:akk:m} Film gesehen?“ Ich antworte: „Nein, aber ich kenne {das|the|def:akk:n} Buch.“ "
                    "Wir gehen durch {den|the|def:akk:m} Park und um {die|the|def:akk:f} Schule. „Das Geschenk in der Tasche "
                    "ist für {dich|you|pers:akk:du}“, sage ich. Ohne {diesen|this|dies:akk:m} Rucksack gehe ich nie aus dem "
                    "Haus. {Wen|whom|wer:akk} treffen wir heute Abend?"),
        "cards": [
            ("Akkusativ: the — masculine / feminine / neuter / plural", "den · die · das · die", "Only the masculine changes."),
            ("The five prepositions that always take the accusative", "durch · für · gegen · ohne · um", ""),
            ("ich, du, er → Akkusativ", "mich · dich · ihn", ""),
            ("sie, es, wir, ihr, sie, Sie → Akkusativ", "sie · es · uns · euch · sie · Sie", ""),
            ("Question words for the accusative", "wen? (people) · was? (things)", ""),
            ("dieser, jeder, welcher → Akkusativ masculine", "diesen · jeden · welchen", ""),
            ("When do you use the accusative?", "For the direct object, and after durch, für, gegen, ohne, um.",
             "Ich kaufe den Tisch. Das ist für den Lehrer."),
        ],
    },
    {
        "id": "dat", "planet": "Dativa", "title": "Dativ", "hue": 265, "ring": False,
        "blurb": "The receiver. New signals: -m, -r, -m, -n.",
        "lesson": [
            ("p", "The dative marks the **indirect object**: the person who receives something or benefits. Ask *wem?* "
                  "(to whom?)."),
            ("ex", [("Ich gebe **dem** Mann das Buch.", "I give the man the book."),
                    ("Ich gebe **der** Frau das Buch.", "I give the woman the book."),
                    ("Ich gebe **dem** Kind das Buch.", "I give the child the book."),
                    ("Ich gebe **den** Kinder**n** das Buch.", "I give the children the book.")]),
            ("rule", "The dative signals are **-m, -r, -m, -n**. Everything changes here, so this row needs real drilling."),
            ("table", "def", ["nom", "akk", "dat"], None),
            ("tip", "Two traps. First: dative feminine is *der*, which looks masculine but isn't. Second: in the dative "
                    "plural the **noun adds -n too**: *mit den Kinder**n***, unless it already ends in -n or -s."),
            ("h", "Prepositions that always take the dative"),
            ("rule", "**aus** · **außer** · **bei** · **mit** · **nach** · **seit** · **von** · **zu** · **gegenüber**"),
            ("ex", [("Ich fahre mit **dem** Bus.", "I go by bus."), ("Sie kommt aus **der** Schule.", "She comes out of the school."),
                    ("Nach **dem** Training essen wir.", "After training we eat.")]),
            ("p", "Some of these merge with the article: *bei dem* → **beim**, *von dem* → **vom**, *zu dem* → **zum**, "
                  "*zu der* → **zur**."),
            ("h", "Verbs that take the dative"),
            ("p", "A handful of common verbs take a dative object where English makes you expect a direct object:"),
            ("rule", "**helfen** · **danken** · **gehören** · **gefallen** · **antworten** · **glauben** · **folgen** · "
                     "**gratulieren** · **vertrauen** · **zuhören** · **schmecken** · **passen**"),
            ("ex", [("Ich helfe **dem** Lehrer.", "I help the teacher."), ("Das Buch gehört **der** Frau.", "The book belongs to the woman.")]),
            ("h", "Dative pronouns"),
            ("table", "pers", None, [0, 1, 2]),
            ("tip", "The signals repeat in the pronouns: de**m** → ih**m**, de**r** → ih**r**, de**n** → ihne**n**."),
        ],
        "tables": [("def", ["nom", "akk", "dat"], None), ("dies", ["dat"], None), ("pers", None, [1, 2])],
        "pool": lambda: [G("plain", K("def", ["dat"]), 3), G("plain", K("dies", ["dat"]), 2), G("plain", K("pers", ["dat"]), 3),
                         G("plain", T("trig:p:", "dat") + T("trig:v:", "dat"), 3), G("plain", ["noun:dat:pl"], 1),
                         G("plain", ["wer:dat"], .4), G("dsent", K("def", ["dat"]) + K("dies", ["dat"]), 4)],
        "reading": ("Nach dem Training",
                    "Nach {dem|the|def:dat:n} Training fahre ich mit {der|the|def:dat:f} Trainerin in die Stadt. Wir kommen aus "
                    "{dem|the|def:dat:n} Fitnessstudio und sprechen mit {den|the|def:dat:pl} Kinder{n||noun:dat:pl} vor der Tür. "
                    "Ein Junge zeigt {der|the|def:dat:f} Trainerin sein Fahrrad. Das Fahrrad gehört {dem|the|def:dat:m} Bruder "
                    "von Max. Die Trainerin hilft {dem|the|def:dat:n} Kind, und das Kind dankt {ihr|her|pers:dat:sie}. Dann "
                    "fragt sie mich: „Gefällt {dir|you|pers:dat:du} die Stadt?“ – „Ja, sie gefällt {mir|me|pers:dat:ich} sehr.“ "
                    "Seit {diesem|this|dies:dat:m} Sommer wohne ich hier. {Wem|to whom|wer:dat} gehört eigentlich die Tasche dort?"),
        "cards": [
            ("Dativ: the — masculine / feminine / neuter / plural", "dem · der · dem · den (+n on the noun)", "Signals: -m, -r, -m, -n"),
            ("Prepositions that always take the dative", "aus · außer · bei · mit · nach · seit · von · zu · gegenüber", ""),
            ("Common verbs that take the dative", "helfen · danken · gehören · gefallen · antworten · glauben · folgen · gratulieren · vertrauen · zuhören · schmecken · passen", ""),
            ("ich, du, er, sie, es → Dativ", "mir · dir · ihm · ihr · ihm", ""),
            ("wir, ihr, sie, Sie → Dativ", "uns · euch · ihnen · Ihnen", ""),
            ("Question word for the dative", "wem?", ""),
            ("Dative plural: what happens to the noun?", "It adds -n: mit den Kindern.", "Not if it already ends in -n or -s: mit den Frauen, mit den Autos."),
            ("bei dem, von dem, zu dem, zu der →", "beim · vom · zum · zur", ""),
        ],
    },
    {
        "id": "two", "planet": "Wechsel-Nebel", "title": "Wo oder wohin?", "hue": 320, "ring": False, "nebula": True,
        "blurb": "Nine prepositions that switch between accusative and dative.",
        "lesson": [
            ("p", "Nine prepositions can take **either** the accusative or the dative. The sentence's meaning decides."),
            ("rule", "**an** · **auf** · **hinter** · **in** · **neben** · **über** · **unter** · **vor** · **zwischen**"),
            ("h", "One question decides"),
            ("p", "Is something **moving to a new place**? Ask *wohin?* (where to?) and use the **accusative**. Is it "
                  "**already there**? Ask *wo?* (where?) and use the **dative**."),
            ("ex", [("Ich gehe in **den** Park.", "I'm going into the park. (wohin? → accusative)"),
                    ("Ich bin in **dem** Park.", "I'm in the park. (wo? → dative)"),
                    ("Ich lege das Buch auf **den** Tisch.", "I put the book on the table. (wohin?)"),
                    ("Das Buch liegt auf **dem** Tisch.", "The book is lying on the table. (wo?)")]),
            ("h", "Verb pairs give it away"),
            ("p", "German has pairs of verbs: one means *put it there* (accusative), the other means *it is there* (dative)."),
            ("ex", [("stellen → stehen", "to stand something somewhere → to be standing"),
                    ("legen → liegen", "to lay something down → to be lying"),
                    ("setzen → sitzen", "to sit someone down → to be sitting"),
                    ("hängen → hängen", "to hang something up → to be hanging")]),
            ("tip", "Movement **inside** one place is still dative: *Ich laufe in **dem** Park* means I'm running around "
                    "in the park. Accusative needs a change of place: *Ich laufe in **den** Park*."),
            ("p", "Contractions you will see all the time: *in dem* → **im**, *an dem* → **am**, *in das* → **ins**, "
                  "*an das* → **ans**."),
        ],
        "tables": [],
        "pool": lambda: [G("plain", T("trig:w:"), 4), G("wsent", K("def", ["akk", "dat"]), 5),
                         G("wsent", K("dies", ["akk", "dat"]), 1)],
        "reading": ("Ich räume auf",
                    "Ich räume mein Zimmer auf. Ich lege die Bücher auf {den|the|def:akk:m} Tisch. Jetzt liegen sie auf "
                    "{dem|the|def:dat:m} Tisch. Die Lampe hänge ich über {das|the|def:akk:n} Bett; sie hängt jetzt über "
                    "{dem|the|def:dat:n} Bett. Die Katze läuft unter {den|the|def:akk:m} Stuhl und schläft dann unter "
                    "{dem|the|def:dat:m} Stuhl. Ich lege die Jacke in {die|the|def:akk:f} Tasche. Der Schlüssel ist schon in "
                    "{der|the|def:dat:f} Tasche. Das Fahrrad stelle ich hinter {das|the|def:akk:n} Haus, und das Auto steht vor "
                    "{dem|the|def:dat:n} Haus. Zum Schluss hänge ich die Bilder an {die|the|def:akk:f} Wand. Jetzt hängen sie an "
                    "{der|the|def:dat:f} Wand, neben {dem|the|def:dat:n} Fenster."),
        "cards": [
            ("The nine two-way prepositions", "an · auf · hinter · in · neben · über · unter · vor · zwischen", ""),
            ("Two-way preposition + movement to a new place (wohin?)", "Akkusativ", "Ich gehe in den Park."),
            ("Two-way preposition + location (wo?)", "Dativ", "Ich bin in dem Park (im Park)."),
            ("stellen / stehen: which case after a two-way preposition?", "stellen → Akkusativ · stehen → Dativ",
             "Ich stelle die Flasche auf den Tisch. Die Flasche steht auf dem Tisch."),
            ("legen / liegen: which case?", "legen → Akkusativ · liegen → Dativ", "Ich lege das Buch auf das Bett. Es liegt auf dem Bett."),
            ("in dem, an dem, in das, an das →", "im · am · ins · ans", ""),
        ],
    },
    {
        "id": "ein", "planet": "Planet Ein", "title": "ein, kein, mein", "hue": 150, "ring": False,
        "blurb": "The same signals, with three famous gaps.",
        "lesson": [
            ("p", "*ein*, *kein* and the possessives (*mein, dein, sein, ihr, unser, euer, Ihr*) are called **ein-words**. "
                  "They use the same signal endings you already know from *dieser*, with one twist."),
            ("rule", "In **three slots an ein-word has no ending at all**: nominative masculine, nominative neuter and "
                     "accusative neuter. *ein Mann, ein Kind, ein Kind.*"),
            ("table", "ein", ["nom", "akk", "dat"], None),
            ("p", "Compare with *dieser*: dies**er** Mann but **ein** Mann; dies**es** Kind but **ein** Kind. Everywhere "
                  "else the endings match: dies**en** / ein**en**, dies**em** / ein**em**, dies**er** / ein**er**."),
            ("h", "kein and the possessives"),
            ("p", "*kein* is just *ein* with a k, and it also has a plural: *keine Kinder, mit keinen Kindern*. The "
                  "possessives take exactly the same endings:"),
            ("table", "mein", ["nom", "akk", "dat"], None),
            ("ex", [("Das ist **mein** Bruder.", "That is my brother. (nominative masculine: no ending)"),
                    ("Ich sehe **meinen** Bruder.", "I see my brother."),
                    ("Ich helfe **meinem** Bruder.", "I help my brother."),
                    ("Ich fahre mit **meiner** Schwester.", "I travel with my sister.")]),
            ("h", "Two decisions for a possessive"),
            ("p", "First pick the word by the **owner**: ich → mein, du → dein, er → sein, sie → ihr, es → sein, "
                  "wir → unser, ihr → euer, sie → ihr, Sie → Ihr. Then add the ending by the **thing owned**: its gender, "
                  "number and case."),
            ("tip", "*euer* drops an e when it gets an ending: **eure** Mutter, mit **eurem** Vater."),
        ],
        "tables": [("ein", ["nom", "akk", "dat"], None), ("kein", ["nom", "akk", "dat"], None), ("mein", ["nom", "akk", "dat"], None)],
        "pool": lambda: [G("plain", K("ein", ["nom", "akk", "dat"]), 3), G("plain", K("poss", ["nom", "akk", "dat"]), 4),
                         G("dsent", K("ein", ["nom", "akk", "dat"]) + K("poss", ["nom", "akk", "dat"]), 4)],
        "reading": ("Mein Bruder Max",
                    "Das ist {mein|my|poss:nom:m} Bruder Max. Er hat {eine|a|ein:akk:f} Wohnung in Berlin und "
                    "{einen|a|ein:akk:m} Hund, aber {kein|no|ein:akk:n} Auto. {Seine|his|poss:nom:f} Freundin heißt Lena. Sie "
                    "arbeitet in {einem|a|ein:dat:n} Büro und fährt jeden Tag mit {ihrem|her|poss:dat:n} Fahrrad. Am Wochenende "
                    "besuchen sie {unsere|our|poss:akk:pl} Eltern. Max bringt {seiner|his|poss:dat:f} Mutter Blumen mit, und Lena "
                    "schenkt {unserem|our|poss:dat:m} Vater {ein|a|ein:akk:n} Buch. „Habt ihr {eure|your|poss:akk:pl} Jacken?“, "
                    "fragt die Mutter. Wir haben {keine|no|ein:akk:pl} Zeit mehr und gehen schnell los."),
        "cards": [
            ("ein in the nominative: masculine / feminine / neuter", "ein · eine · ein", ""),
            ("ein in the accusative: masculine / feminine / neuter", "einen · eine · ein", ""),
            ("ein in the dative: masculine / feminine / neuter", "einem · einer · einem", ""),
            ("kein in the plural: Nominativ / Akkusativ / Dativ", "keine · keine · keinen", ""),
            ("The possessives for ich, du, er, sie, es, wir, ihr, sie, Sie", "mein · dein · sein · ihr · sein · unser · euer · ihr · Ihr", ""),
            ("In which three slots do ein-words have no ending?", "Nominative masculine, nominative neuter, accusative neuter.",
             "ein Mann · ein Kind · (ich sehe) ein Kind"),
            ("What happens to euer when it takes an ending?", "It drops an e: eure, euren, eurem, eurer.", ""),
        ],
    },
    {
        "id": "gen", "planet": "Genitara", "title": "Genitiv", "hue": 172, "ring": True,
        "blurb": "Possession. des and der, and an -s on the noun.",
        "lesson": [
            ("p", "The genitive shows **possession**, like English *of the* or *'s*. Ask *wessen?* (whose?). The owner "
                  "comes second: *das Auto **des Mannes*** is the man's car."),
            ("table", "def", ["nom", "akk", "dat", "gen"], None),
            ("rule", "Only two forms to learn: **des** for masculine and neuter, **der** for feminine and plural."),
            ("p", "Masculine and neuter **nouns add -s or -es** as well. Short words and words ending in -s, -ß, -z or "
                  "-sch take **-es**: *des Mann**es**, des Haus**es***. Longer words take **-s**: *des Lehrer**s**, des "
                  "Auto**s***. Feminine and plural nouns don't change."),
            ("ex", [("das Auto **des** Lehrer**s**", "the teacher's car"), ("die Tasche **der** Frau", "the woman's bag"),
                    ("die Farbe **des** Haus**es**", "the color of the house"), ("die Eltern **der** Kinder", "the children's parents")]),
            ("h", "ein-words in the genitive"),
            ("table", "ein", ["gen"], None),
            ("p", "The possessives follow: *das Auto **meines** Vaters, die Wohnung **meiner** Schwester*."),
            ("h", "Prepositions with the genitive"),
            ("rule", "**wegen** (because of) · **trotz** (despite) · **während** (during) · **statt** (instead of) · "
                     "**innerhalb** (inside) · **außerhalb** (outside)"),
            ("ex", [("Wegen **des** Wetters bleiben wir hier.", "Because of the weather we're staying here."),
                    ("Während **der** Pause trinke ich Kaffee.", "During the break I drink coffee.")]),
            ("tip", "In everyday speech people often say *von dem* instead: *das Auto von dem Lehrer*. You need the "
                    "genitive for writing, reading and exams."),
        ],
        "tables": [("def", ["nom", "akk", "dat", "gen"], None), ("ein", ["gen"], None), ("mein", ["gen"], None)],
        "pool": lambda: [G("plain", K("def", ["gen"]), 3), G("plain", K("dies", ["gen"]) + K("ein", ["gen"]) + K("poss", ["gen"]), 3),
                         G("plain", ["noun:gen:m", "noun:gen:n"], 1.5), G("plain", T("trig:p:", "gen"), 1.5),
                         G("plain", ["wer:gen"], .4), G("dsent", K("def", ["gen"]) + K("ein", ["gen"]) + K("poss", ["gen"]), 4)],
        "reading": ("Das Haus meines Onkels",
                    "Das ist das Haus {meines|my|poss:gen:m} Onkels. Die Farbe {des|the|def:gen:n} Haus{es||noun:gen:n} ist gelb. "
                    "Wegen {des|the|def:gen:n} Wetters bleiben wir heute drinnen. Das Auto {der|the|def:gen:f} Nachbarin steht "
                    "vor der Tür, und die Fahrräder {der|the|def:gen:pl} Kinder liegen im Garten. Trotz {des|the|def:gen:m} "
                    "Regen{s||noun:gen:m} spielt der Hund draußen. Während {der|the|def:gen:f} Pause trinken wir Kaffee. Am Ende "
                    "{dieses|this|dies:gen:m} Tages kommt die Tochter {einer|a|ein:gen:f} Freundin zu Besuch. "
                    "{Wessen|whose|wer:gen} Jacke ist das? Das ist die Jacke {eines|a|ein:gen:n} Kindes."),
        "cards": [
            ("Genitiv: the — masculine / feminine / neuter / plural", "des (+s) · der · des (+s) · der", ""),
            ("Prepositions with the genitive", "wegen · trotz · während · statt · innerhalb · außerhalb", ""),
            ("Genitive masculine and neuter: what happens to the noun?", "It adds -s or -es: des Lehrers, des Hauses.",
             "-es after short words and after -s, -ß, -z, -sch."),
            ("ein in the genitive: masculine / feminine / neuter", "eines · einer · eines", ""),
            ("Question word for the genitive", "wessen? (whose?)", ""),
            ("Say in German: my father's car", "das Auto meines Vaters", ""),
        ],
    },
    {
        "id": "adjw", "planet": "Adjektiva I", "title": "Adjectives after der", "hue": 45, "ring": False,
        "blurb": "Only two endings exist here: -e and -en.",
        "lesson": [
            ("p", "Now the adjectives. When an adjective stands **in front of a noun**, it needs an ending. Which one "
                  "depends on what stands before it. This planet covers the easiest situation: a **der-word** comes first "
                  "(*der, dieser, jeder, welcher, alle*)."),
            ("rule", "The der-word already shows the case signal, so the adjective can relax. It takes only **-e** or **-en**."),
            ("table", "adjw", None, None),
            ("h", "How to remember it"),
            ("p", "**-e** in exactly five slots: the three nominative singulars, plus accusative feminine and neuter. "
                  "Those are the slots where the article still looks like its dictionary form (*der, die, das, die, das*). "
                  "**Everything else is -en**: all datives, all genitives, all plurals, and accusative masculine."),
            ("ex", [("der neu**e** Film", "the new film (nominative)"), ("Ich sehe den neu**en** Film.", "I see the new film. (accusative masculine)"),
                    ("die neu**e** Lampe", "the new lamp (nominative and accusative)"), ("mit der neu**en** Lampe", "with the new lamp (dative)"),
                    ("die neu**en** Filme", "the new films (plural: always -en)")]),
            ("tip", "A quick test: if the article has changed from its dictionary form, or it's plural, the answer is -en."),
            ("p", "A few adjectives change their spelling when they take an ending: *teuer* → *teur-* (der teure Wein), "
                  "*dunkel* → *dunkl-* (das dunkle Zimmer), *hoch* → *hoh-* (der hohe Berg)."),
        ],
        "tables": [("adjw", None, None)],
        "pool": lambda: [G("plain", decl.KEYS["adjw"], 5), G("combo", decl.KEYS["adjw"], 3), G("sent", decl.KEYS["adjw"], 3)],
        "reading": ("Der alte Mann",
                    "Der alt{e||adjw:nom:m} Mann wohnt in dem klein{en||adjw:dat:n} Haus an der Ecke. Jeden Morgen trinkt er den "
                    "schwarz{en||adjw:akk:m} Kaffee und liest die neu{e||adjw:akk:f} Zeitung. Das klein{e||adjw:nom:n} Mädchen "
                    "von nebenan besucht ihn oft. Sie mag die alt{en||adjw:akk:pl} Bücher und das groß{e||adjw:akk:n} Sofa. Mit "
                    "der freundlich{en||adjw:dat:f} Nachbarin spricht er über die Blumen. Die rot{en||adjw:nom:pl} Rosen sind "
                    "die Lieblingsblumen des alt{en||adjw:gen:m} Mannes. Am Abend sitzt er mit dem müd{en||adjw:dat:m} Hund vor "
                    "dem Haus und denkt an die schön{en||adjw:akk:pl} Tage."),
        "cards": [
            ("Adjective after a der-word: which five slots take -e?", "Nominative masculine, feminine, neuter; accusative feminine and neuter.",
             "Everything else takes -en."),
            ("der neu_ Film / den neu_ Film", "der neue Film / den neuen Film", ""),
            ("Which words count as der-words?", "der, dieser, jeder, welcher, mancher, jener, alle", ""),
            ("mit der nett_ Frau", "mit der netten Frau", "Dative is always -en."),
            ("die alt_ Bücher (plural)", "die alten Bücher", "After a der-word the plural is always -en."),
            ("das klein_ Kind / mit dem klein_ Kind", "das kleine Kind / mit dem kleinen Kind", ""),
        ],
    },
    {
        "id": "adjm", "planet": "Adjektiva II", "title": "Adjectives after ein", "hue": 95, "ring": True,
        "blurb": "Where ein is silent, the adjective speaks: -er and -es.",
        "lesson": [
            ("p", "After an **ein-word** (*ein, kein, mein, dein...*) the adjective endings are almost the same as on the "
                  "last planet. The difference comes from those three slots where ein-words have **no ending**."),
            ("rule", "Somebody has to show the gender. If the ein-word doesn't, **the adjective does**: ein neu**er** Film "
                     "(like de**r**), ein neu**es** Auto (like da**s**)."),
            ("table", "adjm", None, None),
            ("ex", [("der neu**e** Film → ein neu**er** Film", "nominative masculine"),
                    ("das neu**e** Auto → ein neu**es** Auto", "nominative and accusative neuter"),
                    ("die neu**e** Lampe → eine neu**e** Lampe", "feminine: no change"),
                    ("den neu**en** Film → einen neu**en** Film", "accusative masculine: no change")]),
            ("p", "So there are only **three special slots** to remember, and they are exactly the three where *ein* is "
                  "bare. Everywhere else you already know the answer: -e for feminine nominative and accusative, **-en** "
                  "for all the rest."),
            ("tip", "Plural after *keine, meine, deine...* is always **-en**: *meine alt**en** Freunde, keine gut**en** Ideen*."),
        ],
        "tables": [("adjm", None, None)],
        "pool": lambda: [G("plain", decl.KEYS["adjm"], 5), G("combo", decl.KEYS["adjm"], 3), G("sent", decl.KEYS["adjm"], 3)],
        "reading": ("Mein neuer Job",
                    "Ich habe einen neu{en||adjm:akk:m} Job in einer klein{en||adjm:dat:f} Firma. Mein neu{er||adjm:nom:m} Chef "
                    "ist nett, und ich habe ein schön{es||adjm:akk:n} Büro mit einem groß{en||adjm:dat:n} Fenster. Eine "
                    "nett{e||adjm:nom:f} Kollegin zeigt mir alles. Sie hat keine leicht{e||adjm:akk:f} Arbeit, aber sie hilft "
                    "mir trotzdem. In der Pause essen wir in einem gut{en||adjm:dat:n} Restaurant. Dort gibt es kein "
                    "teur{es||adjm:akk:n} Essen. Meine alt{en||adjm:nom:pl} Freunde fragen: „Ist das dein erst{er||adjm:nom:m} "
                    "Job?“ – „Nein, aber es ist mein best{er||adjm:nom:m} Job.“ Nach einem lang{en||adjm:dat:m} Tag fahre ich "
                    "mit meinem alt{en||adjm:dat:n} Fahrrad nach Hause."),
        "cards": [
            ("Adjective after an ein-word: the three special slots", "ein neuer (nom. masc.) · ein neues (nom. and acc. neuter)",
             "Feminine nom./acc. takes -e; everything else takes -en."),
            ("ein gut_ Film / einen gut_ Film", "ein guter Film / einen guten Film", ""),
            ("ein klein_ Kind", "ein kleines Kind", ""),
            ("meine alt_ Freunde", "meine alten Freunde", "Plural after an ein-word is always -en."),
            ("Why 'ein guter Mann' but 'der gute Mann'?", "Something must show the gender. ein has no ending, so the adjective carries the -er.", ""),
            ("mit einem alt_ Freund / mit einer alt_ Freundin", "mit einem alten Freund / mit einer alten Freundin", ""),
        ],
    },
    {
        "id": "adjs", "planet": "Adjektiva III", "title": "Adjectives alone", "hue": 0, "ring": False,
        "blurb": "No article at all, so the adjective does all the work.",
        "lesson": [
            ("p", "Sometimes there is **no article** at all: *kalter Kaffee, frische Milch, gute Freunde*. This happens "
                  "with food and materials, with plurals, and after numbers."),
            ("rule", "With no article, the adjective **takes the signal ending itself**, the same ending *dieser* would "
                     "have: dies**er** Kaffee → kalt**er** Kaffee."),
            ("table", "adjs", None, None),
            ("ex", [("kalt**er** Kaffee", "cold coffee (like dieser)"), ("frisch**e** Milch", "fresh milk (like diese)"),
                    ("kalt**es** Wasser", "cold water (like dieses)"), ("mit frisch**er** Milch", "with fresh milk (like mit dieser)"),
                    ("mit kalt**em** Wasser", "with cold water (like mit diesem)"), ("gut**e** Freunde", "good friends (like diese)")]),
            ("tip", "One exception: genitive masculine and neuter take **-en**, not -es, because the noun already shows "
                    "the -s: *trotz schlecht**en** Wetter**s***."),
            ("h", "The whole system in one sentence"),
            ("p", "The signal ending must appear **once** in the noun phrase. If an article shows it, the adjective takes "
                  "-e or -en. If nothing shows it, the adjective shows it. That is all three adjective planets."),
        ],
        "tables": [("adjs", None, None)],
        "pool": lambda: [G("plain", decl.KEYS["adjs"], 5), G("combo", decl.KEYS["adjs"], 3), G("sent", decl.KEYS["adjs"], 3)],
        "reading": ("Frühstück im Garten",
                    "Zum Frühstück gibt es frisch{es||adjs:akk:n} Brot mit gut{er||adjs:dat:f} Butter und heiß{en||adjs:akk:m} "
                    "Kaffee. Kalt{e||adjs:nom:f} Milch steht auf dem Tisch. Ich mag deutsch{es||adjs:akk:n} Bier nicht, aber ich "
                    "trinke gern grün{en||adjs:akk:m} Tee. Im Garten wachsen rot{e||adjs:nom:pl} Tomaten und "
                    "klein{e||adjs:nom:pl} Gurken. Wir essen Salat mit frisch{en||adjs:dat:pl} Tomaten. Am Abend kochen wir Suppe "
                    "mit frisch{em||adjs:dat:n} Gemüse. Gut{er||adjs:nom:m} Wein ist teuer, aber bei schön{em||adjs:dat:n} Wetter "
                    "trinken wir ein Glas im Garten. Lieb{e||adjs:nom:pl} Freunde sind immer willkommen."),
        "cards": [
            ("Adjective with no article: what is the rule?", "It takes the ending dieser would have: kalter, kalte, kaltes.",
             "Exception: genitive masculine and neuter take -en."),
            ("kalt_ Kaffee (nominative) / kalt_ Kaffee (accusative)", "kalter Kaffee / kalten Kaffee", ""),
            ("mit frisch_ Milch", "mit frischer Milch", ""),
            ("mit kalt_ Wasser", "mit kaltem Wasser", ""),
            ("gut_ Freunde (nominative) / mit gut_ Freunden", "gute Freunde / mit guten Freunden", ""),
        ],
    },
    {
        "id": "pron", "planet": "Pronomen-Ring", "title": "Pronouns & weak nouns", "hue": 290, "ring": True,
        "blurb": "Relative and reflexive pronouns, and nouns that take -n.",
        "lesson": [
            ("h", "Relative pronouns"),
            ("p", "A relative pronoun starts a clause that describes a noun: *the man **who** lives here*. In German it "
                  "looks like the article *der, die, das*, with three exceptions."),
            ("table", "rel", None, None),
            ("rule", "**Gender and number** come from the noun it refers to. **Case** comes from its job inside the "
                     "relative clause."),
            ("ex", [("Der Mann, **der** dort steht, ist mein Lehrer.", "subject of the clause → nominative"),
                    ("Der Mann, **den** ich sehe, ist mein Lehrer.", "object of sehen → accusative"),
                    ("Der Mann, **dem** ich helfe, ist mein Lehrer.", "helfen takes the dative"),
                    ("Der Mann, **dessen** Auto dort steht, ist mein Lehrer.", "whose → genitive")]),
            ("tip", "The exceptions are the long forms: genitive **dessen** and **deren**, and dative plural **denen**."),
            ("h", "Reflexive pronouns"),
            ("p", "Reflexive verbs point back at the subject: *Ich wasche **mich***. The pronouns are the normal "
                  "accusative and dative ones, except that every third person and formal *Sie* use **sich**."),
            ("table", "refl", None, None),
            ("rule", "Use the **dative** (*mir, dir*) when the sentence has another direct object: *Ich wasche **mich***, "
                     "but *Ich wasche **mir** die Hände*."),
            ("h", "Weak nouns"),
            ("p", "A small group of masculine nouns, mostly people, add **-n or -en in every case except the "
                  "nominative singular**: *der Student, der Kollege, der Junge, der Kunde, der Nachbar, der Mensch, der "
                  "Herr, der Polizist*."),
            ("ex", [("Das ist der Student.", "nominative: no ending"), ("Ich sehe den Student**en**.", "accusative"),
                    ("Ich helfe dem Student**en**.", "dative"), ("das Buch des Student**en**", "genitive (no -s!)")]),
        ],
        "tables": [("rel", None, None), ("refl", None, None)],
        "pool": lambda: [G("plain", decl.KEYS["rel"], 4), G("plain", decl.KEYS["refl"], 3),
                         G("plain", ["noun:akk:weak", "noun:dat:weak", "noun:gen:weak"], 2)],
        "reading": ("Unser Nachbar",
                    "Das ist Herr Braun, {der|who|rel:nom:m} neben uns wohnt. Ich kenne den Student{en||noun:akk:weak}, "
                    "{dem|whom|rel:dat:m} er oft hilft. Die Frau, {die|whom|rel:akk:f} du gestern gesehen hast, ist seine "
                    "Kollegin. Jeden Morgen wäscht er {sich|himself|refl:akk:3} und putzt {sich|himself|refl:dat:3} die Zähne. "
                    "Ich freue {mich|myself|refl:akk:ich} auf das Wochenende, denn ich kaufe {mir|myself|refl:dat:ich} ein neues "
                    "Fahrrad. Die Kinder, mit {denen|whom|rel:dat:pl} wir spielen, wohnen im Haus des Nachbar{n||noun:gen:weak}. "
                    "Das Mädchen, {dessen|whose|rel:gen:n} Hund so laut ist, heißt Mia. Setzt {euch|yourselves|refl:akk:ihr} "
                    "bitte! Wir geben dem Kolleg{en||noun:dat:weak} das Buch, {das|which|rel:akk:n} er sucht."),
        "cards": [
            ("Where do relative pronouns differ from der, die, das?", "Genitive: dessen, deren. Dative plural: denen.", ""),
            ("Relative pronoun: where do its gender and its case come from?",
             "Gender and number from the noun it refers to; case from its job in the relative clause.", "Der Mann, dem ich helfe, ..."),
            ("Reflexive pronouns, accusative: ich, du, er/sie/es, wir, ihr, sie/Sie", "mich · dich · sich · uns · euch · sich", ""),
            ("When is the reflexive pronoun dative (mir, dir)?", "When the sentence has another direct object.", "Ich wasche mir die Hände."),
            ("What is a weak noun?", "A masculine noun that adds -(e)n in every case but the nominative singular.",
             "der Student, Kollege, Junge, Kunde, Nachbar, Mensch, Herr"),
            ("der Herr → Akkusativ / Dativ / Genitiv singular, and the plural", "den Herrn · dem Herrn · des Herrn · die Herren", ""),
        ],
    },
    {
        "id": "home", "planet": "Heimat", "title": "Everything together", "hue": 130, "ring": False, "home": True,
        "blurb": "The final approach. Every case, every ending, in full sentences.",
        "lesson": [
            ("p", "You have visited every planet. This last stop mixes everything, the way real German does. For every "
                  "noun phrase, run the same three questions:"),
            ("rule", "**1. Which case?** Look at the verb and the preposition. **2. Which gender or number?** That comes "
                     "from the noun. **3. Who shows the signal?** The article if it can; otherwise the adjective."),
            ("h", "The whole system on one page"),
            ("table", "dies", None, None),
            ("p", "These sixteen signal endings are the core. *der, die, das* is the same table with different vowels. "
                  "ein-words use it too, minus three endings. Adjectives with no article copy it."),
            ("table", "adjw", None, None),
            ("p", "And when an article already shows the signal, the adjective takes -e in five slots and -en everywhere "
                  "else. After an ein-word with no ending, the adjective takes the missing -er or -es."),
            ("ex", [("Ich gebe **dem** alt**en** Mann **einen** heiß**en** Kaffee.", "dative receiver, accusative thing"),
                    ("Wegen **des** schlecht**en** Wetters bleibt **mein** klein**er** Bruder zu Hause.", "genitive after wegen; bare mein, so -er"),
                    ("Wir sitzen mit gut**en** Freunden in **einem** schön**en** Garten.", "dative plural; dative after in (wo?)")]),
            ("tip", "From here it is all about speed. Keep coming back for the daily mix until the endings come out "
                    "without thinking."),
        ],
        "tables": [],
        "pool": lambda: [G("sent", decl.KEYS["adjw"] + decl.KEYS["adjm"] + decl.KEYS["adjs"], 6),
                         G("combo", decl.KEYS["adjw"] + decl.KEYS["adjm"] + decl.KEYS["adjs"], 2),
                         G("dsent", decl.KEYS["def"] + decl.KEYS["ein"] + decl.KEYS["poss"], 2),
                         G("plain", decl.KEYS["pers"], 1), G("plain", decl.KEYS["rel"], 1), G("plain", decl.KEYS["refl"], .5),
                         G("plain", decl.KEYS["trig"], 1)],
        "reading": ("Eine lange Reise",
                    "Letzten Sommer habe ich mit mein{er||poss:dat:f} best{en||adjm:dat:f} Freundin ein{e||ein:akk:f} "
                    "lang{e||adjm:akk:f} Reise gemacht. Wir sind mit d{em||def:dat:m} alt{en||adjw:dat:m} Zug durch "
                    "d{ie||def:akk:f} ganz{e||adjw:akk:f} Schweiz gefahren. In ein{em||ein:dat:n} klein{en||adjm:dat:n} Dorf haben "
                    "wir ein{en||ein:akk:m} nett{en||adjm:akk:m} Mann getroffen, d{er||rel:nom:m} uns sein{en||poss:akk:m} "
                    "schön{en||adjm:akk:m} Garten gezeigt hat. Trotz d{es||def:gen:n} schlecht{en||adjw:gen:n} Wetters sind wir "
                    "auf ein{en||ein:akk:m} hoh{en||adjm:akk:m} Berg gestiegen. Oben gab es heiß{e||adjs:akk:f} Suppe und "
                    "frisch{es||adjs:akk:n} Brot. Das war d{er||def:nom:m} schönst{e||adjw:nom:m} Tag d{er||def:gen:f} "
                    "ganz{en||adjw:gen:f} Reise."),
        "cards": [
            ("The sixteen signal endings (dieser): Nominativ / Akkusativ / Dativ / Genitiv",
             "Nom: -er -e -es -e · Akk: -en -e -es -e · Dat: -em -er -em -en · Gen: -es -er -es -er", "Order: masculine, feminine, neuter, plural."),
            ("The three questions for every noun phrase", "1. Which case? 2. Which gender or number? 3. Who shows the signal: article or adjective?", ""),
            ("Adjective endings in one sentence",
             "If an article shows the signal, the adjective takes -e or -en. If nothing shows it, the adjective does.", ""),
        ],
    },
]
STAGE = {s["id"]: s for s in STAGES}
ORDER = [s["id"] for s in STAGES]
for _s in STAGES:
    _s["pool"] = _s["pool"]()

STEP_INFO = {
    "learn": ("Briefing", "Read how it works, with charts and examples."),
    "chart": ("Charts", "Fill in the tables from memory."),
    "drill": ("Drill", "20 quick questions. Get 16 right to pass."),
    "reading": ("Reading", "Fill in the endings in a short text."),
    "cards": ("Flashcards", "Flip through the key rules."),
    "checkpoint": ("Checkpoint", "Pass this to unlock the next planet."),
}
DRILL_LEN, DRILL_PASS = 20, 16
READING_PASS = .8


def steps_of(stage):
    return ["learn"] + (["chart"] if stage["tables"] else []) + ["drill", "reading", "cards", "checkpoint"]


def checkpoint_size(stage):
    return (25, 21) if stage.get("home") else (15, 13)


def stage_keys(stage):
    """The skills this stage teaches (its own, not the review mixed into checkpoints). Noun genders are drilled
    on the first planet but not counted here: there are over a hundred and they'd swamp the planet's progress."""
    core = decl._core_keys()
    return sorted({k for g in stage["pool"] for k in g["keys"] if k in core and not k.startswith("gender:")})


# ---------- questions ----------
SENTENCE_MODES = ("dsent", "wsent", "sent", "combo")


def _build(mode, key):
    if mode == "dsent":
        return decl.gen_det_sentence(key)
    if mode == "wsent":
        return decl.gen_det_sentence(key, trig_prefix="trig:w:")
    if mode in ("sent", "combo"):
        return decl.GENERATORS[mode](key)
    return decl.GENERATORS[key.split(":")[0]](key)


def question(stage_id, mode="drill", recent=()):
    """One question for a stage. Checkpoints lean on full sentences and mix in review of earlier stages."""
    stage = STAGE[stage_id]
    idx = ORDER.index(stage_id)
    checkpoint = mode == "checkpoint"
    if checkpoint and idx and random.random() < .2:
        stage = STAGES[random.randrange(idx)]
    groups = stage["pool"]
    weights = [g["w"] * (2 if checkpoint and g["mode"] in SENTENCE_MODES else 1) for g in groups]
    group = random.choices(groups, weights)[0]
    st, now, recent = decl._state(), db.now(), set(recent or ())
    key = random.choices(group["keys"], [decl._weight(k, st, recent, now) for k in group["keys"]])[0]
    return _build(group["mode"], key)


# ---------- readings ----------
_GAP = re.compile(r"\{([^{}|]+)\|([^{}|]*)(?:\|([^{}|]*))?\}")


def parse_reading(text):
    """'Ich sehe {den|the|def:akk:m} Mann' -> text and gap segments."""
    out, pos = [], 0
    for m in _GAP.finditer(text):
        if m.start() > pos:
            out.append({"t": text[pos:m.start()]})
        out.append({"a": m.group(1).strip(), "hint": m.group(2).strip(), "key": (m.group(3) or "").strip() or None})
        pos = m.end()
    if pos < len(text):
        out.append({"t": text[pos:]})
    return out


def reading_brief(stage_id):
    """What a freshly written reading for this stage should practice (for the AI writer)."""
    stage = STAGE[stage_id]
    return {"focus": f"{stage['title']}: {stage['blurb']}", "example": stage["reading"][1]}


# ---------- progress ----------
def _done():
    out = {}
    for r in db.q("SELECT * FROM decl_progress"):
        out.setdefault(r["stage"], {})[r["step"]] = r
    return out


def journey():
    done, st = _done(), decl._state()
    stages, unlocked, current = [], True, None
    for s in STAGES:
        mine = done.get(s["id"], {})
        steps = steps_of(s)
        complete = "checkpoint" in mine
        keys = stage_keys(s)
        solid = sum(1 for k in keys if st.get(k, {}).get("box", 0) >= 3)
        all_steps = all(x in mine for x in steps)
        stars = (1 if complete else 0) + (1 if complete and all_steps else 0) + (1 if complete and all_steps and solid >= .8 * len(keys) else 0)
        if unlocked and not complete and current is None:
            current = s["id"]
        size, need = checkpoint_size(s)
        stages.append({
            "id": s["id"], "planet": s["planet"], "title": s["title"], "blurb": s["blurb"], "hue": s["hue"],
            "ring": s.get("ring", False), "nebula": s.get("nebula", False), "home": s.get("home", False),
            "unlocked": unlocked, "complete": complete, "stars": stars,
            "skills": {"total": len(keys), "solid": solid, "seen": sum(1 for k in keys if k in st)},
            "steps": [{"id": x, "label": STEP_INFO[x][0], "text": STEP_INFO[x][1], "done": x in mine,
                       "best": mine.get(x, {}).get("best"), "skipped": bool(mine.get(x, {}).get("skipped"))} for x in steps],
            "checkpoint": {"size": size, "need": need}, "cards": len(s["cards"]),
        })
        unlocked = unlocked and complete
    return {"stages": stages, "current": current or ORDER[-1], "finished": current is None,
            "stars": sum(s["stars"] for s in stages), "max_stars": 3 * len(stages),
            "drill": {"size": DRILL_LEN, "need": DRILL_PASS}}


def detail(stage_id):
    s = STAGE[stage_id]
    return {"id": s["id"], "lesson": [list(b) for b in s["lesson"]],
            "tables": [{"id": t, "rows": rows, "cols": cols} for t, rows, cols in s["tables"]],
            "reading": {"title": s["reading"][0], "segments": parse_reading(s["reading"][1])},
            "cards": [{"front": f, "back": b, "extra": e} for f, b, e in s["cards"]],
            "cards_added": db.q1("SELECT COUNT(*) AS n FROM cards WHERE tags LIKE ?", (f'%"decl:{s["id"]}"%',))["n"]}


def _unlocked(stage_id):
    return next(s["unlocked"] for s in journey()["stages"] if s["id"] == stage_id)


def complete(stage_id, step, score=None, total=None):
    """Mark a step done if it was passed. Returns whether it counted, and the updated journey."""
    stage = STAGE[stage_id]
    if step not in steps_of(stage):
        raise db.UserError("Unknown step")
    if not _unlocked(stage_id):
        raise db.UserError("This planet is still locked.")
    passed = True
    if step == "drill":
        passed = (score or 0) >= DRILL_PASS and (total or 0) >= DRILL_LEN
    elif step == "checkpoint":
        size, need = checkpoint_size(stage)
        passed = (score or 0) >= need and (total or 0) >= size
    elif step == "reading":
        passed = bool(total) and score / total >= READING_PASS
    was_complete = bool(db.q1("SELECT 1 AS x FROM decl_progress WHERE stage=? AND step='checkpoint'", (stage_id,)))
    if passed:
        db.ex("INSERT INTO decl_progress(stage, step, done_at, best) VALUES(?,?,?,?) ON CONFLICT(stage, step) DO UPDATE SET "
              "best = MAX(COALESCE(best, 0), COALESCE(excluded.best, 0))", (stage_id, step, db.now(), score))
    idx = ORDER.index(stage_id)
    newly = passed and step == "checkpoint" and not was_complete
    return {"passed": passed, "planet_complete": newly,
            "next": ORDER[idx + 1] if newly and idx + 1 < len(ORDER) else None, "journey": journey()}


def add_cards(stage_id):
    """Put the stage's rule cards into the learner's spaced-repetition deck (once)."""
    s = STAGE[stage_id]
    tag = f'["declension", "decl:{s["id"]}"]'
    have = {r["front"] for r in db.q("SELECT front FROM cards WHERE tags LIKE ?", (f'%"decl:{s["id"]}"%',))}
    t = i18n.tr if i18n.lang() == "tr" else (lambda x: x)  # cards go into the deck in the app's language
    rows = [(None, None, "rule", t(f), t(b), t(e), tag, db.now()) for f, b, e in s["cards"]
            if f not in have and i18n.tr(f) not in have]  # a card added in either language counts
    if rows:
        db.exmany("INSERT INTO cards(book_id, chapter_id, type, front, back, extra, tags, created_at) VALUES(?,?,?,?,?,?,?,?)", rows)
    return {"added": len(rows), "already": len(have)}


def record(items, family="sent"):
    """Results from a reading or the case-matching game: [{key, correct}]. Updates the skills that have a key and
    logs every answer under the given family (it decides the topic shown in progress)."""
    core = decl._core_keys()
    for it in items:
        right = bool(it.get("correct"))
        if it.get("key") in core:
            decl.update_skill(it["key"], right, False)
        decl._log_answer(family, right)
    return {"ok": True}


def brief():
    """The journey in a few numbers, for the Today page."""
    j = journey()
    cur = next(s for s in j["stages"] if s["id"] == j["current"])
    todo = [x for x in cur["steps"] if not x["done"]]
    return {"finished": j["finished"], "title": cur["title"], "planet": cur["planet"], "blurb": cur["blurb"],
            "steps_done": len(cur["steps"]) - len(todo), "steps_total": len(cur["steps"]),
            "next_step": todo[0]["label"] if todo else None,
            "planets_done": sum(1 for s in j["stages"] if s["complete"]), "planets_total": len(j["stages"]),
            "stars": j["stars"], "max_stars": j["max_stars"]}


def coach_summary():
    j = journey()
    cur = next(s for s in j["stages"] if s["id"] == j["current"])
    return {
        "what": "A guided course on the Declensions page: planets unlocked in order (Nominativ, Akkusativ, Dativ, two-way "
                "prepositions, ein-words, Genitiv, three adjective stages, pronouns, final mix). Each has a briefing, charts, "
                "a drill, a reading, flashcards and a checkpoint.",
        "planets_complete": sum(1 for s in j["stages"] if s["complete"]), "planets_total": len(j["stages"]),
        "finished": j["finished"],
        "current_planet": f"{cur['title']} ({cur['planet']})",
        "steps_left_on_current": [x["label"] for x in cur["steps"] if not x["done"]],
    }
