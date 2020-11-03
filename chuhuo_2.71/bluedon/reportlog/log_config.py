#! /usr/bin/env python
# -*- coding:utf-8 -*-
import os
import ConfigParser
import commands
import threading
import ast
from math import ceil
from utils.logger_init import logger_init
from logging import getLogger
from utils import crontab
from utils.log_logger import FWLOG_DEBUG

msmtprc_path = r'/usr/local/mail/msmtp/etc/msmtprc'
muttrc_path = r'/usr/local/mail/mutt/etc/Muttrc'
log_config_ini = r'/usr/local/bluedon/conf/log_config.ini'
LOG_PATH = r'/var/log'
beep = r'/home/bluedon/beep/beepalert'
bd_cron_config = {
        "bd_logrotate_cron" : r'/etc/cron.d/bd_logrotate_cron',
        "bd_logrotate" : r'/etc/logrotate.d/bd_logrotate',
        "bd_log_cron" : r'/etc/cron.d/bd_log_cron'
}

SRV_CFG = {'smtp_address':'smtp.163.com',
          'smtp_port':'25',
          'send_address':'bluedon_test@163.com',
          'password':'bluedon111',
          'gateway_mail':'on',
          'receive_address':'bluedon_test@163.com',
          'souce_alert':'on'}

LOG_CFG = {'full':'pause','mail':'off','import':'on'}
ARCH_CFG = {'compress':0,'cycle':'every_day'}
SYS_LOG_CFG = {'status':'1','server_ip':'172.16.3.124','protocol':'udp','port':'514'}

def log_logger(msg):
    getLogger('log_daemon').debug(msg)
    #getLogger('main').info(msg)
    pass

def log_logger_main(msg):
    getLogger('main').info(msg)
    pass

def log_logger_daemon(msg):
    getLogger('log_daemon').debug(msg)
    pass

def beep_alert(on='on'):
    #os.system(beep)
    config = read_config_ini('Server Config')
    onoff = config.get('souce_alert', 'off')
    if onoff == 'on':
        # print 'beep on'
        os.system(beep)
    else:
        pass

def send_mail(subject,msg,to):
    cmd = 'echo -e "%s" | /usr/local/mail/mutt/bin/mutt -s "%s" %s' % (msg,subject,to)
    os.system(cmd)
    beep_alert()
    log_logger('send mail:%s' % cmd)

def save_config_ini(log_cfg=None,server_cfg=None,arch_cfg=None,syslog_cfg=None,path=log_config_ini):
    return
    # pass
    # config = ConfigParser.RawConfigParser()
    # if not os.path.exists(path):
    #     config.add_section('LOG Config')
    #     config.add_secton('Server Config')
    #     config.add_section('ARCH Config')
    #     config.add_section('Syslog Config')
    # else:
    #     config.read(path)

    # if log_cfg != None:
    #     #log_cfg section
    #     #config.add_section('LOG Config')
    #     config.set('LOG Config','full',log_cfg['full'])
    #     config.set('LOG Config','mail',log_cfg['mail'])
    #     config.set('LOG Config','import',log_cfg['import'])
    #     log_logger('change log ini')

    # if server_cfg != None:
    #     #sercer_cfg section
    #     #config.add_section('Server Config')
    #     config.set('Server Config','send_address',server_cfg['send_address'])
    #     config.set('Server Config','password',server_cfg['password'])
    #     config.set('Server Config','smtp_address',server_cfg['smtp_address'])
    #     config.set('Server Config','smtp_port',server_cfg['smtp_port'])
    #     config.set('Server Config','gateway_mail',server_cfg['gateway_mail'])
    #     config.set('Server Config','receive_address',server_cfg['receive_address'])
    #     config.set('Server Config','souce_alert',server_cfg['souce_alert'])
    #     log_logger('change server ini')


    # if arch_cfg != None:
    #     config.set('ARCH Config','compress',arch_cfg['compress'])
    #     config.set('ARCH Config','cycle',arch_cfg['cycle'])
    #     log_logger('chage arch ini')

    # if syslog_cfg != None:
    #     config.set('Syslog Config','status',syslog_cfg['status'])
    #     config.set('Syslog Config','server_ip',syslog_cfg['server_ip'])
    #     config.set('Syslog Config','protocol',syslog_cfg['protocol'])
    #     config.set('Syslog Config','port',syslog_cfg['port'])
    #     log_logger('chage syslog ini')

    # with open(path,'wb') as cfg:
    #     config.write(cfg)

def read_config_ini_old(section,path=log_config_ini):
    pass
    # if not os.path.exists(path):
    #     save_config_ini(log_cfg=LOG_CFG,server_cfg=SRV_CFG,arch_cfg=ARCH_CFG)
    # #what to do if log_config_ini DO NOT exist at the beginning
    # config = ConfigParser.ConfigParser()
    # config.read(path)

    return dict(config.items(section))

