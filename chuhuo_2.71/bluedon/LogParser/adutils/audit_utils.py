#!/usr/bin/env python
# coding=utf-8


import os
import sys
import time
import logging
import geoip2.database
from netaddr import *
from collections import deque
from config import fetchall_sql as fcal_3306
reload(sys)
sys.setdefaultencoding('utf-8')

# mmdb file path
GEOLITE_CITY_MMDB = '/usr/local/bluedon/LogParser/GeoLite2-City.mmdb'

# text color
_colorred = "\033[01;31m{0}\033[00m{1}"
_colorgrn = "\033[02;32m{0}\033[00m{1}"

ERR_TEXT = lambda x,y='' : _colorred.format(x, y)
TIP_TEXT = lambda x,y='' : _colorgrn.format(x, y)

def timestr_to_timestamp(s, fmt='%Y-%m-%d %H:%M:%S'):
    try:
        ta = time.strptime(s, fmt)
        return int(time.mktime(ta))
    except Exception as e:
        print 'wrong time: ', e
        print s
        return None


def int_to_ip(i):
    try:
        ip = IPAddress(i)
        return str(ip)
    except:
        return None

class geo_info_item:
    from maxminddb import MODE_MEMORY
    geo_info_cache = {}
    cls_georeader = geoip2.database.Reader(GEOLITE_CITY_MMDB, mode=MODE_MEMORY)
    def __init__(self):
        self.continent = ''
        self.country = ''
        self.city = ''
        self.subdivisions = ''
        self.scc_flag = ''            # 0 境外
        # self.georeader = geoip2.database.Reader(GEOLITE_CITY_MMDB)
        self.georeader = self.get_geoinfo_reader()
        self.scc_flag_infos = {u'中国':'1', u'台湾':'2', u'香港':'3', u'澳门':'4'}

    @classmethod
    def get_geoinfo_cache(cls, dip):
        #
        return cls.get_geoinfo_cache.get(dip, None)

    @classmethod
    def add_geoinfo_cache(cls, dip, item):
        if len(cls.get_geoinfo_cache) > 1024:
            pass
        cls.get_geoinfo_cache[dip] = item

    @classmethod
    def get_geoinfo_reader(cls):
        return cls.cls_georeader


    def get_geoinfo(self, dip):
        geoinfo = None
        try:
            geoinfo = self.georeader.city(dip)
        except:
            pass
            # logging.debug("can not found geoinfo about %s", dip)

        if geoinfo != None:
            self.continent = ''
            if geoinfo.continent != None:
                try:
                    self.continent = geoinfo.continent.names['zh-CN']
                except:
                    try:
                        self.continent = geoinfo.continent.names['en']
                    except:
                        pass

            self.country = ''
            if geoinfo.country != None:
                try:
                    self.country = geoinfo.country.names['zh-CN']
                except:
                    try:
                        self.country = geoinfo.country.names['en']
                    except:
                        pass

            self.city = ''
            if geoinfo.city != None:
                try:
                    self.city = geoinfo.city.names['zh-CN']
                except:
                    try:
                        self.city = geoinfo.city.names['en']
                    except:
                        pass

            self.subdivisions = ''
            if geoinfo.subdivisions != None:
                try:
                    (sd,) = geoinfo.subdivisions
                    self.subdivisions = sd.names['zh-CN']
                except:
                    try:
                        self.subdivisions = sd.names['en']
                    except:
                        pass


        if self.continent != None:
            try:
                self.continent = self.continent.decode().encode('utf8')
            except:
                pass
        if self.country != None:
            try:
                self.country = self.country.decode().encode('utf8')
            except:
                pass
        if self.city != None:
            try:
                self.city = self.city.decode().encode('utf8')
            except:
                pass
        if self.subdivisions != None:
            try:
                self.subdivisions = self.subdivisions.decode().encode('utf8')
            except:
                pass
        self.scc_flag = self.scc_flag_infos.get(self.country.decode(), '0')

# from collections import OrderedDict
# def get_scc(dip, history=OrderedDict()):
def get_scc(dip, history={}):
    MAX = 1024
    try:
        if dip in history:
            # update query history
            return history[dip]
        #scc and scc_flag
        geo = geo_info_item()
        geo.get_geoinfo(dip)
        geo_info = [
            info for info in
            [geo.continent, geo.country, geo.subdivisions, geo.city]
            if info
        ]
        scc = '|'.join(geo_info) if geo_info else 'local'
        scc_flag = str(geo.scc_flag) if scc != 'local' else '5'
        overseas = True if scc_flag == '0' else False
        # add new ip to history, delete ip if history length is greater than MAX
        if len(history) > MAX:
            history.popitem()
            pass
        history[dip] = scc, scc_flag, overseas
        return scc, scc_flag, overseas
    except:
        print 'error'
        return '-', '5', False


def get_auth_detail():
    import json
    user_sql = 'SELECT sUserName, iGroupID, sIP FROM m_tbusers WHERE iStatus=1;'
    group_sql = 'SELECT id, sGroupName FROM m_tbgroup;'

    _nobody = 'anonymous'

    _user = {}
    _group = {}
    # get group name
    # for res in fcal_3306(group_sql):
    #     _group[res['id']] = res['sGroupName']

    # for res in fcal_3306(user_sql):
    #     for _ip in res['sIP'].split(','):
    #         if _ip != '':
    #             _user[_ip] = (res['sUserName'], _group.get(int(res['iGroupID']), _nobody))

    try:
        with open('/usr/local/bluedon/conf/online_users', 'r') as fp:
            lines = fp.readlines()

        js_lines = json.loads(''.join(lines))
        for ip, ip_info in js_lines.items():
            _user[ip] = (ip_info[0], ip_info[2])
    except Exception as e:
        pass


    return _user


if __name__ == '__main__':
    print get_auth_detail()
    # import time
    # ip = '203.192.9.7'
    # ips = ['108.61.214.131', '108.61.214.132', '108.61.214.133', '108.61.214.134']
    # ast = time.time()
    # for i in range(1):
    #     # st = time.time()
    #     res = get_scc(ip)
    #     # for _ip in ips:
    #     #     res = get_scc(_ip)
    #     print 'ip: %s, from: %s' % (ip, res[0])
    #     # et = time.time()
    #     # print '%d Try time = %s' % (i, (et - st))
    # aet = time.time()
    # print 'ALL Try time = %s' % (aet - ast)
