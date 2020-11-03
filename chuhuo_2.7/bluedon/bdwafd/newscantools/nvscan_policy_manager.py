#!/usr/bin/env python
#-*-encoding:UTF-8-*-

from random import randint
import os
import sys
import MySQLdb
from nvscan_xmlrpc import *
import logging
import ConfigParser
from nvscan_policy_parse import *
from HostScan import db_manager

WAF_CONFIG   = "/var/waf/waf.conf"

cfg    = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
HOST   = cfg.get("mysql","db_ip").replace('"','')
USER   = cfg.get("mysql","db_user").replace('"','')
PASSWD = cfg.get("mysql","db_passwd").replace('"','')

POLICY_TMP_DIR = '/tmp/'

def DEBUG(msg):
    logging.getLogger().info(msg)

def WARN(msg):
    logging.getLogger().warn('nvscan_policy_manager, ' + msg)

def ERROR(msg):
    logging.getLogger().error('nvscan_policy_manager, ' + msg)


class nvscan_policy_manager(object):
    """docstring for nvscan_policy_manager"""
    def __init__(self, policy_id):
        try:
            self.policy_id = policy_id
            self.db = db_manager()
            self.scanner = nvscan_xmlrpc()
        except Exception, e:
            ERROR("nvscan_policy_manager.__init__:"+str(e))

    def get_nvscan_policy_id_from_host_policy(self):
        DEBUG('Enter nvscan_policy_manager.get_nvscan_policy_id_from_host_policy')
        try:
            sql = 'select nvscan_policy_id from host_policy where `id` = %d' % (int(self.policy_id))
            res = self.db.get_one_item_from_db(sql)
            DEBUG(res)
            if res:
                return res.get('nvscan_policy_id')
            else:
                return None
        except Exception, e:
            ERROR("nvscan_policy_manager.get_nvscan_policy_id_from_host_policy:"+str(e))
        DEBUG('Leave nvscan_policy_manager.get_nvscan_policy_id_from_host_policy')

    def policy_add(self):
        DEBUG('Enter nvscan_policy_manager.policy_add')
        try:
            #Step 1.generate new policy file
            real_file_name = self.policy_generate()

            #Step 2.add policy to nvscan and clear policy file
            nvscan_policy_id = self.scanner.add_policy(real_file_name)
            DEBUG('new nvscan_policy_id is ' + str(nvscan_policy_id))
            if nvscan_policy_id == -1 or not nvscan_policy_id:
                nvscan_policy_id == -1
                ERROR('Add policy failed, policy_id:%s'%(self.policy_id))
            DEBUG('remove tmp file')
            os.remove('/tmp/'+real_file_name)
            
            #Step 3.Modify  policy table set nvcan_policy_id = new policy_id
            sql = 'update host_policy set nvscan_policy_id = %d where `id` = %d' % (nvscan_policy_id, int(self.policy_id))
            self.db.set_item_to_db(sql)

        except Exception, e:
            ERROR("nvscan_policy_manager.policy_add:"+str(e))
        DEBUG('Leave nvscan_policy_manager.policy_add')

    def policy_update(self):
        DEBUG('Enter nvscan_policy_manager.policy_update')
        try:
            #Step 1.delete nvscan policy by nvscan_policy_id
            nvscan_policy_id = self.get_nvscan_policy_id_from_host_policy()
            self.scanner.del_policy(nvscan_policy_id)

            #Step 2.call policy_add(old policy_id)
            self.policy_add()
            
        except Exception, e:
            ERROR("nvscan_policy_manager.policy_update:"+str(e))
        DEBUG('Leave nvscan_policy_manager.policy_update')

    def policy_delete(self):
        DEBUG('Enter nvscan_policy_manager.policy_delete')
        try:
            if self.policy_id == '1' or self.policy_id == '2':
                ERROR('Default policy:%s do not allowed to be deleted. Please check if device under attack.'%(self.policy_id))
                return

            #Step 1.get nvscan_policy id 
            # nvscan_policy_id = self.get_nvscan_policy_id_from_host_policy()
            # When action is 'delete', the policy_id means nvscan_policy_id
            nvscan_policy_id = self.policy_id
            DEBUG('get nvscan_policy_id ' + str(nvscan_policy_id))

            #Step 2.call xmlrpc to delete policy by nvscan_policy_id
            self.scanner.del_policy(nvscan_policy_id)

            #Step 3.delete record in host_policy
            # sql = 'delete from host_policy where `id` = %d'%(int(self.policy_id))
            # self.db.set_item_to_db(sql)
            # DEBUG('delete policy:%s success.'%(self.policy_id))

            #Step 4.delete record in nvscan_server_preference and nvscan_plugin_preference
            #
            
        except Exception, e:
            ERROR("nvscan_policy_manager.policy_delete:"+str(e))
        DEBUG('Leave nvscan_policy_manager.policy_delete')

    def policy_generate(self):
        DEBUG('Enter nvscan_policy_manager.policy_generate')
        try:
            #Step 1.get server_preference and plugin preference and generate them
            #common_config = {'policyName':'xxx', 'policyOwner':'xyy'}
            real_file_name = 'nvscan' + self.policy_id + '.nessus'
            policy_file_name = POLICY_TMP_DIR + real_file_name
            common_config = {'policyName':real_file_name, 'policyOwner':'admin'}

            server_config = []
            sql = 'select * from nvscan_server_preference where policy_id = %s' % (self.policy_id)
            res = self.db.get_all_item_from_db(sql)
            if res:
                for item in res:
                    #server_config = [{'name':'throttle_scan', 'value':'xxxx'}, {'name':'listen_address', 'value':'1.1.1.1'}]
                    tmp_item = {'name':item.get('name'), 'value':item.get('value')}
                    server_config.append(tmp_item)

            plugin_config = []            

            #plugin_config = [{'pluginId':'15868'
            #, 'pluginName':'Hydra (NASL wrappers options)'
            #, 'fullName':'Hydra (NASL wrappers options)[entry]:Timeout (in seconds) :'
            #, 'preferenceName':'Timeout (in seconds) :'
            #, 'preferenceValues':'30'
            #, 'preferenceType':'entry'
            #, 'selectedValue':''}]
            sql = 'select * from nvscan_plugin_preference where policy_id = %s' % (self.policy_id)
            res = self.db.get_all_item_from_db(sql)
            if res:
                for item in res:
                    tmp_item = {'pluginId':item.get('pluginId')
                    , 'pluginName':item.get('pluginName')
                    , 'fullName':item.get('fullName')
                    , 'preferenceName':item.get('preferenceName')
                    , 'preferenceValues':item.get('preferenceValues')
                    , 'preferenceType':item.get('preferenceType')
                    , 'selectedValue':item.get('selectedValue')}
                    plugin_config.append(tmp_item)

            p = policyer()
            DEBUG(len(common_config))
            p.generate_common_config(common_config)
            DEBUG(len(server_config))
            p.generate_server_config(server_config)
            DEBUG(len(plugin_config))
            p.generate_plugin_config(plugin_config)

            #Step 2.get all plugin id and generate them (need support ddos switch)
            #plugin_id_list = [{'PluginId':'18895'
            #, 'PluginName':'FreeBSD : phpbb -- multiple vulnerabilities (326c517a-d029-11d9-9aed-000e0c2e438a)'
            #, 'Family':'FreeBSD Local Security Checks'}]
            plugin_id_list = []
            
            vul_id_list = []
            sql = 'select `vul_id` from host_policy_ref where policy_id = %d' % (int(self.policy_id))
            res = self.db.get_all_item_from_db(sql)
            DEBUG(len(res))
            if res:
                for vul in res:
                    vul_id_list.append(vul.get('vul_id'))

            ddos_vul_list = []
            enable_ddos = -1
            sql = 'select `enable_ddos` from host_policy where id = %d' % (int(self.policy_id))
            res = self.db.get_one_item_from_db(sql)
            DEBUG(res)
            if res:
                enable_ddos = res.get('enable_ddos')

            if enable_ddos == 1:
                DEBUG('enable_ddos is open')
                #do something to remove ddos plugins
                sql = 'select `vul_id` from vul_info where ddos = 1'
                ddos_res = self.db.get_all_item_from_db(sql)
                if ddos_res:
                    for ddos_vul_id in ddos_res:
                        ddos_vul_list.append(ddos_vul_id.get('vul_id'))
                #get Difference set
                # DEBUG(len(vul_id_list))
                vul_id_list = list(set(vul_id_list).difference(set(ddos_vul_list)))
                # DEBUG(len(ddos_vul_list))
                # DEBUG(len(vul_id_list))
            else:
                DEBUG('enable_ddos is close')
            
            #get plugin info by vul_id
            for vul_id in vul_id_list:
                sql = 'select vul_name, family_old from vul_info where vul_id = %d' % (int(vul_id))
                res = self.db.get_one_item_from_db(sql)
                if res:
                    tmp_item = {'PluginId':vul_id, 'PluginName':res.get('vul_name'), 'Family':res.get('family_old')}
                    plugin_id_list.append(tmp_item)

            p.combine_plugin_by_id(plugin_id_list)
            p.write_policy(policy_file_name) #change temp policy file name

            return real_file_name
        except Exception, e:
            ERROR("nvscan_policy_manager.policy_generate:"+str(e))
        DEBUG('Leave nvscan_policy_manager.policy_generate')
        
