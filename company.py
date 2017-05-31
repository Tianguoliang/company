#coding:utf-8
#Actor:Tyson
import time
import requests
from bs4 import BeautifulSoup
import pymongo
import re
import json
from urllib import parse
from config import *
from multiprocessing import Pool
import random
client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]
def search_company_information(keyword,p):
    session = requests.session()
    a={'http':'111.20.214.25:9999'},{'http':'200.29.191.151:3128'}
    session.proxies=random.choice(a)
    b="111.20.214.25",'200.29.191.151'
    session.cookies.set("tnet", random.choice(b))
    start_url = 'http://www.tianyancha.com/search/or'
    keyword8=parse.quote(keyword)   #把索引关键字转换为Unicode码
    public_headerses={"User-Agent":'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'},\
                 {"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36"},
    {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"}
    public_headers =random.choice(public_headerses)
    api_headers = public_headers.copy()
    index_url = start_url + str(start) + str(end)+'/p{}?key='.format(str(p))+str(keyword8) #
    # print('index_url')
    # print(index_url)
    tongji_url = "http://www.tianyancha.com/tongji/"+keyword+str(".json?random=%s") % (int(time.time()) * 1000)
    api_url = "http://www.tianyancha.com/search/"+keyword+str(".json?&pn=%s&moneyStart=%s&moneyEnd=%s") % (p,start,end)
    # print('api_url')
    # print(api_url)
    api_headers.update({
        "Tyc-From": "normal",
        "Accept": "application/json, text/plain, */*",
        "Referer": index_url,
        "Accept-Encoding":"gzip, deflate, sdch"
    })
    # print('api-heders')
    # print (api_headers)
    index_page = session.request("GET", index_url, headers = public_headers)

    soup = BeautifulSoup(index_page.text,'lxml')
    a=(soup.select('script'))

    s=re.compile('src="(.*?)">',re.S)
    js_url=re.findall(s,str(a))[0]
    # print('js_url')
    # print (js_url)

    js_page = session.request("GET", js_url, headers = public_headers)

    try:
        sgattrs = json.loads(re.findall(r"n\._sgArr=(.+?);", str(js_page.content))[0])
    except json.JSONDecodeError:
        print('求sgattrs出错')
        return None
    tongji_page = session.request("GET", tongji_url, headers = api_headers)

    js_code = "".join([ chr(int(code)) for code in tongji_page.json()["data"]["v"].split(",") ])
    token = re.findall(r"token=(\w+);", js_code)[0]

    fxck_chars = re.findall(r"\'([\d\,]+)\'", js_code)[0].split(",")
    sogou = sgattrs[9]
    utm = "".join([sogou[int(fxck)] for fxck in fxck_chars])

    session.cookies.set("token", token)
    session.cookies.set("_utm", utm)

    response = session.request("GET", api_url,
                        headers = api_headers)
    try:
        if response.status_code==200:
            data=response.json().get('data')
            # print(data)
            return data
    except RequestException:

        print('请求公司信息失败,等待。。。。')
        time.sleep(30)
        return None

def save_to_mongo(company_information):
    if db[MONGO_TABLE].insert(company_information):
        print('Waiting save data.............')
        time.sleep(0.1)
        print('保存数据中。。。。。。')
        print('Successfully Saved to Mongo')
        return True
    return False



def main(p):
    # p_end=50
    # for p in range(1,p_end):   #P为页数
    keywordlist=['上海市浦东','上海市闵行','上海市宝山','上海市嘉定','上海市宝山','上海嘉定区','上海闵行区','上海松江','上海青浦','上海奉贤','上海金山']
    for keyword in keywordlist:
        print(keyword)
        print(p)
        company_information=search_company_information(keyword,p)
        # detail_result=get_detail_result(company_information)
        if company_information is not None: save_to_mongo(company_information)

if __name__ == "__main__":
    p = ([x for x in range(GROUP_START, GROUP_END + 1)])
    pool = Pool(8)
    pool.map(main, p)
    pool.close()
    pool.join()



