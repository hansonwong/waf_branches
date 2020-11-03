#!/usr/bin/env python
# coding=utf-8

from netaddr import iter_iprange
from db.mysql_db import select,update,select_one
import time
from ipsec_client.netport_in_out import IpsecClient
from netaddr import *
import os
import shelve
from collections import defaultdict
from logging import getLogger
import threading



def generate_ip(startIP,endIP,filterIP):
    for ip in iter_iprange(startIP,endIP):
        if set([str(ip)])&filterIP:
            continue
        yield ip


class UserManage():
    def __init__(self,user=None,action=None):
        self.user =user
        self.user_data = ''
        self.del_user_iptables(self.user)
        if action=='del':
            self.chap_secrets_conf()
            print '********del********'
            return
        self.get_user_data(self.user)
        self.user_usergroup_permission()
        self.allot_user_IP(self.user,action)
        self.chap_secrets_conf()
        self.iptables_polisy()

    def get_user_data(self,user=None):
        """
        user为NONE获取所有生效用户,反之则获取具体用户信息
        """
        nowtime = time.time()
        self.user_data = select('select id,sUserName,sPassword,virtual_ip,default_action,iGroupID,IP,Expirationtime\
                                from m_tbipsec_user where UNIX_TIMESTAMP(Expirationtime)>%d %s'\
                                %(nowtime,'and sUserName="%s"'%user if user is not None else ''))
        self.user_data.extend((select("select id,sUserName,sPassword,virtual_ip,perssiomData,default_action,iGroupID,IP,Expirationtime\
                                      from m_tbipsec_user where Expirationtime='' %s"\
                                      %('and sUserName="%s"'%user if user is not None else ''))))


    def user_usergroup_permission(self):
        """
        用户权限包含用户自身权限及用户组为其配置的权限
        """
        permission_args = lambda perssiom:'|'.join(['%s,%s,%s'%(tmp1['server_name'],tmp1['server_allow'],tmp1['server_time'])
                                                    for tmp1 in perssiom])
        for i,tmp in  enumerate(self.user_data):
            user_id = select_one('select id from m_tbipsec_usergroup where sGroupName="%s"'%tmp['iGroupID'])
            user_id = user_id and user_id.get('id') or 0
            permission_group = select('select server_name,server_allow,server_time from m_tbipsec_perssiom \
                              where user_group_id=%d and iType=2'%user_id)
            usergroup_polisy = permission_args(permission_group)

            permission_user = select('select server_name,server_allow,server_time from m_tbipsec_perssiom \
                              where user_group_id=%d and iType=1'%tmp['id'])
            user_polisy = permission_args(permission_user)
            if usergroup_polisy and user_polisy:
                tmp['perssiomData'] = '|'.join([usergroup_polisy,user_polisy])
            else :
                tmp['perssiomData'] = usergroup_polisy or user_polisy
            self.user_data[i]=tmp



    def allot_user_IP(self,user=None,action=None):
        """
        在IP池中为用户分配IP
        """
        cls_ipcli = IpsecClient()
        startIP,endIP = cls_ipcli.get_outnet_IPpool()
        vpn_ip = cls_ipcli.vpn_interface_set()

        #若只是修改用户则用原先已分配好的IP,或是用户编辑的IP
        if user is not None and action=='modify':
            if IPAddress(self.user_data[0]['IP']) in IPRange(startIP,endIP):
                self.user_data[0]['virtual_ip'] = self.user_data[0]['IP']
            return

        db = shelve.open('ipsec_user_iptables')

        #已给用户分配出去的IP不能再被分配，加入过滤集合中
        filterIP = set([ tmp['virtual_ip'] for tmp in self.user_data if tmp['virtual_ip']
                        if IPAddress(tmp['virtual_ip']) in IPRange(startIP,endIP)])
        filterIP.add(vpn_ip)
        user_count = select_one('select COUNT(*) from m_tbipsec_user')

        #若添加的不是首个用户，则startIP是db数据库记录的开始IP
        if user is not None and user_count['COUNT(*)']>1:
            if db.has_key('startIP')and db.has_key('endIP'):
                if IPAddress(db['startIP']['startIP']) in IPRange(startIP,endIP) and db['endIP']['endIP']==endIP:
                    virIP = generate_ip(db['startIP']['startIP'],endIP,filterIP)
        else:
            print 'startIP',startIP
            print 'endIP',endIP
            virIP = generate_ip(startIP,endIP,filterIP)

        #为用户分配IP
        for i,tmp in enumerate(self.user_data):
            if not tmp['virtual_ip'] or IPAddress(tmp['virtual_ip']) not in IPRange(startIP,endIP):
                virtual_ip = next(virIP)
                update('update m_tbipsec_user set IP="%s" where sUserName="%s"'%(virtual_ip,tmp['sUserName']))
                tmp['virtual_ip']=virtual_ip
                self.user_data[i] = tmp

        #db记录下次的开始IP,结束IP
        try:
            db['startIP']={'startIP':next(virIP)}
            db['endIP']={'endIP':endIP}
        except Exception as e:
            print e
        finally:
            db.close()

        #self.chap_secrets_conf()


    def chap_secrets_conf(self):
        """
        用户虚拟IP,用户名,密码格式化写入文件
        """
        nowtime = time.time()
        user_name_pwd = select('select sUserName,sPassword,IP from m_tbipsec_user where UNIX_TIMESTAMP(Expirationtime)>%d'%(nowtime))
        user_name_pwd.extend(select("select sUserName,sPassword,IP from m_tbipsec_user where Expirationtime=''"))
        fw =open('/etc/ppp/chap-secrets','w')
        for i,tmp in enumerate(user_name_pwd):
            if i==0:
                print >>fw,'# Secrets for authentication using CHAP'
                print >>fw,'# client'.ljust(15),'server'.ljust(10),'secret'.ljust(22),'IP addresses'
            #print>>fw, tmp['sUserName'].ljust(15),'12tpd'.ljust(10),tmp['sPassword'].ljust(22),tmp['IP']
            print >>fw,' '.join([tmp['sUserName'],'l2tpd',tmp['sPassword'],tmp['IP']])
        fw.close()
