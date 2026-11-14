"""Turkish for the text the server sends to the screen: the Declensions course (lessons, cards, steps) and the
drill engine (explanations, hints, table labels).

The course and drill code is written in English. When the app language is Turkish, its responses go through
`localize_*` below, which swap English text for Turkish. Only text fields are touched, never answers or keys,
so grading works the same in both languages.

How a string is translated (`tr`):
1. an exact entry in EXACT;
2. else a template in PATTERNS, where "{}" matches anything and the matched parts are translated again
   (so "The preposition mit always takes the dative." finds "dative" -> "Dativ");
3. else it is split into sentences and each sentence is tried on its own (drill explanations are built by
   gluing sentences together).
Anything without an entry stays English.
"""
import re

from . import db


def lang():
    return db.get_settings().get("ui_language", "en")


# ---------------------------------------------------------------------------------------------------------------
# Exact strings
# ---------------------------------------------------------------------------------------------------------------
EXACT = {
    # ----- grammar words used inside templates -----
    "nominative": "Nominativ", "accusative": "Akkusativ", "dative": "Dativ", "genitive": "Genitiv",
    "masculine": "eril", "feminine": "dişil", "neuter": "nötr", "plural": "çoğul",

    # ----- steps -----
    "Briefing": "Brifing", "Read how it works, with charts and examples.": "Tablolar ve örneklerle nasıl çalıştığını okuyun.",
    "Charts": "Tablolar", "Fill in the tables from memory.": "Tabloları ezberden doldurun.",
    "Drill": "Alıştırma", "20 quick questions. Get 16 right to pass.": "20 hızlı soru. Geçmek için 16 doğru gerekir.",
    "Reading": "Okuma", "Fill in the endings in a short text.": "Kısa bir metinde ekleri doldurun.",
    "Flashcards": "Kartlar", "Flip through the key rules.": "Temel kurallara göz atın.",
    "Checkpoint": "Kontrol noktası", "Pass this to unlock the next planet.": "Sonraki gezegeni açmak için bunu geçin.",

    # ----- planet: Nominativ -----
    "The subject. Where every noun starts: der, die, das.": "Özne. Her ismin başladığı yer: der, die, das.",
    "Every German noun phrase wears a small badge that says what job it does in the sentence. That badge is the **case**, and it shows up as an ending on the article. There are only four cases, and you will take them one planet at a time.":
        "Almancadaki her isim öbeği, cümlede hangi görevi yaptığını söyleyen küçük bir rozet taşır. Bu rozet **hâl**dir (case) ve artikelin sonunda bir ek olarak görünür. Türkçedeki hâl eklerine (-i, -e, -in) benzer; ama Almancada ek ismin değil artikelin üzerindedir. Yalnızca dört hâl vardır ve her birini bir gezegende öğreneceksiniz.",
    "The nominative is the subject": "Nominativ öznedir",
    "The nominative marks **who or what does the action**. It is also the form you find in the dictionary. Ask *wer?* (who?) or *was?* (what?) to find it.":
        "Nominativ **eylemi kimin veya neyin yaptığını** gösterir; Türkçedeki yalın hâl gibidir. Sözlükte bulduğunuz biçim de budur. Bulmak için *wer?* (kim?) veya *was?* (ne?) diye sorun.",
    "The dog is sleeping.": "Köpek uyuyor.", "The woman is reading.": "Kadın okuyor.",
    "The child is playing.": "Çocuk oynuyor.", "The children are playing.": "Çocuklar oynuyor.",
    "After **sein**, **werden** and **bleiben** the noun is nominative too, because it is the same thing as the subject: *Das ist **der** Lehrer.*":
        "**sein**, **werden** ve **bleiben** fiillerinden sonra isim yine Nominativ'dir, çünkü özneyle aynı şeydir: *Das ist **der** Lehrer.*",
    "The key idea: signal endings": "Ana fikir: sinyal ekleri",
    "Look at the last letter of each article: de**r**, di**e**, da**s**, di**e**. Those four letters, **-r, -e, -s, -e**, are the nominative signals. Other words carry the same signals:":
        "Her artikelin son harfine bakın: de**r**, di**e**, da**s**, di**e**. Bu dört harf, **-r, -e, -s, -e**, Nominativ sinyalleridir. Başka kelimeler de aynı sinyalleri taşır:",
    "*jeder* (every), *welcher* (which) and *mancher* (some) work exactly like *dieser*. Learn the signals once and you get all of these words for free. Every later planet is just a new row of signals.":
        "*jeder* (her), *welcher* (hangi) ve *mancher* (bazı) tam olarak *dieser* gibi çalışır. Sinyalleri bir kez öğrenin, bu kelimelerin hepsi bedavaya gelir. Sonraki her gezegen yalnızca yeni bir sinyal satırıdır.",
    "The signals only help if you know the noun's gender. Always learn a noun with its article: not *Tisch*, but *der Tisch*. Endings help: -ung, -heit, -keit, -schaft, -ion are *die*; -chen and -lein are *das*.":
        "Sinyaller ancak ismin cinsiyetini biliyorsanız işe yarar. Türkçede cinsiyet olmadığı için bu en zor kısımdır: her ismi artikeliyle öğrenin, *Tisch* değil *der Tisch*. Ekler yardımcı olur: -ung, -heit, -keit, -schaft, -ion *die*; -chen ve -lein *das*.",
    "Nominativ: the — masculine / feminine / neuter / plural": "Nominativ: belirli artikel — eril / dişil / nötr / çoğul",
    "Nominativ: dieser — masculine / feminine / neuter / plural": "Nominativ: dieser — eril / dişil / nötr / çoğul",
    "Signals: -r, -e, -s, -e": "Sinyaller: -r, -e, -s, -e",
    "When do you use the nominative?": "Nominativ ne zaman kullanılır?",
    "For the subject (who or what does it), and after sein, werden, bleiben.": "Özne için (eylemi kim veya ne yapıyor) ve sein, werden, bleiben'den sonra.",
    "Question words for the nominative": "Nominativ soru kelimeleri",
    "wer? (people) · was? (things)": "wer? (kişiler) · was? (şeyler)",
    "jeder, welcher, mancher: which endings do they take?": "jeder, welcher, mancher: hangi ekleri alır?",
    "The same as dieser: jeder, jede, jedes · welcher, welche, welches": "dieser ile aynı: jeder, jede, jedes · welcher, welche, welches",
    "Nouns ending in -ung, -heit, -keit, -schaft, -ion: which gender?": "-ung, -heit, -keit, -schaft, -ion ile biten isimler: hangi cinsiyet?",
    "die (feminine)": "die (dişil)",
    "Nouns ending in -chen or -lein: which gender?": "-chen veya -lein ile biten isimler: hangi cinsiyet?",
    "das (neuter)": "das (nötr)",

    # ----- planet: Akkusativ -----
    "The direct object. Only one thing changes: der becomes den.": "Nesne. Yalnızca bir şey değişir: der, den olur.",
    "The accusative marks the **direct object**: the person or thing the action is done to. Ask *wen?* (whom?) or *was?* (what?).":
        "Akkusativ **nesneyi** gösterir: eylemin yapıldığı kişi veya şey; Türkçedeki -i hâline (belirtme hâli) benzer. *wen?* (kimi?) veya *was?* (neyi?) diye sorun.",
    "I see the dog.": "Köpeği görüyorum.", "I see the woman.": "Kadını görüyorum.",
    "I see the child.": "Çocuğu görüyorum.", "I see the children.": "Çocukları görüyorum.",
    "Good news: in the accusative **only the masculine changes**. *der* becomes *de**n***. Feminine, neuter and plural look exactly like the nominative.":
        "İyi haber: Akkusativ'de **yalnızca eril değişir**. *der*, *de**n*** olur. Dişil, nötr ve çoğul tam olarak Nominativ gibi görünür.",
    "The signal **-n** appears on every masculine der-word: *dieser* becomes *diese**n***, *jeder* becomes *jede**n***, *welcher* becomes *welche**n***.":
        "**-n** sinyali her eril der-kelimesinde görünür: *dieser* → *diese**n***, *jeder* → *jede**n***, *welcher* → *welche**n***.",
    "Prepositions that always take the accusative": "Her zaman Akkusativ alan edatlar",
    "After these five the noun is accusative, every time, whatever the verb is doing:": "Bu beş edattan sonra isim, fiil ne olursa olsun, her zaman Akkusativ'dir:",
    "**durch** (through) · **für** (for) · **gegen** (against) · **ohne** (without) · **um** (around)":
        "**durch** (içinden) · **für** (için) · **gegen** (karşı) · **ohne** (-sız) · **um** (etrafında)",
    "The present is for the teacher.": "Hediye öğretmen için.", "We walk through the park.": "Parkın içinden yürüyoruz.",
    "Pronouns change too": "Zamirler de değişir",
    "The -n shows up in the pronoun as well: de**n** Mann → ih**n**. And notice *sie*, *es* and *sie* don't change at all, just like *die*, *das* and *die*.":
        "-n zamirde de görünür: de**n** Mann → ih**n**. Dikkat edin: *sie*, *es* ve *sie* hiç değişmez, tıpkı *die*, *das* ve *die* gibi.",
    "Akkusativ: the — masculine / feminine / neuter / plural": "Akkusativ: belirli artikel — eril / dişil / nötr / çoğul",
    "Only the masculine changes.": "Yalnızca eril değişir.",
    "The five prepositions that always take the accusative": "Her zaman Akkusativ alan beş edat",
    "Question words for the accusative": "Akkusativ soru kelimeleri",
    "wen? (people) · was? (things)": "wen? (kişiler) · was? (şeyler)",
    "dieser, jeder, welcher → Akkusativ masculine": "dieser, jeder, welcher → Akkusativ eril",
    "When do you use the accusative?": "Akkusativ ne zaman kullanılır?",
    "For the direct object, and after durch, für, gegen, ohne, um.": "Nesne için ve durch, für, gegen, ohne, um'dan sonra.",

    # ----- planet: Dativ -----
    "The receiver. New signals: -m, -r, -m, -n.": "Alıcı. Yeni sinyaller: -m, -r, -m, -n.",
    "The dative marks the **indirect object**: the person who receives something or benefits. Ask *wem?* (to whom?).":
        "Dativ **dolaylı nesneyi** gösterir: bir şeyi alan veya bundan yararlanan kişi; Türkçedeki -e hâline (yönelme hâli) benzer. *wem?* (kime?) diye sorun.",
    "I give the man the book.": "Adama kitabı veriyorum.", "I give the woman the book.": "Kadına kitabı veriyorum.",
    "I give the child the book.": "Çocuğa kitabı veriyorum.", "I give the children the book.": "Çocuklara kitabı veriyorum.",
    "The dative signals are **-m, -r, -m, -n**. Everything changes here, so this row needs real drilling.":
        "Dativ sinyalleri **-m, -r, -m, -n**'dir. Burada her şey değişir, bu yüzden bu satır gerçekten çalışma ister.",
    "Two traps. First: dative feminine is *der*, which looks masculine but isn't. Second: in the dative plural the **noun adds -n too**: *mit den Kinder**n***, unless it already ends in -n or -s.":
        "İki tuzak var. Birincisi: Dativ dişil *der*'dir; eril gibi görünür ama değildir. İkincisi: Dativ çoğulda **isim de -n alır**: *mit den Kinder**n***, zaten -n veya -s ile bitmiyorsa.",
    "Prepositions that always take the dative": "Her zaman Dativ alan edatlar",
    "I go by bus.": "Otobüsle gidiyorum.", "She comes out of the school.": "Okuldan çıkıyor.", "After training we eat.": "Antrenmandan sonra yemek yiyoruz.",
    "Some of these merge with the article: *bei dem* → **beim**, *von dem* → **vom**, *zu dem* → **zum**, *zu der* → **zur**.":
        "Bunların bazıları artikelle birleşir: *bei dem* → **beim**, *von dem* → **vom**, *zu dem* → **zum**, *zu der* → **zur**.",
    "Verbs that take the dative": "Dativ alan fiiller",
    "A handful of common verbs take a dative object where English makes you expect a direct object:":
        "Bazı yaygın fiiller, nesne beklediğiniz yerde Dativ alır. Türkçeden düşünmek bazen yardımcı olur: *birine yardım etmek* (helfen), *birine teşekkür etmek* (danken):",
    "I help the teacher.": "Öğretmene yardım ediyorum.", "The book belongs to the woman.": "Kitap kadına ait.",
    "Dative pronouns": "Dativ zamirleri",
    "The signals repeat in the pronouns: de**m** → ih**m**, de**r** → ih**r**, de**n** → ihne**n**.":
        "Sinyaller zamirlerde tekrar eder: de**m** → ih**m**, de**r** → ih**r**, de**n** → ihne**n**.",
    "Dativ: the — masculine / feminine / neuter / plural": "Dativ: belirli artikel — eril / dişil / nötr / çoğul",
    "dem · der · dem · den (+n on the noun)": "dem · der · dem · den (isme +n)",
    "Signals: -m, -r, -m, -n": "Sinyaller: -m, -r, -m, -n",
    "Common verbs that take the dative": "Dativ alan yaygın fiiller",
    "Question word for the dative": "Dativ soru kelimesi",
    "Dative plural: what happens to the noun?": "Dativ çoğul: isme ne olur?",
    "It adds -n: mit den Kindern.": "-n alır: mit den Kindern.",
    "Not if it already ends in -n or -s: mit den Frauen, mit den Autos.": "Zaten -n veya -s ile bitiyorsa almaz: mit den Frauen, mit den Autos.",

    # ----- planet: Wo oder wohin? -----
    "Nine prepositions that switch between accusative and dative.": "Akkusativ ile Dativ arasında geçiş yapan dokuz edat.",
    "Nine prepositions can take **either** the accusative or the dative. The sentence's meaning decides.":
        "Dokuz edat Akkusativ **ya da** Dativ alabilir. Cümlenin anlamı karar verir.",
    "One question decides": "Tek bir soru karar verir",
    "Is something **moving to a new place**? Ask *wohin?* (where to?) and use the **accusative**. Is it **already there**? Ask *wo?* (where?) and use the **dative**.":
        "Bir şey **yeni bir yere mi gidiyor**? *wohin?* (nereye?) diye sorun ve **Akkusativ** kullanın. **Zaten orada mı**? *wo?* (nerede?) diye sorun ve **Dativ** kullanın. Türkçedeki *-e* (nereye) ve *-de* (nerede) ayrımı gibi düşünün.",
    "I'm going into the park. (wohin? → accusative)": "Parka gidiyorum. (wohin? → Akkusativ)",
    "I'm in the park. (wo? → dative)": "Parktayım. (wo? → Dativ)",
    "I put the book on the table. (wohin?)": "Kitabı masaya koyuyorum. (wohin?)",
    "The book is lying on the table. (wo?)": "Kitap masanın üstünde duruyor. (wo?)",
    "Verb pairs give it away": "Fiil çiftleri ele verir",
    "German has pairs of verbs: one means *put it there* (accusative), the other means *it is there* (dative).":
        "Almancada fiil çiftleri vardır: biri *oraya koy* (Akkusativ), diğeri *orada duruyor* (Dativ) anlamına gelir.",
    "to stand something somewhere → to be standing": "bir şeyi bir yere dikmek → dikili durmak",
    "to lay something down → to be lying": "bir şeyi yatırmak → yatık durmak",
    "to sit someone down → to be sitting": "birini oturtmak → oturuyor olmak",
    "to hang something up → to be hanging": "bir şeyi asmak → asılı durmak",
    "Movement **inside** one place is still dative: *Ich laufe in **dem** Park* means I'm running around in the park. Accusative needs a change of place: *Ich laufe in **den** Park*.":
        "Bir yerin **içindeki** hareket yine Dativ'dir: *Ich laufe in **dem** Park* parkta koşuyorum demektir. Akkusativ için yer değiştirmek gerekir: *Ich laufe in **den** Park* (parka koşuyorum).",
    "Contractions you will see all the time: *in dem* → **im**, *an dem* → **am**, *in das* → **ins**, *an das* → **ans**.":
        "Sürekli göreceğiniz kısaltmalar: *in dem* → **im**, *an dem* → **am**, *in das* → **ins**, *an das* → **ans**.",
    "The nine two-way prepositions": "Dokuz iki yönlü edat",
    "Two-way preposition + movement to a new place (wohin?)": "İki yönlü edat + yeni bir yere hareket (wohin?)",
    "Two-way preposition + location (wo?)": "İki yönlü edat + konum (wo?)",
    "stellen / stehen: which case after a two-way preposition?": "stellen / stehen: iki yönlü edattan sonra hangi hâl?",
    "legen / liegen: which case?": "legen / liegen: hangi hâl?",

    # ----- planet: ein, kein, mein -----
    "The same signals, with three famous gaps.": "Aynı sinyaller, üç ünlü boşlukla.",
    "*ein*, *kein* and the possessives (*mein, dein, sein, ihr, unser, euer, Ihr*) are called **ein-words**. They use the same signal endings you already know from *dieser*, with one twist.":
        "*ein*, *kein* ve iyelik sözcükleri (*mein, dein, sein, ihr, unser, euer, Ihr*) **ein-kelimeleri** olarak adlandırılır. *dieser*'den bildiğiniz sinyal eklerini kullanırlar, tek bir farkla.",
    "In **three slots an ein-word has no ending at all**: nominative masculine, nominative neuter and accusative neuter. *ein Mann, ein Kind, ein Kind.*":
        "**Üç yerde ein-kelimesi hiç ek almaz**: Nominativ eril, Nominativ nötr ve Akkusativ nötr. *ein Mann, ein Kind, ein Kind.*",
    "Compare with *dieser*: dies**er** Mann but **ein** Mann; dies**es** Kind but **ein** Kind. Everywhere else the endings match: dies**en** / ein**en**, dies**em** / ein**em**, dies**er** / ein**er**.":
        "*dieser* ile karşılaştırın: dies**er** Mann ama **ein** Mann; dies**es** Kind ama **ein** Kind. Diğer her yerde ekler aynıdır: dies**en** / ein**en**, dies**em** / ein**em**, dies**er** / ein**er**.",
    "kein and the possessives": "kein ve iyelik sözcükleri",
    "*kein* is just *ein* with a k, and it also has a plural: *keine Kinder, mit keinen Kindern*. The possessives take exactly the same endings:":
        "*kein*, başına k gelmiş *ein*'dır ve çoğulu da vardır: *keine Kinder, mit keinen Kindern*. İyelik sözcükleri de tamamen aynı ekleri alır:",
    "That is my brother. (nominative masculine: no ending)": "Bu benim erkek kardeşim. (Nominativ eril: ek yok)",
    "I see my brother.": "Erkek kardeşimi görüyorum.", "I help my brother.": "Erkek kardeşime yardım ediyorum.",
    "I travel with my sister.": "Kız kardeşimle seyahat ediyorum.",
    "Two decisions for a possessive": "İyelik sözcüğü için iki karar",
    "First pick the word by the **owner**: ich → mein, du → dein, er → sein, sie → ihr, es → sein, wir → unser, ihr → euer, sie → ihr, Sie → Ihr. Then add the ending by the **thing owned**: its gender, number and case.":
        "Önce kelimeyi **sahibine** göre seçin: ich → mein, du → dein, er → sein, sie → ihr, es → sein, wir → unser, ihr → euer, sie → ihr, Sie → Ihr. Sonra eki **sahip olunan şeye** göre ekleyin: cinsiyeti, sayısı ve hâli.",
    "*euer* drops an e when it gets an ending: **eure** Mutter, mit **eurem** Vater.": "*euer* ek aldığında bir e düşürür: **eure** Mutter, mit **eurem** Vater.",
    "ein in the nominative: masculine / feminine / neuter": "Nominativ'de ein: eril / dişil / nötr",
    "ein in the accusative: masculine / feminine / neuter": "Akkusativ'de ein: eril / dişil / nötr",
    "ein in the dative: masculine / feminine / neuter": "Dativ'de ein: eril / dişil / nötr",
    "kein in the plural: Nominativ / Akkusativ / Dativ": "Çoğulda kein: Nominativ / Akkusativ / Dativ",
    "The possessives for ich, du, er, sie, es, wir, ihr, sie, Sie": "ich, du, er, sie, es, wir, ihr, sie, Sie için iyelik sözcükleri",
    "In which three slots do ein-words have no ending?": "ein-kelimeleri hangi üç yerde ek almaz?",
    "Nominative masculine, nominative neuter, accusative neuter.": "Nominativ eril, Nominativ nötr, Akkusativ nötr.",
    "What happens to euer when it takes an ending?": "euer ek aldığında ne olur?",
    "It drops an e: eure, euren, eurem, eurer.": "Bir e düşer: eure, euren, eurem, eurer.",

    # ----- planet: Genitiv -----
    "Possession. des and der, and an -s on the noun.": "Sahiplik. des ve der, isimde de bir -s.",
    "The genitive shows **possession**, like English *of the* or *'s*. Ask *wessen?* (whose?). The owner comes second: *das Auto **des Mannes*** is the man's car.":
        "Genitiv **sahipliği** gösterir; Türkçedeki ilgi hâli (-in) gibidir. *wessen?* (kimin?) diye sorun. Sahip ikinci gelir, Türkçenin tersine: *das Auto **des Mannes*** adamın arabası demektir.",
    "Only two forms to learn: **des** for masculine and neuter, **der** for feminine and plural.":
        "Öğrenilecek yalnızca iki biçim var: eril ve nötr için **des**, dişil ve çoğul için **der**.",
    "Masculine and neuter **nouns add -s or -es** as well. Short words and words ending in -s, -ß, -z or -sch take **-es**: *des Mann**es**, des Haus**es***. Longer words take **-s**: *des Lehrer**s**, des Auto**s***. Feminine and plural nouns don't change.":
        "Eril ve nötr **isimler de -s veya -es alır**. Kısa kelimeler ve -s, -ß, -z veya -sch ile bitenler **-es** alır: *des Mann**es**, des Haus**es***. Daha uzun kelimeler **-s** alır: *des Lehrer**s**, des Auto**s***. Dişil ve çoğul isimler değişmez.",
    "the teacher's car": "öğretmenin arabası", "the woman's bag": "kadının çantası",
    "the color of the house": "evin rengi", "the children's parents": "çocukların ebeveynleri",
    "ein-words in the genitive": "Genitiv'de ein-kelimeleri",
    "The possessives follow: *das Auto **meines** Vaters, die Wohnung **meiner** Schwester*.":
        "İyelik sözcükleri de aynı yolu izler: *das Auto **meines** Vaters, die Wohnung **meiner** Schwester*.",
    "Prepositions with the genitive": "Genitiv alan edatlar",
    "**wegen** (because of) · **trotz** (despite) · **während** (during) · **statt** (instead of) · **innerhalb** (inside) · **außerhalb** (outside)":
        "**wegen** (yüzünden) · **trotz** (rağmen) · **während** (sırasında) · **statt** (yerine) · **innerhalb** (içinde) · **außerhalb** (dışında)",
    "Because of the weather we're staying here.": "Hava yüzünden burada kalıyoruz.",
    "During the break I drink coffee.": "Molada kahve içiyorum.",
    "In everyday speech people often say *von dem* instead: *das Auto von dem Lehrer*. You need the genitive for writing, reading and exams.":
        "Günlük konuşmada insanlar çoğu zaman bunun yerine *von dem* der: *das Auto von dem Lehrer*. Yazma, okuma ve sınavlar için Genitiv gerekir.",
    "Genitiv: the — masculine / feminine / neuter / plural": "Genitiv: belirli artikel — eril / dişil / nötr / çoğul",
    "Genitive masculine and neuter: what happens to the noun?": "Genitiv eril ve nötr: isme ne olur?",
    "It adds -s or -es: des Lehrers, des Hauses.": "-s veya -es alır: des Lehrers, des Hauses.",
    "-es after short words and after -s, -ß, -z, -sch.": "-es kısa kelimelerden ve -s, -ß, -z, -sch'den sonra.",
    "ein in the genitive: masculine / feminine / neuter": "Genitiv'de ein: eril / dişil / nötr",
    "Question word for the genitive": "Genitiv soru kelimesi",
    "wessen? (whose?)": "wessen? (kimin?)",
    "Say in German: my father's car": "Almanca söyleyin: babamın arabası",

    # ----- planet: adjectives after der -----
    "Adjectives after der": "der'den sonra sıfatlar",
    "Only two endings exist here: -e and -en.": "Burada yalnızca iki ek var: -e ve -en.",
    "Now the adjectives. When an adjective stands **in front of a noun**, it needs an ending. Which one depends on what stands before it. This planet covers the easiest situation: a **der-word** comes first (*der, dieser, jeder, welcher, alle*).":
        "Şimdi sıfatlar. Bir sıfat **ismin önünde** durduğunda ek alması gerekir. Hangi eki alacağı önünde ne olduğuna bağlıdır. Bu gezegen en kolay durumu kapsar: önce bir **der-kelimesi** gelir (*der, dieser, jeder, welcher, alle*).",
    "The der-word already shows the case signal, so the adjective can relax. It takes only **-e** or **-en**.":
        "der-kelimesi hâl sinyalini zaten gösterir, bu yüzden sıfat rahat olabilir. Yalnızca **-e** veya **-en** alır.",
    "How to remember it": "Nasıl hatırlanır",
    "**-e** in exactly five slots: the three nominative singulars, plus accusative feminine and neuter. Those are the slots where the article still looks like its dictionary form (*der, die, das, die, das*). **Everything else is -en**: all datives, all genitives, all plurals, and accusative masculine.":
        "**-e** tam olarak beş yerde: üç Nominativ tekil, artı Akkusativ dişil ve nötr. Bunlar artikelin hâlâ sözlükteki biçimine benzediği yerlerdir (*der, die, das, die, das*). **Geri kalan her şey -en**: tüm Dativler, tüm Genitivler, tüm çoğullar ve Akkusativ eril.",
    "the new film (nominative)": "yeni film (Nominativ)", "I see the new film. (accusative masculine)": "Yeni filmi görüyorum. (Akkusativ eril)",
    "the new lamp (nominative and accusative)": "yeni lamba (Nominativ ve Akkusativ)", "with the new lamp (dative)": "yeni lambayla (Dativ)",
    "the new films (plural: always -en)": "yeni filmler (çoğul: her zaman -en)",
    "A quick test: if the article has changed from its dictionary form, or it's plural, the answer is -en.":
        "Hızlı bir test: artikel sözlükteki biçiminden değiştiyse ya da çoğulsa cevap -en'dir.",
    "A few adjectives change their spelling when they take an ending: *teuer* → *teur-* (der teure Wein), *dunkel* → *dunkl-* (das dunkle Zimmer), *hoch* → *hoh-* (der hohe Berg).":
        "Birkaç sıfat ek aldığında yazılışını değiştirir: *teuer* → *teur-* (der teure Wein), *dunkel* → *dunkl-* (das dunkle Zimmer), *hoch* → *hoh-* (der hohe Berg).",
    "Adjective after a der-word: which five slots take -e?": "der-kelimesinden sonra sıfat: hangi beş yer -e alır?",
    "Nominative masculine, feminine, neuter; accusative feminine and neuter.": "Nominativ eril, dişil, nötr; Akkusativ dişil ve nötr.",
    "Everything else takes -en.": "Geri kalan her şey -en alır.",
    "Which words count as der-words?": "Hangi kelimeler der-kelimesi sayılır?",
    "Dative is always -en.": "Dativ her zaman -en'dir.",
    "die alt_ Bücher (plural)": "die alt_ Bücher (çoğul)",
    "After a der-word the plural is always -en.": "der-kelimesinden sonra çoğul her zaman -en'dir.",

    # ----- planet: adjectives after ein -----
    "Adjectives after ein": "ein'dan sonra sıfatlar",
    "Where ein is silent, the adjective speaks: -er and -es.": "ein'ın sustuğu yerde sıfat konuşur: -er ve -es.",
    "After an **ein-word** (*ein, kein, mein, dein...*) the adjective endings are almost the same as on the last planet. The difference comes from those three slots where ein-words have **no ending**.":
        "Bir **ein-kelimesinden** sonra (*ein, kein, mein, dein...*) sıfat ekleri önceki gezegendekiyle neredeyse aynıdır. Fark, ein-kelimelerinin **ek almadığı** o üç yerden gelir.",
    "Somebody has to show the gender. If the ein-word doesn't, **the adjective does**: ein neu**er** Film (like de**r**), ein neu**es** Auto (like da**s**).":
        "Cinsiyeti birinin göstermesi gerekir. ein-kelimesi göstermiyorsa **sıfat gösterir**: ein neu**er** Film (de**r** gibi), ein neu**es** Auto (da**s** gibi).",
    "nominative masculine": "Nominativ eril", "nominative and accusative neuter": "Nominativ ve Akkusativ nötr",
    "feminine: no change": "dişil: değişiklik yok", "accusative masculine: no change": "Akkusativ eril: değişiklik yok",
    "So there are only **three special slots** to remember, and they are exactly the three where *ein* is bare. Everywhere else you already know the answer: -e for feminine nominative and accusative, **-en** for all the rest.":
        "Yani hatırlanacak yalnızca **üç özel yer** var ve bunlar tam olarak *ein*'ın çıplak olduğu üç yerdir. Diğer her yerde cevabı zaten biliyorsunuz: dişil Nominativ ve Akkusativ için -e, geri kalan her şey için **-en**.",
    "Plural after *keine, meine, deine...* is always **-en**: *meine alt**en** Freunde, keine gut**en** Ideen*.":
        "*keine, meine, deine...*'den sonra çoğul her zaman **-en**'dir: *meine alt**en** Freunde, keine gut**en** Ideen*.",
    "Adjective after an ein-word: the three special slots": "ein-kelimesinden sonra sıfat: üç özel yer",
    "ein neuer (nom. masc.) · ein neues (nom. and acc. neuter)": "ein neuer (Nom. eril) · ein neues (Nom. ve Akk. nötr)",
    "Feminine nom./acc. takes -e; everything else takes -en.": "Dişil Nom./Akk. -e alır; geri kalan her şey -en alır.",
    "Plural after an ein-word is always -en.": "ein-kelimesinden sonra çoğul her zaman -en'dir.",
    "Why 'ein guter Mann' but 'der gute Mann'?": "Neden 'ein guter Mann' ama 'der gute Mann'?",
    "Something must show the gender. ein has no ending, so the adjective carries the -er.": "Bir şeyin cinsiyeti göstermesi gerekir. ein ek almadığı için -er'i sıfat taşır.",

    # ----- planet: adjectives alone -----
    "Adjectives alone": "Tek başına sıfatlar",
    "No article at all, so the adjective does all the work.": "Hiç artikel yok, bu yüzden bütün işi sıfat yapar.",
    "Sometimes there is **no article** at all: *kalter Kaffee, frische Milch, gute Freunde*. This happens with food and materials, with plurals, and after numbers.":
        "Bazen hiç **artikel yoktur**: *kalter Kaffee, frische Milch, gute Freunde*. Bu, yiyecek ve malzemelerde, çoğullarda ve sayılardan sonra olur.",
    "With no article, the adjective **takes the signal ending itself**, the same ending *dieser* would have: dies**er** Kaffee → kalt**er** Kaffee.":
        "Artikel yoksa sıfat **sinyal ekini kendisi alır**, *dieser*'in alacağı ekin aynısını: dies**er** Kaffee → kalt**er** Kaffee.",
    "cold coffee (like dieser)": "soğuk kahve (dieser gibi)", "fresh milk (like diese)": "taze süt (diese gibi)",
    "cold water (like dieses)": "soğuk su (dieses gibi)", "with fresh milk (like mit dieser)": "taze sütle (mit dieser gibi)",
    "with cold water (like mit diesem)": "soğuk suyla (mit diesem gibi)", "good friends (like diese)": "iyi arkadaşlar (diese gibi)",
    "One exception: genitive masculine and neuter take **-en**, not -es, because the noun already shows the -s: *trotz schlecht**en** Wetter**s***.":
        "Tek bir istisna: Genitiv eril ve nötr -es değil **-en** alır, çünkü isim -s'yi zaten gösterir: *trotz schlecht**en** Wetter**s***.",
    "The whole system in one sentence": "Bütün sistem tek cümlede",
    "The signal ending must appear **once** in the noun phrase. If an article shows it, the adjective takes -e or -en. If nothing shows it, the adjective shows it. That is all three adjective planets.":
        "Sinyal eki isim öbeğinde **bir kez** görünmelidir. Artikel gösteriyorsa sıfat -e veya -en alır. Hiçbir şey göstermiyorsa sıfat gösterir. Üç sıfat gezegeninin hepsi bundan ibaret.",
    "Adjective with no article: what is the rule?": "Artikelsiz sıfat: kural nedir?",
    "It takes the ending dieser would have: kalter, kalte, kaltes.": "dieser'in alacağı eki alır: kalter, kalte, kaltes.",
    "Exception: genitive masculine and neuter take -en.": "İstisna: Genitiv eril ve nötr -en alır.",
    "kalt_ Kaffee (nominative) / kalt_ Kaffee (accusative)": "kalt_ Kaffee (Nominativ) / kalt_ Kaffee (Akkusativ)",
    "gut_ Freunde (nominative) / mit gut_ Freunden": "gut_ Freunde (Nominativ) / mit gut_ Freunden",

    # ----- planet: pronouns & weak nouns -----
    "Pronouns & weak nouns": "Zamirler ve zayıf isimler",
    "Relative and reflexive pronouns, and nouns that take -n.": "İlgi ve dönüşlü zamirler, bir de -n alan isimler.",
    "Relative pronouns": "İlgi zamirleri",
    "A relative pronoun starts a clause that describes a noun: *the man **who** lives here*. In German it looks like the article *der, die, das*, with three exceptions.":
        "İlgi zamiri bir ismi niteleyen bir yan cümle başlatır: *burada yaşa**yan** adam* (der Mann, **der** hier wohnt). Almancada *der, die, das* artikeline benzer, üç istisnayla.",
    "**Gender and number** come from the noun it refers to. **Case** comes from its job inside the relative clause.":
        "**Cinsiyet ve sayı** işaret ettiği isimden gelir. **Hâl** ise yan cümle içindeki görevinden gelir.",
    "subject of the clause → nominative": "yan cümlenin öznesi → Nominativ", "object of sehen → accusative": "sehen'in nesnesi → Akkusativ",
    "helfen takes the dative": "helfen Dativ alır", "whose → genitive": "kimin → Genitiv",
    "The exceptions are the long forms: genitive **dessen** and **deren**, and dative plural **denen**.":
        "İstisnalar uzun biçimlerdir: Genitiv **dessen** ve **deren**, Dativ çoğul **denen**.",
    "Reflexive pronouns": "Dönüşlü zamirler",
    "Reflexive verbs point back at the subject: *Ich wasche **mich***. The pronouns are the normal accusative and dative ones, except that every third person and formal *Sie* use **sich**.":
        "Dönüşlü fiiller özneye geri döner, Türkçedeki *kendini yıkamak* gibi: *Ich wasche **mich***. Zamirler normal Akkusativ ve Dativ zamirleridir; yalnız tüm üçüncü şahıslar ve resmî *Sie* **sich** kullanır.",
    "Use the **dative** (*mir, dir*) when the sentence has another direct object: *Ich wasche **mich***, but *Ich wasche **mir** die Hände*.":
        "Cümlede başka bir nesne varsa **Dativ** (*mir, dir*) kullanın: *Ich wasche **mich***, ama *Ich wasche **mir** die Hände*.",
    "Weak nouns": "Zayıf isimler",
    "A small group of masculine nouns, mostly people, add **-n or -en in every case except the nominative singular**: *der Student, der Kollege, der Junge, der Kunde, der Nachbar, der Mensch, der Herr, der Polizist*.":
        "Çoğu insan bildiren küçük bir eril isim grubu, **Nominativ tekil dışındaki her hâlde -n veya -en alır**: *der Student, der Kollege, der Junge, der Kunde, der Nachbar, der Mensch, der Herr, der Polizist*.",
    "nominative: no ending": "Nominativ: ek yok", "genitive (no -s!)": "Genitiv (-s yok!)",
    "Where do relative pronouns differ from der, die, das?": "İlgi zamirleri der, die, das'tan nerede ayrılır?",
    "Genitive: dessen, deren. Dative plural: denen.": "Genitiv: dessen, deren. Dativ çoğul: denen.",
    "Relative pronoun: where do its gender and its case come from?": "İlgi zamiri: cinsiyeti ve hâli nereden gelir?",
    "Gender and number from the noun it refers to; case from its job in the relative clause.": "Cinsiyet ve sayı işaret ettiği isimden; hâl yan cümledeki görevinden.",
    "Reflexive pronouns, accusative: ich, du, er/sie/es, wir, ihr, sie/Sie": "Dönüşlü zamirler, Akkusativ: ich, du, er/sie/es, wir, ihr, sie/Sie",
    "When is the reflexive pronoun dative (mir, dir)?": "Dönüşlü zamir ne zaman Dativ olur (mir, dir)?",
    "When the sentence has another direct object.": "Cümlede başka bir nesne olduğunda.",
    "What is a weak noun?": "Zayıf isim nedir?",
    "A masculine noun that adds -(e)n in every case but the nominative singular.": "Nominativ tekil dışındaki her hâlde -(e)n alan eril bir isim.",
    "der Herr → Akkusativ / Dativ / Genitiv singular, and the plural": "der Herr → Akkusativ / Dativ / Genitiv tekil ve çoğul",

    # ----- planet: everything together -----
    "Everything together": "Hepsi bir arada",
    "The final approach. Every case, every ending, in full sentences.": "Son yaklaşma. Her hâl, her ek, tam cümlelerde.",
    "You have visited every planet. This last stop mixes everything, the way real German does. For every noun phrase, run the same three questions:":
        "Her gezegeni ziyaret ettiniz. Bu son durak, gerçek Almancanın yaptığı gibi her şeyi karıştırır. Her isim öbeği için aynı üç soruyu sorun:",
    "**1. Which case?** Look at the verb and the preposition. **2. Which gender or number?** That comes from the noun. **3. Who shows the signal?** The article if it can; otherwise the adjective.":
        "**1. Hangi hâl?** Fiile ve edata bakın. **2. Hangi cinsiyet veya sayı?** Bu isimden gelir. **3. Sinyali kim gösteriyor?** Yapabiliyorsa artikel; yoksa sıfat.",
    "The whole system on one page": "Bütün sistem tek sayfada",
    "These sixteen signal endings are the core. *der, die, das* is the same table with different vowels. ein-words use it too, minus three endings. Adjectives with no article copy it.":
        "Bu on altı sinyal eki işin özüdür. *der, die, das* farklı ünlülerle aynı tablodur. ein-kelimeleri de bunu kullanır, üç ek eksik. Artikelsiz sıfatlar onu kopyalar.",
    "And when an article already shows the signal, the adjective takes -e in five slots and -en everywhere else. After an ein-word with no ending, the adjective takes the missing -er or -es.":
        "Artikel sinyali zaten gösteriyorsa sıfat beş yerde -e, diğer her yerde -en alır. Eksiz bir ein-kelimesinden sonra sıfat eksik olan -er veya -es'i alır.",
    "dative receiver, accusative thing": "Dativ alıcı, Akkusativ şey",
    "genitive after wegen; bare mein, so -er": "wegen'den sonra Genitiv; mein eksiz, bu yüzden -er",
    "dative plural; dative after in (wo?)": "Dativ çoğul; in'den sonra Dativ (wo?)",
    "From here it is all about speed. Keep coming back for the daily mix until the endings come out without thinking.":
        "Bundan sonrası tamamen hızla ilgili. Ekler düşünmeden gelene kadar günlük karışım için geri gelmeye devam edin.",
    "The sixteen signal endings (dieser): Nominativ / Akkusativ / Dativ / Genitiv": "On altı sinyal eki (dieser): Nominativ / Akkusativ / Dativ / Genitiv",
    "Order: masculine, feminine, neuter, plural.": "Sıra: eril, dişil, nötr, çoğul.",
    "The three questions for every noun phrase": "Her isim öbeği için üç soru",
    "1. Which case? 2. Which gender or number? 3. Who shows the signal: article or adjective?": "1. Hangi hâl? 2. Hangi cinsiyet veya sayı? 3. Sinyali kim gösteriyor: artikel mi sıfat mı?",
    "Adjective endings in one sentence": "Sıfat ekleri tek cümlede",
    "If an article shows the signal, the adjective takes -e or -en. If nothing shows it, the adjective does.": "Artikel sinyali gösteriyorsa sıfat -e veya -en alır. Hiçbir şey göstermiyorsa sıfat gösterir.",

    # ----- drill engine: fixed explanations -----
    "This is the subject of the sentence, so it is nominative.": "Bu cümlenin öznesi, bu yüzden Nominativ.",
    "After sein, the noun is nominative too.": "sein'dan sonra isim de Nominativ'dir.",
    "This is the direct object, so it is accusative.": "Bu nesne, bu yüzden Akkusativ.",
    "With geben, the person receiving is dative and the thing given is accusative.": "geben ile alan kişi Dativ, verilen şey Akkusativ'dir.",
    "With zeigen, the person you show it to is dative and the thing shown is accusative.": "zeigen ile gösterilen kişi Dativ, gösterilen şey Akkusativ'dir.",
    "mit always takes the dative.": "mit her zaman Dativ alır.",
    "'Of someone' is the genitive.": "'Birinin' anlamı Genitiv'dir.",
    "It is the subject of the relative clause, so it is nominative.": "Yan cümlenin öznesi, bu yüzden Nominativ.",
    "It is the object of gesehen in the relative clause, so it is accusative.": "Yan cümlede gesehen'in nesnesi, bu yüzden Akkusativ.",
    "für takes the accusative.": "für Akkusativ alır.", "helfen takes the dative.": "helfen Dativ alır.", "mit takes the dative.": "mit Dativ alır.",
    "'Whose' is the genitive.": "'Kimin' Genitiv'dir.",
    "wer asks for the subject.": "wer özneyi sorar.",
    "wen asks for an accusative: a direct object or after an accusative preposition.": "wen Akkusativ sorar: bir nesne ya da Akkusativ edatından sonrası.",
    "wem asks for a dative: after a dative verb or preposition.": "wem Dativ sorar: Dativ fiili veya edatından sonrası.",
    "wessen means 'whose'.": "wessen 'kimin' demektir.",
    "Words ending in -ung, -heit, -keit, -schaft, -ion, -tät and -ik are feminine.": "-ung, -heit, -keit, -schaft, -ion, -tät ve -ik ile biten kelimeler dişildir.",
    "Words ending in -chen and -lein are always neuter.": "-chen ve -lein ile biten kelimeler her zaman nötrdür.",
    "Words ending in -ment and -um are usually neuter.": "-ment ve -um ile biten kelimeler genellikle nötrdür.",
    "Words ending in -ling, -ismus, -ist and -or are usually masculine.": "-ling, -ismus, -ist ve -or ile biten kelimeler genellikle erildir.",
    "Female people ending in -in are feminine.": "-in ile biten kadın kişi isimleri dişildir.",
    "Most words ending in -e are feminine.": "-e ile biten kelimelerin çoğu dişildir.",
    "Many words ending in -er, especially people, are masculine, but check each one.": "-er ile biten birçok kelime, özellikle kişiler, erildir; ama her birini kontrol edin.",
    "No reliable pattern for this one, so learn it with its article.": "Bunun için güvenilir bir kalıp yok, artikeliyle birlikte öğrenin.",
    "ein-words have no ending in the nominative masculine or the nominative and accusative neuter.": "ein-kelimeleri Nominativ erilde ve Nominativ ile Akkusativ nötrde ek almaz.",
    "The nominative is the dictionary form.": "Nominativ sözlükteki biçimdir.",
    "In the accusative only the masculine changes: it ends in -n.": "Akkusativ'de yalnızca eril değişir: -n ile biter.",
    "Dative plural ends in -n, and the noun adds -n too unless it already ends in -n or -s.": "Dativ çoğul -n ile biter; isim de zaten -n veya -s ile bitmiyorsa -n alır.",
    "Dative feminine ends in -r.": "Dativ dişil -r ile biter.",
    "After a der-word the adjective takes -e in the nominative singular and the feminine and neuter accusative. Everywhere else it is -en.":
        "der-kelimesinden sonra sıfat Nominativ tekilde ve dişil ile nötr Akkusativ'de -e alır. Diğer her yerde -en'dir.",
    "After a der-word the adjective takes -en here. Only the nominative singular and feminine and neuter accusative take -e.":
        "der-kelimesinden sonra sıfat burada -en alır. Yalnızca Nominativ tekil ile dişil ve nötr Akkusativ -e alır.",
    # the two tips above, sentence by sentence (they get glued to other explanations)
    "After a der-word the adjective takes -e in the nominative singular and the feminine and neuter accusative.":
        "der-kelimesinden sonra sıfat Nominativ tekilde ve dişil ile nötr Akkusativ'de -e alır.",
    "Everywhere else it is -en.": "Diğer her yerde -en'dir.",
    "After a der-word the adjective takes -en here.": "der-kelimesinden sonra sıfat burada -en alır.",
    "Only the nominative singular and feminine and neuter accusative take -e.": "Yalnızca Nominativ tekil ile dişil ve nötr Akkusativ -e alır.",
    "ein has no ending here, so the adjective shows the gender: -er.": "ein burada ek almıyor, bu yüzden cinsiyeti sıfat gösterir: -er.",
    "ein has no ending here, so the adjective shows the gender: -es.": "ein burada ek almıyor, bu yüzden cinsiyeti sıfat gösterir: -es.",
    "Feminine nominative and accusative: the adjective takes -e, as after die.": "Dişil Nominativ ve Akkusativ: sıfat, die'den sonraki gibi -e alır.",
    "After an ein-word every dative, genitive, plural and masculine accusative takes -en.": "ein-kelimesinden sonra her Dativ, Genitiv, çoğul ve eril Akkusativ -en alır.",
    "With no article the adjective acts like the article, except in the genitive masculine and neuter: -en, because the noun already shows -(e)s.":
        "Artikel yoksa sıfat artikel gibi davranır; Genitiv eril ve nötr hariç: orada -en, çünkü isim -(e)s'yi zaten gösterir.",
    "teuer drops an e before an ending: teure.": "teuer ek almadan önce bir e düşürür: teure.",
    "dunkel drops an e before an ending: dunkle.": "dunkel ek almadan önce bir e düşürür: dunkle.",
    "hoch becomes hoh- before an ending: hohe.": "hoch ek almadan önce hoh- olur: hohe.",
    "euer drops an e before an ending: eure, eurem.": "euer ek almadan önce bir e düşürür: eure, eurem.",
    "For wir and ihr the accusative and dative are the same.": "wir ve ihr için Akkusativ ile Dativ aynıdır.",
    "When the sentence already has another object (die Hände), the reflexive pronoun is dative.": "Cümlede zaten başka bir nesne varsa (die Hände), dönüşlü zamir Dativ'dir.",
    "With no other object in the sentence, the reflexive pronoun is accusative.": "Cümlede başka nesne yoksa dönüşlü zamir Akkusativ'dir.",
    "All third-person forms and formal Sie use sich.": "Tüm üçüncü şahıs biçimleri ve resmî Sie, sich kullanır.",
    "Only ich and du have different accusative and dative forms.": "Yalnızca ich ve du'nun farklı Akkusativ ve Dativ biçimleri vardır.",
    "Genitive forms are dessen and deren.": "Genitiv biçimleri dessen ve deren'dir.",
    "The dative plural is the one surprise: denen.": "Tek sürpriz Dativ çoğuldur: denen.",
    "Plurals often change the vowel or add an ending, so learn each noun with its plural.": "Çoğullar çoğu zaman ünlüyü değiştirir veya ek alır; her ismi çoğuluyla birlikte öğrenin.",
    "Dative plural: the noun adds -n unless it already ends in -n or -s.": "Dativ çoğul: isim, zaten -n veya -s ile bitmiyorsa -n alır.",
    "Genitive masculine and neuter nouns add -s, or -es after a short word or one ending in -s, -ß, -z or -sch.":
        "Genitiv eril ve nötr isimler -s alır; kısa bir kelimeden veya -s, -ß, -z ya da -sch ile bitenden sonra -es.",
    "Movement to a new place (wohin?) takes the accusative.": "Yeni bir yere hareket (wohin?) Akkusativ ister.",
    "A fixed location (wo?) takes the dative.": "Sabit bir konum (wo?) Dativ ister.",

    # ----- drill engine: labels and cues -----
    "After der-words": "der-kelimelerinden sonra", "After ein-words": "ein-kelimelerinden sonra", "With no article": "Artikelsiz",
    "Reflexive: mich, mir, sich": "Dönüşlü: mich, mir, sich", "Relative: der, dem, denen": "İlgi: der, dem, denen",
    "Which case?": "Hangi hâl?", "Noun genders": "İsim cinsiyetleri", "Plurals": "Çoğullar", "Noun endings": "İsim ekleri",
    "Whole phrases": "Bütün öbekler", "In sentences": "Cümle içinde",
    "Articles": "Artikeller", "Adjective endings": "Sıfat ekleri", "Pronouns": "Zamirler", "Case triggers": "Hâli belirleyenler",
    "Nouns": "İsimler", "Combinations": "Birleşimler",
    "ich (I)": "ich (ben)", "du (you)": "du (sen)", "er (he)": "er (o, erkek)", "sie (she)": "sie (o, kadın)", "es (it)": "es (o, şey)",
    "wir (we)": "wir (biz)", "ihr (you all)": "ihr (siz, hepiniz)", "sie (they)": "sie (onlar)", "Sie (you, formal)": "Sie (siz, resmî)",
    "Sie (she)": "Sie (o, kadın)", "Sie (they)": "Sie (onlar)",
    "Mask.": "Eril", "Fem.": "Dişil", "Neut.": "Nötr", "Plural": "Çoğul", "who?": "kim?",
    "Adjective after der-words": "der-kelimelerinden sonra sıfat", "Adjective after ein-words": "ein-kelimelerinden sonra sıfat",
    "Adjective with no article": "Artikelsiz sıfat", "Relative pronouns": "İlgi zamirleri", "Personal pronouns": "Şahıs zamirleri",
    "Question words": "Soru kelimeleri",
    "Dative plural nouns add -n. Genitive masculine and neuter nouns add -(e)s.": "Dativ çoğul isimler -n alır. Genitiv eril ve nötr isimler -(e)s alır.",
    "jeder, welcher, mancher and jener take the same endings. jeder has no plural: use alle.": "jeder, welcher, mancher ve jener aynı ekleri alır. jeder'in çoğulu yoktur: alle kullanın.",
    "ein has no plural.": "ein'ın çoğulu yoktur.",
    "kein takes the same endings as ein, and also has a plural.": "kein, ein ile aynı ekleri alır ve çoğulu da vardır.",
    "euer drops an e before an ending: eure, eurem, euren.": "euer ek almadan önce bir e düşürür: eure, eurem, euren.",
    "ihr means her or their. Capitalized, Ihr means your (formal).": "ihr 'onun (kadın)' veya 'onların' demektir. Büyük harfle Ihr 'sizin (resmî)' demektir.",
    "sein means his or its.": "sein 'onun (erkek veya şey)' demektir.",
    "After der, dieser, jeder, welcher, alle. Only five slots take -e; all the rest take -en.": "der, dieser, jeder, welcher, alle'den sonra. Yalnızca beş yer -e alır; geri kalanların hepsi -en.",
    "After ein, kein, mein, dein... Where ein has no ending, the adjective shows the gender: -er or -es.": "ein, kein, mein, dein... sonrasında. ein'ın ek almadığı yerde cinsiyeti sıfat gösterir: -er veya -es.",
    "The adjective takes the article's ending, except in the genitive masculine and neuter: -en.": "Sıfat artikelin ekini alır; Genitiv eril ve nötr hariç: -en.",
    "Like der, die, das, except the genitive (dessen, deren) and the dative plural (denen).": "der, die, das gibi; Genitiv (dessen, deren) ve Dativ çoğul (denen) hariç.",
    "Genitive forms (meiner, deiner...) are rare today.": "Genitiv biçimleri (meiner, deiner...) bugün nadirdir.",
    "Dative when the sentence has another object: Ich wasche mir die Hände.": "Cümlede başka nesne varsa Dativ: Ich wasche mir die Hände.",
    "Always accusative": "Her zaman Akkusativ", "Always dative": "Her zaman Dativ", "Always genitive": "Her zaman Genitiv",
    "Verbs with the dative": "Dativ alan fiiller", "Two-way: wohin? accusative, wo? dative": "İki yönlü: wohin? Akkusativ, wo? Dativ",
}

