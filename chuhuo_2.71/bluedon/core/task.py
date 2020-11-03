#! /usr/bin/ env python
# -*- coding:utf-8 -*-

import time
import threading
import os
import sys
import json
import ConfigParser
from logging import getLogger
from collections import deque
import commands as cd

from networking.fwdb import  insert_interfaces
from db.mysqlconnect import execute_sql
from firedam.nat import set_nat
from firedam.ipmac import bind_ipmac, ipmac_exception,ipmac_exception_ip,stop_start_ipmac
from firedam.safe_tactics import safetactics_main, del_mark_scount
from firedam.connlimit import source_connect_limit, destination_connect_limit
from firedam.ddos import main as ddosmain
from firedam.virtual_fw import proc_virtualfw
from flowmanage.flow_manage import VirtualLine, Aisle


from networking.virtual_line import virtual_line
from networking.isp_route import set_isp_route
from networking.iface_aggregation import iface_aggregation  # 以上四个导入，为原network_config文件夹

from networking.config_iface import IfaceAddress
from networking.route import static_routes
from networking.pppoe import ppp_data
from networking.dhcp import config_dhcp, DhcpV6
from networking.config_vlan import config_vlan
from networking.config_bridge import BridgeAddress
from networking.dns import config_dns
from networking.config_ospf import conf_ospf
from networking.config_rip import conf_rip
from networking.config_bgp import conf_bgp
from networking.config_zebra import conf_zebra
from networking.config_ospf_6 import v6_zebra, conf_ospf_6
from networking.set_mirror import add_mirror, del_mirror, enable_mirror
#from networking.config_strategy_route import TacticsRoute     # 新的策略路由
from networking.tactics_route import TacticsRoute     # 精简版策略路由
from networking.ipv6tunnel import GreTunnel, SixToFourTunnel, IsatapTunnel, FourOverSixTunnel, GreTunnelIPv4
from networking.nat64 import NatSixFour
from networking.set_nginx import set_nginx
from networking.config_ecmp import con_ecmp, con_ecmp_del

from objectdefine.url_group import UrlGroupConfigFile
#from objectdefine.set_ipgroup import IpGroup
from objectdefine.set_ipgroup import set_ipset
from objectdefine.obj_ip import handle_ip
from reportlog.log_config import update_log_config, update_server_config, mail_test, log_archive
from reportlog.config_syslog import syslog_config
from reportlog.system_reboot_log import shutdown_bluedon
from reportlog.log_query import recover_log
from safetydefend.url_filter import UrlFilterConfigFile
from safetydefend.IPS_defined import generate_config_restart, custom_ips_rule
from safetydefend.web import web_defined, web_strategy
from safetydefend.filter import eml_key, virus
from safetydefend.file_filter import file_filter
from safetydefend.keyword_filter import keyword_filter
from safetydefend.session_control import config_suricata
from safetydefend.web_content_keyword import web_keyword
from safetydefend.url_filter_strategy import url_filter_strategy
from safetydefend.url_list_filter import UrlBlackListFilter, UrlWhiteListFilter
from smartdefend.honeypot import honey_pot
from smartdefend.revcamera import process_revcamera
from smartdefend.revscan import process_revscan
from smartdefend.exception_params import add_params, del_params
from smartdefend.del_param import del_param
from system.ha import HAStartStop,HotStandbyConfig
from system.config_snmp import config_snmp
from system.config_guide import guide
from system.system_config import sys_config_processer, set_time
from system.offline_upgrade import tar_file
from system.backup_recover import tables_backup,table_restore
from system.ntp_server import config_ntp_server
from system.packet_capture import main_capture
from system.nets_within_nets import NetsWithinNets
from usermanage.user_group import User, UserGroup
from usermanage.tactics import AuthTactics, OutAuthenticate, on_off
from usermanage.authentication import auth_downline, auth_login
from utils.logger_init import logger_init
from utils.del_session_file import del_file_session
from sslvpn.sslvpn import (VPN, vpn_status_return, CCD, modify_user,
                           dynamic_iptables, SSLUser, stop_action, all_app_config, modify_service
)
#from l2tpvpn import switch, user_manage
# from sslvpn.vpn import VPN,vpn_status_return
from ipsecvpn.branch_docking import proc_branch
from ipsecvpn.ipsevpn_status import SubnetMapTunnel
from ipsecvpn.n_to_n import CenterNode, EdgeNode
from firedam.session_manage.session_status import stop_session
# export log to csv
from reportlog.export_to_csv import cmd_export_csv
from system.hasync.start_stop_hasync import sync_main
from ipsec_client.netport_in_out import IpsecClient
from ipsec_client.ipsec_user_management import UserManage
from system.multicast_route import multicast_route
from antivirus.antivirus_config import antivirus_config
from antivirus.antivirus_strategy import strategy_config

