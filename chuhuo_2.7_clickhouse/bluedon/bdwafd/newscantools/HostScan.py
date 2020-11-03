#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import os
import sys
import threading
import logging
import MySQLdb
from Queue import *
import ConfigParser
from lib.common import *
from lib.waf_netutil import *

import socket
import urllib

from nvscan_xmlrpc import *
import time
from random import randint
from NvscanReport import *
from output import *
reload(sys)
sys.setdefaultencoding( "utf-8" )

################################
#author: yuying xia
#2013-12-05 complete scan task and get report
#
#TO-DO
#1.Support pause scan and resume scan --2013-12-06 added but not test ---2013-12-09 done
#2.Support stop scan                  --2013-12-06 added but not test ---2013-12-09 done
#3.Add clear task function            --2013-12-06 added but not test 
#4.Add parse report and update scan result function -----2013-12-13 done by jie shen
################################

WAF_CONFIG   = "/var/waf/waf.conf"

cfg    = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
HOST   = cfg.get("mysql","db_ip").replace('"','')
USER   = cfg.get("mysql","db_user").replace('"','')
PASSWD = cfg.get("mysql","db_passwd").replace('"','')

firewall_vuls = []
enable_firewall_inline = False
firewall_ip = ""
firewall_block_time = 60

db = None

# def init_log(console_level, file_level, logfile):
#     formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
#     logging.getLogger().setLevel(logging.INFO)
    
#     console_log = logging.StreamHandler()
#     console_log.setLevel(console_level)
#     console_log.setFormatter(formatter)
    
#     file_log = logging.FileHandler(logfile)
#     file_log.setLevel(file_level)
#     file_log.setFormatter(formatter)

#     logging.getLogger().addHandler(file_log)
#     logging.getLogger().addHandler(console_log)
# #end def

class scan_reulst(object):
    def __init__(self, proto, port, vul_id, output):
        self.proto  = proto
        self.port   = int(port)
        self.vul_id = int(vul_id)
        self.output = output
    #end def
#end class

class vtask(object):
    def __init__(self, task_id, task_name, ip_list, policy_id, asset_scan_id, scan_uuid, timeout):
        
        self.task_id         = task_id
        self.task_name       = task_name
        self.target_list     = ip_list
        self.policy_id       = int(policy_id)
        self.asset_scan_id   = asset_scan_id
        #for xmlrpc
        self.scan_uuid       = scan_uuid
        self.time_out        = timeout
#end class

class db_manager:
    """docstring for db_manager"""
    def __init__(self):
        try:
            self._connect()
        except Exception, e:
            ERROR("db_manager.__init__:"+str(e))

    def __del__(self):
        try:
            self.conn.close()
        except Exception, e:
            ERROR("db_manager.__del__:"+str(e))

    def _connect(self):
        try:
            self.conn = MySQLdb.connect(HOST, USER, PASSWD, db='waf_hw', charset='utf8')
            self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
        except Exception, e:
            ERROR("db_manager._connect:"+str(e))

    def _check_connect(self):
        try:
            self.conn.ping()
        except Exception, e:
            ERROR("db_manager._check_connect:"+str(e) + "--will reconnect.")
            time.sleep(10)
            self._connect()

    def _execute(self,sql, args=None):
        try:
            if not args:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, args)
            self.conn.commit()
        except Exception, e:
            self._check_connect()
            if not args:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, args)
            self.conn.commit()

    def get_one_item_from_db(self, sql):
        try:
            if not sql:
                return None
            self._execute(sql)
            return self.cur.fetchone()
        except Exception, e:
            ERROR("db_manager.get_one_item_from_db:"+str(e)+'##'+str(self.conn)+str(self.cur))
            return -1

    def get_all_item_from_db(self, sql):
        try:
            if not sql:
                return None
            self._execute(sql)
            return self.cur.fetchall()
        except Exception, e:
            ERROR("db_manager.get_all_item_from_db:"+str(e))

    def get_one_item_from_db_by_args(self, sql, args):
        try:
            self._execute(sql, args)
            return self.cur.fetchone()
        except Exception, e:
            ERROR("db_manager.get_one_item_from_db_by_args:"+str(e))

    def set_item_to_db(self, sql):
        try:
            DEBUG('set_item_to_db:' + sql)
            self._execute(sql)
        except Exception, e:
            ERROR("db_manager.set_item_to_db:"+str(e))

    def safe_execute(self,sql, args=None):
        try:
            if not args:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, args)
        except Exception, e:
            self._check_connect()
            if not args:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, args)

    def set_item_to_db_safe(self, sql):
        try:
            self.safe_execute(sql)
        except Exception, e:
            ERROR("db_manager.set_item_to_db_safe:"+str(e))

    def commit_trans(self):
        try:
            self.conn.commit()
        except Exception, e:
            ERROR("db_manager.commit_trans:"+str(e))

    def set_item_to_db_by_args(self, sql, args):
        try:
            self._execute(sql, args)
        except Exception, e:
            ERROR("db_manager.set_item_to_db_by_args:"+str(e))

def check_if_log_cve(dbh, vul_id):
    
    need_log_cve = []
    need_log_cve.append(3)
    need_log_cve.append(27)
    need_log_cve.append(29)
    need_log_cve.append(31)
    
    try:
        sql = "select family from host_family_ref where vul_id = %d" % int(vul_id)
        ret = dbh.get_one_item_from_db(sql)
        
        if int(ret["family"]) in need_log_cve:
            return True
        #end if
    except Exception,e:
        logging.getLogger().error("check_if_log_cve:vul_id = %d" % int(vul_id))
    #end try
    return False

def task_init(task_id):
    try:
        sql = "select * from task_manage where id = %d" % int(task_id)
        re = db.get_one_item_from_db(sql)

        #Set default value
        timeout = 10

        if re:
            task_name = re["task_name"]
            asset_scan_id = re["asset_scan_id"]
            scan_uuid = re.get('scan_uuid')
            timeout = re.get('host_timeout')
            #end if
        else:
            logging.getLogger().error("task_init:" + "error task id, there is no taskid = %d" % int(task_id))
            return -1
        #end if
        ip_list = Queue()
        policy_id = -1
        nvscan_policy_id = -1
        task = -1
        #Step 1. get ip list
        sql = ""
        if asset_scan_id > 0:
            sql = "select `ip` from hostmsg_%d where `asset_scan_id` = '%d'" % (int(task_id),asset_scan_id)
        else:
            sql = "select `ip` from hostmsg_%d" %  int(task_id)
        res = db.get_all_item_from_db(sql)
        if res:
            for item in res:
                ip_list.put(item.get('ip'))

        #Step 2. get policy id
        sql = "select `host_policy` from task_manage where id = %d" % int(task_id)
        res = db.get_one_item_from_db(sql)
        if res:
            policy_id = int(res.get("host_policy"))
        else:
            ERROR("task_init:" + "error host_policy, None value!")
            return -1

        sql = 'select `nvscan_policy_id` from host_policy where `id` = %d'% (policy_id)
        res = db.get_one_item_from_db(sql)
        if res:
            nvscan_policy_id = int(res.get('nvscan_policy_id'))
        else:
            ERROR("task_init:" + "error nvscan_policy_id, None value!")
            return -1

        if nvscan_policy_id <= 0:
            ERROR("task_init:" + "error nvscan_policy_id is -1, not a valid value! Will use default policy, -1.")
            cmd = "python /var/waf/nvscan_policy_manager.py add %s#" % (str(policy_id))
            vulscan_popen(cmd)

        res = db.get_one_item_from_db(sql)
        if res:
            nvscan_policy_id = int(res.get('nvscan_policy_id'))

        task = vtask(task_id, task_name, ip_list, nvscan_policy_id, asset_scan_id, scan_uuid, timeout)

        return task
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, task_init:" + str(e) + ",task_id:" + str(task_id))
        return -1
