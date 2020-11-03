#!/bin/bash
#
# Copyright (C) Bluedon, 2016
# Author: Linfan Hu (hlf@chinabluedon.cn)
# Date: 2016/11/21
#

# Save pakages root directory
ROOT_DIR=$(pwd)
PHP_DIR=$ROOT_DIR/waf_php
PYTHON_DIR=$ROOT_DIR/waf_python
DB_DIR=$ROOT_DIR/waf_mysql

# In new version some apps run as system service
ENABLE_SERVICE=/usr/local/bluedon/scripts/enable_services.sh
RC_LOCAL=/etc/rc.d/rc.local
CRONTAB=/etc/crontab

# Working status file path
STATUS=$ROOT_DIR/../update_status
PHP_READ_STATE=/tmp/updateSysStatus.json

USR_SEL_PHP=
USR_SEL_PYTHON=
USR_SEL_DATABASE=

# Signal handler: do cleanup
trap "echo \"abort\" > $STATUS; exit 1" INT QUIT TERM STOP TSTP KILL

# Check if update is in progress
VAR=`ps -ef | grep "$0" | grep -Ev "grep|$$" | wc -l`
if [ $VAR -gt 0 ]; then
    echo "update_in_progress" > $STATUS
    exit 1
fi

# Determine which pakages to update
for dir in `ls $ROOT_DIR -F | grep "/$"`
do
	echo "$dir"
    if [ "$dir" == "waf_php/" ]; then
        USR_SEL_PHP=1
    elif [ "$dir" == "waf_python/" ]; then
        USR_SEL_PYTHON=2
    elif [ "$dir" == "waf_mysql/" ]; then
        USR_SEL_DATABASE=3
    fi
done
echo $USR_SEL_PHP
echo $USR_SEL_PYTHON
echo $USR_SEL_DATABASE

echo "{\"state\": \"1\"}"
echo "{\"state\": \"1\"}" > $PHP_READ_STATE

# Check packages dependency
#dependency_check
#if [ $? -ne 0 ]; then
#    exit 1
#fi
echo "{\"state\": \"2\"}"
echo "{\"state\": \"2\"}" > $PHP_READ_STATE

# Update UI
sh update_firewall_product.sh status=$STATUS php=$PHP_DIR python=$PYTHON_DIR db=$DB_DIR << _EOT
$USR_SEL_PHP
$USR_SEL_PYTHON
$USR_SEL_DATABASE
9
_EOT

echo "{\"state\": \"3\"}"
echo "{\"state\": \"3\"}" > $PHP_READ_STATE

sh php_migrate.sh

if [ $? -ne 0 ]; then
    echo "incorrect_version_number" > $STATUS
    exit 1
fi

echo "{\"state\": \"4\"}"
echo "{\"state\": \"4\"}" > $PHP_READ_STATE

echo "success" > $STATUS
echo "Succeed updating system"

