#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime, date, time
from lib.waf_netutil import *
import MySQLdb
import ConfigParser

PATH_HOSTS = "/etc/hosts"
PATH_HOSTS_NEW = "/etc/hosts.new"
PATH_HOSTS_HEAD = '/etc/hosts.head'
PATH_HOSTS_HEAD_NEW = '/etc/hosts.head.new'
CMD_COPY = "cp -f "

WAF_CONFIG   = "/var/waf/waf.conf"
WAF_VENDOR = '/var/waf/vendor.conf'

DEFAULT_HOST_ONE_REF = '127.0.0.1 %snvs.localdomain %snvs'
DEFAULT_HOST_TWO_REF = '127.0.0.1 localhost.localdomain localhost'
DEFAULT_HOST_THREE_REF = '127.0.0.1 %snvs'

cfg    = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
host   = cfg.get("mysql","db_ip").replace('"','')
user   = cfg.get("mysql","db_user").replace('"','')
passwd = cfg.get("mysql","db_passwd").replace('"','')

def backupHosts():
	currentTime = datetime.now()
	cmdStr = CMD_COPY + PATH_HOSTS + " " + PATH_HOSTS + ".bak." + str(currentTime)[0:str(currentTime).find('.')].replace(' ', '').replace('-', '').replace(':', '')
	#print cmdStr
	os.system(cmdStr)

def checkHosts():
    try:
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
        logging.getLogger().error("cleanHosts" + str(e))

def getItemsFromHosts():
	try:
		rf = open(PATH_HOSTS, 'r')
		wp = open(PATH_HOSTS_NEW, 'w+')
	except Exception, e:
		logging.getLogger().error('uable to open ' + PATH_HOSTS + str(e))
		return
		#get oem
	vendor    = ConfigParser.RawConfigParser()
	vendor.readfp(open(WAF_VENDOR))
	oem = vendor.get("vendor", "VENDOR_SHORT_NAME_STR_ID").replace('"', '').strip()
	if 'yxlink' in oem:
		pass
	else:
		oem = ''
		
	DEFAULT_HOST_ONE = DEFAULT_HOST_ONE_REF%(oem, oem)
	DEFAULT_HOST_TWO = DEFAULT_HOST_TWO_REF
	DEFAULT_HOST_THREE = DEFAULT_HOST_THREE_REF%(oem)

	wp.write(DEFAULT_HOST_ONE+'\n'+DEFAULT_HOST_TWO+'\n'+DEFAULT_HOST_THREE+'\n')
	lines = rf.readlines()
	for line in lines:
		item = line.split('#')
		if 5 != len(item):
			continue
		if checkItem(item):
			wp.write(line)
		else:
			pass		
	rf.close()
	wp.close()
	#backup hosts file fisrt
	#backupHosts()
	coverHosts()
	#add to check if defaultHost is deleted
	#checkHosts()

def coverHosts():
	#cmdStr = 'cat ' + PATH_HOSTS + ' | grep -v ' + item[1]+'#'+item[2] + ' >>' + PATH_HOSTS + '.new'
	cmdStr = 'mv -f ' +  PATH_HOSTS_NEW + ' ' + PATH_HOSTS
	os.system(cmdStr)
	
def checkItem(item):
	try:
		#To-do do some checkItem
		conn = MySQLdb.connect(host, user, passwd, db='waf_hw', charset='utf8')
		cur = conn.cursor(MySQLdb.cursors.DictCursor)

		sql = "select * from task_manage where state = 2"

		cur.execute(sql)
	    
		conn.commit()

		res = cur.fetchall()

		id_list = []
		for row in res:
		    #print row['id']
		    if str(row['id']).strip() not in id_list:
			    id_list += [str(row['id']).strip()]
		if item[2].strip() in id_list:
			#print item[2]
			return True
		else:
			return False

	except Exception,e:
		logging.getLogger().error("cleanHosts" + str(e))
		
if __name__ == "__main__":

    # init_log(logging.ERROR, logging.ERROR, os.path.realpath(__file__).split(".")[0] + ".log")
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    
    try:
        getItemsFromHosts()
    except Exception,e:
        logging.getLogger().error("cleanHosts" + str(e))
    #end try
#end if
