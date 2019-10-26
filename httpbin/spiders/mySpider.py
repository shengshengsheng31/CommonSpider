# -*- coding: utf-8 -*-
import scrapy
import json


class MyspiderSpider(scrapy.Spider):
    name = 'mySpider'
    allowed_domains = ['httpbin.org/ip']
    start_urls = ['http://httpbin.org/ip']
    count = 1  # 爬虫次数

    def parse(self, response):
        print("爬虫%s次" % (self.count), "爬虫内容：", response.xpath("//title/text()").get())
        print(response.text)
        self.count += 1
        yield scrapy.Request(self.start_urls[0], dont_filter=True)
