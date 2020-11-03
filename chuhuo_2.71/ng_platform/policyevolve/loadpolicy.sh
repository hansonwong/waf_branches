#!/bin/sh
TABLE=filter
function remove_chain()
{
    echo -n removing chain...
    {
#       sudo /sbin/iptables -t ${TABLE} -D PREROUTING -j NF_QUEUE_CHAIN
#       sudo /sbin/iptables -t ${TABLE} -D OUTPUT -j NF_QUEUE_CHAIN
#       sudo /sbin/iptables -t ${TABLE} -D PREROUTING -j NF_QUEUE_CHAIN
#       sudo /sbin/iptables -t ${TABLE} -D OUTPUT -j NF_QUEUE_CHAIN
	sudo /sbin/iptables -t ${TABLE} -D FORWARD -j NF_QUEUE_CHAIN
        sudo /sbin/iptables -t ${TABLE} -F NF_QUEUE_CHAIN
        sudo /sbin/iptables -t ${TABLE} -X NF_QUEUE_CHAIN
    }
    &>/dev/null
    echo done
}

function create_chain()
{
    echo -n creating chain...
    sudo /sbin/iptables -t ${TABLE} -N NF_QUEUE_CHAIN
#   sudo /sbin/iptables -t ${TABLE} -A NF_QUEUE_CHAIN -j MARK --set-mark 10
#   sudo /sbin/iptables -t ${TABLE} -A NF_QUEUE_CHAIN -m mark --mark 10 -j NFQUEUE --queue-balance 12:14
    sudo /sbin/iptables -t ${TABLE} -A NF_QUEUE_CHAIN -j NFQUEUE --queue-balance 12:14
    sudo /sbin/iptables -t ${TABLE} -I FORWARD -j NF_QUEUE_CHAIN
#    sudo /sbin/iptables -t ${TABLE} -I PREROUTING -j NF_QUEUE_CHAIN
#   sudo /sbin/iptables -t ${TABLE} -I OUTPUT -p tcp ! --sport 22 -j NF_QUEUE_CHAIN
#   sudo /sbin/iptables -t ${TABLE} -I PREROUTING -p tcp ! --dport 22 -j NF_QUEUE_CHAIN
    echo done
}

function on_iqh(){
    remove_chain
    exit 1
}

trap on_iqh INT QUIT HUP
remove_chain
create_chain
./nftse -F ./tse.ini -Q 12-14 -L DEBUG
remove_chain
