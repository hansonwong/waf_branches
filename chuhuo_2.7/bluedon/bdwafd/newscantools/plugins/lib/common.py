#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import MySQLdb
import ConfigParser
import re
import logging
import logging.handlers
import os
import socket
import urllib2
import subprocess
import httplib
import httplib2
import urlparse
import hashlib
import threading
import time
import base64
import ssl
import datetime
import sys
import errno
import tldextract


sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)
WAF_CONFIG   = sys_path("waf.conf")

VULDBDIR     = "/var/vuls_db/"
FLAG         = "#d9Fa0j#"
FILE_PREFIX  = "vuldb_"
LOG_DIR      = "/var/www/tmp/"
CRACK_DIC    = "/var/www/yx_python_link/"
cfg          = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
host         = cfg.get("mysql","db_ip").replace('"','')
user         = cfg.get("mysql","db_user").replace('"','')
passwd       = cfg.get("mysql","db_passwd").replace('"','')
database     = "security"
http_status_dict = {'100':'Continue','101':'Switching Protocols','200':'OK','201':'Created','202':'Accepted','203':'Non-Authoritative Information','204':'No Content','205':'Reset Content','206':'Partial Content','300':'Multiple Choices','301':'Moved Permanently','302':'Found','303':'See Other','304':'Not Modified','305':'Use Proxy','307':'Temporary Redirect','400':'Bad Request','401':'Unauthorized','403':'Forbidden','404':'Not Found','405':'Method Not Allowed','406':'Not Acceptable','407':'Proxy Authentication Required','408':'Request Timeout','409':'Conflict','410':'Gone','411':'Length Required','412':'Precondition Failed','413':'Request Entity Too Large','414':'Request URI Too Long','415':'Unsupported Media Type','416':'Requested Range Not Satisfiable','417':'Expectation Failed','500':'Internal Server Error','501':'Not Implemented','502':'Bad Gateway','503':'Service Unavailable','504':'Gateway Timeout','505':'HTTP Version Not Supported'}
not_run_type_list = ['rar','zip','tar','js','css','db','xml','txt']

connect_status = ['Connection reset by peer','Broken pipe']

FACILITY = {
    'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
    'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
    'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
    'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
    'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
}

LEVEL = {
    'emerg': 0, 'alert':1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}
DEVID = "error_serial_num"
syslog_servers = []
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
    conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    sql = "select * from license where Name = 'serial_num'"
    cur.execute(sql)
    ret = cur.fetchone()
    if ret and len(ret["Value"]) > 1:
        DEVID = ret["Value"]
    #end if
    sql = "select * from config where Name = 'syslog_server1'"
    cur.execute(sql)
    ret = cur.fetchone()
    if ret and len(ret["Value"]) > 1:
        tmpserver = ret["Value"]
        if len(tmpserver.split("|")) == 2:
            syslog_servers.append(tmpserver)
        #end if
    #end if
    sql = "select * from config where Name = 'syslog_server2'"
    cur.execute(sql)
    ret = cur.fetchone()
    if ret and len(ret["Value"]) > 1:
        tmpserver = ret["Value"]
        if len(tmpserver.split("|")) == 2:
            syslog_servers.append(tmpserver)
        #end if
    #end if
    sql = "select * from config where Name = 'syslog_server3'"
    cur.execute(sql)
    ret = cur.fetchone()
    if ret and len(ret["Value"]) > 1:
        tmpserver = ret["Value"]
        if len(tmpserver.split("|")) == 2:
            syslog_servers.append(tmpserver)
        #end if
    #end if
    conn.close()
except Exception,e:
    print e
#end
VUL_SYSLOG_HEADER = "NVSCAN_VULSCAN:%s#NVSCANSPLIT#" % (DEVID)

def checkIpv6(ipv6_addr):
    try:
        addr= socket.inet_pton(socket.AF_INET6, ipv6_addr)
    except socket.error:
        return False
    else:
        return True



def syslog_raw(message, level=LEVEL['notice'], facility=FACILITY['daemon'],host='127.0.0.1', port=514):
    try:
        sock = ''
        if checkIpv6(host):
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = '<%d>%s' % (level + facility*8, message)
        sock.sendto(data, (host, port))
        sock.close()
    except Exception,e:
        logging.getLogger().error("syslog_raw Exception:" + str(e))
    #end try
#end def

def syslog(message):
    try:
        for s in syslog_servers:
            tmpip = s.split("|")[0]
            tmpport = int(s.split("|")[1])
            syslog_raw(message, host = tmpip, port = tmpport)
        #end for
    except Exception,e:
        logging.getLogger().error("syslog Exception:" + str(e))
    #end try
#end def


def syslog_web_vul(task_id, task_name, ip, web_vul_name, detail, url, domain, factor):
    try:
        if factor == "HIGH":
            factor = "高风险"
        elif factor == "MED":
            factor = "中风险"
        elif factor == "LOW":
            factor = "低风险"
        else:
            factor = "信息"
        #endif
        data = VUL_SYSLOG_HEADER + \
             (str(task_id)) + "#NVSCANSPLIT#" + \
             (task_name.decode("utf8")) + "#NVSCANSPLIT#" + \
             ("2") + "#NVSCANSPLIT#" + \
             (ip) + "#NVSCANSPLIT#" + \
             (web_vul_name.decode("utf8")) + "#NVSCANSPLIT#" + \
             (detail.decode("utf8")) + "#NVSCANSPLIT#" + \
             (url.decode("utf8")) + "#NVSCANSPLIT#" + \
             (domain.decode("utf8")) + "#NVSCANSPLIT#" + \
             (factor.decode("utf8"))
        #print data
        syslog(data.encode("utf8"))
    except Exception,e:
        logging.getLogger().error("syslog_web_vul Exception:" + str(e))
    #end try
#end def


