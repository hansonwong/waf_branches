#!/usr/bin/env python
# coding=utf-8


"""
    FILE MONITOR
    check if a file is changed and call the handler function
"""
import os
import time
import threading
from pyinotify import WatchManager, Notifier, \
    ProcessEvent,IN_DELETE, IN_CREATE,IN_MODIFY, IN_ACCESS, IN_CLOSE_WRITE, \
    ALL_EVENTS, IN_ATTRIB, IN_DELETE_SELF

from adutils.audit_logger import rLog_dbg, rLog_err


FWLOG_DBG = lambda x : rLog_dbg('FsMonitor', x)
FWLOG_ERR = lambda x : rLog_err('FsMonitor', x)

TABLE_PATH = '/usr/local/mysql/data/db_firewall'
LOG_TABLE_PATH = '/var/mysql/data/db_firewall_log'


def add_file_monitor(path=None, cbfunc=None, isTable=False):
    """
        path MUST BE a abspath
    """
    if path is None or cbfunc is None:
        return

    if not os.path.exists(path):
        FWLOG_DBG('[add_file_monitor]%s is not exists' % path)
        print('[add_file_monitor]%s is not exists' % path)
        return

    if not callable(cbfunc):
        FWLOG_DBG('[add_file_monitor]%s is not a function' % cbfunc)
        print('[add_file_monitor]%s is not a function' % cbfunc)


    _Observer.add_observer(path, cbfunc, isTable)


def add_table_monitor(tbname=None, cbfunc=None, db_port=3306):
    if tbname is None or cbfunc is None:
        return -1

    if db_port == 3306:
        _path = TABLE_PATH
    elif db_port == 3307:
        _path = LOG_TABLE_PATH
    else:
        FWLOG_DBG('[add_table_monitor]get wrong db_port')
        return -1
    tb_path_ibd = os.path.join(_path, tbname + '.ibd')
    tb_path_myd = os.path.join(_path, tbname + '.MYD')

    if os.path.exists(tb_path_ibd):
        add_file_monitor(tb_path_ibd, cbfunc, isTable=True)
        print tb_path_ibd
        return 0

    if os.path.exists(tb_path_myd):
        add_file_monitor(tb_path_myd, cbfunc, isTable=True)
        print tb_path_myd
        return 0

    return -1


class EventHandler(ProcessEvent):

    # add _Observer here

    def process_IN_CREATE(self, event):
        # print "Create file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("Create file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, event)

    def process_IN_DELETE(self, event):
        # print "Delete file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("Delete file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, event)

    def process_IN_MODIFY(self, event):
        # print "Modify file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("Modify file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, event)

    def process_IN_ACCESS(self, event):
        # print "IN_ACCESS file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("IN_ACCESS file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, event)

    def process_IN_CLOSE_WRITE(self, event):
        # print "IN_ACCESS file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("IN_close file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, event)

    def process_IN_DELETE_SELF(self, event):
        # print "IN_ACCESS file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("IN_close file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, event)


def test_handler(event):
    print 'get changed %s' % event

def test_handler1(event):
    print 'get changed111 %s' % event


class _Observer(object):
    FWLOG_DBG('in MysqlObserver')
    ob = {}
    ob_file = dict()
    ob_type = {}
    ob_count = 0

    # pyinotify
    _wm = WatchManager()
    # _mask = IN_MODIFY | IN_CREATE | IN_DELETE | IN_CLOSE_WRITE | IN_ATTRIB
    # _mask = ALL_EVENTS
    _mask = IN_CLOSE_WRITE
    _notifier = Notifier(_wm, EventHandler())
    _status = 0
    _stop = True


    @classmethod
    def add_ob_count(cls):
        cls.ob_count += 1
        if cls.ob_count > 255:
            raise RuntimeError('Too Much observers...')

    @classmethod
    def add_observer(cls, key, observer, isTable=False):
        if not cls.ob.has_key(key):
            cls.ob[key] = [observer]

            if isTable:
                print 'isTable'
                cls._wm.add_watch(key, IN_MODIFY)
            else:
                print 'NotTable'
                cls._wm.add_watch(os.path.split(key)[0], cls._mask)


            # add key type
            if os.path.isdir(key):
                cls.ob_type[key] = 'file'
        else:
            cls.ob[key].append(observer)

        cls.add_ob_count()
        cls.notify_observer(key, 'adding ob[%s] key=%s' % (cls.ob_count, key))


    @classmethod
    def notify_observer(cls, key, *args, **kwargs):
        if key in cls.ob:
            for fun in cls.ob[key]:
                fun(*args, **kwargs)
                FWLOG_DBG('notify_observer:%s handler=%s' % (key, fun))
        else:
            path = os.path.split(key)[0]
            if path in cls.ob_type.keys():
                for fun in cls.ob[path]:
                    fun(key)
                    FWLOG_DBG('notify_observer:%s handler=%s' % (key, fun))
            else:
                pass
                # raise RuntimeError('Observer didn\'t have this observer[%s]' % key)

    @classmethod
    def start(cls):
        cls._status = 1
        cls._stop = False

        while 1:
            try:
                if cls._stop:
                    FWLOG_DBG('[_Observer]Stopping...')
                    break
                cls._notifier.process_events()
                if cls._notifier.check_events(timeout=1000):
                    print "check event true."
                    cls._notifier.read_events()
                    print 'event done'
            except KeyboardInterrupt:
                print "keyboard Interrupt."
                break
            except Exception as e:
                FWLOG_ERR(e)
                print e

        cls._notifier.stop()
        cls._status = 0
        FWLOG_DBG('[_Observer]Exited')

    @classmethod
    def get_status(cls):
        return cls._status

    @classmethod
    def stop(cls):
        cls._stop = True
        pass

    @classmethod
    def is_running(cls):
        return not cls._stop


class FsMonitor(threading.Thread):
    def __init__(self):
        super(FsMonitor, self).__init__()
        self.setName('fw_fsmonitor')


    def run(self):
        if not _Observer.is_running():
            _Observer.start()
        else:
            FWLOG_DBG('[FsMonitor]Exited...An instance is running')
        FWLOG_DBG('[FsMonitor]Exited')


    def start(self):
        super(FsMonitor, self).start()


    def stop(self):
        if _Observer.is_running():
            _Observer.stop()
            FWLOG_DBG('[FsMonitor]Stopping...')
        else:
            FWLOG_DBG('[FsMonitor]Exited...No instance is running')



if __name__ == '__main__':
    # add_file_monitor('/usr/local/bluedon/conf/online_users', test_handler)
    add_file_monitor('/data/conf/bd_local_rulefiles/last_version', test_handler1)
    # add_file_monitor('/data/conf/bd_local_rulefiles', test_handler1)
    # add_file_monitor('/tmp/tt', test_handler1)
    add_table_monitor('m_tbconfig', test_handler1)
    # print add_table_monitor('m_tbrole_copy', test_handler1)
    # print add_table_monitor('m_tbusers', test_handler1)
    # print add_table_monitor('m_tbnetport', test_handler1)
    # _Observer.start()
    fm = FsMonitor()
    fm.start()
    try:
        time.sleep(300)
    except KeyboardInterrupt:
        pass
    fm.stop()

    # FsMonitor('/tmp')
    # FsMonitor('/usr/local/bluedon/tmp')
    # FsMonitor('/usr/local/bluedon/tmp')

    pass
