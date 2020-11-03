#!/usr/bin/env/python
# *-* coding: utf-8 *-*

import os
import sys
from logging import getLogger
from utils.logger_init import logger_init
from utils.log_logger import rLog_dbg, rLog_alert
from IPy import IP
import commands


def process_cmd(cmd, info=''):
    ret = True
    (status, output) = commands.getstatusoutput(cmd)
    return status


def execute_cmd(cmd, log_name):
    " execute command and log status and output "
    status, output = commands.getstatusoutput(cmd)
    msg = 'status:%s | cmd:%s | output:%s' % (status, cmd, output)
    if status or not output:
        rLog_alert(log_name, msg)
    else:
        rLog_dbg(log_name, msg)
    return status, output


def device_down(device):
    process_cmd('ifconfig %s down' % device)


def device_up(device):
    process_cmd('ifconfig %s up' % device)


cmd_virutal_line_app = '/home/ng_platform/bd_dpdk_warper/clients/vir_line '


def add_virtual_line(iface1, iface2):
    cmd = cmd_virutal_line_app + 'add %s %s'
    process_cmd(cmd % (iface1, iface2))


def edit_virtual_line(iface1, iface2):
    cmd = cmd_virutal_line_app + 'edit %s %s'
    process_cmd(cmd % (iface1, iface2))


def del_virtual_line(iface1, iface2):
    cmd = cmd_virutal_line_app + 'del %s %s'
    process_cmd(cmd % (iface1, iface2))


cmd_load_bonding = 'modprobe bonding'
def load_bonding():
    process_cmd(cmd_load_bonding)


cmd_restart_network = '/usr/sbin/ifup %s'
def restart_network(bondname):
    process_cmd(cmd_restart_network % (bondname))


cmd_down_bond = 'ifconfig %s down'
def down_bond(bond):
    process_cmd(cmd_down_bond % bond)


add_or_del2 = lambda x: '+' if x else  '-'
cmd_add_bond_iface = 'echo %s%s> /sys/class/net/%s/bonding/slaves'
def add_iface_bond(iface, bond, add = True):
    process_cmd(cmd_add_bond_iface % (add_or_del2(add), iface, bond))
    if not add:
        process_cmd('rm -rf /etc/sysconfig/network-scripts/ifcfg-%s' %(iface))

cmd_del_bond = 'echo -%s > /sys/class/net/bonding_masters'
def del_bond(bond):
    process_cmd(cmd_del_bond % bond)
    process_cmd('rm -rf /etc/sysconfig/network-scripts/ifcfg-%s -f' % bond)
