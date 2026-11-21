"""The reading room's built-in library: 30 short original texts, 10 each at A1, A2 and B1.

Written for this app (no copied text). The grammar follows the level:
- A1: present tense, simple sentences, nominative / accusative and the most common dative phrases.
- A2: Perfekt, modal verbs, dative, simple "weil / dass / wenn" clauses.
- B1: Präteritum for stories, subordinate clauses, Konjunktiv II and the passive.

Each text is one line per paragraph (for dialogues, one line per turn). genre and topic are short English labels
from GENRES / TOPICS so the page can translate them; summaries are given in English and Turkish.
"""

LEVELS = ("A1", "A2", "B1")
GENRES = ("Story", "Dialogue", "Email", "Messages", "Magazine", "Recipe", "Blog", "Forum", "Mystery")
TOPICS = ("Daily life", "Family", "Food", "Housing", "Shopping", "Free time", "Cities", "Animals", "Weather", "Travel",
          "Health", "Work", "Celebrations", "Culture", "Environment", "Art", "Life stories", "Dreams")


def _t(id, level, genre, topic, title, en, tr, text):
    return {"id": id, "level": level, "genre": genre, "topic": topic, "title": title, "summary_en": en,
            "summary_tr": tr, "paragraphs": [p.strip() for p in text.strip().split("\n") if p.strip()]}


