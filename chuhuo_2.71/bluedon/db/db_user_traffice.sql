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
  `sAddress` varchar(512) DEFAULT NULL COMMENT '��ַ',
  `sIPV` varchar(32) DEFAULT NULL COMMENT '��ַ���ͣ�ipv4��ipv6',
  `sNetmask` varchar(255) DEFAULT NULL COMMENT '����λ��',
  `sAddtype` varchar(255) DEFAULT NULL COMMENT '��ַ���ͣ�1����ip��2��ip��',
  `sMark` varchar(255) DEFAULT NULL COMMENT '��ע',
  `sInserttime` varchar(12) DEFAULT NULL,
  `sUpdatetime` varchar(12) DEFAULT NULL,
  `IpgroupId` int(11) DEFAULT NULL COMMENT '�û���ID',
  `sIPJson` varchar(255) DEFAULT NULL COMMENT '����ip������,�����Ӧ��jsonֵ.''iprange'':ip����;''ipmaskrange_str'': ʮ����ip����(1.1.1.0/255.255.255.0);''ipmaskrange_int'': ������ip����(1.1.1.0/24);''ipmaskalone_str'':ʮ����ip;''ipmaskalone_int'':������ip',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='��ַ����-��ַ�б�';

-- ----------------------------
-- Table structure for m_tbaddressgroup_scm
-- ----------------------------
DROP TABLE IF EXISTS `m_tbaddressgroup_scm`;
CREATE TABLE `m_tbaddressgroup_scm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sGroupName` varchar(32) DEFAULT NULL COMMENT '����',
  `HideID` varchar(128) DEFAULT NULL COMMENT 'д��iptables�õ���id',
  `sIP` varchar(128) DEFAULT NULL COMMENT 'IP��Ա',
  `sMark` varchar(32) DEFAULT NULL COMMENT '��ע',
  `sGroupIPV` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='��ַ����-��';

-- ----------------------------
-- Table structure for m_tbSearitystrate_scm
-- ----------------------------
DROP TABLE IF EXISTS `m_tbSearitystrate_scm`;
CREATE TABLE `m_tbSearitystrate_scm` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `sStrategyName` varchar(255) DEFAULT NULL COMMENT '��������',
  `sInputPort` varchar(64) DEFAULT NULL COMMENT '���',
  `sOutPort` varchar(64) DEFAULT NULL COMMENT '����',
  `sSourceValue` varchar(255) DEFAULT NULL COMMENT 'Դ��ַ',
  `iSourceType` tinyint(2) DEFAULT NULL COMMENT 'Դip��ip�飬1ΪIP/2ΪIP��',
  `sTargetValue` varchar(255) DEFAULT NULL COMMENT 'Ŀ�ĵ�ַ',
  `iTargetIPType` tinyint(2) DEFAULT NULL COMMENT 'Ŀ��IP��IP�飬1ΪIP��2Ϊ��',
  `sProtocol` varchar(64) DEFAULT NULL COMMENT 'Э��',
  `sSourcePort` int(11) DEFAULT NULL COMMENT 'Դ�˿�',
  `sTargetPort` int(11) DEFAULT NULL COMMENT 'Ŀ�Ķ˿�',
  `iEffectiveTime` int(11) DEFAULT NULL COMMENT '��Чʱ��',
  `iEffectiveTimeType` tinyint(2) DEFAULT NULL COMMENT '��Чʱ�����ͣ�1Ϊ����ʱ�䣬2Ϊѭ��ʱ��',
  `sMark` varchar(255) DEFAULT NULL COMMENT '��ע',
  `sAppName` varchar(255) DEFAULT NULL COMMENT 'Ӧ������',
  `iAppID` int(11) DEFAULT NULL COMMENT 'Ӧ��id',
  `iAction` tinyint(2) NOT NULL COMMENT '������1����2�ܾ�',
  `iLog` tinyint(2) NOT NULL COMMENT '�Ƿ��¼��־',
  `iSort` int(11) DEFAULT NULL COMMENT '�����',
  `iStatus` tinyint(2) NOT NULL COMMENT '״̬',
  `iOneway` tinyint(2) DEFAULT '0' COMMENT '����0��û��ѡ��1����ѡ��',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for m_tbtimeplan_loop_scm
-- ----------------------------
DROP TABLE IF EXISTS `m_tbtimeplan_loop_scm`;
CREATE TABLE `m_tbtimeplan_loop_scm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sPlanName` varchar(256) DEFAULT NULL COMMENT '�ƻ�����',
  `iMondayOn` tinyint(2) DEFAULT NULL COMMENT 'ʹ����һʱ���',
  `sMonday` varchar(512) DEFAULT NULL COMMENT '��һ',
  `iTuesdayOn` tinyint(2) DEFAULT NULL COMMENT 'ʹ���ܶ�ʱ���',
  `sTuesday` varchar(512) DEFAULT NULL COMMENT '�ܶ�',
  `iWednesdayOn` tinyint(2) DEFAULT NULL COMMENT 'ʹ������ʱ���',
  `sWednesday` varchar(512) DEFAULT NULL COMMENT '����',
  `iThursdayOn` tinyint(2) DEFAULT NULL COMMENT 'ʹ������ʱ���',
  `sThursday` varchar(512) DEFAULT NULL COMMENT '����',
  `iFridayOn` tinyint(2) DEFAULT NULL COMMENT 'ʹ������ʱ���',
  `sFriday` varchar(512) DEFAULT NULL COMMENT '����',
  `iSaturdayOn` tinyint(2) DEFAULT NULL COMMENT 'ʹ������ʱ���',
  `sSaturday` varchar(512) DEFAULT NULL COMMENT '����',
  `iSundayOn` tinyint(2) DEFAULT NULL COMMENT 'ʹ������ʱ���',
  `sSunday` varchar(512) DEFAULT NULL COMMENT '����',
  `sMark` varchar(512) DEFAULT NULL COMMENT '��ע',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='ʱ��ƻ�-ѭ���ƻ�';

-- ----------------------------
-- Table structure for m_tbtimeplan_single_scm
-- ----------------------------
DROP TABLE IF EXISTS `m_tbtimeplan_single_scm`;
CREATE TABLE `m_tbtimeplan_single_scm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sPlanName` varchar(64) DEFAULT NULL COMMENT '�ƻ�����',
  `dStartTime` datetime DEFAULT NULL COMMENT '��ʼʱ��',
  `dEndTime` datetime DEFAULT NULL COMMENT '����ʱ��',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='ʱ��ƻ�-���μƻ�';
