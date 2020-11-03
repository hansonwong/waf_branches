# -*- coding:utf-8 -*-
import os
import re
import sys
import esm
import time
import json
import signal
import threading
from collections import defaultdict
import adutils.StringUtil as StringUtil
from adutils.file_monitor import add_file_monitor, add_table_monitor, FsMonitor
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR
from adutils.url_filter_audit import make_url_filter_conf
from rpc.redisrpc.rpclient import RedisRPCClient
from proc_user_login import UserLoginHandler, reload_online_user


class UrlFilterEngine(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.event = threading.Event()
        self.setName('url_filter')
        # record of rule id and ip { IP: set(rule_id) }
        self.ruleid_ip_mapping = defaultdict(set)
        # { user_id: set(IP) }
        self.gip_map = defaultdict(set)
        self.uip_map = defaultdict(set)
        # group/user id and rule mapping { user_id: set(rule_id) }
        self.grule_map = defaultdict(set)
        self.urule_map = defaultdict(set)

        self.user_handler = UserLoginHandler(self.online_hook, self.offline_hook,
                                             callfrom='UrlFilterEngine')

        # client for ips notification service
        self.ips_client = 'RedisRPCIps'
        self.rpc_client = RedisRPCClient('BDAUDIT_IPSCLIENT')
        self.rpc_client.register_function(self.get_online_user)


        # self.lock = threading.Lock()
        reload_online_user(self.online_hook)
        self.update_url_config()

        # self.setDaemon(True)
        # self.start()

    def update_url_config(self, *args, **kwargs):
        # make new url config file
        confs = make_url_filter_conf()
        self.grule_map = defaultdict(set)
        self.urule_map = defaultdict(set)
        print 'processing url config'
        # update url filter rule and ip mapping
        for conf in confs:
            # just process user and user group
            if conf['iType'] == 1: # user
                # update userid_rule mapping
                self.urule_map[conf['iTypeValue']].add(conf['id'])

            elif conf['iType'] == 2: # user group
                self.grule_map[conf['iTypeValue']].add(conf['id'])

            else:
                continue
            print conf

        # update ip rule mapping, once the rule is updated
        self.update_ip_rule()
        self.get_online_user()


    def update_ip_rule(self, user_info=None):
        if user_info is None:
            # update all
            self.ruleid_ip_mapping = defaultdict(set)
            for id_ in self.urule_map:
                for ip in self.uip_map[id_]:
                    self.ruleid_ip_mapping[ip] |= self.urule_map[id_]

            for id_ in self.grule_map:
                for ip in self.gip_map[id_]:
                    self.ruleid_ip_mapping[ip] |= self.grule_map[id_]

        else: # just update user of user_info
            if user_info.isOnline == 1: # user online
                if user_info.uid in self.urule_map:
                    self.ruleid_ip_mapping[user_info.IP] = self.urule_map[user_info.uid]
                if user_info.gid in self.grule_map:
                    self.ruleid_ip_mapping[user_info.IP] |= self.grule_map[user_info.gid]
                pass
            else: # user offline
                try:
                    self.ruleid_ip_mapping.pop(user_info.IP)
                except:
                    pass

        print 'U'*55
        print self.ruleid_ip_mapping
        pass



    def online_hook(self, user_info):
        # call when a new user login
        print 'I'*55
        print user_info
        # add user ip to two dict, save the relationship of uid->ip and gid->ip,
        # so we can find ip by user's uid or gid after
        self.uip_map[user_info.uid].add(user_info.IP)
        self.gip_map[user_info.gid].add(user_info.IP)
        print self.uip_map
        print self.gip_map
        # update rule_ip mapping, add new login ip to current rule
        self.update_ip_rule(user_info)
        # call ips service
        if len(self.ruleid_ip_mapping[user_info.IP]) > 0:
            _ids = self.ruleid_ip_mapping[user_info.IP]
            self.rpc_client.invoke(self.ips_client, "IpOnline",
                                  [{"Ip": user_info.IP, "Ids": list(_ids)}], async_=True)
        print 'P'*55
        pass

    def offline_hook(self, user_info):
        # call when a user logout
        print 'I'*55
        print user_info
        # find ip by uid(get from redis), remove if exists
        if user_info.IP in self.uip_map[user_info.uid]:
            self.uip_map[user_info.uid].remove(user_info.IP)
            if len(self.uip_map[user_info.uid]) == 0:
                self.uip_map.pop(user_info.uid)
        if user_info.IP in self.gip_map[user_info.gid]:
            self.gip_map[user_info.gid].remove(user_info.IP)
            if len(self.gip_map[user_info.gid]) == 0:
                self.gip_map.pop(user_info.gid)
        print self.uip_map
        print self.gip_map
        # update rule_ip mapping, remove logout ip from rule
        self.update_ip_rule(user_info)
        self.rpc_client.invoke(self.ips_client, "IpOffline",
                              [{"Ip": user_info.IP}], async_=True)
        print 'P'*55
        pass


    def get_online_user(self, *args, **kwargs):
        online_users = [{'Ip': ip, 'Ids': list(ids)}
                        for ip, ids in self.ruleid_ip_mapping.items()
                        if len(ids) > 0]

        if len(online_users) > 0:
            self.rpc_client.invoke(self.ips_client, "IpOnline", online_users, async_=True)
        return None

    def run(self):
        print 'start_reload'
        fs_monitor = FsMonitor()
        # add_table_monitor('adutils/UrlFilterEngine.py', self.update_url_config)
        add_file_monitor('/data/conf/url_rulefiles', self.update_url_config)
        # # add_file_monitor('/usr/local/bluedon/conf/online_users', self.online_users_reload_handler)
        try:
            fs_monitor.start()
            self.user_handler.start()
            while 1:
                if self.event.isSet():
                    # raise RuntimeError
                    break
                time.sleep(2)
            ADLOG_INFO('[UrlFilterEngine] Exiting...')
        except KeyboardInterrupt as e:
            ADLOG_INFO('[UrlFilterEngine] Exiting...')
        except Exception as e:
            ADLOG_ERR('[UrlFilterEngine] Exiting...%s' % e)
        finally:
            self.user_handler.stop()
            self.rpc_client.stop()
            fs_monitor.stop()
            ADLOG_INFO('[UrlFilterEngine] LogNotify Exited...')
        ADLOG_INFO('[UrlFilterEngine] Exited...')

    def start(self):
        super(UrlFilterEngine, self).start()

    def stop(self):
        self.event.set()
        pass

    def acquire(self):
        # self.lock.acquire()
        pass

    def unlock(self):
        # self.lock.release()
        pass


if __name__ == '__main__':
    obj = UrlFilterEngine()
    obj.start()
    time.sleep(60)
    obj.stop()
    pass
