#!/usr/bin/env python
# coding=utf-8

"""
    第二代防火墙 --> 自定义对象--> url类型组

    modify log
    2016-4-6:
        1、增加恢复系统默认设置选项
    2016-5-24::
        1、重构代码(pylint 2.64/befor 9.52/after)
        2、修复编码问题
    2016-7-11:
        1、系统命令路径统一从 core.setting 中导入
        2、过滤空url列表项，不写入配置文件
"""

import os
import sys
import codecs
from logging import getLogger

from db.config import search_data, execute_sql, mkdir_file
from utils.logger_init import logger_init
from core.setting import LOG_BASE_PATH


FILE_PATH = '/usr/local/bdwaf/conf/url_filter_category.conf'
URL_PATH = '/usr/local/bdwaf/conf/URLs'
LOG_NAME = 'URL_GROUP'
LOG_PATH = os.path.join(LOG_BASE_PATH, 'url_group.log')

logger_init(LOG_NAME, LOG_PATH, 'DEBUG')

reload(sys)
sys.setdefaultencoding('utf-8')


class UrlGroupConfigFile(object):
    """
    把url类型组写入到配置文件中
    """

    def __init__(self, data):
        """
        初始化
        """

        self.data = data
        mkdir_file(FILE_PATH, 'file')

    def add(self):
        """
        把url类型组写到配置文件
        args:
            None
        return:
            True: 增加成功
            False: 增加失败
        """

        config_list = []
        # id
        id_str = 'ID:%d' %(int(self.data['id']))
        config_list.append(id_str)

        # URL组名称
        urlg_name_str = 'URLG Name:%s' %(self.data['sURLGroupName'])
        config_list.append(urlg_name_str)

        # URL组描述
        urlg_desc_str = 'URLG Description:%s' %(self.data['sGroupDesc'])
        config_list.append(urlg_desc_str)

        # url(多个用分号分隔)
        url_num = 0
        urls = []
        if self.data['sURL']:
            if self.data['sURL'].endswith('.txt'):
                filepath = codecs.open(self.data['sURL'], 'r', 'utf-8')
                lines = filepath.readlines()
                filepath.close()
                if lines:
                    urls = [x.replace('\n', '').replace('\r', '').strip() for x in lines]
            else:
                urls = self.data['sURL'].split(',')
                urls = [item.strip() for item in urls]
        if urls:
            urls = [item for item in urls if item]  # 去除空项
            url_num = len(urls)
            for i in xrange(0, url_num, 30):
                url_list = urls[i:i+30]
                url_str = ';'.join(url_list)
                url_str = 'URL:%s' %(url_str)
                config_list.append(url_str)
        else:
            config_list.append('URL:')

        # 关键字
        #keyword_str = 'Keyword:%s' %(self.data['sDomainKey'])
        #config_list.append(keyword_str)
        config_list.append('\n')

        try:
            config_str = '\n'.join(config_list)
        except Exception as err:
            getLogger(LOG_NAME).debug(err)

        # 把规则写入配置文件
        try:
            filepath = codecs.open(FILE_PATH, 'a', 'utf-8')
            filepath.write(config_str)
            return True
        except IOError as err:
            getLogger(LOG_NAME).debug(err)
            return False
        finally:
            filepath.close()

    def delete(self):
        """
        删除url类型组
        args:
            None
        return:
            True: 删除成功
            False: 删除失败
        """

        try:
            filepath = codecs.open(FILE_PATH, 'r', 'utf-8')
            lines_list = filepath.readlines()
        except IOError as err:
            getLogger(LOG_NAME).debug(err)
        finally:
            filepath.close()

        # 求匹配的开始和结束索引号
        re_str = 'ID:%d\n' %(int(self.data['id']))

        if not re_str in lines_list:
            return

        snum = lines_list.index(re_str)

        count = snum + 1
        len_lines = len(lines_list) -1
        while count <= len_lines:
            if lines_list[count] == '\n':
                enum = count
                break
            count += 1

        # 删除匹配的规则并从新写入配置文件
        for i in xrange(enum, snum-1, -1):
            lines_list.pop(i)
        lines_str = ''.join(lines_list)
        try:
            filepath = codecs.open(FILE_PATH, 'w', 'utf-8')
            filepath.write(lines_str)
            return True
        except IOError as err:
            getLogger(LOG_NAME).debug(err)
        finally:
            filepath.close()
            return False

def set_urls():
    """ 将内置的url过滤规则入库 """
    files = os.listdir(URL_PATH)
    files = [x for x in files if x.endswith('.txt')]

    # 先删除库中内置类型数据
    filenames = [x.split('.')[0].decode('utf-8') for x in files]
    for filename in filenames:
        sql = 'DELETE from m_tburlgroup where sURLGroupName="%s" and iType=1;' \
                %(filename)
        execute_sql(sql)

    contents = [[x.split('.')[0].decode('utf-8'), URL_PATH+'/'+x.decode('utf-8'), 1] for x in files]
    urlg = codecs.open('/usr/local/bdwaf/conf/URLs/m_tburlgroup.csv', 'r', 'utf-8')
    lines = urlg.readlines()
    urlg.close()

    num = len(contents)
    for line in lines:
        line = line.split(',')
        for i in range(num):
            if line[1] == contents[i][0]:
                contents[i].insert(1, line[2])
                break

    for content in contents:
        try:
            sql = 'INSERT INTO m_tburlgroup (sURLGroupName, sGroupDesc, sURL, \
                    iType) VALUES("%s", "%s", "%s", %d)' \
                    %(content[0], content[1], content[2], content[3])
        except Exception as err:
            getLogger(LOG_NAME).debug(err)
        execute_sql(sql)

def main(args):
    """ 主函数 """

    os.system('/usr/bin/cat /dev/null > %s' % (FILE_PATH))

    if args == 'init':
        pass
    elif args == 'reboot':
        #set_urls()

        g_sql = 'select * from m_tburlgroup;'
        datas = search_data(g_sql)
        for data in datas:
            conf = UrlGroupConfigFile(data)
            conf.add()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        getLogger(LOG_NAME).debug('more args (eg: python url_filter init/reboot)')
    else:
        main(sys.argv[1])
    #print "url group well done"
