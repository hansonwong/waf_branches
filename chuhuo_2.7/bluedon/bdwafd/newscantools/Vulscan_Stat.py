#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys
import datetime
import os
import Mail
from lib.common import *

class Vulscan_Stat:
    
    def __init__(self):
        
        try:
        
            self.conn = ""

            self.cursor = ""
            
        except Exception,e:
            
            logging.getLogger().error("init CountVul Exception(Vulscan_Stat):" + str(e))
            
        #end try
    #end def
    
    def mysqlConnect(self):
        
        try:
        
            self.conn = MySQLdb.connect(host, user, passwd , db = "waf_hw", charset = "utf8")
        
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            
        except Exception,e:
            
            logging.getLogger().error("mysql connect Exception(Vulscan_Stat):" + str(e))
            
        #end try            
    #end def
    
    def mysqlClose(self):
        
        try:
        
            self.cursor.close()
        
            self.conn.close()
            
        except Exception,e:
            
            logging.getLogger().error("mysql close Exception(Vulscan_Stat):" + str(e))
            
        #end try          
    #end def
    
    def isTaskRun(self):
        
        try:
            
            #logging.getLogger().error("check isTaskRun")
            
            self.mysqlConnect()
            
            self.cursor.execute("select count(Id) as c from `task_list` where `Status` = '2' ")
    
            ret = self.cursor.fetchone()
            
            self.mysqlClose()
            
            if ret and len(ret) > 0:
                
                count = ret['c']
                
                if count > 0:
                    
                    return True
                
                else:
                    
                    return False
                
                #end if
                
            else:
                
                return False
            
            #end if
        
        except Exception,e:
            
            logging.getLogger().error("isTaskRun Exception(Vulscan_Stat):" + str(e))
            
        #end try          
    #end def
    
    def isDomainRun(self):
        
        try:
            
            #logging.getLogger().error("check isDomainRun")
            
            self.mysqlConnect()
            
            self.cursor.execute("select count(Id) as c from `domain_list` where `Status` = '2' ")
            
            ret = self.cursor.fetchone()
            
            self.mysqlClose()
            
            if ret and len(ret) > 0:
                
                if ret['c'] > 0:
                    
                    return True
                
                else:
                    
                    return False
                
                #end if
                
            else:
                
                return False
            
            #end if
            
        except Exception,e:
            
            logging.getLogger().error("isDomainRun Exception(Vulscan_Stat):" + str(e))
            
        #end try          
    #end def
    
    def update_task_count(self):
        
        try:
            
            #logging.getLogger().error("run update_task_count")
            
            list = []
            
            self.mysqlConnect()
            
            self.cursor.execute("select `Id` from `task_list` where `Status` = '2' ")
            
            ret = self.cursor.fetchall()
            
            if ret and len(ret) > 0:
                
                for row in ret:
                    
                    list.append(str(row['Id']))
                    
                #end for
            #end if
            
            if list and len(list) > 0:
                
                for i in range(0,len(list)):
                    
                    tablename = "scan_result_" + list[i]
                    
                    if table_exists(tablename):
                        
                        #sql_num = 0
                        
                        high = 0
                        
                        med = 0
                        
                        low = 0
                        
                        self.cursor.execute("select count(Id) as c , `Level` from " + tablename + " group by `Level` ")
                        
                        ret = self.cursor.fetchall()
                        
                        if ret and len(ret):
                            
                            for row in ret:
                                
                                if str(row['Level']) == "HIGH":
                                    
                                    high = row['c']
                                    
                                elif str(row['Level']) == "MED":
                                    
                                    med = row['c']
                                    
                                elif str(row['Level']) == "LOW":
                                    
                                    low = row['c']
                                    
                                #end if
                            #end for
                        #end if
                        
                        count = high + med + low
                        
                        self.cursor.execute("update `task_list` set `High` = '" + str(high) + "' , `Med` = '" + str(med) + "' , `Low` = '" + str(low) + "' , `Count` = '" + str(count) + "' where `Id` = '" + list[i] + "' ")
                        
                        self.conn.commit()
                        
                    #end if
                #end for
            #end if
            
            self.mysqlClose()
            
        except Exception,e:
            
            logging.getLogger().error("update_task_count Exception(Vulscan_Stat):" + str(e))
            
        #end try
    #end def
    
    def update_domain_count(self):
        
        try:
    
            #logging.getLogger().error("run update_domain_count")
            
            self.mysqlConnect()
            
            list = []
            
            self.cursor.execute("select `Id` from `domain_list` where `Status` = '2' ")
            
            ret = self.cursor.fetchall()
            
            if ret and len(ret) > 0:
                
                for row in ret:
                    
                    list.append(str(row['Id']))
                    
                #end for
            #end if
            
            if list and len(list) > 0:
                
                for i in range(0,len(list)):
                    
                    domainId = list[i]
                    
                    self.cursor.execute("select `TaskId` from `domain_list` where `Id` = '" + domainId + "' ")
                    
                    ret = self.cursor.fetchone()
                    
                    if ret and len(ret) > 0:
                        
                        tablename = "scan_result_" + str(ret['TaskId'])
                        
                        if table_exists(tablename):
                            
                            high = 0
                            
                            med = 0
                            
                            low = 0
                            
                            self.cursor.execute("select count(Id) as c , `Level` from " + tablename + " where `DomainId` = '" + domainId + "' group by `Level` ")
                            
                            ret = self.cursor.fetchall()
                            
                            if ret and len(ret) > 0:
                                
                                for row in ret:
                                    
                                    if str(row['Level']) == "HIGH":
                                        
                                        high = row['c']
                                        
                                    elif str(row['Level']) == "MED":
                                        
                                        med = row['c']
                                        
                                    elif str(row['Level']) == "LOW":
                                        
                                        low = row['c']
                                        
                                    #end if
                                #end for
                            #end if
                            
                            count = high + med + low
                            
                            self.cursor.execute("update `domain_list` set `High` = '" + str(high) + "' , `Med` = '" + str(med) + "' , `Low` = '" + str(low) + "' , `Count` = '" + str(count) + "' where `Id` = '" + domainId + "' ")
                            
                            self.conn.commit()
                            
                        #end if
                    #end if
                #end for
            #end if
            
            self.mysqlClose()
            
        except Exception,e:
            
            logging.getLogger().error("update_domain_count Exception(Vulscan_Stat):" + str(e))
            
        #end try
    #end def
    
    def update_scan_result(self):
        
        try:
            
            #logging.getLogger().error("run update_scan_result")
            
            vullist = []
            
            userlist = []
            
            vulCount = []
            
            self.mysqlConnect()
            
            self.cursor.execute("select `Id` from `vul_list` ")
            
            ret = self.cursor.fetchall()
            
            if ret and len(ret) > 0:
                
                for row in ret:
                    
                    vullist.append(str(row['Id']))
                    
                #end for
            #end if
            
            self.cursor.execute("select `UserId` from `task_list` group by `UserId` ")
            
            ret = self.cursor.fetchall()
            
            if ret and len(ret) > 0:
                
                for row in ret:
                    
                    #UserId = str(row['UserId'])
                    userlist.append(str(row['UserId']))
                    
                #end for
            #end if
            
            if userlist and len(userlist) > 0:
                
                for i in range(0,len(userlist)):
                    
                    userId = userlist[i]
                    
                    for i in range(0,len(vullist)):
                
                        #vulCount[i] = 0
                        vulCount.append(0)
                
                    #end for
                    
                    self.cursor.execute("select `Id` from `task_list` where `UserId` = '" + userId + "' ")
                    
                    ret = self.cursor.fetchall()
                    
                    if ret and len(ret) > 0:
                        
                        for row in ret:
                            
                            Id = str(row['Id'])
                            
                            tablename = "scan_result_" + Id

                            if table_exists(tablename):
                                
                                self.cursor.execute("select count(Id) as c , VulId from " + tablename + " group by VulId ")
                                
                                countList = self.cursor.fetchall()
                                
                                if countList and len(countList) > 0:
                                    
                                    for countItem in countList:
                                        
                                        count = countItem['c']
                                        
                                        vulId = countItem['VulId']
                                        
                                        '''
                                        if vulId == 1:
                                            
                                            count = count / 2
                                            
                                        #end if
                                        '''
                                        
                                        vulCount[vulId-1] += count
                                        
                                    #end for
                                #end if
                            #end if
                        #end for
                    #end if
                    
                    content = ""
                    
                    for i in range(0,len(vullist)):
                        
                        content += str(i + 1) + ":" + str(vulCount[i]) + ","
                        
                    #end for
                    
                    content = content[0:-1]
                    
                    self.cursor.execute("delete from `user_vullist` where `UserId` not in (select `Id` from `user`)")
                    
                    self.conn.commit()
                    
                    self.cursor.execute("select `Id` from `user_vullist` where `UserId` = '" + userId + "' ")
                    
                    ret = self.cursor.fetchall()
                    
                    if ret and len(ret) > 0:
                        
                        sql = "update `user_vullist` set `VulList` = '" + content + "' where `UserId` = '" + userId + "' "
                        
                    else:
                        
                        sql = "insert into `user_vullist` (`UserId`,`VulList`) values ('" + userId + "','" + content + "')"
                    
                    #end if
                    
                    self.cursor.execute(sql)
                    
                    self.conn.commit()
                    
                #end for
            #end if
            
            self.mysqlClose()
            
        except Exception,e:
            
            logging.getLogger().error("update scan result Exception(Vulscan_Stat):" + str(e))
            
        #end try
    #end def
    
    def check_task_schedule(self):
        
        try:
            
            #logging.getLogger().error("run check_task_schedule")
            
            f = file("/etc/crontab", "r+")
        
            lines = f.readlines()
            
            for line in lines:
                
                if line.find("TaskManage.py") >= 0:
                    
                    list = []
                    
                    list = line.split(' ')
                    
                    taskId = list[len(list)-5]
                    
                    self.mysqlConnect()
                    
                    self.cursor.execute("select count(Id) as c from `task_list` where `Id` = '" + taskId + "' and `Status` = '1' and `Schedule` <> '' ")
                    
                    ret = self.cursor.fetchone()
                    
                    self.mysqlClose()
                    
                    #logging.getLogger().error(taskId)
                    
                    if ret and len(ret) > 0:
                        
                        if ret['c'] > 0:
                            
                            continue
                        
                        else:
                            
                            lines.remove(line)
                            
                            #logging.getLogger().error("remove line : " + line)
                        
                        #end if
                        
                    else:
                        
                        lines.remove(line)
                        
                        #logging.getLogger().error("remove line : " + line)
                        
                    #end if
                #end if
            #end for
            
            f.close()
        
            f = file("/etc/crontab", "w+")
        
            f.writelines(lines)
        
            f.close()
            
        except Exception,e:
            
            logging.getLogger().error("check_task_schedule Exception(Vulscan_Stat):" + str(e))
        
        #end try
    #end def
    
    def update_task_schedule(self):
        
        try:
            
            self.mysqlConnect()
            
            self.cursor.execute("select `Id` , `Schedule` from `task_list` where `Status` = '1' and `Schedule` <> '' ")
            
            ret = self.cursor.fetchall()
            
            if ret and len(ret) > 0:
                
                for row in ret:
                    
                    Id = str(row['Id'])
                    
                    command1 = ""
                    
                    Schedule = str(row['Schedule'])
                    
                    if Schedule.find('#') < 0:
                        
                        list = Schedule.split(':')
                        
                        if len(list) != 3:
                            
                            continue
                        
                        #end if
                        
                        hour = list[0]
                        
                        minute = list[1]
                        
                        command1 = minute + " " + hour + " * * *"
                        
                    else:
                        
                        list = Schedule.split('#')
                        
                        if len(list) != 2:
                            
                            continue
                        
                        #end if
                        
                        type = list[0]
                        
                        Schedule = list[1]
                        
                        list = Schedule.split(':')
                        
                        if len(list) != 3:
                            
                            continue
                        
                        #end if
                        
                        hour = list[0]
                        
                        minute = list[1]
                        
                        if len(type) == 1:
                            
                            if type == "7":
                                
                                command1 = minute + " " + hour + " * * 0"
                                
                            else:
                                
                                command1 = minute + " " + hour + " * * " + type
                                
                            #end if
                            
                        else:
                            
                            command1 = minute + " " + hour + " " + type + " * *" 
                        
                    #end if
                    
                    command2 = " www-data /usr/bin/python /var/vulscan/TaskManage.py " + Id + " 1 > /dev/null &"
                    
                    f = file("/etc/crontab", "r+")
        
                    lines = f.readlines()
                    
                    flag = True
            
                    for line in lines:
                        
                        if line.find(command2) >= 0:
                            
                            flag = False
                            
                            if line.find(command1) >= 0:
                                
                                break
                            
                            else:
                                
                                lines.remove(line)
                                
                                lines.append(command1 + command2)
                                
                                #logging.getLogger().error("add schedule1:" + command1 + command2)
                                
                                break
                            
                            #end if
                        #end if
                    #end for
                    
                    if flag:
                        
                        lines.append(command1 + command2)
                        
                        #logging.getLogger().error("add schedule2:" + command1 + command2)
                        
                    #end if
                    
                    f.close()
        
                    f = file("/etc/crontab", "w+")
        
                    f.writelines(lines)
        
                    f.close()
                    
                    lines = []
                    
                #end for
            #end if
            
            self.mysqlClose()
            
        except Exception,e:
            
            logging.getLogger().error("update_task_schedule Exception(Vulscan_Stat):" + str(e))
            
        #end try
    #end def
    
    def send_email(self,taskId):
        
        try:
        
            mainManage = Mail.MailManage(taskId)
            
        except Exception,e:
            
            logging.getLogger().error("send email Exception:" + str(e))
            
        #end try
    #end def
    
    def checkTaskShow(self):
        
        try:
            
            self.mysqlConnect()
            
            self.cursor.execute("select `Id` from `task_list` where `Status` = '2' ")
            
            ret = self.cursor.fetchall()
            
            self.mysqlClose()
            
            if ret and len(ret) > 0:
                
                for row in ret:
                
                    taskId = str(row['Id'])
                    
                    lines = vulscan_popen("ps aux|grep 'TaskManage.py " + taskId + " '")
                    
                    if lines and len(lines) >= 3:
                        
                        continue
                    
                    else:
                        
                        #stop task show
                        current_time = time.strftime("%Y-%m-%d %X",time.localtime())
                        
                        self.mysqlConnect()
                        
                        self.cursor.execute("update `task_list` set `Status` = '3' , `EndTime` = '" + current_time + "' where `Id` = '" + taskId + "' ")
                        
                        self.conn.commit()
                        
                        self.cursor.execute("update `domain_list` set `Status` = '3' , `EndTime` = '" + current_time + "' where `TaskId` = '" + taskId + "' and `Status` <> '3' ")
                        
                        self.conn.commit()
                        
                        self.mysqlClose()
                        
                        self.update_scan_result()
                        
                        self.update_domain_count()
                        
                        self.update_task_count()
                        
                        self.send_email(taskId)
                        
                        #logging.getLogger().error("TaskId : " + taskId + " run Exception,stop Exception(Vulscan_Stat)----" + str(len(lines)))
                        
                    #end if
                #end for
            #end if
            
        except Exception,e:
            
            logging.getLogger().error("checkTaskShow Exception(Vulscan_Stat):" + str(e))
            
        #end try
    #end def
    
    def checkTaskRun(self):
        
        try:
            
            command = "ps aux|grep python"
            
            lines = vulscan_popen(command)
            
            if lines and len(lines) > 0:
                
                for line in lines:
                   
                    if line.find("TaskManage.py") >= 0:
                       
                        list = line.split(' ')
                       
                        if list and len(list) > 3:
                           
                            taskId = list[2]
                            
                            self.mysqlConnect()
                            
                            self.cursor.execute("select count(Id) as c from `task_list` where `Status` = '2' and `Id` = '" + taskId + "' ")
                            
                            ret = self.cursor.fetchone()
                            
                            if ret and len(ret) > 0:
                                
                                if ret['c'] <= 0:
                    
                                    os.system("/bin/kill $(ps -ef|grep '/usr/bin/python /var/vulscan/TaskManage.py " + taskId + " ' | /usr/bin/awk '$0 !~/grep/ {print $2}' | tr -s '\n' ' ')")
                                    
                                    self.update_scan_result()
                                    
                                    self.update_domain_count()
                                    
                                    self.update_task_count()
                                    
                                #end if
                                
                            else:
                                
                                os.system("/bin/kill $(ps -ef|grep '/usr/bin/python /var/vulscan/TaskManage.py " + taskId + " ' | /usr/bin/awk '$0 !~/grep/ {print $2}' | tr -s '\n' ' ')")
                                
                                self.update_scan_result()
                                
                                self.update_domain_count()
                                
                                self.update_task_count()
                                
                            #end if
                            
                            self.mysqlClose()
                            
                        #end if
                    #end if
                #end for
            #end if
            
        except Exception,e:
            
            logging.getLogger().error("checkTaskRun Exception(Vulscan_Stat):" + str(e))
            
        #try
    #end def
    
    def checkDNS(self):
        
        #logging.getLogger().error("run checkDNS")
        
        try:
            
            self.mysqlConnect()
            
            self.cursor.execute("select `Id` , `Domain` , `Ip` from `domain_list` where `Status` = '2' ")
            
            ret = self.cursor.fetchall()
            
            if ret and len(ret) > 0:
                
                for row in ret:
                    
                    msg = ""
                    
                    Id = str(row['Id'])
                    
                    Domain = row['Domain']
                    
                    Ip = row['Ip']
                    
                    msg = Ip + " " + Domain + " #scanleak" + Id
                    
                    try:
        
                        f = file("/etc/hosts", "r+")
        
                        lines = f.readlines()
                        
                        flag = False
                        
                        if lines and len(lines) > 0:
                            
                            for line in lines:
                                
                                if line.find(msg) >= 0:
                                    
                                    flag = True
                                    
                                    break
                                
                                #end if
                            #end for
                        #end if
                        
                        if flag == False:
                            
                            lines.append(msg + "\n")
                        
                        #end if
            
                        f.close()
                        
                        if flag == False:
        
                            f = file("/etc/hosts", "w+")
        
                            f.writelines(lines)
        
                            f.close()
                            
                        #end if
            
                    except Exception,e1:
            
                        logging.getLogger().error("add domain Exception:" + str(e1))
            
                    #end try
                #end for
            #end if
            
            self.mysqlClose()
            
        except Exception,e:

            logging.getLogger().error("checkDNS Exception(Vulscan_Stat):" + str(e))

        #end try
    #end def

    def main(self):
    
        try:
            
            if self.isTaskRun():
                
                self.update_scan_result()
                
            #end if
            
            if self.isDomainRun():
                
                self.update_domain_count()
                
            #end if
            
            if self.isTaskRun():
                
                self.update_task_count()
                
            #end if

            self.checkTaskShow()
            
            self.checkDNS()
        
        except Exception,e:
        
            logging.getLogger().error("main Exception(Vulscan_Stat):" + str(e))
    
        #end try
    #end def
    
#end class

if __name__ == "__main__":

    init_log(logging.ERROR, logging.ERROR, LOG_DIR + os.path.basename(__file__).split(".")[0] + ".log")

    try:
        
        #logging.getLogger().error("run Vulscan_Stat")
        
        vulscan_stat = Vulscan_Stat()
    
        vulscan_stat.main()
        
    except Exception,e:
        
        logging.getLogger().error("__main__ Exception(Vulscan_Stat):" + str(e))
    
    #end try
#end if
    
    
    
    
    