#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json
from db.mysqlconnect import execute_sql
from set_mirror import add_mirror, mirror_data


def reply_mirror():
    sql = "select * from m_tbport_mirror"
    results = execute_sql(sql)
    f = open("/etc/mp_server/mirror/mirror_in.conf", "w")
    f1 = open("/etc/mp_server/mirror/mirror_out.conf", "w")
    f.close()
    f1.close()
    checkports = []
    for i in range(len(results)):
        results[i]['sMirrorSource'] = json.loads(results[i]['sMirrorSource'])
        item_in, item_out, checkport = mirror_data(results[i])
        if int(results[i]["iStatus"]) == 1:
            fp = open("/etc/mp_server/mirror/mirror_in.conf", "a")
            fp2 = open("/etc/mp_server/mirror/mirror_out.conf", "a")
            for j in item_in:
                fp.write(str(j) + "\n")
            for j in item_out:
                fp2.write(str(j) + "\n")
            fp.close()
            fp2.close()
        checkports.append(checkport)

    for i in checkports:
        os.system("/home/ng_platform/bd_dpdk_warper/clients/port_config %s 9" % i)
        break

    os.system("/home/ng_platform/bd_dpdk_warper/clients/set_mirror in")
    os.system("/home/ng_platform/bd_dpdk_warper/clients/set_mirror out")


if __name__ == "__main__":
    reply_mirror()
