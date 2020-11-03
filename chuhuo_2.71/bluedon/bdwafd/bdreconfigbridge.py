#!/usr/bin/env python
# -*- coding: utf-8 -*-

import commands
import time
from bridgesetting import ConfigAllBridge
from common import logger_init, init_iptables_bridge, init_iptables_reverseproxy, init_soft_bypass, init_iptables_transparentbridge


if __name__ == '__main__':
    tag = 0
    while tag < 60:
        status, callback = commands.getstatusoutput("ps aux | grep mp_server|grep -v grep")
        if not status:
            break
        time.sleep(1)
    ConfigAllBridge()
    init_iptables_transparentbridge(True)
