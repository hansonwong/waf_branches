#!/usr/bin/env python
#-*-coding:utf-8-*-

import time
import os
import sys
from config import config
from db import conn_scope


KEEPALIVED_MB_CONF = '''! Configuration File for keepalived

global_defs {
   router_id SERVER_%s
}

vrrp_script chk {
    script /usr/local/bluedon/bdwafd/check.py
    interval 1
    weight -20
}

vrrp_instance VI_1 {
    state MASTER
    interface %s
    virtual_router_id 51
    priority %s #120
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        %s #172.16.5.136
    }

    track_script {
        chk
    }
    notify_master /usr/local/bluedon/bdwafd/haup.py
    notify_backup /usr/local/bluedon/bdwafd/hadown.py
}
'''

KEEPALIVED_MM_CONF = '''! Configuration File for keepalived

global_defs {
   router_id SERVER_%s
}

vrrp_script chk {
    script /usr/local/bluedon/bdwafd/check.py
    interval 1
    weight -20
}

vrrp_instance VI_1 {
    state MASTER
    interface %s
    virtual_router_id 51
    priority %s #120
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        %s #172.16.5.136
    }

    track_script {
        chk
    }
    notify_master /usr/local/bluedon/bdwafd/haup.py
    notify_backup /usr/local/bluedon/bdwafd/hadown.py
}

vrrp_instance VI_2 {
    state BACKUP
    interface %s
    virtual_router_id 52
    priority %s #120
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
        %s #172.16.5.136
    }

    track_script {
        chk
    }
    notify_master /usr/local/bluedon/bdwafd/haup.py
    notify_backup /usr/local/bluedon/bdwafd/hadown.py
}

'''


def haset():
    os.system('service keepalived stop')
    if len(sys.argv) > 1 and sys.argv[1] == 'deploy':
        with conn_scope(**config['db']) as (conn, cursor):
            cursor.execute("select is_use, type, interface, ip, ip_backup from `t_ha_setting`")
            data = cursor.fetchall()[0]
            if data[0] and data[2]:
                if data[1] == 1:
                    conf = KEEPALIVED_MB_CONF%(str(int(time.time()))[-4:], data[2], 110, data[3])
                if data[1] == 2:
                    conf = KEEPALIVED_MM_CONF%(str(int(time.time()))[-4:], data[2], 120, data[3], data[2], 110, data[4])
                with open('/etc/keepalived/keepalived.conf', 'w') as fp:
                    fp.seek(0)
                    fp.write(conf)
                os.system('service keepalived restart')


if __name__ == '__main__':
    haset()
