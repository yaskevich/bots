#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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

popular_currencies = [c[1][0] for c in curlist["cbr"]]

# state

def getCur(tags):
    arr = []
    for tag in tags:
        if tag:
            vals = list(tag.values())
            if vals:
                arr.extend(vals)
    flat = [item for sublist in arr for item in sublist]    
    return max(flat, key=flat.count) if flat else None
    
def getCode(userinput):
    qs  = userinput.split()
    rating  = {}
    tags  = [None] * len(qs)
    src = {}
    country = []
    for i, q in enumerate(qs):            
        print(i, q)
        if re.match(r"\d+", q):
            tags[i] = {"NUM": q}
        
        for twoletter in staterules:
            for rule in staterules[twoletter]:
                # print(rule, "=", q)
                if re.match(rule, q, flags=re.IGNORECASE):
                    # print(twoletter, rule)
                    if tags[i] == None:
                        tags[i] = {"STT": []}
                    countryCode = state2code[twoletter]
                    print("now",twoletter)
                    tags[i]["STT"].append(countryCode)
                    country.append(twoletter)
        
        
        for k in list(curlist.keys()):
            for item in curlist[k]:
                curCode = item[1][0]
                for chunk in (item[0]+ [curCode.lower()]):
                    if re.match(chunk, q):
                        if tags[i] == None:
                            tags[i] = {"CUR": []}
                        tags[i]["CUR"].append(curCode)
                        src[curCode] = k

    print (tags)
    print (src)
    
    grammar = ""
    for tt in tags:
        grammar += next(iter(tt)) if tt else "" # SEP
        grammar += " "
    
    # grammar = re.sub(r"^(SEP)\s+","", grammar)
    print(grammar)
    
    
    amount  = 1
    slots = []
    current_slot = 0
    res =  {type: "na"}
    
    # print(tags)
    # NUM STT CUR
    if re.match ("\s*NUM\s*[STT]*\s*CUR\s*[STT]*\s*CUR", grammar):
        # print("bingo")
        for i, item in enumerate(tags):            
        # for item in tags:
            # print(">", item)
            if item:
                key = next(iter(item))
                if key in ['STT', 'CUR']:
                    # print("lol", item)
                    try:
                        slots[current_slot].extend(item[key])
                    except IndexError:
                        slots.append(item[key])
                    # if slots
                    
                elif item and 'NUM' in item:
                    amount = item['NUM']               
                    # print(item['NUM'])
                    # del tags[i]
            else:
                current_slot +=1
        print(slots[0], slots[1])
        if slots[1] == ['RUB', 'BYN']:
            slots[1] = ['RUB']
        c1 = max(slots[0], key=slots[0].count)
        c2 = max(slots[1], key=slots[1].count)
        res  = {"type":"con", "qty": amount, "c1": c1, "c2": c2, "src1": src[c1], "src2": src[c2]}
    elif not re.findall("CUR", grammar):
        print("not cur")
        return None
    else:
        print("fallback")
        cc = getCur(tags)
        # {'RUB': 'ru', 'BYN': 'cbr'}
        # print(cc, src)
        this_src = ""
        if not src:
            if cc in popular_currencies:
                this_src = "cbr" 
            else:
                this_src = "na"
        else:
            if cc in src:
                print("aaa", src, cc)
                this_src =  src[cc]
        
        res = {"type":"cur", "code":cc, "src": this_src, "country": country} if this_src else None
    return res
 
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

def getBTC(data, date):
    r = requests.get("https://blockchain.info/ticker")
    # r = requests.get("https://blockchain.info/tobtc?currency=RUB&value=1")
    d  = None
    if r.status_code == 200:
        json = r.json()
        d  = json["RUB"]["last"]
    return { "rub": d }


# https://chain.so/api#code-examples    
def getChainSo(data, date):
    r = requests.get("https://chain.so/api/v2/get_price/" + data["code"])
    d  = None
    if r.status_code == 200:
        datum = r.json()["data"]["prices"][0]
        price  = float(datum["price"])
        price_base = datum["price_base"]
        base  = processCurrencies(price_base)
        d  = price * float(base["val"])
    return { "rub": d }

def getETH(data, date):
    r = requests.get("https://api.etherscan.io/api?module=stats&action=ethprice&apikey=YourApiKeyToken")
    d  = None
    if r.status_code == 200:
        d = r.json()["result"]["ethusd"]
        usd  = processCurrencies()        
    return { "rub": float(d)*usd["val"], "usd": d }

def processCurrencies(data, indate = datetime.date.today()):   

    code  = data["code"] if "code" in data else "USD"
    # print("ccu", code, indate)
    # sys.exit()
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
                    datum = currencies_object
            # print(currencies_data)
    else:
        print(code)
        fulldata = table_currencies.search((dbdata.code == code) & (dbdata.reqdate == bankdate))
        datum = fulldata[0] if fulldata else None
    if datum: 
        datum["rub"] = datum["val"] # just to not update db, renew db later
        # print("dfdsfsdfs", data)
        # datum["country"] = data["country"][0]
    # print("cbr", datum)
    return datum

