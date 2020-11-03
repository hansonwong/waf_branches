#!/bin/bash

curdir=$(dirname `pwd`)

BD_DPDK_WARPER="/home/ng_platform/bd_dpdk_warper"
BD_WAF_PATH="/usr/local/bdwaf"

./configure --prefix=$BD_WAF_PATH \
    --with-pcre=/home/tools/pcre-8.32 \
    --add-module=$curdir/ModSecurity/nginx/modsecurity  \
    --with-debug  \
    --with-cc-opt="-I $BD_DPDK_WARPER/include \
        -I $BD_DPDK_WARPER/include2 " \
      --pid-path=$BD_WAF_PATH/logs_bridge/nginx.pid  \
    --http-log-path=$BD_WAF_PATH/logs_bridge/access.log  \
    --error-log-path=$BD_WAF_PATH/logs_bridge/error.log  \
    --lock-path=$BD_WAF_PATH/logs_bridge/nginx.lock  \
    --with-dpdk="-L$BD_DPDK_WARPER/lib2 -ldpdk_bd \
    -L$BD_DPDK_WARPER/lib -ldpdk  -ldl  -lrt -lnet -lbdpi -lext -lcrypto -lz -lzlog -L/usr/local/lib -lhiredis"

#-ggdb3会让gdb支持解析宏
#用--with-ld-opt的话，nginx会默认检查第三方库是否可编译