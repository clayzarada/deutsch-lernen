"""Verb engine: about 190 common verbs, conjugated by rule in eight tenses, plus the drills built on them.

Rule-based like the declension engine (app/decl.py): instant, free, works offline. Skills share the decl_skills
table (keys start with "vb:" for a tense skill and "vp:" for one verb's principal parts), so spaced repetition,
"skills solid" and the Mistake Book work the same way.
"""
import random
import re

from . import db, decl
from .i18n import lang

# ---------- the verbs ----------
# infinitive | Präteritum (- = regular weak) | Partizip II (- = regular) | aux (h/s) | du,er if the present changes |
# English | Turkish | pattern (strong verbs: for the principal-parts tables)
# Separable verbs are written with | (an|rufen) and take their forms from the base verb. Reflexive: "sich ...".
_DATA = """
sein|war|gewesen|s||to be|olmak|irr
haben|hatte|gehabt|h||to have|sahip olmak|irr
werden|wurde|geworden|s||to become|olmak (dönüşmek)|irr
wissen|wusste|gewusst|h||to know (a fact)|bilmek|mixed
tun|tat|getan|h||to do|yapmak|other
können|konnte|gekonnt|h||can, to be able to|-ebilmek|modal
müssen|musste|gemusst|h||must, to have to|zorunda olmak|modal
dürfen|durfte|gedurft|h||may, to be allowed to|izinli olmak|modal
wollen|wollte|gewollt|h||to want to|istemek|modal
sollen|sollte|gesollt|h||should, to be supposed to|-meli|modal
mögen|mochte|gemocht|h||to like|sevmek, hoşlanmak|modal
machen|-|-|h||to make, to do|yapmak|
sagen|-|-|h||to say|söylemek|
fragen|-|-|h||to ask|sormak|
antworten|-|-|h||to answer|cevap vermek|
arbeiten|-|-|h||to work|çalışmak|
spielen|-|-|h||to play|oynamak|
lernen|-|-|h||to learn|öğrenmek|
kaufen|-|-|h||to buy|satın almak|
verkaufen|-|-|h||to sell|satmak|
hören|-|-|h||to hear, to listen|duymak, dinlemek|
brauchen|-|-|h||to need|ihtiyaç duymak|
glauben|-|-|h||to believe|inanmak|
wohnen|-|-|h||to live (somewhere)|oturmak, yaşamak|
leben|-|-|h||to live|yaşamak|
lieben|-|-|h||to love|sevmek|
kochen|-|-|h||to cook|yemek pişirmek|
suchen|-|-|h||to look for|aramak|
zeigen|-|-|h||to show|göstermek|
bezahlen|-|-|h||to pay|ödemek|
warten|-|-|h||to wait|beklemek|
öffnen|-|-|h||to open|açmak|
reisen|-|-|s||to travel|seyahat etmek|
tanzen|-|-|h||to dance|dans etmek|
putzen|-|-|h||to clean|temizlemek|
legen|-|-|h||to lay, to put|koymak (yatırarak)|
stellen|-|-|h||to put (upright)|koymak (dik)|
lachen|-|-|h||to laugh|gülmek|
holen|-|-|h||to fetch|getirmek, almak|
schicken|-|-|h||to send|göndermek|
besuchen|-|-|h||to visit|ziyaret etmek|
erklären|-|-|h||to explain|açıklamak|
erzählen|-|-|h||to tell|anlatmak|
versuchen|-|-|h||to try|denemek|
gehören|-|-|h||to belong to|ait olmak|
studieren|-|-|h||to study (at university)|okumak (üniversitede)|
telefonieren|-|-|h||to phone|telefonla konuşmak|
probieren|-|-|h||to try (out)|denemek, tatmak|
reparieren|-|-|h||to repair|tamir etmek|
passieren|-|-|s||to happen|olmak (meydana gelmek)|
funktionieren|-|-|h||to work (function)|çalışmak (işlemek)|
kosten|-|-|h||to cost|mal olmak|
dauern|-|-|h||to last|sürmek|
feiern|-|-|h||to celebrate|kutlamak|
wandern|-|-|s||to hike|yürüyüş yapmak|
sammeln|-|-|h||to collect|toplamak|
folgen|-|-|s||to follow|takip etmek|
danken|-|-|h||to thank|teşekkür etmek|
gratulieren|-|-|h||to congratulate|tebrik etmek|
wünschen|-|-|h||to wish|dilemek|
schmecken|-|-|h||to taste|tadı olmak|
passen|-|-|h||to fit|uymak|
fehlen|-|-|h||to be missing|eksik olmak|
packen|-|-|h||to pack|toplamak (bavul)|
malen|-|-|h||to paint|resim yapmak|
zeichnen|-|-|h||to draw|çizmek|
rechnen|-|-|h||to calculate|hesaplamak|
baden|-|-|h||to bathe|banyo yapmak|
duschen|-|-|h||to shower|duş almak|
frühstücken|-|-|h||to have breakfast|kahvaltı etmek|
fühlen|-|-|h||to feel|hissetmek|
benutzen|-|-|h||to use|kullanmak|
übernachten|-|-|h||to stay overnight|gecelemek|
heiraten|-|-|h||to marry|evlenmek|
klingeln|-|-|h||to ring|çalmak (zil)|
regnen|-|-|h||to rain|yağmur yağmak|
auf|machen|-|-|h||to open|açmak|
zu|machen|-|-|h||to close|kapatmak|
ein|kaufen|-|-|h||to shop|alışveriş yapmak|
auf|hören|-|-|h||to stop|bırakmak, durmak|
ab|holen|-|-|h||to pick up|almak (birini/bir şeyi)|
auf|räumen|-|-|h||to tidy up|toplamak, düzenlemek|
mit|machen|-|-|h||to join in|katılmak|
an|machen|-|-|h||to switch on|açmak (cihaz)|
aus|machen|-|-|h||to switch off|kapatmak (cihaz)|
fahren|fuhr|gefahren|s|fährst,fährt|to drive, to go|gitmek (araçla), sürmek|a-u-a
tragen|trug|getragen|h|trägst,trägt|to carry, to wear|taşımak, giymek|a-u-a
waschen|wusch|gewaschen|h|wäschst,wäscht|to wash|yıkamak|a-u-a
wachsen|wuchs|gewachsen|s|wächst,wächst|to grow|büyümek|a-u-a
schlagen|schlug|geschlagen|h|schlägst,schlägt|to hit|vurmak|a-u-a
laden|lud|geladen|h|lädst,lädt|to load|yüklemek|a-u-a
schlafen|schlief|geschlafen|h|schläfst,schläft|to sleep|uyumak|a-ie-a
fallen|fiel|gefallen|s|fällst,fällt|to fall|düşmek|a-ie-a
halten|hielt|gehalten|h|hältst,hält|to hold, to stop|tutmak, durmak|a-ie-a
lassen|ließ|gelassen|h|lässt,lässt|to let, to leave|bırakmak|a-ie-a
laufen|lief|gelaufen|s|läufst,läuft|to run, to walk|koşmak, yürümek|a-ie-a
fangen|fing|gefangen|h|fängst,fängt|to catch|yakalamak|a-i-a
rufen|rief|gerufen|h||to call|seslenmek|other
heißen|hieß|geheißen|h||to be called|adı olmak|other
geben|gab|gegeben|h|gibst,gibt|to give|vermek|e-a-e
essen|aß|gegessen|h|isst,isst|to eat|yemek|e-a-e
lesen|las|gelesen|h|liest,liest|to read|okumak|e-a-e
sehen|sah|gesehen|h|siehst,sieht|to see|görmek|e-a-e
vergessen|vergaß|vergessen|h|vergisst,vergisst|to forget|unutmak|e-a-e
helfen|half|geholfen|h|hilfst,hilft|to help|yardım etmek|e-a-o
sprechen|sprach|gesprochen|h|sprichst,spricht|to speak|konuşmak|e-a-o
nehmen|nahm|genommen|h|nimmst,nimmt|to take|almak|e-a-o
treffen|traf|getroffen|h|triffst,trifft|to meet|buluşmak|e-a-o
werfen|warf|geworfen|h|wirfst,wirft|to throw|atmak|e-a-o
sterben|starb|gestorben|s|stirbst,stirbt|to die|ölmek|e-a-o
brechen|brach|gebrochen|h|brichst,bricht|to break|kırmak|e-a-o
empfehlen|empfahl|empfohlen|h|empfiehlst,empfiehlt|to recommend|tavsiye etmek|e-a-o
kommen|kam|gekommen|s||to come|gelmek|other
bekommen|bekam|bekommen|h||to get, to receive|almak (elde etmek)|other
finden|fand|gefunden|h||to find|bulmak|i-a-u
trinken|trank|getrunken|h||to drink|içmek|i-a-u
singen|sang|gesungen|h||to sing|şarkı söylemek|i-a-u
springen|sprang|gesprungen|s||to jump|zıplamak|i-a-u
beginnen|begann|begonnen|h||to begin|başlamak|i-a-o
schwimmen|schwamm|geschwommen|s||to swim|yüzmek|i-a-o
gewinnen|gewann|gewonnen|h||to win|kazanmak|i-a-o
sitzen|saß|gesessen|h||to sit|oturmak|other
liegen|lag|gelegen|h||to lie (be lying)|yatmak, bulunmak|other
bitten|bat|gebeten|h||to ask (for)|rica etmek|other
bleiben|blieb|geblieben|s||to stay|kalmak|ei-ie-ie
schreiben|schrieb|geschrieben|h||to write|yazmak|ei-ie-ie
scheinen|schien|geschienen|h||to shine, to seem|parlamak, görünmek|ei-ie-ie
steigen|stieg|gestiegen|s||to climb, to rise|çıkmak, yükselmek|ei-ie-ie
leihen|lieh|geliehen|h||to lend|ödünç vermek|ei-ie-ie
entscheiden|entschied|entschieden|h||to decide|karar vermek|ei-ie-ie
schneiden|schnitt|geschnitten|h||to cut|kesmek|ei-i-i
streiten|stritt|gestritten|h||to argue|tartışmak|ei-i-i
fliegen|flog|geflogen|s||to fly|uçmak|ie-o-o
ziehen|zog|gezogen|h||to pull|çekmek|ie-o-o
verlieren|verlor|verloren|h||to lose|kaybetmek|ie-o-o
schließen|schloss|geschlossen|h||to close|kapatmak|ie-o-o
bieten|bot|geboten|h||to offer|sunmak|ie-o-o
genießen|genoss|genossen|h||to enjoy|keyfini çıkarmak|ie-o-o
lügen|log|gelogen|h||to lie (tell lies)|yalan söylemek|ie-o-o
gehen|ging|gegangen|s||to go|gitmek|other
stehen|stand|gestanden|h||to stand|ayakta durmak|other
verstehen|verstand|verstanden|h||to understand|anlamak|other
hängen|hing|gehangen|h||to hang (be hanging)|asılı durmak|other
gefallen|gefiel|gefallen|h|gefällst,gefällt|to please, to like|hoşuna gitmek|a-ie-a
verlassen|verließ|verlassen|h|verlässt,verlässt|to leave|terk etmek, çıkmak|a-ie-a
bringen|brachte|gebracht|h||to bring|getirmek|mixed
denken|dachte|gedacht|h||to think|düşünmek|mixed
kennen|kannte|gekannt|h||to know (be familiar with)|tanımak|mixed
nennen|nannte|genannt|h||to name, to call|adlandırmak|mixed
rennen|rannte|gerannt|s||to run|koşmak|mixed
brennen|brannte|gebrannt|h||to burn|yanmak|mixed
an|rufen|||h||to call (phone)|telefonla aramak|
auf|stehen|||s||to get up|kalkmak|
an|kommen|||s||to arrive|varmak|
mit|kommen|||s||to come along|birlikte gelmek|
zurück|kommen|||s||to come back|geri gelmek|
ein|laden|||h||to invite|davet etmek|
an|fangen|||h||to begin|başlamak|
fern|sehen|||h||to watch TV|televizyon izlemek|
aus|sehen|||h||to look (appear)|görünmek|
um|ziehen|||s||to move (house)|taşınmak|
ab|fahren|||s||to depart|hareket etmek, kalkmak|
ein|schlafen|||s||to fall asleep|uykuya dalmak|
aus|gehen|||s||to go out|dışarı çıkmak|
statt|finden|||h||to take place|gerçekleşmek|
mit|nehmen|||h||to take along|yanına almak|
ein|steigen|||s||to get in|binmek|
aus|steigen|||s||to get out|inmek|
an|bieten|||h||to offer|teklif etmek|
vor|lesen|||h||to read aloud|sesli okumak|
sich freuen|-|-|h||to be happy|sevinmek|
sich interessieren|-|-|h||to be interested|ilgilenmek|
sich beeilen|-|-|h||to hurry|acele etmek|
sich erholen|-|-|h||to recover, to relax|dinlenmek|
sich entschuldigen|-|-|h||to apologize|özür dilemek|
sich ärgern|-|-|h||to be annoyed|sinirlenmek|
sich kümmern|-|-|h||to take care|ilgilenmek, bakmak|
sich setzen|-|-|h||to sit down|oturmak (yerleşmek)|
sich waschen|wusch|gewaschen|h|wäschst,wäscht|to wash (oneself)|yıkanmak|
sich treffen|traf|getroffen|h|triffst,trifft|to meet (each other)|buluşmak|
sich an|ziehen|||h||to get dressed|giyinmek|
sich vor|stellen|||h||to introduce oneself|kendini tanıtmak|
"""

