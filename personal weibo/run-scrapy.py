from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
import os

def runSpider():
    args = sys.argv
    uid= args[1]
    print(uid)
    dir_name = './result/'+str(uid)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    process = CrawlerProcess(get_project_settings())
    print(get_project_settings())
    name = ['weibocn']
    #for i in name:
    #    process.crawl(i,userid='leon')
    #    process.start()
    process.crawl('weibocn',uid)
    process.start()
