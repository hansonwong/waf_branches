#!/usr/bin/env python
# coding=utf-8


import os
import time
import json
import Queue
import string
import random
import threading
from calendar import monthrange
from datetime import datetime, timedelta
from collections import defaultdict
from socket import error as SocketError
from xmlrpclib import ServerProxy
from operator import itemgetter

from config import execute_sql as exec_3306
from config import fetchall_sql as fcal_3306
from config import fetchone_sql as fetch_3306

from config1 import execute_sql as exec_3307
from config1 import fetchall_sql as fcal_3307
from config1 import fetchone_sql as fetch_3307
from redis_utils.redis_op import create_redis, get_msg_from_channel, RedisChannel
from adutils.audit_logger import rLog_dbg, rLog_err


LOG_DEBUG = lambda x : rLog_dbg('audit_traffic_statistics', x)
LOG_ERR = lambda x : rLog_err('audit_traffic_statistics', x)

# table action
DROP = 'drop'
CREATE = 'create'
AUDIT_TRAFFIC_STATISTICS_CH = 'audit_flow'
AUDIT_TRAFFIC_ALERT_CH = 'netlog_flow_alert'

# user info path
# key: ip/values: username, int, group_name, group_id, user_id
ONLINE_USER = '/usr/local/bluedon/conf/online_users'

# table name
FLOW_RULE_TB = 'm_tbflow_limit'


REDIS = RedisChannel()


def humanTobyte(x, unit):
    # M = 1024*1024 bytes
    # G = 1024M    T = 1024G
    units = {'M': 1048576, 'G': 1073741824, 'T': 1099511627776}
    u = units.get(unit, 1)
    return int(x) * u


class TrafficRule(object):
    def __init__(self, max_traffic, expire_type, enable=False):
        super(TrafficRule, self).__init__()
        self.max_traffic = max_traffic
        self.expire_type = expire_type
        self.enable = enable
        self.expire_time = self.get_expire_time()


    def get_expire_time(self):
        today = datetime.today()
        last_day = today

        if self.expire_type == 'week':
            last_day = today + timedelta(7 - today.weekday())
        elif self.expire_type == 'month':
            __d = today.replace(day=28) + timedelta(days=4) # someday of next month
            last_day = __d - timedelta(__d.day - 1) # first date of next month
            pass
        else: # date
            return 0

        last_day = datetime.combine(last_day, datetime.min.time())
        last_day_ts = int(time.mktime(last_day.timetuple()))
        print self.expire_type
        print last_day_ts

        return last_day_ts


