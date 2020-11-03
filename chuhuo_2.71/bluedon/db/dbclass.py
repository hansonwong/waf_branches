# _*_ coding:utf-8 _*_


__version__ = '$Revision: 2.0 $'

import MySQLdb
import sys
import os, types
import time, random


PRE_WORED = ['from', 'into', 'update']
EXISTED_DBARGS = {}


#以id区间方式查询，适合主键id连续性较好的数据,为默认选项
range_section = 1
#以limit 固定增量方式查询，适合主键id存在较大空段的数据，避免不必要的空循环
range_limit = 2

def escape_string(val):
    if not val:
        return ''
    return MySQLdb.escape_string(val)

class Dbclass:
    def __init__(self,  source):
        self._conn = None
        self._cursor = None
        self._source = source

    def connect(self, charset='gbk', commit=True):

        self._charset = charset
        db_arg = self._source
        attempt = 0

        while True:
            try:
                if db_arg.has_key('sql_db'):
                    self._conn = MySQLdb.connect(host=db_arg['sql_host'],
                        user=db_arg['sql_user'], passwd=db_arg['sql_passwd'],
                        db=db_arg['sql_db'], port=db_arg['sql_port'],
                        charset=charset, use_unicode=False,
                        unix_socket=db_arg['unix_socket'],)
                else:
                    self._conn = MySQLdb.connect(host=db_arg['sql_host'],
                        user=db_arg['sql_user'], passwd=db_arg['sql_passwd'],
                        port=db_arg['sql_port'],
                        charset=charset, use_unicode=False,
                        unix_socket=db_arg['unix_socket'],)

                self._cursor = self._conn.cursor(MySQLdb.cursors.DictCursor)
                #self._cursor = self._conn.cursor(MySQLdb.cursors.Cursor)
                if commit:
                    self._cursor.execute("set autocommit=1;")
                break
            except MySQLdb.Error , e:
                attempt += 1
                if attempt >= 3:
                    return (-1, e)

        return (0, None)

    def escape_string(self, val):
        return MySQLdb.escape_string(val)

    def query(self, sql, param=None):
        ver = MySQLdb.version_info
        ver = ver[0] * 100 + ver[1] * 10 + ver[2]

        #版本1.2.1之后无须转换
        if ver <= 121:
            if not isinstance(sql, unicode):
                sql = sql.decode(self._charset, 'ignore')

        attempt = 0
        while True:
            try:
                if not param:
                    self._cursor.execute(sql)
                else:
                    self._cursor.execute(sql, param)
                break
                #infos = self._cursor.fetchall()
            except MySQLdb.Error , e:
                if e[0] in (2006, 2013):
                    attempt += 1
                    if attempt >= 3:
                        return (-1, e)
                    self.connect()
                    continue
                return (-1, e)
            except UnicodeDecodeError, e:
                return (-1, e)

        infos = self._cursor.fetchall()


        return (0, infos)


    def commit(self):
        try:
            self._conn.commit()
        except Exception, e:
            return (e[0], e)

        return 0, None


    def rollback(self):
        try:
            self._conn.rollback()
        except Exception, e:
            return (e[0], e)

        return 0, None


    def close(self):
        try:
            if self._cursor:
                self._cursor.close()
                self._cursor = None
            if self._conn:
                self._conn.close()
                self._conn = None
        except:
            pass

    def __del__(self):

        self.close()


def get_sql_table(sql):
    """
    从 sql 语句解析 获得库名，表名
    Args:
        sql         查询语句
    Return:
        table_name  解析得到的表名
        base_name   解析得到的库名
    """

    table_name = ''
    base_name  = ''
    base_table = ''

    sql = sql.lower()
    sql_words = sql.split()
    pre_tmp = ''
    for word in sql_words:
        if pre_tmp in PRE_WORED:
            #如果上一个词是操作关键字的，则当前词为库表名
            base_table = word
            break
        pre_tmp = word
    tmp = base_table.split('.')

    if tmp:
        table_name = tmp[0]
    if len(tmp) == 2:
        table_name = tmp[1]
        base_name = tmp[0]

    return table_name, base_name


def fetch_dbarg(base_conf, sql='', table_name='', base_name='', multi_base=False):
    """
    按表名、库名 获取配置
    Args:
        base_conf   配置信息汇总库的 数据库连接参数
        sql         sql 包含表名/库名的查询语句
        table_name  表名
        base_name   库名
        multi_base  是否需要返回多库， 默认否; 即按表名找到多个配置时，默认返回随机的一个
    Return:
        (status, database_conf)  （状态码， 数据库连接参数） 当按表名找到多组参数时，随机返回其中一组

    注：当已经传入表名或库名时，sql参数可以不传，否则以sql中的表名 库名 为准去找数据库配置
    """
    if table_name or base_name:
        pass
    else:
        table_name, base_name = get_sql_table(sql)

    #已经读过的配置不再重复去读
    arg_index = '%s.%s' % (table_name, base_name)
    if EXISTED_DBARGS.has_key(arg_index):
        return 0, EXISTED_DBARGS[arg_index]

    #按指定下标获得配置参数
    arg_keys = ['sql_host','sql_user','sql_db','sql_passwd','sql_port']
    if base_name:
        sql = "select %s from data_conf.base_conf where id in (select conf_id from data_conf.base_by_table " \
              "where base_name='%s' and table_name='%s')" % (','.join(arg_keys), base_name, table_name)
    else:
        sql = "select %s from data_conf.base_conf where id in (select conf_id from data_conf.base_by_table " \
              "where table_name='%s')" % (','.join(arg_keys), table_name)

    res, desc = exec_sql(base_conf, sql)
    arg_list = []

    if res != 0:
        return res, desc

    for row in desc:
        arg_list.append(row)
    random.shuffle(arg_list)

    if not arg_list:
        #按表名没找到库
        return -1, 'no database configuration for table %s.%s [%s]' % (table_name, base_name, sql)

    if multi_base:
        #返回多库
        arg_detail = arg_list
    else:
        arg_detail = arg_list[0]

    if arg_detail:
        EXISTED_DBARGS[arg_index] = arg_detail

    return 0, arg_detail


