#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Database operation module

1. Return record of Dict object which can access with `.` operator and `[]`,
such as `record.id==record['id'].
2. Auto open and connect database when execute sql.
3. Can deal with transaction, by `with` keyword.
4. Can insert dict data into database.
"""

import os
import threading
import functools
import time
from logging import getLogger

from MySQLdb import OperationalError

from core.setting import DB, BASE_DIR
from utils.logger_init import get_logger


get_logger('db', os.path.join(BASE_DIR, 'log/database.log'))

class Dict(dict):
    """Simple dict but support access as x.y style.

    >>> d1 = Dict()
    >>> d1['x'] = 100
    >>> d1.x
    100
    >>> d1.x = 200
    >>> d1['x']
    200
    >>> d2 = Dict(('a','b',), (1,2))
    >>> d2
    {'a': 1, 'b': 2}
    >>> d2['c']
    Traceback (most recent call last):
    KeyError: 'c'
    >>> d2.c
    Traceback (most recent call last):
    AttributeError: "Dict" object has no attribute "c"
    """

    def __init__(self, names=(), values=(), **kwargs):
        super(Dict, self).__init__(**kwargs)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r'"Dict" object has no attribute "%s"' % key)

    def __setattr__(self, key, value):
        self[key] = value


class DBError(Exception):
    pass


class _Engine(object):
    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect()


class _LasyConnection(object):
    def __init__(self):
        self.connection = None

    def cursor(self):
        if self.connection is None:
            conn = engine.connect()
            getLogger('db.mysql_db').info('open connection <%s>...' % hex(id(conn)))
            self.connection = conn
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            conn = self.connection
            self.connection = None
            getLogger('db.mysql_db').info('close connection <%s>...' % hex(id(conn)))
            conn.close()


class _DbCtx(threading.local):
    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return self.connection is not None

    def init(self):
        getLogger('db.mysql_db').info('open lazy connection...')
        self.connection = _LasyConnection()
        self.transactions = 0

    def cleanup(self):
        self.connection.cleanup()

    def cursor(self):
        """
        Return cursor
        """
        return self.connection.cursor()


_db_ctx = _DbCtx()


class _ConnectionCtx(object):
    """
    _ConnectionCtx object that can open and close connection context.
    It can be nested and only the most outer connection has effect.

    with connection():
        pass
        with connection():
            pass
    """
    def __enter__(self):
        global _db_ctx
        if not _db_ctx.is_init():
            _db_ctx.init()
        self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()


class  _TransactionCtx(object):
    """_TransactionCtx object that can handle transactions.

    note: the code block with _TransactionCtx can't use with_connection
    with _TransactionCtx():
        pass
    """
    def __enter__(self):
        global _db_ctx
        if not _db_ctx.is_init():
            _db_ctx.init()
        self.should_close_conn = True
        _db_ctx.transactions += 1
        getLogger('db.mysql_db').info(_db_ctx.transactions==1 and 'begin transactions...'
                     or 'join current transaction...')
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        _db_ctx.transactions -= 1
        try:
            if _db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        getLogger('db.mysql_db').info('commit transactions...')
        try:
            _db_ctx.connection.commit()
            getLogger('db.mysql_db').info('commit ok.')
        except:
            getLogger('db.mysql_db').warning('commit failed. try rollback...')
            _db_ctx.connection.rollback()
            getLogger('db.mysql_db').warning('rollback ok.')
            raise

    def rollback(self):
        global _db_ctx
        getLogger('db.mysql_db').warning('rollback transaction...')
        _db_ctx.connection.rollback()
        getLogger('db.mysql_db').info('rollback ok.')


def _profiling(start, sql=''):
    """analyze the SQL execute time"""

    t = time.time() - start
    if t > 0.1:
        getLogger('db.mysql_db').warning('[PROFILING] [DB] %s: %s' % (t, sql))
    else:
        getLogger('db.mysql_db').info('[PROFILING] [DB] %s: %s' % (t, sql))


def connection():
    return _ConnectionCtx()


def with_connection(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        with _ConnectionCtx():
            return func(*args, **kwargs)
    return _wrapper


def transaction():
    return _TransactionCtx()


def with_transaction(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        _start = time.time()
        with _TransactionCtx():
            _result = func(*args, **kwargs)
        _profiling(_start)
        return _result
    return _wrapper


def value2str(data):
    """convert values of dict to string"""

    if isinstance(data, dict):
        for i in data.iterkeys():
            data[i] = str(data[i])
    return data


def _select(sql, first, *args):
    """execute select SQL and return unique result or list results."""

    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    try:
        cursor = _db_ctx.connection.cursor()
        getLogger('db.mysql_db').info('SQL: %s, ARGS: %s' % (sql, args))
        cursor.execute(sql, args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        if first:
            values = cursor.fetchone()
            if not values:
                return None
            return Dict(names, values)
        return [Dict(names, x) for x in cursor.fetchall()]
    except OperationalError as e:
        getLogger('db.mysql_db').error('SQL: %s ===> %s ' % ((sql % args), e))
    finally:
        if cursor:
            cursor.close()


@with_connection
def select_one(sql, *args):
    """fetch one record from database, auto close connection
    args:
        sql: 'select * from user where id=?;'
        args: the value will replace `?`
    return:
        `Dict` object
    """
    return _select(sql, True, *args)


@with_connection
def select(sql, *args):
    """fetch records from database, auto close connection
    args:
        sql: 'select * from user where id=?;'
        args: the value will replace `?`
    return:
        `list` object which contain one or more Dict object
    """
    return _select(sql, False, *args)


def raw_select(sql, *args):
    """fetch records from database, without auto close connection"""
    return _select(sql, False, *args)


def _update(sql, *args):
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    try:
        cursor = _db_ctx.connection.cursor()
        getLogger('db.mysql_db').info('SQL: %s, ARGS: %s' % (sql, args))
        cursor.execute(sql, args)
        r = cursor.rowcount
        if _db_ctx.transactions == 0:
            getLogger('db.mysql_db').info('auto commit')
            _db_ctx.connection.commit()
        return r
    except OperationalError as e:
        getLogger('db.mysql_db').error('SQL: %s ===> %s ' % ((sql % args), e))
    finally:
        if cursor:
            cursor.close()


@with_connection
def insert(table, **kwargs):
    """insert record into table, auto unpack dict object
    usage:
        u1 = dict(id=2000, name='Bob', email='bob@test.org', passwd='bobobob')
        insert('user', **u1)
    args:
        table: table name
        kwargs: the dict object you want to insert into table
    return:
        change record count
    """
    cols, args = zip(*kwargs.iteritems())
    sql = 'insert into `%s` (%s) values (%s)'
    sql = sql % (table,
                 ','.join(['`%s`' % col for col in cols]),
                 ','.join(['?' for i in range(len(cols))]))
    return _update(sql, *args)


@with_connection
def update(sql, *args):
    """execute all sql which can change database
    usage:
        update('update user set passwd=? where id=?', '***', '123\' or id=\'456')
    """
    return _update(sql, *args)


engine = None


def create_engine(**kwargs):
    import MySQLdb
    global engine
    if engine is not None:
        raise DBError('Engine is already initialized.')
    defaults = dict(use_unicode=True, charset='utf8',)
    if 'cursorclass' in kwargs: del kwargs['cursorclass']
    for k, v in defaults.iteritems():
        if not k in kwargs:
            kwargs[k] = v
    engine = _Engine(lambda: MySQLdb.connect(**kwargs))
    getLogger('db.mysql_db').info('Init MySQL engine <%s> ok.' % hex(id(engine)))



create_engine(**DB)