def init_log(console_level, file_level, logfile):
    formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
    logging.getLogger().setLevel(0)
    console_log = logging.StreamHandler()
    console_log.setLevel(console_level)
    console_log.setFormatter(formatter)
    file_log = logging.handlers.RotatingFileHandler(logfile,maxBytes=1024*1024,backupCount=2)
    file_log.setLevel(file_level)
    file_log.setFormatter(formatter)
    logging.getLogger().addHandler(file_log)
    logging.getLogger().addHandler(console_log)
#end def

def checkUrlType(url):
    try:
        filename = url.split('/')[-1].split('.')
        type = ""
        if len(filename) > 1:
            type = filename[1]
        #end if
        if type != "":
            if type in not_run_type_list:
                return False
        #end if

        return True
    except Exception,e:
        logging.getLogger().error("File:common.py, function checkUrlType:" + str(e))
        return True
    #end try
#end def

def write_log_en(conn,cursor,task_id,list, task_name, asset_scan_id):
    try:
        if conn != '' and cursor != '' and list and len(list) > 0:
            for item in list:
                try:
                    sql = ""
                    if asset_scan_id > 0:
                        sql = "select count(id) as c from scan_result_" + str(task_id) + "_en where `url`=%s and `vul_id`=%s and `domain_id`=%s and `level`=%s and `detail`=%s and `asset_scan_id`='"+str(asset_scan_id)+"'"
                    else:
                        sql = "select count(id) as c from scan_result_" + str(task_id) + "_en where `url`=%s and `vul_id`=%s and `domain_id`=%s and `level`=%s and `detail`=%s"
                    #end if
                    cursor.execute(sql,(item['url'],item['vul_id'],item['domain_id'],item['level'],item['detail']))
                    conn.commit()
                    res = cursor.fetchone()
                    if res and len(res) > 0 and res['c'] > 0:
                        continue
                    #end if

                    sql = "SELECT vul_name FROM web_vul_list_en WHERE vul_id=%s"
                    cursor.execute(sql,item['vul_id'])
                    conn.commit()
                    res = cursor.fetchone()
                    vul_type = ""
                    if res and len(res) > 0:
                        vul_type = res['vul_name']
                    else:
                        continue
                    #end if

                    logging.getLogger().error("write_log_en+task_id="+str(task_id))
                    logging.getLogger().error("write_log_en+domain_id="+item['domain_id'])
                    logging.getLogger().error("write_log_en+url="+item['url'])
                    logging.getLogger().error("write_log_en+ip="+item['ip'])
                    logging.getLogger().error("write_log_en+vul_type="+item['vul_type'])
                    logging.getLogger().error("write_log_en+domain="+item['domain'])
                    logging.getLogger().error("write_log_en+level="+item['level'])
                    logging.getLogger().error("write_log_en+detail="+item['detail'])
                    logging.getLogger().error("write_log_en+vul_id="+item['vul_id'])
                    logging.getLogger().error("write_log_en+request="+item['request'])
                    logging.getLogger().error("write_log_en+response="+item['response'])
                    logging.getLogger().error("write_log_en+output="+item['output'])
                    sql = "insert into scan_result_" + str(task_id) + "_en (`domain_id`,`url`,`ip`,`vul_type`,`domain`,`level`,`detail`,`vul_id`,`request`,`response`,`output`,`asset_scan_id`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql,(item['domain_id'],item['url'],item['ip'],vul_type,item['domain'],item['level'],item['detail'],item['vul_id'],item['request'],item['response'],item['output'],asset_scan_id))
                    conn.commit()

                    #syslog_web_vul(str(task_id), task_name, item['ip'], item['vul_type'], item['detail'], item['url'], item['domain'], item['level'])
                except Exception,e1:
                    print '''------------------------------------------------------------
第二层错误: %s
------------------------------------------------------------'''%e1
                    logging.getLogger().error("File:common.py, function write_log_en:" + str(e1))
                #end if
            #end for
        #end if
    except Exception,e:
        print '''------------------------------------------------------------
第一层错误: %s
------------------------------------------------------------'''%e
        logging.getLogger().error("File:common.py, function write_log_en:" + str(e))
    #end try
#end def

def write_log(conn,cursor,task_id,list, task_name, asset_scan_id):
    try:
        if conn != '' and cursor != '' and list and len(list) > 0:
            for item in list:
                try:
                    sql = ""
                    if asset_scan_id > 0:
                        sql = "select count(id) as c from scan_result_" + str(task_id) + " where `url`=%s and `vul_id`=%s and `domain_id`=%s and `level`=%s and `detail`=%s and `asset_scan_id`='"+str(asset_scan_id)+"'"
                    else:
                        sql = "select count(id) as c from scan_result_" + str(task_id) + " where `url`=%s and `vul_id`=%s and `domain_id`=%s and `level`=%s and `detail`=%s"
                    #end if
                    cursor.execute(sql,(item['url'],item['vul_id'],item['domain_id'],item['level'],item['detail']))
                    conn.commit()
                    res = cursor.fetchone()
                    if res and len(res) > 0 and res['c'] > 0:
                        continue
                    #end if
                    logging.getLogger().error("write_log+task_id="+str(task_id))
                    logging.getLogger().error("write_log+domain_id="+item['domain_id'])
                    logging.getLogger().error("write_log+url="+item['url'])
                    logging.getLogger().error("write_log+ip="+item['ip'])
                    logging.getLogger().error("write_log+vul_type="+item['vul_type'])
                    logging.getLogger().error("write_log+domain="+item['domain'])
                    logging.getLogger().error("write_log+level="+item['level'])
                    logging.getLogger().error("write_log+detail="+item['detail'])
                    logging.getLogger().error("write_log+vul_id="+item['vul_id'])
                    logging.getLogger().error("write_log+request="+item['request'])
                    logging.getLogger().error("write_log+response="+item['response'])
                    logging.getLogger().error("write_log+output="+item['output'])
                    sql = "insert into scan_result_" + str(task_id) + " (`domain_id`,`url`,`ip`,`vul_type`,`domain`,`level`,`detail`,`vul_id`,`request`,`response`,`output`,`asset_scan_id`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql,(item['domain_id'],item['url'],item['ip'],item['vul_type'],item['domain'],item['level'],item['detail'],item['vul_id'],item['request'],item['response'],item['output'],asset_scan_id))
                    conn.commit()

                    syslog_web_vul(str(task_id), task_name, item['ip'], item['vul_type'], item['detail'], item['url'], item['domain'], item['level'])
                    write_log_en(conn,cursor,task_id,list, task_name, asset_scan_id)
                except Exception,e1:
                    logging.getLogger().error("File:common.py, function write_log:" + str(e1))
                #end if
            #end for
        #end if
    except Exception,e:
        logging.getLogger().error("File:common.py, function write_log:" + str(e))
    #end try
