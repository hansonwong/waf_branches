#!/usr/bin/env python
# coding=utf-8

"""
url: /Site/UserLogin

modify log:
    2016-11-4:
        1、用户认证
"""


import os
import sys
import json
import codecs
import commands
import time
from threading import Thread

from IPy import IP

from db.config import search_data, mkdir_file, execute_sql
from db.config1 import execute_sql as exs
from db.mysql_db import select_one
from utils.logger_init import logger_init
from core.exceptions import ArgumentError
from core.setting import LOG_BASE_PATH, CMD_SED
from objectdefine.ip_range import get_ip
from system.hasync.sync_send import dump_file_data


LOG_PATH = os.path.join(LOG_BASE_PATH, 'authentication.log')
LOG_NAME = 'AUTHENTICATION'

COMMANDS = commands.getstatusoutput

logger = logger_init(LOG_NAME, LOG_PATH, 'DEBUG')


def judge_data(msql, flag=True):
    """ 判断查询的记录集是否为空 """

    key_word = ''
    tablename = ''
    condiction = ''
    words = msql.split()
    for word in words:
        if key_word == 'from':
            tablename = word
        elif key_word == 'where':
            condiction = word
        key_word = word.lower()
    results = search_data(msql)
    if not results and flag:
        logger.debug('%s table not %s' %(tablename, condiction))
        raise ArgumentError
    return results

def get_ips(data):
    """
    获取关联ip/ip组的相关数据
    args:
        data: 记录集
    return:
        ips: ip集
        ipsets: 设置ipset或iptables规则所需的ip
        itype: ip的类型
    """
    ips = []
    ipsets = ''
    itype = None

    def netmarkip(result):
        """ 获取ip """
        vips = []
        vipsets = ''
        vtype = None
        if str(result['sAddtype']) == '1':
            if result['sAddress'].endswith('.0'):
                if '.' not in result['sNetmask']:
                    addrs = IP('%s/%s' %(result['sAddress'], result['sNetmask']))
                else:
                    addrs = IP('%s/%s' %(result['sAddress'],
                                         result['sNetmask']), make_net=True)
                vips.append(addrs)
                vipsets = addrs.strNormal(1)
            else:
                vips.append(result['sAddress'])
                vipsets = result['sAddress']
            vtype = 'onlyip'
        elif str(result['sAddtype']) == '2':
            vipsets = '%s-%s' %(result['sAddress'], result['sNetmask'])
            vips = get_ip(vipsets)
            vtype = 'iprange'
        return  vips, vipsets, vtype

    if str(data['iRangeType']) == '1':	    # ip
        addr_sql = 'select sAddress, sNetmask, sAddtype from m_tbaddress_list\
                where id=%d;' %(int(data['sRange']))
        result = judge_data(addr_sql)[0]
        vips, vipsets, vtype = netmarkip(result)
        ipsets = vipsets
        ips = ips + vips
        itype = vtype
    elif str(data['iRangeType']) == '2':    # ip组
        g_sql = 'select HideID, sIP from m_tbaddressgroup where id=%d;'\
                %(int(data['sRange']))
        result = judge_data(g_sql)[0]

        ipsets = result['HideID']
        itype = 'ipgroup'

        ids = result['sIP'].split(',')
        ids = ['id=%s' %(x) for x in ids]
        ids = ' or '.join(ids)
        addr_sql = 'select sAddress, sNetmask, sAddtype from m_tbaddress_list\
                where %s;' %(ids)
        results = judge_data(addr_sql)
        for result in results:
            vips, vipsets, vtype = netmarkip(result)
            ips = ips + vips

    return (set(ips), ipsets, itype)


