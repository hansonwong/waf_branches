#!/bin/bash

curdir=$(dirname `pwd`)
BD_WAF_PATH="/usr/local/bdwaf"
export LUAJIT_LIB=/usr/local/lib
export LUAJIT_INC=/usr/local/include/luajit-2.0

cp -fv $curdir/lua-5.1.4/src/liblua.* /usr/lib64/

./configure --prefix=/usr/local/bdwaf \
            --with-cust-ld-opt="-lhiredis -ldl -llua" \
            --add-module=/root/new/modsecurity/nginx/modsecurity \
            --add-module=/root/new/substi \
            --with-http_ssl_module \
            --conf-path=$BD_WAF_PATH/conf_proxy/nginx.conf  \
                --pid-path=$BD_WAF_PATH/logs_proxy/nginx.pid  \
    --http-log-path=$BD_WAF_PATH/logs_proxy/access.log  \
    --error-log-path=$BD_WAF_PATH/logs_proxy/error.log  \
    --lock-path=$BD_WAF_PATH/logs_proxy/nginx.lock  \
    --with-http_geoip_module \
    --with-openssl=/usr/local/ssl
