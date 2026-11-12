"""Declension trainer: a rule-based grammar engine, so drills are instant, unlimited, always correct and free.

Every form the learner must produce is a "skill" with a key such as adjm:dat:f (adjective after an ein-word,
dative feminine). Each skill sits in a box from 0 to 5 that rises with fast right answers spread over days.
Questions are picked from the skills that are weakest or due; mixed questions train several skills at once.
"""
import datetime as dt
import random
import re

from . import db

CASES = ("nom", "akk", "dat", "gen")
CASE_NAME = {"nom": "Nominativ", "akk": "Akkusativ", "dat": "Dativ", "gen": "Genitiv"}
CASE_EN = {"nom": "nominative", "akk": "accusative", "dat": "dative", "gen": "genitive"}
GENDERS = ("m", "f", "n", "pl")
GENDER_EN = {"m": "masculine", "f": "feminine", "n": "neuter", "pl": "plural"}

ARTICLE = {
    "nom": {"m": "der", "f": "die", "n": "das", "pl": "die"},
    "akk": {"m": "den", "f": "die", "n": "das", "pl": "die"},
    "dat": {"m": "dem", "f": "der", "n": "dem", "pl": "den"},
    "gen": {"m": "des", "f": "der", "n": "des", "pl": "der"},
}
DIES_END = {
    "nom": {"m": "er", "f": "e", "n": "es", "pl": "e"},
    "akk": {"m": "en", "f": "e", "n": "es", "pl": "e"},
    "dat": {"m": "em", "f": "er", "n": "em", "pl": "en"},
    "gen": {"m": "es", "f": "er", "n": "es", "pl": "er"},
}
EIN_END = {
    "nom": {"m": "", "f": "e", "n": "", "pl": "e"},
    "akk": {"m": "en", "f": "e", "n": "", "pl": "e"},
    "dat": {"m": "em", "f": "er", "n": "em", "pl": "en"},
    "gen": {"m": "es", "f": "er", "n": "es", "pl": "er"},
}
ADJ_END = {
    "w": {  # weak: after der, dieser, jeder...
        "nom": {"m": "e", "f": "e", "n": "e", "pl": "en"},
        "akk": {"m": "en", "f": "e", "n": "e", "pl": "en"},
        "dat": {"m": "en", "f": "en", "n": "en", "pl": "en"},
        "gen": {"m": "en", "f": "en", "n": "en", "pl": "en"},
    },
    "m": {  # mixed: after ein, kein, mein...
        "nom": {"m": "er", "f": "e", "n": "es", "pl": "en"},
        "akk": {"m": "en", "f": "e", "n": "es", "pl": "en"},
        "dat": {"m": "en", "f": "en", "n": "en", "pl": "en"},
        "gen": {"m": "en", "f": "en", "n": "en", "pl": "en"},
    },
    "s": {  # strong: no article
        "nom": {"m": "er", "f": "e", "n": "es", "pl": "e"},
        "akk": {"m": "en", "f": "e", "n": "es", "pl": "e"},
        "dat": {"m": "em", "f": "er", "n": "em", "pl": "en"},
        "gen": {"m": "en", "f": "er", "n": "en", "pl": "er"},
    },
}
ADJ_CLASS_NAME = {"w": "after a der-word", "m": "after an ein-word", "s": "with no article"}

# Person: (label for the learner, nominative, accusative, dative)
PERSONS = {
    "ich": ("ich (I)", "ich", "mich", "mir"),
    "du": ("du (you)", "du", "dich", "dir"),
    "er": ("er (he)", "er", "ihn", "ihm"),
    "sie": ("sie (she)", "sie", "sie", "ihr"),
    "es": ("es (it)", "es", "es", "ihm"),
    "wir": ("wir (we)", "wir", "uns", "uns"),
    "ihr": ("ihr (you all)", "ihr", "euch", "euch"),
    "pl": ("sie (they)", "sie", "sie", "ihnen"),
    "Sie": ("Sie (you, formal)", "Sie", "Sie", "Ihnen"),
}
OWNERS = [
    ("ich", "my", "mein"), ("du", "your", "dein"), ("er", "his", "sein"), ("sie", "her", "ihr"), ("es", "its", "sein"),
    ("wir", "our", "unser"), ("ihr", "your, plural", "euer"), ("sie", "their", "ihr"), ("Sie", "your, formal", "Ihr"),
]
REFL = {"ich": ("mich", "mir"), "du": ("dich", "dir"), "3": ("sich", "sich"), "wir": ("uns", "uns"), "ihr": ("euch", "euch")}
RELATIVE = {
    "nom": {"m": "der", "f": "die", "n": "das", "pl": "die"},
    "akk": {"m": "den", "f": "die", "n": "das", "pl": "die"},
    "dat": {"m": "dem", "f": "der", "n": "dem", "pl": "denen"},
    "gen": {"m": "dessen", "f": "deren", "n": "dessen", "pl": "deren"},
}
WER = {"nom": "wer", "akk": "wen", "dat": "wem", "gen": "wessen"}

