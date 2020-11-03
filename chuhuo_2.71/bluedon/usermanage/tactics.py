#!/usr/bin/env python
# coding=utf-8

"""
modify log:
    2016-11-4:
        1、用户认证策略
"""


import os
import sys
import json
import codecs
import base64

from IPy import IP

from db.config import search_data, mkdir_file, execute_sql
from db.config1 import execute_sql as exs
from utils.logger_init import logger_init
from core.exceptions import ArgumentError
from core.setting import CMD_IPTABLES, LOG_BASE_PATH, CMD_SED
from objectdefine.ip_range import get_ip


LOG_PATH = os.path.join(LOG_BASE_PATH, 'tactics.log')
LOG_NAME = 'TACTICS'

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

def ip_ipgroup(vtype, vid, sdtype):
    """
    args:
        vtype: ip(1)或ip组(2)
        vid: 相关连ip/ip组表的id
        sdtype: 源地址(s), 目的地址(d)
    return:
        istr: 拼接后的字符串
    """

    type_dict = {
        's': {
            'onlyip': ' -s %s ',
            'iprange': ' -m iprange --src-range %s-%s ',
            'ipgroup': ' -m set --match-set %s src '
            },
        'd': {
            'onlyip': ' -d %s ',
            'iprange': ' -m iprange --dst-range %s-%s ',
            'ipgroup': ' -m set --match-set %s dst '
            }
        }

    istr = u' '
    if vtype == '1':        # ip
        ip_sql = 'select sAddress, sNetmask, sAddtype from \
                m_tbaddress_list where id=%d;' %(vid)
        data = search_data(ip_sql)
        if not data:
            logger.info('m_tbaddress_list table not id %d' %(vid))
            raise ArgumentError
        data = data[0]
        if str(data['sAddtype']).strip() == '1':        # ip和掩码形式
            if data['sAddress'].endswith('.0'):
                if '.' not in data['sNetmask']:
                    addr = '%s/%s' %(data['sAddress'], data['sNetmask'])
                else:
                    addr = IP('%s/%s' %(data['sAddress'], data['sNetmask']),
                            make_net=True).strNormal(1)
            else:
                addr = data['sAddress']
            istr = type_dict[sdtype]['onlyip'] %(addr)
        elif str(data['sAddtype']).strip() == '2':        # ip段
            istr = type_dict[sdtype]['iprange']
            istr = istr %(data['sAddress'], data['sNetmask'])
    elif vtype == '2':     # ip组
        ipg_sql = 'select HideID from m_tbaddressgroup where id=%d;' %(vid)
        data = search_data(ipg_sql)
        if not data:
            logger.info('m_tbaddressgroup table not id %d' %(vid))
            raise ArgumentError
        data = data[0]
        istr = type_dict[sdtype]['ipgroup'] %(data['HideID'])
    return istr


def set_iptables_fw_nat_auth():
    """ 设置FW_NAT_AUTH链规则 """

    os.system('%s -t nat -F FW_NAT_AUTH' %(CMD_IPTABLES))

    lst = ['/usr/sbin/iptables -t nat -A FW_NAT_AUTH -m set --match-set authed_set src -g FW_NAT_AUTH_TA1',
           '/usr/sbin/iptables -t nat -A FW_NAT_AUTH -m set --match-set authed_set dst -g FW_NAT_AUTH_TA1',
           '/usr/sbin/iptables -t nat -A FW_NAT_AUTH -m set --match-set auth_local_mode src -g FW_NAT_AUTH_TA1',
           '/usr/sbin/iptables -t nat -A FW_NAT_AUTH -m set --match-set auth_local_mode dst -g FW_NAT_AUTH_TA1']
    for item in lst:
        os.system(item)

    cmd_443 = '/usr/sbin/iptables -t nat -A FW_NAT_AUTH {0} -i {1} -p tcp -m\
               multiport --dports 443 -j DNAT  --to {2}:4443'
    cmd_6666 = '/usr/sbin/iptables -t nat -A FW_NAT_AUTH {0} -i {1} -p tcp -m\
                multiport --dports 80,8080 -j DNAT  --to {2}:6666'

    # 查找所有策略推送ip并设置相应iptables
    auth_sql = 'select sTuisongIp, sAuthNetport, iRangeType, sRange from m_tbusers_authentication_tactics\
                where iStatus=1 and sAuthNetport !="" and sAuthenticationType != "1" order by iPriority desc;'
    results = judge_data(auth_sql, flag=False)
    for result in results:
        addr = result.get('sTuisongIp', '')
        port = result.get('sAuthNetport', '')
        if port:
            if '/' in addr:
                addr = addr.split('/')[0]
            src_str = ip_ipgroup(str(result['iRangeType']), int(result['sRange']), 's')
            os.system(cmd_443.format(src_str, port, addr))
            os.system(cmd_6666.format(src_str, port, addr))
        else:
            logger.debug('not search network ip is {0}'.format(addr))

