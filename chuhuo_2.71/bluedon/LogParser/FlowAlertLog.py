#!/usr/bin/env python
# coding=utf-8

import json
import time
from LogProcessor import LogProcessor
from LogCounter import LogCount, LOG_COUNT_MIN
from adutils.AcEngine import AcEngine
from adutils.audit_utils import timestr_to_timestamp, get_scc
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR

common_keys = ['iTime', 'sIP', 'sAlertType', 'iFlowTraffic', 'iDstPort',
               'sUser', 'sDept']


backquote_list = lambda x: ','.join(['`' + i + '`' for i in x])
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""
LOAD_SQL_GEN = lambda :load_sql % (backquote_list(common_keys))

class FlowAlertLogProcessor(LogProcessor):
    def __init__(self, _type, load_sql=LOAD_SQL_GEN()):
        # load_sql = LOAD_SQL_GEN()
        super(FlowAlertLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)


FlowAlertLog = FlowAlertLogProcessor('alert_audit_traffic')

class FlowAlertParser(object):
    def __init__(self):
        super(FlowAlertParser, self).__init__()

    def parser_line(self, line, user_detail=None, ac_search=None, rlist=None):
        try:
            log = json.loads(line)
        except Exception as e:
            ADLOG_ERR('alert_audit_traffic:load json errror[%s]' % e)
            ADLOG_ERR(line)
            return None

        itime = int(log.get('itime'))
        sip = log.get('SrcIP')
        alert_type = log.get('alert_type')
        traffic = log.get('flow_traffic')
        dport = log.get('DstPort')

        if user_detail is not None and sip in user_detail:
            # user= user_detail[sip][0]
            # dept = user_detail[sip][1]
            user, dept = user_detail[sip]
        else:
            user= 'Anonymous'
            dept = 'Anonymous'


        res = [str(itime), sip, alert_type, str(traffic), str(dport), user, dept]

        return '\t'.join(res)
