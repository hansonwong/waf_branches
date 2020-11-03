use db_firewall_log;
/*
Navicat MySQL Data Transfer

Source Server         : 3.99_log
Source Server Version : 50630
Source Host           : localhost:3307
Source Database       : db_firewall_log

Target Server Type    : MYSQL
Target Server Version : 50630
File Encoding         : 65001

Date: 2016-07-12 15:30:01
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for m_IPS_template_rules
-- ----------------------------
DROP TABLE IF EXISTS `m_IPS_template_rules`;
CREATE TABLE `m_IPS_template_rules` (
  `id` int(11) NOT NULL,
  `iSID` int(11) NOT NULL,
  `sRules` text,
  PRIMARY KEY (`iSID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- ----------------------------
-- Table structure for m_tbauthenticate_log
-- ----------------------------
DROP TABLE IF EXISTS `m_tbauthenticate_log`;
CREATE TABLE `m_tbauthenticate_log` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `iTime` int(32) DEFAULT NULL COMMENT '用户上下线时间',
  `sUserName` varchar(32) DEFAULT NULL COMMENT '用户名',
  `sIP` varchar(32) DEFAULT NULL COMMENT '用户ip',
  `iAction` tinyint(1) DEFAULT NULL COMMENT '1表示上线， 0表示下线',
  `iStatus` tinyint(1) DEFAULT '0' COMMENT '0 成功， 1 失败， 2 找不到策略， 3 找不到认证服务器， 4 登录ip与该用户所绑定的ip不相符， 5 没有开启用户认证， 6 找不到该用户',
  `iType` tinyint(1) DEFAULT NULL COMMENT '2本地认证， 3外部认证',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tbcustom_ips_lib
-- ----------------------------
DROP TABLE IF EXISTS `m_tbcustom_ips_lib`;
CREATE TABLE `m_tbcustom_ips_lib` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sRuleID` varchar(128) DEFAULT NULL COMMENT '规则ID',
  `sRuleName` varchar(128) DEFAULT NULL COMMENT '规则名称',
  `sDesc` varchar(256) DEFAULT NULL COMMENT '描述',
  `sRuleType` varchar(256) DEFAULT NULL COMMENT '规则分类',
  `sDangerLever` varchar(64) DEFAULT NULL COMMENT '危险等级，1高，2中，3低',
  `sCharacterString` varchar(512) DEFAULT NULL COMMENT '字符串（json数据）',
  `iChartCaseSensitive` tinyint(1) DEFAULT NULL COMMENT '字符区分大小写',
  `sRegularExpressions` varchar(128) DEFAULT NULL COMMENT '正则表达式字符串',
  `iRegularCaseSensitive` tinyint(1) DEFAULT NULL COMMENT '正则区分大小写',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `iStatus` tinyint(2) DEFAULT '0' COMMENT '启用不启用,1为启用，0为不启用',
  `iCustomOrInset` tinyint(2) DEFAULT NULL COMMENT '自定义的还是内置的，1为自定义的，2为内置的',
  `sAction` varchar(50) DEFAULT NULL COMMENT '动作',
  `sRule` text,
  `sRuleBelongFile` varchar(200) DEFAULT NULL COMMENT '规则所在文件',
  PRIMARY KEY (`id`),
  KEY `i_sRuleID` (`sRuleID`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='自定义ips规则库';

-- ----------------------------
-- Table structure for m_tbfileset
-- ----------------------------
DROP TABLE IF EXISTS `m_tbfileset`;
CREATE TABLE `m_tbfileset` (
  `sDir` varchar(100) DEFAULT NULL,
  `sDate` varchar(50) DEFAULT NULL,
  `sTime` varchar(50) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- ----------------------------
-- Table structure for m_tbhoneypot_log
-- ----------------------------
DROP TABLE IF EXISTS `m_tbhoneypot_log`;
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

-- ----------------------------
-- Table structure for m_tbhoneypot_status
-- ----------------------------
DROP TABLE IF EXISTS `m_tbhoneypot_status`;
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

-- ----------------------------
-- Table structure for m_tblog_app_admin
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_app_admin`;
CREATE TABLE `m_tblog_app_admin` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` varchar(64) NOT NULL COMMENT '动作',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAppName` (`iTime`,`sAppName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='应用管理日志';

-- ----------------------------
-- Table structure for m_tblog_ddos
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_ddos`;
CREATE TABLE `m_tblog_ddos` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sEventName` varchar(128) NOT NULL COMMENT '事件名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sThreshold` varchar(64) DEFAULT NULL COMMENT '阈值',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sStatus` tinyint(2) NOT NULL COMMENT '状态',
  PRIMARY KEY (`id`),
  KEY `I_iTimeEventName` (`iTime`,`sEventName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='DDos防御日志';

-- ----------------------------
-- Table structure for m_tblog_ddos_record
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_ddos_record`;
CREATE TABLE `m_tblog_ddos_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sEventName` varchar(64) NOT NULL COMMENT '事件名称',
  `iCount` bigint(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sEventName` (`sEventName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tblog_evil_code
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_evil_code`;
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
  PRIMARY KEY (`id`),
  KEY `I_iTiemVirName` (`iTime`,`sViruesName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='恶意代码防御日志';

-- ----------------------------
-- Table structure for m_tblog_evilcode_record
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_evilcode_record`;
CREATE TABLE `m_tblog_evilcode_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sVirusName` varchar(128) NOT NULL,
  `sLogLevel` varchar(64) DEFAULT NULL,
  `iCount` bigint(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sVirusName` (`sVirusName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tblog_firewall
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_firewall`;
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
  PRIMARY KEY (`id`),
  KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`),
  KEY `i_sourceip` (`sSourceAddr`,`iTime`) USING BTREE,
  KEY `i_targetip` (`sTargetAddr`,`iTime`) USING BTREE,
  KEY `i_action` (`sAction`,`iTime`) USING BTREE
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='防火墙日志';

-- ----------------------------
-- Table structure for m_tblog_info_leak
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_info_leak`;
CREATE TABLE `m_tblog_info_leak` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sFileKeywork` varchar(128) DEFAULT NULL COMMENT '文件/关键字',
  `sFilterType` varchar(64) DEFAULT NULL COMMENT '过滤类型',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sStatus` varchar(64) NOT NULL COMMENT '状态',
  PRIMARY KEY (`id`),
  KEY `I_iTime` (`iTime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='信息泄漏防御日志';

-- ----------------------------
-- Table structure for m_tblog_ips
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_ips`;
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
  `sDesc` varchar(256) DEFAULT NULL COMMENT '描述',
  `sRuleType` varchar(256) DEFAULT NULL COMMENT '规则分类',
  PRIMARY KEY (`id`),
  KEY `I_iTimeAndEvent` (`iTime`,`sEventName`) USING BTREE,
  KEY `I_sRuleID` (`sRuleID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='入侵防御日志';

-- ----------------------------
-- Table structure for m_tblog_ips_record
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_ips_record`;
CREATE TABLE `m_tblog_ips_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sEventName` varchar(256) NOT NULL COMMENT '事件名称',
  `sRuleID` varchar(128) NOT NULL COMMENT '规则ID',
  `sGrade` varchar(16) DEFAULT NULL COMMENT '风险等级',
  `iCount` bigint(32) NOT NULL,
  `sRuleType` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sEventName` (`sEventName`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tblog_library
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_library`;
CREATE TABLE `m_tblog_library` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sDate` varchar(32) NOT NULL,
  `sFileName` varchar(64) NOT NULL,
  `sSize` varchar(64) NOT NULL,
  `iTime` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Table structure for m_tblog_size_record
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_size_record`;
CREATE TABLE `m_tblog_size_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sLogName` varchar(255) NOT NULL,
  `sImportSize` bigint(32) NOT NULL DEFAULT '0',
  `iTime` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `log_name` (`sLogName`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tblog_sys_admin
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_sys_admin`;
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

-- ----------------------------
-- Table structure for m_tblog_sys_backup
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_sys_backup`;
CREATE TABLE `m_tblog_sys_backup` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iUserId` varchar(50) NOT NULL COMMENT '用户id',
  `iLoginTime` int(11) NOT NULL COMMENT '登录时间',
  `sIp` varchar(64) DEFAULT NULL COMMENT '操作IP',
  `sStatus` tinyint(2) NOT NULL COMMENT '状态',
  `sContent` varchar(255) DEFAULT NULL COMMENT '日志内容',
  PRIMARY KEY (`id`),
  KEY `I_iLoginTime` (`iLoginTime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='恢复与备份日志';

-- ----------------------------
-- Table structure for m_tblog_sys_reboot
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_sys_reboot`;
CREATE TABLE `m_tblog_sys_reboot` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iUserId` varchar(50) NOT NULL COMMENT '用户id',
  `iLoginTime` int(11) NOT NULL COMMENT '登录时间',
  `sIp` varchar(64) DEFAULT NULL COMMENT '操作IP',
  `sStatus` tinyint(2) NOT NULL COMMENT '状态',
  `sContent` varchar(255) DEFAULT NULL COMMENT '日志内容',
  PRIMARY KEY (`id`),
  KEY `I_iLoginTime` (`iLoginTime`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='重启与关机日志';

-- ----------------------------
-- Table structure for m_tblog_sys_resource
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_sys_resource`;
CREATE TABLE `m_tblog_sys_resource` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '登录时间',
  `sSubject` varchar(128) DEFAULT NULL COMMENT '告警项',
  `sContent` varchar(255) DEFAULT NULL COMMENT '描述',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='重启与关机日志';

-- ----------------------------
-- Table structure for m_tblog_url_visit
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_url_visit`;
CREATE TABLE `m_tblog_url_visit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(100) NOT NULL COMMENT '时间',
  `sUrl` varchar(512) NOT NULL COMMENT 'url地址',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sWebType` varchar(64) DEFAULT NULL COMMENT '网站类型',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sAction` tinyint(2) DEFAULT NULL COMMENT '动作',
  PRIMARY KEY (`id`),
  KEY `I_iTime` (`iTime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='url访问日志';

-- ----------------------------
-- Table structure for m_tblog_webapp_record
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_webapp_record`;
CREATE TABLE `m_tblog_webapp_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sEventName` varchar(128) DEFAULT NULL COMMENT '事件名称',
  `sSeverity` varchar(50) DEFAULT NULL,
  `sBugType` varchar(64) DEFAULT NULL COMMENT '漏洞类型',
  `iCount` bigint(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sEventName` (`sEventName`,`sSeverity`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tblog_webapplication
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_webapplication`;
CREATE TABLE `m_tblog_webapplication` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sEventName` varchar(128) DEFAULT NULL COMMENT '事件名称',
  `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
  `sBugType` varchar(64) DEFAULT NULL COMMENT '漏洞类型',
  `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sStatus` varchar(10) DEFAULT NULL COMMENT '状态',
  `sSeverity` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `iTime` (`iTime`,`sEventName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='web应用防御日志';

-- ----------------------------
-- Table structure for m_tblog_wifi_audit
-- ----------------------------
DROP TABLE IF EXISTS `m_tblog_wifi_audit`;
CREATE TABLE `m_tblog_wifi_audit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) NOT NULL COMMENT '时间',
  `sShareHost` varchar(128) NOT NULL COMMENT '共享主机',
  `sTerminal` varchar(512) DEFAULT NULL COMMENT '共享上网主机',
  `sTableName` varchar(32) NOT NULL COMMENT '表名',
  PRIMARY KEY (`id`),
  KEY `I_iTimeShareHost` (`iTime`,`sShareHost`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='共享上网日志';

-- ----------------------------
-- Table structure for m_tbloginlog
-- ----------------------------
DROP TABLE IF EXISTS `m_tbloginlog`;
CREATE TABLE `m_tbloginlog` (
  `iloginLogId` bigint(20) NOT NULL AUTO_INCREMENT,
  `iUserId` varchar(50) NOT NULL,
  `iLoginTime` int(11) NOT NULL,
  `sIp` varchar(64) DEFAULT NULL,
  `sStatus` tinyint(2) NOT NULL,
  `sContent` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`iloginLogId`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tblogtable
-- ----------------------------
DROP TABLE IF EXISTS `m_tblogtable`;
CREATE TABLE `m_tblogtable` (
  `iId` bigint(20) NOT NULL AUTO_INCREMENT,
  `iLogtablename` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `iLogtablestate` varchar(2) CHARACTER SET utf8 DEFAULT '0',
  PRIMARY KEY (`iId`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Table structure for m_tboperatelog
-- ----------------------------
DROP TABLE IF EXISTS `m_tboperatelog`;
CREATE TABLE `m_tboperatelog` (
  `iLogId` bigint(20) NOT NULL AUTO_INCREMENT,
  `iDateTime` int(11) NOT NULL,
  `sIp` varchar(64) NOT NULL,
  `sOperateUser` varchar(50) NOT NULL,
  `sRs` varchar(200) NOT NULL,
  `sContent` varchar(255) NOT NULL,
  `sOperateAction` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`iLogId`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tbprotected_log
-- ----------------------------
DROP TABLE IF EXISTS `m_tbprotected_log`;
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
  `sDetail` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='防护日志';

-- ----------------------------
-- Table structure for m_tbrevcamera_log
-- ----------------------------
DROP TABLE IF EXISTS `m_tbrevcamera_log`;
CREATE TABLE `m_tbrevcamera_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `iTime` int(11) DEFAULT NULL COMMENT '时间',
  `sTrigerReason` varchar(512) DEFAULT NULL COMMENT '触发原因',
  `sTargetAddr` varchar(64) DEFAULT NULL COMMENT '目标地址',
  `sHostType` varchar(256) DEFAULT NULL COMMENT '主机类型',
  `sDistance` varchar(64) DEFAULT NULL COMMENT '距离',
  `sTimeDelay` varchar(64) DEFAULT NULL COMMENT '时延',
  `sDetail` text COMMENT '详细操作',
  `sFileName` varchar(512) DEFAULT NULL COMMENT '文件名',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 CHECKSUM=1 COMMENT='拍照日志';

-- ----------------------------
-- Table structure for m_tbstatistics
-- ----------------------------
DROP TABLE IF EXISTS `m_tbstatistics`;
CREATE TABLE `m_tbstatistics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sName` varchar(128) DEFAULT NULL COMMENT '名称',
  `sValue` text COMMENT '值',
  `sMark` varchar(512) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `i_name` (`sName`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='统计数据表';

-- ----------------------------
-- Table structure for m_tbsystem_update_log
-- ----------------------------
DROP TABLE IF EXISTS `m_tbsystem_update_log`;
CREATE TABLE `m_tbsystem_update_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sVersion` varchar(128) DEFAULT NULL COMMENT '升级版本',
  `sDescription` varchar(512) DEFAULT NULL COMMENT '描述',
  `iTime` int(11) DEFAULT NULL COMMENT '升级时间',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tbwebapplication_lib
-- ----------------------------
DROP TABLE IF EXISTS `m_tbwebapplication_lib`;
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
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='web应用防护规则库';