from bdwafd.config_iface_deploy import ConfigIfaceDeploy
from bdwafd.config_virline import ConfigVirLine
from bdwafd.config_iptables import ConfigIptables
from bdwafd.config_bridge import ConfigBridge


from utils.log_logger import rLog_dbg
DBG = lambda x: rLog_dbg('sslvpn_task', x)


def proc_staticroute(args):
    static_routes(args[0], json.loads(args[-1]))


def proc_nat(args):
    """ set SNAT and DNAT """

    nat_type = args[0].strip().upper()
    set_nat(nat_type, 'reboot')

def proc_set_virtual_line(args):
    ConfigVirLine(args).write_bridge_conf()
    return virtual_line().handle_cmd(args)


def proc_config_interface(args):
    # return iface_config().handle_cmd(args)
    iface = IfaceAddress(json.loads(args[1]))
    iface.config()
    ConfigIfaceDeploy().config_mode(json.loads(args[1])['sWorkMode'])

def proc_stategy_routing(args):
    # 策略路由
    #action = args[0]
    #data = json.loads(args[1])
    #iptype = data.get('sIPV', 'ipv4')
    #ip_4_6_dict = {'ipv4': ' ', 'ipv6': ' -6 '}
    #ip_4_6 = ip_4_6_dict[iptype]
    #if iptype == 'ipv4':
    #    iptables = '/usr/sbin/iptables'
    #else:
    #    iptables = '/usr/sbin/ip6tables'
    #tacticsroute = TacticsRoute(data, iptables, ip_4_6, action)
    #tacticsroute.run()

    # 精简版
    action = args[0]
    data = json.loads(args[1])
    tacticsroute = TacticsRoute(data, action)
    tacticsroute.modify()


def proc_bridge_routing(args):
    data = json.loads(args[-1])
    if args[0] == "del":
        data['iStatus'] = 0
    BridgeAddress(data).config()
    ConfigIptables().init_bridge_iptables()
    ConfigIfaceDeploy().config_tproxy_mode()


def proc_isp_config(args):
    data = json.loads(args[1])

    if args[0] == 'add':
        if str(data['iStatus']) == '1':
            set_isp_route(data, 'add')
    elif args[0] == 'del':
        set_isp_route(data, 'del')


def proc_aggre(args):
    return iface_aggregation().handle_cmd(args)


def proc_dial(args):
    print "args:", args
    ppp_data(args[0], args[-1])


def proc_dhcp(args):
    try:
        dhcp_data = json.loads(args[0])
    except ValueError:
        dhcp_data = dict()
        pass
        # dhcp_data = json.loads(args[1])

    
    if dhcp_data.get('sIPV') == 'ipv6':
        pass
    else:
        dhcp_data['sIPV'] = 'ipv4'

    if dhcp_data['sIPV'] == 'ipv4':
        # dhcp v4, the dhcp data is useless 20170525
        config_dhcp(dhcp_data)
    elif dhcp_data['sIPV'] == 'ipv6':
        DhcpV6(dhcp_data).config()


def proc_vlan(args):
    data = json.loads(args[-1])
    if args[0] == "del":
        data['iStatus'] = 0
    config_vlan(data)


def proc_dns(args):
    config_dns(args[0], info_old=args[1], info_new=args[2])

def proc_setIP(args):
    #ip_set = IpGroup(args)
    #ip_set.process_data(ip_set.choice())
    data = json.loads(args[1])
    iptype = data['sGroupIPV'] if data.get('sGroupIPV', '') else 'ipv4'
    set_ipset(data, args[0], iptype)


def proc_strategy(args):
    """ 安全策略设置 """

    # data = json.loads(args[1])
    # if args[0] == 'del':
    #    del_mark_scount(data, 'del')
    #iptype = data.get('sIPV', 'ipv4')
    os.system('iptables -t mangle -F APPMARK')
    safetactics_main()


def proc_ddos(args):
    """ 设置ddos """
    ddosmain('reboot')


def proc_nginx(args):
    """ 更改nginx监听端口 """
    set_nginx(args[0])

def proc_sourcelimit(args):
    source_connect_limit(args[0], args[1])


def proc_destinationlimit(args):
    destination_connect_limit(args[0], args[1])


def proc_ha(args):
    info = json.loads(args[1])
    #if args[0] == 'refresh':
    #    #info = json.loads(args[1])
    #    main_backup(info['sHaModel'])
    #else:
    cls = HAStartStop(args[0], info)
    cls.start_or_stop()
    action = info.get('iTurn', 'stop')
    if action == 'stop':
        sync_main(action)


def proc_mirror(args):
    data = json.loads(args[1])
    if args[0] == "add":
        if data["iStatus"] == 1:
            add_mirror(data)
    elif args[0] == "del":
        if data["iStatus"] == 1:
            del_mirror(data)
    elif args[0] == "enable":
        enable_mirror(data)


def proc_honeypot(args):
    print "******honeypot*******", args
    honey_pot().handle_cmd(args)


