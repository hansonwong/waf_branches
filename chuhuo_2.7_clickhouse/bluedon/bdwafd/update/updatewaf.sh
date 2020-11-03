#!/bin/bash

#mv $2 /usr/local/bluedon/bdwafd/update/
cd /usr/local/bluedon/bdwafd/update/
#rm -rf patch*
#openssl enc -d -aes-256-cbc -in $1 -out $1.tar.gz -pass pass:bdwafsys
tar xf $1.tar
#chown -R root:root *
#cd $1
#chmod 777 patch.py
#python patch.py
#cd /usr/local/bluedon/bdwafd/update/
#rm -rf $1 $1.tar

exit 0