#end def

def check_prescan(task_id):
    try:
        sql = "select `prescan_state` from task_manage where id = %d" % (int(task_id))
        re = db.get_one_item_from_db(sql)
        if re:
            if int(re["prescan_state"]) == 1:
                return True
            else:
                return False
        else:
            return False
        #end if
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, check_prescan:" + str(e) + ",task_id:" + str(task_id))
        return False
    #end try
#end def

def write_weak_log(dbh, task_id, task_name, ip, stype, username, password, asset_scan_id, port, proto):
    try:
        sql = ""
        if asset_scan_id > 0:
            sql = "select count(*) as c from weak_pwd_details_" + task_id + " where `type` = %s and `username` = %s and `password` = %s and `ip` = %s and `asset_scan_id` = '" + str(asset_scan_id) + "'"
        else:
            sql = "select count(*) as c from weak_pwd_details_" + task_id + " where `type` = %s and `username` = %s and `password` = %s and `ip` = %s"
        #end if
        
        res = dbh.get_one_item_from_db_by_args(sql, (stype, username, password, ip))
        if res and len(res) > 0 and res['c'] > 0:
            return
        #end if
        
        sql = "insert into weak_pwd_details_" + task_id + " (`taskid`,`taskname`,`ip`,`type`,`username`,`password`,`asset_scan_id`, `port`, `proto`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        dbh.set_item_to_db_by_args(sql, (task_id,task_name,ip,stype,username,password,str(asset_scan_id), port, proto))
        #syslog_weak_vul(self.task_id, self.task_name, ip, type, username, password)
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, write_weak_log:" + str(e))
    #end try
#end def

def func(m):
    import re
    tmp = re.sub(r"\s", "", m.group(1)).strip()
    # logging.getLogger().debug(tmp)
    # logging.getLogger().debug("".join(base64.decodestring(tmp).split("\n")))
    return "".join(base64.decodestring(tmp).split("\n"))

def output_decode(data):
    try:
        import re
        p = re.compile("#YB64#([\s\S]*?)#YB64#")
        return p.sub(func, data)
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, output_decode:" + str(e) + ",data:" + str(data))
        return ""
    #end try
#end def


def update_hostinfo(dbh, info):
    try:
        global tmptask
        task_id = str(tmptask.task_id)
        asset_scan_id = tmptask.asset_scan_id
    
        list = []
        
        try:
            new_dict = {}
            if asset_scan_id > 0:
                sql = "select ip, mac_address, os, `state` from hostmsg_%s where asset_scan_id = '%d'" % (task_id,asset_scan_id)
            else:
                sql = "select ip, mac_address, os, `state` from hostmsg_%s" % (task_id)
            #end if
            res = dbh.get_all_item_from_db(sql)
            for row in res:
                new_dict[row['ip']] = {'ip':row['ip'],'mac_address':row['mac_address'],'os':row['os'],'state':row['state']}
            #end for
        except Exception,e1:
            logging.getLogger().error("File:HostScan.py, update_hostinfo 111111:" + str(e1))
        #end try
        
        try:
            for row in info:
                '''
                for k in row.keys():
                    logging.getLogger().debug("File:HostScan.py, update_hostinfo, key:%s, value:%s" % (k,row[k]))
                #end for
                '''
                if new_dict.has_key(row['ip']):
                    t = {'ip':row['ip']}
                    if new_dict[row['ip']]['mac_address'] == row['mac_address'] and new_dict[row['ip']]['os'] == row['os'] and row['mac_address'] == '' and row['os'] == '' and str(new_dict[row['ip']]['state']) == '1':
                        continue
                    #end if
                    if new_dict[row['ip']]['mac_address'] != row['mac_address'] and row['mac_address'] != '':
                        t['mac_address'] = row['mac_address']
                    #end if
                    if new_dict[row['ip']]['os'] != row['os'] and row['os'] != '':
                        t['os'] = row['os']
                    #end if
                    t['state'] = 1
                    list.append(t)
                #end if
            #end for
        except Exception,e2:
            logging.getLogger().error("File:HostScan.py, update_hostinfo 222222:" + str(e2))
        #end try
        
        try:
            for row in list:
        
                if len(row.keys()) < 2:
                    continue
                #end if
        
                sql = "update hostmsg_%s set " % (task_id)
                if row.has_key('mac_address'):
                    sql += " mac_address = '%s'," % (row['mac_address'])
                #end if
                if row.has_key('os'):
                    sql += " os = '%s'," % (row['os'])
                #end if
                if row.has_key('state'):
                    sql += " `state` = '%s'," % (str(row['state']))
                #end if
                sql = sql[0:-1]
                sql = "%s where ip = '%s'" % (sql,row['ip'])
                if asset_scan_id > 0:
                    sql = "%s and asset_scan_id = '%d'" % (sql,asset_scan_id)
                #end if
                dbh.set_item_to_db_safe(sql)
            #end for
            dbh.commit_trans()
        except Exception,e3:
            logging.getLogger().error("File:HostScan.py, update_hostinfo 3333333:" + str(e3))
        #end try
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, update_hostinfo:" + str(e))
    #end try
#end def

def update_hostport(dbh, portlist):
    try:
        global tmptask
    
        task_id   = str(tmptask.task_id)
        asset_scan_id = tmptask.asset_scan_id
    
        list = []
        sql = ""
        if asset_scan_id > 0:
            sql = "select ip, port, proto from port_list_%s where asset_scan_id = '%d'" % (task_id,asset_scan_id)
        else:
            sql = "select ip, port, proto from port_list_%s" % (task_id)
        #end if
        res = dbh.get_all_item_from_db(sql)
        if res and len(res) > 0:
            for row in res:
                t = "%s%s%s" % (row['ip'],str(row['port']),row['proto'])
                list.append(t)
            #end for
        #end if
    
        for row in portlist:
            ip = row['ip']
            port = str(row['port'])
            proto = row['proto']
        
            t = "%s%s%s" % (ip,port,proto)
            if t in list:
                continue
            #end if
        
            sql = "insert into port_list_%s (`ip`,`state`,`port`,`proto`,`asset_scan_id`) values ('%s','open','%s','%s','%d')" % (task_id,ip,port,proto,asset_scan_id)
            dbh.set_item_to_db_safe(sql)
        #end for
        dbh.commit_trans()
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, update_hostport:" + str(e))
    #end try
#end def

