#!/usr/bin/env python
# coding=utf-8


import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
from db.config import fetchall_sql as fcal_3306
from db.config1 import execute_sql, executemany_sql
from log_process_base import LogProcessBase
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR
from ..log_size_record import log_size_record

# vpn log status defination
E_SAFE = 2
E_EXCEPTION = 3

R_FAILD = 0
R_SUCCESS = 1
R_ESTABLISH = 2
R_DELETE = 3

S_ERR = 'S_ERR'
S_PHASE_1 = 'new phase 1'
S_PHASE_1_EST = 'ISAKMP-SA established'
S_PHASE_1_ERR = 'phase1 negotiation failed'

S_KEY_EXPIRE = 'ISAKMP-SA expired'
S_KEY_DELETE = 'ISAKMP-SA deleted'

S_TUN_EST_1 = 'IPsec-SA established: ESP/Tunnel'
S_TUN_EST_2 = S_TUN_EST_1

S_TUN_EXPIRE_1 = 'IPsec-SA expired'
S_TUN_EXPIRE_2 = S_TUN_EXPIRE_1
S_TUN_EXPIRE_3 = S_TUN_EXPIRE_1
S_TUN_EXPIRE_4 = S_TUN_EXPIRE_1

ERR_STAT_LIST = {
    S_ERR: '异常事件',
}

STAT_LIST = {
    S_PHASE_1: '密钥交换',
    S_PHASE_1_EST: '密钥交换成功',
    S_PHASE_1_ERR: '密钥交换失败',

    S_TUN_EST_1: '建立隧道',
    S_TUN_EST_2: '建立隧道',

    S_KEY_EXPIRE: '密钥过期删除',
    S_KEY_DELETE: '密钥过期删除',

    S_TUN_EXPIRE_1: '删除隧道',
    S_TUN_EXPIRE_2: '删除隧道',
    S_TUN_EXPIRE_3: '删除隧道',
    S_TUN_EXPIRE_4: '删除隧道'

}

def timestamp(d, t):
     ts = time.strptime(d + ' ' + t, '%Y-%m-%d %H:%M:%S')
     s = time.mktime(ts)
     date = time.strftime('%Y%m%d',ts)
     return int(s),date


