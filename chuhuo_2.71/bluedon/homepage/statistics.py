#!/usr/bin/env python
# -*-coding:utf-8-*-
from __future__ import division
import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
import commands
import time
import json
import socket
import threading
from IPy import IP
from logging import getLogger
from reportlog.log_config import beep_alert
from reportlog.log_config import read_config_ini
from reportlog.traffic_statistic import TrafficStatistic
from reportlog.log_clear import log_clear_release_disk
from db.config1 import execute_sql, executemany_sql, search_data, get_mysql_db, fetchone_sql, fetchall_sql
from homepage.system_usage import cpu_usage_mpstat, mem_usage, disk_usage
from homepage.if_watch import interface_current_time, interface_get_traffic,interface_traffic
from homepage.iftop import get_net_io, get_net_speed
from db.mysql_observer import MysqlObserver
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR
from utils.file_monitor import add_file_monitor

SYS_ALERT_SUBJECT = 'SYSTEM USAGE ALERT'
CPU_ALERT = 99
MEM_ALERT = 99
DISK_ALERT = 80
DISK_THRES_PATH = '/Data/apps/wwwroot/firewall/data/configdata/iLogpercent.conf'
# CPU_ALERT = 2
# MEM_ALERT = 9
# DISK_ALERT = 0

# Interface bandwidth thresold
BW_1000M_MAX = 800
BW_10000M_MAX = 8000
#BW_1000M_MAX = 0
#BW_10000M_MAX = 0

SYS_STAT = '/usr/local/bluedon/log/sys_statistic.json'
NET_STAT = '/usr/local/bluedon/log/net_statistic.json'

TB_NAME = 'm_tbstatistics'
# cmd to get interface type
INTERFACE_TYPE = r'/home/ng_platform/bd_dpdk_warper/clients/get_interface_type'
IMPORT_ON_OFF = r'/tmp/db_firewall_import_onoff'
IMPORT_IS_OFF = r'/tmp/db_firewall_import_isoff'


def read_traffic_info():
    # time.sleep(5)
    getLogger('log_daemon').debug('run read')
    status, output = commands.getstatusoutput("systemctl list-units |grep get_statistics_data.service")
    if 'get_statistics_data.service' not in output:
        os.system('/usr/bin/taskset -c 1 /home/ng_platform/bd_dpdk_warper/clients/get_statistics_data')
        FWLOG_DEBUG('start get_statistics_data.service by os.system')
    else:
        FWLOG_DEBUG('start get_statistics_data.service by systemctl')
    return True

def stop_traffic_info():
    #kill read_traffic_info thread
    # s = commands.getoutput("ps -aux | grep /home/ng_platform/bd_dpdk_warper/clients/get_statistics_data| grep -v grep | awk '{print $2}'")
    os.system('killall get_statistics_data')

def import_switch(on_off):
    """
        Description:
            Send cmd to second_firewall fifo with [import] = on_off,
            then wait for a while and check if the change takes effect
    """
    try:
        if on_off == 'on':
            if os.path.exists(IMPORT_ON_OFF):
                os.system('rm -f %s' % IMPORT_ON_OFF)
        elif on_off == 'off':
            if not os.path.exists(IMPORT_ON_OFF):
                os.system('touch %s' % IMPORT_ON_OFF)
    except:
        pass

    return os.path.exists(IMPORT_IS_OFF)

    # _log_ini = read_config_ini('LOG Config')
    # _log_ini['import'] = on_off
    # ind = 'CMD_LOG_CONFIG|' + str(_log_ini)
    # os.system('echo "%s" > /Data/apps/wwwroot/firewall/fifo/second_firewall.fifo &' % ind)
    # # wait for a while in case the fifo is busy
    # time.sleep(3)
    # _log_ini = read_config_ini('LOG Config')
    # return _log_ini

