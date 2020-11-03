use db_firewall;
/*
Navicat MySQL Data Transfer

Source Server         : 3.99
Source Server Version : 50630
Source Host           : localhost:3306
Source Database       : db_firewall

Target Server Type    : MYSQL
Target Server Version : 50630
File Encoding         : 65001

Date: 2016-07-08 18:20:58
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for m_tbuser_icmp_traffic
-- ----------------------------
DROP TABLE IF EXISTS `m_tbuser_icmp_traffic`;
CREATE TABLE `m_tbuser_icmp_traffic` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sUserIP` varchar(64) NOT NULL,
  `sProtocol` varchar(10) NOT NULL,
  `sAppType` varchar(10) NOT NULL,
  `sTraffic` text NOT NULL,
  `sLastUpdate` varchar(32) NOT NULL,
  `iTime` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tbuser_tcp_traffic
-- ----------------------------
DROP TABLE IF EXISTS `m_tbuser_tcp_traffic`;
CREATE TABLE `m_tbuser_tcp_traffic` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sUserIP` varchar(64) NOT NULL,
  `sProtocol` varchar(10) NOT NULL,
  `sAppType` varchar(10) NOT NULL,
  `sTraffic` text NOT NULL,
  `sLastUpdate` varchar(32) NOT NULL,
  `iTime` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tbuser_udp_traffic
-- ----------------------------
DROP TABLE IF EXISTS `m_tbuser_udp_traffic`;
CREATE TABLE `m_tbuser_udp_traffic` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sUserIP` varchar(64) NOT NULL,
  `sProtocol` varchar(10) NOT NULL,
  `sAppType` varchar(10) NOT NULL,
  `sTraffic` text NOT NULL,
  `sLastUpdate` varchar(32) NOT NULL,
  `iTime` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for m_tbaddress_list_scm
-- ----------------------------
DROP TABLE IF EXISTS `m_tbaddress_list_scm`;
CREATE TABLE `m_tbaddress_list_scm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sAddressname` varchar(255) DEFAULT NULL,
  `sAddress` varchar(512) DEFAULT NULL COMMENT '地址',
  `sIPV` varchar(32) DEFAULT NULL COMMENT '地址类型，ipv4，ipv6',
  `sNetmask` varchar(255) DEFAULT NULL COMMENT '掩码位数',
  `sAddtype` varchar(255) DEFAULT NULL COMMENT '地址类型，1：单ip，2：ip段',
  `sMark` varchar(255) DEFAULT NULL COMMENT '备注',
  `sInserttime` varchar(12) DEFAULT NULL,
  `sUpdatetime` varchar(12) DEFAULT NULL,
  `IpgroupId` int(11) DEFAULT NULL COMMENT '用户组ID',
  `sIPJson` varchar(255) DEFAULT NULL COMMENT '根据ip的类型,存放相应的json值.''iprange'':ip区间;''ipmaskrange_str'': 十进制ip掩码(1.1.1.0/255.255.255.0);''ipmaskrange_int'': 二进制ip掩码(1.1.1.0/24);''ipmaskalone_str'':十进制ip;''ipmaskalone_int'':二进制ip',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='地址管理-地址列表';

-- ----------------------------
-- Table structure for m_tbaddressgroup_scm
-- ----------------------------
DROP TABLE IF EXISTS `m_tbaddressgroup_scm`;
CREATE TABLE `m_tbaddressgroup_scm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sGroupName` varchar(32) DEFAULT NULL COMMENT '组名',
  `HideID` varchar(128) DEFAULT NULL COMMENT '写入iptables用到的id',
  `sIP` varchar(128) DEFAULT NULL COMMENT 'IP成员',
  `sMark` varchar(32) DEFAULT NULL COMMENT '备注',
  `sGroupIPV` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='地址管理-组';

-- ----------------------------
-- Table structure for m_tbSearitystrate_scm
-- ----------------------------
DROP TABLE IF EXISTS `m_tbSearitystrate_scm`;
CREATE TABLE `m_tbSearitystrate_scm` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `sStrategyName` varchar(255) DEFAULT NULL COMMENT '策略名称',
  `sInputPort` varchar(64) DEFAULT NULL COMMENT '入口',
  `sOutPort` varchar(64) DEFAULT NULL COMMENT '出口',
  `sSourceValue` varchar(255) DEFAULT NULL COMMENT '源地址',
  `iSourceType` tinyint(2) DEFAULT NULL COMMENT '源ip或ip组，1为IP/2为IP组',
  `sTargetValue` varchar(255) DEFAULT NULL COMMENT '目的地址',
  `iTargetIPType` tinyint(2) DEFAULT NULL COMMENT '目的IP或IP组，1为IP，2为组',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
  `sSourcePort` int(11) DEFAULT NULL COMMENT '源端口',
  `sTargetPort` int(11) DEFAULT NULL COMMENT '目的端口',
  `iEffectiveTime` int(11) DEFAULT NULL COMMENT '生效时间',
  `iEffectiveTimeType` tinyint(2) DEFAULT NULL COMMENT '生效时间类型，1为单次时间，2为循环时间',
  `sMark` varchar(255) DEFAULT NULL COMMENT '备注',
  `sAppName` varchar(255) DEFAULT NULL COMMENT '应用名称',
  `iAppID` int(11) DEFAULT NULL COMMENT '应用id',
  `iAction` tinyint(2) NOT NULL COMMENT '动作，1允许，2拒绝',
  `iLog` tinyint(2) NOT NULL COMMENT '是否记录日志',
  `iSort` int(11) DEFAULT NULL COMMENT '排序号',
  `iStatus` tinyint(2) NOT NULL COMMENT '状态',
  `iOneway` tinyint(2) DEFAULT '0' COMMENT '单向（0：没勾选，1：勾选）',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tbtimeplan_loop_scm
-- ----------------------------
DROP TABLE IF EXISTS `m_tbtimeplan_loop_scm`;
CREATE TABLE `m_tbtimeplan_loop_scm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sPlanName` varchar(256) DEFAULT NULL COMMENT '计划名称',
  `iMondayOn` tinyint(2) DEFAULT NULL COMMENT '使用周一时间段',
  `sMonday` varchar(512) DEFAULT NULL COMMENT '周一',
  `iTuesdayOn` tinyint(2) DEFAULT NULL COMMENT '使用周二时间段',
  `sTuesday` varchar(512) DEFAULT NULL COMMENT '周二',
  `iWednesdayOn` tinyint(2) DEFAULT NULL COMMENT '使用周三时间段',
  `sWednesday` varchar(512) DEFAULT NULL COMMENT '周三',
  `iThursdayOn` tinyint(2) DEFAULT NULL COMMENT '使用周四时间段',
  `sThursday` varchar(512) DEFAULT NULL COMMENT '周四',
  `iFridayOn` tinyint(2) DEFAULT NULL COMMENT '使用周五时间段',
  `sFriday` varchar(512) DEFAULT NULL COMMENT '周五',
  `iSaturdayOn` tinyint(2) DEFAULT NULL COMMENT '使用周六时间段',
  `sSaturday` varchar(512) DEFAULT NULL COMMENT '周六',
  `iSundayOn` tinyint(2) DEFAULT NULL COMMENT '使用周日时间段',
  `sSunday` varchar(512) DEFAULT NULL COMMENT '周日',
  `sMark` varchar(512) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='时间计划-循环计划';

-- ----------------------------
-- Table structure for m_tbtimeplan_single_scm
-- ----------------------------
DROP TABLE IF EXISTS `m_tbtimeplan_single_scm`;
CREATE TABLE `m_tbtimeplan_single_scm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sPlanName` varchar(64) DEFAULT NULL COMMENT '计划名称',
  `dStartTime` datetime DEFAULT NULL COMMENT '开始时间',
  `dEndTime` datetime DEFAULT NULL COMMENT '结束时间',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='时间计划-单次计划';
