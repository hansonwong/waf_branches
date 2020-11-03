#!/usr/bin/env python
# -*-coding:utf-8-*-
from __future__ import division
import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
import commands
import time
import threading
import MySQLdb
import socket
import ast
import random
from IPy import IP
from logging import getLogger
from reportlog.log_config import mail_test
from db.config import execute_sql,search_data,get_mysql_db,fetchone_sql,fetchall_sql,executemany_sql


def _key(ip, app):
    return (ip, app)

def _new_record():
    return {'min':[0]*120,'hour':[0]*120,'day':[0]*168}


class SecondTrafficStatistic(threading.Thread):

    event = threading.Event()
    def __init__(self):
        super(SecondTrafficStatistic, self).__init__()
        self.tcp = {}
        self.udp = {}
        self.ip = ''
        self.ind = 0
        self.ihour = 0
        self.iday = 0
        self.last_ind = 0
        self.last_hour = 0
        self.last_day = 0
        self.ind_clear = False
        self.hour_clear = False
        self.day_clear = False

        self.tcp_list_u = {}
        self.udp_list_u = {}
        self.icmp_list_u = {}
        self.tcp_list_i = {}
        self.udp_list_i = {}
        self.icmp_list_i = {}

        self.commit_time = int(time.time())


    def transfer_app_num(self, app_ten):
        qur_sql = "SELECT class_1, class_2 FROM `m_tbdefault_app_list` WHERE app_id_ten={}".format(int(app_ten))
        num_result= fetchone_sql(qur_sql)
        try:
            c1 = int(num_result['class_1'])
            c2 = int(num_result['class_2'])
        except:
            return app_ten

        sect_sql = "SELECT app_id_ten FROM `m_tbdefault_app_list` WHERE class_1={} AND class_2={} AND class_3={}".format(c1,c2,0)
        if not sect_sql:
            return
        scd_type_num = fetchone_sql(sect_sql)['app_id_ten']
        return scd_type_num


    def add_tcp_item(self, ip, pair):
        """
            Description:
                add tcp record to dict tcp_list_u/i, and update value of (ip,app)
        """
        if not len(pair.split(',')) == 2:
            return
        app,bw = pair.split(',')
        app = self.transfer_app_num(app)
        this_key = _key(ip,app)

        if this_key in self.tcp_list_i:
            lst = self.tcp_list_i

        elif this_key in self.tcp_list_u:
            lst = self.tcp_list_u

        # this key is not save in our list, fetch it in database
        else:
            _sql = ("SELECT sTraffic FROM `m_tbuser_traffic_BiLevel`"
                    " WHERE sUserIP='%s' and sAppType='%s' and sProtocol='%s' limit 1")
            res = fetchone_sql(_sql % (ip,app,'TCP'))
            # if this key is not exists, create one
            if res is None:
                lst = self.tcp_list_i
                lst[this_key] = _new_record()
            else:
                lst = self.tcp_list_u
                lst[this_key] = ast.literal_eval(res['sTraffic'].rstrip('\'').lstrip('\''))

        self.update_record(lst, this_key, bw)


    def add_udp_item(self, ip, pair):
        """
            Description:
                add udp record to dict udp_list_u/i, and update value of (ip,app)
        """
        if not len(pair.split(',')) == 2:
            return
        app,bw = pair.split(',')
        app = self.transfer_app_num(app)
        this_key = _key(ip,app)

        if this_key in self.udp_list_i:
            lst = self.udp_list_i

        elif this_key in self.udp_list_u:
            lst = self.udp_list_u

        # this key is not save in our list, fetch it in database
        else:
            _sql = ("select sTraffic from m_tbuser_traffic_BiLevel"
                    " where sUserIP='%s' and sAppType='%s' and sProtocol='%s' limit 1")
            res = fetchone_sql(_sql % (ip,app,'UDP'))
            # if this key is not exists, create one
            if res is None:
                lst = self.udp_list_i
                lst[this_key] = _new_record()
            else:
                lst = self.udp_list_u
                lst[this_key] = ast.literal_eval(res['sTraffic'].rstrip('\'').lstrip('\''))

        # update lst
        self.update_record(lst,this_key,bw)


    def update_record(self,lst,key,bw):
        """
            Description:update lst[key] by bw, index is specified by time
        """
        record = lst[key]
        # reset the value if there comes a new index
        if self.last_ind != self.ind:
            record['min'][self.ind] = 0
            self.last_ind = self.ind
        if self.last_hour != self.ihour:
            record['hour'][self.ihour] = 0
            self.last_hour = self.ihour
        if self.last_day!= self.iday:
            record['day'][self.iday] = 0
            self.last_day = self.iday
        # update the value specified by self.ind/self.ihour/self.iday
        record['min'][self.ind] += abs(int(bw))
        record['hour'][self.ihour] += abs(int(bw))
        record['day'][self.iday] += abs(int(bw))

        lst[key] = record

    def insert_record_db(self, lst, tb, proto, lud, t):
        """
            Description:
        """
        args = []
        _insert_sql = ('insert into ' + tb + ''
                       ' (sUserIP,sProtocol,sAppType,sTraffic,sLastUpdate,iTime,sTrafficHour,sTrafficDay,sTrafficWeek) '
                       'values("%s","%s","%s","%s","%s",%s,"%s","%s","%s")')


        for key in lst:
            if self.event.isSet():
                break
            # new fileds added by AnkiYang 2017.5.3
            sTrafficHour = lst[key]['min']
            sTrafficDay = lst[key]['hour']
            sTrafficWeek = lst[key]['day']

            # args.append((key[0], proto, key[1], str(lst[key]), lud, t))

            execute_sql(_insert_sql % (key[0], proto, key[1], lst[key], lud, t, sTrafficHour, sTrafficDay, sTrafficWeek))
            # executemany_sql(_insert_sql, args)

    def update_record_db(self, lst, tb, proto, lud, t):
        """
            Description:
        """
        args = []
        _update_sql = ('UPDATE `{}` SET sTraffic="%s",sLastUpdate="%s",iTime=%s, '
                       'sTrafficHour="%s", sTrafficDay="%s", sTrafficWeek="%s" '
                       'where sUserIP="%s" and sAppType="%s"'.format(tb))

        for key in lst:
            if self.event.isSet():
                break

            sTrafficHour = lst[key]['min']
            sTrafficDay = lst[key]['hour']
            sTrafficWeek = lst[key]['day']

            execute_sql(_update_sql % (lst[key], lud, t, sTrafficHour, sTrafficDay, sTrafficWeek, key[0], key[1]))


        # executemany_sql(_update_sql, args)
        pass

    def update_db(self,t):
        """
            Description:
                Insert/update records of xxx_list_i/xxx_list_u
        """
        commit_counter = t
        lud = "%s|%s|%s" % (self.ind,self.ihour,self.iday)

        # insert/update tcp
        self.insert_record_db(self.tcp_list_i, 'm_tbuser_traffic_BiLevel',
                           'TCP', lud, commit_counter)

        self.update_record_db(self.tcp_list_u, 'm_tbuser_traffic_BiLevel',
                           'TCP', lud, commit_counter)

        # insert/update udp
        self.insert_record_db(self.udp_list_i, 'm_tbuser_traffic_BiLevel',
                           'UDP', lud, commit_counter)

        self.update_record_db(self.udp_list_u, 'm_tbuser_traffic_BiLevel',
                           'UDP', lud, commit_counter)

        # clear record this can also be done in self.clear_record
        self.tcp_list_u = {}
        self.udp_list_u = {}
        self.icmp_list_u = {}
        self.tcp_list_i = {}
        self.udp_list_i = {}
        self.icmp_list_i = {}

    def clear_record_ind(self,m_tb,lud):
        """
            Description:clear records haven't update in 7days 24hours or 60mins
        """
        current_time = int(time.time())
        current_time = current_time - current_time%30
        expire_hour = current_time  - 3600
        expire_day = current_time - 86400
        expire_week =  current_time - 604800
        #expire_week delete this record from database
        sql = 'delete from ' + m_tb + ' where iTime <= "%s"' % expire_week
        execute_sql(sql)

        sql = 'select * from ' + m_tb + ' where iTime <= "%s"' % expire_hour
        res = fetchall_sql(sql)

        for rec in res:
            if self.event.isSet():
                break
            record = ast.literal_eval(rec['sTraffic'].rstrip("\'").lstrip("\'"))
            #expire_hour: set min[120] = 0 but not update sLastUpdate
            record['min']  = [0]*120
            rec['sTrafficHour'] = [0] * 120

            if rec['iTime'] <= expire_day:
                #expire_day set hour[120] = 0 but not update sLastUpdate
                record['hour']  = [0]*120
                rec['sTrafficDay'] = [0] * 120
            # args.append((str(record),rec['id']))
            sql = 'update ' + m_tb + ' set sTraffic="%s",sTrafficHour="%s", sTrafficDay="%s" where id="%s"'
            execute_sql(sql % (record, rec['sTrafficHour'], rec['sTrafficDay'], rec['id']))
            # sql = 'update ' + m_tb + ' set sTraffic="%s" where id="%s"'
            # execute_sql(sql % (record,rec['id']))



    #clear records haven't update in 7days 24hours or 60mins
    # def clear_record(self):
    def run(self):
        """
            Description:clear records haven't update in 7days 24hours or 60mins
        """
        # m_tb = ['m_tbuser_tcp_BiLevel_traffic','m_tbuser_udp_BiLevel_traffic']
        m_tb = 'm_tbuser_traffic_BiLevel'
        lud = '%s|%s|%s' % (self.ind,self.ihour,self.iday)
        _time_counter = int(time.time())

        while 1:
        # while self.event.isSet():
        #     print 'running %s' % self.event.isSet()
            if self.event.isSet():
                getLogger('log_daemon').debug('EVENT SET:[TRAFFIC_STATISTIC_SECOND]:CLEAR OLD RECORD')
                break
            if int(time.time()) - _time_counter > 60:
                _time_counter = int(time.time())
                # [self.clear_record_ind(tb,lud) for tb in m_tb]
                self.clear_record_ind(m_tb, lud)
                # clear exists records
                # self.tcp_list_u = {}
                # self.udp_list_u = {}
                # self.icmp_list_u = {}
                # self.tcp_list_i = {}
                # self.udp_list_i = {}
                # self.icmp_list_i = {}

            time.sleep(1)

        getLogger('log_daemon').debug('QUIT:[TRAFFIC_STATISTIC_SECOND:CLEAR OLD RECORD]')

    def start(self):
        super(SecondTrafficStatistic,self).start()
        pass

    def stop(self):

        getLogger('log_daemon').debug('[TRAFFIC_STATISTIC_SECOND]CLEAR PROCESS END')
        self.event.set()
        #kill read_traffic_info thread





if __name__ == '__main__':
    SecondTS = SecondTrafficStatistic()
    SecondTS.transfer_app_num('66564')
