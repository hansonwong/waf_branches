#! /usr/bin/python  
#-*-coding:utf-8-*-

import os
import sys  
import struct
import ctypes
import socket
import threading
import CFTP_pb2
from MySQL import MySQL
from config import config
from getSystemInfo import Systeminfo
import time


class CloudfenceLinkage(threading.Thread):
    db = None
    sleeptime = 10
    def __init__(self):
        super(CloudfenceLinkage, self).__init__(name = self.__class__.__name__)
        self.event  = threading.Event()
    
    def start(self):
        getLogger('main').info(self.__class__.__name__+ ' starting...')
        super(CloudfenceLinkage, self).start()
        getLogger('main').info(self.__class__.__name__+ ' started.')
    
    def stop(self):
        getLogger('main').info(self.__class__.__name__+ ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__+ ' Exited.')
    
    def check_ddos(self, speed, status):
        tag = False
        #DOTO(peixu): 获取ddos攻击信息，如果受到攻击，转移ddos, 有攻击或者状态为0才会返回有数据列表
        #net_flow_info = Systeminfo().net_flow()
        #目前先简单判断是否有ddos攻击，后续再完善
        self.db.query("SELECT * FROM logs.t_ddoslogs WHERE logtime=%d"%(int(time.time())-self.sleeptime))
        result = self.db.fetchAllRows()
        if result or not status:
            tag = True
        domains = []
        if not tag:
            return False
        self.db.query("SELECT * FROM t_website WHERE ddosfencetype='waf'")
        for website in self.db.fetchAllRows():
            domains.append(website.sWebSiteName)
        return list(set(domains))
    
    def into_db(self, data):
        if data["mid"] != CFTP_pb2.MESS_RES_WAF_DOMAIN_STATUS:
            self.db.update("UPDATE t_cloudfence_linkage SET status=1")
            return False

        noneddos = True
        for domainstatus in ResWafDDos["data"]["status"]:
            ddosfencetype = "waf"
            if domainstatus["status"] == 1:
                noneddos = False
                ddosfencetype = "cloudfence"
            self.db.update("UPDATE t_website SET ddosfencetype='%s' WHERE sWebSiteName='%s'"
                    %(ddosfencetype, domainstatus['domain']))
        if noneddos:
            self.db.update("UPDATE t_cloudfence_linkage SET status=1")
        if ResWafDDos["data"]["type"] == 1:
            self.db.update("UPDATE t_cloudfence_linkage SET status=0")
        return True
    
    def proc(self):
        self.db = MySQL(config['db'])
        self.db.query("SELECT * FROM t_cloudfence_linkage")
        cloudfence = self.db.fetchOneRow()
        if cloudfence["is_use"]:
            domains = self.check_ddos(cloudfence["speed"], cloudfence['status'])
            if domains:
                if cloudfence["status"] == 1:
                    waf_cloudfence = WAF_CLOUDFENCE(cloudfence["CloudfenceHost"],
                            cloudfence["CloudfencePort"])
                    result = waf_cloudfence.set_cloudfence_ddos(domains, cloudfence_setting["username"])
                else:
                    waf_cloudfence = WAF_CLOUDFENCE(cloudfence["CloudfenceHost"],
                            cloudfence["CloudfencePort"])
                    result = waf_cloudfence.get_cloudfence_ddos_status(domains, cloudfence_setting["username"])
                self.into_db(result)
        self.db.close()
    
    def run(self):
        while 1:
            try:
                if self.event.isSet():
                    break
                self.proc()
                time.sleep(self.sleeptime)
            except Exception, e:
                getLogger('main').exception(e)


