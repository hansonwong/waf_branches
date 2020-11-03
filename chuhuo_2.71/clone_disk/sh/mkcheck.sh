#!/bin/bash
# 2017/06/13 15:19:36 Tue

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LANGUAGE=en_US.UTF-8


mother_dev=$1
child_dev=$2
MOTHER_SN=$3

if [ -z "$child_dev" -o -z "$mother_dev" -o -z "$MOTHER_SN" ]; then
	echo "Please input something."
	exit 1
fi

if [ "$mother_dev" != "sda" ]; then
	echo -e "\033[32m Warnning: mother device is $mother_dev, confirm:[y/n] \033[0m"
	read choice
	if [ "$choice" != "y" -a "$choice" != "Y" ];then
		exit 1
	fi
fi

if [ "$child_dev" != "sdb" ]; then
	echo -e "\033[32m Warnning: child device is $child_dev, confirm:[y/n] \033[0m"
	read choice
	if [ "$choice" != "y" -a "$choice" != "Y" ];then
		exit 1
	fi
fi

get_disk_info()
{
	local disk_dev="$1"
	disk_model=`hdparm -i /dev/$disk_dev | grep '^ Model' |awk -F',' '{print $1}'`
	disk_sn=`hdparm -i /dev/$disk_dev | grep '^ Model' |awk -F',' '{print $3}'|awk -F'=' '{print $2}'`
}

# 获取母盘磁盘信息
get_disk_info $mother_dev
mother_model=$disk_model
mother_sn=$disk_sn

# 获取需要装系统磁盘信息
get_disk_info $child_dev
child_model=$disk_model
child_sn=$disk_sn


if [ -z "$mother_sn" -o -z "$child_sn" ]; then
	echo "Error: No device $mother_sn -o $child_sn"
	exit 1
fi
echo -e "MOTHER_SN:\033[32m $MOTHER_SN \033[0m"
echo -e "mother: /dev/$mother_dev \033[32m $mother_sn \033[0m, $mother_model\nchild: /dev/$child_dev $child_sn, $child_model, Confirm: y/n"

read choice
if [ "$choice" != "y" -a "$choice" != "Y" ];then
	exit 1
fi

if [ "$MOTHER_SN" != "$mother_sn" ]; then
	echo "Error: 母盘应该是 /dev/$mother_dev, $mother_sn - $MOTHER_SN"
	exit 1
fi

echo "/root/clone_disk/sh/mksdb.sh $child_dev"
echo "/root/clone_disk/sh/mkosb.sh $child_dev"

/root/clone_disk/sh/mksdb.sh $child_dev
/root/clone_disk/sh/mkosb.sh $child_dev

