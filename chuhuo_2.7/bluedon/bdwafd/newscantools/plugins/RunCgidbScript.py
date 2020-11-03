#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
from lib.ex_httplib2 import *
from ScanCommonScript import *
from Queue import Empty
import threading

class RunCgidbScript():
    def __init__(self,ob):
        try:
            self.ob = ob
            self.asset_scan_id = ob['asset_scan_id']
            
            
        except Exception,e:
            logging.getLogger().error("File:RunCgidbScript.py, RunCgidbScript.__init__:" + str(e) + ",task id:" + self.ob['task_id'] + ",domain id:" + self.ob['domain_id'])
        #end try
    #end def
    
    def main(self,rules,result):
        try:
            #print ">>>>>>>>>>>>>>>>>>>>>>"
            #rules:
            #    vul_id:漏洞ID
            #    vul_name:漏洞名称
            #    level:风险等级
            #    url:追加的URL
            #    method:请求类型
            #    response:返回值
            #    response_type:返回类型
            
            #result:扫描结果数组
            
            scanobj = ScanCommon(self.ob)
            while True:
                # if rules.empty():
                #     break
                #end if
                #fix BUG #3187
                try:
                    rule_obj = rules.get_nowait()
                except Empty:
                    break
                write_scan_log(self.ob['task_id'],self.ob['domain_id'],"漏洞ID：%5s 漏洞名：%s 开始扫描 " % (rule_obj['vul_id'],rule_obj['vul_name']))
                prev = time.time()
                vul_result = scanobj.start(rule_obj)
                
                if vul_result and len(vul_result) > 0:
                    result.extend(vul_result)
                #end if
                write_scan_log(self.ob['task_id'],self.ob['domain_id'],"漏洞ID：%5s 漏洞名：%s 扫描已结束" % (rule_obj['vul_id'],rule_obj['vul_name']))
                flowControl(self,time.time()-prev,self.ob["rec"],self.ob["isForce"],self.ob["web_speed"],self.ob["web_minute_package_count"],False)
            #end while
            
        except Exception,e:
            logging.getLogger().error("File:RunCgidbScript.py, RunCgidbScript.main:" + str(e) + ",task id:" + self.ob['task_id'] + ",domain id:" + self.ob['domain_id'])
            write_scan_log(self.ob['task_id'],self.ob['domain_id'],"File:RunCgidbScript.py, RunCgidbScript.main:" + str(e))
        #end try
    #end def
    
    def start(self,rules):
        self.connect_count=0
        try:
        
            result = []
            rules_count = rules.qsize()
            if rules_count > 0:
                thread_list = []
                for i in range(10):
                    
                    thread_list.append(threading.Thread(target=self.main, args=(rules,result)))
                #end for
                for t in thread_list:
                    t.start()
                #end for
                for t in thread_list:
                    t.join()
                #end for
                
                if len(result) > 0 and len(result) < rules_count / 4:
               
                    conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
                    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
                    write_log(conn,cursor,self.ob['task_id'],result,self.ob["task_name"],self.asset_scan_id)
                  
                    conn.close()
                #end if
            #end if
            
        except Exception,e:
            logging.getLogger().error("File:RunDomainScript.py, RunDomainScript.start:" + str(e) + ",task id:" + self.ob['task_id'] + ",domain id:" + self.ob['domain_id'])
            write_scan_log(self.ob['task_id'],self.ob['domain_id'],"File:RunDomainScript.py, RunDomainScript.start:" + str(e))
        #end try
    #end def
#end class




