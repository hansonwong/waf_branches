#! /usr/bin/env python
# -*-coding:utf-8-*-

import commands
import sys
import os
import json
from itertools import chain
from collections import OrderedDict
from logging import getLogger
import datetime
import time

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from core.iptables_init import iptables_init
from db.mysqlconnect import mysql_connect_dict
from networking.fwdb import insert_interfaces
from db.mysql_db import select
from utils.logger_init import logger_init
from utils.log_logger import rLog_dbg
DBG = lambda x: rLog_dbg('main', x)
MANAGE_NIC_PATH = '/etc/network_config/mgt_nic.txt'

class ConfigReset(object):
    def __init__(self):

        reset_function = OrderedDict()
        # 系统配置-抓包工具
        reset_function['packet_capture'] = 'python system.packet_capture reset'
        #网络设置出厂恢复

        reset_function['nic']              = 'python -m networking.config_iface reset'
        reset_function['mirror']           = 'python -m networking.initial_mirror'
        reset_function['virtual_line']     = 'python -m networking.virtual_line factory_recover'
        reset_function['bridge']           = 'python -m networking.config_bridge factory_recover'
        reset_function['pppoe']            = 'python -m networking.pppoe factory_recover'
        reset_function['port_aggregation'] = 'python -m networking.iface_aggregation factory_recover'
        reset_function['VLAN']             = 'python -m networking.config_vlan factory_recover'
        reset_function['static_route']     = 'python -m networking.route factory_recover'
        #reset_function['strategy_route']   = 'python -m networking.config_strategy_route init'    # 策略路由
        reset_function['strategy_route']   = 'python -m networking.tactics_route init'     # 精简版策略路由
        reset_function['ISP']              = 'python -m networking.isp_route init'
        reset_function['dynamic_route']    = 'python -m networking.initial_dynamic_route'
        reset_function['dhcp']             = 'systemctl stop dhcpd.service'
        reset_function['best_routing']     = 'python -m networking.best_routing factory_recover'
        reset_function['multicast_route']  = 'python -m system.multicast_route factory_recover'

        #对象定义
        reset_function['IP_group']         = 'python -m objectdefine.set_ipgroup init'
        reset_function['web_define_rule']  = "echo '' > /usr/local/bdwaf/conf/activated_rules/cusrule.conf"
        reset_function['ips_define_rule']  = "echo '' > /etc/suricata/custom.rules"

        reset_function['nets_within_nets'] = 'python -m system.nets_within_nets factory_recover'

        #防火墙
        reset_function['ddos']            = 'python -m firedam.ddos init'
        reset_function['virtualfw']       = 'python -m firedam.virtual_fw factory_recover'

        #安全防护
        reset_function['url_filter']      = 'python -m safetydefend.url_filter init'
        reset_function['virus_size']      = "echo '' > /etc/suricata/conf/filesize.rules"
        reset_function['virus_type']      = "echo '' > /etc/suricata/conf/filetype.rules"
        reset_function['eml_content']     = "echo '' > /etc/suricata/conf/content.rules"
        reset_function['eml_filename']    = "echo '' > /etc/suricata/conf/filename.rules"
        reset_function['eml_subject']     = "echo '' > /etc/suricata/conf/subject.rules"
        reset_function['keyword_filter']  = "echo '' > /etc/suricata/conf/key.txt"
        reset_function['file_filter']     = "echo '' > /etc/suricata/conf/fkey.txt"
        reset_function['web_keyword']     = "echo '' > /etc/suricata/conf/htp-content-kw.txt"
        reset_function['url_filter_strategy'] = "echo '' > /etc/suricata/conf/filter/url-policy.json"
        reset_function['url_filter_black'] = "echo '' > /etc/suricata/conf/filter/url-black.json"
        reset_function['url_filter_white'] = "echo '' > /etc/suricata/conf/filter/url-white.json"

        # 防病毒配置
        reset_function['antivirus_config'] = "echo '' > /etc/suricata/conf/antivirus.json"
        reset_function['antivirus_strategy'] = "echo '' > /etc/suricata/conf/filter/av-policy.json"

        #用户管理
        reset_function['usergroup']        = 'python -m usermanage.user_group init'
        reset_function['tactics']        = 'python -m usermanage.tactics init'
        reset_function['tactics']        = 'python -m usermanage.tactics onoff_init'

        #流量管理
        reset_function['flowmanage']      = 'python -m flowmanage.flow_manage init'

        #智能防护
        reset_function['revcamera']       = '/etc/antidetect/antidet stop'
        reset_function['revscan']         = 'killall snort'

        #ipv6隧道
        reset_function['ipv6tunnel']      ='python -m networking.ipv6tunnel factory_recover'
        #sslvpn
        reset_function['sslvpn']          = 'python -m sslvpn.sslvpn reset_recover'

        #ipsecvpn
        reset_function['ipsecvpn']        = 'python -m ipsecvpn.branch_docking factory_recover'
        reset_function['n2n-vpn']        = 'python ipsecvpn.n_to_n factory_recover'

        #nat64
        reset_function['nat64']           = 'python -m networking.nat64 factory_recover'
        reset_function['ip_monitor']     = 'python -m networking.ip_monitor factory_recover'

        self.reset_function = reset_function

    def _clean_config(self):
        #清除iptables规则
        iptables_init('iptables')
        iptables_init('ip6tables')
        #pass

        getLogger('main').info('begin to clean function')
        for k, v in self.reset_function.items():
            try:
                (status,output) = commands.getstatusoutput(v)
                print '*****************',k
                getLogger('main').info(k)
                if status != 0:
                    print output
            except Exception as e:
                print e
        getLogger('main').info('finish clean function')


