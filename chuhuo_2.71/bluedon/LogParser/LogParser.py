#!/usr/bin/python
#-*- coding:utf-8 -*-
import time
import signal
import multiprocessing
import adutils.BcpUtil as BcpUtil
import adutils.thread
from multiprocessing import Manager
from adutils.AcEngine import AcEngine
from adutils.file_monitor_redis import FsMonitor
from adutils.LogReportEngine import LogReportEngine
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR
from adutils.audit_traffic_statistic import AuditTrafficStatistics
from adutils.statistic_cron_task import check_service as check_statistic_service
from adutils.logclear_cron_task import check_service as check_logclear_service
from RedisLog import RedisLog
from EmailParser import EmailLog, EmailOverseasLog, EmailAlertLog
from LogCounter import LogCounter, StatisticsLog
from FtpParser import FtpLog, FtpOverseasLog, FtpAlertLog
from SqlParser import SqlLog, SqlOverseasLog, SqlAlertLog
from HttpParser import HttpSearchLog, HttpWebMailLog, HttpBBSLog, HttpBlogLog, HttpNetStoreLog, HttpShoppingLog, HttpVideoLog, HttpWeiboLog, HttpUrlLog
from HttpParser import HttpSearchOverseasLog, HttpWebMailOverseasLog, HttpBBSOverseasLog
from HttpParser import HttpSearchAlertLog, HttpWebMailAlertLog, HttpBBSAlertLog, HttpBlogAlertLog, HttpNetStoreAlertLog, HttpShoppingAlertLog, HttpVideoAlertLog, HttpWeiboAlertLog, HttpUrlAlertLog
from HttpParser import HttpBlogOverseasLog, HttpNetStoreOverseasLog, HttpShoppingOverseasLog
from HttpParser import HttpVideoOverseasLog, HttpWeiboOverseasLog, HttpUrlOverseasLog
from BDLocalParser import P2PLog, P2POverseasLog, P2PAlertLog
from BDLocalParser import ProxyLog, ProxyOverseasLog, ProxyAlertLog
from BDLocalParser import GameLog, GameOverseasLog, GameAlertLog
from BDLocalParser import TrojanLog, TrojanOverseasLog, TrojanAlertLog
from BDLocalParser import StockLog, StockOverseasLog, StockAlertLog
from TelnetParser import TelnetLog, TelnetOverseasLog, TelnetAlertLog
from QQParser import QQLog, QQOverseasLog, QQAlertLog
from DNSParser import DNSLog, DNSOverseasLog, DNSAlertLog
from NetBIOSParser import NetBiosLog, NetBiosOverseasLog, NetBiosAlertLog
from NFSParser import NFSLog, NFSOverseasLog, NFSAlertLog
from FlowAlertLog import FlowAlertLog
from URLFilterParser import UrlFilterLog
from AppFilterParser import AppFilterLog
from DropLogParser import DropLog
from system_exception_check import SystemExceptionCheck
from system_exception_log import SystemExceptionLog
from adutils.mail_utils.log_mail_config import LogMail


EXIT_SIGNAL = 0
# register TERM signal action, when get TERM signal raise a runtimeerror
def sighandler(var1, var2):
    global EXIT_SIGNAL
    EXIT_SIGNAL = 1
    # raise RuntimeError('Get Exit Signal')


# process for all logs data loading
def log_proc(proc_list, _name, _flag):
    if not isinstance(proc_list, list):
        print '[LogParser:%s] arg error' % _name
        return

    _exit = 0
    def _sighandler(v1, v2): _exit = 1
    signal.signal(signal.SIGTERM,_exit)
    # start all log loading threads
    for proc in proc_list:
        proc.start()
        pass

    try:
        # wait for TERM signal
        while True:
            # if _flag.value: break
            if _exit: break
            time.sleep(1)
    except (KeyboardInterrupt, RuntimeError):
        ADLOG_DEBUG('Exit by Keyboard')
    finally:
        ADLOG_INFO('[LogParser:%s]audit log_proc exiting...' % _name)
        for proc in proc_list:
            proc.stop()
        for proc in proc_list:
            proc.join()
        ADLOG_INFO('[LogParser:%s]audit log_proc exiting...done' % _name)


