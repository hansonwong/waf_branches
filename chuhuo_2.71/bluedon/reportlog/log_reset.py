#!/usr/bin/env python
# coding=utf-8

"""
    0. All *.log files
        /var/log/fw/*.log
        /var/log/bdwaf/logs/url_filter.log
        /var/log/suricata/*.log
        /var/log/*.log

    1. All Mysql log TABLES and log RECORD

    2. Other log TABLES
        'm_tblogtable',
        'm_tblog_library'

        'm_tboperatelog',
        'm_tbloginlog',
        'm_tbhoneypot_log',
        'm_tbhoneypot_status',
        'm_tbrevcamera_log',
        'm_tbprotected_log'
        'm_tbauthenticate_log'

    3. Traffice Statistics Data
        m_tbuser_icmp_traffic
        m_tbuser_tcp_traffic
        m_tbuser_udp_traffic

    4. All Mysql log TABLES backup files
        /var/log/log_tables_backup/

    5. All log archive files
        /var/log_bak/*.tar

    6. Delete log files backup by system, with file name like
    'log_name.log-YYYYMMDD' of 'log_name.log.x'

    7. m_tbstatistics/m_tblog_size_record
        Reset Values but not clear

"""


import os
import sys


os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')


from db.config import execute_sql as exec_3306
from db.config1 import execute_sql as exec_3307
from db.config1 import fetchall_sql as fcal_3307


#LOG FILEs
LOG_PATH_CLEAR = ['/var/log/bdwaf/logs/url_filter.log',
                  '/var/log/ddos/bd_ddos.log',
                  '/var/log/fw/iptables-ng.log',
                  '/var/log/suricata/fast.log',
                  '/var/log/suricata/AvScan.log',
                  '/var/log/suricata/smtp.log',
                  '/var/log/messages',
                  '/var/log/maillog',
                  '/var/log/wifi_audit.log',
                  '/var/log/suricata/session.log',
                  '/usr/local/ipsec-vpn/etc/racoon.log']

LOG_PATH_REMOVE = ['/var/log/bdwaf/logs/audit/*',
                   '/var/log/cron-*',
                   '/var/log/maillog-*',
                   '/var/log/messages-*',
                   '/var/log/btmp-*',
                   '/var/log/wtmp-*',
                   '/var/log/secure-*',
                   '/var/log/spooler-*',
                   '/var/log/wifi_audit.log-*']

#LOG ARCHIVES
LOG_ARCHIVES = '/var/log_bak/*.*'

#LOG TABLES BACKUP
LOG_TABLES_BAK = '/var/log/log_tables_backup/'

#DROP
LOG_TABLES = ("SELECT TABLE_NAME from information_schema.`TABLES` "
              "WHERE TABLE_NAME LIKE 'm_tb%_2%';")

LOG_RECORDS = ("SELECT TABLE_NAME from information_schema.`TABLES` "
               "WHERE TABLE_NAME LIKE 'm_tblog_%_record';")

#CLEAR
other_tb = ['m_tbauthenticate_log',
            'm_tblogtable',
            'm_tblog_library',
            'm_tbloginlog',
            'm_tbhoneypot_log',
            'm_tbhoneypot_status',
            'm_tbrevcamera_log',
            'm_tbprotected_log',
            'm_tboperatelog']

other_tb_3306 = ['m_tboperatelog',
                 'm_tbloginlog',
                 'm_tbhoneypot_log',
                 'm_tbhoneypot_status']

#no add/delete/modify administrator
sys_log = ['m_tbloginlog','m_tblog_sys_backup','m_tblog_sys_reboot',
           'm_tblog_sys_resource']


#TRAFFIC STATISTICS DATA
TRAFFIC_STAT = ['m_tbuser_icmp_traffic',
                'm_tbuser_tcp_traffic',
                'm_tbuser_udp_traffic']

def drop_tables():
    tables = []
    # get table names
    for res in fcal_3307(LOG_TABLES):
        tables.append(res['TABLE_NAME'])
    if tables:
        drop = ('DROP TABLES %s' % ','.join(tables))
        exec_3307(drop)
    pass


def _clear_a_table(tb):
    exec_3307('DELETE FROM %s' % tb)


def clear_tables():
    # clear log records
    for res in fcal_3307(LOG_RECORDS):
        exec_3307('DELETE FROM %s' % res['TABLE_NAME'])

    #clear sys_log
    for res in sys_log:
        exec_3307('DELETE FROM %s' % res)

    #clear other_tb
    for res in other_tb:
        exec_3307('DELETE FROM %s' % res)

    #clear other tables in 3306
    for res in other_tb_3306:
        exec_3306('DELETE FROM %s' % res)
        # clear in 3307 either
        # exec_3307('DELETE FROM %s' % res)

    #clear traffic_stat
    for res in TRAFFIC_STAT:
        exec_3306('DELETE FROM %s' % res)
    pass


