#!/usr/bin/python
#-*- coding:utf-8 -*-
import os
import sys
import time
import threading

import uuid
import json
import redis
import Queue

class RedisRPCClient(threading.Thread):

    ACTION_INVOKE = 0       # 执行方法
    ACTION_SENDRESP = 1     # 推送返回值
    ACTION_INVOKE_ASYNC = 2

    def __init__(self, clientname):
        super(RedisRPCClient, self).__init__()
        self.clientname = clientname
        self.clientchannel = 'redisrpc_%s_task' % (clientname)
        self.funs = {}
        self.resp_dic = {}
        self.resp_events = {}

        self.stop_client = threading.Event()

        # 统计超时的返回值个数
        self.counter_timeout_resp_count = 0
        self.counter_get_resp_timeout_count = 0
        # 调用成功的次数
        self.counter_invoke_success = 0
        # 被调用能正常返回的次数
        self.counter_be_invoke_success = 0
        # 上一秒调用次数
        self.counter_last_sec_invoke_count = 0

        if self._register(clientname):
            self.setDaemon(True)
            self.start()

    def _register(self, clientname):
        try:
            self.rc = redis.Redis(host='127.0.0.1')
            self.rc.ping()
            self.ps = self.rc.pubsub()
            self.ps.psubscribe(['redisrpc_%s_task' % (clientname)])
        except :
            return False
        return True

    def register_function(self, fun):
        self.funs[fun.__name__] = fun

    def invoke(self, clientname, funname, param, timeout=1, async_=False):

        retval = None
        uid = uuid.uuid4().hex
        data = json.dumps({
            "action": self.ACTION_INVOKE if not async_ else self.ACTION_INVOKE_ASYNC,
            "clientname": self.clientname,
            "taskid": uid,
            "funname": funname,
            "param": param
        })

        eventname = "%s_%s" % (funname, uid)
        self.resp_events[eventname] = threading.Event()
        #print "add event ", eventname, time.time()
        self.rc.publish('redisrpc_%s_task' % (clientname), data)

        if async_: return None

        if self.resp_events[eventname].wait(timeout=timeout):
            self.counter_invoke_success += 1
            task = self.resp_dic[eventname]
            del self.resp_dic[eventname]

            if task is not None:
                param = task["param"]
                retval = param
        else:
            # 超时
            self.counter_get_resp_timeout_count += 1
            pass

        if self.resp_events.has_key(eventname):
            #print "del event2", eventname, time.time()
            del self.resp_events[eventname]


        return retval

    def _sendRet(self, task, ret):
        clientname = task["clientname"]
        funname = task["funname"]
        param = task["param"]
        taskid = task["taskid"]

        retobj = {
            "action": self.ACTION_SENDRESP,
            "clientname": self.clientname,
            "taskid": taskid,
            "funname": funname,
            "param": ret
        }
        self.rc.publish('redisrpc_%s_task' % (clientname), json.dumps(retobj))
        #print 'redisrpc_%s_task' % (clientname), json.dumps(retobj)


    def _doTask(self, task):
        clientname = task["clientname"]
        funname = task["funname"]
        param = task["param"]
        taskid = task["taskid"]
        action = task["action"] # 0 invoke  1 getresp

        if action == 0:
            # 解析任务信息，并处理任务
            #print "doTsk", fun_name, param, taskid

            if self.funs.has_key(funname):
                self.counter_be_invoke_success += 1
                #print self.funs[fun_name]
                ret = self.funs[funname](param)
                self._sendRet(task, ret)
                return True
            else:

                return False
        elif action == 1:
            # 解析返回值

            task["time"] = time.time()
            # 拼凑event名称
            eventname = "%s_%s" % (funname, taskid)
            # 将task保存到字典中
            self.resp_dic[eventname] = task


            # 调用event
            if self.resp_events.has_key(eventname):
                #print "set ret ", eventname, "OK"
                self.resp_events[eventname].set()
            else:
                print "set ret ", eventname, "FAIL"

        elif action == self.ACTION_INVOKE_ASYNC:
            # async call
            if self.funs.has_key(funname):
                self.counter_be_invoke_success += 1
                #print self.funs[fun_name]
                ret = self.funs[funname](param)
                return True
            else:
                return False




    def dump(self):
        print "-----------------------------"
        print "超时的返回数量: %d" % self.counter_get_resp_timeout_count
        print "调用成功的次数: %d" % self.counter_invoke_success
        print "被调用的次数  : %d" % self.counter_be_invoke_success
        print "返回值缓存数量: %d" % len(self.resp_dic)
        print "每秒远程调用量: %d" % (self.counter_invoke_success - self.counter_last_sec_invoke_count)

    def stop(self):
        print 'stopping RedisRPCClient'
        # set stop event
        self.stop_client.set()
        print 'stop RedisRPCClient: Event Set'
        # tell client to stop waiting message from redis
        self.rc.publish(self.clientchannel, '')
        print 'stop RedisRPCClient: Send null message to %s' % self.clientchannel
        # release all waiting task
        for eventname in self.resp_events:
            self.resp_events[eventname].set()
            print 'stop RedisRPCClient: Event Set %s' % eventname

    def run(self):
        last_clear_time = time.time()
        last_print_time = last_clear_time


        while True:
            if self.stop_client.isSet(): break
            for item in self.ps.listen():
                if self.stop_client.isSet(): break
                if item['type'] == 'pmessage':
                    data = item['data']
                    #print data
                    try:
                        task = json.loads(data)
                        self._doTask(task)
                    except:
                        # log here
                        print 'wrong task: %s' % data

                # 清理超时的返回值
                t = time.time()
                # 三秒钟进行一次超时释放操作
                if t - last_clear_time > 3:
                    del_key_list = []
                    for k in self.resp_dic:
                        task = self.resp_dic[k]
                        if t - task["time"] > 3:
                            #del self.resp_dic[k]
                            # 记录要删除的返回值的key
                            del_key_list.append(k)

                    for k in del_key_list:
                        self.counter_timeout_resp_count += 1
                        print "del key", k
                        del self.resp_dic[k]

                    last_clear_time = time.time()

                # 每一秒钟输出一次统计信息
                if t - last_print_time >= 1:
                    self.dump()
                    self.counter_last_sec_invoke_count = self.counter_invoke_success
                    last_print_time = time.time()

        # do clean job
        print 'Exit RedisRPCClient'
        pass

