#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os, sys
from contextlib import contextmanager
sys.path.append("/usr/local/bluedon/bdwafd/")

from common import logger_init
from config import config
from db import session_scope, DevInfo
from logging import getLogger

version = '1.3.1patch7'

def updatefiles():
    files = [
        ['acclogtable.py', '/usr/local/bluedon/bdwafd/'],
        ['alertor.py', '/usr/local/bluedon/bdwafd/'],
        ['bdblocked.py', '/usr/local/bluedon/bdwafd/'],
        ['bdntpdate.py', '/usr/local/bluedon/bdwafd/'],
        ['bducarp.py', '/usr/local/bluedon/bdwafd/'],
        ['clogtable.py', '/usr/local/bluedon/bdwafd/'],
        ['common.py', '/usr/local/bluedon/bdwafd/'],
        ['db.py', '/usr/local/bluedon/bdwafd/'],
        ['deploy.php', '/usr/local/bluedon/www/controllers/'],
        ['modsecurity', '/usr/local/bluedon/bdwafd/data/template/'],
        ['cusrule', '/usr/local/bluedon/bdwafd/data/template/'],
        ['selfstudyrule', '/usr/local/bluedon/bdwafd/data/template/'],
        ['task.py', '/usr/local/bluedon/bdwafd/'],
        ['weboutlog.py', '/usr/local/bluedon/bdwafd/'],
        ['waf.sql', '/usr/local/bluedon/bdwafd/data/'],
        ]
    for f in files:
        os.system('cp %s %s' % (f[0], f[1]))

def updatewaf():
    #getLogger('main').info('updatewaf start.')
    updatefiles()
    with session_scope() as session:
        devinfo = session.query(DevInfo).first()
        if devinfo.sys_ver < version:
            updatefiles()
            devinfo.sys_ver = version
            return 0
        return 1
    #getLogger('main').info('updatewaf start.')

if __name__ == '__main__':
    #cwd = config['cwd']
    #os.chdir(cwd)
    #logger_init('main', config['logger']['cleardisk']['path'], config['logger']['cleardisk']['level'])
    exit(updatewaf())