PRESENT_IRR = {  # whole present rows that no rule produces
    "sein": "bin bist ist sind seid sind", "haben": "habe hast hat haben habt haben",
    "werden": "werde wirst wird werden werdet werden", "wissen": "weiß weißt weiß wissen wisst wissen",
    "tun": "tue tust tut tun tut tun", "können": "kann kannst kann können könnt können",
    "müssen": "muss musst muss müssen müsst müssen", "dürfen": "darf darfst darf dürfen dürft dürfen",
    "wollen": "will willst will wollen wollt wollen", "sollen": "soll sollst soll sollen sollt sollen",
    "mögen": "mag magst mag mögen mögt mögen",
}
# Konjunktiv II forms of their own: required for sein, haben and the modal verbs, accepted for the rest.
KONJ2_OWN = {"sein": "wäre", "haben": "hätte", "werden": "würde", "können": "könnte", "müssen": "müsste",
             "dürfen": "dürfte", "mögen": "möchte", "wollen": "wollte", "sollen": "sollte", "wissen": "wüsste",
             "kommen": "käme", "gehen": "ginge", "geben": "gäbe", "finden": "fände", "bleiben": "bliebe",
             "lassen": "ließe", "tun": "täte"}
KONJ2_REQUIRED = {"sein", "haben", "werden", "können", "müssen", "dürfen", "mögen", "wollen", "sollen", "wissen"}
INSEP = ("be", "ge", "er", "ver", "zer", "ent", "emp", "miss", "über")
REFL = ["mich", "dich", "sich", "uns", "euch", "sich"]
PERSONS = ["ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie"]
SUBJECTS = [(0, "ich"), (1, "du"), (2, "er"), (2, "sie (she)"), (2, "es"), (2, "man"), (3, "wir"), (4, "ihr"),
            (5, "sie (they)"), (5, "Sie")]
