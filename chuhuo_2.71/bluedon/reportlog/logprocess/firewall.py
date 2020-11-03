#!/usr/bin/env python
# coding=utf-8

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import random
import string
import threading
import Queue
import commands
from multiprocessing import Pool, Manager
from db.config1 import execute_sql as exec_3307
from db.config import fetchall_sql as fcal_3306
from db.config1 import executemany_sql as execmany_3307
from reportlog.log_statistics import webapp_log_statistics
from log_process_base import LogProcessBase
# from reportlog.log_size_record import log_size_record
from ..log_size_record import log_size_record
from db.mysql_observer import MysqlObserver
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR


class LogFirewall(LogProcessBase):

    def __init__(self):

        from reportlog.log_app_names import get_app_names
        self.app_names = get_app_names()
        self.protocols = dict()

        keys = [
            # 'iTime','sInputPort','sOutPort','sSourceAddr',
            # 'sSourcePort','sProtocol','sTargetAddr','sTargetPort','sAction'
            'iTime','sInputPort','sOutPort','sSourceAddr',
            'sSourcePort','sProtocol','sTargetAddr','sTargetPort','sAction','iCount'
        ]

        # self.app_tb_name = 'm_tblog_app_admin'
        self.app_tb_name = 'm_tblog_app_admin'
        self.app_args = []
        self.app_keys = [
            # 'iTime','sInputPort','sOutPort','sSourceAddr',
            # 'sSourcePort','sProtocol','sTargetAddr','sTargetPort','sAction'
            'iTime','sAppName','sSourceIP','sProtocol','sTargetIP','sAction','iCount'
        ]
        # super(LogFirewall,self).__init__('iptables-ng_log','m_tblog_firewall',
        #                              '/var/log/fw/iptables-ng.log',keys)
        # test with m_tblog_test_firewall
        super(LogFirewall,self).__init__('iptables-ng_log','m_tblog_firewall',
                                     '/var/log/fw/iptables-ng.log',keys)

        # get interfaces' name from m_tbnetport
        self.ifname = {
            res['sPortName'] : res['sLan']
            for res in fcal_3306('SELECT sPortName, sLan FROM m_tbnetport;')
        }

        self.get_protocols()


    def get_protocols(self):
        # get id: protocol mapping)
        with open('/etc/protocols', 'r') as fp:
            lines = fp.readlines()

        for line in lines:
            if line.startswith('#'): continue
            if len(line.split()) > 3:
                i, n = line.split()[1:3]
                self.protocols[i] = n


    def parser_line(self, line):
        if not line:
            return self.null

        try:
            ls = line.split()

            if len(ls) < 14:
                FWLOG_DEBUG('log_split_firewall:len too short[%s]' % line)
                return self.null

            try:
                ls[0] = str(int(time.mktime(time.strptime(ls[0], '%Y-%m-%d:%H:%M:%S'))))
            except:
                pass

            t = ls[0]
            # if timestamp is a wrong number
            if int(t) < 1400000000:
                return self.null

            #optimize
            res = {i.split('=')[0]:i.split('=')[1] for i in ls if not len(i.split('=')) < 2}
            act = res.get('ipt_log', '-')
            inp = res['IN'] or '-'
            out = res['OUT'] or '-'
            sip = res['SRC']
            dip = res['DST']
            proto = res['PROTO']
            proto = self.protocols.get(proto, proto)
            spt = res.get('SPT', '-')
            dpt = res.get('DPT', '-')
            app_mark = res.get('MARK', '')

            if res.get('PHYSIN') and res.get('PHYSOUT'):
                inp = res['PHYSIN']
                out = res['PHYSOUT']

            # inport and outport names transfer
            inp = self.ifname.get(inp, inp)
            out = self.ifname.get(out, out)

            # t = ls[0]
            date = time.strftime('%Y%m%d', time.localtime(int(t)))
            if t == '0' or date == None:
                return self.null

            result = (str(t) + '|' + inp + '|' + out + '|' + sip + '|' + spt + '|'
                   + proto + '|' + dip + '|' + dpt + '|' + act + '|' + app_mark)

            # print result

            return result ,date

        except:
            FWLOG_ERR('%s get wrong line: [%s]' % (self.tb_name, line))
            return self.null


    def save_to_file(self, args, name):
        _file = self.create_tmp_file(name)
        self.app_args = []
        for i in range(len(args)):
            arg = args[i].split('|')
            mark = arg[-2]

            if not mark == '':
                mark = int(mark, 16) & 0xFFFFF
                mark = self.app_names.get(mark, 'unknow')
                self.app_args.append((arg[0], mark, arg[3], arg[5],
                                     arg[6], arg[8], arg[10]))

            arg.pop(-2)
            args[i] = '|'.join(arg)

        with open(_file, 'a+') as fp:
                fp.write('\n'.join(args))

        return _file, name


    def other_jobs(self, args):
        # print args
        if self.app_args:
            # print self.app_args
            tb = self.app_tb_name + '_' + self.tb.split('_')[-1]
            sql = "CREATE TABLE IF NOT EXISTS `%s` LIKE `%s`" % (tb,
                                                                 self.app_tb_name)
            exec_3307(sql)
            app_mysql_insert_cmd = (
                "insert into " + tb +''
                "(iTime,sAppName,sSourceIP,sProtocol,sTargetIP,sAction,iCount)"
                " values(%s,%s,%s,%s,%s,%s,%s)")

            execmany_3307(app_mysql_insert_cmd,self.app_args)
            # reset app_mark
            self.app_args = []

        pass

if __name__ == '__main__':
    firewall = LogFirewall()
    # s = time.time()
    # # firewall.main_loop()
    # firewall.start()
    # time.sleep(20)
    # print 'time up'
    # firewall.stop()
    # print 'Use time = %s' % (time.time() - s)
    firewall.get_protocols()
    pass
