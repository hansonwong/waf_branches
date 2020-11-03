#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from logging import getLogger
from itertools import groupby
from ConfigParser import ConfigParser
from config import config
from db import conn_scope
from nginx import NginxController, NginxConfGenerator


class ConfigDeploy:
    '''
    config interface work mode
    '''

    def __init__(self):
        self.tproxy_nic = []
        self.bridge_nic = []
        self.getdata()

    def getdata(self):
        with conn_scope(**config['db']) as (_, cursor):
            # 网口模式(业务口)
            cursor.execute('select sPortName, sWorkMode from db_firewall.m_tbnetport '
                            'where sPortName like "vEth%"')
            self.port_workmodes = dict(cursor.fetchall())

            # 站点组
            cursor.execute("SELECT id from t_website WHERE type=2")
            self.reverseproxy_website = cursor.fetchall()
            # 桥
            cursor.execute('select sBindDevices,bridgeType from db_firewall.m_tbbridgedevice where iStatus=1')
            for binddev, br_type in cursor.fetchall():
                if br_type == 'tproxy':
                    self.tproxy_nic.extend(binddev.split(','))
                elif br_type == 'bridge':
                    self.bridge_nic.append(binddev)
            # 虚拟线
            cursor.execute('select sVirtualPortOne, sVirtualPortTwo from '
                           'db_firewall.m_tbvirtualline where iStatus=1')
            self.virLine = cursor.fetchall()

    def is_reverseproxy_deploy(self):
        '''
        当前是否反向代理模式
        '''
        return self.reverseproxy_website and (
               set(self.port_workmodes.values()) & set(config['reverseproxy']['workmode']))

    def is_tproxy_deploy(self):
        '''
        当前是否透明代理模式
        '''
        return True if self.tproxy_nic else False

    def is_bridge_deploy(self):
        '''
        当前是否桥/虚拟线模式
        '''
        return (True if self.bridge_nic else False) or (True if self.virLine else False)

    def gen_nginx_conf(self):
        '''
        配置混合模式
        '''
        # 透明代理
        # if self.is_tproxy_deploy():
            # NginxConfGenerator(config['tproxy']['conf_path']).gen_tproxy_conf()
            # NginxController().restart_nginx('tproxy')
        # 反向代理
        if self.is_reverseproxy_deploy():
            NginxConfGenerator(config['reverseproxy']['conf_path']).gen_reverseproxy_conf()
            NginxController().restart_nginx('reverseproxy')
        # 透明桥 虚拟线
        if self.is_bridge_deploy():
            NginxConfGenerator(config['bridge']['conf_path']).gen_bridge_conf()
            NginxController().restart_nginx('bridge')

    def config_iface_mode(self, iface_info):
        '''
        配置网口模式
        '''
        self.config_filter_port()  # 桥过滤口
        iface_data = json.loads(iface_info[1])
        if iface_data['sWorkMode'] in config['reverseproxy']['workmode']:
            if not NginxController().is_nginx_active('reverseproxy'):
                # 首次起该模式
                NginxConfGenerator(config['reverseproxy']['conf_path']).gen_reverseproxy_conf()
            NginxController().start_nginx('reverseproxy')
        if not self.is_reverseproxy_deploy():
            NginxController().stop_nginx('reverseproxy')

    def config_bridge_mode(self, br_info):
        '''
        配置透明代理,透明桥 桥模式
        '''
        br_data = json.loads(br_info[1]) 
        if br_data['bridgeType'] == 'tproxy':  # 透明代理
            if self.is_tproxy_deploy():
                if not NginxController().is_nginx_active('tproxy'):
                    # 首次起该模式
                    NginxConfGenerator(config['tproxy']['conf_path']).gen_tproxy_conf()
                NginxController().restart_nginx('tproxy')
            else:
                NginxController().stop_nginx('tproxy')
            self.config_filter_port()  # 桥过滤口
        elif br_data['bridgeType'] == 'bridge':  # 透明桥
            self.write_waf_bridge()
            if self.is_bridge_deploy():
                if not NginxController().is_nginx_active('bridge'):
                    # 首次起该模式
                    NginxConfGenerator(config['bridge']['conf_path']).gen_bridge_conf()
                NginxController().restart_nginx('bridge')
            else:
                NginxController().stop_nginx('bridge')

    def config_virLine(self):
        '''
        配置虚拟线模式
        '''
        self.write_waf_bridge()
        if self.is_bridge_deploy():
            if not NginxController().is_nginx_active('bridge'):
                # 首次起该模式
                NginxConfGenerator(config['bridge']['conf_path']).gen_bridge_conf()
            NginxController().restart_nginx('bridge')
        else:
            NginxController().stop_nginx('bridge')

    def write_waf_bridge(self):
        '''
        写waf_bridge配置文件,桥模式时配置
        '''
        devices = []
        # 桥配置
        for nics in self.bridge_nic:
            devices.append('br %s 8' % nics)
        # 虚拟线配置
        for vline_1, vline_2 in self.virLine:
            devices.append('vl %s,%s 7' % (vline_1, vline_2))
        getLogger('main').info(devices)
        with open('/usr/local/bdwaf/conf/waf_bridge.conf', 'w') as f:
            f.write('\n'.join(devices))


    def config_filter_port(self):
        '''
        过滤口走桥nginx, 过滤口格式 0-1|3-5|7-7
        反向代理和透明代理口未非过滤口
        修改网口模式,新建透明代理桥时配置
        '''
        nport = []
        for port, workmode in self.port_workmodes.items():
            if workmode in config['reverseproxy']['workmode'] or port in self.tproxy_nic:
                continue
            nport.append(int(filter(str.isdigit, port)))
        strport = []
        for k, l in groupby(enumerate(sorted(nport)), lambda (i, v): v - i):
            lst = [v for _, v in l]
            strport.append('%s-%s' % (lst[0], lst[-1]))
        new_port = '|'.join(strport)

        bridge_ini = '/usr/local/bdwaf/conf/bridge.ini'
        cf = ConfigParser()
        cf.read(bridge_ini)
        # 未修改
        if new_port == cf.get('mp_server', 'filter_data').strip():
            return False

        cf.set('mp_server', 'filter_data', new_port)
        with open(bridge_ini, 'w') as f:
            cf.write(f)
        getLogger('main').info('bridge.ini: ' + new_port)
        if self.is_bridge_deploy():
            NginxController().restart_nginx('bridge')


if __name__ == '__main__':
    ConfigDeploy().gen_nginx_conf()
