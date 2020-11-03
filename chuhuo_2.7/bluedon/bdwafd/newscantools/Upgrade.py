#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import os
import sys
import time
import socket
import signal
import urllib
import urllib2
import hashlib
import MySQLdb
import urlparse
import cookielib
import subprocess
import ConfigParser
from StringIO import StringIO
from lib.common import *
from plugins import json
import datetime

WAF_CONSTANT_RC = "/etc/waf_constant.rc"
WAF_SETTING_RC = "/etc/waf_setting.rc"
WAF_CONF = "/var/waf/waf.conf"

"""
在线升级错误代码：

1  config.upgrade_package_type_version_md5字段格式有误
2  数据库程序失败，导致config为空
3  有其它升级进程
4  升级包下载失败
5  系统已过质保期，如需升级，请联系供货商或厂家
6  该进程被kill掉
8  升级包MD5校验失败
16 自动升级获取最新包出错
20 Upgrade.start异常，possible？

"""

def catch(rets=None):
    def _deco(fun):
        def _func(*args,**kwargs):
            try:
                return fun(*args,**kwargs)
            except Exception,e:
                info = str(fun)+str(args)
                if kwargs:
                    info += str(kwargs)
                logging.getLogger().error("File:upgrade.py, catch:%s,%s" %(info,str(e)))
                return rets
        return _func
    return _deco    