TENSES = {"praes": "Präsens", "perf": "Perfekt", "fut1": "Futur I", "modal": "Modalverben", "praet": "Präteritum",
          "plusq": "Plusquamperfekt", "konj2": "Konjunktiv II", "fut2": "Futur II"}
WERDEN = PRESENT_IRR["werden"].split()


def _parse():
    out, by = [], {}
    for line in _DATA.strip().splitlines():
        parts = line.split("|")
        if len(parts) == 9:  # a separable verb: prefix|base|...
            prefix, rest = parts[0], parts[1:]
        else:
            prefix, rest = "", parts
        inf, praet, pp, aux, pres, en, tr, pattern = rest
        refl = inf.startswith("sich ")
        if refl:
            inf = inf[5:]
            if " " in prefix:  # "sich an" | "ziehen"
                pass
        if prefix.startswith("sich "):
            refl, prefix = True, prefix[5:]
        v = {"base": inf, "prefix": prefix, "inf": prefix + inf, "praet": praet, "pp": pp, "aux": aux,
             "pres": pres.split(",") if pres else None, "en": en, "tr": tr, "pattern": pattern, "refl": refl}
        out.append(v)
        by.setdefault(v["inf"], v)
    return out, by


VERBS, _BY_INF = _parse()


def _base(v):
    """The verb a separable verb takes its forms from (an|rufen -> rufen)."""
    if v["prefix"] and (not v["praet"] or not v["pp"]):
        b = _BY_INF.get(v["base"])
        if b:
            return b
    return v


def display_inf(v):
    return ("sich " if v["refl"] else "") + v["inf"]


def meaning(v):
    return v["tr"] if lang() == "tr" else v["en"]


# ---------- classifying ----------
def is_modal(v):
    return v["pattern"] == "modal"


def is_irr(v):
    return v["pattern"] == "irr" or v["inf"] in ("wissen", "tun")


def strength(v):
    """weak, strong, mixed or irr (sein, haben, werden)."""
    b = _base(v)
    if b["pattern"] == "irr":
        return "irr"
    if b["pattern"] in ("mixed", "modal"):
        return "mixed"
    if b["praet"] in ("-", ""):
        return "weak"
    return "strong"


def _insep(inf):
    return any(inf.startswith(p) and len(inf) > len(p) + 3 for p in INSEP)


def no_ge(v):
    """Partizip II without ge-: -ieren verbs and inseparable prefixes."""
    if v["prefix"]:
        return False
    inf = v["inf"]
    return inf.endswith("ieren") or (_insep(inf) and inf not in ("geben", "gehen", "essen", "erben"))


# ---------- forms ----------
def _stem(inf):
    if inf.endswith(("eln", "ern")) and not inf.endswith("ieren"):
        return inf[:-1]
    return inf[:-2]


def _needs_e(stem):
    """arbeiten -> du arbeitest, öffnen -> er öffnet."""
    if stem.endswith(("t", "d")):
        return True
    return bool(re.search(r"[^aeiouäöülrhmn][mn]$", stem))


def _present_simple(v):
    """Six finite present forms of a verb without its separable prefix."""
    b = v if not v["prefix"] else _BY_INF.get(v["base"], v)
    inf = b["base"] if b["prefix"] else b["inf"]
    if inf in PRESENT_IRR:
        return PRESENT_IRR[inf].split()
    st = _stem(inf)
    e = "e" if _needs_e(st) else ""
    if inf.endswith("eln"):
        ich = st[:-2] + "le"
    elif inf.endswith("ern"):
        ich = st + "e"
    else:
        ich = st + "e"
    du = st + e + ("t" if st.endswith(("s", "ß", "z", "x")) else "st")
    er = st + e + "t"
    wir = inf
    ihr = st + e + "t"
    pres = b["pres"] or v["pres"]
    if pres:
        du, er = pres
    return [ich, du, er, wir, ihr, wir]


def _praet_stem(v):
    b = _base(v)
    if b["praet"] not in ("-", ""):
        return b["praet"] if not v["prefix"] or b is not v else b["praet"]
    inf = b["base"] if b["prefix"] else b["inf"]
    st = _stem(inf)
    return st + ("e" if _needs_e(st) else "") + "te"


def _praet_simple(v):
    p = _praet_stem(v)
    if p.endswith("e"):
        return [p, p + "st", p, p + "n", p + "t", p + "n"]
    es = "e" if p.endswith(("t", "d", "s", "ß", "z")) else ""
    et = "e" if p.endswith(("t", "d")) else ""
    du = p + ("est" if p.endswith(("s", "ß", "z")) else es + "st")
    return [p, du, p, p + "en", p + et + "t", p + "en"]


