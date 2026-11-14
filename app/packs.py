"""The flashcard pack library: ready-made decks that work without AI or a textbook.

Word lists are hand-picked (with hand-written English); genders, plurals and verb forms come from the offline
dictionary. The two "most common nouns" packs come straight from the dictionary's frequency ranks.
Cards from a pack are tagged "pack:<id>" so the library can show what's added and remove a pack again.
"""
import functools
import json
import re

from . import db, dictionary

# ---------- hand-written lists ----------
# Topic nouns: "article Word = English"
TOPICS = {
    "family": ("Family and people", "A1", """
die Familie=family; die Mutter=mother; der Vater=father; das Kind=child; der Sohn=son; die Tochter=daughter;
der Bruder=brother; die Schwester=sister; die Großmutter=grandmother; der Großvater=grandfather; die Oma=grandma;
der Opa=grandpa; der Onkel=uncle; die Tante=aunt; der Cousin=cousin (male); die Cousine=cousin (female);
der Neffe=nephew; die Nichte=niece; der Mann=man; husband; die Frau=woman; wife; der Freund=friend; boyfriend;
die Freundin=friend; girlfriend; der Nachbar=neighbor; das Baby=baby; der Junge=boy; das Mädchen=girl;
der Ehemann=husband; die Ehefrau=wife; die Hochzeit=wedding; der Mensch=person, human being"""),
    "food": ("Food and drink", "A1", """
das Brot=bread; das Brötchen=bread roll; die Butter=butter; der Käse=cheese; die Wurst=sausage; das Ei=egg;
die Milch=milk; der Kaffee=coffee; der Tee=tea; das Wasser=water; der Saft=juice; das Bier=beer; der Wein=wine;
der Apfel=apple; die Banane=banana; die Kartoffel=potato; die Tomate=tomato; das Gemüse=vegetables;
das Obst=fruit; das Fleisch=meat; der Fisch=fish; das Hähnchen=chicken (food); der Reis=rice; die Nudel=noodle;
die Suppe=soup; der Salat=salad; lettuce; der Kuchen=cake; der Zucker=sugar; das Salz=salt;
das Frühstück=breakfast; das Mittagessen=lunch; das Abendessen=dinner; die Speisekarte=menu; die Rechnung=bill"""),
    "home": ("At home", "A1", """
die Wohnung=apartment; das Haus=house; das Zimmer=room; die Küche=kitchen; das Bad=bathroom;
das Schlafzimmer=bedroom; das Wohnzimmer=living room; der Flur=hallway; der Balkon=balcony; der Garten=garden;
die Tür=door; das Fenster=window; die Treppe=stairs; der Tisch=table; der Stuhl=chair; das Bett=bed;
der Schrank=cupboard; wardrobe; das Sofa=sofa; die Lampe=lamp; der Kühlschrank=fridge; der Herd=stove;
die Waschmaschine=washing machine; der Schlüssel=key; die Miete=rent; der Vermieter=landlord;
die Heizung=heating; der Boden=floor; ground; die Wand=wall; die Decke=ceiling; blanket"""),
    "town": ("Town and travel", "A1", """
die Stadt=city, town; das Dorf=village; die Straße=street; der Platz=square; seat; die Kreuzung=intersection;
die Ampel=traffic light; der Bahnhof=train station; der Zug=train; der Bus=bus; die Haltestelle=stop (bus, tram);
die U-Bahn=subway; die Straßenbahn=tram; das Auto=car; das Fahrrad=bicycle; das Flugzeug=airplane;
der Flughafen=airport; die Fahrkarte=ticket; das Gleis=platform, track; die Abfahrt=departure;
die Ankunft=arrival; das Hotel=hotel; der Koffer=suitcase; der Pass=passport; die Reise=trip, journey;
der Urlaub=vacation; die Bank=bank; bench; die Post=post office; mail; die Apotheke=pharmacy;
das Krankenhaus=hospital; der Supermarkt=supermarket; die Kirche=church; das Museum=museum"""),
    "body": ("Body and health", "A1", """
der Körper=body; der Kopf=head; das Gesicht=face; das Auge=eye; das Ohr=ear; die Nase=nose; der Mund=mouth;
der Zahn=tooth; das Haar=hair; der Hals=neck; throat; die Schulter=shoulder; der Arm=arm; die Hand=hand;
der Finger=finger; der Bauch=stomach, belly; der Rücken=back; das Bein=leg; das Knie=knee; der Fuß=foot;
das Herz=heart; der Arzt=doctor; die Ärztin=doctor (female); die Krankheit=illness; das Fieber=fever;
der Schmerz=pain; die Erkältung=cold (illness); der Husten=cough; das Medikament=medicine; die Tablette=pill;
der Termin=appointment"""),
    "work": ("Work and school", "A2", """
die Arbeit=work; der Beruf=profession; die Stelle=job, position; die Firma=company; das Büro=office;
der Kollege=colleague; die Kollegin=colleague (female); der Chef=boss; der Lohn=wage; das Gehalt=salary;
die Bewerbung=job application; das Vorstellungsgespräch=job interview; die Besprechung=meeting;
der Computer=computer; die Schule=school; die Universität=university; der Lehrer=teacher;
die Lehrerin=teacher (female); der Schüler=pupil; der Student=student; der Unterricht=lessons, class;
die Prüfung=exam; die Hausaufgabe=homework; das Buch=book; das Heft=exercise book; der Kuli=pen;
der Bleistift=pencil; die Note=grade; der Kurs=course"""),
    "time": ("Days, months and seasons", "A1", """
der Tag=day; die Woche=week; der Monat=month; das Jahr=year; die Stunde=hour; die Minute=minute;
der Morgen=morning; der Vormittag=late morning; der Mittag=noon; der Nachmittag=afternoon; der Abend=evening;
die Nacht=night; der Montag=Monday; der Dienstag=Tuesday; der Mittwoch=Wednesday; der Donnerstag=Thursday;
der Freitag=Friday; der Samstag=Saturday; der Sonntag=Sunday; das Wochenende=weekend; der Januar=January;
der Februar=February; der März=March; der April=April; der Mai=May; der Juni=June; der Juli=July;
der August=August; der September=September; der Oktober=October; der November=November;
der Dezember=December; der Frühling=spring; der Sommer=summer; der Herbst=fall, autumn; der Winter=winter;
der Feiertag=public holiday; der Geburtstag=birthday"""),
    "clothes": ("Clothes", "A1", """
die Kleidung=clothes; das Hemd=shirt; das T-Shirt=T-shirt; die Bluse=blouse; der Pullover=sweater;
die Jacke=jacket; der Mantel=coat; die Hose=pants, trousers; die Jeans=jeans; der Rock=skirt; das Kleid=dress;
der Anzug=suit; die Socke=sock; der Schuh=shoe; der Stiefel=boot; die Mütze=knit hat, cap; der Hut=hat;
der Schal=scarf; der Handschuh=glove; der Gürtel=belt; die Tasche=bag; pocket; die Brille=glasses;
der Schlafanzug=pajamas; die Größe=size; die Farbe=color"""),
    "nature": ("Nature and weather", "A2", """
das Wetter=weather; die Sonne=sun; der Regen=rain; der Schnee=snow; der Wind=wind; die Wolke=cloud;
das Gewitter=thunderstorm; der Himmel=sky; heaven; die Temperatur=temperature; der Baum=tree; die Blume=flower;
das Gras=grass; der Wald=forest; der Berg=mountain; der See=lake; das Meer=sea; der Fluss=river;
der Strand=beach; die Insel=island; das Tier=animal; der Hund=dog; die Katze=cat; der Vogel=bird;
das Pferd=horse; die Kuh=cow; die Natur=nature; die Luft=air; die Erde=earth; soil"""),
    "feelings": ("Feelings", "A2", """
die Liebe=love; die Freude=joy; das Glück=happiness; luck; die Angst=fear; die Wut=rage; der Ärger=anger; trouble;
die Trauer=grief; die Sorge=worry; die Hoffnung=hope; der Spaß=fun; die Langeweile=boredom;
das Gefühl=feeling; die Laune=mood; der Stress=stress; die Lust=desire (Lust haben: to feel like);
die Geduld=patience; die Überraschung=surprise; die Enttäuschung=disappointment; der Stolz=pride;
die Eifersucht=jealousy; das Vertrauen=trust"""),
}