def init_log(console_level, file_level, logfile):
    formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
    logging.getLogger().setLevel(logging.INFO)
    
    console_log = logging.StreamHandler()
    console_log.setLevel(console_level)
    console_log.setFormatter(formatter)
    
    file_log = logging.FileHandler(logfile)
    file_log.setLevel(file_level)
    file_log.setFormatter(formatter)

    logging.getLogger().addHandler(file_log)
    logging.getLogger().addHandler(console_log)
#end def

def checkNvscan():
    try:
        cmd='''#!/bin/sh
process=`ps -ef | grep "nvscan-service" | grep -v grep|wc -l`
if test $process -eq 0
then
    echo "no"
    service nvscand start
else
    echo "yes"
fi
'''
        fp = open('/tmp/checknvs.sh', 'w+')
        fp.write(cmd)
        fp.close()
        os.system('/bin/sh /tmp/checknvs.sh')
        os.system('/bin/rm /tmp/checknvs.sh')
    except Exception, e:
        logging.getLogger().error("File:HostScan.py, checkNvscan:" + str(e))


if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    if len(sys.argv) < 3:
        WARN('__main__: need param action and policy id')
        sys.exit(-1)
    else:
        checkNvscan()
        policy_id = sys.argv[2].replace('#', '').strip()
        policy_manager = nvscan_policy_manager(policy_id)
        if sys.argv[1].strip() == 'add':
            policy_manager.policy_add()
        elif sys.argv[1].strip() == 'update':
            policy_manager.policy_update()
        elif sys.argv[1].strip() == 'delete':
            policy_manager.policy_delete()
        else:
            WARN('__main__: No such action = ' + sys.argv[1])