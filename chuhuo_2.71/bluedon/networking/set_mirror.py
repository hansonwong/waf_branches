#! /usr/bin/env python
# -*- coding:utf-8: -*-

"""
    端口镜像的配置操作
    其中包括增加删除
"""


import os
import commands
import json
import re
import itertools
from logging import getLogger


# 判断文件夹是否存在，不存在就创建
if not os.path.exists("/etc/mp_server/mirror/"):
    os.makedirs("/etc/mp_server/mirror/")


def mirror_data(data):
    """
    从接收到的数据，然后处理成配置文件需求的格式类型
    item_in:处理后输入方向的数据
    item_out:处理后输出方向的数据
    checkport:观察端口
    """
    protocol = {"ICMP": "proto:1/255",
                "IGMP": "proto:2/255",
                "IPV4": "proto:4/255",
                "TCP": "proto:6/255",
                "UDP": "proto:17/255",
                "IPV6": "proto:41/255",
                "RSVP": "proto:46/255",
                "GRE": "proto:47/255",
                "ESP": "proto:50/255",
                "AH": "proto:51/255",
                "OSPF": "proto:89/255",
                "PIM": "proto:103/255",
                "VRRP": "proto:112/255",
                "ISIS": "proto:124/255",
                "SCTP": "proto:132/255",
                "UDPLITE": "proto:136/255",
                "all": "proto:0/0"}
    pattern = re.compile(r"\d")
    checkport = data["sCheckPort"]
    # checkport = pattern.findall(checkport)                                      # 找出端口的数字
    # checkport = int("".join(checkport))                            # 将数字列表合成字符串
    results = data["sMirrorSource"]
    item_in = []
    item_out = []

    for result in results:
        sport = result["sPort"]
        sport_num = pattern.findall(sport)
        sport_num = int("".join(sport_num))
        item = protocol[result['sFiveGroup']['sProtocol']] + "," \
                        + "sip:%s" % result['sFiveGroup']['sSourceIP'] + "," \
                        + "dip:%s" % result['sFiveGroup']['sTargetIP'] + ","\
                        + "sport:%s" % result['sFiveGroup']['sSourcePort'] + ","\
                        + "dport:%s" % result['sFiveGroup']['sTargetPort']        # 数据处理成mirror_in.conf文件识别的格式
        if result["sRule"] == "all":
            item_in_one = "all,inport:%s" % sport_num
            item_out_one = "all,outport:%s" % sport_num
            if result["sDirection"] == "twoway":
                item_in.append(item_in_one)
                item_out.append(item_out_one)
            elif result["sDirection"] == "input":
                item_in.append(item_in_one)
            elif result["sDirection"] == "output":
                item_out.append(item_out_one)
        elif result["sRule"] == "fiveGroup":
            itemin = item + "," + "inport:%s" % sport_num
            itemout = item + "," + "outport:%s" % sport_num
            if result["sDirection"] == "twoway":
                item_in.append(itemin)
                item_out.append(itemout)
            elif result["sDirection"] == "input":
                item_in.append(itemin)
            elif result["sDirection"] == "output":
                item_out.append(itemout)
    return item_in, item_out, checkport


def add_mirror(data):
    """
    增加项目数据
    """
    item_in, item_out, checkport = mirror_data(data)
    f = open("/etc/mp_server/mirror/mirror_in.conf", "a")
    f1 = open("/etc/mp_server/mirror/mirror_out.conf", "a")
    os.system("/home/ng_platform/bd_dpdk_warper/clients/port_config %s 9" % checkport)
    getLogger("main").info("port_config %s" % checkport)
    for i in item_in:
        f.write(str(i) + "\n")
    for i in item_out:
        f1.write(str(i) + "\n")
    f.close()
    f1.close()
    os.system("/home/ng_platform/bd_dpdk_warper/clients/set_mirror in")
    getLogger("main").info("set_mirror in ")
    os.system("/home/ng_platform/bd_dpdk_warper/clients/set_mirror out")
    getLogger("main").info("set_mirror out ")


def del_mirror(data):
    """
    删除项目数据，然后重新写入配置数据
    """
    item_in, item_out, checkport = mirror_data(data)
    (status1, output_in) = commands.getstatusoutput("cat /etc/mp_server/mirror/mirror_in.conf")
    (status2, output_out) = commands.getstatusoutput("cat /etc/mp_server/mirror/mirror_out.conf")
    output_in_new = output_in.split()
    output_out_new = output_out.split()
    try:
        for i in item_in:
            output_in_new.remove(i)
        for i in item_out:
            output_out_new.remove(i)
    except Exception as e:
        getLogger("main").error(e)

    f = open("/etc/mp_server/mirror/mirror_in.conf", "w")
    f1 = open("/etc/mp_server/mirror/mirror_out.conf", "w")
    # os.system("/home/ng_platform/bd_dpdk_warper/clients/port_config %s 9" % checkport)
    # getLogger("main").info("port_config %s 9" % checkport)
    for i in output_in_new:
        f.write(str(i) + "\n")
    for i in output_out_new:
        f1.write(str(i) + "\n")
    f.close()
    f1.close()
    os.system("/home/ng_platform/bd_dpdk_warper/clients/set_mirror in")
    getLogger("main").info("set_mirror in")
    os.system("/home/ng_platform/bd_dpdk_warper/clients/set_mirror out")
    getLogger("main").info("set_mirror out")


def enable_mirror(data):
    if data["iStatus"] == 1:
        add_mirror(data)
    else:
        del_mirror(data)


if __name__ == "__main__":
    data ={}
    add_mirror(data)


