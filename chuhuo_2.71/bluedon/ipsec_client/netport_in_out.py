#!/usr/local/env python
# coding=utf-8

from jinja2 import Template
from netaddr import *
from IPy import IP
from logging import  getLogger
from db.mysql_db import select_one,select,update
from system.ha import init_tenv
from collections import defaultdict
from logging import getLogger
import commands
import os
import shelve
import socket
import struct
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class IpsecClient():

    def __init__(self,action=None):
        self.startIP = ''
        self.endIP = ''
        self.outnet_addr = ''
        self.tenv = init_tenv()
        self.iptables_cmd = "iptables -I IPSECCLIENTS -o ppp+ -i %s -m iprange --dst-range %s -s %s -j ACCEPT"
        self.flag = False


    def get_outnet_IPpool(self):
        """
        获取'启动客户端接入'界面选择的外网口IP及虚拟IP池
        """
        self.client_info = select_one('select sValue from m_tbconfig where sName="Ipsec_Vpn_Client"')
        self.client_info = json.loads(self.client_info['sValue'])

        #外网口IP
        outnet_set = select_one('select sIpaddresss from m_tbipsecoutnetport where sNetport="%s"'%self.client_info.get('sNetport',''))
        self.outnet_addr = outnet_set['sIpaddresss']

        #虚拟IP池
        virtualIP_set  = select_one('select * from m_tbVirtualNet where id=%d'%int(self.client_info.get('sClientIp','0')))
        self.startIP,self.endIP = virtualIP_set['sVirtualStartIp'],virtualIP_set['sVirtualEndIp']

        if self.startIP and self.endIP and self.outnet_addr:
            self.flag = True
            return self.startIP,self.endIP


    def ipsec_secrets_conf(self):
        """
       根据认证方式及外网口IP配置文件 /etc/ipsec.secrets,/etc/ipsec.conf
        """
        self.get_outnet_IPpool()
        if self.outnet_addr:
            secrets_way = select_one('select sValue from m_tbconfig where sName="ipsecVpn_Auth"')
            secrets_way =json.loads(secrets_way['sValue'])
            x509,share_key = ('authby=rsasig','#authby=secret') if secrets_way['auth']=='509'\
                                                                else ('#authby=rsasig','authby=secret')
            self.tenv.get_template('ipsec.secrets').stream(outnet_addr=self.outnet_addr,
                                                           key = secrets_way.get('key',''),
                                                           rsa = ': RSA /etc/ipsec.d/private/server-key.pem' if secrets_way['auth']=='509' else '',
                                                           ).dump('/etc/ipsec.secrets')

            self.tenv.get_template('ipsec.conf').stream(outnet_addr=self.outnet_addr,
                                                        #virtualIP_net=virtualIP_net,
                                                        x509 = x509,
                                                        share_key = share_key
                                                        ).dump('/etc/ipsec.conf')

    def vpn_interface_set(self,):
        """
        配置文件/usr/local/ipsec-vpn/client/etc/xl2tpd.conf
        """
        split_ip = lambda x:x.split('.')[-1]
        if self.flag:
            ip_int = int(IPAddress(self.startIP))-1
            vpn_ip = socket.inet_ntoa(struct.pack('I',socket.htonl(ip_int)))
            if split_ip(self.startIP)=='0' or split_ip(self.startIP)=='1':
                vpn_ip = self.endIP
            self.tenv.get_template('xl2tpd.conf').stream(outnet_addr = self.outnet_addr,
                                                         ippool='-'.join([self.startIP,self.endIP]),
                                                         vpn_ip = vpn_ip).dump('/usr/local/ipsec-vpn/client/etc/xl2tpd.conf')
            return vpn_ip
        return ''

    def start_stop_ipsecclient(self):
        """
        启动/关闭ipsec
        """
        client_on_off = self.client_info.get('type','stop')
        _,output=commands.getstatusoutput('/usr/local/ipsec-vpn/client/etc/ipsec-client-stop.sh')
        getLogger('main').info('stop client %s'%output)
        if client_on_off=='start' or client_on_off=='restart':
            _,output = commands.getstatusoutput('/usr/local/ipsec-vpn/client/etc/ipsec-client.sh')
            getLogger('main').info('stop client %s'%output)
            _,output=commands.getstatusoutput('/usr/local/ipsec-vpn/client/etc/ipsec-client-start.sh')
            getLogger('main').info('stop client %s'%output)

    def state_return(self):
        """
        ipsec启动与否状态返回
        """
        status,output = commands.getstatusoutput('ps -ef |grep ipsec  |grep -v grep |wc -l')
        #print 'output',output
        with open('/tmp/fifo/ipsec_vpn','w') as f:
            if int(output)>5:
                print >>f,json.dumps({"state":"1"})
            if int(output)<3:
                print>>f,json.dumps({"state":"0"})
        pass


if __name__=='__main__':
    #import pdb
    #pdb.set_trace()
    cls = IpsecClient()
    cls.ipsec_secrets_conf()
    cls.del_internet_iptables()
    cls.internet_iptables_status()
    cls.vpn_interface_set()
    cls.start_stop_ipsecclient()
    cls.state_return()