# Templates: "{}" matches anything; {1}, {2} put the (re-translated) matches back.
PATTERNS = [
    ("The preposition {} always takes the {}.", "{1} edatı her zaman {2} ister."),
    ("{} is one of the verbs that take the dative, not the accusative.", "{1}, Akkusativ değil Dativ alan fiillerden biridir."),
    ("{} takes a direct object in the accusative.", "{1}, nesnesini Akkusativ'de alır."),
    ("{} is a two-way preposition.", "{1} iki yönlü bir edattır."),
    ("{} is a two-way preposition: accusative for movement to a place (wohin?), dative for a location (wo?).",
     "{1} iki yönlü bir edattır: bir yere hareket (wohin?) Akkusativ, bir konum (wo?) Dativ ister."),
    ("An exception to the pattern: {}", "Kalıbın bir istisnası: {1}"),
    ("In the accusative only the masculine changes, so the {} looks like the nominative.", "Akkusativ'de yalnızca eril değişir, bu yüzden {1} biçim Nominativ gibi görünür."),
    ("Dative {} ends in -m.", "Dativ {1} -m ile biter."),
    ("Genitive {} ends in -s, and the noun adds -(e)s.", "Genitiv {1} -s ile biter ve isim -(e)s alır."),
    ("Genitive {} ends in -r.", "Genitiv {1} -r ile biter."),
    ("With no article the adjective carries the ending the article would have ({}).", "Artikel yoksa sıfat, artikelin alacağı eki taşır ({1})."),
    ("{} is a weak noun: it takes -(e)n in every case but the nominative.", "{1} zayıf bir isimdir: Nominativ dışındaki her hâlde -(e)n alır."),
    ("{} is a weak noun: masculine people and animals, often ending in -e, -ist or -ent, take -(e)n in every case but the nominative.",
     "{1} zayıf bir isimdir: çoğu -e, -ist veya -ent ile biten eril insan ve hayvan isimleri, Nominativ dışındaki her hâlde -(e)n alır."),
    ("{} in the {} is {}.", "{1} → {2}: {3}."),
    ("{}: accusative.", "{1}: Akkusativ."),
    ("{}: dative.", "{1}: Dativ."),
    ("Gender and number come from {} ({}).", "Cinsiyet ve sayı şuradan gelir: {1} ({2})."),
    ("The case comes from the relative clause: {}", "Hâl yan cümleden gelir: {1}"),
    ("{} (plural)", "{1} (çoğul)"),
    ("{} (my) + {}", "{1} (benim) + {2}"), ("{} (your) + {}", "{1} (senin) + {2}"), ("{} (his) + {}", "{1} (onun, erkek) + {2}"),
    ("{} (her) + {}", "{1} (onun, kadın) + {2}"), ("{} (its) + {}", "{1} (onun, şey) + {2}"), ("{} (our) + {}", "{1} (bizim) + {2}"),
    ("{} (your, plural) + {}", "{1} (sizin, hepiniz) + {2}"), ("{} (their) + {}", "{1} (onların) + {2}"),
    ("{} (your, formal) + {}", "{1} (sizin, resmî) + {2}"),
]