# def extract_emojis(str):
  # return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)
  
def stub(data, date):
    return { "rub": 1}  
    
processor = {
    "cs": getChainSo,
    "bc": getBTC,
    "es": getETH,
    "cbr": processCurrencies,
    "ru" : stub
    
}
symbols = {
    "BTC": "₿",
    "USD": "$",
    "AUD": "$",
    "CAD": "$",
    "RUB": "₽",
    "BYN": "₽",
    "UAH": "₴",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CNY": "¥",
    "ILS": "₪",
    "INR": "₨",
    "KRW": "₩",
    "NGN": "₦",
    "THB": "฿",
    "KZT": "₸",
}

def flagByCode(code):
    flags  = [st["emoji"] for st in states if st["code"] == code[0:2]]
    flag  = flags[0] if flags else code
    if code in ["BTC", "ETH", "ZEC", "DOGE", "LTC"]:
        flag = ""
    return flag

def output(data, bankdate):
    currency = data["code"]
    group = data["src"]
    res = None
    if data["src"] == "na":
        if not data["code"]:
            return "Нет информации"
            
        cur_eng = " (" + currencies_info[currency]["name"] + ")" if \
                currency in currencies_info else ""
        res  = ""
        if data and "country" in data and data["country"]:
            res = "Страна валюты – " + code2country[data["country"][0]] + ". "
        res += "Нет данных по курсу этой валюты" + cur_eng
        return res
    new_data = processor[group](data, bankdate)
    threshold=2 
    frm = "%."+str(threshold)+"f"    
    if currency in symbols:
        currency = symbols[currency]
    
    
    
    flag  = flagByCode(data["code"])
    
  
    
    if new_data and "usd" in new_data:
        res = "1" + currency + "= "+  new_data["usd"] + "$ (≈" + str("%.0f" %(new_data["rub"]))+"₽)"
    elif group == "cbr":
        print("common", new_data)
        if new_data:
            prefix = ""
            postfix = " (на дату " + new_data["realdate"] + ")" if "realdate" in new_data else ""
            # print("=====", new_data)
            if data["country"]:
                if ((currency  == "USD" and data["country"][0] != "US") or (currency  == "EUR" and data["country"][0] != "EU")):
                    country_name = code2country[data["country"][0]]
                    prefix = country_name + ". "
            # # new_data['name'][:1].lower() + new_data['name'][1:] + " = " + \    
            
            res = str(new_data['nom']) + currency + flag + "= " + \
            ("%.2f" % new_data['val']).replace('.', ',')+"₽🇷🇺" + postfix
    else:
        # print("else", res)
        # res =  "1" + currency + flag + "= "+  (frm % new_data["rub"]).rstrip('0').rstrip('.') + "₽🇷🇺" 
        res =  "1" + currency + flag + "= "+  (frm % new_data["rub"]) + "₽🇷🇺" 
    return res
    
def processRequest(userinput, userdate=None):
    # emojis  = re.findall(r'[^\w\s,]', userinput)
    # if not re.match("курс", grammar):
    bankdate  = datestring2date(userdate) if userdate else datetime.date.today()
    res = None
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
        # print("input", userinput)
        
        
        data = getCode(userinput)
        print("data", data)
        if data:
            if data["type"] == "cur":
                if data["code"] == "GIP": data["code"] = "GBP" 
                formatted  = output(data, bankdate)
                res  = formatted if formatted else "Нет данных на эту дату"
                
                # if currency_code == "RUB":
                    # res = "1 российский рубль стоит 1 российский рубль"
                # else:
                   
            elif data["type"] == "con":
                print("Conversion implement", data)
                c1 = {"code": data["c1"]}
                c2 = {"code": data["c2"]}
                f1 = flagByCode(data["c1"])
                f2 = flagByCode(data["c2"])
                s1 = symbols[data["c1"]] if data["c1"] in symbols else data["c1"]
                s2 = symbols[data["c2"]] if data["c2"] in symbols else data["c2"]
                
                c1_res = processor[data["src1"]](c1, bankdate)
                c2_res = processor[data["src2"]](c2, bankdate)
                
                c1_nom  = float(c1_res["nom"]) if "nom" in c1_res else 1
                c2_nom  = float(c2_res["nom"]) if "nom" in c2_res else 1
                
                # print("wow", c1_res, c2_res,)
                # print("wow", float(c1_res["rub"]), float(c2_res["rub"]))
                n1  = float(data["qty"])* float(c1_res["rub"])/c1_nom 
                n2  = float(c2_res["rub"]) / c2_nom
                # print(n1, n2)
                number = n1/n2
                # print("wow", number)
                out  = ("%.2f" % number)
                sign  = "="
                if out == "0.00":
                    sign = "<"
                    out = "0.01"
                
                    
                res =  data["qty"] + s1 + f1 + sign +" "+  out + s2 + f2  
                
            else:
                res = "Нет данных"
    
    print(res)
    return res if res else ""

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
