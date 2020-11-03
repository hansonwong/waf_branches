#!/usr/bin/env python
# coding=utf-8

import json
import time
from LogProcessor import LogProcessor
from LogCounter import LogCount, LOG_COUNT_MIN
from adutils.AcEngine import AcEngine
from adutils.audit_utils import timestr_to_timestamp, get_scc
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR

common_keys = ['sAppProto', 'iDate', 'sSrcMac', 'sSrcIP', 'iSrcPort',
               'sDstMac', 'sDstIP', 'iDstPort', 'sUser', 'sDept',
               'sScc', 'sSccFlag',
               'sAppName', 'sAction', 'sDeviceID']

append_keys = ['sAlertDetail', 'sAlertKeyword']

backquote_list = lambda x: ','.join(['`' + i + '`' for i in x])
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""
LOAD_SQL_GEN = lambda :load_sql % (backquote_list(common_keys))
LOAD_SQL_GEN_A = lambda :load_sql % (backquote_list(common_keys + append_keys))

class DropLogProcessor(LogProcessor):
    def __init__(self, _type, load_sql=LOAD_SQL_GEN()):
        # load_sql = LOAD_SQL_GEN()
        super(DropLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)


DropLog = DropLogProcessor('app_drop')

class DropParser(object):
    def __init__(self):
        super(DropParser, self).__init__()

    def parser_line(self, line, user_detail=None, ac_search=None, rlist=None):
        try:
            log = json.loads(line)
        except Exception as e:
            ADLOG_ERR('bd_local_parser:load json errror[%s]' % e)
            ADLOG_ERR(line)
            return None

        # app type
        app_proto = log['AppProto']

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


        # Description
        if app_proto == 'HTTP':
            app_name = log.get('SiteName', '')
            # http type
            log_type = log['Type']
            if log_type == 'httpurl':log_type = 'url_log'
            log_type = 'http_' + log_type
            action = log.get('Action')
        else:
            # if app_proto = app-drop/reject-bd-local-xxx
            app_name = log.get('Descr', '')
            # bd-local-x
            log_type = app_proto.split('-')[-1]
            # app-drop-bd-... or app-reject-bd-...
            action = app_proto.split('-')[1]
            # change app_proto:  app-drop/reject-bd-local-xxx ---> xxx
            app_proto = log_type


        # scc and scc_flag
        scc, scc_flag, overseas = get_scc(dip)

        device_id = log.get('device_id', '-')

        res = [app_proto, str(log_time), smac, sip, sport, dmac, dip, dport, user, dept,
               scc, str(scc_flag),
               app_name, action, device_id]

        LogCount([log_min, log_type, 'filter', sip, user, dept, '-',
                  int(overseas), device_id]).send_count()

        return '\t'.join(res)
