
import sys
import re
import datetime
import requests, unicodedata
import xmltodict, json
import emoji
# https://github.com/martinblech/xmltodict

from datum import * 

from tinydb import TinyDB, Query
db = TinyDB('db.json')
dbdata = Query()
table_dates = db.table('dates')
table_currencies = db.table('currencies')

# code change because of currency denomination: BYR → BYN, July 1, 2016
byr2bynDay  =  datetime.datetime.strptime("20160701", "%Y%m%d").date()
# https://github.com/carpedm20/emoji/blob/master/emoji/unicode_codes.py
curlist  = {    
    "cs" : [
        [["Zcash"], ["ZEC"]],
        [[r"\bд[эа]ш"], ["DASH"]],
        [[r"\bла[йи]тко[ийе]н", ], ["LTC"]],
        [[r"\bдоге", ], ["DOGE"]],
        ],
    "bc" : [
        [[r"\bбит[о]к",r"\bбитко[ийе]н", r"₿" ], ["BTC"]],
        ],
    "es" : [ # 
        [[r"\bэфир",r"\bэтер", r"Ξ" ], ["ETH"]],
        ],
    "cbr": [
        [[r"\bдо[л]+ар", r"\bбакс", r":heavy_dollar_sign:", r'зел[её]н' ], ["USD"]],
        [[r"\bдо[л]+ар"], ["AUD"]],
        [[r"\bманат"], ["AZN"]],
        [[r"\bфунт",r"\bстерлинг", r'£'], ["GBP"]],
        [[r"\bдрам"], ["AMD"]],
        [[r"\bрубе?л"], ["BYN"]],
        [[r"\bлев"], ["BGN"]],
        [[r"\bреал"], ["BRL"]],
        [[r"\bфоринт"], ["HUF"]],
        [[r"\bдо[л]+ар"], ["HKD"]],
        [[r"\bкрон"], ["DKK"]],	
        [[r"\bевро\b", r"€"], ["EUR"]],
        [[r"\bрупи"], ["INR"]],
        [[r"\bтенге"], ["KZT"]],
        [[r"\bдо[л]+ар"], ["CAD"]],
        [[r"\bсом"], ["KGS"]],
        [[r"\bюан"], ["CNY"]],
        [[r"\bлее", r"\bлея", r"\bлей"], ["MDL"]],
        [[r"\bкрон"], ["NOK"]],
        [[r"\bзлот"], ["PLN"]],
        [[r"\bлее", r"\bлея", r"\bлей"], ["RON"]],
        [[r"\bсдр"], ["XDR"]],
        [[r"\bдо[л]+ар"], ["SGD"]],
        [[r"\bсомон"], ["TJS"]],
        [[r"\bлир"], ["TRY"]],
        [[r"\bманат"], ["TMT"]],
        [[r"\bсум"], ["UZS"]],
        [[r"\bгривен", r"\bгривн"], ["UAH"]],
        [[r"\bкрон"], ["CZK"]],
        [[r"\bкрон"], ["SEK"]],
        [[r"\bфранк"], ["CHF"]],
        [[r"\bрэнд",r"\bранд"], ["ZAR"]],
        [[r"\bвон"], ["KRW"]],
        [[r"\bиен",r"\bен", r'¥'], ["JPY"]]
        ],
}
popular_currencies = [c[1][0] for c in curlist["cbr"]]

