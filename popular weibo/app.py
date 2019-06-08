# coding:utf-8
#!/usr/bin/env python
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit
import time
from mobile_phone_weibo import WeiBoSpider
from analyse import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('client_event',namespace='/weibo')
def server_event():
    socketio.emit("clean", namespace='/weibo') # 先清空所有内容
    socketio.emit("server_jindu_event", '正在爬取', namespace='/weibo')
    weibo = WeiBoSpider(socketio)
    weibo.run() # 微博爬虫
    socketio.emit("server_jindu_event", '爬取完毕', namespace='/weibo')
    socketio.emit("server_jindu_event", '开始分析', namespace='/weibo')
    top(socketio) # 接下来开始分析，先获取之最
    socketio.emit("server_jindu_event", '开始分词', namespace='/weibo')
    fenci() # 在进行结巴分词
    socketio.emit("server_jindu_event", '开始生成词云', namespace='/weibo')
    wordcloud(socketio) # 生成词云
    socketio.emit("server_jindu_event", '开始情感分析', namespace='/weibo')
    qinggan(socketio) # 情感分析
    socketio.emit("server_jindu_event", '分析完毕', namespace='/weibo')
        
        # time.sleep(600)

    # for i in range(10):
    #     time.sleep(1)server_event
    #     emit('server_event', msg, namespace='/subdomain')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0',port=801,debug=True)
