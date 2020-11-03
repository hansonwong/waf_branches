# -*- coding: utf-8 -*-
# created by szl 2014-03-14

import re
import os
import time
import datetime
import pygeoip
import MySQLdb
import types
import json
import GeoIP
import multiprocessing
from MySQLdb import escape_string
from config import config
from logging import getLogger
from common import logger_init
from scanfile import file_queue
from db import (AlertLogSet, session_scope,
    ReverseProxy, conn_scope, AlertReport, formatsqlstr,get_config)
from filemanage import filemanage_queue
from clickhouse_driver import Client


# access log REXP
re_start = re.compile('--\S+-A--')
re_end = re.compile(r'^--([0-9a-fA-F]{8,})-Z--')
rexpFront = re.compile(r'^--([0-9a-fA-F]{8,})-([A-Z])--')
rexpHeader = re.compile(
    r'^\[(.+) (.+)\] (\S+) ([.:0-9a-f]+) (\d+) ([.:0-9a-f]+) (\d+)')
rexpPattern = re.compile(r'^(\S+) (.+)')
rexpUserAgent = re.compile(r'^User-Agent\s*:\s*(.+)')
rexpHost = re.compile(r'^Host\s*:\s*(.+)')
rexpReferer = re.compile(r'^Referer\s*:\s*(.+)')
rexpRequestCT = re.compile(r'^Accept\s*:\s*(.+)')
rexpStatusCode = re.compile(r'^(HTTP\/\d\.\d) (\d{3}) (.+)')
rexpResponseCT = re.compile(r'^Content\-Type\s*:\s*(.+)')
rexpMessageHead = re.compile(r'^Message\s*:\s*([^\.]+)\. ([^\.]+)')
rexpMessageAll = re.compile(r'\[(\w+?) "(.+?)"\]')
rexpdallowed = re.compile(r'Access allowed')
rexpdenied = re.compile(r'denied with code')
rexpclosed = re.compile(r'denied with connection close')
rexpwaring = re.compile(r'Warning')
rexpcheckurl = re.compile(r'(http://[^/]+)(\S+)')
rexpCookie = re.compile(r'^Cookie:\s*(.+)')

# gic = pygeoip.GeoIP('/usr/local/bluedon/bdwafd/data/GeoLiteCity.dat')
gic = GeoIP.open('/usr/local/bluedon/bdwafd/data/GeoLiteCity.dat', GeoIP.GEOIP_STANDARD)

def cal_time(func):
    def wrapper(*args):
        s = time.time()
        ret = func(*args)
        getLogger('audit').info('{}: {}'.format(func.__name__, time.time() - s))
        return ret
    return wrapper

def split_log(msg):
    flag = 0
    result = []
    lines = msg.split('\n')
    for line in lines:
        if flag == 0 and re_start.match(line):  #直到第一次遇到结束标记前, 判断是不是 --c715332d-A--[开始标记]
            flag = 1
        if not re_end.match(line):  #不是 --c715332d-Z--[结束标记] 的位置
            result.append(line)
        else:     #遇到 --c715332d-Z--[结束标记]
            result.append(line)
            if flag == 0:  #第一行不是--c715332d-A--,这种情况下第一次遇到结束标记, 清空存起来的日志
                result = []
                flag = 1
            else:
                return result


allproccess = []

def multi_processtask(lines_list):
    dp = []
    for p in allproccess:
        if not p.is_alive():
            p.join()
            dp.append(p)
    for p in dp:
        allproccess.remove(p)
    for i in range(0, len(lines_list), 2000):
        p = multiprocessing.Process(target=processtask, args=(lines_list[i:i+2000],))
        p.daemon = True
        p.start()
        allproccess.append(p)


