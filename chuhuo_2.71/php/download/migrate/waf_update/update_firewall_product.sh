#!/bin/bash
#
# Copyright (C) Bluedon, 2016
# Author: Linfan Hu (hlf@chinabluedon.cn)
# Date: 2016/11/17
#

# Check if update is in progress
VAR=`ps -ef | grep "$0" | grep -Ev "grep|$$" | wc -l`
if [ $VAR -gt 0 ]; then
    echo "Error: $0 in progress"
    exit 1
fi

# constant data definition
USR_SEL_PHP=1
USR_SEL_PYTHON=2
USR_SEL_DATABASE=3
USR_SEL_ALL=4
USR_SEL_EXIT=9

# packages svn path
SVN_IPADDR=
PHP_SVN_PATH=
PYTHON_SVN_PATH=
PY_CFG_SVN_PATH=
DB_SVN_PATH=

# packages default directories
# You can specify these through script parameters
PHP_DIR=waf_php
PYTHON_DIR=waf_python
#PY_CFG_DIR=firewall_python_etc
DB_DIR=waf_mysql
SH_DIR=waf_shell

NETWORK_INTERFACE=/etc/network_config/network_interface.cfg

# update status file
STATUS=/dev/null

# Signal handler: do cleanup
trap "do_clean; exit 1" INT QUIT TERM STOP TSTP KILL

# Parse command line and redirect source pakages if needed
for i in $@
do
    VAR=`echo $i | awk -F"=" '{print $1}'`	
    if [ "$VAR" == "php" ]; then
        PHP_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "python" ]; then
        PYTHON_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "db" ]; then
        DB_DIR=`echo $i | awk -F"=" '{print $2}'`
    fi
done
echo "PHP_DIR: $PHP_DIR"
echo "PYTHON_DIR: $PYTHON_DIR"
echo "DB_DIR: $DB_DIR"
echo "SH_DIR: $SH_DIR"

#########################################################

function svn_check()
{
    if [ -z "$SVN_IPADDR" ]; then
        echo "Error: Missing SVN server ip address"
        return 1
    fi

    # Check if svn server is reachable
    for ((i = 0; i < 4; i++))
    do
        VAR=`ping $SVN_IPADDR -c 1 | grep ttl`
        if [ -n "$VAR" ]; then
            break
        fi
    done
    if [ $i -ge 4 ]; then
        echo "Error: Cannot connect to svn server."
        return 1
    fi

    # Check if php svn path is valid
    VAR=`svn log $PHP_SVN_PATH | awk 'NR==2{print "PHP "$1}'`
    if [ -z "$VAR" ]; then
        echo "Error: php svn path unreachable. Check your svn server $SVN_IPADDR"
        return 1
    fi

    # Check if python svn path is valid
    VAR=`svn log $PYTHON_SVN_PATH | awk 'NR==2{print "Python "$1}'`
    if [ -z "$VAR" ]; then
        echo "Error: python svn path unreachable. Check your svn server $SVN_IPADDR"
        return 1
    fi

    # Check if python config svn path is valid
    VAR=`svn log $PY_CFG_SVN_PATH | awk 'NR==2{print "Python "$1}'`
    if [ -z "$VAR" ]; then
        echo "Error: python svn path unreachable. Check your svn server $SVN_IPADDR"
        return 1
    fi

    # Check if database svn path is valid
    VAR=`svn log $DB_SVN_PATH | awk 'NR==2{print "Database "$1}'`
    if [ -z "$VAR" ]; then
        echo "Error: database svn path unreachable. Check your svn server $SVN_IPADDR"
        return 1
    fi

    return 0
}

