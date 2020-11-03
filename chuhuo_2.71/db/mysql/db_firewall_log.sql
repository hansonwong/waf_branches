-- MySQL dump 10.13  Distrib 5.6.30, for Linux (x86_64)
--
-- Host: localhost    Database: db_firewall_log
-- ------------------------------------------------------
-- Server version	5.6.30

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bm_smbssj`
--

DROP TABLE IF EXISTS `bm_smbssj`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bm_smbssj` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `event_id` varchar(10) DEFAULT NULL COMMENT '事件编号',
  `device_id` varchar(10) DEFAULT NULL COMMENT '设备编号',
  `event_class` varchar(4) DEFAULT NULL COMMENT '事件类型',
  `event_type` varchar(2) DEFAULT NULL COMMENT '具体事件子类',
  `event_time` varchar(24) DEFAULT NULL COMMENT '事件产生时间',
  `sip` varchar(18) DEFAULT NULL COMMENT '外部主机ip',
  `sport` varchar(8) DEFAULT NULL COMMENT '端口号',
  `dmac` varchar(18) DEFAULT NULL COMMENT '内部主机的mac',
  `dip` varchar(18) DEFAULT NULL COMMENT '内部主机ip',
  `dport` varchar(8) DEFAULT NULL COMMENT '端口号',
  `sender` varchar(64) DEFAULT NULL COMMENT '发送人id',
  `receiver` text COMMENT '接收人id或接收方网址',
  `title` varchar(128) DEFAULT NULL COMMENT '与event_type对应:event_type-title:电子邮件-邮件标题；即时通信软件-软件的官方名称;博客/论坛/网盘-接收方网址',
  `file_name` text COMMENT '表示文件名或敏感内容',
  `descr` varchar(128) DEFAULT NULL COMMENT '描述文件的属性或其他信息',
  `sen_msg` varchar(128) DEFAULT NULL COMMENT '为1011时有效，表示匹配的铭感词列表，用#分隔',
  `attach_path` varchar(256) DEFAULT NULL COMMENT '附件在服务器上的路径',
  `internal_file` varchar(256) DEFAULT NULL COMMENT '协议解析时产生的文件:邮件服务对应eml文件;',
  `internal_path` varchar(256) DEFAULT NULL COMMENT '内部文件的路径',
  `internet_access` varchar(256) DEFAULT NULL COMMENT '上网方式',
  `attach_code` varchar(512) DEFAULT NULL COMMENT '附件路径对应的索引号',
  `internal_file_code` varchar(512) DEFAULT NULL COMMENT '邮件文件对应的索引号',
  `match_flag` int(10) DEFAULT NULL COMMENT '涉密类型标识',
  `iState` varchar(10) DEFAULT NULL COMMENT '状态：1.已审核；null.未审核',
  `tablename` varchar(64) DEFAULT NULL COMMENT '记录对应的实际表名',
  PRIMARY KEY (`id`),
  KEY `dip` (`dip`),
  KEY `sip` (`sip`),
  KEY `squery` (`id`,`sip`,`dip`,`dport`,`sport`),
  KEY `id_time` (`event_time`,`id`),
  KEY `title_time` (`title`,`id`),
  KEY `type_id` (`event_type`,`id`),
  KEY `send_id` (`sender`,`id`),
  KEY `internet_id` (`internet_access`,`id`),
  KEY `state_id` (`iState`,`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_audit_traffic`
--

DROP TABLE IF EXISTS `m_tb_alert_audit_traffic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_audit_traffic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `iTime` int(20) NOT NULL COMMENT '''时间''',
  `sIP` varchar(128) NOT NULL COMMENT '''源IP''',
  `sAlertType` varchar(32) NOT NULL COMMENT '''阈值告警类型(日周月)''',
  `iFlowTraffic` int(20) NOT NULL COMMENT '''流量值''',
  `iDstPort` int(10) NOT NULL COMMENT '''目的端口''',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_dns_log`
--

DROP TABLE IF EXISTS `m_tb_alert_dns_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_dns_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDomain` varchar(255) NOT NULL COMMENT '''域名''',
  `sIPs` varchar(255) NOT NULL COMMENT '''IP''',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-DNS日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_email_log`
--

DROP TABLE IF EXISTS `m_tb_alert_email_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_email_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(150) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(150) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(32) NOT NULL COMMENT '用户名称',
  `sDept` varchar(32) NOT NULL COMMENT '部门',
  `iVlanId` int(16) NOT NULL COMMENT 'vlan_id',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sSender` varchar(128) NOT NULL COMMENT '发件人',
  `sSendTo` text NOT NULL COMMENT '收件人',
  `sSendBb` text NOT NULL COMMENT '密送',
  `sSendCc` text NOT NULL COMMENT '抄送',
  `sSubject` text NOT NULL COMMENT '标题',
  `sContentPath` varchar(512) NOT NULL COMMENT '正文内容文件路径',
  `sAttCount` int(10) NOT NULL COMMENT '附件数量',
  `sAttachFilename` text NOT NULL COMMENT '附件文件名，多个用分号隔开',
  `sAttachFilesize` varchar(1024) NOT NULL COMMENT '文件大小，多个用分号隔开',
  `sAttachFilenamePath` text NOT NULL COMMENT '附件存放文件路径，多个用分号隔开',
  `sAppName` varchar(64) NOT NULL COMMENT '协议类型 smtp、pop3、imap',
  `sMatchInfo` text NOT NULL COMMENT '匹配日志 json',
  `iOverseas` tinyint(1) NOT NULL,
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`),
  KEY `iTime_Dept_Name` (`iDate`,`sDept`,`sUser`) USING BTREE,
  KEY `iOverseas` (`iOverseas`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-邮件日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_ftp_log`
--

DROP TABLE IF EXISTS `m_tb_alert_ftp_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_ftp_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sAction` varchar(128) NOT NULL,
  `sPara` varchar(255) NOT NULL COMMENT '''文件名''',
  `sFtpUserName` varchar(255) DEFAULT NULL COMMENT '''Ftp登陆用户名''',
  `sFilename` varchar(255) NOT NULL COMMENT '''文件名''',
  `sFileSize` varchar(255) DEFAULT NULL COMMENT '''文件大小''',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-FTP日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_game`
--

DROP TABLE IF EXISTS `m_tb_alert_game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_game` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-游戏日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_http_bbs`
--

DROP TABLE IF EXISTS `m_tb_alert_http_bbs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_http_bbs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(128) NOT NULL COMMENT '用户名',
  `sPassword` varchar(128) NOT NULL COMMENT '密码',
  `sSubject` varchar(255) NOT NULL COMMENT '主题',
  `sContent` text NOT NULL COMMENT '内容',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-BBS论坛日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_http_blog`
--

DROP TABLE IF EXISTS `m_tb_alert_http_blog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_http_blog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(64) NOT NULL COMMENT '用户名',
  `sSubject` varchar(255) NOT NULL,
  `sContent` text NOT NULL COMMENT '''博客内容''',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Blog博客日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_http_netstore`
--

DROP TABLE IF EXISTS `m_tb_alert_http_netstore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_http_netstore` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(128) NOT NULL COMMENT '用户名',
  `sFilename` varchar(512) NOT NULL COMMENT '''文件名''',
  `sAttachFilename` text NOT NULL COMMENT '文件名',
  `sAttachFileSize` text COMMENT '''文件大小''',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-网盘日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_http_search`
--

DROP TABLE IF EXISTS `m_tb_alert_http_search`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_http_search` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sKeyword` varchar(64) NOT NULL COMMENT '关键字',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='上网行为审计-搜索日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_http_shopping`
--

DROP TABLE IF EXISTS `m_tb_alert_http_shopping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_http_shopping` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sTitle` varchar(64) NOT NULL COMMENT '网页标题',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-购物网站日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_http_url_log`
--

DROP TABLE IF EXISTS `m_tb_alert_http_url_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_http_url_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sURL` text COMMENT 'URL',
  `sTitle` varchar(512) NOT NULL COMMENT '''标题''',
  `sCategory` varchar(256) DEFAULT NULL COMMENT '''URL分类''',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-HTTP URL日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_http_video`
--

DROP TABLE IF EXISTS `m_tb_alert_http_video`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_http_video` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sTitle` varchar(64) NOT NULL COMMENT '网页标题',
  `sVideo_name` varchar(64) DEFAULT NULL COMMENT '视频名称',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-视频日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_http_webmail`
--

DROP TABLE IF EXISTS `m_tb_alert_http_webmail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_http_webmail` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` text NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sFrom` varchar(255) NOT NULL COMMENT '发件人',
  `sTo` varchar(255) NOT NULL COMMENT '收件人',
  `sChao` varchar(255) DEFAULT NULL COMMENT '抄送',
  `sMi` varchar(255) DEFAULT NULL COMMENT '密送',
  `sSubject` varchar(255) DEFAULT NULL COMMENT '邮件主题',
  `sContent` text COMMENT '邮件内容',
  `sAttachFilename` text NOT NULL COMMENT '''附件-文件名''',
  `sAttachFileSize` text COMMENT '''附件大小''',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-WebMail日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_http_weibo`
--

DROP TABLE IF EXISTS `m_tb_alert_http_weibo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_http_weibo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(64) NOT NULL COMMENT '用户名',
  `sContent` text NOT NULL COMMENT '内容',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-微博日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_netbios`
--

DROP TABLE IF EXISTS `m_tb_alert_netbios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_netbios` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sType` varchar(128) NOT NULL COMMENT '''类型(上传或下载)''',
  `sStorepath` varchar(255) NOT NULL COMMENT '''文件保存路径''',
  `sUsername` varchar(255) DEFAULT NULL COMMENT '''用户名''',
  `sFilename` varchar(255) NOT NULL COMMENT '''文件名''',
  `sOldFilename` varchar(255) DEFAULT NULL COMMENT '''类型为重命名时的原文件名''',
  `sFilzesize` varchar(255) DEFAULT NULL COMMENT '''文件大小''',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-FTP日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_nfs`
--

DROP TABLE IF EXISTS `m_tb_alert_nfs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_nfs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sType` varchar(128) NOT NULL COMMENT '''类型(上传或下载)''',
  `sStorepath` varchar(255) NOT NULL COMMENT '''文件保存路径''',
  `sFilename` varchar(255) NOT NULL COMMENT '''文件名''',
  `sOldFilename` varchar(255) DEFAULT NULL COMMENT '''类型为重命名时的原文件名''',
  `sFilesize` varchar(255) DEFAULT NULL COMMENT '''文件大小''',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-NFS日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_proxy`
--

DROP TABLE IF EXISTS `m_tb_alert_proxy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_proxy` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Proxy日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_qq`
--

DROP TABLE IF EXISTS `m_tb_alert_qq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_qq` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sSendID` bigint(32) NOT NULL COMMENT 'QQ发送ID',
  `sRecvID` bigint(32) NOT NULL COMMENT 'QQ接收ID',
  `sAction` varchar(256) NOT NULL COMMENT 'QQ动作',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-QQ日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_sql_log`
--

DROP TABLE IF EXISTS `m_tb_alert_sql_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_sql_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDatabaseType` varchar(128) NOT NULL COMMENT '数据库类型',
  `sDatabaseName` varchar(255) NOT NULL COMMENT '数据库名称',
  `sSQL` varchar(1024) NOT NULL COMMENT 'SQL语句',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-SQL日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_stock`
--

DROP TABLE IF EXISTS `m_tb_alert_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_stock` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-股票软件日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_telnet`
--

DROP TABLE IF EXISTS `m_tb_alert_telnet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_telnet` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUserName` varchar(128) NOT NULL COMMENT 'Telnet用户名',
  `sPassword` varchar(128) NOT NULL COMMENT 'Telnet密码',
  `sAction` varchar(256) NOT NULL COMMENT 'Telnet动作',
  `sFilename` varchar(256) NOT NULL COMMENT '文件名',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Telnet日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_trojan`
--

DROP TABLE IF EXISTS `m_tb_alert_trojan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_trojan` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Trojan日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_alert_urlfilter`
--

DROP TABLE IF EXISTS `m_tb_alert_urlfilter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_alert_urlfilter` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUrlType` varchar(255) DEFAULT NULL COMMENT 'URL分类',
  `sRuleName` varchar(255) NOT NULL COMMENT '规则名',
  `sRuleId` varchar(512) NOT NULL COMMENT '规则ID',
  `sRuleAction` varchar(512) NOT NULL COMMENT '规则动作',
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL DEFAULT '0' COMMENT '''告警状态''',
  `sAlertKeyword` varchar(255) DEFAULT NULL COMMENT '''命中关键字''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `iAlertFlag` int(1) NOT NULL DEFAULT '0' COMMENT '告警标记',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '警告' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-URL Filter日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_app_drop`
--

DROP TABLE IF EXISTS `m_tb_app_drop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_app_drop` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sAppName` varchar(255) NOT NULL,
  `sAction` varchar(64) NOT NULL,
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-阻断日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_appfilter`
--

DROP TABLE IF EXISTS `m_tb_appfilter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_appfilter` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sAppId` varchar(255) DEFAULT NULL COMMENT 'URL分类',
  `sRuleName` varchar(255) NOT NULL COMMENT '规则名',
  `sRuleId` varchar(512) NOT NULL COMMENT '规则ID',
  `sRuleAction` varchar(512) NOT NULL COMMENT '规则动作',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-URL Filter日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_audit_traffic_statistics`
--

DROP TABLE IF EXISTS `m_tb_audit_traffic_statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_audit_traffic_statistics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sIP` bigint(32) NOT NULL COMMENT '''IP''',
  `sProto` varchar(32) CHARACTER SET latin1 NOT NULL COMMENT '''协议''',
  `iAppMark` int(11) NOT NULL DEFAULT '0' COMMENT '''应用号''',
  `iDstPort` int(11) NOT NULL COMMENT '''目的端口''',
  `sUsername` varchar(255) NOT NULL COMMENT '''用户名''',
  `sGroupname` varchar(255) NOT NULL COMMENT '''用户组''',
  `iDown` int(20) NOT NULL COMMENT '''下行流量''',
  `iUp` int(20) NOT NULL COMMENT '''上行流量''',
  `iUpdateTime` int(20) NOT NULL COMMENT '''更新时间''',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`),
  KEY `indexUpdateTime` (`iUpdateTime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_dns_log`
--

DROP TABLE IF EXISTS `m_tb_dns_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_dns_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDomain` varchar(255) NOT NULL COMMENT '''域名''',
  `sIPs` varchar(255) NOT NULL COMMENT '''IP''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-DNS日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_dns_log_overseas`
--

DROP TABLE IF EXISTS `m_tb_dns_log_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_dns_log_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDomain` varchar(255) NOT NULL COMMENT '''域名''',
  `sIPs` varchar(255) NOT NULL COMMENT '''IP''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-DNS日志-海外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_email_log`
--

DROP TABLE IF EXISTS `m_tb_email_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_email_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(150) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(150) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(32) NOT NULL COMMENT '用户名称',
  `sDept` varchar(32) NOT NULL COMMENT '部门',
  `iVlanId` int(16) NOT NULL COMMENT 'vlan_id',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sSender` varchar(128) NOT NULL COMMENT '发件人',
  `sSendTo` text NOT NULL COMMENT '收件人',
  `sSendBb` text NOT NULL COMMENT '密送',
  `sSendCc` text NOT NULL COMMENT '抄送',
  `sSubject` text NOT NULL COMMENT '标题',
  `sContentPath` varchar(512) NOT NULL COMMENT '正文内容文件路径',
  `sAttCount` int(10) NOT NULL COMMENT '附件数量',
  `sAttachFilename` text NOT NULL COMMENT '附件文件名，多个用分号隔开',
  `sAttachFilesize` varchar(1024) NOT NULL COMMENT '文件大小，多个用分号隔开',
  `sAttachFilenamePath` text NOT NULL COMMENT '附件存放文件路径，多个用分号隔开',
  `sAppName` varchar(64) NOT NULL COMMENT '协议类型 smtp、pop3、imap',
  `sMatchInfo` text NOT NULL COMMENT '匹配日志 json',
  `iOverseas` tinyint(1) NOT NULL,
  `sAlertDetail` text COMMENT '''告警详情''',
  `sAlertStatus` varchar(32) NOT NULL COMMENT '''告警状态''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`),
  KEY `iTime_Dept_Name` (`iDate`,`sDept`,`sUser`) USING BTREE,
  KEY `iOverseas` (`iOverseas`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-邮件日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_email_log_overseas`
--

DROP TABLE IF EXISTS `m_tb_email_log_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_email_log_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(150) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(150) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(32) NOT NULL COMMENT '用户名称',
  `sDept` varchar(32) NOT NULL COMMENT '部门',
  `iVlanId` int(16) NOT NULL COMMENT 'vlan_id',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sSender` varchar(128) NOT NULL COMMENT '发件人',
  `sSendTo` text NOT NULL COMMENT '收件人',
  `sSendBb` text NOT NULL COMMENT '密送',
  `sSendCc` text NOT NULL COMMENT '抄送',
  `sSubject` text NOT NULL COMMENT '标题',
  `sContentPath` varchar(512) NOT NULL COMMENT '正文内容文件路径',
  `sAttCount` int(10) NOT NULL COMMENT '附件数量',
  `sAttachFilename` text NOT NULL COMMENT '附件文件名，多个用分号隔开',
  `sAttachFilesize` varchar(1024) NOT NULL COMMENT '文件大小，多个用分号隔开',
  `sAttachFilenamePath` text NOT NULL COMMENT '附件存放文件路径，多个用分号隔开',
  `sAppName` varchar(64) NOT NULL COMMENT '协议类型 smtp、pop3、imap',
  `sMatchInfo` text NOT NULL COMMENT '匹配日志 json',
  `iOverseas` tinyint(1) NOT NULL,
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`),
  KEY `iTime_Dept_Name` (`iDate`,`sDept`,`sUser`) USING BTREE,
  KEY `iOverseas` (`iOverseas`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-邮件日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_ftp_log`
--

DROP TABLE IF EXISTS `m_tb_ftp_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_ftp_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sAction` varchar(128) NOT NULL,
  `sPara` varchar(255) NOT NULL COMMENT '''文件名''',
  `sFtpUserName` varchar(255) DEFAULT NULL COMMENT '''Ftp登陆用户名''',
  `sFilename` varchar(255) NOT NULL COMMENT '''文件名''',
  `sFileSize` varchar(255) DEFAULT NULL COMMENT '''文件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-FTP日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_ftp_log_overseas`
--

DROP TABLE IF EXISTS `m_tb_ftp_log_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_ftp_log_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sAction` varchar(128) NOT NULL,
  `sPara` varchar(255) NOT NULL,
  `sFtpUserName` varchar(255) DEFAULT NULL COMMENT '''Ftp登陆用户名''',
  `sFilename` varchar(255) NOT NULL COMMENT '''文件名''',
  `sFileSize` varchar(255) DEFAULT NULL COMMENT '''文件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-FTP日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_game`
--

DROP TABLE IF EXISTS `m_tb_game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_game` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-游戏日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_game_overseas`
--

DROP TABLE IF EXISTS `m_tb_game_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_game_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-游戏日志-海外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_bbs`
--

DROP TABLE IF EXISTS `m_tb_http_bbs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_bbs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(128) NOT NULL COMMENT '用户名',
  `sPassword` varchar(128) NOT NULL COMMENT '密码',
  `sSubject` varchar(255) NOT NULL COMMENT '主题',
  `sContent` text NOT NULL COMMENT '内容',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-BBS论坛日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_bbs_overseas`
--

DROP TABLE IF EXISTS `m_tb_http_bbs_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_bbs_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(128) NOT NULL COMMENT '用户名',
  `sPassword` varchar(128) NOT NULL COMMENT '密码',
  `sSubject` varchar(255) NOT NULL COMMENT '主题',
  `sContent` text NOT NULL COMMENT '内容',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-BBS论坛日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_blog`
--

DROP TABLE IF EXISTS `m_tb_http_blog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_blog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(64) NOT NULL COMMENT '用户名',
  `sSubject` varchar(255) NOT NULL COMMENT '''博客主题''',
  `sContent` text COMMENT '''博客内容''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Blog博客日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_blog_overseas`
--

DROP TABLE IF EXISTS `m_tb_http_blog_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_blog_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(64) NOT NULL COMMENT '用户名',
  `sSubject` varchar(255) NOT NULL COMMENT '''博客主题''',
  `sContent` text COMMENT '''博客内容''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Blog博客日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_netstore`
--

DROP TABLE IF EXISTS `m_tb_http_netstore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_netstore` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(128) NOT NULL COMMENT '用户名',
  `sFilename` varchar(512) NOT NULL COMMENT '''文件名''',
  `sAttachFilename` text NOT NULL COMMENT '文件名与文件路径',
  `sAttachFileSize` text COMMENT '''文件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-网盘日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_netstore_overseas`
--

DROP TABLE IF EXISTS `m_tb_http_netstore_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_netstore_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(128) NOT NULL COMMENT '用户名',
  `sFilename` varchar(512) NOT NULL COMMENT '''文件名''',
  `sAttachFilename` text NOT NULL COMMENT '文件名',
  `sAttachFileSize` text COMMENT '''文件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-网盘日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_search`
--

DROP TABLE IF EXISTS `m_tb_http_search`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_search` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sKeyword` varchar(64) NOT NULL COMMENT '关键字',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-搜索日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_search_overseas`
--

DROP TABLE IF EXISTS `m_tb_http_search_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_search_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sKeyword` varchar(64) NOT NULL COMMENT '关键字',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-搜索日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_shopping`
--

DROP TABLE IF EXISTS `m_tb_http_shopping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_shopping` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sTitle` varchar(64) NOT NULL COMMENT '网页标题',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-购物网站日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_shopping_overseas`
--

DROP TABLE IF EXISTS `m_tb_http_shopping_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_shopping_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sTitle` varchar(64) NOT NULL COMMENT '网页标题',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-购物网站日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_url_log`
--

DROP TABLE IF EXISTS `m_tb_http_url_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_url_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sURL` text COMMENT 'URL',
  `sTitle` varchar(512) NOT NULL COMMENT '''标题''',
  `sCategory` varchar(256) DEFAULT NULL COMMENT '''URL分类''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-HTTP URL日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_url_log_overseas`
--

DROP TABLE IF EXISTS `m_tb_http_url_log_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_url_log_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sURL` text COMMENT 'URL',
  `sTitle` varchar(512) NOT NULL COMMENT '''标题''',
  `sCategory` varchar(256) DEFAULT NULL COMMENT '''URL分类''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-HTTP URL日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_video`
--

DROP TABLE IF EXISTS `m_tb_http_video`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_video` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sTitle` varchar(64) NOT NULL COMMENT '网页标题',
  `sVideo_name` varchar(64) DEFAULT NULL COMMENT '视频名称',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-视频日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_video_overseas`
--

DROP TABLE IF EXISTS `m_tb_http_video_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_video_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sTitle` varchar(64) NOT NULL COMMENT '网页标题',
  `sVideo_name` varchar(64) DEFAULT NULL COMMENT '视频名称',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-视频日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_webmail`
--

DROP TABLE IF EXISTS `m_tb_http_webmail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_webmail` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` text NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sFrom` varchar(255) NOT NULL COMMENT '发件人',
  `sTo` varchar(255) NOT NULL COMMENT '收件人',
  `sChao` varchar(255) DEFAULT NULL COMMENT '抄送',
  `sMi` varchar(255) DEFAULT NULL COMMENT '密送',
  `sSubject` varchar(255) DEFAULT NULL COMMENT '邮件主题',
  `sContent` text COMMENT '邮件内容',
  `sAttachFilename` text NOT NULL COMMENT '''附件-文件名''',
  `sAttachFileSize` text COMMENT '''附件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-WebMail日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_webmail_overseas`
--

DROP TABLE IF EXISTS `m_tb_http_webmail_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_webmail_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` text NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sFrom` varchar(255) NOT NULL COMMENT '发件人',
  `sTo` varchar(255) NOT NULL COMMENT '收件人',
  `sChao` varchar(255) DEFAULT NULL COMMENT '抄送',
  `sMi` varchar(255) DEFAULT NULL COMMENT '密送',
  `sSubject` varchar(255) DEFAULT NULL COMMENT '邮件主题',
  `sContent` text COMMENT '邮件内容',
  `sAttachFilename` text NOT NULL COMMENT '''附件-文件名''',
  `sAttachFileSize` text COMMENT '''附件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-WebMail日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_weibo`
--

DROP TABLE IF EXISTS `m_tb_http_weibo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_weibo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(64) NOT NULL COMMENT '用户名',
  `sContent` text NOT NULL COMMENT '内容',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-微博日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_http_weibo_overseas`
--

DROP TABLE IF EXISTS `m_tb_http_weibo_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_http_weibo_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sSiteName` varchar(64) NOT NULL COMMENT '站点名',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sMethod` varchar(8) NOT NULL COMMENT 'http访问方式，如POST,GET',
  `sField` varchar(512) NOT NULL COMMENT '获取的信息字段，一条记录中可以包含多个字段信息',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUsername` varchar(64) NOT NULL COMMENT '用户名',
  `sContent` text NOT NULL COMMENT '内容',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-微博日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_netbios`
--

DROP TABLE IF EXISTS `m_tb_netbios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_netbios` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sType` varchar(128) NOT NULL COMMENT '''类型(上传或下载)''',
  `sStorepath` varchar(255) NOT NULL COMMENT '''文件保存路径''',
  `sUsername` varchar(255) DEFAULT NULL COMMENT '''用户名''',
  `sFilename` varchar(255) NOT NULL COMMENT '''文件名''',
  `sOldFilename` varchar(255) DEFAULT NULL COMMENT '''类型为重命名时的原文件名''',
  `sFilzesize` varchar(255) DEFAULT NULL COMMENT '''文件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-NetBIOS日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_netbios_overseas`
--

DROP TABLE IF EXISTS `m_tb_netbios_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_netbios_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sType` varchar(128) NOT NULL COMMENT '''类型(上传或下载)''',
  `sStorepath` varchar(255) NOT NULL COMMENT '''文件保存路径''',
  `sUsername` varchar(255) DEFAULT NULL COMMENT '''用户名''',
  `sFilename` varchar(255) NOT NULL COMMENT '''文件名''',
  `sOldFilename` varchar(255) DEFAULT NULL COMMENT '''类型为重命名时的原文件名''',
  `sFilzesize` varchar(255) DEFAULT NULL COMMENT '''文件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-NetBIOS日志-海外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_nfs`
--

DROP TABLE IF EXISTS `m_tb_nfs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_nfs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sType` varchar(128) NOT NULL COMMENT '''类型(上传或下载)''',
  `sStorepath` varchar(255) NOT NULL COMMENT '''文件保存路径''',
  `sFilename` varchar(255) NOT NULL COMMENT '''文件名''',
  `sOldFilename` varchar(255) DEFAULT NULL COMMENT '''类型为重命名时的原文件名''',
  `sFilesize` varchar(255) DEFAULT NULL COMMENT '''文件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-NFS日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_nfs_overseas`
--

DROP TABLE IF EXISTS `m_tb_nfs_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_nfs_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sType` varchar(128) NOT NULL COMMENT '''类型(上传或下载)''',
  `sStorepath` varchar(255) NOT NULL COMMENT '''文件保存路径''',
  `sFilename` varchar(255) NOT NULL COMMENT '''文件名''',
  `sOldFilename` varchar(255) DEFAULT NULL COMMENT '''类型为重命名时的原文件名''',
  `sFilesize` varchar(255) DEFAULT NULL COMMENT '''文件大小''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-NFS日志-海外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_proxy`
--

DROP TABLE IF EXISTS `m_tb_proxy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_proxy` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Proxy日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_proxy_overseas`
--

DROP TABLE IF EXISTS `m_tb_proxy_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_proxy_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Proxy日志-海外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_qq`
--

DROP TABLE IF EXISTS `m_tb_qq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_qq` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sSendID` bigint(32) NOT NULL COMMENT 'QQ发送ID',
  `sRecvID` bigint(32) NOT NULL COMMENT 'QQ接收ID',
  `sAction` varchar(256) NOT NULL COMMENT 'QQ动作',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-QQ日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_qq_overseas`
--

DROP TABLE IF EXISTS `m_tb_qq_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_qq_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sSendID` bigint(32) NOT NULL COMMENT 'QQ发送ID',
  `sRecvID` bigint(32) NOT NULL COMMENT 'QQ接收ID',
  `sAction` varchar(256) NOT NULL COMMENT 'QQ动作',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-QQ日志-海外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_report_manage`
--

DROP TABLE IF EXISTS `m_tb_report_manage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_report_manage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sname` varchar(300) DEFAULT NULL,
  `scontent` varchar(128) DEFAULT NULL,
  `sdesc` varchar(128) DEFAULT NULL,
  `stype` varchar(10) DEFAULT NULL,
  `iTime` varchar(200) NOT NULL DEFAULT 'CURRENT_TIMESTAMP(6)',
  `spath` varchar(256) DEFAULT NULL,
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_sql_log`
--

DROP TABLE IF EXISTS `m_tb_sql_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_sql_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDatabaseType` varchar(128) NOT NULL COMMENT '数据库类型',
  `sDatabaseName` varchar(255) NOT NULL COMMENT '数据库名称',
  `sSQL` varchar(1024) NOT NULL COMMENT 'SQL语句',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-SQL日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_sql_log_overseas`
--

DROP TABLE IF EXISTS `m_tb_sql_log_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_sql_log_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDatabaseType` varchar(128) NOT NULL COMMENT '数据库类型',
  `sDatabaseName` varchar(255) NOT NULL COMMENT '数据库名称',
  `sSQL` varchar(1024) NOT NULL COMMENT 'SQL语句',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-SQL日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_audit`
--

DROP TABLE IF EXISTS `m_tb_statistics_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_audit` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''统计类型-audit|alert|filter''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `sUsername` varchar(32) DEFAULT NULL COMMENT '''认证用户名''',
  `sDept` varchar(32) DEFAULT NULL COMMENT '''认证部门''',
  `sKeyword` varchar(256) DEFAULT NULL COMMENT '''命中关键字(alert|filter)''',
  `iOverseas` int(8) NOT NULL COMMENT '''是否海外日志 0-否  1-是''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`),
  KEY `i_time_index` (`iTime`),
  KEY `s_apptype_index` (`sAppType`,`iCount`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''Email应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_audit_date`
--

DROP TABLE IF EXISTS `m_tb_statistics_audit_date`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_audit_date` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''统计类型-audit|alert|filter''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `sUsername` varchar(32) DEFAULT NULL COMMENT '''认证用户名''',
  `sDept` varchar(32) DEFAULT NULL COMMENT '''认证部门''',
  `sKeyword` varchar(256) DEFAULT NULL COMMENT '''命中关键字(alert|filter)''',
  `iOverseas` int(8) NOT NULL COMMENT '''是否海外日志 0-否  1-是''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`),
  KEY `i_time_index` (`iTime`),
  KEY `s_apptype_index` (`sAppType`,`iCount`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''Email应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_audit_halfhour`
--

DROP TABLE IF EXISTS `m_tb_statistics_audit_halfhour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_audit_halfhour` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''统计类型-audit|alert|filter''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `sUsername` varchar(32) DEFAULT NULL COMMENT '''认证用户名''',
  `sDept` varchar(32) DEFAULT NULL COMMENT '''认证部门''',
  `sKeyword` varchar(256) DEFAULT NULL COMMENT '''命中关键字(alert|filter)''',
  `iOverseas` int(8) NOT NULL COMMENT '''是否海外日志 0-否  1-是''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`),
  KEY `i_time_index` (`iTime`),
  KEY `s_apptype_index` (`sAppType`,`iCount`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''Email应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_audit_hour`
--

DROP TABLE IF EXISTS `m_tb_statistics_audit_hour`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_audit_hour` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''统计类型-audit|alert|filter''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `sUsername` varchar(32) DEFAULT NULL COMMENT '''认证用户名''',
  `sDept` varchar(32) DEFAULT NULL COMMENT '''认证部门''',
  `sKeyword` varchar(256) DEFAULT NULL COMMENT '''命中关键字(alert|filter)''',
  `iOverseas` int(8) NOT NULL COMMENT '''是否海外日志 0-否  1-是''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`),
  KEY `i_time_index` (`iTime`),
  KEY `s_apptype_index` (`sAppType`,`iCount`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''Email应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_email`
--

DROP TABLE IF EXISTS `m_tb_statistics_email`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_email` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''统计类型-audit|alert|filter''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `sUsername` varchar(32) DEFAULT NULL COMMENT '''认证用户名''',
  `sDept` varchar(32) DEFAULT NULL COMMENT '''认证部门''',
  `sKeyword` varchar(256) DEFAULT NULL COMMENT '''命中关键字(alert|filter)''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COMMENT='''Email应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_ftp`
--

DROP TABLE IF EXISTS `m_tb_statistics_ftp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_ftp` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''FTP应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_game`
--

DROP TABLE IF EXISTS `m_tb_statistics_game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_game` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''游戏应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_http_bbs`
--

DROP TABLE IF EXISTS `m_tb_statistics_http_bbs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_http_bbs` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''BBS应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_http_blog`
--

DROP TABLE IF EXISTS `m_tb_statistics_http_blog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_http_blog` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''BLOG应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_http_netstore`
--

DROP TABLE IF EXISTS `m_tb_statistics_http_netstore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_http_netstore` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''网盘应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_http_search`
--

DROP TABLE IF EXISTS `m_tb_statistics_http_search`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_http_search` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''搜索引擎应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_http_shopping`
--

DROP TABLE IF EXISTS `m_tb_statistics_http_shopping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_http_shopping` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''购物网站应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_http_url_log`
--

DROP TABLE IF EXISTS `m_tb_statistics_http_url_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_http_url_log` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''网页浏览应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_http_video`
--

DROP TABLE IF EXISTS `m_tb_statistics_http_video`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_http_video` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''视频网站应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_http_webmail`
--

DROP TABLE IF EXISTS `m_tb_statistics_http_webmail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_http_webmail` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''网页邮件应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_http_weibo`
--

DROP TABLE IF EXISTS `m_tb_statistics_http_weibo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_http_weibo` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''微博应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_proxy`
--

DROP TABLE IF EXISTS `m_tb_statistics_proxy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_proxy` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''Proxy应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_qq`
--

DROP TABLE IF EXISTS `m_tb_statistics_qq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_qq` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''QQ应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_sql`
--

DROP TABLE IF EXISTS `m_tb_statistics_sql`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_sql` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''SQL应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_telnet`
--

DROP TABLE IF EXISTS `m_tb_statistics_telnet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_telnet` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''Telnet应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_statistics_trojan`
--

DROP TABLE IF EXISTS `m_tb_statistics_trojan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_statistics_trojan` (
  `id` int(20) NOT NULL,
  `sAppType` varchar(64) NOT NULL COMMENT '''应用类型''',
  `sStatisticsType` varchar(64) NOT NULL COMMENT '''策略类型 标题-正文_消息-附件名_文件名-附件_文件内容''',
  `sAlertGrade` varchar(32) NOT NULL COMMENT '''警告级别 高-中-低''',
  `sIP` varchar(256) NOT NULL COMMENT '''IP''',
  `iTime` int(20) NOT NULL COMMENT '''统计时间''',
  `iCount` int(20) NOT NULL COMMENT '''命中计数''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='''木马应用监控策略命中统计''';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_stock`
--

DROP TABLE IF EXISTS `m_tb_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_stock` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-股票软件日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_stock_overseas`
--

DROP TABLE IF EXISTS `m_tb_stock_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_stock_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-股票软件日志-海外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_telnet`
--

DROP TABLE IF EXISTS `m_tb_telnet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_telnet` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUserName` varchar(128) NOT NULL COMMENT 'Telnet用户名',
  `sPassword` varchar(128) NOT NULL COMMENT 'Telnet密码',
  `sAction` varchar(256) NOT NULL COMMENT 'Telnet动作',
  `sFilename` varchar(256) NOT NULL COMMENT '文件名',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Telnet日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_telnet_overseas`
--

DROP TABLE IF EXISTS `m_tb_telnet_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_telnet_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUserName` varchar(128) NOT NULL COMMENT 'Telnet用户名',
  `sPassword` varchar(128) NOT NULL COMMENT 'Telnet密码',
  `sAction` varchar(256) NOT NULL COMMENT 'Telnet动作',
  `sFilename` varchar(256) NOT NULL COMMENT '文件名',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Telnet日志-海外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_trojan`
--

DROP TABLE IF EXISTS `m_tb_trojan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_trojan` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Trojan日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_trojan_overseas`
--

DROP TABLE IF EXISTS `m_tb_trojan_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_trojan_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(32) NOT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sUser` varchar(255) NOT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) NOT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sDescr` varchar(256) NOT NULL COMMENT '描述',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-Trojan日志-海外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_urlfilter`
--

