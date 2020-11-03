#!/usr/bin/env python
# coding: utf-8

""" 
Author: scolia
Date: 2016/10/26 8:47

配置向导

"""
import json
import sys
import time
import os
from MySQL import MySQL
from config import config
from common import logger_init
from logging import getLogger
from db import get_config

logger_init('main', config['logger']['main']['path'], config['logger']['main']['level'])

class Base(object):
    def __init__(self, data):
        self.fifo = '/tmp/bdwaf.fifo'
        self.db = MySQL(config['db'])

        # 路由相关数据
        self.__route_data = data['route']
        self.__route_nic = self.__route_data['nics']
        self.__route_dest = self.__route_data['destru']
        self.__route_mask = self.__route_data['masks']
        self.__route_gateway = self.__route_data['gateway']

        #管理口数据
        self.__entry_data = data['entrance']
        self.__entry_nic = self.__entry_data.get('nics', "")
        self.__entry_ip = self.__entry_data['ip']
        self.__entry_mask = self.__entry_data['subnet']
        self.__entry_gateway = self.__entry_data.get("gateway", "")
        self.__entry_brgname = self.__entry_data.get("brgname", "")
        self.__entry_workpattern = self.__entry_data.get("workpattern", "")

        self.db.query("SELECT * FROM t_staticroute")
        self.now_route = self.db.fetchAllRows()


    def conf_route(self):
        """写入路由信息"""
        self.db.update("DELETE FROM t_staticroute")
        self.db.insert("INSERT INTO t_staticroute (nic, isdefault, dest, mask, gateway) \
                VALUES('%s', 0, '%s', '%s', '%s')"%(self.__route_nic, self.__route_dest,
                self.__route_mask, self.__route_gateway))
        os.system("echo 'CMD_ROUTE|%s|%s|%s|%s' > %s"%(self.__route_nic, self.__route_dest,
            self.__route_mask, self.__route_gateway, self.fifo))
            

    def conf_nicset(self):
        """写入网卡信息"""
        self.db.update("DELETE FROM t_nicset WHERE nic='%s'"%self.__entry_nic)
        self.db.insert("INSERT INTO t_nicset (nic, ip, mask, gateway, isstart, islink, workmode, \
                brgname, workpattern) VALUES ('%s', '%s', '%s', '%s', 1, 1, 'full', '%s', '%s')"
                %(self.__entry_nic, self.__entry_ip, self.__entry_mask, self.__entry_gateway,
                self.__entry_brgname, self.__entry_workpattern))
        os.system("echo 'CMD_INTERFACE|%s' > %s"%(self.__entry_nic, self.fifo))

    def bak_baseconf(self):
        conf = get_config("BaseConfig")
        self.bak_baseconfig = conf
        return self.bak_baseconfig

    def bak_conf(self):
        """配置备份"""
        self.db.query("SELECT * FROM t_nicset")
        self.bak_nicsets = self.db.fetchAllRows()
        self.db.query("SELECT * FROM t_staticroute")
        self.bak_staticroute = self.db.fetchAllRows()
        self.db.query("SELECT * FROM t_bridge")
        self.bak_bridge = self.db.fetchAllRows()
        self.db.query("SELECT * FROM t_dnat")
        self.bak_dnat = self.db.fetchAllRows()
        self.bak_baseconf()
        #print 'bak_conf:',self.bak_baseconfig
    
    
    def list_in_db(self, data, tablename):
        """将list存入对应的表中"""
        if not data:
            return
        sqlstr = "INSERT INTO %s("%tablename
        for index, key in enumerate(data[0].keys()):
            if index != 0:
                sqlstr += (",`%s`"%key)
            else:
                sqlstr += "`%s`"%key
        sqlstr += ") VALUES ("
        for tmpdata in data:
            tmpsqlstr = sqlstr
            index = 0
            for key, value in tmpdata.items():
                if index != 0:
                    tmpsqlstr += ','
                if (not value and value != 0) or value == 'null':
                    value = ""
                if type(value) == type(1) or type(value) == type(1L):
                    tmpsqlstr += ('%d'%value)
                else:
                    tmpsqlstr += ("'%s'"%value)
                index += 1
            tmpsqlstr += ")"
            #print tmpsqlstr
            self.db.insert(tmpsqlstr)

    def list_in_config(self, data, symbol):
        """将list存入对应的配置列中"""
        if not data:
            return
        sqlstr = "UPDATE config set json= '%s' where symbol='%s'" % (data[0],symbol)
        self.db.update(sqlstr)

    def rollback_conf(self):
        """回滚配置"""
        self.rollback_baseconfig()
        self.rollback_nicset()
        self.rollback_route()
        self.rollback_bridge()
        self.rollback_dnat()
        os.system("echo 'CMD_UCARP|deploy' > %s"%self.fifo)
        os.system("echo CMD_REFLASH_NIC > %s"%self.fifo)
        os.system("echo CMD_REFLASH_ROUTE > %s"%self.fifo)

    def rollback_bridge(self):
        """回滚桥信息"""
        self.db.update("DELETE FROM t_bridge")
        self.list_in_db(self.bak_bridge, "t_bridge")
        for br in self.bak_bridge:
            os.system("echo 'CMD_BRIDGE|%s' > %s"%(br['name'], self.fifo))
        time.sleep(5)
        os.system("echo CMD_REFLASH_ROUTE > %s"%self.fifo)

    def rollback_route(self):
        """回滚路由信息"""
        self.db.update("DELETE FROM t_staticroute")
        self.list_in_db(self.bak_staticroute, 't_staticroute')
        for route in self.now_route:
            #print "-"*8, route
            os.system("echo 'CMD_ROUTE|%s|%s|%s|%s' > %s"%(
                route['nic'], route['dest'], route['mask'], route['gateway'], self.fifo))

    def rollback_nicset(self):
        """回滚网卡信息"""
        self.db.update("DELETE FROM t_nicset")
        self.list_in_db(self.bak_nicsets, "t_nicset")
        for nic in self.bak_nicsets:
            os.system("echo 'CMD_INTERFACE|%s' > %s"%(nic['nic'], self.fifo))

    def rollback_dnat(self):
        """回滚dnat信息"""
        self.db.update("DELETE FROM t_dnat")
        self.list_in_db(self.bak_dnat, "t_dnat")
        os.system("echo CMD_DNAT > %s" % self.fifo)
    
    def rollback_baseconfig(self):
        """回滚基础配置信息"""
        #print type(self.bak_baseconfig)
        self.list_in_config([self.bak_baseconfig], "BaseConfig")
        os.system("echo CMD_DEPLOY_TYPE > %s"%self.fifo)
        while self.bak_baseconfig["deploy"] not in ["reverseproxy", "bridge"]:
            result = os.popen("ps aux | grep mp_server |grep -v grep")
            if result.read():
                break

