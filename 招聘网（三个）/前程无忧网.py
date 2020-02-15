
# -*- coding:utf-8 -*-
# By qixinlei
import urllib
import re,codecs
import time,random
import requests
from lxml import html
from urllib import parse
import csv
import time
#搜索关键字，这里只爬取了数据挖掘的数据，读者可以更换关键字爬取其他行业数据
path=input("请输入需要查询的名单文件所在路径（请确保文件名以及文件格式输入完整）:")
key=input("请为输出文件命名（请确保不与其他文件名重复，否则结果将会被覆盖）：")
#编码调整
# key=parse.quote(parse.quote(key))
 
#伪装爬取头部，以防止被网站禁止
headers={'Host':'search.51job.com',
         'Upgrade-Insecure-Requests':'1',
         'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)\
         Chrome/63.0.3239.132 Safari/537.36'}
new_file="前程无忧:"+key+".csv"
print(new_file)
#打开Data_mining.csv文件，进行写入操作
csvFile = open("前程无忧_"+key+".csv", 'w', newline='')
writer = csv.writer(csvFile)
writer.writerow(('link','job','company','salary','date','detail','companytype','direction','describe'))


def get_list(path):
    import pandas as pd
    company=pd.read_excel(path)
    company_list=[]
    for i in company.values:
        company_list.extend(i)
    return company_list

#获取职位详细页面
def get_links(page,company):
    url ='http://search.51job.com/list/000000,000000,0000,00,9,99,'+company+',2,'+ str(page)+'.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare='
    r= requests.get(url,headers,timeout=10)
    s=requests.session()
    s.keep_alive = False
    r.encoding = 'gbk'
    reg = re.compile(r'class="t1 ">.*? <a target="_blank" title=".*?" href="(.*?)".*? <span class="t2">', re.S)
    links = re.findall(reg, r.text)
    reg2 = re.compile(r'<span class="td">(.*?)</span>', re.S)
    pages=re.findall(reg2, r.text)
    page=re.findall('\d+',pages[0])
    
    reg3 = re.compile(r'<span class="t5">(.*?)</span>', re.S)
    Dates=re.findall(reg3, r.text)
    
    
    return [links,page[0],Dates]
#多页处理，下载到文件
def get_content(link,date):
    r1=requests.get(link,headers,timeout=10)
    s=requests.session()
    s.keep_alive = False
    r1.encoding = 'gb2312'
    t1=html.fromstring(r1.text)
    #print(link)
    job=t1.xpath('//div[@class="tHeader tHjob"]//h1/text()')[0].strip()
#     print(job)
    company = t1.xpath('//p[@class="cname"]/a/text()')[0].strip()
    #print(company)
    sa = t1.xpath('//div[@class="cn"]//strong/text()')
    salary=[]
    for i in sa:
        salary.append(i.strip())
    if salary==[]:
        salary=["暂无数据"]

    Detail=t1.xpath('//p[@class="msg ltype"]/text()')
#     reg=re.compile(r'[\u4E00-\u9FA5\s]+',re.S)
    detail=[]
    for i in Detail:
        i=i.strip()
        i+=','
        detail.append(i)
    
    companytype=t1.xpath('//p[@class="at"]/text()')[0].strip()
    #print(companytype)
    companyscale = t1.xpath('//p[@class="at"]/text()')[1].strip()
    #print(companyscale)
    direction = t1.xpath('//div[@class="com_tag"]/p/a/text()')[0].strip()
    #print(direction)
    describe = t1.xpath('//div[@class="bmsg job_msg inbox"]//text()')
    #print(describe)
    try:
        writer.writerow((link,job,company,salary,date,detail,companytype,direction,describe))
    except:
        try:
            writer.writerow((link,job,company,salary,date,"暂无数据","暂无数据","暂无数据","暂无数据"))
        except:
            writer.writerow((link,"该岗位已停止招聘","该岗位已停止招聘","该岗位已停止招聘",date,"暂无数据","暂无数据","暂无数据","暂无数据"))
    return True
 
#主调动函数
Time=0
for company in get_list(path):
    page=get_links(1,company)[1]

    for i in range(1,int(page)+1): 
        print('正在爬取{}:第{}/{}页信息'.format(company,i,int(page)))
        links=get_links(i,company)

        for j in range(len(links[0])):
            try:
                get_content(links[0][j],links[2][j])
            except:
                print("数据有缺失值")
                continue
    Time+=1
    if Time%10==0:
        print("======================已爬取{}个公司，休眠30秒=====================".format(Time))
        time.sleep(30)
            
#关闭写入文件
print("所有内容爬取完毕")
csvFile.close()