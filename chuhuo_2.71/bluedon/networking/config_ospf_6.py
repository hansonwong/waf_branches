#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import codecs
import ast
import socket
import struct
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
from db.config import fetchall_sql,fetchone_sql
from core.exceptions import ArgumentError
from logging import getLogger
# from networking.config_zebra import conf_zebra


def ospf_set_data():
    sql = "select sValue from m_tbconfig where sName = 'OSPFSetV3' "
    # result = fetchone_sql(sql)
    # data = json.loads(result[0]["sValue"])
    result = fetchone_sql(sql)
    data = ast.literal_eval(result['sValue'])

    ospf_on = data["sOSPFRouterON"]
    static_on = data["sOSPFStatic"]
    ripng = data["sOSPFRIP"]
    if not data.get("sOSPFRouterID", ""):
        raise ArgumentError("no sOSPFRouterID in OSPFSet")

    ip = socket.inet_ntoa(struct.pack('I', socket.htonl(int(data["sOSPFRouterID"]))))   # 把32位整数转换成IP格式
    item_ip = "router-id %s" % ip
    return item_ip,static_on,ripng, ospf_on



def v6_zebra():
    sql = 'SELECT * FROM `m_tbdynamicroute_ospf_v3`'
    datas = fetchall_sql(sql)

    fp = codecs.open("/usr/local/etc/zebra.conf", "a", "utf-8")
    fp.write('\n')
    fp.write('hostname zebra' + '\n')
    fp.write('password bluedon' + '\n')
    fp.write('enable password bluedon' + '\n')

    for dic in datas:
        sPort = dic['sPort']
        fp.write('interface %s' % sPort + '\n')

        sIP = dic['sIP']
        fp.write('ipv6 address %s' % sIP + '\n')


    fp.close()

def v6_ospf6d(item_ip, static_on, ripng):

    sql = 'SELECT * FROM `m_tbdynamicroute_ospf_v3`'
    datas = fetchall_sql(sql)

    fp = codecs.open("/usr/local/etc/ospf6d.conf", "w", "utf-8")

    fp.write('hostname ospf6d' + '\n')
    fp.write('password bluedon' + '\n')
    fp.write('enable password bluedon' + '\n')

    fp.write('router ospf6' + '\n')

    fp.write('%s' % item_ip + '\n')
    if static_on == "1":
        fp.write('redistribute static' + '\n')
    fp.write('redistribute connected' + '\n')
    if ripng == "1":
        fp.write('redistribute ripng' + '\n')

    for dic in datas:
        sPort = dic['sPort']
        fp.write('interface %s' % sPort + '\n')
        #
        # sIP = dic['sIP']
        # fp.write(' ipv6 address %s' % sIP + '\n')

        iCost = dic['iCost']
        fp.write('ipv6 ospf6 cost %s' % iCost + '\n')

        iHelloDiff = dic['iHelloDiff']
        fp.write('ipv6 ospf6 hello-interval %s' % iHelloDiff + '\n')

        iDeadDiff = dic['iDeadDiff']
        fp.write('ipv6 ospf6 dead-interval %s' % iDeadDiff + '\n')

        iResendDiff = dic['iResendDiff']
        fp.write('ipv6 ospf6 retransmit-interval %s' % iResendDiff + '\n')

    fp.close()


def conf_ospf_6():
    item_ip, static_on, ripng, ospf_on = ospf_set_data()

    if ospf_on == "1":
        os.system('/usr/sbin/iptables -6 -I FWINPUT -p 89 -j ACCEPT')

        v6_ospf6d(item_ip, static_on, ripng)

        try:
            os.system("killall ospf6d")
            getLogger("main").info("ospf6d down")
            os.system("killall zebra")
            getLogger("main").info("zebra down")
            os.system("/usr/local/sbin/zebra -d --user=root --group=root")
            getLogger("main").info("zebra on")
            os.system("/usr/local/sbin/ospf6d -d --user=root --group=root")
            getLogger("main").info("ospf6d on")
        except Exception as e:
            os.system("/usr/local/sbin/zebra -d --user=root --group=root")
            getLogger("main").info("zebra on")
            os.system("/usr/local/sbin/ospf6d -d --user=root --group=root")
            getLogger("main").info("ospf6d on")
            getLogger("main").error(e)

    else:
        os.system('/usr/sbin/iptables -6 -D FWINPUT -p 89 -j ACCEPT')
        if os.popen('pgrep ospfd').read():
            os.system("killall ospf6d")
            getLogger("main").info("ospf6d down")
        else:
            os.system("killall zebra")
            getLogger("main").info("zebra down")
            os.system("killall ospf6d")
            getLogger("main").info("ospf6d down")


if __name__ == '__main__':
    # v6_zebra()
    v6_ospf6d()
    # conf_ospf_6()

