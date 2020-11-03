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
from adutils.http_url_category import HTTPCategory

common_keys = ['sAppProto', 'iDate', 'sSrcMac', 'sSrcIP', 'iSrcPort',
               'sDstMac', 'sDstIP', 'iDstPort', 'sType', 'sSiteName',
               'sHost', 'sUri', 'sMethod', 'sField', 'sUser', 'sDept',
               'sScc', 'sSccFlag', 'sDeviceID']
# Keys of Mysql tables
type_keys = {
    'bbs' : ['sUsername', 'sPassword', 'sSubject', 'sContent'],
    'blog' : ['sUsername', 'sSubject', 'sContent'],
    'netstore' : ['sUsername', 'sFilename', 'sAttachFilename'],
    'search' : ['sKeyword'],
    'shopping' : ['sTitle'],
    'video' : ['sTitle', 'sVideo_name'],
    'webmail' : ['sFrom', 'sTo', 'sChao', 'sMi', 'sSubject', 'sContent',
                 'sAttachFilename'],
    'weibo'  : ['sUsername', 'sContent'],
    'url_log': ['sURL', 'sTitle', 'sCategory']
}

# Keys of logs
fields_keys = {
    'bbs' : ['username', 'password', 'subject', 'content'],
    'blog' : ['username', 'subject', 'content'],
    'netstore' : ['username', 'filename'],
    'search' : ['kw'],
    'shopping' : ['title'],
    'video' : ['title', 'video_name'],
    'webmail' : ['from', 'to', 'chao', 'mi', 'subject', 'content'],
    'weibo'  : ['username', 'content'],
    # 'url_log': []
}

append_keys = ['sAlertDetail', 'sAlertKeyword']

keys_len = {}

AC_TITLE = AcEngine.TYPE_TITLE
AC_CONTENT = AcEngine.TYPE_CONTENT
AC_FILENAME = AcEngine.TYPE_FILE_NAME
AC_FILE_CONTENT = AcEngine.TYPE_FILE_CONTENT
#alert type
alert_type = {
    'bbs' : {'subject': AC_TITLE, 'content': AC_CONTENT, 'username': AC_TITLE},
    'blog' : {'username': AC_TITLE, 'subject': AC_TITLE, 'content': AC_CONTENT},
    'netstore' : {'filename': AC_FILENAME, 'username': AC_TITLE},
    'search' : {'kw': AC_CONTENT},
    'shopping' : {'title': AC_TITLE},
    'video' : {'title':AC_TITLE, 'video_name': AC_CONTENT},
    'webmail' : {'subject': AC_TITLE, 'content': AC_CONTENT},
    'weibo'  : {'content': AC_CONTENT},
}