def processtask(lines_list):
    '''
    parser and insert into mysql
    '''
    if not lines_list:
        return
    try:
        dtime = time.strftime("%Y%m%d", time.localtime())
        counturidtime = "%s-%s-%s" % (dtime[0:4], dtime[4:6], dtime[6:8])

        with conn_scope(**config['dbacc']) as (conn, cursor):
            result= get_config("SelfStudySet")
            selfstudy_is_use = result["isUse"]
            cursor.execute('select sWorkMode from db_firewall.m_tbnetport')
            workmodes = map(lambda x: x[0], cursor.fetchall())
            attack_type = get_attacktype(cursor)

            sqlstr = AlertLogSet().sqlact()
            count = 0
            s = time.time()
            for lines in lines_list:
                parser = AuditParser(lines, sqlstr, attack_type)
                if not parser.parse():
                    continue
                count += 1
            getLogger('audit').info(time.time() - s)
            getLogger('audit').info('parse: %s' % count)

            if(count):
                sqlstr[0] = sqlstr[0][0:-1] + ';'
                #sqlstr[1] = sqlstr[1][0:-1] + ';'
                count = 0
                if len(sqlstr[0]) > 460:  # cc
                    count = 1
                    cursor.execute(sqlstr[0])
                #if len(sqlstr[1]) > 460:  # alert
                if parser.alertloglist:
                    count = 1
                    #cursor.execute(sqlstr[1])
                    ckclient = Client('localhost', password='wafabc123',port='9001')
                    #ckclient.execute(sqlstr[1])
                    #ckclient.execute(sqlstr[1].replace('\n', ''))
                    getLogger('audit').info(parser.alertloglist)
                    getLogger('audit').info(sqlstr[1])
                    ckclient.execute(sqlstr[1], parser.alertloglist)
                if count:
                    counturi(cursor, sqlstr[4], counturidtime)
                    countruleid(cursor, sqlstr[3], dtime)
                    countseverity(cursor, sqlstr[2], dtime)
                    countsourceip(cursor, sqlstr[5], dtime)
                if selfstudy_is_use:
                    selfstudyrule(conn,cursor, sqlstr[6])  # selfstudy
    except Exception, e:
        getLogger('audit').exception(e)
    finally:
        getLogger('audit').info('all: %s' % len(lines_list))


def get_attacktype(cursor):
    attack_type = {}
    # 内置规则 自定义规则 访问控制
    for tb in ('t_rules', 't_customrules', 't_baseaccessctrl'):
        cursor.execute("select realid, type from waf.{}".format(tb))
        attack_type.update(dict(cursor.fetchall()))
    # 防盗链 自学习
    for ruleid in [350001] + (range(350110, 350118)):
        attack_type[ruleid] = 'CUSTOM'  # 自定义
    return attack_type


def selfstudyrule(conn,cursor, srules):
    flag = 0
    selfstudy = []
    if len(srules):
        flag += 1
        selfstudy = get_config("SelfStudyResult")

    for srule in srules:
        flag += 1
        if len(srule[0]):
            selfstudy["uriMax"] = max(selfstudy["uriMax"], len(srule[0])) if selfstudy["uriMax"] != "" else len(srule[0])
            buff = srule[0].split("?")
            if len(buff) > 1:
                buff = buff[1].split("&")
                selfstudy["argCountMax"] = max(selfstudy["argCountMax"], len(buff)) if selfstudy["argCountMax"] != "" else len(buff)
                for argname in buff:
                    buf = argname.split("=")
                    selfstudy["argNameMax"] = max(selfstudy["argNameMax"], len(buf[0])) if selfstudy["argNameMax"] != "" else len(buf[0])
                    if len(buf) > 1:
                        selfstudy["argContentMax"] = max(selfstudy["argContentMax"], len(buf[1])) if selfstudy["argContentMax"] != "" else len(buf[1])
        if len(srule[1]):
            selfstudy["cookieMax"] = max(selfstudy["cookieMax"], len(srule[1])) if selfstudy["cookieMax"] != "" else len(srule[1])
            buff = srule[1].split(";")
            selfstudy["cookieCountMax"] = max(selfstudy["cookieCountMax"], len(buff)) if selfstudy["cookieCountMax"] != "" else len(buff)
            for argname in buff:
                buf = argname.split("=")
                selfstudy["cookieNameMax"] = max(selfstudy["cookieNameMax"], len(buf[0])) if selfstudy["cookieNameMax"] != "" else len(buf[0])
                if len(buf) > 1:
                    selfstudy["cookieContentMax"] = max(selfstudy["cookieContentMax"], len(buf[1])) if selfstudy["cookieContentMax"] != "" else len(buf[1])

    if flag:
        json = "{'uriMax':'%s','argNameMax':'%s','argContentMax':'%s','argCountMax':'%s','cookieMax':'%s',\
                'cookieNameMax':'%s','cookieContentMax':'%s','cookieCountMax':'%s'}" % (selfstudy['uriMax'],selfstudy['argNameMax'],\
                selfstudy['argContentMax'],selfstudy['argCountMax'],selfstudy['cookieMax'],selfstudy['cookieNameMax'],\
                selfstudy['cookieContentMax'],selfstudy['cookieCountMax'])
        sqlstr = "update config set json='%s' where symbol='SelfStudyResult'" % json
        cursor.execute(sqlstr)


