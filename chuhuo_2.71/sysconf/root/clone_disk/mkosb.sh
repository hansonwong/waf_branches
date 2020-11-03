
echo "make system"

dmsetup remove_all


echo "============ Format sdb1 ==============="
mkfs.ext3 /dev/sdb1
echo "============ Format sdb2 ==============="
mkfs.ext3 /dev/sdb2
echo "============ Format sdb3 ==============="
mkfs.ext3 /dev/sdb3

mount /dev/sdb2 /mnt

cd /mnt
mkdir boot
mkdir var
mkdir mnt
mkdir proc
mkdir sys
mkdir dev
mkdir home

mount /dev/sdb1 /mnt/boot
mount /dev/sdb3 /mnt/var

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
grub2-install --recheck /dev/sdb  --root-directory=/mnt

#cp /root/clone_disk/fstab /mnt/etc/ -f
#cp /root/clone_disk/fstab /mnt/boot/grub2 -f
#cp /root/clone_disk/grub.cfg /mnt/boot/grub2 -f

chmod -R 777 /mnt/tmp

sleep 5

cd /
umount /mnt/boot
umount /mnt/var
umount /mnt

#echo "============ finish ==============="
echo "拷盘成功"
