# -*- coding: utf-8 -*-
# created by szl 2014-03-14

import re
import os
import time

sdate = '20140315'
stime = '20140315-0948'
etime = time.strftime("%Y%m%d-%H%M%S", time.localtime())
edate = etime[:8]
#std_dir = '/usr/local/bluedon/bdwaf/logs/audit/'
std_dir = '/home/bluedon/szl/ddd/'
#access log REXP
REXPFront = '--([0-9a-fA-F]{8,})-([A-Z])--'
REXPHeader = '\[(.+) (.+)\] (\S+) ([.:0-9a-f]+) (\d+) ([.:0-9a-f]+) (\d+)'
REXPPattern = '(\S+) (.*?) (HTTP\/\d.\d)';
REXPUserAgent = 'User-Agent\s*:\s*(.+)'
REXPUserAgent = 'User-Agent\s*:\s*(.+)'
REXPHost = 'Host\s*:\s*(.+)'
REXPReferer = 'Referer\s*:\s*(.+)'
REXPRequestCT = 'Accept\s*:\s*(.+)'
REXPStausCode = '(HTTP\/\d\.\d) (\d{3}) (.+)'
REXPResponseCT = 'Content\-Type\s*:\s*(.+)'
REXPMessageHead = 'Message\s*:\s*([^\.]+)\. ([^\.]+)';
REXPMessageAll = '\[(\w+?) "(.+?)"\]';


AccessLog = {
    'AuditLogUniqueID': 'NULL',
    'AuditLogDate': '2014-03-14',
    'AuditLogTime': '12:00:00',
    'SourceIP': '0.0.0.0',
    'SourcePort': 0,
    'DestinationIP': '0.0.0.0',
    'DestinationPort': 0,
    'Referer': 'NULL',
    'UserAgent': 'NULL',
    'HttpMethod': 'NULL',
    'Uri': 'NULL',
    'QueryString': 'NULL',
    'HttpProtocol': 0,
    'Host': 'NULL',
    'RequestContentType': 'NULL',
    'ResponseContentType': 'NULL',
    'HttpStatusCode': 0
}

AlertLog = {
    'AuditLogUniqueID': 'NULL', 
    'GeneralMsg': 'NULL', 
    'Rulefile': 'NULL', 
    'RuleID': 0, 
    'MatchData': 'NULL', 
    'Rev': 'NULL', 
    'Msg': 'NULL',
    'Severity': 0, 
    'Tag1': 'NULL', 
    'Tag2': 'NULL', 
    'Tag3': 'NULL', 
    'Status': 0
}


#遍历目录并获取文件名
def WalkLogDir(dirname, flag):
    names = os.listdir(dirname)
    for name in sorted(names):
        print name
        if(os.path.isfile(dirname+name)):
            ParserMSG(dirname+name)
        elif(not flag and name >= sdate):
            WalkLogDir(dirname+name+'/', True)
        elif(flag and (name > stime and name < etime)):
            WalkLogDir(dirname+name+'/', True)


#解析文件
def ParserMSG(filename):
    rexp = re.compile(REXPFront)
    fd = open(filename)
    line = fd.readline()
    while(line):
        match = rexp.search(line)
        if(not match):
            pass
        elif(match.group(2) == 'A'):
            HeaderParser(fd)
        elif(match.group(2) == 'B'):
            RequestHeadersParser(fd)
        elif(match.group(2) == 'F'):
            ResponseHeadersParser(fd)
        elif(match.group(2) == 'H'):
            MessageParser(fd)
        elif(match.group(2) == 'Z'):
            break
        line = fd.readline()
    fd.close()
#    printdict(AccessLog)
#    printdict(AlertLog)

def HeaderParser(filed):
    rexp = re.compile(REXPHeader);
    line = filed.readline()
    match = rexp.search(line)
    if(not match):
        return False

    tFomat = time.strptime(match.group(1), "%d/%b/%Y:%H:%M:%S")
    AccessLog['AuditLogDate'] = "%d-%d-%d" % (tFomat.tm_year, tFomat.tm_mon, tFomat.tm_mday)
    AccessLog['AuditLogTime'] = "%d:%d:%d" % (tFomat.tm_hour, tFomat.tm_min, tFomat.tm_sec)

    AlertLog['AuditLogUniqueID'] = match.group(3)
    AccessLog['AuditLogUniqueID'] = match.group(3)
    AccessLog['SourceIP'] = match.group(4)
    AccessLog['SourcePort'] = match.group(5)
    AccessLog['DestinationIP'] = match.group(6)
    AccessLog['DestinationPort'] = match.group(7)


