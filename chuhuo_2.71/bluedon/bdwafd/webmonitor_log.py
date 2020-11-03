#! /usr/bin/env python
# -*-coding:utf-8 -*-


import time
import os
import re
import threading
import random
import subprocess
import datetime
from logging import getLogger
from config import config
from db import conn_scope, session_scope, Website, WebMonitor, rows2list, WebsiteServers
from config_sql import execute_sql, fetchall_sql, fetchone_sql, execute_sql_logs
from linkinglogsmonitor import parse_log
import calendar


nginx_log_path = "/usr/local/bdwaf/logs_proxy/access.log"


class WebMonitorLog(threading.Thread):
    # web 应用监控
    event = threading.Event()

    def __init__(self):
        super(WebMonitorLog, self).__init__(name=self.__class__.__name__)

    def start(self):
        getLogger('main').debug(self.__class__.__name__ + ' starting...')
        super(WebMonitorLog, self).start()
        getLogger('main').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('main').debug(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__ + ' Exited.')

    def proc_for_transparentbridge(self):
        get_sql = 'select * from t_website_nginx '
        old_size = fetchone_sql(get_sql)[1]
        new_size = os.path.getsize(nginx_log_path)
        now_utc = time.gmtime()
        get_websites_sql = "select distinct(sWebSiteName) from t_website,t_website_servers where t_website.id=t_website_servers.webSiteId"
        get_ips_sql = "select ip from t_website,t_website_servers where t_website.id=t_website_servers.webSiteId and t_website.sWebSiteName='%s'"
        for website in fetchall_sql(get_websites_sql):
            #getLogger('main').info('website is %s'% website)
            ip_list = []
            for ip in fetchall_sql(get_ips_sql % (website[0])):
                if ip[0]:
                    ip_list.append(ip[0])
            data_dict = parse_log(now_utc, ip_list, precision2=8, path_to_file = "/usr/local/bdwaf/logs_proxy/linking_num.log")
#            getLogger('main').info(data_dict)
            if data_dict:
#                getLogger('main').info("hello here")
                ntime = datetime.datetime.now()
                ntime = ntime.strftime("%Y%m%d %H:%M:%S").split()[0]
                table_name = "t_web_connections_%s" % ntime
                sql = create_table(table_name)
                execute_sql_logs(sql)
                insert_sql = "insert into " + table_name + "(sWebSiteName,iNewConnections,iConConnections,iTransactions,iTime,siteflow) values('%s','%s','%s','%s','%s','%s')"
                #getLogger('main').info('new size is  %s'% new_size)
                #getLogger('main').info('old size is %s' % old_size)
                if new_size > old_size:
                    site_flow = web_flow_monitor(old_size, ip_list)
                    #getLogger('main').info('size flow is %s' % site_flow)
                    #getLogger('main').info('iplist is %s' % ip_list)
                else:
                    site_flow = 0
                insert_sql_cmd = insert_sql % (website[0], data_dict["NEW_LINK_NUM"],
                                               data_dict["CURRENT_LINK_NUM"],
                                               data_dict["TRANSACTION_NUM"],
                                               calendar.timegm(now_utc), site_flow)
                execute_sql_logs(insert_sql_cmd)
        update_sql = "update t_website_nginx set nginxsizes=%s" % new_size
        execute_sql(update_sql)

    def proc(self):
        get_sql = 'select * from t_website_nginx '
        old_size = fetchone_sql(get_sql)[1]
        new_size = os.path.getsize(nginx_log_path)
        # print old_size
        with session_scope() as session:
            sites = rows2list(session.query(Website).all())
            # print sites
            if not sites:
                return
        for site in sites:
            # print site
            items = {}
            if self.event.isSet():
                return
            # web_ip = site["sWebSiteIP"]
            # web_port = site["iWebSitePort"]
            web_name = site["sWebSiteName"]
            web_id = site["id"]
            # web_ip_port = "%s:%s" % (web_ip, web_port)
            web_names = []
            ip_ports = []
            web_names.append(web_name)
            with session_scope() as session1:
                server_sites = rows2list(session1.query(WebsiteServers).filter(
                    WebsiteServers.webSiteId == web_id).all())
                for server_site in server_sites:
                    web_names.append(server_site["ip"])
                    ip_port = "%s:%s" % (server_site["ip"], server_site["port"])
                    ip_ports.append(ip_port)
            #print web_ip_port
            now = int(time.time())
            for i in ip_ports:
                out = subprocess.check_output("""netstat -n | awk '/^tcp/ {if($4=="%s"){++S[$NF]}} END {for(a in S) print a, S[a]}'""" % i, shell=True)
                out = out.split("\n")[:-1]
                for j in out:
                    item = j.split()
                    if item[0] in set(k for k in items):
                        items[item[0]] = int(items[item[0]]) + int(item[1])
                    else:
                        items[item[0]] = int(item[1])
            items.setdefault("TIME_WAIT", 0)
            items.setdefault("ESTABLISHED", 0)
            items.setdefault("FIN_WAIT1", 0)
            # print items
            ntime = datetime.datetime.now()
            ntime = ntime.strftime("%Y%m%d %H:%M:%S").split()[0]
            table_name = "t_web_connections" + "_" + "%s" % ntime
            sql = create_table(table_name)
            execute_sql_logs(sql)
            if new_size > old_size:
                site_flow = web_flow_monitor(old_size, web_names)
            else:
                site_flow = 0
            insert_sql = "insert into " + table_name + "(sWebSiteName,iNewConnections,iConConnections,iTransactions,iTime,siteflow)" + " values('%s','%s','%s','%s','%s','%s')"
            insert_sql_cmd = insert_sql % (web_name, items["TIME_WAIT"],
                                           items["ESTABLISHED"],
                                           items["FIN_WAIT1"],
                                           now, site_flow)
            execute_sql_logs(insert_sql_cmd)
        update_sql = "update t_website_nginx set nginxsizes=%s" % new_size
        execute_sql(update_sql)

    def run(self):
        create_nginx_log_table()
        while True:
            try:
                for _ in range(10):
                    if self.event.isSet():
                        return
                    time.sleep(1)
                if self.event.isSet():
                    return
                # sql = "select deploy from t_baseconfig;"
                # deploy = fetchone_sql(sql)[0]
                # getLogger('main').info('get deploy which is %s' % deploy)
                # if deploy == u'transparentbridge':
                    # self.proc_for_transparentbridge()
                    # delete_table()
                # else:
                self.proc()
                delete_table()
            except Exception, e:
                getLogger('main').exception(e)