def proc_url_filter(args):
    """ 防火墙--> url过滤 """

    data = json.loads(args[1])
    urlf = UrlFilterConfigFile(data)
    if args[0] == 'add':
        urlf.add()
    elif args[0] == 'del':
        urlf.delete()
    elif args[0] == 'enable':
        urlf.delete()
        urlf.add()


def proc_url_group(args):
    """ 自定义对象--> url类型组 """

    data = json.loads(args[1])
    urlg = UrlGroupConfigFile(data)
    if args[0] == 'add':
        urlg.add()
    elif args[0] == 'del':
        urlg.delete()

def proc_handle_ip(args):
    """ 自定义对象--> ip """
    data = json.loads(args[0])
    if data.get('sIPV', '') == 'ipv4':
        handle_ip(data)

def pro_config_ospfd(args):
    conf_zebra()
    v6_zebra()
    conf_ospf()


def pro_config_ripd(args):
    conf_zebra()
    conf_rip()


def pro_config_bgpd(args):
    conf_zebra()
    conf_bgp()

def pro_ospf_v6(args):
    conf_zebra()
    v6_zebra()
    conf_ospf_6()

def proc_IPS_defined(args):
    custom_ips_rule()


def proc_aisle(args):
    """ 流量管理--> 通道 """

    #print args
    data = json.loads(args[1])

    aisle = Aisle(data)
    if args[0] == 'add':
        if int(data['iStatus']) == 1:
            aisle.add()
    elif args[0] == 'del':
        aisle.delete()
    elif args[0] == 'seq':
        aisle.seq()


def proc_virtual_line(args):
    """ 流量管理--> 虚拟线路 """

    data = json.loads(args[1])
    vline = VirtualLine(data)
    if args[0] == 'add':
        vline.add()
    elif args[0] == 'del':
        vline.delete()


def proc_user_manage(args):
    """ 用户管理--> 用户 """

    data = json.loads(args[1])
    data['sUserName'] = str(data['sUserName'])
    user = User(data)
    if args[0] == 'add':
        user.add()
    elif args[0] == 'del':
        user.delete()


def proc_user_group(args):
    """ 用户管理--> 用户组 """

    if args[0] == 'add':
        data = json.loads(args[1])
        user_group = UserGroup(data)
        user_group.add()
    elif args[0] == 'del':
        g_data = json.loads(args[2])
        u_data = json.loads(args[1])
        user_group = UserGroup(g_data)
        user_group.delete(u_data)


def proc_auth_tactics(args):
    """ 用户管理--> 认证策略 """

    data = json.loads(args[1])
    auth_tactics = AuthTactics(data)
    if args[0] == 'add':
        auth_tactics.add()
    elif args[0] == 'del':
        auth_tactics.delete()
    elif args[0] == 'enable':
        auth_tactics.delete()
        auth_tactics.add()
    elif args[0] == 'on_off':
        action = str(data.get('iTurnOn', '0'))
        on_off(action)


def proc_authenticate(args):
    """ 用户管理--> 外部认证 """

    data = json.loads(args[1])
    authenticate = OutAuthenticate(data)
    if args[0] == 'add':
        authenticate.add()
    elif args[0] == 'del':
        authenticate.delete()
    elif args[0] == 'enable':
        authenticate.delete()
        authenticate.add()


def proc_auth_login(args):
    """ 用户管理--> 登录页验证 """

    data = json.loads(args[0])
    auth_login(data)


def proc_auth_downline(args):
    """ 用户管理--> 用户下线 """

    data = json.loads(args[0])
    auth_downline(data)


def proc_ipmac_bind(args):
    process = ''.join(args)
    bind_ipmac(process)


def proc_log_config(args):
    update_log_config(args)
    #print 'proc_log_config'


def proc_server_config(args):
    update_server_config(args)
    #print 'proc_server_config'


def proc_mail_test(args):
    mail_test(args)
    #print 'mail_test'


def proc_log_arch(args):
    log_archive(args)
    #print 'log_archive'


def proc_web_define(args):
    web_defined()


def pro_web_strategy(args):
    web_strategy()


def proc_eml_key(args):
    eml_key()


def proc_config_guide(args):
    """ 配置向导 """
    guide()


def proc_ips_strategy(args):
    #custom_ips_template()
    generate_config_restart()


def proc_revcamera(args):
    if not os.path.isdir('/tmp/fifo'):
        os.mkdir('/tmp/fifo')
    if args[0]=='refresh':
       data=''
       process_revcamera(args[0], data)
    else:
       data = json.loads(args[1])
       process_revcamera(args[0], data)


def proc_revscan(args):
    if not os.path.isdir('/tmp/fifo'):
        os.mkdir('/tmp/fifo')
    if args[0].strip() in ['refresh']:
        process_revscan(args[0], '')
    else:
        data = json.loads(args[1])
        process_revscan(args[0], data)


def proc_nic_flush(args):
    insert_interfaces()
    multicast_route()