def partizip(v):
    b = _base(v)
    if v["prefix"]:
        if b["pp"] not in ("-", ""):
            return v["prefix"] + b["pp"]
        st = _stem(v["base"])
        return v["prefix"] + "ge" + st + ("e" if _needs_e(st) else "") + "t"
    if v["pp"] not in ("-", ""):
        return v["pp"]
    st = _stem(v["inf"])
    t = ("e" if _needs_e(st) else "") + "t"
    if no_ge(v):
        return st + t
    return "ge" + st + t


def aux_present(v):
    return PRESENT_IRR["sein" if v["aux"] == "s" else "haben"].split()


def aux_praet(v):
    return ["war", "warst", "war", "waren", "wart", "waren"] if v["aux"] == "s" else ["hatte", "hattest", "hatte", "hatten", "hattet", "hatten"]


def _join(*parts):
    return " ".join(p for p in parts if p)


def forms(v, tense, p):
    """All accepted answers for verb v, tense, person index p (0-5). The first is the one shown."""
    refl = REFL[p] if v["refl"] else ""
    pre = v["prefix"]
    if tense in ("praes", "modal") and not (tense == "modal" and not is_modal(v)):
        return [_join(_present_simple(v)[p], refl, pre)]
    if tense == "praet":
        return [_join(_praet_simple(v)[p], refl, pre)]
    if tense == "perf":
        return [_join(aux_present(v)[p], refl, partizip(v))]
    if tense == "plusq":
        return [_join(aux_praet(v)[p], refl, partizip(v))]
    if tense == "fut1":
        return [_join(WERDEN[p], refl, v["inf"])]
    if tense == "fut2":
        return [_join(WERDEN[p], refl, partizip(v), "sein" if v["aux"] == "s" else "haben")]
    if tense == "konj2":
        own = KONJ2_OWN.get(v["base"] if not pre else v["base"])
        out = []
        if own:
            stem_forms = [own, own + "st", own, own + "n", own + "t", own + "n"]
            out.append(_join(stem_forms[p], refl, pre))
            if p in (1, 4) and not own.endswith("te") and own != "würde":  # wärst / kämt as well as wärest / kämet
                out.append(_join(own[:-1] + ("st" if p == 1 else "t"), refl, pre))
        wuerde = _join(KONJ2_W[p], refl, v["inf"])
        if v["inf"] in KONJ2_REQUIRED:
            return out or [wuerde]
        return [wuerde] + [o for o in out if o != wuerde]
    raise ValueError(tense)


KONJ2_W = ["würde", "würdest", "würde", "würden", "würdet", "würden"]


# ---------- skills ----------
def tense_key(v, tense):
    """The skill a form of this verb in this tense trains."""
    if tense == "praes":
        if is_modal(v):
            return "vb:modal:praes"
        if is_irr(v):
            return "vb:praes:irr"
        if v["prefix"]:
            return "vb:praes:sep"
        if v["pres"] or _base(v)["pres"]:
            return "vb:praes:stem"
        return "vb:praes:reg"
    if tense == "praet":
        if is_modal(v):
            return "vb:modal:praet"
        s = strength(v)
        return {"weak": "vb:praet:weak", "strong": "vb:praet:strong", "mixed": "vb:praet:mixed", "irr": "vb:praet:irr"}[s]
    if tense == "perf":
        return pp_key(v)
    if tense == "konj2":
        return "vb:konj2:irr" if v["inf"] in KONJ2_REQUIRED else "vb:konj2:wuerde"
    if tense == "modal":
        return "vb:modal:praes"
    return f"vb:{tense}"


def pp_key(v):
    if v["prefix"]:
        return "vb:pp:sep"
    if no_ge(v):
        return "vb:pp:noge"
    return "vb:pp:weak" if strength(v) == "weak" else "vb:pp:strong"


TENSE_KEYS = {
    "praes": ["vb:praes:reg", "vb:praes:stem", "vb:praes:irr", "vb:praes:sep"],
    "perf": ["vb:perf:aux", "vb:pp:weak", "vb:pp:strong", "vb:pp:noge", "vb:pp:sep"],
    "fut1": ["vb:fut1"],
    "modal": ["vb:modal:praes", "vb:modal:praet", "vb:modal:sent"],
    "praet": ["vb:praet:weak", "vb:praet:strong", "vb:praet:mixed", "vb:praet:irr"],
    "plusq": ["vb:plusq"],
    "konj2": ["vb:konj2:wuerde", "vb:konj2:irr"],
    "fut2": ["vb:fut2"],
}
PARTS_VERBS = [v for v in VERBS if not v["prefix"] and strength(v) in ("strong", "mixed", "irr") and not is_modal(v)
               and not v["refl"]]


def key_tense(key):
    p = key.split(":")
    if p[0] == "vp":
        return None
    if p[1] == "pp":
        return "perf"
    return p[1] if p[1] in TENSES else None


def _verbs_for(key, need=None):
    """Verbs whose form trains this skill."""
    p = key.split(":")
    if p[0] == "vp":
        return [_BY_INF[p[1]]]
    t = key_tense(key)
    if key == "vb:perf:aux":
        pool = [v for v in VERBS if not is_modal(v)]
    elif key in ("vb:modal:praes", "vb:modal:praet", "vb:modal:sent"):
        pool = [v for v in VERBS if is_modal(v)]
    elif p[1] == "pp":
        pool = [v for v in VERBS if not is_modal(v) and pp_key(v) == key]
    elif t in ("fut1", "fut2", "plusq"):
        pool = [v for v in VERBS if not is_modal(v)]
    else:
        pool = [v for v in VERBS if tense_key(v, t) == key and not (is_modal(v) and t != "konj2")]
    if need:
        pool = [v for v in pool if need(v)] or pool
    return pool


# ---------- explanations (each sentence has a Turkish version in app/i18n.py) ----------
def _aux_why(v):
    if v["aux"] == "s":
        if v["base"] in ("sein", "bleiben", "werden", "passieren"):
            return f"{display_inf(v)} takes sein, like sein, werden, bleiben and passieren."
        return f"{display_inf(v)} takes sein: it describes movement or a change of state."
    return f"{display_inf(v)} takes haben, like most verbs."


