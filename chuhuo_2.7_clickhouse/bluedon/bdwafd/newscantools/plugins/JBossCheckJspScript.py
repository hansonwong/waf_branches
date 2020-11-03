#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]
        detail = u""                                    
        detail = detail.encode('utf8')
        domain=ob['domain']
        url="zecmd/zecmd.jsp"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)        
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("<HTML><BODY> <FORM METHOD=\"GET\" NAME=\"comments\" ACTION=\"\"> <INPUT TYPE=\"text\" NAME=\"comment\"> <INPUT TYPE=\"submit\" VALUE=\"Send\"> </FORM> <pre>  </pre> </BODY></HTML>")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
        else:
            url1="idssvc/idssvc.jsp"
            geturl1="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url1)
            response1,content1=requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
            if content.find("<HTML><BODY> <FORM METHOD=\"GET\" NAME=\"comments\" ACTION=\"\"> <INPUT TYPE=\"text\" NAME=\"comment\"> <INPUT TYPE=\"submit\" VALUE=\"Send\"> </FORM> <pre>  </pre> </BODY></HTML>")>=0:
                request = getRequest(geturl1)
                response = getResponse(response)
                result.append(getRecord(ob,geturl1,ob['level'],detail,request,response))
            else:
                url2="wstats/wstats.jsp"
                geturl2="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url2)
                response1,content1=requestUrl(http,geturl2,ob['task_id'],ob['domain_id'])
                if content.find("<HTML><BODY> <FORM METHOD=\"GET\" NAME=\"comments\" ACTION=\"\"> <INPUT TYPE=\"text\" NAME=\"comment\"> <INPUT TYPE=\"submit\" VALUE=\"Send\"> </FORM> <pre>  </pre> </BODY></HTML>")>=0:
                    request = getRequest(geturl2)
                    response = getResponse(response)
                    result.append(getRecord(ob,geturl2,ob['level'],detail,request,response))
                else:
                    url2="iesvc/iesvc.jsp"
                    geturl2="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url2)
                    response1,content1=requestUrl(http,geturl2,ob['task_id'],ob['domain_id'])
                    if content.find("<HTML><BODY> <FORM METHOD=\"GET\" NAME=\"comments\" ACTION=\"\"> <INPUT TYPE=\"text\" NAME=\"comment\"> <INPUT TYPE=\"submit\" VALUE=\"Send\"> </FORM> <pre>  </pre> </BODY></HTML>")>=0:
                        request = getRequest(geturl2)
                        response = getResponse(response)
                        result.append(getRecord(ob,geturl2,ob['level'],detail,request,response))
                    else:
                        url2="invoker/invoker.jsp"
                        geturl2="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url2)
                        response1,content1=requestUrl(http,geturl2,ob['task_id'],ob['domain_id'])
                        if content.find("<HTML><BODY> <FORM METHOD=\"GET\" NAME=\"comments\" ACTION=\"\"> <INPUT TYPE=\"text\" NAME=\"comment\"> <INPUT TYPE=\"submit\" VALUE=\"Send\"> </FORM> <pre>  </pre> </BODY></HTML>")>=0:
                            request = getRequest(geturl2)
                            response = getResponse(response)
    except Exception, e:
        logging.getLogger().error("File:JBossCheckJSPscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:JBossCheckJSPscript.py, run_domain function :" + str(e))
    return result