class HomePageUpdate(threading.Thread):


    event = threading.Event()
    def __init__(self):
        super(HomePageUpdate,self).__init__()
        self.interface={}
        self.user=[]
        self.application=[]
        self.iIN,self.iOUT = 0,0
        self.mail_msg=[]
        self.if_count = 0
        self.init_record = {"interface":{},"user":[],"application":[]}
        self.if_mail = False
        self.if_res = {}
        self.section = {'user':self.proc_user,'application':self.proc_application}
        self.m_tb = TB_NAME
        self.queried_ip = set()
        self.queried_ip_timer = 0
        self.address_list = []
        self.address_group = []
        self.address_snat = []
        self.address_id = -1
        self.netport = []
        self.natport = []
        self.bridgeport = []
        self.netportinfo = []
        if not os.path.exists(SYS_STAT):
            os.system('touch %s' % SYS_STAT)
        if not os.path.exists(NET_STAT):
            os.system('touch %s' % NET_STAT)

        self.disk_max = 80
        self.update_disk_threshold()

        self.update_info()
        MysqlObserver.add_observer('m_tbSnat', self.update_info)
        MysqlObserver.add_observer('m_tbaddress_list', self.update_info)
        MysqlObserver.add_observer('m_tbaddressgroup', self.update_info)
        MysqlObserver.add_observer('m_tbnetport', self.update_info)
        MysqlObserver.add_observer('m_tbbridgedevice', self.update_info)


    def record_statistics(self):
        #init_record = {"interface":{},"user":[],"application":[]}

        #get new data
        self.init_record['interface'] = self.interface
        self.init_record['user'] = self.user
        self.init_record['application'] = self.app_bw_add_unit(self.application)

        js = json.dumps(self.init_record)
        _s = str((js))
        with open(NET_STAT,'w+') as fp:
            fp.write(_s)

    def record_resource_alert(self,sub,cont):
        sql = 'insert into m_tblog_sys_resource (iTime,sSubject,sContent)' + ' values(%s,"%s","%s")'

        execute_sql(sql % (int(time.time()),sub,cont))
        pass

    def update_disk_threshold(self, *args, **kwargs):
        _disk_max = 80
        try:
            with open(DISK_THRES_PATH) as fp:
                log_content = fp.read()

            _disk_max = int(log_content.strip())
        except:
            FWLOG_DEBUG('ERROR:iLog_file write error')

        # print '[hp]_disk_max=%s' % _disk_max
        FWLOG_DEBUG('[hp]_disk_max=%s' % _disk_max)
        self.disk_max = _disk_max

    def sys_info_update(self):
        usage_alert_tb = "m_tblog_sys_resource"
        usage = {"cpu":{},"mem":0,"disk":0}
        count = 0
        send = False
        msg = ''
        stop_by_diskalert = False

        # add disk thresold monitor
        add_file_monitor(DISK_THRES_PATH, self.update_disk_threshold)

        while 1:
            if self.event.isSet():
                FWLOG_DEBUG('EVENT SET:[STATISTICS:sys_info_update]')
                getLogger('log_daemon').debug('EVENT SET:[STATISTICS:sys_info_update]')
                break

            usage["cpu"] = cpu_usage_mpstat()
            usage["mem"] = mem_usage()
            usage["disk"] = disk_usage()

            js = json.dumps(usage)
            s = str((js))
            with open(SYS_STAT,'wb') as fp:
                fp.write(s)

            if usage["cpu"]["all"] > CPU_ALERT or usage["mem"] > MEM_ALERT or usage["disk"] > self.disk_max:
                #record in database
                sql = 'insert into ' + usage_alert_tb + ' (iTime,sSubject,sContent)' + ' values("%s","%s","%s")'
                if usage["cpu"]["all"] > CPU_ALERT:
                    execute_sql(sql % (int(time.time()),'CPU','CPU使用率 %s%%' % usage["cpu"]["all"]))
                if usage["mem"] > MEM_ALERT:
                    execute_sql(sql % (int(time.time()),'内存','内存使用率 %s%%' % usage["mem"]))
                if usage["disk"] > self.disk_max:
                    execute_sql(sql % (int(time.time()),'磁盘','磁盘使用率 %s%%' % usage["disk"]))

                msg = "cpu:%s%%,mem:%s%%,disk:%s%% at %s" % (usage["cpu"]["all"],usage["mem"],usage["disk"],time.ctime())

                # send mail if system is overload
                from reportlog.log_mail_config import send_email_msg
                beep_alert()
                send_email_msg('usage', '系统资源警报', msg)

            time.sleep(2)

        FWLOG_DEBUG('QUIT:[STATISTICS:sys_info_update]')
        getLogger('log_daemon').debug('QUIT:[STATISTICS:sys_info_update]')

    def get_interface_type(self,args):
        """
            Description:
                Get Interface type of interface name specified by args
            Return:
                interface_name:interface_type
                1000   --> '1000M'
                10000  --> '10000M'
                error  --> -1
        """
        if not args:
            return {}
        _TYPE = ['ERROR_TYPE','1000M','10000M']
        arg = ' '.join(args)
        res = commands.getoutput(INTERFACE_TYPE + ' ' + arg).split('\n')
        res = res[-len(args):]
        if_name = lambda x:x.split(',')[0]
        if_type = lambda x:(int(x.split(',')[1]) + 1)
        return {if_name(i):_TYPE[if_type(i)] for i in res}

    def if_traffic_check(self,traffic,types):
        """
            Description:
                check if the interface is overload
        """
        # get interface type for interfaces that haven't record in self.if_type
        no_type_vEth = [ vEth for vEth in traffic if not vEth in types ]
        if no_type_vEth:
            new_type_vEth = self.get_interface_type(no_type_vEth)
            for key in new_type_vEth:
                types[key] = new_type_vEth[key]

        from reportlog.log_mail_config import send_email_msg

        _MAX_TRAFFIC = {'ERROR_TYPE':99999,'1000M':BW_1000M_MAX, '10000M': BW_10000M_MAX }
        msgs = []
        for vEth in traffic:
            if vEth == 'GLOBAL':
                continue

            if traffic[vEth]['IN'] > _MAX_TRAFFIC[types[vEth]]:
                # traffic alert
                msgs.append('%s接口 [%s] INPUT %sMbps'
                            % (types[vEth], vEth, traffic[vEth]['IN']))

            if traffic[vEth]['OUT'] > _MAX_TRAFFIC[types[vEth]]:
                # traffic alert
                msgs.append('%s接口 [%s] OUTPUT %sMbps'
                            % (types[vEth], vEth, traffic[vEth]['OUT']))

        # alert by sound and mail
        if msgs:
            beep_alert()
            date = time.ctime()
            send_email_msg('interface', '带宽警报', '\n'.join(msgs) + '\n' + date)
            # record in database
            args = []
            t = int(time.time())
            sql = ('insert into m_tblog_sys_resource (iTime,sSubject,sContent)'
                   ' values(%s,%s,%s)')
            for msg in msgs:
                args.append((t, '带宽警报', msg))
            executemany_sql(sql, args)
        pass

    def if_watch_thread(self):
        """
            Description:
                Get interface traffic
        """

        self.if_type = {}
        # t_pre =  interface_current_time()
        # res_pre = interface_get_traffic()

        pre_t = time.time()
        pre_io = get_net_io()
        speed = {}

        no_traffic = {'GLOBAL':{'OUT':0.0, 'IN':0.0}}
        result = no_traffic
        # t = t_pre
        # res_pre_pre = {}
        interval = 2
        # net_port_query_time = int(time.time())
        # nat_ports = self.natport
        while 1:
            if self.event.isSet():
                self.if_res = no_traffic
                FWLOG_DEBUG('EVENT SET:[STATISTICS:if watch process]')
                getLogger('log_daemon').debug('EVENT SET:[STATISTICS:if watch process]')
                break

            traffic_pre = result
            nat_ports = self.natport
            bdg_ports = self.bridgeport
            ports_info = self.netportinfo
            # result,_pre,t_pre,_pre_pre = interface_traffic(t_pre,res_pre,
            #                                                nat_ports,res_pre_pre)

            try:
                # pre_io, pre_t, _, speed = get_net_speed(pre_io, pre_t, nat_ports, bdg_ports)
                pre_io, pre_t, _, speed = get_net_speed(pre_io, pre_t,
                                                    nat_ports, bdg_ports, ports_info)
                # check if interface is overload
                self.if_traffic_check(speed, self.if_type)
            except Exception as e:
                FWLOG_ERR('[if watch]error %s' % e)
                FWLOG_ERR('[if watch]error %s' % nat_ports)
                FWLOG_ERR('[if watch]error %s' % bdg_ports)
                FWLOG_ERR('[if watch]error %s' % ports_info)
                
                self.update_info()
                nat_ports = self.natport
                bdg_ports = self.bridgeport
                ports_info = self.netportinfo
                pre_t = time.time()
                pre_io = get_net_io()
                speed = {}
                time.sleep(1)
                continue

            # if result == no_traffic:
            #     result = traffic_pre
            #     t_pre = t
            #     _pre = res_pre
            #     _pre_pre = res_pre_pre
            # else:
            #     self.if_traffic_check(result, self.if_type)
            #     t = t_pre
            #     traffic_pre = result
            #     res_pre = _pre
            #     res_pre_pre = _pre_pre
            # self.if_res = result
            self.if_res = speed
            time.sleep(interval)


        FWLOG_DEBUG('QUIT:[STATISTICS:if watch process]')
        getLogger('log_daemon').debug('QUIT:[STATISTICS:if watch process]')

    def is_local_ip(self,ip):
        """
            Description:
                Find out if the ip should be processed, if not, return False,
                Else True
        """
        for _ip, mode in self.netport:
            for i in _ip.split(','):
                _ip = i
                if _ip:
                    addr = _ip.split('/')[0]
                    mask = _ip.split('/')[1]
                    # new for gjdw test
                    if ip in IP(addr):
                        return True

                    # # if netport mode is NAT, ignore all IP in the same net as
                    # # netport
                    # if mode == "nat":
                    #     # netport IP change from a.b.c.d/mask to a.b.c.0/mask
                    #     addr = '.'.join(addr.split('.')[0:3]) + '.0/' + mask

                    # # if netport mode is NOT NAT, just check if IP is same as
                    # # netport IP
                    # if ip in IP(addr):
                    #     return True

        return False
        pass

    def update_address_info(self):
        """
            Description:
                query database and fetch all useful infomation
        """
        # from db.config import fetchall_sql as fetchall_sql_3306

        # # this _FILE is create by PHP, if _FILE does not exists at first,create
        # # time is 0
        # _FILE = '/tmp/.ADDRESS_INFO_UPDATE_FLAG'

        # _file_mtime = lambda :0 if not os.path.exists(_FILE) else os.stat(_FILE).st_mtime
        # _current_mtime = -1
        # ipset_id = set()


        # def _add_queried_ip(_res):
        #     ip_all = '0.0.0.0'
        #     # find record of active IP/IPSet
        #     if not _res['sAddress'] == ip_all:
        #         # format and add IP/IPSET to queried_ip
        #         if _res['sAddtype'] == '1':
        #             if _res['sAddress'][-1] == 0:
        #                 mid = r'/'
        #                 ip_set = _res['sAddress'] + mid + _res['sNetmask']
        #             else:
        #                 ip_set = _res['sAddress']
        #             self.queried_ip.add((ip_set,_res['id']))
        #         elif _res['sAddtype'] == '2':
        #             ip_net = '.'.join(_res['sAddress'].split('.')[0:3])
        #             ip_from = int(_res['sAddress'].split('.')[3])
        #             ip_to = int(_res['sNetmask'].split('.')[3])
        #             for i in range(ip_from,ip_to + 1):
        #                 self.queried_ip.add((ip_net + '.' + str(i),_res['id']))
        #     pass

        # while 1:
        #     if self.event.isSet():
        #         print 'EVENT SET:[STATISTICS:update_address_info]'
        #         getLogger('log_daemon').debug('EVENT SET:[STATISTICS:update_address_info]')
        #         break
        #     # if queried_ip is Null or time to query again, update queried_ip set
        #     if _current_mtime < _file_mtime():
        #         _current_mtime = _file_mtime()
        #         # print 'update_address_info'
        #         self.queried_ip_timer = int(time.time())
        #         self.queried_ip = set()
        #         sql = 'select id,sAddress,sNetmask,sAddtype from m_tbaddress_list'
        #         self.address_list = {res['id']:res for res in fetchall_sql_3306(sql)}
        #         sql = 'select id,sGroupName,sIP from m_tbaddressgroup ORDER BY id DESC'
        #         self.address_group = {res['id']:res for res in fetchall_sql_3306(sql)}
        #         sql = 'select sSourceIP,iSourceIPType,iStatus from m_tbSnat'
        #         self.address_snat = [res for res in fetchall_sql_3306(sql)]
        #         sql = ('select sPortName,sIPV4Address,sWorkMode from m_tbnetport '
        #                'where sPortName like "vEth%%"')
        #         _query_res = [res for res in fetchall_sql_3306(sql)]
        #         self.natport = [res['sPortName'] for res in _query_res
        #                         if res['sWorkMode'] == "nat"]
        #         self.netport = [(res['sIPV4Address'], res['sWorkMode'])
        #                         for res in _query_res]
        #         self.bridgeport = [res['sPortName'] for res in _query_res
        #                            if res['sWorkMode'] == "bridge"]

        #         ## get active ip set id
        #         for res in self.address_snat:
        #             if res['iStatus'] == 1:
        #                 ipset_id.add((res['sSourceIP'],res['iSourceIPType']))
        #         # print ipset_id

        #         # find out all active IP/IPSET
        #         for (_id,_id_type) in ipset_id:
        #             _id = int(_id)
        #             # find active IP/IPSET from address_list
        #             if int(_id_type) == 1:
        #                 try:
        #                     _add_queried_ip(self.address_list[_id])
        #                 except KeyError:
        #                     pass
        #             elif int(_id_type) == 2:
        #                 if _id in self.address_group:
        #                     _ips = self.address_group[_id]['sIP'].split(',')
        #                     for _ip in _ips:
        #                         _ip = int(_ip)
        #                         try:
        #                             _add_queried_ip(self.address_list[_ip])
        #                         except KeyError:
        #                             pass

        #                 pass
        #                 # ip set
        #         # print self.queried_ip
        #     time.sleep(1)

        FWLOG_DEBUG('QUIT:[STATISTICS:update_address_info]')
        getLogger('log_daemon').debug('QUIT:[STATISTICS:update_address_info]')
        pass

    def is_config_ip(self,ip):
        """
            Description:
                Find out if the ip should be processed, if not, return False, Else True
        """

        # if ip is in SHOULD PROCESS set
        for (exists_ip,_ip_id) in self.queried_ip:
            if ip in IP(exists_ip):
                self.address_id = _ip_id
                return False

        # if ip is a PRIVATE ip, process it anyway
        self.address_id = -1
        if IP(ip).iptype() == 'PRIVATE':
            return False

        return True


    def proc_user(self,l):
        ls = l.split(',')
        try:
            assert(len(ls[0].split('.')) == 4)
            _ = IP(ls[0])
        except:
            return
        #IP Fliter
        #dont process broadcast ip
        if ls[0].split('.')[3] == '255':
            return
        ##dont process system ip
        if self.is_local_ip(ls[0]):
            return
        ##if ip is not in database
        if self.is_config_ip(ls[0]):
            return
        # if ip should be processed find group name and add unit
        # if no group name is found, set it 'Anonymous'
        ug = 'Anonymous'
        if self.address_id != (-1):
            for res in self.address_group:
                if self.address_id in self.address_group[res]['sIP'].split(','):
                    ug = self.address_group[res]['sGroupName']
                    break
            pass

        #inter function, use for adding unit to bandwidth
        def add_unit(num):
            return (str(num) +'B/s' if num < 1024 else str(round(num/1024,2))+'KB/s'
                    if num < 1048576 else str(round(num/1048576,2))+'MB/s')

        self.user.append({'sUserName':ls[0],'iGroupID':str(ug),
                          'iUpload':add_unit(int(ls[1])),
                          'iDownload':add_unit(int(ls[2]))})

    def user_bw_add_unit(self,user):
        if user ==[]:
            return []
        #sortl = sorted(user,key = lambda x:x['iUpload']+x['iDownload'],reverse=True)
        sort = [ {'sUserName':item['sUserName'],'iGroupID':item['iGroupID'],'iUpload':self.add_unit([item['iUpload']]),'iDownload':self.add_unit([item['iDownload']])}for item in user]
        return sort

    def proc_application(self,l):
        ls = l.split(',')
        #self.application[ls[0]] = ls[1]
        self.application.append({ls[0]:int(ls[1])})

    def app_bw_add_unit(self,app):
        if app == []:
            return []
        sortl = sorted(app,key=lambda x:x.values(),reverse=True)

        sortl = [ {item.keys()[0]:self.add_unit(item.values())} for item in sortl  ]
        return sortl

    def add_unit(self,numl):
        num = numl[0]
        return str(num) +'B/s' if num < 1024 else str(round(num/1024,2))+'KB/s' if num < 1048576 else str(round(num/1048576,2))+'MB/s'

    def run(self):
        count = 0
        self.sys_thd = threading.Thread(target=self.sys_info_update)
        self.sys_thd.setDaemon(True)
        self.sys_thd.start()
        self.if_watch = threading.Thread(target=self.if_watch_thread)
        self.if_watch.setDaemon(True)
        self.if_watch.start()
        # self.info_thd = threading.Thread(target=self.update_address_info)
        # self.info_thd.setDaemon(True)
        # self.info_thd.start()
        # self.tfs = TrafficStatistic()
        # self.tfs.start()
        self.thread = threading.Thread(target=read_traffic_info)
        self.thread.setDaemon(True)
        #SOCKET init
        server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.settimeout(5)
        server.bind(('127.0.0.1',5678))

        self.thread.start()

        sect = ''
        t_pre = interface_current_time()
        res_pre = interface_get_traffic()
        interface_pre = self.interface
        interface_no_traffic = {'GLOBAL':{'OUT':0.0, 'IN':0.0}}
        t = t_pre
        while True:
            if self.event.isSet():
                FWLOG_DEBUG('EVENT SET:[STATISTICS:run]')
                getLogger('log_daemon').debug('EVENT SET:[STATISTICS:run]')
                self.interface={'GLOBAL':{'OUT':0.0,'IN':0.0,}}
                self.user=[]
                self.application=[]
                self.iIN = 0
                self.iOUT = 0
                self.record_statistics()
                break
                #return
            try:
                rec = server.recvfrom(1024)[0]
            except:
                self.user=[]
                self.application=[]
                self.interface = self.if_res
                self.record_statistics()
                continue
            count = 0
            ls = rec.split('\n')[0:-1]

            for l in ls:
                if l == '' or l == '\n':
                    continue
                if l == 'end':
                    sect = l
                    break
                if l in self.section:
                    sect = l
                else:
                    self.section[sect](l)

            # if sect == 'application':
            if sect == 'end':
                if self.user or self.application:
                    self.interface = self.if_res
                else:
                    self.interface = self.if_res
                    # self.interface = interface_no_traffic
                self.record_statistics()
                self.user=[]
                self.application=[]

            #time.sleep(0.1)
        self.sys_thd.join()
        FWLOG_DEBUG('QUIT:[STATISTICS:run]')
        getLogger('log_daemon').debug('QUIT:[STATISTICS:run]')
        stop_traffic_info()

    def start(self):
        super(HomePageUpdate,self).start()
        pass

    def stop(self):
        FWLOG_DEBUG('statistic stop')
        getLogger('log_daemon').debug('statistic stop')
        self.event.set()
        # self.tfs.stop()
        # stop_traffic_info()
        pass

    def update_info(self, *args, **kwargs):
        """
            Description:
                query database and fetch all useful infomation
        """
        from db.config import fetchall_sql as fetchall_sql_3306

        ipset_id = set()

        def _add_queried_ip(_res):
            ip_all = '0.0.0.0'
            # find record of active IP/IPSet
            if not _res['sAddress'] == ip_all:
                # format and add IP/IPSET to queried_ip
                if _res['sAddtype'] == '1':
                    if _res['sAddress'][-1] == 0:
                        mid = r'/'
                        ip_set = _res['sAddress'] + mid + _res['sNetmask']
                    else:
                        ip_set = _res['sAddress']
                    self.queried_ip.add((ip_set,_res['id']))
                elif _res['sAddtype'] == '2':
                    ip_net = '.'.join(_res['sAddress'].split('.')[0:3])
                    ip_from = int(_res['sAddress'].split('.')[3])
                    ip_to = int(_res['sNetmask'].split('.')[3])
                    for i in range(ip_from,ip_to + 1):
                        self.queried_ip.add((ip_net + '.' + str(i),_res['id']))
            pass

        FWLOG_DEBUG('update_address_info')
        self.queried_ip = set()
        sql = 'select id,sAddress,sNetmask,sAddtype from m_tbaddress_list'
        self.address_list = {res['id']:res for res in fetchall_sql_3306(sql)}
        sql = 'select id,sGroupName,sIP from m_tbaddressgroup ORDER BY id DESC'
        self.address_group = {res['id']:res for res in fetchall_sql_3306(sql)}
        sql = 'select sSourceIP,iSourceIPType,iStatus from m_tbSnat'
        self.address_snat = [res for res in fetchall_sql_3306(sql)]
        sql = ('select sPortName,sIPV4Address,sWorkMode from m_tbnetport '
               'where sPortName like "vEth%%"')
        _query_res = [res for res in fetchall_sql_3306(sql)]
        self.natport = [res['sPortName'] for res in _query_res
                        if res['sWorkMode'] == "nat"]
        self.netport = [(res['sIPV4Address'], res['sWorkMode'])
                        for res in _query_res]
        sql = ('select sBindDevices from m_tbbridgedevice where iStatus=1;')
        # net-number: less is inter-net, bigger is outer-net
        self.bridgeport = [tuple(sorted(res['sBindDevices'].split(',')))
                           for res in fetchall_sql_3306(sql)]
        sql = ('SELECT sPortName, sWorkMode, sPortMode FROM m_tbnetport WHERE `iStatus`=1;')
        self.netportinfo = {res['sPortName']:res['sPortMode']
                            for res in fetchall_sql_3306(sql)}


        ## get active ip set id
        for res in self.address_snat:
            if res['iStatus'] == 1:
                ipset_id.add((res['sSourceIP'],res['iSourceIPType']))
        FWLOG_DEBUG(ipset_id)

        # find out all active IP/IPSET
        for (_id,_id_type) in ipset_id:
            _id = int(_id)
            # find active IP/IPSET from address_list
            if int(_id_type) == 1:
                try:
                    _add_queried_ip(self.address_list[_id])
                except KeyError:
                    pass
            elif int(_id_type) == 2:
                if _id in self.address_group:
                    _ips = self.address_group[_id]['sIP'].split(',')
                    for _ip in _ips:
                        _ip = int(_ip)
                        try:
                            _add_queried_ip(self.address_list[_ip])
                        except KeyError:
                            pass

                pass
                # ip set
        FWLOG_DEBUG(self.queried_ip)


