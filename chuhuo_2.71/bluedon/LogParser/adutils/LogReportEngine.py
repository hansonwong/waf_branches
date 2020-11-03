#!/usr/bin/python
#-*-coding:utf8-*-

import threading
import ctypes
import time
import Queue
import signal
from jinja2 import Environment, FileSystemLoader
from redis_utils.redis_op import create_redis, publish_channel, subscribe_channel
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR

TEMPLATE_PATH = '/usr/local/bluedon/LogParser/adutils/templates'
report_types = {'ftp': 'ftp.template',
                'web': 'web.template',
                'sql': 'sql.template'}

ftp_arg = {'time': '', 'actid': '', 'act': '', }


def get_report_template(report_type):
    if report_type not in report_types:
        # log here
        ADLOG_DEBUG('No reporter for tpye[%s]' % report_type)
        return None

    try:
        ldr = FileSystemLoader(TEMPLATE_PATH)
        env = Environment(loader=ldr)
        template = env.get_template(report_types[report_type])
        return template
    except Exception as e:
        # log here
        ADLOG_ERR('get_report_template error %s' % e)
        return None


def render_report_template(report_temp, report_items):
    if report_temp is None:
        # log here
        ADLOG_DEBUG('No template')
        return None
    try:
        report_str = report_temp.render(log_item=report_items)
        return report_str
    except:
        # log here
        ADLOG_ERR('render report template error')
        return None




class AuditLogReporter(object):
    report_queue = Queue.Queue(maxsize=4096)
    AUDIT_LOG_REPORT_CHN = 'AUDIT_LOG_REPORT_CHN'
    def __init__(self):
        super(AuditLogReporter, self).__init__()

    @classmethod
    def report_msg(cls, msg, block=True, timeout=0):
        # if cls.report_queue.full():
        #     # log here
        #     print 'AuditLogReporter: Queue is full'
        #     return
        # print 'put'
        # print id(cls.report_queue)
        # cls.report_queue.put(msg, block=block, timeout=timeout)
        re = create_redis()
        publish_channel(re, cls.AUDIT_LOG_REPORT_CHN, msg)
        re.connection_pool.disconnect()

    @classmethod
    def get_report_msg(cls):
        msg = cls.report_queue.get()
        return msg



class LogReportEngine():
    """统计各类日志"""
    def __init__(self):
        #加载动态库
        self.so = ctypes.cdll.LoadLibrary
        self.lib = self.so("/usr/lib/libsdktest.so")
        self._worker = None
        self._agent = None
        self.enable = False
        #创建队列
        self.objects = Queue.Queue(maxsize = 4096)

    def push(self, obj, block=True, timeout=0):
        #连不上后台时，内部上报接口会有阻塞，队列满则弃
        if self.objects.full():
            print "Queue is full, obj drop"
            return
        self.objects.put(obj, block=block, timeout=timeout)

    def agent_run(self):
        #初始化并运行代理
        self.lib.bd_agent_start()

    def worker_run(self):
        re = create_redis()
        while self.enable:
            try:
                #从队列获取一个数据，当队列为空时，会阻塞直到有数据
                # obj = AuditLogReporter.get_report_msg()
                with subscribe_channel(re, AuditLogReporter.AUDIT_LOG_REPORT_CHN) as msgs:
                    for obj in msgs:
                        msg = obj['data']
                        if isinstance(msg, str):
                        # obj = self.objects.get()
                            # transform to gbk
                            gbk_msg = msg.decode('utf8').encode('gbk')
                            # print 'gbk_msg: ',gbk_msg.decode('gbk')
                            #内部上报接口
                            # self.lib.bd_agent_report(msg)
                            # comment at 20170213 for test(too many  output)
                            # self.lib.bd_agent_report(gbk_msg)
            except Exception as e:
                # log here
                ADLOG_ERR('[LogReportEngine] Error happend when reporting log')
                ADLOG_ERR(e)
                if not re:
                    re = create_redis()
                    ADLOG_ERR('[LogReportEngine]Redis isinstance creating Error')
                pass

    #外部上报接口
    def logreport(self, obj=None):
        #加入队列
        self.push(obj)

    # register TERM signal action, when get TERM signal raise a runtimeerror
    def sighandler(self, v1, v2):
        ADLOG_INFO('[LogReportEngine] sighandler TERM Signal...')
        self.stop()

    def start(self):
        if not self._worker:
            #代理线程
            self._agent = threading.Thread(target=self.agent_run)
            self._agent.daemon = True
            self._agent.setName('agent')
            self._agent.start()
            #上报线程
            self.enable = True
            self._worker = threading.Thread(target=self.worker_run)
            self._worker.daemon = True
            self._worker.setName('report_engine')
            self._worker.start()
            # self._worker.join()
            try:
                signal.signal(signal.SIGTERM,self.sighandler)
                while 1:
                    # AuditLogReporter.report_msg('<?xml version="1.0" encoding="GBK"?><ViewData name="health-index" version="2.00"><AdditionalData meaning="系统健康指数" type="xml"><xml><cpu-usage>0</cpu-usage><mem-usage>13246628/32716536</mem-usage><disk-usage>404496613/-1131625479</disk-usage><service-status><item name="网络行为监控" state ="normal"  reason=""/></service-status></xml></AdditionalData></ViewData>')
                    time.sleep(1)
            except (KeyboardInterrupt, RuntimeError) as e:
                ADLOG_ERR(e)
            finally:
                ADLOG_INFO('[LogReportEngine] Exited...')

    def stop(self):
        #结束上报
        self.enable = False
        #结束代理
        self.lib.bd_agent_stop()


if __name__ == '__main__':
    eg = LogReportEngine()
    eg.start()
    # time.sleep(1)
    # print 'started...'
    # eg.logreport('<?xml version="1.0" encoding="GBK"?><ViewData name="health-index" version="2.00"><AdditionalData meaning="系统健康指数" type="xml"><xml><cpu-usage>0</cpu-usage><mem-usage>13246628/32716536</mem-usage><disk-usage>404496613/-1131625479</disk-usage><service-status><item name="网络行为监控" state ="normal"  reason=""/></service-status></xml></AdditionalData></ViewData>')
    # AuditLogReporter.report_msg('<?xml version="1.0" encoding="GBK"?><ViewData name="health-index" version="2.00"><AdditionalData meaning="系统健康指数" type="xml"><xml><cpu-usage>0</cpu-usage><mem-usage>13246628/32716536</mem-usage><disk-usage>404496613/-1131625479</disk-usage><service-status><item name="网络行为监控" state ="normal"  reason=""/></service-status></xml></AdditionalData></ViewData>')
    # eg.stop()
