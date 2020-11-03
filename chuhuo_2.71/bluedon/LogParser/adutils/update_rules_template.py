#!/usr/bin/env python
# coding=utf-8


import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from config import execute_sql as exec_3306

RULES_PATH = '/etc/suricata/rules'
RULE_SET = ('bd-local-game.rules', 'bd-local-p2p.rules', 'bd-local-proxy.rules',
            'bd-local-trojan.rules', 'bd-local-stock.rules')


def rule_parser(rule_path):
    # insert sql
    sql = "INSERT INTO m_tbaudit_rule_templates (sRuleName, sClassType, sTemplate, iSid) values('{n}', '{typ}', '{tpl}', '{sid}');"
    with open(rule_path, 'r') as fp:
        rules = fp.readlines()

    for rule in rules:
        # ignore comment
        if rule.startswith('#'):
            continue

        if rule == '\n':
            continue

        # generate template
        rule_full = '{rule_option} {rule_content}'
        rule_items = rule.split()
        if len(rule_items) < 6:
            continue
        rule_proto = rule_items[1]
        rule_sport = rule_items[3]
        rule_dip = rule_items[5]
        rule_dport = rule_items[6]
        if rule_proto not in ('tcp', 'udp', 'http', 'dns', 'icmp'):
            print 'WARNNING: protocol %s is not recognized' % rule_proto
        rule_option = '{action} %s {sip} %s -> %s %s' % (rule_proto, rule_sport, rule_dip, rule_dport)

        # get rule name from rule
        reg_rule_name = r'(?<=\(msg:").+?(?=";)'
        re_ret = re.search(reg_rule_name, rule, re.DOTALL)
        rule_name = re_ret.group(0)
        # print 'get rule name [%s]' % rule_name

        # get classtype
        reg_rule_type = r'(?<=classtype:).+?(?=;)'
        re_ret = re.search(reg_rule_type, rule, re.DOTALL)
        rule_type = re_ret.group(0).strip()
        # print 'get rule type [%s]' % rule_type

        # get rule content
        reg = r'\(msg.*\)'
        re_ret = re.search(reg, rule, re.DOTALL)
        rule_content = re_ret.group(0)
        # rule_content_r = rule_content.replace(rule_name, '{rule_name}')
        # rule_content_r = rule_content_r.replace(rule_type, '{classtype}')

        # get rev id
        # reg_rev_id = r'(?<=rev:)\d+?(?=;)'

        # get sid
        reg_sid_id = r'(?<=sid:).+?(?=;)'
        re_ret = re.search(reg_sid_id, rule, re.DOTALL)
        # print 'processing :', rule
        rule_sid = re_ret.group(0)

        # print 'get rule content [%s]' % rule_content
        # replace
        rule_content = re.sub(reg_rule_name, '{rule_name}', rule_content)
        rule_content = re.sub(reg_rule_type, '{classtype}', rule_content)
        rule_content = re.sub(reg_sid_id, '{sid}', rule_content)
        # print 'replace content\n %s' % rule_content

        # generate template
        rule_template = rule_full.format(rule_option=rule_option, rule_content=rule_content)
        # print rule_template

        # insert into database
        _insert_sql = sql.format(n=rule_name, typ=rule_type, tpl=rule_template, sid=rule_sid)
        # print _insert_sql
        exec_3306(_insert_sql)


def parse_rule_files(path):
    # truncate table first
    _truncate_sql = 'truncate table m_tbaudit_rule_templates;'
    exec_3306(_truncate_sql)
    for path, dirs, files in os.walk(path):
        for f in files:
            if f not in RULE_SET:
                continue
            rule_path = os.path.join(path, f)
            print 'processing rule file[%s]' % rule_path
            rule_parser(rule_path)

if __name__ == '__main__':
    parse_rule_files(RULES_PATH)
    pass


