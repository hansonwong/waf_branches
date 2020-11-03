#!/usr/bin/python
#-*-encoding:UTF-8-*-
import MySQLdb
import logging
import sys
from lib.common import *

dic_list = ['form','ftp','mssql','mysql','oracle','rdp','smb','ssh','telnet','vnc','webshell','form','keyword','tomcatweakpwd','tomcatweakpwd_port']

def createDic():
    try:
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "select `Id` from `user` where `Type` = '2' or `Type` = '4'"
        cursor.execute(sql)
        res = cursor.fetchall()
        if res and len(res) > 0:
            for row in res:
                user_id = str(row['Id'])
                
                for dic_item in dic_list:
                    f = file("/var/www/dic/%s.dic" % (dic_item), "r+")
                    lines = f.readlines()
                    f.close()
                    
                    f = file("/var/www/dic/%s_%s.dic" % (dic_item,user_id),'w+')
                    f.writelines(lines)
                    f.close()
                    vulscan_popen("chown www-data /var/www/dic/%s_%s.dic" % (dic_item,user_id))
                    vulscan_popen("chgrp www-data /var/www/dic/%s_%s.dic" % (dic_item,user_id))
                #end for
            #end for
        #end if
        cursor.close()
        conn.close() 
    except Exception,e:
        logging.getLogger().error("File:WeakDic.py, createDic function:" + str(e))
    #end try
#end def

def updateDic():
    try:
        conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "select `Id` from `user` where `Type` = '2' or `Type` = '4'"
        cursor.execute(sql)
        res = cursor.fetchall()
        if res and len(res) > 0:
            for row in res:
                user_id = str(row['Id'])
                
                for dic_item in dic_list:
                    lines = []
                    if dic_item == "rdp":
                        vulscan_popen("touch /var/www/dic/rdp_%s.dic" % (user_id))
                        vulscan_popen("touch /var/www/dic/remote_%s.dic" % (user_id))
                        
                        baselines = []
                        f = file("/var/www/dic/rdp.dic", "r+")
                        temp = f.readlines()
                        f.close()
                        for row in temp:
                            t = row.replace("\n","").replace("\r","").strip()
                            if t == "":
                                continue
                            #end if
                            baselines.append("%s\n" % (t))
                        #end for
                        
                        f = file("/var/www/dic/rdp_%s.dic" % (user_id), "r+")
                        temp = f.readlines()
                        f.close()
                        for row in temp:
                            t = row.replace("\n","").replace("\r","").strip()
                            if t == "":
                                continue
                            #end if
                            t = "%s\n" % (t)
                            if t in baselines:
                                continue
                            else:
                                lines.append(t)
                            #end if
                        #end for
                        
                        f = file("/var/www/dic/remote_%s.dic" % (user_id), "r+")
                        temp = f.readlines()
                        f.close()
                        for row in temp:
                            t = row.replace("\n","").replace("\r","").strip()
                            if t == "":
                                continue
                            #end if
                            t = "%s\n" % (t)
                            if t in baselines:
                                continue
                            else:
                                lines.append(t)
                            #end if
                        #end for
                        
                        lines.extend(baselines)
                    elif dic_item == "tomcatweakpwd_port":
                        vulscan_popen("touch /var/www/dic/%s_%s.dic" % (dic_item,user_id))
                        list = []
                        
                        f = file("/var/www/dic/%s.dic" % (dic_item), "r+")
                        temp = f.readlines()
                        f.close()
                        temp = temp[0].replace("\n","").replace("\r","").replace(" ","").split("|")
                        for row in temp:
                            if row == "":
                                continue
                            else:
                                if row in list:
                                    continue
                                else:
                                    list.append(row)
                                #end if
                            #end if
                        #end for
                        
                        f = file("/var/www/dic/%s_%s.dic" % (dic_item,user_id), "r+")
                        temp = f.readlines()
                        f.close()
                        if len(temp) > 0:
                            temp = temp[0].replace("\n","").replace("\r","").replace(" ","").split("|")
                            for row in temp:
                                if row == "":
                                    continue
                                else:
                                    if row in list:
                                        continue
                                    else:
                                        list.append(row)
                                    #end if
                                #end if
                            #end for
                        #end if
                        
                        if len(list) > 0:
                            lines.append("|".join(list))
                        #end if
                    else:
                        vulscan_popen("touch /var/www/dic/%s_%s.dic" % (dic_item,user_id))
                        
                        f = file("/var/www/dic/%s_%s.dic" % (dic_item,user_id), "r+")
                        temp = f.readlines()
                        f.close()
                        for row in temp:
                            t = row.replace("\n","").replace("\r","").strip()
                            if t == "":
                                continue
                            #end if
                            if dic_item == 'keyword' and t.find('|') >= 0:
                                continue
                            #end if
                            lines.append("%s\n" % (t))
                        #end for
                        
                        f = file("/var/www/dic/%s.dic" % (dic_item), "r+")
                        temp = f.readlines()
                        f.close()
                        for row in temp:
                            t = row.replace("\n","").replace("\r","").strip()
                            if t == "":
                                continue
                            #end if
                            t = "%s\n" % (t)
                            if t in lines:
                                continue
                            else:
                                lines.append(t)
                            #end if
                        #end for
                    #end if
                    
                    f = file("/var/www/dic/%s_%s.dic" % (dic_item,user_id),'w+')
                    f.writelines(lines)
                    f.close()
                    vulscan_popen("chown www-data /var/www/dic/%s_%s.dic" % (dic_item,user_id))
                    vulscan_popen("chgrp www-data /var/www/dic/%s_%s.dic" % (dic_item,user_id))
                #end for
            #end for
        #end if
        cursor.close()
        conn.close()
    except Exception,e:
        logging.getLogger().error("File:WeakDic.py, updateDic function:" + str(e))
    #end try
#end def

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        if len(sys.argv) == 2:
            type = sys.argv[1]
            if type == 'create':
                logging.getLogger().debug("File:WeakDic.py, __main__: create ")
                createDic()
            elif type == 'update':
                logging.getLogger().debug("File:WeakDic.py, __main__: update ")
                updateDic()
            else:
                logging.getLogger().error("File:WeakDic.py, __main__: argv error ")
            #end if
        else:
            logging.getLogger().error("File:WeakDic.py, __main__: argv error ")
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:WeakDic.py, __main__:" + str(e))
    #end try
#end if

