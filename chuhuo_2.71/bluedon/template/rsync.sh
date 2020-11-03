#!/bin/bash 
#/usr/sbin/iptables -I FWINPUT -p tcp --dport 873 -j ACCEPT
host={{ terminalIP }} 
src=/home/rsync/send/     
des=web 
user=webuser 
/usr/local/inotify/bin/inotifywait -mrq --timefmt '%d/%m/%y %H:%M' --format '%T %w%f%e' -e modify,delete,create,attrib $src | while read files 
do 
/usr/bin/rsync -vzrtopg --delete --progress --password-file=/usr/local/rsync/server.passwd $src $user@$host::$des > /dev/null &
echo "${files} was rsynced" >>/var/log/rsync.log 2>&1 
done
