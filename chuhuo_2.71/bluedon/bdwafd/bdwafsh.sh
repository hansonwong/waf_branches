#!/bin/bash

#管道文件
#PIPEFILE="/tmp/test"
PIPEFILE=/tmp/bdwaf.fifo

cmdlist='setIp ipcheck resetPwd route traceroute resetSys restart halt listcmd help'

function help()
{
    echo "setIp             配置eth0网口信息"
    echo "ipcheck           检查ip配置信息"
#   echo "ipmodify          修改ip配置信息"
    echo "resetPwd          修改conadmin密码"
    echo "ping              标准linux 命令"
    echo "route             标准linux 命令"
    echo "arp               查看apr信息"
    echo "traceroute        标准linux 命令"
    echo "resetSys          复位操作（密码恢复出厂设置）"
    echo "restart           重启系统"
    echo "halt              标准linux 命令"
    echo "listcmd           显示所有命令和参数"
    echo "help xxx          显示xxx命令的用法"
}

#用法：get_cmd_option cmd_line
#对输入的一行中提取参数
function get_cmd_option()
{
	str=$*
	if [ $# == 1 ]; then
		echo ""       #一行中只有一个字符串。只有命令无参数
	else
	echo ${str#* }  #去掉第一个空格以及之前的字符
	fi
}

function setIp()
{
  if [ $# -gt 1 ] || [ x$1 = x"--help" ]  ;then
  	echo "Usage:      setIp [destination] "
  	echo "exmaple 1:  setIp  ;缺省IP 192.168.0.1 "
  	echo "exmaple 2:  setIp 172.16.8.88   "
  	return 
  fi
  
  if [ $# -lt 1 ];then
     IPVAL=192.168.0.1   #缺省值192.168.0.1
  else IPVAL=$1
  fi
  
  #ifconfig eth0 $IPVAL netmask 255.255.255.0
  echo "setIp eth0 whith ip $IPVAL"
  sudo ifconfig eth0 $IPVAL netmask 255.255.255.0
}

function ipcheck() 
{
	if [ x$1 == x"--help" ];then
  	echo "Usage:      ipcheck " 
  	return
  fi
    ifconfig
}

#未使用
function ipmodify()
{
    echo "ipmodify "
}

function resetPwd()
{
    #passwd $*
    if [ $# -gt 1 ] || [ x$1 == x"--help" ];then
        echo "Usage: resetPwd username"
        return
    fi
    username=$1
    python /usr/local/bluedon/bdwafd/changeUserPad.py -username $username -passwd
    if [ $? -eq 0 ];then
        echo "Can not search this user, please check your parameter!"
    else
        echo "New password: "
        read password1
        echo "\nRetype new password: "
        read password2
        if [ $password1 != $password2 ];then
            echo "\nSorry, passwords do not match.\n"
            return
        else
            python /usr/local/bluedon/bdwafd/changeUserPad.py -username $username -passwd $password2
            if [ $? -eq 1 ];then
                echo "Password reset successfully!"
            else
                echo "Password reset faile!"
            fi
        fi
    fi
}

function resetSys()
{
   if [ $# -gt 1 ] || [ x$1 = x"--help" ]  ;then
  	  echo "Usage: resetSys"
      echo "Restore the system to factory Settings."
  	  return
   fi
  
   echo "Restore the system[Y/N]: "
   read SURE
   if [ "Y" != $SURE ] ; then
       exit 0
   fi    

   echo "reset operation"
   echo "CMD_SYSTOOL|reset" >> $PIPEFILE
}

function waf_ping()
{  
  #限制显示三次ping的结果
  if [ x$1 == x"--help" ] || [ $# -lt 1 ];then
  	echo "Usage:      ping destination"
  	echo "exmaple:    ping 192.168.0.2"
  	return
  else
  	ping -c 3 $* 
  fi
}

function waf_route()
{
    route $*
}

function waf_arp()
{
    arp -a
}

function waf_reboot()
{
    reboot $*
}

function waf_halt()
{
    halt $*
}

function listcmd()
{	
    if [ $# -gt 1 ] || [ x$1 = x"--help" ]  ;then
  	   echo "Usage:      listcmd "
  	   return
  	fi
  	
	echo "setIp  [destination] ;     配置eth0网口信息; 参数destination:待配置的IP"
    echo "ipcheck                       检查ip配置信息"
    echo "resetPwd                      修改conadmin密码"
    echo "ping                          标准linux 命令"
    echo "route                         标准linux 命令"
    echo "arp                           查看apr信息"
    echo "traceroutte                   标准linux 命令"
    echo "resetSys                      复位操作（密码恢复出厂设置）"
    echo "restart                       重启系统"
    echo "halt                          标准linux 命令"
    echo "listcmd                       显示所有命令和参数"
    echo "help xxx                      显示一条命令的用法;参数xxx: 以上的一条命令"
    return
}

function walf_traceroute()
{
   traceroute $*

}

function waf_help()
{	
	for cmd in $cmdlist
	do
		if [ x$* == x$cmd ];then
			#找到对应命令
			$* --help
			return
		fi
	done
	if [ x$* == x"ping" ];then
	   waf_ping --help
	   return
	fi   
	#不正确的格式，重新help
	help
}

while true
do
echo -n "BDWAF>> "
    read cmdline
    cmd=${cmdline%% *}
    optparm=`get_cmd_option $cmdline`
    
    if [  -z $cmd ]; then
        help
    elif [ $cmd = "setIp" ];then
        setIp $optparm		
    elif [ $cmd = "ipcheck" ];then
        ipcheck $optparm
    elif [ $cmd = "ipmodify" ];then
        ipmodify $optparm
    elif [ $cmd = "resetPwd" ];then
        resetPwd $optparm
    elif [ $cmd = "ping" ];then        
    		waf_ping $optparm                     
    elif [ $cmd = "route" ];then
        waf_route $optparm
    elif [ $cmd = "arp" ];then
        waf_arp $optparm
    elif [ $cmd = "traceroute" ];then
        walf_traceroute $optparm 		
    elif [ $cmd = "resetSys" ];then
        resetSys $optparm
    elif [ $cmd = "restart" ];then
        waf_reboot $optparm         
    elif [ $cmd = "halt" ];then
        halt $optparm 
    elif [ $cmd = "listcmd" ];then
        listcmd &optparm
    elif [ $cmd = "help" ];then        
    		waf_help $optparm                                    
    else
        help
    fi
done
