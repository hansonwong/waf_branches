#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import zipfile 
from M2Crypto.EVP import Cipher  
from M2Crypto import m2  
from lib.waf_netutil import *
import logging
import ConfigParser
import MySQLdb
import signal
import time
from CheckInstance import sendUpgradeState
import subprocess
 
iv      = "eacpqkdckzefjalceacpqkdckzefjalc" 
passKey = "vbglodckidapckcavbglodckidapckca" 

upload_file = "/tmp/rules.dat"
output_zip  = "/var/rules.zip"
rules_dir   = "/var/rules_dir/"
repo_dir    = "/var/vuls_db/"

WAF_CONFIG   = "/var/waf/waf.conf"

cfg    = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
host   = cfg.get("mysql","db_ip").replace('"','')
user   = cfg.get("mysql","db_user").replace('"','')
passwd = cfg.get("mysql","db_passwd").replace('"','')
 
def encrypt(buf):  
    #ecb 模式不受iv影响  
    cipher = Cipher(alg="aes_256_cbc", key=passKey, iv=iv, op=1) # 1 is encrypt  
    # padding 有时设置为1  
    #cipher.set_padding(padding=m2.no_padding)  
    v = cipher.update(buf)  
    v = v + cipher.final()  
    del cipher 
 
    out = ""  
    for i in v:  
        out += "%02X" % (ord(i))  
    #print out  
 
    return v  
 
def decrypt(buf):  
    cipher = Cipher(alg="aes_256_cbc", key=passKey, iv=iv, op=0) # 0 is decrypt  
    #cipher.set_padding(padding=m2.no_padding)  
    v = cipher.update(buf)  
    v = v + cipher.final()  
    del cipher  #需要删除  
    #print v  
    return v  
#end def

def vulscan_popen(cmd):
    try:
        return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()
    except Exception,e:
        return ""
    #end try
#end def

def usage():
    print "usage: rulesupdate.py [decrypt][update]"
#end def
 
def check_version():
    
    try:
        cfg    = ConfigParser.RawConfigParser()
        cfg.readfp(open("/etc/waf_setting.rc"))
        local_rulever = cfg.get("version","rulever").replace('"','')
        print local_rulever
        
        cfg.readfp(open(rules_dir + "ver.txt"))
        new_rulever = cfg.get("version","rulever").replace('"','')
        print new_rulever
        
        local_n = local_rulever.strip().split(".")
        new_n = new_rulever.strip().split(".")
        
        if len(local_n) == 4 and len(new_n) == 4:
            if int(local_n[0]) == int(new_n[0]) and \
               int(local_n[1]) == int(new_n[1]) and \
               int(local_n[2]) == int(new_n[2]) :
                
                return True
            else:
                return False
            #end if
        else:
            return False
        #end if
    except Exception, e:
        logging.getLogger().error("check_version:" + str(e))
        return False
    #end try
#end def

def clean_files():
    os.system("rm -rf %s" % rules_dir)
    os.system("rm  %s" % upload_file)
    os.system("rm  %s" % output_zip)
#end def

def get_now_rule_ver():
    cfg.readfp(open(rules_dir + "ver.txt"))
    new_rulever = cfg.get("version","rulever").replace('"','')
    return new_rulever
#end def

def write_syslog(data):
    try:
        conn = MySQLdb.connect(host, user, passwd , db = "waf_hw", charset = "utf8")
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "insert into syslog values(0, now(),'%s')" % data
        print sql
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        logging.getLogger().error("write_syslog:" + str(e))
    #end try
#end def