def clear_log_files():
    # clear log files
    for f in LOG_PATH_CLEAR:
        os.system('echo > %s' % f)


def delete_log_files():
    # delete log files, which are backup by system
    for f in LOG_PATH_REMOVE:
        os.system('rm -fr  %s' % f)


def delete_log_archive():
    # delete log archives in /var/log_bak
    os.system('rm -f %s' % LOG_ARCHIVES)


def delete_log_backup():
    os.system("find %s -name '*.sql' -delete" % LOG_TABLES_BAK)


def reset_m_tbstatistics():
    import ast

    cate = ast.literal_eval(
        "{'m_tblog_ddos': 0, 'm_tblog_ips': 0, "
        "'m_tblog_webapplication': 0, "
        "'m_tblog_evil_code': 0}")

    attk = ast.literal_eval(
        "{'m_tblog_ddos': 'm_tblog_ddos', "
        "'m_tblog_ips': 'm_tblog_ips', "
        "'m_tblog_webapplication': 'm_tblog_webapplication', "
        "'m_tblog_evil_code': 'm_tblog_evil_code'}")

    exec_3307('DELETE FROM m_tbstatistics')
    sql = ('INSERT INTO m_tbstatistics '
           '(sName,sValue) VALUES ("%s","%s") ON DUPLICATE KEY'
           ' UPDATE sValue="%s";')

    exec_3307(sql % ('AttackCategory', cate, cate))
    exec_3307(sql % ('AttackTables', attk, attk))
    # sql = ('SELECT * FROM m_tbstatistics LIMIT 2')
    # update = ('UPDATE m_tbstatistics SET sValue="%s" WHERE sName="%s"')
    # for record in fcal_3307(sql):
    #     # get Attackcategory, Set all log record equal 0
    #     if record['sName'] == 'AttackCategory':
    #         res = ast.literal_eval(record['sValue'])
    #         for key in res:
    #             res[key] = 0
    #         exec_3307(update % (res, 'AttackCategory'))
    #     # get Attacktables, Set all newest table name equal log name
    #     elif record['sName'] == 'AttackTables':
    #         res = ast.literal_eval(record['sValue'])
    #         for key in res:
    #             res[key] = key
    #         exec_3307(update % (res, 'AttackTables'))


def reset_log_size_record():
    import time
    from reportlog.log_size_record import tb_list
    t = time.time()

    # tb_list=[
    #     "http_log","dns_log","fast_log","eve_json",
    #     "iptables-ng_log","ddos_log","url_log","app_admin",
    #     "evil_code","info_leak","webaudit_log","web_app"
    # ]

    exec_3307('DELETE FROM m_tblog_size_record')
    for tb in tb_list:
        _sql = ('insert into m_tblog_size_record(sLogName,sImportSize,'
                'iTime) values("%s",%s,%s)')
        exec_3307(_sql % (tb,0,t))


if __name__ == '__main__':
    # """
    #     0. All *.log files
    #         /var/log/fw/*.log
    #         /var/log/bdwaf/logs/url_filter.log
    #         /var/log/suricata/*.log
    #         /var/log/*.log
    # """
    clear_log_files()

    # """
    #     1. All Mysql log TABLES and log RECORD
    #     2. Other log TABLES
    #         'm_tblogtable',
    #         'm_tblog_library'

    #         'm_tboperatelog',
    #         'm_tbloginlog',
    #         'm_tbhoneypot_log',
    #         'm_tbhoneypot_status',
    #         'm_tbrevcamera_log',
    #         'm_tbprotected_log'
    #         'm_tbauthenticate_log'
    #     3. Traffice Statistics Data
    #         m_tbuser_icmp_traffic
    #         m_tbuser_tcp_traffic
    #         m_tbuser_udp_traffic
    # """
    drop_tables()
    clear_tables()

    # """
    #     4. All Mysql log TABLES backup files
    #         /var/log/log_tables_backup/
    # """
    delete_log_backup()

    # """
    #     5. All log archive files
    #         /var/log_bak/*.tar
    # """
    delete_log_archive()

    # """
    #     6. Delete log files backup by system, with file name like
    #     'log_name.log-YYYYMMDD' of 'log_name.log.x'
    # """
    delete_log_files()
    # """
    #     7. m_tbstatistics
    #         Reset Values but not clear
    # """
    reset_m_tbstatistics()
    reset_log_size_record()

    pass