class InitDatabase(object):

    def __init__(self,):
        sql_config = 'select sName,sValue from m_tbconfig'
        self.cur_dict = mysql_connect_dict()
        self.cur_dict.execute(sql_config)
        self.results_config = self.cur_dict.fetchall()
        dateC =datetime.datetime(2016,1,1)
        self.timestamp = time.mktime(dateC.timetuple())

    def _process_default_data(self):
        #默认配置(web控，ddos,管理员密码安全策略)
        default_config = {
                            "iDeepEngine":"1",
                            "iLoginChangePass":"1",
                            "iCheckMaxDay":"1",
                            "iTxtMaxDay":"30",
                            "iCheckMinLong":"1",
                            "ITxtMinLong":"6",
                            "setType": "1",
                            "iWebPort":"444",
                            "iTimeOut":"30",
                            "iMaxConcurrent":"100",
                            "iLoginLimit":"5",
                            "iMaxLoginNumber":"5",
                            "iThreshold":"100",
                            "iICMPThreshold":"100",
                            "iUDPThreshold":"100",
                            "iSYNThreshold":"100",
                            "iDNSThreshold":"100",
                            "full":"cover",
                            "compress":"1",
                            "isslLimit":"100"
                        }

        self.default_config = default_config
        self.key_config = [key for key in chain( self.default_config.keys())]

    def _retain_table(self):
        #不能清空的表
        self.table = [  'm_tbrolenavtree',
                        'm_tbconfig',
                        'm_tbnetport',
                        'm_tbrole',
                        'm_tbwebapplication_lib',
                        'm_tbaccount',
                        'm_tbnavtree',
                        'm_tburlgroup',
                        'm_tbaddress_isp',
                        'm_tbcustom_ips_lib',
                        'm_tbaddress_list',
                        'm_tbdefined_application',
                        'm_tbfiletypegroup',
                        'm_tbGId',
                        'm_tbndpi_protocol',
                        'm_tbsystem_info',
                        'm_tbprotocoltype',
                        'm_tbbdvpn_ssl_group',
                        'm_tbalgorithm'
                      ]

        #默认账号密码
        user_password = {'root':'ef8414f3a6d950f965502dd5a3c2257f',
                         'admin':'4022be391c9ab40996e2aeb217253252',
                         'secadmin':'a1ac8ddaf95ba4de6925d656500ffad3',
                         'audit':'483849c4c8d8fe2f6cec2360921b7099'
                    }

        #删除表m_tbnetport管理口除外的所有数据
        with open(MANAGE_NIC_PATH,'r') as f:
            manage_nic = [ str(k) for k in json.loads(f.read().strip()).keys()]
            manage_nic_format = str(manage_nic).replace('[','(').replace(']',')')
            sql_nic_del = 'DELETE from m_tbnetport WHERE sPortName not in  {}'.format(manage_nic_format)

        #web规则表,ips规则表只保留默认规则,删除自定义规则;账号表m_tbaccount只保留系统用户
        #ip表m_tbaddress_list需保留'all';文件类型m_tbfiletypegroup表保留"所有文件类型"
        sqls = {"sql_web":   'delete from m_tbwebapplication_lib where iCustomOrInset = "1"',
                "sql_ips":   'delete from m_tbcustom_ips_lib where iCustomOrInset ="1"',
                "sql_accont":'DELETE from m_tbaccount WHERE sUerName is NULL',
                "sql_accont_update":'UPDATE m_tbaccount set iUpdatePwd=%d'%self.timestamp,
                "sql_address_list": 'DELETE from m_tbaddress_list WHERE sAddressname not in ("all")',
                "sql_file_type": 'DELETE from m_tbfiletypegroup WHERE sFileExt != "*"',
                "sql_nic":   sql_nic_del,
                "sql_ssl_group": 'delete from m_tbbdvpn_ssl_group where sName != "系统默认组"',
                }

        for k,v in sqls.items():
            #print v
            self.cur_dict.execute(v)
        #初始化账号及密码
        [self.cur_dict.execute('update m_tbaccount set sPasswd="{password}" where sLoginAccount="{user}"'
                               .format(password=v,user=k)) for k,v in user_password.items()]

    def _clean_log(self):
        os.system('python /usr/local/bluedon/reportlog/log_reset.py')

    def _clean_table(self):
        self._process_default_data()
        self._retain_table()
        for data in self.results_config:
            if data['sName'] == 'sFileTypes':
                continue
            value = data['sValue']
            if not value:
                continue
            value = json.loads(value)
            for k,v in value.items():
                if set([str(k)]) & set(self.key_config):
                    value[k] = self.default_config[k]
                else:
                    value[k] = type(v)()
            value = json.dumps(value)
            sql = "update m_tbconfig set sValue = '%s' where sName = '%s'"%(value,data['sName'])
            self.cur_dict.execute(sql)

        sql_all_tables = "SELECT table_name from information_schema.`TABLES` WHERE TABLE_SCHEMA='db_firewall' and TABLE_TYPE = 'base table'"
        self.cur_dict.execute(sql_all_tables)
        result = self.cur_dict.fetchall()
        getLogger('main').info('begin to clean database')
        for table in result:
            if not (set([table['table_name']]) & set(self.table)):
                #print table['table_name']
                getLogger('main').info(table['table_name'])
                try:
                    self.cur_dict.execute('truncate table %s'%table['table_name'])
                except Exception as e:
                    print e

        self.cur_dict.close()
        self._clean_log()
        self._default_config()
        getLogger('main').info('finish clean database')

    def _default_config(self):
        default ={}
        #default['safetactics']   = 'python -m firedam.safe_tactics'
        default['ddos']          = 'python -m firedam.ddos reboot'
        default['system_config'] = 'python -m system.system_config'
        default['manage_port']   = 'python -m networking.set_nginx'
        default['IPS']           = 'python -m safetydefend.IPS_defined'
        default['web']           = 'python -m safetydefend.web'
        for k,v in default.items():
            try:
                (status,output) = commands.getstatusoutput(v)
                #print '*******默认配置******',k
                if status != 0:
                    print output
            except Exception as e:
                print e



