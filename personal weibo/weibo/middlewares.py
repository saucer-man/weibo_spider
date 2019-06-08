# -*- coding: utf-8 -*-

import random
import json
import logging
import requests



class UAMiddleware():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # 设置User-Agent
    def process_request(self, request, spider):
        agent = self.get_random_ua()
        request.headers['User-Agent'] = agent
        self.logger.debug('当前user-agent: ' + agent)

    def get_random_ua(self):
        first_num = random.randint(55, 75)
        third_num = random.randint(0, 3200)
        fourth_num = random.randint(0, 140)
        os_type = [
            '(Windows NT 6.1; WOW64)',
            '(Windows NT 10.0; WOW64)',
            '(X11; Linux x86_64)',
            '(X11; Linux i686) ',
            '(Macintosh;U; Intel Mac OS X 10_12_6;en-AU)',
            '(iPhone; U; CPU iPhone OS 11_0_6 like Mac OS X; en-SG)',
            '(Windows NT 10.0; Win64; x64; Xbox; Xbox One) ',
            '(iPad; U; CPU OS 11_3_2 like Mac OS X; en-US) ',
            '(Macintosh; Intel Mac OS X 10_14_1)'
        ]
        chrome_version = 'Chrome/{}.0.{}.{}'.format(
            first_num, third_num, fourth_num)

        random_ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                              '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                             )
        return random_ua


class CookiesMiddleware():
    def __init__(self, setting):
        self.logger = logging.getLogger(__name__)
        self.cookies_path = setting.get('COOKIES_DATA_PATH')
        self.cookies_list = self.get_cookies_list()

    @classmethod
    def from_crawler(cls, crawler): # 实例化的时候加载setting
        return cls(crawler.settings)

    def get_cookies_list(self):
        # 获取全部cookies, 返回列表
        cookies_list = []
        with open(self.cookies_path, 'r') as f:
            for cookie in f.readlines():
                try:
                    cookies = {}
                    for line in cookie.strip().split(';'):
                        name, value = line.split('=', 1)
                        cookies[name.strip()] = value.strip()
                    cookies_list.append(cookies)
                except:
                    pass
        return cookies_list

    def get_random_cookies(self):
        # 随机获取一个cookie
        try:
            cookie = random.choice(self.cookies_list)
        except Exception as e:
            self.logger.error('Get Cookies failed: {}'.format(e))
        else:
            return cookie

    def process_request(self, request, spider):
        cookie = self.get_random_cookies()
        if cookie:
            request.cookies = cookie
            self.logger.debug('使用Cookies: ' + json.dumps(cookie))

    def process_response(self, request, response, spider):
        """
        对此次请求的响应进行处理。
        """
        # 携带cookie进行页面请求时，可能会出现cookies失效的情况。访问失败会出现两种情况：1. 重定向302到登录页面；2. 也能会出现验证的情况；

        # 想拦截重定向请求，需要在settings中配置。
        if response.status in [302, 301]:
            # 如果出现了重定向，获取重定向的地址
            redirect_url = response.headers['location']
            if 'passport' in redirect_url:
                # 重定向到了登录页面，Cookie失效。
                self.logger.error('Cookies 失效')
            if '验证页面' in redirect_url:
                # Cookies还能继续使用，针对账号进行的反爬虫。
                self.logger.error('当前Cookie无法使用，需要认证。')

            # 如果出现重定向，说明此次请求失败，继续获取一个新的Cookie，重新对此次请求request进行访问。
            request.cookies = self.get_random_cookies()
            # 返回值request: 停止后续的response中间件，而是将request重新放入调度器的队列中重新请求。
            return request

        # 如果没有出现重定向，直接将response向下传递后续的中间件。
        return response

class ProxyMiddleware():
    def __init__(self, proxy_url):
        self.logger = logging.getLogger(__name__)
        self.proxy_url = proxy_url

    def get_random_proxy(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        if request.meta.get('retry_times'):
            proxy = self.get_random_proxy()
            if proxy:
                uri = 'https://{proxy}'.format(proxy=proxy)
                self.logger.debug('使用代理 ' + proxy)
                request.meta['proxy'] = uri

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            proxy_url=settings.get('PROXY_URL')
        )