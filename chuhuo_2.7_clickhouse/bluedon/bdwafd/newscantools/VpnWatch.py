import os
import sys
import time
import logging
import logging.handlers
import ConfigParser
from lib.common import *
from HostScan import db_manager
from VpnManage import VpnManage
from nvscan_xmlrpc import *

def DEBUG(msg):
    logging.getLogger().info(msg)

def WARN(msg):
    logging.getLogger().warn(msg)

def ERROR(msg):
    logging.getLogger().error('File:Vpn_Watch.py, ' + msg)

def vpn_on():
    try:
        vpnManage = VpnManage(1)
    except Exception,e:
        ERROR("vpn_on:"+str(e))

def vpn_off():
    try:
        vpnManage = VpnManage(2)
    except Exception,e:
        ERROR("vpn_off:"+str(e))

def resume_task(dbh):
    try:
        sql = "update task_manage set state = 2 where state = 4 and web_pause = 0 and vpn_enable = 1"
        dbh.set_item_to_db(sql)
    except Exception,e:
        ERROR("resume_task, "+str(e))

def check_vpn_connection():
    try:
        res = vulscan_popen('ifconfig | grep ppp')
        if not res:
            return False
        else:
            return True
    except Exception, e:
        ERROR('check_vpn_connection,' + str(e))
        return False

def check_is_vpn_config_ok(dbh):
    try:
        sql = "select Value from config where Name='vpn_username' or Name='vpn_password' or Name='vpn_ip'"
        items = dbh.get_all_item_from_db(sql)
        for item in items:
            if not item.get('Value'):
                return False
        return True
    except Exception, e:
        ERROR('check_is_vpn_config_ok,' + str(e))
        return False

def pause_nvscan(task_id, scan_uuid, dbh):
    try:
        if not scan_uuid:
            return
        scanner = nvscan_xmlrpc()
        scanner.stop_scan(scan_uuid)
        scanner.del_report(scan_uuid)
        sql = "update task_manage set scan_uuid = '' where `id` = %d" % (int(task_id))
        dbh.set_item_to_db(sql)
    except Exception, e:
        ERROR('pause_nvscan,' + str(e))

def pause_task(dbh, pause_flag=0):
    try:
        sql = "select id, scan_uuid from task_manage where vpn_enable=1 and web_pause = 0"
        vpn_tasks = dbh.get_all_item_from_db(sql)
        # ERROR(str(vpn_tasks))
        if vpn_tasks:
            for vpn_task in vpn_tasks:

                cmd = """for i in $(ps -ef | grep /usr/bin/python |grep -v grep | grep -e "[WebScan|WeakScan|PreScan|HostScan|ScanHostMsg]" | grep "%s#" |awk '$0 !~/grep/ {print $2}' |tr -s '\\n' ' ');do
 kill -9  $(ps -ef | grep $i | grep -v grep | awk '{print $2}')
done"""%(vpn_task.get('id'))
                vulscan_popen(cmd)
                pause_nvscan(vpn_task.get('id'), vpn_task.get('scan_uuid'), dbh)


        #Step 1. Modify task_manage table status 

        sql = ''
        if pause_flag == 0:
            sql = "update task_manage set state = 4 where state = 2 and vpn_enable = 1 and web_pause = 0" 
        elif pause_flag == 1:
            sql = "update task_manage set state = 4, web_pause = 1, vpn_enable = 2 where vpn_enable = 1 and (state = 2 || state = 4) and web_pause = 0" 
        # ERROR(sql)
        dbh.set_item_to_db(sql)

    except Exception, e:
        ERROR("pause_task,"+str(e))

def task_running(dbh):
    try:
        sql = "select count(*) as c from task_manage where web_pause = 0 and vpn_enable = 1 and (state = 2 or state = 4)"
        running_task = dbh.get_one_item_from_db(sql)
        # ERROR(str(running_task))
        if running_task['c'] > 0:
            return True
        else:
            return False
    except Exception,e:
        ERROR("task_running:"+str(e))
        return False

def quit(dbh):
    try:
        pause_task(dbh, 1)
        vpn_off()
    except Exception, e:
        ERROR("quit, "+str(e))

def main():
    try:
        dbh = db_manager()
        reconnect_times = 0;
        #Step 1. check if all vpn username and password is ok
        if not task_running(dbh):
            quit(dbh)
            return
        if check_is_vpn_config_ok(dbh):
            sql = "select Value from config where Name='vpn_times'"
            res = dbh.get_one_item_from_db(sql)
            if res:
                reconnect_times = int(res.get('Value'))
            if reconnect_times < 1 or reconnect_times > 100:
                ERROR('main, reconnect_times error[' + str(reconnect_times) + '],exit')
                quit(dbh)
                return
            while reconnect_times > 0:
                #Step 2. check vpn connection is ok
                if check_vpn_connection():
                    if task_running(dbh):
                        resume_task(dbh)
                    else:
                        quit(dbh)
                        return
                else:
                    #step 3. stop all vpn task
                    ERROR('no vpn connection, stop all vpn task')
                    ERROR('reconnect_times:' + str(reconnect_times))

                    pause_task(dbh)
                    #step 4. reconnect vpn
                    ERROR('reconnect vpn')
                    vpn_on()
                    reconnect_times -= 1
                    time.sleep(10)

                time.sleep(1)
            ERROR('main, reach max retry times, stop it.')
            quit(dbh)
        else:
            ERROR('Check VPN config failed, exit.')
            quit(dbh)
            return

    except Exception, e:
        ERROR('main,' + str(e))


if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    main()

