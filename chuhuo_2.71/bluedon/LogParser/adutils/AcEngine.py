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
from adutils.make_rules import make_rules_from_file
# from adutils.LogNotify import LogNotify
from adutils.file_monitor import add_file_monitor, add_table_monitor, FsMonitor
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR
from adutils.audit_logger import rLog_dbg
from adutils.url_filter_audit import make_url_filter_conf
from adutils.UrlFilterEngine import UrlFilterEngine
from ip_user_utils import get_ip_mapping, parser_user_ip_map
from proc_user_login import UserLoginHandler, reload_online_user
from adutils.mail_utils.log_mail_config import send_email_msg, get_mail_switch_conf


g_SM_IP = 1
g_SM_SUBJECT = 2
g_SM_ATTACH = 3
g_SM_CONTENT = 4
g_SM_ATTACH_CONTENT = 5
g_SM_LOCAL_IP = 6
g_SM_LOCAL_SUBJECT = 7
g_SM_LOCAL_CONTENT = 8
g_SM_LOCAL_ATTACH = 9
g_SM_LOCAL_ATTACH_CONTENT = 10
g_local_match_dir = "/data/conf/bd_local_rulefiles"
g_superior_match_dir = "/data/conf/bd_higher_rulefiles"

RULE_LOG = lambda x : rLog_dbg('audit_statis_rule', x)

# register TERM signal action, when get TERM signal raise a runtimeerror
def sighandler(var1, var2):
    raise RuntimeError('Get Exit Signal')


class AcType(object):
    def __init__(self):
        super(AcType, self).__init__()

        # predefine all log type for AcEngine
        self.ac_email = None
        self.ac_bbs = None
        self.ac_blog = None
        self.ac_netstore = None
        self.ac_search = None
        self.ac_shopping = None
        self.ac_video = None
        self.ac_webmail = None
        self.ac_weibo = None
        self.ac_http_url = None
        self.ac_ftp = None
        self.ac_sql = None
        self.ac_p2p = None
        self.ac_proxy = None
        self.ac_game = None
        self.ac_trojan = None
        self.ac_telnet = None
        self.ac_qq = None

        self.path_of_counter = '/usr/local/bluedon/log/audit_log_counter.json'
        self.today = time.localtime().tm_mday
        self.counter_name = lambda x: '_'.join(['icount', x])
        self.new_count = lambda x="": dict(yesterday=0, today=0,
                                           total=0, type=x, detail=list())

        self.detail_counter_name = lambda x: '_'.join(['detail', x])
        self.new_detail_count = lambda x="": dict(yesterday=0, today=0,
                                                  total=0, type=x)
        self.icount_audit = self.new_count()
        self.icount_audit_ove = self.new_count()
        self.icount_app_filter = self.new_count()
        self.icount_url_filter = self.new_count()
        self.icount_alert = self.new_count()

        self.init_counter()

        # init all dict object, use a dict for every match type
        for attr in dir(self):
            if attr.startswith('ac_'):
                setattr(self, attr, [{ idx:{} for idx in range(AcEngine.TYPE_COUNT) }
                                     for _ in range(2)])
                # print getattr(self, attr)

    def init_counter(self):
        # try load old data from disk
        try:
            with open(self.path_of_counter, 'r') as fp:
                raw_data = fp.readlines()
            pre = json.loads(''.join(raw_data))

            self.today = pre['date']
            pre_data = pre['log']

            for rec in pre_data:
                attr = rec['type']
                # init static counter
                if hasattr(self, attr):
                    getattr(self, attr).update(rec)
                else:
                    # init dynamic counter
                    setattr(self, attr, rec)

                for detail in rec['detail']:
                    attr = detail['type']
                    # init static counter
                    if hasattr(self, attr):
                        getattr(self, attr).update(detail)
                    else:
                        # init dynamic counter
                        setattr(self, attr, detail)

        except (IOError, KeyError, ValueError) as e:
            for attr in dir(self):
                if attr.startswith('icount_'):
                    getattr(self, attr)["type"] = attr

        self.save_counter()

    def save_counter(self):
        try:

            self.update_counter()
            js = json.dumps({ "log": self.dcount, "date": self.today })
            with open(self.path_of_counter, 'w') as fp:
                fp.write(js)
        except:
            pass

    def add_counter(self, log_type):
        log_type = self.detail_counter_name(log_type)
        if not hasattr(self, log_type):
            setattr(self, log_type, self.new_detail_count(log_type))

            if 'filter' in log_type:
                if 'url' in log_type:
                    self.icount_url_filter['detail'].append(getattr(self, log_type))
                elif 'app' in log_type:
                    self.icount_app_filter['detail'].append(getattr(self, log_type))
                    pass
            elif 'alert' in log_type:
                self.icount_alert['detail'].append(getattr(self, log_type))
            else:
                if 'ove' in log_type:
                    self.icount_audit_ove['detail'].append(getattr(self, log_type))
                else:
                    self.icount_audit['detail'].append(getattr(self, log_type))

    def update_counter(self):
        self.dcount = [ getattr(self, attr) \
                        for attr in dir(self) if attr.startswith('icount_') ]

        real_today = time.localtime().tm_mday
        if self.today != real_today:
            self.today = real_today
            for i in self.dcount:
                i['yesterday'] = i['today']
                i['today'] = 0

                for j in i['detail']:
                    j['yesterday'] = j['today']
                    j['today'] = 0

        return self.dcount

    def inc_counter(self, typ):
        pass
        if 'filter' in typ:
            if 'url' in typ:
                self.inc_urlfilter()
            elif 'app' in typ:
                self.inc_appfilter()
                pass
        elif 'alert' in typ:
            self.inc_alert()
        else:
            if 'ove' in typ:
                self.inc_audit_ove()
                pass
            self.inc_audit()

        getattr(self, self.detail_counter_name(typ))['today'] += 1
        getattr(self, self.detail_counter_name(typ))['total'] += 1

    def inc_audit(self):
        self.icount_audit['today'] += 1
        self.icount_audit['total'] += 1

    def inc_audit_ove(self):
        self.icount_audit_ove['today'] += 1
        self.icount_audit_ove['total'] += 1

    def inc_alert(self):
        self.icount_alert['today'] += 1
        self.icount_alert['total'] += 1

    def inc_appfilter(self):
        self.icount_app_filter['today'] += 1
        self.icount_app_filter['total'] += 1

    def inc_urlfilter(self):
        self.icount_url_filter['today'] += 1
        self.icount_url_filter['total'] += 1

        pass

    def printout(self):
        for attr in dir(self):
            if attr.startswith('ac_'):
                print getattr(self, attr)

    @classmethod
    def load_ac_into_file(cls, ac):
        pass


