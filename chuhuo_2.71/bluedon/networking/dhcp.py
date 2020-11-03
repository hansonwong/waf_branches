#! /usr/bin/env python
# -*-coding:utf-8 -*-

import json
import os
import re
import commands
from logging import getLogger
from commands import getstatusoutput

from IPy import IP
from netaddr import IPSet, IPRange
from jinja2 import Template

from db.mysql_db import select_one, select
from system.ha import init_tenv
from utils.mask_transition import strmask_to_intv6
from utils.file_handling import get_lines


# pylint: disable=E1101

class DhcpV6(object):
    def __init__(self, dhcp_data):
        for key, val in dhcp_data.iteritems():
            setattr(self, key, isinstance(val, int) and str(val) or val)
        self.int_mask = strmask_to_intv6(self.sDhcpServerMask)
        self.data = {}
        self.pre_data = (json.loads(list(get_lines('tmp/pre_dhcpv6_data.json'))[0])
                         if os.path.exists('tmp/pre_dhcpv6_data.json') else None)
        with open('tmp/pre_dhcpv6_data.json', 'w') as conf:
            conf.write(json.dumps(dhcp_data))

    def config(self):
        getLogger('main').info('Config DhcpV6 begin...')
        if self.iDhcpServerOn == '1':
            self.enable()
        elif self.iDhcpServerOn == '0':
            self.disable()

    def enable(self):
        self._clean_up()
        self._prepare_data()
        self._conf_radvd()
        self._dhcp_config()

    def disable(self):
        self._clean_up()

    def _clean_up(self):
        os.system('ip6tables -D FWINPUT -p UDP -m multiport --dport 546,547 -j ACCEPT;'
                  'ip6tables -D FWINPUT -p UDP -m multiport --sport 546,547 -j ACCEPT;')
        getstatusoutput(r"/usr/bin/sed -i '/NETWORKING_IPV6/d' /etc/sysconfig/network")
        pid_path = '/usr/local/bluedon/tmp/dhcp6.pid'
        _pre_dhcp_pid = list(get_lines(pid_path, is_strip=True))[0] if os.path.exists(pid_path) else None
        if _pre_dhcp_pid is not None:
            getstatusoutput('kill -9 %s' % _pre_dhcp_pid)
            getLogger('main').info('kill old dhcpv6 sever pid `%s`', _pre_dhcp_pid)

        if self.pre_data is not None:
            with open('/etc/radvd.conf', 'r+') as f:
                try:
                    result = re.sub(r'interface\s+%s*?\n\{.*?\n\};.*?\n?' % self.pre_data['sDhcpName'], '', f.read(), flags=re.DOTALL)
                    f.seek(0)
                    f.write(result)
                    f.truncate()
                except:
                    print 'get not match'
            _, output = getstatusoutput('service radvd restart')
            getLogger('main').info('restart service radvd: %s', output)

    def _prepare_data(self):
        self.data['dns'] = [self.sDhcpDNSIP, self.sDhcpBackupDNSIP]
        raw_range = IPSet()
        to_remove = IPSet()
        raw_range.add(IPRange(self.sDhcpIPStart, self.sDhcpIPEnd))
        for i in zip(self.sDhcpExceptIPStart, self.sDhcpExceptIPEnd):
            if not all(i): continue
            to_remove.add(IPRange(i[0], i[1]))
        ip_pool = raw_range - to_remove
        self.data['pool'] = ['  '.join([str(i[0]), str(i[-1])]) for i in ip_pool.iter_ipranges()]
        self.data['network'] = IP('%s/%s' % (self.sDhcpServerIP, self.sDhcpServerMask),
                                  make_net=True)

    def _conf_radvd(self):
        with open('template/radvd_dhcpv6', 'r') as fp:
            conf = Template(fp.read())
        with open('/etc/radvd.conf', 'a') as fp:
            fp.write(conf.render(name=self.sDhcpName))
        _, output = getstatusoutput('service radvd restart')
        getLogger('main').info('restart service radvd: %s', output)

    def _dhcp_config(self):
        os.system('ip6tables -I FWINPUT -p UDP -m multiport --dport 546,547 -j ACCEPT;'
                  'ip6tables -I FWINPUT -p UDP -m multiport --sport 546,547 -j ACCEPT;')
        getstatusoutput(r"echo 'NETWORKING_IPV6=yes' >> /etc/sysconfig/network")
        status, output = getstatusoutput('sysctl -w net.ipv6.conf.all.forwarding=1')
        if status:
            getLogger('main').error(output)
        tenv = init_tenv()
        tenv.get_template('dhcp6').stream(dhcp=self.data).dump('/etc/dhcp/dhcpd6.conf')
        os.system('dhcpd -6 -f -cf /etc/dhcp/dhcpd6.conf & echo $! > /usr/local/bluedon/tmp/dhcp6.pid')
        getLogger('main').info('dhcpv6 server up on `%s`' % self.sDhcpName)

def get_dhcp_data():
    ret = select('SELECT * FROM m_tbdhcpfour WHERE iDhcpServerOn=1;')
    return ret

