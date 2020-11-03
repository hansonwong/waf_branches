#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import commands
import time
import json
import shelve
import thread
import copy
from logging import getLogger
from netaddr import IPNetwork
from db.mysql_db import update, select, select_one
from utils.mask_transition import exchange_mask
from utils.common import init_tenv, change_path_and_add_it

change_path_and_add_it('/usr/local/bluedon')
BRIDGE_CONFIG_PATH = '/etc/keepalived/bridge_ha.sh'
KEEPALIVED_PATH = '/etc/keepalived/keepalived.conf'
LINK_STATUS_PATH = '/usr/local/bluedon/tmp/ha_link_check.txt'
CONNTRACK_PATH = '/etc/conntrackd/conntrackd.conf'
RSYNC_CONF_PATH = '/usr/local/rsync/rsync.conf'
RSYNC_SH_PATH = '/etc/conntrackd/rsync.sh'
check_link_result = []
ha_start_flag = '0'
thread_status = []


def del_allnic_iptables():
    db = shelve.open('ha-shelve')
    for key in db:
        os.system(db[key][key])
        del db[key]
    db.close()


def check_link(ip, nic, thread_num):
    """
    作用：
        封装ping检查链路是否通
    """

    ret, _ = commands.getstatusoutput('ping -c 1 %s -I %s' % (ip, nic))
    if ret == 0:
        link_status = '1'
        check_link_result.append('1')
    else:
        link_status = '0'
        check_link_result.append('0')
    sql = 'update m_tbdoublehot set check_state=? where sNetCardName=?'
    update(sql, link_status, nic)
    thread_status[thread_num] = 'True'


def check_link_thread(ha_data):

    for i, tmp in enumerate(ha_data):
        thread.start_new_thread(check_link, (tmp['sDuiduanIp'], tmp['sNetCardName'], i))
    while 1:
        if thread_status == ['True'] * len(ha_data):
            break


def virtual_ipset(data):
    """
    db存储的数据格式：
        ｛'ip': {'ip': 'ipset'}}
        如： ['1.1.1.1': {'1.1.1.1': '/usr/local/sbin/ipset -A auth_local_mode 2.1.1.1'}}
    outip:
        ip/mask
    """

    db = shelve.open('outip-shelve')
    for key in db:
        commands.getstatusoutput(db[key][key])
        del db[key]

    for tmp in data:
        outip = str(tmp['sOutIP']).split(',')
        if outip != ['/']:
            for ip in outip:
                cmd = '/usr/local/sbin/ipset -A auth_local_mode %s' % ip.split('/')[0]
                commands.getstatusoutput(cmd)
                db[ip.split('/')[0]] = {ip.split('/')[0]: cmd.replace('-A', '-D')}
    db.close()


def all_link_on_or_off(results, action=None):
    """
    检测所有链路是否都ping通，若不通则关闭HA,回写HA状态表
    args:
        results:
            从数据表m_tbdoublehot读取到iStatus=1的所有数据，并且保存为一个tuple的格式
        action:
            refresh等
    """
    global thread_status, ha_start_flag, check_link_result

    if action is not None:
        thread_status = ['False'] * len(results)
        check_link_thread(results)
    else:
        link = []
        for tmp in results:
            if tmp['check_state'] == 2:
                link.append(tmp)
            if tmp['check_state'] == 1:
                check_link_result.append('1')
            if tmp['check_state'] == 0:
                check_link_result.append('0')
        thread_status = ['False'] * len(link)
        check_link_thread(link)

    # print check_link_result, ['1'] * len(results)
    if check_link_result == ['1'] * len(results):
        ha_start_flag = '1'
    else:
        ha_start_flag = '0'
    check_link_result = []
    with open(LINK_STATUS_PATH, 'w') as f:
        f.write(json.dumps({'state': ha_start_flag}))

    # 链路不通关闭HA
    if ha_start_flag == '0':
        config_syn('0')
        conntrackd_config('0')
        (status, output) = commands.getstatusoutput('killall keepalived')
        commands.getstatusoutput('/etc/keepalived/route-config.sh del')
        sql = 'select sValue from m_tbconfig where sName = "HaSetting"'
        ha_status = select_one(sql)
        del_allnic_iptables()
        if not ha_status:
            return
        ha_status = json.loads(ha_status['sValue'])
        ha_status['iTurn'] = 'stop'
        sql = 'update m_tbconfig set sValue=? where sName=?'
        update(sql, json.dumps(ha_status), "HaSetting")