def firewall_reset():

    logger_init('main','/usr/local/bluedon/log/main.log','INFO')
    getLogger('main').info('Factory Reset begin ...........')
    #os.system("/usr/bin/mysql --sock=/tmp/mysql3306.sock -uroot --password='bd_123456' -e 'source /usr/local/bluedon/conf/m_tbaccount.sql'")
    # disable and stop sshd
    # os.system('systemctl disable sshd.service')
    # getLogger('main').info('disable sshd...........')
    # os.system('systemctl stop sshd.service')
    # getLogger('main').info('stop sshd...........')

    config_reset = ConfigReset()
    config_reset._clean_config()

    database_init = InitDatabase()
    database_init._clean_table()
    with open(MANAGE_NIC_PATH, 'r') as f:
        manage_nic_dict =  json.loads(f.read().strip())
        for key,value in manage_nic_dict.items():
            os.system('ip addr flush dev %s'%key)
            os.system('ifconfig %s %s'%(key,value))
        #manage_nic = [ str(k) for k in manage_nic_dict.keys()]
        #manage_nic_format = str(manage_nic).replace('[','(').replace(']',')')
        #nic_config_info = select("select * from m_tbnetport where sPortName in {}".format(manage_nic_format))
        #for tmp in nic_config_info:
        #    del_ip = set(tmp['sIPV4Address'].split(',')) ^ set([manage_nic_dict[tmp['sPortName']]])
        #    while del_ip:
        #        del_ip_cmd = 'ip addr del %s dev %s'%(del_ip.pop(),tmp['sPortName'])
        #        getLogger('main').info(del_ip_cmd)
        #        os.system(del_ip_cmd)
    insert_interfaces()
    getLogger('main').info('Factory Reset end ...........')
    os.system('reboot')

def restore_database():
    os.system("/usr/bin/mysql --sock=/tmp/mysql3306.sock -uroot --password='bd_123456' -e 'source /usr/local/bluedon/tmp/sql1.sql'")

def backup_database():
    open('/usr/local/bluedon/tmp/backup.sql','w').close()
    os.system("echo 'use db_firewall;' >>/usr/local/bluedon/tmp/backup.sql")
    os.system("/usr/bin/mysqldump --sock=/tmp/mysql3306.sock -uroot --password='bd_123456' db_firewall >> /usr/local/bluedon/tmp/backup.sql")


if __name__=='__main__' :

    if sys.argv[1] == 'firewall':
        firewall_reset()
    if sys.argv[1] == 'restore':
        restore_database()
    if sys.argv[1] == 'backup':
        backup_database()

