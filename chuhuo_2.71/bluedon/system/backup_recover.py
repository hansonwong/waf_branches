#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import time
import MySQLdb
import heapq
from logging import getLogger

from db.mysqlconnect import mysql_connect_dict,mysql_connect
from utils.logger_init import logger_init
from smartdefend.revscan import process_revscan
from smartdefend.revcamera import process_revcamera
from db.mysql_db import select,update,select_one
from db.config1 import execute_sql


def tables_backup(args):
    """
    使用mysqldump备份3306数据库db_firewall;模块heapq控制保存最新的3次备份
    备份结果存入3307日志表m_tblog_sys_backup
    """
    #备份数据库
    print '****args:',args
    getLogger('main').info('backup tables begine')
    result_flag = False

    today=time.strftime("%Y-%m-%d-%H:%M:%S",time.localtime(time.time()))
    timeArray = time.strptime(today, "%Y-%m-%d-%H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    backup_file="/usr/local/bluedon/tmp/%s_%s.sql"%(args['sName'],today)
    sing_file="/usr/local/bluedon/tmp/%s_%s.sing"%(args['sName'],today)
    open(backup_file,'w').close()

    try:
        backup_sql='update m_tbbackup set sPath="%s",iTime="%s" where sName="%s"'%(backup_file,timeStamp,args['sName'])
        update(backup_sql)
        os.system("echo '/*The Second Firewall*/'>>'%s'"%backup_file )
        os.system("echo 'use db_firewall;' >>'%s'"%backup_file)
        print 'backup_file',backup_file

        os.system("/usr/bin/mysqldump  --sock=/tmp/mysql3306.sock --ignore-table=db_firewall.m_tbbackup  -uroot --password='bd_123456' db_firewall >> %s"%backup_file)
        # encrypt sql file in a sing file
        src_path, src = os.path.split(backup_file)
        os.system("/usr/bin/tar -zcvf - -C {src_path} {src} -P|openssl des3 -salt -k bluedon | dd of={dst}".format(src_path=src_path, src=src, dst=sing_file))
        # rename sing file to sql file
        os.system("/usr/bin/mv -f {fr} {to}".format(fr=sing_file, to=backup_file))
        time_tmp=[]
        all_backup_time = select('select iTime from m_tbbackup')
        for info in  all_backup_time:
            time_tmp.append(info['iTime'])
        retain=heapq.nlargest(3,time_tmp)
        remove_backup=set(time_tmp)^set(retain)
        while remove_backup:
            remove_time=remove_backup.pop()
            remove_file=select_one('select sPath from m_tbbackup where iTime=%s'%remove_time).get('sPath','')
            os.system('rm -f "%s"'%remove_file)
            update('delete from m_tbbackup where iTime=%s'%remove_time)
        getLogger('main').info('backup tables end')
    except Exception as e:
        print e
        result_flag=True

    finally:
        content='备份'
        sql = 'insert into m_tblog_sys_backup (iUserId,iTime,sIp,sContent,sResult)\
              values("{iUserId}","{iTime}","{sIp}","{sContent}","{sResult}")'.format(iUserId ="%s"% args['iUserId'],
                                                                                          iTime="%s"%timeStamp,
                                                                                          sIp="%s"%args['sIp'],
                                                                                          sContent=content,
                                                                                          sResult = '失败' if result_flag else '成功')
        print sql
        execute_sql(sql)


def table_restore(args):
    """
    使用mysql source将数据库覆盖,再执行配置恢复脚本second_firewall_init.py
    """
    pass
    flag = False
    today=time.strftime("%Y-%m-%d-%H:%M:%S",time.localtime(time.time()))
    timeArray = time.strptime(today, "%Y-%m-%d-%H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    try:
        # decrypt sql file
        os.system("dd if={p} |openssl des3 -d -k bluedon|tar zxf - -C /usr/local/bluedon/tmp".format(p=args['path'])) 
        os.system("/usr/bin/mysql -uroot --password='bd_123456' -e 'source %s'"%args['path'])
        os.system('python /usr/local/bluedon/core/second_firewall_init.py')
    except Exception as e:
        print e
        flag = True

    finally:
        content='恢复'
        sql = 'insert into m_tblog_sys_backup (iUserId,iTime,sIp,sContent,sResult)\
              values("{iUserId}","{iTime}","{sIp}","{sContent}","{sResult}")'.format(iUserId ="%s"% args['iUserId'],
                                                                                          iTime="%s"%timeStamp,
                                                                                          sIp="%s"%args['sIp'],
                                                                                          sContent=content,
                                                                                          sResult = '失败' if flag else '成功' )
        print sql
        execute_sql(sql)



def revscan_recover(cur=None):

    with open('/tmp/fifo/revscan','r') as fr:
         status = fr.read()
         status = eval(status)

    cur=mysql_connect_dict()
    scan_sql = 'select sValue from m_tbconfig where sName="RevscanSet"'
    cur.execute(scan_sql)
    scan_info = cur.fetchone()
    cur.close()
    if scan_info:
       data = scan_info['sValue']
       data = data.replace("\\",'')
       data = eval(data)
       print data
       if int(status['start'])==1:
          process_revscan('start', data,reset=False)


def revcamera_recover(cur=None):
    with open('/tmp/fifo/revcamera','r')as fr:
         status = fr.read()
         status = eval(status)
    cur = mysql_connect_dict()
    camera_sql = 'select sValue from m_tbconfig where sName="RevcameraSet"'
    cur.execute(camera_sql)
    camera_info = cur.fetchone()
    cur.close()
    if camera_info:
       data = camera_info['sValue']
       data = eval(data)
       #print data
       #print type(data)
       if int(status['start'])==1:
          process_revcamera('start',data,reset=False)


def recover_database(path):
    print path
    ret=os.system("/usr/bin/mysql -uroot --password='bd_123456' -e 'source %s'"%path)
    print "恢复完毕",ret


if __name__=="__main__":
    #init_database = InitDatabase()
    #init_database._clean_table()
    tables_backup()





