#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import datetime
import time
from lib.common import *
import os
import ConfigParser
import MySQLdb
import sys
import glob
import Upgrade

DEFAULT_HOST_ONE_REF = '127.0.0.1 %snvs.localdomain %snvs'
DEFAULT_HOST_TWO_REF = '127.0.0.1 localhost.localdomain localhost'
DEFAULT_HOST_THREE_REF = '127.0.0.1 %snvs'

PATH_HOSTS = "/etc/hosts"
PATH_HOSTS_HEAD = '/etc/hosts.head'
PATH_HOSTS_HEAD_NEW = '/etc/hosts.head.new'

WAF_VENDOR = '/var/waf/vendor.conf'

class CheckInstance:
    def __init__(self):
        try:
            self.conn = ""
            self.cursor = ""
        except Exception,e:
            logging.getLogger().error("File:CheckInstance.py, CheckInstance.__init__: " + str(e))
        #end try
    #end def
    
    def clearTempFile(self):
        try:
            time_diff = 3600 * 12 * 7
            dir = "/var/webs/"
            lines = vulscan_popen("ls -l %s" % (dir))
            
            for line in lines:
                if line.find('task_id') >= 0 and line.find('domain_id') >= 0:
                    temp = line.split(' ')
                    last_edit_time = "%s %s" % (temp[-3],temp[-2])
                    name = temp[-1]
                    
                    format="%Y-%m-%d %H:%M"
                    t1=time.strptime(last_edit_time,format)
                    t2=datetime.datetime(t1[0],t1[1],t1[2],t1[3],t1[4],t1[5],t1[6])
                    ux = int(time.mktime(t2.timetuple()))
                    
                    if ux < time.time() - time_diff:
                        vulscan_popen("rm -R /var/webs/%s" % (name))
                    #end if
                #end if
            #end for
            
        except Exception,e:
            logging.getLogger().error("File:CheckInstance.py, CheckInstance.clearTempFile:" + str(e))
        #end try
    #end def

    #Add function to check hosts file
    def checkHosts(self):
        try:
            #get oem
            cfg    = ConfigParser.RawConfigParser()
            cfg.readfp(open(WAF_VENDOR))
            oem = cfg.get("vendor", "VENDOR_SHORT_NAME_STR_ID").replace('"', '').strip()
            if 'yxlink' in oem:
                pass
            else:
                oem = ''
            DEFAULT_HOST_ONE = DEFAULT_HOST_ONE_REF%(oem, oem)
            DEFAULT_HOST_TWO = DEFAULT_HOST_TWO_REF
            DEFAULT_HOST_THREE = DEFAULT_HOST_THREE_REF%(oem)
            fp = open(PATH_HOSTS, 'rb')
            lines = fp.readlines()

            flagOne = False
            flagTwo = False
            flagThree = False

            for line in lines:
                items = line.split()
                if len(items) >= 2 and items[0].strip() == '127.0.0.1':
                    if DEFAULT_HOST_ONE.split()[1].strip() == items[1].strip():
                        flagOne = True  
                    if DEFAULT_HOST_TWO.split()[1].strip() == items[1].strip():
                        flagTwo = True  
                    if DEFAULT_HOST_THREE.split()[1].strip() == items[1].strip():
                        flagThree = True    
            fp.close()

            wp = open(PATH_HOSTS_HEAD, 'wb+')
            if not flagOne:
                wp.write(DEFAULT_HOST_ONE + '\n')
            if not flagTwo:
                wp.write(DEFAULT_HOST_TWO + '\n')
            if not flagThree:
                wp.write(DEFAULT_HOST_THREE + '\n')
            wp.close()

            if not flagOne or not flagTwo or not flagThree:
                cmdstr1 = 'cat ' + PATH_HOSTS_HEAD + ' ' + PATH_HOSTS + ' > ' + PATH_HOSTS_HEAD_NEW
                cmdstr2 = 'mv -f ' + PATH_HOSTS_HEAD_NEW + ' ' + PATH_HOSTS
                cmdstr3 = 'rm ' + PATH_HOSTS_HEAD 
                os.system(cmdstr1)
                os.system(cmdstr2)
                os.system(cmdstr3)

        except Exception, e:
            logging.getLogger().error("File:CheckInstance.py, CheckInstance.main:" + str(e))

    def clearScanLog(self):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = "select id,end_time,web_enable from task_manage"
            cursor.execute(sql)
            conn.commit()
            results = cursor.fetchall()
            for res in results:
                if res['web_enable'] and res['end_time'] and (int(time.time()) - int(time.mktime(res["end_time"].timetuple()))) >= 7*12*3600:
                    match = glob.iglob('/var/webs/scanlog/%s#*' % res['id'])
                    for m in match:
                        os.remove(m)
                    #end for
                #end if
            #end for
        except Exception,e:
            logging.getLogger().error("File:CheckInstance.py, CheckInstance.clearScanLog:" + str(e))
        #end try
    #end def

    def checkNvscan(self):
        try:
            cmd='''#!/bin/sh
process=`ps -ef | grep "nvscan-service" | grep -v grep|wc -l`
if test $process -eq 0
then
    echo "no"
    service nvscand restart
else
    echo "yes"
fi

res1=`ps -ef | grep "nvscan-service" | grep -v grep|wc -l`
res2=`ps -ef | grep "nvscand -q" | grep -v grep|wc -l`
if [ $res1 -eq 0 ] || [ $res2 -eq 0 ]
then
    if [ $res1 -eq 1 ]
    then
        ps -efw | grep "nvscan-service" | grep -v grep  | awk '{print $2}'| xargs kill -9
    fi 

    if [ $res2 -eq 1 ]
    then
        ps -efw | grep "nvscand -q" | grep -v grep  | awk '{print $2}'| xargs kill -9
    fi 
    
    service nvscand restart
fi

'''

            fp = open('/tmp/checkNvs.sh', 'w+')
            fp.write(cmd)
            fp.close()
            os.system('/bin/sh /tmp/checkNvs.sh')
        except Exception, e:
            logging.getLogger().error("File:CheckInstance.py, CheckInstance.checkNvscan:" + str(e))

    def clearNvscanuuid(self):
        try:
            import nvscan_xmlrpc
            import HostScan
            db = HostScan.db_manager()
            p = nvscan_xmlrpc.nvscan_xmlrpc()
            scan_uuid_list = []

            #Step 1.get all uuid from mysql
            sql = 'select scan_uuid from nvscan_list'
            res = db.get_all_item_from_db(sql)
            if res:
                for item in res:
                    scan_uuid_list.append(item.get('scan_uuid'))
            #Step 2.del report and del scan_uuid
            if scan_uuid_list:
                for scan_uuid in scan_uuid_list:
                    p.stop_scan(scan_uuid)
                    p.del_report(scan_uuid)
                    sql = "delete from nvscan_list where scan_uuid = '%s'" % (scan_uuid.strip())
                    db.set_item_to_db(sql)
            #Add for BUG #3325 by xiayuying 2014-02-10
            os.system('find /opt/nvscan/var/nvscan/users/admin/reports -mtime +0 -name "*.nvscan*" | xargs rm -f')
            #End

        except Exception, e:
            logging.getLogger().error("File:CheckInstance.py, CheckInstance.clearNvscanuuid:" + str(e))

    #Add by xiayuying 2014-02-20 for BUG #3578
    def backupNvscan(self):
        try:
            if not os.path.isfile("/var/nvscan/nvscan.tar.gz"):
                os.system("touch /var/nvscan/backup.tmp")
                os.system("/bin/tar -zcf /var/nvscan/nvscan.tar.gz -C /var/nvscan nvscan.img&")
                os.system("rm /var/nvscan/backup.tmp")
            else:
                if os.path.isfile("/var/nvscan/backup.tmp"):
                    os.system("/bin/tar -zcf /var/nvscan/nvscan.tar.gz -C /var/nvscan nvscan.img&")
                    os.system("rm /var/nvscan/backup.tmp")
        except Exception, e:
            logging.getLogger().error("File:CheckInstance.py, CheckInstance.backupNvscan:" + str(e))

    def main(self):
        try:
            self.clearTempFile()
            self.checkHosts()
            self.clearScanLog()
            self.checkNvscan()
            # self.backupNvscan()
            self.clearNvscanuuid()
        except Exception,e:
            logging.getLogger().error("File:CheckInstance.py, CheckInstance.main:" + str(e))
        #end try
    #end def
