#!/usr/bin/env python
# coding=utf-8



""" 智能防护--> 反向扫描 """


import os
import re
import json
import time
import commands
import time
import datetime
import linecache
import threading
from IPy import IP
from Queue import Queue

from db.config1 import  search_data, execute_sql, mkdir_file
from utils.logger_init import logger_init
from utils.mask_transition import exchange_mask
from system.ha import init_tenv


#FILE_PATH = '/etc/snort'
#LOG_PATH = '/etc/snort/log'
COMMANDS = commands.getstatusoutput

FLAG = True
STOP_SRC = None
STOP_TIME = None
php_to_python_revscanfile=''


logger = logger_init('REVSCAN', '/usr/local/bluedon/log/revscan.log', 'DEBUG')


def run_revscan_client():
    #cmd = '%s -c %s -l %s --daq dpdk' %(FILE_PATH + '/bin/snort',
    #      FILE_PATH + '/snort.conf', LOG_PATH)
    cmd = '/etc/snort/bin/snort -c /etc/snort/snort.conf -l /etc/snort/log --daq dpdk'
    (status, output) = COMMANDS(cmd)

class REVSCAN_THREAD(threading.Thread):
    """ 多线程, 用于处理反向拍照和日志分析还有拍照来源ip """

    def __init__(self, name_1, name_2,data,content,reset):
        super(REVSCAN_THREAD, self).__init__()
        self.th_1 = threading.Thread(target=name_1)
        self.name_2 = name_2
        self.data = data
        self.content = content
        self.reset = reset

    def run(self):
        self.th_1.start()
        if self.reset:
           open('/tmp/fifo/%s'%self.data['Revscanfile'],'w').close()
           fw=open('/tmp/fifo/revscan', 'w')
           print>>fw,self.content
           fw.close()
        global FLAG
       # print "#####################",FLAG
        self.th_2 = threading.Thread(target=self.name_2)
        self.th_2.start()
        # self.th_2.join()
        while FLAG:
            res = search_process()
            if res == 0:
                time.sleep(10)
                FLAG = False

def search_process():

    """ 存在进程返回0, 不存在返回1 """

    PROCESS = "ps -ef|grep snort|grep -v grep|grep -v PPID|awk '{ print $8}'"
    (s, output) = COMMANDS(PROCESS)
    snort_process = output.split('\n')
    snort_process = set(snort_process)
    snort = ['/etc/snort/bin/snort']
    snort = set(snort)

    if snort & snort_process:
       status = 1
    else:
       status = 0
    return status


def revscan_conf_file(data):

    scan_ini = {}
    scan_ini['proto'] = str(data['protocol']).strip() or 'all'
    way = { 'nmap':   'portscan',
            'normal': 'portsweep',
            'wz':     'decoy_portscan',
            'fbs':    'distributed_portscan',
            'all':    'all',
            '':       'all'}
    scan_ini['type'] = way[data['way'].strip()] or 'all'

    scan_ini['level'] = data['level'].strip() or 'low'
    if data['level'].strip()=='mid':
       scan_ini['level'] = 'medium'

    for k,v in data.items():
       if k=='check_ip' or k=='src_ip' or k=='des_ip':
          ip_list = []
          for tmp in v.split(','):
              if not tmp:
                 break

              mask=tmp.split('/')[-1]
              if '.' in mask and len(mask)==2:
                 mask_int=exchange_mask(mask)
                 tmp=tmp.replace(mask,str(mask_int))
              ip_list.append(tmp)
          scan_ini[k]  = ','.join(ip_list)

    tenv = init_tenv()
    tenv.get_template('snort').stream(scan_ini = scan_ini).dump('/etc/snort/snort.conf')


def read_file(filepath):
    """ 读取文件内容"""
    try:
        return linecache.getlines(filepath)
    except Exception as e:
        logger.debug(e)
        return []


def write_file(filepath, con):
    """ 把数据写入文件 """

    try:
        with open(filepath, 'w') as fp:
            fp.write(con)
    except Exception as e:
        logger.debug(e)