# ---------- vocabulary ----------
# gender | word | genitive singular (for weak nouns: the form in every case but the nominative) | plural | tags
_NOUNS = """
m|Mann|Mannes|Männer|person
m|Vater|Vaters|Väter|person
m|Bruder|Bruders|Brüder|person
m|Sohn|Sohnes|Söhne|person
m|Freund|Freundes|Freunde|person
m|Lehrer|Lehrers|Lehrer|person
m|Trainer|Trainers|Trainer|person
m|Arzt|Arztes|Ärzte|person
m|Student|Studenten|Studenten|person weak
m|Kollege|Kollegen|Kollegen|person weak
m|Junge|Jungen|Jungen|person weak
m|Kunde|Kunden|Kunden|person weak
m|Nachbar|Nachbarn|Nachbarn|person weak
m|Mensch|Menschen|Menschen|person weak
m|Herr|Herrn|Herren|person weak
m|Polizist|Polizisten|Polizisten|person weak
f|Frau||Frauen|person
f|Mutter||Mütter|person
f|Schwester||Schwestern|person
f|Tochter||Töchter|person
f|Freundin||Freundinnen|person
f|Lehrerin||Lehrerinnen|person
f|Trainerin||Trainerinnen|person
f|Ärztin||Ärztinnen|person
f|Kollegin||Kolleginnen|person
f|Nachbarin||Nachbarinnen|person
n|Kind|Kindes|Kinder|person
n|Mädchen|Mädchens|Mädchen|person
n|Baby|Babys|Babys|person
m|Schlüssel|Schlüssels|Schlüssel|object
m|Koffer|Koffers|Koffer|object
m|Computer|Computers|Computer|object
m|Stift|Stiftes|Stifte|object
m|Apfel|Apfels|Äpfel|object
m|Brief|Briefes|Briefe|object
m|Rucksack|Rucksacks|Rucksäcke|object
m|Ball|Balles|Bälle|object
f|Tasche||Taschen|object
f|Flasche||Flaschen|object
f|Lampe||Lampen|object
f|Uhr||Uhren|object
f|Zeitung||Zeitungen|object
f|Karte||Karten|object
f|Jacke||Jacken|object
n|Buch|Buches|Bücher|object
n|Auto|Autos|Autos|object
n|Handy|Handys|Handys|object
n|Geschenk|Geschenkes|Geschenke|object
n|Heft|Heftes|Hefte|object
n|Fahrrad|Fahrrads|Fahrräder|object
n|Foto|Fotos|Fotos|object
n|Glas|Glases|Gläser|object
n|Messer|Messers|Messer|object
n|Bild|Bildes|Bilder|object
m|Tisch|Tisches|Tische|furniture
m|Stuhl|Stuhls|Stühle|furniture
m|Schrank|Schranks|Schränke|furniture wall
f|Matte||Matten|furniture
f|Kiste||Kisten|furniture
n|Bett|Bettes|Betten|furniture
n|Sofa|Sofas|Sofas|furniture
n|Regal|Regals|Regale|furniture tall
f|Wand||Wände|wall
f|Tür||Türen|wall
f|Tafel||Tafeln|wall
n|Fenster|Fensters|Fenster|wall
m|Park|Parks|Parks|place
m|Garten|Gartens|Gärten|place
m|Supermarkt|Supermarkts|Supermärkte|place
m|Bahnhof|Bahnhofs|Bahnhöfe|place
m|Kraftraum|Kraftraums|Krafträume|place
m|Laden|Ladens|Läden|place
f|Schule||Schulen|place
f|Stadt||Städte|place
f|Wohnung||Wohnungen|place
f|Bank||Banken|place
f|Küche||Küchen|place
f|Halle||Hallen|place
f|Apotheke||Apotheken|place
n|Büro|Büros|Büros|place
n|Kino|Kinos|Kinos|place
n|Restaurant|Restaurants|Restaurants|place
n|Hotel|Hotels|Hotels|place
n|Haus|Hauses|Häuser|place tall
n|Zimmer|Zimmers|Zimmer|place
n|Fitnessstudio|Fitnessstudios|Fitnessstudios|place
n|Café|Cafés|Cafés|place
m|Film|Films|Filme|event
m|Kurs|Kurses|Kurse|event
m|Termin|Termins|Termine|event
m|Urlaub|Urlaubs|Urlaube|event
f|Prüfung||Prüfungen|event
f|Reise||Reisen|event
f|Übung||Übungen|event
f|Stunde||Stunden|event
f|Pause||Pausen|event
n|Training|Trainings|Trainings|event
n|Konzert|Konzertes|Konzerte|event
n|Spiel|Spieles|Spiele|event
n|Essen|Essens|Essen|event
m|Turm|Turmes|Türme|tall
m|Berg|Berges|Berge|tall
m|Kaffee|Kaffees||mass
m|Tee|Tees||mass
m|Wein|Weines||mass
m|Saft|Saftes||mass
m|Käse|Käses||mass
f|Milch|||mass
f|Butter|||mass
f|Suppe|||mass
f|Schokolade|||mass
n|Wasser|Wassers||mass
n|Bier|Bieres||mass
n|Brot|Brotes||mass
n|Fleisch|Fleisches||mass
n|Gemüse|Gemüses||mass
"""
NOUNS = []
for _line in _NOUNS.strip().splitlines():
    _g, _w, _gen, _pl, _tags = _line.split("|")
    _t = _tags.split()
    NOUNS.append({"g": _g, "word": _w, "gen": _gen or _w, "pl": _pl, "tags": _t, "weak": "weak" in _t, "tag": _t[0]})
NOUN_BY_WORD = {n["word"]: n for n in NOUNS}

ADJ_STEM = {"teuer": "teur", "dunkel": "dunkl", "hoch": "hoh", "müde": "müd"}  # spelling changes before an ending
ADJ_BY_TAG = {
    "person": "alt jung nett freundlich klug müde neu",
    "object": "neu alt teuer billig schön klein groß schwer schwarz rot",
    "furniture": "neu alt teuer billig schön klein groß schwarz weiß dunkel",
    "wall": "neu alt weiß schwarz groß klein schön dunkel",
    "place": "neu alt klein groß schön teuer modern dunkel ruhig",
    "event": "neu lang kurz gut interessant wichtig",
    "tall": "hoch alt groß schön",
    "mass": "kalt warm frisch gut teuer billig deutsch",
}
ADJ_BY_TAG = {k: v.split() for k, v in ADJ_BY_TAG.items()}

# ---------- what triggers which case ----------
# key -> (what the learner sees, case, explanation)
TRIGGERS = {}
for _case, _words in (("akk", "durch für gegen ohne um"),
                      ("dat", "aus außer bei mit nach seit von zu gegenüber"),
                      ("gen", "wegen trotz während statt innerhalb außerhalb")):
    for _w in _words.split():
        TRIGGERS[f"trig:p:{_w}"] = (f"{_w} + ?", _case, f"The preposition {_w} always takes the {CASE_EN[_case]}.")
for _case, _words in (("dat", "helfen danken gehören gefallen antworten glauben folgen gratulieren vertrauen zuhören schmecken passen"),
                      ("akk", "sehen kaufen brauchen kennen besuchen haben")):
    for _w in _words.split():
        _rule = ("is one of the verbs that take the dative, not the accusative" if _case == "dat"
                 else "takes a direct object in the accusative")
        TRIGGERS[f"trig:v:{_w}"] = (f"{_w} + ?", _case, f"{_w} {_rule}.")
TWO_WAY = {
    "in": ("Ich gehe in ___ Park.", "Ich bin in ___ Park."),
    "an": ("Ich hänge das Bild an ___ Wand.", "Das Bild hängt an ___ Wand."),
    "auf": ("Ich lege das Buch auf ___ Tisch.", "Das Buch liegt auf ___ Tisch."),
    "hinter": ("Der Hund läuft hinter ___ Haus.", "Der Hund liegt hinter ___ Haus."),
    "neben": ("Ich stelle die Flasche neben ___ Bett.", "Die Flasche steht neben ___ Bett."),
    "über": ("Ich hänge die Lampe über ___ Tisch.", "Die Lampe hängt über ___ Tisch."),
    "unter": ("Die Katze läuft unter ___ Sofa.", "Die Katze schläft unter ___ Sofa."),
    "vor": ("Ich stelle das Auto vor ___ Haus.", "Das Auto steht vor ___ Haus."),
    "zwischen": ("Ich stelle den Stuhl zwischen ___ Betten.", "Der Stuhl steht zwischen ___ Betten."),
}
for _w, (_to, _at) in TWO_WAY.items():
    TRIGGERS[f"trig:w:{_w}:wohin"] = (_to, "akk", f"{_w} is a two-way preposition. Movement to a new place (wohin?) takes the accusative.")
    TRIGGERS[f"trig:w:{_w}:wo"] = (_at, "dat", f"{_w} is a two-way preposition. A fixed location (wo?) takes the dative.")

