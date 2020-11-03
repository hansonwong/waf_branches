#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import ConfigParser
import MySQLdb
import re
import time
import datetime
import logging
import logging.handlers
import sys
import os
import subprocess
import socket
import fcntl
import struct
import urllib
import urllib2
import httplib
import httplib2
import urlparse
import hashlib
import threading
import smtplib
import ssl
import shutil
import glob
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from waf_netutil import syslog_vul_end
import tldextract

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)
WAF_CONFIG   = sys_path("waf.conf")

VENDOR_CONFIG = sys_path("vendor.conf")
VULDBDIR      = "/var/vuls_db/"
FLAG          = "#d9Fa0j#"
FILE_PREFIX   = "vuldb_"
LOG_DIR       = "/var/www/tmp/"
CRACK_DIC     = "/var/www/yx_python_link/"
cfg           = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
host          = cfg.get("mysql","db_ip").replace('"','')
user          = cfg.get("mysql","db_user").replace('"','')
passwd        = cfg.get("mysql","db_passwd").replace('"','')
database      = "security"
cfg.readfp(open(VENDOR_CONFIG))
company_short_name = cfg.get("company","COMPANY_SHORT_NAME_STR_ID").replace('"','')
company_site = cfg.get("url","COMPANY_SITE_STR_ID").replace('"','')
SYSTEM_ENG_NAME_STR_ID = cfg.get("system","SYSTEM_ENG_NAME_STR_ID").replace('"','')



http_status_dict = {'100':'Continue','101':'Switching Protocols','200':'OK','201':'Created','202':'Accepted','203':'Non-Authoritative Information','204':'No Content','205':'Reset Content','206':'Partial Content','300':'Multiple Choices','301':'Moved Permanently','302':'Found','303':'See Other','304':'Not Modified','305':'Use Proxy','307':'Temporary Redirect','400':'Bad Request','401':'Unauthorized','403':'Forbidden','404':'Not Found','405':'Method Not Allowed','406':'Not Acceptable','407':'Proxy Authentication Required','408':'Request Timeout','409':'Conflict','410':'Gone','411':'Length Required','412':'Precondition Failed','413':'Request Entity Too Large','414':'Request URI Too Long','415':'Unsupported Media Type','416':'Requested Range Not Satisfiable','417':'Expectation Failed','500':'Internal Server Error','501':'Not Implemented','502':'Bad Gateway','503':'Service Unavailable','504':'Gateway Timeout','505':'HTTP Version Not Supported'}
connect_status = ['Connection reset by peer','Broken pipe']

def init_log(console_level, file_level, logfile):
    """init_log functionaa"""
    
    #logname = os.path.basename(__file__).split(".")[0]
    

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

def vulscan_popen(cmd):
    try:
        logging.getLogger().error(cmd)
        return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()
    except Exception,e:
        logging.getLogger().error("vulscan_popen Exception(common):" + str(e) + "," + cmd)
        return ""
    #end try
#end def

def vulscan_call(cmd):
    try:
        logging.getLogger().debug(cmd)
        return subprocess.call(cmd,shell=True,close_fds=True,bufsize=-1)
    except Exception,e:
        logging.getLogger().error("vulscan_call Exception(common):" + str(e) + "," + cmd)
        return -1
    #end try
#end def

def is_dmi_interface_running(interface):
    try:
        return vulscan_popen("ifconfig %s | grep RUNNING" % interface)
    except Exception,e:
        logging.getLogger().error("is_dmi_interface_running"+str(e))

def is_config_ipv6(interface):
    try:
        return vulscan_popen("ifconfig %s | grep Global" % interface)    
    except Exception,e:
        logging.getLogger().error("File:apache_IPv6.py is_config_ipv6()"+str(e))

def getIfaceByRoute(dest_ip):
    try:
        default = ""
        dest_network = ''
        if checkIpv4(dest_ip):
            temp = dest_ip.split('.')
            dest_network = hex((int(temp[0])*256**3 + int(temp[1])*256**2 + int(temp[2])*256 + int(temp[3])) & 0xFFFFFF00)
            
            ifacelist = []
            lines = vulscan_popen("cat /proc/net/route")
            row = lines[0]
            iface_num = 0
            #dest_num = row.find('Destination')-1
            #mask_num = row.find('Mask')-1
            dest_num = 5
            mask_num = 34
        
            #print row
            for row in lines:
                if row.find('eth') >= 0:
                    #print row
                    match = re.findall(r"eth([0-9]{1,2})",row,re.I)
                    if len(match) > 0:
                        iface = "eth%s" % (match[0][0])
                        ip = row[dest_num:(dest_num+8)]
                        ip = "%s%s%s%s" % (ip[6:],ip[4:6],ip[2:4],ip[0:2])
                        mask = row[mask_num:(mask_num+8)]
                        mask = "%s%s%s%s" % (mask[6:],mask[4:6],mask[2:4],mask[0:2])
                    
                        #print iface,ip,mask
                    
                        if ip == '00000000':
                            default = iface
                            continue
                        #end if
                    
                        ip = int(ip,16)
                        mask = int(mask,16)
                    
                        if dest_network == hex(ip & mask):
                            return iface
                        #end if
                    #end if
                #end if
            #end for
        else:
            dest_ip = fullIpv6(dest_ip)
            #print 'fill dest_ipv6:',dest_ip

            lines = vulscan_popen("cat /proc/net/ipv6_route")
            

            temp = dest_ip.split(':')
            for i in range(8):
                dest_network += temp[i]
            temp = dec2bin(int(int(dest_network,16)))
            dest_network = str(temp)[2:]
            #print 'dest_network:',dest_network

            for row in lines:
                if row.find('eth') >= 0:
                    #print '----------------------------------------'
                    match = re.findall(r"eth([0-9]{1,2})",row,re.I)
                    if len(match) > 0:
                        iface = "eth%s" % (match[0][0])
                        #print 'iface',iface
                        ipv6 = row[:32]
                        maskv6 = int(row[33:35])
                        #print maskv6
                        temp = dec2bin(int(ipv6,16))
                        ipv6 = str(temp)[2:]
                        #print 'ipv6(2):',ipv6
                        temp_dest = dest_network[:maskv6]
                        for i in range(maskv6,128):
                            temp_dest += '0'
                        #print 'temp_dest(2):',temp_dest
                        if cmp(temp_dest,ipv6) == 0:
                            if is_dmi_interface_running(iface) and is_config_ipv6(iface):
                                return iface
        
        return default
    except Exception,e:
        logging.getLogger().error("getIfaceByRoute Exception(common):" + str(e) + "," + dest_ip)
        return ""
    #end try
#end def

def updateCveResult(ob):
    try:
        #vul_id = "0"#str(ob['vul_id'])
        cve = ob['cve']
        task_id = str(ob['task_id'])
        port = str(ob['port'])
        proto = ob['proto']
        ip = ob['ip']
        family = ob['family']
        risk_factor = ob['risk_factor']
        output = ob['output']
        metasploit = ob['metasploit']
        asset_scan_id = ob['asset_scan_id']
        #logging.getLogger().error(cve)
      
        if cve is None or cve == "":
            return False
        #end if
        
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        flag = True
        cve_list = cve.split(',')
        for cve_item in cve_list:
            cve_item = cve_item.strip()
            sql = "select * from cve_info where cve_id = '%s'" % (cve_item)
            cur.execute(sql)
            res = cur.fetchone()
            if res and len(res) > 0:
                cve = res['cve_id']
                vul_id = str(0)
                cnnvd = res['cnnvd']
                vul_name = res['vul_name']
                desc = res['abstruct']
                solution = res['notice']
                ref = res['ref']
                
                sql = ""
                if asset_scan_id > 0:
                    sql = "select count(*) as c from vul_details_%s where `cve` = '%s' and `ip` = '%s' and `port` = '%s' and `asset_scan_id` = '%s'" % (task_id, cve, ip, port, asset_scan_id)
                else:
                    sql = "select count(*) as c from vul_details_%s where `cve` = '%s' and `ip` = '%s' and `port` = '%s'" % (task_id,cve,ip, port)
                #end if
                cur.execute(sql)
                res = cur.fetchone()
                if res and len(res) > 0 and res['c'] > 0:
                    continue
                else:
                    sql = "insert into vul_details_" + task_id + " (`ip`,`vul_id`,`cve`,`cnnvd`,`risk_factor`,`vul_name`,`desc`,`solution`,`ref`,`output`,`family`,`port`,`proto`,`metasploit`,`asset_scan_id`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    cur.execute(sql,(ip,vul_id,cve,cnnvd,risk_factor,vul_name,desc,solution,ref,output,family,port,proto,metasploit,asset_scan_id))
                    conn.commit()
                #end if
            else:
                logging.getLogger().debug("not existed:" + cve_item)
                flag = False
            #end if
        #end for
        
        conn.close()
        return flag
    except Exception,e:
        logging.getLogger().error("updateCveResult Exception(common):" + str(e))
        
    #end try 
    return False
