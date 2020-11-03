#!/usr/bin/env python
# coding=utf-8

import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
import sqlite3
import time
import json
import sys
import shelve
from collections import defaultdict
import commands
from operator import itemgetter
from itertools import groupby
from threading import Thread
from IPy import IP

from utils.mask_transition import int_to_strmask
from logging import getLogger
from db.mysqlconnect import mysql_connect_dict
from system.ha import init_tenv
from utils.log_logger import rLog_dbg

DBG = lambda x: rLog_dbg('sslvpn', x)

IPTABLES_CMD = '/usr/sbin/iptables -I SSL_VPN_FORWARD -i tun0 -s %s' \
               ' -d %s -p %s -m multiport --dport %s -j RETURN'


ipset2 = [[1, 2], [5, 6], [9, 10], [13, 14], [17, 18],
          [21, 22], [25, 26], [29, 30], [33, 34], [37, 38],
          [41, 42], [45, 46], [49, 50], [53, 54], [57, 58],
          [61, 62], [65, 66], [69, 70], [73, 74], [77, 78],
          [81, 82], [85, 86], [89, 90], [93, 94], [97, 98],
          [101, 102], [105, 106], [109, 110], [113, 114], [117, 118],
          [121, 122], [125, 126], [129, 130], [133, 134], [137, 138],
          [141, 142], [145, 146], [149, 150], [153, 154], [157, 158],
          [161, 162], [165, 166], [169, 170], [173, 174], [177, 178],
          [181, 182], [185, 186], [189, 190], [193, 194], [197, 198],
          [201, 202], [205, 206], [209, 210], [213, 214], [217, 218],
          [221, 222], [225, 226], [229, 230], [233, 234], [237, 238],
          [241, 242], [245, 246], [249, 250], [253, 254]]


def edit_database():
    """
    在数据库/etc/openvpn/openvpn_use.db创建表auth
    """
    try:
        sqlite_conn = sqlite3.connect('/etc/openvpn/openvpn_use.db')
        sqlite_cursor = sqlite_conn.cursor()
        sql_add = """CREATE TABLE IF NOT EXISTS auth(
                     `id` char(128) not null PRIMARY KEY,
                     `name` char(255) not null,
                     `passwd` char(255) not null,
                     `locked` int not null default 0,
                     `dept` char(255)
                     );"""
        sqlite_cursor.execute(sql_add)
        return sqlite_conn, sqlite_cursor
    except sqlite3.Error as e:
        print e.args[0]
        return


def process_data(data, cur, key):
    """
    用户名作为键值，sql的返回值作为值
    """

    data_ret = defaultdict(list)
    try:
        for tmp in data:
            k = tmp.keys()[0]
            v = tmp.values()[0]
            cur.execute(v)
            info = cur.fetchall()
            [data_ret[k].append(str(info1[key])) for info1 in info]
        return data_ret
    except Exception as e:
        print e


def start_stop_iptables(action, port):

    if action == 'start':
        commands.getstatusoutput('/etc/openvpn/open_port.sh %s' % port)
    if action == 'stop':
        commands.getstatusoutput('/etc/openvpn/shdown_port.sh %s' % port)


def user_db(user_data, sqlite_conn, sqlite_cursor):
    """
    用户名及密码写入表auth
    """

    old_info = set([])
    try:
        sqlite_cursor.execute('select * from auth')
        info_in_table = sqlite_cursor.fetchall()
        old_info = set([tmp[1] + ',' + tmp[2] for tmp in info_in_table])
    except Exception as e:
        print e
    new_info = set([tmp['username'] + ',' + tmp['password']
                    for tmp in user_data])
    insert_info, rev_info = new_info - old_info, old_info - new_info
    insert_sql = 'insert into auth(id, name, passwd, locked, dept) ' \
                 'values("%s", "%s", "%s", 0, "0")'
    insert_data = [insert_sql % (
        tmp.split(',')[0], tmp.split(',')[0], tmp.split(',')[1])
        for tmp in insert_info]

    delete_sql = ['delete from auth where name="%s" and passwd="%s"' % (
        tmp.split(',')[0], tmp.split(',')[1]) for tmp in rev_info]
    try:
        [sqlite_cursor.execute(i) for i in delete_sql]
    except Exception as e:
        print e
    try:
        [sqlite_cursor.execute(i) for i in insert_data]
        sqlite_conn.commit()
    except Exception as e:
        print e


