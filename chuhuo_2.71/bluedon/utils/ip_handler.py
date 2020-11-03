# coding:utf-8
from netaddr import IPRange, IPNetwork
from utils.log_logger import rLog_dbg
from objectdefine.ip_range import deal_ip
from db.mysql_db import select, select_one


IP_MASK_TYPE = 1      # 地址类型：IP网络
IP_RANGE_TYPE = 2     # 地址类型: IP范围
SUPPORT_IP_TYPE = [IP_MASK_TYPE, IP_RANGE_TYPE]

SOURCE_TYPE_IP = '1'
SOURCE_TYPE_IPGROUP = '2'
SUPPORT_SOURCE_TYPE = [SOURCE_TYPE_IP, SOURCE_TYPE_IPGROUP]
IP_LOG = lambda x: rLog_dbg('ip_log', x)
ERROR_IP_TYPE = -1
PARTIAL_IP_TYPE = 0
ALL_IP_TYPE = 1


def get_ips_by_ids(ids):
    """
    @function: 根据表m_tbaddress中的id取出数据, 返回数组
    @param ids(str): m_tbaddress的id字符串拼接 eg: 1,2,3
    @return result(list): m_tbaddress_list数据
    """
    if not ids:
        IP_LOG('Params Error: No ID')
        return []
    sql = 'select * from m_tbaddress_list where id in (%s)' % ','.join(ids)
    result = select(sql)
    return result


def get_ids_by_ipgroup(group_id):
    """
    @function: 根据group_id从m_tbaddressgroup中获取ip_ids
    @param group_id(int/str): m_tbaddressgroup的id
    @return result(dict): m_tbaddressgroup数据
    """
    if not group_id:
        IP_LOG('Params Error: No Group_id')
    sql = 'select sIP from m_tbaddressgroup where id=%s' % group_id
    result = select_one(sql)
    if not result:
        IP_LOG('NO DATA from m_tbaddressgroup By %s' % group_id)
    return result


def handle_ips(ip_data):
    """
    @function: 处理ip, 返回网络中所有的ip
    @param ipdata(list): 从m_tbaddress中获取ip地址的数据数组
    @return address(list): 排好序的IP
            mark(int): -1为错误类型 0为非全部IP， 1为全部IP
    """
    ip_count = 0
    address = set()
    if not ip_data:
        IP_LOG('NO IPDATA to handle')
        return [], ERROR_IP_TYPE
    for res in ip_data:
        if int(res['sAddtype']) == IP_MASK_TYPE:     # ip形式
            ip_str, ip_type = deal_ip(res['sAddress'], res['sNetmask'])
            IP_LOG('FORMAT IP ADDRESS %s' % ip_str)
            if ip_type == 'single':
                ips = [ip_str]
            else:
                if ip_str in ['0.0.0.0/0', '0.0.0.0/0.0.0.0']:
                    IP_LOG('return ALL IP')
                    return [], ALL_IP_TYPE
                ips = IPNetwork(ip_str)
        elif int(res['sAddtype']) == IP_RANGE_TYPE:  # ip段形式
            ips = IPRange(res['sAddress'], res['sNetmask'])
        else:
            IP_LOG('WRONG Addtype %s in ID %s' % (res['sAddtype']))
            continue
        # control IP quatity, avoid overflow
        for ip in ips:
            ip_count += 1
            address.add(str(ip))
            if ip_count >= 1000:
                IP_LOG('OVERFLOW 1000 IP')
                return sorted(list(address)), PARTIAL_IP_TYPE
    IP_LOG('return %s address' % ip_count)
    return sorted(list(address)), PARTIAL_IP_TYPE


def ip_list_by_source(source_id, source_type):
    """ 区分ip和ip_group处理 """
    source_id = str(source_id)
    source_type = str(source_type)
    if source_type not in SUPPORT_SOURCE_TYPE:
        IP_LOG('PARAMS ERROR: ERROR SOURCE TYPE')
        return [], ERROR_IP_TYPE
    if source_type == SOURCE_TYPE_IP:
        ip_ids = [source_id]
    elif source_type == SOURCE_TYPE_IPGROUP:
        group_data = get_ids_by_ipgroup(source_id)
        ip_ids = group_data['sIP'].split(',') if group_data else []
    if not ip_ids:
        IP_LOG('NO DATA RETURN from DB')
        return [], ERROR_IP_TYPE
    ip_data = get_ips_by_ids(ip_ids)
    ips, is_all_ip = handle_ips(ip_data)
    return ips, is_all_ip


if __name__ == '__main__':
    print ip_list_by_source(2, '1')
    print ip_list_by_source(3, '1')
    print ip_list_by_source(1, '2')
    print ip_list_by_source(2, '2')
