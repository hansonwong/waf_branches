#!/usr/bin/env python
# coding=utf-8

import os
import ast
import commands
from jinja2 import Environment, FileSystemLoader

# need to update syslog-ng.tpl in template folder
TEMPLATE_PATH = '/usr/local/bluedon/template'
TARGET_FILE = '/usr/local/syslog-ng/etc/syslog-ng.conf'
SYSLOG_TEMPLATE = 'syslog-ng.tpl'

def LOG_ERR(x):
    print x

def LOG_DEBUG(x):
    print x

def get_template(path=TEMPLATE_PATH, tpl=SYSLOG_TEMPLATE):
    ldr = FileSystemLoader(path)
    env = Environment(loader=ldr)
    template = env.get_template(tpl)
    return template


def render_template(confs):
    tpl = get_template()
    report_str = tpl.render(syslog_conf=confs)
    target_file = TARGET_FILE
    with open(target_file, 'w') as fp:
        fp.write(report_str)
    print report_str


def syslog_config(args=None):
    args = ast.literal_eval(args[0])
    LOG_DEBUG(type(args))
    LOG_DEBUG(args)
    import re
    port_reg = '(udp|tcp)\(".+?"\sport\((\d+)\)\);'
    # d = ast.literal_eval(args[0])
    try:
        # kill syslog-ng at first
        os.system('killall syslog-ng')
        LOG_DEBUG('stop syslog-ng')
        #delete the previous iptables if exists
        with open('/usr/local/syslog-ng/etc/syslog-ng.conf','r') as fp:
            lines = fp.read()
        pat = re.compile(port_reg)
        old_ports = pat.findall(lines)
        LOG_DEBUG('[syslog-ng.conf] DELETE old_port:%s' % old_ports)
        for old_port in old_ports:
            res = commands.getoutput('iptables -D FWINPUT -p %s --sport %s -j ACCEPT' % old_port)
            LOG_DEBUG('iptables -D FWINPUT -p %s --sport %s -j ACCEPT' % old_port)

        confs = list()
        for arg in args:
            LOG_DEBUG('processing')
            LOG_DEBUG(arg)
            # check if syslog config is enable
            if not arg['status']:
                continue
            
            ip = arg['server_ip']
            proto = arg['protocol']
            port = arg['port']

            confs.append(dict(proto=proto, ip=ip, port=port))
            
            res = commands.getoutput('iptables -C FWINPUT -p {proto} \
                --sport {port} -j ACCEPT'.format(proto=proto, port=port))
            if 'iptables: Bad rule' in res:
                #comment in 250/249/248
                res = commands.getoutput('iptables -A FWINPUT -p {proto} \
                    --sport {port} -j ACCEPT'.format(proto=proto, port=port))
                pass

        # start syslog-ng if at least one server enable
        if len(confs) > 0:
            # generate syslog-ng config file
            render_template(confs)
            # run syslog-ng
            LOG_DEBUG('start syslog-ng')
            os.system('/usr/local/syslog-ng/sbin/syslog-ng')


            

        # if d['status'] == '1':
        #     #print 'syslog-ng on'
        #     ip = d['server_ip']
        #     port = d['port']
        #     proto = d['protocol']
        #     #if protocol is tcp, add iptables rule
        #     if d['protocol'] == 'tcp':
        #         #comment in 250/249/248
        #         res = commands.getoutput('iptables -C FWINPUT -p tcp --sport %s -j ACCEPT' % int(d['port']))
        #         if 'iptables: Bad rule' in res:
        #             #comment in 250/249/248
        #             res = commands.getoutput('iptables -A FWINPUT -p tcp --sport %s -j ACCEPT' % int(d['port']))
        #             pass

        #     pass
        #     # restart syslog-ng
        #     os.system('killall syslog-ng')
        #     os.system('/usr/local/syslog-ng/sbin/syslog-ng')

        # elif d['status'] == 0:
        #     #comment in 250/249/248
        #     # res = commands.getoutput('iptables -D FWINPUT -p tcp --sport %s -j ACCEPT' % int(old_port))
        #     # kill syslog-ng
        #     os.system('killall syslog-ng')
        #     pass
    except Exception as e:
        LOG_ERR('ERROR:WRITING [syslog-ng.conf]')
        LOG_ERR(e)

    pass


if __name__ == '__main__':
    conf1 = dict(proto='tcp', ip='1.1.1.1', port=111)
    conf2 = dict(proto='udp', ip='2.2.2.2', port=222)
    conf3 = dict(proto='tcp', ip='3.3.3.3', port=333)
    confs =[conf1, conf2, conf3]
    render_template(confs)
    syslog_config()
    pass
