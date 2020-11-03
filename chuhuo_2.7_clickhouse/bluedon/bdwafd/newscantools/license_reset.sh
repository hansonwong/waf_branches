#!/bin/sh

# clear the license file


/bin/rm /etc/waf.lic

/bin/rm /etc/license.count


echo -n "In order to reset waf license completely, press any key to reboot"
read ANS_REBOOT

/sbin/reboot
