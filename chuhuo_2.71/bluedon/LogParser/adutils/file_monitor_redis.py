#!/usr/bin/env python
# coding=utf-8


"""
    FILE MONITOR by Redis
    check if a file is changed and call the handler function, once the monitor found
    file(register by client) is change, send message to notify client by Redis

    Usage:
        Monitor--->
        monitor = FsMonitor()
        monitor.start()

        Client--->
        client = FsMonitorClient()
        # Must start client before adding any files
        client.start()
        client.add_file_monitor(file_abs_path1, handler1)
        client.add_file_monitor(file_abs_path2, handler2)
        ...
        client.add_file_monitor(file_abs_pathN, handlerN)
        # same file can have multi handlers
"""
import os
import time
import threading
from pyinotify import WatchManager, Notifier, \
    ProcessEvent,IN_DELETE, IN_CREATE,IN_MODIFY, IN_ACCESS, IN_CLOSE_WRITE, \
    ALL_EVENTS

from adutils.audit_logger import rLog_dbg, rLog_err
from adutils.redis_utils.redis_op import create_redis, publish_channel, get_msg_from_channel


FSMONITOR_REG_CH = 'bdfw_reg_fsmonitor_channel' # must different from FSMONITOR_CH
FSMONITOR_CH = lambda x : 'bdfw_fsmonitor_'  + x

FWLOG_DBG = lambda x : rLog_dbg('AuditFsMonitor', x)
FWLOG_ERR = lambda x : rLog_err('AuditFsMonitor', x)

TABLE_PATH = '/usr/local/mysql/data/db_firewall'
LOG_TABLE_PATH = '/var/mysql/data/db_firewall_log'

# Define actions using in channels
FILE_ADDED = 'added'


class EventHandler(ProcessEvent):

    # add _Observer here
    ACTIONS = ['create', 'delete', 'modify', 'access']

    def process_IN_CREATE(self, event):
        # print "Create file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("Create file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, 'create')

    def process_IN_DELETE(self, event):
        # print "Delete file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("Delete file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, 'delete')

    def process_IN_MODIFY(self, event):
        # print "Modify file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("Modify file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, 'modify')

    def process_IN_ACCESS(self, event):
        # print "IN_ACCESS file:%s." %os.path.join(event.path,event.name)
        FWLOG_DBG("IN_ACCESS file:%s." %os.path.join(event.path,event.name))
        _Observer.notify_observer(event.pathname, 'access')


def test_handler(event):
    print 'get changed %s' % event
    print 'get changed'

def test_handler1(event):
    print 'get changed222 %s' % event
    print 'get changed222'


class _Observer(object):
    FWLOG_DBG('in MysqlObserver')
    ob = {}
    ob_files = []
    ob_count = 0

    # pyinotify
    _wm = WatchManager()
    _mask = IN_MODIFY | IN_CREATE | IN_DELETE
    _notifier = Notifier(_wm, EventHandler())
    _status = 0
    _stop = False


    @classmethod
    def add_ob_count(cls):
        cls.ob_count += 1
        if cls.ob_count > 255:
            raise RuntimeError('Too Much observers...')

    @classmethod
    def add_observer(cls):
        redis_obj = create_redis()
        start_time = time.time()
        try:
            for data in get_msg_from_channel(redis_obj, FSMONITOR_REG_CH, mode='sub'):
                if time.time() - start_time > 30:
                    print 'add_observer exit time out'
                    break
                if cls._stop:
                    print 'add_observer exit cls._stop'
                    break

                if data is not None and os.path.exists(data):
                    if data not in cls.ob_files:
                        print 'add file %s' % data
                        cls._wm.add_watch(data, cls._mask)
                        cls.ob_files.append(data)

                    # notify client file is added
                    publish_channel(redis_obj, FSMONITOR_CH(data), FILE_ADDED)

                    cls.add_ob_count()
            if redis_obj is not None:redis_obj.connection_pool.disconnect()
        except:
            pass
        finally:
            pass


    @classmethod
    def notify_observer(cls, data, action):
        # notify client file is added
        redis_obj = create_redis()
        publish_channel(redis_obj, FSMONITOR_CH(data), action)
        if redis_obj is not None:redis_obj.connection_pool.disconnect()


    @classmethod
    def start(cls):
        cls._status = 1
        cls._stop = False

        add_thread = threading.Thread(target=cls.add_observer)
        add_thread.setName('add_observer')
        add_thread.setDaemon(True)
        add_thread.start()

        while 1:
            try:
                if cls._stop:
                    FWLOG_DBG('[_Observer]Stopping...')
                    break
                cls._notifier.process_events()
                if cls._notifier.check_events(timeout=1000):
                    print "check event true."
                    cls._notifier.read_events()
            except KeyboardInterrupt:
                print "keyboard Interrupt."
                break
            except Exception as e:
                print e

        cls.stop()
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

