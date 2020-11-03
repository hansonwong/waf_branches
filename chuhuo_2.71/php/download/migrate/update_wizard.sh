#!/bin/bash
#
# Copyright (C) 2016 Bluedon. All rights reserved.
# Author: Linfan Hu (hlf@chinabluedon.cn)
# Date: 2016/11/23
#

WORK_DIR=$(pwd)
STATUS=$WORK_DIR/update_status

PASSWORD=

# Signal handler: do cleanup
trap "do_cleanup; echo \"abort\" > $STATUS; exit 1" INT QUIT TERM STOP TSTP KILL

# Parse command line and redirect source packages if needed
for i in $@
do
    VAR=`echo $i | awk -F"=" '{print $1}'`
    if [ "$VAR" == "passwd" ]; then
        PASSWORD=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "packdir" ]; then
        WORK_DIR=`echo $i | awk -F"=" '{print $2}'`
        STATUS=$WORK_DIR/update_status
    fi
done

# Check if update is in progress
VAR=`ps -ef | grep "$0" | grep -Ev "grep|$$" | wc -l`
if [ $VAR -gt 2 ]; then
    echo "update_in_progress" > $STATUS
    exit 1
fi

# Do cleanup
function do_cleanup()
{
    cd $WORK_DIR
    rm -rf waf_update
    rm -rf waf_update.tar.gz
}

cd $WORK_DIR
rm -f $STATUS

# Check if tar ball exists
if [ ! -f "waf_update.tar.gz.enc" ]; then
    echo "no_update_package" > $STATUS
    exit 1
fi

# Check password
if [ -z "$PASSWORD" ]; then
    echo -e "Please input password:\c "
    read -s PASSWORD
fi

# line feeds
echo ""
echo "Update is under flying, please wait..."

# Verify md5 for this tar ball
MD5=`openssl dgst -md5 waf_update.tar.gz.enc | awk '{print $2}'`
MD5_ORIG=`cat waf_update.md5`
if [ "$MD5" != "$MD5_ORIG" ]; then
    echo "md5_check_fail" > $STATUS
    exit 1
fi

# Decrypt tar ball
openssl aes-128-cbc -d -salt -k $PASSWORD -in waf_update.tar.gz.enc -out waf_update.tar.gz
if [ $? -ne 0 ]; then
    echo "unable_to_decrypt_package" > $STATUS
    do_cleanup
    exit 1
fi

# Extract tar ball
rm -rf waf_update
tar -xzf waf_update.tar.gz
if [ $? -ne 0 ]; then
    echo "cannot_extract_update_tar_ball" > $STATUS
    do_cleanup
    exit 1
fi

# start time
echo $(date '+%Y-%m-%d %H:%M:%S') > /var/log/update_system.log

# Process update
cd waf_update
sh update_system.sh >> /var/log/update_system.log 2>&1
if [ $? -ne 0 ]; then
    echo "fail"
    do_cleanup
    exit 1
fi

# end time
echo $(date '+%Y-%m-%d %H:%M:%S') >> /var/log/update_system.log

do_cleanup

echo "success"
exit 0
