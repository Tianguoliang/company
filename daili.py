import time
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
import pymongo
import re
import json
from urllib import parse
import random
from requests import RequestException
def get_detail_html(company_url):
    response=requests.get(company_url)
    try:
        if response.status_code==200:
            return response.text
        return None
    except RequestException:
        print('请求详情页（get_detail_html)失败')
        return None
def get(url):
    response=requests.get(url)
    try:
        if response.status_code==200:
            return response.json()
        return None
    except RequestException:
        print('请求详情页（get_detail_html)失败')
        return None
def main():
    url='http://www.tianyancha.com/expanse/annu.json?id=539721727&ps=5&pn=1'
    a=get(url)
    print(a)
    b=(a.get('data'))
    print(b)
    for data in b:
        year=data.json().get('reportYear')
        print(year)
        print(id())
        data={'id':id,
              'year':year}
        company_url='http://www.tianyancha.com/annualreport/newReport.json?'+urlencode(data)
        print(company_url)
    print(get_detail_html(company_url))

if __name__=='__main__':
   main()
