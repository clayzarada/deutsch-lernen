"""The built-in course, level A1: 20 short lessons for learners without a textbook (A2 is in lessons_a2.py).

Each lesson: words ("German=English", nouns with their article), a dialogue ("Speaker|German|English"),
one grammar point (title, short explanation, examples "German=English") and exercises
("Sentence with ___|answer|wrong choice|wrong choice"). app/lessons.py turns these into lessons and quizzes.
"""

LESSONS = [
    {
        "id": "hallo", "title": "Hallo!", "subtitle": "Greetings and saying your name",
        "level": "A1", "unit": "First contacts",
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
        "level": "A1", "unit": "First contacts",
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
        "level": "A1", "unit": "Numbers and time",
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
        "level": "A1", "unit": "Food and drink",
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
        "level": "A1", "unit": "People",
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
        "level": "A1", "unit": "Daily life",
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
        "level": "A1", "unit": "Shopping",
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
        "level": "A1", "unit": "At home",
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
        "level": "A1", "unit": "In town",
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
        "level": "A1", "unit": "Free time",
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
        "level": "A1", "unit": "Daily life",
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
        "level": "A1", "unit": "Daily life",
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
    {
        "id": "beruf", "title": "Arbeit und Beruf", "subtitle": "Jobs, workplaces and yes/no questions",
        "level": "A1", "unit": "Work",
        "words": """der Beruf=job, profession; der Lehrer=teacher (male); die Lehrerin=teacher (female); der Arzt=doctor (male);
die Ärztin=doctor (female); der Verkäufer=shop assistant (male); die Verkäuferin=shop assistant (female);
der Student=student (male); die Studentin=student (female); das Büro=office; die Firma=company; das Geld=money;
die Stunde=hour; als=as (a job); studieren=to study (at university); verdienen=to earn; interessant=interesting;
anstrengend=tiring, hard""",
        "dialogue": """Jonas|Was sind Sie von Beruf, Frau Yilmaz?|What do you do for a living, Ms. Yilmaz?
Frau Yilmaz|Ich bin Ärztin. Ich arbeite im Krankenhaus.|I'm a doctor. I work in the hospital.
Jonas|Ist die Arbeit interessant?|Is the work interesting?
Frau Yilmaz|Ja, sehr. Aber sie ist auch anstrengend. Und Sie? Arbeiten Sie auch?|Yes, very. But it's also tiring. And you? Do you work too?
Jonas|Ich studiere noch. Aber am Wochenende arbeite ich als Verkäufer.|I'm still a student. But at the weekend I work as a shop assistant.
Frau Yilmaz|Verdienen Sie gut?|Do you earn well?
Jonas|Es geht. Zwölf Euro pro Stunde.|It's okay. Twelve euros an hour.""",
        "grammar": ("Jobs with -in, and yes/no questions", """For most jobs, the woman's form adds **-in**: der Lehrer → die Lehrer**in**, der Verkäufer → die Verkäufer**in**, der Student → die Student**in**. Some also get an umlaut: der Arzt → die **Ä**rzt**in**.

To say what your job is, use **no article**: Ich bin **Lehrer**. Sie ist **Ärztin**. Or with **als**: Ich arbeite **als** Verkäufer.

A yes/no question starts with the **verb**: **Arbeiten Sie** im Büro? **Ist** die Arbeit interessant? **Studierst du**? The answer is ja or nein.""",
                    "Ich bin Lehrerin.=I'm a teacher.; Er arbeitet als Verkäufer.=He works as a shop assistant.; Studierst du?=Are you a student?; Ist die Firma groß?=Is the company big?"),
        "exercises": """Sie ist ___. (doctor)|Ärztin|Arzt|Ärzte
Er ist ___. (teacher)|Lehrer|Lehrerin|Lehrers
___ du in Berlin?|Studierst|Studiere|Studiert
___ Sie im Büro?|Arbeiten|Arbeitet|Arbeitest
Ich arbeite ___ Verkäuferin.|als|wie|am
Was ___ Sie von Beruf?|sind|ist|bist
Er ___ zehn Euro pro Stunde.|verdient|verdiene|verdienst""",
    },
    {
        "id": "datum", "title": "Wann hast du Geburtstag?", "subtitle": "Months, dates and birthdays",
        "level": "A1", "unit": "Numbers and time",
        "words": """der Januar=January; der Februar=February; der März=March; der April=April; der Mai=May; der Juni=June;
der Juli=July; der August=August; der September=September; der Oktober=October; der November=November;
der Dezember=December; der Geburtstag=birthday; das Datum=date; der Monat=month; feiern=to celebrate;
die Party=party; einladen=to invite""",
        "dialogue": """Mia|Wann hast du Geburtstag, Emre?|When is your birthday, Emre?
Emre|Am vierten Mai. Und du?|On the fourth of May. And you?
Mia|Im Dezember, am zwanzigsten Dezember.|In December, on the twentieth of December.
Emre|Welches Datum ist heute?|What's the date today?
Mia|Heute ist der dritte Mai. Dann hast du ja morgen Geburtstag!|Today is the third of May. So your birthday is tomorrow!
Emre|Ja! Ich feiere am Samstag. Ich lade dich ein.|Yes! I'm celebrating on Saturday. I'm inviting you.
Mia|Danke! Ich komme gern zur Party.|Thanks! I'd love to come to the party.""",
        "grammar": ("Dates: der dritte Mai, am dritten Mai", """Dates use **ordinal numbers** (first, second, third). Up to 19, add **-te**; from 20, add **-ste**:

- erste (1st), zweite (2nd), **dritte** (3rd), vierte (4th), **siebte** (7th), achte (8th)
- neunzehnte (19th), zwanzig**ste** (20th), einunddreißig**ste** (31st)

In writing, a dot after the number makes it an ordinal: **der 3. Mai**.

Which date is it? **der** dritte Mai: Heute ist **der dritte** Mai.

On which date? **am** + **-en**: Ich habe **am dritten** Mai Geburtstag.

With months, use **im**: **im** Mai, **im** Dezember.""",
                    "Heute ist der erste April.=Today is the first of April.; Ich habe am zweiten Juni Geburtstag.=My birthday is on the second of June.; Im August habe ich Urlaub.=I'm on holiday in August.; Die Party ist am 20. Dezember.=The party is on the 20th of December."),
        "exercises": """Heute ist der ___ Mai. (3rd)|dritte|dritten|dreite
Ich habe am ___ Juli Geburtstag. (1st)|ersten|erste|einsten
___ Januar ist es kalt.|Im|Am|Um
Mein Geburtstag ist ___ zehnten März.|am|im|um
Heute ist der ___ Oktober. (7th)|siebte|siebten|siebzehnte
Wir feiern am ___ Juni. (20th)|zwanzigsten|zwanzigten|zwanzigste
Ich ___ dich zur Party ein.|lade|lädst|laden""",
    },
    {
        "id": "arzt", "title": "Beim Arzt", "subtitle": "The body, feeling ill and the doctor's advice",
        "level": "A1", "unit": "Health",
        "words": """der Kopf=head; der Bauch=stomach, belly; der Hals=throat, neck; der Rücken=back; der Arm=arm; das Bein=leg;
das Auge=eye; das Fieber=fever, temperature; die Erkältung=cold (illness); die Tablette=tablet, pill;
das Rezept=prescription; die Praxis=doctor's practice; krank=ill, sick; gesund=healthy; wehtun=to hurt;
bleiben=to stay""",
        "dialogue": """Ärztin|Guten Tag, Herr Brandt. Was fehlt Ihnen?|Hello, Mr. Brandt. What's the matter?
Herr Brandt|Ich habe Kopfschmerzen und mein Hals tut weh.|I have a headache and my throat hurts.
Ärztin|Haben Sie auch Fieber?|Do you have a temperature too?
Herr Brandt|Ja, ein bisschen. Seit gestern.|Yes, a little. Since yesterday.
Ärztin|Sie haben eine Erkältung. Bleiben Sie zwei Tage im Bett und trinken Sie viel Tee.|You have a cold. Stay in bed for two days and drink a lot of tea.
Herr Brandt|Brauche ich Tabletten?|Do I need tablets?
Ärztin|Ja, hier ist ein Rezept. Nehmen Sie morgens und abends eine Tablette. Gute Besserung!|Yes, here is a prescription. Take one tablet in the morning and one in the evening. Get well soon!""",
        "grammar": ("The imperative: Trink! Trinken Sie!", """To tell someone what to do, use the **imperative**. The verb comes **first**.

- **Sie** (formal): verb + Sie: **Bleiben Sie** im Bett! **Nehmen Sie** eine Tablette!
- **du**: the du form without **-st** and without du: du trinkst → **Trink** viel Tee! du gehst → **Geh** nach Hause!
- **ihr**: the ihr form without ihr: ihr kommt → **Kommt** bitte!

Verbs that change e to i keep the i: du nimmst → **Nimm** eine Tablette! But a → ä doesn't: du schläfst → **Schlaf** gut!

**sein** is irregular: **Sei** ruhig! **Seien Sie** pünktlich!

Add **bitte** to sound polite: **Kommen Sie bitte** herein.""",
                    "Trink viel Wasser!=Drink a lot of water!; Nimm eine Tablette!=Take a tablet!; Bleiben Sie zu Hause!=Stay at home!; Kommt bitte morgen!=Please come tomorrow! (to several people)"),
        "exercises": """___ Sie bitte im Bett!|Bleiben|Bleibst|Bleibt
___ viel Tee! (du)|Trink|Trinkst|Trinkt
___ eine Tablette! (du)|Nimm|Nehm|Nimmst
___ Sie zwei Tabletten am Tag!|Nehmen|Nimm|Nehmt
Mein Kopf tut ___.|weh|krank|gut
Ich habe Fieber. Ich bin ___.|krank|gesund|gut
___ ruhig, Paul!|Sei|Bist|Sein""",
    },
    {
        "id": "kleidung", "title": "Kleidung kaufen", "subtitle": "Clothes, colors and the accusative",
        "level": "A1", "unit": "Shopping",
        "words": """die Kleidung=clothes; die Hose=trousers, pants; das Hemd=shirt; die Jacke=jacket; der Rock=skirt;
das Kleid=dress; der Schuh=shoe; der Pullover=sweater, jumper; die Größe=size; die Farbe=color; rot=red;
blau=blue; schwarz=black; weiß=white; grün=green; anprobieren=to try on; passen=to fit""",
        "dialogue": """Verkäuferin|Guten Tag. Kann ich Ihnen helfen?|Hello. Can I help you?
Lisa|Ja, ich suche eine Jacke. Haben Sie die Jacke hier auch in Blau?|Yes, I'm looking for a jacket. Do you have this jacket in blue too?
Verkäuferin|Ja. Welche Größe haben Sie?|Yes. What size are you?
Lisa|Größe 38. Kann ich sie anprobieren?|Size 38. Can I try it on?
Verkäuferin|Natürlich. Und? Passt sie?|Of course. Well? Does it fit?
Lisa|Ja, sie passt gut. Und der Pullover hier ist auch schön. Ich nehme ihn auch.|Yes, it fits well. And this sweater here is nice too. I'll take it too.
Verkäuferin|Gern. Das macht zusammen 89 Euro.|Certainly. That's 89 euros altogether.""",
        "grammar": ("The accusative: den, einen, ihn", """The person or thing a verb acts on (the **object**) is in the **accusative**. Only der words change:

- der → **den**: Ich kaufe **den** Rock.
- ein → **einen**, kein → **keinen**: Ich suche **einen** Pullover.
- die, das and plurals stay the same: Ich nehme **die** Jacke, **das** Hemd, **die** Schuhe.

Pronouns work the same way: der Rock → **ihn**, die Jacke → **sie**, das Kleid → **es**. Ich nehme **ihn**. Ich probiere **sie** an.

Verbs like **kaufen, nehmen, suchen, brauchen, haben, möchten** and **es gibt** take the accusative.""",
                    "Ich kaufe den Pullover.=I'm buying the sweater.; Sie sucht einen Rock.=She's looking for a skirt.; Der Rock ist schön. Ich nehme ihn.=The skirt is nice. I'll take it.; Die Schuhe passen gut.=The shoes fit well."),
        "exercises": """Ich kaufe ___ Rock.|den|der|dem
Ich suche ___ Pullover.|einen|ein|eine
Ich nehme ___ Jacke.|die|den|der
Das Hemd ist schön. Ich nehme ___.|es|ihn|sie
Der Rock ist zu klein. Ich nehme ___ nicht.|ihn|er|es
Kann ich die Hose ___?|anprobieren|anprobiere|probieren an
Die Schuhe ___ gut.|passen|passt|passe""",
    },
    {
        "id": "wetter", "title": "Das Wetter", "subtitle": "Weather and the seasons",
        "level": "A1", "unit": "Weather",
        "words": """das Wetter=weather; die Sonne=sun; der Regen=rain; der Schnee=snow; der Wind=wind; die Wolke=cloud;
der Frühling=spring; der Sommer=summer; der Herbst=autumn, fall; der Winter=winter; regnen=to rain;
schneien=to snow; scheinen=to shine; warm=warm; kalt=cold; heiß=hot; sonnig=sunny; der Grad=degree""",
        "dialogue": """Paul|Wie ist das Wetter in Hamburg?|What's the weather like in Hamburg?
Lena|Nicht so gut. Es regnet und es ist windig.|Not so good. It's raining and it's windy.
Paul|Hier in München scheint die Sonne. Es ist warm, fünfundzwanzig Grad!|Here in Munich the sun is shining. It's warm, twenty-five degrees!
Lena|Toll! Im Sommer regnet es in Hamburg oft.|Great! In summer it often rains in Hamburg.
Paul|Und im Winter? Schneit es viel?|And in winter? Does it snow a lot?
Lena|Manchmal. Aber es ist oft kalt und grau.|Sometimes. But it's often cold and grey.""",
        "grammar": ("Weather with es: es regnet, es ist kalt", """Weather sentences start with **es** (it), as in English:

- **Es regnet.** (It's raining.) **Es schneit.** (It's snowing.)
- **Es ist** kalt / warm / sonnig / windig.
- Temperatures: **Es ist zwanzig Grad.** Below zero: **minus fünf Grad**.

But the sun has its own verb: **Die Sonne scheint.**

Seasons and months use **im**: **im** Sommer, **im** Winter, **im** Juli. With a time word first, the verb stays second and es moves behind it: **Im Herbst regnet es** oft.""",
                    "Es ist heute sehr heiß.=It's very hot today.; Im Winter schneit es.=It snows in winter.; Morgen regnet es.=It's going to rain tomorrow.; Die Sonne scheint.=The sun is shining."),
        "exercises": """Im Winter ___ es oft.|schneit|schneien|schneist
Heute ___ es kalt.|ist|hat|macht
Die Sonne ___.|scheint|scheinen|regnet
___ Sommer ist es heiß.|Im|Am|Um
Im Herbst regnet ___ viel.|es|er|sie
Es ist ___ Grad. (–5 °C)|minus fünf|fünf minus|unter fünf
Wie ___ das Wetter in Berlin?|ist|hat|geht""",
    },
    {
        "id": "bahn", "title": "Mit dem Zug", "subtitle": "Tickets, timetables, müssen and wollen",
        "level": "A1", "unit": "Travel",
        "words": """die Fahrkarte=ticket; der Fahrplan=timetable; das Gleis=platform, track; die Abfahrt=departure;
die Ankunft=arrival; die Reise=trip, journey; der Schalter=ticket desk, counter; die Verspätung=delay;
abfahren=to leave, to depart; ankommen=to arrive; umsteigen=to change (trains); besuchen=to visit;
müssen=must, to have to; wollen=to want; einfach=one-way; simple; hin und zurück=return, round trip;
pünktlich=on time""",
        "dialogue": """Ben|Guten Tag. Ich möchte eine Fahrkarte nach Köln, bitte.|Hello. I'd like a ticket to Cologne, please.
Mitarbeiterin|Einfach oder hin und zurück?|One-way or return?
Ben|Hin und zurück. Ich will meine Schwester besuchen. Wann fährt der Zug ab?|Return. I want to visit my sister. When does the train leave?
Mitarbeiterin|Um 9.15 Uhr von Gleis 4. Sie müssen in Frankfurt umsteigen.|At 9:15 from platform 4. You have to change in Frankfurt.
Ben|Und wann komme ich in Köln an?|And when do I arrive in Cologne?
Mitarbeiterin|Um 13.40 Uhr, wenn der Zug pünktlich ist. Das macht 98 Euro.|At 1:40 p.m., if the train is on time. That's 98 euros.""",
        "grammar": ("müssen and wollen", """**müssen** (have to) and **wollen** (want to) work like **können**: the modal verb is in second place, and the second verb goes to the **end** in its dictionary form.

- müssen: ich **muss**, du **musst**, er/sie **muss**, wir **müssen**, ihr **müsst**, sie/Sie **müssen**
- wollen: ich **will**, du **willst**, er/sie **will**, wir **wollen**, ihr **wollt**, sie/Sie **wollen**

ich and er/sie have the same form, with no ending: ich **muss**, er **muss**.

Careful: **ich will** means "I want", not "I will"! **Ich möchte** is the more polite way to say what you want.

Separable verbs stay in one piece at the end: Ich muss in Frankfurt **umsteigen**.""",
                    "Ich muss um sechs Uhr aufstehen.=I have to get up at six.; Wir wollen nach Wien fahren.=We want to go to Vienna.; Musst du heute arbeiten?=Do you have to work today?; Er will seinen Bruder besuchen.=He wants to visit his brother."),
        "exercises": """Ich ___ heute arbeiten.|muss|musst|müssen
Du ___ in Mannheim umsteigen.|musst|muss|müsst
Wir ___ nach Berlin fahren. (want)|wollen|will|wollt
___ du mitkommen? (want)|Willst|Will|Wollt
Sie muss in Köln ___.|umsteigen|umsteigt|steigt um
Der Zug fährt um acht Uhr ___.|ab|an|um
Wann ___ der Zug in Hamburg an?|kommt|kommen|kommst""",
    },
    {
        "id": "wo", "title": "Wo ist mein Handy?", "subtitle": "Where things are: prepositions with the dative",
        "level": "A1", "unit": "At home",
        "words": """das Handy=mobile phone; der Schlüssel=key; das Sofa=sofa; das Regal=shelf; die Lampe=lamp; die Wand=wall;
das Bild=picture; auf=on (top of); unter=under; neben=next to; vor=in front of; hinter=behind;
zwischen=between; an=on (a wall), at; liegen=to lie (flat), to be; stehen=to stand; hängen=to hang""",
        "dialogue": """Tom|Lena, wo ist mein Handy?|Lena, where is my phone?
Lena|Liegt es nicht auf dem Tisch?|Isn't it on the table?
Tom|Nein. Und mein Schlüssel ist auch weg!|No. And my key is gone too!
Lena|Der Schlüssel hängt an der Wand, neben der Tür.|The key is hanging on the wall, next to the door.
Tom|Ah, danke. Aber das Handy?|Ah, thanks. But the phone?
Lena|Schau mal unter dem Sofa. Oder hinter der Lampe im Regal.|Have a look under the sofa. Or behind the lamp on the shelf.
Tom|Da ist es, zwischen dem Sofa und dem Regal!|There it is, between the sofa and the shelf!""",
        "grammar": ("Where? Prepositions with the dative", """To say **where** something is, use **in, an, auf, unter, neben, vor, hinter, zwischen** with the **dative**. The articles change:

- der → **dem**: auf **dem** Tisch, unter **dem** Stuhl
- das → **dem**: neben **dem** Sofa, **im** (= in dem) Regal
- die → **der**: an **der** Wand, hinter **der** Tür
- plural die → **den**, and the noun adds -n: zwischen **den** Büchern

Short forms: in dem → **im**, an dem → **am**.

The verbs that go with them: **liegen** (lying flat), **stehen** (standing up), **hängen** (hanging).""",
                    "Das Buch liegt auf dem Tisch.=The book is on the table.; Die Lampe steht neben dem Bett.=The lamp is next to the bed.; Das Bild hängt an der Wand.=The picture is on the wall.; Die Katze ist unter dem Sofa.=The cat is under the sofa."),
        "exercises": """Das Handy liegt auf ___ Tisch.|dem|den|der
Die Brille liegt neben ___ Lampe.|der|dem|die
Der Schlüssel hängt an ___ Wand.|der|dem|die
Die Schuhe stehen unter ___ Bett.|dem|der|das
Der Hund liegt ___ dem Sofa. (under)|unter|zwischen|hinten
Das Bild ___ an der Wand.|hängt|liegt|sitzt
Die Bank ist ___ der Post und dem Supermarkt.|zwischen|neben|hinter""",
    },
    {
        "id": "unterwegs", "title": "Unterwegs in der Stadt", "subtitle": "Getting around: mit, zu, nach, von, bei",
        "level": "A1", "unit": "In town",
        "words": """das Auto=car; das Fahrrad=bicycle; die U-Bahn=underground, subway; die Straßenbahn=tram;
die Haltestelle=stop (bus, tram); die Ampel=traffic light; das Kino=cinema; das Museum=museum; der Park=park;
zu=to (a place or person); nach=to (a city or country); after; von=from; bei=at (someone's place), near;
nach Hause=home (going home); zu Fuß=on foot""",
        "dialogue": """Sara|Wie kommst du zur Arbeit, Jonas?|How do you get to work, Jonas?
Jonas|Mit dem Fahrrad. Und du? Fährst du mit dem Auto?|By bike. And you? Do you drive?
Sara|Nein, ich fahre mit der U-Bahn. Aber heute gehe ich zu Fuß zum Kino.|No, I take the underground. But today I'm walking to the cinema.
Jonas|Wo ist das Kino?|Where is the cinema?
Sara|Beim Park. Ich gehe bis zur Ampel und dann links.|By the park. I walk to the traffic light and then turn left.
Jonas|Und nach dem Film?|And after the film?
Sara|Dann fahre ich mit der Straßenbahn nach Hause.|Then I take the tram home.""",
        "grammar": ("mit, zu, nach, von, bei: always dative", """Some prepositions **always** take the dative: **mit, zu, nach, von, bei, aus**.

- der / das → **dem**: mit **dem** Auto, mit **dem** Fahrrad
- die → **der**: mit **der** U-Bahn, von **der** Arbeit

Short forms are very common: zu dem → **zum**, zu der → **zur**, bei dem → **beim**, von dem → **vom**: Ich gehe **zum** Arzt. Ich fahre **zur** Arbeit.

Where to? **zu** + places and people (**zum** Bahnhof, **zu** Anna), **nach** + cities and countries (**nach** Berlin), and **nach Hause** (home).

Transport: **mit** + dative: Ich fahre **mit dem** Zug. But on foot is **zu Fuß**.""",
                    "Ich fahre mit dem Bus zur Schule.=I take the bus to school.; Wir fahren nach Wien.=We're going to Vienna.; Er geht zum Arzt.=He's going to the doctor.; Sie wohnt bei ihrer Schwester.=She lives at her sister's."),
        "exercises": """Ich fahre mit ___ Fahrrad.|dem|der|das
Sie fährt mit ___ Straßenbahn.|der|dem|die
Ich gehe ___ Arzt.|zum|zur|nach
Wir gehen ___ Arbeit.|zur|zum|nach
Im Sommer fliegen wir ___ Spanien.|nach|zu|in
Am Abend fahre ich nach ___.|Hause|Haus|Häuser
Ich komme um sechs Uhr ___ der Arbeit. (from)|von|nach|zu""",
    },
]

# Hand-written items for the A1 level test (same format as the exercises).
TEST = """Wie ___ Sie? (formal)|heißen|heißt|heiße
Ich ___ aus der Türkei.|komme|kommt|kommen
Das ___ meine Schwester.|ist|bin|sind
Hast du ___ Bruder?|einen|ein|eine
Wir haben heute ___ Zeit. (no)|keine|kein|keinen
Am Montag ___ ich nicht.|arbeite|arbeitet|arbeiten
Er ___ um sieben Uhr auf.|steht|stehe|stehen
Ich ___ gestern ins Kino gegangen.|bin|habe|hat
Sie hat eine Pizza ___.|gegessen|gegesst|essen
Ich kann heute leider nicht ___.|kommen|komme|kommst
Die Lampe steht neben ___ Bett.|dem|den|das
Ich fahre mit ___ Bus.|dem|den|der
___ Sie bitte langsam!|Sprechen|Sprichst|Spricht
Der Kaffee ist kalt. Ich trinke ___ nicht.|ihn|er|es
Wir fahren im Sommer ___ Italien.|nach|zu|in
Heute ist der ___ Juni. (2nd)|zweite|zweiten|zwei
Ich ___ einen Kaffee, bitte.|möchte|möchten|möchtest
Was ___ die Äpfel?|kosten|kostet|koste"""
