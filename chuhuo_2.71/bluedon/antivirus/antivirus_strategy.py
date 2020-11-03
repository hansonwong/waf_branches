# coding:utf-8

import os
import json
from db.mysql_db import select
from utils.ip_handler import ip_list_by_source
from utils.log_logger import rLog_dbg, rLog_alert


ALL_PROTOCOL = 'all'
CONFIG_PATH = '/etc/suricata/conf/filter/av-policy.json'
DBG = lambda x: rLog_dbg('antivirus', x)
ALERT = lambda x: rLog_alert('antivirus', x)
directory = '/etc/suricata/conf/filter'
if not os.path.exists(directory):
    os.makedirs(directory)


def strategy_config():
    DBG('antivirus strategy start')
    sql = 'select * from m_tbevil_strategy where iStatus=1 order by iOrder desc'
    result = select(sql)
    strategys = []
    for res in result:
        ips, ip_type = ip_list_by_source(res['sSourceValue'], res['iSourceType'])
        if ip_type < 0:
            ALERT('Error type: %s sourcetype:%s sourcevalue:%s' % (ip_type, res['sSourceType'], res['sSourceValue']))
            continue
        strategy = {
            'Name': res['sName'],
            'Id': res['id'],
            'Ips': ips,
            'AllIp': ip_type,
            'Action': res['iAction'],
            'AllProto': 1 if res['sProtocol'] == ALL_PROTOCOL else 0,
            'Protocols': [] if not res['sProtocol'] or res['sProtocol'] == ALL_PROTOCOL else res['sProtocol'].split(','),
            'Log': res.get('iLog', 0),
        }
        DBG('strategy:%s' % strategy)
        strategys.append(strategy)
    with open(CONFIG_PATH, 'w') as f:
        f.write(json.dumps(strategys, indent=4))
    DBG('antivirus strategy end')


if __name__ == '__main__':
    strategy_config()
