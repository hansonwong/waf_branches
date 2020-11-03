#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Bluedon Web Application Firewall Setup Program

Usage:
  setup.py (install|uninstall)

Options:
  -h --help                  show this help message and exit
  -v --version               show version and exit
"""

import os, logging, signal, threading, time, tempfile
from docopt import docopt
from config import config
from systeminfo import getFormattedNicSetInfo, SystemInfo
from sysinfo_tables import WafSessionManager

def sysinit():
    sinfo   = SystemInfo()
    session = WafSessionManager()
    #add nic info
    nicinfos = getFormattedNicSetInfo(sinfo) 
    for nicname in nicinfos:
        session.AddNicInfo(nicinfos[nicname])
    del session

def setup_rc_local(install, command):
    rclocal = '/etc/rc.local'
    end = 'exit 0'
    f = tempfile.NamedTemporaryFile(delete=False)
    find = False
    for line in open(rclocal):
        if line.strip() == command:
            find = True
            if not install:
                continue
        elif line.strip() == end:
            if not find and install:
                f.write(command+'\n')
        f.write(line)
    f.close()
    if install and find or not install and not find:
        os.remove(f.name)
    else:
        os.rename(f.name, rclocal)
        os.system('chmod 755 '+rclocal)

def setup_cron(install):
    if install:
        with open(config['cron']['filepath'], 'w') as fp:
            fp.write(config['cron']['crontab'])
    else:
        os.remove(config['cron']['filepath'])

def setup_db():
    pass

if __name__ == '__main__':
    args = docopt(__doc__, version='1.0.0')
    if args['install']:
        setup_rc_local(True, config['bootscript'])
        #setup_cron(True)
        sysinit()
    elif args['uninstall']:
        setup_rc_local(False, config['bootscript'])
        #setup_cron(False)

