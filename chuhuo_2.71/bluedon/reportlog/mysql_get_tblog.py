#!/usr/bin/env python
# -*-coding:utf-8-*-
import os
import sys

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

import threading
import time
import MySQLdb
import threading
import gc
import psutil
from logging import getLogger
from reportlog.mysql_log_backup import update_newest_table,get_ten_newest_lines_from_table
from reportlog.log_config import mail_test_attach,read_config_ini,beep_alert
from reportlog.ip_extraction import ip_extra
from reportlog.log_statistics import log_statistics_init
from reportlog.log_mail_config import send_email_msg

from reportlog.logprocess.ddos import LogDDOS
from reportlog.logprocess.evil_code import LogEvilCode
from reportlog.logprocess.firewall import LogFirewall
from reportlog.logprocess.info_leak import LogInfoLeak
from reportlog.logprocess.ips import LogIPS
from reportlog.logprocess.url import LogURL
from reportlog.logprocess.web_app import WebApp
from reportlog.logprocess.webaudit import LogWebAudit
from reportlog.logprocess.ipsec_vpn import LogIPSecVPN
from reportlog.logprocess.log_process_base import LogImportStatus

from db.config1 import execute_sql,executemany_sql,fetchone_sql,fetchall_sql,get_mysql_db,init_db_table
from homepage.statistics import import_switch,IMPORT_ON_OFF,IMPORT_IS_OFF, DISK_ALERT
from utils.log_logger import FWLOG_DEBUG
from utils.file_monitor import add_file_monitor

sleeptime = 0.5
MAIL_CONTENT = r'/usr/local/bluedon/log/mail_content.txt'
DISK_THRES_PATH = '/Data/apps/wwwroot/firewall/data/configdata/iLogpercent.conf'


tb_list = ['m_tblog_ddos','m_tblog_evil_code','m_tblog_ips','m_tblog_webapplication']
TB = {'m_tblog_evil_code'     :'m_tblog_evilcode_record',
      'm_tblog_ddos'          :'m_tblog_ddos_record',
      'm_tblog_ips'           :'m_tblog_ips_record',
      'm_tblog_webapplication':'m_tblog_webapp_record'}

def already_running(py):
    s = commands.getstatusoutput("ps -aux | grep 'python %s' | grep -v grep"  % py)
    log_logger(s[1].split("\n"))
    running = len(s[1].split("\n"))
    log_logger(running)
    if running <= 1:
        return False
    else:
        return True

#base class of viewer
class MysqlGetTblog(threading.Thread):

    #event = threading.Event()
    def __init__(self):
          super(MysqlGetTblog,self).__init__()