def update_host():
    try:
        if os.path.isdir(rules_dir + "host"):
            #..1 update nasl files, need restart nvscand, this may take a few minutes
            
            if os.path.isdir(rules_dir + "host/nasl"):
                if len(os.listdir(rules_dir + "host/nasl")) > 0:
                    logging.getLogger().info("update....update_host...copy nasl files")
                    
                    os.system("service nvscand stop")

                    cmd = "tar xfvj /var/rules_dir/host/plugins-original.tar.bz -C /opt/nvscan/lib/nvscan/plugins"
                    vulscan_popen(cmd)
                    
                    os.system("cp %shost/nasl/* /opt/nvscan/lib/nvscan/plugins/" % rules_dir)
                    time.sleep(5)

                    logging.getLogger().info("update....update_host...rebuild nasl")
                    cmd = "/opt/nvscan/sbin/nvscan-service -R"
                    logging.getLogger().debug("File:rule_update.py, updateHostpoilcy function: %s" % (cmd))
                    vulscan_popen(cmd)

                    time.sleep(10)
                   
                    logging.getLogger().info("update....update_host...start nvscand")
                    
                    os.system("service nvscand start")
    
                else:
                    logging.getLogger().info("update....update_host...no nasl files found ,skip")
                #end if
            #end if
            
            #..2 update host sql files
            logging.getLogger().info("update....update_host...import host sql files")
            #Fix Bug #2460 #2462
            flag = False
            for f in os.listdir(rules_dir + "host"):
                if f.split(".")[-1] == "sql":
                    if 'host_family_ref' in f:
                        flag = True
                    else:
                        os.system("mysql -u%s -p%s waf_hw < %s" % (user, passwd, rules_dir + "host/" + f))
            if flag:
                os.system("mysql -u%s -p%s waf_hw < %s" % (user, passwd, rules_dir + "host/" + 'host_family_ref.sql'))

                #end if
            #end for

            #..3 update host policy
            logging.getLogger().info("update....update_host... update host policy")
            
                
        #end if
    except Exception, e:
        logging.getLogger().error("update_host:" + str(e))
    #end try
    
    return 1
#end def

def updateHostpoilcy():
    conn = MySQLdb.connect(host, user, passwd, db='waf_hw', charset='utf8')
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    cur.callproc('create_host_policy')
    #cur.execute(sql)
    conn.commit()
    
    sql = "select * from host_policy"
    cur.execute(sql)
    res = cur.fetchall()
    for row in res:
        if row['nvscan_policy_id'] and row['nvscan_policy_id'] > 0:
            cmd = "python /var/waf/nvscan_policy_manager.py update %s#" % (str(row['id']))
        else:
            cmd = "python /var/waf/nvscan_policy_manager.py add %s#" % (str(row['id']))
        #end if
        logging.getLogger().debug("File:rule_update.py, updateHostpoilcy function: %s" % (cmd))
        vulscan_popen(cmd)
    #end for
    
#end def

def update_web():
    if os.path.isdir(rules_dir + "web"):
        
        logging.getLogger().info("update....update_web...copy python files")
        if os.path.isdir(rules_dir + "web/plugins"):
            logging.getLogger().info( "cp -r %sweb/plugins/* /var/waf/plugins/" % rules_dir)
            os.system("cp -r %sweb/plugins/* /var/waf/plugins/" % rules_dir)
        #end if
        
        logging.getLogger().info("update....update_web...import sql files")
        #Fix Bug #2460 #2462
        flag = False
        for f in os.listdir(rules_dir + "web"):
            if f.split(".")[-1] == "sql":
                if 'web_family_ref' in f:
                    flag = True
                else:
                    os.system("mysql -u%s -p%s waf_hw < %s" % (user, passwd, rules_dir + "web/" + f))

        if flag:
            os.system("mysql -u%s -p%s waf_hw < %s" % (user, passwd, rules_dir + "web/" + 'web_family_ref.sql'))
            #end if
        #end for        
    #end if
    
    return 1
#end def

def update_vuls_repo():
    if os.path.isdir(rules_dir + "vuls_repo"):
        logging.getLogger().info( "cp -r %svuls_repo/* /var/vuls_db/" % rules_dir)
        os.system("cp -r %svuls_repo/* /var/vuls_db/" % rules_dir)
    #end if
    
    return 1
#end def

