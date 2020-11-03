#!/usr/bin/python
#-*- coding:utf-8 -*-

import sys
import os

# os.chdir('/usr/local/bluedon')
# if '/usr/local/bluedon' not in sys.path:
#     sys.path.append('/usr/local/bluedon')

import redis
import json
import geoip2.database
import time
import threading
import logging

from netaddr import *
from adutils.BcpUtil import BcpWriter
from adutils.BcpUtil import BcpDispatcher
from adutils.AcEngine import AcType, AcEngine
from adutils.redis_utils.redis_op import REDIS_CHN_MYSQL
from LogProcessor import LogType
from HttpParser import HttpParser
from HttpParser import type_keys as HTTP_TYPES
from EmailParser import email_log_parser
from FtpParser import FtpParser
from SqlParser import SqlParser
from BDLocalParser import BDLocalParser, BD_LOCAL_TYPES
from TelnetParser import TelnetParser
from QQParser import QQParser
from DropLogParser import DropParser
from DNSParser import DNSParser
from NetBIOSParser import NetBiosParser
from NFSParser import NFSParser
from FlowAlertLog import FlowAlertParser
from URLFilterParser import UrlFilterParser
from AppFilterParser import AppFilterParser
from adutils.audit_utils import geo_info_item, get_auth_detail
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR
from adutils.audit_logger import rLog_dbg, rLog_err
from adutils.udp_sender import send_out, read_send_conf
from adutils.redis_utils.redis_remote_op import RemoteRedis, REDIS_CONF_REMOTE, tag_device_id
from adutils.device_connect import DeviceConnect
from adutils.ssl_category import SSLCategory


reload(sys)
sys.setdefaultencoding('utf-8')

ATT_PATH = '/home/cyren/checkfile/'
LOG_PATH = '/tmp/audit_log/'
LOG_SIZE = 1024 * 1024 * 2
LOG_INTERVAL = 10

REDIS_LOG = lambda x : rLog_dbg('redis_audit_record', x)
REDIS_ERR_LOG = lambda x : rLog_err('redis_audit_record', x)

# Log_Counter = AcType()
# counter decorator
def CountThisLog(counter):
    def count_this_dec(fn):
        def wrapper(*args, **kwargs):
            # counter.inc_counter(fn.__name__)
            fn(*args, **kwargs)
        return wrapper
    return count_this_dec

