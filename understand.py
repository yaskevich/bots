import re
import datetime
import requests, unicodedata
import xmltodict, json
import emoji
# https://github.com/martinblech/xmltodict

import json
# https://github.com/matiassingers/emoji-flags/blob/master/data.json
with open('states.json') as json_states, open ('Common-Currency.json') as json_currencies:  
    states = json.load(json_states)
    currencies_info = json.load(json_currencies)
    
# http://country.io/currency.json
state2code = {"EU": "EUR", "BD": "BDT", "BE": "EUR", "BF": "XOF", "BG": "BGN", "BA": "BAM", "BB": "BBD", "WF": "XPF", "BL": "EUR", "BM": "BMD", "BN": "BND", "BO": "BOB", "BH": "BHD", "BI": "BIF", "BJ": "XOF", "BT": "BTN", "JM": "JMD", "BV": "NOK", "BW": "BWP", "WS": "WST", "BQ": "USD", "BR": "BRL", "BS": "BSD", "JE": "GBP", "BY": "BYN", "BZ": "BZD", "RU": "RUB", "RW": "RWF", "RS": "RSD", "TL": "USD", "RE": "EUR", "TM": "TMT", "TJ": "TJS", "RO": "RON", "TK": "NZD", "GW": "XOF", "GU": "USD", "GT": "GTQ", "GS": "GBP", "GR": "EUR", "GQ": "XAF", "GP": "EUR", "JP": "JPY", "GY": "GYD", "GG": "GBP", "GF": "EUR", "GE": "GEL", "GD": "XCD", "GB": "GBP", "GA": "XAF", "SV": "USD", "GN": "GNF", "GM": "GMD", "GL": "DKK", "GI": "GIP", "GH": "GHS", "OM": "OMR", "TN": "TND", "JO": "JOD", "HR": "HRK", "HT": "HTG", "HU": "HUF", "HK": "HKD", "HN": "HNL", "HM": "AUD", "VE": "VEF", "PR": "USD", "PS": "ILS", "PW": "USD", "PT": "EUR", "SJ": "NOK", "PY": "PYG", "IQ": "IQD", "PA": "PAB", "PF": "XPF", "PG": "PGK", "PE": "PEN", "PK": "PKR", "PH": "PHP", "PN": "NZD", "PL": "PLN", "PM": "EUR", "ZM": "ZMK", "EH": "MAD", "EE": "EUR", "EG": "EGP", "ZA": "ZAR", "EC": "USD", "IT": "EUR", "VN": "VND", "SB": "SBD", "ET": "ETB", "SO": "SOS", "ZW": "ZWL", "SA": "SAR", "ES": "EUR", "ER": "ERN", "ME": "EUR", "MD": "MDL", "MG": "MGA", "MF": "EUR", "MA": "MAD", "MC": "EUR", "UZ": "UZS", "MM": "MMK", "ML": "XOF", "MO": "MOP", "MN": "MNT", "MH": "USD", "MK": "MKD", "MU": "MUR", "MT": "EUR", "MW": "MWK", "MV": "MVR", "MQ": "EUR", "MP": "USD", "MS": "XCD", "MR": "MRO", "IM": "GBP", "UG": "UGX", "TZ": "TZS", "MY": "MYR", "MX": "MXN", "IL": "ILS", "FR": "EUR", "IO": "USD", "SH": "SHP", "FI": "EUR", "FJ": "FJD", "FK": "FKP", "FM": "USD", "FO": "DKK", "NI": "NIO", "NL": "EUR", "NO": "NOK", "NA": "NAD", "VU": "VUV", "NC": "XPF", "NE": "XOF", "NF": "AUD", "NG": "NGN", "NZ": "NZD", "NP": "NPR", "NR": "AUD", "NU": "NZD", "CK": "NZD", "XK": "EUR", "CI": "XOF", "CH": "CHF", "CO": "COP", "CN": "CNY", "CM": "XAF", "CL": "CLP", "CC": "AUD", "CA": "CAD", "CG": "XAF", "CF": "XAF", "CD": "CDF", "CZ": "CZK", "CY": "EUR", "CX": "AUD", "CR": "CRC", "CW": "ANG", "CV": "CVE", "CU": "CUP", "SZ": "SZL", "SY": "SYP", "SX": "ANG", "KG": "KGS", "KE": "KES", "SS": "SSP", "SR": "SRD", "KI": "AUD", "KH": "KHR", "KN": "XCD", "KM": "KMF", "ST": "STD", "SK": "EUR", "KR": "KRW", "SI": "EUR", "KP": "KPW", "KW": "KWD", "SN": "XOF", "SM": "EUR", "SL": "SLL", "SC": "SCR", "KZ": "KZT", "KY": "KYD", "SG": "SGD", "SE": "SEK", "SD": "SDG", "DO": "DOP", "DM": "XCD", "DJ": "DJF", "DK": "DKK", "VG": "USD", "DE": "EUR", "YE": "YER", "DZ": "DZD", "US": "USD", "UY": "UYU", "YT": "EUR", "UM": "USD", "LB": "LBP", "LC": "XCD", "LA": "LAK", "TV": "AUD", "TW": "TWD", "TT": "TTD", "TR": "TRY", "LK": "LKR", "LI": "CHF", "LV": "EUR", "TO": "TOP", "LT": "EUR", "LU": "EUR", "LR": "LRD", "LS": "LSL", "TH": "THB", "TF": "EUR", "TG": "XOF", "TD": "XAF", "TC": "USD", "LY": "LYD", "VA": "EUR", "VC": "XCD", "AE": "AED", "AD": "EUR", "AG": "XCD", "AF": "AFN", "AI": "XCD", "VI": "USD", "IS": "ISK", "IR": "IRR", "AM": "AMD", "AL": "ALL", "AO": "AOA", "AQ": "", "AS": "USD", "AR": "ARS", "AU": "AUD", "AT": "EUR", "AW": "AWG", "IN": "INR", "AX": "EUR", "AZ": "AZN", "IE": "EUR", "ID": "IDR", "UA": "UAH", "QA": "QAR", "MZ": "MZN"}
# https://github.com/gbif/portal16/blob/master/locales/translations/ru/enums/country.json
code2country = {
    "EU": "Еврозона",
    "AF": "Афганистан",
    "AX": "Аландские острова",
    "AL": "Албания",
    "DZ": "Алжир",
    "AS": "Американское Самоа",
    "AD": "Андорра",
    "AO": "Ангола",
    "AI": "Ангилья",
    "AQ": "Антарктида",
    "AG": "Антигуа и Барбуда",
    "AR": "Аргентина",
    "AM": "Армения",
    "AW": "Аруба",
    "AU": "Австралия",
    "AT": "Австрия",
    "AZ": "Азербайджан",
    "BS": "Багамские Острова",
    "BH": "Бахрейн",
    "BD": "Бангладеш",
    "BB": "Барбадос",
    "BY": "Белоруссия",
    "BE": "Бельгия",
    "BZ": "Белиз",
    "BJ": "Бенин",
    "BM": "Бермудские Острова",
    "BT": "Бутан",
    "BO": "Боливия, Многонациональное Государство",
    "BA": "Босния и Герцеговина",
    "BW": "Ботсвана",
    "BV": "Остров Буве",
    "BR": "Бразилия",
    "BQ": "Бонэйр, Синт-Эстатиус и Саба",
    "IO": "Британская Территория в Индийском океане",
    "BN": "Бруней Даруссалам",
    "BG": "Болгария",
    "BF": "Буркина-Фасо",
    "BI": "Бурунди",
    "KH": "Камбоджа",
    "CM": "Камерун",
    "CA": "Канада",
    "CV": "Кабо-Верде",
    "KY": "Каймановы Острова",
    "CF": "Центральноафриканская Республика",
    "TD": "Чад",
    "CL": "Чили",
    "CN": "Китай",
    "CX": "Остров Рождества",
    "CC": "Кокосовые ( Килинг) острова",
    "CO": "Колумбия",
    "KM": "Коморские Острова",
    "CG": "Республика Конго",
    "CD": "Демократическая Республика Конго",
    "CK": "Острова Кука",
    "CR": "Коста-Рика",
    "CI": "Кот-д’Ивуар",
    "HR": "Хорватия",
    "CU": "Куба",
    "CW": "Кюрасао",
    "CY": "Кипр",
    "CZ": "Чехия",
    "DK": "Дания",
    "DJ": "Джибути",
    "DM": "Доминика",
    "DO": "Доминиканская Республика",
    "EC": "Эквадор",
    "EG": "Египет",
    "SV": "Сальвадор",
    "GQ": "Экваториальная Гвинея",
    "ER": "Эритрея",
    "EE": "Эстония",
    "ET": "Эфиопия",
    "FK": "Фолклендские Острова (Мальвинские)",
    "FO": "Фарерские Острова",
    "FJ": "Фиджи",
    "FI": "Финляндия",
    "FR": "Франция",
    "GF": "Французская Гвиана",
    "PF": "Французская Полинезия",
    "TF": "Французские Южные Территории",
    "GA": "Габон",
    "GM": "Гамбия",
    "GE": "Грузия",
    "DE": "Германия",
    "GH": "Гана",
    "GI": "Гибралтар",
    "GR": "Греция",
    "GL": "Гренландия",
    "GD": "Гренада",
    "GP": "Гваделупа",
    "GU": "Гуам",
    "GT": "Гватемала",
    "GG": "Гернси",
    "GN": "Гвинея",
    "GW": "Гвинея-Бисау",
    "GY": "Гайана",
    "HT": "Гаити",
    "HM": "Остров Херд и Острова МакДональд",
    "VA": "Ватикан",
    "HN": "Гондурас",
    "HK": "Гонконг",
    "HU": "Венгрия",
    "IS": "Исландия",
    "IN": "Индия",
    "ID": "Индонезия",
    "IR": "Иран, Исламская Республика",
    "IQ": "Ирак",
    "IE": "Ирландия",
    "IM": "Остров Мэн",
    "IL": "Израиль",
    "IT": "Италия",
    "JM": "Ямайка",
    "JP": "Япония",
    "JE": "Джерси",
    "JO": "Иордания",
    "KZ": "Казахстан",
    "KE": "Кения",
    "KI": "Кирибати",
    "KP": "Корейская Народно-Демократическая Республика",
    "KR": "Корея, Республика",
    "XK": "Косово",
    "KW": "Кувейт",
    "KG": "Киргизия",
    "LA": "Лаосская Народно-Демократическая Республика",
    "LV": "Латвия",
    "LB": "Ливан",
    "LS": "Лесото",
    "LR": "Либерия",
    "LY": "Ливия",
    "LI": "Лихтенштейн",
    "LT": "Литва",
    "LU": "Люксембург",
    "MO": "Макао",
    "MK": "Македония, бывшая югославская Республика",
    "MG": "Мадагаскар",
    "MW": "Малави",
    "MY": "Малайзия",
    "MV": "Мальдивы",
    "ML": "Мали",
    "MT": "Мальта",
    "MH": "Маршалловы Острова",
    "MQ": "Мартиника",
    "MR": "Мавритания",
    "MU": "Маврикий",
    "YT": "Майотта",
    "MX": "Мексика",
    "FM": "Микронезия, Федеративные Штаты",
    "MD": "Молдова, Республика",
    "MC": "Монако",
    "MN": "Монголия",
    "ME": "Черногория",
    "MS": "Монтсеррат",
    "MA": "Марокко",
    "MZ": "Мозамбик",
    "MM": "Мьянма",
    "NA": "Намибия",
    "NR": "Науру",
    "NP": "Непал",
    "NL": "Нидерланды",
    "AN": "Нидерландские Антильские острова",
    "NC": "Новая Каледония",
    "NZ": "Новая Зеландия",
    "NI": "Никарагуа",
    "NE": "Нигер",
    "NG": "Нигерия",
    "NU": "Ниуэ",
    "NF": "Остров Норфолк",
    "MP": "Северные Марианские Острова",
    "NO": "Норвегия",
    "OM": "Оман",
    "PK": "Пакистан",
    "PW": "Палау",
    "PS": "Палестина, Государство",
    "PA": "Панама",
    "PG": "Папуа - Новая Гвинея",
    "PY": "Парагвай",
    "PE": "Перу",
    "PH": "Филиппины",
    "PN": "Питкэрн",
    "PL": "Польша",
    "PT": "Португалия",
    "PR": "Пуэрто-Рико",
    "QA": "Катар",
    "RE": "Реюньон",
    "RO": "Румыния",
    "RU": "Российская Федерация",
    "RW": "Руанда",
    "SH": "Острова Святой Елены, Вознесения и Тристан-да-Кунья",
    "KN": "Сент-Китс и Невис",
    "LC": "Сент-Люсия",
    "BL": "Сен-Бартелеми",
    "MF": "Сен-Мартен (владение Франции)",
    "PM": "Сен-Пьер и Микелон",
    "VC": "Сент-Винсент и Гренадины",
    "WS": "Самоа",
    "SM": "Сан-Марино",
    "ST": "Сан-Томе и Принсипи",
    "SA": "Саудовская Аравия",
    "SN": "Сенегал",
    "RS": "Сербия",
    "SC": "Сейшельские Острова",
    "SL": "Сьерра-Леоне",
    "SG": "Сингапур",
    "SX": "Синт-Мартен (владение Нидерландов)",
    "SK": "Словакия",
    "SI": "Словения",
    "SB": "Соломоновы Острова",
    "SO": "Сомали",
    "ZA": "Южная Африка",
    "GS": "Южная Георгия и Южные Сандвичевы острова",
    "ES": "Испания",
    "LK": "Шри-Ланка",
    "SD": "Судан",
    "SR": "Суринам",
    "SS": "Южный Судан",
    "SJ": "Шпицберген и Ян-Майен",
    "SZ": "Эсватини",
    "SE": "Швеция",
    "CH": "Швейцария",
    "SY": "Сирийская Арабская Республика",
    "TW": "Тайвань",
    "TJ": "Таджикистан",
    "TZ": "Танзания, Объединенная Республика",
    "TH": "Таиланд",
    "TL": "Восточный Тимор",
    "TG": "Того",
    "TK": "Токелау",
    "TO": "Тонга",
    "TT": "Тринидад и Тобаго",
    "TN": "Тунис",
    "TR": "Турция",
    "TM": "Туркменистан",
    "TC": "Острова Теркс и Кайкос",
    "TV": "Тувалу",
    "UG": "Уганда",
    "UA": "Украина",
    "AE": "Объединенные Арабские Эмираты",
    "GB": "Великобритания",
    "US": "Соединенные Штаты Америки",
    "UM": "Внешние малые острова США",
    "UY": "Уругвай",
    "UZ": "Узбекистан",
    "VU": "Вануату",
    "VE": "Венесуэла, Боливарианская Республика",
    "VN": "Вьетнам",
    "VG": "Британские Виргинские Острова",
    "VI": "Виргинские острова, США",
    "WF": "Уоллис и Футуна",
    "EH": "Западная Сахара",
    "YE": "Йемен",
    "ZM": "Замбия",
    "XZ": "Международные воды",
    "ZW": "Зимбабве",
    "QO": "Океания",
    "ZZ": "Неизвестная страна"
  }