if __name__ == '__main__':
    hp = HomePageUpdate()

    ###os.system('/home/ng_platform/bd_dpdk_warper/clients/traffic_count_flag disable')
    #hp.start()
    ##hp.proc_user('199.189.1.16,123')
    #hp.proc_user('192.168.10.11,123')
    #hp.proc_user('1.0.1.12,123')
    #time.sleep(5)
    hp.run()
    #hp.if_watch_thread()
    #hp.get_interface_type('aa','vEth0','dd','vEth1','dc')
    #hp.if_type = {}
    #hp.if_traffic_check({'vEth0':{'IN':1,'OUT':2}},hp.if_type)
    #print hp.if_type
    #hp.if_traffic_check({'vEth0':{'IN':1,'OUT':2}},hp.if_type)
    #print hp.if_type
    #hp.if_traffic_check({'vEth0':{'IN':1,'OUT':2}},hp.if_type)
    #print hp.if_type
    #print hp.update_address_list()
    ## import on/off test
    # from log_config import read_config_ini
    # d = read_config_ini('LOG Config')
    # d['import'] = 'on'
    # print str(d)
    # ind = 'CMD_LOG_CONFIG|' + str(d)
    # print ind
    # os.system('echo "%s" > /Data/apps/wwwroot/firewall/fifo/second_firewall.fifo' % ind)

    print hp.is_local_ip('172.16.3.99')
    print hp.is_local_ip('172.16.3.9')
    FWLOG_DEBUG(hp.is_local_ip('172.16.3.99'))
    #hp.update_address_info()

    print hp.is_config_ip('182.168.10.3')
    print hp.is_config_ip('119.16.5.89')
    print hp.is_config_ip('192.168.0.255')
    print hp.is_config_ip('172.16.3.3')
    print hp.is_config_ip('3.3.3.3')
    print hp.is_config_ip('2.2.2.2')
    print hp.is_config_ip('1.1.1.1')
    #hp.stop()
    #hp.sys_info_update()
    hp.proc_user('192.168.200.3,432,123')
    hp.proc_user('2.2.2.2,432,123')
    hp.proc_user('a,432,123')
    ###cmd = "ps -ef | grep '/usr/sbin/CROND -n' | grep -v grep | awk '{print $2}'"
    ###ppid = commands.getoutput(cmd)
    ###if not ppid=='':
    ###    print 'ppid = ',ppid
    ###else:
    ###    print 'cant find ppid'
