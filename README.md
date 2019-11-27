# CommonSpider
通用型爬虫
    1、随机性UserAgent
    2、采用西刺免费代理(过滤掉透明代理和不可用代理，一次性爬取3个页面的代理，全部测试后重新爬取，保证代理IP的时效性)
    3、pipeline同步和异步保存到mysql
    redis分布（未完成）