from tinydb import TinyDB, Query
db = TinyDB('db.json')
dbdata = Query()
table_dates = db.table('dates')
table_currencies = db.table('currencies')

# code change because of currency denomination: BYR → BYN, July 1, 2016
byr2bynDay  =  datetime.datetime.strptime("20160701", "%Y%m%d").date()
# https://github.com/carpedm20/emoji/blob/master/emoji/unicode_codes.py
curlist  = [
    [[r"\bдо[л]+ар",r"\bсша", r"\bштат", r"\bамерик", r"\bбакс", r":heavy_dollar_sign:", r'зел[её]н' ], ["USD"]],
	[[r"\bа[встр]+ал",r"\bдо[л]+ар"], ["AUD"]],
	[[r"\bазербайджан",r"\bманат"], ["AZN"]],
	[[r"\bфунт",r"\bстерлинг",r"\bвеликобрит",r"\bкоролевств", r"\bбритан", r":England:", r":Scotland:", r":Wales:", r'£'], ["GBP"]],
	[[r"\bармян", r"\bармен",r"\bдрам"], ["AMD"]],
	[[r"\bбел", r"\bбелорус", r"\bбеларус", r"\bрубе?л"], ["BYN"]],
	[[r"\bболгар",r"\bлев"], ["BGN"]],
	[[r"\bбразил",r"\bреал"], ["BRL"]],
	[[r"\bвенгер",r"\bвенгр",r"\bфоринт"], ["HUF"]],
	[[r"\bг[оа]нконг",r"\bдо[л]+ар"], ["HKD"]],
	[[r"\bдатск", r"\bдацк", r"\bдан",r"\bкрон"], ["DKK"]],	
	[[r"\bевр", r"€", r":European_Union:"], ["EUR"]],
	[[r"\bинди",r"\bрупи"], ["INR"]],
	[[r"\bказах",r"\bтенге"], ["KZT"]],
	[[r"\bканад",r"\bдо[л]+ар"], ["CAD"]],
	[[r"\bкиргиз",r"\bсом"], ["KGS"]],
	[[r"\bкитай",r"\bюан"], ["CNY"]],
	[[r"\bмолдав", r"\bмолдов",r"\bлее", r"\bлея", r"\bлей"], ["MDL"]],
	[[r"\bнорвеж",r"\bнорвег",r"\bкрон"], ["NOK"]],
	[[r"\bпольск",r"\bпольш",r"\bзлот"], ["PLN"]],
	[[r"\bрумын",r"\bлее", r"\bлея", r"\bлей"], ["RON"]],
	[[r"\bсдр"], ["XDR"]],
	[[r"\bсингапур",r"\bдо[л]+ар"], ["SGD"]],
	[[r"\bтаджи[кц]",r"\bсомон"], ["TJS"]],
	[[r"\bтурец",r"\bтурц",r"\bлир"], ["TRY"]],
	[[r"\bтуркмен",r"\bманат"], ["TMT"]],
	[[r"\bузбе[кц]",r"\bсум"], ["UZS"]],
	[[r"\bукраин",r"\bгривен", r"\bгривн"], ["UAH"]],
	[[r"\bчешс", r"\bчеx",r"\bкрон"], ["CZK"]],
	[[r"\bшведс",r"\bшвец",r"\bкрон"], ["SEK"]],
	[[r"\bшвейцар",r"\bфранк"], ["CHF"]],
	[[r"\bюжноафрикан", r"\bафрик", r"\bрэнд",r"\bранд"], ["ZAR"]],
	[[r"\bвон",r"\bкорея", r"\bкорей"], ["KRW"]],
	[[r"\bяпон",r"\bиен",r"\bен", r'¥'], ["JPY"]]
]
popular_currencies = [c[1][0] for c in curlist]

