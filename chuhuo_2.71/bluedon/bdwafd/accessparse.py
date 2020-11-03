#!/usr/bin/env python
#-*-coding:utf-8-*-

"""
解析bdwaf/logs/access.log文件
将访问的站点域名/IP、端口、请求的url页面、请求方式
及（动态建模中主要的）参数信息保存入t_urltrait数据库中
"""


import re
import os
import time
import json
import threading
import MySQLdb
from logging import getLogger
from config import config
from db import conn_scope
from urlparse import urlparse

isDigit = re.compile(r'^-?(\.\d+|\d+(\.\d+)?)')

class AccessParse(threading.Thread):
    def __init__(self):
        super(AccessParse, self).__init__(name = self.__class__.__name__)
        self.last_pos = 0
        self.accessPath = '/usr/local/bluedon/bdwaf/logs/access.log'
        self.fileSize = 0
        self.tag = False
        self.sites = []
        self.event = threading.Event()

    def start(self):
        getLogger('main').debug(self.__class__.__name__+ ' starting...')
        #print (self.__class__.__name__+ ' starting...')
        super(AccessParse, self).start()
        getLogger('main').info(self.__class__.__name__+ ' started.')
        #print (self.__class__.__name__+ ' started.')
    
    def stop(self):
        getLogger('main').debug(self.__class__.__name__+ ' Exiting...')
        #print (self.__class__.__name__+ ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__+ ' Exited.')
        #print (self.__class__.__name__+ ' Exited.')
    
    def checkFile(self):
        """
        获取最近一次读取access.log的游标位置t_urltraitsupport.lastPos
        并更新数据库中access.log的文件大小记录t_urltraitsupport.fileSize
        """
        with conn_scope(**config['db']) as (conn, cursor):
            select_sql = "select lastPos, fileSize from waf.t_urltraitsupport"
            cursor.execute(select_sql)
            result = cursor.fetchone()
            filesize = os.path.getsize(self.accessPath)
            sql_str = "update t_urltraitsupport set `fileSize`=%s"%filesize
            self.last_pos = result[0]
            if filesize < result[1]:
                self.last_pos = 0
            cursor.execute(sql_str)

    def urlParse(self, urlStr):
        """解析access.log的url
        分析日志中

        Args:
            urlStr:待解析的日志
        Return:
            data:包含host，method，port，parameters，urlStr的字典
        """
        url_data = urlStr.split(" ")
        data = {}
        if len(url_data) < 9 or (url_data[6] == '"-"' == url_data[9] and url_data[8] == '0'):
            return False
        data['port'] = urlparse(url_data[11][1:-1]).netloc
        data['port'] = data['port'].find(":") != -1 and data['port'].split(":")[1] or '80'
        data["host"] = url_data[0]
        if data["host"] not in self.sites:
            return False
        temp_url_data = url_data[7]
        path_data = temp_url_data.split("?")
        data["path"] = path_data[0]
        errcode = ["000", "400", "401", "500", "200" ,"404"]
        method = ["GET", "POST", "HEAD", "OPTIONS", "DELETE", "SEARCH",
                "PROPFIND", "CHECKOUT", "CHECHIN", "MKCOL", "PROPPATCH",
                "SHOWMETHOD", "TEXTSEARCH", "COPY", "LOCK", "LINK", "SPACEJUMP",
                "PUT", "CONNECT", "MOVE", "UNLOCK", "UNLINK", "TRACK", "DEBUG", "UNKNOWN"]
        data["parameters"] = {}
        data["method"] = url_data[6][1:]

        # 判断不符合规则的日志记录
        if data["path"] == "" or data["path"] == '/' or data["path"] in \
            errcode or url_data[8] in errcode or data["method"] not in method:
            return False
            
        data["urlStr"] = urlStr
        
        # 解析url中的参数如"?keywords=test", 保存为{'keywords':{'value':'test', 'type':'str', 'length':'4'}, {}, ...}
        if len(path_data) >= 2:
            parameter_data = path_data[1].split("&")
            for parameter in parameter_data:
                if parameter.find("=") != -1:
                    temp_parameter_data = parameter.split("=")
                    variate = temp_parameter_data[0]
                    value = temp_parameter_data[1]
                    length = len(value)
                    value_type = "str"
                    if isDigit.search(value):
                        value_type = "number"
                    data["parameters"][variate] = {"value":value, "type": value_type, "length": length}
        return data
    

    def get_sites(self):
        """获取学习期内的站点"""
        with conn_scope(**config['db']) as (conn, cursor):
            cursor = conn.cursor(cursorclass =MySQLdb.cursors.DictCursor)
            sql_str = "SELECT * FROM t_website WHERE mstatus=1"
            cursor.execute(sql_str)
            sites = cursor.fetchall()
            self.sites = []
            for site in sites:
                self.sites.append(site['sWebSiteName'])
    

    def proc(self):
        self.checkFile()
        self.get_sites()
        self.tag = True
        #getLogger('main').info("access Parse proc start")
        with conn_scope(**config['db']) as (conn, cursor):
            with open(self.accessPath) as fp:
                fp.seek(self.last_pos)
                line = 'True'
                while line:
                    line = fp.readline().strip()
                    self.last_pos = fp.tell()
                    if line and line != 'True':
                        url_data = self.urlParse(line)
                        if url_data:
                            self.saveResult(url_data)
            sql_str = "update t_urltraitsupport set `lastPos`=%s"%self.last_pos
            cursor.execute(sql_str)
        self.tag = False

    def saveResult(self, data):
        """更新t_urltrait，
        保存URL解析结果中parameters到t_urltrait.trait中
        """
        with conn_scope(**config['db']) as (conn, cursor):
            select_sql = "select `trait` from waf.t_urltrait where `host`='%s' and `method`='%s' and `path`='%s' and port=%d"%(data["host"].encode('string-escape'), data["method"].encode('string-escape'), data["path"].encode('string-escape'), int(data['port']))
            cursor.execute(select_sql)
            result = cursor.fetchone()
            variate_keys = data["parameters"].keys()
            # 若已存在该站点域名/IP、端口、请求方法、路径的记录则更新其参数数据
            if result:
                temp_trait = json.loads(result[0])
                for key in variate_keys:
                    trait = {}
                    if temp_trait.has_key(key):
                        trait = temp_trait[key]
                        length = data["parameters"][key]["length"]
                        value_type = data["parameters"][key]["type"]
                        if length > trait["max_length"]: trait["max_length"] = length
                        if length < trait["min_length"]: trait["min_length"] = length
                        if value_type not in trait["type"]: trait["type"].append(value_type)
                    else:
                        trait["min_length"] = trait["max_length"] = data["parameters"][key]["length"]
                        trait["type"] = [data["parameters"][key]["type"]]
                # 此时并未将修改后的trait数据更新回数据库
                sql_str = "update waf.t_urltrait set `trait`='%s' where `host`='%s' and `method`='%s' and `path`='%s' and `port`=%d"%(json.dumps(temp_trait), data["host"].encode('string-escape'), data["method"].encode('string-escape'), data["path"].encode('string-escape'), int(data['port']))
                #getLogger('main').info("sql_str: %s"%sql_str)
                cursor.execute(sql_str)
            else:
                temp_trait = {}
                for key in variate_keys:
                    trait_data = data["parameters"][key]
                    trait = {"type": [trait_data["type"]], "max_length": trait_data["length"], "min_length": trait_data["length"]}
                    temp_trait[key] = trait
                sql_str = "insert into waf.t_urltrait(`host`, `method`, `path`, `trait`, `urlStr`, `port`) values('%s', '%s', '%s', '%s', '%s', %d)"%(data["host"], data["method"], data["path"].encode('string-escape'), json.dumps(temp_trait), data["urlStr"].replace("'",'"').encode('string-escape'), int(data['port']))
                #getLogger('main').info("sql_str: %s"%sql_str)
                cursor.execute(sql_str)

    def run(self):
        while(1):
            try:
                if self.event.isSet():
                    break
                #getLogger('main').info("AccessParse tag: %s"%self.tag)
                if not self.tag:
                    self.proc()

                #time.sleep(600)
                time.sleep(10)
            except Exception, e:
                self.tag = False
                getLogger('main').exception(e)
                #print (e)


if __name__ == "__main__":
    pass
