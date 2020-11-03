#!/usr/bin/env python
# coding=utf-8

import time
import json
import threading
from adutils.audit_logger import rLog_dbg, rLog_err
from adutils.config1 import execute_sql as exec_3307
from adutils.redis_utils.redis_op import create_redis, get_msg_from_channel
from adutils.file_monitor import add_file_monitor, add_table_monitor, FsMonitor
from adutils.mail_utils.log_mail_config import send_email_msg, get_mail_switch_conf



EXCEPTION_CH = 'bdaudit_exception_behavior'
DBG = lambda x: rLog_dbg('system_exception_audit', x)
ERR = lambda x: rLog_err('system_exception_audit', x)

class SystemExceptionLog(threading.Thread):
    def __init__(self):
        super(SystemExceptionLog, self).__init__()
        self.setName('exception_log')
        self.event = threading.Event()
        self.redis_obj = create_redis()

        # record login information
        self.login_failure_count = {}
        self.login_failure_time = {}

        # send warning mail config
        self.fsmonitor = FsMonitor()
        self.enable_warning = 0
        self.update_alert_mail_conf()


    def update_alert_mail_conf(self, *args, **kwargs):
        _, self.enable_warning = get_mail_switch_conf()

    def run(self):
        sql = "INSERT INTO m_tblog_sys_resource (`iTime`, `sSubject`, `sContent`) \
            VALUES ({t},'{s}','{c}')"

        # send warning mail config
        add_table_monitor('m_tbconfig', self.update_alert_mail_conf)
        self.fsmonitor.start()
        source = 'warning'

        # get a generator to receive messages
        msgs = get_msg_from_channel(self.redis_obj, EXCEPTION_CH, mode='sub')
        for msg in msgs:
            if self.event.isSet():
                break

            if msg is None: continue
            # parse the message and record in database
            DBG(msg)
            js = json.loads(msg)
            msg_type = js.get('type', None)
            if msg_type is None: continue

            if msg_type in ('cpu', 'mem', 'disk'):

                # get msg_type
                if msg_type == 'cpu':
                    real_type = 'CPU'
                elif msg_type == 'mem':
                    real_type = '内存'
                elif msg_type == 'disk':
                    real_type = '磁盘'

                # # get usage and log time of msg
                # usage = js.get('info')
                logtime = js.get('logtime')
                # real_msg = '{t} 使用率 {u}%'.format(t=real_type, u=usage)
                real_msg = js['content']

                print(sql.format(t=logtime, s=real_type, c=real_msg))
                exec_3307(sql.format(t=logtime, s=real_type, c=real_msg))

                if self.enable_warning:
                    send_email_msg(source, real_type, real_msg, logtime)

            elif msg_type == 'login':
                # check login status
                login_status = js.get('status')
                if login_status == "1":
                    continue

                username = js.get('username')
                ip = js.get('ip')
                logtime = js.get('logintime')

                # chekck if count is greater than X Every Y seconds
                for u in self.login_failure_time:
                    # remove records have not update for a long time
                    if logtime - self.login_failure_time[u] > 20:
                        try:
                            self.login_failure_time.pop(u)
                            self.login_failure_count.pop(u)
                            continue
                        except KeyError:
                            # key u maybe not in self.login_failure_count
                            pass

                    if self.login_failure_count.get(u, 0) > 2:
                        # exceed in Y seconds
                        if logtime - self.login_failure_time[u] <= 10:
                            # do alert
                            real_type = '登陆异常'

                            print 'login exception: {ip}:{un} failure for {ts}'.format(
                            ip=ip, un=username, ts=self.login_failure_count[u])
                            real_msg = '{ip}'.format(ip=ip)

                            print(sql.format(t=logtime, s=real_type, c=real_msg))
                            exec_3307(sql.format(t=logtime, s=real_type, c=real_msg))

                            if self.enable_warning:
                                send_email_msg(source, real_type, real_msg, logtime)

                        # reset counter for key u
                        self.login_failure_count[u] = 0

                # add count for user
                # user = (ip, username)
                user = ip # user ip as key
                if user not in self.login_failure_count:
                    self.login_failure_count[user] = 1
                else:
                    self.login_failure_count[user] += 1


                # add login time for user
                self.login_failure_time[user] = logtime



    def start(self):
        super(SystemExceptionLog, self).start()

    def stop(self):
        self.event.set()

if __name__ == '__main__':
    sel = SystemExceptionLog()
    sel.start()
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    sel.stop()

    pass