class WAF_CLOUDFENCE():
    sock = None
    login_tag = False

    def __init__(self, host='172.16.2.107', port=50001):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.closed = False
    
    def __del__(self):
        self.sock.close()
        self.login_tag = False
    
    def send_message(self, message, nid):
        if not self.login_tag:
            self.login()

        idsize = ctypes.sizeof(ctypes.c_int32(nid))
        size = message.ByteSize()
        allsize = ctypes.sizeof(ctypes.c_int32(size)) + idsize + size
        self.sock.sendall(struct.pack('!i', allsize))
        self.sock.sendall(struct.pack('!i', nid))
        self.sock.sendall(message.SerializeToString())
        buf = self.sock.recv(1024)
        return buf
    
    def read_simple_message(self, message):
        ResSimple = CFTP_pb2.ResSimple()
        ResSimple.ParseFromString(message)
        #print "result: ", ResSimple.result
        #print "description: ", ResSimple.description
        data = {"result": ResSimple.result, "description": ResSimple.description}
        return data

    def logout(self):
        self.sock.sendall(struct.pack('!i', 8))
        self.sock.sendall(struct.pack('!i', CFTP_pb2.MESS_LOGOUT))
        self.__del__()
        return "logout"
    
    def read_waf_domain_status(self, message):
        # lrs test start
        #f = open("abc", "w")
        #f.write(message)
        #f.close()
        # lrs test end
        ResWafDDos = CFTP_pb2.ResWafDDos()
        ResWafDDos.ParseFromString(message)
        result_type = ResWafDDos.type
        domain_status = {}
        for domaindata in ResWafDDos.domainStatus:
            domain_status[domaindata.domain] = domaindata.status
        data = {"type": result_type, "status": domain_status}
        return data

    def read_message(self, messagebuf):
        message = messagebuf[8:]
        allsize = struct.unpack("!i", messagebuf[:4])[0]
        mid = struct.unpack("!i", messagebuf[4:8])[0]
        messages = {
                CFTP_pb2.MESS_RES_SIMPLE: self.read_simple_message,
                CFTP_pb2.MESS_LOGOUT: self.logout,
                CFTP_pb2.MESS_RES_WAF_DOMAIN_STATUS: self.read_waf_domain_status,
                CFTP_pb2.MESS_RES_WAF_DDOS: self.read_waf_domain_status,
                }
        if mid in messages.keys():
            return {"mid": mid, "data": messages[mid](message)}
        print mid
        return False

    def login(self):
        self.login_tag = True
        reqlogin = CFTP_pb2.ReqLogin()
        reqlogin.user = 'cloudfence'
        reqlogin.passwd = 'cloudfence'
        reqlogin.type = CFTP_pb2.HOST_NODE_TYPE_WAF_DDOS
        result_message = self.send_message(reqlogin, CFTP_pb2.MESS_LOGIN)
        result = None
        if result_message:
            result = self.read_message(result_message)
        if result["data"]["result"]:
            self.login_tag = False

    def get_cmd_waf_ddos_message(self, domains, username, mtype):
        CmdWafDDos = CFTP_pb2.CmdWafDDos()
        for domain in domains:
            CmdWafDDos.domain.append(domain)
        CmdWafDDos.type = mtype
        CmdWafDDos.username = username
        return CmdWafDDos


    def set_cloudfence_ddos(self, domains, username):
        message = self.get_cmd_waf_ddos_message(domains, username, 1)
        result_message = self.send_message(message, CFTP_pb2.MESS_CMD_WAF_DDOS)
        result = None
        if result_message: 
            result = self.read_message(result_message)
        return result

    def get_cloudfence_ddos_status(self, domains, username):
        message = self.get_cmd_waf_ddos_message(domains, username, 2)
        result_message = self.send_message(message, CFTP_pb2.MESS_CMD_WAF_DDOS)
        result = None
        if result_message: 
            result = self.read_message(result_message)
        return result

    def stop_cloudfence_ddos(self, domains, username):
        message = self.get_cmd_waf_ddos_message(domains, username, 3)
        result_message = self.send_message(message, CFTP_pb2.MESS_CMD_WAF_DDOS)
        result = None
        if result_message:
            result = self.read_message(result)
        return result

if __name__ == "__main__":
    #waf_cloudfence = WAF_CLOUDFENCE('172.16.2.134', 50001)
    waf_cloudfence = WAF_CLOUDFENCE()
    domains = ['www.peixu.com',"www.haoliang.com","www.lrstst.cn","www.jjj.com.cn","www.lhz.com"]
    print waf_cloudfence.set_cloudfence_ddos(domains, 'demo@chinabluedon.cn')
    print waf_cloudfence.get_cloudfence_ddos_status(domains, 'demo@chinabluedon.cn')
    waf_cloudfence.logout()
    #time.sleep(30);
