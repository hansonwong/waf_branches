<?php

/*
WAF�����ļ�
*/

// [CH] ���±�������ݿռ����ṩ���˺Ų����޸�,��������,����ϵ�������ṩ��

        $dbhost = '127.0.0.1';            // ���ݿ������
        $dbuser = 'root';                  // ���ݿ��û���
        $dbpw = 'd2!d%9)@d';                       // ���ݿ�����
        $dbname = 'waf_hw';               // ���ݿ���
	$pconnect = 0;                    // ���ݿ�־����� 0=�ر�, 1=��

// [CH] С���޸����±���, ������ܵ���ϵͳ�޷�����ʹ��


	$host = '127.0.0.1';              // WEBSERVER
        $servicecode = 'NVS0BD0D3201';    // Ψһ�������
        $swver = '2.0';	                  // �̼��汾
        $build = '2.0.03.5363';           // build
        $rulever = '1.0.0.2247';            // ����汾
        $hwver = '2.0';                   // Ӳ���汾
        $model = 'BD-SCANNER-5000';              // Ӳ���ͺ�	
        $enhance = '1';                   // ������ǿ����
        $feature_set = '00101000,10000000,00000000,00000000';        // ��ǿ�����������
	$database = 'mysql';              // ���ݿ����ͣ������޸�
	$dbcharset = 'utf8';              // MySQL �ַ���, ��ѡ 'gbk', 'big5', 'utf8', 'latin1'
	$charset = 'utf-8';               // ҳ��Ĭ���ַ���, ��ѡ 'gbk', 'big5', 'utf-8'
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
