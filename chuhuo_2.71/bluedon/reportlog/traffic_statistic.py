#!/usr/bin/env python
# -*-coding:utf-8-*-
from __future__ import division
import os
import commands
import time
#import sys
import threading
import MySQLdb
import socket
import ast
from IPy import IP
from logging import getLogger
from reportlog.log_config import mail_test
from reportlog.traffic_statistic_second import SecondTrafficStatistic
from db.config import execute_sql,search_data,get_mysql_db,fetchone_sql,fetchall_sql,executemany_sql
#from db.config1 import execute_sql,search_data,get_mysql_db,fetchone_sql,fetchall_sql,executemany_sql


ip_reg = r"(\d{1,3}\.){3}\d{1,3}"
SYS_ALERT_SUBJECT = 'SYSTEM USAGE ALERT'
TRAFFIC_INFO_FIFO = '/tmp/fifo/traffic_statistic_info_fifo'
READ_TRAFFICE_INFO = '/home/ng_platform/bd_dpdk_warper/clients'

def read_traffic_count_table():
    #time.sleep(12)
    #os.system('/usr/bin/taskset -c 1 /home/ng_platform/bd_dpdk_warper/clients/read_traffic_count_table')
    return True

def stop_traffic_count_table():
    pass
    #kill read_traffic_info thread
    #s = commands.getoutput("ps -aux | grep read_traffic_count_table | grep -v grep | awk '{print $2}'")
    #for pid in s.split():
    #    os.system("kill -9 %s" % pid)
    #    getLogger('log_daemon').debug('KILL [read_traffic_count_table] PID[%s]' % pid)


def _key(ip, app):
    return (ip, app)

def _new_record():
    return {'min':[0]*120,'hour':[0]*120,'day':[0]*168}



