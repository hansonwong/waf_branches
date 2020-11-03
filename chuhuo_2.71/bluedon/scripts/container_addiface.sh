#!/bin/bash
# ./docker_network.sh dockername iface_name
# eg: ./docker_network.sh dockername iface_name

docker_name="$1"
iface="$2"
iface_id=${iface//[!0-9]/}
br_name="br-${iface}"
brctl addbr ${br_name}
ip link set ${br_name} up
pid=$(docker inspect --format '{{ .State.Pid }}' ${docker_name})
mkdir -p /var/run/netns
ln -s /proc/$pid/ns/net /var/run/netns/$pid
ip link add v-${pid}-${iface_id}a type veth peer name v-${pid}-${iface_id}b
brctl addif ${br_name} v-${pid}-${iface_id}a
ip link set v-${pid}-${iface_id}a up
ip link set v-${pid}-${iface_id}b netns $pid
ip netns exec $pid ip link set dev v-${pid}-${iface_id}b name ${iface}
ip netns exec $pid ip link set ${iface} up
