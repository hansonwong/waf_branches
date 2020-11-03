#! /usr/bin/env python
# -*-coding:utf-8 -*-


import re
import json
from logging import getLogger
from sqlalchemy import Column, Integer, String, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from networking.devices import devices
from db.mysql_db import insert, select, update
from utils.log_logger import rLog_dbg
DBG = lambda x: rLog_dbg('fwdb', x)
MANAGE_NIC_PATH = '/etc/network_config/mgt_nic.txt'
Base = declarative_base()
constr = "mysql://root:bd_123456@localhost/db_firewall?unix_socket=/tmp/mysql3306.sock"
engine = create_engine(constr, encoding='utf-8', pool_recycle=3600,echo=False)
Session = sessionmaker(bind=engine)


class net_interface(Base):
    __tablename__ = "m_tbnetport"
    id =                        Column(Integer, primary_key=True)
    sPortName =                 Column(String(128))
    sNetMask =                  Column(String(64))
    sWorkMode =                 Column(String(64))
    iByManagement =             Column(SmallInteger)
    iSSH =                      Column(SmallInteger)
    iWeb =                      Column(SmallInteger)
    iAllowPing =                Column(SmallInteger)
    iAllowTraceRoute =          Column(SmallInteger)
    iAllowFlow     =            Column(SmallInteger)
    iIPV4ConnectionType =       Column(SmallInteger)
    sIPV4Address =              Column(String(512))
    sIPV4NextJump =             Column(String(32))
    iIPV6ConnectionType =       Column(SmallInteger)
    sIPV6Address =              Column(String(512))
    sIPV6NextJump =             Column(String(32))
    iStatus =                   Column(String(11))
    iMAC =                      Column(String(100))
    sLan =                       Column(String(10))

    def __repr__(self):
        return "<m_tbnetport(id=%d,sPortName='%s',sNetMask='%s',sWorkMode='%s'," \
               "iByManagement=%d, iSSH=%d, iWeb=%d, iAllowPing=%d,iAllowTraceRoute=%d,iAllowFlow=%d,iIPV4ConnectionType=%d" \
               "sIPV4Address='%s', sIPV4NextJump='%s',iIPV6ConnectionType=%d" \
               "sIPV6Address='%s', sIPV6NextJump ='%s',iStatus=%s,iMAC='%s',sLan='%s'" % (
                self.id, self.sPortName, self.sNetMask, self.sWorkMode,
                self.iByManagement, self.iSSH, self.iWeb, self.iAllowPing, self.iAllowFlow,
                self.iAllowTraceRoute, self.iIPV4ConnectionType,
                self.sIPV4Address, self.sIPV4NextJump, self.iIPV6ConnectionType,
                self.sIPV6Address, self.sIPV6NextJump, self.iStatus, self.iMAC,
                self.sLan)


def vEth_map_lan(session):
    """
    vEth口对应的lan口，例：vEth0->lan1
    """
    portname_in_table = session.query(net_interface)
    for instance in portname_in_table:
        flush = session.query(net_interface).filter(net_interface.sPortName == instance.sPortName)
        if instance.sLan == '' or instance.sLan is None or instance.sLan == instance.sPortName:
            if (filter(str.isalpha, instance.sPortName) == 'vEth' and '.' not in instance.sPortName):
                flush.update({net_interface.sLan: ''.join(['Lan', str(int(filter(str.isdigit, instance.sPortName))+1)]),})
            elif 'vEth' in instance.sPortName and '.' in instance.sPortName:
                portname = instance.sPortName.split('.')
                if not re.match('^vEth\d+$', portname[0]):
                    continue
                portname[0] = ''.join(['Lan', str(int(filter(str.isdigit, portname[0])) + 1)])
                portname = '.'.join(portname)
                flush.update({net_interface.sLan: portname})
            else:
                flush.update({net_interface.sLan: instance.sPortName})


def vEth_lan_json_file(session, flag=None):
    if flag:
        vEth_lan = {}
        for instance in session.query(net_interface):
            vEth_lan[instance.sPortName] = instance.sLan
        f = open('/usr/local/bluedon/tmp/vEth_map_lan.txt', 'w')
        print>>f, json.dumps(vEth_lan)
        f.close()


def insert_interfaces():
    flag = True
    # 获取后台所有网卡
    (ifaces, allnic) = devices().get_interfaces()
    DBG('server ifaces:%s' % ifaces)
    DBG('server allnic:%s' % allnic)
    # exception_nic(allnic)
    tablenic = []
    allnic_set = set(allnic)
    # engine = create_engine(constr, encoding='utf-8', echo=False)
    # Session = sessionmaker(bind=engine)
    session = Session()
    # 获取表中所有网卡,及若表中网卡不在后台网卡allnic_set序列中,则删除表中的该网卡数据
    try:
        portname_in_table = session.query(net_interface)
        for instance in portname_in_table:
            portname = set([instance.sPortName])
            if not portname & allnic_set:
                session.delete(instance)
                # flag=True
            tablenic.append(instance.sPortName)
        tablenic = set(tablenic)

        # 后台网卡若不在表中,则加入表中
        for nic in allnic:
            net = net_interface()
            nic_set = set([nic])
            if not nic_set & tablenic:
                for info in ifaces:
                    if nic == info['nic']:
                        net.sPortName = info['nic']
                        net.sIPV4Address = info['ip']
                        net.iStatus = info['status']
                        net.iMAC = info['mac']
                        session.add(net)
                        # flag = True

        # 更新网卡信息
        for iface in ifaces:
            flush = session.query(net_interface).filter(net_interface.sPortName==iface['nic'])
            for info in flush:
                if not info.sWorkMode:
                    info.sWorkMode = 'nat' if info.sPortName.startswith('ppp') else 'route'
            with open(MANAGE_NIC_PATH, 'r') as f:
                manage_nic = json.loads(f.read().strip())
                manage_nic = set(manage_nic.keys())
                DBG('manage_nic:%s' % manage_nic)
            if set([iface['nic']]) & manage_nic:
                flush.update({
                    net_interface.iStatus: iface['status'],
                    net_interface.sIPV4Address: iface['ip'],
                    net_interface.sIPV6Address: iface['ipv6'],
                    net_interface.iWeb: '1',
                    net_interface.iMAC: iface['mac'],
                })
            else:
                flush.update({
                    net_interface.iStatus: iface['status'],
                    net_interface.sIPV4Address: iface['ip'],
                    net_interface.sIPV6Address: iface['ipv6'],
                    net_interface.iMAC: iface['mac'],
                })
        vEth_map_lan(session)
        vEth_lan_json_file(session, flag)
        session.commit()
    except Exception as e:
        getLogger('main').info(e)
    finally:
        session.close()


if __name__ == "__main__":
    insert_interfaces()