#os.chmod('/etc/ppp/chap-secrets',333)


    def del_user_iptables(self,user=None):
        """
        删除上一次配置的iptables规则
        """
        db = shelve.open('ipsec_user_iptables')
        if user is not None:
            if db.has_key(user):
                [os.system(iptables) for iptables in db[user][user]]
                del db[user]
        else:
            for key in db:
                if key != 'startIP' and key != 'endIP':
                    [os.system(iptables) for iptables in db[key][key]]
                    del db[key]
        db.close()

    def  nic_iptables(self,user_iptables,**kwargv):
        """
        使用内网口,用户IP,用户有效时间配置规则
        """
        iptables_nic = lambda ppp_nic,user_ip,starttime,endtime,pro:'iptables -A IPSECCLIENTS \
                            {ppp_nic} {user_ip} {starttime} {endtime} {pro} -j ACCEPT'.format(
                                                                                ppp_nic = ppp_nic,
                                                                                user_ip = user_ip,
                                                                                starttime = starttime,
                                                                                endtime = endtime,
                                                                                pro = '-p %s'%pro if pro!='ALL' else ''
                                                                                )
        nic_info = select('select sNetport from m_tbipsecinternetport')
        for tmp in nic_info:
             iptables1 = iptables_nic(' -i ppp+ -o %s '%tmp['sNetport'],'-s %s'%kwargv['user_ip'],
                                      kwargv['starttime'],kwargv['endtime'],kwargv['pro'])

             iptables2 = iptables_nic(' -o ppp+ -i %s '%tmp['sNetport'],'-d %s'%kwargv['user_ip'],
                                      kwargv['starttime'],kwargv['endtime'],kwargv['pro'])
             os.system(iptables1)
             os.system(iptables2)
             user_iptables.append(iptables1.replace('-A','-D'))
             user_iptables.append(iptables2.replace('-A','-D'))
             pass

    def iptables_polisy(self,):
        """
        为用户的每个权限配置规则,若权限的协议为'ALL'需多配置条来回规则;
        为每个用户配置'缺省动作'规则
        使用shelve记录每个用户已配置的规则
        """
        iptables_str = "/usr/sbin/iptables -A IPSECCLIENTS -i ppp+ {addr} {starttime}  {endtime}  {pro} -j {action}"
        db = shelve.open('ipsec_user_iptables')
        for tmp in self.user_data:
            user_iptables = defaultdict(list)
            print tmp['virtual_ip'],tmp['perssiomData']

            #配置用户的每个权限规则
            for static in tmp['perssiomData'].split('|'):
                try:
                    pro,action,timeid = static.split(',')
                except Exception as e:
                    pro,action,timeid='','',''
                    print e
                if timeid:
                    time_set = select_one('select sStartTime,sEndTime from m_tbipsectimeset where id="%s"'%timeid)
                    starttime,endtime = (['-m time --datestart  ','T'.join(time_set['sStartTime'].split(' '))],
                                         ['--datestop  ','T'.join(time_set['sEndTime'].split(' ')),'  --kerneltz'])\
                                        if time_set is not None else ('','')

                    nic_iptables_args={'user_ip':tmp['virtual_ip'],
                                       'starttime':''.join(starttime),
                                       'endtime':''.join(endtime),
                                       'pro':pro
                                       }
                    self.nic_iptables(user_iptables[tmp['sUserName']],**nic_iptables_args)

            #配置用户的缺省动作规则
            if tmp['default_action']==0:
                iptables = 'iptables -A IPSECCLIENTS -i ppp+ {addr} -j DROP'.format(addr='-s %s'%tmp['virtual_ip'])
                os.system(iptables)
                user_iptables[tmp['sUserName']].append(iptables.replace('-A','-D'))
            else:
                iptables_i='iptables -A IPSECCLIENTS -i ppp+ {addr} -j ACCEPT'.format(addr='-s %s'%tmp['virtual_ip'])
                iptables_o='iptables -A IPSECCLIENTS -o ppp+ {addr} -j ACCEPT'.format(addr='-d %s'%tmp['virtual_ip'])
                os.system(iptables_i)
                os.system(iptables_o)
                user_iptables[tmp['sUserName']].append(iptables_i.replace('-A','-D'))
                user_iptables[tmp['sUserName']].append(iptables_o.replace('-A','-D'))
            db[str(tmp['sUserName'])] = user_iptables
        db.close()

class OutDateUser(threading.Thread):
    def __init__(self,):
        pass
    def run(self):
        while 1:
            nowtime = time.time()
            user_count = select_one("select COUNT(*) from m_tbipsec_user where UNIX_TIMESTAMP(Expirationtime)>%d\
                                    and Expirationtime!=''"%nowtime)
            print user_count['COUNT(*)']

            ineffective_user = select("select sUserName from m_tbipsec_user where UNIX_TIMESTAMP(Expirationtime)<%d\
                                      and Expirationtime!=''"%nowtime)
            for tmp in ineffective_user:
                UserManage(str(tmp['sUserName']),'del')
            print ineffective_user
            if not user_count['COUNT(*)']:
                print 'break'
                break
            time.sleep(5)




if __name__=='__main__':
    cls = UserManage()
    #OutDateUser().run()
   # cls.get_user_data('user5')
   # cls.user_usergroup_permission()
   # cls.allot_user_IP('user5')
   # cls.chap_secrets_conf()
   # cls.del_user_iptables('user5')
   # cls.iptables_polisy()
