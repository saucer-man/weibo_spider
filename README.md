## weibo_spider

### 1. 代理池

从以下免费代理网站爬取的：

- 西刺免费代理 https://www.xicidaili.com/
- goubanjia http://www.goubanjia.com/
- 快代理 https://www.kuaidaili.com
- 免费代理库 http://ip.jiangxianli.com

采用flask提供api接口，爬取完毕之后会通过setting.py里面的website验证代理有效性。


### 2. 个人微博的爬取及分析

![](https://github.com/saucer-man/weibo_spider/blob/master/img/process.png?raw=true)

主要流程：

- 前端输入要爬取的用户uid
- 后端收到请求，针对该用户，调用爬虫爬取其所有微博，并对微博内容进行整理，存入数据库
- 调用分析模块对整理后的微博内容进行分析
  - 从数据库取出微博内容
  - 获取评论，点赞的最多的微博
  - 将所有微博内容使用jieba分词
  - 利用WordCloud生成词云
  - 利用SnowNLP进行情感分析
- 在web界面展示出爬取及分析结果

技术栈：

- 前端 bootstrap+jquery
- 后端 python flask + websocket
- 爬虫 scrapy(代理池，cookie池，随机user-agent)
- 数据库 mongodb
- 内容分析 python自然语言处理库(jieba、wordcloud、snownlp、numpy)

分析结果：

- top

![](https://github.com/saucer-man/weibo_spider/blob/master/img/result1.png?raw=true)

- 词云

![](https://github.com/saucer-man/weibo_spider/blob/master/img/result2.png?raw=true)

- 情感

![](https://github.com/saucer-man/weibo_spider/blob/master/img/result3.png?raw=true)

### 3.  热点微博的爬取及分析

流程类似，只是爬虫部分换成了requests，没有用scrapy

技术栈基本一致。。

### 4. 备注

只是个课程小作业，代码写的比较丑，只是在github保存一下。如果有人(基本没人)会用到代码的话，可供改进的点：
- 代理池可用数量比较少，尤其是对于weibo这样的https网站，免费的总不让人省心。
- 前端写的反人类的丑(虽然用bootstrap撸的，然后基本没有装饰)
- 个人微博爬虫采用的是scrapy，热点微博爬虫是直接requests取的，建议把两个爬虫写进一个scrapy项目里，两个项目也可以合并为一个web项目。
- 分析部分情感分析，snownlp需要语料库训练才会准确(默认语料库不适合微博内容)。本项目是基于频率绘图，可以基于时间线绘图。


为啥自己不改进？都说了课程小作业了，另外爬微博真的没意思。