# Verbs: "infinitive=English", the 150 or so a learner needs first, roughly most common first.
VERBS = """
sein=to be; haben=to have; werden=to become; können=can, to be able to; müssen=must, to have to; sagen=to say;
machen=to make, to do; geben=to give; kommen=to come; sollen=should, to be supposed to; wollen=to want;
gehen=to go; wissen=to know (a fact); sehen=to see; lassen=to let; to leave; stehen=to stand; finden=to find;
bleiben=to stay; liegen=to lie (be lying); heißen=to be called; denken=to think; nehmen=to take; tun=to do;
dürfen=may, to be allowed to; glauben=to believe; halten=to hold; to stop; nennen=to name, to call;
mögen=to like; zeigen=to show; führen=to lead; sprechen=to speak; bringen=to bring; leben=to live;
fahren=to drive, to go (by vehicle); meinen=to mean; to think; fragen=to ask; kennen=to know (be familiar with);
stellen=to put (upright); spielen=to play; arbeiten=to work; brauchen=to need; folgen=to follow;
lernen=to learn; verstehen=to understand; setzen=to put, to set; bekommen=to get, to receive;
beginnen=to begin; erzählen=to tell (a story); versuchen=to try; schreiben=to write; laufen=to run; to walk;
erklären=to explain; sitzen=to sit; ziehen=to pull; to move (house); scheinen=to shine; to seem;
fallen=to fall; gehören=to belong to; erhalten=to receive; treffen=to meet; to hit; suchen=to look for;
legen=to lay, to put (flat); tragen=to carry; to wear; schaffen=to manage (to do); lesen=to read;
verlieren=to lose; erkennen=to recognize; reden=to talk; aussehen=to look (like); erscheinen=to appear;
anfangen=to start; erwarten=to expect; wohnen=to live (reside); warten=to wait; helfen=to help;
gewinnen=to win; schließen=to close; fühlen=to feel; bieten=to offer; erinnern=to remind; studieren=to study;
fehlen=to be missing; bedeuten=to mean; essen=to eat; trinken=to drink; schlafen=to sleep; kaufen=to buy;
bezahlen=to pay; öffnen=to open; vergessen=to forget; verkaufen=to sell; besuchen=to visit;
hören=to hear; to listen; antworten=to answer; kochen=to cook; waschen=to wash; tanzen=to dance;
singen=to sing; schwimmen=to swim; fliegen=to fly; reisen=to travel; aufstehen=to get up; einkaufen=to shop;
anrufen=to call (on the phone); ankommen=to arrive; abfahren=to depart; mitnehmen=to take along;
einladen=to invite; umziehen=to move (house); fernsehen=to watch TV; vorbereiten=to prepare; benutzen=to use;
bestellen=to order; lieben=to love; hoffen=to hope; danken=to thank; feiern=to celebrate; kosten=to cost;
dauern=to last, to take (time); passieren=to happen; gefallen=to please (es gefällt mir: I like it);
schmecken=to taste; werfen=to throw; sterben=to die; rufen=to call, to shout; steigen=to climb;
springen=to jump; wachsen=to grow; brechen=to break; stehlen=to steal; empfehlen=to recommend;
verbieten=to forbid; leihen=to lend; to borrow; schneiden=to cut; streiten=to argue; schweigen=to be silent;
riechen=to smell; lügen=to lie (tell lies); fangen=to catch; hängen=to hang; schlagen=to hit;
rennen=to run; brennen=to burn; senden=to send; vergleichen=to compare; entscheiden=to decide;
bitten=to ask (for), to request; beweisen=to prove; sinken=to sink; treten=to step; to kick;
heben=to lift; frieren=to freeze, to be cold; gießen=to pour; to water; leiden=to suffer;
genießen=to enjoy; schieben=to push; fressen=to eat (animals); messen=to measure; geschehen=to happen"""

