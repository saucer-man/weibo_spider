# -*- coding:utf-8 -*-
__author__ = '10029'
__time__ = '2019/6/4 18:03'
'''
热点话题的发布者，正文信息，点赞数，评论数，创建时间等信息
'''
import requests
import datetime
import re
import pymongo
import time

def time_fix(time_string):
    now_time = datetime.datetime.now()
    if '分钟前' in time_string:
        minutes = re.search(r'^(\d+)分钟', time_string).group(1)
        created_at = now_time - datetime.timedelta(minutes=int(minutes))
        return created_at.strftime('%Y-%m-%d %H:%M:%S')

    if '小时前' in time_string:
        minutes = re.search(r'^(\d+)小时', time_string).group(1)
        created_at = now_time - datetime.timedelta(hours=int(minutes))
        return created_at.strftime('%Y-%m-%d %H:%M:%S')

    if '今天' in time_string:
        return time_string.replace('今天', now_time.strftime('%Y-%m-%d'))

    if '月' in time_string:
        time_string = time_string.replace('月', '-').replace('日', '')
        time_string = str(now_time.year) + '-' + time_string
        return time_string

    return time_string



class WeiBoSpider(object):

    def __init__(self,socketio):
        LOCAL_MONGO_HOST = '192.168.2.170'
        LOCAL_MONGO_PORT = 27017
        DB_NAME = 'weiboredian'
        client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
        db = client[DB_NAME]
        self.collection = db["weibo"]
        # 每次爬取前先删除之前的
        self.collection.delete_many({})
        self.socketio = socketio

        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
            "cookie":"_T_WM=99296475331; SCF=ArFP1Yde47WB_7eHSXCZ_bAaVSJWRxnkR7gUGb_g5zOVUCOOHcLrxQi2KRTief1PycxxIcdgifyBjGyToyunLNc.; SUB=_2A25x8VO3DeRhGeBJ7FoT9ijEzDyIHXVTGn3_rDV6PUJbktANLWamkW1NRiNX2QMxNXMIKGD3_yDfkMXFSLD2lHhf; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5w7Lwqd.FFdq_o3e_JgEfq5JpX5KzhUgL.FoqNS0nESoqRS052dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMcS0MReoqc1hM7; SUHB=0h1Z7ZI6m03FU9; SSOLoginState=1559569383; WEIBOCN_FROM=1110006030; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803%26fid%3D102803%26uicode%3D10000011; XSRF-TOKEN=752823",
        }
        self.baseurl = "https://m.weibo.cn/api/container/getIndex?containerid=102803&openApp=0&since_id="
        self.statrtpage = 0
    def run(self):
        while self.statrtpage <= 5:
            url = self.baseurl + str(self.statrtpage)
            self.get_page(url)
            time.sleep(1)
            self.statrtpage += 1

    def get_page(self,url):
        res =  requests.get(url=url,headers=self.headers)
        self.parse(res.json())

    def parse(self,content):
        alist = content['data']['cards']
        for item in alist:
            name = item['mblog']['user']['screen_name']
            text = item['mblog']['text']
            pattern = re.compile(r'</?\.*[^>]*>')
            text = pattern.sub('',text)
            likes_num = item['mblog']['attitudes_count']
            comments_num = item['mblog']['comments_count']
            created_at = item['mblog']['created_at']
            created_at = time_fix(created_at)
            msg = f'博主: {name} 内容: {text} 点赞数: {likes_num} 评论数: {comments_num} 时间: {created_at}'
            self.socketio.emit("server_weibo_event", msg, namespace='/weibo')
            print(name)
            print(text)
            print(likes_num)
            print(comments_num)
            print(created_at)
            self.save(name,text,likes_num,comments_num,created_at)
    def save(self,name,text,likes_num,comments_num,created_at):
        with open('./a.txt','a',encoding='utf8') as f:
            text1 = name+'\t'+text+'\t'+str(likes_num)+'\t'+str(comments_num)+'\t'+created_at+'\n'
            f.write(text1)
        item = dict(
            name = name,
            text=text,
            likes_num=likes_num,
            comments_num=comments_num,
            created_at=created_at,
        )
        self.collection.insert(item)

# if __name__ == '__main__':
#     weibo = WeiBoSpider()
#     weibo.run()