class FsMonitorRedisBase(threading.Thread):
    def __init__(self):
        super(FsMonitorRedisBase, self).__init__()

    def get_msg(self):
        pass


class FsMonitor(threading.Thread):
    def __init__(self):
        super(FsMonitor, self).__init__()
        self.setName('fs_monitor')


    def run(self):
        _Observer.start()
        FWLOG_DBG('[FsMonitor]Exited')


    def start(self):
        super(FsMonitor, self).start()


    def stop(self):
        _Observer.stop()


class FsMonitorClient(threading.Thread):
    def __init__(self):
        super(FsMonitorClient, self).__init__()
        self.observers = {}
        self.event = threading.Event()
        self.redis_obj = create_redis()
        self.client_running = False
        self.add_done = False
        self.setName('fs_client')


    def add_file_monitor(self, path=None, cbfunc=None):
        """
            path MUST BE a abspath
        """
        if not self.client_running:
            FWLOG_DBG('[add_file_monitor]client is not running')
            return -1

        if path is None or cbfunc is None:
            return

        if not os.path.exists(path):
            FWLOG_DBG('[add_file_monitor]%s is not exists' % path)
            return -2

        if not callable(cbfunc):
            FWLOG_DBG('[add_file_monitor]%s is not a function' % cbfunc)
            return -3

        # add file-function relationship
        if not self.observers.has_key(FSMONITOR_CH(path)):
            self.observers[FSMONITOR_CH(path)] = [cbfunc]
        else:
            self.observers[FSMONITOR_CH(path)].append(cbfunc)
        add_timeout = 0
        publish_channel(self.redis_obj, FSMONITOR_REG_CH, path)
        while self.add_done is False:
            if add_timeout > 10:
                FWLOG_DBG('add file failed %s' % path)
                return -4
            time.sleep(0.5)
            add_timeout += 1
            # retry
            publish_channel(self.redis_obj, FSMONITOR_REG_CH, path)

        self.add_done = False
        return 0


    def add_table_monitor(self, tbname=None, cbfunc=None, db_port=3306):
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
            print tb_path_ibd
            return self.add_file_monitor(tb_path_ibd, cbfunc)

        if os.path.exists(tb_path_myd):
            print tb_path_myd
            return self.add_file_monitor(tb_path_myd, cbfunc)



    def run(self):
        try:
            while 1:
                if self.event.isSet():
                    break

                print 'running'
                # listen all fsmonitor channel from redis
                # for ch, msg in get_msg_from_channel(self.redis_obj, FSMONITOR_CH('*')):
                for item in get_msg_from_channel(self.redis_obj, FSMONITOR_CH('*')):
                    if self.event.isSet():
                        break

                    if item is None:
                        continue

                    ch = item[0]
                    msg = item [1]

                    if msg in EventHandler.ACTIONS:

                        if ch in self.observers:
                            for func in self.observers[ch]:
                                func(ch + ' ' + msg)

                    elif msg == FILE_ADDED:
                        self.add_done = True
                        pass

        except Exception as e:
            print e
            FWLOG_ERR(e)
            # if error happends reconncet to redis
            self.redis_obj = create_redis()
            time.sleep(1)
        FWLOG_DBG('FSMONITOR Exit')


    def start(self):
        self.client_running = True
        super(FsMonitorClient, self).start()


    def stop(self):
        self.client_running = False
        self.event.set()



if __name__ == '__main__':
    # add_file_monitor('/usr/local/bluedon/tmp/notify_test', test_handler)
    # add_file_monitor('/usr/local/bluedon/tmp/notify_*', test_handler1)
    # print add_table_monitor('m_tbrole_copy', test_handler)
    # print add_table_monitor('m_tbrole_copy', test_handler1)
    # print add_table_monitor('m_tbusers', test_handler1)
    # print add_table_monitor('m_tbnetport', test_handler1)
    # _Observer.start()
    fm = FsMonitor()
    fmc = FsMonitorClient()
    fm.start()
    fmc.start()
    print fmc.add_file_monitor('/usr/local/bluedon/tmp/xxxxx.txt', test_handler)
    print fmc.add_file_monitor('/usr/local/bluedon/tmp/txt', test_handler)
    print fmc.add_table_monitor('m_tbnetport', test_handler)
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        print 'stop'
    fm.stop()
    fmc.stop()

    # FsMonitor('/tmp')
    # FsMonitor('/usr/local/bluedon/tmp')
    # FsMonitor('/usr/local/bluedon/tmp')

    pass
