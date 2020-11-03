#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os
import logging
from core.setting import LOG_LEVEL


def logger_init(name, filepath, level=logging.DEBUG):
    if name in logging.Logger.manager.loggerDict:
        return logging.getLogger(name)
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL or level)
    ch = logging.FileHandler(filepath)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def get_logger(name, path, level=logging.DEBUG):
    if name in logging.Logger.manager.loggerDict:
        return logging.getLogger(name)
    else:
        return logger_init(name, path, level)


def log_cmd(filename, message):
    path = '/usr/local/bluedon/log/cmd.log'
    filename = os.path.basename(filename)
    msg = '[%s] %s' % (filename, message)
    get_logger('cmd', path).debug(msg)


def log_debug(filename, mark, message):
    path = '/usr/local/bluedon/log/debug.log'
    filename = os.path.basename(filename)
    msg = '[%s] %s %s' % (filename, mark, message)
    get_logger('debug', path).debug(msg)
