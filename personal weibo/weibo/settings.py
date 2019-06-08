# -*- coding: utf-8 -*-


BOT_NAME = 'weibo'

SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'


# 数据库
MONGO_URI = '192.168.2.170'
MONGO_PORT = 27017
MONGO_DATABASE = 'weibo'

# Obey robots.txt rules
# 首先去掉robots改动
ROBOTSTXT_OBEY = False

# 并发数
CONCURRENT_REQUESTS = 20

# 延迟时间
DOWNLOAD_DELAY = 0

# 设置默认请求头
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
    'Connection': 'keep-alive',
    'Host': 'm.weibo.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}




# 设置log级别
LOG_LEVEL = 'INFO'

# 是否开启缓存
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 设置pipeline，先存储到本地文件
ITEM_PIPELINES = {
    'weibo.pipelines.WeiboTimePipeline': 301,  # 格式化创建时间和爬取时间
    'weibo.pipelines.MongoPipeline': 302,  # 保存到数据库中
    'weibo.pipelines.SavefilePipeline': 303,  # 保存在文件中
}

# 设置中间件
DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.UAMiddleware': 542, # useragent
    'weibo.middlewares.CookiesMiddleware': 543,  # cookie中间件,数字越小，越先执行
}
# Cookie池，这里先使用文件中读取
COOKIES_DATA_PATH = 'D:\\Code\\test\\weibo\\data\\cookies.txt'

# 代理池
PROXY_URL = "http://127.0.0.1:5000/get"
