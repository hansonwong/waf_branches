#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
A module can persist data.
This module base on sqlite3 and json, database file storing in tmpfs of system.
When system reboot, all persisted data would be gone, be careful.

Usage:
>>> from utils.cache import *
>>> cache.set('aa', {'aadsd': 1111})
>>> cache.get('aa')
{u'aadsd': 1111}
>>> cache.get('bb', 'No found')
'No found'
>>> cache.set('bb', {'aadsd': 1111}, clean_when_exit=True)

# after restart process
>>> from utils.cache import *
>>> cache.get('aa')
{'aadsd': 1111}
>>> cache.get('bb')  # no found

# after restart system
>>> from utils.cache import *
>>> cache.get('aa')  # no found
>>> cache.get('bb')  # no found
"""

import atexit
import json
import sqlite3


__author = 'ruan.lj@foxmail.com'
__all__ = ['cache']

# for ubuntu it is /run/shm, for centos it is /dev/shm
CACHE_PATH = '/dev/shm/python_cache.sqlite3'


def _sqlite_connect():
    conn = sqlite3.connect(CACHE_PATH)
    cur = conn.cursor()
    if not cur.execute('SELECT * FROM sqlite_master WHERE `name`="cache";').fetchall():
        table_sql = 'CREATE TABLE "cache" ("name"  TEXT(128) PRIMARY KEY NOT NULL UNIQUE, '\
                    '"value"  TEXT, "clean_when_exit"  INTEGER NOT NULL DEFAULT 0);'
        cur.execute(table_sql)
        conn.commit()
    return conn, cur


class _Cache(object):
    @staticmethod
    def _update(sql, *args):
        conn, cur = _sqlite_connect()
        cur.execute(sql, args)
        conn.commit()
        conn.close()

    @staticmethod
    def _select(sql, *args):
        conn, cur = _sqlite_connect()
        cur.execute(sql, args)
        records = cur.fetchall()
        conn.close()
        return records

    def set(self, name, py_obj, clean_when_exit=False):
        """set cache
        args:
            name: name of cache. str or unicode.
            py_obj: jsonable python object, such as dict, list, int, str.
            clean_when_exit: True or False, default False
        """
        if isinstance(name, basestring):
            name = name.strip()
        else:
            raise ValueError('The name of cache must be string!')
        js_str = json.dumps(py_obj)
        clean_when_exit = 1 if clean_when_exit else 0
        if self._select('SELECT * FROM `cache` WHERE `name`=?', name):
            self._update('UPDATE `cache` SET `value`=?, `clean_when_exit`=? WHERE `name`=?',
                         js_str, clean_when_exit, name)
        else:
            self._update('INSERT INTO `cache` (`name`, `value`, `clean_when_exit`) VALUES (?, ?, ?)',
                         name, js_str, clean_when_exit)

    def get(self, name, default=None):
        """get cache
        args:
            name: name of cache. str or unicode.
            default: return default if name is not found in database.
        """
        if isinstance(name, basestring):
            name = name.strip()
        else:
            raise ValueError('The name of cache must be string!')
        records = self._select('SELECT * FROM `cache` WHERE `name`=?', name)
        if len(records):
            return json.loads(records[0][1])
        return default

    def show_names(self):
        """show all cache names"""
        records = self._select('SELECT `name` FROM `cache`')
        return [i[0] for i in records]


@atexit.register
def clear_expired_cache():
    cache._update('DELETE FROM `cache` WHERE `clean_when_exit`=1;')


cache = _Cache()
