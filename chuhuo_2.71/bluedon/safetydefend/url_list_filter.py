# coding:utf-8
import os
import json
from db.mysql_db import select
from utils.log_logger import rLog_dbg, rLog_alert
from safetydefend.url_filter_common import get_urls_by_types
DBG = lambda x: rLog_dbg('url_filter', x)
ALERT = lambda x: rLog_alert('url_filter', x)
directory = '/etc/suricata/conf/filter'
if not os.path.exists(directory):
    os.makedirs(directory)


class UrlListFilter():
    def __init__(self):
        pass

    def get_list_data_from_db(self):
        sql = 'select * from %s where iStatus=1 order by iOrder desc' % self.tb
        return select(sql)

    def entry(self):
        DBG('url list filter start')
        url_types = []
        rules = self.get_list_data_from_db()
        if not rules:
            ALERT('no data in list to filter')
        url_types = [rule['sUrlType'] for rule in rules] if rules else []
        DBG('url type:%s' % url_types)
        if not url_types:
            ALERT('no type setting')
        urls_map, groupname_map = get_urls_by_types(url_types)
        ret = [{
            'url': urls_map[rule['sUrlType']],
            'type': groupname_map[rule['sUrlType']],
            'log': rule.get('iLog', '0'),
        } for rule in rules] if rules else []
        with open(self.path, 'w') as f:
            f.write(json.dumps(ret, indent=4))
        DBG('url list filter end')


class UrlBlackListFilter(UrlListFilter):
    def __init__(self):
        self.tb = 'm_tburlblacklist'
        self.path = '/etc/suricata/conf/filter/url-black.json'


class UrlWhiteListFilter(UrlListFilter):
    def __init__(self):
        self.tb = 'm_tburlwhilelist'
        self.path = '/etc/suricata/conf/filter/url-white.json'


if __name__ == '__main__':
    UrlBlackListFilter().entry()
    UrlWhiteListFilter().entry()
