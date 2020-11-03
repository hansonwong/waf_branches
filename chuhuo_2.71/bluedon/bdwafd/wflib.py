#!/usr/bin/env python
#-*-coding:utf-8-*-
 
import urllib
import urllib2
import cookielib
import re
import sys
import cPickle
import time
import os
from MySQL import MySQL
from config import config

try:
    import cPickle as pickle
except:
    import pickle

def savedata(obj):
    with open("wflibdata.txt", "w+") as fp:
        pickle.dump(obj, fp)

def getdata():
    if os.path.exists("wflibdata.txt"):
        with open("wflibdata.txt", "rb") as fp:
            try:
                return pickle.load(fp)
            except EOFError:
                return False
    else:
        return False


class WfLib():
    def __init__(self):
        self.opener = None
        self.host = "https://172.16.2.233:8080/"
        self.posturl = self.hosturl = "%sindex.php"%(self.host)
        self.postData = {
                    "username": "admin",
                    "password": "admin"
                    }
        self.sessionId=None
        self.timestamp = int(time.time())


    '''
    @parameters:
    hosturl: 登录的主页面
    posturl: post数据接收和处理的页面（我们要向这个页面发送我们构造的Post数据）
    data: post发送的数据
    '''
    def login(self, check = False):
        if not check:
            db = MySQL(config['db'])
            db.query("SELECT * FROM t_webguard")
            result = db.fetchOneRow()
            self.host = result['url']+'/'
            self.postData['username'] = result['username']
            self.postData['password'] = result['password']
            db.close()
        #设置一个cookie处理器，它负责从服务器下载cookie到本地，并且在发送请求时带上本地的cookie
        #cj = cookielib.LWPCookieJar()
        #cookie_support = urllib2.HTTPCookieProcessor(cj)
        #self.opener = opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        #urllib2.install_opener(opener)

        #打开登录主页面（他的目的是从页面下载cookie，这样我们在再送post数据时就有cookie了，否则发送不成功）
        h = urllib2.urlopen(self.host)

        #构造header，一般header至少要包含一下两项。这两项是从抓到的包里分析得出的。
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        #需要给Post数据编码
        postData = urllib.urlencode(self.postData)

        #通过urllib2提供的request方法来向指定Url发送我们构造的数据，并完成登录过程
        request = urllib2.Request(self.posturl, postData, headers)
        res = urllib2.urlopen(request).read()
        self.sessionId = res.split("href='")[1].split("'<")[0].split("?")[1].split("=")[1]
        return res


    def check(self, url=None, check=False):
        if int(time.time())-self.timestamp > 600:
            self.sessionId = None
        try:
            if not self.sessionId:
                self.login(check)
            if not url:
                print {'msg': 'success', 'code':1}
                return
            
            if url.find("8080") == -1:
                url = "%s/%s"%(self.host, url)

            if url.find("sessionid") == -1:
                if url.find("?") != -1:
                    url += "&sessionid=%s"%self.sessionId
                else:
                    url += "?sessionid=%s"%self.sessionId
            return url        
        except Exception, e:
            print {"msg":'error', 'code':-1}


    def get(self, url, data=None):
        url = self.check(url)
        cs = ""
        if data:
            for keys, value in data.items():
                cs += "%s=%s&"%(keys, value)
            cs = cs[:-1]    
            if url.find("?") != -1:
                url = "%s&%s"%(url, cs)
            else:
                url = "%s?%s"%(url, cs)
        #urllib2.install_opener(self.opener)
        res =urllib2.urlopen(url).read()  
        return res

    def post(self, posturl, data):
        posturl = self.check(posturl)
        #urllib2.install_opener(self.opener)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        postData = urllib.urlencode(data)
        request = urllib2.Request(posturl, postData, headers)
        res = urllib2.urlopen(request).read()
        return res

    def visit(self):
        argvs = sys.argv
        method = argvs[1].lower()
        url = argvs[2]
        data = None
        if len(argvs) < 3:
            print "Parameter must be greater than 3"
        if len(argvs) > 3:
            data = eval(argvs[3])
        if method == "get":
            print self.get(url, data)
        elif method == 'check':
            self.sessionId = None
            self.host = data['host']+'/'
            self.postData = {"username": data["username"],
                    "password": data['password']}
            self.check(check=True)
            return
        else:
            print self.post(url, data)


def main():
    obj = getdata()
    if not obj:
        obj = WfLib()
    obj.visit()
    savedata(obj)

if __name__ == "__main__":
    main()
