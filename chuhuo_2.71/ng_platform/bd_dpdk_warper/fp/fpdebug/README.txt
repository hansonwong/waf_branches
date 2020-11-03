0.功能：
fpdebug模块主要是用于辅助调试。方便调试时查看/改变某些变量的值。

1.编译
在当前目录下执行make ，也可以先make clean再make

2.启动程序：
切换到程序所在的目录，执行以下命令启动fpdebug程序：
./fp-debug 

3.退出程序：
键入exit或者quit

4.帮助信息：
通过输入help，可查看目前已经添加的调试命令，以及命令的使用方法。

5.具体的命令使用
				
5.1 dump_client		
作用：打印指定的client的信息。
用法：先输入dump_client，程序会输出每一个client的name和pid。然后通过"dump_client name"或者"dump_client pid"来打印对应client的详细信息。

5.2 dump_clients
作用：打印所有的client
用法：dump_clients（不带任何选项）

5.3 dump_clients_byhook
作用：dump system by hook
用法：dump_clients_byhook（不带任何选项）

5.4 dump_filter
作用：打印出所有的filter
用法：dump_filter

5.5 dump_portinfo
作用：打印所有网口的信息
用法：dump_portinfo

5.6 dump_portmode
作用：打印当前可用的所有网口模式
用法：dump_portmode

5.7 set_portmode
作用：显示/设置网口模式
用法：set_port_mode不带选项，显示所有网口的信息；”set_portmode [<portid> <mode> <value>]“设置portid（数字）对应的网口的mode（数字）和value（数字）。具体的mode值和对应的名字可以通过命令”set_port_mode“查看，或者参考”doc/bd-dpdk-warper_user-guide.txt“。

5.8 loginfoshow
作用：打印fpdebug调试模块的信息，包括oglevel,logtype,logmode,ratelimit
用法：loginfoshow

5.9 loglevel
作用：显示或者设置调试信息的level（0-7级），0最重要，7级最不重要，默认是4
用法：loglevel不带参数用于显示当前的level；”loglevel val“，其中val是0-7之间的数字，用于把loglevel设置为val

5.10 logmode
作用：显示或者设置log信息输出的位置：console（控制台）、syslog、file（文件）。默认值是console
用法：logmode不带参数，显示当前的log mode；”logmode [console|syslog|file]“设置log mode为console（控制台）、syslog、file（文件）三者中的其中一种。

5.11 logtype
作用：用于显示/设置那些模块的log日志是打开的。默认值是所有模块都打开。
用法：logtype不带参数，显示当前那些模块式打开的、哪些是关闭的。”logtype [<type|all> <on|off>]“，设置那些模块的log日志是打开的.

5.12 logratelimit
作用：用于显示/设置同一个语句的打印速率，避免同一语句在短时间内出现大量的重复的打印。log日志的ratelimit表示同一个语句必须相隔ratelimit毫秒以上才可以打印。默认ratelimit为100毫秒。
用法：logratelimit不带参数，显示当前的速率。”logratelimit [value]“把打印速率设置成对应的值。
