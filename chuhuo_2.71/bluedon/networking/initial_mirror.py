#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os
from logging import getLogger


def initial_mirror():

    if not os.path.exists("/etc/mp_server/mirror/"):
        os.makedirs("/etc/mp_server/mirror/")

    f = open("/etc/mp_server/mirror/mirror_in.conf", "w")
    f1 = open("/etc/mp_server/mirror/mirror_out.conf", "w")
    f.write("")
    f1.write("")
    f.close()
    f1.close()

    os.system("/home/ng_platform/bd_dpdk_warper/clients/set_mirror in")
    getLogger("main").info("set_mirror in")
    os.system("/home/ng_platform/bd_dpdk_warper/clients/set_mirror out")
    getLogger("main").info("set_mirror out")


if __name__ == "__main__":
    initial_mirror()
