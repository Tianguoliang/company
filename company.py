#coding:utf-8
#Actor:Tyson
import time
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
import pymongo
import re
import json
from urllib import parse
from pip._vendor.requests import RequestException
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
    try:
        js_code = "".join([ chr(int(code)) for code in tongji_page.json()["data"]["v"].split(",") ])
        token = re.findall(r"token=(\w+);", js_code)[0]

        fxck_chars = re.findall(r"\'([\d\,]+)\'", js_code)[0].split(",")
        sogou = sgattrs[9]
        utm = "".join([sogou[int(fxck)] for fxck in fxck_chars])
    except:
        print('请求utm和token失败')
        return None

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

#给到id之后，从网页返回url_datas（包含假的id和year）
def get_annureport_count(id):
    url='http://www.tianyancha.com/expanse/annu.json?id='+str(id)+'&ps=5&pn=1'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            rs=response.json().get('data')
            if rs is not None and '无数据':
                url_datas=[]
                for r in rs:
                    url_data={'id':id,'year':r.get('reportYear')}
                    url_datas.append(url_data)
                return url_datas
        return None
    except RequestException:
        print('请求公司多少次年报失败')
        return None

#根据url_data获取每一年的年报信息，并保存到nianbaos。涉及知识点：字典的叠加！
def get_nianbao(annureport_count):
    if annureport_count is not None:
        nianbaos={}.copy()
        a=''
        i=0
        try:
            for annureport_data in annureport_count:
                i=i+1
                url='http://www.tianyancha.com/annualreport/newReport.json?'+urlencode(annureport_data)
                try:
                    response=requests.get(url,timeout=1)
                    if response.status_code==200:
                        a={str(i):response.json()}
                        nianbaos.update(a)
                    return nianbaos
                except:
                    print('异常')
        except RequestException:
            print('请求公司年报失败')
            return None

#获取公司人员信息
def get_staff_informaton(id):
    url='http://www.tianyancha.com/expanse/staff.json?id='+str(id)+'&ps=20&pn=1'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            staff_information=response.json().get('data')
            if staff_information is not None and '无数据':
                return staff_information
        return None
    except RequestException:
        print('请求公司人员信息失败')
        return None

#获取公司股东信息
def get_holder_informaton(id):
    url='http://www.tianyancha.com/expanse/holder.json?id='+str(id)+'&ps=20&pn=1'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            holder_information=response.json().get('data')
            if holder_information is not None and '无数据':
                return holder_information
        return None
    except RequestException:
        print('请求公司对外投资信息失败')
        return None

#获取公司对外投资信息
def get_inverst_informaton(id):
    url='http://www.tianyancha.com/expanse/inverst.json?id='+str(id)+'&ps=20&pn=1'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            inverst_information=response.json().get('data')
            if inverst_information is not None and '无数据':
                return inverst_information
        return None
    except RequestException:
        print('请求公司股东信息失败')
        return None

#获取公司变更信息
def get_changeinfo_informaton(id):
    url='http://www.tianyancha.com/expanse/changeinfo.json?id='+str(id)+'&ps=5&pn=1'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            changeinfo_informaton=response.json().get('data')
            if changeinfo_informaton is not None and '无数据':
                return changeinfo_informaton
        return None
    except RequestException:
        print('请求公司股东信息失败')
        return None

#获取公司核心团队
def get_findTeamMember(company_name):
    url='http://www.tianyancha.com/expanse/findTeamMember.json?name='+company_name+'&ps=5&pn=1'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            findTeamMember=response.json().get('data')
            if findTeamMember is not None and '无数据':
                return findTeamMember
        return None
    except RequestException:
        print('获取公司核心团队失败')
        return None
#获取公司企业业务
def get_findProduct(company_name):
    url='http://www.tianyancha.com/expanse/findProduct.json?name='+company_name+'&ps=15&pn=1'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            findProduct=response.json().get('data')
            if findProduct is not None and '无数据':
                return findProduct
        return None
    except RequestException:
        print('获取公司企业业务失败')
        return None

#获取公司投资事件
def get_findTzanli(company_name):
    url='http://www.tianyancha.com/expanse/findTzanli.json?name='+company_name+'&ps=10&pn=1'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            findTzanli=response.json().get('data')
            if findTzanli is not None and '无数据':
                return findTzanli
        return None
    except RequestException:
        print('获取公司投资事件失败')
        return None

#获取竞品信息
def get_findJingpin(company_name):
    url='http://www.tianyancha.com/expanse/findJingpin.json?name='+company_name+'&ps=10&pn=1'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            findJingpin=response.json().get('data')
            if findJingpin is not None and '无数据':
                return findJingpin
        return None
    except RequestException:
        print('获取竞品信息')
        return None

#获取法律诉讼信息
def get_getlawsuit(company_name):
    url='http://www.tianyancha.com/v2/getlawsuit/'+company_name+'.json?page=1&ps=10'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            getlawsuit=response.json().get('data')
            if getlawsuit is not None and '无数据':
                return getlawsuit
        return None
    except RequestException:
        print('获取法律诉讼信息失败')
        return None
#获取法院公告
def get_court(company_name):
    url='http://www.tianyancha.com/v2/getlawsuit/'+company_name+'.json?'
    response=requests.get(url)
    try:
        if response.status_code==200 and  'data' in response.json():
            court=response.json().get('data')
            if court is not None and '无数据':
                return court
        return None
    except RequestException:
        print('获取法院公告失败')
        return None

def save_to_mongo(all_information):
    if db[MONGO_TABLE].insert(all_information):
        print('Waiting save data.............')
        time.sleep(0.1)
        print('保存信息数据中。。。。。。')
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
        company_informations=search_company_information(keyword,p)
        for company_information in company_informations:
            #获取重要的公司名称和id
            id=(company_information).get('id')
            company_name=company_information.get('name').replace('<em>','   ').replace('</em>','')


            #由id获取公司信息
            annureport_count=get_annureport_count(id)
            staff_informaton=get_staff_informaton(id)
            holder_informaton=get_holder_informaton(id)
            inverst_information=get_inverst_informaton(id)
            changeinfo_informaton=get_changeinfo_informaton(id)
            nianbaos=get_nianbao(annureport_count)

            #由name获取公司发展信息
            findTeamMember=get_findTeamMember(company_name)
            findProduct=get_findProduct(company_name)
            findTzanli=get_findTzanli(company_name)
            findJingpin=get_findJingpin(company_name)

            #由name获取公司司法风险信息
            getlawsuit=get_getlawsuit(company_name)
            court=get_court(company_name)

            if company_information is not None:
                all_information={'公司基本信息':company_information,
                                 '公司年报':nianbaos,
                                 '公司主要人员':staff_informaton,
                                 '公司股东信息':holder_informaton,
                                 '公司对外投资信息':inverst_information,
                                 '公司变更记录':changeinfo_informaton,
                                 '公司核心团队':findTeamMember,
                                 '公司企业业务':findProduct,
                                 '公司投资事件':findTzanli,
                                 '竞品信息':findJingpin,
                                 '法律诉讼信息':getlawsuit,
                                 '法院公告':court}
                save_to_mongo(all_information)

if __name__ == "__main__":
    p = ([x for x in range(GROUP_START, GROUP_END + 1)])
    pool = Pool(8)
    pool.map(main, p)
    pool.close()
    pool.join()


