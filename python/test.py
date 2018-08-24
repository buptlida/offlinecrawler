#!encoding=utf-8
import sys
import urllib
import urllib.request
from bs4 import BeautifulSoup 
import http.cookiejar
import queue
import jieba
import threading
import time
import datetime
import re
import hashlib
import pymysql

httpHandler = urllib.request.HTTPHandler(debuglevel=0)
httpsHandler = urllib.request.HTTPSHandler(debuglevel=0)
cookiejar = http.cookiejar.CookieJar()
cookie_support= urllib.request.HTTPCookieProcessor(cookiejar = cookiejar)
opener = urllib.request.build_opener(httpHandler, httpsHandler, cookie_support)
urllib.request.install_opener(opener)

rentinfo = []

areainfo = dict()
subarea = list()
subinfo = dict()
subways = list()

areanum = dict()
subareanum = dict()
subwaysnum = dict()
subwaynum = dict()

db = pymysql.connect(host="127.0.0.1", port=3306, db="rentinfo", user="root", passwd="buptlida", charset='utf8', unix_socket="/opt/lampp/var/mysql/mysql.sock")
cur = db.cursor()
data=['https://www.douban.com/group/topic/120895668/', '21efdc95816e1fab9136dbbc91f6af2b', '诚心求方庄蒲黄榆附近2居', "yi'lu", -1, 1532438820, '诚心求方庄蒲黄榆附近2居', 1532438832, -1, -1, -1, 2, -1, 0, 150, 4, 246, 10, '豆瓣']
sql = "insert into info(md5url,url,title,author,firsteditime,bedroom,gender,renttype,housetype,cashtype,price,streetcode,regioncode,sublinecode,subwaycode,source) values('" + \
              data[1] + "','" + data[0] + "','" + data[2] + "','" + data[3] + "'," + ",".join([str(d) for d in data[7:-1]]) + ",'" + data[-1] + "')"
print(sql)
#cur.execute(sql) 
#db.commit()
