#!/usr/bin/env python
# coding=utf-8


"""
    2016-10-10:
        Plus all tx/rx as global interface rate
    2016-10-18:
        Use interface with smaller number as inter-net
    2016-10-26:
        Use just one interface's data of a 2-interface bridge
    2016-11-04:
        Get PortMode from Database
"""

from __future__ import division
import os
import psutil
import time
import operator


_rx = operator.itemgetter(0)
_tx = operator.itemgetter(1)

_pre_pre_ns = {}

def bytes2human(n):
    """
        >>> bytes2human(10000)
        '9.8 K'
        >>> bytes2human(100001221)
        '95.4 M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % (n)


def bits2human(n):
    """
        >>> bytes2human(10000)
        '9.8 K'
        >>> bytes2human(100001221)
        '95.4 M'
    """
    symbols = ('Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f b' % (n)


def is_vEth(x):
    return x[0:4] == 'vEth'


def get_net_io():
    _net_io = {}
    stat = psutil.net_io_counters(pernic=True)
    for ifname in stat:
        if is_vEth(ifname):
            _net_io[ifname] = (stat[ifname].bytes_recv,
                               stat[ifname].bytes_sent)
    return _net_io


def print_net_speed(ns):
    os.system('clear')
    print('{:<6}:  {:<16}| {:<16}'.format('IFace','IN','OUT'))
    for vEth in sorted(ns):
        print('{:<6}:  {:<16}| {:<16}'.format(vEth,ns[vEth]['IN'], ns[vEth]['OUT']))


def add_unit(i):
    i = int(i)/1048576
    return round(i, 4) if i < 1 else round(i, 2)


def get_net_speed(_pre_io, _pre_t, nat=None, bridges=None, portsinfo=None):
    ns = {}
    _ns = {}
    raw_ns = {}
    post_ns = {}   # save net speed after process
    gin, gout = (0, 0)
    _cur_io = get_net_io()
    _cur_t = time.time()
    dt = _cur_t - _pre_t

    for vEth in _cur_io:
        # try:
        if vEth not in _pre_io:
            _pre_io[vEth] = (0, 0)

        """
            IN  ---> download
            OUT ---> upload
        """
        rx = (_rx(_cur_io[vEth]) - _rx(_pre_io[vEth])) / dt
        tx = (_tx(_cur_io[vEth]) - _tx(_pre_io[vEth])) / dt

        rx = 0 if rx < 0 else rx
        tx = 0 if tx < 0 else tx

        # save original speed first
        raw_ns[vEth] = (rx, tx)
        global _pre_pre_ns
        if _pre_pre_ns:
            pre_rx = _rx(_pre_pre_ns.get(vEth, (0, 0)))
            pre_tx = _tx(_pre_pre_ns.get(vEth, (0, 0)))

            # fliter
            if abs(rx - pre_rx) > 0.45 * pre_rx:
                _r = rx
                rx = (rx - pre_rx) * 0.25 + pre_rx
                # if _r == 0 and rx < 0.001:rx = 0
                # print ('rx change too fast: rx_old={:16.8f}, '
                #        'rx_new={:16.8f}, pre_rx={:16.8f}').format(_r, rx, pre_rx)

            if abs(tx - pre_tx) > 0.45 * pre_tx:
                _t = tx
                tx = (tx - pre_tx) * 0.25 + pre_tx
                # if _t == 0 and tx < 0.001:tx = 0
                # print ('tx change too fast: tx_old={:16.8f}, '
                #        'tx_new={:16.8f}, pre_tx={:16.8f}').format(_t, tx, pre_tx)


        # raw_ns[vEth] = (rx, tx)
        post_ns[vEth] = (rx, tx)

        # if nat is not None and vEth in nat:
        if portsinfo is not None and vEth in portsinfo:
            if str(portsinfo.get(vEth, 0)) == '1':
                ns[vEth] = {'IN': bits2human(rx * 8),
                            'OUT': bits2human(tx * 8)}

                _ns[vEth] = {'IN': add_unit(tx * 8),
                             'OUT': add_unit(rx * 8)}

                gin += tx * 8
                gout += rx * 8

            # else:
            # outer-port
            elif str(portsinfo.get(vEth, 0)) == '2':
                ns[vEth] = {'IN': bits2human(tx * 8),
                            'OUT': bits2human(rx * 8)}

                _ns[vEth] = {'IN': add_unit(rx * 8),
                             'OUT': add_unit(tx * 8)}

        # ns[vEth] = {'IN': (_rx(_cur_io[vEth]) - _rx(_pre_io[vEth])) / dt,
        #             'OUT': (_tx(_cur_io[vEth]) - _tx(_pre_io[vEth])) / dt}

        pass
        # except KeyError:
        #     pass

    # # choose the bigger rate as download rate 2016-10-10
    # if gout > gin:
    #     gout, gin = gin, gout

    # bridge
    # if portsinfo is not None:
    #     for port in portsinfo:
    #         # 1 for inter-port, 2 for outer-port
    #         if not str(portsinfo[port]) == '2':
    #             continue

    #         # just one interface's data
    #         try:
    #             gin += (_tx(post_ns[port])) * 8
    #             gout += (_rx(post_ns[port])) * 8
    #         except:
    #             print 'can\'t get netport [%s]speed' % port

    #         pass

    _ns['GLOBAL'] = {'IN': add_unit(gin), 'OUT': add_unit(gout)}

    # print _ns

    _pre_pre_ns = raw_ns

    return _cur_io, _cur_t, ns, _ns


class NetIO(object):
    def __init__(self):
        pass

if __name__ == '__main__':
    pre_io = get_net_io()
    pre_t = time.time()
    speed = {}
    try:
        while 1:
            print pre_io
            pre_io, pre_t, speed, _  = get_net_speed(pre_io, pre_t)
            print_net_speed(speed)

            time.sleep(2)
    except KeyboardInterrupt:
        pass
    pass
