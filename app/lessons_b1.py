"""The built-in course, level B1: 22 lessons along the Goethe-Zertifikat B1 themes and grammar.

Same format as app/lessons_data.py: words ("German=English", nouns with their article), a dialogue
("Speaker|German|English"), one grammar point (title, explanation, examples "German=English") and exercises
("Sentence with ___|answer|wrong choice|wrong choice"), plus "level". Ids start with "b1-".
The grammar builds up lesson by lesson: Präteritum, als/wenn, Plusquamperfekt, time clauses, Konjunktiv II,
zu + infinitive, relative clauses, the passive, n-declension, genitive, verbs with prepositions, two-part
conjunctions, Futur I, indirect questions, adjective endings and participles.
Turkish for every English text here is in app/lessons_b1_tr.py; tests/test_lessons_b1.py checks both.
"""

LESSONS = [
    {
        "id": "b1-lebenslauf", "level": "B1", "title": "Mein Lebenslauf", "subtitle": "Telling your life story in the Präteritum",
        "words": """der Lebenslauf=CV, résumé; die Ausbildung=vocational training; das Studium=university studies;
der Abschluss=degree, qualification; die Erfahrung=experience; die Stelle=job, position; der Beruf=profession;
die Firma=company; das Praktikum=internship; der Arbeitgeber=employer; die Verantwortung=responsibility;
geboren=born; aufwachsen=to grow up; studieren=to study (at university); umziehen=to move (house);
beginnen=to begin; damals=back then; später=later; zuerst=at first""",
        "dialogue": """Frau Brandt|Erzählen Sie doch bitte etwas über sich, Herr Demir.|Please tell me a little about yourself, Mr. Demir.
Herr Demir|Gern. Ich wurde 1995 in Izmir geboren und wuchs dort auf.|Gladly. I was born in Izmir in 1995 and grew up there.
Frau Brandt|Und was machten Sie nach der Schule?|And what did you do after school?
Herr Demir|Ich studierte Informatik in Ankara. Im dritten Jahr machte ich ein Praktikum bei einer Firma in Hamburg.|I studied computer science in Ankara. In my third year I did an internship at a company in Hamburg.
Frau Brandt|Wie gefiel Ihnen die Arbeit dort?|How did you like the work there?
Herr Demir|Sie gefiel mir sehr gut. Deshalb zog ich 2020 nach Deutschland um.|I liked it very much. That's why I moved to Germany in 2020.
Frau Brandt|Und seitdem arbeiten Sie als Programmierer?|And since then you've been working as a programmer?
Herr Demir|Ja. Zuerst hatte ich eine kleine Stelle, später bekam ich mehr Verantwortung.|Yes. At first I had a small job, later I got more responsibility.""",
        "grammar": ("The Präteritum", """In written German (a CV, a report, a story, the news) the past is usually told in the **Präteritum**. In conversation, people use it mostly with **sein**, **haben** and the modal verbs: war, hatte, konnte, musste.

**Regular verbs** add **-te** to the stem:
- ich mach**te**, du mach**test**, er mach**te**, wir mach**ten**, ihr mach**tet**, sie mach**ten**
- After -t or -d the stem gets an extra e: arbeiten → ich arbeit**ete**

**Irregular verbs** change their vowel. The ich and er forms have no ending:
- gehen → ging → ist gegangen
- beginnen → begann → hat begonnen
- finden → fand → hat gefunden
- ich ging, du gingst, er ging, wir gingen, ihr gingt, sie gingen

**Mixed verbs** change the vowel and also add -te: denken → dachte, bringen → brachte, kennen → kannte.

Separable verbs split just as in the present: Ich **zog** 2020 nach Berlin **um**.""",
                    "Ich wuchs in einem kleinen Dorf auf.=I grew up in a small village.; Nach der Schule begann sie eine Ausbildung.=After school she started vocational training.; Wir zogen 2018 nach Köln um.=We moved to Cologne in 2018.; Damals arbeitete er bei einer großen Firma.=Back then he worked for a big company."),
        "exercises": """Ich ___ 2015 mein Studium. (beginnen)|begann|beginnte|begonnen
Früher ___ er drei Jahre in München. (arbeiten)|arbeitete|arbeitet|arbeitte
Wir ___ in einer kleinen Stadt auf. (wachsen)|wuchsen|wachsten|wuchs
Damals ___ sie keine Zeit. (haben)|hatte|habte|hattet
2019 ___ ich nach Berlin um. (ziehen)|zog|ziehte|zogen
___ du damals schon in Hamburg? (sein)|Warst|War|Wart
Nach dem Abschluss ___ er schnell eine Stelle. (finden)|fand|findete|fanden""",
    },
    {
        "id": "b1-schulzeit", "level": "B1", "title": "Meine Schulzeit", "subtitle": "School memories with als and wenn",
        "words": """die Grundschule=primary school; das Gymnasium=academic secondary school; das Fach=school subject;
die Note=grade, mark; das Zeugnis=school report; die Prüfung=exam; die Klasse=class, school year;
die Hausaufgabe=homework task; das Abitur=final secondary school exam; bestehen=to pass (an exam);
durchfallen=to fail (an exam); sich erinnern=to remember; streng=strict; fleißig=hard-working; faul=lazy;
stolz=proud; als=when (once in the past); wenn=when, whenever, if""",
        "dialogue": """Jana|Erinnerst du dich gern an deine Schulzeit?|Do you like remembering your school days?
Murat|Meistens schon. Als ich in die Grundschule kam, konnte ich noch kein Deutsch.|Mostly, yes. When I started primary school, I couldn't speak any German yet.
Jana|Das war bestimmt schwer.|That must have been hard.
Murat|Am Anfang schon. Aber wenn ich etwas nicht verstand, half mir meine Lehrerin.|At first, yes. But whenever I didn't understand something, my teacher helped me.
Jana|Und auf dem Gymnasium? Warst du ein fleißiger Schüler?|And at secondary school? Were you a hard-working student?
Murat|Nicht immer! In Mathe hatte ich oft schlechte Noten. Einmal bin ich sogar durch eine Prüfung gefallen.|Not always! In math I often had bad grades. Once I even failed an exam.
Jana|Und wie war es, als du das Abitur bestanden hast?|And what was it like when you passed your final exams?
Murat|Wunderbar! Meine Eltern waren sehr stolz, und wir haben die ganze Nacht gefeiert.|Wonderful! My parents were very proud, and we celebrated all night.""",
        "grammar": ("als or wenn?", """Both mean "when", but German keeps them apart:

- **als**: one single event or one period in the past. **Als** ich sechs war, kam ich in die Schule.
- **wenn**: something that happened again and again in the past (whenever): **Wenn** ich Hausaufgaben machte, hörte ich Musik.
- **wenn** also for anything in the present or future (when, if): **Wenn** ich morgen Zeit habe, rufe ich dich an.

Both start a side clause, so the verb goes to the **end**. If the side clause comes first, the main clause starts with its verb: **Als ich klein war, wohnten wir in Bremen.**

The question word "when?" is **wann**: **Wann** hast du Abitur gemacht? It also starts indirect questions: Ich weiß nicht, **wann** er kommt.""",
                    "Als ich zehn war, zogen wir nach Köln.=When I was ten, we moved to Cologne.; Wenn ich eine gute Note hatte, war meine Mutter stolz.=Whenever I got a good grade, my mother was proud.; Als sie die Prüfung bestand, war sie sehr glücklich.=When she passed the exam, she was very happy.; Wenn du Fragen hast, ruf mich an.=If you have questions, call me."),
        "exercises": """___ ich klein war, wohnten wir in Bremen.|Als|Wenn|Wann
___ es regnete, spielten wir immer drinnen.|Wenn|Als|Wann
___ hast du das Abitur gemacht?|Wann|Als|Wenn
___ ich morgen Zeit habe, komme ich vorbei.|Wenn|Als|Wann
Als er das Zeugnis bekam, ___ sehr froh.|war er|er war|ist er
Ich war traurig, als ich durch die Prüfung ___.|fiel|falle|gefallen
Jedes Mal, ___ der Lehrer kam, wurde es still.|wenn|als|wann""",
    },
    {
        "id": "b1-reisepech", "level": "B1", "title": "Pech auf der Reise", "subtitle": "Travel problems and the Plusquamperfekt",
        "words": """die Verspätung=delay; der Anschluss=connection (train, bus); der Flug=flight; der Flughafen=airport;
das Gepäck=luggage; der Koffer=suitcase; das Gleis=platform, track; die Durchsage=announcement;
der Schalter=counter, ticket desk; der Wecker=alarm clock; ausfallen=to be cancelled;
verpassen=to miss (a train, a flight); verlieren=to lose; abfahren=to depart; landen=to land;
umsteigen=to change (trains, buses); pünktlich=on time; leider=unfortunately""",
        "dialogue": """Sophie|Wie war deine Reise nach Wien?|How was your trip to Vienna?
Lukas|Eine Katastrophe! Als ich am Bahnhof ankam, war mein Zug schon abgefahren.|A disaster! When I got to the station, my train had already left.
Sophie|Oh nein! Warum warst du so spät?|Oh no! Why were you so late?
Lukas|Ich hatte den Wecker nicht gehört. Also nahm ich den nächsten Zug, aber der hatte eine Stunde Verspätung.|I hadn't heard the alarm clock. So I took the next train, but it was an hour late.
Sophie|Und dann hast du den Anschluss in München verpasst?|And then you missed your connection in Munich?
Lukas|Genau. Und in Wien merkte ich, dass ich meinen Koffer im Zug vergessen hatte.|Exactly. And in Vienna I noticed that I had left my suitcase on the train.
Sophie|Hast du ihn wiederbekommen?|Did you get it back?
Lukas|Ja, zum Glück hatte ihn jemand im Fundbüro abgegeben.|Yes, luckily someone had handed it in at the lost and found office.""",
        "grammar": ("Plusquamperfekt: the past before the past", """When you tell a story in the past and need to go one step further back, use the **Plusquamperfekt**. It's formed like the Perfekt, but with the past of haben or sein: **hatte / war + Partizip II**.

- Perfekt: Der Zug **ist abgefahren**.
- Plusquamperfekt: Der Zug **war** schon **abgefahren**. (before I arrived)

The forms:
- ich **hatte** gehört / ich **war** gegangen
- du **hattest** gehört / du **warst** gegangen
- er, sie, es **hatte** gehört / **war** gegangen
- wir **hatten** gehört / wir **waren** gegangen

Verbs that take sein in the Perfekt take **war** here: abfahren → der Zug **war abgefahren**, ankommen → wir **waren angekommen**. All other verbs take **hatte**: verpassen → ich **hatte** den Zug **verpasst**.

It often comes with **als** or **nachdem**: Als ich ankam, **war** der Zug schon **abgefahren**.""",
                    "Ich hatte das Ticket schon gekauft.=I had already bought the ticket.; Als wir landeten, hatte der Regen aufgehört.=When we landed, the rain had stopped.; Sie war noch nie geflogen.=She had never flown before.; Er hatte seinen Pass zu Hause vergessen.=He had left his passport at home."),
        "exercises": """Als ich ankam, ___ der Zug schon abgefahren.|war|hatte|ist
Als wir in München ankamen, ___ wir den Anschluss schon verpasst.|hatten|waren|sind
Sie hatte ihren Koffer im Zug ___.|vergessen|vergisst|vergaß
Das Flugzeug war schon ___, als wir am Flughafen waren.|gelandet|landete|landen
Er kam zu spät, denn er ___ den Wecker nicht gehört.|hatte|war|ist
Ich war vorher noch nie in Wien ___.|gewesen|gehabt|sein""",
    },
    {
        "id": "b1-arbeitstag", "level": "B1", "title": "Der erste Arbeitstag", "subtitle": "Time clauses: bevor, nachdem, während, seit",
        "words": """der Arbeitsplatz=workplace, job; der Kollege=colleague (man); die Kollegin=colleague (woman); der Chef=boss;
die Besprechung=meeting; die Aufgabe=task; die Pause=break; die Kantine=canteen; der Vertrag=contract;
die Überstunde=hour of overtime; vorstellen=to introduce; erledigen=to get done; unterschreiben=to sign;
zuständig=responsible (for); bevor=before; nachdem=after; während=while; seit=since""",
        "dialogue": """Herr Lehmann|Willkommen, Frau Kaya! Bevor wir anfangen, stelle ich Ihnen das Team vor.|Welcome, Ms. Kaya! Before we start, I'll introduce you to the team.
Frau Kaya|Danke! Wann ist eigentlich die Mittagspause?|Thank you! When is the lunch break, by the way?
Herr Lehmann|Um zwölf. Nachdem wir gegessen haben, haben wir eine kurze Besprechung.|At twelve. After we've eaten, we have a short meeting.
Frau Kaya|Wer ist für meine Einarbeitung zuständig?|Who is responsible for training me?
Herr Lehmann|Frau Roth. Sie arbeitet seit zehn Jahren hier und kennt alle Aufgaben.|Ms. Roth. She has been working here for ten years and knows all the tasks.
Frau Kaya|Muss ich heute noch den Vertrag unterschreiben?|Do I need to sign the contract today?
Herr Lehmann|Ja, bitte. Während Sie unterschreiben, hole ich uns einen Kaffee.|Yes, please. While you sign, I'll get us a coffee.""",
        "grammar": ("bevor, nachdem, während, seit", """These words start a side clause about time. The verb goes to the **end** of the clause.

- **bevor** (before): **Bevor** ich zur Arbeit gehe, trinke ich einen Kaffee.
- **nachdem** (after): **Nachdem** ich den Vertrag unterschrieben hatte, begann ich mit der Arbeit.
- **während** (while): **Während** du telefonierst, schreibe ich die E-Mail.
- **seit** or **seitdem** (since): **Seit** ich hier arbeite, fahre ich mit dem Rad.

With **nachdem** the tenses move one step back, because the action in the nachdem clause happened first:
- Main clause in the present → Perfekt: Nachdem ich gegessen **habe**, gehe ich zur Besprechung.
- Main clause in the past → Plusquamperfekt: Nachdem ich gegessen **hatte**, ging ich zur Besprechung.

Don't mix up the conjunction **nachdem** with the preposition **nach**: **nach** der Arbeit, but **nachdem** ich gearbeitet habe.""",
                    "Bevor du gehst, mach bitte das Licht aus.=Before you leave, please turn off the light.; Nachdem sie die Aufgabe erledigt hatte, machte sie eine Pause.=After she had finished the task, she took a break.; Während der Chef spricht, schreibe ich mit.=While the boss is speaking, I take notes.; Seit er hier arbeitet, macht er viele Überstunden.=Since he started working here, he has done a lot of overtime."),
        "exercises": """___ ich die E-Mail abschicke, lese ich sie noch einmal.|Bevor|Nachdem|Seit
Nachdem er gegessen ___, ging er zurück ins Büro.|hatte|hat|war
___ sie in Berlin wohnt, fährt sie mit dem Rad zur Arbeit.|Seit|Bevor|Nachdem
___ ich koche, höre ich immer Radio.|Während|Nachdem|Seit
Nachdem ich den Vertrag unterschrieben ___, beginne ich mit der Arbeit.|habe|hatte|bin
Bevor ich nach Hause gehe, ___ die E-Mails.|lese ich|ich lese|ich lesen
___ der Arbeit gehe ich einkaufen.|Nach|Nachdem|Bevor""",
    },
    {
        "id": "b1-bewerbung", "level": "B1", "title": "Die Bewerbung", "subtitle": "Applying for a job and asking politely",
        "words": """die Bewerbung=application; sich bewerben=to apply; die Stellenanzeige=job advertisement;
das Vorstellungsgespräch=job interview; das Gehalt=salary; die Voraussetzung=requirement;
der Bewerber=applicant; das Anschreiben=cover letter; die Teilzeit=part-time work; die Vollzeit=full-time work;
die Probezeit=probation period; einstellen=to hire; kündigen=to quit, to give notice; verdienen=to earn;
erfahren=experienced; flexibel=flexible; selbstständig=independent, independently""",
        "dialogue": """Frau Schulz|Firma Weber und Partner, Schulz am Apparat. Guten Tag!|Weber and Partners, Schulz speaking. Hello!
Herr Yılmaz|Guten Tag, mein Name ist Yılmaz. Ich habe Ihre Stellenanzeige gelesen und hätte ein paar Fragen.|Hello, my name is Yılmaz. I read your job advertisement and have a few questions.
Frau Schulz|Gern. Worum geht es?|Of course. What is it about?
Herr Yılmaz|Könnten Sie mir sagen, ob die Stelle auch in Teilzeit möglich ist?|Could you tell me whether the job is also possible part-time?
Frau Schulz|Leider nicht, wir suchen jemanden in Vollzeit.|Unfortunately not, we're looking for someone full-time.
Herr Yılmaz|Das ist kein Problem. Würden Sie mir noch sagen, an wen ich meine Bewerbung schicken soll?|That's no problem. Would you also tell me who I should send my application to?
Frau Schulz|Schicken Sie sie bitte direkt an mich. Wir würden uns freuen, bald von Ihnen zu hören!|Please send it straight to me. We'd be glad to hear from you soon!
Herr Yılmaz|Vielen Dank, das mache ich gern.|Thank you very much, I'll be glad to.""",
        "grammar": ("Konjunktiv II: asking politely", """To make a request or a wish sound polite, German uses the **Konjunktiv II**. It's like English "would", "could" or "might".

The most useful forms:
- **würde** + infinitive: Ich **würde** gern mehr **verdienen**. **Würden** Sie mir helfen?
- **könnte** (could): **Könnten** Sie das bitte wiederholen?
- **hätte** (would have): Ich **hätte** eine Frage.
- **wäre** (would be): Das **wäre** sehr nett.
- **möchte** (would like): Ich **möchte** mich um die Stelle bewerben.
- **sollte** (should): Sie **sollten** Ihren Lebenslauf mitschicken.

The endings: ich würde, du würdest, er würde, wir würden, ihr würdet, sie würden. hätte, wäre and könnte work the same way: du hättest, du wärst, du könntest.

Compare: **Können Sie** mir helfen? (direct) → **Könnten Sie** mir helfen? (more polite)""",
                    "Könnten Sie mir bitte die Unterlagen schicken?=Could you send me the documents, please?; Ich hätte gern mehr Informationen über die Stelle.=I'd like more information about the position.; Würden Sie mich bitte zurückrufen?=Would you please call me back?; Es wäre schön, wenn wir uns persönlich treffen könnten.=It would be nice if we could meet in person."),
        "exercises": """___ Sie mir bitte helfen?|Könnten|Konnten|Könntest
Ich ___ gern mehr über die Stelle erfahren.|würde|wurde|würdest
Ich ___ eine Frage zum Gehalt.|hätte|hättest|hätten
Das ___ wirklich nett von Ihnen.|wäre|wären|wärst
___ du mir kurz deinen Lebenslauf zeigen?|Könntest|Könnten|Könnte
Wir ___ uns freuen, von Ihnen zu hören.|würden|würde|würdet
Sie ___ unbedingt Ihre Zeugnisse mitschicken.|sollten|solltest|sollte""",
    },
    {
        "id": "b1-gesund", "level": "B1", "title": "Gesund leben", "subtitle": "Health, habits and the Konjunktiv II for wishes",
        "words": """die Gesundheit=health; die Ernährung=diet, nutrition; die Bewegung=exercise, movement; der Stress=stress;
das Gewicht=weight; der Rücken=back (body); der Schmerz=pain; die Krankheit=illness; das Rezept=prescription, recipe;
die Krankenkasse=health insurance company; sich ernähren=to eat (a diet); abnehmen=to lose weight;
zunehmen=to gain weight; aufhören=to stop; sich entspannen=to relax; regelmäßig=regular, regularly;
ungesund=unhealthy""",
        "dialogue": """Ärztin|Herr Becker, Ihre Rückenschmerzen kommen vom Stress und von zu wenig Bewegung.|Mr. Becker, your back pain comes from stress and too little exercise.
Herr Becker|Ich weiß. Wenn ich mehr Zeit hätte, würde ich jeden Tag Sport machen.|I know. If I had more time, I would do sports every day.
Ärztin|Schon zwanzig Minuten am Tag würden helfen. Sie könnten zum Beispiel mit dem Rad zur Arbeit fahren.|Even twenty minutes a day would help. You could cycle to work, for example.
Herr Becker|Das wäre eine Idee. Aber ich wohne so weit weg.|That would be an idea. But I live so far away.
Ärztin|Und wie ernähren Sie sich?|And how do you eat?
Herr Becker|Ehrlich gesagt ziemlich ungesund. Ich wünschte, ich könnte besser kochen.|To be honest, quite unhealthily. I wish I could cook better.
Ärztin|An Ihrer Stelle würde ich einen Kochkurs machen. Die Krankenkasse bezahlt oft einen Teil.|If I were you, I would take a cooking class. The health insurance often pays part of it.""",
        "grammar": ("Konjunktiv II: wishes and unreal conditions", """The Konjunktiv II also talks about things that are **not real**: wishes, dreams and "what if".

**Unreal conditions** use **wenn** and the Konjunktiv II in both parts:
- **Wenn** ich mehr Zeit **hätte**, **würde** ich mehr Sport **machen**. (But I don't have more time.)
- **Wenn** ich du **wäre**, **würde** ich zum Arzt gehen.

Compare a real condition: **Wenn** ich Zeit **habe**, mache ich Sport. (That's possible.)

**Wishes** use **wenn ... nur** or **ich wünschte**:
- **Wenn** ich **nur** gesünder **wäre**!
- **Ich wünschte**, ich **könnte** besser schlafen.

**Advice**: **An deiner Stelle würde ich** ... (If I were you, I would ...)

Most verbs use **würde** + infinitive. sein, haben and the modal verbs use their own forms: **wäre, hätte, könnte, müsste, dürfte**. A few common verbs also have their own: **käme, ginge, wüsste**.""",
                    "Wenn ich nicht so müde wäre, würde ich joggen gehen.=If I weren't so tired, I would go jogging.; Wenn sie weniger Stress hätte, könnte sie besser schlafen.=If she had less stress, she could sleep better.; Ich wünschte, ich hätte mehr Zeit für Sport.=I wish I had more time for sports.; An deiner Stelle würde ich mit dem Rauchen aufhören.=If I were you, I would stop smoking."),
        "exercises": """Wenn ich mehr Zeit ___, würde ich Sport machen.|hätte|habe|hatte
Wenn ich du ___, würde ich zum Arzt gehen.|wäre|bin|war
Ich wünschte, ich ___ besser schlafen.|könnte|kann|konnte
An deiner Stelle ___ ich weniger Kaffee trinken.|würde|werde|wurde
Wenn er gesünder essen würde, ___ abnehmen.|könnte er|er könnte|er kann
Wenn wir nur nicht so viel Stress ___!|hätten|haben|hättet
Immer wenn ich Zeit habe, ___ ich spazieren.|gehe|würde|wäre""",
    },
    {
        "id": "b1-reklamation", "level": "B1", "title": "Die Reklamation", "subtitle": "Consumer complaints and the Konjunktiv II in the past",
        "words": """die Reklamation=complaint about a faulty product; die Beschwerde=complaint; sich beschweren=to complain;
der Kunde=customer; der Kundenservice=customer service; die Garantie=warranty, guarantee; die Quittung=receipt;
der Umtausch=exchange (of goods); umtauschen=to exchange; zurückgeben=to return, to give back;
reparieren=to repair; defekt=faulty, defective; zurückbekommen=to get back; der Fehler=fault, mistake;
die Lieferung=delivery; ärgerlich=annoying; enttäuscht=disappointed""",
        "dialogue": """Frau Aydın|Guten Tag. Ich möchte mich beschweren. Diese Kaffeemaschine ist nach zwei Wochen kaputtgegangen.|Hello. I'd like to make a complaint. This coffee machine broke after two weeks.
Verkäufer|Das tut mir leid. Haben Sie die Quittung dabei?|I'm sorry. Do you have the receipt with you?
Frau Aydın|Ja, hier. Ich hätte gern mein Geld zurück.|Yes, here. I'd like my money back.
Verkäufer|Wir könnten die Maschine reparieren lassen. Sie hat zwei Jahre Garantie.|We could have the machine repaired. It has a two-year warranty.
Frau Aydın|Ehrlich gesagt bin ich enttäuscht. Wenn ich das gewusst hätte, hätte ich ein anderes Modell gekauft.|Honestly, I'm disappointed. If I had known that, I would have bought a different model.
Verkäufer|Ich verstehe. Dann tauschen wir sie gegen ein neues Modell um.|I understand. Then we'll exchange it for a new model.
Frau Aydın|Danke. Das hätten Sie mir auch gleich anbieten können!|Thank you. You could have offered me that right away!""",
        "grammar": ("Konjunktiv II in the past", """To talk about something that **didn't happen** in the past (regrets, missed chances), use **hätte** or **wäre** + **Partizip II**:

- Wenn ich das **gewusst hätte**, **hätte** ich die Maschine nicht **gekauft**. (But I didn't know.)
- Wenn das Paket früher **gekommen wäre**, **wäre** ich zu Hause **gewesen**.

Choose hätte or wäre just as you choose haben or sein in the Perfekt:
- gekauft, gewusst, gesagt → **hätte**
- gekommen, gegangen, gewesen → **wäre**

Regrets: **Hätte** ich **nur** die Garantie **gelesen**! (If only I had read the warranty!)

With a modal verb, use **hätte** and two infinitives at the end: Sie **hätten** mich anrufen **sollen**. (You should have called me.) Das **hätten** Sie mir gleich anbieten **können**. (You could have offered me that right away.)""",
                    "Wenn ich die Quittung aufgehoben hätte, hätte ich das Geld zurückbekommen.=If I had kept the receipt, I would have got the money back.; Wenn die Lieferung pünktlich gekommen wäre, hätte ich mich nicht beschwert.=If the delivery had come on time, I wouldn't have complained.; Hätte ich nur ein anderes Modell gekauft!=If only I had bought a different model!; Sie hätten mich anrufen sollen.=You should have called me."),
        "exercises": """Wenn ich das gewusst ___, hätte ich nichts gekauft.|hätte|wäre|habe
Wenn das Paket pünktlich gekommen ___, wäre ich zufrieden gewesen.|wäre|hätte|ist
___ ich nur die Garantie gelesen!|Hätte|Wäre|Habe
Wir wären früher gekommen, wenn wir es ___ hätten.|gewusst|gewesen|wissen
Sie hätten mich anrufen ___.|sollen|gesollt|sollten
Ohne Quittung hätte ich mein Geld nicht ___.|zurückbekommen|zurückbekam|zurückzubekommen
Wenn der Verkäufer freundlicher gewesen ___, hätte ich mich nicht beschwert.|wäre|hätte|war""",
    },
    {
        "id": "b1-weiterbildung", "level": "B1", "title": "Lernen ein Leben lang", "subtitle": "Further education and the infinitive with zu",
        "words": """die Weiterbildung=further training; der Kurs=course; die Volkshochschule=adult education center;
die Gebühr=fee; das Zertifikat=certificate; das Ziel=goal; die Möglichkeit=possibility, opportunity;
die Anmeldung=registration; die Fähigkeit=ability, skill; vorhaben=to plan, to intend; versuchen=to try;
sich anmelden=to register, to sign up; teilnehmen=to take part; beschließen=to decide; empfehlen=to recommend;
anbieten=to offer; beruflich=professional, professionally""",
        "dialogue": """Elif|Ich habe beschlossen, eine Weiterbildung zu machen.|I've decided to do some further training.
Thomas|Super! Was hast du vor?|Great! What are you planning?
Elif|Ich habe vor, einen Kurs in Buchhaltung zu besuchen. Die Volkshochschule bietet einen an.|I'm planning to take a course in bookkeeping. The adult education center offers one.
Thomas|Ist es schwer, einen Platz zu bekommen?|Is it hard to get a place?
Elif|Nein, man muss sich nur online anmelden. Die Gebühr ist auch nicht hoch.|No, you just have to register online. The fee isn't high either.
Thomas|Hast du denn Zeit, neben der Arbeit zu lernen?|Do you have time to study alongside your job, though?
Elif|Ich versuche, jeden Abend eine Stunde zu lernen. Am Ende bekomme ich ein Zertifikat.|I try to study for an hour every evening. At the end I get a certificate.
Thomas|Das klingt gut. Ich empfehle dir, dein Ziel aufzuschreiben.|That sounds good. I recommend you write down your goal.""",
        "grammar": ("zu + infinitive", """After many verbs, nouns and adjectives, a second verb comes with **zu** at the very end:

- Ich **versuche**, jeden Tag **zu lernen**.
- Ich **habe** keine **Zeit**, ins Kino **zu gehen**.
- **Es ist wichtig**, regelmäßig **zu üben**.

With separable verbs, **zu** goes between the prefix and the verb, written as one word: an**zu**fangen, auf**zu**stehen, an**zu**melden.

Common starters:
- verbs: **anfangen, aufhören, beschließen, vergessen, versuchen, vorhaben, empfehlen**
- nouns: **Lust haben, Zeit haben, Angst haben**
- adjectives: **es ist wichtig / schwer / leicht / schön**

**No zu** after the modal verbs: Ich **muss** lernen. Wir **können** morgen anfangen.""",
                    "Ich habe vor, nächstes Jahr einen Sprachkurs zu machen.=I'm planning to do a language course next year.; Vergiss nicht, dich rechtzeitig anzumelden!=Don't forget to register in time!; Es ist nicht leicht, neben der Arbeit zu studieren.=It isn't easy to study alongside a job.; Hast du Lust, mit mir den Kurs zu besuchen?=Would you like to take the course with me?"),
        "exercises": """Ich habe vor, einen Kurs ___.|zu machen|machen|zu mache
Es ist wichtig, früh ___.|aufzustehen|zu aufstehen|aufstehen
Wir können morgen ___.|anfangen|anzufangen|zu anfangen
Hast du Lust, ins Kino ___?|zu gehen|gehen|zu gehst
Sie hat vergessen, sich ___.|anzumelden|zu anmelden|anmelden
Er versucht, jeden Tag Deutsch ___.|zu sprechen|sprechen|zu spricht
Ich muss heute lange ___.|arbeiten|zu arbeiten|arbeite""",
    },
    {
        "id": "b1-bank", "level": "B1", "title": "Auf der Bank", "subtitle": "Money and banking: um ... zu, damit, ohne ... zu, statt ... zu",
        "words": """das Konto=bank account; die Überweisung=bank transfer; überweisen=to transfer (money);
die Kreditkarte=credit card; die Geheimzahl=PIN; der Geldautomat=cash machine, ATM; abheben=to withdraw (money);
sparen=to save (money); leihen=to lend, to borrow; der Kredit=loan; die Miete=rent; ausgeben=to spend;
das Bargeld=cash; der Betrag=amount; eröffnen=to open (an account, a shop); der Kontoauszug=bank statement;
die Filiale=branch (of a bank or shop)""",
        "dialogue": """Beraterin|Guten Tag, was kann ich für Sie tun?|Hello, what can I do for you?
Herr Novak|Ich möchte ein Konto eröffnen, um mein Gehalt hier zu bekommen.|I'd like to open an account so I can get my salary paid here.
Beraterin|Gern. Brauchen Sie auch eine Kreditkarte?|Certainly. Do you also need a credit card?
Herr Novak|Ja, damit ich im Ausland bezahlen kann. Kostet das Konto etwas?|Yes, so that I can pay abroad. Does the account cost anything?
Beraterin|Wenn Sie Onlinebanking nutzen, ist es kostenlos. So können Sie Überweisungen machen, ohne in die Filiale zu kommen.|If you use online banking, it's free. That way you can make transfers without coming to the branch.
Herr Novak|Sehr gut. Und kann ich überall Geld abheben?|Very good. And can I withdraw money everywhere?
Beraterin|An unseren Geldautomaten ja. Aber statt bar zu bezahlen, können Sie fast überall die Karte benutzen.|At our cash machines, yes. But instead of paying cash, you can use the card almost everywhere.""",
        "grammar": ("um ... zu, damit, ohne ... zu, statt ... zu", """**um ... zu** and **damit** both give a purpose (in order to, so that):
- Ich spare, **um** ein Auto **zu kaufen**. (same person: I save, I buy)
- Ich spare, **damit** meine Kinder studieren **können**. (different people: I save, my children study)

With the same person in both parts, use **um ... zu**. With different people you must use **damit**. It starts a side clause, so the verb goes to the end.

**ohne ... zu** (without ...ing): Er hat bezahlt, **ohne** die Rechnung **zu lesen**.
**statt ... zu** (instead of ...ing): **Statt** Geld **zu sparen**, gibt sie alles aus.

In all three zu forms, **zu** + infinitive comes at the end, and separable verbs take zu in the middle: Ich gehe zur Bank, um Geld ab**zu**heben.""",
                    "Ich gehe zum Geldautomaten, um Bargeld abzuheben.=I'm going to the cash machine to withdraw cash.; Ich überweise dir das Geld, damit du die Miete bezahlen kannst.=I'll transfer the money to you so that you can pay the rent.; Sie hat das Konto eröffnet, ohne die Gebühren zu prüfen.=She opened the account without checking the fees.; Statt einen Kredit aufzunehmen, sparen wir lieber.=Instead of taking out a loan, we'd rather save."),
        "exercises": """Ich spare, ___ eine Reise zu machen.|um|damit|ohne
Er arbeitet viel, ___ seine Familie gut leben kann.|damit|um|statt
Er hat unterschrieben, ___ den Vertrag zu lesen.|ohne|damit|weil
___ Geld zu sparen, kauft er ständig neue Sachen.|Statt|Um|Damit
Ich gehe zur Bank, um Geld ___.|abzuheben|zu abheben|abheben
Wir brauchen eine Kreditkarte, damit wir im Ausland bezahlen ___.|können|zu können|kann
Ich überweise das Geld, damit du es morgen ___.|hast|zu haben|haben""",
    },
    {
        "id": "b1-medien", "level": "B1", "title": "Medien und Technik", "subtitle": "Devices and media: relative clauses",
        "words": """das Gerät=device, appliance; der Bildschirm=screen; das Netz=network, internet; die Nachricht=message, news item;
die Sendung=broadcast, TV program; der Sender=channel, station; die Werbung=advertising, ads; die App=app;
das Passwort=password; der Akku=rechargeable battery; der Drucker=printer; herunterladen=to download;
speichern=to save (data); löschen=to delete; aufladen=to charge (a battery); installieren=to install;
benutzen=to use""",
        "dialogue": """Oma|Leon, kannst du mir helfen? Das ist das Handy, das ich letzte Woche gekauft habe.|Leon, can you help me? This is the phone I bought last week.
Leon|Klar, Oma. Was ist das Problem?|Sure, Grandma. What's the problem?
Oma|Der Akku, den ich jeden Tag aufladen muss, ist immer so schnell leer.|The battery, which I have to charge every day, is always empty so quickly.
Leon|Das liegt an den Apps, die im Hintergrund laufen. Ich lösche ein paar.|That's because of the apps that run in the background. I'll delete a few.
Oma|Aber nicht die App, die mir deine Mutter installiert hat!|But not the app your mother installed for me!
Leon|Keine Sorge. Wer ist eigentlich die Frau, der du so viele Nachrichten schickst?|Don't worry. By the way, who's the woman you send so many messages to?
Oma|Das ist meine Freundin Gisela, die seit einem Jahr in Spanien wohnt!|That's my friend Gisela, who has been living in Spain for a year!""",
        "grammar": ("Relative clauses", """A relative clause describes a noun more closely, like English "who", "which" or "that". It starts with a **relative pronoun**, the verb goes to the **end**, and there is always a comma before it.

The relative pronoun takes its **gender and number** from the noun it describes, and its **case** from its role in the relative clause:
- Nominative: Der Mann, **der** dort steht, ist mein Chef.
- Accusative: Der Laptop, **den** ich gekauft habe, ist schnell.
- Dative: Die Frau, **der** ich die E-Mail schicke, wohnt in Wien.

The forms (masculine, feminine, neuter, plural):
- Nominative: der, die, das, die
- Accusative: **den**, die, das, die
- Dative: **dem**, **der**, **dem**, **denen**
- Genitive: **dessen**, **deren**, **dessen**, **deren**

Unlike English, you can **never** leave out the relative pronoun: the phone I bought = das Handy, **das** ich gekauft habe.""",
                    "Das ist das Gerät, das nicht mehr funktioniert.=This is the device that doesn't work any more.; Wo ist der Drucker, den wir neu gekauft haben?=Where's the new printer we bought?; Die Kollegen, denen ich das Passwort gegeben habe, sind schon da.=The colleagues I gave the password to are already here.; Ich suche eine App, die keine Werbung hat.=I'm looking for an app that has no ads."),
        "exercises": """Der Laptop, ___ ich gekauft habe, ist sehr schnell.|den|der|dem
Die App, ___ ich benutze, ist kostenlos.|die|der|den
Das ist der Kollege, ___ mir geholfen hat.|der|den|dem
Die Frau, ___ ich die Nachricht geschickt habe, antwortet nicht.|der|die|denen
Das Handy, ___ auf dem Tisch liegt, gehört mir.|das|der|dem
Meine Eltern, ___ ich oft Fotos schicke, wohnen in Ankara.|denen|die|der
Der Sender, ___ ich am liebsten höre, spielt viel Musik.|den|der|dem""",
    },
    {
        "id": "b1-verein", "level": "B1", "title": "Im Verein", "subtitle": "Clubs and culture: relative clauses with prepositions, dessen and deren",
        "words": """der Verein=club, association; das Mitglied=member; die Veranstaltung=event; das Konzert=concert;
die Ausstellung=exhibition; das Theaterstück=play (theater); die Bühne=stage; der Eintritt=admission;
die Eintrittskarte=ticket (for an event); das Ehrenamt=volunteer work; der Chor=choir; die Mannschaft=team;
das Publikum=audience; sich engagieren=to get involved; mitmachen=to join in; stattfinden=to take place;
spannend=exciting""",
        "dialogue": """Nina|Was machst du eigentlich am Wochenende?|What do you actually do at the weekend?
Sami|Ich singe in einem Chor, in dem fast nur Rentner sind.|I sing in a choir that's almost all retirees.
Nina|Wirklich? Ist das nicht langweilig?|Really? Isn't that boring?
Sami|Gar nicht! Nächsten Monat findet ein Konzert statt, für das wir schon lange üben.|Not at all! Next month there's a concert we've been practicing for for a long time.
Nina|Toll! Ich bin in einem Theaterverein, dessen Mitglieder alle Anfänger sind.|Great! I'm in a theater club whose members are all beginners.
Sami|Und gibt es ein Stück, über das alle reden?|And is there a play everyone is talking about?
Nina|Ja, eine Komödie, deren Ende ich noch nicht verrate! Kommst du zur Premiere?|Yes, a comedy whose ending I'm not giving away yet! Will you come to the premiere?
Sami|Gern. Wo bekommt man Eintrittskarten?|Gladly. Where can you get tickets?""",
        "grammar": ("Relative clauses with prepositions; dessen and deren", """When the verb in the relative clause needs a preposition, the preposition comes **first**, then the relative pronoun in the case the preposition needs:

- sich interessieren **für** + accusative: Das ist der Verein, **für den** ich mich interessiere.
- singen **in** + dative: Der Chor, **in dem** ich singe, ist sehr gut.
- sprechen **über** + accusative: Das ist das Stück, **über das** alle sprechen.
- **mit** + dative: Die Freunde, **mit denen** ich ins Theater gehe, kommen aus Polen.

In German the preposition can **never** go to the end as in English (the club I'm interested in).

**Whose** is **dessen** for masculine and neuter nouns and **deren** for feminine nouns and plurals. The noun after it has no article:
- Der Verein, **dessen** Mitglieder alle Anfänger sind ... (the club whose members ...)
- Die Sängerin, **deren** Stimme so schön ist ... (the singer whose voice ...)""",
                    "Das ist die Ausstellung, von der ich dir erzählt habe.=That's the exhibition I told you about.; Der Verein, in dem ich spiele, sucht neue Mitglieder.=The club I play in is looking for new members.; Kennst du den Schauspieler, dessen Film gerade läuft?=Do you know the actor whose film is showing right now?; Die Nachbarn, mit denen wir ins Konzert gehen, sind sehr nett.=The neighbors we're going to the concert with are very nice."),
        "exercises": """Der Verein, in ___ ich spiele, hat 200 Mitglieder.|dem|den|der
Das ist die Band, für ___ ich mich interessiere.|die|der|den
Die Freunde, mit ___ ich ins Kino gehe, warten schon.|denen|den|die
Das Theaterstück, über ___ alle sprechen, ist ausverkauft.|das|dem|den
Der Sänger, ___ Konzert ich besucht habe, kommt aus Wien.|dessen|deren|den
Die Mannschaft, ___ Trainer neu ist, spielt sehr gut.|deren|dessen|der
Die Stadt, in ___ das Festival stattfindet, ist klein.|der|dem|die""",
    },
    {
        "id": "b1-umwelt", "level": "B1", "title": "Umwelt schützen", "subtitle": "The environment and the passive",
        "words": """die Umwelt=environment; der Müll=rubbish, garbage; die Verpackung=packaging; das Plastik=plastic;
die Energie=energy; der Strom=electricity; das Klima=climate; die Luft=air; der Verkehr=traffic;
das Pfand=deposit (on bottles); trennen=to separate; sammeln=to collect; recyceln=to recycle;
verbrauchen=to consume, to use up; schützen=to protect; verschmutzen=to pollute;
umweltfreundlich=environmentally friendly""",
        "dialogue": """Paul|Entschuldigung, Frau Schmidt, in welche Tonne kommt dieser Joghurtbecher?|Excuse me, Ms. Schmidt, which bin does this yogurt cup go in?
Frau Schmidt|In die gelbe Tonne. Dort werden alle Verpackungen aus Plastik gesammelt.|In the yellow bin. All plastic packaging is collected there.
Paul|Und was passiert dann damit?|And what happens to it then?
Frau Schmidt|Der Müll wird abgeholt und sortiert. Vieles wird recycelt.|The rubbish is picked up and sorted. A lot of it is recycled.
Paul|Und die Flaschen? Werden die auch in die gelbe Tonne geworfen?|And the bottles? Are they also thrown into the yellow bin?
Frau Schmidt|Nein! Für viele Flaschen bekommt man Pfand. Sie werden im Supermarkt zurückgegeben.|No! For many bottles you get a deposit. They're returned at the supermarket.
Paul|In Deutschland wird wirklich alles getrennt!|In Germany, everything really gets separated!""",
        "grammar": ("The passive: werden + Partizip II", """In the **passive**, what is done matters more than who does it. Form it with **werden** + **Partizip II** at the end:

- Active: Die Stadt **sammelt** den Müll.
- Passive: Der Müll **wird** (von der Stadt) **gesammelt**.

The object of the active sentence becomes the subject: **den** Müll → **der** Müll.

The forms of werden:
- ich **werde** gefragt, du **wirst** gefragt, er, sie, es **wird** gefragt
- wir **werden** gefragt, ihr **werdet** gefragt, sie, Sie **werden** gefragt

To say who does it, use **von** + dative: Das Papier wird **von den Kindern** gesammelt. Usually you leave it out.

A sentence with **man** says the same thing in the active: **Man** trennt den Müll. = Der Müll **wird** getrennt.""",
                    "In Deutschland wird der Müll getrennt.=In Germany, rubbish is separated.; Die Flaschen werden im Supermarkt zurückgegeben.=The bottles are returned at the supermarket.; Hier wird viel Strom verbraucht.=A lot of electricity is used here.; Das Papier wird jeden Dienstag abgeholt.=The paper is collected every Tuesday."),
        "exercises": """Der Müll ___ jeden Montag abgeholt.|wird|werden|ist
Die Flaschen ___ recycelt.|werden|wird|wirst
Hier wird viel Plastik ___.|verbraucht|verbrauchen|verbrauchte
Man trennt den Müll. → Der Müll wird ___.|getrennt|trennen|trennt
In der Schule ___ wir über das Klima informiert.|werden|wird|werdet
Das Papier wird ___ den Kindern gesammelt.|von|mit|bei
Die Firma produziert Strom. → Strom ___ von der Firma produziert.|wird|werden|hat""",
    },
    {
        "id": "b1-geschichte", "level": "B1", "title": "Ein Stück Geschichte", "subtitle": "Culture and history: the passive in the past",
        "words": """die Geschichte=history, story; das Denkmal=monument; das Schloss=palace, castle; der Krieg=war;
die Mauer=wall; die Grenze=border; die Wiedervereinigung=reunification; das Jahrhundert=century;
der König=king; der Künstler=artist; das Gemälde=painting; die Führung=guided tour; gründen=to found;
zerstören=to destroy; errichten=to erect, to put up; entdecken=to discover; malen=to paint; berühmt=famous""",
        "dialogue": """Führerin|Herzlich willkommen zur Führung! Dieses Schloss wurde im 18. Jahrhundert gebaut.|Welcome to the tour! This palace was built in the 18th century.
Besucher|Wer hat hier gewohnt?|Who lived here?
Führerin|Es wurde von einem König als Sommerhaus genutzt. Später wurde es ein Museum.|It was used by a king as a summer house. Later it became a museum.
Besucher|Ist das Gebäude im Krieg zerstört worden?|Was the building destroyed in the war?
Führerin|Ja, zum Teil. Nach dem Krieg wurde es wieder aufgebaut.|Yes, partly. After the war it was rebuilt.
Besucher|Und dieses Gemälde? Von wem wurde es gemalt?|And this painting? Who was it painted by?
Führerin|Es wurde von einem berühmten Künstler gemalt und erst 1990 im Keller entdeckt.|It was painted by a famous artist and only discovered in the basement in 1990.
Besucher|Unglaublich! Gut, dass es nicht weggeworfen worden ist.|Incredible! Good thing it wasn't thrown away.""",
        "grammar": ("The passive in the past", """The passive has a past too.

**Präteritum**: **wurde** + Partizip II. This is the usual form in writing, history and the news:
- Das Schloss **wurde** 1750 **gebaut**.
- Die Bilder **wurden** im Keller **gefunden**.
- ich wurde, du wurdest, er wurde, wir wurden, ihr wurdet, sie wurden

**Perfekt**: **ist ... worden**. The passive Perfekt always uses **sein**, and **worden** (not geworden) comes last:
- Das Schloss **ist** im Krieg **zerstört worden**.

Watch out: **geworden** belongs to werden as a normal verb (to become): Er ist Lehrer **geworden**. In the passive it's **worden**: Er ist gefragt **worden**.

Also don't mix up **wurde** (was, became) with **würde** (would) from the Konjunktiv II.""",
                    "Die Mauer wurde 1961 gebaut.=The wall was built in 1961.; Die Mauer wurde 1989 geöffnet.=The wall was opened in 1989.; Die Kirche ist im Krieg zerstört worden.=The church was destroyed in the war.; Das Museum wurde 1902 gegründet.=The museum was founded in 1902."),
        "exercises": """Das Schloss ___ im 18. Jahrhundert gebaut.|wurde|wurden|würde
Die Bilder ___ im Keller gefunden.|wurden|wurde|würden
Die Kirche ist im Krieg zerstört ___.|worden|geworden|wurde
Er ist Arzt ___.|geworden|worden|wurde
Von wem ___ das Bild gemalt?|wurde|wurden|würde
Die Stadt ist im Jahr 1200 gegründet ___.|worden|geworden|werden
Die Mauer ___ 1989 geöffnet.|wurde|würde|wurden""",
    },
    {
        "id": "b1-hausordnung", "level": "B1", "title": "Die Hausordnung", "subtitle": "Living together: the passive with modal verbs",
        "words": """die Hausordnung=house rules; der Nachbar=neighbor (man); die Nachbarin=neighbor (woman);
der Hausmeister=caretaker, janitor; der Vermieter=landlord; der Mieter=tenant; das Treppenhaus=stairwell;
der Keller=basement, cellar; der Lärm=noise; die Ruhe=quiet, peace; die Rücksicht=consideration;
der Hof=courtyard; die Mülltonne=garbage bin; stören=to disturb; erlauben=to allow; verbieten=to forbid;
beachten=to observe, to follow (rules); laut=loud""",
        "dialogue": """Hausmeister|Herr Rossi, haben Sie die Hausordnung schon gelesen?|Mr. Rossi, have you read the house rules yet?
Herr Rossi|Noch nicht ganz. Was muss denn beachtet werden?|Not completely. So what has to be observed?
Hausmeister|Ab 22 Uhr muss die Nachtruhe eingehalten werden. Laute Musik ist dann verboten.|From 10 p.m. the night-time quiet hours have to be respected. Loud music is forbidden then.
Herr Rossi|Und das Treppenhaus? Muss es von den Mietern geputzt werden?|And the stairwell? Does it have to be cleaned by the tenants?
Hausmeister|Ja, jede Woche. Der Plan hängt unten im Flur.|Yes, every week. The schedule hangs downstairs in the hallway.
Herr Rossi|Darf mein Fahrrad im Hof abgestellt werden?|May my bike be left in the courtyard?
Hausmeister|Ja, natürlich. Nur im Treppenhaus darf nichts abgestellt werden.|Yes, of course. But nothing may be left in the stairwell.
Herr Rossi|Alles klar. Ich will ja keine Nachbarn stören.|All right. I certainly don't want to disturb any neighbors.""",
        "grammar": ("The passive with modal verbs", """To say what **must**, **can**, **may** or **should** be done, put the modal verb in second place and **Partizip II + werden** at the end:

- Der Müll **muss** getrennt **werden**. (has to be separated)
- Das Fahrrad **kann** im Hof abgestellt **werden**. (can be left)
- Im Treppenhaus **darf** nicht geraucht **werden**. (no smoking)
- Die Fenster **sollen** geschlossen **werden**. (are to be closed)

The modal verb agrees with the subject: Die Mülltonne **muss** ... Die Mülltonnen **müssen** ...

In a side clause the modal verb goes to the very end: Ich weiß, dass der Keller aufgeräumt werden **muss**.

In the past, use the Präteritum of the modal verb: Die Wohnung **musste** renoviert werden.""",
                    "Das Treppenhaus muss jede Woche geputzt werden.=The stairwell has to be cleaned every week.; Nach 22 Uhr darf keine laute Musik gespielt werden.=No loud music may be played after 10 p.m.; Die Heizung konnte nicht repariert werden.=The heating couldn't be repaired.; Der Hausmeister sagt, dass die Mülltonnen in den Hof gestellt werden sollen.=The caretaker says that the bins are to be put in the courtyard."),
        "exercises": """Der Müll muss getrennt ___.|werden|wird|worden
Im Treppenhaus darf nicht ___ werden.|geraucht|rauchen|raucht
Die Fenster ___ geschlossen werden.|müssen|muss|musst
Die Heizung ___ gestern nicht repariert werden.|konnte|kann|könnt
Ich weiß, dass der Keller aufgeräumt werden ___.|muss|müssen|musst
Kann das Fahrrad im Hof abgestellt ___?|werden|worden|wurde
Die Nachbarn sollen nicht ___ werden.|gestört|stören|stört""",
    },
    {
        "id": "b1-kollegen", "level": "B1", "title": "Kollegen und Kunden", "subtitle": "Work contacts and the n-declension",
        "words": """der Praktikant=intern; der Assistent=assistant; der Experte=expert; der Lieferant=supplier;
der Architekt=architect; der Kandidat=candidate; der Journalist=journalist; der Fotograf=photographer;
der Mensch=person, human being; der Herr=gentleman, Mr.; begrüßen=to greet, to welcome; betreuen=to look after;
beraten=to advise; vertreten=to stand in for; duzen=to call someone du; siezen=to call someone Sie;
höflich=polite""",
        "dialogue": """Frau Berger|Max, kannst du heute den neuen Praktikanten betreuen?|Max, can you look after the new intern today?
Max|Gern. Wie heißt er denn?|Sure. What's his name?
Frau Berger|Jonas Keller. Bitte zeig dem Praktikanten zuerst das Büro und stell ihn den Kollegen vor.|Jonas Keller. Please show the intern the office first and introduce him to the colleagues.
Max|Mache ich. Und um zehn kommt doch der Architekt, oder?|Will do. And the architect is coming at ten, isn't he?
Frau Berger|Genau. Kannst du Herrn Meyer bitte begrüßen und ihm einen Kaffee anbieten?|Exactly. Can you please welcome Mr. Meyer and offer him a coffee?
Max|Klar. Duzen wir den Architekten eigentlich oder siezen wir ihn?|Sure. Do we actually call the architect du or Sie?
Frau Berger|Wir siezen ihn. Er ist ein sehr höflicher Mensch, aber ein bisschen formell.|We call him Sie. He's a very polite person, but a bit formal.""",
        "grammar": ("The n-declension", """A group of **masculine** nouns adds **-n** or **-en** in every case except the nominative singular:

- Nominative: **der** Kollege, **der** Praktikant
- Accusative: **den** Kollege**n**, **den** Praktikant**en**
- Dative: **dem** Kollege**n**, **dem** Praktikant**en**
- Genitive: **des** Kollege**n**, **des** Praktikant**en**
- Plural, all cases: **die** Kollege**n**, **die** Praktikant**en**

Which nouns? Masculine nouns, mostly for people and animals:
- ending in **-e**: der Kollege, der Kunde, der Junge, der Experte
- ending in **-ant, -ent, -ist**: der Praktikant, der Assistent, der Journalist
- ending in **-at, -oge, -graf**: der Kandidat, der Biologe, der Fotograf
- a few others: der **Mensch**, der **Nachbar**, der **Architekt**, der **Herr** (den Herr**n**, plural die Herr**en**)

In letters: Sehr geehrter **Herr** Meyer (nominative), but Ich spreche mit **Herrn** Meyer.""",
                    "Ich frage den Kollegen.=I'll ask the colleague.; Kannst du dem Praktikanten helfen?=Can you help the intern?; Wir warten auf den Lieferanten.=We're waiting for the supplier.; Das ist das Büro des Assistenten.=This is the assistant's office."),
        "exercises": """Ich habe den ___ schon begrüßt.|Kunden|Kunde|Kundes
Kannst du dem ___ das Büro zeigen?|Praktikanten|Praktikant|Praktikante
Das ist unser neuer ___.|Kollege|Kollegen|Kolleges
Ich schreibe eine E-Mail an ___ Meyer.|Herrn|Herr|Herre
Der Chef spricht mit dem ___.|Journalisten|Journalist|Journalists
Das ist das Auto meines ___.|Nachbarn|Nachbar|Nachbares
Er ist ein netter ___.|Mensch|Menschen|Menschs""",
    },
    {
        "id": "b1-streik", "level": "B1", "title": "Streik am Flughafen", "subtitle": "Travel trouble: the genitive and wegen, trotz, während",
        "words": """der Streik=strike; das Unwetter=storm, severe weather; die Baustelle=construction site, roadworks;
der Stau=traffic jam; die Umleitung=detour, diversion; die Entschädigung=compensation;
die Fluggesellschaft=airline; der Passagier=passenger; die Ursache=cause; stornieren=to cancel (a booking);
buchen=to book; erstatten=to refund, to reimburse; wegen=because of; trotz=despite, in spite of;
innerhalb=within; außerhalb=outside of""",
        "dialogue": """Durchsage|Wegen eines Streiks fallen heute alle Flüge nach Hamburg aus.|Because of a strike, all flights to Hamburg are cancelled today.
Frau Kılıç|Entschuldigung, ich habe einen Flug nach Hamburg gebucht. Was soll ich jetzt machen?|Excuse me, I booked a flight to Hamburg. What should I do now?
Mitarbeiter|Trotz des Streiks fahren die Züge. Wir buchen Sie gern auf einen Zug um.|Despite the strike, the trains are running. We'll be glad to rebook you onto a train.
Frau Kılıç|Und bekomme ich eine Entschädigung?|And do I get compensation?
Mitarbeiter|Ja. Innerhalb einer Woche erstattet Ihnen die Fluggesellschaft den Preis des Tickets.|Yes. Within a week the airline will refund you the price of the ticket.
Frau Kılıç|Gut. Kann ich während der Wartezeit irgendwo arbeiten?|Good. Is there somewhere I can work while I wait?
Mitarbeiter|Natürlich. Wegen des Streiks ist die Lounge heute für alle Passagiere geöffnet.|Of course. Because of the strike, the lounge is open to all passengers today.""",
        "grammar": ("The genitive and wegen, trotz, während", """The **genitive** shows that something belongs to someone or something (like English "of" or "'s"). It's used more in writing than in speech.

The article forms:
- masculine: **des** Streik**s**, **eines** Mann**es** (the noun adds -s or -es)
- neuter: **des** Ticket**s**, **eines** Kind**es**
- feminine: **der** Fluggesellschaft, **einer** Woche (no ending on the noun)
- plural: **der** Passagiere

Short nouns of one syllable usually take **-es** (des Mannes, des Zuges), longer ones **-s** (des Flughafens). n-nouns take -n or -en: des Kollegen.

Some prepositions take the genitive:
- **wegen** (because of): **wegen des** Wetters
- **trotz** (despite): **trotz des** Streiks
- **während** (during): **während der** Reise
- **innerhalb, außerhalb** (within, outside of): **innerhalb einer** Woche
- **statt** (instead of): **statt eines** Flugs

In everyday speech you'll often hear wegen and trotz with the dative (wegen dem Wetter). In writing, use the genitive.""",
                    "Wegen des Unwetters hatte der Zug Verspätung.=Because of the storm, the train was delayed.; Trotz des Staus kamen wir pünktlich an.=Despite the traffic jam, we arrived on time.; Während der Fahrt habe ich gelesen.=I read during the journey.; Das ist der Koffer meines Bruders.=This is my brother's suitcase."),
        "exercises": """Wegen ___ Streiks fällt der Flug aus.|des|dem|der
Trotz ___ Regens gehen wir spazieren.|des|den|die
Während ___ Reise habe ich viel gelesen.|der|des|die
Das ist das Auto ___ Nachbarn.|meines|meinem|meinen
Innerhalb ___ Woche bekommen Sie Ihr Geld zurück.|einer|eines|eine
Der Preis des ___ ist gestiegen.|Tickets|Ticket|Tickete
Wegen des ___ kamen wir zu spät.|Staus|Stau|Staue""",
    },
    {
        "id": "b1-gefuehle", "level": "B1", "title": "Gefühle und Beziehungen", "subtitle": "Feelings and relationships: verbs with prepositions",
        "words": """die Beziehung=relationship; die Liebe=love; die Freundschaft=friendship; das Vertrauen=trust;
die Eifersucht=jealousy; der Streit=argument, quarrel; die Hochzeit=wedding; sich verlieben=to fall in love;
sich trennen=to break up, to separate; sich streiten=to argue; sich freuen auf=to look forward to;
sich freuen über=to be happy about; sich ärgern über=to be annoyed about; denken an=to think of;
sich kümmern um=to take care of; warten auf=to wait for; träumen von=to dream of; eifersüchtig=jealous""",
        "dialogue": """Aylin|Du siehst so glücklich aus! Worüber freust du dich?|You look so happy! What are you happy about?
Lea|Über alles! Ich habe mich verliebt.|About everything! I've fallen in love.
Aylin|Wirklich? In wen denn?|Really? Who with?
Lea|In Tim, den Bruder von Jana. Ich denke die ganze Zeit an ihn.|With Tim, Jana's brother. I think about him all the time.
Aylin|Wie schön! Weiß er davon?|How lovely! Does he know about it?
Lea|Ja, wir treffen uns am Samstag. Ich freue mich schon sehr darauf.|Yes, we're meeting on Saturday. I'm really looking forward to it.
Aylin|Und was ist mit Ben? Ärgert er sich nicht darüber?|And what about Ben? Isn't he annoyed about it?
Lea|Wir haben uns doch schon vor Monaten getrennt. Ich habe lange von einer neuen Liebe geträumt.|We broke up months ago, you know. I dreamed of a new love for a long time.""",
        "grammar": ("Verbs with prepositions; da- and wo- words", """Many German verbs go with a fixed preposition, and the preposition decides the case. Learn them as one piece:

- warten **auf** + accusative: Ich warte **auf den** Bus.
- sich freuen **auf** + accusative (something still to come): Ich freue mich **auf das** Wochenende.
- sich freuen **über** + accusative (something that has happened): Ich freue mich **über das** Geschenk.
- denken **an** + accusative: Ich denke oft **an meine** Familie.
- sich kümmern **um** + accusative, träumen **von** + dative, sprechen **mit** + dative

**For things**, replace preposition + noun with **da-** + preposition (with an extra **r** before a vowel):
- Freust du dich auf den Urlaub? Ja, ich freue mich **darauf**.
- Ärgerst du dich über den Lärm? Ja, ich ärgere mich **darüber**.

**To ask about things**, use **wo-** (wor- before a vowel): **Worauf** wartest du? **Worüber** sprecht ihr? **Wovon** träumst du?

**For people**, keep the preposition and use a pronoun: **Auf wen** wartest du? Ich warte **auf ihn**.""",
                    "Ich freue mich auf deinen Besuch.=I'm looking forward to your visit.; Worüber habt ihr euch gestritten?=What did you argue about?; Er kümmert sich um seine kranke Mutter.=He's taking care of his sick mother.; Denkst du an meinen Geburtstag? Ja, ich denke daran.=Will you remember my birthday? Yes, I'll remember it."),
        "exercises": """Ich warte ___ den Bus.|auf|an|für
Sie freut sich ___ das Geschenk.|über|von|mit
Er denkt oft ___ seine Kindheit.|an|von|für
___ wartest du? Auf den Zug?|Worauf|Wofür|Woran
Freust du dich auf die Reise? Ja, ich freue mich sehr ___.|darauf|darüber|davon
Mit ___ hast du gestern telefoniert?|wem|wen|womit
Wir kümmern uns ___ die Kinder.|um|für|an""",
    },
    {
        "id": "b1-stadtland", "level": "B1", "title": "Stadt oder Land?", "subtitle": "Where to live: two-part conjunctions",
        "words": """das Dorf=village; die Großstadt=big city; die Gegend=area, region; der Vorort=suburb; die Natur=nature;
die Landschaft=landscape; die Verbindung=connection, transport link; die Lebensqualität=quality of life;
das Angebot=offer, range on offer; die Nähe=closeness, vicinity; der Vorteil=advantage; der Nachteil=disadvantage;
ruhig=quiet; lebendig=lively; einsam=lonely; günstig=cheap, good value; abwechslungsreich=varied""",
        "dialogue": """Julia|Sollen wir in der Stadt bleiben oder aufs Land ziehen?|Should we stay in the city or move to the countryside?
Marco|Ich weiß nicht. Die Stadt bietet sowohl Kultur als auch gute Jobs.|I don't know. The city offers both culture and good jobs.
Julia|Aber die Mieten sind hier nicht nur hoch, sondern sie steigen auch jedes Jahr.|But the rents here are not only high, they also go up every year.
Marco|Das stimmt. Auf dem Land hätten wir weder Lärm noch Stau.|That's true. In the countryside we'd have neither noise nor traffic jams.
Julia|Dafür gibt es dort oft weder ein Kino noch eine gute Busverbindung.|But then there's often neither a cinema nor a good bus connection there.
Marco|Je länger ich darüber nachdenke, desto besser gefällt mir ein Vorort.|The longer I think about it, the more I like the idea of a suburb.
Julia|Gute Idee. Entweder wir finden etwas Günstiges in der Nähe von München, oder wir bleiben hier.|Good idea. Either we find something affordable near Munich, or we stay here.""",
        "grammar": ("Two-part conjunctions", """Some conjunctions come in two parts and connect two words or two whole clauses:

- **sowohl ... als auch** (both ... and): Ich mag **sowohl** die Stadt **als auch** das Land.
- **nicht nur ... sondern auch** (not only ... but also): Die Wohnung ist **nicht nur** groß, **sondern auch** günstig.
- **weder ... noch** (neither ... nor): Im Dorf gibt es **weder** ein Kino **noch** einen Supermarkt.
- **entweder ... oder** (either ... or): **Entweder** wir ziehen um, **oder** wir renovieren.

**weder ... noch** is already negative: never add nicht or kein.

**je ... desto** (the more ... the more) is special. The **je** part is a side clause with the verb at the end. **desto** is followed directly by the comparative, then the verb:
- **Je** länger ich hier wohne, **desto** besser gefällt es mir.
- **Je** größer die Stadt ist, **desto** teurer sind die Wohnungen.""",
                    "Das Dorf hat sowohl eine Schule als auch einen Arzt.=The village has both a school and a doctor.; Hier gibt es weder Lärm noch Stau.=There's neither noise nor traffic here.; Wir wohnen entweder in der Stadt oder in einem Vorort.=We'll live either in the city or in a suburb.; Je ruhiger die Gegend ist, desto besser schlafe ich.=The quieter the area is, the better I sleep."),
        "exercises": """Ich mag sowohl die Stadt ___ das Land.|als auch|noch|oder
Im Dorf gibt es weder ein Kino ___ ein Theater.|noch|oder|als auch
___ wir ziehen um, oder wir bleiben hier.|Entweder|Weder|Sowohl
Die Wohnung ist nicht nur hell, ___ auch ruhig.|sondern|aber|oder
Je größer die Stadt ist, ___ teurer sind die Mieten.|desto|je|als
Je länger ich hier wohne, desto ___.|besser gefällt es mir|besser es gefällt mir|es gefällt mir besser
Er spricht ___ Deutsch noch Englisch.|weder|entweder|sowohl""",
    },
    {
        "id": "b1-wahl", "level": "B1", "title": "Die Wahl", "subtitle": "Politics and society: Futur I",
        "words": """die Politik=politics; die Wahl=election, choice; wählen=to vote, to choose; die Partei=party (political);
die Regierung=government; das Parlament=parliament; der Bürger=citizen; die Gesellschaft=society;
die Demokratie=democracy; das Gesetz=law; die Steuer=tax; die Meinung=opinion; die Zukunft=future;
die Rente=pension; die Stimme=vote, voice; versprechen=to promise; ändern=to change; sozial=social""",
        "dialogue": """Can|Am Sonntag ist Wahl. Wirst du wählen gehen?|There's an election on Sunday. Are you going to vote?
Emma|Natürlich! Jede Stimme ist wichtig.|Of course! Every vote counts.
Can|Ich darf leider noch nicht wählen. Ich bekomme erst nächstes Jahr den deutschen Pass.|Unfortunately I'm not allowed to vote yet. I won't get my German passport until next year.
Emma|Dann wirst du beim nächsten Mal wählen! Was meinst du, wer wird gewinnen?|Then you'll vote next time! What do you think, who will win?
Can|Ich glaube, die Regierung wird die Mehrheit verlieren. Viele Bürger sind unzufrieden.|I think the government will lose its majority. Many citizens are dissatisfied.
Emma|Alle Parteien versprechen, dass sie die Steuern senken werden.|All the parties promise that they'll lower taxes.
Can|Ob sich wirklich etwas ändern wird? Wir werden sehen.|Will anything really change? We'll see.""",
        "grammar": ("Futur I: werden + infinitive", """For the future, German often just uses the **present** with a time word: Morgen **gehe** ich wählen.

The **Futur I** is used for predictions, promises, firm plans and guesses. Put **werden** in second place and the **infinitive** at the end:
- ich **werde** wählen, du **wirst** wählen, er, sie, es **wird** wählen
- wir **werden** wählen, ihr **werdet** wählen, sie, Sie **werden** wählen

Uses:
- Prediction: Die Partei **wird** die Wahl **gewinnen**.
- Promise: Wir **werden** die Steuern **senken**.
- Guess about now (with wohl, sicher, bestimmt): Er **wird** wohl krank **sein**.

In a side clause, werden goes to the very end: Sie sagen, dass sie die Steuern senken **werden**.

Don't mix up werden + infinitive (future) with werden + Partizip II (passive): Ich **werde** fragen. (I'll ask.) Ich **werde** gefragt. (I'm being asked.)""",
                    "Die Regierung wird ein neues Gesetz beschließen.=The government will pass a new law.; Ich werde nächstes Jahr zum ersten Mal wählen.=I'll vote for the first time next year.; Es wird sich nicht viel ändern.=Not much will change.; Sie wird wohl schon zu Hause sein.=She's probably at home already."),
        "exercises": """Ich ___ am Sonntag wählen.|werde|wird|wirst
Die Partei wird die Wahl ___.|gewinnen|gewinnt|gewonnen
___ du nächstes Jahr in Berlin wohnen?|Wirst|Wird|Werdet
Sie versprechen, dass sie die Steuern senken ___.|werden|wird|werdet
Wir ___ sehen, was passiert.|werden|wird|wurden
Er ist nicht da. Er wird wohl krank ___.|sein|ist|gewesen
Es ___ sich nicht viel ändern.|wird|werden|wirst""",
    },
    {
        "id": "b1-amt", "level": "B1", "title": "Auf dem Amt", "subtitle": "At the authorities: indirect questions",
        "words": """das Amt=public office, authority; die Behörde=government office, authority; der Antrag=application (form), request;
das Formular=form; der Ausweis=ID card; der Reisepass=passport; die Aufenthaltserlaubnis=residence permit;
die Unterschrift=signature; der Wohnsitz=place of residence; die Bescheinigung=certificate (official);
die Frist=deadline; ausfüllen=to fill out; beantragen=to apply for; verlängern=to extend; gültig=valid;
abgeben=to hand in; erforderlich=required""",
        "dialogue": """Herr Petrov|Guten Tag. Können Sie mir sagen, wo ich meine Aufenthaltserlaubnis verlängern kann?|Hello. Can you tell me where I can extend my residence permit?
Sachbearbeiterin|Hier bei mir. Haben Sie das Formular schon ausgefüllt?|Here with me. Have you already filled out the form?
Herr Petrov|Ja. Ich weiß aber nicht, ob ich auch eine Bescheinigung vom Arbeitgeber brauche.|Yes. But I don't know whether I also need a certificate from my employer.
Sachbearbeiterin|Ja, die ist erforderlich. Und Ihren Reisepass brauche ich auch.|Yes, that's required. And I need your passport too.
Herr Petrov|Hier, bitte. Wissen Sie, wie lange die Bearbeitung dauert?|Here you are. Do you know how long the processing takes?
Sachbearbeiterin|Ungefähr vier Wochen. Ihre jetzige Erlaubnis bleibt bis dahin gültig.|About four weeks. Your current permit stays valid until then.
Herr Petrov|Darf ich noch fragen, wann ich die neue Karte abholen kann?|May I also ask when I can pick up the new card?
Sachbearbeiterin|Wir schicken Ihnen einen Brief, sobald sie fertig ist.|We'll send you a letter as soon as it's ready.""",
        "grammar": ("Indirect questions", """An indirect question is a question inside another sentence. It sounds more polite and is very common at offices:

- Direct: **Wo** kann ich den Antrag abgeben?
- Indirect: Können Sie mir sagen, **wo** ich den Antrag abgeben **kann**?

The question word starts a side clause, so the **verb goes to the end**.

**W-questions** keep their question word (wo, wann, wie, was, wer, warum, wie lange ...):
- Ich weiß nicht, **wann** das Amt **öffnet**.

**Yes/no questions** become **ob** clauses (whether, if):
- Brauche ich einen Termin? → Wissen Sie, **ob** ich einen Termin **brauche**?

Useful starters: **Können Sie mir sagen, ...** / **Wissen Sie, ...** / **Ich möchte wissen, ...** / **Ich weiß nicht, ...** / **Darf ich fragen, ...**

The sentence ends with a question mark only when the main part is a question: Wissen Sie, ob ...? but Ich weiß nicht, ob ... .""",
                    "Können Sie mir sagen, wo das Bürgeramt ist?=Can you tell me where the citizens' office is?; Ich weiß nicht, ob mein Pass noch gültig ist.=I don't know whether my passport is still valid.; Wissen Sie, wie lange ich warten muss?=Do you know how long I have to wait?; Darf ich fragen, warum der Antrag abgelehnt wurde?=May I ask why the application was rejected?"),
        "exercises": """Können Sie mir sagen, ___?|wo das Amt ist|wo ist das Amt|wo das Amt sein
Ich weiß nicht, ___ ich einen Termin brauche.|ob|wenn|dass
Wissen Sie, wann die Behörde ___?|öffnet|öffnen|offen
Ich möchte wissen, ___ der Antrag kostet.|wie viel|wer|wo
Darf ich fragen, warum mein Antrag ___?|abgelehnt wurde|wurde abgelehnt|abgelehnt werden
Brauche ich ein Foto? → Wissen Sie, ___ ich ein Foto brauche?|ob|dass|wenn
Ich weiß nicht, wie lange die Bearbeitung ___.|dauert|dauern|dauerst""",
    },
    {
        "id": "b1-wohnungssuche", "level": "B1", "title": "Wohnungssuche", "subtitle": "Finding an apartment: adjective endings",
        "words": """die Anzeige=advertisement, ad; die Kaltmiete=rent without utilities; die Kaution=rental deposit;
der Quadratmeter=square meter; die Besichtigung=viewing; der Balkon=balcony; die Einbauküche=fitted kitchen;
der Stock=floor, story; der Aufzug=elevator, lift; die Heizung=heating; der Mietvertrag=rental agreement;
die Lage=location; möbliert=furnished; renoviert=renovated; zentral=central; gemütlich=cozy;
geräumig=spacious; besichtigen=to view (an apartment)""",
        "dialogue": """Sara|Hör mal: „Helle Wohnung mit großem Balkon in ruhiger Lage.“ Klingt gut, oder?|Listen: "Bright apartment with a big balcony in a quiet location." Sounds good, doesn't it?
Ali|Und was kostet die schöne Wohnung?|And how much does this nice apartment cost?
Sara|900 Euro Kaltmiete. Dafür hat sie eine neue Einbauküche und ein renoviertes Bad.|900 euros rent without utilities. For that it has a new fitted kitchen and a renovated bathroom.
Ali|Hm. In welchem Stock liegt sie?|Hm. Which floor is it on?
Sara|Im vierten Stock, leider ohne Aufzug.|On the fourth floor, unfortunately without an elevator.
Ali|Mit unserem schweren Sofa? Das wird ein langer Umzug!|With our heavy sofa? That'll be a long move!
Sara|Ich rufe trotzdem an und frage nach einem Termin für die Besichtigung.|I'll call anyway and ask for an appointment for a viewing.""",
        "grammar": ("Adjective endings: the full picture", """An adjective before a noun gets an ending. Which one depends on what comes before it.

**After der, die, das** (and dieser, jeder, welcher) the article already shows the case, so the adjective takes only **-e** or **-en**:
- der hell**e** Raum, die hell**e** Küche, das hell**e** Bad
- **-en** in all plurals, in the dative and genitive, and in the masculine accusative: mit dem hell**en** Raum, ich suche den hell**en** Raum

**After ein, kein, mein ...**: where ein has no ending (masculine nominative, neuter nominative and accusative), the adjective shows the gender:
- ein groß**er** Balkon, ein groß**es** Bad, eine groß**e** Küche
- everywhere else it's the same as after der: mit einem groß**en** Balkon

**With no article** the adjective takes the ending der, die or das would have (one exception: masculine and neuter genitive take **-en**, as in trotz schlecht**en** Wetters):
- groß**er** Balkon, groß**e** Küche, groß**es** Bad, mit groß**em** Balkon, in ruhig**er** Lage

The rule behind it all: either the article or the adjective shows gender and case clearly. If the article doesn't, the adjective must.""",
                    "Wir suchen eine helle Wohnung mit großem Balkon.=We're looking for a bright apartment with a big balcony.; Das renovierte Bad gefällt mir sehr.=I really like the renovated bathroom.; Die Wohnung hat einen kleinen Keller.=The apartment has a small cellar.; Wir wohnen in einem alten Haus im dritten Stock.=We live in an old building on the third floor."),
        "exercises": """Wir suchen eine ___ Wohnung.|helle|hellen|heller
Die Wohnung hat einen ___ Balkon.|großen|großer|großes
Ich wohne in einem ___ Haus.|alten|altes|alter
Das ist ein ___ Zimmer.|gemütliches|gemütliche|gemütlichen
Wohnung mit ___ Einbauküche zu vermieten|neuer|neue|neuen
Der ___ Mietvertrag liegt auf dem Tisch.|neue|neuer|neuen
Die Mieter der ___ Wohnungen sind zufrieden.|renovierten|renovierte|renoviertes""",
    },
    {
        "id": "b1-nachrichten", "level": "B1", "title": "Die Nachrichten", "subtitle": "News and media: participles as adjectives",
        "words": """die Schlagzeile=headline; der Artikel=article; der Bericht=report; die Meldung=news item, report;
das Ereignis=event, incident; der Unfall=accident; die Feuerwehr=fire department; die Umfrage=survey, poll;
die Studie=study (research); die Quelle=source; steigen=to rise; sinken=to fall, to sink; berichten=to report;
veröffentlichen=to publish; aktuell=current, up to date; zunehmend=increasingly; verletzt=injured""",
        "dialogue": """Mira|Gibt es etwas Neues in der Zeitung?|Is there anything new in the paper?
Dennis|Hier: „Steigende Mieten: Viele Familien suchen günstigere Wohnungen.“|Here: "Rising rents: many families are looking for cheaper apartments."
Mira|Das ist leider keine überraschende Nachricht.|Unfortunately that's no surprising news.
Dennis|Und hier ist ein Bericht über den gestern gemeldeten Unfall. Zwei verletzte Personen wurden ins Krankenhaus gebracht.|And here's a report on the accident reported yesterday. Two injured people were taken to hospital.
Mira|Wie schrecklich. Steht da auch etwas über den angekündigten Streik?|How terrible. Is there anything about the announced strike too?
Dennis|Ja, der angekündigte Streik findet doch nicht statt.|Yes, the announced strike isn't happening after all.
Mira|Gut! Dann fährt mein Zug morgen. Lies mir doch noch die aktuelle Wettermeldung vor!|Good! Then my train is running tomorrow. Read me the latest weather report too!""",
        "grammar": ("Participles as adjectives", """Both participles can stand before a noun like an adjective, with the usual adjective endings.

**Partizip I** is the infinitive + **d**: steigen → steigen**d**. It describes something happening right now (English -ing):
- die steigend**en** Preise (the rising prices: prices that are rising)
- ein schlafend**es** Kind (a sleeping child)

**Partizip II** describes something that has been done or has happened:
- der gemeldet**e** Unfall (the reported accident: the accident that was reported)
- die verletzt**en** Personen (the injured people)
- ein gut renoviert**es** Haus (a well renovated house)

These forms replace a whole relative clause, which is why newspapers love them:
- die Preise, **die steigen** → die **steigenden** Preise
- der Streik, **der angekündigt wurde** → der **angekündigte** Streik

More words can stand in front of the participle: der **gestern gemeldete** Unfall.""",
                    "Die steigenden Preise sind ein großes Problem.=The rising prices are a big problem.; Die Feuerwehr half den verletzten Personen.=The fire department helped the injured people.; Der gestern veröffentlichte Artikel war sehr kritisch.=The article published yesterday was very critical.; Wir sahen ein lachendes Kind.=We saw a laughing child."),
        "exercises": """die Preise, die steigen → die ___ Preise|steigenden|steigende|gesteigten
der Unfall, der gemeldet wurde → der ___ Unfall|gemeldete|meldende|gemeldeter
Die ___ Personen wurden ins Krankenhaus gebracht.|verletzten|verletzte|verletztes
ein Kind, das schläft → ein ___ Kind|schlafendes|geschlafenes|schlafende
Der gestern ___ Artikel war sehr gut.|veröffentlichte|veröffentlichende|veröffentlicht
Wir sprechen über die ___ Mieten.|steigenden|steigend|steigende
der Streik, der angekündigt wurde → der ___ Streik|angekündigte|ankündigende|angekündigten""",
    },
]
