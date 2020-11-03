#! /usr/bin/env python
# -*-coding:utf-8-*-

import os
import chardet
from operator import itemgetter
from itertools import groupby
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import linecache
import re
from netaddr import *
from IPy import IP

from db.mysqlconnect import mysql_connect_dict,mysql_connect,mysql_connect_dict_3307,mysql_connect_3307
from system.ha import init_tenv
from utils.mask_transition import exchange_mask
from system.system_config import ips_switch



classtype_info={'attempted-admin':'管理员特权获取-未遂',
           'attempted-user':'用户特权获取-未遂',
           'inappropriate-content':'不当内容检测',
           'policy-violation':'潜在的侵犯企业隐私',
           'shellcode-detect':'检测可执行代码',
           'successful-admin':'管理员特权获取-成功',
           'successful-user':'用户特权获取-成功',
           'trojan-activity':'网络木马 ',
           'unsuccessful-user':'用户特权获取-失败',
           'web-application-attack':'web应用攻击',
           'attempted-dos':'拒绝服务-未遂',
           'attempted-recon':'信息泄露-未遂',
           'bad-unknown':'潜在不良流量',
           'default-login-attempt':'试图通过默认的用户名和密码登录',
           'denial-of-service':'拒绝服务-成功',
           'misc-attack':'其他攻击',
           'non-standard-protocol':'非标准协议及事件',
           'rpc-portmap-decode':'非正常RPC解码',
           'successful-dos':'拒绝服务-成功',
           'successful-recon-largescale':'大量信息泄露-成功',
           'successful-recon-limited':'信息泄露-成功',
           'suspicious-filename-detect':'检测到可疑文件名',
           'suspicious-login':'未遂可疑用户名登陆',
           'system-call-detect':'检测系统调用',
           'unusual-client-port-connection':'客户端非正常端口使用',
           'web-application-activity':'Web应用程序脆弱性攻击',
           'icmp-event':'通用ICMP事件',
           'misc-activity':'其他行为',
           'network-scan':'网络扫描',
           'not-suspicious':'常规流量',
           'protocol-command-decode':'通用协议命令解码',
           'string-detect':'检测到可疑字符串',
           'unknown':'未知流量',
           'tcp-connection':'检测TCP连接'
          }

def custom_ips_rule():
    """
    根据ips规则的格式，填写完整IPS自定义规则
    """
    classtype_dict={}
    for key in classtype_info:
        value=classtype_info[key].decode('utf-8').strip(' ')
        classtype_dict[value]=key

    cur=mysql_connect_dict()
    sql='select * from m_tbcustom_ips_lib where iCustomOrInset=1'
    cur.execute(sql)
    results=cur.fetchall()
    frule=open('/etc/suricata/custom.rules','w')
    for result in results:
        action=result['sAction']
        sid=str(result['sRuleID'])
        msg=result['sDesc']
        classtype=classtype_dict[result['sRuleType'].decode('utf-8')]
        content=''
        distance=''
        depth=''
        within=''
        offset=''
        string=eval(result['sCharacterString'])
        if string['content']:
           content='content:"%s";'%string['content']
        if string['distance']:
           distance='distance:%s;'%string['distance']
        if string['depth']:
           depth='depth:%s;'%string['depth']
        if string['within']:
           within='within:%s;'%string['within']
        if string['offset']:
           offset='offset:%s;'%string['offset']
        protocol=result['sProtocol']
        if int(result['iChartCaseSensitive'])==1:
           rule='%s %s $EXTERNAL_NET any -> $HOME_NET any (msg:"%s"; %s %s %s %s %s classtype:%s; sid:%s; rev:1;)'%(action,protocol,msg,content,offset,depth,within,distance,classtype,sid)

        else:
           if content:
              rule='%s %s $EXTERNAL_NET any -> $HOME_NET any (msg:"%s"; %s nocase; %s %s %s %s classtype:%s; sid:%s; rev:1;)'%(action,protocol,msg,content,offset,depth,within,distance,classtype,sid)
           else:
              rule='%s %s $EXTERNAL_NET any -> $HOME_NET any (msg:"%s";%s%s%s%s%s classtype:%s; sid:%s; rev:1;)'%(action,protocol,msg,content,offset,depth,within,distance,classtype,sid)
        print >>frule,rule
        sql = "update m_tbcustom_ips_lib set sRule='%s',sRuleBelongFile='%s' where sRuleID='%s'"%(rule,'/etc/suricata/custom.rules',sid)
        cur.execute(sql)
    cur.close()
    frule.close()