# def translate_output(src):
#     try:
#         # logging.getLogger().error('translate:'+src)
#         # zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
#         ks = output_dict.keys()
#         ks = sorted(ks, key=len)
#         ks.reverse()
#         flag = False
#         for k in ks:
#             if k in src:
#                 flag = True
#                 # logging.getLogger().error('Got it.')
#                 src = src.replace(k.replace(':','').strip(),output_dict.get(k).replace(':','').strip())
#             else:
#                 continue
#         # logging.getLogger().error('after:'+src)
#         # match = zhPattern.search(src)
#         if flag:
#             return src
#         else:
#             return ''
#     except Exception, e:
#         logging.getLogger().error("File:HostScan.py, translate_output:" + str(e))
#         return src

def get_trans_dict(dbh,vul_id):
    try:
        dict_tmp={}

        if not vul_id and int(vul_id) != 0:
            return None
        #end if 

        sql = 'select output_en,output_cn from translation_info where vul_id=%d' %(int(vul_id))
        output_list = dbh.get_all_item_from_db(sql)

        if not output_list:
            return None
        #end if

        for output in output_list:
            dict_tmp[output['output_en'].strip()] = output['output_cn'].strip()
        #enf for

        return dict_tmp
    except Exception,e:
        ERROR("File:HostScan.py, get_trans_dict:"+str(e))
        return None
    #end try
#end def


def translate_output(dbh,vul_id,output):
    try:
        output = output.replace("Nessus","Nvscan").replace("nessus","nvscan").replace("NESSUS","NVSCAN")
        # Nessus_patten = re.compile("Nessus",re.I)
        # Nessus_list = re.findall(Nessus_patten,output)
        # for Nessus_key in Nessus_list:
        #     output = output.replace(Nessus_key,"Nvscan")
        en2cn = get_trans_dict(dbh,vul_id)

        if not en2cn :
            return output
        #end if

        en2cn_keys = en2cn.keys()
        en2cn_keys = sorted(en2cn_keys,key=len,reverse=True)
        for dict_key in en2cn_keys:
            if dict_key in output:
                # ERROR(str(k))
                output=output.replace(dict_key,en2cn.get(dict_key))
            else:
                continue
            #end if
        #end for
        return output
    except Exception,e:
        ERROR("translate_output:"+str(e))
        return output
    #end try
#end def




def update_hostvul(dbh, vul_list):
    
    global tmptask
    
    task_id   = tmptask.task_id
    task_name = tmptask.task_name
    asset_scan_id = tmptask.asset_scan_id
    
    logging.getLogger().debug("update_hostvul func enter.")
    
    old_list = []
    sql = ""
    if asset_scan_id > 0:
        sql = "select vul_id,ip,port,proto from vul_details_%d where vul_id > 0 and `asset_scan_id` = '%d'" % (int(task_id),asset_scan_id)
    else:
        sql = "select vul_id,ip,port,proto from vul_details_%d where vul_id > 0" % (int(task_id))
    #end if
    res = dbh.get_all_item_from_db(sql)
    for row in res:
        old_list.append("%s%s%s%s" % (str(row['vul_id']),str(row['ip']),str(row['port']),str(row['proto'])))
    #end for
    
    
    try:
        ##...0 update host_process in task_manager
        sql = ""
        if asset_scan_id > 0:
            sql = "select count(*) from hostmsg_%d where `asset_scan_id` = '%d' and (`state` = 0 or `host_state` = 1)" % (int(task_id),asset_scan_id)
        else:
            sql = "select count(*) from hostmsg_%d where `state` = 0 or `host_state` = 1" % int(task_id)
        #end if
        re = dbh.get_one_item_from_db(sql)
        
        tmpfinished = int(re["count(*)"])
        
        if vul_list and len(vul_list) > 0:
            
            for vul in vul_list:
                
                vul_id = vul['vulid']
                # if vul_id in ['10335','11219','34277','40861']:
                    # continue
                #end if
                
                ip = vul['ip']
                port = vul['port']
                proto = vul['proto']
                output = vul['output']
                t = "%s%s%s%s" % (str(vul_id),str(ip),str(port),str(proto))
                if t in old_list:
                    continue
                #end if
 
                if int(vul_id)  == 41028: #snmp public
                    write_weak_log(dbh, str(task_id),task_name,ip,"SNMP默认团体名","public","public",asset_scan_id, port, proto)                    
                    #continue
                #end if
 
                if int(vul_id)  == 10660: #oracle tnslsnr
                    write_weak_log(dbh, str(task_id),task_name,ip,"ORACLE","tnslsnr","空密码",asset_scan_id, port, proto)
                    #continue
                #end if
                
                if int(vul_id)  == 17162: #Sybase
                    write_weak_log(dbh, str(task_id),task_name,ip,"Sybase","SA","空密码",asset_scan_id, port, proto)  
                    #continue
                #end if
                
                if int(vul_id)  == 10481: #mysql
                    write_weak_log(dbh, str(task_id),task_name,ip,"MYSQL","root","空密码",asset_scan_id, port, proto)        
                    #continue
                #end if
                    
                sql = "select * from vul_info where vul_id = %d" % int(vul_id)
                re = dbh.get_one_item_from_db(sql)
                
                if re:
                    tmp_factor = re["risk_factor"].encode("utf8").decode("utf8")
                    tmp_name   = MySQLdb.escape_string(re["vul_name_cn"].encode("utf8")).decode("utf8")
                    tmp_desc   = MySQLdb.escape_string(re["desc_cn"].encode("utf8")).decode("utf8")
                    tmp_solu   = MySQLdb.escape_string(re["solu_cn"].encode("utf8")).decode("utf8")
                    tmp_ref    = MySQLdb.escape_string(re["ref_cn"].encode("utf8")).decode("utf8")
                    sql = "select `desc` from host_family_list where id = (select family from host_family_ref where vul_id = %d)" % int(vul_id)
                    tmp_family = dbh.get_one_item_from_db(sql)
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
                    # if int(re["output_enable"]) == 1:
                    #     tmp_output    = MySQLdb.escape_string(output_decode(output))
                    # else:
                    #     tmp_output    = ""
                    #end if
                    #tmp_output    = MySQLdb.escape_string(output_decode(output))
                    tmp_output = translate_output(dbh,int(vul_id),output)
                    # tmp_output    = output
                    tmp_output = MySQLdb.escape_string(tmp_output.encode("utf8")).decode("utf8")
        
                    if re["metasploit"]:
                        tmp_metasploit = MySQLdb.escape_string(re["metasploit"])
                    else:
                        tmp_metasploit = ""
                    #end if
                    global firewall_vuls
                    if enable_firewall_inline:
                        if int(vul_id) in firewall_vuls:
                            global firewall_block_time
                            block_ip(firewall_ip, ip, int(port), proto, tmp_name.encode("utf8"), firewall_block_time)
                        #end if
                    #end if
                    
                    INSERT_RAW_VUL_INFO = True
                    
                    if check_if_log_cve(dbh, vul_id) and len(tmp_cve.strip().split(",")) > 1:
                        ob = {}
                        ob['cve'] = tmp_cve.strip()
                        ob['task_id'] = str(task_id)
                        ob['family'] = tmp_family
                        ob['port'] = str(port)
                        ob['proto'] = proto
                        ob['ip'] = ip
                        ob['risk_factor'] = tmp_factor
                        '''
                        if int(re["output_enable"]) == 1:
                            ob['output'] = vul['output']
                        else:
                            ob['output'] = ''
                        #end if
                        '''
                        ob['output'] = translate_output(dbh,int(vul_id),output)
                        ob['metasploit'] = tmp_metasploit
                        ob['asset_scan_id'] = asset_scan_id
                        if updateCveResult(ob):
                            INSERT_RAW_VUL_INFO= False
                        #end if    
                    #end if
                    
                    try:
                        syslog_task_name = task_name.encode("utf8")
                        syslog_vul_name_cn = re["vul_name_cn"].encode("utf8")
                        syslog_family = re["family"].encode("utf8")
                        syslog_risk_factor = re["risk_factor"].encode("utf8")
                        vul_index = ''
                        if re['vul_index'] and len(re['vul_index']) > 0:
                            vul_index = re['vul_index']
                        else:
                            vul_index = '1'
                        #end if
                        syslog_url = "https://" + get_dmi_ip() + "/" + vul_index + ".html"
                        
                        syslog_host_vul(task_id, syslog_task_name, str(ip), str(port), str(proto), syslog_vul_name_cn, syslog_family, syslog_risk_factor, syslog_url)
                    except Exception,e1:
                        logging.getLogger().error("function syslog_host_vul exception:" + str(e1))
                    #end try
                    
                    if INSERT_RAW_VUL_INFO:
                        sql = "insert into vul_details_%d values(0, '%s', %d, '%s', '%s', '%s', '%s', '%s', '%s',  '%s',  '%s',  '%s',  '%s', %d, '%s', '%s', '%d')"\
                            % (task_id, ip, int(vul_id), tmp_cve, tmp_cnvd, tmp_cnnvd, tmp_factor, tmp_name, tmp_desc, tmp_solu, tmp_ref, tmp_output.decode("utf8"), tmp_family, int(port), proto, tmp_metasploit, asset_scan_id)
                        dbh.set_item_to_db_safe(sql)
                    #end if
                #end if
            #end for
            dbh.commit_trans()
        #end if
        
        ##...3 insert host_vul
        pass
        
        ##...4 update host_msg
        sql = ""
        if asset_scan_id > 0:
            sql = "update hostmsg_%d set `host_state` = 1 where asset_scan_id = '%d' and host_progress = '100'" % (task_id, asset_scan_id)
        else:
            sql = "update hostmsg_%d set host_state = 1 where host_progress = '100'" % (task_id)
        #end if
        dbh.set_item_to_db(sql)
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, update_hostvul:" + str(e))
    #end try