def main():
    from adutils.audit_utils import ERR_TEXT, TIP_TEXT
    print TIP_TEXT('starting...')
    ADLOG_INFO('starting...')

    # not user in FW
    # # check service
    # check_statistic_service()
    # check_logclear_service()

    # file_monitor_redis, start first
    t_file_monitor = FsMonitor()
    t_file_monitor.start()


    # 创建bcp调度引擎
    t_bcp_dispatcher = BcpUtil.BcpDispatcher()
    # 启动bcp调度引擎
    t_bcp_dispatcher.start()

    acengine = None

    t_redis = RedisLog(t_bcp_dispatcher, acengine)
    t_redis.start()

    # not use in FW
    # # flow statistics thread
    # t_flow_record = AuditTrafficStatistics()
    # t_flow_record.start()

    # # system exception check and log
    # t_sys_ex_check = SystemExceptionCheck()
    # t_sys_ex_check.start()

    # t_sys_ex_log = SystemExceptionLog()
    # t_sys_ex_log.start()

    # t_logmail = LogMail()
    # t_logmail.start()

    # using multiprocess
    proc_list = [FtpLog, FtpOverseasLog,
                 SqlLog, SqlOverseasLog,
                 EmailLog, EmailOverseasLog,
                 HttpSearchLog, HttpSearchOverseasLog,
                 HttpWebMailLog, HttpWebMailOverseasLog,
                 HttpBBSLog, HttpBBSOverseasLog,
                 HttpBlogLog,HttpBlogOverseasLog,
                 HttpNetStoreLog, HttpNetStoreOverseasLog,
                 HttpShoppingLog, HttpShoppingOverseasLog,
                 HttpVideoLog, HttpVideoOverseasLog,
                 HttpWeiboLog, HttpWeiboOverseasLog,
                 HttpUrlLog, HttpUrlOverseasLog,
                 P2PLog, P2POverseasLog,
                 ProxyLog, ProxyOverseasLog,
                 GameLog, GameOverseasLog,
                 TrojanLog, TrojanOverseasLog,
                 TelnetLog, TelnetOverseasLog,
                 QQLog, QQOverseasLog,
                 DNSLog, DNSOverseasLog,
                 NetBiosLog, NetBiosOverseasLog,
                 NFSLog, NFSOverseasLog,
                 StockLog, StockOverseasLog,
                 UrlFilterLog, AppFilterLog]

    # ac_proc_list = [EmailAlertLog, FtpAlertLog,
    #                 HttpSearchAlertLog, HttpWebMailAlertLog,
    #                 HttpBBSAlertLog, HttpBlogAlertLog,
    #                 HttpNetStoreAlertLog, HttpShoppingAlertLog,
    #                 HttpVideoAlertLog, HttpWeiboAlertLog, HttpUrlAlertLog,
    #                 P2PAlertLog, ProxyAlertLog, GameAlertLog, TrojanAlertLog,
    #                 QQAlertLog, SqlAlertLog, TelnetAlertLog, StockAlertLog,
    #                 DNSAlertLog, NetBiosAlertLog, NFSAlertLog,
    #                 StatisticsLog, DropLog, FlowAlertLog]

    process_manager = Manager()
    flag = process_manager.Value('i', 0)

    p_log_processors = multiprocessing.Process(target=log_proc, args=(proc_list, 'LogProcessList', flag))
    p_log_processors.start()

    # not use in FW
    # p_alert_log_processors = multiprocessing.Process(target=log_proc, args=(ac_proc_list, 'AlertLogProcessList', flag))
    # p_alert_log_processors.start()

    # log_counter = LogCounter()
    # p_log_counter = multiprocessing.Process(target=log_counter.start_counter)
    # p_log_counter.start()

    # log_reporter = LogReportEngine()
    # p_log_reporter = multiprocessing.Process(target=log_reporter.start)
    # p_log_reporter.start()



    try:
        signal.signal(signal.SIGTERM,sighandler)
        while True:
            if EXIT_SIGNAL: break
            time.sleep(1)

    except KeyboardInterrupt:
        print ERR_TEXT('Exited By Keyboard')
    except Exception as e:
        print ERR_TEXT(e)
        ADLOG_ERR('ERROR: %s' % e)
    finally:
        print ERR_TEXT('Exiting...')
        ADLOG_INFO('Exiting...')

        # not use in FW
        # t_flow_record.stop()
        # t_sys_ex_log.stop()
        # t_sys_ex_check.stop()
        # t_logmail.stop()
        t_file_monitor.stop()
        t_bcp_dispatcher.stop()


        p_log_processors.terminate()
        # p_alert_log_processors.terminate()

        # p_log_reporter.terminate()
        # p_log_counter.terminate()

        p_log_processors.join()
        # p_alert_log_processors.join()
        # p_log_counter.join()

        t_redis.close()

        print ERR_TEXT('LogAuditor Process end')
        ADLOG_INFO('LogAuditor Process end')


if __name__ == '__main__':
    main()
