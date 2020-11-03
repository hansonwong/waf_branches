#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telnetlib import Telnet

class Telnet_login:
    def __init__(self,host,port=23):
        self.host = host;
        self.port = port
        self.timeout = 20
        self.prompt = "\w+:"
        self.errmsg = ""

        self.geterrormsg()
        self.err_dict = ['incorrect','retry','error','failed','fail']
        self.suc_dict = ['welcome', 'success']

    def connect(self):
        return Telnet(self.host,self.port)

    def geterrormsg(self):
        try:
            errUser = 'null111'
            errPass = 'n1l1u1l'
            errfp = self.connect()
            errfp.set_debuglevel(1)
            _, _, banner = errfp.expect([self.prompt], timeout=self.timeout)
            errfp.write(errUser+'\r\n')
            _, _, passwdinfo = errfp.expect([self.prompt], timeout=self.timeout)
            errfp.write(errPass+'\r\n')
            _, _, self.errmsg = errfp.expect([self.prompt,'#','\$'], timeout=self.timeout)
            self.errmsg = self.errmsg.replace(errUser,'').replace('*'*len(errPass),'').strip()
            errfp.close()
        except Exception:
            self.errmsg = ""


    def check(self,User,Passwd):
        try:
            # print User,Passwd

            loginfp = self.connect()
            loginfp.set_debuglevel(1)
            _, _, banner = loginfp.expect([self.prompt], timeout=self.timeout)
            # print banner
            # print '--------------------------'
            loginfp.write(User+'\r')
            _, _, passwdinfo = loginfp.expect([self.prompt], timeout=self.timeout)
            # print passwdinfo
            # print '--------------------------'
            #print 'passwdinfo:'+passwdinfo.replace(User,'').strip()
            if passwdinfo.replace(User,'').strip() == self.errmsg:
                # print 'strip'
                return False
            loginfp.write(Passwd+'\r')
            login_index, _, loginmsg = loginfp.expect([self.prompt,'#','\$'], timeout=self.timeout)
            # print loginmsg
            # print '--------------------------'
            loginmsg = loginmsg.replace(User,'').strip()
            loginfp.close()
            # print 'loginmsg'+loginmsg
            # print 'errmsg'+self.errmsg
            # print 'Begin to check  err_dict', self.err_dict
            for item in self.err_dict:
                if item in  loginmsg.lower():
                    return False

            # print 'Begin to check suc_dict', self.suc_dict
            for suc in self.suc_dict:
                if suc in loginmsg.lower():
                    return True

            if self.errmsg != '' and loginmsg != self.errmsg:
                return True
            else:
                return False
        except Exception:
            return False


if __name__ == '__main__':
    t = Telnet_login('192.168.9.161')
    print t.check('administrator','123456')
    t = Telnet_login('220.130.128.192')
    print t.check('root','')
    # print t.check('root','')
    # print t.check('admin','admin')