#end def


def update_result(dbh, ip,vul_list):
    
    global tmptask
    
    task_id   = tmptask.task_id
    task_name = tmptask.task_name
    asset_scan_id = tmptask.asset_scan_id
    
    logging.getLogger().debug("update_result func enter.")
    
    old_list = []
    sql = ""
    if asset_scan_id > 0:
        sql = "select vul_id,ip,port,proto from vul_details_%d where ip = '%s' and `asset_scan_id` = '%d'" % (int(task_id),ip,asset_scan_id)
    else:
        sql = "select vul_id,ip,port,proto from vul_details_%d where ip = '%s'" % (int(task_id),ip)
    #end if
    res = dbh.get_all_item_from_db(sql)
    for row in res:
        old_list.append("%s%s%s%s" % (str(row['vul_id']),str(row['ip']),str(row['port']),str(row['proto'])))
    #end for
    
    
    try:
        ##...0 update host_process in task_manager
        sql = ""
        if asset_scan_id > 0:
            sql = "select count(*) from hostmsg_%d where `asset_scan_id` = '%d' and (`state` = 0 or `host_state` = 1)" % (int(task_id),asset_scan_id)
        else:
            sql = "select count(*) from hostmsg_%d where `state` = 0 or `host_state` = 1" % int(task_id)
        #end if
        re = dbh.get_one_item_from_db(sql)
        
        tmpfinished = int(re["count(*)"])
        
        if vul_list and len(vul_list) > 0:
            
            for vul in vul_list:
                
                vul_id = vul['vulid']
                port = vul['port']
                proto = vul['proto']
                t = "%s%s%s%s" % (str(vul_id),str(ip),str(port),str(proto))
                if t in old_list:
                    continue
                #end if
                
 
                if int(vul['vulid'])  == 41028: #snmp public
                    write_weak_log(dbh, str(task_id),task_name,ip,"SNMP默认团体名","public","public",asset_scan_id, port, proto)                    
                    #continue
                #end if
 
                if int(vul['vulid'])  == 10660: #oracle tnslsnr
                    write_weak_log(dbh, str(task_id),task_name,ip,"ORACLE","tnslsnr","空密码",asset_scan_id, port, proto)
                    #continue
                #end if
                
                if int(vul['vulid'])  == 17162: #Sybase
                    write_weak_log(dbh, str(task_id),task_name,ip,"Sybase","SA","空密码",asset_scan_id, port, proto)  
                    #continue
                #end if
                
                if int(vul['vulid'])  == 10481: #mysql
                    write_weak_log(dbh, str(task_id),task_name,ip,"MYSQL","root","空密码",asset_scan_id, port, proto)        
                    #continue
                #end if
                    
                sql = "select * from vul_info where vul_id = %d" % int(vul['vulid'])
  
                re = dbh.get_one_item_from_db(sql)
                
                if re:
                    tmp_factor = re["risk_factor"].encode("utf8").decode("utf8")

                    tmp_name   = MySQLdb.escape_string(re["vul_name_cn"].encode("utf8")).decode("utf8")
                  
                    tmp_desc   = MySQLdb.escape_string(re["desc_cn"].encode("utf8")).decode("utf8")
                    tmp_solu   = MySQLdb.escape_string(re["solu_cn"].encode("utf8")).decode("utf8")
                    tmp_ref    = MySQLdb.escape_string(re["ref_cn"].encode("utf8")).decode("utf8")
                    #tmp_family = MySQLdb.escape_string(re["family"].encode("utf8")).decode("utf8")
                    
                    sql = "select `desc` from host_family_list where id = (select family from host_family_ref where vul_id = %d)" % int(vul['vulid'])
                    tmp_family = dbh.get_one_item_from_db(sql)

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
                    
                    # if int(re["output_enable"]) == 1:
                    #     tmp_output    = MySQLdb.escape_string(output_decode(vul['output']))
                    # else:
                    #     tmp_output    = ""
                    #end if
                    tmp_output = translate_output(dbh,int(vul_id),output)
                    #tmp_output    = MySQLdb.escape_string(tmp_output)
                    tmp_output = MySQLdb.escape_string(tmp_output.encode("utf8")).decode("utf8")
                    
                    if re["metasploit"]:
                        tmp_metasploit = MySQLdb.escape_string(re["metasploit"])
                    else:
                        tmp_metasploit = ""
                    #end if
                    
                    global firewall_vuls
                    if enable_firewall_inline:
                        if int(vul['vulid']) in firewall_vuls:
                            global firewall_block_time
                            block_ip(firewall_ip, ip, int(vul['port']), vul['proto'], tmp_name.encode("utf8"), firewall_block_time)
                        #end if
                    #end if
                    
                    INSERT_RAW_VUL_INFO = True
                    
                    if check_if_log_cve(dbh, vul['vulid']) and len(tmp_cve.strip().split(",")) > 1:
                        #ob['family_id'] = 
                        
                        #logging.getLogger().error(tmp_cve.strip())
                        ob = {}
                        ob['cve'] = tmp_cve.strip()
                        ob['task_id'] = str(task_id)
                        ob['family'] = tmp_family
                        ob['port'] = str(vul['port'])
                        ob['proto'] = vul['proto']
                        ob['ip'] = ip
                        ob['risk_factor'] = tmp_factor
                        '''
                        if int(re["output_enable"]) == 1:
                            ob['output'] = vul['output']
                        else:
                            ob['output'] = ''
                        #end if
                        '''
                        ob['output'] = translate_output(dbh,int(vul_id),vul['output'])
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
                        vul_index = ''
                        if re["vul_index"]:
                            vul_index = re["vul_index"]
                        #end if
                        syslog_url = "https://%s/%s.html" % (get_dmi_ip(),vul_index)
                        msg = "syslog_task_name:%s, syslog_vul_name_cn:%s, syslog_family:%s, syslog_risk_factor:%s, syslog_url:%s" % (syslog_task_name,syslog_vul_name_cn,syslog_family,syslog_risk_factor,syslog_url)
                        ERROR(msg)
                        syslog_host_vul(task_id, syslog_task_name, ip, str(vul['port']), vul['proto'], syslog_vul_name_cn, syslog_family, syslog_risk_factor, syslog_url)
                    except Exception,e1:
                        logging.getLogger().error("function syslog_host_vul exception:" + str(e1))
                    #end try
                    #logging.getLogger().error("222222222222222222222,ip:"+ip)
                    if INSERT_RAW_VUL_INFO:
                        sql = "insert into vul_details_%d values(0, '%s', %d, '%s', '%s', '%s', '%s', '%s', '%s',  '%s',  '%s',  '%s',  '%s', %d, '%s', '%s', '%d')"\
                            % (task_id, ip, int(vul['vulid']), tmp_cve, tmp_cnvd, tmp_cnnvd, tmp_factor, tmp_name, tmp_desc, tmp_solu, tmp_ref, tmp_output.decode("utf8"), tmp_family, int(vul['port']), vul['proto'], tmp_metasploit, asset_scan_id)
                        dbh.set_item_to_db_safe(sql)
                    #end if
                #end if
            #end for
            dbh.commit_trans()
        #end if
        
        ##...3 insert host_vul
        pass
        
        ##...4 update host_msg
        sql = ""
        if asset_scan_id > 0:
            sql = "update hostmsg_%d set `host_state` = 1 where `ip` = '%s' and asset_scan_id = '%d' and host_progress = '100'" % (task_id, ip, asset_scan_id)
        else:
            sql = "update hostmsg_%d set host_state = 1 where ip = '%s' and host_progress = '100'" % (task_id, ip)
        #end if
        dbh.set_item_to_db(sql)
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, update_result:" + str(e) + ",ip:" + str(ip))
    #end try

