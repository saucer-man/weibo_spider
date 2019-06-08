from flask import Flask
from flask import render_template
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
from flask_socketio import SocketIO, emit
from analyse import *
import pymongo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

def runSpider(uid):
    print(uid)
    dir_name = './result/'+str(uid)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    process = CrawlerProcess(get_project_settings())
    print(get_project_settings())
    # name = ['weibocn']
    process.crawl('weibocn',uid)
    process.start()
    process.join()

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@socketio.on('client_event', namespace='/uid')
def search(uid):
    # 开始爬取之前先清空mongodb
    client = pymongo.MongoClient('192.168.2.170', 27017)
    db = client['weibo']
    collection = db['weibos']
    collection.delete_many({})
    collection = db['user']
    collection.delete_many({})
    # print("接收到了"+uid)
    runSpider(uid)
    with open(f'result/{uid}/user.json',encoding='utf-8') as f:
        for msg in f.readlines():
            print("--------------------------")
            socketio.emit("weibo_response", msg, namespace='/uid')
    with open(f'result/{uid}/weibo.json',encoding='utf-8') as f:
        for msg in f.readlines():
            socketio.emit("weibo_response", msg, namespace='/uid')
    top(socketio)
    fenci()
    wordcloud(socketio)
    qinggan(socketio)
    print('Ok!')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0',port=800,debug=True)