def getCode(userinput, ruleset="cbr"):
    qs  = userinput.split()
    rating  = {}
    tags  = [None] * len(qs)

    for i, q in enumerate(qs):            
        # print(chunk, q)
        for twoletter in staterules:
            for rule in staterules[twoletter]:
                # print(rule, "=", q)
                if re.match(rule, q):
                    # print(twoletter, rule)
                    if tags[i] == None:
                        tags[i] = {"STT": []}
                    tags[i]["STT"].append(state2code[twoletter])
                    
        for item in curlist[ruleset]:
            curCode = item[1][0]
            for chunk in (item[0]+ [curCode.lower()]):
                if re.match(chunk, q):
                    if tags[i] == None:
                        tags[i] = {"CUR": []}
                    tags[i]["CUR"].append(curCode)
                    # if curCode in rating:
                        # rating[curCode] += 1
                    # else:
                        # rating[curCode] = 1
    
            # print(chunk)
    
    print (tags)
    arr = []
    for tag in tags:
        if tag:
            vals = list(tag.values())
            if vals:
                arr.extend(vals)
    flat = [item for sublist in arr for item in sublist]    
    # print(arr)
    print(flat)
    res  = max(flat, key=flat.count)
    # print({x:a.count(x) for x in a})
    return res if res else None
    # if "USD" in rating and max(rating.values()) == 1: rating["USD"] += 1
    # return max(rating, key=rating.get) if rating else None

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

def getBTC():
    r = requests.get("https://blockchain.info/ticker")
    # r = requests.get("https://blockchain.info/tobtc?currency=RUB&value=1")
    d  = None
    if r.status_code == 200:
        d = r.json()
    return d    

def getETH():
    r = requests.get("https://api.etherscan.io/api?module=stats&action=ethprice&apikey=YourApiKeyToken")
    d  = None
    if r.status_code == 200:
        d = r.json()["result"]["ethusd"]
    return d
    
# https://chain.so/api#code-examples    
def getChainSo(code):
    r = requests.get("https://chain.so/api/v2/get_price/" + code)
    d  = None
    if r.status_code == 200:
        data = r.json()["data"]["prices"][0]
        price  = float(data["price"])
        price_base = data["price_base"]
        base  = processCurrencies(price_base)
        d  = price * float(base["val"])
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
                # print("[\""+x["Name"].lower() + "\"] = \"" +  x["CharCode"] + "\"")
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
        currency_code = getCode(userinput, "cbr")
        if not currency_code:
            currency_code = getCode(userinput, "bc")

        if not currency_code:
            currency_code = getCode(userinput, "es")
        
        if not currency_code:
            currency_code = getCode(userinput, "cs")
        
    bankdate  = datestring2date(userdate) if userdate else datetime.date.today()
    if currency_code:
        if currency_code  == "GIP":
            currency_code  = "GBP"
        
        if currency_code == "RUB":
            res = "1 российский рубль стоит 1 российский рубль"
        elif currency_code == "BTC":
            # btcInRub  = "%.9f" % getBTC()
            # res = "1 ₿ = "+  btcInRub.rstrip('0') + "₽" 
            bcdata = getBTC()
            res = "1₿ = "+  ("%.4f" % bcdata["RUB"]["last"]).rstrip('0') + "₽" 
        elif currency_code in ["LTC", "DOGE", "ZEC"]: # , "BTC"
            # btcInRub  = "%.9f" % getBTC()
            # res = "1 ₿ = "+  btcInRub.rstrip('0') + "₽" 
            rub = getChainSo(currency_code)
            res = "1 " + currency_code + " = "+  ("%.2f" % rub).rstrip('0') + "₽" 
        elif currency_code == "ETH":
            ethdata = getETH()
            usd  = processCurrencies()
            # print(ethdata, usd["val"])
            res = "1 ETH = "+  ethdata + "$ (≈" + str("%.0f" %(usd["val"]*float(ethdata)))+"₽)"
        elif currency_code in popular_currencies:
            data  = processCurrencies(currency_code, bankdate)
            # print(f"{data['nom']} {data['name']} = {str(data['val']).replace('.', ',')}₽")
            if data:
                prefix = ""
                if ((currency_code  == "USD" and state_code != "US") or (currency_code  == "EUR" and state_code != "EU")) and country_name:
                    prefix = country_name + ". "
                    
                res = prefix + str(data['nom']) +" "+ \
                data['name'][:1].lower() + data['name'][1:] + " = " + \
                ("%.2f" % data['val']).replace('.', ',')+"₽" 
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
