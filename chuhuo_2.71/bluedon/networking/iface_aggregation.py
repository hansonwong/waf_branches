#!/usr/bin/env/python
# *-* coding: utf-8 *-*

# Copyright (C) 1998-2015 Bluedon. All Rights Reserve
# This file is part of Bluedon Firewall


"""
modify:
   2016-5-11:
        1、重启网络命令由(systemctl restart network)替换为(ifup bondx)
        2、因为重启整个网络会重配ip从而导致重启过程中连接被中断
    2016-9-28:
        #1、新增工作模式
        2、bond ip 不写配置文件中, 改为ip addr add/del ip dev bondXX
"""

import pdb
from confparse import properties

import db.tables
from networking import net_cmd
from networking import ihandler
from db.mysqlconnect import mysql_connect_dict
import json
import sys
import os


class iface_aggregation(ihandler.ihandler):
    def handle_cmd(self, argvs):
        if len(argvs) != 2:
            return False
        ins = db.tables.convert_iface_aggregation_arg(argvs[1])
        return iface_aggregation.config(argvs[0], ins)

    @staticmethod
    def config(option, ins):
        #if ins.iStatus == 0:
        #    net_cmd.down_bond(ins.sBridgeName)
        #    return True
        if option == 'add':
            if int(ins.iStatus) == 1:
                return iface_aggregation.add_bond(ins)
        elif option == 'del':
            return iface_aggregation.del_bond(ins)
        elif option == 'enable':
            if int(ins.iStatus) == 0:
                return iface_aggregation.del_bond(ins)
            elif int(ins.iStatus) == 1:
                return iface_aggregation.add_bond(ins)
        elif option == 'edit':
            return False
        return False

    @staticmethod
    def add_bond(ins):
        if int(ins.sIPV4Type) == 1:    # 静态
            properties( DEVICE=ins.sBridgeName,
                        #IPADDR=ins.sIPV4,
                        #NETMASK=ins.sIPV4Mask,
                        #GATEWAY=ins.sIPV4Gw,
                        #BOOTPORTO='static',
                        ONBOOT='yes',
                        USERCTL='no',
                        BONDING_OPTS='\"mode=6 miimon=100\"').apply_to('/etc/sysconfig/network-scripts/ifcfg-%s' %(ins.sBridgeName))

        iface_aggregation.bond_to(ins.sBridgeName, ins.sBindDevices.split(','))
        net_cmd.load_bonding()
        net_cmd.restart_network(ins.sBridgeName)

        # add ip
        ip_cmd = 'ip addr add {0} dev {1}'
        for item in ins.sIPV4.split(','):
            cmd = ip_cmd.format(item, ins.sBridgeName)
            #print cmd
            os.system(cmd)

        return True

    @staticmethod
    def bond_to(bond, ifaces):
        for item in ifaces:
            properties( DEVICE=item,
                        USERCTL='no',
                        MASTER=bond,
                        SLAVE='yes',
                        BOOTPROTO='none').apply_to('/etc/sysconfig/network-scripts/ifcfg-%s'% item )

    @staticmethod
    def del_bond(ins):
        # del ip
        ip_cmd = 'ip addr del {0} dev {1}'
        for item in ins.sIPV4.split(','):
            cmd = ip_cmd.format(item, ins.sBridgeName)
            #print cmd
            os.system(cmd)

        net_cmd.down_bond(ins.sBridgeName)
        ifaces = ins.sBindDevices.split(',')
        for i in ifaces:
            net_cmd.add_iface_bond(i, ins.sBridgeName, False)
        net_cmd.del_bond(ins.sBridgeName)
        return True

def recover():
    if len(sys.argv) == 1:
        return

    cur = mysql_connect_dict()
    aggregation_sql='select * from m_tbportaggregation where iStatus=1'
    cur.execute(aggregation_sql)
    aggregation_info=cur.fetchall()
    for aggregation_data in aggregation_info:
        aggregation_tmp=[]
        if sys.argv[1] == 'factory_recover':
            aggregation_tmp.append('del')
            aggregation_tmp.append(json.dumps(aggregation_data))
            iface_aggregation().handle_cmd(aggregation_tmp)
        if sys.argv[1] == 'boot_recover':
            aggregation_tmp.append('add')
            aggregation_tmp.append(json.dumps(aggregation_data))
            iface_aggregation().handle_cmd(aggregation_tmp)
    cur.close()


if __name__== "__main__":
    recover()



