#!/usr/bin/env python
# -*- coding: utf-8 -*-

import stat, os, time, threading, datetime, psutil,sys
from logging import getLogger
from db import conn_scope, session_scope, row2dict,get_config
from config import config
from smtplib import SMTP_SSL, SMTP
from email.header import Header
from email.mime.text import MIMEText
from jinja2 import Environment, PackageLoader, FileSystemLoader

reload(sys)
sys.setdefaultencoding("utf-8")

def sendmail(server, user, passwd, sender, receiver, title, context, charset='utf-8', debug=False):
    smtp = SMTP(server)
    if debug:
        smtp.set_debuglevel(1)
    smtp.login(user, passwd)
    msg = MIMEText(context, _charset=charset)
    msg["Subject"] = Header(title, charset)
    msg["from"] = sender
    msg["to"] = receiver
    smtp.sendmail(sender, receiver, msg.as_string())
    #smtp.close()
    smtp.quit()


def get_disk_info():
    diskclean = get_config("DiskClear")
    parts = psutil.disk_partitions()
    total, used = 0, 0
    for part in parts:
        disk = psutil.disk_usage(part.mountpoint)
        total += disk.total
        used += disk.used
    percent = float(used)/float(total)*100
    if diskclean['limit'] < percent+60:
        return [diskclean['limit'], percent]
    return False


class AlertorDisk(threading.Thread):
    ''' 报警器 '''
    
    event = threading.Event()

    def __init__(self, ):
        super(AlertorDisk, self).__init__(name = self.__class__.__name__)
    
    def start(self):
        getLogger('main').debug(self.__class__.__name__+ ' starting...')
        super(AlertorDisk, self).start()
        getLogger('main').info(self.__class__.__name__+ ' started.')

    def stop(self):
        getLogger('main').debug(self.__class__.__name__+ ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__+ ' Exited.')

    def proc(self, mailset):
        data = {"SENDOR": "admin",}
        result = get_disk_info()
        #getLogger('main').info(str(data))
        if result:
            data['DATE'] = time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            data["SENDOR"] = mailset["userName"]
            data["fz"] = result[0]
            title = '蓝盾Web防火墙报警 ' + time.strftime('%Y-%m-%d', time.localtime(time.time()))
            msg = Environment(loader=FileSystemLoader('data/template/')).get_template('statisticsdisk').render(data=data)
            getLogger('main').info(msg)
            user = mailset['sender']
            sendmail(mailset['smtpServer'], user, mailset['password'], mailset['sender'], mailset['receiver'], title, msg)
            
    def run(self):
        '''
        读报警日志的总数，与上次的记录的总数相减。数字大于0就发送邮件报警。
        '''
        interval = 1
        while 1:
            try:
                for _ in range(10):
                    time.sleep(1)
                    interval = interval + 1
                    if self.event.isSet():
                        return
                mailset = get_config("MailSet")
                if not mailset:
                   continue
                self.proc(mailset)
            except Exception, e:
                getLogger('main').exception(e)
                
if __name__ == '__main__':
    mailset = get_config("MailSet")
    AlertorDisk().proc(mailset)
    """
    test_get_statistics()
    #echo '你好' | ./bin/gnokii --config config --sendsms 13929530587
    exit(0)
    session = Session()
    mailalert = session.query(MailAlert).one()
    #self.interval = 60 * 60 * int(mailalert.interval)
    if 1:
        mailset = session.query(MailSet).one()
        user = mailset.sender.split("@")[0]
        interval = 0
        data = {'SENDOR': mailset.username, 'INTERVAL': mailalert.interval}
        
        get_statistics(data)
        if data['ALL'] > 0:
            data['DATE'] = time.strftime('%Y-%m-%d %X',time.localtime(time.time()))
            title = '蓝盾Web防火墙报警 ' + time.strftime('%Y-%m-%d', time.localtime(time.time()))
            msg = Environment(loader=FileSystemLoader('data/template/')).get_template('statistics').render(data=data)
            getLogger('main').info(msg)
            sendmail(mailset.smtpserver, user, mailset.password, mailset.sender, mailset.receiver, title, msg)
    exit(0)
    context = '''<p>入侵分类数据统计:</p>
         <p style="text-indent:2em;">入侵总数: $count</p>
         <p style="text-indent:2em;">SQL注入: $num1</p>
         <p style="text-indent:2em;">XSS跨站脚本: $num2</p>
         <p style="text-indent:2em;">通用攻击: $num3</p>
         <p style="text-indent:2em;">HTTP协议保护: $num4</p>
         <p style="text-indent:2em;">特洛伊木马: $num5</p>
         <p style="text-indent:2em;">信息泄漏: $num6</p>
         <p style="text-indent:2em;">其它攻击: $num7</p>
         <p style="text-indent:2em;">发送日期: $date</p>'''
    sendmail('smtp.163.com', 'testfor51', 'testforwy', 'testfor51@163.com', 'testfor51@163.com', 'title', context)
    #sendmail2()
    """