class AcEngine(threading.Thread):

    #匹配类型
    TYPE_TITLE = 0
    TYPE_CONTENT = 1
    TYPE_FILE_NAME = 2
    TYPE_FILE_CONTENT = 3
    TYPE_CONTENT_INFILE = 4
    TYPE_COUNT = 5

    #匹配策略类型
    TYPE_POLICY_LOCAL = 0
    TYPE_POLICY_NATION = 1
    TYPE_POLICY_COUNT = 2

    def __init__(self):
        threading.Thread.__init__(self)

        # 操作方法参考http://www.tuicool.com/articles/vYNNva3
        self.ac_title = esm.Index()
        self.ac_title.fix()
        self.ac_content = esm.Index()
        self.ac_content.fix()
        self.ac_filename = esm.Index()
        self.ac_filename.fix()
        self.ac_filecontent = esm.Index()
        self.ac_filecontent.fix()
        self.ac_title_dict = {}
        self.ac_content_dict = {}
        self.ac_filename_dict = {}
        self.ac_filecontent_dict = {}
        self.n_title = esm.Index()
        self.n_title.fix()
        self.n_content = esm.Index()
        self.n_content.fix()
        self.n_filename = esm.Index()
        self.n_filename.fix()
        self.n_filecontent = esm.Index()
        self.n_filecontent.fix()
        self.n_title_dict = {}
        self.n_content_dict = {}
        self.n_filename_dict = {}
        self.n_filecontent_dict = {}
        self.re_s = re.compile('[\s|\xE3\x80\x80|,\.;\:"!\(\)]')
        self.re_space = re.compile("^\s*$")
        self.actype = AcType()
        self.mapping = None
        self.ac_caller = None
        self.event = threading.Event()
        self.setName('acengine')

        # record of rule id and ip
        self.ruleid_ip_mapping = defaultdict(set)
        self.gip_map = defaultdict(set)
        self.uip_map = defaultdict(set)
        self.user_handler = UserLoginHandler(self.online_hook, self.offline_hook)

        # IPS URL Filter Engine
        self.ips_urlfilter = UrlFilterEngine()

        self.update_mapping()

        # load statistics files
        for dir_path, dir_name, file_name in os.walk(g_local_match_dir):
            for f in file_name:
                self.ac_reload(os.path.join(dir_path, f))

        # load superior rule files
        for dir_path, dir_name, file_name in os.walk(g_superior_match_dir):
            for f in file_name:
                self.ac_reload(os.path.join(dir_path, f))

        self.counters = []

        for i in range(0, self.TYPE_POLICY_COUNT):
            cs = []
            self.counters.append(cs)
            for j in range(0, self.TYPE_COUNT):
                cs.append({})

        # alert mail setting
        self.enable_alert = 0
        self.update_alert_mail_conf()


        #print 'content', self.get_ac_content()
        #print str(self.ac_title)
        #print str(self.ac_title_dict)
        #patter = self.ac_search(self.TYPE_POLICY_LOCAL, self.TYPE_TITLE, "C programming")
        #print str(patter)



        self.lock = threading.Lock()
        reload_online_user(self.online_hook)

        # self.setDaemon(True)
        # self.start()

    def online_hook(self, user_info):
        # call when a new user login
        print '='*55
        print user_info
        # add user ip to two dict, save the relationship of uid->ip and gid->ip,
        # so we can find ip by user's uid or gid after
        self.uip_map[user_info.uid].add(user_info.IP)
        self.gip_map[user_info.gid].add(user_info.IP)
        print self.uip_map
        print self.gip_map
        # update rule_ip mapping in ac_*_dict, add new login ip to current rule
        self.update_ac_dict(user_info)
        # call ips service
        if len(self.ruleid_ip_mapping[user_info.IP]) > 0:
            _ids = self.ruleid_ip_mapping[user_info.IP]
            # offline info is sent by UrlFilterEngine
            # self.ac_client.invoke(self.ips_client, "IpOnline",
            #                       [{"Ip": user_info.IP, "Ids": list(_ids)}], async_=True)
        print '#'*55
        pass

    def offline_hook(self, user_info):
        # call when a user logout
        print '='*55
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
        # update rule_ip mapping in ac_*_dict, remove logout ip from rule
        self.update_ac_dict(user_info)
        # offline info is sent by UrlFilterEngine
        # self.ac_client.invoke(self.ips_client, "IpOffline",
        #                       [{"Ip": user_info.IP}], async_=True)
        print '#'*55
        pass

    def update_ac_dict(self, user_info):
        # update ac local/superior rules-ip mapping
        ac_dicts = [self.ac_title_dict, self.ac_content_dict,
                    self.ac_filecontent_dict,self.ac_filename_dict,
                    self.n_title_dict, self.n_content_dict,
                    self.n_filecontent_dict, self.n_filename_dict]
        for ac_dict in ac_dicts:
            # print 'BEFORE'
            # print ac_dict
            # do for every rule
            for key, rule in ac_dict.items():
                # if find user id in this rule, add/remove ip, otherwise do
                # nothing to this rule
                if user_info.uid in rule['uid'] or user_info.gid in rule['gid']:
                    if user_info.isOnline:
                        # if user login
                        # print 'Add %s to Rule: %s' % (user_info, rule)
                        rule['ips'].add(user_info.IP)
                        # update ruleid_ip_mapping
                        self.ruleid_ip_mapping[user_info.IP] |= rule['id']
                    else:
                        # else user logout
                        try:
                            # print 'Remove %s from Rule: %s' % (user_info, rule)
                            rule['ips'].remove(user_info.IP)
                            # remove ruleid for logout ip from ruleid_ip_mapping
                            if user_info.IP in self.ruleid_ip_mapping:
                                self.ruleid_ip_mapping.pop(user_info.IP)
                        except:
                            print 'no rule for %s' % str(user_info)

                print 'update in update_ac_dict[%s]' % key
                print rule


            # print 'AFTER'
            # print ac_dict
            # print 'ruleid_ip_mapping'
            # print self.ruleid_ip_mapping


    def get_online_user(self, *args, **kwargs):
        online_users = [{'Ip': ip, 'Ids': list(ids)}
                        for ip, ids in self.ruleid_ip_mapping.items()
                        if len(ids) > 0]

        # self.ac_client.invoke(self.ips_client, "IpOnline", online_users, async_=True)
        return None


    def update_alert_mail_conf(self, *args, **kwargs):
        self.enable_alert, _ = get_mail_switch_conf()


    def start_reload(self):
        # signal.signal(signal.SIGTERM,sighandler)
        # nofity = LogNotify([
        #     '/data/conf/bd_local_rulefiles',
        #     '/usr/local/bluedon/conf/online_users'
        # ], self.ac_reload_handler, LogNotify.WAIT_NOTIFY)

        print 'start_reload'
        fs_monitor = FsMonitor()
        # add_file_monitor('/data/conf/bd_local_rulefiles', self.ac_reload_handler)
        add_file_monitor('/data/conf/bd_local_rulefiles/last_version', self.ac_reload_handler)
        add_file_monitor('/data/conf/bd_higher_rulefiles/last_version', self.ac_reload_handler)
        add_table_monitor('m_tbconfig', self.update_alert_mail_conf)
        try:
            # nofity.start()
            fs_monitor.start()
            self.user_handler.start()
            self.ips_urlfilter.start()
            while 1:
                if self.event.isSet():
                    # raise RuntimeError
                    break
                time.sleep(2)
            ADLOG_INFO('[AcEngine] Exiting...')
        except KeyboardInterrupt as e:
            ADLOG_INFO('[AcEngine] Exiting...')
        except Exception as e:
            ADLOG_ERR('[AcEngine] Exiting...%s' % e)
        finally:
            # nofity.stop()
            self.user_handler.stop()
            # self.ac_client.stop()
            self.ips_urlfilter.stop()
            fs_monitor.stop()
        ADLOG_INFO('[AcEngine] Exited...')


    def stop_reload(self):
        self.event.set()
        pass

    def update_mapping(self):
        # 创建映射表
        self.mapping = [
            [
                [self.get_ac_title, self.searchTxt, self.ac_title_dict],
                [self.get_ac_content, self.searchTxt, self.ac_content_dict],
                [self.get_ac_filename, self.searchTxt, self.ac_filename_dict],
                [self.get_ac_filecontent, self.searchFile, self.ac_filecontent_dict],
                [self.get_ac_content, self.searchFile, self.ac_content_dict]        #正文内容保存在文件中
            ],
            [
                [self.get_n_title, self.searchTxt, self.n_title_dict],
                [self.get_n_content, self.searchTxt, self.n_content_dict],
                [self.get_n_filename, self.searchTxt, self.n_filename_dict],
                [self.get_n_filecontent, self.searchFile, self.n_filecontent_dict],
                [self.get_n_content, self.searchFile, self.n_content_dict]
            ]
        ]

    def run(self):
        pass

    def acquire(self):
        self.lock.acquire()

    def unlock(self):
        self.lock.release()

    def run_old(self):

        while True:
            time.sleep(60)
            self.acquire()
            #print self, self.counters

            dit = {}
            for i in range(0, self.TYPE_POLICY_COUNT):
                dit2 = None
                if i == self.TYPE_POLICY_LOCAL:
                    #print 'local'
                    dit2 = dit['local'] = {}
                elif i == self.TYPE_POLICY_NATION:
                    #print 'nation'
                    dit2 = dit['nation'] = {}

                for j in range(0, self.TYPE_COUNT):

                    if j == self.TYPE_TITLE:
                        #print 'title'
                        dit2['title'] = self.counters[i][j]

                    elif j == self.TYPE_CONTENT:
                        #print 'msg'
                        dit2['msg'] = self.counters[i][j]
                    elif j == self.TYPE_FILE_NAME:
                        #print 'filename'
                        dit2['filename'] = self.counters[i][j]
                    elif j == self.TYPE_FILE_CONTENT:
                        #print 'filecontent'
                        dit2['filecontent'] = self.counters[i][j]
                    self.counters[i][j] = {}
            self.unlock();
            jstr = json.dumps(dit)
            print jstr
            try:
                os.mkdir("/var/log/suricata/matchcounter/")
            except:
                pass
            fp = None
            try:
                fp = open("/var/log/suricata/matchcounter/matchinfo.%d.json" % (time.time()), "w")
                if fp is not None:
                    fp.write(jstr)
            except:
                pass
            finally:
                if fp is not None: fp.close()



    def ac_reload_handler(self, filename):
        print 'has update the policy!'
        if hasattr(filename, 'pathname'):
            print filename.pathname
            filename = filename.pathname

        ADLOG_DEBUG('ac_reload_handler %s' % filename)
        # load statistics files
        if filename.find(g_local_match_dir) != -1:        #本地
            for dir_path, dir_name, file_name in os.walk(g_local_match_dir):
                for f in file_name:
                    self.ac_reload(os.path.join(dir_path, f))

        # load superior rule files
        elif filename.find(g_superior_match_dir) != -1:       #上级策略
            for dir_path, dir_name, file_name in os.walk(g_superior_match_dir):
                for f in file_name:
                    self.ac_reload(os.path.join(dir_path, f))

    def get_ac_title(self):
        return self.ac_title
    def get_ac_content(self):
        return self.ac_content
    def get_ac_filename(self):
        return self.ac_filename
    def get_ac_filecontent(self):
        return self.ac_filecontent
    def get_n_title(self):
        return self.n_title
    def get_n_content(self):
        return self.n_content
    def get_n_filename(self):
        return self.n_filename
    def get_n_filecontent(self):
        return self.n_filecontent

    def ac_reload(self, filename):                #重新加载ac匹配关键字
        print 'ac_reload', filename
        # update ip conf file for ips(ip/ip_group)
        # make_url_filter_conf()

        if os.path.isfile(filename) == False:
            return

        if filename.find('last_version') != -1:
            return

        if filename.find('bd_applyfilter_') != -1:
            print 'make_rules'
            # update rules
            make_rules_from_file(filename)
            return

        fp = open(filename, "r")
        alllines = None
        try:
            alllines = fp.readlines()
        except:
            pass
        finally:
            fp.close()

        #空文件
        if alllines == None or len(alllines) == 0:
            RULE_LOG('rule file[%s] is null' % filename)
            # return

        # get ip from online_users
        gip_map, uip_map = parser_user_ip_map()

        #追加策略关键字
        g_tmp_pattern = esm.Index()
        # statistics keywords list
        g_tmp_dict = {}
        for line in alllines:
            line = line.strip("\r\n")

            result = line.split("#")
            # if len(result) != 4:
            if len(result) < 4:
                continue

            if self.re_space.match(result[0]) is None:
                print 'add key word----------------------------'
                print result[0]
                g_tmp_pattern.enter(result[0])

            if g_tmp_dict.get(result[0], None) is None:
                g_tmp_dict[result[0]] = defaultdict(set)

            # get rule id(database record id of rule)
            g_tmp_dict[result[0]]['id'] |= set(result[-1])
            # get all ips of this rule
            ip_mapping = get_ip_mapping(int(result[-4]), int(result[-3]),
                                        self.gip_map, self.uip_map)
            g_tmp_dict[result[0]]['ips'] |= ip_mapping

            if int(result[-4]) == 1: # user
                g_tmp_dict[result[0]]['uid'] |= set([int(result[-3])])
                # update ruleid_ip_mapping when rule file is updated
                for ip in ip_mapping:
                    self.ruleid_ip_mapping[ip] |= set(result[-1]) # rule id

            elif int(result[-4]) == 2: # user group
                g_tmp_dict[result[0]]['gid'] |= set([int(result[-3])])
                # update ruleid_ip_mapping when rule file is updated
                for ip in ip_mapping:
                    self.ruleid_ip_mapping[ip] |= set(result[-1]) # rule id
            # do nothing if rule is for ip/ip_group

        g_tmp_pattern.fix()
        print filename
        print g_tmp_dict
        RULE_LOG(g_tmp_dict)
        print '-'*40
        print '+'*40

        #区分本地策略和上级策略
        if filename.find(g_local_match_dir) != -1:        #本地
            if filename.find("bd_title_") != -1:
                self.ac_title = g_tmp_pattern
                self.ac_title_dict = g_tmp_dict
            elif filename.find("bd_content_") != -1:
                self.ac_content = g_tmp_pattern
                self.ac_content_dict = g_tmp_dict
            elif filename.find("bd_filecontent_") != -1:
                self.ac_filecontent = g_tmp_pattern
                self.ac_filecontent_dict = g_tmp_dict
            elif filename.find("bd_filename_") != -1:
                self.ac_filename = g_tmp_pattern
                self.ac_filename_dict = g_tmp_dict

        elif filename.find(g_superior_match_dir) != -1:       #上级策略
            if filename.find("bd_title_") != -1:
                self.n_title = g_tmp_pattern
                self.n_title_dict = g_tmp_dict
            elif filename.find("bd_content_") != -1:
                self.n_content = g_tmp_pattern
                self.n_content_dict = g_tmp_dict
            elif filename.find("bd_filename_") != -1:
                self.n_filename = g_tmp_pattern
                self.n_filename_dict = g_tmp_dict
            elif filename.find("bd_filecontent_") != -1:
                self.n_filecontent = g_tmp_pattern
                self.n_filecontent_dict = g_tmp_dict

        self.update_mapping()
        # notify ips to update user_ruleid
        self.get_online_user()
        # self.notify_caller(self.ac_caller)


    def searchFileInfos(self, log, policy, mtype):
        for fileinfo in log.fileinfos:
            if mtype == self.TYPE_FILE_NAME:
                fileinfo.filename_match_patterns = self.ac_search(log, policy, mtype, fileinfo.filename)
            elif mtype == self.TYPE_FILE_CONTENT:
                fileinfo.txtfile_match_patterns = self.ac_search(log, policy, mtype, fileinfo.txtfilepath)


    def searchFile(self, log, pattern, filepath):                # 对txt文件中的内容进行匹配

        #print 'searchFile', filepath
        if filepath == None:
            return []
        if os.path.isfile(filepath) == False:
            return []
        txt = None
        f = open(filepath)
        if f != None:
            try:
                txt = f.read()                    #read the whole file content, 文件会不会太大呀!?
            except:
                f.close()
                return []
            finally:
                f.close()
            return self.searchTxt(log, pattern, txt)
        return []


    def searchTxt(self, log, pattern, txt):            #AC核心函数，以[]格式返回匹配的文本
        ret = []
        if txt == None:
            return ret
        # txt_not_s =re.sub(self.re_s, '', txt)
        txt_not_s = txt
        #txt_not_s = re.sub(self.re_s2, '', txt_not_s)
        try:
            ms = pattern.query(txt_not_s)
        except Exception as e:
            ADLOG_ERR('searchTxt ERROR %s' % e)
        for (start, end), p in ms:
            #print start, '(' + p + ')', StringUtil.get_content(txt_not_s, start, 30)
            ret.append(p)
        return ret


    def ac_search(self, log, policy, mtype, txt, ip=None, countlist=None):        #提供外部使用的统一匹配接口,以[]形式返回匹配的文本;
        #print 'do search:', txt
        # self.mapping[policy][mtype], 'log' is not use here
        info = self.mapping[0][mtype]
        ret_local = info[1](log, info[0](), txt)
        info = self.mapping[1][mtype]
        ret_superior = info[1](log, info[0](), txt)
        level = 0
        check_flag = False
        ret = ret_local + ret_superior

        if countlist is None or ip is None:
            # log here
            print 'ac_search: countlist or IP is None'
        try:

            # res_list = countlist[policy][mtype]
            # print res_list

            if len(ret) > 0:
                # check if ip in strategy
                strategy_ip = info[2]
                for kw in ret:
                    strategy = strategy_ip.get(kw, {})
                    for ips in strategy.get('ips', {}):
                        if ip in ips:
                            check_flag = True

                    # send mail
                    if self.enable_alert:
                        source = 'alert'
                        type = log.get('AppProto', '')
                        t = log.get('Date', time.ctime())
                        smtype = ('标题', '内容', '文件名', '文件内容', '文件内容')
                        content = '{mtype} 命中关键字 {kw}'.format(mtype=smtype[mtype],
                                                                   kw=kw)
                        send_email_msg(source, type, content, t)
                # key = (ip, level)
                # just use policy 0 in countlist to record log amount
                # for i in ret:
                #     if key in res_list:
                #         countlist[policy][mtype][key] += 1
                #     else:
                #         countlist[policy][mtype][key] = 1
                #     pass

                # self.unlock();
        except Exception as e:
            # log here
            print e
        finally:
            pass
        if check_flag:
        # if True:
            return ret
        else:
            return list()

if __name__ == '__main__':
    # at = AcType()
    # # txt = '你好吗他们哈哈哈'
    # txt = '2017'
    # ip = '172.16.3.123'
    # acE = AcEngine()
    # # acE.start_reload()
    # ret = acE.ac_search(None, 0, 0, txt, ip, at.ac_search)
    # print ret
    # for i in ret:
    #     print i
    # at.printout()
    at = AcType()
    at.update_counter()
    at.save_counter()

    pass
