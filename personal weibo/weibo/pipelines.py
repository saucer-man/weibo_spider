# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import re, time
import logging
import json
import codecs
from weibo.items import UserItem, WeiboItem
import pymongo
import os


class MongoPipeline(object):
    def __init__(self, mongo_uri,mongo_port, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_port = mongo_port

    @classmethod
    def from_crawler(cls, crawler):
        return cls( # 获取setting数据
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        # 连接MongoDB
        self.client = pymongo.MongoClient(self.mongo_uri, self.mongo_port)
        # 获取weibo数据库的句柄
        self.db = self.client[self.mongo_db]
        # 创造两个collection，两个表
        self.db[UserItem.collection].create_index([('id', pymongo.ASCENDING)])
        self.db[WeiboItem.collection].create_index([('id', pymongo.ASCENDING)])

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # 插入数据到相应的表中
        dict_item = dict(item)
        self.db[item.collection].insert(dict_item)
        return item


class SavefilePipeline(object):
    # 存储数据，将 Item 实例作为 json 数据写入到文件中
    # 初始化时指定要操作的文件
    #def __init__(self):
    #self.has_dir_path = False
    # self.dir_path = ''
    #     self.file_user = codecs.open('user.json', 'w', encoding='utf-8')
    #     self.file_weibo = codecs.open('weibo.json', 'w', encoding='utf-8')

    # 存储数据，将 Item 实例作为 json 数据写入到文件中
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'

        if isinstance(item, UserItem):
            
            self.dir_path = f'result/{item["id"]}'
            file_user = codecs.open(f'{self.dir_path}/user.json', 'a', encoding='utf-8')
            file_user.write(lines)
            file_user.close()

        elif isinstance(item, WeiboItem):
            self.dir_path = f'result/{item["user"]}'
            file_weibo = codecs.open(f'{self.dir_path}/weibo.json', 'a', encoding='utf-8')
            file_weibo.write(lines)
            file_weibo.close()

        return item

    # # 处理结束后关闭 文件 IO 流
    # def close_spider(self, spider):
    #     self.file_user.close()
    #     self.file_weibo.close()


class WeiboTimePipeline(object):
    def parse_time(self, date):
        if re.match('刚刚', date):
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        if re.match('\d+分钟前', date):
            minute = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前', date):
            # print(date) 20小时前
            hour = date.strip("小时前").strip()
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*', date):
            # print(date) 昨天 10:04
            date = re.match('昨天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime(int(time.time()-24 * 60 * 60))) + ' ' + date
        if re.match('\d{2}-\d{2}', date):
            date = time.strftime('%Y-', time.localtime()) + date + ' 00:00'

        return date

    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item.get('created_at'))
            if item.get('pictures'):
                item['pictures'] = [pic.get('url') for pic in item.get('pictures')]
        now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
        item['crawled_at'] = now
        return item


