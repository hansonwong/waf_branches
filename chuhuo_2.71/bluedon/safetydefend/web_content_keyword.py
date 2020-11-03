# coding:utf-8
#!/usr/bin/env python

from db.mysql_db import select
import sys
import re
from logging import getLogger
from utils.log_logger import rLog_dbg
reload(sys)
sys.setdefaultencoding('utf-8')


CONFIG_PATH = '/etc/suricata/conf/htp-content-kw.txt'
FILTER_LOG = lambda x: rLog_dbg('filter', x)


def web_keyword():
    """
    按格式:'内容类型';'算法';'关键字';'日志';将参数写入文件/etc/suricata/conf/htp-content-kw.txt
    多个关键字需被拆分,一个关键字一行数据
    """
    web_info_list = select('select * from m_tbkeyword_webcontent where iStatus=1')
    f = open(CONFIG_PATH, 'w')
    string_join = lambda _type, suanfa, keyword, log: ';'.join([_type, suanfa, keyword, log])
    for info in web_info_list:
        try:
            if str(info['sKeyword']) != '':
                # english_keyword = re.findall(r'\w+', info['sKeyword'])
                FILTER_LOG('ORIGIN WEB_KEYWORD is %s' % info['sKeyword'])
                info['sKeyword'] = info['sKeyword'].replace('\n', ';')
                english_keyword = re.split(' |;', info['sKeyword'])
                china_keyword = re.findall(u'[\u4e00-\u9fa5]+', info['sKeyword'])
                english_keyword.extend(china_keyword)
                FILTER_LOG('WEB_KEYWORD is %s' % info['sKeyword'])
                for tmp in english_keyword:
                    tmp = tmp.strip()
                    if not tmp:
                        continue
                    FILTER_LOG('CURRENT WEB KEYWORD %s' % tmp)
                    string = string_join(info['sType'], str(info['sSuanfa']), tmp, str(info['iLog']))
                    FILTER_LOG('WEB_CONFIG is %s' % string)
                    print>>f, string + ';'
        except Exception as e:
            print e
            getLogger('main').info(e)
    f.close()

if __name__ == '__main__':
    web_keyword()
