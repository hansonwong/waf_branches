# coding:utf-8
"""
检测特定网口的ipv6地址是否包含在其它网口设置的地址中
此脚本提供给PHP使用

执行命令有以下两种方式：
    @param: {ipv6} 单个ipv6地址
    @param: {netport}: 目标端口
    python -m utils.check_ipv6 {ipv6} {netport}
    python -m /usr/local/bluedon/utils/check_ipv6 {ipv6} {netport}
"""
import sys
sys.path.append('/usr/local/bluedon')
from netaddr import IPNetwork, IPSet
from db.mysql_db import select


def is_addr_overlapping(ipv6_addr, netport):
    # 从数据库取出其它网口的ipv6地址
    sql = 'select sIPV6Address, sPortName from m_tbnetport where sPortName != "%s"' % netport
    result = select(sql)
    ipv6_set = IPSet(IPNetwork(ipv6_addr).cidr)
    for res in result:
        if not res['sIPV6Address']:
            continue
        addrs = res['sIPV6Address'].split(',')
        for addr in addrs:
            if not ipv6_set.isdisjoint(IPSet(IPNetwork(addr).cidr)):
                return '%s,%s' % (addr, res['sPortName'])
    return 'true'
    # 1: 表示传过来的ipv6地址已包含在其他网口设置的地址中, 不可用
    # 0: 表示传过来的ipv6地址不包含在其他网口设置的地址中，为可用


if __name__ == '__main__':
    if len(sys.argv) == 3:
        ipv6_addr = sys.argv[1]
        netport = sys.argv[2]
        print is_addr_overlapping(ipv6_addr, netport)