# Sentence frames: case, noun tags, trigger key (or None), singular text, plural text (None = the same),
# preposition placed in front of the gap (or None), explanation when there is no trigger key.
_SUBJECT = "This is the subject of the sentence, so it is nominative."
_PRED = "After sein, the noun is nominative too."
_OBJECT = "This is the direct object, so it is accusative."
FRAMES = [
    ("nom", ("person",), None, "{x} wartet vor der Tür.", "{x} warten vor der Tür.", None, _SUBJECT),
    ("nom", ("person",), None, "{x} kommt heute nicht.", "{x} kommen heute nicht.", None, _SUBJECT),
    ("nom", ("person",), None, "{x} trainiert jeden Tag.", "{x} trainieren jeden Tag.", None, _SUBJECT),
    ("nom", ("object", "furniture", "place"), None, "{x} ist hier.", "{x} sind hier.", None, _SUBJECT),
    ("nom", ("person", "object"), None, "Das ist {x}.", "Das sind {x}.", None, _PRED),
    ("nom", ("mass",), None, "{x} ist gesund.", None, None, _SUBJECT),
    ("akk", ("person", "object"), "trig:v:sehen", "Ich sehe {x}.", None, None, _OBJECT),
    ("akk", ("object",), "trig:v:kaufen", "Wir kaufen {x}.", None, None, _OBJECT),
    ("akk", ("object",), "trig:v:brauchen", "Ich brauche {x}.", None, None, _OBJECT),
    ("akk", ("object",), "trig:v:haben", "Hast du {x}?", None, None, _OBJECT),
    ("akk", ("person",), "trig:v:kennen", "Kennst du {x}?", None, None, _OBJECT),
    ("akk", ("person", "place"), "trig:v:besuchen", "Morgen besuche ich {x}.", None, None, _OBJECT),
    ("akk", ("mass",), "trig:v:kaufen", "Wir kaufen {x}.", None, None, _OBJECT),
    ("akk", ("mass",), None, "Ich trinke gern {x}.", None, None, _OBJECT),
    ("akk", ("place",), "trig:p:durch", "Wir laufen {x}.", None, "durch", None),
    ("akk", ("person",), "trig:p:für", "Das Geschenk ist {x}.", None, "für", None),
    ("akk", ("person",), "trig:p:gegen", "Er spielt {x}.", None, "gegen", None),
    ("akk", ("person",), "trig:p:ohne", "Ich fahre nicht {x}.", None, "ohne", None),
    ("akk", ("place",), "trig:p:um", "Wir joggen {x}.", None, "um", None),
    ("akk", ("place",), "trig:w:in:wohin", "Ich gehe {x}.", None, "in", None),
    ("akk", ("furniture",), "trig:w:auf:wohin", "Ich lege das Buch {x}.", None, "auf", None),
    ("akk", ("wall",), "trig:w:an:wohin", "Ich hänge das Bild {x}.", None, "an", None),
    ("akk", ("furniture",), "trig:w:neben:wohin", "Ich stelle die Flasche {x}.", None, "neben", None),
    ("akk", ("furniture",), "trig:w:unter:wohin", "Die Katze läuft {x}.", None, "unter", None),
    ("akk", ("place",), "trig:w:vor:wohin", "Ich fahre das Auto {x}.", None, "vor", None),
    ("akk", ("furniture",), "trig:w:über:wohin", "Ich hänge die Lampe {x}.", None, "über", None),
    ("akk", ("place",), "trig:w:hinter:wohin", "Der Hund läuft {x}.", None, "hinter", None),
    ("dat", ("person",), "trig:v:helfen", "Ich helfe {x}.", None, None, None),
    ("dat", ("person",), "trig:v:gehören", "Das Handy gehört {x}.", None, None, None),
    ("dat", ("person",), "trig:v:gefallen", "Das Buch gefällt {x}.", None, None, None),
    ("dat", ("person",), "trig:v:danken", "Wir danken {x}.", None, None, None),
    ("dat", ("person",), "trig:v:antworten", "Ich antworte {x}.", None, None, None),
    ("dat", ("person",), "trig:v:glauben", "Ich glaube {x}.", None, None, None),
    ("dat", ("person",), "trig:v:zuhören", "Wir hören {x} zu.", None, None, None),
    ("dat", ("person",), "trig:v:gratulieren", "Wir gratulieren {x}.", None, None, None),
    ("dat", ("person",), None, "Ich gebe {x} den Schlüssel.", None, None, "With geben, the person receiving is dative and the thing given is accusative."),
    ("dat", ("person",), None, "Er zeigt {x} das Foto.", None, None, "With zeigen, the person you show it to is dative and the thing shown is accusative."),
    ("dat", ("person",), "trig:p:mit", "Ich trainiere {x}.", None, "mit", None),
    ("dat", ("person",), "trig:p:bei", "Ich wohne {x}.", None, "bei", None),
    ("dat", ("person",), "trig:p:von", "Das Geschenk ist {x}.", None, "von", None),
    ("dat", ("person", "place"), "trig:p:zu", "Ich gehe {x}.", None, "zu", None),
    ("dat", ("place",), "trig:p:aus", "Er kommt {x}.", None, "aus", None),
    ("dat", ("event",), "trig:p:nach", "Wir essen {x}.", None, "nach", None),
    ("dat", ("event",), "trig:p:seit", "Ich bin {x} müde.", None, "seit", None),
    ("dat", ("person",), "trig:p:außer", "Alle kommen {x}.", None, "außer", None),
    ("dat", ("mass",), None, "Das schmeckt mit {x} besser.", None, None, "mit always takes the dative."),
    ("dat", ("place",), "trig:w:in:wo", "Ich bin {x}.", None, "in", None),
    ("dat", ("furniture",), "trig:w:auf:wo", "Das Buch liegt {x}.", None, "auf", None),
    ("dat", ("wall",), "trig:w:an:wo", "Das Bild hängt {x}.", None, "an", None),
    ("dat", ("furniture",), "trig:w:neben:wo", "Die Flasche steht {x}.", None, "neben", None),
    ("dat", ("furniture",), "trig:w:unter:wo", "Die Katze schläft {x}.", None, "unter", None),
    ("dat", ("place",), "trig:w:vor:wo", "Das Auto steht {x}.", None, "vor", None),
    ("dat", ("furniture",), "trig:w:über:wo", "Die Lampe hängt {x}.", None, "über", None),
    ("dat", ("place",), "trig:w:hinter:wo", "Der Hund liegt {x}.", None, "hinter", None),
    ("gen", ("event",), "trig:p:wegen", "Ich bin {x} nervös.", None, "wegen", None),
    ("gen", ("event",), "trig:p:trotz", "Ich bin {x} ruhig.", None, "trotz", None),
    ("gen", ("event",), "trig:p:während", "Ich trinke {x} Wasser.", None, "während", None),
    ("gen", ("person",), "trig:p:statt", "Ich komme {x}.", None, "statt", None),
    ("gen", ("place",), "trig:p:außerhalb", "Wir treffen uns {x}.", None, "außerhalb", None),
    ("gen", ("place",), "trig:p:innerhalb", "Wir bleiben {x}.", None, "innerhalb", None),
    ("gen", ("person",), None, "Das ist das Auto {x}.", None, None, "'Of someone' is the genitive."),
    ("gen", ("person",), None, "Der Name {x} ist schön.", None, None, "'Of someone' is the genitive."),
]
CONTRACT = {("in", "dem"): "im", ("in", "das"): "ins", ("an", "dem"): "am", ("an", "das"): "ans",
            ("bei", "dem"): "beim", ("von", "dem"): "vom", ("zu", "dem"): "zum", ("zu", "der"): "zur"}
CONTRACTING = {"in", "an", "bei", "von", "zu"}

PERS_FRAMES = {
    "akk": ["Anna sieht ___.", "Das Geschenk ist für ___.", "Max wartet auf ___.", "Anna kennt ___.",
            "Alle lieben ___.", "Ohne ___ fährt Max nicht.", "Der Lehrer fragt ___."],
    "dat": ["Anna hilft ___.", "Das Auto gehört ___.", "Max kommt mit ___.", "Der Film gefällt ___.",
            "Anna wohnt bei ___.", "Der Trainer gibt ___ den Ball.", "Wie geht es ___?", "Das Essen schmeckt ___."],
}
# (reflexive case, verb forms for ich, du, er, sie-she, wir, ihr, sie-they, Sie; sentence after the verb)
REFL_VERBS = [
    ("akk", "wasche wäschst wäscht wäscht waschen wascht waschen waschen", "___ jeden Morgen."),
    ("akk", "freue freust freut freut freuen freut freuen freuen", "___ auf das Wochenende."),
    ("akk", "setze setzt setzt setzt setzen setzt setzen setzen", "___ auf den Stuhl."),
    ("akk", "beeile beeilst beeilt beeilt beeilen beeilt beeilen beeilen", "___ heute."),
    ("dat", "wasche wäschst wäscht wäscht waschen wascht waschen waschen", "___ die Hände."),
    ("dat", "kaufe kaufst kauft kauft kaufen kauft kaufen kaufen", "___ ein neues Handy."),
    ("dat", "putze putzt putzt putzt putzen putzt putzen putzen", "___ die Zähne."),
    ("dat", "merke merkst merkt merkt merken merkt merken merken", "___ die Regel."),
]
REFL_SUBJECTS = [("ich", "Ich", 0), ("du", "Du", 1), ("3", "Er", 2), ("3", "Sie (she)", 3), ("wir", "Wir", 4),
                 ("ihr", "Ihr", 5), ("3", "Sie (they)", 6), ("3", "Sie (you, formal)", 7)]