#end def







def requestUrl(http,url,task_id,domain_id):
    def request(url):
        res = {}
        content = ''
        try:
            headers = {"Accept-Encoding":"identity"}
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            a = url.find("[")
            b = url.find("]")
            if a >=0 and b >=0:
                host_domain = url[a+1:b]
                if checkIpv6(host_domain):
                    headers["Host"] = '[' + host_domain + ']'
            res, content = http.request(url, "GET", None, headers)
        except socket.timeout,e:
            res['status'] = '404'
            res['content-location'] = url
        except Exception,e:
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            header = response.info()
            location = response.geturl()
            content = response.read()
            response.close()
            for key in header:
                res[key] = header[key]
            #end for
            res['status'] = '200'
            res['content-location'] = location

        return res,content
        #end try
    #end def
      
    try:
        if not url or url.lower().find('http') == -1:
            return {'status':'404'},""
        sep = "####################"
        #download_dir = "/var/webs/task_id%sdomain_id%s/" % (str(task_id),str(domain_id))
        download_dir = "/var/webs/task%s/" % (str(task_id))
        res = {}
        content = ""
        filename = hashlib.sha1(url).hexdigest()
        filename = "%s#%s#" % (filename,str(domain_id))
        if os.path.isfile(download_dir + filename):
            #print "+++++++++++++++++++++++++++++++++++++++++++++++++++++   read from file , url : ",url
            lines = []
            try:
                f = file(download_dir + filename, "r+")
                lines = f.readlines()
                f.close()
                flag = True
                for row in lines:
                    if row.find(sep) >= 0:
                        flag = False
                        continue
                    #end if
                    if flag:
                        if row.find(':') > 0:
                            row = row.replace("\n","")
                            temp = row.split(':')
                            res[temp[0]] = ':'.join(temp[1:])
                        #end if
                    else:
                        content += row
                    #end if
                #end for
            except IOError:
                res,content = request(url)
        else:
            #print "---------------------------------------------------- file not exists , url : ",url
            res,content = request(url)

            
            '''
            lines = []
            for k in res:
                lines.append(k+':'+res[k] + "\n")
            #end for
            lines.append(sep+"\n")
            lines.append(content)
            f = file(download_dir + filename,'w+')
            f.writelines(lines)
            f.close()
            if res.has_key('content-location') and res['content-location'] != url:
                filename = hashlib.sha1(res['content-location']).hexdigest()
                f = file(download_dir + filename,'w+')
                f.writelines(lines)
                f.close()
            #end if
            lines = []
            '''
        #end if
        return res,content
    except socket.timeout,e:
        logging.getLogger().debug("requestUrl Exception(common):" + str(e) + " ,url:" + url)
    except Exception,e:
        logging.getLogger().error("requestUrl Exception(common):" + str(e) + " ,url:" + url)
    #end try
    return {'status':'404','content-location':url},""
#end def

def changeParams(params):
    list = []
    try:
        params = params.split('&')
        count = len(params)
        if count == 0:
            list.append(params[0])
        else:
            for i in range(len(params)):
                temp = params[0]
                params = params[1:]
                params.append(temp)
                list.append('&'.join(params))
            #end for
        #end if
        return list
    except Exception,e:
        print "changeParams Exception",str(e)
        return list
    #end try
#end def

def getRequest(url,method='GET',headers={},body=""):
    try:
        parse = urlparse.urlparse(url)
        scheme = parse[0]
        domain = parse[1]
        if checkIpv6(domain):
            doamin = '[' + domain + ']'
        path = url.replace("%s://%s" % (scheme,domain),"")

        '''
        path = parse[2]
        if url.find(";")>=0:
            path="%s;%s"%(parse[2],parse[3])
        if parse[4] != "":
            path = "%s?%s" % (path,parse[4])
        #end if
        '''
        list = []
        if path == "":
            path = "/"
        #end if
        list.append("%s %s  HTTP/1.1" % (method,path))

        if len(headers.keys()) > 0:
            for k in headers:
                list.append("%s: %s" % (k,headers[k]))
            #end for
        else:
            list.append("Host: %s" % (domain))
            list.append("Connection: Keep-alive")
            list.append("Accept: text/plain")
            list.append("User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5")
        #end if
        if body != "":
            list.append("Content: %s" % (body))
        #end if
        return "\n".join(list)
    except Exception,e:
        logging.getLogger().error("File:common.py, getRequest function:" + str(e) + ",url:" + str(url))
        return ''
#end def






def postRequest(url,method='POST',headers={},data="",body=""):
    try:
        parse = urlparse.urlparse(url)
        scheme = parse[0]
        domain = parse[1]
        path = url.replace("%s://%s" % (scheme,domain),"")

        '''
        path = parse[2]
        if url.find("product-gnotify")>=0:
            path="/?product-gnotify"
        if url.find("asp;")>=0:
            path="%s;%s"%(parse[2],parse[3])
        if parse[4] != "":
            path = "%s?%s" % (path,parse[4])
        #end if
        '''
        list = []
        list.append("%s %s  HTTP/1.1" % (method,path))
#
        if len(headers.keys()) > 0:
            for k in headers:
                list.append("%s: %s" % (k,headers[k]))
            #end for
        else:
            list.append("Host: %s" % (domain))
            list.append("Connection: Keep-alive")
            list.append("Accept: text/plain")
            list.append("User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5")
        #end if
        if data!="":
            list.append("")
            list.append(data)
        if body != "":
            list.append("Content: %s" % (body))
        #end if
        return "\n".join(list)
    except Exception,e:
        logging.getLogger().error("File:common.py, getRequest function:" + str(e) + ",url:" + str(url))
        return ''
    #end try
