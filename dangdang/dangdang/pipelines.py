# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class DangdangPipeline(object):
    def __init__(self):
        # 连接数据库
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)#连接MongoDB
        self.test = self.client['dangdang']#创建数据库dangdang
        self.post = self.test['book']

    def process_item(self, item, spider):

        data = dict(item)#插入数据之前需要把字段转换成字典形式
        flag=1#判断是否为空，默认为1，表示不为空
        for key,value in data.items():
            if (value == []):
                flag = 0
                break
            if(type(value)==list):
                data[key]=value[0]

        if(flag==1):
            self.post.insert(data)#插入数据
        # return item
