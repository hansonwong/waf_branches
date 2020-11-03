import os
import time
import atexit
from db.config1 import execute_sql,fetchone_sql,fetchall_sql
from db.db_log_tables_reset import TB_3307
from utils.log_logger import FWLOG_DEBUG
from utils.cache import cache


tb_list=["http_log","dns_log","fast_log","eve_json",
         "iptables-ng_log","ddos_log","url_log","app_admin",
         "evil_code","info_leak","webaudit_log","web_app", "vpn"]

_KEY = lambda x : 'bdfw_log_size_{}'.format(x)




class _Singleton(type):
    """Singleton Mode Meta Class"""
    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


class log_size_record(object):
    __metaclass__ = _Singleton

    def __init__(self,path = "log_size_record"):
        super(log_size_record, self).__init__()
        try:
            execute_sql(TB_3307('m_tblog_size_record'))
            sql = 'SELECT COUNT(*) FROM m_tblog_size_record;'
            t = int(time.time())

            # create log_size_record table if not exists
            for tb in tb_list:
                sql = 'select sImportSize from m_tblog_size_record where sLogName="%s"'
                if fetchone_sql(sql % tb) == None:
                    _sql = ('insert into m_tblog_size_record(sLogName,sImportSize,'
                            'iTime) values("%s",%s,%s)')
                    execute_sql(_sql % (tb,0,t))

            # read size from table and save in cache
            sql = 'select sLogName,sImportSize from m_tblog_size_record'
            [cache.set(_KEY(res['sLogName']), res['sImportSize']) for res in fetchall_sql(sql)]
        except:
            # if error in reading log_size_record table
            for _tb in  tb_list:
                cache.set(_KEY(tb), 0)


    def set_record(self,log,size):
        if not log in tb_list:
            FWLOG_DEBUG('Invalid Log Name')
            return
        # t = int(time.time())

        # sql = 'update m_tblog_size_record set sImportSize=%s,iTime=%s where sLogName="%s"' % (size,t,log)
        # execute_sql(sql)

        # set record in cache
        cache.set(_KEY(log), size)

    @classmethod
    def update_record(cls):
        print 'update_record'
        _t = int(time.time())
        sql = 'update m_tblog_size_record set sImportSize={s}, iTime={t} where sLogName="{n}"'
        for _tb in tb_list:
            _size = cache.get(_KEY(_tb))
            print(sql.format(s=_size, t=_t, n=_tb))
            execute_sql(sql.format(s=_size, t=_t, n=_tb))
        pass

    def get_record_by(self,log):
        # sql = 'select sImportSize from m_tblog_size_record where sLogName="%s"' % log
        # res = int(fetchone_sql(sql)['sImportSize'])

        res = cache.get(_KEY(log))
        return res

    def get_record(self):
        # sql = 'select sLogName,sImportSize from m_tblog_size_record'
        # d = {str(res['sLogName']):int(res['sImportSize']) for res in fetchall_sql(sql)}

        # get all size in cache
        d = { tb: cache.get(_KEY(tb))for tb in tb_list }
        return d

    def clear_record(self,tb='all'):
        if tb == 'all':
            for t in tb_list:
                self.set_record(t,0)
        elif tb in tb_list:
            self.set_record(tb,0)
        else:
            FWLOG_DEBUG('log_size_record:no tb name %s' % tb)


@atexit.register
def log_size_record_exit():
    log_size_record.update_record()

if __name__ == "__main__":
    #log_record().update_record()
    lr = log_size_record()
    lr1 = log_size_record()
    print lr is lr1
    print id(lr)
    print id(lr1)
    print lr.set_record("http_log",1024)
    #lr.clear_record('web_app')
    ##lr.update_record()
    print lr.get_record_by('fast_log')
    print lr.get_record()
    del lr
    del lr1


