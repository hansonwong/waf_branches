#!/bin/sh

/usr/bin/cp -vf /usr/local/bluedon/conf/systemctl/*.service /usr/lib/systemd/system

echo '****************************************************************************'

systemctl enable dpdk-init.service
systemctl enable dpdk.service
systemctl enable firewall-python-init.service
systemctl enable firewall-python-daemon.service
systemctl enable mysql_log_daemon.service
systemctl enable get_statistics_data.service
systemctl enable mysqld.service
systemctl enable php-fpm.service
systemctl enable php-nginx.service
systemctl enable firewall-iptables-log.service
systemctl enable firewall_autoupdate_cron_task.timer
# systemctl enable bdwaf.service 
