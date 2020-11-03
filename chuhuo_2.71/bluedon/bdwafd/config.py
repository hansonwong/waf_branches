#!/usr/bin/env python
# -*- coding: utf-8 -*-

config={}

# debug flag
config['debug'] = True

# default working direcotry, can be overset by command args 
config['cwd'] = '/usr/local/bluedon/bdwafd'

# database config
config['db'] = {}
config['db']['host'] = 'localhost'
config['db']['user'] = 'root'
config['db']['passwd'] = 'bd_123456'
config['db']['db'] = 'waf'
config['db']['port'] = 3306
config['db']['unix_socket']='/tmp/mysql3306.sock'
config['db']['charset'] = 'utf8'
config['db']['use_unicode'] = False

config['dbacc'] = {}
config['dbacc']['host'] = 'localhost'
config['dbacc']['user'] = 'root'
config['dbacc']['passwd'] = 'bd_123456'
config['dbacc']['db'] = 'logs'
config['dbacc']['port'] = 3306
config['dbacc']['unix_socket']='/tmp/mysql3306.sock'
config['dbacc']['charset'] = 'utf8'
config['dbacc']['use_unicode'] = False

config['dbfw'] = {}
config['dbfw']['host'] = 'localhost'
config['dbfw']['user'] = 'root'
config['dbfw']['passwd'] = 'bd_123456'
config['dbfw']['db'] = 'db_firewall'
config['dbfw']['port'] = 3306
config['dbfw']['unix_socket']='/tmp/mysql3306.sock'
#config['db']['unix_socket']='/var/run/mysqld/mysqld.sock'
config['dbfw']['charset'] = 'utf8'
config['dbfw']['use_unicode'] = False

# redis connect
config['redis'] = {}
config['redis']['host'] = 'localhost'
config['redis']['port'] = 6379

config['dbsecurity'] = {}
config['dbsecurity']['host'] = 'localhost'
config['dbsecurity']['user'] = 'root'
config['dbsecurity']['passwd'] = 'bd_123456'
config['dbsecurity']['db'] = 'security'
config['dbsecurity']['port'] = 3306
#config['db']['unix_socket']='/var/run/mysqld/mysqld.sock'
config['dbsecurity']['charset'] = 'utf8'
config['dbsecurity']['use_unicode'] = False


# logger config
config['logger'] = {}
config['logger']['bdinit'] = {}
config['logger']['bdinit']['level'] = 'DEBUG' # DEBUG, INFO, WARNING, ERROR, CRITICAL
config['logger']['bdinit']['path'] = '/var/log/bdwafd/bdinit.log'
config['logger']['cleardisk'] = {}
config['logger']['cleardisk']['level'] = 'INFO' # DEBUG, INFO, WARNING, ERROR, CRITICAL
config['logger']['cleardisk']['path'] = '/var/log/bdwafd/cleardisk.log'
config['logger']['sysupdate'] = {}
config['logger']['sysupdate']['level'] = 'INFO' # DEBUG, INFO, WARNING, ERROR, CRITICAL
config['logger']['sysupdate']['path'] = '/var/log/bdwafd/sysupdate.log'
config['logger']['main'] = {}
config['logger']['main']['level'] = 'INFO' # DEBUG, INFO, WARNING, ERROR, CRITICAL
config['logger']['main']['path'] = '/var/log/bdwafd/main.log'
config['logger']['webtask'] = {}
config['logger']['webtask']['level'] = 'INFO' # DEBUG, INFO, WARNING, ERROR, CRITICAL
config['logger']['webtask']['path'] = '/var/log/bdwafd/webtask.log'
config['logger']['audit'] = {}
config['logger']['audit']['level'] = 'INFO' # DEBUG, INFO, WARNING, ERROR, CRITICAL
config['logger']['audit']['path'] = '/var/log/bdwafd/audit.log'
config['logger']['audittask'] = {}
config['logger']['audittask']['level'] = 'INFO' # DEBUG, INFO, WARNING, ERROR, CRITICAL
config['logger']['audittask']['path'] = '/var/log/bdwafd/audittask.log'
config['logger']['ntpdate'] = {}
config['logger']['ntpdate']['level'] = 'INFO' # DEBUG, INFO, WARNING, ERROR, CRITICAL
config['logger']['ntpdate']['path'] = '/var/log/bdwafd/ntpdate.log'


# crontab 
config['cron'] = {}
config['cron']['filepath'] = '/etc/cron.d/bdwaf'
config['cron']['crontab'] = '''
* * * * * root sudo /usr/local/bluedon/bdwafd/bdwafd.py -s start #bdwafd
* * * * * root /usr/local/bluedon/bdwafd/bdauditd.py -s start #bdauditd
'''

# system reboot run this script
config['shell'] = {}
config['bootscript'] = '/usr/local/bluedon/bdwafd/bdinit.py'
config['shell']['bdinit'] = '/usr/local/bluedon/bdwafd/bdinit.py'
config['shell']['mkfifo'] = '/usr/local/bluedon/bdwafd/try_make_fifo.py'


# modsec
config['modsecruledir'] = {'/usr/local/bdwaf/conf/custom_rules'
                           '/usr/local/bdwaf/conf_proxy/custom_rules',
                           '/usr/local/bdwaf/conf_tproxy/custom_rules'}
# admin website
config['adminwww'] = '/Data/apps/wwwroot/waf/www/web'

# bridge config
config['bridge'] = {}
config['bridge']['br'] = 'br0'
config['bridge']['eth1'] = 'eth5'
config['bridge']['eth2'] = 'eth6'

config['htmlmodedir'] = '/Data/apps/wwwroot/waf/cache/data/mode/'


config['reverseproxy'] = {'service': 'bdwaf.proxy',
                          'conf_path': '/usr/local/bdwaf/conf_proxy',
                          'logs_path': '/usr/local/bdwaf/logs_proxy',
                          'workmode': ('route', 'nat',),
                          }

config['tproxy'] = {'service': 'bdwaf.tproxy',
                    'conf_path': '/usr/local/bdwaf/conf_tproxy',
                    'logs_path': '/usr/local/bdwaf/logs_tproxy',
                    'workmode': ('tproxy',),
                    }

config['bridge'] = {'service': 'bdwaf.bridge',
                    'conf_path': '/usr/local/bdwaf/conf',
                    'logs_path': '/usr/local/bdwaf/logs_bridge',
                    'workmode': ('route', 'nat', 'bridge', 'virtual', 'bypass', 'mirror', 'redundancy'),
                    }


if __name__ == '__main__':
    import json
    print json.dumps(config, encoding='utf-8', ensure_ascii=False, indent=4)
