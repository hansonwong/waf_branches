#!/usr/bin/env python
# coding=utf-8

import os
import sys
import csv
import json
import signal
import codecs
import threading
from multiprocessing import Process
from utils.log_logger import rLog_dbg, rLog_err
from db.config1 import fetchall_sql as fcal_3307
from db.config1 import fetchone_sql as fetch_3307
from db.config1 import execute_sql as exec_3307

"""
    Need db/config1.py use DB1 as Mysql connection parameter
"""

FWLOG_DBG = lambda x : rLog_dbg('export_to_csv', x)
FWLOG_ERR = lambda x : rLog_err('export_to_csv', x)
CMDLOG_ERR = lambda x : rLog_err('export_to_csv_cmd', x)
# FWLOG_DBG = lambda x : x
# FWLOG_ERR = lambda x : x
# CMDLOG_ERR = lambda x : x

CSV_PATH = r'/tmp/fw_log_export_csv/'
CMD_RM = lambda x : '/usr/bin/rm -f {}'.format(x)
CMD_RM_PATH = lambda x : '/usr/bin/rm -fr {}'.format(x)
CMD_MKDIR = lambda x : '/usr/bin/mkdir -p {}'.format(x)
CMD_TAR = lambda x, y, z : '/usr/bin/tar czvf {t} -C {s} {f} --index-file=/dev/null'.format(t=x, s=y, f=z)
# CMD_TAR = lambda x, y : '/usr/bin/tar czvf {t} {s} --index-file=/dev/null'.format(t=x, s=y)

ST_RUNNING = 'running'
ST_STOP = 'stop'
ST_DONE = 'done'

INSERT_SQL = ('INSERT INTO m_tbexport_csv(iTime, sFilename, sPath, sCondition, sStatus, iPID) '
              'values("{ti}", "{fn}", "{pt}", "{cd}", "{st}", "{pid}")')

NEW_TASK_SQL = ('UPDATE m_tbexport_csv SET iTime="{ti}", sFilename="{fn}", sPath="{pt}", sCondition="{cd}", sStatus="{st}", iPID="{pid}" WHERE id={id};')

UPDATE_SQL = ('UPDATE m_tbexport_csv SET sStatus="{st}", iPID="{pid}" WHERE id="{id}"')
UPDATE_STOP_SQL = ('UPDATE m_tbexport_csv SET sStatus="{st}", iPID="0" WHERE iPID="{pid}"')


