#!/usr/bin/env python
# coding=utf-8

import os
import time
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import collections
from netaddr import IPRange, IPNetwork, IPAddress
from config import fetchall_sql as fcal_3306

# RuleCmd = collections.namedtuple('RuleCmd', 'id_, snortid, jsonid, sip, iptype, reserve')
RuleCmd = collections.namedtuple('RuleCmd', 'id_, snortid, jsonid, iptype, sip, reserve')
cmd = '1#1,23,3,4#rule_json#1,2,3#1#{ct}'

rule_template_sql = 'SELECT * FROM m_tbaudit_rule_templates WHERE id in ({ids})'
rule_default_sql = 'SELECT * FROM m_tbaudit_rule_templates WHERE id not in ({ids})'
rule_default_sql_all = 'SELECT * FROM m_tbaudit_rule_templates WHERE 1=1'
rule_enable_sql = ('SELECT sSnortRuleTemplate, SourceIPGroup, iSourceIPType '
                   'FROM m_tbaudit_app_rules WHERE istatus=1;')

RELOAD_SURICATA_CMD = 'kill -12 `cat /var/run/suricata.pid`'
AUDIT_CMD_FILE = '/data/conf/bd_local_rulefiles/bd_applyfilter_*.rule'
AUDIT_RULE_FILE = '/etc/suricata/rules/bd_fw_audit_rules.rules'
JSON_OUTPUT_FILE = '/etc/suricata/conf/htp-audit.txt'

DROP_SID_MIN = 4200001
DROP_SID_MAX = 4300000

REJECT_SID_MIN = 4300001
REJECT_SID_MAX = 4400000

def make_rules(rule_list):
    rule_buffer = []
    rule_buf_count = 0
    rule_count = 0
    active_rule_set = set()
    print rule_list
    with open(AUDIT_RULE_FILE, 'w+') as fp:
        fp.write('')

    for rule in rule_list:
        if rule.snortid == 'NULL' or not rule.snortid:
            # log here
            print '[make_rules]get NULL snortid'
            continue
        if 'undefined' in rule.snortid:
            print '[make_rules]get NULL snortid'
            continue


        # add active rule to a set
        _rule_ids = rule.snortid.split(',')
        print '_rule_ids: ', _rule_ids
        active_rule_set = active_rule_set | set(_rule_ids)

        _sip = rule.sip
        _act = 'drop' # action is drop or reject, depend on IPS(drop) or IDS(reject) mode
        _classtype = ''
        print(rule_template_sql.format(ids=rule.snortid))
        for res in fcal_3306(rule_template_sql.format(ids=rule.snortid)):
            try:
                tpl = res.get('sTemplate')
                if _act == 'drop':
                    _sid = DROP_SID_MIN + rule_count
                    if _sid > DROP_SID_MAX:
                        # log here too much rule
                        break
                    rule_count += 1
                elif _act == 'reject':
                    _sid = REJECT_SID_MIN + rule_count
                    if _sid > REJECT_SID_MAX:
                        # log here too much rule
                        break
                    rule_count += 1
                    pass
                else:
                    # wrong action
                    break
                _classtype = 'app-{act}-{cltp}'.format(act=_act, cltp=res.get('sClassType'))
                _actual_rule =tpl.format(action=_act, sip=_sip, rule_name=res['sRuleName'],
                                         classtype=_classtype, sid=_sid)
                print _actual_rule

            except Exception as e:
                # log here
                print 'make audit rule error: %s' % e
                continue

            # cache rules in a list, write to file when get more then 1024 rules
            if rule_buf_count < 1024:
                rule_buffer.append(_actual_rule)
                rule_buf_count += 1
            else:
                with open(AUDIT_RULE_FILE, 'a+') as fp:
                    for r in rule_buffer:
                        fp.write('%s\n' % r)
                rule_buf_count = 0
                rule_buffer = []

    # if rules are less than 1024
    if rule_buf_count > 0:
        with open(AUDIT_RULE_FILE, 'a+') as fp:
            for r in rule_buffer:
                fp.write('%s\n' % r)
        rule_buf_count = 0

    rule_buffer = []

    # default rules
    if len(active_rule_set) == 0:
        default_rule = rule_default_sql_all

    else:
        default_rule = rule_default_sql.format(ids=','.join(active_rule_set))
    print active_rule_set
    print default_rule
    for res in fcal_3306(default_rule):
        tpl = res.get('sTemplate')
        _sid = res.get('iSid')
        _actual_rule =tpl.format(action='alert', sip='any', rule_name=res.get('sRuleName'),
                                 classtype=res.get('sClassType'), sid=_sid)

        rule_buffer.append(_actual_rule)

    with open(AUDIT_RULE_FILE, 'a+') as fp:
        for r in rule_buffer:
            fp.write('%s\n' % r)


    pass

