#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""
modify log:
    2016-4-29:
        1、启动ospf时添加:
            iptables -I FWINPUT -p 89 -j ACCEPT
"""


import os
import json
import codecs
import socket
import struct
from logging import getLogger

from db.mysqlconnect import mysql_connect_dict
from core.exceptions import ArgumentError
# from config_rip import rip_port_data, rip_set_data


def execute_sql(sql):
    """
    从数据库提取数据
    """
    cur = mysql_connect_dict()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    return results


def ospf_port_data():
    item = []
    item_port = []
    item_ip = []
    sql = "select * from m_tbdynamicroute_ospf_port"
    data = execute_sql(sql)
    for i in range(len(data)):
        item_port.append(data[i]["sPort"])
        item_ip.append(data[i]["sIP"])
        item1 = "interface %s" % data[i]["sPort"]
        item.append(item1)

        if data[i]["sAuthentication"] == "NONE":
            pass

        elif data[i]["sAuthentication"] == "TEXT":
            item5 = "ip ospf authentication"
            item6 = "ip ospf authentication-key %s" % data[i]["sCommand"]
            item.append(item5)
            item.append(item6)

        elif data[i]["sAuthentication"] == "MD5":
            item7 = "ip ospf authentication message-digest"
            item8 = "ip ospf message-digest-key %s md5 %s" % (data[i]["iSecretID"], data[i]["iSecretValue"])
            item.append(item7)
            item.append(item8)
        item4 = "ip ospf cost %s" % data[i]["sCost"]
        item2 = "ip ospf dead-interval %s" % data[i]["iDeadDiff"]
        item3 = "ip ospf hello-interval %s" % data[i]["iHelloDiff"]
        item.append(item4)
        item.append(item2)
        item.append(item3)
    return item, item_port, item_ip


def ospf_set_data():
    """
    路由重发布设置，转换成配置文件指令
    然后返回一个指令列表
    """
    sql = "select  sValue from m_tbconfig where sName = 'OSPFSet' "
    result = execute_sql(sql)
    data = json.loads(result[0]["sValue"])
    ospf_on = data["sOSPFRouterON"]
    item_one = ["router ospf"]
    if not data.get("sOSPFRouterID", ""):
        raise ArgumentError("no sOSPFRouterID in OSPFSet")
    ip = socket.inet_ntoa(struct.pack('I', socket.htonl(int(data["sOSPFRouterID"]))))   # 把32位整数转换成IP格式
    item2 = "ospf router-id %s" % ip
    item_one.append(item2)
    item_two = []
    item3 = "redistribute connected"
    item4 = "redistribute static"
    item5 = "redistribute rip"
    item6 = "redistribute bgp"

    if str(data.get("sOSPFLinkPointer", 0)) == "1":
        item_two.append(item3)

    if str(data.get("sOSPFStatic", 0)) == "1":
        item_two.append(item4)

    if str(data.get("sOSPFRIP", 0)) == "1":
        item_two.append(item5)

    if str(data.get("sOSPFBGP", 0)) == "1":
        item_two.append(item6)

    if str(data.get("sOSPFkernel", 0)) == "1":
        item_two.append('redistribute kernel')
    return item_one, item_two, ospf_on


def ospf_net_data():
    """
    网络设置指令的转换，并返回一个指令列表
    """
    item_net = []
    sql = "select * from m_tbdynamicroute_ospf_net"
    data = execute_sql(sql)

    for i in range(len(data)):
        area_sql = "select * from m_tbdynamicroute_ospf_area where id=%d" % int(data[i]["sArea"])
        area_data = execute_sql(area_sql)
        area_data = area_data[0]
        item = "network %s area %s" % (data[i]["sIP"], area_data["sAreaIP"])
        item_net.append(item)
    return item_net


def ospf_area_data():
    """
    各个区的配置指令转换，并返回指令列表
    """
    sql = "select * from m_tbdynamicroute_ospf_area"
    data = execute_sql(sql)
    item = []

    for i in range(len(data)):

        if data[i]["sAuthentication"] == "NONE":
            # item1 = "area %s" % int(data[i]["sAreaIP"])
            # item.append(item1)

            if data[i]["sType"] == "Regular":
                pass

            elif data[i]["sType"] == "STUB":
                item2 = "area %s stub" % int(data[i]["sAreaIP"])
                item.append(item2)

            elif data[i]["sType"] == "NSSA":
                item3 = "area %s nssa translate-candidate" % int(data[i]["sAreaIP"])
                item.append(item3)

        elif data[i]["sAuthentication"] == "TEXT":
            item4 = "area %s authentication" % int(data[i]["sAreaIP"])
            item.append(item4)
            if data[i]["sType"] == "Regular":
                pass
            elif data[i]["sType"] == "STUB":
                item5 = "area %s stub" % int(data[i]["sAreaIP"])
                item.append(item5)
            elif data[i]["sType"] == "NSSA":
                item6 = "area %s nssa translate-candidate" % int(data[i]["sAreaIP"])
                item.append(item6)

        elif data[i]["sAuthentication"] == "MD5":
            item3 = "area %s authentication message-digest" % int(data[i]["sAreaIP"])
            item.append(item3)

            if data[i]["sType"] == "Regular":
                pass

            elif data[i]["sType"] == "STUB":
                item6 = "area %s stub" % int(data[i]["sAreaIP"])
                item.append(item6)

            elif data[i]["sType"] == "NSSA":
                item7 = "area %s nssa translate-candidate" % int(data[i]["sAreaIP"])
                item.append(item7)
        # item8 = "area %s virtual-link %s" % (int(data[i]["sAreaIP"]), data[i]["sRemoteRouteIP"])
        # item.append(item8)
    return item


def conf_ospf():
    """
    接收各个配置指令的列表并按顺序写入ospfd.conf配置文件里面
    并执行开始指令
    """
    conf_data = ["hostname ospfd", "password 123456", "enable password 123456"]
    item_set_one, item_set_two, ospf_on = ospf_set_data()
    item_port_data, item_port, item_ip = ospf_port_data()
    item_net = ospf_net_data()
    item_area = ospf_area_data()

    if ospf_on == "1":
        os.system('/usr/sbin/iptables -I FWINPUT -p 89 -j ACCEPT')

        fp = codecs.open("/usr/local/etc/ospfd.conf", "w", "utf-8")

        for i in conf_data:
            fp.write(i + "\n")

        for i in item_port_data:
            fp.write(i + "\n")

        for i in item_set_one:
            fp.write(i + "\n")

        for i in item_set_two:
            fp.write(i + "\n")

        for i in item_net:
            fp.write(i + "\n")

        for i in item_area:
            fp.write(i + "\n")
        fp.close()
        try:
            os.system("killall ospfd")
            getLogger("main").info("ospfd down")
            os.system("killall zebra")
            getLogger("main").info("zebra down")
            os.system("/usr/local/sbin/zebra -d --user=root --group=root")
            getLogger("main").info("zebra on")
            os.system("/usr/local/sbin/ospfd -d --user=root --group=root")
            getLogger("main").info("ospfd on")
        except Exception as e:
            os.system("/usr/local/sbin/zebra -d --user=root --group=root")
            getLogger("main").info("zebra on")
            os.system("/usr/local/sbin/ospfd -d --user=root --group=root")
            getLogger("main").info("ospfd on")
            getLogger("main").error(e)
    else:
        os.system('/usr/sbin/iptables -D FWINPUT -p 89 -j ACCEPT')
        if os.popen('pgrep ospf6d').read():
            os.system("killall ospfd")
            getLogger("main").info("ospfd down")
        else:
            os.system("killall zebra")
            getLogger("main").info("zebra down")
            os.system("killall ospfd")
            getLogger("main").info("ospfd down")


if __name__ == "__main__":
    # ospf_net_data()
    conf_ospf()



