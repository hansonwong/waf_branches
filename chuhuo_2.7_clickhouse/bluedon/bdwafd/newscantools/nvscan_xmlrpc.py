#!/usr/bin/env python
#-*-encoding:UTF-8-*-

from random import randint
from urllib import urlencode
from httplib import HTTPSConnection,CannotSendRequest,ImproperConnectionState
import xml.etree.ElementTree
import logging
import xml.etree.cElementTree as et
import StringIO
from encoder import *
import sys
import time
import os

SEQMIN = 10000
SEQMAX = 99999
HOST = '127.0.0.1'
PORT = 8834
LOGIN = 'admin'
PWD = 'admin'

def DEBUG(msg):
    logging.getLogger().info(msg)

def WARN(msg):
    logging.getLogger().warn(msg)

def ERROR(msg):
    logging.getLogger().error("File: nvscan_xmlrpc.py, " + msg)


class nvscan_xmlrpc(object):

    """docstring for nvscan_xmlrpc"""
    def __init__(self):
        try:
            self.set_xmlrpc_protocol()
            self._connect(HOST, PORT)
            self.headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0'}
            self.token = ''
            self.obj = XML2Dict(coding='utf-8')

            if LOGIN != None and PWD != None:
                self.login(LOGIN, PWD)

        except Exception, e:
            ERROR("nvscan_xmlrpc.__init__:"+str(e))

    def _connect(self, host, port):
        try:
            self.connection = HTTPSConnection( host, port )
        except Exception, e:
            ERROR("nvscan_xmlrpc._connect:"+str(e))
        
    def set_xmlrpc_protocol(self):
        try:
            self.xmlrpc_protocol = {'login':'/login'
            ,'logout':'/logout'
            ,'scan_new':'/scan/new'
            ,'scan_list':'/scan/list'
            ,'scan_stop':'/scan/stop'
            ,'report_list':'/report/list'
            ,'report_generate':'/report/format/generate'
            ,'report_hosts':'/report/hosts'
            ,'chapter_generate':'/chapter?report=%s&chapters=compliance;compliance_exec;vuln_by_host;vuln_by_plugin;vuln_hosts_summary&format=%s&token=%s'
            ,'report_delete':'/report/delete'
            ,'scan_pause':'/scan/pause'
            ,'scan_resume':'/scan/resume'
            ,'file_upload':'/file/upload'
            ,'policy_import':'/file/policy/import'
            ,'policy_delete':'/policy/delete'}
        except Exception, e:
            ERROR("nvscan_xmlrpc.set_xmlrpc_protocol:"+str(e))

    #send request to nvscand server
    def _request(self, method, target, params):
        try:
            try:
                if self.connection is None:
                    self._connect(HOST, PORT)
                self.connection.request(method, target, params, self.headers)
            except CannotSendRequest,ImproperConnectionState:
                self._connect(HOST, PORT)
                self.login(LOGIN, PWD )
                #Modify to fix task can not stop bug
                self.connection.request(method, target, params, self.headers)

            #Fix bug, the response is large
            res = self.connection.getresponse()
            # DEBUG(res.getheaders())
            #Modify by xiayuying 2014-02-10 optimize performance
            response = ''
            tmp_list = []
            while True:
                try:
                    # DEBUG('read response')
                    tmp = res.read(1024*64)
                    if not tmp:
                        # DEBUG('tmp is None')
                        break
                    else:
                        # DEBUG('====================tmp=========================')
                        # DEBUG(len(tmp))
                        # response += tmp
                        tmp_list.append(tmp)
                except Exception, e:
                    ERROR('next read  is None')
                    break
            # DEBUG('================================response================')
            # DEBUG(len(response))
            response = ''.join(tmp_list)
            if 'Nessus is initializing...' in response:
                ERROR("Nvscan is initializing... .")
                # time.sleep(60)
                # sys.exit(-1)
            return response
        except Exception, e:
            ERROR("nvscan_xmlrpc._request:"+str(e))
            if 'Connection refused' in str(e) or 'EOF occurred in violation of protocol' in str(e) or 'Connection reset by peer' in str(e):
                ERROR("Nvscan isnt running or exception... .")
                # time.sleep(60)
                # sys.exit(-1)
        

    #parse response form nvscand server
    def _rparse(self, parsed):
        try:
            result = dict()
            # Iterate over each element
            for element in parsed.getchildren():
                # If the element has children, use a dictionary
                children = element.getchildren()
                if len(children) > 0:
                    # We have children for this element
                    if type(result) is list:
                        # Append the next parse, we're apparently in a list()
                        result.append(self._rparse( element ))
                    elif type(result) is dict and result.has_key(element.tag):
                        # Change the dict() to a list() if we have multiple hits
                        tmp = result
                        result = list()
                        # Iterate through the values in the dictionary, adding values only
                        # - This reduces redundancy in parsed output (no outer tags)
                        for val in tmp.itervalues():
                            result.append(val)
                    else:
                        result[element.tag] = dict()
                        result[element.tag] = self._rparse( element )
                else:
                    result[element.tag] = element.text
            # debug(result)
            return result
        except Exception, e:
            ERROR("nvscan_xmlrpc._rparse:"+str(e))

    def parse(self, response):
        try:
            # DEBUG(response)
            return self.obj.parse(response).get('reply')
            # debug(response)
            # return self._rparse(xml.etree.ElementTree.fromstring(response.replace("\n", "")))
        except Exception, e:
            ERROR("nvscan_xmlrpc.parse:"+str(e))
            if 'syntax error' in str(e) or 'no element found' in str(e):
                ERROR('nvscand response invalid')
                # time.sleep(30)
                # sys.exit(-1)

    #log manage
    def login(self, login, password, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.login')
        try:
            params = urlencode({'login':login, 'password':password, 'seq':seq})
            response = self._request("POST", self.xmlrpc_protocol.get('login'), params)
            if 'Nessus is initializing...' in response:
                WARN("Nvscan is initializing... will sleep 60s.")
                # import sys
                # sys.exit(-1)
            parsed = self.parse(response)
            # DEBUG(parsed)
            #if login success save token
            if parsed.get('status') == 'OK':
                DEBUG('nvscan_xmlrpc.login success')
                contents = parsed.get('contents')
                self.token = contents.get('token')
                user = contents.get('user')
                self.isadmin = user.get('admin')
                self.headers['Cookie'] = "token=%s"%(self.token)
            else:
                pass #error log unable to login + parsed
            # debug('login complete:'+self.token+'##'+self.isadmin+'##' + str(self.headers))
        except Exception, e:
            ERROR("nvscan_xmlrpc.login:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.login')

    def logout(self, seq=randint(SEQMIN,SEQMAX)):
        try:
            params = urlencode({'seq':seq})
            response = self._request("POST", self.xmlrpc_protocol['logout'], params)
            parsed = self.parse(response)
            #parse if logout success
        except Exception, e:
            ERROR("nvscan_xmlrpc.logout:"+str(e))

    #policy manage
    def add_policy(self, policy_file_name):
        DEBUG('Enter nvscan_xmlrpc.add_policy')
        try:
            #Step 1.update file
            self.upload_file(policy_file_name)
            #Step 2.upload policy
            policy_id = self.upload_policy(policy_file_name)
            DEBUG('Leave nvscan_xmlrpc.add_policy')
            return policy_id
        except Exception, e:
            ERROR("nvscan_xmlrpc.add_policy:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.add_policy')

    def update_policy(self):
        try:
            params = urlencode({'seq':seq})
            response = self._request("POST", self.xmlrpc_protocol['policy_update'], params)
            parsed = self.parse(response)
            #parse result
        except Exception, e:
            ERROR("nvscan_xmlrpc.update_policy:"+str(e))

    def list_policy(self, seq=randint(SEQMIN,SEQMAX)):
        try:
            params = urlencode({'seq':seq})
            response = self._request("POST", self.xmlrpc_protocol['policy_list'], params)
            parsed = self.parse(response)
            #parse result
        except Exception, e:
            ERROR("nvscan_xmlrpc.list_policy:"+str(e))

    def del_policy(self, policy_id, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.del_policy')
        try:
            DEBUG('policy id is ' + str(policy_id))
            params = urlencode({'seq':seq, 'policy_id':policy_id})
            response = self._request("POST", self.xmlrpc_protocol['policy_delete'], params)
            parsed = self.parse(response)
            #parse result
            if parsed.get('status') == 'OK':
                DEBUG('delete policy success')
        except Exception, e:
            ERROR("nvscan_xmlrpc.del_policy:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.del_policy')

    def upload_policy(self, policy_file_name, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.upload_policy')
        try:
            params = urlencode({'seq':seq, 'file':policy_file_name})
            response = self._request("POST", self.xmlrpc_protocol['policy_import'], params)
            # if '<status>OK</status>' in response:
            #     DEBUG('import policy success')
            #     return self.safe_parse(response, policy_file_name)
            # else:
            #     WARN('import policy failed')
            #     return -1
            parsed = self.parse(response)
            # DEBUG(parsed)
            #parse result
            # DEBUG(parsed.has_key('status'))
            if parsed.get('status') == 'OK':
                DEBUG('import policy success')
                contents = parsed.get('contents')
                # DEBUG(contents)
                if contents:
                    policies = contents.get('policies')
                    if policies:
                        if type(policies) is dict:
                            policy = policies.get('policy')
                            if type(policy) is list:
                                for item in policy:
                                    if item.get('policyName').strip() == policy_file_name.strip():
                                        DEBUG('nvscan policy id is ' + item.get('policyID'))
                                        return int(item.get('policyID'))
                            elif type(policy) is dict:
                                if policy.get('policyName').strip() == policy_file_name.strip():
                                    DEBUG('nvscan policy id is ' + policy.get('policyID'))
                                    return int(policy.get('policyID'))
                        else:
                            for policy in policies:
                                # DEBUG(policy)
                                # DEBUG(len(policy))
                                # DEBUG(policy.get('policyName'))
                                # DEBUG(policy_file_name)
                                if policy.get('policyName').strip() == policy_file_name.strip():
                                    DEBUG('nvscan policy id is ' + policy.get('policyID'))
                                    return int(policy.get('policyID'))
        except Exception, e:
            ERROR("nvscan_xmlrpc.upload_policy:"+str(e))
            return -1
        DEBUG('Leave nvscan_xmlrpc.upload_policy')

    def upload_file(self, policy_file_name):
        DEBUG('Enter nvscan_xmlrpc.upload_file')
        try:
            #Content-Type:multipart/form-data; boundary=----WebKitFormBoundaryHYLJz6NWJEH94dLf
            tmp = self.headers['Content-type']
            DEBUG(tmp)
            self.headers['Content-type'] = 'multipart/form-data; boundary=---------------------------27285279223182'
            # params = urlencode({'seq':seq})
            params = '''-----------------------------27285279223182\r\nContent-Disposition: form-data; name="Filedata"; filename="%s"\r\nContent-Type: application/octet-stream\r\n\r\n%s\r\n-----------------------------27285279223182--\r\n''' % (policy_file_name, open('/tmp/'+policy_file_name, 'rb').read())
            # DEBUG(str(self.headers))
            # DEBUG(params)
            response = self._request("POST", self.xmlrpc_protocol['file_upload'], params)
            # DEBUG(response)
            parsed = self.parse(response)
            #parse result
            if parsed.get('status') == 'OK':
                DEBUG('upload_file success')
            self.headers['Content-type'] = tmp
        except Exception, e:
            ERROR("nvscan_xmlrpc.upload_file:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.upload_file')

    #scan manage
    def add_scan(self, scan_name, target_list, policy_id, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.add_scan')
        try:
            # scan_uuid = ''#c6f9829b-93fe-48b1-3a05-f4a575c472774c38a128fdde2ca5'
            DEBUG(target_list)
            target = ''
            while not target_list.empty():
                target += target_list.get().strip() + '\n'
            target = target[:-1]
            params = urlencode({'scan_name':scan_name,'target':target,'policy_id':policy_id,'seq':seq})
            DEBUG(params)
            response = self._request("POST", self.xmlrpc_protocol['scan_new'], params)
            parsed = self.parse(response)
            DEBUG(parsed)
            if parsed.get('status') == 'OK':
                contents = parsed.get('contents')
                if contents:
                    scan = contents.get('scan')
                    if scan:
                        return scan.get('uuid')
            #parse result get scan uuid
            return None
        except Exception, e:
            ERROR("nvscan_xmlrpc.add_scan:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.add_scan')

    def stop_scan(self, uuid, seq=randint(SEQMIN,SEQMAX)):
        try:
            params = urlencode({'seq':seq, 'scan_uuid':uuid})
            response = self._request("POST", self.xmlrpc_protocol['scan_stop'], params)
            parsed = self.parse(response)
            #parse result
        except Exception, e:
            ERROR("nvscan_xmlrpc.stop_scan:"+str(e))

    def pause_scan(self, uuid, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.pause_scan')
        try:
            params = urlencode({'seq':seq, 'scan_uuid':uuid})
            response = self._request("POST", self.xmlrpc_protocol['scan_pause'], params)
            parsed = self.parse(response)
            #parse result
            if parsed.get('status') == 'OK':
                DEBUG('pause scan ' + uuid + ' success')

        except Exception, e:
            ERROR("nvscan_xmlrpc.pause_scan:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.pause_scan')

    def resume_scan(self, uuid, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.resume_scan')
        try:
            params = urlencode({'seq':seq, 'scan_uuid':uuid})
            response = self._request("POST", self.xmlrpc_protocol['scan_resume'], params)
            parsed = self.parse(response)
            #parse result
            if parsed.get('status') ==  'OK':
                DEBUG('resume scan ' + uuid + ' success')
        except Exception, e:
            ERROR("nvscan_xmlrpc.resume_scan:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.resume_scan')

    def clear_scan(self, task_id):
        DEBUG('Enter nvscan_xmlrpc.clear_scan')
        try:
            res = self.list_all_report()
            for item in res:
                if item.get('readableName').strip == 'nvscan'+str(task_id):
                    DEBUG(item.get('readableName')+':'+'nvscan'+str(task_id) +':'+item.get('name'))
                    self.stop_scan(item.get('name'))
                    time.sleep(5)
                    self.del_report(item.get('name'))
        except Exception, e:
            ERROR("nvscan_xmlrpc.clear_scan:"+str(e) + ', task_id:' + str(task_id))
        DEBUG('Leave nvscan_xmlrpc.clear_scan')

    def list_scan(self, uuid, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.list_scan')
        try:
            params = urlencode({'seq':seq})
            response = self._request("POST", self.xmlrpc_protocol['scan_list'], params)
            parsed = self.parse(response)
            DEBUG(parsed)
            #parse result
            return 'running'
        except Exception, e:
            ERROR("nvscan_xmlrpc.list_scan:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.list_scan')

    def get_scan_progress(self, uuid, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.get_scan_progress')
        try:
            params = urlencode({'seq':seq, 'report':uuid})
            response = self._request("POST", self.xmlrpc_protocol['report_hosts'], params)
            parsed = self.parse(response)
            res = []
            if type(parsed) is dict and parsed.get('status') == 'OK':
                contents = parsed.get('contents')
                if type(contents) is dict:
                    host_list = contents.get('hostList')
                    if type(host_list) is dict:
                        host = host_list.get('host')
                        if type(host) is dict:
                            scanProgressCurrent = host.get('scanProgressCurrent')
                            scanProgressTotal = host.get('scanProgressTotal')
                            numChecksConsidered = host.get('numChecksConsidered')
                            totalChecksConsidered = host.get('totalChecksConsidered')
                            hostname = host.get('hostname')
                            res.append({hostname:self.calc_scan_progress(scanProgressTotal, totalChecksConsidered, scanProgressCurrent, numChecksConsidered)})
                        elif type(host) is list:
                            for item in host:
                                scanProgressCurrent = item.get('scanProgressCurrent')
                                scanProgressTotal = item.get('scanProgressTotal')
                                numChecksConsidered = item.get('numChecksConsidered')
                                totalChecksConsidered = item.get('totalChecksConsidered')
                                hostname = item.get('hostname')
                                res.append({hostname:self.calc_scan_progress(scanProgressTotal, totalChecksConsidered, scanProgressCurrent, numChecksConsidered)})
            return res
        except Exception, e:
            ERROR("nvscan_xmlrpc.get_scan_progress:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.get_scan_progress')

    def calc_scan_progress(self, scanProgressTotal, totalChecksConsidered, scanProgressCurrent, numChecksConsidered):
        try:
            return ((int(scanProgressCurrent)+int(numChecksConsidered))*100)/(int(scanProgressTotal)+int(totalChecksConsidered))
        except Exception, e:
            ERROR("nvscan_xmlrpc.calc_scan_progress:"+str(e))

    #report manage
    def list_report(self, uuid, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.list_report')
        try:
            if not uuid:
                return None
            DEBUG(uuid)
            status = ''
            params = urlencode({'seq':seq})
            response = self._request("POST", self.xmlrpc_protocol['report_list'], params)
            # DEBUG(response)
            parsed = self.parse(response)
            DEBUG(parsed)
            if type(parsed) is dict:
                if parsed.get('status') == 'OK':
                    contents = parsed.get('contents')
                    if contents:
                        reports = contents.get('reports')
                        if type(reports) is dict:
                            item = reports.get('report')
                            if type(item) is list:
                                for report in item:
                                    if uuid in str(report):
                                        return report.get('status')
                            elif type(item) is dict:
                                return item.get('status')
                        else:
                            for item in reports:
                                DEBUG(item)
                                if uuid in str(item):
                                    DEBUG(uuid)
                                    return item.get('status')
            DEBUG('status not find, return None')
            return 'running'

            #parse result
        except Exception, e:
            ERROR("nvscan_xmlrpc.list_report:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.list_report')

    def list_all_report(self, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.list_all_report')
        try:
            status = ''
            params = urlencode({'seq':seq})
            response = self._request("POST", self.xmlrpc_protocol['report_list'], params)
            # DEBUG(response)
            parsed = self.parse(response)
            DEBUG(parsed)
            if type(parsed) is dict:
                if parsed.get('status') == 'OK':
                    contents = parsed.get('contents')
                    if contents:
                        reports = contents.get('reports')
                        if type(reports) is dict:
                            item = reports.get('report')
                            if type(item) is list:
                                return item
                            elif type(item) is dict:
                                return [item]
            DEBUG('status not find, return None')
            return None

            #parse result
        except Exception, e:
            ERROR("nvscan_xmlrpc.list_all_report:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.list_all_report')

    def del_report(self, uuid, seq=randint(SEQMIN,SEQMAX)):
        DEBUG('Enter nvscan_xmlrpc.del_report')
        try:
            params = urlencode({'seq':seq,'report':uuid})
            response = self._request("POST", self.xmlrpc_protocol['report_delete'], params)
            # parsed = self.parse(response)
            #parse result
            try:
                #del /opt/nvscan/var/nvscan/users/admin/reports/uuid.nvscan or uuid.nvscan.v1
                os.remove('/opt/nvscan/var/nvscan/users/admin/reports/%s.nvscan'%(uuid))
                os.remove('/opt/nvscan/var/nvscan/users/admin/reports/%s.nvscan.v1'%(uuid))
            except Exception, e:
                WARN("It's ok, report file may not exist.:" + str(e))
            
        except Exception, e:
            ERROR("nvscan_xmlrpc.del_report:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.del_report')

    def status_report(self, report_name):
        try:
            status = ''#= self.list_report(uuid)
            return status
        except Exception, e:
            ERROR("nvscan_xmlrpc.status_report:"+str(e))

    def gen_report(self,uuid, format):
        DEBUG('Enter nvscan_xmlrpc.gen_report')
        try:
            #report=2894958a-9446-d995-45c5-86567bf47f92458afbde82525adb
            #&format=xslt.csv.xsl
            #&json=1
            #&token=3f28b52d4c3c77775b4256ce68a49aca8a5357fbd5ad07e3
            params = urlencode({'report':uuid,'format':'xslt.csv.xsl', 'token':self.token})
            response = self._request("POST", self.xmlrpc_protocol.get('report_generate'), params)
            print response
            parsed = self.parse(response)
            DEBUG(parsed)
        except Exception, e:
            ERROR("nvscan_xmlrpc.gen_report:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.gen_report')

    def down_report(self, report_name):
        try:
            params = urlencode({'seq':seq})
            response = self._request("POST", self.xmlrpc_protocol['file_report_download'], params)
            parsed = self.parse(response)
            #parse result
        except Exception, e:
            ERROR("nvscan_xmlrpc.down_report:"+str(e))

    def gen_chapter(self, uuid, format):
        DEBUG('Enter nvscan_xmlrpc.gen_chapter')
        try:
            #chapter?report=%s&chapters=compliance;compliance_exec;vuln_by_host;vuln_by_plugin;vuln_hosts_summary&format=%s&token=%s
            response = self._request("GET", self.xmlrpc_protocol.get('chapter_generate')%(uuid, format, self.token), '')
            if not response:
                return ''

            report_url = response[response.find('5;url=')+6:response.find('.html')+5]
            # self.down_file(report_url)
            DEBUG('Leave nvscan_xmlrpc.gen_chapter')
            return report_url
        except Exception, e:
            ERROR("nvscan_xmlrpc.gen_chapter:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.gen_chapter')

    def down_file(self, report_url):
        DEBUG('Enter nvscan_xmlrpc.down_file')
        try:
            # DEBUG('report_url:'+report_url)
            if not report_url:
                return ''
            response = self._request("GET", report_url, '')
            DEBUG('Leave nvscan_xmlrpc.down_file')
            try:
                #After download, remove tmp report
                if report_url.find('?fileName='):
                    os.remove('/opt/nvscan/var/nvscan/users/admin/files/%s.xslt-results'%(report_url[report_url.find('?fileName=')+10:].strip()))
            except Exception, e:
                WARN("Remove tmp report file failed, it's ok, will delete by restart nvscand at 5:05. " + str(e))
            
            return response
            # DEBUG(response)
        except Exception, e:
            ERROR("nvscan_xmlrpc.down_file:"+str(e))
        DEBUG('Leave nvscan_xmlrpc.down_file')


