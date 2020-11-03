#!/usr/bin/env python
#-*-coding:utf-8-*-

import time
import MySQLdb


#对MySQLdb常用函数进行封装的类
class MySQL(object):

    error_code = '' #MySQL错误号码

    _conn = None #数据库conn
    _cur = None #游标

    _TIMEOUT = 30 #默认超时30秒
    _timecount = 0

    '''
    构造器：根据数据库连接参数，创建MySQL连接
    @parameters:
        dbconfig: 数据库连接参数
        默认使用waf数据库
    '''
    def __init__(self, dbconfig, db=None):
        try:
            self._conn = MySQLdb.connect(host=dbconfig['host'],
                           port = dbconfig['port'], 
                           user = dbconfig['user'],
                           passwd = dbconfig['passwd'],
                           db = db and db or 'waf',
                           unix_socket = dbconfig['unix_socket'],
                           charset = dbconfig['charset'])
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            error_msg = 'MySQL error! ', e.args[0], e.args[1]
            print error_msg
        
            # 如果没有超过预设超时时间，则再次尝试连接，
            if self._timecount < self._TIMEOUT:
                interval = 5
                self._timecount += interval
                time.sleep(interval)
                return self.__init__(dbconfig)
            else:
                raise Exception(error_msg)
      
        self._cur = self._conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    
    def select_db(self, db):
        try:
            self._conn.select_db(db)
        except Exception, e:
            print e
    
    '''
    执行 SELECT 语句
    @parameters:
        sql: sql语句
    '''
    def query(self,sql):
        try:
            self._cur.execute("SET NAMES utf8") 
            result = self._cur.execute(sql)
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            print "数据库错误代码:",e.args[0],e.args[1]
            result = False
        return result

    '''
    执行 UPDATE 及 DELETE 语句
    @parameters:
        sql: sql语句
    '''
    def update(self,sql):
        try:
            self._cur.execute("SET NAMES utf8") 
            result = self._cur.execute(sql)
            self._conn.commit()
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            print "数据库错误代码:",e.args[0],e.args[1]
            result = False
        return result
      
    '''
    执行 INSERT 语句
    @parameters:
        sql: sql语句
    @return:
        如主键为自增长int，则返回新生成的ID
    '''
    def insert(self,sql):
        try:
            self._cur.execute("SET NAMES utf8")
            self._cur.execute(sql)
            insert_id = self._conn.insert_id()
            self._conn.commit()
            return insert_id
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            return False

    '''
    返回结果元组
    @reutrn:
        返回结果的元组元素为字典类型
    '''
    def fetchAllRows(self):
        return self._cur.fetchall()

    '''
    返回一行结果，然后游标指向下一行。到达最后一行以后，返回None
    @reutrn:
        返回的结果类型为字典
    '''
    def fetchOneRow(self):
        return self._cur.fetchone()

    '''
    获取结果行数
    @return:
        返回结果行数int
    '''
    def getRowCount(self):
        return self._cur.rowcount

    '''
    数据库commit操作
    '''
    def commit(self):
        self._conn.commit()

    '''
    数据库回滚操作
    '''
    def rollback(self):
        self._conn.rollback()

    '''
    释放资源(系统GC自动调用)
    '''
    def __del__(self): 
        try:
            self._cur.close() 
            self._conn.close() 
        except:
            pass
    
    '''
    关闭数据库连接
    '''
    def  close(self):
        self.__del__()


if __name__ == '__main__':
    '''使用样例'''
    #数据库连接参数  
    dbconfig = {'host':'localhost', 
        'port': 3306, 
        'user':'root', 
        'passwd':'bd_123456',
        'db':'waf', 
        'charset':'utf8',
        'use_unicode': 'False'}
  
    #连接数据库，创建这个类的实例
    db = MySQL(dbconfig)

    #操作数据库
    sql = "SELECT * FROM `t_nicset`"
    db.query(sql);

    #获取结果列表
    result = db.fetchAllRows();

    #相当于php里面的var_dump
    print result

    #对行进行循环
    for row in result:
        print row
        #使用下标进行取值
        print row["nic"]

    db.select_db("logs")
    #关闭数据库
    db.close()
