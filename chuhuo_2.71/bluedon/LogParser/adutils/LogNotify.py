# -*-coding:utf-8 -*-
import os
import datetime
import pyinotify
import logging
import threading
import thread
import time


class NotifierEventHandler(pyinotify.ProcessEvent):
    """扫描通知处理"""
    def __init__(self, log_notify):
        self.log_notify = log_notify

    def process_IN_CLOSE_NOWRITE(self, event):
        self.log_notify.event_handler([event.pathname]);

    def process_IN_CLOSE_WRITE(self, event):
        self.process_IN_CLOSE_NOWRITE(event)

    def process_IN_MODIFY(self, event):
        self.process_IN_CLOSE_NOWRITE(event)


class LogNotify(pyinotify.ProcessEvent):
    """扫描监控目录"""

    # 通过linux find 命令进行扫描
    WAIT_LIST = 0
    # 通过pyinotify 模块监控
    WAIT_NOTIFY = 1
    # 扫面目录间隔，或者notify读取事件间隔
    SLEEP_INTERVAL_SECOND = 2.5
    # 每个目录扫描固定个数的文件
    SCAN_FILE_PER_DIR_COUNT = 10
    def __init__(self, paths, event_handler, watch_way=WAIT_LIST,
                 exclude_filter=None):

        self.event_handler = event_handler
        self.paths = paths
        self.watch_way = watch_way
        self.thread_ = None
        self.notifier = None
        self.running_ = False

        if self.watch_way == self.WAIT_NOTIFY:
            wm = pyinotify.WatchManager()
            for path in paths:
                try:
                    if not os.path.exists(path):
                        os.makedirs(path)
                except OSError, e:
                    logging.warning("% not exist, try to create fold fail", path)
                    continue
                # wm.add_watch(path, pyinotify.IN_CLOSE_WRITE|pyinotify.IN_MODIFY, rec=True)
                wm.add_watch(path, pyinotify.IN_CLOSE_WRITE|pyinotify.IN_MODIFY)
            handler = NotifierEventHandler(self)
            # notifier
            self.notifier = pyinotify.Notifier(wm, handler, timeout=self.SLEEP_INTERVAL_SECOND)

    def check_folder(self, folder):
        """递归扫描目录，返回目录下修改时间超过3秒的文件路径名"""
        if not os.path.exists(folder):
            logging.info('%s not exist, try to create', folder)
            os.makedirs(folder)
        # lines = os.popen("find %s -type f | wc -l" % (folder)).readlines();
        # if not lines or int(lines[0]) == 0:
        #   return None
        lines = os.popen("find %s -type f | xargs ls -rt | head -n %d" %
                         (folder, self.SCAN_FILE_PER_DIR_COUNT)).readlines()
        if not lines or len(lines) == 0:
            return None
        fl = []
        for l in lines:
            filename = l.rstrip('\r\n ')
            if not filename:
                continue
            if (time.time() - os.stat(filename).st_ctime) > 3:
                fl.append(filename)
        return fl

    def run(self):
        self.running_ = True
        if self.thread_:
            logging.debug("notify thread start up %s", threading.currentThread())
        else:
            logging.debug("notify start running")

        if self.watch_way == self.WAIT_LIST:
            while self.running_:
                counter = 0
                start = time.time()
                for p in self.paths:
                    r = self.check_folder(p)
                    if r:
                        # event_handler回调处理任务，如果队列已满会进行阻塞
                        self.event_handler(r)
                        counter += len(r)

                # 延长睡眠时间，过于频繁扫描
                # TODO:优化睡眠时间
                now = time.time()
                if counter > 0 and now - start < self.SLEEP_INTERVAL_SECOND:
                    # 扫描到文件睡眠时间稍微短一点，确保轮询间隔是SLEEP_INTERVAL_SECOND秒
                    # logging.debug("%s sleep ...", threading.currentThread())
                    s = self.SLEEP_INTERVAL_SECOND - (now - start)
                    time.sleep(min(s, self.SLEEP_INTERVAL_SECOND))
                elif counter == 0:
                    # 没有扫描到文件，休眠时间稍微长一点
                    time.sleep(self.SLEEP_INTERVAL_SECOND*2)
        elif self.watch_way == self.WAIT_NOTIFY:
            # TODO:可能通知的比较慢，来不及响应，后面优待测试与优化
            self.notifier.loop(callback=lambda x: not self.running_)

        if self.thread_:
            logging.debug("notify thread exit %s", threading.currentThread())

    def start(self, block=False):
        """启动目录扫描线程, block会阻塞线程直到调用stop线程结束"""
        assert not self.running_, "Notify thread is running"
        if not block:
            self.thread_ = threading.Thread(target=self.run)
            self.thread_.setName('LogNotify')
            self.thread_.setDaemon(True)
            self.thread_.start()
        else:
            self.run()
            logging.debug("notify blockrun exit")

    def stop(self):
        assert self.running_, 'Notify thread not running'
        self.running_ = False
        if self.thread_:
            logging.debug('notify thread join')
            self.thread_.join()

