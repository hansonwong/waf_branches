#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import MySQLdb
from logging import getLogger
import commands
from netaddr import *
import json
import sys
from db.mysqlconnect import mysql_connect,mysql_connect_dict

#conn=MySQLdb.connect(host='localhost',port=3306,user='root',passwd='123456',db='db_firewall',charset='utf8',unix_socket='/opt/lampp/var/mysql/mysql.sock')
#cur=conn.cursor()
ipstr='([0-9]{1,3}\\.){3}[0-9]{1,3}'
macstr='([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}'
v=re.compile(r'(%s)\s*?.*?\s*?(%s)'%(ipstr,macstr))


def rem_same():
    arp_info = []
    with open('/usr/local/bluedon/tmp/ipmac.txt','r') as fr:
         for line in fr:
             try:
               ip=v.match(line).group(1)
               mac=v.match(line).group(3)
               arp_info.append(ip+','+mac)
             except:
               pass
    del_same = set(arp_info)
    return del_same

def get_ipmac():
    conn=MySQLdb.connect(host='localhost',port=3306,user='root',passwd='bd_123456',db='db_firewall',charset='utf8',unix_socket='/tmp/mysql3306.sock')
    cur=conn.cursor()

    """ipstr='([0-9]{1,3}\\.){3}[0-9]{1,3}'
    macstr='([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}'
    v=re.compile(r'(%s)\s*?.*?\s*?(%s)'%(ipstr,macstr))"""

    ipmac_table_sql='select sSourceIP,sMac from m_tbip_mac_defined'
    cur.execute(ipmac_table_sql)
    ipmac_in_table=cur.fetchall()
    ipmac_set=[]
    for ipmac_tmp in ipmac_in_table:
        ipmac_set.append(ipmac_tmp[0]+','+ipmac_tmp[1])
    ipmac_set=set(ipmac_set)

    ipmac_info=os.popen('arp -n').read()
    fipmac=open('/usr/local/bluedon/tmp/ipmac.txt','w')
    print >>fipmac,ipmac_info
    fipmac.close()

    ip64 = {'4':'ipv4',
            '6':'ipv6'
            }
    ip_mac_info = rem_same()
    ip_mac_table = []
    for info in ip_mac_info:
        tmp =[]
        ip_mac_arp = set([info])
        if not ip_mac_arp & ipmac_set:
           tmp_info = info.split(',')
           ip = IPAddress(tmp_info[0])
           ip_version = ip.version
           ip_int = int(ip)
           tmp.append(tmp_info[0])
           tmp.append(tmp_info[1])
           tmp.append(0)
           tmp.append(ip64[str(ip_version)])
           tmp.append(ip_int)
           ip_mac_table.append(tuple(list(tmp)))
        #   print '\n'

    for i in range(len(ip_mac_table)):
        sql="insert into m_tbip_mac_defined (sSourceIP,sMac,iBind,sIPV,sSourceIPInt) values('%s','%s',%d,'%s',%d)"%ip_mac_table[i]
        cur.execute(sql)
    conn.commit()

    cur.execute(ipmac_table_sql)
    ipmac_in_table=cur.fetchall()
    ipmac_set=[]
    for ipmac_tmp in ipmac_in_table:
        ipmac_set.append(ipmac_tmp[0]+','+ipmac_tmp[1])
    ipmac_set=set(ipmac_set)

    if ip_mac_info^ipmac_set:
       remove_ip=ip_mac_info^ipmac_set
       remove_ip=list(tuple(remove_ip))
       for i in range(len(remove_ip)):
           delete_sql='delete from m_tbip_mac_defined where sSourceIP="%s"'%remove_ip[i].split(',')[0]
           cur.execute(delete_sql)

    conn.commit()
    cur.close()
    conn.close()


def on_off_ipmac_iptables(on_off):

    commands.getstatusoutput('/usr/sbin/iptables -D FORWARD -m state --state NEW -j IP_MAC_CHECK')
    commands.getstatusoutput('/usr/sbin/ip6tables -D FORWARD -m state --state NEW -j IP_MAC_CHECK')
    if on_off == '1':
        commands.getstatusoutput('/usr/sbin/iptables -I FORWARD -m state --state NEW -j IP_MAC_CHECK')
        commands.getstatusoutput('/usr/sbin/ip6tables -I FORWARD -m state --state NEW -j IP_MAC_CHECK')

def stop_start_ipmac():
    cur=mysql_connect()
    ipmac_bind_enable_sql='select sValue from m_tbconfig where sName="IPMacBind"'
    cur.execute(ipmac_bind_enable_sql)
    ipmac_bind_enable=cur.fetchall()
    if len(ipmac_bind_enable):
       enable=eval(ipmac_bind_enable[0][0])
       on_off_ipmac_iptables(enable['iTurnOn'])
    cur.close()


