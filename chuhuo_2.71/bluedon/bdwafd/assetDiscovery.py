#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wpx 2016-06-01

import re, httplib, os, copy
from db import conn_scope,get_config
from config import config

#正则匹配日志分析
HOSTService = re.compile(r'\d+\/tcp[ ]+\S*[ ]+\S*[ ]+[ \S]*')
OSSearch = re.compile(r'Service Info: OS[\S\s]*')
Ending = re.compile(r'HOP\s+RTT\s+ADDRESS')

#class AssetDiscovery(threading.Thread):
#根据部署模式，获取局域网ip地址
def getLANIp():
    ipList = []
    with conn_scope(**config['db']) as (conn, cursor):
        conf = get_config("BaseConfig")
        deploy = conf["deploy"]
        if deploy == 'bridge':  #透明代理
            cursor.execute("select ip from waf.t_nicset where nic like('br%')")
            result = cursor.fetchall()
            for ip in result:
                ipList.append(ip[0])
        elif deploy == 'reverseproxy':  #反向代理
            cursor.execute("select ip from waf.t_nicset where nic='eth3'")
            ip = cursor.fetchone()
            ipList.append(ip[0])
        else:   #透明桥接
            cursor.execute("select ip from waf.t_nicset where nic='eth0'")
            ip = cursor.fetchone()
            ipList.append(ip[0])
    return ipList


#扫描局域网主机
def nmapScan(ip):
    ipSplit = ip.split('.')
    netSegment = "%s.%s.%s.0/24"%(ipSplit[0], ipSplit[1], ipSplit[2])
    filePath = 'log/nmap_%s.log'%(ipSplit[2])
    cmd = "nmap -A %s --exclude %s -p 80,443,444,8080 -vv > %s"%(netSegment, ip, filePath)
    print cmd
    result = os.system(cmd)
    return filePath


#对字符串进行分段，并去除空白段
def nmapResultSplit(resultStr):
    data = resultStr.split(' ')
    while '' in data:
        data.remove('')
    port = data[0].split('/')[0]
    software = ''
    data_len = len(data)
    if data_len >= 4:
        for index in range(3, data_len):
            if index == 3:
                software = data[index]
                continue
            software = "%s %s"%(software, data[index])
    return port, software


#分析扫描日志
def parserNmap(ipList):
    data = []
    filePaths = []
    for ip in ipList:
        filePath = nmapScan(ip)
        print 'nmapScan ending and path: %s'%filePath
        filePaths.append(filePath)
        with open(filePath, 'r') as fp:
            index = 0
            tag = 0
            temp_data = {}
            while 1:
                line = fp.readline()
                line = line.strip()
                if line.find('Nmap scan report for') != -1 and line.find(
                    'host down') == -1 and line.find(ip) == -1:
                    tag = 1
                    ip = line.split(' ')[-1]
                    temp_data = {
                            'ip': ip,
                            'https': [],
                            'http': [],
                            'OS': '',
                            'db': ''}
                if Ending.findall(line):
                    tag = 0
                    print temp_data
                    data.append(copy.deepcopy(temp_data))
                if tag:    
                    result = HOSTService.findall(line)
                    if result:
                        result = result[0]
                        if result.find('ssl/https') != -1 or result.find('ssl/http') != -1 or result.find('https') != -1:
                            port, software = nmapResultSplit(result)
                            temp_data['https'].append({'port': port, 'software': software})
                        if result.find('http') != -1 and result.find('ssl/http') == -1 and result.find('https') == -1:
                            port, software = nmapResultSplit(result)
                            temp_data['http'].append({'port': port, 'software': software})
                        if result.find('mysql') != -1 or result.find('ms-sql-s') != -1 or \
                            result.find('oracle') != -1:
                            port, software = nmapResultSplit(result)
                            if temp_data['db']:
                                temp_data['db'] = '%s/%s'%(temp_data['db'], software)
                            else:
                                temp_data['db'] = software

                    os_resulrt = OSSearch.findall(line)
                    if os_resulrt:
                        os_resulrt = os_resulrt[0]
                        OS = os_resulrt.split(':')[-1]
                        temp_data['OS'] = OS

                temp_index = fp.tell()
                if temp_index == index:
                    break
                index = temp_index
    return data, filePaths


#入库
def saveData(datas):
    with conn_scope(**config['db']) as (conn, cursor):
        for data in datas:
            sWebSiteIP = data['ip']
            for protocol in ('http', 'https'):
                if data[protocol]:
                    for host in data[protocol]:
                        iWebSitePort = host['port']
                        sWebSiteProtocol = protocol
                        sWebSiteOs = data['OS']
                        sWebSiteDb = data['db']
                        sWebSiteName = "%s:%s"%(sWebSiteIP, iWebSitePort)
                        print sWebSiteIP, iWebSitePort, sWebSiteProtocol
                        sDevelopmentLanguage = getPoweredBy(sWebSiteIP, iWebSitePort, sWebSiteProtocol)
                        if sDevelopmentLanguage == 'false': continue

                        selectSqlStr = "select * from t_website_servers where \
                                ip ='%s' and port='%s' and protocol='%s' and \
                                os='%s' and db='%s' and developmentLanguage='%s'"%(
                                sWebSiteIP, iWebSitePort, sWebSiteProtocol, sWebSiteOs,
                                sWebSiteDb, sDevelopmentLanguage)
                        count = cursor.execute(selectSqlStr)
                        if count: continue
                        insertSqlStr = "insert into t_website_servers(ip, port, \
                                protocol, os, db , developmentLanguage, webSiteId) values( \
                                '%s', '%s', '%s', '%s', '%s', '%s', 1)"%(
                                sWebSiteIP, iWebSitePort, sWebSiteProtocol, sWebSiteOs,
                                sWebSiteDb, sDevelopmentLanguage)
                        print insertSqlStr
                        cursor.execute(insertSqlStr)        


#获取主机的http头信息
def getPoweredBy(ip, port, pType='http'):
    try:
        conn = None
        if not ip:
            return False
        if pType == 'http':
            conn = httplib.HTTPConnection(ip, port, timeout=30)
        else:
            conn = httplib.HTTPSConnection(ip, port, timeout=30)
        conn.request('GET', '/')
        headers = conn.getresponse().getheaders()
        poweredBy = ''
        for header in headers:
            if header[0].lower() == 'x-powered-by': 
                poweredBy = header[1]
                if header[1].lower().find('jsp') != -1:
                    poweredBy = 'Java'
    except:
        poweredBy = 'false'
    return poweredBy


def main():
    ipList = getLANIp()
    data, filePaths = parserNmap(ipList)
    saveData(data)
    for filePath in filePaths:
        os.popen('rm -rf %s'%filePath)        


if __name__ == "__main__":
    main()
