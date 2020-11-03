#!/usr/bin/env python
# coding=utf-8

import os
from db.config import search_data
from db.config import execute_sql as exec_3306
# from scm.safe_tactics_scm import SafeTactics
from scm.safe_tactics_scm import safetactics_main
from scm.set_ipgroup import set_ipset

load_sql = ("/usr/bin/mysql --port=3306 --socket=/tmp/mysql3306.sock "
            "-uroot --password='bd_123456' --port=3306 -e 'source %s'")
CHAIN = 'SCM'

sql_file_path = '/usr/local/bluedon/tmp/m_tbaddress_list.sql'

load_data_infile = """load data infile '%s' ignore into table `%s`
                     character set utf8 fields TERMINATED BY ','
                     ENCLOSED BY '"' LINES TERMINATED BY '\r\n'"""

# tables = {'m_tbSearitystrate_scm': '/usr/local/bluedon/tmp/SCM/gk_data_1469163790_m_tbSearitystrate.txt',
#           'm_tbaddress_list_scm': '/usr/local/bluedon/tmp/SCM/gk_data_1469163790_m_tbaddress_list.txt',
#           'm_tbaddressgroup_scm': '/usr/local/bluedon/tmp/SCM/gk_data_1469163790_m_tbaddressgroup.txt',
#           'm_tbtimeplan_loop_scm': '/usr/local/bluedon/tmp/SCM/gk_data_1469163790_m_tbtimeplan_loop.txt',
#           'm_tbtimeplan_single_scm': '/usr/local/bluedon/tmp/SCM/gk_data_1469163790_m_tbtimeplan_single.txt'}


def change_ipset(action):
    sql = 'select * from m_tbaddressgroup_scm;'
    datas = search_data(sql)
    for data in datas:
        set_ipset(data, action)


def load_to_mysql(_tables=None):
    os.system('iptables -F %s' % CHAIN)
    change_ipset('del')
    if not _tables:
        print 'table none'
        return
    for name in _tables:
        with open(_tables[name], 'r') as fp:
            lines = fp.readlines()
        new_lines = []
        for line in lines:
            new_lines += line.replace('"N','\\N')

        with open(_tables[name], 'w') as fp:
            # print(''.join(new_lines))
            fp.write(''.join(new_lines))


        exec_3306('delete from %s' % name)
        exec_3306(load_data_infile % (_tables[name], name))
    pass

    # print file
    # os.system('cat %s' % _tables['m_tbSearitystrate_scm'])
    change_ipset('add')
    # execute strategy
#     for iptype in ['ipv4', 'ipv6']:
#         safetactics_main(iptype)
    safetactics_main()




if __name__ == '__main__':
    load_to_mysql()
    pass
