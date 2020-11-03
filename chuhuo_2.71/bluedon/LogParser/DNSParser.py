#!/usr/bin/env python
# coding=utf-8

import json
import time
import chardet
from LogProcessor import LogProcessor
from LogCounter import LogCount, LOG_COUNT_MIN
from adutils.AcEngine import AcEngine
from adutils.audit_utils import timestr_to_timestamp, get_scc
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR
from adutils.LogReportEngine import get_report_template, render_report_template, AuditLogReporter

common_keys = ['sAppProto', 'iDate', 'sSrcMac', 'sSrcIP', 'iSrcPort',
               'sDstMac', 'sDstIP', 'iDstPort', 'sUser', 'sDept',
               'sScc', 'sSccFlag',
               'sDomain', 'sIPs', 'sDeviceID']

append_keys = ['sAlertDetail', 'sAlertKeyword']

backquote_list = lambda x: ','.join(['`' + i + '`' for i in x])
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""
LOAD_SQL_GEN = lambda :load_sql % (backquote_list(common_keys))
LOAD_SQL_GEN_A = lambda : load_sql % (backquote_list(common_keys + append_keys))


class DNSLogProcessor(LogProcessor):
    def __init__(self, _type='dns_log', load_sql=LOAD_SQL_GEN()):
        # load_sql = LOAD_SQL_GEN()
        super(DNSLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)

DNSLog = DNSLogProcessor()
DNSOverseasLog = DNSLogProcessor('dns_log_overseas')
DNSAlertLog = DNSLogProcessor(_type='alert_dns_log', load_sql=LOAD_SQL_GEN_A())


class DNSParser(object):
    def __init__(self):
        super(DNSParser, self).__init__()

    def parser_line(self, line, user_detail=None, ac_search=None, rlist=None):
        try:
            log = json.loads(line)
        except Exception as e:
            ADLOG_ERR('dns_parser:load json errror[%s]' % e)
            ADLOG_ERR(line)
            return None, None, None

        # app type
        app_name = log['AppProto']
        # time
        log_time = timestr_to_timestamp(log['Date'])
        log_min = log_time - (log_time % LOG_COUNT_MIN)
        # log_time = str(log_time)

        # source mac
        smac = log['SrcMac']
        # source ip
        sip = log['SrcIP']
        # source port
        sport = str(log['SrcPort'])

        if user_detail is not None and sip in user_detail:
            # user= user_detail[sip][0]
            # dept = user_detail[sip][1]
            user, dept = user_detail[sip]
        else:
            user= 'Anonymous'
            dept = 'Anonymous'

        # destination mac
        dmac = log['DstMac']
        # destination ip
        dip = log['DstIP']
        # destination port
        dport = str(log['DstPort'])

        # scc and scc_flag
        scc ,scc_flag, overseas = get_scc(dip)

        domain = log['Domain']
        ips = log['Ip']
        device_id = log.get('device_id', '-')

        res = [app_name, str(log_time), smac, sip, sport, dmac, dip, dport, user, dept,
               scc, str(scc_flag),
               domain, ips, device_id]

        # alter function
        ac_ret = None
        if ac_search is not None and rlist is not None:
            ret = {}
            _all_keywords = []
            ret['domain'] = ac_search(log, 0, AcEngine.TYPE_CONTENT,
                                        domain, sip, rlist)
            _all_keywords.extend(ret['domain'])
            ret['ips'] = ac_search(log, 0, AcEngine.TYPE_CONTENT,
                                         ips, sip, rlist)
            _all_keywords.extend(ret['ips'])
            pass


            if _all_keywords:
                _js = json.dumps(ret, encoding="UTF-8", ensure_ascii=False)
                ac_ret = '\t'.join(res) + '\t' + _js + '\t' + '#' + '#'.join(_all_keywords)
                # print 'FTP Alert log result:'
                # print ac_ret
                for kw in _all_keywords:
                    LogCount([log_min, 'dns_log', 'alert', sip, user, dept, kw,
                              int(overseas), device_id]).send_count()
            else:
                LogCount([log_min, 'dns_log', 'audit', sip, user, dept, '-',
                          int(overseas), device_id]).send_count()


            pass

        return '\t'.join(res), overseas, ac_ret
