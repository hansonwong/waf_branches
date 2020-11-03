#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from jinja2 import Environment, FileSystemLoader
from db import session_scope, ErrorList
from config import config
from logging import getLogger

def gen_errorpage(statusCode):
    '''
    gen error(404,403..) html page
    '''
    try:
        with session_scope() as session:
            errorpage = session.query(ErrorList).filter(
                            ErrorList.status_code == statusCode).one()
            g = {'errorpage': errorpage}
            tenv = Environment(loader=FileSystemLoader('data/template/'))
            tenv.get_template('errorpage').stream(g).dump(
                os.path.join(config['htmlmodedir'], '%s.html' % statusCode))
    except Exception, e:
        getLogger('main').error(e)
    getLogger('main').info('gen errorpage end')


if __name__ == '__main__':
    gen_errorpage('403')