def why(v, tense, key):
    inf = display_inf(v)
    s = []
    if tense in ("praes", "modal") and key != "vb:modal:praet":
        if key == "vb:praes:irr" or is_modal(v):
            s.append(f"{inf} is irregular in the present: learn the whole row.")
            if is_modal(v):
                s.append("Modal verbs have no ending in ich and er/sie/es: ich kann, er kann.")
        elif key == "vb:praes:stem":
            pres = v["pres"] or _base(v)["pres"]
            s.append(f"{inf} changes its vowel in du and er/sie/es: du {pres[0]}, er {pres[1]}.")
        else:
            s.append("Präsens: stem + -e, -st, -t, -en, -t, -en.")
            st = _stem(_base(v)["inf"] if v["prefix"] else v["inf"])
            if _needs_e(st):
                s.append("Stems ending in -t, -d or a consonant + -m/-n add an -e- before -st and -t: du arbeitest, er öffnet.")
        if v["prefix"]:
            s.append(f"{inf} is separable: the prefix {v['prefix']} goes to the end.")
    elif tense in ("praet",) or key == "vb:modal:praet":
        st = strength(v)
        if is_modal(v):
            s.append(f"Modal verbs in the Präteritum take -te and lose the umlaut: {_praet_stem(v)}.")
        elif st == "weak":
            s.append("Weak verbs add -te: -te, -test, -te, -ten, -tet, -ten.")
        elif st == "strong":
            s.append(f"{inf} is a strong verb: Präteritum {_praet_stem(v)}. ich and er/sie/es have no ending.")
        elif st == "mixed":
            s.append(f"{inf} is a mixed verb: a vowel change and -te: {_praet_stem(v)}.")
        else:
            s.append(f"{inf} is irregular: {_praet_stem(v)}.")
        if v["prefix"]:
            s.append(f"{inf} is separable: the prefix {v['prefix']} goes to the end.")
    elif tense in ("perf", "plusq", "fut2"):
        s.append({"perf": "Perfekt: haben or sein in the present + Partizip II.",
                  "plusq": "Plusquamperfekt: haben or sein in the Präteritum + Partizip II.",
                  "fut2": "Futur II: werden + Partizip II + haben or sein."}[tense])
        s.append(_aux_why(v))
        s.append(pp_why(v))
    elif tense == "fut1":
        s.append("Futur I: werden in the present + the infinitive at the end.")
    elif tense == "konj2":
        own = KONJ2_OWN.get(v["base"])
        if v["inf"] in KONJ2_REQUIRED:
            s.append(f"{inf} uses its own Konjunktiv II form ({own}), not würde + infinitive.")
        else:
            s.append("Konjunktiv II: würde + infinitive works for almost every verb.")
            if own:
                s.append(f"{inf} also has its own form: {own}.")
    if v["refl"]:
        s.append("Reflexive verbs keep their pronoun: mich, dich, sich, uns, euch, sich.")
    return " ".join(s)


def pp_why(v):
    pp = partizip(v)
    k = pp_key(v)
    if k == "vb:pp:sep":
        return f"Separable verbs put ge- after the prefix: {pp}."
    if k == "vb:pp:noge":
        return f"No ge- for verbs ending in -ieren or starting with be-, ver-, er-, ent-, emp-, ge-, zer-: {pp}."
    if k == "vb:pp:weak":
        return f"Weak Partizip II: ge- + stem + -t: {pp}."
    if strength(v) in ("mixed", "irr") and pp.endswith("t"):
        return f"{display_inf(v)} has an irregular Partizip II: a vowel change but -t: {pp}."
    return f"Strong Partizip II, often with a new vowel and -en: {pp}."


# ---------- question builders ----------
def _q(family, key, prompt, answers, display, why_text, cue="", tense=None, kind="text", choices=None, parts=None, full=None):
    return {"family": family, "label": FAMILY_LABEL[family], "key": key, "prompt": prompt, "answers": answers,
            "display": display, "why": why_text, "cue": cue, "case": tense, "gender": None, "hide_case": False,
            "kind": kind, "choices": choices, "parts": parts or [{"key": key}], "full": full or display}


def _pick_subject(v, tense):
    p, shown = random.choice(SUBJECTS)
    return p, shown


def gen_conj(key):
    t = key_tense(key) or "praes"
    if key == "vb:perf:aux":
        t = "perf"
    if key == "vb:modal:praet":
        t = "praet"
    v = random.choice(_verbs_for(key))
    p, shown = _pick_subject(v, t)
    tense_for_forms = "praes" if t == "modal" else t
    ans = forms(v, tense_for_forms, p)
    parts = [{"key": key}]
    if t in ("perf", "plusq", "fut2"):
        parts = [{"key": pp_key(v), "tokens": [partizip(v)]}, {"key": "vb:perf:aux", "tokens": [ans[0].split()[0]]}]
    if t == "plusq":
        parts.append({"key": "vb:plusq"})
    if t == "fut2":
        parts.append({"key": "vb:fut2"})
    subj = shown.split(" (")[0]
    return _q("conj", key, f"{shown} ___", ans, ans[0], why(v, t, key), f"{display_inf(v)} · {meaning(v)}",
              "modal" if key.startswith("vb:modal") else t, parts=parts, full=f"{subj} {ans[0]}")


def gen_aux(key):
    v = random.choice(_verbs_for("vb:perf:aux"))
    ans = "sein" if v["aux"] == "s" else "haben"
    return _q("aux", "vb:perf:aux", f"{display_inf(v)} → ___ {partizip(v)}", [ans], ans, _aux_why(v), meaning(v), "perf",
              kind="choice", choices=["haben", "sein"], full=f"{'ist' if ans == 'sein' else 'hat'} {partizip(v)}")


def gen_pp(key):
    v = random.choice(_verbs_for(key))
    pp = partizip(v)
    aux = "ist" if v["aux"] == "s" else "hat"
    return _q("pp", key, f"{display_inf(v)} → {aux} ___", [pp, f"{aux} {pp}"], pp, pp_why(v), meaning(v), "perf",
              full=f"{display_inf(v)} → {aux} {pp}")


def gen_parts(key):
    v = _BY_INF[key.split(":")[1]]
    pr, pp = _praet_stem(v), partizip(v)
    er = _present_simple(v)[2]
    aux = "ist" if v["aux"] == "s" else "hat"
    answers = [f"{pr} {pp}", f"{pr}, {pp}", f"{pr} - {pp}", f"{pr} – {pp}", f"{pr} {aux} {pp}", f"{pr}, {aux} {pp}",
               f"{pr} – {aux} {pp}", f"{pr} - {aux} {pp}"]
    shown = f"{pr} – {aux} {pp}"
    return _q("parts", key, f"{v['inf']} – ___", answers, shown,
              f"Principal parts: {v['inf']} – {pr} – {aux} {pp} (er {er}). Learn strong verbs as a set of three.",
              f"{meaning(v)} · Präteritum, Partizip II", None, full=f"{v['inf']} – {pr} – {aux} {pp}")


