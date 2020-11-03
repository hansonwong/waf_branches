#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import os
import sys
import threading
import time
import Queue
import uuid
import json
import uuid

import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn

class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):pass


class Dispatch(threading.Thread):

    def __init__(self):
        super(Dispatch, self).__init__()
        self.server = ThreadXMLRPCServer(("localhost", 89), allow_none=True, logRequests=False)
        self.server.register_function(self.getTask, "getTask")
        self.server.register_function(self.register, "register")
        self.server.register_function(self.invoke, "invoke")
        self.server.register_function(self.sendRet, "sendRet")
        
        
        # 统计用的计数器
        self.timeout_counter = 0
        self.no_such_task_counter = 0
        self.get_task_count = 0
        self.send_resp_count = 0
        
        # 统计速度用
        self.last_get_task_count = 0;
        
        self.task_dic = {}
        self.ret_dic = {}
        
        self.setDaemon(True)
        self.start()
        print "starting"
        
    def serve_forever(self):
        self.server.serve_forever()
    
    def register(self, client_name):
        self.task_dic[client_name] = None
        self.task_dic[client_name] = Queue.Queue()
        
        self.ret_dic[client_name] = None
        self.ret_dic[client_name] = {}
        
        print "register client", client_name
        
        return True

    def getTask(self,  client_name):
        """
            客户端获取任务（阻塞型）
        """
        obj = self._getTask(client_name)
        
        
        
        if obj:
            self.get_task_count += 1
            return json.dumps(obj)
        else:
            return ""
    
    def _getTask(self,  client_name):
        """
            客户端获取任务（阻塞型）
        """
        if not self.task_dic.has_key(client_name):
            self.task_dic[client_name] = Queue.Queue()
            self.ret_dic[client_name] = {}
        
        
        try:
            task = self.task_dic[client_name].get(timeout = 3)
        except:
            return None
        #print "get task", task
        return task
        
    def sendRet(self, client_name, issuccess, taskid, ret):
        """
            给client上报处理结果
        """
        self.send_resp_count += 1
        #print "recv Ret", ret
        self.ret_dic[client_name][taskid] = {"issuccess": issuccess, "ret": ret}

    def invoke(self, client_name, fun_name, param):
        obj = self._invoke(client_name, fun_name, param)
        return json.dumps(obj)
    def _invoke(self, client_name, fun_name, param):
        
        if not self.task_dic.has_key(client_name):
            # 没找到响应的客户端
            return {"errorInfo": "no such client"}
        
        # 创建唯一的任务ID
        taskid = "%s-%s" % (client_name, uuid.uuid4())
        # 获取任务队列
        queue = self.task_dic[client_name]
        # 往任务队列中添加任务
        queue.put({"fun_name": fun_name, "param": param, "taskid": taskid})
        
        # 等待任务执行并把结果压入结果队列
        hadFind = False
        for i in range(400) :
            if self.ret_dic[client_name].has_key(taskid):
                hadFind = True
                break
            else:
                time.sleep(0.005)
        #print "hadFind", hadFind
        if hadFind:
            if self.ret_dic[client_name].has_key(taskid):
                ret = self.ret_dic[client_name][taskid]
                del self.ret_dic[client_name][taskid]
                return {"errorInfo": "success", "result": ret}
            else:
                self.no_such_task_counter += 1
                return {"errorInfo": "no such task"}
        else:
            self.timeout_counter += 1
            return {"errorInfo": "timeout"}
            
        return {"errorInfo": "error"}
    def run(self):
        print "监控管理线程"
        while True:
            
            cache_task_count = 0
            for cleint_name in self.task_dic:
                q = self.task_dic[cleint_name]
                cache_task_count += q.qsize()
            
            cache_ret_count = 0
            for cleint_name in self.ret_dic:
                d = self.ret_dic[cleint_name]
                cache_task_count += len(d)
            
            
            print "-------------------------"
            print "缓存任务数：    ", cache_task_count
            print "缓存任务结果数：", cache_ret_count
            print "获取结果超时数：", self.timeout_counter
            print "找不到任务数：  ", self.no_such_task_counter
            print "处理任务数：    ", self.get_task_count
            print "处理速度：      ", self.get_task_count - self.last_get_task_count
            print "获取任务结果数：", self.send_resp_count
            self.last_get_task_count = self.get_task_count
            time.sleep(1)
        
class XmlRcpClient(threading.Thread):

    def __init__(self, client_name):
        super(XmlRcpClient, self).__init__()
        self.funs = {}
        self.client_name = client_name
        self.client_task = xmlrpclib.ServerProxy("http://localhost:89")
        self.client_invoke = xmlrpclib.ServerProxy("http://localhost:89")
        
        self.client_task.register(self.client_name)
        
        self.setDaemon(True)
        self.start()
    def invoke(self, client_name, fun_nae, param):
        ret = self.client_invoke.invoke(client_name, fun_nae, param)
        j = json.loads(ret)
        if j["errorInfo"] == "success":
            if j["result"]["issuccess"] in (True, 1):
                return j["result"]["ret"]
            else:
                raise Exception("no such function")
        else:
            raise Exception(j["errorInfo"])
        return None
        
    def register_function(self, fun):
        self.funs[fun.__name__] = fun

    def doTask(self, task):
        fun_name = task["fun_name"]
        param = task["param"]
        taskid = task["taskid"]
        #print "doTsk", fun_name, param, taskid
        if self.funs.has_key(fun_name):
            #print self.funs[fun_name]
            ret = self.funs[fun_name](param)
            #print "doTsk", fun_name, param, taskid, "ret =", ret
            self.client_task.sendRet(self.client_name, True, taskid, ret)
            return True
        else:
            self.client_task.sendRet(self.client_name, False, taskid, None)
            return False
            
    def run(self):
        
        while True:
            task = self.client_task.getTask(self.client_name)
            if task is not None:
                if self.doTask(task):
                    #print "do Task success"
                    pass
                else:
                    #print "do Task fail"
                    pass
            else:
                time.sleep(1)
                
def getNameA(param):
    return "my name is ydc a"

def getNameAJSON(param):
    return {"a": 1, "b": 2, "c": [1, 2, 3, 4]}
    
def getNameB(param):
    return "my name is ydc b"


def main():
    print sys.argv
    if len(sys.argv) > 1:
        if sys.argv[1] == "server":
            server = Dispatch()
            server.serve_forever()
            
        elif sys.argv[1] == "test1":
            
            client = XmlRcpClient("clientA")
            time.sleep(2)
            client.register_function(getNameA)
            client.register_function(getNameAJSON)
            try:
                ret = client.invoke("clientB", "getNameB", "")
                print "getname ret = ", ret
            except Exception, e:
                print e
            while True:
                time.sleep(1)
                
        elif sys.argv[1] == "test2":
            
            client = XmlRcpClient("clientB")
            time.sleep(2)
            client.register_function(getNameB)
            try:
                ret = client.invoke("clientA", "getNameA", "")
                print "getname ret = ", ret
            except Exception, e:
                print e
            while True:
                time.sleep(1)
                
        elif sys.argv[1] == "test":
            
            client = XmlRcpClient("clientC")
            client.register_function(getNameB)
            while True:
                try:
                    
                    ret = client.invoke("clientTest", "myTestFun", "%s" % (uuid.uuid4()))
                    print "getname ret = ", ret
                    
                    ret = client.invoke("clientTest", "myAddFun", {"a": 1, "b": 2})
                    print "getname ret = ", ret
                except Exception, e:
                    print e
            #while True:
            #    time.sleep(1)

if __name__ == "__main__":
    main()