class TrafficCounter(object):
    def __init__(self, username, rule=None):
        super(TrafficCounter, self).__init__()
        self.user = username
        self.ip = set()
        self.up = 0
        self.dw = 0
        self.tt = 0 # total traffic
        self._overshoot = False
        self.last_overshoot_time = 0
        self.alert_interval = 10
        # traffic count rule, may be changed
        self.rule = rule
        self.dl_cause = ''
        self.get_pre_traffic()

    def __repr__(self):
        return 'username:{:<}, ip:{:<}, total traffic:{:<}, max_flow:{:<}\n'.format(
            self.user, self.ip, self.tt, self.rule.max_traffic)

    def add(self, up=0, dw=0):
        # add traffic according to the rule
        self.up += int(up)
        self.dw += int(dw)
        self.tt = self.tt + int(up) + int(dw)

        if self.rule is None:
            return

        # check with rule
        if self.tt > self.rule.max_traffic:
            # TODO: user downline action
            self._overshoot = True
            # self.overshoot()
            self.do_alert()

        else:
            self._overshoot = False
            pass

    def add_IP(self, ip):
        self.ip.add(ip)

    def del_IP(self, ip):
        # remove ip if exists
        try:
            self.ip.remove(ip)
        except:
            pass

    def update_rule(self, rule):
        # update_rule if changed
        self.rule = rule
        self.save_current_traffic()

    def overshoot(self):
        sql = "UPDATE m_tbuser_traffic_rule SET iOverTraffic=1 WHERE sUsername='{un}'"
        exec_3306(sql.format(un=self.user))

    def isovershoot(self):
        return self._overshoot

    def do_alert(self):
        cur_time = int(time.time())
        if abs(cur_time - self.last_overshoot_time) > self.alert_interval:
            self.save_current_traffic()
            self.last_overshoot_time = cur_time
            # set status in database
            print '{un}:{ip} is overshoot, traffic = [{tf}]'.format(
                un=self.user,ip=self.ip,tf=self.tt)
            msg = '{un}:{ip} is overshoot, traffic = [{tf}]'.format(
                un=self.user,ip=self.ip,tf=self.tt)

            content = {'itime': cur_time, 'SrcIP': self.user, 'flow_traffic': self.tt,
                       'alert_type': self.rule.expire_type, 'DstPort': 0}
            js = json.dumps(content)
            REDIS.publish('test_ch', content)

    def clear_register_ip(self):
        sql = "UPDATE m_tbuser_traffic_rule SET sIP='' WHERE sUsername='{un}'"
        exec_3306(sql.format(un=self.user))

    def is_overshoot(self):
        return self._overshoot

    def reset(self):
        self._overshoot = False
        self.up = 0
        self.dw = 0
        self.tt = 0 # total traffic
        self.last_overshoot_time = 0
        self.save_current_traffic()

    def status_check(self):
        if self.rule.expire_time < int(time.time()):
            # self.downline(cause='TIME_EXPIRE')
            self.reset()
            print '{un} is expired...'

        if self.is_overshoot():
            self.do_alert()


    def downline(self, cause=None):
        # do downline action, clear all ip of this user
        # self.ip = set()
        # the real downline action will be done by another python prog
        # self.clear_register_ip()
        pass


    # get previous traffic at the beginning
    def get_pre_traffic(self):
        sql = "SELECT iUsedTraffic, iUsedTrafficUp, iUsedTrafficDown, iOverTraffic \
            FROM m_tbuser_traffic_rule WHERE sUsername='{n}'"

        res = fetch_3306(sql.format(n=self.user))
        if res is not None:
            self.up += int(res['iUsedTrafficUp'])
            self.dw += int(res['iUsedTrafficDown'])
            self.tt += int(res['iUsedTraffic'])
            self._overshoot = int(res['iOverTraffic'])

        else:
            self.reset()


    # save current traffic before exit
    def save_current_traffic(self):
        # sql = "UPDATE m_tbuser_traffic_rule SET iUsedTraffic={t}, iUsedTrafficUp={up}, \
        #     iUsedTrafficDown={dw} WHERE sUsername='{n}';"

        sql = "INSERT INTO m_tbuser_traffic_rule (sUsername, iUsedTraffic, iUsedTrafficUp, \
            iUsedTrafficDown, iOverTraffic) VALUES('{un}', {tt},{up},{dw},{ovf}) \
            ON DUPLICATE KEY UPDATE sUsername='{un}', iUsedTraffic={tt}, \
            iUsedTrafficUp={up}, iUsedTrafficDown={dw}, iOverTraffic={ovf};"

        exec_3306(sql.format(tt=self.tt, up=self.up, dw=self.dw, un=self.user,
                             ovf=self._overshoot))