"""反向代理"""
class ReverseProxy(Base):
    def conf(self):
        """配置下发"""
        deploy = self.bak_baseconf()["deploy"]
        self.db.update("UPDATE config SET json = REPLACE(json, '\"deploy\":\"%s\"', '\"deploy\":\"reverseproxy\"') where symbol='BaseConfig'" % deploy)
        os.system("echo 'CMD_DEPLOY_TYPE' > %s"%self.fifo)
        os.system("echo 'CMD_UCARP|deploy' > %s"%self.fifo)
        self.conf_nicset()
        self.conf_route()

""""透明代理"""
class Bridge(Base):
    def conf(self):
        pass


"""透明桥接"""
class TransparentBridge(Base):
    def __init__(self, data):
        super(TransparentBridge, self).__init__(data)
        self.__bridge_data = data['bridge']
        self.__bridge_name = self.__bridge_data['name']
        self.__bridge_nics = self.__bridge_data['nics']

    def conf_bridge(self):
        """写入桥信息"""
        nicnames = self.__bridge_nics.split(",")

        #修改网卡工作模式
        for nicname in nicnames:
            self.db.update("UPDATE t_nicset SET workpattern='bridge', brgname='%s', isstart=1 \
                    WHERE nic='%s'"%(nicname, self.__bridge_name))
            os.system("echo 'CMD_INTERFACE|%s' > %s"%(nicname, self.fifo))

        self.db.insert("INSERT INTO t_bridge(name, nics, ageingtime, stp, forwarddelay, maxage,\
            hellotime, level) VALUES ('%s', '%s', 300, 0, 15, 20, 2, 32767)"%(self.__bridge_name, self.__bridge_nics))
        os.system("echo 'CMD_BRIDGE|%s' > %s"%(self.__bridge_name, self.fifo))

    def conf(self):
        """下发配置"""
        deploy = self.bak_baseconf()["deploy"]
        self.db.update("UPDATE config SET json = REPLACE(json, '\"deploy\":\"%s\"', '\"deploy\":\"transparentbridge\"') where symbol='BaseConfig'" % deploy)
        os.system("echo 'CMD_DEPLOY_TYPE' > %s"%self.fifo)
        os.system("echo 'CMD_UCARP|deploy' > %s"%self.fifo)
        while 1:
            result = os.popen("ps aux | grep mp_server |grep -v grep")
            result_data = result.read()
            if result_data:
                #print result_data
                break
        time.sleep(10)
        self.conf_nicset()
        #print "self.conf_nicset()"
        self.conf_route()
        #print "self.conf_route()"
        time.sleep(20)
        self.conf_bridge()
        #print "self.conf_bridge()"


