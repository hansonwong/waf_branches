#!/bin/sh

services="\
ips.service
firewall-python-init.service
firewall-python-daemon.service
dpdk-init.service
dpdk.service
mysql_log_daemon.service
get_statistics_data.service
mysqld.service
php-fpm.service
php-nginx.service
firewall-iptables-log.service
bdwaf.service
firewall_autoupdate_cron_task.timer"

for i in ${services}; do
    systemctl stop $i
    systemctl disable $i
    rm -vf /usr/lib/systemd/system/$i
done

cp -f /usr/local/bluedon/conf/ips.service.bak /usr/lib/systemd/system/ips.service