class OnlineDownline(object):
    """ 用户上下线 """

    def __init__(self, data):
        """ 初始化 """
        self.username = data.get('sUserName', '')
        self.userip = data.get('sIP', '')
        self.filename = data.get('filename', '')
        self.passwd = data.get('sPassword', '')
        self.stype = data.get('type', '')
        self.filepath = '/usr/local/bluedon/conf/online_users'
        mkdir_file(self.filepath, 'file')
        self.content = self.get_online_user()  # 所有上线用户的字典 ｛ip: (用户名，策略id)，｝

    def search_tactics(self):
        """ 根据ip查找其适用的策略并返回 """

        tactics_sql = 'select * from m_tbusers_authentication_tactics\
                where iStatus=1;'
        results = search_data(tactics_sql)

        tactics = None
        imax = 0
        for result in results:
            ips, ipsets, itype = get_ips(result)
            for item in ips:
                if self.userip in item and imax < result['iPriority']:
                    tactics = result
                    imax = result['iPriority']
                    break
        return tactics

    def update_table_userip(self, tactics, username, userip, action):
        """ 更新用户表中的ip """

        user_sql = 'select sIP, iBinIp from m_tbusers where\
                sUserName="%s";' %(username)
        result = judge_data(user_sql)[0]

        ips = result['sIP'].split(',') if result['sIP'] else []
        if action == 'downline':
            if userip in ips:
                ips.remove(userip)
        elif action == 'online':
            if int(tactics['iAllowMultiLogin']) == 2:   # 仅允许一人登录
                ips = [userip]
            else:
                ips.append(userip)
        ips = ','.join(ips)

        if result['iBinIp'] == 1: # 绑定ip的用户, 只更改在线状态
            if action == 'downline':
                u_sql = 'UPDATE m_tbusers SET iOnline=%d where\
                        sUserName="%s";' %(0, username)
            else:
                u_sql = 'UPDATE m_tbusers SET iOnline=%d where\
                        sUserName="%s";' %(1, username)
        elif result['iBinIp'] == 0: # 未绑定ip的用户，更改在线状态, 更新ip
            if not ips:
                ionline = 0
            else:
                ionline = 1
            u_sql = 'UPDATE m_tbusers SET sIP="%s", iOnline=%d where\
                    sUserName="%s";' %(ips, ionline, username)
        execute_sql(u_sql)

    def get_online_user(self):
        """ 获取上线的用户 """
        with open(self.filepath, 'r') as fp:
            contents = fp.read()
            if '\n' == contents:
                contents = {}
        contents = json.loads(contents) if contents else {}
        return contents

    def update_online_user(self):
        """ 更新上线的用户 """
        with open(self.filepath, 'w') as fp:
            line = json.dumps(self.content)
            fp.write(line)
        logger.info('update online_user file contents: {}'.format(self.content))
        tr = Thread(target=dump_file_data, args=('files',))
        tr.setDaemon(True)
        tr.start()

    def update_ipset(self, dip, action='add'):
        """ 更新ipset """
        ipset_cmd = '/usr/local/sbin/ipset %s authed_set %s' %(action, dip)
        os.system(ipset_cmd)

    def online(self):
        """ 用户上线 """

        def write_file(vip, status):
            """ 认证状态写入文件
            /tmp/fifo/rz*
            """
            line = dict()
            line.setdefault('ip', '%s' %(vip))
            line.setdefault('status', '%s' %(status))
            line = json.dumps(line)
            cmd_echo = "/usr/bin/echo '%s' > %s" %(line, file_path)
            os.system(cmd_echo)

        file_path = '/tmp/fifo/%s' %(self.filename)
        mkdir_file(file_path, 'file')

        config_sql = 'select sValue from m_tbconfig where sName="UserStrategy";'
        result = search_data(config_sql)[0]['sValue']
        result = json.loads(result)
        if str(result['iTurnOn']) == '0':
            logger.debug('AUTH_LOGIN: 没有开启用户认证 ....')
            write_log_to_file_and_table(self.username, self.userip, 1, 5)
            write_file(self.userip, '5')
            return

        tactics = self.search_tactics()
        if not tactics:
            logger.debug('AUTH_LOGIN:  all tactics not\
                                      match %s' %(self.userip))
            write_log_to_file_and_table(self.username, self.userip, 1, 2)
            write_file(self.userip, '2')
            return


        def get_oldtactics(oldid):
            oldtactics_sql = 'select * from m_tbusers_authentication_tactics\
                     where id=%s' %(oldid)
            oldtactics = judge_data(oldtactics_sql)[0]
            return oldtactics

        def proc_status():
            # 此处group_name提供给审计日志使用
            sql_ = 'SELECT sGroupName FROM m_tbgroup WHERE id=(SELECT iGroupID FROM m_tbusers WHERE sUserName=?);'
            data = select_one(sql_, self.username)
            group_name = data and data['sGroupName'] or 'Anonymous'
            if self.userip in self.content: # 同一ip再次登录
                oldname, oldid, _ = self.content[self.userip]   # # 用户名 策略号 用户组名
                self.content.update({self.userip: [self.username, tactics['id'], group_name]})
                self.update_online_user()
                if oldid != tactics['id']:  # 再次登录时，匹配策略发生改变
                    oldtactics = get_oldtactics(oldid)
                    oldauthentype = int(oldtactics['sAuthenticationType'])
                    if oldauthentype == 2:
                        self.update_table_userip(oldtactics, oldname,
                                                 self.userip, 'downline')
                    write_log_to_file_and_table(oldname, self.userip, 0, 0,
                                                oldauthentype)
                if int(tactics['sAuthenticationType']) == 2:
                    self.update_table_userip(tactics, self.username,
                                             self.userip, 'online')
            else:
                if int(tactics['iAllowMultiLogin']) == 2:   # 仅允许一人登录
                    for k, v in self.content.items():
                        if tactics['id'] == v[1] and self.username == v[0]:
                            oldtactics = get_oldtactics(tactics['id'])
                            oldauthentype = int(oldtactics['sAuthenticationType'])
                            if oldauthentype == 2:
                                self.update_table_userip(oldtactics, v[0], k, 'downline')
                            self.update_ipset(k, 'del')  # 将上一个用户从ipset中删除
                            self.content.pop(k)
                            self.update_online_user()
                            write_log_to_file_and_table(v[0], k, 0, 0, oldauthentype)
                            # 被挤下线, touch文件通知php告诉用户
                            touchpath = '/tmp/downuser/'
                            if not os.path.exists(touchpath):
                                os.system('mkdir -p {0}'.format(touchpath))
                            touchname = '%s_%s_false' %(v[0], k)  #  username_ip_false
                            os.system('/usr/bin/touch {0}'.format(os.path.join(touchpath, touchname)))
                self.content.update({self.userip: [self.username, tactics['id'], group_name]})
                #print 'content: ', self.content
                self.update_online_user()
                self.update_ipset(self.userip, 'add')
                if int(tactics['sAuthenticationType']) == 2:
                    self.update_table_userip(tactics, self.username, self.userip, 'online')

            write_log_to_file_and_table(self.username, self.userip, 1, 0,
                                        int(tactics['sAuthenticationType']))
            write_file(self.userip, 0)

        # 短信认证(直接增删ipset)
        if self.stype == 'msg':
            proc_status()
            return

        if int(tactics['sAuthenticationType']) == 2: #  本地认证
            u_sql = 'select sIP, iBinIp from m_tbusers where sUserName="%s";'\
                    %(self.username)
            result = search_data(u_sql)
            if not result:
                logger.debug('m_tbusers table not sUserName=%s'\
                                          %(self.username))
                write_log_to_file_and_table(self.username, self.userip, 1, 6, 2)
                write_file(self.userip, '6')
                return
            result = result[0]
            if (result['sIP'] and result['iBinIp'] == 1 and
                result['sIP'] != self.userip):
                write_log_to_file_and_table(self.username, self.userip, 1, 4, 2)
                write_file(self.userip, '4')
                return

        client_path = '/usr/bin/userauth/portal_client'
        cmd_str = '%s -u %s -p %s -a %s -n %d' %(client_path, self.username,
                                                 self.passwd, self.userip,
                                                 int(tactics['id']))
        #print cmd_str
        (status, output) = COMMANDS(cmd_str)
        #print status
        #print output

        if int(status) != 0:
            logger.debug('AUTH_LOGIN:  %s' %(output.decode('utf-8')))
            write_log_to_file_and_table(self.username, self.userip, 1, 1,
                                        int(tactics['sAuthenticationType']))
            write_file(self.userip, '1')
            return

        output = output.split('\n')
        for line in output:
            if line.strip().isdigit() and line.strip() in ['0', '1', '2', '3']:
                output = line.strip()
                break

        # 把验证结果写入管道
        if int(output) == 0:
            proc_status()
        else:
            logger.debug('AUTH_LOGIN:  %s' %(output.decode('utf-8')))
            write_log_to_file_and_table(self.username, self.userip, 1, 1,
                                        int(tactics['sAuthenticationType']))
            write_file(self.userip, str(output))

    def downline(self):
        """ 用户下线 """
        if self.userip in self.content:
            tactics_id = int(self.content[self.userip][1]) # 获取策略id号
            self.content.pop(self.userip) # 删除该登录的用户

            self.update_online_user()
            self.update_ipset(self.userip, 'del')

            tactics_sql = 'select * from m_tbusers_authentication_tactics\
                    where id=%d' %(tactics_id)
            tactics = judge_data(tactics_sql)[0]
            if int(tactics['sAuthenticationType']) == 2: # 本地认证则更新表
                self.update_table_userip(tactics, self.username,
                                         self.userip, 'downline')

            write_log_to_file_and_table(self.username, self.userip, 0, 0,
                                        int(tactics['sAuthenticationType']))