def set_iptables():
    """ 设置iptables """
    # 先清空相应链的iptables, 再从新设置
    os.system('%s -t nat -F FW_NAT_AUTH_TA' %(CMD_IPTABLES))
    os.system('%s -t filter -F FW_FILTER_AUTH_TA' %(CMD_IPTABLES))

    cmd_iptables_dict = {
        '1': {'onlyip': ['%s -t nat -%s FW_NAT_AUTH_TA -s %s -j FW_NAT_AUTH',
                         '%s -t filter -%s FW_FILTER_AUTH_TA\
                         -s %s -j FW_FILTER_AUTH'],
              'ipgroup': ['%s -t nat -%s FW_NAT_AUTH_TA -m set --match-set\
                          %s src -j FW_NAT_AUTH',
                          '%s -t filter -%s FW_FILTER_AUTH_TA -m set\
                          --match-set %s src -j FW_FILTER_AUTH'],
              'iprange': ['%s -t nat -%s FW_NAT_AUTH_TA -m iprange\
                          --src-range %s -j FW_NAT_AUTH',
                          '%s -t filter -%s FW_FILTER_AUTH_TA -m iprange\
                          --src-range %s -j FW_FILTER_AUTH'],
              'all': ['%s -t nat -%s FW_NAT_AUTH_TA -j FW_NAT_AUTH',
                      '%s -t filter -%s FW_FILTER_AUTH_TA -j FW_FILTER_AUTH']
             },
        '0': {'onlyip': ['%s -t nat -%s FW_NAT_AUTH_TA -s %s -j RETURN',
                         '%s -t filter -%s FW_FILTER_AUTH_TA -s %s -j RETURN',
                         '%s -t filter -%s FW_FILTER_AUTH_TA -d %s -j RETURN'],
            'ipgroup': ['%s -t nat -%s FW_NAT_AUTH_TA -m set --match-set\
                        %s src -j RETURN',
                        '%s -t filter -%s FW_FILTER_AUTH_TA -m set\
                        --match-set %s src -j RETURN',
                        '%s -t filter -%s FW_FILTER_AUTH_TA -m set\
                        --match-set %s dst -j RETURN'],
            'iprange': ['%s -t nat -%s FW_NAT_AUTH_TA -m iprange\
                        --src-range %s -j RETURN',
                        '%s -t filter -%s FW_FILTER_AUTH_TA -m iprange\
                        --src-range %s -j RETURN',
                        '%s -t filter -%s FW_FILTER_AUTH_TA -m iprange\
                        --dst-range %s -j RETURN'],
            'all': ['%s -t nat -%s FW_NAT_AUTH_TA -j RETURN',
                    '%s -t filter -%s FW_FILTER_AUTH_TA -j RETURN']
             }
    }

    a_sql = 'select * from m_tbusers_authentication_tactics where \
            iStatus=1 order by iPriority desc;'
    results = judge_data(a_sql, flag=False)
    modify_iptables(results, cmd_iptables_dict)

