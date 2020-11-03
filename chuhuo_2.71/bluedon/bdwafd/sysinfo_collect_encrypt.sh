#!/bin/sh 

# System Infomation Collector and encryptor

BDWAFDIR=/usr/local/bdwaf
BDWAFDDIR=/var/log/bdwafd
TMPDIR=/usr/local/bluedon/bdwafd/tmp
WWWDIR=/var/wafDownload/web/cache

mkdir -p $TMPDIR/sysinfo/bdwaf/conf
mkdir -p $TMPDIR/sysinfo/bdwaf/conf_proxy
mkdir -p $TMPDIR/sysinfo/bdwaf/conf_tproxy
mkdir -p $TMPDIR/sysinfo/logs_bridge
mkdir -p $TMPDIR/sysinfo/logs_proxy
mkdir -p $TMPDIR/sysinfo/logs_tproxy
mkdir -p $WWWDIR

tail -n 1000 /var/log/secure > $TMPDIR/sysinfo/secure
tail -n 1000 /var/log/messages > $TMPDIR/sysinfo/messages

tail -n 1000 ${BDWAFDIR}/logs_bridge/error.log > $TMPDIR/sysinfo/logs_bridge/error.log
tail -n 1000 ${BDWAFDIR}/logs_bridge/access.log > $TMPDIR/sysinfo/logs_bridge/access.log
tail -n 1000 ${BDWAFDIR}/logs_bridge/modsec_audit.log > $TMPDIR/sysinfo/logs_bridge/modsec_audit.log
tail -n 1000 ${BDWAFDIR}/logs_bridge/modsec_debug.log > $TMPDIR/sysinfo/logs_bridge/modsec_debug.log
tail -n 1000 ${BDWAFDIR}/logs_bridge/syslog/error_syslog.log > $TMPDIR/sysinfo/logs_bridge/syslog.log

tail -n 1000 ${BDWAFDIR}/logs_proxy/error.log > $TMPDIR/sysinfo/logs_proxy/error.log
tail -n 1000 ${BDWAFDIR}/logs_proxy/access.log > $TMPDIR/sysinfo/logs_proxy/access.log
tail -n 1000 ${BDWAFDIR}/logs_proxy/modsec_audit.log > $TMPDIR/sysinfo/logs_proxy/modsec_audit.log
tail -n 1000 ${BDWAFDIR}/logs_proxy/modsec_debug.log > $TMPDIR/sysinfo/logs_proxy/modsec_debug.log
tail -n 1000 ${BDWAFDIR}/logs_proxy/syslog/error_syslog.log > $TMPDIR/sysinfo/logs_proxy/syslog.log

tail -n 1000 ${BDWAFDIR}/logs_tproxy/error.log > $TMPDIR/sysinfo/logs_tproxy/error.log
tail -n 1000 ${BDWAFDIR}/logs_tproxy/access.log > $TMPDIR/sysinfo/logs_tproxy/access.log
tail -n 1000 ${BDWAFDIR}/logs_tproxy/modsec_audit.log > $TMPDIR/sysinfo/logs_tproxy/modsec_audit.log
tail -n 1000 ${BDWAFDIR}/logs_tproxy/modsec_debug.log > $TMPDIR/sysinfo/logs_tproxy/modsec_debug.log
tail -n 1000 ${BDWAFDIR}/logs_tproxy/syslog/error_syslog.log > $TMPDIR/sysinfo/logs_tproxy/syslog.log

tail -n 1000 ${BDWAFDDIR}/audit.log > $TMPDIR/sysinfo/bdwafd_audit.log
tail -n 1000 ${BDWAFDDIR}/audittask.log > $TMPDIR/sysinfo/bdwafd_audittask.log
tail -n 1000 ${BDWAFDDIR}/main.log > $TMPDIR/sysinfo/bdwafd_main.log
tail -n 1000 ${BDWAFDDIR}/webtask.log > $TMPDIR/sysinfo/bdwafd_webtask.log
tail -n 1000 ${BDWAFDDIR}/bdinit.log > $TMPDIR/sysinfo/bdinit.log

cp ${BDWAFDIR}/conf/modsecurity.conf $TMPDIR/sysinfo/bdwaf/conf/modsecurity.conf
cp ${BDWAFDIR}/conf/nginx.conf $TMPDIR/sysinfo/bdwaf/conf/nginx.conf
cp ${BDWAFDIR}/conf/activated_rules/limits.conf $TMPDIR/sysinfo/bdwaf/conf/limits.conf
cp ${BDWAFDIR}/conf/sites/proxy.conf $TMPDIR/sysinfo/bdwaf/conf/proxy.conf

cp ${BDWAFDIR}/conf_proxy/modsecurity.conf $TMPDIR/sysinfo/bdwaf/conf_proxy/modsecurity.conf
cp ${BDWAFDIR}/conf_proxy/nginx.conf $TMPDIR/sysinfo/bdwaf/conf_proxy/nginx.conf
cp ${BDWAFDIR}/conf_proxy/activated_rules/limits.conf $TMPDIR/sysinfo/bdwaf/conf_proxy/limits.conf
cp ${BDWAFDIR}/conf_proxy/sites/proxy.conf $TMPDIR/sysinfo/bdwaf/conf_proxy/proxy.conf

cp ${BDWAFDIR}/conf_tproxy/modsecurity.conf $TMPDIR/sysinfo/bdwaf/conf_tproxy/modsecurity.conf
cp ${BDWAFDIR}/conf_tproxy/nginx.conf $TMPDIR/sysinfo/bdwaf/conf_tproxy/nginx.conf
cp ${BDWAFDIR}/conf_tproxy/activated_rules/limits.conf $TMPDIR/sysinfo/bdwaf/conf_tproxy/limits.conf
cp ${BDWAFDIR}/conf_tproxy/sites/proxy.conf $TMPDIR/sysinfo/bdwaf/conf_tproxy/proxy.conf

iptables -t mangle -L > $TMPDIR/sysinfo/iptables_mangle
iptables -t filter -L > $TMPDIR/sysinfo/iptables_filter
iptables -t nat -L > $TMPDIR/sysinfo/iptables_filter
ifconfig > $TMPDIR/sysinfo/ifconfig
route -n > $TMPDIR/sysinfo/route_n
top -b -n 1 > $TMPDIR/sysinfo/top_b_n_1
ps aux > $TMPDIR/sysinfo/ps_aux
free > $TMPDIR/sysinfo/free
netstat -lp > $TMPDIR/sysinfo/netstat_lp
netstat -p > $TMPDIR/sysinfo/netstat_p

cd $TMPDIR
tar czf sysinfo.tar.gz sysinfo/
openssl enc -aes-256-cbc -in sysinfo.tar.gz -out sysinfo.data -pass pass:bdwaf
rm sysinfo.tar.gz sysinfo/ -rf
mv sysinfo.data $WWWDIR

exit 0
