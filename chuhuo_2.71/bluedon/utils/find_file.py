#!/usr/bin/env python
# coding=utf-8

import os
import time
import datetime

TYPE_FTP = 'ftp/'
TYPE_MAIL = 'mail/'
TYPE_HTTP = 'http/'
TYPE_VIRUS = 'virus/'

# a list of string constant
TYPES = [TYPE_FTP, TYPE_MAIL, TYPE_HTTP, TYPE_VIRUS]


def get_all_files_in(path):
    """find all files in path, return their absolute paths in a list"""
    ret = []
    if not os.path.exists(path) or not os.path.isdir(path):
        return ret
    for root, directory, files in os.walk(path):
        for filename in files:
            ret.append(os.path.join(root, filename))
    return ret


def find_files_older_than(path, n_date, f_type=None):
    """
        find files in path whose last modify time are older than n_date
        path must be an absolute path, n_date is a date like YYYYMMDD
    """
    ret = []
    files = get_all_files_in(path)
    if len(files) == 0:
        return ret

    # change n_date to datetime
    try:
        latest_date = datetime.datetime.strptime(n_date, "%Y%m%d")
    except:
        # log here
        print 'find_files_older_than: GET WRONG DATE %s' % n_date
        return ret


    for f in files:
        timestamp = os.path.getmtime(f)
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        if dt < latest_date:
            # check file type by filename
            if f_type is None or f_type in f:
                print f, '  ', dt
                ret.append(f)

    return ret


def find_files_of_date(path, n_date, f_type=''):
    """
        find files in path whose last modify time are  n_date
        path must be an absolute path, n_date is a date like YYYYMMDD
    """
    ret = []
    files = get_all_files_in(path)
    if len(files) == 0:
        return ret

    # change n_date to datetime
    try:
        latest_date = datetime.datetime.strptime(n_date, "%Y%m%d")
    except:
        # log here
        print 'find_files_older_than: GET WRONG DATE %s' % n_date
        return ret


    for f in files:
        timestamp = os.path.getmtime(f)
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        # prefix length
        prefix_len = len(os.path.split(f)[0]) + 2
        if dt.date() == latest_date.date():
            try:
                # check file type by filename
                if f_type == '' or f_type in f[:prefix_len]:
                    ret.append(f)
                    print f, '  ', dt.date()
            except Exception as e:
                print e

    return ret



if __name__ == '__main__':
    PATH = '/var/suricata/audit'
    DATE = '20161202'
    TYPE = 'ftp/'
    # TYPE = 'mail/'
    # find_files_older_than(PATH, DATE, TYPE_HTTP)
    find_files_of_date(PATH, DATE, TYPE_FTP)