class LogImport(threading.Thread):
    event = threading.Event()
    def __init__(self):
        super(LogImport,self).__init__()
        self.setName('logimport')

        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.log_processors = [
            LogDDOS(), LogEvilCode(), LogFirewall(), LogIPS(),
            LogWebAudit(), LogInfoLeak(), LogURL(), WebApp(), LogIPSecVPN()
        ]
        self.import_status = LogImportStatus()

        # init_db_table()
        # log_statistics_init()
        import_switch('on')

        self.disk_max = 80
        self.update_disk_threshold()

        self.lst = {}
        self.s_tb = 'm_tbstatistics'
        self.line_record = {'m_tblog_ddos': 0, 'm_tblog_ips': 0, 'm_tblog_evil_code': 0,'m_tblog_webapplication':0}

    def close_db(self,obj):
        pass

    def update_disk_threshold(self, *args, **kwargs):
        _disk_max = 80
        try:
            with open(DISK_THRES_PATH) as fp:
                log_content = fp.read()

            _disk_max = int(log_content.strip())
        except:
            FWLOG_DEBUG('ERROR:iLog_file write error')

        # print '_disk_max=%s' % _disk_max
        FWLOG_DEBUG('_disk_max=%s' % _disk_max)
        self.disk_max = _disk_max



    def run(self):
        # start a new thread to monitor if new logs are comming
        thd_new_log = threading.Thread(target=self.new_log_monitor)
        thd_new_log.setName('newlog_monitor')
        thd_new_log.setDaemon(True)
        thd_new_log.start()

        # start thread of all log processor
        for proc in self.log_processors:
            self.import_status.attach(proc)
            proc.setDaemon(True)
            proc.start()

        # add disk threshold monitor
        add_file_monitor(DISK_THRES_PATH, self.update_disk_threshold)

        self.import_status.setON()

        count = 0
        while 1:
            count += 1
            try:
                if self.event.isSet():
                    FWLOG_DEBUG('EVENT SET:[MYSQL_GET_TBLOG3]')
                    getLogger('log_daemon').debug('EVENT SET:[MYSQL_GET_TBLOG3]')
                    # return
                    break

                # check if disk if full before importing log
                var_used = psutil.disk_usage('/var').percent
                if var_used > self.disk_max:
                    from reportlog.log_config import read_config_ini
                    if self.import_status.isON():
                        self.import_status.setOFF()
                    FWLOG_DEBUG('MYSQL_GET_TBLOG3:import stop...because disk is too full...')
                    log_ini = read_config_ini('LOG Config')

                    if log_ini['full'] == 'cover':
                        from reportlog.log_clear import log_clear_release_disk
                        FWLOG_DEBUG('MYSQL_GET_TBLOG3:log cover...')
                        # log_clear_release_disk(max_usage = self.disk_max)
                        log_clear_release_disk()
                        FWLOG_DEBUG('MYSQL_GET_TBLOG3:log cover...done')

                    time.sleep(1)
                    continue
                else:
                    if not self.import_status.isON():
                        self.import_status.setON()


                ip_extra()
                time.sleep(sleeptime)
            except Exception,e:
                FWLOG_DEBUG(e)

        thd_new_log.join()
        # stop threads of all log processor
        for proc in self.log_processors:
            proc.stop()
        proc.join()

        FWLOG_DEBUG('QUIT:[MYSQL_GET_TBLOG3]')
        getLogger('log_daemon').debug('QUIT:[MYSQL_GET_TBLOG3]')


    def stop(self):
        self.event.set()
        self.join()

    def start(self):
        super(LogImport,self).start()


    def new_log_monitor(self)    :
        """
            Description:
                detect new log, and send alert mail
        """
        new_log = []
        res = self.record_lines()
        line_record = res

        while 1:
            if self.event.isSet():
                FWLOG_DEBUG('EVENT SET:[MYSQL_GET_TBLOG3:new_log_monitor]')
                getLogger('log_daemon').debug('EVENT SET:[MYSQL_GET_TBLOG3:new_log_monitor]')
                break

            # check update time of newest table
            try:
                self.record_tables()
                res = self.record_lines()

                new_log = [ key for key in line_record.keys()
                      if line_record.get(key) - res.get(key) != 0 ]

                for item in set(new_log):
                    self.alert_by_mail(item,res[item])
                new_log = []

                line_record = res
            except Exception as e:
                getLogger('log_daemon').debug('ERROR:[MYSQL_GET_TBLOG3:new_log_monitor]')
                FWLOG_DEBUG('ERROR:[MYSQL_GET_TBLOG3:new_log_monitor]%s' % e)
                pass
            time.sleep(5)

        FWLOG_DEBUG('QUIT:[MYSQL_GET_TBLOG3:new_log_monitor]')
        getLogger('log_daemon').debug('QUIT:[MYSQL_GET_TBLOG3:new_log_monitor]')
        pass

    def parse_db_line(self,tb,ln):
        #ln = list(ln)
        ln['iTime'] = time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(ln['iTime']))
        if tb == "m_tblog_ddos":
            return u'时间=%s 事件=%s 源地址=%s 阈值=%s 目标地址=%s' % (ln['iTime'],ln['sEventName'],ln['sSourceIP'],ln['sThreshold'],ln['sTargetIP'])
        elif tb == "m_tblog_ips":
            return u'时间=%s 事件=%s 源地址=%s 协议=%s 目标地址=%s' % (ln['iTime'],ln['sEventName'],ln['sSourceIP'],ln['sProtocol'],ln['sTargetIP'])
        elif tb == "m_tblog_evil_code":
            return u'时间=%s 病毒名称=%s 源地址=%s 协议=%s 目标地址=%s' % (ln['iTime'],ln['sViruesName'],ln['sSourceIP'],ln['sProtocol'],ln['sTargetIP'])
        elif tb == "m_tblog_webapplication":
            return u'时间=%s 事件=%s 源地址=%s 漏洞类型=%s 目标地址=%s' % (ln['iTime'],ln['sEventName'],ln['sSourceIP'],ln['sBugType'],ln['sTargetIP'])
        else:
            getLogger('log_daemon').debug('parse_db_line:No this parser')
            return ''
            pass

    def alert_by_mail(self,name,number):
        event= {"m_tblog_ddos":"DDOS警报","m_tblog_ips":"入侵防御警报","m_tblog_evil_code":"病毒防护警报","m_tblog_webapplication":"WEB应用防护警报"}
        title = event[name]
        res = get_ten_newest_lines_from_table(name)
        #write res into MAIL_CONTENT
        if res is not None:
            content = '\n'.join([self.parse_db_line(name,l) for l in res])
            beep_alert()
            send_email_msg('log', title, content)
        pass


    def record_tables(self):
        """
            Description:
                Find out the newest table name of log
        """
        sql = ("SELECT table_name FROM information_schema.tables "
               "WHERE table_schema='db_firewall_log' "
               "and table_name LIKE '%s_2%%' "
               "ORDER BY table_name DESC LIMIT 1")

        tables = [fetchone_sql(sql % tb) for tb in tb_list]

        self.lst = {tb_list[i]:str(tb_list[i])
                    if tables[i] == None else str(tables[i]['table_name'])
                    for i in range(4)}

        sql = ('INSERT INTO ' + self.s_tb + ' '
               '(sName,sValue) VALUES ("AttackTables","%s") ON DUPLICATE KEY'
               ' UPDATE sValue="%s";')

        execute_sql(sql % (self.lst,self.lst))

    def record_lines(self):
        """
            Description:
                Record counts of lines, save the result in m_tbstatistics/AttackCategory
                Records are saved in tables m_tblog_[log_name]_recrod
        """
        d = {}

        sql = "SELECT CONCAT(SUM(iCount),'') as iCount from %s"
        for name in TB:
            res = fetchone_sql(sql % TB[name])['iCount']
            d[name] = 0 if res is None else int(res)

        sql = ('INSERT INTO ' + self.s_tb + ' '
               '(sName,sValue) VALUES ("AttackCategory","%s") ON DUPLICATE KEY'
               ' UPDATE sValue="%s";')

        execute_sql(sql % (d, d))

        return d

if __name__ == '__main__':
    logimport = LogImport()
    #logimport.run()
    logimport.start()
    time.sleep(30)
    print 'stop the thread'
    logimport.stop()
    #logimport.record_tables()
    # logimport.record_lines()
    # logimport.new_log_monitor()
