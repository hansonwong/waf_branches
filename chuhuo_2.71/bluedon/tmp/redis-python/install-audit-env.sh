#!/bin/bash

tar xzf pip-8.1.2.tar.gz
cd pip-8.1.2
python setup.py install

cd ..
pip install esmre-0.3.1.tar.gz
pip install ipaddr-2.1.11.tar.gz
pip install ipaddress-1.0.17-py2-none-any.whl
pip install meld3-1.0.2-py2.py3-none-any.whl
pip install maxminddb-1.2.1.tar.gz
pip install requests-2.11.1-py2.py3-none-any.whl
pip install elementtree-1.2.6-20050316.tar.gz
pip install redis-2.10.5-py2.py3-none-any.whl
