"""Turkish for the B1 lessons (app/lessons_b1.py), merged into app/i18n.py like i18n_words.py.

Written per lesson in the same shape and order as the English, so the two can be read side by side:
words (";"-separated, one per word), dialogue (one line per line), grammar (title, text, examples).
EXACT below turns them into {English: Turkish} for i18n.tr(). German stays German.
"""
from .lessons_b1 import LESSONS
from .packs import _items, _rows

TR = {
    "b1-lebenslauf": {
        "subtitle": "Hayat hikâyenizi Präteritum ile anlatmak",
        "words": """özgeçmiş; mesleki eğitim; üniversite öğrenimi; diploma, mezuniyet; deneyim; iş, pozisyon; meslek; şirket;
staj; işveren; sorumluluk; doğmuş; büyümek; (üniversitede) okumak; taşınmak (ev); başlamak; o zamanlar; daha sonra;
önce, ilk başta""",
        "dialogue": """Lütfen bize biraz kendinizden bahseder misiniz, Bay Demir?
Memnuniyetle. 1995'te İzmir'de doğdum ve orada büyüdüm.
Peki okuldan sonra ne yaptınız?
Ankara'da bilgisayar bilimleri okudum. Üçüncü yılımda Hamburg'da bir şirkette staj yaptım.
Oradaki iş hoşunuza gitti mi?
Çok hoşuma gitti. Bu yüzden 2020'de Almanya'ya taşındım.
Ve o zamandan beri programcı olarak mı çalışıyorsunuz?
Evet. Önce küçük bir işim vardı, sonra daha fazla sorumluluk aldım.""",
        "grammar": ("Präteritum (geçmiş zaman)", """Yazılı Almancada (özgeçmiş, rapor, hikâye, haberler) geçmiş genellikle **Präteritum** ile anlatılır. Konuşmada ise çoğunlukla **sein**, **haben** ve kiplik fiillerle kullanılır: war, hatte, konnte, musste.

**Düzenli fiiller** köke **-te** ekler:
- ich mach**te**, du mach**test**, er mach**te**, wir mach**ten**, ihr mach**tet**, sie mach**ten**
- Kök -t veya -d ile bitiyorsa araya bir e girer: arbeiten → ich arbeit**ete**

**Düzensiz fiiller** ünlülerini değiştirir. ich ve er biçimleri ek almaz:
- gehen → ging → ist gegangen
- beginnen → begann → hat begonnen
- finden → fand → hat gefunden
- ich ging, du gingst, er ging, wir gingen, ihr gingt, sie gingen

**Karma fiiller** hem ünlüyü değiştirir hem de -te alır: denken → dachte, bringen → brachte, kennen → kannte.

Ayrılabilen fiiller şimdiki zamandaki gibi ayrılır: Ich **zog** 2020 nach Berlin **um**.""",
                    "Küçük bir köyde büyüdüm.; Okuldan sonra mesleki eğitime başladı.; 2018'de Köln'e taşındık.; O zamanlar büyük bir şirkette çalışıyordu."),
    },
    "b1-schulzeit": {
        "subtitle": "als ve wenn ile okul anıları",
        "words": """ilkokul; lise (üniversiteye hazırlayan); ders (okulda); not; karne; sınav; sınıf, okul yılı; ödev;
lise bitirme sınavı; (sınavı) geçmek; (sınavdan) kalmak; hatırlamak; sert, katı; çalışkan; tembel; gururlu;
-dığında (geçmişte bir kez); -dığında, her ne zaman, eğer""",
        "dialogue": """Okul yıllarını hatırlamayı sever misin?
Çoğunlukla evet. İlkokula başladığımda henüz hiç Almanca bilmiyordum.
Bu kesin zor olmuştur.
Başta evet. Ama bir şeyi anlamadığım her seferde öğretmenim bana yardım ederdi.
Peki lisede? Çalışkan bir öğrenci miydin?
Her zaman değil! Matematikte sık sık kötü notlar alırdım. Bir keresinde bir sınavdan kaldım bile.
Peki lise bitirme sınavını geçtiğinde nasıldı?
Harikaydı! Ailem çok gururluydu ve bütün gece kutlama yaptık.""",
        "grammar": ("als mı, wenn mi?", """İkisi de "-dığında" anlamına gelir, ama Almanca ikisini birbirinden ayırır:

- **als**: geçmişte tek bir olay veya tek bir dönem. **Als** ich sechs war, kam ich in die Schule.
- **wenn**: geçmişte tekrar tekrar olan bir şey (her ne zaman): **Wenn** ich Hausaufgaben machte, hörte ich Musik.
- **wenn** ayrıca şimdi veya gelecekteki her şey için (-dığında, eğer): **Wenn** ich morgen Zeit habe, rufe ich dich an.

İkisi de bir yan cümle başlatır, bu yüzden fiil **sona** gider. Yan cümle önce gelirse, ana cümle fiiliyle başlar: **Als ich klein war, wohnten wir in Bremen.**

"Ne zaman?" soru sözcüğü **wann**'dır: **Wann** hast du Abitur gemacht? Dolaylı soruları da başlatır: Ich weiß nicht, **wann** er kommt.""",
                    "On yaşındayken Köln'e taşındık.; Ne zaman iyi bir not alsam annem gurur duyardı.; Sınavı geçtiğinde çok mutluydu.; Sorun olursa beni ara."),
    },
    "b1-reisepech": {
        "subtitle": "Yolculuk sorunları ve Plusquamperfekt",
        "words": """gecikme; aktarma bağlantısı (tren, otobüs); uçuş; havalimanı; bagaj; bavul; peron, ray; anons;
gişe, bilet gişesi; çalar saat; iptal olmak; kaçırmak (tren, uçak); kaybetmek; kalkmak (araç); inmek (uçak);
aktarma yapmak; zamanında; maalesef""",
        "dialogue": """Viyana yolculuğun nasıldı?
Tam bir felaket! İstasyona vardığımda trenim çoktan kalkmıştı.
Olamaz! Neden bu kadar geç kaldın?
Çalar saati duymamıştım. Ben de bir sonraki trene bindim ama o da bir saat rötarlıydı.
Sonra da Münih'teki aktarmayı mı kaçırdın?
Aynen. Viyana'da da bavulumu trende unuttuğumu fark ettim.
Geri alabildin mi?
Evet, neyse ki biri onu kayıp eşya bürosuna teslim etmişti.""",
        "grammar": ("Plusquamperfekt: geçmişten önceki geçmiş", """Geçmişte geçen bir şeyi anlatırken bir adım daha geriye gitmeniz gerekirse **Plusquamperfekt** kullanılır. Perfekt gibi kurulur, ama haben veya sein'ın geçmiş biçimiyle: **hatte / war + Partizip II**.

- Perfekt: Der Zug **ist abgefahren**.
- Plusquamperfekt: Der Zug **war** schon **abgefahren**. (ben varmadan önce)

Biçimler:
- ich **hatte** gehört / ich **war** gegangen
- du **hattest** gehört / du **warst** gegangen
- er, sie, es **hatte** gehört / **war** gegangen
- wir **hatten** gehört / wir **waren** gegangen

Perfekt'te sein alan fiiller burada **war** alır: abfahren → der Zug **war abgefahren**, ankommen → wir **waren angekommen**. Diğer bütün fiiller **hatte** alır: verpassen → ich **hatte** den Zug **verpasst**.

Çoğunlukla **als** veya **nachdem** ile birlikte kullanılır: Als ich ankam, **war** der Zug schon **abgefahren**.""",
                    "Bileti çoktan almıştım.; İndiğimizde yağmur dinmişti.; Daha önce hiç uçağa binmemişti.; Pasaportunu evde unutmuştu."),
    },
    "b1-arbeitstag": {
        "subtitle": "Zaman yan cümleleri: bevor, nachdem, während, seit",
        "words": """iş yeri, iş; iş arkadaşı (erkek); iş arkadaşı (kadın); şef, patron; toplantı; görev; mola; kantin, yemekhane;
sözleşme; fazla mesai saati; tanıştırmak; halletmek; imzalamak; sorumlu, yetkili; -madan önce; -dıktan sonra;
-ken; -dığından beri""",
        "dialogue": """Hoş geldiniz, Bayan Kaya! Başlamadan önce sizi ekiple tanıştırayım.
Teşekkür ederim! Bu arada öğle arası ne zaman?
Saat on ikide. Yemek yedikten sonra kısa bir toplantımız var.
İşe alışmamdan kim sorumlu?
Bayan Roth. On yıldır burada çalışıyor ve bütün görevleri biliyor.
Sözleşmeyi bugün imzalamam gerekiyor mu?
Evet, lütfen. Siz imzalarken ben de bize birer kahve getireyim.""",
        "grammar": ("bevor, nachdem, während, seit", """Bu sözcükler zamanla ilgili bir yan cümle başlatır. Fiil yan cümlenin **sonuna** gider.

- **bevor** (-madan önce): **Bevor** ich zur Arbeit gehe, trinke ich einen Kaffee.
- **nachdem** (-dıktan sonra): **Nachdem** ich den Vertrag unterschrieben hatte, begann ich mit der Arbeit.
- **während** (-ken): **Während** du telefonierst, schreibe ich die E-Mail.
- **seit** veya **seitdem** (-dığından beri): **Seit** ich hier arbeite, fahre ich mit dem Rad.

**nachdem** ile zamanlar bir adım geri kayar, çünkü nachdem cümlesindeki eylem önce olmuştur:
- Ana cümle şimdiki zamanda → Perfekt: Nachdem ich gegessen **habe**, gehe ich zur Besprechung.
- Ana cümle geçmiş zamanda → Plusquamperfekt: Nachdem ich gegessen **hatte**, ging ich zur Besprechung.

Bağlaç olan **nachdem** ile edat olan **nach**'ı karıştırmayın: **nach** der Arbeit, ama **nachdem** ich gearbeitet habe.""",
                    "Gitmeden önce lütfen ışığı kapat.; Görevi bitirdikten sonra mola verdi.; Şef konuşurken ben not alıyorum.; Burada çalışmaya başladığından beri çok fazla mesai yapıyor."),
    },
    "b1-bewerbung": {
        "subtitle": "İş başvurusu yapmak ve kibarca sormak",
        "words": """başvuru; başvurmak; iş ilanı; iş görüşmesi; maaş; şart, ön koşul; aday, başvuran; ön yazı; yarı zamanlı iş;
tam zamanlı iş; deneme süresi; işe almak; istifa etmek, işten ayrılmak; kazanmak (para); deneyimli; esnek;
bağımsız, kendi başına""",
        "dialogue": """Weber ve Ortakları, ben Schulz. İyi günler!
İyi günler, adım Yılmaz. İş ilanınızı okudum ve birkaç sorum olacaktı.
Tabii. Konu nedir?
Bu pozisyonun yarı zamanlı da mümkün olup olmadığını söyleyebilir misiniz?
Maalesef hayır, tam zamanlı birini arıyoruz.
Sorun değil. Başvurumu kime göndermem gerektiğini de söyler misiniz?
Lütfen doğrudan bana gönderin. Sizden yakında haber almaktan memnun oluruz!
Çok teşekkür ederim, memnuniyetle.""",
        "grammar": ("Konjunktiv II: kibarca rica etmek", """Bir ricayı veya isteği kibar söylemek için Almanca **Konjunktiv II** kullanır. Türkçedeki "-ir misiniz", "-abilir misiniz", "-mek isterdim" gibidir.

En kullanışlı biçimler:
- **würde** + mastar: Ich **würde** gern mehr **verdienen**. **Würden** Sie mir helfen?
- **könnte** (-abilirdi): **Könnten** Sie das bitte wiederholen?
- **hätte** (olurdu, sahip olurdu): Ich **hätte** eine Frage.
- **wäre** (olurdu): Das **wäre** sehr nett.
- **möchte** (isterdi): Ich **möchte** mich um die Stelle bewerben.
- **sollte** (-malı): Sie **sollten** Ihren Lebenslauf mitschicken.

Ekler: ich würde, du würdest, er würde, wir würden, ihr würdet, sie würden. hätte, wäre ve könnte de aynı şekilde çekimlenir: du hättest, du wärst, du könntest.

Karşılaştırın: **Können Sie** mir helfen? (doğrudan) → **Könnten Sie** mir helfen? (daha kibar)""",
                    "Bana belgeleri gönderebilir misiniz lütfen?; Pozisyon hakkında daha fazla bilgi almak isterdim.; Beni lütfen geri arar mısınız?; Yüz yüze görüşebilseydik güzel olurdu."),
    },
    "b1-gesund": {
        "subtitle": "Sağlık, alışkanlıklar ve dilekler için Konjunktiv II",
        "words": """sağlık; beslenme; hareket, egzersiz; stres; kilo, ağırlık; sırt; ağrı; hastalık; reçete, yemek tarifi;
sağlık sigortası şirketi; beslenmek; kilo vermek; kilo almak; bırakmak, durmak; dinlenmek, rahatlamak;
düzenli, düzenli olarak; sağlıksız""",
        "dialogue": """Bay Becker, sırt ağrılarınız stresten ve az hareketten kaynaklanıyor.
Biliyorum. Daha çok zamanım olsaydı her gün spor yapardım.
Günde yirmi dakika bile yardımcı olurdu. Örneğin işe bisikletle gidebilirsiniz.
Bu bir fikir olabilir. Ama çok uzakta oturuyorum.
Peki nasıl besleniyorsunuz?
Açıkçası oldukça sağlıksız. Keşke daha iyi yemek yapabilsem.
Sizin yerinizde olsam bir yemek kursuna giderdim. Sağlık sigortası çoğu zaman bir kısmını ödüyor.""",
        "grammar": ("Konjunktiv II: dilekler ve gerçek dışı koşullar", """Konjunktiv II **gerçek olmayan** şeylerden de söz eder: dilekler, hayaller ve "ya olsaydı".

**Gerçek dışı koşullarda** **wenn** kullanılır ve iki bölümde de Konjunktiv II olur:
- **Wenn** ich mehr Zeit **hätte**, **würde** ich mehr Sport **machen**. (Ama daha fazla zamanım yok.)
- **Wenn** ich du **wäre**, **würde** ich zum Arzt gehen.

Gerçek bir koşulla karşılaştırın: **Wenn** ich Zeit **habe**, mache ich Sport. (Bu mümkün.)

**Dilekler** için **wenn ... nur** veya **ich wünschte** kullanılır:
- **Wenn** ich **nur** gesünder **wäre**!
- **Ich wünschte**, ich **könnte** besser schlafen.

**Tavsiye**: **An deiner Stelle würde ich** ... (Senin yerinde olsam ...)

Çoğu fiil **würde** + mastar kullanır. sein, haben ve kiplik fiillerin kendi biçimleri vardır: **wäre, hätte, könnte, müsste, dürfte**. Bazı yaygın fiillerin de kendi biçimleri vardır: **käme, ginge, wüsste**.""",
                    "Bu kadar yorgun olmasaydım koşuya giderdim.; Daha az stresi olsaydı daha iyi uyuyabilirdi.; Keşke spor için daha çok zamanım olsa.; Senin yerinde olsam sigarayı bırakırdım."),
    },
    "b1-reklamation": {
        "subtitle": "Tüketici şikâyetleri ve geçmişte Konjunktiv II",
        "words": """kusurlu ürün şikâyeti; şikâyet; şikâyet etmek; müşteri; müşteri hizmetleri; garanti; fiş, makbuz;
değişim (ürün); değiştirmek (ürün); iade etmek, geri vermek; tamir etmek; arızalı, kusurlu; geri almak;
hata, kusur; teslimat; can sıkıcı; hayal kırıklığına uğramış""",
        "dialogue": """İyi günler. Şikâyette bulunmak istiyorum. Bu kahve makinesi iki hafta sonra bozuldu.
Çok üzgünüm. Fişiniz yanınızda mı?
Evet, buyurun. Paramı geri almak isterdim.
Makineyi tamir ettirebiliriz. İki yıl garantisi var.
Açıkçası hayal kırıklığına uğradım. Bunu bilseydim başka bir model alırdım.
Anlıyorum. O zaman onu yeni bir modelle değiştirelim.
Teşekkürler. Bunu bana en başta da önerebilirdiniz!""",
        "grammar": ("Geçmişte Konjunktiv II", """Geçmişte **olmamış** bir şeyden söz etmek için (pişmanlıklar, kaçırılan fırsatlar) **hätte** veya **wäre** + **Partizip II** kullanılır:

- Wenn ich das **gewusst hätte**, **hätte** ich die Maschine nicht **gekauft**. (Ama bilmiyordum.)
- Wenn das Paket früher **gekommen wäre**, **wäre** ich zu Hause **gewesen**.

hätte ile wäre arasında, Perfekt'te haben ile sein arasında seçtiğiniz gibi seçim yapın:
- gekauft, gewusst, gesagt → **hätte**
- gekommen, gegangen, gewesen → **wäre**

Pişmanlık: **Hätte** ich **nur** die Garantie **gelesen**! (Keşke garantiyi okusaydım!)

Kiplik fiille **hätte** kullanılır ve sonda iki mastar olur: Sie **hätten** mich anrufen **sollen**. (Beni aramalıydınız.) Das **hätten** Sie mir gleich anbieten **können**. (Bunu bana hemen önerebilirdiniz.)""",
                    "Fişi saklasaydım paramı geri alırdım.; Teslimat zamanında gelseydi şikâyet etmezdim.; Keşke başka bir model alsaydım!; Beni aramalıydınız."),
    },
    "b1-weiterbildung": {
        "subtitle": "Mesleki gelişim ve zu'lu mastar",
        "words": """mesleki gelişim eğitimi; kurs; halk eğitim merkezi; ücret, harç; sertifika; hedef; olanak, fırsat; kayıt;
yetenek, beceri; planlamak, niyetinde olmak; denemek; kaydolmak; katılmak; karar vermek; tavsiye etmek;
sunmak, teklif etmek; mesleki, mesleki olarak""",
        "dialogue": """Bir mesleki gelişim eğitimi almaya karar verdim.
Süper! Ne yapmayı planlıyorsun?
Muhasebe kursuna gitmeyi planlıyorum. Halk eğitim merkezi böyle bir kurs açıyor.
Yer bulmak zor mu?
Hayır, sadece internetten kaydolmak gerekiyor. Ücret de yüksek değil.
Peki işin yanında ders çalışmaya vaktin var mı?
Her akşam bir saat çalışmaya çalışıyorum. Sonunda bir sertifika alıyorum.
Kulağa hoş geliyor. Hedefini yazmanı tavsiye ederim.""",
        "grammar": ("zu + mastar", """Pek çok fiil, isim ve sıfattan sonra ikinci fiil en sonda **zu** ile gelir:

- Ich **versuche**, jeden Tag **zu lernen**.
- Ich **habe** keine **Zeit**, ins Kino **zu gehen**.
- **Es ist wichtig**, regelmäßig **zu üben**.

Ayrılabilen fiillerde **zu** ön ek ile fiilin arasına girer ve tek kelime olarak yazılır: an**zu**fangen, auf**zu**stehen, an**zu**melden.

Sık kullanılan başlangıçlar:
- fiiller: **anfangen, aufhören, beschließen, vergessen, versuchen, vorhaben, empfehlen**
- isimler: **Lust haben, Zeit haben, Angst haben**
- sıfatlar: **es ist wichtig / schwer / leicht / schön**

Kiplik fiillerden sonra **zu kullanılmaz**: Ich **muss** lernen. Wir **können** morgen anfangen.""",
                    "Gelecek yıl bir dil kursuna gitmeyi planlıyorum.; Zamanında kaydolmayı unutma!; İşin yanında üniversite okumak kolay değil.; Kursa benimle gelmek ister misin?"),
    },
    "b1-bank": {
        "subtitle": "Para ve bankacılık: um ... zu, damit, ohne ... zu, statt ... zu",
        "words": """banka hesabı; havale; havale etmek; kredi kartı; şifre (PIN); bankamatik, ATM; (para) çekmek;
biriktirmek (para); ödünç vermek, ödünç almak; kredi, borç; kira; harcamak; nakit para; tutar, miktar;
açmak (hesap, dükkân); hesap dökümü; şube (banka veya mağaza)""",
        "dialogue": """İyi günler, size nasıl yardımcı olabilirim?
Maaşımı buraya yatırtmak için bir hesap açmak istiyorum.
Memnuniyetle. Kredi kartına da ihtiyacınız var mı?
Evet, yurt dışında ödeme yapabilmem için. Hesabın bir ücreti var mı?
İnternet bankacılığı kullanırsanız ücretsiz. Böylece şubeye gelmeden havale yapabilirsiniz.
Çok iyi. Her yerden para çekebilir miyim?
Bizim bankamatiklerimizden evet. Ama nakit ödemek yerine kartı neredeyse her yerde kullanabilirsiniz.""",
        "grammar": ("um ... zu, damit, ohne ... zu, statt ... zu", """**um ... zu** ve **damit** ikisi de bir amaç bildirir (-mek için, -sin diye):
- Ich spare, **um** ein Auto **zu kaufen**. (aynı kişi: ben biriktiriyorum, ben alıyorum)
- Ich spare, **damit** meine Kinder studieren **können**. (farklı kişiler: ben biriktiriyorum, çocuklarım okuyor)

İki bölümde de aynı kişi varsa **um ... zu** kullanın. Farklı kişiler varsa **damit** kullanmak zorunludur. damit bir yan cümle başlatır, bu yüzden fiil sona gider.

**ohne ... zu** (-madan): Er hat bezahlt, **ohne** die Rechnung **zu lesen**.
**statt ... zu** (-mek yerine): **Statt** Geld **zu sparen**, gibt sie alles aus.

Bu üç zu yapısında da **zu** + mastar sona gelir ve ayrılabilen fiillerde zu ortaya girer: Ich gehe zur Bank, um Geld ab**zu**heben.""",
                    "Nakit çekmek için bankamatiğe gidiyorum.; Kirayı ödeyebilesin diye parayı sana havale ediyorum.; Ücretleri kontrol etmeden hesabı açtı.; Kredi çekmek yerine biriktirmeyi tercih ediyoruz."),
    },
    "b1-medien": {
        "subtitle": "Cihazlar ve medya: ilgi cümleleri",
        "words": """cihaz, alet; ekran; ağ, internet; mesaj, haber; yayın, TV programı; kanal, istasyon; reklam; uygulama;
şifre, parola; şarjlı pil, batarya; yazıcı; indirmek; kaydetmek (veri); silmek; şarj etmek; yüklemek (program);
kullanmak""",
        "dialogue": """Leon, bana yardım edebilir misin? Bu geçen hafta aldığım telefon.
Tabii, babaanne. Sorun ne?
Her gün şarj etmem gereken batarya hep çok çabuk bitiyor.
Bu arka planda çalışan uygulamalardan kaynaklanıyor. Birkaçını siliyorum.
Ama annenin bana yüklediği uygulamayı silme!
Merak etme. Bu arada, bu kadar çok mesaj gönderdiğin kadın kim?
O, bir yıldır İspanya'da yaşayan arkadaşım Gisela!""",
        "grammar": ("İlgi cümleleri", """İlgi cümlesi bir ismi daha yakından tanımlar, Türkçedeki "-an, -dığı" yapıları gibi. Bir **ilgi zamiri** ile başlar, fiil **sona** gider ve önünde her zaman virgül olur.

İlgi zamiri **cinsiyetini ve sayısını** tanımladığı isimden, **halini** ise ilgi cümlesindeki görevinden alır:
- Nominativ: Der Mann, **der** dort steht, ist mein Chef.
- Akkusativ: Der Laptop, **den** ich gekauft habe, ist schnell.
- Dativ: Die Frau, **der** ich die E-Mail schicke, wohnt in Wien.

Biçimler (eril, dişil, nötr, çoğul):
- Nominativ: der, die, das, die
- Akkusativ: **den**, die, das, die
- Dativ: **dem**, **der**, **dem**, **denen**
- Genitiv: **dessen**, **deren**, **dessen**, **deren**

İngilizcedekinin aksine ilgi zamiri **asla** atlanamaz: aldığım telefon = das Handy, **das** ich gekauft habe.""",
                    "Bu artık çalışmayan cihaz.; Yeni aldığımız yazıcı nerede?; Şifreyi verdiğim iş arkadaşları zaten burada.; Reklamı olmayan bir uygulama arıyorum."),
    },
    "b1-verein": {
        "subtitle": "Kulüpler ve kültür: edatlı ilgi cümleleri, dessen ve deren",
        "words": """kulüp, dernek; üye; etkinlik; konser; sergi; tiyatro oyunu; sahne; giriş (ücreti); bilet (etkinlik için);
gönüllü çalışma; koro; takım; seyirci; gönüllü olarak katkıda bulunmak; katılmak (bir şeye); gerçekleşmek, yapılmak;
heyecanlı, sürükleyici""",
        "dialogue": """Hafta sonları aslında ne yapıyorsun?
Neredeyse sadece emeklilerin olduğu bir koroda şarkı söylüyorum.
Gerçekten mi? Sıkıcı değil mi?
Hiç de değil! Gelecek ay uzun zamandır prova yaptığımız bir konser var.
Harika! Ben de bütün üyeleri yeni başlayan bir tiyatro kulübündeyim.
Peki herkesin konuştuğu bir oyun var mı?
Evet, sonunu henüz söylemeyeceğim bir komedi! Galaya gelir misin?
Memnuniyetle. Biletler nereden alınıyor?""",
        "grammar": ("Edatlı ilgi cümleleri; dessen ve deren", """İlgi cümlesindeki fiil bir edat gerektiriyorsa, edat **başa** gelir, ardından edatın gerektirdiği halde ilgi zamiri gelir:

- sich interessieren **für** + Akkusativ: Das ist der Verein, **für den** ich mich interessiere.
- singen **in** + Dativ: Der Chor, **in dem** ich singe, ist sehr gut.
- sprechen **über** + Akkusativ: Das ist das Stück, **über das** alle sprechen.
- **mit** + Dativ: Die Freunde, **mit denen** ich ins Theater gehe, kommen aus Polen.

Almancada edat, İngilizcedeki gibi **asla** sona gidemez.

"Kimin, neyin" anlamındaki sahiplik biçimi eril ve nötr isimler için **dessen**, dişil isimler ve çoğullar için **deren**'dir. Ondan sonraki isim artikel almaz:
- Der Verein, **dessen** Mitglieder alle Anfänger sind ... (üyelerinin hepsi yeni başlayan kulüp ...)
- Die Sängerin, **deren** Stimme so schön ist ... (sesi çok güzel olan şarkıcı ...)""",
                    "Sana bahsettiğim sergi bu.; Oynadığım kulüp yeni üyeler arıyor.; Filmi şu an gösterimde olan oyuncuyu tanıyor musun?; Konsere birlikte gittiğimiz komşular çok iyi insanlar."),
    },
    "b1-umwelt": {
        "subtitle": "Çevre ve edilgen yapı",
        "words": """çevre; çöp; ambalaj; plastik; enerji; elektrik; iklim; hava; trafik; depozito (şişeler için); ayırmak;
toplamak; geri dönüştürmek; tüketmek, harcamak; korumak; kirletmek; çevre dostu""",
        "dialogue": """Affedersiniz Bayan Schmidt, bu yoğurt kabı hangi çöp kutusuna gidiyor?
Sarı kutuya. Orada bütün plastik ambalajlar toplanıyor.
Peki sonra onlara ne oluyor?
Çöpler alınıp ayrıştırılıyor. Birçoğu geri dönüştürülüyor.
Peki şişeler? Onlar da sarı kutuya mı atılıyor?
Hayır! Birçok şişe için depozito alırsınız. Onlar süpermarkete iade ediliyor.
Almanya'da gerçekten her şey ayrıştırılıyor!""",
        "grammar": ("Edilgen yapı: werden + Partizip II", """**Edilgen yapıda** işi kimin yaptığından çok ne yapıldığı önemlidir. **werden** + sonda **Partizip II** ile kurulur:

- Etken: Die Stadt **sammelt** den Müll.
- Edilgen: Der Müll **wird** (von der Stadt) **gesammelt**.

Etken cümlenin nesnesi özne olur: **den** Müll → **der** Müll.

werden'in biçimleri:
- ich **werde** gefragt, du **wirst** gefragt, er, sie, es **wird** gefragt
- wir **werden** gefragt, ihr **werdet** gefragt, sie, Sie **werden** gefragt

İşi kimin yaptığını söylemek için **von** + Dativ kullanılır: Das Papier wird **von den Kindern** gesammelt. Genellikle bu kısım söylenmez.

**man** ile kurulan bir cümle aynı şeyi etken yapıda söyler: **Man** trennt den Müll. = Der Müll **wird** getrennt.""",
                    "Almanya'da çöpler ayrıştırılır.; Şişeler süpermarkete iade edilir.; Burada çok elektrik tüketiliyor.; Kâğıtlar her salı toplanır."),
    },
    "b1-geschichte": {
        "subtitle": "Kültür ve tarih: geçmiş zamanda edilgen yapı",
        "words": """tarih, hikâye; anıt; saray, şato; savaş; duvar; sınır; yeniden birleşme; yüzyıl; kral; sanatçı; tablo, resim;
rehberli tur; kurmak (kuruluş); yıkmak; dikmek, inşa etmek; keşfetmek; resim yapmak, boyamak; ünlü""",
        "dialogue": """Tura hoş geldiniz! Bu saray 18. yüzyılda inşa edildi.
Burada kim yaşadı?
Bir kral tarafından yazlık olarak kullanıldı. Daha sonra müzeye dönüştü.
Bina savaşta yıkıldı mı?
Evet, kısmen. Savaştan sonra yeniden inşa edildi.
Peki bu tablo? Kim tarafından yapıldı?
Ünlü bir sanatçı tarafından yapıldı ve ancak 1990'da bodrumda bulundu.
İnanılmaz! İyi ki atılmamış.""",
        "grammar": ("Geçmiş zamanda edilgen yapı", """Edilgen yapının geçmiş zamanı da vardır.

**Präteritum**: **wurde** + Partizip II. Yazıda, tarihte ve haberlerde en çok kullanılan biçimdir:
- Das Schloss **wurde** 1750 **gebaut**.
- Die Bilder **wurden** im Keller **gefunden**.
- ich wurde, du wurdest, er wurde, wir wurden, ihr wurdet, sie wurden

**Perfekt**: **ist ... worden**. Edilgen Perfekt her zaman **sein** ile kurulur ve **worden** (geworden değil) en sona gelir:
- Das Schloss **ist** im Krieg **zerstört worden**.

Dikkat: **geworden**, normal fiil olarak werden'e (olmak) aittir: Er ist Lehrer **geworden**. Edilgen yapıda **worden** kullanılır: Er ist gefragt **worden**.

**wurde** (oldu, -ıldı) ile Konjunktiv II'deki **würde** (-ardı) biçimini de karıştırmayın.""",
                    "Duvar 1961'de inşa edildi.; Duvar 1989'da açıldı.; Kilise savaşta yıkıldı.; Müze 1902'de kuruldu."),
    },
    "b1-hausordnung": {
        "subtitle": "Birlikte yaşamak: kiplik fiillerle edilgen yapı",
        "words": """apartman kuralları; komşu (erkek); komşu (kadın); kapıcı, bina görevlisi; ev sahibi (kiraya veren); kiracı;
merdiven boşluğu; bodrum, kiler; gürültü; sessizlik, huzur; saygı, düşünceli davranma; avlu; çöp kutusu; rahatsız etmek;
izin vermek; yasaklamak; uymak, dikkate almak (kurallar); yüksek sesli, gürültülü""",
        "dialogue": """Bay Rossi, apartman kurallarını okudunuz mu?
Tamamını değil. Peki nelere dikkat edilmesi gerekiyor?
Saat 22'den itibaren gece sessizliğine uyulması gerekiyor. O saatten sonra yüksek sesle müzik yasak.
Peki merdiven boşluğu? Kiracılar tarafından mı temizlenmesi gerekiyor?
Evet, her hafta. Plan aşağıda koridorda asılı.
Bisikletim avluya bırakılabilir mi?
Evet, tabii ki. Yalnız merdiven boşluğuna hiçbir şey bırakılmamalı.
Anlaşıldı. Zaten hiçbir komşuyu rahatsız etmek istemem.""",
        "grammar": ("Kiplik fiillerle edilgen yapı", """Neyin yapılması **gerektiğini**, yapılabileceğini, yapılmasına **izin** verildiğini veya yapılması **istendiğini** söylemek için kiplik fiil ikinci sıraya, **Partizip II + werden** sona gelir:

- Der Müll **muss** getrennt **werden**. (ayrıştırılmalı)
- Das Fahrrad **kann** im Hof abgestellt **werden**. (bırakılabilir)
- Im Treppenhaus **darf** nicht geraucht **werden**. (sigara içilmez)
- Die Fenster **sollen** geschlossen **werden**. (kapatılmalı)

Kiplik fiil özneye uyar: Die Mülltonne **muss** ... Die Mülltonnen **müssen** ...

Yan cümlede kiplik fiil en sona gider: Ich weiß, dass der Keller aufgeräumt werden **muss**.

Geçmiş zamanda kiplik fiilin Präteritum biçimi kullanılır: Die Wohnung **musste** renoviert werden.""",
                    "Merdiven boşluğu her hafta temizlenmeli.; Saat 22'den sonra yüksek sesle müzik çalınamaz.; Kalorifer tamir edilemedi.; Kapıcı çöp kutularının avluya konulması gerektiğini söylüyor."),
    },
    "b1-kollegen": {
        "subtitle": "İş ilişkileri ve n-çekimi",
        "words": """stajyer; asistan; uzman; tedarikçi; mimar; aday; gazeteci; fotoğrafçı; insan, kişi; bey, beyefendi;
selamlamak, karşılamak; ilgilenmek, bakmak; danışmanlık yapmak; vekâlet etmek; birine du demek; birine Sie demek;
kibar""",
        "dialogue": """Max, bugün yeni stajyerle ilgilenebilir misin?
Memnuniyetle. Adı ne?
Jonas Keller. Lütfen stajyere önce ofisi göster ve onu iş arkadaşlarıyla tanıştır.
Tamamdır. Saat onda mimar da geliyor, değil mi?
Aynen. Lütfen Bay Meyer'i karşılayıp ona bir kahve ikram eder misin?
Tabii. Bu arada mimara du mu diyoruz, Sie mi?
Ona Sie diyoruz. Çok kibar bir insan ama biraz resmî.""",
        "grammar": ("n-çekimi", """Bir grup **eril** isim, tekil Nominativ dışındaki her halde **-n** veya **-en** alır:

- Nominativ: **der** Kollege, **der** Praktikant
- Akkusativ: **den** Kollege**n**, **den** Praktikant**en**
- Dativ: **dem** Kollege**n**, **dem** Praktikant**en**
- Genitiv: **des** Kollege**n**, **des** Praktikant**en**
- Çoğul, bütün hallerde: **die** Kollege**n**, **die** Praktikant**en**

Hangi isimler? Çoğunlukla insanlar ve hayvanlar için kullanılan eril isimler:
- **-e** ile bitenler: der Kollege, der Kunde, der Junge, der Experte
- **-ant, -ent, -ist** ile bitenler: der Praktikant, der Assistent, der Journalist
- **-at, -oge, -graf** ile bitenler: der Kandidat, der Biologe, der Fotograf
- birkaç başka isim: der **Mensch**, der **Nachbar**, der **Architekt**, der **Herr** (den Herr**n**, çoğulu die Herr**en**)

Mektuplarda: Sehr geehrter **Herr** Meyer (Nominativ), ama Ich spreche mit **Herrn** Meyer.""",
                    "İş arkadaşına soracağım.; Stajyere yardım edebilir misin?; Tedarikçiyi bekliyoruz.; Burası asistanın ofisi."),
    },
    "b1-streik": {
        "subtitle": "Yolculuk sorunları: Genitiv ve wegen, trotz, während",
        "words": """grev; fırtına, kötü hava; şantiye, yol çalışması; trafik sıkışıklığı; sapma, alternatif güzergâh; tazminat;
havayolu şirketi; yolcu; neden, sebep; iptal etmek (rezervasyon); rezervasyon yapmak; iade etmek, geri ödemek;
-den dolayı, yüzünden; -e rağmen; içinde (süre, yer); dışında""",
        "dialogue": """Bir grev nedeniyle bugün Hamburg'a giden bütün uçuşlar iptal edilmiştir.
Affedersiniz, Hamburg'a bir uçuş rezervasyonum var. Şimdi ne yapmalıyım?
Greve rağmen trenler çalışıyor. Sizi memnuniyetle bir trene aktarırız.
Peki tazminat alacak mıyım?
Evet. Havayolu şirketi bir hafta içinde bilet ücretini size iade edecek.
İyi. Beklerken bir yerde çalışabilir miyim?
Tabii ki. Grev nedeniyle salon bugün bütün yolculara açık.""",
        "grammar": ("Genitiv ve wegen, trotz, während", """**Genitiv**, bir şeyin birine veya bir şeye ait olduğunu gösterir (Türkçedeki "-in, -ın" gibi). Konuşmadan çok yazıda kullanılır.

Artikel biçimleri:
- eril: **des** Streik**s**, **eines** Mann**es** (isim -s veya -es alır)
- nötr: **des** Ticket**s**, **eines** Kind**es**
- dişil: **der** Fluggesellschaft, **einer** Woche (isim ek almaz)
- çoğul: **der** Passagiere

Tek heceli kısa isimler genellikle **-es** alır (des Mannes, des Zuges), daha uzun olanlar **-s** (des Flughafens). n-isimleri -n veya -en alır: des Kollegen.

Bazı edatlar Genitiv ister:
- **wegen** (-den dolayı): **wegen des** Wetters
- **trotz** (-e rağmen): **trotz des** Streiks
- **während** (sırasında): **während der** Reise
- **innerhalb, außerhalb** (içinde, dışında): **innerhalb einer** Woche
- **statt** (yerine): **statt eines** Flugs

Günlük konuşmada wegen ve trotz'u sık sık Dativ ile duyarsınız (wegen dem Wetter). Yazıda Genitiv kullanın.""",
                    "Fırtına yüzünden tren rötarlıydı.; Trafik sıkışıklığına rağmen zamanında vardık.; Yolculuk sırasında kitap okudum.; Bu, kardeşimin bavulu."),
    },
    "b1-gefuehle": {
        "subtitle": "Duygular ve ilişkiler: edatlı fiiller",
        "words": """ilişki; aşk, sevgi; arkadaşlık, dostluk; güven; kıskançlık; kavga, tartışma; düğün; âşık olmak; ayrılmak;
kavga etmek, tartışmak; dört gözle beklemek; -e sevinmek; -e kızmak; -i düşünmek; -e bakmak, ilgilenmek; -i beklemek;
-in hayalini kurmak; kıskanç""",
        "dialogue": """Çok mutlu görünüyorsun! Neye seviniyorsun?
Her şeye! Âşık oldum.
Gerçekten mi? Kime peki?
Tim'e, Jana'nın erkek kardeşine. Sürekli onu düşünüyorum.
Ne güzel! Onun bundan haberi var mı?
Evet, cumartesi buluşuyoruz. Şimdiden dört gözle bekliyorum.
Peki Ben ne olacak? Buna kızmıyor mu?
Biz aylar önce ayrıldık ya. Uzun zamandır yeni bir aşkın hayalini kuruyordum.""",
        "grammar": ("Edatlı fiiller; da- ve wo- sözcükleri", """Pek çok Almanca fiil sabit bir edatla kullanılır ve hali edat belirler. Bunları tek parça olarak öğrenin:

- warten **auf** + Akkusativ: Ich warte **auf den** Bus.
- sich freuen **auf** + Akkusativ (henüz gelecek bir şey): Ich freue mich **auf das** Wochenende.
- sich freuen **über** + Akkusativ (olmuş bir şey): Ich freue mich **über das** Geschenk.
- denken **an** + Akkusativ: Ich denke oft **an meine** Familie.
- sich kümmern **um** + Akkusativ, träumen **von** + Dativ, sprechen **mit** + Dativ

**Şeyler için** edat + ismin yerine **da-** + edat kullanılır (edat ünlüyle başlıyorsa araya bir **r** girer):
- Freust du dich auf den Urlaub? Ja, ich freue mich **darauf**.
- Ärgerst du dich über den Lärm? Ja, ich ärgere mich **darüber**.

**Şeyler hakkında soru sormak için** **wo-** (ünlüden önce wor-) kullanılır: **Worauf** wartest du? **Worüber** sprecht ihr? **Wovon** träumst du?

**Kişiler için** edat kalır ve bir zamir kullanılır: **Auf wen** wartest du? Ich warte **auf ihn**.""",
                    "Ziyaretini dört gözle bekliyorum.; Ne hakkında tartıştınız?; Hasta annesiyle ilgileniyor.; Doğum günümü unutmayacak mısın? Evet, unutmayacağım."),
    },
    "b1-stadtland": {
        "subtitle": "Nerede yaşamalı: iki parçalı bağlaçlar",
        "words": """köy; büyük şehir; bölge, civar; banliyö; doğa; manzara, peyzaj; bağlantı, ulaşım bağlantısı; yaşam kalitesi;
teklif, sunulan olanaklar; yakınlık, civar; avantaj; dezavantaj; sakin, sessiz; canlı, hareketli; yalnız, ıssız;
uygun fiyatlı; çeşitli, renkli""",
        "dialogue": """Şehirde mi kalalım yoksa kırsala mı taşınalım?
Bilmiyorum. Şehir hem kültür hem de iyi işler sunuyor.
Ama buradaki kiralar sadece yüksek değil, aynı zamanda her yıl artıyor.
Doğru. Kırsalda ne gürültü ne de trafik sıkışıklığı olurdu.
Ama orada çoğu zaman ne sinema ne de iyi bir otobüs bağlantısı oluyor.
Bunu ne kadar çok düşünürsem banliyö fikri o kadar hoşuma gidiyor.
İyi fikir. Ya Münih yakınlarında uygun fiyatlı bir şey buluruz ya da burada kalırız.""",
        "grammar": ("İki parçalı bağlaçlar", """Bazı bağlaçlar iki parçadan oluşur ve iki sözcüğü veya iki tam cümleyi bağlar:

- **sowohl ... als auch** (hem ... hem de): Ich mag **sowohl** die Stadt **als auch** das Land.
- **nicht nur ... sondern auch** (sadece ... değil, aynı zamanda): Die Wohnung ist **nicht nur** groß, **sondern auch** günstig.
- **weder ... noch** (ne ... ne de): Im Dorf gibt es **weder** ein Kino **noch** einen Supermarkt.
- **entweder ... oder** (ya ... ya da): **Entweder** wir ziehen um, **oder** wir renovieren.

**weder ... noch** zaten olumsuzdur: yanına asla nicht veya kein eklemeyin.

**je ... desto** (ne kadar ... o kadar) özeldir. **je** bölümü fiili sonda olan bir yan cümledir. **desto**'dan hemen sonra karşılaştırma biçimi, ardından fiil gelir:
- **Je** länger ich hier wohne, **desto** besser gefällt es mir.
- **Je** größer die Stadt ist, **desto** teurer sind die Wohnungen.""",
                    "Köyde hem okul hem de doktor var.; Burada ne gürültü ne de trafik var.; Ya şehirde ya da bir banliyöde oturacağız.; Bölge ne kadar sakin olursa o kadar iyi uyurum."),
    },
    "b1-wahl": {
        "subtitle": "Siyaset ve toplum: Futur I",
        "words": """siyaset, politika; seçim, tercih; oy vermek, seçmek; parti (siyasi); hükümet; parlamento; vatandaş; toplum;
demokrasi; yasa, kanun; vergi; fikir, görüş; gelecek; emekli maaşı; oy, ses; söz vermek; değiştirmek; sosyal""",
        "dialogue": """Pazar günü seçim var. Oy vermeye gidecek misin?
Tabii ki! Her oy önemli.
Maalesef henüz oy kullanamıyorum. Alman pasaportunu ancak gelecek yıl alacağım.
O zaman bir dahaki sefere oy vereceksin! Sence kim kazanacak?
Bence hükümet çoğunluğu kaybedecek. Birçok vatandaş memnun değil.
Bütün partiler vergileri düşüreceklerine söz veriyor.
Gerçekten bir şey değişecek mi acaba? Göreceğiz.""",
        "grammar": ("Futur I: werden + mastar", """Gelecek için Almanca çoğu zaman bir zaman sözcüğüyle birlikte sadece **şimdiki zamanı** kullanır: Morgen **gehe** ich wählen.

**Futur I** tahminler, sözler, kesin planlar ve varsayımlar için kullanılır. **werden** ikinci sıraya, **mastar** sona gelir:
- ich **werde** wählen, du **wirst** wählen, er, sie, es **wird** wählen
- wir **werden** wählen, ihr **werdet** wählen, sie, Sie **werden** wählen

Kullanımlar:
- Tahmin: Die Partei **wird** die Wahl **gewinnen**.
- Söz: Wir **werden** die Steuern **senken**.
- Şimdiye dair varsayım (wohl, sicher, bestimmt ile): Er **wird** wohl krank **sein**.

Yan cümlede werden en sona gider: Sie sagen, dass sie die Steuern senken **werden**.

werden + mastar (gelecek zaman) ile werden + Partizip II'yi (edilgen yapı) karıştırmayın: Ich **werde** fragen. (Soracağım.) Ich **werde** gefragt. (Bana soruluyor.)""",
                    "Hükümet yeni bir yasa çıkaracak.; Gelecek yıl ilk kez oy kullanacağım.; Pek bir şey değişmeyecek.; Muhtemelen çoktan evdedir."),
    },
    "b1-amt": {
        "subtitle": "Resmî dairede: dolaylı sorular",
        "words": """resmî daire, makam; resmî kurum, daire; başvuru (formu), dilekçe; formüler, form; kimlik kartı; pasaport; oturma izni; imza;
ikamet yeri; belge (resmî); son tarih, süre; doldurmak (form); başvurmak (bir şey için); uzatmak; geçerli; teslim etmek;
gerekli""",
        "dialogue": """İyi günler. Oturma iznimi nerede uzatabileceğimi söyleyebilir misiniz?
Burada, bende. Formu doldurdunuz mu?
Evet. Ama işverenimden bir belgeye de ihtiyacım olup olmadığını bilmiyorum.
Evet, o gerekli. Pasaportunuza da ihtiyacım var.
Buyurun. İşlemin ne kadar süreceğini biliyor musunuz?
Yaklaşık dört hafta. Şu anki izniniz o zamana kadar geçerli kalıyor.
Yeni kartı ne zaman alabileceğimi de sorabilir miyim?
Hazır olur olmaz size bir mektup göndereceğiz.""",
        "grammar": ("Dolaylı sorular", """Dolaylı soru, başka bir cümlenin içindeki sorudur. Daha kibar duyulur ve resmî dairelerde çok yaygındır:

- Doğrudan: **Wo** kann ich den Antrag abgeben?
- Dolaylı: Können Sie mir sagen, **wo** ich den Antrag abgeben **kann**?

Soru sözcüğü bir yan cümle başlatır, bu yüzden **fiil sona gider**.

**W-soruları** soru sözcüklerini korur (wo, wann, wie, was, wer, warum, wie lange ...):
- Ich weiß nicht, **wann** das Amt **öffnet**.

**Evet/hayır soruları** **ob** cümlelerine dönüşür (-ıp -madığı):
- Brauche ich einen Termin? → Wissen Sie, **ob** ich einen Termin **brauche**?

Kullanışlı başlangıçlar: **Können Sie mir sagen, ...** / **Wissen Sie, ...** / **Ich möchte wissen, ...** / **Ich weiß nicht, ...** / **Darf ich fragen, ...**

Cümle yalnızca ana bölüm bir soruysa soru işaretiyle biter: Wissen Sie, ob ...? ama Ich weiß nicht, ob ... .""",
                    "Vatandaşlık dairesinin nerede olduğunu söyleyebilir misiniz?; Pasaportumun hâlâ geçerli olup olmadığını bilmiyorum.; Ne kadar beklemem gerektiğini biliyor musunuz?; Başvurunun neden reddedildiğini sorabilir miyim?"),
    },
    "b1-wohnungssuche": {
        "subtitle": "Ev aramak: sıfat ekleri",
        "words": """ilan; ısınma ve aidat hariç kira; kira depozitosu; metrekare; evi görmeye gitme; balkon; ankastre mutfak; kat;
asansör; kalorifer, ısıtma; kira sözleşmesi; konum; eşyalı; yenilenmiş, tadilatlı; merkezî; rahat, sıcak (ortam);
geniş, ferah; (evi) gezip görmek""",
        "dialogue": """Dinle: "Sakin konumda, büyük balkonlu aydınlık daire." Kulağa hoş geliyor, değil mi?
Peki bu güzel daire kaça?
Isınma ve aidat hariç 900 avro. Buna karşılık yeni bir ankastre mutfağı ve yenilenmiş bir banyosu var.
Hmm. Kaçıncı katta?
Dördüncü katta, maalesef asansörsüz.
Bizim ağır kanepemizle mi? Bu uzun bir taşınma olur!
Yine de arayıp evi görmek için randevu isteyeceğim.""",
        "grammar": ("Sıfat ekleri: tam tablo", """İsimden önce gelen bir sıfat ek alır. Hangi eki alacağı, önünde ne olduğuna bağlıdır.

**der, die, das'tan sonra** (ve dieser, jeder, welcher'den sonra) hal zaten artikelde görünür, bu yüzden sıfat yalnızca **-e** veya **-en** alır:
- der hell**e** Raum, die hell**e** Küche, das hell**e** Bad
- bütün çoğullarda, Dativ ve Genitiv'de ve eril Akkusativ'de **-en**: mit dem hell**en** Raum, ich suche den hell**en** Raum

**ein, kein, mein ...'den sonra**: ein'ın ek almadığı yerlerde (eril Nominativ, nötr Nominativ ve Akkusativ) cinsiyeti sıfat gösterir:
- ein groß**er** Balkon, ein groß**es** Bad, eine groß**e** Küche
- diğer her yerde der'den sonrakiyle aynıdır: mit einem groß**en** Balkon

**Artikel yoksa** sıfat, der, die veya das'ın alacağı eki alır (tek istisna: eril ve nötr Genitiv **-en** alır, örneğin trotz schlecht**en** Wetters):
- groß**er** Balkon, groß**e** Küche, groß**es** Bad, mit groß**em** Balkon, in ruhig**er** Lage

Hepsinin arkasındaki kural: cinsiyeti ve hali ya artikel ya da sıfat açıkça gösterir. Artikel göstermiyorsa sıfat göstermek zorundadır.""",
                    "Büyük balkonlu aydınlık bir daire arıyoruz.; Yenilenmiş banyo çok hoşuma gidiyor.; Dairenin küçük bir bodrumu var.; Eski bir binanın üçüncü katında oturuyoruz."),
    },
    "b1-nachrichten": {
        "subtitle": "Haberler ve medya: sıfat olarak ortaçlar",
        "words": """manşet; makale; rapor, haber; haber, bildiri; olay; kaza; itfaiye; anket; araştırma, çalışma; kaynak;
yükselmek, artmak; düşmek, batmak; haber vermek, bildirmek; yayımlamak; güncel; giderek, gittikçe; yaralı""",
        "dialogue": """Gazetede yeni bir şey var mı?
Burada: "Artan kiralar: Birçok aile daha uygun daireler arıyor."
Ne yazık ki bu şaşırtıcı bir haber değil.
Bir de dün bildirilen kazayla ilgili bir haber var. İki yaralı kişi hastaneye kaldırıldı.
Ne korkunç. Duyurulan grevle ilgili de bir şey yazıyor mu?
Evet, duyurulan grev yapılmayacakmış.
İyi! O zaman yarın trenim çalışıyor. Bana güncel hava durumunu da okusana!""",
        "grammar": ("Sıfat olarak ortaçlar", """İki ortaç da bir ismin önünde sıfat gibi durabilir ve olağan sıfat eklerini alır.

**Partizip I**, mastar + **d**'dir: steigen → steigen**d**. Şu anda olmakta olan bir şeyi anlatır (Türkçedeki "-an"):
- die steigend**en** Preise (yükselen fiyatlar: yükselmekte olan fiyatlar)
- ein schlafend**es** Kind (uyuyan bir çocuk)

**Partizip II**, yapılmış veya olmuş bir şeyi anlatır (Türkçedeki "-ılan, -mış"):
- der gemeldet**e** Unfall (bildirilen kaza: bildirilmiş olan kaza)
- die verletzt**en** Personen (yaralı kişiler)
- ein gut renoviert**es** Haus (iyi yenilenmiş bir ev)

Bu biçimler bütün bir ilgi cümlesinin yerini tutar, gazeteler de bu yüzden onları çok sever:
- die Preise, **die steigen** → die **steigenden** Preise
- der Streik, **der angekündigt wurde** → der **angekündigte** Streik

Ortacın önüne başka sözcükler de gelebilir: der **gestern gemeldete** Unfall.""",
                    "Artan fiyatlar büyük bir sorun.; İtfaiye yaralı kişilere yardım etti.; Dün yayımlanan makale çok eleştireldi.; Gülen bir çocuk gördük."),
    },
}


def _pairs():
    """(English, Turkish) for every English text in the B1 lessons, matched by position."""
    for l in LESSONS:
        t = TR[l["id"]]
        yield l["subtitle"], t["subtitle"]
        en_words = [en for _de, en in _items(l["words"])]
        tr_words = [w.strip() for w in t["words"].replace("\n", " ").split(";")]
        en_lines = [r[2] for r in _rows(l["dialogue"])]
        tr_lines = [x.strip() for x in t["dialogue"].strip().splitlines()]
        title, text, examples = l["grammar"]
        tr_title, tr_text, tr_examples = t["grammar"]
        en_ex = [en for _de, en in _items(examples)]
        tr_ex = [x.strip() for x in tr_examples.split(";")]
        if not (len(en_words) == len(tr_words) and len(en_lines) == len(tr_lines) and len(en_ex) == len(tr_ex)):
            raise ValueError(f"Turkish for {l['id']} doesn't line up with the English")
        yield from zip(en_words, tr_words)
        yield from zip(en_lines, tr_lines)
        yield title, tr_title
        yield text, tr_text
        yield from zip(en_ex, tr_ex)


EXACT = dict(_pairs())
