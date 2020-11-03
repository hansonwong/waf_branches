#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib
import urllib2
import httplib2
from lib.common import *
from cStringIO import StringIO
import traceback

#header inject
_headerKey = "NvsInjHeader"
_headerValue = "nvsinjected"
_headerKeyWord = "\n%s:%s" %(_headerKey,_headerValue)

#redirect inject
_redirKeyWord = "Header may not contain more than a single header, new line detected"


def _encode_multipart(data,row,injectType):
    """
    injectType: {1:header,2:redir}
    """
    boundary = '--------------NvscanBoundaryLWYILYHBY1314520'
    sep_boundary = '\r\n--' + boundary
    end_boundary = sep_boundary + '--'
    body = StringIO()
    for key, value in data.items():
        # handle multiple entries for the same name
        if type(value) != type([]):
            value = [value]
        for value in value:
            if type(value) is tuple:
                fn = '; filename="%s"' % value[0]
                value = value[1]
            else:
                fn = ""

            body.write(sep_boundary)
            body.write('\r\nContent-Disposition: form-data; name="%s"' % key)
            body.write(fn)
            body.write("\r\n\r\n")
            if key == row:
                if injectType == 1:
                    body.write("\r\n%s:%s" %(_headerKey,_headerValue))
            else:
                body.write(value)
    body.write(end_boundary)
    body.write("\r\n")
    return body.getvalue(), boundary

def headerInject(res,content):
    if content.find(_redirKeyWord) != -1:
        return True
    for value in res.itervalues():
        if value.find(_headerKeyWord) != -1:
            return True
    #end for
    return False


def run_url(http,ob,item):
    result = []
    try:
        if item['params'] == '':
            return result
        #end if
        url = urllib.unquote(item['url'])
        _http=http
    
        if item['method'] == 'get':
            params_dict = dict(map(lambda s: s.split('=',1) if len(s.split('='))>1 else [s[:s.find('=')],''],item['params'].split('&')))
            for row in params_dict:
                tmp = params_dict.copy()
                tmp[row] = '%%0d%%0a%s%%3a%s' %(_headerKey,_headerValue)
                new_url = "%s?%s" %(url, '&'.join("%s=%s" %(k,v) for k,v in tmp.iteritems()))
                #res,content = _http.request(new_url)
                res,content = yx_httplib2_request(_http,new_url)
                if (res.has_key(_headerKey) and res[_headerKey] == _headerValue) or headerInject(res,content):
                    request = getRequest(new_url)
                    response = getResponse(res)
                    detail = "注入参数："+row
                    result.append(getRecord(ob,new_url,ob['level'],detail,request,response))
                #end if
            #end for

        elif item['method'] == 'post':
            params_list = json.read(item['params'])
            params = {}
            upload = False
            for row in params_list:
                if row['type'] == 'file':
                    upload = True
                    params[row['name']] = ('','')
                else:
                    params[row['name']] = row['value']
            #end for
            if upload:
                for row in params:
                    data, boundary = _encode_multipart(params,row,1)
                    headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
                            'Content-Length': str(len(data)),
                        }
                    #res,content = _http.request(url, 'POST', data, headers=headers)
                    res,content = yx_httplib2_request(_http,url, 'POST', data, headers=headers)
                    if (res.has_key(_headerKey) and res[_headerKey] == _headerValue) or headerInject(res,content):
                        request = postRequest(url,data=data)
                        response = getResponse(res)
                        detail = "注入参数："+row
                        result.append(getRecord(ob,new_url,ob['level'],detail,request,response))
                    #end if
                #end for
            else:
                for row in params:
                    headers = {"Content-Type":"application/x-www-form-urlencoded"}                
                    tmp = params.copy()
                    tmp[row] = '\r\n%s:%s' %(_headerKey,_headerValue)
                    data = urllib.urlencode(tmp)
                    #res,content = _http.request(url, 'POST', data, headers=headers)
                    res,content = yx_httplib2_request(_http,url, 'POST', data, headers=headers)
                    if (res.has_key(_headerKey) and res[_headerKey] == _headerValue) or headerInject(res,content):
                        request = postRequest(url,data=data)
                        response = getResponse(res)
                        detail = "注入参数："+row
                        result.append(getRecord(ob,url,ob['level'],detail,request,response))
                    #end if
                #end for
            #end if
        #end if
        return result

    except Exception,e:
        logging.getLogger().error("File:HttpResponseSplit.py, run_url function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s, url:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path'],item['url']))
        write_scan_log(ob['task_id'],ob['domain_id'],"File:HttpResponseSplit.py, run_url function :%s , url:%s" % (str(e),item['url']))
    #end try
    return result
#end def