def double_hot_bridge(tenv, nics, ha_data):
    bridge_name = ''
    if ha_data['sHaModel'] == 'sDoubleHostBridge':
        bridge_name = ha_data.get('bridge', '')
        sql = 'select sBridgeName,sBindDevices from m_tbbridgedevice where iStatus =1'
        bridge_info = select(sql)
        brg_nic = {}
        for brg in bridge_info:
            brg_nic[brg['sBridgeName']] = brg['sBindDevices']
        # print brg_nic
        if bridge_name:
            for tmp in bridge_name:
                if set([tmp]) & set(nics):
                    nics.remove(tmp)
                for i in brg_nic[tmp].split(','):
                    nics.append(i)
    tenv.get_template('bridge_ha').stream(brg=bridge_name).dump(BRIDGE_CONFIG_PATH)
    # if ha_data['sHaModel']=='sDoubleGroupBridge':
    #     for brg in bridge_name:
    #         os.system('brctl stp {brgname} on'.format(brgname=brg))


class HotStandbyConfig():
    """
    双机热备配置入口
    """
    def __init__(self, action=None):
        global ha_start_flag
        self.hotStandby_data = tuple(select('select * from m_tbdoublehot where iStatus=1'))
        self.tenv = init_tenv()
        self.nics = []
        self.get_priority_onoff()
        self.get_model()
        if self.model == 'sDoubleDetectionBridge':
            ret = 1
            if self.ha_data['sClientIP']:
                ret, _ = commands.getstatusoutput('ping -c 1 %s' % (self.ha_data['sClientIP']))
                getLogger('main').info('ha ping %s ret %s' % (self.ha_data['sClientIP'], ret))
            ha_start_flag = '1' if ret == 0 else '0'
            with open(LINK_STATUS_PATH, 'w') as f:
                f.write(json.dumps({'state': ha_start_flag}))
        else:
            all_link_on_or_off(self.hotStandby_data, action)
        if action == 'refresh':
            return
        virtual_ipset(self.hotStandby_data)
        self.process_keepalive_data()
        double_hot_bridge(self.tenv, self.nics, self.ha_data)
        self.filter_static_route()
        self.keepalived_conf()
        self.restart_keepalive()

    def get_model(self):
        if self.hotStandby_data:
            self.model = self.hotStandby_data[0]['sHaModel']
        else:
            self.model = self.ha_data['sHaModel']
        getLogger('main').info('HotStandbyConfig Model: %s' % self.model)

    def get_priority_onoff(self,):
        self.ha_data = select_one('select sValue from m_tbconfig where sName="HaSetting"')
        self.ha_data = json.loads(self.ha_data['sValue']) or {}
        self.ha_data['priority'] = self.ha_data.get('sHaLever', '')
        self.ha_data['turn_on_off'] = self.ha_data.get('iTurn', 'stop')
        self.ha_data['heart_addr'] = self.ha_data.get('sHeartAddress', '')
        self.ha_data['vrid'] = self.ha_data.get('sVRID', '')

    def process_keepalive_data(self,):
        self.hot = []
        for i, result in enumerate(self.hotStandby_data):
            hotStandby = {}
            hotStandby['NUM'] = i + 1
            hotStandby['VRID'] = result['sVRID']
            hotStandby['NIC'] = result['sNetCardName']
            hotStandby['nicIP'] = result['sNetCardIP']
            hotStandby['terminalIP'] = result['sDuiduanIp']
            outip = result['sOutIP'].split(',')
            virip = []
            if outip != ['/']:
                for j in range(len(outip)):
                    bits = exchange_mask(outip[j].split('/')[-1])
                    virip.append(outip[j].split('/')[0] + "/" + str(bits))
            hotStandby['OUTIP'] = virip
            hotStandby['LEVEL'] = self.ha_data['priority']
            self.nics.append(result['sNetCardName'])
            hotStandby['targetip'] = result['sTargetIP'].split('/')[0]
            if hotStandby['targetip'].split('.')[-1] == '0':
                hotStandby['mask'] = result['sTargetIP'].split('/')[1]
            else:
                hotStandby['mask'] = '255.255.255.255'
            hotStandby['gateway'] = result['sGateWay']
            self.hot.append(hotStandby)
        self.iptables_nic = copy.copy(self.nics)
        if self.ha_data['heart_addr'] not in self.iptables_nic:
            self.iptables_nic.append(self.ha_data['heart_addr'])
        try:
            self.nics.remove(self.ha_data['heart_addr'])
        except Exception as e:
            print e

    def filter_static_route(self):
        sql = 'select sTargetAddress,sMask,sNextJumpIP from m_tbstaticroute'
        static_route_info = select(sql)
        self.route_del_info = copy.deepcopy(self.hot)
        self.route_add_info = []
        # print 'before', self.route_del_info
        for tmp in self.route_del_info:
            tmp['OUTIP'] = [ip.split('/')[0] for ip in tmp['OUTIP']]
            self.route_add_info.append(tmp)
            for tmp1 in static_route_info:
                try:
                    if IPNetwork(tmp['targetip'] + '/' + tmp['mask']) == IPNetwork(tmp1['sTargetAddress'] + '/' + tmp1['sMask']):
                        if tmp['gateway'] == tmp1['sNextJumpIP']:
                            self.route_del_info.remove(tmp)
                except Exception as e:
                    print e
        # print 'affter', self.route_del_info
        # print 'route_add_info', self.route_add_info

    def keepalived_conf(self):
        for i in range(len(self.hot)):
            self.hot[i]['nics'] = self.nics
        commands.getstatusoutput('/etc/keepalived/route-config.sh del')
        if self.model == 'sDoubleDetectionBridge':
            self.tenv.get_template('keepalived_detect') \
                .stream(ha_data=self.ha_data, hot=self.hot) \
                .dump(KEEPALIVED_PATH)
        else:
            self.tenv.get_template('keepalived') \
                .stream(hot=self.hot).dump(KEEPALIVED_PATH)
        self.tenv.get_template('ha_route') \
            .stream(add_hot=self.route_add_info, del_hot=self.route_del_info) \
            .dump('/etc/keepalived/route-config.sh')
        pass

    def restart_keepalive(self,):
        del_allnic_iptables()
        db = shelve.open('ha-shelve')
        global ha_start_flag
        if self.ha_data['turn_on_off'] == "start" and ha_start_flag == '1':
            nic_cmd_set = {}
            for nic in self.iptables_nic:
                cmd = '/usr/sbin/iptables -I FWINPUT -i %s -d 224.0.0.18 -p vrrp -j ACCEPT'%nic
                os.system(cmd)
                nic_cmd_set[nic] = cmd.replace('-I', '-D')
                db[str(nic)] = nic_cmd_set
            commands.getstatusoutput('killall keepalived')
            commands.getstatusoutput('/etc/init.d/keepalived restart')
        db.close()


