#!/bin/sh

#clean ipset authed_set
/usr/local/sbin/ipset -F authed_set

#clean auth rule
/usr/sbin/iptables -t nat -F FW_NAT_AUTH
/usr/sbin/iptables -t filter -F FW_FILTER_AUTH

#delete mount 
/usr/sbin/iptables -t nat -D PREROUTING -j FW_NAT_AUTH_TA
/usr/sbin/iptables -t filter -D INPUT -j FW_FILTER_AUTH_TA
/usr/sbin/iptables -t filter -D FORWARD -j FW_FILTER_AUTH_TA
/usr/sbin/iptables -t nat -D PREROUTING -j FW_NAT_AUTH_TA1
/usr/sbin/iptables -t filter -D INPUT -j FW_FILTER_AUTH_TA1
/usr/sbin/iptables -t filter -D FORWARD -j FW_FILTER_AUTH_TA1
/usr/sbin/iptables -t filter -D FWINPUT -j AUTH_FWINPUT

#clean AUTH_FWINPUT
/usr/sbin/iptables -t filter -F AUTH_FWINPUT
