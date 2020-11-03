#!/usr/bin/env python
# coding=utf-8

import os
import sys
import json

if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from db.mysql_db import select
if '/usr/local/bluedon' in sys.path:
    sys.path.remove('/usr/local/bluedon')
reload(sys)
sys.setdefaultencoding('utf-8')

CONF_FILE_PATH = '/etc/suricata/audit/filter/filter.json'

CONF_TB = 'm_tburl_filter_ips'
SQL_BY_ID = 'SELECT * FROM {tb} WHERE id={idx};'

TIME_PLAN_TB = {1: 'm_tbtimeplan_single', 2: 'm_tbtimeplan_loop'}
ADDRESS_TB = {3: 'm_tbaddress_list', 4: 'm_tbaddressgroup'}
URL_LIST_TB = 'm_tburlgroup'

def get_url_filter_conf():
    SQL_BY_ID_CONF = 'SELECT * FROM {tb} WHERE iStatus=1 \
        ORDER BY iOrder DESC;'.format(tb=CONF_TB)
    return select(SQL_BY_ID_CONF)

def get_timeplan(type_, idx):
    return select(SQL_BY_ID.format(tb=TIME_PLAN_TB[type_], idx=idx))

def get_ipaddress(type_, idx):
    ret = list()
    if type_ not in ADDRESS_TB: return ret
    if 'm_tbaddressgroup' == ADDRESS_TB[type_]:
        r = select(SQL_BY_ID.format(tb=ADDRESS_TB[type_], idx=idx))[0]
        for ridx in r['sIP'].split(','):
            r_ = select(SQL_BY_ID.format(tb=ADDRESS_TB[3], idx=ridx))
            [ ret.append(r__) for r__ in r_ ]
        return ret
    else:
        return select(SQL_BY_ID.format(tb=ADDRESS_TB[type_], idx=idx))

def ip_expand(ip_str, ip_type=None, ip_split='/'):
    """
        ip_type: range/mask
    """
    from netaddr import IPAddress, IPRange, IPNetwork
    support_types = ('range', 'mask')
    if ip_type not in support_types:
        return ip_str

    ret_lst = list()
    ip_count = 0
    if ip_type == 'mask':
        ips = IPNetwork(ip_str)

    elif ip_type == 'range':
        ips = IPRange(*ip_str.split(ip_split))

    for ip in ips:
        ret_lst.append(str(ip))
        ip_count += 1
        if ip_count >= 1000: return ret_lst

    return ret_lst

def get_urllist(idx):
    idx = int(idx)
    if idx == 0:
        return [0]
    print(SQL_BY_ID.format(tb=URL_LIST_TB, idx=idx))
    return select(SQL_BY_ID.format(tb=URL_LIST_TB, idx=idx))

def get_url_frompath(p):
    ret_lst = list()
    if not os.path.exists(p):
        return ret_lst

    fp = open(p, 'r')
    try:
        while 1:
            lines = fp.readlines()
            if len(lines) > 0: ret_lst.extend([l.strip().rstrip() for l in lines])
            else: break
    finally:
        fp.close()

    return ret_lst


def get_url_typepath(idx=None):
    ret = dict()
    if idx is None:
        SQL = 'SELECT sURLGroupName, sURL FROM m_tburlgroup WHERE iType=1;'
    else:
        SQL = 'SELECT sURLGroupName, sURL FROM m_tburlgroup WHERE id=%d;' % int(idx)

    for r in select(SQL):
        ret[r['sURLGroupName']] = r['sURL']

    return ret



