#!/usr/bin/python
# -*- coding:utf-8 -*-
import StringIO
import time
import threading

class BcpWriter:

    def __init__(self, filepath, time_limit, size_limit, typ=None, ct=None):
        self.time_limit = time_limit
        self.size_limit = size_limit
        self.filepath = filepath

        self.s = StringIO.StringIO()
        self.t = time.mktime(time.localtime())
        self.lock = threading.Lock()
        self.size = 0
        self.totalsize = 0
        self.time_check_counter = 0
        self.MAX_TIME_CHECK = 5

        self.logtype = typ
        self.counter = ct

    def acquire(self):
        self.lock.acquire()

    def unlock(self):
        self.lock.release()


    def write(self, str):
        #print '** write', str
        try:

            self.acquire()
            #print self.filepath
            self.s.write(str)
            ret = self.s.pos
            self.size += ret
            self.totalsize += ret
        finally:
            self.unlock()

        # increase counter, by type name
        if self.logtype is not None:
            self.counter.inc_counter(self.logtype.TYPE)
        return ret

    def size_check(self):
        try:
            self.acquire()
            #print 'pos:', self.s.pos, self.size_limit
            if self.s.pos >= self.size_limit:
                print 'pos:', self.s.pos
                self.save()
        finally:
            self.unlock()

    def time_check(self):
        try:
            self.acquire()
            self.time_check_counter += 1
            if self.time_check_counter > self.MAX_TIME_CHECK:
                self.time_check_counter = 0
                self.save()
            # now = time.mktime(time.localtime())
            # tlimi = now - self.t
            # #print tlimi, self.time_limit
            # if tlimi >= self.time_limit:
            #     self.save()
        finally:
            self.unlock()

    def save(self):

        if self.size == 0:
            return

        self.t = time.mktime(time.localtime())
        fp = open('%s.%s' % (self.filepath, long(self.t)), 'wb')
        _path = '%s.%s' % (self.filepath, long(self.t))
        if fp:
            self.s.seek(0)
            # ret = self.s.read()
            # modify
            ret = self.s.read().strip('\n')

            self.s.close()
            self.s = StringIO.StringIO()

            fp.write(ret)

            fp.close()
            self.notify_redis(_path)
            self.size = 0
        #print ret

    def notify_redis(self, path):
        if self.logtype is None:
            return
        # publish_channel to tell there is a new file
        from .redis_utils.redis_op import create_redis, publish_channel
        re = create_redis()
        if re is None:
            # log error
            print "can't open redis"
            return

        # publish to channel specified by logtype
        # print 'send %s to ch[%s]' % (path, self.logtype.redis_ch)
        publish_channel(re, self.logtype.redis_ch, path)
        re.connection_pool.disconnect()

    def close(self):
        print self.totalsize


class BcpDispatcher:
    """定时检查是否需要将信息写入bcp"""
    def __init__(self):
        self.bcpwriters = []
        self.t = threading.Thread(target = self.run)
        self.t.setDaemon(True)
        self.lock = threading.Lock()
        self.event = threading.Event()


    def acquire(self):
        self.lock.acquire()

    def unlock(self):
        self.lock.release()

    def run(self):
        while True:
            if self.event.isSet(): break
            self.acquire()
            try:
                for bcp in self.bcpwriters:
                    bcp.size_check()
                    bcp.time_check()
            except:
                # TODO: log here
                print 'BcpError'
            self.unlock()
            time.sleep(2)

    def appendBcp(self, bcpwriter):
        self.acquire()
        self.bcpwriters.append(bcpwriter)
        self.unlock()

    def start(self):
        self.t.start()

    def stop(self):
        self.event.set()
