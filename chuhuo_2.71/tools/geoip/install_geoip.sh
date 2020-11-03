# !/bin/bash

tar zxf GeoIP-1.4.8.tar.gz
cd GeoIP-1.4.8
./configure; make && make install

cd ..
tar zxf Geo-IP-1.40.tar.gz
cd Geo-IP-1.40
perl Makefile.PL
make && make install

cd ..
rm -rf GeoIP-1.4.8 Geo-IP-1.40
