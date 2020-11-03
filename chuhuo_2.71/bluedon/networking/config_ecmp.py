#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
import json
from utils.log_logger import rLog_dbg, rLog_err

DBG = lambda x: rLog_dbg('network_ecmp', x)
ERR = lambda x: rLog_err('network_ecmp', x)


# IP(IP).make_net(Netmask).strNormal()

def exchange_mask(mask):
    """
    转换子网掩码格式
    """
    # 计算二进制字符串中 '1' 的个数
    count_bit = lambda bin_str: len([i for i in bin_str if i=='1'])

    # 分割字符串格式的子网掩码为四段列表
    mask_splited = mask.split('.')
    # 转换各段子网掩码为二进制, 计算十进制
    mask_count = [count_bit(bin(int(i))) for i in mask_splited]
    return sum(mask_count)

def con_ecmp(args):

    data = json.loads(args[1])
    target = data["sTargetAddress"]
    mask = data["sMask"]
    mask_count = exchange_mask(mask)
    NextJumpIP = data["sNextJumpIP"].split(',')
    weight = str(data["sWeight"]).split(',')
    #
    # port = data["sPort"]
    # ipv = data["sIPV"]
    status = data["iStatus"]

    if (args[0] in ['add','enable']) and status == 1:
        DBG('add args:%s, status:%s' % (args, status))

        cmd_add = 'ip route add %s/%s ' % (target, mask_count)
        for next_ip, next_weight in zip(NextJumpIP, weight):
            next_addr = 'nexthop via %s weight %s ' % (next_ip, next_weight)
            cmd_add += next_addr

        DBG('cmd_add：%s'% cmd_add)
        os.system(cmd_add)

    elif args[0] == 'del' or status == "0":
        DBG('del args:%s' % args)

        cmd_del = 'ip route del %s/%s ' % (target, mask_count)
        # for next_ip in NextJumpIP:
        for next_ip, next_weight in zip(NextJumpIP, weight):
            next_addr = 'nexthop via %s weight %s ' % (next_ip, next_weight)
            cmd_del += next_addr

        DBG('cmd_del：%s' % cmd_del)
        os.system(cmd_del)


def con_ecmp_del(args):

    DBG('del args:%s' % args)

    data = json.loads(args[0])
    target = data["sTargetAddress"]
    mask = data["sMask"]
    mask_count = exchange_mask(mask)
    NextJumpIP = data["sNextJumpIP"].split(',')
    weight = str(data["sWeight"]).split(',')
    # port = data["sPort"]
    # ipv = data["sIPV"]
    # status = data["iStatus"]

    cmd_del = 'ip route del %s/%s ' % (target, mask_count)
    for next_ip in NextJumpIP:
        next_addr = 'nexthop via %s weight %s ' % (next_ip, weight)
        cmd_del += next_addr

    DBG('cmd_add：%s' % cmd_del)
    os.system(cmd_del)

if __name__ == '__main__':
    print exchange_mask('255.255.254.0')
