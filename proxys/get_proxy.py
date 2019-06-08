#!/usr/bin/env python3
# coding:utf-8
# date:2019/04/17
# 免费代理爬取

from gevent import monkey
monkey.patch_all()
import gevent
from lxml import etree
import requests 
from setting import origin_proxys, headers


class GetProxy:
    def __init__(self):
        # 设置爬取的页数
        self.xicidaili_page_count = 5
        self.kuaidaili_page_count = 5
        self.jiangxianli_page_count = 5

    def get(self):
        gevent.joinall(
            [gevent.spawn(self._xicidaili),
            gevent.spawn(self._goubanjia),
            gevent.spawn(self._kuaidaili),
            gevent.spawn(self._jiangxianli),
            ])

    def _xicidaili(self):
        url_list = [
            'https://www.xicidaili.com/nn/',  # 高匿
            'https://www.xicidaili.com/nt/',  # 透明
        ]
        for each_url in url_list:
            for page in range(1, self.xicidaili_page_count + 1):
                page_url = each_url + str(page)
                try:
                    r = requests.get(page_url, headers=headers)
                    html = etree.HTML(r.text)
                    proxy_list = html.xpath('.//table[@id="ip_list"]//tr[position()>1]')
                    for proxy in proxy_list:
                        ip= proxy[1].xpath('string(.)').strip()
                        port = proxy[2].xpath('string(.)').strip()
                        protocol = proxy[5].xpath('string(.)').strip()
                        if protocol.lower() == "https":
                            origin_proxys.add("https://" + ip + ":" + port)
                        elif protocol.lower() == "http":
                            origin_proxys.add("http://" + ip + ":" + port)
                    gevent.sleep(2)
                except:
                    pass

    def _goubanjia(self):
        # guobanjia http://www.goubanjia.com/
        for i in range(2):
            r = requests.get('http://www.goubanjia.com', headers=headers)
            html = etree.HTML(r.text)
            proxy_list = html.xpath('//tr')
            xpath_str = """.//*[not(contains(@style, 'display: none'))
                            and not(contains(@style, 'display:none'))
                            and not(contains(@class, 'port'))
                            ]/text()
                    """
            for each_proxy in proxy_list[1:]:
                tds = each_proxy.xpath('./td')
                ip = ''.join(tds[0].xpath(xpath_str))
                port = tds[0].xpath(".//span[contains(@class, 'port')]/text()")[0]
                protocol = tds[2].xpath('string(.)').strip()
                if protocol.lower() == "https":
                    origin_proxys.add("https://" + ip + ":" + port)
                elif protocol.lower() == "http":
                    origin_proxys.add("http://" + ip + ":" + port)
            # gevent.sleep(3)

    def _kuaidaili(self):
        """
        快代理 https://www.kuaidaili.com
        """
        url_list = [
            'https://www.kuaidaili.com/free/inha/',
            'https://www.kuaidaili.com/free/intr/'
        ]
        for url in url_list:
            for i in range(1, self.kuaidaili_page_count+1):
                page_url = url + '/'+ str(i)
                r = requests.get(url, headers=headers)
                html = etree.HTML(r.text)
                proxy_list = html.xpath('.//table//tr')
                for tr in proxy_list[1:]:
                    ip = tr.xpath('./td/text()')[0]
                    port = tr.xpath('./td/text()')[1]
                    protocol = tr.xpath('./td/text()')[3]
                    if protocol.lower() == "https":
                        origin_proxys.add("https://" + ip + ":" + port)
                    elif protocol.lower() == "http":
                        origin_proxys.add("http://" + ip + ":" + port)
    
    def _jiangxianli(self):
        """
        http://ip.jiangxianli.com
        免费代理库
        """
        for i in range(1, self.kuaidaili_page_count+1):
            url = 'http://ip.jiangxianli.com/?page={}'.format(i)
            r = requests.get(url, headers=headers)
            html = etree.HTML(r.text)
            tr_list = html.xpath("/html/body/div[1]/div/div[1]/div[2]/table/tbody/tr")
            if len(tr_list) == 0:
                break
            for tr in tr_list:
                ip = tr.xpath("./td[2]/text()")[0]
                port = tr.xpath("./td[3]/text()")[0]
                protocol = tr.xpath("./td[5]/text()")[0]
                if protocol.lower() == "https":
                    origin_proxys.add("https://" + ip + ":" + port)
                elif protocol.lower() == "http":
                    origin_proxys.add("http://" + ip + ":" + port)