class UpgradeApi:
    """
    /updateapi/versionlist/升级包类型/产品类型/版本/设备序列号/固件版本
    /updateapi/download/升级包类型/产品类型/版本/设备序列号
    升级包类型：build或者rule
    产品类型：NVS
    版本：3.0.03.1100
    设备序列号：sdfsdfsdfs
    固件版本：参数可选，只在是规则升级包下有用
    """

    def __init__(self,config):
        self.packageType = config['packageType']
        self.productType = config['productType']
        self.site = config['site']
        self.version = config['version'].replace('.','_')
        self.fireware = config['fireware'].replace('.','_')
        self.isProxy = int(config['httpproxy_enable'])
        self.proxySite = config['proxy_site']
        self.proxyPort = config['proxy_port']
        self.proxyUser = config['proxy_username']
        self.proxyPass = config['proxy_passwd']
        self.servicecode = config['servicecode']
        self.varifypre = "_YxLiNk_"
        self.opener = self._build_opener()

    def _build_opener(self):
        filename = "/var/log/UPGRADEPYSESSION"
        self.cj = cookielib.MozillaCookieJar(filename)
        if os.path.exists(filename):
            self.cj.load(ignore_discard=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        if self.isProxy:
            site = self.proxySite.lower()
            if site.find('http') > -1:
                parse = urlparse.urlparse(site)
                listParse = list(parse)
                if self.proxyUser != "" or self.proxyPass != "":
                    listParse[1] = "%s:%s@%s:%s" %(self.proxyUser,self.proxyPass,parse[1],self.proxyPort)
                tupleParse = tuple(listParse)
                site = urlparse.urlunparse(tupleParse)
            else:
                if self.proxyUser != "" or self.proxyPass != "":
                    site = "http://%s:%s@%s:%s" % (self.proxyUser,self.proxyPass,site,self.proxyPort)
                else:
                    site = "http://%s:%s" % (site,self.proxyPort)
            proxyHandler = urllib2.ProxyHandler({'http':site})
            opener.add_handler(proxyHandler)
        #end if
        return opener

    @catch((False,""))
    def _request(self,url,data=None,timeout=10,filedesc=False):
        '''
         data = {'email':'myemail'}
         if filedesc is True,return file descriptor,not content,because download need file-like object
        '''
        flag = False
        f = StringIO()  # in case exception,f preferably with a read() method
        socket.setdefaulttimeout(timeout)
        if data:
            data = urllib.urlencode(data)
        try:
            f = self.opener.open(url,data)
        except urllib2.HTTPError,e:
            if e.code == 401 and self._verify():
                f = self.opener.open(url,data)
            else:
                raise
        return filedesc and (True,f) or (True,f.read())
    

    @catch(False)
    def _verify(self):
        challengeUrl = "%s/updateapi/challenge/%s" %(self.site,self.servicecode)
        c= self.opener.open(challengeUrl).read()
        result = json.read(c)
        if result['success']:
            challenge = result['challenge']
            code = self.varifypre + challenge + self.servicecode
            code_md5 = hashlib.md5(code).hexdigest()
            checkUrl = "%s/updateapi/authenticate/%s" %(self.site,code_md5)
            c = self.opener.open(checkUrl).read()
            result = json.read(c)
            if result['success'] and result['authenticate']:
                self.cj.save(ignore_discard=True) #只有当认证成功才写cookie
                return True
            #end if
        #end if
        return False

    @catch(None)
    def getServerDate(self):
        url = "%s/updateapi/challenge/%s" %(self.site,self.servicecode)
        f,fp= self._request(url,filedesc=True)
        if f and fp:
            date = fp.headers.getdate('date') #(2014, 4, 22, 8, 24, 22, 0, 1, 0) or None
            if date:
                return date[:3]

    @catch(False)
    def getNewestVersion(self):
        url = "%s/updateapi/newestVersion/%s/%s/%s/%s/%s" %(self.site,self.packageType,self.productType,self.version,self.servicecode,self.fireware)
        f,c = self._request(url)
        if f:
            result = json.read(c)
            if result['success']:
                newest = result['newest']
                return (True,newest['build'],newest['issue'],newest['desc'],newest['md5'])
            else:
                return (True,'') #没有最新版本
        return False

    @catch(False)
    def send(self,sendmail):
        url = "%s/updateapi/sendstate/%s/%s/%s/%s/%s" %(self.site,self.packageType,self.productType,self.version,self.servicecode,self.fireware)
        f,c = self._request(url)
        if sendmail: sendUpgradeSuccess(self.packageType,self.version.replace('_','.'))
        return True

               
    @catch(False)
    def download(self,version,downloadDir,downloadName):
        version = version.replace('.','_')
        downloadUrl ="%s/updateapi/download/%s/%s/%s/%s/%s/%s" %(self.site,self.packageType,self.productType,version,self.servicecode,self.version,self.fireware)
        filename = downloadDir+downloadName
        f,fp= self._request(downloadUrl,filedesc=True)
        if not f:
            return False
        headers = fp.info()
        tfp = open(filename, 'wb')
        bs = 8192
        size = -1
        read = 0
        if "content-length" in headers:
            size = int(headers["Content-Length"])
        while 1:
            block = fp.read(bs)
            if not block:
                break
            read += len(block)
            tfp.write(block)
        fp.close()
        tfp.close()
        del fp
        del tfp

        if size >= 0 and read < size:
            return False
        else:
            return True
        return False


class Upgrade:
    productType = "NVS"
    updating = False
    def __init__(self,init=True):
        self.packageType = None
        self.version = None
        self.md5 = None
        self.config = None
        self.conn()
        if init:
            self.init()
            self.config = self._getConfig()

    @catch()
    def conn(self):
        self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

    @catch()
    def init(self):
        sql = "SELECT Value from config WHERE Name ='upgrade_package_type_version_md5'"
        self.cursor.execute(sql)
        self.conn.commit()
        result = self.cursor.fetchone()
        value = result['Value'].encode('utf-8').split('#')
        if len(value) == 3:
            self.packageType,self.version,self.md5 = value
        else:
            write_syslog("在线升级失败，错误代码1")
            sys.exit(-1)

    @catch()
    def update_version_md5(self,version,md5): #change 'upgrade_package_type_version_md5' record
        v = "%s#%s#%s" %(self.packageType,version,md5)
        sql ="update config set Value='%s' where Name ='upgrade_package_type_version_md5'" % v
        self.cursor.execute(sql)
        self.conn.commit()


    @catch({})
    def _getConfig(self):
        prefix = None
        config = {}
        if not self.packageType:
            return config #no packageType,so (maybe self.init failed,also you can provied packageType)
        if self.packageType == "build":
            prefix = "upgrade_build_"
            config['packageType'] = "build"
        elif self.packageType == "rule":
            prefix = "upgrade_rules_"
            config['packageType'] = "rule"
        else:
            logging.getLogger().error("File:upgrade.py, Upgrade.getConfig type error")
            return config

        config['productType'] = self.productType

        sql = "SELECT Name,Value from config WHERE substring(Name,1,14)='%s'" % prefix
        self.cursor.execute(sql)
        self.conn.commit()
        results = self.cursor.fetchall()
        for v in results:
            name = v["Name"][14:].encode("utf-8")
            value = v["Value"].encode("utf-8")
            config[name] = value
        # {u'schedule': u'01#05', u'proxy_site': u'192.168.9.1', u'site': u'http://buildupdate.yxlink.com', u'proxy_passwd': u'yxserver', u'proxy_port': u'8080', u'httpproxy_enable': u'1', u'mode': u'3', u'proxy_username': u'root'}
        cfg = ConfigParser.RawConfigParser()
        cfg.readfp(open(WAF_CONSTANT_RC))
        config['servicecode'] = cfg.get("resource", "servicecode").strip()
        cfg.readfp(open(WAF_SETTING_RC))
        build = cfg.get("version","swver").strip()
        rule = cfg.get("version","rulever").strip()
        if config['packageType'] == "build":
            config['version'] = build
            config['fireware'] = rule
        else:
            config['version'] = rule
            config['fireware'] = build
        return config

    @catch()
    def getUpgradeApi(self,packageType):
        self.packageType = packageType
        config = self._getConfig()
        return UpgradeApi(config)


    @catch(False)
    def _md5_file(self,filepath,filemd5):
        f=open(filepath,'rb')
        md5=hashlib.md5()
        while 1:
            data=f.read(8192)
            if not data:
                break
            md5.update(data)
        f.close()
        if md5.hexdigest() == filemd5:
            return True
        return False

    @catch(-1)
    def call(self,cmd):
        return subprocess.call(cmd,shell=True,close_fds=True,bufsize=-1)

    @catch("")
    def popen(self,cmd):
        return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()

    @catch(False)
    def unlink(self,filepath):
        os.remove(filepath)
        return True

    @catch(1)
    def processCount(self,process): # strict mode,if exception means exist
        cmd = "ps -ef | grep '%s' | grep -v grep | grep -v \"sh -c\"  | wc -l" % process
        result = self.popen(cmd)
        if result:
            return int(result[0]) # result[0] may be '1\n',int() work ok
        return 0

    @catch(False)
    def allprocessShutdown(self): # Upgrade.py is self,mins one
        if self.processCount("Upgrade.py") -1  or self.processCount("rules_update.py") or self.processCount("preupdate.sh"):
            return False
        return True

    @catch(False)
    def writeupgradelog(self,version,issue,desc): #自动升级记录日志
        unknown = "未知"
        upgradeType = self.packageType == "build" and "固件升级" or "规则升级"
        upgradeversion = version and version or unknown
        issue = issue and issue or unknown
        desc = desc and desc or unknown
        content = "升级类型：" + upgradeType + " 升级包版本：" + version + " 发布日期：" + issue + " 更新内容：" + desc + " 开始升级"
        sql = "insert into upgradelog (Username,Ip,Log) values ('webadmin','127.0.0.1','%s')" % content
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    @catch(False)
    def _upgrade(self,filepath):
        Upgrade.updating = True
        if self.packageType == "build":
            cmd = "cp /var/waf/preupdate.sh /var/run/preupdate.sh; /var/run/preupdate.sh " + filepath
            self.call("/usr/bin/touch /var/waf/update.state")
            self.call("/usr/bin/touch /var/log/build.state")
            time.sleep(1)
            self.call(cmd)
        else:
            if self.call("/usr/bin/python /var/waf/rules_update.py decrypt"):
                logging.getLogger().error("File:upgrade.py,Upgrade.upgrade :rules_update.py decrypt error")
            else:
                self.call("/usr/bin/touch /var/log/rules.state")
                self.call("/usr/bin/python /var/waf/rules_update.py update&")
        return True

    @catch(False)
    def in_warranty_duration(self,upgradeApi):

        def exceed(other_day,today=None):
            if today is None:
                today = datetime.date.today()
            else:
                today = datetime.date(int(today[0]),int(today[1]),int(today[2]))
            other_day = datetime.date(int(other_day[0]),int(other_day[1]),int(other_day[2]))
            if int((today - other_day).days) <= 0:
                return False
            else:
                return True

        cfg = ConfigParser.RawConfigParser()
        cfg.readfp(open(WAF_CONF))
        duration = cfg.get("warranty", "warranty_duration").strip()
        if duration == "1": #永久质保
            return True
        else:
            end_time = duration.split('/')[-1][:-1]
            end_time_list = end_time.split('-')
            print end_time_list
            if exceed(end_time_list):
                return False
            else:
                today = upgradeApi.getServerDate()
                if today and exceed(end_time_list,today):
                    return False
                else:
                    return True

    @catch(20)
    def start(self):
        if not self.config:
            return 2

        downloadDir = "/tmp/"
        name = self.packageType == "build" and "hwaf-update.dat" or "rules.dat"
        filepath = downloadDir + name

        upgradeApi=UpgradeApi(self.config)

        if self.packageType == "build" and not self.in_warranty_duration(upgradeApi):
            return 5
        
        if not self.allprocessShutdown():
            logging.getLogger().error("allprocessShutdown failed: already has process run")
            return 3

        if self.version and self.md5: # 前台升级
            if not upgradeApi.download(self.version,downloadDir,name):
                return 4
            write_syslog("升级包下载成功，版本：" + self.version) #注意不要用self.cursor,时间长会导致mysql连接超时
            if not self._md5_file(filepath,self.md5):
                self.unlink(filepath)
                return 8
            self._upgrade(filepath) #不需要出错记录，升级脚本会记录
        else:  #后台
            newest = upgradeApi.getNewestVersion()
            if newest and len(newest) == 5:
                f,version,issue,desc,md5 = newest
                if f:
                    self.update_version_md5(version,md5)
                    self.writeupgradelog(version,issue,desc)
                    if not upgradeApi.download(version,downloadDir,name):
                        return 4
                    write_syslog("升级包下载成功，版本：" + version)
                    if not self._md5_file(filepath,md5):
                        self.unlink(filepath)
                        return 8
                    self.call("/usr/bin/touch /var/log/upgrade.background")
                    self._upgrade(filepath)
                #end if
            elif len(newest) == 2:
                write_syslog("没有最新升级包")
            else:
                return 16
            #end if
        #end if
        return None

@catch()
def write_syslog(data):
    conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
    cur = conn.cursor(MySQLdb.cursors.DictCursor) 
    sql = "insert into syslog values(0, now(),'%s')" % data
    cur.execute(sql)
    conn.commit()
#end def

@catch()
def _getUpgradeApi(upgradeType):
    upgrade = Upgrade(init=False)
    if upgradeType == "build":
        return upgrade.getUpgradeApi("build")
    elif upgradeType == "rule":
        return upgrade.getUpgradeApi("rule")
    else:
        logging.getLogger().error("File:upgrade.py,_getUpgradeApi: upgradeType error")
        return None

@catch()
def sendstate(upgradeType):
    path = "/var/log/upgrade.background"
    sendmail = os.path.exists(path)
    os.remove(path)
    api = _getUpgradeApi(upgradeType)
    if api:api.send(sendmail)

def sighandler(signum, frame):
    if signum == signal.SIGTERM:
        if not Upgrade.updating: #mean,cancel download
            write_syslog("在线升级失败，错误代码6")
    sys.exit(-1)

def main():
    try:
        write_syslog("开始在线升级，请稍等")
        upgrade = Upgrade()
        ret = upgrade.start()
        if ret:
            write_syslog("在线升级失败，错误代码"+str(ret))
    except Exception,e:
        logging.getLogger().error("File:upgrade.py,main:" + str(e))

def test():
   #  print '-- start --'
   #api = _getUpgradeApi("build")
   #  print api.__dict__
   #  print api.getNewestVersion()
   # # print api.download('3.0.03.3600','/tmp/','nvs.dat')
   #  print api.getNewestVersion()
   #sendstate("build")
   #upgrade = Upgrade()
   #print upgrade.in_warranty_duration()
   main()
    
   
if __name__ == "__main__":
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    signal.signal(signal.SIGTERM,sighandler)
    try:
        if len(sys.argv) == 1:
            main()
        elif len(sys.argv) == 2 and sys.argv[1] == "test":
            test()
        else:
            print "argv error"
    except Exception,e:
        logging.getLogger().error("File:upgrade.py, __main__:" + str(e))
    #end try
#end if