key_name = {
    'm_tblog_app_admin' :{
        'id':'ID',
        'iTime':'时间',
        'sAppName':'应用名称',
        'sSourceIP':'源地址',
        'sProtocol':'协议',
        'sTargetIP':'目标地址',
        'sAction':'动作',
        'iCount':'统计',
    },

    'm_tblog_ddos' :{
        'id':'ID',
        'iTime':'时间',
        'sEventName':'事件名称',
        'sSourceIP':'源地址',
        'sThreshold':'阈值',
        'sTargetIP':'目标地址',
        'sStatus':'状态',
        'iCount':'统计',
    },

    'm_tblog_evil_code' :{
        'id':'ID',
        'iTime':'时间',
        'sViruesName':'病毒名称',
        'sSourceIP':'源地址',
        'sProtocol':'协议',
        'sTargetIP':'目标地址',
        'sStatus':'状态',
        'sLogLevel':'日志等级',
        'sFileName':'文件名',
        'sUserName':'用户名',
        'iCount': '统计'
    },

    'm_tblog_firewall' :{
        'id':'ID',
        'iTime':'时间',
        'sInputPort':'入网口',
        'sOutPort':'出网口',
        'sSourceAddr':'源地址',
        'sSourcePort':'源端口',
        'sProtocol':'协议',
        'sTargetAddr':'目标地址',
        'sTargetPort':'目标端口',
        'sAction':'动作',
        'iCount':'统计',
    },

    'm_tblog_info_leak' :{
        'id':'ID',
        'iTime':'时间',
        'sFileKeywork':'文件/关键字',
        'sFilterType':'过滤类型',
        'sSourceIP':'源地址',
        'sProtocol':'协议',
        'sTargetIP':'目标地址',
        'sStatus':'状态',
        'iCount':'统计',
    },

    'm_tblog_ips' :{
        'id':'ID',
        'iTime':'时间',
        'sEventName':'事件名称',
        'sSourceIP':'源地址',
        'sProtocol':'协议',
        'sTargetIP':'目标地址',
        'sStatus':'状态',
        'sLogName':'log文件名称',
        'sRuleID':'规则ID',
        'sGrade':'风险等级',
        'sDesc':'描述',
        'sRuleType':'规则分类',
        'iCount':'统计',
     },

    'm_tblog_url_visit' :{
        'id':'ID',
        'iTime':'时间',
        'sUrl':'url地址',
        'sSourceIP':'源地址',
        'sWebType':'网站类型',
        # 'sTargetIP':'目标地址',
        'sAction':'动作',
        'iCount':'统计',
    },

    'm_tblog_webapplication' :{
        'id':'ID',
        'iTime':'时间',
        'sEventName':'事件名称',
        'sSourceIP':'源地址',
        'sBugType':'漏洞类型',
        'sTargetIP':'目标地址',
        'sStatus':'状态',
        'sSeverity':'    风险等级',
        'iCount':'统计',
    },

    'm_tblog_wifi_audit' :{
        'id':'ID',
        'iTime':'时间',
        'sShareHost':'共享主机',
        'sTerminal':'共享上网主机',
        'sTableName':'表名',
        'iCount':'统计',
   }
}

import time
import datetime
import collections
def timestamp_parser(st, et):
    """
        Description:
            from st(start time) to et(end time), figure out the date and st and
            et of every date
        INPUT:
            st: start time
            et: end time
        OUTPUT:
            type: dict
            format: {date0: (st, et), date1: (st, et)...dateN: (st, et)}
    """
    _date = lambda x : x.strftime("%Y%m%d")
    _ts = lambda x : time.mktime(x.timetuple())
    _st_ts = lambda x : _ts(datetime.datetime.combine(x, datetime.time.min))
    _et_ts = lambda x : _ts(datetime.datetime.combine(x, datetime.time.max))

    # container of start/end time for every date
    dad = collections.OrderedDict()

    st = int(st)
    et = int(et)

    if st > et:
        # log here
        FWLOG_ERR('[timestamp_parser]input error: End time is less than Start time')
        return



    ds = datetime.datetime.fromtimestamp(st)
    de = datetime.datetime.fromtimestamp(et)

    dt = de - ds
    if dt.days == 0:
        # just one day
        dad[_date(ds)] = (st, et)

    else:
        # start date
        dad[_date(ds)] = (st, _et_ts(ds))

        st_day = ds
        for d in range(dt.days):
            next_d = st_day +  datetime.timedelta(days=1)
            dad[_date(next_d)] = (_st_ts(next_d), _et_ts(next_d))
            st_day = next_d


        # end date
        dad[_date(de)] = (_st_ts(de), et)
    return dad

def signal_handler_stop(sig, var):
    """ hanlder when receive stop signal """
    myPID = os.getpid()
    # find output path of process of THIS PID
    find_sql = 'SELECT * FROM m_tbexport_csv WHERE iPID="{}"'.format(myPID)
    res = fetch_3307(find_sql)
    if res is None:
        os._exit(1)
    else:
        tar_path = res.get('sPath')
        clear_path = os.path.split(tar_path)[0]
        try:
            os.system(CMD_RM_PATH(clear_path))
        except:
            pass
    # update running status
    stop_sql = UPDATE_STOP_SQL.format(st=ST_STOP, pid=myPID)
    exec_3307(stop_sql)

    FWLOG_DBG('process[%s] get signal [%s]' % (myPID, sig))
    os._exit(0)

