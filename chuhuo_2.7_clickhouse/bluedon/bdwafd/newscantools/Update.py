#!/usr/bin/python
#-*-encoding:UTF-8-*-
import MySQLdb
import logging
import sys
from lib.common import *
import pexpect

def update_old_task_manage():
    try:
        logging.getLogger().debug("update_old_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        list = []
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            list.append(row['COLUMN_NAME'])
        #end for
        
        host_enable = "host_enable"
        web_enable = "web_enable"
        weak_enable = "weak_enable"
        port_enable = "port_enable"

        if host_enable in list and web_enable in list and weak_enable in list and port_enable in list:
            cursor.close()
            conn.close()
            return True
        else:
            cursor.execute("DROP TABLE IF EXISTS `task_manage`")
            conn.commit()
            sql = "CREATE TABLE `task_manage` ("
            sql += "`id` int(11) NOT NULL auto_increment,"
            sql += "`task_name` varchar(256) default NULL,"
            sql += "`target` text,"
            sql += "`state` int(1) default NULL,"
            sql += "`init_state` int(1) default NULL,"
            sql += "`prescan_state` int(1) default NULL,"
            sql += "`c` int(11) default NULL,"
            sql += "`h` int(11) default NULL,"
            sql += "`m` int(11) default NULL,"
            sql += "`l` int(11) default NULL,"
            sql += "`i` int(11) default NULL,"
            sql += "`start_time` timestamp NULL default NULL,"
            sql += "`end_time` timestamp NULL default NULL,"
            sql += "`schedule` varchar(128) default NULL,"
            sql += "`host_enable` int(1) default NULL,"
            sql += "`enable_ddos` int(1) default NULL,"
            sql += "`host_state` int(1) default NULL,"
            sql += "`host_policy` int(11) default NULL,"
            sql += "`host_max_script` int(11) default NULL,"
            sql += "`host_thread` int(4) default NULL,"
            sql += "`host_timeout` int(4) default '30',"
            sql += "`web_enable` int(1) default NULL,"
            sql += "`web_spider_enable` int(1) default NULL,"
            sql += "`web_state` int(1) default NULL,"
            sql += "`web_speed` int(1) default NULL,"
            sql += "`web_minute_package_count` int(11) default NULL,"
            sql += "`web_thread` int(4) default NULL,"
            sql += "`web_policy` int(11) default NULL,"
            sql += "`web_url_count` int(11) default NULL,"
            sql += "`web_timeout` int(4) default NULL,"
            sql += "`web_getdomain_timeout` int(4) default NULL,"
            sql += "`web_getdomain_policy` int(1) default NULL,"
            sql += "`web_getdomain_enable` int(1) default NULL,"
            sql += "`web_getdomain_state` int(1) default NULL,"
            sql += "`web_exp_try_times` int(11) default NULL,"
            sql += "`web_exp_try_interval` int(11) default NULL,"
            sql += "`spider_flag` int(1) default NULL,"
            sql += "`weak_enable` int(1) default NULL,"
            sql += "`weak_state` int(1) default NULL,"
            sql += "`weak_thread` int(4) default NULL,"
            sql += "`weak_policy` int(11) default NULL,"
            sql += "`weak_timeout` int(4) default NULL,"
            sql += "`port_enable` int(1) default NULL,"
            sql += "`port_state` int(1) default NULL,"
            sql += "`port_timeout` int(4) default NULL,"
            sql += "`port_thread` int(4) default NULL,"
            sql += "`port_policy` int(11) default NULL,"
            sql += "`vpn_enable` int(1) default '0',"
            sql += "`web_pause` int(1) default '0',"
            sql += "`user_id` int(11) default NULL,"
            sql += "`email` varchar(100) default NULL,"
            sql += "`asset_scan_id` int(11) default '0',"
            sql += "`as_id` int(11) default '0',"
            sql += "`am_id` int(11) default '0',"
            sql += "PRIMARY KEY  (`id`)"
            sql += ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8"
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            return False
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_old_task_manage function:" + str(e))
        return True
    #end try
#end def

def update_add_email_to_task_manage():
    try:
        logging.getLogger().debug("update_add_email_to_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'email':
                cursor.close()
                conn.close()
                return
            #end if
        #end for
        sql = "alter table task_manage add `email` varchar (100) default ''"
        cursor.execute(sql)
        conn.commit()
        
        cursor.close()
        conn.close()
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_email_to_task_manage function:" + str(e))
    #end try
#end def

def update_add_enable_ddos_to_task_manage():
    try:
        logging.getLogger().debug("update_add_enable_ddos_to_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'enable_ddos':
                cursor.close()
                conn.close()
                return
            #end if
        #end for
        sql = "alter table task_manage add `enable_ddos` int(1) default '1'"
        cursor.execute(sql)
        conn.commit()
        
        cursor.close()
        conn.close()
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_enable_ddos_to_task_manage function:" + str(e))
    #end try
#end def

def update_add_web_exp_try_to_task_manage():
    try:
        logging.getLogger().debug("update_add_web_exp_try_to_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        times_exist = False
        interval_exist = False
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'web_exp_try_times':
                times_exist = True
            elif row['COLUMN_NAME'] == 'web_exp_try_interval':
                interval_exist = True
            #end if
        #end for
        if not times_exist:
            sql = "alter table task_manage add `web_exp_try_times` int(11) default '3'"
            cursor.execute(sql)
            conn.commit()
        #end if
        if not interval_exist:
            sql = "alter table task_manage add `web_exp_try_interval` int(11) default '30'"
            cursor.execute(sql)
            conn.commit()
        #end if
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_web_exp_try_to_task_manage function:" + str(e))
    #end try
#end def

def update_add_web_speed_to_task_manage():
    try:
        logging.getLogger().debug("update_add_web_speed_to_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        speed_exist = False
        count_exist = False
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'web_speed':
                speed_exist = True
            elif row['COLUMN_NAME'] == 'web_minute_package_count':
                count_exist = True
            #end if
        #end for
        if not speed_exist:
            sql = "alter table task_manage add `web_speed` int(1) default NULL"
            cursor.execute(sql)
            conn.commit()
        #end if
        if not count_exist:
            sql = "alter table task_manage add `web_minute_package_count` int(11) default NULL"
            cursor.execute(sql)
            conn.commit()
        #end if
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_web_speed_to_task_manage function:" + str(e))
    #end try
#end def

def update_add_spider_flag_to_task_manage():
    try:
        logging.getLogger().debug("update_add_spider_flag_to_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'spider_flag':
                cursor.close()
                conn.close()
                return
        sql = "alter table task_manage add `spider_flag` int(1) default 0"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_spider_flag_to_task_manage function:" + str(e))


def update_add_vpn_to_task_manage():
    try:
        logging.getLogger().debug("update_add_vpn_to_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        vpn_enable_flag = True
        web_pause_flag = True
        for row in res:
            if row['COLUMN_NAME'] == 'vpn_enable':
                vpn_enable_flag = False
            #end if
            if row['COLUMN_NAME'] == 'web_pause':
                web_pause_flag = False
            #end if
        #end for
        if vpn_enable_flag:
            sql = "alter table task_manage add `vpn_enable` int(1) default 0"
            cursor.execute(sql)
            conn.commit()
        #end if
        if web_pause_flag:
            sql = "alter table task_manage add `web_pause` int(1) default 0"
            cursor.execute(sql)
            conn.commit()
        #end if
        cursor.close()
        conn.close()
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_vpn_to_task_manage function:" + str(e))
#end def

def update_add_nvs_interface_to_net_config():
    try:
        logging.getLogger().debug("update_add_nvs_interface_to_net_config")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select count(*) as c from `net_config` where `Type` like '%NVS%'"
        cursor.execute(sql)
        res = cursor.fetchone()
        if res and res['c'] > 0:
            cursor.close()
            conn.close()
        else:
            sql = "update `net_config` set `Type` = 'DMI|NVS' where `Type` = 'DMI'"
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
        #end if
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_nvs_interface_to_net_config function:" + str(e))
    #end try
#end def

def update_add_Iprange_to_user():
    try:
        logging.getLogger().debug("update_add_Iprange_to_user")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'user'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'Iprange':
                cursor.close()
                conn.close()
                return
            #end if
        #end for
        sql = "alter table `user` add `Iprange` varchar (1024) default '*.*.*.*'"
        cursor.execute(sql)
        conn.commit()
        
        cursor.close()
        conn.close()
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_Iprange_to_user function:" + str(e))
    #end try
#end def

def update_add_Maxtasks_to_user():
    try:
        logging.getLogger().debug("update_add_Maxtasks_to_user")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'user'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'Maxtasks':
                cursor.close()
                conn.close()
                return
            #end if
        #end for
        sql = "alter table `user` add `Maxtasks` int(11) DEFAULT 1"
        cursor.execute(sql)
        conn.commit()
        
        cursor.close()
        conn.close()
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_Maxtasks_to_user function:" + str(e))
    #end try
#end def

def update_reportlist():
    try:
        logging.getLogger().debug("update_reportlist")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select * from report_list"
        cursor.execute(sql)
        res = cursor.fetchall()
        conn.close()
        if res and len(res) > 0:
            for row in res:
                filename = row['filename']
                path = "/var/www/Report/%s.zip" % (filename)
                if os.path.isfile(path):
                    continue
                #end if
                path = "/var/www/Report/%s/" % (filename)
                if os.path.isdir(path):
                    vulscan_popen("mv /var/www/Report/%s/report.zip /var/www/Report/%s.zip" % (filename,filename))
                    vulscan_popen("rm -rf /var/www/Report/%s/" % (filename))
                #end if
            #end for
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_reportlist function:" + str(e))
    #end try
#end def

def update_size_reportlist():
    try:
        logging.getLogger().debug("update_reportlist")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        size_exist = False
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'report_list'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'size':
                size_exist = True
            #end if
        #end for
        if not size_exist:
            sql = "alter table `report_list` add `size` varchar(20) default NULL"
            cursor.execute(sql)
            conn.commit()
        
        sql = "select * from report_list where size is null"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            filename = row['filename']
            path = "/var/www/Report/%s.zip" % (filename)
            if os.path.isfile(path):
                size = os.path.getsize(path)/1024
                if size > 1048576:
                    size = "%s GB" % (str(round(size/1048576.0,2)))
                elif size > 1024:
                    size = "%s MB" % (str(round(size/1024.0,2)))
                else:
                    size = "%s KB" % (str(size))
                #end if
                #size = str(round(os.path.getsize(path)/1024.0,2))
                sql = "update `report_list` set `size` = '%s' where `id` = '%s'" % (size,str(row['id']))
                cursor.execute(sql)
                conn.commit()
            else:
                sql = "delete from `report_list` where `id` = '%s'" % str(row['id'])
                cursor.execute(sql)
                conn.commit()
            #end if
        #end for
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_size_reportlist function:" + str(e))
    #end try
#end def

def update_cnvd_vul_details():
    try:
        logging.getLogger().debug("update_cnvd_vul_details")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        '''
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'vul_info'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == "cnvd":
                conn.close()
                return
            #end if
        #end for
        '''
        
        sql = "select id from task_manage"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            table_name = "vul_details_%s" % (str(row['id']))
            
            if table_exists(table_name):
                cnvd_enable = False
                sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = '%s'" % (table_name)
                cursor.execute(sql)
                res2 = cursor.fetchall()
                for row2 in res2:
                    if row2['COLUMN_NAME'] == 'cnvd':
                        cnvd_enable = True
                    #end if
                #end for
                if cnvd_enable == False:
                    sql = "alter table `%s` add `cnvd` varchar(512) default NULL after `cve`" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                #end if
            #end if
        #end for
        cursor.close()
        conn.close()
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_cnvd_vul_details function:" + str(e))
    #end try 
#end def

def restartTask():
    try:
        logging.getLogger().debug("restartTask")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        cmd = "kill -9 $(ps -ef|grep '/usr/bin/python /var/waf/PreScan.py'|awk '$0 !~/grep/ {print $2}' |tr -s '\\n' ' ') "
        vulscan_popen(cmd)
        
        cmd = "kill -9 $(ps -ef|grep '/usr/bin/python /var/waf/HostScan.py'|awk '$0 !~/grep/ {print $2}' |tr -s '\\n' ' ') "
        vulscan_popen(cmd)
        
        cmd = "kill -9 $(ps -ef|grep '/usr/bin/python /var/waf/WebScan.py'|awk '$0 !~/grep/ {print $2}' |tr -s '\\n' ' ') "
        vulscan_popen(cmd)
        
        cmd = "kill -9 $(ps -ef|grep '/usr/bin/python /var/waf/WeakScan.py'|awk '$0 !~/grep/ {print $2}' |tr -s '\\n' ' ') "
        vulscan_popen(cmd)
        
        cmd = "kill -9 $(ps -ef|grep '/usr/bin/python /var/waf/ScanHostMsg.py'|awk '$0 !~/grep/ {print $2}' |tr -s '\\n' ' ') "
        vulscan_popen(cmd)
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, restartTask function:" + str(e))
    #end try
#end def

def update_domain_list_table():
    try:
        logging.getLogger().debug("update_domain_list_table")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select `id` from task_manage"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            id = str(row['id'])
            
            table_name = "domain_list_%s" % (id)
            if table_exists(table_name):
                scheme_enable = False
                title_enable = False
                state_enable = False
                spider_state_enable = False
                progress_enable = False
                progress_status_enable = False
                exception_enable = False
                exception_count_enable = False
                base_path_enable = False
                policy_enable = False
                policy_detail_enable = False
                service_type_enable = False
                site_type_enable = False
                database_type_enable = False
                next_start_time_enable = False
                cookie_url_enable = False
                begin_path_enable = False
                exclude_url_enable = False
                sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = '%s'" % (table_name)
                cursor.execute(sql)
                res2 = cursor.fetchall()
                for row2 in res2:
                    if row2['COLUMN_NAME'] == 'scheme':
                        scheme_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'title':
                        title_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'state':
                        state_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'spider_state':
                        spider_state_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'progress':
                        progress_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'progress_status':
                        progress_status_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'exception':
                        exception_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'exception_count':
                        exception_count_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'base_path':
                        base_path_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'policy':
                        policy_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'policy_detail':
                        policy_detail_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'service_type':
                        service_type_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'site_type':
                        site_type_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'database_type':
                        database_type_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'next_start_time':
                        next_start_time_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'cookie_url':
                        cookie_url_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'begin_path':
                        begin_path_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'exclude_url':
                        exclude_url_enable = True
                    #end if
                #end for
                
                if scheme_enable == False:
                    sql = "alter table `%s` add `scheme` varchar(6) DEFAULT 'http'" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert scheme ")
                #end if
                if title_enable == False:
                    sql = "alter table `%s` add `title` varchar(500) DEFAULT ''" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert scheme ")
                #end if
                if state_enable == False:
                    sql = "alter table `%s` add `state` int(1) DEFAULT '0'" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert state ")
                #end if
                if spider_state_enable == False:
                    sql = "alter table `%s` add `spider_state` int(1) DEFAULT '0'" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert spider_state ")
                #end if
                if progress_enable == False:
                    sql = "alter table `%s` add `progress` text DEFAULT ''" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert progress ")
                #end if
                if progress_status_enable == False:
                    sql = "alter table `%s` add `progress_status` mediumtext" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert progress_status ")
                #end if
                if exception_enable == False:
                    sql = "alter table `%s` add `exception` varchar(512) DEFAULT ''" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert exception ")
                #end if
                if exception_count_enable == False:
                    sql = "alter table `%s` add `exception_count` int(1) DEFAULT '0'" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert exception_count ")
                #end if
                if base_path_enable == False:
                    sql = "alter table `%s` add `base_path` varchar(500) DEFAULT '/'" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert base_path ")
                #end if
                if policy_enable == False:
                    sql = "alter table `%s` add `policy` int(1) DEFAULT '1'" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert policy ")
                #end if
                if policy_detail_enable == False:
                    sql = "alter table `%s` add `policy_detail` text default ''" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert policy_detail ")
                #end if
                if service_type_enable == False:
                    sql = "alter table `%s` add `service_type` varchar(255) DEFAULT ''" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert service_type ")
                #end if
                if site_type_enable == False:
                    sql = "alter table `%s` add `site_type` varchar(255) DEFAULT ''" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert site_type ")
                #end if
                if database_type_enable == False:
                    sql = "alter table `%s` add `database_type` varchar(255) DEFAULT ''" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert database_type ")
                #end if
                if next_start_time_enable == False:
                    sql = "alter table `%s` add `next_start_time` timestamp NULL DEFAULT NULL" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert next_start_time ")
                #end if
                if cookie_url_enable == False:
                    sql = "alter table `%s` add `cookie_url` varchar(1024) DEFAULT ''" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert cookie_url ")
                #end if
                if begin_path_enable == False:
                    sql = "alter table `%s` add `begin_path` varchar(500) DEFAULT ''" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert begin_path ")
                #end if
                if exclude_url_enable == False:
                    sql = "alter table `%s` add `exclude_url` text" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                    logging.getLogger().debug("File:Update.py, alert exclude_url ")
                #end if
            #end if
        #end for
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_domain_list_table function:" + str(e))
    #end try
#end def

def update_scan_result_table():
    try:
        logging.getLogger().debug("update_scan_result_table")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select id from task_manage"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            task_id = str(row['id'])
            table_name = "scan_result_%s" % (task_id)
            if table_exists(table_name):
                output_enable = False
                sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = '%s'" % (table_name)
                cursor.execute(sql)
                res2 = cursor.fetchall()
                for row2 in res2:
                    if row2['COLUMN_NAME'] == 'output':
                        output_enable = True
                    #end if
                #end for
                if output_enable == False:
                    sql = "alter table `%s` add `output` mediumtext after `detail`" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                #end if
            #end if
        #end for
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_scan_result_table function:" + str(e))
    #end try
#end def

def update_weak_pwd_details_table():
    try:
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select id from task_manage"
        cursor.execute(sql)
        res = cursor.fetchall()
        port_enable = False
        proto_enable = False
        for row in res:
            task_id = str(row['id'])
            table_name = "weak_pwd_details_%s" % (task_id)
            if table_exists(table_name):
                output_enable = False
                sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = '%s'" % (table_name)
                cursor.execute(sql)
                res2 = cursor.fetchall()
                for row2 in res2:
                    if row2['COLUMN_NAME'] == 'port':
                        port_enable = True
                    if row2['COLUMN_NAME'] == 'proto':
                        proto_enable = True
                    #end if
                #end for
                if port_enable == False:
                    sql = "alter table `%s` add `port` varchar(256) after `asset_scan_id`" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                if proto_enable == False:
                    sql = "alter table `%s` add `proto` varchar(256) after `port`" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                #end if
            #end if
        #end for
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_weak_pwd_details_table function:" + str(e))
    #end try
#end def

def update_hostmsg_table():
    try:
        logging.getLogger().debug("update_hostmsg_table")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select id from task_manage"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            task_id = str(row['id'])
            table_name = "hostmsg_%s" % (task_id)
            if table_exists(table_name):
                host_progress_enable = False
                weak_progress_enable = False
                sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = '%s'" % (table_name)
                cursor.execute(sql)
                res2 = cursor.fetchall()
                for row2 in res2:
                    if row2['COLUMN_NAME'] == 'host_progress':
                        host_progress_enable = True
                    #end if
                    if row2['COLUMN_NAME'] == 'weak_progress':
                        weak_progress_enable = True
                #end for
                if host_progress_enable == False:
                    sql = "alter table `%s` add `host_progress` int(3) default '0'" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                #end if
                if weak_progress_enable == False:
                    sql = "alter table `%s` add `weak_progress` int(3) default '0'" % (table_name)
                    cursor.execute(sql)
                    conn.commit()
                #end if
            #end if
        #end for
        
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_hostmsg_table function:" + str(e))
    #end try
#end def


#Add by xiayuying 2013-09-10 for BUG #
def update_license_flag():
    try:
        #update the 5th flag in yx.config.inc.php
        php_fp = open('/var/www/yx.config.inc.php', 'rb')
        lines = php_fp.readlines()
        key_line = ''
        key_index = -1
        for line in lines:
            if 'feature_set' in line:
                key_line = line
                key_index = lines.index(line)
        value = key_line.split('=')[1].split(';')[0].strip()[1:-1]
        result = value[0:4] + '1' + value[5:]
        key_line = key_line.replace(value, result)
        lines[key_index] = key_line
        php_fp.close()
        php_fp = open('/var/www/yx.config.inc.php', 'w+')
        for line in lines:
            php_fp.write(line)
        php_fp.close()
        #update the 5th flag in /etc/waf_setting.rc
        import ConfigParser
        cf = ConfigParser.ConfigParser()
        cf.read('/etc/waf_setting.rc')
        orignal =cf.get('feature', 'feature_set')
        last = orignal[0:5] +'1' +orignal[6:]
        cf.set('feature', 'feature_set', last)
        cf.write(open("/etc/waf_setting.rc", "wb"))

    except Exception, e:
        logging.getLogger().error("File:Update.py, update_license_flag function:" + str(e))
        

def update_for_asset_to_task_manage():
    try:
        logging.getLogger().debug("update_for_asset_to_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        scan_id_exist = False
        as_id_exist = False
        am_id_exist = False
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'asset_scan_id':
                scan_id_exist = True
            elif row['COLUMN_NAME'] == 'as_id':
                as_id_exist = True
            elif row['COLUMN_NAME'] == 'am_id':
                am_id_exist = True
            #end if
        #end for
        
        if not scan_id_exist:
            sql = "alter table task_manage add `asset_scan_id` int(11) default '0'"
            cursor.execute(sql)
            conn.commit()
        #end if
        if not as_id_exist:
            sql = "alter table task_manage add `as_id` int(11) default '0'"
            cursor.execute(sql)
            conn.commit()
        #end if
        if not am_id_exist:
            sql = "alter table task_manage add `am_id` int(11) default '0'"
            cursor.execute(sql)
            conn.commit()
        #end if
        
        sql = "select id from task_manage"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            id = str(row['id'])
            
            list = []
            list.append("hostmsg_%s" % (id))
            list.append("port_list_%s" % (id))
            list.append("domain_list_%s" % (id))
            list.append("scan_result_%s" % (id))
            list.append("url_list_%s" % (id))
            list.append("vul_details_%s" % (id))
            list.append("weak_pwd_details_%s" % (id))
            
            for table in list:
                if table_exists(table):
                    flag = False
                    sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = '%s'" % (table)
                    cursor.execute(sql)
                    res2 = cursor.fetchall()
                    for row2 in res2:
                        if row2['COLUMN_NAME'] == 'asset_scan_id':
                            flag = True
                        #end if
                    #end if
                    
                    if flag == False:
                        sql = "alter table %s add `asset_scan_id` int(11) default 0" % (table)
                        cursor.execute(sql)
                        conn.commit()
                    #end if
                #end if
            #end for
        #end for
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_for_asset_to_task_manage function:" + str(e))
    #end try
#end def


def update_add_scan_uuid_to_task_manage():
    try:
        logging.getLogger().debug("update_scan_uuid_to_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        flag = False
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'scan_uuid':
                flag = True
            #end if
        #end for
        
        if flag == False:
            sql = "alter table task_manage add `scan_uuid` varchar(128) default ''"
            cursor.execute(sql)
            conn.commit()
        #end if
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_scan_uuid_to_task_manage function:" + str(e))
    #end try
#end def

def update_add_host_timeout_to_task_manage():
    try:
        logging.getLogger().debug("update_add_host_timeout_to_task_manage")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        flag = False
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'task_manage'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'host_timeout':
                flag = True
            #end if
        #end for
        
        if flag == False:
            sql = "alter table task_manage add `host_timeout` int(4) default '30'"
            cursor.execute(sql)
            conn.commit()
        #end if
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_host_timeout_to_task_manage function:" + str(e))
    #end try
#end def

def update_add_host_timeout_to_asset_scan():
    try:
        logging.getLogger().debug("update_add_host_timeout_to_asset_scan")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        flag = False
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'asset_scan'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'host_timeout':
                flag = True
            #end if
        #end for
        
        if flag == False:
            sql = "alter table asset_scan add `host_timeout` int(4) default '30'"
            cursor.execute(sql)
            conn.commit()
        #end if
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_host_timeout_to_asset_scan function:" + str(e))
    #end try
#end def

def update_cgidb_vul_id_index():
    try:
        logging.getLogger().debug("update_cgidb_vul_id_index")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        flag = False
        sql = "show index from cgidb"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['Column_name'] == 'vul_id':
                flag = True
            #end if
        #end for

        if flag == False:
            sql = "alter table `cgidb` add index vul_id(`vul_id`)"
            cursor.execute(sql)
            conn.commit()
        #end if

        cursor.close()
        conn.close()

    except Exception,e:
        logging.getLogger().error("File:Update.py, update_cgidb_vul_id_index function:" + str(e))
    #end try
#end def


def update_web_vul_list_vul_id_index():
    try:
        logging.getLogger().debug("update_web_vul_list_vul_id_index")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        flag = False
        sql = "show index from web_vul_list"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['Column_name'] == 'vul_id':
                flag = True
            #end if
        #end for

        if flag == False:
            sql = "alter table `web_vul_list` add index vul_id(`vul_id`)"
            cursor.execute(sql)
            conn.commit()
        #end if

        cursor.close()
        conn.close()

    except Exception,e:
        logging.getLogger().error("File:Update.py, update_web_vul_list_vul_id_index function:" + str(e))
    #end try
#end def


def check_nvscan_server_preference_table():
    try:
        logging.getLogger().debug("check_nvscan_server_preference_table")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select  GROUP_CONCAT(`COLUMN_NAME`) as `names` from `INFORMATION_SCHEMA`.`COLUMNS` where TABLE_SCHEMA = 'waf_hw' and TABLE_NAME = 'nvscan_server_preference'"
        cursor.execute(sql)
        res = cursor.fetchone()
        if res and res['names'] and res['names'] != "":
            flag = True
            
            sql = "select count(*) as c, policy_id from nvscan_server_preference where policy_id = '1' or policy_id = '2' group by policy_id"
            cursor.execute(sql)
            res = cursor.fetchall()
            for row in res:
                if row['c'] != 32:
                    flag = False
                #end if
            #end for
            
            if flag:
                cursor.close()
                conn.close()
                return
            #end if
        #end if
        
        logging.getLogger().debug("File:Update.py, check_nvscan_server_preference_table function: start rebuild nvscan_server_preference table")
        
        if os.path.isfile("/var/waf/nvscan_server_preference.sql"):
            cmd = "/usr/bin/mysql -u%s -p%s -h%s -e \"source /var/waf/nvscan_server_preference.sql\"" % (user,passwd,host)
            vulscan_popen(cmd)
            
            sql = "update host_policy set nvscan_policy_id = '-1' where id = '1' or id = '2'"
            cursor.execute(sql)
            conn.commit()
        else:
            logging.getLogger().error("File:Update.py, check_nvscan_server_preference_table function: /var/waf/nvscan_server_preference.sql not exist")
        #end if
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, check_nvscan_server_preference_table function:" + str(e))
    #end try
#end def

def check_nvscan_plugin_preference_table():
    try:
        logging.getLogger().debug("check_nvscan_plugin_preference_table")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select  GROUP_CONCAT(`COLUMN_NAME`) as `names` from `INFORMATION_SCHEMA`.`COLUMNS` where TABLE_SCHEMA = 'waf_hw' and TABLE_NAME = 'nvscan_plugin_preference'"
        cursor.execute(sql)
        res = cursor.fetchone()
        if res and res['names'] and res['names'] != "":
            flag = True
            
            sql = "select count(*) as c, policy_id from nvscan_plugin_preference where policy_id = '1' or policy_id = '2' group by policy_id"
            cursor.execute(sql)
            res = cursor.fetchall()
            for row in res:
                if row['c'] != 243:
                    flag = False
                #end if
            #end for
            
            '''
            if flag:
                cursor.close()
                conn.close()
                # return
            #end if
            '''
        #end if
        
        logging.getLogger().debug("File:Update.py, check_nvscan_server_preference_table function: start rebuild nvscan_plugin_preference table")
        
        if os.path.isfile("/var/waf/nvscan_plugin_preference.sql"):
            cmd = "/usr/bin/mysql -u%s -p%s -h%s -e \"source /var/waf/nvscan_plugin_preference.sql\"" % (user,passwd,host)
            vulscan_popen(cmd)
            
            sql = "update host_policy set nvscan_policy_id = '-1' where id = '1' or id = '2'"
            cursor.execute(sql)
            conn.commit()
        else:
            logging.getLogger().error("File:Update.py, check_nvscan_plugin_preference_table function: /var/waf/nvscan_plugin_preference.sql not exist")
        #end if

        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, check_nvscan_plugin_preference_table function:" + str(e))
    #end try
#end def

def update_nvscan_preference(policy_id):
    try:
        logging.getLogger().debug("update_nvscan_preference")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        server_count = 0
        plugin_count = 0
        
        sql = "select count(*) as c from nvscan_server_preference where policy_id = '1'"
        cursor.execute(sql)
        res = cursor.fetchone()
        server_count = res['c']
        sql = "select count(*) as c from nvscan_plugin_preference where policy_id = '1'"
        cursor.execute(sql)
        res = cursor.fetchone()
        plugin_count = res['c']
        
        flag = False
        
        sql = "select count(*) as c from nvscan_server_preference where policy_id = '%s'" % (str(policy_id))
        cursor.execute(sql)
        res = cursor.fetchone()
        if res and res['c'] != server_count:
            logging.getLogger().debug("File:Update.py, update_nvscan_preference function: update nvscan_server_preference, policy_id:%s" % (str(policy_id)))
            
            flag = True
            
            sql = "delete from nvscan_server_preference where policy_id = '%s'" % (str(policy_id))
            cursor.execute(sql)
            conn.commit()
            
            sql = ""
            cursor.execute("select * from nvscan_server_preference where policy_id = '1'")
            res = cursor.fetchall()
            for row in res:
                sql += "('%s','%s','%s')," % (str(policy_id),row['name'],row['value'])
            #end for
            sql = sql[0:-1]
            sql = "insert into nvscan_server_preference (`policy_id`, `name`, `value`) values %s" % sql
            cursor.execute(sql)
            conn.commit()
        #end if
        
        sql = "select count(*) as c from nvscan_plugin_preference where policy_id = '%s'" % (str(policy_id))
        cursor.execute(sql)
        res = cursor.fetchone()
        if res and res['c'] != plugin_count:
            logging.getLogger().debug("File:Update.py, update_nvscan_preference function: update nvscan_plugin_preference, policy_id:%s" % (str(policy_id)))
            
            flag = True
            
            sql = "delete from nvscan_plugin_preference where policy_id = '%s'" % (str(policy_id))
            cursor.execute(sql)
            conn.commit()
            
            sql = ""
            cursor.execute("select * from nvscan_plugin_preference where policy_id = '1'")
            res = cursor.fetchall()
            for row in res:
                sql += "('%s','%s','%s','%s','%s','%s','%s','%s')," % (str(policy_id),row['pluginName'],row['pluginId'],row['fullName'],row['preferenceName'],row['preferenceType'],row['preferenceValues'],row['selectedValue'])
            #end for
            sql = sql[0:-1]
            sql = "insert into nvscan_plugin_preference (`policy_id`, `pluginName`, `pluginId`, `fullName`, `preferenceName`, `preferenceType`, `preferenceValues`, `selectedValue`) values %s" % sql
            cursor.execute(sql)
            conn.commit()
        #end if   
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_nvscan_preference function:" + str(e))
    #end try
#end def

def update_host_policy_table():
    try:
        logging.getLogger().debug("update_host_policy_table")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        nvscan_policy_id_flag = True
        enable_ddos_flag = True
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'host_policy'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'nvscan_policy_id':
                nvscan_policy_id_flag = False
            #end if
            
            if row['COLUMN_NAME'] == 'enable_ddos':
                enable_ddos_flag = False
            #end if
        #end for
        
        if enable_ddos_flag:
            sql = "alter table host_policy add `enable_ddos` int(1) default '1'"
            cursor.execute(sql)
            conn.commit()
        #end if
        
        if nvscan_policy_id_flag:
            sql = "alter table host_policy add `nvscan_policy_id` int(11) default '-1'"
            cursor.execute(sql)
            conn.commit()
        #end if
        
        check_nvscan_server_preference_table()
        check_nvscan_plugin_preference_table()
        
        sql = "select id from host_policy where id > 2"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            update_nvscan_preference(row['id'])
        #end for
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_host_policy_table function:" + str(e))
    #end try
#end def

def update_nvscan_policy():
    try:
        logging.getLogger().debug("update_host_policy_table")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select * from host_policy"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['nvscan_policy_id'] and row['nvscan_policy_id'] > 0:
                cmd = "python /var/waf/nvscan_policy_manager.py update %s#" % (str(row['id']))
            else:
                cmd = "python /var/waf/nvscan_policy_manager.py add %s#" % (str(row['id']))
            #end if
            logging.getLogger().debug("File:Update.py, update_nvscan_policy function: %s" % (cmd))
            vulscan_popen(cmd)
        #end for
        
        cursor.close()
        conn.close()
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_nvscan_policy function:" + str(e))
    #end try
#end def

def update_nvscan_user():
    try:
        c = '/opt/nvscan/sbin/nvscan-adduser'
        USER_NAME = 'admin'
        USER_PWD  = 'admin' 
        child = pexpect.spawn(c)
        fout = file('/opt/nvscan/var/nvscan/logs/adduser.log', 'a+')
        child.logfile=fout
        index = child.expect(['Login :', pexpect.EOF, pexpect.TIMEOUT])
        if index == 0:
            child.sendline(USER_NAME)
            index = child.expect(['Login password :', 'already exists', pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                child.sendline(USER_PWD)
                index = child.expect(['Login password (again)', pexpect.EOF, pexpect.TIMEOUT])
                child.sendline(USER_PWD)
                index = child.expect(['can upload plugins', pexpect.EOF, pexpect.TIMEOUT])
                child.sendline('y')
                index = child.expect(['BLANK LINE once', pexpect.EOF, pexpect.TIMEOUT])
                child.sendline()
                index = child.expect(['Is that ok ?', pexpect.EOF, pexpect.TIMEOUT])
                child.sendline('y')
                index = child.expect(['User added', pexpect.EOF, pexpect.TIMEOUT])
                if index == 0:
                    logging.getLogger().info('File:Update.py, update_nvscan_user function: add nvscan user success!')
                else:
                    logging.getLogger().error('File:Update.py, update_nvscan_user function: add nvscan user error pls check log for details')
            elif index == 1:
                logging.getLogger().info('File:Update.py, update_nvscan_user function: user %s is exists'% (USER_NAME))
            else:
                print 6
        else:
            logging.getLogger().error('File:Update.py, update_nvscan_user function: add nvscan user error pls check log for details')
    except Exception, e:
        logging.getLogger().error("File:Update.py, update_nvscan_user function:" + str(e))

def update_add_ipv6info_to_net_config():
    try:
        logging.getLogger().debug("update_add_ipv6info_to_net_config")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        Ipv6_flag = False
#       Netmaskv6_flag = False
#       NextHopv6_flag = False
#       Gatewayv6_flag = False
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'net_config'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'Ipv6':
                Ipv6_flag = True
#           elif row['COLUMN_NAME'] == 'Netmaskv6':
#           	Netmaskv6_flag = True
#           elif row['COLUMN_NAME'] == 'NextHopv6':
#           	NextHopv6_flag = True;
#           elif row['COLUMN_NAME'] == 'Gatewayv6':
#           	Gatewayv6_flag = True
            #end if
        #end for
        
        if Ipv6_flag == False:
            sql = "alter table net_config add `Ipv6` varchar(45)  default NULL"
            cursor.execute(sql)
            sql = "alter table net_config add `Netmaskv6` varchar(45)  default NULL"
            cursor.execute(sql)
            sql = "alter table net_config add `NextHopv6` varchar(45)  default NULL"
            cursor.execute(sql)
            sql = "alter table net_config add `Gatewayv6` varchar(45)  default NULL"
            cursor.execute(sql)
            conn.commit()
        #end if
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_ipv6info_to_net_config function:" + str(e))
    #end try
#end def

def update_add_ipv6_to_user_route():
    try:
        logging.getLogger().debug("update_add_ipv6_to_user_route")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        Ipv6_flag = False
        sql = "select `COLUMN_NAME` from information_schema.COLUMNS  where TABLE_NAME = 'user_route'"
        cursor.execute(sql)
        res = cursor.fetchall()
        for row in res:
            if row['COLUMN_NAME'] == 'Destv6':
                Ipv6_flag = True
            #end if
        #end for
        
        if Ipv6_flag == False:
            sql = "alter table user_route add `Destv6` varchar(45) default NULL"
            cursor.execute(sql)
            sql = "alter table user_route add `Netmaskv6` varchar(45) default NULL"
            cursor.execute(sql)
            sql = "alter table user_route add `Gatewayv6` varchar(45) default NULL"
            cursor.execute(sql)
            conn.commit()
        #end if
        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, update_add_ipv6_to_user_route function:" + str(e))
    #end try
#end def


def mofify_api_auth_ip_type():
    try:
        logging.getLogger().debug("mofify_api_auth_ip_type")
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "alter table api_auth modify `ip` char(80) default NULL"
        cursor.execute(sql)

        
        cursor.close()
        conn.close()
        
    except Exception,e:
        logging.getLogger().error("File:Update.py, mofify_api_auth_ip_type function:" + str(e))
    #end try
#end def



if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        if update_old_task_manage():
            update_add_email_to_task_manage()
            update_add_enable_ddos_to_task_manage()
            update_add_web_exp_try_to_task_manage()
            update_add_web_speed_to_task_manage()
            update_add_spider_flag_to_task_manage()
            update_for_asset_to_task_manage()
            update_add_scan_uuid_to_task_manage()
            update_add_host_timeout_to_task_manage()
            update_add_vpn_to_task_manage()
        #end if
        update_add_nvs_interface_to_net_config()
        update_add_Maxtasks_to_user()
        update_add_Iprange_to_user()
        update_reportlist()
        update_size_reportlist()
        update_cnvd_vul_details()
        update_domain_list_table()
        update_scan_result_table()
        update_weak_pwd_details_table()
        update_license_flag()
        update_cgidb_vul_id_index()
        update_web_vul_list_vul_id_index()
        #add for xmlrpc
        update_nvscan_user()
        update_host_policy_table()
        
        update_hostmsg_table()
        update_add_host_timeout_to_asset_scan()

        update_add_ipv6info_to_net_config()
        update_add_ipv6_to_user_route()
        mofify_api_auth_ip_type()

        restartTask()
        update_nvscan_policy()
        restartTask()
    except Exception,e:
        logging.getLogger().error("File:Update.py, __main__:" + str(e))
    #end try
#end if

