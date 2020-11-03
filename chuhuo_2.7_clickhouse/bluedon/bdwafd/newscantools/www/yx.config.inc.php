<?php

/*
WAF配置文件
*/

// [CH] 以下变量请根据空间商提供的账号参数修改,如有疑问,请联系服务器提供商

        $dbhost = '127.0.0.1';            // 数据库服务器
        $dbuser = 'root';                  // 数据库用户名
        $dbpw = 'd2!d%9)@d';                       // 数据库密码
        $dbname = 'waf_hw';               // 数据库名
	$pconnect = 0;                    // 数据库持久连接 0=关闭, 1=打开

// [CH] 小心修改以下变量, 否则可能导致系统无法正常使用


	$host = '127.0.0.1';              // WEBSERVER
        $servicecode = 'NVS0BD0D3201';    // 唯一服务代码
        $swver = '2.0';	                  // 固件版本
        $build = '2.0.03.5363';           // build
        $rulever = '1.0.0.2247';            // 规则版本
        $hwver = '2.0';                   // 硬件版本
        $model = 'BD-SCANNER-5000';              // 硬件型号	
        $enhance = '1';                   // 基本增强功能
        $feature_set = '00101000,10000000,00000000,00000000';        // 增强功能配置项集合
	$database = 'mysql';              // 数据库类型，请勿修改
	$dbcharset = 'utf8';              // MySQL 字符集, 可选 'gbk', 'big5', 'utf8', 'latin1'
	$charset = 'utf-8';               // 页面默认字符集, 可选 'gbk', 'big5', 'utf-8'
        $max_thread_global = '10';
        $max_task_global = '10';
        $max_task_ip_global = '65535';
        $ip_range_global = '*.*.*.*';
        $max_port_thread_global = '10';
        $max_host_thread_global = '20';
        $max_web_thread_global = '10';
        $max_weak_thread_global = '20';
        $warranty_duration = '2015-03-02/2018-03-01';
	$memory_limit = '1024M';
?>
