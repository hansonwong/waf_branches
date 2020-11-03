#!/usr/bin/env python
# coding=utf-8


""" 智能防护--> 反向拍照 """

import os
import json
import commands
import codecs
import threading
import time
import pyinotify
from logging import getLogger
from db.config1 import  search_data, execute_sql
from utils.logger_init import logger_init
from system.ha import init_tenv
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


COMMANDS = commands.getstatusoutput
FLAG = True
RUN_LOG_THREAD = False
php_to_python_file=''
logger = logger_init('REVCAMERA', '/usr/local/bluedon/log/revcamera.log', 'DEBUG')
lock = threading.RLock()


# 触发原因对应的中文
reason_dict = { 'dionaea':   '1',#蜜罐
               'mointor':           '32',#异常监控',
               'scan':              '2',#反扫描',
               'invasion':  '64',#入侵防御',
               'web_attract':       '4',#web防护',
               'ddos':              '8',#DDOS防护',
               'virus':     '16',#病毒防护',
               'leakage':      '128',#信息泄露'
               }


def run_revcamera_client():
    # cmd = '/etc/antidetect/antidet -c /etc/antidetect/antidet.ini -l /etc/antidetect/log -s /etc/antidetect'
    cmd = 'systemctl start revcamera'
    print cmd
    (status, output) = COMMANDS(cmd)

class Filehandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        logger.debug('modify:%s' % event.pathname)
        revcamera_log_file(event.pathname)

    def process_IN_CREATE(self, event):
        logger.debug('create:%s' %event.pathname)


def log_file_monitor():
    wm = pyinotify.WatchManager()
    wm.add_watch('/etc/antidetect/log', pyinotify.ALL_EVENTS, rec=True)
    eh = Filehandler()
    notifier = pyinotify.ThreadedNotifier(wm, eh)
    return notifier


def loop_check_log(files):
    global FLAG
    global RUN_LOG_THREAD
    while FLAG:
        cur_files = os.listdir('/etc/antidetect/log')
        logger.debug(cur_files)
        logger.debug(files)
        for filename in cur_files:
            if filename in files or os.path.getsize('/etc/antidetect/log/%s' % filename) < 10 or filename.startswith('.'):
                continue
            else:
                logger.debug("add log %s" % filename)
                try:
                    revcamera_log_file('/etc/antidetect/log/%s' % filename)
                except Exception as e:
                    logger.error("add log %s fail:%s" % (filename, e))
                files.append(filename)
        time.sleep(5)
    RUN_LOG_THREAD = False


class REVCAMERA_THREAD(threading.Thread):

    """ 多线程, 用于处理反向拍照和日志分析还有拍照来源ip """

    def __init__(self, run_revcamera_client, revcamera_log_file,data,content,reset):

        super(REVCAMERA_THREAD, self).__init__()
        self.revcamera_cmd = threading.Thread(target = run_revcamera_client)
        self.data    = data
        self.content = content
        self.reset   = reset
        self.handle_log = revcamera_log_file

    def run(self):
        origin_log_files = os.listdir("/etc/antidetect/log")
        self.revcamera_cmd.start()

        global FLAG
        global RUN_LOG_THREAD
        if self.reset:
            open('/tmp/fifo/%s'%self.data['Revcamerafile'],'w').close()
            fw2=open('/tmp/fifo/revcamera', 'w')
            print>>fw2,self.content
            fw2.close()
            # 检查当前是否有日志处理线程存在
            try:
                lock.acquire()
                if not RUN_LOG_THREAD:
                    threading.Thread(target=self.handle_log, args=(origin_log_files, )).start()
                    RUN_LOG_THREAD = True
            finally:
                lock.release()
            while FLAG:
                res = search_process()
                if res == 0:
                    FLAG = False
                    break
                time.sleep(10)


def search_process():

    """ 存在进程返回0 不存在返回1 """

    PROCESS = "ps -ef|grep antidet|grep -v grep|grep -v PPID|awk '{ print $8}'"
    (s, output) = COMMANDS(PROCESS)
    process=output.split('\n')
    process=set(process)
    antidet=['/etc/antidetect/antidet']
    antidet=set(antidet)
    if process & antidet:
        status = 1
    else:
        status = 0
    return status


def revcamera_ini_file(data):

    content_ini = {}
    content_ini['start'] = '1'
    content_ini['task']  = str(data['task_num']) or '0'
    content_ini['queue'] = str(data['queue_num']) or '0'

    photo_origin = {'1': 'b_dionaea',     '2': 'b_scan',
                    '4': 'b_web_attract', '8': 'b_ddos',
                    '16': 'b_virus',      '32': 'b_mointor',
                    '64': 'b_invasion',   '128': 'b_leakage'
                   }
   # if data['src']:
    origin_set = set(data['src'].split(','))or set([''])
    origin_list = []
    for key in photo_origin.keys():
        if set([key]) & origin_set:
            origin_list.append(photo_origin[key] + ' 1')
        else:
            origin_list.append(photo_origin[key] + ' 0')
    content_ini['photo_origin'] = origin_list

    #if data['content']:
    scan_set = set(data['content'].split(',')) or set([''])
    photo_content_dict = {'1': 'scan_host',
                          '2': 'scan_port',
                          '8': 'scan_router'}
    photo_content = []
    for key in photo_content_dict.keys():
        if set([key]) & scan_set:
            photo_content.append(photo_content_dict[key] + ' 1')
        else:
            photo_content.append(photo_content_dict[key] + ' 0')
    content_ini['photo_content'] = photo_content

    tenv = init_tenv()
    tenv.get_template('antidet').stream(content_ini=content_ini).dump('/etc/antidetect/antidet.ini')