def exec_sql(who, sql, param=None, pre={}, get_lastid=False, affected_rows = False, charset='gbk', commit=True, base_conf={}):
    if not who:
        if not base_conf:
            return -1, 'base_conf can not be empty while who is empty !'
        res, desc = fetch_dbarg(base_conf, sql)
        if res != 0:
            return res, desc
        who = desc
    info = Dbclass(who)
    res, desc = info.connect(charset=charset, commit=commit)
    if res != 0:
        return (res, desc)
    res = 0
    for v in pre:
        res, desc = info.query(v)
        if res != 0:
            return (res, desc)

    res, desc = info.query(sql, param)
    lastid = 0
    if res == 0 and get_lastid:
        res, tmp = info.query('SELECT LAST_INSERT_ID() as lastid;')
        if res == 0 and len(tmp) > 0:
            lastid = tmp[0]['lastid']
    if res == 0 and affected_rows:
        res, tmp = info.query('SELECT ROW_COUNT() as affected_rows;')
        if res == 0 and len(tmp) > 0:
            lastid = tmp[0]['affected_rows']

    #if res == 0:
    #    res, commit_desc = info.commit()
    #    if res != 0:
    #        return res, commit_desc

    info.close()
    if (get_lastid or affected_rows) and res == 0:
        return (res, (desc, lastid))
    return (res, desc)


def query_range(who, table, field="*", idfield="id", step=10000, begin=0, end=0, _sql='', reserver=False, charset='gbk', range_type=range_section, base_conf={}):
    if range_type == 1:
        return query_range_sec(who, table, field, idfield, step, begin, end, _sql, reserver, charset, base_conf)
    else:
        return query_range_limit(who, table, field, idfield, step, begin, end, _sql, charset, base_conf)


def query_range_sec(who, table, field="*", idfield="id", step=10000, begin=0, end=0, _sql='', reserver=False, charset='gbk', base_conf={}):
    res = 0
    if begin <= 0 or end <= 0:
        idx = idfield.find('.')
        tmpfield = idfield
        if idx:
            tmpfield = idfield[idx + 1:]

        sql = 'select MIN(%s), MAX(%s) from %s' % (tmpfield, tmpfield, table)
        res, desc = exec_sql(who, sql, charset=charset, base_conf=base_conf)
        if res != 0:
            yield (res, (desc, sql))
        else:
            v = desc[0].values()
            v.sort()
            min_id = v[0]
            if v[1]:
                max_id = v[1] + 1
            else:
                max_id = min_id
    if res == 0:
        if begin > 0:
            min_id = begin
        if end > 0:
            max_id = end + 1
        cur_id = min_id
        while cur_id < max_id:
            _cur_max = cur_id + step
            if _cur_max > max_id:
                _cur_max = max_id

            if reserver:
                high = max_id - cur_id + 1
                low = max_id - _cur_max + 1
            else:
                low =  cur_id
                high = _cur_max
            if _sql:
                sql = '%s and %s >= %d and %s < %d;' % (_sql, idfield, low, idfield, high)
            else:
                sql = 'select %s from %s where %s >= %d and %s < %d;' % (field, table, idfield, low, idfield, high)

            res, desc = exec_sql(who, sql, charset=charset, base_conf=base_conf)
            yield (res, (desc, sql))
            cur_id += step

def query_range_limit(who, table, field="*", idfield="id", step=10000, begin=0, end=0, _sql='', charset='gbk', base_conf={}):

    res = 0
    if begin <= 0 or end <= 0:
        idx = idfield.find('.')
        tmpfield = idfield
        if idx:
            tmpfield = idfield[idx + 1:]

        sql = 'select MIN(%s), MAX(%s) from %s' % (tmpfield, tmpfield, table)
        res, desc = exec_sql(who, sql, charset=charset, base_conf=base_conf)
        if res != 0:
            yield (res, (desc, sql))
        else:
            v = desc[0].values()
            v.sort()
            min_id = v[0]
            if v[1]:
                max_id = v[1] + 1
            else:
                max_id = min_id
    if res == 0:
        if begin > 0:
            min_id = begin
        if end > 0:
            max_id = end + 1
        low = min_id
        d_index = 0
        while (low < max_id) and (d_index > -1):
            if _sql:
                sql = '%s and %s >= %d order by %s asc limit %d;' % (_sql, idfield, low, idfield, step)
            else:
                sql = 'select %s from %s where %s >= %d order by %s asc limit %d;' % (field, table, idfield, low, idfield, step)

            res, desc = exec_sql(who, sql, charset=charset, base_conf=base_conf)
            try:
                d_index   = len(desc)-1
                if d_index > -1:
                    if low == desc[d_index][tmpfield]:
                        break
                    else:
                        low = desc[d_index][tmpfield]
            except:
                pass

            yield (res, (desc, sql))