def conntrackd_config(conntrackd_status):
    os.system('/usr/sbin/iptables -D FWINPUT -d 225.0.0.50 -j ACCEPT')
    os.system('/usr/sbin/iptables -D FWOUTPUT -d 225.0.0.50 -j ACCEPT')
    if conntrackd_status == "1":
        os.system('/usr/sbin/iptables -I FWINPUT -d 225.0.0.50 -j ACCEPT')
        os.system('/usr/sbin/iptables -I FWOUTPUT -d 225.0.0.50 -j ACCEPT')
        (status, output) = commands.getstatusoutput('killall conntrackd')
        (status, output) = commands.getstatusoutput('conntrackd -d')
        getLogger('main').info('conntrackd %s' % output)
    else:
        (status, output) = commands.getstatusoutput('killall conntrackd')
        getLogger('main').info('killall conntrackd %s' % output)


def config_syn(status):

    os.system('/usr/sbin/iptables -D FWINPUT -p tcp --sport 873 -j ACCEPT')
    os.system('/usr/sbin/iptables -D FWINPUT -p tcp --dport 873 -j ACCEPT')
    if status == '1':
        # print 'config_syn start'
        os.system('/usr/sbin/iptables -I FWINPUT -p tcp --sport 873 -j ACCEPT')
        os.system('/usr/sbin/iptables -I FWINPUT -p tcp --dport 873 -j ACCEPT')
        try:
            os.system('killall rsync')
            # os.system('killall rsync.sh')
            # os.system('killall inotifywait')
            while os.path.exists('/var/run/rsyncd.pid'):
                time.sleep(1)
            os.system('/usr/local/rsync/bin/rsync --daemon --config=/usr/local/rsync/rsync.conf')
            #os.system('/etc/conntrackd/rsync.sh &')
        except Exception as e:
            getLogger('main').info(e)
    else:
        # os.system('killall rsync.sh')
        os.system('killall rsync')
        # os.system('killall inotifywait')