#end def

def WriteLog(msg):
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        sql = "insert into `syslog` ( `LogTime` , `Log` ) values ('%s','%s') " % (current_time,msg)
        cur.execute(sql)
        conn.commit()
        logging.getLogger().debug("send Log successful")
        conn.close()
    except Exception,e:
        logging.getLogger().error("send log Exception:" + str(e))    
    #end try
#end def

def get_config_value(name):
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')

        cur = conn.cursor(MySQLdb.cursors.DictCursor)
    
        sql = "select * from config where Name = '%s'" % name
        cur.execute(sql)
        re = cur.fetchone()
        conn.close()
        
        return re["Value"]
 
    except Exception,e:
        logging.getLogger().debug("get_config_value Exception:" + str(e))
        return -1

#end def

def updateTaskManage():
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "select group_concat(t.id) as ids,t.user_id as user_id,u.Maxtasks as max_count from task_manage t,user u where t.user_id = u.id and t.state = '5' group by t.user_id"
        cur.execute(sql)
        res = cur.fetchall()
        for row in res:
            ids = row['ids'].split(',')
            user_id = row['user_id']
            max_count = row['max_count']
            
            sql = "select count(*) as c from task_manage where `user_id` = '%s' and `state` = '2'" % (str(user_id))
            cur.execute(sql)
            temp = cur.fetchone()
            count = max_count - temp['c']
            if count <= 0:
                continue
            #end if
            list = []
            for t in ids:
                list.append(t)
                count = count - 1
                if count <= 0:
                    break
                #end if
            #end for
            
            sql = "update `task_manage` set `state` = '2',start_time = now() where `id` in (%s)" % (','.join(list))
            cur.execute(sql)
            conn.commit()
        #end for
        cur.close()
        conn.close()
    except Exception,e:
        logging.getLogger().debug("updateTaskManage Exception:" + str(e))
    #end try 
#end def

def check_if_all_end(taskid):
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from task_manage where id = %d" % int(taskid)
        cur.execute(sql)
        ret = cur.fetchone()
        
        if ret:
            if int(ret["state"]) == 3:
                syslog_vul_end(int(taskid), ret["task_name"].encode("utf8"))
            #end fi
        #end if
        cur.close()
        conn.close()
    except Exception,e:
        logging.getLogger().debug("check_if_all_end Exception:" + str(e))
    #end try 
#end def
    

def createReport(task_id):
    try:
        conn = httplib.HTTPSConnection("127.0.0.1")
        conn.request("GET", "/html/autoreport/%s" % (str(task_id)))
        ret = conn.getresponse() 
        try:
            content = ret.read()
            if content.find('#') >= 0 and content != "#error#":
                report_id = content.split('#')[1]
                
                vulscan_popen("/usr/bin/php -c /etc/php5/apache2/php.ini -f /var/www/yx_createreport_link.php %s" % (report_id))
                
                conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
                cur = conn.cursor(MySQLdb.cursors.DictCursor)
                sql = "select `filename` from `report_list` where `id` = '%s'" % (str(report_id))
                cur.execute(sql)
                res = cur.fetchone()
                filename = res['filename']
                conn.close()
                
                vulscan_popen("chown www-data /var/www/Report/%s.zip" % (filename))
                vulscan_popen("chgrp www-data /var/www/Report/%s.zip" % (filename))
                return filename
            else:
                logging.getLogger().error('get_report error:' + content)
            #end if
        except Exception, e1:
            logging.getLogger().error("build_report error:" + str(e1)) 
        #end try
        
        return -1
    except Exception,e:
        logging.getLogger().debug("createReport Exception:" + str(e))
        return -1
    #end try 
#end def

def sendEmail(task_id):
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select `state`,`task_name`,`email` from `task_manage` where `id` = '%s'" % (str(task_id))
        cur.execute(sql)
        res = cur.fetchone()
        state = res['state']
        task_name = res['task_name'].encode('utf8')
        email = ""
        if res['email'] and res['email'] != "":
            email = res['email']
        else:
            email = ""
        #end if
        email = res['email']
        if state != 3 or email == "":
            conn.close()
            return
        #end if
        
        email_ob = {}
        sql = "select `Name`,`Value` from `config` where `Name` in ('email_from','email_account','email_pass','email_smtp','email_smtp_port','email_send_to')"
        cur.execute(sql)
        res = cur.fetchall()
        conn.close()
        
        for row in res:
            email_ob[row['Name']] = row['Value']
        #end for
        
        filename = createReport(task_id)
        if filename == -1:
            return
        #end if
        email_ob['filename'] = "/var/www/Report/%s.zip" % (filename)
        email_ob['html'] = ""
        email_ob['title'] = "自动报表（任务名：%s）" % (task_name)
        
        msg = MIMEMultipart()
        
        body = MIMEText(email_ob['html'], 'html', 'utf-8')
        msg.attach(body)
        try:
            att = MIMEText(open(email_ob['filename'], 'rb').read(), 'base64', 'gb2312')
            att['content-type'] = 'application/octet-stream'
            att['content-disposition'] = 'attachment;filename="%s"' % os.path.basename(email_ob['filename'])
            msg.attach(att)
        except Exception, e1:
            logging.getLogger().error("no such file error:" + str(e1))
            return -1
        #end try
        
        #msg['to'] = email_ob['email_send_to']
        msg['to'] = email
        msg['from'] = email_ob['email_from']
        msg['subject'] = email_ob['title'] + "，" + time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        try:
            smtp = smtplib.SMTP(email_ob['email_smtp'] + ":" + str(email_ob['email_smtp_port']))
            smtp.login(email_ob['email_account'], email_ob['email_pass'])
            smtp.sendmail(msg['from'], msg['to'], msg.as_string())
            smtp.close()
        except Exception, e1:
            logging.getLogger().error("send_report error:" + str(e1))
        #end try
    
        WriteLog('发送Email，名称：' + msg['subject'] )
        
    except Exception,e:
        logging.getLogger().error("sendEmail Exception:" + str(e))
    #end try 
#end def


def sendUpgradeSuccess(packageType,version):
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        email_ob = {}
        sql = "select `Name`,`Value` from `config` where `Name` in ('email_from','email_account','email_pass','email_smtp','email_smtp_port','email_send_to')"
        cur.execute(sql)
        res = cur.fetchall()
        conn.close()
        
        for row in res:
            email_ob[row['Name']] = row['Value']
        #end for
        smtp = smtplib.SMTP(email_ob['email_smtp'] + ":" + str(email_ob['email_smtp_port']))
        smtp.login(email_ob['email_account'], email_ob['email_pass'])

        msg_str = ""
        if packageType == "build":
            msg_str = '固件升级成功\n时间：%s\n版本：%s'%(str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())),version)
        else:
            msg_str = '规则升级成功\n时间：%s\n版本：%s'%(str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())),version)
        #end if

        msg = MIMEText(msg_str,'plain','utf-8')
        msg['to'] = email_ob['email_send_to']
        msg['from'] = email_ob['email_from']
        msg['subject'] = '设备升级成功'
        smtp.sendmail(email_ob['email_from'], email_ob['email_send_to'] , msg.as_string())
        smtp.close()
    except Exception, e:
        logging.getLogger().error("send upgrade success email error:" + str(e))
    #end try