def update_ver(new_ver):
    #..1 update /etc/waf_setting.rc 
    os.system("/bin/sed -i \"s/^.*rulever.*$/rulever = %s /g\" /etc/waf_setting.rc" % new_ver)
    
    #..2 update /var/www/yx.config.inc.php
    os.system("/bin/sed -i \"s/^.*\$rulever.*;/        \$rulever = \'%s\';/g\" /var/www/yx.config.inc.php" % new_ver)
#end def

def single_process( a, b):
    logging.getLogger().error("updating stoped, exit(0)")

    sys.exit(0)
#end def

def copy_all_sql_file_to_waf():
    try:
        if os.path.isdir(rules_dir + "host"):
            os.system("cp -rf " + rules_dir + "host/*.sql /var/waf/")
        if os.path.isdir(rules_dir + "web"):
            os.system("cp -rf " + rules_dir + "web/*.sql /var/waf/")

    except Exception, e:
       logging.getLogger().error("rules_update.copy_all_sql_file_to_waf failed," + str(e))

if __name__ == '__main__':
    init_log(logging.DEBUG, logging.DEBUG, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    #write_syslog(u"测试中文")
    #write_syslog("开始规则升级，亲稍等")
    #check_version()
    #sys.exit(0)
    
    signal.signal(signal.SIGTERM,single_process) 
    signal.signal(signal.SIGINT,single_process)
    
    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)
    #end if
    
    if sys.argv[1] == "decrypt":
        logging.getLogger().info("decrypt....start")
        try:
            #backup package for update again when reboot
            os.system("cp -rf %s /var/waf/rules_back.dat" % upload_file)
            logging.getLogger().info("decrypt....open upload file")
            f = open(upload_file, "rb")
            logging.getLogger().info("decrypt....create zip file")
            newf = open(output_zip, "wb")
            
            logging.getLogger().info("decrypt....decrypting...")
            newf.write(decrypt(f.read()))
            f.close()
            newf.close()
            
            os.system("rm -rf %s" % rules_dir)
            os.system("mkdir %s" % rules_dir)
            logging.getLogger().info("decrypt....unzip...")
            os.system("unzip -o %s -d %s" % (output_zip, rules_dir))
            
            logging.getLogger().info("decrypt....check_version...")
            if check_version():
                logging.getLogger().info("decrypt....check_version...ok")

                sys.exit(0)
            else:
                logging.getLogger().info("decrypt....check_version...failed")
                
                write_syslog("规则文件有误，请检查文件格式及规则版本号是否匹配")
                
                sys.exit(1)
            #end if
        except Exception, e:
            logging.getLogger().error(str(e))
            write_syslog("规则文件有误，请检查文件格式及规则版本号是否匹配")
            sys.exit(-1)
        #end try
    elif sys.argv[1] == "update":
        
        
        if os.path.exists("/var/waf/rules_updating"):
            write_syslog("继续规则升级，请稍等")
        else:
            os.system("touch /var/waf/rules_updating")
            write_syslog("开始规则升级，请稍等")
        #end if
        logging.getLogger().info("update....copy all sql file to /var/waf..")
        copy_all_sql_file_to_waf()
        logging.getLogger().info("update....update_web...")
        update_web()
        logging.getLogger().info("update....update_host...")
        update_host()
        logging.getLogger().info("update....update_vuls_repo...")
        update_vuls_repo()
        write_syslog("规则升级成功，版本号：%s" % get_now_rule_ver())
        
        update_ver(get_now_rule_ver())
        
        os.system("rm /var/waf/rules_updating")
        logging.getLogger().info("update....clean...")
        clean_files()
        sendUpgradeState("rule") #send upgrade success to server
        updateHostpoilcy()
        logging.getLogger().info("update....finished...")
        
    else:
        usage()
        sys.exit(-1)
    #end if
    
    #aes_file = ".." + os.sep + "factory" + os.sep + "release" + os.sep + "rules_update.zip.aes"
    #output   = ".." + os.sep + "factory" + os.sep + "release" + os.sep + "new.zip"
    
    