def read_config_ini(section='all'):
    conf_sect = {'LOG Config':'logConfig',
                 'Server Config':'mailAlert',
                 'ARCH Config':'logFileLib',
                 'Syslog Config':'SyslogServer'}

    try:
        if section == 'all':
            from db.config import fetchall_sql as fcal_3306
            sql = ('SELECT sName, sValue FROM m_tbconfig WHERE sName in '
                             '("%s")' % '", "'.join(conf_sect.values()))
            # sName as key
            _d = {res['sName']:res['sValue'] for res in fcal_3306(sql)}
            # section Name as key
            d = {key:_d[conf_sect[key]] for key in conf_sect}

            return d
        else:
            from db.config import fetchone_sql as fetch_3306
            sName = conf_sect.get(section)
            if sName:
                res = fetch_3306('SELECT sValue FROM m_tbconfig WHERE sName="%s"' % sName)
                return ast.literal_eval(res['sValue'])
            else:
                return {}

    except Exception as e:
        raise Exception('read_config_ini error %s' % e)


def get_disk_usage(path):
    try:
        fs = os.statvfs(path)
        used = fs.f_blocks - fs.f_bfree
        usage = used / (used + fs.f_bavail) * 100
        return ceil(usage)
    except Exception as e:
        return -1

def update_log_config(args):
    d = ast.literal_eval(args[0])
    #MysqlLogDaemon.log_cfg.log_cfg = d
    if not d.has_key('import'):
        d['import'] = 'on'
    # save_config_ini(log_cfg = d)
    getLogger('main').info('Log config  %s' % d)

def update_server_config(args):
    d = ast.literal_eval(args[0])
    if not d.has_key('souce_alert'):
        d['souce_alert']='off'
    from reportlog.log_mail_config import MailConfigFile
    MailConfigFile(msmtprc_path,muttrc_path).update_msmtprc(d)
    MailConfigFile(msmtprc_path,muttrc_path).update_muttrc(d)
    #MysqlLogDaemon.server_cfg.server_cfg = d
    #DELETE previous rule from iptables first
    old_port = None
    new_port = d.get('smtp_port', None)
    try:
        with open('/usr/local/bluedon/conf/mail_port', 'r+') as fp:
            old_port = fp.readline()
        if old_port:
            res = commands.getoutput('iptables -D FWINPUT -p tcp --sport %s -j ACCEPT' % int(old_port))
            getLogger('main').info('Log mail delete old port %s' % old_port)
    except:
        pass
    # save_config_ini(server_cfg = d)
    #insert iptables
    if d['gateway_mail'] == 'on':
        if new_port is not None:
            res = commands.getoutput('iptables -C FWINPUT -p tcp --sport %s -j ACCEPT' % int(new_port))
            if 'iptables: Bad rule' in res:
                res = commands.getoutput('iptables -A FWINPUT -p tcp --sport %s -j ACCEPT' % int(new_port))

    with open('/usr/local/bluedon/conf/mail_port', 'w+') as fp:
        fp.write(new_port or '')
        getLogger('main').info('Log mail config new port %s' % new_port)

    getLogger('main').info('Log mail config  %s' % d)

def mail_test(args):
    d = ast.literal_eval(args[0])
    config = read_config_ini('Server Config')
    if config['gateway_mail'] == 'on':
        r_addr = config['receive_address']
        beep_on = config.get('souce_alert', 'off')

        res = commands.getoutput('iptables -C FWINPUT -p tcp --sport %s -j ACCEPT' % int(config['smtp_port']))
        if 'iptables: Bad rule' in res:
            res = commands.getoutput('iptables -A FWINPUT -p tcp --sport %s -j ACCEPT' % int(config['smtp_port']))

        getLogger('main').info('sending mail to %s' % r_addr)
        beep_alert(beep_on)
        send_mail(d['title'],d['content'],r_addr)

def mail_test_attach(subject,attach):
    config = read_config_ini('Server Config')
    if config['gateway_mail'] == 'on':
        r_addr = config['receive_address']
        beep_on = config.get('souce_alert', 'off')

        #insert iptables
        res = commands.getoutput('iptables -C FWINPUT -p tcp --sport %s -j ACCEPT' % int(config['smtp_port']))
        if 'iptables: Bad rule' in res:
            res = commands.getoutput('iptables -A FWINPUT -p tcp --sport %s -j ACCEPT' % int(config['smtp_port']))

        #send_mail(d['title'],d['content'],r_addr)
        cmd = '/usr/local/mail/mutt/bin/mutt -s "%s" %s < %s' % (subject,r_addr,attach)
        beep_alert(beep_on)
        getLogger('main').info('sending mail to %s' % r_addr)
        os.system(cmd)

def log_archive(args):
    d = ast.literal_eval(args[0])
    # save_config_ini(arch_cfg = d)
    set_crontab(d)
    getLogger('main').info(d)

def set_crontab(args):
    #cmd = 'sh /usr/local/bluedon/log_bak.sh'
    cmd = 'python /usr/local/bluedon/reportlog/log_backup_lib.py'
    c = '5 0 * * 0 root %s\n' % cmd
    try:
        if args['cycle'] == 'every_month':
            c = '5 0 1 * * root %s\n' % cmd
            #c = '*/1 * * * * %s\n' % cmd
        elif args['cycle'] == 'every_day':
            c = '5 0 * * * root %s\n' % cmd
        elif args['cycle'] == 'every_week':
            c = '5 0 * * 0 root %s\n' % cmd
    except KeyError:
        # use default setting(week)
        pass
    crontab.update_crontab('log_arch',c)
    getLogger('main').info('UPDATE [crontab] %s' % c)

