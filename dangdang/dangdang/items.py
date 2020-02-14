# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DangdangItem(scrapy.Item):
    # define the fields for your item here like:
    #定义需要爬取的变量名
    name=scrapy.Field()#定义保存书名的变量
    author=scrapy.Field()#作者
    price = scrapy.Field()#价格
    comments=scrapy.Field()#销量
    category=scrapy.Field()#图书分类