#end def



def check_enable_host(task_id):
    try:
        sql = "select `state` , `host_enable` , `host_state` , `asset_scan_id` from task_manage where id = %d" % int(task_id)
        re = db.get_one_item_from_db(sql)
        
        if re and int(re["host_enable"]) == 1 and int(re["host_state"]) == 0:
            return True
        else:
            asset_scan_id = re['asset_scan_id']
            
            sql = ""
            if asset_scan_id > 0:
                sql = "update hostmsg_%d set `host_state` = '1' where `state` = '1' and `asset_scan_id` = '%d'" % (int(task_id),asset_scan_id)
            else:
                sql = "update hostmsg_%d set `host_state` = '1' where `state` = '1'" % int(task_id)
            #end if
            db.set_item_to_db(sql)
            
            sql = "update task_manage set `host_state` = 1 where id = %d" % int(task_id)
            db.set_item_to_db(sql)
            
            sql = "update `task_manage` set `state` = '3' , `end_time` = now()  where `id` = %d and `web_state` =1 and `weak_state` = 1 and `port_state` = 1 and `init_state` = 1 and `prescan_state` = 1" % int(task_id)
            db.set_item_to_db(sql)
            
            sendEmail(str(task_id))
            
            updateTaskManage()
            check_if_all_end(task_id)
            return False
        #end if
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, check_enable_host:" + str(e) + ",task_id:" + str(task_id))
        return False
    #end try
#end def

def get_dmi_ip():
    try:
        
        sql = "select * from net_config where `Type` like '%DMI%'"
        re = db.get_one_item_from_db(sql)
        
        if re and len(re["Ip"]) > 0:
            return re["Ip"]
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, get_dmi_ip:" + str(e))
    #end try
    
    return "0.0.0.0"
#end def

def init_firewall_inline():
    try:
        sql = "select * from config where Name = 'firewall_enable'"
        ret = db.get_one_item_from_db(sql)
        
        if ret and int(ret["Value"]) == 1:
            
            sql = "select * from config where Name = 'firewall_ip'"
            ret = db.get_one_item_from_db(sql)

            if ret and len(ret["Value"]) > 0:
                
                global enable_firewall_inline
                global firewall_ip
                enable_firewall_inline = True
                firewall_ip = ret["Value"]
                
                print "firewall ip :",
                print firewall_ip

                sql = "select * from config where Name = 'firewall_block_time'"
                ret = db.get_one_item_from_db(sql)
                
                if ret and len(ret["Value"]) > 0:
                    global firewall_block_time
                    firewall_block_time = int(ret["Value"])

                    sql = "select * from firewall_vuls"
                    ret = db.get_one_item_from_db(sql)
                    
                    if ret and len(ret["vuls"]) > 0:
                        global firewall_vuls
                        
                        for vul in ret["vuls"].split(","):
                            firewall_vuls.append(int(vul))
                        #end for
                    #end if
                #end if
            #end if
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, init_firewall_inline:" + str(e))
    #end try
#end def

def block_ip(ip, target, port, proto, vul_name, timeout):
    
    try:
        task_name = "%s_%d" % (target, int(time.time()))
        params = urllib.urlencode({'action':'add', 'ip':target, 'port':port, 'proto':proto, 'vul_name':vul_name, 'block_time':timeout})  
        
        sock = urllib.urlopen("https://%s/scan_inline.php" % ip , params)  
        html = sock.read()
        sock.close()
    except Exception,e:
        logging.getLogger().error("File:HostScan.py, block_ip:" + str(e))
    #end try
#end def

