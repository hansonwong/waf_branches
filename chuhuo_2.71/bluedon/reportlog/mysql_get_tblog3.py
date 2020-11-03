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
from reportlog.log_split_firewall import MysqlGetTblogFirewall
from reportlog.log_split_ips import MysqlGetTblogIps
from reportlog.log_split_ddos import MysqlGetTblogDdos
from reportlog.log_split_url import MysqlGetTblogUrl
from reportlog.log_split_info_leak import MysqlGetTblogInfoLeak
from reportlog.log_split_app_admin import MysqlGetTblogAppAdmin
from reportlog.log_split_evil_code import MysqlGetTblogEvilCode
from reportlog.log_split_webaudit import MysqlGetTblogWebaudit
from reportlog.log_split_web_app import MysqlGetTblogWebApp
from reportlog.mysql_log_backup import update_newest_table,get_ten_newest_lines_from_table
from reportlog.log_config import mail_test_attach,read_config_ini,beep_alert
from reportlog.ip_extraction import ip_extra
from reportlog.log_statistics import log_statistics_init
from reportlog.log_mail_config import send_email_msg
from db.config1 import execute_sql,executemany_sql,fetchone_sql,fetchall_sql,get_mysql_db,init_db_table
from homepage.statistics import import_switch,IMPORT_ON_OFF,IMPORT_IS_OFF, DISK_ALERT
from utils.log_logger import FWLOG_DEBUG

log_record = './log/log_record_split'
sleeptime = 0.5
tb_list = ['m_tblog_ddos','m_tblog_evil_code','m_tblog_ips','m_tblog_webapplication']
MAIL_CONTENT = r'/usr/local/bluedon/log/mail_content.txt'

LOG_PATH = { 'apa' : "/var/log/apply_controls/app_mgt_.log",
             'ddos': "/var/log/ddos/bd_ddos.log",
             'evc' : "/var/log/suricata/AvScan.log",
             'fw'  : "/var/log/fw/iptables-ng.log",
             'ifl' : "/var/log/suricata/smtp.log",
             'ips' : "/var/log/suricata/fast.log",
             'url' : "/var/log/bdwaf/logs/url_filter.log",
             'wbad': "/var/log/wifi_audit.log"
}

TB = {'m_tblog_evil_code'     :'m_tblog_evilcode_record',
      'm_tblog_ddos'          :'m_tblog_ddos_record',
      'm_tblog_ips'           :'m_tblog_ips_record',
      'm_tblog_webapplication':'m_tblog_webapp_record'}



class LogImport(threading.Thread):
    event = threading.Event()
    def __init__(self):
        super(LogImport,self).__init__()

        reload(sys)
        sys.setdefaultencoding('utf-8')
        # self.apa = MysqlGetTblogAppAdmin(path = LOG_PATH['apa'])
        self.ddos = MysqlGetTblogDdos(path = LOG_PATH['ddos'])
        self.evc = MysqlGetTblogEvilCode(path = LOG_PATH['evc'])
        self.fw = MysqlGetTblogFirewall(path = LOG_PATH['fw'])
        self.ifl = MysqlGetTblogInfoLeak(path = LOG_PATH['ifl'])
        self.ips = MysqlGetTblogIps(path = LOG_PATH['ips'])
        self.url = MysqlGetTblogUrl(path = LOG_PATH['url'])
        self.wbad = MysqlGetTblogWebaudit(path = LOG_PATH['wbad'])
        self.wbap = MysqlGetTblogWebApp()

        init_db_table()
        log_statistics_init()
        import_switch('on')

        self.lst = {}
        self.s_tb = 'm_tbstatistics'
        self.line_record = {'m_tblog_ddos': 0, 'm_tblog_ips': 0, 'm_tblog_evil_code': 0,'m_tblog_webapplication':0}

    def close_db(self,obj):
        pass

    def run(self):
        # start a new thread to monitor if new logs are comming
        thd_new_log = threading.Thread(target=self.new_log_monitor)
        thd_new_log.setDaemon(True)
        thd_new_log.start()

        while 1:
            try:
                if self.event.isSet():
                    FWLOG_DEBUG('EVENT SET:[MYSQL_GET_TBLOG3]')
                    getLogger('log_daemon').debug('EVENT SET:[MYSQL_GET_TBLOG3]')
                    # return
                    break

                # check if disk if full before importing log
                var_used = psutil.disk_usage('/var').percent
                if var_used > DISK_ALERT:
                    from reportlog.log_config import read_config_ini
                    FWLOG_DEBUG('MYSQL_GET_TBLOG3:import stop...because disk is too full...')
                    log_ini = read_config_ini('LOG Config')

                    if log_ini['full'] == 'cover':
                        from reportlog.log_clear import log_clear_release_disk
                        FWLOG_DEBUG('MYSQL_GET_TBLOG3:log cover...')
                        log_clear_release_disk(max_usage = DISK_ALERT)
                        FWLOG_DEBUG('MYSQL_GET_TBLOG3:log cover...done')

                    time.sleep(1)
                    continue

                # #check if somewhere has set `import` to 'off' to stop importing
                # # if not conf == 'on':
                # if os.path.exists(IMPORT_ON_OFF):
                #     FWLOG_DEBUG('mysql_get_tblog3:[LOG Config] import is set to off...')
                #     if not os.path.exists(IMPORT_IS_OFF):
                #         os.system('touch %s' % IMPORT_IS_OFF)
                #     time.sleep(1)
                #     continue
                # else:
                #     if os.path.exists(IMPORT_IS_OFF):
                #         os.system('rm -f %s' % IMPORT_IS_OFF)

                # self.apa.app_admin()
                ##getLogger('log_daemon').debug('app_admin done')
                self.ddos.ddos_log()
                ##getLogger('log_daemon').debug('ddos done')
                self.evc.evil_code()
                ##getLogger('log_daemon').debug('evil_code done')
                self.fw.iptables_ng_log()
                ##getLogger('log_daemon').debug('firewall done')
                self.ifl.info_leak()
                ##getLogger('log_daemon').debug('info_leak done')
                self.ips.fast_log()
                ##getLogger('log_daemon').debug('ips done')
                self.url.url_log()
                ##getLogger('log_daemon').debug('url done')
                self.wbad.webaudit_log()
                ##getLogger('log_daemon').debug('webaudit done')
                self.wbap.file_scanner()


                ip_extra()
                time.sleep(sleeptime)
            except Exception,e:
                FWLOG_DEBUG(e)
        thd_new_log.join()
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
            except:
                getLogger('log_daemon').debug('ERROR:[MYSQL_GET_TBLOG3:new_log_monitor]')
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
                Records are save in tables m_tblog_[log_name]_recrod
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
    #logimport.record_tables()
    # logimport.record_lines()
    logimport.new_log_monitor()
