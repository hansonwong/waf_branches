#!/usr/bin/env python
# coding=utf-8


import os
import sys
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from usermanage.authentication import auth_downline
# if '/usr/local/bluedon' in sys.path:
#     sys.path.remove('/usr/local/bluedon')
import time
import json
import Queue
import string
import random
import threading
import commands
from IPy import IP
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
from adutils.proc_user_login import UserLoginHandler
from adutils.file_monitor import FsMonitor, add_table_monitor


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

# traffic interval
COUNT_MIN = 30


REDIS = RedisChannel()


def humanTobyte(x, unit):
    # M = 1024*1024 bytes
    # G = 1024M    T = 1024G
    units = {'M': 1048576, 'G': 1073741824, 'T': 1099511627776}
    u = units.get(unit, 1)
    return int(x) * u


class TrafficRule(object):
    def __init__(self, max_traffic, expire_type, action, enable=False):
        super(TrafficRule, self).__init__()
        self.max_traffic = max_traffic
        self.expire_type = expire_type
        self.enable = enable
        self.expire_time = self.get_expire_time()
        self.action = action


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
        LOG_DEBUG(self.expire_type)
        LOG_DEBUG(last_day_ts)

        return last_day_ts


class TrafficCounter(object):
    def __init__(self, username, groupname, rule=None):
        super(TrafficCounter, self).__init__()
        self.user = username
        self.group = groupname
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

        # do nothing if no rule for this counter
        if self.rule is None:
            return

        # check with rule, do altert when overshoot
        if self.tt > self.rule.max_traffic:
            self._overshoot = True
            self.do_alert()

        else:
            # add traffic according to the rule
            self.up += int(up)
            self.dw += int(dw)
            self.tt = self.tt + int(up) + int(dw)
            if self._overshoot: self._overshoot = False
            pass

    def add_IP(self, ip):
        self.ip.add(ip)

    def del_IP(self, ip):
        # remove ip if exists
        try:
            self.ip.remove(ip)
        except:
            pass
    def len_IP(self):
        return len(self.ip)

    def update_rule(self, rule):
        # update_rule if changed
        self.rule = rule
        self.add()
        self.save_current_traffic()

    def set_overshoot(self, isTrue):
        """isTrue must be 0 (for False) or 1 (for True)"""
        if isTrue not in (0, 1): isTrue = 0 # default not overshoot
        sql = "UPDATE m_tbuser_traffic_rule SET iOverTraffic={i} WHERE sUsername='{un}'"
        exec_3306(sql.format(i=isTrue, un=self.user))

    def isovershoot(self):
        return self._overshoot

    def do_alert(self):
        cur_time = int(time.time())
        if abs(cur_time - self.last_overshoot_time) > self.alert_interval:
            self.save_current_traffic()
            self.last_overshoot_time = cur_time
            # set status in database
            LOG_DEBUG('{un}:{ip} is overshoot, traffic = [{tf}]'.format(
                un=self.user,ip=self.ip,tf=self.tt))
            msg = '{un}:{ip} is overshoot, traffic = [{tf}]'.format(
                un=self.user,ip=self.ip,tf=self.tt)

            content = {'itime': str(cur_time), 'SrcIP': self.user, 'flow_traffic': str(self.tt),
                       'alert_type': self.rule.expire_type, 'DstPort': '0'}
            js = json.dumps(content)
            REDIS.publish(AUDIT_TRAFFIC_ALERT_CH, js)

    def clear_register_ip(self):
        sql = "UPDATE m_tbuser_traffic_rule SET sIP='' WHERE sUsername='{un}'"
        exec_3306(sql.format(un=self.user))

    def is_overshoot(self):
        return self._overshoot

    def reset(self):
        LOG_DEBUG('reset for user[%s]' % self.user)
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
            LOG_DEBUG('{un} is expired...'.format(un=self.user))

        if self.is_overshoot():
            self.do_alert()

    def should_downline(self):
        return self.is_overshoot() and self.rule.action == 1

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

            LOG_DEBUG('get_pre_traffic for user[%s] total=[%s]' % (self.user, self.tt))

        else:
            # no record ever for user
            LOG_DEBUG('no record exists for user[%s]' % self.user)
            self.reset()


    # save current traffic before exit
    def save_current_traffic(self):
        # sql = "UPDATE m_tbuser_traffic_rule SET iUsedTraffic={t}, iUsedTrafficUp={up}, \
        #     iUsedTrafficDown={dw} WHERE sUsername='{n}';"
        # check if user is registered
        GET_USER = 'SELECT id FROM m_tbusers WHERE sUsername="{}"'.format(self.user)
        user_in_system = fetch_3306(GET_USER)
        if user_in_system:
            LOG_DEBUG('save_current_traffic for user[%s] total=%s' % (self.user, self.tt))

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
        self.tf_lock = threading.Lock()

        self.flow_records = {}

        self.today = lambda : time.strftime(time.localtime(), "%Y%m%d")
        self._load_date= ''
        self.last_n_date = '' # keep the value of last n_date

        # alter threshold
        self.date_threshold = 90
        self.week_threshold = 900
        self.month_threshold = 9000

        self.split = '|'
        self.keys = ['iUpdateTime', 'sIP', 'sProto', 'iDstPort', 'iAppMark', \
                     'sUsername', 'sGroupname', 'iUp', 'iDown']

        # delete tmp files
        os.system('rm -f /dev/shm/.db_audit_log_{n:}*'.format(n=self.orgin_table))

        # traffic counter dict of user name(un) and ip
        self.tf_counters_un = {}
        self.tf_counters_ip = {}
        self.user_traffic_rule = defaultdict(list)

        # login info
        self.uip_map = defaultdict(set) # user_id -> ip mapping
        self.gip_map = defaultdict(set) # user_group_id -> ip mapping
        self.user_handler = UserLoginHandler(self.online_hook, self.offline_hook,
                                             callfrom='AuditTrafficStatistics')

        # current_online_ip
        self.current_online_ip = dict()

        self.update_user_rule()
        self.reload_online_user()

        # no traffic expire_time
        self.no_traffic_expire_time = 0
        self.no_traffic_expire_way = 0
        self.update_expire_time_and_way()


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

    def acquire_tf_lock(self):
        self.tf_lock.acquire()

    def release_tf_lock(self):
        if self.tf_lock.locked(): self.tf_lock.release()

    def online_hook(self, user_info):
        # self.uip_map[user_info.uid].add(user_info.IP)
        # self.gip_map[user_info.gid].add(user_info.IP)

        self.acquire_tf_lock()
        try:
            self.current_online_ip[user_info.IP] = int(time.time())
            self.update_user_ip(user_info)
        finally:
            self.release_tf_lock()

        # find rule for this user_ip
        pass

    def offline_hook(self, user_info):
        # if user_info.IP in self.uip_map[user_info.uid]:
        #     self.uip_map[user_info.uid].remove(user_info.IP)
        #     if len(self.uip_map[user_info.uid]) == 0:
        #         self.uip_map.pop(user_info.uid)
        # if user_info.IP in self.gip_map[user_info.gid]:
        #     self.gip_map[user_info.gid].remove(user_info.IP)
        #     if len(self.gip_map[user_info.gid]) == 0:
        #         self.gip_map.pop(user_info.gid)
        self.acquire_tf_lock()
        try:
            self.update_user_ip(user_info)
        finally:
            self.release_tf_lock()
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
            LOG_DEBUG('init datetime')
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
            LOG_DEBUG('sub_table_list is null')
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
            LOG_DEBUG('action [%s] is not support' % action)
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
            # LOG_DEBUG('[%s] loading LINES=[%s]' % (n, len(args)))
            # LOG_DEBUG('add_task: %s' % f)
            self.work_queue.put((f, n))
        else:
            LOG_DEBUG('[add_task]task queue is FULL ignore')
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
                    # LOG_DEBUG('committing %s at table %s...' % (f, n))
                    # LOG_DEBUG('_tCount = %s' % self._tCount)
                    _st = time.time()
                    exec_3307(sql % (f, n))
                    os.system('rm -f %s' % f)
                    # LOG_DEBUG('committing %s at table %s...DONE++++++' % (f, n))
                    # LOG_DEBUG('committing TIME=[%s]' % (time.time() - _st))
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
                    # LOG_DEBUG('_tCount = %s' % self._tCount)


            def ignore_task(f, n):
                try:
                    LOG_DEBUG('_tCount = %s' % self._tCount)
                    os.system('rm -f %s' % f)
                    LOG_DEBUG('ignore task %s at table %s...REMOVED------' % (f, n))
                except Exception as e:
                    LOG_DEBUG('[ignore task]error %s at table %s...%s' % (f, n, e))

            try:
                # LOG_DEBUG('create_time=%s' % os.path.getctime(_file))
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
                pass
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
        items = json.loads(msg)
        # if len(items) == 0: return None, None
        if len(items) == 0: yield None, None
        idate = None
        itime = None
        try:
            _d = items[0].get('Date')
            idate = ''.join(_d.split()[0].split('-'))
            itime = int(time.mktime(time.strptime(_d, "%Y-%m-%d %H:%M:%S")))
            itime = itime - (itime % COUNT_MIN)
            for item in items:
                sip = item.get('SrcIP')
                dip = item.get('DstIP')
                app = item.get('AppProto')
                dport = item.get('DstPort')
                up_bw = item.get('Ups')
                dw_bw = item.get('Downs')
                tt_bw = int(up_bw) + int(dw_bw) # total traffic
                mark = str(item.get('PktMark', 0))

                yield idate, itime, sip, dip, app, dport, up_bw, dw_bw, tt_bw, mark

        except Exception as e:
            LOG_DEBUG(e)

        # return idate, itime, sip, app, dport, up_bw, dw_bw, tt_bw

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
            rule_id = int(r['id'])
            rule_type = int(r['iType'])
            action = int(r['iAction'])
            gid = 0
            # if get user group
            if rule_type == 2:
                gid = int(r['iTypeValue'])
                # get all user in group
                GID_SQL = 'SELECT sUserName FROM m_tbusers WHERE iGroupID={};'
                for u in fcal_3306(GID_SQL.format(gid)):
                    ret[u['sUserName']].update(expire_type=expire_type,
                               max_flow=max_flow, action=action)
                    pass
            # else single user
            elif rule_type == 1:
                uid = int(r['iTypeValue'])
                UID_SQL = 'SELECT sUserName, iGroupID FROM m_tbusers WHERE id={};'
                u = fetch_3306(UID_SQL.format(uid))
                if u is not None:
                    ret[u['sUserName']].update(expire_type=expire_type,
                               max_flow=max_flow, action=action)
                    gid = u['iGroupID']

            # get group name
            groupname = 'Anonymous'
            if gid > 0:
                g = fetch_3306("SELECT sGroupName FROM m_tbgroup WHERE id='{}';".format(gid))
                if g is not None: groupname = g['sGroupName']
        pass
        # remove users thoes in last rule table but not in current rule table
        cur_Users = set(ret.keys()) # current users
        orgin_Users = set(self.tf_counters_un.keys()) # previous users
        for user in (orgin_Users - cur_Users): # users in previous but not current
            LOG_DEBUG('del user[%s]' % user)
            # save user's traffic before delelte user
            self.tf_counters_un[user].save_current_traffic()
            self.unregister_userip(user=user)
            # self.tf_counters_un.pop(user)
        for user in ret:
            user_rule = ret[user]
            rule = TrafficRule(user_rule['max_flow'], user_rule['expire_type'],
                               user_rule['action'])
            if user in self.tf_counters_un:
                LOG_DEBUG('update user[%s] rule' % user)
                self.tf_counters_un[user].update_rule(rule)

            else:
                LOG_DEBUG('add user[%s]' % user)
                self.tf_counters_un[user] = TrafficCounter(user, groupname, rule)

        # update current ip_user when update rules

        # print self.tf_counters_un


    def reload_online_user(self):
        # old scheme
        # check if user-ip mapping file exists
        if not os.path.exists(ONLINE_USER):
            LOG_DEBUG('[audit_traffic_statistics] %s dose not exists' % ONLINE_USER)
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

        for ip, uip_info in user_group_map.items():
            # get username
            uname = _uname(uip_info)

            # if no rules for user `uname`, do nothing
            if uname not in self.tf_counters_un:
                # delete record of uname from m_tbuser_traffic_rule
                exec_3306("DELETE FROM m_tbuser_traffic_rule WHERE \
                          sUsername='{}';".format(uname))
                LOG_DEBUG('no rule for user[%s]' % uname)
                continue

            # if rule exists for `uname` add ip to this rule
            LOG_DEBUG('add IP %s' % ip)
            self.tf_counters_un[uname].add_IP(ip)
            self.tf_counters_ip[ip] = self.tf_counters_un[uname]
            self.current_online_ip[ip] = int(time.time())

    # update user's ip
    def update_user_ip(self, user_info=None):
        # new scheme
        if user_info is None:
            return

        if user_info.isOnline == 1: # online
            # add ip to user if exists
            if user_info.uname in self.tf_counters_un:
                self.tf_counters_un[user_info.uname].add_IP(user_info.IP)
                self.tf_counters_ip[user_info.IP] = self.tf_counters_un[user_info.uname]
            else:
                LOG_DEBUG('no rule for user[%s]' % user_info.uname)

        else: # offline
            self.unregister_userip(ip=user_info.IP)


    def unregister_userip(self, user=None, ip=None):
        LOG_DEBUG('in unregister_userip')

        # unregister_ip
        if ip is not None and ip in self.tf_counters_ip:
            LOG_DEBUG('unregister ip {ip} to user {u}'.format(
                ip=ip, u=self.tf_counters_ip[ip].user))
            # if ip is the only one ip of user
            if self.tf_counters_ip[ip].len_IP == 1 and user is None:
                user = self.tf_counters_ip[ip].user
                LOG_DEBUG('last ip {ip} of user {u}'.format(
                    ip=ip, u=self.tf_counters_ip[ip].user))
            # remove ip from traffic counter object
            self.tf_counters_ip[ip].del_IP(ip)
            # remove traffic counter object from list
            self.tf_counters_ip.pop(ip)

        # unregister_user
        if user is None: return
        LOG_DEBUG('unregister user {u}'.format(u=user))
        for ip in self.tf_counters_un[user].ip:
            # remove ip in tf_counters_ip
            if ip in self.tf_counters_ip:
                self.tf_counters_ip.pop(ip)
        if user in self.tf_counters_un:
            self.tf_counters_un.pop(user)


    def update_expire_time_and_way(self):
        # get expire time from database
        res = fetch_3306('SELECT sValue FROM m_tbconfig WHERE sName="UserOffLine";')
        js = json.loads(res['sValue'])
        self.no_traffic_expire_time = int(js.get('timeout', 1) or 1) * 60
        self.no_traffic_expire_way = int(js.get('type', 0) or 0)
        LOG_DEBUG('no_traffic_expire_time = [%s], way=[%s]' % (self.no_traffic_expire_time,
                                                           self.no_traffic_expire_way))


    def update_current_ip(self):

        ip_list = self.current_online_ip.keys()
        d = dict(count=len(ip_list), ip_list=ip_list)
        js = json.dumps(d)
        with open('/usr/local/bluedon/log/current_online_ip', 'w') as fp:
            fp.write(js)

    def traffic_status_check(self, current_time):
        self.update_user_rule()

        # print '-'*40
        downline_user = list()
        # expire user check
        for user in self.tf_counters_un:
            self.tf_counters_un[user].status_check()
            if self.tf_counters_un[user].should_downline():
                for ip in self.tf_counters_un[user].ip:
                    data = {'sUserName': user, 'sIP': ip,
                            'sPassword': '', 'filename': ''}
                    downline_user.append(data)
                    # auth_downline(data)
                    LOG_DEBUG('^'*55)
                    LOG_DEBUG('IP[{ip}] downline overshoot'.format(ip=ip))

        self.update_expire_time_and_way()
        current_online_ip = self.current_online_ip.keys()
        for ip in current_online_ip:
            if current_time - self.current_online_ip[ip] > self.no_traffic_expire_time:
                # if ip is from a auth user, kick the user downline
                if ip in self.tf_counters_ip:
                    if self.no_traffic_expire_way == 1:
                        data = {'sUserName': self.tf_counters_ip[ip].user,
                                'sIP': ip,
                                'sPassword': '', 'filename': ''}
                        downline_user.append(data)
                        # auth_downline(data)
                        # remove auth IP when user downline
                        self.current_online_ip.pop(ip)
                        LOG_DEBUG('^'*55)
                        LOG_DEBUG('IP[{ip}] downline timeout'.format(ip=ip))
                    else:
                        pass
                        LOG_DEBUG('^'*55)
                        LOG_DEBUG('IP[{ip}] downline timeout but not downline'.format(ip=ip))

                else:
                    # normal ip should be removed
                    self.current_online_ip.pop(ip)
                    LOG_DEBUG('^'*55)
                    LOG_DEBUG('IP[{ip}] downline timeout'.format(ip=ip))

        # excute user downline
        LOG_DEBUG('downline user list: %s' % downline_user)
        for data in downline_user:
            auth_downline(data)

        LOG_DEBUG('CURRENT ONLINE IP NUMBERS = [[[%s]]]' % len(self.current_online_ip.keys()))

        self.update_current_ip()


    def run(self):
        max_line = 50000
        max_time = 30
        max_none = 300
        last_date = 0
        last_time = 0
        last_none_time = int(time.time())
        none_count = 0
        current_time = 0

        # add table monitor
        # add_table_monitor(FLOW_RULE_TB, self.update_user_rule)


        # start load_data_infile thread
        self.load_thread = threading.Thread(target=self.load_data_infile)
        self.load_thread.setName('ad_tra_statis')
        self.load_thread.setDaemon(True)
        self.load_thread.start()

        msgs = get_msg_from_channel(self.redis_obj, AUDIT_TRAFFIC_STATISTICS_CH,
                                    mode='sub')

        # xmlrpc for user downline
        # xmlrpc_client = ServerProxy("http://127.0.0.1:18000", allow_none=True)

        # start user login handler
        self.user_handler.start()

        for msg in msgs:
            if self.event.isSet():
                break

            # update rule_ip mapping every 30s
            if int(time.time()) - current_time > 30:
                current_time = int(time.time())
                # print 'user list'
                # print self.tf_counters_un
                # print 'ip list'
                # print self.tf_counters_ip
                self.acquire_tf_lock()
                try:
                    self.traffic_status_check(current_time)
                finally:
                    self.release_tf_lock()


            # traffic statistic
            if msg is None:
                none_count += 1
                # if none_count >= max_none and len(self.flow_records) > 0:
                #     print 'get 30 none_count, save_current_traffic'
                #     none_count == 0

                #     # save current traffic
                #     self.add_task(self.flow_records, self.tb_date(last_date))
                #     self.flow_records = {}
                #     last_time = itime

                # time out when a None message is arrived
                # if int(time.time()) - last_none_time >= max_time:
                #     if len(self.flow_records) > 0:
                if none_count >= max_none and len(self.flow_records) > 0:
                   LOG_DEBUG('load in last_none_time(get None)')
                   self.add_task(self.flow_records, self.tb_date(last_date))
                   self.flow_records = {}
                   pass

                   # last_none_time = int(time.time())
                continue
            else: none_count = 0

            # idate, itime, sip, app, dport, up_bw, dw_bw, tt_bw = self.parser(msg)
            for idate, itime, sip, dip, app, dport, up_bw, dw_bw, tt_bw, mark in self.parser(msg):

                # add ip to online set, clear every 30s
                if IP(sip).iptype() == 'PRIVATE':
                    self.current_online_ip[sip] = itime
                elif IP(dip).iptype() == 'PRIVATE':
                    # if dip is PRIVATE
                    sip, up_bw, dw_bw = dip, dw_bw, up_bw
                    self.current_online_ip[dip] = itime
                else:
                    # do not process msg which neither sip nor dip is PRIVATE IP
                    continue

                # get username and group_name
                username = 'Anonymous'
                groupname = 'Anonymous'
                if sip in self.tf_counters_ip:
                    self.tf_counters_ip[sip].add(up_bw, dw_bw)
                    username = self.tf_counters_ip[sip].user
                    groupname = self.tf_counters_ip[sip].group
                else:
                    # this ip has not statistic rule
                    pass

                # check if date is changed
                if last_date != idate:
                    LOG_DEBUG('last_date is different')
                    if len(self.flow_records) > 0:
                        LOG_DEBUG('load in last_date')
                        self.add_task(self.flow_records, self.tb_date(last_date))
                        self.flow_records = {}
                        pass

                    last_date = idate
                    last_time= itime

                elif len(self.flow_records) >= max_line:
                    LOG_DEBUG('load in max_line')
                    self.add_task(self.flow_records, self.tb_date(last_date))
                    self.flow_records = {}
                    last_time = itime

                elif itime != last_time:
                    if len(self.flow_records) > 0:
                        LOG_DEBUG('load in last_time')
                        self.add_task(self.flow_records, self.tb_date(last_date))
                        self.flow_records = {}
                        pass

                    last_time = itime

                # IP -> int
                sip = str(IP(sip).int())
                # record IP and flow traffic in redis(for traffic alert)
                # self.record_key(sip, idate, tt_bw, itime, dport)
                this_key = '|'.join((str(itime), sip, app, dport, mark, username, groupname))
                # record in a dict(for traffic statistic)
                if this_key not in self.flow_records:
                    self.flow_records[this_key] = (int(up_bw), int(dw_bw))
                else:
                    u = self.flow_records[this_key][0] + int(up_bw)
                    d = self.flow_records[this_key][1] + int(dw_bw)
                    self.flow_records[this_key] = (u, d)

                # if sip == '172.16.7.66':
                #     print '{ip:<16} up={up:<10} up_t={up_t:<10} \
                #         dw={dw:<10} dw_t={dw_t:<10}'.format(ip=sip, up=up_bw,
                #                 up_t=0, dw=dw_bw, dw_t=0)

        if len(self.flow_records) != 0:
            # do clean job
            pass

        # save current traffic in database
        for user in self.tf_counters_un:
            self.tf_counters_un[user].save_current_traffic()

        LOG_DEBUG('[audit_traffic_statistics]Exit done')


    def start(self):
        super(AuditTrafficStatistics, self).start()


    def stop(self):
        self.event.set()
        self.user_handler.stop()



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