def export_to_csv(sql_args, fn, record_id):
    """ export tables to csv files """
    reload(sys)
    sys.setdefaultencoding('utf-8')

    # register signal
    signal.signal(signal.SIGUSR1, signal_handler_stop)

    # args parser
    st = sql_args.get('st', 0)
    et = sql_args.get('et', 0)
    sel = sql_args.get('select', '*')
    tb = sql_args.get('from', None)
    wh = sql_args.get('where', '1=1')

    if tb is None:
        FWLOG_DBG('[cmd_export_csv]get invalid args TABLE')
        return
    if tb not in key_name:
        # log here
        FWLOG_ERR('Please add table type[%s] in key_name dict' % tb)
        return None


    # get date and start time/end time of every date
    try:
        date_list = timestamp_parser(st, et)
    except Exception as e:
        # log here
        FWLOG_ERR('[cmd_export_csv]timestamp_parser error %s' % e)
        return

    # generate condition clause
    _where = '{w} and iTime > {s_t} and iTime < {e_t}'.format(w=wh, s_t=st, e_t=et)
    # get task start time
    current_time = int(time.time())
    # get process pid
    myPID = os.getpid()
    # print 'PID=%s' % myPID
    FWLOG_DBG("[export_to_csv]running at !!!!!!!!!!!pid[%s]!!!!!!!!!!!" % myPID)

    # make dir for csv file, _dir=targe_file_directory, _path=save_path
    _dir = '{tb}_{t}'.format(tb=tb, t=current_time)
    # print _dir
    _path = os.path.join(CSV_PATH, _dir)
    # _file_tar = _dir + '.tar.gz'
    _file_tar = fn + '.tar.gz'
    _path_tar = os.path.join(_path, _file_tar)

    # insert running status to MYSQL
    running_sql = NEW_TASK_SQL.format(ti=current_time, st=ST_RUNNING, pid=myPID,
                                    cd=_where, fn=_file_tar, pt=_path, id=record_id)
    exec_3307(running_sql)

    # SQL template
    # _sql = 'SELECT {s} FROM {tb} WHERE {w} and iTime > {s_t} and iTime < {e_t}'
    _sql = 'SELECT CONCAT(" ", FROM_UNIXTIME(iTime, "%Y-%m-%d %H:%i:%S")) as iTime, {s} \
        INTO OUTFILE "{of}" FIELDS TERMINATED BY "," LINES TERMINATED BY "\n" \
        FROM {tb} WHERE {w} and iTime > {s_t} and iTime < {e_t}'

    if not os.path.exists(_path):
        os.system(CMD_MKDIR(_path))
        os.system('chmod 0777 %s' % _path)

    # export to csv
    for date in date_list:
        tb_date = tb + '_' + date

        row_name = ['时间']
        # chinese name of table keys
        if sel != '*':
            k_sel = [ i.strip() for i in sel.split(',') ]
            fieldnames = list(set(k_sel) & set(key_name[tb].keys()))
            _sel = list(set(k_sel) & set(key_name[tb].keys()))
            _sel.remove('iTime')
            for _n in _sel:
                row_name.append(key_name[tb][_n])
            _sel = ','.join(_sel)
            print _sel

        else:
            _sel = key_name[tb].keys()
            _sel.remove('iTime')
            for _n in _sel:
                row_name.append(key_name[tb][_n])
            _sel = ','.join(_sel)
            if tb == 'm_tblog_url_visit':
                _sel = _sel.replace('sAction', "REPLACE(sAction,0,'阻断') as sAction")
            print _sel
            fieldnames = key_name[tb].keys()

        # print 'fieldnames=%s' % fieldnames
        # row_name = { _n: key_name[tb][_n] for _n in fieldnames }
        print ','.join(row_name)

        # print sel_sql
        file_name = os.path.join(_path, tb_date + '.csv')
        FWLOG_DBG('[export_to_csv]export to %s' % file_name)
        # make sure the file is not exists
        if os.path.exists(file_name):
            os.system('rm -f %s' % file_name)

        # combine and generate the SQL
        sel_sql = _sql.format(s=_sel, of=file_name, tb=tb_date, w=wh,
                              s_t=date_list[date][0], e_t=date_list[date][1])
        try:
            # use select into outfile
            exec_3307(sel_sql)
            # os.system('sed -i 1i\ {} {}'.format(codecs.BOM_UTF8 + ','.join(row_name.values()), file_name))
            os.system('sed -i 1i\ {} {}\n'.format(u'\uFEFF' + ','.join(row_name), file_name))
            # with open(file_name, 'a+') as csvfile:
            #     csvfile.seek(0)
            #     csvfile.write(codecs.BOM_UTF8)


            # with open(file_name, 'w') as csvfile:
            #     csvfile.write(codecs.BOM_UTF8)
            #     # csvfile.write(','.join(row_name.values()))
            #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel')
            #     # writer.writerow(key_name[tb])
            #     writer.writerow(row_name)
            #     for row in fcal_3307(sel_sql):
            #         writer.writerow(row)
        except Exception as e:
            os.system(CMD_RM(file_name))
            FWLOG_ERR('[export_to_csv]%s' % e )


    # package csv files
    _path_src = os.path.join(_path, '*.csv')

    # os.system(CMD_TAR(_path_tar, _path_src))
    # print(CMD_TAR(_path_tar, _path_src))

    os.chdir(_path)
    os.system(CMD_TAR(_path_tar, _path, '*.csv'))
    print (CMD_TAR(_path_tar, _path, '*.csv'))

    print(CMD_RM(_path_src))
    # os.system(CMD_RM(_path_src))

    # update running status
    # done_sql = UPDATE_SQL.format(st=ST_DONE, pid=0, fn=_file_tar)
    done_sql = UPDATE_SQL.format(st=ST_DONE, pid=0, id=record_id)
    exec_3307(done_sql)

    FWLOG_DBG('[export_to_csv]done')


