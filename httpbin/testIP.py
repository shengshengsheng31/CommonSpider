# import requests
# from lxml import etree
# import random
#
# url = "http://www.89ip.cn"
# response = requests.get(url)
# iplist = []
# # 解析成网页
# response = etree.HTML(response.text)
# ip_port_selectors = response.xpath('//tbody/tr')
# for ip_port_selector in ip_port_selectors:
#     ip = ip_port_selector.xpath('./td/text()')[0].strip()
#     port = ip_port_selector.xpath('./td/text()')[1].strip()
#     iplist.append({
#         ip: port
#     })
#     # ip = "http://" + ip + ":" + port
#     # iplist.append(ip)
#
# proxies = random.choice(iplist)
# # proxies = proxies.split(':',1)
# # proxies = {proxies[0]:proxies[1]}
# print(proxies)
#
# temp_url = "http://httpbin.org/ip"
#
# response= requests.get(temp_url, proxies=proxies)
# status = response.status_code
# ip = response.text
# print(status,ip)
#
#
from typing import Dict

dic = {'e': 'd', 't': 'e'}
print(dic[0])
