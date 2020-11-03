#!/usr/bin/env python
# coding=utf-8

import os
import json
import redis
from redis_config import *


ENABLE = 'enable'
DISABLE = 'disable'
IPTABLES_CMD = '/usr/sbin/iptables {cmd}'
REMOTE_REDIS_OUT = '-{act} FWINPUT -p tcp --sport {port} -j ACCEPT'
REMOTE_REDIS_IN = '-{act} FWINPUT -p tcp --dport {port} -j ACCEPT'


REDIS_CONF_REMOTE = {
    'host': '172.16.3.123',
    'port': PORT,
    'db': DB,
    'password': 'fw@redis',
}

def tag_device_id(json_data, _id=None):
    ret = None
    if _id == None:
        _id = '301b6626432e4b2_test_id'
    tag = ',"device_id":"{0}"'.format(_id)
    ret = json_data[0:-1] + tag + json_data[-1]

    return ret

def set_redis_iptable(act, port):
    return
    if act.lower() == 'enable':
        o_cmd = REMOTE_REDIS_OUT.format(act='A', port=port)
        i_cmd = REMOTE_REDIS_IN.format(act='A', port=port)
    else:
        o_cmd = REMOTE_REDIS_OUT.format(act='D', port=port)
        i_cmd = REMOTE_REDIS_IN.format(act='D', port=port)

    print(IPTABLES_CMD.format(cmd=o_cmd))
    os.system(IPTABLES_CMD.format(cmd=o_cmd))
    print(IPTABLES_CMD.format(cmd=i_cmd))
    os.system(IPTABLES_CMD.format(cmd=i_cmd))


class RemoteRedis(object):
    def __init__(self, *args, **kwargs):
        super(RemoteRedis, self).__init__()
        self.obj = None
        self.para = kwargs
        self.port = kwargs.get('port', 6379)


    def open(self):
        return self.__enter__()

    def close(self):
        self._exit_clean()

    def publish(self, channel, msg):
        if self.obj is None:
            return

        self.obj.publish(channel, msg)

    def __enter__(self):
        try:
            set_redis_iptable(ENABLE, self.port)
            if self.obj is None:
                self.obj = redis.Redis(**self.para)

            # test if redis is connected successfully
            self.obj.ping()
        except:
            # remove the rules when errors occur
            self._exit_clean()
            raise

        print '__enter__ at RemoteRedis'
        return self.obj


    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit_clean()
        print '__exit__ from RemoteRedis'

    def _exit_clean(self):
        try:
            self.obj.connection_pool.disconnect()
        except:
            pass
        set_redis_iptable(DISABLE, self.port)
        self.obj = None


if __name__ == '__main__':
    import time
    r = RemoteRedis(**REDIS_CONF_REMOTE)
    r.open()
    r.publish('aaa', time.time())
    r.close()
    print 'exit'
    # with RemoteRedis(**REDIS_CONF_REMOTE) as r:
    #     for _ in range(10):
    #         r.publish('aaa', time.time())
    #         time.sleep(1)
    pass
