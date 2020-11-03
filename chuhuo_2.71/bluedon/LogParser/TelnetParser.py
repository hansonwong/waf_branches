#!/usr/bin/env python
# coding=utf-8

import os
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
               'sUserName', 'sPassword', 'sAction', 'sFilename', 'sDeviceID']

append_keys = ['sAlertDetail', 'sAlertKeyword']

backquote_list = lambda x: ','.join(['`' + i + '`' for i in x])
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""
LOAD_SQL_GEN = lambda :load_sql % (backquote_list(common_keys))
LOAD_SQL_GEN_A = lambda :load_sql % (backquote_list(common_keys + append_keys))


class TelnetLogProcessor(LogProcessor):
    def __init__(self, _type='telnet', load_sql=LOAD_SQL_GEN()):
        super(TelnetLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)

TelnetLog = TelnetLogProcessor()
TelnetOverseasLog = TelnetLogProcessor('telnet_overseas')
TelnetAlertLog = TelnetLogProcessor('alert_telnet', load_sql=LOAD_SQL_GEN_A())


class TelnetParser(object):
    def __init__(self):
        super(TelnetParser, self).__init__()

    def parser_line(self, line, user_detail=None, ac_search=None, rlist=None):
        try:
            log = json.loads(line)
        except Exception as e:
            ADLOG_ERR('telnet_parser:load json errror[%s]' % e)
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

        username = log['UserName'] or ''
        password = log['PassWord'] or ''
        action = log['Action'] or ''
        filename = log['FileName'] or ''

        # telnet file process
        if filename != '':
            if os.path.exists(filename):
                os.system('chmod 0777 %s' % filename)
        #         tmpfile = filename + '.tmp'
        #         newfile = filename.split('.')[0] + '_new' + filename.split('.')[1]
        #         ADLOG_DEBUG('print filename content')
        #         with open(filename, 'r') as fp:
        #             for l in fp.readlines():
        #                 ADLOG_DEBUG(l)
        #         ADLOG_DEBUG('print filename content done')
        #         os.system('/usr/local/bin/iconv -f GB2312 -t UTF-8 {inf} > {of}'.format(inf=filename, of=tmpfile))
        #         ADLOG_DEBUG('/usr/local/bin/iconv -f GB2312 -t UTF-8 {inf} > {of}'.format(inf=filename, of=tmpfile))
        #         os.system('/usr/bin/filt -T {inf} > {of}'.format(inf=tmpfile, of=filename))
        #         ADLOG_DEBUG('/usr/bin/filt -T {inf} > {of}'.format(inf=tmpfile, of=filename))

        device_id = log.get('device_id', '-')
        res = [app_name, str(log_time), smac, sip, sport, dmac, dip, dport, user, dept,
               scc, str(scc_flag),
               username, password, action, filename, device_id]

        # alert function
        ac_ret = None
        if ac_search is not None and rlist is not None:
            ret = {}
            _all_keywords = []
            if filename:
                # search filename
                ret['filename'] = ac_search(log, 0, AcEngine.TYPE_FILE_NAME,
                                            filename, sip, rlist)
                _all_keywords.extend(ret['filename'])
                ret['file_content'] = ac_search(log, 0, AcEngine.TYPE_FILE_CONTENT,
                                                filename, sip, rlist)
                _all_keywords.extend(ret['file_content'])

                if _all_keywords:
                    _js = json.dumps(ret, encoding="UTF-8", ensure_ascii=False)
                    ac_ret = '\t'.join(res) + '\t' + _js + '\t' + '#' + '#'.join(_all_keywords)

                    for kw in _all_keywords:
                        LogCount([log_min, 'telnet', 'alert', sip, user, dept, kw,
                                  int(overseas), device_id]).send_count()
            else:
                LogCount([log_min, 'telnet', 'audit', sip, user, dept, '-',
                          int(overseas), device_id]).send_count()
                # print ac_ret

        return '\t'.join(res), overseas, ac_ret
