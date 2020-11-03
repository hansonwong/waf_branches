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
               'sType', 'sStorepath', 'sFilename', 'sOldFilename', 'sFilesize', 'sDeviceID']

append_keys = ['sAlertDetail', 'sAlertKeyword']

backquote_list = lambda x: ','.join(['`' + i + '`' for i in x])
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""
LOAD_SQL_GEN = lambda :load_sql % (backquote_list(common_keys))
LOAD_SQL_GEN_A = lambda : load_sql % (backquote_list(common_keys + append_keys))

NFS_ACT_LIST = {
    'download': u'下载文件',
    'upload': u'上传文件',
    'rename': u'重命名',
    'delete': u'删除文件',
}


class NFSLogProcessor(LogProcessor):
    def __init__(self, _type='nfs', load_sql=LOAD_SQL_GEN()):
        # load_sql = LOAD_SQL_GEN()
        super(NFSLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)

NFSLog = NFSLogProcessor()
NFSOverseasLog = NFSLogProcessor('nfs_overseas')
NFSAlertLog = NFSLogProcessor(_type='alert_nfs', load_sql=LOAD_SQL_GEN_A())


class NFSParser(object):
    def __init__(self):
        super(NFSParser, self).__init__()

    def parser_line(self, line, user_detail=None, ac_search=None, rlist=None):
        try:
            det_ret = chardet.detect(line)
            code_set = det_ret.get('encoding')
            confidence = det_ret.get('confidence')

            if code_set != 'utf-8' and confidence > 0.95:
                try:
                    line_recode = line.decode(code_set).encode('UTF-8')
                except:
                    line_recode = line.decode('GB2312').encode('UTF-8')
            else:
                line_recode = line

            # log = json.loads(line)
            log = json.loads(line_recode)
        except Exception as e:
            ADLOG_ERR('nfs_parser:load json errror[%s]' % e)
            ADLOG_ERR('nfs_parser:load json errror[%s, %s]' % (code_set, confidence))
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

        action_type = log['Type']
        storepath = log.get('storepath', '-')
        fname = log.get('filename')
        oldfname = log.get('oldfilename', '-')
        fsize = log.get('filesize', '0')


        act = NFS_ACT_LIST.get(action_type)
        device_id = log.get('device_id', '-')

        res = [app_name, str(log_time), smac, sip, sport, dmac, dip, dport, user, dept,
               scc, str(scc_flag),
               act, storepath, fname, oldfname, str(fsize), device_id]

        # alter function
        ac_ret = None
        if ac_search is not None and rlist is not None:
            ret = {}
            _all_keywords = []
            # file name and content
            ret['filename'] = ac_search(log, 0, AcEngine.TYPE_FILE_NAME,
                                        fname, sip, rlist)
            _all_keywords.extend(ret['filename'])
            ret['file_content'] = ac_search(log, 0, AcEngine.TYPE_FILE_CONTENT,
                                         storepath, sip, rlist)
            _all_keywords.extend(ret['file_content'])
            pass

            if _all_keywords:
                _js = json.dumps(ret, encoding="UTF-8", ensure_ascii=False)
                ac_ret = '\t'.join(res) + '\t' + _js + '\t' + '#' + '#'.join(_all_keywords)

                for kw in _all_keywords:
                    LogCount([log_min, 'nfs', 'alert', sip, user, dept, kw,
                              int(overseas), device_id]).send_count()
            else:
                LogCount([log_min, 'nfs', 'audit', sip, user, dept, '-',
                          int(overseas), device_id]).send_count()


            pass

        return '\t'.join(res), overseas, ac_ret