def counturi(cursor, uridata, dtime):
    for data in uridata:
        ct = "logdate='%s' and Host='%s' and Uri='%s' and \
              QueryString='%s'" % (dtime, data[0], data[1], data[2])
        getsql = "select * from t_counturi where %s" % ct
        count = cursor.execute(getsql)
        if(count == 1):
            getsql = "UPDATE t_counturi SET Hits = Hits+1 where %s" % ct
        else:
            if(count > 1):
                getsql = "DELETE FROM t_counturi where %s" % ct
                cursor.execute(getsql)
            getsql = "insert into t_counturi(logdate, Host, Uri, QueryString, Hits) values\
                     ('%s', '%s', '%s', '%s', '1');" % formatsqlstr((dtime, data[0], data[1], data[2]))
        cursor.execute(getsql)


def countruleid(cursor, ruleid, dtime):
    for (k, v) in ruleid.items():
        ct = "logdate='%s' and ruleid='%s'" % (dtime, k)
        getsql = "select * from t_ruleid where %s" % ct
        count = cursor.execute(getsql)
        if(count == 1):
            getsql = "UPDATE t_ruleid SET hits = hits+%d where %s" % (v, ct)
        else:
            if(count > 1):
                getsql = "DELETE FROM t_ruleid where %s" % ct
                cursor.execute(getsql)
            getsql = "insert into t_ruleid(logdate, ruleid, hits) values\
                     ('%s', '%s', '%d');" % (dtime, k, v)
        cursor.execute(getsql)


def countseverity(cursor, severity, dtime):
    getsql = "select * from t_countsety where logdate = '%s'" % dtime
    count = cursor.execute(getsql)
    if(count == 1):
        getsql = ("UPDATE t_countsety SET emergency=emergency+%d, alert=alert+%d,"
                  "critical=critical+%d,error=error+%d,warning=warning+%d,notice=notice+%d,"
                  "info=info+%d,debug=debug+%d where logdate = '%s'" % (severity['EMERGENCY'],
                  severity['ALERT'], severity['CRITICAL'], severity['ERROR'], severity['WARNING'],
                  severity['NOTICE'], severity['INFO'], severity['DEBUG'], dtime))
    else:
        if(count > 1):
            getsql = "DELETE FROM t_countsety where logdate = '%s'" % dtime
            cursor.execute(getsql)
        getsql = "insert t_countsety(logdate, emergency, alert, critical, error, warning, \
                  notice, info, debug) values('%s', %d, %d, %d, %d, %d, %d, %d, %d);" % \
             (dtime, severity['EMERGENCY'], severity['ALERT'], severity['CRITICAL'],
             severity['ERROR'], severity['WARNING'], severity['NOTICE'], severity['INFO'],
             severity['DEBUG'])
    cursor.execute(getsql)


def countsourceip(cursor, ipdata, dtime):
    for data in ipdata:
        ct = "logdate='%s' and SourceIP='%s'" % (dtime, data[3])
        getsql = "select * from t_sourceip where %s" % ct
        count = cursor.execute(getsql)
        if(count == 1):
            getsql = "UPDATE t_sourceip SET Hits = Hits+1 where %s" % ct
        else:
            if(count > 1):
                getsql = "DELETE FROM t_sourceip where %s" % ct
                cursor.execute(getsql)
            getsql = "insert into t_sourceip(logdate, CountryCode, RegionCode, City, SourceIP, Hits) \
                      values('%s', '%s', '%s', '%s', '%s', '1');" % (dtime, data[0], data[1], data[2], data[3])
        cursor.execute(getsql)


def gettypename(ruleId):
    config['db']['charset'] = 'utf8'
    with conn_scope(**config['db']) as (conn, cursor):
        sqlstr = 'select t_rulecat.desc from t_rulecat inner join t_rules on \
                t_rules.type=t_rulecat.name where t_rules.realid=%s' % ruleId
        cursor.execute(sqlstr)
        typeName = cursor.fetchone()
    if typeName:
        typeName = typeName[0]
    else:
        typeName = ''
    return typeName


