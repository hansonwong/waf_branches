#!/bin/sh  

case "$1" in  
send)  
echo "$3"|smbclient -I "$2" -M `nmblookup -A "$2"|sed -e '1d'  -e '3,/*/d'|cut -f2|cut -d' ' -f1`  ;;  *)  
echo "Usage:net send <IPaddr.> <message>"  
exit 1  
esac  