#end def


def requestUrl(http,url,task_id,domain_id):
    try:
        sep = "####################"
        #download_dir = "/tmp/task_id%sdomain_id%s/" % (str(task_id),str(domain_id))
        download_dir = "/var/webs/task%s/" % (str(task_id))
        res = {}
        content = ""
        filename = hashlib.sha1(url).hexdigest()
        if os.path.isfile(download_dir + filename):
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
                    #读取状态
                    if row.find(':') > 0:
                        row = row.replace("\n","")
                        temp = row.split(':')
                        res[temp[0]] = ':'.join(temp[1:])
                    #end if
                else:
                    #读取内容
                    content += row
                #end if
            #end for
        else:
#           res, content = http.request(url)
            res, content = nvs_httplib2_request(http,url)
            lines = []
            for k in res.keys():
                lines.append(k+':'+res[k] + "\n")
            #end for
            lines.append(sep+"\n")
            lines.append(content)
            f = file(download_dir+filename,'w+')
            f.writelines(lines)
            f.close()
            if res.has_key('content-location') and res['content-location'] != url:
                filename = hashlib.sha1(res['content-location']).hexdigest()
                f = file(download_dir+filename,'w+')
                f.writelines(lines)
                f.close()
            #end if
            lines = []
        #end if
        return res,content
    except Exception,e:
        logging.getLogger().debug("requestUrl Exception(common):" + str(e))
        #print url
        return {'status':'404'},""
    #end try
#end def

def changeUrl(url):
    try:
        list = []
        if url.find('?') > 0:
            t1 = url.split('?')
            tt = t1[-1].split('&')
            for j in range(0,len(tt)):
                msg = ""
                for i in range(0,len(tt)):
                    if i == j:
                        temp = tt[i]
                    else:
                        msg = msg + tt[i]
                        msg = msg + '&'
                    #end if
                #end for
                url2 = t1[0] + '?' + msg + temp
                list.append(url2)
            #end for
        #end if
        return list
    except Exception,e:
        logging.getLogger().error("File:common.py, changeUrl function:" + str(e) + ", url:" + str(url))
        return []
    #end try
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

def getRequest(url,method,headers={},body=""):
    try:
        parse = urlparse.urlparse(url)
        domain = parse[1]
        path = parse[2]
        list = []
        list.append("%s %s  HTTP/1.1#" % (method,path))
        list.append("Host: %s" % (domain))
        if len(headers.keys()) > 0:
            for k in headers:
                list.append("%s: %s" % (k,headers[k]))
            #end for
        else:    
            list.append("Connection: Keep-alive")
            list.append("Accept: text/plain")
            list.append("User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5")
        #end if
        if body != "":
            list.append("Content: %s" % (body))
        #end if
        return '#'.join(list)
    except Exception,e:
        logging.getLogger().error("File:common.py, getRequest function:" + str(e) + ",url:" + str(url))
        return ''
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
        return '#'.join(list)
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
        list = []
        list.append("GET %s HTTP/1.1" % (path))
        list.append("Host: %s" % (domain))
        list.append("Connection: Keep-alive")
        list.append("Accept: text/plain")
        list.append("User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5")
        return '#'.join(list)
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
        return '#'.join(list)
    except Exception, e:
        logging.getLogger().error("File:common.py, getGetResponse function:" + str(e) + ",task id:" + task_id + ", domain id:" + domain_id + ",url:" + url)
        return ''
    #end try
#end def

def get_url_object(url,timeout):
    try:
        if url == '':
            return ''
        #end if
        url = url.replace(' ','')
        if url.lower().find('http://') < 0:
            url = 'http://' + url
        #end if
        socket.setdefaulttimeout(timeout)
        f = urllib2.urlopen(url)
        f.close()
        return f
    except Exception,e:
        return ''
    #end try
#end def

def get_url_content(url,timeout):
    
    try:
        
        if url == "":
            
            return ""
        
        #end if
            
        url = url.replace(' ','')
        
        if url.lower().find('http://') < 0:
            
            url = 'http://' + url
                
        #end if
        
        if url != '':
        
            socket.setdefaulttimeout(timeout)
            
            f = urllib2.urlopen(url)
            
            if f:
                
                html = f.read()
        
                f.close()
        
                return html
            
            else:
                
                return ''
            
            #end if
        
        else:
            
            return ''
        
        #end if
        
    except Exception,e:
        
        #logging.getLogger().error("get url conent Exception(common):" + str(e))
        
        return ''
        
    #end try
#end def

def get_url_response(domain,url,method):

    try:
        
        domain = domain.lower()
            
        domain = domain.replace(' ','') 
        
        if domain.find("http://") >= 0:
            
            domain = domain[7:]
            
        #end if
    
        conn = httplib.HTTPConnection(domain)
            
        conn.request(method, url[len("http://" + domain):], headers = {"Host":domain,"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Accept":"text/plain"})

        result = conn.getresponse()
        
        conn.close()
        
        return result
        
    except Exception,e:
        
        logging.getLogger().debug("get url response Exception(common):" + str(e))
        
        return ''
    
    #end try
#end def

def get_content_len_httplib2(url,timeout):
    
    try:
        
        http = httplib2.Http()
    
        socket.setdefaulttimeout(timeout)
            
#       content = http.request("http://"+self.domain+"/test111111sadfasdfasdfasf.exe")
        res,content = nvs_httplib2_request(http,"http://"+self.domain+"/test111111sadfasdfasdfasf.exe")      
        if content != '':
        
            falselen=len(content)
        
            return falselen
        
        else:
            
            return 0
        
        #end if
        
    except Exception,e:
        
        logging.getLogger().debug("get content len httplib2 Exception(common):" + str(e))
        
        return 0
    
    #end try
#end def  

def toStr(msg):
        
    try:
            
        return msg.encode('utf-8')
        
    except Exception,e:
            
        logging.getLogger().debug("toStr Exception(common):" + str(e))
            
        return ''
        
    #end try
#end def

def table_exists(tablename):
    
    try:
        
        conn = MySQLdb.connect(host,user,passwd,db=database,charset='utf8')

        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select count(*) as c from information_schema.tables  where table_name = '%s' and TABLE_SCHEMA = '%s'" % (tablename, database)
        
        cur.execute(sql)
        
        ret = cur.fetchone()
        
        conn.close()
        
        if int(ret["c"]) == 1:
            
            return True
        
        else:
            
            return False
        
        #end if
        
    except Exception,e:
        
        logging.getLogger().error("table_exists Exception(common):" + str(e))
        
        return False
    
    #end try
#end def

def httpRequest(url,method,headers,body,timeout,enable_forward):
    
    http = httplib2.Http()
    
    if enable_forward:
        
        http.follow_redirects = True
        
    else:
        
        http.follow_redirects = False
        
    #end if
            
    socket.setdefaulttimeout(timeout)
    
    response, content = http.request(url,method,headers=headers,body=body)
            
    #response, content = http.request("http://192.168.9.119/sdfsdsdfgsdffffffffffffffffffffffffffffffffdsd/test.txt", 'PUT', body="hello world>>>>>>>>>>>>")
    
    #response, content = http.request("http://192.168.9.119/test/")
    
    returnDict = dict()
    
    #returnDict['response'] = "sdfsfds"
    
    #returnDict['content'] = "dfsdfsdf"
    
    #print response
    
    #print content
    
    return returnDict
    
#end def
        
