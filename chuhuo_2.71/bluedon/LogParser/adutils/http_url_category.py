#!/usr/bin/env python
# coding=utf-8


import os
import sys
import esm
import json

reload(sys)
sys.setdefaultencoding('utf-8')

from adutils.url_filter_audit import get_urllist, get_url_frompath, get_url_typepath


class HTTPCategory(object):
    def __init__(self):
        super(HTTPCategory, self).__init__()
        self.rules = dict()
        self.update_rule()


    def update_rule(self):
        rule_path = get_url_typepath()

        for name, p in rule_path.items():
            urls = get_url_frompath(p)
            finder = esm.Index()
            for host in urls:
                finder.enter(host)
            finder.fix()
            self.rules[name] = finder


    def get_host_category(self, host):
        for name, finder in self.rules.items():
            for (start, end), p in finder.query(host):
                if p: return name

        return '未知分类'

if __name__ == '__main__':
    s = HTTPCategory()
    # s.update_rule()
    print s.get_host_category('baidu.com')
    pass
