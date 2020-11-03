#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, time, threading, urllib, urllib2, json, hashlib
from db import conn_scope 
from config import config
from logging import getLogger
from copy import deepcopy
from common import logger_init


class Replication(threading.Thread):
    def __init__(self):
        super(Replication,self).__init__(name = self.__class__.__name__)
        self.event = threading.Event()
        self.cmds = []
        self.secret = 'e6f6447fc3a05bc787490605c6029e01'
        self.reUser = {
            "username": "mysyc",
            "passwd": "6029e01",
            }
        self.tables = [
            'waf.t_actioncat',
            'waf.t_advaccessctrl',
            'waf.t_baseaccessctrl',
            'waf.t_customrules',
            'waf.t_dns',
            'waf.t_httprequesttype',
            'waf.t_httptypeset',
            'waf.t_httpver',
            'waf.t_ipfragment',
            'waf.t_keywordset',
            'waf.t_overflowset',
            'waf.t_redirectpage',
            'waf.t_restrictheaders',
            'waf.t_reverporxy',
            #'waf.t_ha_setting',
            'waf.t_rulecat',
            'waf.t_rulefiles',
            'waf.t_rules',
            'waf.t_ruleset',
            'waf.t_severity',
            'waf.t_spiders',
            'waf.t_user',
            'waf.t_userconfig',
            'waf.t_userrole',
            'waf.t_selfstudyrule',
            'waf.t_snmp_up',
            'waf.t_syslog_up',
            'waf.t_ntp_setting',
            'waf.t_sitestatus',
            'waf.t_webserver_outbound',
            'waf.t_selfstudy_ip_white']

        with open('log/cmdReplicationCache.log', 'w+') as fp:
            line = fp.readline()
            if line:
                self.cmds = json.decode(line)
        open('log/cmdReplicationCache.log', 'w').close()        
        self.quit = 0

    #创建主从备份使用的用户
    def createReUser(self):
        with conn_scope(**config['db']) as (conn, cursor):
            cursor.execute("select * from waf.t_ha_setting limit 1")
            result = cursor.fetchall()[0]
            # database_ip = result[7] or "%"
            database_ip = '%'
            cursor.execute("GRANT REPLICATION SLAVE ON *.* to '"+ self.reUser['username']\
            +"'@'" + database_ip + "' identified by '" + self.reUser['passwd'] + "'")
            cursor.execute("GRANT ALL PRIVILEGES  ON *.* to '" + self.reUser['username']\
             + "'@'" + database_ip + "' identified by '" + self.reUser['passwd'] + "'")

    #修改mysql配置文件,将server_id,offset_id写入数据库
    def changeMysqlcnf(self, filepath="/etc/my.cnf", sid=1, oid=1):
        os.popen('cp %s %s'%(filepath, filepath+'.bck'))
        with conn_scope(**config['db']) as (conn, cursor):
            cursor.execute("select * from waf.t_ha_setting limit 1")
            current_result = cursor.fetchall()[0]
            opposite_database_ip = current_result[7]
            opposite_database_port = current_result[8]
            current_is_setting = current_result[9]
            current_server_id = current_result[10]
            current_offset_id = current_result[11]
        opposite_db = self.getOppositeDatabaseLink()
        opposite_server_id = None
        try:
            with conn_scope(**opposite_db) as (conn, cursor):
                cursor.execute("select * from waf.t_ha_setting limit 1")
                opposite_result = cursor.fetchall()[0]    
                opposite_server_id = opposite_result[10]
                opposite_offset_id = opposite_result[11]
                opposite_is_setting = opposite_result[9]
        except  Exception , e:
            pass
        
        if opposite_server_id:
            if opposite_server_id == 1: sid = 2
            if opposite_offset_id == 1: oid = 2
        
        with conn_scope(**config['db']) as (conn, cursor):
            cursor.execute("update waf.t_ha_setting set server_id=%d, offset_id=%d"%(sid, oid))

        with open(filepath, 'r+') as fp:
            cnfs = {
                "server-id": sid, 
                "log-bin": "mysql-bin",
                "slave-skip-errors": "all",
                "auto_increment_increment": 2,
                "auto_increment_offset": oid,
                "replicate_wild_do_table": self.tables}
            cnfs_index = {}
            for cnf in cnfs.keys():
                cnfs_index[cnf] = 0
            cnfs_index["[mysqld]"] = 0
            lines = fp.readlines()
            for idx, line in enumerate(lines):
                for cnf in cnfs_index.keys():
                    if line.find(cnf) != -1:
                        cnfs_index[cnf] = idx
                        break
                for table in cnfs["replicate_wild_do_table"]: 
                    if line.find(table) != -1:
                        cnfs["replicate_wild_do_table"].remove(table)
                        break
            for cnf in cnfs_index.keys():
                if cnf == "[mysqld]": continue
                if cnf == "replicate_wild_do_table":
                    for tab in cnfs["replicate_wild_do_table"]:
                        lines[cnfs_index["[mysqld]"]] += "\nreplicate_wild_do_table=%s\n"%(tab)
                    continue
                if cnfs_index[cnf] != 0:
                    lines[cnfs_index[cnf]] = "%s=%s\n"%(cnf, cnfs[cnf])
                else:
                    lines[cnfs_index["[mysqld]"]] += "\n%s=%s\n"%(cnf, cnfs[cnf])
            fp.seek(0)    
            fp.writelines(lines)
        os.system('rm /var/lib/mysql/auto.cnf')  # uuid
        os.popen("service mysql restart")    

    def stopHA(self):
        try: 
            oppositedb = self.getOppositeDatabaseLink()
            with conn_scope(**oppositedb) as (conn, cursor):
                cursor.execute("stop slave")
        except:
            return False

        try:
            with conn_scope(**dbconfig) as (conn, cursor):
                cursor.execute("stop slave")
        except:
            return False
        return True

    def startHA(self):
        # 对端设置为本地slave
        oppositedb = self.getOppositeDatabaseLink()
        try: 
            with conn_scope(**oppositedb) as (conn, cursor):
                cursor.execute("select database_ip from waf.t_ha_setting")
                youhost = cursor.fetchall()[0][0]
            with conn_scope(**config['db']) as (conn, cursor):
                cursor.execute("show master status")
                youstatus = cursor.fetchall()[0]
            start_you = self.startSlave(youstatus, youhost, oppositedb)
            getLogger('main').info("start you %s" % start_you)
        except Exception , e:
            #getLogger('main').error(e)
            return False
        # 本地设置为对端slave
        try:
            OppositemasterStatus, myhost = self.getOppositeDatabaseMasterStatus()
            start_my = self.startSlave(OppositemasterStatus, myhost, config['db'])
        except Exception , e:
            pass
            #getLogger('main').error(e)
        return start_my and start_you

    #配置本地服务器为Slave
    def slaveConfig(self, host, logFile, logPos, dbconfig = config['db']):
        with conn_scope(**dbconfig) as (conn, cursor):
            cursor.execute("stop slave")
            cursor.execute("change master to master_host='" + host + "', master_user='"\
            + self.reUser['username'] +"', master_password='" + self.reUser['passwd'] +\
            "', master_log_file='" + logFile + "',master_log_pos=%d"%logPos)
            cursor.execute("start slave")

    #查询对端主机的master status
    def getOppositeDatabaseMasterStatus(self):
        oppositedb = self.getOppositeDatabaseLink()
        status = False
        try: 
            with conn_scope(**oppositedb) as (conn, cursor):
                cursor.execute("show master status")
                status = cursor.fetchall()[0]
        except Exception , e:
            pass
        with conn_scope(**config['db']) as (conn, cursor):
            cursor.execute("select database_ip from waf.t_ha_setting")
            host = cursor.fetchall()[0][0]
        return status, host


    #以对端为主机,建立备份关系
    def startSlave(self, OppositemasterStatus, host, config):
        #getLogger("main").info("startSlave")
        print OppositemasterStatus, host
        if OppositemasterStatus:
            self.slaveConfig(host, OppositemasterStatus[0], OppositemasterStatus[1], dbconfig=config)
            if self.checkState(config):
                return True
        return False


    #检查slave状态
    def checkState(self, dbconfig):
        try:
            with conn_scope(**dbconfig) as (conn, cursor):
                cursor.execute("show slave status")
                status = cursor.fetchall()
                if status: status = status[0]
            if status and status[10] == 'Yes' and status[11] == 'Yes':
                return True
        except:
            pass
        return False

    #检查对端slave状态
    def checkOppositeState(self):
        oppositedb = self.getOppositeDatabaseLink()
        if self.checkState(oppositedb):
            return True
        return False

    #检查本机slave状态
    def checkCurrentState(self):
        if self.checkState(config['db']):
            return True
        return False

    def init_dbdata(self, my_db_ip, you_db_ip):
        '''
        同步数据库初始数据
        '''
        
        self.stopHA()
        try:
            from task import proc_nginx, proc_deploy_type, proc_ddos
            cmd = 'select TABLE_NAME,UPDATE_TIME from information_schema.TABLES \
                    where TABLE_SCHEMA="waf" order by UPDATE_TIME desc;'
            my_last_time = 0
            you_last_time = 0
            with conn_scope(**config['db']) as (conn, cursor):
                cursor.execute(cmd)
                waf_tables = cursor.fetchall()
                for table in waf_tables:
                    if 'waf.%s' % table[0] in self.tables:
                        break
                my_last_time = table[1]
            
            oppositedb = self.getOppositeDatabaseLink()
            with conn_scope(**oppositedb) as (conn, cursor):
                cursor.execute(cmd)
                waf_tables = cursor.fetchall()
                for table in waf_tables:
                    if 'waf.%s' % table[0] in self.tables:
                        break
                you_last_time = table[1]
        
            from_ip = my_db_ip
            to_ip = you_db_ip
        
            from_db_u = "root"
            from_db_p = "d2!d%9\\)@d"
        
            to_db_u = self.reUser['username']
            to_db_p = self.reUser['passwd']
            if my_last_time > you_last_time:
                # my to you
                from_ip = "127.0.0.1"
                getLogger('main').info('my to you')
                #print "my to you"
            else:
                # you to my
                from_ip = you_db_ip
                to_ip = "127.0.0.1"

                to_db_u = "root"
                to_db_p = from_db_p
            
                from_db_u = self.reUser['username']
                from_db_p = self.reUser['passwd']
                getLogger('main').info('you to me')
                #print "you to my"
        
                #print "sync", "from", from_ip, "to", to_ip
            syc_tables = ' '.join(map(lambda x:x.split('.')[1], self.tables))
            os.system('echo "use waf" > /tmp/syc_tables.sql')
            if from_ip == "127.0.0.1":
                # backup
                os.system('mysqldump -u%s -p%s waf %s >> /tmp/syc_tables.sql' % (from_db_u, from_db_p, syc_tables))
                # update
                os.system("mysql -h%s -u%s -p%s < /tmp/syc_tables.sql" % (to_ip, to_db_u, to_db_p))
            else:
                os.system('mysqldump -h%s -u%s -p%s waf %s >> /tmp/syc_tables.sql' % (from_ip, from_db_u, from_db_p, syc_tables))
                os.system("mysql -u%s -p%s < /tmp/syc_tables.sql" % (to_db_u, to_db_p))
        
            getLogger('main').info('syc db')
            if self.startHA():
                try:
                    with conn_scope(**oppositedb) as (conn, cursor):
                        cursor.execute("update t_ha_setting set had_sync=1") 
                    with conn_scope(**config['db']) as (conn, cursor):
                        cursor.execute("update t_ha_setting set had_sync=1")
                except:
                    pass
            else:
                self.stopHA()
            proc_nginx([])
            proc_ddos([])
        except:
            pass

    def set_opposync(self, sync):       
        oppositedb = self.getOppositeDatabaseLink()                   
        with conn_scope(**oppositedb) as (conn, cursor):              
            cursor.execute("update t_ha_setting set had_sync = %s" % sync) 

    def dbNeedSync(self):
        try:
            had_sync_my = 0
            my_db_ip = ""
            my_enable_ha = 0
            had_sync_you = 0
            you_db_ip = ""
            you_enable_ha = 0
            with conn_scope(**config['db']) as (conn, cursor):
                cursor.execute("select had_sync, database_ip, is_use from waf.t_ha_setting limit 1")
                current_result = cursor.fetchone()
                if current_result:
                    had_sync_my = current_result[0]
                    you_db_ip = current_result[1]
                    my_enable_ha = current_result[2]
            oppositedb = self.getOppositeDatabaseLink()
            with conn_scope(**oppositedb) as (conn, cursor):
                cursor.execute("select had_sync, database_ip, is_use from waf.t_ha_setting limit 1")
                current_result = cursor.fetchone()
                if current_result:
                    had_sync_you = current_result[0]
                    my_db_ip = current_result[1]
                    you_enable_ha = current_result[2]
            return (my_enable_ha == 1 and you_enable_ha == 1, had_sync_my == 0 and
                   had_sync_you == 0, my_db_ip < you_db_ip, my_db_ip, you_db_ip)
        except Exception, e:
            pass
            #getLogger('main').error(e)

    #数据库双主同步
    def dbReplication(self):
        with conn_scope(**config['db']) as (conn, cursor):
            cursor.execute("select * from waf.t_ha_setting")
            current_result = cursor.fetchall()
            if current_result: current_result = current_result[0]

        #获取对端主机的设置
        opposite_result = None
        oppositedb = self.getOppositeDatabaseLink()
        try: 
            with conn_scope(**oppositedb) as (conn, cursor):
                cursor.execute("select * from waf.t_ha_setting") 
                opposite_result = cursor.fetchall()
                if opposite_result: opposite_result = opposite_result[0]
        except:
            pass

        #本机设置数据库同步为开启
        if current_result[16] == 1:
            #数据库双主设置成功
            #getLogger('main').info(current_result[9])
            if current_result[9] == 1:
                try:
                    had_sync_my = 0
                    had_sync_you = 0
                    with conn_scope(**config['db']) as (conn, cursor):
                        cursor.execute("select had_sync from waf.t_ha_setting limit 1")
                        current_result = cursor.fetchone()
                        if current_result:
                            had_sync_my = current_result[0]
                    oppositedb = self.getOppositeDatabaseLink()
                    with conn_scope(**oppositedb) as (conn, cursor):
                        cursor.execute("select had_sync from waf.t_ha_setting limit 1")
                        current_result = cursor.fetchone()
                        if current_result:
                            had_sync_you = current_result[0]
                    if had_sync_my == had_sync_you and had_sync_you == 1:
                        if self.checkCurrentState() and self.checkOppositeState():
                            pass
                        else:
                            #getLogger('main').info('----- slave status not YES-----------')
                            with conn_scope(**config['db']) as (conn, cursor):
                                cursor.execute("update t_ha_setting set had_sync=0")
                            with conn_scope(**oppositedb) as (conn, cursor):
                                cursor.execute("update t_ha_setting set had_sync=0") 
                except Exception, e:
                    pass
                return True
        #本机设置高可用为关闭
        else:
            #数据库双主设置成功
            #if current_result[9] == 1:
            #关闭本机slave
            if self.checkCurrentState():
                with conn_scope(**config['db']) as (conn, cursor):
                    cursor.execute("stop slave")
                    cursor.execute("update waf.t_ha_setting set is_setting=0")
            #关闭对端slave    
            if self.checkOppositeState():
                with conn_scope(**oppositedb) as (conn, cursor):
                    cursor.execute("stop slave")
                    cursor.execute("update waf.t_ha_setting set is_setting=0")
            return True    

        #对端ip判断
        if current_result[7]:
            if not current_result[10]:
                #创建账号  
                self.createReUser()
                #写配置文件
                configPath = '/etc/my.cnf'
                self.changeMysqlcnf(configPath)
        else:
            return False

        #如果获取到对端的设置,并且双端都打开了数据同步
        if opposite_result and opposite_result[16] == 1 and current_result[16] == 1:
            #以对端为主机建立备份关系
            #if not self.checkCurrentState() and not self.startSlave():
            #    return False

            #修改状态
            if self.checkOppositeState() and self.checkCurrentState():
                with conn_scope(**config['db']) as (conn, cursor):
                    cursor.execute("update waf.t_ha_setting set is_setting=1")
                return True
            return False    

        
    def startReplication(self, cmd):
        getLogger('main').info('Replication startReplication %s' % (cmd,))
        self.cmds.append(cmd)

    def stopReplication(self):
        if not self.cmd:
            getLogger('main').info('Replication stopReplication success!')
        else:
            with open('log/cmdReplicationCache.log', 'w+') as fp:
                fp.write(json.encode(self.cmds))
            getLogger('main').info('Replication stopReplication success! cmds write in ReplicationCache.log')
    
    #获取校验码
    def getToken(self):
        ts = int(time.time())
        token = hashlib.md5("%s%s"%(ts, self.secret)).hexdigest()
        return token, ts
    
    #获取对端主机的数据库链接
    def getOppositeDatabaseLink(self):
        with conn_scope(**config['db']) as (conn, cursor):
            cursor.execute("select * from waf.t_ha_setting limit 1")
            current_result = cursor.fetchall()[0]
            opposite_database_ip = current_result[7]
            opposite_database_port = current_result[8]
        opposite_db = deepcopy(config['db'])
        opposite_db["host"] = opposite_database_ip
        opposite_db["user"] = self.reUser["username"]
        opposite_db["passwd"] = self.reUser["passwd"]
        if opposite_database_port:
            opposite_db["port"] = int(opposite_database_port)
        else:
            opposite_db["port"] = 3306
        return opposite_db

    #get请求
    def httpGet(self, url):
        res =urllib2.urlopen(url).read()
        return res
    
    #post请求
    def httpPost(self, data):
        req = urllib2.Request(url, json.dumps(data, ensure_ascii=ensure_ascii))
        req.add_header("Content-Type", "application/json; charset=utf-8")
        ret = json.loads(urllib2.urlopen(req).read())
        return ret
    
    #命令检查
    def checkCmd(self, cmd):
        getLogger('main').info("Replication checkCmd %s"%(cmd))
        noOppositeCmds = [
                "CMD_SYSTOOL|halt",
                "CMD_SYSTOOL|reboot",
                "CMD_ROUTE",
                "CMD_TAR_SYSTEMINFO",
                "CMD_SITESCAN",
                "CMD_TAR_SYSTEMINFO_SEND",
                "CMD_CLEAR_DISK",
                "CMD_UPDATECERT",#更新授权
                "CMD_TAR_SYSCONFIG",#生成配置文件
                "CMD_BRIDGE_MULIP",#网桥相关配置
                "CMD_REFLASH_NIC",
                "CMD_REFLASH_BRIDGE",
                "CMD_REFLASH_ROUTE",
                "CMD_BRIDGE",
                "CMD_SYS_UPDATE",
                "CMD_SSL_LICENCE",
                "CMD_INTERFACE",
                "CMD_DEPLOY_TYPE",
                "CMD_UCARP",
                ]
        if cmd.find("CMD_SYSCONFIG_RESTORE") !=-1 or cmd.find('CMD_UPDATERULE') != -1:
            cmd = "CMD_USE_SYSCONFIG_RESTORE"
        for oppositeCmd in noOppositeCmds:
            if cmd.find(oppositeCmd) != -1: return False
        return cmd

    #发送命令到对端主机
    def sendCmd(self, cmd):
        getLogger('main').info("Replication sendCmd")
        cmd = self.checkCmd(cmd)
        getLogger('main').info("Replication sendCmd checked cmd: %s"%cmd)
        if not cmd:
            return False
        with conn_scope(**config['db']) as (conn, cursor):
            cursor.execute("select is_use, database_ip from waf.t_ha_setting")
            current_result = cursor.fetchall()[0]
        try:    
            oppositedb = self.getOppositeDatabaseLink()
            with conn_scope(**oppositedb) as (conn, cursor):
                cursor.execute("select is_use from waf.t_ha_setting")
                opposite_result = cursor.fetchall()[0]
        except:
            return False
        if current_result[0] == 1 and opposite_result[0] == 1:
            token, ts = self.getToken()
            url = "https://%s:444/cmd.php?token=%s&ts=%s&cmd=Rep$%s"%(current_result[1], token, ts, cmd)
            getLogger('main').info("Replication sendCmd url:  %s"%url)
            result = self.httpGet(url)
            if result == 'false':
                getLogger('main').info("Replication url result %s"%result)
                return False
            return True
        return False

    def start(self):
        getLogger('main').debug(self.__class__.__name__+ ' starting...')
        super(Replication, self).start()
        try:
            oppositedb = self.getOppositeDatabaseLink()
            with conn_scope(**oppositedb) as (conn, cursor):
                cursor.execute("update t_ha_setting set had_sync=0") 
            with conn_scope(**config['db']) as (conn, cursor):
                cursor.execute("update t_ha_setting set had_sync=0")
        except Exception, e:
            pass
        getLogger('main').info(self.__class__.__name__+ ' started.')

    def stop(self):
        getLogger('main').debug(self.__class__.__name__+ ' Exiting...')
        self.stopReplication()
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__+ ' Exited.')

    def proc(self):
        ret = self.dbNeedSync()
        if ret:
            (ha, sync, ip, my_db_ip, you_db_ip) = ret
            if ha and sync and ip:
                self.init_dbdata(my_db_ip, you_db_ip)
        self.dbReplication()
        if self.event.isSet():
            self.quit = 1
            return 0
        if self.cmds:
            cmd = self.cmds.pop()
            self.sendCmd(cmd)
        return 1

    def run(self):
        while True:
            try:
                if self.quit == 1:
                    return
                self.proc()
                time.sleep(10)
            except Exception, e:
                getLogger('main').exception(e)

if __name__ == '__main__':
    #Replication().dbReplication()
    t = Replication()
    ret = t.run()

