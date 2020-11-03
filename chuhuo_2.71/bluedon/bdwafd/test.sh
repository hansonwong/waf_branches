#!/bin/bash
dir="/usr/local/bluedon/bdwafd"
ppid=""
named="bdwaf.license"

clean ()
{
cd $dir
./setup.py install 2>&-
./gencert.py 2>&-
./gencert.py option=4 2>&-
}

outgen ()
{
cd $dir
tmppid=pid$RANDOM
./gencert.py > $tmppid 2>&-
cat $tmppid | sed -n '$p'
}

mkgen ()
{
cd $dir
./gencert.py option=1 file=$named free=1 serial=outgen expire="2030-12-30 00:00:00" name= addr= email= tel=
}

ingen ()
{
cd $dir
./gencert.py option=2
}

cleanpid ()
{
  echo "" > $tmppid
  #echo "" > $ppid
}

if [ "$#" -ne 1 ]
then
  echo "EG: $0 (install|reload)"
  exit 1
else
if [ "$1" ! = "install" -o "$1" ! = "reload" ]
then
  echo "EG: $0 (install|reload)"
  exit 1
fi
if [ "$1" = "install" ]
then
  clean
  export outgen
  outgen
  mkgen
  ingen
  cleanpid
else
if [ "$1" = "reload" ]
then
  cleanpid
  export outgen
  outgen
  mkgen
  ingen
    fi
  fi
fi
