#!/usr/bin/env python
# coding=utf-8

import os
import time
import json
import psutil
import threading
from redis_utils.redis_op import create_redis, publish_channel
from LogProcessor import set_loading

# text color
_colorred = "\033[01;31m{0}\033[00m{1}"
_colorgrn = "\033[02;32m{0}\033[00m{1}"

ERR_TEXT = lambda x,y='' : _colorred.format(x, y)
TIP_TEXT = lambda x,y='' : _colorgrn.format(x, y)

EXCEPTION_CH = 'bdaudit_exception_behavior'

class SystemInfoCheck(threading.Thread):
    def __init__(self, info_type, threshold, exceed_interval=1, exceed_time=30):
        super(SystemInfoCheck, self).__init__()
        self.info_type = info_type
        self.event = threading.Event()

        # define the rules of alert, if $info is greater $threshold
        # $exceed_time every exceed_interval(second), call alert function
        self.alert_threshold = threshold
        self.exceed_interval = max(int(exceed_interval), 1)
        self.exceed_time = min(int(exceed_time), 600)
        self.exceed_time_min = max(int(exceed_time)/60, 1)
        self.exceed_count = int(time.time()) % self.exceed_time
        self.exceed_count_max = int(self.exceed_time/self.exceed_interval)
        self.exceed_record = [0] * self.exceed_count_max
        self.exceed_record_tmp = [0] * self.exceed_count_max
        self.alert_rate = 0.8 * self.exceed_count_max # 80 percent
        self.should_alert = False
        self.setName(info_type)
        self.redis_obj = create_redis()

    def get_info(self):
        pass

    def set_alert_threshold(self, threshold):
        self.alert_threshold= threshold
        print 'set %s threshold = %d' % (self.info_type, threshold)

    def declare_alert_msg(self, alert_dict):
        return alert_dict
        pass

    def alert(self, content_dict):
        try:
            content = self.declare_alert_msg(content_dict)
            content_dict['content'] = content
            alert_msg = json.dumps(content_dict)
            print 'check check: ', alert_msg
            # redis_obj = create_redis()
            publish_channel(self.redis_obj, EXCEPTION_CH, alert_msg)
            # redis_obj.connection_pool.disconnect()
        except Exception as e:
            # log here
            print e

        print '%s is exceed range!!!!' % self.info_type
        print self.exceed_record
        print self.exceed_record_tmp
        pass

    def exeed_hook(self, *args, **kwargs):
        # do something if system use too much resource(info_type)
        pass

    def under_hook(self, *args, **kwargs):
        # do something while system resource usage is normal
        pass

    def run(self):
        while 1:
            if self.event.isSet():
                break
            info = self.get_info()
            if self.alert_threshold <= info:
                self.exceed_record[self.exceed_count] = 1
                self.exceed_record_tmp[self.exceed_count] = info
                self.exeed_hook()
            else: self.under_hook()

            if sum(self.exceed_record) >= self.alert_rate:
                # do alert action
                info = max(self.exceed_record_tmp)
                alert_dict = {'type': self.info_type, 'logtime': int(time.time()),
                              'info': info, 'threshold': self.alert_threshold,
                              'exceed_time': self.exceed_time_min}
                self.alert(alert_dict)
                # reset the exceed_record
                self.exceed_record = [0] * self.exceed_count_max
                self.exceed_record_tmp = [0] * self.exceed_count_max

            # count + 1 every exceed_interval second
            time.sleep(self.exceed_interval)
            self.exceed_count = (self.exceed_count + 1) % self.exceed_time

        pass


    def start(self):
        super(SystemInfoCheck, self).start()


    def stop(self):
        self.event.set()
        pass


# psutil.cpu_percent(interval=0.1)
class CPUSystemInfoCheck(SystemInfoCheck):
    def __init__(self, threshold):
        super(CPUSystemInfoCheck, self).__init__('cpu', threshold)

    def get_info(self):
        return psutil.cpu_percent()

    def declare_alert_msg(self, alert_dict):
        msg = '使用率 {u}% 连续 {t}分钟 超过阈值 {m}%'
        ret = msg.format(u=alert_dict['info'], t=alert_dict['exceed_time'],
                         m=alert_dict['threshold'])
        return ret


class MEMSystemInfoCheck(SystemInfoCheck):
    def __init__(self, threshold):
        super(MEMSystemInfoCheck, self).__init__('mem', threshold)

    def get_info(self):
        return psutil.virtual_memory().percent

    def declare_alert_msg(self, alert_dict):
        msg = '使用率 {u}% 连续 {t}分钟 超过阈值 {m}%'
        ret = msg.format(u=alert_dict['info'], t=alert_dict['exceed_time'],
                         m=alert_dict['threshold'])
        return ret


class DISKSystemInfoCheck(SystemInfoCheck):
    def __init__(self, threshold, path='/var'):
        super(DISKSystemInfoCheck, self).__init__('disk', threshold)
        self.path = path

    def get_info(self):
        return psutil.disk_usage(self.path).percent

    def exeed_hook(self, *args, **kwargs):
        set_loading(action='STOP')
        pass

    def declare_alert_msg(self, alert_dict):
        msg = '使用率 {u}% 连续 {t}分钟 超过阈值 {m}%'
        ret = msg.format(u=alert_dict['info'], t=alert_dict['exceed_time'],
                         m=alert_dict['threshold'])
        return ret

    def under_hook(self, *args, **kwargs):
        set_loading(action='START')
        pass

class FLOWSystemInfoCheck(SystemInfoCheck):
    pass

if __name__ == '__main__':
    # sic = SystemInfoCheck('cpu', 1)
    # sic = CPUSystemInfoCheck()
    # sic = MEMSystemInfoCheck(30)
    sic = DISKSystemInfoCheck(1)
    sic.start()
    try:
        while 1:time.sleep(1)
    except KeyboardInterrupt:
        sic.stop()
    pass
