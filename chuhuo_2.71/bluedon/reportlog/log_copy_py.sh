#! /bin/sh

###########################
#   ADD FILE HERE IF NEW  #
###########################
PY_LIST='
config1.py
crontab.py
daemon.py
ip_extraction.py
if_watch.py
load_infile.py 
log_app_names.py
log_backup_lib.py
log_bak.sh
log_clear.py
log_cover.sh
log_config.py
log_mail_config.py
log_query.py
log_size_record.py
log_split_app_admin.py
log_split_ddos.py
log_split_evil_code.py
log_split_firewall.py
log_split_info_leak.py
log_split_ips.py
log_split_url.py
log_split_webaudit.py
log_statistics.py
mysql_get_tblog3.py
mysql_get_tblog.py
mysql_log_backup.py
mysql_log_daemon.py
multi_process.py
multi_process2.py
multi_process3.py
mysql_daemon_restart.sh
statistics.py
system_running_time.py
system_usage.py
traffic_statistic.py
bd_log_cron.bak
bd_logrotate.bak
bd_logrotate_cron.bak
./log/log_config.ini
/etc/cron.d/bd_log_cron
/etc/cron.d/bd_logrotate_cron
/etc/logrotate.d/bd_logrotate
'

PY_PATH='/usr/local/bluedon/'
PY_DEST_PATH='./log_py_backup/'


#Run mode selection
if [ $# -eq 0  ];then
	echo 'Run as Default...'
	echo 'Default PY_PATH='$PY_PATH
	echo 'Default PY_DEST_PATH='$PY_DEST_PATH
else
	#get source and destination path
	echo 'Run in interactive mode...'
	printf 'Input PY_PATH(The path of *.py):'
	read -r PY_PATH
	printf 'Input PY_DEST_PATH(The backup path):'
	read -r PY_DEST_PATH
fi

#validate the path
PY_PATH=${PY_PATH%/}/
PY_DEST_PATH=${PY_DEST_PATH%/}/

#make dir if not exists
mkdir -p $PY_DEST_PATH

for i in $PY_LIST
do
	echo $i
	cp -f $PY_PATH$i $PY_DEST_PATH
done


dir=`pwd`
echo $dir
cd $PY_DEST_PATH
tar -czvf $dir/log_py.tar.gz ./*.*

echo 'Backup Done!'

