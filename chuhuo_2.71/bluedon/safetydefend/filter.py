#! /usr/bin/env python
# -*- coding:utf-8 -*-

import codecs
import os
import re
import sys
from db.mysqlconnect import mysql_connect_dict
from system.system_config import anti_virus_fast_scan
from utils.log_logger import rLog_dbg
reload(sys)
sys.setdefaultencoding('utf-8')

FILTER_LOG = lambda x: rLog_dbg('filter', x)
SUBJECT_CONFIG = '/etc/suricata/conf/subject.rules'
CONTENT_CONFIG = '/etc/suricata/conf/content.rules'
ATTACHMENT_CONFIG = '/etc/suricata/conf/filename.rules'
RECEIVE_CONFIG = '/etc/suricata/conf/receive.rules'
SEND_CONFIG = '/etc/suricata/conf/send.rules'


def write_config(fd, text, is_log=0):
    if text:
        lines = re.split(u'[;；，,\s]\s*', text)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            fd.write("%s:%s\n" % (line, is_log))


def eml_key():
    cur = mysql_connect_dict()
    sql = "select sTitle,sText,sFile,iLog,sSenderUser,sReceiveUser from m_tbKeywordFilter where iStatus=1 and iType=1"
    cur.execute(sql)
    results = cur.fetchall()
    f_subject = codecs.open(SUBJECT_CONFIG, 'w', 'utf-8')
    f_content = codecs.open(CONTENT_CONFIG, 'w', 'utf-8')
    f_attachment = codecs.open(ATTACHMENT_CONFIG, 'w', 'utf-8')
    f_receive = codecs.open(RECEIVE_CONFIG, 'w', 'utf-8')
    f_send = codecs.open(SEND_CONFIG, 'w', 'utf-8')
    for result in results:
        write_config(f_subject, result['sTitle'], result['iLog'])
        write_config(f_content, result['sText'], result['iLog'])
        write_config(f_attachment, result['sFile'], result['iLog'])
        write_config(f_send, result['sSenderUser'], result['iLog'])
        write_config(f_receive, result['sReceiveUser'], result['iLog'])
    f_subject.close()
    f_content.close()
    f_attachment.close()
    f_receive.close()
    f_send.close()
    if os.path.exists('/var/run/suricata.pid'):
        fpid = open('/var/run/suricata.pid', 'r')
        pid = fpid.read().strip('\n')
        fpid.close()
        os.system('kill -10 %s' % pid)
    cur.close()


def virus():
    cur = mysql_connect_dict()
    sql = 'select sValue from m_tbconfig where sName="EvilProtectedSet"'
    cur.execute(sql)
    result = cur.fetchall()
    if len(result):
        result = result[0]
    else:
        return
    f_type = codecs.open('/etc/suricata/conf/filetype.rules', 'w', 'utf-8')
    f_fsize = codecs.open('/etc/suricata/conf/filesize.rules', 'w', 'utf-8')
    f_fzip = codecs.open('/etc/suricata/conf/filezip.rules', 'w', 'utf-8')
    for i in eval(result['sValue'])['sFileType']:
        sql_type = "select sFileExt from m_tbfiletypegroup where id ='%s'" % i
        cur.execute(sql_type)
        ty = cur.fetchall()
        if ty:
            ty = ty[0]['sFileExt'].split(',')
            if ty[0] == '*':
                f_type.write('none' + '\n')
            else:
                for filetype in ty:
                    filetype = filetype.strip('*')
                    print filetype
                    f_type.write(filetype + '\n')
    f_fsize.write(eval(result['sValue'])['iMaxFileSize'] + '\n')
    f_fzip.write(eval(result['sValue'])['iMaxDecompressionLever'] + '\n')
    f_type.close()
    f_fsize.close()
    f_fzip.close()
    cur.close()

    # 开启快速扫描
    fast_scan = eval(result['sValue']).get('iFastScan', '0')
    anti_virus_fast_scan(str(fast_scan))

if __name__ == "__main__":
    eml_key()
    virus()