def load_scripts(task_id):

    result = []
    
    try:
        conn = MySQLdb.connect(host,user,passwd,db=database,charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select `web_scan_policy` from task_manage where id = %d" % task_id
        
        cur.execute(sql)
        ret = cur.fetchone()
        
        if ret and len(ret["web_scan_policy"]) > 0:
            vul_list = ret["web_scan_policy"].split(",")
            
            for vul in vul_list:
                try:
                    if vul == "1" or vul == "3" or vul == "4":
                        continue
                    #end if
                    filename = VULDBDIR + FILE_PREFIX + vul
                    f = open(filename, "r")
                    #for l in  f.readlines():
                    #    print l
                
                    #while f.readline():
                    for line in f.readlines():
                        result.append(vul + "#VUL_ID_SPLIT#" + line)
                        #result = result + f.readlines()
                    f.close()
                except Exception,e:
                    continue
                #end try
            #end for
        #end if
                
        #print "load total scripts: %d" % len(result)        
        return result
    except Exception,e:
        
        print e
        
        return result
           
#end def

def create_dir(dir):
    try:
        if os.path.exists(dir):
            shutil.rmtree(dir,True)
        #end if
        if os.path.exists(dir) == False:
            os.mkdir(dir)
        #end if
        
        return True
    except Exception,e:
        logging.getLogger().error("function create_dir Exception:%s, dir:%s" % (str(e),dir))
        return False
    #end try
#end def

isufs = int(vulscan_call("which mkfs.ufs > /dev/null")) == 0

#print "isufs:",isufs

def create_dmfs(imgfile,filesize):
    try:
        if check_dmfs_exists(imgfile):
            logging.getLogger().error("imgfile:%s is running" % (imgfile))
            return True
        #end if
        if os.path.exists(imgfile):
            os.remove(imgfile)
        #end if
        
        cmd = "dd if=/dev/zero of=%s bs=1M count=%d" % (imgfile,filesize)
        vulscan_popen(cmd)
        buf = "mkfs.ufs" if isufs else "echo 'y'|mkfs.ext3 -q"
        cmd = "%s %s" % (buf,imgfile)
        vulscan_popen(cmd)
        
        return True
    except Exception,e:
        logging.getLogger().error("function create_dmfs Exception:%s" % (str(e)))
        return False
    #end try
#end def

def check_dmfs_exists(imgfile):
    try:
        lines = vulscan_popen("mount")
        for row in lines:
            if row.find(imgfile) >= 0:
                return True
            #end if
        #end for
        return False
    except Exception,e:
        logging.getLogger().error("function check_dmfs_exists Exception:%s" % (str(e)))
        return False
    #end try
#end def

def mount_dmfs(imgfile,dir):
    try:
        if os.path.exists(dir) == False:
            os.mkdir(dir)
        #end if
        if os.path.exists(imgfile) == False:
            return False
        #end if
        
        if check_dmfs_exists(imgfile):
            return True
        #end if
        buf = "mount -t ufs -o ufstype=ufs2,rw -o loop" if isufs else "mount -o loop"
        cmd = "%s %s %s" % (buf,imgfile,dir)
        vulscan_popen(cmd)
        
        if check_dmfs_exists(imgfile):
            return True
        else:
            return False
        #end if
    except Exception,e:
        logging.getLogger().error("function mount_dmfs Exception:%s" % (str(e)))
        return False
    #end try
#end def

def umount_dmfs(imgfile,dir):
    try:
        if check_dmfs_exists(imgfile):
            cmd = "umount %s" % (imgfile)
            vulscan_popen(cmd)
        #end if
        if check_dmfs_exists(imgfile):
            return False
        #end if
        
        if os.path.exists(dir):
            shutil.rmtree(dir)
        #end if
        
        return True
    except Exception,e:
        logging.getLogger().error("function umount_dmfs Exception:%s" % (str(e)))
        return False
    #end try
#end def

def remove_dmfs(imgfile,dir):
    try:
        if os.path.exists(imgfile):
            os.remove(imgfile)
        #end if
        
        if os.path.exists(dir):
            shutil.rmtree(dir)
        #end if
        
        return True
    except Exception,e:
        logging.getLogger().error("function remove_dmfs Exception:%s" % (str(e)))
        return False
    #end try
#end def 

'''
def create_dmfs(imgfile,filesize):
    try:
        keyfile = "/var/waf/webtmp.key"
        if os.path.exists(keyfile) == False:
            vulscan_popen("touch %s" % (keyfile))
        #end if
        f = file(keyfile,"r+")
        lines = f.readlines()
        f.close()
        if lines and len(lines) == 1 and len(lines[0]) == 32:
            pass
        else:
            f = file(keyfile,"w+")
            lines = ['12345678123456781234567812345678']
            f.writelines(lines)
            f.close()
        #end if
        
        devfile = imgfile.split("/")[-1].split(".")[0]
        if os.path.exists(imgfile) and os.path.exists("/dev/mapper/%s" % (devfile)):
            return True
        #end if
        if os.path.exists(imgfile) and os.path.exists("/dev/mapper/%s" % (devfile)) == False:
            os.remove(imgfile)
        #end if
        if os.path.exists(imgfile) == False and os.path.exists("/dev/mapper/%s" % (devfile)):
            remove_dmfs(devfile)
        #end if
        
        cmd = "dd if=/dev/zero of=%s bs=1M count=%d;"
        cmd += "losetup /dev/loop0 %s;"
        cmd += "cryptsetup create %s /dev/loop0 -d %s;"
        cmd += "mkfs.ext3 /dev/mapper/%s;"
        
        cmd = cmd % (imgfile,filesize,imgfile,devfile,keyfile,devfile)
        vulscan_popen(cmd)
        
        return True
    except Exception,e:
        logging.getLogger().error("function create_dmfs Exception:%s" % (str(e)))
        return False
    #end try
#end def

def mount_dmfs(devfile,mountdir):
    try:
        if devfile.find("/") < 0:
            devfile = "/dev/mapper/%s" % (devfile)
        #end if
        if os.path.exists(devfile) == False:
            return False
        #end if
        if os.path.exists(mountdir) == False:
            os.mkdir(mountdir)
        #end if
        lines = vulscan_popen("mount")
        for row in lines:
            if row.find("%s on" % (devfile)) >= 0:
                return True
            #end if
        #end for
        cmd = "mount %s %s" % (devfile,mountdir)
        vulscan_popen(cmd)
        
        return True
    except Exception,e:
        logging.getLogger().error("function mount_dmfs Exception:%s" % (str(e)))
        return False
    #end try 
#end def

def umount_dmfs(devfile,mountdir):
    try:
        if devfile.find("/") < 0:
            devfile = "/dev/mapper/%s" % (devfile)
        #end if
        flag = True
        lines = vulscan_popen("mount")
        for row in lines:
            if row.find("%s on" % (devfile)) >= 0:
                flag = False
                break
            #end if
        #end for
        if flag == False:
            cmd = "umount %s" % (devfile)
            vulscan_popen(cmd)
        #end if
        
        if os.path.exists(mountdir):
            shutil.rmtree(mountdir)
        #end if
        
        return True
    except Exception,e:
        logging.getLogger().error("function umount_dmfs Exception:%s" % (str(e)))
        return False
    #end try
#end def

def remove_dmfs(devfile):
    try:
        if devfile.find("/") < 0:
            devfile = "/dev/mapper/%s" % (devfile)
        #end if
        imgfile = "/var/webs/%s.img" % (devfile.split("/")[-1])
        
        if os.path.exists(devfile):
            cmd = "cryptsetup remove %s" % (devfile)
            vulscan_popen(cmd)
        #end if
        
        if os.path.exists(devfile):
            return False
        else:
            if os.path.exists(imgfile):
                os.remove(imgfile)
            #end if
            return True
        #end if
    except Exception,e:
        logging.getLogger().error("function remove_dmfs Exception:%s" % (str(e)))
        return False
    #end try
#end def


'''

def create_web_tmp(task_id):
    try:
        filesize = 150
        imgfile = "/var/webs/task%s.img" % (task_id)
        dir = "/var/webs/%s" % (imgfile.split("/")[-1].split(".")[0])
        
        if create_dmfs(imgfile,filesize):
            if mount_dmfs(imgfile,dir):
                return True
            else:
                create_dir(dir)
                return False
            #end if
        else:
            create_dir(dir)
            return False
        #end if
        
        return True
    except Exception,e:
        logging.getLogger().error("function create_web_tmp Exception:%s, task id:%s" % (str(e),task_id))
        return False
    #end try
#end def

def process_exist(process):
    try:
        result = vulscan_popen("ps -ef | grep %s | grep -v grep | wc -l" % process)
        if result and int(result[0]) > 0:
            return True
        return False
    except Exception,e:
        logging.getLogger().error("function process_exist Exception:%s,process:%s" % (str(e),process))
        return False

def create_scanlog_tmp(task_id):
    try:
        logging.getLogger().error("task_id:%s,scanlog:%s" %(task_id,"create scanlog begin"))
        while 1:
            if process_exist("scanlog.sh"):
                time.sleep(0.1)
            else:
                if not process_exist("scanlog.sh"): # double check
                    result = vulscan_popen("/var/waf/scanlog.sh")
                    logging.getLogger().error("task_id:%s,scanlog:%s" %(task_id,''.join(result)))
                    break
                #end if
            #end if
    except Exception,e:
        logging.getLogger().error("function create_scanlog_tmp Exception:%s, task id:%s" % (str(e),task_id))
        return False
    #end try
#end def

def clear_scanlog(task_id):
    try:
        match = glob.iglob('/var/webs/scanlog/%s#*' % task_id)
        for m in match:
            os.remove(m)
    except Exception,e:
        logging.getLogger().error("function clear_scanlog Exception:%s, task id:%s" % (str(e),task_id))
    #end try
#end def

def remove_web_tmp(task_id):
    try:
        imgfile = "/var/webs/task%s.img" % (task_id)
        dir = "/var/webs/%s" % (imgfile.split("/")[-1].split(".")[0])
        
        if umount_dmfs(imgfile,dir):
            if remove_dmfs(imgfile,dir):
                return True
            else:
                return False
            #end if
        else:
            return False
        #end if
        
    except Exception,e:
        logging.getLogger().error("function remove_web_tmp Exception:%s, task id:%s" % (str(e),task_id))
        return False
    #end try
#end def

def getFullUrl(scheme,domain,url):
    try:
        if url.find('http://') >= 0 or url.find('https://') >= 0 or url.find('HTTP://') >= 0 or url.find('HTTPS://') >= 0:
            return url
        #end if
        url = url.replace("../","/").replace("./","/").replace("//","/")
        if url == '':
            return "%s://%s/" % (scheme,domain)
        else:
            if url[0] == '/':
                return "%s://%s%s" % (scheme,domain,url)
            else:
                return "%s://%s/%s" % (scheme,domain,url)
            #end if
        #end if
        
    except Exception,e:
        logging.getLogger().error("function getFullUrl Exception:%s, scheme:%s, domain:%s, url:%s" % (str(e),scheme,domain,url))
    #end try
    
    return url
#end def

def parseUrl(url):
    try:
        scheme = ''
        domain = ''
        base_path = ''
        
        parse = urlparse.urlparse(url)
        scheme = parse[0]
        domain = parse[1]
        if domain.find(':') > 0:
            port = domain.split(':')[1]
            if port == '80':
                scheme = 'http'
                domain = domain.split(':')[0]
            elif port == '443':
                scheme = 'https'
                domain = domain.split(':')[0]
            #end if
        #end if
        if parse[2] == "":
            base_path = "/"
        else:
            t = parse[2].split("/")
            if len(t) <= 2:
                base_path = "/"
            else:
                t[-1] = ""
                base_path = "/".join(t)
            #end if
        #end if
        
        return True,scheme,domain,base_path
    except Exception,e:
        logging.getLogger().error("function parseUrl Exception:%s, url:%s" % (str(e),url))
        return False,'','',''
    #end try 
#end def

def getRedirect(url):
    scheme = 'http'
    domain = ''
    base_path = ''
    
    try:
        
        parse = urlparse.urlparse(url)
        if parse[0] == 'http' or parse[0] == 'https':
            scheme = parse[0]
        #end if
        domain = parse[1]
        base_path = parse[2]
        if base_path == '':
            base_path = '/'
        #end if
        
        url = "%s://%s%s" % (scheme,domain,base_path)
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        http.follow_redirects = False
        socket.setdefaulttimeout(120)
#       res, content = http.request(url)
        res, content = nvs_httplib2_request(http,url)
        if res and res.has_key('status') and res['status'] in ['200','301','302','403']:
            if res['status'] in ['301','302'] and res.has_key('location'):
                url = getFullUrl(scheme,domain,res['location'])
                
                return parseUrl(url)
            #end if
            
            match = re.findall(r"<(\s*)meta(\s+)http-equiv=(\s*)(\"|')(\s*)refresh(\s*)(\4)(\s+)content=(\s*)(\"|')([\.0-9\s]+);(\s*)url=(\s*)(\"|')?(.+?)(\"|')?(\s*)(\"|')(\s*)[/]*>",content,re.I)
            if match and len(match) > 0:
                url = getFullUrl(scheme,domain,match[0][-5].replace(" ",""))
                
                return parseUrl(url)
            #end if
            
            if res.has_key('content-location'):
                url = getFullUrl(scheme,domain,res['content-location'])
                
                return parseUrl(url)
            #end if
            
            return parseUrl(url)
        #end if
            
    except Exception,e:
        logging.getLogger().error("function getRedirect Exception:%s, url:%s" % (str(e),url))
        return parseUrl(url)
    #end try
        
    return False,scheme,domain,base_path
#end def

def updateAssetCount(task_id,asset_scan_id):
    try:
        if asset_scan_id > 0:
            conn = MySQLdb.connect(host,user,passwd,db=database,charset='utf8')
            cur = conn.cursor(MySQLdb.cursors.DictCursor)
            #sql = "select count(*) as c from `task_manage` where `id` = '%s'" % (task_id)
            #cur.execute(sql)
            #res = cur.fetchone()
            sql = "select `state` from task_manage where id = '%s'" % (task_id)
            cur.execute(sql)
            res = cur.fetchone()
            if res and len(res) > 0 and str(res['state']) == "3":
                sql = "select `target` from `asset_scan` where `id` = '%s'" % (asset_scan_id)
                cur.execute(sql)
                res = cur.fetchone()
                target = res['target']
                
                vul_detail_table = "vul_details_%s" % (task_id)
                scan_result_table = "scan_result_%s" % (task_id)
                weak_pwd_details_table = "weak_pwd_details_%s" % (task_id)
                domain_list_table = "domain_list_%s" % (task_id)
                hostmsg_table = "hostmsg_%s" % (task_id)
                
                dic = {}
                sql = "select count(*) as c, risk_factor as level, ip from %s where asset_scan_id = '%s' group by concat(ip,risk_factor) union all select count(*) as c, level,ip from %s where asset_scan_id = '%s' group by concat(ip,level) union all select count(*) as c, 'H' as level,ip from %s where asset_scan_id = '%s' group by ip" % (vul_detail_table,asset_scan_id,scan_result_table,asset_scan_id,weak_pwd_details_table,asset_scan_id)
                cur.execute(sql)
                res = cur.fetchall()
                for row in res:
                    ip = row['ip']
                    level = ''
                    if row['level'] == 'C':
                        level = 'C'
                    elif row['level'] == 'H' or row['level'] == 'HIGH':
                        level = 'H'
                    elif row['level'] == 'M' or row['level'] == 'MED':
                        level = 'M'
                    elif row['level'] == 'L' or row['level'] == 'LOW':
                        level = 'L'
                    elif row['level'] == 'I':
                        level = 'I'
                    else:
                        level = 'I'
                    #end if
                    c = row['c']
                    if dic.has_key(ip):
                        dic[ip][level] += c
                    else:
                        dic[ip] = {'C':0, 'H':0, 'M':0, 'L':0, 'I':0}
                        dic[ip][level] += c
                    #end if
                #end for
                for k in dic.keys():
                    ip = k
                    h = dic[k]['H'] + dic[k]['C']
                    m = dic[k]['M']
                    l = dic[k]['L'] + dic[k]['I']
                    level = 'N'
                    if dic[k]['C'] > 0:
                        level = 'C'
                    else:
                        if dic[k]['H'] > 0:
                            level = 'H'
                        else:
                            if dic[k]['M'] > 0:
                                level = 'M'
                            else:
                                if dic[k]['L'] > 0:
                                    level = 'L'
                                else:
                                    if dic[k]['I'] > 0:
                                        level = 'I'
                                    else:
                                        level = 'N'
                                    #end if
                                #end if
                            #end if
                        #end if
                    #end if
                    
                    sql = "update `as_register` set `AS_Level` = '%s', `AS_HighNum` = '%s', `AS_MidNum` = '%s', `AS_LowNum` = '%s' where `AS_Ip` = '%s'" % (level,h,m,l,ip)
                    cur.execute(sql)
                    conn.commit()
                #end for
                
                dic = {}
                sql = "select count(*) as c, d.scheme as scheme, d.domain as domain, s.level as level from %s s, %s d where s.asset_scan_id = '%s' and s.domain_id = d.id group by concat(s.domain_id,s.level)" % (scan_result_table,domain_list_table,asset_scan_id)
                cur.execute(sql)
                res = cur.fetchall()
                for row in res:
                    scheme = row['scheme']
                    domain = row['domain']
                    ip = "%s://%s" % (scheme,domain)
                    level = row['level']
                    c = row['c']
                    if dic.has_key(ip):
                        dic[ip][level] += c
                    else:
                        dic[ip] = {'HIGH':0, 'MED':0, 'LOW':0}
                        dic[ip][level] += c
                    #end if
                #end for
                
                for k in dic.keys():
                    ip = k
                    h = dic[k]['HIGH']
                    m = dic[k]['MED']
                    l = dic[k]['LOW']
                    level = 'N'
                    if dic[k]['HIGH'] > 0:
                        level = 'H'
                    else:
                        if dic[k]['MED'] > 0:
                            level = 'M'
                        else:
                            if dic[k]['LOW'] > 0:
                                level = 'L'
                            else:
                                level = 'N'
                            #end if
                        #end if
                    #end if
                    
                    sql = "update `as_register` set `AS_Level` = '%s', `AS_HighNum` = '%s', `AS_MidNum` = '%s', `AS_LowNum` = '%s' where `AS_Ip` like '%s'" % (level,h,m,l,ip+"%")
                    cur.execute(sql)
                    conn.commit()
                #end for
                
                sql = "update `as_register` set `state` = '1' where `AS_Ip` in (select `ip` from %s where `state` = '1' and `asset_scan_id` = '%s')" % (hostmsg_table,asset_scan_id)
                cur.execute(sql)
                conn.commit()
                
                sql = "update `as_register` set `state` = '2', AS_Level = '', AS_HighNum = '0', AS_MidNum = '0', AS_LowNum = '0' where `AS_Ip` in (select `ip` from %s where `state` = '2' and `asset_scan_id` = '%s')" % (hostmsg_table,asset_scan_id)
                cur.execute(sql)
                conn.commit()
                
                targetlist = target.split(",")
                sql = "select `scheme`,`domain` from %s where `asset_scan_id` = '%s'" % (domain_list_table,asset_scan_id)
                cur.execute(sql)
                res = cur.fetchall()
                domainlist = []
                for row in res:
                    scheme = row['scheme']
                    domain = row['domain']
                    domainlist.append("%s://%s" % (scheme,domain))
                #end for
                for row in targetlist:
                    if row.find("http://") < 0 and row.find("https://") < 0:
                        continue
                    #end if
                    state = '2'
                    for domain in domainlist:
                        if row.find(domain) >= 0:
                            state = '1'
                            break
                        #end if 
                    #end for
                    if state == '1':
                        sql = "update `as_register` set `state` = '%s' where `AS_Ip` = '%s'" % (state,row)
                    else:
                        sql = "update `as_register` set `state` = '%s', AS_Level = '', AS_HighNum = '0', AS_MidNum = '0', AS_LowNum = '0' where `AS_Ip` = '%s'" % (state,row)
                    #end if
                    cur.execute(sql)
                    conn.commit()
                #end for
            #end if
            
            cur.close()
            conn.close()
        #end if
    except Exception,e:
        logging.getLogger().error("function updateAssetCount Exception:%s, task id:%s" % (str(e),task_id))
    #end try
#end def

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

def checkProcess(cmd):
    try:
        if cmd == '':
            return True
        #end if
        cmd = "ps -ef | grep '%s' | grep -v grep | grep -v \"sh -c\" | wc -l" % (cmd)
        res = vulscan_popen(cmd)
        res = int(res[0].strip())
        
        if res and res >= 2:
            return False
        #end if
        
        print '''------------------------------------------------------------
checkProcess 成功
------------------------------------------------------------'''
        return True
    except Exception,e:
        logging.getLogger().error("function checkProcess Exception:%s" % str(e))
        return False
    #end try
#end def

def updateHostScan(ip,cursor,conn,task_id,asset_scan_id):
    try:
        _cursor = cursor
        _conn = conn
       
        sql = "select count(*) as c from hostmsg_%s where `ip` = '%s' and `asset_scan_id` = '%s'" % (task_id,ip,asset_scan_id)
        #end if
        _cursor.execute(sql)
        _conn.commit()
        res = _cursor.fetchone()
        if res and len(res) > 0:
            if res['c'] == 1:
                sql = "select count(*) as c from hostmsg_%s where `ip` = '%s' and `state` = '2' and `asset_scan_id` = '%s'" % (task_id,ip,asset_scan_id)
                _cursor.execute(sql)
                _conn.commit()
                if res and len(res) > 0 and res['c'] == 1:
                    sql = "update hostmsg_%s set `state` = '1',`host_state` = '0',`weak_state` = '0',`port_state` = '0' where `ip` ='%s' and `asset_scan_id` = '%s'" % (task_id,ip,asset_scan_id)
                    _cursor.execute(sql)
                    _conn.commit()
                    sql = "update `task_manage` set `host_state` = '0',`weak_state` = '0',`port_state` = '0' where `id` = '%s'" % (task_id)
                    _cursor.execute(sql)
                    _conn.commit()
                #end if
            elif res['c'] == 0:
                current_time = time.strftime("%Y-%m-%d %X",time.localtime())
                sql = "insert into hostmsg_%s (`task_id`,`task_name`,`ip`,`state`,`port_state`,`host_state`,`web_state`,`weak_state`,`start_time`,`asset_scan_id`) values ('%s','','%s','1','0','0','0','0','%s','%s')" % (task_id,task_id,ip,current_time,asset_scan_id)
                _cursor.execute(sql)
                _conn.commit()
                sql = "update `task_manage` set `host_state` = '0',`weak_state` = '0',`port_state` = '0' where `id` = '%s'" % (task_id)
                _cursor.execute(sql)
                _conn.commit()
            #end if
        #end if
        del _cursor
        del _conn
    except Exception,e:
        logging.getLogger().error("function addHostScan Exception:%s" % str(e))




def valid_urls(domain, url_list, res_list=[200]):
    try:
        live_list = []
        #Step 1. Send HEAD request to valid url
        conn = httplib.HTTPConnection(domain)
        for item in url_list:
            try:
                conn.request("HEAD", item)
                res = conn.getresponse()
                res.read() #fix bug 3569
                if res.status in res_list:
                    live_list.append(item)
            except Exception, e:
                logging.getLogger().warn("function valid_urls for Exception:%s" % str(e))
        conn.close()
        return live_list                
    except Exception, e:
        logging.getLogger().warn("function valid_urls Exception:%s" % str(e))
        return live_list

_nonascii = re.compile(r"[^\x00-\xff]")
def nonascii(url,code="utf-8"):
    try:
        if isinstance(url, str):
            url = url.decode(code)
        return _nonascii.search(url)
    except Exception, e:
        logging.getLogger().error("function allascii Exception:%s" % str(e))


_reserved = ';/?:@&=+$|,#' # RFC 3986 (Generic Syntax)
_unreserved_marks = "-_.!~*'()" # RFC 3986 sec 2.3
_safe_chars = urllib.always_safe + '%' + _reserved + _unreserved_marks
def safe_url_string(url):
    return urllib.quote(url,  _safe_chars)


def isIntranetIP(ip):
    tmp = ip.split(".")
    if len(tmp) == 4:
        return int(tmp[0]) == 10 or (int(tmp[0]) == 172 and int(tmp[1]) >= 16 and int(tmp[1]) <= 31) or (int(tmp[0]) == 192 and int(tmp[1]) == 168)

def insertDomain(self,ob):
    try:
        domain_id = 0
        scheme = "http"
        cookie_url = ""
        begin_path = ""

        if ob['ip'] == "":
            return
        if ob.has_key("scheme"):
            scheme = ob["scheme"]
        if ob.has_key("cookie_url"):
            cookie_url = ob["cookie_url"]
        if ob.has_key("begin_path"):
            begin_path = ob["begin_path"]

        domain = ob['domain']
        base_path = ob['base_path']    
            
        flag,scheme,domain,base_path = getRedirect("%s://%s%s" % (scheme,domain,base_path))
        if scheme != 'http' and scheme != 'https':
            scheme = 'http'
        if domain == "" or domain.find(".") <= 0:
            return
            
        if self.mysqlConnect():
            if self.asset_scan_id > 0:
                sql = "select count(*) as c from domain_list_%s where `domain` = '%s' and `scheme` = '%s' and `ip` = '%s' and `base_path` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,domain,scheme,ob['ip'],base_path,self.asset_scan_id)
            else:
                sql = "select count(*) as c from domain_list_%s where `domain` = '%s' and `scheme` = '%s' and `ip` = '%s' and `base_path` = '%s'" % (self.task_id,domain,scheme,ob['ip'],base_path)
            self.cursor.execute(sql)
            self.conn.commit()
            res = self.cursor.fetchone()
            if res and len(res) > 0 and res['c'] > 0:
                return
            else:
                #Fix BUG #2092
                if not base_path:
                    base_path = '/'
                #end if
                sql = "insert into domain_list_" + self.task_id + " (`task_id`,`task_name`,`scheme`,`domain`,`ip`,`state`,`spider_state`,`progress`,`title`,`base_path`,`policy`,`policy_detail`,`service_type`,`site_type`,`database_type`,`start_time`,`end_time`,`cookie_url`,`begin_path`,`asset_scan_id`) values (%s,'',%s,%s,%s,'0','0','',%s,%s,%s,%s,'','','','0000-00-00 00:00:00','0000-00-00 00:00:00',%s,%s,%s) "
                self.cursor.execute(sql,(self.task_id,scheme,domain,ob['ip'],ob['title'],base_path,ob['policy'],ob['policy_detail'],cookie_url,begin_path,self.asset_scan_id))
                self.conn.commit()
                sql = "select LAST_INSERT_ID() as domain_id"
                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchone()
                if res and len(res) > 0 and res['domain_id'] > 0:
                    domain_id = res['domain_id']
                    self.domain_queue.put(str(domain_id))
                    if self.asset_scan_id > 0:
                        sql = "select count(*) as c from hostmsg_%s where `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,ob['ip'],self.asset_scan_id)
                    else:
                        sql = "select count(*) as c from hostmsg_%s where ip = '%s'" % (self.task_id,ob['ip'])
                    self.cursor.execute(sql)
                    self.conn.commit()
                    res = self.cursor.fetchone()
                    if res and len(res) > 0 and res['c'] == 0:
                        current_time = time.strftime("%Y-%m-%d %X",time.localtime())
                        sql = "insert into hostmsg_%s (`task_id`,`task_name`,`ip`,`state`,`port_state`,`host_state`,`web_state`,`weak_state`,`start_time`,`asset_scan_id`) values ('%s','','%s','1','0','0','0','0','%s','%s')" % (self.task_id,self.task_id,ob['ip'],current_time,self.asset_scan_id)
                        self.cursor.execute(sql)
                        self.conn.commit()
                        sql = "update `task_manage` set `host_state` = '0',`weak_state` = '0',`port_state` = '0' where `id` = '%s'" % (self.task_id)
                        self.cursor.execute(sql)
                        self.conn.commit()
                    #end if
                        
                    logging.getLogger().debug("File:common.py,insertDomain:insert into domain_list success,task id:" + self.task_id + ",ip:" + ob['ip'] + ",domain:" + ob['domain'])
                    #end if
                #end if
        else:
            logging.getLogger().error("File:common.py,insertDomain:mysql connect error,task id:" + self.task_id + ",ip:" + ob['ip'] + ",domain:" + ob['domain'])
            #end if
    except Exception,e:
        logging.getLogger().error("File:common.py,insertDomain:" + str(e) + ",task id:" + self.task_id + ",ip:" + ob['ip'] + ",domain:" + ob['domain'])
    #end try
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

def getDomainPolicy(self,http,ip,domain,policy='2'):
    try:
        if isIntranetIP(ip):
            return
        url = "http://query.yxlink.com/dns.py?action=cha&ip=%s" % (ip)
        #logging.getLogger().error("####chaip:"+ip)
        res, content = http.request(url)
        lines = content.split("<br>")
        for line in lines:
            record = line.split("#")
            #logging.getLogger().error("####doamin:"+str(record))
            if len(record) == 2:
                tmpdomain,title = record
                _policy = '5'
                #issubDomain = getTopDomain(tmpdomain) == getTopDomain(domain)
                if policy in ('2','55') and (getTopDomain(tmpdomain) == getTopDomain(domain)):
                    _policy = policy
                #end if
                ob = {'domain':tmpdomain,'scheme':'http','ip':ip,'title':title,'base_path':'/','policy':_policy,'policy_detail':'','cookie_url':''}
                insertDomain(self,ob)
    except Exception,e:
        logging.getLogger().error("File:common.py, getDomainPolicy:" + str(e) + ",ip:" + ip + ",domain:" + domain)
    #end try
#end def


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
        logging.getLogger().error("File:common.py, check_exclude_item_url: %s" % (str(e)))
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
        logging.getLogger().error("File:common.py, check_exclude_url: %s" % (str(e)))
        return False
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

def checkIpv4Inner(ip):
    match = re.findall(u"(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])",ip,re.I)
    if match and len(match) > 0:
        return True
    else:
        return False
    #end if
#end def

def checkIpv4Range(ip_range):
    match = re.findall(u"^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])-(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$",ip_range,re.I)
    if match and len(match) > 0:
        return True
    else:
        return False
    #end if
#end def
'''
def checkIpv6(ip):
    ip = ip.upper()
    match = re.findall(u"^((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?$",ip,re.I)
    if match and len(match) > 0:
        return True
    else:
        return False
    #end if
#end def
'''
def checkIpv6(ipv6_addr):
    try:
        addr= socket.inet_pton(socket.AF_INET6, ipv6_addr)
    except socket.error:
        return False
    else:
        return True

def checkIpv6Inner(ipaddr):
    ip = ipaddr.upper()
    match = re.findall(u"((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?",ip,re.I)
    if match and len(match) > 0:
        return True
    else:
        return False
    #end if
#end def

def checkIpv6Domain(domain):
    ip = domain.upper()
    match = re.findall(u"^\[((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\]$",ip,re.I)
    if match and len(match) > 0:
        return True
    else:
        return False
    #end if
#end def
def checkIpv6Range(ip_range):
    try:
        last_colon_index = 0
        tmp = ip_range.split('-')
        if len(tmp) == 2:
            if checkIpv6(tmp[0]):
                if checkIpv6(tmp[1]):
                    return True
                for i in range(len(tmp[0])):
                    if tmp[0][i] == ':':
                        last_colon_index = i
                tmp_line = tmp[0][last_colon_index+1:]
                if len(tmp_line) > len(tmp[1]):
                    return False
                elif len(tmp_line) < len(tmp[1]):
                    return True
                else:
                    if cmp(tmp_line,tmp[1]) <= 0:
                        return True
                    else:
                        return False
            else:
                return False
        else:
            return False
    except Exception, e:
        logging.getLogger().error("File:common.py, checkIpv6Range: %s" % (str(e)))
        return False

'''
def checkIpv6Range(ip_range):
    ip_range = ip_range.upper()
    match = re.findall(u"^((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?-((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?$",ip_range,re.I)
    if match and len(match) > 0:
        return True
    else:
        return False
    #end if
#end def
'''


# 十进制 to 二进制
def dec2bin(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 2)
        mid.append(str(rem))
    result = ''.join([str(x) for x in mid[::-1]])
    result = '0b' + result
    return result
#end def

# 十六进制 to 十进制
def hex2dec(string_num):
    return int(string_num.upper(), 16)
#end def

# 十进制 to 十六进制
def dec2hex(string_num):
    base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 16)
        mid.append(base[rem])

    return ''.join([str(x) for x in mid[::-1]])