def auth_login(data):
    """ 用户上线 """
    #print data
    ondownline = OnlineDownline(data)
    ondownline.online()

def auth_downline(data):
    """ 用户下线 """

    ondownline = OnlineDownline(data)
    ondownline.downline()

    filename = data['sUserName'] + '_' + data['sIP']
    os.system('/usr/bin/rm -rf /tmp/user/%s' %(filename))

def write_log_to_file_and_table(username, userip, action, status, itype=None):
    """ 登录日志写入表和文件 """

    auth_login_log = '/var/log/authenticate/auth_enticate.log'
    mkdir_file(auth_login_log, 'file')

    login_type = {1: u'上线', 0: u'下线'}
    login_status = {0: u'成功', 1: u'失败', 2: u'找不到认证策略',
                    3: u'找不到认证服务器', 4: u'登录ip与该用户所绑定的ip不相符',
                    5: u'没有开启用户认证', 6: u'找不到该用户'
                   }
    tactics_type = {1: u'不需要认证', 2: u'本地认证', 3: u'外部认证', 4: u'短信认证'}

    frm = '%Y-%m-%d %X'
    nowtime = time.localtime()
    tabletime = int(time.mktime(nowtime))
    logtime = time.strftime(frm, nowtime)

    # 时间 用户名 ip 上/下线 状态 本/外部认证
    if itype:
        log_str = '%s %s %s %s %s %s\n' %(logtime, username, userip,
                                          login_type[action],
                                          login_status[status],
                                          tactics_type[itype])
        l_sql = 'insert into m_tbauthenticate_log (iTime, sUserName, sIP,\
                iAction, iStatus, iType) values(%d, "%s", "%s", %d, %d,\
                %d);'  %(tabletime, username, userip, action, status, itype)
    else:
        log_str = '%s %s %s %s %s\n' %(logtime, username, userip,
                                          login_type[action],
                                          login_status[status])
        l_sql = 'insert into m_tbauthenticate_log (iTime, sUserName, sIP,\
                iAction, iStatus) values(%d, "%s", "%s", %d, %d);'\
                %(tabletime, username, userip, action, status)
    try:
        filepath = codecs.open(auth_login_log, 'a', 'utf-8')
        filepath.write(log_str)
        filepath.close()
    except IOError as err:
        logger.debug(err)
    exs(l_sql)
