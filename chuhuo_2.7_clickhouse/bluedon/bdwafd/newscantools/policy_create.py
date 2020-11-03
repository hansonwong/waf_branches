#coding: utf-8
import os
import sys
import re
import MySQLdb
import ConfigParser

WAF_CONFIG   = "/var/waf/waf.conf"

cfg    = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
host   = cfg.get("mysql","db_ip").replace('"','')
user   = cfg.get("mysql","db_user").replace('"','')
passwd = cfg.get("mysql","db_passwd").replace('"','')

def rebuild_policy_manage_table():
    sql = """CREATE TABLE `policy_manage` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) default NULL,
  `name` varchar(255) default NULL,
  `vuls` mediumtext,
  `type` int(1) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"""
    
    try:
	conn = MySQLdb.connect(host, user, passwd, db = 'waf_hw', charset = 'utf8')
    
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
	cur.execute("drop table `policy_manage`")
	conn.commit()
	
    except Exception,e:
	pass
    #end try
    
    try:
	conn = MySQLdb.connect(host, user, passwd, db = 'waf_hw', charset = 'utf8')
    
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
	
	cur.execute(sql)
	conn.commit()
    except Exception,e:
	print e
    #end try
#end def

def create_policy():
    try:
	conn = MySQLdb.connect(host, user, passwd, db = 'waf_hw', charset = 'utf8')
    
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
	
	#
	sql = "select distinct vul_id from vul_info where enable = 1 and chs = 1"
	#print 1
        cur.execute(sql)
        ree = cur.fetchall()
        #print 2
        tmp = ""
	for vul_id in ree:
	    tmp = tmp + str(vul_id["vul_id"]) + "|" 
	#end for

	sql = "insert into policy_manage values (0, 2, '%s', '%s', 0)" % ("全部漏洞", tmp)
        cur.execute(sql)
        conn.commit()



	#
	sql = "select distinct vul_id from vul_info where enable = 1 and chs = 1 and (risk_factor = 'H' or risk_factor = 'C')"
        cur.execute(sql)
        ree = cur.fetchall()
        
        tmp = ""
        for vul_id in ree:
            tmp = tmp + str(vul_id["vul_id"]) + "|"
	#end for

        sql = "insert into policy_manage values (0, 2, '%s', '%s', 0)" % ("全部高危漏洞", tmp)
        cur.execute(sql)
        conn.commit()
		
		
	#

        familys = []
        
        sql = "select distinct family ,count(*) from vul_info where enable = 1 and chs = 1 group by family"
        cur.execute(sql)
        ree = cur.fetchall()
	for f in ree:

            sql = "select distinct vul_id from vul_info where enable = 1 and chs = 1 and family = '%s'" % f["family"]
	    #print sql
            cur.execute(sql)
            ree = cur.fetchall()
            
            tmp = ""
            for vul_id in ree:
                tmp = tmp + str(vul_id["vul_id"]) + "|"
            #end for

            sql = "insert into policy_manage values (0, 2, '%s', '%s', 0)" % (f["family"], tmp)
            #sql = "update policy_manage set vuls = '%s'" % tmp

            cur.execute(sql)
            conn.commit()
	#end for
        conn.close()
     
    except Exception,e:
    
        print e
    #end try
#end def

def update_policy():
    try:
	conn = MySQLdb.connect(host, user, passwd, db = 'waf_hw', charset = 'utf8')
    
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "show tables like 'policy_manage'"
        cur.execute(sql)
        ree = cur.fetchall()
        if ree and len(ree) > 0:
            print "policy_manage exists"
        else:
            rebuild_policy_manage_table()
            create_policy()
        #end if
	
	#
	sql = "select distinct vul_id from vul_info where enable = 1 and chs = 1"
	#print 1
        cur.execute(sql)
        ree = cur.fetchall()
        #print 2
        tmp = ""
	for vul_id in ree:
	    tmp = tmp + str(vul_id["vul_id"]) + "|" 
	#end for

	sql = "update policy_manage set `vuls` = '%s' where name = '%s'" % (tmp, "全部漏洞")
        cur.execute(sql)
        conn.commit()



	#
	sql = "select distinct vul_id from vul_info where enable = 1 and chs = 1 and (risk_factor = 'H' or risk_factor = 'C')"
        cur.execute(sql)
        ree = cur.fetchall()
        
        tmp = ""
        for vul_id in ree:
            tmp = tmp + str(vul_id["vul_id"]) + "|"
	#end for

	sql = "update policy_manage set `vuls` = '%s' where name = '%s'" % (tmp, "全部高危漏洞")
        cur.execute(sql)
        conn.commit()
		
		
	#

        familys = []
        
        sql = "select distinct family ,count(*) from vul_info where enable = 1 and chs = 1 group by family"
        cur.execute(sql)
        ree = cur.fetchall()
	for f in ree:

            sql = "select distinct vul_id from vul_info where enable = 1 and chs = 1 and family = '%s'" % f["family"]
	    #print sql
            cur.execute(sql)
            ree = cur.fetchall()
            
            tmp = ""
            for vul_id in ree:
                tmp = tmp + str(vul_id["vul_id"]) + "|"
            #end for
	    
	    sql = "update policy_manage set `vuls` = '%s' where name = '%s'" % (tmp, f["family"])
            #sql = "update policy_manage set vuls = '%s'" % tmp

            cur.execute(sql)
            conn.commit()
	#end for
        conn.close()
     
    except Exception,e:
    
        print e
    #end try
#end def
if __name__ == '__main__':
    
    if len(sys.argv) != 2:
	print "policy_create.py install; or"
	print "policy_create.py update; "
	
	sys.exit(0)
    #end if
    
    if sys.argv[1] == "install":
	rebuild_policy_manage_table()
	create_policy()
    elif sys.argv[1] == "update":
	update_policy()
    else:
	print "policy_create.py install; or"
	print "policy_create.py update; "
	
	sys.exit(0)
    #end if
#end if
    
    