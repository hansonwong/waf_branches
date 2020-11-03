#!/bin/bash
# ./docker_network test1 172.16.3.123 2222

docker_name="$1"
out_ip="$2"
out_port="$3"
pid=$(docker inspect --format '{{ .State.Pid }}' ${docker_name})
mkdir -p /var/run/netns
ln -s /proc/$pid/ns/net /var/run/netns/$pid
inner_ip=$(ip netns exec $pid ifconfig eth0|grep inet|head -1|sed 's/\:/ /'|awk '{print $2}')

if [[ $4 == 'del' ]]; then
    iptables -D FORWARD  -j ACCEPT
    iptables -t nat -D PREROUTING -d ${out_ip} -p tcp --dport ${out_port} -j DNAT --to-destination ${inner_ip}:444
else
    iptables -I FORWARD  -j ACCEPT
    iptables -t nat -A PREROUTING -d ${out_ip} -p tcp --dport ${out_port} -j DNAT --to-destination ${inner_ip}:444
fi

