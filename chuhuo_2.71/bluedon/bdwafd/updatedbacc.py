import MySQLdb
from config import config
from logging import getLogger

if __name__=="__main__":
    try:
        conn = MySQLdb.connect(**config['dbacc'])
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE t_alertlogs MODIFY HttpMethod varchar(10)")
    except Exception, e:
        getLogger('audit').info(e)
    finally:
        conn.commit()
        cursor.close()
        conn.close()

