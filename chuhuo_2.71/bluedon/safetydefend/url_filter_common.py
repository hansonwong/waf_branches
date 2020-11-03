# coding:utf-8
import re
from db.mysql_db import select
from utils.log_logger import rLog_dbg
from utils.common import get_file_content
DBG = lambda x: rLog_dbg('url_filter', x)


def get_urls_by_types(url_types):
    """
    @param url_types: 规则中所有的url类型id
    @return url_map: {id:surl}
    @return groupname: {id:groupname}
    """
    urls_map = {}
    groupname_map = {}
    DBG('GET URLS By Types')
    if not url_types:
        DBG('NO url types to query m_tburlgroup')
        return urls_map, groupname_map
    DBG('URL Types: %s' % url_types)
    sql = 'select id, sURLGroupName, sURL, iType from m_tburlgroup where id in (%s)' % ','.join(url_types)
    datas = select(sql)
    if not datas:
        DBG('query no data from m_tburlgroup')
    for data in datas:
        if data['iType'] == 1:
            urls_map[str(data['id'])] = get_file_content(data['sURL'])
        elif data['iType'] == 2:
            tmp = re.split('\n|\r|;|,', data['sURL'])
            DBG('spliting URLs: %s' % tmp)
            urls = [t for t in tmp if t.strip()]
            DBG('id %s urls %s' % (data['id'], urls))
            urls_map[str(data['id'])] = urls
        groupname_map[str(data['id'])] = data['sURLGroupName']
    return urls_map, groupname_map