ADJECTIVES = """
gut=good; neu=new; alt=old; groß=big, tall; klein=small; lang=long; kurz=short; hoch=high; jung=young;
schön=beautiful, nice; wichtig=important; richtig=right, correct; falsch=wrong; schnell=fast; langsam=slow;
leicht=easy; light; schwer=difficult; heavy; einfach=simple; schwierig=difficult; billig=cheap;
teuer=expensive; warm=warm; kalt=cold; heiß=hot; nah=near; weit=far; früh=early; spät=late; voll=full;
leer=empty; laut=loud; leise=quiet (sound); hell=bright, light; dunkel=dark; stark=strong; schwach=weak;
reich=rich; arm=poor; glücklich=happy; traurig=sad; müde=tired; krank=sick; gesund=healthy; froh=glad;
böse=angry; evil; nett=nice, kind; freundlich=friendly; lustig=funny; langweilig=boring;
interessant=interesting; sauber=clean; schmutzig=dirty; ruhig=calm, quiet; gefährlich=dangerous; sicher=safe; sure;
möglich=possible; frei=free; offen=open; fertig=finished, ready; bereit=ready, willing; eng=narrow, tight;
breit=wide; dick=thick; fat; dünn=thin; süß=sweet; sauer=sour; annoyed; scharf=spicy; sharp; frisch=fresh;
nass=wet; trocken=dry; weich=soft; hart=hard; bekannt=well-known; berühmt=famous; fremd=foreign, strange;
gleich=same; verschieden=different; wahr=true; klug=clever; dumm=stupid; faul=lazy; fleißig=hard-working;
höflich=polite; ehrlich=honest; pünktlich=on time; ähnlich=similar; bequem=comfortable; praktisch=practical"""

