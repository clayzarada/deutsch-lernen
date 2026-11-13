"""The Verbs journey: Alexander's march from Macedon to the Indus and back to Babylon, one tense per stop.
Same steps as the Declensions planets (briefing, charts, drill, reading, flashcards, checkpoint); questions come
from the verb engine in verbs.py. Region ids match the map in static/js/alexmap.js."""
from . import verbs
from .coursekit import Course, G

TK = verbs.TENSE_KEYS
PARTS = verbs.KEYS["parts"]


def review(*tenses, w=.4):
    return [G("conj", [k for t in tenses for k in TK[t] if k not in ("vb:perf:aux", "vb:modal:sent")], w, review=True)]


# Lesson blocks as in course.py: ("p", text) ("h", heading) ("rule", text) ("tip", text) ("ex", [(german, english)])
# ("table", table id, None, column indexes or None). **bold** marks what to notice.
STAGES = [
    {
        "id": "v-praes", "region": "hellas", "planet": "Hellas", "title": "Präsens",
        "blurb": "The present. Stem plus ending, and a few verbs that change their vowel.",
        "lesson": [
            ("p", "Every German verb has an infinitive ending in -en (machen, lernen). Take off -en and you have the **stem**: "
                  "mach-, lern-. The present tense adds one ending per person."),
            ("table", "t-praes", None, [0, 1]),
            ("rule", "**ich -e · du -st · er/sie/es -t · wir -en · ihr -t · sie/Sie -en**. The wir and sie/Sie forms are "
                     "always the infinitive."),
            ("h", "Stems that need a little help"),
            ("p", "If the stem ends in -t or -d (arbeit-, find-) or in a consonant + m/n (öffn-, rechn-), add an **-e-** "
                  "before -st and -t so you can pronounce it: du arbeit**e**st, er öffn**e**t."),
            ("h", "Vowel changers"),
            ("p", "Many strong verbs change their vowel in **du** and **er/sie/es** only: **a → ä** (fahren → du fährst), "
                  "**e → i** (geben → du gibst), **e → ie** (lesen → du liest). ich, wir, ihr and sie stay regular."),
            ("table", "t-praes", None, [2, 3]),
            ("h", "Separable verbs"),
            ("p", "Verbs like an|rufen and auf|stehen split up: the verb goes in second place and the **prefix jumps to the "
                  "end**: Ich **rufe** dich morgen **an**."),
            ("h", "The irregular ones"),
            ("p", "sein, haben, werden and wissen have their own rows. Learn them first: you need them in every other tense "
                  "on this journey."),
            ("table", "t-praes", None, [4, 5]),
            ("ex", [("Ich **lerne** Deutsch.", "I'm learning German."), ("Du **fährst** zu schnell.", "You drive too fast."),
                    ("Er **liest** die Zeitung.", "He's reading the newspaper."), ("Wir **stehen** um sieben **auf**.", "We get up at seven.")]),
            ("tip", "The present also covers the future when a time word makes it clear: *Morgen fahre ich nach Athen.* "
                    "That is how Germans usually talk about plans."),
        ],
        "tables": [("t-praes", None, None)],
        "pool": lambda: [G("conj", ["vb:praes:reg"], 3), G("conj", ["vb:praes:stem"], 3), G("conj", ["vb:praes:irr"], 2),
                         G("conj", ["vb:praes:sep"], 1.5), G("vsent", ["vb:praes:reg", "vb:praes:stem"], 2)],
        "reading": ("Ein Tag in Athen",
                    "Lena {wohnt|wohnen|vb:praes:reg} seit einem Jahr in Athen. Jeden Morgen {steht|aufstehen|vb:praes:sep} sie "
                    "um sieben auf und {trinkt|trinken|vb:praes:reg} einen Kaffee auf dem Balkon. Ihr Freund Nikos "
                    "{schläft|schlafen|vb:praes:stem} meistens noch. Lena {fährt|fahren|vb:praes:stem} mit dem Bus zur Arbeit. "
                    "Sie {arbeitet|arbeiten|vb:praes:reg} in einem Museum und {spricht|sprechen|vb:praes:stem} jeden Tag Englisch, "
                    "Griechisch und Deutsch. „Du {bist|sein|vb:praes:irr} ja eine echte Europäerin!“, sagt ihre Chefin. Am Abend "
                    "{liest|lesen|vb:praes:stem} Lena ein Buch, und Nikos {kocht|kochen|vb:praes:reg}. Sie "
                    "{haben|haben|vb:praes:irr} ein schönes Leben."),
        "cards": [
            ("Präsens endings", "ich -e · du -st · er/sie/es -t · wir -en · ihr -t · sie/Sie -en", "ich mache, du machst, er macht"),
            ("When does a verb add -e- (du arbeitest)?", "When the stem ends in -t, -d, or a consonant + -m/-n.", "du arbeitest, er findet, sie öffnet"),
            ("Which persons change the vowel in fahren, geben, lesen?", "Only du and er/sie/es.", "du fährst, er gibt, sie liest"),
            ("sein in the present", "bin · bist · ist · sind · seid · sind", ""),
            ("haben in the present", "habe · hast · hat · haben · habt · haben", ""),
            ("Separable verbs in a sentence", "The prefix goes to the end.", "Ich rufe dich morgen an."),
        ],
    },
    {
        "id": "v-perf", "region": "anatolia", "planet": "Anatolien", "title": "Perfekt",
        "blurb": "The spoken past. haben or sein, and the Partizip II at the end.",
        "lesson": [
            ("p", "The Perfekt is how Germans talk about the past in everyday speech. It has two parts: **haben or sein** in "
                  "the present, and the **Partizip II** at the very end of the sentence."),
            ("ex", [("Ich **habe** Pizza **gegessen**.", "I ate pizza."), ("Wir **sind** nach Ankara **gefahren**.", "We drove to Ankara."),
                    ("**Hast** du das Buch **gelesen**?", "Did you read the book?")]),
            ("h", "haben or sein?"),
            ("p", "Most verbs take **haben**. Verbs of **movement from A to B** (gehen, fahren, fliegen, kommen) and **change "
                  "of state** (aufwachen, einschlafen, sterben, werden) take **sein**, and so do sein, bleiben and passieren."),
            ("rule", "Ask: does the subject move somewhere, or turn into something else? Yes: sein. No: haben."),
            ("h", "Building the Partizip II"),
            ("p", "**Weak verbs:** ge- + stem + -t: machen → **ge**mach**t**, arbeiten → **ge**arbeit**et**."),
            ("p", "**Strong verbs:** ge- + often a new vowel + -en: finden → **ge**fund**en**, schreiben → **ge**schrieb**en**. "
                  "These you learn by heart."),
            ("p", "**No ge-** for verbs ending in -ieren (studiert) or starting with be-, ver-, er-, ent-, emp-, ge-, zer-: "
                  "besucht, verstanden."),
            ("p", "**Separable verbs** put ge- in the middle: an**ge**rufen, auf**ge**standen."),
            ("table", "t-perf", None, None),
            ("tip", "The Partizip II always goes last. Everything else sits between the two parts: Ich **habe** gestern mit "
                    "meiner Schwester lange **telefoniert**."),
        ],
        "tables": [("t-perf", None, None)],
        "pool": lambda: [G("aux", ["vb:perf:aux"], 3), G("pp", ["vb:pp:weak"], 2), G("pp", ["vb:pp:strong"], 3),
                         G("pp", ["vb:pp:noge"], 2), G("pp", ["vb:pp:sep"], 1.5),
                         G("conj", ["vb:pp:weak", "vb:pp:strong", "vb:pp:noge", "vb:pp:sep"], 2),
                         G("vsent", ["vb:perf:aux", "vb:pp:weak", "vb:pp:strong"], 2)] + review("praes"),
        "reading": ("Eine Reise durch Anatolien",
                    "Letzten Sommer {sind|sein|vb:perf:aux} wir durch Anatolien gereist. Zuerst {haben|haben|vb:perf:aux} wir "
                    "Istanbul {besucht|besuchen|vb:pp:noge}. Dann sind wir mit dem Bus nach Kappadokien "
                    "{gefahren|fahren|vb:pp:strong}. Dort {haben|haben|vb:perf:aux} wir in einem Höhlenhotel "
                    "{übernachtet|übernachten|vb:pp:noge}. Am Morgen sind wir sehr früh {aufgestanden|aufstehen|vb:pp:sep}, "
                    "denn wir wollten die Ballons sehen. Mein Bruder hat hundert Fotos {gemacht|machen|vb:pp:weak}. Am Abend "
                    "haben wir Kebab {gegessen|essen|vb:pp:strong} und Ayran {getrunken|trinken|vb:pp:strong}. Leider "
                    "{hat|haben|vb:perf:aux} es am letzten Tag {geregnet|regnen|vb:pp:weak}."),
        "cards": [
            ("Perfekt: how is it built?", "haben or sein (present) + Partizip II at the end", "Ich habe gearbeitet. Wir sind gefahren."),
            ("Which verbs take sein in the Perfekt?", "Movement from A to B, change of state, and sein, bleiben, passieren.", "Ich bin gegangen. Er ist eingeschlafen."),
            ("Partizip II of weak verbs", "ge- + stem + -t", "gemacht, gearbeitet"),
            ("Partizip II without ge-", "Verbs in -ieren and with be-, ver-, er-, ent-, emp-, ge-, zer-", "studiert, besucht, verstanden"),
            ("Partizip II of separable verbs", "ge- between the prefix and the verb", "angerufen, aufgestanden"),
            ("gehen, kommen, fahren in the Perfekt", "ist gegangen · ist gekommen · ist gefahren", ""),
        ],
    },
    {
        "id": "v-fut1", "region": "phoenicia", "planet": "Phönizien", "title": "Futur I",
        "blurb": "The future. werden plus the infinitive, for predictions and promises.",
        "lesson": [
            ("p", "The Futur I is **werden** in the present + the **infinitive** at the end: Ich **werde** morgen **arbeiten**."),
            ("table", "t-fut1", None, None),
            ("rule", "werden: werde · wirst · wird · werden · werdet · werden. Careful: du **wirst** and er **wird** are irregular."),
            ("h", "When do Germans use it?"),
            ("p", "Less often than you might think. For plans with a time word, the present is normal: *Morgen fahre ich nach "
                  "Tyros.* Use the Futur I for **predictions**, **promises** and things that are **not certain**:"),
            ("ex", [("Es **wird** morgen **regnen**.", "It will rain tomorrow."), ("Ich **werde** dir **helfen**, versprochen!", "I'll help you, I promise!"),
                    ("Er **wird** wohl krank **sein**.", "He's probably ill.")]),
            ("tip", "With *wohl* or *sicher* the Futur I makes a guess about the present: *Sie wird wohl im Büro sein* "
                    "(she's probably at the office)."),
        ],
        "tables": [("t-fut1", None, None)],
        "pool": lambda: [G("conj", ["vb:fut1"], 3), G("vsent", ["vb:fut1"], 2)] + review("praes", "perf", w=.5),
        "reading": ("Morgen in Tyros",
                    "Morgen {wird|werden|vb:fut1} unser Schiff in Tyros ankommen. Der Kapitän sagt: „Es {wird|werden|vb:fut1} "
                    "ein schöner Tag.“ Ich {werde|werden|vb:fut1} zuerst den Hafen besuchen. Meine Freunde "
                    "{werden|werden|vb:fut1} lieber am Strand liegen. „{Wirst|werden|vb:fut1} du mit uns essen?“, fragt Mira. "
                    "„Ja, ich {werde|werden|vb:fut1} um acht da sein“, antworte ich. Ihr {werdet|werden|vb:fut1} sehen: Die "
                    "Stadt {wird|werden|vb:fut1} euch gefallen."),
        "cards": [
            ("Futur I: how is it built?", "werden (present) + infinitive at the end", "Ich werde dich anrufen."),
            ("werden in the present", "werde · wirst · wird · werden · werdet · werden", ""),
            ("Plans with a time word: Futur I or present?", "Usually the present.", "Morgen fahre ich nach Hause."),
            ("What else does the Futur I express?", "Predictions, promises, and guesses with wohl", "Er wird wohl krank sein."),
        ],
    },
    {
        "id": "v-modal", "region": "egypt", "planet": "Ägypten", "title": "Modalverben",
        "blurb": "können, müssen, dürfen, wollen, sollen, mögen, and the infinitive at the end.",
        "lesson": [
            ("p", "Six **modal verbs** say how you relate to an action: **können** (can), **müssen** (must), **dürfen** (may), "
                  "**wollen** (want to), **sollen** (should) and **mögen** (like). The other verb goes to the end as an **infinitive**."),
            ("ex", [("Ich **kann** gut **schwimmen**.", "I can swim well."), ("Du **musst** morgen früh **aufstehen**.", "You have to get up early tomorrow."),
                    ("Hier **darf** man nicht **rauchen**.", "You're not allowed to smoke here."), ("Wir **wollen** die Pyramiden **sehen**.", "We want to see the pyramids.")]),
            ("table", "t-modal", None, None),
            ("rule", "In the singular they are irregular: **no ending in ich and er/sie/es** (ich kann, er kann), and most change "
                     "their vowel (können → kann, müssen → muss, dürfen → darf, wollen → will, mögen → mag)."),
            ("h", "möchte"),
            ("p", "*Ich möchte* (I would like) is the polite everyday form. It conjugates like a Präteritum: ich möchte, du "
                  "möchtest, er möchte."),
            ("h", "In the past"),
            ("p", "In the past, modal verbs normally use the **Präteritum**, not the Perfekt: *Ich **konnte** nicht kommen.* The "
                  "endings are -te, and the umlaut disappears: können → konnte, müssen → musste, dürfen → durfte, mögen → mochte."),
            ("table", "t-modal-praet", None, None),
            ("tip", "*müssen nicht* means *don't have to*, not *must not*. For *must not*, use *nicht dürfen*: *Du darfst hier "
                    "nicht parken.*"),
        ],
        "tables": [("t-modal", None, None), ("t-modal-praet", None, None)],
        "pool": lambda: [G("conj", ["vb:modal:praes"], 3), G("modsent", ["vb:modal:sent"], 3), G("conj", ["vb:modal:praet"], 1.5)]
        + review("praes", "perf", w=.3),
        "reading": ("Ein Tag in Alexandria",
                    "In Alexandria {will|wollen|vb:modal:praes} Sara unbedingt die Bibliothek sehen. „Wir "
                    "{müssen|müssen|vb:modal:praes} früh losgehen“, sagt sie, „denn heute {darf|dürfen|vb:modal:praes} man nur "
                    "bis fünf hinein.“ Ihr Bruder Tim {kann|können|vb:modal:praes} nicht so früh aufstehen. "
                    "„{Kannst|können|vb:modal:praes} du nicht allein gehen?“, fragt er. „Du {sollst|sollen|vb:modal:praes} "
                    "mitkommen, das hat Mama gesagt!“ Am Ende geht Tim mit. Später sagt er: „Ich {mag|mögen|vb:modal:praes} "
                    "Bücher eigentlich nicht, aber das {musste|müssen|vb:modal:praet} ich sehen. Gestern "
                    "{wollte|wollen|vb:modal:praet} ich nur schlafen.“"),
        "cards": [
            ("The six modal verbs", "können · müssen · dürfen · wollen · sollen · mögen", "can · must · may · want to · should · like"),
            ("Modal verbs: ich and er/sie/es", "No ending: ich kann, er kann", "ich muss, sie darf, er will"),
            ("Where does the second verb go?", "To the end, as an infinitive", "Ich kann heute nicht kommen."),
            ("müssen nicht vs. nicht dürfen", "don't have to vs. must not", "Du musst nicht kommen. Du darfst nicht rauchen."),
            ("Modal verbs in the past", "Präteritum: -te and no umlaut", "konnte, musste, durfte, wollte, sollte, mochte"),
        ],
    },
    {
        "id": "v-praet", "region": "syria", "planet": "Syrien", "title": "Präteritum",
        "blurb": "The past of stories. -te for weak verbs, a new vowel for strong ones.",
        "lesson": [
            ("p", "The Präteritum is the past of **stories, books and news**. In speech most verbs use the Perfekt, but a few "
                  "common ones prefer the Präteritum even in conversation: **sein (war), haben (hatte), werden (wurde)**, the "
                  "modal verbs, and *es gab* (there was)."),
            ("h", "Weak verbs: -te"),
            ("p", "Stem + **-te** + ending: ich mach**te**, du mach**test**, er mach**te**, wir mach**ten**, ihr mach**tet**, sie "
                  "mach**ten**. After -t or -d: arbeit**ete**."),
            ("h", "Strong verbs: a new vowel"),
            ("p", "Strong verbs change their vowel and take **no ending in ich and er/sie/es**: ich **fuhr**, er **fuhr**, wir "
                  "**fuhren**. Learn each one with its principal parts: **fahren – fuhr – gefahren**."),
            ("table", "t-praet", None, None),
            ("h", "Mixed verbs"),
            ("p", "A few verbs do both, a new vowel **and** -te: bringen → **brachte**, denken → **dachte**, kennen → "
                  "**kannte**, wissen → **wusste**."),
            ("tip", "Most strong verbs follow a handful of vowel patterns (ei – ie – ie: bleiben, blieb, geblieben; i – a – u: "
                    "finden, fand, gefunden). The tables in free practice group them by pattern."),
        ],
        "tables": [("t-praet", None, None)],
        "pool": lambda: [G("conj", ["vb:praet:weak"], 2), G("conj", ["vb:praet:strong"], 3), G("conj", ["vb:praet:mixed"], 1.5),
                         G("conj", ["vb:praet:irr"], 2), G("parts", PARTS, 2), G("vsent", ["vb:praet:weak", "vb:praet:strong"], 1.5)]
        + review("praes", "perf", w=.3),
        "reading": ("Der Teppich aus Bagdad",
                    "Vor vielen Jahren {war|sein|vb:praet:irr} mein Großvater Händler in Aleppo. Jeden Morgen "
                    "{ging|gehen|vb:praet:strong} er auf den Markt und {verkaufte|verkaufen|vb:praet:weak} Seife und Gewürze. Er "
                    "{hatte|haben|vb:praet:irr} viele Kunden und {kannte|kennen|vb:praet:mixed} alle beim Namen. Einmal "
                    "{kam|kommen|vb:praet:strong} ein Mann aus Bagdad. Er {brachte|bringen|vb:praet:mixed} einen Teppich mit und "
                    "{wollte|wollen|vb:modal:praet} ihn tauschen. Mein Großvater {lachte|lachen|vb:praet:weak} und "
                    "{sagte|sagen|vb:praet:weak}: „Ein Teppich für zehn Kilo Seife? Einverstanden!“ Der Teppich "
                    "{liegt|liegen|vb:praes:reg} heute noch in unserem Wohnzimmer."),
        "cards": [
            ("Präteritum of weak verbs", "stem + -te: ich machte, du machtest, wir machten", ""),
            ("Präteritum of strong verbs: ich and er/sie/es", "No ending: ich fuhr, er fuhr", ""),
            ("Which verbs use the Präteritum even in speech?", "sein, haben, werden, the modal verbs, es gab", "Ich war müde. Wir hatten keine Zeit."),
            ("Mixed verbs", "A new vowel and -te", "bringen → brachte, denken → dachte, wissen → wusste"),
            ("Principal parts of gehen", "gehen – ging – ist gegangen", ""),
            ("Principal parts of finden", "finden – fand – hat gefunden", ""),
        ],
    },
    {
        "id": "v-plusq", "region": "persia", "planet": "Persien", "title": "Plusquamperfekt",
        "blurb": "The past before the past. hatte or war plus the Partizip II.",
        "lesson": [
            ("p", "The Plusquamperfekt is the **past before the past**: something that had already happened before another past "
                  "event. It's built like the Perfekt, but with haben or sein in the **Präteritum**: hatte or war + Partizip II."),
            ("ex", [("Als wir ankamen, **hatte** der Film schon **begonnen**.", "When we arrived, the film had already started."),
                    ("Sie **war** schon **gegangen**.", "She had already left."),
                    ("Nachdem ich **gegessen hatte**, ging ich spazieren.", "After I had eaten, I went for a walk.")]),
            ("table", "t-plusq", None, None),
            ("rule", "haben or sein? Exactly as in the Perfekt: a verb with sein in the Perfekt (ist gefahren) takes war here "
                     "(war gefahren)."),
            ("tip", "*nachdem* (after) almost always brings the Plusquamperfekt with it: *Nachdem er angerufen hatte, ...*"),
        ],
        "tables": [("t-plusq", None, None)],
        "pool": lambda: [G("conj", ["vb:plusq"], 3), G("vsent", ["vb:plusq"], 2), G("aux", ["vb:perf:aux"], 1), G("parts", PARTS, .8)]
        + review("perf", "praet", w=.4),
        "reading": ("Zu spät in Persepolis",
                    "Als wir in Persepolis ankamen, {hatte|haben|vb:plusq} die Sonne schon den ganzen Tag "
                    "{geschienen|scheinen|vb:pp:strong}. Unser Führer {war|sein|vb:plusq} schon nach Hause "
                    "{gegangen|gehen|vb:pp:strong}, weil wir zu spät waren. Zum Glück {hatte|haben|vb:plusq} meine Schwester "
                    "vorher ein Buch über die Stadt {gekauft|kaufen|vb:pp:weak}. Sie {hatte|haben|vb:plusq} es im Zug "
                    "{gelesen|lesen|vb:pp:strong} und erklärte uns alles. Nachdem wir alles {gesehen|sehen|vb:pp:strong} hatten, "
                    "aßen wir in einem kleinen Restaurant."),
        "cards": [
            ("Plusquamperfekt: how is it built?", "hatte or war + Partizip II", "Ich hatte gegessen. Er war gefahren."),
            ("When do you use the Plusquamperfekt?", "For something that happened before another past event", "Als wir ankamen, hatte der Film schon begonnen."),
            ("Which word often brings the Plusquamperfekt?", "nachdem (after)", "Nachdem ich gegessen hatte, ging ich spazieren."),
        ],
    },
    {
        "id": "v-konj2", "region": "bactria", "planet": "Baktrien", "title": "Konjunktiv II",
        "blurb": "Wishes, polite requests and what isn't real: würde, wäre, hätte, könnte.",
        "lesson": [
            ("p", "The Konjunktiv II is for **wishes, polite requests and things that aren't real**. For most verbs it's simply "
                  "**würde + infinitive**: *Ich **würde** gern nach Samarkand **reisen**.*"),
            ("table", "t-konj2", None, None),
            ("h", "The verbs with their own forms"),
            ("p", "sein, haben and the modal verbs don't use würde. They have their own forms, and these are the ones you hear "
                  "all the time: **wäre, hätte, könnte, müsste, dürfte, sollte, wollte, möchte**."),
            ("ex", [("Wenn ich Zeit **hätte**, **würde** ich mehr lesen.", "If I had time, I would read more."),
                    ("**Könnten** Sie mir helfen?", "Could you help me?"), ("Das **wäre** schön!", "That would be nice!"),
                    ("Du **solltest** mehr schlafen.", "You should sleep more.")]),
            ("h", "A few strong verbs"),
            ("p", "Some strong verbs have their own Konjunktiv II too (käme, ginge, gäbe, wüsste). *Wenn es mehr Zeit gäbe ...* "
                  "sounds elegant, but würde + infinitive is always correct for them."),
            ("tip", "Polite requests: *Könnten Sie ...?* and *Würden Sie ...?* are the standard in shops, offices and emails."),
        ],
        "tables": [("t-konj2", None, None)],
        "pool": lambda: [G("conj", ["vb:konj2:wuerde"], 2), G("conj", ["vb:konj2:irr"], 3),
                         G("vsent", ["vb:konj2:wuerde", "vb:konj2:irr"], 2)] + review("praes", "praet", w=.4),
        "reading": ("Wenn ich in Samarkand wäre",
                    "Wenn ich mehr Zeit {hätte|haben|vb:konj2:irr}, {würde|werden|vb:konj2:wuerde} ich durch ganz Zentralasien "
                    "reisen. Ich {würde|werden|vb:konj2:wuerde} zuerst nach Samarkand fahren. Das {wäre|sein|vb:konj2:irr} "
                    "wunderbar! Meine Freundin sagt: „Du {solltest|sollen|vb:konj2:irr} nicht nur träumen. "
                    "{Könntest|können|vb:konj2:irr} du nicht im Sommer fahren?“ Sie hat recht. Ich "
                    "{müsste|müssen|vb:konj2:irr} nur ein bisschen sparen. Und vielleicht {würdest|werden|vb:konj2:wuerde} du "
                    "ja mitkommen?"),
        "cards": [
            ("Konjunktiv II for most verbs", "würde + infinitive", "Ich würde gern reisen."),
            ("Konjunktiv II of sein and haben", "wäre · hätte", "Das wäre schön. Ich hätte gern einen Kaffee."),
            ("Konjunktiv II of the modal verbs", "könnte · müsste · dürfte · sollte · wollte · möchte", ""),
            ("A polite request", "Könnten Sie ...? / Würden Sie ...?", "Könnten Sie mir bitte helfen?"),
            ("Wenn ich Zeit hätte, ...", "... würde ich mehr lesen.", "If I had time, I would read more."),
        ],
    },
    {
        "id": "v-fut2", "region": "indus", "planet": "Indus", "title": "Futur II",
        "blurb": "What will have happened: werden plus Partizip II plus haben or sein.",
        "lesson": [
            ("p", "The Futur II looks ahead to something that **will have happened** by a certain time: *Bis Freitag **werde** "
                  "ich das Buch **gelesen haben**.* It's werden + Partizip II + haben or sein."),
            ("table", "t-fut2", None, None),
            ("p", "It's the rarest tense on this journey. In speech, the Perfekt usually does the job: *Bis Freitag habe ich das "
                  "Buch gelesen.*"),
            ("h", "Guessing about the past"),
            ("p", "Its most common use is a guess with *wohl*: *Er **wird** den Bus **verpasst haben*** (he's probably missed "
                  "the bus)."),
            ("rule", "haben or sein at the end follows the Perfekt: ich habe gegessen → ich werde gegessen **haben**; ich bin "
                     "gefahren → ich werde gefahren **sein**."),
        ],
        "tables": [("t-fut2", None, None)],
        "pool": lambda: [G("conj", ["vb:fut2"], 3), G("vsent", ["vb:fut2"], 2), G("aux", ["vb:perf:aux"], 1)] + review("perf", "fut1", w=.5),
        "reading": ("Am Indus",
                    "In einer Woche {werden|werden|vb:fut2} wir den Indus {gesehen|sehen|vb:pp:strong} haben. Bis dahin "
                    "{wird|werden|vb:fut2} mein Bruder bestimmt hundert Fotos {gemacht|machen|vb:pp:weak} haben. Und unsere "
                    "Mutter? Sie {wird|werden|vb:fut2} sich wohl Sorgen {gemacht|machen|vb:pp:weak} haben, denn wir haben seit "
                    "Tagen nicht angerufen. „Keine Sorge“, sagt mein Bruder, „bis Sonntag {werden|werden|vb:fut2} wir längst "
                    "wieder zu Hause {angekommen|ankommen|vb:pp:sep} sein.“"),
        "cards": [
            ("Futur II: how is it built?", "werden + Partizip II + haben/sein", "Ich werde gegessen haben. Er wird gefahren sein."),
            ("Futur II with wohl", "A guess about the past", "Er wird den Bus verpasst haben."),
            ("Futur II: haben or sein at the end?", "The same as in the Perfekt", "gegessen haben · gefahren sein"),
        ],
    },
    {
        "id": "v-all", "region": "babylon", "planet": "Babylon", "title": "Alle Zeiten", "home": True,
        "blurb": "The final stop. Every tense, mixed, until it's automatic.",
        "lesson": [
            ("p", "You have marched through every tense. Babylon mixes them all, the way real German does. For every verb, run "
                  "the same three questions:"),
            ("rule", "**1. When?** Look for the time word (gestern, morgen, damals, schon, gern). **2. Which tense?** Spoken past: "
                     "Perfekt. Stories: Präteritum. Before the past: Plusquamperfekt. Wishes: Konjunktiv II. **3. Which form?** "
                     "Strong or weak, haben or sein, separable or not."),
            ("ex", [("Ich **fahre**.", "Präsens"), ("Ich **bin gefahren**.", "Perfekt"), ("Ich **werde fahren**.", "Futur I"),
                    ("Ich **fuhr**.", "Präteritum"), ("Ich **war gefahren**.", "Plusquamperfekt"), ("Ich **würde fahren**.", "Konjunktiv II"),
                    ("Ich **werde gefahren sein**.", "Futur II")]),
            ("p", "From here it's about speed. Come back for the daily mix until the forms come out without thinking. Babylon "
                  "never closes."),
        ],
        "tables": [],
        "pool": lambda: [G("conj", [k for t in ("praes", "praet", "konj2", "fut1", "plusq", "fut2") for k in TK[t]], 3),
                         G("conj", ["vb:pp:weak", "vb:pp:strong", "vb:pp:noge", "vb:pp:sep"], 2), G("vsent", verbs._SENT_KEYS, 3),
                         G("modsent", ["vb:modal:sent"], 1), G("aux", ["vb:perf:aux"], 1), G("parts", PARTS, 1.5)],
        "reading": ("Zurück in Babylon",
                    "Gestern {sind|sein|vb:perf:aux} wir endlich in Babylon angekommen. Die Reise {war|sein|vb:praet:irr} lang, "
                    "aber wir {haben|haben|vb:perf:aux} viel gesehen. Heute {schlafen|schlafen|vb:praes:stem} alle lange. "
                    "Morgen {werden|werden|vb:fut1} wir den Palast besuchen. Wenn ich noch Kraft {hätte|haben|vb:konj2:irr}, "
                    "{würde|werden|vb:konj2:wuerde} ich sofort weiterreisen. Aber zuerst {muss|müssen|vb:modal:praes} ich "
                    "meiner Mutter schreiben: Sie {hatte|haben|vb:plusq} mich vor der Reise gewarnt, und sie hatte recht!"),
        "cards": [
            ("fahren in all seven tenses (ich)", "fahre · bin gefahren · werde fahren · fuhr · war gefahren · würde fahren · werde gefahren sein", ""),
            ("Spoken past or written past?", "Perfekt in speech; Präteritum in stories, and for sein, haben and the modal verbs", ""),
            ("Three questions for every verb", "When? Which tense? Which form?", ""),
        ],
    },
]

STEP_INFO = {
    "reading": ("Reading", "Fill in the verbs in a short text."),
    "checkpoint": ("Checkpoint", "Pass this to unlock the next region."),
}

VERBS_COURSE = Course(
    STAGES, verbs, counts=lambda k: not k.startswith("vp:"), card_tag="verbs", step_info=STEP_INFO,
    what="A guided course on the Verbs page, following Alexander's march: Präsens, Perfekt, Futur I, modal verbs, "
         "Präteritum, Plusquamperfekt, Konjunktiv II, Futur II, then a final mixed stop. Each has a briefing, charts, "
         "a drill, a reading, flashcards and a checkpoint.")
