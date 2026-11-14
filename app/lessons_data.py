"""The built-in beginner course (A1, part 1): 12 short lessons for learners without a textbook.

Each lesson: words ("German=English", nouns with their article), a dialogue ("Speaker|German|English"),
one grammar point (title, short explanation, examples "German=English") and exercises
("Sentence with ___|answer|wrong choice|wrong choice"). app/lessons.py turns these into lessons and quizzes.
"""

LESSONS = [
    {
        "id": "hallo", "title": "Hallo!", "subtitle": "Greetings and saying your name",
        "words": """Hallo=hello; Guten Morgen=good morning; Guten Tag=hello, good day; Guten Abend=good evening;
Tschüss=bye; Auf Wiedersehen=goodbye; danke=thank you; bitte=please; you're welcome; ja=yes; nein=no;
der Name=name; ich=I; du=you (informal); Sie=you (formal)""",
        "dialogue": """Anna|Hallo! Ich bin Anna. Wie heißt du?|Hello! I'm Anna. What's your name?
Ben|Hallo Anna! Ich heiße Ben.|Hello Anna! My name is Ben.
Anna|Freut mich, Ben. Wie geht's?|Nice to meet you, Ben. How are you?
Ben|Gut, danke. Und dir?|Good, thanks. And you?
Anna|Auch gut, danke. Tschüss, Ben!|Good too, thanks. Bye, Ben!
Ben|Tschüss, bis bald!|Bye, see you soon!""",
        "grammar": ("du or Sie?", """German has two words for "you". Use **du** with friends, family, children and people your own age in casual settings. Use **Sie** (always with a capital S) with strangers, in shops and offices, and with anyone you'd call Mr. or Ms.

The verb changes with it: **Wie heißt du?** but **Wie heißen Sie?**

To say your name, use **Ich heiße ...** (I am called ...) or **Ich bin ...** (I am ...).""",
                    "Wie heißt du?=What's your name? (informal); Wie heißen Sie?=What's your name? (formal); Ich heiße Maria.=My name is Maria.; Ich bin Tom.=I'm Tom."),
        "exercises": """Ich ___ Anna.|heiße|heißt|heißen
Wie heißt ___?|du|Sie|ich
Wie heißen ___?|Sie|du|ich
Guten ___! (at 8 in the morning)|Morgen|Abend|Nacht
Wie ___ du?|heißt|heiße|heißen
Ich ___ Ben.|bin|bist|ist""",
    },
    {
        "id": "woher", "title": "Woher kommst du?", "subtitle": "Countries, cities and languages",
        "words": """kommen=to come; wohnen=to live (reside); sprechen=to speak; lernen=to learn; Deutschland=Germany;
Österreich=Austria; die Schweiz=Switzerland; die Türkei=Turkey; Deutsch=German (language); Englisch=English (language);
die Stadt=city; das Land=country; woher=where from; wo=where; aus=from; in=in; ein bisschen=a little""",
        "dialogue": """Lena|Woher kommst du, Tom?|Where are you from, Tom?
Tom|Ich komme aus England. Und du?|I'm from England. And you?
Lena|Ich komme aus Österreich, aus Wien.|I'm from Austria, from Vienna.
Tom|Wo wohnst du jetzt?|Where do you live now?
Lena|Ich wohne in Berlin. Sprichst du Deutsch?|I live in Berlin. Do you speak German?
Tom|Ja, ein bisschen. Ich lerne Deutsch.|Yes, a little. I'm learning German.""",
        "grammar": ("Verb endings: ich, du, er/sie", """German verbs change their ending with the person. Take off **-en** from the dictionary form and add:

- **ich** → **-e**: ich komm**e**, ich wohn**e**
- **du** → **-st**: du komm**st**, du wohn**st**
- **er / sie / es** → **-t**: er komm**t**, sie wohn**t**
- **Sie** (formal) keeps **-en**: Sie komm**en**

Questions with a question word put the verb second: **Woher kommst du?** **Wo wohnst du?**""",
                    "Ich komme aus Spanien.=I'm from Spain.; Du wohnst in Köln.=You live in Cologne.; Sie lernt Deutsch.=She is learning German.; Woher kommen Sie?=Where are you from? (formal)"),
        "exercises": """Ich ___ aus Italien.|komme|kommst|kommt
Woher ___ du?|kommst|komme|kommen
Er ___ in Hamburg.|wohnt|wohne|wohnst
Ich komme ___ der Türkei.|aus|in|wo
Wo ___ Sie?|wohnen|wohnst|wohne
Sie ___ Deutsch. (she)|lernt|lerne|lernst
Ich wohne ___ Berlin.|in|aus|woher""",
    },
    {
        "id": "zahlen", "title": "Zahlen und Alter", "subtitle": "Numbers 0 to 20, age and phone numbers",
        "words": """null=zero; eins=one; zwei=two; drei=three; vier=four; fünf=five; sechs=six; sieben=seven; acht=eight;
neun=nine; zehn=ten; elf=eleven; zwölf=twelve; zwanzig=twenty; das Jahr=year; alt=old;
die Nummer=number; das Telefon=telephone; wie=how; wer=who""",
        "dialogue": """Frau Weber|Guten Tag. Wie ist Ihr Name, bitte?|Hello. What's your name, please?
Herr Kaya|Mein Name ist Emre Kaya.|My name is Emre Kaya.
Frau Weber|Wie alt sind Sie, Herr Kaya?|How old are you, Mr. Kaya?
Herr Kaya|Ich bin neunzehn Jahre alt.|I'm nineteen years old.
Frau Weber|Und wie ist Ihre Telefonnummer?|And what's your phone number?
Herr Kaya|Null, eins, sieben, zwei, vier, acht, fünf.|Zero, one, seven, two, four, eight, five.""",
        "grammar": ("sein (to be)", """**sein** is the most important German verb, and it's irregular:

- ich **bin** (I am)
- du **bist** (you are)
- er / sie / es **ist** (he / she / it is)
- wir **sind** (we are)
- ihr **seid** (you all are)
- sie / Sie **sind** (they are / you are, formal)

For age, German uses sein, like English: **Ich bin zwanzig Jahre alt.** The numbers 13 to 19 end in **-zehn**: dreizehn, vierzehn, fünfzehn, sechzehn, siebzehn, achtzehn, neunzehn.""",
                    "Ich bin zwölf Jahre alt.=I'm twelve years old.; Wie alt bist du?=How old are you?; Sie ist zwanzig.=She is twenty.; Wir sind aus Polen.=We are from Poland."),
        "exercises": """Ich ___ achtzehn Jahre alt.|bin|bist|ist
Wie alt ___ du?|bist|bin|sind
Er ___ zehn Jahre alt.|ist|bin|bist
Wie alt ___ Sie?|sind|bist|ist
drei + vier = ___|sieben|sechs|acht
zehn + zwei = ___|zwölf|elf|zwanzig
Wir ___ in Berlin.|sind|seid|ist""",
    },
    {
        "id": "cafe", "title": "Im Café", "subtitle": "Ordering food and drinks",
        "words": """der Kaffee=coffee; der Tee=tea; das Wasser=water; der Saft=juice; die Milch=milk; der Kuchen=cake;
das Brötchen=bread roll; die Suppe=soup; möchten=would like; nehmen=to take; trinken=to drink; essen=to eat;
die Rechnung=bill, check; der Euro=euro; mit=with; ohne=without; und=and; oder=or""",
        "dialogue": """Kellner|Guten Tag! Was möchten Sie?|Hello! What would you like?
Sara|Ich möchte einen Kaffee mit Milch, bitte.|I'd like a coffee with milk, please.
Kellner|Gern. Möchten Sie auch etwas essen?|Certainly. Would you like something to eat too?
Sara|Ja, ich nehme ein Brötchen und eine Suppe.|Yes, I'll take a bread roll and a soup.
Kellner|Sehr gut. Kommt sofort.|Very good. Coming right up.
Sara|Die Rechnung, bitte.|The check, please.
Kellner|Das macht neun Euro.|That's nine euros.""",
        "grammar": ("der, die, das and ein, eine", """Every German noun has a gender, shown by its word for "the":

- **der** (masculine): der Kaffee, der Tee
- **die** (feminine): die Milch, die Suppe
- **das** (neuter): das Wasser, das Brötchen

Learn each noun together with its article. "A / an" is **ein** for der and das words, **eine** for die words.

When you order or have something, masculine words change: **der → den**, **ein → einen**. Feminine and neuter stay the same: Ich möchte **einen** Kaffee, **eine** Suppe, **ein** Wasser.""",
                    "Ich möchte einen Tee.=I'd like a tea.; Ich nehme eine Suppe.=I'll take a soup.; Er trinkt ein Wasser.=He drinks a water.; Der Kaffee ist gut.=The coffee is good."),
        "exercises": """Ich möchte ___ Kaffee.|einen|ein|eine
Ich nehme ___ Suppe.|eine|einen|ein
Sie möchte ___ Wasser.|ein|einen|eine
___ Milch ist kalt.|Die|Der|Das
___ Kuchen ist gut.|Der|Die|Das
Ich trinke Tee ___ Milch.|mit|und|oder
Was ___ Sie?|möchten|möchte|möchtest""",
    },
    {
        "id": "familie", "title": "Die Familie", "subtitle": "Talking about your family",
        "words": """die Familie=family; die Mutter=mother; der Vater=father; die Eltern=parents; der Bruder=brother;
die Schwester=sister; das Kind=child; der Sohn=son; die Tochter=daughter; der Mann=man; husband;
die Frau=woman; wife; der Freund=friend; boyfriend; haben=to have; verheiratet=married; mein=my; dein=your;
kein=no, not a""",
        "dialogue": """Ben|Hast du Geschwister, Mia?|Do you have siblings, Mia?
Mia|Ja, ich habe einen Bruder und eine Schwester.|Yes, I have a brother and a sister.
Ben|Wie heißt dein Bruder?|What's your brother's name?
Mia|Mein Bruder heißt Jonas. Er ist verheiratet.|My brother's name is Jonas. He's married.
Ben|Hat er Kinder?|Does he have children?
Mia|Ja, eine Tochter. Und du? Hast du Geschwister?|Yes, a daughter. And you? Do you have siblings?
Ben|Nein, ich habe keine Geschwister.|No, I don't have any siblings.""",
        "grammar": ("haben and mein / dein", """**haben** (to have):

- ich **habe**
- du **hast**
- er / sie / es **hat**
- wir **haben**
- ihr **habt**
- sie / Sie **haben**

**mein** (my) and **dein** (your) take the same endings as ein: **mein** Bruder (der), **meine** Schwester (die), **mein** Kind (das).

To say you don't have something, use **kein / keine**: Ich habe **keinen** Bruder. Ich habe **keine** Schwester.""",
                    "Ich habe eine Schwester.=I have a sister.; Hast du Kinder?=Do you have children?; Meine Mutter heißt Eva.=My mother's name is Eva.; Er hat keinen Bruder.=He has no brother."),
        "exercises": """Ich ___ einen Bruder.|habe|hast|hat
___ du Kinder?|Hast|Habe|Hat
Er ___ eine Tochter.|hat|habe|hast
___ Mutter heißt Anna. (my)|Meine|Mein|Meinen
___ Vater ist Lehrer. (my)|Mein|Meine|Meinen
Wie heißt ___ Schwester? (your)|deine|dein|deinen
Ich habe ___ Schwester. (no)|keine|kein|keinen""",
    },
    {
        "id": "tag", "title": "Mein Tag", "subtitle": "Daily routine and telling the time",
        "words": """die Uhr=clock; o'clock; der Morgen=morning; der Abend=evening; die Nacht=night; die Arbeit=work;
die Schule=school; arbeiten=to work; gehen=to go; schlafen=to sleep; frühstücken=to have breakfast;
spielen=to play; heute=today; morgen=tomorrow; jetzt=now; dann=then; früh=early; spät=late; um=at (time)""",
        "dialogue": """Paul|Wie spät ist es?|What time is it?
Lisa|Es ist sieben Uhr.|It's seven o'clock.
Paul|So früh! Wann gehst du zur Arbeit?|So early! When do you go to work?
Lisa|Um acht Uhr. Zuerst frühstücke ich.|At eight o'clock. First I have breakfast.
Paul|Und was machst du heute Abend?|And what are you doing this evening?
Lisa|Heute Abend spiele ich Tennis. Dann schlafe ich früh.|This evening I'm playing tennis. Then I'm going to sleep early.""",
        "grammar": ("The verb comes second", """In a German statement the verb is always the **second** element. If you start with a time word, the subject moves behind the verb:

- **Ich spiele** heute Tennis.
- **Heute spiele ich** Tennis.

Both are correct. The verb stays in second place.

For clock times, say **Es ist ... Uhr** (It's ... o'clock) and **um ... Uhr** (at ... o'clock): Ich arbeite **um neun Uhr**.""",
                    "Ich gehe um acht Uhr zur Schule.=I go to school at eight.; Um acht Uhr gehe ich zur Schule.=At eight I go to school.; Morgen arbeite ich nicht.=Tomorrow I'm not working.; Es ist zehn Uhr.=It's ten o'clock."),
        "exercises": """Heute ___ ich Fußball.|spiele|spielst|spielt
Um neun Uhr ___ er zur Arbeit.|geht|gehe|gehst
Es ___ acht Uhr.|ist|bin|sind
Ich arbeite ___ zehn Uhr.|um|in|aus
Wie ___ ist es?|spät|früh|alt
Morgen ___ wir Tennis.|spielen|spielt|spiele
Dann ___ ich.|schlafe|schläfst|schlafen""",
    },
    {
        "id": "einkaufen", "title": "Einkaufen", "subtitle": "Shopping for food, prices and plurals",
        "words": """der Supermarkt=supermarket; das Brot=bread; der Käse=cheese; der Apfel=apple; die Banane=banana;
die Tomate=tomato; das Ei=egg; die Kartoffel=potato; das Fleisch=meat; kaufen=to buy; brauchen=to need;
kosten=to cost; teuer=expensive; billig=cheap; viel=much, a lot; wie viel=how much; das Kilo=kilo; die Tasche=bag""",
        "dialogue": """Mia|Was brauchen wir?|What do we need?
Jonas|Wir brauchen Brot, Käse und sechs Eier.|We need bread, cheese and six eggs.
Mia|Haben wir noch Tomaten?|Do we still have tomatoes?
Jonas|Nein, wir haben keine Tomaten. Und keine Äpfel.|No, we have no tomatoes. And no apples.
Mia|Entschuldigung, was kosten die Äpfel?|Excuse me, how much are the apples?
Verkäufer|Ein Kilo kostet zwei Euro.|A kilo costs two euros.
Mia|Gut, ich nehme zwei Kilo.|Good, I'll take two kilos.""",
        "grammar": ("Plurals and kein", """German plurals don't follow one rule, so learn the plural with each noun. Common patterns:

- **-n / -en**: die Banane → die Banane**n**, die Tomate → die Tomate**n**
- **-e** (often with an umlaut): das Brot → die Brot**e**, der Apfel → die **Ä**pfel
- **-er**: das Ei → die Ei**er**, das Kind → die Kind**er**
- **-s**: das Kilo → die Kilo**s**

In the plural the article is always **die**: die Äpfel, die Eier.

**kein** means "no" or "not a". Use **keine** for die words and all plurals: Wir haben **keine** Tomaten.""",
                    "Ich kaufe drei Bananen.=I'm buying three bananas.; Die Äpfel sind billig.=The apples are cheap.; Wir haben kein Brot.=We have no bread.; Ich brauche keine Eier.=I don't need any eggs."),
        "exercises": """ein Apfel, zwei ___|Äpfel|Apfels|Apfeln
ein Ei, sechs ___|Eier|Eis|Eien
eine Tomate, vier ___|Tomaten|Tomates|Tomate
Wir haben ___ Brot. (no)|kein|keine|keinen
Ich brauche ___ Bananen. (no)|keine|kein|keinen
Was ___ der Käse?|kostet|kosten|koste
___ Äpfel sind teuer.|Die|Der|Das""",
    },
    {
        "id": "wohnung", "title": "Die Wohnung", "subtitle": "Rooms, furniture and describing things",
        "words": """die Wohnung=apartment; das Haus=house; das Zimmer=room; die Küche=kitchen; das Bad=bathroom;
das Schlafzimmer=bedroom; der Tisch=table; der Stuhl=chair; das Bett=bed; der Schrank=cupboard, wardrobe;
das Fenster=window; die Tür=door; groß=big; klein=small; schön=nice, beautiful; neu=new; alt=old; hell=bright;
es gibt=there is, there are""",
        "dialogue": """Tom|Deine Wohnung ist schön! Wie viele Zimmer hat sie?|Your apartment is nice! How many rooms does it have?
Lena|Sie hat drei Zimmer, eine Küche und ein Bad.|It has three rooms, a kitchen and a bathroom.
Tom|Die Küche ist groß.|The kitchen is big.
Lena|Ja, aber das Bad ist klein. Hier ist das Schlafzimmer.|Yes, but the bathroom is small. Here is the bedroom.
Tom|Ist das Bett neu?|Is the bed new?
Lena|Ja. Aber der Schrank ist alt. Es gibt auch einen Balkon.|Yes. But the wardrobe is old. There's a balcony too.""",
        "grammar": ("er, sie, es for things, and es gibt", """In German, things are "he", "she" or "it" depending on their gender:

- der Tisch → **er**: Der Tisch ist neu. **Er** ist neu.
- die Küche → **sie**: Die Küche ist groß. **Sie** ist groß.
- das Bad → **es**: Das Bad ist klein. **Es** ist klein.

After **sein**, adjectives take no ending: Das Zimmer ist **hell**.

**Es gibt** means "there is / there are" and takes the same forms as ordering: **Es gibt einen Tisch**, **eine Küche**, **ein Bad**.""",
                    "Der Stuhl ist alt. Er ist alt.=The chair is old. It is old.; Die Wohnung ist hell. Sie ist hell.=The apartment is bright. It is bright.; Es gibt ein Fenster.=There is a window.; Es gibt einen Schrank.=There is a wardrobe."),
        "exercises": """Der Tisch ist neu. ___ ist neu.|Er|Sie|Es
Die Küche ist klein. ___ ist klein.|Sie|Er|Es
Das Bett ist groß. ___ ist groß.|Es|Er|Sie
Es gibt ___ Stuhl.|einen|ein|eine
Es gibt ___ Küche.|eine|einen|ein
Es gibt ___ Bad.|ein|einen|eine
Die Wohnung ___ schön.|ist|sind|bin""",
    },
    {
        "id": "stadt", "title": "In der Stadt", "subtitle": "Places in town and asking the way",
        "words": """der Bahnhof=train station; die Bank=bank; die Post=post office; die Apotheke=pharmacy;
das Krankenhaus=hospital; die Straße=street; der Platz=square; der Bus=bus; der Zug=train; links=left;
rechts=right; geradeaus=straight ahead; hier=here; dort=there; weit=far; nah=near; fahren=to go (by vehicle);
suchen=to look for""",
        "dialogue": """Tourist|Entschuldigung, wo ist der Bahnhof?|Excuse me, where is the train station?
Frau|Der Bahnhof ist nicht weit. Gehen Sie geradeaus.|The station isn't far. Go straight ahead.
Tourist|Und dann?|And then?
Frau|Dann gehen Sie links. Der Bahnhof ist am Marktplatz.|Then go left. The station is on the market square.
Tourist|Gibt es dort eine Apotheke?|Is there a pharmacy there?
Frau|Ja, die Apotheke ist im Bahnhof.|Yes, the pharmacy is in the station.
Tourist|Vielen Dank!|Thank you very much!""",
        "grammar": ("Where? im, am, in der", """To say where something is, German uses **in** or **an** with a changed article:

- der / das words: **in dem → im**, **an dem → am**: **im** Bahnhof, **im** Haus, **am** Platz
- die words: **in der**, **an der**: **in der** Stadt, **in der** Apotheke

To give directions politely, put the verb first and add **Sie**: **Gehen Sie** links. **Fahren Sie** geradeaus.""",
                    "Ich bin im Supermarkt.=I'm in the supermarket.; Die Bank ist in der Stadt.=The bank is in town.; Wir sind am Bahnhof.=We are at the station.; Gehen Sie rechts.=Go right."),
        "exercises": """Ich bin ___ Bahnhof.|im|in der|in
Sie ist ___ Apotheke.|in der|im|am
Wir sind ___ Haus.|im|in der|an der
Wo ___ die Post?|ist|sind|bin
___ Sie geradeaus.|Gehen|Gehst|Gehe
Der Bahnhof ist nicht ___. (far)|weit|wo|aus
Die Bank ist ___ Stadt.|in der|im|am""",
    },
    {
        "id": "freizeit", "title": "Freizeit", "subtitle": "Hobbies, likes and what you can do",
        "words": """die Freizeit=free time; das Hobby=hobby; die Musik=music; der Sport=sport; der Film=film, movie;
das Buch=book; lesen=to read; hören=to listen, to hear; schwimmen=to swim; kochen=to cook; tanzen=to dance;
reisen=to travel; können=can, to be able to; gern=gladly (like doing); oft=often; nie=never; manchmal=sometimes;
zusammen=together""",
        "dialogue": """Sara|Was machst du gern in der Freizeit?|What do you like doing in your free time?
Emre|Ich höre gern Musik und ich koche gern.|I like listening to music and I like cooking.
Sara|Kannst du gut kochen?|Can you cook well?
Emre|Ja, ziemlich gut. Und du? Was sind deine Hobbys?|Yes, quite well. And you? What are your hobbies?
Sara|Ich schwimme oft und ich lese gern Bücher.|I swim often and I like reading books.
Emre|Ich kann nicht schwimmen!|I can't swim!
Sara|Kein Problem. Wir können zusammen kochen.|No problem. We can cook together.""",
        "grammar": ("gern and können", """To say you like doing something, add **gern** after the verb: Ich **koche gern**. (I like cooking.) For "don't like", use **nicht gern**: Ich tanze **nicht gern**.

**können** (can) is irregular:

- ich **kann**
- du **kannst**
- er / sie / es **kann**
- wir **können**
- sie / Sie **können**

With können, the second verb goes to the **end** of the sentence in its dictionary form: Ich **kann** gut **schwimmen**.""",
                    "Ich lese gern.=I like reading.; Er tanzt nicht gern.=He doesn't like dancing.; Kannst du kochen?=Can you cook?; Wir können morgen schwimmen.=We can swim tomorrow."),
        "exercises": """Ich ___ gut kochen.|kann|kannst|können
___ du schwimmen?|Kannst|Kann|Können
Wir ___ zusammen tanzen.|können|kann|kannst
Ich höre ___ Musik. (I like to)|gern|kann|bin
Sie ___ gern Bücher. (she)|liest|lese|lesen
Ich kann nicht ___.|schwimmen|schwimme|schwimmst
Er ___ oft.|kocht|koche|kochen""",
    },
    {
        "id": "termine", "title": "Termine", "subtitle": "Days of the week and making plans",
        "words": """der Montag=Monday; der Dienstag=Tuesday; der Mittwoch=Wednesday; der Donnerstag=Thursday;
der Freitag=Friday; der Samstag=Saturday; der Sonntag=Sunday; die Woche=week; das Wochenende=weekend;
der Termin=appointment; die Zeit=time; anrufen=to call (phone); aufstehen=to get up; einkaufen=to shop;
treffen=to meet; wann=when; am=on (day); vielleicht=maybe""",
        "dialogue": """Lisa|Hast du am Samstag Zeit?|Do you have time on Saturday?
Paul|Am Samstag kaufe ich ein. Aber am Sonntag habe ich Zeit.|On Saturday I'm going shopping. But on Sunday I have time.
Lisa|Gut! Treffen wir uns am Sonntag?|Good! Shall we meet on Sunday?
Paul|Gern. Wann?|Gladly. When?
Lisa|Um drei Uhr? Ich stehe am Wochenende spät auf.|At three? I get up late on weekends.
Paul|Okay. Ich rufe dich am Sonntag an.|Okay. I'll call you on Sunday.""",
        "grammar": ("Separable verbs and am + day", """Some verbs have a prefix that splits off and goes to the **end** of the sentence:

- **auf**stehen: Ich **stehe** um sieben Uhr **auf**.
- **an**rufen: Ich **rufe** dich morgen **an**.
- **ein**kaufen: Wir **kaufen** am Samstag **ein**.

With days, use **am**: **am Montag**, **am Wochenende**. With clock times, use **um**: **um drei Uhr**.""",
                    "Ich stehe früh auf.=I get up early.; Er ruft seine Mutter an.=He calls his mother.; Am Freitag kaufen wir ein.=On Friday we go shopping.; Wann stehst du auf?=When do you get up?"),
        "exercises": """Ich stehe um acht Uhr ___.|auf|an|ein
Er ruft mich morgen ___.|an|auf|ein
Wir kaufen am Samstag ___.|ein|an|auf
___ Montag arbeite ich.|Am|Um|Im
___ neun Uhr habe ich einen Termin.|Um|Am|In
Wann ___ du auf?|stehst|stehe|steht
Hast du am Sonntag ___?|Zeit|Uhr|wann""",
    },
    {
        "id": "gestern", "title": "Was hast du gemacht?", "subtitle": "Talking about the past",
        "words": """gestern=yesterday; letzte Woche=last week; machen=to do, to make; gemacht=done, made; gekauft=bought;
gespielt=played; gelernt=learned; gearbeitet=worked; gegessen=eaten; getrunken=drunk; gegangen=gone;
gefahren=gone (by vehicle), driven; gekommen=come; geblieben=stayed; der Urlaub=vacation; zu Hause=at home;
schon=already; noch nicht=not yet""",
        "dialogue": """Mia|Was hast du gestern gemacht?|What did you do yesterday?
Ben|Ich habe gearbeitet und dann Fußball gespielt. Und du?|I worked and then played soccer. And you?
Mia|Ich bin in die Stadt gefahren und habe eine Tasche gekauft.|I went into town and bought a bag.
Ben|Hast du schon gegessen?|Have you eaten already?
Mia|Nein, noch nicht. Gestern habe ich nur Kuchen gegessen.|No, not yet. Yesterday I only ate cake.
Ben|Dann gehen wir jetzt essen!|Then let's go eat now!""",
        "grammar": ("The Perfekt: haben or sein + ge-", """To talk about the past, spoken German uses the **Perfekt**: a form of **haben** or **sein** in second place, and the **ge-** form of the verb at the end.

- Ich **habe** Fußball **gespielt**. (I played soccer.)
- Er **hat** ein Buch **gekauft**. (He bought a book.)

Regular verbs form it with **ge- ... -t**: machen → **gemacht**, lernen → **gelernt**. Many common verbs are irregular and end in **-en**: essen → **gegessen**, trinken → **getrunken**.

Verbs of movement or change use **sein**: Ich **bin** nach Berlin **gefahren**. Sie **ist** nach Hause **gegangen**. Wir **sind** zu Hause **geblieben**.""",
                    "Ich habe Deutsch gelernt.=I learned German.; Wir haben Pizza gegessen.=We ate pizza.; Sie ist nach Wien gefahren.=She went to Vienna.; Bist du zu Hause geblieben?=Did you stay at home?"),
        "exercises": """Ich ___ Fußball gespielt.|habe|bin|hat
Er ___ nach Berlin gefahren.|ist|hat|habe
Wir ___ Pizza gegessen.|haben|sind|hat
Ich ___ zu Hause geblieben.|bin|habe|ist
Was hast du gestern ___?|gemacht|machen|macht
Sie hat ein Buch ___.|gekauft|kaufen|kauft
___ du schon gegessen?|Hast|Bist|Hat""",
    },
]