def proc_virus(args):
    virus()


def proc_tbrolelib(args):
    # data = json.loads(args[1])
    # config_evillib(args[0], data)
    pass


def pro_file_filter(args):
    """信息泄露防护-->文件过滤"""
    file_filter()


def pro_keyword_filter(args):
    """信息泄露防护-->上传关键字过滤"""
    keyword_filter()


def proc_log_query(args):
    recover_log(args)
    pass


def proc_config_snmp(args):
    data = json.loads(args[1])
    if args[0] == "on_off":
        if int(data["iTurnOnSnmp"]) == 1:
            os.system("iptables -I FWINPUT -p UDP --dport 161 -j ACCEPT")
            os.system("service snmpd restart")
            getLogger("main").info("service snmpd restart")
        elif int(data["iTurnOnSnmp"]) == 0:
            os.system("killall snmpd")
            os.system("iptables -D FWINPUT -p udp --dport 161 -j ACCEPT")
            getLogger("main").info("killall snmpd")
    else:
        config_snmp()


def proc_config_backup(args):
    data = json.loads(args[0])
    tables_backup(data)


def proc_system_config(args):
    '''系统 -->系统配置'''
    data = json.loads(args[0])
    sys_config_processer(data)


def proc_nets_within_nets(args):
    """ 系统->系统配置->网中网阻断 """
    data = json.loads(args[-1])
    data['iStatus'] = str(data.get('iStatus', '0'))
    data['iAction'] = str(data['iAction'])
    if args[0] == "del":
        data['iStatus'] = '0'
    NetsWithinNets(data).entry()


def proc_time_set(args):
    data = json.loads(args[0])
    set_time(data)


def proc_tbrolelib_offline(args):
    data = args[0]
    tar_file(data)


def proc_recover(args):
    args=json.loads(args[0])

    if args['iType']=='2' or args['iType']=='1':
        print "恢复"
        table_restore(args)
    if args['iType']=='3':
       print '出厂配置'
       os.system('python /usr/local/bluedon/core/second_firewall_reset.py firewall')


def proc_config_param(args):
    turn_sql = "select sValue from m_tbconfig where sName = 'AutorRuleExceptionTurn' "
    result = execute_sql(turn_sql)[0]["sValue"]
    result = json.loads(result)
    on_off = int(result["iExceptionStrategyOn"])
    param_path = "/home/ng_platform/policyevolve"
    conf = ConfigParser.ConfigParser()
    conf.read(param_path + "/tse.ini")
    val = conf.get("system", "default queue")
    # print "OOOO...", val
    if on_off == 1:
        os.system("%s/nftse -B -F %s/tse.ini -Q %s -L DEBUG" % (param_path, param_path, val))
        print "%s/nftse -B -F %s/tse.ini -Q %s -L DEBUG" % (param_path, param_path, val)
    else:
        os.system("killall nftse")
    # datas = json.loads(args).split("|")
    add_data = json.loads(args[1])
    del_data = json.loads(args[0])
    # print "PPP..", add_data
    del_params(del_data)
    add_params(add_data)


def proc_del_param(args):
    if args[0] == "del":
        del_param(args[1])
    elif args[0] == "delall":
        os.system("iptables -F TSE_CHAIN")
        # print "ppp:", "iptables -F TSE_CHAIN"


def proc_syslog_config(args):
    syslog_config(args)


def pro_del_session(args):
    del_file_session(args)


def proc_ipmac_exception(args):
    ipmac_exception()


def proc_system_reboot(args):
    # print args
    shutdown_bluedon(args[0], json.loads(args[1]))

def proc_hot_standby(args):
    if len(args) and args[0]=='refresh':
        HotStandbyConfig(args[0])
    else:
        HotStandbyConfig()

def proc_vpns(args=None):
    (status,output1) =  cd.getstatusoutput(
        "ps -ef | grep sslvpn/sslvpn.py | grep -v grep | awk '{print $2}'")
    os.system('kill -9 %s' % output1)

    vpn = VPN()
    vpn._user_db_staticip(None)
    DBG('dynamic_iptables')
    time.sleep(2)
    dynamic_iptables()
    os.system("python /usr/local/bluedon/sslvpn/sslvpn.py '' &")
    DBG('end dynamic_iptables')


def proc_vpn_user(args):
    if args[0] == 'add' or args[0] == 'del':
        ssluser = SSLUser()
        ssluser.create_user()
    elif args[0] == 'modify':
        DBG('modify user')
        modify_user(args[1])
    time.sleep(3)
    dynamic_iptables()
    DBG('Finish run dynamic_iptables()')


def proc_vpn_service(args):
    all_app_config()
    if args[0] == 'modify' or args[0] == 'del':
        DBG('Starting run modify_service()')
        modify_service()
        DBG('Finish run modify_service()')


def proc_vpn(args):
    DBG(args)


