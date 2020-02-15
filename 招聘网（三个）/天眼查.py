import requests
import re
import random
import csv
import time
import pandas as pd
headers_list=[
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

path=input("请输入需要查询的名单文件所在路径（请确保文件名以及文件格式输入完整）:")
key=input("请为输出文件命名（请确保不与其他文件名重复，否则结果将会被覆盖）：")
new_file="天眼查_"+key
csvFile = open(new_file+".csv", 'w', newline='',encoding='utf-8')
writer = csv.writer(csvFile)
writer.writerow(("详情页链接","职位名称","招聘状态","发布日期","招聘企业","所在城市","工作经验","职位描述"))

def get_list(path):
    import pandas as pd
    company=pd.read_excel(path)
    company_list=[]
    for i in company.values:
        company_list.extend(i)
    return company_list

def parse_page(url,page):
    head=random.choice(headers_list)
    headers={'User-Agent':head}
    url+="/p"+str(page)
    print(url)
    r=requests.get(url,headers)

    reg_info=re.compile(r'<div class="risk-title">(.*?)</div>',re.S)
    reg_salary=re.compile(r'<span class="ori-salary">(.*?)</span>',re.S)
    reg_company=re.compile(r'<div class="item-right">招聘企业：<span>(.*?)</span></div>',re.S)

    info=re.findall(reg_info,r.text)
    links=[]#详情页链接
    title=[]#职位名称
    status=[]#招聘状态
    for i in info:
        li=re.findall(r'<a class="link-click" target="_blank" href="(.*?)">',i,re.S)
        ti=re.findall(r'<a class="link-click" target="_blank" href=".*?">(.*?)</a>',i,re.S)
        st=re.findall(r'<span class="recruit-status">(.*?)</span>',i,re.S)
        links.extend(li)
        status.extend(st)
        title.extend(ti)
    salary=re.findall(reg_salary,r.text)
    date=re.findall(r'<div class="item-left item-fix">发布日期：<span>(.*?)</span></div>',r.text,re.S)
    company=re.findall(reg_company,r.text)
    city=re.findall(r'<div class="item-left item-fix">所在城市：<span>(.*?)</span></div>',r.text,re.S)
    experience=re.findall(r'<div class="item-right">工作经验：<span>(.*?)</span></div>',r.text,re.S)

   
    details=[]    #获取详情页的职位描述
    for link in links:
        r2=requests.get(link,headers)
        detail=re.findall(r'<div class="content">.*?<br>(.*?)</div>',r2.text,re.S)
        details.extend(detail)
    for i in range(len(title)):
        try:
            writer.writerow((links[i],title[i],status[i],date[i],company[i],city[i],experience[i],details[i]))
        except:
            writer.writerow((url,title[i],status[i],date[i],company[i],city[i],experience[i],"静态加载页面，无法获取"))
            
def decode_file():
    d=pd.read_csv(new_file+".csv")
    d.to_excel(new_file+".xlsx",index=False)

for company in get_list(path): 
    url='https://job.tianyancha.com/search/'+company
    head=random.choice(headers_list)
    headers={'User-Agent':head}
    request=requests.get(url,headers)

    try:
        results=int(re.findall(r'<span class="num">(.*?)&nbsp;</span>',request.text,re.S)[0])
    except:
        results=1
    pages=results//10+1
    for page in range(1,pages+1):
        print("===============正在爬取{}第{}/{}页信息===================".format(company,page,pages))
        parse_page(url,page)
    decode_file()
    stop=random.randint(1,5)
    time.sleep(stop)
csvFile.close()
print("所有内容爬取完毕")