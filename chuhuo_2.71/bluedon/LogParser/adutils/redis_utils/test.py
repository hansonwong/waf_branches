#!/usr/bin/env python
# coding=utf-8

import sys
import redis
from redis_config import *
from contextlib import contextmanager


# subscribe redis channel
@contextmanager
def subscribe_channel(redis_obj, chn):
    try:
        # setup
        ps = redis_obj.pubsub()
        ps.subscribe(chn)
        yield ps.listen()
    finally:
        # cleanup
        ps.unsubscribe(chn)


def publish_channel(redis_obj, chn, content):
    redis_obj.publish(chn, content)


def create_redis(host=HOST, port=PORT, db=DB):
    try:
        re = redis.Redis(host=host, port=port, db=db)
    except Exception as e:
        re = None
        print e
    return re


if __name__ == '__main__':
    re = create_redis()
    if sys.argv[1] == 'sub':
        try:
            ch = sys.argv[2] or SUB_CHANNEL
            with subscribe_channel(re, ch) as sub:
                for i in sub:
                    print i
        except KeyboardInterrupt:
            print 'exit'
    elif sys.argv[1] == 'pub':
        # publish_channel(re, SUB_CHANNEL, 'aaa')
        with open('/usr/local/bluedon/tmp/LogParser/logs/mail.bcp.1473400424', 'r') as fp:
            l = fp.readline()
        # CH = 'netlog_email'
        # d = {"AppProto":"POP","Date":"2016-9-19 9:4:13",
        #      "SrcMac":"b8-88-e3-df-1d-87","SrcIP":"192.168.11.104",
        #      "SrcPort":"62690","DstMac":"0-10-f3-51-3e-a8",
        #      "DstIP":"220.181.12.101","DstPort":"110",
        #      "MailFrom":"'liukai_mr@163.com' <liukai_mr@163.com> ",
        #      "MailTo":"'18942557667@163.com' <18942557667@163.com> ",
        #      "MailCc":"'liukai_mr@126.com' <liukai_mr@126.com> ",
        #      "MailBcc":"","MailSubject":"机密邮件 邮件",
        #      "MailContent":"pop_content_1474247051704769.txt",
        #      "MailAttach":"1474247045952973_pop_file---- rule.txt",
        #      "MailMatch":{"Sendbox": "","Recbox": "","Subject": "","Content": "","Filename": "#病毒","Virus": ""}}

        CH = 'netlog_mysql_audit'
        d = {"action":1,
             "userip":'192.168.11.104',
             "username":'test1',
             "groupname":'testgroup',
             }

        import json
        l = json.dumps(d)
        publish_channel(re, CH, l)

    elif sys.argv[1] == 'pub1':
        # publish_channel(re, SUB_CHANNEL, 'aaa')
        with open('/usr/local/bluedon/tmp/LogParser/logs/mail.bcp.1473400424', 'r') as fp:
            l = fp.readline()
        CH = 'netlog_email'
        # publish_channel(re, SUB_CHANNEL, 'aaa')
        publish_channel(re, CH, l)
    pass
