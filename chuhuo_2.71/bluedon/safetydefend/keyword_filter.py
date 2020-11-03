#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import codecs
from utils.log_logger import rLog_dbg
from db.config import search_data as select

CONFIG_PATH = '/etc/suricata/conf/key.txt'
FILTER_LOG = lambda x: rLog_dbg('filter', x)


def keyword_filter():
    """
    安全防护->信息泄露防护->关键字过滤->上传关键字过滤
    """
    lines = []
    sql = 'SELECT sHttp, sFtp, iLog FROM m_tbKeywordFilter WHERE iType=2 AND iStatus=1;'
    keywrods_data = select(sql)
    for i in keywrods_data:
        http_keys = re.split(ur'\s+|;|\uff1b', i['sHttp'])
        FILTER_LOG('HTTP KEYWORD is %s' % i['sHttp'])
        ftp_keys = re.split(ur'\s+|;|\uff1b', i['sFtp'])
        FILTER_LOG('FTP KEYWORD is %s' % i['sFtp'])
        for http in http_keys:
            http = http.strip()
            if not http:
                continue
            line = 'htpkey:%s;log:%s;\n' % (http, i['iLog'] or 0)
            FILTER_LOG('HTTP LINE: %s' % line)
            lines.append(line)
        for ftp in ftp_keys:
            ftp = ftp.strip()
            if not ftp:
                continue
            line = 'ftpkey:%s;log:%s;\n' % (ftp, i['iLog'] or 0)
            FILTER_LOG('FTP LINE: %s' % line)
            lines.append(line)
    with codecs.open(CONFIG_PATH, 'w', 'utf-8') as f:
        f.write(''.join(lines))


if __name__ == '__main__':
    keyword_filter()