TEXTS = [
    # ---------------------------------------------------------------- A1
    _t("a1-mein-tag", "A1", "Story", "Daily life", "Mein Tag",
       "Lena works in a bookshop in Leipzig and describes an ordinary day.",
       "Lena Leipzig'de bir kitapçıda çalışıyor ve sıradan bir gününü anlatıyor.", """
Ich heiße Lena. Ich bin 24 Jahre alt und wohne in Leipzig. Ich arbeite in einer Buchhandlung.
Mein Tag beginnt früh. Um halb sieben klingelt der Wecker. Ich stehe auf, dusche und mache Kaffee. Zum Frühstück esse ich ein Brötchen mit Käse. Dann lese ich die Nachrichten auf dem Handy.
Um acht Uhr fahre ich mit dem Fahrrad zur Arbeit. Die Buchhandlung ist nicht weit. Ich verkaufe Bücher, ich bestelle neue Bücher und ich spreche mit den Kunden. Die Arbeit macht mir Spaß.
Mittags habe ich eine Pause. Ich gehe oft mit meiner Kollegin Sara in ein kleines Restaurant. Wir essen Suppe oder Salat und trinken Wasser.
Um fünf Uhr ist die Arbeit zu Ende. Am Abend koche ich, ich telefoniere mit meiner Mutter oder ich treffe Freunde. Ich lese natürlich auch gern. Um elf Uhr gehe ich ins Bett. Gute Nacht!
"""),
    _t("a1-familie", "A1", "Story", "Family", "Meine Familie",
       "Emre lives in Cologne and introduces his wife, his children, his parents and his sister.",
       "Emre Köln'de yaşıyor; eşini, çocuklarını, anne babasını ve kız kardeşini tanıtıyor.", """
Hallo! Mein Name ist Emre. Ich komme aus der Türkei, aber ich lebe schon lange in Köln. Ich bin verheiratet. Meine Frau heißt Aylin. Sie ist Lehrerin. Ich bin Ingenieur.
Wir haben zwei Kinder: eine Tochter und einen Sohn. Unsere Tochter heißt Defne. Sie ist zehn Jahre alt und geht in die vierte Klasse. Sie spielt gern Fußball. Unser Sohn heißt Can. Er ist erst drei. Er geht in den Kindergarten und malt sehr gern.
Meine Eltern wohnen auch in Köln. Mein Vater ist Rentner. Er kocht jeden Sonntag für die ganze Familie, und meine Mutter backt einen Kuchen. Am Sonntag essen wir alle zusammen. Das ist sehr schön, aber auch sehr laut!
Meine Schwester Elif wohnt in Istanbul. Sie ist Ärztin. Wir telefonieren jede Woche. Im Sommer besuchen wir sie. Die Kinder freuen sich schon.
"""),
    _t("a1-im-cafe", "A1", "Dialogue", "Food", "Im Café",
       "Mr and Mrs Braun order drinks and a piece of cake in a café, then pay.",
       "Braun çifti bir kafede içecek ve bir dilim pasta sipariş ediyor, sonra hesabı ödüyor.", """
Kellnerin: Guten Tag! Was möchten Sie trinken?
Herr Braun: Guten Tag! Ich hätte gern einen Kaffee, bitte.
Frau Braun: Und ich nehme einen Tee mit Zitrone.
Kellnerin: Gern. Möchten Sie auch etwas essen? Wir haben heute Apfelkuchen und Käsekuchen.
Herr Braun: Ist der Apfelkuchen frisch?
Kellnerin: Ja, natürlich. Er ist von heute Morgen.
Herr Braun: Dann nehme ich ein Stück Apfelkuchen mit Sahne.
Frau Braun: Für mich bitte nur ein Wasser. Ich habe keinen Hunger.
Kellnerin: Also, einen Kaffee, einen Tee mit Zitrone, ein Stück Apfelkuchen mit Sahne und ein Wasser. Mit Kohlensäure oder ohne?
Frau Braun: Ohne, bitte.
Herr Braun: Entschuldigung! Wir möchten bitte bezahlen.
Kellnerin: Zusammen oder getrennt?
Herr Braun: Zusammen, bitte.
Kellnerin: Das macht zwölf Euro achtzig.
Herr Braun: Hier sind vierzehn Euro. Stimmt so.
Kellnerin: Vielen Dank! Einen schönen Tag noch!
Frau Braun: Danke, Ihnen auch. Auf Wiedersehen!
"""),
    _t("a1-neue-wohnung", "A1", "Email", "Housing", "Meine neue Wohnung",
       "In an email to her friend Julia, Mia describes her new flat and invites her to a party.",
       "Mia, arkadaşı Julia'ya yazdığı e-postada yeni dairesini anlatıyor ve onu bir partiye davet ediyor.", """
Liebe Julia,
wie geht es dir? Mir geht es sehr gut, denn ich habe endlich eine neue Wohnung! Sie ist in der Gartenstraße 12, in der Nähe vom Bahnhof.
Die Wohnung hat zwei Zimmer, eine Küche, ein Bad und einen kleinen Balkon. Das Wohnzimmer ist groß und hell. Dort stehen ein Sofa, ein Tisch und ein Regal. Das Schlafzimmer ist klein, aber gemütlich. Die Küche ist neu. Leider habe ich noch keinen Kühlschrank.
Die Miete ist nicht billig, aber okay. Ich bezahle 650 Euro im Monat. Die Nachbarn sind sehr nett. Unter mir wohnt eine alte Frau mit einem Hund.
Am Samstag mache ich eine kleine Party. Hast du Zeit? Die Party beginnt um sieben Uhr. Ich koche Nudeln und mache einen Salat. Bring bitte gute Laune mit!
Viele Grüße
deine Mia
"""),
    _t("a1-markt", "A1", "Dialogue", "Shopping", "Auf dem Markt",
       "Mr Schulz buys tomatoes, cucumbers and apples at the Saturday market.",
       "Bay Schulz cumartesi pazarında domates, salatalık ve elma alıyor.", """
Es ist Samstag. Herr Schulz geht auf den Markt. Er kauft gern frisches Obst und Gemüse.
Verkäuferin: Guten Morgen! Was darf es sein?
Herr Schulz: Guten Morgen! Ich brauche ein Kilo Tomaten und zwei Gurken.
Verkäuferin: Bitte schön. Sonst noch etwas?
Herr Schulz: Was kosten die Äpfel?
Verkäuferin: Ein Kilo kostet drei Euro. Die Äpfel kommen hier aus der Region. Sie sind sehr süß. Möchten Sie einen probieren?
Herr Schulz: Ja, gern. Mmh, die sind wirklich lecker! Dann nehme ich zwei Kilo.
Verkäuferin: Haben Sie eine Tasche?
Herr Schulz: Ja, ich habe eine Tasche dabei. Ich brauche keine Plastiktüte.
Verkäuferin: Sehr gut! Brauchen Sie noch Kartoffeln oder Zwiebeln?
Herr Schulz: Nein, danke. Kartoffeln habe ich noch zu Hause. Was macht das zusammen?
Verkäuferin: Das macht elf Euro fünfzig.
Herr Schulz: Bitte schön.
Verkäuferin: Danke schön. Schönes Wochenende!
Herr Schulz geht zufrieden nach Hause. Heute Abend kocht er eine Gemüsesuppe.
"""),
    _t("a1-wochenende", "A1", "Messages", "Free time", "Pläne fürs Wochenende",
       "Tom and Nina text each other and plan pizza and a film for Saturday.",
       "Tom ve Nina mesajlaşıyor ve cumartesi için pizza ve sinema planlıyor.", """
Tom: Hallo Nina! Was machst du am Wochenende?
Nina: Hi Tom! Am Samstag arbeite ich bis zwei Uhr. Danach habe ich Zeit. Warum?
Tom: Ich möchte am Samstag ins Kino gehen. Es gibt eine neue Komödie. Kommst du mit?
Nina: Gern! Wann beginnt der Film?
Tom: Um acht Uhr. Wir können vorher etwas essen. Kennst du die Pizzeria am Marktplatz?
Nina: Ja, die ist super! Treffen wir uns um sechs Uhr dort?
Tom: Perfekt. Und am Sonntag? Hast du am Sonntag auch Zeit?
Nina: Am Sonntag besuche ich meine Oma. Sie hat Geburtstag. Sie wird achtzig!
Tom: Oh, toll! Herzlichen Glückwunsch an deine Oma!
Nina: Danke! Und du? Was machst du am Sonntag?
Tom: Ich gehe vielleicht schwimmen. Oder ich bleibe einfach zu Hause und schlafe lange.
Nina: Das klingt auch gut. Also, bis Samstag!
Tom: Bis Samstag! Ich kaufe die Kinokarten online.
"""),
    _t("a1-berlin", "A1", "Magazine", "Cities", "Berlin",
       "A short portrait of Berlin: sights, parks, many languages and the Currywurst.",
       "Berlin'in kısa bir portresi: görülecek yerler, parklar, birçok dil ve Currywurst.", """
Berlin ist die Hauptstadt von Deutschland. Hier leben fast vier Millionen Menschen. Keine Stadt in Deutschland ist so groß.
Berlin ist alt, aber auch sehr modern. Viele Touristen besuchen jedes Jahr die Stadt. Sie sehen das Brandenburger Tor, den Reichstag und den Fernsehturm. Der Fernsehturm ist 368 Meter hoch. Von oben sieht man die ganze Stadt.
In Berlin gibt es viele Museen, Theater und Clubs. Es gibt auch viele Parks und Seen. Im Sommer schwimmen die Berliner gern im See, oder sie sitzen im Park und machen ein Picknick.
Die Menschen in Berlin kommen aus der ganzen Welt. Man hört auf der Straße viele Sprachen: Deutsch, Englisch, Türkisch, Arabisch, Polnisch und viele mehr. Es gibt auch sehr viele Restaurants. Hier kann man Essen aus vielen Ländern probieren. Ein typisches Essen in Berlin ist die Currywurst. Auch der Döner ist sehr beliebt.
Die Stadt ist groß. Man fährt am besten mit der U-Bahn, mit der S-Bahn oder mit dem Bus. Viele Berliner fahren auch mit dem Fahrrad.
"""),
    _t("a1-minka", "A1", "Story", "Animals", "Wo ist Minka?",
       "Mrs Wagner's cat has disappeared. She and her neighbour search everywhere, but the cat is somewhere surprising.",
       "Bayan Wagner'in kedisi kaybolmuş. Komşusuyla her yeri arıyorlar ama kedi hiç beklenmedik bir yerde.", """
Frau Wagner hat eine Katze. Die Katze heißt Minka. Sie ist schwarz und weiß und sehr neugierig.
Heute Morgen ist Minka nicht da. Frau Wagner sucht die Katze in der Küche, im Wohnzimmer und im Schlafzimmer. Sie sucht sie auch unter dem Bett und hinter dem Sofa. Aber Minka ist nicht da.
Frau Wagner geht in den Garten. „Minka! Minka!“, ruft sie. Keine Antwort. Jetzt ist Frau Wagner sehr nervös.
Sie klingelt bei ihrem Nachbarn. Herr Krüger öffnet die Tür. „Guten Morgen, Herr Krüger. Ist meine Katze vielleicht bei Ihnen?“
„Nein, leider nicht“, sagt Herr Krüger. „Aber ich helfe Ihnen. Wir suchen zusammen.“
Sie suchen auf der Straße und im Park. Sie fragen die Kinder auf dem Spielplatz. Niemand weiß etwas.
Am Mittag kommt Frau Wagner traurig nach Hause. Sie macht den Kleiderschrank auf und sucht eine Jacke. Und da liegt Minka! Sie schläft auf einem Pullover.
Frau Wagner lacht. „Du bist wirklich eine verrückte Katze!“ Minka öffnet die Augen, gähnt und schläft weiter.
"""),
    _t("a1-jahreszeiten", "A1", "Magazine", "Weather", "Vier Jahreszeiten",
       "What spring, summer, autumn and winter are like in Germany.",
       "Almanya'da ilkbahar, yaz, sonbahar ve kışın nasıl geçtiği.", """
In Deutschland gibt es vier Jahreszeiten: Frühling, Sommer, Herbst und Winter. Jede Jahreszeit ist anders.
Im Frühling wird es wärmer. Die Tage sind wieder länger, und die Bäume sind grün. Es regnet oft, aber manchmal scheint auch die Sonne. Viele Menschen arbeiten jetzt im Garten.
Im Sommer ist es warm, manchmal auch heiß. Es ist lange hell, oft bis zehn Uhr abends. Die Kinder haben Ferien. Viele Familien fahren in den Urlaub, zum Beispiel ans Meer oder in die Berge.
Im Herbst ist es kühl und oft windig. Die Blätter sind gelb, rot und braun. Es gibt viele Äpfel und Kürbisse. Am Morgen ist es oft neblig.
Im Winter ist es kalt. Manchmal schneit es, aber nicht jedes Jahr. Es wird früh dunkel, schon um vier oder fünf Uhr. Im Dezember gibt es Weihnachtsmärkte. Dort trinken die Leute Glühwein oder Kinderpunsch und essen Lebkuchen.
Und Sie? Welche Jahreszeit mögen Sie am liebsten?
"""),
    _t("a1-pfannkuchen", "A1", "Recipe", "Food", "Pfannkuchen",
       "A simple recipe for German pancakes, sweet or savoury.",
       "Tatlı ya da tuzlu yenebilen Alman krepi (Pfannkuchen) için basit bir tarif.", """
Pfannkuchen sind einfach und lecker. In Deutschland isst man sie oft zum Mittagessen oder am Nachmittag. Kinder lieben Pfannkuchen!
Für vier Pfannkuchen brauchen Sie:
200 Gramm Mehl
2 Eier
300 Milliliter Milch
eine Prise Salz
etwas Butter für die Pfanne
So geht es:
Geben Sie das Mehl, die Eier und die Milch in eine Schüssel. Nehmen Sie auch eine Prise Salz. Rühren Sie alles gut. Jetzt ist der Teig glatt und flüssig. Warten Sie zehn Minuten.
Machen Sie die Pfanne heiß und geben Sie ein bisschen Butter hinein. Geben Sie dann etwas Teig in die Pfanne. Nach ein bis zwei Minuten drehen Sie den Pfannkuchen um. Die andere Seite braucht auch etwa eine Minute. Der Pfannkuchen ist jetzt goldbraun.
Was essen Sie zu den Pfannkuchen? Das ist Geschmackssache. Viele Leute essen sie süß, mit Zucker, Marmelade oder Apfelmus. Andere essen sie lieber herzhaft, mit Käse und Schinken oder mit Spinat.
Guten Appetit!
"""),

    # ---------------------------------------------------------------- A2
    _t("a2-ostsee", "A2", "Email", "Travel", "Urlaub an der Ostsee",
       "Clara writes to Ben from her family holiday on the Baltic coast: beach, rain, a bike tour and fish sandwiches.",
       "Clara, ailesiyle Baltık kıyısındaki tatilinden Ben'e yazıyor: plaj, yağmur, bisiklet turu ve balık ekmek.", """
Hallo Ben,
viele Grüße von der Ostsee! Ich bin jetzt seit einer Woche mit meiner Familie in Warnemünde. Das ist ein kleiner Ort in der Nähe von Rostock. Du musst ja diesen Sommer leider arbeiten, deshalb schreibe ich dir ein bisschen von unserem Urlaub.
Wir sind am Samstag mit dem Zug gekommen. Die Fahrt hat sechs Stunden gedauert, weil wir in Hamburg umsteigen mussten. Unsere Ferienwohnung liegt direkt am Strand. Vom Balkon können wir das Meer sehen!
Am Sonntag war das Wetter super. Wir haben den ganzen Tag am Strand gelegen und sind im Meer geschwommen. Das Wasser war ziemlich kalt, aber das hat den Kindern nichts ausgemacht. Am Montag hat es dann den ganzen Tag geregnet. Wir haben ein Museum in Rostock besucht und danach in einer gemütlichen Bäckerei Kuchen gegessen.
Gestern haben wir Fahrräder gemietet und sind an der Küste entlanggefahren. Wir sind fast vierzig Kilometer gefahren! Am Abend haben wir frischen Fisch gegessen. Mein Sohn hat zum ersten Mal ein Fischbrötchen probiert, und es hat ihm sehr gut geschmeckt.
Morgen wollen wir mit der Fähre nach Dänemark fahren. Darauf freue ich mich schon sehr. Am Sonntag fahren wir leider schon wieder nach Hause.
Und wie geht es dir? Hast du viel Arbeit? Wir können uns nach dem Urlaub mal treffen. Dann zeige ich dir die Fotos.
Liebe Grüße
deine Clara
"""),
    _t("a2-arzt", "A2", "Dialogue", "Health", "Beim Arzt",
       "Mr Demir has a sore throat and a fever. The doctor examines him and tells him what to do.",
       "Bay Demir'in boğazı ağrıyor ve ateşi var. Doktor onu muayene ediyor ve ne yapması gerektiğini söylüyor.", """
Ärztin: Guten Morgen, Herr Demir. Bitte setzen Sie sich. Was fehlt Ihnen denn?
Herr Demir: Guten Morgen, Frau Doktor. Seit drei Tagen habe ich Halsschmerzen und Kopfschmerzen. Gestern Abend habe ich auch Fieber bekommen.
Ärztin: Wie hoch war das Fieber?
Herr Demir: Ich habe es gemessen: 38,5 Grad.
Ärztin: Haben Sie auch Husten?
Herr Demir: Ja, ein bisschen. Und ich bin sehr müde. Ich habe in der Nacht schlecht geschlafen.
Ärztin: Haben Sie schon Medikamente genommen?
Herr Demir: Nur eine Tablette gegen die Kopfschmerzen. Aber sie hat nicht viel geholfen.
Ärztin: Gut, dann möchte ich Sie kurz untersuchen. Machen Sie bitte den Mund weit auf. Ihr Hals ist ziemlich rot. Jetzt höre ich noch die Lunge ab. Atmen Sie bitte tief ein und aus. So, die Lunge ist in Ordnung.
Herr Demir: Was habe ich denn?
Ärztin: Sie haben eine starke Erkältung. Das ist zum Glück keine Grippe.
Herr Demir: Muss ich Antibiotika nehmen?
Ärztin: Nein, die brauchen Sie nicht. Antibiotika helfen nicht gegen Viren. Sie müssen viel trinken, am besten Tee mit Honig. Und Sie sollen sich ausruhen. Ich schreibe Ihnen ein Rezept für ein Spray gegen die Halsschmerzen.
Herr Demir: Darf ich morgen wieder arbeiten?
Ärztin: Nein, auf keinen Fall. Sie bleiben bis Freitag zu Hause. Ich schreibe Sie krank. Ihre Krankenkasse bekommt die Krankmeldung direkt von uns.
Herr Demir: Vielen Dank. Und wenn das Fieber nicht besser wird?
Ärztin: Dann kommen Sie bitte am Donnerstag noch einmal in die Praxis. Gute Besserung, Herr Demir!
Herr Demir: Danke, auf Wiedersehen!
"""),
    _t("a2-umzug", "A2", "Story", "Housing", "Der Umzug",
       "The Hoffmann family moves from a small flat into a house with a garden, and the sofa won't fit through the door.",
       "Hoffmann ailesi küçük bir daireden bahçeli bir eve taşınıyor; kanepe ise kapıdan sığmıyor.", """
Letzten Monat ist Familie Hoffmann umgezogen. Vorher haben sie in einer kleinen Wohnung in der Stadt gewohnt. Die Wohnung hatte nur drei Zimmer, und die Kinder mussten sich ein Zimmer teilen. Jetzt wohnen sie in einem Haus mit Garten am Stadtrand.
Der Umzug war viel Arbeit. Zwei Wochen lang haben die Hoffmanns Kartons gepackt. Herr Hoffmann hat die Bücher eingepackt, Frau Hoffmann hat sich um die Küche gekümmert, und die Kinder haben ihre Spielsachen in Kisten gelegt. Die alten Möbel haben sie verkauft oder verschenkt.
Am Samstag ist der Umzugswagen gekommen. Zum Glück haben viele Freunde geholfen. Sie haben die schweren Schränke getragen und die Kartons in den Wagen gestellt. Um zwölf Uhr war der Wagen voll. Mittags hat Frau Hoffmann Pizza für alle bestellt.
Im neuen Haus gab es dann ein Problem: Das große Sofa hat nicht durch die Tür gepasst! Die Männer haben es zuerst gerade und dann schräg versucht. Am Ende haben sie es durch die Terrassentür ins Wohnzimmer gebracht.
Am Abend waren alle müde, aber glücklich. Die Kinder sind sofort in den Garten gelaufen. Jetzt hat jedes Kind ein eigenes Zimmer. Lukas hat sein Zimmer inzwischen blau gestrichen, und seine Schwester Emma hat ihr Bett ans Fenster gestellt.
Nur eine Sache fehlt noch: Die Hoffmanns kennen ihre Nachbarn noch nicht. Deshalb wollen sie nächste Woche ein kleines Fest im Garten machen und alle Nachbarn einladen.
"""),
    _t("a2-arbeitstag", "A2", "Blog", "Work", "Mein erster Arbeitstag",
       "A graphic designer writes about her nervous, busy and happy first day at a new agency in Frankfurt.",
       "Bir grafik tasarımcı, Frankfurt'taki yeni ajansta heyecanlı, yoğun ve mutlu geçen ilk iş gününü anlatıyor.", """
Gestern war mein erster Arbeitstag in der neuen Firma. Ich arbeite jetzt als Grafikdesignerin in einer Werbeagentur in Frankfurt. Ich war sehr nervös und habe in der Nacht kaum geschlafen.
Ich bin früh aufgestanden, weil ich auf keinen Fall zu spät kommen wollte. Ich habe meine beste Bluse angezogen und bin mit der S-Bahn in die Stadt gefahren. Um Viertel vor neun war ich schon da, eine Viertelstunde zu früh.
Am Empfang hat mich meine neue Chefin, Frau Lange, begrüßt. Sie ist sehr freundlich und hat mir zuerst das Büro gezeigt. Dann hat sie mich den Kolleginnen und Kollegen vorgestellt. Alle haben „du“ zu mir gesagt. Das war am Anfang ein bisschen komisch, denn in meiner alten Firma haben wir „Sie“ gesagt.
Mein Kollege Jonas hat mir dann den Computer und die Programme erklärt. Ich musste viele Formulare ausfüllen und habe einen Ausweis für die Tür bekommen. Mittags sind wir alle zusammen in die Kantine gegangen. Das Essen war gut und nicht teuer.
Am Nachmittag habe ich schon meine erste Aufgabe bekommen: ein Plakat für ein Konzert. Ich habe zwei Entwürfe gemacht und sie Frau Lange gezeigt. Sie hat gesagt, dass ihr der zweite Entwurf sehr gut gefällt. Da war ich wirklich froh!
Um fünf Uhr bin ich nach Hause gefahren. Ich war total müde, aber auch sehr zufrieden. Ich glaube, ich habe die richtige Stelle gefunden. Heute ist mein zweiter Tag. Mal sehen, was kommt!
"""),
    _t("a2-wg", "A2", "Magazine", "Housing", "Leben in einer WG",
       "Why so many people in Germany share a flat, how you find a room, and who cleans the bathroom.",
       "Almanya'da neden bu kadar çok insanın ortak evde yaşadığı, nasıl oda bulunduğu ve banyoyu kimin temizlediği.", """
In Deutschland wohnen viele junge Leute in einer Wohngemeinschaft, kurz WG. In einer WG hat jede Person ein eigenes Zimmer. Die Küche, das Bad und manchmal auch das Wohnzimmer teilen alle zusammen.
Besonders Studentinnen und Studenten leben gern in einer WG. Der wichtigste Grund ist das Geld: Die Mieten in Städten wie München, Hamburg oder Berlin sind sehr hoch. Ein Zimmer in einer WG ist meistens billiger als eine eigene Wohnung. Aber es geht nicht nur ums Geld. Viele Leute wollen nicht allein wohnen. In einer WG ist man selten einsam: Man kann zusammen kochen, Filme sehen oder am Wochenende feiern.
Wie findet man ein WG-Zimmer? Meistens sucht man im Internet. Wenn ein Zimmer frei ist, lädt die WG oft mehrere Leute zu einem „WG-Casting“ ein. Die Bewohner wollen die neue Person kennenlernen. Sie stellen Fragen: Was studierst du? Kochst du gern? Bist du ordentlich? Danach entscheiden sie zusammen.
Natürlich gibt es in einer WG auch Probleme. Wer putzt das Bad? Wer bringt den Müll raus? Warum steht schon wieder schmutziges Geschirr in der Spüle? Deshalb haben viele WGs einen Putzplan. Auf dem Plan steht, wer in welcher Woche putzen muss.
Heute ziehen manchmal auch ältere Menschen in eine WG. Sie wollen im Alter nicht allein sein und sich gegenseitig helfen. Für viele ist die WG also mehr als eine billige Wohnung. Sie ist eine kleine Familie.
"""),
    _t("a2-opa", "A2", "Story", "Celebrations", "Eine Überraschung für Opa",
       "For Grandpa Heinz's 80th birthday, his family secretly plans a party with old photos and a song.",
       "Ailesi, Dede Heinz'ın 80. doğum günü için eski fotoğraflar ve bir şarkıyla gizlice bir parti hazırlıyor.", """
Letzten Sonntag ist Opa Heinz achtzig Jahre alt geworden. Seine Familie wollte ihm eine besondere Freude machen und hat eine Überraschungsparty geplant.
Die Vorbereitungen haben schon vier Wochen vorher begonnen. Seine Tochter Sabine hat einen Raum in einem Restaurant reserviert. Sein Enkel Max hat alte Fotos gesammelt und daraus ein Fotobuch gemacht. Die Enkelin Lea hat mit ihren Cousins ein Lied geübt. Und alle mussten ein Geheimnis bewahren. Das war am schwierigsten!
Am Sonntag hat Sabine ihren Vater zu Hause abgeholt. Sie hat ihm gesagt: „Wir gehen heute zu zweit essen.“ Opa Heinz hat sich gefreut und seinen besten Anzug angezogen.
Als sie ins Restaurant gekommen sind, war es im Raum ganz dunkel. Dann ist plötzlich das Licht angegangen, und dreißig Leute haben gerufen: „Überraschung! Alles Gute zum Geburtstag!“ Opa Heinz konnte zuerst gar nichts sagen. Dann hat er gelacht und alle umarmt. Sogar sein alter Freund Walter war da. Er ist extra aus Österreich gekommen.
Nach dem Essen haben die Enkelkinder ihr Lied gesungen. Dann hat Max seinem Opa das Fotobuch gegeben. Auf den Fotos war Opa als kleiner Junge, als junger Mann bei seiner Hochzeit und als stolzer Vater. Opa hat jedes Bild lange angesehen und zu jedem Foto eine Geschichte erzählt.
Die Party hat bis spät in die Nacht gedauert. Auf dem Heimweg hat Opa Heinz gesagt: „Das war der schönste Geburtstag in meinem Leben. Aber nächstes Jahr feiern wir wieder ganz ruhig, ja?“
"""),
    _t("a2-verspaetung", "A2", "Messages", "Travel", "Der Zug hat Verspätung",
       "Aylin's train is late and she will miss her connection, so her friend Markus offers to pick her up.",
       "Aylin'in treni rötarlı ve aktarmayı kaçıracak; arkadaşı Markus onu almaya gelmeyi teklif ediyor.", """
Aylin: Hallo Markus, ich sitze im Zug nach Köln. Leider haben wir schon dreißig Minuten Verspätung.
Markus: Oh nein! Was ist denn passiert?
Aylin: Es gab eine Störung an einem Signal. Der Zug musste lange vor Frankfurt warten. Jetzt fahren wir wieder, aber sehr langsam.
Markus: Typisch Bahn! Schaffst du deinen Anschlusszug in Köln?
Aylin: Ich glaube nicht. Der Anschlusszug fährt um 14:12 Uhr ab, und wir kommen erst um 14:30 Uhr an. Ich habe schon in der App nachgesehen. Der nächste Zug nach Aachen fährt eine Stunde später.
Markus: Kein Problem. Ich kann dich auch mit dem Auto in Köln abholen. Ich muss heute sowieso nicht mehr arbeiten.
Aylin: Echt? Das ist total lieb von dir! Aber ist das nicht zu weit?
Markus: Nein, das sind nur siebzig Kilometer. Ich habe Zeit und fahre gern.
Aylin: Danke! Dann kann ich dir unterwegs von meinem Wochenende in Frankfurt erzählen. Ich habe so viel erlebt!
Markus: Gern! Schreib mir einfach, wenn du in Köln angekommen bist. Ich warte vor dem Bahnhof, am Ausgang zum Dom.
Aylin: Mache ich. Ach, und eine gute Nachricht: Wenn ein Zug mehr als eine Stunde Verspätung hat, bekommt man einen Teil vom Geld zurück.
Markus: Dann musst du hoffen, dass der Zug noch langsamer fährt!
Aylin: Haha, sehr witzig. Ich möchte einfach nur ankommen!
Aylin: So, ich bin jetzt in Köln. Am Ende hatten wir fünfundvierzig Minuten Verspätung. Wo bist du?
Markus: Ich stehe direkt vor dem Dom. Ich sehe dich schon! Ich winke.
"""),
    _t("a2-hamburg", "A2", "Blog", "Cities", "Ein Wochenende in Hamburg",
       "A travel blog about a weekend in Hamburg: the Speicherstadt, the Elbphilharmonie, the harbour and the fish market.",
       "Hamburg'da geçen bir hafta sonu hakkında gezi blogu: Speicherstadt, Elbphilharmonie, liman ve balık pazarı.", """
Letztes Wochenende habe ich zum ersten Mal Hamburg besucht. Ich wollte diese Stadt im Norden schon lange sehen. Hamburg ist nach Berlin die zweitgrößte Stadt in Deutschland und hat einen der größten Häfen in Europa.
Am Freitagabend bin ich mit dem Zug angekommen. Mein Hotel war nicht weit vom Hafen. Ich habe nur noch eine Kleinigkeit gegessen und bin früh ins Bett gegangen.
Am Samstag habe ich zuerst die Speicherstadt besucht. Dort stehen alte Lagerhäuser aus rotem Backstein direkt am Wasser. Früher hat man dort Kaffee, Tee und Gewürze gelagert. Danach bin ich zur Elbphilharmonie gegangen. Das moderne Konzerthaus sieht aus wie eine große Welle aus Glas. Von der Plaza, einer Terrasse in 37 Metern Höhe, hat man einen tollen Blick über den Hafen. Am Nachmittag habe ich eine Hafenrundfahrt gemacht. Das Boot ist ganz nah an den riesigen Containerschiffen vorbeigefahren.
Am Sonntag musste ich sehr früh aufstehen, denn der berühmte Fischmarkt ist nur am Sonntagmorgen geöffnet. Um sieben Uhr war es dort schon voll und laut. Die Händler haben laut gerufen und ihre Waren angeboten: Fisch, Obst, Blumen und sogar Pflanzen. Ich habe ein Fischbrötchen zum Frühstück gegessen, um sieben Uhr morgens!
Danach bin ich um die Außenalster spaziert. Das ist ein großer See mitten in der Stadt. Leider hat es am Nachmittag angefangen zu regnen. Aber das ist in Hamburg ganz normal, haben mir die Hamburger gesagt.
Am Abend bin ich müde, aber glücklich nach Hause gefahren. Ich komme bestimmt wieder!
"""),
    _t("a2-muell", "A2", "Magazine", "Environment", "Mülltrennung: Welche Tonne?",
       "Which bin is for what in Germany, where the glass goes, and how the bottle deposit works.",
       "Almanya'da hangi çöp kutusunun neye ait olduğu, camın nereye atıldığı ve şişe depozitosunun nasıl işlediği.", """
In Deutschland trennen die meisten Menschen ihren Müll. Für Besucher aus anderen Ländern ist das am Anfang oft kompliziert, denn es gibt viele verschiedene Tonnen. Die Farben können von Stadt zu Stadt ein bisschen anders sein, aber meistens funktioniert es so:
In die blaue Tonne kommt Papier: Zeitungen, Zeitschriften und Kartons. In die gelbe Tonne oder in den gelben Sack kommen Verpackungen aus Plastik und Metall, zum Beispiel Joghurtbecher, Dosen oder Folie. In die braune Tonne kommen Bioabfälle: Reste von Obst und Gemüse, Kaffeesatz oder Teebeutel. Alles andere kommt in die schwarze oder graue Tonne, den Restmüll.
Und was macht man mit Glas? Flaschen und Gläser bringt man zum Glascontainer. Dort muss man sie nach Farben trennen: Weißglas, Grünglas und Braunglas. Aber Vorsicht: Man soll am Sonntag oder spät am Abend kein Glas einwerfen, weil das zu laut für die Nachbarn ist.
Viele Flaschen muss man gar nicht wegwerfen. Auf vielen Flaschen und Dosen gibt es Pfand. Das heißt: Beim Kauf zahlt man zum Beispiel 25 Cent extra. Wenn man die leere Flasche in den Supermarkt zurückbringt, bekommt man das Geld wieder.
Manche Leute finden die Mülltrennung anstrengend. Aber sie hat einen Sinn: Aus altem Papier kann man neues Papier machen, und aus Bioabfällen wird Kompost. So produziert man weniger Müll und schützt die Umwelt.
Übrigens: Wenn Sie den Müll falsch trennen, schreibt Ihnen vielleicht ein Nachbar einen freundlichen oder auch nicht so freundlichen Brief!
"""),
    _t("a2-flohmarkt", "A2", "Story", "Shopping", "Auf dem Flohmarkt",
       "Two friends go to the flea market: one haggles for records, the other finds a lamp with a story.",
       "İki arkadaş bit pazarına gidiyor: biri plaklar için pazarlık ediyor, diğeri hikâyesi olan bir lamba buluyor.", """
Jeden ersten Samstag im Monat gibt es in unserer Stadt einen großen Flohmarkt. Letzten Samstag bin ich mit meiner Freundin Paula hingegangen. Paula sammelt alte Schallplatten, und ich suche schon lange eine schöne Lampe für mein Wohnzimmer.
Wir sind schon um acht Uhr losgegangen, denn morgens findet man die besten Sachen. Auf dem Flohmarkt waren schon viele Leute. An über hundert Ständen haben die Leute alles Mögliche verkauft: Kleidung, Bücher, Geschirr, Spielzeug, alte Fotos und Möbel.
Paula hat schnell einen Stand mit Schallplatten gefunden. Sie hat eine Stunde lang gesucht und am Ende fünf Platten gekauft. Der Verkäufer wollte zuerst dreißig Euro, aber Paula hat gehandelt. Am Ende hat sie nur zwanzig Euro bezahlt. Auf dem Flohmarkt darf man nämlich handeln. Das gehört dazu!
Ich hatte weniger Glück. Ich habe viele Lampen gesehen, aber keine hat mir richtig gefallen. Die eine war zu groß, die andere zu teuer, und die dritte hat nicht funktioniert.
Kurz vor dem Ende haben wir einen kleinen Stand mit einer alten Dame entdeckt. Sie hat Sachen aus ihrem Keller verkauft. Und da stand sie: eine wunderschöne grüne Lampe aus den Siebzigerjahren! „Die Lampe hat meinem Mann gehört“, hat die Dame erzählt. „Er hat jeden Abend unter dieser Lampe gelesen.“ Sie wollte nur zehn Euro dafür haben.
Ich habe die Lampe sofort gekauft. Jetzt steht sie neben meinem Sofa, und jeden Abend lese ich unter ihr ein Buch. Dann denke ich oft an die alte Dame und ihren Mann.
"""),

    # ---------------------------------------------------------------- B1
    _t("b1-bild-1", "B1", "Mystery", "Art", "Das verschwundene Bild (1)",
       "Part 1 of a mystery: the most famous painting in a small-town museum is gone, and the director's assistant hasn't come to work.",
       "Bir polisiye hikâyenin 1. bölümü: küçük bir kasabadaki müzenin en ünlü tablosu kaybolmuş ve müdürün asistanı işe gelmemiş.", """
Es war ein ruhiger Montagmorgen in Lindenau, einer kleinen Stadt in Süddeutschland. Wie jeden Morgen schloss Herr Kowalski, der Hausmeister des Stadtmuseums, um halb acht die Tür auf. Er machte das Licht an, kochte sich einen Kaffee und begann seinen Rundgang durch die Ausstellung.
Im ersten Saal war alles in Ordnung. Im zweiten Saal auch. Doch als er den dritten Saal betrat, blieb er plötzlich stehen. An der Wand, wo seit über hundert Jahren das berühmteste Bild des Museums hing, war nur noch ein heller Fleck zu sehen. „Der Sonnenuntergang am See“ von dem Maler Friedrich Lindner war verschwunden.
Herr Kowalski rief sofort die Polizei. Eine halbe Stunde später stand Kommissarin Anna Berger im Saal. Sie war eine kleine Frau mit kurzen grauen Haaren, die schon seit dreißig Jahren bei der Polizei arbeitete und die Stadt sehr gut kannte.
„Wer hat einen Schlüssel für das Museum?“, fragte sie.
„Nur drei Personen“, antwortete Herr Kowalski. „Ich selbst, unsere Direktorin, Frau Seidel, und ihr Assistent, Herr Brandt.“
Die Kommissarin sah sich den Saal genau an. Die Fenster waren geschlossen und nicht beschädigt. Auch an der Tür gab es keine Spuren. Die Alarmanlage war in der Nacht nicht losgegangen.
„Das bedeutet“, sagte Anna Berger langsam, „dass der Dieb entweder einen Schlüssel hatte oder dass er sich schon im Museum versteckt hatte, als es am Abend geschlossen wurde.“
Dann entdeckte sie etwas auf dem Boden: einen kleinen dunkelblauen Knopf. Er stammte offensichtlich von einer Jacke oder einem Mantel. Vorsichtig steckte sie ihn in eine Plastiktüte.
In diesem Moment kam die Direktorin in den Saal. Frau Seidel war blass und zitterte. „Das ist eine Katastrophe!“, rief sie. „Das Bild ist mehr als eine Million Euro wert. Und am Freitag sollte es für eine große Ausstellung nach Berlin gebracht werden!“
„Wer wusste von dieser Ausstellung?“, fragte die Kommissarin.
„Eigentlich alle“, sagte Frau Seidel. „Es stand sogar in der Zeitung.“
Anna Berger nickte und schrieb etwas in ihr Notizbuch. Dann fragte sie: „Und wo ist eigentlich Ihr Assistent, Herr Brandt?“
Die Direktorin sah auf die Uhr. „Das ist seltsam. Er ist sonst immer pünktlich. Heute ist er noch nicht gekommen.“
Fortsetzung folgt.
"""),
    _t("b1-bild-2", "B1", "Mystery", "Art", "Das verschwundene Bild (2)",
       "Part 2: a neighbour saw the assistant leave with a large flat parcel, and a camera photographs him in Munich.",
       "2. bölüm: bir komşu asistanın büyük, yassı bir paketle çıktığını görmüş; bir kamera onu Münih'te görüntülüyor.", """
Am Nachmittag fuhr Kommissarin Berger zur Wohnung von Thomas Brandt. Er wohnte im dritten Stock eines alten Hauses in der Nähe vom Bahnhof. Sie klingelte zweimal, aber niemand öffnete. Eine Nachbarin, die gerade die Treppe herunterkam, blieb stehen.
„Suchen Sie Herrn Brandt?“, fragte sie neugierig. „Der ist gestern Abend mit einem großen Paket weggefahren. Ich habe mich noch gewundert, weil er sonst nie so spät aus dem Haus geht.“
„Wie groß war das Paket?“, fragte die Kommissarin.
Die Nachbarin zeigte es mit den Händen. „Ungefähr so groß. Flach und rechteckig.“
Anna Berger bedankte sich. Ein flaches, rechteckiges Paket, genau so groß wie das verschwundene Bild. Die Sache sah nicht gut aus für Thomas Brandt.
Zurück im Büro suchte sie im Computer nach Informationen über ihn. Thomas Brandt war 34 Jahre alt und hatte Kunstgeschichte studiert. Er arbeitete seit fünf Jahren im Museum und war noch nie mit der Polizei in Konflikt gekommen. Aber Frau Seidel hatte am Telefon erzählt, dass er Geldprobleme hatte. „Er wollte letzten Monat mehr Gehalt“, hatte sie gesagt, „aber das Museum hat leider kein Geld.“
Am Abend rief Herr Kowalski an. Er klang aufgeregt. „Frau Kommissarin, mir ist noch etwas eingefallen. Am Sonntagabend war ich als Letzter im Museum. Als ich gegangen bin, brannte im Büro der Direktorin noch Licht. Ich habe gedacht, sie hätte es vergessen. Aber vielleicht war jemand dort.“
„Warum erzählen Sie mir das erst jetzt?“
„Es tut mir leid. Ich war heute Morgen so durcheinander.“
Die Kommissarin dachte nach. Wenn die Direktorin am Sonntagabend im Museum gewesen wäre, hätte sie das sicher erwähnt. Oder nicht?
Am nächsten Morgen kam eine überraschende Nachricht: Thomas Brandt war am Hauptbahnhof in München gesehen worden. Eine Kamera hatte ihn um sechs Uhr morgens fotografiert. Auf dem Foto trug er eine dunkelblaue Jacke.
Anna Berger vergrößerte das Foto am Computer. An der Jacke fehlte ein Knopf.
„Jetzt haben wir ihn“, sagte ihr junger Kollege Paul zufrieden. „Der Knopf, das Paket, die Geldprobleme. Alles passt zusammen.“
Doch Anna Berger schüttelte den Kopf. „Vielleicht passt es ein bisschen zu gut zusammen“, sagte sie leise.
Fortsetzung folgt.
"""),
    _t("b1-bild-3", "B1", "Mystery", "Art", "Das verschwundene Bild (3)",
       "Part 3: the assistant has a simple explanation, and the inspector finds out who really took the painting and why.",
       "3. bölüm: asistanın basit bir açıklaması var; komiser tabloyu gerçekte kimin ve neden aldığını ortaya çıkarıyor.", """
Zwei Tage später saß Thomas Brandt im Büro der Kommissarin. Die Münchner Polizei hatte ihn in einem kleinen Hotel gefunden. Er sah müde aus, aber er wirkte nicht wie ein Dieb, der Angst hat. Er wirkte eher verwirrt.
„Herr Brandt, wo ist das Bild?“, fragte Anna Berger direkt.
„Welches Bild?“, fragte er. Dann verstand er. „Sie glauben, ich hätte den ‚Sonnenuntergang am See‘ gestohlen? Das ist doch verrückt!“
„Sie sind am Sonntagabend mit einem großen, flachen Paket weggefahren. An Ihrer Jacke fehlt ein Knopf, und genau diesen Knopf haben wir im Museum gefunden.“
Thomas Brandt lachte nervös. „Das Paket war ein Spiegel, ein Geschenk für meine Schwester in München. Sie ist gerade umgezogen. Und den Knopf habe ich schon letzte Woche verloren, als ich im dritten Saal eine Lampe repariert habe. Außerdem hatte ich für Montag und Dienstag Urlaub genommen. Frau Seidel wusste das. Sie hat den Urlaub selbst unterschrieben.“
Die Kommissarin rief die Schwester an. Sie bestätigte alles und schickte sogar ein Foto von dem Spiegel, der jetzt in ihrem Flur hing.
Anna Berger lehnte sich zurück. Frau Seidel hatte also gelogen: Sie hatte gewusst, dass Brandt nicht kommen würde, und trotzdem so getan, als wäre sie überrascht. „Wer wusste von Ihren Geldproblemen?“, fragte sie.
Brandt überlegte. „Nur Frau Seidel. Ich habe es ihr erzählt, als ich um mehr Gehalt gebeten habe.“
In diesem Moment wurde der Kommissarin vieles klar. Die Direktorin hatte ihr selbst von Brandts Geldproblemen erzählt. Sie hatte einen Schlüssel. Und am Sonntagabend hatte in ihrem Büro Licht gebrannt.
Noch am selben Nachmittag ließ Anna Berger das Büro der Direktorin durchsuchen. Hinter einem Schrank fanden die Polizisten eine große Holzkiste. Darin lag, gut verpackt, „Der Sonnenuntergang am See“.
Frau Seidel gab schließlich alles zu. Das Museum hatte hohe Schulden, und die Stadt wollte es nächstes Jahr schließen. Ein reicher Sammler aus dem Ausland hatte ihr viel Geld für das Bild angeboten. „Ich wollte das Museum retten“, sagte sie leise. „Mit dem Geld hätten wir noch zehn Jahre weitermachen können. Und der Verdacht sollte auf Thomas fallen, weil jeder von seinen Geldproblemen wusste.“
Eine Woche später hing das Bild wieder an seinem Platz. Herr Kowalski putzte den Rahmen besonders gründlich. Und Thomas Brandt? Er wurde der neue Direktor des Museums. Seine erste Idee war eine Ausstellung mit dem Titel „Verschwunden und wiedergefunden“.
Ende.
"""),
    _t("b1-sonntag", "B1", "Magazine", "Culture", "Sonntags ist Ruhe",
       "Why shops are closed on Sundays in Germany, what quiet hours are, and why people still argue about it.",
       "Almanya'da pazar günleri dükkânların neden kapalı olduğu, sessizlik saatlerinin ne olduğu ve bunun neden hâlâ tartışıldığı.", """
Wer zum ersten Mal in Deutschland lebt, wundert sich oft am ersten Sonntag: Die Supermärkte sind geschlossen, die Straßen sind ruhig, und aus der Nachbarwohnung hört man kein Bohren und kein Hämmern. Der Sonntag ist in Deutschland ein Ruhetag, und das ist sogar im Grundgesetz festgelegt.
Die meisten Geschäfte dürfen am Sonntag nicht öffnen. Ausnahmen gibt es zum Beispiel für Bäckereien, die morgens für ein paar Stunden Brötchen verkaufen dürfen, für Tankstellen und für Geschäfte an Bahnhöfen und Flughäfen. Außerdem werden in vielen Städten einige verkaufsoffene Sonntage im Jahr erlaubt, oft in der Zeit vor Weihnachten.
Aber nicht nur beim Einkaufen gibt es Regeln. In vielen Häusern gilt eine Hausordnung, in der die Ruhezeiten festgelegt werden. Normalerweise soll man zwischen 22 Uhr abends und 6 Uhr morgens leise sein. Viele Hausordnungen sehen außerdem eine Mittagsruhe vor, meistens von 13 bis 15 Uhr. Am Sonntag gilt die Ruhe sogar den ganzen Tag. Rasenmähen, Bohren oder laute Musik werden dann von den Nachbarn nicht gern gesehen. Wenn die Regeln oft gebrochen werden, kann es Ärger geben, im schlimmsten Fall mit dem Vermieter.
Für viele Menschen aus dem Ausland sind diese Regeln am Anfang ungewohnt. „In Istanbul konnte ich jeden Tag bis Mitternacht einkaufen“, erzählt Deniz, die seit zwei Jahren in Stuttgart wohnt. „Hier musste ich lernen, am Samstag alles für das Wochenende zu besorgen. Inzwischen finde ich den ruhigen Sonntag aber schön. Man trifft sich mit Freunden, geht spazieren oder macht einfach nichts.“
Nicht alle sind dieser Meinung. Manche Menschen würden gern auch am Sonntag einkaufen, weil sie unter der Woche lange arbeiten. Die Kirchen und die Gewerkschaften sind dagegen: Sie wollen, dass der Sonntag ein freier Tag für Familie, Erholung und Freizeit bleibt. Über dieses Thema wird seit Jahren diskutiert, und ein Ende ist nicht in Sicht.
Übrigens: Wer am Sonntag doch etwas Wichtiges vergessen hat, kann oft noch an einem Kiosk oder an der Tankstelle einkaufen, allerdings zu etwas höheren Preisen.
"""),
    _t("b1-karneval", "B1", "Magazine", "Celebrations", "Karneval in Köln",
       "How Cologne celebrates carnival, the 'fifth season', from 11 November to Ash Wednesday.",
       "Köln'ün 'beşinci mevsim' denen karnavalı 11 Kasım'dan Kül Çarşambası'na kadar nasıl kutladığı.", """
Wenn im Februar in Köln plötzlich Clowns, Piraten und Prinzessinnen in der Straßenbahn sitzen, dann ist wieder Karneval. Die Kölner nennen diese Zeit auch die „fünfte Jahreszeit“.
Offiziell beginnt die Karnevalssaison schon am elften November um 11:11 Uhr. An diesem Tag treffen sich Tausende verkleidete Menschen in der Altstadt und feiern. Danach wird es zunächst wieder ruhiger, denn bis Weihnachten wird nur wenig gefeiert. Der Höhepunkt kommt erst im Februar oder März, in der Woche vor dem Aschermittwoch.
Der Straßenkarneval beginnt am Donnerstag, der „Weiberfastnacht“ genannt wird. An diesem Tag schneiden Frauen den Männern traditionell die Krawatte ab. Bis Dienstag wird dann fast ohne Pause gefeiert: in Kneipen, auf der Straße und in großen Sälen. Überall werden Karnevalslieder gesungen, die viele Kölner auswendig kennen.
Der wichtigste Tag ist der Rosenmontag. Dann zieht ein riesiger Umzug durch die Stadt. Der Zug ist mehrere Kilometer lang, und es dauert Stunden, bis alle Wagen und Gruppen vorbeigezogen sind. Von den Wagen werden Süßigkeiten, Blumen und kleine Geschenke in die Menge geworfen. Die Süßigkeiten nennt man in Köln „Kamelle“. Wenn die Zuschauer „Kamelle!“ rufen, wollen sie Bonbons haben. Hunderttausende Menschen stehen am Straßenrand, und viele kommen aus dem ganzen Land.
Auf vielen Wagen werden auch Politiker und aktuelle Ereignisse auf lustige Weise kritisiert. Diese Tradition ist alt: Schon vor über zweihundert Jahren hat man sich im Karneval über die Mächtigen lustig gemacht.
Am Aschermittwoch ist dann alles vorbei. Mit diesem Tag beginnt die Fastenzeit vor Ostern. Viele Kölner essen an diesem Tag traditionell Fisch, und manche fragen sich, warum sie in den Tagen davor so viel Kölsch getrunken haben.
Nicht jeder mag den Karneval. Manche Kölner fahren in dieser Zeit lieber in den Urlaub, weil ihnen der Lärm und die vielen Menschen zu viel sind. Aber für die meisten ist klar: Ohne Karneval wäre Köln nicht Köln.
"""),
    _t("b1-beschwerde", "B1", "Email", "Housing", "Eine Beschwerde",
       "A tenant writes a polite but firm complaint to the property management because the heating has been broken for weeks.",
       "Bir kiracı, kalorifer haftalardır bozuk olduğu için site yönetimine kibar ama kararlı bir şikâyet e-postası yazıyor.", """
Betreff: Defekte Heizung in der Wohnung Lindenstraße 8
Sehr geehrte Damen und Herren,
ich wohne seit März letzten Jahres in Ihrer Wohnung in der Lindenstraße 8 im zweiten Stock. Leider muss ich mich heute bei Ihnen über ein Problem beschweren, das schon seit mehreren Wochen besteht.
Seit Anfang November funktioniert die Heizung im Wohnzimmer und im Schlafzimmer nicht mehr richtig. Die Heizkörper werden nur lauwarm, obwohl ich sie ganz aufgedreht habe. Inzwischen ist es in der Wohnung abends nur noch 16 Grad warm. Besonders nachts ist es so kalt, dass ich mit Pullover und Mütze schlafen muss.
Ich habe Sie bereits Anfang November telefonisch über den Schaden informiert. Damals wurde mir versprochen, dass innerhalb einer Woche ein Handwerker vorbeikommen würde. Leider ist bis heute niemand gekommen. Auch auf meine E-Mail vor zwei Wochen habe ich keine Antwort erhalten.
Ich arbeite zurzeit viel von zu Hause aus, deshalb ist eine warme Wohnung für mich besonders wichtig. Außerdem mache ich mir Sorgen, dass sich durch die Kälte Schimmel an den Wänden bilden könnte. In der Ecke hinter dem Schrank habe ich schon kleine dunkle Flecken entdeckt.
Ich möchte Sie daher bitten, die Heizung so schnell wie möglich reparieren zu lassen. Wäre es möglich, dass ein Handwerker noch in dieser Woche kommt? Ich bin jeden Tag ab 16 Uhr zu Hause. Nach Absprache könnte ich mir auch einen Vormittag freinehmen.
Ich wäre Ihnen dankbar, wenn Sie mir bis Freitag einen Termin nennen könnten. Sollte das Problem nicht bald gelöst werden, sehe ich mich leider gezwungen, die Miete zu mindern. Darüber habe ich mich bereits beim Mieterverein informiert.
Vielen Dank im Voraus für Ihre Bemühungen.
Mit freundlichen Grüßen
Selin Aksoy
"""),
    _t("b1-lotto", "B1", "Dialogue", "Dreams", "Was wäre, wenn …?",
       "Two friends with a lottery ticket imagine what they would do with ten million euros.",
       "Elinde piyango bileti olan iki arkadaş on milyon euroyla ne yapacaklarını hayal ediyor.", """
Jana und Felix sitzen nach der Arbeit in einer Kneipe. Auf dem Tisch liegt ein Lottoschein.
Felix: Heute Abend ist die Ziehung. Stell dir vor, wir würden gewinnen! Was würdest du mit zehn Millionen Euro machen?
Jana: Zehn Millionen? Zuerst würde ich meinen Job kündigen. Na ja, vielleicht nicht sofort. Aber ich würde nur noch arbeiten, wenn ich Lust hätte.
Felix: Ich nicht. Ich würde weiterarbeiten. Ohne Arbeit wäre mir langweilig. Aber ich würde mir ein Haus am Meer kaufen, vielleicht in Portugal.
Jana: Ein Haus am Meer klingt toll. Ich hätte lieber eine Wohnung in einer großen Stadt, in New York oder in Tokio. Und ich würde jedes Jahr ein paar Monate reisen. Es gibt so viele Länder, die ich noch nie gesehen habe.
Felix: Und deine Familie? Würdest du ihr etwas von dem Geld geben?
Jana: Natürlich! Meine Eltern könnten endlich ihren Kredit für das Haus zurückzahlen. Und mein Bruder könnte sich ein neues Auto kaufen. Seins ist schon zwanzig Jahre alt.
Felix: Ich würde auch einen Teil spenden. Wenn ich so viel Geld hätte und alles für mich behalten würde, hätte ich ein schlechtes Gewissen. Vielleicht würde ich ein Tierheim unterstützen.
Jana: Das ist eine schöne Idee. Aber weißt du, was ich gelesen habe? Viele Lottogewinner sind nach ein paar Jahren nicht glücklicher als vorher. Manche haben am Ende sogar weniger Geld als früher.
Felix: Ja, davon habe ich auch gehört. Wahrscheinlich ist es gar nicht so einfach, plötzlich reich zu sein. Auf einmal wollen alle etwas von dir.
Jana: Eben. Wenn ich ehrlich bin, bin ich eigentlich ganz zufrieden. Ich hätte nur gern ein bisschen mehr Zeit.
Felix: Zeit kann man leider nicht im Lotto gewinnen.
Jana: Leider nicht. Aber weißt du was? Wenn wir gewinnen, bezahle ich heute die Getränke!
Felix: Und wenn wir nicht gewinnen?
Jana: Dann bezahlst du. Das wäre doch fair, oder?
Felix lacht und bestellt noch zwei Apfelschorlen.
"""),
    _t("b1-grossmutter", "B1", "Story", "Life stories", "Die Geschichte meiner Großmutter",
       "A grandchild tells how their grandmother came from a village in Turkey to work in Germany in 1971 and stayed for a lifetime.",
       "Bir torun, büyükannesinin 1971'de Türkiye'deki bir köyden çalışmak için Almanya'ya nasıl geldiğini ve bir ömür boyu kaldığını anlatıyor.", """
Meine Großmutter Fatma wurde 1948 in einem kleinen Dorf in der Nähe von Kayseri geboren. Sie war das älteste von sechs Kindern. Schon als kleines Mädchen musste sie ihrer Mutter im Haushalt und auf dem Feld helfen. Zur Schule ging sie nur fünf Jahre, denn die nächste weiterführende Schule war zu weit entfernt.
Mit neunzehn heiratete sie meinen Großvater Mehmet. Er arbeitete als Schneider in der Stadt, aber er verdiente nur wenig Geld. Als in den Sechzigerjahren deutsche Firmen in der Türkei Arbeitskräfte suchten, entschied sich mein Großvater, nach Deutschland zu gehen. Im Jahr 1969 fuhr er mit dem Zug von Istanbul nach München. Die Reise dauerte drei Tage.
Meine Großmutter blieb zuerst mit ihrer kleinen Tochter, meiner Mutter, im Dorf. Zwei Jahre lang schrieben sich die beiden Briefe. Telefonieren war damals schwierig und sehr teuer. „Ich habe jeden Brief zehnmal gelesen“, erzählt sie heute.
Im Jahr 1971 kam sie dann auch nach Deutschland. Sie fand Arbeit in einer Fabrik in Ludwigshafen, in der Kabel produziert wurden. Die Arbeit war hart, und am Anfang verstand sie kein Wort Deutsch. „Wenn ich damals einen Deutschkurs hätte machen können, wäre vieles einfacher gewesen“, sagt sie. Aber Kurse gab es kaum, und nach zehn Stunden in der Fabrik war sie zu müde zum Lernen. Also lernte sie die Sprache von ihren Kolleginnen, beim Einkaufen und später von ihren Kindern.
Eigentlich wollten meine Großeltern nur ein paar Jahre bleiben, Geld sparen und dann in die Türkei zurückkehren. Aber es kam anders. Meine Mutter ging in Deutschland zur Schule, zwei weitere Kinder wurden in Ludwigshafen geboren, und die Familie fand viele Freunde. Aus ein paar Jahren wurde ein ganzes Leben.
Heute ist meine Großmutter fast achtzig Jahre alt. Sie wohnt immer noch in Ludwigshafen, in derselben Straße wie früher. Jeden Sommer fliegt sie für zwei Monate in ihr Dorf. „Ich habe zwei Heimaten“, sagt sie oft. „Wenn ich in der Türkei bin, vermisse ich Deutschland. Und wenn ich hier bin, vermisse ich die Türkei.“
Ich finde ihre Geschichte sehr mutig. Ich weiß nicht, ob ich in ihrem Alter den Mut gehabt hätte, ohne ein Wort Deutsch in ein fremdes Land zu gehen.
"""),
    _t("b1-brot", "B1", "Magazine", "Food", "Das deutsche Brot",
       "Why Germans miss their bread abroad: rye and sourdough, regional rolls, 'Abendbrot', and the future of small bakeries.",
       "Almanların yurt dışında neden ekmeklerini özlediği: çavdar ve ekşi maya, yöresel küçük ekmekler, 'Abendbrot' ve küçük fırınların geleceği.", """
Wenn Deutsche längere Zeit im Ausland leben, vermissen sie oft vor allem eine Sache: richtiges Brot. Das ist kein Klischee. In Deutschland gibt es über dreitausend Brotsorten, mehr als in fast jedem anderen Land der Welt. Seit 2014 steht die deutsche Brotkultur sogar im bundesweiten Verzeichnis des immateriellen Kulturerbes.
Typisch für deutsches Brot ist, dass oft Roggen verwendet wird. Roggenbrot ist dunkler, schwerer und etwas saurer als Weißbrot. Damit der Teig aus Roggenmehl gut aufgeht, wird Sauerteig benutzt. Der Sauerteig wird oft schon am Vortag angesetzt und muss viele Stunden ruhen. Deshalb bleibt ein gutes Roggenbrot auch mehrere Tage frisch.
Beliebt sind auch Mischbrote aus Roggen und Weizen, Vollkornbrote und Brote mit Körnern wie Sonnenblumenkernen, Kürbiskernen oder Leinsamen. Im Süden isst man gern Brezeln, im Norden eher Schwarzbrot. Und am Wochenende werden zum Frühstück traditionell frische Brötchen beim Bäcker geholt. Je nach Region heißen sie auch Semmeln, Schrippen oder Wecken.
Brot spielt im deutschen Alltag eine große Rolle. Viele Familien essen abends nicht warm, sondern Brot mit Wurst, Käse und Gemüse. Diese Mahlzeit wird „Abendbrot“ genannt. Auch in der Mittagspause werden in vielen Büros belegte Brote gegessen, die man zu Hause vorbereitet hat.
Doch die Brotkultur verändert sich. Früher gab es in fast jedem Dorf eine eigene Bäckerei. Heute müssen jedes Jahr viele kleine Bäckereien schließen, weil sie keine Nachfolger finden oder weil sie mit den billigen Backwaren aus dem Supermarkt nicht konkurrieren können. Dort werden die Brötchen oft aus tiefgefrorenem Teig nur noch aufgebacken.
Gleichzeitig gibt es einen neuen Trend: In vielen Städten haben junge Bäckerinnen und Bäcker kleine Handwerksbäckereien eröffnet. Dort wird wieder langsam und mit wenigen Zutaten gebacken. Ein Brot kostet hier zwar mehr, aber viele Kunden sind bereit, für gute Qualität mehr zu bezahlen. Wer einmal ein frisches, knuspriges Roggenbrot probiert hat, versteht, warum die Deutschen ihr Brot so sehr lieben.
"""),
    _t("b1-homeoffice", "B1", "Forum", "Work", "Homeoffice oder Büro?",
       "Five people in an online forum explain whether they prefer working from home or in the office, and why.",
       "Bir çevrimiçi forumda beş kişi evden mi yoksa ofisten mi çalışmayı tercih ettiklerini ve nedenini anlatıyor.", """
In einem Onlineforum wurde gefragt: „Arbeitet ihr lieber im Homeoffice oder im Büro?“ Hier sind einige Antworten.
Kathrin, 38, Hamburg: Ich arbeite seit drei Jahren fast nur noch von zu Hause aus und möchte nie wieder zurück ins Büro. Früher habe ich jeden Tag über eine Stunde im Stau gestanden. Diese Zeit habe ich jetzt für Sport und für meine Kinder. Außerdem kann ich mich zu Hause viel besser konzentrieren, weil mich niemand ständig unterbricht.
Murat, 29, Düsseldorf: Bei mir ist es genau umgekehrt. Als ich während der Pandemie monatelang im Homeoffice war, habe ich mich ziemlich einsam gefühlt. Meine Wohnung ist klein, und ich hatte keinen richtigen Schreibtisch. Abends wusste ich oft nicht, wann die Arbeit aufhört und die Freizeit beginnt. Jetzt gehe ich wieder jeden Tag ins Büro und bin viel zufriedener. Ich brauche meine Kollegen und die Gespräche in der Kaffeeküche.
Sabine, 51, Leipzig: Ich finde, die beste Lösung liegt in der Mitte. In unserer Firma wurde vor zwei Jahren ein neues Modell eingeführt: Zwei Tage arbeiten wir im Büro, drei Tage zu Hause. An den Bürotagen finden alle Besprechungen statt, und neue Projekte werden gemeinsam geplant. An den anderen Tagen erledige ich die Aufgaben, für die ich Ruhe brauche. Für mich funktioniert das perfekt.
Jonas, 24, München: Ich habe gerade meine erste Stelle angefangen und bin froh, dass ich im Büro arbeiten kann. Wenn ich nur zu Hause säße, würde ich viel weniger lernen. Im Büro kann ich meine Kollegen einfach fragen, wenn ich etwas nicht verstehe. Per Videoanruf ist das viel komplizierter. Trotzdem wäre es schön, wenn ich ab und zu einen Tag zu Hause arbeiten dürfte, zum Beispiel wenn ein Handwerker kommt.
Petra, 45, Köln: Leider habe ich gar keine Wahl. Ich bin Krankenpflegerin, und meine Arbeit kann nicht von zu Hause aus gemacht werden. Manchmal ärgert mich die ganze Diskussion ein bisschen. Für Millionen Menschen in der Pflege, im Handel oder in der Produktion ist Homeoffice keine Option. Ich wünsche mir, dass auch über diese Menschen gesprochen wird.
Die Antworten zeigen: Eine Lösung, die für alle passt, gibt es nicht. Viele Firmen versuchen deshalb, flexible Modelle zu finden, mit denen möglichst viele Mitarbeiter zufrieden sind.
"""),
]

BY_ID = {t["id"]: t for t in TEXTS}
