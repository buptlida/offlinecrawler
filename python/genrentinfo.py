import sys
import urllib
import urllib.request
from bs4 import BeautifulSoup 
import http.cookiejar
import queue
import jieba
import threading
import time

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

def getrentinfo(url):
  global rentinfo
  print("getrent start")
  url = url + "discussion?start="
  url = "https://www.douban.com/group/beijingzufang/discussion?start="
  count = -1
  while True:
    count += 10
    url = url + str(25 * count)
    print(url)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36", "Upgrade-Insecure-Requests":1, "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Cache-Control":"max-age=0", "Host":"www.douban.com"}
    request = urllib.request.Request(url = url, headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read().decode("UTF-8")
    soup = BeautifulSoup(html, "lxml")
    result = soup.select(".olt .title")
    for r in result:
      print(r)
      break
    print("getrent over")
    break
  
def SortAndWriteToFile():
  output = open("./data/groupinfo.txt", "w")
  for group in groupinfo:
    output.write(group[0] + "\t" + str(group[1]) + "\n")
  output.close()

def putGroupUrlToQueue():
  que = queue.Queue()
  with open("./data/groupinfo.txt") as file:
    for line in file:
      info = line.strip().split("\t")
      que.put(info[0] + "/discussion?start=")
  return que

if __name__=="__main__":
  #获取各小组内租房信息
  #q = putGroupUrlToQueue()
  #multithread(scrawler, q, 50)
  getrentinfo("a")
  
  
