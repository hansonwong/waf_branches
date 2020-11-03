
child_dev=$1
if [ -z "$child_dev" -o ! -b "/dev/${child_dev}1" -o ! -b "/dev/${child_dev}2" -o ! -b "/dev/${child_dev}3" ]; then
    echo "Error: invalid dev $child_dev"
	exit 1
fi

echo "------------------------------"
echo "Copy system to /dev/${child_dev}, confirm:[y/n]"
#read choice
choice="y"
if [ "$choice" != "y" -a "$choice" != "Y" ];then
   exit 1
fi
echo "make system"

dmsetup remove_all

echo "============ Format ${child_dev}1 ==============="
mkfs.ext4 /dev/${child_dev}1
echo "============ Format ${child_dev}2 ==============="
mkfs.ext4 /dev/${child_dev}2
echo "============ Format ${child_dev}3 ==============="
mkfs.ext4 /dev/${child_dev}3
echo "============ Format ${child_dev}4 ==============="
mkswap /dev/${child_dev}4

mount /dev/${child_dev}2 /mnt

cd /mnt
mkdir boot
mkdir var
mkdir mnt
mkdir proc
mkdir sys
mkdir dev
mkdir home

mount /dev/${child_dev}1 /mnt/boot
mount /dev/${child_dev}3 /mnt/var

echo "============ copy /[a-c]* ==============="
cp -r -p /[a-c]* /mnt

echo "============ copy /[e-i] ==============="
cp -r -p /[e-i]* /mnt

echo "============ copy /Data ==============="
cp -r -p /Data /mnt

echo "============ copy /lib ==============="
cp -r -p /lib /mnt

echo "============ copy /lib64 ==============="
cp -r -p /lib64 /mnt

echo "============ copy /media ==============="
cp -r -p /media /mnt

echo "============ copy /opt ==============="
cp -r -p /opt /mnt

echo "============ copy /root ==============="
cp -r -p /root /mnt

echo "============ copy /run ==============="
cp -r -p /run /mnt

echo "============ copy /sbin ==============="
cp -r -p /sbin /mnt

echo "============ copy /srv ==============="
cp -r -p /srv /mnt

echo "============ copy /tmp ==============="
cp -r -p /tmp /mnt

echo "============ copy /[uv]* ==============="
cp -r -p /[uv]* /mnt



echo "============ grub install ==============="
grub2-install --recheck /dev/${child_dev}  --root-directory=/mnt

cp /root/clone_disk/conf/fstab /mnt/etc/ -f
cp /root/clone_disk/conf/fstab /mnt/boot/grub2 -f
cp /root/clone_disk/conf/grub.cfg /mnt/boot/grub2 -f

chmod -R 777 /mnt/tmp

sleep 5

cd /
umount /mnt/boot
umount /mnt/var
umount /mnt

echo "============ finish ==============="
