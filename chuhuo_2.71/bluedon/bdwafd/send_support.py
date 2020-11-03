#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import Encoders
from db import conn_scope
from config import config

sender = 'wafsupport@chinabluedon.cn'
mailto = 'wafsupport@chinabluedon.cn'
# imgfiles = '/usr/local/bluedon/www/downloads/sysinfo.data'
imgfiles = '/Data/apps/wwwroot/waf/download/web/cache/sysinfo.data'


def send_support_mail(args=None):
    '''
    发送技术支持邮件
    '''
    os.system('/usr/local/bluedon/bdwafd/sysinfo_collect_encrypt.sh')
    msg = MIMEMultipart()
    msg['Subject'] = u'蓝盾技术支持邮件'
    msg['To'] = u'蓝盾WAF技术支持'
    msg['From'] = 'test'

    with conn_scope(**config['db']) as (_, cursor):
        cursor.execute("SELECT * FROM t_devinfo,t_license")
        devinfo = cursor.fetchone()
    content = '''设备型号：%s <br> 系统版本：%s <br> 规则版本：%s <br>
                 序列号：%s <br> 机器码：%s''' % (devinfo[0],
                 devinfo[1], devinfo[2], devinfo[3], devinfo[4])
    Contents = MIMEText(content, 'html', _charset='utf-8')
    msg.attach(Contents)

    att = MIMEBase('application', "octet-stream")
    fp = open(imgfiles, 'rb')
    att.set_payload(fp.read())
    fp.close()
    Encoders.encode_base64(att)
    att.add_header('content-disposition', 'attachment', filename='sysinfo.data')
    msg.attach(att)

    smtp = smtplib.SMTP('smtp.chinabluedon.cn')
    smtp.login('wafsupport', 'bluedonwaf')

    smtp.sendmail(sender, mailto, msg.as_string())
    smtp.quit()


if __name__ == '__main__':
    send_support_mail()