def proc_vpn_on_off(args):
    CPD = "/usr/local/sslvpn-1.0/app-rsc/cpd/"
    if not os.path.isdir('/tmp/fifo'):
        os.mkdir('/tmp/fifo')
    open('/tmp/fifo/sslvpn','w').close()
    if args[0] == 'refresh':
        vpn_status_return()
        return
    elif args[0] == 'clear':
        vpn_status_return('clear')
    else:
        vpn = VPN(args[1])
    if args[0] =='restart' or args[0]=='stop':
        from commands import getstatusoutput
        os.system('/usr/sbin/iptables -F SSL_VPN_FORWARD')
        os.system('/usr/sbin/iptables -I SSL_VPN_FORWARD -i tun0 -s 0.0.0.0/0 -d 0.0.0.0/0 -j DROP')
        for tmp in os.listdir(CCD):
            cmd = 'rm -f {}{}'.format(CCD, tmp)
            status, output = getstatusoutput('rm -f {}{}'.format(CCD, tmp))
            DBG('status: %s cmd:%s output %s' % (status, cmd, output))
        for tmp in os.listdir(CPD):
            cmd = 'rm -f {}{}'.format(CPD, tmp)
            status, output = getstatusoutput('rm -f {}{}'.format(CPD, tmp))
            DBG('status: %s cmd:%s output %s' % (status, cmd, output))
        try:
            os.remove('/usr/local/bluedon/unused_ip_shelve')
            os.remove('/usr/local/bluedon/used_ip_shelve')
            os.remove('/usr/local/bluedon/user_ip.db')
        except Exception as e:
            getLogger('main').info(e)

    if args[0] == 'stop':
        data = json.loads(args[1])
        port = data['sPort']
        stop_action(port)
        DBG('stop %s' % args[0])
    elif args[0] == 'start' or args[0] =='restart':
        vpn._vpn_start_stop(args[1])
        time.sleep(4)
        DBG('start or restart')
        proc_vpns()



def proc_ipv6_tunnel(args):
    data = json.loads(args[1])
    if args[0] == 'del':
        data['iStatus'] = '0'
    if data['sTunnalType'] == 'Tunnal':
        GreTunnel(data).config()
    elif data['sTunnalType'] == 'Ipv6ToIpv4':
        SixToFourTunnel(data).config()
    elif data['sTunnalType'] == 'Isatap':
        IsatapTunnel(data).config()
    elif data['sTunnalType'] == '4over6':
        FourOverSixTunnel(data).config()
    elif data['sTunnalType'] == 'GreTunnelIPv4':
        GreTunnelIPv4(data).config()
    else:
        getLogger('main').error('wrong args')


def proc_ipsecvpn_branch(args):
    """ IPSEC_VPN """
    proc_branch()


def pro_ipsecvpn_status(args):
    tunnel = SubnetMapTunnel()
    tunnel.main()

def proc_strategy_from_scm(args):
    import threading
    from scm.deal_scm_data import deal_scm_data
    getLogger('main').debug('start deal_scm_data...')
    deal_scm_data(args[0])
    getLogger('main').debug('end deal_scm_data...')
    # t = threading.Thread(target=deal_scm_data, args=(args[0],))
    # t.start()
    # t.join()

def proc_session(args):
    """ 会话管理--> 会话状态 """

    data = json.loads(args[0])
    smark = data.get('sMark', '')
    if smark:
        stop_session(smark)

def proc_session_control(args):
    config_suricata()


def proc_nat64(args):
    data = json.loads(args[-1])
    if args[0] == 'del':
        data['iStatus'] = 0
    NatSixFour(data).config()


def proc_ntp_server(args):
    data = json.loads(args[-1])
    config_ntp_server(data)

def proc_ipmac_exception_ip(args):
    ipmac_exception_ip()


def proc_web_key(args):
    web_keyword()


def proc_best_routing(args):
    from networking.best_routing import start_best_routing
    args = json.loads(args[-1])
    start_best_routing(args['iTurnOn'] or 0)

def proc_export_csv(args):
    cmd_export_csv(args)

def proc_ipsec_out(args):
    cls = IpsecClient()
    cls.ipsec_secrets_conf()
    #cls.del_internet_iptables()
    #cls.internet_iptables_status()
    cls.vpn_interface_set()
    cls.start_stop_ipsecclient()
    cls.state_return()
    UserManage()

#def proc_ipsec_in(args):
#    cls = IpsecClient()
#    cls.del_internet_iptables()
#    cls.get_outnet_IPpool()
#    cls.internet_iptables_status()
#
#def proc_ipsec_vpn(args):
#    cls = IpsecClient()
#    cls.get_outnet_IPpool()
#    cls.vpn_interface_set()

def proc_ipsec_user(args):
    _,output = cd.getstatusoutput('ps -ef|grep ipsec_client.ipsec_user_manag |grep -v grep|wc -l')
    if not int(output):
        os.system('python -m ipsec_client.ipsec_user_management &')
    user_data = json.loads(args[1])
    UserManage(str(user_data['sUserName']),args[0])
    print 'end end end end end end end'