# Sentences: a time word decides the tense. Complements for verbs that fit a simple sentence.
COMPL = {
    "fahren": "nach Hamburg", "kaufen": "ein Brot", "essen": "eine Pizza", "trinken": "einen Kaffee", "lesen": "ein Buch",
    "schreiben": "eine E-Mail", "sehen": "einen Film", "spielen": "Fußball", "lernen": "Deutsch", "arbeiten": "im Büro",
    "kochen": "eine Suppe", "gehen": "ins Kino", "kommen": "nach Hause", "schlafen": "lange", "laufen": "im Park",
    "fliegen": "nach Rom", "bleiben": "zu Hause", "finden": "den Schlüssel", "nehmen": "den Bus", "helfen": "der Nachbarin",
    "besuchen": "die Oma", "bezahlen": "die Rechnung", "verkaufen": "das Auto", "treffen": "alte Freunde",
    "sprechen": "mit dem Chef", "warten": "auf den Bus", "suchen": "eine Wohnung", "machen": "die Hausaufgaben",
    "hören": "Musik", "tanzen": "die ganze Nacht", "reisen": "nach Spanien", "schwimmen": "im See", "waschen": "das Auto",
    "bringen": "Blumen", "vergessen": "den Termin", "verstehen": "die Frage", "geben": "dem Kind ein Eis",
    "telefonieren": "mit Anna", "studieren": "in Berlin", "wandern": "in den Bergen", "singen": "ein Lied",
    "verlieren": "das Spiel", "gewinnen": "das Spiel", "tragen": "einen Mantel", "denken": "an dich",
    "sagen": "die Wahrheit", "fragen": "den Lehrer", "glauben": "an das Gute", "wohnen": "in Köln", "leben": "in Spanien",
    "lieben": "das Meer", "zeigen": "ihm die Stadt", "öffnen": "die Tür", "putzen": "das Bad", "lachen": "über den Witz",
    "holen": "Brötchen", "schicken": "ein Paket", "erklären": "die Regel", "erzählen": "eine Geschichte",
    "versuchen": "ein neues Rezept", "probieren": "den Kuchen", "reparieren": "das Fahrrad", "feiern": "den Geburtstag",
    "sammeln": "Briefmarken", "folgen": "dem Weg", "danken": "der Lehrerin", "gratulieren": "dem Gewinner",
    "wünschen": "dir alles Gute", "packen": "den Koffer", "malen": "ein Bild", "zeichnen": "eine Karte",
    "rechnen": "im Kopf", "duschen": "kalt", "frühstücken": "im Hotel", "benutzen": "das Wörterbuch",
    "übernachten": "im Zelt", "heiraten": "im Mai", "kennen": "den Weg", "rennen": "zum Bus", "bitten": "um Hilfe",
    "sitzen": "im Garten", "liegen": "am Strand", "stehen": "an der Kasse", "springen": "ins Wasser",
    "empfehlen": "das Restaurant", "werfen": "den Ball", "fangen": "den Ball", "halten": "eine Rede",
    "schließen": "die Tür", "genießen": "die Sonne", "leihen": "ihm Geld", "schneiden": "das Brot",
    "streiten": "mit dem Nachbarn", "steigen": "auf den Berg", "bekommen": "einen Brief", "verlassen": "das Haus",
    "wissen": "die Antwort", "haben": "keine Zeit", "sein": "sehr müde",
}
SENT_SUBJECTS = [(0, "Ich"), (1, "Du"), (2, "Anna"), (2, "Max"), (3, "Wir"), (4, "Ihr"), (5, "Meine Eltern")]
TIME = {"praes": "heute", "praet": "damals", "perf": "gestern", "fut1": "morgen", "konj2": "gern",
        "plusq": "schon", "fut2": "bis morgen"}


def _sent_verb(key):
    # Reflexive verbs share an infinitive with their plain verb ("sich treffen"/"treffen") but not its object.
    return random.choice(_verbs_for(key, need=lambda v: v["inf"] in COMPL and not v["refl"]))


def gen_vsent(key):
    t = key_tense(key) or "praes"
    p, subj = random.choice(SENT_SUBJECTS)
    if key == "vb:konj2:irr":
        v = _BY_INF[random.choice(["sein", "haben"])]
        c = "jetzt gern am Meer" if v["inf"] == "sein" else "gern mehr Zeit"
        f = forms(v, "konj2", p)
        prompt = f"{subj} ___ {c}."
        return _q("vsent", key, prompt, f, f[0], why(v, "konj2", key), display_inf(v), "konj2", full=prompt.replace("___", f[0]))
    v = _sent_verb(key)
    if v["inf"] not in COMPL or v["refl"]:
        return gen_conj(key)
    c, inf, pp = COMPL[v["inf"]], v["inf"], partizip(v)
    auxinf = "sein" if v["aux"] == "s" else "haben"
    if t == "praes":
        f = forms(v, "praes", p); prompt = f"{subj} ___ heute {c}."
    elif t == "praet":
        f = forms(v, "praet", p); prompt = f"{subj} ___ damals {c}."
    elif key == "vb:perf:aux":
        f = [aux_present(v)[p]]; prompt = f"{subj} ___ gestern {c} {pp}."
    elif t == "perf":  # a Partizip II gap
        f = [pp]; prompt = f"{subj} {aux_present(v)[p]} gestern {c} ___."
    elif t == "fut1":
        f = [WERDEN[p]]; prompt = f"{subj} ___ morgen {c} {inf}."
    elif t == "plusq":
        f = [aux_praet(v)[p]]; prompt = f"{subj} ___ schon {c} {pp}, als wir kamen."
    elif t == "konj2":
        f = [KONJ2_W[p]]; prompt = f"{subj} ___ gern {c} {inf}."
    elif t == "fut2":
        f = [WERDEN[p]]; prompt = f"{subj} ___ bis morgen {c} {pp} {auxinf}."
    else:
        return gen_conj(key)
    parts = [{"key": key}] if t != "perf" or key == "vb:perf:aux" else [{"key": key}]
    return _q("vsent", key, prompt, f, f[0], why(v, t, key), f"{display_inf(v)} · {meaning(v)}", t, parts=parts,
              full=prompt.replace("___", f[0]))


# Modal verbs in sentences: the modal in second place, the infinitive at the end.
MODAL_FRAMES = [
    ("können", "{s} ___ heute leider nicht kommen.", "can"), ("können", "{s} ___ sehr gut schwimmen.", "can"),
    ("müssen", "{s} ___ morgen früh aufstehen.", "must"), ("müssen", "{s} ___ noch die Rechnung bezahlen.", "must"),
    ("dürfen", "Hier ___ {s} nicht rauchen.", "may"), ("dürfen", "{s} ___ heute länger aufbleiben.", "may"),
    ("wollen", "{s} ___ nächstes Jahr nach Japan fliegen.", "want to"), ("wollen", "{s} ___ ein neues Auto kaufen.", "want to"),
    ("sollen", "{s} ___ mehr Wasser trinken.", "should"), ("sollen", "{s} ___ die Fenster schließen.", "should"),
    ("mögen", "{s} ___ keinen Fisch.", "like"), ("mögen", "{s} ___ Katzen sehr.", "like"),
]
MODAL_TR = {"can": "-ebilmek", "must": "zorunda olmak", "may": "izinli olmak", "want to": "istemek", "should": "-meli", "like": "sevmek"}


