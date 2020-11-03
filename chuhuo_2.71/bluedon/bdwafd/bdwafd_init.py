#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from logging import getLogger
from config import config
from clogtable import creatlogstables
from config_iptables import init_iptables
from common import logger_init
from deploymode import switch_bdwaf, init_all_conf


def bdwaf_init():
    '''waf 初始化'''
    os.chdir(config['cwd'])
    logger_init('main', config['logger']['bdinit']['path'], 
                        config['logger']['bdinit']['level'])
    getLogger('main').info('bdinit start.')
    try:
        init_all_conf()
        switch_bdwaf()
        init_iptables(reboot=True)
        os.system('killall -9 syslog-ng; /usr/local/syslog-ng/sbin/syslog-ng')
        creatlogstables(time.strftime("%Y%m", time.localtime()), 0)
    except Exception, e:
        getLogger('main').exception(e)
    getLogger('main').info('bdinit end.')


if __name__ == '__main__':
    bdwaf_init()