REL_FRAMES = {
    "nom": ("{a}, ___ dort steht, {be} nett.", "{a}, ___ dort stehen, {be} nett.", "It is the subject of the relative clause, so it is nominative."),
    "akk": ("{a}, ___ ich gestern gesehen habe, {be} nett.", None, "It is the object of gesehen in the relative clause, so it is accusative."),
    "akk2": ("{a}, für ___ ich arbeite, {be} nett.", None, "für takes the accusative."),
    "dat": ("{a}, ___ ich oft helfe, {be} nett.", None, "helfen takes the dative."),
    "dat2": ("{a}, mit ___ ich trainiere, {be} nett.", None, "mit takes the dative."),
    "gen": ("{a}, ___ Auto kaputt ist, {be} nett.", None, "'Whose' is the genitive."),
}
WER_FRAMES = {
    "nom": ["___ kommt heute?", "___ ist das?", "___ trainiert mit dir?"],
    "akk": ["___ siehst du?", "Für ___ ist das Geschenk?", "___ besuchst du morgen?", "___ kennst du hier?"],
    "dat": ["___ hilfst du?", "Mit ___ trainierst du?", "Bei ___ wohnst du?", "___ gehört das Auto?"],
    "gen": ["___ Auto ist das?", "___ Tasche liegt hier?", "___ Handy klingelt?"],
}
WER_WHY = {"nom": "wer asks for the subject.", "akk": "wen asks for an accusative: a direct object or after an accusative preposition.",
           "dat": "wem asks for a dative: after a dative verb or preposition.", "gen": "wessen means 'whose'."}

GENDER_HINTS = [
    (("ung", "heit", "keit", "schaft", "ion", "tät", "ik"), "die", "Words ending in -ung, -heit, -keit, -schaft, -ion, -tät and -ik are feminine."),
    (("chen", "lein"), "das", "Words ending in -chen and -lein are always neuter."),
    (("ment", "um"), "das", "Words ending in -ment and -um are usually neuter."),
    (("ling", "ismus", "ist", "or"), "der", "Words ending in -ling, -ismus, -ist and -or are usually masculine."),
    (("in",), "die", "Female people ending in -in are feminine."),
    (("e",), "die", "Most words ending in -e are feminine."),
    (("er",), "der", "Many words ending in -er, especially people, are masculine, but check each one."),
]

# ---------- families shown in the app ----------
FAMILIES = [
    ("def", "der, die, das", "Articles"), ("dies", "dieser, jeder, welcher", "Articles"), ("ein", "ein, kein", "Articles"),
    ("poss", "mein, dein, sein...", "Articles"),
    ("adjw", "After der-words", "Adjective endings"), ("adjm", "After ein-words", "Adjective endings"),
    ("adjs", "With no article", "Adjective endings"),
    ("pers", "ich, mich, mir...", "Pronouns"), ("refl", "Reflexive: mich, mir, sich", "Pronouns"),
    ("rel", "Relative: der, dem, denen", "Pronouns"), ("wer", "wer, wen, wem, wessen", "Pronouns"),
    ("trig", "Which case?", "Case triggers"),
    ("gender", "Noun genders", "Nouns"), ("plural", "Plurals", "Nouns"), ("noun", "Noun endings", "Nouns"),
    ("combo", "Whole phrases", "Combinations"), ("sent", "In sentences", "Combinations"),
]
FAMILY_LABEL = {f[0]: f[1] for f in FAMILIES}
FAMILY_GROUP = {f[0]: f[2] for f in FAMILIES}
CELL_FAMILIES = ("def", "dies", "ein", "poss", "adjw", "adjm", "adjs", "rel")
BOX_DAYS = {1: None, 2: 1, 3: 3, 4: 7, 5: 21}  # box 1 comes back after 10 minutes
MASTERED_BOX = 4


def _all_keys():
    keys = {f: [f"{f}:{c}:{g}" for c in CASES for g in GENDERS] for f in CELL_FAMILIES}
    keys["pers"] = [f"pers:{c}:{p}" for c in ("akk", "dat") for p in PERSONS]
    keys["refl"] = [f"refl:{c}:{p}" for c in ("akk", "dat") for p in REFL]
    keys["wer"] = [f"wer:{c}" for c in CASES]
    keys["trig"] = list(TRIGGERS)
    keys["gender"] = [f"gender:{n['word']}" for n in NOUNS]
    keys["plural"] = [f"plural:{n['word']}" for n in NOUNS if n["pl"]]
    keys["noun"] = ["noun:dat:pl", "noun:gen:m", "noun:gen:n", "noun:akk:weak", "noun:dat:weak", "noun:gen:weak"]
    adj = keys["adjw"] + keys["adjm"] + keys["adjs"]
    keys["combo"] = adj  # mixed questions are scheduled by the adjective they contain
    keys["sent"] = adj
    return keys


KEYS = _all_keys()
REAL_FAMILIES = [f[0] for f in FAMILIES if f[0] not in ("combo", "sent")]


def key_case(key):
    if key.startswith("trig:"):
        return TRIGGERS[key][1]
    parts = key.split(":")
    return parts[1] if len(parts) > 1 and parts[1] in CASES else None


def key_label(key):
    """A skill key in words, for the coach."""
    p = key.split(":")
    if key.startswith("trig:"):
        return "case after " + TRIGGERS[key][0].replace(" + ?", "")
    if p[0] in ("gender", "plural"):
        return f"{p[0]} of {p[1]}"
    if p[0] == "wer":
        return f"{WER[p[1]]} ({CASE_EN[p[1]]})"
    what = FAMILY_LABEL.get(p[0], p[0])
    if p[0] in ("pers", "refl"):
        return f"{what}: {p[2]} in the {CASE_EN[p[1]]}"
    if p[0] == "noun":
        return f"noun endings: {CASE_EN[p[1]]} {'weak nouns' if p[2] == 'weak' else GENDER_EN[p[2]]}"
    return f"{what}: {CASE_EN[p[1]]} {GENDER_EN[p[2]]}"


# ---------- grammar ----------
def det_form(family, word, case, g):
    if family == "def":
        return ARTICLE[case][g]
    if family == "dies":
        return word + DIES_END[case][g]
    end = EIN_END[case][g]
    return ("eur" if word == "euer" and end else word) + end


def adj_form(adj, cls, case, g):
    return ADJ_STEM.get(adj, adj) + ADJ_END[cls][case][g]


def noun_form(n, case, g):
    if g == "pl":
        return n["pl"] + "n" if case == "dat" and not n["pl"].endswith(("n", "s")) else n["pl"]
    if n["weak"]:
        return n["word"] if case == "nom" else n["gen"]
    return n["gen"] if case == "gen" and n["g"] in "mn" else n["word"]


def noun_alts(n, case, g):
    """Other accepted spellings: des Mannes and des Manns are both standard."""
    form = noun_form(n, case, g)
    if g == "pl" or n["weak"] or case != "gen" or n["g"] == "f":
        return [form]
    w = n["word"]
    if w.endswith(("s", "ß", "z", "x", "sch", "zt", "a", "e", "i", "o", "u", "y", "é", "er", "el", "en", "ing")):
        return [form]
    return [w + "es", w + "s"]