#Add for check '/opt/nvscan' dir 
def checkNvscanDir():
    try:
        lock_file = '/tmp/recover.tmp'
        if os.path.isfile('/opt/nvscan/sbin/nvscand'):
            return
        else:
            #Has nvscan recover process need to wait for complete
            if os.path.isfile(lock_file):
                import time
                while True:
                    if os.path.isfile(lock_file):
                        time.sleep(5)
                        continue
                    else:
                        break
                return
            else:
                #touch tmp file for mark recover process
                os.system('touch ' + lock_file)

            cmd = '''ps -ef | grep nvs | grep -v grep | awk '{print $2}'|xargs kill -9
            lsof | grep opt | awk '{print $2}' | xargs kill -9
umount /opt >> /var/log/nvscan_recover.log
cryptsetup remove nvscan >> /var/log/nvscan_recover.log
losetup -d /dev/loop0 >> /var/log/nvscan_recover.log
modprobe dm-crypt >> /var/log/nvscan_recover.log
cd /var/nvscan >> /var/log/nvscan_recover.log
/bin/tar zxf /var/nvscan/nvscan.tar.gz >> /var/log/nvscan_recover.log
losetup /dev/loop0 /var/nvscan/nvscan.img >> /var/log/nvscan_recover.log
touch /tmp/dm.key >> /var/log/nvscan_recover.log
/usr/bin/dm create >> /var/log/nvscan_recover.log
mount /dev/mapper/nvscan /opt >> /var/log/nvscan_recover.log
/bin/rm /tmp/dm.key
service nvscand start'''
            fp = open('/tmp/tmp.sh', 'w+')
            fp.write(cmd)
            fp.close()
            os.system('/bin/sh /tmp/tmp.sh')
            os.system('rm /tmp/tmp.sh')
            os.system('rm ' + lock_file)

    except Exception, e:
        logging.getLogger().error("File:HostScan.py, checkNvscanDir:" + str(e))

def checkNvscan():
    try:
        cmd='''#!/bin/sh
process=`ps -ef | grep "nvscan-service" | grep -v grep|wc -l`
if test $process -eq 0
then
    echo "no"
    service nvscand start
else
    echo "yes"
fi
'''
        fp = open('/tmp/checknvs.sh', 'w+')
        fp.write(cmd)
        fp.close()
        os.system('/bin/sh /tmp/checknvs.sh')
        os.system('/bin/rm /tmp/checknvs.sh')
    except Exception, e:
        logging.getLogger().error("File:HostScan.py, checkNvscan:" + str(e))

def DEBUG(msg):
    logging.getLogger().info(msg)

def WARN(msg):
    logging.getLogger().warn(msg)

def ERROR(msg):
    logging.getLogger().error('File:HostScan.py, ' + msg)

MAX_SIZE = 5
SCAN_START = 1
SCAN_PAUSE = 2
SCAN_RESUME = 3
SCAN_STOP = 4


start_time = 0

