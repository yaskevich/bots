import re
import datetime
import requests, unicodedata
import xmltodict, json
import emoji
# https://github.com/martinblech/xmltodict

import json
# https://github.com/matiassingers/emoji-flags/blob/master/data.json
with open('states.json') as json_file:  
    states = json.load(json_file)

state2code = {"BD": "BDT", "BE": "EUR", "BF": "XOF", "BG": "BGN", "BA": "BAM", "BB": "BBD", "WF": "XPF", "BL": "EUR", "BM": "BMD", "BN": "BND", "BO": "BOB", "BH": "BHD", "BI": "BIF", "BJ": "XOF", "BT": "BTN", "JM": "JMD", "BV": "NOK", "BW": "BWP", "WS": "WST", "BQ": "USD", "BR": "BRL", "BS": "BSD", "JE": "GBP", "BY": "BYN", "BZ": "BZD", "RU": "RUB", "RW": "RWF", "RS": "RSD", "TL": "USD", "RE": "EUR", "TM": "TMT", "TJ": "TJS", "RO": "RON", "TK": "NZD", "GW": "XOF", "GU": "USD", "GT": "GTQ", "GS": "GBP", "GR": "EUR", "GQ": "XAF", "GP": "EUR", "JP": "JPY", "GY": "GYD", "GG": "GBP", "GF": "EUR", "GE": "GEL", "GD": "XCD", "GB": "GBP", "GA": "XAF", "SV": "USD", "GN": "GNF", "GM": "GMD", "GL": "DKK", "GI": "GIP", "GH": "GHS", "OM": "OMR", "TN": "TND", "JO": "JOD", "HR": "HRK", "HT": "HTG", "HU": "HUF", "HK": "HKD", "HN": "HNL", "HM": "AUD", "VE": "VEF", "PR": "USD", "PS": "ILS", "PW": "USD", "PT": "EUR", "SJ": "NOK", "PY": "PYG", "IQ": "IQD", "PA": "PAB", "PF": "XPF", "PG": "PGK", "PE": "PEN", "PK": "PKR", "PH": "PHP", "PN": "NZD", "PL": "PLN", "PM": "EUR", "ZM": "ZMK", "EH": "MAD", "EE": "EUR", "EG": "EGP", "ZA": "ZAR", "EC": "USD", "IT": "EUR", "VN": "VND", "SB": "SBD", "ET": "ETB", "SO": "SOS", "ZW": "ZWL", "SA": "SAR", "ES": "EUR", "ER": "ERN", "ME": "EUR", "MD": "MDL", "MG": "MGA", "MF": "EUR", "MA": "MAD", "MC": "EUR", "UZ": "UZS", "MM": "MMK", "ML": "XOF", "MO": "MOP", "MN": "MNT", "MH": "USD", "MK": "MKD", "MU": "MUR", "MT": "EUR", "MW": "MWK", "MV": "MVR", "MQ": "EUR", "MP": "USD", "MS": "XCD", "MR": "MRO", "IM": "GBP", "UG": "UGX", "TZ": "TZS", "MY": "MYR", "MX": "MXN", "IL": "ILS", "FR": "EUR", "IO": "USD", "SH": "SHP", "FI": "EUR", "FJ": "FJD", "FK": "FKP", "FM": "USD", "FO": "DKK", "NI": "NIO", "NL": "EUR", "NO": "NOK", "NA": "NAD", "VU": "VUV", "NC": "XPF", "NE": "XOF", "NF": "AUD", "NG": "NGN", "NZ": "NZD", "NP": "NPR", "NR": "AUD", "NU": "NZD", "CK": "NZD", "XK": "EUR", "CI": "XOF", "CH": "CHF", "CO": "COP", "CN": "CNY", "CM": "XAF", "CL": "CLP", "CC": "AUD", "CA": "CAD", "CG": "XAF", "CF": "XAF", "CD": "CDF", "CZ": "CZK", "CY": "EUR", "CX": "AUD", "CR": "CRC", "CW": "ANG", "CV": "CVE", "CU": "CUP", "SZ": "SZL", "SY": "SYP", "SX": "ANG", "KG": "KGS", "KE": "KES", "SS": "SSP", "SR": "SRD", "KI": "AUD", "KH": "KHR", "KN": "XCD", "KM": "KMF", "ST": "STD", "SK": "EUR", "KR": "KRW", "SI": "EUR", "KP": "KPW", "KW": "KWD", "SN": "XOF", "SM": "EUR", "SL": "SLL", "SC": "SCR", "KZ": "KZT", "KY": "KYD", "SG": "SGD", "SE": "SEK", "SD": "SDG", "DO": "DOP", "DM": "XCD", "DJ": "DJF", "DK": "DKK", "VG": "USD", "DE": "EUR", "YE": "YER", "DZ": "DZD", "US": "USD", "UY": "UYU", "YT": "EUR", "UM": "USD", "LB": "LBP", "LC": "XCD", "LA": "LAK", "TV": "AUD", "TW": "TWD", "TT": "TTD", "TR": "TRY", "LK": "LKR", "LI": "CHF", "LV": "EUR", "TO": "TOP", "LT": "LTL", "LU": "EUR", "LR": "LRD", "LS": "LSL", "TH": "THB", "TF": "EUR", "TG": "XOF", "TD": "XAF", "TC": "USD", "LY": "LYD", "VA": "EUR", "VC": "XCD", "AE": "AED", "AD": "EUR", "AG": "XCD", "AF": "AFN", "AI": "XCD", "VI": "USD", "IS": "ISK", "IR": "IRR", "AM": "AMD", "AL": "ALL", "AO": "AOA", "AQ": "", "AS": "USD", "AR": "ARS", "AU": "AUD", "AT": "EUR", "AW": "AWG", "IN": "INR", "AX": "EUR", "AZ": "AZN", "IE": "EUR", "ID": "IDR", "UA": "UAH", "QA": "QAR", "MZ": "MZN"}

