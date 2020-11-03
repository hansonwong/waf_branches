#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys
import os



from lib.waf_netutil import *

TRANSFER_TABLE = "/var/waf/.flag_to_transfer_left_alert_tables"


STAT_ALERT_SQL       = "select `BlockReason` as ruleid,count(*) as num from `%s` group by `BlockReason` order by num desc limit %d"
STAT_ALERT_GROUP_SQL = "select count(*) as ct, gp as name from (select %s.HackId  as id,yx_rules_ref.`Group` as gp  from %s LEFT JOIN yx_rules_ref on yx_rules_ref.Rid = %s.BlockReason) as b group by gp order by ct desc limit %d"


STAT_ALERT_TABLE       = "stat_alert"
STAT_ALERT_GROUP_TABLE = "stat_alert_group"
STAT_ALERT_DAY_TABLE   = "stat_alert_day"

def table_exists(tablename):
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        #conn = MySQLdb.connect("192.168.9.33","root","yxserver",db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select count(*) as c from information_schema.tables  where table_name = '%s' and TABLE_SCHEMA = '%s'" % (tablename, "waf_hw")
        cur.execute(sql)
        re = cur.fetchone()
        
        if int(re["c"]) == 1:
            return True
        else:
            return False
        #end if
        
    except Exception,e:
        logging.getLogger().debug("table_exists Exception:" + str(e))
        
        return False
    #end try
#end def

def count_table(tablename):
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        #conn = MySQLdb.connect("192.168.9.33","root","yxserver",db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select count(*) as c from %s" % tablename
        cur.execute(sql)
        re = cur.fetchone()
        
        return int(re["c"])
        
    except Exception,e:
        logging.getLogger().debug("count_table Exception:" + str(e))
        
        return 0
    #end try
#end def
    
    
def get_rule_name(rid):
    
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select Name from yx_rules_ref where Rid = %d" % int(rid)
        cur.execute(sql)
        re = cur.fetchall()
        
        if len(re) != 1:
            return u"自定义规则"
        else:
            return re[0]["Name"]
        #end if
    except Exception,e:
        logging.getLogger().debug("get_rule_name Exception:" + str(e))
        
        return ""
    #end try
#end def
        
    
    

def update_alert_stat():
    
    global STAT_ALERT_GROUP_SQL
    
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        curr_alert_tablename = "alert_" + time.strftime("%Y%m%d")
        
        sql = "delete from %s" % STAT_ALERT_TABLE
        cur.execute(sql)
        
        if table_exists(curr_alert_tablename) == False or count_table(curr_alert_tablename) < 1:
            sql = "insert into %s values (0, '0', 0)" % STAT_ALERT_TABLE
            
            for i in range(8):
                cur.execute(sql)
            #end for
            
            return
            
        #end if
    
        sql = STAT_ALERT_SQL % (curr_alert_tablename, 20)
        cur.execute(sql)
        
        re = cur.fetchall()
        
        max_num = 8
        
        for i in re:
            max_num = max_num - 1
            
            if max_num < 0:
                break
            #end if
            
            tmpname = (get_rule_name((i["ruleid"])))
            
            sql = "insert into %s values (%d, '%s', %d)" % (STAT_ALERT_TABLE, int(i["ruleid"]), tmpname, int(i["num"]))
            cur.execute(sql)
        #end for      
        
        conn.close()
 
    except Exception,e:
        logging.getLogger().debug("update_alert_stat Exception:" + str(e))
        return -1
#end def

def update_alert_group_stat():
    
    global STAT_ALERT_GROUP_SQL
    global STAT_ALERT_GROUP_TABLE
    
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        curr_alert_tablename = "alert_" + time.strftime("%Y%m%d")
        
        sql = "delete from %s" % STAT_ALERT_GROUP_TABLE
        cur.execute(sql)
        
        if table_exists(curr_alert_tablename) == False or count_table(curr_alert_tablename) < 1:
            sql = "insert into %s values ('0', 0)" % STAT_ALERT_GROUP_TABLE
            
            for i in range(8):
                cur.execute(sql)
            #end for
            
            return
            
        #end if
    
        sql = STAT_ALERT_GROUP_SQL % (curr_alert_tablename, curr_alert_tablename, curr_alert_tablename, 20)

        cur.execute(sql)
        
        re = cur.fetchall()
        
        sql = "delete from %s" % STAT_ALERT_GROUP_TABLE
        cur.execute(sql)
        
        
        max_num = 8
        
        for i in re:
            
            max_num = max_num - 1
            
            if max_num < 0:
                break
            #end if
  
            if not i["name"]:
                i["name"] = u"自定义规则"
            sql = "insert into %s values ('%s', %d)" % (STAT_ALERT_GROUP_TABLE, i["name"], int(i["ct"]))
            cur.execute(sql)
        #end for      
        
        conn.close()
 
    except Exception,e:
        logging.getLogger().debug("update_alert_group_stat Exception:" + str(e))
        return -1
#end def

def update_alert_day_stat():
    
    global STAT_ALERT_DAY_TABLE
    
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        #conn = MySQLdb.connect("192.168.9.33","root","yxserver",db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        curr_alert_tablename = "alert_" + time.strftime("%Y%m%d")
        
        if table_exists(curr_alert_tablename) == False or count_table(curr_alert_tablename) < 1:
            for i in range(24):


                sql = "update %s set `Count` = 0 where `Hour` = %d" % (STAT_ALERT_DAY_TABLE, i)
    
                cur.execute(sql)

            #end for   
            
            return
        #end if
    
        sql = "select `HackTime` from %s" % curr_alert_tablename

        cur.execute(sql)
        
        re = cur.fetchall()
        
        hour_count = []
        for i in range(24):
            hour_count.append(0)
        #end for
        
        for i in re:
            hour = int(i["HackTime"].split(" ")[1].split(":")[0])
            hour_count[hour] = hour_count[hour] + 1
        
        hour = 0
            
        for i in hour_count:


            sql = "update %s set `Count` = %d where `Hour` = %d" % (STAT_ALERT_DAY_TABLE, int(i), hour)

            cur.execute(sql)
            
            hour = hour + 1
        #end for      
        
        conn.close()
 
    except Exception,e:
        logging.getLogger().debug("update_alert_day_stat Exception:" + str(e))
        return -1
#end def

if __name__ == "__main__":
    
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")    
    
    while True:
        
        update_alert_stat()
        update_alert_group_stat()    
        update_alert_day_stat()
        
        time.sleep(60)
    #end while

#end if
    