def delete_user_iptables(rev_file):
    """
    删除不生效或被删除的用户与之对应的所有规则
    """
    print 'rev_file', rev_file
    db_iptables = shelve.open('user_iptables_shelve')
    for tmp in rev_file:
        for del_iptables in db_iptables[tmp][tmp]:
            print del_iptables
            os.system(del_iptables)
        del db_iptables[tmp]
    for key in db_iptables:
        print db_iptables[key]
    db_iptables.close()


def vpn_status_return(action=None):
    """
    vpn启用状态值返回给界面
    """

    time.sleep(1)
    (status, output) = commands.getstatusoutput('pgrep openvpn')
    with open('/tmp/fifo/sslvpn', 'w') as f:
        if output:
            print >> f, json.dumps({"state": "1"})
        else:
            if action == 'clear':
                print >> f, json.dumps({"state": "2"})
            else:
                print >> f, json.dumps({"state": "0"})


def config_iptables(pro, client_ip, cs_ip, user_iptables_D=[], port_21=False):
    """
     配置用户映射到服务的iptables规则
    """
    if pro == 'ALL':
        iptables_cmd_all = 'iptables -I SSL_VPN_FORWARD -i tun0 -s %s -d %s -j RETURN' % (
            client_ip, cs_ip)
        (status, output) = commands.getstatusoutput(iptables_cmd_all)
        user_iptables_D.append(iptables_cmd_all.replace('I', 'D', 1))

    if pro == 'ICMP':
        iptables_cmd_icmp1 = 'iptables -I SSL_VPN_FORWARD -i tun0 -s %s -d %s -p %s -j RETURN' % (
            client_ip, cs_ip, pro)
        iptables_cmd_icmp2 = 'iptables -I SSL_VPN_FORWARD -i tun0 -s %s -d %s -p %s -j RETURN' % (
            cs_ip, client_ip, pro)
        (status, output) = commands.getstatusoutput(iptables_cmd_icmp1)
        (status, output) = commands.getstatusoutput(iptables_cmd_icmp2)
        user_iptables_D.append(iptables_cmd_icmp1.replace('I', 'D', 1))
        user_iptables_D.append(iptables_cmd_icmp2.replace('I', 'D', 1))

    if port_21:
        iptables_cmd_21 = 'iptables -I SSL_VPN_FORWARD -i tun0 -s %s -p %s --dport 21 -j RETURN' % (
            client_ip, pro)
        iptables_cmd_20 = 'iptables -I SSL_VPN_FORWARD -i tun0 -s %s -p %s --dport 20 -j RETURN' % (
            client_ip, pro)
        iptables_cmd_1024 = 'iptables -I SSL_VPN_FORWARD -i tun0 -s %s -p %s --dport 1024: -m state --state ESTABLISHED,RELATED -j RETURN' % (
            client_ip, pro)
        (status, output) = commands.getstatusoutput(iptables_cmd_21)
        (status, output) = commands.getstatusoutput(iptables_cmd_20)
        (status, output) = commands.getstatusoutput(iptables_cmd_1024)
        user_iptables_D.append(iptables_cmd_21.replace('I', 'D', 1))
        user_iptables_D.append(iptables_cmd_20.replace('I', 'D', 1))
        user_iptables_D.append(iptables_cmd_1024.replace('I', 'D', 1))
    return user_iptables_D


def clear_iptables_file():
    """
    清空规则,文件
    """
    os.system('/usr/sbin/iptables -F SSL_VPN_FORWARD')
    os.system(
        '/usr/sbin/iptables -I SSL_VPN_FORWARD -i tun0 -s 0.0.0.0/0 -d 0.0.0.0/0 -j DROP')
    [os.system('rm -f /etc/openvpn/ccd/%s' % tmp)
     for tmp in os.listdir('/etc/openvpn/ccd/')]

    try:
        os.remove('/usr/local/bluedon/unused_ip_shelve')
        os.remove('/usr/local/bluedon/used_ip_shelve')
        os.remove('/usr/local/bluedon/user_iptables_shelve')
    except Exception as e:
        getLogger('main').info(e)


