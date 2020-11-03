#!/usr/bin/env python
# -*-coding:utf-8-*-

import os

def iptables_init(iptable):
    """
    创建安全策略、SNAT、DNAT、源IP连接数控制、目的IP连接数控制自定义链
    初始化%s规则
    """

    os.system('/usr/sbin/%s -t filter -F'%iptable)
    os.system('/usr/sbin/%s -t filter -X'%iptable)
    os.system('/usr/sbin/%s -t nat -F'%iptable)
    os.system('/usr/sbin/%s -t nat -X'%iptable)
    os.system('/usr/sbin/%s -t mangle -F'%iptable)
    os.system('/usr/sbin/%s -t mangle -X'%iptable)

    ############################################
    #1. filter table
    ############################################
    os.system('/usr/sbin/%s -N FWINPUT'%iptable)
    os.system('/usr/sbin/%s -N CONNLIMIT_SRC'%iptable)
    os.system('/usr/sbin/%s -N CONNLIMIT_DST'%iptable)
    os.system('/usr/sbin/%s -N IP_MAC_CHECK'%iptable)          #ip-mac
    os.system('/usr/sbin/%s -I IP_MAC_CHECK -j DROP'%iptable)  #ip-mac
    os.system('/usr/sbin/%s -N IDSFW'%iptable)                 #ids-ipt
    os.system('/usr/sbin/%s -N FWFORWARD'%iptable)
    os.system('/usr/sbin/%s -N SECURITYPOLICY'%iptable)
    os.system('/usr/sbin/%s -N FW_FILTER_AUTH'%iptable)
    os.system('/usr/sbin/%s -N FW_FILTER_AUTH_TA'%iptable)
    os.system('/usr/sbin/%s -N FW_FILTER_AUTH_TA1'%iptable)
    os.system('/usr/sbin/%s -N ANTI_CAMERA'%iptable)
    os.system('/usr/sbin/%s -N ANTI_SCAN'%iptable)
    os.system('/usr/sbin/%s -N FWOUTPUT'%iptable)
    os.system('/usr/sbin/%s -N TSE_CHAIN'%iptable)
    os.system('/usr/sbin/%s -N WIFI_AUDIT'%iptable)
    os.system('/usr/sbin/%s -N SSL_VPN_FORWARD'%iptable)
    os.system('/usr/sbin/%s -N SCM'%iptable)
    os.system('/usr/sbin/%s -N AUTH_FWINPUT'%iptable)
    os.system('/usr/sbin/%s -N IPSECCLIENTS'%iptable)


    #1.1 INPUT chain(filter table)
    os.system('/usr/sbin/%s -A INPUT -j FWINPUT'%iptable)
    os.system('/usr/sbin/%s -A INPUT -m hashlimit --hashlimit 5/minute --hashlimit-mode srcip,dstip --hashlimit-name input_log -j LOG --log-prefix "ipt_log=DROP "'%iptable) # LOG
    os.system('/usr/sbin/%s -A INPUT -j DROP'%iptable) # MUST

    os.system('/usr/sbin/%s -A FORWARD -j WIFI_AUDIT'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j CONNLIMIT_SRC'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j CONNLIMIT_DST'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j FWFORWARD'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j IDSFW'%iptable)
    #os.system('/usr/sbin/%s -A FORWARD -j SECURITYPOLICY'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j ANTI_CAMERA'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j ANTI_SCAN'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j TSE_CHAIN'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j SCM'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -i tun0 -j SSL_VPN_FORWARD'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j SECURITYPOLICY'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -m mark --mark 0xfff/0xfff -j ACCEPT'%iptable)
    os.system('/usr/sbin/%s -A FORWARD -j DROP'%iptable) # MUST

    #1.3 OUTPUT chain(filter table)
    os.system('/usr/sbin/%s -A OUTPUT -j FWOUTPUT'%iptable)

    ############################################
    #2. nat table
    ############################################
    os.system('/usr/sbin/%s -t nat -N FWSNAT'%iptable)
    os.system('/usr/sbin/%s -t nat -N FWPREROUTING'%iptable)
    os.system('/usr/sbin/%s -t nat -N FWPOSTROUTING'%iptable)
    os.system('/usr/sbin/%s -t nat -N FW_NAT_AUTH'%iptable)
    os.system('/usr/sbin/%s -t nat -N FW_NAT_AUTH_TA'%iptable)
    os.system('/usr/sbin/%s -t nat -N IPSECVPN'%iptable)

    os.system('/usr/sbin/%s -t nat -N FW_NAT_AUTH_TA1'%iptable)
    os.system('/usr/sbin/%s -t nat -N FWDNAT'%iptable)

    #2.1 PREROUTING(nat table)
    os.system('/usr/sbin/%s -t nat -A PREROUTING -j FWPREROUTING'%iptable)
    os.system('/usr/sbin/%s -t nat -A PREROUTING -j FWDNAT'%iptable)

    #2.2 POSTROUTING(nat table)
    os.system('/usr/sbin/%s -t nat -A POSTROUTING -j FWPOSTROUTING'%iptable)
    os.system('/usr/sbin/%s -t nat -A POSTROUTING -j IPSECVPN'%iptable)
    os.system('/usr/sbin/%s -t nat -A POSTROUTING -j FWSNAT'%iptable)

    ############################################
    #3. mangle table
    ############################################
    os.system('/usr/sbin/%s -t mangle -N APPMARK'%iptable)
    os.system('/usr/sbin/%s -t mangle -N TC_RULES_CHAIN'%iptable)
    os.system('/usr/sbin/%s -t mangle -N POLICY_ROUTE_MARK'%iptable)
    os.system('/usr/sbin/%s -t mangle -N NF_QUEUE_CHAIN'%iptable)
    os.system('/usr/sbin/%s -t mangle -A PREROUTING -j POLICY_ROUTE_MARK'%iptable)

    #3.1 PREROUTING(mangle table)
    os.system('/usr/sbin/%s -t mangle -I PREROUTING -j APPMARK'%iptable)
    os.system('/usr/sbin/%s -t mangle -I FORWARD -j TC_RULES_CHAIN'%iptable)

    ############################################
    # raw table
    ############################################
    os.system('/usr/sbin/%s -t raw -F'%iptable)
    os.system('/usr/sbin/%s -t raw -X'%iptable)
    os.system('/usr/sbin/%s -t raw -I OUTPUT -o lo -j NOTRACK'%iptable)

    ############################################
    #4. other init
    ############################################
    os.system('/usr/local/sbin/ipset -N authed_set iphash')

    #http https
    if iptable == "iptables":
        os.system('/usr/sbin/%s -A FWINPUT -s 127.0.0.1 -j ACCEPT'%iptable)
        # os.system('/usr/sbin/%s -A FWINPUT -p tcp --dport 80 -j ACCEPT'%iptable)
        # 用户认证-短信认证，向百信通推消息
        # os.system('/usr/sbin/%s -A FWINPUT -p tcp --dport 9999 -j ACCEPT'%iptable)
        # os.system('/usr/sbin/%s -A FWINPUT -p tcp --sport 9999 -j ACCEPT'%iptable)
       
    elif iptable == "ip6tables":
        os.system('/usr/sbin/%s -A FWINPUT -s ::1 -j ACCEPT'%iptable)

    if iptable == 'iptables':
        # ping, firewall can ping other v4 ip
        os.system('/usr/sbin/%s -I FWINPUT -p icmp --icmp-type 0 -j ACCEPT'%iptable)

    #for FW to traceroute remote_ip  (only for ipv4)
    if iptable == "iptables":
        os.system('/usr/sbin/%s -A FWINPUT -p udp -m state --state ESTABLISHED -m udp --sport 53 -j ACCEPT'%iptable)
        os.system('/usr/sbin/%s -A FWINPUT -p tcp -m state --state ESTABLISHED -m tcp --sport 53 -j ACCEPT'%iptable)
        os.system('/usr/sbin/%s -A FWINPUT -p icmp -m icmp --icmp-type 11 -j ACCEPT'%iptable)
        os.system('/usr/sbin/%s -A FWINPUT -p icmp -m icmp --icmp-type 3 -j ACCEPT'%iptable)

    # accept loopback
    os.system('/usr/sbin/%s -I FWINPUT -i lo -j ACCEPT'%iptable)

    #mysql ,debug only
    # os.system('/usr/sbin/%s -I FWINPUT -p udp --dport 3306 -j ACCEPT'%iptable)
    # os.system('/usr/sbin/%s -I FWINPUT -p tcp --dport 3306 -j ACCEPT'%iptable)

    os.system('/usr/local/sbin/ipset -N auth_local_mode iphash')
    os.system('/usr/local/sbin/ipset -A auth_local_mode 127.0.0.1')
    os.system('/usr/local/sbin/ipset -A auth_local_mode 224.0.0.18')
    os.system('/usr/local/sbin/ipset -A auth_local_mode 225.0.0.50')

    #scan photograph
    #os.system('/usr/local/sbin/ipset create blacklist hash:ip timeout 180')
    os.system('/usr/local/sbin/ipset create scan_blist_v4 hash:ip timeout 180')
    os.system('/usr/local/sbin/ipset create scan_blist_v6 hash:net family inet6 timeout 180')
    if iptable=='iptables':
        os.system('/usr/sbin/%s -A ANTI_SCAN -m set --match-set scan_blist_v4 src -j DROP'%iptable)
    if iptable=='ip6tables':
        os.system('/usr/sbin/%s -A ANTI_SCAN -m set --match-set scan_blist_v6 src -j DROP'%iptable)

    os.system('/usr/sbin/%s -A ANTI_CAMERA -m set --match-set blacklist src -j DROP'%iptable)
    if iptable == 'iptables':
        os.system('/usr/sbin/iptables -I SSL_VPN_FORWARD -i tun0 -s 0.0.0.0/0 -d 0.0.0.0/0 -j DROP')

    ############################################
    #npi set mark
    ############################################
    """with open('/usr/local/bluedon/%s_ndpi','r') as fr:
         for line in fr:
             line=line.strip('\n')
             #print line
             os.system(line)"""

if __name__=="__main__":
   iptables_init('iptables')
   iptables_init('ip6tables')