# German front | English back | example
PHRASES = """
Guten Morgen!|Good morning!|
Guten Tag!|Hello! (formal, during the day)|
Guten Abend!|Good evening!|
Gute Nacht!|Good night!|
Tschüss!|Bye!|
Auf Wiedersehen!|Goodbye!|
Bis später!|See you later!|
Bis morgen!|See you tomorrow!|
Wie geht es Ihnen?|How are you? (formal)|
Wie geht's?|How's it going?|
Mir geht es gut, danke.|I'm fine, thanks.|
Und Ihnen?|And you? (formal)|
Wie heißen Sie?|What's your name? (formal)|
Ich heiße …|My name is …|
Woher kommen Sie?|Where are you from? (formal)|
Ich komme aus …|I'm from …|
Freut mich!|Nice to meet you!|
Bitte.|Please. / You're welcome.|
Danke schön!|Thank you very much!|
Gern geschehen.|You're welcome.|
Entschuldigung!|Excuse me! / Sorry!|
Es tut mir leid.|I'm sorry.|
Kein Problem.|No problem.|
Wie bitte?|Pardon? / Sorry, what?|
Ich verstehe das nicht.|I don't understand.|
Können Sie das bitte wiederholen?|Could you repeat that, please?|
Sprechen Sie bitte langsamer.|Please speak more slowly.|
Was bedeutet das?|What does that mean?|
Wie sagt man das auf Deutsch?|How do you say that in German?|
Wo ist die Toilette?|Where is the restroom?|
Wie viel kostet das?|How much does that cost?|
Ich hätte gern …|I'd like …|Ich hätte gern einen Kaffee.
Die Rechnung, bitte.|The check, please.|
Stimmt so.|Keep the change.|
Wie spät ist es?|What time is it?|
Ich weiß es nicht.|I don't know.|
Keine Ahnung.|No idea.|
Alles klar!|All right! / Got it!|
Viel Glück!|Good luck!|
Gute Besserung!|Get well soon!|
Herzlichen Glückwunsch!|Congratulations! / Happy birthday!|
Schönes Wochenende!|Have a nice weekend!|
Prost!|Cheers!|
Guten Appetit!|Enjoy your meal!|
Das ist mir egal.|I don't mind. / I don't care.|
Genau!|Exactly!|
Schade!|What a pity!|
Moment, bitte.|One moment, please.|
Kann ich Ihnen helfen?|Can I help you? (formal)|
Ich habe Hunger.|I'm hungry.|
Ich habe Durst.|I'm thirsty.|
Mir ist kalt.|I'm cold.|
Mir ist schlecht.|I feel sick.|
Das macht nichts.|That doesn't matter.|
Ich bin dran.|It's my turn.|"""

# verb | English | example (the verb takes a dative object)
DATIVE_VERBS = """
helfen|to help|Ich helfe meiner Mutter.
danken|to thank|Wir danken Ihnen für die Hilfe.
gefallen|to please (I like it)|Das Kleid gefällt mir.
gehören|to belong to|Das Buch gehört dem Lehrer.
antworten|to answer|Sie antwortet ihrem Freund nicht.
folgen|to follow|Der Hund folgt dem Kind.
gratulieren|to congratulate|Ich gratuliere dir zum Geburtstag.
schmecken|to taste (good)|Die Suppe schmeckt mir.
passen|to fit; to suit|Die Hose passt mir nicht.
fehlen|to be missing; to be missed|Du fehlst mir.
glauben|to believe (someone)|Ich glaube dir.
vertrauen|to trust|Er vertraut seiner Schwester.
begegnen|to run into, to meet|Ich bin ihm gestern begegnet.
zuhören|to listen to|Hör mir bitte zu!
widersprechen|to contradict|Er widerspricht seinem Chef.
gehorchen|to obey|Das Kind gehorcht den Eltern.
verzeihen|to forgive|Verzeih mir bitte!
schaden|to harm|Rauchen schadet der Gesundheit.
nützen|to be of use to|Das nützt mir nichts.
zustimmen|to agree with|Ich stimme dir zu.
leidtun|to be sorry|Es tut mir leid.
wehtun|to hurt|Mein Kopf tut mir weh.
gelingen|to succeed (for someone)|Der Kuchen ist mir gut gelungen.
raten|to advise|Ich rate dir, früh zu gehen.
ähneln|to resemble|Sie ähnelt ihrer Mutter.
zuschauen|to watch|Wir schauen den Kindern beim Spielen zu.
drohen|to threaten|Er droht seinem Nachbarn.
winken|to wave to|Sie winkt ihren Freunden."""

