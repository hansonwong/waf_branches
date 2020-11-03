#!/bin/sh

#INPUT and FORWARD of filter
/usr/sbin/iptables -t filter -I INPUT 1 -j FW_FILTER_AUTH_TA1
/usr/sbin/iptables -t filter -I FORWARD -j FW_FILTER_AUTH_TA1
/usr/sbin/iptables -t filter -I INPUT 1 -j FW_FILTER_AUTH_TA
/usr/sbin/iptables -t filter -I FORWARD -j FW_FILTER_AUTH_TA
/usr/sbin/iptables -t filter -I FWINPUT -j AUTH_FWINPUT

#FILTER FW_FILTER_AUTH
/usr/sbin/iptables -A FW_FILTER_AUTH -m set ! --match-set authed_set src -p tcp --dport 6666 -j ACCEPT
/usr/sbin/iptables -A FW_FILTER_AUTH -p tcp  --dport 4443 -j ACCEPT
/usr/sbin/iptables -A FW_FILTER_AUTH -p udp --dport 53 -g FW_FILTER_AUTH_TA1
/usr/sbin/iptables -A FW_FILTER_AUTH -p udp --sport 53 -g FW_FILTER_AUTH_TA1
/usr/sbin/iptables -A FW_FILTER_AUTH -m set --match-set auth_local_mode dst -g FW_FILTER_AUTH_TA1
/usr/sbin/iptables -A FW_FILTER_AUTH -m set --match-set auth_local_mode src -g FW_FILTER_AUTH_TA1
/usr/sbin/iptables -A FW_FILTER_AUTH -m set --match-set authed_set dst -g FW_FILTER_AUTH_TA1
/usr/sbin/iptables -A FW_FILTER_AUTH -m set --match-set authed_set src -g FW_FILTER_AUTH_TA1 
/usr/sbin/iptables -A FW_FILTER_AUTH -j DROP

#FILTER AUTH_FWINPUT
/usr/sbin/iptables -A AUTH_FWINPUT -p tcp --dport 389 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p udp --dport 389 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p tcp --sport 389 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p udp --sport 389 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p tcp --dport 636 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p udp --dport 636 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p tcp --sport 636 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p udp --sport 636 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p tcp --dport 1812 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p udp --dport 1812 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p tcp --sport 1812 -j ACCEPT
/usr/sbin/iptables -A AUTH_FWINPUT -p udp --sport 1812 -j ACCEPT 

#PREROUTING of nat
/usr/sbin/iptables -t nat -I PREROUTING -j FW_NAT_AUTH_TA1
/usr/sbin/iptables -t nat -I PREROUTING -j FW_NAT_AUTH_TA