def modify_iptables(datas, cmd_iptables_dict):
    """
    设置相应的iptables
    args:
        datas: 所有策略的记录集
    """

    action = 'A'
    flag = False
    for data in datas:
        if str(data['sAuthenticationType']) == '1':	# 不需要认证
            authen = '0'
        else:
            authen = '1'

        ips, ipsets, itype = get_ips(data)

        items = cmd_iptables_dict[authen][itype]

        if ipsets == '0.0.0.0/0':
            for item in cmd_iptables_dict[authen]['all']:
                cmd = item %(CMD_IPTABLES, action)
                os.system(cmd)
            flag = True
        else:
            for item in items:
                cmd = item %(CMD_IPTABLES, action, ipsets)
                os.system(cmd)
    if not flag:
        os.system('%s -t filter -D FW_FILTER_AUTH_TA -j FW_FILTER_AUTH'\
                  %(CMD_IPTABLES))
        os.system('%s -t filter -A FW_FILTER_AUTH_TA -j FW_FILTER_AUTH'\
                  %(CMD_IPTABLES))

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


class AuthTactics(object):
    """ 认证策略
    内部认证
    """

    def __init__(self, data):
        """ 初始化 """

        self.data = data
        self.file_path = '/etc/userauth/auth_tactics.conf'
        mkdir_file(self.file_path, 'file')
        set_iptables()
        set_iptables_fw_nat_auth()

    def add(self):
        """ 把认证策略写入配置文件 """

        # 如果是不需要认证, 则直接return
        if int(self.data['iStatus']) == 0:
            return False

        str_list = []
        # id
        id_str = 'id:%d' %(int(self.data['id']))
        str_list.append(id_str)

        # 认证方式
        authenticate_type_str = 'approvetype:%s'\
                %(str(self.data['sAuthenticationType']))
        str_list.append(authenticate_type_str)

        if str(self.data['sAuthenticationType']) == '1':	# 不需要认证
            pass
        elif str(self.data['sAuthenticationType']) == '2':	# 本地认证
            authtype_str = 'authtype:%s' %(str(self.data['sLocalAuthentication']))
            str_list.append(authtype_str)

        elif str(self.data['sAuthenticationType']) == '3':	# 外部认证
            # url重定向
            if self.data['sURLRedirect']:
                url_str = 'urlredirect:%s' %(str(self.data['sURLRedirect']))
                str_list.append(url_str)
            # 认证服务器id
            authserver_str = 'authserverid:%d' %(int(self.data['iAuthenticationServer']))
            str_list.append(authserver_str)

        # 写到ldap配置文件
        lines = ' '.join(str_list)
        lines = lines + '\n'
        try:
            filepath = codecs.open(self.file_path, 'a', 'utf-8')
            filepath.write(lines)
        except IOError as err:
            logger.debug(err)
        finally:
            filepath.close()


    def delete(self):
        """ 删除认证策略 """

        # 删除配置文件中相应的认证策略
        lines = []
        try:
            filepath = codecs.open(self.file_path, 'r', 'utf-8')
            lines = filepath.readlines()
        except IOError as err:
            logger.debug(err)
        finally:
            filepath.close()

        if lines:
            for line in lines:
                if line.startswith(u'id:%d ' %(int(self.data['id']))):
                    lines.remove(line)
                    break

            lines_str = ''.join(lines)
            try:
                filepath = codecs.open(self.file_path, 'w', 'utf-8')
                filepath.write(lines_str)
            except IOError as err:
                logger.debug(err)
            finally:
                filepath.close()