# 轮询日志文件写入队列
def loop_read_file(filename, q):

    if mkdir_file('/usr/local/bluedon/conf/revscan', 'file'):
        con = json.dumps({'size': 0})
        write_file('/usr/local/bluedon/conf/revscan', con)

    with open('/usr/local/bluedon/conf/revscan') as f:
        f.seek(0)
        seek_position = json.load(f).get('size')

    while FLAG:
        with open(filename) as f:
            f.seek(seek_position)
            lines = f.read().split('\n')
            offset = len(lines.pop(-1))
            seek_position = f.tell() - offset
            write_file('/usr/local/bluedon/conf/revscan', json.dumps({'size': seek_position}))
            for line in lines:
                q.put(line)
        time.sleep(5)
    logger.debug("loop read file over!")


# 整合队列中的日志
def loop_handle_queue(q):
    while FLAG:
        lines = []
        while True:
            try:
                line = q.get(timeout=10)
            except Exception as e:
                break
            if line:
                lines.append(line)
            elif len(line) < 1 and len(lines) > 7:
                handle_log(lines)
                break
    logger.debug("loop handle queue over!")


# 处理一个完整的日志
def handle_log(lines):
    field_dict = {}
    for i, line in enumerate(lines):
        # 时间
        if line.startswith('Time:'):
            Time = line.split(':', 1)[1].split('.')[0].strip().replace('/',' ').replace('-',' ').replace(':',' ').split(' ')
            year = time.strftime("%Y", time.localtime())
            dateC=datetime.datetime(int(year),int(Time[0]),int(Time[1]),int(Time[2]),int(Time[3]))
            timestamp=time.mktime(dateC.timetuple())
            field_dict['iTime']=timestamp

        # 来源地址 and 目的地址 and 扫瞄类型
        elif '->' in line and '(portscan)' in line:
            source_target=[]
            for tmp in line.split():
                try:
                    ip = IP(tmp)
                    source_target.append(ip)
                except Exception as e:
                    pass
            field_dict['sSourceAddr'] = source_target[0]
            field_dict['sTargetAddr'] = source_target[1]
            portscan = line.split('(portscan)')[1].strip()
            field_dict['sScanType'] = portscan
        # 链接数
        elif line.startswith('Connection Count:'):
            field_dict['iConnectNum'] = line.split(':')[1].strip()
        # 地址数
        elif line.startswith('IP Count:'):
            field_dict['iAddressNum'] = line.split(':')[1].strip()
        # 端口数
        elif line.startswith('Port/Proto Count:'):
            field_dict['iPortNum'] = line.split(':')[1].strip()
        # 端口范围
        elif line.startswith('Port/Proto Range:'):
            field_dict['iPortRange'] = line.split(':', 1)[1].strip()
        elif line.startswith('Scanning trace:'):
            scanning_trace_string=[]
            for tmp in lines[i+1:]:
                if len(tmp)>1:
                    scanning_trace_string.append(tmp)
                else:
                    break
            field_dict['scanning_trace'] = ','.join(scanning_trace_string)

    sql = 'INSERT INTO m_tbprotected_log(id,iTime, sScanType, sSourceAddr, \
        sTargetAddr, iConnectNum, iAddressNum, iPortNum, iPortRange,sDetail) \
        VALUES (Null,"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s","%s")'
    global STOP_TIME, STOP_SRC

    # 如果勾选了阻止攻击来源, 则设置iptables规则
    ipet_rule = lambda v4_or_v6,addr,timeout:'/usr/local/sbin/ipset add scan_blist_v4 "%s" timeout "%s"'
    if 1:
        if STOP_SRC == '1':
            scan_cmd = ''
            if IP(field_dict['sSourceAddr']).version() == 4:
                scan_cmd = '/usr/local/sbin/ipset add scan_blist_v4 {addr}  {timeout}'\
                    .format(addr=field_dict['sSourceAddr'],timeout='timeout %s'%str(int(STOP_TIME)*60) if STOP_TIME is not None else 'timeout 0')
            if IP(field_dict['sSourceAddr']).version() == 6:
                scan_cmd = '/usr/local/sbin/ipset add scan_blist_v6 {addr} {timeout}'\
                    .format(addr=field_dict['sSourceAddr'],timeout='timeout %s'%str(int(STOP_TIME)*60) if STOP_TIME is not None else 'timeout 0')
                #scan_cmd = '/usr/local/sbin/ipset add scan_blist_v6 "%s" timeout "%s"'%(item['sSourceAddr'],int(STOP_TIME)*60)
            if scan_cmd:
                (status, output) = COMMANDS(scan_cmd)
           #getLogger('REVSCAN').debug('%s  %s' %(scan_cmd, output))
        try:
            sql_log = sql % (field_dict['iTime'], field_dict['sScanType'], field_dict['sSourceAddr'], field_dict['sTargetAddr'], field_dict['iConnectNum'], \
                             field_dict['iAddressNum'], field_dict['iPortNum'], field_dict['iPortRange'], field_dict['scanning_trace'])
            execute_sql(sql_log)
        except Exception as e:
            logger.error(field_dict)