def getCode(userinput):
    qs  = userinput.split()
    rating  = {}
    for item in curlist:
        curCode = item[1][0]
        for chunk in item[0]:
            for q in qs:
                # print(chunk, q)
                if re.match(chunk, q):
                    if curCode in rating:
                        rating[curCode] += 1
                    else:
                        rating[curCode] = 1
    # print (rating)
    if "USD" in rating and max(rating.values()) == 1: rating["USD"] += 1
    return max(rating, key=rating.get) if rating else "USD"

def datestring2date(datestring):
    return  datetime.datetime.strptime(datestring, '%d%m%Y').date()
    
def CBRdate(this_date):
    return this_date.strftime("%d/%m/%Y")

def getCBRdata(url, data={}):
    r = requests.get(url, params=data)
    if r.status_code == 200:
        xml = r.text
        d = xmltodict.parse(xml, attr_prefix = "")
        # print(json.dumps(d, indent=4, ensure_ascii=False))
    return d

def processCurrencies(code = "USD", indate = datetime.date.today()):    
    bankdate = CBRdate(indate)
    # print(code, bankdate)
    # CBRdate(datestring2date('24052019'))
    fulldata = table_dates.search((dbdata.date == bankdate) & (dbdata.type == "currency"))
    if code  == "BYN" and (indate - byr2bynDay).days < 0: 
        code  = "BYR"     
    
    if not fulldata:
        print("call ext API")        
        currencies_data  = getCBRdata("http://www.cbr.ru/scripts/XML_daily.asp", \
        {'date_req': bankdate})
        if currencies_data:
            table_dates.insert({'date': bankdate, 'type': "currency"})
            # print (currencies_data["ValCurs"]["Date"], bankdate)
            for x in currencies_data["ValCurs"]["Valute"]:
                print("[\""+x["Name"].lower() + "\"] = \"" +  x["CharCode"] + "\"")
                currencies_object = {'reqdate': bankdate, 'realdate':  currencies_data["ValCurs"]["Date"].replace(".", "/"), 'code': x["CharCode"], "nom": int(x["Nominal"]), "name": x["Name"], "val": float(x["Value"].replace(",", "."))}
                table_currencies.insert(currencies_object)
                if x["CharCode"] == code: 
                    data = currencies_object
            # print(currencies_data)
    else:
        print(code)
        fulldata = table_currencies.search((dbdata.code == code) & (dbdata.reqdate == bankdate))
        data = fulldata[0] if fulldata else None
    return data

