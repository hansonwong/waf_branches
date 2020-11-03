#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
import time
import json
import shutil
import threading
import subprocess
from datetime import datetime
from logging import getLogger
from db import conn_scope
from config import config
from redis_db import redis_conn, redis_subscripe


class ScanVirus(threading.Thread):
    '''
    智能木马检测
    '''
    def __init__(self):
        super(ScanVirus, self).__init__()
        self.event = threading.Event()
        self.chn = 'upfileinfo'
        self.virus_path = '/usr/local/bluedon/www/downloads/scan_virus'
        self.cyren_cmd = '/home/cyren/ScanFile'
        self.severity_level = {'high': 2, 'medium': 1, 'low': 0}
        self.redisdb = redis_conn()

    def start(self):
        getLogger('audit').debug(self.__class__.__name__ + ' starting...')
        super(ScanVirus, self).start()
        getLogger('audit').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('audit').debug(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        getLogger('audit').info(self.__class__.__name__ + ' Exited.')

    def scan_virus(self, path):
        '''
        扫描病毒
        '''
        cmd = "%s %s" % (self.cyren_cmd, path.encode('string_escape'))
        getLogger("audit").info(cmd)
        ret = subprocess.check_output(cmd, shell=True)
        scan_result = ret.strip().split("\n")
        result = scan_result[-2].split(" = ")[1]
        getLogger("audit").info(result)
        if result == "E":  # scan error
            getLogger('audit').error("ScanFile Error: %s" % scan_result[-2])
        elif result == 'F':  # no virus
            os.remove(path)
        elif result == "T":  # virus
            self.severity = 'low'
            virus_datas = []
            for virus in scan_result[2:-2]:
                virus_result = virus.split()
                cur_severity = virus_result[2]
                virus_datas.append({"type": virus_result[0],
                                    "detail": virus_result[1],
                                    "severity": cur_severity,
                                    })
                # 以病毒信息严重等级最高的为该病毒严重等级
                if (self.severity_level.get(cur_severity, -1) >
                        self.severity_level.get(self.severity, -1)):
                    self.severity = cur_severity
            return json.dumps(virus_datas)

    def save_virus_info(self, log_data):
        '''
        保存病毒结果
        '''
        with conn_scope(**config['db']) as (_, cursor):
            cursor.execute('select * from t_scanvirus_setting')
            is_use, extend_name = cursor.fetchone()
            if not is_use:
                return
            upfile_data = dict(map(lambda x: x.split('='), log_data.split('|::|')))
            path = upfile_data['tmpname']
            path_ext = os.path.splitext(path)[1]
            if path_ext and path_ext in extend_name.split('|'):
                report = '[]'
                self.severity = 'high'  # 自定义严重等级为高
            else:
                report = self.scan_virus(path)
            if report is not None:
                file_down_path = os.path.join(self.virus_path, os.path.basename(path))
                file_time = upfile_data['time'].split()[0]
                create_time = datetime.strptime(file_time, '%d/%b/%Y:%H:%M:%S')
                sql_str = ("insert into logs.t_viruslogs(`filepath`,`uploadtime`,"
                            "`result`,`url`,`filename`,`rating`) values(%s,%s,%s,%s,%s,%s)")
                cursor.execute(sql_str, (file_down_path, create_time, report,
                                upfile_data['url'], upfile_data['realname'], self.severity))
                # shutil.move(path, file_down_path)

    def proc(self):
        with redis_subscripe(self.redisdb, self.chn) as logs:
            for log in logs:
                if self.event.isSet():
                    return
                if log['type'] == 'message':
                    self.save_virus_info(log['data'])

    def run(self):
        while 1:
            try:
                if self.event.isSet():
                    return
                self.proc()
            except Exception, e:
                getLogger('audit').error(e)
                self.redisdb = redis_conn()
                time.sleep(1)

if __name__ == '__main__':
    ScanVirus().proc()