class OutAuthenticate(object):
    """ 外部认证 """

    def __init__(self, data):
        """ 初始化 """

        self.data = data
        self.file_path = '/etc/userauth/external_auth.conf'
        mkdir_file(self.file_path, 'file')

    def add(self):
        """ 把ldap或radius写到配置文件 """

        if int(self.data['iStatus']) == 0:
            return False

        str_list = []
        # id
        id_str = 'serverid:%d' %(int(self.data['id']))
        str_list.append(id_str)

        # 认证端口号
        if self.data['sAuthenticationPort']:
            port_str = 'port:%s' %(str(self.data['sAuthenticationPort']))
            str_list.append(port_str)

        # 超时重传时间
        if self.data['iTimeOutResent']:
            time_str = 'resend_timeout:%s' %(str(self.data['iTimeOutResent']))
            str_list.append(time_str)

        # 认证方式
        if self.data['sAuthenticationType']:
            type_str = 'authtype:%s' %(str(self.data['sAuthenticationType']))
            str_list.append(type_str)

        if self.data['sType'].upper() == 'LDAP':    # ldap
            str_list.insert(0, 'LDAP')
            # 服务ip
            if self.data['sServerIP']:
                serverip_str = 'serverip:%s' %(str(self.data['sServerIP']))
                str_list.insert(2, serverip_str)
            if self.data['sDnMode']:
                dn_str = 'dn:%s' %(str(self.data['sDnMode']))
                str_list.append(dn_str)
            if self.data['sBaseName']:
                base_name_str = 'standard_name:%s' %(str(self.data['sBaseName']))
                str_list.append(base_name_str)
            if self.data['sUserName']:
                user_name_str = 'admin_name:%s' %(str(self.data['sUserName']))
                str_list.append(user_name_str)
            if self.data['sPassword']:
                password = base64.b64decode(self.data['sPassword'])
                pw_str = 'passwd:%s' %(password)
                str_list.append(pw_str)
        elif self.data['sType'].upper() == 'RADIUS':    # radius
            str_list.insert(0, 'RADIUS')
            # 服务ip
            if self.data['sServerIP']:
                serverip_str = 'serverip:%s' %(str(self.data['sServerIP']))
                str_list.insert(2, serverip_str)

            if self.data['sAuditPort']:
                audit_port_str = 'audit_port:%s' %(str(self.data['sAuditPort']))
                str_list.append(audit_port_str)
            if self.data['sShareKey']:
                pw_str = 'shared_pw:%s' %(str(self.data['sShareKey']))
                str_list.append(pw_str)

        lines = ' '.join(str_list)
        lines = lines + '\n'
        try:
            filepath = codecs.open(self.file_path, 'a', 'utf-8')
            filepath.write(lines)
        except IOError as err:
            logger.debug(err)
        finally:
            filepath.close()

    def delete(self):
        """ 删除外部认证 """

        lines = []
        try:
            filepath = codecs.open(self.file_path, 'r', 'utf-8')
            lines = filepath.readlines()
        except IOError as err:
            logger.debug(err)
        finally:
            filepath.close()

        if not lines:
            return False

        if self.data['sType'].upper() == 'RADIUS':    # radius
            type_str = 'RADIUS'
        elif self.data['sType'].upper() == 'LDAP':    # ldap
            type_str = 'LDAP'

        for line in lines:
            startword = '%s serverid:%d ' %(type_str, int(self.data['id']))
            if line.startswith(startword):
                lines.remove(line)
                break

        lines_str = ''.join(lines)
        try:
            filepath = codecs.open(self.file_path, 'w', 'utf-8')
            filepath.write(lines_str)
        except IOError as err:
            logger.debug(err)
        finally:
            filepath.close()


