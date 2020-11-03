#!/usr/bin/env python
#-*-coding:utf-8-*-

import time
import MySQLdb


#��MySQLdb���ú������з�װ����
class MySQL(object):

    error_code = '' #MySQL�������

    _conn = None #���ݿ�conn
    _cur = None #�α�

    _TIMEOUT = 30 #Ĭ�ϳ�ʱ30��
    _timecount = 0

    '''
    ���������������ݿ����Ӳ���������MySQL����
    @parameters:
        dbconfig: ���ݿ����Ӳ���
        Ĭ��ʹ��waf���ݿ�
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
        
            # ���û�г���Ԥ�賬ʱʱ�䣬���ٴγ������ӣ�
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
    ִ�� SELECT ���
    @parameters:
        sql: sql���
    '''
    def query(self,sql):
        try:
            self._cur.execute("SET NAMES utf8") 
            result = self._cur.execute(sql)
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            print "���ݿ�������:",e.args[0],e.args[1]
            result = False
        return result

    '''
    ִ�� UPDATE �� DELETE ���
    @parameters:
        sql: sql���
    '''
    def update(self,sql):
        try:
            self._cur.execute("SET NAMES utf8") 
            result = self._cur.execute(sql)
            self._conn.commit()
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            print "���ݿ�������:",e.args[0],e.args[1]
            result = False
        return result
      
    '''
    ִ�� INSERT ���
    @parameters:
        sql: sql���
    @return:
        ������Ϊ������int���򷵻������ɵ�ID
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
    ���ؽ��Ԫ��
    @reutrn:
        ���ؽ����Ԫ��Ԫ��Ϊ�ֵ�����
    '''
    def fetchAllRows(self):
        return self._cur.fetchall()

    '''
    ����һ�н����Ȼ���α�ָ����һ�С��������һ���Ժ󣬷���None
    @reutrn:
        ���صĽ������Ϊ�ֵ�
    '''
    def fetchOneRow(self):
        return self._cur.fetchone()

    '''
    ��ȡ�������
    @return:
        ���ؽ������int
    '''
    def getRowCount(self):
        return self._cur.rowcount

    '''
    ���ݿ�commit����
    '''
    def commit(self):
        self._conn.commit()

    '''
    ���ݿ�ع�����
    '''
    def rollback(self):
        self._conn.rollback()

    '''
    �ͷ���Դ(ϵͳGC�Զ�����)
    '''
    def __del__(self): 
        try:
            self._cur.close() 
            self._conn.close() 
        except:
            pass
    
    '''
    �ر����ݿ�����
    '''
    def  close(self):
        self.__del__()


if __name__ == '__main__':
    '''ʹ������'''
    #���ݿ����Ӳ���  
    dbconfig = {'host':'localhost', 
        'port': 3306, 
        'user':'root', 
        'passwd':'bd_123456',
        'db':'waf', 
        'charset':'utf8',
        'use_unicode': 'False'}
  
    #�������ݿ⣬����������ʵ��
    db = MySQL(dbconfig)

    #�������ݿ�
    sql = "SELECT * FROM `t_nicset`"
    db.query(sql);

    #��ȡ����б�
    result = db.fetchAllRows();

    #�൱��php�����var_dump
    print result

    #���н���ѭ��
    for row in result:
        print row
        #ʹ���±����ȡֵ
        print row["nic"]

    db.select_db("logs")
    #�ر����ݿ�
    db.close()
