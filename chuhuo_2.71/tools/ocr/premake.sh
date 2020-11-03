#!/bin/bash


# yum install -y tesseract-langpack-chi_sim tesseract

tar -zxf leptonica-1.74.tar.gz
cd leptonica-1.74
./configure && make install

cd ..

tar -zxf tesseract-3.04.00.tar.gz
cd tesseract-3.04.00
./configure && make install
cd ..


mkdir -p /usr/local/share/tessdata
echo "export TESSDATA_PREFIX=/usr/local/share" >> /etc/profile

tar -zxf tessdata.tar.gz -C /usr/local/share

# if [ ! -f /usr/local/share/tessdata ]; then
# 	ln -sv /usr/local/share/tessdata/lang/tessdata /usr/local/share/tessdata
# 	ln -svf /usr/local/lib/libtesseract.so.3 /usr/lib
# fi


# tar -zcf waf2.7-ocr.tar.gz /usr/local/bin/tesseract /usr/local/lib/libtesseract.* /usr/local/lib/liblept.* /usr/local/bdwaf/conf_proxy/activated_rules/tesseract_ocr.lua /usr/local/bdwaf/conf_proxy/activated_rules/modsecurity_ocr_scanners.data /usr/local/bdwaf/sbin/bdwaf.proxy /usr/local/share/tessdata -P
