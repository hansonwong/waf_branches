#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""
modify log:
    2016-4-29:
        1、启动rip时添加:
            iptables -I FWINPUT -p udp --dport 520 -j ACCEPT
            iptables -I FWINPUT -p udp --sport 520 -j ACCEPT
"""

import os
import json
import codecs
from db.mysqlconnect import mysql_connect_dict
from logging import getLogger


def execute_sql(sql):
    """
    从数据库提取数据
    """
    cur = mysql_connect_dict()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    return results


def rip_port_data():
    """
    把端口的数据转换成配置指令
    """
    sql = "select * from m_tbdynamicroute_rip_port"
    data = execute_sql(sql)
    item = []
    item_name = []
    item_ip = []

    for i in range(len(data)):
        item_name.append(data[i]["sName"])
        item_ip.append(data[i]["sIP"])

        if data[i]["sAuthenticationMode"] == "chain":
            item1 = "key chain %s" % data[i]["sChainName"]
            item.append(item1)

            if data[i]["sChainGroup"]:
                result = json.loads(data[i]["sChainGroup"])

                for j in result:
                    item2 = "key %s" % j["id"]
                    item3 = "key-string %s" % j["value"]
                    item.append(item2)
                    item.append(item3)
                item4 = "interface %s" % data[i]["sName"]
                item5 = "ip rip send version %s" % data[i]["sSendControl"]
                item9 = "ip rip receive version %s" % data[i]["sReceiveControl"]
                item.append(item4)
                item.append(item5)
                item.append(item9)

                if data[i]["sAuthentication"] == "MD5":
                    item6 = "ip rip authentication mode md5"
                    item.append(item6)

                if data[i]["sAuthentication"] == "TEXT":
                    item7 = "ip rip authentication mode text"
                    item.append(item7)
                item8 = "ip rip authentication key-chain %s" % data[i]["sChainName"]
                item.append(item8)

        if data[i]["sAuthenticationMode"] == "single":
            item_1 = "interface %s" % data[i]["sName"]
            item_2 = "ip rip send version %s" % data[i]["sSendControl"]
            item6 = "ip rip receive version %s" % data[i]["sReceiveControl"]
            item.append(item_1)
            item.append(item_2)
            item.append(item6)

            if data[i]["sAuthentication"] == "MD5":
                item_3 = "ip rip authentication mode md5"
                item.append(item_3)

            if data[i]["sAuthentication"] == "TEXT":
                item_4 = "ip rip authentication mode text"
                item.append(item_4)
            item_5 = "ip rip authentication string %s" % data[i]["sSingleSecret"]
            item.append(item_5)
    return item, item_name, item_ip


def rip_set_data():
    """
    把设置的数据转换成配置指令
    """
    sql = "select  sValue from m_tbconfig where sName = 'RIPSet' "
    data_set = execute_sql(sql)
    data_set = json.loads(data_set[0]["sValue"])
    data_set_on = data_set["sRIPRouterON"]
    item_set = ["router rip"]

    if str(data_set_on) == '1':
        if data_set["iRIPV"] == "1":
            item1 = "version 1"
            item_set.append(item1)
        elif data_set["iRIPV"] == "2":
            item2 = "version 2"
            item_set.append(item2)

    return item_set, data_set_on


def rip_option_data():
    """
    把选项的数据转换成配置指令
    """
    sql = "select  sValue from m_tbconfig where sName = 'RipAdvancedOption' "
    data = execute_sql(sql)
    data = json.loads(data[0]["sValue"])
    item = []
    if str(data["iTimerDefault"]) == '0':
        item1 = "timers basic %s %s %s" % (data["iRipUpdate"], data["iRipTimeOut"], data["iRipCollection"])
    # item2 = "default-information originate"
        item.append(item1)
    elif str(data["iTimerDefault"]) == '1':
        item1 = "no timers basic"
        item.append(item1)
    # item.append(item2)

    if data["iRipCoreRouter"] == "1":
        if data["sRipCoreRouter"]:
            item3 = "redistribute kernel metric %s" % data["sRipCoreRouter"]
            item.append(item3)
        else:
            item3 = "redistribute kernel"
            item.append(item3)

    if data["iRipDirectRouter"] == "1":
        if data["sRipDirectRouterMetric"]:
            item4 = "redistribute connected metric %s" % data["sRipDirectRouterMetric"]
            item.append(item4)
        else:
            item4 = "redistribute connected"
            item.append(item4)

    if data["iRipStaticRouter"] == "1":
        if data["sRipStaticRouterMetric"]:
            item5 = "redistribute static metric %s" % data["sRipStaticRouterMetric"]
            item.append(item5)
        else:
            item5 = "redistribute static"
            item.append(item5)

    if data["iRipOSPF"] == "1":
        if data["sRipOSPFMetric"]:
            item6 = "redistribute ospf metric %s" % data["sRipOSPFMetric"]
            item.append(item6)
        else:
            item6 = "redistribute ospf"
            item.append(item6)

    if data["iRipBGP"] == "1":
        if data["sRipBGPMetric"]:
            item7 = "redistribute bgp metric %s" % data["sRipBGPMetric"]
            item.append(item7)
        else:
            item7 = "redistribute bgp"
            item.append(item7)
    return item


def rip_net_data():
    """
    把网络的时间转换成配置指令
    """
    sql = "select * from m_tbdynamicroute_rip_net"
    data = execute_sql(sql)
    item = []

    for i in range(len(data)):
        item1 = "network %s" % data[i]["sIP"]
        item.append(item1)
    return item


def conf_rip():
    """
    从函数 rip_port_data,rip_set_data,rip_option_data中返回的值写进配置文件里
    """
    conf_data = ["hostname ripd", "password centos7", "enable password centos7"]
    item_port, item_name, item_ip = rip_port_data()
    item_set, set_on = rip_set_data()
    item_option = rip_option_data()
    item_net = rip_net_data()

    print set_on
    if set_on == "1":
        print 'add'
        os.system('/usr/sbin/iptables -I FWINPUT -p udp --dport 520 -j ACCEPT')
        os.system('/usr/sbin/iptables -I FWINPUT -p udp --sport 520 -j ACCEPT')

        with open("/usr/local/etc/ripd.conf", "w") as fp:
            for i in conf_data:
                fp.write(str(i) + "\n")
            for i in item_port:
                fp.write(str(i) + "\n")
            for i in item_set:
                fp.write(str(i) + "\n")
            for i in item_option:
                fp.write(str(i) + "\n")
            for i in item_net:
                fp.write(str(i) + "\n")
        try:
            os.system("killall ripd")
            getLogger("main").info("ripd down")
            os.system("killall zebra")
            getLogger("main").info("zebra down")
            os.system("/usr/local/sbin/zebra -d --user=root --group=root")
            getLogger("main").info("zebra on")
            os.system("/usr/local/sbin/ripd -d --user=root --group=root")
            getLogger("main").info("ripd on")
        except Exception as e:
            os.system("/usr/local/sbin/zebra -d --user=root --group=root")
            getLogger("main").info("zebra on")
            os.system("/usr/local/sbin/ripd -d --user=root --group=root")
            getLogger("main").info("ripd on")
            getLogger("main").error(e)

    else:
        os.system('/usr/sbin/iptables -D FWINPUT -p udp --dport 520 -j ACCEPT')
        os.system('/usr/sbin/iptables -D FWINPUT -p udp --sport 520 -j ACCEPT')
        print 'del'

        with open("/usr/local/etc/ripd.conf", "w") as fp:
            for i in conf_data:
                fp.write(i + "\n")
        os.system("killall ripd")
        getLogger("main").info("rip down")


if __name__ == "__main__":
    # conf_rip()
    # rip_port_data()
    rip_option_data()
