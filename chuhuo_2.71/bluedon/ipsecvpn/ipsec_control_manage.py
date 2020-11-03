#!/usr/bin/env python
# coding=utf-8

"""
IPSEC VPN --> 监控管理
"""

import re
import commands
from collections import defaultdict
from db.config import get_mysql_db
import sys
import os
import json
import psutil
from logging import getLogger

reload(sys)
sys.setdefaultencoding('utf-8')



def running_statsus():
    """
    获取各个隧道接收发送流量
    """
    (conn,cur) = get_mysql_db()
    current_flow = {}

    (status, output) = commands.getstatusoutput('/usr/local/ipsec-vpn/sbin/setkey -D')
    output = output.split('refcnt=0\n')
    for line in output:
        comment = re.compile('^(?P<ip>\d+\.\d+\.\d+\.\d+\s*\d+\.\d+\.\d+\.\d+).*current:\s*(\d+.*?)\s*.*', re.DOTALL)
        info = comment.findall(line)
        for tmp in info:
            current_flow[tmp[0]] = float(tmp[1])
    if not len(current_flow):
        del_sql = 'truncate table m_tbipsecstatusmonitor'
        cur.execute(del_sql)
    conn.close()
    cur.close()
    return current_flow

    #time.sleep(3)
def select_tabledata(cur,sql):
    cur.execute(sql)
    data = cur.fetchall()
    return data

def net_gateway_of_tunnel(tunnel_info,net,cur):
    """
    获取隧道本地子网，对端子网，连接方式，网关
    """
    connect_dict = {1:'直连Internet',
                    2:'非直连Internet'
                }
    nic_rev = []
    nic_send = []
    ipsecstatus_info =defaultdict(list)
    for k,v in tunnel_info.items():
        status_info_2 = {}
        for tmp in v:
            try:

                info = select_tabledata(cur,tmp)
                info = info and info[0] or {}

                if 'sDuiduanChildIp' in ','.join(info.keys()):
                    status_info_2['terminal_net']=info['sDuiduanChildIp']+'/'+info['sDuiduanChildMask']
                if 'sLocalChildIp' in ','.join(info.keys()):
                    status_info_2['local_net'] = info['sLocalChildIp']+'/'+info['sLocalChildMask']
                if 'sIpaddresss'in ','.join(info.keys()):
                    status_info_2['local_ip'] = info['sIpaddresss']
                    status_info_2['connect_type'] = connect_dict[info['iConnettype']]
                    gateway_sql = 'select sNextJumpIP from m_tbstaticroute where sPort="%s" and sIPV="ipv4"'%info['sNetport']
                    gate_info = select_tabledata(cur,gateway_sql)
                    status_info_2['gateway']= gate_info and gate_info[0]['sNextJumpIP'] or ''

                    nic_rev.append(net[info['sNetport']].bytes_recv)
                    nic_send.append(net[info['sNetport']].bytes_sent)

            except Exception as e :

                if '.'in tmp:
                    status_info_2['terminal_ip'] = tmp
                else:
                    status_info_2['status'] = tmp
        status_info_2['rev_bytes']= status_info_2['terminal_ip']+' '+status_info_2['local_ip']
        status_info_2['send_bytes'] = status_info_2['local_ip']+' '+status_info_2['terminal_ip']
        del status_info_2['local_ip']
        del status_info_2['terminal_ip']
        ipsecstatus_info[k].append(status_info_2)
    return ipsecstatus_info,nic_rev,nic_send


