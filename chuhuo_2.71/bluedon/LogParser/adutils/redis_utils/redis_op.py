#!/usr/bin/env python
# coding=utf-8

import sys
import redis
import time
from redis_config import *
from contextlib import contextmanager
# from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR
from ..audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR

REDIS_CHN_OF_TB = lambda x : 'AUDIT_NEW_LOGFILE_{}'.format(x).upper()
REDIS_CHN_EXIT = 'AUDIT_NEW_LOGFILE_REDIS_CHN_EXIT'
REDIS_CHN_MYSQL = 'netlog_mysql_audit'

# subscribe redis channel
@contextmanager
def subscribe_channel(redis_obj, chn):
    try:
        # setup
        ps = redis_obj.pubsub()
        ps.subscribe(chn)
        yield ps.listen()
    except (KeyboardInterrupt, RuntimeError):
        pass
    finally:
        # cleanup
        ps.unsubscribe(chn)


def get_msg_from_channel(redis_obj=None, chn=None, mode='psubscribe'):
    """
        Usage:
                for msg in get_msg_from_channel(CH):
                    do sth with msg
    """
    if chn is None:
        # log here
        print 'get_msg_from_channel: No Channel is set'

    redis_obj = redis_obj or create_redis()
    if redis_obj is None:
        # log here
        print 'can\' t create redis_obj'
    # connect to redis and channel
    ps = redis_obj.pubsub()
    if mode == 'psubscribe':
        ps.psubscribe(chn)
    else:
        ps.subscribe(chn)

    try:
        while 1:
            # get message from redis channel
            item = ps.get_message()
            if item is None:
                yield None
                time.sleep(1)
                # yield [] or not?
                # yield []
            elif item['type'][-7:] == 'message':
                # data validate before yield?
                if mode == 'psubscribe':
                    yield (item['channel'], item['data'])
                else:
                    yield item['data']

    except StopIteration:
        print 'stop StopIteration'
    except GeneratorExit:
        print 'stop GeneratorExit'
    except redis.ConnectionError as e:
        print e.message
    finally:
        ps.close()
        redis_obj.connection_pool.disconnect()
        print 'stop get_msg_from_channel'

    # log here
    print 'get_msg_from_channel Exit'



def publish_channel(redis_obj, chn, content):
    redis_obj.publish(chn, content)


def create_redis(host=HOST, port=PORT, db=DB, pw=PW):
    try:
        re = redis.Redis(host=host, port=port, db=db)
        re.ping()
    except Exception as e:
        re = None
        ADLOG_ERR('create_redis ERROR: %s' % e)
    return re

def publish_audit(content, chn=REDIS_CHN_MYSQL):
    redis_obj = create_redis()
    redis_obj.publish(chn, content)


class RedisChannel(object):
    def __init__(self, host=HOST, port=PORT, db=DB, pw=PW, auth=False):
        super(RedisChannel, self).__init__()
        if auth:
            self.para = dict(host=host, port=port, db=db, password=pw)
        else:
            self.para = dict(host=host, port=port, db=db)
        self.auth = auth
        self.obj = None
        self.retry = 0

        self.init_redis()


    def init_redis(self):
        self.obj = self.new_instance()


    def new_instance(self):
        obj = None
        try:
            obj = redis.Redis(**self.para)
            obj.ping()
        except Exception as e:
            # log here
            print '[RedisChannel]: create error'
            print e

        return obj


    def reconnect(self):
        # disconnect
        if self.obj is not None:
            try:
                self.obj.connection_pool.disconnect()
            except:
                pass

        while self.retry < 10:
            self.retry += 1
            self.init_redis()
            time.sleep(self.retry * 2)

            # reconnect success
            if self.obj is not None:
                self.retry = 0
                return

        print '[RedisChannel]reconnect faild'



    def publish(self, ch, msg):
        if self.obj is None:
            # log here
            print '[RedisChannel]No Avaliable Redis Connection'
            return

        try:
            self.obj.publish(ch, msg)
        except redis.ConnectionError as e:
            print '[RedisChannel]ConnectionError %s' % e
            self.reconnect()





if __name__ == '__main__':
    re = create_redis()
    if sys.argv[1] == 'sub':
        try:
            with subscribe_channel(re, SUB_CHANNEL) as sub:
                for i in sub:
                    print i
        except KeyboardInterrupt:
            print 'exit'
    elif sys.argv[1] == 'pub':
        # publish_channel(re, SUB_CHANNEL, 'aaa')
        with open('/usr/local/bluedon/tmp/LogParser/logs/mail.bcp.1473400424', 'r') as fp:
            l = fp.readline()
        CH = 'netlog_email'
        # publish_channel(re, SUB_CHANNEL, 'aaa')
        publish_channel(re, CH, l)
    else:
        # normal test
        CH = 'bdfw_fsmonitor_*'
        CH = 'bdfw_reg_fsmonitor_channel'
        msgs = get_msg_from_channel(re, CH, mode='1')
        count = 0
        try:
            for i in msgs:
                count += 1
                if count > 3:
                    break
                    # msgs.close()
                print i
        except KeyboardInterrupt:
            print 'KeyboardInterrupt'
        print 'done'
    pass
