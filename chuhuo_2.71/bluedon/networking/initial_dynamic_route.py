#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os


def initial_route():
    # 动态路由初始化
    ospf_data = ["hostname ospfd", "password 123456", "enable password 123456"]
    rip_data = ["hostname ripd", "password centos7", "enable password centos7"]
    bgp_data = ["hostname bgpd", "password centos7", "enable password centos7"]
    zebra_data = ["hostname zebra", "password centos7", "enable password centos7"]

    with open("/usr/local/etc/ospfd.conf", "w") as fp:
        for i in ospf_data:
            fp.write(i + "\n")
    os.system("killall ospfd")

    with open("/usr/local/etc/ripd.conf", "w") as fp:
        for i in rip_data:
            fp.write(i + "\n")
    os.system("killall ripd")

    with open("/usr/local/etc/bgpd.conf", "w") as fp:
        for i in bgp_data:
            fp.write(i + "\n")
    os.system("killall bgpd")

    with open("/usr/local/etc/zebra.conf", "w") as fp:
        for i in zebra_data:
            fp.write(i + "\n")
    os.system("killall zebra")


if __name__ == "__main__":
    initial_route()

