from reportlog.mysql_log_backup import mysql_log_init_db as init_db
from db.config1 import get_mysql_db




if __name__ == '__main__':
    conn,cur = get_mysql_db()
    sql = 'select sRuleID from m_tblog_ips_20160526'
    cur.execute(sql)
    args = []
    for res in cur.fetchall():
        sql = 'select iSID,sCve from m_tbipsrules where iSID=%s' % int(res['sRuleID'])
        #args.append((int(res['sRuleID'])))
        cur.execute(sql)
        r = cur.fetchone()
        l = r if r == None else 'SID = %s , CVE = %s' % (r['iSID'],r['sCve'])
        print l
  
    
    #print 'start sql'
    #sql = 'select iSID,sCve from m_tbipsrules where iSID=%s'
    #cur.executemany(sql , args)
    #print 'executemany done'
    #for r in cur.fetchall():
    #    l = r if r == None else 'SID = %s , CVE = %s' % (r['iSID'],r['sCve'])
    #    print l

    cur.close()
    conn.close()
    pass