class AuditParser:
    def __init__(self, lines, sqlstr, attack_type):
        self.flag = 0
        self.uricheck = ''
        self.cookie = ''
        self.sqlstr = sqlstr
        self.attack_type = attack_type
        self.alertlog = AlertLogSet()
        self.alertreport = AlertReport()
        # self.gic = pygeoip.GeoIP('data/GeoLiteCity.dat')
        self.alertlog.LogSource = lines[0]
        self.lines = lines[1]
        self.len = len(self.lines)
        self.alertloglist = []

    # @cal_time
    def parse(self):
        id = 0
        while(id < self.len):
            match = rexpFront.search(self.lines[id])
            if not match:
                pass
            elif match.group(2) == 'A':
                id = self.parse_header(id)
            elif match.group(2) == 'B':
                id = self.parse_request_headers(id)
            elif match.group(2) == 'F':
                id = self.parse_response_headers(id)
            elif match.group(2) == 'H':
                id = self.parse_message(id)
            elif match.group(2) == 'Z':
                break
            id += 1
        return self.flag

    def setreportvalue(self):
        self.alertreport.LogDateTime = self.alertlog.LogDateTime
        self.alertreport.Url = self.alertlog.Url
        self.alertreport.Host = self.alertlog.Host
        self.alertreport.SourceIP = self.alertlog.SourceIP

    # @cal_time
    def parse_header(self, id):
        id += 1
        # match = rexpHeader.search(self.lines[id])
        # if not match:
            # return id

        # tFomat = time.strptime(match.group(1), "%d/%b/%Y:%H:%M:%S")
        # self.alertlog.LogDateTime = time.strftime("%Y-%m-%d %H:%M:%S", tFomat)
        # self.alertlog.AuditLogUniqueID = match.group(3)
        # self.alertlog.SourceIP = match.group(4)
        # self.alertlog.SourcePort = match.group(5)
        # self.alertlog.DestinationIP = match.group(6)
        # self.alertlog.DestinationPort = match.group(7)
        header_data = dict(map(lambda x: x.split('|:::|'), self.lines[id].split('|::|')))
        # header_data = json.loads(self.lines[id])
        if not header_data:
            return id
        # tFomat = time.strptime(header_data.get('LogDateTime'), "%d/%b/%Y:%H:%M:%S")
        # self.alertlog.LogDateTime = time.strftime("%Y-%m-%d %H:%M:%S", tFomat)
        self.alertlog.LogDateTime = '2017-10-10 19:01:42'
        self.alertlog.AuditLogUniqueID = header_data.get('AuditLogUniqueID')
        self.alertlog.SourceIP = header_data.get('SourceIP')
        self.alertlog.SourcePort = header_data.get('SourcePort')
        self.alertlog.DestinationIP = header_data.get('DestinationIP')
        self.alertlog.DestinationPort = header_data.get('DestinationPort')
        self.alertlog.CountryCode = 'CN'
        self.alertlog.RegionCode = 'unknown'
        self.alertlog.City = 'unknown'

        # getaddrs = self.gic.record_by_addr(self.alertlog.SourceIP)
        getaddrs = gic.record_by_addr(self.alertlog.SourceIP)
        if getaddrs:
            self.alertlog.CountryCode = getaddrs['country_code']
            self.alertlog.RegionCode = getaddrs['region_code']
            self.alertlog.City = getaddrs['city']
        return id

    # @cal_time
    def parse_request_headers(self, id):
        # self.alertlog.Referer = ''
        # self.alertlog.UserAgent = ''
        id += 1
        request_headers_data = dict(map(lambda x: x.split('|:::|'), self.lines[id].split('|::|')))
        # request_headers_data = json.loads(self.lines[id])
        if not request_headers_data:
            return id

        query_string = request_headers_data.get('QUERY_STRING', '').split(' ')
        if query_string:
            self.alertlog.HttpMethod, self.alertlog.Url, self.alertlog.HttpProtocol = query_string
            # if contain http:// ?
            match = rexpcheckurl.search(self.alertlog.Url)
            if match:
                self.alertlog.Url = match.group(1)
            buf = self.alertlog.Url.split('?')
            self.alertlog.Uri = buf[0][:512]
            if(len(buf) > 1):
                self.alertlog.QueryString = buf[1][:512].replace("'", '"')

        host = request_headers_data.get('HOST', '')
        if host:
            self.alertlog.Url = host + self.alertlog.Url
            self.alertlog.Url = escape_string(self.alertlog.Url[:512])
            buf = host.split(':')
            self.alertlog.Host = escape_string(buf[0][:255])
            if(len(buf) > 1) and buf[1].isdigit():
                self.alertlog.DestinationPort = buf[1]

        self.alertlog.UserAgent = escape_string(request_headers_data.get('User-Agent', '')[:255])
        self.alertlog.Referer = escape_string(request_headers_data.get('Referer', '')[:255])
        self.alertlog.RequestContentType = request_headers_data.get('Accept', '')[:255]
        self.cookie = request_headers_data.get('Cookie', '')

        return id


        flag1, flag2, flag3, flag4, flag5, flag6 = True, True, True, True, True, True
        while(id < self.len):
            id += 1
            match = rexpFront.search(self.lines[id])
            if(match):
                id -= 1
                break

            if flag1:
                match = rexpPattern.search(self.lines[id])
                if match:
                    self.alertlog.HttpMethod = match.group(1)
                    buf = match.group(2).split(' ')
                    self.uricheck = buf[0]
                    self.alertlog.HttpProtocol = buf[-1]
                    strlen = len(match.group(2)) - len(buf[-1]) - 1
                    self.alertlog.Url = match.group(2)[0:strlen]

                    # if contain http:// ?
                    match = rexpcheckurl.search(self.alertlog.Url)
                    if match:
                        self.alertlog.Url = match.group(1)

                    buf = self.alertlog.Url.split('?')
                    # self.uri = escape_string(buf[0][:512])
                    self.alertlog.Uri = buf[0][:512]
                    if(len(buf) > 1):
                        # self.querystr = escape_string(buf[1][:512])
                        self.alertlog.QueryString = buf[1][:512].replace("'", '"')
