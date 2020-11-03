#!/usr/bin/env python
# -*- coding:utf-8 -*-

import codecs
from utils.mask_transition import exchange_mask
from db.config import search_data as select


def file_filter():
    rules = []
    sql = 'SELECT ff.sName, ff.sIpGroup, ff.iIpGroupType, ff.sAction, ff.iLog, ' \
          'ftg.sFileExt FROM m_tbFileFilter AS ff, m_tbfiletypegroup AS ftg ' \
          'WHERE ff.sType=ftg.id AND ff.iStatus=1 ORDER BY snum;'
    rules_data = select(sql)
    for i in rules_data:
        # 获得文件扩展名
        fileexts = i.get('sFileExt', '')
        if not fileexts: continue
        fileexts = 'none' if fileexts == '*' else fileexts.replace('*', '')

        # 获得ip地址
        if int(i['iIpGroupType']) == 2:  # ip组
            sql = 'SELECT sIP FROM m_tbaddressgroup WHERE id=%s' % i['sIpGroup']
            ip_ids = select(sql)
            if not ip_ids: continue
            ip_ids = ip_ids[0]['sIP'].split(',')
        elif int(i['iIpGroupType']) == 1:  # ip
            ip_ids = [i['sIpGroup']]
        else:
            continue
        sql = 'SELECT sAddress, sAddtype, sNetmask FROM m_tbaddress_list ' \
              'WHERE id in (%s);' % ','.join(ip_ids)
        ips_data = select(sql)
        ips = []
        for ip in ips_data:  # ip格式转换
            if ip['sAddtype'] == '2':
                ips.append('%s:%s' % (ip['sAddress'], ip['sNetmask'].split('.')[-1]))
            else:
                net_mask = ip.get('sNetmask', '24')
                if '.' in net_mask:
                    net_mask = exchange_mask(net_mask)
                ips.append('%s/%s' % (ip['sAddress'], net_mask))

        line = u'name:%s;type:%s;src:%s;action:%s;log:%s;\n' % \
            (i['sName'], fileexts, ','.join(ips), i['sAction'], i['iLog'])
        rules.append(line)
        # print rules
    with codecs.open('/etc/suricata/conf/fkey.txt', 'w', 'utf-8') as f:
        f.write(''.join(rules))


if __name__ == '__main__':
    file_filter()



