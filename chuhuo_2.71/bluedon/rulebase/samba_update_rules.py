#!/usr/bin/env python
# coding=utf-8

import os
import sys
from collections import defaultdict

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from rulebase.samba_down import smb_downfile, smb_get_filelsit
from rulebase.rule_update import IpsRuleUpdate, AvRuleUpdate, WAFRuleUpdate
from db.config import fetchall_sql as fcal3306
from db.config import fetchone_sql as fetch3306
from utils.log_logger import rLog_dbg, rLog_err


# debug function
# def DBG(x):
#     print x
# 
# def ERR(x):
#     print x
LOGGER_NAME = 'smb_auto_update'
DBG = lambda x : rLog_dbg(LOGGER_NAME, x)
ERR = lambda x : rLog_err(LOGGER_NAME, x)

IPS_UPDATE_PATCH_PREFIX = 'IPS_rules_'
WAF_UPDATE_PATCH_PREFIX = 'WAF_rules_'
AV_UPDATE_PATCH_PREFIX = 'AV_rules_'

SUPPORT_TYPE = ['WAF', 'AV', 'IPS']
TYPE_PREFIX = {
    'WAF': WAF_UPDATE_PATCH_PREFIX,
    'IPS': IPS_UPDATE_PATCH_PREFIX, 
    'AV': AV_UPDATE_PATCH_PREFIX
    }

TYPE_UPDATE_FUNC = {
    'WAF': WAFRuleUpdate,
    'IPS': IpsRuleUpdate, 
    'AV':AvRuleUpdate 
    }

def get_smb_setting(file_type):
    if file_type not in SUPPORT_TYPE:
        ERR('file type [%s] not support' % file_type)
        raise
    
    # get id of file_type
    sql = 'SELECT * FROM m_tbrolelib WHERE sRelationLib="{}"'.format(file_type)
    ret = fetch3306(sql)
    if ret['iAutoUpdate'] == 0:
        DBG('%s AutoUpate not Enable' % file_type)
        return None, None, None
    _id = ret['id']
    # e.g. v1.x.x.x
    version = ret['sCurrentVersion'].strip('v')

    if not _id:
        ERR('cannot find id for %s' % file_type)
        raise

    # get smb server setting from m_tbrolelib_autoupdate
    sql = 'SELECT iTurnOn, sUpdateServerIP, sUpdateServerPort \
        FROM m_tbrolelib_autoupdate WHERE iLibId={};'.format(_id)

    ret = fetch3306(sql)
    DBG(sql)
    DBG(ret)
    
    # return smb servce ip, port and current version of file_type
    return ret['sUpdateServerIP'], ret['sUpdateServerPort'], version
    

def update_rules():
    for file_type in SUPPORT_TYPE:
        DBG('Processing %s' % file_type)
        _get_update_conf(file_type)

def _get_update_conf(file_type):
    host_ip, port, current_ver = get_smb_setting(file_type)
    if host_ip is None or port is None:
        DBG('No need or No Setting for %s to update' % file_type)
        return
    type_prefix = TYPE_PREFIX[file_type]
    ret = dict()
    rule_file = defaultdict(list)
    DBG('fetching files from %s:%s' % (host_ip, port))
    new_files_on_server = smb_get_filelsit(host_ip)
    DBG('all files in server')
    DBG(new_files_on_server)

    for f in new_files_on_server:
        if f.startswith(type_prefix):
            if f.endswith('.tar.gz'):
                name_ver = f.replace('.tar.gz', '')
                ver = name_ver.split('_')[-1]
            rule_file[file_type].append(dict(ver=ver, fname=f))

    DBG('rule_file of %s' % file_type)
    DBG(rule_file)


    for _file in rule_file[file_type]:
        n_ver = _file['ver']
        n_file = _file['fname']
        DBG('comparing {o} to {n}...'.format(o=current_ver, n=n_ver))
        if n_ver > current_ver:
            DBG('updating {o} to {n}...'.format(o=current_ver, n=n_ver))
            ret = smb_downfile(n_file)
            TYPE_UPDATE_FUNC[file_type](ret[0], n_ver).main()
            break

if __name__ == '__main__':
    # os.system('systemctl stop firewall_autoupdate_cron_task.timer')
    update_rules()
    # os.system('systemctl start firewall_autoupdate_cron_task.timer')
    pass
