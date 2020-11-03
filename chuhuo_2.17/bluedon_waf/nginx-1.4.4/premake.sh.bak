#!/bin/bash

curdir=$(dirname `pwd`)

BD_DPDK_WARPER="/home/ng_platform/bd_dpdk_warper"

./configure --prefix=/usr/local/bluedon/bdwaf \
    --with-pcre=$curdir/thirddep/pcre \
    --add-module=$curdir/ModSecurity/nginx/modsecurity  \
    --with-debug  \
    --with-cc-opt="-I $BD_DPDK_WARPER/include \
        -I $BD_DPDK_WARPER/include2 " \
    --with-dpdk="-L$BD_DPDK_WARPER/lib2 -ldpdk_bd \
        -L$BD_DPDK_WARPER/lib -ldpdk  -ldl  -lrt -L/usr/local/lib -lhiredis"

#-ggdb3会让gdb支持解析宏
#用--with-ld-opt的话，nginx会默认检查第三方库是否可编译