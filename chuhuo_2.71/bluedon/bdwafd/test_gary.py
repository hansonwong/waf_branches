from config_sql import fetchone_sql
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')

sql = 'select modelname from t_ruleset '

a = fetchone_sql(sql)[0]

print a