#end class

def sendUpgradeState(mode):
    try:
        if mode == "build":
            if os.path.exists("/var/log/build.state"):
                os.remove("/var/log/build.state")
                Upgrade.sendstate("build")
        elif mode == "rule":
            if os.path.exists("/var/log/rules.state"):
                os.remove("/var/log/rules.state")
                Upgrade.sendstate("rule")
    except Exception, e:
            logging.getLogger().error("File:CheckInstance.py,sendUpgradeState:" + str(e))

def rulescheck(): #check rules update success,if failed,update again(call in nvs_boot_check.sh)
    def updatefailed():
        return os.path.isdir("/var/rules_dir") and os.path.exists("/var/waf/rules_back.dat")

    def clearmiddlefile():
        os.system("rm -rf /var/rules_dir")
        os.system("rm -rf /var/waf/rules_back.dat")

    try:
        if not os.path.exists("/var/log/ruleupdate.once"):
            if not updatefailed():
                clearmiddlefile()
                return
            logging.getLogger().error("File:CheckInstance.py,rulescheck:Last rule update failed,update again")
            os.system("touch /var/log/ruleupdate.once")
            os.system("cp -rf /var/waf/rules_back.dat /tmp/rules.dat")
            if vulscan_call("/usr/bin/python /var/waf/rules_update.py decrypt"): #only success return 0 
                logging.getLogger().error("File:CheckInstance.py,rulescheck :rules_update.py decrypt error")
            else:
                vulscan_call("/usr/bin/touch /var/log/rules.state")
                vulscan_call("/usr/bin/python /var/waf/rules_update.py update&")
        else:
            clearmiddlefile()
            if not updatefailed(): #double check
                os.system("rm -rf /var/log/ruleupdate.once")
            
    except Exception, e:
        logging.getLogger().error("File:CheckInstance.py,rulescheck:" + str(e))

if __name__ == "__main__":
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        if len(sys.argv) == 1:
            checkInstance = CheckInstance()
            checkInstance.main()
        elif len(sys.argv) == 2:
            if sys.argv[1] == "-s":
                sendUpgradeState("build")
            elif sys.argv[1] == "-c":
                rulescheck()
    except Exception,e:
        logging.getLogger().error("File:CheckInstance.py, __main__:" + str(e))
    #end try
#end if
    
    
    
    
    