"""路由模式"""
class Route(Base):
    def __init__(self, data):
        super(Route, self).__init__(data)
        self.__dnatdata = data['dnat']
    
    def conf_dnat(self):
        """写入dnat信息"""
        #修改网卡工作模式
        if self.__dnatdata["nicName"] and self.__dnatdata["nicName"] != 'null':
            self.db.update("UPDATE t_nicset SET workpattern='nat',isstart=1 WHERE nic='%s'"%(self.__dnatdata["nicName"]))
            os.system("echo 'CMD_INTERFACE|%s' > %s"%(self.__dnatdata["nicName"], self.fifo))
        self.db.update("DELETE FROM t_dnat")
        self.__dnatdata["sort"] = 1
        self.list_in_db([self.__dnatdata], 't_dnat')

    def conf(self):
        deploy = self.bak_baseconf()["deploy"]
        self.db.update("UPDATE config SET json = REPLACE(json, '\"deploy\":\"%s\"', '\"deploy\":\"route\"') where symbol='BaseConfig'" % deploy)
        os.system("echo 'CMD_DEPLOY_TYPE' > %s"%self.fifo)
        os.system("echo 'CMD_UCARP|deploy' > %s"%self.fifo)
        time.sleep(10)
        #os.system("echo CMD_REFLASH_NIC > %s"%self.fifo)
        self.conf_nicset()
        self.conf_route()
        time.sleep(20)
        self.conf_dnat()

def conf_factory(json_data):
    """工厂函数"""
    data = json.loads(json_data)
    if data['type'] == 'reverseproxy':
        return ReverseProxy(data)
    elif data['type'] == 'bridge':
        return Bridge(data)
    elif data['type'] == 'transparentbridge':
        return TransparentBridge(data)
    elif data['type'] == 'route':
        return Route(data)
    else:
        raise Exception("Cannot find deploy type")


if __name__ == '__main__':
    try:
        getLogger("main").info("guide start work.")
        conf = conf_factory(json_data=sys.argv[1])
        conf.bak_conf()
        conf.conf()
        sleep_times = 60*10
        getLogger("main").info("guide wait.")
        for second in xrange(sleep_times):
            if os.path.exists("guide_single.txt"):
                os.remove("guide_single.txt")
                getLogger("main").info("guide user stop work.")
                sys.exit(0)
            if os.path.exists("guide_single_stop.txt"):
                os.remove("guide_single_stop.txt")
                getLogger("main").info("guide user rollback conf.")
                break
            time.sleep(1)
        getLogger("main").info("guide rollback conf")
        conf.rollback_conf()
    except Exception, e:
        getLogger('main').exception(e)