# verb … | English | preposition + case | example
VERB_PREPS = """
warten|to wait for|auf + Akkusativ|Ich warte auf den Bus.
denken|to think of|an + Akkusativ|Ich denke oft an dich.
sich freuen|to look forward to|auf + Akkusativ|Ich freue mich auf das Wochenende.
sich freuen|to be happy about|über + Akkusativ|Sie freut sich über das Geschenk.
sich interessieren|to be interested in|für + Akkusativ|Er interessiert sich für Musik.
Angst haben|to be afraid of|vor + Dativ|Das Kind hat Angst vor dem Hund.
sich erinnern|to remember|an + Akkusativ|Ich erinnere mich an den Urlaub.
sich kümmern|to take care of|um + Akkusativ|Sie kümmert sich um ihre Oma.
teilnehmen|to take part in|an + Dativ|Er nimmt an dem Kurs teil.
sprechen|to talk about|über + Akkusativ|Wir sprechen über das Wetter.
sprechen|to talk to|mit + Dativ|Ich spreche mit dem Arzt.
sich ärgern|to be annoyed about|über + Akkusativ|Er ärgert sich über den Stau.
sich bewerben|to apply for|um + Akkusativ|Sie bewirbt sich um die Stelle.
bitten|to ask for|um + Akkusativ|Ich bitte dich um Hilfe.
sich beschweren|to complain about|über + Akkusativ|Er beschwert sich über das Essen.
sich entschuldigen|to apologize for|für + Akkusativ|Ich entschuldige mich für die Verspätung.
sich entschuldigen|to apologize to|bei + Dativ|Ich entschuldige mich bei dir.
fragen|to ask about|nach + Dativ|Er fragt nach dem Weg.
sich gewöhnen|to get used to|an + Akkusativ|Ich gewöhne mich an das Wetter.
glauben|to believe in|an + Akkusativ|Sie glaubt an das Gute im Menschen.
träumen|to dream of|von + Dativ|Ich träume von einem Haus am Meer.
sich verlassen|to rely on|auf + Akkusativ|Du kannst dich auf mich verlassen.
sich verlieben|to fall in love with|in + Akkusativ|Er hat sich in sie verliebt.
sich vorbereiten|to prepare for|auf + Akkusativ|Ich bereite mich auf die Prüfung vor.
abhängen|to depend on|von + Dativ|Das hängt vom Wetter ab.
achten|to pay attention to|auf + Akkusativ|Achte auf den Verkehr!
aufhören|to stop (doing)|mit + Dativ|Er hört mit dem Rauchen auf.
sich beschäftigen|to deal with, to be busy with|mit + Dativ|Ich beschäftige mich mit Geschichte.
bestehen|to consist of|aus + Dativ|Das Team besteht aus fünf Leuten.
danken|to thank for|für + Akkusativ|Danke für die Blumen!
sich erkundigen|to inquire about|nach + Dativ|Ich erkundige mich nach dem Preis.
gehören|to be part of|zu + Dativ|Er gehört zur Familie.
helfen|to help with|bei + Dativ|Ich helfe dir bei den Hausaufgaben.
lachen|to laugh about|über + Akkusativ|Wir lachen über den Witz.
sich unterhalten|to chat with|mit + Dativ|Ich unterhalte mich mit meiner Nachbarin.
sich treffen|to meet up with|mit + Dativ|Ich treffe mich mit Freunden.
sich sorgen|to worry about|um + Akkusativ|Sie sorgt sich um ihren Sohn.
suchen|to search for|nach + Dativ|Ich suche nach meinem Schlüssel.
sich konzentrieren|to concentrate on|auf + Akkusativ|Konzentrier dich auf die Aufgabe!
es geht|it's about|um + Akkusativ|Es geht um die Zukunft.
sich verabschieden|to say goodbye to|von + Dativ|Er verabschiedet sich von allen.
zweifeln|to doubt|an + Dativ|Ich zweifle an seiner Geschichte.
reagieren|to react to|auf + Akkusativ|Sie reagiert nicht auf meine Nachricht.
einladen|to invite to|zu + Dativ|Ich lade dich zum Essen ein."""

