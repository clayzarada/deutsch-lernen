"""Turkish for the noun and number drills (app/wordtrain.py), merged into app/i18n.py like i18n_verbs.py."""

EXACT = {
    # ----- labels -----
    "Numbers 0–100: word to digits": "0–100 arası sayılar: yazıdan rakama",
    "Numbers 0–100: write them out": "0–100 arası sayılar: yazıyla yazın",
    "Big numbers: word to digits": "Büyük sayılar: yazıdan rakama", "Big numbers: write them out": "Büyük sayılar: yazıyla yazın",
    "Clock times, everyday": "Saatler, günlük dilde", "Clock times: words to digits": "Saatler: yazıdan rakama",
    "Clock times, official (14:30)": "Saatler, resmî (14:30)", "Dates: am dritten Mai": "Tarihler: am dritten Mai",
    "Dates: der dritte Mai": "Tarihler: der dritte Mai", "Prices": "Fiyatlar", "Years": "Yıllar",
    "The 200 most common nouns": "En yaygın 200 isim", "The 650 most common": "En yaygın 650 isim",
    "The 1,900 most common": "En yaygın 1.900 isim", "All 8,500": "8.500 ismin hepsi",
    # ----- instructions -----
    "Write it in digits": "Rakamla yazın", "Write it out in words": "Yazıyla yazın",
    "Say it the everyday way": "Günlük dilde söyleyin", "Write the time in digits": "Saati rakamla yazın",
    "Say it the official way": "Resmî biçimde söyleyin", "Write the date out (Ich komme ...)": "Tarihi yazıyla yazın (Ich komme ...)",
    "Write the date out": "Tarihi yazıyla yazın", "Say the price": "Fiyatı söyleyin", "Say the year": "Yılı söyleyin",
    # ----- explanations -----
    "Numbers 21–99 say the ones first: einundzwanzig = one-and-twenty.":
        "21–99 arası sayılarda önce birler söylenir: einundzwanzig = bir-ve-yirmi.",
    "Write them as one word.": "Tek kelime olarak yazılır.",
    "Write numbers as one word, however long.": "Sayılar ne kadar uzun olursa olsun tek kelime olarak yazılır.",
    "Careful: sechzehn and siebzehn drop letters (not sechszehn, siebenzehn).":
        "Dikkat: sechzehn ve siebzehn'de harf düşer (sechszehn, siebenzehn değil).",
    "halb vier = half to four: halb points to the coming hour.": "halb vier = dörde yarım var (3:30): halb gelecek saati gösterir.",
    "Viertel nach drei = quarter past three.": "Viertel nach drei = üçü çeyrek geçiyor.",
    "In parts of Germany: viertel vier.": "Almanya'nın bazı bölgelerinde: viertel vier.",
    "Viertel vor vier = quarter to four.": "Viertel vor vier = dörde çeyrek var.",
    "In parts of Germany: drei viertel vier.": "Almanya'nın bazı bölgelerinde: drei viertel vier.",
    "nach = past, vor = to.": "nach = geçiyor, vor = var.",
    "Around the half hour Germans count from halb: fünf vor halb vier = 3:25.":
        "Buçuğa yakın saatlerde Almanlar halb'den sayar: fünf vor halb vier = 3:25.",
    "Official times (timetables, the news) use the 24-hour clock: the hour, then Uhr, then the minutes.":
        "Resmî saatlerde (tarifeler, haberler) 24 saat kullanılır: önce saat, sonra Uhr, sonra dakika.",
    "am + date takes the dative: am dritten, am zwanzigsten.": "am + tarih Dativ ister: am dritten, am zwanzigsten.",
    "1st-19th add -t-, 20th and up add -st-.": "1.–19. -t- alır, 20. ve sonrası -st- alır.",
    "After der in the nominative the ordinal ends in -e: der dritte, der zwanzigste.":
        "Nominativ'de der'den sonra sıra sayısı -e ile biter: der dritte, der zwanzigste.",
    "Special: erste, dritte, siebte, achte.": "Özel olanlar: erste, dritte, siebte, achte.",
    "Prices: euros, then the cents, usually without saying Cent: drei Euro fünfzig.":
        "Fiyatlar: önce euro, sonra sent, genellikle Cent denmeden: drei Euro fünfzig.",
    "The comma is the decimal point in German.": "Almancada ondalık ayırıcı virgüldür.",
    "Years before 2000 are said in hundreds: neunzehnhundertneunundneunzig.":
        "2000'den önceki yıllar yüzlerle söylenir: neunzehnhundertneunundneunzig.",
    "From 2000 on: zweitausend...": "2000'den itibaren: zweitausend...",
    "No reliable ending rule for this one, so learn it with its article.":
        "Bunun için güvenilir bir ek kuralı yok, artikeliyle birlikte öğrenin.",
    "Learn each noun with its plural.": "Her ismi çoğuluyla birlikte öğrenin.",
    "Full hours: the number, then Uhr (vier Uhr).": "Tam saatler: sayı, sonra Uhr (vier Uhr).",
    "One o'clock is ein Uhr.": "Saat bir ein Uhr olur.",
    "no change": "değişmez", "umlaut only": "yalnızca Umlaut", "an irregular change": "düzensiz bir değişim",
}

PATTERNS = [
    ("{} → {}: {}.", "{1} → {2}: {3}."),
    ("umlaut + {}", "Umlaut + {1}"),
]