def phrase(det, adj, n, case, g, cls=None):
    """The whole noun phrase as words: det may be None for no article."""
    words = []
    if det:
        words.append(det_form(det[0], det[1], case, g))
    if adj:
        words.append(adj_form(adj, cls, case, g))
    words.append(noun_form(n, case, g))
    return " ".join(words)


def _cue(det, adj, n, case, g, cls):
    """What the learner starts from. Normally the phrase in the nominative; when the nominative itself is asked,
    that would give the answer away, so show the building blocks instead: 'ein- + alt + der Mann'."""
    if case != "nom":
        return phrase(det, adj, n, "nom", g, cls)
    noun = noun_form(n, "nom", g)
    if det and det[0] == "def":  # the article is the answer, so the gender must come from memory
        return " + ".join(([adj] if adj else []) + [noun + (" (plural)" if g == "pl" else "")])
    blocks = ([det[1] + "-"] if det else []) + ([adj] if adj else []) + [f"{ARTICLE['nom'][g]} {noun}"]
    return " + ".join(blocks)


def _adj_cls(det):
    if not det:
        return "s"
    return "w" if det[0] in ("def", "dies") else "m"


def case_tip(case, g, ein=False):
    if ein and not EIN_END[case][g]:
        return "ein-words have no ending in the nominative masculine or the nominative and accusative neuter."
    if case == "nom":
        return "The nominative is the dictionary form."
    if case == "akk":
        if g == "m":
            return "In the accusative only the masculine changes: it ends in -n."
        return f"In the accusative only the masculine changes, so the {GENDER_EN[g]} looks like the nominative."
    if case == "dat":
        if g == "pl":
            return "Dative plural ends in -n, and the noun adds -n too unless it already ends in -n or -s."
        return "Dative feminine ends in -r." if g == "f" else f"Dative {GENDER_EN[g]} ends in -m."
    if g in "mn":
        return f"Genitive {GENDER_EN[g]} ends in -s, and the noun adds -(e)s."
    return f"Genitive {GENDER_EN[g]} ends in -r."


def adj_tip(cls, case, g):
    end = ADJ_END[cls][case][g]
    if cls == "w":
        if end == "e":
            return "After a der-word the adjective takes -e in the nominative singular and the feminine and neuter accusative. Everywhere else it is -en."
        return "After a der-word the adjective takes -en here. Only the nominative singular and feminine and neuter accusative take -e."
    if cls == "m":
        if end == "er":
            return "ein has no ending here, so the adjective shows the gender: -er."
        if end == "es":
            return "ein has no ending here, so the adjective shows the gender: -es."
        if end == "e":
            return "Feminine nominative and accusative: the adjective takes -e, as after die."
        return "After an ein-word every dative, genitive, plural and masculine accusative takes -en."
    if case == "gen" and g in "mn":
        return "With no article the adjective acts like the article, except in the genitive masculine and neuter: -en, because the noun already shows -(e)s."
    return f"With no article the adjective carries the ending the article would have ({ARTICLE[case][g]} → -{end})."


def _pick_word(family, g):
    if family == "dies":
        return random.choice(["dies", "welch", "all"] if g == "pl" else ["dies", "dies", "welch", "jed"])
    return "kein" if g == "pl" else random.choice(["ein", "ein", "kein"])


def _noun(g, tags=None, mass=False):
    pool = [n for n in NOUNS
            if (n["g"] == g if g != "pl" else bool(n["pl"]))
            and ("mass" in n["tags"]) == mass
            and (not tags or set(tags) & set(n["tags"]))]
    return random.choice(pool) if pool else None


def _adj(n):
    tags = [t for t in n["tags"] if t in ADJ_BY_TAG]
    pool = ADJ_BY_TAG[tags[0]][:]
    if "tall" in tags and tags[0] != "tall":
        pool.append("hoch")
    return random.choice(pool)


def _spell_note(adj):
    if adj == "teuer":
        return " teuer drops an e before an ending: teure."
    if adj == "dunkel":
        return " dunkel drops an e before an ending: dunkle."
    if adj == "hoch":
        return " hoch becomes hoh- before an ending: hohe."
    return ""


# ---------- question builders ----------
def _q(family, key, prompt, answers, display, why, cue="", case=None, g=None, hide_case=False, kind="text",
       choices=None, parts=None, full=None):
    return {"family": family, "label": FAMILY_LABEL[family], "key": key, "prompt": prompt, "answers": answers,
            "display": display, "why": why, "cue": cue, "case": case, "gender": g, "hide_case": hide_case,
            "kind": kind, "choices": choices, "parts": parts or [{"key": key}], "full": full or display}


def _gen_article(key):
    family, case, g = key.split(":")
    n = _noun(g)
    if family == "poss":
        owner, eng, word = random.choice(OWNERS)
        det = ("poss", word)
        cue = f"{owner} ({eng}) + {ARTICLE['nom'][g]} {noun_form(n, 'nom', g)}"
    else:
        det = ("def", "der") if family == "def" else (family, _pick_word(family, g))
        cue = _cue(det, None, n, case, g, "w") if case != "nom" or family != "def" else ""
    form = det_form(*det, case, g)
    noun = noun_form(n, case, g)
    extra = ""
    if det[1] == "euer" and EIN_END[case][g]:
        extra = " euer drops an e before an ending: eure, eurem."
    why = case_tip(case, g, family in ("ein", "poss")) + extra
    return _q(family, key, f"___ {noun}", [form], form, why, cue, case, g, full=f"{form} {noun}")


def _gen_adj(key):
    family, case, g = key.split(":")
    cls = family[-1]
    if cls == "s":
        det, n = None, _noun(g, mass=g != "pl")
    else:
        n = _noun(g)
        if cls == "w":
            det = ("def", "der") if random.random() < .6 else ("dies", _pick_word("dies", g))
        elif random.random() < .5:
            det = ("ein", _pick_word("ein", g))
        else:
            det = ("poss", random.choice(OWNERS)[2])
    adj = _adj(n)
    end = ADJ_END[cls][case][g]
    stem = ADJ_STEM.get(adj, adj)
    head = f"{det_form(*det, case, g)} " if det else ""
    prompt = f"{head}{stem}___ {noun_form(n, case, g)}"
    cue = _cue(det, adj, n, case, g, cls)
    return _q(family, key, prompt, [end, stem + end], stem + end, adj_tip(cls, case, g) + _spell_note(adj), cue, case, g,
              full=phrase(det, adj, n, case, g, cls))


def _det_for_class(cls, g, sentence=False):
    if cls == "s":
        return None
    if cls == "w":
        if random.random() < .6:
            return ("def", "der")
        options = (["dies", "all"] if g == "pl" else ["dies", "jed"]) if sentence else None
        return ("dies", random.choice(options) if options else _pick_word("dies", g))
    return ("poss", random.choice(OWNERS)[2]) if random.random() < .5 else ("ein", _pick_word("ein", g))


def _np_parts(det, adj, n, case, g, cls):
    """The skills a phrase trains, each with the word that shows whether it was right."""
    parts = []
    det_family = None
    if det:
        det_family = det[0]
        form = det_form(*det, case, g)
        parts.append({"key": f"{det_family}:{case}:{g}", "tokens": [form]})
    if adj:
        parts.append({"key": f"adj{cls}:{case}:{g}", "tokens": [adj_form(adj, cls, case, g)]})
    nkey = None
    if g == "pl" and case == "dat":
        nkey = "noun:dat:pl"
    elif g != "pl" and n["weak"] and case != "nom":
        nkey = f"noun:{case}:weak"
    elif g in ("m", "n") and case == "gen" and not n["weak"]:
        nkey = f"noun:gen:{g}"
    if nkey:
        parts.append({"key": nkey, "tokens": noun_alts(n, case, g)})
    return parts