DROP TABLE IF EXISTS `m_tb_urlfilter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_urlfilter` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUrlType` varchar(255) DEFAULT NULL COMMENT 'URL分类',
  `sRuleName` varchar(255) NOT NULL COMMENT '规则名',
  `sRuleId` varchar(512) NOT NULL COMMENT '规则ID',
  `sRuleAction` varchar(512) NOT NULL COMMENT '规则动作',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-URL Filter日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tb_urlfilter_overseas`
--

DROP TABLE IF EXISTS `m_tb_urlfilter_overseas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tb_urlfilter_overseas` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sAppProto` varchar(10) DEFAULT NULL COMMENT '应用协议',
  `iDate` int(11) NOT NULL COMMENT '当前记录生成时间',
  `sSrcMac` varchar(64) NOT NULL COMMENT '源mac地址',
  `sSrcIP` varchar(20) NOT NULL COMMENT '源ip',
  `iSrcPort` int(16) NOT NULL COMMENT '源端口',
  `sDstMac` varchar(64) NOT NULL COMMENT '目的mac地址',
  `sDstIP` varchar(20) NOT NULL COMMENT '目的ip',
  `iDstPort` int(16) NOT NULL COMMENT '目的端口',
  `sType` varchar(16) NOT NULL COMMENT '类型,如webmail,search,netstore等',
  `sHost` varchar(128) NOT NULL COMMENT '站点host',
  `sUri` text NOT NULL COMMENT '访问的uri',
  `sUser` varchar(255) DEFAULT NULL COMMENT '认证用户的用户名',
  `sDept` varchar(255) DEFAULT NULL COMMENT '认证用户所属部门',
  `sScc` varchar(64) NOT NULL COMMENT '地理位置',
  `sSccFlag` int(11) NOT NULL COMMENT '0-境外 1-中国 2-台湾 3-香港 4-澳门',
  `sUrlType` varchar(255) DEFAULT NULL COMMENT 'URL分类',
  `sRuleName` varchar(8) NOT NULL COMMENT '规则名',
  `sRuleId` varchar(512) NOT NULL COMMENT '规则ID',
  `sRuleAction` varchar(512) NOT NULL COMMENT '规则动作',
  `sDeviceID` varchar(255) DEFAULT NULL COMMENT '日志来源设备ID',
  `sAlertLevel` varchar(32) NOT NULL DEFAULT '信息' COMMENT '''告警级别''',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='上网行为审计-URL Filter日志-境外';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbauthenticate_log`