def query_range_update(who, table, sql, idfield="id", step=10000, begin=0, end=0, reserver=False, charset='gbk', base_conf={}):
    res = 0
    if begin <= 0 or end <= 0:
        idx = idfield.find('.')
        tmpfield = idfield
        if idx:
            tmpfield = idfield[idx + 1:]

        tmp = 'select MIN(%s), MAX(%s) from %s' % (tmpfield, tmpfield, table)
        res, desc = exec_sql(who, tmp, charset=charset, base_conf=base_conf)
        if res != 0:
            yield (res, (desc, tmp))
        else:
            v = desc[0].values()
            v.sort()
            min_id = v[0]
            max_id = v[1] + 1
    if res == 0:
        if begin > 0:
            min_id = begin
        if end > 0:
            max_id = end + 1
        cur_id = min_id
        while cur_id < max_id:
            _cur_max = cur_id + step
            if _cur_max > max_id:
                _cur_max = max_id

            if reserver:
                high = max_id - cur_id + 1
                low = max_id - _cur_max + 1
            else:
                low =  cur_id
                high = _cur_max

            tmp = '%s and %s >= %d and %s < %d;' % (sql, idfield, low, idfield, high)
            res, desc = exec_sql(who, tmp, charset=charset, base_conf=base_conf)
            yield (res, (desc, tmp))
            cur_id += step


def query_range_bykeys(who, table, field="*", keyfield="id", step=10000, keys=list(), charset='gbk', base_conf={}):
    cur = 0
    _max = len(keys)
    _tmp = list()
    if keys:
        if type(keys[0]) == types.IntType or type(keys[0]) == types.LongType:
            _tmp = ['%d' % v for v in keys]
        else:
            _tmp = ['"%s"' % escape_string(v) for v in keys]
    while cur < _max:
        _cur_max = cur + step
        if _cur_max > len(keys):
            _cur_max = len(keys)
        sql = 'select %s from %s where %s in (%s)' % (field, table, keyfield, ','.join(_tmp[cur:_cur_max]))
        res, desc = exec_sql(who, sql, charset=charset, base_conf=base_conf)
        yield (res, (desc, sql))
        cur+= step

def get_count_list(count_key, count_list, db_arg, table_name, field_name_rs, filed_name_id,
                    query_step=0, bgin_id=0, end_id=0, sql='', range_type=1):
    """获取统计数据 统计方式以符合条件的统计结果的个数总和来算

    Args:
        count_key  统计关键字
        count_list 统计结果保存对像，按count_key原来已有统计数据的，累加合并
        db_arg     数据连接参数
        table_name 被统计表
        field_name_rs 统计查询返回字段
        filed_name_id 被统计表主键
        query_step 查询步长
        bgin_id    开始id
        end_id     结束id
        sql        统计查询语句

        Returns:
          元组(0,count_list)

        Raises:
          None。
    """

    for res,desc in query_range(who=db_arg, table=table_name, field=field_name_rs,
                    idfield=filed_name_id, step=query_step, begin=bgin_id,
                    end=end_id, _sql=sql, range_type=range_type
                    ):
        if res == 0:
            #print desc[1]
            for row in desc[0]:
                #print row[count_key]

                key_val = row[count_key]

                if count_list.has_key(key_val):
                    count_list[key_val] = count_list[key_val] + 1
                else:
                    count_list[key_val] = 1
        else:
            return -1,desc

    return 0,count_list

if __name__ == '__main__':
    pass
    print "\\"
    sql = "1)2004年10月20日下午17:00左右伤者当事人在上班途中騎自行車行駛到龍崗植物園鵬達門診\北段時﹐被身後同向行駛的機動車撞傷在地。伤者當時不醒人事﹐醒後在後腦右側大量出血的情況下﹐勉強從地面爬起並在鵬達門診\附近徘徊走動﹐隨後門診\部醫生看傷者出血過多﹐神智不清﹐便果斷給傷者縫紮傷口並報警。事故發生後对方当事人駕駛車輛逃離事故現場。2)伤者在门诊治疗期间所交付的费用发票被盗，伤者家属已报警。"
    sql = '根據以上的描述，對於F律師，你認為我可以要求他賠償嗎？我應該怎樣做？如果自2004年F律師和L律師互相勾結，我可以要求F律師退回所有律師費嗎？由2004年4月至2005年12月，他在那件房地產商業串謀'
    print escape_string(sql.decode('utf8').encode('gbk'))