def revcamera_log_file(filename):
    """
    分析反向拍照日志文件, 提取相应字段入库
    """
    print '*************log****************'
    if 1:
        fp = codecs.open(filename, 'r', 'utf-8')
        lines = fp.readlines()
        fp.close()
        field_dict = {
            'iTime': '',
            'sTrigerReason': '',
            'sTargetAddr': '',
            'sHostType': [],
            'sDistance': '',
            'sTimeDelay': '',
            'sDetail': [],
            'sFileName': '',
            }
        field_dict['sFileName'] = os.path.basename(filename)
        for line in lines:
            # 目的地址
            if not field_dict['sTargetAddr'] and line.startswith('addrip:'):
                field_dict['sTargetAddr'] = line.split(':')[1].replace('\n', '')
            # 触发原因
            elif not field_dict['sTrigerReason'] and line.startswith('trigger_reason:'):
                key = line.split(':')[1].replace('\n', '').strip()
                field_dict['sTrigerReason'] = reason_dict.get(key, key)
            # 主机类型
            elif len(field_dict['sHostType'])<=2 and line.startswith('osmatch:'):
                field_dict['sHostType'].append(line.split(':', 1)[1].replace('\n', ''))
            # 距离
            elif not field_dict['sDistance'] and line.startswith('distance:'):
                field_dict['sDistance'] = line.split(':')[1].replace('\n', '')
            # 时延
            elif not field_dict['sTimeDelay'] and line.startswith('latency:'):
                field_dict['sTimeDelay'] = line.split(':')[1].replace('\n', '')
            # 记录日志时间
            elif not field_dict['iTime'] and line.startswith('revcamera_dtime:'):
                field_dict['iTime'] = line.split(':')[1].replace('\n', '')
            # 详细操作
            elif line.startswith('portid:'):
                field_dict['sDetail'].append(line.replace('\n', ''))

        #portid = '\n'.join(portid)
        field_dict['sDetail'] = '\n'.join(field_dict['sDetail'])
        field_dict['sHostType']='\n'.join(field_dict['sHostType'])
        try:
            sql = """INSERT INTO m_tbrevcamera_log (iTime, sTrigerReason, sTargetAddr,
                  sHostType, sDistance, sTimeDelay, sDetail, sFileName)
                  VALUES (%s, '%s', '%s', '%s', '%s', '%s', '%s', '%s')""" % (float(field_dict['iTime']),
                  field_dict['sTrigerReason'], field_dict['sTargetAddr'], field_dict['sHostType'], field_dict['sDistance'],
                  field_dict['sTimeDelay'], field_dict['sDetail'], field_dict['sFileName'])
            execute_sql(sql)
        except Exception as e :
            print e

    print "**************end log*****************"


def process_revcamera(action, data,reset=True):

    """
    主函数
    启动反向拍照时，将其在/etc/antidetect/log产生的日志入表m_tbrevcamera_log，停止反向拍照方停止日志入表
    启动反向拍照：/etc/antidetect/antidet -c /etc/antidetect/antidet.ini -l /etc/antidetect/log -s /etc/antidetect
    停止反向拍照：/etc/antidetect/antidet stop
    """

    global FLAG,php_to_python_file

    if reset:
        if data:
            php_to_python_file=data['Revcamerafile']

    if action == 'start':
        FLAG = True
        revcamera_ini_file(data)
        content = json.dumps({action: 1})
        rev = REVCAMERA_THREAD(run_revcamera_client, loop_check_log,data,content,reset)
        rev.start()

    elif action == 'restart':
        cmd ='systemctl stop revcamera'
        COMMANDS(cmd)

        while 1:
          res = search_process()
          if not res :
             break

        FLAG = True
        revcamera_ini_file(data)
        content = json.dumps({'start': 1})
        rev = REVCAMERA_THREAD(run_revcamera_client, loop_check_log,data,content,reset)
        rev.start()

    elif action == 'stop':
        cmd ='systemctl stop revcamera'
        COMMANDS(cmd)
        content = json.dumps({'start': 0})
        while 1:
          res = search_process()
          if not res :
             break

        if reset:
           fw2=open('/tmp/fifo/revcamera', 'w')
           print>>fw2,content
           fw2.close()
           open('/tmp/fifo/%s'%data['Revcamerafile'],'w').close()


    elif action == 'refresh':
        res = search_process()

        if res == 1:
           content=json.dumps({'start': 1})
           fw = open('/tmp/fifo/revcamera', 'w')
           print>>fw,content
        else:
           content=json.dumps({'start': 0})
           fw = open('/tmp/fifo/revcamera', 'w')
           print>>fw,content

        if php_to_python_file:
           os.system('rm -f /tmp/fifo/%s'%php_to_python_file)

        fw.close()


if __name__ == '__main__':
   data = {"state":"1","action":"addtobw","src":"1,2,4,16","forbid_time":"1","queue_num":"3","content":"1","task_num":"5","Revcamerafile":"revcamera_1465868109.conf"}
   revcamera_ini_file(data)

