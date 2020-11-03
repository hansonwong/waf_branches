#!/usr/bin/env python
#-*-encoding:UTF-8-*-

######################################################################
## Before import this moudle pls read me.
## The class policyer is designed for a xml file which size is small.
## Do not use this module for a large xml file.
## Author: yuying xia
## Date: 2013-12-11
## ToDo: 2013-12-11 stage1 and stage 2 complete
##       2013-12-12 stage3 complete. plugin id --- doing(90% function combine_plugin_by_id)
#####################################################################

import logging
import xml.etree.cElementTree as et
import os
import StringIO
import cgi

def DEBUG(msg):
    logging.getLogger().info(msg)

def WARN(msg):
    logging.getLogger().warn(msg)

def ERROR(msg):
    logging.getLogger().error(msg)


class policyer(object):
    """docstring for policyer"""
    def __init__(self):
        try:
            self.policy_tpl = '''<nvscanClientData_v2>
<Policy>
<policyName>all</policyName>
<policyOwner>admin</policyOwner>
<visibility>private</visibility>
<policyComments></policyComments>

<Preferences>
<ServerPreferences>
</ServerPreferences>
<PluginsPreferences>
</PluginsPreferences>
</Preferences>
<FamilySelection>
<FamilyItem>
<FamilyName>MacOS X Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>DNS</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Gain a shell remotely</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Solaris Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Port scanners</FamilyName>
<Status>enabled</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Web Servers</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>SMTP problems</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Brute force attacks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Service detection</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>CGI abuses : XSS</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Debian Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Mandriva Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Databases</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Denial of Service</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Default Unix Accounts</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Settings</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Backdoors</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>HP-UX Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>VMware ESX Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>SCADA</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>General</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Oracle Linux Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Red Hat Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>FreeBSD Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>CGI abuses</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Netware</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Windows : User management</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Amazon Linux Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Peer-To-Peer File Sharing</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Slackware Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>SNMP</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Fedora Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Gentoo Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Ubuntu Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Misc.</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>FTP</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Firewalls</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Windows : Microsoft Bulletins</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Junos Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Mobile Devices</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Policy Compliance</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Windows</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>SuSE Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>RPC</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>CentOS Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>AIX Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>CISCO</FamilyName>
<Status>mixed</Status>
</FamilyItem>
<FamilyItem>
<FamilyName>Scientific Linux Local Security Checks</FamilyName>
<Status>mixed</Status>
</FamilyItem>
</FamilySelection>
<IndividualPluginSelection>
<PluginItem><PluginId>34220</PluginId>
<PluginName>Netstat Portscanner (WMI)</PluginName>
<Family>Port scanners</Family>
<Status>enabled</Status>
</PluginItem><PluginItem><PluginId>14274</PluginId>
<PluginName>Nessus SNMP Scanner</PluginName>
<Family>Port scanners</Family>
<Status>enabled</Status>
</PluginItem><PluginItem><PluginId>14272</PluginId>
<PluginName>netstat portscanner (SSH)</PluginName>
<Family>Port scanners</Family>
<Status>enabled</Status>
</PluginItem><PluginItem><PluginId>10180</PluginId>
<PluginName>Ping the remote host</PluginName>
<Family>Port scanners</Family>
<Status>enabled</Status>
</PluginItem><PluginItem><PluginId>10335</PluginId>
<PluginName>Nessus TCP scanner</PluginName>
<Family>Port scanners</Family>
<Status>enabled</Status>
</PluginItem><PluginItem><PluginId>11219</PluginId>
<PluginName>Nessus SYN scanner</PluginName>
<Family>Port scanners</Family>
<Status>enabled</Status>
</PluginItem>
</IndividualPluginSelection>
</Policy>
</nvscanClientData_v2>'''

            self.server_preference_tpl = '''<preference>
<name>%s</name>
<value>%s</value>
</preference>'''

            self.plugin_preference_tpl = '''<item>
 <pluginName>%s</pluginName>
 <pluginId>%s</pluginId>
<fullName>%s</fullName>
<preferenceName>%s</preferenceName>
<preferenceType>%s</preferenceType>
<preferenceValues>%s</preferenceValues>
<selectedValue>%s</selectedValue>
</item>'''

            self.family_item_tpl = '''<FamilyItem>
<FamilyName>%s</FamilyName>
<Status>%s</Status>
</FamilyItem>'''

            self.plugin_item_tpl = '''<PluginItem>
<PluginId>%s</PluginId>
<PluginName>%s</PluginName>
<Family>%s</Family>
<Status>enabled</Status>
</PluginItem>'''

            fp = StringIO.StringIO(self.policy_tpl)
            self.tree = et.ElementTree()
            self.tree.parse(fp)
            self.root = self.tree.getroot()
            fp.close()
            self.count = 0

        except Exception, e:
            ERROR("policyer.__init__:"+str(e))

    def set_policy_all_preference(self, common_config, service_config, plugin_config):
        DEBUG('Enter policyer.set_policy_all_preference')
        try:
            self.find_tag_2(self.root, common_config, service_config, plugin_config)
        except Exception, e:
            ERROR("policyer.set_policy_all_preference:"+str(e))
        DEBUG('Leave policyer.set_policy_all_preference')

    #stage 1.root, policyname, text
    #stage 2.root, ServicePreferences, preference, throttle_scan, value
    #stage 3.root, PluginsPreferences, item, pluginsName/pluginID, preferenceName, preferenceValues
    #
    #common_config = {'policyName':'xxx', 'policyOwner':'admin'}
    #service_config = [{'name':'throttle_scan', 'value':'yes'}, {'name':'listen_address', 'value':'0.0.0.0'}]
    #plugin_config = [{'pluginId':'15868', 'preferenceName':['Timeout (in seconds) :', 'Try empty passwords'], 'preferenceValues':['30', 'yes']}]
    #
    def find_tag_2(self, root, common_config, service_config, plugin_config):
        DEBUG('Enter policyer.find_tag_2')
        try:
            DEBUG('CALL ME ' + str(self.count))
            self.count += 1
            for child in root:
                if common_config.has_key(child.tag):
                    DEBUG('before ' + child.tag + '=' + child.text)
                    child.text = common_config.get(child.tag)
                    DEBUG('after ' + child.tag + '=' + child.text)

                elif child.tag == 'ServerPreferences':
                    for preference in child.getchildren():
                        name = preference.find('name')
                        res = self.get_item_from_service_config(name.text, service_config)
                        if res:
                            # DEBUG('before ' + name.text + ' = ' + preference.find('value').text)
                            preference.find('value').text = res
                            # DEBUG('after ' + name.text + ' = ' + preference.find('value').text)

                elif child.tag == 'PluginsPreferences':
                    for item in child.getchildren():
                        plugin_id = item.find('pluginId')
                        preference_name = item.find('preferenceName')
                        # DEBUG('plugin_id:'+plugin_id.text)
                        res = self.get_item_from_plugin_config(plugin_id.text, preference_name.text, plugin_config)
                        if res:
                            # DEBUG('===========find it==========')
                            item.find('preferenceValues').text = res
                            # DEBUG('===========find end==========')

                elif not child.getchildren():
                    continue
                else:
                    self.find_tag_2(child, common_config, service_config, plugin_config)
        except Exception, e:
            ERROR("policyer.find_tag_2:"+str(e))
        DEBUG('Leave policyer.find_tag_2')

    def get_item_from_service_config(self, keyname, service_config):
        try:
            for item in service_config:
                if item.get('name') == keyname:
                    return item.get('value')
            return None
        except Exception, e:
            ERROR("policyer.get_item_from_service_config:"+str(e))

    def get_item_from_plugin_config(self, plugin_id, preference_name, plugin_config):
        try:
            for item in plugin_config:
                if item.get('pluginId') == plugin_id:
                    if preference_name in item.get('preferenceName'):
                        return item.get('preferenceValues')[item.get('preferenceName').index(preference_name)]
            return None
        except Exception, e:
            ERROR("policyer.get_item_from_plugin_config:"+str(e))

    #stage 1.root, policyname, text
    #common_config = {'policyName':'xxx', 'policyOwner':'admin'}
    def generate_common_config(self, common_config):
        DEBUG('Enter policyer.generate_common_config')
        try:
            self.find_tag_3(self.root, common_config)
        except Exception, e:
            ERROR("policyer.generate_common_config:"+str(e))
        DEBUG('Leave policyer.generate_common_config')

    def find_tag_3(self, root, common_config):
        # DEBUG('Enter policyer.find_tag_3')
        try:
            # DEBUG('CALL ME ' + str(self.count))
            self.count += 1
            for child in root:
                if common_config.has_key(child.tag):
                    DEBUG('before ' + child.tag + '=' + child.text)
                    child.text = common_config.get(child.tag)
                    DEBUG('after ' + child.tag + '=' + child.text)

                elif not child.getchildren():
                    continue
                else:
                    self.find_tag_3(child, common_config)
        except Exception, e:
            ERROR("policyer.find_tag_3:"+str(e))
        # DEBUG('Leave policyer.find_tag_3')


    #stage 2.root, ServicePreferences, preference, throttle_scan, value
    #server_config = [{'name':'throttle_scan', 'value':'yes'}, {'name':'listen_address', 'value':'0.0.0.0'}]
    def generate_server_config(self, server_config):
        DEBUG('Enter policyer.generate_server_config')
        try:
            if not server_config:
                ERROR('server_config is None, return')
                return
            server_preferences = self.find_tag(self.root, 'ServerPreferences')
            for item in server_config:
                tmp_item = self.server_preference_tpl%(item.get('name'), item.get('value'))
                server_preferences.append(et.fromstring(tmp_item))

        except Exception, e:
            ERROR("policyer.generate_server_config:"+str(e))
        DEBUG('Leave policyer.generate_server_config')

    #stage 3.root, PluginsPreferences, item, pluginsName/pluginID, preferenceName, preferenceValues
    #plugin_config = [{'pluginId':'15868'
    #, 'pluginName':'Hydra (NASL wrappers options)'
    #, 'fullName':'Hydra (NASL wrappers options)[entry]:Timeout (in seconds) :'
    #, 'preferenceName':'Timeout (in seconds) :'
    #, 'preferenceValues':'30'
    #, 'preferenceType':'entry'
    #, 'selectedValue':''}]
    #
    def generate_plugin_config(self, plugin_config):
        DEBUG('Enter policyer.generate_plugin_config')
        try:
            if not plugin_config:
                ERROR('plugin_config is None, return, pls check')
                return
            plugin_preference = self.find_tag(self.root, 'PluginsPreferences')
            for plugin in plugin_config:
                tmp_item = self.plugin_preference_tpl%(plugin.get('pluginName')
                    , plugin.get('pluginId'),
                     plugin.get('fullName')
                    , plugin.get('preferenceName')
                    , plugin.get('preferenceType')
                    , plugin.get('preferenceValues')
                    , plugin.get('selectedValue'))
                plugin_preference.append(et.fromstring(tmp_item))
        except Exception, e:
            ERROR("policyer.generate_plugin_config:"+str(e))
        DEBUG('Leave policyer.generate_plugin_config')

    def find_tag(self, root, tagname):
        # DEBUG('Enter policyer.find_tag')
        try:
            res = None
            for child in root:
                if res != None:
                    # DEBUG('res not none, break')
                    break
                else:
                    # DEBUG('res is none' + str(res))
                    pass

                if child.tag == tagname:
                    DEBUG('find ' + tagname + str(child))
                    res = child
                    break
                elif not child.getchildren():
                    # DEBUG('father has no child, continue')
                    continue
                else:
                    # DEBUG('father has child, find_tag')
                    res = self.find_tag(child, tagname)
                    # DEBUG('get res is ' + str(res))
            # DEBUG('res is ' + str(res))
            return res

        except Exception, e:
            ERROR("policyer.find_tag:"+str(e))
        # DEBUG('Leave policyer.find_tag')

    #plugin_id_list = [{'PluginId':'18895', 'PluginName':'FreeBSD : phpbb -- multiple vulnerabilities (326c517a-d029-11d9-9aed-000e0c2e438a)', 'Family':'FreeBSD Local Security Checks'}]
    #After combine:
    #<PluginItem>
    #    <PluginId>18895</PluginId>
    #    <PluginName>FreeBSD : phpbb -- multiple vulnerabilities (326c517a-d029-11d9-9aed-000e0c2e438a)</PluginName>
    #    <Family>FreeBSD Local Security Checks</Family>
    #    <Status>enabled</Status>
    #</PluginItem>
    def combine_plugin_by_id(self, plugin_id_list):
        DEBUG('Enter policyer.combine_plugin_by_id')
        try:
            if not plugin_id_list:
                ERROR('plugin_id_list is None, return, pls check')
                return
            individual_plugin_selection = self.root.getchildren()[0].getchildren()[6]
            for plugin in plugin_id_list:
                # DEBUG('PluginId' + str(plugin.get('PluginId')))
                try:
                    tmp_item = self.plugin_item_tpl%(plugin.get('PluginId')
                        , self.escape_plugin_name(plugin.get('PluginName'))
                        , plugin.get('Family'))
                    # DEBUG(tmp_item)
                    individual_plugin_selection.append(et.fromstring(tmp_item))
                except Exception, e:
                    WARN('Invalid params, vul_id:' + str(plugin.get('PluginId')) + str(e))
                    continue
                
        except Exception, e:
            ERROR("policyer.combine_plugin_by_id:"+str(e))
        DEBUG('Leave policyer.combine_plugin_by_id')

    def escape_plugin_name(self, plugin_name):
        try:
            if not plugin_name:
                return 'nvscan_common_plugin'
            else:
                return cgi.escape(plugin_name).replace('"', '&quot;').replace("'", '&apos;')
        except Exception, e:
            ERROR("policyer.escape_plugin_name:"+str(e))

    def write_policy(self, filename):
        DEBUG('Enter policyer.write_policy')
        try:
            if not self.root:
                DEBUG('generate policy failed, tree is empty')
                return
            self.tree.write(filename)
        except Exception, e:
            ERROR("policyer.write_policy:"+str(e))
        DEBUG('Leave policyer.write_policy')
        
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


# Add for test
if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")

    p = policyer()

    common_config = {'policyName':'xxx', 'policyOwner':'xyy'}
    server_config = [{'name':'throttle_scan', 'value':'xxxx'}, {'name':'listen_address', 'value':'1.1.1.1'}]
    plugin_config = [{'pluginId':'15868', 'pluginName':'Hydra (NASL wrappers options)', 'fullName':'Hydra (NASL wrappers options)[entry]:Timeout (in seconds) :', 'preferenceName':'Timeout (in seconds) :', 'preferenceValues':'30', 'preferenceType':'entry', 'selectedValue':''}]
    # p.set_policy_all_preference(common_config, server_config, plugin_config)
    p.generate_common_config(common_config)
    p.generate_service_config(server_config)
    p.generate_plugin_config(plugin_config)

    plugin_id_list = [{'PluginId':'18895', 'PluginName':'FreeBSD : phpbb -- multiple vulnerabilities (326c517a-d029-11d9-9aed-000e0c2e438a)', 'Family':'FreeBSD Local Security Checks'}]
    p.combine_plugin_by_id(plugin_id_list)

    p.write_policy('test.nessus')