class RedisLog(threading.Thread):
    def __init__(self, bcp_dispatcher, ac_engine):
        threading.Thread.__init__(self, name = "redis_log_thread")
        self.setDaemon(True)
        self.closed = True
        self.bcp_dispatcher = bcp_dispatcher
        # self.acengine = AcEngine()
        # self.actype = self.acengine.actype
        self.acengine = None
        self.actype = AcType()

        # check if log path exists
        if not os.path.exists(LOG_PATH):
            os.system('mkdir -p %s' % LOG_PATH)

        def _new_bcp_writer(log_type, log_size=LOG_SIZE, log_interval=LOG_INTERVAL):
            _bcp = '{}.bcp'.format(log_type)
            _p = os.path.join(LOG_PATH, _bcp)
            _t = LogType(log_type)

            # add dynamic counter
            self.actype.add_counter(log_type)

            return BcpWriter(_p, log_interval, log_size, _t, ct=self.actype)

        # email bcp writer
        self.bcp_writer_mail = _new_bcp_writer("email_log")
        self.bcp_writer_mail_ove = _new_bcp_writer("email_log_overseas")
        self.bcp_writer_mail_alert = _new_bcp_writer("alert_email_log")

        self.bcp_dispatcher.appendBcp(self.bcp_writer_mail)
        self.bcp_dispatcher.appendBcp(self.bcp_writer_mail_ove)
        self.bcp_dispatcher.appendBcp(self.bcp_writer_mail_alert)
        # ftp bcp writer
        self.bcp_writer_ftp = _new_bcp_writer("ftp_log")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_ftp)

        self.bcp_writer_ftp_ove = _new_bcp_writer("ftp_log_overseas")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_ftp_ove)

        self.bcp_writer_ftp_alert = _new_bcp_writer("alert_ftp_log")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_ftp_alert)

        # sql bcp writer
        self.bcp_writer_sql = _new_bcp_writer("sql_log")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_sql)

        self.bcp_writer_sql_ove = _new_bcp_writer("sql_log_overseas")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_sql_ove)

        self.bcp_writer_sql_alert = _new_bcp_writer("alert_sql_log")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_sql_alert)

        # telnet bcp writer
        self.bcp_writer_telnet = _new_bcp_writer("telnet")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_telnet)

        self.bcp_writer_telnet_ove = _new_bcp_writer("telnet_overseas")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_telnet_ove)

        self.bcp_writer_telnet_alert = _new_bcp_writer("alert_telnet")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_telnet_alert)

        # qq bcp writer
        self.bcp_writer_qq = _new_bcp_writer("qq")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_qq)

        self.bcp_writer_qq_ove = _new_bcp_writer("qq_overseas")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_qq_ove)

        self.bcp_writer_qq_alert = _new_bcp_writer("alert_qq")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_qq_alert)

        # add http log writer
        self.bcp_writer_http = {}
        self.bcp_writer_http_ove = {}
        self.bcp_writer_http_alert = {}
        for _type in HTTP_TYPES:
            # print _type
            http_type = 'http_{}'.format(_type)
            self.bcp_writer_http[_type] = _new_bcp_writer(http_type)
            self.bcp_dispatcher.appendBcp(self.bcp_writer_http[_type])
            # http overseas log
            http_type_ove = 'http_{}_overseas'.format(_type)
            self.bcp_writer_http_ove[_type] = _new_bcp_writer(http_type_ove)
            self.bcp_dispatcher.appendBcp(self.bcp_writer_http_ove[_type])
            # alert log
            http_type = 'alert_http_{}'.format(_type)
            self.bcp_writer_http_alert[_type] = _new_bcp_writer(http_type)
            self.bcp_dispatcher.appendBcp(self.bcp_writer_http_alert[_type])

        # add bd-local log writer
        self.bcp_writer_bd_local = {}
        self.bcp_writer_bd_local_ove = {}
        self.bcp_writer_bd_local_alert = {}
        for _type in BD_LOCAL_TYPES:
            self.bcp_writer_bd_local[_type] = _new_bcp_writer(_type)
            self.bcp_dispatcher.appendBcp(self.bcp_writer_bd_local[_type])

            # overseas
            _type_ove = '{}_overseas'.format(_type)
            self.bcp_writer_bd_local_ove[_type] = _new_bcp_writer(_type_ove)
            self.bcp_dispatcher.appendBcp(self.bcp_writer_bd_local_ove[_type])
            # alert log
            alert_type = 'alert_{}'.format(_type)
            self.bcp_writer_bd_local_alert[_type] = _new_bcp_writer(alert_type)
            self.bcp_dispatcher.appendBcp(self.bcp_writer_bd_local_alert[_type])

        # statistics bcp writer
        # self.bcp_writer_st_email = _new_bcp_writer("statistics_email")
        # self.bcp_dispatcher.appendBcp(self.bcp_writer_st_email)

        # drop log  bcp writer
        self.bcp_writer_droplog = _new_bcp_writer("app_drop")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_droplog)

        # dns log bcp writer
        self.bcp_writer_dnslog = _new_bcp_writer("dns_log")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_dnslog)

        self.bcp_writer_dnslog_ove = _new_bcp_writer("dns_log_overseas")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_dnslog_ove)

        self.bcp_writer_dns_alert = _new_bcp_writer("alert_dns_log")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_dns_alert)

        # netbios log bcp writer
        self.bcp_writer_netbios = _new_bcp_writer("netbios")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_netbios)

        self.bcp_writer_netbios_ove = _new_bcp_writer("netbios_overseas")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_netbios_ove)

        self.bcp_writer_netbios_alert = _new_bcp_writer("alert_netbios")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_netbios_alert)

        # nfs log bcp writer
        self.bcp_writer_nfs = _new_bcp_writer("nfs")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_nfs)

        self.bcp_writer_nfs_ove = _new_bcp_writer("nfs_overseas")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_nfs_ove)

        self.bcp_writer_nfs_alert = _new_bcp_writer("alert_nfs")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_nfs_alert)

        # flow alert log  bcp writer
        self.bcp_writer_flowalert= _new_bcp_writer("alert_audit_traffic")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_flowalert)

        # url filter log bcp writer
        self.bcp_writer_urlfilter = _new_bcp_writer("urlfilter")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_urlfilter)

        # app filter log bcp writer
        self.bcp_writer_appfilter = _new_bcp_writer("appfilter")
        self.bcp_dispatcher.appendBcp(self.bcp_writer_appfilter)

        # processor for ssl
        self.ssl_category = SSLCategory()

    # statistics writer
    # pass

    # writer api
    # http log writer
    # @CountThisLog(Log_Counter)
    def write_http_log(self, typ, log):
        return self.bcp_writer_http[typ].write(log)

    # @CountThisLog(Log_Counter)
    def write_http_log_ove(self, typ, log):
        return self.bcp_writer_http_ove[typ].write(log)

    # @CountThisLog(Log_Counter)
    def write_http_alert(self, typ, log):
        return self.bcp_writer_http_alert[typ].write(log)

    # ftp log writer
    # @CountThisLog(Log_Counter)
    def write_ftp_log(self, log):
        return self.bcp_writer_ftp.write(log)

    # @CountThisLog(Log_Counter)
    def write_ftp_log_ove(self, log):
        return self.bcp_writer_ftp_ove.write(log)

    # @CountThisLog(Log_Counter)
    def write_ftp_log_alert(self, log):
        return self.bcp_writer_ftp_alert.write(log)

    # sql log writer
    # @CountThisLog(Log_Counter)
    def write_sql_log(self, log):
        return self.bcp_writer_sql.write(log)

    # @CountThisLog(Log_Counter)
    def write_sql_log_ove(self, log):
        return self.bcp_writer_sql_ove.write(log)

    # @CountThisLog(Log_Counter)
    def write_sql_log_alert(self, log):
        return self.bcp_writer_sql_alert.write(log)

    # telnet log writer
    # @CountThisLog(Log_Counter)
    def write_telnet(self, log):
        return self.bcp_writer_telnet.write(log)

    # @CountThisLog(Log_Counter)
    def write_telnet_ove(self, log):
        return self.bcp_writer_telnet_ove.write(log)

    # @CountThisLog(Log_Counter)
    def write_telnet_alert(self, log):
        return self.bcp_writer_telnet_alert.write(log)
    # qq log writer
    # @CountThisLog(Log_Counter)
    def write_qq(self, log):
        return self.bcp_writer_qq.write(log)

    # @CountThisLog(Log_Counter)
    def write_qq_ove(self, log):
        return self.bcp_writer_qq_ove.write(log)

    # @CountThisLog(Log_Counter)
    def write_qq_alert(self, log):
        return self.bcp_writer_qq_alert.write(log)

    # bd local log writer
    # @CountThisLog(Log_Counter)
    def write_bd_local(self, typ, log):
        return self.bcp_writer_bd_local[typ].write(log)

    # @CountThisLog(Log_Counter)
    def write_bd_local_ove(self, typ, log):
        return self.bcp_writer_bd_local_ove[typ].write(log)

    # @CountThisLog(Log_Counter)
    def write_bd_local_alert(self, typ, log):
        return self.bcp_writer_bd_local_alert[typ].write(log)

    # drop log
    # @CountThisLog(Log_Counter)
    def write_droplog(self, log):
        return self.bcp_writer_droplog.write(log)

    # dns log
    # @CountThisLog(Log_Counter)
    def write_dnslog(self, log):
        return self.bcp_writer_dnslog.write(log)

    # @CountThisLog(Log_Counter)
    def write_dnslog_ove(self, log):
        return self.bcp_writer_dnslog_ove.write(log)

    # netbios log
    # @CountThisLog(Log_Counter)
    def write_netbios(self, log):
        return self.bcp_writer_netbios.write(log)

    # @CountThisLog(Log_Counter)
    def write_netbios_ove(self, log):
        return self.bcp_writer_netbios_ove.write(log)

    # @CountThisLog(Log_Counter)
    def write_netbios_alert(self, log):
        return self.bcp_writer_netbios_alert.write(log)

    # nfs log
    # @CountThisLog(Log_Counter)
    def write_nfs(self, log):
        return self.bcp_writer_nfs.write(log)

    # @CountThisLog(Log_Counter)
    def write_nfs_ove(self, log):
        return self.bcp_writer_nfs_ove.write(log)

    # @CountThisLog(Log_Counter)
    def write_nfs_alert(self, log):
        return self.bcp_writer_nfs_alert.write(log)

    # flow alert log
    # @CountThisLog(Log_Counter)
    def write_flowalert(self, log):
        return self.bcp_writer_flowalert.write(log)

    # urlfilter log
    # @CountThisLog(Log_Counter)
    def write_urlfilter(self, log):
        return self.bcp_writer_urlfilter.write(log)

    # appfilter log
    # @CountThisLog(Log_Counter)
    def write_appfilter(self, log):
        return self.bcp_writer_appfilter.write(log)

    def close(self):
        self.closed = True
        self.join()


    def run(self):
        delay = 1
        msg_count = 0
        self.closed = False
        logging.debug('redis log start up %s', threading.currentThread())

        # ac_engine_reload_thread = threading.Thread(target=self.acengine.start_reload)
        # ac_engine_reload_thread.setDaemon(True)
        # ac_engine_reload_thread.start()

        geo = geo_info_item()
        # geo.get_geoinfo("56.23.52.41")
        # print geo.scc_flag, ("%s/%s/%s/%s") % (geo.continent, geo.country, geo.city, geo.subdivisions)
        # geo.get_geoinfo("220.181.12.17")
        # print geo.scc_flag, ("%s/%s/%s/%s") % (geo.continent, geo.country, geo.city, geo.subdivisions)

        # upload initial
        # upload_flag = False
        # try:
        #     # deviceconnect for message upload
        #     deviceconnect = DeviceConnect()
        #     deviceconnect.setDaemon(True)
        #     deviceconnect.start()
        #     upload_flag = True
        # except:
        #     pass

        # ssl rule update
        self.ssl_category.update_rule()

        while not self.closed:
            # record user detail for email log
            # user_detail = get_auth_detail()
            _t_check = int(time.time())
            # create parser for logs
            http_parser = HttpParser()
            ftp_parser = FtpParser()
            sql_parser = SqlParser()
            bd_local_parser = BDLocalParser()
            telnet_parser = TelnetParser()
            qq_parser = QQParser()
            droplog_parser = DropParser()
            dns_parser = DNSParser()
            nfs_parser = NFSParser()
            netbios_parser = NetBiosParser()
            flowalert_parser = FlowAlertParser()
            urlfilter_parser = UrlFilterParser()
            appfilter_parser = AppFilterParser()
            # send out by socket
            # ip, port, proto, status = read_send_conf()
            try:
                rc = redis.Redis(host='127.0.0.1')
                rc.ping()
                ps = rc.pubsub()
                ps.psubscribe(['netlog_*'])

            except Exception as e:
                logging.debug('can not connect to redis, sleep %d'% delay)
                ADLOG_ERR('can not connect to redis, error: %s'% e)
                ADLOG_ERR('can not connect to redis, sleep %d'% delay)
                if not self.closed:
                    # sleep delay seconds for next connection
                    time.sleep(delay)
                    delay = delay*2 if delay < 60 else 60
                continue

            # # upload log to remote redis
            # try:
            #     rc_remote = RemoteRedis(**REDIS_CONF_REMOTE)
            #     rc_remote.open()
            # except:
            #     rc_remote.close()

            logging.info('connect to redis')
            delay = 1
            user_detail = dict()
            while True:
                # add user_detail check
                _t_current = int(time.time())
                if _t_current - _t_check > 10:
                    _t_check = _t_current
                    # user_detail = get_auth_detail()
                    # Log_Counter.save_counter()
                    self.actype.save_counter()

                try:
                    item = ps.get_message()
                    if self.closed:
                        # self.acengine.stop_reload()
                        break
                    elif not item:
                        time.sleep(0.1)
                        continue
                except:
                    # 出现异常说明已经断开连接
                    logging.exception('redis disconnect...')
                    print('redis disconnect...')
                    ADLOG_ERR('redis disconnect...')
                    time.sleep(1)
                    break


                if item['type'] == 'pmessage':

                    try:
                        # # send out msg by udp/tcp
                        # try:
                        #     send_out(item['channel'], item['data'], ip, port, proto, status)

                        #     if 'device_id' in item['data']:
                        #         # just forward this message to up-level device
                        #         # rc_remote.publish(item['channel'], item['data'])
                        #         deviceconnect.forward_to_superiors(item['channel'], item['data'])
                        #         pass
                        #     else:
                        #         # tag by own device_id and forward to up-level
                        #         # device
                        #         # rc_remote.publish(item['channel'], tag_device_id(item['data']))
                        #         pass
                        #         # test statement
                        #         deviceconnect.upload_to_superiors(item['channel'], item['data'])
                        #         # rc_remote.publish(item['channel'], item['data'])
                        # except Exception as e:
                        #     print e
                        #     pass

                        # log parse
                        if item['channel'].startswith("netlog_email"):
                            res, isOverseas, ac_ret = email_log_parser(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_email)
                            if res is None:
                                continue

                            self.write_http_log('webmail', "%s\n" % res)

                            if isOverseas:
                                self.write_http_log_ove('webmail', "%s\n" % res)

                            if ac_ret is not None:
                                self.bcp_writer_http_alert['webmail'].write("%s\n" % ac_ret)
                                pass

                        elif item['channel'].startswith("netlog_http") or \
                            item['channel'].startswith("netlog_ssl"):

                            if 'ssl' in item['channel']:
                                # do ssl parse
                                item['data'] = self.ssl_category.parse_line (item['data'])
                                if len(item['data']) == 0: continue
                                pass

                            res, http_type, isOverseas, ac_ret = http_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)
                            if res is None:
                                continue

                            # if http_type == 'httpurl':http_type = 'url_log'
                            self.write_http_log(http_type, "%s\n" % res)

                            if isOverseas:
                                self.write_http_log_ove(http_type, "%s\n" % res)

                            if ac_ret is not None:
                                self.write_http_alert(http_type, "%s\n" % ac_ret)

                        elif item['channel'].startswith("netlog_ftp"):
                            res, isOverseas, ac_ret  = ftp_parser.ftp_parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_ftp)
                            if res is None:
                                continue

                            self.write_ftp_log("%s\n" % res)
                            if isOverseas:
                                self.write_ftp_log_ove("%s\n" % res)

                            if ac_ret is not None:
                                self.write_ftp_log_alert("%s\n" % ac_ret)

                        elif item['channel'].startswith("netlog_sql_log"):
                            res, isOverseas, ac_ret = sql_parser.sql_parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)
                            if res is None:
                                continue

                            self.write_sql_log("%s\n" % res)
                            if isOverseas:
                                self.write_sql_log_ove("%s\n" % res)

                            if ac_ret is not None:
                                self.write_sql_log_alert("%s\n" % ac_ret)

                        elif item['channel'].startswith("netlog_bd-local"):
                            res, _type, isOverseas, ac_ret = bd_local_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)
                            if res is None:
                                continue

                            self.write_bd_local(_type, "%s\n" % res)

                            if isOverseas:
                                self.write_bd_local_ove(_type, "%s\n" % res)

                            if ac_ret is not None:
                                self.write_bd_local_alert(_type, "%s\n" % ac_ret)

                        elif item['channel'].startswith("netlog_telnet"):
                            res, isOverseas, ac_ret = telnet_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)
                            if res is None:
                                continue

                            self.write_telnet("%s\n" % res)
                            if isOverseas:
                                self.write_telnet_ove("%s\n" % res)

                            if ac_ret is not None:
                                self.write_telnet_alert("%s\n" % ac_ret)

                        elif item['channel'].startswith("netlog_qq"):
                            res, isOverseas, ac_ret = qq_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)
                            if res is None:
                                continue

                            self.write_qq("%s\n" % res)
                            if isOverseas:
                                self.write_qq_ove("%s\n" % res)

                            if ac_ret is not None:
                                self.write_qq_alert("%s\n" % ac_ret)

                        # get drop/reject log
                        elif item['channel'].startswith("netlog_match_http") or \
                            item['channel'].startswith("netlog_app-drop-bd-local-"):
                            res = droplog_parser.parser_line(item['data'], user_detail)

                            if res is None:
                                continue

                            self.write_droplog("%s\n" % res)
                            pass

                        # dns log
                        elif item['channel'].startswith("netlog_dns"):
                            res, isOverseas, ac_ret = dns_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)

                            if res is None:
                                continue

                            self.write_dnslog("%s\n" % res)
                            if isOverseas:
                                self.write_dnslog_ove("%s\n" % res)

                            if ac_ret is not None:
                                self.bcp_writer_dns_alert("%s\n" % ac_ret)

                        # netbios log
                        elif item['channel'].startswith("netlog_netbios"):
                            res, isOverseas, ac_ret = netbios_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)

                            if res is None:
                                continue

                            self.write_netbios("%s\n" % res)
                            if isOverseas:
                                self.write_netbios_ove("%s\n" % res)

                            if ac_ret is not None:
                                self.write_netbios_alert("%s\n" % ac_ret)

                        # nfs log
                        elif item['channel'].startswith("netlog_nfs"):
                            res, isOverseas, ac_ret = nfs_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)

                            if res is None:
                                continue

                            self.write_nfs("%s\n" % res)
                            if isOverseas:
                                self.write_nfs_ove("%s\n" % res)

                            if ac_ret is not None:
                                self.write_nfs_alert("%s\n" % ac_ret)

                        # flow alert log
                        elif item['channel'].startswith("netlog_flow_alert"):
                            res = flowalert_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)

                            if res is None:
                                continue

                            self.write_flowalert("%s\n" % res)

                        # urlfilter log
                        elif item['channel'].startswith("netlog_url_filter"):
                            res, isOverseas = urlfilter_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)

                            if res is None:
                                continue

                            self.write_urlfilter("%s\n" % res)

                        # appfilter log
                        elif item['channel'].startswith("netlog_app_filter"):
                            res, isOverseas = appfilter_parser.parser_line(item['data'], user_detail,
                                                               None,
                                                               self.actype.ac_http_url)

                            if res is None:
                                continue

                            self.write_appfilter("%s\n" % res)

                        # get user detail when user login
                        # elif item['channel'] == REDIS_CHN_MYSQL:
                        #     msg = json.loads(item['data'])
                        #     # log here
                        #     ADLOG_DEBUG(msg)

                        #     if not isinstance(msg, dict):
                        #         ADLOG_DEBUG('Channel[%s] get wrong message...%s' % (REDIS_CHN_MYSQL, msg))
                        #         continue
                        #     uip = msg.get('userip', 'anonymous')
                        #     if msg.get('action', 0) == 1:
                        #         uname  = msg.get('username', 'anonymous')
                        #         gname = msg.get('groupname', 'anonymous')
                        #         if not uip == 'anonymous':
                        #             user_detail[uip]=(uname, gname)
                        #     else:
                        #         try:
                        #             user_detail.pop(uip)
                        #         except KeyError:
                        #             # log here
                        #             ADLOG_DEBUG('user_detail:[%s] is not exists' % uip)
                        #     ADLOG_DEBUG('user_detail now is: %s' % user_detail)


                        #     pass

                        msg_count += 1
                    except Exception as e:
                        # log here
                        print 'RedisLog Error'
                        print e
                        # ADLOG_ERR('[RedisLog Error][%s]' % e)
                        REDIS_ERR_LOG(e)
                        REDIS_ERR_LOG(item)
                        continue
                        # print 'msg_count = %d' % msg_count

        # deviceconnect.stop()
        # rc_remote.close()
        # Log_Counter.save_counter()
        self.actype.save_counter()
        # logging.debug('redis log thread exit %s', threading.currentThread())
        ADLOG_INFO('redis log thread exit %s' % threading.currentThread())
