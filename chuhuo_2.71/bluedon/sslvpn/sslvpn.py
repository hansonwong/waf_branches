#!/usr/bin/env python
# coding=utf-8

import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
import sqlite3
from datetime import datetime
import time
import json
import shelve
import re
from threading import Thread
from commands import getstatusoutput
from collections import defaultdict
import base64

from db.mysqlconnect import execute_sql
from db.mysql_db import select
from utils.mask_transition import int_to_strmask
from objectdefine.ip_range import deal_ip
from system.ha import init_tenv
from utils.log_logger import rLog_dbg, rLog_err
DBG = lambda x: rLog_dbg('sslvpn', x)
ERR = lambda x: rLog_err('sslvpn', x)
reload(sys)
sys.setdefaultencoding("utf-8")

# dir
DB_USER = '/usr/local/sslvpn-1.0/sql-management/bd-sslvpn-user.db'
CCD = '/usr/local/sslvpn-1.0/sslvpn-main-components/ccd/'
CPD = '/usr/local/sslvpn-1.0/app-rsc/cpd/'
SSL_CONFIG = '/usr/local/sslvpn-1.0/sslvpn-main-components/server_config/bd-sslvpn-config'
APP_CONFIG = '/usr/local/sslvpn-1.0/app-rsc/app.config'
PIC = '/Data/apps/wwwroot/firewall/apps/admin/themes/default/skin/blue/images/sslvpn/'

# cmd
SSL_CMD = '/usr/sbin/iptables -I SSL_VPN_FORWARD -i tun0 -s {}' \
    ' -d {} -p tcp -m multiport --dport {} -j RETURN -w'
OTHER = SSL_CMD.replace('tcp', '{}')
ALL_PORT = '/usr/sbin/iptables -I SSL_VPN_FORWARD -i tun0 -s {} -d {} -p {} -j RETURN -w'

# ip加端口的格式
regx_url = r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(' \
    r'?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))(:\d+)?'
