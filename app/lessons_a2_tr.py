"""Turkish for the A2 lessons (app/lessons_a2.py), merged into app/i18n.py like lessons_b1_tr.py.

Written per lesson in the same shape and order as the English, so the two can be read side by side:
words (";"-separated, one per word, in the lesson's order), dialogue (one line per line), grammar (title, text,
examples ";"-separated) and hints (the English hints in brackets at the end of exercises, "English=Turkish").
EXACT below turns them into {English: Turkish} for i18n.tr(); app/lessons.py also uses them lesson by lesson.
German stays German.
"""
from .lessons_a2 import LESSONS
from .lessons_tr import exact

TR = {
    "urlaub": {
        "subtitle": "Tatil anıları: Perfekt'in tamamı",
        "words": """deniz; plaj, kumsal; ada; gezi; bagaj, eşya; bavul; fotoğraf; görülecek yer; gezmek (görülecek yeri); fotoğraf
çekmek; yaşamak, deneyimlemek; geri gelmek; kaybetmek; unutmak; olmak, başına gelmek; doğa yürüyüşü yapmak""",
        "dialogue": """Merhaba Tim! İyice bronzlaşmışsın! Tatil nasıldı?
Süperdi! İki hafta Girit'teydik.
Neler yaptınız?
Bir sürü geziye çıktık ve eski tarihî yerleri gezdik. Bir de dağlarda yürüyüş yaptık.
Her şey yolunda gitti mi?
Neredeyse. İlk gün havayolu şirketi bavulumu kaybetti! Ancak üç gün sonra geldi.
Olamaz! Fotoğraf çektin mi?
Evet, çok fotoğraf çektim. Birazdan sana gösteririm.""",
        "grammar": ('Perfekt: her türlü ortaç', """Perfekt'i zaten biliyorsunuz: ikinci sırada **haben** veya **sein**, sonda ortaç (Partizip). Şimdi özel ortaçlar:

- Ayrılabilen fiillerde **-ge-** ön ekten sonra gelir: einkaufen → ein**ge**kauft, ankommen → an**ge**kommen, zurückkommen → zurück**ge**kommen.
- **be-, ver-, er-, ent-, emp-, ge-, zer-** ile başlayan fiiller **ge- almaz**: besichtigen → besichtigt, verlieren → verloren, vergessen → vergessen, erleben → erlebt.
- **-ieren** ile biten fiiller **ge- almaz**: fotografieren → fotografiert, passieren → passiert.

**sein**, bir yerden başka bir yere hareket (fahren, gehen, fliegen, wandern), değişim (aufstehen, einschlafen) ve **sein, bleiben, passieren** fiilleri için kullanılır: Was **ist** passiert? Wir **sind** in Spanien gewesen.""",
                    'Eski şehri gezdik.; Anahtarımı unuttum.; Tren zamanında vardı.; Ne oldu?'),
    },
    "frueher": {
        "subtitle": 'Çocukluk anıları: war ve hatte',
        "words": """çocukluk; köy; bahçe; oyuncak; büyükanne; büyükbaba; evcil hayvan; köpek; kedi; eskiden; o zamanlar; sert, katı;
mutlu; utangaç; yaramaz, arsız; anlatmak""",
        "dialogue": """Babaanne, çocukluğun nasıldı?
Güzeldi ama bugünkünden çok farklıydı. Çok paramız yoktu.
O zamanlar nerede oturuyordun?
Küçük bir köyde. Büyük bir bahçemiz ve bir köpeğimiz vardı.
Çok oyuncağın var mıydı?
Hayır, sadece bir bebeğim vardı. Ama çoğu zaman dışarıdaydım ve çok mutluydum.
Okul zor muydu?
Hayır, ama öğretmenimiz çok sertti!""",
        "grammar": ("war ve hatte: sein ve haben'ın Präteritum'u", """**sein** ve **haben** için Almanlar genellikle Perfekt değil **Präteritum** (di'li geçmiş) kullanır. "Ich war", "ich bin gewesen"den daha kısa ve daha yaygındır.

- sein: ich **war**, du **warst**, er/sie/es **war**, wir **waren**, ihr **wart**, sie/Sie **waren**
- haben: ich **hatte**, du **hattest**, er/sie/es **hatte**, wir **hatten**, ihr **hattet**, sie/Sie **hatten**

ich ve er/sie/es aynı biçimdedir. Konuşurken diğer fiillerin çoğu Perfekt'te kalır: Ich **war** müde und **habe** früh **geschlafen**.""",
                    'Eskiden çok utangaçtım.; Bir kedimiz vardı.; Dün neredeydin?; Vaktiniz var mıydı? (birkaç kişiye)'),
    },
    "schulzeit": {
        "subtitle": 'Okul ve meslek eğitimi: geçmişte modal fiiller',
        "words": """sınav; karne, belge; not; ders (konu); sınıf; ev ödevi; meslek eğitimi, çıraklık; üniversite; lise bitirme
sınavı (üniversiteye giriş); ders (sınıfta); teneffüs, mola; geçmek (sınavı); -ebilmek (izinli olmak); -meli
(başkası istiyor)""",
        "dialogue": """Okulda en sevdiğin ders hangisiydi?
Matematik! Ama Almancam pek iyi değildi.
Çok ödev yapmak zorunda mıydınız?
Evet, her gün. Bir de derste telefonla oynamamıza izin yoktu.
Ben okuldan hemen sonra çalışmak istedim ve meslek eğitimi aldım.
Benim üniversiteye gitmem gerekiyordu ama istemedim. Annemle babam hiç mutlu değildi!""",
        "grammar": ('Geçmişte modal fiiller: konnte, musste, wollte', """Modal fiiller de sein ve haben gibi geçmiş için **Präteritum** kullanır. Mastarın umlautunu kaldırın, **-en**'i atın ve **-te** ekleyin:

- können → ich **konnte**, müssen → ich **musste**, dürfen → ich **durfte**
- wollen → ich **wollte**, sollen → ich **sollte**, mögen → ich **mochte** (g → ch)

Ekler: ich konnte, du konnte**st**, er/sie konnte, wir konnte**n**, ihr konnte**t**, sie/Sie konnte**n**.

Şimdiki zamanda olduğu gibi ikinci fiil sona gider: Ich **musste** viel **lernen**.

**dürfen** "izni olmak", **sollen** "-mesi gerekmek (başkası öyle istiyor)" demektir.""",
                    'Çocukken yüzemiyordum.; Her gün ödev yapmak zorundaydık.; Akşamları dışarı çıkmama izin yoktu.; Doktor olmak istiyordu.'),
    },
    "geschenke": {
        "subtitle": 'Kutlamalar, hediyeler ve Dativ',
        "words": """hediye; bayram, kutlama; düğün; Noel; Paskalya; davet; çiçek; mum; yaş pasta; hediye etmek; vermek; göstermek;
getirmek, götürmek; tebrik etmek; Tebrikler! İyi ki doğdun!; Mutlu Noeller!""",
        "dialogue": """Gelecek hafta annemin doğum günü. Ona ne hediye etsem?
Ona çiçek al. Ya da güzel bir mum.
Çiçeği geçen yıl zaten benden aldı.
Peki bir kitap? Okumayı seviyor, değil mi?
İyi fikir! Babama da bir pasta alacağım. Pastaya bayılır.
Onun da mı doğum günü?
Hayır, ama ona da bir şey götüreceğim. Yoksa üzülür!""",
        "grammar": ('Kim alıyor? Dativ nesnesi', """**geben, schenken, zeigen, bringen, kaufen** gibi fiillerin çoğu zaman iki nesnesi vardır: şey (**Akkusativ**) ve onu alan kişi (**Dativ**).

Ich schenke **meiner Mutter** (Dativ) **ein Buch** (Akkusativ).

Dativ artikelleri: der / das → **dem, einem, meinem**; die → **der, einer, meiner**; çoğul → **den, meinen** ve isim -n alır: Ich gebe **dem** Kind einen Apfel. Ich zeige **den Kindern** das Foto.

Dativ zamirleri: ich → **mir**, du → **dir**, er / es → **ihm**, sie → **ihr**, wir → **uns**, ihr → **euch**, sie → **ihnen**, Sie → **Ihnen**.

Kişi genellikle şeyden önce gelir: Ich gebe **dir** das Buch.""",
                    'Erkek kardeşime bir tişört hediye ediyorum.; Bana fotoğrafı gösterebilir misin?; Ona çiçek götürüyoruz.; Çocuklara çikolata veriyor.'),
        "hints": 'my=benim; your=senin; you, informal=sen; her=o (kadın); him=o (erkek)',
    },
    "restaurant": {
        "subtitle": 'Restoranda: Dativ alan fiiller',
        "words": """yemek listesi, menü; başlangıç, meze; ana yemek; tatlı; içecek; bıçak; çatal; kaşık; bahşiş; tadı (güzel) olmak;
hoşuna gitmek; ait olmak; yardım etmek; tavsiye etmek; sipariş etmek; lezzetli; acı (yemek), keskin""",
        "dialogue": """İyi akşamlar! Buyurun menü. Şimdiden bir içecek getireyim mi?
Evet, iki su, lütfen. Bize ne tavsiye edersiniz?
Balık bugün çok güzel. Tatlı olarak da elmalı pastayı tavsiye ederim.
Yemeğiniz nasıl, beğendiniz mi?
Evet, çok lezzetli! Sadece sos bana biraz acı geldi.
Restoran hoşuma gitti. Sizin mi?
Hayır, amcamın. Ben sadece hafta sonları ona yardım ediyorum.""",
        "grammar": ('Dativ alan fiiller: gefallen, schmecken, helfen', """Sık kullanılan bazı fiiller Akkusativ değil **Dativ** nesne alır:

- **helfen**: Ich helfe **dir**. (dich değil)
- **danken**: Wir danken **Ihnen**.
- **gefallen**: Das Bild gefällt **mir**. (Resim hoşuma gidiyor.)
- **schmecken**: Schmeckt **dir** die Suppe? (Çorbayı beğendin mi?)
- **gehören**: Das Auto gehört **meinem** Vater. (ait olmak)
- **passen**: Die Hose passt **mir** nicht. (bana olmuyor)
- **antworten**: Er antwortet **ihr**.

gefallen ve schmecken ile beğenilen şey **öznedir**, bu yüzden fiil ona uyar: Die Schuhe gefall**en** mir.""",
                    'Çorbayı beğendim.; Şehri nasıl buldun?; Bana yardım edebilir misin?; Kitap kız kardeşime ait.'),
        "hints": 'me=ben; him=o (erkek); you, informal=sen; my=benim; you, formal=siz',
    },
    "nachbarn": {
        "subtitle": 'Mahalle: aus, bei, mit, nach, seit, von, zu',
        "words": """komşu (erkek); komşu (kadın); semt, mahalle; çevre, bölge; avlu; merdiven boşluğu; kat; asansör; kapıcı;
karşısında; -den beri; tanışmak, tanımak; taşınmak (yeni eve); sakin, sessiz; gürültülü, yüksek sesli; güler
yüzlü, nazik""",
        "dialogue": """Merhaba! Buraya yeni mi geldiniz?
Evet, bir hafta önce taşındım. Üçüncü katta oturuyorum.
Ben on yıldır burada oturuyorum, asansörün karşısında. Nerelisiniz?
Leipzigliyim. Şimdi istasyonun yakınındaki bir şirkette çalışıyorum.
Bu çevre çok sakin. Kapıcı da çok güler yüzlü.
Ne güzel. Şimdi bisikletle işe gidiyorum. Görüşmek üzere!
Pazar günü bana kahveye gelsenize! O zaman tanışırız.""",
        "grammar": ('Dativ alan edatlar', """Bu edatlar **her zaman** Dativ alır: **aus, bei, mit, nach, seit, von, zu** ve **gegenüber**.

- **aus** (-den, içinden): Ich komme **aus der** Schweiz.
- **bei** (birinin yanında, bir şirkette): Ich wohne **bei meinen** Eltern. Er arbeitet **bei einer** Firma.
- **mit** (ile): **mit dem** Fahrrad
- **nach** (şehre, ülkeye; sonra): **nach dem** Essen
- **seit** (-den beri): **seit einem** Jahr, **seit zehn** Jahren
- **von** (-den, -in): **vom** Arzt, ein Freund **von mir**
- **zu** (kişilere ve yerlere): **zu mir**, **zum** Kaffee
- **gegenüber** (karşısında): **gegenüber vom** Aufzug

**seit** şimdiki zamanla kullanılır: Ich wohne **seit** zwei Jahren hier. (İki yıldır burada oturuyorum.)""",
                    "Bir aydır Hamburg'da oturuyorum.; Bir bankada çalışıyor.; Yemekten sonra kahve içiyoruz.; Bugün bana geliyor musun?"),
    },
    "verkehr": {
        "subtitle": 'Şehrin içinden: durch, für, gegen, ohne, um',
        "words": """trafik; trafik sıkışıklığı; köprü; yol; köşe; kaza; ehliyet; bisiklet yolu; belediye binası; kask; içinden, -den
geçerek; -e karşı, -e (çarpmak); etrafında; boyunca; park etmek; dikkatli; tehlikeli""",
        "dialogue": """Affedersiniz, belediye binasına nasıl gidebilirim?
Arabayla mı? Orada bugün trafik sıkışık. Köprüde bir kaza oldu.
Hayır, bisikletliyim.
O zaman parkın içinden ve nehir boyunca gidin. Orası güzel bir bisiklet yolu.
Sonra?
Pazar meydanının etrafından dolaşın. Belediye binası köşede. Ama dikkatli olun! Kasksız tehlikeli.
Yardımınız için çok teşekkürler!""",
        "grammar": ('Akkusativ alan edatlar', """Bu edatlar **her zaman** Akkusativ alır: **durch, für, gegen, ohne, um** (ve **bis**).

- **durch** (içinden): **durch den** Park
- **für** (için): ein Geschenk **für meinen** Vater, Danke **für die** Hilfe
- **gegen** (karşı, -e çarpmak): Er ist **gegen einen** Baum gefahren.
- **ohne** (-sız, olmadan): **ohne den** Helm, **ohne mich**
- **um** (etrafında; saat ...'de): **um den** Platz herum, **um** acht Uhr

Akkusativ'de yalnızca der kelimeleri değişir: der → **den**, ein → **einen**. Zamirler: mich, dich, ihn, sie, es, uns, euch, sie, Sie.

**entlang** genellikle isimden sonra gelir: **den** Fluss **entlang**.""",
                    'Şehrin içinden yürüyoruz.; Hediye senin için.; Kasksız asla bisiklete binmem.; Araba duvara çarptı.'),
        "hints": 'you, informal=sen; his=onun (erkek); me=ben',
    },
    "umzug": {
        "subtitle": 'Taşınma: wo? mu, wohin? mi; iki hâlli edatlar',
        "words": """taşınma; kutu, sandık; mobilya; halı; ayna; bodrum; koridor, hol; buzdolabı; koymak (dik); koymak (yatırarak);
asmak; taşımak; (kutudan) çıkarmak, açmak; ağır, zor; hafif, kolay; üstünde, üzerine""",
        "dialogue": """Kanepeyi nereye koyayım?
Duvara daya, pencerenin yanına.
Ya halı? Nereye serilsin?
Kanepenin önüne ser. Aynayı da koridora asalım.
Kitap kutuları çok ağır! Bunları nereye koyalım?
Bodruma. Kitapları yarın çıkarırız.
Tamam. Peki kahve nerede? Bir molaya ihtiyacım var!
Mutfakta, masanın üstünde.""",
        "grammar": ('Wo? mu, wohin? mi? İki hâlli edatlar', """**in, an, auf, unter, über, vor, hinter, neben, zwischen** edatları iki hâl alabilir:

- **Wo?** (nerede: bir yer) → **Dativ**: Das Bild hängt **an der** Wand. Der Teppich liegt **vor dem** Sofa.
- **Wohin?** (nereye: bir hareket) → **Akkusativ**: Ich hänge das Bild **an die** Wand. Ich lege den Teppich **vor das** Sofa.

Fiiller çift olarak gelir:

- **stellen** (dik koymak) → **stehen** (dik durmak): Ich stelle die Lampe **auf den** Tisch. Die Lampe steht **auf dem** Tisch.
- **legen** (yatırarak koymak) → **liegen** (yatay durmak): Ich lege das Buch **ins** Regal. Das Buch liegt **im** Regal.
- **hängen** (asmak) → **hängen** (asılı olmak)

Kısaltmalar: in das → **ins**, an das → **ans**.""",
                    'Şişeyi buzdolabına koyuyorum.; Şişe buzdolabında.; Telefonu masanın üstüne koyuyor.; Lambayı masanın üstüne asıyoruz.'),
    },
    "mode": {
        "subtitle": "Moda: der, die, das'tan sonra sıfat ekleri",
        "words": """palto; bere, şapka; atkı; eldiven; çizme; bluz; takım elbise; kravat; tişört; moda; rahat; dar; şık; modern;
çirkin; giymek, takmak; giymek, üstüne giymek""",
        "dialogue": """Mavi paltoyu nasıl buldun?
Mavi palto güzel. Ama siyahı da hoşuna gidiyor mu?
Hayır, o çok dar. Maviyi alıyorum.
Sıcak eldivenlere de ihtiyacın var mı?
Evet, kışın hep eldiven takarım. Buradaki kırmızı bere de çok tatlı.
Kırmızı bere yeni paltoya çok yakışıyor!
Doğru. Hemen takıyorum!""",
        "grammar": ("der, die, das'tan sonra sıfat ekleri", """İsimden **önce** gelen sıfat ek alır. **der, die, das** (ve dieser, welcher) sonrasında ek ya **-e** ya **-en** olur:

- Yalın hâl tekilde **-e**: **der** blau**e** Mantel, **die** rot**e** Mütze, **das** neu**e** Kleid; die ve das kelimelerinin Akkusativ'inde de: Ich nehme **die** rot**e** Mütze und **das** neu**e** Kleid.
- Diğer her yerde **-en**: Ich nehme **den** blau**en** Mantel (der kelimesi, Akkusativ), mit **dem** neu**en** Mantel (Dativ), **die** warm**en** Handschuhe (çoğul).

sein fiilinden sonra ek yoktur: Der Mantel ist **blau**.""",
                    'Siyah takım elbise şık.; Yeşil atkıyı alıyorum.; Beyaz bluz çok dar.; Yeni çizmeleri giyiyor.'),
    },
    "wohnungssuche": {
        "subtitle": "Ev arama: ein, kein, mein'dan sonra sıfat ekleri",
        "words": """kira; ilan; ev sahibi; ek giderler (ısınma, su); depozito; balkon; kalorifer, ısıtma; metrekare; konum; zemin
kat; evi görme randevusu; kiralamak; eşyalı; merkezî; uygun fiyatlı""",
        "dialogue": """Yeni bir ev buldun mu?
Belki. İlginç bir ilan okudum: büyük balkonlu, aydınlık, iki odalı bir daire.
Kulağa hoş geliyor! Kira ne kadar?
750 avro artı ek giderler. Merkezî bir konum için uygun.
Eşyalı mı?
Hayır, ama yeni bir mutfağı ve güzel bir ahşap zemini var.
Evi görmeye ne zaman gidiyorsun?
Yarın saat beşte. Ev sahibi güler yüzlü bir adam galiba.""",
        "grammar": ("ein, kein, mein'dan sonra sıfat ekleri", """**ein, kein** ve **mein, dein, sein...** sonrasında artikelin gösteremediği cinsiyeti sıfat gösterir:

- der kelimesi: **ein** groß**er** Balkon (yalın hâl), **einen** groß**en** Balkon (Akkusativ)
- das kelimesi: **ein** hell**es** Zimmer (yalın hâl ve Akkusativ)
- die kelimesi: **eine** neu**e** Küche (yalın hâl ve Akkusativ)
- Dativ, bütün cinsiyetler: **-en**: mit **einem** groß**en** Balkon, in **einer** ruhig**en** Straße
- keine / meine ile çoğul: **-en**: **meine** neu**en** Nachbarn

İpucu: ein, der ve das kelimelerinde aynı görünür; bu yüzden sıfat bunu netleştirmek için **-er** (der) veya **-es** (das) alır.""",
                    'Bu güzel bir balkon.; Uygun fiyatlı bir daire arıyoruz.; Aydınlık bir odası var.; Küçük bir evde oturuyorum.'),
    },
    "vergleich": {
        "subtitle": 'Karşılaştırma: größer als, so groß wie, am größten',
        "words": """doğa; hava (solunan); gürültü; kültür; seçenekler, teklif; avantaj; dezavantaj; büyükşehir; kırsalda, köyde;
temiz; kirli; heyecanlı, ilginç; yüksek; -den (daha); kadar (so ... wie); tercihen, daha çok (severek); daha
iyi; daha çok""",
        "dialogue": """Şehirde mi yaşamayı tercih edersin, kırsalda mı?
Şehirde! Kültürel seçenekler kırsaldakinden çok daha fazla.
Ama kırsalda hava daha temiz ve daha az gürültü var.
Doğru. Ama şehirde her şey daha yakın: iş, sinemalar, arkadaşlar.
Benim için en önemlisi doğa. Yakında küçük bir köye taşınıyorum.
Bir köy Berlin kadar heyecanlı değil! Ama seni seve seve ziyaret ederim.""",
        "grammar": ('Karşılaştırma: -er als, so ... wie, am -sten', """Karşılaştırmak için sıfata **-er** ekleyin ve **als** (-den) kullanın: Die Stadt ist laut**er** **als** das Dorf.

Eşitlik: **so** + sıfat + **wie** (kadar): Ein Dorf ist nicht **so** spannend **wie** Berlin.

En üstünlük: **am** + sıfat + **-sten**: Die Natur ist mir **am** wichtig**sten**.

Kısa sıfatların çoğu umlaut alır: groß → gr**ö**ßer → am gr**ö**ßten, alt → **ä**lter → am **ä**ltesten, warm → w**ä**rmer, jung → j**ü**nger, kalt → k**ä**lter.

Düzensizler: gut → **besser** → am **besten**; viel → **mehr** → am **meisten**; gern → **lieber** → am **liebsten**; hoch → **höher** → am **höchsten**.

-t, -d, -s, -ß ve -z'den sonra -sten'den önce -e- eklenir: am ält**e**sten, am heiß**e**sten. İstisna: am **größten**.""",
                    "Erkek kardeşim benden büyük.; Berlin Hamburg'dan büyük.; Çayı kahveye tercih ederim.; En sıcak temmuzda olur."),
        "hints": 'old=yaşlı',
    },
    "morgens": {
        "subtitle": 'Günlük düzen: dönüşlü fiiller',
        "words": """yıkanmak; duş almak; giyinmek; saçını taramak; tıraş olmak; makyaj yapmak; acele etmek; sevinmek; dinlenmek;
(kendini) hissetmek; gündelik hayat; çalar saat; diş fırçası; havlu; sabun; yorgun""",
        "dialogue": """Neden hâlâ hazır değilsin? Çıkmamız lazım!
Özür dilerim! Çalar saatim çalmadı. Daha giyinmem lazım.
Lütfen acele et! Duş aldın mı?
Evet, ama daha saçımı tarayıp makyaj yapmam lazım.
Banyoda hep bir saat geçiriyorsun!
Sen de hiç tıraş olmuyorsun! Tamam, hazırım. Gezi için çok heyecanlıyım!""",
        "grammar": ('Dönüşlü fiiller: sich waschen', """Dönüşlü fiillerde özneye geri dönen bir zamir vardır, Türkçedeki "kendini" gibi. Almancada pek çok gündelik fiil dönüşlüdür:

- ich wasche **mich**
- du wäschst **dich**
- er / sie / es wäscht **sich**
- wir waschen **uns**
- ihr wascht **euch**
- sie / Sie waschen **sich**

Yalnızca er / sie / es ve sie / Sie **sich** kullanır; diğerleri normal Akkusativ zamirlerini kullanır.

Zamir fiilin hemen arkasına gelir: Ich **ziehe mich** an. Sorularda ve zaman kelimesinden sonra öznenin arkasına gelir: Wann **duschst du dich**? Morgens **rasiert er sich**.

Perfekt'te dönüşlü fiiller **haben** alır: Ich **habe mich** beeilt.""",
                    'Her sabah duş alırım.; Acele et!; Seviniyoruz.; Hızlıca giyindi.'),
        "hints": 'his own=kendi',
    },
    "interessen": {
        "subtitle": 'Edatlı fiiller: warten auf, sich interessieren für',
        "words": """kulüp, dernek; takım; oyun, maç; antrenman; gol, kapı; şampiyona; kazanmak; antrenman yapmak; -e ilgi duymak; -i
beklemek; -i dört gözle beklemek; -e kızmak; -i düşünmek; -in hayalini kurmak; -e katılmak""",
        "dialogue": """Futbolla ilgileniyor musun?
Evet, çok! Hatta bir kulüpteyim. Haftada iki kez antrenman yapıyoruz.
Harika! Bir şampiyonada da oynuyor musunuz?
Evet. Cumartesi önemli bir maçımız var. Şimdiden dört gözle bekliyorum!
Ben hep takımıma kızıyorum. Neredeyse her maçı kaybediyor.
Cumartesi bizim maçımıza gelsene! Seni girişte beklerim.
Seve seve! Sana şans dilerim.""",
        "grammar": ('Sabit edatlı fiiller', """Pek çok Almanca fiil **sabit bir edatla** kullanılır ve bu edat çoğu zaman beklediğiniz edat değildir. Bunları hâliyle birlikte tek parça olarak öğrenin:

- **warten auf** + Akkusativ: Ich warte **auf den** Bus.
- **sich freuen auf** + Akkusativ (dört gözle beklemek): Ich freue mich **auf das** Wochenende.
- **sich interessieren für** + Akkusativ: Er interessiert sich **für** Musik.
- **sich ärgern über** + Akkusativ: Sie ärgert sich **über den** Lärm.
- **denken an** + Akkusativ: Ich denke **an dich**.
- **träumen von** + Dativ: Er träumt **von einem** Haus am Meer.
- **teilnehmen an** + Dativ: Wir nehmen **an einem** Kurs teil.

Şeyler için **da-** + edat kullanılır: Ich freue mich **darauf**. Sorularda **wo-** kullanılır: **Worauf** wartest du? **Wofür** interessierst du dich? Ünlüden önce -r- eklenir: d**ar**auf, w**or**an.""",
                    'Treni bekliyoruz.; Siyasetle ilgileniyorum.; Tatili dört gözle bekliyor.; Ne düşünüyorsun?'),
    },
    "umwelt": {
        "subtitle": 'Sebep bildirme: denn, deshalb, trotzdem',
        "words": """çevre; çöp; şişe; plastik; enerji; elektrik; iklim; orman; nehir; hayvan; bitki; korumak; tasarruf etmek,
biriktirmek; ayırmak; atmak (çöpe); çünkü; bu yüzden; yine de""",
        "dialogue": """Çöpü neden bu kadar dikkatle ayırıyorsun?
Çevreyi korumak istiyorum, çünkü plastik denizdeki hayvanlar için çok tehlikeli.
Doğru. Bu yüzden artık plastik şişe almıyorum.
Ben de bisiklete biniyorum, çünkü böylece enerjiden ve paradan tasarruf ediyorum.
Arabam yok. Yine de tatile sık sık uçakla gidiyorum. Bu iklim için pek iyi değil.
Belki bir dahaki sefere trenle gidersin?""",
        "grammar": ('denn, deshalb, trotzdem', """Sebep ve sonuç için iki tür bağlaç vardır.

**denn** (çünkü) kelime sırasını **değiştirmez**. İki cümlenin arasında durur ve fiil ikinci sırada kalır: Ich fahre Rad, **denn** ich **spare** so Geld. **und, aber, oder** de böyledir.

**deshalb** (bu yüzden) ve **trotzdem** (yine de) ikinci cümlenin bir parçasıdır. Başa geldiklerinde fiil **hemen arkalarından** gelir ve özne fiilin arkasına geçer:

- Plastik ist gefährlich. **Deshalb kaufe ich** keine Plastikflaschen.
- Es regnet. **Trotzdem gehe ich** spazieren.

Fiilden sonra da gelebilirler: Ich kaufe **deshalb** keine Plastikflaschen.""",
                    'Evde kalıyorum, çünkü hastayım.; Hastayım. Bu yüzden evde kalıyorum.; Hava soğuk. Yine de gölde yüzüyoruz.; Çöpü ayırıyoruz, çünkü bu çevre için iyi.'),
    },
    "gesundheit": {
        "subtitle": 'Sağlık ve alışkanlıklar: weil ile sebep bildirme',
        "words": """sağlık; beslenme; sebze; meyve; şeker; hareket, egzersiz; kilo, ağırlık; stres; sigara içmek; kilo vermek; kilo
almak; hareket etmek, spor yapmak; koşu yapmak; formda; sağlıksız; düzenli, düzenli olarak; çünkü (yan cümle)""",
        "dialogue": """Bay Wagner, bugün neden buradasınız?
Sık sık yorgun oluyorum, çünkü işte çok stresim var.
Düzenli olarak hareket ediyor musunuz?
Yeterince değil. İşe arabayla gidiyorum, çünkü daha hızlı.
Ya beslenmeniz? Bol meyve ve sebze yiyor musunuz?
Maalesef hayır. Ofiste sık sık tatlı yiyorum, çünkü öğle yemeğine vaktim yok.
O zaman öğle arasında yürüyüşe çıkın. Strese iyi gelir.""",
        "grammar": ('weil: fiil sona gider', """**weil** (çünkü) bir **yan cümle** başlatır. Yan cümlede çekimli fiil **en sona** gider:

- Ich bin müde. Ich **habe** viel Stress. → Ich bin müde, **weil** ich viel Stress **habe**.
- Modal fiil varsa modal en sona gelir: ..., weil ich früh aufstehen **muss**.
- Perfekt'te haben veya sein en sona gelir: ..., weil ich schlecht geschlafen **habe**.
- Ayrılabilen fiiller yeniden birleşir: ..., weil ich jeden Tag um sechs Uhr **aufstehe**.

weil'den önce her zaman **virgül** konur. **Warum?** diye sorulur, **Weil ...** diye cevap verilir.

Karşılaştırın: **denn** normal kelime sırasını korur: ..., denn ich habe viel Stress.""",
                    'Koşuyorum, çünkü formda kalmak istiyorum.; Artık sigara içmiyor, çünkü sağlıksız.; Et yemiyor, çünkü hayvanları seviyor.; Neden gelmedin? – Çünkü hastaydım.'),
    },
    "arbeit": {
        "subtitle": "İş ve iş arkadaşları: dass'lı yan cümleler",
        "words": """iş arkadaşı (erkek); iş arkadaşı (kadın); patron, şef (erkek); patron, şef (kadın); toplantı; sözleşme; maaş; iş
başvurusu; iş, pozisyon; fazla mesai saati; istifa etmek, işten çıkmak; başvurmak (işe); inanmak, sanmak; ummak;
bilmek (bir bilgiyi); -dığını, ki""",
        "dialogue": """Bay Schulz'un istifa ettiğini duydun mu?
Hayır! Memnun olmadığını bilmiyordum.
Çok fazla mesai yaptığını söylüyor. Maaş da pek iyi değil.
Bence haklı. Yeni bir işi var mı?
Evet, Hamburg'da bir şirkete başvurdu ve sözleşmeyi bile imzaladı.
O zaman umarım şef yakında yeni birini bulur. Şimdiden çok fazla işimiz var!""",
        "grammar": ('dass: söylenen, düşünülen ve bilinen', """**dass** (-dığını, ki) birinin söylediğini, düşündüğünü, bildiğini veya umduğunu aktarır. weil gibi fiili **sona** gönderir:

- Er kündigt. → Ich weiß, **dass** er **kündigt**.
- Sie hat recht. → Ich glaube, **dass** sie recht **hat**.
- Er hat sich beworben. → Sie sagt, **dass** er sich beworben **hat**.

dass'tan önce sık gelen fiiller: **sagen, glauben, denken, wissen, hoffen, finden, hören** ve **Es ist wichtig / schön, dass ...**

dass'tan önce virgül konur. Konuşmada dass çoğu zaman düşer; o zaman fiil ikinci sırada kalır: Ich glaube, er **hat** recht.

Yazım: **das** (artikel, "o") tek s ile, **dass** (iki cümleyi bağlayan) iki s ile yazılır.""",
                    'Çok çalıştığını biliyorum.; İşi alacağını umuyor.; Toplantının saat onda olduğunu söylüyor.; Zamanında olmamız önemli.'),
    },
    "reise": {
        "subtitle": 'Seyahat planları ve koşullar: wenn',
        "words": """uçak; havalimanı; uçuş; çadır; kamp yeri; konaklama yeri; çift kişilik oda; tek kişilik oda; pasaport; kimlik
kartı; yurt dışı; rezervasyon yapmak; ayırtmak; geceyi geçirmek, konaklamak; uçmak, uçakla gitmek; eğer,
-dığında""",
        "dialogue": """Yazın nereye gidiyoruz?
Yeterince paramız olursa Portekiz'e uçarız.
Ya uçuşlar çok pahalıysa?
O zaman trenle Baltık Denizi'ne gider, bir kamp yerinde kalırız.
Çadırda mı? Ancak yağmur yağmazsa!
Tamam, o zaman bir konaklama yeri ayırtırız. Bu akşam vaktim olunca internete bakarım.
Süper. Bir de unutma: Portekiz için pasaportuna ya da kimlik kartına ihtiyacın var!""",
        "grammar": ('wenn: eğer ve -dığında', """**wenn**, **eğer** (koşul) veya **-dığında / her ... -dığında** (şimdiki ya da gelecek zamanda) demektir. Yan cümle başlatır, bu yüzden fiil **sona** gider: **Wenn** das Wetter schön **ist**, gehen wir an den Strand.

wenn'li cümle **önce** gelirse ana cümle **fiiliyle** başlar: **Wenn** ich Zeit habe, **buche** ich das Hotel. (fiil, virgül, fiil)

Ana cümle önce gelirse kelime sırası normaldir: Ich buche das Hotel, **wenn** ich Zeit **habe**.

Ana cümle **dann** ile de başlayabilir: Wenn es regnet, **dann bleiben** wir zu Hause.""",
                    'Tatile çıktığımda denize giderim.; Hava sıcak olursa çadırda kalırız.; Uçuş ucuzsa hemen ayırtırız.; Yağmur yağarsa ne yaparsın?'),
    },
    "medien": {
        "subtitle": 'Telefon, internet ve haberler: ob ve dolaylı sorular',
        "words": """mesaj, haber; haberler; gazete; dergi; televizyon; program, yayın; internet; bilgisayar; şifre, parola; e-posta;
uygulama; indirmek; kaydetmek; göndermek; televizyon izlemek; çalışmak (cihaz); -ip -mediğini""",
        "dialogue": """Bana yardım edebilir misin? Bu uygulamanın nasıl çalıştığını bilmiyorum.
Tabii, dede. Ne yapmak istiyorsun?
Burada haberleri okuyup okuyamayacağımı öğrenmek istiyorum. Artık gazete okumuyorum da.
Evet, olur. Ama önce uygulamayı indirmen gerekiyor. Şifren nerede, biliyor musun?
Bir kâğıda yazdım. Ama kâğıdın nerede olduğunu artık bilmiyorum!
Sorun değil. Anneme biliyor mu diye sorarım.""",
        "grammar": ('Dolaylı sorular: ob, wo, wann, wie', """Başka bir cümlenin içindeki soruya **dolaylı soru** denir. Yan cümledir, bu yüzden fiil **sona** gider.

- Evet/hayır soruları **ob** ile kurulur (-ip -mediğini): Kommt er? → Ich weiß nicht, **ob** er **kommt**.
- Soru kelimeli sorular soru kelimesini korur: Wo ist das Passwort? → Weißt du, **wo** das Passwort **ist**?

Sık kullanılan başlangıçlar: **Ich weiß nicht, ...** / **Weißt du, ...?** / **Ich frage, ...** / **Können Sie mir sagen, ...?** (kibar bir soru biçimi).

Dikkat: koşul bildiren "eğer" için **wenn**, "-ip -mediğini" için **ob** kullanılır: Ich frage, **ob** du Zeit hast.""",
                    'Uygulamanın ücretsiz olup olmadığını bilmiyorum.; Programın ne zaman başladığını söyleyebilir misiniz?; Bunun nasıl çalıştığını biliyor musun?; Bu akşam televizyon izleyip izlemeyeceğimizi soruyor.'),
    },
    "amt": {
        "subtitle": 'Resmî daireler ve hizmetler: hätte, könnte, würde ile kibar ricalar',
        "words": """resmî daire; form; kayıt, ikamet kaydı; imza; banka hesabı; başvuru (formu); harç, ücret; sıra numarası; çalışma
saatleri; doldurmak (form); imzalamak; başvurmak (bir şey için); açıklamak; tekrarlamak; acil; kibar""",
        "dialogue": """Günaydın. İkamet kaydı için bir randevu almak istiyorum.
Sıra numaranız var mı?
Evet, buyurun. Hangi belgelere ihtiyacım olduğunu açıklayabilir misiniz, lütfen?
Kimlik kartınız ve kira sözleşmeniz. Bir de bu formu doldurmanız gerekiyor.
Bana yardım eder misiniz? Bütün kelimeleri anlamıyorum.
Tabii. Buraya adresinizi yazıyorsunuz, aşağıda da imzanız gerekiyor.
Çok teşekkür ederim, çok naziksiniz!""",
        "grammar": ('Kibar ricalar: hätte, könnte, würde', """Kibarca rica etmek için Almanca **Konjunktiv II** (dilek-şart biçimleri) kullanır:

- **hätte gern** (almak isterdim): Ich **hätte gern** einen Termin.
- **könnte** (-ebilirdi): **Könnten** Sie mir helfen?
- **würde** + mastar (-erdi): **Würden** Sie das bitte wiederholen?

Biçimler: ich hätte, du hättest, er/sie hätte, wir hätten, Sie hätten. ich könnte, du könntest, er/sie könnte, wir könnten, Sie könnten. ich würde, du würdest, er/sie würde, wir würden, Sie würden.

Modal fiillerde olduğu gibi mastar sona gider: **Könnten** Sie mir das Formular **erklären**?

**bitte** ile rica çok kibar olur: Würden Sie bitte hier unterschreiben?""",
                    'Bir form almak istiyorum.; Bunu açıklayabilir misiniz, lütfen?; Lütfen daha yavaş konuşur musunuz?; Bir hesap açabilir miyim?'),
    },
    "lebenslauf": {
        "subtitle": 'Hayat hikâyeniz: vor, seit, nach, ab, von ... bis',
        "words": """özgeçmiş; deneyim; staj; diploma, mezuniyet; üniversite öğrenimi; dil; kurs; doğmuş; büyümek; evlenmek;
başlamak; bitirmek; önce, önünde; -den itibaren; -e kadar""",
        "dialogue": """Lütfen bize biraz kendinizden bahsedin.
Tabii. 1995'te İzmir'de doğdum ve orada büyüdüm.
Ne zamandan beri Almanya'da yaşıyorsunuz?
Beş yıldır. Beş yıl önce üniversiteyi bitirdim ve sonra Stuttgart'a taşındım.
Peki üniversiteden sonra ne yaptınız?
Önce marttan ağustosa kadar staj yaptım. O zamandan beri bir şirkette mühendis olarak çalışıyorum.
Peki bizde ne zamandan itibaren başlayabilirsiniz?
Bir ekimden itibaren.""",
        "grammar": ('Zaman: vor, seit, nach, ab, von ... bis', """Bu edatlar **Wann?** (ne zaman?) ve **Seit wann?** (ne zamandan beri?) sorularına cevap verir. Bir isimden önce geldiklerinde **Dativ** alırlar:

- **vor** (önce): **vor** zwei Jahren, **vor** einer Woche. Fiil geçmiş zamandadır.
- **seit** (-den beri): **seit** 2020, **seit** einem Monat. Geçmişte başlamış ve hâlâ sürüyor, bu yüzden fiil **şimdiki zamandadır**!
- **nach** (sonra): **nach** dem Studium, **nach** der Arbeit
- **ab** (-den itibaren): **ab** Montag, **ab** dem ersten Mai
- **von ... bis** (-den ... -e kadar): **von** März **bis** August, **von** neun **bis** fünf Uhr (tek başına bis Akkusativ alır: **bis** nächsten Montag)
- **in** (içinde, şu andan itibaren): **in** zwei Wochen

Dikkat: hâlâ süren bir durum için "iki yıldır" **seit** zwei Jahren olur: Ich wohne **seit** zwei Jahren hier.

Yıllar için Almanca yalnızca sayıyı (Ich bin **1995** geboren) veya **im Jahr** 1995 der; asla "in 1995" demez.""",
                    "Üç yıl önce Berlin'e taşındım.; İki yıldır Almanca öğreniyorum.; Okuldan sonra staj yaptım.; Pazartesiden itibaren tatildeyim."),
    },
}

EXACT = exact(LESSONS, TR)