# preposition | case and English | example
PREPOSITIONS = """
durch|Akkusativ: through|Wir gehen durch den Park.
für|Akkusativ: for|Das Geschenk ist für dich.
gegen|Akkusativ: against|Er ist gegen den Plan.
ohne|Akkusativ: without|Ich trinke Kaffee ohne Zucker.
um|Akkusativ: around; at (time)|Wir sitzen um den Tisch. Der Kurs beginnt um acht.
bis|Akkusativ: until; as far as|Ich bleibe bis Montag.
aus|Dativ: out of; from (origin)|Sie kommt aus der Schweiz.
bei|Dativ: at (someone's place); near; with|Ich wohne bei meinen Eltern.
mit|Dativ: with; by (transport)|Ich fahre mit dem Zug.
nach|Dativ: after; to (cities, countries)|Nach dem Essen fahren wir nach Berlin.
seit|Dativ: since; for (time until now)|Ich lerne seit einem Jahr Deutsch.
von|Dativ: from; of; by|Das ist ein Brief von meiner Oma.
zu|Dativ: to (people, places)|Ich gehe zum Arzt.
gegenüber|Dativ: opposite|Die Bank ist gegenüber dem Bahnhof.
an|Wechsel: Akk. (where to?) / Dat. (where?): at, on (vertical)|Ich hänge das Bild an die Wand. Das Bild hängt an der Wand.
auf|Wechsel: Akk. (where to?) / Dat. (where?): on (top of)|Ich lege das Buch auf den Tisch. Das Buch liegt auf dem Tisch.
hinter|Wechsel: Akk. / Dat.: behind|Der Garten liegt hinter dem Haus.
in|Wechsel: Akk. (where to?) / Dat. (where?): in, into|Ich gehe in die Küche. Ich bin in der Küche.
neben|Wechsel: Akk. / Dat.: next to|Stell den Stuhl neben das Sofa. Er steht neben dem Sofa.
über|Wechsel: Akk. / Dat.: over, above|Die Lampe hängt über dem Tisch.
unter|Wechsel: Akk. / Dat.: under|Die Katze liegt unter dem Bett.
vor|Wechsel: Akk. / Dat.: in front of; before; ago|Wir treffen uns vor dem Kino. Vor einem Jahr ...
zwischen|Wechsel: Akk. / Dat.: between|Das Café liegt zwischen der Post und der Bank.
wegen|Genitiv: because of|Wegen des Regens bleiben wir zu Hause.
trotz|Genitiv: despite|Trotz des Wetters gehen wir spazieren.
während|Genitiv: during|Während des Essens spricht er nicht.
statt|Genitiv: instead of|Statt eines Autos kauft sie ein Fahrrad.
innerhalb|Genitiv: within|Innerhalb einer Woche ist es fertig."""

# German | what it really means | the trap
FALSE_FRIENDS = """
bekommen|to get, to receive|not "to become" (werden)
das Gift|poison|not "gift" (das Geschenk)
das Handy|cell phone|
aktuell|current, up to date|not "actual" (tatsächlich)
eventuell|possibly, maybe|not "eventually" (schließlich)
sensibel|sensitive|not "sensible" (vernünftig)
der Chef|boss|not "chef" (der Koch)
der Rat|advice|not "rat" (die Ratte)
also|so, therefore|not "also" (auch)
bald|soon|not "bald" (glatzköpfig)
der Brand|fire|not "brand" (die Marke)
fast|almost|not "fast" (schnell)
das Kind|child|not "kind" (nett)
der Mist|manure; rubbish, nonsense|not "mist" (der Nebel)
die Rente|pension|not "rent" (die Miete)
die Art|kind, type; way|not "art" (die Kunst)
spenden|to donate|not "to spend" (ausgeben)
wer|who|not "where" (wo)
er will|he wants|not "he will" (er wird)
die Billion|trillion|not "billion" (die Milliarde)
die Kaution|deposit|not "caution" (die Vorsicht)
die Dose|can, tin|not "dose" (die Dosis)
sympathisch|likeable, nice|not "sympathetic" (mitfühlend)
die Fabrik|factory|not "fabric" (der Stoff)
das Gymnasium|academic high school|not "gym" (das Fitnessstudio)
die Hose|pants, trousers|not "hose" (der Schlauch)
die Mappe|folder|not "map" (die Landkarte)
der Smoking|tuxedo|
die Promotion|doctorate (PhD)|not "promotion" (die Beförderung)
die Konkurrenz|competition (rivals)|not "concurrence" (die Übereinstimmung)"""