# 反扫描日志文件处理
def revscan_log_file_new():
    """
    开启两个线程，一个负责轮询日志文件，将读取的内容写入队列，另一个负责读取列队中的内容
    :return:
    """
    q = Queue(maxsize=1024*1024)
    threading.Thread(target=loop_read_file, args=("/etc/snort/log/log", q)).start()
    threading.Thread(target=loop_handle_queue, args=(q, )).start()


def revscan_log_file():
    """
    分析反向扫描日志文件, 提取相应字段并入库
    """

    # 判断是否存在revscn文件, 不存在则创建
    if mkdir_file('/usr/local/bluedon/conf/revscan', 'file'):
        con = json.dumps({'size': 0})
        write_file('/usr/local/bluedon/conf/revscan', con)

    f_record = open('/usr/local/bluedon/conf/revscan','r')
    res = eval(f_record.read()) or {'size': 0}
    f_record.close()

    file_now_size = os.path.getsize('/etc/snort/log/log')
    if int(res.get('size', 0)) == file_now_size:
        logger.debug('日志文件没有新增的内容')
        return
    if int(res.get('size', 0))>file_now_size:
        con = json.dumps({'size': file_now_size})
        write_file('/usr/local/bluedon/conf/revscan', con)
        return

    # 分析log文件, 提取相应内容
    field_list = []
    with open('/etc/snort/log/log','r') as f:
        seek_position = int(res.get('size'))
        # if seek_position>10:
        #     seek_position = seek_position-10
        f.seek(seek_position)
        lines = f.read(file_now_size - seek_position).split('\n')
        con = json.dumps({'size': file_now_size})
        write_file('/usr/local/bluedon/conf/revscan', con)

    field_dict = {}
    for i,line in enumerate(lines):
        # 时间
        if line.startswith('Time:'):
            Time = line.split(':', 1)[1].split('.')[0].strip().replace('/',' ').replace('-',' ').replace(':',' ').split(' ')
            year = time.strftime("%Y", time.localtime())
            dateC=datetime.datetime(int(year),int(Time[0]),int(Time[1]),int(Time[2]),int(Time[3]))
            timestamp=time.mktime(dateC.timetuple())
            field_dict['iTime']=timestamp

        # 来源地址 and 目的地址 and 扫瞄类型
        elif '->' in line and '(portscan)' in line:
            source_target=[]
            for tmp in line.split():
                try:
                    ip = IP(tmp)
                    source_target.append(ip)
                except Exception as e:
                    pass
            field_dict['sSourceAddr'] = source_target[0]
            field_dict['sTargetAddr'] = source_target[1]
            portscan = line.split('(portscan)')[1].strip()
            field_dict['sScanType'] = portscan
        # 链接数
        elif line.startswith('Connection Count:'):
            field_dict['iConnectNum'] = line.split(':')[1].strip()
        # 地址数
        elif line.startswith('IP Count:'):
            field_dict['iAddressNum'] = line.split(':')[1].strip()
        # 端口数
        elif line.startswith('Port/Proto Count:'):
            field_dict['iPortNum'] = line.split(':')[1].strip()
        # 端口范围
        elif line.startswith('Port/Proto Range:'):
            field_dict['iPortRange'] = line.split(':', 1)[1].strip()
        elif line.startswith('Scanning trace:'):
            scanning_trace_string=[]
            for tmp in lines[i+1:]:
                if len(tmp)>1:
                    scanning_trace_string.append(tmp)
                else:
                    break
            field_dict['scanning_trace'] = ','.join(scanning_trace_string)

            if field_dict:
               field_list.append(field_dict)
            field_dict = {}

    sql = 'INSERT INTO m_tbprotected_log(id,iTime, sScanType, sSourceAddr, \
        sTargetAddr, iConnectNum, iAddressNum, iPortNum, iPortRange,sDetail) \
        VALUES (Null,"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s","%s")'
    global STOP_TIME, STOP_SRC

    # 如果勾选了阻止攻击来源, 则设置iptables规则
    ipet_rule = lambda v4_or_v6,addr,timeout:'/usr/local/sbin/ipset add scan_blist_v4 "%s" timeout "%s"'
    if 1:
        for item in field_list:
            if STOP_SRC == '1':
                scan_cmd = ''
                if IP(item['sSourceAddr']).version() == 4:
                    scan_cmd = '/usr/local/sbin/ipset add scan_blist_v4 {addr}  {timeout}'\
                        .format(addr=item['sSourceAddr'],timeout='timeout %s'%str(int(STOP_TIME)*60) if STOP_TIME is not None else 'timeout 0')
                if IP(item['sSourceAddr']).version() == 6:
                    scan_cmd = '/usr/local/sbin/ipset add scan_blist_v6 {addr} {timeout}'\
                        .format(addr=item['sSourceAddr'],timeout='timeout %s'%str(int(STOP_TIME)*60) if STOP_TIME is not None else 'timeout 0')
                    #scan_cmd = '/usr/local/sbin/ipset add scan_blist_v6 "%s" timeout "%s"'%(item['sSourceAddr'],int(STOP_TIME)*60)
                if scan_cmd:
                    (status, output) = COMMANDS(scan_cmd)
               #getLogger('REVSCAN').debug('%s  %s' %(scan_cmd, output))
            try:
                sql_log = sql % (item['iTime'], item['sScanType'], item['sSourceAddr'], item['sTargetAddr'], item['iConnectNum'],\
                             item['iAddressNum'],item['iPortNum'], item['iPortRange'],item['scanning_trace'])
                execute_sql(sql_log)
            except Exception as e:
                logger.error(item)

    if os.path.getsize('/etc/snort/log/log')>1000**3:
       open('/etc/snort/log/log','w').close()
       con = json.dumps({'size': 0})
       write_file('/usr/local/bluedon/conf/revscan', con)

