## 经济、娱乐、军事
# * 新闻标题
# * 新闻内容
# * 新闻标签
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import jieba  
import time
import random

def getHTMLText(url):
    '''
    获取网页html
    '''
    user_agent = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko"
    ]

    headers = {'User-Agent': random.choice(user_agent)}

    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.content
    except:
        return ""
    
def parase_index(url):
    '''
    解析首页内容
    '''
    html=getHTMLText(url)
    soup = BeautifulSoup(html, "lxml")
    uls=soup.find_all('ul')

    news_type=""#新闻类别
    if "finance" in url:
        news_type="财经"
    elif "ent" in url:
        news_type="娱乐"
    elif "milite" in url:
        news_type="军事"
    elif "tech" in url:
        news_type="科技"
    elif "world" in url:
        news_type="国际"
    print("==========================={}===========================".format(news_type))
    
    for l in uls[1].find_all('li'):
        detail_url=l.a.attrs['href']#详情页链接
        
        try:
            title,content=getContent(detail_url)#获取详情页的标题名称，正文
        except:
            continue
       
        print(title)
        tags=l.find_all(attrs={'class':'tags'})#新闻标签       
        #提取标签文字
        tags=re.findall('target="_blank">(.*?)</a>',str(tags[0]))
        tags=",".join(tags)
        
        writer.writerow((news_type,tags,title,content))
    time.sleep(2)
        
def getContent(url):
    '''
    解析新闻正文html
    '''
    html = getHTMLText(url)
    soup = BeautifulSoup(html, "lxml")
    title=soup.h1.get_text()#获取标题
    artical=soup.find_all(attrs={'class':'one-p'})
    content=""
    for para in artical:
        content+=para.get_text()
    return title,content

def update(old,new):
    '''
    更新数据集：将本次新爬取的数据加入到数据集中（去除掉了重复元素）
    '''
    data=new.append(old)
    data=data.drop_duplicates()
    return data

def word_count(data):
    '''
    词频统计
    '''
    txt=""
    for i in data:
        txt+=str(i)
    #加载停用词表  
    stopwords = [line.strip() for line in open("stop_words.txt",encoding="utf-8").readlines()]  
    words  = jieba.lcut(txt)  
    counts = {}  
    for word in words:  
        #不在停用词表中  
        if word not in stopwords:  
            #不统计字数为一的词  
            if len(word) == 1:  
                continue  
            else:  
                counts[word] = counts.get(word,0) + 1  
    items = list(counts.items())  
    items.sort(key=lambda x:x[1], reverse=True)   
    return pd.DataFrame(items)

#需要爬取的链接：经济、娱乐、军事、科技、国际
url_list=['https://new.qq.com/ch/finance/',
        'https://new.qq.com/ch/ent/',
        'https://new.qq.com/ch/milite/',
         'https://new.qq.com/ch/tech/',
          'https://new.qq.com/ch/world/'
         ]

#定义数据集保存的文件名
file_name="NewsData.csv"
try:
    data_old=pd.read_csv(file_name,encoding='gbk')
except:
    pass
csvFile = open(file_name, 'a', newline='',encoding="gb2312")
writer = csv.writer(csvFile)
writer.writerow(("新闻分类","新闻标签","新闻标题","新闻内容"))

for url in url_list:
    parase_index(url)
    
print("爬取完毕！")
csvFile.close()
print("=====================")
print("开始更新数据集")
data_new=pd.read_csv(file_name,encoding='gbk')
update(data_old,data_new).to_csv(file_name,index=None,encoding='gbk')
print("更新完毕!")
print("=================")
print("开始词频统计")
data=pd.read_csv(file_name,encoding="gbk")
res=word_count(data['新闻内容'])
res.to_csv("frequence.txt",header=None,index=None)
print("统计完毕!")
print(res)