#end def
















def getResponse(res,content=''):
    try:
        list = []
        if res and len(res.keys()) > 0:
            list.append("HTTP/1.1 %s %s" % (res['status'],http_status_dict[res['status']]))
            for k in res:
                if k != 'status':
                    list.append("%s:%s" % (k,res[k]))
                #end if
            #end for
        #end if
        if content != "":
            if res and len(res.keys() > 0):
                list.append("")
            #end if
            list.append(content)
        #end if
        return "\n".join(list)
    except Exception,e:
        logging.getLogger().error("File:common.py, getResponse function:" + str(e))
        return ''
    #end try
#end def

def getGetRequest(url):
    try:
        parse = urlparse.urlparse(url)
        domain = parse[1]

        path = parse[2]
        if parse[4] != "":
            path = "%s?%s" % (path,parse[4])
        #end if
        list = []
        list.append("GET %s HTTP/1.1" % (path))
        list.append("Host: %s" % (domain))
        list.append("Connection: Keep-alive")
        list.append("Accept: text/plain")
        list.append("User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5")
        return "\n".join(list)
    except Exception,e:
        logging.getLogger().error("File:common.py, getGetRequest function:" + str(e) + ",url:" + str(url))
        return ''
    #end try
#end def

def getGetResponse(http,url,task_id,domain_id):
    try:
        list = []
        res, content = requestUrl(http,url,task_id,domain_id)
        if len(res.keys()) > 0:
            list.append("HTTP/1.1 %s %s" % (res['status'],http_status_dict[res['status']]))
            for k in res:
                if k != 'status':
                    list.append("%s:%s" % (k,res[k]))
                #end if
            #end for
        #end if
        return "\n".join(list)
    except Exception, e:
        logging.getLogger().error("File:common.py, getGetResponse function:" + str(e) + ",task id:" + task_id + ", domain id:" + domain_id + ",url:" + url)
        return ''
    #end try
#end def


def vulscan_popen(cmd):
    try:
        logging.getLogger().debug(cmd)
        return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()
    except Exception,e:
        logging.getLogger().error("vulscan_popen Exception(common):" + str(e) + "," + cmd)
        return ""
    #end try
#end def



def XssGetKeyWord(content,keyword):
    try:
        if content.find(keyword) >= 0:
            lines = content.replace('\r\n','\n').split('\n')
            for line in lines:
                #test <title>
                match = re.findall(r"<(\s*?)title(\s*?)>(.+?)<(\s*?)/(\s*?)title(\s*?)>",line,re.I)
                #print match
                for row in match:
                    if row[2].find(keyword) >= 0:
                        return True,"</title>%s" % (keyword)
                    #end if
                 #end for

                #test <textarea>
                match = re.findall(r"<(\s*?)textarea(.*?)>(.+?)<(\s*?)/(\s*?)textarea(\s*?)>",line,re.I)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        return True,"</textarea>%s" % (keyword)
                #end for

                #test input
                match = re.findall(r"<(\s*?)input(.+?)value=(.+?)/(\s*?)>",line,re.I)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        temp = row[2].strip()
                        if temp[0] == "'":
                            return True,"'/>%s" % (keyword)
                        elif temp[0] == "\"":
                            return True,"\"/>%s" % (keyword)
                        else:
                            return True,"/>%s" % (keyword)
                        #end if
                    #end if
                #end for

                #test input
                match = re.findall(r"<(\s*)input(.+?)value(\s*)=(\s*)(\"|'|\s*)(.+?)\5(\s*)>",line,re.I)
                for row in match:
                    if row[5].find(keyword) >= 0:
                        temp = row[5].strip()
                        if row[4] == "'":
                            return True,"'>%s" % (keyword)
                        elif row[4] == "\"":
                            return True,"\">%s" % (keyword)
                        else:
                            return True,">%s" % (keyword)
                        #end if
                    #end if
                #end for

                #test action and href
                match = re.findall(r"(action|href)(\s*)=(\s*)(\"|')(.+?)\4",line,re.I)
                for row in match:
                    if row[4].find(keyword) >= 0:
                        return True,"%s>%s" % (row[3],keyword)
                    #end if
                #end for
            #end for
            #test <script>
            match = re.findall(r"<(\s*?)script(.*?)>(.+?)<(\s*?)/(\s*?)script(\s*?)>",content,re.I|re.DOTALL)
            for row in match:
                if row[2].find("<script>") >= 0:
                    return True,"</script>%s" % (keyword)
                #end if
            #end for

            return True,keyword
        else:
            return False,""
        #end if
    except Exception,e:
        print "XssGetKeyWord exception : ",str(e)
        return False,""
    #end try
#end def