def template_rule(ruleID):
    """
    若模板不是标准模板，则将模板中的规则在指定文件中另生成
    """
    cur = mysql_connect_dict()
    template_rule = []
    template_rule_append = template_rule.append
    for sid in ruleID:
        sql_rule = 'select sRule,sRuleBelongFile from m_tbcustom_ips_lib  where sRuleID = "%s"'%sid
        cur.execute(sql_rule)
        result = cur.fetchall()
        if len(result):
           template_rule_append(result[0])

    os.system('rm -f /etc/suricata/rules/custom_rules/*')
    template_rule.sort(key=itemgetter('sRuleBelongFile'))
    for sRuleBelongFile, items in groupby(template_rule, key=itemgetter('sRuleBelongFile')):
        if sRuleBelongFile:
           f_rule = open('/etc/suricata/rules/custom_rules/'+sRuleBelongFile.split('/')[-1],'w')
           for rule in items:
               print >>f_rule,rule['sRule']
           os.system('chmod 777 %s'%'/etc/suricata/rules/custom_rules/'+sRuleBelongFile.split('/')[-1])
           f_rule.close()
    cur.close()


def source_ip(sourceip):
    """
    源ip根据需要转换格式
    """
    ip_range = []
    ipinfo = ''
    if sourceip['sAddtype'] == '2':
        ip_range = [ str(tmp) for tmp in iter_iprange(sourceip['sAddress'],sourceip['sNetmask'])]
        ipinfo = ','.join(ip_range)
    else:
       ipinfo = str(IPNetwork(sourceip['sAddress']+'/'+sourceip['sNetmask']))
    return ipinfo


def config_file_sourceip(cur,iptype,value,ipsconf_info):
    """
    获取界面配置的源IP
    """

    if int(iptype) == 1:
        sql_sip='select sAddress,sNetmask,sAddtype from m_tbaddress_list where id=%s'%value
        cur.execute(sql_sip)
        sourceip=cur.fetchone()
        ipsconf_info['sourceip'] = source_ip(sourceip)

    if int(iptype) == 2:
        sql_sipgroup='select sIP from m_tbaddressgroup where id=%s'%value
        cur.execute(sql_sipgroup)
        sipgroup_num=cur.fetchone()
        if len(sipgroup_num):
            #sipgroup_num=sipgroup_num[0]
            sipgroup_num=sipgroup_num['sIP'].split(',')
            ip_range=[]
            for i in range(len(sipgroup_num)):
                sql_1='select sAddress,sNetmask,sAddtype from m_tbaddress_list where id=%s'%sipgroup_num[i]
                cur.execute(sql_1)
                sip=cur.fetchone()
                if not sip :
                    continue
                ip = source_ip(sip)
                ip_range.append(ip)
            ipsconf_info['sourceip']=','.join(ip_range)
    for tmp in ipsconf_info['sourceip'].split(','):
        try:
            tmp = tmp.split('/')
            ip = IP(tmp[0]).make_net(tmp[1])
            if ip == IP('0.0.0.0/0'):
                ipsconf_info['sourceip']='any'
            break
        except Exception as e:
            pass
    print ipsconf_info
    #print e
    #pattern = re.compile(r'0.0.0.0')
    #if pattern.findall(ipsconf_info['sourceip']):
    #    ipsconf_info['sourceip']='any'
    #else:
    #    ipsconf_info['sourceip'] = ipsconf_info['sourceip']
    #return ipsconf_info