def bind_ipmac(process):

    if process=='auto':
       get_ipmac()
       return

    if not os.path.exists('/usr/local/bluedon/tmp/ipmac_bind.txt'):
       os.system('touch /usr/local/bluedon/tmp/ipmac_bind.txt')

    cur=mysql_connect()
    stop_start_ipmac()
    #ipmac_bind_enable_sql='select sValue from m_tbconfig where sName="IPMacBind"'
    #cur.execute(ipmac_bind_enable_sql)
    #ipmac_bind_enable=cur.fetchall()
    #if len(ipmac_bind_enable):
    #   enable=eval(ipmac_bind_enable[0][0])
    #   on_off_ipmac_iptables(enable['iTurnOn'])

    with open('/usr/local/bluedon/tmp/ipmac_bind.txt','r')as fr:
         for del_ipmac_info in fr:
             del_ipmac_info = del_ipmac_info.replace('\n','')
             commands.getstatusoutput(del_ipmac_info)
    commands.getstatusoutput('/usr/sbin/iptables -D IP_MAC_CHECK -j DROP')
    commands.getstatusoutput('/usr/sbin/ip6tables -D IP_MAC_CHECK -j DROP')

    iptables64 = {'4':'/usr/sbin/iptables',
                  '6':'/usr/sbin/ip6tables',
                  }

    sql='select sSourceIP,sMac,iLog from m_tbip_mac'
    cur.execute(sql)
    results=cur.fetchall()
    fw = open('/usr/local/bluedon/tmp/ipmac_bind.txt','w')
    for result in results:
        ip=result[0].replace('\r','')
        mac=result[1].replace('\r','')
        if ip and mac:
           ip = ip
           mac = mac
        else:
           continue

        log=result[2]
        IPV = IPAddress(ip)
        IPV = str(IPV.version)
        if log==1:

           iptables_log='%s -A IP_MAC_CHECK -s %s -m mac --mac %s -j LOG --log-prefix "ipt_log=RETURN "'%(iptables64[IPV],ip,mac)
           (status,output)=commands.getstatusoutput(iptables_log)
           getLogger('main').info('%s %s'%(iptables_log,output))
           print >>fw,iptables_log.replace('-A','-D')


        iptables_str='%s -A IP_MAC_CHECK -s %s -m mac --mac %s -j RETURN'%(iptables64[IPV],ip,mac)
        (status,output)=commands.getstatusoutput(iptables_str)
        getLogger('main').info('%s %s'%(iptables_str,output))
        print >>fw,iptables_str.replace('-A','-D')
    commands.getstatusoutput('/usr/sbin/iptables -A IP_MAC_CHECK -j DROP')
    commands.getstatusoutput('/usr/sbin/ip6tables -A IP_MAC_CHECK -j DROP')
    fw.close()
    cur.close()

def exception_iptables(iptables,nic_del):

    ret = os.system('%s IP_MAC_CHECK -i %s -j RETURN'%(iptables,nic_del))
    if ret:
       os.system('%s IP_MAC_CHECK -m physdev --physdev-in %s -j RETURN'%(iptables,nic_del))


def ipmac_exception():
    """
    ipmac绑定-->例外网口
    """
    if not os.path.exists('/usr/local/bluedon/tmp/ipmac_exception_nic.txt'):
       os.system('touch /usr/local/bluedon/tmp/ipmac_exception_nic.txt')

    cur=mysql_connect_dict()
    fr=open('/usr/local/bluedon/tmp/ipmac_exception_nic.txt','r')
    nic_delconfig=fr.readlines()
    for nic_del in nic_delconfig:
        nic_del=(nic_del.strip('\n'))
        exception_iptables('/usr/sbin/iptables -D',nic_del)
        exception_iptables('/usr/sbin/ip6tables -D',nic_del)
    fr.close()

    fw=open('/usr/local/bluedon/tmp/ipmac_exception_nic.txt','w')
    ipmac_exception_sql='select sPortName,sWorkMode from m_tbnetport where exStatus=1'
    cur.execute(ipmac_exception_sql)
    nic_config=cur.fetchall()
    for nic in nic_config:
        if nic['sWorkMode']=='bridge':
           os.system('/usr/sbin/iptables -I IP_MAC_CHECK -m physdev --physdev-in %s -j RETURN'%nic['sPortName'])
           os.system('/usr/sbin/ip6tables -I IP_MAC_CHECK -m physdev --physdev-in %s -j RETURN'%nic['sPortName'])
        else:
           os.system('/usr/sbin/iptables -I IP_MAC_CHECK -i %s -j RETURN'%nic['sPortName'])
           os.system('/usr/sbin/ip6tables -I IP_MAC_CHECK -i %s -j RETURN'%nic['sPortName'])
        print>>fw,nic['sPortName']
    fw.close()
    cur.close()

def ipmac_exception_ip():
    commands.getstatusoutput('/usr/local/sbin/ipset create exception_ip hash:net')
    commands.getstatusoutput('/usr/local/sbin/ipset flush exception_ip')
    commands.getstatusoutput('/usr/sbin/iptables -D IP_MAC_CHECK  -m set --match-set exception_ip src -j RETURN')
    cur=mysql_connect()
    exip_sql='select sValue from m_tbconfig where sName="IPMacExip"'
    cur.execute(exip_sql)
    exip = json.loads(cur.fetchall()[0][0])
    ip_list = exip['exip'].split('\r\n')
    [os.system('/usr/local/sbin/ipset add exception_ip %s'%tmp) for tmp in ip_list if tmp !='']
    commands.getstatusoutput('/usr/sbin/iptables -I IP_MAC_CHECK  -m set --match-set exception_ip src -j RETURN')
    cur.close()


def recover():
    open('/usr/local/bluedon/tmp/ipmac_bind.txt','w').close()
    open('/usr/local/bluedon/tmp/ipmac_exception_nic.txt','w').close()
    bind_ipmac('')
    ipmac_exception()
    ipmac_exception_ip()
    stop_start_ipmac()



if __name__=="__main__":

    if len(sys.argv)==2 and sys.argv[1]=='bind_ipmac':
        bind_ipmac('')
    elif len(sys.argv)==2 and sys.argv[1]=='exception_nic':
        ipmac_exception()
    elif len(sys.argv)==2 and sys.argv[1]=='exception_ip':
        ipmac_exception_ip()
    elif len(sys.argv)==2 and sys.argv[1]=='start_stop':
        stop_start_ipmac()
    elif len(sys.argv)==1:
        print '********'
        recover()
   #get_ipmac()

