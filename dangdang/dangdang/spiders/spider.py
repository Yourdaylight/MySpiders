import scrapy
import re
from dangdang.items import DangdangItem
class SpiderSpider(scrapy.Spider):
    name = 'spider'
    allowed_domains = ['store.dangdang.com/282']
    start_urls = ['http://store.dangdang.com/282']


    def parse(self, response):
        #urls=response.xpath('//*[@id="sidefloat"]/div[2]/div/div/map/area').extract()
        urls=response.xpath('//*[@id="sidefloat"]/div[2]/div/div/map/area/@href').extract()#获取分类列表的链接
        categories=response.xpath('//*[@id="sidefloat"]/div[2]/div/div/map/area').extract()#获取分类名称

        for url,category in zip(urls,categories):#爬取分类链接的详情页
            text = re.findall('title="(.*?)" alt',category)#正则匹配，提取分类关键字信息
            for i in range(1,20):#爬取分页信息
                url_now=url+'&page_index="+str(i)
                yield scrapy.Request(url=url_now,callback=lambda response, category=text : self.parse_subpage(response,category), dont_filter=True)

    def parse_subpage(self,response,category):

        length= len(response.xpath('//*[@id="component_0__0__8395"]/li/a/img').extract())#获取每一面的图书数量
        for i in range(0,length+1):
            item = DangdangItem()

            item['name']=response.xpath('//*[@id = "component_0__0__8395"] /li[{}]/p[2]/a/text()'.format(i)).extract()
            item['author']=response.xpath('//*[@id="component_0__0__8395"]/li[{}]/p[5]/text()'.format(i)).extract()
            item['price']=response.xpath('//*[@id="component_0__0__8395"]/li[{}]/p[1]/span[1]/text()'.format(i)).extract()
            item['comments']=response.xpath('//*[@id="component_0__0__8395"]/li[{}]/p[4]/a/text()'.format(i)).extract()
            item['category']=category

            yield item