--

DROP TABLE IF EXISTS `m_tbauthenticate_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbauthenticate_log` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `iTime` int(32) DEFAULT NULL COMMENT '用户上下线时间',
  `sUserName` varchar(32) DEFAULT NULL COMMENT '用户名',
  `sIP` varchar(32) DEFAULT NULL COMMENT '用户ip',
  `iAction` tinyint(1) DEFAULT NULL COMMENT '1表示上线， 0表示下线',
  `iStatus` tinyint(1) DEFAULT '0' COMMENT '0 成功， 1 失败， 2 找不到策略， 3 找不到认证服务器， 4 登录ip与该用户所绑定的ip不相符， 5 没有开启用户认证， 6 找不到该用户',
  `iType` tinyint(1) DEFAULT NULL COMMENT '2本地认证， 3外部认证',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbexport_csv`
--

DROP TABLE IF EXISTS `m_tbexport_csv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbexport_csv` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) DEFAULT NULL COMMENT '时间',
  `sFilename` varchar(128) DEFAULT NULL COMMENT '导出文件名',
  `sPath` varchar(512) DEFAULT NULL COMMENT '导出路径',
  `sCondition` varchar(256) DEFAULT NULL COMMENT '导出条件',
  `sStatus` varchar(32) DEFAULT 'NotExists' COMMENT '运行状态',
  `iPID` int(10) DEFAULT '0' COMMENT '导入进程的PID号',
  `sEname` varchar(100) DEFAULT NULL,
  `sData` varchar(255) DEFAULT NULL COMMENT '存储所有数据',
  `sExportobject` varchar(255) DEFAULT NULL,
  `iStatus` tinyint(2) DEFAULT NULL,
  `sDate` varchar(255) DEFAULT NULL,
  `eDate` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbfileset`
