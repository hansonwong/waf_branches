#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json


def del_param(args):

    args = json.loads(args)

    source_ip = args["sSourceIP"]
    target_ip = args["sTargetIP"]
    start_time = args["iStartTime"]
    end_time = args["iEndTime"]
    #status = str(args["iStatus"])

    cmd_options = "iptables -D TSE_CHAIN -s %s -d %s -m time --kerneltz --timestart %s --timestop %s -j DROP"

    os.system(cmd_options % (source_ip, target_ip, start_time, end_time))

    print "drop", cmd_options % (source_ip, target_ip, start_time, end_time)

    cmd_options = "iptables -D TSE_CHAIN -s %s -d %s -m time --kerneltz --timestart %s --timestop %s -m limit --limit 3/s -j LOG --log-level 4 --log-prefix=\"ipt_log=DROP \""

    os.system(cmd_options % (source_ip, target_ip, start_time, end_time))

    print "log", cmd_options % (source_ip, target_ip, start_time, end_time)
