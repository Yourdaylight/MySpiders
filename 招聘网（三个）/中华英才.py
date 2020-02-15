import re
import time
import requests
import csv

#中华英才网，一次最多查询5个，省份编号11-44
#url='http://www.chinahr.com/sou/?orderField=relate&keyword=java&city=34;35;36;39;45&page=1'
#base_url='http://www.chinahr.com/sou/?city=3B34%3B35%3B36%3B39%3B45&keyword=java'

#搜索关键字，这里只爬取了数据挖掘的数据，读者可以更换关键字爬取其他行业数据
path=input("请输入需要查询的名单文件所在路径（请确保文件名以及文件格式输入完整）:")
key=input("请为输出文件命名（请确保不与其他文件名重复，否则结果将会被覆盖）：")

city_list=[11,12,13,14,15]
base_url='http://www.chinahr.com/sou/?orderField=relate&keyword={}&city={};{};{};{};{}&page='
initial_url='http://www.chinahr.com/sou/?city={}%3B{}%3B{}%3B{}%3B{}&keyword={}'
header={'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'}


new_file="中华英才_"+key+".csv"
print(new_file)
csvFile = open(new_file, 'w', newline='')
writer = csv.writer(csvFile)
writer.writerow(("岗位名称","发布时间","公司名称","薪水","相关要求","公司属性"))

def get_page(company,city_list):
    url= initial_url.format(city_list[0],city_list[1],city_list[2],city_list[3],city_list[4],company)
    r=requests.get(url+str(1),headers=header)
    initial_html=r.content.decode('utf-8')
    reg=re.compile(r'<div class="jobList"(.*?)</div>',re.S)#匹配搜索到的工作列表
    reg2=re.compile(r'<span><i>1</i>&nbsp;/&nbsp;(.*?)</span>',re.S)#匹配页数
    pages=int(re.findall(reg2,initial_html)[0])
    return pages

def get_list(path):
    import pandas as pd
    company=pd.read_excel(path)
    company_list=[]
    for i in company.values:
        company_list.extend(i)
    return company_list

def parsePage(company,page,city_list):
    '''
    url:翻页之后的连接
    '''

    url= base_url.format(company,city_list[0],city_list[1],city_list[2],city_list[3],city_list[4])+page
    reg=re.compile(r'<div class="jobList"(.*?)</div>',re.S)#匹配搜索到的工作列表
    reg2=re.compile(r'<span><i>1</i>&nbsp;/&nbsp;(.*?)</span>',re.S)#匹配页数
    r=requests.get(url,headers=header)
    initial_html=r.content.decode('utf-8')
    job_list=re.findall(reg,initial_html)
    for job in job_list:
        job_name=re.findall(r'" target="_blank">(.*?)</a>',job,re.S)[0]
        job_name=job_name.replace("<span style='color:#F00'><strong>","")
        job_name=job_name.replace("</strong></span>","")
  
        update_time=re.findall(r'<span class="e2">(.*?)</span>',job)[0]
        company_name=re.findall(r'" target="_blank">(.*?)</a>',job,re.S)[1]
        salary=re.findall(r'<span class="e2">(.*?)</span>',job,re.S)[1]
        detail=re.findall(r'<span class="e1" title = "">(.*?)</span>',job,re.S)[0].replace("\t","").strip()
        feature=re.findall(r'<em>(.*?)</em>',job,re.S)
        
        try:
            writer.writerow((job_name,update_time,company_name,salary,detail,feature))
        except:
            print("数据缺失")
flag=0        
for company in get_list(path):
    for cities in range(7):
        try:
            page=get_page(company,city_list)
            print("正在爬取{}公司信息(共{}页),对应省份编号{},{},{},{},{}".format(company,page,city_list[0],city_list[1],city_list[2],city_list[3],city_list[4]))
            for i in range(0,page):
                parsePage(company,str(i+1),city_list)
            city_list=[i+5 for i in city_list]
        except:
            flag+=1
            city_list=[i+5 for i in city_list]
            continue
    if flag==7:
        print("{}爬取完毕，未查询到相关信息".format(company))
    else:
        print("{}爬取完毕！".format(company))
    city_list=[11,12,13,14,15]
    flag=0
    time.sleep(3)
csvFile.close()
print('爬取完毕')