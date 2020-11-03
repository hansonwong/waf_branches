#!/bin/bash

iptables -F
iptables -X

iptables -N UDP-SCAN
iptables -N UDP-LIMIT

iptables -F UDP-SCAN
iptables -F UDP-LIMIT

iptables -A FORWARD -p udp -j UDP-SCAN
iptables -A UDP-SCAN -j UDP-LIMIT
iptables -A UDP-SCAN -m hashlimit --hashlimit-name UDP-SCAN --hashlimit 20/sec --hashlimit-burst 20 --hashlimit-mode srcip -j ACCEPT
#iptables -A FORWARD -p udp -m limit --limit 3/min -j LOG --log-prefix "Probable_ddos:udp-flood "
iptables -A UDP-SCAN -j LOG --log-prefix "Probable ddos:udp-flood "
iptables -A UDP-SCAN -j DROP

iptables -A UDP-LIMIT -m limit --limit 10000/sec --limit-burst 10000 -j RETURN
iptables -A UDP-LIMIT -j DROP