def on_off(action):
    """ 用户认证开/关 """

    mkdir_file('/etc/cron.d/user_downline', 'file', mod=644)
    os.system('/usr/bin/chmod 644 /etc/cron.d/user_downline')

    if action == '0':
        # 关闭 用户认证-短信认证
        os.system('/usr/sbin/iptables -D FWINPUT -p tcp --dport 9999 -j ACCEPT')
        os.system('/usr/sbin/iptables -D FWINPUT -p tcp --sport 9999 -j ACCEPT')

        del_iptables = '/usr/bin/userauth/clean_iptables.sh'
        os.system(del_iptables)

        os.system('/usr/bin/killall -9 user_attestation')  # 推送认证页进程

        # 清空已上线/待删除的用户文件
        online_del_users = ['online_users', 'del_users']
        for item in online_del_users:
            path = os.path.join('/usr/local/bluedon/conf/', item)
            if os.path.exists(path):
                os.system('%s -i ""d %s' %(CMD_SED, path))
            else:
                mkdir_file(path, 'file')

        # 删除用户下线的crontab定时任务
        os.system(r'%s -i "/%s\>/"d %s'
                  %(CMD_SED, 'user_downline.py', '/etc/cron.d/user_downline'))  # 用户下线
        os.system(r'%s -i "/%s\>/"d %s'
                  %(CMD_SED, 'del_file.py', '/etc/cron.d/user_downline'))  # 删除 /tmp/fifo下的rz* 文件

        # 清空用户表中(绑定ip/未绑定ip)所有上线的用户
        u_sql = 'update m_tbusers set sIP="", iOnline=0 where iBinip=0;'
        s_sql = 'update m_tbusers set iOnline=0 where iBinip=1;'
        execute_sql(u_sql)
        execute_sql(s_sql)
    elif action == '1':
        add_iptables = '/usr/bin/userauth/set_auth_iptables.sh'
        os.system(add_iptables)

        server_path = '/usr/bin/userauth/start_auth_server.sh' # 启动用户认证后台进程
        os.system(server_path)

        os.system('/usr/sbin/service radiusd restart')

        # 开启 用户认证-短信认证，向百信通推消息
        os.system('/usr/sbin/iptables -A FWINPUT -p tcp --dport 9999 -j ACCEPT')
        os.system('/usr/sbin/iptables -A FWINPUT -p tcp --sport 9999 -j ACCEPT')
        # 增加用户下线的crontab定时任务
        with open('/etc/cron.d/user_downline', 'a') as filepath:
            line_1 = '*/1 * * * * root /usr/bin/python\
                    /usr/local/bluedon/usermanage/user_downline.py\n'
            line_2 = '0 21 * * * root /usr/bin/python\
                    /usr/local/bluedon/usermanage/del_file.py\n'
            filepath.write(line_1)
            filepath.write(line_2)


def main(action):
    """ 主函数 """

    # 删除认证策略
    auth_tactics_path = '/etc/userauth/auth_tactics.conf'
    mkdir_file(auth_tactics_path, 'file')
    auth_cmd = '%s -i ""d %s' %(CMD_SED, auth_tactics_path)
    os.system(auth_cmd)
    # 删除外部认证
    out_authenticate_path = '/etc/userauth/external_auth.conf'
    mkdir_file(out_authenticate_path, 'file')
    out_cmd = '%s -i ""d %s' %(CMD_SED, out_authenticate_path)
    os.system(out_cmd)

    if action == 'reboot':
        # 认证策略
        a_sql = 'select * from m_tbusers_authentication_tactics where iStatus=1;'
        a_datas = judge_data(a_sql, flag=False)
        for item in a_datas:
            authtactics = AuthTactics(item)
            authtactics.add()
        # 外部认证
        o_sql = 'select * from m_tbusers_out_authentication;'
        o_datas = judge_data(o_sql, flag=False)
        for item in o_datas:
            outauthenticate = OutAuthenticate(item)
            outauthenticate.add()
			
def authentication_on_off(motion):
    # 检查是否启用用户认证
    on_off('0')
    if motion == 'init':  # 恢复出厂
        return
    on_off_sql = 'select sValue from m_tbconfig where sName="UserStrategy";'
    result = judge_data(on_off_sql)
    result = result[0]['sValue']
    result = json.loads(result)
    action = str(result.get('iTurnOn', '0'))
    if action == '1':
        on_off(action)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.debug('more args (eg: python -m usermanage.tactics reboot/init)')
    elif sys.argv[1] in ['init', 'reboot']:
        main(sys.argv[1])
    elif sys.argv[1] == 'onoff_init':
        authentication_on_off('init')
    elif sys.argv[1] == 'onoff_reboot':
        authentication_on_off('reboot')
