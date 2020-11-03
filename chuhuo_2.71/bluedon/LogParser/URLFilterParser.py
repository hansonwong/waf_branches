#!/usr/bin/env python
# coding=utf-8

import os
import re
import json
import time
import chardet
from adutils.audit_utils import timestr_to_timestamp, get_scc
from LogProcessor import LogProcessor
from LogCounter import LogCount, LOG_COUNT_MIN
from adutils.AcEngine import AcEngine
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR
from adutils.LogReportEngine import get_report_template, render_report_template, AuditLogReporter

common_keys = ['sAppProto', 'iDate', 'sSrcMac', 'sSrcIP', 'iSrcPort',
               'sDstMac', 'sDstIP', 'iDstPort', 'sType',
               'sUri', 'sUser', 'sDept',
               'sScc', 'sSccFlag',
               'sUrlType', 'sRuleName','sRuleId','sRuleAction','sDeviceID']

append_keys = ['sAlertDetail', 'sAlertKeyword']

keys_len = {}


# return sql keys of different url filter application types
sql_keys = lambda x : ','.join(common_keys.extend(type_keys[x]))
# backquote
backquote_list = lambda x : ','.join(['`' + i + '`' for i in x])
# sql statement for different kind of http logs
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""

LOAD_SQL_GEN = lambda :load_sql % (backquote_list(common_keys))
LOAD_SQL_GEN_A = lambda : load_sql % (backquote_list(common_keys + append_keys))


_LEN = lambda x, y=1024 : x if len(x) < y else x[:y]


class URLFilterLogProcessor(LogProcessor):
    def __init__(self, _type='urlfilter', load_sql=LOAD_SQL_GEN()):
        # load_sql = LOAD_SQL_GEN()
        super(URLFilterLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)

UrlFilterLog = URLFilterLogProcessor()
# UrlFilterOverseasLog = URLFilterLogProcessor('urlfilter_overseas')


class UrlFilterParser(object):
    def __init__(self):
        super(UrlFilterParser, self).__init__()

    def parser_line(self, line, user_detail=None, ac_search=None, rlist=None):

        try:
            line = re.sub(r'[\x01-\x1f]','', line)
            # line = line.replace('\\', '\\\\')
            line = line.replace('\r\n', '')
            confidence, code_set = chardet.detect(line)
            # if code_set != 'utf-8' and confidence > 0.95:
            #     line_recode = line.decode(code_set).encode('UTF-8')
            # else:
            #     line_recode = line

            # line_recode = line.decode(chardet.detect(line)['encoding']).encode('UTF-8')
            line_recode = line
            log = json.loads(line_recode, strict=False)
            # import ast
            # log = ast.literal_eval(line_recode)
            # log = json.loads(line.replace('\r\n', ''))
        except Exception as e:
            ADLOG_ERR('url_filter_log_parser: load json try correct[%s]' % e)
            ADLOG_ERR(chardet.detect(line))
            ADLOG_ERR(line)

            return None, None

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

        # type
        _type = 'url_filter'

        # host
        # host = log['Host']

        # Url
        url = log.get('Url', None)
        if url is None:
            url = ''.join([log['Host'], log['Uri']])


        device_id = log.get('device_id', '-')

        url_type = log.get('UrlType', '-')
        rule_name = log.get('RuleName', '-')
        rule_id = log.get('RuleId', '-')
        rule_action = log.get('RuleAction', '-')

        res = [app_name, str(log_time), smac, sip, sport, dmac, dip, dport, _type,
               url, user, dept, scc, str(scc_flag),
               url_type, rule_name, str(rule_id), str(rule_action), device_id]

        return '\t'.join(res), overseas
        pass



if __name__ == '__main__':
    import time
    try:
        lp = HttpLogProcessor('search', search_sql)
        # print lp.search_logfiles()
        lp.setDaemon(True)
        lp.start()
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        lp.stop()
        lp.join()
