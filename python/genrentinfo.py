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

def genareainfo():
  global subarea
  global areainfo
  global subinfo
  global subways
  global areanum
  global subareanum
  global subwaysnum
  global subwaynum
  with open("../data/area.txt") as file:
    for line in file:
      info = line.strip().split(":")
      if len(info)==2:
        for a in info[1].split(" "):
          subarea.append(a)
          areainfo[a] = info[0]
  with open("../data/subway.txt") as file:
    for line in file:
      info = line.strip().split(":")
      if len(info)==2:
        for a in info[1].split(" "):
          subways.append(a)
          subinfo[a] = info[0]
  with open("../data/areanum.txt") as file:
    for line in file:
      info = line.strip().split("\t")
      areanum[info[0]] = info[1] 
  with open("../data/subareanum.txt") as file:
    for line in file:
      info = line.strip().split("\t")
      subareanum[info[0]] = info[1] 
  with open("../data/subwaysnum.txt") as file:
    for line in file:
      info = line.strip().split("\t")
      subwaysnum[info[0]] = info[1] 
  with open("../data/subwaynum.txt") as file:
    for line in file:
      info = line.strip().split("\t")
      subwaynum[info[0]] = info[1] 
  

def scrawler(queue):
  time.sleep(1)
  threedaysago = int(time.time()) - 3600
  while not queue.empty():
    try:
      print('thread %s is running...' % threading.currentThread().name)
      # 不阻塞的读取队列数据
      url = queue.get_nowait()
      getrentinfo(url, threedaysago)
    except Exception as e:
      print(e)
      continue

def multithread(func, q, number):
    thread_list = []
    for i in range(number):
        t = threading.Thread(target=func, args=(q,), name="child_thread_%d" % i)
        thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

