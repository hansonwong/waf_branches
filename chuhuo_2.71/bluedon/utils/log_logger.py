#!/usr/bin/env python
# coding=utf-8

import logging
from logging import handlers
from core.setting import LOG_LEVEL

# return how many bytes of input
hm = lambda x :int(x[:-1]) * pow(1024, ['B','K','M','G'].index(x[-1]))

#get log path by name, usage: P_LOG(name)
P_LOG = lambda x :r'/usr/local/bluedon/log/' + x + '.log'

# MAX = hm('10M')
MAX = hm('10M')


# RotatingFileHandler
def init_rLog(n, path, level=LOG_LEVEL):
    level = logging.DEBUG
    logger = logging.getLogger(n)
    logger.setLevel(level)
    h = handlers.RotatingFileHandler(path, maxBytes=MAX, backupCount=1)
    f = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S')

    h.setFormatter(f)
    logger.addHandler(h)

    return logger


def rLog(n):
    if n in logging.Logger.manager.loggerDict:
        return logging.getLogger(n)
    else:
        return init_rLog(n, P_LOG(n))
    pass


def rLog_dbg(n, msg):
    rLog(n).debug(msg)
    pass

def rLog_info(n, msg):
    rLog(n).info(msg)
    pass

def rLog_err(n, msg):
    rLog(n).error(msg)
    pass

def rLog_ctl(n, msg):
    rLog(n).critical(msg)
    pass

def rLog_alert(n, msg):
    rLog(n).warning(msg)
    pass


# pre-defined LOGGER
def FWLOG_DEBUG(msg):
    rLog('reportlog').debug(msg)

def FWLOG_INFO(msg):
    rLog('reportlog').info(msg)

def FWLOG_ERR(msg):
    rLog('reportlog').error(msg)

def HOMEPAGE_DEBUG(msg):
    rLog('homepage').debug(msg)

def HOMEPAGE_INFO(msg):
    rLog('homepage').info(msg)


if __name__ == '__main__':
    import time
    msg = 'testing...%s'
    count = 0
    while 1:
        rLog_dbg('FWlog', msg % count)
        count += 1
        rLog_info('FWlog', msg % count)
        count += 1
        rLog_err('FWlog', msg % count)
        count += 1
        rLog_ctl('FWlog', msg % count)
        count += 1
        rLog_alert('FWlog', msg % count)
        count += 1
        FWLOG_DEBUG(msg % count)
        time.sleep(1)

