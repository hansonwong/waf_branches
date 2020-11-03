#!/bin/sh

echo "------------------------------------"
echo "To fdisk /dev/$1, confirm:[y/n]"
read choice
if [ "$choice" != "y" -a "$choice" != "Y" ];then
   exit 1
fi

if [ -n "$1" -a -b "/dev/$1" ]; then
fdisk /dev/$1 <<_EOT
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
4

+8G
t
4
82
n
p
3


a
1
w
_EOT
	sleep 10
else
	echo "child disk error: $1"
    exit 1
fi
