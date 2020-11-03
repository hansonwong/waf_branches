#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
from Queue import Queue
import threading
from  threading import Thread
import urllib2
import time
import socket
import commands
import os
import sys
import base64
import re
import sys
import logging
import telnetlib
from lib.common import *
from pexpect import *
from lib.waf_netutil import *
from lib.nvs_telnet import *

class WeakScan:
    def __init__(self,task_id):
        try:
            self.conn = ""
            self.cursor = ""
            self.task_id = str(task_id)
            self.user_id = 0
            self.task_name = ""
            self.state = 2
            self.init_state = 1
            self.prescan_state = 1
            self.weak_enable = 1
            self.weak_state = 0
            self.weak_thread = 1
            self.weak_policy = []
            self.weak_timeout = 60*5
            self.compiled_rule = re.compile('\x5b[\d]+\x5d\x5b[\w]+\x5d\s+host:.*.login:.*.password:.*.')

            self.thread_lock = threading.Lock()
            
            self.queue = Queue()
            
            self.asset_scan_id = 0
            
        except Exception,e:
            logging.getLogger().error("File:WeakScan.py, WeakScan.__init__:" + str(e) + ",task id:" + str(task_id))
        #end try
    #end def
    
    def mysqlConnect(self):
        def reconnect():
            self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            if self.conn == '' or self.cursor == '':
                reconnect()
            else:
                try:
                    self.conn.ping()
                except MySQLdb.OperationalError,e:
                    self.mysqlClose()
                    reconnect()
                    logging.getLogger().error("File:WeakScan.py, WeakScan.mysqlConnect reconnect:" + str(e) + ",task id:" + self.task_id)
            #end if
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:WeakScan.py, WeakScan.mysqlConnect:" + str(e) + ",task id:" + self.task_id)
            return False
        #end try
    #end def
    
    def mysqlClose(self):
        try:
            if self.conn != '' and self.cursor != '':
                self.cursor.close()
                self.conn.close()
            #end if
            self.conn = ''
            self.cursor = ''
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:WeakScan.py, WeakScan.mysqlClose:" + str(e) + ",task id:" + self.task_id)
            return False
        #end try
    #end def
    
    def init(self):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = "select t.task_name as task_name,t.asset_scan_id as asset_scan_id,t.state as state, t.init_state as init_state, t.prescan_state as prescan_state,t.weak_enable as weak_enable,t.weak_state as weak_state,t.weak_thread as weak_thread,w.vuls as vuls,t.weak_timeout as weak_timeout,t.user_id as user_id from task_manage t,weak_policy w where t.id = '%s' and t.weak_policy = w.id" % (self.task_id)
            cursor.execute(sql)
            conn.commit()
            res = cursor.fetchone()
            if res and len(res) > 0:
                self.user_id = str(res['user_id'])
                self.task_name = res['task_name'].encode('utf8')
                self.state = res['state']
                self.init_state = res['init_state']
                self.prescan_state = res['prescan_state']
                self.weak_enable = res['weak_enable']
                self.weak_state = res['weak_state']
                self.weak_thread = res['weak_thread']
                self.weak_policy = res['vuls'].split('|')
                self.weak_timeout = res['weak_timeout']
                self.asset_scan_id = res['asset_scan_id']
                
                '''
                if self.state != 2:
                    return False
                #end if
                '''
                
                return True

            else:
                logging.getLogger().error("File:WeakScan.py, WeakScan.init  : mysql connect error ,task id:" + self.task_id)
                return False
            #end if
        except Exception,e:
            logging.getLogger().error("File:WeakScan.py, WeakScan.init:" + str(e) + ",task id:" + self.task_id)
        #end try
    #end def    
    def checkIpPort_ipv6(self,ip,port,type):
        try:
            try:
                sk = ''
                if checkIpv6(ip):
                    sk = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                else:
                    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #end if
                sk.settimeout(5)
                sk.connect((ip,port))
                if type == '6':
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
#modify by yinkun  2014-11-18 inorder to more faster    
    def checkIpPort(self,ip):
        try:
            res = []            
            iface = getIfaceByRoute(ip)
            print 'iface:',iface
            port_list = ''
            cmd_iptype = ''
            cmd = ''
            port_dic = {'21':'ftp','22':'ssh','3389':'rdp','23':'telnet','1433':'mssql','3306':'mysql','1521':'oracle','445':'smb','139':'smb','5900':'vnc'}
            if checkIpv6(ip):
                cmd_iptype = '-6'
            if '1' in self.weak_policy:
                port_list += '21,'       #ftp
            if '2' in self.weak_policy:
                port_list += '22,'       #ssh
            if '3' in self.weak_policy:
                port_list += '3389,'      #3389
            if '4' in self.weak_policy:
                port_list += '23,'         #telnet
            if '5' in self.weak_policy:
                port_list += '1433,'     #mssql
            if '6' in self.weak_policy:
                port_list += '3306,'     #mysql
            if '7' in self.weak_policy:
                port_list += '1521,'     #oracle
            if '8' in self.weak_policy:
                port_list += '445,139,'   #smb
            if '9' in self.weak_policy: 
                port_list += '5900,'     #vnc

            port_list_len = len(port_list)
            if port_list_len > 0:
                port_list = port_list[:port_list_len-1]
                print 'port_list: ',port_list

                if checkIpv6(ip):
                    if iface == "":
                        cmd = "/usr/bin/nmap -6 %s -p %s --host-timeout 30s -P0" % (ip, port_list)
                    else:
                        cmd = "/usr/bin/nmap -6 %s -p %s --host-timeout 30s -P0 -e %s" % (ip, port_list, iface)
                else:
                    if iface == "":
                        cmd = "/usr/bin/nmap -sS %s -p %s --host-timeout 30s -P0" % (ip, port_list)
                    else:
                        cmd = "/usr/bin/nmap -sS %s -p %s --host-timeout 30s -P0 -e %s" % (ip, port_list, iface)
                print cmd
                lines = vulscan_popen(cmd)

                for row in lines:
                    #print 'line:',row
                    if row.find('/tcp') > 0 and row.find('open') > 0:
                        tmp_port = row.split('/tcp')[0]
                        if cmp(tmp_port,'139') == 0 and ('smb' in res):
                            continue
                        res.append(port_dic.get(tmp_port))

                return res
            else:
                return []
        except Exception, e:
            return []
           
    def writelog(self,ip,type,username,password):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            
            if type == "RDP":
                type = "远程协助"
            #end if
            
            sql = ""
            if self.asset_scan_id > 0:
                sql = "select count(*) as c from weak_pwd_details_" + self.task_id + " where `type` = %s and `username` = %s and `password` = %s and `ip` = %s and `asset_scan_id` = '" + str(self.asset_scan_id) + "'"
            else:
                sql = "select count(*) as c from weak_pwd_details_" + self.task_id + " where `type` = %s and `username` = %s and `password` = %s and `ip` = %s "
            #end if
            cursor.execute(sql,(type,username,password,ip))
            conn.commit()
            res = cursor.fetchone()
            if res and len(res) > 0 and res['c'] > 0:
                return
            #end if
            sql = "insert into weak_pwd_details_" + self.task_id + " (`taskid`,`taskname`,`ip`,`type`,`username`,`password`,`asset_scan_id`) values (%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(self.task_id,self.task_name,ip,type,username,password,self.asset_scan_id))
            conn.commit()

            syslog_weak_vul(self.task_id, self.task_name, ip, type, username, password)
        except Exception,e:
            logging.getLogger().error("File:WeakScan.py, WeakScan.writelog:" + str(e) + ",task id:" + self.task_id)
        #end try
    #end def
    
    def new_crack(self, ip ,type):
        try:
            logging.getLogger().debug("File:WeakScan.py, WeakScan.crach:type:%s" % type)

            hydra_type = ""
            if checkIpv6(ip):
                hydra_type = " -6"
            #end if
            
            dic_file = "/var/www/dic/%s_%s.dic" % (type,self.user_id)
            
            f = open(dic_file, "r")
            lines = f.readlines()
            
            start_time = time.time()
            if type == "telnet":
                telnet_check = Telnet_login(ip)
            
            for line in lines:
                
                try:
                    if int(time.time() - start_time) > self.weak_timeout:
                        break
                    #end if
                
                    if type == "vnc":
                        username = ""
                        password = line.strip()
                    
                        password = password.replace("\\", "\\\\")
                        password = password.replace("`", "\\`")
                        password = password.replace("\"", "\\\"")
                    else:
                        up = line.split(":", 1)
                        if len(up) < 2:
                            continue
                        #end if
                        username = up[0].strip()
                        password = up[1].strip()
                    
                        username = username.replace("\\", "\\\\")
                        username = username.replace("`", "\\`")
                        username = username.replace("\"", "\\\"")
                    
                        password = password.replace("\\", "\\\\")
                        password = password.replace("`", "\\`")
                        password = password.replace("\"", "\\\"")
                    #end if
                
                    cmd = ""
                
                    if type == "vnc":
                        if password == "{NULL}":
                            cmd = "/usr/local/bin/hydra %s -t 1 -sid=%s -p \"\" %s %s" % (hydra_type, self.task_id, ip, type)
                        else:
                            cmd = "/usr/local/bin/hydra %s -t 1 -sid=%s -p \"%s\" %s %s" % (hydra_type, self.task_id, password, ip, type)
                        #end if
                    elif type == "oracle":
                        if password == "{NULL}":
                            cmd = "/usr/local/bin/hydra %s -t 1 -sid=%s -l \"%s\" -e n %s %s ORCL" % (hydra_type, self.task_id, username, ip, type)
                        else:
                            cmd = "/usr/local/bin/hydra %s -t 1 -sid=%s -l \"%s\" -p \"%s\" %s %s ORCL" % (hydra_type, self.task_id, username, password, ip, type)
                        #end if
                    else:
                        if password == "{NULL}":
                            cmd = "/usr/local/bin/hydra %s -t 1 -sid=%s -l \"%s\" -e n %s %s" % (hydra_type, self.task_id, username, ip, type)
                        else:
                            cmd = "/usr/local/bin/hydra %s -t 1 -sid=%s -l \"%s\" -p \"%s\" %s %s" % (hydra_type, self.task_id, username, password, ip, type)
                        #end if
                    #end if
                
                    (output, exitstatus) = run(cmd, withexitstatus=1, timeout=20)
                    m = self.compiled_rule.findall(output)
                    if len(m) == 1:
                        i = m[0]
                        s = str(i).replace("\r", "").split(' ')
                        
                        if len(s) < 11:
                            continue
                        #end if
                        if type == "telnet":
                            telnet_passwd = '' if len(s[10]) == 0 else s[10]
                            if not telnet_check.check(s[6],telnet_passwd):
                                continue

                        if len(s[10]) == 0:
                            self.writelog(ip, type.upper(), s[6], "空密码")
                            
                            if type.upper() == "FTP":
                                self.writelog(ip, type.upper(), "ftp", "ftp")
                            #end if
                        else:
                            self.writelog(ip, type.upper(), s[6], s[10])
                        #end if
                        
                        return 

                    #end if
                except Exception,e1:
                    logging.getLogger().error("File:WeakScan.py, WeakScan.new_crack: e1 " + str(e1) + ",task id:" + self.task_id + ",ip:" + ip + ",type:" + type)
                    continue
                #end try
            #end for
        except Exception,e:
            logging.getLogger().error("File:WeakScan.py, WeakScan.new_crack: e " + str(e) + ",task id:" + self.task_id + ",ip:" + ip + ",type:" + type)
        #end try
    #end def
    
    def updateHostState(self,ip):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = ""
            if self.asset_scan_id > 0:
                sql = "update hostmsg_%s set `weak_state` = '1' where `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,ip,self.asset_scan_id)
            else:
                sql = "update hostmsg_%s set `weak_state` = '1' where `ip` = '%s'" % (self.task_id,ip)
            #end if
            cursor.execute(sql)
            conn.commit()
            
            sql = ""
            if self.asset_scan_id > 0:
                sql = "update hostmsg_%s set `end_time` = now() where `port_state` = '1' and `host_state` = '1' and `web_state` = '1' and `weak_state` = '1' and `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,ip,self.asset_scan_id)
            else:
                sql = "update hostmsg_%s set `end_time` = now() where `port_state` = '1' and `host_state` = '1' and `web_state` = '1' and `weak_state` = '1' and `ip` = '%s'" % (self.task_id,ip)
            #end if
            cursor.execute(sql)
            conn.commit()
            
            cursor.close()
            conn.close()
        except Exception,e:
            logging.getLogger().error("File:WeakScan.py, WeakScan.updateHostState:" + str(e) + ",task id:" + self.task_id + ",ip:" + ip)
        #end try
    #end def
    
    def clearResult(self,ip):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = ""
            if self.asset_scan_id > 0:
                sql = "delete from weak_pwd_details_%s where `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,ip,self.asset_scan_id)
            else:
                sql = "delete from weak_pwd_details_%s where `ip` = '%s'" % (self.task_id,ip)
            #end if
            cursor.execute(sql)
            conn.commit()

            conn.close()

        except Exception,e:
            logging.getLogger().error("File:WeakScan.py, WeakScan.clearResult:" + str(e) + ",task id:" + self.task_id + ",ip:" + ip)
        #end try
    #end def
    
    def judgeEnable(self,vul_id):
        if vul_id in self.weak_policy:
            return True
        else:
            return False
        #end if
    #end def

    def updateProgress(self,ip,progress):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = ""
            if self.asset_scan_id > 0:
                sql = "update hostmsg_%s set `weak_progress` = '%s' where `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id, progress, ip, self.asset_scan_id)
            else:
                sql = "update hostmsg_%s set `weak_progress` = '%s' where `ip` = '%s'" % (self.task_id, progress, ip)
            #end if
            cursor.execute(sql)
            conn.commit()

            cursor.close()
            conn.close()
        except Exception,e:
            logging.getLogger().error("File:WeakScan.py, WeakScan.updateProgress: %s, task id: %s, ip: %s" % (str(e), self.task_id, ip))
        #end try
    #end def
    
    def startMain(self):
        try:
            while True:
                if self.queue.qsize() < 1:
                    break
                #end if
                ip = self.queue.get_nowait()
                if ip and ip != "":
                    print "start to check ip : ",ip
                    
                    tmp_list = self.checkIpPort(ip)
                    print 'tmp_list: ',tmp_list
                    progress = 0
                    if tmp_list and len(tmp_list) > 0:
                        add_progress = 100/len(tmp_list)
                        for line in tmp_list:
                            print ip,line
                            self.new_crack(ip, line)
                            progress += add_progress
                            self.updateProgress(ip,str(progress))
  
                    #更新主机状态
                    self.updateProgress(ip,'100')
                    self.updateHostState(ip)
                #end if
            #end while
        except Exception,e:
            logging.getLogger().error("File:WeakScan.py, WeakScan.startMain:" + str(e) + ",task id:" + self.task_id + ",ip:" + ip)
        #end try
    #end def
    
    def startWeakScan(self,type):
        try:
            if self.init():
                conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
                cursor = conn.cursor(MySQLdb.cursors.DictCursor)
                
                #判断初始初始化是否成功
                if self.init_state == 0:
                    logging.getLogger().debug("File:WeakScan.py, WeakScan.startWeakScan: task not init ,task id:" + self.task_id)
                    return
                #end if
                
                #判断是否开启了弱密码扫描
                if self.weak_enable == 0:
                    sql = ""
                    if self.asset_scan_id > 0:
                        sql = "update hostmsg_%s set `weak_state` = '1' where `state` = '1' and `asset_scan_id` = '%s'" % (self.task_id,self.asset_scan_id)
                    else:
                        sql = "update hostmsg_%s set `weak_state` = '1' where `state` = '1'" % (self.task_id)
                    #end if
                    cursor.execute(sql)
                    conn.commit()
                    self.endWeakScan()
                    logging.getLogger().debug("File:WeakScan.py, WeakScan.startWeakScan: weak_enable is 0 ,task id:" + self.task_id)
                    return
                #end if
                
                '''
                if type == "restart":
                    sql = "update hostmsg_%s set `weak_state` = '0'" % (self.task_id)
                    cursor.execute(sql)
                    conn.commit()
                    sql = "delete from weak_pwd_details_%s" % (self.task_id)
                    cursor.execute(sql)
                    conn.commit()
                #end if
                '''
                
                sql = ""
                if self.asset_scan_id > 0:
                    sql = "select `ip` from hostmsg_%s where `weak_state` <> '1' and `asset_scan_id` = '%s'" % (self.task_id,self.asset_scan_id)
                else:
                    sql = "select `ip` from hostmsg_%s where `weak_state` <> '1'" % (self.task_id)
                #end if
                cursor.execute(sql)
                res = cursor.fetchall()
                if res and len(res) > 0:
                    for row in res:
                        self.queue.put(row['ip'])
                    #end for
                #end if
                
                sql = ""
                if self.asset_scan_id > 0:
                    sql = "delete from weak_pwd_details_%s where `asset_scan_id` = '%s' and `ip` in (select `ip` from hostmsg_%s where `weak_state` <> '1' and `asset_scan_id` = '%s')" % (self.task_id,self.asset_scan_id,self.task_id,self.asset_scan_id)
                else:
                    sql = "delete from weak_pwd_details_%s where ip in (select ip from hostmsg_%s where `weak_state` <> '1')" % (self.task_id,self.task_id)
                #end if
                cursor.execute(sql)
                conn.commit()
                
                thread_list = []
                for i in range(self.weak_thread):
                    thread_list.append(Thread(target=self.startMain, args=()))
                #end for
                for t in thread_list:
                    t.start()
                #end for
                for t in thread_list:
                    t.join()
                #end for
                
                self.endWeakScan()
            else:
                logging.getLogger().error("File:WeakScan.py, WeakScan.startWeakScan: init function error ,task id:" + self.task_id)
            #end if
        except Exception,e:
            #self.endWeakScan()
            logging.getLogger().error("File:WeakScan.py, WeakScan.startWeakScan:" + str(e) + ",task id:" + self.task_id)
        #end try
    #end def
    
    def endWeakScan(self):
        try:
            logging.getLogger().debug("File:WeakScan.py, WeakScan.endWeakScan: task come to end ,task id:" + self.task_id)
            current_time = time.strftime("%Y-%m-%d %X",time.localtime())
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            #check weak_state
            
            sql = ""
            if self.asset_scan_id > 0:
                sql = "select count(*) as c from hostmsg_%s where `state` = '1' and `weak_state` <> '1' and `asset_scan_id` = '%s'" % (self.task_id,self.asset_scan_id)
            else:
                sql = "select count(*) as c from hostmsg_%s where `state` = '1' and weak_state <> '1'" % (self.task_id)
            #end if
            cursor.execute(sql)
            conn.commit()
            res = cursor.fetchone()
            if res and len(res) > 0 and res['c'] == 0:
                sql = "update `task_manage` set `weak_state` = '1' where `id` = '%s'" % (self.task_id)
                cursor.execute(sql)
                conn.commit()
            #end if
            
            #check task state and end_time
            sql = "update `task_manage` set `state` = '3', `end_time` = now() where `id` = '%s' and `init_state` = '1' and `prescan_state` = '1' and `port_state` = '1' and `host_state` = '1' and `web_state` = '1' and `weak_state` = '1'" % (self.task_id)
            cursor.execute(sql)
            conn.commit()
            sendEmail(self.task_id)
            updateTaskManage()
            check_if_all_end(self.task_id)
            
            updateAssetCount(self.task_id,self.asset_scan_id)

        except Exception,e:
            logging.getLogger().error("File:WeakScan.py, WeakScan.endWeakScan:" + str(e) + ",task id:" + self.task_id)
        #end try
    #end if
    
#end class 

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    #init_log(logging.DEBUG, logging.DEBUG, os.path.realpath(__file__).split(".")[0] + ".log")
    try:
        '''
        if len(sys.argv) == 2:
            task_id = str(sys.argv[1])
            ob = WeakScan(task_id)
            ob.startWeakScan("")
        else:
            task_id = str(sys.argv[1])
            ob = WeakScan(task_id)
            ob.startWeakScan("restart")
        #end if
        '''
        if len(sys.argv) == 2:
            task_id = str(sys.argv[1].replace("#", ""))
            cmd = "/usr/bin/python /var/waf/WeakScan.py %s#" % (task_id)
            res = checkProcess(cmd)
            if res == False:
                logging.getLogger().error("File:WeakScan.py, __main__: Process: %s is exist" % (cmd))
                sys.exit(0)
            #end if
            
            ob = WeakScan(task_id)
            ob.startWeakScan("")
            #clear oracle log
            os.system("rm -rf /root/oradiag_root")
            os.system("rm -rf /root/hydra.restore")
            os.system("rm -rf /oradiag_root")
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:WeakScan.py, __main__:" + str(e))
    #end try
#end if
