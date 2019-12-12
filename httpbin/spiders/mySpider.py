# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy_redis.spiders import RedisSpider

# 分布式改造1，使用redis的爬虫
class MyspiderSpider(RedisSpider):
    name = 'mySpider'
    allowed_domains = ['httpbin.org/ip']
    # 分布式改造2，取消start_urls使用redis_key
    # start_urls = ['http://httpbin.org/ip']
    redis_key = "fangSpider:start_urls"
    count = 1  # 爬虫次数

    def parse(self, response):
        print("爬虫%s次" % (self.count), "爬虫内容：", response.xpath("//title/text()").get())
        print(response.text)
        self.count += 1
        yield scrapy.Request(self.start_urls[0], dont_filter=True)
