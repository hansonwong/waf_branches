#!/usr/bin/python
#-*- coding:utf-8 -*-

import sys
import os

import re
import logging
import json
from netaddr import *
from LogProcessor import LogProcessor
from LogCounter import LogCount, LOG_COUNT_MIN
from adutils.AcEngine import AcEngine
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR
from adutils.audit_utils import timestr_to_timestamp, geo_info_item, get_scc


reload(sys)
sys.setdefaultencoding('utf-8')

LOG_TYPE_NAME = 'email_log'

ATT_PATH = '/home/cyren/checkfile/'
CONTENT_PATH = '/var/log/suricata/content/'

common_keys = ['sAppProto', 'iDate', 'sSrcMac', 'sSrcIP', 'iSrcPort',
               'sDstMac', 'sDstIP', 'iDstPort', 'sUser', 'sDept']


email_keys = ["iVlanId", "sScc", "sSccFlag", "sSender", "sSendTo", "sSendBb",
              "sSendCc", "sSubject", "sContentPath", "sAttCount", "sAttachFilename",
              "sAttachFilesize", "sAttachFilenamePath", "sAppName","sMatchInfo",
              "iOverseas"]

append_keys = ['sAlertDetail', 'sAlertKeyword']



FSIZE = lambda x: os.path.getsize(x)
PATH_ATT = lambda x : os.path.join(ATT_PATH, x)

# backquote
backquote_list = lambda x : ','.join(['`' + i + '`' for i in x])
# sql statement for different kind of http logs
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""

LOAD_SQL_GEN = lambda : load_sql % (backquote_list(common_keys + email_keys))
LOAD_SQL_GEN_A = lambda : load_sql % (backquote_list(common_keys + email_keys + append_keys))

_LEN = lambda x, y=1024 : x if len(x) < y else x[:y]


class EmailLogProcessor(LogProcessor):
    def __init__(self, _type='email_log', load_sql=LOAD_SQL_GEN()):
        super(EmailLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)

# email log parser
EmailLog = EmailLogProcessor()
EmailOverseasLog = EmailLogProcessor(_type='email_log_overseas')
EmailAlertLog = EmailLogProcessor(_type='alert_email_log', load_sql=LOAD_SQL_GEN_A())