class TrafficStatistic(threading.Thread):

    event = threading.Event()
    def __init__(self):
        super(TrafficStatistic,self).__init__()
        self.tcp={}
        self.udp={}
        self.ip = ''
        self.ind=0
        self.ihour=0
        self.iday=0
        self.last_ind=0
        self.last_hour=0
        self.last_day=0
        self.ind_clear = False
        self.hour_clear = False
        self.day_clear = False
        # if not os.path.exists(TRAFFIC_INFO_FIFO):
        #     os.system('mkfifo %s' % TRAFFIC_INFO_FIFO)

        self.tcp_list_u = {}
        self.udp_list_u = {}
        self.icmp_list_u = {}
        self.tcp_list_i = {}
        self.udp_list_i = {}
        self.icmp_list_i = {}

        self.secd_traffic = SecondTrafficStatistic()


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
        # print 'update_record: ',record


    def clear_record_ind(self,m_tb,lud):
        """
            Description:clear records haven't update in 7days 24hours or 60mins
        """
        # print 'clear record %s' % m_tb
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
        args = []
        for rec in res:
            if self.event.isSet():
                break

            record = ast.literal_eval(rec['sTraffic'].rstrip("\'").lstrip("\'"))

            # new fields added at 2017/5/3, also need to be cleaned. AnkiYang

            #expire_hour: set min[120] = 0 but not update sLastUpdate
            record['min']  = [0]*120
            # new add
            rec['sTrafficHour'] = [0]*120

            #print 'expire_hour',rec['sLastUpdate'],':',rec['iTime']
            if rec['iTime'] <= expire_day:
                #expire_day set hour[120] = 0 but not update sLastUpdate
                record['hour']  = [0]*120
                # new add
                rec['sTrafficDay'] = [0]*120

            # args.append((str(record),rec['id']))
            sql = 'update ' + m_tb + ' set sTraffic="%s",sTrafficHour="%s", sTrafficDay="%s" where id="%s"'
            execute_sql(sql % (record,rec['sTrafficHour'], rec['sTrafficDay'],rec['id']))
            # sql = 'update ' + m_tb + ' set sTraffic="%s" where id="%s"'
        # executemany_sql(sql, args)
        args = []

    #clear records haven't update in 7days 24hours or 60mins
    def clear_record(self):
        """
            Description:clear records haven't update in 7days 24hours or 60mins
        """
        m_tb = ['m_tbuser_udp_traffic','m_tbuser_tcp_traffic','m_tbuser_icmp_traffic']
        lud = '%s|%s|%s' % (self.ind,self.ihour,self.iday)
        _time_counter = int(time.time())

        while 1:
            if self.event.isSet():
                print 'EVENT SET:[TRAFFIC_STATISTIC:clear_record]'
                getLogger('log_daemon').debug('EVENT SET:[TRAFFIC_STATISTIC:clear_record]')
                break
            if int(time.time()) - _time_counter > 60:
                _time_counter = int(time.time())
                [self.clear_record_ind(tb,lud) for tb in m_tb]
                # clear exists records
                # self.tcp_list_u = {}
                # self.udp_list_u = {}
                # self.icmp_list_u = {}
                # self.tcp_list_i = {}
                # self.udp_list_i = {}
                # self.icmp_list_i = {}
            time.sleep(1)

        print 'QUIT:[TRAFFIC_STATISTIC:clear_record]'
        getLogger('log_daemon').debug('QUIT:[TRAFFIC_STATISTIC:clear_record]')


    def proc_ip(self,l):
        icmp = l.split('|')[3]
        self.update_icmp_record(icmp)
        pass


    def add_icmp_item(self, ip, bw):
        """
            Description:
                add tcp record to dict tcp_list_u/i, and update value of (ip,app)
        """
        # if int(bw) == 0:
        #     return
        this_key = ip
        if this_key in self.icmp_list_i:
            lst = self.icmp_list_i
        elif this_key in self.icmp_list_u:
            lst = self.icmp_list_u
        # this key is not save in our list, fetch it in database
        else:
            _sql = ('select sTraffic from m_tbuser_icmp_traffic'
                    ' where sUserIP="%s" limit 1')
            res = fetchone_sql(_sql % ip)
            # if this key is not exists, create one
            if res is None:
                lst = self.icmp_list_i
                lst[this_key] = _new_record()
            else:
                lst = self.icmp_list_u
                lst[this_key] = ast.literal_eval(res['sTraffic'].rstrip('\'').lstrip('\''))
        # update lst
        self.update_record(lst,this_key,bw)



    def add_tcp_item(self, ip, pair):
        """
            Description:
                add tcp record to dict tcp_list_u/i, and update value of (ip,app)
        """
        if not len(pair.split(',')) == 2:
            return
        app,bw = pair.split(',')
        this_key = _key(ip,app)

        if this_key in self.tcp_list_i:
            lst = self.tcp_list_i

        elif this_key in self.tcp_list_u:
            lst = self.tcp_list_u

        # this key is not save in our list, fetch it in database
        else:
            _sql = ('select sTraffic from m_tbuser_tcp_traffic'
                    ' where sUserIP="%s" and sAppType="%s" limit 1')
            res = fetchone_sql(_sql % (ip,app))
            # if this key is not exists, create one
            if res is None:
                lst = self.tcp_list_i
                lst[this_key] = _new_record()
            else:
                lst = self.tcp_list_u
                lst[this_key] = ast.literal_eval(res['sTraffic'].rstrip('\'').lstrip('\''))

        # update lst
        self.update_record(lst,this_key,bw)


    def add_udp_item(self, ip, pair):
        """
            Description:
                add udp record to dict udp_list_u/i, and update value of (ip,app)
        """
        if not len(pair.split(',')) == 2:
            return
        app,bw = pair.split(',')
        this_key = _key(ip,app)

        if this_key in self.udp_list_i:
            lst = self.udp_list_i

        elif this_key in self.udp_list_u:
            lst = self.udp_list_u

        # this key is not save in our list, fetch it in database
        else:
            _sql = ('select sTraffic from m_tbuser_udp_traffic'
                    ' where sUserIP="%s" and sAppType="%s" limit 1')
            res = fetchone_sql(_sql % (ip,app))
            # if this key is not exists, create one
            if res is None:
                lst = self.udp_list_i
                lst[this_key] = _new_record()
            else:
                lst = self.udp_list_u
                lst[this_key] = ast.literal_eval(res['sTraffic'].rstrip('\'').lstrip('\''))

        # update lst
        self.update_record(lst,this_key,bw)

    def update_list(self,lst,key,bw):
        lud = '%s|%s|%s' % (self.ind,self.ihour,self.iday)
        pass

    def insert_index(self):
        """
            Description:
                refresh self.ind/self.ihour/self.iday by current time
        """
        ta = time.localtime()
        d = ta[6]*24 + ta[3]
        h = ta[3]*5 + ta[4]//12
        ind = ta[4] * 2 + ta[5]//30
        return ind,h,d

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

            #new fields added at 2017/5/3 .AnkiYang

            sTrafficHour = lst[key]['min']
            sTrafficDay =  lst[key]['hour']
            sTrafficWeek = lst[key]['day']

            if proto == 'ICMP':
                # args.append((key, proto, '0', str(lst[key]), lud, t))
                execute_sql(_insert_sql % (key, proto, '0', lst[key], lud, t, sTrafficHour, sTrafficDay, sTrafficWeek))
            else:
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

            # new fields added at 2017/5/3 .AnkiYang

            sTrafficHour = lst[key]['min']
            sTrafficDay = lst[key]['hour']
            sTrafficWeek = lst[key]['day']

            if proto == 'ICMP':
                # args.append((str(lst[key]), lud, t, key, '0'))
                execute_sql(_update_sql % (lst[key], lud, t, sTrafficHour, sTrafficDay, sTrafficWeek, key, '0'))
            else:
                # args.append((str(lst[key]), lud, t, key[0], key[1]))
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
        self.insert_record_db(self.tcp_list_i, 'm_tbuser_tcp_traffic',
                           'TCP', lud, commit_counter)
        #print 'self.tcp_list_i:',self.tcp_list_i

        self.update_record_db(self.tcp_list_u, 'm_tbuser_tcp_traffic',
                           'TCP', lud, commit_counter)
        #print 'self.tcp_list_u:',self.tcp_list_u

        # insert/update udp
        self.insert_record_db(self.udp_list_i, 'm_tbuser_udp_traffic',
                           'UDP', lud, commit_counter)
        #print 'self.udp_list_i:',self.udp_list_i

        self.update_record_db(self.udp_list_u, 'm_tbuser_udp_traffic',
                           'UDP', lud, commit_counter)
        #print 'self.udp_list_u:',self.udp_list_u

        # insert/update icmp
        self.insert_record_db(self.icmp_list_i, 'm_tbuser_icmp_traffic',
                           'ICMP', lud, commit_counter)
        #print 'self.icmp_list_i:',self.icmp_list_i

        self.update_record_db(self.icmp_list_u, 'm_tbuser_icmp_traffic',
                           'ICMP', lud, commit_counter)
        #print 'self.icmp_list_u:',self.icmp_list_u

        # clear record this can also be done in self.clear_record
        self.tcp_list_u = {}
        self.udp_list_u = {}
        self.icmp_list_u = {}
        self.tcp_list_i = {}
        self.udp_list_i = {}
        self.icmp_list_i = {}


    def run(self):
        server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.settimeout(10)
        server.bind(('127.0.0.1',5679))


        # start a thread to clear expire record
        self.thread_clear_record = threading.Thread(target=self.clear_record)
        self.thread_clear_record.setDaemon(True)
        self.thread_clear_record.start()

        self.thread_clear_record_2nd = threading.Thread(target=self.secd_traffic.start())
        self.thread_clear_record_2nd.setDaemon(True)
        self.thread_clear_record_2nd.start()

        sect = 'ip'
        f_process_ip = True
        last = [0,0,0]
        getLogger('log_daemon').debug('TRAFFICE_STATISTIC:[START]')
        commit_counter = int(time.time())
        #main loop
        while True:
            if self.event.isSet():
                print 'EVENT SET:[TRAFFIC_STATISTIC]'
                getLogger('log_daemon').debug('EVENT SET:[TRAFFIC_STATISTIC]')
                break

            # if another minute is come, inser/update current records into db
            if int(time.time()) - commit_counter >= 30:
                commit_counter = int(time.time())
                self.update_db(commit_counter)
                self.secd_traffic.update_db(commit_counter)

            try:
                rec = server.recvfrom(1024)[0]
            except:
                #print 'data table recv timeout'
                continue

            # self.ind,self.ihour,self.iday = self.insert_index()
            now_ind, now_h, now_d = self.insert_index()
            self.ind, self.ihour, self.iday = now_ind, now_h, now_d
            self.secd_traffic.ind, self.secd_traffic.ihour, self.secd_traffic.iday = now_ind, now_h, now_d
            #clear record not update for a long time
            #self.clear_record()

            #rec_list = rec.split('\n')[0:-1]
            rec_list = rec.split('\n')[0:]

            for l in rec_list:
                if l == '' or len(l.split('|')) <= 2:
                    continue
                self.ip = l.split('|')[0].strip()

                if len(self.ip.split('.')) < 4:
                    continue
                if not IP(self.ip).iptype() == 'PRIVATE':
                    f_process_ip = False
                    continue
                else:
                    f_process_ip = True

                prefix = int(l.split('|')[1].strip())

                if prefix == 1:
                    # icmp_bw = int(l.split('|')[-1].strip())
                    icmp_bw = l.split('|')[-1].rstrip('\x00')
                    self.add_icmp_item(self.ip, icmp_bw)

                elif prefix in [2, 3]:
                    ls = l.split('|')[2:]
                    if ls != []:
                        if prefix == 2:
                            [self.add_tcp_item(self.ip, pair.rstrip('\x00').strip()) for pair in ls if pair != '']
                            [self.secd_traffic.add_tcp_item(self.ip, pair.rstrip('\x00').strip()) for pair in ls if pair != '']
                        if prefix == 3:
                            [self.add_udp_item(self.ip, pair.rstrip('\x00').strip()) for pair in ls if pair != '']
                            [self.secd_traffic.add_udp_item(self.ip, pair.rstrip('\x00').strip()) for pair in ls if pair != '']

        print 'QUIT:[TRAFFIC_STATISTIC]'
        stop_traffic_count_table()
        getLogger('log_daemon').debug('QUIT:[TRAFFIC_STATISTIC]')

    def start(self):
        super(TrafficStatistic,self).start()
        pass

    def stop(self):
        print 'tarffic statistic stop'
        getLogger('log_daemon').debug('traffic statistic stop')
        self.secd_traffic.event.set()
        self.event.set()
        #kill read_traffic_info thread
        stop_traffic_count_table()


if __name__ == '__main__':
    hp = TrafficStatistic()
    #hp.start()
    #time.sleep(5)
    hp.run()
    #hp.stop()
