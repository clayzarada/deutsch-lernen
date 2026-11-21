"""Turkish for the A1 lessons (app/lessons_data.py), merged into app/i18n.py like lessons_b1_tr.py.

Written per lesson in the same shape and order as the English, so the two can be read side by side:
words (";"-separated, one per word, in the lesson's order), dialogue (one line per line), grammar (title, text,
examples ";"-separated) and hints (the English hints in brackets at the end of exercises, "English=Turkish").
EXACT below turns them into {English: Turkish} for i18n.tr(); app/lessons.py also uses them lesson by lesson.
German stays German.
"""
from .lessons_data import LESSONS
from .lessons_tr import exact

TR = {
    "hallo": {
        "subtitle": 'Selamlaşma ve adınızı söyleme',
        "words": """merhaba; günaydın; iyi günler, merhaba; iyi akşamlar; hoşça kal; hoşça kalın, görüşmek üzere; teşekkürler;
lütfen, rica ederim; evet; hayır; ad, isim; ben; sen (samimi); siz (resmî)""",
        "dialogue": """Merhaba! Ben Anna. Adın ne?
Merhaba Anna! Benim adım Ben.
Memnun oldum, Ben. Nasılsın?
İyiyim, teşekkürler. Ya sen?
Ben de iyiyim, teşekkürler. Hoşça kal, Ben!
Hoşça kal, görüşürüz!""",
        "grammar": ('du mu, Sie mi?', """Almancada "sen / siz" için iki kelime vardır. **du**, arkadaşlarla, aileyle, çocuklarla ve gündelik ortamlarda yaşıtlarınızla kullanılır. **Sie** (her zaman büyük S ile) yabancılarla, mağazalarda ve resmî dairelerde, Bay veya Bayan diye hitap edeceğiniz herkesle kullanılır.

Fiil de buna göre değişir: **Wie heißt du?** ama **Wie heißen Sie?**

Adınızı söylemek için **Ich heiße ...** (Benim adım ...) veya **Ich bin ...** (Ben ...) dersiniz.""",
                    'Adın ne? (samimi); Adınız ne? (resmî); Benim adım Maria.; Ben Tom.'),
        "hints": "at 8 in the morning=sabah saat 8'de; formal=resmî",
    },
    "woher": {
        "subtitle": 'Ülkeler, şehirler ve diller',
        "words": """gelmek; oturmak, yaşamak; konuşmak; öğrenmek; Almanya; Avusturya; İsviçre; Türkiye; Almanca; İngilizce; şehir;
ülke; nereden; nerede; -den, -dan (nereli olduğunu söylerken); -de, -da, içinde; biraz""",
        "dialogue": """Nerelisin, Tom?
İngiltere'denim. Ya sen?
Avusturya'danım, Viyana'dan.
Şimdi nerede oturuyorsun?
Berlin'de oturuyorum. Almanca konuşuyor musun?
Evet, biraz. Almanca öğreniyorum.""",
        "grammar": ('Fiil ekleri: ich, du, er/sie', """Almanca fiillerin sonu kişiye göre değişir. Sözlük biçiminden **-en**'i atın ve şunu ekleyin:

- **ich** → **-e**: ich komm**e**, ich wohn**e**
- **du** → **-st**: du komm**st**, du wohn**st**
- **er / sie / es** → **-t**: er komm**t**, sie wohn**t**
- **Sie** (resmî) **-en** ile kalır: Sie komm**en**

Soru kelimesiyle başlayan sorularda fiil ikinci sıradadır: **Woher kommst du?** **Wo wohnst du?**""",
                    "İspanya'danım.; Köln'de oturuyorsun.; O (kadın) Almanca öğreniyor.; Nerelisiniz? (resmî)"),
        "hints": 'she=o (kadın)',
    },
    "zahlen": {
        "subtitle": "0'dan 20'ye sayılar, yaş ve telefon numaraları",
        "words": """sıfır; bir; iki; üç; dört; beş; altı; yedi; sekiz; dokuz; on; on bir; on iki; yirmi; yıl; yaşlı, eski; numara;
telefon; nasıl; kim""",
        "dialogue": """İyi günler. Adınız nedir, lütfen?
Adım Emre Kaya.
Kaç yaşındasınız, Bay Kaya?
On dokuz yaşındayım.
Peki telefon numaranız nedir?
Sıfır, bir, yedi, iki, dört, sekiz, beş.""",
        "grammar": ('sein (olmak)', """**sein** Almancanın en önemli fiilidir ve düzensizdir:

- ich **bin** (ben ...im)
- du **bist** (sen ...sin)
- er / sie / es **ist** (o ...dir)
- wir **sind** (biz ...iz)
- ihr **seid** (siz ...siniz, birkaç kişiye)
- sie / Sie **sind** (onlar ...dir / siz ...siniz, resmî)

Yaş söylerken Almanca da sein kullanır: **Ich bin zwanzig Jahre alt.** (Yirmi yaşındayım.) 13'ten 19'a kadar sayılar **-zehn** ile biter: dreizehn, vierzehn, fünfzehn, sechzehn, siebzehn, achtzehn, neunzehn.""",
                    'On iki yaşındayım.; Kaç yaşındasın?; O (kadın) yirmi yaşında.; Polonyalıyız.'),
    },
    "cafe": {
        "subtitle": 'Yiyecek ve içecek sipariş etme',
        "words": """kahve; çay; su; meyve suyu; süt; pasta, kek; küçük ekmek; çorba; istemek (kibarca); almak; içmek; yemek; hesap;
avro; ile; -sız, olmadan; ve; veya""",
        "dialogue": """İyi günler! Ne arzu edersiniz?
Sütlü bir kahve istiyorum, lütfen.
Tabii. Bir şey yemek de ister misiniz?
Evet, bir küçük ekmek ve bir çorba alayım.
Çok güzel. Hemen geliyor.
Hesap, lütfen.
Dokuz avro tutuyor.""",
        "grammar": ('der, die, das ve ein, eine', """Almancada her ismin bir cinsiyeti vardır; bunu artikel gösterir:

- **der** (eril): der Kaffee, der Tee
- **die** (dişil): die Milch, die Suppe
- **das** (nötr): das Wasser, das Brötchen

Her ismi artikeliyle birlikte öğrenin. "Bir" anlamındaki artikel der ve das kelimelerinde **ein**, die kelimelerinde **eine** olur.

Bir şey sipariş ettiğinizde veya bir şeye sahip olduğunuzda eril kelimeler değişir: **der → den**, **ein → einen**. Dişil ve nötr kelimeler aynı kalır: Ich möchte **einen** Kaffee, **eine** Suppe, **ein** Wasser.""",
                    'Bir çay istiyorum.; Bir çorba alayım.; O bir su içiyor.; Kahve güzel.'),
    },
    "familie": {
        "subtitle": 'Aileniz hakkında konuşma',
        "words": """aile; anne; baba; anne baba; erkek kardeş; kız kardeş; çocuk; oğul; kız evlat; adam, koca; kadın, eş (kadın);
arkadaş, erkek arkadaş; sahip olmak; evli; benim; senin; hiç, -sız (olumsuz)""",
        "dialogue": """Kardeşin var mı, Mia?
Evet, bir erkek ve bir kız kardeşim var.
Erkek kardeşinin adı ne?
Erkek kardeşimin adı Jonas. O evli.
Çocukları var mı?
Evet, bir kızı var. Ya sen? Kardeşin var mı?
Hayır, hiç kardeşim yok.""",
        "grammar": ('haben ve mein / dein', """**haben** (sahip olmak):

- ich **habe**
- du **hast**
- er / sie / es **hat**
- wir **haben**
- ihr **habt**
- sie / Sie **haben**

**mein** (benim) ve **dein** (senin), ein ile aynı ekleri alır: **mein** Bruder (der), **meine** Schwester (die), **mein** Kind (das).

Bir şeyin olmadığını söylemek için **kein / keine** kullanılır: Ich habe **keinen** Bruder. Ich habe **keine** Schwester.""",
                    'Bir kız kardeşim var.; Çocukların var mı?; Annemin adı Eva.; Onun erkek kardeşi yok.'),
        "hints": 'my=benim; your=senin; no=hiç (olumsuz)',
    },
    "tag": {
        "subtitle": 'Günlük düzen ve saati söyleme',
        "words": """saat; sabah; akşam; gece; iş; okul; çalışmak; gitmek (yürüyerek); uyumak; kahvaltı yapmak; oynamak; bugün;
yarın; şimdi; sonra; erken; geç; saat ...de""",
        "dialogue": """Saat kaç?
Saat yedi.
Çok erken! İşe ne zaman gidiyorsun?
Saat sekizde. Önce kahvaltı yapıyorum.
Peki bu akşam ne yapıyorsun?
Bu akşam tenis oynuyorum. Sonra erken yatıyorum.""",
        "grammar": ('Fiil ikinci sıradadır', """Almanca düz cümlede fiil her zaman **ikinci** öğedir. Cümleye bir zaman kelimesiyle başlarsanız özne fiilin arkasına geçer:

- **Ich spiele** heute Tennis.
- **Heute spiele ich** Tennis.

İkisi de doğrudur. Fiil ikinci sırada kalır.

Saatler için **Es ist ... Uhr** (Saat ...) ve **um ... Uhr** (saat ...'de) denir: Ich arbeite **um neun Uhr**.""",
                    'Saat sekizde okula gidiyorum.; Saat sekizde okula gidiyorum.; Yarın çalışmıyorum.; Saat on.'),
    },
    "einkaufen": {
        "subtitle": 'Yiyecek alışverişi, fiyatlar ve çoğullar',
        "words": """süpermarket; ekmek; peynir; elma; muz; domates; yumurta; patates; et; satın almak; ihtiyacı olmak; fiyatı olmak,
tutmak; pahalı; ucuz; çok; ne kadar; kilo; çanta""",
        "dialogue": """Neye ihtiyacımız var?
Ekmek, peynir ve altı yumurtaya ihtiyacımız var.
Hâlâ domatesimiz var mı?
Hayır, hiç domatesimiz yok. Elmamız da yok.
Affedersiniz, elmalar kaça?
Bir kilosu iki avro.
Tamam, iki kilo alayım.""",
        "grammar": ('Çoğullar ve kein', """Almanca çoğullar tek bir kurala uymaz; bu yüzden her ismin çoğulunu da öğrenin. Sık görülen kalıplar:

- **-n / -en**: die Banane → die Banane**n**, die Tomate → die Tomate**n**
- **-e** (çoğu zaman umlaut ile): das Brot → die Brot**e**, der Apfel → die **Ä**pfel
- **-er**: das Ei → die Ei**er**, das Kind → die Kind**er**
- **-s**: das Kilo → die Kilo**s**

Çoğulda artikel her zaman **die**'dir: die Äpfel, die Eier.

**kein** "hiç" veya "bir ... değil" demektir. die kelimeleri ve bütün çoğullar için **keine** kullanılır: Wir haben **keine** Tomaten.""",
                    'Üç muz alıyorum.; Elmalar ucuz.; Hiç ekmeğimiz yok.; Yumurtaya ihtiyacım yok.'),
        "hints": 'no=hiç (olumsuz)',
    },
    "wohnung": {
        "subtitle": 'Odalar, mobilyalar ve eşyaları tarif etme',
        "words": """daire, ev; ev, bina; oda; mutfak; banyo; yatak odası; masa; sandalye; yatak; dolap, gardırop; pencere; kapı;
büyük; küçük; güzel; yeni; eski; aydınlık; var""",
        "dialogue": """Evin çok güzel! Kaç odası var?
Üç odası, bir mutfağı ve bir banyosu var.
Mutfak büyük.
Evet, ama banyo küçük. İşte yatak odası.
Yatak yeni mi?
Evet. Ama dolap eski. Bir de balkon var.""",
        "grammar": ('Eşyalar için er, sie, es ve es gibt', """Almancada eşyalar cinsiyetlerine göre **er**, **sie** veya **es** zamiriyle anılır:

- der Tisch → **er**: Der Tisch ist neu. **Er** ist neu.
- die Küche → **sie**: Die Küche ist groß. **Sie** ist groß.
- das Bad → **es**: Das Bad ist klein. **Es** ist klein.

sein fiilinden sonra sıfatlar ek almaz: Das Zimmer ist **hell**.

**Es gibt** "var" demektir ve sipariş verirken kullanılan biçimleri alır: **Es gibt einen Tisch**, **eine Küche**, **ein Bad**.""",
                    'Sandalye eski. O eski.; Daire aydınlık. O aydınlık.; Bir pencere var.; Bir dolap var.'),
    },
    "stadt": {
        "subtitle": 'Şehirdeki yerler ve yol sorma',
        "words": """tren istasyonu, gar; banka; postane; eczane; hastane; cadde, sokak; meydan; otobüs; tren; sol, solda; sağ,
sağda; dümdüz; burada; orada; uzak; yakın; gitmek (araçla); aramak""",
        "dialogue": """Affedersiniz, tren istasyonu nerede?
İstasyon uzak değil. Dümdüz gidin.
Sonra?
Sonra sola dönün. İstasyon pazar meydanında.
Orada bir eczane var mı?
Evet, eczane istasyonun içinde.
Çok teşekkür ederim!""",
        "grammar": ('Nerede? im, am, in der', """Bir şeyin nerede olduğunu söylemek için **in** veya **an** kullanılır ve artikel değişir:

- der / das kelimeleri: **in dem → im**, **an dem → am**: **im** Bahnhof, **im** Haus, **am** Platz
- die kelimeleri: **in der**, **an der**: **in der** Stadt, **in der** Apotheke

Kibarca yol tarif ederken fiil başa gelir ve **Sie** eklenir: **Gehen Sie** links. **Fahren Sie** geradeaus.""",
                    'Süpermarketteyim.; Banka şehirde.; İstasyondayız.; Sağa gidin.'),
        "hints": 'far=uzak',
    },
    "freizeit": {
        "subtitle": 'Hobiler, sevdikleriniz ve yapabildikleriniz',
        "words": """boş zaman; hobi; müzik; spor; film; kitap; okumak; dinlemek, duymak; yüzmek; yemek pişirmek; dans etmek; seyahat
etmek; -ebilmek; severek; sık sık; asla, hiç; bazen; birlikte""",
        "dialogue": """Boş zamanında ne yapmayı seversin?
Müzik dinlemeyi ve yemek pişirmeyi severim.
İyi yemek yapabiliyor musun?
Evet, oldukça iyi. Ya sen? Hobilerin neler?
Sık sık yüzerim ve kitap okumayı severim.
Ben yüzemiyorum!
Sorun değil. Birlikte yemek yapabiliriz.""",
        "grammar": ('gern ve können', """Bir şeyi yapmayı sevdiğinizi söylemek için fiilden sonra **gern** ekleyin: Ich **koche gern**. (Yemek yapmayı severim.) "Sevmem" demek için **nicht gern**: Ich tanze **nicht gern**.

**können** (-ebilmek) düzensizdir:

- ich **kann**
- du **kannst**
- er / sie / es **kann**
- wir **können**
- sie / Sie **können**

können ile ikinci fiil sözlük biçimiyle cümlenin **sonuna** gider: Ich **kann** gut **schwimmen**.""",
                    'Okumayı severim.; Dans etmeyi sevmez.; Yemek yapabilir misin?; Yarın yüzebiliriz.'),
        "hints": 'I like to=severek; she=o (kadın)',
    },
    "termine": {
        "subtitle": 'Haftanın günleri ve plan yapma',
        "words": """pazartesi; salı; çarşamba; perşembe; cuma; cumartesi; pazar; hafta; hafta sonu; randevu; zaman, vakit; telefonla
aramak; kalkmak (yataktan); alışveriş yapmak; buluşmak; ne zaman; ...günü; belki""",
        "dialogue": """Cumartesi vaktin var mı?
Cumartesi alışveriş yapıyorum. Ama pazar günü vaktim var.
Güzel! Pazar günü buluşalım mı?
Seve seve. Ne zaman?
Saat üçte mi? Hafta sonları geç kalkıyorum.
Tamam. Pazar günü seni ararım.""",
        "grammar": ('Ayrılabilen fiiller ve am + gün', """Bazı fiillerin ön eki ayrılır ve cümlenin **sonuna** gider:

- **auf**stehen: Ich **stehe** um sieben Uhr **auf**.
- **an**rufen: Ich **rufe** dich morgen **an**.
- **ein**kaufen: Wir **kaufen** am Samstag **ein**.

Günlerle **am** kullanılır: **am Montag**, **am Wochenende**. Saatlerle **um** kullanılır: **um drei Uhr**.""",
                    'Erken kalkarım.; Annesini arıyor.; Cuma günü alışveriş yapıyoruz.; Ne zaman kalkarsın?'),
    },
    "gestern": {
        "subtitle": 'Geçmiş hakkında konuşma',
        "words": """dün; geçen hafta; yapmak; yaptı (machen); satın aldı (kaufen); oynadı (spielen); öğrendi (lernen); çalıştı
(arbeiten); yedi (essen); içti (trinken); gitti (gehen); (araçla) gitti, sürdü (fahren); geldi (kommen); kaldı
(bleiben); tatil; evde; zaten, çoktan; henüz değil""",
        "dialogue": """Dün ne yaptın?
Çalıştım, sonra futbol oynadım. Ya sen?
Şehre gittim ve bir çanta aldım.
Yemek yedin mi?
Hayır, henüz değil. Dün sadece pasta yedim.
O zaman şimdi yemeğe gidelim!""",
        "grammar": ('Perfekt: haben veya sein + ge-', """Konuşma dilinde geçmişten bahsederken **Perfekt** kullanılır: ikinci sırada **haben** veya **sein**'ın bir biçimi, sonda da fiilin **ge-** biçimi.

- Ich **habe** Fußball **gespielt**. (Futbol oynadım.)
- Er **hat** ein Buch **gekauft**. (Bir kitap aldı.)

Düzenli fiiller **ge- ... -t** ile yapılır: machen → **gemacht**, lernen → **gelernt**. Sık kullanılan birçok fiil düzensizdir ve **-en** ile biter: essen → **gegessen**, trinken → **getrunken**.

Hareket veya değişim bildiren fiiller **sein** kullanır: Ich **bin** nach Berlin **gefahren**. Sie **ist** nach Hause **gegangen**. Wir **sind** zu Hause **geblieben**.""",
                    "Almanca öğrendim.; Pizza yedik.; Viyana'ya gitti.; Evde mi kaldın?"),
    },
    "beruf": {
        "subtitle": 'Meslekler, iş yerleri ve evet/hayır soruları',
        "words": """meslek; öğretmen (erkek); öğretmen (kadın); doktor (erkek); doktor (kadın); satış görevlisi (erkek); satış
görevlisi (kadın); üniversite öğrencisi (erkek); üniversite öğrencisi (kadın); ofis, büro; şirket, firma; para;
saat (süre); olarak (meslek); üniversitede okumak; kazanmak (para); ilginç; yorucu""",
        "dialogue": """Mesleğiniz ne, Bayan Yılmaz?
Doktorum. Hastanede çalışıyorum.
İş ilginç mi?
Evet, çok. Ama yorucu da. Ya siz? Siz de çalışıyor musunuz?
Henüz öğrenciyim. Ama hafta sonları satış görevlisi olarak çalışıyorum.
İyi kazanıyor musunuz?
Fena değil. Saati on iki avro.""",
        "grammar": ('-in ile meslekler ve evet/hayır soruları', """Çoğu meslekte kadın biçimi **-in** eki alır: der Lehrer → die Lehrer**in**, der Verkäufer → die Verkäufer**in**, der Student → die Student**in**. Bazılarına umlaut da gelir: der Arzt → die **Ä**rzt**in**.

Mesleğinizi söylerken **artikel kullanılmaz**: Ich bin **Lehrer**. Sie ist **Ärztin**. Ya da **als** ile: Ich arbeite **als** Verkäufer.

Evet/hayır soruları **fiille** başlar: **Arbeiten Sie** im Büro? **Ist** die Arbeit interessant? **Studierst du**? Cevap ja veya nein'dır.""",
                    'Öğretmenim. (kadın); Satış görevlisi olarak çalışıyor.; Üniversitede okuyor musun?; Şirket büyük mü?'),
        "hints": 'doctor=doktor; teacher=öğretmen',
    },
    "datum": {
        "subtitle": 'Aylar, tarihler ve doğum günleri',
        "words": """ocak; şubat; mart; nisan; mayıs; haziran; temmuz; ağustos; eylül; ekim; kasım; aralık; doğum günü; tarih; ay;
kutlamak; parti; davet etmek""",
        "dialogue": """Doğum günün ne zaman, Emre?
Dört mayısta. Ya seninki?
Aralıkta, yirmi aralıkta.
Bugün ayın kaçı?
Bugün üç mayıs. O zaman yarın senin doğum günün!
Evet! Cumartesi kutluyorum. Seni davet ediyorum.
Teşekkürler! Partiye seve seve gelirim.""",
        "grammar": ('Tarihler: der dritte Mai, am dritten Mai', """Tarihlerde **sıra sayıları** (birinci, ikinci, üçüncü) kullanılır. 19'a kadar **-te**, 20'den itibaren **-ste** eklenir:

- erste (1.), zweite (2.), **dritte** (3.), vierte (4.), **siebte** (7.), achte (8.)
- neunzehnte (19.), zwanzig**ste** (20.), einunddreißig**ste** (31.)

Yazıda sayıdan sonraki nokta onu sıra sayısı yapar: **der 3. Mai**.

Bugün ayın kaçı? **der** dritte Mai: Heute ist **der dritte** Mai.

Hangi tarihte? **am** + **-en**: Ich habe **am dritten** Mai Geburtstag.

Aylarla **im** kullanılır: **im** Mai, **im** Dezember.""",
                    'Bugün bir nisan.; Doğum günüm iki haziranda.; Ağustosta tatildeyim.; Parti yirmi aralıkta.'),
        "hints": '3rd=3.; 1st=1.; 7th=7.; 20th=20.; 2nd=2.',
    },
    "arzt": {
        "subtitle": 'Vücut, hastalık ve doktorun tavsiyeleri',
        "words": """baş, kafa; karın; boğaz, boyun; sırt; kol; bacak; göz; ateş; soğuk algınlığı; tablet, hap; reçete; muayenehane;
hasta; sağlıklı; ağrımak, acımak; kalmak""",
        "dialogue": """İyi günler, Bay Brandt. Neyiniz var?
Başım ağrıyor ve boğazım acıyor.
Ateşiniz de var mı?
Evet, biraz. Dünden beri.
Soğuk algınlığınız var. İki gün yatakta kalın ve bol çay için.
İlaç almam gerekiyor mu?
Evet, işte reçeteniz. Sabah ve akşam birer tablet alın. Geçmiş olsun!""",
        "grammar": ('Emir kipi: Trink! Trinken Sie!', """Birine ne yapacağını söylemek için **emir kipi** kullanılır. Fiil **başa** gelir.

- **Sie** (resmî): fiil + Sie: **Bleiben Sie** im Bett! **Nehmen Sie** eine Tablette!
- **du**: du biçiminden **-st** ve du atılır: du trinkst → **Trink** viel Tee! du gehst → **Geh** nach Hause!
- **ihr**: ihr biçiminden ihr atılır: ihr kommt → **Kommt** bitte!

e'yi i'ye çeviren fiiller i'yi korur: du nimmst → **Nimm** eine Tablette! Ama a → ä değişimi korunmaz: du schläfst → **Schlaf** gut!

**sein** düzensizdir: **Sei** ruhig! **Seien Sie** pünktlich!

Kibar olmak için **bitte** ekleyin: **Kommen Sie bitte** herein.""",
                    'Bol su iç!; Bir tablet al!; Evde kalın!; Lütfen yarın gelin! (birkaç kişiye)'),
    },
    "kleidung": {
        "subtitle": 'Giysiler, renkler ve Akkusativ',
        "words": """giysi, kıyafet; pantolon; gömlek; ceket, mont; etek; elbise; ayakkabı; kazak; beden; renk; kırmızı; mavi; siyah;
beyaz; yeşil; denemek (giysi); olmak, uymak (beden)""",
        "dialogue": """İyi günler. Yardımcı olabilir miyim?
Evet, bir ceket arıyorum. Bu ceketin mavisi de var mı?
Evet. Bedeniniz kaç?
38 beden. Deneyebilir miyim?
Tabii. Nasıl, oldu mu?
Evet, tam oldu. Buradaki kazak da güzel. Onu da alıyorum.
Memnuniyetle. Hepsi 89 avro tutuyor.""",
        "grammar": ('Akkusativ: den, einen, ihn', """Fiilin etkilediği kişi veya şey (**nesne**) **Akkusativ** hâlindedir. Yalnızca der kelimeleri değişir:

- der → **den**: Ich kaufe **den** Rock.
- ein → **einen**, kein → **keinen**: Ich suche **einen** Pullover.
- die, das ve çoğullar aynı kalır: Ich nehme **die** Jacke, **das** Hemd, **die** Schuhe.

Zamirler de aynı şekilde çalışır: der Rock → **ihn**, die Jacke → **sie**, das Kleid → **es**. Ich nehme **ihn**. Ich probiere **sie** an.

**kaufen, nehmen, suchen, brauchen, haben, möchten** ve **es gibt** gibi fiiller Akkusativ alır.""",
                    'Kazağı alıyorum.; Bir etek arıyor.; Etek güzel. Onu alıyorum.; Ayakkabılar tam oluyor.'),
    },
    "wetter": {
        "subtitle": 'Hava durumu ve mevsimler',
        "words": """hava (durumu); güneş; yağmur; kar; rüzgâr; bulut; ilkbahar; yaz; sonbahar; kış; yağmur yağmak; kar yağmak;
parlamak; ılık, sıcak; soğuk; çok sıcak; güneşli; derece""",
        "dialogue": """Hamburg'da hava nasıl?
Pek iyi değil. Yağmur yağıyor ve rüzgârlı.
Burada, Münih'te güneş parlıyor. Hava sıcak, yirmi beş derece!
Harika! Hamburg'da yazın sık sık yağmur yağar.
Ya kışın? Çok kar yağar mı?
Bazen. Ama hava çoğu zaman soğuk ve gri.""",
        "grammar": ('es ile hava durumu: es regnet, es ist kalt', """Hava durumu cümleleri **es** ile başlar:

- **Es regnet.** (Yağmur yağıyor.) **Es schneit.** (Kar yağıyor.)
- **Es ist** kalt / warm / sonnig / windig.
- Sıcaklık: **Es ist zwanzig Grad.** Sıfırın altında: **minus fünf Grad**.

Ama güneşin kendi fiili vardır: **Die Sonne scheint.**

Mevsimler ve aylarla **im** kullanılır: **im** Sommer, **im** Winter, **im** Juli. Cümle bir zaman kelimesiyle başlarsa fiil yine ikinci sırada kalır ve es arkasına geçer: **Im Herbst regnet es** oft.""",
                    'Bugün hava çok sıcak.; Kışın kar yağar.; Yarın yağmur yağacak.; Güneş parlıyor.'),
    },
    "bahn": {
        "subtitle": 'Biletler, tarifeler, müssen ve wollen',
        "words": """bilet; tarife, sefer saatleri; peron, hat; kalkış; varış; yolculuk, seyahat; gişe; gecikme, rötar; kalkmak,
hareket etmek; varmak; aktarma yapmak; ziyaret etmek; zorunda olmak, -meli; istemek; tek yön, basit; gidiş
dönüş; zamanında, dakik""",
        "dialogue": """İyi günler. Köln'e bir bilet istiyorum, lütfen.
Tek yön mü, gidiş dönüş mü?
Gidiş dönüş. Kız kardeşimi ziyaret etmek istiyorum. Tren ne zaman kalkıyor?
Saat 9.15'te, 4. perondan. Frankfurt'ta aktarma yapmanız gerekiyor.
Köln'e ne zaman varıyorum?
Tren zamanında olursa saat 13.40'ta. 98 avro tutuyor.""",
        "grammar": ('müssen ve wollen', """**müssen** (zorunda olmak) ve **wollen** (istemek) **können** gibi çalışır: modal fiil ikinci sıradadır, ikinci fiil sözlük biçimiyle cümlenin **sonuna** gider.

- müssen: ich **muss**, du **musst**, er/sie **muss**, wir **müssen**, ihr **müsst**, sie/Sie **müssen**
- wollen: ich **will**, du **willst**, er/sie **will**, wir **wollen**, ihr **wollt**, sie/Sie **wollen**

ich ve er/sie aynı biçimdedir ve ek almaz: ich **muss**, er **muss**.

Dikkat: **ich will** "istiyorum" demektir, İngilizcedeki "will" gibi gelecek zaman bildirmez! İsteğinizi söylemenin daha kibar yolu **Ich möchte**'dir.

Ayrılabilen fiiller sonda bütün hâlde kalır: Ich muss in Frankfurt **umsteigen**.""",
                    "Saat altıda kalkmam gerekiyor.; Viyana'ya gitmek istiyoruz.; Bugün çalışman gerekiyor mu?; Erkek kardeşini ziyaret etmek istiyor."),
        "hints": 'want=istemek',
    },
    "wo": {
        "subtitle": 'Eşyalar nerede: Dativ alan edatlar',
        "words": """cep telefonu; anahtar; kanepe; raf; lamba; duvar; resim, tablo; üstünde; altında; yanında; önünde; arkasında;
arasında; -de, -da (duvarda), yanında; (yatay) durmak, yatmak; (dik) durmak; asılı olmak""",
        "dialogue": """Lena, telefonum nerede?
Masanın üstünde değil mi?
Hayır. Anahtarım da yok!
Anahtar duvarda asılı, kapının yanında.
Ah, teşekkürler. Ya telefon?
Kanepenin altına bir bak. Ya da raftaki lambanın arkasına.
İşte orada, kanepeyle rafın arasında!""",
        "grammar": ('Nerede? Dativ alan edatlar', """Bir şeyin **nerede** olduğunu söylemek için **in, an, auf, unter, neben, vor, hinter, zwischen** edatları **Dativ** ile kullanılır. Artikeller değişir:

- der → **dem**: auf **dem** Tisch, unter **dem** Stuhl
- das → **dem**: neben **dem** Sofa, **im** (= in dem) Regal
- die → **der**: an **der** Wand, hinter **der** Tür
- çoğul die → **den** ve isim -n alır: zwischen **den** Büchern

Kısaltmalar: in dem → **im**, an dem → **am**.

Bunlarla kullanılan fiiller: **liegen** (yatay durmak), **stehen** (dik durmak), **hängen** (asılı olmak).""",
                    'Kitap masanın üstünde.; Lamba yatağın yanında.; Resim duvarda asılı.; Kedi kanepenin altında.'),
        "hints": 'under=altında',
    },
    "unterwegs": {
        "subtitle": 'Şehirde dolaşmak: mit, zu, nach, von, bei',
        "words": """araba; bisiklet; metro; tramvay; durak; trafik lambası; sinema; müze; park; -e, -a (bir yere veya kişiye); -e,
-a (şehre veya ülkeye), sonra; -den, -dan; -de, -da (birinin yanında), yakınında; eve; yürüyerek""",
        "dialogue": """İşe nasıl gidiyorsun, Jonas?
Bisikletle. Ya sen? Arabayla mı gidiyorsun?
Hayır, metroyla gidiyorum. Ama bugün sinemaya yürüyerek gidiyorum.
Sinema nerede?
Parkın yanında. Trafik lambasına kadar yürüyüp sola dönüyorum.
Peki filmden sonra?
Sonra tramvayla eve dönüyorum.""",
        "grammar": ('mit, zu, nach, von, bei: her zaman Dativ', """Bazı edatlar **her zaman** Dativ alır: **mit, zu, nach, von, bei, aus**.

- der / das → **dem**: mit **dem** Auto, mit **dem** Fahrrad
- die → **der**: mit **der** U-Bahn, von **der** Arbeit

Kısaltmalar çok yaygındır: zu dem → **zum**, zu der → **zur**, bei dem → **beim**, von dem → **vom**: Ich gehe **zum** Arzt. Ich fahre **zur** Arbeit.

Nereye? Yerler ve kişiler için **zu** (**zum** Bahnhof, **zu** Anna), şehirler ve ülkeler için **nach** (**nach** Berlin), eve gitmek için **nach Hause**.

Ulaşım: **mit** + Dativ: Ich fahre **mit dem** Zug. Ama yürüyerek gitmek: **zu Fuß**.""",
                    "Okula otobüsle gidiyorum.; Viyana'ya gidiyoruz.; Doktora gidiyor.; Kız kardeşinin yanında oturuyor."),
        "hints": 'from=-den',
    },
}

EXACT = exact(LESSONS, TR)