class nvscan_manager(object):
    """docstring for nvscan_manager"""
    def __init__(self, taskinfo):
        try:
            if not taskinfo:
                ERROR("empty taskinfo")
                return

            self.scanner = nvscan_xmlrpc()
            self.task_id = taskinfo.task_id
            self.policy_id = taskinfo.policy_id
            self.task_name = 'nvscan' + str(self.task_id)
            self.target_list = taskinfo.target_list
            self.nvscan_task_timeout = taskinfo.time_out
            self.scan_uuid = taskinfo.scan_uuid
            self.asset_scan_id = taskinfo.asset_scan_id

            self.max_scan_time = self.nvscan_task_timeout*self.target_list.qsize()*60

            #scan status manage
            self.scanning = []
            self.scanned = []
            self.scan_flag = 0 # 0:do nothing 1:start scan 2:pause scan 3:resume scan 4:stop scan

            #report
            self.reporter = report_manager(self.scanner)

            #host scan status
            #[{'ip':'status'}]
            self.host_status = []

        except Exception, e:
            ERROR("nvscan_manager.__init__:"+str(e))

    def init_host_state(self):
        DEBUG('Enter nvscan_manager.init_host_state')
        try:
            sql = 'select ip,host_progress from hostmsg_%d where host_progress != 0'%(int(self.task_id))
            res = db.get_all_item_from_db(sql)
            # DEBUG(res)
            if res:
                for item in res:
                    self.host_status.append({item.get('ip'):item.get('host_progress')})
        except Exception, e:
            ERROR("nvscan_manager.init_host_state:"+str(e))
        DEBUG('Leave nvscan_manager.init_host_state')

    def pre_scan_clear(self):
        DEBUG('Enter nvscan_manager.pre_scan_clear')
        try:
            #Step 1. clear current task_id
            #Step 2. clear the task that status is completed and task_state isn't 2
            res = self.scanner.list_all_report()
            if not res:
                # DEBUG('Nvscan hasnt any task.')
                return
            for item in res:
                # DEBUG(item)
                # DEBUG(item.get('readableName').replace('nvscan', '').strip())
                readableName = item.get('readableName')
                if not readableName:
                    continue
                if readableName.replace('nvscan', '').strip() == str(self.task_id):
                    DEBUG('taskid:' + item.get('readableName')+':'+item.get('name'))
                    self.scanner.stop_scan(item.get('name'))
                    self.scanner.del_report(item.get('name'))

                if self.check_complete_by_id(readableName.replace('nvscan', '').strip()):
                    DEBUG(item.get('readableName')+':'+item.get('name'))
                    self.scanner.stop_scan(item.get('name'))
                    self.scanner.del_report(item.get('name'))

            DEBUG('Leave nvscan_manager.pre_scan_clear')
        except Exception, e:
            ERROR("nvscan_manager.pre_scan_clear:"+str(e))

    def check_complete_by_id(self, task_id):
        try:
            sql = "select state from task_manage where `id` = %s"%task_id
            res = db.get_one_item_from_db(sql)
            DEBUG(task_id)
            DEBUG(res)
            if res:
                if res == -1:
                    return False
                if res.get('state') != 2:
                    return True
                return False
            else:
                return True

        except Exception, e:
            ERROR("nvscan_manager.check_complete_by_id:"+str(e) + ', task_id:' + task_id)

    def scan_manage(self):
        try:
            DEBUG('Enter nvscan_manager.scan_manage')
            self.pre_scan_clear()
            self.scan_flag = SCAN_START
            self.init_host_state()
            if self.scan_uuid:
                #resume scan
                self.scan_resume()
            else:
                res = self.scan_new()
                if res == -1:
                    return

            self.scan_status()
        except Exception, e:
            ERROR("nvscan_manager.scan_manage:"+str(e))
        DEBUG('Leave nvscan_manager.scan_manage')

    def scan_new(self):
        DEBUG('Enter nvscan_manager.scan_new')
        try:
            self.scan_uuid = self.scanner.add_scan(self.task_name, self.target_list, self.policy_id)

            if not self.scan_uuid:
                ERROR("start scan failed, task_id %s:"%self.task_id)
                return -1
            else:
                DEBUG('start scan success: scan_uuid:'+self.scan_uuid)

                sql = "update task_manage set scan_uuid = '%s' where `id` = %d " % (self.scan_uuid, int(self.task_id))
                db.set_item_to_db(sql)
            return 0
        except Exception, e:
            ERROR("nvscan_manager.scan_new:"+str(e))
        DEBUG('leave nvscan_manager.scan_new')

    def update_host_msg(self, scan_progress, ip):
        try:
            sql = "update hostmsg_%d set host_progress = %d where `ip` = '%s'" % (int(tmptask.task_id), scan_progress, ip)
            db.set_item_to_db(sql)
        except Exception, e:
            ERROR("nvscan_manager.update_host_msg:"+str(e))

    def check_scan_progress(self):
        DEBUG('Enter nvscan_manager.check_scan_progress')
        try:
            #Step 1.get all hosts's scan progress
            current_progress = self.scanner.get_scan_progress(self.scan_uuid)

            # DEBUG(len(current_progress))
            # DEBUG(current_progress)
            #Step 2.compare with old status
            # DEBUG(len(self.host_status))
            # DEBUG(self.host_status)
            if not current_progress:
                DEBUG('Has no scan progress now.')
                return
            for item in current_progress:
                key = item.keys()[0]
                if key not in str(self.host_status):
                    #update table 
                    self.update_host_msg(item.get(key), key.strip())
                    self.host_status.append(item)
                else:
                    tmp = [x for x in self.host_status if x.keys()[0].strip() == key.strip()]
                    if item not in tmp and tmp:
                        #update table
                        self.update_host_msg(item.get(key), key.strip())
                        #update self.host_status
                        tmp[0][tmp[0].keys()[0]] = item.get(key)
                    else:
                        #do nothing
                        pass
        except Exception, e:
            ERROR("nvscan_manager.check_scan_progress:"+str(e))
        DEBUG('leave nvscan_manager.check_scan_progress')

    def scan_status(self):
        DEBUG('Enter nvscan_manager.scan_status')
        try:
            while self.scan_flag == SCAN_START or self.scan_flag == SCAN_RESUME:
                self.check_scan_progress()

                self.get_task_status()
                if self.scan_flag == SCAN_PAUSE:
                    #call scan_pause
                    DEBUG('Scan flag is pause')
                    self.scan_stop()
                    break
                elif self.scan_flag == SCAN_STOP:
                    #call scan_stop
                    DEBUG('Scan flag is stop')
                    self.scan_stop()
                    break

                status = self.scanner.list_report(self.scan_uuid)
                if status == 'completed':
                    # DEBUG('scan task id %s completed, scan_uuid: %s' %(self.task_id, self.scan_uuid))
                    ERROR('scan task id %s completed, scan_uuid: %s' %(str(self.task_id), self.scan_uuid))
                    self.scan_complete()
                    break

                global start_time 
                current_time = time.time()
                DEBUG('max_scan_time:' + str(self.max_scan_time))
                last_time = current_time - start_time
                DEBUG('last_time:' + str(last_time))
                if last_time > self.max_scan_time:
                    self.scan_timeout()
                    ERROR('nvscan_manager.scan_status:reach max host scan timeout:'+str(self.max_scan_time) + ', has scanned ' + str(last_time) + ' seconds.')
                    break

                if self.scan_uuid:
                    self.reporter.report_gen(self.scan_uuid)

                DEBUG('================nvscan_manager begin to sleep 60s=====================')            
                time.sleep(60)

            DEBUG('Leave scan_status')
            return
        except Exception, e:
            ERROR("nvscan_manager.scan_status:"+str(e))
        DEBUG('Leave nvscan_manager.scan_status')
     
    def scan_timeout(self):
        try:
            #Step 1.call reporter
            # ERROR('timeout gen report')
            self.reporter.report_gen(self.scan_uuid)
            #Step 2.stop scan
            # ERROR('time out stop scan')
            self.scan_stop()
            #Step 3.Add to avoid Hostscan.py restarted by wafmgr
            ERROR('Scan task time out, set host_state to 1')
            sql = "update task_manage set scan_uuid = '', `host_state` = 1 where `id` = %d" % (int(self.task_id))
            # ERROR(sql)
            db.set_item_to_db(sql)
        except Exception, e:
            raise e

    def scan_complete(self):
        DEBUG('Enter nvscan_manager.scan_complete')
        try:
            self.reporter.report_gen(self.scan_uuid)
            self.scanner.del_report(self.scan_uuid)
            #TODO del scan_uuid in table -- done by xiayuying 20131224
            if not check_if_need_nvscancmd(self.task_id, self.asset_scan_id):
                sql = "update task_manage set scan_uuid = '', `host_state` = 1 where `id` = %d" % (int(self.task_id))
                db.set_item_to_db(sql)
        except Exception, e:
            ERROR("nvscan_manager.scan_complete:"+str(e))
        DEBUG('Leave nvscan_manager.scan_complete')

    def scan_pause(self):
        DEBUG('Enter nvscan_manager.scan_pause')
        try:
            self.scanner.pause_scan(self.scan_uuid)
        except Exception, e:
            ERROR("nvscan_manager.scan_pause:"+str(e))
        DEBUG('Leave nvscan_manager.scan_pause')

    def check_if_all_ip_complete(self):
        try:
            sql = ""
            if self.asset_scan_id > 0:
                sql = "select `ip` from hostmsg_%d where `host_state` <> 1 and `asset_scan_id` = '%d'" % (int(self.task_id),self.asset_scan_id)
            else:
                sql = "select `ip` from hostmsg_%d where `host_state` <> 1  " %  int(self.task_id)
            res = db.get_all_item_from_db(sql)
            if res:
                if len(res) > 0:
                    self.target_list = Queue()
                    for item in res:
                        self.target_list.put(item.get('ip'))
                    return False
            return True
        except Exception, e:
            ERROR("nvscan_manager.check_if_all_ip_complete:"+str(e))

    def scan_resume(self):
        DEBUG('Enter nvscan_manager.scan_resume')
        try:
            if self.check_if_all_ip_complete():
                DEBUG('all ip completed.')
                self.scanner.resume_scan(self.scan_uuid)
            else:
                DEBUG('some ip uncompleted.')
                #Step 1.get all uncomplete ip
                #Step 2.delete old task
                self.scan_stop()
                #Step 3.new task
                self.scan_new()
                
        except Exception, e:
            ERROR("nvscan_manager.scan_resume:"+str(e))
        DEBUG('Leave nvscan_manager.scan_resume')

    def scan_stop(self):
        DEBUG('Etner nvscan_manager.scan_stop')
        try:
            self.scanner.stop_scan(self.scan_uuid)
            self.scanner.del_report(self.scan_uuid)
            sql = "update task_manage set scan_uuid = '' where `id` = %d" % (int(self.task_id))
            db.set_item_to_db(sql)
        except Exception, e:
            ERROR("nvscan_manager.scan_stop:"+str(e))
        DEBUG('Leave nvscan_manager.scan_stop')

    def get_task_status(self):
        DEBUG('Enter nvscan_manager.get_task_status')
        try:
            if self.scan_flag == SCAN_STOP or self.scan_flag == SCAN_PAUSE:
                DEBUG('scan_flag is pause.........')
                return
            sql = "select state from task_manage where id = %d" % int(self.task_id)
            res = db.get_one_item_from_db(sql)
            #state 1:unscan 2:scanning 3:scanned 4:pause
            DEBUG(res)
            if res:
                state = res.get('state')
                DEBUG('++++++state tpye is ' + str(type(state)))
                if  state == 1:
                    self.scan_flag = SCAN_STOP
                elif state == 2:
                    self.scan_flag = SCAN_START
                # elif state == 3:
                #     self.scan_flag == SCAN_START
                elif state == 4:
                    DEBUG('Front pause the task.')
                    self.scan_flag = SCAN_PAUSE
            DEBUG('current scan_flag:' + str(self.scan_flag))
        except Exception, e:
            ERROR("nvscan_manager.get_task_status:"+str(e))
        DEBUG('Leave nvscan_manager.get_task_status')