def _np_answers(det, adj, n, case, g, cls):
    return [" ".join(filter(None, [det_form(*det, case, g) if det else "", adj_form(adj, cls, case, g) if adj else "", form]))
            for form in noun_alts(n, case, g)]


def _np_why(det, adj, n, case, g, cls):
    bits = []
    if det:
        bits.append(case_tip(case, g, det[0] in ("ein", "poss")))
    if adj:
        bits.append(adj_tip(cls, case, g) + _spell_note(adj))
    elif not det:
        bits.append(case_tip(case, g))
    if n["weak"] and g != "pl" and case != "nom":
        bits.append(f"{n['word']} is a weak noun: it takes -(e)n in every case but the nominative.")
    return " ".join(bits)


def _gen_combo(key):
    family_key, case, g = key.split(":")
    cls = family_key[-1]
    det = _det_for_class(cls, g)
    n = _noun(g, mass=cls == "s" and g != "pl")
    adj = _adj(n) if cls == "s" or random.random() < .75 else None
    cue = _cue(det, adj, n, case, g, cls)
    answers = _np_answers(det, adj, n, case, g, cls)
    return _q("combo", key, "___", answers, answers[0], _np_why(det, adj, n, case, g, cls), cue, case, g,
              parts=_np_parts(det, adj, n, case, g, cls))


def _det_for_family(family, g):
    if family == "def":
        return ("def", "der")
    if family == "dies":
        return ("dies", random.choice(["dies", "all"] if g == "pl" else ["dies", "dies", "jed"]))
    if family == "ein":
        return ("ein", _pick_word("ein", g))
    return ("poss", random.choice(OWNERS)[2])


def gen_det_sentence(key, trig_prefix=None):
    """A sentence where only the article word is needed (no adjective): for learners who haven't reached
    adjective endings yet. key is an article skill such as def:akk:m."""
    return _gen_sentence(key, plain_det=True, trig_prefix=trig_prefix)


def _gen_sentence(key, plain_det=False, trig_prefix=None):
    family_key, case, g = key.split(":")
    cls = "w" if family_key in ("def", "dies") else "m" if plain_det else family_key[-1]
    mass = cls == "s" and g != "pl"
    frames = [f for f in FRAMES if f[0] == case and ("mass" in f[1]) == mass
              and (not trig_prefix or (f[2] or "").startswith(trig_prefix))]
    random.shuffle(frames)
    for fr in frames:
        n = _noun(g, fr[1], mass=mass)
        if not n:
            continue
        _case, _tags, trig, sg, pl, prep, note = fr
        if plain_det:
            det, adj = _det_for_family(family_key, g), None
        else:
            det = _det_for_class(cls, g, sentence=True)
            adj = _adj(n) if cls == "s" or random.random() < .75 else None
        text = pl if g == "pl" and pl else sg
        answers = _np_answers(det, adj, n, case, g, cls)
        cue = _cue(det, adj, n, case, g, cls)
        parts = _np_parts(det, adj, n, case, g, cls)
        art = det_form(*det, case, g) if det else ""
        if prep in CONTRACTING and det and det[0] == "def":
            long_forms = [f"{prep} {a}" for a in answers]
            short = CONTRACT.get((prep, art))
            if short:
                rest = [a.split(" ", 1)[1] for a in answers]
                answers = [f"{short} {r}" for r in rest] + long_forms
                parts[0]["tokens"].append(short)
            else:
                answers = long_forms
            cue = f"{prep} + {cue}"
            prompt = text.replace("{x}", "___")
        elif prep:
            prompt = text.replace("{x}", f"{prep} ___")
        else:
            prompt = text.replace("{x}", "___")
        rule = TRIGGERS[trig][2] if trig else note
        if trig:
            parts.append({"key": trig, "tokens": parts[0]["tokens"]})  # the first word shows if the case was right
        shown = answers[0]
        whole = prompt.replace("___", shown)
        return _q("sent", key, prompt, answers, shown, f"{rule} {_np_why(det, adj, n, case, g, cls)}".strip(), cue, case, g,
                  hide_case=True, parts=parts, full=whole[0].upper() + whole[1:])
    return _gen_article(key) if plain_det else _gen_combo(key)


def _gen_pers(key):
    _f, case, p = key.split(":")
    label, _nom, akk, dat = PERSONS[p]
    form = akk if case == "akk" else dat
    frame = random.choice(PERS_FRAMES[case])
    full = frame.replace("___", form)
    return _q("pers", key, frame, [form], form, _pers_why(case, p, form), label, case, hide_case=True, full=full)


def _pers_why(case, p, form):
    base = f"{PERSONS[p][1]} in the {CASE_EN[case]} is {form}."
    return base + (" For wir and ihr the accusative and dative are the same." if p in ("wir", "ihr") else "")


def _gen_refl(key):
    _f, case, p = key.split(":")
    subject, shown, idx = random.choice([s for s in REFL_SUBJECTS if s[0] == p])
    _c, forms, rest = random.choice([v for v in REFL_VERBS if v[0] == case])
    form = REFL[p][0 if case == "akk" else 1]
    verb = forms.split()[idx]
    plain = shown.split(" (")[0]
    prompt = f"{plain} {verb} {rest}"
    note = (" When the sentence already has another object (die Hände), the reflexive pronoun is dative." if case == "dat"
            else " With no other object in the sentence, the reflexive pronoun is accusative.")
    if p == "3":
        note += " All third-person forms and formal Sie use sich."
    elif p in ("ich", "du"):
        note += " Only ich and du have different accusative and dative forms."
    cue = shown if "(" in shown else ""
    return _q("refl", key, prompt, [form], form, f"{form}: {CASE_EN[case]}.{note}", cue, case, hide_case=True,
              full=prompt.replace("___", form))


def _gen_rel(key):
    _f, case, g = key.split(":")
    n = _noun(g, ("person",))
    frames = [k for k in REL_FRAMES if k.startswith(case)]
    sg, pl, note = REL_FRAMES[random.choice(frames)]
    ante = f"{ARTICLE['nom'][g]} {noun_form(n, 'nom', g)}"
    ante = ante[0].upper() + ante[1:]
    text = (pl if g == "pl" and pl else sg).format(a=ante, be="sind" if g == "pl" else "ist")
    form = RELATIVE[case][g]
    extra = " Genitive forms are dessen and deren." if case == "gen" else (" The dative plural is the one surprise: denen." if case == "dat" and g == "pl" else "")
    why = f"Gender and number come from {ante} ({GENDER_EN[g]}). The case comes from the relative clause: {note}{extra}"
    return _q("rel", key, text, [form], form, why, "", case, g, hide_case=True, full=text.replace("___", form))


def _gen_wer(key):
    case = key.split(":")[1]
    frame = random.choice(WER_FRAMES[case])
    form = WER[case]
    shown = form.capitalize() if frame.startswith("___") else form
    return _q("wer", key, frame, [form], shown, WER_WHY[case], "", case, hide_case=True, full=frame.replace("___", shown))


def _gen_trig(key):
    prompt, case, why = TRIGGERS[key]
    names = ["Akkusativ", "Dativ"] if key.startswith("trig:w:") else ["Akkusativ", "Dativ", "Genitiv"]
    return _q("trig", key, prompt, [CASE_NAME[case]], CASE_NAME[case], why, "", case, hide_case=True, kind="choice",
              choices=names, full=f"{prompt.replace(' + ?', '')} → {CASE_NAME[case]}" if "___" not in prompt else prompt.replace("___", f"[{CASE_NAME[case]}]"))


def _gender_hint(n):
    w = n["word"].lower()
    art = ARTICLE["nom"][n["g"]]
    for ends, hint_art, text in GENDER_HINTS:
        if w.endswith(ends):
            return text if hint_art == art else f"An exception to the pattern: {text}"
    return "No reliable pattern for this one, so learn it with its article."