def syslog_config(args):
    import re
    port_reg = '(udp|tcp)\(".+?"\sport\((\d+)\)\);'
    d = ast.literal_eval(args[0])
    try:
        #delete the previous iptables if exists
        with open('/usr/local/syslog-ng/etc/syslog-ng.conf','r') as fp:
            lines = fp.read()
        try:
            old_port = re.search(port_reg, lines, re.DOTALL).group(2)
            getLogger('main').info('[syslog-ng.conf] DELETE old_port:%s' % old_port)
        except:
            getLogger('main').error('[syslog-ng.conf] ERROR :cannot find old port')
            old_port = None
        if old_port is not None:
            res = commands.getoutput('iptables -D FWINPUT -p tcp --sport %s -j ACCEPT' % int(old_port))

        if d['status'] == '1':
            #print 'syslog-ng on'
            ip = d['server_ip']
            port = d['port']
            proto = d['protocol']
            #if protocol is tcp, add iptables rule
            if d['protocol'] == 'tcp':
                #comment in 250/249/248
                res = commands.getoutput('iptables -C FWINPUT -p tcp --sport %s -j ACCEPT' % int(d['port']))
                if 'iptables: Bad rule' in res:
                    #comment in 250/249/248
                    res = commands.getoutput('iptables -A FWINPUT -p tcp --sport %s -j ACCEPT' % int(d['port']))
                    pass

            with open('/usr/local/syslog-ng/etc/syslog-ng.conf','r') as fp:
                replace = '%s("%s" port(%s));' % (proto,ip,port)
                l = re.sub(r"udp\(.+\)\;|tcp\(.+\)\;",replace,fp.read())
            with open('/usr/local/syslog-ng/etc/syslog-ng.conf','w') as fp:
                if not l == '':
                    fp.write(l)
                else:
                    getLogger('main').error('ERROR:WRITING [syslog-ng.conf]')
            pass
            # restart syslog-ng
            os.system('killall syslog-ng')
            os.system('/usr/local/syslog-ng/sbin/syslog-ng')

        elif d['status'] == 0:
            #comment in 250/249/248
            # res = commands.getoutput('iptables -D FWINPUT -p tcp --sport %s -j ACCEPT' % int(old_port))
            # kill syslog-ng
            os.system('killall syslog-ng')
            pass

        # save_config_ini(syslog_cfg = d)
    except Exception as e:
        print e
        getLogger('main').error('ERROR:WRITING [syslog-ng.conf]')
        getLogger('main').error(e)

    pass

def process_is_running(pn):
    import commands
    res = commands.getoutput("ps -aux | grep %s | grep -v grep | awk '{print $2}'" % pn).split('\n')
    print res
    print not res == ['']
    return not res == ['']
    pass


def log_cron_recovery():
    cron_config = {
            "bd_logrotate_cron" : r'/usr/local/bluedon/conf/bd_logrotate_cron.bak',
            "bd_logrotate" : r'/usr/local/bluedon/conf/bd_logrotate.bak',
            "bd_log_cron" : r'/usr/local/bluedon/conf/bd_log_cron.bak'
    }
    for f in bd_cron_config:
        if not os.path.exists(bd_cron_config[f]):
            os.system('cp %s %s' % (cron_config[f],bd_cron_config[f]))
        else:
            FWLOG_DEBUG('File %s is exists...' % bd_cron_config[f])


def log_config_recovery():

    res = read_config_ini('all')

    # 'LOG Config':'logConfig',  NO NEED TO RECOVER
    # update_log_config([res['LOG Config']])

    # 'Server Config':'mailAlert',
    update_server_config([res['Server Config']])

    # 'ARCH Config':'logFileLib',
    log_archive([res['ARCH Config']])

    # 'Syslog Config':'SyslogServer'
    syslog_config([res['Syslog Config']])

    return


if __name__ == '__main__':
    pass
    log_config_recovery()
    # send_mail("test mail","TEST MAIL\nThis is a test mail",'bluedon_fw@126.com')
    #args = ['{"status":"0","server_ip":"3.2.3.2","protocol":"tcp","port":"123"}']
    #syslog_config(args)
    # beep_alert()
    #log_config_recovery()
    #process_is_running('python')
    #SRV_CFG =["""{'smtp_address':'smtp.163.com',
    #          'smtp_port':'25',
    #          'send_address':'bluedon_test@163.com',
    #          'password':'bluedon111',
    #          'gateway_mail':'on',
    #          'receive_address':'bluedon_test@163.com',
    #          'souce_alert':'on'}"""]
    ##update_server_config(SRV_CFG)
    #SYSLOG_CFG = ["{'status':'1','server_ip':'172.16.3.4','protocol':'tcp','port':'514'}"]
    #syslog_config(SYSLOG_CFG)
    #log_cron_recovery()