def process_revscan(action, data,reset=True):

    global STOP_TIME, STOP_SRC,php_to_python_revscanfile,FLAG
    if data:
       if data.has_key('stop_time'):

          STOP_TIME = int(data['stop_time']) if data['stop_time'] else 0
       if data.has_key('stop_src'):
          STOP_SRC = str(data['stop_src'])
       if reset:
          php_to_python_revscanfile = data['Revscanfile']

    if action =='start':
        FLAG = True
        revscan_conf_file(data)
        content=json.dumps({'start': 1})
        rev = REVSCAN_THREAD(run_revscan_client, revscan_log_file_new,data,content,reset)
        rev.start()

    elif action=='restart':
         (s, o) = COMMANDS('killall snort')
         while 1:
            re = search_process()
            if not re:
               break
         time.sleep(4)
         FLAG = True
         os.system('/usr/local/sbin/ipset flush scan_blist_v4')
         os.system('/usr/local/sbin/ipset flush scan_blist_v6')
         revscan_conf_file(data)
         content=json.dumps({'start': 1})
         rev = REVSCAN_THREAD(run_revscan_client, revscan_log_file_new,data,content,reset)
         rev.start()

    elif action == 'stop':
         os.system('/usr/local/sbin/ipset flush scan_blist_v4')
         os.system('/usr/local/sbin/ipset flush scan_blist_v6')
         content = json.dumps({'start': 0})
         COMMANDS('killall snort')
         while 1:
            re = search_process()
            if not re:
               break
         open('/tmp/fifo/%s'%data['Revscanfile'],'w').close()
         fw=open('/tmp/fifo/revscan','w')
         print>>fw,content
         fw.close()


    elif action == 'refresh':
        res = search_process()
        if res == 1:
           content = json.dumps({'start': 1})
           fw=open('/tmp/fifo/revscan','w')
           print>>fw,content
           fw.close()
        else:
           content = json.dumps({'start': 0})
           fw=open('/tmp/fifo/revscan','w')
           print>>fw,content
           fw.close()
        if php_to_python_revscanfile:
           os.system('rm -f /tmp/fifo/%s'%php_to_python_revscanfile)

if __name__ == '__main__':
    #revscan_conf_file(data)
    #revscan_conf_file(data)
    revscan_log_file()
    f = open()
    f.readlines()