#end def

def ipv4Toint(addr):
    try:
        return struct.unpack("!I",socket.inet_aton(addr))[0]
    except Exception,e:
        logging.getLogger().error("File:common.py, ipv4Toint: %s, addr: %s" % (str(e), str(addr)))
        return ''  
    #end try
#end def

def intToipv4(i):
    try:
        return socket.inet_ntoa(struct.pack("!I",i))
    except Exception,e:
        logging.getLogger().error("File:common.py, intToipv4: %s, i: %s" % (str(e), str(i)))
        return '' 
    #end try
#end def

def fullIpv6(ip):
    if ip == "" or len(ip) < 4 or len(ip) > 39:
        return False
    #end if
    ip = ip.upper()
    match = re.findall(u"^((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?$",ip,re.I)
    if match and len(match) > 0:
        ip_sep = ip.split(":")
        if len(ip_sep) < 8:
            t = 8 - len(ip_sep)
            ip = ip.replace("::",":"*(t+2))
        #end if
        ip_sep = ip.split(":")
        ip = []
        for row in ip_sep:
            row = "0000%s" % (row)
            ip.append(row[-4:])
        #end for
        ip = ":".join(ip)

        return ip
    else:
        return False
    #end if
#end def

def easyIpv6(ip):
    if ip == "" or len(ip) < 4 or len(ip) > 39:
        return False
    #end if
    ip = ip.lower()
    match = re.findall(u"^((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?$",ip,re.I)
    if match and len(match) > 0:
        ip_sep = ip.split(":")
        ip = []
        for row in ip_sep:
            i = 0
            for i in range(len(row)):
                if row == "":
                    break
                elif row == "0":
                    row = "0"
                    break
                elif row[0] == "0":
                    row = row[1:]
                else:
                    break
                #end if
            #end for
            ip.append(row)
        #end for
        
        if len(ip) == 8:
            ip = ":".join(ip)
            i = 8
            while i > 1:
                index = ip.find(":"+"0:"*i)
                if index > 0:
                    ip = "%s::%s" % (ip[0:index],ip[index+(2*i+1):])
                    break
                #end if
                i -= 1
            #end while
        else:
            ip = ":".join(ip)
        #end if

        return ip
    else:
        return False
    #end if
