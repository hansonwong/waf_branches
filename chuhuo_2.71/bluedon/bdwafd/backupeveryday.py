import os
import time
import socket
import psutil

db_user = 'root'
db_password = 'bd_123456'
db = 'waf'
base_dir = '/var/backup/'

code_python = ['/usr/local/bluedon/bdwafd/']
code_c = ['/root/new/',
          '/root/bluedon_waf/',
          '/home/ng_platform/']

def gen_info():
    datestr = time.strftime('%m-%d',time.localtime(time.time()))
    # nic_info = psutil.net_if_addrs()
    # for key in nic_info:
    #     if key.lower().startswith(('enp','eth0')):
    #         print nic_info[key]
    return datestr

def bkpython(bkdir):
    os.system('tar czfP %s/waf_bdwafd.tar.gz /usr/local/bluedon/ --exclude log/*' % bkdir)

def bksql(bkdir):
    cmd = "mysqldump -u " + db_user + " -p" + db_password + " " + db + " > " + bkdir + "/" + db + ".sql"
    os.system(cmd)

def bkc(bkdir):
    os.system('tar czfP %s/new.tar.gz /root/new/' % bkdir)
    os.system('tar czfP %s/bluedon_waf.tar.gz /root/bluedon_waf/' % bkdir)
    os.system('tar czfP %s/ng_platform.tar.gz /home/ng_platform/' % bkdir)
    
def bkphp(bkdir):
    os.system('tar czfP %s/waf_php.tar.gz /Data/apps/wwwroot/waf/' % bkdir)

def bknginx(bkdir):
    os.system('tar czfP %s/nginx.tar.gz /usr/local/bdwaf/conf/ /usr/local/bdwaf/conf_proxy/ /usr/local/bdwaf/conf_tproxy/' % bkdir)

def bksys(bkdir):
    os.system('cp /etc/sysctl.conf %s/sysctl.conf' % bkdir)
    os.system('cp /etc/crontab %s/crontab' % bkdir)


if __name__ == "__main__":
    backup_dir = base_dir + gen_info() 
    if not os.path.exists(backup_dir):
        os.system('mkdir %s' % backup_dir)
    bksql(backup_dir)
    bkpython(backup_dir)
    bkc(backup_dir)
    bkphp(backup_dir)
    bknginx(backup_dir)
    bksys(backup_dir)