def create_table(table_name):
    # 每天创建一个新的日志表
    sql = """CREATE TABLE IF NOT EXISTS %s (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10444 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;""" % table_name

    return sql


def delete_table():
    # 删除30天前的数据表
    table = "t_web_connections_"
    thirty_day_ago = (datetime.datetime.now() - datetime.timedelta(days=30))
    table_time = thirty_day_ago.strftime("%Y%m%d %H:%M:%S").split()[0]
    table_name = table + table_time
    delete_sql = "DROP TABLE %s" % table_name
    execute_sql_logs(delete_sql)


def web_flow_monitor(size, data):

    # 监控各个站点的流量单位B
    ip_flow = {}
    # print "zzz", ip_flow
    ip_num = {}
    # 正则匹配
    re_flow = re.compile('"' + '\D' + str(200) + '\D(\d+)\D')
    # re_time = re.compile("(\d+)/([a-zA-Z]+)/(\d+):(\d+:\d+:\d+\s+[+\d]+)")
    # 定义http状态码(你可以把日志里经常出现的状态码放在前面)
    code = [302, 206, 100, 101, 102, 201, 202, 203, 204, 205, 207, 300, 301,
            303,
            304, 305, 306, 307, 400, 401, 402, 403, 404, 405, 406, 407, 408,
            409,
            410, 411, 412, 413, 414, 415, 416, 417, 421, 422, 424, 425, 426,
            449,
            500, 501, 502, 503, 504, 505, 506, 507, 509, 510]
    # 定义月数的英文缩写格式
    mon = {"Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4", "May": "5",
           "Jun": "6",
           "Jul": "7", "Aug": "8", "Sep": "9", "Oct": "10", "Nov": "11",
           "Dec": "12"}

    with open(nginx_log_path, "r") as fp:
        fp.seek(size)
        logs = fp.readlines()
        for line in logs:
            try:
                ip = line.split()[0]
            except:
                continue
            if ip not in data:
                # print "wwww"
                continue
            flow = re_flow.findall(line)
            if not flow:
                for i in code:
                    codere = re.compile('"' + '\D' + str(i) + '\D(\d+)\D')
                    flow = codere.findall(line)
                    if flow:
                        break
            if not flow:
                break
            if ip in set(k.lower() for k in ip_flow):
                ip_num[ip] += 1
                ip_flow[ip] = int(ip_flow[ip]) + int(flow[0])
            else:
                ip_num[ip] = 1
                ip_flow[ip] = int(flow[0])
        # print "YYY", ip_flow
        if not ip_flow:
            return 0
        else:
            total = 0.0
            for name in data:
                if name in ip_flow:
                    total += float(ip_flow[name]/1024.0)
            return total

            # return int(ip_flow[data]/1024)


def create_nginx_log_table():
    # 创建一个记录nginx日志的库，记录日志的size

    sql = """CREATE TABLE IF NOT EXISTS `t_website_nginx` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nginxsizes` bigint(20) DEFAULT NULL COMMENT 'nginx log',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;"""
    execute_sql(sql)
    sql_get = 'select * from t_website_nginx '
    result = fetchone_sql(sql_get)
    if not result:
        execute_sql('insert into t_website_nginx(nginxsizes) values("0")')


if __name__ == "__main__":
    a = WebMonitorLog()
    a.proc()
    # a.start()
    # table_name = "t_web_connections_2%"
    # sql = "SHOW TABLES FROM waf LIKE '%s'" % table_name
    # a = [i[0] for i in fetchall_sql(sql)]
    # print a
    # delete_table()
    # create_nginx_log_table()
    # sql = 'update t_website_nginx set nginxsizes=%s' % 20
    # execute_sql(sql)
    # sizes = os.path.getsize("/usr/local/bluedon/bdwaf/logs/access.log")
    # a = web_flow_monitor(0, "addons.g-fox.cn")
    # print a
    # from db import conn_scope, session_scope, WebsiteGroup, WebMonitor, \
    #     rows2list
    #
    # with session_scope() as session:
    #     sites = rows2list(session.query(WebsiteGroup).all())
    #     print sites