#end def
        
def getIpv4Range(ip_start, ip_end):
    ip_list = []
    ip_start_int = ipv4Toint(ip_start)
    ip_end_int = ipv4Toint(ip_end)

    if ip_start_int > ip_end_int:
        ip_list = False
    elif ip_start_int == ip_end_int:
        ip_list.append(ip_start)
    else:
        for i in range(ip_start_int, ip_end_int+1):
            ip = intToipv4(i)
            ip_list.append(ip)
        #end for
    #end if

    return ip_list
#end def

def getIpv6Range(ip_start, ip_end):
    ip_list = []
    ip_start = fullIpv6(ip_start)
    ip_end = fullIpv6(ip_end)

    if ip_start == False or ip_end == False:
        return False
    #end if
    if ip_start == ip_end:
        ip_list.append(easyIpv6(ip_start))
        return ip_list
    #end if
    if cmp(ip_start,ip_end) == 1:
        return False
    #end if

    ip_org = ""
    i = 0
    for i in range(len(ip_start)):
        if ip_start[i] != ip_end[i]:
            ip_org = ip_start[0:i]
            ip_start = ip_start[i:]
            ip_end = ip_end[i:]
            break
        #end if
    #end for
    if len(ip_start) > 4:
        return False
    #end if
    j = len(ip_start)

    for i in range(hex2dec(ip_start),hex2dec(ip_end)+1):
        t = dec2hex(i)
        t = "0000%s" % (t)
        t = "%s%s" % (ip_org,t[-j:])
        ip_list.append(easyIpv6(t))
    #end for

    return ip_list