from tinydb import TinyDB, Query
db = TinyDB('db.json')
dbdata = Query()
table_dates = db.table('dates')
table_currencies = db.table('currencies')

# code change because of currency denomination: BYR → BYN, July 1, 2016
byr2bynDay  =  datetime.datetime.strptime("20160701", "%Y%m%d").date()
# https://github.com/carpedm20/emoji/blob/master/emoji/unicode_codes.py
curlist  = [
    [[r"\bдо[л]+ар",r"\bсша", r"\bштат", r"\bамерик", r"\bбакс", r":United_States:", r":heavy_dollar_sign:", r'зел[её]н' ], ["USD"]],
	[[r"\bа[встр]+ал",r"\bдо[л]+ар"], ["AUD"]],
	[[r"\bазербайджан",r"\bманат", r":Azerbaijan:"], ["AZN"]],
	[[r"\bфунт",r"\bстерлинг",r"\bвеликобрит",r"\bкоролевств", r"\bбритан", r':United_Kingdom:', r'£'], ["GBP"]],
	[[r"\bармян", r"\bармен",r"\bдрам", r":Armenia:"], ["AMD"]],
	[[r"\bбел", r"\bбелорус", r"\bбеларус",r"\bруб[e]?л", r":Belarus:"], ["BYN"]],
	[[r"\bболгар",r"\bлев", r":Bulgaria:"], ["BGN"]],
	[[r"\bбразил",r"\bреал", r':Brazil:'], ["BRL"]],
	[[r"\bвенгер",r"\bвенгр",r"\bфоринт", r':Hungary:'], ["HUF"]],
	[[r"\bг[оа]нконг",r"\bдо[л]+ар", r':Hong_Kong_SAR_China:'], ["HKD"]],
	[[r"\bдатск", r"\bдацк", r"\bдан",r"\bкрон", r':Denmark:'], ["DKK"]],	
	[[r"\bевр", r"€", r":European_Union:"], ["EUR"]],
	[[r"\bинди",r"\bрупи", r':India:'], ["INR"]],
	[[r"\bказах",r"\bтенге", r':Kazakhstan:'], ["KZT"]],
	[[r"\bканад",r"\bдо[л]+ар", r':Canada:'], ["CAD"]],
	[[r"\bкиргиз",r"\bсом", r':Kyrgyzstan:'], ["KGS"]],
	[[r"\bкитай",r"\bюан", r':China:'], ["CNY"]],
	[[r"\bмолдав", r"\bмолдов",r"\bлее", r"\bлея", r"\bлей", r':Moldova:'], ["MDL"]],
	[[r"\bнорвеж",r"\bнорвег",r"\bкрон", r':Norway:'], ["NOK"]],
	[[r"\bпольск",r"\bпольш",r"\bзлот", r':Poland:'], ["PLN"]],
	[[r"\bрумын",r"\bлее", r"\bлея", r"\bлей", r':Romania:'], ["RON"]],
	[[r"\bсдр", r':United_Nations:'], ["XDR"]],
	[[r"\bсингапур",r"\bдо[л]+ар", r':Singapore:'], ["SGD"]],
	[[r"\bтаджи[кц]",r"\bсомон", r':Tajikistan:'], ["TJS"]],
	[[r"\bтурец",r"\bтурц",r"\bлир", r':Turkey:'], ["TRY"]],
	[[r"\bтуркмен",r"\bманат", r':Turkmenistan:'], ["TMT"]],
	[[r"\bузбе[кц]",r"\bсум", r':Uzbekistan:'], ["UZS"]],
	[[r"\bукраин",r"\bгривен", r"\bгривн", r':Ukraine:'], ["UAH"]],
	[[r"\bчешс", r"\bчеx",r"\bкрон", r':Czechia:'], ["CZK"]],
	[[r"\bшведс",r"\bшвец",r"\bкрон", r':Sweden:'], ["SEK"]],
	[[r"\bшвейцар",r"\bфранк", r':Switzerland:'], ["CHF"]],
	[[r"\bюжноафрикан", r"\bафрик", r"\bрэнд",r"\bранд", r':South_Africa:'], ["ZAR"]],
	[[r"\bвон",r"\bкорея", r"\bкорей", r':South_Korea:'], ["KRW"]],
	[[r"\bяпон",r"\bиен",r"\bен", r':Japan:', r'¥'], ["JPY"]]
]

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
    if code  == "BYN" and (indate - byr2bynDay).days < 0: code  = "BYR"    
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

def extract_emojis(str):
  return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)
  
def processRequest(userinput, userdate=None):
    # emojis  = re.findall(r'[^\w\s,]', userinput)
    for state in states:
        if state["emoji"] in userinput:
            print(state["code"], state2code[state["code"]])
    userinput = emoji.demojize(userinput)
    print(userinput)

    currency_code = getCode(userinput)
    bankdate  = datestring2date(userdate) if userdate else datetime.date.today()
    data  = processCurrencies(currency_code, bankdate)
    # print(f"{data['nom']} {data['name']} = {str(data['val']).replace('.', ',')}₽")
    
    res = str(data['nom']) +" "+ data['name'][:1].lower() + data['name'][1:]   + " = "+ str(data['val']).replace('.', ',')+"₽" \
    if data else "Нет данных на эту дату"
    
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
