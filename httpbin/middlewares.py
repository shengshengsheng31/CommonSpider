# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import requests
from lxml import etree
import json
import time
from selenium import webdriver
from scrapy.http.response.html import HtmlResponse


class HttpbinSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class HttpbinDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# 随机请求头
class UserAgentDownloadMiddleware(object):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36'
    ]

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent


# scrapy和requests添加代理的方式不同
# scrapy直接添加代理字符串，requests需要以字典类型加入，且要注明https/http
# 代理池，爬取http://www.89ip.cn/index.html，该代理现在（2019年10月26日）全部为http代理，注意该该网站的代理不一定是匿名代理
# 简单ip代理池
class IPProxyDownloadMiddleware(object):
    def __init__(self):
        self.num = 1  # 翻页用
        self.get_url = "http://www.89ip.cn/index_" + str(self.num) + ".html"
        self.ip_list = []  # IP池，需要检测可用性
        self.ip = "http://0.0.0.0"  # 可用的IP
        self.index = 0  # IP池列表的进度

    # 获取IP池，将重置现有IP池，防止列表过大
    def getIPPool(self):
        response = etree.HTML(requests.get(self.get_url).text)
        ip_port_selectors = response.xpath('//tbody/tr')
        tempList = []
        for ip_port_selector in ip_port_selectors:
            ip = ip_port_selector.xpath('./td/text()')[0].strip()
            port = ip_port_selector.xpath('./td/text()')[1].strip()
            tempList.append(
                "http://" + ip + ":" + port
            )
        self.ip_list = tempList

    # 检测IP池,获取一个可用的IP
    def testIPPool(self):
        # 判断是否初次获取IP池
        if len(self.ip_list):
            self.testIP()
        else:
            self.getIPPool()
            print("初次获取ip池:")
            print(self.ip_list)

    # 检测IP，超出列表元素数后递归
    def testIP(self):
        list = self.ip_list
        strIp = list[self.index]  # 字符串
        ip = strIp.split("//")[1].split(":")[0]
        port = strIp.split("//")[1].split(":")[1]
        ip = "http://" + ip + ":" + port
        tempIp = {"http": ip}
        testUrl = "http://httpbin.org/ip"
        # 判断IP可用性
        try:
            response = requests.get(url=testUrl, proxies=tempIp, timeout=1)
            self.ip = strIp
            print("ip检测通过，正在使用：", strIp, "当前检测ip个数", self.index + 1, "/", len(self.ip_list), "--", self.num)
            print("测试的文本:", response.text.split())
        except:
            self.index += 1
            print("IP不可用:", strIp, "正在更换IP", "当前检测ip个数", self.index + 1, "/", len(self.ip_list), "--", self.num)
            # 当前页所有IP检测完进入下一页
            if self.index + 1 > len(self.ip_list):
                self.num += 1
                self.index = 0
                self.testIPPool()
            self.testIP()

    def process_request(self, request, spider):
        # spider.crawler.engine.close_spider(spider, '错误信息')
        self.testIPPool()
        request.meta["proxy"] = self.ip


# 获取前三页中所有ip加入IP池
# 检测所有的ip并使用
# 当ip池用尽，重新爬取前三页的ip加入IP池
class IPProxyProDownloadMiddleware(object):
    def __init__(self):
        self.num = 1  # 网站的页数
        self.count = 1  # 获取ip池的次数
        self.ip_list = []  # IP池
        self.index = 0  # 300个IP的使用序号
        self.ip = "http://0.0.0.0"

    # 获取前三页的IP
    def getIPPool(self):
        resource_url = 'https://www.xicidaili.com/nn/' + str(self.num)
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        response = requests.get(url=resource_url, headers=header)
        html = etree.HTML(response.text)
        print("获取IP源网页次数：", self.num, "获取IP池次数：", self.count, "状态：", response)
        ipSelectors = html.xpath('//tr[@class]')
        for ipSelector in ipSelectors:
            ht = ipSelector.xpath('./td/text()')[5].strip().lower()
            ip = ipSelector.xpath('./td/text()')[0].strip()
            port = ipSelector.xpath('./td/text()')[1].strip()
            strIp = ht + "://" + ip + ":" + port
            self.ip_list.append(strIp)
        self.num += 1
        time.sleep(2)  # 对ip网站延时两秒避免被屏蔽
        if self.num > 3 * self.count:
            print(self.ip_list)
        if self.num <= 3 * self.count:
            self.getIPPool()

    # 测试IP池中的IP可用性，如果可用就使用该IP进行爬虫
    def testIp(self):
        try:
            strIp = self.ip_list[self.index]  # http://59.57.149.242:9999
            sp = strIp.split(':')
            ht = sp[0]
            ip = {ht: strIp}
            temp_url = "http://httpbin.org/ip"
            # 测试网站的请求头设置
            headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/69.0.3497.100 Safari/537.36'}
            response = requests.get(temp_url, headers=headers, proxies=ip, timeout=3)
            print("%s/%s[%s]，ip:%s可用，测试内容%s" % (self.index + 1, len(self.ip_list), self.count, strIp, response.content))
            temp_ip = strIp.split(':')[1].replace('//', '')  # 59.57.149.242
            # 透明代理直接抛出异常进行下一个测试
            if temp_ip not in response.text:
                print("XXX透明代理", strIp)
                raise Exception()
            self.ip = strIp  # 通过测试的代理
        except Exception as e:
            print("--%s/%s[%s]，无效的IP：%s，" % (self.index + 1, len(self.ip_list), self.count, strIp))
            # 测试下一个IP
            self.index += 1
            if self.index > len(self.ip_list) - 1:  # 300
                self.ip_list = []  # IP池重置
                self.index = 0  # 使用的IP序号重置
                self.count += 1
                self.getIPPool()
            self.testIp()
            # IP耗尽，重新爬取网页

    def process_request(self, request, spider):
        # 初始状态获取ip池
        if self.ip_list == []:
            self.getIPPool()
        self.testIp()
        # 设置代理
        request.meta['proxy'] = self.ip


# 使用selenium接替scrapy的request，获取ajax数据
class SeleniumDownloadMiddleware(object):
    def __init__(self):
        # web引擎
        self.driver = webdriver.Chrome(executable_path=r"D:\Program Files (x86)\chromedriver_win32\chromedriver.exe")

    def process_reuest(self, request, spider):
        self.driver.get(request.url)
        time.sleep(1)
        # 对需要点击的ajax数据进行点击
        try:
            while True:
                ajaxData = self.driver.find_element_by_class_name("[classname]")
                ajaxData.click()
                time.sleep(0.5)
                if not ajaxData:
                    break
        except Exception as e:
            print(e)
        source = self.driver.page_source  # 源网页
        response = HtmlResponse(url=self.driver.current_url, body=source, request=request, encoding='utf-8')
        return response