def LinkGetKeyWord(content,keyword):
    try:
        if content.find(keyword) >= 0:
            lines = content.replace('\r\n','\n').split('\n')
            for line in lines:
                #test <title>
                match = re.findall(r"<(\s*)title(\s*)>(.+?)<(\s*)/(\s*)title(\s*)>",line,re.I)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        return True,"</title><iframe src=http://www.baidu.com></iframe>"
                    #end if
                #end for

                #test <textarea>
                match = re.findall(r"<(\s*)textarea(.*?)>(.+?)<(\s*)/(\s*)textarea(\s*)>",line,re.I)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        return True,"</textarea><iframe src=http://www.baidu.com></iframe>"
                #end for

                #test input
                match = re.findall(r"<(\s*)input(.+?)value=(.+?)/(\s*)>",line,re.I)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        temp = row[2].strip()
                        if temp[0] == "'":
                            return True,"'/><iframe src=http://www.baidu.com></iframe>"
                        elif temp[0] == "\"":
                            return True,"\"/><iframe src=http://www.baidu.com></iframe>"
                        else:
                            return True,"/><iframe src=http://www.baidu.com></iframe>"
                        #end if
                    #end if
                #end for

                #test input
                match = re.findall(r"<(\s*)input(.+?)value(\s*)=(\s*)(\"|'|\s*)(.+?)\5(\s*)>",line,re.I)
                for row in match:
                    if row[5].find(keyword) >= 0:
                        temp = row[5].strip()
                        if row[4] == "'":
                            return True,"'><iframe src=http://www.baidu.com></iframe>"
                        elif row[4] == "\"":
                            return True,"\"><iframe src=http://www.baidu.com></iframe>"
                        else:
                            return True,"><iframe src=http://www.baidu.com></iframe>"
                        #end if
                    #end if
                #end for

                #test action and href
                match = re.findall(r"(action|href)(\s*)=(\s*)(\"|')(.+?)\4",line,re.I)
                for row in match:
                    if row[4].find(keyword) >= 0:
                        return True,"%s><iframe src=http://www.baidu.com></iframe>" % (row[3])
                    #end if
                #end for

                #test <script>
                match = re.findall(r"<(\s*)script(.*?)>(.+?)<(\s*)/(\s*)script(\s*)>",line,re.I)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        return True,"</script><iframe src=http://www.baidu.com></iframe>"
                    #end if
                #end for
            #end for

            return True,"<iframe src=http://www.baidu.com></iframe>"
        else:
            return False,""
        #end if
    except Exception,e:
        print "LinkGetKeyWord exception : ",str(e)
        return False,""
    #end try
#end def

def LinkGetKeyWordNoSrc(content,keyword):
    try:
        if content.find(keyword) >= 0:
            lines = content.replace('\r\n','\n').split('\n')
            for line in lines:
                #test <title>
                match = re.findall(r"<(\s*)title(\s*)>(.+?)<(\s*)/(\s*)title(\s*)>",line,re.I)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        return True,"</title><iframe></iframe>"
                    #end if
                #end for

                #test <textarea>
                match = re.findall(r"<(\s*)textarea(.*?)>(.+?)<(\s*)/(\s*)textarea(\s*)>",line,re.I)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        return True,"</textarea><iframe></iframe>"
                #end for

                #test input
                match = re.findall(r"<(\s*)input(.+?)value=(.+?)/(\s*)>",line,re.I)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        temp = row[2].strip()
                        if temp[0] == "'":
                            return True,"'/><iframe></iframe>"
                        elif temp[0] == "\"":
                            return True,"\"/><iframe></iframe>"
                        else:
                            return True,"/><iframe></iframe>"
                        #end if
                    #end if
                #end for

                #test input
                match = re.findall(r"<(\s*)input(.+?)value(\s*)=(\s*)(\"|'|\s*)(.+?)\5(\s*)>",line,re.I)
                for row in match:
                    if row[5].find(keyword) >= 0:
                        temp = row[5].strip()
                        if row[4] == "'":
                            return True,"'><iframe></iframe>"
                        elif row[4] == "\"":
                            return True,"\"><iframe></iframe>"
                        else:
                            return True,"><iframe></iframe>"
                        #end if
                    #end if
                #end for

                #test action and href
                match = re.findall(r"(action|href)(\s*)=(\s*)(\"|')(.+?)\4",line,re.I)
                for row in match:
                    if row[4].find(keyword) >= 0:
                        return True,"%s><iframe></iframe>" % (row[3])
                    #end if
                #end for
            #end for
            
            #test <script>
            if content.find("script") > 0:
                match = re.findall(r"<(\s*)script(.*?)>(.+?)<(\s*)/(\s*)script(\s*)>",content,re.I|re.DOTALL)
                for row in match:
                    if row[2].find(keyword) >= 0:
                        return True,"</script><iframe></iframe>"
                    #end if
                #end for
            #end if

            return True,"<iframe></iframe>"
        else:
            return False,""
        #end if
    except Exception,e:
        print "LinkGetKeyWordNoSrc exception : ",str(e)
        return False,""
    #end try
#end def

def getRecord(ob,url,level,detail,request="",response="",output=""):
    return {'domain_id':ob['domain_id'],'url':url,'ip':ob['ip'],'vul_type':ob['vul_type'],'domain':ob['domain'],'level':level,'vul_id':ob['vul_id'],'request':request,'response':response,'detail':detail,'output':output}
#end def


    #rules:
            #    vul_id:漏洞ID
            #    vul_name:漏洞名称
            #    level:风险等级
            #    url:追加的URL
            #    method:请求类型
            #    response:返回值
            #    response_type:返回类型

def getRecord_cgidb(rule_obj,ob,url,level,detail,request="",response="",output=""):
    return {'domain_id':ob['domain_id'],'url':url,'ip':ob['ip'],'vul_type':rule_obj['vul_name'],'domain':ob['domain'],'level':level,'vul_id':rule_obj['vul_id'],'request':request,'response':response,'detail':detail,'output':output}
#end def


def httpRequest(url,method,headers,body,timeout,enable_forward):
    http = httplib2.Http()
    if enable_forward:
        http.follow_redirects = True
    else:
        http.follow_redirects = False
    #end if
    socket.setdefaulttimeout(timeout)
    #response, content = http.request(url,method,headers=headers,body=body)
    response, content = yx_httplib2_request(http,url,method,headers=headers,body=body)
    returnDict = dict()
    #print response
    #print content
    return returnDict
#end def

