#!/usr/bin/env python
# coding=utf-8

"""
    2016-09-27:
        Add: NGINX port setting for IPv6

"""
""" 更改nginx监听端口并重启服务 """
import os
from logging import getLogger
from utils.logger_init import logger_init
from db.config import fetchall_sql as fcal_3306
from utils.logger_init import log_cmd


MGT_NT_PATH = r'/etc/network_config/mgt_nic.txt'

""" 更改监听端口号 """
nginx_file = '/Data/apps/nginx/conf/ssl.conf'
nginx_kill = '/usr/bin/killall nginx'
nginx_service = '/Data/apps/nginx/sbin/nginx'
log_path = '/usr/local/bluedon/log/nginx.log'
log_name = 'NGINX'
logger_init(log_name, log_path)


def run_cmd(allow, device, port, ilog=0):
    add_or_del = {True: '-I', False: '-D'}[allow]
    cmd = '/usr/sbin/iptables {add_or_del} FWINPUT -i {device} -p tcp -m multiport --dport {port},80 -j {jump}'
    tmp = cmd.format(add_or_del=add_or_del, device=device, port=port, jump='ACCEPT')
    os.system(tmp)
    log_cmd(__file__, tmp)
    add_or_del = {True: '-I', False: '-D'}[allow and ilog or False]
    tmp = cmd.format(add_or_del=add_or_del, device=device, port=port,
                     jump='LOG --log-prefix "ipt_log=ACCEPT "')
    os.system(tmp)
    log_cmd(__file__, tmp)


def get_all_mgt():
    mgt = []
    sql = 'SELECT sPortName,iStatus,iAllowLog FROM m_tbnetport WHERE iWeb=1 and iStatus="1";'
    for res in fcal_3306(sql):
        print 'all res', res
        mgt.append((res['sPortName'], res['iAllowLog']))
    print 'all_mgt ', mgt
    return mgt


def get_none_mgt():
    mgt = []
    sql = 'SELECT sPortName,iStatus,iWeb,iAllowLog FROM m_tbnetport'
    for res in fcal_3306(sql):
        print 'none mgt ', res
        if not res['iWeb'] == '1' or not res['iStatus'] == '1':
            mgt.append((res['sPortName'], res['iAllowLog']))
    print 'none mgt ', mgt
    return mgt


def set_nginx(data):
    # logger_init(log_name, log_path)
    lines = []
    os.system(nginx_kill)
    try:
        with open(nginx_file, 'r') as fp:
            lines = fp.readlines()
    except IOError as e:
        getLogger(log_name).debug(e)
        return

    for line in lines:
        if line.strip().startswith('listen'):
            # find old port
            old_port = line.split()[1].rstrip(';')
            # if int(old_port) == int(data):
                # return
            import re
            print 'line ', line
            new_line = 'listen %d;' % (int(data))
            idx = lines.index(line)
            lines[idx] = re.sub('listen\s*\w+;', new_line, line)
            if lines[idx + 1].strip().startswith('listen'):
                lines[idx + 1] = '    listen [::]:{port};\n'.format(port=(int(data)))
            break
    try:
        with open(nginx_file, 'w') as fp:
            content = ''.join(lines)
            print 'write file'
            fp.write(content)
            getLogger(log_name).debug('modify nginx listen %d' % (int(data)))
    except IOError as e:
            getLogger(log_name).debug(e)

    # config iptables
    for mgt in get_all_mgt():
        run_cmd(False, mgt[0], old_port, mgt[1])
        run_cmd(True, mgt[0], data, mgt[1])
    os.system(nginx_service)


def recover_nginx():
    try:
        with open(nginx_file, 'r') as fp:
            lines = fp.readlines()
    except IOError as e:
        getLogger(log_name).debug(e)
        return

    for line in lines:
        if line.strip().startswith('listen'):
            # find old port
            old_port = line.split()[1].rstrip(';')
            break

    for mgt in get_none_mgt():
        run_cmd(False, mgt[0], old_port, mgt[1])

    for mgt in get_all_mgt():
        # delete old port nginx
        run_cmd(False, mgt[0], old_port, mgt[1])
        run_cmd(True, mgt[0], old_port, mgt[1])


if __name__ == '__main__':
    # reboot recover don't remove
    recover_nginx()
    # set_nginx('888')
