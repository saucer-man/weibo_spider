# coding:utf-8
#!/usr/bin/env python
from flask import Flask
from get_proxy import GetProxy
from check import proxy_check
from setting import origin_proxys, useful_proxys
import time
import random
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s] - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
logger = logging.getLogger(__name__)

        
@app.route('/get')
def get():
    return random.choice(list(useful_proxys))

@app.route('/get_all')
def get_all():
    return list(useful_proxys)

@app.route('/get_num')
def get_num():
    return len(useful_proxys)

if __name__ == '__main__':
    logger.info("开始爬取代理")
    proxys = GetProxy()
    proxys.get()
    # 获得没有经过过滤的ip代理
    logger.info("代理爬取完毕，一共爬取到{}条".format(len(origin_proxys)))

    # 接下来开始验证，验证完之后保存在文本中
    logger.info("接下来开始验证")
    proxy_check()
    logger.info("验证结束,有用的代理有{}条".format(len(useful_proxys)))
    logger.info(useful_proxys)

    with open("proxys.txt", 'w') as f:
        for proxy in useful_proxys:
            f.write(proxy+'\n')
    app.run(debug=True)