class request_exception_counter(object):

    def __init__(self, max_err):
        self.mutex = threading.Lock()

        self.timeout_err  = 0
        self.other_err    = 0
        self.success      = 0

        self.max_err      = max_err
        self.count        = 0

        self.now_vul_id   = 0
        self.domain       = "unknown"

        self.init_time    = time.time()
    #end def

    def log_output(self):
        if (self.timeout_err + self.other_err + self.success) % 50 == 0:
            logging.getLogger().warn("domain:%s, vul_id:%d, timeout:%d, other:%d, success:%d, count:%d, time:%ds" \
                    % (self.domain, self.now_vul_id, self.timeout_err, self.other_err, self.success,  self.count, time.time() - self.init_time))
        #end if

    def add_timeout_err(self):
        self.mutex.acquire()
        self.timeout_err = self.timeout_err + 1
        self.count = self.count + 1

        self.log_output()
        self.mutex.release()
    #end def

    def add_other_err(self):
        self.mutex.acquire()
        self.other_err = self.other_err + 1
        self.count = self.count + 1

        self.log_output()
        self.mutex.release()
    #end def

    def add_success(self):
        self.mutex.acquire()
        self.success = self.success + 1
        if self.count > 0:
            self.count = self.count - 1
        #end if

        self.log_output()
        self.mutex.release()
    #end def

    def dump_info(self):
        return str("timeout:%d, other:%d, success:%d, count:%d, time:%ds" \
                    % (self.timeout_err, self.other_err, self.success,  self.count, time.time() - self.init_time))
    #end def

    def err_out(self):
        ret = False
        self.mutex.acquire()

        if self.count >= self.max_err:
            ret = True
        #end if
        self.mutex.release()

        return ret
    #end def

    def get_total(self):
        self.mutex.acquire()
        ret = self.timeout_err + self.other_err + self.success
        self.mutex.release()

        return ret
    #end def

    def get_err_count(self):
        self.mutex.acquire()
        ret = (self.timeout_err + self.other_err) - self.success
        self.mutex.release()

        return ret
    #end def

    def clear_count(self):
        self.mutex.acquire()
        self.timeout_err  = 0
        self.other_err    = 0
        self.success      = 0
        self.count        = 0
        self.mutex.release()
    #end def

    def get_all_count(self):
        self.mutex.acquire()
        timeout_err = self.timeout_err
        other_err = self.other_err
        success = self.success
        self.mutex.release()

        return timeout_err,other_err,success
    #end def
#end class

