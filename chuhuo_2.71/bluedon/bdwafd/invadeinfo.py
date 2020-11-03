import os
import datetime
import json
import MySQLdb

datafile = '/Data/apps/wwwroot/waf/cache/invadeinfo.json'
dbtables = ['t_alertlogs', 't_ddoslogs', 't_weboutlogs', 't_bdblockedlogs', 't_ruleid', 't_countsety', 't_cclogs']
dbconfig = {
    'host':'127.0.0.1',
    'user':'root',
    'passwd':'bd_123456',
    'db':'waf',
    'port':3306,
    'charset':'utf8',
    'use_unicode':False
    }
dblogconfig = {
    'host':'127.0.0.1',
    'user':'root',
    'passwd':'bd_123456',
    'db':'logs',
    'port':3306,
    'charset':'utf8',
    'use_unicode':False
    }

class InvadeInfo():

    def __init__(self):
        self.ruletypes = []
        self.counts = {}
        self.getrulecat()
        self.nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def getrulecat(self):
        db = MySQLdb.connect(**dbconfig)
        cursor = db.cursor()
        cursor.execute('select * from t_rulecat')
        rulecats = cursor.fetchall()
        for rulecat in rulecats:
            self.ruletypes.append(rulecat[1])

    def initdata(self):
        last_ids = {}
        counts = {}
        countsety = {}
        monthstr = self.nowtime[:8] + '01 00:00:00'
        db = MySQLdb.connect(**dblogconfig)
        cursor = db.cursor()
        for table in dbtables:
            cursor.execute("select id from %s order by id DESC limit 1" % table)
            tmp_id = cursor.fetchone()
            last_ids[table] = int(tmp_id[0]) if tmp_id else 0
            if table == 't_alertlogs':
                for ruletype in self.ruletypes:
                    if ruletype == 'CC':
                        continue
                    if last_ids[table]:
                        cursor.execute("select count(*) from t_alertlogs where unix_timestamp(LogDateTime) > unix_timestamp('%s') and AttackType='%s' and id<=%s" % (monthstr, ruletype, last_ids[table]))
                        count = cursor.fetchone()[0]
                        counts[ruletype] = int(count) if count else 0
                    else: counts[ruletype] = 0
                if last_ids[table]:
                    cursor.execute("SELECT count(*) AS num FROM logs.t_alertlogs WHERE DATE_FORMAT(`LogDateTime`,'%Y-%m')='{}' AND AttackType='None' AND id<={}".format(monthstr, last_ids[table]))
                    count = cursor.fetchone()[0]
                    counts['UNDEFINED'] = int(count) if count else 0
                else: counts['UNDEFINED'] = 0
            if table == 't_weboutlogs':
                if last_ids[table]:
                    cursor.execute("select count(*) from t_weboutlogs where unix_timestamp(`dt`) > unix_timestamp('%s') and id<=%s" % (monthstr, last_ids[table]))
                    count = cursor.fetchone()[0]
                    counts['WEBOUT'] = int(count) if count else 0
                else: counts['WEBOUT'] = 0
            if table == 't_ddoslogs':
                if last_ids[table]:
                    cursor.execute("select count(*) from t_ddoslogs where from_unixtime(`logtime`) > unix_timestamp('%s') and id<=%s" % (monthstr, last_ids[table]))
                    count = cursor.fetchone()[0]
                    counts['DDOS'] = int(count) if count else 0
                else: counts['DDOS'] = 0
            if table == 't_bdblockedlogs':
                if last_ids[table]:
                    cursor.execute("select count(*) from t_bdblockedlogs where from_unixtime(`logtime`) > unix_timestamp('%s') and id<=%s" % (monthstr, last_ids[table]))
                    count = cursor.fetchone()[0]
                    counts['SMARTBLOCK'] = int(count) if count else 0
                else: counts['SMARTBLOCK'] = 0
            if table == 't_cclogs':
                if last_ids[table]:
                    cursor.execute("select count(*) from t_cclogs where from_unixtime(`LogDateTime`) > unix_timestamp('%s') and id<=%s" % (monthstr, last_ids[table]))
                    count = cursor.fetchone()[0]
                    counts['CC'] = int(count) if count else 0
                else: counts['CC'] = 0
            if table == 't_countsety':
                if last_ids[table]:
                    cursor.execute("SELECT sum(emergency) as emergency,sum(alert) as alert,sum(critical) as critical,sum(error) as error,sum(warning) as warning FROM t_countsety WHERE DATE_FORMAT(`logdate`,'%Y-%m')='{}' and id<={}".format(monthstr[:7], last_ids[table]))
                    decimalnums = cursor.fetchone()
                    countsety['EMERG'] = int(decimalnums[0]) if decimalnums else 0
                    countsety['ALERT'] = int(decimalnums[1]) if decimalnums else 0
                    countsety['CRITI'] = int(decimalnums[2]) if decimalnums else 0
                    countsety['ERROR'] = int(decimalnums[3]) if decimalnums else 0
                    countsety['WARN'] = int(decimalnums[4]) if decimalnums else 0
                else: countsety['EMERG'] = countsety['ALERT'] = countsety['CRITI'] = countsety['ERROR'] = countsety['WARN'] = 0
        data = {
            'last_ids':last_ids,
            'counts':counts,
            'last_runtime':self.nowtime,
            'countsety': countsety
            }
        with open(datafile, 'w') as write_file:
            json.dump(data,write_file)

    def update(self, data):
        last_ids = data.get('last_ids')
        new_ids = {}
        tmp_dic = {}
        db = MySQLdb.connect(**dblogconfig)
        cursor = db.cursor()
        for table in dbtables:
            cursor.execute("select id from %s order by id DESC limit 1" % table)
            tmp_id = cursor.fetchone()
            new_ids[table] = int(tmp_id[0]) if tmp_id else 0
            if table == 't_alertlogs':
                for ruletype in self.ruletypes:
                    if ruletype == 'CC':
                        continue
                    if new_ids[table]:
                        if last_ids[table]:
                            cursor.execute("select count(*) from t_alertlogs where id > %s and AttackType='%s' and id<=%s" % (last_ids[table], ruletype, new_ids[table]))
                            count = cursor.fetchone()[0] 
                            tmp_dic[ruletype] = int(count) if count else 0
                        else:
                            cursor.execute("select count(*) from t_alertlogs where AttackType='%s' and id<=%s" % (ruletype, new_ids[table]))
                            tmp_dic[ruletype] = int(cursor.fetchone()[0])
                    else: tmp_dic[ruletype] = 0
                if new_ids[table]:
                    if last_ids[table]:
                        cursor.execute("SELECT count(*) AS num FROM logs.t_alertlogs WHERE AttackType='None' AND id>%s AND id<=%s" % (last_ids[table], new_ids[table]))
                        count = cursor.fetchone()[0] 
                        tmp_dic['UNDEFINED'] = int(count) if count else 0
                    else:
                        cursor.execute("SELECT count(*) AS num FROM logs.t_alertlogs WHERE AttackType='None' AND id<=%s" % new_ids[table])
                        tmp_dic['UNDEFINED'] = int(cursor.fetchone()[0])
                else: tmp_dic['UNDEFINED'] = 0
            if table == 't_weboutlogs':
                if new_ids[table]:
                    if last_ids[table]:
                        cursor.execute("select count(*) from t_weboutlogs where id>%s and id<=%s" % (last_ids[table], new_ids[table]))
                        count = cursor.fetchone()[0] 
                        tmp_dic['WEBOUT'] = int(count) if count else 0
                    else:
                        cursor.execute("select count(*) from t_weboutlogs where id<=%s" % new_ids[table])
                        tmp_dic['WEBOUT'] = int(cursor.fetchone()[0])
                else: tmp_dic['WEBOUT'] = 0
            if table == 't_ddoslogs':
                if new_ids[table]:
                    if last_ids[table]:
                        cursor.execute("select count(*) from t_ddoslogs where id>%s and id<=%s" % (last_ids[table], new_ids[table]))
                        count = cursor.fetchone()[0] 
                        tmp_dic['DDOS'] = int(count) if count else 0
                    else:
                        cursor.execute("select count(*) from t_ddoslogs where id<=%s" % new_ids[table])
                        tmp_dic['DDOS'] = int(cursor.fetchone()[0])
                else: tmp_dic['DDOS'] = 0
            if table == 't_bdblockedlogs':
                if new_ids[table]:
                    if last_ids[table]:
                        cursor.execute("select count(*) from t_bdblockedlogs where id>%s and id<=%s" % (last_ids[table], new_ids[table]))
                        count = cursor.fetchone()[0] 
                        tmp_dic['SMARTBLOCK'] = int(count) if count else 0
                    else:
                        cursor.execute("select count(*) from t_bdblockedlogs where id<=%s" % new_ids[table])
                        tmp_dic['SMARTBLOCK'] = int(cursor.fetchone()[0])
                else: tmp_dic['SMARTBLOCK'] = 0
            if table == 't_cclogs':
                if new_ids[table]:
                    if last_ids[table]:
                        cursor.execute("select count(*) from t_cclogs where id>%s and id<=%s" % (last_ids[table], new_ids[table]))
                        count = cursor.fetchone()[0] 
                        tmp_dic['CC'] = int(count) if count else 0
                    else:
                        cursor.execute("select count(*) from t_cclogs where id<=%s" % new_ids[table])
                        tmp_dic['CC'] = int(cursor.fetchone()[0])
                else: tmp_dic['CC'] = 0
            if table == 't_countsety':
                if new_ids[table]:
                    if last_ids[table]:
                        cursor.execute("SELECT sum(emergency) as emergency,sum(alert) as alert,sum(critical) as critical,sum(error) as error,sum(warning) as warning FROM t_countsety WHERE id>%s and id <=%s" % (last_ids[table], new_ids[table]))
                        decimalnums = cursor.fetchone()[0] 
                        tmp_dic['COUNTSETY'] = {}
                        tmp_dic['COUNTSETY']['EMERG'] = int(decimalnums[0]) if decimalnums else 0
                        tmp_dic['COUNTSETY']['ALERT'] = int(decimalnums[1]) if decimalnums else 0
                        tmp_dic['COUNTSETY']['CRITI'] = int(decimalnums[2]) if decimalnums else 0
                        tmp_dic['COUNTSETY']['ERROR'] = int(decimalnums[3]) if decimalnums else 0
                        tmp_dic['COUNTSETY']['WARN'] = int(decimalnums[4]) if decimalnums else 0
                    else:
                        cursor.execute("SELECT sum(emergency) as emergency,sum(alert) as alert,sum(critical) as critical,sum(error) as error,sum(warning) as warning FROM t_countsety WHERE id <=%s" % new_ids[table])
                        decimalnums = cursor.fetchone()[0] 
                        tmp_dic['COUNTSETY'] = {}
                        tmp_dic['COUNTSETY']['EMERG'] = int(decimalnums[0]) if decimalnums else 0
                        tmp_dic['COUNTSETY']['ALERT'] = int(decimalnums[1]) if decimalnums else 0
                        tmp_dic['COUNTSETY']['CRITI'] = int(decimalnums[2]) if decimalnums else 0
                        tmp_dic['COUNTSETY']['ERROR'] = int(decimalnums[3]) if decimalnums else 0
                        tmp_dic['COUNTSETY']['WARN'] = int(decimalnums[4]) if decimalnums else 0
                else: tmp_dic['COUNTSETY']['EMERG'] = tmp_dic['COUNTSETY']['ALERT'] = tmp_dic['COUNTSETY']['CRITI'] = tmp_dic['COUNTSETY']['ERROR'] = tmp_dic['COUNTSETY']['WARN'] = 0
        old_counts = data.get('counts')
        for k in old_counts:
            if k == 'COUNTSETY':
                for key in old_counts[k]:
                    old_counts[k][key] = int(old_counts[k][key]) + tmp_dic[k][key]
            else:
                old_counts[k] = int(old_counts[k]) + tmp_dic[k]
        old_countsety = data.get('countsety')
        for key in old_countsety:
            old_countsety[key] = int(old_countsety[key]) + tmp_dic['COUNTSETY'][key]

        new_data = {
                'last_ids': new_ids,
                'counts': old_counts,
                'last_runtime': self.nowtime,
                'countsety': old_countsety
            }
        print "new data : "
        print json.dumps(new_data, indent=4)
        with open(datafile, 'w') as write_file:
            json.dump(new_data,write_file)
    
    def proc(self):
        if os.path.exists(datafile):
            with open(datafile, 'r') as load_file:
                data = json.load(load_file) 
                print 'source data : '
                print data
            if data.get('last_runtime')[5:7] == self.nowtime[5:7]:
                print data.get('last_runtime')
                print self.nowtime
                self.update(data)
            else: self.initdata()
        else:
            self.initdata()

if __name__ == '__main__':
    info = InvadeInfo()
    info.proc()