def getrentinfo(baseurl, threedaysago):
  global rentinfo
  count = -1
  while True:
    count += 1
    url = baseurl + str(25 * count)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36", "Upgrade-Insecure-Requests":1, "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Cache-Control":"max-age=0", "Host":"www.douban.com"}
    request = urllib.request.Request(url = url, headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read().decode("UTF-8")
    soup = BeautifulSoup(html, "html.parser")
    result = soup.select(".olt .title")
    ##线程退出标识
    tag = 0
    rlen = len(result)
    for r in result:
      data = []
      data.append(r.a["href"])
      title = r.a["title"].strip()
      data.append(title)
      data.append(r.next_sibling.next_sibling.string)
      num = r.next_sibling.next_sibling.next_sibling.next_sibling.string
      if num==None:
          data.append(-1)
      else:
          data.append(int(num))
      if len(r.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.string)==10:
          lastreply = r.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.string + " 00:00"
      else:
          lastreply = str(datetime.datetime.now().year) + "-" + r.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.string
      timeArray = time.strptime(lastreply, "%Y-%m-%d %H:%M")
      data.append(int(time.mktime(timeArray)))
      request = urllib.request.Request(url = r.a["href"], headers=headers)
      response = urllib.request.urlopen(request)
      html = response.read().decode("UTF-8")
      soup = BeautifulSoup(html, "html.parser")
      content = title
      result = soup.select(".topic-richtext p") 
      for r in result:
          if r.string==None:
              continue
          content = content +  r.string.strip() + " " 
      data.append(content)
      firstedit = soup.select(".color-green")[0].string
      timeArray = time.strptime(firstedit, "%Y-%m-%d %H:%M:%S")
      data.append(int(time.mktime(timeArray)))
      data = GetInfo(title, content, data)
      if data[4] < threedaysago:
        tag += 1
      time.sleep(4)
    ##该线程释放
    if tag==rlen:
      return 

def GetInfo(title, content, data):
  ##判断主次卧
  tag = -1
  pat1 = re.compile('次卧')
  pat2 = re.compile('主卧')
  if bool(pat1.search(content)) and not bool(pat2.search(content)):
    tag = 1
  elif not bool(pat1.search(content)) and bool(pat2.search(content)):
    tag = 2
  elif bool(pat1.search(content)) and bool(pat2.search(content)):
    tag = 3 
  data.append(tag)
  ##判断限男女
  tag = -1
  pat3 = re.compile('男')
  pat4 = re.compile('女')
  pat5 = re.compile('不限')
  if bool(pat3.search(title)) and  (not bool(pat5.search(title))):
    tag = 1 
  if bool(pat4.search(title)) and  (not bool(pat5.search(title))):
    tag = 2
  data.append(tag)
  ##判断整合组
  tag = -1
  pat6 = re.compile('整租|整套直租|整套出租|整套')
  if bool(pat6.search(title)):
    tag = 1
  data.append(tag)
  ##判断房型
  tag = -1
  pat7 = re.compile('1居|一居|1室|一室')
  tag = 1 if bool(pat7.search(title)) else tag 
  pat8 = re.compile('2居|两居|二居|2室|两室')
  tag = 2 if bool(pat8.search(title)) else tag
  pat9 = re.compile('3居|三居|3室|三室')
  tag = 3 if bool(pat9.search(title)) else tag
  pat10 = re.compile('4居|四居|4室|四室')
  tag = 4 if bool(pat10.search(title)) else tag
  pat11 = re.compile('单间')
  tag = 5 if bool(pat11.search(title)) else tag
  data.append(tag)
  ##押金类别
  tag = -1
  pat12 = re.compile('押一付一|押1付1')
  tag = 1 if bool(pat12.search(content)) else tag
  pat13 = re.compile('押一付二|押1付2')
  tag = 2 if bool(pat13.search(content)) else tag
  pat14 = re.compile('押一付三|押1付3')
  tag = 3 if bool(pat14.search(content)) else tag
  data.append(tag)
  ##判断价格
  pat15 = re.compile(' \d{4,5} |\d{3,}/月|主卧:\d{3,}|主卧\d{3,}|次卧:\d{3,}|次卧\d{3,}|\d{3,}元|\d{3,}-\d{3,}|\d{3,}到\d{3,}|隔断\d{3,}|价格\d{3,}|每月\d{3,}|\d{3,}每月|一个月\d{3,}|\d{3,}一个月|整租:\d{3,}|整租\d{3,}|为\d{3,}|小卧室\d{3,}|大卧室\d{3,}|月付\d{3,}|\d{3,}~\d{3,}|\d{3,}～\d{3,}|房租:\d{3,}|房租\d{3,}|\d{3,}--\d{3,}|起\d{3,}|租金\d{3,}|合租\d{3,}|急租\d{3,}|价格：/d{3,}|价格:\d{3,}')
  price = pat15.findall(title + content)
  rental = set()
  for p in price:
      if "-" in p:
          ptwo = p.split("-")
          if not (ptwo[0].isdigit() and ptwo[1].isdigit()):
            continue
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
      if "--" in p:
          ptwo = p.split("-")
          if not (ptwo[0].isdigit() and ptwo[1].isdigit()):
            continue
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
      if "到" in p:
          ptwo = p.split("到")
          if not (ptwo[0].isdigit() and ptwo[1].isdigit()):
            continue
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
      if "~" in p:
          ptwo = p.split("~")
          if not (ptwo[0].isdigit() and ptwo[1].isdigit()):
            continue
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
      if "～" in p:
          ptwo = p.split("~")
          if not (ptwo[0].isdigit() and ptwo[1].isdigit()):
            continue
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
      m = p.replace("主卧:","").replace("次卧:","").replace("元","").replace("/月","").replace("隔断","").replace("价格","").replace("每月","").replace("一个月","").replace("主卧","").replace("次卧","").replace("为","").replace("小卧室","").replace("大卧室","").replace("月付","").replace("房租:","").replace("房租","").replace("起","").replace("租金","").replace("合租","").replace("急租","").replace("价格：","").replace("价格:","").strip()
      if m.isdigit():
          rental.add(int(m))
  pat16 = re.compile('\d{4}')
  p = pat16.findall("\d{4}")
  if len(p)==1:
      rental.add(int(p[0]))
  tag = -1 
  for r in rental:
    if r < 1500:
      tag = 0
    else:
      num = pow(2, int(r/500 -3))
      tag = (tag | num)
  data.append(tag)  
  ##获取区域信息
  belong = [-1,-1,-1,-1]
  for a in subarea:
    if a in title:
      belong[0] = int(subareanum[a])
      belong[1] = int(areanum[areainfo[a]])
      break
  for a in subways:
    if a in title:
      belong[2] = int(subwaynum[a])
      belong[3] = int(subwaysnum[subinfo[a]])
      break
  print(title)
  print(belong)
  data = data + belong
  return data
      
  
 
def SortAndWriteToFile():
  output = open("../data/groupinfo.txt", "w")
  for group in groupinfo:
    output.write(group[0] + "\t" + str(group[1]) + "\n")
  output.close()

def putGroupUrlToQueue():
  que = queue.Queue()
  with open("../data/groupinfo.txt") as file:
    for line in file:
      info = line.strip().split("\t")
      que.put(info[0] + "/discussion?start=")
  return que

if __name__=="__main__":
  genareainfo()
  #获取各小组内租房信息
  q = putGroupUrlToQueue()
  multithread(scrawler, q, 1)
  
  
