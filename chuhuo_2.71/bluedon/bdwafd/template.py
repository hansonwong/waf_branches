#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jinja2 import Environment, PackageLoader, FileSystemLoader
env = Environment(loader=FileSystemLoader('.'))

if __name__ == '__main__':
    template = env.get_template('limits.template')
    rules = [{'id':'300201', 'name': 'Accept-Charset', 'limit': '2048'},
             {'id':'300202', 'name': 'Cookie', 'limit': '32767'},
             ]
    template.stream(rules=rules).dump('limits.conf')