def RequestHeadersParser(filed):
    rexp1 = re.compile(REXPFront)
    rexp2 = re.compile(REXPPattern)
    rexp3 = re.compile(REXPUserAgent)
    rexp4 = re.compile(REXPHost)
    rexp5 = re.compile(REXPReferer)
    rexp6 = re.compile(REXPRequestCT)
    while(True):
        last_pos = filed.tell()
        line = filed.readline()
        match = rexp1.search(line)
        if(match):
            filed.seek(last_pos)
            break

        match = rexp2.search(line)
        if(match):
            AccessLog['HttpMethod'] = match.group(1)
            AccessLog['HttpProtocol'] = match.group(3)
            buf = match.group(2).split('?')
            AccessLog['Uri'] = buf[0]
            if(len(buf) > 1):
                AccessLog['QueryString'] = buf[1]
            continue

        match = rexp3.search(line)
        if(match):
            AccessLog['UserAgent'] = match.group(1)
            continue

        match = rexp4.search(line)
        if(match):
            AccessLog['Host'] = match.group(1)
            continue

        match = rexp5.search(line)
        if(match):
            AccessLog['Referer'] = match.group(1)
            continue

        match = rexp6.search(line)
        if(match):
            AccessLog['RequestContentType'] = match.group(1)
            continue


def ResponseHeadersParser(filed):
    rexp1 = re.compile(REXPFront)
    rexp2 = re.compile(REXPStausCode)
    rexp3 = re.compile(REXPResponseCT)
    while(True):
        last_pos = filed.tell()
        line = filed.readline()
        match = rexp1.search(line)
        if(match):
            filed.seek(last_pos)
            break

        match = rexp2.search(line)
        if(match):
            AccessLog['HttpStatusCode'] = match.group(2)
            continue

        match = rexp3.search(line)
        if(match):
            AccessLog['ResponseContentType'] = match.group(1)
            continue


def MessageParser(filed):
    rexp1 = re.compile(REXPFront)
    rexp2 = re.compile(REXPMessageHead)
    rexp3 = re.compile(REXPMessageAll)
    while(True):
        last_pos = filed.tell()
        line = filed.readline()
        match = rexp1.search(line)
        if(match):
            filed.seek(last_pos)
            break

        match = rexp2.search(line)
        if(match):
            AlertLog['Status'] = match.group(1)
            AlertLog['GeneralMsg'] = match.group(2)
            m = re.match('code\s*(\d+)', match.group(1))
            if(m):
                AccessLog['HttpStatusCode'] = m.group(1)

            count = 0
            for m in rexp3.finditer(line):
                if(m.group(1) == 'file'):
                    AlertLog['Rulefile'] = m.group(2)
                elif(m.group(1) == 'id'):
                    AlertLog['RuleID'] = m.group(2)
                elif(m.group(1) == 'rev'):
                    AlertLog['Rev'] = m.group(2)
                elif(m.group(1) == 'msg'):
                    AlertLog['Msg'] = m.group(2)
                elif(m.group(1) == 'severity'):
                    AlertLog['Severity'] = m.group(2)
                elif(m.group(1) == 'data'):
                    AlertLog['MatchData'] = m.group(2)
                elif(m.group(1) == 'tag'):
                    count += 1
                    if(count >= 3):
                        break
                    tagstr = "Tag%d" % count
                    AlertLog[tagstr] = m.group(2)
#                printdict(AlertLog)
                print("\n")
#            printdict(AccessLog)
            print("\n")
        else:
            break


def printdict(dictstr):
    for k,v in dictstr.items():
        print("%s --> %s" % (k,v))
    print("\n\n")


WalkLogDir(std_dir, False)
#print("%s\n" % match.group(1))

