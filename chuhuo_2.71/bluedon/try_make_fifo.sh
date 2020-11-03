#!/bin/sh

# try to create pipe file for communication between php and python

fifopath='/Data/apps/wwwroot/firewall/fifo/second_firewall.fifo'

if [ ! -d "/Data/apps/wwwroot/firewall/fifo" ]; then
    mkdir "/Data/apps/wwwroot/firewall/fifo"
    chmod 777 "/Data/apps/wwwroot/firewall/fifo"
fi

if [ ! -p $fifopath ]; then
    rm $fifopath -f
    mkfifo $fifopath
    chmod 777 $fifopath
fi

exit 0