class LogIPSecVPN(LogProcessBase):
    def __init__(self):
        keys = [
            "iTime", "sLocal", "sTarget", "iType", "sType", "iStatus", "sData", "iCount"
        ]

        self.current_date = ''

        super(LogIPSecVPN, self).__init__('vpn','m_tbipsec_log',
                                     '/usr/local/ipsec-vpn/etc/racoon.log',keys)


    def main_loop(self):
        if not os.path.exists(self.path):
            return
        log_file = open(self.path,"r")
        try:
            self.log_record = log_size_record()
            imported_size = self.log_record.get_record_by(self.log_name)
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0

            count = 0
            # print 'imported_size = %d' % imported_size
            # print 'log_size = %d' % fsize

            if imported_size == fsize:
                log_file.close()
                return

            if imported_size > fsize:
                log_file.close()
                self.log_record.set_record(self.log_name, 0)
                return

            log_file.seek(imported_size,0)
            where = log_file.tell()
            done  = False
            args = []
            mysql_insert_cmd = "insert into " + self.tb + "(iTime, sLocal, \
                sTarget, iType, sType, iStatus, sData) values(%s, %s, %s, %s, %s, %s, %s)"

            cur_stat = ''
            pre_stat = ''
            wait_stat = ''
            log_msg = None
            tun_expire_count = 0
            itype = 0
            iresult = 0
            stype = 0
            ip_local = '-'
            ip_remote = '-'
            pre_ip_local = '-'
            pre_ip_remote = '-'

            while not done:
                if self.onoff != 'on': break
                l = log_file.readline()
                ##self.logger_debug(l)
                if l == '':
                    done = True
                    continue

                ls = l.split()
                if len(ls) < 3:
                    # print 'log_split_vpn:len too short',len(ls)
                    # raise RuntimeError('log_split_vpn:len too short')
                    continue

                # get status
                if ls[2].startswith('INFO'):
                    cur_stat = None
                    for s in STAT_LIST:
                        if s in l:
                            cur_stat = s
                            # print '%s in STAT_LIST' % s
                            break
                    if cur_stat is None: continue

                elif ls[2].startswith('ERROR') or ls[3].startswith('ERROR'):
                    if S_PHASE_1_ERR in l:
                        cur_stat = S_PHASE_1_ERR
                    else:
                        cur_stat = S_ERR
                    pass
                else:
                    continue


                # try to get ip
                local_remote = None
                # 2 IP in this item
                if len(ls[-1].split('.')) == 7:
                    local_remote = ls[-1]
                elif len(ls[-2].split('.')) == 7:
                    local_remote = ls[-2]

                if local_remote is not None:
                    try:
                        ip_local, ip_remote = local_remote.split('-')
                    except:
                        ip_local, ip_remote = local_remote.split('>')

                    ip_local = ip_local.split('[')[0]
                    ip_remote = ip_remote.split('[')[0].lstrip('>')
                else:
                    # ip_local = '-'
                    # ip_remote = '-'

                    # use pre ip
                    ip_local = pre_ip_local
                    ip_remote = pre_ip_remote


                if cur_stat in ERR_STAT_LIST:
                    # get an error log here
                    # print 'GET:[%s ERROR MSG] %s' % (pre_stat, ' '.join(ls[2:]))
                    # op = STAT_LIST.get(pre_stat, ERR_STAT_LIST[cur_stat])

                    # process recognized event error
                    if pre_stat in STAT_LIST:
                        # do not process phase1 status here
                        if pre_stat != S_PHASE_1 and pre_stat != S_PHASE_1_ERR:
                            op = STAT_LIST[pre_stat]
                            log_msg = '{op}失败: {ca}'.format(op=op, ca=' '.join(ls[2:]))
                            stype = '{op}失败'.format(op=op)
                        else:
                            op = ERR_STAT_LIST[S_ERR]
                            log_msg = '{op}: {ca}'.format(op=op, ca=' '.join(ls[2:]))
                            stype = '{op}'.format(op=op)

                    # others are exception event
                    else:
                        log_msg = '异常事件: {ca}'.format(ca=' '.join(ls[2:]))
                        stype = '异常事件'

                    itype = E_EXCEPTION
                    iresult = R_FAILD

                    # status control
                    if pre_stat != S_PHASE_1: pre_stat = cur_stat

                else:
                    if cur_stat == S_PHASE_1:
                        pre_ip_local = ip_local
                        pre_ip_remote = ip_remote

                    # phase1 established
                    if cur_stat == S_PHASE_1_EST and pre_stat != S_PHASE_1:
                        # print 'GET[phase1] %s' % ' '.join(ls[2:])
                        stype = '密钥重新建立'
                        log_msg = stype  + ' ' +  ' '.join(ls[3:])
                        cur_stat = wait_stat

                    # phase1 process
                    if pre_stat == S_PHASE_1 and cur_stat == S_PHASE_1_EST:
                        # create a new log for phase 1 established
                        # print 'GET[phase1] %s' % ' '.join(ls[2:])
                        stype = STAT_LIST[cur_stat]
                        log_msg = stype  + ' ' +  ' '.join(ls[3:])

                        cur_stat = wait_stat

                    # phase1 error
                    elif pre_stat == S_PHASE_1 and cur_stat != S_PHASE_1_EST:
                        # create a new log for phase 1 established
                        # print 'GET[phase1 ERROR] %s' % ' '.join(ls[2:])
                        stype = STAT_LIST[S_PHASE_1_ERR]
                        log_msg = stype  + ' ' +  ' '.join(ls[3:])
                        # set cur_stat S_ERR so next status will not get phase1
                        # error, but if cur_stat is S_PHASE_1, that means last
                        # phase1 failed and another phase1 is restarted, so do
                        # not change cur_stat if it is S_PHASE_1
                        if cur_stat == S_PHASE_1: pass
                        else: cur_stat = S_ERR

                    if pre_stat == S_TUN_EST_1 and cur_stat == S_TUN_EST_2:
                        # print 'GET[Tunnel Established] %s' % ' '.join(ls[2:])
                        stype = STAT_LIST[cur_stat]
                        log_msg = stype  + ' ' +  ' '.join(ls[3:])

                        cur_stat = wait_stat

                    if pre_stat == S_KEY_EXPIRE and cur_stat == S_KEY_DELETE:
                        # print 'GET[Key Del] %s' % ' '.join(ls[2:])
                        stype = STAT_LIST[cur_stat]
                        log_msg = stype  + ' ' +  ' '.join(ls[3:])

                        cur_stat = wait_stat

                    if cur_stat == S_TUN_EXPIRE_2:
                        tun_expire_count += 1
                        if tun_expire_count == 4:
                            # print 'GET[Tunnel Del] %s' % ' '.join(ls[2:])
                            stype = STAT_LIST[cur_stat]
                            log_msg = stype  + ' ' +  ' '.join(ls[3:])

                            cur_stat = wait_stat

                            # reset tunnel expired counter
                            tun_expire_count = 0
                    else:
                        tun_expire_count = 0


                    itype = E_SAFE
                    iresult = R_SUCCESS

                    # status  control
                    pre_stat = cur_stat

                # print 'local ip = %s' % ip_local
                # print 'remote ip = %s' % ip_remote
                # print 'pre: %s' % pre_stat
                # print 'cur: %s' % cur_stat
                # print '-'*40
                # update pre_stat
                # pre_stat = cur_stat
                cur_stat = None

                # if there is a log
                if log_msg is None: continue
                if ip_local == '-' and ip_remote == '-': continue

                t,date = timestamp(ls[0],ls[1].rstrip(':'))

                if self.current_date != date:
                    self.current_date = date
                    self.tb = self.tb_name + '_' + date
                    executemany_sql(mysql_insert_cmd,args)
                    args = []
                    #run mysql cmd CREATE IF NOT EXISTS
                    sql = "CREATE TABLE IF NOT EXISTS `%s` LIKE m_tbipsec_log" % self.tb
                    execute_sql(sql)

                mysql_insert_cmd = "insert into " + self.tb + "(iTime, sLocal, \
                    sTarget, iType, sType, iStatus, sData) values(%s, %s, %s, %s, %s, %s, %s)"

                # add a log to a list, and reset log_msg
                args.append((t, ip_local, ip_remote, itype, stype, iresult, log_msg))
                log_msg = None

                count += 1
                if count == 5000:
                    where = log_file.tell()
                    # print("VPN:commiting ...... at where = %d" % where)
                    executemany_sql(mysql_insert_cmd,args)
                    self.log_record.set_record(self.log_name, where)
                    # print("VPN:commiting DONE!!!")
                    count = 0
                    done = True

            #insert to mysql
            if not count == 0:
                where = log_file.tell()
                # print("VPN:commiting ...... at where = %d" % where)
                executemany_sql(mysql_insert_cmd,args)
                self.log_record.set_record(self.log_name, where)
                # print("VPN:commiting DONE!!!")

        except ValueError as e:
             where = log_file.tell()
             # print("VPN ERROR:commiting ...... at where = %d" % where)
             executemany_sql(mysql_insert_cmd,args)
             self.log_record.set_record(self.log_name, where)
             # print("VPN ERROR:commiting DONE!!! with exception")
             # print l
             # print e
        except Exception as e:
            print e

        finally:
            log_file.close()
            del log_file


if __name__ == '__main__':
    ips = LogIPSecVPN()
    s = time.time()
    # ips.main_loop()
    ips.start()
    time.sleep(10)
    print 'time up'
    ips.stop()
    print 'Use time = %s' % (time.time() - s)
    pass
