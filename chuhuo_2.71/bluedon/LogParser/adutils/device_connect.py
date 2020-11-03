#!/usr/bin/env python
# coding=utf-8

import sys
import time
import Queue
import threading

from adutils.audit_logger import ADLOG_INFO, ADLOG_ERR
from adutils.config import fetchall_sql as fcal_3306
from adutils.config import fetchone_sql as fetch_3306
from adutils.redis_utils.redis_remote_op import RemoteRedis, tag_device_id
from adutils.file_monitor import add_table_monitor, FsMonitor

reload(sys)
sys.setdefaultencoding('utf-8')

# a simple enum
class Enum(tuple): __getattr__ = tuple.index
ROLE = Enum(['superior', 'INFERIO', 'MYSELF'])


class DeviceInfo(object):
    def __init__(self, myid, ip, port, role=ROLE.MYSELF):
        super(DeviceInfo, self).__init__()
        self.ID = myid
        self.ip = ip
        self.port = port
        self.role = role
        self.receiver = self.set_receiver()


    def __repr__(self):
        return 'id: {i} ip: {ip} port: {port} role:{role}'.format(i=self.ID,
                    ip=self.ip, port=self.port, role=self.role)

    def set_receiver(self):
        conf = {
            'host': self.ip,
            'port': self.port,
            'db': 0,
            # 'password': 'fw@redis',
        }
        ADLOG_INFO('RedisConf=%s' % conf)
        return RemoteRedis(**conf)


class DeviceConnect(threading.Thread):
    def __init__(self):
        super(DeviceConnect, self).__init__()
        # self.device = DeviceInfo(myid, ip, port, ROLE.MYSELF)
        self.dev_id = self.get_device_id()
        self.superior = set()
        self.inferior = set()
        self.trust_inferior_id = set()
        self.superior_receiver = set()
        self.event = threading.Event()
        self.queue = Queue.Queue(1024)
        self.check_count = 0
        self.check_time = int(time.time())
        self.check_dt = 0
        self.MAX_CHECK = 100
        self.MAX_CHECK_TIME = 10
        self.setName('devconnect')
        self.fs_monitor = FsMonitor()
        self.update_relationship()


    def get_device_id(self):
        sql = 'SELECT SerialNum FROM m_tbsystem_info LIMIT 1;'
        ret = fetch_3306(sql)

        return ret.get('SerialNum', '0')


    def run(self):
        ADLOG_INFO('[DeviceConnect] Started')
        # self.update_relationship()
        add_table_monitor('m_tbcascade', self.update_relationship)
        self.fs_monitor.start()
        while 1:
            if self.event.isSet(): break
            if self.queue.empty():
                time.sleep(0.1)
                continue

            # check every MAX_CHECK messages
            # if self.check_count >= self.MAX_CHECK:
            # if self.check_count % self.MAX_CHECK == 0:
            #     self.check_count = 0
            #     self.update_relationship()

            # # adjust update rate according to messages rate
            # if self.check_count >= self.MAX_CHECK:
            #     cur_time = int(time.time())
            #     self.check_dt = cur_time - self.check_time
            #     self.check_time = cur_time

            #     if self.check_dt > self.MAX_CHECK_TIME:
            #         self.MAX_CHECK = max(0, self.MAX_CHECK - 100)
            #     elif self.check_dt < self.MAX_CHECK_TIME:
            #         self.MAX_CHECK = min(10000, self.MAX_CHECK + 100)
            #     else:
            #         pass

            #     print 'Z'*55
            #     print 'check_dt=', self.check_dt
            #     print 'MAX_CHECK=', self.MAX_CHECK
            #     self.check_count = 0
            #     self.update_relationship()

            # get a message from queue and send to all current superior
            ch, msg = self.queue.get()
            for dev in self.superior:
                dev.receiver.publish(ch, msg)

            self.check_count += 1

        self.fs_monitor.stop()
        ADLOG_INFO('[DeviceConnect] Exited')


    def update_relationship(self, *args, **kwargs):
        sql = 'SELECT sDeviceId, sIp, sPushPort, iType FROM m_tbcascade \
            WHERE iOnline=1 and iTrust=1;'

        ret = fcal_3306(sql)

        # clear previous relationship
        self.superior = set()
        self.inferior = set()
        self.trust_inferior_id = set()

        for dev in ret:
            d = DeviceInfo(dev['sDeviceId'], dev['sIp'], dev['sPushPort'],
                           int(dev['iType']))

            try:
                d.receiver.open()
                if int(dev['iType']) == ROLE.superior: self.superior.add(d)
                elif int(dev['iType']) == ROLE.INFERIO:
                    self.inferior.add(d)
                    self.trust_inferior_id.add(dev['sDeviceId'])
            except:
                print 'error processing dev %s' % dev['sIp']
                pass

        print 'Y'*55
        print self.superior
        print self.inferior


    def my_message(self, msg_dev_id):
        # check if message is product from this device
        if msg_dev_id == '-' or len(msg_dev_id) == 0:
            return True
        return False

    def upload_to_superiors(self, chn, msg):
        # tag id to the message, if msg_dev_id is None(msg comes from this
        # device)
        msg_with_id = tag_device_id(msg, self.dev_id)

        for dev in self.superior:
            # print 'send [%s] to [%s] in ch[%s]' % (msg_with_id, dev, chn)
            # dev.receiver.publish(chn, msg_with_id)
            if not self.queue.full():
                self.queue.put((chn, msg_with_id))

    def forward_to_superiors(self, chn ,msg):
        # just forward the message to superios
        for dev in self.superior:
            # dev.receiver.publish(chn, msg)
            if not self.queue.full():
                self.queue.put((chn, msg))
        pass

    def start(self):
        super(DeviceConnect, self).start()

    def stop(self):
        self.event.set()



if __name__ == '__main__':
    dc = DeviceConnect()
    dc.update_relationship()
    dc.start()
    dc.upload_to_superiors('netlog_kkkk', '{"a":1}')
    try:
        while 1:
            time.sleep(1)
            dc.upload_to_superiors('netlog_kkkk', '{"a":1}')
    except KeyboardInterrupt:
        pass
    print 'stopping...'
    dc.stop()
    dc.join()
    print 'stopped'
    pass
