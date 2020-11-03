#! /usr/bin/env python
# -*- coding:utf-8 -*-


import time
import datetime
import re
import os
import json
import threading
from config_sql import execute_sql, fetchall_sql, fetchone_sql, execute_sql_logs
from logging import getLogger
from helperforabanalyse import dict_combine
import pickle



FILE_PATH = "/usr/local/bluedon/bdwaf/logs/access.log"
#超过的倍数
MAGNIFICATION = 2
# re_time = re.compile(r"(\d+)/([a-zA-Z]+)/(\d+):(\d+:\d+:\d+\s+[+\d]+)")
#re_ip = re.compile(r"(\d{3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
re_flow = re.compile(r'"' + '\D' + str(200) + '\D(\d+)\D')
code = [302, 206, 100, 101, 102, 201, 202, 203, 204, 205, 207, 300, 301,
        303,
        304, 305, 306, 307, 400, 401, 402, 403, 404, 405, 406, 407, 408,
        409,
        410, 411, 412, 413, 414, 415, 416, 417, 421, 422, 424, 425, 426,
        449,
        500, 501, 502, 503, 504, 505, 506, 507, 509, 510]

#站点信息获取
def get_website_data():
    websitestr = "select id, sWebSiteName, daymaxtraffic, dayipmaxvisit, modelingendday from t_website"
    webSiteDatas = {}
    for webSiteData in fetchall_sql(websitestr):
        traffic = webSiteData[2] and json.loads(webSiteData[2]) or {}
        if not webSiteData[4]:
            tag = "inactive"
        else:
            tag = (webSiteData[4] > datetime.date.today()) and "analyse" or "report"
        if not traffic and tag == "report":
            continue
        webSiteDatas[webSiteData[1]] = {
                "id": webSiteData[0],
                "name": webSiteData[1],
                "traffic": traffic,
                "visit": webSiteData[3] and json.loads(webSiteData[3]) or {},
                "modelingendday": webSiteData[4],
                "server": [webSiteData[1]],
                "tag": tag}
        serverStr = "select ip from t_website_servers where webSiteId = %d"%webSiteData[0]
        for serverData in fetchall_sql(serverStr):
            webSiteDatas[webSiteData[1]]["server"].append(serverData[0])
    return webSiteDatas

#日志分析
def parse_log(size):
    ip_dict = {}
    with open(FILE_PATH, "r") as fp:
        fp.seek(size)
        for line in fp:
            traffic_math = re_flow.search(line)
            if not traffic_math:
                for i in code:
                    re_traffic = re.compile(r'"' + '\D' + str(i) + '\D(\d+)\D')
                    traffic_math = re_traffic.search(line)
                    if traffic_math:
                        break
            try:
                tempIpListData = line.split("-")[0]
                key = (tempIpListData[0] != " ") and "%s_%s"%(tempIpListData.split()[0],
                        tempIpListData.split()[1]) or "unkonw_%s"%(tempIpListData.split()[0])
                traffic = traffic_math.groups()[0]
            except Exception, e:
                pass
            else:
                ip_dict.setdefault(key, {"number": 0, "traffic": 0})["number"] += 1
                ip_dict.setdefault(key, {"number": 0, "traffic": 0})["traffic"] += int(traffic)
    return ip_dict            

