#爬取的整体过程
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import os


os.chdir(os.path.abspath(os.path.dirname(__file__)))
# 创建webdriver对象
options = webdriver.ChromeOptions()
# 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
options.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Chrome(options=options)
# 等待变量
wait = WebDriverWait(driver, 5)
RATE=[]
PRICE=[]
DATE=[]
URL=[]
STORE=[]
url='https://login.tmall.com/'
driver.get(url)
def input_key(locator,key):
    btn=driver.find_element_by_xpath(locator)
    btn.clear()
    btn.send_keys(key)
    return btn

# 一直等待某元素可见，默认超时10秒
def is_visible(locator, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except :
        return False

def click_btn(locator):
    btn=driver.find_element_by_xpath(locator)
    btn.click()
    
def is_exist(locator):
    is_exist=driver.find_element_by_xpath(locator)
#     print(is_exist.get_attribute('textContent'))
#     if '没找到' in is_exist.get_attribute('textContent'):
#         return {'error':is_exist.get_attribute('textContent'),'msg':False}
    
    try:
        click_btn('//*[@id="content"]/div[2]/div[1]/div[1]/a')
        return {'msg':True}
    except:
        try:
            if is_exist.get_attribute('textContent'):
                return {'error':is_exist.get_attribute('textContent'),'msg':False}
        except:
            return {'error':'未找到页面元素','msg':False}
        
        
def parse(store,flag):
    '''解析页面，若无内容，则只获取url，其他内容返回无'''
    driver.switch_to.window(driver.window_handles[-1])
    url=driver.current_url
    #访问验证判断:
    try:
        click_btn('//*[@id="ks-overlay-close-ks-component395"]')
    except:
        pass
    print("开始解析:",flag)
    if flag==1:
        rate,price,date='无'*3
        RATE.append(rate)
        PRICE.append(price)
        DATE.append(date)
        URL.append(url)
        STORE.append(store)
        save()
        return rate,price,date,url
    if is_visible('//*[@id="ks-overlay-close-ks-component395"]',timeout=3):
        click_btn('//*[@id="ks-overlay-close-ks-component395"]')
    elif is_visible('//*[@id="shop-rate-box"]/div[1]/div[1]/div/div[2]/div[2]/div/div[1]/div[1]/table/tbody/tr[1]/td[2]'):
        print("解析内容:",end="")
#     try:
    rate=driver.find_element_by_xpath('//*[@id="shop-rate-box"]/div[1]/div[1]/div/div[2]/div[2]/div/div[1]/div[1]/table/tbody/tr[1]/td[2]').get_attribute('textContent')
    price=driver.find_element_by_xpath('//*[@id="shop-rate-box"]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/span').get_attribute('textContent')  
    date=driver.find_element_by_xpath('//*[@id="relalist"]/div/div/div[2]/div[1]/div[3]/div/div[2]/span[1]').get_attribute('textContent')
#     except:
#         rate,price,date='无'*3
    RATE.append(rate)
    PRICE.append(price)
    DATE.append(date)
    URL.append(url)
    STORE.append(store)
    save()
    return rate,price,date,url

def close_handle():
    #获取标签页的数量,关闭到只剩首页
    length = len(driver.window_handles)
    for i in range(length-1):
        handles = driver.window_handles
        driver.switch_to.window(handles[-1])
        driver.close()
        time.sleep(1)
    driver.switch_to.window(driver.window_handles[0])

def save(out_file_name):
    df=pd.DataFrame({
    '店铺':STORE,
    '退款率':RATE,
    '最后评论日期':DATE,
    '保证金余额':PRICE,
    '详情链接':URL
    })
    df.to_csv(out_file_name+".csv",encoding='gbk',index=None)
    
def main(lists):
    for store in lists:
        print("=============={}======================".format(store))
        driver.switch_to.window(driver.window_handles[0])
        if is_visible('//*[@id="mq"]'):
            #查询
            input_key('//*[@id="mq"]',store)
            #点击
            click_btn('//*[@id="mallSearch"]/form/fieldset/div/button')
            time.sleep(1)
            #检查店铺搜索返回值
            try:
                judge=is_exist('//*[@id="content"]/div/div[3]')
            except:
                parse(store,1)
                continue
            #存在该店铺则点击进入详情页采集信息
            if judge['msg']:
                #点开店铺信息的下拉框
                driver.switch_to.window(driver.window_handles[-1])
                #检查页面是否是404:
                if driver.title=='404 Not Found':
                    #如果是404,将该店铺加到搜索列表的末尾，待前面店铺搜索完后再继续
                    lists.append(store)
                    print("当前页面404，该店铺将加到搜索列表的末尾，待前面店铺搜索完后重试")
                    close_handle()
                    time.sleep(10)
                    continue
                
                #进入评分页
                try:
                    if is_visible('//*[@id="shop-info"]/div[2]/a'):
                        click_btn('//*[@id="shop-info"]/div[2]/a')
                except:
                    print(parse(store,1))
                    close_handle()
                    continue
                time.sleep(2)
                try:
                    click_btn('/html/body/div[1]/div[2]/div/div[1]/div[2]/div[3]/div/div/div/div[1]/ul/li[1]/a')
                    print(parse(store,0))
                except:
                    print(parse(store,1))
                close_handle()
            else:
                print(judge['error'])
      
        time.sleep(random.randint(1,8))
    print("全部爬取完毕")
    close_handle()
    driver.close()
def entrace(input_file,out_file='result'):

    # ===========================配置输入输出内容===============================
    # 设置读取的文件名称,仅支持.xlsx的文件
    INPUT_FILE = "stores.xlsx"
    # 设置输出的文件名称
    OUT_FILE_NAME = out_file
    # ===============================================================

    stores = pd.read_excel(INPUT_FILE)
    store_list = stores['stores'].tolist()
    main(store_list)



if __name__=='__main__':
    entrace()