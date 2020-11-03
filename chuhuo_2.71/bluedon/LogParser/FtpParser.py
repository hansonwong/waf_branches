#!/usr/bin/env python
# coding=utf-8

import os
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
               'sAction', 'sPara', 'sFtpUserName', 'sFilename', 'sFileSize', 'sDeviceID']

append_keys = ['sAlertDetail', 'sAlertKeyword']

backquote_list = lambda x: ','.join(['`' + i + '`' for i in x])
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""
LOAD_SQL_GEN = lambda :load_sql % (backquote_list(common_keys))
LOAD_SQL_GEN_A = lambda : load_sql % (backquote_list(common_keys + append_keys))

FTP_ACT_LIST = {
    'LOGIN': (1002, u'FTP登陆'),
    'RETR': (1003, u'下载文件'),
    'STOR': (1004, u'上传文件'),
    'DELE': (1005, u'删除文件'),
    'MKD': (1007, u'创建目录'),
    'RMD': (1008, u'删除目录'),
    # 'CWD': (1000, u'切换目录'),
    # 'UNKNOW': (1000, u'未知动作'),
}


class FtpLogProcessor(LogProcessor):
    def __init__(self, _type='ftp_log', load_sql=LOAD_SQL_GEN()):
        # load_sql = LOAD_SQL_GEN()
        super(FtpLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)

FtpLog = FtpLogProcessor()
FtpOverseasLog = FtpLogProcessor('ftp_log_overseas')
FtpAlertLog = FtpLogProcessor(_type='alert_ftp_log', load_sql=LOAD_SQL_GEN_A())


class FtpParser(object):
    def __init__(self):
        super(FtpParser, self).__init__()
        self.template = get_report_template('ftp')

    def ftp_parser_line(self, line, user_detail=None, ac_search=None, rlist=None):
        try:
            det_ret = chardet.detect(line)
            code_set = det_ret.get('encoding')
            confidence = det_ret.get('confidence')

            # if code_set != 'utf-8' and confidence > 0.95:
            #     try:
            #         line_recode = line.decode(code_set).encode('UTF-8')
            #     except:
            #         line_recode = line.decode('GB2312').encode('UTF-8')
            # else:
            #     line_recode = line

            # log = json.loads(line)
            # log = json.loads(line_recode)

            # check code_set for different code
            possible_code_set = ['GB2312', 'GBK', 'UTF-8']
            if code_set != 'UTF-8' and confidence > 0.95:
                possible_code_set.insert(0, code_set)
            for cs in possible_code_set:
                try:
                    line_recode = line.decode(cs).encode('UTF-8')
                    log = json.loads(line_recode)
                    break
                except Exception as e:
                    ADLOG_ERR('ftp_parser:load json error in for[%s]' % e)
                    if cs == 'UTF-8': raise
                    else: continue
        except Exception as e:
            ADLOG_ERR('ftp_parser:load json errror[%s]' % e)
            ADLOG_ERR('ftp_parser:load json errror[%s, %s]' % (code_set, confidence))
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

        # ftp username
        ftpuser = log.get('User', '-')

        # scc and scc_flag
        scc ,scc_flag, overseas = get_scc(dip)

        action = log['Action']
        if action == 'CWD':
            return None, None, None
        para = log['Para']
        # try get file size if Para is a File Path
        try:
            filesize = str(os.path.getsize(para))
        except OSError:
            filesize = '0'

        fname = log.get('Display', para)
        device_id = log.get('device_id', '-')


        actid = FTP_ACT_LIST.get(action, (1000, u'未知动作'))[0]
        act = FTP_ACT_LIST.get(action, (1000, u'未知动作'))[1]
        UTC_now = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(log_time))
        report_items = {'time': UTC_now, 'actid': actid, 'act':act, 'user': user,
                       'sip': sip, 'smac': smac, 'sport': sport,
                       'dip': dip, 'dmac': dmac, 'dport': dport,
                       }
        if action in FTP_ACT_LIST and action != 'LOGIN':
        # if action in FTP_ACT_LIST and action != 'CWD':
            report_items['act_obj'] = para
        report_str = render_report_template(self.template, report_items)
        AuditLogReporter.report_msg(report_str)

        res = [app_name, str(log_time), smac, sip, sport, dmac, dip, dport, user, dept,
               scc, str(scc_flag),
               act, para, ftpuser, fname, filesize, device_id]

        # alter function
        ac_ret = None
        if ac_search is not None and rlist is not None:
            ret = {}
            _all_keywords = []
            if actid == (1000, 1002):
                # unknow and login is ignore
                pass
            elif actid in (1002, 1004, 1005):
                # file name and content
                ret['filename'] = ac_search(log, 0, AcEngine.TYPE_FILE_NAME,
                                            fname, sip, rlist)
                _all_keywords.extend(ret['filename'])
                ret['file_content'] = ac_search(log, 0, AcEngine.TYPE_FILE_CONTENT,
                                             para, sip, rlist)
                _all_keywords.extend(ret['file_content'])
                pass

            elif actid in (1007, 1008):
                # file name only
                ret['filename'] = ac_search(log, 0, AcEngine.TYPE_FILE_NAME,
                                            para, sip, rlist)
                _all_keywords.extend(ret['filename'])
                pass
            else:
                # undefined action, do nothing
                pass

            if _all_keywords:
                _js = json.dumps(ret, encoding="UTF-8", ensure_ascii=False)
                ac_ret = '\t'.join(res) + '\t' + _js + '\t' + '#' + '#'.join(_all_keywords)
                # print 'FTP Alert log result:'
                # print ac_ret
                for kw in _all_keywords:
                    LogCount([log_min, 'ftp_log', 'alert', sip, user, dept, kw,
                              int(overseas), device_id]).send_count()
            else:
                LogCount([log_min, 'ftp_log', 'audit', sip, user, dept, '-',
                          int(overseas), device_id]).send_count()


            pass

        return '\t'.join(res), overseas, ac_ret