# return sql keys of different http application types
sql_keys = lambda x : ','.join(common_keys.extend(type_keys[x]))
# backquote
backquote_list = lambda x : ','.join(['`' + i + '`' for i in x])
# sql statement for different kind of http logs
load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
                fields terminated by '\t' lines terminated by '\n'
                (%s);"""

LOAD_SQL_GEN = lambda x : load_sql % (backquote_list(common_keys + type_keys[x]))
LOAD_SQL_GEN_A = lambda x : load_sql % (backquote_list(common_keys + type_keys[x] + append_keys))

_LEN = lambda x, y=1024 : x if len(x) < y else x[:y]


class HttpParser(object):
    def __init__(self):
        super(HttpParser, self).__init__()
        self.template = get_report_template('web')
        self.category = HTTPCategory()


    def fields_to_dict(self,f_list):
        res = {}
        for f in f_list:
            if f['Name'] == 'subject':
                res['subject'] = _LEN(f['Value'], 255)
            elif f['Name'] == 'content':
                res['content'] = _LEN(f['Value'], 5120)
            elif f['Name'] == 'kw':
                res['kw'] = _LEN(f['Value'], 64)
            elif f['Name'] == 'title':
                res['title'] = _LEN(f['Value'], 64)
            elif f['Name'] == 'username':
                res['username'] = _LEN(f['Value'], 128)
            elif f['Name'] == 'video_name':
                res['video_name'] = _LEN(f['Value'], 64)
            elif f['Name'] == 'filename':
                res['filename'] = _LEN(f['Value'], 512)

                pass
            else:
                res[f['Name']] = f['Value']
        return res


    # return fields of lst parameter
    def common_process(self, typ, lst):
        res = []
        # if lst is null, return a list fill with '-'(process for ssl)
        if len(lst) == 0:
            res = [ '-' for _ in fields_keys[typ] ]
            return res, {}

        f_dict = self.fields_to_dict(lst)

        # for Webmail address, remove <string> and </string>
        if typ== 'webmail':
            # ADLOG_DEBUG('Get WebMail message')
            # print('Get WebMail message')
            for item in f_dict:
                # search every address
                if item in ('from', 'to', 'chao', 'mi'):
                    if not f_dict[item]:
                        continue
                    _addrs = f_dict[item].strip()
                    _addrs = _addrs.replace('&lt;', '<').replace('&gt;', '>')
                    _addrs = _addrs.replace('<string>', '')
                    _addrs = _addrs.replace('</string>', ';')
                    f_dict[item] = _addrs.strip(';')

        for _key in fields_keys[typ]:
            res.append(f_dict.get(_key, '-'))


        return res, f_dict


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
            ADLOG_ERR('http_log_parser: load json try correct[%s]' % e)
            ADLOG_ERR(chardet.detect(line))
            ADLOG_ERR(line)

            return None, None, None, None

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
        http_type = log['Type']
        if http_type == 'httpurl':http_type = 'url_log'

        # site name
        # site_name = log['SiteName']
        site_name = log.get('SiteName', '-')

        # host
        host = log.get('Host', '-')

        # Uri
        uri = log.get('Uri', '-')

        # method
        method = log.get('Method', '-')

        # Fields
        # fields = log['Fields']
        fields = log.get('Fields', {})

        # process fields
        if http_type == 'url_log':
            host_category = self.category.get_host_category(host)
            # print host_category
            if app_name == 'SSL': # just for ssl
                f_list = ['-', site_name, host_category]
                f_dict = {}
            else:
                _url = 'http://{h}/{u}'.format(h=host, u=uri.lstrip('/'))
                _http_title = log.get('Title')
                f_list = [_url, _http_title, host_category]
                f_dict = dict(url=_url, title=_http_title)
                # f_dict['title'] = _http_title
        elif http_type in type_keys and http_type in fields_keys:
            f_list, f_dict = self.common_process(http_type, fields)


        else:
            f_list = []
            f_dict = {}


        device_id = log.get('device_id', '-')

        res = [app_name, str(log_time), smac, sip, sport, dmac, dip, dport, http_type,
               site_name, host, uri, method, str('-'), user, dept, scc, str(scc_flag),
               device_id]

        if f_list:res += f_list

        UTC_now = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(log_time))
        report_items = {'time': UTC_now, 'url': uri,
                       'sip': sip, 'smac': smac, 'sport': sport,
                       'dip': dip, 'dmac': dmac, 'dport': dport,
                       }
        report_str = render_report_template(self.template, report_items)
        AuditLogReporter.report_msg(report_str)
        # print report_str

        ac_ret = None
        # get alert type of specified fields
        if http_type == 'url_log':
            _alert_type = dict(url = AcEngine.TYPE_TITLE)
            _alert_type['title'] = AcEngine.TYPE_TITLE
        else:
            _alert_type = alert_type.get(http_type, {})


        # if ac_engine is exists
        if ac_search is not None and rlist is not None:
            ret = {}
            _all_keywords = []
            # if field keys are specified in _alert_type
            for key in f_dict:
                if key not in _alert_type:
                    continue

                # search the value of f_dict
                ret[key] = ac_search(log, 0, _alert_type[key],
                                     f_dict[key], sip, rlist)
                _all_keywords.extend(ret[key])

            # attr for webmail
            if http_type == 'webmail' or http_type == 'netstore':
                _attrs = log.get('Atts', None)
                _d_attr_files = {}
                _file_content_match = []
                _file_name_match = []

                if _attrs is not None and len(_attrs) > 0:

                    # ADLOG_DEBUG('attach:%s' % _attrs)
                    for _attr in _attrs:

                        # get filename
                        _attr_filename = _attr.get('filename', None)
                        _attr_filepath = _attr.get('storepath', '')
                        if _attr['filename'] is None or not os.path.exists(_attr_filepath):
                            continue

                        _attr_filesize = os.path.getsize(_attr_filepath)

                        # _d_attr_files[_attr['filename']] = _attr['storepath']
                        # _d_attr_files[_attr['storepath']] = _attr['filename']
                        _d_attr_files[_attr_filepath] = {'filename': _attr_filename,
                                                         'size': _attr_filesize}
                        # search attach file content
                        _file_name_match.extend(ac_search(log, 0, AcEngine.TYPE_FILE_NAME,
                                                             _attr['filename'], sip, rlist))
                        _file_content_match.extend(ac_search(log, 0, AcEngine.TYPE_FILE_CONTENT,
                                                             _attr['storepath'], sip, rlist))

                    # ADLOG_DEBUG('attach:%s' % _d_attr_files)

                    # save search result
                    ret['filename'] = _file_name_match
                    _all_keywords.extend(ret['filename'])
                    ret['file_content'] = _file_content_match
                    _all_keywords.extend(ret['file_content'])

                    _js_attr = json.dumps(_d_attr_files, encoding="UTF-8", ensure_ascii=False)
                else:
                    # if nothing in Atts
                    _js_attr = 'none'

                res.append(_js_attr)


            if _all_keywords:
                # print ret
                # print res
                _js = json.dumps(ret, encoding="UTF-8", ensure_ascii=False)
                ac_ret = '\t'.join(res) + '\t' + _js+ '\t' + '#' + '#'.join(_all_keywords)

                # print 'HttpAlertLog for %s ' % http_type
                # print '\t'.join(res)
                for kw in _all_keywords:
                    LogCount([log_min, 'http_' + http_type, 'alert', sip, user,
                              dept, kw, int(overseas), device_id]).send_count()
            else:
                LogCount([log_min, 'http_' + http_type, 'audit', sip, user, dept,
                          '-', int(overseas), device_id]).send_count()

        if http_type == 'webmail':
            # print 'HttpAlertLog for %s ' % http_type
            # print _attrs
            # print ac_ret
            # print '\t'.join(res)
            # ADLOG_DEBUG('attach:%s' % log)
            ADLOG_DEBUG('log++++++++++++++++++++++++++++++++++++++:\n%s' % log)
            ADLOG_DEBUG('res--------------------------------------:\n%s' % res)

        return '\t'.join(res), http_type, overseas, ac_ret
        pass


class HttpLogProcessor(LogProcessor):
    # !!!_type is in type_keys.keys()!!!
    # ['bbs','blog','netstore','search','shopping','video','webmail']
    def __init__(self, _typ, load_sql):
        _type = 'http_{}'.format(_typ)
        super(HttpLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)

class HttpAlertLogProcessor(LogProcessor):
    # !!!_type is in type_keys.keys()!!!
    # ['bbs','blog','netstore','search','shopping','video','webmail']
    def __init__(self, _typ, load_sql):
        _type = 'alert_http_{}'.format(_typ)
        super(HttpAlertLogProcessor, self).__init__(TYPE=_type, LOAD=load_sql)

# http url log
HttpUrlLog = HttpLogProcessor('url_log', LOAD_SQL_GEN('url_log'))
HttpUrlOverseasLog = HttpLogProcessor('url_log_overseas', LOAD_SQL_GEN('url_log'))
HttpUrlAlertLog = HttpAlertLogProcessor('url_log', LOAD_SQL_GEN_A('url_log'))

# search log
# search_sql = load_sql % (backquote_list(common_keys + type_keys['search']))
# HttpSearchLog = HttpLogProcessor('search', search_sql)
HttpSearchLog = HttpLogProcessor('search', LOAD_SQL_GEN('search'))
HttpSearchOverseasLog = HttpLogProcessor('search_overseas', LOAD_SQL_GEN('search'))
HttpSearchAlertLog = HttpAlertLogProcessor('search', LOAD_SQL_GEN_A('search'))

#webmail log
# webmail_sql = load_sql % (backquote_list(common_keys + type_keys['webmail']))
# HttpWebMailLog = HttpLogProcessor('webmail', webmail_sql)
HttpWebMailLog = HttpLogProcessor('webmail', LOAD_SQL_GEN('webmail'))
HttpWebMailOverseasLog = HttpLogProcessor('webmail_overseas', LOAD_SQL_GEN('webmail'))
HttpWebMailAlertLog = HttpAlertLogProcessor('webmail', LOAD_SQL_GEN_A('webmail'))

#bbs log
# bbs_sql = load_sql % (backquote_list(common_keys + type_keys['bbs']))
# HttpBBSLog = HttpLogProcessor('bbs', bbs_sql)
HttpBBSLog = HttpLogProcessor('bbs', LOAD_SQL_GEN('bbs'))
HttpBBSOverseasLog = HttpLogProcessor('bbs_overseas', LOAD_SQL_GEN('bbs'))
HttpBBSAlertLog = HttpAlertLogProcessor('bbs', LOAD_SQL_GEN_A('bbs'))

#blog log
# blog_sql = load_sql % (backquote_list(common_keys + type_keys['blog']))
# HttpBlogLog = HttpLogProcessor('blog', blog_sql)
HttpBlogLog = HttpLogProcessor('blog', LOAD_SQL_GEN('blog'))
HttpBlogOverseasLog = HttpLogProcessor('blog_overseas', LOAD_SQL_GEN('blog'))
HttpBlogAlertLog = HttpAlertLogProcessor('blog', LOAD_SQL_GEN_A('blog'))

#netstore log
# netstore_sql = load_sql % (backquote_list(common_keys + type_keys['netstore']))
# HttpNetStoreLog = HttpLogProcessor('netstore', netstore_sql)
HttpNetStoreLog = HttpLogProcessor('netstore', LOAD_SQL_GEN('netstore'))
HttpNetStoreOverseasLog = HttpLogProcessor('netstore_overseas', LOAD_SQL_GEN('netstore'))
HttpNetStoreAlertLog = HttpAlertLogProcessor('netstore', LOAD_SQL_GEN_A('netstore'))

#shopping log
# shopping_sql = load_sql % (backquote_list(common_keys + type_keys['shopping']))
# HttpShoppingLog = HttpLogProcessor('shopping', shopping_sql)
HttpShoppingLog = HttpLogProcessor('shopping', LOAD_SQL_GEN('shopping'))
HttpShoppingOverseasLog = HttpLogProcessor('shopping_overseas', LOAD_SQL_GEN('shopping'))
HttpShoppingAlertLog = HttpAlertLogProcessor('shopping', LOAD_SQL_GEN_A('shopping'))

#video log
# video_sql = load_sql % (backquote_list(common_keys + type_keys['video']))
# HttpVideoLog = HttpLogProcessor('video', video_sql)
HttpVideoLog = HttpLogProcessor('video', LOAD_SQL_GEN('video'))
HttpVideoOverseasLog = HttpLogProcessor('video_overseas', LOAD_SQL_GEN('video'))
HttpVideoAlertLog = HttpAlertLogProcessor('video', LOAD_SQL_GEN_A('video'))

#weibo log
# weibo_sql = load_sql % (backquote_list(common_keys + type_keys['weibo']))
# HttpWeiboLog = HttpLogProcessor('weibo', weibo_sql)
HttpWeiboLog = HttpLogProcessor('weibo', LOAD_SQL_GEN('weibo'))
HttpWeiboOverseasLog = HttpLogProcessor('weibo_overseas', LOAD_SQL_GEN('weibo'))
HttpWeiboAlertLog = HttpAlertLogProcessor('weibo', LOAD_SQL_GEN_A('weibo'))

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
