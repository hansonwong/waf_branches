#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import logging
import binascii
import zipfile
from lib.common import *
from lib.waf_netutil import *

class RtfReport:
    def __init__(self,report_id):
        try:
            self.conn = ''
            self.cursor = ''
            self.mysqlConnect()
            self.cursor.execute("select `name`,`filename`,`task_id`,`other` from `report_list` where `id` = '%s'" % (report_id))
            res = self.cursor.fetchone()
            self.report_name = res['name'].encode('utf8')
            self.task_id = str(res['task_id'])
            self.filename = res['filename']
            self.other = res['other']
            list = self.other.split('#')
            self.iplist = list[0].split(':')[1]
            self.block = list[1].split(':')[1]
            self.vullevel = list[2].split(':')[1]
            self.weaklist = list[3].split(':')[1]
            self.isCondReport = False
            if self.iplist != '' and self.block != '':
                self.isCondReport = True
            #end if
            self.filepath = "/var/www/Report/" + res['filename'] + "/report.rtf"
            self.mysqlClose()
            self.tempfile = "/var/www/Report/default/rtf_template.rtf"
            self.tempfile_ip = "/var/www/Report/default/rtf_ip_template.rtf"
            self.inext = 0
            self.task_summary_table = "task_summary_" + self.task_id
            self.hostmsg_table = "hostmsg_" + self.task_id
            self.host_vul_table = "host_vul_" + self.task_id
            self.web_vul_table = "web_vul_" + self.task_id
            self.weak_pwd_table = "weak_pwd_" + self.task_id
            self.vul_details_table = "vul_details_" + self.task_id
            self.scan_result_table = "scan_result_" + self.task_id
            self.weak_pwd_details_table = "weak_pwd_details_" + self.task_id
            self.port_list_table = "port_list_" + self.task_id
            
            self.c_level_str = "\\lang2052\\f1\\'a1\\'be\\cf4\\'bd\\'f4\\'bc\\'b1\\cf0\\'a1\\'bf\\lang1033\\f0 "
            self.h_level_str = "\\lang2052\\f1\\'a1\\'be\\cf5\\'b8\\'df\\'b7\\'e7\\'cf\\'d5\\cf0\\'a1\\'bf\\lang1033\\f0 "
            self.m_level_str = "\\lang2052\\f1\\'a1\\'be\\cf6\\'d6\\'d0\\'b7\\'e7\\'cf\\'d5\\cf0\\'a1\\'bf\\lang1033\\f0 "
            self.l_level_str = "\\lang2052\\f1\\'a1\\'be\\cf7\\'b5\\'cd\\'b7\\'e7\\'cf\\'d5\\cf0\\'a1\\'bf\\lang1033\\f0 "
            self.n_level_str = "\\lang2052\\f1\\'a1\\'be\\cf8\\'d0\\'c5\\'cf\\'a2\\cf0\\'a1\\'bf\\lang1033\\f0 "
            
            self.c_level_str_ip = "\\lang2052\\f1\\'a1\\'be\\cf6\\'bd\\'f4\\'bc\\'b1\\cf0\\'a1\\'bf\\lang1033\\f0 "
            self.h_level_str_ip = "\\lang2052\\f1\\'a1\\'be\\cf7\\'b8\\'df\\'b7\\'e7\\'cf\\'d5\\cf0\\'a1\\'bf\\lang1033\\f0 "
            self.m_level_str_ip = "\\lang2052\\f1\\'a1\\'be\\cf8\\'d6\\'d0\\'b7\\'e7\\'cf\\'d5\\cf0\\'a1\\'bf\\lang1033\\f0 "
            self.l_level_str_ip = "\\lang2052\\f1\\'a1\\'be\\cf9\\'b5\\'cd\\'b7\\'e7\\'cf\\'d5\\cf0\\'a1\\'bf\\lang1033\\f0 "
            self.n_level_str_ip = "\\lang2052\\f1\\'a1\\'be\\cf10\\'d0\\'c5\\'cf\\'a2\\cf0\\'a1\\'bf\\lang1033\\f0 "
            
        except Exception,e:
            logging.getLogger().error("__init__(RtfReport) exception:" + str(e))
        #end try
    #end def
    
    def mysqlConnect(self):
        try:
            self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            return True
        except Exception,e:
            logging.getLogger().error("mysql connect Exception(RtfReport):" + str(e))
            return False
        #end try
    #end def
    
    def mysqlClose(self):
        try:
            self.cursor.close()
            self.conn.close()
            return True
        except Exception,e:
            logging.getLogger().error("mysql close Exception(RtfReport):" + str(e))
            return False
        #end try
    #end def
    
    def str2ascii(self,content):
        try:
            if content == "":
                return ""
            #end if
            #content = content.decode("utf8").encode("gb2312")
            try:
                content = content.decode("utf8").encode("gb2312")
            except Exception,e1:
                content.encode("gb2312")   
            #end try
            sb = ""
            array = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
            bit = 0
            for i in range(0,len(content)):
                num = ord(content[i])
                bit = (num & 0x0f0)>>4
                if num > 0:
                    sb += "\\'"
                else:
                    if self.inext == 0:
                        sb += "\\lang2052\\f1"
                        sb += "\\'"
                        self.inext = 1
                    else:
                        sb += "\\'"
                    #end if
                #end if
                sb += array[bit]
                bit = num & 0x0f
                sb += array[bit]
                if num < 0 and self.inext == 1:
                    sb += "\\lang1033\\f0"
                    self.inext = 0
                #end if
            #end for
            sb = "\\lang2052\\f1" + sb + "\\lang3081\\f0"
            return sb
        except Exception,e:
            logging.getLogger().debug("str2ascii(RtfReport) exception:" + str(e) + "(content:" + content + ")")
            return ""
        #end try
    #end def
    
    def img2htx(self,filepath):
        try:
            if filepath == '':
                return ""
            #end if
            f = open(filepath,"rb")
            msg = f.read()
            f.close()
            msg = binascii.b2a_hex(msg)
            
            return msg
        except Exception,e:
            logging.getLogger().error("img2htx(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getImgContent(self,filepath):
        try:
            start = "{\\pict\\wmetafile8\\picwgoal8698\\pichgoal5219\n"
            end = "}\n"
            
            msg = start + self.img2htx(filepath) + end
            
            return msg
        except Exception,e:
            logging.getLogger().error("getImgContent(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end

    def getTemp(self):
        content = []
        try:
            f = file(self.tempfile, "r+")
            content = f.readlines()
            f.close()
            return content
        except Exception,e:
            logging.getLogger().error("getTemp(RtfReport) exception:" + str(e))
            return content
        #end try
    #end def
    
    def getTemp_ip(self):
        content = []
        try:
            f = file(self.tempfile_ip,"r+")
            content = f.readlines()
            f.close()
            return content
        except Exception,e:
            logging.getLogger().error("getTemp_ip(RtfReport) exception:" + str(e))
            return content
        #end try
    #end def
    
    def rmdirs(self,dir):
        try:
            files = os.listdir(dir)
            if len(files) > 0:
                for f in files:
                    #print f
                    if f == '.' or f == '..':
                        continue
                    #end if
                    if os.path.isfile(os.path.join(dir,f)):
                        os.remove(os.path.join(dir,f))
                    else:
                        self.rmdirs(os.path.join(dir,f))
                    #end if
                 #end for
            #end if
            os.rmdir(dir)
        except Exception,e:
            logging.getLogger().error("rmdirs(RtfReport) exception:" + str(e))
        #end try
    #end def
    
    def createReport(self):
        try:
            
            if os.path.exists("/var/www/Report/"+self.filename):
                self.rmdirs("/var/www/Report/"+self.filename+"/")
            #end if
            os.mkdir("/var/www/Report/"+self.filename)
            os.mkdir("/var/www/Report/"+self.filename+"/hosts")
            
            self.writeRtf()
            
            if self.isCondReport == False or self.iplist == '':
                sql = "select `ip` from %s where `status` = '1'" % (self.task_summary_table)
            else:
                sql = "select `ip` from %s where `status` = '1' and `id` in (%s)" % (self.task_summary_table,self.iplist)
            #end if
            self.mysqlConnect()
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            self.mysqlClose()
            if res and len(res) > 0:
                for row in res:
                    ip = row['ip']
                    self.writeRtf_ip(ip)
                #end for
            #end if
            
            waf_popen("cd /var/www/Report/" + self.filename + "; zip -q -r report.zip report.rtf hosts;")
        except Exception,e:
            logging.getLogger().error("createReport(RtfReport) exception:" + str(e))
            return False
        #end try
    #end def
    
    def writeRtf(self):
        try:
            content = self.main()
            f = file("/var/www/Report/"+self.filename+"/report.rtf", "w+")
            #f = file(self.filepath, "w+")
            f.writelines(content)
            f.close()
            
            
            
            #f = zipfile.ZipFile("/var/www/Report/"+self.filename+"/report.zip", 'w') 
            #f.write("/var/www/Report/"+self.filename+"/report.rtf","report.rtf") 
            #f.close() 
            #vulscan_popen("zip /var/www/Report/%s/report.zip /var/www/Report/%s/report.rtf" % (self.filename,self.filename))
            
        except Exception,e:
            logging.getLogger().error("writeRtf(RtfReport) exception:" + str(e))
        #end try
    #end def
    
    def writeRtf_ip(self,ip):
        try:
            content_ip = self.main_ip(ip)
            filepath = ""
            dir = "/var/www/Report/"+self.filename+"/hosts/"
            filepath = dir + ip + '.rtf'
            f = file(filepath,"w+")
            f.writelines(content_ip)
            f.close()
        except Exception,e:
            logging.getLogger().error("writeRtf_ip(RtfReport) exception:" + str(e))
        #end try
    #end def
    
    def createImg(self):
        try:
            import urllib
            import urllib2
            value = {'task_id':self.task_id,'iplist':self.iplist,'block':self.block,'vullevel':self.vullevel,'weaklist':self.weaklist}
            req = urllib2.Request("https://127.0.0.1/html/autoreport/createimg",urllib.urlencode(value))
            res = urllib2.urlopen( req )
            html = res.read()
            res.close()
            if html.find("success") > 0:
                return True
            else:
                return False
            #end if
        except Exception,e:
            logging.getLogger().error("createImg(RtfReport) exception:" + str(e))
            return False
        #end try
    #end def
    
    def getHeaderContent(self):
        try:
            msg = "铱迅信息“远程安全评估系统”安全评估报告"
            msg = self.str2ascii(msg)
            content = "\\clbrdrb\\brdrw10\\brdrs \\cellx8414\\pard\\intbl\\nowidctlpar\\qc\\kerning2\\f0\\fs30 #report_title#\\cell\\row\\pard\\nowidctlpar\\qj\\fs21\\parn"
            content = content.replace("#report_title#",msg)
            return content
        except Exception,e:
            logging.getLogger().error("getHeaderContent(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getHeaderContent_ip(self,ip):
        try:
            content = "\\clbrdrb\\brdrw10\\brdrs\\brdrcf1 \\cellx8748\\pard\\intbl\\nowidctlpar\\qc\\lang2052\\kerning2\\b\\f1\\fs24\\'d2\\'bf\\'d1\\'b8\\'d0\\'c5\\'cf\\'a2\\lang1033\\f2\\ldblquote\\lang2052\\f1\\'d4\\'b6\\'b3\\'cc\\'b0\\'b2\\'c8\\'ab\\'c6\\'c0\\'b9\\'c0\\'cf\\'b5\\'cd\\'b3\\lang1033\\f0 --\\f2 ip\\f0\\f2\\rdblquote\\lang2052\\f1\\'b0\\'b2\\'c8\\'ab\\'c6\\'c0\\'b9\\'c0\\'b1\\'a8\\'b8\\'e6\\lang1033\\b0\\f0\\cell\\row\\pard\\nowidctlpar\\qj\\fs21\\par"
            content = content.replace("ip",ip)
            return content
        except Exception,e:
            logging.getLogger().error("getHeaderContent_ip(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getVersion(self):
        try:
            version = ""
            f = file("/var/www/yx.config.inc.php","r+")
            lines = f.readlines()
            f.close()
            for line in lines:
                if line.find("build") > 0:
                    tmp = line.split("'")
                    if len(tmp) == 3:
                        version = tmp[1]
                        break
                    #end if
                #end if
            #end for
            return str(version)
        except Exception,e:
            logging.getLogger().error("getVersion(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    
    def getReviewData(self):
        #dirlist = ["1.综述","2.风险类别","  2.1.网络风险分布","  2.2.漏洞分类","3.操作系统分布","4.主机风险等级列表","5.漏洞分布","6.主机漏洞详细信息","7.Web漏洞详细信息","8.脆弱账号","  8.1.FTP账号","  8.2.SSH账号","  8.3.3389账号","  8.4.Telnet账号","  8.5.MsSQL账号","  8.6.MySQL账号","  8.7.Oracle账号","  8.8.SMB账号","  8.9.VNC账号"]
        #dirlist = ["综述","风险类别","网络风险分布","漏洞分类","操作系统分布","主机风险等级列表","漏洞分布","主机漏洞详细信息","Web漏洞详细信息","脆弱账号","FTP账号","SSH账号","3389账号","Telnet账号","MsSQL账号","MySQL账号","Oracle账号","SMB账号","VNC账号"]
        try:
            self.mysqlConnect()
            sql = "select `task_name`,`status`,`start_time`,`end_time`,`en_fast`,`en_host`,`en_web`,`en_weak`,`init_state`,`prescan_state`,`port_state`,`weak_state`,`web_state`,`host_state`, (c+h) as high, m as med, l as low, i as none from `task_manage` where `id` = '%s'" % (self.task_id)
            self.cursor.execute(sql)
            res = self.cursor.fetchone()
            if res and len(res) > 0:
                task_name = res['task_name'].encode('utf8')
                start_time = str(res['start_time'])
                end_time = str(res['end_time'])
                status = res['status']
                en_fast = res['en_fast']
                en_host = res['en_host']
                en_web = res['en_web']
                en_weak = res['en_weak']
                init_state = res['init_state']
                prescan_state = res['prescan_state']
                port_state = res['port_state']
                weak_state = res['weak_state']
                web_state = res['web_state']
                host_state = res['host_state']
                high = res['high']
                med = res['med']
                low = res['low']
                none = res['none']

                if status == 2 or status == 3:
                    status = 3
                    if init_state != 1:
                        status = 2
                    #end if
                    if prescan_state != 1:
                        status = 2
                    #end if
                    if en_fast == 2 and port_state != 1:
                        status = 2
                    #end if
                    if en_host == 1 and host_state != 1:
                        status = 2
                    #end if
                    if en_web == 1 and web_state != 1:
                        status = 2
                    #end if
                    if en_weak == 1 and weak_state != 1:
                        status = 2
                    #end if
                #end if
                if status == 1:
                    start_time = "--"
                    end_time = "--"
                elif status == 2:
                    end_time = "--"
                #end if
                if self.isCondReport:
                    high = 0
                    med = 0
                    low = 0
                    none = 0
                    self.cursor.execute("select count(*) as c,risk_factor as level from " + self.vul_details_table + " v," + self.task_summary_table + " t where v.ip=t.ip and t.id in (" + self.iplist + ") group by risk_factor union all select count(*) as c , level as level from " + self.scan_result_table + " s," + self.task_summary_table + " t where s.ip=t.ip and t.id in (" + self.iplist + ") group by level union all select count(*) as c,'H' as level from " + self.weak_pwd_details_table + " w," + self.task_summary_table + " t where w.ip = t.ip and t.id in (" + self.iplist + ")")
                    res = self.cursor.fetchall()
                    if res and len(res) > 0:
                        for row in res:
                            if row['level'] == 'C' or row['level'] == 'H' or row['level'] == 'HIGH':
                                high += row['c']
                            elif row['level'] == 'M' or row['level'] == 'MED':
                                med += row['c']
                            elif row['level'] == 'L' or row['level'] == 'LOW':
                                low += row['c']
                            else:
                                none += row['c']
                            #end if
                        #end for
                    #end if
                #end if
                netrisk = ""
                if high > 0:
                    netrisk = "高危风险"
                else:
                    if med > 0:
                        netrisk = "中等风险"
                    else:
                        if low > 0:
                            netrisk = "低风险"
                        else:
                            netrisk = "信息"
                        #end if
                    #end if
                #end if
                if self.isCondReport:
                    ip_scaned = str(len(self.iplist.split(',')))
                    self.cursor.execute("call createIpMostWeakTable(" + self.task_id + ")")
                    self.cursor.execute("select count(*) as c from tmp_ipmostweak tm," + self.task_summary_table + " ta where tm.ip=ta.ip and ta.id in (" + self.iplist + ")")
                    res = self.cursor.fetchone()
                    ip_dangerious = str(res['c'])
                else:
                    sql = "select count(id) as c from %s where `status` = '1'" % (self.task_summary_table)
                    self.cursor.execute(sql)
                    res = self.cursor.fetchone()
                    ip_scaned = str(res['c'])
                    self.cursor.execute("call createIpMostWeakTable(%s)" % (self.task_id))
                    self.conn.commit()
                    self.cursor.execute("select count(*) as c from tmp_ipmostweak")
                    res = self.cursor.fetchone()
                    ip_dangerious = str(res['c'])
                #end if
                if ip_scaned == "":
                    ip_scaned = "0"
                #end if
                if ip_dangerious == "":
                    ip_dangerious = "0"
                #end if
                report_name = str(self.report_name)
                version = self.getVersion()
                
                dirlist = ["1.综述","2.风险类别","    2.1.网络风险分布","    2.2.漏洞分类"]
                num = 3
                if self.isCondReport == False or self.block[0] == '1':
                    dirlist.append(str(num) + ".操作系统分布")
                    num += 1
                #end if
                dirlist.append(str(num) + ".主机风险等级列表")
                if self.isCondReport == False or self.block[1] == '1' or self.block[2] == '1':
                    dirlist.append(str(num) + ".漏洞分布")
                    num += 1
                #end if
                if self.isCondReport == False or self.block[1] == '1':
                    dirlist.append(str(num) + ".主机漏洞详细信息")
                    num += 1
                #end if
                if self.isCondReport == False or self.block[2] == '1':
                    dirlist.append(str(num) + ".Web漏洞详细信息")
                    num += 1
                #end if
                if self.isCondReport == False or self.block[3] == '1':
                    dirlist.append(str(num) + ".脆弱账号")
                    i = 1
                    if self.isCondReport == False or self.weaklist[0] == '1':
                        dirlist.append(str(num) + "." + str(i) + ".FTP账号")
                        i += 1
                    #end if
                    if self.isCondReport == False or self.weaklist[1] == '1':
                        dirlist.append(str(num) + "." + str(i) + ".SSH账号")
                        i += 1
                    #end if
                    if self.isCondReport == False or self.weaklist[2] == '1':
                        dirlist.append(str(num) + "." + str(i) + ".3389账号")
                        i += 1
                    #end if
                    if self.isCondReport == False or self.weaklist[3] == '1':
                        dirlist.append(str(num) + "." + str(i) + ".Telnet账号")
                        i += 1
                    #end if
                    if self.isCondReport == False or self.weaklist[4] == '1':
                        dirlist.append(str(num) + "." + str(i) + ".MsSQL账号")
                        i += 1
                    #end if
                    if self.isCondReport == False or self.weaklist[5] == '1':
                        dirlist.append(str(num) + "." + str(i) + ".MySQL账号")
                        i += 1
                    #end if
                    if self.isCondReport == False or self.weaklist[6] == '1':
                        dirlist.append(str(num) + "." + str(i) + ".Oracle账号")
                        i += 1
                    #end if
                    if self.isCondReport == False or self.weaklist[7] == '1':
                        dirlist.append(str(num) + "." + str(i) + ".SMB账号")
                        i += 1
                    #end if
                    if self.isCondReport == False or self.weaklist[8] == '1':
                        dirlist.append(str(num) + "." + str(i) + ".VNC账号")
                        i += 1
                    #end if
                #end if
                
                data = {"report_name":report_name,"task_name":task_name,"netrisk":netrisk,"ip_scaned":ip_scaned,"ip_dangerious":ip_dangerious,"start_time":start_time,"end_time":end_time,"version":version,"dirlist":dirlist}
            else:
                data = {"report_name":self.report_name,"task_name":"","netrisk":"","ip_scaned":"","ip_dangerious":"","start_time":"","end_time":"","version":self.getVersion(),"dirlist":dirlist}
            #end if
            
            
            #data = {"report_name":self.report_name,"task_name":"yxlink","netrisk":"危险等级","ip_scaned":"100","ip_dangerious":"10","start_time":"2012-01-02","end_time":"2012-01-03","version":self.getVersion(),"dirlist":dirlist}
            self.mysqlClose()
            return data
        except Exception,e:
            logging.getLogger().error("getReviewData(RtfReport) exception:" + str(e))
            data = {"report_name":self.report_name,"task_name":"","netrisk":"","ip_scaned":"","ip_dangerious":"","start_time":"","end_time":"","version":self.getVersion(),"dirlist":dirlist}
            return data
        #end try
    #end def
    
    
    def getReviewContent(self):
        try:
            data = self.getReviewData()
            
            content = "\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx6237\\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\b\\f1\\fs30\\'d7\\'db\\'ca\\'f6\\lang1033\\f0\\nestcell\\b0\\fs21\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1271\\cellx6091\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\nestcell\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1271\\cellx6091\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'b1\\'a8\\'b8\\'e6\\'c3\\'fb\\'b3\\'c6\\lang1033\\f0\\nestcell #report_name#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1271\\cellx6091\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'c8\\'ce\\'ce\\'f1\\'c3\\'fb\\'b3\\'c6\\lang1033\\f0\\nestcell #task_name#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1271\\cellx6091\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'cd\\'f8\\'c2\\'e7\\'b7\\'e7\\'cf\\'d5\\lang1033\\f0\\nestcell #netrisk#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1271\\cellx6091\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'d6\\'f7\\'bb\\'fa\\'cd\\'b3\\'bc\\'c6\\lang1033\\f0\\nestcell\\lang2052\\f1\\'d2\\'d1\\'c9\\'a8\\'c3\\'e8\\'d6\\'f7\\'bb\\'fa\\'ca\\'fd\\'a3\\'ba\\lang1033\\f0 #ip_scaned#\\par\\lang2052\\f1\\'b7\\'c7\\'b3\\'a3\\'ce\\'a3\\'cf\\'d5\\'d6\\'f7\\'bb\\'fa\\'a3\\'ba\\lang1033\\f0 #ip_dangerious#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1271\\cellx6091\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'ca\\'b1\\'bc\\'e4\\'cd\\'b3\\'bc\\'c6\\lang1033\\f0\\nestcell\\lang2052\\f1\\'bf\\'aa\\'ca\\'bc\\'ca\\'b1\\'bc\\'e4\\'a3\\'ba\\lang1033\\f0 #start_time#\\par\\lang2052\\f1\\'bd\\'e1\\'ca\\'f8\\'ca\\'b1\\'bc\\'e4\\'a3\\'ba\\lang1033\\f0 #end_time#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1271\\cellx6091\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'cf\\'b5\\'cd\\'b3\\'b0\\'e6\\'b1\\'be\\lang1033\\f0\\nestcell #version#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1271\\cellx6091\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\nowidctlpar\\qj\\cell\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\fs20\\'c4\\'bf\\'c2\\'bc\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs \\cellx2285\\nestrow}{\\nonesttables\\par}\n"
            
            dirItem = "\\pard\\intbl\\itap2\\nowidctlpar\\qj #dirname#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            dirItem += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs \\cellx2285\\nestrow}{\\nonesttables\\par}\n"
            
            contentEnd = "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            contentEnd += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx2285\\nestrow}{\\nonesttables\\par}\n"
            contentEnd += "\\pard\\intbl\\nowidctlpar\\qj\\cell\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\cellx6237\\cellx8748\\row\\pard\\nowidctlpar\\qj\\par\n"
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            content = content.replace("#report_name#",self.str2ascii(data['report_name']))
            content = content.replace("#task_name#",self.str2ascii(data['task_name']))
            content = content.replace("#netrisk#",self.str2ascii(data['netrisk']))
            content = content.replace("#ip_scaned#",self.str2ascii(data['ip_scaned']))
            content = content.replace("#ip_dangerious#",self.str2ascii(data['ip_dangerious']))
            content = content.replace("#start_time#",data['start_time'])
            content = content.replace("#end_time#",data['end_time'])
            content = content.replace("#version#",self.str2ascii(data['version']))
            
            for line in data['dirlist']:
                content += dirItem.replace("#dirname#",self.str2ascii(line))
            #end for
            
            content += contentEnd
            
            return content 
            
        except Exception,e:
            logging.getLogger().error("getReviewContent(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getReviewData_ip(self,ip):
        try:
            task_name = '--'
            start_time = '--'
            end_time = '--'
            os = '--'
            dir = []
            
            self.mysqlConnect()
            self.cursor.execute("select task_name from task_manage where id = '%s'" % (self.task_id))
            res = self.cursor.fetchone()
            if res and len(res) > 0:
                task_name = self.str2ascii(res['task_name'].encode('utf8'))
            #end if
            self.cursor.execute("select os,running_os from %s where ip = '%s'" % (self.hostmsg_table,ip))
            res = self.cursor.fetchone()
            if res and len(res) > 0:
                os = res['os']
                running_os = res['running_os']
            #end if
            if os == '':
                os = running_os
            #end if
            self.cursor.execute("select start_time,end_time from %s where ip = '%s'" % (self.task_summary_table,ip))
            res = self.cursor.fetchone()
            if res and len(res) > 0:
                start_time = str(res['start_time'])
                end_time = str(res['end_time'])
            #end if
            self.mysqlClose()
            
            if self.isCondReport:
                i = 0
                i += 1
                dir.append(str(i) + ". 综述")
                if self.block[0] == '1':
                    i += 1
                    dir.append(str(i) + ". 开放端口")
                #end if
                if self.block[2] == '1':
                    i += 1
                    dir.append(str(i) + ". Web漏洞")
                #end if
                if self.block[1] == '1':
                    i += 1
                    dir.append(str(i) + ". 主机漏洞")
                #end if
                if self.block[3] == '1':
                    i += 1
                    dir.append(str(i) + ". 脆弱账号")
                    
                    ii = 0
                    if self.weaklist[0] == '1':
                        ii += 1
                        dir.append("    " + str(i) + "." + str(ii) + ". FTP账号")
                    #end if
                    if self.weaklist[1] == '1':
                        ii += 1
                        dir.append("    " + str(i) + "." + str(ii) + ". SSH账号")
                    #end if
                    if self.weaklist[2] == '1':
                        ii += 1
                        dir.append("    " + str(i) + "." + str(ii) + ". 3389账号")
                    #end if
                    if self.weaklist[3] == '1':
                        ii += 1
                        dir.append("    " + str(i) + "." + str(ii) + ". Telnet账号")
                    #end if
                    if self.weaklist[4] == '1':
                        ii += 1
                        dir.append("    " + str(i) + "." + str(ii) + ". MsSQL账号")
                    #end if
                    if self.weaklist[5] == '1':
                        ii += 1
                        dir.append("    " + str(i) + "." + str(ii) + ". MySQL账号")
                    #end if
                    if self.weaklist[6] == '1':
                        ii += 1
                        dir.append("    " + str(i) + "." + str(ii) + ". Oracle账号")
                    #end if
                    if self.weaklist[7] == '1':
                        ii += 1
                        dir.append("    " + str(i) + "." + str(ii) + ". SMB账号")
                    #end if
                    if self.weaklist[8] == '1':
                        ii += 1
                        dir.append("    " + str(i) + "." + str(ii) + ". VNC账号")
                    #end if
                #end if
                
            else:
                dir.append("1. 综述")
                dir.append("2. 开放端口")
                dir.append("3. Web漏洞")
                dir.append("4. 主机漏洞")
                dir.append("5. 脆弱账号")
                dir.append("    5.1. FTP账号")
                dir.append("    5.2. SSH账号")
                dir.append("    5.3. 3389账号")
                dir.append("    5.4. Telnet账号")
                dir.append("    5.5. MsSQL账号")
                dir.append("    5.6. MySQL账号")
                dir.append("    5.7. Oracle账号")
                dir.append("    5.8. SMB账号")
                dir.append("    5.9. VNC账号")
            #end if
            dirtmp = dir
            dir = []
            for row in dirtmp:
                dir.append(self.str2ascii(row))
            #end for
            dirtmp = []
            
            data = {'report_name':self.str2ascii(self.report_name),'task_name':task_name,'start_time':start_time,'end_time':end_time,'os':os,'dir':dir}
            return data
        except Exception,e:
            logging.getLogger().error("getReviewData_ip(RtfReport) exception:" + str(e))
            data = {'report_name':'','task_name':'','start_time':'','end_time':'','os':'','dir':[]}
            return data
        #end try
    #end def
    
    def getReviewContent_ip(self,ip):
        try:
            
            data = self.getReviewData_ip(ip)
            report_name = '--'
            task_name = '--'
            start_time = '--'
            end_time = '--'
            os = '--'
            dir = []
            if data['report_name'] and data['report_name'] != '':
                report_name = data['report_name']
            #end if
            if data['task_name'] and data['task_name'] != '':
                task_name = data['task_name']
            #end if
            if data['start_time'] and data['start_time'] != '':
                start_time = data['start_time']
            #end if
            if data['end_time'] and data['end_time'] != '':
                end_time = data['end_time']
            #end if
            if data['os'] and data['os'] != '':
                os = data['os']
            #end if
            if data['dir'] and len(data['dir']) > 0:
                dir = data['dir']
            #end if

            content = "\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx6096\\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qj\\b 1. \\lang2052\\f1\\'d7\\'db\\'ca\\'f6\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat3\\cellx5973\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\b0\\fs18\\nestcell\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1129\\cellx5973\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'b1\\'a8\\'b8\\'e6\\'c3\\'fb\\'b3\\'c6\\lang1033\\f0\\nestcell #report_name#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1129\\cellx5973\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'c8\\'ce\\'ce\\'f1\\'c3\\'fb\\'b3\\'c6\\lang1033\\f0\\nestcell #task_name#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1129\\cellx5973\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'d6\\'f7\\'bb\\'fa\\lang1033\\f0 IP\\nestcell #ip#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1129\\cellx5973\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'ca\\'b1\\'bc\\'e4\\'cd\\'b3\\'bc\\'c6\\lang1033\\f0\\nestcell\\lang2052\\f1\\'bf\\'aa\\'ca\\'bc\\'a3\\'ba\\lang1033\\f0 #start_time#\\par\n"
            content += "\\lang2052\\f1\\'bd\\'e1\\'ca\\'f8\\'a3\\'ba\\lang1033\\f0 #end_time#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1129\\cellx5973\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'b2\\'d9\\'d7\\'f7\\'cf\\'b5\\'cd\\'b3\\lang1033\\f0\\nestcell #os#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx1129\\cellx5973\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\nowidctlpar\\qj\\fs21\\cell\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'c4\\'bf\\'c2\\'bc\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx2426\\nestrow}{\\nonesttables\\par}\n"
            
            dirItem = "\\pard\\intbl\\itap2\\nowidctlpar\\qj #dirname#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            dirItem += "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx2426\\nestrow}{\\nonesttables\\par}\n"
            
            contentEnd = "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            contentEnd += "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx2426\\nestrow}{\\nonesttables\\par}\n"
            contentEnd += "\\pard\\intbl\\nowidctlpar\\qj\\cell\\trowd\\trgaph108\\trleft-108\\cellx6096\\cellx8748\\row\\pard\\nowidctlpar\\qj\\fs21\\par\n"
            
            content = content.replace("#report_name#",report_name)
            content = content.replace("#task_name#",task_name)
            content = content.replace("#ip#",ip)
            content = content.replace("#start_time#",start_time)
            content = content.replace("#end_time#",end_time)
            content = content.replace("#os#",os)

            for row in dir:
                #print row
                content += dirItem.replace("#dirname#",row)
            #end for
            content += contentEnd
            
            return content
            
        except Exception,e:
            logging.getLogger().error("getReviewContent_ip(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getPortData_ip(self,ip):
        try:
            portlist = []
            self.mysqlConnect()
            self.cursor.execute("select port,proto,service,version from %s where ip = '%s'" % (self.port_list_table,ip))
            res = self.cursor.fetchall()
            if res and len(res) > 0:
                for row in res:
                    portlist.append({'port':str(row['port']),'proto':str(row['proto']),'service':str(row['service']),'version':str(row['version'])})
                #end for
            #end if
            self.mysqlClose()
            
            return portlist
        except Exception,e:
            logging.getLogger().error("getPortData_ip(RtfReport) exception:" + str(e))
            return []
        #end try
    #end def
    
    def getPortContent_ip(self,ip):
        try:
            
            if self.isCondReport and self.block[0] == '0':
                return ""
            #end if
            
            portlist = self.getPortData_ip(ip)
            
            content = "\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat3\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\b #num#\\lang2052\\f1\\'bf\\'aa\\'b7\\'c5\\'b6\\'cb\\'bf\\'da\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx993\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1985\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx4536\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qc\\lang2052\\b0\\f1\\fs18\\'b6\\'cb\\'bf\\'da\\lang1033\\f0\\cell\\lang2052\\f1\\'d0\\'ad\\'d2\\'e9\\lang1033\\f0\\cell\\lang2052\\f1\\'b7\\'fe\\'ce\\'f1\\lang1033\\f0\\cell\\lang2052\\f1\\'b0\\'e6\\'b1\\'be\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            portItem = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx993\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1985\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx4536\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qc #port#\\cell #proto#\\cell #service#\\cell #version#\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            nodata = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qc\\lang2052\\f1\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            contentEnd = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qc\\cell\\row\\pard\\nowidctlpar\\qj\\fs21\\par\n"
            
            if self.isCondReport == False or self.block[0] == '1':
                content = content.replace("#num#","2. ")
            #end if
            
            for row in portlist:
                port = row['port']
                proto = row['proto']
                service = row['service']
                version = row['version']
                content += portItem.replace("#port#",port).replace("#proto#",proto).replace("#service#",service).replace("#version#",version)
            #end for
            content += contentEnd
            
            return content
            
        except Exception,e:
            logging.getLogger().error("getPortContent_ip(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getWebVulData_ip(self,ip):
        try:
            sql = ""
            if self.isCondReport:
                wheresql = ""
                if self.vullevel[1] == '1':
                    wheresql += "'HIGH',"
                #end if
                if self.vullevel[2] == '1':
                    wheresql += "'MED',"
                #end if
                if self.vullevel[3] == '1':
                    wheresql += "'LOW',"
                #end if
                if wheresql == "":
                    return []
                else:
                    wheresql = wheresql[0:-1]
                    sql = "select `url`,`vul_type` ,`level`,`detail` from %s where ip = '%s' and `level` in (%s)" % (self.scan_result_table,ip,wheresql)
                #end if
            else:
                sql = "select `url`,`vul_type` ,`level`,`detail` from %s where ip = '%s'" % (self.scan_result_table,ip)
            #end if
            self.mysqlConnect()
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            weblist = []
            if res and len(res) > 0:
                for row in res:
                    vul_type = self.str2ascii(row['vul_type'].encode('utf8'))
                    #level = self.str2ascii(row['level'].encode('utf8'))
                    level = row['level']
                    if level == 'HIGH':
                        level = self.h_level_str_ip
                    elif level == 'MED':
                        level = self.m_level_str_ip
                    elif level == 'LOW':
                        level = self.l_level_str_ip
                    else:
                        level = level.encode('utf8')
                    #end if
                    detail = self.str2ascii(row['detail'].encode('utf8'))
                    url = row['url'].encode('utf8')
                    
                    flag = True
                    i = 0
                    for i in range(len(weblist)):
                        if weblist[i]['vulname'] == vul_type and weblist[i]['level'] == level and weblist[i]['detail'] == detail:
                            weblist[i]['urllist'].append(url)
                            flag = False
                            break
                        #end if
                    #end for
                    if flag:
                        urllist = []
                        urllist.append(url)
                        weblist.append({'vulname':vul_type,'level':level,'detail':detail,'urllist':urllist})
                    #end if
                #end for
            #end if
            self.mysqlClose()
            
            return weblist
        except Exception,e:
            logging.getLogger().error("getWebVulData_ip(RtfReport) exception:" + str(e))
            return []
        #end try
    #end def
    
    def getWebVulContent_ip(self,ip):
        try:
            if self.isCondReport and self.block[2] == '0':
                return ""
            #end if
            
            weblist = self.getWebVulData_ip(ip)
            
            content = "\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat3\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\b #num#Web\\lang2052\\f1\\'c2\\'a9\\'b6\\'b4\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            webItem = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\b0\\f1\\fs18\\'c2\\'a9\\'b6\\'b4\\'c3\\'fb\\'b3\\'c6\\lang1033\\f0\\nestcell #vulname#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            webItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'ce\\'a3\\'cf\\'d5\\'b5\\'c8\\'bc\\'b6\\lang1033\\f0\\nestcell #level#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            webItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj URL\\nestcell #url#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            webItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'cf\\'ea\\'cf\\'b8\\'c3\\'e8\\'ca\\'f6\\lang1033\\f0\\nestcell #detail#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            webItem += "\\pard\\intbl\\nowidctlpar\\qj\\fs21\\cell\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            nodata = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            nodata += "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\fs21\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            contentEnd = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\cell\\row\\pard\\nowidctlpar\\qj\\par\n"            
            
            if self.isCondReport:
                num = 1
                if self.block[0] == '1':
                    num += 1
                #end if
                num += 1
                content = content.replace("#num#", str(num) + ". ")
            else:
                content = content.replace("#num#", "3. ")
            #end if
            
            if weblist and len(weblist) > 0:
                for row in weblist:
                    vulname = row['vulname']
                    level = row['level']
                    detail = row['detail']
                    url_str = ''
                    for url_item in row['urllist']:
                        url_str += url_item + '\n'
                    #end for
                    content += webItem.replace("#vulname#",vulname).replace("#level#",level).replace("#url#",url_str).replace("#detail#",detail)
                #end for
            else:
                content += nodata
            #end if
            content += contentEnd
            
            return content
            
        except Exception,e:
            logging.getLogger().error("getWebVulContent_ip(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getHostVulData_ip(self,ip):
        try:
            sql = ""
            if self.isCondReport:
                wheresql = ""
                if self.vullevel[0] == '1':
                    wheresql += "'C',"
                #end if
                if self.vullevel[1] == '1':
                    wheresql += "'H',"
                #end if
                if self.vullevel[2] == '1':
                    wheresql += "'M',"
                #end if
                if self.vullevel[3] == '1':
                    wheresql += "'L',"
                #end if
                if self.vullevel[4] == '1':
                    wheresql += "'I',"
                #end if
                if wheresql == "":
                    return []
                else:
                    wheresql = wheresql[0:-1]
                    sql = "select `cve`,`risk_factor` as `level`,`vul_name` as `vulname`,`desc`,`solution`,`ref`,`port`,`proto` from %s where `ip` = '%s' and `risk_factor` in (%s)" % (self.vul_details_table,ip,wheresql)
                #end if
            else:
                sql = "select `cve`,`risk_factor` as `level`,`vul_name` as `vulname`,`desc`,`solution`,`ref`,`port`,`proto` from %s where `ip` = '%s'" % (self.vul_details_table,ip)
            #end if
            
            hostlist = []
            self.mysqlConnect()
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            if res and len(res) > 0:
                for row in res:
                    cve = ''
                    level = ''
                    vulname = ''
                    desc = ''
                    solution = ''
                    ref = ''
                    port = ''
                    proto = ''
                    if row['cve'] != '':
                        cve = row['cve'].encode('utf8')
                        cve = cve.replace("\r\n", "")
                    #end if
                    level = row['level']
                    if level == 'C':
                        level = self.c_level_str_ip
                    elif level == 'H':
                        level = self.h_level_str_ip
                    elif level == 'M':
                        level = self.m_level_str_ip
                    elif level == 'L':
                        level = self.l_level_str_ip
                    elif level == 'I':
                        level = self.n_level_str_ip
                    else:
                        level = level.encode('utf8')
                    #end if
                    vulname = row['vulname'].encode('utf8')
                    vulname = vulname.replace("\n", "")
                    vulname = vulname.replace("\r", "")
                    port = str(row['port'])
                    proto = row['proto'].encode('utf8')
                    vulname = vulname + " 【" + proto + "/" + port +"】"
                    desc = row['desc'].encode('utf8')
                    desc = desc.replace("\r\n", "\n")
                    if row['solution'] != '':
                        solution = row['solution'].encode('utf8')
                        solution = solution.replace("\r\n", "\n")
                    #end if
                    if row['ref'] != '':
                        ref = row['ref'].encode('utf8')
                        ref = ref.replace("\r\n", "\n")
                    #end if
                    hostlist.append({'vulname':vulname,'level':level,'desc':desc,'solu':solution,'cve':cve,'ref':ref})
                #end for
            #end if
            self.mysqlClose()
            
            return hostlist
        except Exception,e:
            logging.getLogger().error("getHostVulData_ip(RtfReport) exception:" + str(e))
            return []
        #end try
    #end def
    
    def getHostVulContent_ip(self,ip):
        try:
            if self.isCondReport and self.block[1] == '0':
                return ""
            #end if
            
            hostlist = self.getHostVulData_ip(ip)
            
            content = "\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat3\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\b #num#\\lang2052\\f1\\'d6\\'f7\\'bb\\'fa\\'c2\\'a9\\'b6\\'b4\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            
            hostItem = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\b0\\f1\\fs18\\'c2\\'a9\\'b6\\'b4\\'c3\\'fb\\'b3\\'c6\\lang1033\\f0\\nestcell #vulname#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'ce\\'a3\\'cf\\'d5\\'b5\\'c8\\'bc\\'b6\\lang1033\\f0\\nestcell #level#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'cf\\'ea\\'cf\\'b8\\'c3\\'e8\\'ca\\'f6\\lang1033\\f0\\nestcell #desc#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'bd\\'e2\\'be\\'f6\\'b7\\'bd\\'b0\\'b8\\lang1033\\f0\\nestcell #solu#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj CVE\\nestcell #cve#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'b2\\'ce\\'bf\\'bc\\lang1033\\f0\\nestcell #ref#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx1276\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\nowidctlpar\\qj\\fs21\\cell\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"            
            
            nodata = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            nodata += "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\fs21\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            contentEnd = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\cell\\row\\pard\\nowidctlpar\\qj\\par\n"            
            
            if self.isCondReport:
                num = 1
                if self.block[0] == '1':
                    num += 1
                #end if
                if self.block[2] == '1':
                    num += 1
                #end if
                num += 1
                content = content.replace("#num#", str(num) + ". ")
            else:
                content = content.replace("#num#", "4. ")
            #end if
            
            if hostlist and len(hostlist) > 0:
                for row in hostlist:
                    vulname = self.str2ascii(row['vulname'])
                    #level = self.str2ascii(row['level'])
                    level = row['level']
                    desc = self.str2ascii(row['desc'])
                    solu = self.str2ascii(row['solu'])
                    cve = self.str2ascii(row['cve'])
                    ref = self.str2ascii(row['ref'])
                    
                    content += hostItem.replace("#vulname#",vulname).replace("#level#",level).replace("#desc#",desc).replace("#solu#",solu).replace("#cve#",cve).replace("#ref#",ref)
                #end for
            else:
                content += nodata
            #end if
            content += contentEnd
            
            return content
        except Exception,e:
            logging.getLogger().error("getHostVulContent_ip(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getWeakVulData_ip(self,ip):
        try:
            weakvullist = []
            typelist = []
            if self.isCondReport:
                if self.weaklist[0] == '1':
                    typelist.append('ftp')
                #end if
                if self.weaklist[1] == '1':
                    typelist.append('ssh')
                #end if
                if self.weaklist[2] == '1':
                    typelist.append('3389')
                #end if
                if self.weaklist[3] == '1':
                    typelist.append('telnet')
                #end if
                if self.weaklist[4] == '1':
                    typelist.append('mssql')
                #end if
                if self.weaklist[5] == '1':
                    typelist.append('mysql')
                #end if
                if self.weaklist[6] == '1':
                    typelist.append('oracle')
                #end if
                if self.weaklist[7] == '1':
                    typelist.append('smb')
                #end if
                if self.weaklist[8] == '1':
                    typelist.append('vnc')
                #end if
            else:
                typelist.append('ftp')
                typelist.append('ssh')
                typelist.append('3389')
                typelist.append('telnet')
                typelist.append('mssql')
                typelist.append('mysql')
                typelist.append('oracle')
                typelist.append('smb')
                typelist.append('vnc')
            #end if
            self.mysqlConnect()
            for typeItem in typelist:
                self.cursor.execute("select `username`,`password` from %s where `ip` = '%s' and `type` = '%s'" % (self.weak_pwd_details_table,ip,typeItem))
                res = self.cursor.fetchall()
                list = []
                if res and len(res) > 0:
                    for row in res:
                        username = str(row['username'])
                        password = str(row['password'])
                        list.append({'username':username,'password':password})
                    #end for
                #end if
                weakvullist.append({'type':typeItem,'list':list})
            #end for
            self.mysqlClose()
            
            return weakvullist
        except Exception,e:
            logging.getLogger().error("getWeakVulData_ip(RtfReport) exception:" + str(e))
            return []
        #end try
    #end def
    
    def getWeakVulContent_ip(self,ip):
        try:
            if self.isCondReport and self.block[3] == '0':
                return ""
            #end if
            
            data = self.getWeakVulData_ip(ip)
            
            content = "\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat3\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\b #num#\\lang2052\\f1\\'b4\\'e0\\'c8\\'f5\\'d5\\'cb\\'ba\\'c5\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            weakItemType = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qj\\b0 #type#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemType += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            
            weakItemHeader = "\\pard\\intbl\\itap3\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'d3\\'c3\\'bb\\'a7\\'c3\\'fb\\lang1033\\f0\\nestcell\\lang2052\\f1\\'c3\\'dc\\'c2\\'eb\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemHeader += "\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx4202\\clcbpat5\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            
            weakItemRow = "\\pard\\intbl\\itap3\\nowidctlpar\\qc #username#\\nestcell #password#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemRow += "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx4202\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrt\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            
            weakItemNodata = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\~\\lang2052\\f1\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemNodata += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            
            weakItemEnd = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemEnd += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            weakItemEnd += "\\pard\\intbl\\nowidctlpar\\qj\\fs21\\cell\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemEnd += "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\cell\\row\\trowd\\trgaph108\\trleft-108\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"

            contentEnd = "\\clbrdrl\\brdrw10\\brdrs\\brdrcf3\\clbrdrr\\brdrw10\\brdrs\\brdrcf3\\clbrdrb\\brdrw10\\brdrs\\brdrcf3 \\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\cell\\row\\pard\\nowidctlpar\\qj\\par\n"            
            
            #content += weakItemType + weakItemHeader + weakItemRow + weakItemRow + weakItemEnd + contentEnd
            if self.isCondReport:
                num = 1
                if self.block[0] == '1':
                    num += 1
                #end if
                if self.block[2] == '1':
                    num += 1
                #end if
                if self.block[1] == '1':
                    num += 1
                #end if
                num += 1
                content = content.replace("#num#", str(num) + ". ")
            else:
                content = content.replace("#num#", "5. ")
            #end if
            
            for row in data:
                type = row['type']
                list = row['list']
                content += weakItemType.replace("#type#",type)
                if len(list) > 0:
                    content += weakItemHeader
                    for list_item in list:
                        content += weakItemRow.replace("#username#", list_item['username']).replace("#password#",list_item['password'])
                    #end for
                else:
                    content += weakItemNodata
                #end if
                content += weakItemEnd
            #end for
            content += contentEnd
            
            return content
        except Exception,e:
            logging.getLogger().error("getWeakVulContent_ip(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getRiskTypeData(self):
        try:
            self.mysqlConnect()
            netriskdis_img = ""
            vultype_img = ""
            if self.createImg():
                vultype_img = "/var/www/Report/default/rtfimages/invasion_vultype_bar_chart.png"
                netriskdis_img = "/var/www/Report/default/rtfimages/netriskdis.png"
            #end if
            list = []
            sql = ""
            if self.isCondReport:
                sql = "call createVultypeTable("+self.task_id+",'"+self.iplist+"')"
            else:
                sql = "call createVultypeTable("+self.task_id+",'')"
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
            self.cursor.execute("select * from tmp_vultype order by high desc,med desc,low desc")
            res = self.cursor.fetchall()
            if res and len(res) > 0:
                for row in res:
                    vul_family = row['vulname'].encode('utf8')
                    if row['high']:
                        h_r = str(row['high'])
                    else:
                        h_r = "0"
                    #end if
                    if row['med']:
                        m_r = str(row['med'])
                    else:
                        m_r = "0"
                    #end if
                    if row['low']:
                        l_r = str(row['low'])
                    else:
                        l_r = "0"
                    #end if
                    if row['total']:
                        t_r = str(row['total'])
                    else:
                        t_r = "0"
                    #end if
                    item = {"vul_family":vul_family,"h_r":h_r,"m_r":m_r,"l_r":l_r,"t_r":t_r}
                    list.append(item)
                #end for
            #end if
            data = {"netriskdis_img":netriskdis_img,"vultype_img":vultype_img,"list":list}
            self.mysqlClose()
            
            return data
        except Exception,e:
            logging.getLogger().error("getRiskTypeData(RtfReport) exception:" + str(e))
            data = {"netriskdis_img":"","vultype_img":"","list":[]}
            return data
    #end def
    
    def getRiskTypeContent(self):
        try:
            data = self.getRiskTypeData()
            
            content = "\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\tx1318\\lang2052\\b\\f1\\fs30\\'b7\\'e7\\'cf\\'d5\\'c0\\'e0\\'b1\\'f0\\lang1033\\f0\\tab\\cell\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\b0\\fs20     \\lang2052\\f1\\'cd\\'f8\\'c2\\'e7\\'b7\\'e7\\'cf\\'d5\\'b7\\'d6\\'b2\\'bc\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trrh4170\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qj #netriskdis_img#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trrh4170\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\nowidctlpar\\qj\\cell\\trowd\\trgaph108\\trleft-108\\trrh4170\\cellx8748\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\nowidctlpar\\fi400\\qj\\lang2052\\f1\\'c2\\'a9\\'b6\\'b4\\'b7\\'d6\\'c0\\'e0\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trrh4167\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qj #vultype_img#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trrh4167\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            content += "\\pard\\intbl\\nowidctlpar\\qj\\cell\\trowd\\trgaph108\\trleft-108\\trrh4167\\cellx8748\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qj\\lang2052\\f1\\'b7\\'d6\\'c0\\'e0\\'c3\\'fb\\lang1033\\f0\\nestcell\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\'b8\\'df\\'b7\\'e7\\'cf\\'d5\\lang1033\\f0\\nestcell\\lang2052\\f1\\'d6\\'d0\\'b7\\'e7\\'cf\\'d5\\lang1033\\f0\\nestcell\\lang2052\\f1\\'b5\\'cd\\'b7\\'e7\\'cf\\'d5\\lang1033\\f0\\nestcell\\lang2052\\f1\\'d7\\'dc\\'bc\\'c6\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx4962\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx5954\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx6804\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx7797\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            vulItem = "\\pard\\intbl\\itap2\\nowidctlpar\\qj #vul_family#\\nestcell\\pard\\intbl\\itap2\\nowidctlpar\\qc #h_r#\\nestcell #m_r#\\nestcell #l_r#\\nestcell #t_r#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            vulItem += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx4962\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx5954\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx6804\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx7797\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            vulEmpty = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            vulEmpty += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            contentEnd = "\\pard\\intbl\\nowidctlpar\\qj\\fs20\\cell\\trowd\\trgaph108\\trleft-108\\cellx8748\\row\\pard\\nowidctlpar\\qj\\par\n"
            
            content = content.replace("#netriskdis_img#",self.getImgContent(data['netriskdis_img']))
            content = content.replace("#vultype_img#",self.getImgContent(data['vultype_img']))
            if len(data['list']) > 0:
                for rowdata in data['list']:
                    content += vulItem.replace("#vul_family#",self.str2ascii(rowdata['vul_family'])).replace("#h_r#",rowdata['h_r']).replace("#m_r#",rowdata['m_r']).replace("#l_r#",rowdata['l_r']).replace("#t_r#",rowdata['t_r'])
                #end for
            else:
                content += vulEmpty
            #end if
            content += contentEnd
            
            return content
        except Exception,e:
            logging.getLogger().error("getRiskTypeContent(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getOsDisData(self):
        try:
            #logging.getLogger().debug("getOsDisData")
            list = []
            self.mysqlConnect()
            total = 0
            sql = ""
            if self.isCondReport:
                total = len(self.iplist.split(','))
                sql = "select count(h.id) as c , h.running_os as running_os from "+self.hostmsg_table+" h,"+self.task_summary_table+" t where h.ip = t.ip and t.status = '1' and t.id in ("+self.iplist+") group by `running_os`"
            else:
                self.cursor.execute("select count(id) as c from %s where `status` = '1'" % (self.task_summary_table))
                res = self.cursor.fetchone()
                if res and len(res) > 0:
                    total = res['c']
                else:
                    total = 0
                #end if
                sql = "select count(h.id) as c , h.running_os as running_os from "+self.hostmsg_table+" h,"+self.task_summary_table+" t where h.ip = t.ip and t.status = '1'  group by `running_os`"
            #end if
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            if res and len(res) > 0:
                all = 100.0
                allCount = total
                for row in res:
                    h_count = row['c']
                    os = row['running_os']
                    if not os or os == "":
                        continue
                    #end if
                    item = {"h_count":str(h_count),"os":os.encode('utf8'),"bl":str(h_count/total)}
                    all -= h_count/total
                    allCount -= h_count
                    list.append(item)
                #end for
                if all > 0:
                    item = {"h_count":str(allCount),"os":"--","bl":str(all)}
                    list.append(item)
                #end if
            #end if
            
            self.mysqlClose()
            
            return list
        except Exception,e:
            logging.getLogger().error("getOsDisData(RtfReport) exception:" + str(e))
            return []
        #end try
    #end def
    
    def getOsDisContent(self):
        try:
            if self.isCondReport and self.block[0] == '0':
                return ""
            #end if
            data = self.getOsDisData()
            #logging.getLogger().debug("getOsDisContent")
            
            content = "\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\lang2052\\b\\f1\\fs30\\'b2\\'d9\\'d7\\'f7\\'cf\\'b5\\'cd\\'b3\\'b7\\'d6\\'b2\\'bc\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\b0\\f1\\fs20\\'d6\\'f7\\'bb\\'fa\\'ca\\'fd\\'c1\\'bf\\lang1033\\f0\\nestcell\\lang2052\\f1\\'b2\\'d9\\'d7\\'f7\\'cf\\'b5\\'cd\\'b3\\lang1033\\f0\\nestcell\\lang2052\\f1\\'b1\\'c8\\'c0\\'fd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1134\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx7655\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            osItem = "\\pard\\intbl\\itap2\\nowidctlpar\\qc #h_count#\\nestcell #os#\\nestcell #bl#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            osItem += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1134\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx7655\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            
            osEmpty = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            osEmpty += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            contentEnd = "\\pard\\intbl\\nowidctlpar\\qj\\cell\\trowd\\trgaph108\\trleft-108\\cellx8748\\row\\pard\\nowidctlpar\\qj\\par\n"
            
            if len(data) > 0:
                for rowdata in data:
                    content += osItem.replace("#h_count#",rowdata['h_count']).replace("#os#",rowdata['os']).replace("#bl#",rowdata['bl'])
                #end for
            else:
                content += osEmpty
            #end if
            content += contentEnd
            
            return content
        except Exception,e:
            logging.getLogger().error("getOsDisContent(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getHostRiskData(self):
        try:
            #logging.getLogger().debug("getHostRiskData")
            
            list = []
            self.mysqlConnect()
            sql = ""
            if self.isCondReport:
                sql = "call createIpRiskTable("+self.task_id+",'"+self.iplist+"')"
            else:
                sql = "call createIpRiskTable("+self.task_id+",'')"
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
            self.cursor.execute("select * from tmp_iplist")
            res = self.cursor.fetchall()
            if res and len(res) > 0:
                for row in res:
                    if not row['ip'] or row['ip'] == '':
                        ip = "--"
                    else:
                        ip = row['ip'].encode('utf8')
                    #end if
                    if not row['os'] or row['os'] == '':
                        os = "--"
                    else:
                        os = row['os'].encode('utf8')
                    #end if
                    if not row['high']:
                        h_r = "0"
                    else:
                        h_r = str(row['high'])
                    #end if 
                    if not row['med']:
                        m_r = "0"
                    else:
                        m_r = str(row['med'])
                    #end if
                    if not row['low']:
                        l_r = 0
                    else:
                        l_r = row['low']
                    #end if
                    if not row['none']:
                        n_r = 0
                    else:
                        n_r = row['none']
                    #end if
                    l_r = l_r + n_r
                    l_r = str(l_r)
                    
                    item = {"ip":ip,"os":os,"h_r":h_r,"m_r":m_r,"l_r":l_r}
                    list.append(item)
                #end for
            #end if
            self.mysqlClose()
            
            return list
        except Exception,e:
            logging.getLogger().error("getHostRiskData(RtfReport) exception:" + str(e))
            return []
        #end try
    #end def
    
    def getHostRiskContent(self):
        try:
            data = self.getHostRiskData()
            #logging.getLogger().debug("getHostRiskContent")
            
            content = "\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\lang2052\\b\\f1\\fs30\\'d6\\'f7\\'bb\\'fa\\'b7\\'e7\\'cf\\'d5\\'b5\\'c8\\'bc\\'b6\\'c1\\'d0\\'b1\\'ed\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qc\\b0\\fs20 IP\\lang2052\\f1\\'b5\\'d8\\'d6\\'b7\\lang1033\\f0\\nestcell\\lang2052\\f1\\'b2\\'d9\\'d7\\'f7\\'cf\\'b5\\'cd\\'b3\\lang1033\\f0\\nestcell\\lang2052\\f1\\'b8\\'df\\'b7\\'e7\\'cf\\'d5\\lang1033\\f0\\nestcell\\lang2052\\f1\\'d6\\'d0\\'b7\\'e7\\'cf\\'d5\\lang1033\\f0\\nestcell\\lang2052\\f1\\'b5\\'cd\\'b7\\'e7\\'cf\\'d5\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1730\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx6096\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx6946\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx7797\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            ipItem = "\\pard\\intbl\\itap2\\nowidctlpar\\qc #ip#\\nestcell #os#\\nestcell #h_r#\\nestcell #m_r#\\nestcell #l_r#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            ipItem += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1730\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx6096\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx6946\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx7797\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            ipEmpty = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            ipEmpty += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            contentEnd = "\\pard\\intbl\\nowidctlpar\\qj\\cell\\trowd\\trgaph108\\trleft-108\\cellx8748\\row\\pard\\nowidctlpar\\qj\\par\n"
            
            if len(data) > 0:
                for rowdata in data:
                    content += ipItem.replace("#ip#",rowdata['ip']).replace("#os#",rowdata['os']).replace("#h_r#",rowdata['h_r']).replace("#m_r#",rowdata['m_r']).replace("#l_r#",rowdata['l_r'])
                #end for
            else:
                content += ipEmpty
            #end if 
            content += contentEnd
            
            return content
        except Exception,e:
            logging.getLogger().error("getHostRiskContent(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def getVulDisData(self):
        try:
            #logging.getLogger().debug("getVulDisData")
            
            list = []
            self.mysqlConnect()
            sql = ""
            if self.isCondReport:
                sql = "call createVulDisTable("+self.task_id+",'"+self.iplist+"')"
            else:
                sql = "call createVulDisTable("+self.task_id+",'')"
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
            self.cursor.execute("select * from tmp_vuldis order by FIELD(level,'C','H','HIGH','M','MED','L','LOW','I')")
            res = self.cursor.fetchall()
            if res and len(res) > 0:
                for row in res:
                    vulname = ""
                    if row['vulname'] and row['vulname'] != "":
                        vulname = row['vulname'].strip()
                        vulname = vulname.encode('utf8')
                        #vulname = row['vulname'].encode('utf8')
                    #end if
                    proto = str(row['proto'])
                    port = str(row['port'])
                    if proto != "" and port != "" and vulname != "":
                        vulname += "[" + proto + ":" + port + "]"
                    #end if
                    count = ''
                    if self.isCondReport:
                        count = str(row['c'])
                    else:
                        count = str(len(row['list'].split('|')))
                    #end if
                    level = row['level'].encode('utf8')
                    
                    if self.isCondReport and self.block[1] == '0':
                        if level == 'C' or level == 'H' or level == 'M' or level == 'L' or level == 'I':
                            continue
                        #end if
                    #end if
                    if self.isCondReport and self.block[2] == '0':
                        if level == 'HIGH' or level == 'MED' or level == 'LOW':
                            continue
                        #end if
                    #end if
                    if self.isCondReport and self.vullevel[0] == '0' and level == 'C':
                        continue
                    #end if
                    if self.isCondReport and self.vullevel[1] == '0':
                        if level == 'H' or level == 'HIGH':
                            continue
                        #end if
                    #end if
                    if self.isCondReport and self.vullevel[2] == '0':
                        if level == 'M' or level == 'MED':
                            continue
                        #end if
                    #end if
                    if self.isCondReport and self.vullevel[3] == '0':
                        if level == 'L' or level == 'LOW':
                            continue
                        #end if
                    #end if
                    if self.isCondReport and self.vullevel[4] == '0' and level == 'I':
                        continue
                    #end if
                    
                    if level == "C":
                        level = self.c_level_str
                    elif level == "H" or level == "HIGH":
                        level = self.h_level_str
                    elif level == "M" or level == "MED":
                        level = self.m_level_str
                    elif level == "L" or level == "LOW":
                        level = self.l_level_str
                    else:
                        level = self.n_level_str
                    #end if
                    
                    item = {"vulname":vulname,"count":count,"level":level}
                    list.append(item)
                #end for
            #end if
            self.mysqlClose()
            
            return list
        except Exception,e:
            logging.getLogger().error("getVulDisData(RtfReport) exception:" + str(e))
            return []
        #end try
    #end def
    
    def getVulDisContent(self):
        try:
            if self.isCondReport and self.block[1] == '0' and self.block[2] == '0':
                return ""
            #end if
            data = self.getVulDisData()
            #logging.getLogger().debug("getVulDisContent")
            
            content = "\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\lang2052\\b\\f1\\fs30\\'c2\\'a9\\'b6\\'b4\\'b7\\'d6\\'b2\\'bc\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\b0\\f1\\fs20\\'c2\\'a9\\'b6\\'b4\\'c3\\'fb\\'b3\\'c6\\lang1033\\f0\\nestcell\\lang2052\\f1\\'b3\\'f6\\'cf\\'d6\\'b4\\'ce\\'ca\\'fd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            content += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx7513\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            vulItem = "\\pard\\intbl\\itap2\\nowidctlpar #vulname#\\nestcell\\pard\\intbl\\itap2\\nowidctlpar\\qc #count#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            vulItem += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx7513\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            vulEmpty = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            vulEmpty += "\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8630\\nestrow}{\\nonesttables\\par}\n"
            
            contentEnd = "\\pard\\intbl\\nowidctlpar\\qj\\cell\\trowd\\trgaph108\\trleft-108\\cellx8748\\row\\pard\\nowidctlpar\\qj\\par\n"
            
            if len(data) > 0:
                for rowdata in data:
                    content += vulItem.replace("#vulname#",rowdata['level']+self.str2ascii(rowdata['vulname'])).replace("#count#",rowdata['count'])
                #end for
            else:
                content += vulEmpty
            #end if
            content += contentEnd
            
            return content
        except Exception,e:
            logging.getLogger().error("getVulDisContent(RtfReport) exception:" + str(e))
            return ""
    #end def
    
    def getVulDetailData(self):
        try:
            #logging.getLogger().debug("getVulDisContent")
            
            hostlist = []
            weblist = []
            
            self.mysqlConnect()
            
            ipTotalArray = []
            if self.isCondReport:
                self.cursor.execute("select ip from "+self.task_summary_table+" where id in ("+self.iplist+")")
                res = self.cursor.fetchall()
                for row in res:
                    ipTotalArray.append(row['ip'].encode('utf8'))
                #end for
            #end if
            
            if self.isCondReport == False or self.block[1] == '1':
                self.cursor.execute("select h.vul_name as `vulname`,h.risk_factor as `level`,h.ip_list as `ip_list`,v.cve as `cve`,v.desc as `desc`,v.solution as `solu`,v.ref as `ref` from %s h,%s v where h.vul_id=v.vul_id group by h.vul_name order by FIELD(h.risk_factor,'C','H','HIGH','M','MED','L','LOW','I')" % (self.host_vul_table,self.vul_details_table))
                res = self.cursor.fetchall()
                if res and len(res) > 0:
                    for row in res:
                        vulname = row['vulname'].strip()
                        vulname = vulname.encode('utf8')
                        level = row['level'].strip()
                        level = level.encode('utf8')
                        if self.isCondReport and self.vullevel[0] == '0' and level == 'C':
                            continue
                        #end if
                        if self.isCondReport and self.vullevel[1] == '0' and level == 'H':
                            continue
                        #end if
                        if self.isCondReport and self.vullevel[2] == '0' and level == 'M':
                            continue
                        #end if
                        if self.isCondReport and self.vullevel[3] == '0' and level == 'L':
                            continue
                        #end if
                        if self.isCondReport and self.vullevel[4] == '0' and level == 'I':
                            continue
                        #end if
                        if level == "C":
                            level = self.c_level_str
                        elif level == "H" or level == "HIGH":
                            level = self.h_level_str
                        elif level == "M" or level == "MED":
                            level = self.m_level_str
                        elif level == "L" or level == "LOW":
                            level = self.l_level_str
                        else:
                            level = self.n_level_str
                        #end if
                        ip_list = row['ip_list'].strip()
                        ip_list = ip_list.encode('utf8')
                        if self.isCondReport:
                            array = ip_list.split('|')
                            ip_list = ''
                            for array_item in array:
                                if array_item in ipTotalArray:
                                    ip_list += array_item + "|"
                                #end if
                            #end for
                            if ip_list == '':
                                continue
                            else:
                                ip_list = ip_list[0:-1]
                            #end if
                        #end if
                        cve = row['cve'].strip()
                        cve = cve.replace("\r\n","\n")
                        cve = cve.encode('utf8')
                        desc = row['desc'].strip()
                        desc = desc.replace("\r\n","\n")
                        desc = desc.encode('utf8')
                        solu = row['solu'].strip()
                        solu = solu.replace("\r\n","\n")
                        solu = solu.encode('utf8')
                        ref = row['ref'].strip()
                        ref = ref.replace("\r\n","\n")
                        ref = ref.encode('utf8')
                        count = str(len(ip_list.split("|")))
                        ip_list = ip_list.replace("|"," , ")
                        item = {"vulname":vulname,"count":count,"ip_list":ip_list,"desc":desc,"solu":solu,"cve":cve,"ref":ref,"level":level}
                        hostlist.append(item)
                    #end for
                #end if
            #end if
            
            if self.isCondReport == False or self.block[2] == '1':
                sql = ""
                if self.isCondReport:
                    sql = "select `vul_type` as `vulname`,`url`,`level`,`detail` as `desc` from "+self.scan_result_table+" s,"+self.task_summary_table+" t where s.ip=t.ip and t.id in ("+self.iplist+") order by FIELD(`level`,'HIGH','MED','LOW')"
                else:
                    sql = "select `vul_type` as `vulname`,`url`,`level`,`detail` as `desc` from %s " % (self.scan_result_table)
                #end if
                self.cursor.execute(sql)
                res = self.cursor.fetchall()
                if res and len(res) > 0:
                    for row in res:
                        vulname = row['vulname'].encode('utf8')
                        url = row['url'].encode('utf8')
                        level = row['level'].encode('utf8')
                        if self.isCondReport and level == 'HIGH' and self.vullevel[1] == '0':
                            continue
                        #end if
                        if self.isCondReport and level == 'MED' and self.vullevel[2] == '0':
                            continue
                        #end if
                        if self.isCondReport and level == 'LOW' and self.vullevel[3] == '0':
                            continue
                        #end if
                        if level == "C":
                            level = self.c_level_str
                        elif level == "H" or level == "HIGH":
                            level = self.h_level_str
                        elif level == "M" or level == "MED":
                            level = self.m_level_str
                        elif level == "L" or level == "LOW":
                            level = self.l_level_str
                        else:
                            level = self.n_level_str
                        #end if
                        desc = row['desc'].encode('utf8')
                        desc = desc.replace("\r\n","\n")
                        item = {"vulname":vulname,"url":url,"level":level,"desc":desc}
                        weblist.append(item)
                    #end for
                #end if
            #end if
            
            data = {"hostlist":hostlist,"weblist":weblist}
            self.mysqlClose()
            
            return data
        except Exception,e:
            logging.getLogger().error("getVulDetailData(RtfReport) exception:" + str(e))
            data = {"hostlist":[],"weblist":[]}
            return data
        #end try
    #end def
    
    def getVulDetailContent(self):
        try:
            if self.isCondReport and self.block[1] == '0' and self.block[2] == '0':
                return ""
            #end if
            
            data = self.getVulDetailData()
            #logging.getLogger().debug("getVulDetailContent")
            
            content = ""
            
            huiche_content = "\\par\n"
            
            hostcontentStart = "\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostcontentStart += "\\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\lang2052\\b\\f1\\fs30\\'d6\\'f7\\'bb\\'fa\\'c2\\'a9\\'b6\\'b4\\'cf\\'ea\\'cf\\'b8\\'d0\\'c5\\'cf\\'a2\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            hostItem = "\\cellx8748\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\b0\\f1\\fs20\\'c2\\'a9\\'b6\\'b4\\'c3\\'fb\\'b3\\'c6\\lang1033\\f0\\nestcell #vulname#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\f1\\'b3\\'f6\\'cf\\'d6\\'b4\\'ce\\'ca\\'fd\\lang1033\\f0\\nestcell #count#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\f1\\'ca\\'dc\\'d3\\'b0\\'cf\\'ec\\'d6\\'f7\\'bb\\'fa\\lang1033\\f0\\nestcell #ip_list#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n" 
            hostItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\f1\\'ce\\'a3\\'cf\\'d5\\'b5\\'c8\\'bc\\'b6\\lang1033\\f0\\nestcell #level#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\f1\\'cf\\'ea\\'cf\\'b8\\'c3\\'e8\\'ca\\'f6\\lang1033\\f0\\nestcell #desc#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\f1\\'bd\\'e2\\'be\\'f6\\'b0\\'ec\\'b7\\'a8\\lang1033\\f0\\nestcell #solu#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj CVE\\lang2052\\f1\\'b1\\'e0\\'ba\\'c5\\lang1033\\f0\\nestcell #cve#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\f1\\'b2\\'ce\\'bf\\'bc\\lang1033\\f0\\nestcell #ref#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            hostItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostItem += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            
            hostEmpty = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostEmpty += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            hostEmpty += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\fs20\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            hostEmpty += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            
            hostcontentEnd = "\\pard\\intbl\\nowidctlpar\\qj\\cell\\trowd\\trgaph108\\trleft-108\\cellx8748\\row\\pard\\nowidctlpar\\qj\\par\n"
            
            
            webcontentStart = "\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webcontentStart += "\\cellx8748\\pard\\intbl\\nowidctlpar\\qj\\lang2052\\b\\f1\\fs30Web\\'c2\\'a9\\'b6\\'b4\\'cf\\'ea\\'cf\\'b8\\'d0\\'c5\\'cf\\'a2\\lang1033\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            
            webItem = "\\cellx8748\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\b0\\f1\\fs20\\'c2\\'a9\\'b6\\'b4\\'c3\\'fb\\'b3\\'c6\\lang1033\\f0\\nestcell #vulname#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            webItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj URL\\nestcell #url#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            webItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\f1\\'ce\\'a3\\'cf\\'d5\\'b5\\'c8\\'bc\\'b6\\lang1033\\f0\\nestcell #level#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            webItem += "\\pard\\intbl\\itap3\\nowidctlpar\\qj\\lang2052\\f1\\'c3\\'e8\\'ca\\'f6\\lang1033\\f0\\nestcell #desc#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1305\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            webItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            webItem += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webItem += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            
            webEmpty = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\fs18\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webEmpty += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            webEmpty += "\\pard\\intbl\\itap2\\nowidctlpar\\qj\\fs20\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            webEmpty += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            
            webcontentEnd = "\\pard\\intbl\\nowidctlpar\\qj\\cell\\trowd\\trgaph108\\trleft-108\\cellx8748\\row\\pard\\nowidctlpar\\qj\\par\n" 
            
            hostlist = data['hostlist']
            weblist = data['weblist']
            
            if self.isCondReport == False or self.block[1] == '1':
                content += hostcontentStart
                if len(hostlist) > 0:
                    for rowdata in hostlist:
                        content += hostItem.replace("#vulname#",self.str2ascii(rowdata['vulname'])).replace("#count#",rowdata['count']).replace("#ip_list#",rowdata['ip_list']).replace("#level#",rowdata['level']).replace("#desc#",self.str2ascii(rowdata['desc'])).replace("#solu#",self.str2ascii(rowdata['solu'])).replace("#cve#",self.str2ascii(rowdata['cve'])).replace("#ref#",self.str2ascii(rowdata['ref']))
                    #end for
                else:
                    content += hostEmpty
                #end if
                content += hostcontentEnd
                content += huiche_content + huiche_content
            #end if
            
            if self.isCondReport == False or self.block[2] == '1':
                content += webcontentStart
                if len(weblist) > 0:
                    for rowdata in weblist:
                        content += webItem.replace("#vulname#",self.str2ascii(rowdata['vulname'])).replace("#url#", self.str2ascii(rowdata['url'])).replace("#level#",rowdata['level']).replace("#desc#",self.str2ascii(rowdata['desc']))
                    #end for
                else:
                    content += webEmpty
                #end if
                content += webcontentEnd
            #end if
            
            return content
        except Exception,e:
            logging.getLogger().error("getVulDetailContent(RtfReport) exception:" + str(e))
            return ""
    #end def
    
    def getWeakPwdData(self):
        try:
            #logging.getLogger().debug("getWeakPwdData")
            
            total = []
            vullist = ["ftp","ssh","3389","telnet","mssql","mysql","oracle","smb","vnc"]
            self.mysqlConnect()
            for vul in vullist:
                if self.isCondReport and self.weaklist[0] == '0' and vul == 'ftp':
                    continue
                #end if
                if self.isCondReport and self.weaklist[1] == '0' and vul == 'ssh':
                    continue
                #end if
                if self.isCondReport and self.weaklist[2] == '0' and vul == '3389':
                    continue
                #end if
                if self.isCondReport and self.weaklist[3] == '0' and vul == 'telnet':
                    continue
                #end if
                if self.isCondReport and self.weaklist[4] == '0' and vul == 'mssql':
                    continue
                #end if
                if self.isCondReport and self.weaklist[5] == '0' and vul == 'mysql':
                    continue
                #end if
                if self.isCondReport and self.weaklist[6] == '0' and vul == 'oracle':
                    continue
                #end if
                if self.isCondReport and self.weaklist[7] == '0' and vul == 'smb':
                    continue
                #end if
                if self.isCondReport and self.weaklist[8] == '0' and vul == 'vnc':
                    continue
                #end if
                    
                mylist = []
                self.cursor.execute("select `username`,`password` from %s where `type` = '%s' group by concat(username,password)" % (self.weak_pwd_details_table,vul))
                res = self.cursor.fetchall()
                if res and len(res) > 0:
                    for row in res:
                        username = row['username']
                        password = row['password']
                        ip = ""
                        
                        sql = "select ip from " + self.weak_pwd_details_table + " where `type` = %s and `username` = %s and `password` = %s "
                        self.cursor.execute(sql,(vul,username,password))
                        result = self.cursor.fetchall()
                        if len(result) > 0:
                            for result_item in result:
                                ip += result_item['ip'] + ","
                            #end for
                            ip = ip[0:-1]
                        #end if
                        mylist_item = {"ip":ip,"username":username,"password":password}
                        mylist.append(mylist_item)
                    #end for
                #end if
                item = {"type":vul,"list":mylist}
                total.append(item)
            #end for
            self.mysqlClose()
            
            
            return total
            
        except Exception,e:
            logging.getLogger().error("getWeakPwdData(RtfReport) exception:" + str(e))
            return []
        #end try
    #end def

    def getWeakPwdContent(self):
        try:
            if self.isCondReport and self.block[3] == '0':
                return ""
            #end if
            data = self.getWeakPwdData()
            #logging.getLogger().debug("getWeakPwdContent")
            
            content = ""

            contentStart = "\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            contentStart += "\\cellx8748\\pard\\intbl\\nowidctlpar\\lang2052\\b\\f1\\fs30\\'b4\\'e0\\'c8\\'f5\\'d5\\'cb\\'ba\\'c5\\lang1033\\b0\\f0\\cell\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"

            weakItemStart = "\\cellx8748\\pard\\intbl\\itap2\\nowidctlpar\\fs24 \\b#type#\\b0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3"
            weakItemStart += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"

            weakItemRow = "\\pard\\intbl\\itap3\\nowidctlpar\\lang2052\\f1\\'d3\\'c3\\'bb\\'a7\\'c3\\'fb\\lang1033\\f0\\nestcell #username#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemRow += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1447\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            weakItemRow += "\\pard\\intbl\\itap3\\nowidctlpar\\lang2052\\f1\\'c3\\'dc\\'c2\\'eb\\lang1033\\f0\\nestcell #password#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemRow += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1447\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            weakItemRow += "\\pard\\intbl\\itap3\\nowidctlpar\\lang2052\\f1\\'ca\\'dc\\'d3\\'b0\\'cf\\'ec\\'b5\\'c4\\lang1033\\f0 IP\\nestcell #ip#\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trleft5\\trbrdrl\\brdrs\\brdrw10 \\trbrdrt\\brdrs\\brdrw10 \\trbrdrr\\brdrs\\brdrw10 \\trbrdrb\\brdrs\\brdrw10 \\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemRow += "\\clcbpat2\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx1447\\clbrdrl\\brdrw10\\brdrs\\clbrdrt\\brdrw10\\brdrs\\clbrdrr\\brdrw10\\brdrs\\clbrdrb\\brdrw10\\brdrs \\cellx8399\\nestrow}{\\nonesttables\\par}\n"
            weakItemRow += "\\pard\\intbl\\itap2\\nowidctlpar\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemRow += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            weakItemRow += "\\pard\\intbl\\itap2\\nowidctlpar\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemRow += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"

            #weakItemEmpty = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\f1\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\f0\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            #weakItemEmpty += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            weakItemEmpty = "\\pard\\intbl\\itap2\\nowidctlpar\\qc\\lang2052\\b0\\f1\\fs20\\'c3\\'bb\\'d3\\'d0\\'ca\\'fd\\'be\\'dd\\lang1033\\b\\f0\\fs24\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemEmpty += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"
            weakItemEmpty += "\\pard\\intbl\\itap2\\nowidctlpar\\nestcell{\\*\\nesttableprops\\trowd\\trgaph108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemEmpty += "\\cellx8625\\nestrow}{\\nonesttables\\par}\n"

            weakItemEnd = "\\pard\\intbl\\nowidctlpar\\cell\\trowd\\trgaph108\\trleft-108\\cellx8748\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            weakItemEnd += "\\cellx8748\\pard\\intbl\\nowidctlpar\\cell\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"

            contentEnd = "\\pard\\intbl\\nowidctlpar\\cell\\trowd\\trgaph108\\trleft-108\\cellx8748\\row\\trowd\\trgaph108\\trleft-108\\trpaddl108\\trpaddr108\\trpaddfl3\\trpaddfr3\n"
            contentEnd += "\\cellx8748\\pard\\intbl\\nowidctlpar\\cell\\row\\pard\\nowidctlpar\\par\n"
            
            if len(data) > 0:
                content += contentStart
                for rowdata in data:
                    type = rowdata['type']
                    content += weakItemStart.replace("#type#",self.str2ascii(type))
                    
                    #list = rowdata['list']
                    if len(rowdata['list']) > 0:
                        for row in rowdata['list']:
                            username = row['username']
                            password = row['password']
                            ip = row['ip']

                            #content += weakItemRow
                            content += weakItemRow.replace("#username#",username).replace("#password#",password).replace("#ip#",ip)
                        #end for
                    else:
                        content += weakItemEmpty
                    #end if
                    
                    content += weakItemEnd
                #end for
                content += contentEnd
            #end if
            
            return content
        except Exception,e:
            logging.getLogger().error("getWeakPwdContent(RtfReport) exception:" + str(e))
            return ""
        #end try
    #end def
    
    def main(self):
        content = []
        try:
            templist = self.getTemp()
            if templist and len(templist) > 0:
                for row in templist:
                    if row.find("#headercontent#") >= 0:
                        content.append(row.replace("#headercontent#",self.getHeaderContent()))
                    elif row.find("#reviewcontent#") >= 0:
                        content.append(row.replace("#reviewcontent#",self.getReviewContent()))
                    elif row.find("#risktypecontent#") >= 0:
                        content.append(row.replace("#risktypecontent#",self.getRiskTypeContent()))
                    elif row.find("#osdiscontent#") >= 0:
                        content.append(row.replace("#osdiscontent#",self.getOsDisContent()))
                    elif row.find("#hostriskcontent#") >= 0:
                        content.append(row.replace("#hostriskcontent#",self.getHostRiskContent()))
                    elif row.find("#vuldiscontent#") >= 0:
                        content.append(row.replace("#vuldiscontent#",self.getVulDisContent()))
                    elif row.find("#vuldetailcontent#") >= 0:
                        content.append(row.replace("#vuldetailcontent#",self.getVulDetailContent()))
                    elif row.find("#weakpwdcontent#") >= 0:
                        content.append(row.replace("#weakpwdcontent#",self.getWeakPwdContent()))
                    else:
                        content.append(row)
                    #end if
                #end for
            #end if
            return content
        except Exception,e:
            logging.getLogger().error("main(RtfReport) exception:" + str(e))
            return content
        #end try
    #end def
    
    def main_ip(self,ip):
        content = []
        try:
            templist = self.getTemp_ip()
            if templist and len(templist) > 0:
                for row in templist:
                    if row.find("#headercontent#") >= 0:
                        #print "headercontent"
                        #print self.getHeaderContent_ip(ip)
                        content.append(row.replace("#headercontent#",self.getHeaderContent_ip(ip)))
                    elif row.find("#reviewcontent#") >= 0:
                        #print "reviewcontent"
                        content.append(row.replace("#reviewcontent#",self.getReviewContent_ip(ip)))
                    elif row.find("#portcontent#") >= 0:
                        #print "portcontent"
                        content.append(row.replace("#portcontent#",self.getPortContent_ip(ip)))
                    elif row.find("#webcontent#") >= 0:
                        #print "webcontent"
                        content.append(row.replace("#webcontent#",self.getWebVulContent_ip(ip)))
                    elif row.find("#hostcontent#") >= 0:
                        #print "hostcontent"
                        content.append(row.replace("#hostcontent#",self.getHostVulContent_ip(ip)))
                    elif row.find("#weakcontent#") >= 0:
                        #print "weakcontent"
                        content.append(row.replace("#weakcontent#",self.getWeakVulContent_ip(ip)))
                    else:
                        content.append(row)
                    #end if
                #end for
            #end if
            return content
        except Exception,e:
            logging.getLogger().error("main_ip(RtfReport) exception:" + str(e))
            return content
        #end try
    #end def
    
    def test2(self):
        try:
            import httplib
            import urllib
            import urllib2
            
            value = {'task_id':self.task_id}
            req = urllib2.Request("https://127.0.0.1/html/autoreport/createimg",urllib.urlencode(value))
            res = urllib2.urlopen( req )
            html = res.read()
            res.close()
            #print html
        except Exception,e:
            logging.getLogger().error("createImg(RtfReport) exception:" + str(e))
        #end try
    #end def
    
#end class

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        report_id = str(int(sys.argv[1]))

        rtf_report = RtfReport(report_id)
        rtf_report.createReport()
        #rtf_report.writeRtf()
        #rtf_report.writeRtf_ip("192.168.9.4","/var/www/Report/default/")
        
    except Exception,e:
        logging.getLogger().error("__name__ Exception(VpnManage):" + str(e))   
    #end try
#end __main__
