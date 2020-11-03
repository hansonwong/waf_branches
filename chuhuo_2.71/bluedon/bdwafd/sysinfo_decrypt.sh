#!/bin/sh

# System Infomation Collector and decryptor

if test "x$1" = "x" || test x$2 = x ; then
    echo "Usgae: $0 infile outfile"
    exit 1
fi

if [ ! -f $1 ]; then
    echo "infile is not a regular file"
    exit 1
fi

openssl enc -d -aes-256-cbc -in $1 -out $2 -pass pass:bdwaf

exit 0