def gen_modsent(key):
    verb, frame, hint = random.choice(MODAL_FRAMES)
    v = _BY_INF[verb]
    p, subj = random.choice(SENT_SUBJECTS)
    inverted = frame.startswith("Hier")
    s = subj if not inverted else (subj.lower() if subj in ("Ich", "Du", "Wir", "Ihr") else subj)
    prompt = frame.replace("{s}", s)
    f = forms(v, "praes", p)
    shown_hint = MODAL_TR[hint] if lang() == "tr" else hint
    return _q("modsent", "vb:modal:sent", prompt, f, f[0],
              f"{verb} in the present: {f[0]}. The modal verb comes second; the other verb goes to the end as an infinitive.",
              f"{verb} · {shown_hint}", "modal", full=prompt.replace("___", f[0]))


GENERATORS = {"conj": gen_conj, "aux": gen_aux, "pp": gen_pp, "parts": gen_parts, "vsent": gen_vsent, "modsent": gen_modsent}

# ---------- families shown in free practice ----------
FAMILIES = [
    ("conj", "Conjugation", "Forms"), ("vsent", "In sentences", "Sentences"), ("modsent", "Modal verbs in sentences", "Sentences"),
    ("aux", "haben or sein?", "Perfekt"), ("pp", "Partizip II", "Perfekt"), ("parts", "Principal parts", "Strong verbs"),
]
FAMILY_LABEL = {f[0]: f[1] for f in FAMILIES}
FAMILY_GROUP = {f[0]: f[2] for f in FAMILIES}
_SENT_KEYS = ["vb:praes:reg", "vb:praes:stem", "vb:perf:aux", "vb:pp:weak", "vb:pp:strong", "vb:fut1", "vb:praet:weak",
              "vb:praet:strong", "vb:plusq", "vb:konj2:wuerde", "vb:konj2:irr", "vb:fut2"]
KEYS = {
    "conj": [k for t, ks in TENSE_KEYS.items() for k in ks if k not in ("vb:perf:aux", "vb:modal:sent")],
    "vsent": _SENT_KEYS, "modsent": ["vb:modal:sent"], "aux": ["vb:perf:aux"],
    "pp": ["vb:pp:weak", "vb:pp:strong", "vb:pp:noge", "vb:pp:sep"],
    "parts": [f"vp:{v['inf']}" for v in PARTS_VERBS],
}
REAL_FAMILIES = [f[0] for f in FAMILIES]


def core_keys():
    return {k for f in REAL_FAMILIES for k in KEYS[f]}


def build(mode, key):
    return GENERATORS[mode](key)


def key_label(key):
    """A skill in words, for the coach."""
    if key.startswith("vp:"):
        return f"principal parts of {key[3:]}"
    return {"vb:praes:reg": "present tense, regular verbs", "vb:praes:stem": "present tense, verbs that change their vowel",
            "vb:praes:irr": "present tense, irregular verbs", "vb:praes:sep": "present tense, separable verbs",
            "vb:perf:aux": "Perfekt with haben or sein", "vb:pp:weak": "Partizip II of weak verbs",
            "vb:pp:strong": "Partizip II of strong verbs", "vb:pp:noge": "Partizip II without ge-",
            "vb:pp:sep": "Partizip II of separable verbs", "vb:fut1": "Futur I", "vb:modal:praes": "modal verbs, present",
            "vb:modal:praet": "modal verbs, Präteritum", "vb:modal:sent": "modal verbs in sentences",
            "vb:praet:weak": "Präteritum of weak verbs", "vb:praet:strong": "Präteritum of strong verbs",
            "vb:praet:mixed": "Präteritum of mixed verbs", "vb:praet:irr": "Präteritum of sein, haben, werden",
            "vb:plusq": "Plusquamperfekt", "vb:konj2:wuerde": "Konjunktiv II with würde",
            "vb:konj2:irr": "Konjunktiv II of sein, haben and modal verbs", "vb:fut2": "Futur II"}.get(key, key)


# ---------- free practice ----------
def _allowed(family, tenses):
    keys = KEYS[family]
    return [k for k in keys if key_tense(k) is None or key_tense(k) in tenses] if tenses else keys


def next_question(focus=None, cases=None, recent=(), keys=None):
    """focus: families (empty = smart mix). cases: tenses to include. keys: drill exactly these skills."""
    st, now, recent = decl._state(), db.now(), set(recent or ())
    if keys:
        pool = [k for k in keys if k in core_keys()]
        if not pool:
            raise db.UserError("None of these mistakes can be drilled here.")
        key = random.choices(pool, [decl._weight(k, st, recent, now) for k in pool])[0]
        return build(_family_for(key), key)
    tenses = [c for c in (cases or []) if c in TENSES]
    families = [f for f in (focus or []) if f in KEYS] or REAL_FAMILIES
    families = [f for f in families if _allowed(f, tenses)] or ["conj"]
    weights = [1 + min(sum(1 for k in KEYS[f] if st.get(k, {}).get("box", 0) < decl.MASTERED_BOX), 12) for f in families]
    family = random.choices(families, weights)[0]
    pool = _allowed(family, tenses) or KEYS[family]
    key = random.choices(pool, [decl._weight(k, st, recent, now) for k in pool])[0]
    return build(family, key)


def _family_for(key):
    if key.startswith("vp:"):
        return "parts"
    if key == "vb:modal:sent":
        return "modsent"
    if key == "vb:perf:aux":
        return random.choice(["aux", "vsent"])
    return random.choice(["conj", "conj", "vsent"]) if key in _SENT_KEYS else "conj"


def topic(family):
    return f"Verbs: {FAMILY_GROUP.get(family, 'Forms').lower()}"


def log_answer(family, right):
    db.ex("INSERT INTO answers(source, topic, correct, ts, date) VALUES('verbs',?,?,?,?)",
          (topic(family), int(right), db.now(), db.today()))


