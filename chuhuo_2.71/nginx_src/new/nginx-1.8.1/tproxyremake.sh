#!/bin/bash

curdir=$(dirname `pwd`)
BD_WAF_PATH="/usr/local/bdwaf"

./configure --prefix=/usr/local/bdwaf \
            --with-ld-opt="-L$curdir/lua-5.1.4/src/liblua.a" \
            --with-cust-ld-opt="-lhiredis" \
            --add-module=/root/new/modsecurity/nginx/modsecurity \
            --add-module=/root/new/substi \
            --with-http_ssl_module \
            --conf-path=$BD_WAF_PATH/conf_tproxy/nginx.conf  \
                --pid-path=$BD_WAF_PATH/logs_tproxy/nginx.pid  \
    --http-log-path=$BD_WAF_PATH/logs_tproxy/access.log  \
    --error-log-path=$BD_WAF_PATH/logs_tproxy/error.log  \
    --lock-path=$BD_WAF_PATH/logs_tproxy/nginx.lock  \
    --with-openssl=/usr/local/ssl 
            
