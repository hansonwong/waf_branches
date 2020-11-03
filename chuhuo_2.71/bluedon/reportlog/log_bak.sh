#!/bin/sh

BAK="/var/log_bak/"

if [ ! -d $BAK ]; then
    mkdir $BAK
fi

FILES=`find /var/log/log_tables_backup/ -name '*.sql'`
for i in $FILES
do
    echo ${i#./}
    cp $i $BAK${i#./} > /dev/null 2>&1
done
var=`date "+%Y%m%d"`
tar -czf $BAK$var.tar.gz * 
rm -f $BAK*.sql
python /usr/local/bluedon/log_backup_lib.py
