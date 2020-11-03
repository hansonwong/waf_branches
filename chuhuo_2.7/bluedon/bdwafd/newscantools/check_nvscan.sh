#! /bin/bash
size=`ls -l /opt/nvscan/var/nvscan/ext.db | awk '{print $5}'`
echo $size
if [ $size -ge 32 ];then
	echo "nvscand is illege, need to fix"
        /usr/bin/chattr -i /opt/nvscan/var/nvscan/ext.db
	cp /var/waf/ext.db /opt/nvscan/var/nvscan/ext.db
	/usr/bin/chattr +i /opt/nvscan/var/nvscan/ext.db
	echo "nvscan fixed"
fi
