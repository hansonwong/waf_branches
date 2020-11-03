#!/bin/bash
#
# Copyright (C) 2016 Bluedon. All rights reserved.
# Author: Linfan Hu (hlf@chinabluedon.cn)
# Date: 2016/11/23
#

SVN_IPADDR=172.16.3.234
VERSION_FILE=version.txt

# revision format: "-r 1234"
PHP_REVISION=
PYTHON_REVISION=
PY_CFG_REVISION=
DB_REVISION=
DPDK_REVISION=
DPDK_WARPER_REVISION=
POLICY_REVISION=
WAF_REVISION=
IPS_REVISION=
USR_AUTHEN_REVISION=
HA_REVISION=
AVSCAN_REVISION=
ANTI_DETECT_REVISION=
ANTI_SCAN_REVISION=
DAQ_REVISION=
IPSECVPN_REVISION=
SSLVPN_REVISION=

if [ -f "$VERSION_FILE" ]; then
    while read line
    do
        VAR=`echo $line | awk '{print $1}'`
        if [ "$VAR" == "PHP" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                PHP_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "PYTHON" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                PYTHON_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "PYTHON_CFG" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                PY_CFG_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "DATABASE" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                DB_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "DPDK" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                DPDK_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "DPDK_WARPER" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                DPDK_WARPER_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "POLICY_EVOLVE" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                POLICY_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "WAF" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                WAF_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "IPS" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                IPS_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "USR_AUTHEN" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                USR_AUTHEN_REVISION="-r $VER"
            fi
        elif [ "$VAR" == "IPSECVPN" ]; then
            VER=`echo $line | awk '{print $2}'`
            if [ -n "$VER" ]; then
                IPSECVPN_REVISION="-r $VER"
            fi
        fi
    done < $VERSION_FILE
fi

[ ! -d "bdfw_update" ] && mkdir bdfw_update
cd bdfw_update

cp -f ../package/libraries.tar.gz ./
cp -f ../package/python-modules.tar.gz ./
tar xzf libraries.tar.gz
tar xzf python-modules.tar.g
rm -f python-modules.tar.g
rm -f libraries.tar.gz

rm -rf firewall
rm -rf firewall_python_etc
rm -rf firewall_python_1.1_product
rm -rf MySQL_Database
rm -rf dpdk-1.8.0
rm -rf bd_dpdk_warper
rm -rf policyevolve
rm -rf nginx-1.4.4
rm -rf user_authentication
rm -rf ipsec-guomi
rm -rf ngfw-sysconfig
rm -rf antidetect-rec
rm -rf av_install_package
rm -rf suricata
rm -rf daq-2.0.6
rm -rf snort-2.9.8.0

iptables -I INPUT -j ACCEPT

svn export svn://$SVN_IPADDR/ng_platform/fw_scripts/ngfw-sysconfig

svn export $PHP_REVISION svn://$SVN_IPADDR/PHP/secfw/truck_new/firewall0804/firewall
svn export $PY_CFG_REVISION svn://$SVN_IPADDR/python-controller/firewall_python_etc
svn export $PYTHON_REVISION svn://$SVN_IPADDR/python-controller/python-controller/branches/firewall_python_1.1_product
svn export $DB_REVISION svn://$SVN_IPADDR/python-controller/MySQL_Database

rm -f MySQL_Database/Mysql_3306_audit_v1_1.sql
rm -f MySQL_Database/Mysql_3306_beijingtest_20160906.sql
rm -f MySQL_Database/Mysql_3306_DAC.sql
rm -f MySQL_Database/Mysql_3306_international.sql
rm -f MySQL_Database/Mysql_3306_VirusWall.sql
rm -f MySQL_Database/Mysql_3306_vpn.sql
rm -f MySQL_Database/Mysql_3307_audit_v1_1.sql
rm -f MySQL_Database/Mysql_3307_beijingtest_20160906.sql
rm -f MySQL_Database/Mysql_3307_DAC.sql
rm -f MySQL_Database/Mysql_3307_VirusWall.sql
rm -f MySQL_Database/Mysql_3307_vpn.sql

svn export $DPDK_REVISION svn://$SVN_IPADDR/ng_platform/trunk/dpdk-1.8.0
svn export $DPDK_WARPER_REVISION svn://$SVN_IPADDR/ng_platform/trunk/bd_dpdk_warper
svn export $POLICY_REVISION svn://$SVN_IPADDR/ng_platform/trunk/policyevolve
svn export $WAF_REVISION svn://$SVN_IPADDR/ng_platform/FW_WAF/nginx-1.4.4
svn export $USR_AUTHEN_REVISION svn://$SVN_IPADDR/ng_platform/user_authentication
svn export $IPSECVPN_REVISION svn://$SVN_IPADDR/ng_platform/vpn/ipsecvpn/ipsec-guomi

svn export $AVSCAN_REVISION svn://$SVN_IPADDR/ng-audit/branch/IPS/Av/av_install_package-nodeff_v8.tar.gz
tar xzf av_install_package-nodeff_v8.tar.gz
rm -f av_install_package-nodeff_v8.tar.gz

svn export $DAQ_REVISION svn://$SVN_IPADDR/Intelligence-security/AntiScan/daq-2.0.6
svn export $ANTI_SCAN_REVISION svn://$SVN_IPADDR/Intelligence-security/AntiScan/snort-2.9.8.0
svn export $ANTI_DETECT_REVISION svn://$SVN_IPADDR/Intelligence-security/AntiDetect/antidetect-rec
svn export $IPS_REVISION svn://$SVN_IPADDR/ng-audit/branch/IPS/Suricata-3.1/suricata-3.1
mv suricata-3.1 suricata

mkdir -p waf-config
cd waf-config/
rm -rf bdwaf_restart.sh
rm -rf bdwaf
svn export svn://$SVN_IPADDR/ng_platform/FW_WAF/bdwaf_restart.sh
svn export svn://$SVN_IPADDR/ng_platform/FW_WAF/bdwaf
chmod a+x bdwaf_restart.sh
cd -

mkdir -p ips-config
cd ips-config/
rm -rf http-audit-config
rm -rf rules
rm -rf yaml
svn export svn://$SVN_IPADDR/ng-audit/branch/IPS/Suricata-3.1/audit/http-audit-config
svn export svn://$SVN_IPADDR/ng-audit/branch/IPS/Suricata-3.1/audit/rules
svn export svn://$SVN_IPADDR/ng-audit/branch/IPS/Suricata-3.1/yaml
cd -

mkdir -p HA
cd HA
rm -rf check.sh
rm -rf primary-backup.sh
svn export svn://$SVN_IPADDR/ng_platform/HA/check.sh
svn export svn://$SVN_IPADDR/ng_platform/HA/primary-backup.sh
chmod a+x *.sh
cd -

# remove unneeded files
rm -f ch_passwd.go
rm -f ch_passwd
rm -f config_firewall.sh
rm -f update_firewall_authen.sh
rm -rf ipsec-guomi/ipsec-tools-0.8.2/src/racoon/missing/crypto_card/doc

DATE=`date '+%Y-%m-%d'`
echo $DATE > $VERSION_FILE

svn log $PHP_REVISION svn://$SVN_IPADDR/PHP/secfw/truck_new/firewall0804/firewall | awk 'NR==2{print "PHP           " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $PY_CFG_REVISION svn://$SVN_IPADDR/python-controller/firewall_python_etc | awk 'NR==2{print "PYTHON_CFG    " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $PYTHON_REVISION svn://$SVN_IPADDR/python-controller/python-controller/branches/firewall_python_1.1_product | awk 'NR==2{print "PYTHON        " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $DB_REVISION svn://$SVN_IPADDR/python-controller/MySQL_Database | awk 'NR==2{print "DATABASE      " $1}' | sed 's/r//' >> $VERSION_FILE

svn log $DPDK_REVISION svn://$SVN_IPADDR/ng_platform/trunk/dpdk-1.8.0 | awk 'NR==2{print "DPDK          " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $DPDK_WARPER_REVISION svn://$SVN_IPADDR/ng_platform/trunk/bd_dpdk_warper | awk 'NR==2{print "DPDK_WARPER   " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $POLICY_REVISION svn://$SVN_IPADDR/ng_platform/trunk/policyevolve | awk 'NR==2{print "POLICY_EVOLVE " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $WAF_REVISION svn://$SVN_IPADDR/ng_platform/FW_WAF/nginx-1.4.4 | awk 'NR==2{print "WAF           " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $USR_AUTHEN_REVISION svn://$SVN_IPADDR/ng_platform/user_authentication | awk 'NR==2{print "USR_AUTHEN    " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $HA_REVISION svn://$SVN_IPADDR/ng_platform/HA | awk 'NR==2{print "HA            " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $IPSECVPN_REVISION svn://$SVN_IPADDR/ng_platform/vpn/ipsecvpn/ipsec-guomi | awk 'NR==2{print "IPSEC_VPN     " $1}' | sed 's/r//' >> $VERSION_FILE

svn log $IPS_REVISION svn://$SVN_IPADDR/ng-audit/branch/IPS/Suricata-3.1/suricata-3.1 | awk 'NR==2{print "IPS           " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $AVSCAN_REVISION svn://$SVN_IPADDR/ng-audit/branch/IPS/Av/av_install_package | awk 'NR==2{print "AVSCAN        " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $ANTI_SCAN_REVISION svn://$SVN_IPADDR/Intelligence-security/AntiScan/snort-2.9.8.0 | awk 'NR==2{print "ANTI_SCAN     " $1}' | sed 's/r//' >> $VERSION_FILE
svn log $ANTI_DETECT_REVISION svn://$SVN_IPADDR/Intelligence-security/AntiDetect/antidetect-rec | awk 'NR==2{print "ANTI_DETECT   " $1}' | sed 's/r//' >> $VERSION_FILE

iptables -D INPUT -j ACCEPT