# 根据掩码生成
def init_dynamic_ip(min_ip, max_ip, mask):
    """
    根据掩码的值来选择ip的生成方式
    """

    if mask != '24':
        min_ips = min_ip.split('.')
        max_ips = max_ip.split('.')
        min_ = int(min_ips[2]) + 1
        max_ = int(max_ips[2]) + 1
        iters = ([m, z[0], z[1]] for m in xrange(min_, max_) for z in ipset2)
    else:
        iters = ([z[0], z[1]] for z in ipset2)
    return iters


class VPN():

    def __init__(self, args=None):
        """
        SSLVPN启动关闭命令集
        """
        self.start_ssl_cmd = [
            'echo 1 >> /proc/sys/net/ipv4/ip_forward',
            '/etc/openvpn/managed  /etc/openvpn/manage.config -d',
            '/etc/openvpn/openvpn --config /etc/openvpn/sslvpn_config_file --daemon',
        ]

        self.stop_ssl_cmd = ['killall openvpn',
                             'killall managed',
                             ]


    def getall(sel, sql):
        cur = mysql_connect_dict()
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        return data

    def _vpn_start_stop(self, args=None):
        """
        VPN开启及关闭
            1.VPN开启关闭前需配置文件/etc/openvpn/sslvpn_config_file
            2.需调用/etc/openvpn/open_port.sh配置相关iptables规则
            3.  关闭vpn, SSL_VPN_FORWARD链只留默认规则，清空用户目录/etc/openvpn/ccd/,
                清iptables规则缓存文件/usr/local/bluedon/tmp/cs_iptables.txt
        """
        getLogger('main').info('VPN start/stop begin .......')
        self.cur = mysql_connect_dict()
        sql_cs_config = {
            "cs_data": 'select cCsServiceAddr,cAddrType from m_tbsslvpncsservice'}
        self.cur.execute(sql_cs_config['cs_data'])
        cs_data = self.cur.fetchall()
        self.cur.close()

        print 'cs_data', type(cs_data)
        # 写配置文件/etc/openvpn/sslvpn_config_file
        if args:
            try:
                base_config_data = json.loads(args)
            except:
                base_config_data = args
            with open('vpn_args.txt', 'w') as f:
                print >> f, base_config_data
            if base_config_data:
                config = {}
                config['zip'] = str(base_config_data['sZip'])
                config['http_port'] = str(base_config_data['sPort'])
                config['vpn_addr'] = base_config_data['vpnAddr']
                ip_mask = base_config_data['sChildNetIp'].split('/')
                config['server_addr'] = ip_mask[0]
                config['server_mask'] = ip_mask[1]
        else:
            [os.system(stop_cmd) for stop_cmd in self.stop_ssl_cmd]
            vpn_status_return('clear')
            return
        try:
            mask_str = int_to_strmask(config['server_mask'])
            push_route_ip = [{'ip': tmp['cCsServiceAddr'], 'mask':'255.255.255.255'}
                             for tmp in cs_data if tmp['cAddrType'] == 1]
            ip_mask = lambda x: IP(x.split('/')[0]).make_net(x.split('/')[1])
            push_route_net = [{'ip': str(ip_mask(tmp['cCsServiceAddr'])).split('/')[0],
                               'mask':str(ip_mask(tmp['cCsServiceAddr']).netmask())}
                              for tmp in cs_data if tmp['cAddrType'] == 2]
            print '$$$'
            push_route = push_route_ip + push_route_net
            print 'push', push_route
            tenv = init_tenv()
            tenv.get_template('sslvpn_config_file').stream(
                mask_str=mask_str,
                push_route=push_route,
                config=config).dump('/etc/openvpn/sslvpn_config_file')
        except Exception as e:
            getLogger('main').info("%s" % e)

        # 启动、关闭vpn

        start_stop_iptables('stop', config['http_port'])
        if str(base_config_data['iStatus']) == '1':
            start_stop_iptables('start', config['http_port'])
            [os.system(stop_cmd) for stop_cmd in self.stop_ssl_cmd]
            for tmp in self.start_ssl_cmd:
                (status, output) = commands.getstatusoutput(tmp)
                getLogger('main').info("%s  %s" % (tmp, status))
        else:
            start_stop_iptables('stop', config['http_port'])
            [os.system(stop_cmd) for stop_cmd in self.stop_ssl_cmd]

        # vpn状态返回
        vpn_status_return()
        getLogger('main').info('VPN start/stop end ..........')

    def get_effective_user(self):
        """
        获取所有有效的用户
        """

        self.cur = mysql_connect_dict()
        now = time.time()
        sql_user = 'select user_id,username,password from m_tbsslvpnusers where ' \
                   'user_state=1 and (is_expire=1 or expire_time>%s)' % now
        self.cur.execute(sql_user)
        user_data = self.cur.fetchall()
        return user_data

    # 重写
    @staticmethod
    def get_ip_format(user_change, ip, mask, db1, f='.'):
        """
        根据输入的ip和mask获取相应的格式
        """
        iplist = ip.split(f)
        str_ = '{}.{}.{}.{}'

        if mask != '24':
            m, x, y = db1[user_change].values()[0].split(',')
            pre_ip = str_.format(iplist[0], iplist[1], m, x.strip())
            fin_ip = str_.format(iplist[0], iplist[1], m, y.strip())
        else:
            x, y = db1[user_change].values()[0].split(',')
            pre_ip = str_.format(iplist[0], iplist[1], iplist[2], x.strip())
            fin_ip = str_.format(iplist[0], iplist[1], iplist[2], y.strip())

        return pre_ip, fin_ip

    def _user_db_staticip(self, user_change):
        """
        用户名及密码入表auth, 为有效用户分配IP
        文件unused_ip_shelve存放待分配的IP, used_ip_shelve存放已分配的IP,
        删除用户, 该用户IP被unused_ip_shelve回收,
        """

        # 参数传入的ip和mask
        # with open('vpn_args.txt', 'r') as f:
        #     for i in f:
        #         base_data = eval(i)
        sql = 'SELECT * FROM m_tbsslvpn_setting;'
        base_data = self.getall(sql)[0]

        print 'base_data', base_data
        min_ip_mask = base_data['sChildNetIp'].split('/')
        mask = min_ip_mask[1]
        vpn_ip = min_ip_mask[0]
        min_ip = base_data['firstip']
        max_ip = base_data['lastip']

        print 'min_ip', min_ip_mask

        # 获取有效的用户, 并且使用sqlite, 将用户账号密码写入/etc/openvpn/openvpn_use.db
        user_data = self.get_effective_user()
        (sqlite_conn, sqlite_cursor) = edit_database()
        user_db(user_data, sqlite_conn, sqlite_cursor)

        # 根据掩码mask来分配ip, unused_ip_shelve存放曾经使用过如今是空闲状态的ip,
        # used_ip_shelve用于存放正在使用的ip, init_dynamic_ip产生一个ip的迭代器
        if not os.path.exists('unused_ip_shelve'):
            shelve.open('unused_ip_shelve').close()
        db = shelve.open('unused_ip_shelve')
        db1 = shelve.open('used_ip_shelve')
        ips = init_dynamic_ip(min_ip, max_ip, mask)
        print 'mask', mask

        # 保证再次启动时能回到之前分配结束的位置
        for i in xrange(len(db) + len(db1)):
            next(ips)

        user_ip = defaultdict(list)
        if user_change:
            try:
                delete_user_iptables(set([user_change]))
                ip = self.get_ip_format(user_change, vpn_ip, mask, db1)
                user_ip[user_change].append(ip)
                user_ip[user_change].append(''.join(
                    [str(i['user_id']) for i in user_data if i['username'] == user_change]))
            except Exception as e:
                getLogger('main').info("%s %s" % (user_change, e))

        # 获取需删除用户及需增加用户
        old_file = set([tmp for tmp in os.listdir('/etc/openvpn/ccd')])
        file_in_table = set([tmp['username'] for tmp in user_data])
        rev_file, new_file = old_file - file_in_table, file_in_table - old_file

        # 删除用户时需做:用户IP放回到"待分配IP",删除文件,删除该用户规则
        for tmp in rev_file:
            db[db1[tmp].keys()[0]] = db1[tmp]
            print db1[tmp]
            del db1[tmp]
            os.remove('/etc/openvpn/ccd/%s' % tmp)
        if rev_file:
            delete_user_iptables(rev_file)

        # 增加用户,需为用户分配ip,并配置文件/etc/openvpn/ccd/用户名
        for i, tmp in enumerate(new_file):
            user_file = '/etc/openvpn/ccd/%s' % tmp
            f = open(user_file, 'w')
            db_set = set(db)

            ip_str = u' '
            # 只有unused_ip_shelve为空时才从生成器里生出一个ip
            if len(db_set) == 0:
                try:
                    ip_str = str(next(ips)).replace('[', '').replace(']', '')
                    print 'ip', ip_str
                except StopIteration:
                    getLogger('main').info('all ips were used!')
            else:
                ip_str = str(db_set.pop())
            db1[tmp] = {ip_str: ip_str}

            print 'tmp', tmp

            pre_ip, fin_ip = self.get_ip_format(tmp, vpn_ip, mask, db1)
            user_ip[tmp].append(pre_ip)
            user_ip[tmp].append(''.join([str(i['user_id'])
                                         for i in user_data if i['username'] == tmp]))

            push_ip = "ifconfig-push {} {} ".format(pre_ip, fin_ip)
            print >> f, push_ip

            f.close()
        print '*****len db:', len(db)
        print '*****len db1:', len(db1)
        db.close()
        db1.close()
        self.user_ip = user_ip

    def _user_iptables(self, user_change=None):
        """
        通过表间关系，根据用户-->角色-->服务，找用户对应的所有服务
        根据服务协议分类,将同一协议的所有端口,使用multiport配置在一条iptables规则上
        icmp协议需配置来回规则,tcp21端口,需增加配置20端口及1024端口相关规则
        """
        self._user_db_staticip(user_change)
        #user_role = defaultdict(list)

        # 获取用户所有服务
        sql_user_role = [{k: 'select role_id from m_tbsslvpnusers_role where user_id = "%s"' % v[
            1]} for k, v in self.user_ip.items()]
        user_role = process_data(sql_user_role, self.cur, 'role_id')

        sql_user_groupid = [
            {
                k: 'select group_id from m_tbsslvpnusers_group where user_id = "%s"' %
                v[1]} for k,
            v in self.user_ip.items()]
        for tmp in sql_user_groupid:
            k = tmp.keys()[0]
            v = tmp.values()[0]
            self.cur.execute(v)
            info = self.cur.fetchall()
            group_id = []
            if info:
                for tmp in info:
                    group_id.append(str(tmp['group_id']))
                sql_group_role = 'select role_id from m_tbsslvpngroup_role where group_id in {}'.format(
                    str(group_id).replace('[', '(').replace(']', ')'))
                self.cur.execute(sql_group_role)
                info1 = self.cur.fetchall()
                for tmp in info1:
                    user_role[k].append(str(tmp['role_id']))

        sql_role_cs = [{k: "select server_id from m_tbsslvpnrole_server where role_id in {}".format(
            str(v).replace('[', '(').replace(']', ')'))} for k, v in user_role.items()]
        user_server_id = process_data(sql_role_cs, self.cur, 'server_id')

        db_iptables = shelve.open('user_iptables_shelve')

        # 配置用户所有服务规则
        for k, v in user_server_id.items():
            user_iptables = {}
            client_ip = self.user_ip[k][0]
            user_iptables_D = []
            for server_id in v:
                cs_pro_port_ip = 'select type,port,port_message from m_tbsslvpncsservice_port where server_id = "%s"' % server_id
                self.cur.execute(cs_pro_port_ip)
                pro_port_ip = self.cur.fetchall()
                pro_port_ip = list(tuple(pro_port_ip))
                pro_port_ip.sort(key=itemgetter('type'))
                #cs_ip = cs_ip.split('/')[0]
                rule_pro_port = {}

                # 以协议进行分组
                for pro, item in groupby(pro_port_ip, key=itemgetter('type')):
                    if pro:
                        flag_zone = False
                        tmp = []
                        for i in item:
                            cs_ip = IP(i['port_message'])
                            if i['port'] == 0:
                                flag_zone = True
                            else:
                                tmp.append(str(i['port']))
                        rule_pro_port['pro'] = pro

                        # 配置协议为all,icmp规则
                        user_iptables_D = config_iptables(
                            pro=pro, client_ip=client_ip, cs_ip=cs_ip, user_iptables_D=user_iptables_D)

                        # 这里配置有端口,协议为tcp,udp的规则
                        if tmp:
                            rule_pro_port['port'] = ','.join(tmp)
                            iptables_cmd = IPTABLES_CMD % (client_ip, cs_ip, rule_pro_port[
                                                           'pro'], rule_pro_port['port'])
                            (status, output) = commands.getstatusoutput(
                                iptables_cmd)
                            user_iptables_D.append(
                                iptables_cmd.replace('I', 'D', 1))
                            if rule_pro_port['pro'] == 'TCP':
                                if set(['21']) & set(tmp):
                                    user_iptables_D = config_iptables(
                                        pro=pro,
                                        client_ip=client_ip,
                                        cs_ip=cs_ip,
                                        user_iptables_D=user_iptables_D,
                                        port_21=True)

                        # 此处配置没有端口，协议为tcp、udp的规则
                        if flag_zone and pro != 'ICMP' and pro != 'ALL':
                            iptables_cmd1 = 'iptables -I SSL_VPN_FORWARD -i tun0 -s %s -d %s -p %s -j RETURN' % (
                                client_ip, cs_ip, rule_pro_port['pro'])
                            (status, output) = commands.getstatusoutput(
                                iptables_cmd1)
                            user_iptables_D.append(
                                iptables_cmd1.replace('I', 'D', 1))
            user_iptables[k] = user_iptables_D
            db_iptables[k] = user_iptables
        db_iptables.close()
        self.cur.close()

    def _run(self, user_change=None):
        while True:

            (status, output) = commands.getstatusoutput('pgrep openvpn')
            if output:
                self._user_iptables(user_change)
                if len(user_change):
                    break
            else:
                (sqlite_conn, sqlite_cursor) = edit_database()
                sqlite_cursor.execute("delete from auth")
                clear_iptables_file()
                break
            time.sleep(3)


