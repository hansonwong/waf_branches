#! /usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
from datetime import datetime

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from db.config import execute_sql, fetchall_sql
from usermanage.user_group import radius_file


TB_USERS = 'm_tbusers'


def del_expire_user():
    
    rec = fetchall_sql('select id,sUserName,iExpiredTime from m_tbusers')
    for r in rec:
        if not r['iExpiredTime'] == None:
            if r['iExpiredTime'] <= datetime.now():
                radius_file(r, 'del')
                del_sql = 'delete from ' + TB_USERS + ' where id="%s"' % r['id']
                execute_sql(del_sql)
                os.system('/usr/sbin/userdel -f -r "%s"' % r['sUserName'])


if __name__ == '__main__':
    del_expire_user()
    pass

