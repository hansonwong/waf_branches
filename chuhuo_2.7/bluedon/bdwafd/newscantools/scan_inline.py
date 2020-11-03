#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import MySQLdb
import sys
import socket
import time
import urllib
import os
import struct

host = "192.168.9.45"
user = "root"
passwd = "yxserver"
dbname = "snort"

index_file = "/var/waf/.index_file"


def get_last_index(end_id):
    try:
    
        if os.path.isfile(index_file):
            f = open(index_file, "r")
            data = f.read()
            f.close()
            
            last_index = int(data)
            
            return last_index
        else:
            f = open(index_file, "w")
            f.write(str(end_id))
            f.close()
            
            return end_id
        #end if
    except Exception,e:
        f = open(index_file, "w")
        f.write(str(end_id))
        f.close()
        
        return end_id
    #end try
    
#end def

def update_index(now_index):
    
    f = open(index_file, "w")
    f.write(str(now_index))
    f.close()
 
#end def


def start_scan(scan_host, target):
    task_name = "%s_%d" % (target, int(time.time()))
    params = urllib.urlencode({'action':'create', 'task_name':task_name, 'target':target, 'en_host':1})  
    sock = urllib.urlopen("https://%s/vulscan.php" % scan_host , params)  
    html = sock.read()
    sock.close()
#end def



def check_alert():
    
    #dict: vul-ip
    scan_inline_config = {}
    
    try:
        conn = MySQLdb.connect(host, user, passwd, db=dbname, charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select * from scan_inline"
        cur.execute(sql)
        ret = cur.fetchall()
        
        if ret and len(ret) > 0:
            for c in ret:
                ip = c["ip"]
                vuls = c["vul_list"]
                
                if len(vuls) > 0:
                    vuls = vuls.split(",")
                    if len(vuls) > 0:
                        for vul in vuls:
                            scan_inline_config.setdefault(int(vul), ip)
                        #end  for
                    #end if
                #end if
            #end for
        #end if
        
        print scan_inline_config
  
        sql = "select id from acid_event group by id desc limit 1"
        cur.execute(sql)
        ret = cur.fetchone()
        
        end_id   = int(ret["id"])
        start_id = get_last_index(end_id)
        print start_id,
        print end_id
        

        update_index(end_id)
        
        if end_id == start_id:
            return
        #end if
        
        sql = "select `signature`, `ip_dst` from acid_event where id > %d and id <= %d" % (start_id, end_id)
        cur.execute(sql)
        ret = cur.fetchall()
        
        print ret
        
        if ret and len(ret) > 0:
            for  row in ret:
                tmpip = scan_inline_config.get(int(row["signature"])) 
                if tmpip:
                    
                    sql = "select * from scaned_ip_list where ip = '%s'" % socket.inet_ntoa(struct.pack("!I", int(row["ip_dst"])))
                    cur.execute(sql)
                    scaned_ip = cur.fetchone()
                    
                    if scaned_ip:
                        if int(time.time()) - int(scaned_ip["last_scaned_time"]) < 180:
                            continue
                        #end if
                    else:
                        sql = "insert into scaned_ip_list values(0, '%s', 0)" % (socket.inet_ntoa(struct.pack("!I", int(row["ip_dst"]))))
                        cur.execute(sql)
                        conn.commit()
                    #end if
                    
                    sql = "update scaned_ip_list set last_scaned_time = %d where ip = '%s'" % (int(time.time()), socket.inet_ntoa(struct.pack("!I", int(row["ip_dst"]))))
                    cur.execute(sql)
                    conn.commit()
                    
                    if tmpip != socket.inet_ntoa(struct.pack("!I", int(row["ip_dst"]))):
                        start_scan(tmpip, socket.inet_ntoa(struct.pack("!I", int(row["ip_dst"]))))
                    #end if

                #end if
            #end for
        #end if
        
    except Exception,e:
        print e
    #end try
        
        
#end def



if __name__ == "__main__":
    while True:
        check_alert()
        
        time.sleep(5)
    #end while
#end