def grade(q, answer, ms=None):
    """Like decl.grade: every skill the question trained is updated, then the answer is logged."""
    given = decl.norm(answer)
    right = given in {decl.norm(a) for a in q["answers"]}
    fast = bool(right and ms is not None and ms <= decl.speed_limit_ms(q))
    words = set(given.split())
    wrong = []
    for part in q["parts"]:
        ok = right or bool(part.get("tokens") and all(decl.norm(t) in words for t in part["tokens"]))
        decl.update_skill(part["key"], ok, fast, ms)
        if not ok:
            wrong.append(part["key"])
    log_answer(q["family"], right)
    return {"correct": right, "fast": fast, "wrong_parts": wrong}


# ---------- tables ----------
def _conj_table(tid, title, tense, infs, note=""):
    vs = [_BY_INF[i] for i in infs]
    rows = [{"label": PERSONS[p], "cells": [{"form": forms(v, tense, p)[0], "key": tense_key(v, tense) if tense != "perf" else pp_key(v)} for v in vs]}
            for p in range(6)]
    return {"id": tid, "title": title, "family": "conj", "cols": [display_inf(v) for v in vs], "rows": rows, "note": note, "ending": False}


PART_GROUPS = [("a-u-a", "a – u – a"), ("a-ie-a", "a – ie – a"), ("e-a-e", "e – a – e"), ("e-a-o", "e – a – o"),
               ("i-a-u", "i – a – u"), ("i-a-o", "i – a – o"), ("ei-ie-ie", "ei – ie – ie"), ("ei-i-i", "ei – i – i"),
               ("ie-o-o", "ie – o – o"), ("mixed", "Mixed verbs"), ("other", "Others to learn by heart")]


def _parts_table(pattern, title):
    vs = [v for v in PARTS_VERBS if v["pattern"] == pattern or (pattern == "other" and v["pattern"] in ("other", "irr", "a-i-a"))]
    rows = []
    for v in vs:
        k = f"vp:{v['inf']}"
        aux = "ist " if v["aux"] == "s" else "hat "
        rows.append({"label": v["inf"], "cells": [{"form": _present_simple(v)[2], "key": k}, {"form": _praet_stem(v), "key": k},
                                                  {"form": aux + partizip(v), "key": k}]})
    return {"id": f"p-{pattern}", "title": title, "family": "parts", "cols": ["er/sie/es", "Präteritum", "Perfekt"],
            "rows": rows, "note": "", "ending": False}


def tables():
    out = [
        _conj_table("t-praes", "Präsens", "praes", ["machen", "arbeiten", "fahren", "nehmen", "sein", "haben"],
                    "fahren and nehmen change their vowel only in du and er/sie/es."),
        _conj_table("t-praes-sep", "Präsens: separable and reflexive", "praes", ["anrufen", "aufstehen", "freuen", "werden", "wissen"],
                    "The prefix goes to the end; the reflexive pronoun follows the verb."),
        _conj_table("t-perf", "Perfekt", "perf", ["machen", "fahren", "gehen", "anrufen", "besuchen"],
                    "haben or sein in the present + Partizip II at the end."),
        _conj_table("t-fut1", "Futur I", "fut1", ["machen", "fahren", "anrufen"], "werden + infinitive."),
        _conj_table("t-modal", "Modal verbs: Präsens", "praes", ["können", "müssen", "dürfen", "wollen", "sollen", "mögen"],
                    "No ending in ich and er/sie/es; most change their vowel in the singular."),
        _conj_table("t-modal-praet", "Modal verbs: Präteritum", "praet", ["können", "müssen", "dürfen", "wollen", "sollen", "mögen"],
                    "-te endings, and the umlaut disappears."),
        _conj_table("t-praet", "Präteritum", "praet", ["machen", "arbeiten", "fahren", "gehen", "bringen", "sein", "haben", "werden"],
                    "Weak verbs: -te. Strong verbs: a new vowel and no ending in ich and er/sie/es."),
        _conj_table("t-plusq", "Plusquamperfekt", "plusq", ["machen", "fahren", "gehen"], "hatte or war + Partizip II."),
        _conj_table("t-konj2", "Konjunktiv II", "konj2", ["sein", "haben", "werden", "können", "machen"],
                    "sein, haben and the modal verbs use their own forms; everything else can use würde + infinitive."),
        _conj_table("t-fut2", "Futur II", "fut2", ["machen", "fahren"], "werden + Partizip II + haben or sein."),
    ]
    out += [_parts_table(p, t) for p, t in PART_GROUPS]
    return [t for t in out if t["rows"]]


def check_table(table_id, answers):
    table = next((t for t in tables() if t["id"] == table_id), None)
    if not table:
        raise db.UserError("Unknown table")
    results = {}
    for pos, text in answers.items():
        if not (text or "").strip():
            continue
        r, c = map(int, pos.split(":"))
        cell = table["rows"][r]["cells"][c]
        right = decl.norm(text) == decl.norm(cell["form"])
        results[pos] = {"correct": right, "form": cell["form"]}
        if cell["key"]:
            decl.update_skill(cell["key"], right, False)
        log_answer(table["family"], right)
    return {"results": results}


# ---------- progress ----------
def progress():
    st = decl._state()
    fams = []
    for fid, label, group in FAMILIES:
        keys = KEYS[fid]
        fams.append({"id": fid, "label": label, "group": group, "total": len(keys), "seen": sum(1 for k in keys if k in st),
                     "mastered": sum(1 for k in keys if st.get(k, {}).get("box", 0) >= decl.MASTERED_BOX),
                     "avg_box": round(sum(st.get(k, {}).get("box", 0) for k in keys) / len(keys), 2)})
    today = db.q1("SELECT COUNT(*) AS n, COALESCE(SUM(correct),0) AS c FROM answers WHERE source='verbs' AND date=?", (db.today(),))
    return {"families": fams, "boxes": {k: {"box": v["box"], "seen": v["seen"], "correct": v["correct"]} for k, v in st.items()},
            "today": {"answered": today["n"], "correct": today["c"]},
            "best_sprint": int(db.get_settings().get("verbs_best_sprint") or 0)}


def save_sprint(score):
    best = int(db.get_settings().get("verbs_best_sprint") or 0)
    if score > best:
        db.set_setting("verbs_best_sprint", score)
    return {"best": max(best, score), "new_best": score > best}


def coach_summary():
    st = decl._state()
    p = progress()
    weakest = sorted((r for r in st.values() if r["seen"] >= 2 and r["key"] in core_keys()),
                     key=lambda r: (r["box"], r["correct"] / r["seen"]))[:8]
    return {"how_to_use": "Rule-based verb drills on the Verbs page (free practice): conjugation in 8 tenses, haben or sein, "
                          "Partizip II, principal parts, sentences. Instant and free.",
            "answered_today": p["today"]["answered"],
            "skills": [{"area": f["label"], "seen": f["seen"], "mastered": f["mastered"], "total": f["total"]} for f in p["families"]],
            "weakest": [key_label(r["key"]) for r in weakest]}