def _gen_gender(key):
    n = NOUN_BY_WORD[key.split(":")[1]]
    art = ARTICLE["nom"][n["g"]]
    return _q("gender", key, n["word"], [art], art, _gender_hint(n), "", None, n["g"], kind="choice",
              choices=["der", "die", "das"], full=f"{art} {n['word']}")


def _gen_plural(key):
    n = NOUN_BY_WORD[key.split(":")[1]]
    cue = f"{ARTICLE['nom'][n['g']]} {n['word']}"
    return _q("plural", key, f"die ___", [n["pl"], "die " + n["pl"]], n["pl"], "Plurals often change the vowel or add an ending, so learn each noun with its plural.",
              cue, None, "pl", full=f"die {n['pl']}")


def _gen_noun(key):
    _f, case, kind = key.split(":")
    if kind == "pl":
        n = random.choice([x for x in NOUNS if x["pl"] and not x["pl"].endswith(("n", "s"))])
        form = noun_form(n, "dat", "pl")
        return _q("noun", key, "mit den ___", [form], form, "Dative plural: the noun adds -n unless it already ends in -n or -s.",
                  f"die {n['pl']}", "dat", "pl", full=f"mit den {form}")
    if kind == "weak":
        n = random.choice([x for x in NOUNS if x["weak"]])
        frame = {"akk": "Ich sehe den ___.", "dat": "Ich helfe dem ___.", "gen": "Der Name des ___ ist schön."}[case]
        form = n["gen"]
        why = f"{n['word']} is a weak noun: masculine people and animals, often ending in -e, -ist or -ent, take -(e)n in every case but the nominative."
        return _q("noun", key, frame, [form], form, why, f"der {n['word']}", case, "m", full=frame.replace("___", form))
    n = random.choice([x for x in NOUNS if x["g"] == kind and not x["weak"] and "mass" not in x["tags"]])
    frame = "Der Name des ___" if "person" in n["tags"] else "Die Farbe des ___"
    alts = noun_alts(n, "gen", kind)
    return _q("noun", key, frame, alts, alts[0], "Genitive masculine and neuter nouns add -s, or -es after a short word or one ending in -s, -ß, -z or -sch.",
              f"{ARTICLE['nom'][kind]} {n['word']}", "gen", kind, full=frame.replace("___", alts[0]))


GENERATORS = {"def": _gen_article, "dies": _gen_article, "ein": _gen_article, "poss": _gen_article,
              "adjw": _gen_adj, "adjm": _gen_adj, "adjs": _gen_adj, "combo": _gen_combo, "sent": _gen_sentence,
              "pers": _gen_pers, "refl": _gen_refl, "rel": _gen_rel, "wer": _gen_wer, "trig": _gen_trig,
              "gender": _gen_gender, "plural": _gen_plural, "noun": _gen_noun}


# ---------- choosing the next question ----------
def _state():
    return {r["key"]: r for r in db.q("SELECT * FROM decl_skills")}


def _weight(key, st, recent, now):
    if key in recent:
        return .001
    row = st.get(key)
    if not row:
        return 6
    if row["wrong_last"]:
        return 60
    if not row["due"] or row["due"] <= now:
        return 12 + 2 * (5 - row["box"])
    return .5


def _allowed(family, cases):
    keys = KEYS[family]
    return [k for k in keys if key_case(k) is None or key_case(k) in cases] if cases else keys


def _unmastered(family, st):
    return sum(1 for k in KEYS[family] if st.get(k, {}).get("box", 0) < MASTERED_BOX)


def question_for_keys(keys, recent=()):
    """A question on one of the given skills (e.g. the ones linked to Mistake Book entries), weakest first.
    Article and adjective skills come in full sentences part of the time, so the case has to be worked out."""
    pool = [k for k in keys if k in _core_keys()]
    if not pool:
        raise db.UserError("None of these mistakes can be drilled here.")
    st, now = _state(), db.now()
    key = random.choices(pool, [_weight(k, st, set(recent or ()), now) for k in pool])[0]
    family = key.split(":")[0]
    if family in ("def", "dies", "ein", "poss") and random.random() < .5:
        return gen_det_sentence(key)
    if family in ("adjw", "adjm", "adjs") and random.random() < .5:
        return _gen_sentence(key)
    return GENERATORS[family](key)


def next_question(focus=None, cases=None, recent=(), keys=None):
    """focus: families to drill (empty = a smart mix). cases: which cases to include (empty = all).
    keys: drill exactly these skills instead."""
    if keys:
        return question_for_keys(keys, recent)
    st = _state()
    cases = [c for c in (cases or []) if c in CASES]
    now = db.now()
    recent = set(recent or ())
    families = [f for f in (focus or []) if f in KEYS]
    smart = not families
    if smart:
        families = REAL_FAMILIES
    families = [f for f in families if _allowed(f, cases)] or (["def"] if smart else list(focus))
    family = None
    if smart and random.random() < .35:
        family = random.choice(["sent", "sent", "combo"])
        if not _allowed(family, cases):
            family = None
    if not family:
        # Weigh families by what is left to learn, capped so the long noun lists don't take over.
        weights = [1 + min(_unmastered(f, st), 16) for f in families]
        family = random.choices(families, weights)[0]
    pool = _allowed(family, cases) or KEYS[family]
    weights = [_weight(k, st, recent, now) for k in pool]
    key = random.choices(pool, weights)[0]
    return GENERATORS[family](key)


# ---------- grading and scheduling ----------
_ASCII = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "é": "e"})


def norm(s):
    s = (s or "").strip().lower().translate(_ASCII)
    s = re.sub(r"\s+", " ", s)
    return s.lstrip("-–— ").rstrip(".,!? ")


def speed_limit_ms(q):
    if q["kind"] == "choice":
        return 3500
    extra = 3000 if q.get("hide_case") else 0
    return 3500 + extra + 150 * len(q["display"])


def update_skill(key, right, fast, ms=None):
    row = db.q1("SELECT * FROM decl_skills WHERE key=?", (key,))
    now = dt.datetime.now()
    stamp = now.isoformat(timespec="seconds")
    box = row["box"] if row else 0
    if right:
        not_due_yet = row and row["due"] and row["due"] > stamp
        if box < 2:
            box += 1
        elif fast and not not_due_yet:  # higher boxes only rise when the skill was really due, spread over days
            box = min(5, box + 1)
    else:
        box = max(0, box - 2)
    days = BOX_DAYS.get(box)
    due = now if box == 0 else now + (dt.timedelta(days=days) if days else dt.timedelta(minutes=10))
    db.ex("INSERT INTO decl_skills(key, seen, correct, box, due, last_ms, last_seen, wrong_last) VALUES(?,1,?,?,?,?,?,?) "
          "ON CONFLICT(key) DO UPDATE SET seen=seen+1, correct=correct+excluded.correct, box=excluded.box, due=excluded.due, "
          "last_ms=excluded.last_ms, last_seen=excluded.last_seen, wrong_last=excluded.wrong_last",
          (key, int(right), box, due.isoformat(timespec="seconds"), ms, stamp, int(not right)))
    db.ex("INSERT INTO decl_log(key, date, correct) VALUES(?,?,?)", (key, db.today(), int(right)))
    return box


def topic(family):
    return f"Declensions: {FAMILY_GROUP[family].lower()}"


def _log_answer(family, right):
    db.ex("INSERT INTO answers(source, topic, correct, ts, date) VALUES('declension',?,?,?,?)",
          (topic(family), int(right), db.now(), db.today()))


