#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import os
import subprocess
import sys
import threading
import logging
import MySQLdb
from Queue import *
import ConfigParser
import time
from lib.common import *
from lib.waf_netutil import *
import signal
import fcntl

import socket
import urllib
import struct
#from progressbar import ydy_progress

NASL_DIR = "/naslscript/plugins/"
#NASL_EXE = "/opt/nessus/bin/nessuscmd"
NASL_EXE = "/opt/nvscan/bin/nvscancmd"
WAF_CONFIG   = "/var/waf/waf.conf"
#HOST = "127.0.0.1"
#USER = "root"
#PASSWD = "yxserver"

cfg    = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
HOST   = cfg.get("mysql","db_ip").replace('"','')
USER   = cfg.get("mysql","db_user").replace('"','')
PASSWD = cfg.get("mysql","db_passwd").replace('"','')

total_exec = 0
total_timeout = 0
total_ok = 0

no_more_target = False

DMI_IP = ""

firewall_vuls = []
enable_firewall_inline = False
firewall_ip = ""
firewall_block_time = 60

asset_scan_id = 0

def waf_popen(cmd):
    
    #logging.getLogger().debug(cmd)
    return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()

#end def

class scan_reulst(object):
    def __init__(self, proto, port, vul_id, output):
        self.proto  = proto
        self.port   = int(port)
        self.vul_id = int(vul_id)
        self.output = output
    #end def
#end class

class vtask(object):
    

    def __init__(self, task_id, name, total_ip, total_finished_ip, last_scan_ip_list, policy_id, vul_file_list, thread_num, script_num, vul_dict, asset_scan_id):
        
        self.task_id         = task_id
        self.name            = name
        self.total_ip        = total_ip
        self.total_finished_ip = total_finished_ip
        self.target_list     = last_scan_ip_list
        self.policy_id       = int(policy_id)
        self.thread_num      = int(thread_num)
        self.vul_file_list   = vul_file_list
        self.script_num      = int(script_num)
        self.total_script    = len(vul_file_list)
        self.vul_dict        = vul_dict
        self.asset_scan_id   = asset_scan_id
        
        
        print len(vul_file_list)
        #sys.exit(0)
        #self.total_need_exec_script_num = self.total_online_ip * self.total_script 
        #---------------------------------------------

    def add_vul(self, ip, s_result):
  
        global ip_result
        global mutex_a
        
        #print "try to add %s, %d" % (ip, int(vul_id))
        
        mutex_a.acquire()
        
        tmp_result = ip_result.get(ip)
        if tmp_result == None:
            ip_result.setdefault(ip, s_result)
        else:
            ip_result[ip] = tmp_result + s_result
        #end if
        
        print ip_result.get(ip)
        
        mutex_a.release()
        
        #print "try to add %s, %d ok" % (ip, int(vul_id))
    #end def
    
    def get_next(self, ip):
        global ip_nextid
        global ip_result
        global mutex_a
        global mutex_b
        mutex_b.acquire()
        
        tmp = ip_nextid.get(ip)
        
        
        if tmp == None:
            tmp = 0
            ip_nextid.setdefault(ip, tmp)
            
        else:
            if int(tmp) >= self.total_script:
                mutex_b.release()
                return -1
            ip_nextid[ip] = int(tmp) + 1

        #end if
        mutex_b.release()
        
        return int(tmp)
        #end if
    #end def
#end class


def get_vul_filename(vul_id):
    try:
        conn = MySQLdb.connect(HOST, USER, PASSWD, db='waf_hw', charset='utf8')

        cur = conn.cursor(MySQLdb.cursors.DictCursor)
    
        sql = "select `filename` from vul_info where vul_id = %d" % int(vul_id)
        cur.execute(sql)      
        re = cur.fetchone()
        
        if re:
            return re["filename"]
        else:
            logging.getLogger().error("get_vul_filename:" + "error vul_id %d, None value!" % vul_id)
            return -1
        #end if
    except Exception,e:
        logging.getLogger().error("File:HostScanTail.py, get_vul_filename:" + str(e) + ",vul_id:" + str(vul_id))
        return -1