def cmd_export_csv(args):
    """create a new thread to export csv file"""
        # create thread
    if not os.path.exists(CSV_PATH):
        os.system(CMD_MKDIR(CSV_PATH))

    CMDLOG_ERR('[export_to_csv]args is %s' % args)

    # print args
    if len(args) != 3:
        CMDLOG_ERR('[export_to_csv]args length error %s' % args)
        return


    try:
        import ast
        sql_arg = ast.literal_eval(args[0])
        # sql_arg = json.loads(args[0])
        fn = args[1]
        record_id = int(args[2])
        _p = Process(target=export_to_csv, args=(sql_arg, fn, record_id, ))
        _p.start()
    # no need to join here if cmd is execute within fw's process
    # _p.join()
    except Exception as e:
        CMDLOG_ERR('[export_to_csv]error %s' % e)
        CMDLOG_ERR('[export_to_csv]error %s' % args)


if __name__ == '__main__':
    arg = {'select': '*', 'from': 'm_tblog_firewall', 'where': '1=1',
           'st': 1476252001, 'et': 1481627352}
    arg = ['{"select":"*","from":"m_tblog_firewall","where":"1=1","st":"1479830549","et":"1479913349"}', 'filename', 11]
    # arg = ["{'select': 'iTime, sInputPort, sOutPort', 'from': 'm_tblog_firewall', 'where': '1=1','st': 1476252001,'et': 1481627352}", 'sss', 64]
    cmd_export_csv(arg)
    time.sleep(20)
    print 'done'
    # sql = 'SELECT * FROM m_tblog_info_leak_20160512;'
    # export_to_csv('m_tblog_info_leak', sql)
    # timestamp_parser(1421077403, 1422077403)
    # timestamp_parser(1421077403, 1421078303)
    pass
