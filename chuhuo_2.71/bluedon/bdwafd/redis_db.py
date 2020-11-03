#!/usr/bin/env python
# -*- coding:utf8 -*-
# redis连接

import redis
from contextlib import contextmanager
from config import config

HOST = config['redis']['host']
PORT = config['redis']['port']


def redis_conn(host=HOST, port=PORT):
    '''
    redis连接
    '''
    try:
        rc = redis.Redis(host=host, port=port)
        rc.ping()
    except Exception, e:
        rc = None
    return rc


@contextmanager
def redis_subscripe(redis_obj, chn):
    '''
    订阅
    '''
    try:
        ps = redis_obj.pubsub()
        ps.subscribe(chn)
        yield ps.listen()
    except (KeyboardInterrupt, RuntimeError):
        pass
    finally:
        ps.unsubscribe(chn)


def redis_public(chn):
    '''
    发布
    '''
    pass