#end def

def check_if_log_cve(vul_id):
    
    need_log_cve = []
    need_log_cve.append(3)
    need_log_cve.append(27)
    need_log_cve.append(29)
    need_log_cve.append(31)
    
    try:
        conn = MySQLdb.connect(HOST, USER, PASSWD, db='waf_hw', charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select family from host_family_ref where vul_id = %d" % int(vul_id)
        cur.execute(sql)      
        ret = cur.fetchone()
        
        if int(ret["family"]) in need_log_cve:
            return True
        #end if
    except Exception,e:
        logging.getLogger().error("check_if_log_cve:vul_id = %d" % int(vul_id))
    #end try
    
    return False


def task_inits(task_id):
    try:
        global asset_scan_id;
        
        conn = MySQLdb.connect(HOST, USER, PASSWD, db='waf_hw', charset='utf8')

        cur = conn.cursor(MySQLdb.cursors.DictCursor)
    
        sql = "select * from task_manage where id = %d" % int(task_id)
        cur.execute(sql)      
        re = cur.fetchone()
        
        enable_ddos = 0
        
        if re:
            task_name = re["task_name"]
            asset_scan_id = re["asset_scan_id"]
            thread_num = int(re["host_thread"])
            enable_ddos = int(re["enable_ddos"])
            
            if thread_num > 10:
                thread_num = 10
            #end if
            script_num = int(re["host_max_script"])
        else:
            logging.getLogger().error("task_init:" + "error task id, there is no taskid = %d" % int(task_id))
            return -1
        #end if

        sql = ""

        if not table_exists("vul_details_%d"%(int(task_id))):
            if asset_scan_id > 0:
                # sql = "select count(*) as c from hostmsg_%d where `asset_scan_id` = '%d'" % (int(task_id), asset_scan_id)
                sql = "select ip from hostmsg_%d where `asset_scan_id` = '%d'"%(int(task_id), asset_scan_id)
            else:
                sql = "select ip from hostmsg_%d"%(int(task_id))
            #end if
        else:
            if asset_scan_id > 0:
                # sql = "select count(*) as c from hostmsg_%d where `asset_scan_id` = '%d'" % (int(task_id), asset_scan_id)
                sql = "select ip from hostmsg_%d where ip not in (select ip from vul_details_%d where `asset_scan_id` = '%d' group by ip) and `asset_scan_id` = '%d'"%(int(task_id), int(task_id), asset_scan_id, asset_scan_id)
            else:
                sql = "select ip from hostmsg_%d where ip not in (select ip from vul_details_%d group by ip)"%(int(task_id), int(task_id))
            #end if
        cur.execute(sql)      
        re = cur.fetchall() 
        
        total_ip = len(re)
        
        # sql = ""
        # if asset_scan_id > 0:
        #     sql = "select count(*) as c from hostmsg_%d where `asset_scan_id` = '%d' and (`host_state` = 1 or `state` = 0)" % (int(task_id),asset_scan_id)
        # else:
        #     sql = "select count(*) as c from hostmsg_%d where `host_state` = 1 or `state` = 0" % int(task_id)
        # #end if
        # cur.execute(sql)      
        # re = cur.fetchone() 
        
        total_finished_ip = 0
        
        
        last_scan_ip_list = Queue()
        if re:
            for ip in re:
                last_scan_ip_list.put(ip["ip"])

        
        # sql = ""
        # if asset_scan_id > 0:
        #     sql = "select `ip` from hostmsg_%d where `asset_scan_id` = '%d' and `host_state` = 2" % (int(task_id),asset_scan_id)
        # else:
        #     sql = "select `ip` from hostmsg_%d where `host_state` = 2" %  int(task_id)
        # #end if
        # cur.execute(sql)      
        # re = cur.fetchall() 
        
        # if re:
        #     for ip in re:
        #         last_scan_ip_list.put(ip["ip"])
        #     #end for
        # #end if

        sql = "select `host_policy` from task_manage where id = %d" % int(task_id)
        cur.execute(sql)      
        re = cur.fetchone()
        
        if re:
            policy_id = int(re["host_policy"])
        else:
            logging.getLogger().error("task_init:" + "error host_policy, None value!")
            return -1
        #end if
        
        sql = "select `vul_id` from host_policy_ref where policy_id = %d" % int(policy_id)
        cur.execute(sql)      
        re = cur.fetchall() 
        
        if re:
            pass
        else:
            logging.getLogger().error("task_init:" + "error policy id, None value!")
            return -1
        #end if
        
        sql = "select `vul_id` from vul_info where ddos = 1"
        cur.execute(sql)      
        ddos_vul_id = cur.fetchall()
        ddos_vul_ids = []
        for i in ddos_vul_id:
            ddos_vul_ids.append(int(i["vul_id"]))
        #end for
        
        vul_list = []
        
        tmpdict = {}
        
        tmpcount = 0
        tmpvulstr = ""

        #print vuls
        for vul in re:
            
            if tmpcount > 20000:
                vul_list.append(tmpvulstr)
                tmpvulstr = ""
                tmpcount = 0
           
                continue
            else:
                if enable_ddos == 0 and int(vul["vul_id"]) in ddos_vul_ids:
                    continue
                #end if
                
                if tmpcount == 0:
                    tmpvulstr = str(vul["vul_id"])
                else:
                    tmpvulstr = tmpvulstr + "," + str(vul["vul_id"])
                #end if
            tmpcount = tmpcount + 1
        #end for
        
        #logging.getLogger().error("vulstr len :" + str(len(tmpvulstr)))
        # res = ''
        # sql = "select `vul_id` from vul_info_dep"
        # try:
        #     cur.execute(sql)
        #     res = cur.fetchall()
        # except Exception, e:
        #     logging.getLogger().error("File:HostScanTail.py, task_init, vul_info_dep:" + str(e) + ",task_id:" + str(task_id))
        #     res = None
        
        # if res:
        #     for item in res:
        #         tmpvulstr = tmpvulstr + "," + str(item.get('vul_id'))
        
        vul_list.append(tmpvulstr)
        
        task = vtask(task_id, task_name, total_ip,total_finished_ip, last_scan_ip_list, policy_id, vul_list, thread_num, script_num, tmpdict, asset_scan_id)
        
        return task
    
    except Exception,e:
        logging.getLogger().error("File:HostScanTail.py, task_init:" + str(e) + ",task_id:" + str(task_id))
        return -1
#end def

def exe_nasl(ip, offset):
    #from send_udp import send_udp_thread
    
    #s_thread = send_udp_thread(ip)
    #s_thread.start()
    
    cmd = NASL_EXE + " -sS -p 1-9999 -V -i " + offset + " " + ip
    # logging.getLogger().error(cmd)
    #print cmd
    popen_data = waf_popen(cmd)
    #s_thread.stop()
    print popen_data
    ree = handle_result(popen_data)
    
    for r in ree:
        print r.vul_id,
        print r.proto,
        print r.port
        #print r.output
    
    tmp_task.add_vul(ip, ree)
#end def

def dump_task(tmp_task):
    print "task name:",
    print tmp_task.name
    print "target list:",
    
    while tmp_task.target_list.empty() == False:
        print tmp_task.target_list.get()
    print "policy id:",
    print tmp_task.policy_id
    print "thread num:",
    print tmp_task.thread_num
    print "script num:",
    print tmp_task.script_num
    print "vul scripts:"
    print tmp_task.vul_file_list
#end def

class script_scan_thread(threading.Thread):
    
    def __init__(self, scan_id, offset, ip):
        threading.Thread.__init__(self)
        self.scan_id = scan_id
        self.offset = offset
        self.ip = ip
    #end def
    
    def run(self):
        #print "scan thread:%d, script thread:%d, ip:%s" % (self.scan_id, self.id, self.ip)
        

        

        #print time.ctime()
        exe_nasl(self.ip, self.offset)
        #print time.ctime()
"""
        while True:
            offset = tmp_task.get_next(self.ip)
            if offset == -1:
                return
            #end if
            #mybar.set_progress(self.ip, -1)
            import time
            print time.ctime()
            exe_nasl(self.ip, offset)
"""   
            
            
    #end def
    
#end class



class vul_scan_thread(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id
    #end def
    
    def run(self):
        #print self.id
        global tmp_task
        global no_more_target
        
        try:
            while True:
            #while tmp_task.target_list.empty() == False and check_prescan() == False:
                
                if tmp_task.target_list.empty() == False:
                    
                    try:
                        ip = tmp_task.target_list.get_nowait()
                    except Exception,e:
                        continue
                    #end try
                    
                    
                    script_threads = []
                    
                    
                    for offset in tmp_task.vul_file_list:
                        script_threads.append(script_scan_thread(self.id, offset, ip))
                    #end for
                    for t in script_threads:
                        t.start()
                    #end for
            
                    for t in script_threads:
                        t.join()
                    #end for
                    
                    
                    update_results(ip)
                # elif no_more_target == False:
                #     time.sleep(1)
                else:
                    break
                #end if
            #end while
        except Exception,e:
            logging.getLogger().error("File:HostScanTail.py, vul_scan_thread.run:" + str(e) + ",id:" + str(self.id))
            
        #end while
    #end def
#end class


def write_weak_logs(task_id, task_name, ip, type, username, password, asset_scan_id, port, proto):
    try:
        conn = MySQLdb.connect(host, user, passwd , db = 'waf_hw', charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = ""
        if asset_scan_id > 0:
            sql = "select count(*) as c from weak_pwd_details_" + task_id + " where `type` = %s and `username` = %s and `password` = %s and `ip` = %s and `asset_scan_id` = '" + str(asset_scan_id) + "'"
        else:
            sql = "select count(*) as c from weak_pwd_details_" + task_id + " where `type` = %s and `username` = %s and `password` = %s and `ip` = %s"
        #end if
        
        cursor.execute(sql,(type,username,password,ip))
        conn.commit()
        res = cursor.fetchone()
        if res and len(res) > 0 and res['c'] > 0:
            return
        #end if
        
        
        sql = "insert into weak_pwd_details_" + task_id + " (`taskid`,`taskname`,`ip`,`type`,`username`,`password`,`asset_scan_id`, `port`, `proto`) values (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,(task_id,task_name,ip,type,username,password,str(asset_scan_id), port, proto))
        conn.commit()

        #syslog_weak_vul(self.task_id, self.task_name, ip, type, username, password)
    except Exception,e:
        logging.getLogger().error("File:HostScanTail.py, write_weak_logs:" + str(e))
    #end try
#end def

def strip_vul_list(vul_list):
    tmp = []
    
    ret = []
    
    for i in vul_list:
        if (str(i.vul_id) + "#" + str(i.port)) not in tmp:
            ret.append(i)
            
            tmp.append(str(i.vul_id) + "#" + str(i.port))
        else:
            continue
        #end if
    #end for
    
    return ret
#end def
       
def update_results(ip):
    
    global ip_result
    global DMI_IP
    
    task_id   = tmp_task.task_id
    task_name = tmp_task.name
    asset_scan_id = tmp_task.asset_scan_id
    
    logging.getLogger().debug("update_results func enter.")
    try:
        conn = MySQLdb.connect(HOST, USER, PASSWD, db='waf_hw', charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        ##...0 update host_process in task_manager
        
        sql = ""
        if asset_scan_id > 0:
            sql = "select count(*) from hostmsg_%d where `asset_scan_id` = '%d' and (`state` = 0 or `host_state` = 1)" % (int(task_id),asset_scan_id)
        else:
            sql = "select count(*) from hostmsg_%d where `state` = 0 or `host_state` = 1" % int(task_id)
        #end if
        cur.execute(sql)
        re = cur.fetchone()
        
        tmpfinished = int(re["count(*)"])
        
        ##...1 update task_summary
        vul_list = ip_result.get(ip)
        ##...2 insert vul_details
        
        vul_list = strip_vul_list(vul_list)
        ison = False
        if vul_list:
            ison = True
            for vul in vul_list:
                
                print vul.vul_id

 
                if int(vul.vul_id)  == 41028: #snmp public
                    write_weak_logs(str(task_id),task_name,ip,"SNMP默认团体名","public","public",asset_scan_id, vul.port, vul.proto)                    
                    #continue
                #end if
 
                if int(vul.vul_id)  == 10660: #oracle tnslsnr
                    write_weak_logs(str(task_id),task_name,ip,"ORACLE","tnslsnr","空密码",asset_scan_id, vul.port, vul.proto)
                    #continue
                #end if
                
                if int(vul.vul_id)  == 17162: #Sybase
                    write_weak_logs(str(task_id),task_name,ip,"Sybase","SA","空密码",asset_scan_id, vul.port, vul.proto)  
                    #continue
                #end if
                
                if int(vul.vul_id)  == 10481: #mysql
                    write_weak_logs(str(task_id),task_name,ip,"MYSQL","root","空密码",asset_scan_id, vul.port, vul.proto)        
                    #continue
                #end if
                    
                sql = "select * from vul_info where vul_id = %d" % int(vul.vul_id)
  
                cur.execute(sql)
                re = cur.fetchone()
                
                if re:
                    tmp_factor = re["risk_factor"].encode("utf8").decode("utf8")

                    tmp_name   = MySQLdb.escape_string(re["vul_name_cn"].encode("utf8")).decode("utf8")
                  
                    tmp_desc   = MySQLdb.escape_string(re["desc_cn"].encode("utf8")).decode("utf8")
                    tmp_solu   = MySQLdb.escape_string(re["solu_cn"].encode("utf8")).decode("utf8")
                    tmp_ref    = MySQLdb.escape_string(re["ref_cn"].encode("utf8")).decode("utf8")
                    #tmp_family = MySQLdb.escape_string(re["family"].encode("utf8")).decode("utf8")
                    
                    sql = "select `desc` from host_family_list where id = (select family from host_family_ref where vul_id = %d)" % int(vul.vul_id)
                    cur.execute(sql)
                    tmp_family = cur.fetchone()
                    if tmp_family:
                        tmp_family = MySQLdb.escape_string(tmp_family["desc"].encode("utf8")).decode("utf8")
                    else:
                        tmp_family = ""
                    #end if
                    
                    tmp_cve    = MySQLdb.escape_string(re["cve"])

                    if re["cnnvd"] is None:
                        tmp_cnnvd = ""
                    else:
                        tmp_cnnvd = MySQLdb.escape_string(re["cnnvd"])
                    #end if
                    
                    if re["cnvd"] is None:
                        tmp_cnvd = ""
                    else:
                        tmp_cnvd = MySQLdb.escape_string(re["cnvd"])
                    #end if
                    
                    if int(re["output_enable"]) == 1:
                        tmp_output    = MySQLdb.escape_string(vul.output)
                    else:
                        tmp_output    = ""
                    #end if
                    
                    if re["metasploit"]:
                        tmp_metasploit = MySQLdb.escape_string(re["metasploit"])
                    else:
                        tmp_metasploit = ""
                    #end if
                    
                    global firewall_vuls
                    if enable_firewall_inline:
                        if int(vul.vul_id) in firewall_vuls:
                            
                            global firewall_block_time
                            block_ip(firewall_ip, ip, int(vul.port), vul.proto, tmp_name.encode("utf8"), firewall_block_time)
                        #end if
                    #end if
                    
                    INSERT_RAW_VUL_INFO = True
                    
                    if check_if_log_cve(vul.vul_id) and len(tmp_cve.strip().split(",")) > 1:
                        #ob['family_id'] = 
                        
                        #logging.getLogger().error(tmp_cve.strip())
                        ob = {}
                        ob['cve'] = tmp_cve.strip()
                        ob['task_id'] = str(task_id)
                        ob['family'] = tmp_family
                        ob['port'] = str(vul.port)
                        ob['proto'] = vul.proto
                        ob['ip'] = ip
                        ob['risk_factor'] = tmp_factor
                        if int(re["output_enable"]) == 1:
                            ob['output'] = vul.output
                        else:
                            ob['output'] = ''
                        #end if
                        ob['metasploit'] = tmp_metasploit
                        ob['asset_scan_id'] = asset_scan_id
                        if updateCveResult(ob):
                            INSERT_RAW_VUL_INFO= False
                            
                    #end if
             
                    #logging.getLogger().error("111111111111111111,ip:"+ip)
                    try:
                        syslog_task_name = task_name.encode("utf8")
                        syslog_vul_name_cn = re["vul_name_cn"].encode("utf8")
                        syslog_family = re["family"].encode("utf8")
                        syslog_risk_factor = re["risk_factor"].encode("utf8")
                        syslog_url = "https://" + DMI_IP + "/" + re["vul_index"] + ".html"
                        syslog_host_vul(task_id, syslog_task_name, ip, str(vul.port), vul.proto, syslog_vul_name_cn, syslog_family, syslog_risk_factor, syslog_url)
                    except Exception,e1:
                        logging.getLogger().error("function syslog_host_vul exception:" + str(e1))
                    #end try
                    #logging.getLogger().error("222222222222222222222,ip:"+ip)
                    if INSERT_RAW_VUL_INFO:
                        sql = "select count(*) as c from vul_details_%d where ip = '%s' and vul_id = '%d' and port = '%d' and proto = '%s' and asset_scan_id = '%d'" % (task_id,ip,int(vul.vul_id),int(vul.port),vul.proto,asset_scan_id)
                        cur.execute(sql)
                        res = cur.fetchone()
                        if res['c'] <= 0:
                            #logging.getLogger().error("3333333333333333333333,ip:"+ip)
                            sql = "insert into vul_details_%d values(0, '%s', %d, '%s', '%s', '%s', '%s', '%s', '%s',  '%s',  '%s',  '%s',  '%s', %d, '%s', '%s', '%d')"\
                                % (task_id, ip, int(vul.vul_id), tmp_cve, tmp_cnvd, tmp_cnnvd, tmp_factor, tmp_name, tmp_desc, tmp_solu, tmp_ref, tmp_output.decode("utf8"), tmp_family, int(vul.port), vul.proto, tmp_metasploit, asset_scan_id)
                            cur.execute(sql)
                            conn.commit()
                        #end if
                    #end if
                    
                #end if
            #end for
        #end if
        else:
            ison = False
        ##...3 insert host_vul
        pass
        
        ##...4 update host_msg
        sql = ""
        if asset_scan_id > 0:
            if ison:
                sql = "update hostmsg_%d set `host_state` = 1, state = 1 where `ip` = '%s' and asset_scan_id = '%d'" % (task_id, ip, asset_scan_id)
            else:
                sql = "update hostmsg_%d set `host_state` = 1 where `ip` = '%s' and asset_scan_id = '%d'" % (task_id, ip, asset_scan_id)
        else:
            if ison:
                sql = "update hostmsg_%d set host_state = 1, state = 1 where ip = '%s'" % (task_id, ip)
            else:
                sql = "update hostmsg_%d set host_state = 1 where ip = '%s'" % (task_id, ip)
        #end if
        cur.execute(sql)
        conn.commit()
            
    except Exception,e:
        logging.getLogger().error("File:HostScanTail.py, update_results:" + str(e) + ",ip:" + str(ip))
    #end try

#end def


def check_vulid(vulid):
    try:
        conn = MySQLdb.connect(HOST, USER, PASSWD, db='waf_hw', charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select `enable`, `chs` from vul_info where vul_id = %d" % int(vulid)
        cur.execute(sql)
        re = cur.fetchone()
        
        if re and int(re["enable"]) == 1 and int(re["chs"]) == 1:
            return True
        else:
            return False
    except Exception,e:
        logging.getLogger().error("File:HostScanTail.py, check_vulid:" + str(e) + ",vulid:" + str(vulid))
    #end try
#end def

def func(m):
    import re

    tmp = re.sub(r"\s", "", m.group(1)).strip()
    """
    logging.getLogger().debug(tmp)

    
    logging.getLogger().debug("".join(base64.decodestring(tmp).split("\n")))
  
    """
    return "".join(base64.decodestring(tmp).split("\n"))

def output_decode(data):
    
    try:
        import re
        p = re.compile("#YB64#([\s\S]*?)#YB64#")
        
        return p.sub(func, data)
    
    except Exception,e:
        logging.getLogger().error("File:HostScanTail.py, output_decode:" + str(e) + ",data:" + str(data))
        return ""
    #end try
#end def
    
def handle_result(popen_data):
    """
    f = open("./re", "a")
    f.writelines(popen_data)
    f.close()
    """
    
    return_result = []
    datalist = []
    #tmp = waf_popen(NASL_EXE + " -V -i 11011,10114,11197,26920,10150,35362,10281,10287,10114,11197,45004,42052,48244,41014,34477,10107,43111,22964" + " 192.168.9.104")
    for l in popen_data:
        if l.split():
            datalist.append(l.strip())
        #end if
    #end for

    
    data = "\n".join(datalist)
    data = data.replace("\n|", "\n")
    
    import re

    datalist = data.split("\n-")
    datalist.pop(0)

    tmp = []
    p = re.compile(r'\n{2,}')
    
    for i in datalist:
        tmp.append(p.sub("\n", i))
    #end for
    
    datalist = tmp
    
    for item in datalist:
        items = item.split("\n")
        
        first_line = items[0].strip()
        
        p1 = re.compile(r"^(.+) information")
        p2 = re.compile(r"^Port.+\((.+)\)")
        
        if len(p1.findall(first_line)) == 1:
            proto = p1.findall(first_line)[0]
            port = 0
        elif len(p2.findall(first_line)) == 1:
            proto = p2.findall(first_line)[0].split("/")[1]
            port  = p2.findall(first_line)[0].split("/")[0]
        else:
            proto = ""
            port = 0
        #end if

        p = re.compile(r"Plugin ID (\d{1,6})")
        
        vul_ids = p.findall(item)
        if len(vul_ids) > 0:
            vul_num = len(vul_ids)

            p = re.compile(r"Plugin ID ([\s\S]*?)(?:\[.\]|$)")
            
            
            #print item
            vul_datas = p.findall(item)
            
            if len(vul_datas) == vul_num:
                
                p = re.compile(r"Plugin output :([\s\S]*?)(?:CVE|$)")
                for vul_data in vul_datas:
                    #print type(vul_data)
                    
                    vul_output = p.findall(vul_data)
                 
                    if len(vul_output) == 1:
                        vul_output = output_decode(vul_output[0])
                    else:
                        vul_output = ""
                    #end if
                    
                    vul_id = vul_ids[vul_datas.index(vul_data)]
                    
                    return_result.append(scan_reulst(proto, int(port), int(vul_id), vul_output))
                    """
                    if check_vulid(int(vul_id)) == True:
                    
                        try:
                            return_result.append(scan_reulst(proto, int(port), int(vul_id), vul_output))
                        except Exception,e:
                            pass
                        #end try
                    #end if
                    """
                #end for
            #end if
        #end if
    #end for
    
    return return_result
#end def


        
def main(taskid):
    global ip_result
    global ip_nextid
    ip_result = {}
    ip_nextid = {}
    
    global mutex_a
    global mutex_b
    
    #global DMI_IP
    global tmp_task
    mutex_a = threading.Lock()
    mutex_b = threading.Lock()
    
    mutex_exec    = threading.Lock()
    mutex_timeout = threading.Lock()
    
    
    tmp_task = task_inits(taskid)
    
    #mybar = ydy_progress("#", 30)
    import time
    
    t_start = time.time()
    if tmp_task != -1:
        #dump_task(tmp_task)
        #sys.exit(0)
        asset_scan_id = tmp_task.asset_scan_id
        
        scan_threads = []
        
        for i in range(0, tmp_task.thread_num):
            scan_threads.append(vul_scan_thread(i))
        #end for

        for t in scan_threads:
            t.start()
        #end for
        
        for t in scan_threads:
            t.join()
