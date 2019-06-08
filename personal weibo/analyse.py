# 导入相关模块
from snownlp import SnowNLP
import pymongo
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba
import codecs
import re
import numpy as np
import base64
'''
def users():
    client = pymongo.MongoClient('192.168.2.170', 27017)
    db = client['weibo']
    collection = db['users']
    users = collection.find_one({"id":userid})
    print("用户信息")
    print(f"id:{users['id']}")
    print(f"用户名:{users['name']}")
    gender = "男" if users['gender']=="m" else "女"
    print(f"性别:{gender}")
    if users['verified']:
        print(f"微博认证:{users['verified_reason']}")
    print(f"头像:{users['avatar']}")
    print(f"粉丝数:{users['fans_count']}")
    print(f"关注数:{users['follows_count']}")
    print(f"微博数:{users['weibos_count']}")
    client.close()
'''
def top(socketio):
    # 获取转发，评论，点赞的最多的微博
    client = pymongo.MongoClient('192.168.2.170', 27017)
    db = client['weibo']
    collection = db['weibos']

    print("点赞数最多的微博")
    weibos = collection.find().sort('attitudes_count',pymongo.DESCENDING).limit(1)
    #for result in weibos:
    #   print(result)
    print(f"时间：{weibos[0]['created_at']}    点赞数：{weibos[0]['attitudes_count']}\n内容：{weibos[0]['text']}")
    msg= f"时间：{weibos[0]['created_at']}    点赞数：{weibos[0]['attitudes_count']}\n内容：{weibos[0]['text']}"
    socketio.emit("server_analyse_event", '点赞数最多的微博', namespace='/uid')
    socketio.emit("server_analyse_event", msg, namespace='/uid')
    
    print("评论数最多的微博")
    weibos = collection.find().sort('comments_count',pymongo.DESCENDING).limit(1)
    print(f"时间：{weibos[0]['created_at']}    评论数：{weibos[0]['comments_count']}\n内容：{weibos[0]['text']}")
    msg=f"时间：{weibos[0]['created_at']}    评论数：{weibos[0]['comments_count']}\n内容：{weibos[0]['text']}"
    socketio.emit("server_analyse_event", '评论数最多的微博', namespace='/uid')
    socketio.emit("server_analyse_event", msg, namespace='/uid')

    print("转发最多的微博")
    weibos = collection.find().sort('reposts_count',pymongo.DESCENDING).limit(1)
    print(f"时间：{weibos[0]['created_at']}    转发数：{weibos[0]['reposts_count']}\n内容：{weibos[0]['text']}")
    msg= f"时间：{weibos[0]['created_at']}    转发数：{weibos[0]['reposts_count']}\n内容：{weibos[0]['text']}"
    socketio.emit("server_analyse_event", '转发最多的微博', namespace='/uid')
    socketio.emit("server_analyse_event", msg, namespace='/uid')

    client.close()


def fenci():
    # 读取所有微博，利用jieba中文分词，保存在fenci_text.txt
    client = pymongo.MongoClient('192.168.2.170', 27017)
    db = client['weibo']
    collection = db['weibos']
    fenci_text = codecs.open("fenci_text.txt",'w','utf-8')
    for x in collection.find({}, {'text':1, '_id':0}):
        text = re.sub(r"<.*?>|[\U00010000-\U0010ffff]|[\uD800-\uDBFF][\uDC00-\uDFFF]|", "", x['text'])
        text = re.sub(r"@.*?:","",text)
        text = re.sub(r"[@|.|/|'|\"|!！|,|。|:|?|？|(|（|)|）|…|“ |”|、|《|》|，|：|—|_|;|･|#|ˊ_&gt;]", "", text) # 去除标点
        words = [word for word in jieba.cut(text, cut_all=False) if len(word) >= 2]
        output = r" ".join(words)
        fenci_text.write(output+" ")
    fenci_text.write("\r\n")
    fenci_text.close()
    client.close()



def wordcloud(socketio):
    # 读取分词结果，进行词云的生成
    exclude_words = [
        "哈哈哈", "哈哈", "哈哈哈哈", "现在", "这个", "什么", "就是",
        "这样", "不要", "一起", "你们", "自己", "起来", "没有",
        "有点", "如果", "知道", "还有", "怎么", "已经", "不会",
        "感觉", "可能", "看到", "还是", "供给", "坚决", "力度",
        "查看", "回忆", "专用", "图片", "大家", "不是", "朋友",
        "他们", "觉得", "可以", "本人", "全文", "链接", "马甲",
        "视频", "以后", "以前", "今天", "微博", "转发"
        ]
    exclude_words = "|".join(exclude_words)
    datas = open('fenci_text.txt','r',encoding='utf-8').read()
    datas = re.sub(exclude_words, "", datas)
    # back_coloring = imread("heart.jpg")
    my_wordcloud = WordCloud(font_path="simsun.ttf",
                    background_color="white",  # 背景颜色
                    max_words=1000,  # 词云显示的最大词数
                    # mask=back_coloring,  # 设置背景图片
                    max_font_size=150,  # 字体最大值
                    random_state=42,
                    ).generate(datas)
    plt.imshow(my_wordcloud)
    plt.axis("off")
    plt.savefig("wordcloud.png")
    with open (r'wordcloud.png','rb') as f:
        msg = base64.b64encode(f.read())

    print(type(msg))
    socketio.emit("server_wordcloud_event",msg.decode(), namespace='/uid')
    print("图片发送完毕")

def qinggan(socketio):# 情感分析
    # 先读文章打分
    client = pymongo.MongoClient('192.168.2.170', 27017)
    db = client['weibo']
    collection = db['weibos']
    qinggan = codecs.open("qinggan_result.txt",'w','utf-8')
    for x in collection.find({}, {'text':1, 'created_at': 1,}):
        s = SnowNLP(x['text'])
        qinggan.write(x['created_at'] + ":  " + str(s.sentiments) + "\n")
    qinggan.write("\r\n")
    qinggan.close()

    # 再进行绘图
    sentimentslist = []
    with open('qinggan_result.txt','r',encoding='utf-8') as f:
        for line in f.readlines():
            try:
                sentiment = line.split(':')[-1].strip()
                sentimentslist.append(float(sentiment))
            except Exception as e:
                print(e)
                print(line)
    plt.figure("sentiment")
    plt.hist(sentimentslist, bins=np.arange(0, 1, 0.02))
    plt.savefig("qinggan.png")

    with open (r'qinggan.png','rb') as f2:
        msg = base64.b64encode(f2.read())

    print(type(msg))
    socketio.emit("server_qinggan_event",msg.decode(), namespace='/uid')
    print("图片发送完毕")
    client.close()

# if __name__=="__main__":
#     global userid
#     userid = 3217179555
#     users() # 获取用户信息
#     top() # 获取微博之最
#     print("开始分词")
#     fenci()
#     print("开始生成词云")
#     wordcloud() # 获取微博词云
#     print("开始情感分析")
#     qinggan() # 对微博内容进行情感分析
