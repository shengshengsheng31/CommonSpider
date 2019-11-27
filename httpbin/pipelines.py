# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi
from pymysql import cursors


class HttpbinPipeline(object):
    def process_item(self, item, spider):
        return item


# 异步保存到数据库，多次请求后保存，效率更高
class AsynPipeline(object):
    def __init__(self):
        self._sql = None
        dbparams = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'shength',
            'password': 'password',
            'database': 'myspider',
            'charset': 'utf8',
            'cursor': cursors.DictCursor  # 指定游标,返回字典(dict)表示的记录,默认返回以列表(list)表示
        }
        # 连接池连接到数据库
        self.dbPool = adbapi.ConnectionPool('pymsql', **dbparams)

    # 属性
    @property
    def sql(self):
        if not self._sql:
            self._sql = "INSERT INTO [table] ([key],[key],[key]) VALUES (null,[value],[value]) "  # INSERT INTO jianshu_article (id,title,article_id,origin_url,author,content) VALUES (null,%s,%s,%s,%s,%s)
        return self._sql

    # 主程序
    def process_item(self, item, spider):
        defer = self.dbPool.runInteraction(self.insert_item, item)  # 执行sql语句
        defer.addErrback(self.handle_error, item, spider)

    # 准备sql语句
    def insert_item(self, cursor, item):
        cursor.execute(self.sql, (item['key'], item['key'], item[
            'key']))  # (item['title'], item['article_id'], item['origin_url'], item['author'], item['content'])

    # 错误处理
    def handle_error(self, error):
        print("=" * 10 + str(error) + "=" * 10)


# 同步保存到数据库
class SynPipeline(object):
    def __init__(self):
        self._sql = None
        dbparams = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'shength',
            'password': 'password',
            'database': 'myspider',
            'charset': 'utf8'
        }
        # 创建连接
        self.conn = pymysql.connect(**dbparams)
        # 创建游标
        self.cursor = self.conn.cursor()

    # 属性
    @property
    def sql(self):
        if not self._sql:
            self._sql = "INSERT INTO [table] ([key],[key],[key]) VALUES (null,[value],[value]) "  # INSERT INTO jianshu_article (id,title,article_id,origin_url,author,content) VALUES (null,%s,%s,%s,%s,%s)
        return self._sql

    # 主程序
    def process_item(self, item, spider):
        self.cursor.execute(self.sql, (item['key'], item['key'], item[
            'key']))  # (item['title'], item['article_id'], item['origin_url'], item['author'], item['content'])
        self.conn.commit()
