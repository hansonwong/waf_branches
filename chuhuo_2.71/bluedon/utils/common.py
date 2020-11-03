#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
from jinja2 import Environment, FileSystemLoader

# 常用的路径常量
BASE_DIR = '/usr/local/bluedon'
LOG_BASE_PATH = '/usr/local/bluedon/log/'


def change_path_and_add_it(path):
    """
    更改当前的工作目录，如果不在sys.path则添加
    """

    os.chdir(path)
    if path not in sys.path:
        sys.path.append(path)


def init_tenv(filename=''):
    """
    初始化jinja２
    """

    tenv = Environment(loader=FileSystemLoader('/usr/local/bluedon/template/{}'.format(filename)))
    return tenv


def judge_null(data):
    """
    判断参数是否为数字类型或者是非空字符串
    args:
        data: 需判断的数据
    return:
        flag(True or False)
    """

    flag = False
    if isinstance(data, (int, long)):
        flag = True
    elif isinstance(data, (str, unicode)):
        if data.strip():
            flag = True
    return flag


def get_file_content(path):
    lines = []
    if os.path.exists(path):
        with open(path, 'r') as fp:
            lines = fp.readlines()
            lines = [l.strip().rstrip() for l in lines if len(l) > 0]
    return lines
