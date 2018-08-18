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
      print(data)
      time.sleep(4)

def GetInfo(title, content, info):
  print(title)
  ##判断主次卧
  r1 = '[次卧]'
  print(bool(re.search(r1, title)))
 
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
  
  