def _items(text, sep=";"):
    """'a=b; c=d' → [(a, b), ...]; an English part may itself contain ';' if it doesn't contain '='."""
    out, cur = [], None
    for part in re.split(r";\s*\n?\s*|\n", text):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            de, en = part.split("=", 1)
            cur = [de.strip(), en.strip()]
            out.append(cur)
        elif cur:
            cur[1] += "; " + part
    return out


def _rows(text):
    return [[x.strip() for x in line.split("|")] for line in text.strip().splitlines() if line.strip()]


# ---------- the dictionary side ----------
def _entry(word, pos):
    for e in dictionary.lookup(word, 8):
        if e["word"] == word and e["pos"] == pos:
            return e
    return None


def _noun_card(de, en, tags):
    art, _, word = de.partition(" ")
    e = _entry(word, "noun")
    plural = e["plural"] if e else ""
    extra = f"Plural: die {plural}" if plural and plural != "-" else ("no plural" if e and not plural else "")
    return {"type": "vocab", "front": de, "back": en, "extra": extra, "tags": tags}


def verb_forms(word):
    """'er fährt, fuhr, ist gefahren' (or '' when the dictionary doesn't know the verb)."""
    if word in FORMS:
        return FORMS[word]
    e = _entry(word, "verb")
    return e["forms_text"] if e and e.get("forms_text") else ""


FORMS = {"sein": "er ist, war, ist gewesen"}  # (the dictionary keeps sein's forms in a table it doesn't parse)


def _is_irregular(word):
    e = _entry(word, "verb")
    if not e:
        return False
    i = e["info"]
    praet, pp = (i.get("praet") or "").split(" ")[0], i.get("pp") or ""
    stem = re.sub(r"(e?n)$", "", word)
    regular = praet in (stem + "te", stem + "ete") and pp.endswith(("t",)) and stem in pp
    return bool(praet and pp) and not regular


# ---------- the packs ----------
def _vocab_pack(text, tag):
    return [_noun_card(de, en, ["pack", tag]) for de, en in _items(text)]


def _verbs():
    return [{"type": "verb", "front": de, "back": en, "extra": verb_forms(de), "tags": ["pack", "verbs"]}
            for de, en in _items(VERBS)]


def _irregular():
    out = []
    for de, en in _items(VERBS):
        if de in ("sein", "haben", "werden") or _is_irregular(de):
            forms = verb_forms(de)
            if forms:
                out.append({"type": "verb", "front": f"{de} · {en}", "back": forms,
                            "extra": "Say the er-form, the Präteritum and the Perfekt.", "tags": ["pack", "irregular"]})
    return out


def _adjectives():
    out = []
    for de, en in _items(ADJECTIVES):
        e = _entry(de, "adj")
        comp, sup = (e["info"].get("comp"), e["info"].get("sup")) if e else (None, None)
        extra = f"{de}, {comp}, {sup}" if comp and sup else ""
        out.append({"type": "vocab", "front": de, "back": en, "extra": extra, "tags": ["pack", "adjectives"]})
    return out


def _common_nouns(lo, hi):
    out = []
    for n in dictionary.nouns(0, 100000):
        if len(out) >= hi:
            break
        art = {"m": "der", "f": "die", "n": "das"}.get(n["g"])
        if not art or not n["pl"]:
            continue
        out.append({"type": "vocab", "front": f"{art} {n['word']}", "back": dictionary.short([n["meaning"]]),
                    "extra": f"Plural: die {n['pl']}" if n["pl"] != "-" else "no plural", "tags": ["pack", "nouns"]})
    return out[lo:hi]


