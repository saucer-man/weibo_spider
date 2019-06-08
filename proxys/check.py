#!/usr/bin/env python3
# coding:utf-8

from gevent import monkey
monkey.patch_all()
import gevent

from setting import origin_proxys, useful_proxys, website, headers

import requests

def proxy_check():
    if len(origin_proxys) > 300:
        gevent.joinall([gevent.spawn(check) for i in range(0, 300)])
    else:
        gevent.joinall([gevent.spawn(check) for i in range(0, len(origin_proxys))])


def check():
    # 验证代理
    while len(origin_proxys) > 0:
        ip_for_test = origin_proxys.pop()
        proxies = {
        'https': ip_for_test,
        'http': ip_for_test
        }
        try:
            response = requests.get(website, headers=headers, proxies=proxies, timeout=5)
            # print(response.headers)
            if response.status_code == 200:
                useful_proxys.add(ip_for_test)
        except Exception as e:
            # print(e)
            continue


            