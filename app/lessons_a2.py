"""The built-in course, level A2: 20 lessons after the A1 ones in lessons_data.py, in the same format.

Themes and grammar follow the Goethe-Zertifikat A2 syllabus: the Perfekt in full, the Präteritum of sein, haben
and the modal verbs, the dative, two-way prepositions, adjective endings, comparison, reflexive verbs, verbs with
prepositions and the subordinate clauses with weil, dass, wenn and ob. Turkish is in TR at the end of the file.
"""

LESSONS = [
    {
        "id": "urlaub", "title": "Wie war der Urlaub?", "subtitle": "Holiday stories: the Perfekt in full",
        "level": "A2", "unit": "Travel",
        "words": """das Meer=sea; der Strand=beach; die Insel=island; der Ausflug=trip, excursion; das Gepäck=luggage;
der Koffer=suitcase; das Foto=photo; die Sehenswürdigkeit=sight (for tourists); besichtigen=to visit (a sight);
fotografieren=to take photos; erleben=to experience; zurückkommen=to come back; verlieren=to lose;
vergessen=to forget; passieren=to happen; wandern=to hike""",
        "dialogue": """Anna|Hallo Tim! Du bist ja ganz braun! Wie war der Urlaub?|Hi Tim! You've got a real tan! How was your holiday?
Tim|Super! Wir sind zwei Wochen auf Kreta gewesen.|Great! We were on Crete for two weeks.
Anna|Was habt ihr gemacht?|What did you do?
Tim|Wir haben viele Ausflüge gemacht und alte Sehenswürdigkeiten besichtigt. Und wir sind in den Bergen gewandert.|We went on lots of trips and visited old sights. And we hiked in the mountains.
Anna|Ist alles gut gegangen?|Did everything go well?
Tim|Fast. Am ersten Tag hat die Fluggesellschaft meinen Koffer verloren! Er ist erst nach drei Tagen angekommen.|Almost. On the first day the airline lost my suitcase! It only arrived three days later.
Anna|Oh nein! Hast du Fotos gemacht?|Oh no! Did you take photos?
Tim|Ja, ich habe sehr viel fotografiert. Ich zeige sie dir gleich.|Yes, I took lots of photos. I'll show them to you in a moment.""",
        "grammar": ("The Perfekt: every kind of participle", """You already know the Perfekt: **haben** or **sein** in second place, the participle at the end. Now the special participles:

- Separable verbs put **-ge-** after the prefix: einkaufen → ein**ge**kauft, ankommen → an**ge**kommen, zurückkommen → zurück**ge**kommen.
- Verbs starting with **be-, ver-, er-, ent-, emp-, ge-, zer-** take **no ge-**: besichtigen → besichtigt, verlieren → verloren, vergessen → vergessen, erleben → erlebt.
- Verbs ending in **-ieren** take **no ge-**: fotografieren → fotografiert, passieren → passiert.

**sein** is used for movement from one place to another (fahren, gehen, fliegen, wandern), for changes (aufstehen, einschlafen) and for **sein, bleiben, passieren**: Was **ist** passiert? Wir **sind** in Spanien gewesen.""",
                    "Wir haben die Altstadt besichtigt.=We visited the old town.; Ich habe meinen Schlüssel vergessen.=I forgot my key.; Der Zug ist pünktlich angekommen.=The train arrived on time.; Was ist passiert?=What happened?"),
        "exercises": """Wir haben das Museum ___.|besichtigt|gebesichtigt|besichtigen
Er hat seine Tasche ___.|verloren|geverloren|verliert
Ich habe am Strand viel ___.|fotografiert|gefotografiert|fotografieren
Wann bist du ___?|zurückgekommen|gezurückkommen|zurückkommst
Was ___ passiert?|ist|hat|sind
Wir ___ im Urlaub viel gewandert.|sind|haben|hat
Sie hat im Supermarkt ___.|eingekauft|geeinkauft|einkauft""",
    },
    {
        "id": "frueher", "title": "Früher war alles anders", "subtitle": "Childhood memories: war and hatte",
        "level": "A2", "unit": "People",
        "words": """die Kindheit=childhood; das Dorf=village; der Garten=garden; das Spielzeug=toy, toys;
die Großmutter=grandmother; der Großvater=grandfather; das Haustier=pet; der Hund=dog; die Katze=cat;
früher=in the past, used to; damals=back then; streng=strict; glücklich=happy; schüchtern=shy; frech=cheeky;
erzählen=to tell (a story)""",
        "dialogue": """Lea|Oma, wie war deine Kindheit?|Grandma, what was your childhood like?
Oma|Schön, aber ganz anders als heute. Wir hatten nicht viel Geld.|Nice, but very different from today. We didn't have much money.
Lea|Wo hast du damals gewohnt?|Where did you live back then?
Oma|In einem kleinen Dorf. Wir hatten einen großen Garten und einen Hund.|In a small village. We had a big garden and a dog.
Lea|Hattest du viel Spielzeug?|Did you have lots of toys?
Oma|Nein, nur eine Puppe. Aber ich war oft draußen und war sehr glücklich.|No, just a doll. But I was outside a lot and I was very happy.
Lea|Und war die Schule schwer?|And was school hard?
Oma|Nein, aber unser Lehrer war sehr streng!|No, but our teacher was very strict!""",
        "grammar": ("war and hatte: the Präteritum of sein and haben", """For **sein** and **haben**, Germans normally use the **Präteritum** (simple past), not the Perfekt. "Ich war" is shorter and more common than "ich bin gewesen".

- sein: ich **war**, du **warst**, er/sie/es **war**, wir **waren**, ihr **wart**, sie/Sie **waren**
- haben: ich **hatte**, du **hattest**, er/sie/es **hatte**, wir **hatten**, ihr **hattet**, sie/Sie **hatten**

ich and er/sie/es have the same form. Most other verbs stay in the Perfekt when you speak: Ich **war** müde und **habe** früh **geschlafen**.""",
                    "Früher war ich sehr schüchtern.=I used to be very shy.; Wir hatten eine Katze.=We had a cat.; Wo warst du gestern?=Where were you yesterday?; Hattet ihr Zeit?=Did you have time? (to several people)"),
        "exercises": """Früher ___ ich sehr frech.|war|hatte|bin
Wir ___ einen großen Garten.|hatten|waren|hattet
___ du gestern im Kino?|Warst|War|Hattest
Meine Großmutter ___ fünf Kinder.|hatte|hattest|war
Ihr ___ damals noch klein.|wart|waren|wartet
Als Kind ___ er keine Haustiere.|hatte|hattet|war
Gestern ___ das Wetter schön.|war|hatte|waren""",
    },
    {
        "id": "schulzeit", "title": "Die Schulzeit", "subtitle": "School and training: modal verbs in the past",
        "level": "A2", "unit": "Education",
        "words": """die Prüfung=exam; das Zeugnis=school report, certificate; die Note=grade, mark; das Fach=subject;
die Klasse=class, school year; die Hausaufgabe=homework; die Ausbildung=vocational training, apprenticeship;
die Universität=university; das Abitur=school-leaving exam (for university); der Unterricht=lessons, class;
die Pause=break; bestehen=to pass (an exam); dürfen=may, to be allowed to; sollen=should, to be supposed to""",
        "dialogue": """Jan|Was war dein Lieblingsfach in der Schule?|What was your favorite subject at school?
Sophie|Mathe! Aber Deutsch konnte ich nicht so gut.|Math! But I wasn't so good at German.
Jan|Musstet ihr viele Hausaufgaben machen?|Did you have to do lots of homework?
Sophie|Ja, jeden Tag. Und wir durften im Unterricht nicht mit dem Handy spielen.|Yes, every day. And we weren't allowed to play with our phones in class.
Jan|Ich wollte nach der Schule sofort arbeiten und habe eine Ausbildung gemacht.|I wanted to work right after school, so I did an apprenticeship.
Sophie|Und ich sollte studieren, aber ich wollte nicht. Meine Eltern waren nicht glücklich!|And I was supposed to go to university, but I didn't want to. My parents weren't happy!""",
        "grammar": ("Modal verbs in the past: konnte, musste, wollte", """Modal verbs use the **Präteritum** for the past, like sein and haben. Take the infinitive without its umlaut, drop **-en** and add **-te**:

- können → ich **konnte**, müssen → ich **musste**, dürfen → ich **durfte**
- wollen → ich **wollte**, sollen → ich **sollte**, mögen → ich **mochte** (g → ch)

Endings: ich konnte, du konnte**st**, er/sie konnte, wir konnte**n**, ihr konnte**t**, sie/Sie konnte**n**.

As in the present, the second verb goes to the end: Ich **musste** viel **lernen**.

**dürfen** means "be allowed to"; **sollen** means "be supposed to" (someone else wants it).""",
                    "Als Kind konnte ich nicht schwimmen.=As a child I couldn't swim.; Wir mussten jeden Tag Hausaufgaben machen.=We had to do homework every day.; Ich durfte abends nicht ausgehen.=I wasn't allowed to go out in the evening.; Er wollte Arzt werden.=He wanted to become a doctor."),
        "exercises": """Früher ___ ich nicht gut kochen.|konnte|kann|könnte
Früher ___ wir viel lernen.|mussten|musste|müssten
Er ___ Lehrer werden.|wollte|willte|wollten
Als Kind ___ ich abends nicht fernsehen.|durfte|dürfte|darfte
Ihr ___ um acht Uhr in der Schule sein.|musstet|musstest|mussten
Ich habe die Prüfung ___.|bestanden|gebestanden|bestehen
___ du als Kind schwimmen?|Konntest|Konnte|Kanntest""",
    },
    {
        "id": "geschenke", "title": "Feste und Geschenke", "subtitle": "Celebrations, presents and the dative",
        "level": "A2", "unit": "Celebrations",
        "words": """das Geschenk=present, gift; das Fest=celebration, festival; die Hochzeit=wedding; Weihnachten=Christmas;
Ostern=Easter; die Einladung=invitation; die Blume=flower; die Kerze=candle; die Torte=layer cake, gateau;
schenken=to give (as a present); geben=to give; zeigen=to show; bringen=to bring;
gratulieren=to congratulate; Herzlichen Glückwunsch!=Congratulations! Happy birthday!;
Frohe Weihnachten!=Merry Christmas!""",
        "dialogue": """Mia|Nächste Woche hat meine Mutter Geburtstag. Was soll ich ihr schenken?|It's my mother's birthday next week. What should I give her?
Ben|Schenk ihr doch Blumen. Oder eine schöne Kerze.|Why not give her flowers? Or a nice candle.
Mia|Blumen hat sie letztes Jahr schon von mir bekommen.|She already got flowers from me last year.
Ben|Und ein Buch? Sie liest doch gern.|And a book? She likes reading, doesn't she?
Mia|Gute Idee! Und meinem Vater kaufe ich eine Torte. Er isst so gern Kuchen.|Good idea! And I'll buy my father a cake. He loves cake.
Ben|Hat er auch Geburtstag?|Is it his birthday too?
Mia|Nein, aber ich bringe ihm auch etwas mit. Sonst ist er traurig!|No, but I'll bring him something too. Otherwise he'll be sad!""",
        "grammar": ("Who gets it? The dative object", """Verbs like **geben, schenken, zeigen, bringen, kaufen** often have two objects: the thing (**accusative**) and the person who gets it (**dative**).

Ich schenke **meiner Mutter** (dative) **ein Buch** (accusative).

Dative articles: der / das → **dem, einem, meinem**; die → **der, einer, meiner**; plural → **den, meinen**, and the noun adds -n: Ich gebe **dem** Kind einen Apfel. Ich zeige **den Kindern** das Foto.

Dative pronouns: ich → **mir**, du → **dir**, er / es → **ihm**, sie → **ihr**, wir → **uns**, ihr → **euch**, sie → **ihnen**, Sie → **Ihnen**.

The person usually comes before the thing: Ich gebe **dir** das Buch.""",
                    "Ich schenke meinem Bruder ein T-Shirt.=I'm giving my brother a T-shirt.; Kannst du mir das Foto zeigen?=Can you show me the photo?; Wir bringen ihr Blumen.=We're bringing her flowers.; Er gibt den Kindern Schokolade.=He gives the children chocolate."),
        "exercises": """Ich schenke ___ Vater eine Uhr. (my)|meinem|meinen|meiner
Sie gibt ___ Kind einen Apfel.|dem|den|das
Was schenkst du ___ Schwester? (your)|deiner|deinem|deine
Ich zeige ___ meine Wohnung. (you, informal)|dir|dich|du
Wir bringen ___ Blumen. (her)|ihr|sie|ihm
Er kauft ___ ein Eis. (him)|ihm|ihn|er
Herzlichen ___ zum Geburtstag!|Glückwunsch|Gratulation|Geschenk""",
    },
    {
        "id": "restaurant", "title": "Schmeckt's?", "subtitle": "In the restaurant: verbs with the dative",
        "level": "A2", "unit": "Food and drink",
        "words": """die Speisekarte=menu; die Vorspeise=starter; das Hauptgericht=main course; der Nachtisch=dessert;
das Getränk=drink; das Messer=knife; die Gabel=fork; der Löffel=spoon; das Trinkgeld=tip; schmecken=to taste;
gefallen=to please (to be liked); gehören=to belong to; helfen=to help; empfehlen=to recommend;
bestellen=to order; lecker=tasty, delicious; scharf=spicy, hot""",
        "dialogue": """Kellnerin|Guten Abend! Hier ist die Speisekarte. Kann ich Ihnen schon ein Getränk bringen?|Good evening! Here is the menu. Can I bring you a drink already?
Herr Kaya|Ja, zwei Wasser, bitte. Was können Sie uns empfehlen?|Yes, two waters, please. What can you recommend?
Kellnerin|Der Fisch ist heute sehr gut. Und als Nachtisch empfehle ich Ihnen den Apfelkuchen.|The fish is very good today. And for dessert I recommend the apple cake.
Kellnerin|Schmeckt es Ihnen?|Are you enjoying your meal?
Frau Kaya|Ja, sehr lecker! Nur die Soße ist mir ein bisschen zu scharf.|Yes, very tasty! Only the sauce is a bit too spicy for me.
Herr Kaya|Das Restaurant gefällt mir. Gehört es Ihnen?|I like the restaurant. Does it belong to you?
Kellnerin|Nein, es gehört meinem Onkel. Ich helfe ihm nur am Wochenende.|No, it belongs to my uncle. I only help him at weekends.""",
        "grammar": ("Verbs with the dative: gefallen, schmecken, helfen", """A few common verbs take a **dative** object, not an accusative one:

- **helfen**: Ich helfe **dir**. (not dich)
- **danken**: Wir danken **Ihnen**.
- **gefallen**: Das Bild gefällt **mir**. (I like the picture; literally "the picture pleases me")
- **schmecken**: Schmeckt **dir** die Suppe? (Do you like the soup?)
- **gehören**: Das Auto gehört **meinem** Vater. (belongs to)
- **passen**: Die Hose passt **mir** nicht. (doesn't fit me)
- **antworten**: Er antwortet **ihr**.

With gefallen and schmecken, the thing you like is the **subject**, so the verb agrees with it: Die Schuhe gefall**en** mir.""",
                    "Die Suppe schmeckt mir.=I like the soup.; Wie gefällt dir die Stadt?=How do you like the city?; Kannst du mir helfen?=Can you help me?; Das Buch gehört meiner Schwester.=The book belongs to my sister."),
        "exercises": """Kannst du ___ helfen? (me)|mir|mich|ich
Die Schuhe gefallen ___. (him)|ihm|ihn|er
Wie schmeckt ___ der Kuchen? (you, informal)|dir|dich|du
Die Jacke gehört ___ Bruder. (my)|meinem|meinen|mein
Die Bilder ___ mir sehr.|gefallen|gefällt|gefallt
Ich danke ___ für das Essen. (you, formal)|Ihnen|Sie|Ihr
Was können Sie uns ___?|empfehlen|empfiehlt|empfehlt""",
    },
    {
        "id": "nachbarn", "title": "Neue Nachbarn", "subtitle": "The neighborhood: aus, bei, mit, nach, seit, von, zu",
        "level": "A2", "unit": "At home",
        "words": """der Nachbar=neighbor (male); die Nachbarin=neighbor (female); das Viertel=part of town, neighborhood;
die Gegend=area; der Hof=courtyard; das Treppenhaus=stairwell; der Stock=floor (of a building);
der Aufzug=lift, elevator; der Hausmeister=caretaker; gegenüber=opposite; seit=since, for (until now);
kennenlernen=to get to know; einziehen=to move in; ruhig=quiet; laut=loud, noisy; freundlich=friendly""",
        "dialogue": """Frau Novak|Hallo! Sind Sie neu hier?|Hello! Are you new here?
Herr Bauer|Ja, ich bin vor einer Woche eingezogen. Ich wohne im dritten Stock.|Yes, I moved in a week ago. I live on the third floor.
Frau Novak|Ich wohne schon seit zehn Jahren hier, gegenüber vom Aufzug. Woher kommen Sie?|I've lived here for ten years, opposite the lift. Where are you from?
Herr Bauer|Aus Leipzig. Jetzt arbeite ich bei einer Firma in der Nähe vom Bahnhof.|From Leipzig. Now I work for a company near the station.
Frau Novak|Die Gegend ist sehr ruhig. Und der Hausmeister ist sehr freundlich.|The area is very quiet. And the caretaker is very friendly.
Herr Bauer|Das ist schön. Ich fahre jetzt mit dem Fahrrad zur Arbeit. Bis bald!|That's nice. I'm off to work on my bike now. See you soon!
Frau Novak|Kommen Sie doch am Sonntag zum Kaffee zu mir! Dann lernen wir uns kennen.|Why don't you come over for coffee on Sunday? Then we can get to know each other.""",
        "grammar": ("Prepositions with the dative", """These prepositions **always** take the dative: **aus, bei, mit, nach, seit, von, zu** and **gegenüber**.

- **aus** (from, out of): Ich komme **aus der** Schweiz.
- **bei** (at a person's place, at a company): Ich wohne **bei meinen** Eltern. Er arbeitet **bei einer** Firma.
- **mit** (with, by): **mit dem** Fahrrad
- **nach** (to a city or country; after): **nach dem** Essen
- **seit** (since, for): **seit einem** Jahr, **seit zehn** Jahren
- **von** (from, of): **vom** Arzt, ein Freund **von mir**
- **zu** (to people and places): **zu mir**, **zum** Kaffee
- **gegenüber** (opposite): **gegenüber vom** Aufzug

**seit** goes with the present tense: Ich wohne **seit** zwei Jahren hier. (I have lived here for two years.)""",
                    "Seit einem Monat wohne ich in Hamburg.=I've been living in Hamburg for a month.; Sie arbeitet bei einer Bank.=She works at a bank.; Nach dem Essen trinken wir Kaffee.=After the meal we have coffee.; Kommst du heute zu mir?=Are you coming to my place today?"),
        "exercises": """Ich wohne ___ drei Jahren in Köln.|seit|vor|ab
Er arbeitet ___ einer Bank.|bei|mit|zu
___ dem Essen gehen wir spazieren.|Nach|Seit|Bei
Sie kommt ___ der Türkei.|aus|von|nach
Kommst du heute ___ mir?|zu|nach|bei
Die Apotheke ist gegenüber ___ Bahnhof.|vom|von|zum
Ich fahre mit ___ Fahrrad zur Arbeit.|dem|den|das""",
    },
    {
        "id": "verkehr", "title": "Im Straßenverkehr", "subtitle": "Through town: durch, für, gegen, ohne, um",
        "level": "A2", "unit": "In town",
        "words": """der Verkehr=traffic; der Stau=traffic jam; die Brücke=bridge; der Weg=way, path; die Ecke=corner;
der Unfall=accident; der Führerschein=driving licence; der Radweg=cycle path; das Rathaus=town hall;
der Helm=helmet; durch=through; gegen=against, into; um=around; entlang=along; parken=to park;
vorsichtig=careful; gefährlich=dangerous""",
        "dialogue": """Tom|Entschuldigung, wie komme ich zum Rathaus?|Excuse me, how do I get to the town hall?
Passantin|Mit dem Auto? Da gibt es heute einen Stau. Es gab einen Unfall an der Brücke.|By car? There's a traffic jam there today. There was an accident at the bridge.
Tom|Nein, ich bin mit dem Fahrrad unterwegs.|No, I'm on my bike.
Passantin|Dann fahren Sie durch den Park und den Fluss entlang. Das ist ein schöner Radweg.|Then ride through the park and along the river. That's a nice cycle path.
Tom|Und dann?|And then?
Passantin|Fahren Sie um den Marktplatz herum. Das Rathaus ist an der Ecke. Aber seien Sie vorsichtig! Ohne Helm ist das gefährlich.|Ride around the market square. The town hall is on the corner. But be careful! It's dangerous without a helmet.
Tom|Vielen Dank für die Hilfe!|Thanks a lot for your help!""",
        "grammar": ("Prepositions with the accusative", """These prepositions **always** take the accusative: **durch, für, gegen, ohne, um** (and **bis**).

- **durch** (through): **durch den** Park
- **für** (for): ein Geschenk **für meinen** Vater, Danke **für die** Hilfe
- **gegen** (against, into): Er ist **gegen einen** Baum gefahren.
- **ohne** (without): **ohne den** Helm, **ohne mich**
- **um** (around; at a time): **um den** Platz herum, **um** acht Uhr

In the accusative only der words change: der → **den**, ein → **einen**. Pronouns: mich, dich, ihn, sie, es, uns, euch, sie, Sie.

**entlang** usually comes after the noun: **den** Fluss **entlang**.""",
                    "Wir gehen durch die Stadt.=We walk through the town.; Das Geschenk ist für dich.=The present is for you.; Ich fahre nie ohne meinen Helm.=I never ride without my helmet.; Das Auto ist gegen die Wand gefahren.=The car crashed into the wall."),
        "exercises": """Wir fahren durch ___ Park.|den|dem|der
Das Buch ist für ___. (you, informal)|dich|dir|du
Er geht ohne ___ Freund ins Kino. (his)|seinen|seinem|sein
Das Auto ist gegen ___ Baum gefahren.|einen|einem|ein
Sie laufen um ___ See.|den|dem|der
Geh nicht ohne ___! (me)|mich|mir|ich
Danke ___ die Einladung!|für|um|durch""",
    },
    {
        "id": "umzug", "title": "Der Umzug", "subtitle": "Moving in: wo? or wohin? with two-way prepositions",
        "level": "A2", "unit": "At home",
        "words": """der Umzug=move (to a new home); die Kiste=box, crate; die Möbel=furniture; der Teppich=carpet, rug;
der Spiegel=mirror; der Keller=cellar, basement; der Flur=hallway; der Kühlschrank=fridge; stellen=to put (upright);
legen=to put (lying down), to lay; hängen=to hang (up); tragen=to carry; auspacken=to unpack;
schwer=heavy, difficult; leicht=light, easy; über=over, above""",
        "dialogue": """Lukas|Wohin stelle ich das Sofa?|Where shall I put the sofa?
Nina|Stell es an die Wand, neben das Fenster.|Put it against the wall, next to the window.
Lukas|Und der Teppich? Wo soll er liegen?|And the rug? Where should it go?
Nina|Leg ihn vor das Sofa. Und den Spiegel hängen wir in den Flur.|Put it in front of the sofa. And we'll hang the mirror in the hallway.
Lukas|Die Kisten mit den Büchern sind so schwer! Wohin damit?|The boxes of books are so heavy! Where do they go?
Nina|In den Keller. Die Bücher packen wir morgen aus.|Into the basement. We'll unpack the books tomorrow.
Lukas|Gut. Und wo ist der Kaffee? Ich brauche eine Pause!|Good. And where's the coffee? I need a break!
Nina|In der Küche, auf dem Tisch.|In the kitchen, on the table.""",
        "grammar": ("Wo? or wohin? Two-way prepositions", """The prepositions **in, an, auf, unter, über, vor, hinter, neben, zwischen** can take two cases:

- **Wo?** (where: a place) → **dative**: Das Bild hängt **an der** Wand. Der Teppich liegt **vor dem** Sofa.
- **Wohin?** (where to: a movement) → **accusative**: Ich hänge das Bild **an die** Wand. Ich lege den Teppich **vor das** Sofa.

The verbs come in pairs:

- **stellen** (put upright) → **stehen** (stand): Ich stelle die Lampe **auf den** Tisch. Die Lampe steht **auf dem** Tisch.
- **legen** (lay down) → **liegen** (lie): Ich lege das Buch **ins** Regal. Das Buch liegt **im** Regal.
- **hängen** (hang up) → **hängen** (be hanging)

Short forms: in das → **ins**, an das → **ans**.""",
                    "Ich stelle die Flasche in den Kühlschrank.=I put the bottle in the fridge.; Die Flasche steht im Kühlschrank.=The bottle is in the fridge.; Er legt das Handy auf den Tisch.=He puts the phone on the table.; Wir hängen die Lampe über den Tisch.=We hang the lamp above the table."),
        "exercises": """Ich stelle die Lampe auf ___ Tisch.|den|dem|der
Die Lampe steht auf ___ Tisch.|dem|den|das
Leg das Buch bitte in ___ Regal!|das|dem|den
Das Bild hängt an ___ Wand.|der|die|den
Wir hängen das Bild an ___ Wand.|die|der|dem
Die Kiste ___ im Keller.|steht|stellt|stellen
Ich ___ die Jacke auf das Bett.|lege|liege|liegt""",
    },
    {
        "id": "mode", "title": "Was ziehst du an?", "subtitle": "Fashion: adjective endings after der, die, das",
        "level": "A2", "unit": "Shopping",
        "words": """der Mantel=coat; die Mütze=woolly hat, cap; der Schal=scarf; der Handschuh=glove; der Stiefel=boot;
die Bluse=blouse; der Anzug=suit; die Krawatte=tie; das T-Shirt=T-shirt; die Mode=fashion; bequem=comfortable;
eng=tight, narrow; elegant=elegant; modern=modern, fashionable; hässlich=ugly; tragen=to wear;
anziehen=to put on""",
        "dialogue": """Lisa|Wie findest du den blauen Mantel?|What do you think of the blue coat?
Mia|Der blaue Mantel ist schön. Aber gefällt dir auch der schwarze?|The blue coat is nice. But do you like the black one too?
Lisa|Nein, der ist zu eng. Ich nehme den blauen.|No, that one's too tight. I'll take the blue one.
Mia|Und brauchst du auch die warmen Handschuhe?|And do you need the warm gloves too?
Lisa|Ja, im Winter trage ich immer Handschuhe. Und die rote Mütze hier ist auch süß.|Yes, I always wear gloves in winter. And this red hat here is cute too.
Mia|Die rote Mütze passt gut zu dem neuen Mantel!|The red hat goes well with the new coat!
Lisa|Stimmt. Ich ziehe sie gleich an!|True. I'll put it on right away!""",
        "grammar": ("Adjective endings after der, die, das", """An adjective **before** a noun needs an ending. After **der, die, das** (and dieser, welcher) the ending is either **-e** or **-en**:

- **-e** in the nominative singular: **der** blau**e** Mantel, **die** rot**e** Mütze, **das** neu**e** Kleid; and in the accusative of die and das words: Ich nehme **die** rot**e** Mütze und **das** neu**e** Kleid.
- **-en** everywhere else: Ich nehme **den** blau**en** Mantel (der word, accusative), mit **dem** neu**en** Mantel (dative), **die** warm**en** Handschuhe (plural).

After sein there is no ending: Der Mantel ist **blau**.""",
                    "Der schwarze Anzug ist elegant.=The black suit is elegant.; Ich kaufe den grünen Schal.=I'm buying the green scarf.; Die weiße Bluse ist zu eng.=The white blouse is too tight.; Sie trägt die neuen Stiefel.=She's wearing the new boots."),
        "exercises": """Der ___ Mantel ist teuer.|schwarze|schwarzen|schwarzer
Ich nehme den ___ Schal.|roten|rote|roter
Die ___ Bluse gefällt mir.|weiße|weißen|weißer
Das ___ T-Shirt ist bequem.|neue|neuen|neues
Sie trägt die ___ Schuhe.|alten|alte|alter
Mit dem ___ Anzug siehst du gut aus.|grauen|graue|grauer
Der Pullover ist ___.|warm|warme|warmen""",
    },
    {
        "id": "wohnungssuche", "title": "Wohnung gesucht", "subtitle": "Flat hunting: adjective endings after ein, kein, mein",
        "level": "A2", "unit": "At home",
        "words": """die Miete=rent; die Anzeige=advert, ad; der Vermieter=landlord; die Nebenkosten=extra costs (heating, water);
die Kaution=deposit; der Balkon=balcony; die Heizung=heating; der Quadratmeter=square meter;
die Lage=location; das Erdgeschoss=ground floor; die Besichtigung=viewing; mieten=to rent; möbliert=furnished;
zentral=central; günstig=good value, cheap""",
        "dialogue": """Sara|Hast du eine neue Wohnung gefunden?|Have you found a new flat?
Emre|Vielleicht. Ich habe eine interessante Anzeige gelesen: eine helle Zwei-Zimmer-Wohnung mit einem großen Balkon.|Maybe. I read an interesting ad: a bright two-room flat with a big balcony.
Sara|Klingt gut! Wie hoch ist die Miete?|Sounds good! How high is the rent?
Emre|750 Euro plus Nebenkosten. Für eine zentrale Lage ist das günstig.|750 euros plus extra costs. That's good value for a central location.
Sara|Ist sie möbliert?|Is it furnished?
Emre|Nein, aber es gibt eine neue Küche und einen schönen Holzboden.|No, but there's a new kitchen and a nice wooden floor.
Sara|Und wann ist die Besichtigung?|And when is the viewing?
Emre|Morgen um fünf. Der Vermieter ist ein freundlicher Mann, glaube ich.|Tomorrow at five. The landlord is a friendly man, I think.""",
        "grammar": ("Adjective endings after ein, kein, mein", """After **ein, kein** and **mein, dein, sein...** the adjective shows the gender when the article can't:

- der word: **ein** groß**er** Balkon (nominative), **einen** groß**en** Balkon (accusative)
- das word: **ein** hell**es** Zimmer (nominative and accusative)
- die word: **eine** neu**e** Küche (nominative and accusative)
- dative, all genders: **-en**: mit **einem** groß**en** Balkon, in **einer** ruhig**en** Straße
- plural with keine / meine: **-en**: **meine** neu**en** Nachbarn

Tip: ein looks the same for der and das words, so the adjective adds **-er** (der) or **-es** (das) to make it clear.""",
                    "Das ist ein schöner Balkon.=That's a nice balcony.; Wir suchen eine günstige Wohnung.=We're looking for a flat that's good value.; Sie hat ein helles Zimmer.=She has a bright room.; Ich wohne in einem kleinen Haus.=I live in a small house."),
        "exercises": """Die Wohnung hat einen ___ Balkon.|großen|großer|große
Das ist ein ___ Zimmer.|helles|heller|helle
Wir suchen eine ___ Wohnung.|ruhige|ruhigen|ruhiger
Er ist ein ___ Vermieter.|netter|nettes|netten
Ich wohne in einem ___ Haus.|alten|altes|alter
Mein ___ Nachbar heißt Paul.|neuer|neue|neuen
Wir haben keine ___ Küche.|moderne|modernen|moderner""",
    },
    {
        "id": "vergleich", "title": "Stadt oder Land?", "subtitle": "Comparing: größer als, so groß wie, am größten",
        "level": "A2", "unit": "In town",
        "words": """die Natur=nature; die Luft=air; der Lärm=noise; die Kultur=culture; das Angebot=offer, range;
der Vorteil=advantage; der Nachteil=disadvantage; die Großstadt=big city; auf dem Land=in the country;
sauber=clean; schmutzig=dirty; spannend=exciting; hoch=high, tall; als=than; wie=as (so ... wie);
lieber=rather (prefer); besser=better; mehr=more""",
        "dialogue": """Julia|Wohnst du lieber in der Stadt oder auf dem Land?|Do you prefer living in town or in the country?
Max|In der Stadt! Das kulturelle Angebot ist viel größer als auf dem Land.|In town! There's a much bigger range of culture than in the country.
Julia|Aber auf dem Land ist die Luft sauberer und es gibt weniger Lärm.|But in the country the air is cleaner and there's less noise.
Max|Das stimmt. Aber in der Stadt ist alles näher: die Arbeit, die Kinos, die Freunde.|That's true. But in town everything is closer: work, cinemas, friends.
Julia|Für mich ist die Natur am wichtigsten. Ich ziehe bald in ein kleines Dorf.|For me nature is the most important thing. I'm moving to a small village soon.
Max|Ein Dorf ist nicht so spannend wie Berlin! Aber ich besuche dich gern.|A village isn't as exciting as Berlin! But I'll be happy to visit you.""",
        "grammar": ("Comparing: -er als, so ... wie, am -sten", """To compare, add **-er** to the adjective and use **als** (than): Die Stadt ist laut**er** **als** das Dorf.

The same: **so** + adjective + **wie**: Ein Dorf ist nicht **so** spannend **wie** Berlin.

The most: **am** + adjective + **-sten**: Die Natur ist mir **am** wichtig**sten**.

Many short adjectives get an umlaut: groß → gr**ö**ßer → am gr**ö**ßten, alt → **ä**lter → am **ä**ltesten, warm → w**ä**rmer, jung → j**ü**nger, kalt → k**ä**lter.

Irregular: gut → **besser** → am **besten**; viel → **mehr** → am **meisten**; gern → **lieber** → am **liebsten**; hoch → **höher** → am **höchsten**.

After -t, -d, -s, -ß and -z, add -e- before -sten: am ält**e**sten, am heiß**e**sten. Exception: am **größten**.""",
                    "Mein Bruder ist älter als ich.=My brother is older than me.; Berlin ist größer als Hamburg.=Berlin is bigger than Hamburg.; Ich trinke lieber Tee als Kaffee.=I prefer tea to coffee.; Im Juli ist es am heißesten.=It's hottest in July."),
        "exercises": """Die Stadt ist lauter ___ das Dorf.|als|wie|so
Tim ist so groß ___ sein Vater.|wie|als|am
Ich trinke ___ Tee als Kaffee.|lieber|gerner|mehr gern
Dieses Restaurant ist am ___.|besten|gutesten|besser
Berlin ist ___ als München.|größer|großer|größter
Wer ist am ___? (old)|ältesten|älteren|altesten
Mein Haus ist nicht so ___ wie dein Haus.|groß|größer|am größten""",
    },
    {
        "id": "morgens", "title": "Jeden Morgen dasselbe", "subtitle": "Daily routine: reflexive verbs",
        "level": "A2", "unit": "Daily life",
        "words": """sich waschen=to wash (yourself); sich duschen=to have a shower; sich anziehen=to get dressed;
sich kämmen=to comb your hair; sich rasieren=to shave; sich schminken=to put on make-up; sich beeilen=to hurry;
sich freuen=to be happy, to be glad; sich ausruhen=to rest; sich fühlen=to feel; der Alltag=everyday life;
der Wecker=alarm clock; die Zahnbürste=toothbrush; das Handtuch=towel; die Seife=soap; müde=tired""",
        "dialogue": """Paul|Warum bist du noch nicht fertig? Wir müssen los!|Why aren't you ready yet? We have to go!
Lisa|Entschuldigung! Mein Wecker hat nicht geklingelt. Ich muss mich noch anziehen.|Sorry! My alarm didn't go off. I still have to get dressed.
Paul|Beeil dich bitte! Hast du dich schon geduscht?|Please hurry! Have you had a shower yet?
Lisa|Ja, aber ich muss mich noch kämmen und schminken.|Yes, but I still have to comb my hair and put on my make-up.
Paul|Du brauchst immer eine Stunde im Bad!|You always need an hour in the bathroom!
Lisa|Und du rasierst dich nie! So, fertig. Ich freue mich auf den Ausflug!|And you never shave! Right, ready. I'm looking forward to the trip!""",
        "grammar": ("Reflexive verbs: sich waschen", """Reflexive verbs have a pronoun that refers back to the subject, like "myself" in English. Many everyday German verbs are reflexive:

- ich wasche **mich**
- du wäschst **dich**
- er / sie / es wäscht **sich**
- wir waschen **uns**
- ihr wascht **euch**
- sie / Sie waschen **sich**

Only er / sie / es and sie / Sie use **sich**; the others use the normal accusative pronouns.

The pronoun comes right after the verb: Ich **ziehe mich** an. In questions and after a time word, it comes after the subject: Wann **duschst du dich**? Morgens **rasiert er sich**.

In the Perfekt, reflexive verbs use **haben**: Ich **habe mich** beeilt.""",
                    "Ich dusche mich jeden Morgen.=I have a shower every morning.; Beeil dich!=Hurry up!; Wir freuen uns.=We're happy.; Er hat sich schnell angezogen.=He got dressed quickly."),
        "exercises": """Ich wasche ___ jeden Abend.|mich|mir|sich
Du musst ___ beeilen!|dich|dir|sich
Er rasiert ___ jeden Morgen.|sich|ihn|ihm
Wir freuen ___ auf das Wochenende.|uns|euch|sich
Zieht ihr ___ schnell an?|euch|uns|sich
Ich habe ___ heute nicht geschminkt.|mich|sich|mir
Wie fühlen Sie ___?|sich|Sie|Ihnen""",
    },
    {
        "id": "interessen", "title": "Sport und Interessen", "subtitle": "Verbs with prepositions: warten auf, sich interessieren für",
        "level": "A2", "unit": "Free time",
        "words": """der Verein=club; die Mannschaft=team; das Spiel=game, match; das Training=training; das Tor=goal; gate;
die Meisterschaft=championship; gewinnen=to win; trainieren=to train; sich interessieren für=to be interested in;
warten auf=to wait for; sich freuen auf=to look forward to; sich ärgern über=to be annoyed about;
denken an=to think of; träumen von=to dream of; teilnehmen an=to take part in""",
        "dialogue": """Leon|Interessierst du dich für Fußball?|Are you interested in soccer?
Aylin|Ja, sehr! Ich bin sogar in einem Verein. Wir trainieren zweimal pro Woche.|Yes, very! I'm even in a club. We train twice a week.
Leon|Toll! Spielt ihr auch in einer Meisterschaft?|Great! Do you play in a championship too?
Aylin|Ja. Am Samstag haben wir ein wichtiges Spiel. Ich freue mich schon darauf!|Yes. On Saturday we have an important match. I'm already looking forward to it!
Leon|Ich ärgere mich immer über meine Mannschaft. Sie verliert fast jedes Spiel.|I'm always annoyed about my team. They lose almost every match.
Aylin|Komm doch am Samstag zu unserem Spiel! Ich warte am Eingang auf dich.|Come to our match on Saturday! I'll wait for you at the entrance.
Leon|Gern! Ich drücke dir die Daumen.|I'd love to! I'll keep my fingers crossed for you.""",
        "grammar": ("Verbs with a fixed preposition", """Many German verbs go with a **fixed preposition**, often not the one you'd expect from English. Learn them as one piece, together with the case:

- **warten auf** + accusative: Ich warte **auf den** Bus.
- **sich freuen auf** + accusative (look forward to): Ich freue mich **auf das** Wochenende.
- **sich interessieren für** + accusative: Er interessiert sich **für** Musik.
- **sich ärgern über** + accusative: Sie ärgert sich **über den** Lärm.
- **denken an** + accusative: Ich denke **an dich**.
- **träumen von** + dative: Er träumt **von einem** Haus am Meer.
- **teilnehmen an** + dative: Wir nehmen **an einem** Kurs teil.

For things, use **da-** + preposition: Ich freue mich **darauf**. Questions use **wo-**: **Worauf** wartest du? **Wofür** interessierst du dich? Before a vowel, add -r-: d**ar**auf, w**or**an.""",
                    "Wir warten auf den Zug.=We're waiting for the train.; Ich interessiere mich für Politik.=I'm interested in politics.; Sie freut sich auf den Urlaub.=She's looking forward to the holiday.; Woran denkst du?=What are you thinking about?"),
        "exercises": """Ich warte ___ den Bus.|auf|für|an
Interessierst du dich ___ Sport?|für|auf|über
Er ärgert sich ___ das Wetter.|über|auf|von
Ich denke oft ___ meine Familie.|an|auf|für
Sie träumt ___ einem großen Haus.|von|auf|an
Nimmst du ___ dem Kurs teil?|an|auf|bei
___ wartest du? – Auf den Bus.|Worauf|Wofür|Woran""",
    },
    {
        "id": "umwelt", "title": "Umwelt und Natur", "subtitle": "Giving reasons: denn, deshalb, trotzdem",
        "level": "A2", "unit": "Nature",
        "words": """die Umwelt=environment; der Müll=rubbish, trash; die Flasche=bottle; das Plastik=plastic; die Energie=energy;
der Strom=electricity; das Klima=climate; der Wald=forest; der Fluss=river; das Tier=animal; die Pflanze=plant;
schützen=to protect; sparen=to save; trennen=to separate; wegwerfen=to throw away; denn=because;
deshalb=that's why, so; trotzdem=still, all the same""",
        "dialogue": """Lena|Warum trennst du den Müll so genau?|Why do you separate the rubbish so carefully?
Jonas|Ich will die Umwelt schützen, denn Plastik ist sehr gefährlich für die Tiere im Meer.|I want to protect the environment, because plastic is very dangerous for the animals in the sea.
Lena|Stimmt. Ich kaufe deshalb keine Flaschen aus Plastik mehr.|True. That's why I don't buy plastic bottles any more.
Jonas|Und ich fahre mit dem Fahrrad, denn so spare ich Energie und Geld.|And I cycle, because that way I save energy and money.
Lena|Ich habe kein Auto. Trotzdem fliege ich oft in den Urlaub. Das ist nicht so gut für das Klima.|I don't have a car. All the same, I often fly on holiday. That's not so good for the climate.
Jonas|Vielleicht fährst du nächstes Mal mit dem Zug?|Maybe you'll take the train next time?""",
        "grammar": ("denn, deshalb, trotzdem", """There are two kinds of linking words for reasons and results.

**denn** (because) does **not** change the word order. It stands between the two sentences and the verb stays second: Ich fahre Rad, **denn** ich **spare** so Geld. The same goes for **und, aber, oder**.

**deshalb** (that's why, so) and **trotzdem** (still, all the same) are part of the second sentence. When they come first, the verb follows **right after** them and the subject moves behind the verb:

- Plastik ist gefährlich. **Deshalb kaufe ich** keine Plastikflaschen.
- Es regnet. **Trotzdem gehe ich** spazieren.

They can also come after the verb: Ich kaufe **deshalb** keine Plastikflaschen.""",
                    "Ich bleibe zu Hause, denn ich bin krank.=I'm staying at home because I'm ill.; Ich bin krank. Deshalb bleibe ich zu Hause.=I'm ill. That's why I'm staying at home.; Es ist kalt. Trotzdem schwimmen wir im See.=It's cold. We're swimming in the lake all the same.; Wir trennen den Müll, denn das ist gut für die Umwelt.=We separate the rubbish because that's good for the environment."),
        "exercises": """Ich fahre mit dem Rad, ___ ich will Geld sparen.|denn|deshalb|trotzdem
Ich habe wenig Geld. Deshalb ___ nicht in Urlaub.|fahre ich|ich fahre|fahren ich
Es regnet. ___ gehen wir spazieren.|Trotzdem|Denn|Deshalb
Ich bin müde, ___ ich habe schlecht geschlafen.|denn|deshalb|trotzdem
Plastik ist schlecht für die Umwelt. ___ kaufe ich Glasflaschen.|Deshalb|Denn|Trotzdem
Er ist krank. Trotzdem ___ zur Arbeit.|geht er|er geht|gehen er
Wir sparen Energie, denn ___ teuer.|Strom ist|ist Strom|Strom sind""",
    },
    {
        "id": "gesundheit", "title": "Gesund leben", "subtitle": "Health and habits: giving reasons with weil",
        "level": "A2", "unit": "Health",
        "words": """die Gesundheit=health; die Ernährung=diet, food; das Gemüse=vegetables; das Obst=fruit; der Zucker=sugar;
die Bewegung=exercise, movement; das Gewicht=weight; der Stress=stress; rauchen=to smoke;
abnehmen=to lose weight; zunehmen=to put on weight; sich bewegen=to move, to get exercise; joggen=to jog;
fit=fit; ungesund=unhealthy; regelmäßig=regular, regularly; weil=because""",
        "dialogue": """Ärztin|Herr Wagner, warum sind Sie heute hier?|Mr. Wagner, why are you here today?
Herr Wagner|Ich bin oft müde, weil ich so viel Stress bei der Arbeit habe.|I'm often tired because I have so much stress at work.
Ärztin|Bewegen Sie sich regelmäßig?|Do you get regular exercise?
Herr Wagner|Nicht genug. Ich fahre mit dem Auto zur Arbeit, weil es schneller geht.|Not enough. I drive to work because it's quicker.
Ärztin|Und Ihre Ernährung? Essen Sie viel Obst und Gemüse?|And your diet? Do you eat a lot of fruit and vegetables?
Herr Wagner|Leider nicht. Im Büro esse ich oft Süßigkeiten, weil ich keine Zeit für das Mittagessen habe.|Unfortunately not. At the office I often eat sweets because I don't have time for lunch.
Ärztin|Dann gehen Sie doch in der Mittagspause spazieren. Das ist gut gegen Stress.|Then why not go for a walk in your lunch break? That's good for stress.""",
        "grammar": ("weil: the verb goes to the end", """**weil** (because) starts a **subordinate clause**. In a subordinate clause the conjugated verb goes to the **very end**:

- Ich bin müde. Ich **habe** viel Stress. → Ich bin müde, **weil** ich viel Stress **habe**.
- With a modal verb, the modal comes last: ..., weil ich früh aufstehen **muss**.
- In the Perfekt, haben or sein comes last: ..., weil ich schlecht geschlafen **habe**.
- Separable verbs join up again: ..., weil ich jeden Tag um sechs Uhr **aufstehe**.

Always put a **comma** before weil. Ask with **Warum?** and answer with **Weil ...**

Compare **denn**, which keeps the normal word order: ..., denn ich habe viel Stress.""",
                    "Ich jogge, weil ich fit bleiben will.=I jog because I want to stay fit.; Er raucht nicht mehr, weil es ungesund ist.=He doesn't smoke any more because it's unhealthy.; Sie isst kein Fleisch, weil sie Tiere liebt.=She doesn't eat meat because she loves animals.; Warum bist du nicht gekommen? – Weil ich krank war.=Why didn't you come? – Because I was ill."),
        "exercises": """Ich esse viel Obst, weil es gesund ___.|ist|sein|bin
Er geht zu Fuß, weil er abnehmen ___.|will|willst|wollen
Ich bin müde, weil ___.|ich schlecht geschlafen habe|ich habe schlecht geschlafen|habe ich schlecht geschlafen
Sie macht Sport, ___ sie fit bleiben will.|weil|denn|deshalb
Ich trinke abends keinen Kaffee, weil ich sonst nicht ___ kann.|schlafen|schlafe|schläft
Er kommt später, weil ___.|er im Stau steht|er steht im Stau|steht er im Stau
Ich gehe früh ins Bett, weil ich morgen früh ___.|aufstehen muss|muss aufstehen|aufstehe muss""",
    },
    {
        "id": "arbeit", "title": "Im Büro", "subtitle": "Work and colleagues: dass clauses",
        "level": "A2", "unit": "Work",
        "words": """der Kollege=colleague (male); die Kollegin=colleague (female); der Chef=boss (male); die Chefin=boss (female);
die Besprechung=meeting; der Vertrag=contract; das Gehalt=salary; die Bewerbung=job application;
die Stelle=job, position; die Überstunde=hour of overtime; kündigen=to quit, to hand in your notice;
sich bewerben=to apply (for a job); glauben=to believe, to think; hoffen=to hope; wissen=to know (a fact);
dass=that""",
        "dialogue": """Nina|Hast du schon gehört, dass Herr Schulz kündigt?|Have you heard that Mr. Schulz is quitting?
Ali|Nein! Ich wusste nicht, dass er unzufrieden ist.|No! I didn't know he was unhappy.
Nina|Er sagt, dass er zu viele Überstunden macht. Und das Gehalt ist auch nicht so gut.|He says he works too much overtime. And the salary isn't that good either.
Ali|Ich glaube, dass er recht hat. Hat er schon eine neue Stelle?|I think he's right. Does he already have a new job?
Nina|Ja, er hat sich bei einer Firma in Hamburg beworben und den Vertrag schon unterschrieben.|Yes, he applied to a company in Hamburg and has already signed the contract.
Ali|Dann hoffe ich, dass die Chefin bald jemand Neues findet. Wir haben schon jetzt zu viel Arbeit!|Then I hope the boss finds someone new soon. We already have too much work!""",
        "grammar": ("dass: what you say, think and know", """**dass** (that) introduces what someone says, thinks, knows or hopes. Like weil, it sends the verb to the **end**:

- Er kündigt. → Ich weiß, **dass** er **kündigt**.
- Sie hat recht. → Ich glaube, **dass** sie recht **hat**.
- Er hat sich beworben. → Sie sagt, **dass** er sich beworben **hat**.

Typical verbs before dass: **sagen, glauben, denken, wissen, hoffen, finden, hören**, and **Es ist wichtig / schön, dass ...**

Put a comma before dass. In speech, dass is often left out; then the verb stays in second place: Ich glaube, er **hat** recht.

Spelling: **das** (the, that one) has one s; **dass** (that, linking two sentences) has two.""",
                    "Ich weiß, dass du viel arbeitest.=I know that you work a lot.; Sie hofft, dass sie die Stelle bekommt.=She hopes she gets the job.; Er sagt, dass die Besprechung um zehn Uhr ist.=He says the meeting is at ten.; Es ist wichtig, dass wir pünktlich sind.=It's important that we're on time."),
        "exercises": """Ich glaube, dass der Chef heute nicht ___.|kommt|kommen|kommst
Sie sagt, dass sie eine neue Stelle ___.|sucht|suchen|suchst
Ich hoffe, ___ du bald kommst.|dass|das|denn
Weißt du, dass Anna ___?|gekündigt hat|hat gekündigt|kündigt hat
Er findet, ___ das Gehalt zu niedrig ist.|dass|das|denn
Es ist wichtig, dass wir pünktlich ___.|sind|ist|seid
Ich habe gehört, dass sie sich in Berlin ___.|beworben hat|hat beworben|bewirbt hat""",
    },
    {
        "id": "reise", "title": "Reisepläne", "subtitle": "Travel plans and conditions: wenn",
        "level": "A2", "unit": "Travel",
        "words": """das Flugzeug=plane; der Flughafen=airport; der Flug=flight; das Zelt=tent; der Campingplatz=campsite;
die Unterkunft=accommodation; das Doppelzimmer=double room; das Einzelzimmer=single room;
der Reisepass=passport; der Ausweis=identity card; das Ausland=abroad; buchen=to book; reservieren=to reserve;
übernachten=to stay the night; fliegen=to fly; wenn=if, when""",
        "dialogue": """Felix|Wohin fahren wir im Sommer?|Where are we going in the summer?
Clara|Wenn wir genug Geld haben, fliegen wir nach Portugal.|If we have enough money, we'll fly to Portugal.
Felix|Und wenn die Flüge zu teuer sind?|And if the flights are too expensive?
Clara|Dann fahren wir mit dem Zug an die Ostsee und übernachten auf einem Campingplatz.|Then we'll take the train to the Baltic Sea and stay at a campsite.
Felix|Im Zelt? Nur wenn es nicht regnet!|In a tent? Only if it doesn't rain!
Clara|Okay, dann buchen wir eine Unterkunft. Ich schaue heute Abend im Internet, wenn ich Zeit habe.|Okay, then we'll book somewhere to stay. I'll look online this evening when I have time.
Felix|Super. Und vergiss nicht: Für Portugal brauchst du deinen Reisepass oder deinen Ausweis!|Great. And don't forget: for Portugal you need your passport or your identity card!""",
        "grammar": ("wenn: if and when", """**wenn** means **if** (a condition) or **when / whenever** (in the present or future). It starts a subordinate clause, so the verb goes to the **end**: **Wenn** das Wetter schön **ist**, gehen wir an den Strand.

If the wenn clause comes **first**, the main clause starts with its **verb**: **Wenn** ich Zeit habe, **buche** ich das Hotel. (verb, comma, verb)

If the main clause comes first, its word order is normal: Ich buche das Hotel, **wenn** ich Zeit **habe**.

You can start the main clause with **dann**: Wenn es regnet, **dann bleiben** wir zu Hause.""",
                    "Wenn ich Urlaub habe, fahre ich ans Meer.=When I'm on holiday, I go to the seaside.; Wir übernachten im Zelt, wenn es warm ist.=We sleep in the tent if it's warm.; Wenn der Flug billig ist, buchen wir ihn sofort.=If the flight is cheap, we'll book it right away.; Was machst du, wenn es regnet?=What do you do if it rains?"),
        "exercises": """Wenn ich Zeit habe, ___ ich dich.|besuche|ich besuche|besuchen
Wir gehen schwimmen, wenn das Wetter schön ___.|ist|bist|sein
Wenn der Flug zu teuer ist, ___ wir mit dem Zug.|fahren|wir fahren|fährt
Ich buche das Hotel, wenn ___.|ich Geld habe|ich habe Geld|habe ich Geld
___ es regnet, bleiben wir im Hotel.|Wenn|Dann|Denn
Was machst du, wenn du keinen Reisepass ___?|hast|habe|haben
Wenn wir in Wien sind, ___ wir bei Freunden.|übernachten|übernachtet|wir übernachten""",
    },
    {
        "id": "medien", "title": "Medien im Alltag", "subtitle": "Phones, internet and news: ob and indirect questions",
        "level": "A2", "unit": "Media",
        "words": """die Nachricht=message; news item; die Nachrichten=the news; die Zeitung=newspaper; die Zeitschrift=magazine;
das Fernsehen=television; die Sendung=programme, show; das Internet=internet; der Computer=computer;
das Passwort=password; die E-Mail=email; die App=app; herunterladen=to download; speichern=to save;
schicken=to send; fernsehen=to watch TV; funktionieren=to work, to function; ob=whether, if""",
        "dialogue": """Opa|Kannst du mir helfen? Ich weiß nicht, wie diese App funktioniert.|Can you help me? I don't know how this app works.
Emma|Klar, Opa. Was möchtest du machen?|Sure, Grandpa. What do you want to do?
Opa|Ich möchte wissen, ob ich hier die Nachrichten lesen kann. Ich lese nämlich keine Zeitung mehr.|I'd like to know if I can read the news here. You see, I don't read a newspaper any more.
Emma|Ja, das geht. Aber zuerst musst du die App herunterladen. Weißt du, wo dein Passwort ist?|Yes, you can. But first you have to download the app. Do you know where your password is?
Opa|Ich habe es auf einen Zettel geschrieben. Aber ich weiß nicht mehr, wo der Zettel ist!|I wrote it on a piece of paper. But I don't know where the piece of paper is any more!
Emma|Kein Problem. Ich frage Mama, ob sie es weiß.|No problem. I'll ask Mum if she knows it.""",
        "grammar": ("Indirect questions: ob, wo, wann, wie", """A question inside another sentence is an **indirect question**. It's a subordinate clause, so the verb goes to the **end**.

- Yes/no questions use **ob** (whether, if): Kommt er? → Ich weiß nicht, **ob** er **kommt**.
- W-questions keep their question word: Wo ist das Passwort? → Weißt du, **wo** das Passwort **ist**?

Typical starts: **Ich weiß nicht, ...** / **Weißt du, ...?** / **Ich frage, ...** / **Können Sie mir sagen, ...?** (a polite way to ask).

Careful: for "if" meaning a condition, use **wenn**; for "if" meaning "whether", use **ob**: Ich frage, **ob** du Zeit hast.""",
                    "Ich weiß nicht, ob die App kostenlos ist.=I don't know if the app is free.; Können Sie mir sagen, wann die Sendung beginnt?=Can you tell me when the programme starts?; Weißt du, wie das funktioniert?=Do you know how that works?; Sie fragt, ob wir heute Abend fernsehen.=She's asking whether we're watching TV this evening."),
        "exercises": """Ich frage ihn, ___ er heute kommt oder nicht.|ob|wenn|dass
Weißt du, wo ___?|mein Handy ist|ist mein Handy|mein Handy sind
Können Sie mir sagen, wann der Film ___?|beginnt|beginnen|beginnst
Sie fragt, ___ das Internet funktioniert.|ob|wenn|was
Ich weiß nicht, wie ich die App ___.|herunterlade|lade herunter|herunterladen
Hast du gelesen, ___ heute in der Zeitung steht?|was|ob|wo
Er möchte wissen, ob du morgen Zeit ___.|hast|hat|haben""",
    },
    {
        "id": "amt", "title": "Auf dem Amt", "subtitle": "Offices and services: polite requests with hätte, könnte, würde",
        "level": "A2", "unit": "Services",
        "words": """das Amt=public office; das Formular=form; die Anmeldung=registration; die Unterschrift=signature;
das Konto=bank account; der Antrag=application (form); die Gebühr=fee; die Wartenummer=queue number;
die Öffnungszeiten=opening hours; ausfüllen=to fill in; unterschreiben=to sign; beantragen=to apply for;
erklären=to explain; wiederholen=to repeat; dringend=urgent; höflich=polite""",
        "dialogue": """Herr Rossi|Guten Morgen. Ich hätte gern einen Termin für die Anmeldung.|Good morning. I'd like an appointment to register.
Beamtin|Haben Sie eine Wartenummer?|Do you have a queue number?
Herr Rossi|Ja, hier. Könnten Sie mir bitte erklären, welche Papiere ich brauche?|Yes, here. Could you please explain which papers I need?
Beamtin|Ihren Ausweis und den Mietvertrag. Und Sie müssen dieses Formular ausfüllen.|Your identity card and the rental contract. And you have to fill in this form.
Herr Rossi|Würden Sie mir helfen? Ich verstehe nicht alle Wörter.|Would you help me? I don't understand all the words.
Beamtin|Natürlich. Hier schreiben Sie Ihre Adresse, und hier unten brauche ich Ihre Unterschrift.|Of course. You write your address here, and down here I need your signature.
Herr Rossi|Vielen Dank, Sie sind sehr freundlich!|Thank you very much, that's very kind of you!""",
        "grammar": ("Polite requests: hätte, könnte, würde", """To ask politely, German uses the **Konjunktiv II** (the "would" forms):

- **hätte gern** (would like to have): Ich **hätte gern** einen Termin.
- **könnte** (could): **Könnten** Sie mir helfen?
- **würde** + infinitive (would): **Würden** Sie das bitte wiederholen?

The forms: ich hätte, du hättest, er/sie hätte, wir hätten, Sie hätten. ich könnte, du könntest, er/sie könnte, wir könnten, Sie könnten. ich würde, du würdest, er/sie würde, wir würden, Sie würden.

As with modal verbs, the infinitive goes to the end: **Könnten** Sie mir das Formular **erklären**?

With **bitte**, a request sounds very polite: Würden Sie bitte hier unterschreiben?""",
                    "Ich hätte gern ein Formular.=I'd like a form.; Könnten Sie das bitte erklären?=Could you explain that, please?; Würden Sie bitte langsamer sprechen?=Would you speak more slowly, please?; Könnte ich ein Konto eröffnen?=Could I open an account?"),
        "exercises": """Ich ___ gern einen Termin.|hätte|würde|könnte
___ Sie mir bitte helfen?|Könnten|Hätten|Würde
___ Sie bitte hier unterschreiben?|Würden|Würde|Hätten
Könnten Sie das bitte ___?|wiederholen|wiederholt|wiederhole
Wir ___ gern ein Doppelzimmer.|hätten|hätte|hättet
Du ___ mir das Formular erklären.|könntest|könnte|könntet
Ich muss das Formular ___.|ausfüllen|füllen aus|ausfülle""",
    },
    {
        "id": "lebenslauf", "title": "Mein Lebenslauf", "subtitle": "Your life story: vor, seit, nach, ab, von ... bis",
        "level": "A2", "unit": "Work",
        "words": """der Lebenslauf=CV, résumé; die Erfahrung=experience; das Praktikum=internship; der Abschluss=degree, qualification;
das Studium=university studies; die Sprache=language; der Kurs=course; geboren=born; aufwachsen=to grow up;
heiraten=to get married; beginnen=to begin, to start; beenden=to finish; vor=ago; before; ab=from (a time on);
bis=until""",
        "dialogue": """Frau Lang|Erzählen Sie uns bitte etwas über sich.|Please tell us something about yourself.
Herr Demir|Gern. Ich bin 1995 in Izmir geboren und dort aufgewachsen.|Of course. I was born in Izmir in 1995 and grew up there.
Frau Lang|Seit wann wohnen Sie in Deutschland?|How long have you lived in Germany?
Herr Demir|Seit fünf Jahren. Vor fünf Jahren habe ich mein Studium beendet und bin dann nach Stuttgart gezogen.|For five years. Five years ago I finished my studies and then moved to Stuttgart.
Frau Lang|Und was haben Sie nach dem Studium gemacht?|And what did you do after your studies?
Herr Demir|Zuerst habe ich ein Praktikum gemacht, von März bis August. Seitdem arbeite ich als Ingenieur bei einer Firma.|First I did an internship, from March to August. Since then I've been working as an engineer for a company.
Frau Lang|Und ab wann könnten Sie bei uns anfangen?|And from when could you start with us?
Herr Demir|Ab dem ersten Oktober.|From the first of October.""",
        "grammar": ("Time: vor, seit, nach, ab, von ... bis", """These prepositions answer **Wann?** (when?) and **Seit wann?** (since when?). When they come before a noun, they take the **dative**:

- **vor** (ago): **vor** zwei Jahren, **vor** einer Woche. The verb is in the past.
- **seit** (since, for): **seit** 2020, **seit** einem Monat. It started in the past and is still going on, so the verb is in the **present**!
- **nach** (after): **nach** dem Studium, **nach** der Arbeit
- **ab** (from ... on): **ab** Montag, **ab** dem ersten Mai
- **von ... bis** (from ... until): **von** März **bis** August, **von** neun **bis** fünf Uhr (bis on its own takes the accusative: **bis** nächsten Montag)
- **in** (in, from now): **in** zwei Wochen

Careful: English "for two years" is **seit** zwei Jahren when it is still true: Ich wohne **seit** zwei Jahren hier.

For years, German says just the number (Ich bin **1995** geboren) or **im Jahr** 1995, never "in 1995".""",
                    "Vor drei Jahren bin ich nach Berlin gezogen.=Three years ago I moved to Berlin.; Seit zwei Jahren lerne ich Deutsch.=I've been learning German for two years.; Nach der Schule habe ich ein Praktikum gemacht.=After school I did an internship.; Ab Montag habe ich Urlaub.=I'm on holiday from Monday."),
        "exercises": """___ zwei Jahren haben wir geheiratet.|Vor|Seit|Ab
Ich arbeite ___ drei Jahren bei dieser Firma.|seit|vor|ab
Ich habe zuerst studiert. ___ dem Studium habe ich ein Praktikum gemacht.|Nach|Seit|Ab
Der Kurs geht von Montag ___ Freitag.|bis|zu|nach
___ nächster Woche habe ich eine neue Stelle.|Ab|Vor|Seit
Ich bin 1998 in Ankara ___.|geboren|gebärt|geboret
Er ist in einem kleinen Dorf ___.|aufgewachsen|aufgewachst|gewachsen auf""",
    },
]

