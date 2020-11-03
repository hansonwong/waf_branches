#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json
import logging

from db.mysql_db import select_one, select
from utils.logger_init import logger_init

logger = logger_init('snmp', 'snmp.log', logging.INFO)
config_path = "/etc/snmp/snmpd.conf"


def config_snmp():
    sql = "select * from m_tbsnmp"
    set_sql = "select  sValue from m_tbconfig where sName = 'SnmpSwitch' "
    results = select(sql)
    turn_type = json.loads(select_one(set_sql)["sValue"])
    turn_type = str(turn_type["iTurnOnSnmp"])

    os.system("iptables -D FWINPUT -p udp --dport 161 -j ACCEPT")
    if turn_type != '1':
        os.system("killall snmpd")
        logger.info("killall snmpd")
        return

    os.system("iptables -I FWINPUT -p UDP --dport 161 -j ACCEPT")
    lines = []
    trap_lines = []

    for result in results:
        sname = result["sName"]
        groupname = result["sGroupName"]
        host_ip = result["sAddress"]
        adr_type = result["sAddrType"]
        pwd = "SHA %s" % result["sPassword"]
        encryption_pwd = "SHA %s DES %s" % (result["sPassword"], result["sEncryptionPassword"])
        addrtype = {"default": "default",
                    "host": host_ip,
                    "netSegment": host_ip}
        type_choice = {1: "noauth 1.3.6.1.2.1.1",
                       2: "auth 1.3.6.1.2.1",
                       3: "priv 1.3.6.1.2.1"}
        levers = {1: "",
                  2: pwd,
                  3: encryption_pwd}

        if result["sSnmpType"] == "v1":
            if result["sAddrType"] in addrtype:
                ips = addrtype[adr_type].split(',')
                cmd_str = ""
                for ip in ips:
                    cmd_str += "com2sec %s %s %s\n" % (sname, ip, groupname)
                cmd_str1 = "group user_group v1 %s\n" % sname
                cmd_str2 = "view user_view included .1\n"
                cmd_str3 = 'access  user_group  ""  any noauth exact user_view user_view none\n'
                lines.append(cmd_str)
                lines.append(cmd_str1)
                lines.append(cmd_str2)
                lines.append(cmd_str3)
                lines.append("\n")

        elif result["sSnmpType"] == "v2":
            if result["sAddrType"] in addrtype:
                ips = addrtype[adr_type].split(',')
                cmd_str = ""
                for ip in ips:
                    cmd_str += "com2sec %s %s %s\n" % (sname, ip, groupname)
                cmd_str1 = "group user_group v2c %s\n" % sname
                cmd_str2 = "view user_view included .1\n"
                cmd_str3 = 'access  user_group  ""  any noauth exact user_view user_view none\n'
                lines.append(cmd_str)
                lines.append(cmd_str1)
                lines.append(cmd_str2)
                lines.append(cmd_str3)
                lines.append("\n")

        elif result["sSnmpType"] == "v3":
            if int(result["iSecurityLever"]) in levers:
                cmd_str_v3 = "createUser %s %s\n" % (sname, levers[result["iSecurityLever"]])
                cmd_str1_v3 = "rwuser %s %s\n" % (sname, type_choice[result["iSecurityLever"]])
                lines.append(cmd_str_v3)
                lines.append(cmd_str1_v3)
                lines.append("\n")

        elif result["sSnmpType"] == "t1":
            ips = host_ip.split(',')
            for ip in ips:
                trap_lines.append('trapsink {}:162  {}\n'.format(ip, result['sGroupName']))

        elif result["sSnmpType"] == "t2":
            ips = host_ip.split(',')
            for ip in ips:
                trap_lines.append('trap2sink {}:162 {}\n'.format(ip, result['sGroupName']))

        elif result["sSnmpType"] == "t3":
            MD5 = sEncryptionPassword = ''
            if result['sPassword']:
                MD5 = ''.join(['MD5 ', result['sPassword']])
            if result['sEncryptionPassword']:
                sEncryptionPassword = ''.join(['DES ', result['sEncryptionPassword']])
            trap_lines.append('createUser -e {} {} {} {}\n'
                              .format(result['sTrapNum'], result['sName'], MD5, sEncryptionPassword))
            ips = host_ip.split(',')
            for ip in ips:
                trap_lines.append('trapsess -v3  -u {} -a SHA -A {} -l authPriv -e {} {}\n'
                                  .format(result['sName'], result['sPassword'], result['sTrapNum'], ip))

    if trap_lines:
        extra = '''authtrapenable 1

# Event MIB - automatically generate alerts
# #
# # Remember to activate the 'createUser' lines above
iquerySecName internalUser
rouser internalUser
# # generate traps on UCD error conditions
defaultMonitors yes
# # generate traps on linkUp/Down
linkUpDownNotifications yes
notificationEvent  linkUpTrap    linkUp   ifIndex ifAdminStatus ifOperStatus
notificationEvent  linkDownTrap  linkDown ifIndex ifAdminStatus ifOperStatus

monitor  -r 2 -e linkUpTrap   "Generate linkUp" ifOperStatus != 2
monitor  -r 2 -e linkDownTrap "Generate linkDown" ifOperStatus == 2
'''
        trap_lines.append(extra)

    with open(config_path, "w") as fp:
        fp.writelines(lines)
        fp.writelines(trap_lines)

    os.system("service snmpd restart")
    logger.info("service snmpd restart")


def initial_snmp():
    # 初始化
    config_path = "/etc/snmp/snmpd.conf"
    fp = open(config_path, "w")
    fp.close()
    os.system("killall snmpd")
    print "killall snmpd"


if __name__ == "__main__":
    # data = {"id":42,"sName":"test","sAddress":"","sAddrType":"default","sGroupName":"conn","sPassword":"","sEncryptionPassword":"","iSecurityLever":"","sSnmpType":"v1"}
    config_snmp()
    # initial_snmp()