def email_log_parser(line, user_detail=None, ac_search=None, rlist=None):

    try:
        line = re.sub(r'[\x01-\x1f]','', line)
        log = json.loads(line, strict=False)
    except Exception as e:
        ADLOG_ERR('email_log_parser: load json error[%s]' % e)
        ADLOG_ERR(line)
        return None, None, None

    # app type
    app_name = log['AppProto']
    # vlan_id
    vlan_id = 0
    vlan_id = str(vlan_id)

    # time
    log_time = timestr_to_timestamp(log['Date'])
    log_min = log_time - (log_time % LOG_COUNT_MIN)
    log_time = str(log_time)

    # source mac
    smac = log['SrcMac']

    # source ip
    sip = log['SrcIP']
    # sip_s = int_to_ip(int(sip))
    # sip = str(sip)

    # source port
    sport = str(log['SrcPort'])

    # destination mac
    dmac = log['DstMac']

    # destination ip
    dip = log['DstIP']

    # destination port
    dport = str(log['DstPort'])


    # dept and user
    if user_detail is not None and sip in user_detail:
        # user= user_detail[sip][0]
        # dept = user_detail[sip][1]
        user, dept = user_detail[sip]
    else:
        user = 'Anonymous'
        dept = 'Anonymous'

    #scc and scc_flag
    # geo = geo_info_item()
    # geo.get_geoinfo(dip)
    # geo_info = [
    #     info for info in
    #     [geo.continent, geo.country, geo.city, geo.subdivisions]
    #     if info
    # ]
    # scc = '|'.join(geo_info) if geo_info else 'local'
    # scc_flag = str(geo.scc_flag) if scc != 'local' else '5'
    # overseas = '1' if scc_flag == '0' else '0'

    scc, scc_flag, overseas = get_scc(dip)


    def _get_mail_addr_list(l):
        addrs_d = {}
        for addr in  l.split(','):
            addr = addr.strip()
            if not addr:
                continue
            if addr.startswith('<') and addr.endswith('>'):
                addrs_d[addr[1:-1]] = ''
            elif addr.endswith('>'):
                try:
                    # _ad = addr.split('<')
                    # addrs_d[_ad[1][0:-1]] = _ad[0].strip("'")

                    addr_reverse = addr[::-1]
                    lt_i = addr_reverse.find('<')
                    # addrs_d[addr[:-lt_i - 1]] = addr[-lt_i:]
                    addrs_d[addr[-lt_i:-1]] = addr[:-lt_i - 1]
                except KeyError:
                    ADLOG_ERR('KeyError: %s is not an email address' % addr)
                except IndexError:
                    ADLOG_ERR('IndexError: %s is not an email address' % addr)
            elif '@' in addr:
                for symbol in ('@', '"', "'"):
                    _a = addr.split(symbol)
                    if '@' in _a[-1]:
                        addrs_d[_a[-1]] = ' '.join(_a[:-1])
                        break
                print 'get addr[%s] by symbol[%s]'  % (_a[-1], symbol)
                pass
        return addrs_d



    # sender
    # sender = _get_mail_addr_list(items[8])[0]
    try:
        sender = _get_mail_addr_list(log['MailFrom']).keys()[0]
    except KeyError:
        ADLOG_ERR('KeyError: %s is not an email address' % log['MailFrom'])
        sender = ''
    except IndexError:
        ADLOG_ERR('IndexError: %s is not an email address' % log['MailFrom'])
        sender = ''

    # send_to
    send_to = _get_mail_addr_list(log['MailTo']).keys() or ['-']

    # send_bb
    send_bb = _get_mail_addr_list(log['MailBcc']).keys() or ['-']

    # send_cc
    send_cc = _get_mail_addr_list(log['MailCc']).keys() or ['-']

    # subject
    subject = log['MailSubject'] or '-'

    # content_path
    mail_content = log['MailContent'] or ''
    mail_content_path = log.get('MailContentPath') or CONTENT_PATH
    content_path = os.path.join(mail_content_path, mail_content)

    att_files = log['MailAttach'].split(',')
    att_path = log.get('MailContentPath') or ATT_PATH

    # if len(att_files) == 0:
    #     _d_att = {}
    #     _s_att = 'none'
    # if len(att_files) == 1 and att_files[0] == '':
    #     _d_att = {}
    #     _s_att = 'none'
    # else:
    #     _d_att = dict()
    #     for f in att_files:
    #         fpath = os.path.join(att_path, f)
    #         if not os.path.exists(fpath):
    #             continue
    #         fsize = os.path.getsize(fpath)
    #         _d_att[fpath] = {'filename': f, 'size': fsize}
    #     # path: filename
    #     _s_att = json.dumps(_d_att, encoding="UTF-8", ensure_ascii=False)

    # dict { attach_file_path: {'filename': attach_file_name, 'size':attach_file_size} }
    _d_att = dict()
    # list [attach_file_name1, attach_file_name2,...]
    _ac_att_names = list()
    for f in att_files:
        # if f is '', continue
        if not f: continue
        # check if attach_file_path is exists
        fpath = os.path.join(att_path, f)
        if not os.path.exists(fpath):
            continue
        # get attach_file_size if exists
        fsize = os.path.getsize(fpath)
        # keep filename and size in dict
        _d_att[fpath] = {'filename': f, 'size': fsize}
        # keep filename in list
        _ac_att_names.append(f)

    # transfer to json, and _s_att will be stored in database
    _s_att = json.dumps(_d_att, encoding="UTF-8", ensure_ascii=False) if _d_att else 'none'

    # record in table http_webmail, set this values for http_webmail table
    sitename = '-'
    typ = 'email'
    host = '-'
    uri = '-'
    method = '-'
    field = '-'
    device_id = log.get('device_id', '-')
    res = [app_name, log_time, smac, sip, sport, dmac, dip, dport,
           typ, sitename, host, uri, method, field, user, dept, scc, scc_flag,device_id,
           sender, _LEN(';'.join(send_to), 255), _LEN(';'.join(send_cc), 255),
           _LEN(';'.join(send_bb), 255),_LEN(subject, 255), content_path, _s_att,
    ]

    audit_ret = '\t'.join(res)
    ac_ret = None
    if ac_search is not None and rlist is not None:
        matchtype = 0
        ret = {}
        _all_keywords = []
        _concat = lambda x : ';'.join(x)
        # alert function
        # subject
        ret['title'] = ac_search(log, 0, AcEngine.TYPE_TITLE, subject, sip, rlist)
        _all_keywords.extend(ret['title'])
        # content
        ret['content'] = ac_search(log, 0, AcEngine.TYPE_FILE_CONTENT,
                         content_path, sip, rlist)
        _all_keywords.extend(ret['content'])
        # attach file names
        ret['filename']= ac_search(log, 0, AcEngine.TYPE_FILE_NAME,
                             ';'.join(_ac_att_names), sip, rlist)
        _all_keywords.extend(ret['filename'])
        # attach file content
        _tmp_match = []

        for _path in _d_att.keys():
            _tmp_match.extend(ac_search(log, 0, AcEngine.TYPE_FILE_CONTENT,
                                 _path, sip, rlist))
        ret['file_content'] = _tmp_match
        _all_keywords.extend(ret['file_content'])

        # if ret['title']:
        #     matchtype += 1
        # if ret['content']:
        #     matchtype += 2
        # if ret['filename']:
        #     matchtype += 4
        # if ret['file_content']:
        #     matchtype += 8
        # print 'EmailParser: mail search result\n %s' % ret


        if _all_keywords:
            # match
            _js = json.dumps(ret, encoding="UTF-8", ensure_ascii=False)
            # print _js
            ac_ret = '\t'.join(res) + '\t' + _js + '\t' + '#' + '#'.join(_all_keywords)

        # print ac_ret
            for kw in _all_keywords:
                LogCount([log_min, 'email_log', 'alert', sip, user, dept, kw,
                          int(overseas), device_id]).send_count()
        else:
            LogCount([log_min, 'email_log', 'audit', sip, user, dept, '-',
                      int(overseas), device_id]).send_count()



        pass

    # print '\n'.join(res)
    return audit_ret, overseas, ac_ret