def make_json_rules(rule_list):
    rule_buffer = []

    # clear content
    with open(JSON_OUTPUT_FILE, 'w+') as fp:
        fp.write('')

    for _rule in rule_list:
        if _rule.sip == 'any':
            rule_buffer.append('#'.join(['0.0.0.0', _rule.jsonid]))
        else:
            rule_buffer.append('#'.join([str(_rule.sip), _rule.jsonid]))
        if len(rule_buffer) > 1024:
            with open(JSON_OUTPUT_FILE, 'a+') as fp:
                for r in rule_buffer:
                    fp.write('%s\n' % r)
                rule_buffer = []

    if len(rule_buffer) > 0:
        with open(JSON_OUTPUT_FILE, 'a+') as fp:
            for r in rule_buffer:
                fp.write('%s\n' % r)

    pass


# parser for m_tbaddress_list[sIPJson] return a list of ip for snort rules'
def ip_parser(ip_str):
    ret = []
    try:
        ip_js = json.loads(ip_str)
    except Exception as e:
        # log here
        print('[make_rules] get wrong ip string %s, %s' % (ip_str, e))
        return ret

    # ip json has string like 'ip/mask'
    ip_mask = ip_js.get('ipmaskrange_int', None)
    if ip_mask is not None:
        if ip_mask == '0.0.0.0/0':
            ret.append('any')
        else:
            ret.append(ip_mask)

    # ip json is a range
    ip_range = ip_js.get('iprange', None)
    if ip_range is not None:
        _ipr = ip_range.split('-')
        if len(_ipr) != 2:
            # log here
            print('[make_rules] get wrong iprange %s' % ip_range)
        else:
            ret = IPRange(_ipr[0], _ipr[1])

    # ip json is a single ip
    ip_single = ip_js.get('ipmaskalone_int', None)
    if ip_single is not None:
        _ip = IPNetwork(ip_single)
        ret.append(str(_ip.ip))
    return ret

# return a dict of ip and a list of id consist of ids in m_tbaddress_list
def get_address_list():
    addr_dict = dict()
    get_addr_sql = 'SELECT id, sIPJson FROM m_tbaddress_list;'
    for res in fcal_3306(get_addr_sql):
        addr_dict[res['id']] = res['sIPJson']

    addr_group = dict()
    get_addr_group = 'SELECT id, sIP FROM m_tbaddressgroup;'
    for res in fcal_3306(get_addr_group):
        addr_group[res['id']] = [int(i) for i in res['sIP'].split(',')]

    return addr_dict, addr_group


def reload_suricata():
    os.system(RELOAD_SURICATA_CMD)
    pass



# get address ID, generate the rules for those ip
def make_rules_for_ip(_ip_str, _rules_id):
    pass


def make_rules_from_file(cmd_path):
    if not os.path.exists(cmd_path):
        # log here
        print '%s is not exists' % cmd_path
        return

    # read cmd from file
    with open(cmd_path, 'r') as fp:
        cmd_lines = fp.readlines()

    make_rules_list = list()
    # get address list and address group first
    addr, addr_group = get_address_list()
    print addr
    # get address_id, address_type, and rules_id from db
    for line in cmd_lines:
        _cmd = RuleCmd._make(line.split('#'))
        print _cmd
        # ip group
        if _cmd.iptype == 'NULL':continue
        if int(_cmd.iptype) == 2:
            group_id = addr_group.get(int(_cmd.sip))
            if len(group_id) == 0:
                # log here wrong ip group
                continue
            for _id in group_id:
                # addr[id] --> get json description of ip
                # ip_parser return a list of ip get from addr[id]
                _all_sip = ip_parser(addr[_id])
                for _sip in _all_sip:
                    # _rule = RuleCmd(_cmd.id_, _cmd.snortid.strip(','), _cmd.jsonid, _sip, _cmd.iptype, _cmd.reserve)
                    _rule = RuleCmd(_cmd.id_, _cmd.snortid.strip(','), _cmd.jsonid, _cmd.iptype, _sip, _cmd.reserve)
                    make_rules_list.append(_rule)
        # ip
        elif int(_cmd.iptype) == 1:
            # addr[id] --> get json description of ip
            # ip_parser return a list of ip get from addr[id]
            _addr_id = int(_cmd.sip)
            _all_sip = ip_parser(addr[_addr_id])
            for _sip in _all_sip:
                # _rule = RuleCmd(_cmd.id_, _cmd.snortid.strip(','), _cmd.jsonid, _sip, _cmd.iptype, _cmd.reserve)
                _rule = RuleCmd(_cmd.id_, _cmd.snortid.strip(','), _cmd.jsonid, _cmd.iptype, _sip, _cmd.reserve)
                make_rules_list.append(_rule)

        # wrong argument
        else:
            # log here
            print '[make_rules]get wrong argument %s' % line
            pass

    try:
        # print make_rules_list
        make_rules(make_rules_list)
        make_json_rules(make_rules_list)

        reload_suricata()
        pass
    except Exception as e:
        # log here
        print '[make_rules] error %s' % e

if __name__ == '__main__':
    # make_rules(cmd.format(ct=int(time.time())))
    # sql = 'SELECT sIPJson FROM m_tbaddress_list;'
    # for res in fcal_3306(sql):
    #     print res
    #     for ip in ip_parser(res['sIPJson']):
    #         print ip

    # make_rules_from_db()
    make_rules_from_file('/data/conf/bd_local_rulefiles/bd_applyfilter_2016.12.15.10.44.46.rule')
    pass