def load_rules_file(cur,template,ipsconf_info):
    """
    获取模板规则路径及文件
    """
    rulefiles = []
    sql_template='select iQuoteTemp from m_tbips_template where id ="%s"'%template
    cur.execute(sql_template)
    QuoteTemp=cur.fetchall()
    if QuoteTemp:
       if QuoteTemp[0]['iQuoteTemp']==None:
          ipsconf_info['path']='/etc/suricata/rules/custom_rules'
          sql_ID='select sRuleIDS from m_tbips_template where id = %s'%template
          cur.execute(sql_ID)
          ruleID=cur.fetchone()
          ruleID=ruleID['sRuleIDS'].split(',')
          template_rule(ruleID)

          for i in os.listdir('/etc/suricata/rules/custom_rules'):
              if i.endswith('.rules'):
                 rulefiles.append(i)
          rulefiles.sort()
          ipsconf_info['rulefile']=rulefiles

       elif QuoteTemp[0]['iQuoteTemp']==1:
           ipsconf_info['path']='/etc/suricata/rules'
           #for i in os.listdir('/etc/suricata/rules'):
           #    if not i.endswith('.rules'):
           #        continue
           #    if i =='recommend.rules':
           #        continue
           rulefiles.append('recommend.rules')
           rulefiles.sort()
           ipsconf_info['rulefile']=rulefiles


def custom_ips_template():

    """
    无入侵策略生效，/etc/suricata/suricata.yaml配置文件默认
    需改动配置文件的 default-rule-path、rule-files、HOME_NET分别表示：规则文件路径，规则文件，源IP
    ipsconf_info['rulefile']存放规则文件
    ipsconf_info['path']规则文件路径
    ipsconf_info['sourceip']源IP
    """

    if not os.path.exists('/etc/suricata/rules/custom_rules/'):
        os.makedirs('/etc/suricata/rules/custom_rules/')

    tenv        = init_tenv()
    cur         = mysql_connect_dict()
    rulefiles   = []
    ipsconf_info = {}
    sql = 'select * from m_tbips where iStatus=1'
    cur.execute(sql)
    template = cur.fetchall()
    template = template and template[0] or ''

    #无策略生效时，默认配置
    if not template:
        ipsconf_info['path']='/etc/suricata/rules'
        with open('/etc/suricata/rules/none.rules','w') as f:
            rule_none = 'pass tcp [192.168.1.0/24] 1200 -> [192.168.1.0/24] 1200 (msg:"8miles POP3 XTND overflow attempt"; flow:to_server,established; content:"XTND"; nocase; isdataat:50,relative; pcre:"/^XTND\s[^\n]{50}/smi"; classtype:attempted-admin; sid:2101938; rev:5;)'.encode('string-escape')
            print >>f,rule_none
        rulefiles.append('none.rules')
        ipsconf_info['rulefile']=rulefiles
        ipsconf_info['sourceip']="172.16.0.0/16,10.0.0.0/16,192.168.0.0/16"
        return ipsconf_info

    #获取源IP
    config_file_sourceip(cur,template['iSourceType'],template['sSourceValue'],ipsconf_info)

    #获取需加载的规则文件
    load_rules_file(cur,template['sStrategyTemplate'],ipsconf_info)
    cur.close()

    return ipsconf_info


def generate_config_restart():
    os.system('python -m safetydefend.session_control')
    #IPS_on_off = select('select sValue from m_tbconfig where sName="TimeSet"')
    #IPS_on_off = IPS_on_off and json.loads(IPS_on_off[0]['sValue']).has_key('iIPS')\
    #                and json.loads(IPS_on_off[0]['sValue'])['iIPS'] or '0'
    #if IPS_on_off == '1':
    #    ips_switch('0')
    #    time.sleep(5)
    #    ips_switch('1')


def recover():
    custom_ips_rule()
    generate_config_restart()



if __name__=="__main__":
    recover()
    #generate_config_restart()

