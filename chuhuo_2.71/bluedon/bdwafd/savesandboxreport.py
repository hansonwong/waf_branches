#!/usr/bin/env python
#-*-coding:utf-8-*-

import json
import os
import sys
import time
import logging
from logging import getLogger
from common import logger_init
from db import conn_scope
from config import config
from scanfile import filenameparser

dirpath = '/usr/local/bluedon/bdwafd/cuckooreport'
logger_init('save','/tmp/saveandboxreport.log' , 'DEBUG')

def get_rating(result):
    if '"High"' in result:
        return "High"
    if '"Middle"' in result:
        return "Middle"
    return "Low"




def savedata(filepath):
    with open(filepath) as fp:
        data = json.load(fp)
        localfilepath = "/usr/local/bluedon/checkFile/unknownFile/%s" % data['fileName']
        with conn_scope(**config['db']) as (conn, cursor):
            report = json.dumps(data['report'])
            filename = os.path.basename(filepath)[:-19]#remove the "_cuckoo_report.json" from the filename
            r = filenameparser(filename)
            reporttime = int(time.time())
            rating = get_rating(report)
            cursor.execute("insert into logs.t_sandboxlogs(result, filePath) values(%s, %s)",
                           (report, localfilepath))
            cursor.execute("insert into logs.t_uploadedfilelogs(reporttime,url,filename,uploadtime,type,rating,result) values(%s,%s,%s,%s,%s,%s,%s)",
                           (reporttime, r["url"], r["filename"], r["uploadtime"], 0, rating, pretty_report(report)))
            getLogger('save').debug(pretty_report(report))
             
    os.remove(filepath)

def pretty_report(report):
    if "no regkey_written" in report:
        return u'[{"文件无破坏性操作": ""}]'
    else:
        return report

		


def test():
    for filename in sorted(os.listdir(dirpath)):
        filepath = "%s/%s" % (dirpath, filename)
        savedata(filepath)

if __name__ == "__main__":
    try:
        filepath = sys.argv[1]
        savedata(filepath)
    except Exception, e:
        getLogger('save').exception(e)
         
