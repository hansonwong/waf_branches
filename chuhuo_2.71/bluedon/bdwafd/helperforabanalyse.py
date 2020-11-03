# -*- coding: utf-8 -*-
import pickle



# def update_within_1h(pathtofile, minutes=61):
#     from time import time
#     from os import stat
#     now = time()
#     ctime = stat(pathtofile).st_ctime
#     since = (now-ctime)/60
#     if since > minutes:
#         return False
#     return True




# def save_data_for_abnormal_analyse():
#     from config_sql import execute_sql_logs, fetchone_sql
#     from abnormal_analyse import parse_log, get_website_data
#     creattablesql = """CREATE TABLE IF NOT EXISTS data_tmp (
#    `id` int(11) NOT NULL AUTO_INCREMENT,
#     `key` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
#     `number` bigint(20) DEFAULT NULL COMMENT 'dayipvisit',
#     `traffic` bigint(20) DEFAULT NULL COMMENT 'dayiptraffic'
#     PRIMARY KEY (`id`));
#     """
#     execute_sql_logs(creattablesql)
#     getsize_sql = 'select * from t_website_nginx'
#     result = fetchone_sql(getsize_sql)
#     old_size = result[2]
#     data = parse_log(old_size)
#     for key, value in data.items:
#         number = value["number"]
#         traffic = value["traffic"]
#
#         savesql = """INSERT INTO `data_tmp` (`key`,`number`,`traffic`) VALUES
#                     ('%s', %d, %d);""" % (key, number, traffic)
#         execute_sql_logs(savesql)

def save_data_for_abnormal_analyse(path_pickle_file="data.pickle"):
    from abnormal_analyse import parse_log, get_website_data
    from config_sql import  fetchone_sql

    getsize_sql = 'select * from t_website_nginx'
    result = fetchone_sql(getsize_sql)
    old_size = result[2]
    data = parse_log(old_size)
    with open(path_pickle_file, 'wb') as fp:
        pickle.dump(data, fp)

def dict_combine(d1, d2):
    if d1 == {}:
        return d2
    if d2 == {}:
        return d1
    for key in d1.keys():
        if key in d2.keys():
            d2[key]["number"] = d2[key]["number"] + d1[key]["number"]
            d2[key]["traffic"] = d2[key]["traffic"] + d1[key]["traffic"]
        else:
            d2[key] = {}
            d2[key]["number"] = d1[key]["number"]
            d2[key]["traffic"] = d1[key]["traffic"]
    return d2


