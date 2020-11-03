#! /usr/bin/env python
# -*- coding:utf-8 -*-

from utils.mask_transition import exchange_mask, int_to_strmask


def ip2num(ip):
    ip = [int(x) for x in ip.split('.')]
    # print ip
    return ip[0] << 24 | ip[1] << 16 | ip[2] << 8 | ip[3]


def num2ip(num):
    return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24,
                            (num & 0x00ff0000) >> 16,
                            (num & 0x0000ff00) >> 8,
                            num & 0x000000ff)


def get_ip(ip):
    start, end = [ip2num(x) for x in ip.split('-')]
    return [num2ip(num) for num in range(start, end + 1) if num & 0xff]


def ex_mask(mask):
    """
    args:
        mask: '24' or '255.255.255.0'
    returns:
        mask1: int
        mask2: str
    """
    mask1 = exchange_mask(mask)
    mask2 = int_to_strmask(mask)
    return mask1, mask2


def deal_ip(ip_, mask='32'):
    mask1, mask2 = ex_mask(mask)
    rets = None
    mark = 'single'
    if ip_ == '0.0.0.0' or mask2 == '0.0.0.0':
        if ip_ == '0.0.0.0' and mask2 == '0.0.0.0':
            rets = '{}/{}'.format(ip_, mask)
            mark = 'iprange'
        else:
            mark = None
    else:
        if mask1 == '32' or mask1 == 32:
            rets = ip_
        else:
            try:
                ips = ip_.split('.')
                ip = [int(i) for i in ips]
                m_ = mask2.split('.')
                m = [int(i) for i in m_]

                if (ip[0] & m[0] == ip[0]) and (ip[1] & m[1] == ip[1]) and \
                    (ip[2] & m[2] == ip[2]) and (ip[3] & m[3] == ip[3]):
                    rets = '{}/{}'.format(ip_, mask1)
                    mark = 'iprange'
                else:
                    rets = ip_
            except:
                pass
    return rets, mark


if __name__ == '__main__':
    # iplist = get_ip('172.16.3.1-172.16.3.21')
    # a = [i for i in iplist]
    print deal_ip('170.20.2.255', '27')
