# -*- coding: utf-8 -*-
from scrapy import Request, Spider
import json
from weibo.items import UserItem, WeiboItem


# https://juejin.im/post/5b052d526fb9a07ac5608078


class WeiboSpider(Spider):
    name = 'weibocn'
    allowed_domains = ['m.weibo.cn']
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    # start_users = ['3217179555', '1742566624', '2282991915', '1288739185', '3952070245', '5878659096']
    # uid = '3217179555'

    def __init__(self, uid='3217179555', *args, **kwargs):
        super(WeiboSpider, self).__init__(*args, **kwargs)
        self.start_urls = self.user_url.format(uid=uid)

    def start_requests(self):
        yield Request(self.start_urls, callback=self.parse_user)

    def parse_user(self, response):
        """
        解析用户信息
        :param response: Response对象
        """
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            user_item = UserItem()
            field_map = {
                'id': 'id', 'name': 'screen_name', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
                'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
                'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                'verified_reason': 'verified_reason', 'verified_type': 'verified_type'
            }
            for field, attr in field_map.items():
                user_item[field] = user_info.get(attr)
            yield user_item

            uid = user_info.get('id')
            # 微博
            yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                          meta={'page': 1, 'uid': uid})


    def parse_weibos(self, response):
        """
        解析微博列表
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        'id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count', 'created_at': 'created_at', 'source': 'source',
                        'text': 'text', 'raw_text': 'raw_text'
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item
            # 下一页微博
            uid = response.meta.get('uid')
            page = response.meta.get('page') + 1
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                          meta={'uid': uid, 'page': page})