regx_ip = r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(' \
    r'?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'

ipset = [[1, 2], [5, 6], [9, 10], [13, 14], [17, 18],
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


def init_dynamic_ip(min_ip, max_ip, mask):
    """
    min_ip,max_ip是传进来的可选ip范围
    根据掩码的值来选择ip的生成方式,min_和max_加１是为了保证不会取到保留ip
    """

    if mask != '24':
        min_ips = min_ip.split('.')
        max_ips = max_ip.split('.')
        min_ = int(min_ips[2]) + 1
        max_ = int(max_ips[2]) + 1
        iters = ([m, z[0], z[1]] for m in xrange(min_, max_) for z in ipset)
    else:
        iters = ([z[0], z[1]] for z in ipset)
    return iters


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


def start_stop_iptables(action, port):
    """根据传入的action来执行对应的start和stop的shell脚本"""
    script = 'start.sh' if action == 'start' else 'stop.sh'
    cmd = '/usr/local/sslvpn-1.0/{} {}'
    status, output = getstatusoutput(cmd.format(script, port))
    DBG('status %s, cmd %s, output %s' % (status, cmd, output))


# 规则处理
def vpn_status_return(action=None):
    """vpn启用状态值返回给界面"""
    (status, output) = getstatusoutput('pgrep bd-sslvpn')
    with open('/tmp/fifo/sslvpn', 'w') as fw:
        if output:
            text = {"state": "1"}
        else:
            text = {"state": "2"} if action == 'clear' else {"state": "0"}
        fw.write(json.dumps(text))


def clear_iptables_file():
    """
    清空规则,文件
    """
    os.system('/usr/sbin/iptables -F SSL_VPN_FORWARD')
    os.system(
        '/usr/sbin/iptables -I SSL_VPN_FORWARD -i tun0 -s 0.0.0.0/0 -d 0.0.0.0/0 -j DROP')
    for tmp in os.listdir(CCD):
        try:
            os.system('rm -f {}{}'.format(CCD, tmp))
        except:
            pass
    try:
        os.remove('/usr/local/bluedon/unused_ip_shelve')
        os.remove('/usr/local/bluedon/used_ip_shelve')
        os.remove('/usr/local/bluedon/user_iptables_shelve')
    except Exception as e:
        DBG(e)


def delete_user_iptables(rev_file):
    """
    删除不生效或被删除的用户与之对应的所有规则
    """
    db_iptables = shelve.open('user_iptables_shelve')
    for tmp in rev_file:
        for del_iptables in db_iptables[tmp][tmp]:
            os.system(del_iptables)
        del db_iptables[tmp]
    for key in db_iptables:
        print db_iptables[key]
    db_iptables.close()


# *****协议对应的规则*****
def all_icmp(s_ip, d_ip, all_icmp):
    """端口类型为所有或icmp"""
    iptables = []
    cmd = all_icmp.format(s_ip, d_ip)
    (status, output) = getstatusoutput(cmd)
    DBG('status: %s cmd:%s output %s' % (status, cmd, output))
    iptables.append(cmd.replace('-I', '-D', 1))
    return iptables


def tcp_udp(s_ip, d_ip, pro, port):
    """端口类型为tcp或udp"""
    del_cmd = []
    DBG('tcp_udp %s %s %s %s' % (s_ip, d_ip, pro, port))
    p = port.split(',')
    if ('21' in p or '20' in p):
        ftp_ = ftp(s_ip, pro)
        del_cmd = ftp_
    elif port == '0':  # 不选端口代表所有
        cmd = ALL_PORT.format(s_ip, d_ip, pro)
        (status, output) = getstatusoutput(cmd)
        del_cmd.append(cmd.replace('-I', '-D', 1))
        DBG('status: %s cmd:%s output %s' % (status, cmd, output))
    else:
        cmd = OTHER.format(s_ip, d_ip, pro, port)
        (status, output) = getstatusoutput(cmd)
        del_cmd.append(cmd.replace('-I', '-D', 1))
        DBG('status: %s cmd:%s output %s' % (status, cmd, output))
    return del_cmd


def ftp(s_ip, pro):
    """
    当端口为21或20时为ftp协议，需要配置一下规则
    """
    iptables = []
    port = 'iptables -I SSL_VPN_FORWARD -i tun0 -s {} -p {} --dport {} -j ACCEPT'
    cmd_20 = port.format(s_ip, pro, '20')
    cmd_21 = port.format(s_ip, pro, '21')
    cmd_1024 = port.format(
        s_ip, pro, '1024: -m state --state ESTABLISHED,RELATED')

    try:
        getstatusoutput(cmd_20)
        getstatusoutput(cmd_21)
        getstatusoutput(cmd_1024)
    except Exception as e:
        ERR('ftp iptables not effective {}'.format(e))
    iptables.append(cmd_20.replace('-I', '-D', 1))
    iptables.append(cmd_21.replace('-I', '-D', 1))
    iptables.append(cmd_1024.replace('-I', '-D', 1))
    return iptables

# *****协议对应的规则*****

# *****写配置文件*****


def bd_sslvpn_config(config):
    """写配置文件bd-sslvpn-config"""
    try:
        mask_str = int_to_strmask(config['server_mask'])
        port = config['sPort'] if config['sPort'] != '' else '7000'
        tenv = init_tenv()
        tenv.get_template('bd-sslvpn-config').stream(port=port, mask_str=mask_str, config=config).dump(
            '/usr/local/sslvpn-1.0/sslvpn-main-components/server_config/bd-sslvpn-config')
    except Exception as e:
        ERR('Faild to write bd-sslvpn-config. Raise {}'.format(e))


def url(urls, url_type):
    ip_port = re.search(regx_url, urls)
    port = server = ''
    defult_port = '443' if url_type == 2 else '80'
    try:
        ip_port = ip_port.group().split(':')
        port = ip_port[1] if len(ip_port) == 2 else defult_port
        server = ip_port[0] if len(ip_port) > 0 else ''
    except Exception as e:
        ERR(e)
        pass
    return server, port


def all_app_config():
    """写配置app.config"""
    # 查询出所有的服务
    DBG('all_app_config')
    service_sql = 'SELECT * FROM m_tbbdvpn_ssl_service'
    cs_data = execute_sql(service_sql)
    apps = []
    for service in cs_data:
        app = {}
        if service['sUrl']:
            try:
                server, port = url(service['sUrl'], service['iUrlType'])
                app['port'] = port
                app['name'] = str(service['sName'])
                http_pre = 'http://' if str(service['iUrlType']
                                            ) == '1' else 'https://'
                app['vlocation'] = app['location'] = http_pre + service['sUrl']
                app['server'] = server
                app['description'] = service['sMark'] if service['sMark'] else ''
                icon = service['sIcon'] if service['sIcon'] else 'logo_icon.png'
                with open(PIC + icon, 'rb') as fw:
                    app['icon'] = base64.encodestring(fw.read())
                if str(service['iDefaultIcon']) == '1':
                    app['icon'] = ''
                apps.append(app)
            except Exception as e:
                ERR('sslvpn service parameter invalid {}'.format(e))
    try:
        tenv = init_tenv()
        tenv.get_template('bd-sslvpn-app-config').stream(
            apps=apps).dump('/usr/local/sslvpn-1.0/app-rsc/app.config')
    except Exception as e:
        ERR('Faild to write sslvpn app.conf. Raise {}'.format(e))


def single_cpd(user, v):
    cpd = "/usr/local/sslvpn-1.0/app-rsc/cpd/{}"
    try:
        DBG('start write cpd')
        tenv = init_tenv()
        tenv.get_template(
            'bd-sslvpn-cpd-config').stream(services=v).dump(cpd.format(user))
    except Exception as e:
        ERR('Faild to write sslvpn cpd/user conf. Raise {}'.format(e))


def cpd_user_app_config(user):
    """写cpd目录下存储每个用户可推送的服务文件文件名以用户名命名"""
    cpd = "/usr/local/sslvpn-1.0/app-rsc/cpd/{}"
    # for tmp in os.listdir(CPD):
    #     os.system('rm -rf {}{}'.format(CPD, tmp))
    data = fmt_user_app()

    v = data[user]
    # for k, v in data.items():
    try:
        DBG('start write cpd')
        tenv = init_tenv()
        tenv.get_template(
            'bd-sslvpn-cpd-config').stream(services=v).dump(cpd.format(user))
    except Exception as e:
        ERR('Faild to write sslvpn cpd/user conf. Raise {}'.format(e))


def get_route(iptype, ip_):
    """cs服務"""
    dict_ = dict()
    if iptype == 1:
        dict_['ip'] = ip_
        dict_['mask'] = '255.255.255.255'
    elif iptype == 2:
        ip, mask = ip_.split('/')
        dict_['ip'] = ip
        dict_['mask'] = int_to_strmask(mask)
    return dict_


def single_ccd(user, v, pre_ip, fin_ip):
    ccd = '/usr/local/sslvpn-1.0/sslvpn-main-components/ccd/{}'
    push_route = service(v)

    iBan = str(v[0]['iBan'])
    try:
        DBG('start write ccd')
        tenv = init_tenv()
        tenv.get_template('bd-sslvpn-ccd-config').stream(push_route=push_route,
                                                         iBan=iBan, pre_ip=pre_ip, fin_ip=fin_ip).dump(ccd.format(user))
    except Exception as e:
        ERR('Faild to write sslvpn ccd conf. Raise {}'.format(e))


def ccd_user_config(user, pre_ip, fin_ip):
    """ccd目录下存放用户推送的ip, 文件名以用户名命名"""
    ccd = '/usr/local/sslvpn-1.0/sslvpn-main-components/ccd/{}'
    data = fmt_user_app()

    v = data[user]

    push_route = service(v)

    iBan = str(v[0]['iBan'])
    try:
        DBG('start write ccd')
        tenv = init_tenv()
        tenv.get_template('bd-sslvpn-ccd-config').stream(push_route=push_route,
                                                         iBan=iBan, pre_ip=pre_ip, fin_ip=fin_ip).dump(ccd.format(user))
    except Exception as e:
        ERR('Faild to write sslvpn ccd conf. Raise {}'.format(e))
# *****写配置文件*****

# *****查找用户服务的辅助函数*****


def app_belongs_to_user():
    """查找每个用户的服务，包括用户组里面的服务和自身独有的服务"""
    sel = "SELECT u.id AS user_id, u.sName AS user_name, u.iBan, s.id, s.sName, s.iUrlType, " \
          "s.sUrl, s.iIpType, s.sIp, s.sIcon, s.sMark, s.sDns"
    sql1 = "{} FROM (m_tbbdvpn_ssl_user AS u LEFT JOIN {}) LEFT JOIN {};"
    sql = "{} FROM (m_tbbdvpn_ssl_user AS u INNER JOIN {}) INNER JOIN {};"

    unique = sql1.format(
        sel,
        'm_tbbdvpn_ssl_mid_user_service AS us ON u.id = us.user_id',
        'm_tbbdvpn_ssl_service AS s ON s.id = us.service_id'
    )

    user_group_service = sql.format(
        sel,
        'm_tbbdvpn_ssl_mid_group_service AS gs ON u.group_id = gs.group_id',
        'm_tbbdvpn_ssl_service AS s ON gs.service_id = s.id'
    )
    unique_data = execute_sql(unique)
    group_data = execute_sql(user_group_service)
    data = [i for i in group_data]
    # 除重
    for i in unique_data:
        if i not in group_data:
            data.append(i)
    name = set()
    for tmp in data:
        name.add(tmp['user_name'])
    return data, name


def get_port(u_app):
    """獲取端口類型, 端口號"""
    sql = 'select type, port from m_tbbdvpn_ssl_service_port where server_id={}'
    data = select(sql.format(u_app['id']))
    return data


def fmt_user_app():
    """
    获得{name: [service,...],...[...])这种格式的数据
    """
    all_unique_data, users = app_belongs_to_user()
    dict_ = dict()
    for name in users:
        config = []
        for u_app in all_unique_data:
            if u_app['user_name'] == name:
                u_app['port'] = get_port(u_app)
                config.append(u_app)
        dict_.update({name: config})
    return dict_


def get_cs(dict_):
    """获取cs服务的ip/ip段"""
    ips = ''
    if dict_['sIp']:
        if dict_['iIpType'] == 1:
            ips = dict_['sIp']
        elif dict_['iIpType'] == 2:
            ips, _ = deal_ip(dict_['sIp'])
        return ips


def cs_pro_port(data):
    """获取cs服务不同协议对应的端口, data为每个用户对应的cs服务"""
    dict_ = dict()
    tcp = []
    udp = []
    all_ = []
    icmp_ = []
    for p in data:
        type_ = p['type'].lower()
        port_ = str(p['port'])
        if type_ == 'tcp':
            tcp.append(port_)
        elif type_ == 'udp':
            udp.append(port_)
        elif type_ == 'all':
            all_.append(port_)
        elif type_ == 'icmp':
            icmp_.append(port_)

        dict_['tcp'] = ','.join(tcp)
        dict_['udp'] = ','.join(udp)
        dict_['all'] = ','.join(all_)
        dict_['icmp'] = ','.join(icmp_)
    return dict_


def cs_iptables(cs, s_ip):
    """
    配置cs服务的iptables规则
    根据端口的协议类型来调用对应的iptables规则函数
    """
    del_cmd = []

    for app_port in cs:

        for pro, port in app_port[1].items():
            if port == '':
                del app_port[1][pro]

        d_ip = app_port[0]
        for pro, port in app_port[1].items():
            if pro == 'tcp' or pro == 'udp':
                tcp_udp(s_ip, d_ip, pro, port)
            elif pro == 'all':
                all_ = 'iptables -I SSL_VPN_FORWARD -i tun0 -s {} -d {} -j RETURN -w'
                del_cmd = all_icmp(s_ip, d_ip, all_)
            elif pro == 'icmp':
                icmp_ = 'iptables -I SSL_VPN_FORWARD -i tun0 -s {} -d {} -p icmp -j RETURN -w'
                del_cmd = all_icmp(s_ip, d_ip, icmp_)
    return del_cmd


def service(cs_data):
    """
    根据cs/bs服务，得到推送的路由
    """
    push_route = []
    for tmp in cs_data:
        mask = '255.255.255.255'
        if tmp['sUrl']:
            ip_, port = url(tmp['sUrl'], tmp['iUrlType'])
            if ip_ and mask:
                push_route.append({'ip': ip_, 'mask': mask})
        if tmp['sIp']:
            ip = mask = ''
            if tmp['iIpType'] == 2:
                ip_mask = tmp['sIp'].split('/')
                rets, mark = deal_ip(ip_mask[0], ip_mask[1])
                if mark == 'single':
                    ip = rets
                    mask = '255.255.255.255'
                elif mark == 'iprange':
                    ip = ip_mask[0]
                    mask = int_to_strmask(ip_mask[1])
            elif tmp['iIpType'] == 1:
                ip = tmp['sIp']
                mask = '255.255.255.255'
            if ip and mask:
                push_route.append({'ip': ip, 'mask': mask})
    return push_route


def get_effective_user():
    """
    获取所有有效的用户
    """
    all_user = 'SELECT id, sName, sPassword FROM m_tbbdvpn_ssl_user ' \
               'WHERE (iIsExpire=1 or sExpireTime>="{}");'
    now_ = datetime.now()
    user_data = execute_sql(all_user.format(now_.strftime('%Y-%m-%d')))
    return user_data
# *****查找用户服务的辅助函数*****


def all_user_service():
    # 用户对应的所有服务
    user_service = fmt_user_app()
    u_urls = dict()
    u_cs = dict()

    for u, app in user_service.items():
        urls = []  # 保存{用户： urls(d_ip, dports)}
        cs_ip = []
        for ip_port in app:
            if ip_port['sUrl']:
                server, port = url(ip_port['sUrl'], ip_port['iUrlType'])
                if not (server == '' and port == ''):
                    urls.append((server, port))
            if ip_port['sIp']:
                server = get_cs(ip_port)
                port = cs_pro_port(ip_port['port'])  # {'tcp': '22, 33'}
                cs_ip.append((server, port))
        u_cs.update({u: cs_ip})
        u_urls.update({u: urls})
    return u_urls, u_cs


def bs_iptables(user_ip, u_urls):
    # 下发bs服务的iptables规则
    bs = dict()
    for u_key, u_url in u_urls.items():
        iptables = []
        user_iptables = {}
        for u, s_ip in user_ip.items():
            if u == u_key:
                for app_port in u_url:
                    d_ip = app_port[0]
                    port = app_port[1]
                    cmd = SSL_CMD.format(s_ip[0], d_ip, port)
                    try:
                        (status, output) = getstatusoutput(cmd)
                        DBG('status: %s cmd:%s output %s' % (status, cmd, output))
                    except RuntimeError:
                        ERR('run bs iptables reeor')
                    iptables.append(cmd.replace('-I', '-D', 1))
        user_iptables[u_key] = iptables
        bs[u_key] = user_iptables
    return bs


def user_cs_iptables(user_ip, u_cs):
    # 下发cs服务的iptables规则
    cs_ = dict()
    for key, cs in u_cs.items():
        iptables = []
        user_iptables = {}
        for name, s_ip in user_ip.items():
            if name == key:
                for s in s_ip:
                    del_cmd = cs_iptables(cs, s)
                    iptables = iptables + del_cmd
        cs_[key] = user_iptables
    return cs_


# 动态修改用户对应的配置文件和iptables规则
def get_user_vip():
    user_ip = shelve.open('user_ip.db')
    return user_ip


def rm_filie(path):
    DBG('starting rm file')
    for tmp in os.listdir(path):
        try:
            cmd = 'rm -rf {}{}'.format(path, tmp)
            status, output = getstatusoutput(cmd)
            DBG('status {}, cmd {}, output {}'.format(status, cmd, output))
        except Exception as e:
            ERR(e)


# 停止时清楚文件规则
def stop_action(port):
    rm_filie(CCD)
    rm_filie(CPD)

    # 清楚SSL_VPN_FORWARD
    cmd_f = 'iptables -F SSL_VPN_FORWARD -w'
    (status_f, output_f) = getstatusoutput(cmd_f)
    DBG('status: %s cmd:%s output %s' % (status_f, cmd_f, output_f))

    start_stop_iptables('stop', port)


def get_del_iptables():
    cmd = 'iptables -S SSL_VPN_FORWARD | grep {}'


def single_user_iptables(action, name):
    """修改，删除，增加用户时执行对应的规则"""
    pass


def dynamic_iptables():
    """
    动态修改iptables规则
    """
    # 先在FORWARD链创建一条全通规则
    cmd_acc = 'iptables -I FORWARD -s 0.0.0.0/0 -d 0.0.0.0/0 -j ACCEPT -w'
    (status_acc, output_acc) = getstatusoutput(cmd_acc)
    DBG('status: %s cmd:%s output %s' % (status_acc, cmd_acc, output_acc))

    cmd_f = 'iptables -F SSL_VPN_FORWARD -w'
    (status_f, output_f) = getstatusoutput(cmd_f)
    DBG('status: %s cmd:%s output %s' % (status_f, cmd_f, output_f))

    DBG('here')
    all_user = 'SELECT id, sName, sPassword FROM m_tbbdvpn_ssl_user ' \
               'WHERE (iIsExpire=1 or sExpireTime>="{}");'
    now_ = datetime.now()
    users = select(all_user.format(now_.strftime('%Y-%m-%d')))
    u_urls, u_cs = all_user_service()

    ips = {}
    users_ip = shelve.open('user_ip.db')

    ##
    for i, v in users_ip.items():
        ips[i] = v[0]

    DBG(ips)
    for user in users:
        try:
            name = str(user['sName'])
            s_ip = ips[name]
            user_ip = {name: [s_ip]}
            bs_iptables(user_ip, u_urls)
            user_cs_iptables(user_ip, u_cs)
        except Exception as e:
            ERR(e)

    cmd1 = '/usr/sbin/iptables -A SSL_VPN_FORWARD -i tun0 -s 0.0.0.0/0 -d 0.0.0.0/0 -j DROP -w'
    (status, output) = getstatusoutput(cmd1)
    DBG('status: %s cmd:%s output %s' % (status, cmd1, output))
    cmd2 = 'iptables -D FORWARD -j ACCEPT -w'
    (status2, output2) = getstatusoutput(cmd2)
    DBG('status: %s cmd:%s output %s' % (status2, cmd2, output2))


def modify_user(args):
    """修改用户时, 调用此函数"""
    arg = json.loads(args)

    DBG('begin modify user')
    # 根据改动的用户名来取得对应的推送ip和路由
    name = str(arg['sName'])
    time.sleep(1)
    try:
        user_db = shelve.open('user_ip.db')
        pre = user_db[name][0]
        fin = user_db[name][1]
        DBG('pre %s, fin %s' % (pre, fin))
        user_db.close()
        DBG('modify user: name %s, ip %s' % (name, pre))
        ccd_user_config(name, pre, fin)
        cpd_user_app_config(name)
        DBG('end modify user %s' % name)
    except Exception as e:
        ERR(e)


def modify_service():
    DBG('Begin modify service...')
    try:
        name_ips = shelve.open('user_ip.db')
        for name, ips in name_ips.items():
            try:
                pre = ips[0]
                fin = ips[1]
                DBG('modify service: name %s, ip %s' % (name, pre))
                ccd_user_config(name, pre, fin)
                cpd_user_app_config(name)
                DBG('end modify service %s' % name)
            except Exception as e:
                ERR(e)
        dynamic_iptables()
    except Exception as e:
        ERR('modify service. Raise {}'.format(e))


class SSLUser(object):
    """
    用于处理sslvpn的用户操作
    """

    def __init__(self):
        self.sqlite_conn = sqlite3.connect(DB_USER)
        self.sqlite_cursor = self.sqlite_conn.cursor()

    def create_auth(self):
        """
        创建表auth用于存储用户的帐号，密码.其中密码应该存储MD5的哈希值
        如果创建成功则返回对应的连接和光标
        """
        try:
            create_tbl = """CREATE TABLE IF NOT EXISTS auth(
                         id char(128) not null PRIMARY KEY,
                         name char(255) not null UNIQUE,
                         passwd char(255) not null,
                         locked int not null default 0,
                         dept char(255)
                    );"""
            self.sqlite_cursor.execute(create_tbl)
        except sqlite3.Error as e:
            ERR(e)

    def create_user(self):
        """用户名及密码写入表auth, 用集合的性质来得到删除和插入的行"""
        self.create_auth()
        user_data = get_effective_user()
        old_info = self.select_user()
        new_info = set([tmp['sName'] + ',' + tmp['sPassword']
                        for tmp in user_data])
        insert_info = new_info - old_info
        del_info = old_info - new_info

        insert_sql = 'insert into auth(id, name, passwd, locked, dept) ' \
                     'values("{}", "{}", "{}", 0, "0")'
        insert_data = [insert_sql.format(
            tmp.split(',')[0], tmp.split(',')[0], tmp.split(',')[1]
        ) for tmp in insert_info]

        delete_data = ['delete from auth where name="{}" and passwd="{}"'.format(
            tmp.split(',')[0], tmp.split(',')[1]) for tmp in del_info]
        try:
            self._exe(insert_data)
            self._exe(delete_data)
        except RuntimeError as e:
            ERR(e)

    def select_user(self):
        """获取sqlite3数据库里所有的用户信息(name,passwd)"""
        user_info = set([])
        try:
            self.sqlite_cursor.execute('select * from auth')
            info_in_table = self.sqlite_cursor.fetchall()
            user_info = set([tmp[1] + ',' + tmp[2] for tmp in info_in_table])
        except Exception as e:
            ERR(e)
        finally:
            return user_info

    def _exe(self, sql_list):
        try:
            [self.sqlite_cursor.execute(i) for i in sql_list]
            self.sqlite_conn.commit()  # 需要commit才能写入数据库里面
        except Exception as e:
            ERR(e)

    def delete(self):
        self.sqlite_cursor.execute("delete from auth")


class VPN():

    def __init__(self, args=None):
        pass

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

    def _vpn_start_stop(self, args=None):
        """
        VPN开启及关闭
            1.VPN开启关闭前需配置文件
                /usr/local/sslvpn-1.0/sslvpn-main-components/server_config/bd-sslvpn-config
            2.需调用/etc/openvpn/open_port.sh配置相关iptables规则
            3.关闭vpn, SSL_VPN_FORWARD链只留默认规则，清空用户目录CCD,
                清iptables规则缓存文件/usr/local/bluedon/tmp/cs_iptables.txt
        """
        DBG('VPN start/stop begin')

        # 获取写入配置文件bd-sslvpn-config的数据
        port = '7000'
        config = {}
        if args:
            try:
                base_config_data = json.loads(args)
            except:
                base_config_data = args
            if base_config_data:
                ip_mask = base_config_data['sChildNetIp'].split('/')
                config['server_addr'] = ip_mask[0]
                config['server_mask'] = ip_mask[1]
                config['sPort'] = base_config_data.get('sPort', '7000')
                port = config['sPort']
        else:
            # start_stop_iptables('stop', port)
            vpn_status_return('clear')
            DBG('sslvpn atcion no args')
            return
        # 写配置文件bd-sslvpn-config
        bd_sslvpn_config(config)
        # 写配置app.config
        all_app_config()

        # 启动、关闭vpn
        start_stop_iptables('stop', port)
        if str(base_config_data['iStatus']) == '1':
            start_stop_iptables('start', port)
            DBG('VPN start successfully')
        else:
            start_stop_iptables('stop', port)
            DBG('VPN stop successfully')

        # vpn状态返回
        vpn_status_return()
        DBG('VPN start/stop end')


    def _user_db_staticip(self, user_change):
        """
        用户名及密码入表auth, 为有效用户分配IP
        文件unused_ip_shelve存放待分配的IP, used_ip_shelve存放已分配的IP,
        删除用户, 该用户IP被unused_ip_shelve回收,
        """
        sql = 'SELECT * FROM m_tbsslvpn_setting;'
        base_data = execute_sql(sql)[0]

        min_ip_mask = base_data['sChildNetIp'].split('/')
        mask = min_ip_mask[1]
        vpn_ip = min_ip_mask[0]
        min_ip = base_data['firstip']
        max_ip = base_data['lastip']

        # 获取有效的用户, 并且使用sqlite, 将用户账号密码写入bd-sslvpn-user.db的auth表
        ssluser = SSLUser()
        ssluser.create_user()

        # 根据掩码mask来分配ip, unused_ip_shelve存放曾经使用过如今是空闲状态的ip,
        # used_ip_shelve用于存放正在使用的ip, init_dynamic_ip产生一个ip的迭代器
        if not os.path.exists('unused_ip_shelve'):
            shelve.open('unused_ip_shelve').close()
        db = shelve.open('unused_ip_shelve')
        db1 = shelve.open('used_ip_shelve')

        ips = init_dynamic_ip(min_ip, max_ip, mask)

        # 保证再次启动时能回到之前分配结束的位置
        for i in range(len(db) + len(db1)):
            next(ips)

        user_ip = defaultdict(list)
        user_data = get_effective_user()
        if user_change:
            try:
                # delete_user_iptables(set([user_change]))
                ip = self.get_ip_format(user_change, vpn_ip, mask, db1)
                user_ip[user_change].append(ip)
            except Exception as e:
                ERR("%s %s" % (user_change, e))

        # 获取需删除用户及需增加用户
        old_file = set([tmp for tmp in os.listdir(CCD)])
        file_in_table = set([tmp['sName'] for tmp in user_data])
        rev_file, new_file = old_file - file_in_table, file_in_table - old_file

        # 删除用户时需做:用户IP放回到"待分配IP",删除文件,删除该用户规则
        ccd = CCD + '{}'
        cpd = "/usr/local/sslvpn-1.0/app-rsc/cpd/{}"
        for tmp in rev_file:
            db[db1[tmp].keys()[0]] = db1[tmp]
            del db1[tmp]
            try:
                os.remove(ccd.format(tmp))
                os.remove(cpd.format(tmp))
            except:
                ERR('rm ccd or cpd error')

        if rev_file:
            for i, tmp in enumerate(rev_file):
                user_db = shelve.open('user_ip.db')
                del user_db[tmp]
                user_db.close()

        # 增加用户,需为用户分配ip,并配置文件/ccd/用户名


        if len(new_file) != 0:
            data = fmt_user_app()
            # u_urls, u_cs = all_user_service()
            for i, tmp in enumerate(new_file):
                db_set = set(db)
                ip_str = u''
                # 只有unused_ip_shelve为空时才从生成器里生出一个ip
                if len(db_set) == 0:
                    try:
                        ip_str = str(next(ips)).replace('[', '').replace(']', '')
                    except StopIteration:
                        DBG('all ips were used!')
                else:
                    ip_str = str(db_set.pop())
                    db.pop(ip_str)
                db1[tmp] = {ip_str: ip_str}

                pre_ip, fin_ip = self.get_ip_format(tmp, vpn_ip, mask, db1)
                user_ip[tmp].append(pre_ip)
                user_db = shelve.open('user_ip.db')
                user_db[tmp] = [pre_ip, fin_ip]  ##
                user_db.close()
                # 写ccd目录下的配置文件
                v = data[tmp]
                single_ccd(tmp, v, pre_ip, fin_ip)
                # bs_iptables(user_ip, u_urls)
                # user_cs_iptables(user_ip, u_cs)
                # 配置cpd目录下的用户文件
                single_cpd(tmp, v)
        # print '*****len db:', len(db)
        # print '*****len db1:', len(db1)

        db.close()
        db1.close()
        return user_ip

    def _user_iptables(self, user_change=None):
        """
        通过表间关系，根据用户-->(用户组)-->服务，找用户对应的所有服务
        根据服务协议分类,将同一协议的所有端口,使用multiport配置在一条iptables规则上
        icmp协议需配置来回规则,tcp21端口,需增加配置20端口及1024端口相关规则
        """

        user_ip = self._user_db_staticip(user_change)

        # # 所有用户对应的服务
        # u_urls, u_cs = all_user_service()
        #
        # db_iptables = shelve.open('user_iptables_shelve')
        # # bs服务的iptables规则
        # bs = bs_iptables(user_ip, u_urls)
        # for name, value in bs.items():
        #     for key, ips in value.items():
        #             db_iptables[name] = ips
        #
        # # cs服务的iptables规则
        # cs = user_cs_iptables(user_ip, u_cs)
        # for name, value in cs.items():
        #     for key, ips in value.items():
        #             db_iptables[name] += ips
        # db_iptables.close()

    def _run(self, user_change=None):
        while True:
            (status, output) = getstatusoutput('pgrep bd-sslvpn')
            if output:
                self._user_iptables(user_change)
                if user_change:
                    break
            else:
                ssluser = SSLUser()
                ssluser.delete()
                clear_iptables_file()
                break
            time.sleep(3)


def recover(action):
    """开机恢复，出厂恢复"""
    clear_iptables_file()

    if action == 'reset_recover':
        print 'reset_recover'
    elif action == 'boot_recover':
        try:
            with open('/etc/keepalived/status.conf', 'r') as fp:
                line = fp.read().strip()
            status = line.lower()
        except IOError as e:
            print('open /etc/keepalived/status.conf error')
            print(e)
            status = 'backup'


        sql = 'SELECT * FROM m_tbsslvpn_setting;'
        base_data = execute_sql(sql)[0]
        args = json.dumps(base_data)

        vpn = VPN()

        if status == 'master':
            time.sleep(5)
            DBG('starting sslvpn')

            vpn._vpn_start_stop(args)
            (status, output) = getstatusoutput('pgrep bd-sslvpn')
            print 'output', output
            if output:
                vpn._user_iptables()
                time.sleep(2)
                dynamic_iptables()
        else:
            # kill vpn if ha role is backup
            DBG('stopping sslvpn')
            port = args['sPort']
            start_stop_iptables('stop', port)


if __name__ == "__main__":

    if sys.argv[1] == 'boot_recover' or sys.argv[1] == 'reset_recover':
        print sys.argv[1]
        recover(sys.argv[1])
        print 'recver end'
        sys.exit(0)


    vpn = VPN()
    t = Thread(target=vpn._run, args=(sys.argv[1]))
    # t.setDaemon(True)
    t.start()
    # ccd_user_config('xz', '192.168.2.1', '192.168.2.3')

