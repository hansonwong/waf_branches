# coding:utf-8
import os
import json
from db.mysql_db import select
from utils.ip_handler import ip_list_by_source
from utils.log_logger import rLog_dbg, rLog_alert
from safetydefend.url_filter_common import get_urls_by_types
URL_CONF_PATH = '/etc/suricata/conf/filter/url-policy.json'
DBG = lambda x: rLog_dbg('url_filter', x)
ALERT = lambda x: rLog_dbg('url_filter', x)
directory = '/etc/suricata/conf/filter'
if not os.path.exists(directory):
    os.makedirs(directory)


def get_strategy_from_db():
    """ 从m_tburl_filter获取规则"""
    sql = 'select * from m_tburl_filter where iStatus=1 order by iOrder desc'
    datas = select(sql)
    return datas


def url_filter_strategy():
    DBG('url filter strategy start')
    ret = []
    url_types = []
    url_rules = get_strategy_from_db()
    # 先把所需规则取出来
    for rule in url_rules:
        rule['sUrlType'] = rule['sUrlType'].split(',') if rule['sUrlType'] else []
        if not rule['sUrlType']:
            ALERT('url_filter_strategy get urls by id %s' % rule['sUrlType'])
            continue
        url_types.extend(rule['sUrlType'])
    if not url_types:
        ALERT('url_filter strategy get no url types')
    urls_map, groupname_map = get_urls_by_types(url_types)
    DBG('urls_map: %s groupname_map: %s' % (urls_map, groupname_map))
    for rule in url_rules:
        if rule['sUrlType']:
            all_url = False
            urls = [{'url': urls_map[type_id], 'type': groupname_map[type_id]} for type_id in rule['sUrlType']]
        else:
            all_url = True
            urls = []
        address_list, ip_type = ip_list_by_source(rule['sSourceIPGroup'], rule['iSourceIPType'])
        if ip_type < 0:
            ALERT('incorrect source group:%s sourcetype:%s' % (rule['sSourceIPGroup'], rule['iSourceIPType']))
            continue
        DBG('handle id %s url filter strategy' % rule['id'])
        ret.append({
            'Name': rule['sName'],
            'AllIp': ip_type,
            'Ips': address_list,
            'AllUrl': int(all_url),
            'Urls': urls,
            'Action': rule['iAction'],
            'Id': rule['id'],
            'Log': rule.get('iLog', 0),
        })
    with open(URL_CONF_PATH, 'w') as f:
        f.write(json.dumps(ret, indent=4))
    DBG('url filter strategy end')


if __name__ == '__main__':
    url_filter_strategy()
