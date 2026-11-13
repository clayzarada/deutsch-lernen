"""Turkish for the Verbs course and the verb drills (merged into app/i18n.py). Same rules: exact strings, and
templates where "{}" matches anything and is translated again."""

EXACT = {
    # ----- labels and groups -----
    "Conjugation": "Çekim", "Modal verbs in sentences": "Cümle içinde modal fiiller", "haben or sein?": "haben mı sein mi?",
    "Principal parts": "Temel biçimler", "Forms": "Biçimler", "Sentences": "Cümleler", "Strong verbs": "Güçlü fiiller",
    "Präsens: separable and reflexive": "Präsens: ayrılabilen ve dönüşlü", "Modal verbs: Präsens": "Modal fiiller: Präsens",
    "Modal verbs: Präteritum": "Modal fiiller: Präteritum", "Mixed verbs": "Karışık fiiller",
    "Others to learn by heart": "Ezberlenecek diğerleri",
    "fahren and nehmen change their vowel only in du and er/sie/es.": "fahren ve nehmen ünlülerini yalnızca du ve er/sie/es'te değiştirir.",
    "The prefix goes to the end; the reflexive pronoun follows the verb.": "Ön ek sona gider; dönüşlü zamir fiilden sonra gelir.",
    "haben or sein in the present + Partizip II at the end.": "Şimdiki zamanda haben veya sein + sonda Partizip II.",
    "werden + infinitive.": "werden + mastar.",
    "No ending in ich and er/sie/es; most change their vowel in the singular.": "ich ve er/sie/es'te ek yok; çoğu tekilde ünlüsünü değiştirir.",
    "-te endings, and the umlaut disappears.": "-te ekleri; umlaut kaybolur.",
    "Weak verbs: -te. Strong verbs: a new vowel and no ending in ich and er/sie/es.": "Zayıf fiiller: -te. Güçlü fiiller: yeni bir ünlü ve ich ile er/sie/es'te ek yok.",
    "hatte or war + Partizip II.": "hatte veya war + Partizip II.",
    "sein, haben and the modal verbs use their own forms; everything else can use würde + infinitive.":
        "sein, haben ve modal fiiller kendi biçimlerini kullanır; diğer her şey würde + mastar kullanabilir.",
    "werden + Partizip II + haben or sein.": "werden + Partizip II + haben veya sein.",

    # ----- word order -----
    "Verb second": "Fiil ikinci sırada", "Something else first": "Başta başka bir öğe", "Verb bracket": "Fiil parantezi",
    "Verb last": "Fiil sonda", "Questions": "Sorular",
    "In a statement the conjugated verb is always the second element. Details follow the order: time, manner, place.":
        "Düz cümlede çekimli fiil her zaman ikinci öğedir. Ayrıntılar şu sırayı izler: zaman, tarz, yer.",
    "When something other than the subject comes first, the verb stays in second place and the subject moves right behind it.":
        "Başta özneden başka bir öğe varsa fiil ikinci sırada kalır ve özne hemen onun arkasına geçer.",
    "With a helper verb (haben, sein, werden or a modal verb), the helper is second and the infinitive or Partizip II goes to the very end.":
        "Yardımcı fiil varsa (haben, sein, werden veya bir modal fiil), yardımcı fiil ikinci sıradadır; mastar veya Partizip II en sona gider.",
    "The verb is second; its prefix goes to the very end of the sentence.": "Fiil ikinci sıradadır; ön eki cümlenin en sonuna gider.",
    "After weil, dass, wenn, ob or a question word in the middle of a sentence, the conjugated verb goes to the end.":
        "weil, dass, wenn, ob veya cümle ortasındaki bir soru kelimesinden sonra çekimli fiil sona gider; Türkçedeki gibi.",
    "W-questions start with the question word, then the verb. Yes/no questions start with the verb.":
        "W-soruları soru kelimesiyle, sonra fiille başlar. Evet/hayır soruları fiille başlar.",

    # ----- steps -----
    "Fill in the verbs in a short text.": "Kısa bir metinde fiilleri doldurun.",
    "Pass this to unlock the next region.": "Sonraki bölgeyi açmak için bunu geçin.",

    # ----- drill explanations (fixed sentences) -----
    "Modal verbs have no ending in ich and er/sie/es: ich kann, er kann.": "Modal fiiller ich ve er/sie/es'te ek almaz: ich kann, er kann.",
    "Präsens: stem + -e, -st, -t, -en, -t, -en.": "Präsens: gövde + -e, -st, -t, -en, -t, -en.",
    "Stems ending in -t, -d or a consonant + -m/-n add an -e- before -st and -t: du arbeitest, er öffnet.":
        "-t, -d veya ünsüz + -m/-n ile biten gövdeler -st ve -t'den önce bir -e- alır: du arbeitest, er öffnet.",
    "Weak verbs add -te: -te, -test, -te, -ten, -tet, -ten.": "Zayıf fiiller -te alır: -te, -test, -te, -ten, -tet, -ten.",
    "ich and er/sie/es have no ending.": "ich ve er/sie/es ek almaz.",
    "Perfekt: haben or sein in the present + Partizip II.": "Perfekt: şimdiki zamanda haben veya sein + Partizip II.",
    "Plusquamperfekt: haben or sein in the Präteritum + Partizip II.": "Plusquamperfekt: Präteritum'da haben veya sein + Partizip II.",
    "Futur II: werden + Partizip II + haben or sein.": "Futur II: werden + Partizip II + haben veya sein.",
    "Futur I: werden in the present + the infinitive at the end.": "Futur I: şimdiki zamanda werden + sonda mastar.",
    "Konjunktiv II: würde + infinitive works for almost every verb.": "Konjunktiv II: würde + mastar neredeyse her fiil için işe yarar.",
    "Reflexive verbs keep their pronoun: mich, dich, sich, uns, euch, sich.": "Dönüşlü fiiller zamirlerini korur: mich, dich, sich, uns, euch, sich.",
    "The modal verb comes second; the other verb goes to the end as an infinitive.": "Modal fiil ikinci sıradadır; diğer fiil sona mastar olarak gider.",
    "Learn strong verbs as a set of three.": "Güçlü fiilleri üçlü bir set olarak öğrenin.",

    # ----- Hellas: Präsens -----
    "The present. Stem plus ending, and a few verbs that change their vowel.": "Şimdiki zaman. Gövde artı ek, bir de ünlüsünü değiştiren birkaç fiil.",
    "Every German verb has an infinitive ending in -en (machen, lernen). Take off -en and you have the **stem**: mach-, lern-. The present tense adds one ending per person.":
        "Her Almanca fiilin -en ile biten bir mastarı vardır (machen, lernen). -en'i atın, **gövde** kalır: mach-, lern-. Şimdiki zaman her şahsa bir ek ekler; Türkçedeki şahıs eklerine (-ım, -sın, -ız) benzer.",
    "**ich -e · du -st · er/sie/es -t · wir -en · ihr -t · sie/Sie -en**. The wir and sie/Sie forms are always the infinitive.":
        "**ich -e · du -st · er/sie/es -t · wir -en · ihr -t · sie/Sie -en**. wir ve sie/Sie biçimleri her zaman mastarla aynıdır.",
    "Stems that need a little help": "Biraz yardıma ihtiyaç duyan gövdeler",
    "If the stem ends in -t or -d (arbeit-, find-) or in a consonant + m/n (öffn-, rechn-), add an **-e-** before -st and -t so you can pronounce it: du arbeit**e**st, er öffn**e**t.":
        "Gövde -t veya -d ile (arbeit-, find-) ya da ünsüz + m/n ile (öffn-, rechn-) bitiyorsa, telaffuz edebilmek için -st ve -t'den önce bir **-e-** ekleyin: du arbeit**e**st, er öffn**e**t.",
    "Vowel changers": "Ünlüsünü değiştirenler",
    "Many strong verbs change their vowel in **du** and **er/sie/es** only: **a → ä** (fahren → du fährst), **e → i** (geben → du gibst), **e → ie** (lesen → du liest). ich, wir, ihr and sie stay regular.":
        "Birçok güçlü fiil ünlüsünü yalnızca **du** ve **er/sie/es**'te değiştirir: **a → ä** (fahren → du fährst), **e → i** (geben → du gibst), **e → ie** (lesen → du liest). ich, wir, ihr ve sie düzenli kalır.",
    "Separable verbs": "Ayrılabilen fiiller",
    "Verbs like an|rufen and auf|stehen split up: the verb goes in second place and the **prefix jumps to the end**: Ich **rufe** dich morgen **an**.":
        "an|rufen ve auf|stehen gibi fiiller ayrılır: fiil ikinci sıraya gider, **ön ek sona atlar**: Ich **rufe** dich morgen **an**.",
    "The irregular ones": "Düzensiz olanlar",
    "sein, haben, werden and wissen have their own rows. Learn them first: you need them in every other tense on this journey.":
        "sein, haben, werden ve wissen'in kendi satırları vardır. Önce bunları öğrenin: bu yolculuktaki diğer bütün zamanlarda onlara ihtiyacınız olacak.",
    "I'm learning German.": "Almanca öğreniyorum.", "You drive too fast.": "Çok hızlı sürüyorsun.",
    "He's reading the newspaper.": "Gazete okuyor.", "We get up at seven.": "Saat yedide kalkıyoruz.",
    "The present also covers the future when a time word makes it clear: *Morgen fahre ich nach Athen.* That is how Germans usually talk about plans.":
        "Bir zaman kelimesi açıkça belirttiğinde şimdiki zaman geleceği de karşılar: *Morgen fahre ich nach Athen.* Almanlar planlarından genellikle böyle bahseder; Türkçedeki \"yarın Atina'ya gidiyorum\" gibi.",
    "Präsens endings": "Präsens ekleri",
    "When does a verb add -e- (du arbeitest)?": "Bir fiil ne zaman -e- alır (du arbeitest)?",
    "When the stem ends in -t, -d, or a consonant + -m/-n.": "Gövde -t, -d veya ünsüz + -m/-n ile bittiğinde.",
    "Which persons change the vowel in fahren, geben, lesen?": "fahren, geben, lesen'de hangi şahıslar ünlüyü değiştirir?",
    "Only du and er/sie/es.": "Yalnızca du ve er/sie/es.",
    "sein in the present": "Şimdiki zamanda sein", "haben in the present": "Şimdiki zamanda haben",
    "Separable verbs in a sentence": "Cümlede ayrılabilen fiiller", "The prefix goes to the end.": "Ön ek sona gider.",

    # ----- Anatolien: Perfekt -----
    "The spoken past. haben or sein, and the Partizip II at the end.": "Konuşmadaki geçmiş zaman. haben veya sein, ve sonda Partizip II.",
    "The Perfekt is how Germans talk about the past in everyday speech. It has two parts: **haben or sein** in the present, and the **Partizip II** at the very end of the sentence.":
        "Perfekt, Almanların günlük konuşmada geçmişten bahsetme şeklidir. İki parçası vardır: şimdiki zamanda **haben veya sein** ve cümlenin en sonunda **Partizip II**.",
    "I ate pizza.": "Pizza yedim.", "We drove to Ankara.": "Ankara'ya (arabayla) gittik.", "Did you read the book?": "Kitabı okudun mu?",
    "Most verbs take **haben**. Verbs of **movement from A to B** (gehen, fahren, fliegen, kommen) and **change of state** (aufwachen, einschlafen, sterben, werden) take **sein**, and so do sein, bleiben and passieren.":
        "Çoğu fiil **haben** alır. **A'dan B'ye hareket** (gehen, fahren, fliegen, kommen) ve **durum değişikliği** (aufwachen, einschlafen, sterben, werden) bildiren fiiller **sein** alır; sein, bleiben ve passieren de öyle.",
    "Ask: does the subject move somewhere, or turn into something else? Yes: sein. No: haben.":
        "Sorun: özne bir yere mi gidiyor, yoksa başka bir şeye mi dönüşüyor? Evet: sein. Hayır: haben.",
    "Building the Partizip II": "Partizip II'yi oluşturmak",
    "**Weak verbs:** ge- + stem + -t: machen → **ge**mach**t**, arbeiten → **ge**arbeit**et**.":
        "**Zayıf fiiller:** ge- + gövde + -t: machen → **ge**mach**t**, arbeiten → **ge**arbeit**et**.",
    "**Strong verbs:** ge- + often a new vowel + -en: finden → **ge**fund**en**, schreiben → **ge**schrieb**en**. These you learn by heart.":
        "**Güçlü fiiller:** ge- + çoğu zaman yeni bir ünlü + -en: finden → **ge**fund**en**, schreiben → **ge**schrieb**en**. Bunları ezberlersiniz.",
    "**No ge-** for verbs ending in -ieren (studiert) or starting with be-, ver-, er-, ent-, emp-, ge-, zer-: besucht, verstanden.":
        "-ieren ile biten (studiert) veya be-, ver-, er-, ent-, emp-, ge-, zer- ile başlayan fiillerde **ge- yok**: besucht, verstanden.",
    "**Separable verbs** put ge- in the middle: an**ge**rufen, auf**ge**standen.": "**Ayrılabilen fiiller** ge-'yi ortaya koyar: an**ge**rufen, auf**ge**standen.",
    "The Partizip II always goes last. Everything else sits between the two parts: Ich **habe** gestern mit meiner Schwester lange **telefoniert**.":
        "Partizip II her zaman en sona gider. Geri kalan her şey iki parçanın arasına girer: Ich **habe** gestern mit meiner Schwester lange **telefoniert**.",
    "Perfekt: how is it built?": "Perfekt nasıl kurulur?",
    "haben or sein (present) + Partizip II at the end": "haben veya sein (şimdiki zaman) + sonda Partizip II",
    "Which verbs take sein in the Perfekt?": "Perfekt'te hangi fiiller sein alır?",
    "Movement from A to B, change of state, and sein, bleiben, passieren.": "A'dan B'ye hareket, durum değişikliği, bir de sein, bleiben, passieren.",
    "Partizip II of weak verbs": "Zayıf fiillerin Partizip II'si", "ge- + stem + -t": "ge- + gövde + -t",
    "Partizip II without ge-": "ge-'siz Partizip II",
    "Verbs in -ieren and with be-, ver-, er-, ent-, emp-, ge-, zer-": "-ieren ile biten ve be-, ver-, er-, ent-, emp-, ge-, zer- ile başlayan fiiller",
    "Partizip II of separable verbs": "Ayrılabilen fiillerin Partizip II'si",
    "ge- between the prefix and the verb": "Ön ek ile fiil arasında ge-",
    "gehen, kommen, fahren in the Perfekt": "Perfekt'te gehen, kommen, fahren",

    # ----- Phönizien: Futur I -----
    "The future. werden plus the infinitive, for predictions and promises.": "Gelecek zaman. Tahminler ve sözler için werden artı mastar.",
    "The Futur I is **werden** in the present + the **infinitive** at the end: Ich **werde** morgen **arbeiten**.":
        "Futur I, şimdiki zamanda **werden** + sonda **mastar**dır: Ich **werde** morgen **arbeiten**.",
    "werden: werde · wirst · wird · werden · werdet · werden. Careful: du **wirst** and er **wird** are irregular.":
        "werden: werde · wirst · wird · werden · werdet · werden. Dikkat: du **wirst** ve er **wird** düzensizdir.",
    "When do Germans use it?": "Almanlar bunu ne zaman kullanır?",
    "Less often than you might think. For plans with a time word, the present is normal: *Morgen fahre ich nach Tyros.* Use the Futur I for **predictions**, **promises** and things that are **not certain**:":
        "Sandığınızdan daha az. Zaman kelimesi olan planlar için şimdiki zaman normaldir: *Morgen fahre ich nach Tyros.* Futur I'i **tahminler**, **sözler** ve **kesin olmayan** şeyler için kullanın:",
    "It will rain tomorrow.": "Yarın yağmur yağacak.", "I'll help you, I promise!": "Sana yardım edeceğim, söz!", "He's probably ill.": "Muhtemelen hasta.",
    "With *wohl* or *sicher* the Futur I makes a guess about the present: *Sie wird wohl im Büro sein* (she's probably at the office).":
        "*wohl* veya *sicher* ile Futur I şimdiki zaman hakkında bir tahmin yapar: *Sie wird wohl im Büro sein* (muhtemelen ofistedir).",
    "Futur I: how is it built?": "Futur I nasıl kurulur?",
    "werden (present) + infinitive at the end": "werden (şimdiki zaman) + sonda mastar",
    "werden in the present": "Şimdiki zamanda werden",
    "Plans with a time word: Futur I or present?": "Zaman kelimesi olan planlar: Futur I mi şimdiki zaman mı?",
    "Usually the present.": "Genellikle şimdiki zaman.",
    "What else does the Futur I express?": "Futur I başka ne ifade eder?",
    "Predictions, promises, and guesses with wohl": "Tahminler, sözler ve wohl ile yapılan tahminler",

    # ----- Ägypten: Modalverben -----
    "können, müssen, dürfen, wollen, sollen, mögen, and the infinitive at the end.": "können, müssen, dürfen, wollen, sollen, mögen ve sonda mastar.",
    "Six **modal verbs** say how you relate to an action: **können** (can), **müssen** (must), **dürfen** (may), **wollen** (want to), **sollen** (should) and **mögen** (like). The other verb goes to the end as an **infinitive**.":
        "Altı **modal fiil** bir eyleme nasıl yaklaştığınızı söyler: **können** (-ebilmek), **müssen** (zorunda olmak), **dürfen** (izinli olmak), **wollen** (istemek), **sollen** (-meli) ve **mögen** (sevmek). Diğer fiil sona **mastar** olarak gider.",
    "I can swim well.": "İyi yüzebilirim.", "You have to get up early tomorrow.": "Yarın erken kalkman gerekiyor.",
    "You're not allowed to smoke here.": "Burada sigara içmek yasak.", "We want to see the pyramids.": "Piramitleri görmek istiyoruz.",
    "In the singular they are irregular: **no ending in ich and er/sie/es** (ich kann, er kann), and most change their vowel (können → kann, müssen → muss, dürfen → darf, wollen → will, mögen → mag).":
        "Tekilde düzensizdirler: **ich ve er/sie/es'te ek yok** (ich kann, er kann) ve çoğu ünlüsünü değiştirir (können → kann, müssen → muss, dürfen → darf, wollen → will, mögen → mag).",
    "*Ich möchte* (I would like) is the polite everyday form. It conjugates like a Präteritum: ich möchte, du möchtest, er möchte.":
        "*Ich möchte* (isterim / istiyorum, kibarca) günlük kibar biçimdir. Bir Präteritum gibi çekilir: ich möchte, du möchtest, er möchte.",
    "In the past": "Geçmişte",
    "In the past, modal verbs normally use the **Präteritum**, not the Perfekt: *Ich **konnte** nicht kommen.* The endings are -te, and the umlaut disappears: können → konnte, müssen → musste, dürfen → durfte, mögen → mochte.":
        "Geçmişte modal fiiller normalde Perfekt'i değil **Präteritum**'u kullanır: *Ich **konnte** nicht kommen.* Ekler -te'dir ve umlaut kaybolur: können → konnte, müssen → musste, dürfen → durfte, mögen → mochte.",
    "*müssen nicht* means *don't have to*, not *must not*. For *must not*, use *nicht dürfen*: *Du darfst hier nicht parken.*":
        "*müssen nicht* \"yapmak zorunda değilsin\" demektir, \"yapmamalısın\" değil. Yasak için *nicht dürfen* kullanın: *Du darfst hier nicht parken.*",
    "The six modal verbs": "Altı modal fiil", "can · must · may · want to · should · like": "-ebilmek · zorunda olmak · izinli olmak · istemek · -meli · sevmek",
    "Modal verbs: ich and er/sie/es": "Modal fiiller: ich ve er/sie/es", "No ending: ich kann, er kann": "Ek yok: ich kann, er kann",
    "Where does the second verb go?": "İkinci fiil nereye gider?", "To the end, as an infinitive": "Sona, mastar olarak",
    "müssen nicht vs. nicht dürfen": "müssen nicht ve nicht dürfen", "don't have to vs. must not": "zorunda değilsin ve yapmamalısın",
    "Modal verbs in the past": "Geçmişte modal fiiller", "Präteritum: -te and no umlaut": "Präteritum: -te ve umlaut yok",

    # ----- Syrien: Präteritum -----
    "The past of stories. -te for weak verbs, a new vowel for strong ones.": "Hikâyelerin geçmiş zamanı. Zayıf fiiller için -te, güçlüler için yeni bir ünlü.",
    "The Präteritum is the past of **stories, books and news**. In speech most verbs use the Perfekt, but a few common ones prefer the Präteritum even in conversation: **sein (war), haben (hatte), werden (wurde)**, the modal verbs, and *es gab* (there was).":
        "Präteritum **hikâyelerin, kitapların ve haberlerin** geçmiş zamanıdır. Konuşmada çoğu fiil Perfekt kullanır, ama birkaç yaygın fiil konuşmada bile Präteritum'u tercih eder: **sein (war), haben (hatte), werden (wurde)**, modal fiiller ve *es gab* (vardı).",
    "Weak verbs: -te": "Zayıf fiiller: -te",
    "Stem + **-te** + ending: ich mach**te**, du mach**test**, er mach**te**, wir mach**ten**, ihr mach**tet**, sie mach**ten**. After -t or -d: arbeit**ete**.":
        "Gövde + **-te** + ek: ich mach**te**, du mach**test**, er mach**te**, wir mach**ten**, ihr mach**tet**, sie mach**ten**. -t veya -d'den sonra: arbeit**ete**.",
    "Strong verbs: a new vowel": "Güçlü fiiller: yeni bir ünlü",
    "Strong verbs change their vowel and take **no ending in ich and er/sie/es**: ich **fuhr**, er **fuhr**, wir **fuhren**. Learn each one with its principal parts: **fahren – fuhr – gefahren**.":
        "Güçlü fiiller ünlülerini değiştirir ve **ich ile er/sie/es'te ek almaz**: ich **fuhr**, er **fuhr**, wir **fuhren**. Her birini temel biçimleriyle öğrenin: **fahren – fuhr – gefahren**.",
    "A few verbs do both, a new vowel **and** -te: bringen → **brachte**, denken → **dachte**, kennen → **kannte**, wissen → **wusste**.":
        "Birkaç fiil ikisini birden yapar, yeni bir ünlü **ve** -te: bringen → **brachte**, denken → **dachte**, kennen → **kannte**, wissen → **wusste**.",
    "Most strong verbs follow a handful of vowel patterns (ei – ie – ie: bleiben, blieb, geblieben; i – a – u: finden, fand, gefunden). The tables in free practice group them by pattern.":
        "Çoğu güçlü fiil birkaç ünlü kalıbını izler (ei – ie – ie: bleiben, blieb, geblieben; i – a – u: finden, fand, gefunden). Serbest alıştırmadaki tablolar onları kalıba göre gruplar.",
    "Präteritum of weak verbs": "Zayıf fiillerin Präteritum'u",
    "stem + -te: ich machte, du machtest, wir machten": "gövde + -te: ich machte, du machtest, wir machten",
    "Präteritum of strong verbs: ich and er/sie/es": "Güçlü fiillerin Präteritum'u: ich ve er/sie/es",
    "No ending: ich fuhr, er fuhr": "Ek yok: ich fuhr, er fuhr",
    "Which verbs use the Präteritum even in speech?": "Hangi fiiller konuşmada bile Präteritum kullanır?",
    "sein, haben, werden, the modal verbs, es gab": "sein, haben, werden, modal fiiller, es gab",
    "A new vowel and -te": "Yeni bir ünlü ve -te",
    "Principal parts of gehen": "gehen'in temel biçimleri", "Principal parts of finden": "finden'in temel biçimleri",

    # ----- Persien: Plusquamperfekt -----
    "The past before the past. hatte or war plus the Partizip II.": "Geçmişten önceki geçmiş. hatte veya war artı Partizip II.",
    "The Plusquamperfekt is the **past before the past**: something that had already happened before another past event. It's built like the Perfekt, but with haben or sein in the **Präteritum**: hatte or war + Partizip II.":
        "Plusquamperfekt **geçmişten önceki geçmiştir**: başka bir geçmiş olaydan önce çoktan olmuş bir şey; Türkçedeki -mıştı gibi. Perfekt gibi kurulur, ama haben veya sein **Präteritum**'dadır: hatte veya war + Partizip II.",
    "When we arrived, the film had already started.": "Vardığımızda film çoktan başlamıştı.",
    "She had already left.": "O çoktan gitmişti.", "After I had eaten, I went for a walk.": "Yemek yedikten sonra yürüyüşe çıktım.",
    "haben or sein? Exactly as in the Perfekt: a verb with sein in the Perfekt (ist gefahren) takes war here (war gefahren).":
        "haben mı sein mi? Tam Perfekt'teki gibi: Perfekt'te sein alan bir fiil (ist gefahren) burada war alır (war gefahren).",
    "*nachdem* (after) almost always brings the Plusquamperfekt with it: *Nachdem er angerufen hatte, ...*":
        "*nachdem* (-dıktan sonra) neredeyse her zaman Plusquamperfekt'i beraberinde getirir: *Nachdem er angerufen hatte, ...*",
    "Plusquamperfekt: how is it built?": "Plusquamperfekt nasıl kurulur?", "hatte or war + Partizip II": "hatte veya war + Partizip II",
    "When do you use the Plusquamperfekt?": "Plusquamperfekt ne zaman kullanılır?",
    "For something that happened before another past event": "Başka bir geçmiş olaydan önce olan bir şey için",
    "Which word often brings the Plusquamperfekt?": "Hangi kelime genellikle Plusquamperfekt'i getirir?", "nachdem (after)": "nachdem (-dıktan sonra)",

    # ----- Baktrien: Konjunktiv II -----
    "Wishes, polite requests and what isn't real: würde, wäre, hätte, könnte.": "Dilekler, kibar ricalar ve gerçek olmayanlar: würde, wäre, hätte, könnte.",
    "The Konjunktiv II is for **wishes, polite requests and things that aren't real**. For most verbs it's simply **würde + infinitive**: *Ich **würde** gern nach Samarkand **reisen**.*":
        "Konjunktiv II **dilekler, kibar ricalar ve gerçek olmayan şeyler** içindir; Türkçedeki dilek-şart kipine (-se, -erdi) benzer. Çoğu fiil için basitçe **würde + mastar**dır: *Ich **würde** gern nach Samarkand **reisen**.*",
    "The verbs with their own forms": "Kendi biçimleri olan fiiller",
    "sein, haben and the modal verbs don't use würde. They have their own forms, and these are the ones you hear all the time: **wäre, hätte, könnte, müsste, dürfte, sollte, wollte, möchte**.":
        "sein, haben ve modal fiiller würde kullanmaz. Kendi biçimleri vardır ve sürekli duyacaklarınız bunlardır: **wäre, hätte, könnte, müsste, dürfte, sollte, wollte, möchte**.",
    "If I had time, I would read more.": "Zamanım olsaydı daha çok okurdum.", "Could you help me?": "Bana yardım edebilir misiniz?",
    "That would be nice!": "Bu güzel olurdu!", "You should sleep more.": "Daha çok uyumalısın.",
    "A few strong verbs": "Birkaç güçlü fiil",
    "Some strong verbs have their own Konjunktiv II too (käme, ginge, gäbe, wüsste). *Wenn es mehr Zeit gäbe ...* sounds elegant, but würde + infinitive is always correct for them.":
        "Bazı güçlü fiillerin de kendi Konjunktiv II'si vardır (käme, ginge, gäbe, wüsste). *Wenn es mehr Zeit gäbe ...* zarif durur, ama onlar için würde + mastar her zaman doğrudur.",
    "Polite requests: *Könnten Sie ...?* and *Würden Sie ...?* are the standard in shops, offices and emails.":
        "Kibar ricalar: *Könnten Sie ...?* ve *Würden Sie ...?* dükkânlarda, ofislerde ve e-postalarda standarttır.",
    "Konjunktiv II for most verbs": "Çoğu fiil için Konjunktiv II", "würde + infinitive": "würde + mastar",
    "Konjunktiv II of sein and haben": "sein ve haben'in Konjunktiv II'si",
    "Konjunktiv II of the modal verbs": "Modal fiillerin Konjunktiv II'si", "A polite request": "Kibar bir rica",
    "Wenn ich Zeit hätte, ...": "Wenn ich Zeit hätte, ...",

    # ----- Indus: Futur II -----
    "What will have happened: werden plus Partizip II plus haben or sein.": "Olmuş olacak olan: werden artı Partizip II artı haben veya sein.",
    "The Futur II looks ahead to something that **will have happened** by a certain time: *Bis Freitag **werde** ich das Buch **gelesen haben**.* It's werden + Partizip II + haben or sein.":
        "Futur II, belli bir zamana kadar **olmuş olacak** bir şeye ileriden bakar: *Bis Freitag **werde** ich das Buch **gelesen haben**.* werden + Partizip II + haben veya sein'dır.",
    "It's the rarest tense on this journey. In speech, the Perfekt usually does the job: *Bis Freitag habe ich das Buch gelesen.*":
        "Bu yolculuğun en nadir zamanıdır. Konuşmada genellikle Perfekt işi görür: *Bis Freitag habe ich das Buch gelesen.*",
    "Guessing about the past": "Geçmiş hakkında tahmin",
    "Its most common use is a guess with *wohl*: *Er **wird** den Bus **verpasst haben*** (he's probably missed the bus).":
        "En yaygın kullanımı *wohl* ile bir tahmindir: *Er **wird** den Bus **verpasst haben*** (muhtemelen otobüsü kaçırmıştır).",
    "haben or sein at the end follows the Perfekt: ich habe gegessen → ich werde gegessen **haben**; ich bin gefahren → ich werde gefahren **sein**.":
        "Sondaki haben veya sein Perfekt'i izler: ich habe gegessen → ich werde gegessen **haben**; ich bin gefahren → ich werde gefahren **sein**.",
    "Futur II: how is it built?": "Futur II nasıl kurulur?", "werden + Partizip II + haben/sein": "werden + Partizip II + haben/sein",
    "Futur II with wohl": "wohl ile Futur II", "A guess about the past": "Geçmiş hakkında bir tahmin",
    "Futur II: haben or sein at the end?": "Futur II: sonda haben mı sein mi?", "The same as in the Perfekt": "Perfekt'tekiyle aynı",

    # ----- Babylon: Alle Zeiten -----
    "The final stop. Every tense, mixed, until it's automatic.": "Son durak. Her zaman, karışık, otomatikleşene kadar.",
    "You have marched through every tense. Babylon mixes them all, the way real German does. For every verb, run the same three questions:":
        "Bütün zamanların içinden geçtiniz. Babil hepsini gerçek Almancanın yaptığı gibi karıştırır. Her fiil için aynı üç soruyu sorun:",
    "**1. When?** Look for the time word (gestern, morgen, damals, schon, gern). **2. Which tense?** Spoken past: Perfekt. Stories: Präteritum. Before the past: Plusquamperfekt. Wishes: Konjunktiv II. **3. Which form?** Strong or weak, haben or sein, separable or not.":
        "**1. Ne zaman?** Zaman kelimesine bakın (gestern, morgen, damals, schon, gern). **2. Hangi zaman?** Konuşmadaki geçmiş: Perfekt. Hikâyeler: Präteritum. Geçmişten önce: Plusquamperfekt. Dilekler: Konjunktiv II. **3. Hangi biçim?** Güçlü mü zayıf mı, haben mı sein mi, ayrılabilen mi değil mi.",
    "From here it's about speed. Come back for the daily mix until the forms come out without thinking. Babylon never closes.":
        "Bundan sonrası hızla ilgili. Biçimler düşünmeden gelene kadar günlük karışım için geri gelin. Babil hiç kapanmaz.",
    "fahren in all seven tenses (ich)": "fahren yedi zamanın hepsinde (ich)",
    "Spoken past or written past?": "Konuşmadaki geçmiş mi, yazıdaki geçmiş mi?",
    "Perfekt in speech; Präteritum in stories, and for sein, haben and the modal verbs": "Konuşmada Perfekt; hikâyelerde ve sein, haben ile modal fiillerde Präteritum",
    "Three questions for every verb": "Her fiil için üç soru", "When? Which tense? Which form?": "Ne zaman? Hangi zaman? Hangi biçim?",
}