--

DROP TABLE IF EXISTS `m_tbfileset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbfileset` (
  `sDir` varchar(100) DEFAULT NULL,
  `sDate` varchar(50) DEFAULT NULL,
  `sTime` varchar(50) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbfwsessionstatus`
--

DROP TABLE IF EXISTS `m_tbfwsessionstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbfwsessionstatus` (
  `id` int(14) NOT NULL AUTO_INCREMENT,
  `sMark` varchar(100) NOT NULL COMMENT '当前日志唯一标识',
  `sSourceIp` varchar(160) DEFAULT NULL COMMENT '源IP',
  `iSourcePort` int(11) DEFAULT NULL COMMENT '源端口',
  `sTargetIP` varchar(160) DEFAULT NULL COMMENT '目的IP',
  `iTargetPort` int(11) DEFAULT NULL COMMENT '目的端口',
  `sProtocal` varchar(20) DEFAULT NULL COMMENT '协议',
  `sAcProtocal` varchar(255) DEFAULT NULL COMMENT '应用协议',
  `sCreatTime` int(255) DEFAULT NULL COMMENT '会话创建时间',
  `sLastTime` int(255) DEFAULT NULL COMMENT '会话最后更新时间',
  `sOverTime` varchar(20) DEFAULT NULL COMMENT '超时时间',
  `iStatus` varchar(20) NOT NULL COMMENT '状态（1表示已连接，0表示已断开）',
  `sUpdateTime` int(255) DEFAULT NULL COMMENT '日志入库时间',
  PRIMARY KEY (`id`),
  KEY `i_updatetime` (`sUpdateTime`),
  KEY `i_updatetime_status` (`sUpdateTime`,`iStatus`) USING BTREE,
  KEY `i_lasttime` (`sLastTime`) USING BTREE,
  KEY `i_status` (`iStatus`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbfwsessionstatus_20170713`
--

DROP TABLE IF EXISTS `m_tbfwsessionstatus_20170713`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbfwsessionstatus_20170713` (
  `id` int(14) NOT NULL AUTO_INCREMENT,
  `sMark` varchar(100) NOT NULL COMMENT '当前日志唯一标识',
  `sSourceIp` varchar(160) DEFAULT NULL COMMENT '源IP',
  `iSourcePort` int(11) DEFAULT NULL COMMENT '源端口',
  `sTargetIP` varchar(160) DEFAULT NULL COMMENT '目的IP',
  `iTargetPort` int(11) DEFAULT NULL COMMENT '目的端口',
  `sProtocal` varchar(20) DEFAULT NULL COMMENT '协议',
  `sAcProtocal` varchar(255) DEFAULT NULL COMMENT '应用协议',
  `sCreatTime` int(255) DEFAULT NULL COMMENT '会话创建时间',
  `sLastTime` int(255) DEFAULT NULL COMMENT '会话最后更新时间',
  `sOverTime` varchar(20) DEFAULT NULL COMMENT '超时时间',
  `iStatus` varchar(20) NOT NULL COMMENT '状态（1表示已连接，0表示已断开）',
  `sUpdateTime` int(255) DEFAULT NULL COMMENT '日志入库时间',
  PRIMARY KEY (`id`),
  KEY `i_updatetime` (`sUpdateTime`),
  KEY `i_updatetime_status` (`sUpdateTime`,`iStatus`) USING BTREE,
  KEY `i_lasttime` (`sLastTime`) USING BTREE,
  KEY `i_status` (`iStatus`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbfwsessionstatus_sourceip`
--

DROP TABLE IF EXISTS `m_tbfwsessionstatus_sourceip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbfwsessionstatus_sourceip` (
  `id` int(14) NOT NULL AUTO_INCREMENT,
  `sSourceIp` varchar(150) NOT NULL COMMENT '会回中的源ip',
  `sProto` varchar(10) DEFAULT NULL COMMENT '协议',
  `sCount` int(14) DEFAULT '1' COMMENT '会话中源ip出现的次数',
  PRIMARY KEY (`id`),
  UNIQUE KEY `i_source` (`sSourceIp`,`sProto`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbhoneypot_log`
--

DROP TABLE IF EXISTS `m_tbhoneypot_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbhoneypot_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) DEFAULT NULL COMMENT '时间',
  `sProtocol` varchar(128) DEFAULT NULL COMMENT '蜜罐协议',
  `sSourceAddr` varchar(64) DEFAULT NULL COMMENT '来源地址',
  `sSourcePort` varchar(64) DEFAULT NULL COMMENT '来源端口',
  `sTargetAddr` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sTargetPort` varchar(64) DEFAULT NULL COMMENT '目标端口',
  `iConnectTime` int(11) DEFAULT NULL COMMENT '连接时长',
  `sUserName` varchar(128) DEFAULT NULL COMMENT '用户名称',
  `iCommandTotal` int(11) DEFAULT NULL COMMENT '命令总数',
  `sThreatEvaluate` varchar(256) DEFAULT NULL COMMENT '威胁评估',
  `sDetail` varchar(512) DEFAULT NULL COMMENT '详细操作',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='蜜罐日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbhoneypot_status`
--

DROP TABLE IF EXISTS `m_tbhoneypot_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbhoneypot_status` (
  `iId` int(11) NOT NULL,
  `iConnectRootid` int(11) DEFAULT NULL,
  `iConnectParentid` int(11) DEFAULT NULL,
  `sName` varchar(255) DEFAULT NULL COMMENT '名称',
  `sConfigName` varchar(255) DEFAULT NULL COMMENT '配置名称',
  `iTime` bigint(20) DEFAULT NULL,
  `sProtocol` varchar(255) DEFAULT NULL COMMENT '蜜罐协议',
  `sSrcAddr` varchar(255) DEFAULT NULL COMMENT '来源地址',
  `iSrcPort` int(11) DEFAULT NULL,
  `sSrcHostName` varchar(255) DEFAULT NULL,
  `sDesAddr` varchar(255) DEFAULT NULL COMMENT '目标地址',
  `iDesPort` int(11) DEFAULT NULL,
  `iDisconnectTime` bigint(20) DEFAULT NULL COMMENT '连接时间',
  `sUserName` varchar(255) DEFAULT NULL COMMENT '用户名称',
  `iDataFlow` bigint(20) DEFAULT NULL COMMENT '数据流量',
  `sCommand` varchar(255) DEFAULT NULL COMMENT '命令',
  `iThreaten` int(11) DEFAULT NULL COMMENT '威胁',
  `sStatus` varchar(255) DEFAULT NULL COMMENT '状态',
  `sDetail` text,
  PRIMARY KEY (`iId`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='蜜罐状态';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbipsec_log`
--

DROP TABLE IF EXISTS `m_tbipsec_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbipsec_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sLocal` varchar(128) DEFAULT NULL COMMENT '本端',
  `sTarget` varchar(128) DEFAULT NULL COMMENT '对端',
  `iType` tinyint(4) DEFAULT NULL COMMENT '类型 1.操作行为 2.安全事件 3.异常事件',
  `sType` varchar(64) DEFAULT NULL COMMENT 'iType的子类型',
  `sData` varchar(512) DEFAULT NULL COMMENT '详细的日志信息',
  `iStatus` tinyint(4) NOT NULL DEFAULT '1' COMMENT '结果 默认1.成功   0.失败',
  `iTime` int(11) DEFAULT NULL COMMENT '时间戳',
  `iCount` int(11) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbipsec_log_20171112`
--

DROP TABLE IF EXISTS `m_tbipsec_log_20171112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbipsec_log_20171112` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sLocal` varchar(128) DEFAULT NULL COMMENT '本端',
  `sTarget` varchar(128) DEFAULT NULL COMMENT '对端',
  `iType` tinyint(4) DEFAULT NULL COMMENT '类型 1.操作行为 2.安全事件 3.异常事件',
  `sType` varchar(64) DEFAULT NULL COMMENT 'iType的子类型',
  `sData` varchar(512) DEFAULT NULL COMMENT '详细的日志信息',
  `iStatus` tinyint(4) NOT NULL DEFAULT '1' COMMENT '结果 默认1.成功   0.失败',
  `iTime` int(11) DEFAULT NULL COMMENT '时间戳',
  `iCount` int(11) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_app_admin`
--

DROP TABLE IF EXISTS `m_tblog_app_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_app_admin` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` varchar(64) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAppName` (`iTime`,`sAppName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='应用管理日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_app_admin_20171114`
--

DROP TABLE IF EXISTS `m_tblog_app_admin_20171114`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_app_admin_20171114` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` varchar(64) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAppName` (`iTime`,`sAppName`)
) ENGINE=MyISAM AUTO_INCREMENT=223306 DEFAULT CHARSET=utf8 COMMENT='应用管理日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_app_admin_20171115`
--

DROP TABLE IF EXISTS `m_tblog_app_admin_20171115`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_app_admin_20171115` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` varchar(64) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAppName` (`iTime`,`sAppName`)
) ENGINE=MyISAM AUTO_INCREMENT=516243 DEFAULT CHARSET=utf8 COMMENT='应用管理日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_app_admin_20171117`
--

DROP TABLE IF EXISTS `m_tblog_app_admin_20171117`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_app_admin_20171117` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` varchar(64) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAppName` (`iTime`,`sAppName`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='应用管理日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_app_admin_20171121`
--

DROP TABLE IF EXISTS `m_tblog_app_admin_20171121`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_app_admin_20171121` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` varchar(64) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAppName` (`iTime`,`sAppName`)
) ENGINE=MyISAM AUTO_INCREMENT=17963 DEFAULT CHARSET=utf8 COMMENT='应用管理日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_app_admin_20171122`
--

DROP TABLE IF EXISTS `m_tblog_app_admin_20171122`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_app_admin_20171122` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` varchar(64) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAppName` (`iTime`,`sAppName`)
) ENGINE=MyISAM AUTO_INCREMENT=94463 DEFAULT CHARSET=utf8 COMMENT='应用管理日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_app_admin_20171123`
--

DROP TABLE IF EXISTS `m_tblog_app_admin_20171123`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_app_admin_20171123` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` varchar(64) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAppName` (`iTime`,`sAppName`)
) ENGINE=MyISAM AUTO_INCREMENT=569177 DEFAULT CHARSET=utf8 COMMENT='应用管理日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_app_admin_20171124`
--

DROP TABLE IF EXISTS `m_tblog_app_admin_20171124`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_app_admin_20171124` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` varchar(64) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAppName` (`iTime`,`sAppName`)
) ENGINE=MyISAM AUTO_INCREMENT=168055 DEFAULT CHARSET=utf8 COMMENT='应用管理日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_ddos`
--

DROP TABLE IF EXISTS `m_tblog_ddos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_ddos` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sEventName` varchar(128) NOT NULL COMMENT '事件名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sThreshold` varchar(64) DEFAULT NULL COMMENT '阈值',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sStatus` tinyint(2) NOT NULL COMMENT '状态',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeEventName` (`iTime`,`sEventName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='DDos防御日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_ddos_record`
--

DROP TABLE IF EXISTS `m_tblog_ddos_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_ddos_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sEventName` varchar(64) NOT NULL COMMENT '事件名称',
  `iCount` bigint(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sEventName` (`sEventName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_evil_code`
--

DROP TABLE IF EXISTS `m_tblog_evil_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_evil_code` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sViruesName` varchar(128) NOT NULL COMMENT '病毒名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sStatus` varchar(64) NOT NULL COMMENT '状态',
  `sLogLevel` varchar(64) DEFAULT NULL,
  `sFileName` varchar(256) DEFAULT NULL COMMENT '文件名',
  `sUserName` varchar(64) DEFAULT NULL COMMENT '用户名',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTiemVirName` (`iTime`,`sViruesName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='恶意代码防御日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_evilcode_record`
--

DROP TABLE IF EXISTS `m_tblog_evilcode_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_evilcode_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sVirusName` varchar(128) NOT NULL,
  `sLogLevel` varchar(64) DEFAULT NULL,
  `iCount` bigint(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sVirusName` (`sVirusName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall`
--

DROP TABLE IF EXISTS `m_tblog_firewall`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171114`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171114`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171114` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=503034 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171115`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171115`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171115` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=1174097 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171116`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171116`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171116` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=32765 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171117`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171117`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171117` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=40630 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171118`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171118`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171118` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=18903 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171119`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171119`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171119` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=19976 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171120`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171120`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171120` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=42533 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171121`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171121`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171121` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=36664 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171122`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171122`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171122` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=270142 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171123`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171123`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171123` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=1466085 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_firewall_20171124`
--

DROP TABLE IF EXISTS `m_tblog_firewall_20171124`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_firewall_20171124` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
  `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
  `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
  `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
  `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
  `sAction` varchar(32) NOT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=258596 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_info_leak`
--

DROP TABLE IF EXISTS `m_tblog_info_leak`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_info_leak` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sFileKeywork` varchar(128) DEFAULT NULL COMMENT '文件/关键字',
  `sFilterType` varchar(64) DEFAULT NULL COMMENT '过滤类型',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sStatus` varchar(64) NOT NULL COMMENT '状态',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTime` (`iTime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='信息泄漏防御日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_ips`
--

DROP TABLE IF EXISTS `m_tblog_ips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_ips` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sEventName` varchar(256) NOT NULL COMMENT '事件名称',
  `sSourceIP` varchar(64) NOT NULL COMMENT '源地址',
  `sProtocol` varchar(64) NOT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sStatus` varchar(16) NOT NULL COMMENT '状态',
  `sLogName` varchar(255) DEFAULT NULL COMMENT 'log文件名称',
  `sRuleID` varchar(128) NOT NULL COMMENT '规则ID',
  `sGrade` varchar(16) DEFAULT NULL COMMENT '风险等级',
  `sDesc` text COMMENT '描述',
  `sRuleType` varchar(256) DEFAULT NULL COMMENT '规则分类',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAndEvent` (`iTime`,`sEventName`) USING BTREE,
  KEY `I_sRuleID` (`sRuleID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='入侵防御日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_ips_record`
--

DROP TABLE IF EXISTS `m_tblog_ips_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_ips_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sEventName` varchar(256) NOT NULL COMMENT '事件名称',
  `sRuleID` varchar(128) NOT NULL COMMENT '规则ID',
  `sGrade` varchar(16) DEFAULT NULL COMMENT '风险等级',
  `iCount` bigint(32) NOT NULL,
  `sRuleType` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sEventName` (`sEventName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_library`
--

DROP TABLE IF EXISTS `m_tblog_library`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_library` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sDate` varchar(32) NOT NULL,
  `sFileName` varchar(64) NOT NULL,
  `sSize` varchar(64) NOT NULL,
  `iTime` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_size_record`
--

DROP TABLE IF EXISTS `m_tblog_size_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_size_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sLogName` varchar(255) NOT NULL,
  `sImportSize` bigint(32) NOT NULL DEFAULT '0',
  `iTime` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `log_name` (`sLogName`)
) ENGINE=InnoDB AUTO_INCREMENT=174 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_sys_admin`
--

DROP TABLE IF EXISTS `m_tblog_sys_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_sys_admin` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iUserId` varchar(50) NOT NULL COMMENT '用户id',
  `sSubAccount` varchar(64) DEFAULT NULL COMMENT '子帐号',
  `iLoginTime` int(11) NOT NULL COMMENT '登录时间',
  `sIp` varchar(64) DEFAULT NULL COMMENT '操作IP',
  `sStatus` tinyint(2) NOT NULL COMMENT '状态',
  `sContent` varchar(255) DEFAULT NULL COMMENT '日志内容',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='增删改管理员日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_sys_backup`
--

DROP TABLE IF EXISTS `m_tblog_sys_backup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_sys_backup` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iUserId` varchar(50) NOT NULL COMMENT '用户id',
  `iTime` int(11) NOT NULL COMMENT '登录时间',
  `sIp` varchar(128) DEFAULT NULL COMMENT '操作IP',
  `sResult` varchar(255) NOT NULL COMMENT '状态',
  `sContent` varchar(255) DEFAULT NULL COMMENT '日志内容',
  PRIMARY KEY (`id`),
  KEY `I_iLoginTime` (`iTime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='恢复与备份日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_sys_reboot`
--

DROP TABLE IF EXISTS `m_tblog_sys_reboot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_sys_reboot` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iUserId` varchar(50) NOT NULL COMMENT '用户id',
  `iLoginTime` int(11) NOT NULL COMMENT '登录时间',
  `sIp` varchar(64) DEFAULT NULL COMMENT '操作IP',
  `sStatus` tinyint(2) NOT NULL COMMENT '状态',
  `sContent` varchar(255) DEFAULT NULL COMMENT '日志内容',
  PRIMARY KEY (`id`),
  KEY `I_iLoginTime` (`iLoginTime`)
) ENGINE=MyISAM AUTO_INCREMENT=88 DEFAULT CHARSET=utf8 COMMENT='重启与关机日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_sys_resource`
--

DROP TABLE IF EXISTS `m_tblog_sys_resource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_sys_resource` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '登录时间',
  `sSubject` varchar(128) DEFAULT NULL COMMENT '告警项',
  `sContent` varchar(255) DEFAULT NULL COMMENT '描述',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='重启与关机日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_url_visit`
--

DROP TABLE IF EXISTS `m_tblog_url_visit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_url_visit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(100) NOT NULL COMMENT '时间',
  `sUrl` varchar(512) NOT NULL COMMENT 'url地址',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sWebType` varchar(64) DEFAULT NULL COMMENT '网站类型',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` tinyint(2) DEFAULT NULL COMMENT '动作',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTime` (`iTime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='url访问日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_webapp_record`
--

DROP TABLE IF EXISTS `m_tblog_webapp_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_webapp_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sEventName` varchar(128) DEFAULT NULL COMMENT '事件名称',
  `sSeverity` varchar(50) DEFAULT NULL,
  `sBugType` varchar(64) DEFAULT NULL COMMENT '漏洞类型',
  `iCount` bigint(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sEventName` (`sEventName`,`sSeverity`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_webapplication`
--

DROP TABLE IF EXISTS `m_tblog_webapplication`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_webapplication` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sEventName` varchar(128) DEFAULT NULL COMMENT '事件名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sBugType` varchar(64) DEFAULT NULL COMMENT '漏洞类型',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sStatus` varchar(10) DEFAULT NULL COMMENT '状态',
  `sSeverity` varchar(50) DEFAULT NULL,
  `iEventID` int(20) NOT NULL DEFAULT '0' COMMENT '''事件ID''',
  PRIMARY KEY (`id`),
  KEY `iTime` (`iTime`,`sEventName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='web应用防御日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblog_wifi_audit`
--

DROP TABLE IF EXISTS `m_tblog_wifi_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblog_wifi_audit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sShareHost` varchar(128) NOT NULL COMMENT '共享主机',
  `sTerminal` varchar(512) DEFAULT NULL COMMENT '共享上网主机',
  `sTableName` varchar(32) NOT NULL COMMENT '表名',
  `iCount` int(11) NOT NULL DEFAULT '1' COMMENT '重复日志数量',
  PRIMARY KEY (`id`),
  KEY `I_iTimeShareHost` (`iTime`,`sShareHost`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='共享上网日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbloginlog`
--

DROP TABLE IF EXISTS `m_tbloginlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbloginlog` (
  `iloginLogId` bigint(20) NOT NULL AUTO_INCREMENT,
  `iUserId` varchar(50) NOT NULL,
  `iLoginTime` int(11) NOT NULL,
  `sIp` varchar(64) DEFAULT NULL,
  `sStatus` tinyint(2) NOT NULL,
  `sContent` varchar(255) DEFAULT NULL,
  `sRole` tinyint(2) DEFAULT NULL,
  PRIMARY KEY (`iloginLogId`)
) ENGINE=MyISAM AUTO_INCREMENT=109801 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tblogtable`
--

DROP TABLE IF EXISTS `m_tblogtable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tblogtable` (
  `iId` bigint(20) NOT NULL AUTO_INCREMENT,
  `iLogtablename` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `iLogtablestate` varchar(2) CHARACTER SET utf8 DEFAULT '0',
  PRIMARY KEY (`iId`)
) ENGINE=InnoDB AUTO_INCREMENT=200 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tboperatelog`
--

DROP TABLE IF EXISTS `m_tboperatelog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tboperatelog` (
  `iLogId` bigint(20) NOT NULL AUTO_INCREMENT,
  `iDateTime` int(11) NOT NULL,
  `sIp` varchar(64) NOT NULL,
  `sOperateUser` varchar(50) NOT NULL,
  `sRs` varchar(200) NOT NULL,
  `sContent` varchar(255) NOT NULL,
  `sOperateAction` varchar(200) DEFAULT NULL,
  `sRole` tinyint(2) DEFAULT NULL,
  PRIMARY KEY (`iLogId`)
) ENGINE=MyISAM AUTO_INCREMENT=829 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbprotected_log`
--

DROP TABLE IF EXISTS `m_tbprotected_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbprotected_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) DEFAULT NULL COMMENT '时间',
  `sScanType` varchar(64) DEFAULT NULL COMMENT '扫描种类',
  `sSourceAddr` varchar(64) DEFAULT NULL COMMENT '来源地址',
  `sTargetAddr` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `iConnectNum` varchar(64) DEFAULT NULL COMMENT '连接数',
  `iAddressNum` varchar(64) DEFAULT NULL COMMENT '地址数',
  `iPortNum` varchar(64) DEFAULT NULL COMMENT '端口数',
  `iPortRange` varchar(64) DEFAULT NULL COMMENT '端口范围',
  `sDetail` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='防护日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbrevcamera_log`
--

DROP TABLE IF EXISTS `m_tbrevcamera_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbrevcamera_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) DEFAULT NULL COMMENT '时间',
  `sTrigerReason` varchar(512) DEFAULT NULL COMMENT '触发原因',
  `sTargetAddr` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sHostType` text COMMENT '主机类型',
  `sDistance` varchar(64) DEFAULT NULL COMMENT '距离',
  `sTimeDelay` varchar(64) DEFAULT NULL COMMENT '时延',
  `sDetail` text COMMENT '详细操作',
  `sFileName` varchar(512) DEFAULT NULL COMMENT '文件名',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 CHECKSUM=1 COMMENT='拍照日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbsessionstatus_targetip`
--

DROP TABLE IF EXISTS `m_tbsessionstatus_targetip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbsessionstatus_targetip` (
  `id` int(14) NOT NULL AUTO_INCREMENT,
  `sTargetIp` varchar(150) NOT NULL COMMENT '会话中的目的ip',
  `sProto` varchar(10) DEFAULT NULL COMMENT '协议',
  `sCount` int(14) DEFAULT '1' COMMENT '会话中的目的ip出现次数',
  PRIMARY KEY (`id`),
  UNIQUE KEY `s_test` (`sTargetIp`,`sProto`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbstatistics`
--

DROP TABLE IF EXISTS `m_tbstatistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbstatistics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sName` varchar(128) DEFAULT NULL COMMENT '名称',
  `sValue` text COMMENT '值',
  `sMark` varchar(512) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `i_name` (`sName`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8 COMMENT='统计数据表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbsystem_update_log`
--

DROP TABLE IF EXISTS `m_tbsystem_update_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbsystem_update_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sVersion` varchar(128) DEFAULT NULL COMMENT '升级版本',
  `sDescription` varchar(512) DEFAULT NULL COMMENT '描述',
  `iTime` int(11) DEFAULT NULL COMMENT '升级时间',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `m_tbwebapplication_lib`
--

DROP TABLE IF EXISTS `m_tbwebapplication_lib`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbwebapplication_lib` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sRuleID` varchar(128) DEFAULT NULL COMMENT '规则ID',
  `sRealID` varchar(128) DEFAULT NULL COMMENT '后台操作id',
  `iPriority` tinyint(2) DEFAULT NULL COMMENT '优先级',
  `sRuleName` varchar(512) DEFAULT NULL COMMENT '规则名称',
  `sDesc` text COMMENT '说明',
  `sType` varchar(128) DEFAULT NULL COMMENT '类型',
  `sDangerLever` varchar(64) DEFAULT NULL COMMENT '危险等级',
  `sInterceptionMethod` varchar(64) DEFAULT NULL COMMENT '拦截方式',
  `sHttpRequestType` varchar(64) DEFAULT NULL COMMENT 'HTTP请求类型',
  `sMatchAlgorithm` varchar(64) DEFAULT NULL COMMENT '匹配算法',
  `sMatchContent` varchar(64) DEFAULT NULL COMMENT '匹配内容',
  `sFeatureKey` varchar(512) DEFAULT NULL COMMENT '正则表达式字符串',
  `iStatus` tinyint(2) DEFAULT NULL COMMENT '状态，1开启，0关闭',
  `iUpdateTime` int(11) DEFAULT NULL COMMENT '更新时间 ',
  `iCustomOrInset` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='web应用防护规则库';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_ip_blackwhite_list`
--

DROP TABLE IF EXISTS `t_ip_blackwhite_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ip_blackwhite_list` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `s_name` varchar(24) DEFAULT NULL COMMENT '策略名称',
  `bw_type` int(10) DEFAULT NULL COMMENT '黑/白名单：1.黑名单；2.白名单',
  `s_action` int(10) DEFAULT NULL COMMENT '处理动作：1.报警；2.阻止并报警；3.放行',
  `alert_way` int(10) DEFAULT NULL COMMENT '报警方式：1.邮件；2.短信；4.声音；8.界面提示',
  `exp_date` varchar(24) CHARACTER SET latin1 DEFAULT NULL COMMENT '有效期：为空表示始终有效',
  `bewrite` varchar(128) CHARACTER SET latin1 DEFAULT NULL COMMENT '描述',
  `istatus` int(10) DEFAULT NULL COMMENT '启用状态：1.启用中；2.停用；0.未启用',
  `create_time` varchar(24) DEFAULT NULL COMMENT '创建时间',
  `update_time` varchar(24) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sm_keyword`
--

DROP TABLE IF EXISTS `t_sm_keyword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sm_keyword` (
  `iId` int(20) NOT NULL AUTO_INCREMENT,
  `sKeyword` varchar(64) DEFAULT NULL,
  `iTime` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`iId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sm_policy`
--

DROP TABLE IF EXISTS `t_sm_policy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sm_policy` (
  `s_name` varchar(64) DEFAULT NULL,
  `s_action` varchar(64) DEFAULT NULL,
  `alert_way` varchar(64) DEFAULT NULL,
  `bs_type` varchar(64) DEFAULT NULL,
  `bs_key` text,
  `istatus` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_smbscl`
--

DROP TABLE IF EXISTS `t_smbscl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_smbscl` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `s_name` varchar(64) NOT NULL,
  `s_action` varchar(64) DEFAULT NULL COMMENT ' 警告级别：1.低；2.中；3.高',
  `alert_way` varchar(64) DEFAULT NULL COMMENT '报警方式：1邮件，2短信，4声音，8界面消息提示',
  `s_time` datetime DEFAULT NULL COMMENT '开始时间',
  `e_time` datetime DEFAULT NULL COMMENT '结束时间',
  `s_desc` varchar(255) DEFAULT NULL,
  `bs_type` varchar(64) DEFAULT NULL COMMENT '标识类型：1标题，2附件名/文件名，3附件/文件内容，4正文/消息',
  `bs_key` text COMMENT '涉密标识关键字,用#分隔',
  `istatus` tinyint(1) DEFAULT NULL COMMENT '状态：0.未启用，1启用中，2停用',
  `inserttime` datetime DEFAULT NULL,
  `updatetime` datetime DEFAULT NULL,
  `exp_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_smbscl_mid`
--

DROP TABLE IF EXISTS `t_smbscl_mid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_smbscl_mid` (
  `iId` int(20) NOT NULL AUTO_INCREMENT,
  `iRuleId` int(20) DEFAULT NULL,
  `iKeywordId` int(20) DEFAULT NULL,
  `iUserId` int(20) DEFAULT NULL,
  PRIMARY KEY (`iId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-11-24  8:58:01
