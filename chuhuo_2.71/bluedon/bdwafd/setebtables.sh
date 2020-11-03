#!/bin/bash

if test "x$1" = "x" ; then
    exit 1
fi

if test "$1" = "stop" ; then
    ebtables -t broute -F
fi

if test "$1" = "start" ; then
    ebtables -t broute -F
    ebtables -t broute -A BROUTING -p IPv4 -j redirect --redirect-target DROP
fi