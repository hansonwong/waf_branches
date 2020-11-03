#! /usr/bin/env python
# -*-coding:utf-8-*-

from db.mysqlconnect import mysql_connect,mysql_connect_dict
from system.ha import init_tenv
import codecs
import os
import commands
import subprocess
import re
import sys

from networking.keep_pppoe import start_keep_pppoe_if_need


def find_ip_mask(cmd):
    ipstr = '([0-9]{1,3}\.){3}[0-9]{1,3}'
    maskstr = '0x([0-9a-f]{8})'
    #ipconfig_process = subprocess.Popen("%s"%cmd, stdout=subprocess.PIPE)
    #output = ipconfig_process.stdout.read()
    output=os.popen('%s'%cmd).read()
    ip_pattern = re.compile('(inet %s)' % ipstr)
    pattern = re.compile(ipstr)
    iplist = []
    for ipaddr in re.finditer(ip_pattern, str(output)):
        ip = pattern.search(ipaddr.group())
        if ip.group() != "127.0.0.1":
           iplist.append(ip.group())

    mask_pattern = re.compile('(netmask %s)' % ipstr)
    pattern = re.compile(ipstr)
    masklist = []
    for maskaddr in mask_pattern.finditer(str(output)):
        mask = pattern.search(maskaddr.group())
        if mask.group() != '0xff000000' and mask.group() != '255.0.0.0':
           masklist.append(mask.group())
    return iplist,masklist


def ppp_add(config_file,ETH,user,cur):
    os.system('touch %s'%config_file)
#    os.system('cp /etc/ppp/pppoe.conf %s'%config_file)
    f_conf=open('/etc/ppp/pppoe.conf','r')
    f_newconf=codecs.open(config_file,'w','utf-8')
    unit_id = ''.join([i for i in ETH if i in '0123456789'])
    ETH="ETH=%s"%ETH
    USER="USER=%s"%user
    for line in f_conf.readlines():
        if "ETH" in line:
           f_newconf.write(ETH+"\n")
        elif "USER" in line:
           f_newconf.write(USER+"\n")
        elif "DEFAULTROUTE" in line:
            continue
        else:
           f_newconf.write(line)
    f_newconf.write('UNIT=%s\n' % unit_id)
    f_newconf.write("DEFAULTROUTE=no"+"\n")
    f_conf.close()
    f_newconf.close()

    (status,result)=commands.getstatusoutput('/usr/sbin/pppoe-start %s'%config_file)
    cmd='/usr/sbin/pppoe-status %s'%config_file
    (ip,mask)=find_ip_mask(cmd)
    #ip=['192.168.198.106']
    #mask=['255.255.255.0']
    cur.execute("update m_tbdialdevice set sIP='%s',sMask='%s' where sUserName='%s'"%(''.join(ip),''.join(mask),user))


def ppp_data(process,info): #配置拨号设备
    os.system('systemctl stop keep-pppoe')
    info=eval(info)
    user=info['sUserName']
    passwd=info['sPassword']
    device=info['sBindPort']
    ETH=info['sBindPort']
    status=int(info['iStatus'])

    f_pap=codecs.open('/etc/ppp/pap-secrets','w','utf-8')
    f_chap=codecs.open('/etc/ppp/chap-secrets','w','utf-8')
    cur=mysql_connect()
    getsql='select * from m_tbdialdevice'
    cur.execute(getsql)
    results=cur.fetchall()
    for result in results:           #记录用户及密码
        username=result[5]
        password=result[6]
        line='"%s"  *    "%s"'%(username,password)
        print >>f_pap,line
        print >>f_chap,line
    f_pap.close()
    f_chap.close()

    config_file='/etc/ppp/pppoe.conf-%s'%user
    config_file=config_file.encode('utf-8')

    if process=="add":
       ppp_add(config_file,ETH,user,cur)

    if process=="del":
       (status,result)=commands.getstatusoutput('/usr/sbin/pppoe-stop %s'%config_file)
       os.system('rm -f %s'%config_file)

    if process=='enable':
       if status==1:
          if os.path.exists(config_file):
             (status,result)=commands.getstatusoutput('/usr/sbin/pppoe-start %s'%config_file)
             cmd='/usr/sbin/pppoe-status %s'%config_file
             (ip,mask)=find_ip_mask(cmd)
             cur.execute("update m_tbdialdevice set sIP='%s',sMask='%s' where sUserName='%s'"%(''.join(ip),''.join(mask),user))
          else:
             ppp_add(config_file,ETH,user,cur)

       else:
          (status,result)=commands.getstatusoutput('/usr/sbin/pppoe-stop %s'%config_file)
    cur.close()
    start_keep_pppoe_if_need()  # 如果需要就启动服务保持pppoe在线


def recover():

    if len(sys.argv) == 1:
        return

    cur = mysql_connect_dict()
    pppoe_sql='select * from m_tbdialdevice where iStatus=1'
    cur.execute(pppoe_sql)
    pppoe_info=cur.fetchall()
    if len(pppoe_info):
        for pppoe_data in pppoe_info:
            pppoe_data=str(pppoe_data)
            if sys.argv[1] == 'factory_recover':
                ppp_data('del',pppoe_data)
            if sys.argv[1] == 'boot_recover':
                ppp_data('add',pppoe_data)
    cur.close()
    start_keep_pppoe_if_need()  # 如果需要就启动服务保持pppoe在线

if __name__=="__main__":
   recover()
