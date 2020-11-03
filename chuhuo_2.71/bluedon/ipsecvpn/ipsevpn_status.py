#!/usr/bin/env python
# coding=utf-8


from db.mysql_db import update,select,select_one,insert
import commands
import re
import sys
import psutil
import json
from collections import defaultdict
import time
import shelve
from branch_docking import get_duiduan_subnet, get_local_subnet
reload(sys)
sys.setdefaultencoding('utf-8')

def get_managenic_IP():
    pass

comment = re.compile('^(?P<ip>\d+\.\d+\.\d+\.\d+).*?\s*(\d+\.\d+\.\d+\.\d+).*current:\s*(\d+.*?)\s*.*', re.DOTALL)

class SubnetMapTunnel:
    def running_statsus(self,):
        """
        获取各个隧道接收/发送流量
        """
        current_flow_1 = defaultdict(set)
        current_flow_2 = defaultdict(set)
        current_flow = {}

        for current_flow in [current_flow_1,current_flow_2]:
            (status, output) = commands.getstatusoutput('/usr/local/ipsec-vpn/sbin/setkey -D')
            output = output.split('refcnt=0\n')
            for line in output:
                info = comment.findall(line)
                for tmp in info:
                    ip_str = ' '.join([tmp[0],tmp[1]])
                    current_flow[ip_str].add(float(tmp[2]))
            time.sleep(0.5)
        print 'current_flow_1',current_flow_1
        print 'current_flow_2',current_flow_2
        for key,value in current_flow_1.items():
            if len(value)>1:
                revtunnel = set(current_flow_1[key])&set(current_flow_2[key])
                #print 'revtunnel',revtunnel
                #print current_flow_2[key]
                current_flow[key] = current_flow_2[key]-revtunnel or set([0])
            else:
                current_flow[key]=current_flow_2[key]

        print '******',current_flow
        return current_flow

    def get_branceinfo(self,):
        """
        从分支对接获取隧道的会话模式，本地子网，对端子网，接收/发送流量
        """
        current_flow = self.running_statsus()
        allinfo = select('select sName,f_sAddress,s_iLocal,s_iTarget,sIpsecOutNetport,s_iSessionMode,iStatus from m_tbipsec_branch')
        self.tunelname_info = {}
        for info in allinfo:
            tmp = {}
            localnet_list = get_local_subnet(info['s_iLocal']) if info['s_iSessionMode'] == '1' else []
            tmp['localnet'] = ','.join(localnet_list)
            terminalnet_list = get_duiduan_subnet(info['s_iTarget']) if info['s_iSessionMode'] == '1' else []
            tmp['terminalnet'] = ','.join(terminalnet_list)
            outnet_info = select_one('select sIpaddresss,sNetport from m_tbipsecoutnetport where id=%s'%info['sIpsecOutNetport'])
            manage_IP = outnet_info['sIpaddresss']
            tmp['tunnel_rev']=list(current_flow.get('%s %s'%(info['f_sAddress'],str(manage_IP)),set([0])))[0]
            tmp['tunnel_send']=list(current_flow.get('%s %s'%(str(manage_IP),info['f_sAddress']),set([0])))[0]
            tmp['mode']=info['s_iSessionMode']
            tmp['outnic'] = outnet_info['sNetport']
            tmp['status'] = info['iStatus'] if (tmp['tunnel_rev'] != 0 and tmp['tunnel_send'] != 0) else 0
            self.tunelname_info[info['sName']]=tmp


    def proc_table(self,):
        """
        隧道信息入表
        """

        connect_mode = {'1':'隧道模式','2':'传输模式'}
        tunnel_info = select('select sTunnelName,iSendFlow,iRecFlow from m_tbipsecstatusmonitor')
        #tunnel_name_flow=defaultdict(list)
        tunnel_name=[]
        for tmp in tunnel_info:
            tunnel_name.append(str(tmp['sTunnelName']))
            #tunnel_name_flow[tmp['sTunnelName']].append(tmp['iSendFlow'])
            #tunnel_name_flow[tmp['sTunnelName']].append(tmp['iRecFlow'])


        #tune = set(self.tunelname_info.keys())& set(tunnel_name)
        insert_tunnel,rev_tunnel = set(self.tunelname_info.keys())-set(tunnel_name),set(tunnel_name)-set(self.tunelname_info.keys())
        update_tunnel = set(self.tunelname_info.keys()) & set(tunnel_name)
        #print 'insert_tunnel',insert_tunnel
        #print 'rev_tunnel',rev_tunnel
        #print 'update_tunnel',update_tunnel
        for tmp in insert_tunnel:
            insert_info= self.tunelname_info[tmp]
            args = {'sTunnelName':tmp,
                    'sLocalProtectNet':insert_info['localnet'],
                    'sDdProtectNet':insert_info['terminalnet'],
                    'iSendFlow':insert_info['tunnel_send'],#+tunnel_name_flow[tmp][0] if str(insert_info['status'])!='0' else 0,
                    'iRecFlow':insert_info['tunnel_rev'],#+tunnel_name_flow[tmp][1] if str(insert_info['status'])!='0' else 0,
                    'iStatus':str(insert_info['status']),
                    'sConnetType':connect_mode[str(insert_info['mode'])]}
            #print args
            insert('m_tbipsecstatusmonitor',**args)

        for tmp in rev_tunnel:
            update('delete  from m_tbipsecstatusmonitor where sTunnelName="%s"'%tmp)

        for tmp in update_tunnel:
            update_info = self.tunelname_info[tmp]
            update_sql = 'update m_tbipsecstatusmonitor set sLocalProtectNet="%s",sDdProtectNet="%s",sConnetType="%s",\
                         iSendFlow=%d,iRecFlow=%d,iStatus="%s" where sTunnelName="%s"'\
                         %(update_info['localnet'],update_info['terminalnet'],connect_mode[str(update_info['mode'])],
                          update_info['tunnel_send'],#+tunnel_name_flow[tmp][0] if str(update_info['status'])!='0' else 0,
                          update_info['tunnel_rev'],#+tunnel_name_flow[tmp][1] if str(update_info['status'])!='0' else 0,
                          update_info['status'],tmp)
            #print update_sql
            update(update_sql)

    def outnet_vpn_flow(self,):
        """
        隧道接收/发送总流量，外网接口流量
        """
        nic_flow = psutil.net_io_counters(pernic=True)
        vpn_rev =[]
        vpn_send=[]
        nic = set()
        for k,v in self.tunelname_info.items():
            vpn_rev.append(v['tunnel_rev'])
            vpn_send.append(v['tunnel_send'])
            nic.add(v['outnic'])
        nic_rev = []
        nic_send = []
        for tmp in nic:
            nic_rev.append(nic_flow[tmp].bytes_recv)
            nic_send.append(nic_flow[tmp].bytes_sent)
        with open('/usr/local/bluedon/tmp/ipsecvpn_flow.txt','w') as f:
            print >>f,json.dumps({'vpn_rev':str(sum(vpn_rev)),'vpn_send':str(sum(vpn_send)),
                                  'nic_rev':str(sum(nic_rev)),'nic_send':str(sum(nic_send))})

    def main(self):
        self.get_branceinfo()
        self.proc_table()
        self.outnet_vpn_flow()



if __name__ =="__main__":
    cls= SubnetMapTunnel()
    #cls.main()
    cls.running_statsus()
    #running_statsus()
