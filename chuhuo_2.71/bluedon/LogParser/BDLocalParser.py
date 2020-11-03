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
               'sDescr', 'sDeviceID']

append_keys = ['sAlertDetail', 'sAlertKeyword']

backquote_list = lambda x: ','.join(['`' + i + '`' for i in x])
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""
LOAD_SQL_GEN = lambda :load_sql % (backquote_list(common_keys))
LOAD_SQL_GEN_A = lambda :load_sql % (backquote_list(common_keys + append_keys))


class BDLocalLogProcessor(LogProcessor):
    def __init__(self, _type, load_sql=LOAD_SQL_GEN()):
        # load_sql = LOAD_SQL_GEN()
        super(BDLocalLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)

BD_LOCAL_TYPES = ['p2p', 'proxy', 'game', 'trojan', 'stock']
# p2p proxy game trojan
P2PLog = BDLocalLogProcessor('p2p')
P2POverseasLog = BDLocalLogProcessor('p2p_overseas')
P2PAlertLog = BDLocalLogProcessor('alert_p2p', load_sql=LOAD_SQL_GEN_A())

ProxyLog = BDLocalLogProcessor('proxy')
ProxyOverseasLog = BDLocalLogProcessor('proxy_overseas')
ProxyAlertLog = BDLocalLogProcessor('alert_proxy', load_sql=LOAD_SQL_GEN_A())

GameLog = BDLocalLogProcessor('game')
GameOverseasLog = BDLocalLogProcessor('game_overseas')
GameAlertLog = BDLocalLogProcessor('alert_game', load_sql=LOAD_SQL_GEN_A())

TrojanLog = BDLocalLogProcessor('trojan')
TrojanOverseasLog = BDLocalLogProcessor('trojan_overseas')
TrojanAlertLog = BDLocalLogProcessor('alert_trojan', load_sql=LOAD_SQL_GEN_A())

StockLog = BDLocalLogProcessor('stock')
StockOverseasLog = BDLocalLogProcessor('stock_overseas')
StockAlertLog = BDLocalLogProcessor('alert_stock', load_sql=LOAD_SQL_GEN_A())


class BDLocalParser(object):
    def __init__(self):
        super(BDLocalParser, self).__init__()

    def parser_line(self, line, user_detail=None, ac_search=None, rlist=None):
        try:
            log = json.loads(line)
        except Exception as e:
            ADLOG_ERR('bd_local_parser:load json errror[%s]' % e)
            ADLOG_ERR(line)
            return None, None, None, None

        # app type
        app_name = log['AppProto']
        typ = app_name.split('-')[-1]
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
        descr = log['Descr']

        # scc and scc_flag
        scc ,scc_flag, overseas = get_scc(dip)

        device_id = log.get('device_id', '-')

        res = [app_name, str(log_time), smac, sip, sport, dmac, dip, dport, user, dept,
               scc, str(scc_flag),
               descr, device_id]

        # alert function
        ac_ret = None
        if ac_search is not None and rlist is not None:
            ret = {}
            _all_keywords = []
            # search as content
            # ret['Descr'] = ac_search(None, 0, AcEngine.TYPE_CONTENT, descr, sip, rlist)
            # sear as title
            ret['Descr'] = ac_search(log, 0, AcEngine.TYPE_TITLE, descr, sip, rlist)
            _all_keywords.extend(ret['Descr'])

            if _all_keywords:
                _js = json.dumps(ret, encoding="UTF-8", ensure_ascii=False)
                ac_ret = '\t'.join(res) + '\t' + _js + '\t' + '#' + '#'.join(_all_keywords)
                # print ac_ret

                for kw in _all_keywords:
                    LogCount([log_min, typ, 'alert', sip, user, dept, kw,
                              int(overseas), device_id]).send_count()
            else:
                LogCount([log_min, typ, 'audit', sip, user, dept, '-',
                          int(overseas), device_id]).send_count()
            pass

        return '\t'.join(res), typ, overseas, ac_ret
