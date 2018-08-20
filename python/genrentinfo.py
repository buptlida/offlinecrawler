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

httpHandler = urllib.request.HTTPHandler(debuglevel=1)
httpsHandler = urllib.request.HTTPSHandler(debuglevel=1)
cookiejar = http.cookiejar.CookieJar()
cookie_support= urllib.request.HTTPCookieProcessor(cookiejar = cookiejar)
opener = urllib.request.build_opener(httpHandler, httpsHandler, cookie_support)
urllib.request.install_opener(opener)

rentinfo = []

def scrawler(queue):
  time.sleep(1)
  while not queue.empty():
    try:
      print('thread %s is running...' % threading.currentThread().name)
      # 不阻塞的读取队列数据
      url = queue.get_nowait()
      getrentinfo(url)
    except Exception as e:
      print(e)
      continue

def multithread(func, q, number):
    thread_list = []
    for i in range(number):
        t = threading.Thread(target=func, args=(q), name="child_thread_%d" % i)
        thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

def getrentinfo(baseurl):
  global rentinfo
  print("getrent start")
  baseurl = "https://www.douban.com/group/beijingzufang/discussion?start="
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
    for r in result:
      data = []
      data.append(r.a["href"])
      title = r.a["title"]
      data.append(title)
      data.append(r.next_sibling.next_sibling.string)
      num = r.next_sibling.next_sibling.next_sibling.next_sibling.string
      if num==None:
          data.append(-1)
      else:
          data.append(int(num))
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
      info = []
      GetInfo(title, content, info)
      firstedit = soup.select(".color-green")[0].string
      timeArray = time.strptime(firstedit, "%Y-%m-%d %H:%M:%S")
      data.append(int(time.mktime(timeArray)))
      print(content)
      time.sleep(4)

def GetInfo(title, content, info):
  ##判断主次卧
  pat1 = re.compile('次卧')
  pat2 = re.compile('主卧')
  info.append(bool(pat1.search(content)))
  info.append(bool(pat2.search(content)))
  ##判断限男女
  pat3 = re.compile('男')
  pat4 = re.compile('女')
  pat5 = re.compile('不限')
  info.append(bool(pat3.search(title)) and  (not bool(pat5.search(title))))
  info.append(bool(pat4.search(title)) and  (not bool(pat5.search(title))))
  ##判断整合组
  pat6 = re.compile('整租|整套直租|整套出租|整套')
  info.append(bool(pat6.search(title)))
  ##判断房型
  pat7 = re.compile('1居|一居|1室|一室')
  info.append(bool(pat7.search(title)))
  pat8 = re.compile('2居|两居|二居|2室|两室')
  info.append(bool(pat8.search(title)))
  pat9 = re.compile('3居|三居|3室|三室')
  info.append(bool(pat9.search(title)))
  pat10 = re.compile('4居|四居|4室|四室')
  info.append(bool(pat10.search(title)))
  pat11 = re.compile('单间')
  info.append(bool(pat11.search(title)))
  ##押金类别
  pat12 = re.compile('押一付一|押1付1')
  info.append(bool(pat12.search(content)))
  pat13 = re.compile('押一付二|押1付2')
  info.append(bool(pat13.search(content)))
  pat14 = re.compile('押一付三|押1付3')
  info.append(bool(pat14.search(content)))
  ##判断价格
  pat15 = re.compile(' \d{4} |\d{3,4}/月|主卧:\d{3,4}|主卧\d{3,4}|次卧:\d{3,4}|次卧\d{3,4}|\d{3,4}元|\d{3,4}-\d{3,4}|\d{3,4}到\d{3,4}|隔断\d{3,4}|价格\d{3,4}|每月\d{3,4}|\d{3,4}每月|一个月\d{3,4}|\d{3,4}一个月|整租:\d{3,4}|整租\d{3,4}|为\d{3,4}|小卧室\d{3,4}|大卧室\d{3,4}|月付\d{3,4}|\d{3,4}~\d{3,4}|\d{3,4}～\d{3,4}|房租:\d{3,4}|房租\d{3,4}|\d{3,4}--\d{3,4}|起\d{3,4}|租金\d{3,4}|合租\d{3,4}')
  #pat15 = re.compile(' \d{4} |\d{4}/月|主卧\d{4}|主卧:\d{4}|次卧\d{4}|次卧:\d{4}|\d{4}元|\d{4}-\d{4}|\d{4}到\d{4}|隔断\d{4}|价格\d{4}|每月\d{4}|\d{4}每月|一个月\d{4}|\d{4}一个月|整租\d{4}|整租：\d{4}|为\d{4}')
  price = pat15.findall(title + content)
  rental = set()
  for p in price:
      #rental.add(p.replace("主卧|次卧|元|/月","").strip()) 
      #info.append(price[0].replace("主卧","").replace("次卧","").replace("元","").replace("/月","").strip())
      if "-" in p:
          ptwo = p.split("-")
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
          continue
      if "--" in p:
          ptwo = p.split("-")
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
          continue
      if "到" in p:
          ptwo = p.split("到")
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
          continue
      if "~" in p:
          ptwo = p.split("~")
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
          continue
      if "～" in p:
          ptwo = p.split("~")
          rental.add(int(ptwo[0]))
          rental.add(int(ptwo[1]))
          continue
      m = p.replace("主卧:","").replace("次卧:","").replace("元","").replace("/月","").replace("隔断","").replace("价格","").replace("每月","").replace("一个月","").replace("主卧","").replace("次卧","").replace("为","").replace("小卧室","").replace("大卧室","").replace("月付","").replace("房租:","").replace("房租","").replace("起","").replace("租金","").replace("合租","").strip()
      rental.add(int(m))
  pat16 = re.compile('\d{4}')
  p = pat16.findall("\d{4}")
  if len(p)==1:
      rental.add(int(p[0]))
  print(rental)
 
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
  #获取各小组内租房信息
  #q = putGroupUrlToQueue()
  #multithread(scrawler, q, 50)
  getrentinfo("a")
  
  