PATTERNS = [
    ("{} is irregular in the present: learn the whole row.", "{1} şimdiki zamanda düzensizdir: satırın tamamını öğrenin."),
    ("{} changes its vowel in du and er/sie/es: du {}, er {}.", "{1} du ve er/sie/es'te ünlüsünü değiştirir: du {2}, er {3}."),
    ("{} is separable: the prefix {} goes to the end.", "{1} ayrılabilen bir fiildir: {2} ön eki sona gider."),
    ("Modal verbs in the Präteritum take -te and lose the umlaut: {}.", "Modal fiiller Präteritum'da -te alır ve umlautlarını kaybeder: {1}."),
    ("{} is a strong verb: Präteritum {}.", "{1} güçlü bir fiildir: Präteritum {2}."),
    ("{} is a mixed verb: a vowel change and -te: {}.", "{1} karışık bir fiildir: ünlü değişimi ve -te: {2}."),
    ("{} is irregular: {}.", "{1} düzensizdir: {2}."),
    ("{} takes sein, like sein, werden, bleiben and passieren.", "{1}, sein, werden, bleiben ve passieren gibi sein alır."),
    ("{} takes sein: it describes movement or a change of state.", "{1} sein alır: bir hareketi veya durum değişikliğini anlatır."),
    ("{} takes haben, like most verbs.", "{1}, çoğu fiil gibi haben alır."),
    ("Separable verbs put ge- after the prefix: {}.", "Ayrılabilen fiiller ge-'yi ön ekten sonra koyar: {1}."),
    ("No ge- for verbs ending in -ieren or starting with be-, ver-, er-, ent-, emp-, ge-, zer-: {}.",
     "-ieren ile biten veya be-, ver-, er-, ent-, emp-, ge-, zer- ile başlayan fiillerde ge- yok: {1}."),
    ("Weak Partizip II: ge- + stem + -t: {}.", "Zayıf Partizip II: ge- + gövde + -t: {1}."),
    ("{} has an irregular Partizip II: a vowel change but -t: {}.", "{1} düzensiz bir Partizip II'ye sahiptir: ünlü değişir ama -t ile biter: {2}."),
    ("Strong Partizip II, often with a new vowel and -en: {}.", "Güçlü Partizip II, çoğu zaman yeni bir ünlü ve -en ile: {1}."),
    ("{} uses its own Konjunktiv II form ({}), not würde + infinitive.", "{1} würde + mastar değil, kendi Konjunktiv II biçimini ({2}) kullanır."),
    ("{} also has its own form: {}.", "{1} fiilinin kendi biçimi de vardır: {2}."),
    ("{} in the present: {}.", "Şimdiki zamanda {1}: {2}."),
    ("Principal parts: {}.", "Temel biçimler: {1}."),
]
