#!/bin/bash

curdir=`pwd`
./configure --disable-shared --enable-standalone-module --disable-mlogc --enable-lua-cache --with-lua=$curdir/../lua-5.1.4/src
