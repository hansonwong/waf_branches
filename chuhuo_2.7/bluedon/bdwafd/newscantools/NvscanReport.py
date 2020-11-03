#!/usr/bin/python
#-*-encoding:UTF-8-*-
import logging
import re

class NvscanReport:
    
    def __init__(self):
        try:
            self.ip = ""
            self.filename = ""
            self.hostinfo = None
            self.hostport = None
            self.hostvul = None
            self.result = {}
            
        except Exception,e:
            logging.getLogger().error("File:NvscanReport.py, NvscanReport.__init__:%s, ip:%s, filename:%s" % (str(e),self.ip,self.filename))
        #end try    
    #end def
    
    '''
    def startProcess(self,ip,filename):
        try:
            self.ip = ip
            self.filename = filename
            content = self.getContent()
            
            self.hostinfo = self.hostinfoFun(content)
            self.hostport = self.hostportFun(content)
            self.hostvul = self.hostvulFun(content)
            
        except Exception,e:
            logging.getLogger().error("File:NvscanReport.py, NvscanReport.startProcess:%s, ip:%s, filename:%s" % (str(e),self.ip,self.filename))
        #end try
    #end def
    '''
    
    def startProcess(self, content):
        try:
            
            self.hostinfoFun(content)
            self.hostportFun(content)
            self.hostvulFun(content)
            
        except Exception,e:
            logging.getLogger().error("File:NvscanReport.py, NvscanReport.startProcess:%s" % (str(e)))
        #end try
    #end def
    
    def getResult(self):
        return self.result
    #end def
    
    def gethostinfo(self):
        hostinfo = []
        
        if self.result and len(self.result.keys()) > 0:
            for ip in self.result.keys():
                if self.result[ip].has_key('info') and len(self.result[ip]['info'].keys()) > 0:
                    hostinfo.append(self.result[ip]['info'])
                #end if
            #end for
        #end if
        
        return hostinfo
    #end def
    
    def gethostport(self):
        hostport = []
        
        if self.result and len(self.result.keys()) > 0:
            for ip in self.result.keys():
                if self.result[ip].has_key('port') and self.result[ip]['port'] and len(self.result[ip]['port']) > 0: 
                    hostport.extend(self.result[ip]['port'])
                #end if
            #end for
        #end if
        
        return hostport
    #end def
    
    def gethostvul(self):
        hostvul = []
        
        if self.result and len(self.result.keys()) > 0:
            for ip in self.result.keys():
                if self.result[ip].has_key('vul') and self.result[ip]['vul'] and len(self.result[ip]['vul']) > 0: 
                    hostvul.extend(self.result[ip]['vul'])
                #end if
            #end for
        #end if
        
        return hostvul
    #end def
    
    def hostinfoFun(self, content):
        try:
            lines = content.split("\n")
            
            netbios_name = ""
            ip = ""
            mac_address = ""
            os = ""
            flag = False
            i = 0
            for row in lines:
                i += 1
                if row.find("<![endif]]]-->Host Information</h2>") >= 0:
                    flag = True
                #end if
                if flag and row.find("</table>") >= 0:
                    if self.result.has_key(ip):
                        pass
                    else:
                        self.result[ip] = {'info':{},'port':[],'vul':[]}
                    #end if
                    self.result[ip]['info'] = {"netbios_name":netbios_name,"ip":ip,"mac_address":mac_address,"os":os}
                        
                    netbios_name = ""
                    ip = ""
                    mac_address = ""
                    os = ""
                    flag = False
                #end if
                
                if flag:
                    if row.find("Netbios Name:</span>") > 0:
                        match = re.findall(r"<span(.+?)>(.+?)</span>",lines[i],re.I)
                        if match and len(match) > 0:
                            netbios_name = match[0][1]
                        #end if
                    elif row.find("IP:</span>") > 0:
                        match = re.findall(r"<span(.+?)>(.+?)</span>",lines[i],re.I)
                        if match and len(match) > 0:
                            ip = match[0][1]
                        #end if
                    elif row.find("MAC Address:</span>") > 0:
                        match = re.findall(r"<span(.+?)>(.+?)</span>",lines[i],re.I)
                        if match and len(match) > 0:
                            mac_address = match[0][1]
                        #end if
                    elif row.find("OS:</span>") > 0:
                        match = re.findall(r"<span(.+?)>(.+?)</span>",lines[i],re.I)
                        if match and len(match) > 0:
                            os = match[0][1]
                        #end if
                    #end if
                #end if
            #end for
            
        except Exception,e:
            logging.getLogger().error("File:NvscanReport.py, NvscanReport.hostinfoFun:%s" % (str(e)))
        #end try
    #end def
    
    def hostportFun(self, content):
        try:
            lines = content.split("\n")
            
            ip = ""
            flag = False
            i = 0
            for row in lines:
                i += 1
                if row.find("<![endif]]]-->Host Information</h2>") >= 0:
                    flag = True
                    ip = ""
                #end if
                
                if flag:
                    if row.find("<td width=\"20%\" valign=\"top\" class=\"classcell\"><span class=\"classtext\" style=\"color: #263645; font-weight: normal;\">IP:</span></td>") >= 0:
                        match = re.findall(r"<span(.+?)>(.+?)</span>",lines[i],re.I)
                        if match and len(match) > 0:
                            ip = match[0][1]
                        #end if
                    #end if
                    if not ip.strip():  #fix bug 3889
                        continue
                    #end if 
                    if row.find("<h2 xmlns=\"\" class=\"classsubsection \">") >= 0:
                        t = row.replace("<h2 xmlns=\"\" class=\"classsubsection \">","").replace("</h2>","").split("/")
                        port = t[0]
                        proto = t[1]
                        if port == "0":
                            continue
                        #end if
                        
                        if self.result.has_key(ip):
                            pass
                        else:
                            self.result[ip] = {'info':{},'port':[],'vul':[]}
                        #end if
                        self.result[ip]['port'].append({"ip":ip,"port":port,"proto":proto})
                    #end if
                #end if
            #end for
            
        except Exception,e:
            logging.getLogger().error("File:NvscanReport.py, NvscanReport.hostport:%s" % (str(e)))
        #end try
    #end def
    
    def vulaction(self,list):
        try:
            vulid = False
            vulname = False
            
            m = re.findall(r"<h2 xmlns=\"\" class=\"classsection([0-9]*)\" id=\"([a-z0-9]+)\">([0-9]{1,10})(\s+)(.+?)(\s+)\-(\s+)(.+?)</h2>",list[0],re.I|re.DOTALL)
            if m and len(m) > 0:
                vulid = m[0][2]
                vulname = m[0][7]
            else:
                return False
            #end if
            
            i = 0
            for row in list:
                i += 1
                #hosts
                if row.find("<h2 xmlns=\"\" class=\"classh2\" style=\"color:") >= 0:
                    m = re.findall(r"<h2 xmlns=\"\" class=\"classh2\" style=\"color: (.+?)\">(.+?)(\s+)\((tcp|udp)\/([0-9]+)\)</h2>",row,re.I|re.DOTALL)
                    if m and len(m) > 0:
                        ip = m[0][1]
                        proto = m[0][3]
                        port = m[0][4]
                        output = ""
                        if i < len(list):
                            m = re.findall(r"<span xmlns=\"\" class=\"classpre\">(.+?)</span>",list[i],re.I|re.DOTALL)
                            if m and len(m) > 0:
                                output = m[0].replace("<br>","\n")
                            #end if
                        #end if
                        
                        if self.result.has_key(ip):
                            pass
                        else:
                            self.result[ip] = {'info':{},'port':[],'vul':[]}
                        #end if
                        
                        self.result[ip]['vul'].append({"vulid":vulid,"vulname":vulname,"ip":ip,"port":port,"proto":proto,"output":output})
                        
                    #end if
                #end if
            #end for
            
        except Exception,e:
            logging.getLogger().error("File:NvscanReport.py, NvscanReport.vulaction:%s" % (str(e)))
        #end try
    #end def
    
    def hostvulFun(self, content):
        try:
            match = re.findall(r"<h1 xmlns=\"\" class=\"classchapter\" id=\"([a-z0-9]+)\">Vulnerabilities By Plugin</h1>(.+?)<h1 xmlns=\"\" class=\"classchapter\" id=\"([a-z0-9]+)\">Hosts Summary",content,re.I|re.DOTALL|re.M)
            if match and len(match) > 0:
                text = match[0][1]
                lines = text.split("\n")
                ll = []
                for row in lines:
                    m = re.findall(r"<h2 xmlns=\"\" class=\"classsection([0-9]*)\" id=\"([a-z0-9]+)\">(.+?)</h2>",row,re.I|re.DOTALL)
                    if m and len(m) > 0:
                        m_str = "<h2 xmlns=\"\" class=\"classsection%s\" id=\"%s\">%s</h2>" % (m[0][0],m[0][1],m[0][2])
                        ll.append(row.replace(m_str,""))
                        self.vulaction(ll)
                        ll = []
                        ll.append(m_str)
                    else:
                        ll.append(row) 
                    #end if
                #end for
                if ll and len(ll) > 0:
                    self.vulaction(ll)
                #end if
            #end if
            
        except Exception,e:
            logging.getLogger().error("File:NvscanReport.py, NvscanReport.hostvulFun:%s" % (str(e)))
        #end try
    #end def
    
    def getContent(self):
        try:
            path = "%s" % (self.filename)
            f = file(path, "r+")
            lines = f.readlines()
            f.close()
            
            return "".join(lines)
        except Exception,e:
            logging.getLogger().error("File:NvscanReport.py, NvscanReport.getContent:%s, filename:%s" % (str(e),self.filename))
            return ""
        #end try
    #end def
#end class




