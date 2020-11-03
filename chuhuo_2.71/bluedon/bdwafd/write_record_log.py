#! /usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime
from config_sql import execute_sql, fetchall_sql, fetchone_sql


def write_crontab():
    path = "/etc/crontab"
    fi = open(path, "r")
    lines = fi.readlines()
    fi.close()
    cmd = "1 0 * * * root python /usr/local/bluedon/bdwafd/write_record_log.py\n"
    with open(path, "a") as fp:
        if cmd not in lines:
            fp.write(cmd)


def create_record_table():
    sql = """CREATE TABLE IF NOT EXISTS `t_record_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `new_table_name` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `start_time` int(11) DEFAULT NULL,
  `end_time` int(11) DEFAULT NULL,
  `ori_table_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;"""

    execute_sql(sql)


def insert_record():
    # 每天产生两张表，也就是每天产生两条数据
    sitestatus_table = "t_sitestatus"
    web_connections_table = "t_web_connections"
    # 23小时59分的秒数
    delay_time = 86280
    now = int(time.time())
    end_time = now + delay_time
    table_time = time.localtime(now)
    table_time = time.strftime("%Y%m%d %H:%M:%S", table_time).split()[0]

    sql = "insert into t_record_history" + "(new_table_name,start_time,end_time,ori_table_name)" + " values('%s','%s','%s','%s')"
    sitestatus_sql = sql % (sitestatus_table + "_" + table_time,
                            now, end_time, sitestatus_table)
    web_connections_sql = sql % (web_connections_table + "_" + table_time,
                                 now, end_time, web_connections_table)
    execute_sql(sitestatus_sql)
    execute_sql(web_connections_sql)


if __name__ == "__main__":
    insert_record()
    # write_crontab()
    # create_record_table()