#end def

def domainToip(domain):
    try:
        if domain == "":
            return False
        #end if
        if domain.find("://") > 0:
            domain = domain.split("://")[1]
        #end if
        if checkIpv4(domain) or checkIpv6(domain):
            return domain
        #end if
        match = re.findall(u"((\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5]))",domain,re.I)
        if match and len(match) > 0:
            print match
            return match[0][0]
        #end if

        match = re.findall(u"((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?", domain, re.I)
        if match and len(match) > 0:
            
            return match[0][0]
        #end if

        if domain.find(":") > 0:
            if len(domain.split(":") > 2):
                return False
            else:
                domain = domain.split(":")[0]
            #end if
        #end if

        res = socket.getaddrinfo(domain, None)
        if res and len(res) > 0:
            return res[0][4][0]
        #end if

        return False

    except Exception,e:
        logging.getLogger().error("File:common.py, domainToip: %s, domain: %s" % (str(e), domain))
        return False
    #end try
#end def

def ipv6_to_bin(ipv6):
    try:
        tmp = fullIpv6(ipv6)
        if tmp == False:
            return False
        res_ip = ''
        ret = []
        for i in range(len(tmp)):
            if tmp[i] != ':':
                res = dec2bin(int(tmp[i],16))
                res = res[2:]
                a = len(res)
                if a < 4:
                    r = ''
                    for j in range(4-a):
                        r += '0'
                    res += r
                res_ip += res

        return res_ip

    except Exception, e:
        logging.getLogger().error("File:common.py, ipv6_to_bin: %s, ipv6: %s" % (str(e), ipv6))
        return False


def nvs_httplib2_request(http,url, method="GET", body=None, headers=None):
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


def check_ip_port(ip,port):
    try:
        try:
            sk = ''
            if checkIpv6(ip):
                sk = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #end if
            sk.settimeout(1)
            port = int(port)
            sk.connect((ip,port))
            if port == 3306:
                sk.send('test')
                tmp = sk.recv(1024)
                if len(tmp) < 3:
                    sk.close()
                    return False
                #end if
            #end if
            sk.close()
            return True
        except Exception:
            sk.close()
            return False
        #end try
    except Exception:
        return False
    #end try
#end def

def checkPortOpen(ip,port_list):
    try:
        res = []
        for port in port_list:
            if check_ip_port(ip,port):
                res.append(port)
        return res
    except Exception, e:
        logging.getLogger().error("File:common.py, checkPortOpen: %s, ip: %s, port_list: %s" % (str(e), ip, str(port_list)))
        return []