def clientAFunctionA(param):
    c = param["a"] + param["b"]
    return c

def clientBFunctionB(param):
    c = param["a"] + param["b"]
    return c

def clientGetOnlineUsers(param):
    return {"infos": ["1", "2", "3"]}

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "test1":
            # client = RedisRPCClient("clientA")
            #time.sleep(2)
            # client.register_function(clientAFunctionA)
            #for i in range(5000):
            #    if client.invoke("clientB", "clientBFunctionB", "ydc") == None:
            #        print "####################################"
            client = RedisRPCClient("clientA")
            client.register_function(clientAFunctionA)
            ret = client.invoke("BDAUDIT_ACCLIENT", "get_online_user", "", async_=True)
            print ret
            while True:
                ret = client.invoke("BDAUDIT_ACCLIENT", "get_online_user", "", async_=True)
                print ret
                client.dump()
                time.sleep(1)
        elif sys.argv[1] == "test2":
            client = RedisRPCClient("clientB")
            #time.sleep(2)
            client.register_function(clientBFunctionB)
            for i in range(5000000):
                if client.invoke("clientC", "clientAFunctionC", "ydc") == None:
                    print "####################################"
            while True:
                client.dump()
                time.sleep(1)

        elif sys.argv[1] == "online":
            client = RedisRPCClient("logparser")
            #time.sleep(2)
            client.register_function(clientGetOnlineUsers)

            while True:
                a = raw_input("请输入动作(action username ip): ")
                i = a.split()
                if len(i) == 3:
                    client.invoke("suricata", "remoteEvent", {
                        "action": i[0],
                        "username": i[1],
                        "ip": i[2]
                    })



if __name__ == '__main__':
    main()