#                    print 'self.querystr:',self.querystr
                    flag1 = False
                    continue

            if flag2:
                match = rexpHost.search(self.lines[id])
                if(match):
                    self.alertlog.Url = match.group(1) + self.alertlog.Url
                    self.alertlog.Url = escape_string(self.alertlog.Url[:512])
                    buf = match.group(1).split(':')
                    self.alertlog.Host = escape_string(buf[0][:255])

                    if(len(buf) > 1) and buf[1].isdigit():
                        self.alertlog.DestinationPort = buf[1]
                    flag2 = False
                    continue

            if flag3:
                match = rexpUserAgent.search(self.lines[id])
                if(match):
                    # uUserAgent = unicode(match.group(1)[:255], 'utf-8')
                    self.alertlog.UserAgent = escape_string(
                        match.group(1)[:255])
                    flag3 = False
                    continue

            if flag4:
                match = rexpReferer.search(self.lines[id])
                if(match):
                    self.alertlog.Referer = escape_string(match.group(1)[:255])
                    flag4 = False
                    continue

            if flag5:
                match = rexpRequestCT.search(self.lines[id])
                if(match):
                    self.alertlog.RequestContentType = match.group(1)[:255]
                    flag5 = False
                    continue

            if flag6:
                match = rexpCookie.search(self.lines[id])
                if(match):
                    self.cookie = match.group(1)
                    flag6 = False
                    continue
        return id

    # @cal_time
    def parse_response_headers(self, id):
        id += 1
        response_headers_data = dict(map(lambda x: x.split('|:::|'), self.lines[id].split('|::|')))
        # response_headers_data = json.loads(self.lines[id])
        if not response_headers_data:
            return id
        status_line = response_headers_data.get('status_line', '').split(' ')
        if len(status_line) > 2:
            self.alertlog.HttpStatusCode = status_line[2]

        self.alertlog.ResponseContentType = response_headers_data.get('Content-Type', '')[:255]
        return id

        flag1, flag2 = True, True
        while(id < self.len):
            id += 1
            match = rexpFront.search(self.lines[id])
            if(match):
                id -= 1
                break

            if(flag1):
                match = rexpStatusCode.search(self.lines[id])
                if(match):
                    self.alertlog.HttpStatusCode = match.group(2)
                    flag1 = False
                    continue

            if(flag2):
                match = rexpResponseCT.search(self.lines[id])
                if(match):
                    self.alertlog.ResponseContentType = match.group(1)[:255]
                    flag2 = False
                    continue
        return id

    # @cal_time
    def parse_message(self, id):
        while(id < self.len):
            id += 1
            match = rexpFront.search(self.lines[id])
            if(match):
                id -= 1
                break

            match = rexpMessageHead.search(self.lines[id])
            if(match):
                self.alertlog.MatchData = ''
                self.alertlog.Rev = ''
                self.alertlog.Msg = ''
                self.alertlog.Tag = ''
                self.alertlog.Severity = 'WARNING'
                self.alertlog.Status = 'warning'
                if rexpdallowed.search(match.group(1)):
                    self.alertlog.Status = 'allow'
                elif rexpdenied.search(match.group(1)):
                    self.alertlog.Status = 'deny'
                elif rexpclosed.search(match.group(1)):
                    self.alertlog.Status = 'drop'
                elif rexpwaring.search(match.group(1)):
                    self.alertlog.Status = 'warning'

                self.alertlog.GeneralMsg = escape_string(match.group(2)[:512])
                m = re.search('code\s*(\d+)', match.group(1))
                if(m):
                    self.alertlog.HttpStatusCode = m.group(1)

                count = 0
                for m in rexpMessageAll.finditer(self.lines[id]):
                    if(m.group(1) == 'file'):
                        self.alertlog.Rulefile = m.group(2)[:255]
                    elif(m.group(1) == 'id'):
                        self.alertlog.RuleID = m.group(2)
                        # typeName = gettypename(self.alertlog.RuleID)
                        # self.alertreport.TypeName = typeName
                    elif(m.group(1) == 'rev'):
                        self.alertlog.Rev = escape_string(m.group(2)[:128])
                    elif(m.group(1) == 'msg'):
                        self.alertlog.Msg = m.group(2)
                        # self.alertlog.Msg = escape_string(m.group(2)[:128])
                    elif(m.group(1) == 'severity'):
                        self.alertlog.Severity = m.group(2)
                    elif(m.group(1) == 'data'):
                        matchM = m.group(2)[:255]
                        if matchM[len(matchM) - 1] == '\\':
                            matchM = matchM[:254]
                        # self.alertlog.MatchData = escape_string(matchM)
                        matchD = escape_string(m.group(2)[:255])
                        matchD = matchD[:255]
                        if matchD[len(matchD) - 1] == '\\':
                            matchD = matchD[:254]
                        self.alertlog.MatchData = matchD
                    elif(m.group(1) == 'tag'):
                        self.alertlog.Tag = m.group(2)[:64]

                self.flag += 1
                self.alertlog.AttackType = self.attack_type.get(int(self.alertlog.RuleID))
                self.setattrsql()
        return id

    # @cal_time
    def setattrsql(self):
        # self.setreportvalue()
        if self.alertlog.RuleID == '350100':  # selfstudy
            self.sqlstr[6].append([self.uricheck, self.cookie])
            return 1
        if self.alertlog.RuleID in ('800101', '800103'):
            msg_type = {'800101': 0, '800103': 1}
            file_queue.put((msg_type[self.alertlog.RuleID], self.alertlog.Msg))
            return

        self.alertlog.Msg = escape_string(self.alertlog.Msg[:128])
        if self.alertlog.RuleID == '800015' or '800016':
            filemanage_queue.put(self.alertlog.MatchData)
        self.sqlstr[2][self.alertlog.Severity] += 1
        if self.alertlog.RuleID in self.sqlstr[3]:
            self.sqlstr[3][self.alertlog.RuleID] += 1
        else:
            self.sqlstr[3][self.alertlog.RuleID] = 1

        if self.alertlog.AttackType == 'CC':
            self.sqlstr[0] += self.alertlog.retvalues()
        else:
            #self.sqlstr[1] += self.alertlog.retvalues()
            self.alertloglist.append(self.alertlog.getvalues())

        if self.flag == 1:
            self.sqlstr[4].append([self.alertlog.Host, self.alertlog.Uri, self.alertlog.QueryString, self.alertlog.RuleID])
            self.sqlstr[5].append([self.alertlog.CountryCode, self.alertlog.RegionCode,
                                   self.alertlog.City, self.alertlog.SourceIP])


if __name__ == "__main__":
    pass

