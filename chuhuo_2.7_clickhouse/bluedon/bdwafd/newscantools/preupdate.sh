#! /bin/sh
#
# Provides:          preupdate.sh
# Description:       Use this shell script to prepare updating 
#                   
# Author: Claus Wei <zhongwei@yxlink.com>
#
# error code: 1 - 30

errmsg() {
	/bin/echo "$*" >>/var/waf/update.log 2>&1

	if [ -e "/var/waf/ver" ]; then
	    verstr=`cat /var/waf/ver`
	    /var/waf/addsyslog -m "固件升级失败，版本号： $verstr"
	else
	    /var/waf/addsyslog -m "固件升级失败，版本号未知"
	fi
}

msg() {

	/bin/echo "$*" >>/var/waf/update.log 2>&1

	if [ -e "/var/waf/ver" ]; then
	    verstr=`cat /var/waf/ver`
	    /var/waf/addsyslog -m "固件升级成功，版本号： $verstr"
	else
	    /var/waf/addsyslog -m "固件升级成功，版本号未知"
	fi
}


##############              Validate the input arguments                ################

if [ $# -lt 1 ]; then
	echo "Usage: `basename $0` -f FILENAME-VERSION.dat"  >&2; 
	/var/waf/addsyslog -m "固件升级失败，错误代码1"
	exit 1

else
	inputfile=${1}
	echo "input file name: $inputfile"

	if [ ! -e $inputfile ]; then
		echo "Update file $inputfile doesn't exist. Aborting..."
		/var/waf/addsyslog -m "固件升级失败，错误代码2"
		exit 2
	fi

	# check file extension
	ext=${inputfile##*.}
	case $ext in
		dat|Dat|DAT)
		echo "Update file extension is valid"
		decodedfile=${inputfile%.dat}.tar.gz		
		echo "decoded file name: $decodedfile"
		decodeddir=${inputfile%.dat}
		echo "untar dir name: $decodeddir"
		;;

		*)
		echo "Update file extension is not valid. Aborting..."
		/var/waf/addsyslog -m "固件升级失败，错误代码3"

		/bin/rm $inputfile

		exit 3
		;;
	esac
fi


##############           use wafpack to decode the dat file          ################

if [ -x /var/waf/wafpack ]; then
	FAILURE=0
	/var/waf/wafpack -d -i $inputfile -o $decodedfile
	FAILURE=$?
	if [ $FAILURE -ne 0 ]; then
	    echo "Error decoding $inputfile, error when decoding. Aborting..."
	    /var/waf/addsyslog -m "固件升级失败，错误代码4"	
	    /bin/rm $inputfile
	    exit 4 
	fi

	if [ ! -e $decodedfile ]; then
		/var/waf/addsyslog -m "固件升级失败，错误代码5"	
		echo "No $decodedfile exists. Aborting..."
		/bin/rm $inputfile
		exit 5
	fi
else
	/var/waf/addsyslog -m "固件升级失败，错误代码6"	
	echo "No wafpack exists. Aborting..."
	/bin/rm $inputfile
	exit 6
fi

##############          untar the decoded file                       ################
echo "untar the package including xxxupdate.sh and xxx.tar.gz"


if [ -d $decodeddir ]; then
	/bin/rm -rf $decodeddir/*
else
	mkdir $decodeddir
fi

echo "tar xfvz $decodedfile -C $decodeddir"

FAILURE=0
/bin/tar xfvz $decodedfile -C $decodeddir
FAILURE=$?
if [ $FAILURE -ne 0 ]; then
    echo "Error untar $decodedfile, error when untaring. Aborting..."
    /var/waf/addsyslog -m "固件升级失败，错误代码7"	

    /bin/rm $inputfile
    /bin/rm $decodedfile
	
    exit 7
fi


##############          find the update shell in the update.dat          ################
FAILURE=0
updatetar=`find $decodeddir |grep tar.gz`
FAILURE=$?
if [ $FAILURE -ne 0 ]; then
	echo "Error, no update tar. Aborting..."
	/var/waf/addsyslog -m "固件升级失败，错误代码8"	

        /bin/rm $inputfile
        /bin/rm $decodedfile

	exit 8
else
	if [ ! -e $updatetar ]; then
	    echo "Error, failed to find update tar $updatetar. Aborting..."
	    /var/waf/addsyslog -m "固件升级失败，错误代码9"	

   	    /bin/rm $inputfile
	    /bin/rm $decodedfile
	    /bin/rm -rf $decodeddir

	    exit 9
	fi
fi

FAILURE=0
updatesh=`find $decodeddir |grep update.sh`
FAILURE=$?
if [ $FAILURE -ne 0 ]; then
	echo "Error, no update shell. Aborting..."
	/var/waf/addsyslog -m "固件升级失败，错误代码10"	

   	/bin/rm $inputfile
	/bin/rm $decodedfile
	/bin/rm -rf $decodeddir

	exit 10
else
	if [ ! -e "$updatesh" ]; then
	    echo "Error, failed to find update shell $updatesh. Aborting..."
	    /var/waf/addsyslog -m "固件升级失败，错误代码11"	

   	    /bin/rm $inputfile
	    /bin/rm $decodedfile
	    /bin/rm -rf $decodeddir

	    exit 11
	fi
fi


##############         call xxupdate.sh to do actual updating        ################
echo "$updatesh $updatetar"

/bin/chmod +x $updatesh


/var/waf/addsyslog -m "开始固件升级，请稍等"

#/var/waf/addsyslog -m "停止正在进行的扫描任务，请在升级完成后手工启动"

FAILURE=0
eval "$updatesh $updatetar"
FAILURE=$?
if [ $FAILURE -ne 0 ]; then
    echo "Error when run $updatesh. Aborting..."

    # clean up the files if error
    /bin/rm $inputfile
    /bin/rm $decodedfile
    /bin/rm -rf $decodeddir

    /usr/bin/logger -t preupdate  "failed to execute during: $updatesh $updatetar"
    exit $FAILURE
fi


##############         Log this successful update        ################
if [ -e "/var/waf/ver" ]; then
    verstr=`cat /var/waf/ver`
    /var/waf/addsyslog -m "固件升级成功，版本号： $verstr"
else
    /var/waf/addsyslog -m "固件升级成功，版本号未知"
fi


##############         run the add-on shell          ################

#run the add-on shell
if [ -e /var/waf/run.sh ]; then 
	echo "run /var/waf/run.sh"  

	FAILURE=0
	/var/waf/run.sh
	FAILURE=$?
	if [ $FAILURE -ne 0 ]; then

	    echo "Error when run /var/waf/run.sh. Aborting..."

	    /bin/rm $inputfile
	    /bin/rm $decodedfile
	    /bin/rm -rf $decodeddir

	    exit $FAILURE
	fi
fi   

##############         clean up                       ################

echo "/bin/rm $inputfile"
/bin/rm $inputfile

echo "/bin/rm $decodedfile"
/bin/rm $decodedfile

echo "/bin/rm -rf $decodeddir"
/bin/rm -rf $decodeddir


/bin/rm -rf /var/waf/patch/*   > /dev/null 2>&1



