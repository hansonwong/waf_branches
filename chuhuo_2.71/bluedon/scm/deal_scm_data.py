#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from commands import getstatusoutput
from logging import getLogger

from scm.scm_strategy_load import load_to_mysql
from utils.file_handling import folders_walker


def deal_scm_data(file_path):
    untar_cmd = 'dd if={in_file}|openssl des3 -d -k {key}|tar zxf - --strip-components 1 -C {out_path}'
    out_path = '/usr/local/bluedon/tmp/%s' % os.path.split(file_path)[1].split('.')[0]
    getstatusoutput('mkdir %s' % out_path)
    status, output = getstatusoutput(untar_cmd.format(in_file=file_path,
                                                      key='bluedon',
                                                      out_path=out_path))
    if status:
        getLogger('main').error('error when extract file: %s', output)
        return

    data_table = {'m_tbSearitystrate_scm': '',
                  'm_tbaddress_list_scm': '',
                  'm_tbaddressgroup_scm': '',
                  'm_tbtimeplan_loop_scm': '',
                  'm_tbtimeplan_single_scm': ''}

    for file_name in folders_walker(out_path):
        for name in data_table:
            if name[:-4] in file_name:
                data_table[name] = file_name
                break

    print data_table
    load_to_mysql(data_table)
    getstatusoutput('rm -rf %s' % out_path)
    getLogger('main').info('Apply strategies from scm done!')
    getLogger('main').info('Remove strategies file from scm done!')


if __name__ == '__main__':
    deal_scm_data('/tmp/resetfull_data_1469163790.rule')
