#!/usr/bin/env python
# coding=utf-8

import time
from jinja2 import Environment, FileSystemLoader


TEMPLATE_PATH = '/usr/local/bluedon/LogParser/utils/templates'
if __name__ == '__main__':
    ldr = FileSystemLoader(TEMPLATE_PATH)
    env = Environment(loader=ldr)
    template = env.get_template('web.template')
    ts = 1476180830
    UTC_now = time.strftime("%Y-%m-%dT%H:%M:%S",
                            time.localtime(ts))
    darg =  {'time':UTC_now, 'sip':'1.1.1.1', 'act':'Download File', 'act_obj':'aa.txt'
             ,'count':2, 'url':'www.baidu.com'}
    print template.render(log_item=darg)

    pass
