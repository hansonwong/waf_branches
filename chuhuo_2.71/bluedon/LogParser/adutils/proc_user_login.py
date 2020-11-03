#!/usr/bin/env python
# coding=utf-8

import os
import json
import threading
from operator import itemgetter
from collections import namedtuple
from redis_utils.redis_op import create_redis, get_msg_from_channel
from audit_logger import rLog_dbg, rLog_err

# logger
LOG_DBG = lambda x : rLog_dbg('audit_proc_user_login', x)
LOG_ERR = lambda x : rLog_err('audit_proc_user_login', x)

# define user info structure
USER_INFO = namedtuple('USER_INFO', 'uid, uname, gid, gname, IP, isOnline')
# user online/offline notify channel
_ONLINE_USER_CHN = 'bdfw_audit_online_user'
# global redis instance
_REDIS_OBJ = create_redis()
# online_user file
ONLINE_USER = '/usr/local/bluedon/conf/online_users'


def user_status_notify(user_info, cause):
    # need uid, uname, gid, gname, ip
    if not isinstance(user_info, USER_INFO): return

    # transform user_info namedtuple -> OrderDict -> JSON
    _js_info = json.dumps(user_info._asdict())
    print _js_info
    print 'CAUSE: %s' % cause
    # notify as list just one handler will get the message
    # _REDIS_OBJ.lpush(_ONLINE_USER_CHN, _js_info)
    _REDIS_OBJ.publish(_ONLINE_USER_CHN, _js_info)

    LOG_DBG('USER:{u}, STATUS:{s}'.format(u=user_info, s='Online' \
                                          if user_info.isOnline else 'Offline'))


def reload_online_user(online_hook=None):
    # check if user-ip mapping file exists
    if not os.path.exists(ONLINE_USER):
        print '[audit_traffic_statistics] %s dose not exists' % ONLINE_USER
        return

    with open(ONLINE_USER, 'r') as fp:
        # TODO: if ONLINE_USER file is VERY BIG
        lines = fp.readlines()

    if len(lines) == 0: return
    try:
        user_group_map = json.loads(''.join(lines))
    except ValueError:
        return

    _uname = itemgetter(0)
    _gname = itemgetter(2)
    _uid = itemgetter(4)
    _gid = itemgetter(3)

    for ip, x in user_group_map.items():
        # get username
        uinfo = USER_INFO._make([_uid(x), _uname(x), _gid(x), _gname(x), ip, 1])

        # call online_hook if callable, else just call user_status_notify
        if online_hook is not None and callable(online_hook):
            online_hook(uinfo)
        else:
            user_status_notify(uinfo, 'reload_online_user')

        # if no rules for user `uname`, do nothing
        print '{user} Online as {ip}'.format(user=_uname(x), ip=ip)


class UserLoginHandler(threading.Thread):
    def __init__(self, online_hook, offline_hook, callfrom=None):
        super(UserLoginHandler, self).__init__()
        self.online_hook = online_hook if callable(online_hook) else None
        self.offline_hook = offline_hook if callable(offline_hook) else None
        self.setName('user_login_hdl')
        self.stop_event = threading.Event()
        self.callprocess = callfrom


    def run(self):
        while 1:
            if self.stop_event.isSet(): break # break while
            for _info in get_msg_from_channel(chn=_ONLINE_USER_CHN, mode='sub'):
                if self.stop_event.isSet(): break # break generator
                # _info =_REDIS_OBJ.blpop(_ONLINE_USER_CHN, timeout=1)
                # _, _js_info = _info
                if _info is None: continue
                try:
                    # JSON -> DICT -> namedtuple
                    user_info = USER_INFO(**json.loads(_info))
                except (TypeError, ValueError):
                    user_info = None
                    LOG_ERR('GET Invalid user_info:[%s]' % _info)

                if user_info is None: continue

                # online_hook
                if user_info.isOnline:
                    print 'Online'
                    self.online_hook(user_info)
                else:
                    print 'Offline'
                    self.offline_hook(user_info)


    def stop(self):
        self.stop_event.set()


    def start(self):
        super(UserLoginHandler, self).start()


# test hook
def test_hook(user_info):
    print user_info

if __name__ == '__main__':
    import time
    reload_online_user()
    u = UserLoginHandler(test_hook, test_hook)
    u.start()
    try:
        while 1: time.sleep(1)
    except KeyboardInterrupt:
        pass
    u.stop()
    u.join()
    pass