#def proc_ipsec_secrets(args):
#    cls = IpsecClient()
#    cls.ipsec_secrets_conf()

def proc_ipmac_switch(args):
    stop_start_ipmac()


def proc_center_node(args):
    data = json.loads(args[1])
    if args[0] == 'del':
        data['iStatus'] = '0'
    CenterNode(data).config()


def proc_edge_node(args):
    data = json.loads(args[1])
    if args[0] == 'del':
        data['iStatus'] = '0'
    EdgeNode(data).config()


def pro_multicast_router(args):
    multicast_route()
    pass

def proc_ecmp(args):
    con_ecmp(args)

def proc_ecmp_del(args):
    con_ecmp_del(args)

def proc_system_cap_pac(args):
    action = args[0]
    data = json.loads(args[1])
    main_capture(action, data)


def proc_antivirus_config(args):
    antivirus_config()


def proc_antivirus_strategy(args):
    strategy_config()


def proc_url_filter_strategy(args):
    url_filter_strategy()


def proc_url_blacklist(args):
    UrlBlackListFilter().entry()


def proc_url_whitelist(args):
    UrlWhiteListFilter().entry()


commands = {
    'CMD_STATICROUTE': proc_staticroute,                 #静态路由
    'CMD_NAT': proc_nat,                                 #NAT配置
    'CMD_SET_VIRTUAL_LINE': proc_set_virtual_line,       #虚拟线
    'CMD_CONIFG_INTERFACE': proc_config_interface,       #网口配置
    'CMD_STATEGY_ROUTING': proc_stategy_routing,         #策略路由
    'CMD_BRIDGE_CONFIG': proc_bridge_routing,            #网桥配置
    'CMD_ISP_CONFIG': proc_isp_config,                   #ISP路由
    'CMD_DIAL': proc_dial,                               #拨号设备
    'CMD_IFACE_AGGRE': proc_aggre,                       #端口聚合
    'CMD_DHCP': proc_dhcp,                               #DHCP
    'CMD_VLAN': proc_vlan,                               #VLAN
    'CMD_DNS': proc_dns,                                 #DNS
    'CMD_SAFE_STRATEGY': proc_strategy,                  #安全策略
    'CMD_DDOS': proc_ddos,                               # ddos设置
    'CMD_NGINX': proc_nginx,                             # 设置nginx
    'CMD_SOURCELIMIT': proc_sourcelimit,                 #源连接数控制
    'CMD_DESTINATIONLIMIT': proc_destinationlimit,       #目的连接数控制
    'CMD_IPSET': proc_setIP,                             #ip/ip组
    'CMD_HA': proc_ha,                                   #HA
    'CMD_HOT_STANDBY':proc_hot_standby,                 #双机热备
    'CMD_MIRROR': proc_mirror,                           #端口镜像
    'CMD_HONEYPOT': proc_honeypot,
    'CMD_URL_FILTER': proc_url_filter_strategy,          # 安全防护->url过滤->url过滤策略
    'CMD_URLBLACKLIST': proc_url_blacklist,              # 安全防护->url过滤->url黑名单
    'CMD_URLWHITELIST': proc_url_whitelist,              # 安全防护->url过滤->url白名单
    'CMD_URL_GROUP': proc_url_group,                     # url类型组
    'CMD_HANDLE_IP': proc_handle_ip,                     # 自定义对象--> ip
    'CMD_DYNAMICROUTING_OSPF': pro_config_ospfd,         # 动态路由OSPF协议
    'CMD_DYNAMICROUTING_RIP': pro_config_ripd,           # 动态理由rip协议
    'CMD_DYNAMICROUTING_BGP': pro_config_bgpd,           # 动态路由bgp协议
    'CMD_DYNAMICROUTING_OSPF_V3': pro_ospf_v6,           # 启用OSPF v6
    'CMD_ECMP': proc_ecmp,                               # ECMP  增加
    'CMD_ECMP_DEL': proc_ecmp_del,                       # ECMP  删除
    'CMD_BIND_IPMAC': proc_ipmac_bind,                   #ipmac绑定
    'CMD_VIRTUAL_LINE': proc_virtual_line,               #流量管理-->虚拟线路
    'CMD_AISLE': proc_aisle,                             #流量管理-->通道
    'CMD_IPS_DEFINED': proc_IPS_defined,                 #IPS自定义
    'CMD_IPS_STRATEGY': proc_ips_strategy,               #IPS策略
    'CMD_USER': proc_user_manage,                        #用户管理--> 用户
    'CMD_USER_GROUP': proc_user_group,                   #用户管理--> 用户组
    'CMD_AUTH_TACTICS': proc_auth_tactics,               #用户管理--> 认证策略
    'CMD_AUTHENTICATE': proc_authenticate,               #用户管理--> 外部认证
    'CMD_AUTHLOGIN': proc_auth_login,                    #用户管理--> 登录页
    'CMD_AUTH_DOWNLINE': proc_auth_downline,             #用户管理--> 用户下线
    'CMD_LOG_CONFIG': proc_log_config,                   #日志配置-->日志配置
    'CMD_LOG_ALERT': proc_server_config,                 #日志配置-->邮件报警
    'CMD_LOG_MAILTEST': proc_mail_test,                  #日志配置-->邮件测试
    'CMD_LOG_ARCHIVE': proc_log_arch,                    #日志配置-->日志归档入库
    'CMD_WEB_DEFINE': proc_web_define,                   #web自定义
    'CMD_WEB_STRATEGY': pro_web_strategy,                #web策略
    'CMD_EMLKEY': proc_eml_key,                          #邮件过滤
    'CMD_FILE_FILTER': pro_file_filter,                  #信息泄露防护-->文件过滤
    'CMD_KEYWORD_FILTER': pro_keyword_filter,            #信息泄露防护-->上传关键字过滤
    'CMD_GUIDE': proc_config_guide,                      #配置向导
    'CMD_REVCAMERA': proc_revcamera,                     #反向拍照
    'CMD_REVSCAN': proc_revscan,                         #反向扫描
    'CMD_NIC_FLUSH': proc_nic_flush,
    'CMD_TBROLELIB': proc_tbrolelib,                     # 系统-->系统维护-->规则库管理->自动升级
    'CMD_TBROLETB_OFFLINE': proc_tbrolelib_offline,      # # 系统-->系统维护-->规则库管理->离线升级
    'CMD_SNMP': proc_config_snmp,                        # 系统 -->系统配置 -->SNMP
    'CMD_EXCEPTION_PARAMS': proc_config_param,           # 智能防护-->策略自动演进
    'CMD_DEL_PARAM': proc_del_param,                     # 智能防护--》删除策略
    'CMD_SYS_CONFIG': proc_system_config,                # 系统 -->系统配置
    'CMD_SYS_REBOOT': proc_system_reboot,                # 系统 -->系统维护 --> 关机重启
    'CMD_PACKET': proc_system_cap_pac,                   # 系统 -->系统配置- -> 抓包工具
    'CMD_NETS_WITHIN_NETS': proc_nets_within_nets,       # 系统 -->系统配置--> 网中网检测
    'CMD_LOG_QUERY': proc_log_query,                     #日志-->查询
    'CMD_CONFIG_BACKUP': proc_config_backup,             #备份
    'CMD_RECOVER': proc_recover,                         #恢复
    'CMD_SYSLOG_CONFIG': proc_syslog_config,             #日志配置-->syslog
    'CMD_EXPORT_LOG': proc_export_csv,                   #log --> export
    'CMD_SESSION_FILE': pro_del_session,                 #删除session文件
    'CMD_IPMAC_EXCEPTION': proc_ipmac_exception,         #ipmac例外网口
    'CMD_IPMAC_EXCEPTION_IP':proc_ipmac_exception_ip,    #ipmac例外IP
    'CMD_VPN':proc_vpn,                                  #sslvpn
    'CMD_VPN_ON-OFF':proc_vpn_on_off,                    #sslvpn开/关
    'CMD_SSL_VPN_USER': proc_vpn_user,
    'CMD_SSL_VPN_SERVICE': proc_vpn_service,
    'CMD_TUNNEL': proc_ipv6_tunnel,                      # ipv6 隧道
    'CMD_IPSEC_BRANCH': proc_ipsecvpn_branch,            #IPSEC_VPN
    'CMD_IPSECVPN_STATUS':pro_ipsecvpn_status,           #ipsecvpn运行状态监控
    'CMD_SCM_DATA': proc_strategy_from_scm,              # 处理SCM下发数据
    'CMD_SESSION_STATUS': proc_session,                  # 会话状态
    'CMD_SESSION_CONTROL':proc_session_control,          # 会话控制
    'CMD_NAT64': proc_nat64,                             # 网络设置 --> NAT64
    'CMD_TIMESET': proc_time_set,                        # 系统配置 --> 时间配置
    # 'CMD_NTP_SERVER': proc_ntp_server,                   # 系统配置 --> ntpserver
    'CMD_KEYWORD_WEB':proc_web_key,                      #web内容关键字
    'CMD_BEST_ROUTING': proc_best_routing,               # 网络设置--> 策略路由--> 自动选路
    'CMD_IPSEC_OUT':proc_ipsec_out,                       #IPSEC VPN 外网口
    #'CMD_IPSEC_IN':proc_ipsec_in,                        #IPSEC VPN 内网口
    #'CMD_IPSEC_VPN':proc_ipsec_vpn,                      #ipsec vpn接口配置
    'CMD_IPSEC_USER':proc_ipsec_user,                    #ipsec vpn 用户管理
    #'CMD_IPSEC_SECRETS':proc_ipsec_secrets,              #ipsec vnp 认证方式
    'CMD_IPMAC_SWITCH':proc_ipmac_switch,                #ipmac 绑定开关
    'CMD_MULTICAST_ROUTER':pro_multicast_router,         #组播路由转发
    'CMD_VIRTUAL_FW': proc_virtualfw,                    # 防火墙 --> 虚拟防火墙
    'CMD_NTN_CENTER': proc_center_node,                  # 虚拟专网 》n2n 》中心节点
    'CMD_NTN_EDGE': proc_edge_node,                      # 虚拟专网 》n2n 》边缘节点
    'CMD_VIRUS': proc_antivirus_config,                  # 防病毒配置->基本配置
    'CMD_VIRUS_STRATEGY': proc_antivirus_strategy,       # 防病毒配置->防病毒策略设置
}


