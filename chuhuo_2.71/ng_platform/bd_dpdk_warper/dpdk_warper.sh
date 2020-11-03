#!/bin/sh
export RTE_SDK=/home/ng_platform/dpdk-1.8.0
export PWD=/home/ng_platform/bd_dpdk_warper
sdkdir=$RTE_SDK
serverdir=$RTE_SDK/examples/multi_process/wh_works
linuxapp=$RTE_SDK/x86_64-native-linuxapp-gcc
warper=$PWD
dir=$(basename `pwd`)
if [ -z  $sdkdir ] ;then
	echo "please set envrioment firstly:RTE_SDK"
	exit 0;
fi

#if [ $dir != "bd_dpdk_warper" ];then
	#echo "you must cd bd_dpdk_warper then run shell $0"
	#exit 0
#fi

if [ $# -gt 1 ];then
	echo "Usage: $0 or $0 clean"
	exit 0
fi
if [ $# -eq 1 ];then
	if [ $1 != "clean" ];then
		echo "error: $0 or $0 clean"
		exit 0;
	fi
fi

	rm -fr $warper/include/*
	rm -fr $warper/lib/*
	cd $warper/lib2 && make clean
	cd $warper/clients && make clean 
	rm -fr $warper/server/mp_server
	rm -fr $serverdir/lib
	rm -fr $serverdir/*.c
	rm -fr $serverdir/include $serverdir/build 
#       rm -fr $serverdir/ndpi
	rm -fr $serverdir/wh_works
	cd  $RTE_SDK/examples/multi_process
	rm -fr client_server_mp/mp_server/client_server_mp
	rm -fr client_server_mp/mp_client/client_server_mp
	rm -fr simple_mp/simple_mp
	rm -fr symmetric_mp/symmetric_mp
#   	rm -fr /lib/libndpi.so*
#	cd $warper/lib2/ndpi && make clean
	cd $warper/fp/fpdebug && make clean


if [ $# -eq 1 ];then
	rm -fr $linuxapp
	echo "Clean all..."
        exit 0
fi

if [ ! -d  $linuxapp ] ;then
        echo "please compile DPDK-sdk firstly"
        exit 0;
fi


cd $warper/include
rm -fr *
cp -rs $linuxapp/include/* ./


cd $warper/lib
rm -fr *
cp -r $linuxapp/lib/* ./
ls | xargs -i ar x {}
rm -fr *.a
ar cru libdpdk.a *.o
rm -fr *.o

#cd $warper/lib2/ndpi
#make
#if [ $? -ne 0 ];then
#	echo "compile libndpi.so  error,check ..."
#	exit 0;
#fi

cd $warper/lib2
make clean && make 
if [ $? -ne 0 ];then
        echo "compile warper lib2  error,check ..."
        exit 0;
fi

cd $warper/clients
make clean && make
if [ $? -ne 0 ];then
        echo "compile clients error,check ..."
        exit 0;
fi


cd $warper/server
rm -fr mp_server
cp -f server.c $serverdir/
ln -s $warper/lib2  $serverdir/lib
ln -s $warper/include2  $serverdir/include
#ln -s $warper/include2/ndpi  $serverdir/ndpi
make -C  $sdkdir/examples/multi_process/
if [ $? -ne 0 ];then
	echo "compile server error,check ..."
	exit 0;
fi
cp -f $serverdir/wh_works/x86_64-native-linuxapp-gcc/mp_server  ./

cd $warper/fp/fpdebug
make clean && make 
if [ $? -ne 0 ];then
        echo "compile warper fp/fpdebug  error,check ..."
        exit 0;
fi

cd $warper
echo "Success,Congratulations..."


echo $warper
