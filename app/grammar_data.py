"""The Grammar handbook: about 45 short topics from A1 to B1, written once and shipped as data.

Why the text is bilingual data instead of going through app/i18n.py:
i18n.py translates server text by exact English sentence (EXACT) or template (PATTERNS). That suits short drill
messages, but the handbook is long prose written for two audiences: the Turkish version is not a word-for-word
translation (it compares with Turkish where that helps), and an exact-text table would silently fall back to
English whenever one comma of the English changed. So every learner-facing string here is an (English, Turkish)
pair kept side by side, and grammar.py picks the half for the app language (`i18n.lang()`). The Turkish-speaker
note is Turkish only and is shown in both languages. German (examples, tables, mistakes) is never translated.
tests/test_grammar.py checks that every pair has both halves.

A topic:
  id, level ("A1" / "A2" / "B1"), theme (see THEMES), title (en, tr), summary (en, tr)
  keys:      extra search words (German words that should find the topic: "wegen", "dessen")
  body:      blocks: ("p", en, tr) paragraph, ("rule", en, tr) highlighted rule, ("tip", en, tr),
             ("table", {"cols": [...], "rows": [[...], ...], "caption": (en, tr) or None})
             Table cells are German strings or (en, tr) pairs. **bold** and *italic* work in all text.
  examples:  (German, English, Turkish), 4-8 of them
  mistakes:  (wrong, right, why en, why tr)
  note:      the Turkish-speaker note, in Turkish
  try:       where the "Try it" button goes (see static/js/grammar.js), or None
  skills:    skill keys (or key prefixes ending in ":") of the drills that belong to this topic: mistakes linked
             to those skills get an "Explain this" link here (see grammar.py)
  match:     a regular expression for the Mistake Book: a mistake whose topic label or explanation matches it
             is about this topic
"""
from . import decl, genderrules

THEMES = [
    ("nouns", ("Nouns and articles", "İsimler ve artikeller")),
    ("cases", ("The four cases", "Dört hâl")),
    ("pronouns", ("Pronouns and determiners", "Zamirler ve belirleyiciler")),
    ("preps", ("Prepositions", "Edatlar")),
    ("adjectives", ("Adjectives", "Sıfatlar")),
    ("verbs", ("Verbs and tenses", "Fiiller ve zamanlar")),
    ("order", ("Word order and sentences", "Kelime sırası ve cümleler")),
]
LEVELS = ["A1", "A2", "B1"]

GENDER_COLS = ["", "Maskulin", "Feminin", "Neutrum", "Plural"]


def P(en, tr):
    return ("p", en, tr)


def RULE(en, tr):
    return ("rule", en, tr)


def TIP(en, tr):
    return ("tip", en, tr)


def TABLE(cols, rows, caption=None):
    return ("table", {"cols": cols, "rows": rows, "caption": caption})


# ---------- tables built from the app's own grammar engine (decl.py), so they can never disagree ----------
def case_table(cell, caption=None, cases=decl.CASES, label=None):
    return TABLE(GENDER_COLS, [[label(c) if label else decl.CASE_NAME[c]] + [cell(c, g) for g in decl.GENDERS]
                               for c in cases], caption)


def adj_table(cls):
    det = {"w": "der / dieser", "m": "ein / mein / kein", "s": "–"}[cls]
    title = {"w": ("After der-words", "der-kelimelerinden sonra"), "m": ("After ein-words", "ein-kelimelerinden sonra"),
             "s": ("No article", "Artikelsiz")}[cls]
    return case_table(lambda c, g: "-" + decl.ADJ_END[cls][c][g], (f"{title[0]} ({det})", f"{title[1]} ({det})"))


ARTICLES = case_table(lambda c, g: decl.ARTICLE[c][g])
QUESTION = {"nom": "wer? was?", "akk": "wen? was?", "dat": "wem?", "gen": "wessen?"}


def _gender_rule_rows():
    return [[r["label"], genderrules.ARTICLE[r["g"]], (f"{r['pct']}%", f"%{r['pct']}"), ", ".join(r["ex"]),
             ", ".join(r["exceptions"]) or "–"] for r in genderrules.RULES]


def _wo(german):
    """A sentence from the word order practice (wordorder.py) with its translations, so they stay the same."""
    from .wordorder import SENTENCES
    for s in SENTENCES:
        full = " ".join(s["chunks"]) + s["end"]
        if full == german:
            return (full, s["en"], s["tr"])
    raise KeyError(german)


def T(id, level, theme, title, summary, body, examples, mistakes, note, try_=None, keys="", skills=(), match=None):
    return {"id": id, "level": level, "theme": theme, "title": title, "summary": summary, "body": body,
            "examples": examples, "mistakes": mistakes, "note": note, "try": try_, "keys": keys,
            "skills": list(skills), "match": match}


DECL = "decl"
VERBS = "verbs"


def drill(view, focus, cases=None):
    return {"view": view, "sub": "drill", "focus": focus, "cases": cases}


def order(*rules):
    return {"view": VERBS, "sub": "order", "rules": list(rules)}