class AuditTrafficStatistics(threading.Thread):
    def __init__(self):
        super(AuditTrafficStatistics, self).__init__()
        self.setName('traffic_statistics')
        self.orgin_table = 'm_tb_audit_traffic_statistics'
        self.all_table = self.orgin_table + '_all'
        self.tb_date = lambda x : '_'.join([self.orgin_table, x])
        self.event = threading.Event()
        self.redis_obj = create_redis()
        self.work_queue = Queue.Queue(10)

        self.flow_records = {}

        self.today = lambda : time.strftime(time.localtime(), "%Y%m%d")
        self._load_date= ''
        self.last_n_date = '' # keep the value of last n_date

        # alter threshold
        self.date_threshold = 90
        self.week_threshold = 900
        self.month_threshold = 9000

        self.split = '|'
        self.keys = ['iUpdateTime', 'sIP', 'sProto', 'iDstPort', 'iUp', 'iDown']

        # delete tmp files
        os.system('rm -f /dev/shm/.db_audit_log_{n:}*'.format(n=self.orgin_table))

        # traffic counter dict of user name(un) and ip
        self.tf_counters_un = {}
        self.tf_counters_ip = {}
        self.user_traffic_rule = defaultdict(list)


    @property
    def load_date(self):
        return self._load_date

    @load_date.setter
    def load_date(self, v):
        # create new table when a new day comes
        if len(v) != 8: return
        if self._load_date!= v:
            # create a new table
            self.alter_sub_table(v, CREATE)
            self._load_date = v
            pass


    def update_threshold(self):
        # update threshold, just a test function
        self.date_threshold = 90
        self.week_threshold = 900
        self.month_threshold = 9000


    def flow_alert(self, key, bw, itime, dport):
        # do alert action, send msg to redis
        # print 'key[{k}] bw={b} is over threshold {t}'.format(k=key, b=bw,
        #                                                      t=self.date_threshold)
        ip = key.split('_')[-1]
        tp = '_'.join(key.split('_')[0:-1])
        content = {'itime': itime, 'SrcIP': ip, 'flow_traffic': bw,
                   'alert_type': tp, 'DstPort': dport}
        js = json.dumps(content)
        self.redis_obj.publish(AUDIT_TRAFFIC_ALERT_CH, js)


    def ttl_key(self, key):
        # return remaining times of a key
        _ttl = self.redis_obj.ttl(key)
        return 0 if _ttl is None else int(_ttl)


    def set_key(self, key, bw, itime, dport):
        # if key is already exists, set value += bw
        _bw = bw + self.get_key(key)
        # check flow traffic here
        if _bw > self.date_threshold:
            # do the alert job and del key
            self.flow_alert(key, _bw, itime, dport)
            self.del_key(key)
        else:
            self.redis_obj.set(key, _bw)


    def expire_key(self, key, exp):
        # set expire time for key
        self.redis_obj.expireat(key, exp)


    def get_key(self, key):
        # get key by name
        'return bw or 0'
        bw = self.redis_obj.get(key)
        return 0 if bw is None else int(bw)


    def del_key(self, key):
        # delete a key by name
        self.redis_obj.delete(key)


    def del_allkeys(self, pat):
        # delete all keys
        for k in self.redis_obj.keys(pat):
            self.redis_obj.delete(k)


    def record_key(self, ip, n_date, bw, itime, dport):

        # utils lambda
        self.dt_ts = lambda x : int(time.mktime(x.timetuple()))
        self.dt_str = lambda x : datetime.strftime(x, "%Y%m%d")
        self.str_dt = lambda x, y="%Y%m%d" : datetime.strptime(x, y)
        self._key_date = lambda x : 'audit_flow_date_{}'.format(x)
        self._key_week = lambda x : 'audit_flow_week_{}'.format(x)
        self._key_month = lambda x : 'audit_flow_month_{}'.format(x)
        self._key_alert = lambda x : '{}_alert'.format(x)

        # datetime result cache
        if self.last_n_date != n_date:
            print 'init datetime'
            # datetime and expire datetime of date, weekday, and month date
            self.dt_date = self.str_dt(n_date)
            self.dt_date_exp = self.dt_date + timedelta(days=1)

            self.dt_week = self.dt_date - timedelta(self.dt_date.weekday())
            self.dt_week_exp = self.dt_date + timedelta(7 - self.dt_date.weekday())

            self.dt_month = self.dt_date - timedelta(self.dt_date.day - 1)
            __d = self.dt_month.replace(day=28) + timedelta(days=4) # someday of next month
            self.dt_month_exp = __d - timedelta(__d.day - 1) # first date of next month

            self.last_n_date = n_date

        # set 3 keys for an IP
        _date = self._key_date(ip)
        _date_exp = self.dt_ts(self.dt_date_exp)

        self.set_key(_date, bw, itime, dport)
        self.expire_key(_date, _date_exp)

        _week = self._key_week(ip)
        _week_exp = self.dt_ts(self.dt_week_exp)

        self.set_key(_week, bw, itime, dport)
        self.expire_key(_week, _week_exp)

        _month = self._key_month(ip)
        _month_exp = self.dt_ts(self.dt_month_exp)

        self.set_key(_month, bw, itime, dport)
        self.expire_key(_month, _month_exp)


    def update_summary_table(self, sub_table_list):
        if len(sub_table_list) == 0:
            # log error here
            print 'sub_table_list is null'
            return
        drop_sql = "DROP TABLE IF EXISTS {all_tb};"
        create_sql = "CREATE TABLE IF NOT EXISTS `{tb}` LIKE `{orgin}`;"
        alter_sql = "ALTER TABLE {all_tb} ENGINE=MERGE UNION=({sub_tbs}) INSERT_METHOD=LAST"

        # drop all table first
        exec_3307(drop_sql.format(all_tb=self.all_table))
        # create all table again
        exec_3307(create_sql.format(tb=self.all_table, orgin=self.orgin_table))
        # alter table
        sub_table = ','.join(sub_table_list)
        exec_3307(alter_sql.format(all_tb=self.all_table, sub_tbs=sub_table))


    def get_sub_table_list(self):
        sql = "SELECT TABLE_NAME FROM information_schema.`TABLES` \
            WHERE TABLE_NAME like 'm_tb_audit_traffic_statistics_2%'"

        ret = []
        for res in fcal_3307(sql):
            ret.append(res['TABLE_NAME'])

        return ret


    def alter_sub_table(self, n_date, action):
        if action not in ('create', 'drop'):
            print 'action [%s] is not support'
            return

        if action == 'create':
            self._create_sub_table(n_date)
        elif action == 'drop':
            self._drop_sub_table(n_date)

        sub_table_list = self.get_sub_table_list()
        self.update_summary_table(sub_table_list)


    def _create_sub_table(self, n_date):
        sql = "CREATE TABLE IF NOT EXISTS `{tb}` LIKE `{orgin}`;"
        tb_name = self.tb_date(n_date)
        exec_3307(sql.format(tb=tb_name, orgin=self.orgin_table))


    def _drop_sub_table(self, n_date):
        sql = "DROP TABLE IF EXISTS {tb};"
        tb_name = self.tb_date(n_date)
        exec_3307(sql.format(tb=tb_name))


    def _create_tmp_file(self, name):
        while 1:
            randstr = ''.join (random.sample(string.ascii_letters+string.digits,9))
            data_file = r'/dev/shm/.db_audit_log_' + name + '_' + randstr + '.xyz'
            if os.path.exists(data_file):
                continue
            else:
                # os.system('touch %s' % data_file)
                break

        return data_file


    def _save_to_file(self, args, name):
        _file = self._create_tmp_file(name)
        # print args
        with open(_file, 'a+') as fp:
            # parse records
            for k in args:
                line = k + '|' + '|'.join('{0}'.format(n) for n in args[k])
                fp.write('%s\n' % line)
            # fp.write('\n'.join(args))
            pass
        return _file, name


    def add_task(self, args, tb):
        if not self.work_queue.full():
            f, n = self._save_to_file(args, tb)
            print('[%s] loading LINES=[%s]' % (n, len(args)))
            print 'add_task: ', f
            self.work_queue.put((f, n))
        else:
            print('[add_task]task queue is FULL ignore')
        pass


    # run in another thread
    def load_data_infile(self):
        t = None
        # max mysql connections
        self._tCount = 0
        _tMAX = 1
        lock = threading.Lock()

        while 1:
            if self.event.isSet():
                break

            # if get empty data
            if not self.work_queue.empty():
                _file, _name = self.work_queue.get()
            else:
                time.sleep(1)
                continue

            # check if new table is need to create
            self.load_date = _name.split('_')[-1]

            LOG_DEBUG('%s Get %s, %s' % (self.orgin_table, _file, _name))
            # if _file and _name:
            sql = ('load data infile "%s" ignore into table `%s` '
                   'character set utf8 fields TERMINATED BY "{sp}" '
                   'LINES TERMINATED BY "\n" ({k:})').format(sp=self.split,
                                                             k=','.join(self.keys))


            def mysql_task(f, n):
                try:
                    lock.acquire()
                    self._tCount += 1
                    lock.release()
                    LOG_DEBUG('committing %s at table %s...' % (f, n))
                    LOG_DEBUG('_tCount = %s' % self._tCount)
                    _st = time.time()
                    exec_3307(sql % (f, n))
                    os.system('rm -f %s' % f)
                    LOG_DEBUG('committing %s at table %s...DONE++++++' % (f, n))
                    LOG_DEBUG('committing TIME=[%s]' % (time.time() - _st))
                except Exception as e:
                    if lock.locked():
                        lock.release()
                    os.system('rm -f %s' % f)
                    LOG_DEBUG('[mysql_task]error:committing %s at table %s...%s' % (f, n, e))
                finally:
                    lock.acquire()
                    self._tCount -= 1
                    if self._tCount < 0:
                        self._tCount = 0
                    lock.release()
                    LOG_DEBUG('_tCount = %s' % self._tCount)


            def ignore_task(f, n):
                try:
                    LOG_DEBUG('_tCount = %s' % self._tCount)
                    os.system('rm -f %s' % f)
                    LOG_DEBUG('ignore task %s at table %s...REMOVED------' % (f, n))
                except Exception as e:
                    LOG_DEBUG('[ignore task]error %s at table %s...%s' % (f, n, e))

            try:
                LOG_DEBUG('create_time=%s' % os.path.getctime(_file))
                if self._tCount < _tMAX:
                    t = threading.Thread(target=mysql_task, args=(_file, _name))
                    t.setDaemon(True)
                    t.setName('ad_tf_load')
                    t.start()
                    time.sleep(0.1)
                    continue
                # else:
                #     if task is running, just wait
                #     ignore_task(_file, _name)
                #     time.sleep(1)
            except Exception as e:
                LOG_ERR('[load_data_infile]%s' % e)
            # else:
                # pass
                # LOG_DEBUG('%s get the last message...haha' % self.orgin_table)
            time.sleep(1)

        if t is not None:
            LOG_DEBUG('waiting [%s] load_data_infile exit...' % self.orgin_table)
            if lock.locked():
                lock.release()
                LOG_DEBUG('load_data_infile: the lock is still locked release the lock at last...')
            t.join()
            pass
        LOG_DEBUG('[%s]load_data_infile exit...' % self.orgin_table)
        pass


    def parser(self, msg):
        # do the statistic job here
        items = eval(msg)
        if len(items) == 0: return None, None
        idate = None
        itime = None
        try:
            _d = items[0].get('Date')
            idate = ''.join(_d.split()[0].split('-'))
            itime = time.mktime(time.strptime(_d, "%Y-%m-%d %H:%M:%S"))
            for item in items:
                # print item
                sip = item.get('SrcIP')
                app = item.get('AppProto')
                dport = item.get('DstPort')
                up_bw = item.get('Ups')
                dw_bw = item.get('Downs')
                tt_bw = int(up_bw) + int(dw_bw) # total traffic

        except Exception as e:
            print e

        return idate, itime, sip, app, dport, up_bw, dw_bw, tt_bw
        # return '', '', '', '', '', ''
        # return msg.split('|')

    # update user rule
    def update_user_rule(self, user_id=None, group_id=None):
        ret = defaultdict(dict)

        EXP_TYPE = {2: 'week', 3: 'month'}
        # get rules configuration from talbes, and update for every user in table
        SQL = 'SELECT * FROM m_tbflow_limit WHERE iStatus=1 ORDER BY iOrder ASC;'
        for r in fcal_3306(SQL):
            # get rule info
            expire_type = EXP_TYPE.get(int(r['iEffectiveTime']), 0)
            max_flow = humanTobyte(r['iLimit'], r['iLimitType'])
            # if get user group
            if int(r['iType']) == 2:
                gid = int(r['iTypeValue'])
                # get all user in group
                GID_SQL = 'SELECT sUserName FROM m_tbusers WHERE iGroupID={};'
                for u in fcal_3306(GID_SQL.format(gid)):
                    ret[u['sUserName']].update(expire_type=expire_type,
                               max_flow=max_flow)
                    pass
            # else single user
            elif int(r['iType']) == 1:
                uid = int(r['iTypeValue'])
                UID_SQL = 'SELECT sUserName FROM m_tbusers WHERE id={};'
                u = fetch_3306(UID_SQL.format(uid))
                ret[u['sUserName']].update(expire_type=expire_type,
                           max_flow=max_flow)
        pass
        # remove old user
        cur_Users = set(ret.keys())
        orgin_Users = set(self.tf_counters_un.keys())
        for user in (orgin_Users - cur_Users):
            print 'del user[%s]' % user
            # save user data before delelte user
            self.tf_counters_un[user].save_current_traffic()
            self.unregister_userip(user=user)
            # self.tf_counters_un.pop(user)
        for user in ret:
            user_rule = ret[user]
            rule = TrafficRule(user_rule['max_flow'], user_rule['expire_type'])
            if user in self.tf_counters_un:
                print 'update user[%s] rule' % user
                self.tf_counters_un[user].update_rule(rule)

            else:
                print 'add user[%s]' % user
                self.tf_counters_un[user] = TrafficCounter(user, rule)

        # print self.tf_counters_un


    # update user's ip
    def update_user_ip(self):

        # check if user-ip mapping file exists
        if not os.path.exists(ONLINE_USER):
            print '[audit_traffic_statistics] %s dose not exists' % ONLINE_USER
            return ret

        with open(ONLINE_USER, 'r') as fp:
            # TODO: if ONLINE_USER file is VERY BIG
            lines = fp.readlines()

        try:
            if len(lines) > 0:
                user_group_map = json.loads(''.join(lines))
        except ValueError:
            return

        _uname = itemgetter(0)
        # _gname = itemgetter(2)
        # _uid = itemgetter(4)
        # _gid = itemgetter(3)

        # remove old ip
        cur_IPs = defaultdict(set)
        for ip, info in user_group_map.items():
            cur_IPs[_uname(info)].add(ip)

        for user in self.tf_counters_un:
            for ip in (set(self.tf_counters_un[user].ip)- cur_IPs[user]):
                self.unregister_userip(ip=ip)

        for ip in user_group_map:
            uip_info = user_group_map[ip]
            # get username
            uname = _uname(uip_info)

            # if no rules for user `uname`, do nothing
            if uname not in self.tf_counters_un:
                # delete record of uname from m_tbuser_traffic_rule
                exec_3306("DELETE FROM m_tbuser_traffic_rule WHERE \
                          sUsername='{}';".format(uname))
                print 'no rule for user[%s]' % uname
                continue

            # if rule exists for `uname` add ip to this rule
            print 'add IP %s' % ip
            self.tf_counters_un[uname].add_IP(ip)
            self.tf_counters_ip[ip] = self.tf_counters_un[uname]


    def unregister_userip(self, user=None, ip=None):
        print 'in unregister_userip'

        # unregister_ip
        if ip is not None and ip in self.tf_counters_ip:
            print 'unregister ip {ip} to user {u}'.format(
                ip=ip, u=self.tf_counters_ip[ip].user)
            # remove ip from traffic counter object
            self.tf_counters_ip[ip].del_IP(ip)
            # remove traffic counter object from list
            self.tf_counters_ip.pop(ip)

        # unregister_user
        if user is None: return
        print 'unregister user {u}'.format(u=user)
        for ip in self.tf_counters_un[user].ip:
            # remove ip in tf_counters_ip
            if ip in self.tf_counters_ip:
                self.tf_counters_ip.pop(ip)
        if user in self.tf_counters_un:
            self.tf_counters_un.pop(user)


    def run(self):
        max_line = 500
        max_time = 10
        max_none = 30
        last_date = 0
        last_time = 0
        none_count = 0
        current_time = 0


        # start load_data_infile thread
        # self.load_thread = threading.Thread(target=self.load_data_infile)
        # self.load_thread.setName('ad_tra_statis')
        # self.load_thread.setDaemon(True)
        # self.load_thread.start()

        msgs = get_msg_from_channel(self.redis_obj, AUDIT_TRAFFIC_STATISTICS_CH,
                                    mode='sub')
        for msg in msgs:
            if self.event.isSet():
                break

            if int(time.time()) - current_time > 5:
                current_time = int(time.time())
                print 'user list'
                print self.tf_counters_un
                print 'ip list'
                print self.tf_counters_ip
                self.update_user_rule()
                self.update_user_ip()
                print '-'*40
                # expire user check
                for user in self.tf_counters_un:
                    self.tf_counters_un[user].status_check()
                    pass


            if msg is None:
                if none_count >= 30 and len(self.flow_records) > 0:
                    print 'get 30 none_count'
                    none_count == 0
                    self.flow_records = {}
                continue

            idate, itime, sip, app, dport, up_bw, dw_bw, tt_bw = self.parser(msg)

            if sip in self.tf_counters_ip:
                self.tf_counters_ip[sip].add(up_bw, dw_bw)
            else:
                # this ip has not statistic rule
                pass

            # # check if date is changed
            # if last_date != idate:
            #     print 'last_date is different'
            #     if len(self.flow_records) > 0:
            #         print 'load in last_date'
            #         self.add_task(self.flow_records, self.tb_date(last_date))
            #         self.flow_records = {}
            #         pass

            #     last_date = idate
            #     last_time= itime

            # elif len(self.flow_records) >= max_line:
            #     print 'load in max_line'
            #     self.add_task(self.flow_records, self.tb_date(last_date))
            #     self.flow_records = {}
            #     last_time= itime

            # elif itime - last_time >= max_time:
            #     print 'last_time is max_time seconds ago'
            #     if len(self.flow_records) > 0:
            #         print 'load in last_time'
            #         self.add_task(self.flow_records, self.tb_date(last_date))
            #         self.flow_records = {}
            #         pass

            #     last_time = itime

            # # record IP and flow traffic in redis(for traffic alert)
            # self.record_key(sip, idate, tt_bw, itime, dport)
            # this_key = '|'.join((str(itime), sip, app, dport))
            # # record in a dict(for traffic statistic)
            # if this_key not in self.flow_records:
            #     self.flow_records[this_key] = (int(up_bw), int(dw_bw))
            # else:
            #     u = self.flow_records[this_key][0] + int(up_bw)
            #     d = self.flow_records[this_key][1] + int(dw_bw)
            #     self.flow_records[this_key] = (u, d)

            # # time



            # # record in database

        if len(self.flow_records) != 0:
            # do clean job
            pass

        # save current traffic in database
        for user in self.tf_counters_un:
            self.tf_counters_un[user].save_current_traffic()

        print 'Exit done'


    def start(self):
        super(AuditTrafficStatistics, self).start()


    def stop(self):
        self.event.set()



if __name__ == '__main__':
    # o = TrafficRule('','week')
    # o = TrafficRule('','month')
    # o.remaining_time()

    ats = AuditTrafficStatistics()
    # ats.update_user_rule()
    # ats.update_user_ip()
    # ats.update_user_traffic_rule()
    ats.start()
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    ats.stop()
    pass

