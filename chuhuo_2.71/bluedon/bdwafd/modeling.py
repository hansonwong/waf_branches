#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import datetime
import json
import os
import time
from copy import deepcopy
from logging import getLogger
from jinja2 import Environment, PackageLoader, FileSystemLoader
from config import config
from MySQL import MySQL

class Modeling(threading.Thread):
    def __init__(self):
        super(Modeling, self).__init__(name = self.__class__.__name__)
        self.db = None
        self.modelingpath = '/usr/local/bluedon/bdwaf/conf/modeling'
        self.event = threading.Event()
    
    def start(self):
        super(Modeling, self).start()
        getLogger('main').info(self.__class__.__name__+ ' started.')
    
    def stop(self):
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__+ ' Exited.')
    
    def get_site(self):
        """
        获取需要建模的站点
        """
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.db.query("SELECT * FROM t_website WHERE endTime <= '%s' AND mstatus='1'"%nowtime)
        return self.db.fetchAllRows()
    
    def get_t_modeling_id(self, host, url, method, websiteid, port):
        """
        根据建模站点域名/IP, url请求页面，请求方式，站点ID，端口获取模型ID，
        若无记录则添加站点-端口-请求页面-请求方式的记录。

        Return：
            模型ID
        """
        uri = url.split('?')[0]
        if uri[-1] == '/':
            uri = uri[:-1]
        self.db.query("SELECT * from t_modeling WHERE host='%s' AND path='%s' AND port=%d"%(host,  uri, port))
        result = self.db.fetchOneRow()
        if result:
            return result['id']
        else:
            return self.db.insert("INSERT INTO t_modeling(host, path, method, websiteId, port) VALUES('%s', '%s', '%s', %d, %d)"%(host, uri, method, websiteid, port)) 

    def get_t_modeling_detail(self, modelingId, name, value, max_length=None, min_length=None):
        """
        根据模型ID，参数名获取model_detail记录
        model_detail中记录了模型对应的URL参数的type, name, 最短和最长长度(?)
        """
        self.db.query("SELECT * from t_modeling_detail WHERE modelingId=%d AND name='%s'"%(modelingId, name))
        result = self.db.fetchOneRow()
        if not max_length:
            max_length = min_length = len(value)

        # 若model_detail中无此模型ID、url参数记录则插入该记录
        if not result:
            modeling_detail_id = self.db.insert("INSERT INTO t_modeling_detail(modelingId, type, minlength, maxlength, name, is_use) VALUES(%d,'%s', %d, %d, '%s', 1)"%(modelingId, value.isdigit() and 'number' or 'str', min_length, max_length, name))
            self.db.query("SELECT * from t_modeling_detail WHERE id=%d"%modeling_detail_id)
            result = self.db.fetchOneRow()

        # 检查model_detail中minlength & maxlength记录，提高长度精确度(?)并更新记录
        if result['minlength'] > min_length:
            self.db.update("UPDATE t_modeling_detail SET minlength=%d WHERE id=%d"%(min_length, result['id']))
            self.db.query("SELECT * from t_modeling_detail WHERE id=%d"%result['id'])
            result = self.db.fetchOneRow()
        if result['maxlength'] < max_length:
            self.db.update("UPDATE t_modeling_detail SET maxlength=%d WHERE id=%d"%(max_length, result['id']))
            self.db.query("SELECT * from t_modeling_detail WHERE id=%d"%result['id'])
            result = self.db.fetchOneRow()
        return result

    def set_fwb(self, host, start, end, websiteid, port):
        """设置防误报
        从入侵日志中获取动态建模设置的起止时间内日志中对应站点的入侵记录，
        根据请求页面及方法获取站点模型，
        根据获取的入侵记录中URL参数获取站点模型参数记录(若无记录则更新)
        将该入侵记录对应的规则ID以及对应站点模型参数记录等插入站点模型参数规则记录

        Args:
            host:进行建模的站点域名/IP
            start,end:起止时间
            websiteid, port:站点ID，端口
        """
        self.db.query("SELECT * FROM logs.t_alertlogs WHERE Host='%s' AND LogDateTime >= '%s' AND LogDateTime <= '%s' AND DestinationPort='%s'"%(host, start, end, port))
        for logs in self.db.fetchAllRows():
            if not logs:
                continue
            temp_match_data = logs['MatchData']
            if temp_match_data.find('ARGS:') == -1:
                continue

            mid = self.get_t_modeling_id(host, logs['Url'][logs['Url'].find('/'):], logs['HttpMethod'], websiteid, port)
            match_data = temp_match_data[temp_match_data.find('ARGS:'):]
            match_data_list = match_data.split(':')
            parameter_name = match_data_list[1]
            parameter_value = match_data_list[2]
            modeling_detail = self.get_t_modeling_detail(mid, parameter_name, parameter_value)
            # 此处的命中次数和命中频率并未作任何处理
            self.db.insert("INSERT ignore INTO t_modeling_detail_rule(realRuleId, is_use, hitCount, hitChance, modelingDetailId, modelingId, websiteId) VALUES('%s', 1, 0, 0, %d, %d, %d)"%(logs['RuleID'], modeling_detail['id'], mid, websiteid))
    
    def get_access_report(self, websiteid, host, port):
        """
        获取访问日志中URL参数记录，
        检查"站点模型参数记录"中是否有该参数的记录，
        若无则添加此参数。

        Args:
            websiteid:站点ID
            host:主机IP
            port:端口
        """
        self.db.query("SELECT * from t_urltrait WHERE host='%s' AND port=%d"%(host, port))
        for logs in self.db.fetchAllRows():
            # 目前还没有收集post的数据，需要进一步完善
            if not logs:# or logs['method'] == 'post':
                continue
            # 过滤没有参数特征的
            trait = json.loads(logs['trait'])
            # if not trait:
            #     continue
            
            mid = self.get_t_modeling_id(host, logs['path'], logs['method'], websiteid, port)
            for key, value in trait.items():
                mtype = 'number' in value['type'] and 'number' or 'str'
                modeling_detail = self.get_t_modeling_detail(mid, key, '1', value['max_length'], value['min_length'])

    def proc(self):
        self.db = MySQL(config['db'])
        sites = self.get_site()
        for site in sites:
            if not site:
                continue
            self.set_fwb(site['sWebSiteName'], site['beginTime'], site['endTime'], site['id'], site['iWebSitePort'])
            self.get_access_report(site['id'], site['sWebSiteName'], site['iWebSitePort'])
            # 将mstatus设为2（代表已完成？）会导致该站点只执行一次上两行函数即退出学习
            self.db.update("UPDATE t_website SET mstatus=2 WHERE id=%d"%site['id'])
            os.popen("echo CMD_NGINX >> /tmp/bdwaf.fifo")
        self.db.close()
    
    def run(self):
        while 1:
            try:
                if self.event.isSet():
                    break
                self.proc()
                time.sleep(60)
            except Exception, e:
                getLogger('main').exception(e)

if __name__ == "__main__":
    Modeling().proc()