# def extract_emojis(str):
  # return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)
  
def processRequest(userinput, userdate=None):
    # emojis  = re.findall(r'[^\w\s,]', userinput)
    res = "Нет данных на эту дату"
    country_name = ""
    currency_code = None
    state_code = None
    for state in states:
        if state["emoji"] in userinput:
            state_code = state["code"]
            print(state["code"], state2code[state["code"]])
            country_name = code2country[state["code"]]
            currency_code = state2code[state["code"]]
            break
            
    if not currency_code:        
        userinput = emoji.demojize(userinput)
        print(userinput)
        currency_code = getCode(userinput)
        
    bankdate  = datestring2date(userdate) if userdate else datetime.date.today()
    if currency_code:
        if currency_code  == "GIP":
            currency_code  = "GBP" 
        
        if currency_code == "RUB":
            res = "1 российский рубль стоит 1 российский рубль"
        elif currency_code in popular_currencies:
            data  = processCurrencies(currency_code, bankdate)
            # print(f"{data['nom']} {data['name']} = {str(data['val']).replace('.', ',')}₽")
            if data:
                prefix = ""
                if ((currency_code  == "USD" and state_code != "US") or (currency_code  == "EUR" and state_code != "EU")) and country_name:
                    prefix = country_name + ". "
                    
                res = prefix + str(data['nom']) +" "+ \
                data['name'][:1].lower() + data['name'][1:] + " = " + \
                str(data['val']).replace('.', ',')+"₽" 
            else:
                pass
        else:
            cur_eng = " (" + currencies_info[currency_code]["name"] + ")" if \
            currency_code in currencies_info else ""
                
            res = "Страна валюты – " + country_name + \
            ". Нет данных по курсу этой валюты" + cur_eng
    else:
        res = "Нет данных об этой валюте"
    
    print(res)
    return res

# query = "доллар"
# res  = getCode(query)
# print(res)




# curl  = "https://www.sberbank.ru/portalserver/proxy/?pipe=shortCachePipe&url=http://localhost/rates-web/rateService/rate/current%3FregionId%3D77%26currencyCode%3D840%26currencyCode%3D978%26rateCategory%3Dbeznal"

# ಠ_ಠ  = "ololo"
# print(ಠ_ಠ)

# r = requests.get(curl)
# if r.status_code == 200:
    # d = r.json()
    # print(d)
