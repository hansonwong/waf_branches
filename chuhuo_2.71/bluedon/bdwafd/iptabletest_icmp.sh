#!/bin/bash

iptables -F
iptables -X

iptables -N ICMP-SCAN
#iptables -N ICMP-LIMIT

iptables -F ICMP-SCAN
#iptables -F ICMP-LIMIT

iptables -A FORWARD -p icmp -j ICMP-SCAN
#iptables -A ICMP-SCAN -j ICMP-LIMIT
#iptables -A ICMP-SCAN -j LOG --log-prefix "Probable_ddos:icmp-flood"
iptables -A ICMP-SCAN -m hashlimit --hashlimit-name ICMP-SCAN --hashlimit 10/sec --hashlimit-burst 2 --hashlimit-mode srcip -j ACCEPT
#iptables -A ICMP-SCAN -m limit --limit 3/min -j LOG --log-prefix "Probable ddos:icmp-flood "
iptables -A ICMP-SCAN -j LOG --log-prefix "Probable ddos:icmp-flood "
iptables -A ICMP-SCAN -j DROP
#iptables -A ICMP-LIMIT -m limit --limit 10/sec --limit-burst 10 -j RETURN
#iptables -A ICMP-LIMIT -j LOG --log-prefix "Probable_ddos:icmp-flood "
#iptables -A ICMP-LIMIT -j DROP

