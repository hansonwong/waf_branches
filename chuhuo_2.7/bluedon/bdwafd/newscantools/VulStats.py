#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import sys
import datetime
import os
import Mail
from lib.common import *

class VulStats:
    def __init__(self):
        try:
            self.conn = ""
            self.cursor = ""
        except Exception,e:
            logging.getLogger().error("init CountVul Exception(VulStats):" + str(e))
        #end try
    #end def
    
    def mysqlConnect(self):
        try:
            self.conn = MySQLdb.connect(host, user, passwd , db = "waf_hw", charset = "utf8")
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        except Exception,e:
            logging.getLogger().error("mysql connect Exception(VulStats):" + str(e))
        #end try            
    #end def
    
    def mysqlClose(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception,e:
            logging.getLogger().error("mysql close Exception(VulStats):" + str(e))
        #end try          
    #end def
    
    def updateVulTypeStats(self):
        try:
            self.mysqlConnect()
            
            if table_exists('vul_stats'):
                self.cursor.execute("truncate table vul_stats")
                self.conn.commit()
            #end if
            
            self.cursor.execute("select `id`,`user_id`,`asset_scan_id` from `task_manage`")
            ret = self.cursor.fetchall()
            if ret and len(ret) > 0:
                for row in ret:
                    task_id = row['id']
                    user_id = row['user_id']
                    asset_scan_id = row['asset_scan_id']
                
                    vul_details_table = 'vul_details_' + str(task_id)
                    scan_result_table = 'scan_result_' + str(task_id)
                    weak_pwd_details_table = 'weak_pwd_details_' + str(task_id)
                
                    #count host_vul
                    if table_exists(vul_details_table) and table_exists(scan_result_table) and table_exists(weak_pwd_details_table):
                        sql = "select count(*) as c, family, risk_factor as level from %s group by concat(family,risk_factor) union all " % (vul_details_table)
                        sql += " select count(*) as c, vul_type as family, substring(level,1,1) as level from %s group by concat(vul_type,level) union all " % (scan_result_table)
                        sql += " select count(*) as c, type as family, 'H' as level from %s group by type" % (weak_pwd_details_table)      
                        if asset_scan_id > 0:
                            sql = "select count(*) as c, family, risk_factor as level from %s where asset_scan_id = '%d' group by concat(family,risk_factor) union all " % (vul_details_table,asset_scan_id)
                            sql += " select count(*) as c, vul_type as family, substring(level,1,1) as level from %s where asset_scan_id = '%d' group by concat(vul_type,level) union all " % (scan_result_table,asset_scan_id)
                            sql += " select count(*) as c, type as family, 'H' as level from %s where asset_scan_id = '%d' group by type" % (weak_pwd_details_table,asset_scan_id)
                        #end if
                        
                        self.cursor.execute(sql)
                        result = self.cursor.fetchall()
                        for item in result:
                            count = item['c']
                            family = item['family']
                            level = item['level']
                            
                            sql = "select count(id) as c from vul_stats where vul_name = %s and user_id = %s"
                            self.cursor.execute(sql,(family,str(user_id)))
                            query = self.cursor.fetchone()
                            if query and len(query) > 0 and query['c'] > 0:
                                sql = "update vul_stats set "+level.lower()+" = "+level.lower()+" + "+str(count)+" where vul_name = %s and user_id = %s"
                                self.cursor.execute(sql,(family,str(user_id)))
                                self.conn.commit()
                            else:
                                c = 0
                                h = 0
                                m = 0
                                l = 0
                                i = 0
                                if level == 'C':
                                    c = count
                                elif level == 'H':
                                    h = count
                                elif level == 'M':
                                    m = count
                                elif level == 'L':
                                    l = count
                                elif level == 'I':
                                    i = count
                                #end if
                                sql = "insert into vul_stats(vul_name,c,h,m,l,i,user_id)values(%s,%s,%s,%s,%s,%s,%s)"
                                self.cursor.execute(sql,(family,str(c),str(h),str(m),str(l),str(i),str(user_id)))
                                self.conn.commit()
                            #end if
                        #end for
                    #end if
                #end for
            #end if
            self.mysqlClose()
        except Exception,e:
            logging.getLogger().error("updateVulTypeStats Exception(VulStats):" + str(e))
        #end try 
    #end def
    
    def updateVulTaskStats(self):
        try:
            self.mysqlConnect()
            self.cursor.execute("select `id`,`asset_scan_id` from `task_manage`")
            ret = self.cursor.fetchall()
            if ret and len(ret) > 0:
                for row in ret:
                    task_id = row['id']
                    asset_scan_id = row['asset_scan_id']
       
                    vul_details_table = 'vul_details_' + str(task_id)
                    scan_result_table = 'scan_result_' + str(task_id)
                    weak_pwd_details_table = 'weak_pwd_details_' + str(task_id)
                    
                    c = 0
                    h = 0
                    m = 0
                    l = 0
                    i = 0
                    
                    if table_exists(vul_details_table) and table_exists(scan_result_table) and table_exists(weak_pwd_details_table):
                        sql = "select sum(c) as c,a.level as level from ("
                        sql += " select count(*) as c,v.risk_factor as `level` from "+vul_details_table+" v group by v.risk_factor union all "
                        sql += " select count(*) as c,substring(s.level,1,1) as `level` from "+scan_result_table+" s group by s.level union all "
                        sql += " select count(*) as c,'H' as `level` from "+weak_pwd_details_table+" "
                        sql += " ) a group by a.level "
                        if asset_scan_id > 0:
                            sql = "select sum(c) as c,a.level as level from ("
                            sql += " select count(*) as c,v.risk_factor as `level` from %s v where v.asset_scan_id = '%d' group by v.risk_factor union all " % (vul_details_table,asset_scan_id)
                            sql += " select count(*) as c,substring(s.level,1,1) as `level` from %s s where s.asset_scan_id = '%d' group by s.level union all " % (scan_result_table,asset_scan_id)
                            sql += " select count(*) as c,'H' as `level` from %s where asset_scan_id = '%d' " % (weak_pwd_details_table,asset_scan_id)
                            sql += " ) a group by a.level "
                        #end if
                        
                        self.cursor.execute(sql)
                        result = self.cursor.fetchall()
                        if result and len(result) > 0:
                            for item in result:
                                count = item['c']
                                level = item['level']
                                if level == 'C':
                                    c = count
                                elif level == 'H':
                                    h = count
                                elif level == 'M':
                                    m = count
                                elif level == 'L':
                                    l = count
                                elif level == 'I':
                                    i = count
                                #end if
                            #end for
                        #end if
                        sql = "update task_manage set c = '%s', h = '%s', m = '%s', l = '%s', i = '%s' where id = '%s'" % (str(c),str(h),str(m),str(l),str(i),str(task_id))
                        self.cursor.execute(sql)
                        self.conn.commit()
                    #end if
                #end for
            #end if
            self.mysqlClose()
        except Exception,e:
            logging.getLogger().error("updateVulTaskStats Exception(updateVulTaskStats):" + str(e))
        #end try
    #end def

    def main(self):
        try:
            self.updateVulTypeStats()
            self.updateVulTaskStats()
        except Exception,e:
            logging.getLogger().error("main Exception(VulStats):" + str(e))
        #end try
    #end def
#end class

if __name__ == "__main__":
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        vulstats = VulStats()
        vulstats.main()
    except Exception,e:
        logging.getLogger().error("__main__ Exception(VulStats):" + str(e))
    #end try
#end if
    
    
    
    
    