#结果入库
def result_save(data):
    webSiteDatas = get_website_data()
    #print "----------------------------\n", webSiteDatas, "\n----------------------------"
    hour = datetime.datetime.now().hour
    nowdate  = str(datetime.datetime.today()).split()[0]
    hour -= 1
    for webSiteName, webSite in webSiteDatas.items():
        if webSite["tag"] == "inactive": 
            continue
        webSite["visit"].setdefault(str(hour), 0)
        webSite["traffic"].setdefault(str(hour), 0)
        newTraffic = 0
        sqlStr = "insert into logs.t_webvisitinglogs(time, normalvalue, abnormalvalue, type, websiteid, ip, date) values"
        sqllength = len(sqlStr)
        for key, value in data.items():
            tempIp = key.split("_")
            sourceIp = tempIp[0]
            remoteIp = tempIp[1]
            flow = value["traffic"]/1024.0
            if sourceIp in webSite["server"]:
                if webSite["visit"][str(hour)] < value["number"]:
                    if webSite["tag"] == "report":
                        if (webSite["visit"][str(hour)] * MAGNIFICATION) < value["number"]:
                            if len(sqlStr) > sqllength:
                                    sqlStr += ",('%s', %f, %f, 1, %d, '%s', '%s')"%(hour, 
                                        webSite["visit"][str(hour)], value["number"], webSite["id"], remoteIp, nowdate)
                            else:
                                sqlStr += "('%s', %f, %f, 1, %d, '%s', '%s')"%(hour,
                                        webSite["visit"][str(hour)], value["number"], webSite["id"], remoteIp, nowdate)
                    else:
                        webSite["visit"][str(hour)] = value["number"]
                newTraffic += (value["traffic"]/1024.0)
        if webSite["traffic"][str(hour)] < newTraffic:
            if webSite["tag"] == "report":
                if (webSite["traffic"][str(hour)] * MAGNIFICATION) < newTraffic:
                    if len(sqlStr) > sqllength:
                        sqlStr += ",('%s', %f, %f, 0, %d, '', '%s')"%(hour, webSite["traffic"][str(hour)],
                            newTraffic, webSite["id"], nowdate)
                    else:
                        sqlStr += "('%s', %f, %f, 0, %d, '', '%s')"%(hour, webSite["traffic"][str(hour)],
                            newTraffic, webSite["id"], nowdate)

            else:
                webSite["traffic"][str(hour)] = newTraffic
                sqlStr = "UPDATE waf.t_website SET daymaxtraffic='%s', dayipmaxvisit='%s' where id=%d"% \
                        (json.dumps(webSite["traffic"]), json.dumps(webSite["visit"]), webSite["id"])
        if len(sqlStr) > sqllength:
            print sqlStr
            execute_sql_logs(sqlStr)


class AbnormalAnalysis(threading.Thread):

    def __init__(self):
        super(AbnormalAnalysis, self).__init__(name=self.__class__.__name__)
        self.event = threading.Event()

    def start(self):
        getLogger('main').debug(self.__class__.__name__ + ' starting...')
        super(AbnormalAnalysis, self).start()
        getLogger('main').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('main').debug(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__ + ' Exited.')

    def proc(self):
        if self.event.isSet():
            return
        get_sql = 'select * from t_website_nginx '
        old_size = fetchone_sql(get_sql)[2]
        new_size = os.path.getsize(FILE_PATH)
        PATH_TO_PICKLE_FILE = 'data.pickle'
        minute = datetime.datetime.now().minute
        if new_size > old_size and 1 > minute >= 0:
            result_save(parse_log(old_size))
            execute_sql_logs("UPDATE waf.t_website_nginx SET hournginxsize=%d"%new_size)
            return
        if os.path.exists(PATH_TO_PICKLE_FILE) and 1 > minute >= 0:
            data_part1 = parse_log(0)
            #result=fetchall_sql(sql)
            #data_part2 = data_change(result)
            fp=open(PATH_TO_PICKLE_FILE, 'rb')
            data_part2 = pickle.load(fp)
            getLogger('main').info(data_part2)
            fp.close()
            os.remove(PATH_TO_PICKLE_FILE)
            data = dict_combine(data_part1, data_part2)
            getLogger('main').info("part1%s part2%s after combine%s" % (data_part1, data_part2,data))
            result_save(data)
            execute_sql_logs("UPDATE waf.t_website_nginx SET hournginxsize=%d"%new_size)



    def run(self):
        while True:
            try:
                for _ in range(60):
                    if self.event.isSet():
                        return
                    time.sleep(1)
                if self.event.isSet():
                    return
                self.proc()
            except Exception, e:
                getLogger('main').exception(e)


if __name__ == "__main__":
    a = AbnormalAnalysis()
    a.start()
    #b = ParseLog().count(0)
    #result_save(parse_log(0))
    pass