def notify_result(ret, cmd):
    notify = []
    notify.append(cmd)
    if ret:
        notify.append('true')
    else:
        notify.append('false')
    getLogger('main').info('echo \'%s\' > /tmp/fifo/second_firewall_notify.txt' % ('|'.join(notify)))
    os.system('echo \'%s\' > /tmp/fifo/second_firewall_notify.txt' % ('|'.join(notify)))


class TaskProcessor(threading.Thread):
    event = threading.Event()
    #tasks=set()
    tasks = deque()
    #Deques support thread-safe
    #taskslock = threading.Lock()

    def __init__(self,):
        super(TaskProcessor,self).__init__(name=self.__class__.__name__)

    def start(self):
        getLogger('main').debug(self.__class__.__name__+ ' starting...')
        super(TaskProcessor,self).start()
        getLogger('main').debug(self.__class__.__name__+ ' started')

    def stop(self):
        getLogger('main').debug(self.__class__.__name__+ ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').debug(self.__class__.__name__+ ' Exited')

    def add(self, task):
        #self.taskslock.acquire()
        #getLogger('webtask').info('%s'%task)
        self.tasks.append(task)
        #self.taskslock.release()

    def run(self):
        while 1:
            try:
                time.sleep(1)
                if self.event.isSet():
                    getLogger('main').info("Event set!")
                    return
                while self.tasks:
                    args=filter(lambda x: x, map(lambda x: x.strip(), self.tasks.popleft().split('|')))
                    if args and args[0] in commands:
                        commands[args[0]](args[1:])
                    else:
                        getLogger('main').warning('unexecute task: %s', args)
            except Exception as e:
                getLogger('main').exception('%s | args: %s', e, args)
            except BaseException:
                getLogger('main').exception("Unexpected error: %s | args: %s", sys.exc_info()[0], args)
                raise


class TaskDispatcher(threading.Thread):
    # fifo_path=''
    event = threading.Event()
    # processor=None

    def __init__(self,processor, fifo='/Data/apps/wwwroot/firewall/fifo/second_firewall.fifo'):
        super(TaskDispatcher,self).__init__(name=self.__class__.__name__)
        self.fifo_path = fifo
        self.processor = processor

    def start(self):
        getLogger('main').debug(self.__class__.__name__+ ' starting...')
        super(TaskDispatcher,self).start()
        os.system("echo '' > /Data/apps/wwwroot/firewall/fifo/second_firewall.fifo")
        getLogger('main').debug(self.__class__.__name__+ ' started')

    def stop(self):
        getLogger('main').debug(self.__class__.__name__+ ' Exiting...')
        self.event.set()
        os.system("echo '' > /Data/apps/wwwroot/firewall/fifo/second_firewall.fifo")
        self.join()
        getLogger('main').debug(self.__class__.__name__+ ' Exited')

    def run(self):
        # 会话管理--> 会话状态日志入库
        import threading
        from firedam.session_manage.session_status import proce_session_log
        threading.Thread(target=proce_session_log, args=(self.event,)).start()
        while 1:
            try:
                time.sleep(1)
                os.system('/usr/bin/sh /usr/local/bluedon/try_make_fifo.sh')
                f = os.open(self.fifo_path,os.O_NONBLOCK)
                fp = os.fdopen(f)
                #with open(self.fifo_path,) as fp:
                while 1:
                        time.sleep(1)
                        try:
                            fifo_mode =  os.stat('/Data/apps/wwwroot/firewall/fifo/second_firewall.fifo').st_mode
                            if not os.path.stat.S_ISFIFO(fifo_mode):
                                fp.close()
                                raise Exception('not fifo file')
                        except OSError:
                            fp.close()
                            raise Exception('fifo file not exists')

                        if self.event.isSet():
                            return
                        lines = fp.readlines()
                        for line in lines:
                            line = line.strip()
                            getLogger('webtask').info(line)
                            if line:
                                self.processor.add(line)
            except Exception as e:
                getLogger('main').exception(e)
            except BaseException:
                getLogger('main').exception("Unexpected error in TaskDispatcher: %s", sys.exc_info()[0])
                raise
