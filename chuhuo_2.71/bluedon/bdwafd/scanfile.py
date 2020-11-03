#!/usr/bin/env python
#-*-coding:utf-8-*-
import os
import threading
import json
import time
from logging import getLogger
from config import config
from db import conn_scope

def filenameparser(filename):
    result={}
    words = filename.split("__",2)
    getLogger('main').info("ScanFile filename:{0}".format(words))
    result["uploadtime"] = int(words[0])
    result["url"] = words[1].replace("-","/")
    result["filename"] = words[2]
    return result


class ScanFile(threading.Thread):
    def __init__(self):
        super(ScanFile, self).__init__(name = self.__class__.__name__)
        self.prepath = '/tmp/haoliang/'
        self.path = '/root/uploadfile'
        self.down_path = "/usr/local/bluedon/checkFile/"
        self.virus_path = "/usr/local/bluedon/checkFile/viruesFile/"
        self.unknown_path = "/usr/local/bluedon/checkFile/unknownFile/"
        if not os.path.exists(self.down_path):
            os.makedirs(self.down_path)
        if not os.path.exists(self.virus_path):
            os.makedirs(self.virus_path)
        if not os.path.exists(self.unknown_path):
            os.makedirs(self.unknown_path)
        self.event = threading.Event()
        self.fifo = '/tmp/bdwaf.fifo'

    def start(self):
        getLogger('main').info(self.__class__.__name__ + ' starting...')
        super(ScanFile, self).start()
        getLogger('main').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('main').info(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__ + ' Exited.')

    def scanAndSave(self, path):
        ret = os.popen("/usr/local/bluedon/cyren/ScanFile %s" % path)
        file_name = path.split("/")[-1]
        #print "xxxxxxxxxxxxxxxxxxx"
        #print file_name
        file_down_path = self.unknown_path + file_name
        createTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(path)))
        results = ret.read().strip().split("\n")
        #print results
        temp_result = results[-2]
        result = temp_result.split(" = ")
        if result[1] == "E":
            getLogger('main').exception("ScanFile Error: %s" % temp_result)
        else:
            file_type = 0
            with conn_scope(**config['db']) as (conn, cursor):
                virus_datas = []
                if result[1] == "T":
                    file_type = 1
                    file_down_path = self.virus_path + file_name
                    for virus in results[2:-2]:
                        virus_result = virus.split(" ")
                        virus_type = virus_result[0]
                        virus_detail = virus_result[1]
                        virus_level = virus_result[-1]
                        virus_datas.append({"type": virus_type, "detail": virus_detail, "severity": virus_level})
                    report = json.dumps(virus_datas)
                    sql_str = "insert into logs.t_viruslogs(`filePath`, `createTime`, `type`, `virus`)" \
                              " values(%s, %s, %s, %s)"
                    cursor.execute(sql_str, (file_down_path, createTime, file_type, report))
                    sql_str2 = "insert into logs.t_uploadedfilelogs(reporttime,url,filename,uploadtime,type,rating,result)" \
                               " values(%s,%s,%s,%s,%s,%s,%s)"
                    resultofnameparsed = filenameparser(file_name)
                    reporttime = int(time.time())
                    cursor.execute(sql_str2, (reporttime, resultofnameparsed["url"], resultofnameparsed["filename"],
                                              resultofnameparsed["uploadtime"], 1, "High", report))


            cmdstr = "mv %s %s" % (path, file_down_path)
          #  cmd=cmdstr.replace("\\","\\\\")
            cmd = cmdstr
            os.popen(cmd)
            if file_type == 0:
               # os.popen("echo 'CMD_CUCKOO_FILE|%s' >> %s" % (file_down_path.replace("\\","\\\\"), self.fifo))
                os.popen("echo 'CMD_CUCKOO_FILE|%s' >> %s" % (file_down_path, self.fifo))

    def proc(self):
        if os.path.exists(self.prepath):
            for file_ in os.listdir(self.prepath):
                try:
                    os.system("lua read_uploadfile.lua %s" % file_)
                except Exception, e:
                    #getLogger('main').exception(e)
                    #print e
                    pass
                
        for path in sorted(os.listdir(self.path)):
            getLogger('main').info("ScanFile path:{0}".format(path))
            path = self.path + "/" + path
            self.scanAndSave(path)

    def run(self):
        while 1:
            try:
                if self.event.isSet():
                    break
                time.sleep(10)
                self.proc()
            except Exception, e:
                getLogger('main').exception(e)


if __name__ == "__main__":
    pass