TOPICS = [
    # ================================================================== nouns and articles
    T("gender", "A1", "nouns", ("Gender: der, die, das", "Cinsiyet: der, die, das"),
      ("Every German noun is masculine (der), feminine (die) or neuter (das). Learn each noun with its article.",
       "Her Almanca isim eril (der), dişil (die) ya da nötrdür (das). Her ismi artikeliyle öğrenin."),
      [P("German nouns have a grammatical gender. It belongs to the word, not to the thing: *das Mädchen* (the girl) "
         "is neuter, *der Tisch* (the table) is masculine. Natural gender helps with people (*der Mann, die Frau*), but "
         "most nouns simply have to be learned with their article.",
         "Almanca isimlerin dilbilgisel bir cinsiyeti vardır. Bu, şeyin değil kelimenin özelliğidir: *das Mädchen* (kız) "
         "nötr, *der Tisch* (masa) erildir. İnsanlarda doğal cinsiyet yardımcı olur (*der Mann, die Frau*), ama isimlerin "
         "çoğu artikeliyle birlikte öğrenilmelidir."),
       TABLE(GENDER_COLS, [[("the", "belirli"), "der", "die", "das", "die"], [("a / an", "bir"), "ein", "eine", "ein", "–"],
                           [("no, not a", "hiç, yok"), "kein", "keine", "kein", "keine"],
                           [("pronoun", "zamir"), "er", "sie", "es", "sie"]]),
       RULE("In the plural the article is always *die*, whatever the gender of the singular.",
            "Çoğulda artikel, tekilin cinsiyeti ne olursa olsun, her zaman *die*'dir."),
       P("Compound nouns take the gender of their **last** part: *das Haus + die Tür = **die** Haustür*.",
         "Birleşik isimler **son** parçalarının cinsiyetini alır: *das Haus + die Tür = **die** Haustür*."),
       TIP("The pronoun follows the grammatical gender: *Wo ist der Schlüssel? – **Er** ist in der Tasche.*",
           "Zamir dilbilgisel cinsiyeti izler: *Wo ist der Schlüssel? – **Er** ist in der Tasche.*")],
      [("Der Tisch ist neu.", "The table is new.", "Masa yeni."),
       ("Die Lampe ist kaputt.", "The lamp is broken.", "Lamba bozuk."),
       ("Das Buch liegt hier.", "The book is lying here.", "Kitap burada duruyor."),
       ("Die Bücher liegen hier.", "The books are lying here.", "Kitaplar burada duruyor."),
       ("Wo ist der Schlüssel? – Er ist in der Tasche.", "Where is the key? – It's in the bag.", "Anahtar nerede? – Çantada."),
       ("Die Haustür ist offen.", "The front door is open.", "Dış kapı açık.")],
      [("die Tisch", "der Tisch", "The meaning doesn't tell you the gender: learn every noun with its article.",
        "Anlam cinsiyeti söylemez: her ismi artikeliyle öğrenin."),
       ("das Haustür", "die Haustür", "A compound takes the gender of its last part (die Tür).",
        "Birleşik isim son parçasının cinsiyetini alır (die Tür)."),
       ("Der Schlüssel? Es ist hier.", "Der Schlüssel? Er ist hier.", "der Schlüssel → er, even for a thing.",
        "der Schlüssel → er, eşya olsa bile.")],
      "Türkçede dilbilgisel cinsiyet yoktur; 'o' hem erkek hem kadın hem de eşya için kullanılır. Almancada ise her "
      "ismin bir artikeli vardır ve bu artikel cümlede sürekli değişir. Bu yüzden kelimeyi tek başına değil, artikeliyle "
      "birlikte ezberleyin: 'masa' değil, 'der Tisch'. Renk kodu gibi görsel ipuçları (der mavi, die kırmızı, das yeşil) "
      "çok işe yarar. Türkçedeki 'bir' hiç değişmezken Almancadaki ein/eine de cinsiyete göre değişir.",
      {"view": DECL, "sub": "nouns", "mode": "gender"}, keys="Genus Artikel der die das Geschlecht",
      skills=["gender:"], match=r"\bgender|\bgenus\b|der/die/das"),

    T("gender-rules", "A1", "nouns", ("Guessing der, die, das from the ending", "Sondan der, die, das tahmini"),
      ("Endings and word groups predict the gender of almost half of all nouns: -ung is die, -chen is das, days are der.",
       "Ekler ve kelime grupları isimlerin neredeyse yarısının cinsiyetini gösterir: -ung die, -chen das, günler der."),
      [P("You can't always predict the gender, but endings and word groups get you surprisingly far. In the app's "
         "dictionary, **44%** of the 8,500 common nouns are covered by one of the rules below. The percentage says how "
         "often the rule is right.",
         "Cinsiyeti her zaman tahmin edemezsiniz, ama ekler ve kelime grupları sizi şaşırtıcı derecede ileri götürür. "
         "Uygulamanın sözlüğündeki 8.500 yaygın ismin **%44**'ü aşağıdaki kurallardan birine uyar. Yüzde, kuralın ne "
         "sıklıkla doğru olduğunu gösterir."),
       TABLE([("Rule", "Kural"), ("Article", "Artikel"), ("Right", "Doğruluk"), ("Examples", "Örnekler"),
              ("Exceptions", "İstisnalar")], _gender_rule_rows()),
       RULE("Safest bets: -ung, -heit, -keit, -schaft, -ion, -tät are *die*; -chen and -lein are *das*; -ismus and -ling "
            "are *der*.",
            "En güvenli kurallar: -ung, -heit, -keit, -schaft, -ion, -tät *die*; -chen ve -lein *das*; -ismus ve -ling "
            "*der*."),
       TIP("In the der/die/das drill the app tells you after every answer which rule predicts the noun, and counts "
           "which rules you have mastered.",
           "der/die/das alıştırmasında uygulama her cevaptan sonra ismi hangi kuralın öngördüğünü söyler ve hangi "
           "kuralları öğrendiğinizi sayar.")],
      [("die Zeitung, die Freiheit, die Information", "the newspaper, freedom, the information", "gazete, özgürlük, bilgi"),
       ("das Mädchen, das Brötchen", "the girl, the bread roll", "kız, küçük ekmek"),
       ("der Tourismus, der Frühling", "tourism, spring", "turizm, ilkbahar"),
       ("das Museum, das Zentrum", "the museum, the centre", "müze, merkez"),
       ("der Lehrer, der Fahrer", "the teacher, the driver", "öğretmen, sürücü"),
       ("der Montag, der Mai, der Regen", "Monday, May, the rain", "pazartesi, mayıs, yağmur")],
      [("das Information", "die Information", "-ion is feminine.", "-ion dişildir."),
       ("die Mädchen (one girl)", "das Mädchen", "-chen is always neuter, even for a girl.",
        "-chen her zaman nötrdür, bir kız için bile."),
       ("die Name", "der Name", "Most -e nouns are feminine, but not all: der Name, der Käse, das Auge.",
        "-e ile bitenlerin çoğu dişildir ama hepsi değil: der Name, der Käse, das Auge.")],
      "Türkçede -lık, -cı, -lı gibi ekler kelimenin türünü değiştirir ama cinsiyet belirtmez. Almancada ise bazı son ekler "
      "cinsiyeti neredeyse kesin olarak gösterir. Güzel bir köprü: Türkçedeki -lık/-lik eki Almancada çoğu zaman "
      "-heit, -keit veya -ung karşılığıdır ve bunların hepsi die'dir: özgürlük = die Freiheit, olasılık = die "
      "Möglichkeit, hazırlık = die Vorbereitung. Türkçedeki ünlü uyumunda olduğu gibi, burada da kelimenin sonuna "
      "bakarak doğru biçimi seçersiniz.",
      {"view": DECL, "sub": "nouns", "mode": "gender"},
      keys="Endung Genusregel -ung -heit -keit -schaft -ion -tät -chen -lein -ismus -ling -ment -um",
      match=r"gender rule|ending.*gender|noun ending"),

    T("plural", "A1", "nouns", ("Plural forms", "Çoğul biçimler"),
      ("German has about six plural patterns. Learn every noun with its plural: der Tisch, die Tische.",
       "Almancada yaklaşık altı çoğul kalıbı vardır. Her ismi çoğuluyla öğrenin: der Tisch, die Tische."),
      [P("The plural ending often depends on the gender, but there are many exceptions, so learn the plural together "
         "with the noun. The article in the plural is always *die*.",
         "Çoğul eki çoğu zaman cinsiyete bağlıdır ama istisnası çoktur; bu yüzden çoğulu isimle birlikte öğrenin. "
         "Çoğulda artikel her zaman *die*'dir."),
       TABLE([("Pattern", "Kalıp"), ("Typical for", "Tipik olarak"), ("Examples", "Örnekler")], [
           ["-e", ("many masculine nouns", "birçok eril isim"), "der Tisch → die Tische, der Tag → die Tage"],
           [("umlaut + -e", "Umlaut + -e"), ("short masculine nouns", "kısa eril isimler"), "der Stuhl → die Stühle, die Hand → die Hände"],
           ["-(e)n", ("almost all feminine nouns", "dişil isimlerin neredeyse hepsi"), "die Frau → die Frauen, die Lampe → die Lampen"],
           [("-er (+ umlaut)", "-er (+ Umlaut)"), ("many neuter nouns", "birçok nötr isim"), "das Kind → die Kinder, das Buch → die Bücher"],
           [("no ending (+ umlaut)", "eksiz (+ Umlaut)"), ("-er, -el, -en, -chen, -lein", "-er, -el, -en, -chen, -lein"),
            "der Lehrer → die Lehrer, der Vater → die Väter, das Mädchen → die Mädchen"],
           ["-s", ("words from other languages, words ending in a vowel", "yabancı kökenli ve ünlüyle biten kelimeler"),
            "das Auto → die Autos, das Hotel → die Hotels"],
           ["-nen", ("female people in -in", "-in ile biten kadın kişi isimleri"), "die Lehrerin → die Lehrerinnen"]]),
       RULE("In the dative plural the noun adds **-n**: *mit den Kinder**n***, unless it already ends in -n or -s.",
            "Dativ çoğulda isme **-n** eklenir: *mit den Kinder**n***; zaten -n veya -s ile bitiyorsa eklenmez.")],
      [("Ich habe zwei Brüder.", "I have two brothers.", "İki erkek kardeşim var."),
       ("Die Kinder spielen im Garten.", "The children are playing in the garden.", "Çocuklar bahçede oynuyor."),
       ("Wir brauchen drei Stühle.", "We need three chairs.", "Üç sandalyeye ihtiyacımız var."),
       ("Die Lehrerinnen sind nett.", "The (female) teachers are nice.", "Kadın öğretmenler nazik."),
       ("Ich spiele mit den Kindern.", "I'm playing with the children.", "Çocuklarla oynuyorum.")],
      [("zwei Kind", "zwei Kinder", "After a number above one the noun is plural.",
        "Birden büyük bir sayıdan sonra isim çoğul olur."),
       ("die Autoen", "die Autos", "Words ending in a vowel like Auto take -s.", "Auto gibi ünlüyle biten kelimeler -s alır."),
       ("mit den Kinder", "mit den Kindern", "The dative plural adds -n.", "Dativ çoğulda -n eklenir.")],
      "Türkçede çoğul tek bir ekle yapılır: -ler/-lar. Almancada ise yaklaşık altı farklı kalıp vardır ve hangisinin "
      "geleceği çoğu zaman tahmin edilemez; bu yüzden her ismi tekil ve çoğuluyla öğrenin: der Tisch, die Tische. Önemli "
      "bir fark: Türkçede sayıdan sonra isim tekil kalır (iki kitap), Almancada çoğul olur (zwei Bücher). Çoğulda artikel "
      "her zaman die'dir; tıpkı Türkçedeki çoğul ekinin cinsiyete bakmaması gibi.",
      {"view": DECL, "sub": "nouns", "mode": "plural"}, keys="Plural Mehrzahl -en -er -s",
      skills=["plural:", "noun:dat:pl"], match=r"\bplural"),

    T("ein-kein", "A1", "nouns", ("ein and kein", "ein ve kein"),
      ("ein means a/an and has no plural; kein (no, not a) works like ein and has a plural.",
       "ein 'bir' demektir ve çoğulu yoktur; kein ('hiç ... yok') ein gibi çekimlenir ve çoğulu vardır."),
      [P("*ein* is the indefinite article. It has no plural: *ein Buch → Bücher*. Its negative is *kein*, which takes the "
         "same endings and also has a plural: *keine Bücher*.",
         "*ein* belirsiz artikeldir ve çoğulu yoktur: *ein Buch → Bücher*. Olumsuzu *kein*'dir; aynı ekleri alır ve "
         "çoğulu da vardır: *keine Bücher*."),
       case_table(lambda c, g: decl.det_form("ein", "kein", c, g) if g == "pl"
                  else decl.det_form("ein", "ein", c, g) + " / " + decl.det_form("ein", "kein", c, g)),
       RULE("Masculine and neuter nominative have **no ending**: *ein Tisch, ein Buch*. That's why an adjective after "
            "*ein* has to show the gender: *ein neu**er** Tisch*.",
            "Eril ve nötr Nominativ'de **ek yoktur**: *ein Tisch, ein Buch*. Bu yüzden *ein*'dan sonraki sıfat cinsiyeti "
            "göstermek zorundadır: *ein neu**er** Tisch*.")],
      [("Ich habe einen Bruder.", "I have a brother.", "Bir erkek kardeşim var."),
       ("Das ist eine gute Idee.", "That's a good idea.", "Bu iyi bir fikir."),
       ("Wir haben kein Auto.", "We don't have a car.", "Arabamız yok."),
       ("Er hat keine Zeit.", "He has no time.", "Vakti yok."),
       ("Ich trinke keinen Kaffee.", "I don't drink coffee.", "Kahve içmem."),
       ("Hast du Geschwister? – Nein, ich habe keine.", "Do you have brothers or sisters? – No, I don't.", "Kardeşin var mı? – Hayır, yok.")],
      [("Ich habe ein Bruder.", "Ich habe einen Bruder.", "haben takes the accusative: masculine ein → einen.",
        "haben Akkusativ ister: eril ein → einen."),
       ("Ich habe nicht ein Auto.", "Ich habe kein Auto.", "Negate a noun with ein (or no article) with kein, not nicht ein.",
        "ein'lı ya da artikelsiz bir ismi nicht ein ile değil, kein ile olumsuzlayın."),
       ("Ich bin ein Lehrer.", "Ich bin Lehrer.", "Jobs and nationalities after sein usually have no article.",
        "sein'dan sonra meslek ve milliyetler genellikle artikelsiz söylenir.")],
      "Türkçede 'bir' belirsizlik bildirir ve hiç değişmez: bir adam, bir kadın, bir çocuk. Almancada ein cinsiyete ve "
      "hâle göre ek alır: ein Mann, eine Frau, einen Mann. 'Var/yok' yapısı da farklıdır: 'Arabam yok' Almancada 'Ich "
      "habe kein Auto' olur, yani 'yok' isme bağlanan kein ile söylenir. Meslek söylerken Türkçedeki gibi artikelsiz "
      "konuşun: 'Öğretmenim' = Ich bin Lehrer (ein yok).",
      drill(DECL, ["ein"]), keys="ein eine einen einem kein keine keinen unbestimmter Artikel",
      skills=["ein:"], match=r"indefinite article|unbestimmte|\bkein"),

    T("n-decl", "B1", "nouns", ("Weak nouns (n-declension)", "Zayıf isimler (n-Deklination)"),
      ("A group of masculine nouns adds -(e)n in every case except the nominative: den Studenten, dem Kollegen.",
       "Bazı eril isimler Nominativ dışındaki her hâlde -(e)n alır: den Studenten, dem Kollegen."),
      [P("A small group of masculine nouns adds **-(e)n in every case except the nominative singular**. Most are male "
         "people or animals: *der Student, der Kollege, der Junge, der Mensch, der Nachbar, der Löwe*.",
         "Küçük bir eril isim grubu **Nominativ tekil dışındaki her hâlde -(e)n** alır. Çoğu erkek insan veya hayvan "
         "ismidir: *der Student, der Kollege, der Junge, der Mensch, der Nachbar, der Löwe*."),
       TABLE(["", "Singular", "Plural"], [["Nominativ", "der Kollege", "die Kollegen"], ["Akkusativ", "den Kollegen", "die Kollegen"],
                                          ["Dativ", "dem Kollegen", "den Kollegen"], ["Genitiv", "des Kollegen", "der Kollegen"]]),
       RULE("How to spot them: masculine and ending in **-e** (der Kunde), **-ist** (der Polizist), **-ent** (der Student), "
            "**-ant** (der Praktikant), plus a few words like *der Mensch, der Herr, der Nachbar, der Bär*.",
            "Nasıl tanınır: eril ve **-e** (der Kunde), **-ist** (der Polizist), **-ent** (der Student), **-ant** "
            "(der Praktikant) ile biter; ayrıca *der Mensch, der Herr, der Nachbar, der Bär* gibi birkaç kelime."),
       TIP("*Herr* takes -n in the singular and -en in the plural: *Herrn Müller, meine Herren*. A few add -ns in the "
           "genitive: *des Namens, des Gedankens*.",
           "*Herr* tekilde -n, çoğulda -en alır: *Herrn Müller, meine Herren*. Birkaçı Genitiv'de -ns alır: "
           "*des Namens, des Gedankens*.")],
      [("Ich kenne den Studenten.", "I know the student.", "Öğrenciyi tanıyorum."),
       ("Kannst du dem Kollegen helfen?", "Can you help the colleague?", "İş arkadaşına yardım edebilir misin?"),
       ("Das ist das Auto des Nachbarn.", "That's the neighbour's car.", "Bu komşunun arabası."),
       ("Ich habe Herrn Schmidt angerufen.", "I called Mr Schmidt.", "Bay Schmidt'i aradım."),
       ("Der Junge spielt mit einem Hasen.", "The boy is playing with a rabbit.", "Çocuk bir tavşanla oynuyor.")],
      [("Ich sehe den Student.", "Ich sehe den Studenten.", "Student is a weak noun: -en outside the nominative.",
        "Student zayıf bir isimdir: Nominativ dışında -en alır."),
       ("mit dem Herr", "mit dem Herrn", "Herr adds -n in the singular.", "Herr tekilde -n alır."),
       ("der Name des Kunde", "der Name des Kunden", "Weak nouns take -n in the genitive, not -s.",
        "Zayıf isimler Genitiv'de -s değil -n alır.")],
      "Türkçede ismin kendisi hâl eki alır (öğrenci-yi, öğrenci-ye), Almancada ise genellikle yalnızca artikel değişir. "
      "n-Deklination bu kuralın istisnasıdır: burada isim de, tıpkı Türkçedeki gibi, ek alır: den Student-en "
      "(öğrenci-yi), dem Student-en (öğrenci-ye). Fark şu ki Almancada bu ek bütün hâllerde aynıdır (-en); Türkçedeki "
      "gibi her hâl için ayrı bir ek yoktur.",
      drill(DECL, ["noun"]), keys="n-Deklination schwache Nomen Student Kollege Herrn Herr Mensch Junge",
      skills=["noun:akk:weak", "noun:dat:weak", "noun:gen:weak"], match=r"weak noun|n-deklination|n-declension"),

    # ================================================================== cases
    T("cases", "A1", "cases", ("The four cases", "Dört hâl"),
      ("Case shows a noun's job in the sentence, mostly on the article: der (subject), den (object), dem (receiver), des (owner).",
       "Hâl, ismin cümledeki görevini çoğunlukla artikelde gösterir: der (özne), den (nesne), dem (alıcı), des (sahip)."),
      [P("German shows what a noun does in the sentence (subject, object, receiver, owner) with **case**. The case "
         "shows up mainly on the article: *der Mann* (subject), *den Mann* (object), *dem Mann* (to the man), *des Mannes* "
         "(of the man).",
         "Almanca, ismin cümlede ne yaptığını (özne, nesne, alıcı, sahip) **hâl** ile gösterir. Hâl daha çok artikelde "
         "görünür: *der Mann* (özne), *den Mann* (nesne), *dem Mann* (adama), *des Mannes* (adamın)."),
       case_table(lambda c, g: decl.ARTICLE[c][g], label=lambda c: f"{decl.CASE_NAME[c]} ({QUESTION[c]})"),
       P("Three things decide the case: the noun's **role** (subject → Nominativ, direct object → Akkusativ, indirect "
         "object → Dativ), a **preposition** (*mit* → Dativ, *für* → Akkusativ), or a **verb** that demands one "
         "(*helfen* → Dativ).",
         "Hâli üç şey belirler: ismin **görevi** (özne → Nominativ, nesne → Akkusativ, dolaylı nesne → Dativ), bir "
         "**edat** (*mit* → Dativ, *für* → Akkusativ) ya da belirli bir hâl isteyen bir **fiil** (*helfen* → Dativ)."),
       RULE("Find the verb, then ask: who does it? (Nominativ) Who or what is it done to? (Akkusativ) To or for whom? (Dativ)",
            "Önce fiili bulun, sonra sorun: Kim yapıyor? (Nominativ) Kimi, neyi? (Akkusativ) Kime? (Dativ)"),
       TIP("After *sein, werden, bleiben* the noun stays nominative: *Das ist **der** Lehrer.*",
           "*sein, werden, bleiben*'dan sonra isim Nominativ kalır: *Das ist **der** Lehrer.*")],
      [("Der Mann gibt dem Kind den Ball.", "The man gives the child the ball.", "Adam çocuğa topu veriyor."),
       ("Den Ball gibt der Mann dem Kind.", "The man gives the ball to the child (the ball is stressed).", "Topu adam çocuğa veriyor."),
       ("Das ist das Auto des Lehrers.", "That's the teacher's car.", "Bu öğretmenin arabası."),
       ("Ich fahre mit dem Bus.", "I'm going by bus.", "Otobüsle gidiyorum."),
       ("Das Geschenk ist für den Vater.", "The present is for the father.", "Hediye baba için.")],
      [("Ich sehe der Mann.", "Ich sehe den Mann.", "The direct object is accusative: der → den.",
        "Nesne Akkusativ'dedir: der → den."),
       ("Ich helfe den Mann.", "Ich helfe dem Mann.", "helfen takes the dative.", "helfen Dativ ister."),
       ("Das ist den Lehrer.", "Das ist der Lehrer.", "After sein the noun is nominative.", "sein'dan sonra isim Nominativ'dir.")],
      "Türkçede de hâl vardır, hem de Almancadan fazla: yalın (adam), belirtme (adamı), yönelme (adama), bulunma (adamda), "
      "ayrılma (adamdan), ilgi (adamın). Kabaca: Nominativ ≈ yalın hâl, Akkusativ ≈ -(y)i hâli, Dativ ≈ -(y)e hâli, "
      "Genitiv ≈ -(n)in hâli. İki büyük fark var: Almancada hâl ismin sonuna değil, önündeki artikele eklenir (den Mann = "
      "adam-ı); ve -de/-den Almancada ayrı birer hâl değildir, edatlarla söylenir (in dem Haus = evde, aus dem Haus = "
      "evden). Türkçedeki gibi hâl, kimin ne yaptığını gösterdiği için Almancada da kelime sırası esnektir: Den Ball "
      "gibt der Mann dem Kind.",
      drill(DECL, ["def"]), keys="Kasus Fall Nominativ Akkusativ Dativ Genitiv der den dem des",
      skills=["def:nom:"], match=r"nominativ|nominative"),

    T("accusative", "A1", "cases", ("Akkusativ: the direct object", "Akkusativ: nesne"),
      ("The direct object is accusative. Only the masculine changes: der → den, ein → einen.",
       "Nesne Akkusativ'dedir. Yalnızca eril değişir: der → den, ein → einen."),
      [P("The accusative marks the **direct object**: the person or thing the action is done to. Ask *wen?* (whom?) or "
         "*was?* (what?).",
         "Akkusativ **nesneyi** gösterir: eylemin yapıldığı kişi veya şey. *wen?* (kimi?) veya *was?* (neyi?) diye sorun."),
       case_table(lambda c, g: decl.ARTICLE[c][g] + " · " + (decl.det_form("ein", "ein", c, g) if g != "pl" else "–"),
                  cases=("nom", "akk")),
       RULE("Only the masculine changes: der → **den**, ein → **einen**, kein → **keinen**, mein → **meinen**, "
            "er → **ihn**.",
            "Yalnızca eril değişir: der → **den**, ein → **einen**, kein → **keinen**, mein → **meinen**, er → **ihn**."),
       P("The accusative also comes after *durch, für, gegen, ohne, um*, after *es gibt* (there is), and in time "
         "expressions without a preposition: *jeden Tag, nächsten Monat*.",
         "Akkusativ ayrıca *durch, für, gegen, ohne, um*'dan sonra, *es gibt*'ten (vardır) sonra ve edatsız zaman "
         "ifadelerinde kullanılır: *jeden Tag, nächsten Monat*.")],
      [("Ich kaufe einen Tisch.", "I'm buying a table.", "Bir masa alıyorum."),
       ("Siehst du den Hund?", "Do you see the dog?", "Köpeği görüyor musun?"),
       ("Wir besuchen unseren Opa.", "We're visiting our grandpa.", "Dedemizi ziyaret ediyoruz."),
       ("Es gibt einen Park in der Nähe.", "There's a park nearby.", "Yakında bir park var."),
       ("Ich kenne ihn gut.", "I know him well.", "Onu iyi tanıyorum."),
       ("Nächsten Monat fliege ich nach Izmir.", "Next month I'm flying to Izmir.", "Gelecek ay İzmir'e uçuyorum.")],
      [("Ich habe ein Hund.", "Ich habe einen Hund.", "haben takes an accusative object: masculine ein → einen.",
        "haben'ın nesnesi Akkusativ'dedir: eril ein → einen."),
       ("Es gibt ein Park.", "Es gibt einen Park.", "es gibt is followed by the accusative.", "es gibt'ten sonra Akkusativ gelir."),
       ("Ich liebe er.", "Ich liebe ihn.", "The pronoun changes too: er → ihn.", "Zamir de değişir: er → ihn.")],
      "Akkusativ, Türkçedeki belirtme hâline (-ı, -i, -u, -ü) çok benzer: 'Köpeği görüyorum' = Ich sehe den Hund. Ama "
      "dikkat: Türkçede belirsiz nesne ek almaz ('bir köpek gördüm'), Almancada ise belirsiz nesne de Akkusativ'dedir: "
      "Ich sehe einen Hund. Yani 'Türkçede ek yoksa Akkusativ de yok' diye düşünmeyin; nesne her zaman Akkusativ'dir. "
      "'Var' anlamındaki es gibt de Akkusativ ister: Es gibt einen Park (bir park var).",
      drill(DECL, ["def", "dies", "ein", "poss"], ["akk"]), keys="Akkusativ Akk den einen ihn wen es gibt",
      skills=["def:akk:", "noun:akk:"], match=r"akkusativ|accusative|direct object"),

    T("dative", "A1", "cases", ("Dativ: the receiver", "Dativ: alıcı"),
      ("The indirect object (to whom?) is dative, and so is everything after mit, von, zu, bei and verbs like helfen.",
       "Dolaylı nesne (kime?) Dativ'dedir; mit, von, zu, bei'den ve helfen gibi fiillerden sonra gelenler de."),
      [P("The dative marks the **indirect object**, usually a person who receives something or benefits from it. Ask "
         "*wem?* (to whom?).",
         "Dativ **dolaylı nesneyi** gösterir; genellikle bir şeyi alan veya ondan yararlanan kişidir. *wem?* (kime?) "
         "diye sorun."),
       case_table(lambda c, g: decl.ARTICLE[c][g] + " · " + (decl.det_form("ein", "ein", c, g) if g != "pl" else "–"),
                  cases=("dat",)),
       RULE("Dative signals: **-m, -r, -m, -n**. In the plural the noun adds -n too: *mit den Freunde**n***.",
            "Dativ sinyalleri: **-m, -r, -m, -n**. Çoğulda isim de -n alır: *mit den Freunde**n***."),
       P("The dative also comes after *aus, bei, mit, nach, seit, von, zu* and after verbs like *helfen, danken, "
         "gefallen, gehören, antworten, gratulieren, schmecken*.",
         "Dativ ayrıca *aus, bei, mit, nach, seit, von, zu*'dan ve *helfen, danken, gefallen, gehören, antworten, "
         "gratulieren, schmecken* gibi fiillerden sonra gelir.")],
      [("Ich gebe dem Kind ein Eis.", "I'm giving the child an ice cream.", "Çocuğa bir dondurma veriyorum."),
       ("Das Buch gehört meiner Schwester.", "The book belongs to my sister.", "Kitap kız kardeşime ait."),
       ("Kannst du mir helfen?", "Can you help me?", "Bana yardım edebilir misin?"),
       ("Der Film gefällt uns.", "We like the film.", "Film hoşumuza gidiyor."),
       ("Ich wohne bei meinen Eltern.", "I live with my parents.", "Ailemin yanında oturuyorum."),
       ("Wie geht es dir?", "How are you?", "Nasılsın?")],
      [("mit der Bus", "mit dem Bus", "mit always takes the dative: der Bus → dem Bus.", "mit her zaman Dativ ister: der Bus → dem Bus."),
       ("Ich helfe dich.", "Ich helfe dir.", "helfen takes the dative.", "helfen Dativ ister."),
       ("Ich gefalle den Film.", "Der Film gefällt mir.", "With gefallen the thing you like is the subject; you are dative.",
        "gefallen'da beğenilen şey öznedir; beğenen kişi Dativ'dedir.")],
      "Dativ çoğu zaman Türkçedeki yönelme hâline (-a, -e) karşılık gelir: Ich gebe dem Kind ein Eis = Çocuğ-a dondurma "
      "veriyorum. Bazı fiillerde Türkçe mantığı doğrudan işe yarar: helfen (birine yardım etmek), danken (birine teşekkür "
      "etmek), antworten (birine cevap vermek). gefallen tam olarak 'hoşuna gitmek' gibidir: Der Film gefällt mir = Film "
      "hoşuma gidiyor; beğenilen şey öznedir. Ama dikkat: bulunma bildiren -de de Almancada çoğu zaman Dativ'dir (in dem "
      "Haus = evde); yani Dativ hem -e hem -de işini görür.",
      drill(DECL, ["def", "dies", "ein", "poss"], ["dat"]), keys="Dativ Dat dem einem mir dir ihm wem helfen gefallen gehören",
      skills=["def:dat:", "trig:v:"], match=r"\bdativ|\bdative|indirect object"),

    T("genitive", "A2", "cases", ("Genitiv: whose?", "Genitiv: kimin?"),
      ("The genitive shows who something belongs to: das Auto des Vaters. Masculine and neuter nouns add -(e)s.",
       "Genitiv bir şeyin kime ait olduğunu gösterir: das Auto des Vaters. Eril ve nötr isimler -(e)s alır."),
      [P("The genitive shows possession: *das Auto **des** Vater**s*** (the father's car). Masculine and neuter nouns add "
         "**-s** or **-es**. In everyday speech *von* + dative often replaces it: *das Auto von meinem Vater*.",
         "Genitiv aitlik gösterir: *das Auto **des** Vater**s*** (babanın arabası). Eril ve nötr isimler **-s** veya "
         "**-es** alır. Günlük konuşmada yerine çoğu zaman *von* + Dativ kullanılır: *das Auto von meinem Vater*."),
       case_table(lambda c, g: decl.ARTICLE[c][g] + " · " + (decl.det_form("ein", "ein", c, g) if g != "pl" else "–"),
                  cases=("gen",)),
       RULE("Names take just -s, with no apostrophe: *Annas Buch, Peters Auto*.",
            "Özel isimler yalnızca -s alır, kesme işareti yoktur: *Annas Buch, Peters Auto*."),
       P("Written German also uses the genitive after *wegen, trotz, während, statt* (see Prepositions with the genitive).",
         "Yazı dilinde *wegen, trotz, während, statt*'tan sonra da Genitiv kullanılır (Genitiv alan edatlara bakın).")],
      [("Das ist das Haus meines Bruders.", "That's my brother's house.", "Bu erkek kardeşimin evi."),
       ("Die Farbe des Autos gefällt mir.", "I like the colour of the car.", "Arabanın rengi hoşuma gidiyor."),
       ("Das ist Lisas Fahrrad.", "That's Lisa's bike.", "Bu Lisa'nın bisikleti."),
       ("Am Ende des Tages war ich müde.", "At the end of the day I was tired.", "Günün sonunda yorgundum."),
       ("Die Kinder der Nachbarin spielen draußen.", "The neighbour's children are playing outside.", "Komşu kadının çocukları dışarıda oynuyor.")],
      [("Lisa's Fahrrad", "Lisas Fahrrad", "No apostrophe before the genitive -s.", "Genitiv -s'inden önce kesme işareti konmaz."),
       ("das Auto des Vater", "das Auto des Vaters", "Masculine and neuter nouns add -(e)s in the genitive.",
        "Eril ve nötr isimler Genitiv'de -(e)s alır."),
       ("die Tasche der Frau's", "die Tasche der Frau", "Feminine nouns add nothing in the genitive.",
        "Dişil isimler Genitiv'de ek almaz.")],
      "Genitiv, Türkçedeki ilgi hâline (-ın, -in) benzer, ama sıra terstir: Türkçede sahip önce gelir (babanın arabası), "
      "Almancada sonra (das Auto des Vaters, kelimesi kelimesine 'araba babanın'). Türkçedeki iyelik eki (-sı) Almancada "
      "yoktur. Özel isimlerle sıra Türkçedeki gibidir: Lisas Fahrrad = Lisa'nın bisikleti, ama Almancada kesme işareti "
      "kullanılmaz. Konuşmada Genitiv yerine çoğu zaman von + Dativ duyarsınız: das Auto von meinem Vater.",
      drill(DECL, ["def", "dies", "ein", "poss"], ["gen"]), keys="Genitiv des eines wessen -s Besitz",
      skills=["def:gen:", "noun:gen:m", "noun:gen:n"], match=r"genitiv|genitive|possession"),

    # ================================================================== pronouns and determiners
    T("pronouns", "A1", "pronouns", ("Personal pronouns", "Şahıs zamirleri"),
      ("ich, mich, mir: personal pronouns change with the case. Sie (capital S) is the polite 'you'.",
       "ich, mich, mir: şahıs zamirleri hâle göre değişir. Sie (büyük S) kibar 'siz'dir."),
      [TABLE(["", "Nominativ", "Akkusativ", "Dativ"], [[v[0].split(" (")[0], v[1], v[2], v[3]] for v in decl.PERSONS.values()]),
       P("*Sie* with a capital S is the polite 'you' for one or more people. It takes the same verb form as *sie* "
         "(they): *Sie kommen*. Use *du* with friends, family and children, *ihr* for several of them.",
         "Büyük S ile yazılan *Sie*, bir veya birkaç kişi için kibar 'siz'dir; *sie* (onlar) ile aynı fiil biçimini "
         "alır: *Sie kommen*. Arkadaşlara, aileye ve çocuklara *du*, birkaçına birden *ihr* denir."),
       RULE("Pronouns follow the noun's grammatical gender: *der Löffel → er*, *die Gabel → sie*, *das Messer → es*.",
            "Zamirler ismin dilbilgisel cinsiyetini izler: *der Löffel → er*, *die Gabel → sie*, *das Messer → es*.")],
      [("Ich rufe dich morgen an.", "I'll call you tomorrow.", "Yarın seni ararım."),
       ("Gib mir bitte das Salz.", "Please pass me the salt.", "Bana tuzu verir misin lütfen?"),
       ("Wir besuchen euch am Sonntag.", "We'll visit you on Sunday.", "Pazar günü sizi ziyaret ederiz."),
       ("Kennen Sie ihn?", "Do you know him?", "Onu tanıyor musunuz?"),
       ("Der Kuchen ist lecker. Ich esse ihn gern.", "The cake is tasty. I like eating it.", "Pasta lezzetli. Onu severek yerim."),
       ("Ich danke Ihnen.", "Thank you (formal).", "Size teşekkür ederim.")],
      [("Ich gebe dich das Buch.", "Ich gebe dir das Buch.", "The receiver is dative: dir.", "Alıcı Dativ'dedir: dir."),
       ("Der Tisch ist alt. Es ist ...", "Der Tisch ist alt. Er ist ...", "der Tisch → er.", "der Tisch → er."),
       ("Haben sie Zeit, Frau Müller?", "Haben Sie Zeit, Frau Müller?", "Polite Sie is always written with a capital S.",
        "Kibar Sie her zaman büyük harfle yazılır.")],
      "Türkçede özne zamiri çoğu zaman düşer, çünkü fiil eki kişiyi gösterir: 'Geliyorum.' Almancada özne zamiri neredeyse "
      "hiç düşmez: Ich komme. Ayrıca Türkçedeki tek 'o'ya karşılık Almancada er, sie, es vardır ve eşyalar için de "
      "kullanılır. Kibar 'siz' Almancada Sie'dir (büyük S), çoğul 'siz' ise ihr. Nesne zamirleri Türkçedeki hâl ekleri "
      "gibidir: mich = beni, mir = bana; dich = seni, dir = sana; ihn = onu, ihm = ona.",
      drill(DECL, ["pers"]), keys="Personalpronomen ich mich mir du dich dir er ihn ihm uns euch ihnen Ihnen Sie duzen siezen",
      skills=["pers:"], match=r"personal pronoun|personalpronomen|object pronoun|subject pronoun"),

    T("possessives", "A1", "pronouns", ("Possessives: mein, dein, sein ...", "İyelik: mein, dein, sein ..."),
      ("The owner picks the word (er → sein, sie → ihr); the thing owned picks the ending, like ein.",
       "Sahip kelimeyi seçer (er → sein, sie → ihr); ait olan şey eki belirler, tıpkı ein gibi."),
      [TABLE([("Owner", "Sahip"), ("Possessive", "İyelik"), ("Meaning", "Anlam")],
             [["ich", "mein", ("my", "benim")], ["du", "dein", ("your", "senin")], ["er", "sein", ("his", "onun (erkek)")],
              ["sie", "ihr", ("her", "onun (kadın)")], ["es", "sein", ("its", "onun (nötr)")], ["wir", "unser", ("our", "bizim")],
              ["ihr", "euer", ("your (plural)", "sizin (hepiniz)")], ["sie", "ihr", ("their", "onların")],
              ["Sie", "Ihr", ("your (formal)", "sizin (kibar)")]]),
       RULE("Two steps: the **owner** picks the word (*Tom → sein, Anna → ihr*); the **thing owned** picks the ending, "
            "exactly like *ein*: *mein Bruder, meine Schwester, mit meinem Bruder*.",
            "İki adım: **sahip** kelimeyi seçer (*Tom → sein, Anna → ihr*); **ait olan şey** eki belirler, tıpkı *ein* "
            "gibi: *mein Bruder, meine Schwester, mit meinem Bruder*."),
       TIP("*euer* drops its second e when an ending follows: *eure Mutter, euren Vater*.",
           "*euer*, ek aldığında ikinci e'sini düşürür: *eure Mutter, euren Vater*.")],
      [("Das ist mein Bruder und das ist meine Schwester.", "This is my brother and this is my sister.", "Bu erkek kardeşim, bu da kız kardeşim."),
       ("Anna besucht ihren Vater.", "Anna is visiting her father.", "Anna babasını ziyaret ediyor."),
       ("Tom besucht seine Mutter.", "Tom is visiting his mother.", "Tom annesini ziyaret ediyor."),
       ("Wo ist euer Auto?", "Where is your car?", "Arabanız nerede?"),
       ("Wir fahren mit unseren Kindern in den Urlaub.", "We're going on holiday with our children.", "Çocuklarımızla tatile gidiyoruz."),
       ("Ist das Ihr Koffer?", "Is this your suitcase?", "Bu sizin bavulunuz mu?")],
      [("Anna besucht seinen Vater.", "Anna besucht ihren Vater.", "The owner decides the word: Anna is a she → ihr.",
        "Kelimeyi sahip belirler: Anna kadın → ihr."),
       ("Ich sehe mein Bruder.", "Ich sehe meinen Bruder.", "The ending follows the thing owned and its case: den Bruder → meinen.",
        "Ek, ait olan şeye ve hâline göre gelir: den Bruder → meinen."),
       ("euere Mutter", "eure Mutter", "euer + ending → eur-.", "euer + ek → eur-.")],
      "Türkçede iyelik ismin sonuna ek olarak gelir: kardeş-im, kardeş-in, kardeş-i. Almancada ise isimden önce ayrı bir "
      "kelime gelir: mein Bruder. Türkçedeki 'onun' için Almancada iki kelime vardır: sahip erkek veya nötrse sein, kadın "
      "veya çoğulsa ihr. 'Annesi' derken önce kimin annesi olduğunu düşünün: Tom'un annesi = seine Mutter, Anna'nın "
      "annesi = ihre Mutter. İyelik kelimesi ayrıca, ein gibi, ait olunan ismin cinsiyetine ve hâline göre ek alır.",
      drill(DECL, ["poss"]), keys="Possessivpronomen mein dein sein ihr unser euer Ihr meinen meinem",
      skills=["poss:"], match=r"possessiv"),

    T("der-words", "A2", "pronouns", ("dieser, jeder, welcher", "dieser, jeder, welcher"),
      ("dieser (this), jeder (every), welcher (which) take the endings of der, die, das.",
       "dieser (bu), jeder (her), welcher (hangi) der, die, das'ın eklerini alır."),
      [P("*dieser* (this), *jeder* (every), *welcher* (which), *mancher* (some), *jener* (that) and *alle* (all, plural) "
         "take the endings of *der, die, das*: de**r** → diese**r**, de**m** → diese**m**, da**s** → diese**s**.",
         "*dieser* (bu), *jeder* (her), *welcher* (hangi), *mancher* (bazı), *jener* (şu) ve *alle* (bütün, çoğul) "
         "*der, die, das*'ın eklerini alır: de**r** → diese**r**, de**m** → diese**m**, da**s** → diese**s**."),
       case_table(lambda c, g: decl.det_form("dies", "dies", c, g)),
       RULE("*jeder* has no plural; use *alle*: *jeder Schüler → alle Schüler*.",
            "*jeder*'in çoğulu yoktur; *alle* kullanılır: *jeder Schüler → alle Schüler*.")],
      [("Dieser Pullover ist zu teuer.", "This sweater is too expensive.", "Bu kazak çok pahalı."),
       ("Welche Farbe magst du?", "Which colour do you like?", "Hangi rengi seversin?"),
       ("Ich gehe jeden Tag spazieren.", "I go for a walk every day.", "Her gün yürüyüşe çıkarım."),
       ("In welchem Haus wohnst du?", "Which house do you live in?", "Hangi evde oturuyorsun?"),
       ("Alle Kinder spielen draußen.", "All the children are playing outside.", "Bütün çocuklar dışarıda oynuyor.")],
      [("jeder Tag (as a time)", "jeden Tag", "Time expressions without a preposition are accusative.",
        "Edatsız zaman ifadeleri Akkusativ'dedir."),
       ("diese Haus", "dieses Haus", "Neuter: das → dieses.", "Nötr: das → dieses."),
       ("jede Kinder", "alle Kinder", "jeder has no plural: use alle.", "jeder'in çoğulu yoktur: alle kullanılır.")],
      "Türkçede 'bu', 'her', 'hangi' hiç değişmez: bu ev, bu kadın, her gün. Almancada bu kelimeler artikel gibi davranır "
      "ve der, die, das'ın son harfini alır: der → dieser, die → diese, das → dieses. İyi haber: der/die/das tablosunu "
      "biliyorsanız dieser tablosunu da biliyorsunuz. Zaman ifadelerine dikkat: 'her gün' Almancada Akkusativ'dir: jeden Tag.",
      drill(DECL, ["dies"]), keys="dieser diese dieses diesen diesem jeder jeden welcher welche alle mancher jener",
      skills=["dies:"], match=r"\bdieser|\bjeder|\bwelcher|der-word"),

    T("reflexive", "A2", "pronouns", ("Reflexive verbs: sich waschen", "Dönüşlü fiiller: sich waschen"),
      ("With reflexive verbs the object is the subject itself: Ich wasche mich. Many are reflexive only in German.",
       "Dönüşlü fiillerde nesne öznenin kendisidir: Ich wasche mich. Birçoğu yalnızca Almancada dönüşlüdür."),
      [P("With reflexive verbs the object is the subject itself: *Ich wasche **mich***. Many verbs are reflexive in German "
         "but not in English: *sich freuen* (to be happy), *sich beeilen* (to hurry), *sich setzen* (to sit down), "
         "*sich erinnern* (to remember).",
         "Dönüşlü fiillerde nesne öznenin kendisidir: *Ich wasche **mich***. Birçok fiil Almancada dönüşlüdür: *sich "
         "freuen* (sevinmek), *sich beeilen* (acele etmek), *sich setzen* (oturmak), *sich erinnern* (hatırlamak)."),
       TABLE(["", "Akkusativ", "Dativ"], [["ich", "mich", "mir"], ["du", "dich", "dir"], ["er / sie / es", "sich", "sich"],
                                          ["wir", "uns", "uns"], ["ihr", "euch", "euch"], ["sie / Sie", "sich", "sich"]]),
       RULE("Use the **dative** form when the sentence already has a direct object: *Ich wasche **mir** die Hände.* Only "
            "*ich* and *du* show the difference.",
            "Cümlede zaten bir nesne varsa **Dativ** biçimi kullanılır: *Ich wasche **mir** die Hände.* Fark yalnızca "
            "*ich* ve *du*'da görünür.")],
      [("Ich freue mich auf das Wochenende.", "I'm looking forward to the weekend.", "Hafta sonunu dört gözle bekliyorum."),
       ("Setz dich bitte!", "Please sit down!", "Otur lütfen!"),
       ("Wir müssen uns beeilen.", "We have to hurry.", "Acele etmemiz lazım."),
       ("Er hat sich erkältet.", "He has caught a cold.", "Soğuk algınlığına yakalandı."),
       ("Ich putze mir die Zähne.", "I'm brushing my teeth.", "Dişlerimi fırçalıyorum."),
       ("Kannst du dir das vorstellen?", "Can you imagine that?", "Bunu hayal edebiliyor musun?")],
      [("Ich freue auf das Wochenende.", "Ich freue mich auf das Wochenende.", "sich freuen needs its reflexive pronoun.",
        "sich freuen dönüşlü zamirsiz kullanılmaz."),
       ("Ich wasche mich die Hände.", "Ich wasche mir die Hände.", "With another object (die Hände) the reflexive is dative.",
        "Başka bir nesne varsa (die Hände) dönüşlü zamir Dativ olur."),
       ("Wir treffen sich.", "Wir treffen uns.", "sich is only for er, sie, es, sie and Sie.",
        "sich yalnızca er, sie, es, sie ve Sie içindir.")],
      "Türkçede dönüşlülük çoğu zaman fiilin içindedir: yıka-n-mak, giy-in-mek, sevin-mek. Almancada ise ayrı bir zamirle "
      "söylenir: sich waschen, sich anziehen, sich freuen. Türkçedeki 'kendi' bazen yardımcı olur: Ich wasche mich = "
      "kendimi yıkıyorum. Dikkat: Türkçede dönüşlü olmayan bazı fiiller Almancada dönüşlüdür: sich beeilen (acele "
      "etmek), sich erinnern (hatırlamak), sich setzen (oturmak).",
      drill(DECL, ["refl"]), keys="Reflexivpronomen sich mich mir dich dir uns euch sich freuen sich waschen",
      skills=["refl:"], match=r"reflexiv"),

    T("relative", "B1", "pronouns", ("Relative clauses: der, die, das, dessen", "İlgi cümleleri: der, die, das, dessen"),
      ("A relative clause describes a noun: der Mann, der dort steht. Gender from the noun, case from the clause, verb at the end.",
       "İlgi cümlesi bir ismi tanımlar: der Mann, der dort steht. Cinsiyet isimden, hâl yan cümleden gelir; fiil sondadır."),
      [P("A relative clause describes a noun: *der Mann, **der** dort steht*. The relative pronoun takes its **gender and "
         "number** from the noun and its **case** from its job inside the relative clause. The verb goes to the end.",
         "İlgi cümlesi bir ismi tanımlar: *der Mann, **der** dort steht*. İlgi zamiri **cinsiyetini ve sayısını** "
         "isimden, **hâlini** ise ilgi cümlesindeki görevinden alır. Fiil sona gider."),
       case_table(lambda c, g: decl.RELATIVE[c][g]),
       RULE("It looks like *der, die, das* except in the genitive (**dessen, deren**) and the dative plural (**denen**).",
            "Genitiv (**dessen, deren**) ve Dativ çoğul (**denen**) dışında *der, die, das* gibidir."),
       TIP("A preposition goes in front of the pronoun: *die Stadt, **in der** ich wohne*.",
           "Edat zamirin önüne gelir: *die Stadt, **in der** ich wohne*.")],
      [("Das ist der Mann, der neben mir wohnt.", "That's the man who lives next to me.", "Bu, yanımda oturan adam."),
       ("Das ist die Frau, die ich gestern getroffen habe.", "That's the woman I met yesterday.", "Bu, dün tanıştığım kadın."),
       ("Der Freund, dem ich geholfen habe, ruft an.", "The friend I helped is calling.", "Yardım ettiğim arkadaş arıyor."),
       ("Das ist die Stadt, in der ich geboren bin.", "That's the city I was born in.", "Bu, doğduğum şehir."),
       ("Der Kollege, dessen Auto kaputt ist, kommt mit dem Bus.", "The colleague whose car is broken is coming by bus.",
        "Arabası bozuk olan iş arkadaşı otobüsle geliyor."),
       ("Die Kinder, denen wir helfen, sind sehr nett.", "The children we help are very nice.", "Yardım ettiğimiz çocuklar çok tatlı.")],
      [("Das ist der Mann, der ich kenne.", "Das ist der Mann, den ich kenne.", "ich is the subject; the man is the object: den.",
        "Özne ich'tir; adam nesnedir: den."),
       ("der Kollege, der sein Auto kaputt ist", "der Kollege, dessen Auto kaputt ist", "'whose' is dessen (der/das) or deren (die/plural).",
        "'-ın/-in olan' anlamında dessen (der/das) veya deren (die/çoğul) kullanılır."),
       ("..., der wohnt neben mir.", "..., der neben mir wohnt.", "The verb goes to the end of the relative clause.",
        "Fiil ilgi cümlesinin sonuna gider.")],
      "Türkçede ilgi cümlesi ismin önüne gelir ve fiil sıfat-fiile dönüşür: 'yanımda oturan adam', 'dün tanıştığım kadın'. "
      "Almancada sıra terstir: önce isim, sonra virgül, sonra ilgi zamiri, en sonda da çekimli fiil: der Mann, der neben "
      "mir wohnt. Türkçedeki -an ile -dığı ayrımı Almancada ilgi zamirinin hâliyle gösterilir: der (özne: oturan adam), "
      "den (nesne: tanıdığım adam), dem (Dativ: yardım ettiğim adam). 'Arabası bozuk olan' gibi yapılar için dessen/deren "
      "kullanılır.",
      drill(DECL, ["rel"]), keys="Relativsatz Relativpronomen der die das dessen deren denen welcher",
      skills=["rel:"], match=r"relativ"),

    # ================================================================== prepositions
    T("prep-akk", "A1", "preps", ("Prepositions with the accusative", "Akkusativ alan edatlar"),
      ("durch, für, gegen, ohne, um always take the accusative.", "durch, für, gegen, ohne, um her zaman Akkusativ ister."),
      [P("These five always take the accusative, whatever the verb is doing.",
         "Bu beş edat, fiil ne olursa olsun, her zaman Akkusativ ister."),
       TABLE([("Preposition", "Edat"), ("Meaning", "Anlam"), ("Example", "Örnek")], [
           ["durch", ("through", "içinden"), "durch den Park"],
           ["für", ("for", "için"), "für meinen Vater"],
           ["gegen", ("against; around (a time)", "-e karşı; sularında (saat)"), "gegen die Wand, gegen acht Uhr"],
           ["ohne", ("without", "-sız, -madan"), "ohne meine Brille"],
           ["um", ("around; at (a time)", "etrafında; saat ...'de"), "um den See, um acht Uhr"]]),
       TIP("Common contractions: *durchs, fürs, ums* = durch das, für das, um das.",
           "Sık görülen kaynaşmalar: *durchs, fürs, ums* = durch das, für das, um das.")],
      [("Wir gehen durch den Park.", "We're walking through the park.", "Parkın içinden yürüyoruz."),
       ("Das Geschenk ist für dich.", "The present is for you.", "Hediye senin için."),
       ("Ich trinke Kaffee ohne Milch.", "I drink coffee without milk.", "Kahveyi sütsüz içerim."),
       ("Der Film beginnt um acht Uhr.", "The film starts at eight.", "Film saat sekizde başlıyor."),
       ("Wir sitzen um den Tisch.", "We're sitting around the table.", "Masanın etrafında oturuyoruz."),
       ("Bist du für oder gegen den Plan?", "Are you for or against the plan?", "Planı destekliyor musun, yoksa karşı mısın?")],
      [("für dem Vater", "für den Vater", "für always takes the accusative.", "für her zaman Akkusativ ister."),
       ("ohne mir", "ohne mich", "ohne always takes the accusative.", "ohne her zaman Akkusativ ister.")],
      "Türkçede 'için', 'karşı' gibi edatlar ismin arkasına gelir: senin için, duvara karşı. Almancada ise önüne gelir: "
      "für dich, gegen die Wand. Türkçede 'karşı' -e hâli ister (duvar-a karşı); Almancada da her edat belirli bir hâl "
      "ister. Bu beşi her zaman Akkusativ'dir. ohne, Türkçedeki -sız ekinin karşılığıdır: ohne Milch = sütsüz.",
      drill(DECL, ["trig"], ["akk"]), keys="durch für gegen ohne um bis Präposition Akkusativ",
      skills=[], match=r"accusative preposition|präpositionen mit akkusativ|\bdurch\b|\bohne\b|\bfür\b"),

    T("prep-dat", "A1", "preps", ("Prepositions with the dative", "Dativ alan edatlar"),
      ("aus, bei, mit, nach, seit, von, zu always take the dative: mit dem Bus, zum Arzt.",
       "aus, bei, mit, nach, seit, von, zu her zaman Dativ ister: mit dem Bus, zum Arzt."),
      [TABLE([("Preposition", "Edat"), ("Meaning", "Anlam"), ("Example", "Örnek")], [
           ["aus", ("out of; from (origin)", "-den (köken, içinden)"), "aus der Türkei"],
           ["bei", ("at someone's place; near; at work", "birinin yanında, -de"), "bei meiner Tante"],
           ["mit", ("with; by (transport)", "ile"), "mit dem Bus"],
           ["nach", ("after; to (cities, countries)", "-den sonra; -e (şehir, ülke)"), "nach dem Essen, nach Berlin"],
           ["seit", ("since; for (until now)", "-den beri"), "seit einem Jahr"],
           ["von", ("from; of; by", "-den; -in"), "von meinem Freund"],
           ["zu", ("to (people, places)", "-e (kişi, yer)"), "zum Arzt, zur Schule"],
           ["gegenüber", ("opposite", "karşısında"), "gegenüber dem Bahnhof"]]),
       RULE("Contractions: *zu dem → **zum***, *zu der → **zur***, *bei dem → **beim***, *von dem → **vom***.",
            "Kaynaşmalar: *zu dem → **zum***, *zu der → **zur***, *bei dem → **beim***, *von dem → **vom***.")],
      [("Ich komme aus der Türkei.", "I come from Turkey.", "Türkiye'denim."),
       ("Wir fahren mit dem Zug nach Hamburg.", "We're going to Hamburg by train.", "Trenle Hamburg'a gidiyoruz."),
       ("Ich lerne seit einem Jahr Deutsch.", "I've been learning German for a year.", "Bir yıldır Almanca öğreniyorum."),
       ("Nach dem Essen gehen wir spazieren.", "After the meal we go for a walk.", "Yemekten sonra yürüyüşe çıkıyoruz."),
       ("Ich gehe zum Arzt.", "I'm going to the doctor.", "Doktora gidiyorum."),
       ("Das Geschenk ist von meiner Oma.", "The present is from my grandma.", "Hediye büyükannemden.")],
      [("mit den Bus", "mit dem Bus", "mit always takes the dative.", "mit her zaman Dativ ister."),
       ("Ich lerne Deutsch für ein Jahr.", "Ich lerne seit einem Jahr Deutsch.",
        "For something that started in the past and is still going on, use seit + present tense.",
        "Geçmişte başlayıp hâlâ süren şeyler için seit + şimdiki zaman kullanılır."),
       ("Ich gehe zu Hause.", "Ich gehe nach Hause.", "nach Hause = (going) home; zu Hause = at home.",
        "nach Hause = eve (gitmek); zu Hause = evde.")],
      "Bu edatların birçoğu Türkçede bir hâl ekiyle söylenir: aus der Türkei = Türkiye'den, mit dem Bus = otobüsle, seit "
      "einem Jahr = bir yıldan beri, zum Arzt = doktora. Yani Türkçede isme eklenen anlamı Almancada edat taşır ve "
      "artikel Dativ'e geçer. Çeviri yaparken dikkat: 'Bir yıldır Almanca öğreniyorum' Almancada da şimdiki zamanla "
      "söylenir: Ich lerne seit einem Jahr Deutsch.",
      drill(DECL, ["trig"], ["dat"]), keys="aus bei mit nach seit von zu gegenüber zum zur beim vom Präposition Dativ",
      skills=[], match=r"dative preposition|präpositionen mit dativ|\bmit\b|\bseit\b|\bzum\b|\bzur\b|\bbeim\b"),

    T("two-way", "A2", "preps", ("Two-way prepositions: wo or wohin?", "İki yönlü edatlar: wo mu, wohin mi?"),
      ("an, auf, hinter, in, neben, über, unter, vor, zwischen: wohin? → accusative, wo? → dative.",
       "an, auf, hinter, in, neben, über, unter, vor, zwischen: wohin? → Akkusativ, wo? → Dativ."),
      [P("Nine prepositions take the accusative **or** the dative: *an, auf, hinter, in, neben, über, unter, vor, "
         "zwischen*. Movement to a new place (*wohin?*, where to?) → accusative. A location (*wo?*, where?) → dative.",
         "Dokuz edat Akkusativ **ya da** Dativ alır: *an, auf, hinter, in, neben, über, unter, vor, zwischen*. Yeni bir "
         "yere hareket (*wohin?*, nereye?) → Akkusativ. Bir konum (*wo?*, nerede?) → Dativ."),
       TABLE([("Verbs", "Fiiller"), "wohin? + Akkusativ", "wo? + Dativ"], [
           ["stellen / stehen", "Ich stelle die Vase auf den Tisch.", "Die Vase steht auf dem Tisch."],
           ["legen / liegen", "Ich lege das Buch auf das Sofa.", "Das Buch liegt auf dem Sofa."],
           ["setzen / sitzen", "Ich setze mich neben den Mann.", "Ich sitze neben dem Mann."],
           ["hängen / hängen", "Ich hänge das Bild an die Wand.", "Das Bild hängt an der Wand."],
           ["gehen / sein", "Ich gehe in die Küche.", "Ich bin in der Küche."]]),
       RULE("Contractions: *in dem → **im***, *an dem → **am***, *in das → **ins***, *an das → **ans***.",
            "Kaynaşmalar: *in dem → **im***, *an dem → **am***, *in das → **ins***, *an das → **ans***."),
       TIP("For time, *in, an, vor* take the dative: *im Sommer, am Montag, vor einer Woche*.",
           "Zaman bildirirken *in, an, vor* Dativ alır: *im Sommer, am Montag, vor einer Woche*.")],
      [("Wir gehen ins Kino.", "We're going to the cinema.", "Sinemaya gidiyoruz."),
       ("Wir sind im Kino.", "We're at the cinema.", "Sinemadayız."),
       ("Die Katze springt auf das Sofa.", "The cat jumps onto the sofa.", "Kedi kanepeye zıplıyor."),
       ("Die Katze schläft auf dem Sofa.", "The cat is sleeping on the sofa.", "Kedi kanepede uyuyor."),
       ("Häng die Jacke an die Garderobe!", "Hang your jacket on the coat rack!", "Ceketini askılığa as!"),
       ("Vor einer Woche war ich in Wien.", "A week ago I was in Vienna.", "Bir hafta önce Viyana'daydım.")],
      [("Ich gehe in der Küche.", "Ich gehe in die Küche.", "Movement to a place (wohin?) takes the accusative.",
        "Bir yere hareket (wohin?) Akkusativ ister."),
       ("Das Buch liegt auf den Tisch.", "Das Buch liegt auf dem Tisch.", "liegen is a location (wo?): dative.",
        "liegen bir konumdur (wo?): Dativ."),
       ("Ich lege das Buch auf dem Tisch.", "Ich lege das Buch auf den Tisch.", "legen puts something somewhere: accusative.",
        "legen bir şeyi bir yere koymaktır: Akkusativ.")],
      "Bu konu Türkçe konuşanlar için aslında kolaydır, çünkü Türkçe aynı ayrımı hâl ekleriyle yapar: 'mutfağa gidiyorum' "
      "(-e, yönelme) = Ich gehe in die Küche (Akkusativ); 'mutfaktayım' (-de, bulunma) = Ich bin in der Küche (Dativ). "
      "Kural (bu dokuz edat için): Türkçede -e diyorsanız Akkusativ, -de diyorsanız Dativ. Bir istisnaya dikkat: "
      "ankommen ('varmak') Türkçede -e alsa da Dativ ister: Wir kommen im Hotel an (otele varıyoruz). Fiil çiftleri de Türkçedeki gibi ayrılır: koymak / "
      "durmak (stellen / stehen), yatırmak / yatmak (legen / liegen), oturtmak / oturmak (setzen / sitzen).",
      drill(DECL, ["trig"]), keys="Wechselpräpositionen an auf hinter in neben über unter vor zwischen wo wohin im ins am ans stellen stehen legen liegen",
      skills=["trig:w:"], match=r"two-way|wechselpr|wo.{0,4}wohin|\bwohin\b"),

    T("prep-gen", "B1", "preps", ("Prepositions with the genitive: wegen, trotz, während",
                                  "Genitiv alan edatlar: wegen, trotz, während"),
      ("wegen (because of), trotz (despite), während (during), statt (instead of) take the genitive in written German.",
       "wegen (yüzünden), trotz (rağmen), während (sırasında), statt (yerine) yazı dilinde Genitiv ister."),
      [P("*wegen, trotz, während, statt/anstatt, innerhalb, außerhalb* take the genitive in written German. In speech "
         "you'll often hear the dative after *wegen* and *trotz*: *wegen dem Wetter*.",
         "*wegen, trotz, während, statt/anstatt, innerhalb, außerhalb* yazı dilinde Genitiv ister. Konuşmada *wegen* ve "
         "*trotz*'tan sonra sık sık Dativ duyarsınız: *wegen dem Wetter*."),
       TABLE([("Preposition", "Edat"), ("Meaning", "Anlam"), ("Example", "Örnek")], [
           ["wegen", ("because of", "yüzünden, -den dolayı"), "wegen des Wetters"],
           ["trotz", ("despite", "-e rağmen"), "trotz des Regens"],
           ["während", ("during", "sırasında, boyunca"), "während des Unterrichts"],
           ["statt", ("instead of", "yerine"), "statt eines Autos"],
           ["innerhalb", ("within, inside", "içinde"), "innerhalb einer Woche"],
           ["außerhalb", ("outside", "dışında"), "außerhalb der Stadt"]])],
      [("Wegen des Regens bleiben wir zu Hause.", "Because of the rain we're staying at home.", "Yağmur yüzünden evde kalıyoruz."),
       ("Trotz der Kälte gehen wir schwimmen.", "Despite the cold we're going swimming.", "Soğuğa rağmen yüzmeye gidiyoruz."),
       ("Während des Films ist er eingeschlafen.", "He fell asleep during the film.", "Film sırasında uyuyakaldı."),
       ("Statt eines Briefes schreibe ich eine E-Mail.", "Instead of a letter I'm writing an email.", "Mektup yerine e-posta yazıyorum."),
       ("Innerhalb einer Woche war alles fertig.", "Within a week everything was finished.", "Bir hafta içinde her şey hazırdı.")],
      [("wegen dem Wetter (in writing)", "wegen des Wetters", "Written German uses the genitive after wegen.",
        "Yazı dilinde wegen'den sonra Genitiv kullanılır."),
       ("Wegen ich krank bin, ...", "Weil ich krank bin, ...", "wegen is a preposition (+ noun); weil starts a clause.",
        "wegen bir edattır (+ isim); weil ise bir yan cümle başlatır.")],
      "Bu edatlar Türkçede çoğunlukla son edatlarla söylenir: wegen = yüzünden / -den dolayı, trotz = -e rağmen, während "
      "= sırasında, statt = yerine. Türkçede ismin arkasına gelirler ('yağmur yüzünden'), Almancada önüne gelir ve isim "
      "Genitiv'e geçer: wegen des Regens. wegen ile weil'i karıştırmayın: wegen + isim (yağmur yüzünden), weil + cümle "
      "(yağmur yağdığı için).",
      drill(DECL, ["trig"], ["gen"]), keys="wegen trotz während statt anstatt innerhalb außerhalb Präposition Genitiv",
      skills=[], match=r"genitive preposition|präpositionen mit genitiv|\bwegen\b|\btrotz\b|\bwährend\b|\bstatt\b"),

    T("verb-prep", "B1", "preps", ("Verbs with fixed prepositions", "Sabit edatlı fiiller"),
      ("Many verbs come with a fixed preposition that decides the case: warten auf + Akk, Angst haben vor + Dat.",
       "Birçok fiil, hâli belirleyen sabit bir edatla kullanılır: warten auf + Akk, Angst haben vor + Dat."),
      [P("Many verbs come with a fixed preposition, and that preposition decides the case. The pairing can't be guessed "
         "from English or Turkish, so learn them as a unit: *warten **auf** + Akk*.",
         "Birçok fiil sabit bir edatla kullanılır ve hâli bu edat belirler. Eşleşme İngilizceden ya da Türkçeden tahmin "
         "edilemez; bu yüzden kalıp olarak öğrenin: *warten **auf** + Akk*."),
       TABLE([("Verb", "Fiil"), ("Case", "Hâl"), ("Meaning", "Anlam")], [
           ["warten auf", "Akk", ("wait for", "-i beklemek")], ["denken an", "Akk", ("think of", "-i düşünmek")],
           ["sich freuen auf", "Akk", ("look forward to", "-i dört gözle beklemek")],
           ["sich freuen über", "Akk", ("be happy about", "-e sevinmek")],
           ["sich interessieren für", "Akk", ("be interested in", "-e ilgi duymak")],
           ["sich kümmern um", "Akk", ("take care of", "-e bakmak, ile ilgilenmek")],
           ["sich erinnern an", "Akk", ("remember", "-i hatırlamak")],
           ["sich bewerben um", "Akk", ("apply for", "-e başvurmak")],
           ["Angst haben vor", "Dat", ("be afraid of", "-den korkmak")],
           ["träumen von", "Dat", ("dream of", "-i hayal etmek")],
           ["teilnehmen an", "Dat", ("take part in", "-e katılmak")],
           ["fragen nach", "Dat", ("ask about", "-i sormak")],
           ["abhängen von", "Dat", ("depend on", "-e bağlı olmak")],
           ["sprechen mit / über", "Dat / Akk", ("talk to / about", "ile / hakkında konuşmak")]]),
       RULE("In these fixed pairs, *auf* and *über* almost always take the accusative.",
            "Bu sabit kalıplarda *auf* ve *über* neredeyse her zaman Akkusativ ister.")],
      [("Ich warte auf den Bus.", "I'm waiting for the bus.", "Otobüsü bekliyorum."),
       ("Wir freuen uns auf die Ferien.", "We're looking forward to the holidays.", "Tatili dört gözle bekliyoruz."),
       ("Sie interessiert sich für Kunst.", "She's interested in art.", "Sanata ilgi duyuyor."),
       ("Hast du Angst vor Hunden?", "Are you afraid of dogs?", "Köpeklerden korkar mısın?"),
       ("Er denkt oft an seine Familie.", "He often thinks of his family.", "Sık sık ailesini düşünüyor."),
       ("Das hängt vom Wetter ab.", "That depends on the weather.", "Bu havaya bağlı.")],
      [("Ich warte für den Bus.", "Ich warte auf den Bus.", "warten goes with auf.", "warten, auf ile kullanılır."),
       ("Ich interessiere mich an Musik.", "Ich interessiere mich für Musik.", "sich interessieren goes with für.",
        "sich interessieren, für ile kullanılır."),
       ("Ich habe Angst von Hunden.", "Ich habe Angst vor Hunden.", "Angst haben goes with vor + dative.",
        "Angst haben, vor + Dativ ile kullanılır.")],
      "Türkçede fiil, nesnesinin hangi hâl ekini alacağını belirler: bir şey-i beklemek, bir şey-e ilgi duymak, bir "
      "şey-den korkmak. Almancada aynı işi sabit bir edat görür: warten auf, sich interessieren für, Angst haben vor. "
      "Türkçedeki eke bakarak tahmin etmeyin; eşleşme rastgeledir ('-den korkmak' vor ile söylenir, von ile değil). Bu "
      "fiilleri edat ve hâlle birlikte tek bir kalıp olarak öğrenin: warten auf + Akk.",
      None, keys="warten auf denken an sich freuen auf über sich interessieren für Angst haben vor träumen von teilnehmen an Präpositionalverben",
      match=r"verbs? with (fixed )?preposition|präpositionalverb|verb.{0,10}\+ ?preposition|fixed preposition"),

    T("da-wo", "B1", "preps", ("da- and wo- words: darauf, worauf", "da- ve wo- kelimeleri: darauf, worauf"),
      ("For things, preposition + pronoun becomes da(r)- + preposition (darauf); questions use wo(r)- (worauf?).",
       "Eşyalar için edat + zamir da(r)- + edat olur (darauf); sorularda wo(r)- kullanılır (worauf?)."),
      [P("For things and ideas (not people), a preposition + pronoun becomes **da(r)- + preposition**: *auf das → "
         "darauf*, *mit dem → damit*. Questions about things use **wo(r)-**: *Worauf wartest du?* An -r- is added before a "
         "vowel: *dar-an, wor-über*.",
         "Eşyalar ve fikirler için (insanlar için değil) edat + zamir **da(r)- + edat** olur: *auf das → darauf*, "
         "*mit dem → damit*. Eşyalar hakkındaki sorularda **wo(r)-** kullanılır: *Worauf wartest du?* Ünlüden önce "
         "-r- eklenir: *dar-an, wor-über*."),
       TABLE([("Preposition", "Edat"), ("Thing: da-", "Eşya: da-"), ("Question: wo-", "Soru: wo-"), ("Person", "Kişi")], [
           ["auf", "darauf", "worauf?", "auf wen? – auf ihn"], ["an", "daran", "woran?", "an wen? – an sie"],
           ["mit", "damit", "womit?", "mit wem? – mit ihm"], ["über", "darüber", "worüber?", "über wen? – über ihn"],
           ["für", "dafür", "wofür?", "für wen? – für dich"], ["von", "davon", "wovon?", "von wem? – von ihr"]]),
       RULE("People keep preposition + pronoun: *Ich warte auf **ihn**.* Things use da-: *Ich warte **darauf**.*",
            "İnsanlar için edat + zamir kalır: *Ich warte auf **ihn**.* Eşyalar için da- kullanılır: *Ich warte **darauf**.*")],
      [("Worauf wartest du? – Auf den Bus.", "What are you waiting for? – The bus.", "Neyi bekliyorsun? – Otobüsü."),
       ("Auf wen wartest du? – Auf meine Schwester.", "Who are you waiting for? – My sister.", "Kimi bekliyorsun? – Kız kardeşimi."),
       ("Ich freue mich schon darauf.", "I'm already looking forward to it.", "Şimdiden dört gözle bekliyorum."),
       ("Womit fährst du zur Arbeit?", "How do you get to work?", "İşe neyle gidiyorsun?"),
       ("Wir haben lange darüber gesprochen.", "We talked about it for a long time.", "Bunun hakkında uzun uzun konuştuk."),
       ("Denk daran, die Tür abzuschließen!", "Remember to lock the door!", "Kapıyı kilitlemeyi unutma!")],
      [("Ich freue mich auf es.", "Ich freue mich darauf.", "For things use da- + preposition, not preposition + es.",
        "Eşyalar için edat + es değil, da- + edat kullanılır."),
       ("Auf was wartest du?", "Worauf wartest du?", "auf was is common in speech, but worauf is the standard form.",
        "auf was konuşmada yaygındır, ama standart biçim worauf'tur."),
       ("Ich warte darauf. (on a friend)", "Ich warte auf ihn.", "For people, keep preposition + pronoun.",
        "İnsanlar için edat + zamir kullanılır.")],
      "Türkçede 'onu beklemek', 'onunla gitmek' derken insan mı eşya mı olduğuna bakmayız. Almancada bakarız: insan için "
      "edat + zamir (auf ihn, mit ihr), eşya ve fikirler için da- kelimesi (darauf, damit). Soru kelimelerinde de aynı "
      "ayrım vardır: Auf wen? (kimi?) ama Worauf? (neyi?). Türkçedeki 'neyle', 'ne hakkında' gibi soruları womit, "
      "worüber diye düşünebilirsiniz.",
      None, keys="darauf daran damit darüber dafür davon worauf woran womit worüber wofür wovon Pronominaladverb",
      match=r"da-(word|compound)|wo-(word|compound)|pronominaladverb|\bdarauf\b|\bworauf\b|\bdarüber\b|\bworüber\b"),

    # ================================================================== adjectives
    T("adj-endings", "A2", "adjectives", ("Adjective endings: the system", "Sıfat ekleri: sistem"),
      ("An adjective before a noun takes an ending. Which one depends on what comes in front: a der-word, an ein-word, or nothing.",
       "İsimden önceki sıfat ek alır. Hangi ek olduğu önündeki kelimeye bağlıdır: der-kelimesi, ein-kelimesi ya da hiçbiri."),
      [P("An adjective **after** the noun (after *sein, werden, bleiben*) has no ending: *Der Tisch ist neu.* An adjective "
         "**before** the noun always has one: *der neu**e** Tisch*. Which ending depends on what stands in front of it: "
         "a der-word, an ein-word, or nothing.",
         "İsimden **sonra** gelen sıfat (*sein, werden, bleiben*'dan sonra) ek almaz: *Der Tisch ist neu.* İsimden "
         "**önce** gelen sıfat her zaman ek alır: *der neu**e** Tisch*. Hangi ekin geleceği önündeki kelimeye bağlıdır: "
         "der-kelimesi, ein-kelimesi ya da hiçbiri."),
       RULE("One idea explains all three tables: **the gender and case must be shown once**. If the article already shows "
            "it (*der, dem*), the adjective takes a plain -e or -en. If it doesn't (*ein*, no article), the adjective shows "
            "it with the article's own ending.",
            "Üç tabloyu tek bir fikir açıklar: **cinsiyet ve hâl bir kez gösterilmeli**. Artikel zaten gösteriyorsa "
            "(*der, dem*), sıfat sade -e veya -en alır. Göstermiyorsa (*ein*, artikelsiz), bilgiyi sıfat artikelin kendi "
            "ekiyle taşır."),
       adj_table("w"), adj_table("m"), adj_table("s"),
       TIP("Shortcut: after any article, the dative, the genitive and the plural always take **-en**.",
           "Kısa yol: herhangi bir artikelden sonra Dativ, Genitiv ve çoğul her zaman **-en** alır.")],
      [("Der neue Kollege ist nett.", "The new colleague is nice.", "Yeni iş arkadaşı nazik."),
       ("Ein neuer Kollege kommt morgen.", "A new colleague is coming tomorrow.", "Yarın yeni bir iş arkadaşı geliyor."),
       ("Frischer Kaffee riecht gut.", "Fresh coffee smells good.", "Taze kahve güzel kokar."),
       ("Mit dem neuen Auto fahren wir nach Italien.", "We're driving to Italy in the new car.", "Yeni arabayla İtalya'ya gidiyoruz."),
       ("Das Auto ist neu.", "The car is new.", "Araba yeni.")],
      [("Das ist ein neue Auto.", "Das ist ein neues Auto.", "ein shows no gender, so the adjective must: -es.",
        "ein cinsiyeti göstermez, bu yüzden sıfat göstermeli: -es."),
       ("Der Tisch ist neuer.", "Der Tisch ist neu.", "After sein the adjective has no ending (neuer would mean 'newer').",
        "sein'dan sonra sıfat ek almaz (neuer 'daha yeni' demek olur)."),
       ("mit dem neue Auto", "mit dem neuen Auto", "Dative after an article: always -en.", "Artikelden sonra Dativ: her zaman -en.")],
      "Türkçede sıfat hiç değişmez: yeni masa, yeni masayı, yeni masaya. Almancada ise isimden önceki sıfat; artikele, "
      "cinsiyete ve hâle göre ek alır: der neue Tisch, den neuen Tisch, dem neuen Tisch. İşin sırrı şu: cinsiyet ve hâl "
      "bilgisi bir kez gösterilmeli. Artikel gösteriyorsa (der, dem) sıfat sade -e/-en alır; göstermiyorsa (ein, "
      "artikelsiz) bilgiyi sıfat taşır: ein neuer Tisch. Sıfat isimden sonra gelirse, Türkçedeki gibi değişmez: Der Tisch "
      "ist neu.",
      drill(DECL, ["adjw", "adjm", "adjs"]), keys="Adjektivendungen Adjektivdeklination -e -en -er -es -em",
      skills=[], match=r"adjective ending|adjektivendung|adjektivdeklination|adjective declension"),

    T("adj-der", "A2", "adjectives", ("Adjective endings after der-words", "der-kelimelerinden sonra sıfat ekleri"),
      ("After der, dieser, jeder: only -e or -en. Five slots take -e, all the rest -en.",
       "der, dieser, jeder'den sonra: yalnızca -e veya -en. Beş yerde -e, geri kalan her yerde -en."),
      [P("After *der, die, das, dieser, jeder, welcher, alle*, the article already shows the case, so the adjective takes "
         "only **-e** or **-en**.",
         "*der, die, das, dieser, jeder, welcher, alle*'den sonra hâli artikel zaten gösterir; sıfat yalnızca **-e** "
         "veya **-en** alır."),
       adj_table("w"),
       RULE("Only five slots take **-e**: the three nominative singulars (*der neue Tisch, die neue Lampe, das neue Bild*) "
            "and the feminine and neuter accusative (*die neue Lampe, das neue Bild*). Everything else: **-en**.",
            "Yalnızca beş yerde **-e** vardır: üç tekil Nominativ (*der neue Tisch, die neue Lampe, das neue Bild*) ile "
            "dişil ve nötr Akkusativ (*die neue Lampe, das neue Bild*). Geri kalan her yerde: **-en**.")],
      [("Der alte Mann wartet.", "The old man is waiting.", "Yaşlı adam bekliyor."),
       ("Ich kaufe den roten Pullover.", "I'm buying the red sweater.", "Kırmızı kazağı alıyorum."),
       ("Wir wohnen in dem kleinen Haus.", "We live in the small house.", "Küçük evde oturuyoruz."),
       ("Die neuen Nachbarn sind freundlich.", "The new neighbours are friendly.", "Yeni komşular cana yakın."),
       ("Welches blaue Kleid meinst du?", "Which blue dress do you mean?", "Hangi mavi elbiseyi kastediyorsun?")],
      [("den rote Pullover", "den roten Pullover", "Masculine accusative after den: -en.", "den'den sonra eril Akkusativ: -en."),
       ("die neue Nachbarn", "die neuen Nachbarn", "Plural after die: -en.", "Çoğulda die'den sonra: -en.")],
      "Bu tablo üçünün en kolayıdır: yalnızca iki ek vardır, -e ve -en. Türkçede sıfat değişmediği için ilk başta garip "
      "gelebilir; kalıbı bir kez ezberleyin: tekil Nominativ'de ve dişil/nötr Akkusativ'de -e, geri kalan her yerde -en. "
      "'Beş -e, gerisi -en' diye aklınızda tutabilirsiniz.",
      drill(DECL, ["adjw"]), keys="schwache Adjektivdeklination der neue den neuen",
      skills=["adjw:"], match=r"after der-words|weak adjective|schwache"),

    T("adj-ein", "A2", "adjectives", ("Adjective endings after ein-words", "ein-kelimelerinden sonra sıfat ekleri"),
      ("After ein, kein, mein: like the der-words, but where ein has no ending the adjective shows -er or -es.",
       "ein, kein, mein'dan sonra: der-kelimeleri gibi, ama ein'ın ek almadığı yerde sıfat -er veya -es alır."),
      [P("After *ein, kein, mein, dein, sein, ihr, unser, euer* it's mostly like after der-words. But where *ein* has no "
         "ending (masculine nominative, neuter nominative and accusative) the adjective shows the gender: **-er** or **-es**.",
         "*ein, kein, mein, dein, sein, ihr, unser, euer*'den sonra durum çoğunlukla der-kelimelerindeki gibidir. Ama "
         "*ein*'ın ek almadığı yerlerde (eril Nominativ, nötr Nominativ ve Akkusativ) cinsiyeti sıfat gösterir: **-er** "
         "veya **-es**."),
       adj_table("m"),
       RULE("*ein* gives no signal, so the adjective does: ein neu**er** Tisch (like de**r**), ein neu**es** Bild (like "
            "da**s**).",
            "*ein* sinyal vermez, bu yüzden sıfat verir: ein neu**er** Tisch (de**r** gibi), ein neu**es** Bild "
            "(da**s** gibi).")],
      [("Das ist ein guter Film.", "That's a good film.", "Bu iyi bir film."),
       ("Sie hat ein neues Fahrrad.", "She has a new bike.", "Yeni bir bisikleti var."),
       ("Ich suche eine kleine Wohnung.", "I'm looking for a small flat.", "Küçük bir daire arıyorum."),
       ("Er hat keinen guten Grund.", "He has no good reason.", "İyi bir sebebi yok."),
       ("Mit meinem besten Freund gehe ich ins Kino.", "I'm going to the cinema with my best friend.", "En iyi arkadaşımla sinemaya gidiyorum."),
       ("Unsere alten Freunde besuchen uns.", "Our old friends are visiting us.", "Eski arkadaşlarımız bizi ziyaret ediyor.")],
      [("ein gute Film", "ein guter Film", "Masculine nominative after ein: the adjective shows -er.",
        "ein'dan sonra eril Nominativ: sıfat -er alır."),
       ("ein neue Fahrrad", "ein neues Fahrrad", "Neuter after ein: -es.", "ein'dan sonra nötr: -es.")],
      "Türkçedeki 'bir' gibi ein de cinsiyet göstermez, ama Almanca cinsiyetin bir yerde görünmesini ister. ein'ın eksik "
      "bıraktığı yerde sıfat devreye girer: ein guter Film (der Film → -er), ein neues Auto (das Auto → -es). Kalan "
      "yerlerde tablo der-kelimelerininkiyle aynıdır.",
      drill(DECL, ["adjm"]), keys="gemischte Adjektivdeklination ein neuer ein neues meinen guten",
      skills=["adjm:"], match=r"after ein-words|mixed adjective|gemischte"),

    T("adj-none", "B1", "adjectives", ("Adjective endings with no article", "Artikelsiz sıfat ekleri"),
      ("With no article the adjective takes the ending of der, die, das itself: kalter Tee, kalte Milch, kaltes Wasser.",
       "Artikel yoksa sıfat der, die, das'ın ekini kendisi alır: kalter Tee, kalte Milch, kaltes Wasser."),
      [P("With no article at all, the adjective takes the ending of *der, die, das* itself: kalt**er** Tee (der), kalt**e** "
         "Milch (die), kalt**es** Wasser (das). This is common with food and drink, with plurals and after numbers.",
         "Hiç artikel yoksa sıfat *der, die, das*'ın ekini kendisi alır: kalt**er** Tee (der), kalt**e** Milch (die), "
         "kalt**es** Wasser (das). Yiyecek ve içeceklerde, çoğullarda ve sayılardan sonra sık görülür."),
       adj_table("s"),
       RULE("One exception: the genitive masculine and neuter take **-en**, because the noun already shows -s: *trotz "
            "schlecht**en** Wetter**s***.",
            "Tek istisna: eril ve nötr Genitiv **-en** alır, çünkü isim zaten -s gösterir: *trotz schlecht**en** "
            "Wetter**s***.")],
      [("Ich trinke gern heißen Tee.", "I like drinking hot tea.", "Sıcak çay içmeyi severim."),
       ("Frische Milch ist gesund.", "Fresh milk is healthy.", "Taze süt sağlıklıdır."),
       ("Wir suchen nette Kollegen.", "We're looking for nice colleagues.", "Cana yakın iş arkadaşları arıyoruz."),
       ("Mit großem Interesse habe ich Ihre Anzeige gelesen.", "I read your advertisement with great interest.", "İlanınızı büyük bir ilgiyle okudum."),
       ("Liebe Anna, lieber Tom, ...", "Dear Anna, dear Tom, ...", "Sevgili Anna, sevgili Tom, ..."),
       ("Zwei kleine Kinder spielen im Hof.", "Two small children are playing in the yard.", "İki küçük çocuk avluda oynuyor.")],
      [("Ich trinke gern heiße Tee.", "Ich trinke gern heißen Tee.", "Masculine accusative: -en, like den.", "Eril Akkusativ: den gibi -en."),
       ("mit große Interesse", "mit großem Interesse", "Neuter dative: -em, like dem.", "Nötr Dativ: dem gibi -em."),
       ("Lieber Anna", "Liebe Anna", "Anna is feminine: liebe. For a man: Lieber Tom.", "Anna kadın: Liebe. Erkek için: Lieber Tom.")],
      "Artikel yoksa sıfat, artikelin yapacağı işi üstlenir ve onun son harfini alır: der → -er, dem → -em, das → -es. "
      "Mektup başlarında hemen görürsünüz: Lieber Tom (erkek), Liebe Anna (kadın), Liebe Freunde (çoğul). Türkçede hitap "
      "hiç değişmez ('Sevgili Tom', 'Sevgili Anna'); Almancada hitap edilen kişinin cinsiyeti sıfatın ekinden anlaşılır.",
      drill(DECL, ["adjs"]), keys="starke Adjektivdeklination kalter Tee lieber liebe ohne Artikel",
      skills=["adjs:"], match=r"no article|without article|strong adjective|starke|ohne artikel"),

    T("comparison", "A2", "adjectives", ("Comparative and superlative", "Karşılaştırma ve üstünlük"),
      ("schnell → schneller → am schnellsten. 'than' is als, 'as ... as' is so ... wie.",
       "schnell → schneller → am schnellsten. '-den daha' als ile, '... kadar' so ... wie ile söylenir."),
      [P("Comparative: add **-er** (*schnell → schneller*). Superlative: **am ... -sten** (*am schnellsten*), or before a "
         "noun **der/die/das ... -ste** with an adjective ending (*der schnellste Zug*). 'than' is **als**; 'as ... as' is "
         "**so ... wie**.",
         "Karşılaştırma: **-er** eklenir (*schnell → schneller*). Üstünlük: **am ... -sten** (*am schnellsten*) ya da "
         "isimden önce **der/die/das ... -ste** ve sıfat eki (*der schnellste Zug*). '-den daha' **als**, '... kadar' "
         "**so ... wie** ile söylenir."),
       TABLE([("Base", "Yalın"), ("Comparative", "Karşılaştırma"), ("Superlative", "Üstünlük")], [
           ["klein", "kleiner", "am kleinsten"], ["schnell", "schneller", "am schnellsten"], ["alt", "älter", "am ältesten"],
           ["groß", "größer", "am größten"], ["jung", "jünger", "am jüngsten"], ["teuer", "teurer", "am teuersten"],
           ["hoch", "höher", "am höchsten"], ["nah", "näher", "am nächsten"], ["gut", "besser", "am besten"],
           ["viel", "mehr", "am meisten"], ["gern", "lieber", "am liebsten"]]),
       RULE("Many short adjectives with a, o, u take an umlaut: *alt → älter, groß → größer, jung → jünger*. After -t, -d, "
            "-s, -ß, -z the superlative adds an -e-: *am ältesten, am heißesten* (exception: *am größten*).",
            "a, o, u içeren birçok kısa sıfat Umlaut alır: *alt → älter, groß → größer, jung → jünger*. -t, -d, -s, -ß, "
            "-z'den sonra üstünlükte -e- eklenir: *am ältesten, am heißesten* (istisna: *am größten*).")],
      [("Mein Bruder ist älter als ich.", "My brother is older than me.", "Abim benden büyük."),
       ("Berlin ist größer als München.", "Berlin is bigger than Munich.", "Berlin Münih'ten büyük."),
       ("Anna ist so groß wie ihre Mutter.", "Anna is as tall as her mother.", "Anna annesi kadar uzun."),
       ("Ich trinke lieber Tee als Kaffee.", "I prefer tea to coffee.", "Çayı kahveye tercih ederim."),
       ("Im Januar ist es hier am kältesten.", "It's coldest here in January.", "Burası en soğuk ocakta olur."),
       ("Das ist der beste Film des Jahres.", "That's the best film of the year.", "Bu, yılın en iyi filmi.")],
      [("älter wie ich", "älter als ich", "After a comparative, 'than' is als.", "Karşılaştırmadan sonra '-den' için als kullanılır."),
       ("mehr schnell", "schneller", "German adds -er; it doesn't use mehr with an adjective.",
        "Almancada -er eklenir; sıfatla mehr kullanılmaz."),
       ("am bestesten", "am besten", "gut is irregular: besser, am besten.", "gut düzensizdir: besser, am besten.")],
      "Türkçede karşılaştırma ayrı kelimelerle ve hâl ekiyle yapılır: 'benden daha büyük', 'en büyük'. Almancada sıfata "
      "ek gelir: größer (daha büyük), am größten (en büyük). Türkçedeki ayrılma hâli (-den) Almancada als ile söylenir: "
      "älter als ich = benden büyük. 'Kadar' için so ... wie kullanılır: so groß wie ich = benim kadar uzun. Türkçedeki "
      "'daha' kelimesini mehr diye çevirmeyin; -er eki yeterlidir.",
      None, keys="Komparativ Superlativ als wie so wie besser am besten mehr am meisten lieber",
      match=r"comparative|superlative|komparativ|superlativ|comparison|\bals\b.*\bwie\b"),

    # ================================================================== verbs and tenses
    T("present", "A1", "verbs", ("Present tense", "Şimdiki zaman (Präsens)"),
      ("Stem + -e, -st, -t, -en, -t, -en. The German present also covers 'I'm doing' and often the future.",
       "Kök + -e, -st, -t, -en, -t, -en. Almancadaki Präsens hem '-iyor' hem geniş zaman, çoğu zaman da gelecek anlamı taşır."),
      [P("Take the infinitive, remove -en (*spiel-en*) and add the personal endings. The present covers English 'I play' "
         "and 'I'm playing', and often the future: *Morgen spiele ich Tennis*.",
         "Mastardan -en'i atın (*spiel-en*) ve şahıs eklerini ekleyin. Präsens hem 'oynarım' hem 'oynuyorum' demektir, "
         "çoğu zaman da gelecek için kullanılır: *Morgen spiele ich Tennis*."),
       TABLE(["", "spielen", "arbeiten", "sein", "haben", "werden"], [
           ["ich", "spiele", "arbeite", "bin", "habe", "werde"], ["du", "spielst", "arbeitest", "bist", "hast", "wirst"],
           ["er / sie / es", "spielt", "arbeitet", "ist", "hat", "wird"], ["wir", "spielen", "arbeiten", "sind", "haben", "werden"],
           ["ihr", "spielt", "arbeitet", "seid", "habt", "werdet"], ["sie / Sie", "spielen", "arbeiten", "sind", "haben", "werden"]]),
       RULE("Stems ending in -t or -d add an -e- before -st and -t: *du arbeit**e**st, er find**e**t*.",
            "-t veya -d ile biten kökler -st ve -t'den önce -e- alır: *du arbeit**e**st, er find**e**t*.")],
      [("Ich wohne in Köln.", "I live in Cologne.", "Köln'de oturuyorum."),
       ("Was machst du gerade?", "What are you doing right now?", "Şu an ne yapıyorsun?"),
       ("Wir sind müde.", "We're tired.", "Yorgunuz."),
       ("Hast du Hunger?", "Are you hungry?", "Acıktın mı?"),
       ("Morgen arbeite ich nicht.", "I'm not working tomorrow.", "Yarın çalışmıyorum."),
       ("Seit wann wohnt ihr hier?", "How long have you lived here?", "Ne zamandır burada oturuyorsunuz?")],
      [("Ich bin spielen.", "Ich spiele.", "German has no 'am ...-ing' form; the simple present does the job.",
        "Almancada 'be + -ing' gibi bir biçim yoktur; düz Präsens yeterlidir."),
       ("du arbeitst", "du arbeitest", "Stems in -t or -d add -e-.", "-t veya -d ile biten kökler -e- alır."),
       ("ihr seit", "ihr seid", "seid (you are) is spelt with d; seit (since) is a preposition.",
        "seid ('sizsiniz') d ile yazılır; seit ('beri') bir edattır.")],
      "Türkçede olduğu gibi Almancada da kişi fiil ekiyle gösterilir: spiel-e (oynuyorum), spiel-st (oynuyorsun). Ama "
      "Almancada özne zamiri yine de söylenir: Ich spiele. Türkçedeki '-iyor' ile geniş zaman (-ir) ayrımı Almancada "
      "yoktur: Ich spiele hem 'oynuyorum' hem 'oynarım' demektir. Gelecek için de çoğu zaman Präsens kullanılır, tıpkı "
      "Türkçede 'Yarın geliyorum' dediğimiz gibi.",
      drill(VERBS, ["conj"], ["praes"]), keys="Präsens Gegenwart Konjugation sein haben werden bin bist ist sind seid",
      skills=["vb:praes:reg", "vb:praes:irr"], match=r"präsens|present tense|conjugation|konjugation"),

    T("stem-change", "A1", "verbs", ("Verbs that change their vowel", "Ünlüsü değişen fiiller"),
      ("Some verbs change their vowel in du and er/sie/es: sprechen → er spricht, fahren → er fährt.",
       "Bazı fiillerin ünlüsü du ve er/sie/es'te değişir: sprechen → er spricht, fahren → er fährt."),
      [P("Many strong verbs change their stem vowel in the **du** and **er/sie/es** forms only: e → i (*sprechen → du "
         "sprichst*), e → ie (*sehen → du siehst*), a → ä (*fahren → du fährst*), au → äu (*laufen → du läufst*).",
         "Birçok güçlü fiil kök ünlüsünü yalnızca **du** ve **er/sie/es** biçimlerinde değiştirir: e → i (*sprechen → "
         "du sprichst*), e → ie (*sehen → du siehst*), a → ä (*fahren → du fährst*), au → äu (*laufen → du läufst*)."),
       TABLE(["", "sprechen (e → i)", "sehen (e → ie)", "fahren (a → ä)", "laufen (au → äu)"], [
           ["ich", "spreche", "sehe", "fahre", "laufe"], ["du", "sprichst", "siehst", "fährst", "läufst"],
           ["er / sie / es", "spricht", "sieht", "fährt", "läuft"], ["wir", "sprechen", "sehen", "fahren", "laufen"],
           ["ihr", "sprecht", "seht", "fahrt", "lauft"], ["sie / Sie", "sprechen", "sehen", "fahren", "laufen"]]),
       RULE("*ich, wir, ihr, sie* keep the normal vowel. Other common ones: *geben (gibt), nehmen (nimmt), essen (isst), "
            "helfen (hilft), lesen (liest), schlafen (schläft), tragen (trägt)*.",
            "*ich, wir, ihr, sie* normal ünlüyü korur. Diğer yaygın örnekler: *geben (gibt), nehmen (nimmt), essen (isst), "
            "helfen (hilft), lesen (liest), schlafen (schläft), tragen (trägt)*."),
       TIP("*nehmen* changes consonants too: *du nimmst, er nimmt*. *wissen* is irregular: *ich weiß, du weißt, er weiß*.",
           "*nehmen*'de ünsüzler de değişir: *du nimmst, er nimmt*. *wissen* düzensizdir: *ich weiß, du weißt, er weiß*.")],
      [("Sprichst du Deutsch?", "Do you speak German?", "Almanca konuşuyor musun?"),
       ("Er fährt jeden Tag mit dem Rad.", "He cycles every day.", "Her gün bisikletle gidiyor."),
       ("Sie liest gern Krimis.", "She likes reading crime novels.", "Polisiye okumayı sever."),
       ("Was isst du zum Frühstück?", "What do you eat for breakfast?", "Kahvaltıda ne yersin?"),
       ("Das Kind schläft schon.", "The child is already asleep.", "Çocuk çoktan uyudu."),
       ("Nimmst du den Bus?", "Are you taking the bus?", "Otobüse mi biniyorsun?")],
      [("er sprecht", "er spricht", "sprechen changes e → i in du and er/sie/es.", "sprechen, du ve er/sie/es'te e → i olur."),
       ("ich spriche", "ich spreche", "ich never changes the vowel.", "ich'te ünlü hiç değişmez."),
       ("du fahrst", "du fährst", "fahren changes a → ä in du and er/sie/es.", "fahren, du ve er/sie/es'te a → ä olur.")],
      "Türkçede fiil kökü neredeyse hiç değişmez (git-, gel-, oku-); değişiklikler ek tarafında olur. Almancada ise bazı "
      "fiillerin kökü du ve er/sie/es'te değişir: ich spreche, ama du sprichst. Bu fiilleri er biçimiyle birlikte öğrenin: "
      "sprechen – er spricht. Sözlükteki 'er spricht' bilgisi tam da bunun içindir.",
      drill(VERBS, ["conj"], ["praes"]), keys="Vokalwechsel starke Verben spricht sieht fährt nimmt gibt isst liest läuft weiß",
      skills=["vb:praes:stem"], match=r"stem.?chang|vowel change|vokalwechsel"),

    T("separable", "A1", "verbs", ("Separable and inseparable verbs", "Ayrılabilen ve ayrılamayan fiiller"),
      ("Separable prefixes go to the end: Ich rufe dich an. Inseparable ones (be-, ver-, er-...) stay and take no ge-.",
       "Ayrılabilen ön ekler sona gider: Ich rufe dich an. Ayrılamayanlar (be-, ver-, er-...) yapışık kalır ve ge- almaz."),
      [P("Separable prefixes (*an-, auf-, aus-, ein-, mit-, zu-, vor-, zurück-, fern-* ...) are stressed and split off in "
         "main clauses: the verb is second, the prefix goes to the **end**: *Ich **rufe** dich morgen **an**.* In a "
         "subordinate clause they stay together at the end: *..., weil ich dich **anrufe***.",
         "Ayrılabilen ön ekler (*an-, auf-, aus-, ein-, mit-, zu-, vor-, zurück-, fern-* ...) vurguludur ve ana cümlede "
         "fiilden ayrılır: fiil ikinci sırada, ön ek **en sonda**: *Ich **rufe** dich morgen **an**.* Yan cümlede ise "
         "sonda bitişik kalırlar: *..., weil ich dich **anrufe***."),
       TABLE([("Form", "Biçim"), "anrufen", "verstehen"], [
           ["Präsens", "Ich rufe dich an.", "Ich verstehe dich."],
           ["Perfekt", "Ich habe dich angerufen.", "Ich habe dich verstanden."],
           [("with zu", "zu ile"), "anzurufen", "zu verstehen"],
           [("Subordinate clause", "Yan cümle"), "..., weil ich dich anrufe.", "..., weil ich dich verstehe."]]),
       RULE("Inseparable prefixes **be-, emp-, ent-, er-, ge-, miss-, ver-, zer-** never split off, are not stressed, and "
            "their Partizip II has no ge-: *besuchen → besucht, verstehen → verstanden*.",
            "Ayrılamayan ön ekler **be-, emp-, ent-, er-, ge-, miss-, ver-, zer-** hiç ayrılmaz, vurgu almaz ve Partizip "
            "II'leri ge- almaz: *besuchen → besucht, verstehen → verstanden*.")],
      [_wo("Der Zug kommt um acht Uhr in München an."), _wo("Sie steht jeden Morgen um sechs auf."),
       ("Kaufst du heute ein?", "Are you going shopping today?", "Bugün alışverişe gidiyor musun?"),
       ("Wir haben gestern ferngesehen.", "We watched TV yesterday.", "Dün televizyon izledik."),
       ("Ich verstehe die Frage nicht.", "I don't understand the question.", "Soruyu anlamıyorum."),
       ("Sie hat mich gestern besucht.", "She visited me yesterday.", "Dün beni ziyaret etti.")],
      [("Ich anrufe dich.", "Ich rufe dich an.", "In a main clause the prefix goes to the end.", "Ana cümlede ön ek sona gider."),
       ("Ich habe ihn gebesucht.", "Ich habe ihn besucht.", "be- verbs take no ge-.", "be- ile başlayan fiiller ge- almaz."),
       ("Ich habe dich angeruft.", "Ich habe dich angerufen.", "rufen is strong (gerufen), so: angerufen.",
        "rufen güçlü bir fiildir (gerufen), bu yüzden: angerufen.")],
      "Türkçe eklemeli bir dildir: anlam, köke art arda eklenen eklerle kurulur ve hepsi bitişik kalır (ara-yacağ-ım). "
      "Almancada ise ön ek fiilin başına gelir ve ana cümlede kopup en sona gider: Ich rufe dich morgen an. Cümleyi "
      "dinlerken fiilin tam anlamını ancak sonda öğrenirsiniz; bu, Türkçedeki 'asıl anlam sonda' alışkanlığınıza aslında "
      "yakındır. Ayrılamayan ön ekler (be-, ver-, er- ...) ise Türkçedeki ekler gibi hep yapışık kalır.",
      order("sep"), keys="trennbare Verben untrennbar Präfix anrufen aufstehen einkaufen fernsehen be- ver- er- ent- zer-",
      skills=["vb:praes:sep", "vb:pp:sep", "vb:pp:noge", "wo:sep"], match=r"separable|trennbar|prefix|präfix"),

    T("modal", "A1", "verbs", ("Modal verbs", "Modal fiiller"),
      ("können, müssen, dürfen, sollen, wollen, möchten: the modal is second, the other verb goes to the end.",
       "können, müssen, dürfen, sollen, wollen, möchten: modal fiil ikinci sırada, diğer fiil sonda."),
      [P("*können* (can), *müssen* (must, have to), *dürfen* (may, be allowed to), *sollen* (should, be supposed to), "
         "*wollen* (want to), *mögen* / *möchten* (like / would like). The modal is second; the other verb goes to the end "
         "as an infinitive, without *zu*.",
         "*können* (-ebilmek), *müssen* (zorunda olmak), *dürfen* (izinli olmak), *sollen* (-meli, -mesi gerekmek), "
         "*wollen* (istemek), *mögen* / *möchten* (sevmek / istemek). Modal fiil ikinci sıradadır; diğer fiil *zu* "
         "olmadan, mastar olarak sona gider."),
       TABLE(["", "können", "müssen", "dürfen", "wollen", "sollen", "möchten"], [
           ["ich", "kann", "muss", "darf", "will", "soll", "möchte"], ["du", "kannst", "musst", "darfst", "willst", "sollst", "möchtest"],
           ["er / sie / es", "kann", "muss", "darf", "will", "soll", "möchte"],
           ["wir", "können", "müssen", "dürfen", "wollen", "sollen", "möchten"],
           ["ihr", "könnt", "müsst", "dürft", "wollt", "sollt", "möchtet"],
           ["sie / Sie", "können", "müssen", "dürfen", "wollen", "sollen", "möchten"]]),
       RULE("*ich* and *er/sie/es* have the same form, with no ending: *ich kann, er kann*.",
            "*ich* ve *er/sie/es* aynı biçimi alır ve ek yoktur: *ich kann, er kann*."),
       TIP("*nicht müssen* means 'don't have to', not 'mustn't': *Du musst nicht kommen.* 'Mustn't' is *nicht dürfen*: "
           "*Hier darf man nicht rauchen.*",
           "*nicht müssen* 'gerek yok' demektir, 'yasak' değil: *Du musst nicht kommen* (gelmen gerekmiyor). Yasak için "
           "*nicht dürfen* kullanılır: *Hier darf man nicht rauchen.*")],
      [("Ich kann gut schwimmen.", "I can swim well.", "İyi yüzebilirim."), _wo("Wir müssen morgen früh aufstehen."),
       ("Darf ich das Fenster öffnen?", "May I open the window?", "Pencereyi açabilir miyim?"),
       ("Er will Arzt werden.", "He wants to become a doctor.", "Doktor olmak istiyor."),
       ("Du sollst den Arzt anrufen.", "You're supposed to call the doctor.", "Doktoru araman gerekiyor."),
       ("Ich möchte einen Kaffee, bitte.", "I'd like a coffee, please.", "Bir kahve istiyorum, lütfen.")],
      [("Ich kann zu schwimmen.", "Ich kann schwimmen.", "No zu after a modal verb.", "Modal fiilden sonra zu gelmez."),
       ("er kannt", "er kann", "No ending in er/sie/es.", "er/sie/es'te ek yoktur."),
       ("Du musst hier nicht rauchen. (meaning: forbidden)", "Du darfst hier nicht rauchen.",
        "Forbidden is nicht dürfen; nicht müssen only means there's no need.",
        "Yasak nicht dürfen ile söylenir; nicht müssen yalnızca 'gerek yok' demektir.")],
      "Türkçede yeterlilik ve zorunluluk fiile ek olarak gelir: yüz-ebil-mek, git-meli, gel-mek zorunda. Almancada bunlar "
      "ayrı fiillerdir ve ikinci sıraya geçer; asıl fiil mastar olarak cümlenin sonuna gider: Ich kann gut schwimmen = iyi "
      "yüzebilirim. Yani anlam, Türkçedeki gibi sonda tamamlanır. Dikkat: 'gitmen gerekmiyor' (nicht müssen) ile "
      "'gitmemelisin, yasak' (nicht dürfen) farklıdır.",
      {"view": VERBS, "sub": "drill", "focus": ["modsent", "conj"], "cases": ["modal"]},
      keys="Modalverben können müssen dürfen sollen wollen mögen möchten kann muss darf will soll",
      skills=["vb:modal:"], match=r"modal"),

    T("imperative", "A1", "verbs", ("Imperative: giving instructions", "Emir kipi"),
      ("Komm! (du) · Kommt! (ihr) · Kommen Sie! (Sie). bitte makes it polite.",
       "Komm! (du) · Kommt! (ihr) · Kommen Sie! (Sie). bitte kibarlaştırır."),
      [P("Three forms: **du** (the stem, no pronoun: *Komm!*), **ihr** (like the present, no pronoun: *Kommt!*), **Sie** "
         "(verb first, then Sie: *Kommen Sie!*). *bitte* makes it polite.",
         "Üç biçim vardır: **du** (kök, zamirsiz: *Komm!*), **ihr** (Präsens gibi, zamirsiz: *Kommt!*), **Sie** (önce "
         "fiil, sonra Sie: *Kommen Sie!*). *bitte* kibarlaştırır."),
       TABLE(["", "du", "ihr", "Sie"], [
           ["kommen", "Komm!", "Kommt!", "Kommen Sie!"], ["warten", "Warte!", "Wartet!", "Warten Sie!"],
           ["sprechen", "Sprich!", "Sprecht!", "Sprechen Sie!"], ["aufstehen", "Steh auf!", "Steht auf!", "Stehen Sie auf!"],
           ["sein", "Sei leise!", "Seid leise!", "Seien Sie leise!"]]),
       RULE("Verbs with e → i/ie keep the change in the du-form (*sprich, lies, nimm*); verbs with a → ä don't (*fahr!, "
            "schlaf!*).",
            "e → i/ie değişen fiiller du-biçiminde bu değişikliği korur (*sprich, lies, nimm*); a → ä değişenler korumaz "
            "(*fahr!, schlaf!*).")],
      [("Komm bitte her!", "Please come here!", "Buraya gel lütfen!"),
       ("Mach das Fenster zu!", "Close the window!", "Pencereyi kapat!"),
       ("Seid bitte leise!", "Please be quiet! (to several people)", "Lütfen sessiz olun! (birkaç kişiye)"),
       ("Nehmen Sie bitte Platz!", "Please take a seat!", "Buyurun, oturun!"),
       ("Lies den Text!", "Read the text!", "Metni oku!"),
       ("Fahr vorsichtig!", "Drive carefully!", "Dikkatli sür!")],
      [("Kommst du her!", "Komm her!", "The du-imperative drops -st and the pronoun.", "du emir kipinde -st ve zamir düşer."),
       ("Fähr langsam!", "Fahr langsam!", "a → ä verbs don't change in the imperative.", "a → ä değişen fiiller emir kipinde değişmez."),
       ("Sie kommen bitte!", "Kommen Sie bitte!", "In the Sie-imperative the verb comes first.", "Sie emir kipinde fiil başa gelir.")],
      "Türkçede emir kipi çok kolaydır: fiil kökü yeter (gel!, otur!), kibar ya da çoğul biçim için -in eklenir (gelin!, "
      "oturunuz!). Almancada da du-biçimi kökten oluşur (Komm!), ama kibar 'siz' için zamir de söylenir: Kommen Sie! "
      "Türkçedeki 'lütfen' gibi bitte de cümlenin neredeyse her yerine girebilir: Komm bitte! / Bitte komm!",
      None, keys="Imperativ Befehl komm kommt kommen Sie sei seid seien bitte", match=r"imperati"),

    T("perfekt", "A1", "verbs", ("Perfekt: haben or sein?", "Perfekt: haben mı, sein mı?"),
      ("The spoken past: haben/sein in second place + Partizip II at the end. Movement and change take sein.",
       "Konuşmadaki geçmiş zaman: ikinci sırada haben/sein + sonda Partizip II. Hareket ve değişim sein alır."),
      [P("The Perfekt is the normal spoken past: **haben** or **sein** in second place + **Partizip II** at the end: "
         "*Ich **habe** einen Film **gesehen**.*",
         "Perfekt, konuşmadaki olağan geçmiş zamandır: ikinci sırada **haben** veya **sein** + sonda **Partizip II**: "
         "*Ich **habe** einen Film **gesehen**.*"),
       RULE("Use **sein** with movement from A to B (*gehen, fahren, fliegen, kommen*), a change of state (*aufstehen, "
            "einschlafen, werden, sterben*), and *sein, bleiben, passieren*. Everything else, including every verb with an "
            "accusative object, takes **haben**.",
            "**sein**: A'dan B'ye hareket (*gehen, fahren, fliegen, kommen*), durum değişikliği (*aufstehen, "
            "einschlafen, werden, sterben*) ve *sein, bleiben, passieren*. Geri kalan her şey, Akkusativ nesnesi olan "
            "bütün fiiller de dahil, **haben** alır."),
       TABLE(["haben", "sein"], [
           ["Ich habe Pizza gegessen.", "Ich bin nach Hause gegangen."],
           ["Wir haben Fußball gespielt.", "Wir sind nach Spanien geflogen."],
           ["Er hat lange geschlafen.", "Er ist um sieben aufgestanden."],
           ["Sie hat ein Buch gelesen.", "Sie ist zu Hause geblieben."]]),
       TIP("B1: the Plusquamperfekt is the past before the past: *hatte/war* + Partizip II: *Als ich ankam, **war** der "
           "Zug schon **abgefahren***.",
           "B1: Plusquamperfekt, geçmişten de önceki zamandır: *hatte/war* + Partizip II: *Als ich ankam, **war** der "
           "Zug schon **abgefahren*** (vardığımda tren çoktan kalkmıştı).")],
      [("Ich habe gestern Deutsch gelernt.", "I studied German yesterday.", "Dün Almanca çalıştım."),
       ("Wir sind ins Kino gegangen.", "We went to the cinema.", "Sinemaya gittik."),
       ("Was hast du am Wochenende gemacht?", "What did you do at the weekend?", "Hafta sonu ne yaptın?"),
       _wo("Er ist letztes Jahr nach Kanada geflogen."),
       ("Was ist passiert?", "What happened?", "Ne oldu?"),
       ("Ich bin zu Hause geblieben.", "I stayed at home.", "Evde kaldım.")],
      [("Ich habe nach Berlin gefahren.", "Ich bin nach Berlin gefahren.", "Movement to a place: sein.", "Bir yere hareket: sein."),
       ("Ich habe gestern gesehen einen Film.", "Ich habe gestern einen Film gesehen.", "The Partizip II goes to the very end.",
        "Partizip II cümlenin en sonuna gider."),
       ("Was hat passiert?", "Was ist passiert?", "passieren takes sein.", "passieren, sein ile kullanılır.")],
      "Türkçede geçmiş zaman tek bir ekle yapılır: gördüm, gittim. Almancada konuşmadaki geçmiş zaman (Perfekt) iki "
      "parçalıdır: yardımcı fiil (haben/sein) ikinci sırada, Partizip II cümlenin en sonunda: Ich habe einen Film gesehen. "
      "Hangi yardımcı fiilin geleceğini Türkçe size söylemez; kural: bir yerden bir yere hareket veya durum değişikliği "
      "varsa sein, diğer her şeyde haben. Türkçedeki -dı ile -mış ayrımı Almancada yoktur; ikisi de çoğu zaman Perfekt "
      "ile söylenir.",
      {"view": VERBS, "sub": "drill", "focus": ["aux"]},
      keys="Perfekt Vergangenheit haben sein Hilfsverb gegangen gefahren Plusquamperfekt hatte war",
      skills=["vb:perf:aux", "vb:plusq"], match=r"perfekt|perfect tense|haben or sein|haben/sein|auxiliar|hilfsverb|plusquamperfekt"),

    T("partizip", "A2", "verbs", ("Partizip II: gemacht, gegangen", "Partizip II: gemacht, gegangen"),
      ("Weak verbs: ge- ... -t (gemacht). Strong verbs: ge- ... -en, often with a new vowel (getrunken).",
       "Zayıf fiiller: ge- ... -t (gemacht). Güçlü fiiller: ge- ... -en, çoğu zaman yeni bir ünlüyle (getrunken)."),
      [P("Weak (regular) verbs: **ge- + stem + -t**: *machen → gemacht, arbeiten → gearbeitet*. Strong verbs: **ge- + "
         "stem (often with a new vowel) + -en**: *sehen → gesehen, gehen → gegangen, trinken → getrunken*.",
         "Zayıf (düzenli) fiiller: **ge- + kök + -t**: *machen → gemacht, arbeiten → gearbeitet*. Güçlü fiiller: **ge- + "
         "kök (çoğu zaman yeni ünlüyle) + -en**: *sehen → gesehen, gehen → gegangen, trinken → getrunken*."),
       TABLE([("Type", "Tür"), ("Pattern", "Kalıp"), ("Examples", "Örnekler")], [
           [("weak", "zayıf"), "ge- … -t", "machen → gemacht, kaufen → gekauft, arbeiten → gearbeitet"],
           [("strong", "güçlü"), "ge- … -en", "sehen → gesehen, schreiben → geschrieben, trinken → getrunken"],
           [("mixed", "karışık"), ("ge- … -t, new vowel", "ge- … -t, yeni ünlü"), "bringen → gebracht, denken → gedacht, kennen → gekannt"],
           [("separable", "ayrılabilen"), ("prefix + ge + …", "ön ek + ge + …"), "einkaufen → eingekauft, anrufen → angerufen"],
           [("no ge-", "ge- yok"), "be-, ver-, er- …, -ieren", "besuchen → besucht, verstehen → verstanden, studieren → studiert"]]),
       RULE("No **ge-** after an inseparable prefix (*be-, ver-, er-, ent-, emp-, zer-, ge-, miss-*) and none for verbs in "
            "**-ieren**.",
            "Ayrılamayan bir ön ekten (*be-, ver-, er-, ent-, emp-, zer-, ge-, miss-*) sonra ve **-ieren** ile biten "
            "fiillerde **ge-** kullanılmaz.")],
      [("Ich habe die Wohnung geputzt.", "I cleaned the flat.", "Evi temizledim."),
       ("Hast du den Brief geschrieben?", "Did you write the letter?", "Mektubu yazdın mı?"),
       ("Wir haben viel gelacht.", "We laughed a lot.", "Çok güldük."),
       ("Er hat Medizin studiert.", "He studied medicine.", "Tıp okudu."),
       ("Ich habe dich nicht verstanden.", "I didn't understand you.", "Seni anlamadım."),
       ("Sie hat mir ein Geschenk mitgebracht.", "She brought me a present.", "Bana bir hediye getirdi.")],
      [("gestudiert", "studiert", "Verbs in -ieren take no ge-.", "-ieren ile biten fiiller ge- almaz."),
       ("geschreibt", "geschrieben", "schreiben is strong: ge- … -en with a new vowel.", "schreiben güçlüdür: ge- … -en ve yeni ünlü."),
       ("gebringt", "gebracht", "bringen is mixed: gebracht.", "bringen karışık bir fiildir: gebracht.")],
      "Partizip II, Türkçedeki -mış/-miş sıfat-fiiline benzer: gemacht ≈ yapılmış, gesehen ≈ görülmüş. Türkçede bu ek her "
      "fiilde düzenlidir; Almancada ise zayıf fiillerde ge-…-t, güçlü fiillerde ge-…-en kullanılır ve güçlü fiillerin "
      "ünlüsü değişebilir (trinken → getrunken). Güçlü fiilleri üç biçimiyle birlikte ezberleyin: trinken – trank – "
      "getrunken.",
      {"view": VERBS, "sub": "drill", "focus": ["pp"]}, keys="Partizip II Partizip Perfekt ge- -t -en gemacht gegangen",
      skills=["vb:pp:weak", "vb:pp:strong"], match=r"partizip|participle"),

    T("praeteritum", "A2", "verbs", ("Präteritum: the written past", "Präteritum: yazı dilindeki geçmiş"),
      ("The past of stories and news. In speech mainly war, hatte, wurde and the modal verbs: konnte, musste.",
       "Hikâyelerin ve haberlerin geçmiş zamanı. Konuşmada daha çok war, hatte, wurde ve modal fiiller: konnte, musste."),
      [P("The Präteritum is the past of stories, news and books. In speech Germans use it mainly for **sein, haben, "
         "werden** and the modal verbs: *ich war, ich hatte, ich konnte*.",
         "Präteritum; hikâyelerin, haberlerin ve kitapların geçmiş zamanıdır. Konuşmada daha çok **sein, haben, werden** "
         "ve modal fiiller için kullanılır: *ich war, ich hatte, ich konnte*."),
       TABLE(["", "sein", "haben", "können", "machen", "gehen"], [
           ["ich", "war", "hatte", "konnte", "machte", "ging"], ["du", "warst", "hattest", "konntest", "machtest", "gingst"],
           ["er / sie / es", "war", "hatte", "konnte", "machte", "ging"], ["wir", "waren", "hatten", "konnten", "machten", "gingen"],
           ["ihr", "wart", "hattet", "konntet", "machtet", "gingt"], ["sie / Sie", "waren", "hatten", "konnten", "machten", "gingen"]]),
       RULE("Weak verbs add **-te-**: *machte*. Strong verbs change the vowel: *gehen → ging, sehen → sah, kommen → kam*. "
            "*ich* and *er/sie/es* have the same form.",
            "Zayıf fiiller **-te-** alır: *machte*. Güçlü fiillerin ünlüsü değişir: *gehen → ging, sehen → sah, kommen → "
            "kam*. *ich* ve *er/sie/es* aynı biçimi alır.")],
      [("Gestern war ich krank.", "Yesterday I was ill.", "Dün hastaydım."),
       ("Wir hatten keine Zeit.", "We had no time.", "Vaktimiz yoktu."),
       ("Als Kind konnte ich nicht schwimmen.", "As a child I couldn't swim.", "Çocukken yüzme bilmiyordum."),
       ("Es war einmal ein König.", "Once upon a time there was a king.", "Bir varmış, bir yokmuş, bir kral varmış."),
       ("Er kam nach Hause und ging sofort ins Bett.", "He came home and went straight to bed.", "Eve geldi ve hemen yattı."),
       ("Musstest du lange warten?", "Did you have to wait long?", "Uzun süre beklemek zorunda kaldın mı?")],
      [("Ich habe krank gewesen.", "Ich war krank.", "For sein, the Präteritum war is the usual past (and the Perfekt takes sein: ich bin krank gewesen).",
        "sein için olağan geçmiş Präteritum'daki war'dır (Perfekt'i de sein ile kurulur: ich bin krank gewesen)."),
       ("er gingte", "er ging", "Strong verbs don't add -te.", "Güçlü fiiller -te almaz."),
       ("ich hatten", "ich hatte", "ich and er/sie/es: no ending.", "ich ve er/sie/es'te ek yoktur.")],
      "Almancada iki geçmiş zaman vardır ama aralarındaki fark Türkçedeki -dı/-mış farkı değildir; fark üsluptadır: Perfekt "
      "konuşmada, Präteritum yazıda ve hikâye anlatırken kullanılır. Masallardaki 'Es war einmal' tam olarak Türkçedeki "
      "'Bir varmış, bir yokmuş' karşılığıdır. Konuşmada bile war, hatte ile konnte, musste gibi modal biçimler "
      "Präteritum'da söylenir.",
      drill(VERBS, ["conj", "parts"], ["praet"]), keys="Präteritum Imperfekt war hatte konnte musste ging kam sah -te",
      skills=["vb:praet:", "vp:"], match=r"präteritum|prateritum|preterite|simple past|imperfekt"),

    T("future", "A2", "verbs", ("Future: werden + infinitive", "Gelecek zaman: werden + mastar"),
      ("werden in second place + infinitive at the end. Often the present with a time word is enough.",
       "İkinci sırada werden + sonda mastar. Çoğu zaman zaman bildiren bir kelimeyle Präsens yeterlidir."),
      [P("Futur I: **werden** in second place + infinitive at the end: *Ich **werde** dich **anrufen***. Often the present "
         "with a time word is enough: *Ich rufe dich morgen an*.",
         "Futur I: ikinci sırada **werden** + sonda mastar: *Ich **werde** dich **anrufen***. Çoğu zaman zaman bildiren "
         "bir kelimeyle Präsens yeterlidir: *Ich rufe dich morgen an*."),
       TABLE(["", "werden"], [["ich", "werde"], ["du", "wirst"], ["er / sie / es", "wird"], ["wir", "werden"],
                              ["ihr", "werdet"], ["sie / Sie", "werden"]]),
       RULE("Futur I also makes a guess about now: *Er **wird** krank **sein***. (He's probably ill.)",
            "Futur I şimdiki zamanla ilgili bir tahmin de bildirir: *Er **wird** krank **sein***. (Herhalde hastadır.)"),
       TIP("*werden* on its own means 'to become': *Ich werde Lehrerin.*",
           "Tek başına *werden* 'olmak' demektir: *Ich werde Lehrerin* (öğretmen oluyorum).")],
      [("Ich werde dir helfen.", "I'll help you.", "Sana yardım edeceğim."),
       ("Morgen wird es regnen.", "It's going to rain tomorrow.", "Yarın yağmur yağacak."),
       ("Wir werden sehen.", "We'll see.", "Göreceğiz."), _wo("Sie wird uns bestimmt helfen."),
       ("Sie wird wohl im Büro sein.", "She's probably at the office.", "Herhalde ofistedir."),
       ("Er wird Arzt.", "He's becoming a doctor.", "Doktor oluyor.")],
      [("Ich werde helfen dir.", "Ich werde dir helfen.", "The infinitive goes to the end.", "Mastar sona gider."),
       ("Ich will morgen kommen. (meaning: future)", "Ich werde morgen kommen.", "wollen means 'want'; the future uses werden.",
        "wollen 'istemek' demektir; gelecek zaman werden ile yapılır."),
       ("du werdest", "du wirst", "werden is irregular: du wirst, er wird.", "werden düzensizdir: du wirst, er wird.")],
      "Türkçede gelecek zaman tek bir ekle yapılır: gel-eceğ-im. Almancada werden yardımcı fiil olarak ikinci sıraya geçer "
      "ve asıl fiil mastar olarak sona gider: Ich werde kommen. Ama çoğu zaman Türkçedeki gibi şimdiki zaman da yeterlidir: "
      "'Yarın geliyorum' = Ich komme morgen. wollen'ı İngilizcedeki 'will' ile karıştırmayın: wollen 'istemek' demektir.",
      drill(VERBS, ["conj"], ["fut1"]), keys="Futur Zukunft werden wird wirst werde Futur II",
      skills=["vb:fut1", "vb:fut2"], match=r"\bfutur|future"),

    T("konj2", "B1", "verbs", ("Konjunktiv II: würde, hätte, wäre, könnte", "Konjunktiv II: würde, hätte, wäre, könnte"),
      ("For wishes, polite requests and 'if' that isn't real: würde + infinitive, or hätte, wäre, könnte.",
       "Dilekler, kibar ricalar ve gerçek olmayan şartlar için: würde + mastar ya da hätte, wäre, könnte."),
      [P("Konjunktiv II is for wishes, polite requests and situations that aren't real. Most verbs use **würde + "
         "infinitive**: *Ich **würde** gern **reisen***. *sein, haben* and the modal verbs have their own forms: *wäre, "
         "hätte, könnte, müsste, dürfte, sollte, wollte*.",
         "Konjunktiv II; dilekler, kibar ricalar ve gerçek olmayan durumlar içindir. Çoğu fiil **würde + mastar** "
         "kullanır: *Ich **würde** gern **reisen***. *sein, haben* ve modal fiillerin kendi biçimleri vardır: *wäre, "
         "hätte, könnte, müsste, dürfte, sollte, wollte*."),
       TABLE(["", "würde", "wäre", "hätte", "könnte"], [
           ["ich", "würde", "wäre", "hätte", "könnte"], ["du", "würdest", "wärst", "hättest", "könntest"],
           ["er / sie / es", "würde", "wäre", "hätte", "könnte"], ["wir", "würden", "wären", "hätten", "könnten"],
           ["ihr", "würdet", "wärt", "hättet", "könntet"], ["sie / Sie", "würden", "wären", "hätten", "könnten"]]),
       RULE("An unreal 'if': *Wenn ich Zeit **hätte**, **würde** ich dich **besuchen**.* Both parts take Konjunktiv II.",
            "Gerçek olmayan şart: *Wenn ich Zeit **hätte**, **würde** ich dich **besuchen**.* İki kısım da Konjunktiv II "
            "alır."),
       TIP("Polite requests: *Könnten Sie mir helfen? Ich hätte gern ein Wasser. Würden Sie bitte das Fenster öffnen?*",
           "Kibar ricalar: *Könnten Sie mir helfen? Ich hätte gern ein Wasser. Würden Sie bitte das Fenster öffnen?*")],
      [("Ich hätte gern einen Kaffee.", "I'd like a coffee.", "Bir kahve alabilir miyim?"),
       ("Könnten Sie das bitte wiederholen?", "Could you repeat that, please?", "Bunu tekrar edebilir misiniz lütfen?"),
       ("Wenn ich reich wäre, würde ich um die Welt reisen.", "If I were rich, I'd travel around the world.", "Zengin olsaydım dünyayı gezerdim."),
       ("An deiner Stelle würde ich zum Arzt gehen.", "If I were you, I'd go to the doctor.", "Senin yerinde olsam doktora giderdim."),
       ("Das wäre schön!", "That would be nice!", "Bu güzel olurdu!"),
       ("Du solltest mehr schlafen.", "You should sleep more.", "Daha çok uyumalısın.")],
      [("Wenn ich Zeit habe, würde ich kommen.", "Wenn ich Zeit hätte, würde ich kommen.",
        "In an unreal condition both parts take Konjunktiv II.", "Gerçek olmayan bir şartta iki kısım da Konjunktiv II alır."),
       ("Ich würde froh sein.", "Ich wäre froh.", "Use wäre and hätte rather than würde sein and würde haben.",
        "würde sein ve würde haben yerine wäre ve hätte kullanın."),
       ("Wenn ich würde Zeit haben, ...", "Wenn ich Zeit hätte, ...", "After wenn: hätte, with the verb at the end.",
        "wenn'den sonra: hätte, fiil sonda.")],
      "Türkçede dilek ve şart eklerle yapılır: gel-se, gel-ir-di, ol-sa-ydı. Almancada bu işi Konjunktiv II görür: Wenn "
      "ich Zeit hätte, würde ich kommen = Vaktim olsa gelirdim. Türkçedeki '-se' kısmı wenn-cümlesine (hätte, wäre), "
      "'-irdi' kısmı ana cümleye (würde + mastar) karşılık gelir. Kibar ricalarda da kullanılır: Könnten Sie ...? = "
      "...-ebilir misiniz? Tıpkı Türkçede olduğu gibi ricayı yumuşatır.",
      drill(VERBS, ["conj"], ["konj2"]), keys="Konjunktiv II würde hätte wäre könnte müsste sollte Irrealis wenn höflich",
      skills=["vb:konj2:"], match=r"konjunktiv|subjunctive|conditional|\bwürde\b|\bhätte\b|\bwäre\b"),

    T("passive", "B1", "verbs", ("Passive: werden + Partizip II", "Edilgen çatı: werden + Partizip II"),
      ("The passive puts the action in the centre: Das Haus wird gebaut. The doer comes with von + dative.",
       "Edilgen çatı eylemi öne çıkarır: Das Haus wird gebaut. Eylemi yapan von + Dativ ile söylenir."),
      [P("The passive puts the action, not the doer, in the centre: **werden** + Partizip II at the end: *Das Haus **wird** "
         "**gebaut**.* The doer, if mentioned, comes with **von** + dative: *von einer Firma*.",
         "Edilgen çatı, eylemi yapanı değil eylemi öne çıkarır: **werden** + sonda Partizip II: *Das Haus **wird** "
         "**gebaut**.* Eylemi yapan söylenecekse **von** + Dativ ile gelir: *von einer Firma*."),
       TABLE([("Tense", "Zaman"), ("Passive", "Edilgen")], [
           ["Präsens", "Das Auto wird repariert."], ["Präteritum", "Das Auto wurde repariert."],
           ["Perfekt", "Das Auto ist repariert worden."], [("with a modal verb", "modal fiille"), "Das Auto muss repariert werden."]]),
       RULE("In the passive Perfekt, *geworden* loses its ge-: *ist repariert **worden***.",
            "Edilgen Perfekt'te *geworden* ge- ekini kaybeder: *ist repariert **worden***."),
       TIP("The state after the action uses *sein*: *Das Geschäft **ist** geschlossen* (it's closed) vs *Das Geschäft "
           "**wird** geschlossen* (someone is closing it).",
           "Eylemden sonraki durum için *sein* kullanılır: *Das Geschäft **ist** geschlossen* (dükkân kapalı) ama *Das "
           "Geschäft **wird** geschlossen* (dükkân kapatılıyor).")],
      [("Hier wird Deutsch gesprochen.", "German is spoken here.", "Burada Almanca konuşulur."),
       ("Das Paket wurde gestern geschickt.", "The parcel was sent yesterday.", "Paket dün gönderildi."),
       ("Die Brücke wird gerade repariert.", "The bridge is being repaired.", "Köprü şu anda onarılıyor."),
       ("Das Fenster muss geputzt werden.", "The window needs cleaning.", "Pencerenin temizlenmesi gerekiyor."),
       ("Der Film wurde von vielen Menschen gesehen.", "The film was seen by many people.", "Film birçok insan tarafından izlendi."),
       ("Mein Fahrrad ist gestohlen worden.", "My bike has been stolen.", "Bisikletim çalındı.")],
      [("Das Haus ist gerade gebaut.", "Das Haus wird gerade gebaut.", "A process uses werden; sein shows the finished state.",
        "Süren bir işlem werden ile söylenir; sein bitmiş durumu gösterir."),
       ("Das Auto ist repariert geworden.", "Das Auto ist repariert worden.", "In the passive Perfekt: worden, not geworden.",
        "Edilgen Perfekt'te geworden değil worden kullanılır."),
       ("Das Buch wurde durch ihn geschrieben.", "Das Buch wurde von ihm geschrieben.", "The doer comes with von + dative.",
        "Eylemi yapan von + Dativ ile söylenir.")],
      "Türkçede edilgen çatı fiile -ıl/-ın eki getirilerek yapılır: yap-ıl-ıyor, gönder-il-di. Almancada ek yerine werden "
      "yardımcı fiili ve cümle sonunda Partizip II kullanılır: Das Paket wurde geschickt = Paket gönderildi. Türkçedeki "
      "'tarafından' Almancada von + Dativ'dir. 'Burada Almanca konuşulur' gibi öznesiz cümleler iki dilde de aynı mantıkla "
      "kurulur: Hier wird Deutsch gesprochen.",
      None, keys="Passiv Vorgangspassiv Zustandspassiv wird wurde worden von", match=r"passiv|passive"),

    T("zu-inf", "B1", "verbs", ("zu + infinitive and um ... zu", "zu + mastar ve um ... zu"),
      ("After many verbs the second verb takes zu and goes to the end; um ... zu means 'in order to'.",
       "Birçok fiilden sonra ikinci fiil zu alır ve sona gider; um ... zu '-mek için' demektir."),
      [P("After many verbs and expressions the second verb takes **zu** and goes to the end: *Ich habe keine Lust, heute "
         "**zu kochen***. With separable verbs, *zu* goes inside: *an**zu**rufen*.",
         "Birçok fiil ve kalıptan sonra ikinci fiil **zu** alır ve sona gider: *Ich habe keine Lust, heute **zu "
         "kochen*** (bugün yemek yapmaya hiç hevesim yok). Ayrılabilen fiillerde *zu* araya girer: *an**zu**rufen*."),
       TABLE([("Typical starters", "Tipik başlangıçlar"), ("Example", "Örnek")], [
           ["Lust haben", "Ich habe Lust, ins Kino zu gehen."], ["versuchen", "Er versucht, pünktlich zu sein."],
           ["vergessen", "Ich habe vergessen, dich anzurufen."], ["es ist wichtig", "Es ist wichtig, viel zu üben."],
           ["anfangen", "Es hat angefangen zu regnen."], ["um ... zu", "Ich spare, um ein Auto zu kaufen."],
           ["ohne ... zu", "Er ging, ohne Tschüss zu sagen."]]),
       RULE("**um ... zu** = in order to: *Ich lerne Deutsch, **um** in Berlin **zu** arbeiten.* Only when both parts have "
            "the same subject; otherwise use *damit*.",
            "**um ... zu** = -mek için: *Ich lerne Deutsch, **um** in Berlin **zu** arbeiten.* Yalnızca iki kısmın öznesi "
            "aynıysa; değilse *damit* kullanılır."),
       TIP("No *zu* after modal verbs, *werden*, *lassen*, or *gehen, sehen, hören*: *Ich gehe schwimmen.*",
           "Modal fiillerden, *werden*, *lassen* ve *gehen, sehen, hören*'den sonra *zu* gelmez: *Ich gehe schwimmen.*")],
      [("Hast du Zeit, mir zu helfen?", "Do you have time to help me?", "Bana yardım etmeye vaktin var mı?"),
       ("Es ist schön, dich zu sehen.", "It's nice to see you.", "Seni görmek güzel."),
       ("Vergiss nicht, die Tür abzuschließen!", "Don't forget to lock the door!", "Kapıyı kilitlemeyi unutma!"),
       ("Ich lerne Deutsch, um in Deutschland zu studieren.", "I'm learning German in order to study in Germany.", "Almanya'da okumak için Almanca öğreniyorum."),
       ("Er spart Geld, damit seine Kinder studieren können.", "He's saving money so that his children can study.", "Çocukları okuyabilsin diye para biriktiriyor."),
       ("Sie ging, ohne ein Wort zu sagen.", "She left without saying a word.", "Tek kelime etmeden gitti.")],
      [("Ich kann zu kommen.", "Ich kann kommen.", "No zu after modal verbs.", "Modal fiillerden sonra zu gelmez."),
       ("zu anrufen", "anzurufen", "With separable verbs zu goes between the prefix and the verb.",
        "Ayrılabilen fiillerde zu, ön ek ile fiilin arasına girer."),
       ("Ich gehe zur Bank für Geld abheben.", "Ich gehe zur Bank, um Geld abzuheben.", "'in order to' + verb is um ... zu, not für.",
        "'-mek için' + fiil um ... zu ile söylenir, für ile değil.")],
      "zu + mastar, Türkçedeki -mek/-mak ile kurulan yapılara benzer: Ich habe Lust zu schwimmen = canım yüzmek istiyor. "
      "Türkçedeki '-mek için' yapısının karşılığı um ... zu'dur: um Deutsch zu lernen = Almanca öğrenmek için. Özneler "
      "farklıysa ('-sın diye', '-mesi için') damit kullanılır. Türkçede olduğu gibi mastarlı kısım cümlenin sonundadır.",
      None, keys="zu Infinitiv um zu ohne zu statt zu damit anzurufen Infinitivsatz",
      match=r"\bum\b.{0,6}\bzu\b|zu \+ inf|infinitive with zu|infinitiv mit zu|\bzu\b.*infinitiv"),

    # ================================================================== word order and sentences
    T("v2", "A1", "order", ("Verb second (V2)", "Fiil ikinci sırada (V2)"),
      ("In a statement the conjugated verb is always the second element, whatever comes first.",
       "Düz cümlede çekimli fiil, başta ne olursa olsun, her zaman ikinci öğedir."),
      [P("In a German statement the conjugated verb is **always the second element**. First place can hold the subject, a "
         "time, a place, an object, even a whole clause. If something else comes first, the subject moves right behind "
         "the verb.",
         "Almanca düz cümlede çekimli fiil **her zaman ikinci öğedir**. Birinci yerde özne, zaman, yer, nesne, hatta "
         "bütün bir yan cümle olabilir. Başa başka bir öğe gelirse özne fiilin hemen arkasına geçer."),
       TABLE(["1", ("2: verb", "2: fiil"), ("subject", "özne"), ("rest", "geri kalan")], [
           ["Ich", "fahre", "–", "morgen nach Berlin."], ["Morgen", "fahre", "ich", "nach Berlin."],
           ["Nach Berlin", "fahre", "ich", "morgen."], ["Wenn ich Zeit habe,", "fahre", "ich", "nach Berlin."]]),
       RULE("Count elements, not words: *Am nächsten Samstag* is one element. *und, aber, oder, denn, sondern* don't count.",
            "Kelimeleri değil öğeleri sayın: *Am nächsten Samstag* tek bir öğedir. *und, aber, oder, denn, sondern* "
            "sayılmaz.")],
      [_wo("Ich lerne seit einem Jahr Deutsch."), _wo("Morgen fahre ich nach Hamburg."),
       _wo("Am Wochenende besuchen wir unsere Großeltern."), _wo("Leider habe ich keine Zeit."),
       _wo("Deshalb lerne ich jeden Tag Vokabeln."),
       ("Wenn es regnet, bleiben wir zu Hause.", "If it rains, we stay at home.", "Yağmur yağarsa evde kalırız.")],
      [("Morgen ich fahre nach Berlin.", "Morgen fahre ich nach Berlin.", "The verb must be second; the subject moves behind it.",
        "Fiil ikinci olmalı; özne fiilin arkasına geçer."),
       ("Deshalb ich lerne Deutsch.", "Deshalb lerne ich Deutsch.", "deshalb takes first place, so the verb follows straight away.",
        "deshalb birinci yeri alır, fiil hemen arkasından gelir."),
       ("Ich morgen fahre nach Berlin.", "Ich fahre morgen nach Berlin.", "Nothing comes between the subject in first place and the verb.",
        "Birinci yerdeki özne ile fiilin arasına hiçbir şey girmez.")],
      "Türkçede fiil sondadır ve diğer öğeler oldukça serbesttir: 'Yarın Berlin'e gidiyorum'. Almanca düz cümlede ise "
      "çekimli fiil mutlaka ikinci sıradadır: Ich fahre morgen nach Berlin. Türkçe konuşanların en sık hatası, Türkçedeki "
      "gibi önce zamanı sonra özneyi koyup fiili geride bırakmaktır: 'Morgen ich fahre' yanlıştır; doğrusu Morgen fahre "
      "ich. Fiili cümlenin menteşesi gibi düşünün: başa ne gelirse gelsin fiil ikinci kalır, özne gerekirse fiilin "
      "arkasına geçer.",
      order("v2", "inv"), keys="Verbzweitstellung V2 Inversion Wortstellung Hauptsatz Position 2",
      skills=["wo:v2", "wo:inv"], match=r"verb.{0,10}(second|position 2)|\bv2\b|inversion|verbzweit"),

    T("bracket", "A1", "order", ("The verb bracket (Satzklammer)", "Fiil parantezi (Satzklammer)"),
      ("Two-part verbs frame the sentence: the conjugated part is second, the other part goes to the very end.",
       "İki parçalı fiiller cümleyi çerçeveler: çekimli parça ikinci sırada, diğer parça en sonda."),
      [P("When a verb has two parts, they frame the sentence: the conjugated part is second, the other part goes to the "
         "**very end**. This happens with modal verbs, the Perfekt, the future, the passive and separable verbs.",
         "Bir fiil iki parçalıysa, bu parçalar cümleyi çerçeveler: çekimli parça ikinci sırada, diğer parça **en "
         "sonda**. Bu; modal fiillerde, Perfekt'te, gelecek zamanda, edilgen çatıda ve ayrılabilen fiillerde olur."),
       TABLE(["1", "2", ("middle", "orta"), ("end", "son")], [
           ["Ich", "kann", "heute leider nicht", "kommen."], ["Wir", "haben", "gestern im Park Fußball", "gespielt."],
           ["Sie", "wird", "uns bestimmt", "helfen."], ["Der Zug", "kommt", "um acht Uhr in München", "an."],
           ["Das Haus", "wird", "gerade", "renoviert."]]),
       RULE("Everything else goes inside the bracket, however long it gets.",
            "Geri kalan her şey, ne kadar uzun olursa olsun, parantezin içine girer.")],
      [_wo("Ich habe gestern einen Film gesehen."), _wo("Wir müssen morgen früh aufstehen."),
       _wo("Er ist letztes Jahr nach Kanada geflogen."), _wo("Ich möchte einen Kaffee bestellen."),
       _wo("Mein Vater hat mir ein Fahrrad geschenkt.")],
      [("Ich habe gesehen einen Film.", "Ich habe einen Film gesehen.", "The Partizip II closes the bracket at the very end.",
        "Partizip II parantezi en sonda kapatır."),
       ("Ich kann kommen heute nicht.", "Ich kann heute nicht kommen.", "The infinitive goes to the very end.",
        "Mastar en sona gider.")],
      "Fiil parantezi Türkçe konuşanlara aslında tanıdık gelir: Türkçede fiil sonda olduğu gibi, Almancada da asıl anlamı "
      "taşıyan parça (gesehen, kommen, an) sona gider. Fark, Almancada çekimli kısmın (habe, kann, kommt) ikinci sıraya öne "
      "çıkmasıdır. 'Dün bir film izledim' cümlesini şöyle düşünün: Ich habe [dün bir film] gesehen. Ortadaki her şey "
      "parantezin içindedir.",
      order("bracket"), keys="Satzklammer Verbklammer Satzende Partizip am Ende",
      skills=["wo:bracket"], match=r"satzklammer|verb bracket|sentence bracket|participle.{0,15}\bend\b|infinitive.{0,15}\bend\b"),

    T("tekamolo", "A2", "order", ("TeKaMoLo: time, cause, manner, place", "TeKaMoLo: zaman, sebep, tarz, yer"),
      ("In the middle of the sentence: when? why? how? where? And the dative object usually before the accusative.",
       "Cümlenin ortasında sıra: ne zaman? neden? nasıl? nerede? Dativ nesne de genellikle Akkusativ'den önce gelir."),
      [P("In the middle of the sentence, details usually follow the order **Te**mporal (when?), **Ka**usal (why?), "
         "**Mo**dal (how?), **Lo**kal (where?): *Ich fahre **morgen wegen der Arbeit mit dem Zug nach Hamburg***.",
         "Cümlenin ortasındaki ayrıntılar genellikle şu sırayı izler: **Te**mporal (ne zaman?), **Ka**usal (neden?), "
         "**Mo**dal (nasıl?), **Lo**kal (nerede? nereye?): *Ich fahre **morgen wegen der Arbeit mit dem Zug nach "
         "Hamburg***."),
       TABLE(["Te (wann?)", "Ka (warum?)", "Mo (wie?)", "Lo (wo? wohin?)"], [
           ["morgen", "wegen der Arbeit", "mit dem Zug", "nach Hamburg"], ["heute", "–", "zu Fuß", "zur Schule"],
           ["jeden Tag", "aus Spaß", "allein", "im Park"]]),
       RULE("Two objects: two nouns → dative before accusative (*Ich gebe **dem Kind** **den Ball***). A pronoun comes "
            "before a noun, and an accusative pronoun before a dative pronoun: *Ich gebe **ihn** dem Kind. Ich gebe **ihn "
            "ihm**.*",
            "İki nesne: iki isim → Dativ, Akkusativ'den önce (*Ich gebe **dem Kind** **den Ball***). Zamir isimden önce "
            "gelir; iki zamirde Akkusativ zamir Dativ zamirden önce: *Ich gebe **ihn** dem Kind. Ich gebe **ihn ihm**.*"),
       TIP("This is the usual order, not a law: anything can move to first place for emphasis: *Mit dem Zug fahre ich "
           "morgen nach Hamburg.*",
           "Bu bir yasa değil, olağan sıradır: vurgulamak için herhangi bir öğe başa geçebilir: *Mit dem Zug fahre ich "
           "morgen nach Hamburg.*")],
      [("Ich gehe heute mit meiner Freundin ins Kino.", "I'm going to the cinema with my girlfriend today.", "Bugün kız arkadaşımla sinemaya gidiyorum."),
       _wo("Meine Kollegin fährt jeden Tag mit dem Fahrrad zur Arbeit."),
       ("Wir bleiben wegen des Regens zu Hause.", "We're staying at home because of the rain.", "Yağmur yüzünden evde kalıyoruz."),
       ("Ich schenke meiner Mutter Blumen.", "I'm giving my mother flowers.", "Anneme çiçek hediye ediyorum."),
       ("Ich gebe es ihm morgen.", "I'll give it to him tomorrow.", "Onu ona yarın veririm."),
       ("Sie hat mir gestern das Buch gegeben.", "She gave me the book yesterday.", "Dün kitabı bana verdi.")],
      [("Ich fahre nach Hamburg morgen.", "Ich fahre morgen nach Hamburg.", "Time before place.", "Zaman, yerden önce gelir."),
       ("Ich gebe ihm es.", "Ich gebe es ihm.", "Two pronouns: accusative before dative.", "İki zamir: Akkusativ, Dativ'den önce.")],
      "Türkçede de benzer bir doğal sıra vardır: 'Yarın iş yüzünden trenle Hamburg'a gidiyorum': zaman, sebep, tarz, yer. "
      "Yani TeKaMoLo sırası Türkçedeki sezginize oldukça uygundur! Tek fark, Almancada bu öğelerin fiilden sonra "
      "gelmesidir: Ich fahre morgen wegen der Arbeit mit dem Zug nach Hamburg. Yer bilgisi (nach Hamburg) Türkçede fiile "
      "en yakın yerdedir; Almancada da cümlenin sonundadır.",
      order("v2"), keys="TeKaMoLo temporal kausal modal lokal Mittelfeld Dativ vor Akkusativ Reihenfolge",
      match=r"tekamolo|time.{0,20}place|object order|dative before accusative"),

    T("questions", "A1", "order", ("Questions: W-questions and yes/no", "Sorular: W-soruları ve evet/hayır"),
      ("W-questions: question word, then the verb. Yes/no questions: the verb comes first.",
       "W-soruları: soru kelimesi, sonra fiil. Evet/hayır soruları: fiil başa gelir."),
      [P("**W-questions**: question word first, verb second: *Wo **wohnst** du?* **Yes/no questions**: the verb comes "
         "first: ***Wohnst** du in Berlin?*",
         "**W-soruları**: önce soru kelimesi, ikinci sırada fiil: *Wo **wohnst** du?* **Evet/hayır soruları**: fiil başa "
         "gelir: ***Wohnst** du in Berlin?*"),
       TABLE([("Question word", "Soru kelimesi"), ("Meaning", "Anlam")], [
           ["wer", ("who", "kim")], ["wen", ("who(m) (accusative)", "kimi")], ["wem", ("to whom (dative)", "kime")],
           ["wessen", ("whose", "kimin")], ["was", ("what", "ne")], ["wo", ("where", "nerede")], ["wohin", ("where to", "nereye")],
           ["woher", ("where from", "nereden")], ["wann", ("when", "ne zaman")], ["warum", ("why", "neden")],
           ["wie", ("how", "nasıl")], ["wie viel / wie viele", ("how much / how many", "ne kadar / kaç")],
           ["welcher", ("which", "hangi")]]),
       RULE("Answer a negative question with **doch** to say yes: *Kommst du nicht? – **Doch**!*",
            "Olumsuz bir soruya 'evet' demek için **doch** kullanılır: *Kommst du nicht? – **Doch**!*")],
      [("Woher kommst du?", "Where are you from?", "Nerelisin?"), _wo("Was machst du am Wochenende?"),
       ("Hast du heute Zeit?", "Do you have time today?", "Bugün vaktin var mı?"),
       ("Wem gehört das Handy?", "Whose phone is this?", "Bu telefon kimin?"),
       ("Wie viele Geschwister hast du?", "How many brothers and sisters do you have?", "Kaç kardeşin var?"),
       ("Hast du keinen Hunger? – Doch!", "Aren't you hungry? – Yes, I am!", "Aç değil misin? – Açım tabii!")],
      [("Wo du wohnst?", "Wo wohnst du?", "In questions the verb comes right after the question word.",
        "Sorularda fiil, soru kelimesinin hemen arkasından gelir."),
       ("Du kommst morgen?", "Kommst du morgen?", "Yes/no questions start with the verb.", "Evet/hayır soruları fiille başlar."),
       ("Wer hilfst du?", "Wem hilfst du?", "helfen takes the dative: wem.", "helfen Dativ ister: wem.")],
      "Türkçede soru kelimesi genellikle fiilin hemen önüne gelir ve evet/hayır soruları mı/mi ekiyle yapılır: 'Yarın "
      "geliyor musun?' Almancada mı/mi eki yoktur; bunun yerine fiil cümlenin başına geçer: Kommst du morgen? Soru kelimesi "
      "ise en başa gelir: Wo wohnst du? Türkçedeki kim/kimi/kime ayrımı Almancada da vardır: wer, wen, wem. "
      "Nerede/nereye/nereden ayrımı da birebir aynıdır: wo, wohin, woher.",
      order("quest"), keys="Fragen W-Fragen Ja-Nein-Fragen wer wen wem wessen was wo wohin woher wann warum wie doch",
      skills=["wo:quest", "wer:"], match=r"question|\bfrage|w-word|interrogative"),

    T("subordinate", "A2", "order", ("Subordinate clauses: the verb goes last", "Yan cümleler: fiil sona gider"),
      ("After weil, dass, wenn, ob and other subordinating conjunctions the conjugated verb goes to the end.",
       "weil, dass, wenn, ob ve diğer yan cümle bağlaçlarından sonra çekimli fiil sona gider."),
      [P("After a subordinating conjunction (*weil, dass, wenn, ob, als, obwohl, damit, bevor, nachdem*) or a question word "
         "inside a sentence, the conjugated verb goes to the **end** of the clause. A comma separates the clauses.",
         "Bir yan cümle bağlacından (*weil, dass, wenn, ob, als, obwohl, damit, bevor, nachdem*) ya da cümle içindeki "
         "bir soru kelimesinden sonra çekimli fiil yan cümlenin **sonuna** gider. Cümleler virgülle ayrılır."),
       TABLE([("Conjunction", "Bağlaç"), ("Meaning", "Anlam"), ("Example", "Örnek")], [
           ["weil", ("because", "çünkü, -dığı için"), "..., weil ich krank bin."],
           ["dass", ("that", "-dığını, -dığı"), "Ich glaube, dass er kommt."],
           ["wenn", ("if; when(ever)", "-se; -dığında"), "Wenn du Zeit hast, ruf mich an."],
           ["ob", ("whether, if", "-ip -mediğini"), "Ich weiß nicht, ob er kommt."],
           ["obwohl", ("although", "-mesine rağmen"), "..., obwohl es regnet."],
           ["als", ("when (once, in the past)", "-dığında (geçmişte bir kez)"), "Als ich klein war, ..."],
           ["damit", ("so that", "-sın diye"), "..., damit du es verstehst."],
           ["bevor / nachdem", ("before / after", "-meden önce / -dikten sonra"), "Bevor ich gehe, ..."]]),
       RULE("If the subordinate clause comes first, it fills position 1, so the main clause starts with the verb: *Weil ich "
            "krank bin, **bleibe** ich zu Hause.*",
            "Yan cümle başa gelirse birinci yeri doldurur; ana cümle fiille başlar: *Weil ich krank bin, **bleibe** ich "
            "zu Hause.*"),
       TIP("Separable verbs stay together at the end: *..., dass der Bus um acht **abfährt***. With a helper verb, the "
           "helper is last: *..., weil ich lange **gearbeitet habe***.",
           "Ayrılabilen fiiller sonda bitişik kalır: *..., dass der Bus um acht **abfährt***. Yardımcı fiil varsa en sonda "
           "o durur: *..., weil ich lange **gearbeitet habe***.")],
      [_wo("Ich bleibe heute zu Hause, weil ich krank bin."), _wo("Ich glaube, dass er morgen kommt."),
       _wo("Sie fragt, ob wir heute Abend Zeit haben."),
       ("Weil es regnet, nehmen wir den Bus.", "Because it's raining, we're taking the bus.", "Yağmur yağdığı için otobüse biniyoruz."),
       _wo("Ich weiß nicht, wann der Bus abfährt."),
       ("Obwohl er müde ist, arbeitet er weiter.", "Although he's tired, he keeps working.", "Yorgun olmasına rağmen çalışmaya devam ediyor.")],
      [("..., weil ich bin krank.", "..., weil ich krank bin.", "After weil the verb goes to the end.", "weil'den sonra fiil sona gider."),
       ("Weil ich krank bin, ich bleibe zu Hause.", "Weil ich krank bin, bleibe ich zu Hause.",
        "The subordinate clause counts as position 1; the verb comes next.", "Yan cümle birinci yer sayılır; ardından fiil gelir."),
       ("..., dass er hat angerufen.", "..., dass er angerufen hat.", "With a helper verb, the helper goes last.",
        "Yardımcı fiil varsa en sona o gider.")],
      "İşte Türkçe konuşanların avantajı: Almanca yan cümlede fiil, tıpkı Türkçede olduğu gibi, en sondadır: ..., weil "
      "ich krank bin = ..., çünkü hastayım / hasta olduğum için. Türkçede yan cümleler çoğu zaman fiile eklenen eklerle "
      "kurulur (-dığı için, -dığını, -se); Almancada ise yan cümlenin başında bir bağlaç (weil, dass, wenn) durur ve fiil "
      "sona gider. Dikkat: yan cümle başa gelirse ana cümle fiille başlar: Weil ich krank bin, bleibe ich zu Hause.",
      order("sub"), keys="Nebensatz Verbletztstellung weil dass wenn ob obwohl als damit bevor nachdem Konjunktion",
      skills=["wo:sub"], match=r"subordinat|nebensatz|verb.{0,15}\b(last|final|end)\b|\bweil\b|\bdass\b|\bobwohl\b"),

    T("coordinating", "A2", "order", ("und, aber, oder, denn, sondern", "und, aber, oder, denn, sondern"),
      ("These five join main clauses without changing the word order: they stand before position 1.",
       "Bu beşi ana cümleleri kelime sırasını değiştirmeden bağlar: birinci yerden önce dururlar."),
      [P("These five join two main clauses **without changing the word order**. They stand at position 0, so they don't "
         "count and the verb is still second: *Ich bin müde, **aber** ich **gehe** noch einkaufen.*",
         "Bu beş bağlaç iki ana cümleyi **kelime sırasını değiştirmeden** bağlar. Sıfırıncı yerde dururlar, yani "
         "sayılmazlar ve fiil yine ikinci sıradadır: *Ich bin müde, **aber** ich **gehe** noch einkaufen.*"),
       TABLE([("Conjunction", "Bağlaç"), ("Meaning", "Anlam")], [
           ["und", ("and", "ve")], ["aber", ("but", "ama")], ["oder", ("or", "veya, yoksa")], ["denn", ("because", "çünkü")],
           ["sondern", ("but rather (after a negative)", "değil ..., -dir")]]),
       RULE("*denn* and *weil* both mean 'because', but *denn* keeps the verb second and *weil* sends it to the end: "
            "*..., **denn** ich **bin** krank* / *..., **weil** ich krank **bin***.",
            "*denn* ve *weil* ikisi de 'çünkü' demektir, ama *denn* fiili ikinci sırada bırakır, *weil* sona gönderir: "
            "*..., **denn** ich **bin** krank* / *..., **weil** ich krank **bin***."),
       TIP("*sondern* corrects a negative: *Er kommt nicht heute, **sondern** morgen.*",
           "*sondern* olumsuz bir ifadeyi düzeltir: *Er kommt nicht heute, **sondern** morgen* (bugün değil, yarın geliyor).")],
      [("Ich trinke Tee und meine Frau trinkt Kaffee.", "I drink tea and my wife drinks coffee.", "Ben çay içerim, eşim de kahve."),
       ("Ich möchte kommen, aber ich habe keine Zeit.", "I'd like to come, but I don't have time.", "Gelmek isterim ama vaktim yok."),
       ("Kommst du mit oder bleibst du hier?", "Are you coming along or staying here?", "Geliyor musun, yoksa burada mı kalıyorsun?"),
       ("Ich nehme einen Schirm, denn es regnet.", "I'm taking an umbrella because it's raining.", "Şemsiye alıyorum, çünkü yağmur yağıyor."),
       ("Das ist nicht mein Auto, sondern das Auto meines Bruders.", "That isn't my car, it's my brother's.", "Bu benim arabam değil, kardeşimin arabası.")],
      [("..., denn ich krank bin.", "..., denn ich bin krank.", "denn doesn't change the word order.", "denn kelime sırasını değiştirmez."),
       ("..., aber habe ich keine Zeit.", "..., aber ich habe keine Zeit.", "aber is position 0: the subject can come first.",
        "aber sıfırıncı yerdedir: özne başa gelebilir."),
       ("Er kommt nicht heute, aber morgen.", "Er kommt nicht heute, sondern morgen.", "After a negative, 'but rather' is sondern.",
        "Olumsuzdan sonra 'değil ..., -dir' sondern ile söylenir.")],
      "Türkçedeki 've, ama, veya, çünkü' bağlaçları Almancadaki und, aber, oder, denn'e karşılık gelir ve kelime sırasını "
      "değiştirmez. Dikkat: Türkçede 'çünkü' tek bir kelimedir, Almancada iki seçenek vardır: denn (fiil ikinci sırada) "
      "ve weil (fiil sonda). 'Bu benim değil, kardeşimin' gibi 'değil ..., -dir' yapıları Almancada nicht ..., sondern ... "
      "ile kurulur.",
      None, keys="und aber oder denn sondern Konjunktionen ADUSO Hauptsatz", match=r"coordinat|\bdenn\b|\bsondern\b"),

    T("negation", "A1", "order", ("Negation: nicht or kein?", "Olumsuzluk: nicht mi, kein mi?"),
      ("kein for nouns with ein or no article; nicht for everything else. Where nicht goes depends on what it negates.",
       "ein'lı veya artikelsiz isimler için kein, diğer her şey için nicht. nicht'in yeri, olumsuzladığı şeye bağlıdır."),
      [P("**kein** negates a noun that would have *ein* or no article: *Ich habe **kein** Auto. Er trinkt **keinen** "
         "Kaffee.* **nicht** negates everything else: verbs, adjectives, nouns with *der/die/das*, names, adverbs.",
         "**kein**, *ein*'lı ya da artikelsiz bir ismi olumsuzlar: *Ich habe **kein** Auto. Er trinkt **keinen** Kaffee.* "
         "Diğer her şeyi **nicht** olumsuzlar: fiiller, sıfatlar, *der/die/das*'lı isimler, özel isimler, zarflar."),
       TABLE([("Positive", "Olumlu"), ("Negative", "Olumsuz")], [
           ["Ich habe ein Auto.", "Ich habe kein Auto."], ["Ich trinke Kaffee.", "Ich trinke keinen Kaffee."],
           ["Ich kenne den Mann.", "Ich kenne den Mann nicht."], ["Das ist schön.", "Das ist nicht schön."],
           ["Ich komme heute.", "Ich komme heute nicht."]]),
       RULE("Where *nicht* goes: at the end to negate the whole sentence (*Ich kenne ihn **nicht***), but before an "
            "adjective, a place, a prepositional phrase or the second verb part (*Er ist **nicht** müde. Ich fahre "
            "**nicht** nach Berlin. Ich habe ihn **nicht** gesehen.*).",
            "*nicht*'in yeri: bütün cümleyi olumsuzlarken sonda (*Ich kenne ihn **nicht***), ama sıfattan, yerden, edatlı "
            "öbekten veya fiilin ikinci parçasından önce (*Er ist **nicht** müde. Ich fahre **nicht** nach Berlin. Ich "
            "habe ihn **nicht** gesehen.*).")],
      [("Ich habe heute keine Zeit.", "I don't have time today.", "Bugün vaktim yok."),
       ("Das Essen ist nicht teuer.", "The food isn't expensive.", "Yemek pahalı değil."),
       ("Wir haben keine Kinder.", "We don't have children.", "Çocuğumuz yok."),
       ("Ich verstehe das nicht.", "I don't understand that.", "Bunu anlamıyorum."),
       ("Er ist nicht zu Hause.", "He isn't at home.", "Evde değil."),
       ("Ich habe den Film nicht gesehen.", "I haven't seen the film.", "Filmi görmedim.")],
      [("Ich habe nicht Zeit.", "Ich habe keine Zeit.", "Zeit has no article here: negate it with kein.",
        "Zeit burada artikelsizdir: kein ile olumsuzlanır."),
       ("Ich nicht verstehe.", "Ich verstehe nicht.", "nicht comes after the conjugated verb.", "nicht çekimli fiilden sonra gelir."),
       ("Ich habe nicht ihn gesehen.", "Ich habe ihn nicht gesehen.", "To negate the whole sentence, nicht goes after the object.",
        "Bütün cümleyi olumsuzlarken nicht nesneden sonra gelir.")],
      "Türkçede olumsuzluk çoğu zaman fiile eklenir (gel-me-di) ya da 'değil' ve 'yok' ile söylenir. Almancada iki araç "
      "vardır: isim için kein ('yok' gibi: Ich habe kein Auto = arabam yok), diğer her şey için nicht ('değil' ve '-me' "
      "gibi: Das ist nicht teuer = pahalı değil; Ich komme nicht = gelmiyorum). nicht, Türkçedeki gibi fiilin içine "
      "girmez; cümlede ayrı bir kelime olarak genellikle sona veya olumsuzladığı öğenin önüne gelir.",
      drill(DECL, ["ein"]), keys="Negation Verneinung nicht kein keine keinen doch", match=r"negat|verneinung|\bnicht\b"),

    T("wenn-als-ob", "B1", "order", ("wenn, als or ob?", "wenn mi, als mi, ob mu?"),
      ("wenn: if, and when(ever). als: when, once in the past. ob: whether. All three send the verb to the end.",
       "wenn: -se ve -dığında (her seferinde). als: geçmişte bir kez -dığında. ob: -ip -mediğini. Üçünde de fiil sona gider."),
      [P("All three can translate English 'if' or 'when', and all three send the verb to the end.",
         "Üçü de İngilizcedeki 'if' veya 'when' ile çevrilebilir ve üçü de fiili sona gönderir."),
       TABLE([("Word", "Kelime"), ("Use", "Kullanım"), ("Example", "Örnek")], [
           ["wenn", ("if; when (present, future); whenever (past)", "-se; -dığında (şimdi, gelecek); her ... -dığında (geçmiş)"),
            "Wenn ich Zeit habe, komme ich."],
           ["als", ("when: one event or period in the past", "-dığında: geçmişte tek bir olay veya dönem"),
            "Als ich ein Kind war, wohnten wir in Izmir."],
           ["ob", ("whether (if = whether)", "-ip -mediğini"), "Ich weiß nicht, ob er kommt."]]),
       RULE("Past + once → **als**. Past + every time → **wenn** (often with *immer*). Could you say 'whether'? → **ob**.",
            "Geçmiş + bir kez → **als**. Geçmiş + her seferinde → **wenn** (çoğu zaman *immer* ile). 'whether' "
            "denebiliyorsa → **ob**.")],
      [("Wenn es regnet, nehme ich den Bus.", "If it rains, I take the bus.", "Yağmur yağarsa otobüse binerim."),
       ("Als ich nach Deutschland kam, konnte ich kein Deutsch.", "When I came to Germany, I couldn't speak any German.",
        "Almanya'ya geldiğimde hiç Almanca bilmiyordum."),
       ("Immer wenn ich ihn besuchte, kochte er.", "Whenever I visited him, he cooked.", "Onu her ziyaret ettiğimde yemek yapardı."),
       ("Weißt du, ob der Laden heute offen ist?", "Do you know if the shop is open today?", "Dükkânın bugün açık olup olmadığını biliyor musun?"),
       ("Ruf mich an, wenn du ankommst.", "Call me when you arrive.", "Varınca beni ara.")],
      [("Wenn ich ein Kind war, ...", "Als ich ein Kind war, ...", "One period in the past: als.", "Geçmişte tek bir dönem: als."),
       ("Ich weiß nicht, wenn er kommt. (whether)", "Ich weiß nicht, ob er kommt.", "'whether' is ob.", "'-ip -mediğini' ob ile söylenir."),
       ("Als es morgen regnet, ...", "Wenn es morgen regnet, ...", "In the present and future, use wenn.",
        "Şimdiki ve gelecek zamanda wenn kullanılır.")],
      "Türkçede bu üç anlam farklı eklerle söylenir, bu yüzden ipucu aslında sizdedir: '-se/-sa' ve genel ya da tekrarlanan "
      "'-dığında' → wenn; geçmişteki tek bir olay için '-dığında, -ken' → als (Almanya'ya geldiğimde = als ich nach "
      "Deutschland kam); '-ip -mediğini' → ob (gelip gelmediğini = ob er kommt). Üçünden sonra da fiil, tıpkı Türkçede "
      "olduğu gibi, sona gider.",
      None, keys="wenn als ob Temporalsatz Konditionalsatz indirekte Frage",
      match=r"wenn.{0,3}(/|or|oder|vs\.?).{0,3}als|als.{0,3}(/|or|oder|vs\.?).{0,3}wenn|\bob\b.{0,3}(/|or|oder|vs)"),
]
TOPIC_BY_ID = {t["id"]: t for t in TOPICS}
