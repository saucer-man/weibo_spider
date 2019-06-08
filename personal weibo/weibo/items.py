# -*- coding: utf-8 -*-

from scrapy import Item, Field


class UserItem(Item):
    collection = 'users'

    id = Field()
    name = Field()
    avatar = Field()
    cover = Field()
    gender = Field()
    description = Field()
    fans_count = Field()
    follows_count = Field()
    weibos_count = Field()
    verified = Field()
    verified_reason = Field()
    verified_type = Field()
    follows = Field()
    fans = Field()
    crawled_at = Field() # 爬取时间





class WeiboItem(Item):
    collection = 'weibos'

    id = Field()
    attitudes_count = Field()
    comments_count = Field()
    reposts_count = Field()
    source = Field()
    text = Field()
    raw_text = Field()
    user = Field()
    created_at = Field()  # 微博创建发布时间
    crawled_at = Field()  # 爬取时间