def get_app_id(app_id):

    SEARITYSTRATE_TB = 'm_tbSearitystrate'
    def get_confing():
        SQL_BY_ID_CONF = 'SELECT * FROM {tb} WHERE iStatus=1 \
            ORDER BY iSort DESC;'.format(tb=SEARITYSTRATE_TB)
        return select(SQL_BY_ID_CONF)

    rlist = list()
    SQL_BY_ID = "SELECT * FROM m_tbdefault_app_list WHERE app_id_ten='{}';"
    r = select(SQL_BY_ID.format(app_id))[0]
    if int(r.get('app_id_ten', -1)) != int(app_id): return rlist

    if int(r['class_3']) == 0:
        # parent id
        c1 = r['class_1']
        c2 = r['class_2']
        if int(c2) == 0:
            SQL_BY_CLASS = "SELECT * FROM m_tbdefault_app_list WHERE \
                class_1='{c1}';".format(c1=c1)
        else:
            SQL_BY_CLASS = "SELECT * FROM m_tbdefault_app_list WHERE \
                class_1='{c1}' AND class_2='{c2}';".format(c1=c1, c2=c2)
        for app in select(SQL_BY_CLASS):
            rlist.append(int(app['app_id_ten']))

    else:
        # single id
        rlist.append(int(app_id))
        pass

    return rlist




def make_url_filter_conf(*args, **kwargs):
    # file path check
    conf_path = os.path.split(CONF_FILE_PATH)[0]
    if not os.path.exists(conf_path):
        os.system('/usr/bin/mkdir -p {path}'.format(path=conf_path))
    # get all config record from db
    confs = get_url_filter_conf()
    if confs is None:
        print '[url_filter_audit] No rules config'
        return

    conf_lst = list()
    ip_lst = list()
    IP_ALL = 0
    URL_ALL = 0
    APP_ALL = 0


    for r in confs:
        # if ip is all
        # print r
        ip_address = get_ipaddress(r['iType'], r['iTypeValue'])
        for ip in ip_address:
            if ip['sAddress'] == '0.0.0.0':
                IP_ALL = 1
                ip_lst = list()
                break
            else:
                ip_type = {'1': 'mask', '2': 'range'}[ip['sAddtype']]
                # expand all ip
                ip_str = '/'.join((ip['sAddress'], ip['sNetmask']))
                ip_lst = ip_expand(ip_str, ip_type)

        # common values
        url_lst = list()
        app_lst = list()
        filter_type = int(r['iUrlandAppType'])
        action = r['iAction']
        name = str(r['sName'])
        id_ = int(r['id'])
        eff_time = '{}'

        # filter type - url
        if filter_type == 1:
            if int(r['sUrlType']) == 0: URL_ALL = 1
            else:
                urls = get_urllist(r['sUrlType'])
                for u in urls:
                    if int(u['iType']) == 1:
                        # url in file
                        ul = get_url_frompath(u['sURL'])
                    elif int(u['iType']) == 2:
                        # custom define url
                        ul = [l.strip().rstrip() for l in u['sURL'].split(',')]

                    un = str(u['sURLGroupName'])
                    ud = dict(type=un, url=ul)
                    url_lst.append(ud)

        # filter type - app
        elif filter_type == 2:
            # if all app is set
            app_ids = r.get('sAppType', '').split(',')
            app_id_num = len(app_ids)
            if app_id_num == 0: continue
            elif app_id_num == 1 and int(app_ids[0]) == 0:
                APP_ALL = 1
            else:
                app_id_set = set()
                for app_id in app_ids:
                    app_id_set |= set(get_app_id(app_id))
                    # ids = get_app_id(app_id)
                    # app_lst.extend(ids)
                app_lst = list(app_id_set)
                pass

        # not recognized type
        else:
            continue


        conf_item = dict(AllIp=IP_ALL, AllUrl=URL_ALL, Ips=ip_lst, Urls=url_lst,
                         AllApp=APP_ALL, Apps=app_lst, Type=filter_type,
                         Action=action, EffectiveTime=eff_time, Id=id_, Name=name)

        # reset all flag
        IP_ALL = 0
        URL_ALL = 0
        APP_ALL = 0

        conf_lst.append(conf_item)


    with open(CONF_FILE_PATH, 'w') as fp:
        js = json.dumps(conf_lst, ensure_ascii=False,indent=2)
        # print js
        # s = str((js)).decode('utf8')
        fp.write("%s\n" % js)

    return confs

if __name__ == '__main__':
    make_url_filter_conf()
    pass
