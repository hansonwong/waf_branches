#!/bin/sh

killall bdwaf
sleep 1
killall -9 bdwaf
/usr/local/bluedon/bdwaf/sbin/bdwaf
