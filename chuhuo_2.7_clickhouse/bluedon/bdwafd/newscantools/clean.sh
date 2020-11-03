#! /bin/sh
#
# Provides:          clean.sh
# Description:       run it on the TARGET machine to clean system and application logs
#                   
# Author: Claus Wei <zhongwei@yxlink.com>
#
# Usage:  
#   clean.sh 


/bin/rm -rf /var/log/apache2/*

/bin/rm -rf /var/log/*.gz  /var/log/*.log  /var/log/*.log.1  /var/log/*.log.2  /var/log/*.log.3

/bin/rm -rf /tmp/*

/bin/rm -rf /var/waf/*.log.1

/bin/rm -rf /var/www/fcgi-bin/*.log.1 /var/www/cgi-bin/*.log.1  /var/www/cgi-pub/*.log.1 