# Hints shown under the gaps in readings (only used for the reading "hint" field).
HINTS = {
    "the": "belirli", "a": "bir", "this": "bu", "which": "hangi", "every": "her", "no": "hiç", "my": "benim",
    "your": "senin", "our": "bizim", "his": "onun (erkek)", "her": "onun / onu (kadın)", "whose": "kimin",
    "whom": "kimi / kime", "to whom": "kime", "who": "kim", "me": "beni / bana", "you": "seni / sana",
    "myself": "kendimi / kendime", "himself": "kendini / kendine", "yourselves": "kendinizi / kendinize",
}


def _compile():
    out = []
    for en, tr_ in PATTERNS:
        rx = "(.+?)".join(re.escape(p) for p in en.split("{}"))
        out.append((re.compile("^" + rx + "$", re.S), tr_, len(en.replace("{}", ""))))
    return sorted(out, key=lambda x: -x[2])


# The Verbs course keeps its Turkish in its own file.
from .i18n_verbs import EXACT as _VERBS_EXACT, PATTERNS as _VERBS_PATTERNS  # noqa: E402

from .i18n_words import EXACT as _WORDS_EXACT, PATTERNS as _WORDS_PATTERNS  # noqa: E402

EXACT.update(_VERBS_EXACT)
EXACT.update(_WORDS_EXACT)
PATTERNS.extend(_VERBS_PATTERNS)
PATTERNS.extend(_WORDS_PATTERNS)
_PATTERNS = _compile()
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def _one(s):
    if s in EXACT:
        return EXACT[s]
    for rx, out, _n in _PATTERNS:
        m = rx.match(s)
        if m:
            groups = [tr(g) for g in m.groups()]
            return re.sub(r"\{(\d)\}", lambda k: groups[int(k.group(1)) - 1], out)
    return None


