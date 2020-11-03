#!/bin/sh

# try to create pipe file for communication between php and python

fifopath='/tmp/bdwaf.fifo'

if [ ! -p $fifopath ]; then
    rm $fifopath -f
    mkfifo $fifopath
    chmod 777 $fifopath
fi

exit 0