def process_table(ipsecstatus_info,flow,cur):
    """
    更新ipsecvpn状态表的信息
    """
    tunnel_name_sql = 'select sTunnelName from m_tbipsecstatusmonitor'
    tunnel_name = select_tabledata(cur,tunnel_name_sql)
    tunnel_name = [str(tmp['sTunnelName']) for tmp in tunnel_name]
    same = set(ipsecstatus_info.keys())& set(tunnel_name)
    new_tunnel,rev_tunnel = set(ipsecstatus_info.keys())-set(tunnel_name),set(tunnel_name)-set(ipsecstatus_info.keys())

    rev_sql = ['delete from m_tbipsecstatusmonitor where sTunnelName="%s"'%tmp for tmp in rev_tunnel]
    update_sql = []
    insert_sql = []
    sum_send = []
    sum_rev  = []
    for k,v in ipsecstatus_info.items():
        send_flow = flow.has_key(v[0]['send_bytes']) and flow[v[0]['send_bytes']] or '0'
        rev_flow  = flow.has_key(v[0]['rev_bytes']) and flow[v[0]['rev_bytes']] or '0'
        ipsecvpn_status = flow.has_key(v[0]['send_bytes']) and '1' or '0'
        if v[0]['status'] =='0':
            send_flow = 0
            rev_flow  = 0
            ipsecvpn_status = '0'
        if set([k]) & same:
            sql = 'update m_tbipsecstatusmonitor set sDdProtectNet="%s",sConnetType="%s",sLocalProtectNet="%s",\
                iSendFlow="%s",iRecFlow="%s" ,iStatus = "%s",sLocalGateway="%s" where sTunnelName="%s"'\
                %(v[0]['terminal_net'],v[0]['connect_type'],v[0]['local_net'],send_flow,rev_flow,ipsecvpn_status,v[0]['gateway'],k)
            update_sql.append(sql)
        if set([k]) & new_tunnel:
            sql ='insert into m_tbipsecstatusmonitor (sTunnelName,sDdProtectNet,sConnetType,sLocalProtectNet,iSendFlow,iRecFlow,iStatus,sLocalGateway)\
                values("%s","%s","%s","%s","%s","%s","%s","%s")'%(k,v[0]['terminal_net'],v[0]['connect_type'],\
                v[0]['local_net'],send_flow,rev_flow,ipsecvpn_status,v[0]['gateway'])
            insert_sql.append(sql)
        sum_send.append(int(send_flow))
        sum_rev.append(int(rev_flow))
    [cur.execute(tmp) for tmp in update_sql]
    [cur.execute(tmp) for tmp in insert_sql]
    [cur.execute(tmp) for tmp in rev_sql]

    return sum_rev,sum_send


class SubnetMapTunnel():
    def __init__(self):
        self.conn,self.cur = get_mysql_db()
        self.terminal_local_net = {  'sDuiduanChildNet': 'select sDuiduanChildIp,sDuiduanChildMask from m_tbduiduanchildnet where id=%s',
                                      'iLocalChildNet': 'select sLocalChildIp,sLocalChildMask from m_tblocalchildnet where id=%s',
                                      'iIpsecOutNetport':'select sIpaddresss,iConnettype,sNetport from m_tbipsecoutnetport where id=%s',
                                      'sFixedIp':'%s',
                                      'iStartEqu':'%s'
                                  }
        self.first_step_data = {}

    def get_first_branch_data(self):
        first_info_sql = 'select sEquipmentName,sFixedIp,sDuiduanChildNet,iLocalChildNet,iIpsecOutNetport,iStartEqu from  m_tbfirsttage'
        first_step_table = select_tabledata(self.cur,first_info_sql)
        for tmp in first_step_table:
            tmp1 = tmp['sEquipmentName']
            del tmp['sEquipmentName']
            self.first_step_data[tmp1]= tmp

    def get_alldata_tunnel(self):
        net = psutil.net_io_counters(pernic=True)
        tunnel_info = defaultdict(list)
        [tunnel_info[k].append(self.terminal_local_net[k1]%v[k1]) for k,v in self.first_step_data.items() for k1 in v.keys()]
        self.ipsecstatus_info,self.nic_rev,self.nic_send = net_gateway_of_tunnel(tunnel_info,net,self.cur)

    def get_flow_of_tunnel(self):
        self.flow = running_statsus()
        if not len(self.flow):
            with open('/usr/local/bluedon/tmp/ipsecvpn_flow.txt','w') as f :
                print >>f,json.dumps({'vpn_rev':'0','vpn_send':'0','nic_rev':str(sum(self.nic_rev)),'nic_send':str(sum(self.nic_send))})
        #self.flow = {'172.16.3.99 172.16.5.138':'1111','172.16.5.138 172.16.3.99':'1111'}

    def main(self):

        try:
            self.get_first_branch_data()
            self.get_alldata_tunnel()
            self.get_flow_of_tunnel()
        except Exception as e:
            getLogger('main').info("%s"%e)
        if not len(self.flow):
            getLogger('main').info('there is not tunnel')
            return
        getLogger('main').info('Begin to get the info of tunnel........')
        sum_rev,sum_send = process_table(self.ipsecstatus_info,self.flow,self.cur)
        sum_rev_send = {'vpn_rev':str(sum(sum_rev)),'vpn_send':str(sum(sum_send)),'nic_rev':str(sum(self.nic_rev)),'nic_send':str(sum(self.nic_send))}
        with open('/usr/local/bluedon/tmp/ipsecvpn_flow.txt','w') as f:
            print >>f,json.dumps(sum_rev_send)
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        getLogger('main').info('End.........')



if __name__=='__main__':
    #cur = mysql_connect_dict()
    tunnel = SubnetMapTunnel()
    tunnel.main()
    #running_statsus()