def write_weak_log(task_id, task_name, ip,type,username,password):
    try:
        conn = MySQLdb.connect(host, user, passwd , db = 'waf_hw', charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        sql = "select count(*) as c from weak_pwd_details_" + task_id + " where `type` = %s and `username` = %s and `password` = %s and `ip` = %s "
        cursor.execute(sql,(type,username,password,ip))
        conn.commit()
        res = cursor.fetchone()
        if res and len(res) > 0 and res['c'] > 0:
            return
        #end if
        sql = "insert into weak_pwd_details_" + task_id + " (taskid,taskname,ip,type,username,password) values (%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,(task_id,task_name,ip,type,username,password))
        conn.commit()

        #syslog_weak_vul(self.task_id, self.task_name, ip, type, username, password)
    except Exception,e:
        logging.getLogger().error("File:common.py, write_weak_log:" + str(e))
    #end try
#end def

def findCode(content):
    try:
        match = re.findall(r"<meta(.+?)charset(.*?)=(.+?)\"",content,re.I)
        if match and len(match) > 0:
            row = match[0][2].replace(" ","").lower()
            return row
        else:
            return 'utf8'
        #end if
    except Exception,e:
        logging.getLogger().error("File:common.py, findCode:" + str(e))
        return 'utf8'
    #end try
#end def

def changeCode(msg,code='utf8'):
    if code == 'utf8' or code == 'utf-8':
        return msg
    else:
        try:
            return msg.decode(code).encode('utf8')
        except Exception,e:
            return ""
        #end try
    #end if
#end def

# to fix some missing bugs, eg. CheckTestScript,...
def checkFileTypeStatus(scheme,domain,base_path,type,method):
    try:
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        http.follow_redirects = False
        socket.setdefaulttimeout(30)
#-------start 2014-10-14 yinkun ----------------------------------
        conn_domain = ''
        if checkIpv6(domain):
            conn_domain = '[' + domain +']'
        else:
            conn_domain = domain
#-------end-----------------------------------------------------------
        url = "%s://%s%snulllllllllll%s" % (scheme,conn_domain,base_path,type)
        if method.lower() == "head":
            #res, content = http.request(url, "HEAD")
            res, content = yx_httplib2_request(http,url, "HEAD")
        else:
            #res, content = http.request(url)
            res, content = yx_httplib2_request(http,url)
        #end if
        if res and res.has_key('status') and (res['status'] == '404' or res['status'] == '301' or res['status'] == '302'):
            return True
        else:
            return False
        #end if
    except Exception,e:
        #logging.getLogger().error("File:common.py, checkErrorFileStatus:%s,task id:%s,scheme:%s,domain:%s,base_path:%s,type:%s,method:%s" % (str(e),self.task_id,scheme,domain,base_path,type,method))
        #Fix Bug #2112
        logging.getLogger().error("File:common.py, checkFileTypeStatus:%s,scheme:%s,domain:%s,base_path:%s,type:%s,method:%s" % (str(e),scheme,domain,base_path,type,method))
        return False
    #end try
#end def


def checkErrorFileStatus(scheme,domain,base_path,type,method):
    try:
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        http.follow_redirects = False
        socket.setdefaulttimeout(30)
#-------start 2014-10-14 yinkun ----------------------------------
        conn_domain = ''
        if checkIpv6(domain):
            conn_domain = '[' + domain +']'
        else:
            conn_domain = domain
#-------end-----------------------------------------------------------
        url = "%s://%s%snulllllllllll%s" % (scheme,conn_domain,base_path,type)
        if method.lower() == "head":
            #res, content = http.request(url, "HEAD")
            res, content = yx_httplib2_request(http,url, "HEAD")
        else:
            #res, content = http.request(url)
            res, content = yx_httplib2_request(http,url)
        #end if
        if res and res.has_key('status') and res['status'] == '404':
            return True
        else:
            return False
        #end if
    except Exception,e:
        #logging.getLogger().error("File:common.py, checkErrorFileStatus:%s,task id:%s,scheme:%s,domain:%s,base_path:%s,type:%s,method:%s" % (str(e),self.task_id,scheme,domain,base_path,type,method))
        #Fix Bug #2112
        logging.getLogger().error("File:common.py, checkErrorFileStatus:%s,scheme:%s,domain:%s,base_path:%s,type:%s,method:%s" % (str(e),scheme,domain,base_path,type,method))
        return False
    #end try
#end def

def getFullUrl(scheme,domain,base_path,url):
    try:
#-------start 2014-10-14 yinkun ----------------------------------
        conn_domain = ''
        if checkIpv6(domain):
            conn_domain = '[' + domain +']'
        else:
            conn_domain = domain
#-------end-----------------------------------------------------------
        if url == "":
            return "%s://%s%s" % (scheme,conn_domain,base_path)
        #end if
        if url[0] == '/':
            if url == '/':
                return "%s://%s%s" % (scheme,conn_domain,base_path)
            else:
                return "%s://%s%s%s" % (scheme,conn_domain,base_path,url[1:])
            #end if
        else:
            return "%s://%s%s%s" % (scheme,conn_domain,base_path,url)
        #end if
    except Exception,e:
        logging.getLogger().error("File:common.py, getFullUrl:%s, scheme:%s, domain:%s, base_path:%s, url:%s" % (str(e),scheme,domain,base_path,url))
        return "%s://%s%s%s" % (scheme,domain,base_path,url)
    #end try
#end def

def checkIpv4(ip):
    match = re.findall(u"^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$",ip,re.I)
    if match and len(match) > 0:
        return True
    else:
        return False
    #end if
#end def


def checkIpv6Inner(ip):
    ip = ip.upper()
    match = re.findall(u"((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?",ip,re.I)
    if match and len(match) > 0:
        return True
    else:
        return False
    #end if
#end def

'''
def getTopDomain(domain):
    try:
        IP_PATTEN = re.compile("^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})$")
#-----------start  2014-10-13 yinkun 对域名中含IPv6地址处理---------------------
        a = domain.find('[')
        b = domain.find(']')
        if a >=0 and b>=0:
            temp = domain[a+1:b]
            if checkIpv6(temp):
                return False
#-----------end-------------------------------------------------------------------
        domain = domain.split(":")[0]
        if IP_PATTEN.match(domain):
            return False
        #end if
        temp = domain.split('.')
        if len(temp) < 2:
            return False
        #end if
        list = ['.com.cn','.net.cn','.org.cn','.edu.cn','.gov.cn','.net.ag','.net.bz','.com.br','.net.co','.com.mx','.com.ag','.org.ag','.com.bz','.net.br','.com.co','.nom.co','.nom.es','.co.uk','.org.uk','.com.es','.org.es','.me.uk','.co.in','.ind.in','.net.au','.net.nz','.idv.tw','.firm.in','.net.in','.org.au','.org.nz','.org.tw','.gen.in','.org.in','.com.au','.co.nz','.org.tw']
        flag = False
        for i in list:
            if domain.find(i) > 0:
                flag = True
            #end if
        #end for
        if flag:
            if len(temp) < 3:
                return False
            else:
                return '.'.join(temp[-3:])
            #end if
        else:
            return '.'.join(temp[-2:])
        #end if
    except Exception,e:
        logging.getLogger().error("File:common.py, getTopDomain:%s, domain:%s" % (str(e),domain))
        return False
    #end try
#end def
'''

class Util:
    socketLocker = threading.Lock()
    flowLocker = threading.Lock()
    @classmethod
    def addTimeout(cls,t=5):
        cls.socketLocker.acquire()
        timeout = socket.getdefaulttimeout()
        if timeout:
            if timeout < 115:
                socket.setdefaulttimeout(timeout+t)
        cls.socketLocker.release()
    #end def

    @classmethod
    def subTimeout(cls,t=5):
        cls.socketLocker.acquire()
        timeout = socket.getdefaulttimeout()
        if timeout:
            if timeout > 10:
                socket.setdefaulttimeout(timeout-t)
        cls.socketLocker.release()
    #end def

#end class

def flowControl(instance,requestTime,rec,isForce=False,web_speed=0,web_minute_package_count=None,ischeckTimeOut=False):
    try:
        if not isForce:  #非强制扫描
            if web_speed == 0: #高速率
                if rec.err_out():
                    return True  #错误太多，应该停止扫描
                else:
                    if ischeckTimeOut:  #是否已经超时
                        if not instance.checkTimeOut():  #超时或错误太多，应该停止扫描
                            return True
                        #end if
                    #end if
                    return False  #继续扫描
                #end if       
            elif web_speed == 1: #中
                free = web_minute_package_count['speed'] - requestTime
                time.sleep(free) if free > 0 else None
                return False
            elif web_speed == 2: #低              
                free = web_minute_package_count['speed'] - requestTime
                time.sleep(free) if free > 0 else None
                return False
            elif web_speed == 3: #自定义               
                free = web_minute_package_count['speed'] - requestTime
                time.sleep(free) if free > 0 else None
                return False
            elif web_speed == 4: #智能
                free = web_minute_package_count['speed'] - requestTime
                time.sleep(free) if free > 0 else None
                timeout_err,other_err,success = rec.get_all_count()
                sum = timeout_err + other_err + success
                if sum >= 200:
                    waitSeconds,lessRate = 0,1
                    timeout_probability = float(timeout_err) / sum
                    other_probability = float(other_err) / sum
                    success_probability = float(success) / sum
                    if other_probability >= 0.9:
                        waitSeconds,lessRate = 30,2.0
                    elif other_probability >= 0.6:
                        waitSeconds,lessRate = 10,1.8
                    elif other_probability >= 0.3:
                        waitSeconds,lessRate = 5,1.6
                    elif other_probability >= 0.2:
                        waitSeconds,lessRate = 1,1.4
                    elif other_probability >= 0.1:
                        waitSeconds,lessRate = 0.5,1.2
                    time.sleep(waitSeconds)
                    rec.clear_count()
                    if timeout_probability >= 0.8:
                        Util.addTimeout(5)
                        lessRate = 1.5
                    if success_probability >= 0.85:
                        Util.subTimeout(5)
                        lessRate = 0.6
                    Util.flowLocker.acquire()
                    if 0.006 < web_minute_package_count['speed'] < 60:
                        web_minute_package_count['speed'] = web_minute_package_count['speed'] * lessRate
                    Util.flowLocker.release()
                #end if
                return False
            #end if
        #end if
        return False
    except Exception,e:
        logging.getLogger().error("function flowControl Exception:%s" % str(e))
        return False
    #end try
#end def

_lineremovecompile = re.compile(r"[\r\n\^M]")

def write_scan_log(task_id,domain_id,message):
    try:
        #logfile = hashlib.md5(task_id+domain_id).hexdigest()
        logfile = "%s#%s" %(task_id,domain_id)
        logger = logging.getLogger(logfile)
        if os.path.exists("/var/webs/scanlog/%s" % logfile):
            message = _lineremovecompile.sub('',message)
            logger.info(message)
        else:
            pass
    except Exception,e:
        logging.getLogger().error("function write_scan_log Exception:%s" % str(e))
        return False
    #end try
#end def

def _conn_request(conn, request_uri, method="GET", body=None, headers={}):
    RETRIES = 2
    for i in range(RETRIES):
        try:
            if hasattr(conn, 'sock') and conn.sock is None:
                conn.connect()
            conn.request(method, request_uri, body, headers)
        except socket.timeout:
            raise
        except socket.gaierror:
            conn.close()
            raise
        except ssl.SSLError:
            conn.close()
            raise
        except socket.error, e:
            err = 0
            if hasattr(e, 'args'):
                err = getattr(e, 'args')[0]
            else:
                err = e.errno
            if err == errno.ECONNREFUSED: # Connection refused
                raise
        except httplib.HTTPException:
            if hasattr(conn, 'sock') and conn.sock is None:
                if i < RETRIES-1:
                    conn.close()
                    conn.connect()
                    continue
                else:
                    conn.close()
                    raise
            if i < RETRIES-1:
                conn.close()
                conn.connect()
                continue
        try:
            response = conn.getresponse()
        except (socket.error, httplib.HTTPException):
            if i < RETRIES-1:
                conn.close()
                conn.connect()
                continue
            else:
                conn.close()
                raise
        else:
            content = ""
            content = response.read()
        break
    return (response, content)


#Add by xiayuying 20140122 to improve WebShellCheck's performance
def valid_urls(url, url_list, res_list=[200]):
    try:
        if not url_list:
            return []
        live_list = []
        #Step 1. Send HEAD request to valid url
        conn = httplib.HTTPConnection(url)
        for item in url_list:
            try:
                res, _ = _conn_request(conn,item,"HEAD")
                if res.status in res_list:
                    live_list.append(item)
            except Exception, e:
                logging.getLogger().error("function valid_urls for Exception(inner):%s" % str(e))

        conn.close()
        if float(len(live_list))/len(url_list) > 0.3:
            return []

        return live_list                
    except Exception, e:
        logging.getLogger().error("function valid_urls Exception(outer):%s" % str(e))
        return live_list


def check_exclude_item_url(mod_url,url):
    try:
        if mod_url.find("?") > 0:
            r1 = re.compile(mod_url.split("?")[0].replace("*","(.*?)"))
            res = re.findall(r1, url.split("?")[0])
            if res and len(res) > 0:
                mod_params = mod_url.split("?")[1]
                if mod_url == "*" and url.find("?") < 0:
                    return True
                #end if
                if url.find("?") > 0:
                    params = url.split("?")[1]
                    mod_params_list = mod_params.split("&")
                    for row in mod_params_list:
                        r2 = re.compile(row.replace("*","(.*?)"))
                        res = re.findall(r2, params)
                        if res and len(res) > 0:
                            pass
                        else:
                            return False
                        #end if
                    #end for
                    return True
                #end if
            #end if
        else:
            r1 = re.compile(mod_url.replace("*","(.*?)"))
            res = re.findall(r1, url.split("?")[0])
            if res and len(res) > 0:
                return True
            #end if
        #end if
        
        return False
    except Exception,e:
        logging.getLogger().error("File:plugins.lib.common.py, check_exclude_item_url: %s" % (str(e)))
        return False
    #end try
#end def


def check_exclude_url(exclude_list,url):
    try:
        for row in exclude_list:
            if row.find("http://") < 0 and row.find("https://") < 0:
                continue
            #end if
            if check_exclude_item_url(row,url):
                return True
            #end if
        #end for
        
        return False
    except Exception,e:
        logging.getLogger().error("File:plugins.lib.common.py, check_exclude_url: %s" % (str(e)))
        return False
    #end try
#end def


def yx_httplib2_request(http,url, method="GET", body=None, headers=None):
    if headers is None:
        headers = {"Accept-Encoding":"identity"}
        #"Content-Type":"application/x-www-form-urlencoded"
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    else:
        if not headers.has_key("Accept-Encoding"):
            headers["Accept-Encoding"] = "identity"
        if not headers.has_key("Content-Type"):
            headers["Content-Type"] = "application/x-www-form-urlencoded"
    #end if
     
    if not headers.has_key("Host"):    
        a = url.find("[")
        b = url.find("]")
        if a >=0 and b >=0:
            host_domain = url[a+1:b]
            if checkIpv6(host_domain):
                headers["Host"] = '[' + host_domain + ']'
        
    try:
        response, content = http.request(url, method, body, headers)
        return (response, content)
   
    except Exception,e:
        raise
            
    #end try
#end def

def checkIpv6Inner(ipaddr):
    ip = ipaddr.upper()
    match = re.findall(u"((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?",ip,re.I)
    if match and len(match) > 0:
        return True
    else:
        return False
    #end if
#end def

def getTopDomain(domain):
    try:
#-------START yinkun 2014-10-17-----------------     
        if checkIpv6Inner(domain):
            a = domain.find('[')
            b = domain.find(']')
            if a >= 0 and b >= 0:
                return domain[a:b] + ']'
            else:
                return None
#-------END------------------------------------
        else:      
            return '.'.join(tldextract.extract(domain)[-2:])
    except Exception,e:
        logging.getLogger().error("File:common.py, common.getTopDomain:%s,domain:%s" % (str(e),domain))
    #end try
#end def
