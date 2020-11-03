import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
from utils.logger_init import get_logger
from reportlog.mysql_log_backup import mysql_log_recover_by_date
from db.config1 import execute_sql,executemany_sql,fetchone_sql,fetchall_sql,record_in_tb


ARG = ['m_tblog_firewall','20160530']
def recover_log(log_type,date):
    mysql_log_recover_by_date(log_type,date)
    pass


def recover_log(arg):
    sql = "insert into m_tblogtable (iLogtablename,iLogtablestate) values('%s',%s)"
    RECOVERING = '1'
    DONE = '2'
    tb = arg[0]+'_'+arg[1]

    #keep counts of records less than 1000
    #cur.execute('select count(*) from m_tblogtable;')
    res = fetchone_sql('select count(*) from m_tblogtable;').values()[0]

    if res >= 1000:
        execute_sql('delete from m_tblogtable;')

    #i = fetchone_sql('select * from m_tblogtable where iLogtablename="%s" limit 1' % tb)
    if not record_in_tb(tb,'iLogtablename','m_tblogtable'):
    #if i == None:
        #AttackCategory do not exists
        execute_sql(sql % (tb,RECOVERING))
    else:
        #update data
        execute_sql('update m_tblogtable' + ' set iLogtablestate="%s" where iLogtablename="%s"' % (RECOVERING,tb))
    res = mysql_log_recover_by_date(arg[0],arg[1])
    if res == -1:
        DONE = '3'

    i = fetchone_sql('select * from m_tblogtable where iLogtablename="%s" limit 1' % tb)
    if i == None:
        #AttackCategory do not exists
        execute_sql(sql % (tb,DONE))
    else:
        #update data
        execute_sql('update m_tblogtable' + ' set iLogtablestate="%s" where iLogtablename="%s"' % (DONE,tb))



if __name__ == '__main__':
    #recover_log('m_tblog_url_visit','20160126')
    recover_log(ARG)
