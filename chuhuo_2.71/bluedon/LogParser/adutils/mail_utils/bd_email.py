#!/usr/bin/python
# -*- coding: utf8-*-


import os
import sys
import time
import json
import string
import getopt
import MySQLdb
import pexpect
import smtplib_fix as smtplib
import traceback
import email
from email.Header import Header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from adutils.config import fetchone_sql as fetch3306
from adutils.audit_logger import rLog_dbg, rLog_err


MAIL_LOG = 'audit_send_mail'
DBG = lambda x: rLog_dbg(MAIL_LOG, x)
ERR = lambda x: rLog_err(MAIL_LOG, x)

DB = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'passwd': 'bd_123456',
        'db': 'db_firewall',
        'charset': 'utf8',
        #'use_unicode':False,
        'cursorclass': MySQLdb.cursors.DictCursor,
        'unix_socket': '/tmp/mysql3306.sock'
        }

"""
    body template
    body = "你好，\r\n"
    body += "\t蓝盾账号集中管理与审计系统的磁盘状态为：\r\n"
    body += "\t总空间  ：" + str(decimal.Decimal((decimal.Decimal(capacity) / 1024 / 1024 / 1024)).quantize(decimal.Decimal('0.01'))) + " G\r\n"
    body += "\t可用空间：" + str(decimal.Decimal((decimal.Decimal(available) / 1024 / 1024 / 1024)).quantize(decimal.Decimal('0.01'))) + " G\r\n"
    body += "\t已用空间：" + str( decimal.Decimal(per * 100).quantize(decimal.Decimal('0.01')) ) + " %\r\n"
    body += "\t当前的" + tips + "，为了系统的正常使用，请及时删除过旧的日志或增加磁盘空间。\r\n"
    body += "\r\n"
    body += "\r\n"
    body += "\t\t\t\t蓝盾信息安全技术股份有限公司\r\n"
    nowdate = time.strftime( '%Y-%m-%d', time.localtime() )
    body += "\t\t\t\t" + nowdate
    print body.decode('gb2312').encode('utf8')) )
"""

def get_mail_config():
    sql = "SELECT sValue FROM m_tbconfig WHERE sCommand='CMD_LOG_ALERT';"
    ret = fetch3306(sql)
    ret = json.loads(ret.get('sValue', '{}'))
    fr = ret.get('send_address')
    to = ret.get('receive_address')
    smtp_srv = ret.get('smtp_address')
    passwd = ret.get('password')
    enable_mail = ret.get('gateway_mail', 'off')
    DBG(ret)
    return fr, to, smtp_srv, passwd, enable_mail

def send(data) :
    if data == None : return;
    dbconn = None;
    dbcur = None;
    send_ret = 1

    try :
        dbconn  = MySQLdb.connect(**DB);
        dbcur   = dbconn.cursor();

        fr, to, smtpsrv, smtppwd, enable_mail = get_mail_config()
        if enable_mail != 'on':
            DBG('enable_mail = False')
            return 0
        msg = MIMEMultipart()

        body = ""
        # 构造消息内容
        if data.get('subtype') == None :
            body = email.MIMEText.MIMEText(data['body'], _subtype='plain',_charset='utf-8')
        else:
            body = email.MIMEText.MIMEText(data['body'], _subtype='html',_charset='utf-8')

        msg.attach(body);

        nowdate = time.strftime( '%Y-%m-%d', time.localtime() )

        try :
            #加邮件头
            msg['to'] = to
            msg['from'] = fr
            msg['subject'] = Header("%s[%s]" % (data['subject'], nowdate), 'utf-8')
            msg['body'] = data['body']
            smtpusr = fr
            server = smtplib.SMTP()
            # server.set_debuglevel(1)
            server.connect(smtpsrv, 25)
            server.login(smtpusr, smtppwd)
            server.sendmail(msg['from'], msg['to'], msg.as_string())
            server.close

            send_ret = 0
        except Exception, e :
            print e
            print traceback.format_exc()
    finally :
        if dbcur : dbcur.close();
        if dbconn : dbconn.close();
    return send_ret


if __name__ == '__main__':
    data = {
            'subject': '测试邮件来自蓝盾',
            'body': '测试邮件来自蓝盾\n测试邮件来自蓝盾'
            }
    # get_mail_config()
    send(data)
    pass
