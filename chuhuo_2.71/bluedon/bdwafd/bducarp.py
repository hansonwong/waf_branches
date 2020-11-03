import os, sys, re, MySQLdb
import commands
from config import config
from replication import Replication

hadata     = ()
infip      = ''
upscript   = '/usr/local/bluedon/bdwafd/vip-up.py'
downscript = '/usr/local/bluedon/bdwafd/vip-down.py'
rexpucarp  = re.compile(r'/usr/sbin/ucarp')

def gethasets(cursor):
    global hadata
    global infip
    cursor.execute('select is_use,interface,vhid,password,ip from `t_ha_setting`')
    for hadata in cursor.fetchall():
        break

    selsql = "select `ip` from `t_nicset` where nic='%s'" % hadata[1]
    cursor.execute(selsql)
    for data in cursor.fetchall():
        infip = data[0]
        break

def initucarp():
    if not infip:
        return

    ucarpstr = '/usr/sbin/ucarp --interface=' + hadata[1] + ' '
    ucarpstr = ucarpstr + '--srcip=' + infip + ' '
    ucarpstr = ucarpstr + '--vhid=' + str(hadata[2]) + ' '
    ucarpstr = ucarpstr + '--pass=' + str(hadata[3]) + ' '
    ucarpstr = ucarpstr + '--addr=' + hadata[4] + ' '
    ucarpstr = ucarpstr + '--upscript=' + upscript + ' '
    ucarpstr = ucarpstr + '--downscript=' + downscript + ' '
    ucarpstr = ucarpstr + '--daemonize --nomcast'
    os.system(ucarpstr)

def recovery_bridge(cursor):
    selsql = "select `nics` from `t_bridge`"
    cursor.execute(selsql)
    for data in cursor.fetchall():
        buff = data[0].split(",")
        iflen = len(buff)
        for i in range(1,iflen):
            cmdstr = '/sbin/ifconfig %s up' % buff[i]
            os.system(cmdstr)

def killucarp():
    flag = 0
    pfp = os.popen('ps ax | grep ucarp')
    lines = pfp.readlines()
    for line in lines:
        match = rexpucarp.search(line)
        if match:
            flag += 1
    if flag:
        os.system('/usr/bin/killall -9 ucarp')


def clearucarp():
    fifconfig = os.popen("/sbin/ifconfig | grep \"^\\w\"")
    for line in fifconfig:
        info = line.strip().split()
        _, _, sign = info[0].partition(':')
        if sign:
            os.system('/sbin/ifconfig %s down' % info[0])

def allow_mysql_access(iptable, database_ip):
    try:
        # del other ip
        cmd = ("/usr/sbin/%s -nvL INPUT --line-numbers|grep ACCEPT|grep dpt:3306|"
               "awk '{print $1}'") % iptable
        for num in sorted(commands.getoutput(cmd).split(), reverse=True):
            os.system('iptables -D INPUT %s' % num.strip()) 
        # allow ip
        if database_ip:
            os.system('/usr/sbin/%s -A INPUT -s %s -p tcp --dport 3306 -j ACCEPT'
                      % (iptable, database_ip))
        # deny other ip
        os.system('iptables -D INPUT -p tcp --dport 3306 -j DROP')
        os.system('iptables -A INPUT -p tcp --dport 3306 -j DROP')
    except Exception, e:
        print e


if __name__ == '__main__':
    conn = MySQLdb.connect(**config['db'])
    cursor = conn.cursor()
    killucarp()
    try:
        if len(sys.argv) > 2:
            rp = Replication()
            # if (sys.argv[1] == '1' and sys.argv[2] == '0') or (sys.argv[1] == '0'and sys.argv[2] == '1'):
            if sys.argv[1] != sys.argv[2]:
                cursor.execute('update t_ha_setting set had_sync=0')
                rp.set_opposync(0)
    except Exception, e:
        print e

    if len(sys.argv) > 1 and sys.argv[1] == 'deploy':
        cursor.execute("select is_use, interface from `t_ha_setting`")
        for data in cursor.fetchall():
            if data[0] and data[1]:
                os.system('/sbin/ifconfig %s:1 down' % data[1])
            cursor.execute("update `t_ha_setting` set is_use='0', `state`='backup', ip=''")
            conn.commit()
            cursor.close()
            conn.close()
            exit(0)

    gethasets(cursor)
    if hadata[0]:
        clearucarp()
        initucarp()
    else:
        if hadata[1]:
            os.system('/sbin/ifconfig %s:1 down' % hadata[1])

        cursor.execute("update `t_ha_setting` set `state`='backup'")
    cursor.execute("select database_ip from `t_ha_setting`")
    database_ip = cursor.fetchone()[0]
    # allow_mysql_access('iptables', database_ip)

    conn.commit()
    cursor.close()
    conn.close()