def tr(s):
    """Turkish for one English string (unchanged when there's no translation)."""
    if not isinstance(s, str) or not s.strip():
        return s
    core = s.strip()
    # Whole string first (lesson paragraphs are stored whole); otherwise sentence by sentence, so a template's
    # "{}" never swallows the sentences after it.
    done = EXACT.get(core)
    if done is None:
        parts = _SENTENCE.split(core)
        if len(parts) > 1:
            done = " ".join(_one(p) or p for p in parts)
        else:
            done = _one(core)
    if done is None:
        return s
    lead, trail = s[:len(s) - len(s.lstrip())], s[len(s.rstrip()):]
    return lead + done + trail


# ---------------------------------------------------------------------------------------------------------------
# Applying it to responses. Only the listed text fields are translated; answers, keys and choices never are.
# ---------------------------------------------------------------------------------------------------------------
TEXT_FIELDS = {"why", "cue", "label", "title", "blurb", "text", "note", "group", "front", "back", "extra", "next_step", "instr"}


def _walk(o):
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if k in TEXT_FIELDS and isinstance(v, str):
                out[k] = tr(v)
            elif k == "cols" and isinstance(v, list):
                out[k] = [tr(c) if isinstance(c, str) else c for c in v]
            elif k == "segments" and isinstance(v, list):
                out[k] = [{**seg, "hint": HINTS.get(seg["hint"].strip().lower(), seg["hint"])} if seg.get("hint") else seg for seg in v]
            elif k == "lesson" and isinstance(v, list):
                out[k] = [_lesson_block(b) for b in v]
            else:
                out[k] = _walk(v)
        return out
    if isinstance(o, list):
        return [_walk(x) for x in o]
    return o


def _lesson_block(b):
    kind = b[0]
    if kind in ("p", "h", "rule", "tip"):
        return [kind, tr(b[1]), *b[2:]]
    if kind == "ex":
        return [kind, [[de, tr(en)] for de, en in b[1]], *b[2:]]
    return list(b)


def localize(obj):
    """Translate a course/drill response when the app language is Turkish."""
    return _walk(obj) if lang() == "tr" else obj