# arguement: user selection
function svn_revision()
{
    if [ -z "$SVN_IPADDR" ]; then
        return
    fi

    if [ $1 -eq $USR_SEL_PHP ]; then
        svn log $PHP_SVN_PATH | awk 'NR==2{print "PHP version "$1}'
    elif [ $1 -eq $USR_SEL_PYTHON ]; then
        svn log $PY_CFG_SVN_PATH | awk 'NR==2{print "Python config "$1}'
        svn log $PYTHON_SVN_PATH | awk 'NR==2{print "Python version "$1}'
    elif [ $1 -eq $USR_SEL_DATABASE ]; then
        svn log $DB_SVN_PATH | awk 'NR==2{print "Database version "$1}'
    elif [ $1 -eq $USR_SEL_ALL ]; then
        svn log $PHP_SVN_PATH | awk 'NR==2{print "PHP version "$1}'
        svn log $PY_CFG_SVN_PATH | awk 'NR==2{print "Python config "$1}'
        svn log $PYTHON_SVN_PATH | awk 'NR==2{print "Python version "$1}'
        svn log $DB_SVN_PATH | awk 'NR==2{print "Database version "$1}'
    fi
}

# arguement: user selection
function svn_export()
{
    if [ -z "$SVN_IPADDR" ]; then
        return
    fi

    if [ $1 -eq $USR_SEL_PHP ]; then
        rm -rf $PHP_DIR
        svn export $PHP_SVN_PATH
    elif [ $1 -eq $USR_SEL_PYTHON ]; then
        rm -rf $PYTHON_DIR
        rm -rf $PY_CFG_DIR
        svn export $PY_CFG_SVN_PATH
        svn export $PYTHON_SVN_PATH
    elif [ $1 -eq $USR_SEL_DATABASE ]; then
        rm -rf $DB_DIR
        svn export $DB_SVN_PATH
    elif [ $1 -eq $USR_SEL_ALL ]; then
        rm -rf $PHP_DIR
        rm -rf $PYTHON_DIR
        rm -rf $PY_CFG_DIR
        rm -rf $DB_DIR
        svn export $PHP_SVN_PATH
        svn export $PY_CFG_SVN_PATH
        svn export $PYTHON_SVN_PATH
        svn export $DB_SVN_PATH
    fi
}

function stop_backend_services()
{
    # kill processes which occupy fifo file
    VAR=`ps -ef | grep second_firewall | grep fifo | awk '{print $2}'`
    for pid in $VAR 
    do
        kill -9 $pid
    done

    #python /usr/local/bluedon/second_firewall_daemon.py -s stop
    #python /usr/local/bluedon/reportlog/mysql_log_daemon.py -s stop
    systemctl stop firewall-python-daemon
    systemctl stop mysql_log_daemon
}

function start_backend_services()
{
    #sh /usr/local/bluedon/restart.sh
    #python /usr/local/bluedon/second_firewall_daemon.py -s start > /var/log/daemon.log 2>&1 &
    #python /usr/local/bluedon/reportlog/mysql_log_daemon.py -s start > /var/log/mysql.log 2>&1 &
    systemctl start firewall-python-daemon
    systemctl start mysql_log_daemon
}