# version for 20170526 update, base on 3.99
def config_dhcp(dhcp_list=None):
    """
    DHCP配置
    ip池：在起始ip与结束ip之间排除"DHCP排除范围"的IP，IP池分成了几段ip
    """
    os.system('iptables -D FWINPUT -p UDP -m multiport --dport 56,57 -j ACCEPT;'
              'iptables -D FWINPUT -p UDP -m multiport --sport 56,57 -j ACCEPT;')

    dhcp_list = get_dhcp_data()
    if len(dhcp_list) == 0: 
        dhcp_stop = 'systemctl stop dhcpd.service'
        (status, output) = commands.getstatusoutput(dhcp_stop)
        getLogger('main').info('%s %s' % (dhcp_stop, output))
        return

    tenv = init_tenv()
    # dhcp_status = str(dhcp_list['iDhcpServerOn'])

    # if dhcp_status != '1':      # 状态不为1关闭DHCP
    #     dhcp_stop = 'systemctl stop dhcpd.service'
    #     (status, output) = commands.getstatusoutput(dhcp_stop)
    #     getLogger('main').info('%s %s' % (dhcp_stop, output))
    #     return

    os.system('iptables -I FWINPUT -p UDP -m multiport --dport 56,57 -j ACCEPT;'
              'iptables -I FWINPUT -p UDP -m multiport --sport 56,57 -j ACCEPT;')

    dhcp_data_list = list()
    device_list = set()
    for dhcp_data in dhcp_list:
        print dhcp_data
        dhcp = {}
        startip = dhcp_data['sDhcpIPStart']
        endip = dhcp_data['sDhcpIPEnd']

        # raw_range = IPSet()
        # to_remove = IPSet()
        # raw_range.add(IPRange(startip, endip))
        # for i in zip(dhcp_data['sDhcpIPStart'], dhcp_data['sDhcpIPEnd']):
        #     if not all(i):
        #         continue
        #     print i[0], ' ', i[1]
        #     to_remove.add(IPRange(i[0], i[1]))
        # ip_pool = raw_range - to_remove
        print startip
        print endip
        ip_pool = IPSet()
        ip_pool.add(IPRange(startip, endip))
        print ip_pool
        dhcp['pool'] = ['  '.join([str(i[0]), str(i[-1])]) for i in ip_pool.iter_ipranges()]
        dhcp['routers'] = dhcp_data['sDhcpGateWay']
        dhcp['mask'] = dhcp_data['sDhcpServerMask']
        dhcp['subnet'] = IP('%s/%s' % (dhcp_data['sDhcpServerIP'], dhcp_data['sDhcpServerMask']),
                            make_net=True).strNormal(1).split('/')[0]
        dhcp['dns'] = ",".join([i for i in [dhcp_data['sDhcpDNSIP'], dhcp_data['sDhcpBackupDNSIP']] if i.strip()])
        dhcp['lease'] = '-1' if str(dhcp_data['iDhcpLease']) == '1' else dhcp_data['sDhcpLeasePlan']
        dhcp_data_list.append(dhcp)
        print 'debuging', dhcp
        device_list.add(dhcp_data['sDhcpName'])

    tenv.get_template('dhcp').stream(dhcp_data_list=dhcp_data_list).dump('/etc/dhcp/dhcpd.conf')

    # device = dhcp_list['sDhcpName']
    # device_ip = dhcp_list['sDhcpServerIP']
    # device_mask = dhcp_list['sDhcpServerMask']

    # DHCPDARGS = 'DHCPDARGS=%s' % device
    # with open('/etc/sysconfig/dhcpd', 'w')as fw:
    #     fw.write(DHCPDARGS + '\n')

    # write dhcpd file
    DHCPDARGS = [ 'DHCPDARGS=%s' % device for device in device_list ]
    with open('/etc/sysconfig/dhcpd', 'w')as fw:
        fw.write("\n".join(DHCPDARGS))
    
    # dhcpstr = 'systemctl restart dhcpd.service'
    # (status, output) = commands.getstatusoutput(dhcpstr)
    # getLogger('main').info('%s  %s' % (dhcpstr, output))

    dhcpstr='systemctl stop dhcpd.service'
    (status,output)=commands.getstatusoutput(dhcpstr)
    getLogger('main').info('%s  %s'%(dhcpstr,output))



    dhcpstr='systemctl start dhcpd.service'
    (status,output)=commands.getstatusoutput(dhcpstr)
    getLogger('main').info('%s  %s'%(dhcpstr,output))


def recover():
    open('/etc/radvd.conf', 'w').close()
    dhcp_data = select_one('select sValue from m_tbconfig where sName="DHCPServer";')
    dhcp_data = json.loads(dhcp_data['sValue'].strip() or '{}')
    if dhcp_data:
        config_dhcp(dhcp_data)

    dhcpv6_data = select_one('select sValue from m_tbconfig where sName="DHCPServerIPV6";')
    dhcpv6_data = json.loads(dhcpv6_data['sValue'].strip() or '{}')
    if dhcpv6_data and dhcpv6_data['iDhcpServerOn']:
        dhcpv6 = DhcpV6(dhcpv6_data)
        dhcpv6.config()


if __name__ == "__main__":
    # recover()
    # config_dhcp({"sDhcpName":"vEth9","sDhcpServerIP":"2.2.2.3","sDhcpServerMask":"255.255.255.0","sDhcpGateWay":"2.2.2.3","sDhcpDNSIP":"","sDhcpBackupDNSIP":"","sDhcpIPStart":"2.2.2.1","sDhcpIPEnd":"2.2.2.254","iDhcpLease":"1","dStartTime":"","dEndTime":"","sDhcpExceptIPStart":[],"sDhcpExceptIPEnd":[],"sIPV":"ipv4","iDhcpServerOn":0})
    config_dhcp()
    # print get_dhcp_data()