def recover(action):

    clear_iptables_file()

    if action == 'reset_recover':
        print 'reset_recover'

    if action == 'boot_recover':
        try:
            with open('/etc/keepalived/status.conf', 'r') as fp:
                line = fp.read().strip()
            status = line.lower()
        except IOError as e:
            print('open /etc/keepalived/status.conf error')
            print(e)
            status = 'backup'

        cur = mysql_connect_dict()
        cur.execute('select * from m_tbsslvpn_setting')
        sslvpn_baseconfig = cur.fetchall()
        sslvpn_baseconfig = sslvpn_baseconfig and sslvpn_baseconfig[0] or None
        args = sslvpn_baseconfig and json.dumps(sslvpn_baseconfig) or None
        DBG(args)
        DBG(status)
        vpn = VPN()
        cur.close()
        # check ha role, vpn will only start when in master mode
        if status == 'master':
            time.sleep(5)
            DBG('starting sslvpn')
            DBG(args)
            vpn._vpn_start_stop(args)
            (status, output) = commands.getstatusoutput('pgrep openvpn')
            if output:
                vpn._user_iptables()
            pass
        else:
            # kill vpn if ha role is backup
            DBG('stopping sslvpn')
            [os.system(stop_cmd) for stop_cmd in vpn.stop_ssl_cmd]


if __name__ == "__main__":
    if sys.argv[1] == 'boot_recover' or sys.argv[1] == 'reset_recover':
        recover(sys.argv[1])
        sys.exit(0)

    vpn = VPN()
    t = Thread(target=vpn._run, args=(sys.argv[1],))
    t.start()
