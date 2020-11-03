#!/usr/bin/env python
# -*- coding: utf-8 -*-

import stat, os, time, re, threading, MySQLdb
from logging import getLogger
from config import config
from MySQLdb import escape_string
from db import conn_scope

class SysLog(threading.Thread):
    ''' 系统日志收集、写数据库 '''

    event = threading.Event()

    def __init__(self, ):
        super(SysLog, self).__init__(name = self.__class__.__name__)
    
    def start(self):
        getLogger('audit').debug(self.__class__.__name__+ ' starting...')
        super(SysLog, self).start()
        getLogger('audit').info(self.__class__.__name__+ ' started.')

    def stop(self):
        getLogger('audit').debug(self.__class__.__name__+ ' Exiting...')
        self.event.set()
        self.join()
        getLogger('audit').info(self.__class__.__name__+ ' Exited.')

    def proc(self):
        pass

    def run(self):
        interval  = 0
        where     = 0
        filename  = "/var/log/messages"
        rexpinfo  = re.compile(r'([0-9-: ]{19,}) (\w+) (\w+) \[(\w+)\]: (.+)')
        while 1:
            try:
                for _ in range(5):
                    time.sleep(3)
                    if self.event.isSet():
                        return
                with conn_scope(**config['dbacc']) as (conn, cursor):
                    with open(filename,'r') as fp:
                        st_size = os.stat(filename)[6]
                        if(where == 0 or where > st_size):
                            where = st_size
                            fp.seek(where)
                        else:
                            fp.seek(where)
        
                        line = fp.readline()
                        while(line):
                            match = rexpinfo.search(line)
                            if(match):
                                insertsql = "insert into t_syslogs(`time`, `program`, `Severity`, `desc`) \
                                             values('%s', '%s', '%s', '%s');" % (match.group(1), match.group(3), 
                                             match.group(4), escape_string(match.group(5)))
                                cursor.execute(insertsql)
                            where = fp.tell() 
                            line = fp.readline()
            except Exception, e:
                getLogger('audit').exception(e)


if __name__ == '__main__':
    pass