PACKS = [
    # id, title, level, group, description, builder
    ("phrases", "Everyday phrases", "A1", "Words", "Greetings, thanks, asking for help, at the café: the phrases you need first.",
     lambda: [{"type": "phrase", "front": r[0], "back": r[1], "extra": r[2] if len(r) > 2 else "", "tags": ["pack", "phrases"]}
              for r in _rows(PHRASES)]),
    ("nouns-1", "Most common nouns 1", "A1", "Words", "The 300 most common nouns, with der/die/das and the plural. Meanings from Wiktionary.",
     lambda: _common_nouns(0, 300)),
    ("nouns-2", "Most common nouns 2", "A2", "Words", "The next 700 most common nouns.",
     lambda: _common_nouns(300, 1000)),
    ("verbs", "Core verbs", "A1", "Words", "About 160 verbs you'll meet all the time, each with its forms (er geht, ging, ist gegangen).",
     _verbs),
    ("adjectives", "Core adjectives", "A1", "Words", "About 110 common adjectives, with comparative and superlative.",
     _adjectives),
    *[(f"topic-{k}", t, lvl, "Topics", "Nouns with their article and plural.", (lambda text=text, k=k: _vocab_pack(text, k)))
      for k, (t, lvl, text) in TOPICS.items()],
    ("irregular", "Irregular verbs", "A2", "Grammar", "Strong and mixed verbs: from the infinitive, say the er-form, Präteritum and Perfekt.",
     _irregular),
    ("dative-verbs", "Verbs with the dative", "A2", "Grammar", "helfen, danken, gefallen... the verbs whose object is in the dative.",
     lambda: [{"type": "vocab", "front": f"{r[0]} + ?", "back": f"+ Dativ ({r[1]})", "extra": r[2], "tags": ["pack", "dative-verbs"]}
              for r in _rows(DATIVE_VERBS)]),
    ("verb-preps", "Verbs with prepositions", "B1", "Grammar", "warten auf + Akk., Angst haben vor + Dat.: which preposition and which case.",
     lambda: [{"type": "vocab", "front": f"{r[0]} ___ ({r[1]})", "back": r[2], "extra": r[3], "tags": ["pack", "verb-preps"]}
              for r in _rows(VERB_PREPS)]),
    ("prepositions", "Prepositions and their case", "A2", "Grammar", "Accusative, dative, two-way and genitive prepositions, with examples.",
     lambda: [{"type": "vocab", "front": f"{r[0]} + ?", "back": r[1], "extra": r[2], "tags": ["pack", "prepositions"]}
              for r in _rows(PREPOSITIONS)]),
    ("false-friends", "False friends", "A2", "Words", "German words that look English but aren't: bekommen, Gift, Handy...",
     lambda: [{"type": "vocab", "front": r[0], "back": r[1], "extra": r[2] if len(r) > 2 else "", "tags": ["pack", "false-friends"]}
              for r in _rows(FALSE_FRIENDS)]),
]
BY_ID = {p[0]: p for p in PACKS}


@functools.lru_cache(maxsize=None)
def cards(pack_id):
    """The pack's cards, built once (they only depend on the lists above and the dictionary)."""
    p = BY_ID[pack_id]
    out = []
    seen = set()
    for c in p[5]():
        if c["front"] in seen:
            continue
        seen.add(c["front"])
        c["tags"] = ["pack:" + pack_id] + [t for t in c["tags"] if t != "pack"]
        out.append(c)
    return tuple(json.dumps(c, ensure_ascii=False) for c in out)


def pack_cards(pack_id):
    return [json.loads(c) for c in cards(pack_id)]


def _tag_like(pack_id):
    return f'%"pack:{pack_id}"%'


def library():
    have_fronts = {r["front"] for r in db.q("SELECT front FROM cards")}
    out = []
    for pid, title, level, group, desc, _ in PACKS:
        cs = pack_cards(pid)
        added = db.q1("SELECT COUNT(*) AS n FROM cards WHERE tags LIKE ?", (_tag_like(pid),))["n"]
        out.append({"id": pid, "title": title, "level": level, "group": group, "description": desc, "count": len(cs),
                    "added": added, "have": sum(1 for c in cs if c["front"] in have_fronts),
                    "sample": [{k: c[k] for k in ("front", "back", "extra")} for c in cs[:4]]})
    return out


def add(pack_id):
    """Adds the pack's cards that aren't in the deck yet (same front), in the pack's order."""
    have = {r["front"] for r in db.q("SELECT front FROM cards")}
    now = db.now()
    rows = [(None, None, c["type"], c["front"], c["back"], c["extra"], json.dumps(c["tags"], ensure_ascii=False), now)
            for c in pack_cards(pack_id) if c["front"] not in have]
    db.exmany("INSERT INTO cards(book_id, chapter_id, type, front, back, extra, tags, created_at) VALUES(?,?,?,?,?,?,?,?)", rows)
    return {"added": len(rows), "skipped": len(pack_cards(pack_id)) - len(rows)}


def remove(pack_id, only_new=False):
    sql = "DELETE FROM cards WHERE tags LIKE ?" + (" AND due IS NULL" if only_new else "")
    n = db.q1("SELECT COUNT(*) AS n FROM cards WHERE tags LIKE ?" + (" AND due IS NULL" if only_new else ""), (_tag_like(pack_id),))["n"]
    db.ex(sql, (_tag_like(pack_id),))
    return {"removed": n}
