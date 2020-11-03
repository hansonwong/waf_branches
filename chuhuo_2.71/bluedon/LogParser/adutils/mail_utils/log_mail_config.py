#!/usr/bin/env python
# coding=utf-8

import os
import sys
import ast
import json
import time
import socket
import Queue
import threading
from logging import getLogger
from adutils.config import fetchone_sql as fetch3306
from adutils.audit_logger import rLog_dbg, rLog_err
from adutils.mail_utils.bd_email import send, MAIL_LOG

SERVER = {'smtp_address':'smtp.163.com',
          'smtp_port':'25',
          'send_address':'lo5twind',
          'password':'163456455',
          'gateway_mail':'on'}

DBG = lambda x : rLog_dbg(MAIL_LOG, x)
ERR = lambda x : rLog_err(MAIL_LOG, x)

MAIL_QUEUE_MAX = 1024
MAIL_INTERVAL = 10

"""
    Description:
        Using Mysql database to synchronize Send/Post process,
        Where Send process may exists everywhere possible, produce message
        when necessary. Post process is a singleton process receiving the
        message from Send process, then post them to mail server.
"""
UDP_ADDR = '127.0.0.1'
UDP_PORT = 15681

def send_email_msg(source, type, content, t):
    """
        Description:
            Insert information of mail to database
        Input:
            source:The source of mail producer
            subject:Subject of mail
            content:Content of mail
    """
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    msg = dict(source=source, type=type, content=content, time=t)

    try:
        sk.sendto(str(msg), (UDP_ADDR, UDP_PORT))
        DBG('add mail message: %s' % msg)
    except Exception as e:
        DBG(e)
        DBG('msg send:Error %s' % str(msg))
    finally:
        del msg
        sk.close()

def get_mail_socket(addr=UDP_ADDR, port=UDP_PORT):
    """
        Description:
            return a UDP socket for mail message sending and receiving
    """
    try:
        sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        sk.settimeout(1)
        sk.bind((addr, port))
        return sk
    except:
        DBG('mail socket initial error')
        return None


def get_mail_switch_conf():
    sql = "SELECT sValue FROM m_tbconfig WHERE sName='mailAlert'"
    ret = fetch3306(sql)
    js_ret = json.loads(ret.get('sValue', '{}'))
    DBG(js_ret)
    alert_enable = js_ret.get('alert_enable') or None
    warning_enable = js_ret.get('warning_enable') or None

    DBG('alert_enable=%s, warning_enable=%s' % (alert_enable, warning_enable))

    return alert_enable, warning_enable


"""
    Description:
        LogMail create a thread to process mails in database, the thread fetch a
        record from db everytime, send it, and then delete the record
"""
class LogMail(threading.Thread):
    event = threading.Event()
    def __init__(self):
        super(LogMail,self).__init__()
        self.setName('adlogmail')
        self.sk = get_mail_socket()
        self.mail_time = 0
        self.mail_queue = Queue.Queue(MAIL_QUEUE_MAX)
        self.warning_msg = ''

    def run(self):
        # start send mail thread
        send_th = threading.Thread(target=self.send_mail)
        send_th.setName('sendmail')
        send_th.setDaemon(True)
        send_th.start()

        if self.sk is None:
            DBG('LogMail socket open error...')
            return
        while 1:
            if self.event.isSet():
                DBG('EVENT SET:[LOGMAIL:run]')
                getLogger('log_daemon').debug('EVENT SET:[LOGMAIL:run]')
                break
            try:
                # receive from socket every second, but only send mail X(ten)
                # second after last mail had sent
                recv = self.sk.recvfrom(4096)[0]
            except:
                continue

            # convert recv str to dict
            try:
                mail = ast.literal_eval(recv)
                DBG('[LogMail]get mail %s' % mail.get('content'))
                if not self.mail_queue.full():
                    self.mail_queue.put(mail)
                else:
                    DBG('[LogMail]mail_queue is Full')
                    # item = self.mail_queue.get()
                    # DBG('[LogMail]pop %s' % item.get('content'))
                    # self.mail_queue.put(mail)
            except Exception as e:
                pass

            del recv

        DBG('QUIT:[LOGMAIL:run]')
        getLogger('log_daemon').debug('QUIT:[LOGMAIL:run]')

    def start(self):
        super(LogMail,self).start()
        pass

    def stop(self):
        DBG('LOGMAIL stop')
        getLogger('log_daemon').debug('LOGMAIL stop')
        if not self.sk is None:
            self.sk.close()
        self.event.set()
        pass

    def send_mail(self):
        """ get mails from queue and send alternately """
        msg_count = 0
        time_count = 0
        while 1:
            if self.event.isSet():
                break
            if not self.mail_queue.empty() and time_count > 20:
                time_count = 0
                warning_msg = warning_time = ''
                body = "你好，\r\n\t"
                alert_count = 0
                warning_count = 0
                message_list = list()
                for i in range(MAIL_QUEUE_MAX):
                    if self.mail_queue.empty(): break
                    m = self.mail_queue.get()
                    try:
                        if m['source'] == 'alert':
                            m['source'] = '告警'
                            alert_count += 1
                        elif m['source'] == 'warning':
                            m['source'] = '警报'
                            warning_count += 1
                        else:
                            # invalid source type
                            continue
                        # build msg by message in queue
                        _msg = '{source}:[{time}] {type} {content}'.format(**m)
                        message_list.append(_msg)
                        DBG(_msg)
                    except Exception as e:
                        ERR(e)
                        continue
                # build the msg
                body += '\r\n\t'.join(message_list)
                if alert_count > 0:
                    body += '\r\n\t告警[{}]条'.format(alert_count)
                    alert_count = 0
                if warning_count > 0:
                    body += '\r\n\t警报[{}]条'.format(warning_count)
                    warning_count = 0
                body += "\r\n"
                body += "\r\n"
                body += "\t\t\t\t蓝盾信息安全技术股份有限公司\r\n"
                nowdate = time.strftime( '%Y-%m-%d', time.localtime() )
                body += "\t\t\t\t" + nowdate
                subject = '蓝盾审计系统告警邮件'
                mail = {'subject': subject, 'body': body}
                try:
                    send(mail)
                except Exception as e:
                    ERR('[LogMail]%s' % e)

            else:
                time.sleep(1)
                time_count += 1
        DBG('[LogMail]Exit send_mail thread')





if __name__ == '__main__':
    lm = LogMail()
    lm.start()
    for i in range(60):
        send_email_msg('alert', 'test_send_mail', 'key_type: key',time.ctime())
        send_email_msg('warning', 'test_send_mail', 'key_type: key',time.ctime())
        print 'send mail %s' % i
        time.sleep(1)
    lm.stop()

    # lm.run()
    #msmtprc_path = r'/usr/local/mail/msmtp/etc/msmtprc'
    #muttrc_path = r'/usr/local/mail/mutt/etc/Muttrc'
    #MailConfigFile(msmtprc_path,muttrc_path).update_msmtprc(SERVER)
    #MailConfigFile(msmtprc_path,muttrc_path).update_muttrc(SERVER)