# PHP
function update_php()
{
    echo "Updating PHP..."

    if [ ! -d "$PHP_DIR" ]; then
        echo "Error: No PHP package found"
        return 1
    fi

	#rm -rfv /Data/apps/wwwroot/waf/www/migrate/*
    \cp -rfv $PHP_DIR/migrate/* /Data/apps/wwwroot/waf/www/migrate/
	rm -rfv /var/www/migrate/update_php/
    mkdir -p /var/www/migrate/update_php/
    #rm -rf /var/www/migrate/update/update_php/*
    #mkdir -p /var/www/migrate/bak/
    \cp -rfv $PHP_DIR/* /var/www/migrate/update_php/
    #chmod -R 777 /Data/apps/wwwroot/waf/www
    echo "update_php Done"

    return 0
}

# Python
function update_python()
{
    echo "Updating Python..."

    if [ ! -d "$PYTHON_DIR" ]; then
        echo "Error: No Python package found"
        return 1
    fi
	
	rm -rfv /var/www/migrate/update_python/
    mkdir -p /var/www/migrate/update_python/
    #rm -rf /var/www/migrate/update/update_python/*
    #mkdir -p /var/www/migrate/bak/
    \cp -rfv $PYTHON_DIR/* /var/www/migrate/update_python/
    chmod -R 777 /usr/local/bluedon

    echo "update_python Done"

    return 0
}

# Database
function update_database()
{
    # For updating database, mysql must be running.
    VAR=`ps -ef | grep mysql3306 | grep -v grep`
    if [ -z "$VAR" ]; then
        echo "Error: mysql is not running."
        return 1
    fi

    if [ ! -d "$DB_DIR" ]; then
        echo "Error: No Database package found"
        return 1
    fi

    # Database 3306
    if [ -f "$DB_DIR/Mysql_3306_product.sql" ]; then
        echo "Updating Database 3306..."
mysql -uroot -pbd_123456 <<EOT    
    set names utf8;
    set autocommit = 0;
    source $DB_DIR/Mysql_3306_product.sql;
    commit;
    set autocommit = 1;
EOT
        if [ $? -ne 0 ]; then
            echo "update 3306 fail"
            return 1
        fi
        echo "Done"
    fi

    return 0
}

# shell scripts
function update_shell()
{
    [ ! -d "$SH_DIR" ] && return 1

    echo "Updating shell scripts..."

    rm -rfv /var/www/migrate/update_shell
	mkdir -p /var/www/migrate/update_shell/    
    \cp -rfv $SH_DIR/* /var/www/migrate/update_shell/

    echo "Done"

    return 0
}

# arguement: user selection
function do_update()
{
    if [ $1 -eq $USR_SEL_PHP ]; then
        update_php
        if [ $? -ne 0 ]; then 
            echo "update_php_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_PYTHON ]; then
        update_python
        if [ $? -ne 0 ]; then
            echo "update_python_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_DATABASE ]; then
        update_database
        if [ $? -ne 0 ]; then
            echo "update_database_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_ALL ]; then
        update_php
        [ $? -ne 0 ] && return 1

        update_python
        [ $? -ne 0 ] && return 1

        update_database
        [ $? -ne 0 ] && return 1
    fi

    update_shell;

    return 0
}

function do_clean()
{
    if [ -n "$SVN_IPADDR" ]; then
        iptables -D INPUT -j ACCEPT

        rm -rf $PHP_DIR
        rm -rf $PYTHON_DIR
        rm -rf $PY_CFG_DIR
        rm -rf $DB_DIR
    fi
}

function show_help
{
    echo "============================== "
    echo "[$USR_SEL_PHP] Upadte PHP"
    echo "[$USR_SEL_PYTHON] Upadte Python"
    echo "[$USR_SEL_DATABASE] Upadte Database"
    echo "[$USR_SEL_ALL] Upadte all above"
    echo "[$USR_SEL_EXIT] Exit"
    echo -e "Select option:\c "

    read OPT

    # User input must be an integer
    if [[ $OPT =~ ^[0-9]{1,}$ ]]; then
        return $OPT
    fi

    return 0
}

############################################

if [ -n "$SVN_IPADDR" ]; then
    iptables -I INPUT -j ACCEPT
    svn_check
    if [ $? -eq 1 ]; then
        iptables -D INPUT -j ACCEPT
        exit 1
    fi
fi

# We must stop backend services before update
stop_backend_services;

# Main task starts from here
while :
do
    show_help
    USER_SEL=$?

    if [ $USER_SEL -eq 0 ]; then
        continue
    elif [ $USER_SEL -eq $USR_SEL_EXIT ]; then
        break
    fi

    if [ -n "$SVN_IPADDR" ]; then
        svn_export $USER_SEL
    fi
	
	echo "do_update $USER_SEL"
    do_update $USER_SEL
	
    if [ $? -ne 0 ]; then
        do_clean
        exit 1
    fi

    svn_revision $USER_SEL
done

start_backend_services;

do_clean
echo "Succeed updating WAF"
exit 0