# Hand-written items for the A2 level test (same format as the exercises).
TEST = """Gestern ___ ich keine Zeit.|hatte|war|hat
Als Kind ___ ich nicht gut schwimmen.|konnte|kann|könnte
Wir sind letztes Jahr nach Spanien ___.|geflogen|gefliegt|fliegen
Das Fahrrad gehört ___ Bruder. (my)|meinem|meinen|mein
Ich wohne seit einem Jahr ___ meinen Eltern.|bei|mit|zu
Häng das Bild bitte an ___ Wand!|die|der|den
Das ist ein ___ Film.|guter|gutes|gute
Ich nehme die ___ Jacke.|blaue|blauen|blauer
Mein Bruder ist ___ als ich.|älter|alter|ältester
Ich interessiere mich ___ Kunst.|für|auf|an
Sie bleibt zu Hause, weil sie krank ___.|ist|bist|sind
Ich hoffe, dass es dir bald besser ___.|geht|gehst|gehen
Wenn ich Zeit habe, ___ ich ins Kino.|gehe|ich gehe|gehen
Ich frage den Verkäufer, ___ der Laden am Sonntag offen ist.|ob|dass|wenn
___ Sie mir bitte helfen?|Könnten|Hätten|Würde
Er wäscht ___ die Hände. (his own)|sich|ihm|ihn
Wir fahren durch ___ Wald.|den|dem|der
Ich bin müde. ___ gehe ich früh ins Bett.|Deshalb|Denn|Weil"""