def config_syn_file(tenv, ha_info):
    tenv.get_template('conntrackd').stream(HAdata=ha_info).dump(CONNTRACK_PATH)
    tenv.get_template('rsync.conf').stream(terminalIP=ha_info['sClientIP']) \
        .dump(RSYNC_CONF_PATH)
    tenv.get_template('rsync.sh').stream(terminalIP=ha_info['sClientIP']) \
        .dump(RSYNC_SH_PATH)


class HAStartStop():
    """
    HA启用关闭入口
    """
    def __init__(self, action, ha_info):
        self.status = action
        self.tenv = init_tenv()
        self.ha_info = ha_info

    def start_or_stop(self):
        HotStandbyConfig()
        global ha_start_flag
        # print 'ha_start_flag', ha_start_flag
        if ha_start_flag == '0' and self.status != 'stop':
            return
        if self.status == 'start':
            # print "start start"
            self.ha_start()
        if self.status == 'stop':
            self.ha_stop()

    def ha_start(self):
        conntrackd_status = self.ha_info.get('iSynchronizeFlow', '0')
        config_status = self.ha_info.get('iSynchronizeSet', '0')
        with open('/etc/keepalived/sync.conf', 'w') as fw:
            print >>fw, self.ha_info['sLocalIP']
            print >>fw, self.ha_info['sClientIP']

        config_syn_file(self.tenv, self.ha_info)
        conntrackd_config(conntrackd_status)
        config_syn(config_status)
        (status, output) = commands.getstatusoutput('killall keepalived')
        (status, output) = commands.getstatusoutput('/etc/init.d/keepalived restart')
        getLogger('main').info('keepalived %s' % output)

    def ha_stop(self):
        config_syn('0')
        conntrackd_config('0')
        (status, output) = commands.getstatusoutput('killall keepalived')
        commands.getstatusoutput('/etc/keepalived/route-config.sh del')
        getLogger('main').info('killall keepalived %s' % output)


def recover():
    sql = 'select sValue from m_tbconfig where sName="HaSetting"'
    ha_info = select_one(sql)
    # print ha_info
    if len(ha_info):
        ha_info = json.loads(ha_info['sValue'])
        ha_on = ha_info.get('iTurn', 'stop')
        if ha_on == 'start':
            cls = HAStartStop('start', ha_info)
        if ha_on == 'stop':
            cls = HAStartStop('stop', ha_info)
        cls.start_or_stop()

if __name__ == '__main__':
    recover()
