#!/bin/sh

# System Config Collector and encryptor

BDWAFDIR=/usr/local/bluedon/bdwaf
BDWAFDDIR=/usr/local/bluedon/bdwafd
TMPDIR=/usr/local/bluedon/bdwafd/tmp
WWWDIR=/usr/local/bluedon/www/downloads

mkdir -p $TMPDIR
mkdir -p $WWWDIR

cd $TMPDIR
mysqldump -uroot -pbluedon waf t_nicset > sysconfig.sql
openssl enc -aes-256-cbc -in sysconfig.tar.gz -out sysconfig.data -pass pass:bdwaf
rm sysconfig.sql
mv sysconfig.data $WWWDIR

exit 0