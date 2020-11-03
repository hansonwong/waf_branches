import os
import sys
import ast
import json
import time
import socket
import Queue
import threading
from logging import getLogger
from reportlog.log_config import read_config_ini
from utils.log_logger import rLog_dbg

SERVER = {'smtp_address':'smtp.163.com',
          'smtp_port':'25',
          'send_address':'lo5twind',
          'password':'163456455',
          'gateway_mail':'on'}

FWLOG_DEBUG = lambda x : rLog_dbg('send_email_msg', x)
MAIL_QUEUE_MAX = 20
MAIL_INTERVAL = 10



class MailConfigFile:

    def __init__(self,path1,path2):
        #self.msmtprc = r'/home/mail/msmtprc/etc/msmtprc'
        #self.muttrc = r'/home/mail/mutt/etc/Muttrc'
        self.__msmtprc = path1
        self.__muttrc = path2

    def update_msmtprc(self,args):
        try:
            content = []
            content.append('account default\n')
            content.append('host %s' % args['smtp_address'] + '\n')
            content.append('port %s' % args['smtp_port'] + '\n')
            content.append('from %s' % args['send_address'] + '\n')
            content.append('auth login\n')
            content.append('tls off\n')
            content.append('user %s' % args['send_address'] + '\n')
            content.append('password %s' % args['password'] + '\n')
            content.append('logfile /usr/local/mail/msmtp/var/log/mmog')
        except e as Exception:
            FWLOG_DEBUG(e)

        with open(self.__msmtprc,'w+') as f:
            for item in content:
                f.write(item)

    def update_muttrc(self,args):
        try:
            content = []
            content.append('set editor="vi"\n')
            content.append('set from=%s' % args['send_address'] + '\n')
            content.append('set realname="BLUEDON-FW"\n')
            content.append('set sendmail="/usr/local/mail/msmtp/bin/msmtp \
                           -C /usr/local/mail/msmtp/etc/msmtprc"\n')
            content.append('set use_from=yes')

        except e as Exception:
            FWLOG_DEBUG(e)

        with open(self.__muttrc,'w+') as f:
            for item in content:
                f.write(item)

"""
    Description:
        Using Mysql database to synchronize Send/Post process,
        Where Send process may exists everywhere possible, produce message
        when necessary. Post process is a singleton process receiving the
        message from Send process, then post them to mail server.
"""
UDP_ADDR = '127.0.0.1'
UDP_PORT = 15680

def send_email_msg(source,subject,content):
    """
        Description:
            Insert information of mail to database
        Input:
            source:The source of mail producer
            subject:Subject of mail
            content:Content of mail
    """
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    msg = dict()
    msg['source'] = source
    msg['subject'] = subject
    msg['content'] = content

    try:
        sk.sendto(str(msg), (UDP_ADDR, UDP_PORT))
        # FWLOG_DEBUG('sendmail: %s' % msg)
    except Exception as e:
        FWLOG_DEBUG(e)
        FWLOG_DEBUG('msg send:Error %s' % str(msg))
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
        FWLOG_DEBUG('mail socket initial error')
        return None

def post_email_msg(mail):
    """
        Description:
            use mutt to send mail
    """
    # check if mail option is enable, and get receive_address
    config = read_config_ini('Server Config')
    if config['gateway_mail'] == 'on':
        r_addr = config['receive_address']
    else:
        return

    cmd = 'echo -e "%s" | /usr/local/mail/mutt/bin/mutt -s "%s" %s'
    mail_cmd = cmd % (mail['content'],mail['subject'],r_addr)
    getLogger('log_daemon').debug(mail_cmd)
    FWLOG_DEBUG('[post mail] %s' % mail['content'])
    os.system(mail_cmd)
    pass

"""
    Description:
        LogMail create a thread to process mails in database, the thread fetch a
        record from db everytime, send it, and then delete the record
"""
class LogMail(threading.Thread):
    event = threading.Event()
    def __init__(self):
        super(LogMail,self).__init__()
        self.setName('logmail')
        self.sk = get_mail_socket()
        self.mail_time = 0
        self.mail_queue = Queue.Queue(MAIL_QUEUE_MAX)

    def run(self):
        # start send mail thread
        send_th = threading.Thread(target=self.send_mail)
        send_th.setName('sendmail')
        send_th.setDaemon(True)
        send_th.start()

        if self.sk is None:
            FWLOG_DEBUG('LogMail socket open error...')
            return
        while 1:
            if self.event.isSet():
                FWLOG_DEBUG('EVENT SET:[LOGMAIL:run]')
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
                FWLOG_DEBUG('[LogMail]get mail %s' % mail.get('content'))
                if not self.mail_queue.full():
                    self.mail_queue.put(mail)
                else:
                    FWLOG_DEBUG('[LogMail]mail_queue is Full')
                    item = self.mail_queue.get()
                    FWLOG_DEBUG('[LogMail]pop %s' % item.get('content'))
                    self.mail_queue.put(mail)
            except Exception as e:
                pass

            # # send mail to server very X second
            # if int(time.time()) - self.mail_time > 10:
            #     self.mail_time = int(time.time())
            #     # convert recv str to dict
            #     import ast
            #     mail = ast.literal_eval(recv)
            #     post_email_msg(mail)
            #     del mail

            del recv

        FWLOG_DEBUG('QUIT:[LOGMAIL:run]')
        getLogger('log_daemon').debug('QUIT:[LOGMAIL:run]')

    def start(self):
        super(LogMail,self).start()
        pass

    def stop(self):
        FWLOG_DEBUG('LOGMAIL stop')
        getLogger('log_daemon').debug('LOGMAIL stop')
        if not self.sk is None:
            self.sk.close()
        self.event.set()
        pass

    def send_mail(self):
        """ get mails from queue and send alternately """
        while 1:
            if self.event.isSet():
                break
            if not self.mail_queue.empty():
                try:
                    mail = self.mail_queue.get()
                    post_email_msg(mail)
                except Exception as e:
                    FWLOG_DEBUG('[LogMail]%s' % e)

            time.sleep(MAIL_INTERVAL)
        FWLOG_DEBUG('[LogMail]Exit send_mail thread')





if __name__ == '__main__':
    lm = LogMail()
    lm.start()
    for i in range(20):
        send_email_msg('test', 'test_send_mail', i)
        print 'send mail %s' % i
        time.sleep(1)
    lm.stop()

    # lm.run()
    #msmtprc_path = r'/usr/local/mail/msmtp/etc/msmtprc'
    #muttrc_path = r'/usr/local/mail/mutt/etc/Muttrc'
    #MailConfigFile(msmtprc_path,muttrc_path).update_msmtprc(SERVER)
    #MailConfigFile(msmtprc_path,muttrc_path).update_muttrc(SERVER)