def grade(q, answer, ms=None):
    """Mark one answer and update every skill it trained. In a mixed question, each word counts for its own skill."""
    given = norm(answer)
    right = given in {norm(a) for a in q["answers"]}
    fast = bool(right and ms is not None and ms <= speed_limit_ms(q))
    words = set(given.split())
    wrong_parts = []
    for part in q["parts"]:
        ok = right or any(norm(t) in words for t in part.get("tokens", []))
        update_skill(part["key"], ok, fast, ms)
        if not ok:
            wrong_parts.append(part["key"])
    _log_answer(q["family"], right)
    return {"correct": right, "fast": fast, "wrong_parts": wrong_parts}


def _grid(table_id, title, family, cells_fn, note="", is_ending=False):
    rows = []
    for c in CASES:
        cells = []
        for g in GENDERS:
            form = cells_fn(c, g)
            cells.append({"form": form, "key": f"{family}:{c}:{g}" if form else None})
        rows.append({"label": CASE_NAME[c], "case": c, "cells": cells})
    return {"id": table_id, "title": title, "family": family, "cols": ["Mask.", "Fem.", "Neut.", "Plural"], "rows": rows,
            "note": note, "ending": is_ending}


def tables():
    out = [
        _grid("def", "der, die, das", "def", lambda c, g: ARTICLE[c][g], "Dative plural nouns add -n. Genitive masculine and neuter nouns add -(e)s."),
        _grid("dies", "dieser", "dies", lambda c, g: det_form("dies", "dies", c, g), "jeder, welcher, mancher and jener take the same endings. jeder has no plural: use alle."),
        _grid("ein", "ein", "ein", lambda c, g: None if g == "pl" else det_form("ein", "ein", c, g), "ein has no plural."),
        _grid("kein", "kein", "ein", lambda c, g: det_form("ein", "kein", c, g), "kein takes the same endings as ein, and also has a plural."),
    ]
    for word in ("mein", "dein", "sein", "ihr", "unser", "euer"):
        note = {"euer": "euer drops an e before an ending: eure, eurem, euren.",
                "ihr": "ihr means her or their. Capitalised, Ihr means your (formal).",
                "sein": "sein means his or its."}.get(word, "")
        out.append(_grid(word, word, "poss", lambda c, g, w=word: det_form("poss", w, c, g), note))
    out += [
        _grid("adjw", "Adjective after der-words", "adjw", lambda c, g: "-" + ADJ_END["w"][c][g],
              "After der, dieser, jeder, welcher, alle. Only five slots take -e; all the rest take -en.", True),
        _grid("adjm", "Adjective after ein-words", "adjm", lambda c, g: "-" + ADJ_END["m"][c][g],
              "After ein, kein, mein, dein... Where ein has no ending, the adjective shows the gender: -er or -es.", True),
        _grid("adjs", "Adjective with no article", "adjs", lambda c, g: "-" + ADJ_END["s"][c][g],
              "The adjective takes the article's ending, except in the genitive masculine and neuter: -en.", True),
        _grid("rel", "Relative pronouns", "rel", lambda c, g: RELATIVE[c][g],
              "Like der, die, das, except the genitive (dessen, deren) and the dative plural (denen)."),
    ]
    out.append({"id": "pers", "title": "Personal pronouns", "family": "pers", "cols": ["Nominativ", "Akkusativ", "Dativ"], "ending": False,
                "note": "Genitive forms (meiner, deiner...) are rare today.",
                "rows": [{"label": v[0], "cells": [{"form": v[1], "key": None}, {"form": v[2], "key": f"pers:akk:{p}"},
                                                   {"form": v[3], "key": f"pers:dat:{p}"}]} for p, v in PERSONS.items()]})
    labels = {"ich": "ich", "du": "du", "3": "er, sie, es, sie, Sie", "wir": "wir", "ihr": "ihr"}
    out.append({"id": "refl", "title": "Reflexive pronouns", "family": "refl", "cols": ["Akkusativ", "Dativ"], "ending": False,
                "note": "Dative when the sentence has another object: Ich wasche mir die Hände.",
                "rows": [{"label": labels[p], "cells": [{"form": v[0], "key": f"refl:akk:{p}"}, {"form": v[1], "key": f"refl:dat:{p}"}]}
                         for p, v in REFL.items()]})
    out.append({"id": "wer", "title": "Question words", "family": "wer", "cols": ["who?"], "ending": False, "note": "",
                "rows": [{"label": CASE_NAME[c], "case": c, "cells": [{"form": WER[c], "key": f"wer:{c}"}]} for c in CASES]})
    return out


def trigger_lists():
    groups = [("Always accusative", "akk", "trig:p:"), ("Always dative", "dat", "trig:p:"), ("Always genitive", "gen", "trig:p:"),
              ("Verbs with the dative", "dat", "trig:v:")]
    out = []
    for title, case, prefix in groups:
        out.append({"title": title, "case": case, "items": [
            {"word": k.split(":")[2], "key": k} for k, v in TRIGGERS.items() if k.startswith(prefix) and v[1] == case]})
    out.append({"title": "Two-way: wohin? accusative, wo? dative", "case": None,
                "items": [{"word": w, "key": f"trig:w:{w}:wo"} for w in TWO_WAY]})
    return out


def check_table(table_id, answers):
    """answers: {"row:col": text}. Blank cells are skipped and don't count."""
    table = next((t for t in tables() if t["id"] == table_id), None)
    if not table:
        raise db.UserError("Unknown table")
    results = {}
    for pos, text in answers.items():
        if not (text or "").strip():
            continue
        r, c = map(int, pos.split(":"))
        cell = table["rows"][r]["cells"][c]
        if not cell["form"]:
            continue
        right = norm(text) == norm(cell["form"])
        results[pos] = {"correct": right, "form": cell["form"]}
        if cell["key"]:
            update_skill(cell["key"], right, False)
        _log_answer(table["family"], right)
    return {"results": results}


# ---------- progress ----------
def progress():
    st = _state()
    fams = []
    for fid, label, group in FAMILIES:
        keys = KEYS[fid]
        fams.append({"id": fid, "label": label, "group": group, "total": len(keys),
                     "seen": sum(1 for k in keys if k in st),
                     "mastered": sum(1 for k in keys if st.get(k, {}).get("box", 0) >= MASTERED_BOX),
                     "avg_box": round(sum(st.get(k, {}).get("box", 0) for k in keys) / len(keys), 2)})
    today_row = db.q1("SELECT COUNT(*) AS n, COALESCE(SUM(correct),0) AS c FROM answers WHERE source='declension' AND date=?", (db.today(),))
    return {
        "families": fams,
        "boxes": {k: {"box": v["box"], "seen": v["seen"], "correct": v["correct"]} for k, v in st.items()},
        "today": {"answered": today_row["n"], "correct": today_row["c"]},
        "best_sprint": int(db.get_settings().get("decl_best_sprint") or 0),
    }


def save_sprint(score):
    best = int(db.get_settings().get("decl_best_sprint") or 0)
    if score > best:
        db.set_setting("decl_best_sprint", score)
    return {"best": max(best, score), "new_best": score > best}


def coach_summary():
    """What the coach sees when planning."""
    st = _state()
    p = progress()
    weakest = sorted((r for r in st.values() if r["seen"] >= 2 and r["key"] in _core_keys()),
                     key=lambda r: (r["box"], r["correct"] / r["seen"]))[:8]
    return {
        "how_to_use": "Rule-based declension drills on the Declensions page (free practice). Instant and free, about 3-4 questions a minute.",
        "answered_today": p["today"]["answered"],
        "skills": [{"area": f["label"], "group": f["group"], "seen": f["seen"], "mastered": f["mastered"], "total": f["total"]}
                   for f in p["families"] if f["id"] not in ("combo", "sent")],
        "weakest": [key_label(r["key"]) for r in weakest],
    }


def _core_keys():
    return {k for f in REAL_FAMILIES for k in KEYS[f]}
