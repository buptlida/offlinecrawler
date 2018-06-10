import urllib
import urllib.request
import html.parser
from socket import error as SocketError
from http.cookiejar import CookieJar

try:
    url = "https://www.douban.com/group/beijingzufang/discussion?start=225"
    req=urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; G518Rco3Yp0uLV40Lcc9hAzC1BOROTJADjicLjOmlr4=) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Accept-Encoding': 'gzip, deflate, sdch','Accept-Language': 'en-US,en;q=0.8','Connection': 'keep-alive'})
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    response = opener.open(req)
    raw_response = response.read().decode('utf8', errors='ignore')
    print(raw_response)
    response.close()
except urllib.request.HTTPError as inst:
    output = format(inst)
    print(output)
