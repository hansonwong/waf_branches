#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from lib.common import *

_form = None
_name = None
_hide = None
def formNoCsrfProtect(content):
    try:
        global _form, _name, _hide
        if _form is None:
            _form = re.compile(r"<(\s*)form(.+?)>(.+?)<(\s*)/(\s*)form(\s*)>",re.I|re.DOTALL)
        match = _form.findall(content)
        if _name is None:
            _name = re.compile(r"name(\s*)=(\s*)('|\")(.+?)(\3)",re.I)
        if _hide is None:
            _hide = re.compile(r"hidden(.+?)(value(\s*)=(\s*)('|\")(.+?)('|\")|value(\s*)=(\s*)(.+?)(\s|/|$))",re.I)
        for row in match:
            if _name.search(row[2]) and not _hide.search(row[2]):
                return True
            #end if
        #end for
    except Exception,e:
        logging.getLogger().error("File:FormNoCsrfProtect.py, formNoCsrfProtect function :%s" % str(e))


_thereForm = None
def run_url(http,ob,item):
    result = []
    try:
        detail = u"该页面表单容易受到CSRF攻击，请检查该页面所有表单。"
        url = item['url']
        if item['params'] != "":
            return result
        if item['method'] == 'get':
            global _thereForm
            if _thereForm is None:
                _thereForm = re.compile(r"<(\s*)form(.+?)>",re.I|re.DOTALL)
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and _thereForm.search(content) and formNoCsrfProtect(content):
                request = getRequest(url)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
            #end if
        #end if
    except Exception,e:
        logging.getLogger().error("File:FormNoCsrfProtect.py, run_url function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s, url:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path'],item['url']))
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FormNoCsrfProtect.py, run_url function :%s , url:%s" % (str(e),item['url']))
    #end try
    return result
#end def