import sys
import urllib
import urllib.request
from bs4 import BeautifulSoup 
import http.cookiejar
import queue
import jieba
import threading
import time
import os

httpHandler = urllib.request.HTTPHandler(debuglevel=1)
httpsHandler = urllib.request.HTTPSHandler(debuglevel=1)
cookiejar = http.cookiejar.CookieJar()
cookie_support= urllib.request.HTTPCookieProcessor(cookiejar = cookiejar)
opener = urllib.request.build_opener(httpHandler, httpsHandler, cookie_support)
urllib.request.install_opener(opener)

groupinfo = []

def getcity():
  cities = []
  with open("./data/PLACE.txt") as file:
    for line in file:
      info =  line.strip()
      cities.append(info)
  return cities

def geturl(query):
  print("put queue start")
  url = "https://www.douban.com/group/search?"
  data = {"cat":1019, "q":query}
  url_parame=urllib.parse.urlencode(data)
  request = urllib.request.Request(url + url_parame)
  request.add_header("User-Agent", "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)")
  response = urllib.request.urlopen(request)
  html = response.read().decode("UTF-8")
  soup = BeautifulSoup(html, "lxml")
  addresses = soup.select('.paginator a')
  suburl = addresses[0].get("href").split("&")
  gapnum = int(suburl[0][42:]) 
  info = ["https://www.douban.com/group/search?start=","&".join(suburl[1:]), gapnum, int(addresses[-2].string)]
  que = queue.Queue()
  for i in range(1, info[3]):
    que.put(info[0] + str(info[2] * (i-1)) + "&" + info[1])
  print("put queue over")
  return que

def scrawler(queue, query):
  time.sleep(1)
  while not queue.empty():
    try:
      print('thread %s is running...' % threading.currentThread().name)
      # 不阻塞的读取队列数据
      url = queue.get_nowait()
      getgroup(url, query)
    except Exception as e:
      print(e)
      continue

def multithread(func, q, query, number):
    thread_list = []
    for i in range(number):
        t = threading.Thread(target=func, args=(q, query), name="child_thread_%d" % i)
        thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

def getgroup(url, query):
  global groupinfo
  print("getgroup start")
  request = urllib.request.Request(url)
  request.add_header("User-Agent", "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)")
  response = urllib.request.urlopen(request)
  html = response.read().decode("UTF-8")
  soup = BeautifulSoup(html, "lxml")
  result = soup.select(".result .content")
  for r in result:
    humanterms = ",".join(jieba.cut(r.select("a")[0].string))
    terms = humanterms.split(",") 
    if not (query in terms and "租房" in terms):
      continue
    groupinfo.append([r.select("a")[0].get("href"), int(r.select(".info")[0].string.split(" ")[0])])
  print("getgroup over")
  
def WriteToFile():
  output = open("./data/groupinfo.txt.tmp", "w")
  for group in groupinfo:
    output.write(group[0] + "\t" + str(group[1]) + "\n")
  output.close()

def Write():
  mininum = 500
  output = open("./data/groupinfo.txt", "w")
  with open("./data/groupinfo.txt.tmp") as file:
    for line in file:
      info = line.strip().split("\t")
      if len(info)!=2:
        continue
      if int(info[1]) > mininum:
        output.write(info[0] + "\t" + info[1] + "\n")
  output.close()
  os.remove("./data/groupinfo.txt.tmp")


if __name__=="__main__":
  ###获取租房小组
  print("get city group start")
  cities = getcity() 
  for city in cities:
    q = geturl(city + " 租房")
    multithread(scrawler, q, city, 50)
  WriteToFile() 
  Write() 
  print("get city group over")
  
  