class report_manager(threading.Thread):
    """docstring for report_manager"""
    def __init__(self, scanner):
        try:
            threading.Thread.__init__(self)
            self.task_list = Queue()
            self.report_flag = 0 # 0 :stop 1:start
            self.scanner = scanner
            self.task_status = SCAN_START
            self.db = db_manager()
        except Exception, e:
            ERROR("report_manager.__init__:"+str(e))

    def report_gen(self, scan_uuid):
        DEBUG("Enter report_manager.report_gen")
        try:
            report_name = self.scanner.gen_chapter(scan_uuid, 'html')
            DEBUG('Add gen task' + str(scan_uuid))
            count = 1
            while True:
                status = self.scanner.down_file(report_name)

                sleep_time = randint(1,5) + count*5
                if sleep_time > 120:
                    sleep_time = 120
                # if not status:
                #     time.sleep(sleep_time)
                #     continue

                if 'Nessus is formatting the report' in status:
                    count += 1
                    DEBUG("===========Reporter begin to sleep %ds================="%sleep_time)
                    time.sleep(sleep_time)
                else:
                    #parse report
                    DEBUG('Get report success.')
                    self.report_pasrse(status)
                    #after one task completed need to clear task and report
                    # self.report_clear(scan_uuid)
                    break
        except Exception, e:
            ERROR("report_manager.report_gen:"+str(e))
        DEBUG("Leave report_manager.report_gen")

    def report_clear(self, scan_uuid):
        DEBUG('Etner report_managerreport_clear')
        try:
            DEBUG('-------------------------------Clearing task and report  begin------------------------------')
            #clear task and report
            self.scanner.del_report(scan_uuid)
            DEBUG('-------------------------------Clearing task and report  end------------------------------')
        except Exception, e:
            ERROR("report_manager.report_clear:"+str(e))
        DEBUG('Leave report_managerreport_clear')

    def report_pasrse(self, report_content):
        DEBUG('Etner report_manager.report_pasrse')
        try:
            #parse report_content and insert into table
            # DEBUG(len(report_content))
            report = NvscanReport()
            # DEBUG('call start process')
            report.startProcess(report_content)
            info = report.gethostinfo()
            portlist = report.gethostport()
            vullist = report.gethostvul()
            
            #Modify by xiayuying 2014-01-22 to improve performance
            if info:
                update_hostinfo(self.db,info)
            if portlist:
                update_hostport(self.db,portlist)
            if vullist:
                update_hostvul(self.db,vullist)
            #end
            
            '''
            result = report.startProcess(report_content)
            if result and len(result.keys()) > 0:
                for ip in result.keys():
                    update_result(self.db, ip, result[ip]['vul'])
                #end for
            #end if
            '''
        except Exception, e:
            ERROR("report_manager.report_pasrse:"+str(e))
        DEBUG('Leave report_managerreport_pasrse')

def finalize_task():
    try:
        asset_scan_id = tmptask.asset_scan_id
        sql = ""
        if asset_scan_id > 0:
            sql = "select count(*) as c from hostmsg_%d where `state` = '1' and `host_state` <> '1' and asset_scan_id = '%d'" % (int(tmptask.task_id),asset_scan_id)
        else:
            sql = "select count(*) as c from hostmsg_%d where `state` = '1' and `host_state` <> '1'" % int(tmptask.task_id)
        #end if
        res = db.get_one_item_from_db(sql)
        if res and len(res) > 0 and res['c'] == 0 and check_prescan(tmptask.task_id):
            sql = "update task_manage set `host_state` = 1 where id = %d" % int(tmptask.task_id)
            db.set_item_to_db(sql)
        #end if
            
        sql = ""
        if asset_scan_id > 0:
            sql = "update hostmsg_%d set `end_time` = now() where `state` = '1' and `port_state` = '1' and `host_state` = '1' and `web_state` = '1' and `weak_state` = '1' and `end_time` = '' and asset_scan_id = '%d'" % (int(tmptask.task_id),asset_scan_id)
        else:
            sql = "update hostmsg_%d set `end_time` = now() where `state` = '1' and `port_state` = '1' and `host_state` = '1' and `web_state` = '1' and `weak_state` = '1' and `end_time` = ''" % int(tmptask.task_id)
        #end if
        db.set_item_to_db(sql)
            
        sql = "update task_manage set `state` = '3', `end_time` = now()  where `id` = %d and `web_state` =1 and `weak_state` = 1 and `port_state` = 1 and `init_state` = 1 and `prescan_state` = 1" % int(tmptask.task_id)
        db.set_item_to_db(sql)
            
        sendEmail(str(tmptask.task_id))
            
        updateTaskManage()
        check_if_all_end(tmptask.task_id)
            
        updateAssetCount(tmptask.task_id,asset_scan_id)
    except Exception, e:
        ERROR("finalize_task:"+str(e))


def host_scan_tail(taskid):
    try:
        from HostScanTail import *
        main(taskid)
    except Exception, e:
        ERROR("host_scan_tail:"+str(e))

def check_if_need_nvscancmd(task_id, asset_scan_id):
    try:
        if not table_exists("vul_details_%d"%(int(task_id))):
            return True
        else:
            if asset_scan_id > 0:
                # sql = "select count(*) as c from hostmsg_%d where `asset_scan_id` = '%d'" % (int(task_id), asset_scan_id)
                sql = "select ip from hostmsg_%d where ip not in (select ip from vul_details_%d where asset_scan_id = '%d' group by ip) and `asset_scan_id` = '%d'"%(int(task_id), int(task_id), int(asset_scan_id), int(asset_scan_id))
            else:
                sql = "select ip from hostmsg_%d where ip not in (select ip from vul_details_%d group by ip)"%(int(task_id), int(task_id))
            #end if
        res = db.get_one_item_from_db(sql)
        if res:
            if len(res) > 0:
                return True
        return False

    except Exception, e:
        ERROR("check_if_need_nvscancmd:"+str(e))
        return True


if __name__ == "__main__":
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    DEBUG("========================HOSTSCAN BEGIN==========================")
    task_id = int(sys.argv[1].replace("#", ""))
    cmd = "/usr/bin/python /var/waf/HostScan.py %d#" % (task_id)
    res = checkProcess(cmd)
    if res == False:
        ERROR("Process: %s  is exist" % (cmd))
        sys.exit(0)
    #end if
    
    #add by xiayuying for BUG #2839
    checkNvscan()

    #add by xiayuying for BUG #2596
    #checkNvscanDir()

    db = db_manager()

    if check_enable_host(task_id) == False:
        logging.getLogger().debug("host scan not enable,exit!")
        sys.exit(0)
    #end if
    
    tmptask = task_init(task_id)
    ERROR('Start a new Hostscan, task id:' + str(tmptask.task_id))
    init_firewall_inline()
    
    start_time = time.time()
    if tmptask != -1:
        nvscan = nvscan_manager(tmptask)
        nvscan.scan_manage()
        if check_if_need_nvscancmd(task_id, tmptask.asset_scan_id):
            host_scan_tail(task_id)
        finalize_task()

    #end if
    ERROR('End a Hostscan, task id:' + str(tmptask.task_id))
    DEBUG("========================HOSTSCAN END==========================")
#end if