#!/bin/sh
#
#

fdisk /dev/sdb <<_EOT
d
1
d
2
d
3
d
4
d
n
p
1

+500M
n
p
2

+40G
n
p
3


a
1
w
_EOT
sleep 10


