USE waf;
-- MySQL dump 10.13  Distrib 5.6.30, for Linux (x86_64)
--
-- Host: localhost    Database: waf
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
-- Table structure for table `config`
--

DROP TABLE IF EXISTS `config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `config` (
  `symbol` char(255) NOT NULL,
  `desc` char(255) DEFAULT NULL,
  `field_desc` text,
  `json` text,
  PRIMARY KEY (`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `config`
--

LOCK TABLES `config` WRITE;
/*!40000 ALTER TABLE `config` DISABLE KEYS */;
INSERT INTO `config` VALUES ('FileExtension',NULL,NULL,'{\"extension\":\"1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|50|51\",\"extensionHidden\":\"\"}');
INSERT INTO `config` VALUES ('KeyWordAlert',NULL,NULL,'{\"max_file_size\":null,\"urls\":null,\"exts\":null,\"words\":null,\"alert_config\":null,\"status\":null,\"is_block\":null}');
INSERT INTO `config` VALUES ('SensitiveWord','敏感词告警','status:是否开启，0-关闭，1-开启<br>\r\nurls	需要防护的url，留空则所有URL，多个则用‘|’分开,如 “/test|/test2”<br>\r\nexts:需要防护的文件扩展名，留空则为所有文件，多种类型则用‘|’隔开，如 “jgp|tar”<br>\r\nwords:敏感词，多个敏感词用‘|’隔开，如”法轮功|赌博”<br>\r\ncontent_size:需要处理的最大文件大小，超过这个阀值，则跳过处理<br>\r\nis_block:是否阻断，1-阻断，0-不阻断，默认0<br>\r\nalert_setting:告警设置，json格式，interval 邮件发送间隔（单位秒）\r\n{\"type\":\"email\",\"interval\":3600,\"email\":{\"receiver\":\"test@126.com\"}}<br>','{\"max_file_size\":\"22\",\"exts\":\"33\",\"urls\":\"xxx\",\"words\":\"vvv\",\"alert_config\":\"mmm\",\"status\":\"1\",\"is_block\":\"zzz\"}');
INSERT INTO `config` VALUES ('SysLoginConfig','登录配置','max_error:登录尝试次数限制<br>\r\nlock_time:登录错误锁定时间(分钟)<br>\r\nmax_timeout:登录超时时间(分钟)<br>\r\nsystem_default_language:系统默认语言<br>','{\"single_user_login_count_limit\":\"20\",\"max_error\":\"4\",\"lock_time\":\"1\",\"max_timeout\":\"1440\",\"system_default_language\":\"zh-CN\"}');
/*!40000 ALTER TABLE `config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fetch_task`
--

DROP TABLE IF EXISTS `fetch_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fetch_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) DEFAULT NULL COMMENT '标题',
  `host` varchar(30) DEFAULT NULL COMMENT '主机',
  `db` varchar(30) DEFAULT NULL COMMENT '数据库',
  `user` varchar(30) DEFAULT NULL COMMENT '用户',
  `pwd` varchar(30) DEFAULT NULL COMMENT '密码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='fetch任务';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fetch_task`
--

LOCK TABLES `fetch_task` WRITE;
/*!40000 ALTER TABLE `fetch_task` DISABLE KEYS */;
/*!40000 ALTER TABLE `fetch_task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fetch_task_item`
--

DROP TABLE IF EXISTS `fetch_task_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fetch_task_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` int(11) DEFAULT NULL COMMENT '任务ID',
  `parent_id` int(11) DEFAULT '0' COMMENT '任务父ID',
  `title` varchar(100) DEFAULT NULL COMMENT '标题',
  `tb` varchar(100) DEFAULT '' COMMENT '表名',
  `tb_create` text COMMENT '建表SQL',
  `field` text COMMENT '字段',
  `field_global_var` text COMMENT '全局变量',
  `field_attribute_label` text COMMENT '字段标签',
  `field_attribute_labels_config` text,
  `field_rules` text COMMENT '字段规则',
  `field_search` text COMMENT ' 字段搜索配置',
  `field_search_box` text COMMENT '字段搜索框',
  `field_table` text COMMENT '显示字段列',
  `field_edit` text COMMENT '字段编辑样式',
  `field_data` text COMMENT '字段数据匹配设置',
  PRIMARY KEY (`id`),
  KEY `task_id` (`task_id`),
  KEY `parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='fetch任务项目';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fetch_task_item`
--

LOCK TABLES `fetch_task_item` WRITE;
/*!40000 ALTER TABLE `fetch_task_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `fetch_task_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `null_table`
--

DROP TABLE IF EXISTS `null_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `null_table` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `null_table`
--

LOCK TABLES `null_table` WRITE;
/*!40000 ALTER TABLE `null_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `null_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rule_custom_defend_policy`
--

DROP TABLE IF EXISTS `rule_custom_defend_policy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rule_custom_defend_policy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` char(100) NOT NULL DEFAULT '' COMMENT '名称',
  `rule` int(11) NOT NULL DEFAULT '0' COMMENT '规则模板ID',
  `status` char(1) NOT NULL DEFAULT '1' COMMENT '启用?',
  `source_ip` char(255) NOT NULL DEFAULT '' COMMENT '来源IP',
  `destination_ip` char(255) NOT NULL DEFAULT '' COMMENT '目标IP',
  `destination_url` char(255) NOT NULL DEFAULT '' COMMENT '目的URL',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `name` (`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rule_custom_defend_policy`
--

LOCK TABLES `rule_custom_defend_policy` WRITE;
/*!40000 ALTER TABLE `rule_custom_defend_policy` DISABLE KEYS */;
/*!40000 ALTER TABLE `rule_custom_defend_policy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_language_en_us`
--

DROP TABLE IF EXISTS `sys_language_en_us`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_language_en_us` (
  `id` int(11) NOT NULL COMMENT '主键',
  `title` text COMMENT '标题',
  PRIMARY KEY (`id`),
  CONSTRAINT `id_fk` FOREIGN KEY (`id`) REFERENCES `sys_language_source` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_language_en_us`
--

LOCK TABLES `sys_language_en_us` WRITE;
/*!40000 ALTER TABLE `sys_language_en_us` DISABLE KEYS */;
INSERT INTO `sys_language_en_us` VALUES (1,'Update');
INSERT INTO `sys_language_en_us` VALUES (2,'Cache management');
INSERT INTO `sys_language_en_us` VALUES (3,'Add');
INSERT INTO `sys_language_en_us` VALUES (4,'System monitoring');
INSERT INTO `sys_language_en_us` VALUES (5,'Check');
INSERT INTO `sys_language_en_us` VALUES (6,'General information');
INSERT INTO `sys_language_en_us` VALUES (7,'Network traffic monitoring');
INSERT INTO `sys_language_en_us` VALUES (8,'Device load monitoring');
INSERT INTO `sys_language_en_us` VALUES (9,'Delete');
INSERT INTO `sys_language_en_us` VALUES (10,'WEB application monitoring');
INSERT INTO `sys_language_en_us` VALUES (12,'Modify');
INSERT INTO `sys_language_en_us` VALUES (15,'Upload file');
INSERT INTO `sys_language_en_us` VALUES (18,'Modify information');
INSERT INTO `sys_language_en_us` VALUES (19,'Edit');
INSERT INTO `sys_language_en_us` VALUES (22,'Install library');
INSERT INTO `sys_language_en_us` VALUES (23,'Search');
INSERT INTO `sys_language_en_us` VALUES (24,'Configuration table');
INSERT INTO `sys_language_en_us` VALUES (25,'Port configuration');
INSERT INTO `sys_language_en_us` VALUES (26,'Port mirroring');
INSERT INTO `sys_language_en_us` VALUES (28,'Virtual Wire');
INSERT INTO `sys_language_en_us` VALUES (30,'Dial device');
INSERT INTO `sys_language_en_us` VALUES (31,'Aggregate port');
INSERT INTO `sys_language_en_us` VALUES (32,'VLAN device');
INSERT INTO `sys_language_en_us` VALUES (33,'DHCP');
INSERT INTO `sys_language_en_us` VALUES (34,'DNS setting');
INSERT INTO `sys_language_en_us` VALUES (35,'IPV6 tunnel');
INSERT INTO `sys_language_en_us` VALUES (36,'NAT64');
INSERT INTO `sys_language_en_us` VALUES (37,'ECMP');
INSERT INTO `sys_language_en_us` VALUES (38,'Static routing');
INSERT INTO `sys_language_en_us` VALUES (39,'WEB site traffic');
INSERT INTO `sys_language_en_us` VALUES (40,'Policy routing');
INSERT INTO `sys_language_en_us` VALUES (41,'Number of new connections and transactions processing');
INSERT INTO `sys_language_en_us` VALUES (42,'ISP routing');
INSERT INTO `sys_language_en_us` VALUES (43,'Concurrent connections');
INSERT INTO `sys_language_en_us` VALUES (44,'Dynamic routing');
INSERT INTO `sys_language_en_us` VALUES (45,'IP/IP group');
INSERT INTO `sys_language_en_us` VALUES (46,'ISP address');
INSERT INTO `sys_language_en_us` VALUES (47,'Service/group');
INSERT INTO `sys_language_en_us` VALUES (48,'URL type group');
INSERT INTO `sys_language_en_us` VALUES (49,'File type group');
INSERT INTO `sys_language_en_us` VALUES (50,'Time plan');
INSERT INTO `sys_language_en_us` VALUES (51,'User defined IPS rule base');
INSERT INTO `sys_language_en_us` VALUES (52,'WEB application protection rule base');
INSERT INTO `sys_language_en_us` VALUES (53,'NAT');
INSERT INTO `sys_language_en_us` VALUES (54,'Connection quantity control');
INSERT INTO `sys_language_en_us` VALUES (55,'DOS/DDOS prevention');
INSERT INTO `sys_language_en_us` VALUES (56,'Session management');
INSERT INTO `sys_language_en_us` VALUES (57,'Session control');
INSERT INTO `sys_language_en_us` VALUES (58,'Connection ranking list');
INSERT INTO `sys_language_en_us` VALUES (59,'Session status');
INSERT INTO `sys_language_en_us` VALUES (60,'IP-MAC binding configuration');
INSERT INTO `sys_language_en_us` VALUES (61,'Collaboration');
INSERT INTO `sys_language_en_us` VALUES (62,'URL filtering');
INSERT INTO `sys_language_en_us` VALUES (63,'URL filtering policy');
INSERT INTO `sys_language_en_us` VALUES (64,'URL blacklist');
INSERT INTO `sys_language_en_us` VALUES (65,'URL white list');
INSERT INTO `sys_language_en_us` VALUES (66,'Configuration');
INSERT INTO `sys_language_en_us` VALUES (67,'WEB application protection');
INSERT INTO `sys_language_en_us` VALUES (68,'Virus prevention');
INSERT INTO `sys_language_en_us` VALUES (69,'Update 2');
INSERT INTO `sys_language_en_us` VALUES (70,'Basic configuration');
INSERT INTO `sys_language_en_us` VALUES (71,'Anti-virus policy setting');
INSERT INTO `sys_language_en_us` VALUES (72,'Information leakage prevention');
INSERT INTO `sys_language_en_us` VALUES (73,'Keywords filtering');
INSERT INTO `sys_language_en_us` VALUES (75,'File filtering');
INSERT INTO `sys_language_en_us` VALUES (76,'Title');
INSERT INTO `sys_language_en_us` VALUES (78,'SSL VPN');
INSERT INTO `sys_language_en_us` VALUES (79,'Service management');
INSERT INTO `sys_language_en_us` VALUES (80,'User configuration');
INSERT INTO `sys_language_en_us` VALUES (81,'IPSEC VPN');
INSERT INTO `sys_language_en_us` VALUES (82,'Local subnet');
INSERT INTO `sys_language_en_us` VALUES (83,'Branch connection');
INSERT INTO `sys_language_en_us` VALUES (84,'IPSEC monitoring management');
INSERT INTO `sys_language_en_us` VALUES (85,'L2TP VPN');
INSERT INTO `sys_language_en_us` VALUES (86,'Download');
INSERT INTO `sys_language_en_us` VALUES (87,'Monitoring management');
INSERT INTO `sys_language_en_us` VALUES (88,'Homepage customization saved');
INSERT INTO `sys_language_en_us` VALUES (89,'Virtual IP pool');
INSERT INTO `sys_language_en_us` VALUES (90,'Export');
INSERT INTO `sys_language_en_us` VALUES (91,'NAT traversal');
INSERT INTO `sys_language_en_us` VALUES (92,'Website access analysis(current month)');
INSERT INTO `sys_language_en_us` VALUES (93,'Center node');
INSERT INTO `sys_language_en_us` VALUES (94,'Edge node');
INSERT INTO `sys_language_en_us` VALUES (95,'Rescan');
INSERT INTO `sys_language_en_us` VALUES (96,'GRE tunnel');
INSERT INTO `sys_language_en_us` VALUES (97,'Stop');
INSERT INTO `sys_language_en_us` VALUES (98,'Virtual wire');
INSERT INTO `sys_language_en_us` VALUES (99,'Channel configuration');
INSERT INTO `sys_language_en_us` VALUES (100,'Adaptive policy');
INSERT INTO `sys_language_en_us` VALUES (101,'Comprehensive analysis(by day)');
INSERT INTO `sys_language_en_us` VALUES (102,'Honey pot');
INSERT INTO `sys_language_en_us` VALUES (103,'Comprehensive analysis(by month)');
INSERT INTO `sys_language_en_us` VALUES (104,'Reverse photographing');
INSERT INTO `sys_language_en_us` VALUES (105,'Anti-scan');
INSERT INTO `sys_language_en_us` VALUES (106,'Add blacklist and whitelist');
INSERT INTO `sys_language_en_us` VALUES (107,'Report statistics');
INSERT INTO `sys_language_en_us` VALUES (108,'Administrator\'s account');
INSERT INTO `sys_language_en_us` VALUES (109,'System configuration');
INSERT INTO `sys_language_en_us` VALUES (110,'System maintenance');
INSERT INTO `sys_language_en_us` VALUES (111,'Help and support');
INSERT INTO `sys_language_en_us` VALUES (112,'High availability');
INSERT INTO `sys_language_en_us` VALUES (113,'Emergency support');
INSERT INTO `sys_language_en_us` VALUES (115,'Attack report preview');
INSERT INTO `sys_language_en_us` VALUES (116,'Configuration management');
INSERT INTO `sys_language_en_us` VALUES (117,'Basic parameter setting');
INSERT INTO `sys_language_en_us` VALUES (118,'Site group management');
INSERT INTO `sys_language_en_us` VALUES (122,'Access traffic report preview');
INSERT INTO `sys_language_en_us` VALUES (129,'Access control configuration switch');
INSERT INTO `sys_language_en_us` VALUES (133,'HA port and parameter configuration');
INSERT INTO `sys_language_en_us` VALUES (134,'Notice configuration');
INSERT INTO `sys_language_en_us` VALUES (135,'Rule upgrading');
INSERT INTO `sys_language_en_us` VALUES (136,'Alert setting');
INSERT INTO `sys_language_en_us` VALUES (137,'SSH switch');
INSERT INTO `sys_language_en_us` VALUES (140,'System upgrading');
INSERT INTO `sys_language_en_us` VALUES (141,'Attack report');
INSERT INTO `sys_language_en_us` VALUES (142,'Access traffic report');
INSERT INTO `sys_language_en_us` VALUES (143,'Instant report');
INSERT INTO `sys_language_en_us` VALUES (144,'Report management');
INSERT INTO `sys_language_en_us` VALUES (145,'Rule configuration');
INSERT INTO `sys_language_en_us` VALUES (146,'Advanced setting');
INSERT INTO `sys_language_en_us` VALUES (147,'Self-learning');
INSERT INTO `sys_language_en_us` VALUES (148,'Dynamic modeling');
INSERT INTO `sys_language_en_us` VALUES (149,'Illegal external connection');
INSERT INTO `sys_language_en_us` VALUES (150,'DDOS prevention');
INSERT INTO `sys_language_en_us` VALUES (151,'Web page defacement prevention');
INSERT INTO `sys_language_en_us` VALUES (152,'Built-in rule');
INSERT INTO `sys_language_en_us` VALUES (153,'User defined rule');
INSERT INTO `sys_language_en_us` VALUES (154,'Rule template setting');
INSERT INTO `sys_language_en_us` VALUES (155,'Access control');
INSERT INTO `sys_language_en_us` VALUES (156,'HTTP anti-overflow setting');
INSERT INTO `sys_language_en_us` VALUES (157,'HTTP protocol version filtering');
INSERT INTO `sys_language_en_us` VALUES (158,'HTTP header field setting');
INSERT INTO `sys_language_en_us` VALUES (159,'Filename extention filtering');
INSERT INTO `sys_language_en_us` VALUES (160,'Sensitive word filtering setting');
INSERT INTO `sys_language_en_us` VALUES (161,'Anti hotlink setting');
INSERT INTO `sys_language_en_us` VALUES (162,'Anti crawler setting');
INSERT INTO `sys_language_en_us` VALUES (163,'Anti false positive setting');
INSERT INTO `sys_language_en_us` VALUES (164,'Self-learning setting');
INSERT INTO `sys_language_en_us` VALUES (165,'Self-learning access white list');
INSERT INTO `sys_language_en_us` VALUES (166,'Self-learning result');
INSERT INTO `sys_language_en_us` VALUES (167,'Illegal external connection detection');
INSERT INTO `sys_language_en_us` VALUES (168,'Illegal external connection setting');
INSERT INTO `sys_language_en_us` VALUES (169,'Intelligent blocking  setting');
INSERT INTO `sys_language_en_us` VALUES (170,'DDOS prevention setting');
INSERT INTO `sys_language_en_us` VALUES (171,'CC prevention setting');
INSERT INTO `sys_language_en_us` VALUES (172,'Availability monitoring');
INSERT INTO `sys_language_en_us` VALUES (173,'Vulnerability scanning');
INSERT INTO `sys_language_en_us` VALUES (174,'Back to page setting');
INSERT INTO `sys_language_en_us` VALUES (175,'Upload');
INSERT INTO `sys_language_en_us` VALUES (176,'Data management');
INSERT INTO `sys_language_en_us` VALUES (177,'Group/user');
INSERT INTO `sys_language_en_us` VALUES (178,'Data management model');
INSERT INTO `sys_language_en_us` VALUES (179,'System');
INSERT INTO `sys_language_en_us` VALUES (180,'Data sheet');
INSERT INTO `sys_language_en_us` VALUES (181,'Network configuration');
INSERT INTO `sys_language_en_us` VALUES (182,'Account management');
INSERT INTO `sys_language_en_us` VALUES (183,'Database');
INSERT INTO `sys_language_en_us` VALUES (184,'Routing management');
INSERT INTO `sys_language_en_us` VALUES (185,'Object definition');
INSERT INTO `sys_language_en_us` VALUES (186,'Login configuration');
INSERT INTO `sys_language_en_us` VALUES (187,'User management');
INSERT INTO `sys_language_en_us` VALUES (188,'VPN');
INSERT INTO `sys_language_en_us` VALUES (189,'Traffic management');
INSERT INTO `sys_language_en_us` VALUES (190,'Intelligent protection');
INSERT INTO `sys_language_en_us` VALUES (191,'Action ID');
INSERT INTO `sys_language_en_us` VALUES (192,'Name');
INSERT INTO `sys_language_en_us` VALUES (193,'Desc');
INSERT INTO `sys_language_en_us` VALUES (194,'ID');
INSERT INTO `sys_language_en_us` VALUES (196,'Time');
INSERT INTO `sys_language_en_us` VALUES (199,'Order');
INSERT INTO `sys_language_en_us` VALUES (200,'Display');
INSERT INTO `sys_language_en_us` VALUES (202,'Title');
INSERT INTO `sys_language_en_us` VALUES (212,'Type');
INSERT INTO `sys_language_en_us` VALUES (218,'IP type');
INSERT INTO `sys_language_en_us` VALUES (219,'IP or IP segment');
INSERT INTO `sys_language_en_us` VALUES (220,'Type');
INSERT INTO `sys_language_en_us` VALUES (221,'Status');
INSERT INTO `sys_language_en_us` VALUES (222,'Priority');
INSERT INTO `sys_language_en_us` VALUES (223,'Severity');
INSERT INTO `sys_language_en_us` VALUES (230,'Host');
INSERT INTO `sys_language_en_us` VALUES (231,'Db');
INSERT INTO `sys_language_en_us` VALUES (232,'User');
INSERT INTO `sys_language_en_us` VALUES (233,'Pwd');
INSERT INTO `sys_language_en_us` VALUES (234,'Task ID');
INSERT INTO `sys_language_en_us` VALUES (235,'Parent ID');
INSERT INTO `sys_language_en_us` VALUES (236,'Tb');
INSERT INTO `sys_language_en_us` VALUES (237,'Tb Create');
INSERT INTO `sys_language_en_us` VALUES (238,'Field');
INSERT INTO `sys_language_en_us` VALUES (239,'Field Global Var');
INSERT INTO `sys_language_en_us` VALUES (240,'Field Attribute Label');
INSERT INTO `sys_language_en_us` VALUES (241,'Field Attribute Labels Config');
INSERT INTO `sys_language_en_us` VALUES (242,'Field Rules');
INSERT INTO `sys_language_en_us` VALUES (243,'Field Search');
INSERT INTO `sys_language_en_us` VALUES (244,'Field Search Box');
INSERT INTO `sys_language_en_us` VALUES (245,'Field Table');
INSERT INTO `sys_language_en_us` VALUES (246,'Field Edit');
INSERT INTO `sys_language_en_us` VALUES (247,'Field Data');
INSERT INTO `sys_language_en_us` VALUES (248,'Is Use');
INSERT INTO `sys_language_en_us` VALUES (249,'Interface');
INSERT INTO `sys_language_en_us` VALUES (250,'Vhid');
INSERT INTO `sys_language_en_us` VALUES (251,'Password');
INSERT INTO `sys_language_en_us` VALUES (252,'State');
INSERT INTO `sys_language_en_us` VALUES (253,'Ip');
INSERT INTO `sys_language_en_us` VALUES (254,'Database Ip');
INSERT INTO `sys_language_en_us` VALUES (255,'Database Port');
INSERT INTO `sys_language_en_us` VALUES (256,'Is Setting');
INSERT INTO `sys_language_en_us` VALUES (257,'Server ID');
INSERT INTO `sys_language_en_us` VALUES (258,'Offset ID');
INSERT INTO `sys_language_en_us` VALUES (259,'Had Sync');
INSERT INTO `sys_language_en_us` VALUES (260,'Bridge');
INSERT INTO `sys_language_en_us` VALUES (261,'Is Port Aggregation');
INSERT INTO `sys_language_en_us` VALUES (262,'Database Sync Status');
INSERT INTO `sys_language_en_us` VALUES (272,'Secname');
INSERT INTO `sys_language_en_us` VALUES (277,'Report name');
INSERT INTO `sys_language_en_us` VALUES (278,'Report type');
INSERT INTO `sys_language_en_us` VALUES (279,'Report introduction');
INSERT INTO `sys_language_en_us` VALUES (280,'Generation time');
INSERT INTO `sys_language_en_us` VALUES (281,'Path');
INSERT INTO `sys_language_en_us` VALUES (282,'Report classification');
INSERT INTO `sys_language_en_us` VALUES (283,'Format');
INSERT INTO `sys_language_en_us` VALUES (284,'Introduction');
INSERT INTO `sys_language_en_us` VALUES (285,'Email notice');
INSERT INTO `sys_language_en_us` VALUES (286,'File format');
INSERT INTO `sys_language_en_us` VALUES (289,'Different');
INSERT INTO `sys_language_en_us` VALUES (293,'Redirect ID');
INSERT INTO `sys_language_en_us` VALUES (294,'Description');
INSERT INTO `sys_language_en_us` VALUES (295,'Link');
INSERT INTO `sys_language_en_us` VALUES (296,'Username');
INSERT INTO `sys_language_en_us` VALUES (297,'Password');
INSERT INTO `sys_language_en_us` VALUES (298,'Affiliated group');
INSERT INTO `sys_language_en_us` VALUES (299,'Available');
INSERT INTO `sys_language_en_us` VALUES (300,'Group ID');
INSERT INTO `sys_language_en_us` VALUES (301,'Sys Menu ID');
INSERT INTO `sys_language_en_us` VALUES (302,'Enable');
INSERT INTO `sys_language_en_us` VALUES (303,'Group');
INSERT INTO `sys_language_en_us` VALUES (304,'Home key ID');
INSERT INTO `sys_language_en_us` VALUES (305,'Configured key name of system');
INSERT INTO `sys_language_en_us` VALUES (306,'Configured key value of system');
INSERT INTO `sys_language_en_us` VALUES (307,'Configured description of system');
INSERT INTO `sys_language_en_us` VALUES (323,'Country Code');
INSERT INTO `sys_language_en_us` VALUES (330,'Referer');
INSERT INTO `sys_language_en_us` VALUES (333,'Url');
INSERT INTO `sys_language_en_us` VALUES (339,'Rulefile');
INSERT INTO `sys_language_en_us` VALUES (341,'Rev');
INSERT INTO `sys_language_en_us` VALUES (343,'Tag');
INSERT INTO `sys_language_en_us` VALUES (344,'Code');
INSERT INTO `sys_language_en_us` VALUES (345,'Province');
INSERT INTO `sys_language_en_us` VALUES (346,'Area');
INSERT INTO `sys_language_en_us` VALUES (347,'En Country');
INSERT INTO `sys_language_en_us` VALUES (348,'Cn Country');
INSERT INTO `sys_language_en_us` VALUES (349,'Continent');
INSERT INTO `sys_language_en_us` VALUES (354,'Binding device list');
INSERT INTO `sys_language_en_us` VALUES (358,'IPV4 address');
INSERT INTO `sys_language_en_us` VALUES (359,'IPV4 mask');
INSERT INTO `sys_language_en_us` VALUES (360,'IPV6 address');
INSERT INTO `sys_language_en_us` VALUES (361,'IPV6 mask');
INSERT INTO `sys_language_en_us` VALUES (364,'Log in');
INSERT INTO `sys_language_en_us` VALUES (365,'Log out');
INSERT INTO `sys_language_en_us` VALUES (366,'Verification code');
INSERT INTO `sys_language_en_us` VALUES (367,'Change another one');
INSERT INTO `sys_language_en_us` VALUES (368,'Close');
INSERT INTO `sys_language_en_us` VALUES (369,'Start time');
INSERT INTO `sys_language_en_us` VALUES (370,'End time');
INSERT INTO `sys_language_en_us` VALUES (371,'Old password');
INSERT INTO `sys_language_en_us` VALUES (372,'New password');
INSERT INTO `sys_language_en_us` VALUES (373,'Submit');
INSERT INTO `sys_language_en_us` VALUES (374,'Reset');
INSERT INTO `sys_language_en_us` VALUES (375,'Refresh');
INSERT INTO `sys_language_en_us` VALUES (376,'Address');
INSERT INTO `sys_language_en_us` VALUES (377,'Second');
INSERT INTO `sys_language_en_us` VALUES (378,'Disable');
INSERT INTO `sys_language_en_us` VALUES (379,'Hide');
INSERT INTO `sys_language_en_us` VALUES (380,'Yes');
INSERT INTO `sys_language_en_us` VALUES (382,'Add');
INSERT INTO `sys_language_en_us` VALUES (383,'Skip to');
INSERT INTO `sys_language_en_us` VALUES (384,'Total');
INSERT INTO `sys_language_en_us` VALUES (385,'Record');
INSERT INTO `sys_language_en_us` VALUES (386,'Page');
INSERT INTO `sys_language_en_us` VALUES (387,'The first page');
INSERT INTO `sys_language_en_us` VALUES (388,'The last page');
INSERT INTO `sys_language_en_us` VALUES (389,'The next page');
INSERT INTO `sys_language_en_us` VALUES (390,'The previous page');
INSERT INTO `sys_language_en_us` VALUES (391,'Number of items on each page');
INSERT INTO `sys_language_en_us` VALUES (392,'Action');
INSERT INTO `sys_language_en_us` VALUES (393,'Upgrade');
INSERT INTO `sys_language_en_us` VALUES (394,'Select file');
INSERT INTO `sys_language_en_us` VALUES (395,'File type');
INSERT INTO `sys_language_en_us` VALUES (396,'File absent');
INSERT INTO `sys_language_en_us` VALUES (397,'Required fields');
INSERT INTO `sys_language_en_us` VALUES (398,'Length');
INSERT INTO `sys_language_en_us` VALUES (399,'Byte');
INSERT INTO `sys_language_en_us` VALUES (400,'Invert selection');
INSERT INTO `sys_language_en_us` VALUES (401,'Every day');
INSERT INTO `sys_language_en_us` VALUES (402,'Every week');
INSERT INTO `sys_language_en_us` VALUES (403,'Every month');
INSERT INTO `sys_language_en_us` VALUES (404,'Restore');
INSERT INTO `sys_language_en_us` VALUES (405,'Note');
INSERT INTO `sys_language_en_us` VALUES (406,'Reminder');
INSERT INTO `sys_language_en_us` VALUES (407,'E-mail');
INSERT INTO `sys_language_en_us` VALUES (408,'Telephone');
INSERT INTO `sys_language_en_us` VALUES (409,'To');
INSERT INTO `sys_language_en_us` VALUES (410,'File name');
INSERT INTO `sys_language_en_us` VALUES (411,'High');
INSERT INTO `sys_language_en_us` VALUES (412,'Low');
INSERT INTO `sys_language_en_us` VALUES (413,'Name');
INSERT INTO `sys_language_en_us` VALUES (414,'User defined');
INSERT INTO `sys_language_en_us` VALUES (415,'Select');
INSERT INTO `sys_language_en_us` VALUES (416,'Only record');
INSERT INTO `sys_language_en_us` VALUES (417,'Allow to access');
INSERT INTO `sys_language_en_us` VALUES (418,'Access denied');
INSERT INTO `sys_language_en_us` VALUES (419,'Close link');
INSERT INTO `sys_language_en_us` VALUES (420,'Continue');
INSERT INTO `sys_language_en_us` VALUES (421,'Destination');
INSERT INTO `sys_language_en_us` VALUES (422,'Illegal source IP');
INSERT INTO `sys_language_en_us` VALUES (423,'Illegal target IP');
INSERT INTO `sys_language_en_us` VALUES (424,'Add access control');
INSERT INTO `sys_language_en_us` VALUES (425,'Modify access control');
INSERT INTO `sys_language_en_us` VALUES (426,'Source IP anti CC');
INSERT INTO `sys_language_en_us` VALUES (427,'Access speed limit of source IP address');
INSERT INTO `sys_language_en_us` VALUES (428,'Blocking access time');
INSERT INTO `sys_language_en_us` VALUES (429,'Access speed limit of target URI');
INSERT INTO `sys_language_en_us` VALUES (430,'Target URI list');
INSERT INTO `sys_language_en_us` VALUES (431,'Specific URL anti CC');
INSERT INTO `sys_language_en_us` VALUES (432,'Times');
INSERT INTO `sys_language_en_us` VALUES (433,'Network traffic selection');
INSERT INTO `sys_language_en_us` VALUES (434,'Recommend threshold');
INSERT INTO `sys_language_en_us` VALUES (435,'The system will recommend reasonable threshold range according to selected network traffic.');
INSERT INTO `sys_language_en_us` VALUES (436,'Threshold of trigerring total traffic');
INSERT INTO `sys_language_en_us` VALUES (437,'Data packet/s');
INSERT INTO `sys_language_en_us` VALUES (438,'Total traffic threshold/single IP');
INSERT INTO `sys_language_en_us` VALUES (439,'Threshold to trigger packet');
INSERT INTO `sys_language_en_us` VALUES (440,'Packet threshold/single IP');
INSERT INTO `sys_language_en_us` VALUES (441,'Threshold to trigger SYN Flood');
INSERT INTO `sys_language_en_us` VALUES (442,'SYN Flood  threshold/single IP');
INSERT INTO `sys_language_en_us` VALUES (443,'Target IP address');
INSERT INTO `sys_language_en_us` VALUES (444,'Configure file export');
INSERT INTO `sys_language_en_us` VALUES (445,'Export configuration');
INSERT INTO `sys_language_en_us` VALUES (447,'Successfully restore configuration');
INSERT INTO `sys_language_en_us` VALUES (448,'Configuration is applied');
INSERT INTO `sys_language_en_us` VALUES (449,'Congiguration is generated successfully');
INSERT INTO `sys_language_en_us` VALUES (450,'Unkown type');
INSERT INTO `sys_language_en_us` VALUES (451,'Configuration completed');
INSERT INTO `sys_language_en_us` VALUES (452,'Disk threshold');
INSERT INTO `sys_language_en_us` VALUES (453,'Please select a row of data');
INSERT INTO `sys_language_en_us` VALUES (454,'Please select the data to delete');
INSERT INTO `sys_language_en_us` VALUES (455,'Page type');
INSERT INTO `sys_language_en_us` VALUES (456,'Page file');
INSERT INTO `sys_language_en_us` VALUES (457,'Configure text');
INSERT INTO `sys_language_en_us` VALUES (458,'Take effect');
INSERT INTO `sys_language_en_us` VALUES (459,'Page exists');
INSERT INTO `sys_language_en_us` VALUES (460,'Fail to upload file');
INSERT INTO `sys_language_en_us` VALUES (462,'Fill in reminder text');
INSERT INTO `sys_language_en_us` VALUES (463,'Have not selected data');
INSERT INTO `sys_language_en_us` VALUES (464,'Error page type');
INSERT INTO `sys_language_en_us` VALUES (465,'Upload page');
INSERT INTO `sys_language_en_us` VALUES (466,'Reminder text of page');
INSERT INTO `sys_language_en_us` VALUES (467,'File extension name');
INSERT INTO `sys_language_en_us` VALUES (468,'Monitoring interface');
INSERT INTO `sys_language_en_us` VALUES (469,'Priority');
INSERT INTO `sys_language_en_us` VALUES (470,'Limit from 0 to 255');
INSERT INTO `sys_language_en_us` VALUES (471,'Database configuration synchronization');
INSERT INTO `sys_language_en_us` VALUES (472,'End-to-end');
INSERT INTO `sys_language_en_us` VALUES (473,'The selected interface doesn\'t set up IP address.');
INSERT INTO `sys_language_en_us` VALUES (474,'File type will not be compromised');
INSERT INTO `sys_language_en_us` VALUES (475,'Disabled HTTP header field setting');
INSERT INTO `sys_language_en_us` VALUES (476,'HTTP header field');
INSERT INTO `sys_language_en_us` VALUES (478,'Allowed HTTP protocol version setting');
INSERT INTO `sys_language_en_us` VALUES (479,'HTTP protocol version');
INSERT INTO `sys_language_en_us` VALUES (480,'Danger level');
INSERT INTO `sys_language_en_us` VALUES (481,'Attack type');
INSERT INTO `sys_language_en_us` VALUES (482,'Source IP address');
INSERT INTO `sys_language_en_us` VALUES (485,'General information');
INSERT INTO `sys_language_en_us` VALUES (486,'Rule template base updating failed.');
INSERT INTO `sys_language_en_us` VALUES (487,'E-mail alert');
INSERT INTO `sys_language_en_us` VALUES (488,'SMS alert');
INSERT INTO `sys_language_en_us` VALUES (489,'Send interval');
INSERT INTO `sys_language_en_us` VALUES (490,'Alert sending interval, unit: hour');
INSERT INTO `sys_language_en_us` VALUES (491,'Notification setting');
INSERT INTO `sys_language_en_us` VALUES (492,'Login account');
INSERT INTO `sys_language_en_us` VALUES (493,'Login password');
INSERT INTO `sys_language_en_us` VALUES (494,'Send port');
INSERT INTO `sys_language_en_us` VALUES (495,'Email received');
INSERT INTO `sys_language_en_us` VALUES (496,'Mobile Number to receive alert');
INSERT INTO `sys_language_en_us` VALUES (497,'Rule ID');
INSERT INTO `sys_language_en_us` VALUES (498,'Target host');
INSERT INTO `sys_language_en_us` VALUES (499,'Haven\'t selected data to update');
INSERT INTO `sys_language_en_us` VALUES (500,'Haven\'t selected data to delete');
INSERT INTO `sys_language_en_us` VALUES (501,'Transfer to blacklist');
INSERT INTO `sys_language_en_us` VALUES (502,'Transfer to white list');
INSERT INTO `sys_language_en_us` VALUES (503,'Search');
INSERT INTO `sys_language_en_us` VALUES (504,'Block');
INSERT INTO `sys_language_en_us` VALUES (505,'Pass');
INSERT INTO `sys_language_en_us` VALUES (506,'Black list');
INSERT INTO `sys_language_en_us` VALUES (507,'White list');
INSERT INTO `sys_language_en_us` VALUES (508,'Source');
INSERT INTO `sys_language_en_us` VALUES (509,'Target');
INSERT INTO `sys_language_en_us` VALUES (510,'Target port');
INSERT INTO `sys_language_en_us` VALUES (511,'Executed action');
INSERT INTO `sys_language_en_us` VALUES (512,'Source port');
INSERT INTO `sys_language_en_us` VALUES (513,'Geographical location');
INSERT INTO `sys_language_en_us` VALUES (514,'Unkown');
INSERT INTO `sys_language_en_us` VALUES (515,'The name list already exists, no need to add.');
INSERT INTO `sys_language_en_us` VALUES (516,'Add blacklist');
INSERT INTO `sys_language_en_us` VALUES (517,'Add white list');
INSERT INTO `sys_language_en_us` VALUES (518,'Detect port');
INSERT INTO `sys_language_en_us` VALUES (519,'Click \"Generate technical support package\" to generate a downloadable Support Package file');
INSERT INTO `sys_language_en_us` VALUES (520,'Generate technical support package');
INSERT INTO `sys_language_en_us` VALUES (521,'Regular report');
INSERT INTO `sys_language_en_us` VALUES (522,'Access/traffic report');
INSERT INTO `sys_language_en_us` VALUES (523,'Add user defined rule');
INSERT INTO `sys_language_en_us` VALUES (524,'Modify user defined rule');
INSERT INTO `sys_language_en_us` VALUES (525,'Rule template name');
INSERT INTO `sys_language_en_us` VALUES (526,'Inheritance template');
INSERT INTO `sys_language_en_us` VALUES (527,'Inheritance template name');
INSERT INTO `sys_language_en_us` VALUES (528,'Template type');
INSERT INTO `sys_language_en_us` VALUES (529,'Site group template');
INSERT INTO `sys_language_en_us` VALUES (530,'Site template');
INSERT INTO `sys_language_en_us` VALUES (531,'Template type is selected as the site template, but the site template of group is not selected');
INSERT INTO `sys_language_en_us` VALUES (532,'Add rule template');
INSERT INTO `sys_language_en_us` VALUES (533,'Modify rule template');
INSERT INTO `sys_language_en_us` VALUES (534,'Template name');
INSERT INTO `sys_language_en_us` VALUES (535,'Template instruction');
INSERT INTO `sys_language_en_us` VALUES (536,'Affiliated site group template');
INSERT INTO `sys_language_en_us` VALUES (537,'Max length');
INSERT INTO `sys_language_en_us` VALUES (538,'Max length of parameter name');
INSERT INTO `sys_language_en_us` VALUES (539,'Max length of parameter');
INSERT INTO `sys_language_en_us` VALUES (540,'Max number of parameter');
INSERT INTO `sys_language_en_us` VALUES (541,'Max number');
INSERT INTO `sys_language_en_us` VALUES (542,'If the above fields are filled in with 0, then the setting is invalid.');
INSERT INTO `sys_language_en_us` VALUES (543,'It is suggested to close it after learning is finished.');
INSERT INTO `sys_language_en_us` VALUES (544,'Whether to apply learning results');
INSERT INTO `sys_language_en_us` VALUES (545,'Select data');
INSERT INTO `sys_language_en_us` VALUES (546,'Selected data is empty');
INSERT INTO `sys_language_en_us` VALUES (547,'Delete data');
INSERT INTO `sys_language_en_us` VALUES (548,'Disable data');
INSERT INTO `sys_language_en_us` VALUES (549,'Sensitive word filtering');
INSERT INTO `sys_language_en_us` VALUES (550,'Use * to replace the set sensitive word');
INSERT INTO `sys_language_en_us` VALUES (551,'Use \"|\" between words');
INSERT INTO `sys_language_en_us` VALUES (552,'Hide type');
INSERT INTO `sys_language_en_us` VALUES (553,'Monitoring target');
INSERT INTO `sys_language_en_us` VALUES (554,'Latest execution time');
INSERT INTO `sys_language_en_us` VALUES (555,'Response time');
INSERT INTO `sys_language_en_us` VALUES (556,'No data available');
INSERT INTO `sys_language_en_us` VALUES (557,'System error');
INSERT INTO `sys_language_en_us` VALUES (558,'Normal');
INSERT INTO `sys_language_en_us` VALUES (559,'Hour');
INSERT INTO `sys_language_en_us` VALUES (560,'Minute');
INSERT INTO `sys_language_en_us` VALUES (561,'Check report');
INSERT INTO `sys_language_en_us` VALUES (562,'Time frame');
INSERT INTO `sys_language_en_us` VALUES (563,'Response time distribution');
INSERT INTO `sys_language_en_us` VALUES (564,'Response time (millisecond)');
INSERT INTO `sys_language_en_us` VALUES (565,'Monitor target URL status');
INSERT INTO `sys_language_en_us` VALUES (566,'Intelligent blocking');
INSERT INTO `sys_language_en_us` VALUES (567,'Set 300 seconds');
INSERT INTO `sys_language_en_us` VALUES (568,'Not less than 10 times (Unit: times)');
INSERT INTO `sys_language_en_us` VALUES (569,'Benchmark blocking time');
INSERT INTO `sys_language_en_us` VALUES (570,'Not less than 600 seconds (Unit: second)');
INSERT INTO `sys_language_en_us` VALUES (571,'Attack time');
INSERT INTO `sys_language_en_us` VALUES (572,'Blocking duration time(unit: second)');
INSERT INTO `sys_language_en_us` VALUES (573,'Protected against crawler');
INSERT INTO `sys_language_en_us` VALUES (574,'Crawler type');
INSERT INTO `sys_language_en_us` VALUES (575,'Company name');
INSERT INTO `sys_language_en_us` VALUES (576,'Company address');
INSERT INTO `sys_language_en_us` VALUES (577,'Licence file');
INSERT INTO `sys_language_en_us` VALUES (578,'Only part of file is uploaded');
INSERT INTO `sys_language_en_us` VALUES (579,'Only allow to upload');
INSERT INTO `sys_language_en_us` VALUES (580,'Format file');
INSERT INTO `sys_language_en_us` VALUES (581,'IP + subnet mask');
INSERT INTO `sys_language_en_us` VALUES (582,'IP or IP segment exists');
INSERT INTO `sys_language_en_us` VALUES (583,'Illegal IP address, such as 192.168.1.1');
INSERT INTO `sys_language_en_us` VALUES (584,'Illegal IP and subnet mask, such as 192.168.1.0/24');
INSERT INTO `sys_language_en_us` VALUES (585,'Verification code error');
INSERT INTO `sys_language_en_us` VALUES (586,'This user doesnˇt exist or is banned from login.');
INSERT INTO `sys_language_en_us` VALUES (587,'This user is banned from login.');
INSERT INTO `sys_language_en_us` VALUES (588,'Login succeeded');
INSERT INTO `sys_language_en_us` VALUES (589,'Login failed');
INSERT INTO `sys_language_en_us` VALUES (590,'Login timeout(minute)');
INSERT INTO `sys_language_en_us` VALUES (591,'Limit login attempts');
INSERT INTO `sys_language_en_us` VALUES (592,'Login error lockout time (minutes)');
INSERT INTO `sys_language_en_us` VALUES (593,'Home page function customization');
INSERT INTO `sys_language_en_us` VALUES (594,'Technical support order has been sent out.');
INSERT INTO `sys_language_en_us` VALUES (595,'Upgrade succeeded');
INSERT INTO `sys_language_en_us` VALUES (596,'Select to upgrade file');
INSERT INTO `sys_language_en_us` VALUES (597,'Open all');
INSERT INTO `sys_language_en_us` VALUES (598,'Close all');
INSERT INTO `sys_language_en_us` VALUES (599,'Whether to delete this menu');
INSERT INTO `sys_language_en_us` VALUES (600,'Whether to disply submenu');
INSERT INTO `sys_language_en_us` VALUES (601,'Access path');
INSERT INTO `sys_language_en_us` VALUES (602,'Menu name');
INSERT INTO `sys_language_en_us` VALUES (603,'Report time');
INSERT INTO `sys_language_en_us` VALUES (604,'Upload time');
INSERT INTO `sys_language_en_us` VALUES (605,'Site URL');
INSERT INTO `sys_language_en_us` VALUES (606,'File analysis result - display');
INSERT INTO `sys_language_en_us` VALUES (607,'Deleted data is empty');
INSERT INTO `sys_language_en_us` VALUES (608,'Serious level');
INSERT INTO `sys_language_en_us` VALUES (609,'Report');
INSERT INTO `sys_language_en_us` VALUES (610,'Scan');
INSERT INTO `sys_language_en_us` VALUES (611,'Not scan');
INSERT INTO `sys_language_en_us` VALUES (612,'Is scanning');
INSERT INTO `sys_language_en_us` VALUES (613,'Scanning failed');
INSERT INTO `sys_language_en_us` VALUES (614,'Scanning address');
INSERT INTO `sys_language_en_us` VALUES (615,'Fill in real and valid scanning address.');
INSERT INTO `sys_language_en_us` VALUES (616,'Otherwise scanning cannot be performed.');
INSERT INTO `sys_language_en_us` VALUES (617,'Scanning results do not exist.');
INSERT INTO `sys_language_en_us` VALUES (618,'SSH switch setting');
INSERT INTO `sys_language_en_us` VALUES (619,'Site group');
INSERT INTO `sys_language_en_us` VALUES (620,'Rule template');
INSERT INTO `sys_language_en_us` VALUES (621,'Number of sites');
INSERT INTO `sys_language_en_us` VALUES (622,'Among selected site group, there is corresponding site, which cannot be deleted.');
INSERT INTO `sys_language_en_us` VALUES (623,'Parameter error');
INSERT INTO `sys_language_en_us` VALUES (624,'Fail to save');
INSERT INTO `sys_language_en_us` VALUES (625,'Site');
INSERT INTO `sys_language_en_us` VALUES (626,'Port');
INSERT INTO `sys_language_en_us` VALUES (627,'Site group name');
INSERT INTO `sys_language_en_us` VALUES (628,'Policy template');
INSERT INTO `sys_language_en_us` VALUES (629,'Single policy template');
INSERT INTO `sys_language_en_us` VALUES (630,'Whether to reverse proxy');
INSERT INTO `sys_language_en_us` VALUES (631,'Site name error');
INSERT INTO `sys_language_en_us` VALUES (632,'Port error');
INSERT INTO `sys_language_en_us` VALUES (633,'Protocol');
INSERT INTO `sys_language_en_us` VALUES (634,'Operating system');
INSERT INTO `sys_language_en_us` VALUES (635,'Development language');
INSERT INTO `sys_language_en_us` VALUES (636,'Update time');
INSERT INTO `sys_language_en_us` VALUES (637,'IP address error');
INSERT INTO `sys_language_en_us` VALUES (638,'Channel sending failed');
INSERT INTO `sys_language_en_us` VALUES (639,'Add site group');
INSERT INTO `sys_language_en_us` VALUES (640,'Return');
INSERT INTO `sys_language_en_us` VALUES (641,'Modify site group');
INSERT INTO `sys_language_en_us` VALUES (642,'Configure policy');
INSERT INTO `sys_language_en_us` VALUES (643,'Site policy rule priority is higher than site group policy rule.');
INSERT INTO `sys_language_en_us` VALUES (644,'Root node');
INSERT INTO `sys_language_en_us` VALUES (645,'Affiliated site');
INSERT INTO `sys_language_en_us` VALUES (646,'Address and port');
INSERT INTO `sys_language_en_us` VALUES (647,'Site name must be IPV4 address or legal domain name.');
INSERT INTO `sys_language_en_us` VALUES (648,'Add site');
INSERT INTO `sys_language_en_us` VALUES (649,'Modify site');
INSERT INTO `sys_language_en_us` VALUES (650,'Rule');
INSERT INTO `sys_language_en_us` VALUES (651,'Rule name');
INSERT INTO `sys_language_en_us` VALUES (652,'Blocking way');
INSERT INTO `sys_language_en_us` VALUES (653,'Alert level');
INSERT INTO `sys_language_en_us` VALUES (654,'Category');
INSERT INTO `sys_language_en_us` VALUES (655,'Rule set');
INSERT INTO `sys_language_en_us` VALUES (656,'Danger description');
INSERT INTO `sys_language_en_us` VALUES (657,'Solution suggestion');
INSERT INTO `sys_language_en_us` VALUES (658,'Network timeout');
INSERT INTO `sys_language_en_us` VALUES (659,'Successfully modified');
INSERT INTO `sys_language_en_us` VALUES (660,'Modification failed');
INSERT INTO `sys_language_en_us` VALUES (661,'Action succeeded');
INSERT INTO `sys_language_en_us` VALUES (662,'Update failed');
INSERT INTO `sys_language_en_us` VALUES (663,'Failed to delete');
INSERT INTO `sys_language_en_us` VALUES (664,'Completed');
INSERT INTO `sys_language_en_us` VALUES (665,'Stopped');
INSERT INTO `sys_language_en_us` VALUES (666,'Upload successfully');
INSERT INTO `sys_language_en_us` VALUES (670,'Clear cache');
INSERT INTO `sys_language_en_us` VALUES (672,'Privilege check');
INSERT INTO `sys_language_en_us` VALUES (673,'Authorization information');
INSERT INTO `sys_language_en_us` VALUES (674,'Privilege modification');
INSERT INTO `sys_language_en_us` VALUES (676,'Management log');
INSERT INTO `sys_language_en_us` VALUES (677,'System log');
INSERT INTO `sys_language_en_us` VALUES (678,'Compiler uploading');
INSERT INTO `sys_language_en_us` VALUES (681,'Log config');
INSERT INTO `sys_language_en_us` VALUES (688,'Firewall log');
INSERT INTO `sys_language_en_us` VALUES (689,'Intrusion prevention log');
INSERT INTO `sys_language_en_us` VALUES (690,'Security policy');
INSERT INTO `sys_language_en_us` VALUES (691,'Web application protection log');
INSERT INTO `sys_language_en_us` VALUES (692,'Virus prevention log');
INSERT INTO `sys_language_en_us` VALUES (693,'Information leakage prevention log');
INSERT INTO `sys_language_en_us` VALUES (694,'DDOS prevention log');
INSERT INTO `sys_language_en_us` VALUES (695,'Application management and control log');
INSERT INTO `sys_language_en_us` VALUES (696,'URL access log');
INSERT INTO `sys_language_en_us` VALUES (697,'Log library');
INSERT INTO `sys_language_en_us` VALUES (698,'User authentication log');
INSERT INTO `sys_language_en_us` VALUES (699,'Subnet detection log');
INSERT INTO `sys_language_en_us` VALUES (700,'IpsecVPN log');
INSERT INTO `sys_language_en_us` VALUES (703,'Intrusion prevention');
INSERT INTO `sys_language_en_us` VALUES (705,'Clear');
INSERT INTO `sys_language_en_us` VALUES (706,'Add anti false positive');
INSERT INTO `sys_language_en_us` VALUES (707,'Enable');
INSERT INTO `sys_language_en_us` VALUES (708,'Stastistics of intrusion quantity(current month)');
INSERT INTO `sys_language_en_us` VALUES (709,'Stastistics of intrusion type(current month)');
INSERT INTO `sys_language_en_us` VALUES (710,'Product information');
INSERT INTO `sys_language_en_us` VALUES (718,'Bypass setting');
INSERT INTO `sys_language_en_us` VALUES (719,'Multi-language');
INSERT INTO `sys_language_en_us` VALUES (720,'Language test');
INSERT INTO `sys_language_en_us` VALUES (721,'Export lanaguage package');
INSERT INTO `sys_language_en_us` VALUES (722,'Disk clearing');
INSERT INTO `sys_language_en_us` VALUES (723,'Import lanaguage package');
INSERT INTO `sys_language_en_us` VALUES (724,'Language KEY');
INSERT INTO `sys_language_en_us` VALUES (725,'Check uniqueness of translation character');
INSERT INTO `sys_language_en_us` VALUES (728,'Regular report');
INSERT INTO `sys_language_en_us` VALUES (729,'Security management');
INSERT INTO `sys_language_en_us` VALUES (730,'HTTP request action filtering');
INSERT INTO `sys_language_en_us` VALUES (731,'HTTP request content filtering');
INSERT INTO `sys_language_en_us` VALUES (732,'Server information hiding');
INSERT INTO `sys_language_en_us` VALUES (733,'Enable cloud protection');
INSERT INTO `sys_language_en_us` VALUES (734,'Test menu(not open)log');
INSERT INTO `sys_language_en_us` VALUES (735,'Personal setting');
INSERT INTO `sys_language_en_us` VALUES (736,'For developers only');
INSERT INTO `sys_language_en_us` VALUES (737,'Menu privilege management');
INSERT INTO `sys_language_en_us` VALUES (738,'Acquire single privilege information');
INSERT INTO `sys_language_en_us` VALUES (739,'OCR blocking');
INSERT INTO `sys_language_en_us` VALUES (740,'User authentication');
INSERT INTO `sys_language_en_us` VALUES (741,'Bridge device');
INSERT INTO `sys_language_en_us` VALUES (742,'Firewall');
INSERT INTO `sys_language_en_us` VALUES (743,'Transparent proxy');
INSERT INTO `sys_language_en_us` VALUES (744,'Access control');
INSERT INTO `sys_language_en_us` VALUES (745,'Reverse proxy');
INSERT INTO `sys_language_en_us` VALUES (746,'Security protection');
INSERT INTO `sys_language_en_us` VALUES (747,'Log management');
INSERT INTO `sys_language_en_us` VALUES (748,'Log task');
INSERT INTO `sys_language_en_us` VALUES (753,'Cycle');
INSERT INTO `sys_language_en_us` VALUES (754,'Image link');
INSERT INTO `sys_language_en_us` VALUES (783,'Bridge device name');
INSERT INTO `sys_language_en_us` VALUES (786,'Bridge type');
INSERT INTO `sys_language_en_us` VALUES (787,'Confirm');
INSERT INTO `sys_language_en_us` VALUES (788,'Cancel');
INSERT INTO `sys_language_en_us` VALUES (789,'Conirm new password');
INSERT INTO `sys_language_en_us` VALUES (790,'Open');
INSERT INTO `sys_language_en_us` VALUES (791,'Enable');
INSERT INTO `sys_language_en_us` VALUES (792,'All records');
INSERT INTO `sys_language_en_us` VALUES (793,'All');
INSERT INTO `sys_language_en_us` VALUES (794,'Select all');
INSERT INTO `sys_language_en_us` VALUES (795,'Select none');
INSERT INTO `sys_language_en_us` VALUES (796,'Date');
INSERT INTO `sys_language_en_us` VALUES (797,'Log');
INSERT INTO `sys_language_en_us` VALUES (798,'Emergent');
INSERT INTO `sys_language_en_us` VALUES (799,'Alert');
INSERT INTO `sys_language_en_us` VALUES (800,'Serious');
INSERT INTO `sys_language_en_us` VALUES (801,'Error');
INSERT INTO `sys_language_en_us` VALUES (802,'Alert');
INSERT INTO `sys_language_en_us` VALUES (803,'Conirmed password is inconsistent');
INSERT INTO `sys_language_en_us` VALUES (804,'New password must be filled');
INSERT INTO `sys_language_en_us` VALUES (805,'KB/S');
INSERT INTO `sys_language_en_us` VALUES (806,'Traffic');
INSERT INTO `sys_language_en_us` VALUES (807,'Product model');
INSERT INTO `sys_language_en_us` VALUES (808,'System version');
INSERT INTO `sys_language_en_us` VALUES (809,'Rule version');
INSERT INTO `sys_language_en_us` VALUES (810,'Product serial number');
INSERT INTO `sys_language_en_us` VALUES (811,'Engine setting');
INSERT INTO `sys_language_en_us` VALUES (812,'Setting of default blocking way');
INSERT INTO `sys_language_en_us` VALUES (813,'Detect port setting:Designate the port to be detected, if there are several, please use |to separate and don\'t begin with 0');
INSERT INTO `sys_language_en_us` VALUES (814,'Please add http://or https:// at URL');
INSERT INTO `sys_language_en_us` VALUES (815,'Clear menu column');
INSERT INTO `sys_language_en_us` VALUES (816,'Clear all caches');
INSERT INTO `sys_language_en_us` VALUES (817,'Clear successfully');
INSERT INTO `sys_language_en_us` VALUES (818,'After being enabled, any subsequent access of the source IP address will be prohibited when access times of this IP address exceeds the limit');
INSERT INTO `sys_language_en_us` VALUES (819,'Limit of request times');
INSERT INTO `sys_language_en_us` VALUES (820,'After being enabled, any subsequent access of the source IP address will be prohibited when access times of this IP address to target URI exceeds the limit');
INSERT INTO `sys_language_en_us` VALUES (821,'One URI for each line,and several lines can be input with URI right.For example:/test.php (there is no need to input parameter part.)');
INSERT INTO `sys_language_en_us` VALUES (822,'Please fill in relevant parameter about source IP against CC');
INSERT INTO `sys_language_en_us` VALUES (823,'Please fill in relevant parameter about specific URL against CC');
INSERT INTO `sys_language_en_us` VALUES (824,'Open DDOS cloud protection');
INSERT INTO `sys_language_en_us` VALUES (825,'Threshold to trigger other TCP Flood');
INSERT INTO `sys_language_en_us` VALUES (826,'Other TCP Flood threshold/single IP');
INSERT INTO `sys_language_en_us` VALUES (827,'Prohibit all UDP protocol\'s communication.(After being enabled, communication that uses UDP protocol will be prohibited, including DNS resolution service using UDP protocol)');
INSERT INTO `sys_language_en_us` VALUES (828,'Prohibit all ICMP protocol\'s communication.(After being enabled, communication that uses ICMP protocol will be prohibited, including PING request using ICMP protocol)');
INSERT INTO `sys_language_en_us` VALUES (829,'For all the above spaces, please fill in positive integer greater than 0 and each threshold value is suggested to be not less than');
INSERT INTO `sys_language_en_us` VALUES (830,'For network traffic, please fill in digit between 1 and 1024');
INSERT INTO `sys_language_en_us` VALUES (831,'DDOS attack');
INSERT INTO `sys_language_en_us` VALUES (832,'Restore default config');
INSERT INTO `sys_language_en_us` VALUES (833,'Click \"restore default config\" button to restore the default config of this device');
INSERT INTO `sys_language_en_us` VALUES (834,'Config file import');
INSERT INTO `sys_language_en_us` VALUES (835,'Select backup file, and click \"import config\" button to restore previous config');
INSERT INTO `sys_language_en_us` VALUES (836,'Import config');
INSERT INTO `sys_language_en_us` VALUES (837,'Click \"export config\" button to back up current database config');
INSERT INTO `sys_language_en_us` VALUES (838,'It is configuring file, please wait 1 to 2 minutes…');
INSERT INTO `sys_language_en_us` VALUES (839,'Kind notice of system');
INSERT INTO `sys_language_en_us` VALUES (840,'After restoring default config, the system will be restarted to confirm');
INSERT INTO `sys_language_en_us` VALUES (841,'It is configuring file, please wait 1 to 2 minutes…');
INSERT INTO `sys_language_en_us` VALUES (842,'After restoring default config, the system will be restarted');
INSERT INTO `sys_language_en_us` VALUES (843,'The disk will automatically clear parameter setting');
INSERT INTO `sys_language_en_us` VALUES (844,'Whether to open automatic clearing');
INSERT INTO `sys_language_en_us` VALUES (845,'Log will be automatically cleared when it exceeds the set figure');
INSERT INTO `sys_language_en_us` VALUES (846,'Please disable first before modification');
INSERT INTO `sys_language_en_us` VALUES (847,'Unable to acquire uploading file information');
INSERT INTO `sys_language_en_us` VALUES (848,'Confirm the file to be available');
INSERT INTO `sys_language_en_us` VALUES (849,'Disable first before deletion');
INSERT INTO `sys_language_en_us` VALUES (850,'Disable setting of the requested file extension name');
INSERT INTO `sys_language_en_us` VALUES (851,'The requested file extension name type will be prohibited');
INSERT INTO `sys_language_en_us` VALUES (852,'VIP enabled');
INSERT INTO `sys_language_en_us` VALUES (853,'Whether to open');
INSERT INTO `sys_language_en_us` VALUES (854,'Bridge interface');
INSERT INTO `sys_language_en_us` VALUES (855,'Allow HTTP request content');
INSERT INTO `sys_language_en_us` VALUES (856,'What is beyond requested content will be rejected');
INSERT INTO `sys_language_en_us` VALUES (857,'HTTP request content');
INSERT INTO `sys_language_en_us` VALUES (858,'HTTP request action setting');
INSERT INTO `sys_language_en_us` VALUES (859,'HTTP request action');
INSERT INTO `sys_language_en_us` VALUES (860,'After being enabled');
INSERT INTO `sys_language_en_us` VALUES (861,'This HTTP request action will be allowed');
INSERT INTO `sys_language_en_us` VALUES (862,'The requested HTTP header field will be prohibited');
INSERT INTO `sys_language_en_us` VALUES (863,'For all the above spaces, please fill in positive integer greater than 0 but less than 2147483647');
INSERT INTO `sys_language_en_us` VALUES (864,'The requested HTTP protocol version will be allowed');
INSERT INTO `sys_language_en_us` VALUES (866,'Intrusion log');
INSERT INTO `sys_language_en_us` VALUES (867,'Matching content');
INSERT INTO `sys_language_en_us` VALUES (868,'Default template can\'t be found in rule template library');
INSERT INTO `sys_language_en_us` VALUES (869,'The corresponding site doesn\'t exist, so please go to \"site group management\" to add');
INSERT INTO `sys_language_en_us` VALUES (870,'Open the e-mail function of intrusion record');
INSERT INTO `sys_language_en_us` VALUES (871,'Open SMS alert function of intrusion record');
INSERT INTO `sys_language_en_us` VALUES (872,'Sender\'s name');
INSERT INTO `sys_language_en_us` VALUES (873,'Sender\'s e-amil address');
INSERT INTO `sys_language_en_us` VALUES (874,'Send in this name and in EMAIL(it can be the same with sender\'s e-mail)');
INSERT INTO `sys_language_en_us` VALUES (875,'Sender\'s password');
INSERT INTO `sys_language_en_us` VALUES (876,'SMTP server address');
INSERT INTO `sys_language_en_us` VALUES (877,'Sending server');
INSERT INTO `sys_language_en_us` VALUES (878,'SMTP server port');
INSERT INTO `sys_language_en_us` VALUES (879,'Recipient\'s e-mail');
INSERT INTO `sys_language_en_us` VALUES (880,'Recipient\'s cell phone number');
INSERT INTO `sys_language_en_us` VALUES (881,'All the above information is very important, and please ensure what you input is right, otherwise, it is unable to send/receive e-mamil and message');
INSERT INTO `sys_language_en_us` VALUES (882,'Whether to enable');
INSERT INTO `sys_language_en_us` VALUES (884,'Precise searching');
INSERT INTO `sys_language_en_us` VALUES (885,'Such as');
INSERT INTO `sys_language_en_us` VALUES (886,'Illegal external connection log');
INSERT INTO `sys_language_en_us` VALUES (888,'Tip: It will export log according to current condition and the latest 20000 records will be exported at most');
INSERT INTO `sys_language_en_us` VALUES (889,'Designate the port to be detected, and if there are several, please use |to separate and do not start with 0, for example');
INSERT INTO `sys_language_en_us` VALUES (890,'Technical support package is an approach to help manufacturer eliminate system fault. When system breaks down, please generate technical support package and send it to us');
INSERT INTO `sys_language_en_us` VALUES (891,'It is compressing technical support package file, please wait 1 to 2 minutes');
INSERT INTO `sys_language_en_us` VALUES (892,'Beyond the limit, please contact technician to resolve');
INSERT INTO `sys_language_en_us` VALUES (893,'Site group enabled');
INSERT INTO `sys_language_en_us` VALUES (894,'The max length of content');
INSERT INTO `sys_language_en_us` VALUES (895,'Enable self-learning');
INSERT INTO `sys_language_en_us` VALUES (896,'Enable access white list');
INSERT INTO `sys_language_en_us` VALUES (897,'Whether to enable self-learning');
INSERT INTO `sys_language_en_us` VALUES (898,'Whether to enable access white list');
INSERT INTO `sys_language_en_us` VALUES (899,'Enable data');
INSERT INTO `sys_language_en_us` VALUES (900,'Sensitive content');
INSERT INTO `sys_language_en_us` VALUES (901,'Hide server information');
INSERT INTO `sys_language_en_us` VALUES (902,'Monitoring frequency');
INSERT INTO `sys_language_en_us` VALUES (903,'Please write down real and effective monitoring address, otherwise, it is unable to scan');
INSERT INTO `sys_language_en_us` VALUES (904,'Regular monitoring frequency');
INSERT INTO `sys_language_en_us` VALUES (905,'After enabling intelligent blocking(after being enabled, the system will identify the source IP address that launches attack frequently according to set condition and reject access of this IP within a period )');
INSERT INTO `sys_language_en_us` VALUES (906,'Statistical period');
INSERT INTO `sys_language_en_us` VALUES (907,'Intrusion times');
INSERT INTO `sys_language_en_us` VALUES (908,'Please fill in the above spaces as required');
INSERT INTO `sys_language_en_us` VALUES (909,'Intelligently block log');
INSERT INTO `sys_language_en_us` VALUES (910,'Authorized serial number');
INSERT INTO `sys_language_en_us` VALUES (911,'Valid period');
INSERT INTO `sys_language_en_us` VALUES (912,'Select license within valid period');
INSERT INTO `sys_language_en_us` VALUES (913,'File size exceeds server space');
INSERT INTO `sys_language_en_us` VALUES (914,'File size exceeds browser limit');
INSERT INTO `sys_language_en_us` VALUES (915,'Temporary folder of server is lost');
INSERT INTO `sys_language_en_us` VALUES (916,'Writing in file to temporary folder error');
INSERT INTO `sys_language_en_us` VALUES (917,'Please be patient in waiting for authorization and authentication');
INSERT INTO `sys_language_en_us` VALUES (918,'Do not enable blacklist and white list');
INSERT INTO `sys_language_en_us` VALUES (919,'Enable white list');
INSERT INTO `sys_language_en_us` VALUES (920,'Enable blacklist');
INSERT INTO `sys_language_en_us` VALUES (921,'IP range');
INSERT INTO `sys_language_en_us` VALUES (922,'IP range is illegal, for example:192.168.1.1-192.168.255.254');
INSERT INTO `sys_language_en_us` VALUES (924,'Current account has failed to log in for %s, and %s later, it will be locked');
INSERT INTO `sys_language_en_us` VALUES (925,'Normal access');
INSERT INTO `sys_language_en_us` VALUES (926,'From crawler');
INSERT INTO `sys_language_en_us` VALUES (927,'From threat');
INSERT INTO `sys_language_en_us` VALUES (928,'Page views');
INSERT INTO `sys_language_en_us` VALUES (929,'Visitors');
INSERT INTO `sys_language_en_us` VALUES (930,'Number of ages');
INSERT INTO `sys_language_en_us` VALUES (931,'Number of files');
INSERT INTO `sys_language_en_us` VALUES (932,'Access source');
INSERT INTO `sys_language_en_us` VALUES (933,'Real-time traffic');
INSERT INTO `sys_language_en_us` VALUES (934,'Occupation of system resources');
INSERT INTO `sys_language_en_us` VALUES (935,'Select time');
INSERT INTO `sys_language_en_us` VALUES (936,'Real-time monitoring');
INSERT INTO `sys_language_en_us` VALUES (937,'Search historical data');
INSERT INTO `sys_language_en_us` VALUES (938,'Number of connections');
INSERT INTO `sys_language_en_us` VALUES (939,'Number of processing');
INSERT INTO `sys_language_en_us` VALUES (940,'Incorrect time parameter');
INSERT INTO `sys_language_en_us` VALUES (941,'Clearing action will clear all the data under current searching condition');
INSERT INTO `sys_language_en_us` VALUES (942,'Data cannot be restored after being cleared');
INSERT INTO `sys_language_en_us` VALUES (943,'Clearing condition must be contained');
INSERT INTO `sys_language_en_us` VALUES (944,'Anomalous file uploading log');
INSERT INTO `sys_language_en_us` VALUES (945,'Task name');
INSERT INTO `sys_language_en_us` VALUES (946,'There is task ongoing');
INSERT INTO `sys_language_en_us` VALUES (947,'Waiting for task to be finished and then add new ones');
INSERT INTO `sys_language_en_us` VALUES (948,'Stop task before deletion');
INSERT INTO `sys_language_en_us` VALUES (949,'Server number');
INSERT INTO `sys_language_en_us` VALUES (950,'WEB server');
INSERT INTO `sys_language_en_us` VALUES (951,'Storage failed');
INSERT INTO `sys_language_en_us` VALUES (952,'Read-in failed');
INSERT INTO `sys_language_en_us` VALUES (953,'IP address and port must be filled');
INSERT INTO `sys_language_en_us` VALUES (954,'Add server');
INSERT INTO `sys_language_en_us` VALUES (955,'Input name');
INSERT INTO `sys_language_en_us` VALUES (956,'Input');
INSERT INTO `sys_language_en_us` VALUES (957,'You have no such privilege');
INSERT INTO `sys_language_en_us` VALUES (958,'Request failed');
INSERT INTO `sys_language_en_us` VALUES (959,'Do you confirm to delete it?');
INSERT INTO `sys_language_en_us` VALUES (960,'You must input integer greater than 0');
INSERT INTO `sys_language_en_us` VALUES (961,'Please select file to be upgraded');
INSERT INTO `sys_language_en_us` VALUES (962,'You can only input integer');
INSERT INTO `sys_language_en_us` VALUES (963,'You cannot input integer greater than %s');
INSERT INTO `sys_language_en_us` VALUES (964,'You cannot input integer less than %s');
INSERT INTO `sys_language_en_us` VALUES (965,'You can only input integer from %s to %s');
INSERT INTO `sys_language_en_us` VALUES (966,'You can only input digit which can be positive/negative integer or positive/negative floating point');
INSERT INTO `sys_language_en_us` VALUES (967,'You cannot input digit greater than %s');
INSERT INTO `sys_language_en_us` VALUES (968,'You cannot input digit less than %s');
INSERT INTO `sys_language_en_us` VALUES (969,'You can only input digit from %s to %s');
INSERT INTO `sys_language_en_us` VALUES (970,'You can only input digit which can be positive/negative integer or positive/negative floating point(double float)');
INSERT INTO `sys_language_en_us` VALUES (971,'Email format error');
INSERT INTO `sys_language_en_us` VALUES (972,'This item must be filled');
INSERT INTO `sys_language_en_us` VALUES (973,'You can only input data of character type');
INSERT INTO `sys_language_en_us` VALUES (974,'The number of characters you input cannot be greater than %s');
INSERT INTO `sys_language_en_us` VALUES (975,'The number of characters you input cannot be less than %s');
INSERT INTO `sys_language_en_us` VALUES (976,'It is limited to input number of characters from %s to %s');
INSERT INTO `sys_language_en_us` VALUES (977,'This item must be the only one');
INSERT INTO `sys_language_en_us` VALUES (978,'URL address error');
INSERT INTO `sys_language_en_us` VALUES (979,'CC attack');
INSERT INTO `sys_language_en_us` VALUES (980,'CMS vulnerability attack');
INSERT INTO `sys_language_en_us` VALUES (981,'File inclusion vulnerability attack');
INSERT INTO `sys_language_en_us` VALUES (982,'Common attack');
INSERT INTO `sys_language_en_us` VALUES (983,'Information leakage');
INSERT INTO `sys_language_en_us` VALUES (984,'Other attacks');
INSERT INTO `sys_language_en_us` VALUES (985,'Overflow attack');
INSERT INTO `sys_language_en_us` VALUES (986,'HTTP protection');
INSERT INTO `sys_language_en_us` VALUES (987,'SQL injection');
INSERT INTO `sys_language_en_us` VALUES (988,'Trojan virus');
INSERT INTO `sys_language_en_us` VALUES (989,'Web vulnerability attack');
INSERT INTO `sys_language_en_us` VALUES (990,'XSS');
INSERT INTO `sys_language_en_us` VALUES (993,'System tool');
INSERT INTO `sys_language_en_us` VALUES (994,'WEB control config');
INSERT INTO `sys_language_en_us` VALUES (995,'SNMP');
INSERT INTO `sys_language_en_us` VALUES (996,'Network test');
INSERT INTO `sys_language_en_us` VALUES (997,'System time');
INSERT INTO `sys_language_en_us` VALUES (998,'Packet capturing tool');
INSERT INTO `sys_language_en_us` VALUES (999,'Multicast route forwarding');
INSERT INTO `sys_language_en_us` VALUES (1000,'Subnet detection');
INSERT INTO `sys_language_en_us` VALUES (1025,'Modsec Status');
INSERT INTO `sys_language_en_us` VALUES (1026,'Modsec Requestbody Access Switch');
INSERT INTO `sys_language_en_us` VALUES (1027,'Bluedon Information Security Technologies Co., ltd. All rights reserved');
INSERT INTO `sys_language_en_us` VALUES (1028,'Bluedon WAF');
INSERT INTO `sys_language_en_us` VALUES (1029,'Pattern');
INSERT INTO `sys_language_en_us` VALUES (1030,'Default action');
INSERT INTO `sys_language_en_us` VALUES (1031,'Continue to process');
INSERT INTO `sys_language_en_us` VALUES (1032,'WAF rule translation');
INSERT INTO `sys_language_en_us` VALUES (1033,'WAF rule translation export');
INSERT INTO `sys_language_en_us` VALUES (1034,'WAF rule translation import');
INSERT INTO `sys_language_en_us` VALUES (1035,'Create language library file');
INSERT INTO `sys_language_en_us` VALUES (1036,'WAF engine');
INSERT INTO `sys_language_en_us` VALUES (1037,'Deployment pattern');
INSERT INTO `sys_language_en_us` VALUES (1038,'Access pattern');
INSERT INTO `sys_language_en_us` VALUES (1039,'Network traffic');
INSERT INTO `sys_language_en_us` VALUES (1040,'TCP packet triggering threshold');
INSERT INTO `sys_language_en_us` VALUES (1041,'TCP packet threshold/single IP');
INSERT INTO `sys_language_en_us` VALUES (1042,'ACK Flood data packet/s');
INSERT INTO `sys_language_en_us` VALUES (1043,'ACK Flood packet threshold/single IP');
INSERT INTO `sys_language_en_us` VALUES (1044,'UDP data packet/s');
INSERT INTO `sys_language_en_us` VALUES (1045,'UDP packet threshold/single IP');
INSERT INTO `sys_language_en_us` VALUES (1046,'ICMP data packet/s');
INSERT INTO `sys_language_en_us` VALUES (1047,'ICMP packet threshold/single IP');
INSERT INTO `sys_language_en_us` VALUES (1048,'UDP disabled');
INSERT INTO `sys_language_en_us` VALUES (1049,'ICMP disabled');
INSERT INTO `sys_language_en_us` VALUES (1050,'HTTP request content name');
INSERT INTO `sys_language_en_us` VALUES (1051,'HTTP request content state');
INSERT INTO `sys_language_en_us` VALUES (1052,'HTTP request action name');
INSERT INTO `sys_language_en_us` VALUES (1053,'Enable selection');
INSERT INTO `sys_language_en_us` VALUES (1054,'HTTP protocol version name');
INSERT INTO `sys_language_en_us` VALUES (1055,'HTTP protocol version state');
INSERT INTO `sys_language_en_us` VALUES (1056,'Email alert enabled');
INSERT INTO `sys_language_en_us` VALUES (1057,'Now');
INSERT INTO `sys_language_en_us` VALUES (1058,'Max Value');
INSERT INTO `sys_language_en_us` VALUES (1059,'Cycle');
INSERT INTO `sys_language_en_us` VALUES (1060,'Phone Cycle');
INSERT INTO `sys_language_en_us` VALUES (1061,'Set name');
INSERT INTO `sys_language_en_us` VALUES (1062,'Set value');
INSERT INTO `sys_language_en_us` VALUES (1063,'HTTP header field name');
INSERT INTO `sys_language_en_us` VALUES (1064,'HTTP header field state');
INSERT INTO `sys_language_en_us` VALUES (1065,'File extension state');
INSERT INTO `sys_language_en_us` VALUES (1066,'Is Ssl');
INSERT INTO `sys_language_en_us` VALUES (1067,'Ssl Path');
INSERT INTO `sys_language_en_us` VALUES (1068,'Crawler type prevention');
INSERT INTO `sys_language_en_us` VALUES (1069,'Anti hotlink file type');
INSERT INTO `sys_language_en_us` VALUES (1072,'Is Selfstudy');
INSERT INTO `sys_language_en_us` VALUES (1078,'Enable automatic clearing');
INSERT INTO `sys_language_en_us` VALUES (1079,'URI max length');
INSERT INTO `sys_language_en_us` VALUES (1080,'Max length of URI parameter name');
INSERT INTO `sys_language_en_us` VALUES (1081,'Max length of URI parameter');
INSERT INTO `sys_language_en_us` VALUES (1082,'Max number of URI parameter');
INSERT INTO `sys_language_en_us` VALUES (1083,'COOKIE max length');
INSERT INTO `sys_language_en_us` VALUES (1084,'Max length of COOKIE parameter name');
INSERT INTO `sys_language_en_us` VALUES (1085,'Max length of COOKIE content');
INSERT INTO `sys_language_en_us` VALUES (1086,'Max number of COOKIE');
INSERT INTO `sys_language_en_us` VALUES (1087,'Is Ip Black');
INSERT INTO `sys_language_en_us` VALUES (1088,'Is Domain Black');
INSERT INTO `sys_language_en_us` VALUES (1089,'Confirm password');
INSERT INTO `sys_language_en_us` VALUES (1090,'Source IP');
INSERT INTO `sys_language_en_us` VALUES (1091,'Target IP');
INSERT INTO `sys_language_en_us` VALUES (1092,'Site name');
INSERT INTO `sys_language_en_us` VALUES (1093,'Site IP');
INSERT INTO `sys_language_en_us` VALUES (1094,'Site port');
INSERT INTO `sys_language_en_us` VALUES (1095,'Site group ID');
INSERT INTO `sys_language_en_us` VALUES (1096,'Policy template ID');
INSERT INTO `sys_language_en_us` VALUES (1097,'Self policy template ID');
INSERT INTO `sys_language_en_us` VALUES (1098,'Max traffic module per hour in 24 hours');
INSERT INTO `sys_language_en_us` VALUES (1099,'Max visit of single IP per hour in 24 hours');
INSERT INTO `sys_language_en_us` VALUES (1100,'Start time of 24-hour modeling');
INSERT INTO `sys_language_en_us` VALUES (1101,'Time cycle of modeling');
INSERT INTO `sys_language_en_us` VALUES (1102,'Time to end modeling');
INSERT INTO `sys_language_en_us` VALUES (1103,'Modeling state');
INSERT INTO `sys_language_en_us` VALUES (1104,'Time to learn');
INSERT INTO `sys_language_en_us` VALUES (1105,'Time to start learning');
INSERT INTO `sys_language_en_us` VALUES (1106,'Time to stop learning');
INSERT INTO `sys_language_en_us` VALUES (1107,'Note for dynamic modeling');
INSERT INTO `sys_language_en_us` VALUES (1108,'Whether it is reverse proxy');
INSERT INTO `sys_language_en_us` VALUES (1109,'DDOS attack prevention type');
INSERT INTO `sys_language_en_us` VALUES (1110,'Load balance way');
INSERT INTO `sys_language_en_us` VALUES (1111,'Enable cache');
INSERT INTO `sys_language_en_us` VALUES (1112,'Enbale health check');
INSERT INTO `sys_language_en_us` VALUES (1113,'Certificate public key');
INSERT INTO `sys_language_en_us` VALUES (1114,'Certificate secret key');
INSERT INTO `sys_language_en_us` VALUES (1115,'Instruction of reverse proxy');
INSERT INTO `sys_language_en_us` VALUES (1116,'IP address');
INSERT INTO `sys_language_en_us` VALUES (1117,'Creation time');
INSERT INTO `sys_language_en_us` VALUES (1118,'Site ID');
INSERT INTO `sys_language_en_us` VALUES (1119,'Weight');
INSERT INTO `sys_language_en_us` VALUES (1120,'Uri');
INSERT INTO `sys_language_en_us` VALUES (1122,'Whether it is used for management');
INSERT INTO `sys_language_en_us` VALUES (1123,'Whether to allow ping');
INSERT INTO `sys_language_en_us` VALUES (1124,'Whether to allow traceroute');
INSERT INTO `sys_language_en_us` VALUES (1125,'Whether to enable log');
INSERT INTO `sys_language_en_us` VALUES (1126,'Whether to SSH');
INSERT INTO `sys_language_en_us` VALUES (1127,'Whether to WEBUI');
INSERT INTO `sys_language_en_us` VALUES (1128,'Password and confirmed password are inconsistent');
INSERT INTO `sys_language_en_us` VALUES (1129,'Password must contain letter and digit');
INSERT INTO `sys_language_en_us` VALUES (1130,'Succeed');
INSERT INTO `sys_language_en_us` VALUES (1131,'100%');
INSERT INTO `sys_language_en_us` VALUES (1132,'Allow');
INSERT INTO `sys_language_en_us` VALUES (1133,'Disable');
INSERT INTO `sys_language_en_us` VALUES (1134,'No');
INSERT INTO `sys_language_en_us` VALUES (1135,'Month of the year');
INSERT INTO `sys_language_en_us` VALUES (1136,'Day');
INSERT INTO `sys_language_en_us` VALUES (1137,'Undefined');
INSERT INTO `sys_language_en_us` VALUES (1138,'Sequence number');
INSERT INTO `sys_language_en_us` VALUES (1139,'Times');
INSERT INTO `sys_language_en_us` VALUES (1140,'Source IP');
INSERT INTO `sys_language_en_us` VALUES (1141,'Proportion');
INSERT INTO `sys_language_en_us` VALUES (1142,'Website');
INSERT INTO `sys_language_en_us` VALUES (1143,'Key word');
INSERT INTO `sys_language_en_us` VALUES (1144,'Browser');
INSERT INTO `sys_language_en_us` VALUES (1145,'Browse');
INSERT INTO `sys_language_en_us` VALUES (1146,'Automatic');
INSERT INTO `sys_language_en_us` VALUES (1147,'Engine parameter error');
INSERT INTO `sys_language_en_us` VALUES (1148,'Blocking way parameter error');
INSERT INTO `sys_language_en_us` VALUES (1149,'URL address has not been input');
INSERT INTO `sys_language_en_us` VALUES (1150,'Select arbitrary URL and source IP must be specified');
INSERT INTO `sys_language_en_us` VALUES (1151,'Please fill in source IP');
INSERT INTO `sys_language_en_us` VALUES (1152,'Please fill in target IP');
INSERT INTO `sys_language_en_us` VALUES (1153,'Option error between arbitrary URL and specified URL');
INSERT INTO `sys_language_en_us` VALUES (1154,'Whether to enable parameter error');
INSERT INTO `sys_language_en_us` VALUES (1155,'Select data of one row?');
INSERT INTO `sys_language_en_us` VALUES (1156,'Select enabled data');
INSERT INTO `sys_language_en_us` VALUES (1157,'Whether to enable data');
INSERT INTO `sys_language_en_us` VALUES (1158,'Select disabled data');
INSERT INTO `sys_language_en_us` VALUES (1159,'Whether to diasble data');
INSERT INTO `sys_language_en_us` VALUES (1160,'Select deleted data');
INSERT INTO `sys_language_en_us` VALUES (1161,'Whether to delete data');
INSERT INTO `sys_language_en_us` VALUES (1162,'Basic infomration of rule');
INSERT INTO `sys_language_en_us` VALUES (1163,'Arbitrary URL');
INSERT INTO `sys_language_en_us` VALUES (1164,'Specified URL');
INSERT INTO `sys_language_en_us` VALUES (1165,'Eg');
INSERT INTO `sys_language_en_us` VALUES (1166,'Or');
INSERT INTO `sys_language_en_us` VALUES (1167,'Source config');
INSERT INTO `sys_language_en_us` VALUES (1168,'Arbitrary IP');
INSERT INTO `sys_language_en_us` VALUES (1169,'Specified IP');
INSERT INTO `sys_language_en_us` VALUES (1170,'Single IP');
INSERT INTO `sys_language_en_us` VALUES (1171,'IP section');
INSERT INTO `sys_language_en_us` VALUES (1172,'Target config');
INSERT INTO `sys_language_en_us` VALUES (1173,'Writing in config file failed');
INSERT INTO `sys_language_en_us` VALUES (1174,'After opening BYPASS, each pair of WAN/LAN interface will be connected physically, traffic will not pass through device and it is usually used to eliminate network breakdown');
INSERT INTO `sys_language_en_us` VALUES (1175,'After closing BYPASS, traffic will pass through device and restore to normal state');
INSERT INTO `sys_language_en_us` VALUES (1176,'Please select');
INSERT INTO `sys_language_en_us` VALUES (1177,'HTTP type');
INSERT INTO `sys_language_en_us` VALUES (1178,'Rule module');
INSERT INTO `sys_language_en_us` VALUES (1179,'Priority scope is %s');
INSERT INTO `sys_language_en_us` VALUES (1180,'Anti overflow config');
INSERT INTO `sys_language_en_us` VALUES (1181,'Other patterns');
INSERT INTO `sys_language_en_us` VALUES (1182,'Transparent bridge pattern');
INSERT INTO `sys_language_en_us` VALUES (1183,'Reverse proxy pattern');
INSERT INTO `sys_language_en_us` VALUES (1184,'You haven\'t selected data that needs to add anti false positive');
INSERT INTO `sys_language_en_us` VALUES (1185,'Action successfully, and %d logs that match conditions of false positive in total have been processed successfully and %d logs failed');
INSERT INTO `sys_language_en_us` VALUES (1186,'Select add data of anti false positive');
INSERT INTO `sys_language_en_us` VALUES (1187,'Whether to add anti false positive');
INSERT INTO `sys_language_en_us` VALUES (1188,'Disabled corresponding rule data isn\'t filled');
INSERT INTO `sys_language_en_us` VALUES (1189,'Whether to diasble corresponding rule');
INSERT INTO `sys_language_en_us` VALUES (1190,'Alert config');
INSERT INTO `sys_language_en_us` VALUES (1191,'SMTP server address is invalid');
INSERT INTO `sys_language_en_us` VALUES (1192,'Sender\'s name is not login account');
INSERT INTO `sys_language_en_us` VALUES (1193,'Enable the disabled parameter error');
INSERT INTO `sys_language_en_us` VALUES (1194,'Open state');
INSERT INTO `sys_language_en_us` VALUES (1195,'Use \"|\"to separate URL');
INSERT INTO `sys_language_en_us` VALUES (1196,'Use \"|\"to separate extension name');
INSERT INTO `sys_language_en_us` VALUES (1197,'Block extension name');
INSERT INTO `sys_language_en_us` VALUES (1198,'Blocking word');
INSERT INTO `sys_language_en_us` VALUES (1199,'Blacklist and white list');
INSERT INTO `sys_language_en_us` VALUES (1200,'Round Robin');
INSERT INTO `sys_language_en_us` VALUES (1201,'IP hash');
INSERT INTO `sys_language_en_us` VALUES (1202,'Illegal external connection config');
INSERT INTO `sys_language_en_us` VALUES (1203,'What is beyond specified scope will be prohibited');
INSERT INTO `sys_language_en_us` VALUES (1204,'Visit official website of CloudFence http//www.cloudfence.cn -->Register an account-->Write down correct email address and password-->Check email to find the verification mail and click it to complete registration');
INSERT INTO `sys_language_en_us` VALUES (1205,'Log in-->Add guide-->Write down domain name-->Scan record A of the domain name you add-->Click confirm and return to user interface-->Wait for administrator to verify whether the domain name you add is put on record');
INSERT INTO `sys_language_en_us` VALUES (1206,'Verification passed-->Check email to acquire CNAME record-->Log in backstage of domain name registrar to change your CNAME-->Wait for your change to take effect');
INSERT INTO `sys_language_en_us` VALUES (1207,'Verification not passed-->Go to Ministry of Industry and Information ICP/IP address/Domain name information record management system \"http//www.miitbeian.gov.cn to apply for records');
INSERT INTO `sys_language_en_us` VALUES (1208,'Host header name');
INSERT INTO `sys_language_en_us` VALUES (1209,'Host header name must be filled');
INSERT INTO `sys_language_en_us` VALUES (1210,'Load balance way is incorrect');
INSERT INTO `sys_language_en_us` VALUES (1211,'Whether to open cache');
INSERT INTO `sys_language_en_us` VALUES (1212,'Whether to enable health examination');
INSERT INTO `sys_language_en_us` VALUES (1213,'Local monitoring port');
INSERT INTO `sys_language_en_us` VALUES (1214,'Local monitoring port error');
INSERT INTO `sys_language_en_us` VALUES (1215,'Protocol error');
INSERT INTO `sys_language_en_us` VALUES (1216,'Host header name already exists, and please delete it at site group management');
INSERT INTO `sys_language_en_us` VALUES (1217,'Proxy IP and port');
INSERT INTO `sys_language_en_us` VALUES (1218,'Proxy IP and port must be filled');
INSERT INTO `sys_language_en_us` VALUES (1219,'Proxy IP error');
INSERT INTO `sys_language_en_us` VALUES (1220,'Proxy port error');
INSERT INTO `sys_language_en_us` VALUES (1221,'Proxy weight error');
INSERT INTO `sys_language_en_us` VALUES (1222,'Clearing old proxy IP and port failed');
INSERT INTO `sys_language_en_us` VALUES (1223,'Device name');
INSERT INTO `sys_language_en_us` VALUES (1224,'IP address/mask');
INSERT INTO `sys_language_en_us` VALUES (1225,'Binding interface list');
INSERT INTO `sys_language_en_us` VALUES (1226,'Please write down IP address or don\'t select WEBUI, SSH, ALLOW PING, ALLOW Traceroute');
INSERT INTO `sys_language_en_us` VALUES (1227,'The number of ports you select must exceed 2 (include 2)');
INSERT INTO `sys_language_en_us` VALUES (1228,'Empty data');
INSERT INTO `sys_language_en_us` VALUES (1229,'IPV4 format error');
INSERT INTO `sys_language_en_us` VALUES (1230,'Mask format error');
INSERT INTO `sys_language_en_us` VALUES (1231,'Please input correct IP address');
INSERT INTO `sys_language_en_us` VALUES (1232,'IPV6 format error');
INSERT INTO `sys_language_en_us` VALUES (1233,'Weight value scope is 1 to 10, the bigger the value, the greater the weight');
INSERT INTO `sys_language_en_us` VALUES (1234,'IP address, port and weight must be filled');
INSERT INTO `sys_language_en_us` VALUES (1235,'Bridge interface name');
INSERT INTO `sys_language_en_us` VALUES (1236,'Optional binding device list');
INSERT INTO `sys_language_en_us` VALUES (1237,'Please write down several IP in separate lines');
INSERT INTO `sys_language_en_us` VALUES (1238,'Inherit template ID');
INSERT INTO `sys_language_en_us` VALUES (1239,'The smaller the value, the higher the priority');
INSERT INTO `sys_language_en_us` VALUES (1240,'HTTP request type');
INSERT INTO `sys_language_en_us` VALUES (1241,'Feature generation');
INSERT INTO `sys_language_en_us` VALUES (1242,'Matching algorithm');
INSERT INTO `sys_language_en_us` VALUES (1243,'Charatcer string matching');
INSERT INTO `sys_language_en_us` VALUES (1244,'Regular expression matching');
INSERT INTO `sys_language_en_us` VALUES (1245,'Feature key words');
INSERT INTO `sys_language_en_us` VALUES (1246,'Kind tips');
INSERT INTO `sys_language_en_us` VALUES (1247,'Please ensure that what you input is correct, otherwise, the rule might not be executed');
INSERT INTO `sys_language_en_us` VALUES (1248,'Above');
INSERT INTO `sys_language_en_us` VALUES (1249,'Google crawler');
INSERT INTO `sys_language_en_us` VALUES (1250,'Baidu crawler');
INSERT INTO `sys_language_en_us` VALUES (1251,'Yahoo crawler');
INSERT INTO `sys_language_en_us` VALUES (1252,'Sina crawler');
INSERT INTO `sys_language_en_us` VALUES (1253,'Netease crawler');
INSERT INTO `sys_language_en_us` VALUES (1254,'MSN crawler');
INSERT INTO `sys_language_en_us` VALUES (1255,'Bing crawler');
INSERT INTO `sys_language_en_us` VALUES (1256,'SOSO crawler');
INSERT INTO `sys_language_en_us` VALUES (1257,'360 crawler');
INSERT INTO `sys_language_en_us` VALUES (1258,'Jike crawler');
INSERT INTO `sys_language_en_us` VALUES (1259,'East.net');
INSERT INTO `sys_language_en_us` VALUES (1260,'Hot crawler');
INSERT INTO `sys_language_en_us` VALUES (1261,'Huawei Symantec');
INSERT INTO `sys_language_en_us` VALUES (1262,'British crawler');
INSERT INTO `sys_language_en_us` VALUES (1263,'Russian crawler');
INSERT INTO `sys_language_en_us` VALUES (1264,'South Korean crawler');
INSERT INTO `sys_language_en_us` VALUES (1265,'Japanese crawler');
INSERT INTO `sys_language_en_us` VALUES (1266,'Other crawler');
INSERT INTO `sys_language_en_us` VALUES (1267,'Username or password is wrong, and you have %s of login left');
INSERT INTO `sys_language_en_us` VALUES (1268,'Completion time');
INSERT INTO `sys_language_en_us` VALUES (1269,'Affiliated site group');
INSERT INTO `sys_language_en_us` VALUES (1270,'Modify server');
INSERT INTO `sys_language_en_us` VALUES (1271,'Rule template ID');
INSERT INTO `sys_language_en_us` VALUES (1272,'Among selected site, there is reverse proxy site, which cannot be deleted');
INSERT INTO `sys_language_en_us` VALUES (1273,'Deleting data failed');
INSERT INTO `sys_language_en_us` VALUES (1274,'Submitted data cannot be empty');
INSERT INTO `sys_language_en_us` VALUES (1275,'IP address and port');
INSERT INTO `sys_language_en_us` VALUES (1276,'Select year and month');
INSERT INTO `sys_language_en_us` VALUES (1277,'Select year, month and day');
INSERT INTO `sys_language_en_us` VALUES (1278,'Export format');
INSERT INTO `sys_language_en_us` VALUES (1279,'Report is generated and please click relevant link to download');
INSERT INTO `sys_language_en_us` VALUES (1280,'Time(hour)');
INSERT INTO `sys_language_en_us` VALUES (1281,'Event times');
INSERT INTO `sys_language_en_us` VALUES (1282,'URL/IP address');
INSERT INTO `sys_language_en_us` VALUES (1283,'Invalid parameter');
INSERT INTO `sys_language_en_us` VALUES (1284,'Report is generated');
INSERT INTO `sys_language_en_us` VALUES (1285,'Bluedon WAF attack report');
INSERT INTO `sys_language_en_us` VALUES (1286,'Bluedon WAF access report');
INSERT INTO `sys_language_en_us` VALUES (1287,'Statistical time period');
INSERT INTO `sys_language_en_us` VALUES (1288,'Generated time of report');
INSERT INTO `sys_language_en_us` VALUES (1289,'Manage interface address');
INSERT INTO `sys_language_en_us` VALUES (1290,'Report content:Intrusion record statistics');
INSERT INTO `sys_language_en_us` VALUES (1291,'Statistical graph of intrusion quantity-- aggregate');
INSERT INTO `sys_language_en_us` VALUES (1292,'Intrusion trend graph');
INSERT INTO `sys_language_en_us` VALUES (1293,'Intrusion trend graph(24 hours)');
INSERT INTO `sys_language_en_us` VALUES (1294,'Statistical graph of intrusion type');
INSERT INTO `sys_language_en_us` VALUES (1295,'Comparison graph of intrusion type');
INSERT INTO `sys_language_en_us` VALUES (1296,'Statistics of intrusion quantity');
INSERT INTO `sys_language_en_us` VALUES (1297,'Intrusion trend');
INSERT INTO `sys_language_en_us` VALUES (1298,'Statistics of intrusion type');
INSERT INTO `sys_language_en_us` VALUES (1299,'Comparison of intrusion type');
INSERT INTO `sys_language_en_us` VALUES (1300,'Statistics of intrusion source address');
INSERT INTO `sys_language_en_us` VALUES (1301,'Statistics of intrusion source of attack event');
INSERT INTO `sys_language_en_us` VALUES (1302,'Statistics of attack event of intrusion source type');
INSERT INTO `sys_language_en_us` VALUES (1303,'Statistics of attack type based on attacked host');
INSERT INTO `sys_language_en_us` VALUES (1304,'Statistics of attack type of attacked host');
INSERT INTO `sys_language_en_us` VALUES (1305,'Statistics of attack type based on attacked URL');
INSERT INTO `sys_language_en_us` VALUES (1306,'Statistics of attack type of attacked URL');
INSERT INTO `sys_language_en_us` VALUES (1307,'Statistics of attacked host');
INSERT INTO `sys_language_en_us` VALUES (1308,'Statistics of attacked URL');
INSERT INTO `sys_language_en_us` VALUES (1309,'Statistics of attacked URL(contain parameter)');
INSERT INTO `sys_language_en_us` VALUES (1310,'Generate real-time report(In checking HTML report, it is suggested to use such browser as IE10 or higher version/Firefox/Chrome)');
INSERT INTO `sys_language_en_us` VALUES (1311,'Report date');
INSERT INTO `sys_language_en_us` VALUES (1312,'Download report');
INSERT INTO `sys_language_en_us` VALUES (1313,'Preview report');
INSERT INTO `sys_language_en_us` VALUES (1314,'Generate report');
INSERT INTO `sys_language_en_us` VALUES (1315,'It is generating report, please wait…');
INSERT INTO `sys_language_en_us` VALUES (1316,'HTML format');
INSERT INTO `sys_language_en_us` VALUES (1317,'PDF format');
INSERT INTO `sys_language_en_us` VALUES (1318,'DOC format');
INSERT INTO `sys_language_en_us` VALUES (1319,'Please input positive integer');
INSERT INTO `sys_language_en_us` VALUES (1320,'Please fill in as required');
INSERT INTO `sys_language_en_us` VALUES (1321,'Please select searching date');
INSERT INTO `sys_language_en_us` VALUES (1322,'Protection website');
INSERT INTO `sys_language_en_us` VALUES (1323,'Analysis of security statistics');
INSERT INTO `sys_language_en_us` VALUES (1324,'Time duration that user stay on your website');
INSERT INTO `sys_language_en_us` VALUES (1325,'Crawler analysis');
INSERT INTO `sys_language_en_us` VALUES (1326,'Crawler');
INSERT INTO `sys_language_en_us` VALUES (1327,'Website traffic(by day)');
INSERT INTO `sys_language_en_us` VALUES (1328,'Network interface');
INSERT INTO `sys_language_en_us` VALUES (1329,'Receive data packet');
INSERT INTO `sys_language_en_us` VALUES (1330,'Send data packet');
INSERT INTO `sys_language_en_us` VALUES (1331,'Receive byte');
INSERT INTO `sys_language_en_us` VALUES (1332,'Send byte');
INSERT INTO `sys_language_en_us` VALUES (1333,'Received wrong packet');
INSERT INTO `sys_language_en_us` VALUES (1334,'Sent wrong packet');
INSERT INTO `sys_language_en_us` VALUES (1335,'Receive lost');
INSERT INTO `sys_language_en_us` VALUES (1336,'Send lost');
INSERT INTO `sys_language_en_us` VALUES (1337,'Visit times of webiste entry page');
INSERT INTO `sys_language_en_us` VALUES (1338,'Visit times of webiste exit page');
INSERT INTO `sys_language_en_us` VALUES (1339,'Accessed page');
INSERT INTO `sys_language_en_us` VALUES (1340,'Rank of accessed page');
INSERT INTO `sys_language_en_us` VALUES (1341,'Error code ranking');
INSERT INTO `sys_language_en_us` VALUES (1342,'Error code');
INSERT INTO `sys_language_en_us` VALUES (1343,'Search engine');
INSERT INTO `sys_language_en_us` VALUES (1344,'Search key words');
INSERT INTO `sys_language_en_us` VALUES (1345,'Access to my website from search engine');
INSERT INTO `sys_language_en_us` VALUES (1346,'Access to my website from other websites');
INSERT INTO `sys_language_en_us` VALUES (1347,'What OS is user using?');
INSERT INTO `sys_language_en_us` VALUES (1348,'What browser is user using?');
INSERT INTO `sys_language_en_us` VALUES (1349,'Stay time of user');
INSERT INTO `sys_language_en_us` VALUES (1350,'Total PV');
INSERT INTO `sys_language_en_us` VALUES (1351,'Visit times');
INSERT INTO `sys_language_en_us` VALUES (1352,'Number of traffic');
INSERT INTO `sys_language_en_us` VALUES (1353,'Half-duplex');
INSERT INTO `sys_language_en_us` VALUES (1354,'Full duplex');
INSERT INTO `sys_language_en_us` VALUES (1355,'Connected');
INSERT INTO `sys_language_en_us` VALUES (1356,'Not connected');
INSERT INTO `sys_language_en_us` VALUES (1357,'Input ID');
INSERT INTO `sys_language_en_us` VALUES (1358,'Rule instruction');
INSERT INTO `sys_language_en_us` VALUES (1359,'Add successfully');
INSERT INTO `sys_language_en_us` VALUES (1360,'Uploading failed');
INSERT INTO `sys_language_en_us` VALUES (1364,'Mideum risk');
INSERT INTO `sys_language_en_us` VALUES (1365,'Low risk');
INSERT INTO `sys_language_en_us` VALUES (1366,'High risk');
INSERT INTO `sys_language_en_us` VALUES (1367,'Enabled state');
INSERT INTO `sys_language_en_us` VALUES (1368,'HTTP data type');
INSERT INTO `sys_language_en_us` VALUES (1369,'Tip type');
INSERT INTO `sys_language_en_us` VALUES (1370,'User-defined file');
INSERT INTO `sys_language_en_us` VALUES (1371,'State of taking effect');
INSERT INTO `sys_language_en_us` VALUES (1372,'Block URL');
INSERT INTO `sys_language_en_us` VALUES (1373,'website_id');
INSERT INTO `sys_language_en_us` VALUES (1374,'Policy content');
INSERT INTO `sys_language_en_us` VALUES (1375,'Enabled state of site group');
INSERT INTO `sys_language_en_us` VALUES (1376,'Attack type');
INSERT INTO `sys_language_en_us` VALUES (1377,'Severity');
INSERT INTO `sys_language_en_us` VALUES (1378,'Scanning state');
INSERT INTO `sys_language_en_us` VALUES (1379,'Scanning result');
INSERT INTO `sys_language_en_us` VALUES (1380,'Enabling state of sensitive word filtering');
INSERT INTO `sys_language_en_us` VALUES (1381,'State of interlligent blocking');
INSERT INTO `sys_language_en_us` VALUES (1382,'Enbaled state of Bypass');
INSERT INTO `sys_language_en_us` VALUES (1383,'Monitor target URL');
INSERT INTO `sys_language_en_us` VALUES (1384,'Protype');
INSERT INTO `sys_language_en_us` VALUES (1385,'Freq');
INSERT INTO `sys_language_en_us` VALUES (1386,'System\'s default language');
INSERT INTO `sys_language_en_us` VALUES (1387,'Firewall role');
INSERT INTO `sys_language_en_us` VALUES (1388,'AuditLogUniqueID');
INSERT INTO `sys_language_en_us` VALUES (1389,'UserAgent');
INSERT INTO `sys_language_en_us` VALUES (1390,'HTTP request way');
INSERT INTO `sys_language_en_us` VALUES (1391,'Request type');
INSERT INTO `sys_language_en_us` VALUES (1392,'Response type');
INSERT INTO `sys_language_en_us` VALUES (1393,'Request status code');
INSERT INTO `sys_language_en_us` VALUES (1394,'GeneralMsg');
INSERT INTO `sys_language_en_us` VALUES (1395,'Rule file');
INSERT INTO `sys_language_en_us` VALUES (1396,'Aggregate');
INSERT INTO `sys_language_en_us` VALUES (1397,'Default value');
INSERT INTO `sys_language_en_us` VALUES (1398,'Scope');
INSERT INTO `sys_language_en_us` VALUES (1399,'Pattern source');
INSERT INTO `sys_language_en_us` VALUES (1400,'Template cannot be found in rule template library');
INSERT INTO `sys_language_en_us` VALUES (1401,'The template that is being used cannot be deleted');
INSERT INTO `sys_language_en_us` VALUES (1402,'Action failed');
INSERT INTO `sys_language_en_us` VALUES (1403,'Shutdown and restart');
INSERT INTO `sys_language_en_us` VALUES (1404,'Symbol');
INSERT INTO `sys_language_en_us` VALUES (1405,'Field Desc');
INSERT INTO `sys_language_en_us` VALUES (1406,'Json');
INSERT INTO `sys_language_en_us` VALUES (1407,'Version');
INSERT INTO `sys_language_en_us` VALUES (1408,'Contact');
INSERT INTO `sys_language_en_us` VALUES (1409,'Block');
INSERT INTO `sys_language_en_us` VALUES (1410,'Protected URL');
INSERT INTO `sys_language_en_us` VALUES (1411,'Max file size');
INSERT INTO `sys_language_en_us` VALUES (1412,'Block extension time');
INSERT INTO `sys_language_en_us` VALUES (1413,'DestinationIP');
INSERT INTO `sys_language_en_us` VALUES (1416,'RequestContentType');
INSERT INTO `sys_language_en_us` VALUES (1417,'ResponseContentType');
INSERT INTO `sys_language_en_us` VALUES (1418,'HttpStatusCode');
INSERT INTO `sys_language_en_us` VALUES (1420,'Whether it is virus');
INSERT INTO `sys_language_en_us` VALUES (1421,'Result of check');
INSERT INTO `sys_language_en_us` VALUES (1422,'Number');
INSERT INTO `sys_language_en_us` VALUES (1423,'The username must only contain digits and letters');
INSERT INTO `sys_language_en_us` VALUES (1424,'Rescan will clear the original task data. Are you sure to continue?');
INSERT INTO `sys_language_en_us` VALUES (1425,'Welcome');
INSERT INTO `sys_language_en_us` VALUES (1426,'Check the login status');
INSERT INTO `sys_language_en_us` VALUES (1427,'syslog server');
INSERT INTO `sys_language_en_us` VALUES (1428,'Email testing');
INSERT INTO `sys_language_en_us` VALUES (1429,'Logs archive');
INSERT INTO `sys_language_en_us` VALUES (1430,'Initialize');
INSERT INTO `sys_language_en_us` VALUES (1431,'WAF account sync');
INSERT INTO `sys_language_en_us` VALUES (1432,'Enable gateway Email');
INSERT INTO `sys_language_en_us` VALUES (1433,'启用手机报警开关');
INSERT INTO `sys_language_en_us` VALUES (1434,'Configuration item name');
INSERT INTO `sys_language_en_us` VALUES (1435,'Configuration item value');
INSERT INTO `sys_language_en_us` VALUES (1436,'Interface command');
INSERT INTO `sys_language_en_us` VALUES (1437,'Import');
INSERT INTO `sys_language_en_us` VALUES (1438,'Enable phone alert');
INSERT INTO `sys_language_en_us` VALUES (1439,'Login timeout');
INSERT INTO `sys_language_en_us` VALUES (1440,'System homepage');
INSERT INTO `sys_language_en_us` VALUES (1441,'Super admin');
INSERT INTO `sys_language_en_us` VALUES (1442,'System admin');
INSERT INTO `sys_language_en_us` VALUES (1443,'Security admin');
INSERT INTO `sys_language_en_us` VALUES (1444,'Security auditor');
INSERT INTO `sys_language_en_us` VALUES (1445,'Notification');
INSERT INTO `sys_language_en_us` VALUES (1446,'Information');
INSERT INTO `sys_language_en_us` VALUES (1447,'Debug');
INSERT INTO `sys_language_en_us` VALUES (1448,'DDOS log');
INSERT INTO `sys_language_en_us` VALUES (1449,'CC log');
INSERT INTO `sys_language_en_us` VALUES (1450,'Intelligent file log upload');
INSERT INTO `sys_language_en_us` VALUES (1451,'Account management');
INSERT INTO `sys_language_en_us` VALUES (1452,'Update status');
INSERT INTO `sys_language_en_us` VALUES (1453,'Rule copy');
INSERT INTO `sys_language_en_us` VALUES (1454,'Preset rule template');
INSERT INTO `sys_language_en_us` VALUES (1455,'Customized rule template');
INSERT INTO `sys_language_en_us` VALUES (1456,'IP filtering config');
INSERT INTO `sys_language_en_us` VALUES (1457,'Intelligent malware detection');
INSERT INTO `sys_language_en_us` VALUES (1458,'Disable requested file suffix （Requested types of file suffix will be disabled after enabling this function. ）');
INSERT INTO `sys_language_en_us` VALUES (1459,'Block extension name');
INSERT INTO `sys_language_en_us` VALUES (1460,'File size');
INSERT INTO `sys_language_en_us` VALUES (1461,'Imported time');
INSERT INTO `sys_language_en_us` VALUES (1462,'Filtered IP/IP segment');
INSERT INTO `sys_language_en_us` VALUES (1463,'Policy name');
INSERT INTO `sys_language_en_us` VALUES (1464,'Target URL');
INSERT INTO `sys_language_en_us` VALUES (1465,'Preset policy');
INSERT INTO `sys_language_en_us` VALUES (1466,'Single user login limits');
INSERT INTO `sys_language_en_us` VALUES (1467,'User Agent');
INSERT INTO `sys_language_en_us` VALUES (1468,'Http Method');
INSERT INTO `sys_language_en_us` VALUES (1469,'Http Protocol');
INSERT INTO `sys_language_en_us` VALUES (1470,'Rule ID');
INSERT INTO `sys_language_en_us` VALUES (1471,'Download location');
INSERT INTO `sys_language_en_us` VALUES (1472,'Uploaded file ID');
INSERT INTO `sys_language_en_us` VALUES (1473,'Detection result');
INSERT INTO `sys_language_en_us` VALUES (1474,'Copy');
INSERT INTO `sys_language_en_us` VALUES (1475,'Enable rule');
INSERT INTO `sys_language_en_us` VALUES (1476,'Disable rule');
INSERT INTO `sys_language_en_us` VALUES (1477,'IP filtering only takes effect when the bride mode is deployed.');
INSERT INTO `sys_language_en_us` VALUES (1478,'If IP filter is disabled, all requests will be filtered; If IP filter is enabled, only requests with source IP or target IP that fit the setting will be filtered.');
INSERT INTO `sys_language_en_us` VALUES (1479,'Please separate filtered IP/IP segment by \"|\"');
INSERT INTO `sys_language_en_us` VALUES (1480,'It will clear all the data which can not be restored. Continue?');
INSERT INTO `sys_language_en_us` VALUES (1481,'Unclassified site can not be deleted');
INSERT INTO `sys_language_en_us` VALUES (1482,'Hostname should be IPV4 or valid domain name');
INSERT INTO `sys_language_en_us` VALUES (1483,'The format of IP, IP segment, or IP+mask are allowed. The format of IP segment is: ip-ip, e.g. 192.168.1.1-192.168.4.254; the format of IP + Mask is: IP/Mask, e.g.192.168.1.0/24');
INSERT INTO `sys_language_en_us` VALUES (1484,'Preset template');
INSERT INTO `sys_language_en_us` VALUES (1485,'Enable');
INSERT INTO `sys_language_en_us` VALUES (1486,'Notes: Only one of the preset rule templates can be enabled. Selecting \"Strict\" template may cause redundant report, while selecting \"Tolerant\" template may cause false negative.');
INSERT INTO `sys_language_en_us` VALUES (1487,'No template is selected for reset');
INSERT INTO `sys_language_en_us` VALUES (1488,'Please select rule template which needs to be reset');
INSERT INTO `sys_language_en_us` VALUES (1489,'Confirm to reset the selected template?');
INSERT INTO `sys_language_en_us` VALUES (1490,'This item does not take effect when the template of site group is selected.');
INSERT INTO `sys_language_en_us` VALUES (1491,'Uplink');
INSERT INTO `sys_language_en_us` VALUES (1492,'Downlink');
INSERT INTO `sys_language_en_us` VALUES (1493,'Memory');
INSERT INTO `sys_language_en_us` VALUES (1494,'Disk');
INSERT INTO `sys_language_en_us` VALUES (1495,'Current preset rule template name');
INSERT INTO `sys_language_en_us` VALUES (1496,'Upload is not allowed');
INSERT INTO `sys_language_en_us` VALUES (1497,'Keyword alert');
INSERT INTO `sys_language_en_us` VALUES (1498,'Can not select more than two devices');
INSERT INTO `sys_language_en_us` VALUES (1499,'Total {total},  Display {pagesize} per page');
INSERT INTO `sys_language_en_us` VALUES (1500,'Files can not be larger than %sM');
/*!40000 ALTER TABLE `sys_language_en_us` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_language_source`
--

DROP TABLE IF EXISTS `sys_language_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_language_source` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `title` char(255) DEFAULT '' COMMENT '标题',
  `is_use` char(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uidx_title` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=1501 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_language_source`
--

LOCK TABLES `sys_language_source` WRITE;
/*!40000 ALTER TABLE `sys_language_source` DISABLE KEYS */;
INSERT INTO `sys_language_source` VALUES (1,'更新','1');
INSERT INTO `sys_language_source` VALUES (2,'缓存管理','1');
INSERT INTO `sys_language_source` VALUES (3,'添加','1');
INSERT INTO `sys_language_source` VALUES (4,'系统监控','1');
INSERT INTO `sys_language_source` VALUES (5,'查看','1');
INSERT INTO `sys_language_source` VALUES (6,'信息概况','1');
INSERT INTO `sys_language_source` VALUES (7,'网络流量监控','1');
INSERT INTO `sys_language_source` VALUES (8,'设备负载监控','1');
INSERT INTO `sys_language_source` VALUES (9,'删除','1');
INSERT INTO `sys_language_source` VALUES (10,'WEB应用监控','1');
INSERT INTO `sys_language_source` VALUES (12,'修改','1');
INSERT INTO `sys_language_source` VALUES (15,'上传文件','1');
INSERT INTO `sys_language_source` VALUES (18,'修改资料','1');
INSERT INTO `sys_language_source` VALUES (19,'编辑','1');
INSERT INTO `sys_language_source` VALUES (22,'安装库','1');
INSERT INTO `sys_language_source` VALUES (23,'搜索','1');
INSERT INTO `sys_language_source` VALUES (24,'配置表','1');
INSERT INTO `sys_language_source` VALUES (25,'网口配置','1');
INSERT INTO `sys_language_source` VALUES (26,'端口镜像','1');
INSERT INTO `sys_language_source` VALUES (28,'虚拟线','1');
INSERT INTO `sys_language_source` VALUES (30,'拨号设备','1');
INSERT INTO `sys_language_source` VALUES (31,'端口聚合','1');
INSERT INTO `sys_language_source` VALUES (32,'VLAN设备','1');
INSERT INTO `sys_language_source` VALUES (33,'DHCP','1');
INSERT INTO `sys_language_source` VALUES (34,'DNS设置','1');
INSERT INTO `sys_language_source` VALUES (35,'IPV6隧道配置','1');
INSERT INTO `sys_language_source` VALUES (36,'NAT64配置','1');
INSERT INTO `sys_language_source` VALUES (37,'ECMP','1');
INSERT INTO `sys_language_source` VALUES (38,'静态路由','1');
INSERT INTO `sys_language_source` VALUES (39,'WEB站点流量','1');
INSERT INTO `sys_language_source` VALUES (40,'策略路由','1');
INSERT INTO `sys_language_source` VALUES (41,'新建连接数 与 处理事务数','1');
INSERT INTO `sys_language_source` VALUES (42,'ISP路由','1');
INSERT INTO `sys_language_source` VALUES (43,'并发连接数','1');
INSERT INTO `sys_language_source` VALUES (44,'动态路由','1');
INSERT INTO `sys_language_source` VALUES (45,'IP/IP组','1');
INSERT INTO `sys_language_source` VALUES (46,'ISP地址','1');
INSERT INTO `sys_language_source` VALUES (47,'服务/组','1');
INSERT INTO `sys_language_source` VALUES (48,'URL类型组','1');
INSERT INTO `sys_language_source` VALUES (49,'文件类型组','1');
INSERT INTO `sys_language_source` VALUES (50,'时间计划','1');
INSERT INTO `sys_language_source` VALUES (51,'自定义IPS规则库','1');
INSERT INTO `sys_language_source` VALUES (52,'WEB应用防护规则库','1');
INSERT INTO `sys_language_source` VALUES (53,'NAT','1');
INSERT INTO `sys_language_source` VALUES (54,'连接数控制','1');
INSERT INTO `sys_language_source` VALUES (55,'DOS/DDOS防护','1');
INSERT INTO `sys_language_source` VALUES (56,'会话管理','1');
INSERT INTO `sys_language_source` VALUES (57,'会话控制','1');
INSERT INTO `sys_language_source` VALUES (58,'连接排行榜','1');
INSERT INTO `sys_language_source` VALUES (59,'会话状态','1');
INSERT INTO `sys_language_source` VALUES (60,'IP-MAC绑定配置','1');
INSERT INTO `sys_language_source` VALUES (61,'联动','1');
INSERT INTO `sys_language_source` VALUES (62,'URL过滤','1');
INSERT INTO `sys_language_source` VALUES (63,'URL过滤策略','1');
INSERT INTO `sys_language_source` VALUES (64,'URL黑名单','1');
INSERT INTO `sys_language_source` VALUES (65,'URL白名单','1');
INSERT INTO `sys_language_source` VALUES (66,'配置','1');
INSERT INTO `sys_language_source` VALUES (67,'web应用防护','1');
INSERT INTO `sys_language_source` VALUES (68,'病毒防护','1');
INSERT INTO `sys_language_source` VALUES (69,'更新2','1');
INSERT INTO `sys_language_source` VALUES (70,'基本配置','1');
INSERT INTO `sys_language_source` VALUES (71,'防病毒策略设置','1');
INSERT INTO `sys_language_source` VALUES (72,'信息泄漏防护','1');
INSERT INTO `sys_language_source` VALUES (73,'关键词过滤','1');
INSERT INTO `sys_language_source` VALUES (75,'文件过滤','1');
INSERT INTO `sys_language_source` VALUES (76,'标题','1');
INSERT INTO `sys_language_source` VALUES (78,'SSL VPN','1');
INSERT INTO `sys_language_source` VALUES (79,'服务管理','1');
INSERT INTO `sys_language_source` VALUES (80,'用户配置','1');
INSERT INTO `sys_language_source` VALUES (81,'IPSEC VPN','1');
INSERT INTO `sys_language_source` VALUES (82,'本地子网','1');
INSERT INTO `sys_language_source` VALUES (83,'分支对接','1');
INSERT INTO `sys_language_source` VALUES (84,'IPSEC监控管理','1');
INSERT INTO `sys_language_source` VALUES (85,'L2TP VPN','1');
INSERT INTO `sys_language_source` VALUES (86,'下载','1');
INSERT INTO `sys_language_source` VALUES (87,'监控管理','1');
INSERT INTO `sys_language_source` VALUES (88,'首页定制保存','1');
INSERT INTO `sys_language_source` VALUES (89,'虚拟池IP','1');
INSERT INTO `sys_language_source` VALUES (90,'导出','1');
INSERT INTO `sys_language_source` VALUES (91,'NAT 穿越','1');
INSERT INTO `sys_language_source` VALUES (92,'网站访问分析(当月)','1');
INSERT INTO `sys_language_source` VALUES (93,'中心节点','1');
INSERT INTO `sys_language_source` VALUES (94,'边缘节点','1');
INSERT INTO `sys_language_source` VALUES (95,'重新扫描','1');
INSERT INTO `sys_language_source` VALUES (96,'GRE隧道','1');
INSERT INTO `sys_language_source` VALUES (97,'停止','1');
INSERT INTO `sys_language_source` VALUES (98,'虚拟线路','1');
INSERT INTO `sys_language_source` VALUES (99,'通道配置','1');
INSERT INTO `sys_language_source` VALUES (100,'策略自动演进','1');
INSERT INTO `sys_language_source` VALUES (101,'综合分析(按天)','1');
INSERT INTO `sys_language_source` VALUES (102,'蜜罐','1');
INSERT INTO `sys_language_source` VALUES (103,'综合分析(按月)','1');
INSERT INTO `sys_language_source` VALUES (104,'反向拍照','1');
INSERT INTO `sys_language_source` VALUES (105,'防扫描','1');
INSERT INTO `sys_language_source` VALUES (106,'添加黑白名单','1');
INSERT INTO `sys_language_source` VALUES (107,'报表统计','1');
INSERT INTO `sys_language_source` VALUES (108,'管理员帐号','1');
INSERT INTO `sys_language_source` VALUES (109,'系统配置','1');
INSERT INTO `sys_language_source` VALUES (110,'系统维护','1');
INSERT INTO `sys_language_source` VALUES (111,'帮助支持','1');
INSERT INTO `sys_language_source` VALUES (112,'高可用性','1');
INSERT INTO `sys_language_source` VALUES (113,'应急支持','1');
INSERT INTO `sys_language_source` VALUES (115,'攻击报表预览','1');
INSERT INTO `sys_language_source` VALUES (116,'配置管理','1');
INSERT INTO `sys_language_source` VALUES (117,'基本参数设置','1');
INSERT INTO `sys_language_source` VALUES (118,'站点组管理','1');
INSERT INTO `sys_language_source` VALUES (122,'访问流量报表预览','1');
INSERT INTO `sys_language_source` VALUES (129,'访问控制配置开关','1');
INSERT INTO `sys_language_source` VALUES (133,'HA端口及参数配置','1');
INSERT INTO `sys_language_source` VALUES (134,'通知配置','1');
INSERT INTO `sys_language_source` VALUES (135,'规则升级','1');
INSERT INTO `sys_language_source` VALUES (136,'报警设置','1');
INSERT INTO `sys_language_source` VALUES (137,'ssh开关','1');
INSERT INTO `sys_language_source` VALUES (140,'系统升级','1');
INSERT INTO `sys_language_source` VALUES (141,'攻击报表','1');
INSERT INTO `sys_language_source` VALUES (142,'访问流量报表','1');
INSERT INTO `sys_language_source` VALUES (143,'即时报表','1');
INSERT INTO `sys_language_source` VALUES (144,'报表管理','1');
INSERT INTO `sys_language_source` VALUES (145,'规则配置','1');
INSERT INTO `sys_language_source` VALUES (146,'高级设置','1');
INSERT INTO `sys_language_source` VALUES (147,'自学习','1');
INSERT INTO `sys_language_source` VALUES (148,'动态建模','1');
INSERT INTO `sys_language_source` VALUES (149,'非法外联','1');
INSERT INTO `sys_language_source` VALUES (150,'DDOS防护','1');
INSERT INTO `sys_language_source` VALUES (151,'网页防篡改','1');
INSERT INTO `sys_language_source` VALUES (152,'内置规则','1');
INSERT INTO `sys_language_source` VALUES (153,'自定义规则','1');
INSERT INTO `sys_language_source` VALUES (154,'规则模板设置','1');
INSERT INTO `sys_language_source` VALUES (155,'访问控制','1');
INSERT INTO `sys_language_source` VALUES (156,'HTTP防溢出设置','1');
INSERT INTO `sys_language_source` VALUES (157,'HTTP协议版本过滤','1');
INSERT INTO `sys_language_source` VALUES (158,'HTTP头字段设置','1');
INSERT INTO `sys_language_source` VALUES (159,'文件扩展名过滤','1');
INSERT INTO `sys_language_source` VALUES (160,'敏感词过滤设置','1');
INSERT INTO `sys_language_source` VALUES (161,'防盗链设置','1');
INSERT INTO `sys_language_source` VALUES (162,'爬虫防护设置','1');
INSERT INTO `sys_language_source` VALUES (163,'防误报设置','1');
INSERT INTO `sys_language_source` VALUES (164,'自学习设置','1');
INSERT INTO `sys_language_source` VALUES (165,'自学习访问白名单','1');
INSERT INTO `sys_language_source` VALUES (166,'自学习结果','1');
INSERT INTO `sys_language_source` VALUES (167,'非法外联检测','1');
INSERT INTO `sys_language_source` VALUES (168,'非法外联设置','1');
INSERT INTO `sys_language_source` VALUES (169,'智能阻断设置','1');
INSERT INTO `sys_language_source` VALUES (170,'DDOS防护设置','1');
INSERT INTO `sys_language_source` VALUES (171,'CC防护设置','1');
INSERT INTO `sys_language_source` VALUES (172,'可用性监测','1');
INSERT INTO `sys_language_source` VALUES (173,'漏洞扫描','1');
INSERT INTO `sys_language_source` VALUES (174,'返回页面设置','1');
INSERT INTO `sys_language_source` VALUES (175,'上传','1');
INSERT INTO `sys_language_source` VALUES (176,'数据管理','1');
INSERT INTO `sys_language_source` VALUES (177,'组/用户','1');
INSERT INTO `sys_language_source` VALUES (178,'数据管理模型','1');
INSERT INTO `sys_language_source` VALUES (179,'系统','1');
INSERT INTO `sys_language_source` VALUES (180,'数据表','1');
INSERT INTO `sys_language_source` VALUES (181,'网络配置','1');
INSERT INTO `sys_language_source` VALUES (182,'账号管理','1');
INSERT INTO `sys_language_source` VALUES (183,'数据库','1');
INSERT INTO `sys_language_source` VALUES (184,'路由配置','1');
INSERT INTO `sys_language_source` VALUES (185,'对象定义','1');
INSERT INTO `sys_language_source` VALUES (186,'登录配置','1');
INSERT INTO `sys_language_source` VALUES (187,'用户管理','1');
INSERT INTO `sys_language_source` VALUES (188,'虚拟专网','1');
INSERT INTO `sys_language_source` VALUES (189,'流量管理','1');
INSERT INTO `sys_language_source` VALUES (190,'智能防护','1');
INSERT INTO `sys_language_source` VALUES (191,'Action ID','1');
INSERT INTO `sys_language_source` VALUES (192,'Name','1');
INSERT INTO `sys_language_source` VALUES (193,'Desc','1');
INSERT INTO `sys_language_source` VALUES (194,'ID','1');
INSERT INTO `sys_language_source` VALUES (196,'时间','1');
INSERT INTO `sys_language_source` VALUES (199,'排序','1');
INSERT INTO `sys_language_source` VALUES (200,'显示','1');
INSERT INTO `sys_language_source` VALUES (202,'Title','1');
INSERT INTO `sys_language_source` VALUES (212,'Type','1');
INSERT INTO `sys_language_source` VALUES (218,'IP类型','1');
INSERT INTO `sys_language_source` VALUES (219,'IP或IP段','1');
INSERT INTO `sys_language_source` VALUES (220,'类型','1');
INSERT INTO `sys_language_source` VALUES (221,'状态','1');
INSERT INTO `sys_language_source` VALUES (222,'Priority','1');
INSERT INTO `sys_language_source` VALUES (223,'Severity','1');
INSERT INTO `sys_language_source` VALUES (230,'Host','1');
INSERT INTO `sys_language_source` VALUES (231,'Db','1');
INSERT INTO `sys_language_source` VALUES (232,'User','1');
INSERT INTO `sys_language_source` VALUES (233,'Pwd','1');
INSERT INTO `sys_language_source` VALUES (234,'Task ID','1');
INSERT INTO `sys_language_source` VALUES (235,'Parent ID','1');
INSERT INTO `sys_language_source` VALUES (236,'Tb','1');
INSERT INTO `sys_language_source` VALUES (237,'Tb Create','1');
INSERT INTO `sys_language_source` VALUES (238,'Field','1');
INSERT INTO `sys_language_source` VALUES (239,'Field Global Var','1');
INSERT INTO `sys_language_source` VALUES (240,'Field Attribute Label','1');
INSERT INTO `sys_language_source` VALUES (241,'Field Attribute Labels Config','1');
INSERT INTO `sys_language_source` VALUES (242,'Field Rules','1');
INSERT INTO `sys_language_source` VALUES (243,'Field Search','1');
INSERT INTO `sys_language_source` VALUES (244,'Field Search Box','1');
INSERT INTO `sys_language_source` VALUES (245,'Field Table','1');
INSERT INTO `sys_language_source` VALUES (246,'Field Edit','1');
INSERT INTO `sys_language_source` VALUES (247,'Field Data','1');
INSERT INTO `sys_language_source` VALUES (248,'Is Use','1');
INSERT INTO `sys_language_source` VALUES (249,'Interface','1');
INSERT INTO `sys_language_source` VALUES (250,'Vhid','1');
INSERT INTO `sys_language_source` VALUES (251,'Password','1');
INSERT INTO `sys_language_source` VALUES (252,'State','1');
INSERT INTO `sys_language_source` VALUES (253,'Ip','1');
INSERT INTO `sys_language_source` VALUES (254,'Database Ip','1');
INSERT INTO `sys_language_source` VALUES (255,'Database Port','1');
INSERT INTO `sys_language_source` VALUES (256,'Is Setting','1');
INSERT INTO `sys_language_source` VALUES (257,'Server ID','1');
INSERT INTO `sys_language_source` VALUES (258,'Offset ID','1');
INSERT INTO `sys_language_source` VALUES (259,'Had Sync','1');
INSERT INTO `sys_language_source` VALUES (260,'Bridge','1');
INSERT INTO `sys_language_source` VALUES (261,'Is Port Aggregation','1');
INSERT INTO `sys_language_source` VALUES (262,'Database Sync Status','1');
INSERT INTO `sys_language_source` VALUES (272,'Secname','1');
INSERT INTO `sys_language_source` VALUES (277,'报表名称','1');
INSERT INTO `sys_language_source` VALUES (278,'报表类型','1');
INSERT INTO `sys_language_source` VALUES (279,'报表说明','1');
INSERT INTO `sys_language_source` VALUES (280,'生成时间','1');
INSERT INTO `sys_language_source` VALUES (281,'路径','1');
INSERT INTO `sys_language_source` VALUES (282,'报表分类','1');
INSERT INTO `sys_language_source` VALUES (283,'格式','1');
INSERT INTO `sys_language_source` VALUES (284,'说明','1');
INSERT INTO `sys_language_source` VALUES (285,'邮件通知','1');
INSERT INTO `sys_language_source` VALUES (286,'文件格式','1');
INSERT INTO `sys_language_source` VALUES (289,'Different','1');
INSERT INTO `sys_language_source` VALUES (293,'Redirect ID','1');
INSERT INTO `sys_language_source` VALUES (294,'描述','1');
INSERT INTO `sys_language_source` VALUES (295,'链接','1');
INSERT INTO `sys_language_source` VALUES (296,'用户名','1');
INSERT INTO `sys_language_source` VALUES (297,'密码','1');
INSERT INTO `sys_language_source` VALUES (298,'属组','1');
INSERT INTO `sys_language_source` VALUES (299,'可用','1');
INSERT INTO `sys_language_source` VALUES (300,'Group ID','1');
INSERT INTO `sys_language_source` VALUES (301,'Sys Menu ID','1');
INSERT INTO `sys_language_source` VALUES (302,'Enable','1');
INSERT INTO `sys_language_source` VALUES (303,'组别','1');
INSERT INTO `sys_language_source` VALUES (304,'主键id','1');
INSERT INTO `sys_language_source` VALUES (305,'系统配置的键名','1');
INSERT INTO `sys_language_source` VALUES (306,'系统配置的键值','1');
INSERT INTO `sys_language_source` VALUES (307,'系统配置的描述','1');
INSERT INTO `sys_language_source` VALUES (323,'Country Code','1');
INSERT INTO `sys_language_source` VALUES (330,'Referer','1');
INSERT INTO `sys_language_source` VALUES (333,'Url','1');
INSERT INTO `sys_language_source` VALUES (339,'Rulefile','1');
INSERT INTO `sys_language_source` VALUES (341,'Rev','1');
INSERT INTO `sys_language_source` VALUES (343,'Tag','1');
INSERT INTO `sys_language_source` VALUES (344,'Code','1');
INSERT INTO `sys_language_source` VALUES (345,'Province','1');
INSERT INTO `sys_language_source` VALUES (346,'Area','1');
INSERT INTO `sys_language_source` VALUES (347,'En Country','1');
INSERT INTO `sys_language_source` VALUES (348,'Cn Country','1');
INSERT INTO `sys_language_source` VALUES (349,'Continent','1');
INSERT INTO `sys_language_source` VALUES (354,'绑定设备列表','1');
INSERT INTO `sys_language_source` VALUES (358,'IPV4地址','1');
INSERT INTO `sys_language_source` VALUES (359,'IPV4掩码','1');
INSERT INTO `sys_language_source` VALUES (360,'IPV6地址','1');
INSERT INTO `sys_language_source` VALUES (361,'IPV6掩码','1');
INSERT INTO `sys_language_source` VALUES (364,'登录','1');
INSERT INTO `sys_language_source` VALUES (365,'退出','1');
INSERT INTO `sys_language_source` VALUES (366,'验证码','1');
INSERT INTO `sys_language_source` VALUES (367,'换一个','1');
INSERT INTO `sys_language_source` VALUES (368,'关闭','1');
INSERT INTO `sys_language_source` VALUES (369,'开始时间','1');
INSERT INTO `sys_language_source` VALUES (370,'结束时间','1');
INSERT INTO `sys_language_source` VALUES (371,'旧密码','1');
INSERT INTO `sys_language_source` VALUES (372,'新密码','1');
INSERT INTO `sys_language_source` VALUES (373,'提交','1');
INSERT INTO `sys_language_source` VALUES (374,'重置','1');
INSERT INTO `sys_language_source` VALUES (375,'刷新','1');
INSERT INTO `sys_language_source` VALUES (376,'地址','1');
INSERT INTO `sys_language_source` VALUES (377,'秒','1');
INSERT INTO `sys_language_source` VALUES (378,'禁止','1');
INSERT INTO `sys_language_source` VALUES (379,'隐藏','1');
INSERT INTO `sys_language_source` VALUES (380,'是','1');
INSERT INTO `sys_language_source` VALUES (382,'新增','1');
INSERT INTO `sys_language_source` VALUES (383,'跳到','1');
INSERT INTO `sys_language_source` VALUES (384,'共','1');
INSERT INTO `sys_language_source` VALUES (385,'记录','1');
INSERT INTO `sys_language_source` VALUES (386,'页','1');
INSERT INTO `sys_language_source` VALUES (387,'第一页','1');
INSERT INTO `sys_language_source` VALUES (388,'最后一页','1');
INSERT INTO `sys_language_source` VALUES (389,'下页','1');
INSERT INTO `sys_language_source` VALUES (390,'上页','1');
INSERT INTO `sys_language_source` VALUES (391,'每页条数','1');
INSERT INTO `sys_language_source` VALUES (392,'操作','1');
INSERT INTO `sys_language_source` VALUES (393,'升级','1');
INSERT INTO `sys_language_source` VALUES (394,'选择文件','1');
INSERT INTO `sys_language_source` VALUES (395,'文件类型','1');
INSERT INTO `sys_language_source` VALUES (396,'文件不存在','1');
INSERT INTO `sys_language_source` VALUES (397,'必填项','1');
INSERT INTO `sys_language_source` VALUES (398,'长度','1');
INSERT INTO `sys_language_source` VALUES (399,'字节','1');
INSERT INTO `sys_language_source` VALUES (400,'反选','1');
INSERT INTO `sys_language_source` VALUES (401,'每天','1');
INSERT INTO `sys_language_source` VALUES (402,'每周','1');
INSERT INTO `sys_language_source` VALUES (403,'每月','1');
INSERT INTO `sys_language_source` VALUES (404,'还原','1');
INSERT INTO `sys_language_source` VALUES (405,'备注','1');
INSERT INTO `sys_language_source` VALUES (406,'提示','1');
INSERT INTO `sys_language_source` VALUES (407,'电子邮箱','1');
INSERT INTO `sys_language_source` VALUES (408,'电话','1');
INSERT INTO `sys_language_source` VALUES (409,'至','1');
INSERT INTO `sys_language_source` VALUES (410,'文件名','1');
INSERT INTO `sys_language_source` VALUES (411,'高','1');
INSERT INTO `sys_language_source` VALUES (412,'低','1');
INSERT INTO `sys_language_source` VALUES (413,'名称','1');
INSERT INTO `sys_language_source` VALUES (414,'自定义','1');
INSERT INTO `sys_language_source` VALUES (415,'选择','1');
INSERT INTO `sys_language_source` VALUES (416,'仅记录','1');
INSERT INTO `sys_language_source` VALUES (417,'允许访问','1');
INSERT INTO `sys_language_source` VALUES (418,'拒绝访问','1');
INSERT INTO `sys_language_source` VALUES (419,'关闭链接','1');
INSERT INTO `sys_language_source` VALUES (420,'继续','1');
INSERT INTO `sys_language_source` VALUES (421,'目的','1');
INSERT INTO `sys_language_source` VALUES (422,'来源IP不合法','1');
INSERT INTO `sys_language_source` VALUES (423,'目标IP不合法','1');
INSERT INTO `sys_language_source` VALUES (424,'添加访问控制','1');
INSERT INTO `sys_language_source` VALUES (425,'修改访问控制','1');
INSERT INTO `sys_language_source` VALUES (426,'来源IP防CC','1');
INSERT INTO `sys_language_source` VALUES (427,'来源IP地址访问速率限制','1');
INSERT INTO `sys_language_source` VALUES (428,'阻止访问时间','1');
INSERT INTO `sys_language_source` VALUES (429,'目的URI访问速率限制','1');
INSERT INTO `sys_language_source` VALUES (430,'目的URI列表','1');
INSERT INTO `sys_language_source` VALUES (431,'特定URI防CC','1');
INSERT INTO `sys_language_source` VALUES (432,'次','1');
INSERT INTO `sys_language_source` VALUES (433,'网络流量选择','1');
INSERT INTO `sys_language_source` VALUES (434,'推荐阈值','1');
INSERT INTO `sys_language_source` VALUES (435,'系统根据选择的网络流量,推荐合理的阀值范围','1');
INSERT INTO `sys_language_source` VALUES (436,'总流量触发阀值','1');
INSERT INTO `sys_language_source` VALUES (437,'数据包/秒','1');
INSERT INTO `sys_language_source` VALUES (438,'总流量阀值/单IP','1');
INSERT INTO `sys_language_source` VALUES (439,'包触发阀值','1');
INSERT INTO `sys_language_source` VALUES (440,'包阀值/单IP','1');
INSERT INTO `sys_language_source` VALUES (441,'SYN Flood触发阀值','1');
INSERT INTO `sys_language_source` VALUES (442,'SYN Flood阀值/单IP','1');
INSERT INTO `sys_language_source` VALUES (443,'目标IP地址','1');
INSERT INTO `sys_language_source` VALUES (444,'配置文件导出','1');
INSERT INTO `sys_language_source` VALUES (445,'导出配置','1');
INSERT INTO `sys_language_source` VALUES (447,'恢复配置成功','1');
INSERT INTO `sys_language_source` VALUES (448,'配置已应用','1');
INSERT INTO `sys_language_source` VALUES (449,'生成配置成功','1');
INSERT INTO `sys_language_source` VALUES (450,'未知类型','1');
INSERT INTO `sys_language_source` VALUES (451,'配置已完成','1');
INSERT INTO `sys_language_source` VALUES (452,'磁盘阀值','1');
INSERT INTO `sys_language_source` VALUES (453,'选择一行数据','1');
INSERT INTO `sys_language_source` VALUES (454,'选择要删除的数据','1');
INSERT INTO `sys_language_source` VALUES (455,'页面类型','1');
INSERT INTO `sys_language_source` VALUES (456,'页面文件','1');
INSERT INTO `sys_language_source` VALUES (457,'配置文字','1');
INSERT INTO `sys_language_source` VALUES (458,'生效','1');
INSERT INTO `sys_language_source` VALUES (459,'页面已存在','1');
INSERT INTO `sys_language_source` VALUES (460,'文件上传失败','1');
INSERT INTO `sys_language_source` VALUES (462,'填写提示文字','1');
INSERT INTO `sys_language_source` VALUES (463,'没有选择数据','1');
INSERT INTO `sys_language_source` VALUES (464,'错误页面类型','1');
INSERT INTO `sys_language_source` VALUES (465,'上传页面','1');
INSERT INTO `sys_language_source` VALUES (466,'页面提示文字','1');
INSERT INTO `sys_language_source` VALUES (467,'文件扩展名称','1');
INSERT INTO `sys_language_source` VALUES (468,'监控接口','1');
INSERT INTO `sys_language_source` VALUES (469,'优先级','1');
INSERT INTO `sys_language_source` VALUES (470,'限制从0到255','1');
INSERT INTO `sys_language_source` VALUES (471,'数据库配置同步','1');
INSERT INTO `sys_language_source` VALUES (472,'对端','1');
INSERT INTO `sys_language_source` VALUES (473,'选中的接口没有设置IP地址','1');
INSERT INTO `sys_language_source` VALUES (474,'文件类型将不会被盗链','1');
INSERT INTO `sys_language_source` VALUES (475,'禁止的HTTP头字段设置','1');
INSERT INTO `sys_language_source` VALUES (476,'HTTP头字段','1');
INSERT INTO `sys_language_source` VALUES (478,'允许的HTTP协议版本设置','1');
INSERT INTO `sys_language_source` VALUES (479,'HTTP协议版本','1');
INSERT INTO `sys_language_source` VALUES (480,'危害等级','1');
INSERT INTO `sys_language_source` VALUES (481,'攻击类型','1');
INSERT INTO `sys_language_source` VALUES (482,'源IP地址','1');
INSERT INTO `sys_language_source` VALUES (485,'一般信息','1');
INSERT INTO `sys_language_source` VALUES (486,'规则模板库更新失败','1');
INSERT INTO `sys_language_source` VALUES (487,'邮件报警','1');
INSERT INTO `sys_language_source` VALUES (488,'短信报警','1');
INSERT INTO `sys_language_source` VALUES (489,'发送间隔','1');
INSERT INTO `sys_language_source` VALUES (490,'报警发送间隔,单位:小时','1');
INSERT INTO `sys_language_source` VALUES (491,'通知设置','1');
INSERT INTO `sys_language_source` VALUES (492,'登录的帐号','1');
INSERT INTO `sys_language_source` VALUES (493,'登录的密码','1');
INSERT INTO `sys_language_source` VALUES (494,'发送端口','1');
INSERT INTO `sys_language_source` VALUES (495,'接收邮件的email','1');
INSERT INTO `sys_language_source` VALUES (496,'接收报警的手机号码','1');
INSERT INTO `sys_language_source` VALUES (497,'规则ID','1');
INSERT INTO `sys_language_source` VALUES (498,'目标主机','1');
INSERT INTO `sys_language_source` VALUES (499,'没有选择需要更新的数据','1');
INSERT INTO `sys_language_source` VALUES (500,'没有选择需要删除的数据','1');
INSERT INTO `sys_language_source` VALUES (501,'转黑名单','1');
INSERT INTO `sys_language_source` VALUES (502,'转白名单','1');
INSERT INTO `sys_language_source` VALUES (503,'查询','1');
INSERT INTO `sys_language_source` VALUES (504,'拦截','1');
INSERT INTO `sys_language_source` VALUES (505,'放行','1');
INSERT INTO `sys_language_source` VALUES (506,'黑名单','1');
INSERT INTO `sys_language_source` VALUES (507,'白名单','1');
INSERT INTO `sys_language_source` VALUES (508,'源','1');
INSERT INTO `sys_language_source` VALUES (509,'目标','1');
INSERT INTO `sys_language_source` VALUES (510,'目标端口','1');
INSERT INTO `sys_language_source` VALUES (511,'执行动作','1');
INSERT INTO `sys_language_source` VALUES (512,'源端口','1');
INSERT INTO `sys_language_source` VALUES (513,'地理位置','1');
INSERT INTO `sys_language_source` VALUES (514,'未知','1');
INSERT INTO `sys_language_source` VALUES (515,'该名单已存在,不需要添加','1');
INSERT INTO `sys_language_source` VALUES (516,'添加黑名单','1');
INSERT INTO `sys_language_source` VALUES (517,'添加白名单','1');
INSERT INTO `sys_language_source` VALUES (518,'检测端口','1');
INSERT INTO `sys_language_source` VALUES (519,'点击\"生成技术支持包\"按钮,将生成可下载的技术支持包文件','1');
INSERT INTO `sys_language_source` VALUES (520,'生成技术支持包','1');
INSERT INTO `sys_language_source` VALUES (521,'定时报表','1');
INSERT INTO `sys_language_source` VALUES (522,'访问/流量报表','1');
INSERT INTO `sys_language_source` VALUES (523,'添加自定义规则','1');
INSERT INTO `sys_language_source` VALUES (524,'修改自定义规则','1');
INSERT INTO `sys_language_source` VALUES (525,'规则模板名称','1');
INSERT INTO `sys_language_source` VALUES (526,'继承模板','1');
INSERT INTO `sys_language_source` VALUES (527,'继承模板名称','1');
INSERT INTO `sys_language_source` VALUES (528,'模板类型','1');
INSERT INTO `sys_language_source` VALUES (529,'站点组模板','1');
INSERT INTO `sys_language_source` VALUES (530,'站点模板','1');
INSERT INTO `sys_language_source` VALUES (531,'选择了模板类型为站点模板,但没有选择所属站点组模板','1');
INSERT INTO `sys_language_source` VALUES (532,'添加规则模板','1');
INSERT INTO `sys_language_source` VALUES (533,'修改规则模板','1');
INSERT INTO `sys_language_source` VALUES (534,'模板名称','1');
INSERT INTO `sys_language_source` VALUES (535,'模板说明','1');
INSERT INTO `sys_language_source` VALUES (536,'所属站点组模板','1');
INSERT INTO `sys_language_source` VALUES (537,'最大长度','1');
INSERT INTO `sys_language_source` VALUES (538,'参数名称最大长度','1');
INSERT INTO `sys_language_source` VALUES (539,'参数最大长度','1');
INSERT INTO `sys_language_source` VALUES (540,'最大参数个数','1');
INSERT INTO `sys_language_source` VALUES (541,'最大个数','1');
INSERT INTO `sys_language_source` VALUES (542,'以上各项当填写数值为0时，则该项设置不生效','1');
INSERT INTO `sys_language_source` VALUES (543,'建议学习完毕后关闭','1');
INSERT INTO `sys_language_source` VALUES (544,'是否应用学习结果','1');
INSERT INTO `sys_language_source` VALUES (545,'选择数据','1');
INSERT INTO `sys_language_source` VALUES (546,'选中数据为空','1');
INSERT INTO `sys_language_source` VALUES (547,'删除数据','1');
INSERT INTO `sys_language_source` VALUES (548,'停用数据','1');
INSERT INTO `sys_language_source` VALUES (549,'敏感词过滤','1');
INSERT INTO `sys_language_source` VALUES (550,'将对设置的敏感词以*号代替','1');
INSERT INTO `sys_language_source` VALUES (551,'词与词之间用\"|\"隔开','1');
INSERT INTO `sys_language_source` VALUES (552,'隐藏类型','1');
INSERT INTO `sys_language_source` VALUES (553,'监控目标','1');
INSERT INTO `sys_language_source` VALUES (554,'最近执行时间','1');
INSERT INTO `sys_language_source` VALUES (555,'响应时间','1');
INSERT INTO `sys_language_source` VALUES (556,'无数据','1');
INSERT INTO `sys_language_source` VALUES (557,'系统错误','1');
INSERT INTO `sys_language_source` VALUES (558,'正常','1');
INSERT INTO `sys_language_source` VALUES (559,'小时','1');
INSERT INTO `sys_language_source` VALUES (560,'分钟','1');
INSERT INTO `sys_language_source` VALUES (561,'查看报告','1');
INSERT INTO `sys_language_source` VALUES (562,'时间范围','1');
INSERT INTO `sys_language_source` VALUES (563,'响应时间分布','1');
INSERT INTO `sys_language_source` VALUES (564,'响应时间(毫秒)','1');
INSERT INTO `sys_language_source` VALUES (565,'监控目标URL状态','1');
INSERT INTO `sys_language_source` VALUES (566,'智能阻断','1');
INSERT INTO `sys_language_source` VALUES (567,'定值300秒','1');
INSERT INTO `sys_language_source` VALUES (568,'不少于10次(单位:次)','1');
INSERT INTO `sys_language_source` VALUES (569,'基准阻断时间','1');
INSERT INTO `sys_language_source` VALUES (570,'不少于600秒(单位:秒)','1');
INSERT INTO `sys_language_source` VALUES (571,'攻击时间','1');
INSERT INTO `sys_language_source` VALUES (572,'阻断持续时间(单位:秒)','1');
INSERT INTO `sys_language_source` VALUES (573,'将对该类爬虫实施防护','1');
INSERT INTO `sys_language_source` VALUES (574,'爬虫类型','1');
INSERT INTO `sys_language_source` VALUES (575,'公司名称','1');
INSERT INTO `sys_language_source` VALUES (576,'公司地址','1');
INSERT INTO `sys_language_source` VALUES (577,'许可证文件','1');
INSERT INTO `sys_language_source` VALUES (578,'文件仅部分被上传','1');
INSERT INTO `sys_language_source` VALUES (579,'只允许上传','1');
INSERT INTO `sys_language_source` VALUES (580,'格式的文件','1');
INSERT INTO `sys_language_source` VALUES (581,'IP+子网掩码','1');
INSERT INTO `sys_language_source` VALUES (582,'IP或IP段已存在','1');
INSERT INTO `sys_language_source` VALUES (583,'ip地址不合法,例:192.168.1.1','1');
INSERT INTO `sys_language_source` VALUES (584,'ip和子网掩码不合法,例:192.168.1.0/24','1');
INSERT INTO `sys_language_source` VALUES (585,'验证码错误','1');
INSERT INTO `sys_language_source` VALUES (586,'无此用户或禁止此用户登录','1');
INSERT INTO `sys_language_source` VALUES (587,'此用户禁止登录','1');
INSERT INTO `sys_language_source` VALUES (588,'登录成功','1');
INSERT INTO `sys_language_source` VALUES (589,'登录失败','1');
INSERT INTO `sys_language_source` VALUES (590,'登录超时时间(分钟)','1');
INSERT INTO `sys_language_source` VALUES (591,'登录尝试次数限制','1');
INSERT INTO `sys_language_source` VALUES (592,'登录错误锁定时间(分钟)','1');
INSERT INTO `sys_language_source` VALUES (593,'首页功能定制','1');
INSERT INTO `sys_language_source` VALUES (594,'技术支持命令已发出','1');
INSERT INTO `sys_language_source` VALUES (595,'升级成功','1');
INSERT INTO `sys_language_source` VALUES (596,'选择升级文件','1');
INSERT INTO `sys_language_source` VALUES (597,'展开所有','1');
INSERT INTO `sys_language_source` VALUES (598,'闭合所有','1');
INSERT INTO `sys_language_source` VALUES (599,'是否删除此菜单','1');
INSERT INTO `sys_language_source` VALUES (600,'是否显示子菜单','1');
INSERT INTO `sys_language_source` VALUES (601,'访问路径','1');
INSERT INTO `sys_language_source` VALUES (602,'菜单名','1');
INSERT INTO `sys_language_source` VALUES (603,'报告时间','1');
INSERT INTO `sys_language_source` VALUES (604,'上传时间','1');
INSERT INTO `sys_language_source` VALUES (605,'站点URL','1');
INSERT INTO `sys_language_source` VALUES (606,'文件分析结果-展示','1');
INSERT INTO `sys_language_source` VALUES (607,'删除的数据为空','1');
INSERT INTO `sys_language_source` VALUES (608,'严重等级','1');
INSERT INTO `sys_language_source` VALUES (609,'报告','1');
INSERT INTO `sys_language_source` VALUES (610,'扫描','1');
INSERT INTO `sys_language_source` VALUES (611,'未扫描','1');
INSERT INTO `sys_language_source` VALUES (612,'扫描中','1');
INSERT INTO `sys_language_source` VALUES (613,'扫描失败','1');
INSERT INTO `sys_language_source` VALUES (614,'扫描地址','1');
INSERT INTO `sys_language_source` VALUES (615,'填写真实有效的扫描地址','1');
INSERT INTO `sys_language_source` VALUES (616,'否则无法进行扫描','1');
INSERT INTO `sys_language_source` VALUES (617,'扫描结果不存在','1');
INSERT INTO `sys_language_source` VALUES (618,'SSH开关设置','1');
INSERT INTO `sys_language_source` VALUES (619,'站点组','1');
INSERT INTO `sys_language_source` VALUES (620,'规则模板','1');
INSERT INTO `sys_language_source` VALUES (621,'站点数量','1');
INSERT INTO `sys_language_source` VALUES (622,'所选站点组中,有对应的站点,不能删除','1');
INSERT INTO `sys_language_source` VALUES (623,'参数错误','1');
INSERT INTO `sys_language_source` VALUES (624,'保存失败','1');
INSERT INTO `sys_language_source` VALUES (625,'站点','1');
INSERT INTO `sys_language_source` VALUES (626,'端口','1');
INSERT INTO `sys_language_source` VALUES (627,'站点组名称','1');
INSERT INTO `sys_language_source` VALUES (628,'策略模板','1');
INSERT INTO `sys_language_source` VALUES (629,'单独策略模板','1');
INSERT INTO `sys_language_source` VALUES (630,'是否反向代理','1');
INSERT INTO `sys_language_source` VALUES (631,'站点名错误','1');
INSERT INTO `sys_language_source` VALUES (632,'端口错误','1');
INSERT INTO `sys_language_source` VALUES (633,'协议','1');
INSERT INTO `sys_language_source` VALUES (634,'操作系统','1');
INSERT INTO `sys_language_source` VALUES (635,'开发语言','1');
INSERT INTO `sys_language_source` VALUES (636,'更新时间','1');
INSERT INTO `sys_language_source` VALUES (637,'IP地址错误','1');
INSERT INTO `sys_language_source` VALUES (638,'管道发送失败','1');
INSERT INTO `sys_language_source` VALUES (639,'添加站点组','1');
INSERT INTO `sys_language_source` VALUES (640,'返回','1');
INSERT INTO `sys_language_source` VALUES (641,'修改站点组','1');
INSERT INTO `sys_language_source` VALUES (642,'配置策略','1');
INSERT INTO `sys_language_source` VALUES (643,'站点策略规则优先级高于站点组策略规则','1');
INSERT INTO `sys_language_source` VALUES (644,'根节点','1');
INSERT INTO `sys_language_source` VALUES (645,'所属站点','1');
INSERT INTO `sys_language_source` VALUES (646,'地址及端口','1');
INSERT INTO `sys_language_source` VALUES (647,'站点名称必须是IPV4地址或者是合法的域名','1');
INSERT INTO `sys_language_source` VALUES (648,'添加站点','1');
INSERT INTO `sys_language_source` VALUES (649,'修改站点','1');
INSERT INTO `sys_language_source` VALUES (650,'规则','1');
INSERT INTO `sys_language_source` VALUES (651,'规则名称','1');
INSERT INTO `sys_language_source` VALUES (652,'拦截方式','1');
INSERT INTO `sys_language_source` VALUES (653,'告警等级','1');
INSERT INTO `sys_language_source` VALUES (654,'类别','1');
INSERT INTO `sys_language_source` VALUES (655,'个规则集','1');
INSERT INTO `sys_language_source` VALUES (656,'危害描述','1');
INSERT INTO `sys_language_source` VALUES (657,'解决建议','1');
INSERT INTO `sys_language_source` VALUES (658,'网络超时','1');
INSERT INTO `sys_language_source` VALUES (659,'修改成功','1');
INSERT INTO `sys_language_source` VALUES (660,'修改失败','1');
INSERT INTO `sys_language_source` VALUES (661,'操作成功','1');
INSERT INTO `sys_language_source` VALUES (662,'更新失败','1');
INSERT INTO `sys_language_source` VALUES (663,'删除失败','1');
INSERT INTO `sys_language_source` VALUES (664,'已完成','1');
INSERT INTO `sys_language_source` VALUES (665,'已停止','1');
INSERT INTO `sys_language_source` VALUES (666,'上传成功','1');
INSERT INTO `sys_language_source` VALUES (670,'清除缓存','1');
INSERT INTO `sys_language_source` VALUES (672,'权限查看','1');
INSERT INTO `sys_language_source` VALUES (673,'授权信息','1');
INSERT INTO `sys_language_source` VALUES (674,'权限修改','1');
INSERT INTO `sys_language_source` VALUES (676,'管理日志','1');
INSERT INTO `sys_language_source` VALUES (677,'系统日志','1');
INSERT INTO `sys_language_source` VALUES (678,'编译器上传','1');
INSERT INTO `sys_language_source` VALUES (681,'日志配置','1');
INSERT INTO `sys_language_source` VALUES (688,'防火墙日志','1');
INSERT INTO `sys_language_source` VALUES (689,'入侵防御日志','1');
INSERT INTO `sys_language_source` VALUES (690,'安全策略','1');
INSERT INTO `sys_language_source` VALUES (691,'web应用防护日志','1');
INSERT INTO `sys_language_source` VALUES (692,'病毒防护日志','1');
INSERT INTO `sys_language_source` VALUES (693,'信息泄漏防护日志','1');
INSERT INTO `sys_language_source` VALUES (694,'DDOS防护日志','1');
INSERT INTO `sys_language_source` VALUES (695,'应用管控日志','1');
INSERT INTO `sys_language_source` VALUES (696,'url访问日志','1');
INSERT INTO `sys_language_source` VALUES (697,'日志库','1');
INSERT INTO `sys_language_source` VALUES (698,'用户认证日志','1');
INSERT INTO `sys_language_source` VALUES (699,'网中网检测日志','1');
INSERT INTO `sys_language_source` VALUES (700,'IpsecVPN日志','1');
INSERT INTO `sys_language_source` VALUES (703,'入侵防护','1');
INSERT INTO `sys_language_source` VALUES (705,'清空','1');
INSERT INTO `sys_language_source` VALUES (706,'加入防误报','1');
INSERT INTO `sys_language_source` VALUES (707,'启动','1');
INSERT INTO `sys_language_source` VALUES (708,'入侵数量统计(当月)','1');
INSERT INTO `sys_language_source` VALUES (709,'入侵类别统计(当月)','1');
INSERT INTO `sys_language_source` VALUES (710,'产品信息','1');
INSERT INTO `sys_language_source` VALUES (718,'Bypass设置','1');
INSERT INTO `sys_language_source` VALUES (719,'多语言','1');
INSERT INTO `sys_language_source` VALUES (720,'语言检测','1');
INSERT INTO `sys_language_source` VALUES (721,'导出语言包','1');
INSERT INTO `sys_language_source` VALUES (722,'磁盘清理','1');
INSERT INTO `sys_language_source` VALUES (723,'导入语言包','1');
INSERT INTO `sys_language_source` VALUES (724,'语言KEY','1');
INSERT INTO `sys_language_source` VALUES (725,'检查翻译字符唯一','1');
INSERT INTO `sys_language_source` VALUES (728,'定期报表','1');
INSERT INTO `sys_language_source` VALUES (729,'安全管理','1');
INSERT INTO `sys_language_source` VALUES (730,'HTTP请求动作过滤','1');
INSERT INTO `sys_language_source` VALUES (731,'HTTP请求内容过滤','1');
INSERT INTO `sys_language_source` VALUES (732,'服务器信息隐藏','1');
INSERT INTO `sys_language_source` VALUES (733,'开启云防护','1');
INSERT INTO `sys_language_source` VALUES (734,'测试菜单(不开放)日志','1');
INSERT INTO `sys_language_source` VALUES (735,'个人设置','1');
INSERT INTO `sys_language_source` VALUES (736,'开发人员使用','1');
INSERT INTO `sys_language_source` VALUES (737,'菜单权限管理','1');
INSERT INTO `sys_language_source` VALUES (738,'获取单个权限信息','1');
INSERT INTO `sys_language_source` VALUES (739,'OCR拦截','1');
INSERT INTO `sys_language_source` VALUES (740,'用户认证','1');
INSERT INTO `sys_language_source` VALUES (741,'桥设备','1');
INSERT INTO `sys_language_source` VALUES (742,'防火墙','1');
INSERT INTO `sys_language_source` VALUES (743,'透明代理','1');
INSERT INTO `sys_language_source` VALUES (744,'接入控制','1');
INSERT INTO `sys_language_source` VALUES (745,'反向代理','1');
INSERT INTO `sys_language_source` VALUES (746,'安全防护','1');
INSERT INTO `sys_language_source` VALUES (747,'日志管理','1');
INSERT INTO `sys_language_source` VALUES (748,'日志任务','1');
INSERT INTO `sys_language_source` VALUES (753,'周期','1');
INSERT INTO `sys_language_source` VALUES (754,'图片链接','1');
INSERT INTO `sys_language_source` VALUES (783,'桥设备名称','1');
INSERT INTO `sys_language_source` VALUES (786,'桥的类型','1');
INSERT INTO `sys_language_source` VALUES (787,'确定','1');
INSERT INTO `sys_language_source` VALUES (788,'取消','1');
INSERT INTO `sys_language_source` VALUES (789,'确认新密码','1');
INSERT INTO `sys_language_source` VALUES (790,'开启','1');
INSERT INTO `sys_language_source` VALUES (791,'启用','1');
INSERT INTO `sys_language_source` VALUES (792,'全部记录','1');
INSERT INTO `sys_language_source` VALUES (793,'所有','1');
INSERT INTO `sys_language_source` VALUES (794,'全选','1');
INSERT INTO `sys_language_source` VALUES (795,'全不选','1');
INSERT INTO `sys_language_source` VALUES (796,'日期','1');
INSERT INTO `sys_language_source` VALUES (797,'日志','1');
INSERT INTO `sys_language_source` VALUES (798,'紧急','1');
INSERT INTO `sys_language_source` VALUES (799,'警报','1');
INSERT INTO `sys_language_source` VALUES (800,'严重','1');
INSERT INTO `sys_language_source` VALUES (801,'错误','1');
INSERT INTO `sys_language_source` VALUES (802,'警告','1');
INSERT INTO `sys_language_source` VALUES (803,'确认密码不一致','1');
INSERT INTO `sys_language_source` VALUES (804,'新密码不能为空','1');
INSERT INTO `sys_language_source` VALUES (805,'KB/秒','1');
INSERT INTO `sys_language_source` VALUES (806,'流量','1');
INSERT INTO `sys_language_source` VALUES (807,'产品型号','1');
INSERT INTO `sys_language_source` VALUES (808,'系统版本','1');
INSERT INTO `sys_language_source` VALUES (809,'规则版本','1');
INSERT INTO `sys_language_source` VALUES (810,'产品序列号','1');
INSERT INTO `sys_language_source` VALUES (811,'引擎设置','1');
INSERT INTO `sys_language_source` VALUES (812,'默认拦截方式设置','1');
INSERT INTO `sys_language_source` VALUES (813,'检测端口设置:指定要检测的端口,如有多个请用|隔开,不能以0开头.如','1');
INSERT INTO `sys_language_source` VALUES (814,'请在URL开始加上http://或https://','1');
INSERT INTO `sys_language_source` VALUES (815,'清除菜单栏目','1');
INSERT INTO `sys_language_source` VALUES (816,'清除所有缓存','1');
INSERT INTO `sys_language_source` VALUES (817,'清除成功','1');
INSERT INTO `sys_language_source` VALUES (818,'启用后,来源IP地址的访问次数超过设定上限的.禁止该IP地址的任何后续访问','1');
INSERT INTO `sys_language_source` VALUES (819,'请求次数上限','1');
INSERT INTO `sys_language_source` VALUES (820,'启用后,来源IP对目的URI的访问次数超过设定上限的.禁止该IP地址的任何后续访问','1');
INSERT INTO `sys_language_source` VALUES (821,'每行一条URI,可输入多行并确保uri正确. 例: /test.php（不用输入参数部分）','1');
INSERT INTO `sys_language_source` VALUES (822,'请填写 \"来源IP防CC\" 的相关参数','1');
INSERT INTO `sys_language_source` VALUES (823,'请填写 \"特定URL防CC\" 的相关参数','1');
INSERT INTO `sys_language_source` VALUES (824,'开启DDOS云防护','1');
INSERT INTO `sys_language_source` VALUES (825,'其它TCP Flood触发阀值','1');
INSERT INTO `sys_language_source` VALUES (826,'其它TCP Flood阀值/单IP','1');
INSERT INTO `sys_language_source` VALUES (827,'禁止所有UDP协议的通信. (启用后所有使用UDP协议的通信将被禁止,包括使用UDP协议的DNS解释服务','1');
INSERT INTO `sys_language_source` VALUES (828,'禁止所有ICMP协议的通信. (启用后所有使用ICMP协议的通信将被禁止,包括使用ICMP协议的PING请求','1');
INSERT INTO `sys_language_source` VALUES (829,'以上所有项请填写大于0的正整数,各项阀值建议不小于','1');
INSERT INTO `sys_language_source` VALUES (830,'网络流量请填写1-1024以内的数值','1');
INSERT INTO `sys_language_source` VALUES (831,'DDOS攻击','1');
INSERT INTO `sys_language_source` VALUES (832,'恢复默认配置','1');
INSERT INTO `sys_language_source` VALUES (833,'点击\"恢复默认配置\"按钮,恢复本设备默认配置','1');
INSERT INTO `sys_language_source` VALUES (834,'配置文件导入','1');
INSERT INTO `sys_language_source` VALUES (835,'选择备份文件,点击“导入配置”按钮恢复之前的配置','1');
INSERT INTO `sys_language_source` VALUES (836,'导入配置','1');
INSERT INTO `sys_language_source` VALUES (837,'点击\"导出配置\"按钮备份当前数据库配置','1');
INSERT INTO `sys_language_source` VALUES (838,'正在配置文件,请等待1-2分钟','1');
INSERT INTO `sys_language_source` VALUES (839,'系统友情提示','1');
INSERT INTO `sys_language_source` VALUES (840,'恢复默认配置后系统将重启,确认','1');
INSERT INTO `sys_language_source` VALUES (841,'正在配置文件，请等待1-2分钟...','1');
INSERT INTO `sys_language_source` VALUES (842,'恢复默认配置后系统将重启','1');
INSERT INTO `sys_language_source` VALUES (843,'磁盘自动清理参数设置','1');
INSERT INTO `sys_language_source` VALUES (844,'是否开启自动清理','1');
INSERT INTO `sys_language_source` VALUES (845,'超过设置百分比数值时将自动清除日志','1');
INSERT INTO `sys_language_source` VALUES (846,'请先停用再修改','1');
INSERT INTO `sys_language_source` VALUES (847,'无法获取上传文件信息','1');
INSERT INTO `sys_language_source` VALUES (848,'确认文件可用','1');
INSERT INTO `sys_language_source` VALUES (849,'删除前先停用','1');
INSERT INTO `sys_language_source` VALUES (850,'禁止请求的文件扩展名设置','1');
INSERT INTO `sys_language_source` VALUES (851,'请求的文件扩展名类型将被禁止','1');
INSERT INTO `sys_language_source` VALUES (852,'VIP启用','1');
INSERT INTO `sys_language_source` VALUES (853,'是否开启','1');
INSERT INTO `sys_language_source` VALUES (854,'桥接口','1');
INSERT INTO `sys_language_source` VALUES (855,'允许HTTP请求内容','1');
INSERT INTO `sys_language_source` VALUES (856,'请求内容以外的将被拒绝','1');
INSERT INTO `sys_language_source` VALUES (857,'HTTP请求内容','1');
INSERT INTO `sys_language_source` VALUES (858,'HTTP请求动作设置','1');
INSERT INTO `sys_language_source` VALUES (859,'HTTP请求动作','1');
INSERT INTO `sys_language_source` VALUES (860,'启用后','1');
INSERT INTO `sys_language_source` VALUES (861,'该HTTP请求动作将被允许','1');
INSERT INTO `sys_language_source` VALUES (862,'请求的HTTP头字段将被禁止','1');
INSERT INTO `sys_language_source` VALUES (863,'以上所有项请填写大于0，小于2147483647的正整数','1');
INSERT INTO `sys_language_source` VALUES (864,'请求的HTTP协议版本将被允许','1');
INSERT INTO `sys_language_source` VALUES (866,'入侵日志','1');
INSERT INTO `sys_language_source` VALUES (867,'匹配内容','1');
INSERT INTO `sys_language_source` VALUES (868,'规则模板库找不到默认模板','1');
INSERT INTO `sys_language_source` VALUES (869,'所对应的站点不存在,请在\"站点组管理\"增加站点','1');
INSERT INTO `sys_language_source` VALUES (870,'开启入侵记录的E-mail功能','1');
INSERT INTO `sys_language_source` VALUES (871,'开启入侵记录的短信报警功能','1');
INSERT INTO `sys_language_source` VALUES (872,'发件人名称','1');
INSERT INTO `sys_language_source` VALUES (873,'发件人邮箱','1');
INSERT INTO `sys_language_source` VALUES (874,'以该名称发送,格式为EMAIL(可以和发件人邮箱相同)','1');
INSERT INTO `sys_language_source` VALUES (875,'发件人密码','1');
INSERT INTO `sys_language_source` VALUES (876,'SMTP服务器地址','1');
INSERT INTO `sys_language_source` VALUES (877,'发送服务器','1');
INSERT INTO `sys_language_source` VALUES (878,'SMTP服务器端口','1');
INSERT INTO `sys_language_source` VALUES (879,'收件人邮箱','1');
INSERT INTO `sys_language_source` VALUES (880,'收件人手机号码','1');
INSERT INTO `sys_language_source` VALUES (881,'以上信息非常重要,请确保所填信息均无错误,否则无法发送/接收邮件、短信','1');
INSERT INTO `sys_language_source` VALUES (882,'是否启用','1');
INSERT INTO `sys_language_source` VALUES (884,'精确查询','1');
INSERT INTO `sys_language_source` VALUES (885,'如','1');
INSERT INTO `sys_language_source` VALUES (886,'非法外联日志','1');
INSERT INTO `sys_language_source` VALUES (888,'提示:将根据当前的条件导出日志,最多导出最新的20000条记录','1');
INSERT INTO `sys_language_source` VALUES (889,'指定要检测的端口,如有多个请用|隔开,不能以0开头. 如','1');
INSERT INTO `sys_language_source` VALUES (890,'技术支持包是为了方便厂家排除系统故障的手段,当系统出现问题的时候,请生成技术支持包,并发送给我们','1');
INSERT INTO `sys_language_source` VALUES (891,'正在压缩技术支持包文件，请等待1-2分钟','1');
INSERT INTO `sys_language_source` VALUES (892,'超出限制,请联系技术员解决','1');
INSERT INTO `sys_language_source` VALUES (893,'站点组启用','1');
INSERT INTO `sys_language_source` VALUES (894,'内容最大长度','1');
INSERT INTO `sys_language_source` VALUES (895,'启用自学习','1');
INSERT INTO `sys_language_source` VALUES (896,'启用访问白名单','1');
INSERT INTO `sys_language_source` VALUES (897,'是否启用自学习','1');
INSERT INTO `sys_language_source` VALUES (898,'是否启用访问白名单','1');
INSERT INTO `sys_language_source` VALUES (899,'启用数据','1');
INSERT INTO `sys_language_source` VALUES (900,'敏感词内容','1');
INSERT INTO `sys_language_source` VALUES (901,'隐藏服务器信息','1');
INSERT INTO `sys_language_source` VALUES (902,'监控频率','1');
INSERT INTO `sys_language_source` VALUES (903,'请填写真实有效的监控地址,否则无法进行扫描','1');
INSERT INTO `sys_language_source` VALUES (904,'定时监控频率','1');
INSERT INTO `sys_language_source` VALUES (905,'开启智能阻断(启用后,系统将根据设定条件,识别频繁攻击的来源IP地址,在一段时间内拒绝该IP地址的访问.)','1');
INSERT INTO `sys_language_source` VALUES (906,'统计周期','1');
INSERT INTO `sys_language_source` VALUES (907,'入侵次数','1');
INSERT INTO `sys_language_source` VALUES (908,'以上各项请按需求填写','1');
INSERT INTO `sys_language_source` VALUES (909,'智能阻断日志','1');
INSERT INTO `sys_language_source` VALUES (910,'授权序列号','1');
INSERT INTO `sys_language_source` VALUES (911,'有效期','1');
INSERT INTO `sys_language_source` VALUES (912,'选择有效期内的许可证文件','1');
INSERT INTO `sys_language_source` VALUES (913,'文件大小超出服务器空间大小','1');
INSERT INTO `sys_language_source` VALUES (914,'文件大小超出浏览器限制','1');
INSERT INTO `sys_language_source` VALUES (915,'服务器临时文件夹丢失','1');
INSERT INTO `sys_language_source` VALUES (916,'文件写入到临时文件夹出错','1');
INSERT INTO `sys_language_source` VALUES (917,'请耐心等待授权认证','1');
INSERT INTO `sys_language_source` VALUES (918,'不启用黑白名单','1');
INSERT INTO `sys_language_source` VALUES (919,'启用白名单','1');
INSERT INTO `sys_language_source` VALUES (920,'启用黑名单','1');
INSERT INTO `sys_language_source` VALUES (921,'IP区间','1');
INSERT INTO `sys_language_source` VALUES (922,'ip区间不合法,例:192.168.1.1-192.168.255.254','1');
INSERT INTO `sys_language_source` VALUES (924,'当前账号错误登录次数 %s,锁定剩余%s秒','1');
INSERT INTO `sys_language_source` VALUES (925,'正常访问','1');
INSERT INTO `sys_language_source` VALUES (926,'来自爬虫','1');
INSERT INTO `sys_language_source` VALUES (927,'来自威胁','1');
INSERT INTO `sys_language_source` VALUES (928,'浏览数','1');
INSERT INTO `sys_language_source` VALUES (929,'访问人数','1');
INSERT INTO `sys_language_source` VALUES (930,'页面数','1');
INSERT INTO `sys_language_source` VALUES (931,'文件数','1');
INSERT INTO `sys_language_source` VALUES (932,'访问来源','1');
INSERT INTO `sys_language_source` VALUES (933,'实时流量','1');
INSERT INTO `sys_language_source` VALUES (934,'系统资源占用','1');
INSERT INTO `sys_language_source` VALUES (935,'选择时间','1');
INSERT INTO `sys_language_source` VALUES (936,'实时监控','1');
INSERT INTO `sys_language_source` VALUES (937,'历史数据查询','1');
INSERT INTO `sys_language_source` VALUES (938,'连接数','1');
INSERT INTO `sys_language_source` VALUES (939,'处理数','1');
INSERT INTO `sys_language_source` VALUES (940,'时间参数不正确','1');
INSERT INTO `sys_language_source` VALUES (941,'清空操作将对目前查询条件所列数据进行清空','1');
INSERT INTO `sys_language_source` VALUES (942,'清空后将不能恢复','1');
INSERT INTO `sys_language_source` VALUES (943,'不能没有清空条件','1');
INSERT INTO `sys_language_source` VALUES (944,'异常文件上传日志','1');
INSERT INTO `sys_language_source` VALUES (945,'任务名称','1');
INSERT INTO `sys_language_source` VALUES (946,'已有任务正在进行中','1');
INSERT INTO `sys_language_source` VALUES (947,'等待任务完成再添加新任务','1');
INSERT INTO `sys_language_source` VALUES (948,'删除前先停止任务','1');
INSERT INTO `sys_language_source` VALUES (949,'服务器数量','1');
INSERT INTO `sys_language_source` VALUES (950,'WEB服务器','1');
INSERT INTO `sys_language_source` VALUES (951,'入库失败','1');
INSERT INTO `sys_language_source` VALUES (952,'写入失败','1');
INSERT INTO `sys_language_source` VALUES (953,'IP地址、端口不能为空','1');
INSERT INTO `sys_language_source` VALUES (954,'添加服务器','1');
INSERT INTO `sys_language_source` VALUES (955,'输入名称','1');
INSERT INTO `sys_language_source` VALUES (956,'输入','1');
INSERT INTO `sys_language_source` VALUES (957,'权限不足','1');
INSERT INTO `sys_language_source` VALUES (958,'请求失败','1');
INSERT INTO `sys_language_source` VALUES (959,'确认要删除吗','1');
INSERT INTO `sys_language_source` VALUES (960,'必须输入大于0的整数','1');
INSERT INTO `sys_language_source` VALUES (961,'请选择升级文件','1');
INSERT INTO `sys_language_source` VALUES (962,'只能输入整数','1');
INSERT INTO `sys_language_source` VALUES (963,'不能输入大于%s的整数','1');
INSERT INTO `sys_language_source` VALUES (964,'不能输入小于%s的整数','1');
INSERT INTO `sys_language_source` VALUES (965,'只能输入%s~%s间的整数','1');
INSERT INTO `sys_language_source` VALUES (966,'只能输入数字,可为正负整数或正负浮点数','1');
INSERT INTO `sys_language_source` VALUES (967,'不能输入大于%s的数字','1');
INSERT INTO `sys_language_source` VALUES (968,'不能输入小于%s的数字','1');
INSERT INTO `sys_language_source` VALUES (969,'只能输入%s~%s间的数字','1');
INSERT INTO `sys_language_source` VALUES (970,'只能输入数字,可为正负整数或正负浮点数(双精度浮点型)','1');
INSERT INTO `sys_language_source` VALUES (971,'email格式错误','1');
INSERT INTO `sys_language_source` VALUES (972,'此项必填','1');
INSERT INTO `sys_language_source` VALUES (973,'只能输入字符型数据','1');
INSERT INTO `sys_language_source` VALUES (974,'输入字符数不能大于%s','1');
INSERT INTO `sys_language_source` VALUES (975,'输入字符数不能小于%s','1');
INSERT INTO `sys_language_source` VALUES (976,'限制输入字符数为%s~%s','1');
INSERT INTO `sys_language_source` VALUES (977,'此项必须唯一','1');
INSERT INTO `sys_language_source` VALUES (978,'URL地址错误','1');
INSERT INTO `sys_language_source` VALUES (979,'CC攻击','1');
INSERT INTO `sys_language_source` VALUES (980,'CMS漏洞攻击','1');
INSERT INTO `sys_language_source` VALUES (981,'文件包含漏洞攻击','1');
INSERT INTO `sys_language_source` VALUES (982,'通用攻击','1');
INSERT INTO `sys_language_source` VALUES (983,'信息泄漏','1');
INSERT INTO `sys_language_source` VALUES (984,'其他攻击','1');
INSERT INTO `sys_language_source` VALUES (985,'溢出攻击','1');
INSERT INTO `sys_language_source` VALUES (986,'HTTP保护','1');
INSERT INTO `sys_language_source` VALUES (987,'SQL注入','1');
INSERT INTO `sys_language_source` VALUES (988,'木马病毒','1');
INSERT INTO `sys_language_source` VALUES (989,'Web漏洞攻击','1');
INSERT INTO `sys_language_source` VALUES (990,'跨站脚本','1');
INSERT INTO `sys_language_source` VALUES (993,'系统工具','1');
INSERT INTO `sys_language_source` VALUES (994,'WEB控制配置','1');
INSERT INTO `sys_language_source` VALUES (995,'SNMP','1');
INSERT INTO `sys_language_source` VALUES (996,'网络测试','1');
INSERT INTO `sys_language_source` VALUES (997,'系统时间','1');
INSERT INTO `sys_language_source` VALUES (998,'抓包工具','1');
INSERT INTO `sys_language_source` VALUES (999,'组播路由转发','1');
INSERT INTO `sys_language_source` VALUES (1000,'网中网检测','1');
INSERT INTO `sys_language_source` VALUES (1025,'Modsec Status','1');
INSERT INTO `sys_language_source` VALUES (1026,'Modsec Requestbody Access Switch','1');
INSERT INTO `sys_language_source` VALUES (1027,'蓝盾信息安全技术股份有限公司 版权所有 Copyright&copy;1998-2017 Bluedon. All Rights Reserved','1');
INSERT INTO `sys_language_source` VALUES (1028,'蓝盾WEB应用防护系统','1');
INSERT INTO `sys_language_source` VALUES (1029,'模式','1');
INSERT INTO `sys_language_source` VALUES (1030,'默认动作','1');
INSERT INTO `sys_language_source` VALUES (1031,'继续处理','1');
INSERT INTO `sys_language_source` VALUES (1032,'WAF规则翻译','1');
INSERT INTO `sys_language_source` VALUES (1033,'WAF规则翻译导出','1');
INSERT INTO `sys_language_source` VALUES (1034,'WAF规则翻译导入','1');
INSERT INTO `sys_language_source` VALUES (1035,'创建语言库文件','1');
INSERT INTO `sys_language_source` VALUES (1036,'WAF引擎','1');
INSERT INTO `sys_language_source` VALUES (1037,'部署模式','1');
INSERT INTO `sys_language_source` VALUES (1038,'访问模式','1');
INSERT INTO `sys_language_source` VALUES (1039,'网络流量','1');
INSERT INTO `sys_language_source` VALUES (1040,'TCP 包触发阀值','1');
INSERT INTO `sys_language_source` VALUES (1041,'TCP 包阀值/单IP','1');
INSERT INTO `sys_language_source` VALUES (1042,'ACK Flood 数据包/秒','1');
INSERT INTO `sys_language_source` VALUES (1043,'ACK Flood 包阀值/单IP','1');
INSERT INTO `sys_language_source` VALUES (1044,'UDP 数据包/秒','1');
INSERT INTO `sys_language_source` VALUES (1045,'UDP 包阀值/单IP','1');
INSERT INTO `sys_language_source` VALUES (1046,'ICMP 数据包/秒','1');
INSERT INTO `sys_language_source` VALUES (1047,'ICMP 包阀值/单IP','1');
INSERT INTO `sys_language_source` VALUES (1048,'UDP 禁止','1');
INSERT INTO `sys_language_source` VALUES (1049,'ICMP 禁止','1');
INSERT INTO `sys_language_source` VALUES (1050,'HTTP请求内容名称','1');
INSERT INTO `sys_language_source` VALUES (1051,'HTTP请求内容状态','1');
INSERT INTO `sys_language_source` VALUES (1052,'HTTP请求动作名称','1');
INSERT INTO `sys_language_source` VALUES (1053,'启用选择','1');
INSERT INTO `sys_language_source` VALUES (1054,'HTTP协议版本名称','1');
INSERT INTO `sys_language_source` VALUES (1055,'HTTP协议版本状态','1');
INSERT INTO `sys_language_source` VALUES (1056,'邮件报警开启','1');
INSERT INTO `sys_language_source` VALUES (1057,'Now','1');
INSERT INTO `sys_language_source` VALUES (1058,'Max Value','1');
INSERT INTO `sys_language_source` VALUES (1059,'Cycle','1');
INSERT INTO `sys_language_source` VALUES (1060,'Phone Cycle','1');
INSERT INTO `sys_language_source` VALUES (1061,'设置名称','1');
INSERT INTO `sys_language_source` VALUES (1062,'设置值','1');
INSERT INTO `sys_language_source` VALUES (1063,'HTTP头字段名称','1');
INSERT INTO `sys_language_source` VALUES (1064,'HTTP头字段状态','1');
INSERT INTO `sys_language_source` VALUES (1065,'文件扩展状态','1');
INSERT INTO `sys_language_source` VALUES (1066,'Is Ssl','1');
INSERT INTO `sys_language_source` VALUES (1067,'Ssl Path','1');
INSERT INTO `sys_language_source` VALUES (1068,'爬虫防护爬虫类型','1');
INSERT INTO `sys_language_source` VALUES (1069,'防盗链文件类型','1');
INSERT INTO `sys_language_source` VALUES (1072,'Is Selfstudy','1');
INSERT INTO `sys_language_source` VALUES (1078,'开启自动清理','1');
INSERT INTO `sys_language_source` VALUES (1079,'URI 最大长度','1');
INSERT INTO `sys_language_source` VALUES (1080,'URI 参数名称最大长度','1');
INSERT INTO `sys_language_source` VALUES (1081,'URI 参数最大长度','1');
INSERT INTO `sys_language_source` VALUES (1082,'URI 最大参数个数','1');
INSERT INTO `sys_language_source` VALUES (1083,'COOKIE 最大长度','1');
INSERT INTO `sys_language_source` VALUES (1084,'COOKIE 参数名称最大长度','1');
INSERT INTO `sys_language_source` VALUES (1085,'COOKIE 内容最大长度','1');
INSERT INTO `sys_language_source` VALUES (1086,'COOKIE 最大个数','1');
INSERT INTO `sys_language_source` VALUES (1087,'Is Ip Black','1');
INSERT INTO `sys_language_source` VALUES (1088,'Is Domain Black','1');
INSERT INTO `sys_language_source` VALUES (1089,'确认密码','1');
INSERT INTO `sys_language_source` VALUES (1090,'源IP','1');
INSERT INTO `sys_language_source` VALUES (1091,'目标IP','1');
INSERT INTO `sys_language_source` VALUES (1092,'站点名称','1');
INSERT INTO `sys_language_source` VALUES (1093,'站点IP','1');
INSERT INTO `sys_language_source` VALUES (1094,'站点端口','1');
INSERT INTO `sys_language_source` VALUES (1095,'站点组ID','1');
INSERT INTO `sys_language_source` VALUES (1096,'策略模板ID','1');
INSERT INTO `sys_language_source` VALUES (1097,'自身策略模板ID','1');
INSERT INTO `sys_language_source` VALUES (1098,'24小时每小时最大流量模型','1');
INSERT INTO `sys_language_source` VALUES (1099,'24小时每小时单ip最大访问数','1');
INSERT INTO `sys_language_source` VALUES (1100,'24小时建模开始日期','1');
INSERT INTO `sys_language_source` VALUES (1101,'建模的时间周期','1');
INSERT INTO `sys_language_source` VALUES (1102,'建模结束时间','1');
INSERT INTO `sys_language_source` VALUES (1103,'建模状态','1');
INSERT INTO `sys_language_source` VALUES (1104,'学习时间','1');
INSERT INTO `sys_language_source` VALUES (1105,'学习开始时间','1');
INSERT INTO `sys_language_source` VALUES (1106,'学习结束时间','1');
INSERT INTO `sys_language_source` VALUES (1107,'动态建模备注','1');
INSERT INTO `sys_language_source` VALUES (1108,'是否是反向代理','1');
INSERT INTO `sys_language_source` VALUES (1109,'DDOS攻击防护类型','1');
INSERT INTO `sys_language_source` VALUES (1110,'负载均衡方式','1');
INSERT INTO `sys_language_source` VALUES (1111,'开启缓存','1');
INSERT INTO `sys_language_source` VALUES (1112,'启用健康检查','1');
INSERT INTO `sys_language_source` VALUES (1113,'证书公钥','1');
INSERT INTO `sys_language_source` VALUES (1114,'证书密钥','1');
INSERT INTO `sys_language_source` VALUES (1115,'反向代理说明','1');
INSERT INTO `sys_language_source` VALUES (1116,'IP地址','1');
INSERT INTO `sys_language_source` VALUES (1117,'创建时间','1');
INSERT INTO `sys_language_source` VALUES (1118,'站点ID','1');
INSERT INTO `sys_language_source` VALUES (1119,'权重','1');
INSERT INTO `sys_language_source` VALUES (1120,'Uri','1');
INSERT INTO `sys_language_source` VALUES (1122,'是否用于管理','1');
INSERT INTO `sys_language_source` VALUES (1123,'是否允许ping','1');
INSERT INTO `sys_language_source` VALUES (1124,'是否允许traceroute','1');
INSERT INTO `sys_language_source` VALUES (1125,'是启用日志','1');
INSERT INTO `sys_language_source` VALUES (1126,'是否SSH','1');
INSERT INTO `sys_language_source` VALUES (1127,'是否WEBUI','1');
INSERT INTO `sys_language_source` VALUES (1128,'密码与确认密码不一致','1');
INSERT INTO `sys_language_source` VALUES (1129,'密码必须包含字母和数字','1');
INSERT INTO `sys_language_source` VALUES (1130,'成功','1');
INSERT INTO `sys_language_source` VALUES (1131,'百分百','1');
INSERT INTO `sys_language_source` VALUES (1132,'允许','1');
INSERT INTO `sys_language_source` VALUES (1133,'停用','1');
INSERT INTO `sys_language_source` VALUES (1134,'否','1');
INSERT INTO `sys_language_source` VALUES (1135,'月份','1');
INSERT INTO `sys_language_source` VALUES (1136,'天','1');
INSERT INTO `sys_language_source` VALUES (1137,'未定义','1');
INSERT INTO `sys_language_source` VALUES (1138,'序号','1');
INSERT INTO `sys_language_source` VALUES (1139,'次数','1');
INSERT INTO `sys_language_source` VALUES (1140,'来源IP','1');
INSERT INTO `sys_language_source` VALUES (1141,'比例','1');
INSERT INTO `sys_language_source` VALUES (1142,'网址','1');
INSERT INTO `sys_language_source` VALUES (1143,'关键字','1');
INSERT INTO `sys_language_source` VALUES (1144,'浏览器','1');
INSERT INTO `sys_language_source` VALUES (1145,'浏览','1');
INSERT INTO `sys_language_source` VALUES (1146,'自动','1');
INSERT INTO `sys_language_source` VALUES (1147,'引擎参数错误','1');
INSERT INTO `sys_language_source` VALUES (1148,'拦截方式参数错误','1');
INSERT INTO `sys_language_source` VALUES (1149,'URL地址未填写','1');
INSERT INTO `sys_language_source` VALUES (1150,'选择任意URL，必须指定来源IP','1');
INSERT INTO `sys_language_source` VALUES (1151,'请填写来源IP','1');
INSERT INTO `sys_language_source` VALUES (1152,'请填写目标IP','1');
INSERT INTO `sys_language_source` VALUES (1153,'任意URL与指定URL选项错误','1');
INSERT INTO `sys_language_source` VALUES (1154,'是否启用参数错误','1');
INSERT INTO `sys_language_source` VALUES (1155,'选择某一行数据？','1');
INSERT INTO `sys_language_source` VALUES (1156,'选择启用的数据','1');
INSERT INTO `sys_language_source` VALUES (1157,'是否启用数据','1');
INSERT INTO `sys_language_source` VALUES (1158,'选择停用的数据','1');
INSERT INTO `sys_language_source` VALUES (1159,'是否停用数据','1');
INSERT INTO `sys_language_source` VALUES (1160,'选择删除的数据','1');
INSERT INTO `sys_language_source` VALUES (1161,'是否删除数据','1');
INSERT INTO `sys_language_source` VALUES (1162,'规则基本信息','1');
INSERT INTO `sys_language_source` VALUES (1163,'任意URL','1');
INSERT INTO `sys_language_source` VALUES (1164,'指定URL','1');
INSERT INTO `sys_language_source` VALUES (1165,'例','1');
INSERT INTO `sys_language_source` VALUES (1166,'或','1');
INSERT INTO `sys_language_source` VALUES (1167,'来源配置','1');
INSERT INTO `sys_language_source` VALUES (1168,'任意IP','1');
INSERT INTO `sys_language_source` VALUES (1169,'指定IP','1');
INSERT INTO `sys_language_source` VALUES (1170,'单IP','1');
INSERT INTO `sys_language_source` VALUES (1171,'IP段','1');
INSERT INTO `sys_language_source` VALUES (1172,'目标配置','1');
INSERT INTO `sys_language_source` VALUES (1173,'写入配置文件失败','1');
INSERT INTO `sys_language_source` VALUES (1174,'开启BYPASS后，每对WAN/LAN接口在物理上直接连通，流量不经过设备，一般用于网络故障排除。','1');
INSERT INTO `sys_language_source` VALUES (1175,'关闭BYPASS后，流量经过设备，恢复到正常状态。','1');
INSERT INTO `sys_language_source` VALUES (1176,'请选择','1');
INSERT INTO `sys_language_source` VALUES (1177,'HTTP类型','1');
INSERT INTO `sys_language_source` VALUES (1178,'规则模块','1');
INSERT INTO `sys_language_source` VALUES (1179,'优先级范围为%s','1');
INSERT INTO `sys_language_source` VALUES (1180,'防溢出配置','1');
INSERT INTO `sys_language_source` VALUES (1181,'其它模式','1');
INSERT INTO `sys_language_source` VALUES (1182,'透明桥模式','1');
INSERT INTO `sys_language_source` VALUES (1183,'反向代理模式','1');
INSERT INTO `sys_language_source` VALUES (1184,'没有选择需要加入防误报的数据','1');
INSERT INTO `sys_language_source` VALUES (1185,'操作成功, 共成功处理符合防误报条件的%d条日志, 失败的%d条','1');
INSERT INTO `sys_language_source` VALUES (1186,'选择加入防误报的数据','1');
INSERT INTO `sys_language_source` VALUES (1187,'是否加入防误报','1');
INSERT INTO `sys_language_source` VALUES (1188,'停用对应规则数据为空','1');
INSERT INTO `sys_language_source` VALUES (1189,'是否停用对应规则','1');
INSERT INTO `sys_language_source` VALUES (1190,'报警配置','1');
INSERT INTO `sys_language_source` VALUES (1191,'SMTP服务器地址无效','1');
INSERT INTO `sys_language_source` VALUES (1192,'发件人名称非登录帐号','1');
INSERT INTO `sys_language_source` VALUES (1193,'启用停用的参数错误','1');
INSERT INTO `sys_language_source` VALUES (1194,'开启状态','1');
INSERT INTO `sys_language_source` VALUES (1195,'url与url之间用\"|\"隔开','1');
INSERT INTO `sys_language_source` VALUES (1196,'扩展名与扩展名之间用\"|\"隔开','1');
INSERT INTO `sys_language_source` VALUES (1197,'拦截扩展名','1');
INSERT INTO `sys_language_source` VALUES (1198,'拦截词','1');
INSERT INTO `sys_language_source` VALUES (1199,'黑白名单','1');
INSERT INTO `sys_language_source` VALUES (1200,'轮询','1');
INSERT INTO `sys_language_source` VALUES (1201,'IP哈希','1');
INSERT INTO `sys_language_source` VALUES (1202,'非法外联配置','1');
INSERT INTO `sys_language_source` VALUES (1203,'超出指定范围的将被禁止','1');
INSERT INTO `sys_language_source` VALUES (1204,'访问云防线官方网站 http//www.cloudfence.cn --> 注册帐号-->填写正确的邮箱地址、密码等-->查收邮箱点击验证邮件完成注册。','1');
INSERT INTO `sys_language_source` VALUES (1205,'登录-->加入向导-->填写域名-->扫描出您添加域名的A记录-->点确定、回到服务返回用户界面-->等待管理员审核您添加的域名是否备案','1');
INSERT INTO `sys_language_source` VALUES (1206,'审核通过-->查收邮件获取CNAME记录-->登录域名注册商后台更改CNAME-->等待更改生效。','1');
INSERT INTO `sys_language_source` VALUES (1207,'审核不通过-->前往\"工业和信息化部ICP/IP地址/域名信息备案管理系统\"http//www.miitbeian.gov.cn申请备案。','1');
INSERT INTO `sys_language_source` VALUES (1208,'主机头名','1');
INSERT INTO `sys_language_source` VALUES (1209,'主机头名不能为空','1');
INSERT INTO `sys_language_source` VALUES (1210,'负载均衡方式不正确','1');
INSERT INTO `sys_language_source` VALUES (1211,'是否开启缓存','1');
INSERT INTO `sys_language_source` VALUES (1212,'是否启用健康检测','1');
INSERT INTO `sys_language_source` VALUES (1213,'本地监听端口','1');
INSERT INTO `sys_language_source` VALUES (1214,'本地监控端口错误','1');
INSERT INTO `sys_language_source` VALUES (1215,'协议错误','1');
INSERT INTO `sys_language_source` VALUES (1216,'主机头名已存在,请先在站点组管理删除','1');
INSERT INTO `sys_language_source` VALUES (1217,'代理IP及端口','1');
INSERT INTO `sys_language_source` VALUES (1218,'代理IP及端口不能为空','1');
INSERT INTO `sys_language_source` VALUES (1219,'代理IP错误','1');
INSERT INTO `sys_language_source` VALUES (1220,'代理端口错误','1');
INSERT INTO `sys_language_source` VALUES (1221,'代理权重错误','1');
INSERT INTO `sys_language_source` VALUES (1222,'清除旧的代理IP及端口失败','1');
INSERT INTO `sys_language_source` VALUES (1223,'设备名称','1');
INSERT INTO `sys_language_source` VALUES (1224,'IP地址/掩码','1');
INSERT INTO `sys_language_source` VALUES (1225,'绑定接口列表','1');
INSERT INTO `sys_language_source` VALUES (1226,'请填写IP地址或者请勿勾选WEBUI、SSH、允许PING、允许Traceroute','1');
INSERT INTO `sys_language_source` VALUES (1227,'所选网口数必须为两个以上(含两个)','1');
INSERT INTO `sys_language_source` VALUES (1228,'空数据','1');
INSERT INTO `sys_language_source` VALUES (1229,'IPV4格式错误','1');
INSERT INTO `sys_language_source` VALUES (1230,'掩码格式错误','1');
INSERT INTO `sys_language_source` VALUES (1231,'请输入正确的IP地址','1');
INSERT INTO `sys_language_source` VALUES (1232,'IPV6格式错误','1');
INSERT INTO `sys_language_source` VALUES (1233,'权重值范围1-10，值越大，权重越大','1');
INSERT INTO `sys_language_source` VALUES (1234,'IP地址、端口、权重不能为空','1');
INSERT INTO `sys_language_source` VALUES (1235,'桥接口名称','1');
INSERT INTO `sys_language_source` VALUES (1236,'可选绑定设备列表','1');
INSERT INTO `sys_language_source` VALUES (1237,'多个IP请分行填写','1');
INSERT INTO `sys_language_source` VALUES (1238,'继承模板ID','1');
INSERT INTO `sys_language_source` VALUES (1239,'数值越小,优先级越大','1');
INSERT INTO `sys_language_source` VALUES (1240,'HTTP请求类型','1');
INSERT INTO `sys_language_source` VALUES (1241,'特征生成','1');
INSERT INTO `sys_language_source` VALUES (1242,'匹配算法','1');
INSERT INTO `sys_language_source` VALUES (1243,'字符串匹配','1');
INSERT INTO `sys_language_source` VALUES (1244,'正则表达式匹配','1');
INSERT INTO `sys_language_source` VALUES (1245,'特征关键字','1');
INSERT INTO `sys_language_source` VALUES (1246,'温馨提示','1');
INSERT INTO `sys_language_source` VALUES (1247,'请确保您所填写的内容正确,否则该规则可能无法执行','1');
INSERT INTO `sys_language_source` VALUES (1248,'以上','1');
INSERT INTO `sys_language_source` VALUES (1249,'谷歌爬虫','1');
INSERT INTO `sys_language_source` VALUES (1250,'百度爬虫','1');
INSERT INTO `sys_language_source` VALUES (1251,'雅虎爬虫','1');
INSERT INTO `sys_language_source` VALUES (1252,'新浪爬虫','1');
INSERT INTO `sys_language_source` VALUES (1253,'网易爬虫','1');
INSERT INTO `sys_language_source` VALUES (1254,'MSN爬虫','1');
INSERT INTO `sys_language_source` VALUES (1255,'必应爬虫','1');
INSERT INTO `sys_language_source` VALUES (1256,'SOSO爬虫','1');
INSERT INTO `sys_language_source` VALUES (1257,'360爬虫','1');
INSERT INTO `sys_language_source` VALUES (1258,'即刻爬虫','1');
INSERT INTO `sys_language_source` VALUES (1259,'东方网景','1');
INSERT INTO `sys_language_source` VALUES (1260,'热土爬虫','1');
INSERT INTO `sys_language_source` VALUES (1261,'华为赛门铁克','1');
INSERT INTO `sys_language_source` VALUES (1262,'英国爬虫','1');
INSERT INTO `sys_language_source` VALUES (1263,'俄罗斯爬虫','1');
INSERT INTO `sys_language_source` VALUES (1264,'韩国爬虫','1');
INSERT INTO `sys_language_source` VALUES (1265,'日本爬虫','1');
INSERT INTO `sys_language_source` VALUES (1266,'其它爬虫','1');
INSERT INTO `sys_language_source` VALUES (1267,'用户名或者密码错误,剩余 %s 次登录机会','1');
INSERT INTO `sys_language_source` VALUES (1268,'完成时间','1');
INSERT INTO `sys_language_source` VALUES (1269,'所属站点组','1');
INSERT INTO `sys_language_source` VALUES (1270,'修改服务器','1');
INSERT INTO `sys_language_source` VALUES (1271,'规则模板ID','1');
INSERT INTO `sys_language_source` VALUES (1272,'所选站点中,有反向代理站点,不能删除','1');
INSERT INTO `sys_language_source` VALUES (1273,'删除数据失败','1');
INSERT INTO `sys_language_source` VALUES (1274,'提交的数据不能空','1');
INSERT INTO `sys_language_source` VALUES (1275,'IP地址及端口','1');
INSERT INTO `sys_language_source` VALUES (1276,'选择年月','1');
INSERT INTO `sys_language_source` VALUES (1277,'选择年月日','1');
INSERT INTO `sys_language_source` VALUES (1278,'输出格式','1');
INSERT INTO `sys_language_source` VALUES (1279,'报表已生成，请点击相关链接进行下载','1');
INSERT INTO `sys_language_source` VALUES (1280,'时间(时)','1');
INSERT INTO `sys_language_source` VALUES (1281,'事件次数','1');
INSERT INTO `sys_language_source` VALUES (1282,'URL/IP地址','1');
INSERT INTO `sys_language_source` VALUES (1283,'无效参数','1');
INSERT INTO `sys_language_source` VALUES (1284,'报告已生成','1');
INSERT INTO `sys_language_source` VALUES (1285,'蓝盾WEB应用防护系统攻击报表','1');
INSERT INTO `sys_language_source` VALUES (1286,'蓝盾WEB应用防护系统访问报表','1');
INSERT INTO `sys_language_source` VALUES (1287,'统计时间段','1');
INSERT INTO `sys_language_source` VALUES (1288,'报表生成时间','1');
INSERT INTO `sys_language_source` VALUES (1289,'管理接口地址','1');
INSERT INTO `sys_language_source` VALUES (1290,'报表内容:入侵记录统计','1');
INSERT INTO `sys_language_source` VALUES (1291,'入侵数量统计图--总数','1');
INSERT INTO `sys_language_source` VALUES (1292,'入侵趋势图','1');
INSERT INTO `sys_language_source` VALUES (1293,'入侵趋势图(24小时时间段)','1');
INSERT INTO `sys_language_source` VALUES (1294,'入侵类别统计图','1');
INSERT INTO `sys_language_source` VALUES (1295,'入侵类别对比图','1');
INSERT INTO `sys_language_source` VALUES (1296,'入侵数量统计','1');
INSERT INTO `sys_language_source` VALUES (1297,'入侵趋势','1');
INSERT INTO `sys_language_source` VALUES (1298,'入侵类别统计','1');
INSERT INTO `sys_language_source` VALUES (1299,'入侵类别对比','1');
INSERT INTO `sys_language_source` VALUES (1300,'入侵类来源地址统计','1');
INSERT INTO `sys_language_source` VALUES (1301,'攻击事件的入侵类来源统计','1');
INSERT INTO `sys_language_source` VALUES (1302,'入侵类来源的攻击事件统计','1');
INSERT INTO `sys_language_source` VALUES (1303,'攻击类型按被攻击主机统计','1');
INSERT INTO `sys_language_source` VALUES (1304,'被攻击主机的攻击类型统计','1');
INSERT INTO `sys_language_source` VALUES (1305,'攻击类型按被攻击URL的统计','1');
INSERT INTO `sys_language_source` VALUES (1306,'被攻击URL的攻击类型统计','1');
INSERT INTO `sys_language_source` VALUES (1307,'被攻击主机统计','1');
INSERT INTO `sys_language_source` VALUES (1308,'被攻击URL统计','1');
INSERT INTO `sys_language_source` VALUES (1309,'被攻击URL统计(含参数)','1');
INSERT INTO `sys_language_source` VALUES (1310,'生成即时报表(查看HTML报表时建议使用的浏览器: IE10或以上/火狐/谷)','1');
INSERT INTO `sys_language_source` VALUES (1311,'报表日期','1');
INSERT INTO `sys_language_source` VALUES (1312,'下载报表','1');
INSERT INTO `sys_language_source` VALUES (1313,'预览报表','1');
INSERT INTO `sys_language_source` VALUES (1314,'生成报表','1');
INSERT INTO `sys_language_source` VALUES (1315,'报表生成中，请稍后...','1');
INSERT INTO `sys_language_source` VALUES (1316,'HTML格式','1');
INSERT INTO `sys_language_source` VALUES (1317,'PDF格式','1');
INSERT INTO `sys_language_source` VALUES (1318,'DOC格式','1');
INSERT INTO `sys_language_source` VALUES (1319,'请输入正整数','1');
INSERT INTO `sys_language_source` VALUES (1320,'请按需求填写','1');
INSERT INTO `sys_language_source` VALUES (1321,'请选择查询日期','1');
INSERT INTO `sys_language_source` VALUES (1322,'防护网站','1');
INSERT INTO `sys_language_source` VALUES (1323,'安全统计分析','1');
INSERT INTO `sys_language_source` VALUES (1324,'用户在您网站停留的时间','1');
INSERT INTO `sys_language_source` VALUES (1325,'爬虫分析','1');
INSERT INTO `sys_language_source` VALUES (1326,'爬虫','1');
INSERT INTO `sys_language_source` VALUES (1327,'网站流量(按天)','1');
INSERT INTO `sys_language_source` VALUES (1328,'网络接口','1');
INSERT INTO `sys_language_source` VALUES (1329,'接收数据包','1');
INSERT INTO `sys_language_source` VALUES (1330,'发送数据包','1');
INSERT INTO `sys_language_source` VALUES (1331,'接收字节','1');
INSERT INTO `sys_language_source` VALUES (1332,'发送字节','1');
INSERT INTO `sys_language_source` VALUES (1333,'接收的错误包','1');
INSERT INTO `sys_language_source` VALUES (1334,'发送的错误包','1');
INSERT INTO `sys_language_source` VALUES (1335,'接收丢失','1');
INSERT INTO `sys_language_source` VALUES (1336,'发送丢失','1');
INSERT INTO `sys_language_source` VALUES (1337,'网站入口页面访问次数','1');
INSERT INTO `sys_language_source` VALUES (1338,'网站出口页面访问次数','1');
INSERT INTO `sys_language_source` VALUES (1339,'被访页面','1');
INSERT INTO `sys_language_source` VALUES (1340,'页面访问排名','1');
INSERT INTO `sys_language_source` VALUES (1341,'错误码排名','1');
INSERT INTO `sys_language_source` VALUES (1342,'错误码','1');
INSERT INTO `sys_language_source` VALUES (1343,'搜索引擎','1');
INSERT INTO `sys_language_source` VALUES (1344,'搜索关键字','1');
INSERT INTO `sys_language_source` VALUES (1345,'从搜索引擎进入我的网站','1');
INSERT INTO `sys_language_source` VALUES (1346,'从别的网站进入我的网站','1');
INSERT INTO `sys_language_source` VALUES (1347,'用户都用什么样的操作系统？','1');
INSERT INTO `sys_language_source` VALUES (1348,'用户都用什么样的浏览器？','1');
INSERT INTO `sys_language_source` VALUES (1349,'用户停留时间','1');
INSERT INTO `sys_language_source` VALUES (1350,'总PV','1');
INSERT INTO `sys_language_source` VALUES (1351,'访问次数','1');
INSERT INTO `sys_language_source` VALUES (1352,'流量数','1');
INSERT INTO `sys_language_source` VALUES (1353,'半双工','1');
INSERT INTO `sys_language_source` VALUES (1354,'全双工','1');
INSERT INTO `sys_language_source` VALUES (1355,'已连接','1');
INSERT INTO `sys_language_source` VALUES (1356,'未连接','1');
INSERT INTO `sys_language_source` VALUES (1357,'输入ID','1');
INSERT INTO `sys_language_source` VALUES (1358,'规则说明','1');
INSERT INTO `sys_language_source` VALUES (1359,'添加成功','1');
INSERT INTO `sys_language_source` VALUES (1360,'上传失败','1');
INSERT INTO `sys_language_source` VALUES (1364,'中危','1');
INSERT INTO `sys_language_source` VALUES (1365,'低危','1');
INSERT INTO `sys_language_source` VALUES (1366,'高危','1');
INSERT INTO `sys_language_source` VALUES (1367,'启用状态','1');
INSERT INTO `sys_language_source` VALUES (1368,'HTTP数据类型','1');
INSERT INTO `sys_language_source` VALUES (1369,'提示类型','1');
INSERT INTO `sys_language_source` VALUES (1370,'自定义文件','1');
INSERT INTO `sys_language_source` VALUES (1371,'生效状态','1');
INSERT INTO `sys_language_source` VALUES (1372,'拦截url','1');
INSERT INTO `sys_language_source` VALUES (1373,'website_id','1');
INSERT INTO `sys_language_source` VALUES (1374,'策略内容','1');
INSERT INTO `sys_language_source` VALUES (1375,'站点组启用状态','1');
INSERT INTO `sys_language_source` VALUES (1376,'攻击类别','1');
INSERT INTO `sys_language_source` VALUES (1377,'危害级别','1');
INSERT INTO `sys_language_source` VALUES (1378,'扫描状态','1');
INSERT INTO `sys_language_source` VALUES (1379,'扫描结果','1');
INSERT INTO `sys_language_source` VALUES (1380,'敏感词过滤开启状态','1');
INSERT INTO `sys_language_source` VALUES (1381,'智能阻断状态','1');
INSERT INTO `sys_language_source` VALUES (1382,'Bypass启用状态','1');
INSERT INTO `sys_language_source` VALUES (1383,'监控目标URL','1');
INSERT INTO `sys_language_source` VALUES (1384,'Protype','1');
INSERT INTO `sys_language_source` VALUES (1385,'Freq','1');
INSERT INTO `sys_language_source` VALUES (1386,'系统默认语言','1');
INSERT INTO `sys_language_source` VALUES (1387,'防火墙角色','1');
INSERT INTO `sys_language_source` VALUES (1388,'AuditLogUniqueID','1');
INSERT INTO `sys_language_source` VALUES (1389,'UserAgent','1');
INSERT INTO `sys_language_source` VALUES (1390,'HTTP请求方式','1');
INSERT INTO `sys_language_source` VALUES (1391,'请求类型','1');
INSERT INTO `sys_language_source` VALUES (1392,'响应类型','1');
INSERT INTO `sys_language_source` VALUES (1393,'请求状态码','1');
INSERT INTO `sys_language_source` VALUES (1394,'GeneralMsg','1');
INSERT INTO `sys_language_source` VALUES (1395,'规则文件','1');
INSERT INTO `sys_language_source` VALUES (1396,'总数','1');
INSERT INTO `sys_language_source` VALUES (1397,'默认值','1');
INSERT INTO `sys_language_source` VALUES (1398,'范围','1');
INSERT INTO `sys_language_source` VALUES (1399,'模式来源','1');
INSERT INTO `sys_language_source` VALUES (1400,'规则模板库找不到模板','1');
INSERT INTO `sys_language_source` VALUES (1401,'不能删除正在使用的模板','1');
INSERT INTO `sys_language_source` VALUES (1402,'操作失败','1');
INSERT INTO `sys_language_source` VALUES (1403,'重启关机','1');
INSERT INTO `sys_language_source` VALUES (1404,'Symbol','1');
INSERT INTO `sys_language_source` VALUES (1405,'Field Desc','1');
INSERT INTO `sys_language_source` VALUES (1406,'Json','1');
INSERT INTO `sys_language_source` VALUES (1407,'版本类型','1');
INSERT INTO `sys_language_source` VALUES (1408,'联系电话','1');
INSERT INTO `sys_language_source` VALUES (1409,'阻断','1');
INSERT INTO `sys_language_source` VALUES (1410,'防护的url','1');
INSERT INTO `sys_language_source` VALUES (1411,'最大文件大小','1');
INSERT INTO `sys_language_source` VALUES (1412,'阻断持续时间','1');
INSERT INTO `sys_language_source` VALUES (1413,'DestinationIP','1');
INSERT INTO `sys_language_source` VALUES (1416,'RequestContentType','1');
INSERT INTO `sys_language_source` VALUES (1417,'ResponseContentType','1');
INSERT INTO `sys_language_source` VALUES (1418,'HttpStatusCode','1');
INSERT INTO `sys_language_source` VALUES (1420,'是否病毒','1');
INSERT INTO `sys_language_source` VALUES (1421,'检查结果','1');
INSERT INTO `sys_language_source` VALUES (1422,'Number','1');
INSERT INTO `sys_language_source` VALUES (1423,'用户名只能包含数字加字母组合','1');
INSERT INTO `sys_language_source` VALUES (1424,'重新扫描将会清除原来的任务数据,确定要继续么','1');
INSERT INTO `sys_language_source` VALUES (1425,'欢迎您','1');
INSERT INTO `sys_language_source` VALUES (1426,'检测登录状态','1');
INSERT INTO `sys_language_source` VALUES (1427,'syslog服务器','1');
INSERT INTO `sys_language_source` VALUES (1428,'邮件测试','1');
INSERT INTO `sys_language_source` VALUES (1429,'日志入库归档','1');
INSERT INTO `sys_language_source` VALUES (1430,'初始化','1');
INSERT INTO `sys_language_source` VALUES (1431,'waf账号同步','1');
INSERT INTO `sys_language_source` VALUES (1432,'启用网关邮件功能','1');
INSERT INTO `sys_language_source` VALUES (1433,'启用手机报警开关','1');
INSERT INTO `sys_language_source` VALUES (1434,'配置项名称','1');
INSERT INTO `sys_language_source` VALUES (1435,'配置项值','1');
INSERT INTO `sys_language_source` VALUES (1436,'接口命令','1');
INSERT INTO `sys_language_source` VALUES (1437,'导入','1');
INSERT INTO `sys_language_source` VALUES (1438,'启用手机报警功能','1');
INSERT INTO `sys_language_source` VALUES (1439,'登录超时','1');
INSERT INTO `sys_language_source` VALUES (1440,'系统主页','1');
INSERT INTO `sys_language_source` VALUES (1441,'超级管理员','1');
INSERT INTO `sys_language_source` VALUES (1442,'系统管理员','1');
INSERT INTO `sys_language_source` VALUES (1443,'安全管理员','1');
INSERT INTO `sys_language_source` VALUES (1444,'安全审计员','1');
INSERT INTO `sys_language_source` VALUES (1445,'通知','1');
INSERT INTO `sys_language_source` VALUES (1446,'信息','1');
INSERT INTO `sys_language_source` VALUES (1447,'调试','1');
INSERT INTO `sys_language_source` VALUES (1448,'DDOS日志','1');
INSERT INTO `sys_language_source` VALUES (1449,'CC日志','1');
INSERT INTO `sys_language_source` VALUES (1450,'智能上传文件日志','1');
INSERT INTO `sys_language_source` VALUES (1451,'同级账号管理','1');
INSERT INTO `sys_language_source` VALUES (1452,'更新状态','1');
INSERT INTO `sys_language_source` VALUES (1453,'规则复制','1');
INSERT INTO `sys_language_source` VALUES (1454,'预设规则模板','1');
INSERT INTO `sys_language_source` VALUES (1455,'自定义规则模板','1');
INSERT INTO `sys_language_source` VALUES (1456,'IP过滤设置','1');
INSERT INTO `sys_language_source` VALUES (1457,'智能木马检测','1');
INSERT INTO `sys_language_source` VALUES (1458,'禁止请求的文件扩展名设置 (启用后,请求的文件扩展名类型将被禁止)','1');
INSERT INTO `sys_language_source` VALUES (1459,'拦截后缀名','1');
INSERT INTO `sys_language_source` VALUES (1460,'文件大小','1');
INSERT INTO `sys_language_source` VALUES (1461,'入库时间','1');
INSERT INTO `sys_language_source` VALUES (1462,'过滤IP/IP段','1');
INSERT INTO `sys_language_source` VALUES (1463,'策略名','1');
INSERT INTO `sys_language_source` VALUES (1464,'目标Url','1');
INSERT INTO `sys_language_source` VALUES (1465,'预设策略','1');
INSERT INTO `sys_language_source` VALUES (1466,'单用户登录客户端数限制','1');
INSERT INTO `sys_language_source` VALUES (1467,'User Agent','1');
INSERT INTO `sys_language_source` VALUES (1468,'Http Method','1');
INSERT INTO `sys_language_source` VALUES (1469,'Http Protocol','1');
INSERT INTO `sys_language_source` VALUES (1470,'Rule ID','1');
INSERT INTO `sys_language_source` VALUES (1471,'下载路径','1');
INSERT INTO `sys_language_source` VALUES (1472,'上传文件ID','1');
INSERT INTO `sys_language_source` VALUES (1473,'检测结果','1');
INSERT INTO `sys_language_source` VALUES (1474,'复制','1');
INSERT INTO `sys_language_source` VALUES (1475,'是否启用规则','1');
INSERT INTO `sys_language_source` VALUES (1476,'是否停用规则','1');
INSERT INTO `sys_language_source` VALUES (1477,'IP过滤功能,只适合于部署为\"透明桥接\"模式才有效','1');
INSERT INTO `sys_language_source` VALUES (1478,'不使用IP过滤功能,则对所有请求都过滤; 使用IP过滤功能,即仅过滤源IP或目标IP符合设置的请求','1');
INSERT INTO `sys_language_source` VALUES (1479,'过滤IP/IP段之间用\"|\"隔开','1');
INSERT INTO `sys_language_source` VALUES (1480,'清空操作将对目前所有数据进行清空,清空后将不能恢复,确认','1');
INSERT INTO `sys_language_source` VALUES (1481,'未分类站点,不能删除','1');
INSERT INTO `sys_language_source` VALUES (1482,'主机头名必须是IPV4地址或者是合法的域名','1');
INSERT INTO `sys_language_source` VALUES (1483,'允许IP,IP段,IP+掩码等方式,其中IP段格式为: ip-ip ,如(192.168.1.1-192.168.4.254),IP+掩码方式为: ip/掩码 ,如(192.168.1.0/24)','1');
INSERT INTO `sys_language_source` VALUES (1484,'预设模板','1');
INSERT INTO `sys_language_source` VALUES (1485,'当前启用','1');
INSERT INTO `sys_language_source` VALUES (1486,'提示:预设规则模板,只能被启用其中一个. 当选择\"严格\"模板,有可能出现多报的情况,当选择\"宽松\"模板,有可能漏报情况.','1');
INSERT INTO `sys_language_source` VALUES (1487,'没有选择需要重置的模板','1');
INSERT INTO `sys_language_source` VALUES (1488,'请选择需要重置的规则模板','1');
INSERT INTO `sys_language_source` VALUES (1489,'确认需要重置选择的规则模板吗','1');
INSERT INTO `sys_language_source` VALUES (1490,'当选择模板类型为站点组模板,此选项不生效','1');
INSERT INTO `sys_language_source` VALUES (1491,'上行','1');
INSERT INTO `sys_language_source` VALUES (1492,'下行','1');
INSERT INTO `sys_language_source` VALUES (1493,'内存','1');
INSERT INTO `sys_language_source` VALUES (1494,'磁盘','1');
INSERT INTO `sys_language_source` VALUES (1495,'当前预设规则模板名称','1');
INSERT INTO `sys_language_source` VALUES (1496,'不允许上传','1');
INSERT INTO `sys_language_source` VALUES (1497,'关键字告警','1');
INSERT INTO `sys_language_source` VALUES (1498,'不支持选择超过两个设备','1');
INSERT INTO `sys_language_source` VALUES (1499,'共 {total} 条记录, 每页显示 {pagesize} 条','1');
INSERT INTO `sys_language_source` VALUES (1500,'不能上传大于%sM的文件','1');
/*!40000 ALTER TABLE `sys_language_source` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user`
--

DROP TABLE IF EXISTS `sys_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(50) DEFAULT '' COMMENT '管理员',
  `pwd` char(32) DEFAULT '' COMMENT '密码',
  `group_id` int(11) NOT NULL DEFAULT '0' COMMENT '权限组ID',
  `enable` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否启用，1：true,0:false',
  `error_count` int(10) NOT NULL DEFAULT '0',
  `error_lock_time` int(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uidx_name` (`name`),
  KEY `idx_group_id` (`group_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user`
--

LOCK TABLES `sys_user` WRITE;
/*!40000 ALTER TABLE `sys_user` DISABLE KEYS */;
INSERT INTO `sys_user` VALUES (1,'root','202cb962ac59075b964b07152d234b70',1,1,0,0);
INSERT INTO `sys_user` VALUES (2,'admin','1aef232d37cca903e23924eca3ba5135',2,1,0,0);
INSERT INTO `sys_user` VALUES (3,'secure','1aef232d37cca903e23924eca3ba5135',3,1,0,0);
INSERT INTO `sys_user` VALUES (4,'audit','1aef232d37cca903e23924eca3ba5135',4,1,0,0);
/*!40000 ALTER TABLE `sys_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_authority`
--

DROP TABLE IF EXISTS `sys_user_authority`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_user_authority` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `group_id` int(11) DEFAULT '0' COMMENT '权限组ID',
  `sys_menu_id` int(11) DEFAULT '0',
  `enable` int(1) DEFAULT '1' COMMENT '是否启用，1：true,0:false',
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_menu_key` (`group_id`,`sys_menu_id`),
  KEY `idx_group_id` (`group_id`) USING BTREE,
  KEY `idx_sys_menu_id` (`sys_menu_id`) USING BTREE,
  CONSTRAINT `group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `sys_user_group` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sys_menu_id_fk` FOREIGN KEY (`sys_menu_id`) REFERENCES `sys_user_menu` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1577 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_authority`
--

LOCK TABLES `sys_user_authority` WRITE;
/*!40000 ALTER TABLE `sys_user_authority` DISABLE KEYS */;
INSERT INTO `sys_user_authority` VALUES (1,1,1,1);
INSERT INTO `sys_user_authority` VALUES (2,1,2,1);
INSERT INTO `sys_user_authority` VALUES (3,1,3,1);
INSERT INTO `sys_user_authority` VALUES (4,1,4,1);
INSERT INTO `sys_user_authority` VALUES (5,1,5,1);
INSERT INTO `sys_user_authority` VALUES (6,1,6,1);
INSERT INTO `sys_user_authority` VALUES (7,1,7,1);
INSERT INTO `sys_user_authority` VALUES (8,1,8,1);
INSERT INTO `sys_user_authority` VALUES (9,1,9,1);
INSERT INTO `sys_user_authority` VALUES (10,1,10,1);
INSERT INTO `sys_user_authority` VALUES (11,1,11,1);
INSERT INTO `sys_user_authority` VALUES (12,1,12,1);
INSERT INTO `sys_user_authority` VALUES (13,1,13,1);
INSERT INTO `sys_user_authority` VALUES (14,1,14,1);
INSERT INTO `sys_user_authority` VALUES (15,1,15,1);
INSERT INTO `sys_user_authority` VALUES (16,1,16,1);
INSERT INTO `sys_user_authority` VALUES (17,1,17,1);
INSERT INTO `sys_user_authority` VALUES (18,1,18,1);
INSERT INTO `sys_user_authority` VALUES (19,1,19,1);
INSERT INTO `sys_user_authority` VALUES (20,1,20,1);
INSERT INTO `sys_user_authority` VALUES (21,1,21,1);
INSERT INTO `sys_user_authority` VALUES (22,1,22,1);
INSERT INTO `sys_user_authority` VALUES (23,1,23,1);
INSERT INTO `sys_user_authority` VALUES (24,1,24,1);
INSERT INTO `sys_user_authority` VALUES (25,1,25,1);
INSERT INTO `sys_user_authority` VALUES (26,1,26,1);
INSERT INTO `sys_user_authority` VALUES (27,1,27,1);
INSERT INTO `sys_user_authority` VALUES (28,1,28,1);
INSERT INTO `sys_user_authority` VALUES (29,1,29,1);
INSERT INTO `sys_user_authority` VALUES (30,1,30,1);
INSERT INTO `sys_user_authority` VALUES (31,1,31,1);
INSERT INTO `sys_user_authority` VALUES (32,1,32,1);
INSERT INTO `sys_user_authority` VALUES (33,1,33,1);
INSERT INTO `sys_user_authority` VALUES (34,1,34,1);
INSERT INTO `sys_user_authority` VALUES (35,1,35,1);
INSERT INTO `sys_user_authority` VALUES (36,1,36,1);
INSERT INTO `sys_user_authority` VALUES (37,1,37,1);
INSERT INTO `sys_user_authority` VALUES (38,1,38,1);
INSERT INTO `sys_user_authority` VALUES (39,1,39,1);
INSERT INTO `sys_user_authority` VALUES (40,1,40,1);
INSERT INTO `sys_user_authority` VALUES (41,1,41,1);
INSERT INTO `sys_user_authority` VALUES (42,1,42,1);
INSERT INTO `sys_user_authority` VALUES (43,1,43,1);
INSERT INTO `sys_user_authority` VALUES (44,1,44,1);
INSERT INTO `sys_user_authority` VALUES (45,1,45,1);
INSERT INTO `sys_user_authority` VALUES (46,1,46,1);
INSERT INTO `sys_user_authority` VALUES (47,1,47,1);
INSERT INTO `sys_user_authority` VALUES (48,1,48,1);
INSERT INTO `sys_user_authority` VALUES (49,1,49,1);
INSERT INTO `sys_user_authority` VALUES (50,1,50,1);
INSERT INTO `sys_user_authority` VALUES (51,2,1,0);
INSERT INTO `sys_user_authority` VALUES (52,2,2,0);
INSERT INTO `sys_user_authority` VALUES (53,2,3,0);
INSERT INTO `sys_user_authority` VALUES (54,2,4,0);
INSERT INTO `sys_user_authority` VALUES (55,2,5,0);
INSERT INTO `sys_user_authority` VALUES (56,2,6,0);
INSERT INTO `sys_user_authority` VALUES (57,2,7,0);
INSERT INTO `sys_user_authority` VALUES (58,2,8,0);
INSERT INTO `sys_user_authority` VALUES (59,2,9,0);
INSERT INTO `sys_user_authority` VALUES (60,2,10,0);
INSERT INTO `sys_user_authority` VALUES (61,2,11,0);
INSERT INTO `sys_user_authority` VALUES (62,2,12,0);
INSERT INTO `sys_user_authority` VALUES (63,2,13,0);
INSERT INTO `sys_user_authority` VALUES (64,2,14,0);
INSERT INTO `sys_user_authority` VALUES (65,2,15,0);
INSERT INTO `sys_user_authority` VALUES (66,2,16,0);
INSERT INTO `sys_user_authority` VALUES (67,2,17,0);
INSERT INTO `sys_user_authority` VALUES (68,2,18,0);
INSERT INTO `sys_user_authority` VALUES (69,2,19,0);
INSERT INTO `sys_user_authority` VALUES (70,2,20,0);
INSERT INTO `sys_user_authority` VALUES (71,2,21,1);
INSERT INTO `sys_user_authority` VALUES (72,2,22,1);
INSERT INTO `sys_user_authority` VALUES (73,2,23,1);
INSERT INTO `sys_user_authority` VALUES (74,2,24,1);
INSERT INTO `sys_user_authority` VALUES (75,2,25,1);
INSERT INTO `sys_user_authority` VALUES (76,2,26,1);
INSERT INTO `sys_user_authority` VALUES (77,2,27,1);
INSERT INTO `sys_user_authority` VALUES (78,2,28,1);
INSERT INTO `sys_user_authority` VALUES (79,2,29,0);
INSERT INTO `sys_user_authority` VALUES (80,2,30,0);
INSERT INTO `sys_user_authority` VALUES (81,2,31,1);
INSERT INTO `sys_user_authority` VALUES (82,2,32,0);
INSERT INTO `sys_user_authority` VALUES (83,2,33,0);
INSERT INTO `sys_user_authority` VALUES (84,2,34,0);
INSERT INTO `sys_user_authority` VALUES (85,2,35,0);
INSERT INTO `sys_user_authority` VALUES (86,2,36,0);
INSERT INTO `sys_user_authority` VALUES (87,2,37,0);
INSERT INTO `sys_user_authority` VALUES (88,2,38,0);
INSERT INTO `sys_user_authority` VALUES (89,2,39,0);
INSERT INTO `sys_user_authority` VALUES (90,2,40,0);
INSERT INTO `sys_user_authority` VALUES (91,2,41,0);
INSERT INTO `sys_user_authority` VALUES (92,2,42,0);
INSERT INTO `sys_user_authority` VALUES (93,2,43,0);
INSERT INTO `sys_user_authority` VALUES (94,2,44,0);
INSERT INTO `sys_user_authority` VALUES (95,2,45,0);
INSERT INTO `sys_user_authority` VALUES (96,2,46,0);
INSERT INTO `sys_user_authority` VALUES (97,2,47,0);
INSERT INTO `sys_user_authority` VALUES (98,2,48,0);
INSERT INTO `sys_user_authority` VALUES (99,2,49,0);
INSERT INTO `sys_user_authority` VALUES (100,2,50,0);
INSERT INTO `sys_user_authority` VALUES (101,1,51,1);
INSERT INTO `sys_user_authority` VALUES (102,2,51,1);
INSERT INTO `sys_user_authority` VALUES (103,1,52,1);
INSERT INTO `sys_user_authority` VALUES (104,2,52,1);
INSERT INTO `sys_user_authority` VALUES (105,1,53,1);
INSERT INTO `sys_user_authority` VALUES (106,2,53,1);
INSERT INTO `sys_user_authority` VALUES (107,1,54,1);
INSERT INTO `sys_user_authority` VALUES (108,2,54,1);
INSERT INTO `sys_user_authority` VALUES (109,1,55,1);
INSERT INTO `sys_user_authority` VALUES (110,2,55,1);
INSERT INTO `sys_user_authority` VALUES (111,1,56,1);
INSERT INTO `sys_user_authority` VALUES (112,2,56,1);
INSERT INTO `sys_user_authority` VALUES (113,1,57,1);
INSERT INTO `sys_user_authority` VALUES (114,2,57,1);
INSERT INTO `sys_user_authority` VALUES (115,1,58,1);
INSERT INTO `sys_user_authority` VALUES (116,2,58,1);
INSERT INTO `sys_user_authority` VALUES (117,1,59,1);
INSERT INTO `sys_user_authority` VALUES (118,2,59,1);
INSERT INTO `sys_user_authority` VALUES (119,1,60,1);
INSERT INTO `sys_user_authority` VALUES (120,2,60,1);
INSERT INTO `sys_user_authority` VALUES (121,1,61,1);
INSERT INTO `sys_user_authority` VALUES (122,2,61,1);
INSERT INTO `sys_user_authority` VALUES (123,1,62,1);
INSERT INTO `sys_user_authority` VALUES (124,2,62,1);
INSERT INTO `sys_user_authority` VALUES (125,1,63,1);
INSERT INTO `sys_user_authority` VALUES (126,2,63,0);
INSERT INTO `sys_user_authority` VALUES (127,1,64,1);
INSERT INTO `sys_user_authority` VALUES (128,2,64,1);
INSERT INTO `sys_user_authority` VALUES (129,1,65,1);
INSERT INTO `sys_user_authority` VALUES (130,2,65,1);
INSERT INTO `sys_user_authority` VALUES (131,1,66,1);
INSERT INTO `sys_user_authority` VALUES (132,2,66,1);
INSERT INTO `sys_user_authority` VALUES (133,1,67,1);
INSERT INTO `sys_user_authority` VALUES (134,2,67,1);
INSERT INTO `sys_user_authority` VALUES (135,1,68,1);
INSERT INTO `sys_user_authority` VALUES (136,2,68,1);
INSERT INTO `sys_user_authority` VALUES (137,1,69,1);
INSERT INTO `sys_user_authority` VALUES (138,2,69,0);
INSERT INTO `sys_user_authority` VALUES (139,1,70,1);
INSERT INTO `sys_user_authority` VALUES (140,2,70,1);
INSERT INTO `sys_user_authority` VALUES (141,1,71,1);
INSERT INTO `sys_user_authority` VALUES (142,2,71,1);
INSERT INTO `sys_user_authority` VALUES (143,1,72,1);
INSERT INTO `sys_user_authority` VALUES (144,2,72,1);
INSERT INTO `sys_user_authority` VALUES (145,1,73,1);
INSERT INTO `sys_user_authority` VALUES (146,2,73,1);
INSERT INTO `sys_user_authority` VALUES (147,1,74,1);
INSERT INTO `sys_user_authority` VALUES (148,2,74,1);
INSERT INTO `sys_user_authority` VALUES (149,1,75,1);
INSERT INTO `sys_user_authority` VALUES (150,2,75,1);
INSERT INTO `sys_user_authority` VALUES (151,1,76,1);
INSERT INTO `sys_user_authority` VALUES (152,2,76,1);
INSERT INTO `sys_user_authority` VALUES (153,1,77,1);
INSERT INTO `sys_user_authority` VALUES (154,2,77,1);
INSERT INTO `sys_user_authority` VALUES (155,1,78,1);
INSERT INTO `sys_user_authority` VALUES (156,2,78,0);
INSERT INTO `sys_user_authority` VALUES (157,1,79,1);
INSERT INTO `sys_user_authority` VALUES (158,2,79,1);
INSERT INTO `sys_user_authority` VALUES (159,1,80,1);
INSERT INTO `sys_user_authority` VALUES (160,2,80,1);
INSERT INTO `sys_user_authority` VALUES (161,1,81,1);
INSERT INTO `sys_user_authority` VALUES (162,2,81,1);
INSERT INTO `sys_user_authority` VALUES (163,1,82,1);
INSERT INTO `sys_user_authority` VALUES (164,2,82,1);
INSERT INTO `sys_user_authority` VALUES (165,1,83,1);
INSERT INTO `sys_user_authority` VALUES (166,2,83,1);
INSERT INTO `sys_user_authority` VALUES (167,1,84,1);
INSERT INTO `sys_user_authority` VALUES (168,2,84,1);
INSERT INTO `sys_user_authority` VALUES (169,1,85,1);
INSERT INTO `sys_user_authority` VALUES (170,2,85,1);
INSERT INTO `sys_user_authority` VALUES (171,1,86,1);
INSERT INTO `sys_user_authority` VALUES (172,2,86,1);
INSERT INTO `sys_user_authority` VALUES (173,1,87,1);
INSERT INTO `sys_user_authority` VALUES (174,2,87,1);
INSERT INTO `sys_user_authority` VALUES (175,1,88,1);
INSERT INTO `sys_user_authority` VALUES (176,2,88,1);
INSERT INTO `sys_user_authority` VALUES (177,1,89,1);
INSERT INTO `sys_user_authority` VALUES (178,2,89,1);
INSERT INTO `sys_user_authority` VALUES (179,1,90,1);
INSERT INTO `sys_user_authority` VALUES (180,2,90,1);
INSERT INTO `sys_user_authority` VALUES (181,1,91,1);
INSERT INTO `sys_user_authority` VALUES (182,2,91,1);
INSERT INTO `sys_user_authority` VALUES (183,1,92,1);
INSERT INTO `sys_user_authority` VALUES (184,2,92,0);
INSERT INTO `sys_user_authority` VALUES (185,1,93,1);
INSERT INTO `sys_user_authority` VALUES (186,2,93,1);
INSERT INTO `sys_user_authority` VALUES (187,1,94,1);
INSERT INTO `sys_user_authority` VALUES (188,2,94,1);
INSERT INTO `sys_user_authority` VALUES (189,1,95,1);
INSERT INTO `sys_user_authority` VALUES (190,2,95,1);
INSERT INTO `sys_user_authority` VALUES (191,1,96,1);
INSERT INTO `sys_user_authority` VALUES (192,2,96,1);
INSERT INTO `sys_user_authority` VALUES (193,1,97,1);
INSERT INTO `sys_user_authority` VALUES (194,2,97,1);
INSERT INTO `sys_user_authority` VALUES (195,1,98,1);
INSERT INTO `sys_user_authority` VALUES (196,2,98,1);
INSERT INTO `sys_user_authority` VALUES (197,1,99,1);
INSERT INTO `sys_user_authority` VALUES (198,2,99,1);
INSERT INTO `sys_user_authority` VALUES (199,1,100,1);
INSERT INTO `sys_user_authority` VALUES (200,2,100,1);
INSERT INTO `sys_user_authority` VALUES (201,1,101,1);
INSERT INTO `sys_user_authority` VALUES (202,2,101,1);
INSERT INTO `sys_user_authority` VALUES (203,1,102,1);
INSERT INTO `sys_user_authority` VALUES (204,2,102,1);
INSERT INTO `sys_user_authority` VALUES (205,1,103,1);
INSERT INTO `sys_user_authority` VALUES (206,2,103,1);
INSERT INTO `sys_user_authority` VALUES (207,1,104,1);
INSERT INTO `sys_user_authority` VALUES (208,2,104,1);
INSERT INTO `sys_user_authority` VALUES (209,1,105,1);
INSERT INTO `sys_user_authority` VALUES (210,2,105,0);
INSERT INTO `sys_user_authority` VALUES (211,1,106,1);
INSERT INTO `sys_user_authority` VALUES (212,2,106,1);
INSERT INTO `sys_user_authority` VALUES (213,1,107,1);
INSERT INTO `sys_user_authority` VALUES (214,2,107,1);
INSERT INTO `sys_user_authority` VALUES (215,1,108,1);
INSERT INTO `sys_user_authority` VALUES (216,2,108,1);
INSERT INTO `sys_user_authority` VALUES (217,1,109,1);
INSERT INTO `sys_user_authority` VALUES (218,2,109,1);
INSERT INTO `sys_user_authority` VALUES (219,1,110,1);
INSERT INTO `sys_user_authority` VALUES (220,2,110,1);
INSERT INTO `sys_user_authority` VALUES (221,1,111,1);
INSERT INTO `sys_user_authority` VALUES (222,2,111,1);
INSERT INTO `sys_user_authority` VALUES (223,1,112,1);
INSERT INTO `sys_user_authority` VALUES (224,2,112,1);
INSERT INTO `sys_user_authority` VALUES (225,1,113,1);
INSERT INTO `sys_user_authority` VALUES (226,2,113,1);
INSERT INTO `sys_user_authority` VALUES (227,1,114,1);
INSERT INTO `sys_user_authority` VALUES (228,2,114,1);
INSERT INTO `sys_user_authority` VALUES (229,1,115,1);
INSERT INTO `sys_user_authority` VALUES (230,2,115,1);
INSERT INTO `sys_user_authority` VALUES (231,1,116,1);
INSERT INTO `sys_user_authority` VALUES (232,2,116,1);
INSERT INTO `sys_user_authority` VALUES (233,1,117,1);
INSERT INTO `sys_user_authority` VALUES (234,2,117,1);
INSERT INTO `sys_user_authority` VALUES (235,1,118,1);
INSERT INTO `sys_user_authority` VALUES (236,2,118,1);
INSERT INTO `sys_user_authority` VALUES (237,1,119,1);
INSERT INTO `sys_user_authority` VALUES (238,2,119,1);
INSERT INTO `sys_user_authority` VALUES (239,1,120,1);
INSERT INTO `sys_user_authority` VALUES (240,2,120,1);
INSERT INTO `sys_user_authority` VALUES (241,1,121,1);
INSERT INTO `sys_user_authority` VALUES (242,2,121,1);
INSERT INTO `sys_user_authority` VALUES (243,1,122,1);
INSERT INTO `sys_user_authority` VALUES (244,2,122,1);
INSERT INTO `sys_user_authority` VALUES (245,1,123,1);
INSERT INTO `sys_user_authority` VALUES (246,2,123,1);
INSERT INTO `sys_user_authority` VALUES (247,1,124,1);
INSERT INTO `sys_user_authority` VALUES (248,2,124,1);
INSERT INTO `sys_user_authority` VALUES (249,1,125,1);
INSERT INTO `sys_user_authority` VALUES (250,2,125,0);
INSERT INTO `sys_user_authority` VALUES (251,1,126,1);
INSERT INTO `sys_user_authority` VALUES (252,2,126,1);
INSERT INTO `sys_user_authority` VALUES (253,1,127,1);
INSERT INTO `sys_user_authority` VALUES (254,2,127,1);
INSERT INTO `sys_user_authority` VALUES (255,1,128,1);
INSERT INTO `sys_user_authority` VALUES (256,2,128,0);
INSERT INTO `sys_user_authority` VALUES (257,1,129,1);
INSERT INTO `sys_user_authority` VALUES (258,2,129,1);
INSERT INTO `sys_user_authority` VALUES (259,1,130,1);
INSERT INTO `sys_user_authority` VALUES (260,2,130,1);
INSERT INTO `sys_user_authority` VALUES (261,1,131,1);
INSERT INTO `sys_user_authority` VALUES (262,2,131,1);
INSERT INTO `sys_user_authority` VALUES (263,1,132,1);
INSERT INTO `sys_user_authority` VALUES (264,2,132,1);
INSERT INTO `sys_user_authority` VALUES (265,1,133,1);
INSERT INTO `sys_user_authority` VALUES (266,2,133,0);
INSERT INTO `sys_user_authority` VALUES (289,1,145,1);
INSERT INTO `sys_user_authority` VALUES (290,2,145,1);
INSERT INTO `sys_user_authority` VALUES (297,1,149,1);
INSERT INTO `sys_user_authority` VALUES (298,2,149,0);
INSERT INTO `sys_user_authority` VALUES (299,1,150,1);
INSERT INTO `sys_user_authority` VALUES (300,2,150,1);
INSERT INTO `sys_user_authority` VALUES (301,1,151,1);
INSERT INTO `sys_user_authority` VALUES (302,2,151,0);
INSERT INTO `sys_user_authority` VALUES (303,1,152,1);
INSERT INTO `sys_user_authority` VALUES (304,2,152,1);
INSERT INTO `sys_user_authority` VALUES (305,1,153,1);
INSERT INTO `sys_user_authority` VALUES (306,2,153,1);
INSERT INTO `sys_user_authority` VALUES (307,1,154,1);
INSERT INTO `sys_user_authority` VALUES (308,2,154,0);
INSERT INTO `sys_user_authority` VALUES (309,1,155,1);
INSERT INTO `sys_user_authority` VALUES (310,2,155,1);
INSERT INTO `sys_user_authority` VALUES (311,3,1,0);
INSERT INTO `sys_user_authority` VALUES (312,3,2,0);
INSERT INTO `sys_user_authority` VALUES (313,3,3,0);
INSERT INTO `sys_user_authority` VALUES (314,3,4,0);
INSERT INTO `sys_user_authority` VALUES (315,3,5,0);
INSERT INTO `sys_user_authority` VALUES (316,3,6,0);
INSERT INTO `sys_user_authority` VALUES (317,3,7,0);
INSERT INTO `sys_user_authority` VALUES (318,3,8,0);
INSERT INTO `sys_user_authority` VALUES (319,3,9,0);
INSERT INTO `sys_user_authority` VALUES (320,3,10,0);
INSERT INTO `sys_user_authority` VALUES (321,3,11,0);
INSERT INTO `sys_user_authority` VALUES (322,3,12,0);
INSERT INTO `sys_user_authority` VALUES (323,3,13,0);
INSERT INTO `sys_user_authority` VALUES (324,3,14,0);
INSERT INTO `sys_user_authority` VALUES (325,3,15,0);
INSERT INTO `sys_user_authority` VALUES (326,3,16,0);
INSERT INTO `sys_user_authority` VALUES (327,3,17,0);
INSERT INTO `sys_user_authority` VALUES (328,3,18,0);
INSERT INTO `sys_user_authority` VALUES (329,3,19,0);
INSERT INTO `sys_user_authority` VALUES (330,3,20,0);
INSERT INTO `sys_user_authority` VALUES (331,3,21,0);
INSERT INTO `sys_user_authority` VALUES (332,3,22,0);
INSERT INTO `sys_user_authority` VALUES (333,3,23,0);
INSERT INTO `sys_user_authority` VALUES (334,3,24,0);
INSERT INTO `sys_user_authority` VALUES (335,3,25,0);
INSERT INTO `sys_user_authority` VALUES (336,3,26,0);
INSERT INTO `sys_user_authority` VALUES (337,3,27,0);
INSERT INTO `sys_user_authority` VALUES (338,3,28,0);
INSERT INTO `sys_user_authority` VALUES (339,3,29,0);
INSERT INTO `sys_user_authority` VALUES (340,3,30,0);
INSERT INTO `sys_user_authority` VALUES (341,3,31,0);
INSERT INTO `sys_user_authority` VALUES (342,3,32,0);
INSERT INTO `sys_user_authority` VALUES (343,3,33,0);
INSERT INTO `sys_user_authority` VALUES (344,3,34,0);
INSERT INTO `sys_user_authority` VALUES (345,3,35,0);
INSERT INTO `sys_user_authority` VALUES (346,3,36,0);
INSERT INTO `sys_user_authority` VALUES (347,3,37,0);
INSERT INTO `sys_user_authority` VALUES (348,3,38,0);
INSERT INTO `sys_user_authority` VALUES (349,3,39,0);
INSERT INTO `sys_user_authority` VALUES (350,3,40,0);
INSERT INTO `sys_user_authority` VALUES (351,3,41,0);
INSERT INTO `sys_user_authority` VALUES (352,3,42,0);
INSERT INTO `sys_user_authority` VALUES (353,3,43,0);
INSERT INTO `sys_user_authority` VALUES (354,3,44,0);
INSERT INTO `sys_user_authority` VALUES (355,3,45,0);
INSERT INTO `sys_user_authority` VALUES (356,3,46,0);
INSERT INTO `sys_user_authority` VALUES (357,3,47,0);
INSERT INTO `sys_user_authority` VALUES (358,3,48,0);
INSERT INTO `sys_user_authority` VALUES (359,3,49,0);
INSERT INTO `sys_user_authority` VALUES (360,3,50,0);
INSERT INTO `sys_user_authority` VALUES (361,3,51,0);
INSERT INTO `sys_user_authority` VALUES (362,3,52,0);
INSERT INTO `sys_user_authority` VALUES (363,3,53,0);
INSERT INTO `sys_user_authority` VALUES (364,3,54,0);
INSERT INTO `sys_user_authority` VALUES (365,3,55,0);
INSERT INTO `sys_user_authority` VALUES (366,3,56,0);
INSERT INTO `sys_user_authority` VALUES (367,3,57,0);
INSERT INTO `sys_user_authority` VALUES (368,3,58,0);
INSERT INTO `sys_user_authority` VALUES (369,3,59,0);
INSERT INTO `sys_user_authority` VALUES (370,3,60,0);
INSERT INTO `sys_user_authority` VALUES (371,3,61,0);
INSERT INTO `sys_user_authority` VALUES (372,3,62,0);
INSERT INTO `sys_user_authority` VALUES (373,3,63,1);
INSERT INTO `sys_user_authority` VALUES (374,3,64,1);
INSERT INTO `sys_user_authority` VALUES (375,3,65,1);
INSERT INTO `sys_user_authority` VALUES (376,3,66,1);
INSERT INTO `sys_user_authority` VALUES (377,3,67,1);
INSERT INTO `sys_user_authority` VALUES (378,3,68,1);
INSERT INTO `sys_user_authority` VALUES (379,3,69,1);
INSERT INTO `sys_user_authority` VALUES (380,3,70,1);
INSERT INTO `sys_user_authority` VALUES (381,3,71,1);
INSERT INTO `sys_user_authority` VALUES (382,3,72,1);
INSERT INTO `sys_user_authority` VALUES (383,3,73,1);
INSERT INTO `sys_user_authority` VALUES (384,3,74,1);
INSERT INTO `sys_user_authority` VALUES (385,3,75,1);
INSERT INTO `sys_user_authority` VALUES (386,3,76,1);
INSERT INTO `sys_user_authority` VALUES (387,3,77,1);
INSERT INTO `sys_user_authority` VALUES (388,3,78,1);
INSERT INTO `sys_user_authority` VALUES (389,3,79,1);
INSERT INTO `sys_user_authority` VALUES (390,3,80,1);
INSERT INTO `sys_user_authority` VALUES (391,3,81,1);
INSERT INTO `sys_user_authority` VALUES (392,3,82,1);
INSERT INTO `sys_user_authority` VALUES (393,3,83,1);
INSERT INTO `sys_user_authority` VALUES (394,3,84,1);
INSERT INTO `sys_user_authority` VALUES (395,3,85,1);
INSERT INTO `sys_user_authority` VALUES (396,3,86,1);
INSERT INTO `sys_user_authority` VALUES (397,3,87,1);
INSERT INTO `sys_user_authority` VALUES (398,3,88,1);
INSERT INTO `sys_user_authority` VALUES (399,3,89,1);
INSERT INTO `sys_user_authority` VALUES (400,3,90,0);
INSERT INTO `sys_user_authority` VALUES (401,3,91,0);
INSERT INTO `sys_user_authority` VALUES (402,3,92,1);
INSERT INTO `sys_user_authority` VALUES (403,3,93,1);
INSERT INTO `sys_user_authority` VALUES (404,3,94,1);
INSERT INTO `sys_user_authority` VALUES (405,3,95,1);
INSERT INTO `sys_user_authority` VALUES (406,3,96,1);
INSERT INTO `sys_user_authority` VALUES (407,3,97,1);
INSERT INTO `sys_user_authority` VALUES (408,3,98,1);
INSERT INTO `sys_user_authority` VALUES (409,3,99,1);
INSERT INTO `sys_user_authority` VALUES (410,3,100,1);
INSERT INTO `sys_user_authority` VALUES (411,3,101,1);
INSERT INTO `sys_user_authority` VALUES (412,3,102,1);
INSERT INTO `sys_user_authority` VALUES (413,3,103,1);
INSERT INTO `sys_user_authority` VALUES (414,3,104,1);
INSERT INTO `sys_user_authority` VALUES (415,3,105,1);
INSERT INTO `sys_user_authority` VALUES (416,3,106,1);
INSERT INTO `sys_user_authority` VALUES (417,3,107,1);
INSERT INTO `sys_user_authority` VALUES (418,3,108,1);
INSERT INTO `sys_user_authority` VALUES (419,3,109,1);
INSERT INTO `sys_user_authority` VALUES (420,3,110,1);
INSERT INTO `sys_user_authority` VALUES (421,3,111,1);
INSERT INTO `sys_user_authority` VALUES (422,3,112,1);
INSERT INTO `sys_user_authority` VALUES (423,3,113,1);
INSERT INTO `sys_user_authority` VALUES (424,3,114,1);
INSERT INTO `sys_user_authority` VALUES (425,3,115,1);
INSERT INTO `sys_user_authority` VALUES (426,3,116,1);
INSERT INTO `sys_user_authority` VALUES (427,3,117,1);
INSERT INTO `sys_user_authority` VALUES (428,3,118,1);
INSERT INTO `sys_user_authority` VALUES (429,3,119,1);
INSERT INTO `sys_user_authority` VALUES (430,3,120,1);
INSERT INTO `sys_user_authority` VALUES (431,3,121,1);
INSERT INTO `sys_user_authority` VALUES (432,3,122,1);
INSERT INTO `sys_user_authority` VALUES (433,3,123,1);
INSERT INTO `sys_user_authority` VALUES (434,3,124,1);
INSERT INTO `sys_user_authority` VALUES (435,3,125,1);
INSERT INTO `sys_user_authority` VALUES (436,3,126,1);
INSERT INTO `sys_user_authority` VALUES (437,3,127,1);
INSERT INTO `sys_user_authority` VALUES (438,3,128,1);
INSERT INTO `sys_user_authority` VALUES (439,3,129,1);
INSERT INTO `sys_user_authority` VALUES (440,3,130,1);
INSERT INTO `sys_user_authority` VALUES (441,3,131,1);
INSERT INTO `sys_user_authority` VALUES (442,3,132,1);
INSERT INTO `sys_user_authority` VALUES (443,3,133,1);
INSERT INTO `sys_user_authority` VALUES (455,3,145,1);
INSERT INTO `sys_user_authority` VALUES (459,3,149,1);
INSERT INTO `sys_user_authority` VALUES (460,3,150,0);
INSERT INTO `sys_user_authority` VALUES (461,3,151,0);
INSERT INTO `sys_user_authority` VALUES (462,3,152,0);
INSERT INTO `sys_user_authority` VALUES (463,3,153,0);
INSERT INTO `sys_user_authority` VALUES (464,3,154,0);
INSERT INTO `sys_user_authority` VALUES (465,3,155,1);
INSERT INTO `sys_user_authority` VALUES (621,1,156,1);
INSERT INTO `sys_user_authority` VALUES (622,1,157,1);
INSERT INTO `sys_user_authority` VALUES (623,1,158,1);
INSERT INTO `sys_user_authority` VALUES (625,1,160,1);
INSERT INTO `sys_user_authority` VALUES (626,1,161,1);
INSERT INTO `sys_user_authority` VALUES (627,1,162,1);
INSERT INTO `sys_user_authority` VALUES (628,1,163,1);
INSERT INTO `sys_user_authority` VALUES (642,1,177,1);
INSERT INTO `sys_user_authority` VALUES (643,1,178,1);
INSERT INTO `sys_user_authority` VALUES (645,1,181,1);
INSERT INTO `sys_user_authority` VALUES (651,1,187,1);
INSERT INTO `sys_user_authority` VALUES (652,1,188,1);
INSERT INTO `sys_user_authority` VALUES (654,1,190,1);
INSERT INTO `sys_user_authority` VALUES (656,1,192,1);
INSERT INTO `sys_user_authority` VALUES (659,1,196,1);
INSERT INTO `sys_user_authority` VALUES (661,1,198,1);
INSERT INTO `sys_user_authority` VALUES (667,1,204,1);
INSERT INTO `sys_user_authority` VALUES (668,1,205,1);
INSERT INTO `sys_user_authority` VALUES (672,1,209,1);
INSERT INTO `sys_user_authority` VALUES (674,1,211,1);
INSERT INTO `sys_user_authority` VALUES (675,1,212,1);
INSERT INTO `sys_user_authority` VALUES (676,1,213,1);
INSERT INTO `sys_user_authority` VALUES (677,1,214,1);
INSERT INTO `sys_user_authority` VALUES (678,1,215,1);
INSERT INTO `sys_user_authority` VALUES (679,1,216,1);
INSERT INTO `sys_user_authority` VALUES (682,1,220,1);
INSERT INTO `sys_user_authority` VALUES (683,1,221,1);
INSERT INTO `sys_user_authority` VALUES (684,1,232,1);
INSERT INTO `sys_user_authority` VALUES (685,1,233,1);
INSERT INTO `sys_user_authority` VALUES (686,1,234,1);
INSERT INTO `sys_user_authority` VALUES (687,1,235,1);
INSERT INTO `sys_user_authority` VALUES (688,1,236,1);
INSERT INTO `sys_user_authority` VALUES (689,1,237,1);
INSERT INTO `sys_user_authority` VALUES (690,1,238,1);
INSERT INTO `sys_user_authority` VALUES (691,1,239,1);
INSERT INTO `sys_user_authority` VALUES (692,1,240,1);
INSERT INTO `sys_user_authority` VALUES (693,1,241,1);
INSERT INTO `sys_user_authority` VALUES (694,1,242,1);
INSERT INTO `sys_user_authority` VALUES (697,1,228,1);
INSERT INTO `sys_user_authority` VALUES (698,1,229,1);
INSERT INTO `sys_user_authority` VALUES (699,1,230,1);
INSERT INTO `sys_user_authority` VALUES (700,1,231,1);
INSERT INTO `sys_user_authority` VALUES (706,1,243,1);
INSERT INTO `sys_user_authority` VALUES (708,1,222,1);
INSERT INTO `sys_user_authority` VALUES (709,1,244,1);
INSERT INTO `sys_user_authority` VALUES (710,1,245,1);
INSERT INTO `sys_user_authority` VALUES (715,1,267,1);
INSERT INTO `sys_user_authority` VALUES (716,1,268,1);
INSERT INTO `sys_user_authority` VALUES (717,2,269,1);
INSERT INTO `sys_user_authority` VALUES (718,2,270,1);
INSERT INTO `sys_user_authority` VALUES (719,2,271,1);
INSERT INTO `sys_user_authority` VALUES (720,2,272,1);
INSERT INTO `sys_user_authority` VALUES (721,2,273,1);
INSERT INTO `sys_user_authority` VALUES (722,2,274,1);
INSERT INTO `sys_user_authority` VALUES (723,1,269,1);
INSERT INTO `sys_user_authority` VALUES (724,1,270,1);
INSERT INTO `sys_user_authority` VALUES (725,1,271,1);
INSERT INTO `sys_user_authority` VALUES (726,1,272,1);
INSERT INTO `sys_user_authority` VALUES (727,1,273,1);
INSERT INTO `sys_user_authority` VALUES (728,1,274,1);
INSERT INTO `sys_user_authority` VALUES (731,1,277,1);
INSERT INTO `sys_user_authority` VALUES (736,1,282,1);
INSERT INTO `sys_user_authority` VALUES (742,1,287,1);
INSERT INTO `sys_user_authority` VALUES (743,1,288,1);
INSERT INTO `sys_user_authority` VALUES (744,1,289,1);
INSERT INTO `sys_user_authority` VALUES (747,1,224,1);
INSERT INTO `sys_user_authority` VALUES (748,1,246,1);
INSERT INTO `sys_user_authority` VALUES (749,1,247,1);
INSERT INTO `sys_user_authority` VALUES (750,1,292,1);
INSERT INTO `sys_user_authority` VALUES (753,1,295,1);
INSERT INTO `sys_user_authority` VALUES (754,1,296,1);
INSERT INTO `sys_user_authority` VALUES (757,1,299,1);
INSERT INTO `sys_user_authority` VALUES (758,1,300,1);
INSERT INTO `sys_user_authority` VALUES (759,1,301,1);
INSERT INTO `sys_user_authority` VALUES (760,1,302,1);
INSERT INTO `sys_user_authority` VALUES (763,1,248,1);
INSERT INTO `sys_user_authority` VALUES (764,1,249,1);
INSERT INTO `sys_user_authority` VALUES (765,1,250,1);
INSERT INTO `sys_user_authority` VALUES (766,1,252,1);
INSERT INTO `sys_user_authority` VALUES (767,1,225,1);
INSERT INTO `sys_user_authority` VALUES (771,1,226,1);
INSERT INTO `sys_user_authority` VALUES (772,1,251,1);
INSERT INTO `sys_user_authority` VALUES (773,1,254,1);
INSERT INTO `sys_user_authority` VALUES (774,1,255,1);
INSERT INTO `sys_user_authority` VALUES (775,1,308,1);
INSERT INTO `sys_user_authority` VALUES (780,1,313,1);
INSERT INTO `sys_user_authority` VALUES (781,1,314,1);
INSERT INTO `sys_user_authority` VALUES (782,1,315,1);
INSERT INTO `sys_user_authority` VALUES (784,1,317,1);
INSERT INTO `sys_user_authority` VALUES (785,1,318,1);
INSERT INTO `sys_user_authority` VALUES (786,1,319,1);
INSERT INTO `sys_user_authority` VALUES (788,1,321,1);
INSERT INTO `sys_user_authority` VALUES (789,1,323,1);
INSERT INTO `sys_user_authority` VALUES (790,1,322,1);
INSERT INTO `sys_user_authority` VALUES (791,1,325,1);
INSERT INTO `sys_user_authority` VALUES (792,1,326,1);
INSERT INTO `sys_user_authority` VALUES (793,1,327,1);
INSERT INTO `sys_user_authority` VALUES (794,1,328,1);
INSERT INTO `sys_user_authority` VALUES (795,1,329,1);
INSERT INTO `sys_user_authority` VALUES (796,1,330,1);
INSERT INTO `sys_user_authority` VALUES (797,1,331,1);
INSERT INTO `sys_user_authority` VALUES (798,1,332,1);
INSERT INTO `sys_user_authority` VALUES (799,1,333,1);
INSERT INTO `sys_user_authority` VALUES (800,1,334,1);
INSERT INTO `sys_user_authority` VALUES (801,1,335,1);
INSERT INTO `sys_user_authority` VALUES (802,1,336,1);
INSERT INTO `sys_user_authority` VALUES (803,1,337,1);
INSERT INTO `sys_user_authority` VALUES (804,1,338,1);
INSERT INTO `sys_user_authority` VALUES (805,1,339,1);
INSERT INTO `sys_user_authority` VALUES (806,1,340,1);
INSERT INTO `sys_user_authority` VALUES (807,1,341,1);
INSERT INTO `sys_user_authority` VALUES (808,1,342,1);
INSERT INTO `sys_user_authority` VALUES (809,1,343,1);
INSERT INTO `sys_user_authority` VALUES (810,1,344,1);
INSERT INTO `sys_user_authority` VALUES (813,1,347,1);
INSERT INTO `sys_user_authority` VALUES (815,1,349,1);
INSERT INTO `sys_user_authority` VALUES (816,1,350,1);
INSERT INTO `sys_user_authority` VALUES (819,1,353,1);
INSERT INTO `sys_user_authority` VALUES (821,1,355,1);
INSERT INTO `sys_user_authority` VALUES (822,1,356,1);
INSERT INTO `sys_user_authority` VALUES (828,1,362,1);
INSERT INTO `sys_user_authority` VALUES (829,1,363,1);
INSERT INTO `sys_user_authority` VALUES (830,1,364,1);
INSERT INTO `sys_user_authority` VALUES (831,1,365,1);
INSERT INTO `sys_user_authority` VALUES (832,1,366,1);
INSERT INTO `sys_user_authority` VALUES (833,1,369,1);
INSERT INTO `sys_user_authority` VALUES (834,1,368,1);
INSERT INTO `sys_user_authority` VALUES (835,1,367,1);
INSERT INTO `sys_user_authority` VALUES (836,1,370,1);
INSERT INTO `sys_user_authority` VALUES (837,1,371,1);
INSERT INTO `sys_user_authority` VALUES (838,1,372,1);
INSERT INTO `sys_user_authority` VALUES (839,1,373,1);
INSERT INTO `sys_user_authority` VALUES (840,1,374,1);
INSERT INTO `sys_user_authority` VALUES (841,1,375,1);
INSERT INTO `sys_user_authority` VALUES (842,1,376,1);
INSERT INTO `sys_user_authority` VALUES (843,1,377,1);
INSERT INTO `sys_user_authority` VALUES (844,1,378,1);
INSERT INTO `sys_user_authority` VALUES (845,1,379,1);
INSERT INTO `sys_user_authority` VALUES (848,1,383,1);
INSERT INTO `sys_user_authority` VALUES (849,1,382,1);
INSERT INTO `sys_user_authority` VALUES (850,1,384,1);
INSERT INTO `sys_user_authority` VALUES (851,1,385,1);
INSERT INTO `sys_user_authority` VALUES (852,1,386,1);
INSERT INTO `sys_user_authority` VALUES (855,1,389,1);
INSERT INTO `sys_user_authority` VALUES (856,1,390,1);
INSERT INTO `sys_user_authority` VALUES (859,1,393,1);
INSERT INTO `sys_user_authority` VALUES (861,1,395,1);
INSERT INTO `sys_user_authority` VALUES (863,1,397,1);
INSERT INTO `sys_user_authority` VALUES (866,1,400,1);
INSERT INTO `sys_user_authority` VALUES (869,1,403,1);
INSERT INTO `sys_user_authority` VALUES (872,1,406,1);
INSERT INTO `sys_user_authority` VALUES (874,1,408,1);
INSERT INTO `sys_user_authority` VALUES (875,1,410,1);
INSERT INTO `sys_user_authority` VALUES (876,1,409,1);
INSERT INTO `sys_user_authority` VALUES (877,2,411,1);
INSERT INTO `sys_user_authority` VALUES (878,1,411,1);
INSERT INTO `sys_user_authority` VALUES (881,1,414,1);
INSERT INTO `sys_user_authority` VALUES (883,1,416,1);
INSERT INTO `sys_user_authority` VALUES (885,1,419,1);
INSERT INTO `sys_user_authority` VALUES (886,2,409,1);
INSERT INTO `sys_user_authority` VALUES (890,1,425,1);
INSERT INTO `sys_user_authority` VALUES (894,1,429,1);
INSERT INTO `sys_user_authority` VALUES (895,1,223,1);
INSERT INTO `sys_user_authority` VALUES (896,1,227,1);
INSERT INTO `sys_user_authority` VALUES (897,2,375,1);
INSERT INTO `sys_user_authority` VALUES (898,2,377,1);
INSERT INTO `sys_user_authority` VALUES (899,2,382,1);
INSERT INTO `sys_user_authority` VALUES (900,2,383,1);
INSERT INTO `sys_user_authority` VALUES (901,2,384,1);
INSERT INTO `sys_user_authority` VALUES (902,2,385,1);
INSERT INTO `sys_user_authority` VALUES (903,2,386,1);
INSERT INTO `sys_user_authority` VALUES (904,2,321,1);
INSERT INTO `sys_user_authority` VALUES (905,2,322,1);
INSERT INTO `sys_user_authority` VALUES (906,2,323,1);
INSERT INTO `sys_user_authority` VALUES (908,2,410,1);
INSERT INTO `sys_user_authority` VALUES (909,2,292,1);
INSERT INTO `sys_user_authority` VALUES (910,2,177,1);
INSERT INTO `sys_user_authority` VALUES (911,2,355,1);
INSERT INTO `sys_user_authority` VALUES (912,2,181,1);
INSERT INTO `sys_user_authority` VALUES (914,2,188,1);
INSERT INTO `sys_user_authority` VALUES (916,2,187,1);
INSERT INTO `sys_user_authority` VALUES (918,2,190,1);
INSERT INTO `sys_user_authority` VALUES (920,2,192,1);
INSERT INTO `sys_user_authority` VALUES (922,2,196,1);
INSERT INTO `sys_user_authority` VALUES (924,2,198,1);
INSERT INTO `sys_user_authority` VALUES (926,2,209,1);
INSERT INTO `sys_user_authority` VALUES (928,2,178,1);
INSERT INTO `sys_user_authority` VALUES (935,2,204,1);
INSERT INTO `sys_user_authority` VALUES (936,2,205,1);
INSERT INTO `sys_user_authority` VALUES (937,2,363,1);
INSERT INTO `sys_user_authority` VALUES (938,2,364,1);
INSERT INTO `sys_user_authority` VALUES (939,2,365,1);
INSERT INTO `sys_user_authority` VALUES (940,2,429,1);
INSERT INTO `sys_user_authority` VALUES (941,2,325,1);
INSERT INTO `sys_user_authority` VALUES (942,2,326,0);
INSERT INTO `sys_user_authority` VALUES (943,2,327,1);
INSERT INTO `sys_user_authority` VALUES (946,2,356,1);
INSERT INTO `sys_user_authority` VALUES (950,2,373,1);
INSERT INTO `sys_user_authority` VALUES (951,2,376,1);
INSERT INTO `sys_user_authority` VALUES (952,2,328,1);
INSERT INTO `sys_user_authority` VALUES (955,2,393,1);
INSERT INTO `sys_user_authority` VALUES (957,2,395,1);
INSERT INTO `sys_user_authority` VALUES (958,2,329,1);
INSERT INTO `sys_user_authority` VALUES (961,2,400,1);
INSERT INTO `sys_user_authority` VALUES (964,2,403,1);
INSERT INTO `sys_user_authority` VALUES (965,2,330,1);
INSERT INTO `sys_user_authority` VALUES (968,2,389,1);
INSERT INTO `sys_user_authority` VALUES (969,2,390,1);
INSERT INTO `sys_user_authority` VALUES (971,2,397,1);
INSERT INTO `sys_user_authority` VALUES (972,2,331,1);
INSERT INTO `sys_user_authority` VALUES (975,2,406,1);
INSERT INTO `sys_user_authority` VALUES (976,2,408,1);
INSERT INTO `sys_user_authority` VALUES (978,2,332,1);
INSERT INTO `sys_user_authority` VALUES (981,2,414,1);
INSERT INTO `sys_user_authority` VALUES (983,2,416,1);
INSERT INTO `sys_user_authority` VALUES (984,2,425,1);
INSERT INTO `sys_user_authority` VALUES (985,2,344,1);
INSERT INTO `sys_user_authority` VALUES (986,2,343,1);
INSERT INTO `sys_user_authority` VALUES (987,2,342,1);
INSERT INTO `sys_user_authority` VALUES (988,2,341,1);
INSERT INTO `sys_user_authority` VALUES (989,2,340,1);
INSERT INTO `sys_user_authority` VALUES (990,2,339,1);
INSERT INTO `sys_user_authority` VALUES (991,2,338,1);
INSERT INTO `sys_user_authority` VALUES (992,2,337,1);
INSERT INTO `sys_user_authority` VALUES (993,2,336,1);
INSERT INTO `sys_user_authority` VALUES (994,2,335,1);
INSERT INTO `sys_user_authority` VALUES (995,2,334,1);
INSERT INTO `sys_user_authority` VALUES (996,2,333,1);
INSERT INTO `sys_user_authority` VALUES (997,2,156,0);
INSERT INTO `sys_user_authority` VALUES (998,2,157,1);
INSERT INTO `sys_user_authority` VALUES (999,2,158,1);
INSERT INTO `sys_user_authority` VALUES (1001,2,160,1);
INSERT INTO `sys_user_authority` VALUES (1002,2,161,1);
INSERT INTO `sys_user_authority` VALUES (1003,2,162,1);
INSERT INTO `sys_user_authority` VALUES (1004,2,163,1);
INSERT INTO `sys_user_authority` VALUES (1022,2,220,1);
INSERT INTO `sys_user_authority` VALUES (1023,2,228,1);
INSERT INTO `sys_user_authority` VALUES (1026,2,268,1);
INSERT INTO `sys_user_authority` VALUES (1028,2,229,1);
INSERT INTO `sys_user_authority` VALUES (1030,2,287,1);
INSERT INTO `sys_user_authority` VALUES (1031,2,288,1);
INSERT INTO `sys_user_authority` VALUES (1032,2,289,1);
INSERT INTO `sys_user_authority` VALUES (1034,2,230,1);
INSERT INTO `sys_user_authority` VALUES (1037,2,299,1);
INSERT INTO `sys_user_authority` VALUES (1038,2,300,1);
INSERT INTO `sys_user_authority` VALUES (1039,2,308,1);
INSERT INTO `sys_user_authority` VALUES (1040,2,231,1);
INSERT INTO `sys_user_authority` VALUES (1043,2,313,1);
INSERT INTO `sys_user_authority` VALUES (1044,2,314,1);
INSERT INTO `sys_user_authority` VALUES (1045,2,315,1);
INSERT INTO `sys_user_authority` VALUES (1047,2,221,1);
INSERT INTO `sys_user_authority` VALUES (1048,2,232,1);
INSERT INTO `sys_user_authority` VALUES (1050,2,233,1);
INSERT INTO `sys_user_authority` VALUES (1052,2,234,1);
INSERT INTO `sys_user_authority` VALUES (1054,2,235,1);
INSERT INTO `sys_user_authority` VALUES (1056,2,236,1);
INSERT INTO `sys_user_authority` VALUES (1058,2,237,1);
INSERT INTO `sys_user_authority` VALUES (1060,2,238,1);
INSERT INTO `sys_user_authority` VALUES (1062,2,239,1);
INSERT INTO `sys_user_authority` VALUES (1064,2,240,1);
INSERT INTO `sys_user_authority` VALUES (1066,2,241,1);
INSERT INTO `sys_user_authority` VALUES (1068,2,242,1);
INSERT INTO `sys_user_authority` VALUES (1071,2,301,1);
INSERT INTO `sys_user_authority` VALUES (1072,2,302,1);
INSERT INTO `sys_user_authority` VALUES (1073,2,222,1);
INSERT INTO `sys_user_authority` VALUES (1074,2,243,1);
INSERT INTO `sys_user_authority` VALUES (1076,2,244,1);
INSERT INTO `sys_user_authority` VALUES (1079,2,267,1);
INSERT INTO `sys_user_authority` VALUES (1081,2,277,1);
INSERT INTO `sys_user_authority` VALUES (1082,2,282,1);
INSERT INTO `sys_user_authority` VALUES (1083,2,245,1);
INSERT INTO `sys_user_authority` VALUES (1085,2,223,1);
INSERT INTO `sys_user_authority` VALUES (1086,2,246,1);
INSERT INTO `sys_user_authority` VALUES (1089,2,224,1);
INSERT INTO `sys_user_authority` VALUES (1090,2,295,1);
INSERT INTO `sys_user_authority` VALUES (1091,2,296,1);
INSERT INTO `sys_user_authority` VALUES (1092,2,247,1);
INSERT INTO `sys_user_authority` VALUES (1094,2,225,1);
INSERT INTO `sys_user_authority` VALUES (1095,2,248,1);
INSERT INTO `sys_user_authority` VALUES (1097,2,249,1);
INSERT INTO `sys_user_authority` VALUES (1099,2,250,1);
INSERT INTO `sys_user_authority` VALUES (1101,2,226,1);
INSERT INTO `sys_user_authority` VALUES (1102,2,251,1);
INSERT INTO `sys_user_authority` VALUES (1105,2,347,1);
INSERT INTO `sys_user_authority` VALUES (1107,2,349,1);
INSERT INTO `sys_user_authority` VALUES (1108,2,350,1);
INSERT INTO `sys_user_authority` VALUES (1109,2,353,1);
INSERT INTO `sys_user_authority` VALUES (1110,2,254,1);
INSERT INTO `sys_user_authority` VALUES (1113,2,252,1);
INSERT INTO `sys_user_authority` VALUES (1114,2,366,1);
INSERT INTO `sys_user_authority` VALUES (1115,2,372,1);
INSERT INTO `sys_user_authority` VALUES (1116,2,374,1);
INSERT INTO `sys_user_authority` VALUES (1117,2,378,1);
INSERT INTO `sys_user_authority` VALUES (1118,2,379,1);
INSERT INTO `sys_user_authority` VALUES (1121,2,255,1);
INSERT INTO `sys_user_authority` VALUES (1125,2,317,1);
INSERT INTO `sys_user_authority` VALUES (1126,2,318,1);
INSERT INTO `sys_user_authority` VALUES (1127,2,319,1);
INSERT INTO `sys_user_authority` VALUES (1128,2,227,1);
INSERT INTO `sys_user_authority` VALUES (1129,2,211,0);
INSERT INTO `sys_user_authority` VALUES (1130,2,212,1);
INSERT INTO `sys_user_authority` VALUES (1131,2,213,1);
INSERT INTO `sys_user_authority` VALUES (1132,2,419,1);
INSERT INTO `sys_user_authority` VALUES (1133,2,214,1);
INSERT INTO `sys_user_authority` VALUES (1134,2,215,1);
INSERT INTO `sys_user_authority` VALUES (1135,2,367,1);
INSERT INTO `sys_user_authority` VALUES (1136,2,368,1);
INSERT INTO `sys_user_authority` VALUES (1137,2,369,1);
INSERT INTO `sys_user_authority` VALUES (1138,2,216,1);
INSERT INTO `sys_user_authority` VALUES (1139,2,370,1);
INSERT INTO `sys_user_authority` VALUES (1140,2,371,1);
INSERT INTO `sys_user_authority` VALUES (1141,1,432,1);
INSERT INTO `sys_user_authority` VALUES (1144,1,431,1);
INSERT INTO `sys_user_authority` VALUES (1145,1,436,1);
INSERT INTO `sys_user_authority` VALUES (1146,1,437,1);
INSERT INTO `sys_user_authority` VALUES (1147,1,438,1);
INSERT INTO `sys_user_authority` VALUES (1149,1,435,1);
INSERT INTO `sys_user_authority` VALUES (1153,1,443,1);
INSERT INTO `sys_user_authority` VALUES (1154,1,444,1);
INSERT INTO `sys_user_authority` VALUES (1156,1,446,1);
INSERT INTO `sys_user_authority` VALUES (1157,4,133,1);
INSERT INTO `sys_user_authority` VALUES (1158,4,325,0);
INSERT INTO `sys_user_authority` VALUES (1159,4,326,1);
INSERT INTO `sys_user_authority` VALUES (1160,4,327,0);
INSERT INTO `sys_user_authority` VALUES (1161,4,328,0);
INSERT INTO `sys_user_authority` VALUES (1162,4,329,0);
INSERT INTO `sys_user_authority` VALUES (1163,4,330,0);
INSERT INTO `sys_user_authority` VALUES (1164,4,331,0);
INSERT INTO `sys_user_authority` VALUES (1165,4,332,0);
INSERT INTO `sys_user_authority` VALUES (1166,4,333,0);
INSERT INTO `sys_user_authority` VALUES (1167,4,334,0);
INSERT INTO `sys_user_authority` VALUES (1168,4,335,0);
INSERT INTO `sys_user_authority` VALUES (1169,4,336,0);
INSERT INTO `sys_user_authority` VALUES (1170,4,337,0);
INSERT INTO `sys_user_authority` VALUES (1171,4,338,0);
INSERT INTO `sys_user_authority` VALUES (1172,4,339,0);
INSERT INTO `sys_user_authority` VALUES (1173,4,340,0);
INSERT INTO `sys_user_authority` VALUES (1174,4,341,0);
INSERT INTO `sys_user_authority` VALUES (1175,4,342,0);
INSERT INTO `sys_user_authority` VALUES (1176,4,343,0);
INSERT INTO `sys_user_authority` VALUES (1177,4,344,0);
INSERT INTO `sys_user_authority` VALUES (1180,4,356,1);
INSERT INTO `sys_user_authority` VALUES (1184,4,373,1);
INSERT INTO `sys_user_authority` VALUES (1185,4,376,1);
INSERT INTO `sys_user_authority` VALUES (1188,4,393,1);
INSERT INTO `sys_user_authority` VALUES (1190,4,395,1);
INSERT INTO `sys_user_authority` VALUES (1191,2,432,1);
INSERT INTO `sys_user_authority` VALUES (1194,2,436,1);
INSERT INTO `sys_user_authority` VALUES (1195,2,437,1);
INSERT INTO `sys_user_authority` VALUES (1196,2,438,1);
INSERT INTO `sys_user_authority` VALUES (1198,2,435,1);
INSERT INTO `sys_user_authority` VALUES (1201,2,443,1);
INSERT INTO `sys_user_authority` VALUES (1202,2,444,1);
INSERT INTO `sys_user_authority` VALUES (1204,2,446,1);
INSERT INTO `sys_user_authority` VALUES (1205,3,269,1);
INSERT INTO `sys_user_authority` VALUES (1206,3,270,1);
INSERT INTO `sys_user_authority` VALUES (1207,3,271,1);
INSERT INTO `sys_user_authority` VALUES (1208,3,272,1);
INSERT INTO `sys_user_authority` VALUES (1209,3,273,1);
INSERT INTO `sys_user_authority` VALUES (1210,3,274,1);
INSERT INTO `sys_user_authority` VALUES (1212,3,321,1);
INSERT INTO `sys_user_authority` VALUES (1213,3,322,1);
INSERT INTO `sys_user_authority` VALUES (1214,3,323,1);
INSERT INTO `sys_user_authority` VALUES (1215,3,375,0);
INSERT INTO `sys_user_authority` VALUES (1216,3,377,1);
INSERT INTO `sys_user_authority` VALUES (1217,3,382,1);
INSERT INTO `sys_user_authority` VALUES (1218,3,383,1);
INSERT INTO `sys_user_authority` VALUES (1219,3,384,1);
INSERT INTO `sys_user_authority` VALUES (1220,3,385,1);
INSERT INTO `sys_user_authority` VALUES (1221,3,386,1);
INSERT INTO `sys_user_authority` VALUES (1222,3,410,1);
INSERT INTO `sys_user_authority` VALUES (1223,3,409,1);
INSERT INTO `sys_user_authority` VALUES (1224,3,211,1);
INSERT INTO `sys_user_authority` VALUES (1225,3,156,1);
INSERT INTO `sys_user_authority` VALUES (1226,3,325,1);
INSERT INTO `sys_user_authority` VALUES (1227,3,326,0);
INSERT INTO `sys_user_authority` VALUES (1228,3,327,1);
INSERT INTO `sys_user_authority` VALUES (1229,3,328,1);
INSERT INTO `sys_user_authority` VALUES (1230,3,329,1);
INSERT INTO `sys_user_authority` VALUES (1231,3,330,1);
INSERT INTO `sys_user_authority` VALUES (1232,3,331,1);
INSERT INTO `sys_user_authority` VALUES (1233,3,332,1);
INSERT INTO `sys_user_authority` VALUES (1234,3,333,1);
INSERT INTO `sys_user_authority` VALUES (1235,3,334,1);
INSERT INTO `sys_user_authority` VALUES (1236,3,335,1);
INSERT INTO `sys_user_authority` VALUES (1237,3,336,1);
INSERT INTO `sys_user_authority` VALUES (1238,3,337,1);
INSERT INTO `sys_user_authority` VALUES (1239,3,338,1);
INSERT INTO `sys_user_authority` VALUES (1240,3,339,1);
INSERT INTO `sys_user_authority` VALUES (1241,3,340,1);
INSERT INTO `sys_user_authority` VALUES (1242,3,341,1);
INSERT INTO `sys_user_authority` VALUES (1243,3,342,1);
INSERT INTO `sys_user_authority` VALUES (1244,3,343,1);
INSERT INTO `sys_user_authority` VALUES (1245,3,344,1);
INSERT INTO `sys_user_authority` VALUES (1248,3,356,1);
INSERT INTO `sys_user_authority` VALUES (1252,3,373,1);
INSERT INTO `sys_user_authority` VALUES (1253,3,376,1);
INSERT INTO `sys_user_authority` VALUES (1256,3,393,1);
INSERT INTO `sys_user_authority` VALUES (1258,3,395,1);
INSERT INTO `sys_user_authority` VALUES (1261,3,400,1);
INSERT INTO `sys_user_authority` VALUES (1264,3,403,1);
INSERT INTO `sys_user_authority` VALUES (1267,3,389,1);
INSERT INTO `sys_user_authority` VALUES (1268,3,390,1);
INSERT INTO `sys_user_authority` VALUES (1270,3,397,1);
INSERT INTO `sys_user_authority` VALUES (1273,3,406,1);
INSERT INTO `sys_user_authority` VALUES (1275,3,408,1);
INSERT INTO `sys_user_authority` VALUES (1278,3,414,1);
INSERT INTO `sys_user_authority` VALUES (1280,3,416,1);
INSERT INTO `sys_user_authority` VALUES (1281,3,425,1);
INSERT INTO `sys_user_authority` VALUES (1282,3,157,1);
INSERT INTO `sys_user_authority` VALUES (1283,3,220,1);
INSERT INTO `sys_user_authority` VALUES (1284,3,221,1);
INSERT INTO `sys_user_authority` VALUES (1285,3,222,1);
INSERT INTO `sys_user_authority` VALUES (1286,3,223,1);
INSERT INTO `sys_user_authority` VALUES (1287,3,224,1);
INSERT INTO `sys_user_authority` VALUES (1288,3,225,1);
INSERT INTO `sys_user_authority` VALUES (1289,3,226,1);
INSERT INTO `sys_user_authority` VALUES (1290,3,227,1);
INSERT INTO `sys_user_authority` VALUES (1291,3,160,1);
INSERT INTO `sys_user_authority` VALUES (1292,3,158,1);
INSERT INTO `sys_user_authority` VALUES (1294,3,161,1);
INSERT INTO `sys_user_authority` VALUES (1295,3,162,1);
INSERT INTO `sys_user_authority` VALUES (1296,3,163,1);
INSERT INTO `sys_user_authority` VALUES (1314,3,228,1);
INSERT INTO `sys_user_authority` VALUES (1315,3,229,1);
INSERT INTO `sys_user_authority` VALUES (1316,3,230,1);
INSERT INTO `sys_user_authority` VALUES (1317,3,231,1);
INSERT INTO `sys_user_authority` VALUES (1320,3,268,1);
INSERT INTO `sys_user_authority` VALUES (1324,3,287,1);
INSERT INTO `sys_user_authority` VALUES (1325,3,288,1);
INSERT INTO `sys_user_authority` VALUES (1326,3,289,1);
INSERT INTO `sys_user_authority` VALUES (1330,3,299,1);
INSERT INTO `sys_user_authority` VALUES (1331,3,300,1);
INSERT INTO `sys_user_authority` VALUES (1332,3,308,1);
INSERT INTO `sys_user_authority` VALUES (1334,3,315,1);
INSERT INTO `sys_user_authority` VALUES (1335,3,314,1);
INSERT INTO `sys_user_authority` VALUES (1338,3,313,1);
INSERT INTO `sys_user_authority` VALUES (1339,3,232,1);
INSERT INTO `sys_user_authority` VALUES (1340,3,233,1);
INSERT INTO `sys_user_authority` VALUES (1341,3,234,1);
INSERT INTO `sys_user_authority` VALUES (1342,3,235,1);
INSERT INTO `sys_user_authority` VALUES (1343,3,236,1);
INSERT INTO `sys_user_authority` VALUES (1344,3,237,1);
INSERT INTO `sys_user_authority` VALUES (1345,3,238,1);
INSERT INTO `sys_user_authority` VALUES (1346,3,239,1);
INSERT INTO `sys_user_authority` VALUES (1347,3,431,1);
INSERT INTO `sys_user_authority` VALUES (1348,3,242,1);
INSERT INTO `sys_user_authority` VALUES (1349,3,241,1);
INSERT INTO `sys_user_authority` VALUES (1350,3,240,1);
INSERT INTO `sys_user_authority` VALUES (1363,3,301,1);
INSERT INTO `sys_user_authority` VALUES (1365,3,302,1);
INSERT INTO `sys_user_authority` VALUES (1366,3,245,1);
INSERT INTO `sys_user_authority` VALUES (1367,3,244,1);
INSERT INTO `sys_user_authority` VALUES (1368,3,243,1);
INSERT INTO `sys_user_authority` VALUES (1372,3,267,1);
INSERT INTO `sys_user_authority` VALUES (1374,3,277,1);
INSERT INTO `sys_user_authority` VALUES (1375,3,282,1);
INSERT INTO `sys_user_authority` VALUES (1377,3,247,1);
INSERT INTO `sys_user_authority` VALUES (1378,3,246,1);
INSERT INTO `sys_user_authority` VALUES (1379,3,296,1);
INSERT INTO `sys_user_authority` VALUES (1380,3,295,1);
INSERT INTO `sys_user_authority` VALUES (1384,3,250,1);
INSERT INTO `sys_user_authority` VALUES (1385,3,249,1);
INSERT INTO `sys_user_authority` VALUES (1386,3,248,1);
INSERT INTO `sys_user_authority` VALUES (1390,3,251,1);
INSERT INTO `sys_user_authority` VALUES (1391,3,252,1);
INSERT INTO `sys_user_authority` VALUES (1392,3,254,1);
INSERT INTO `sys_user_authority` VALUES (1393,3,255,1);
INSERT INTO `sys_user_authority` VALUES (1396,3,319,1);
INSERT INTO `sys_user_authority` VALUES (1397,3,318,1);
INSERT INTO `sys_user_authority` VALUES (1398,3,317,1);
INSERT INTO `sys_user_authority` VALUES (1402,3,366,1);
INSERT INTO `sys_user_authority` VALUES (1403,3,372,1);
INSERT INTO `sys_user_authority` VALUES (1404,3,374,1);
INSERT INTO `sys_user_authority` VALUES (1405,3,378,1);
INSERT INTO `sys_user_authority` VALUES (1406,3,379,1);
INSERT INTO `sys_user_authority` VALUES (1411,3,347,1);
INSERT INTO `sys_user_authority` VALUES (1413,3,349,1);
INSERT INTO `sys_user_authority` VALUES (1414,3,350,1);
INSERT INTO `sys_user_authority` VALUES (1415,3,353,1);
INSERT INTO `sys_user_authority` VALUES (1416,3,216,1);
INSERT INTO `sys_user_authority` VALUES (1417,3,215,1);
INSERT INTO `sys_user_authority` VALUES (1418,3,213,1);
INSERT INTO `sys_user_authority` VALUES (1419,3,212,1);
INSERT INTO `sys_user_authority` VALUES (1420,3,214,1);
INSERT INTO `sys_user_authority` VALUES (1421,3,411,1);
INSERT INTO `sys_user_authority` VALUES (1422,3,419,1);
INSERT INTO `sys_user_authority` VALUES (1423,3,369,1);
INSERT INTO `sys_user_authority` VALUES (1424,3,368,1);
INSERT INTO `sys_user_authority` VALUES (1425,3,367,1);
INSERT INTO `sys_user_authority` VALUES (1426,3,371,1);
INSERT INTO `sys_user_authority` VALUES (1427,3,370,1);
INSERT INTO `sys_user_authority` VALUES (1430,4,400,1);
INSERT INTO `sys_user_authority` VALUES (1433,4,403,1);
INSERT INTO `sys_user_authority` VALUES (1436,4,389,1);
INSERT INTO `sys_user_authority` VALUES (1437,4,390,1);
INSERT INTO `sys_user_authority` VALUES (1439,4,397,1);
INSERT INTO `sys_user_authority` VALUES (1440,4,425,1);
INSERT INTO `sys_user_authority` VALUES (1441,4,416,1);
INSERT INTO `sys_user_authority` VALUES (1443,4,414,1);
INSERT INTO `sys_user_authority` VALUES (1446,4,408,1);
INSERT INTO `sys_user_authority` VALUES (1448,4,406,1);
INSERT INTO `sys_user_authority` VALUES (1451,4,149,0);
INSERT INTO `sys_user_authority` VALUES (1452,4,269,1);
INSERT INTO `sys_user_authority` VALUES (1453,4,270,1);
INSERT INTO `sys_user_authority` VALUES (1454,4,271,1);
INSERT INTO `sys_user_authority` VALUES (1455,4,272,1);
INSERT INTO `sys_user_authority` VALUES (1456,4,273,1);
INSERT INTO `sys_user_authority` VALUES (1457,4,274,1);
INSERT INTO `sys_user_authority` VALUES (1459,4,321,1);
INSERT INTO `sys_user_authority` VALUES (1460,4,322,1);
INSERT INTO `sys_user_authority` VALUES (1461,4,323,1);
INSERT INTO `sys_user_authority` VALUES (1462,4,375,0);
INSERT INTO `sys_user_authority` VALUES (1463,4,377,1);
INSERT INTO `sys_user_authority` VALUES (1464,4,382,1);
INSERT INTO `sys_user_authority` VALUES (1465,4,383,1);
INSERT INTO `sys_user_authority` VALUES (1466,4,384,1);
INSERT INTO `sys_user_authority` VALUES (1467,4,385,1);
INSERT INTO `sys_user_authority` VALUES (1468,4,386,1);
INSERT INTO `sys_user_authority` VALUES (1469,4,409,1);
INSERT INTO `sys_user_authority` VALUES (1470,4,410,1);
INSERT INTO `sys_user_authority` VALUES (1471,4,155,1);
INSERT INTO `sys_user_authority` VALUES (1474,1,449,1);
INSERT INTO `sys_user_authority` VALUES (1476,1,451,1);
INSERT INTO `sys_user_authority` VALUES (1477,1,452,1);
INSERT INTO `sys_user_authority` VALUES (1478,1,453,1);
INSERT INTO `sys_user_authority` VALUES (1479,1,454,1);
INSERT INTO `sys_user_authority` VALUES (1480,1,455,1);
INSERT INTO `sys_user_authority` VALUES (1481,1,456,1);
INSERT INTO `sys_user_authority` VALUES (1484,1,459,1);
INSERT INTO `sys_user_authority` VALUES (1485,1,467,1);
INSERT INTO `sys_user_authority` VALUES (1486,1,466,1);
INSERT INTO `sys_user_authority` VALUES (1487,1,465,1);
INSERT INTO `sys_user_authority` VALUES (1488,1,464,1);
INSERT INTO `sys_user_authority` VALUES (1489,1,463,1);
INSERT INTO `sys_user_authority` VALUES (1490,1,462,1);
INSERT INTO `sys_user_authority` VALUES (1491,1,461,1);
INSERT INTO `sys_user_authority` VALUES (1492,1,460,1);
INSERT INTO `sys_user_authority` VALUES (1493,2,467,1);
INSERT INTO `sys_user_authority` VALUES (1494,2,466,1);
INSERT INTO `sys_user_authority` VALUES (1495,2,465,1);
INSERT INTO `sys_user_authority` VALUES (1496,2,464,1);
INSERT INTO `sys_user_authority` VALUES (1497,2,463,1);
INSERT INTO `sys_user_authority` VALUES (1498,2,462,1);
INSERT INTO `sys_user_authority` VALUES (1499,2,461,1);
INSERT INTO `sys_user_authority` VALUES (1500,2,460,1);
INSERT INTO `sys_user_authority` VALUES (1501,2,459,1);
INSERT INTO `sys_user_authority` VALUES (1502,3,459,0);
INSERT INTO `sys_user_authority` VALUES (1503,3,460,0);
INSERT INTO `sys_user_authority` VALUES (1504,3,461,0);
INSERT INTO `sys_user_authority` VALUES (1505,3,462,0);
INSERT INTO `sys_user_authority` VALUES (1506,3,463,0);
INSERT INTO `sys_user_authority` VALUES (1507,3,464,0);
INSERT INTO `sys_user_authority` VALUES (1508,3,465,0);
INSERT INTO `sys_user_authority` VALUES (1509,3,466,0);
INSERT INTO `sys_user_authority` VALUES (1510,3,467,0);
INSERT INTO `sys_user_authority` VALUES (1511,1,470,1);
INSERT INTO `sys_user_authority` VALUES (1512,1,469,1);
INSERT INTO `sys_user_authority` VALUES (1513,1,468,1);
INSERT INTO `sys_user_authority` VALUES (1514,1,471,1);
INSERT INTO `sys_user_authority` VALUES (1515,2,449,1);
INSERT INTO `sys_user_authority` VALUES (1516,1,472,1);
INSERT INTO `sys_user_authority` VALUES (1517,2,472,1);
INSERT INTO `sys_user_authority` VALUES (1518,1,473,1);
INSERT INTO `sys_user_authority` VALUES (1519,1,474,1);
INSERT INTO `sys_user_authority` VALUES (1520,1,475,1);
INSERT INTO `sys_user_authority` VALUES (1521,1,476,1);
INSERT INTO `sys_user_authority` VALUES (1522,1,477,1);
INSERT INTO `sys_user_authority` VALUES (1523,1,478,1);
INSERT INTO `sys_user_authority` VALUES (1524,3,473,1);
INSERT INTO `sys_user_authority` VALUES (1525,1,482,1);
INSERT INTO `sys_user_authority` VALUES (1526,1,481,1);
INSERT INTO `sys_user_authority` VALUES (1527,1,480,1);
INSERT INTO `sys_user_authority` VALUES (1528,1,479,1);
INSERT INTO `sys_user_authority` VALUES (1529,2,482,1);
INSERT INTO `sys_user_authority` VALUES (1530,2,480,1);
INSERT INTO `sys_user_authority` VALUES (1531,2,479,1);
INSERT INTO `sys_user_authority` VALUES (1532,2,481,1);
INSERT INTO `sys_user_authority` VALUES (1533,3,479,1);
INSERT INTO `sys_user_authority` VALUES (1534,3,480,1);
INSERT INTO `sys_user_authority` VALUES (1535,3,481,1);
INSERT INTO `sys_user_authority` VALUES (1536,3,482,1);
INSERT INTO `sys_user_authority` VALUES (1537,4,479,1);
INSERT INTO `sys_user_authority` VALUES (1538,4,480,1);
INSERT INTO `sys_user_authority` VALUES (1539,4,481,1);
INSERT INTO `sys_user_authority` VALUES (1540,4,482,1);
INSERT INTO `sys_user_authority` VALUES (1541,4,89,1);
INSERT INTO `sys_user_authority` VALUES (1542,1,483,1);
INSERT INTO `sys_user_authority` VALUES (1543,1,484,1);
INSERT INTO `sys_user_authority` VALUES (1544,1,485,1);
INSERT INTO `sys_user_authority` VALUES (1545,1,486,1);
INSERT INTO `sys_user_authority` VALUES (1546,1,487,1);
INSERT INTO `sys_user_authority` VALUES (1547,1,488,1);
INSERT INTO `sys_user_authority` VALUES (1548,1,489,1);
INSERT INTO `sys_user_authority` VALUES (1549,1,490,1);
INSERT INTO `sys_user_authority` VALUES (1550,1,491,1);
INSERT INTO `sys_user_authority` VALUES (1551,1,492,1);
INSERT INTO `sys_user_authority` VALUES (1552,1,493,1);
INSERT INTO `sys_user_authority` VALUES (1553,1,494,1);
INSERT INTO `sys_user_authority` VALUES (1554,3,488,1);
INSERT INTO `sys_user_authority` VALUES (1555,3,489,1);
INSERT INTO `sys_user_authority` VALUES (1556,3,490,1);
INSERT INTO `sys_user_authority` VALUES (1557,3,491,1);
INSERT INTO `sys_user_authority` VALUES (1558,3,492,1);
INSERT INTO `sys_user_authority` VALUES (1559,3,483,1);
INSERT INTO `sys_user_authority` VALUES (1560,3,484,1);
INSERT INTO `sys_user_authority` VALUES (1561,3,487,1);
INSERT INTO `sys_user_authority` VALUES (1562,3,486,1);
INSERT INTO `sys_user_authority` VALUES (1563,2,486,1);
INSERT INTO `sys_user_authority` VALUES (1564,2,487,1);
INSERT INTO `sys_user_authority` VALUES (1565,3,435,1);
INSERT INTO `sys_user_authority` VALUES (1566,3,443,1);
INSERT INTO `sys_user_authority` VALUES (1567,3,444,1);
INSERT INTO `sys_user_authority` VALUES (1568,3,446,1);
INSERT INTO `sys_user_authority` VALUES (1569,1,500,1);
INSERT INTO `sys_user_authority` VALUES (1570,1,501,1);
INSERT INTO `sys_user_authority` VALUES (1571,3,494,1);
INSERT INTO `sys_user_authority` VALUES (1572,2,494,1);
INSERT INTO `sys_user_authority` VALUES (1573,1,499,1);
INSERT INTO `sys_user_authority` VALUES (1574,1,502,1);
INSERT INTO `sys_user_authority` VALUES (1575,1,503,1);
INSERT INTO `sys_user_authority` VALUES (1576,1,504,1);
/*!40000 ALTER TABLE `sys_user_authority` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_group`
--

DROP TABLE IF EXISTS `sys_user_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_user_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `group_name` varchar(100) DEFAULT '' COMMENT '组别名称',
  `enable` tinyint(1) DEFAULT '1' COMMENT '是否启用，1：true,0:false',
  `descr` varchar(300) DEFAULT '' COMMENT '描述',
  `firewall_user_role` int(11) NOT NULL DEFAULT '3',
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_name` (`group_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_group`
--

LOCK TABLES `sys_user_group` WRITE;
/*!40000 ALTER TABLE `sys_user_group` DISABLE KEYS */;
INSERT INTO `sys_user_group` VALUES (1,'超级管理员',1,'',0);
INSERT INTO `sys_user_group` VALUES (2,'系统管理员',1,'',1);
INSERT INTO `sys_user_group` VALUES (3,'安全管理员',1,'',2);
INSERT INTO `sys_user_group` VALUES (4,'安全审计员',1,'',3);
/*!40000 ALTER TABLE `sys_user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_menu`
--

DROP TABLE IF EXISTS `sys_user_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_user_menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(30) DEFAULT NULL COMMENT '菜单名',
  `parent_id` int(11) DEFAULT '0' COMMENT '父ID，为0是顶级菜单',
  `display_child` tinyint(1) DEFAULT '0',
  `url` varchar(300) DEFAULT '' COMMENT '访问地址',
  `sort` int(5) DEFAULT '1' COMMENT '排序',
  `descr` varchar(300) DEFAULT '' COMMENT '描述',
  `icon_class` char(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=505 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_menu`
--

LOCK TABLES `sys_user_menu` WRITE;
/*!40000 ALTER TABLE `sys_user_menu` DISABLE KEYS */;
INSERT INTO `sys_user_menu` VALUES (1,'开发人员使用',0,1,'开发人员使用',1,'','');
INSERT INTO `sys_user_menu` VALUES (2,'测试菜单(不开放)日志',0,1,'测试菜单(不开放)',0,'','test');
INSERT INTO `sys_user_menu` VALUES (3,'上传',0,0,'上传',0,'','');
INSERT INTO `sys_user_menu` VALUES (4,'个人设置',0,1,'个人设置',0,'','');
INSERT INTO `sys_user_menu` VALUES (5,'菜单权限管理',1,0,'sys-user-menu/index',1,'','');
INSERT INTO `sys_user_menu` VALUES (6,'查看',5,0,'sys-user-menu/view',1,'','');
INSERT INTO `sys_user_menu` VALUES (7,'获取单个权限信息',5,0,'sys-user-menu/one',1,'','');
INSERT INTO `sys_user_menu` VALUES (8,'添加',5,0,'sys-user-menu/create',1,'','');
INSERT INTO `sys_user_menu` VALUES (9,'更新',5,0,'sys-user-menu/update',1,'','');
INSERT INTO `sys_user_menu` VALUES (10,'删除',5,0,'sys-user-menu/delete',1,'','');
INSERT INTO `sys_user_menu` VALUES (11,'缓存管理',1,0,'cache/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (12,'清除缓存',11,0,'cache/clean-cache',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (13,'组/用户',1,0,'sys-user-group/index',1,'','');
INSERT INTO `sys_user_menu` VALUES (14,'查看',13,0,'sys-user-group/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (15,'添加',13,0,'sys-user-group/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (16,'更新',13,0,'sys-user-group/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (17,'删除',13,0,'sys-user-group/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (18,'权限查看',13,0,'sys-user-group/authority',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (19,'权限修改',13,0,'sys-user-group/authority-modify',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (20,'账号管理',89,0,'sys-user/index',3,'','');
INSERT INTO `sys_user_menu` VALUES (21,'查看',20,0,'sys-user/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (22,'添加',20,0,'sys-user/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (23,'更新',20,0,'sys-user/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (24,'删除',20,0,'sys-user/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (25,'管理日志',2,0,'log-admin/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (26,'查看',25,0,'log-admin/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (27,'系统日志',2,0,'log-sys/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (28,'查看',27,0,'log-sys/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (29,'上传文件',3,0,'upload/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (30,'编译器上传',3,0,'upload/ueditor-img',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (31,'修改资料',4,0,'sys-user-config/modify-info',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (32,'数据管理',0,1,'数据管理',0,'','');
INSERT INTO `sys_user_menu` VALUES (33,'数据库',32,0,'fetch-task/index',3,'','');
INSERT INTO `sys_user_menu` VALUES (34,'查看',33,0,'fetch-task/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (35,'添加',33,0,'fetch-task/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (36,'更新',33,0,'fetch-task/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (37,'删除',33,0,'fetch-task/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (38,'数据表',32,0,'fetch-task-item/index',2,'','');
INSERT INTO `sys_user_menu` VALUES (39,'查看',38,0,'fetch-task-item/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (40,'添加',38,0,'fetch-task-item/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (41,'更新',38,0,'fetch-task-item/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (42,'删除',38,0,'fetch-task-item/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (43,'数据管理模型',32,0,'fetch-auto-model/index',1,'','');
INSERT INTO `sys_user_menu` VALUES (44,'查看',43,0,'fetch-auto-model/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (45,'添加',43,0,'fetch-auto-model/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (46,'更新',43,0,'fetch-auto-model/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (47,'删除',43,0,'fetch-auto-model/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (48,'安装库',33,0,'fetch-task/install-base',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (49,'搜索',43,0,'fetch-auto-model/search-result',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (50,'配置表',33,0,'fetch-task/config-table',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (51,'网络配置',0,1,'网络配置',2,'','wlsz');
INSERT INTO `sys_user_menu` VALUES (52,'网口配置',51,0,'/Network/NetPort.htm5',1,'','');
INSERT INTO `sys_user_menu` VALUES (53,'端口镜像',51,0,'/Network/PortMirror.htm5',2,'','');
INSERT INTO `sys_user_menu` VALUES (54,'虚拟线',51,0,'/Network/VirtualLine.htm5',3,'','');
INSERT INTO `sys_user_menu` VALUES (55,'桥设备',51,0,'/Network/BridgeDevice.htm5',4,'','');
INSERT INTO `sys_user_menu` VALUES (56,'拨号设备',51,0,'/Network/DialDevice.htm5',7,'','');
INSERT INTO `sys_user_menu` VALUES (57,'端口聚合',51,0,'/Network/PortAggregation.htm5',8,'','');
INSERT INTO `sys_user_menu` VALUES (58,'VLAN设备',51,0,'/Network/VlanDevice.htm5',9,'','');
INSERT INTO `sys_user_menu` VALUES (59,'DHCP',51,0,'/Network/DHCP.htm5',10,'','');
INSERT INTO `sys_user_menu` VALUES (60,'DNS设置',51,0,'/Network/DnsSetting.htm5',11,'','');
INSERT INTO `sys_user_menu` VALUES (61,'IPV6隧道配置',51,0,'/Ipvtunnelset/Index.htm5',12,'','');
INSERT INTO `sys_user_menu` VALUES (62,'NAT64配置',51,0,'/Natsetting/Index.htm5',13,'','');
INSERT INTO `sys_user_menu` VALUES (63,'路由配置',0,1,'路由配置',3,'','lysz');
INSERT INTO `sys_user_menu` VALUES (64,'ECMP',63,0,'/Ecmp/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (65,'静态路由',63,0,'/Network/StaticRoute.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (66,'策略路由',63,0,'/Network/StrategyRoute.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (67,'ISP路由',63,0,'/Network/IspRoute.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (68,'动态路由',63,0,'/Network/DynamicRoute.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (69,'对象定义',0,1,'对象定义',4,'','dxdy');
INSERT INTO `sys_user_menu` VALUES (70,'IP/IP组',69,0,'/Objectdefine/addressManagement.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (71,'ISP地址',69,0,'/Objectdefine/IspAddress.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (72,'服务/组',69,0,'/Objectdefine/Service.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (73,'URL类型组',69,0,'/Objectdefine/UrlType.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (74,'文件类型组',69,0,'/Objectdefine/FileType.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (75,'时间计划',69,0,'/Objectdefine/TimePlan.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (76,'自定义IPS规则库',69,0,'/Objectdefine/IpsRuleLib.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (77,'WEB应用防护规则库',69,0,'/Objectdefine/SafeRuleLib.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (78,'防火墙',0,1,'防火墙',5,'','fhq');
INSERT INTO `sys_user_menu` VALUES (79,'安全策略',78,0,'/Searitystrate/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (80,'NAT',78,0,'/Nat/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (81,'连接数控制',78,0,'/Connectnum/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (82,'DOS/DDOS防护',78,0,'/Ddos/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (83,'会话管理',78,1,'会话管理',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (84,'会话控制',83,0,'/Fwsession/Control.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (85,'连接排行榜',83,0,'/Fwsession/Connetrank.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (86,'会话状态',83,0,'/Fwsession/Sessionstatus.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (87,'IP-MAC绑定配置',78,0,'/Ipmac/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (88,'联动',78,0,'/Linkage/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (89,'用户管理',0,1,'用户管理',6,'','yhgl');
INSERT INTO `sys_user_menu` VALUES (90,'组/用户',89,0,'/Users/GroupsUsers.htm5',1,'','');
INSERT INTO `sys_user_menu` VALUES (91,'用户认证',89,0,'/Users/UserAuthentication.htm5',2,'','');
INSERT INTO `sys_user_menu` VALUES (92,'安全防护',0,0,'安全防护',7,'','aqfh');
INSERT INTO `sys_user_menu` VALUES (93,'URL过滤',92,1,'URL过滤',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (94,'URL过滤策略',93,0,'/Urlfilter/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (95,'URL黑名单',93,0,'/Urlsecurity/Black.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (96,'URL白名单',93,0,'/Urlsecurity/White.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (97,'入侵防护',92,0,'/Ips/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (98,'web应用防护',92,0,'/Webapp/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (99,'病毒防护',92,1,'病毒防护',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (100,'基本配置',99,0,'/Maliciouscode/EvilProtectedSet.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (101,'防病毒策略设置',99,0,'/Maliciouscode/EvilIndex.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (102,'信息泄漏防护',92,1,'信息泄漏防护',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (103,'关键词过滤',102,0,'/Keywordfilter/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (104,'文件过滤',102,0,'/Filefilter/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (105,'虚拟专网',0,0,'虚拟专网',8,'','xnzw');
INSERT INTO `sys_user_menu` VALUES (106,'SSL VPN',105,1,'SSL VPN',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (107,'基本配置',106,0,'/Sslvpn/Setting.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (108,'服务管理',106,0,'/Bdsslvpn/Service.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (109,'用户配置',106,0,'/Bdsslvpn/User.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (110,'IPSEC VPN',105,1,'IPSEC VPN',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (111,'本地子网',110,0,'/Ipsec/Netindex.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (112,'网口配置',110,0,'/Ipsec/Netport.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (113,'分支对接',110,0,'/Ipsecbranch/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (114,'IPSEC监控管理',110,0,'/Ipsec/Monitor.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (115,'L2TP VPN',105,1,'L2TP VPN',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (116,'基本配置',115,0,'/Bdl2tpvpn/Setting.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (117,'监控管理',115,0,'/Bdl2tpvpn/Monitor.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (118,'服务管理',115,0,'/Bdl2tpvpn/Service.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (119,'用户配置',115,0,'/Bdl2tpvpn/User.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (120,'虚拟池IP',115,0,'/Ipsec/VirtualNet.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (121,'NAT 穿越',105,1,'NAT 穿越',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (122,'中心节点',121,0,'/Ntn/Center.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (123,'边缘节点',121,0,'/Ntn/Edge.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (124,'GRE隧道',105,0,'/Gre/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (125,'流量管理',0,0,'流量管理',9,'','llgl');
INSERT INTO `sys_user_menu` VALUES (126,'虚拟线路',125,0,'/Virtualline/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (127,'通道配置',125,0,'/Socketset/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (128,'智能防护',0,1,'智能防护',10,'','znfh');
INSERT INTO `sys_user_menu` VALUES (129,'策略自动演进',128,0,'/Autorqrule/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (130,'蜜罐',128,0,'/Honeypot/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (131,'反向拍照',128,0,'/Revcamera/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (132,'防扫描',128,0,'/Revscan/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (133,'日志管理',0,1,'报表日志',11,'','rzgl');
INSERT INTO `sys_user_menu` VALUES (145,'报表统计',211,0,'/Report/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (149,'日志任务',0,0,'/Exportlog/Index.htm5',12,'','rzrw');
INSERT INTO `sys_user_menu` VALUES (150,'系统',0,1,'系统',1,'','xt');
INSERT INTO `sys_user_menu` VALUES (151,'管理员帐号',150,0,'/Account/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (152,'系统配置',150,1,'/Systemsetting/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (153,'系统维护',150,1,'/Systemmaintenance/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (154,'高可用性',150,0,'/Ha/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (155,'检测登录状态',0,0,'site/check-login-timeout',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (156,'安全管理',0,1,'安全管理',13,'','aqgl');
INSERT INTO `sys_user_menu` VALUES (157,'配置管理',156,1,'配置管理',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (158,'基本参数设置',157,0,'base-config/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (160,'站点组管理',157,1,'web-site/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (161,'新增',160,0,'web-site/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (162,'更新',160,0,'web-site/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (163,'删除',160,0,'web-site/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (177,'HA端口及参数配置',152,0,'ha-setting/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (178,'更新',177,0,'ha-setting/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (181,'通知配置',152,1,'mail-set/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (187,'规则升级',153,0,'upgrade/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (188,'报警设置',152,1,'mail-alert/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (190,'ssh开关',153,0,'waf-ssh/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (192,'应急支持',153,0,'refresh-zip/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (196,'配置管理',153,1,'deal-config/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (198,'磁盘清理',153,1,'disk-clear/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (204,'登录配置',89,0,'sys-login-config/config',4,'','');
INSERT INTO `sys_user_menu` VALUES (205,'接入控制',89,0,'sys-join-up/index',5,'','');
INSERT INTO `sys_user_menu` VALUES (209,'系统升级',153,1,'sys-up/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (211,'报表管理',0,1,'报表管理报表管理',14,'','bbgl');
INSERT INTO `sys_user_menu` VALUES (212,'攻击报表',211,0,'report-attack/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (213,'访问流量报表',211,0,'report-visit-flow/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (214,'即时报表',211,0,'report-immediately/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (215,'定期报表',211,0,'report-timer/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (216,'报表管理',211,0,'report-manage/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (220,'规则配置',156,1,'规则配置',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (221,'高级设置',156,1,'高级设置',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (222,'自学习',156,1,'自学习',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (223,'动态建模',156,0,'动态建模',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (224,'非法外联',156,1,'非法外联',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (225,'DDOS防护',156,1,'DDOS防护',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (226,'安全管理',156,1,'安全管理',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (227,'网页防篡改',156,0,'网页防篡改',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (228,'内置规则',220,0,'rules/index',1,'','');
INSERT INTO `sys_user_menu` VALUES (229,'自定义规则',220,0,'rules-custom/index',2,'','');
INSERT INTO `sys_user_menu` VALUES (230,'自定义规则模板',220,0,'rules-set/index',4,'','');
INSERT INTO `sys_user_menu` VALUES (231,'访问控制',220,0,'base-visit/index',6,'','');
INSERT INTO `sys_user_menu` VALUES (232,'HTTP防溢出设置',221,0,'overflow/config',1,'','');
INSERT INTO `sys_user_menu` VALUES (233,'HTTP请求动作过滤',221,0,'filter/config',2,'','');
INSERT INTO `sys_user_menu` VALUES (234,'HTTP请求内容过滤',221,0,'http-content-type/config',3,'','');
INSERT INTO `sys_user_menu` VALUES (235,'HTTP协议版本过滤',221,0,'protocol-version/config',4,'','');
INSERT INTO `sys_user_menu` VALUES (236,'HTTP头字段设置',221,0,'http-header/config',5,'','');
INSERT INTO `sys_user_menu` VALUES (237,'文件扩展名过滤',221,0,'file-extension/config',6,'','');
INSERT INTO `sys_user_menu` VALUES (238,'服务器信息隐藏',221,0,'server-header-hide/config',7,'','');
INSERT INTO `sys_user_menu` VALUES (239,'敏感词过滤设置',221,0,'sensitive-word/config',8,'','');
INSERT INTO `sys_user_menu` VALUES (240,'防盗链设置',221,0,'host-link-protection/config',9,'','');
INSERT INTO `sys_user_menu` VALUES (241,'爬虫防护设置',221,0,'spider-defend/config',10,'','');
INSERT INTO `sys_user_menu` VALUES (242,'防误报设置',221,0,'misdeclaration-defend/index',11,'','');
INSERT INTO `sys_user_menu` VALUES (243,'自学习设置',222,1,'self-study-set/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (244,'自学习访问白名单',222,1,'self-study-white-ip/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (245,'自学习结果',222,0,'self-study-result/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (246,'非法外联检测',224,1,'out-link/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (247,'非法外联设置',224,1,'out-link-set/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (248,'智能阻断设置',225,1,'smart-block/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (249,'DDOS防护设置',225,1,'d-dos-set/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (250,'CC防护设置',225,1,'cc-set/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (251,'可用性监测',226,1,'site-status/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (252,'开启云防护',226,0,'protect/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (254,'漏洞扫描',226,0,'vulnerability-scan/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (255,'返回页面设置',226,0,'error-list/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (267,'新增',244,0,'self-study-white-ip/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (268,'更新',228,0,'rules/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (269,'系统监控',0,1,'系统监控',NULL,'','xtjk');
INSERT INTO `sys_user_menu` VALUES (270,'信息概况',269,0,'sys-status-info/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (271,'网络流量监控',269,0,'sys-status-info/system-traffic',NULL,'sys-network-flow-monitoring/index','');
INSERT INTO `sys_user_menu` VALUES (272,'设备负载监控',269,0,'sys-status-info/system-use',NULL,'sys-load-monitoring/index','');
INSERT INTO `sys_user_menu` VALUES (273,'WEB应用监控',269,0,'sys-web-app-monitoring/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (274,'授权信息',269,0,'sys-authorization-info/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (277,'更新',244,0,'self-study-white-ip/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (282,'删除',244,0,'self-study-white-ip/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (287,'更新',229,0,'rules-custom/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (288,'删除',229,0,'rules-custom/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (289,'新增',229,0,'rules-custom/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (292,'删除',25,0,'log-admin/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (295,'更新',246,0,'out-link/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (296,'删除',246,0,'out-link/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (299,'删除',230,0,'rules-set/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (300,'新增',230,0,'rules-set/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (301,'更新',242,0,'misdeclaration-defend/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (302,'删除',242,0,'misdeclaration-defend/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (308,'更新',230,0,'rules-set/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (313,'删除',231,0,'base-visit/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (314,'新增',231,0,'base-visit/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (315,'更新',231,0,'base-visit/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (317,'新增',255,0,'error-list/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (318,'删除',255,0,'error-list/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (319,'编辑',255,0,'error-list/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (321,'WEB站点流量',273,0,'sys-web-app-monitoring/net-flow',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (322,'新建连接数 与 处理事务数',273,0,'sys-web-app-monitoring/connect',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (323,'并发连接数',273,0,'sys-web-app-monitoring/concurrency',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (325,'日志配置',133,1,'日志配置',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (326,'系统日志',133,0,'/Syslog/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (327,'入侵日志',133,0,'invade/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (328,'DDOS日志',133,0,'ddos/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (329,'CC日志',133,0,'cc-logs/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (330,'非法外联日志',133,0,'out-link-log/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (331,'智能阻断日志',133,0,'smart-block-log/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (332,'智能上传文件日志',133,0,'uploaded-file-log/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (333,'防火墙日志',133,0,'/Fwlog/IndexFw.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (334,'入侵防御日志',133,0,'/Fwlog/IndexIps.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (335,'web应用防护日志',133,0,'/Protectlog/IndexWeb.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (336,'病毒防护日志',133,0,'/Protectlog/IndexCode.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (337,'信息泄漏防护日志',133,0,'/Protectlog/IndexInfo.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (338,'DDOS防护日志',133,0,'/Ddoslog/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (339,'应用管控日志',133,0,'/Applylog/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (340,'url访问日志',133,0,'/Urllog/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (341,'日志库',133,0,'/Loglab/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (342,'用户认证日志',133,0,'/Userslog/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (343,'网中网检测日志',133,0,'/Sharelog/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (344,'IpsecVPN日志',133,0,'/Ipseclog/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (347,'新增',251,0,'site-status/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (349,'删除',251,0,'site-status/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (350,'查看',251,0,'site-status/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (353,'更新',251,0,'site-status/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (355,'更新2',177,0,'ha-setting/update-test',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (356,'删除',327,0,'invade/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (362,'查看',205,0,'sys-join-up/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (363,'添加',205,0,'sys-join-up/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (364,'更新',205,0,'sys-join-up/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (365,'删除',205,0,'sys-join-up/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (366,'新增',254,0,'vulnerability-scan/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (367,'添加',215,0,'report-timer/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (368,'更新',215,0,'report-timer/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (369,'删除',215,0,'report-timer/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (370,'删除',216,0,'report-manage/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (371,'下载',216,0,'report-manage/report-download',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (372,'删除',254,0,'vulnerability-scan/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (373,'更新',327,0,'invade/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (374,'查看',254,0,'vulnerability-scan/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (375,'首页定制保存',270,0,'sys-status-info/user-config-save',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (376,'导出',327,0,'invade/export-data',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (377,'网站访问分析(当月)',270,0,'sys-status-info/get-web-visit-info',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (378,'下载',254,0,'vulnerability-scan/download',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (379,'更新',254,0,'vulnerability-scan/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (382,'入侵数量统计(当月)',270,0,'sys-status-info/get-invade-info-count',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (383,'入侵类别统计(当月)',270,0,'sys-status-info/get-invade-info-sort',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (384,'产品信息',270,0,'sys-status-info/get-product-info',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (385,'综合分析(按天)',270,0,'sys-status-info/get-comprehensive-analysis-day',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (386,'综合分析(按月)',270,0,'sys-status-info/get-comprehensive-analysis-month',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (389,'删除',330,0,'out-link-log/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (390,'添加黑白名单',330,0,'out-link-log/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (393,'删除',328,0,'ddos/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (395,'导出',328,0,'ddos/export-data',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (397,'导出',330,0,'out-link-log/export-data',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (400,'删除',329,0,'cc-logs/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (403,'导出',329,0,'cc-logs/export-data',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (406,'删除',331,0,'smart-block-log/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (408,'导出',331,0,'smart-block-log/export-data',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (409,'帮助支持',0,0,'帮助支持',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (410,'应急支持',409,0,'helper/sos',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (411,'攻击报表预览',212,0,'report-attack/preview-create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (414,'删除',332,0,'uploaded-file-log/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (416,'导出',332,0,'uploaded-file-log/export-data',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (419,'访问流量报表预览',213,0,'report-visit-flow/preview-create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (425,'查看',332,0,'uploaded-file-log/view',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (429,'访问控制配置开关',205,0,'sys-join-up/change-mode',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (431,'OCR拦截',221,1,'ocr-set/config',12,'','');
INSERT INTO `sys_user_menu` VALUES (432,'透明代理',51,0,'t-proxy/index',5,'','');
INSERT INTO `sys_user_menu` VALUES (435,'反向代理',157,0,'proxy/index',6,'','');
INSERT INTO `sys_user_menu` VALUES (436,'新增',432,0,'t-proxy/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (437,'更新',432,0,'t-proxy/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (438,'删除',432,0,'t-proxy/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (443,'新增',435,0,'proxy/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (444,'删除',435,0,'proxy/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (446,'更新',435,0,'proxy/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (449,'Bypass设置',152,0,'by-pass/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (451,'多语言',1,1,'多语言',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (452,'语言检测',451,0,'language/language-check',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (453,'导出语言包',451,0,'language/lang-export',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (454,'导入语言包',451,0,'language/lang-import',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (455,'语言KEY',451,0,'language/lang-source-symbol',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (456,'检查翻译字符唯一',451,0,'language/lang-new-word-check',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (459,'系统工具',150,1,'/Systemsetting/Index.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (460,'系统配置',459,0,'/Systemsetting/TimeSet.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (461,'WEB控制配置',459,0,'/Systemsetting/WebSet.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (462,'SNMP',459,0,'/Systemsetting/SnmpSet.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (463,'网络测试',459,0,'/Systemsetting/WebTestSet.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (464,'系统时间',459,0,'/Systemsetting/TimeSets.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (465,'抓包工具',459,0,'/Systemsetting/PacketCapture.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (466,'组播路由转发',459,0,'/Systemsetting/RouterForward.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (467,'网中网检测',459,0,'/Systemsetting/NetInNet.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (468,'WAF规则翻译',1,1,'WAF规则翻译',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (469,'WAF规则翻译导出',468,0,'language/waf-rules-export',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (470,'WAF规则翻译导入',468,0,'language/waf-rules-import',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (471,'创建语言库文件',451,0,'language/create-language-base-file',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (472,'重启关机',153,0,'/Systemmaintenance/Reboot.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (473,'syslog服务器',325,0,'/Logconf/Syslog.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (474,'日志配置',325,0,'/Logconf/Indexconf.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (475,'邮件测试',325,0,'/Logconf/Mailtest.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (476,'日志入库归档',325,0,'/Logconf/LogtoDB.htm5',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (477,'初始化',1,1,'waf初始化',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (478,'waf账号同步',477,0,'index/sync-waf-and-firewall-user',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (479,'同级账号管理',89,0,'sys-user-for-role/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (480,'添加',479,0,'sys-user-for-role/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (481,'更新',479,0,'sys-user-for-role/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (482,'删除',479,0,'sys-user-for-role/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (483,'预设规则模板',220,0,'rules-default/index',3,'','');
INSERT INTO `sys_user_menu` VALUES (484,'更新',483,0,'rules-default/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (485,'新增',242,0,'misdeclaration-defend/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (486,'更新状态',229,0,'rules-custom/update-status',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (487,'规则复制',229,0,'rules-custom/copy-rules',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (488,'高级设置',220,0,'rule-custom-defend-policy/index',5,'','');
INSERT INTO `sys_user_menu` VALUES (489,'添加',488,0,'rule-custom-defend-policy/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (490,'更新',488,0,'rule-custom-defend-policy/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (491,'删除',488,0,'rule-custom-defend-policy/delete',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (492,'更新状态',488,0,'rule-custom-defend-policy/update-status',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (493,'智能木马检测',221,0,'intelligent-trojan-horse-set/config',14,'','');
INSERT INTO `sys_user_menu` VALUES (494,'IP过滤设置',221,0,'ip-filter-set/config',13,'','');
INSERT INTO `sys_user_menu` VALUES (495,'关键字告警',221,0,'key-word-alert/config',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (496,'更新状态',231,0,'base-visit/update-status',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (497,'测试',1,0,'测试',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (498,'测试',1,0,'测试',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (499,'系统配置列表',1,0,'config/index',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (500,'清空',329,0,'cc-logs/empty-data',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (501,'根据条件清空数据',329,0,'cc-logs/empty-data-for-condition',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (502,'添加',499,0,'config/create',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (503,'更新',499,0,'config/update',NULL,'','');
INSERT INTO `sys_user_menu` VALUES (504,'删除',499,0,'config/delete',NULL,'','');
/*!40000 ALTER TABLE `sys_user_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_menu_enable`
--

DROP TABLE IF EXISTS `sys_user_menu_enable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys_user_menu_enable` (
  `id` int(11) NOT NULL COMMENT '主键',
  `enable` tinyint(1) DEFAULT '1' COMMENT '是否启用，1：true,0:false',
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_id` FOREIGN KEY (`id`) REFERENCES `sys_user_menu` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_menu_enable`
--

LOCK TABLES `sys_user_menu_enable` WRITE;
/*!40000 ALTER TABLE `sys_user_menu_enable` DISABLE KEYS */;
INSERT INTO `sys_user_menu_enable` VALUES (1,1);
INSERT INTO `sys_user_menu_enable` VALUES (2,0);
INSERT INTO `sys_user_menu_enable` VALUES (3,0);
INSERT INTO `sys_user_menu_enable` VALUES (4,0);
INSERT INTO `sys_user_menu_enable` VALUES (5,1);
INSERT INTO `sys_user_menu_enable` VALUES (6,1);
INSERT INTO `sys_user_menu_enable` VALUES (7,1);
INSERT INTO `sys_user_menu_enable` VALUES (8,1);
INSERT INTO `sys_user_menu_enable` VALUES (9,1);
INSERT INTO `sys_user_menu_enable` VALUES (10,1);
INSERT INTO `sys_user_menu_enable` VALUES (11,1);
INSERT INTO `sys_user_menu_enable` VALUES (12,1);
INSERT INTO `sys_user_menu_enable` VALUES (13,1);
INSERT INTO `sys_user_menu_enable` VALUES (14,1);
INSERT INTO `sys_user_menu_enable` VALUES (15,1);
INSERT INTO `sys_user_menu_enable` VALUES (16,1);
INSERT INTO `sys_user_menu_enable` VALUES (17,1);
INSERT INTO `sys_user_menu_enable` VALUES (18,1);
INSERT INTO `sys_user_menu_enable` VALUES (19,1);
INSERT INTO `sys_user_menu_enable` VALUES (20,1);
INSERT INTO `sys_user_menu_enable` VALUES (21,0);
INSERT INTO `sys_user_menu_enable` VALUES (22,1);
INSERT INTO `sys_user_menu_enable` VALUES (23,1);
INSERT INTO `sys_user_menu_enable` VALUES (24,1);
INSERT INTO `sys_user_menu_enable` VALUES (25,1);
INSERT INTO `sys_user_menu_enable` VALUES (26,1);
INSERT INTO `sys_user_menu_enable` VALUES (27,1);
INSERT INTO `sys_user_menu_enable` VALUES (28,1);
INSERT INTO `sys_user_menu_enable` VALUES (29,1);
INSERT INTO `sys_user_menu_enable` VALUES (30,1);
INSERT INTO `sys_user_menu_enable` VALUES (31,1);
INSERT INTO `sys_user_menu_enable` VALUES (32,0);
INSERT INTO `sys_user_menu_enable` VALUES (33,1);
INSERT INTO `sys_user_menu_enable` VALUES (34,1);
INSERT INTO `sys_user_menu_enable` VALUES (35,1);
INSERT INTO `sys_user_menu_enable` VALUES (36,1);
INSERT INTO `sys_user_menu_enable` VALUES (37,1);
INSERT INTO `sys_user_menu_enable` VALUES (38,1);
INSERT INTO `sys_user_menu_enable` VALUES (39,1);
INSERT INTO `sys_user_menu_enable` VALUES (40,1);
INSERT INTO `sys_user_menu_enable` VALUES (41,1);
INSERT INTO `sys_user_menu_enable` VALUES (42,1);
INSERT INTO `sys_user_menu_enable` VALUES (43,2);
INSERT INTO `sys_user_menu_enable` VALUES (44,1);
INSERT INTO `sys_user_menu_enable` VALUES (45,1);
INSERT INTO `sys_user_menu_enable` VALUES (46,1);
INSERT INTO `sys_user_menu_enable` VALUES (47,1);
INSERT INTO `sys_user_menu_enable` VALUES (48,1);
INSERT INTO `sys_user_menu_enable` VALUES (49,1);
INSERT INTO `sys_user_menu_enable` VALUES (50,1);
INSERT INTO `sys_user_menu_enable` VALUES (51,1);
INSERT INTO `sys_user_menu_enable` VALUES (52,1);
INSERT INTO `sys_user_menu_enable` VALUES (53,1);
INSERT INTO `sys_user_menu_enable` VALUES (54,1);
INSERT INTO `sys_user_menu_enable` VALUES (55,1);
INSERT INTO `sys_user_menu_enable` VALUES (56,0);
INSERT INTO `sys_user_menu_enable` VALUES (57,1);
INSERT INTO `sys_user_menu_enable` VALUES (58,1);
INSERT INTO `sys_user_menu_enable` VALUES (59,0);
INSERT INTO `sys_user_menu_enable` VALUES (60,1);
INSERT INTO `sys_user_menu_enable` VALUES (61,0);
INSERT INTO `sys_user_menu_enable` VALUES (62,0);
INSERT INTO `sys_user_menu_enable` VALUES (63,1);
INSERT INTO `sys_user_menu_enable` VALUES (64,0);
INSERT INTO `sys_user_menu_enable` VALUES (65,1);
INSERT INTO `sys_user_menu_enable` VALUES (66,1);
INSERT INTO `sys_user_menu_enable` VALUES (67,0);
INSERT INTO `sys_user_menu_enable` VALUES (68,1);
INSERT INTO `sys_user_menu_enable` VALUES (69,1);
INSERT INTO `sys_user_menu_enable` VALUES (70,1);
INSERT INTO `sys_user_menu_enable` VALUES (71,0);
INSERT INTO `sys_user_menu_enable` VALUES (72,1);
INSERT INTO `sys_user_menu_enable` VALUES (73,0);
INSERT INTO `sys_user_menu_enable` VALUES (74,0);
INSERT INTO `sys_user_menu_enable` VALUES (75,0);
INSERT INTO `sys_user_menu_enable` VALUES (76,0);
INSERT INTO `sys_user_menu_enable` VALUES (77,0);
INSERT INTO `sys_user_menu_enable` VALUES (78,1);
INSERT INTO `sys_user_menu_enable` VALUES (79,0);
INSERT INTO `sys_user_menu_enable` VALUES (80,1);
INSERT INTO `sys_user_menu_enable` VALUES (81,0);
INSERT INTO `sys_user_menu_enable` VALUES (82,0);
INSERT INTO `sys_user_menu_enable` VALUES (83,0);
INSERT INTO `sys_user_menu_enable` VALUES (84,1);
INSERT INTO `sys_user_menu_enable` VALUES (85,1);
INSERT INTO `sys_user_menu_enable` VALUES (86,1);
INSERT INTO `sys_user_menu_enable` VALUES (87,0);
INSERT INTO `sys_user_menu_enable` VALUES (88,0);
INSERT INTO `sys_user_menu_enable` VALUES (89,1);
INSERT INTO `sys_user_menu_enable` VALUES (90,0);
INSERT INTO `sys_user_menu_enable` VALUES (91,0);
INSERT INTO `sys_user_menu_enable` VALUES (92,0);
INSERT INTO `sys_user_menu_enable` VALUES (93,0);
INSERT INTO `sys_user_menu_enable` VALUES (94,1);
INSERT INTO `sys_user_menu_enable` VALUES (95,1);
INSERT INTO `sys_user_menu_enable` VALUES (96,1);
INSERT INTO `sys_user_menu_enable` VALUES (97,0);
INSERT INTO `sys_user_menu_enable` VALUES (98,0);
INSERT INTO `sys_user_menu_enable` VALUES (99,1);
INSERT INTO `sys_user_menu_enable` VALUES (100,1);
INSERT INTO `sys_user_menu_enable` VALUES (101,1);
INSERT INTO `sys_user_menu_enable` VALUES (102,1);
INSERT INTO `sys_user_menu_enable` VALUES (103,0);
INSERT INTO `sys_user_menu_enable` VALUES (104,1);
INSERT INTO `sys_user_menu_enable` VALUES (105,0);
INSERT INTO `sys_user_menu_enable` VALUES (106,1);
INSERT INTO `sys_user_menu_enable` VALUES (107,1);
INSERT INTO `sys_user_menu_enable` VALUES (108,1);
INSERT INTO `sys_user_menu_enable` VALUES (109,1);
INSERT INTO `sys_user_menu_enable` VALUES (110,1);
INSERT INTO `sys_user_menu_enable` VALUES (111,1);
INSERT INTO `sys_user_menu_enable` VALUES (112,1);
INSERT INTO `sys_user_menu_enable` VALUES (113,1);
INSERT INTO `sys_user_menu_enable` VALUES (114,1);
INSERT INTO `sys_user_menu_enable` VALUES (115,1);
INSERT INTO `sys_user_menu_enable` VALUES (116,1);
INSERT INTO `sys_user_menu_enable` VALUES (117,1);
INSERT INTO `sys_user_menu_enable` VALUES (118,1);
INSERT INTO `sys_user_menu_enable` VALUES (119,1);
INSERT INTO `sys_user_menu_enable` VALUES (120,1);
INSERT INTO `sys_user_menu_enable` VALUES (121,1);
INSERT INTO `sys_user_menu_enable` VALUES (122,1);
INSERT INTO `sys_user_menu_enable` VALUES (123,1);
INSERT INTO `sys_user_menu_enable` VALUES (124,1);
INSERT INTO `sys_user_menu_enable` VALUES (125,0);
INSERT INTO `sys_user_menu_enable` VALUES (126,1);
INSERT INTO `sys_user_menu_enable` VALUES (127,1);
INSERT INTO `sys_user_menu_enable` VALUES (128,0);
INSERT INTO `sys_user_menu_enable` VALUES (129,1);
INSERT INTO `sys_user_menu_enable` VALUES (130,1);
INSERT INTO `sys_user_menu_enable` VALUES (131,1);
INSERT INTO `sys_user_menu_enable` VALUES (132,1);
INSERT INTO `sys_user_menu_enable` VALUES (133,1);
INSERT INTO `sys_user_menu_enable` VALUES (145,0);
INSERT INTO `sys_user_menu_enable` VALUES (149,0);
INSERT INTO `sys_user_menu_enable` VALUES (150,1);
INSERT INTO `sys_user_menu_enable` VALUES (151,0);
INSERT INTO `sys_user_menu_enable` VALUES (152,1);
INSERT INTO `sys_user_menu_enable` VALUES (153,1);
INSERT INTO `sys_user_menu_enable` VALUES (154,1);
INSERT INTO `sys_user_menu_enable` VALUES (155,2);
INSERT INTO `sys_user_menu_enable` VALUES (156,1);
INSERT INTO `sys_user_menu_enable` VALUES (157,1);
INSERT INTO `sys_user_menu_enable` VALUES (158,1);
INSERT INTO `sys_user_menu_enable` VALUES (160,1);
INSERT INTO `sys_user_menu_enable` VALUES (161,1);
INSERT INTO `sys_user_menu_enable` VALUES (162,1);
INSERT INTO `sys_user_menu_enable` VALUES (163,1);
INSERT INTO `sys_user_menu_enable` VALUES (177,0);
INSERT INTO `sys_user_menu_enable` VALUES (178,0);
INSERT INTO `sys_user_menu_enable` VALUES (181,1);
INSERT INTO `sys_user_menu_enable` VALUES (187,1);
INSERT INTO `sys_user_menu_enable` VALUES (188,1);
INSERT INTO `sys_user_menu_enable` VALUES (190,0);
INSERT INTO `sys_user_menu_enable` VALUES (192,0);
INSERT INTO `sys_user_menu_enable` VALUES (196,1);
INSERT INTO `sys_user_menu_enable` VALUES (198,1);
INSERT INTO `sys_user_menu_enable` VALUES (204,1);
INSERT INTO `sys_user_menu_enable` VALUES (205,1);
INSERT INTO `sys_user_menu_enable` VALUES (209,1);
INSERT INTO `sys_user_menu_enable` VALUES (211,1);
INSERT INTO `sys_user_menu_enable` VALUES (212,1);
INSERT INTO `sys_user_menu_enable` VALUES (213,0);
INSERT INTO `sys_user_menu_enable` VALUES (214,0);
INSERT INTO `sys_user_menu_enable` VALUES (215,1);
INSERT INTO `sys_user_menu_enable` VALUES (216,1);
INSERT INTO `sys_user_menu_enable` VALUES (220,1);
INSERT INTO `sys_user_menu_enable` VALUES (221,1);
INSERT INTO `sys_user_menu_enable` VALUES (222,1);
INSERT INTO `sys_user_menu_enable` VALUES (223,0);
INSERT INTO `sys_user_menu_enable` VALUES (224,1);
INSERT INTO `sys_user_menu_enable` VALUES (225,1);
INSERT INTO `sys_user_menu_enable` VALUES (226,1);
INSERT INTO `sys_user_menu_enable` VALUES (227,2);
INSERT INTO `sys_user_menu_enable` VALUES (228,1);
INSERT INTO `sys_user_menu_enable` VALUES (229,1);
INSERT INTO `sys_user_menu_enable` VALUES (230,1);
INSERT INTO `sys_user_menu_enable` VALUES (231,1);
INSERT INTO `sys_user_menu_enable` VALUES (232,1);
INSERT INTO `sys_user_menu_enable` VALUES (233,1);
INSERT INTO `sys_user_menu_enable` VALUES (234,1);
INSERT INTO `sys_user_menu_enable` VALUES (235,1);
INSERT INTO `sys_user_menu_enable` VALUES (236,1);
INSERT INTO `sys_user_menu_enable` VALUES (237,1);
INSERT INTO `sys_user_menu_enable` VALUES (238,1);
INSERT INTO `sys_user_menu_enable` VALUES (239,1);
INSERT INTO `sys_user_menu_enable` VALUES (240,1);
INSERT INTO `sys_user_menu_enable` VALUES (241,1);
INSERT INTO `sys_user_menu_enable` VALUES (242,1);
INSERT INTO `sys_user_menu_enable` VALUES (243,1);
INSERT INTO `sys_user_menu_enable` VALUES (244,1);
INSERT INTO `sys_user_menu_enable` VALUES (245,1);
INSERT INTO `sys_user_menu_enable` VALUES (246,1);
INSERT INTO `sys_user_menu_enable` VALUES (247,1);
INSERT INTO `sys_user_menu_enable` VALUES (248,1);
INSERT INTO `sys_user_menu_enable` VALUES (249,1);
INSERT INTO `sys_user_menu_enable` VALUES (250,1);
INSERT INTO `sys_user_menu_enable` VALUES (251,1);
INSERT INTO `sys_user_menu_enable` VALUES (252,1);
INSERT INTO `sys_user_menu_enable` VALUES (254,1);
INSERT INTO `sys_user_menu_enable` VALUES (255,1);
INSERT INTO `sys_user_menu_enable` VALUES (267,1);
INSERT INTO `sys_user_menu_enable` VALUES (268,1);
INSERT INTO `sys_user_menu_enable` VALUES (269,1);
INSERT INTO `sys_user_menu_enable` VALUES (270,1);
INSERT INTO `sys_user_menu_enable` VALUES (271,1);
INSERT INTO `sys_user_menu_enable` VALUES (272,1);
INSERT INTO `sys_user_menu_enable` VALUES (273,0);
INSERT INTO `sys_user_menu_enable` VALUES (274,1);
INSERT INTO `sys_user_menu_enable` VALUES (277,1);
INSERT INTO `sys_user_menu_enable` VALUES (282,1);
INSERT INTO `sys_user_menu_enable` VALUES (287,1);
INSERT INTO `sys_user_menu_enable` VALUES (288,1);
INSERT INTO `sys_user_menu_enable` VALUES (289,1);
INSERT INTO `sys_user_menu_enable` VALUES (292,1);
INSERT INTO `sys_user_menu_enable` VALUES (295,1);
INSERT INTO `sys_user_menu_enable` VALUES (296,1);
INSERT INTO `sys_user_menu_enable` VALUES (299,1);
INSERT INTO `sys_user_menu_enable` VALUES (300,1);
INSERT INTO `sys_user_menu_enable` VALUES (301,1);
INSERT INTO `sys_user_menu_enable` VALUES (302,1);
INSERT INTO `sys_user_menu_enable` VALUES (308,1);
INSERT INTO `sys_user_menu_enable` VALUES (313,1);
INSERT INTO `sys_user_menu_enable` VALUES (314,1);
INSERT INTO `sys_user_menu_enable` VALUES (315,1);
INSERT INTO `sys_user_menu_enable` VALUES (317,1);
INSERT INTO `sys_user_menu_enable` VALUES (318,1);
INSERT INTO `sys_user_menu_enable` VALUES (319,1);
INSERT INTO `sys_user_menu_enable` VALUES (321,1);
INSERT INTO `sys_user_menu_enable` VALUES (322,1);
INSERT INTO `sys_user_menu_enable` VALUES (323,1);
INSERT INTO `sys_user_menu_enable` VALUES (325,1);
INSERT INTO `sys_user_menu_enable` VALUES (326,1);
INSERT INTO `sys_user_menu_enable` VALUES (327,1);
INSERT INTO `sys_user_menu_enable` VALUES (328,1);
INSERT INTO `sys_user_menu_enable` VALUES (329,1);
INSERT INTO `sys_user_menu_enable` VALUES (330,1);
INSERT INTO `sys_user_menu_enable` VALUES (331,1);
INSERT INTO `sys_user_menu_enable` VALUES (332,0);
INSERT INTO `sys_user_menu_enable` VALUES (333,0);
INSERT INTO `sys_user_menu_enable` VALUES (334,0);
INSERT INTO `sys_user_menu_enable` VALUES (335,0);
INSERT INTO `sys_user_menu_enable` VALUES (336,0);
INSERT INTO `sys_user_menu_enable` VALUES (337,0);
INSERT INTO `sys_user_menu_enable` VALUES (338,0);
INSERT INTO `sys_user_menu_enable` VALUES (339,0);
INSERT INTO `sys_user_menu_enable` VALUES (340,0);
INSERT INTO `sys_user_menu_enable` VALUES (341,0);
INSERT INTO `sys_user_menu_enable` VALUES (342,0);
INSERT INTO `sys_user_menu_enable` VALUES (343,0);
INSERT INTO `sys_user_menu_enable` VALUES (344,0);
INSERT INTO `sys_user_menu_enable` VALUES (347,1);
INSERT INTO `sys_user_menu_enable` VALUES (349,1);
INSERT INTO `sys_user_menu_enable` VALUES (350,1);
INSERT INTO `sys_user_menu_enable` VALUES (353,1);
INSERT INTO `sys_user_menu_enable` VALUES (355,0);
INSERT INTO `sys_user_menu_enable` VALUES (356,1);
INSERT INTO `sys_user_menu_enable` VALUES (362,0);
INSERT INTO `sys_user_menu_enable` VALUES (363,1);
INSERT INTO `sys_user_menu_enable` VALUES (364,1);
INSERT INTO `sys_user_menu_enable` VALUES (365,1);
INSERT INTO `sys_user_menu_enable` VALUES (366,1);
INSERT INTO `sys_user_menu_enable` VALUES (367,1);
INSERT INTO `sys_user_menu_enable` VALUES (368,1);
INSERT INTO `sys_user_menu_enable` VALUES (369,1);
INSERT INTO `sys_user_menu_enable` VALUES (370,1);
INSERT INTO `sys_user_menu_enable` VALUES (371,1);
INSERT INTO `sys_user_menu_enable` VALUES (372,1);
INSERT INTO `sys_user_menu_enable` VALUES (373,1);
INSERT INTO `sys_user_menu_enable` VALUES (374,1);
INSERT INTO `sys_user_menu_enable` VALUES (375,1);
INSERT INTO `sys_user_menu_enable` VALUES (376,1);
INSERT INTO `sys_user_menu_enable` VALUES (377,1);
INSERT INTO `sys_user_menu_enable` VALUES (378,1);
INSERT INTO `sys_user_menu_enable` VALUES (379,1);
INSERT INTO `sys_user_menu_enable` VALUES (382,1);
INSERT INTO `sys_user_menu_enable` VALUES (383,1);
INSERT INTO `sys_user_menu_enable` VALUES (384,1);
INSERT INTO `sys_user_menu_enable` VALUES (385,1);
INSERT INTO `sys_user_menu_enable` VALUES (386,1);
INSERT INTO `sys_user_menu_enable` VALUES (389,1);
INSERT INTO `sys_user_menu_enable` VALUES (390,1);
INSERT INTO `sys_user_menu_enable` VALUES (393,1);
INSERT INTO `sys_user_menu_enable` VALUES (395,1);
INSERT INTO `sys_user_menu_enable` VALUES (397,1);
INSERT INTO `sys_user_menu_enable` VALUES (400,1);
INSERT INTO `sys_user_menu_enable` VALUES (403,1);
INSERT INTO `sys_user_menu_enable` VALUES (406,1);
INSERT INTO `sys_user_menu_enable` VALUES (408,1);
INSERT INTO `sys_user_menu_enable` VALUES (409,2);
INSERT INTO `sys_user_menu_enable` VALUES (410,1);
INSERT INTO `sys_user_menu_enable` VALUES (411,2);
INSERT INTO `sys_user_menu_enable` VALUES (414,1);
INSERT INTO `sys_user_menu_enable` VALUES (416,1);
INSERT INTO `sys_user_menu_enable` VALUES (419,2);
INSERT INTO `sys_user_menu_enable` VALUES (425,1);
INSERT INTO `sys_user_menu_enable` VALUES (429,1);
INSERT INTO `sys_user_menu_enable` VALUES (431,1);
INSERT INTO `sys_user_menu_enable` VALUES (432,0);
INSERT INTO `sys_user_menu_enable` VALUES (435,1);
INSERT INTO `sys_user_menu_enable` VALUES (436,1);
INSERT INTO `sys_user_menu_enable` VALUES (437,1);
INSERT INTO `sys_user_menu_enable` VALUES (438,1);
INSERT INTO `sys_user_menu_enable` VALUES (443,1);
INSERT INTO `sys_user_menu_enable` VALUES (444,1);
INSERT INTO `sys_user_menu_enable` VALUES (446,1);
INSERT INTO `sys_user_menu_enable` VALUES (449,1);
INSERT INTO `sys_user_menu_enable` VALUES (451,1);
INSERT INTO `sys_user_menu_enable` VALUES (452,1);
INSERT INTO `sys_user_menu_enable` VALUES (453,1);
INSERT INTO `sys_user_menu_enable` VALUES (454,1);
INSERT INTO `sys_user_menu_enable` VALUES (455,1);
INSERT INTO `sys_user_menu_enable` VALUES (456,1);
INSERT INTO `sys_user_menu_enable` VALUES (459,1);
INSERT INTO `sys_user_menu_enable` VALUES (460,0);
INSERT INTO `sys_user_menu_enable` VALUES (461,0);
INSERT INTO `sys_user_menu_enable` VALUES (462,1);
INSERT INTO `sys_user_menu_enable` VALUES (463,1);
INSERT INTO `sys_user_menu_enable` VALUES (464,1);
INSERT INTO `sys_user_menu_enable` VALUES (465,1);
INSERT INTO `sys_user_menu_enable` VALUES (466,0);
INSERT INTO `sys_user_menu_enable` VALUES (467,0);
INSERT INTO `sys_user_menu_enable` VALUES (468,1);
INSERT INTO `sys_user_menu_enable` VALUES (469,1);
INSERT INTO `sys_user_menu_enable` VALUES (470,1);
INSERT INTO `sys_user_menu_enable` VALUES (471,1);
INSERT INTO `sys_user_menu_enable` VALUES (472,1);
INSERT INTO `sys_user_menu_enable` VALUES (473,1);
INSERT INTO `sys_user_menu_enable` VALUES (474,0);
INSERT INTO `sys_user_menu_enable` VALUES (475,0);
INSERT INTO `sys_user_menu_enable` VALUES (476,0);
INSERT INTO `sys_user_menu_enable` VALUES (477,1);
INSERT INTO `sys_user_menu_enable` VALUES (478,1);
INSERT INTO `sys_user_menu_enable` VALUES (479,1);
INSERT INTO `sys_user_menu_enable` VALUES (480,1);
INSERT INTO `sys_user_menu_enable` VALUES (481,1);
INSERT INTO `sys_user_menu_enable` VALUES (482,1);
INSERT INTO `sys_user_menu_enable` VALUES (483,1);
INSERT INTO `sys_user_menu_enable` VALUES (484,1);
INSERT INTO `sys_user_menu_enable` VALUES (485,1);
INSERT INTO `sys_user_menu_enable` VALUES (486,1);
INSERT INTO `sys_user_menu_enable` VALUES (487,1);
INSERT INTO `sys_user_menu_enable` VALUES (488,1);
INSERT INTO `sys_user_menu_enable` VALUES (489,1);
INSERT INTO `sys_user_menu_enable` VALUES (490,1);
INSERT INTO `sys_user_menu_enable` VALUES (491,1);
INSERT INTO `sys_user_menu_enable` VALUES (492,1);
INSERT INTO `sys_user_menu_enable` VALUES (493,0);
INSERT INTO `sys_user_menu_enable` VALUES (494,1);
INSERT INTO `sys_user_menu_enable` VALUES (495,0);
INSERT INTO `sys_user_menu_enable` VALUES (496,1);
INSERT INTO `sys_user_menu_enable` VALUES (499,1);
INSERT INTO `sys_user_menu_enable` VALUES (500,1);
INSERT INTO `sys_user_menu_enable` VALUES (501,0);
INSERT INTO `sys_user_menu_enable` VALUES (502,1);
INSERT INTO `sys_user_menu_enable` VALUES (503,1);
INSERT INTO `sys_user_menu_enable` VALUES (504,1);
/*!40000 ALTER TABLE `sys_user_menu_enable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_actioncat`
--

DROP TABLE IF EXISTS `t_actioncat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_actioncat` (
  `action_id` tinyint(4) NOT NULL,
  `name` varchar(45) NOT NULL,
  `desc` varchar(255) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Blocking action category';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_actioncat`
--

LOCK TABLES `t_actioncat` WRITE;
/*!40000 ALTER TABLE `t_actioncat` DISABLE KEYS */;
INSERT INTO `t_actioncat` VALUES (1,'allow','允许访问');
INSERT INTO `t_actioncat` VALUES (2,'block','默认动作');
INSERT INTO `t_actioncat` VALUES (3,'deny','拒绝访问');
INSERT INTO `t_actioncat` VALUES (4,'drop','关闭链接');
INSERT INTO `t_actioncat` VALUES (5,'pass','继续处理');
INSERT INTO `t_actioncat` VALUES (6,'warning','仅记录');
/*!40000 ALTER TABLE `t_actioncat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_advaccessctrl`
--

DROP TABLE IF EXISTS `t_advaccessctrl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_advaccessctrl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` tinyint(4) DEFAULT '1' COMMENT '0disabled 1enabled',
  `desc` varchar(255) DEFAULT NULL,
  `src_ips` varchar(100) DEFAULT NULL COMMENT 'ip or ips ,null mean no limit',
  `dest_ips` varchar(100) DEFAULT NULL COMMENT 'ip or ips, null mean no limit',
  `url` varchar(1024) DEFAULT NULL,
  `rule_id` int(11) DEFAULT NULL,
  `action` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_t_advaccessctrl_t_actioncat1_idx` (`action`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='advance access control set';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_advaccessctrl`
--

LOCK TABLES `t_advaccessctrl` WRITE;
/*!40000 ALTER TABLE `t_advaccessctrl` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_advaccessctrl` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_advance`
--

DROP TABLE IF EXISTS `t_advance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_advance` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `packet` int(10) DEFAULT '10000',
  `length` int(10) DEFAULT '1460',
  `enable` int(10) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='fragment set';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_advance`
--

LOCK TABLES `t_advance` WRITE;
/*!40000 ALTER TABLE `t_advance` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_advance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_areas`
--

DROP TABLE IF EXISTS `t_areas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_areas` (
  `Code` varchar(2) COLLATE utf8_unicode_ci NOT NULL,
  `Province` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  `Area` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `Desc` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`Code`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_areas`
--

LOCK TABLES `t_areas` WRITE;
/*!40000 ALTER TABLE `t_areas` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_areas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_auditlog`
--

DROP TABLE IF EXISTS `t_auditlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_auditlog` (
  `time` int(11) NOT NULL,
  `username` varchar(16) DEFAULT NULL,
  `level1` varchar(10) DEFAULT NULL,
  `level2` varchar(10) DEFAULT NULL,
  `level3` varchar(10) DEFAULT NULL,
  `desc` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_auditlog`
--

LOCK TABLES `t_auditlog` WRITE;
/*!40000 ALTER TABLE `t_auditlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_auditlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_baseaccessctrl`
--

DROP TABLE IF EXISTS `t_baseaccessctrl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_baseaccessctrl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` tinyint(3) DEFAULT '1' COMMENT '是否启用0disable 1enable',
  `desc` varchar(255) DEFAULT NULL COMMENT '说明description',
  `src_ips` varchar(100) DEFAULT NULL COMMENT '来源ip or ips ,null mean no limits',
  `dest_ips` varchar(100) DEFAULT NULL COMMENT '目的ip or ips, null mean no limits',
  `url` varchar(1024) DEFAULT NULL COMMENT 'URL the website url',
  `action` varchar(45) NOT NULL DEFAULT '' COMMENT '拦截方式',
  `realid` int(11) NOT NULL DEFAULT '0' COMMENT '规则ID',
  `type` varchar(100) NOT NULL DEFAULT '' COMMENT '攻击类型',
  PRIMARY KEY (`id`),
  UNIQUE KEY `realid` (`realid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='访问控制';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_baseaccessctrl`
--

LOCK TABLES `t_baseaccessctrl` WRITE;
/*!40000 ALTER TABLE `t_baseaccessctrl` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_baseaccessctrl` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_baseconfig`
--

DROP TABLE IF EXISTS `t_baseconfig`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_baseconfig` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `wafengine` varchar(20) NOT NULL COMMENT 'On|Off|DetectionOnly',
  `defaultaction` varchar(10) NOT NULL DEFAULT '' COMMENT '拦截方式"allow", "deny", "drop", "pass"',
  `ports` varchar(100) NOT NULL COMMENT '80|8080',
  `deploy` varchar(20) NOT NULL COMMENT 'bridge、reverse proxy',
  `b&w` varchar(8) DEFAULT 'off' COMMENT '任意访问URL ：off为关闭功能，white为白名单模式，black为黑名单模式',
  PRIMARY KEY (`id`),
  UNIQUE KEY `wafengine` (`wafengine`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='基本参数设置';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_baseconfig`
--

LOCK TABLES `t_baseconfig` WRITE;
/*!40000 ALTER TABLE `t_baseconfig` DISABLE KEYS */;
INSERT INTO `t_baseconfig` VALUES (1,'DetectionOnly','deny','80|8080|443|8088','bridge','white');
/*!40000 ALTER TABLE `t_baseconfig` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_blackandwhite`
--

DROP TABLE IF EXISTS `t_blackandwhite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_blackandwhite` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ips` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '来源ip',
  `type` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'black为黑名单ip,white为白名单ip',
  `status` tinyint(1) unsigned DEFAULT '1' COMMENT '数据状态1:正常0待删除，页面不显示',
  `iptype` tinyint(1) unsigned DEFAULT '1' COMMENT 'ip类型:1-单个ip，2-ip段，3-ip段+子网掩码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_blackandwhite`
--

LOCK TABLES `t_blackandwhite` WRITE;
/*!40000 ALTER TABLE `t_blackandwhite` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_blackandwhite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_bridge`
--

DROP TABLE IF EXISTS `t_bridge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_bridge` (
  `name` varchar(45) NOT NULL COMMENT 'virtual bridge''s name',
  `nics` varchar(256) DEFAULT NULL COMMENT 'NIC name',
  `ageingtime` int(11) DEFAULT NULL,
  `stp` tinyint(4) DEFAULT NULL COMMENT '0disable 1enable',
  `forwarddelay` int(11) DEFAULT NULL,
  `maxage` int(11) DEFAULT NULL,
  `hellotime` int(11) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='the virtual net bridge set';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_bridge`
--

LOCK TABLES `t_bridge` WRITE;
/*!40000 ALTER TABLE `t_bridge` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_bridge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_bridge_mulip`
--

DROP TABLE IF EXISTS `t_bridge_mulip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_bridge_mulip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nic` varchar(256) DEFAULT NULL,
  `ip` varchar(256) DEFAULT NULL,
  `mask` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_bridge_mulip`
--

LOCK TABLES `t_bridge_mulip` WRITE;
/*!40000 ALTER TABLE `t_bridge_mulip` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_bridge_mulip` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_ccset`
--

DROP TABLE IF EXISTS `t_ccset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ccset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ccswitch` tinyint(3) DEFAULT '0' COMMENT '来源IP地址访问速率限制 0:unset 1:set',
  `ccperiod` int(11) DEFAULT NULL COMMENT '统计周期',
  `cctimes` int(11) DEFAULT NULL COMMENT '请求次数上限',
  `ccblocktime` int(11) DEFAULT NULL COMMENT '阻止访问时间',
  `brouteswitch` tinyint(3) DEFAULT '0' COMMENT '目的URI访问速率限制0:unset 1:set',
  `brouteperiod` int(11) DEFAULT NULL COMMENT '统计周期',
  `broutetimes` int(11) DEFAULT NULL COMMENT '请求次数上限',
  `brouteurls` varchar(2048) DEFAULT '' COMMENT '目的URI列表split by ;',
  `brouteblocktime` int(11) DEFAULT NULL COMMENT '阻止访问时间',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_ccset`
--

LOCK TABLES `t_ccset` WRITE;
/*!40000 ALTER TABLE `t_ccset` DISABLE KEYS */;
INSERT INTO `t_ccset` VALUES (1,0,15,50,20,0,15,50,'/test/',20);
/*!40000 ALTER TABLE `t_ccset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_cloudfence_linkage`
--

DROP TABLE IF EXISTS `t_cloudfence_linkage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_cloudfence_linkage` (
  `CloudfenceHost` varchar(32) DEFAULT NULL COMMENT '云防线ip地址',
  `CloudfencePort` varchar(8) DEFAULT NULL COMMENT '云防线端口',
  `usename` varchar(255) DEFAULT NULL COMMENT '云防线注册用户名',
  `is_use` tinyint(1) DEFAULT NULL COMMENT '是否开启云防线联动 1：开启 0：关闭',
  `status` tinyint(1) DEFAULT NULL COMMENT '云防线返回的结果; 0:成功  1:失败',
  `speed` float DEFAULT NULL COMMENT 'waf的宽带大小,单位m/s'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_cloudfence_linkage`
--

LOCK TABLES `t_cloudfence_linkage` WRITE;
/*!40000 ALTER TABLE `t_cloudfence_linkage` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_cloudfence_linkage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_countrycode`
--

DROP TABLE IF EXISTS `t_countrycode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_countrycode` (
  `CountryCode` varchar(3) COLLATE utf8_unicode_ci NOT NULL,
  `EnCountry` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `CnCountry` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `Continent` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`CountryCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_countrycode`
--

LOCK TABLES `t_countrycode` WRITE;
/*!40000 ALTER TABLE `t_countrycode` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_countrycode` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_customrules`
--

DROP TABLE IF EXISTS `t_customrules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_customrules` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `realid` int(11) NOT NULL DEFAULT '0' COMMENT '规则ID',
  `priority` int(11) NOT NULL DEFAULT '1' COMMENT '优先级',
  `name` varchar(140) NOT NULL DEFAULT '' COMMENT '名称',
  `desc` varchar(1024) NOT NULL DEFAULT '' COMMENT '说明',
  `severity` varchar(45) NOT NULL DEFAULT '' COMMENT '危害等级',
  `action` varchar(45) DEFAULT NULL COMMENT '拦截方式',
  `status` tinyint(3) DEFAULT NULL COMMENT '是否启用0:stop 1:start',
  `httpdata` tinyint(3) DEFAULT NULL COMMENT 'HTTP数据类型0:request 1:response',
  `httptype` varchar(45) DEFAULT NULL COMMENT 'HTTP请求类型GET POST',
  `matchdata` varchar(128) DEFAULT NULL COMMENT '匹配内容URL|COOKIE|POST',
  `matchalgorithm` tinyint(3) DEFAULT NULL COMMENT '匹配算法0:keyword 1:pcre',
  `keywords` varchar(1024) DEFAULT NULL COMMENT '特征关键字',
  `type` varchar(100) NOT NULL DEFAULT 'CUSTOM' COMMENT '攻击类型',
  PRIMARY KEY (`id`),
  UNIQUE KEY `realid` (`realid`)
) ENGINE=MyISAM AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_customrules`
--

LOCK TABLES `t_customrules` WRITE;
/*!40000 ALTER TABLE `t_customrules` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_customrules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_cyclereport`
--

DROP TABLE IF EXISTS `t_cyclereport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_cyclereport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `type` tinyint(4) DEFAULT NULL COMMENT '1IDS report, 2 flow report, 3 access report',
  `desc` varchar(255) DEFAULT NULL,
  `cycle` tinyint(4) DEFAULT NULL COMMENT '1year, 2month 3week 4day',
  `sendmail` tinyint(4) DEFAULT NULL COMMENT '0 no send mail, 1 send mail',
  `format` varchar(10) DEFAULT NULL COMMENT 'report output format :html、doc、pdf',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=21 DEFAULT CHARSET=utf8 COMMENT='the periodic report set';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_cyclereport`
--

LOCK TABLES `t_cyclereport` WRITE;
/*!40000 ALTER TABLE `t_cyclereport` DISABLE KEYS */;
INSERT INTO `t_cyclereport` VALUES (7,'每月攻击报表',1,'www',3,0,'html');
INSERT INTO `t_cyclereport` VALUES (9,'每天攻击报表',1,'',1,1,'pdf');
INSERT INTO `t_cyclereport` VALUES (18,'ggg',2,'rrr',2,0,'pdf');
INSERT INTO `t_cyclereport` VALUES (19,'sdsdd',1,'uuuu',2,0,'html');
INSERT INTO `t_cyclereport` VALUES (20,'wewee',2,'qwewee',1,0,'html');
/*!40000 ALTER TABLE `t_cyclereport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_ddosset`
--

DROP TABLE IF EXISTS `t_ddosset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ddosset` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `bankwidth` int(10) DEFAULT '0',
  `totalpacket` int(10) DEFAULT '0',
  `perpacket` int(10) DEFAULT '0',
  `tcppacket` int(10) DEFAULT '0',
  `pertcppacket` int(10) DEFAULT '0',
  `synpacket` int(10) DEFAULT '0',
  `persynpacket` int(10) DEFAULT '0',
  `ackpacket` int(10) DEFAULT '0',
  `perackpacket` int(10) DEFAULT '0',
  `othertcp` int(10) DEFAULT '0',
  `perothertcp` int(10) DEFAULT '0',
  `udppacket` int(10) DEFAULT '0',
  `perudppacket` int(10) DEFAULT '0',
  `icmppacket` int(10) DEFAULT '0',
  `pericmppacket` int(10) DEFAULT '0',
  `ddosenable` int(10) DEFAULT '0',
  `udpenable` int(10) DEFAULT '0',
  `icmpenable` int(10) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=456 DEFAULT CHARSET=utf8 COMMENT='ddos logs';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_ddosset`
--

LOCK TABLES `t_ddosset` WRITE;
/*!40000 ALTER TABLE `t_ddosset` DISABLE KEYS */;
INSERT INTO `t_ddosset` VALUES (1,1024,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,0,0,0);
/*!40000 ALTER TABLE `t_ddosset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_detection_types`
--

DROP TABLE IF EXISTS `t_detection_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_detection_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(32) NOT NULL,
  `severity` varchar(32) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_detection_types`
--

LOCK TABLES `t_detection_types` WRITE;
/*!40000 ALTER TABLE `t_detection_types` DISABLE KEYS */;
INSERT INTO `t_detection_types` VALUES (1,'vseDetectionTypeNone','low','pass');
INSERT INTO `t_detection_types` VALUES (2,'Virus','high','Malicious program capable of infecting other programs.');
INSERT INTO `t_detection_types` VALUES (3,'Adware','low','Application supported by adverts.');
INSERT INTO `t_detection_types` VALUES (4,'Application','low','Application that may be legitimate, but may also be unwanted.');
INSERT INTO `t_detection_types` VALUES (5,'Backdoor','high','A backdoor is a type of malware that allows an infected machine to be remotely');
INSERT INTO `t_detection_types` VALUES (6,'Bomb','medium','An archive that when scanned or extracted will exhaust the resources of the');
INSERT INTO `t_detection_types` VALUES (7,'BootVirus','medium','A boot sector virus is a virus that infects the master boot record of a storage device.');
INSERT INTO `t_detection_types` VALUES (8,'Denial','medium','Applications used for Denial of Service (DoS) attacks.');
INSERT INTO `t_detection_types` VALUES (9,'Dialer','medium','Dialers are trojan programs that attempt to dial out of a system using a modem.');
INSERT INTO `t_detection_types` VALUES (10,'Downloader','high','A downloader is a piece of malware that will download other malware.');
INSERT INTO `t_detection_types` VALUES (11,'Exploit','medium','An exploit for some operating system or common application was detected. The');
INSERT INTO `t_detection_types` VALUES (12,'Intended','low','Non-working or corrupt files, mistaken by some AV engines as potentially harmful');
INSERT INTO `t_detection_types` VALUES (13,'Joke','low','A benign application posing as malicious for comic effect.');
INSERT INTO `t_detection_types` VALUES (14,'Macro','medium','Malware using a macro language, e.g. in Office documents');
INSERT INTO `t_detection_types` VALUES (15,'MassMailer','medium','A worm that spreads using email as its primary distribution technique.');
INSERT INTO `t_detection_types` VALUES (16,'Mis-disinfection','low','A mis-disinfected virus is one that another AV engine tried to disinfect but could not');
INSERT INTO `t_detection_types` VALUES (17,'NetworkWorm','high','A worm that spreads using network vulnerabilities or poor network security as is');
INSERT INTO `t_detection_types` VALUES (18,'P2PWorm','high','A worm that spreads using peer to peer file sharing networks');
INSERT INTO `t_detection_types` VALUES (19,'Proxy','high','A backdoor Trojan that will allow unauthorized connections to be made through the');
INSERT INTO `t_detection_types` VALUES (20,'PasswordStealer','high','Malicious applications that will attempt to steal passwords. It will do it by stealing');
INSERT INTO `t_detection_types` VALUES (21,'Remote','medium','This is a document that contains a reference to an external template that can');
INSERT INTO `t_detection_types` VALUES (22,'Risk','high','Generic risk category, where an application could not be accurately categorized as a');
INSERT INTO `t_detection_types` VALUES (23,'Spyware','high','A type of Trojan that collects private information or monitors user behaviour');
INSERT INTO `t_detection_types` VALUES (24,'Tool','low','Applications used to generate viruses or exploits.');
INSERT INTO `t_detection_types` VALUES (25,'Trojan','high','This is an application that will pretend to have a useful purpose and then do damage');
INSERT INTO `t_detection_types` VALUES (26,'HiddenProcess','medium','This is a hidden process as a result of rootkit activity.');
INSERT INTO `t_detection_types` VALUES (27,'InjectedCode','high','This is (possibly) a legitimate process with malicious code injected in it.');
INSERT INTO `t_detection_types` VALUES (28,'Packer','medium','Packers/Obfuscators are tools that are used on an executable to make it smaller or');
INSERT INTO `t_detection_types` VALUES (29,'other','low','pass');
/*!40000 ALTER TABLE `t_detection_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_devinfo`
--

DROP TABLE IF EXISTS `t_devinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_devinfo` (
  `model` varchar(20) NOT NULL COMMENT 'product model',
  `sys_ver` varchar(20) NOT NULL COMMENT 'system version',
  `rule_ver` varchar(20) NOT NULL COMMENT 'rules version',
  `serial_num` varchar(30) NOT NULL COMMENT 'product serial number'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='产品信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_devinfo`
--

LOCK TABLES `t_devinfo` WRITE;
/*!40000 ALTER TABLE `t_devinfo` DISABLE KEYS */;
INSERT INTO `t_devinfo` VALUES ('BD-WAF','V2.7 PATCH1','1.0','031090161');
/*!40000 ALTER TABLE `t_devinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_dnat`
--

DROP TABLE IF EXISTS `t_dnat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_dnat` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `sourceAddress` varchar(255) DEFAULT NULL COMMENT '来源地址',
  `sourceNetmask` varchar(255) DEFAULT NULL COMMENT '来源掩码位数',
  `sourceAddresstype` varchar(255) DEFAULT NULL COMMENT '来源地址类型，1：单ip，2：ip段',
  `targetAddress` varchar(255) DEFAULT NULL COMMENT '目的地址',
  `targetNetmask` varchar(255) DEFAULT NULL COMMENT '目的掩码位数',
  `targetPort` varchar(255) DEFAULT NULL COMMENT '目的端口',
  `targetProtocol` varchar(255) NOT NULL DEFAULT '' COMMENT '目的协议',
  `targetAddresstype` varchar(255) DEFAULT NULL COMMENT '目的地址类型，1：单ip，2：ip段',
  `nicName` varchar(255) DEFAULT NULL COMMENT '网卡',
  `targetIpConverTo` varchar(255) DEFAULT NULL COMMENT '目的的地址转换为',
  `targetPortConverTo` varchar(255) DEFAULT NULL COMMENT '目的地址转换端口',
  `sort` int(11) NOT NULL COMMENT '排序',
  `isLog` tinyint(2) DEFAULT '1' COMMENT '是否记录日志，0否，1是',
  `status` tinyint(2) DEFAULT NULL COMMENT '状态：1：启用 0：不启用',
  `dnatName` varchar(128) DEFAULT NULL COMMENT '名称',
  PRIMARY KEY (`id`),
  UNIQUE KEY `sort` (`sort`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_dnat`
--

LOCK TABLES `t_dnat` WRITE;
/*!40000 ALTER TABLE `t_dnat` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_dnat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_dns`
--

DROP TABLE IF EXISTS `t_dns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_dns` (
  `first` varchar(45) NOT NULL,
  `second` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`first`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_dns`
--

LOCK TABLES `t_dns` WRITE;
/*!40000 ALTER TABLE `t_dns` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_dns` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_errorlist`
--

DROP TABLE IF EXISTS `t_errorlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_errorlist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status_code` varchar(20) NOT NULL DEFAULT '' COMMENT '错误页面类型HTTP',
  `prompt_type` tinyint(1) NOT NULL DEFAULT '0' COMMENT '提示类型：1为上传页面2为页面提示文字',
  `prompt_file` varchar(100) DEFAULT NULL COMMENT '自定义文件',
  `prompt_content` text COMMENT '页面提示文字',
  `desc` varchar(255) DEFAULT NULL COMMENT '备注',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '生效状态',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_errorlist`
--

LOCK TABLES `t_errorlist` WRITE;
/*!40000 ALTER TABLE `t_errorlist` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_errorlist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_ha_setting`
--

DROP TABLE IF EXISTS `t_ha_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ha_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_use` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  `interface` varchar(6) NOT NULL,
  `vhid` int(11) DEFAULT '10',
  `password` varchar(16) NOT NULL,
  `state` varchar(7) DEFAULT 'backup',
  `ip` varchar(16) DEFAULT '' COMMENT 'ip',
  `database_ip` varchar(16) DEFAULT NULL,
  `database_port` varchar(10) DEFAULT NULL,
  `is_setting` int(1) DEFAULT NULL,
  `server_id` int(1) DEFAULT NULL,
  `offset_id` int(1) DEFAULT NULL,
  `had_sync` int(11) DEFAULT '0',
  `priority` int(11) DEFAULT NULL,
  `bridge` varchar(45) DEFAULT NULL,
  `is_port_aggregation` tinyint(4) DEFAULT '0',
  `database_sync_status` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_ha_setting`
--

LOCK TABLES `t_ha_setting` WRITE;
/*!40000 ALTER TABLE `t_ha_setting` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_ha_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_httprequesttype`
--

DROP TABLE IF EXISTS `t_httprequesttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_httprequesttype` (
  `id` tinyint(4) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `status` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_httprequesttype`
--

LOCK TABLES `t_httprequesttype` WRITE;
/*!40000 ALTER TABLE `t_httprequesttype` DISABLE KEYS */;
INSERT INTO `t_httprequesttype` VALUES (1,'application/x-www-form-urlencoded',1);
INSERT INTO `t_httprequesttype` VALUES (2,'multipart/form-data',1);
INSERT INTO `t_httprequesttype` VALUES (3,'text/xml',1);
INSERT INTO `t_httprequesttype` VALUES (4,'application/xml',0);
INSERT INTO `t_httprequesttype` VALUES (5,'application/x-amf',0);
INSERT INTO `t_httprequesttype` VALUES (6,'application/json',0);
/*!40000 ALTER TABLE `t_httprequesttype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_httptypeset`
--

DROP TABLE IF EXISTS `t_httptypeset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_httptypeset` (
  `id` tinyint(4) NOT NULL,
  `name` varchar(45) NOT NULL,
  `desc` varchar(45) DEFAULT NULL,
  `selected` tinyint(4) NOT NULL DEFAULT '0' COMMENT '0:no selected 1:selected',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='http request type category';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_httptypeset`
--

LOCK TABLES `t_httptypeset` WRITE;
/*!40000 ALTER TABLE `t_httptypeset` DISABLE KEYS */;
INSERT INTO `t_httptypeset` VALUES (1,'GET',NULL,1);
INSERT INTO `t_httptypeset` VALUES (2,'POST',NULL,1);
INSERT INTO `t_httptypeset` VALUES (3,'HEAD',NULL,1);
INSERT INTO `t_httptypeset` VALUES (4,'OPTIONS',NULL,1);
INSERT INTO `t_httptypeset` VALUES (5,'DELETE',NULL,0);
INSERT INTO `t_httptypeset` VALUES (6,'PUT',NULL,0);
INSERT INTO `t_httptypeset` VALUES (7,'PROPFIND',NULL,0);
INSERT INTO `t_httptypeset` VALUES (8,'CHECKOUT',NULL,0);
INSERT INTO `t_httptypeset` VALUES (9,'CHECHIN',NULL,0);
INSERT INTO `t_httptypeset` VALUES (10,'MKCOL',NULL,0);
INSERT INTO `t_httptypeset` VALUES (11,'PROPPATCH',NULL,0);
INSERT INTO `t_httptypeset` VALUES (12,'SHOWMETHOD',NULL,0);
INSERT INTO `t_httptypeset` VALUES (13,'TEXTSEARCH',NULL,0);
INSERT INTO `t_httptypeset` VALUES (15,'COPY',NULL,0);
INSERT INTO `t_httptypeset` VALUES (16,'LOCK',NULL,0);
INSERT INTO `t_httptypeset` VALUES (17,'LINK',NULL,0);
INSERT INTO `t_httptypeset` VALUES (18,'SPACEJUMP',NULL,0);
INSERT INTO `t_httptypeset` VALUES (19,'SEARCH',NULL,0);
INSERT INTO `t_httptypeset` VALUES (20,'CONNECT',NULL,0);
INSERT INTO `t_httptypeset` VALUES (21,'MOVE',NULL,0);
INSERT INTO `t_httptypeset` VALUES (22,'UNLOCK',NULL,0);
INSERT INTO `t_httptypeset` VALUES (23,'UNLINK',NULL,0);
INSERT INTO `t_httptypeset` VALUES (24,'TRACK',NULL,0);
INSERT INTO `t_httptypeset` VALUES (25,'DEBUG',NULL,0);
INSERT INTO `t_httptypeset` VALUES (26,'UNKNOWN',NULL,0);
/*!40000 ALTER TABLE `t_httptypeset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_httpver`
--

DROP TABLE IF EXISTS `t_httpver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_httpver` (
  `id` tinyint(4) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `status` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_httpver`
--

LOCK TABLES `t_httpver` WRITE;
/*!40000 ALTER TABLE `t_httpver` DISABLE KEYS */;
INSERT INTO `t_httpver` VALUES (1,'HTTP/1.0',1);
INSERT INTO `t_httpver` VALUES (2,'HTTP/1.1',1);
/*!40000 ALTER TABLE `t_httpver` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_ip_filter_set`
--

DROP TABLE IF EXISTS `t_ip_filter_set`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ip_filter_set` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增加id',
  `ip_addr_start` varchar(200) NOT NULL DEFAULT '' COMMENT 'ip地址结束ip 例：192.168.1.0-192.168.1.254的最一个ip（192.168.1.0）',
  `ip_addr_end` varchar(200) NOT NULL DEFAULT '' COMMENT 'ip地址结束ip 例：192.168.1.0-192.168.1.254的后一个ip（192.168.1.254）',
  `status` tinyint(3) NOT NULL DEFAULT '1' COMMENT 'IP过滤设置是否开启 1开启 0不开启',
  `add_time` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '入库时间',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='IP过滤设置';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_ip_filter_set`
--

LOCK TABLES `t_ip_filter_set` WRITE;
/*!40000 ALTER TABLE `t_ip_filter_set` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_ip_filter_set` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_ipfragment`
--

DROP TABLE IF EXISTS `t_ipfragment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ipfragment` (
  `ischecked` tinyint(4) NOT NULL COMMENT '0:uncheck 1:checked',
  `packetsize` int(11) DEFAULT NULL,
  `maxlen` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_ipfragment`
--

LOCK TABLES `t_ipfragment` WRITE;
/*!40000 ALTER TABLE `t_ipfragment` DISABLE KEYS */;
INSERT INTO `t_ipfragment` VALUES (0,0,0);
/*!40000 ALTER TABLE `t_ipfragment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_keywordset`
--

DROP TABLE IF EXISTS `t_keywordset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_keywordset` (
  `ischecked` tinyint(4) NOT NULL DEFAULT '1' COMMENT '0disable, 1enable',
  `keywords` varchar(2048) DEFAULT NULL COMMENT 'keywords, Multiple keyword separated by  ''|'''
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='keywords filter set';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_keywordset`
--

LOCK TABLES `t_keywordset` WRITE;
/*!40000 ALTER TABLE `t_keywordset` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_keywordset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_license`
--

DROP TABLE IF EXISTS `t_license`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_license` (
  `sn` varchar(100) NOT NULL,
  `vertype` tinyint(4) DEFAULT NULL COMMENT '0test 1normal',
  `validate` int(11) DEFAULT NULL,
  `company` varchar(100) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `telephone` varchar(100) DEFAULT NULL,
  `licensefile` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`sn`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_license`
--

LOCK TABLES `t_license` WRITE;
/*!40000 ALTER TABLE `t_license` DISABLE KEYS */;
INSERT INTO `t_license` VALUES ('106c07ebbbb5655fe4a2ac6e4f53b69d',1,1893427200,'','','','',NULL);
/*!40000 ALTER TABLE `t_license` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_mailalert`
--

DROP TABLE IF EXISTS `t_mailalert`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_mailalert` (
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '邮件报警开启 1为开启',
  `now` tinyint(1) NOT NULL,
  `interval` tinyint(3) NOT NULL DEFAULT '0' COMMENT '发送间隔',
  `maxValue` mediumint(8) NOT NULL,
  `cycle` smallint(5) NOT NULL,
  `phone_status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '短信报警开启，1为开启',
  `phone_cycle` smallint(5) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_mailalert`
--

LOCK TABLES `t_mailalert` WRITE;
/*!40000 ALTER TABLE `t_mailalert` DISABLE KEYS */;
INSERT INTO `t_mailalert` VALUES (1,0,2,0,0,0,24,1);
/*!40000 ALTER TABLE `t_mailalert` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_mailset`
--

DROP TABLE IF EXISTS `t_mailset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_mailset` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `openMail` tinyint(3) NOT NULL DEFAULT '0' COMMENT '启用网关邮件功能: 0 off不启用； 1 on启用',
  `openPhone` tinyint(3) NOT NULL DEFAULT '0' COMMENT '启用手机报警开关: 0 off不启用； 1 on启用',
  `sender` varchar(45) DEFAULT NULL COMMENT '发件人邮箱',
  `username` varchar(45) DEFAULT NULL COMMENT '发件人名称--(废弃)',
  `password` varchar(45) DEFAULT NULL COMMENT '发件人密码',
  `smtpserver` varchar(45) DEFAULT NULL COMMENT 'SMTP服务器地址',
  `smtp_port` int(11) DEFAULT NULL COMMENT 'SMTP服务器端口',
  `receiver` varchar(45) DEFAULT NULL COMMENT '收件人邮箱',
  `receiver_phone` varchar(45) DEFAULT NULL COMMENT '收件人手机号码',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='the mail config';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_mailset`
--

LOCK TABLES `t_mailset` WRITE;
/*!40000 ALTER TABLE `t_mailset` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_mailset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_modeling`
--

DROP TABLE IF EXISTS `t_modeling`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_modeling` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) DEFAULT NULL COMMENT '域名',
  `path` varchar(255) DEFAULT NULL COMMENT '路径',
  `method` varchar(8) DEFAULT NULL COMMENT '访问方式',
  `websiteId` int(11) DEFAULT NULL COMMENT 't_website的外键id',
  `port` int(11) DEFAULT NULL COMMENT '访问的端口',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7501 DEFAULT CHARSET=utf8 COMMENT='动态建模结果';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_modeling`
--

LOCK TABLES `t_modeling` WRITE;
/*!40000 ALTER TABLE `t_modeling` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_modeling` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_modeling_detail`
--

DROP TABLE IF EXISTS `t_modeling_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_modeling_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `modelingId` int(11) DEFAULT NULL COMMENT 't_modeling的外键id',
  `type` varchar(8) DEFAULT NULL COMMENT '参数类型， number  或者 str',
  `minlength` int(11) DEFAULT NULL COMMENT '最小长度',
  `maxlength` int(11) DEFAULT NULL COMMENT '最大长度',
  `name` varchar(255) DEFAULT NULL COMMENT '参数名称',
  `is_use` tinyint(1) DEFAULT '1' COMMENT '0disable 1enable',
  PRIMARY KEY (`id`),
  KEY `modeling_id` (`modelingId`),
  CONSTRAINT `modeling_id` FOREIGN KEY (`modelingId`) REFERENCES `t_modeling` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=209 DEFAULT CHARSET=utf8 COMMENT='动态建模参数';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_modeling_detail`
--

LOCK TABLES `t_modeling_detail` WRITE;
/*!40000 ALTER TABLE `t_modeling_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_modeling_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_modeling_detail_rule`
--

DROP TABLE IF EXISTS `t_modeling_detail_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_modeling_detail_rule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `realRuleId` varchar(11) DEFAULT NULL COMMENT '真实规则id，需要跟modelingDetailId做UNIQUE约束，保证唯一性',
  `is_use` tinyint(1) DEFAULT NULL COMMENT '0disable 1enable',
  `hitCount` int(11) DEFAULT NULL COMMENT '匹配次数',
  `hitChance` tinyint(4) DEFAULT NULL COMMENT '匹配率',
  `modelingDetailId` int(11) DEFAULT NULL COMMENT 't_modeling_detail外键id',
  `modelingId` int(11) DEFAULT NULL COMMENT 't_modeling外键id',
  `websiteId` int(11) DEFAULT NULL COMMENT 't_website外键id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `rule_detail` (`realRuleId`,`modelingDetailId`)
) ENGINE=InnoDB AUTO_INCREMENT=5844 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_modeling_detail_rule`
--

LOCK TABLES `t_modeling_detail_rule` WRITE;
/*!40000 ALTER TABLE `t_modeling_detail_rule` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_modeling_detail_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_netflowhistory`
--

DROP TABLE IF EXISTS `t_netflowhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_netflowhistory` (
  `nic` varchar(20) NOT NULL,
  `time` int(11) NOT NULL,
  `flowin` bigint(20) DEFAULT NULL,
  `flowout` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`nic`,`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_netflowhistory`
--

LOCK TABLES `t_netflowhistory` WRITE;
/*!40000 ALTER TABLE `t_netflowhistory` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_netflowhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_nicset`
--

DROP TABLE IF EXISTS `t_nicset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_nicset` (
  `nic` varchar(45) NOT NULL COMMENT 'nic name',
  `ip` varchar(45) DEFAULT NULL,
  `mask` varchar(45) DEFAULT NULL,
  `gateway` varchar(45) DEFAULT NULL,
  `isstart` tinyint(4) DEFAULT NULL COMMENT '0disable 1enable',
  `islink` tinyint(4) DEFAULT NULL COMMENT '0unlink 1linked',
  `workmode` varchar(45) DEFAULT NULL,
  `desc` varchar(45) DEFAULT NULL,
  `brgname` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`nic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='the NIC set';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_nicset`
--

LOCK TABLES `t_nicset` WRITE;
/*!40000 ALTER TABLE `t_nicset` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_nicset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_nicsflow`
--

DROP TABLE IF EXISTS `t_nicsflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_nicsflow` (
  `nic` varchar(20) NOT NULL COMMENT 'NIC name',
  `mac` varchar(45) DEFAULT NULL COMMENT 'mac address',
  `mode` varchar(4) DEFAULT NULL COMMENT 'work mode',
  `status` tinyint(4) DEFAULT NULL COMMENT 'link status',
  `rcv_pks` bigint(20) DEFAULT NULL COMMENT 'received packets',
  `snd_pks` bigint(20) DEFAULT NULL COMMENT 'sended packets',
  `rcv_bytes` bigint(20) DEFAULT NULL COMMENT 'received bytes',
  `snd_bytes` bigint(20) DEFAULT NULL COMMENT 'sended bytes',
  `rcv_errs` int(11) DEFAULT NULL COMMENT 'received error packets',
  `snd_errs` int(11) DEFAULT NULL COMMENT 'sended error packets',
  `rcv_losts` int(11) DEFAULT NULL COMMENT 'lost packets when receive',
  `snd_losts` int(11) DEFAULT NULL COMMENT 'lost packets when sended',
  `rcv_ratio` int(11) DEFAULT NULL COMMENT 'receive rate',
  `snd_ratio` int(11) DEFAULT NULL COMMENT 'send rate',
  `time` varchar(10) NOT NULL,
  PRIMARY KEY (`nic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='NICS flow';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_nicsflow`
--

LOCK TABLES `t_nicsflow` WRITE;
/*!40000 ALTER TABLE `t_nicsflow` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_nicsflow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_ntp_setting`
--

DROP TABLE IF EXISTS `t_ntp_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ntp_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server` varchar(64) DEFAULT '' COMMENT 'ip',
  `type` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COMMENT='ntp client setting';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_ntp_setting`
--

LOCK TABLES `t_ntp_setting` WRITE;
/*!40000 ALTER TABLE `t_ntp_setting` DISABLE KEYS */;
INSERT INTO `t_ntp_setting` VALUES (1,'cn.pool.ntp.org',0);
INSERT INTO `t_ntp_setting` VALUES (2,'0.cn.pool.ntp.org',0);
INSERT INTO `t_ntp_setting` VALUES (3,'1.cn.pool.ntp.org',0);
INSERT INTO `t_ntp_setting` VALUES (4,'0.asia.pool.ntp.org',0);
INSERT INTO `t_ntp_setting` VALUES (5,'1.asia.pool.ntp.org',0);
INSERT INTO `t_ntp_setting` VALUES (6,'2.asia.pool.ntp.org',0);
/*!40000 ALTER TABLE `t_ntp_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_ocr_block`
--

DROP TABLE IF EXISTS `t_ocr_block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ocr_block` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1-on,0-off',
  `urls` varchar(2048) DEFAULT '' COMMENT 'split by | ',
  `exts` varchar(500) DEFAULT 'gif|jpg|png|bmp' COMMENT 'split by | , 扩展名',
  `words` longtext NOT NULL COMMENT 'split by |',
  `website_id` int(11) NOT NULL DEFAULT '0' COMMENT 'waf2.6.1 t_websit',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `website_id` (`website_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_ocr_block`
--

LOCK TABLES `t_ocr_block` WRITE;
/*!40000 ALTER TABLE `t_ocr_block` DISABLE KEYS */;
INSERT INTO `t_ocr_block` VALUES (1,0,'','gif|jpg|png|bmp','法轮功|李洪志|大纪元|真善忍|新唐人|毛一鲜|黎阳平|张小平|戴海静|赵紫阳|胡耀邦|六四事件|退党|天葬|禁书|枪决现场|疆独|藏独|反共|中共|达赖|班禅|东突|台独|台海|肉棍|淫靡|淫水|迷药|迷昏药|色情服务|成人片|三级片|激情小电影|黄色小电影|色情小电影|援交|打炮|口活|吹萧|打飞机|冰火|毒龙|全身漫游|休闲按摩|丝袜美女|推油|毛片|淫荡|骚妇|熟女|成人电影|换妻|丝袜美足|走光|摇头丸|海洛因|白面|迷幻醉|春药|催情|三唑仑|麻醉乙醚|遗忘药|佳境安定片|蒙汗药粉|麻醉药|买卖枪支|出售枪支|投毒杀人|手机复制|麻醉钢枪|枪支弹药|鬼村|雷管|古方迷香|强效忆药|迷奸药|代考|考研枪手|套牌|刻章|办证|证件集团|办理证件|窃听器|汽车解码器|汽车拦截器|开锁枪|侦探设备|远程偷拍|电表反转调效器|特码|翻牌|办理文凭|代开发票|监听王|透视眼镜|全选|全不选|名字|个人护理|登录|天气',12,'2018-01-03 17:30:36');
/*!40000 ALTER TABLE `t_ocr_block` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_overflowset`
--

DROP TABLE IF EXISTS `t_overflowset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_overflowset` (
  `id` int(11) DEFAULT NULL COMMENT 'rule id',
  `name` varchar(45) NOT NULL,
  `value` int(11) NOT NULL,
  `status` tinyint(4) DEFAULT NULL COMMENT '0:disable 1:enable',
  `secname` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='protect http  head overflow set';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_overflowset`
--

LOCK TABLES `t_overflowset` WRITE;
/*!40000 ALTER TABLE `t_overflowset` DISABLE KEYS */;
INSERT INTO `t_overflowset` VALUES (300200,'Accept',2048,1,'REQUEST_HEADERS:Accept');
INSERT INTO `t_overflowset` VALUES (300201,'Accept-Charset',2048,1,'REQUEST_HEADERS:Accept-Charset');
INSERT INTO `t_overflowset` VALUES (300202,'Accept-Encoding',2048,1,'REQUEST_HEADERS:Accept-Encoding');
INSERT INTO `t_overflowset` VALUES (300203,'Cookie',32767,1,'REQUEST_HEADERS:Cookie');
INSERT INTO `t_overflowset` VALUES (300204,'Post',10000000,1,'REQUEST_BODY');
INSERT INTO `t_overflowset` VALUES (300205,'URI',2048,1,'REQUEST_URI');
INSERT INTO `t_overflowset` VALUES (300206,'Host',2048,1,'REQUEST_HEADERS:Host');
INSERT INTO `t_overflowset` VALUES (300207,'Referer',2048,1,'REQUEST_HEADERS:Referer');
INSERT INTO `t_overflowset` VALUES (300208,'Authorization',2048,1,'REQUEST_HEADERS:Authorization');
INSERT INTO `t_overflowset` VALUES (300209,'Poxy-Authorization',2048,1,'REQUEST_HEADERS:Poxy-Authorization');
INSERT INTO `t_overflowset` VALUES (300210,'User-Agent',2048,1,'REQUEST_HEADERS:User-Agent');
/*!40000 ALTER TABLE `t_overflowset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_pcap`
--

DROP TABLE IF EXISTS `t_pcap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_pcap` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `net` varchar(50) NOT NULL,
  `port` varchar(50) NOT NULL,
  `time` varchar(50) DEFAULT NULL,
  `token` varchar(200) DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  `userid` int(11) DEFAULT NULL,
  `pid` int(11) DEFAULT '0',
  `status` tinyint(1) NOT NULL COMMENT '1=2=',
  `createtime` int(11) DEFAULT NULL,
  `updatetime` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_pcap`
--

LOCK TABLES `t_pcap` WRITE;
/*!40000 ALTER TABLE `t_pcap` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_pcap` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_realportname`
--

DROP TABLE IF EXISTS `t_realportname`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_realportname` (
  `lan` varchar(10) NOT NULL,
  `netport` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`lan`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_realportname`
--

LOCK TABLES `t_realportname` WRITE;
/*!40000 ALTER TABLE `t_realportname` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_realportname` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_record_history`
--

DROP TABLE IF EXISTS `t_record_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_record_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `new_table_name` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `start_time` int(11) DEFAULT NULL,
  `end_time` int(11) DEFAULT NULL,
  `ori_table_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=410 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_record_history`
--

LOCK TABLES `t_record_history` WRITE;
/*!40000 ALTER TABLE `t_record_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_record_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_redirectpage`
--

DROP TABLE IF EXISTS `t_redirectpage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_redirectpage` (
  `redirect_id` tinyint(4) NOT NULL,
  `name` varchar(255) NOT NULL,
  `desc` varchar(255) DEFAULT NULL,
  `http_code` varchar(255) DEFAULT NULL COMMENT 'http result code , e: 200 OK',
  `server` varchar(255) DEFAULT NULL,
  `page` varchar(1024) NOT NULL COMMENT 'page content, html',
  PRIMARY KEY (`redirect_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='redirect page set';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_redirectpage`
--

LOCK TABLES `t_redirectpage` WRITE;
/*!40000 ALTER TABLE `t_redirectpage` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_redirectpage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_reportsmanage`
--

DROP TABLE IF EXISTS `t_reportsmanage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_reportsmanage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `type` tinyint(4) DEFAULT NULL COMMENT '1IDS report, 2 flow report, 3 access report',
  `desc` varchar(255) DEFAULT NULL,
  `time` int(11) DEFAULT NULL COMMENT 'report create time',
  `path` varchar(255) NOT NULL,
  `timetype` tinyint(2) NOT NULL,
  `format` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=475 DEFAULT CHARSET=utf8 COMMENT='报表管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_reportsmanage`
--

LOCK TABLES `t_reportsmanage` WRITE;
/*!40000 ALTER TABLE `t_reportsmanage` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_reportsmanage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_restrictext`
--

DROP TABLE IF EXISTS `t_restrictext`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_restrictext` (
  `id` tinyint(4) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `status` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_restrictext`
--

LOCK TABLES `t_restrictext` WRITE;
/*!40000 ALTER TABLE `t_restrictext` DISABLE KEYS */;
INSERT INTO `t_restrictext` VALUES (1,'.asa',1);
INSERT INTO `t_restrictext` VALUES (2,'.asax',1);
INSERT INTO `t_restrictext` VALUES (3,'.ascx',1);
INSERT INTO `t_restrictext` VALUES (4,'.axd',1);
INSERT INTO `t_restrictext` VALUES (5,'.backup',1);
INSERT INTO `t_restrictext` VALUES (6,'.bak',1);
INSERT INTO `t_restrictext` VALUES (7,'.bat',1);
INSERT INTO `t_restrictext` VALUES (8,'.cdx',1);
INSERT INTO `t_restrictext` VALUES (9,'.cer',1);
INSERT INTO `t_restrictext` VALUES (10,'.cfg',1);
INSERT INTO `t_restrictext` VALUES (11,'.cmd',1);
INSERT INTO `t_restrictext` VALUES (12,'.com',1);
INSERT INTO `t_restrictext` VALUES (13,'.config',1);
INSERT INTO `t_restrictext` VALUES (14,'.conf',1);
INSERT INTO `t_restrictext` VALUES (15,'.cs',1);
INSERT INTO `t_restrictext` VALUES (16,'.csproj',1);
INSERT INTO `t_restrictext` VALUES (17,'.csr',1);
INSERT INTO `t_restrictext` VALUES (18,'.dat',1);
INSERT INTO `t_restrictext` VALUES (19,'.db',1);
INSERT INTO `t_restrictext` VALUES (20,'.dbf',1);
INSERT INTO `t_restrictext` VALUES (21,'.dll',1);
INSERT INTO `t_restrictext` VALUES (22,'.dos',1);
INSERT INTO `t_restrictext` VALUES (23,'.htr',1);
INSERT INTO `t_restrictext` VALUES (24,'.htw',1);
INSERT INTO `t_restrictext` VALUES (25,'.ids',1);
INSERT INTO `t_restrictext` VALUES (26,'.idc',1);
INSERT INTO `t_restrictext` VALUES (27,'.idq',1);
INSERT INTO `t_restrictext` VALUES (28,'.inc',1);
INSERT INTO `t_restrictext` VALUES (29,'.ini',1);
INSERT INTO `t_restrictext` VALUES (30,'.key',1);
INSERT INTO `t_restrictext` VALUES (31,'.licx',1);
INSERT INTO `t_restrictext` VALUES (32,'.lnk',1);
INSERT INTO `t_restrictext` VALUES (33,'.log',1);
INSERT INTO `t_restrictext` VALUES (34,'.mdb',1);
INSERT INTO `t_restrictext` VALUES (35,'.old',1);
INSERT INTO `t_restrictext` VALUES (36,'.pass',1);
INSERT INTO `t_restrictext` VALUES (37,'.pdb',1);
INSERT INTO `t_restrictext` VALUES (38,'.pol',1);
INSERT INTO `t_restrictext` VALUES (39,'.printer',1);
INSERT INTO `t_restrictext` VALUES (40,'.pwd',1);
INSERT INTO `t_restrictext` VALUES (41,'.resources',1);
INSERT INTO `t_restrictext` VALUES (42,'.resx',1);
INSERT INTO `t_restrictext` VALUES (43,'.sql',1);
INSERT INTO `t_restrictext` VALUES (44,'.sys',1);
INSERT INTO `t_restrictext` VALUES (45,'.vb',1);
INSERT INTO `t_restrictext` VALUES (46,'.vbs',1);
INSERT INTO `t_restrictext` VALUES (47,'.vbproj',1);
INSERT INTO `t_restrictext` VALUES (48,'.vsdisco',1);
INSERT INTO `t_restrictext` VALUES (49,'.webinfo',1);
INSERT INTO `t_restrictext` VALUES (50,'.xsd',1);
INSERT INTO `t_restrictext` VALUES (51,'.xsx',1);
/*!40000 ALTER TABLE `t_restrictext` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_restrictheaders`
--

DROP TABLE IF EXISTS `t_restrictheaders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_restrictheaders` (
  `id` tinyint(4) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `status` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_restrictheaders`
--

LOCK TABLES `t_restrictheaders` WRITE;
/*!40000 ALTER TABLE `t_restrictheaders` DISABLE KEYS */;
INSERT INTO `t_restrictheaders` VALUES (1,'Proxy-Connection',0);
INSERT INTO `t_restrictheaders` VALUES (2,'Lock-Token',0);
INSERT INTO `t_restrictheaders` VALUES (3,'Content-Range',0);
INSERT INTO `t_restrictheaders` VALUES (4,'Translate',0);
INSERT INTO `t_restrictheaders` VALUES (5,'via',0);
INSERT INTO `t_restrictheaders` VALUES (6,'if',0);
/*!40000 ALTER TABLE `t_restrictheaders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_reverporxy`
--

DROP TABLE IF EXISTS `t_reverporxy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_reverporxy` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) NOT NULL COMMENT 'host name',
  `proto` varchar(10) DEFAULT NULL COMMENT 'http/https',
  `hatype` varchar(30) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT 'HA Algorithm:1poll, 2IP hash, 3weight',
  `cache` tinyint(4) DEFAULT '0' COMMENT '0:no cache 1:cache',
  `helthcheck` tinyint(4) DEFAULT '0' COMMENT '0 no check, 1 check',
  `locals` varchar(1024) DEFAULT NULL COMMENT 'local NIC and port，format：eth0:port;eth1:port',
  `servers` varchar(1024) DEFAULT NULL COMMENT 'servers，format：ip1:port1:weight1;ip2:port2:weight2',
  `ssl_path1` varchar(255) DEFAULT NULL COMMENT 'ssl file path1',
  `ssl_path2` varchar(255) DEFAULT NULL COMMENT 'ssl file path',
  `remark` varchar(255) DEFAULT NULL COMMENT 'remark information',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='the reverse proxy set';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_reverporxy`
--

LOCK TABLES `t_reverporxy` WRITE;
/*!40000 ALTER TABLE `t_reverporxy` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_reverporxy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_rule_model`
--

DROP TABLE IF EXISTS `t_rule_model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_rule_model` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rule` text COLLATE utf8_unicode_ci COMMENT '策略内容，使用json字符串存储, 在里面的就是不启用规则',
  `ruleDefault` text COLLATE utf8_unicode_ci COMMENT '这是rule字段的 预设规则ID',
  `type` smallint(1) DEFAULT NULL COMMENT '模板类型，1为站点组模板，2为站点特殊模板',
  `isDefault` tinyint(3) NOT NULL DEFAULT '0' COMMENT '1为默认预设模板',
  `groupModelId` int(11) DEFAULT NULL COMMENT '站点组的规则策略模板id',
  `different` text COLLATE utf8_unicode_ci COMMENT '记录了这个当前模板跟继承的被选中的不一样 规则ID',
  `name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '模板名称，最多20字',
  `remark` varchar(355) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '备注，最多100字',
  `ischecked` tinyint(1) DEFAULT NULL COMMENT '是否被选用',
  `confName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'python那边需要的字段',
  PRIMARY KEY (`id`),
  KEY `groupId` (`groupModelId`),
  CONSTRAINT `groupId` FOREIGN KEY (`groupModelId`) REFERENCES `t_rule_model` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='规则模板设置';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_rule_model`
--

LOCK TABLES `t_rule_model` WRITE;
/*!40000 ALTER TABLE `t_rule_model` DISABLE KEYS */;
INSERT INTO `t_rule_model` VALUES (1,'[\"960008\",\"960007\",\"960015\",\"960021\",\"960009\",\"960006\",\"960904\",\"960017\",\"960209\",\"960208\",\"960335\",\"960341\",\"960342\",\"960343\",\"960032\",\"960010\",\"960034\",\"960035\",\"960038\",\"990002\",\"990901\",\"990902\",\"990012\",\"950103\",\"950110\",\"950921\",\"950922\",\"981020\",\"981021\",\"981022\",\"981175\",\"981176\",\"970007\",\"970008\",\"970009\",\"970010\",\"970012\",\"970903\",\"970016\",\"970018\",\"970901\",\"970118\",\"970021\",\"970011\",\"981177\",\"981000\",\"981001\",\"981003\",\"981004\",\"981005\",\"981006\",\"981007\",\"981178\",\"970014\",\"970015\",\"970902\",\"970002\",\"970003\",\"970004\",\"970904\",\"970013\",\"981200\",\"981201\",\"981202\",\"981203\",\"981204\",\"981205\",\"950002\",\"950006\",\"950103\",\"950110\",\"950115\",\"950119\",\"950907\",\"950921\",\"950922\",\"970004\",\"970011\",\"970013\",\"970018\",\"970021\",\"970904\",\"981020\",\"981021\",\"981051\",\"960911\",\"981227\",\"960000\",\"960912\",\"960914\",\"960915\",\"960016\",\"960011\",\"960012\",\"960902\",\"960022\",\"960020\",\"958291\",\"958230\",\"958231\",\"958295\",\"950107\",\"950109\",\"950108\",\"950801\",\"950116\",\"960901\",\"960018\",\"950907\",\"960024\",\"950008\",\"950010\",\"950011\",\"950018\",\"950019\",\"950012\",\"950910\",\"950911\",\"950117\",\"950118\",\"950119\",\"950120\",\"981133\",\"981134\",\"950009\",\"950003\",\"950000\",\"950005\",\"950002\",\"950006\",\"959151\",\"958976\",\"958977\",\"981231\",\"981260\",\"981318\",\"981319\",\"950901\",\"981320\",\"981300\",\"981301\",\"981302\",\"981303\",\"981304\",\"981305\",\"981306\",\"981307\",\"981308\",\"981309\",\"981310\",\"981311\",\"981312\",\"981313\",\"981314\",\"981315\",\"981316\",\"981317\",\"950007\",\"950001\",\"959070\",\"959071\",\"959072\",\"950908\",\"959073\",\"981172\",\"981173\",\"981272\",\"981244\",\"981255\",\"981257\",\"981248\",\"981277\",\"981250\",\"981241\",\"981252\",\"981256\",\"981245\",\"981276\",\"981254\",\"981270\",\"981240\",\"981249\",\"981253\",\"981242\",\"981246\",\"981251\",\"981247\",\"981243\",\"973336\",\"973337\",\"973338\",\"981136\",\"981018\",\"958016\",\"958414\",\"958032\",\"958026\",\"958027\",\"958054\",\"958418\",\"958034\",\"958019\",\"958013\",\"958408\",\"958012\",\"958423\",\"958002\",\"958017\",\"958007\",\"958047\",\"958410\",\"958415\",\"958022\",\"958405\",\"958419\",\"958028\",\"958057\",\"958031\",\"958006\",\"958033\",\"958038\",\"958409\",\"958001\",\"958005\",\"958404\",\"958023\",\"958010\",\"958411\",\"958422\",\"958036\",\"958000\",\"958018\",\"958406\",\"958040\",\"958052\",\"958037\",\"958049\",\"958030\",\"958041\",\"958416\",\"958024\",\"958059\",\"958417\",\"958020\",\"958045\",\"958004\",\"958421\",\"958009\",\"958025\",\"958413\",\"958051\",\"958420\",\"958407\",\"958056\",\"958011\",\"958412\",\"958008\",\"958046\",\"958039\",\"958003\",\"973300\",\"973301\",\"973302\",\"973303\",\"973304\",\"973305\",\"973306\",\"973307\",\"973308\",\"973309\",\"973310\",\"973311\",\"973312\",\"973313\",\"973314\",\"973331\",\"973315\",\"973330\",\"973327\",\"973326\",\"973346\",\"973345\",\"973324\",\"973323\",\"973322\",\"973348\",\"973321\",\"973320\",\"973318\",\"973317\",\"973347\",\"973335\",\"973334\",\"973333\",\"973344\",\"973332\",\"973329\",\"973328\",\"973316\",\"973325\",\"973319\"]','[\"960008\",\"960007\",\"960015\",\"960021\",\"960009\",\"960006\",\"960904\",\"960017\",\"960209\",\"960208\",\"960335\",\"960341\",\"960342\",\"960343\",\"960032\",\"960010\",\"960034\",\"960035\",\"960038\",\"990002\",\"990901\",\"990902\",\"990012\",\"950103\",\"950110\",\"950921\",\"950922\",\"981020\",\"981021\",\"981022\",\"981175\",\"981176\",\"970007\",\"970008\",\"970009\",\"970010\",\"970012\",\"970903\",\"970016\",\"970018\",\"970901\",\"970118\",\"970021\",\"970011\",\"981177\",\"981000\",\"981001\",\"981003\",\"981004\",\"981005\",\"981006\",\"981007\",\"981178\",\"970014\",\"970015\",\"970902\",\"970002\",\"970003\",\"970004\",\"970904\",\"970013\",\"981200\",\"981201\",\"981202\",\"981203\",\"981204\",\"981205\",\"950002\",\"950006\",\"950103\",\"950110\",\"950115\",\"950119\",\"950907\",\"950921\",\"950922\",\"970004\",\"970011\",\"970013\",\"970018\",\"970021\",\"970904\",\"981020\",\"981021\",\"981051\",\"960911\",\"981227\",\"960000\",\"960912\",\"960914\",\"960915\",\"960016\",\"960011\",\"960012\",\"960902\",\"960022\",\"960020\",\"958291\",\"958230\",\"958231\",\"958295\",\"950107\",\"950109\",\"950108\",\"950801\",\"950116\",\"960901\",\"960018\",\"950907\",\"960024\",\"950008\",\"950010\",\"950011\",\"950018\",\"950019\",\"950012\",\"950910\",\"950911\",\"950117\",\"950118\",\"950119\",\"950120\",\"981133\",\"981134\",\"950009\",\"950003\",\"950000\",\"950005\",\"950002\",\"950006\",\"959151\",\"958976\",\"958977\",\"981231\",\"981260\",\"981318\",\"981319\",\"950901\",\"981320\",\"981300\",\"981301\",\"981302\",\"981303\",\"981304\",\"981305\",\"981306\",\"981307\",\"981308\",\"981309\",\"981310\",\"981311\",\"981312\",\"981313\",\"981314\",\"981315\",\"981316\",\"981317\",\"950007\",\"950001\",\"959070\",\"959071\",\"959072\",\"950908\",\"959073\",\"981172\",\"981173\",\"981272\",\"981244\",\"981255\",\"981257\",\"981248\",\"981277\",\"981250\",\"981241\",\"981252\",\"981256\",\"981245\",\"981276\",\"981254\",\"981270\",\"981240\",\"981249\",\"981253\",\"981242\",\"981246\",\"981251\",\"981247\",\"981243\",\"973336\",\"973337\",\"973338\",\"981136\",\"981018\",\"958016\",\"958414\",\"958032\",\"958026\",\"958027\",\"958054\",\"958418\",\"958034\",\"958019\",\"958013\",\"958408\",\"958012\",\"958423\",\"958002\",\"958017\",\"958007\",\"958047\",\"958410\",\"958415\",\"958022\",\"958405\",\"958419\",\"958028\",\"958057\",\"958031\",\"958006\",\"958033\",\"958038\",\"958409\",\"958001\",\"958005\",\"958404\",\"958023\",\"958010\",\"958411\",\"958422\",\"958036\",\"958000\",\"958018\",\"958406\",\"958040\",\"958052\",\"958037\",\"958049\",\"958030\",\"958041\",\"958416\",\"958024\",\"958059\",\"958417\",\"958020\",\"958045\",\"958004\",\"958421\",\"958009\",\"958025\",\"958413\",\"958051\",\"958420\",\"958407\",\"958056\",\"958011\",\"958412\",\"958008\",\"958046\",\"958039\",\"958003\",\"973300\",\"973301\",\"973302\",\"973303\",\"973304\",\"973305\",\"973306\",\"973307\",\"973308\",\"973309\",\"973310\",\"973311\",\"973312\",\"973313\",\"973314\",\"973331\",\"973315\",\"973330\",\"973327\",\"973326\",\"973346\",\"973345\",\"973324\",\"973323\",\"973322\",\"973348\",\"973321\",\"973320\",\"973318\",\"973317\",\"973347\",\"973335\",\"973334\",\"973333\",\"973344\",\"973332\",\"973329\",\"973328\",\"973316\",\"973325\",\"973319\"]',3,1,NULL,'[]','默认模板(普通)','默认模板(普通)',NULL,'default_normal');
INSERT INTO `t_rule_model` VALUES (2,'[\"960008\",\"960007\",\"960015\",\"960021\",\"960009\",\"960006\",\"960904\",\"960017\",\"960209\",\"960208\",\"960335\",\"960341\",\"960342\",\"960343\",\"960032\",\"960010\",\"960034\",\"960035\",\"960038\",\"990002\",\"990901\",\"990902\",\"990012\",\"950103\",\"950110\",\"950921\",\"950922\",\"981020\",\"981021\",\"981022\",\"981175\",\"981176\",\"970007\",\"970008\",\"970009\",\"970010\",\"970012\",\"970903\",\"970016\",\"970018\",\"970901\",\"970118\",\"970021\",\"970011\",\"981177\",\"981000\",\"981001\",\"981003\",\"981004\",\"981005\",\"981006\",\"981007\",\"981178\",\"970014\",\"970015\",\"970902\",\"970002\",\"970003\",\"970004\",\"970904\",\"970013\",\"981200\",\"981201\",\"981202\",\"981203\",\"981204\",\"981205\",\"950002\",\"950006\",\"950103\",\"950110\",\"950115\",\"950119\",\"950907\",\"950921\",\"950922\",\"970004\",\"970011\",\"970013\",\"970018\",\"970021\",\"970904\",\"981020\",\"981021\",\"981051\",\"960911\",\"981227\",\"960000\",\"960912\",\"960914\",\"960915\",\"960016\",\"960011\",\"960012\",\"960902\",\"960022\",\"960020\",\"958291\",\"958230\",\"958231\",\"958295\",\"950107\",\"950109\",\"950108\",\"950801\",\"950116\",\"960901\",\"960018\",\"950907\",\"960024\",\"950008\",\"950010\",\"950011\",\"950018\",\"950019\",\"950012\",\"950910\",\"950911\",\"950117\",\"950118\",\"950119\",\"950120\",\"981133\",\"981134\",\"950009\",\"950003\",\"950000\",\"950005\",\"950002\",\"950006\",\"959151\",\"958976\",\"958977\",\"981231\",\"981260\",\"981318\",\"981319\",\"950901\",\"981320\",\"981300\",\"981301\",\"981302\",\"981303\",\"981304\",\"981305\",\"981306\",\"981307\",\"981308\",\"981309\",\"981310\",\"981311\",\"981312\",\"981313\",\"981314\",\"981315\",\"981316\",\"981317\",\"950007\",\"950001\",\"959070\",\"959071\",\"959072\",\"950908\",\"959073\",\"981172\",\"981173\",\"981272\",\"981244\",\"981255\",\"981257\",\"981248\",\"981277\",\"981250\",\"981241\",\"981252\",\"981256\",\"981245\",\"981276\",\"981254\",\"981270\",\"981240\",\"981249\",\"981253\",\"981242\",\"981246\",\"981251\",\"981247\",\"981243\",\"973336\",\"973337\",\"973338\",\"981136\",\"981018\",\"958016\",\"958414\",\"958032\",\"958026\",\"958027\",\"958054\",\"958418\",\"958034\",\"958019\",\"958013\",\"958408\",\"958012\",\"958423\",\"958002\",\"958017\",\"958007\",\"958047\",\"958410\",\"958415\",\"958022\",\"958405\",\"958419\",\"958028\",\"958057\",\"958031\",\"958006\",\"958033\",\"958038\",\"958409\",\"958001\",\"958005\",\"958404\",\"958023\",\"958010\",\"958411\",\"958422\",\"958036\",\"958000\",\"958018\",\"958406\",\"958040\",\"958052\",\"958037\",\"958049\",\"958030\",\"958041\",\"958416\",\"958024\",\"958059\",\"958417\",\"958020\",\"958045\",\"958004\",\"958421\",\"958009\",\"958025\",\"958413\",\"958051\",\"958420\",\"958407\",\"958056\",\"958011\",\"958412\",\"958008\",\"958046\",\"958039\",\"958003\",\"973300\",\"973301\",\"973302\",\"973303\",\"973304\",\"973305\",\"973306\",\"973307\",\"973308\",\"973309\",\"973310\",\"973311\",\"973312\",\"973313\",\"973314\",\"973331\",\"973315\",\"973330\",\"973327\",\"973326\",\"973346\",\"973345\",\"973324\",\"973323\",\"973322\",\"973348\",\"973321\",\"973320\",\"973318\",\"973317\",\"973347\",\"973335\",\"973334\",\"973333\",\"973344\",\"973332\",\"973329\",\"973328\",\"973316\",\"973325\",\"973319\",\"900040\",\"900041\",\"900042\",\"900043\",\"999005\",\"999006\",\"981036\",\"981037\",\"981038\",\"981039\",\"981040\",\"981041\",\"981042\",\"981043\",\"981044\",\"981045\",\"981045\",\"981046\",\"981047\",\"981048\",\"981049\",\"981050\",\"981051\",\"981052\",\"981053\",\"981054\",\"981055\",\"981056\",\"981057\",\"981058\",\"981059\",\"981060\",\"981061\",\"981062\",\"981063\",\"981064\",\"981078\",\"981079\",\"920019\",\"920005\",\"920007\",\"920009\",\"920011\",\"920015\",\"920017\",\"981080\",\"981081\",\"920020\",\"920006\",\"920008\",\"920010\",\"920012\",\"920016\",\"920018\",\"920021\",\"920022\",\"920023\",\"981082\",\"981085\",\"981086\",\"981087\",\"981088\",\"981089\",\"981090\",\"981091\",\"981092\",\"981093\",\"981094\",\"981095\",\"981096\",\"981097\",\"981103\",\"981104\",\"981110\",\"981105\",\"981098\",\"981099\",\"981100\",\"981101\",\"981102\",\"981131\",\"981132\",\"900032\",\"981137\",\"981138\",\"981139\",\"981140\",\"958297\",\"999010\",\"999011\",\"950923\",\"950020\",\"981142\",\"960001\",\"960002\",\"960003\",\"981143\",\"981144\",\"981145\",\"950115\",\"999003\",\"999004\",\"999008\",\"900033\",\"900034\",\"900035\",\"900044\",\"900045\",\"981219\",\"981220\",\"981221\",\"981222\",\"981223\",\"981224\",\"981237\",\"981238\",\"981235\",\"981184\",\"981236\",\"981185\",\"981239\",\"900046\",\"981400\",\"981401\",\"981402\",\"981403\",\"981404\",\"981405\",\"981406\",\"981407\",\"900047\",\"900048\",\"981180\",\"981181\",\"981182\",\"910008\",\"910007\",\"910006\",\"981187\",\"981188\",\"981189\",\"981190\",\"981191\",\"981192\",\"981193\",\"981194\",\"981195\",\"981196\",\"981197\",\"981198\",\"981199\",\"900036\",\"900037\",\"900038\",\"900039\"]','[\"960008\",\"960007\",\"960015\",\"960021\",\"960009\",\"960006\",\"960904\",\"960017\",\"960209\",\"960208\",\"960335\",\"960341\",\"960342\",\"960343\",\"960032\",\"960010\",\"960034\",\"960035\",\"960038\",\"990002\",\"990901\",\"990902\",\"990012\",\"950103\",\"950110\",\"950921\",\"950922\",\"981020\",\"981021\",\"981022\",\"981175\",\"981176\",\"970007\",\"970008\",\"970009\",\"970010\",\"970012\",\"970903\",\"970016\",\"970018\",\"970901\",\"970118\",\"970021\",\"970011\",\"981177\",\"981000\",\"981001\",\"981003\",\"981004\",\"981005\",\"981006\",\"981007\",\"981178\",\"970014\",\"970015\",\"970902\",\"970002\",\"970003\",\"970004\",\"970904\",\"970013\",\"981200\",\"981201\",\"981202\",\"981203\",\"981204\",\"981205\",\"950002\",\"950006\",\"950103\",\"950110\",\"950115\",\"950119\",\"950907\",\"950921\",\"950922\",\"970004\",\"970011\",\"970013\",\"970018\",\"970021\",\"970904\",\"981020\",\"981021\",\"981051\",\"960911\",\"981227\",\"960000\",\"960912\",\"960914\",\"960915\",\"960016\",\"960011\",\"960012\",\"960902\",\"960022\",\"960020\",\"958291\",\"958230\",\"958231\",\"958295\",\"950107\",\"950109\",\"950108\",\"950801\",\"950116\",\"960901\",\"960018\",\"950907\",\"960024\",\"950008\",\"950010\",\"950011\",\"950018\",\"950019\",\"950012\",\"950910\",\"950911\",\"950117\",\"950118\",\"950119\",\"950120\",\"981133\",\"981134\",\"950009\",\"950003\",\"950000\",\"950005\",\"950002\",\"950006\",\"959151\",\"958976\",\"958977\",\"981231\",\"981260\",\"981318\",\"981319\",\"950901\",\"981320\",\"981300\",\"981301\",\"981302\",\"981303\",\"981304\",\"981305\",\"981306\",\"981307\",\"981308\",\"981309\",\"981310\",\"981311\",\"981312\",\"981313\",\"981314\",\"981315\",\"981316\",\"981317\",\"950007\",\"950001\",\"959070\",\"959071\",\"959072\",\"950908\",\"959073\",\"981172\",\"981173\",\"981272\",\"981244\",\"981255\",\"981257\",\"981248\",\"981277\",\"981250\",\"981241\",\"981252\",\"981256\",\"981245\",\"981276\",\"981254\",\"981270\",\"981240\",\"981249\",\"981253\",\"981242\",\"981246\",\"981251\",\"981247\",\"981243\",\"973336\",\"973337\",\"973338\",\"981136\",\"981018\",\"958016\",\"958414\",\"958032\",\"958026\",\"958027\",\"958054\",\"958418\",\"958034\",\"958019\",\"958013\",\"958408\",\"958012\",\"958423\",\"958002\",\"958017\",\"958007\",\"958047\",\"958410\",\"958415\",\"958022\",\"958405\",\"958419\",\"958028\",\"958057\",\"958031\",\"958006\",\"958033\",\"958038\",\"958409\",\"958001\",\"958005\",\"958404\",\"958023\",\"958010\",\"958411\",\"958422\",\"958036\",\"958000\",\"958018\",\"958406\",\"958040\",\"958052\",\"958037\",\"958049\",\"958030\",\"958041\",\"958416\",\"958024\",\"958059\",\"958417\",\"958020\",\"958045\",\"958004\",\"958421\",\"958009\",\"958025\",\"958413\",\"958051\",\"958420\",\"958407\",\"958056\",\"958011\",\"958412\",\"958008\",\"958046\",\"958039\",\"958003\",\"973300\",\"973301\",\"973302\",\"973303\",\"973304\",\"973305\",\"973306\",\"973307\",\"973308\",\"973309\",\"973310\",\"973311\",\"973312\",\"973313\",\"973314\",\"973331\",\"973315\",\"973330\",\"973327\",\"973326\",\"973346\",\"973345\",\"973324\",\"973323\",\"973322\",\"973348\",\"973321\",\"973320\",\"973318\",\"973317\",\"973347\",\"973335\",\"973334\",\"973333\",\"973344\",\"973332\",\"973329\",\"973328\",\"973316\",\"973325\",\"973319\",\"900040\",\"900041\",\"900042\",\"900043\",\"999005\",\"999006\",\"981036\",\"981037\",\"981038\",\"981039\",\"981040\",\"981041\",\"981042\",\"981043\",\"981044\",\"981045\",\"981045\",\"981046\",\"981047\",\"981048\",\"981049\",\"981050\",\"981051\",\"981052\",\"981053\",\"981054\",\"981055\",\"981056\",\"981057\",\"981058\",\"981059\",\"981060\",\"981061\",\"981062\",\"981063\",\"981064\",\"981078\",\"981079\",\"920019\",\"920005\",\"920007\",\"920009\",\"920011\",\"920015\",\"920017\",\"981080\",\"981081\",\"920020\",\"920006\",\"920008\",\"920010\",\"920012\",\"920016\",\"920018\",\"920021\",\"920022\",\"920023\",\"981082\",\"981085\",\"981086\",\"981087\",\"981088\",\"981089\",\"981090\",\"981091\",\"981092\",\"981093\",\"981094\",\"981095\",\"981096\",\"981097\",\"981103\",\"981104\",\"981110\",\"981105\",\"981098\",\"981099\",\"981100\",\"981101\",\"981102\",\"981131\",\"981132\",\"900032\",\"981137\",\"981138\",\"981139\",\"981140\",\"958297\",\"999010\",\"999011\",\"950923\",\"950020\",\"981142\",\"960001\",\"960002\",\"960003\",\"981143\",\"981144\",\"981145\",\"950115\",\"999003\",\"999004\",\"999008\",\"900033\",\"900034\",\"900035\",\"900044\",\"900045\",\"981219\",\"981220\",\"981221\",\"981222\",\"981223\",\"981224\",\"981237\",\"981238\",\"981235\",\"981184\",\"981236\",\"981185\",\"981239\",\"900046\",\"981400\",\"981401\",\"981402\",\"981403\",\"981404\",\"981405\",\"981406\",\"981407\",\"900047\",\"900048\",\"981180\",\"981181\",\"981182\",\"910008\",\"910007\",\"910006\",\"981187\",\"981188\",\"981189\",\"981190\",\"981191\",\"981192\",\"981193\",\"981194\",\"981195\",\"981196\",\"981197\",\"981198\",\"981199\",\"900036\",\"900037\",\"900038\",\"900039\"]',3,0,NULL,'[]','默认模板(宽松)','默认模板(宽松)',NULL,'default_low');
INSERT INTO `t_rule_model` VALUES (3,'[\"960911\",\"981227\",\"960000\",\"960912\",\"960914\",\"960915\",\"960016\",\"960011\",\"960012\",\"960902\",\"960022\",\"960020\",\"958291\",\"958230\",\"958231\",\"958295\",\"950107\",\"950109\",\"950108\",\"950801\",\"950116\",\"960901\",\"960018\",\"950907\",\"960024\",\"950008\",\"950010\",\"950011\",\"950018\",\"950019\",\"950012\",\"950910\",\"950911\",\"950117\",\"950118\",\"950119\",\"950120\",\"981133\",\"981134\",\"950009\",\"950003\",\"950000\",\"950005\",\"950002\",\"950006\",\"959151\",\"958976\",\"958977\",\"981231\",\"981260\",\"981318\",\"981319\",\"950901\",\"981320\",\"981300\",\"981301\",\"981302\",\"981303\",\"981304\",\"981305\",\"981306\",\"981307\",\"981308\",\"981309\",\"981310\",\"981311\",\"981312\",\"981313\",\"981314\",\"981315\",\"981316\",\"981317\",\"950007\",\"950001\",\"959070\",\"959071\",\"959072\",\"950908\",\"959073\",\"981172\",\"981173\",\"981272\",\"981244\",\"981255\",\"981257\",\"981248\",\"981277\",\"981250\",\"981241\",\"981252\",\"981256\",\"981245\",\"981276\",\"981254\",\"981270\",\"981240\",\"981249\",\"981253\",\"981242\",\"981246\",\"981251\",\"981247\",\"981243\",\"973336\",\"973337\",\"973338\",\"981136\",\"981018\",\"958016\",\"958414\",\"958032\",\"958026\",\"958027\",\"958054\",\"958418\",\"958034\",\"958019\",\"958013\",\"958408\",\"958012\",\"958423\",\"958002\",\"958017\",\"958007\",\"958047\",\"958410\",\"958415\",\"958022\",\"958405\",\"958419\",\"958028\",\"958057\",\"958031\",\"958006\",\"958033\",\"958038\",\"958409\",\"958001\",\"958005\",\"958404\",\"958023\",\"958010\",\"958411\",\"958422\",\"958036\",\"958000\",\"958018\",\"958406\",\"958040\",\"958052\",\"958037\",\"958049\",\"958030\",\"958041\",\"958416\",\"958024\",\"958059\",\"958417\",\"958020\",\"958045\",\"958004\",\"958421\",\"958009\",\"958025\",\"958413\",\"958051\",\"958420\",\"958407\",\"958056\",\"958011\",\"958412\",\"958008\",\"958046\",\"958039\",\"958003\",\"973300\",\"973301\",\"973302\",\"973303\",\"973304\",\"973305\",\"973306\",\"973307\",\"973308\",\"973309\",\"973310\",\"973311\",\"973312\",\"973313\",\"973314\",\"973331\",\"973315\",\"973330\",\"973327\",\"973326\",\"973346\",\"973345\",\"973324\",\"973323\",\"973322\",\"973348\",\"973321\",\"973320\",\"973318\",\"973317\",\"973347\",\"973335\",\"973334\",\"973333\",\"973344\",\"973332\",\"973329\",\"973328\",\"973316\",\"973325\",\"973319\"]','[\"960911\",\"981227\",\"960000\",\"960912\",\"960914\",\"960915\",\"960016\",\"960011\",\"960012\",\"960902\",\"960022\",\"960020\",\"958291\",\"958230\",\"958231\",\"958295\",\"950107\",\"950109\",\"950108\",\"950801\",\"950116\",\"960901\",\"960018\",\"950907\",\"960024\",\"950008\",\"950010\",\"950011\",\"950018\",\"950019\",\"950012\",\"950910\",\"950911\",\"950117\",\"950118\",\"950119\",\"950120\",\"981133\",\"981134\",\"950009\",\"950003\",\"950000\",\"950005\",\"950002\",\"950006\",\"959151\",\"958976\",\"958977\",\"981231\",\"981260\",\"981318\",\"981319\",\"950901\",\"981320\",\"981300\",\"981301\",\"981302\",\"981303\",\"981304\",\"981305\",\"981306\",\"981307\",\"981308\",\"981309\",\"981310\",\"981311\",\"981312\",\"981313\",\"981314\",\"981315\",\"981316\",\"981317\",\"950007\",\"950001\",\"959070\",\"959071\",\"959072\",\"950908\",\"959073\",\"981172\",\"981173\",\"981272\",\"981244\",\"981255\",\"981257\",\"981248\",\"981277\",\"981250\",\"981241\",\"981252\",\"981256\",\"981245\",\"981276\",\"981254\",\"981270\",\"981240\",\"981249\",\"981253\",\"981242\",\"981246\",\"981251\",\"981247\",\"981243\",\"973336\",\"973337\",\"973338\",\"981136\",\"981018\",\"958016\",\"958414\",\"958032\",\"958026\",\"958027\",\"958054\",\"958418\",\"958034\",\"958019\",\"958013\",\"958408\",\"958012\",\"958423\",\"958002\",\"958017\",\"958007\",\"958047\",\"958410\",\"958415\",\"958022\",\"958405\",\"958419\",\"958028\",\"958057\",\"958031\",\"958006\",\"958033\",\"958038\",\"958409\",\"958001\",\"958005\",\"958404\",\"958023\",\"958010\",\"958411\",\"958422\",\"958036\",\"958000\",\"958018\",\"958406\",\"958040\",\"958052\",\"958037\",\"958049\",\"958030\",\"958041\",\"958416\",\"958024\",\"958059\",\"958417\",\"958020\",\"958045\",\"958004\",\"958421\",\"958009\",\"958025\",\"958413\",\"958051\",\"958420\",\"958407\",\"958056\",\"958011\",\"958412\",\"958008\",\"958046\",\"958039\",\"958003\",\"973300\",\"973301\",\"973302\",\"973303\",\"973304\",\"973305\",\"973306\",\"973307\",\"973308\",\"973309\",\"973310\",\"973311\",\"973312\",\"973313\",\"973314\",\"973331\",\"973315\",\"973330\",\"973327\",\"973326\",\"973346\",\"973345\",\"973324\",\"973323\",\"973322\",\"973348\",\"973321\",\"973320\",\"973318\",\"973317\",\"973347\",\"973335\",\"973334\",\"973333\",\"973344\",\"973332\",\"973329\",\"973328\",\"973316\",\"973325\",\"973319\"]',3,0,NULL,'[]','默认模板(严格)','默认模板(严格)',NULL,'default_high');
/*!40000 ALTER TABLE `t_rule_model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_rulecat`
--

DROP TABLE IF EXISTS `t_rulecat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_rulecat` (
  `id` int(11) NOT NULL,
  `name` varchar(45) NOT NULL,
  `desc` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='攻击类别';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_rulecat`
--

LOCK TABLES `t_rulecat` WRITE;
/*!40000 ALTER TABLE `t_rulecat` DISABLE KEYS */;
INSERT INTO `t_rulecat` VALUES (9,'ACCESSCTRL','访问控制');
INSERT INTO `t_rulecat` VALUES (10,'CC','CC攻击');
INSERT INTO `t_rulecat` VALUES (14,'CUSTOM','自定义');
INSERT INTO `t_rulecat` VALUES (3,'GENERIC','通用攻击');
INSERT INTO `t_rulecat` VALUES (6,'LEAKAGE','信息泄漏');
INSERT INTO `t_rulecat` VALUES (7,'OTHER','其他攻击');
INSERT INTO `t_rulecat` VALUES (8,'OVERFLOW','溢出攻击');
INSERT INTO `t_rulecat` VALUES (4,'PROTOCOL','HTTP保护');
INSERT INTO `t_rulecat` VALUES (1,'SQLI','SQL注入');
INSERT INTO `t_rulecat` VALUES (5,'TROJANS','木马病毒');
INSERT INTO `t_rulecat` VALUES (2,'XSS','跨站脚本');
/*!40000 ALTER TABLE `t_rulecat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_rulefiles`
--

DROP TABLE IF EXISTS `t_rulefiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_rulefiles` (
  `id` int(11) NOT NULL,
  `filename` varchar(255) DEFAULT NULL,
  `ruleids` varchar(8192) DEFAULT NULL,
  `desc` varchar(1024) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `isactive` tinyint(4) DEFAULT '0' COMMENT 'is actived?0no 1yes',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_rulefiles`
--

LOCK TABLES `t_rulefiles` WRITE;
/*!40000 ALTER TABLE `t_rulefiles` DISABLE KEYS */;
INSERT INTO `t_rulefiles` VALUES (42,'experimental_rules/modsecurity_crs_46_scanner_integration.conf','999003,999004',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (17,'optional_rules/modsecurity_crs_11_avs_traffic.conf',NULL,NULL,'optional',0);
INSERT INTO `t_rulefiles` VALUES (33,'experimental_rules/modsecurity_crs_11_slow_dos_protection.conf','981051,981052',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (27,'optional_rules/modsecurity_crs_49_header_tagging.conf','900045,900044',NULL,'optional',0);
INSERT INTO `t_rulefiles` VALUES (38,'experimental_rules/modsecurity_crs_40_appsensor_detection_point_2.9_honeytrap.conf','981132,981131',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (41,'experimental_rules/modsecurity_crs_42_csp_enforcement.conf','960003,981142,960001,960002',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (18,'optional_rules/modsecurity_crs_13_xml_enabler.conf','981053','XML攻击防护','optional',1);
INSERT INTO `t_rulefiles` VALUES (37,'experimental_rules/modsecurity_crs_40_appsensor_detection_point_2.1_request_exception.conf','981110,981095,981094,981097,981096,981091,981090,981093,981092,981099,981098,981105,981104,981103,981102,981101,981100,981086,981087,981085,981088,981089',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (30,'experimental_rules/modsecurity_crs_11_brute_force.conf','981042,981043,981037,981036,981040,981041,981039,981038',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (43,'experimental_rules/modsecurity_crs_48_bayes_analysis.conf','900033,900034,900035',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (13,'base_rules/modsecurity_crs_50_outbound.conf','970118,970018,981177,970003,970011,970010,981178,970012,970015,970014,970016,970002,970021,970008,970009,970903,970902,970901,970007,970004,970904,981006,981007,981004,981005,981003,981000,981001,970013','信息泄漏（程序代码泄漏防护、服务器信息泄漏防护、HTTP错误码防护）','base',0);
INSERT INTO `t_rulefiles` VALUES (8,'base_rules/modsecurity_crs_41_xss_attacks.conf','973335,973334,973337,973336,973331,973330,973333,973332,973338,973300,973301,973302,973303,973304,973305,973306,973307,973308,973309,958404,958405,958406,958407,958408,958409,958045,958046,958047,958040,958041,973319,973318,973317,973316,973315,973314,973313,958049,973311,973310,958413,958412,958411,958410,958417,958416,958415,958414,958419,958418,958052,958051,958057,958056,958054,958059,958026,958027,958024,958025,958022,958023,958020,981136,958028,973329,973344,973345,973346,973347,973348,958034,958037,958036,958031,958030,958033,958032,958039,958038,958000,958001,958002,958003,958004,958005,958006,958007,958008,958009,973312,973326,973327,973324,973325,973322,973323,973320,973321,973328,981018,958019,958018,958017,958016,958013,958012,958011,958010,958422,958423,958420,958421','XSS跨站脚本防护','base',1);
INSERT INTO `t_rulefiles` VALUES (25,'optional_rules/modsecurity_crs_46_av_scanning.conf','950115',NULL,'optional',0);
INSERT INTO `t_rulefiles` VALUES (9,'base_rules/modsecurity_crs_42_tight_security.conf','950103','目录遍历防护','base',1);
INSERT INTO `t_rulefiles` VALUES (32,'experimental_rules/modsecurity_crs_11_proxy_abuse.conf','981050',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (45,'experimental_rules/modsecurity_crs_56_pvi_checks.conf','981198,981199',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (39,'experimental_rules/modsecurity_crs_40_appsensor_detection_point_3.0_end.conf',NULL,NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (34,'experimental_rules/modsecurity_crs_16_scanner_integration.conf',NULL,NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (16,'optional_rules/modsecurity_crs_10_ignore_static.conf','999006,999005,900041,900040,900043,900042',NULL,'optional',0);
INSERT INTO `t_rulefiles` VALUES (3,'base_rules/modsecurity_crs_23_request_limits.conf','960335,960341,960342,960343,960209,960208','溢出攻击防护','base',0);
INSERT INTO `t_rulefiles` VALUES (29,'optional_rules/modsecurity_crs_55_marketing.conf','910006,910007,910008',NULL,'optional',0);
INSERT INTO `t_rulefiles` VALUES (22,'optional_rules/modsecurity_crs_25_cc_known.conf','920010,920011,920012,920015,920009,920017,920007,920019,920005,920008,920016,920018,981079,981078,920006,981080,981081,920020','信用卡信息防护','optional',0);
INSERT INTO `t_rulefiles` VALUES (4,'base_rules/modsecurity_crs_30_http_policy.conf','960032,960038,960010,960034,960035','HTTP保护（HTTP策略设置）','base',1);
INSERT INTO `t_rulefiles` VALUES (44,'experimental_rules/modsecurity_crs_55_response_profiling.conf','981196,981197,981190,981191,981192,981193,981194,981195,981189,981188,981187',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (11,'base_rules/modsecurity_crs_47_common_exceptions.conf','981020,981021,981022','通用异常防护（APACHE、FLASH等）','base',1);
INSERT INTO `t_rulefiles` VALUES (15,'base_rules/modsecurity_crs_60_correlation.conf','981204,981205,981201,981202,981203',NULL,'base',0);
INSERT INTO `t_rulefiles` VALUES (24,'optional_rules/modsecurity_crs_43_csrf_protection.conf','981143,981145,981144','CSRF攻击防护','optional',1);
INSERT INTO `t_rulefiles` VALUES (7,'base_rules/modsecurity_crs_41_sql_injection_attacks.conf','959072,959073,959070,959071,981270,981231,950908,981255,981254,981253,981260,981251,981250,950901,981272,981305,981304,981307,981306,981301,981300,981303,981302,981277,981276,981309,981308,981320,981172,950001,950007,981248,981249,981246,981173,981257,981316,981317,981314,981315,981312,981313,981310,981311,981240,981241,981242,981247,981244,981245,981318,981319,981243,981256,981252','SQL注入防护','base',1);
INSERT INTO `t_rulefiles` VALUES (1,'base_rules/modsecurity_crs_20_protocol_violations.conf','960018,960911,960016,960912,960915,960914,960012,950801,960022,958231,958230,950107,950109,950108,958291,958295,960020,960901,960902,960000,960011,981227,950116','HTTP保护（HTTP协议违规防护）','base',1);
INSERT INTO `t_rulefiles` VALUES (5,'base_rules/modsecurity_crs_35_bad_robots.conf','990012,990901,990002,990902','爬虫与扫描攻击防护','base',1);
INSERT INTO `t_rulefiles` VALUES (10,'base_rules/modsecurity_crs_45_trojans.conf','950922,950110,950921','木马病毒','base',1);
INSERT INTO `t_rulefiles` VALUES (36,'experimental_rules/modsecurity_crs_40_appsensor_detection_point_2.0_setup.conf','981082',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (12,'base_rules/modsecurity_crs_49_inbound_blocking.conf','981176,981175',NULL,'base',0);
INSERT INTO `t_rulefiles` VALUES (28,'optional_rules/modsecurity_crs_55_application_defects.conf','900047,981219,981235,981237,981236,981239,981238,981402,981403,981400,981401,981406,981407,981404,981405,981222,981223,981220,981221,981224,900046,900048,981185,981184,981182,981181,981180',NULL,'optional',0);
INSERT INTO `t_rulefiles` VALUES (26,'optional_rules/modsecurity_crs_47_skip_outbound_checks.conf','999008',NULL,'optional',0);
INSERT INTO `t_rulefiles` VALUES (2,'base_rules/modsecurity_crs_21_protocol_anomalies.conf','960021,960009,960008,960015,960017,960007,960006,960904','HTTP协议异常防护','base',1);
INSERT INTO `t_rulefiles` VALUES (46,'experimental_rules/modsecurity_crs_61_ip_forensics.conf','900038,900039,900036,900037',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (21,'optional_rules/modsecurity_crs_16_username_tracking.conf',NULL,NULL,'optional',0);
INSERT INTO `t_rulefiles` VALUES (6,'base_rules/modsecurity_crs_40_generic_attacks.conf','959151,958976,958977,950907,981134,950120,981133,950008,950009,950000,950002,950003,950005,950006,960024,950910,950911,950012,950117,950011,950010,950118,950119,950019,950018','通用攻击（LDAP注入防护，命令注入防护、代码注入防护、XML注入防护、EMAIL注入防护、SSI注入防护、UPDF XSS防护、HTTP请求走私防护、HTTP响应分片防护、远程文件包含防护、空字节注入防护）','base',1);
INSERT INTO `t_rulefiles` VALUES (23,'optional_rules/modsecurity_crs_42_comment_spam.conf','950923,999010,999011,981138,981139,981137,950020,981140,958297','垃圾评论防护','optional',0);
INSERT INTO `t_rulefiles` VALUES (40,'experimental_rules/modsecurity_crs_40_http_parameter_pollution.conf','900032',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (19,'optional_rules/modsecurity_crs_16_authentication_tracking.conf',NULL,NULL,'optional',0);
INSERT INTO `t_rulefiles` VALUES (35,'experimental_rules/modsecurity_crs_25_cc_track_pan.conf','920021,920023,920022',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (14,'base_rules/modsecurity_crs_59_outbound_blocking.conf','981200',NULL,'base',0);
INSERT INTO `t_rulefiles` VALUES (31,'experimental_rules/modsecurity_crs_11_dos_protection.conf','981046,981047,981044,981045,981048,981049',NULL,'experimental',0);
INSERT INTO `t_rulefiles` VALUES (20,'optional_rules/modsecurity_crs_16_session_hijacking.conf','981064,981055,981054,981057,981056,981059,981058,981060,981061,981062,981063','COOKIE防护','optional',0);
INSERT INTO `t_rulefiles` VALUES (47,'slr_rules/modsecurity_crs_46_slr_et_sqli_attacks.conf','2003757,2003763,2003769,2003775,2003781,2003787,2003793,2003798,2003810,2003816,2003822,2003828,2003834,2003840,2003845,2003851,2003857,2003863,2003944,2003950,2003956,2003962,2003968,2003974,2003986,2003992,2003998,2004004,2004010,2004022,2004028,2004034,2004040,2004046,2004052,2004058,2004064,2004070,2004076,2004082,2004088,2004094,2004100,2004106,2004113,2004121,2004127,2004133,2004139,2004145,2004151,2004157,2004163,2004169,2004175,2004181,2004187,2004193,2004199,2004205,2004211,2004217,2004223,2004229,2004234,2004240,2004246,2004252,2004258,2004264,2004270,2004276,2004282,2004288,2004294,2004300,2004306,2004312,2004317,2004324,2004330,2004336,2004342,2004348,2004354,2004360,2004366,2004372,2004378,2004384,2004390,2004402,2004414,2004420,2004426,2004432,2004438,2004455,2004461,2004468,2004469,2004473,2004479,2004485,2004491,2004498,2004504,2004510,2004516,2004522,2004528,2004534,2004540,2004546,2004551,2004605,2004617,2004623,2004629,2004634,2004640,2004646,2004652,2004665,2004671,2004677,2004682,2004688,2004694,2004700,2004710,2004716,2004723,2004729,2004735,2004741,2004747,2004753,2004759,2004765,2004771,2004778,2004784,2004790,2004802,2004808,2004815,2004821,2004827,2004833,2004839,2004845,2004850,2004856,2004862,2004868,2004874,2004880,2004886,2004892,2004898,2004904,2004910,2004916,2004923,2004929,2004935,2004941,2004948,2004954,2004960,2004966,2004972,2004984,2004990,2004996,2005002,2005008,2005014,2005020,2005026,2005032,2005038,2005045,2005050,2005056,2005062,2005068,2005074,2005080,2005086,2005092,2005098,2005104,2005110,2005116,2005122,2005128,2005134,2005140,2005146,2005151,2005163,2005169,2005175,2005181,2005191,2005197,2005203,2005209,2005215,2005221,2005226,2005232,2005238,2005244,2005250,2005255,2005261,2005267,2005273,2005279,2005285,2005291,2005309,2005329,2005335,2005341,2005347,2005353,2005359,2005365,2005371,2005377,2005383,2005389,2005461,2005467,2005473,2005479,2005485,2005492,2005498,2005504,2005510,2005517,2005523,2005529,2005535,2005541,2005547,2005553,2005559,2005566,2005572,2005578,2005584,2005590,2005596,2005602,2005608,2005614,2005620,2005626,2005632,2005638,2005644,2005650,2005656,2005668,2005674,2005680,2005686,2005692,2005698,2005704,2005710,2005716,2005722,2005728,2005734,2005741,2005747,2005753,2005759,2005765,2005771,2005777,2005783,2005789,2005795,2005801,2005810,2005816,2005822,2005828,2005834,2005840,2005846,2005852,2005858,2005864,2005876,2005882,2005888,2005894,2005900,2005906,2005912,2005918,2005924,2005930,2005936,2005942,2005948,2005954,2005960,2005966,2005978,2005984,2005990,2005996,2006002,2006008,2006014,2006020,2006026,2006032,2006038,2006044,2006050,2006056,2006062,2006068,2006074,2006080,2006086,2006092,2006098,2006104,2006110,2006116,2006122,2006128,2006134,2006140,2006146,2006152,2006158,2006164,2006170,2006176,2006182,2006188,2006194,2006200,2006206,2006212,2006218,2006224,2006230,2006236,2006242,2006248,2006254,2006260,2006266,2006272,2006278,2006284,2006290,2006296,2006302,2006308,2006314,2006320,2006326,2006332,2006338,2006344,2006350,2006356,2006454,2006460,2006466,2006472,2006478,2006485,2006491,2006497,2006503,2006509,2006515,2006521,2006527,2006533,2006539,2006545,2006552,2006559,2006566,2006572,2006578,2006584,2006590,2006596,2006602,2006608,2006614,2006620,2006626,2006632,2006638,2006644,2006650,2006656,2006662,2006668,2006674,2006680,2006686,2006692,2006699,2006705,2006711,2006717,2006735,2006741,2006747,2006753,2006759,2006765,2006771,2006777,2006788,2006794,2006800,2006806,2006812,2006818,2006824,2006830,2006836,2006842,2006848,2006854,2006860,2006867,2006873,2006879,2006885,2006891,2006897,2006903,2006909,2006926,2006932,2006938,2006944,2006950,2006956,2006962,2006968,2006980,2006986,2006992,2006998,2007005,2007011,2007017,2007023,2007035,2007041,2007047,2007049,2007053,2007065,2007075,2007081,2007087,2007093,2007099,2007105,2007111,2007117,2007123,2007129,2007135,2007141,2007181,2007187,2007193,2007199,2007204,2007210,2007216,2007222,2007228,2007234,2007240,2007246,2007252,2007258,2007264,2007270,2007276,2007282,2007293,2007299,2007305,2007311,2007317,2007323,2007329,2007335,2007341,2007349,2007355,2007361,2007367,2007373,2007379,2007385,2007391,2007397,2007403,2007409,2007415,2007421,2007427,2007433,2007439,2007445,2007451,2007457,2007463,2007469,2007475,2007481,2007486,2007492,2007498,2007515,2007521,2007527,2007533,2007539,2007545,2007551,2007557,2007563,2007565,2007892,2007897,2009979,2010073,2010078,2010135,2010189,2010275,2010619,2010656,2011061,2011095,2011137,2011159,2011172,2011219,2011266,2011382,2011450,2011730,2011835,2011841,2011879,2011934,2011947,2012005,2012020,2012030,2012038,2012163,2012215,2012342,2012350,2012363,2012368,2012378,2012425,2012473,2012490,2012560,2012570,2012580,2012600,2012655,2012677,2012702,2012719,2012749,2012792,2012876,2012991,2013084,2013129,2013231,2013307','Web漏洞攻击','slr_rules',0);
INSERT INTO `t_rulefiles` VALUES (48,'slr_rules/modsecurity_crs_46_slr_et_rfi_attacks.conf','2002800,2002996,2003333,2003517,2003669,2003670,2003671,2003672,2003673,2003674,2003675,2003676,2003677,2003678,2003679,2003680,2003682,2003683,2003684,2003687,2003688,2003689,2003690,2003691,2003696,2003698,2003699,2003700,2003701,2003702,2003703,2003704,2003705,2003706,2003707,2003708,2003709,2003710,2003711,2003712,2003713,2003714,2003715,2003716,2003718,2003719,2003720,2003721,2003722,2003723,2003724,2003725,2003726,2003727,2003728,2003729,2003730,2003731,2003732,2003733,2003735,2003736,2003737,2003738,2003739,2003740,2003741,2003742,2003743,2003744,2003745,2003746,2003747,2003867,2008826,2008833,2008871,2008879,2008897,2008899,2008900,2008901,2008902,2008903,2008904,2008922,2008962,2008966,2008967,2008968,2008969,2008970,2008996,2009051,2009053,2009059,2009060,2009061,2009062,2009071,2009101,2009123,2009141,2009142,2009144,2009163,2009164,2009165,2009166,2009167,2009179,2009180,2009188,2009190,2009196,2009225,2009229,2009316,2009317,2009318,2009321,2009325,2009326,2009327,2009333,2009364,2009370,2009371,2009372,2009378,2009379,2009381,2009382,2009386,2009395,2009397,2009398,2009415,2009416,2009427,2009432,2009435,2009459,2009460,2009466,2009467,2009468,2009502,2009504,2009506,2009653,2009654,2009663,2009690,2009691,2009717,2009723,2009733,2009754,2009755,2009756,2009757,2009758,2009759,2009760,2009788,2009793,2009838,2009839,2009840,2009841,2009842,2009843,2009844,2009845,2009846,2009848,2009870,2009871,2009872,2009873,2009874,2009877,2009888,2009889,2009890,2009891,2009898,2009903,2010024,2010027,2010080,2010092,2010093,2010094,2010095,2010096,2010097,2010099,2010124,2010125,2010126,2010191,2010192,2010193,2010197,2010198,2010223,2010252,2010276,2010354,2010355,2010359,2010360,2010361,2010362,2010466,2010475,2010484,2010485,2010564,2010661,2010707,2010708,2010709,2010771,2010772,2010773,2010774,2010775,2010776,2010777,2010847,2010922,2010923,2010979,2011000,2011018,2011051,2011052,2011062,2011063,2011096,2011097,2011098,2011099,2011100,2011116,2011161,2011164,2011165,2011167,2011209,2011214,2011254,2011255,2011259,2011274,2011377,2011384,2011454,2011552,2011553,2011564,2011565,2011725,2011831,2011837,2011880,2011881,2011948,2011949,2011950,2012006,2012007,2012013,2012015,2012024,2012031,2012130,2012165,2012181,2012182,2012184,2012185,2012334,2012344,2012496,2012497,2012561,2012562,2012563,2012564,2012565,2012572,2012583,2012584,2012604,2012605,2012724,2012743,2012795,2012877,2012878,2012879,2012880,2012881,2012950,2012951,2012952,2012953,2012954,2012994,2013087,2013088,2013089,2013465,2013466,100000356,100000357,100000358,100000728,100000729,100000730,100000731,100000732,100000733,100000734,100000735,100000736,100000737,100000738,100000739,100000740,100000741,100000742,100000908','文件包含漏洞攻击','slr_rules',0);
INSERT INTO `t_rulefiles` VALUES (49,'slr_rules/modsecurity_crs_46_slr_et_lfi_attacks.conf','2008651,2008652,2008687,2008832,2008849,2008850,2008851,2008852,2008853,2008854,2008855,2008856,2008857,2008858,2008878,2008880,2008881,2008882,2008898,2008923,2008937,2008961,2008992,2009018,2009070,2009085,2009087,2009089,2009145,2009168,2009169,2009181,2009182,2009191,2009194,2009195,2009224,2009230,2009231,2009306,2009308,2009310,2009312,2009320,2009324,2009329,2009330,2009331,2009332,2009377,2009380,2009390,2009393,2009396,2009417,2009418,2009420,2009421,2009422,2009423,2009428,2009429,2009430,2009431,2009436,2009437,2009461,2009462,2009463,2009464,2009503,2009505,2009507,2009508,2009509,2009652,2009659,2009660,2009661,2009719,2009720,2009724,2009726,2009728,2009729,2009743,2009745,2009746,2009761,2009764,2009789,2009790,2009875,2009876,2009904,2009905,2009926,2009928,2010023,2010025,2010127,2010255,2010631,2010800,2010801,2010802,2010803,2010804,2011140,2011453,2011562,2011563,2011572,2011573,2011574,2011828,2011829,2011830,2011843,2011846,2011853,2011882,2011883,2011884,2011928,2011936,2011941,2012008,2012010,2012012,2012025,2012032,2012033,2012069,2012071,2012122,2012123,2012124,2012125,2012126,2012127,2012128,2012129,2012168,2012186,2012217,2012336,2012343,2012354,2012373,2012657,2012668,2012721,2012750,2012794,2012945,2012947,2012949','文件包含漏洞攻击','slr_rules',0);
INSERT INTO `t_rulefiles` VALUES (50,'slr_rules/modsecurity_crs_46_slr_et_xss_attacks.conf','2001218,2003167,2003871,2003872,2003873,2003874,2003875,2003876,2003877,2003878,2003879,2003880,2003881,2003882,2003883,2003884,2003886,2003887,2003888,2003889,2003890,2003891,2003892,2003893,2003894,2003895,2003896,2003902,2003906,2003907,2003908,2003909,2003910,2003911,2003912,2003913,2003914,2003915,2003916,2003917,2003918,2003919,2003920,2003921,2003922,2004552,2004554,2004555,2004557,2004558,2004559,2004560,2004561,2004562,2004563,2004564,2004565,2004566,2004567,2004568,2004569,2004570,2004571,2004572,2004573,2004574,2004575,2004576,2004577,2004578,2004579,2004580,2004581,2004582,2004583,2004584,2004585,2004586,2004587,2004588,2004589,2004590,2004591,2004592,2004593,2004594,2004595,2004596,2009590,2009591,2009592,2009593,2009647,2009671,2009672,2009673,2009990,2010031,2010082,2010145,2010146,2010147,2010167,2010168,2010169,2010170,2010171,2010172,2010173,2010174,2010175,2010176,2010177,2010178,2010179,2010180,2010181,2010182,2010183,2010184,2010200,2010770,2010862,2010865,2010980,2011054,2011065,2011082,2011083,2011114,2011115,2011117,2011152,2011153,2011154,2011190,2011191,2011192,2011193,2011194,2011195,2011268,2011383,2011423,2011452,2011566,2011571,2011676,2011731,2011845,2011852,2011927,2012011,2012023,2012040,2012070,2012187,2012190,2012191,2012216,2012220,2012337,2012351,2012355,2012370,2012371,2012380,2012394,2012395,2012418,2012419,2012474,2012475,2012483,2012484,2012573,2012574,2012582,2012603,2012656,2012658,2012669,2012670,2012678,2012679,2012680,2012681,2012706,2012797,2012992,2013085,2013086,2013099,2013100,2013101,2013102,2013103,2013104,2013105,2013106,2013107,2013108,2013109,2013110,2013111,2013112,2013117,2013118,2013133,2013134,2013226,2013434','Web漏洞攻击','slr_rules',0);
INSERT INTO `t_rulefiles` VALUES (51,'slr_rules/modsecurity_crs_46_slr_et_wordpress_attacks.conf','2009010,2012407,2012408,2012426,2012571,2012705,2013309,2013464','文件包含漏洞攻击','slr_rules',0);
INSERT INTO `t_rulefiles` VALUES (52,'slr_rules/modsecurity_crs_46_slr_et_joomla_attacks.conf','2010714','Web漏洞攻击','slr_rules',0);
INSERT INTO `t_rulefiles` VALUES (53,'slr_rules/modsecurity_crs_46_slr_et_phpbb_attacks.conf','2008938,2009073,2009074','文件包含漏洞攻击','slr_rules',0);
/*!40000 ALTER TABLE `t_rulefiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_rules`
--

DROP TABLE IF EXISTS `t_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_rules` (
  `realid` int(11) NOT NULL DEFAULT '0' COMMENT '规则ID',
  `name` varchar(255) DEFAULT NULL COMMENT '规则名称',
  `content` varchar(1024) DEFAULT NULL COMMENT '规则说明',
  `desc` varchar(1024) DEFAULT NULL COMMENT '备注',
  `type` varchar(45) DEFAULT NULL COMMENT '攻击类别',
  `action` varchar(45) DEFAULT NULL COMMENT '拦截方式',
  `status` tinyint(3) DEFAULT NULL COMMENT '是否启用0disable 1enable',
  `update_time` int(11) DEFAULT NULL COMMENT '更新时间',
  `redirect_id` tinyint(4) DEFAULT NULL,
  `id` int(11) DEFAULT NULL COMMENT 'our rule id',
  `warn` varchar(10) DEFAULT NULL COMMENT '危害级别',
  `harm_desc` text COMMENT '危害描述',
  `suggest` text COMMENT '解决建议',
  `old_type` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`realid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='内置规则';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_rules`
--

LOCK TABLES `t_rules` WRITE;
/*!40000 ALTER TABLE `t_rules` DISABLE KEYS */;
INSERT INTO `t_rules` VALUES (301200,'Accept溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30000,'中危','当accept参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对Accpet字段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义Accept大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301201,'Accept-Charset溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30001,'中危','当Accept-Charset参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对Accpet-Charset字段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义Accept-Charset大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301202,'Accept-Encoding溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30002,'中危','当Accept-Encoding参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对Accpet-Encoding字段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义Accept-Encoding大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301203,'Cookie溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30003,'中危','当Cookie参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对Cookie字段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义Cookie大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301204,'Post溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30004,'中危','当Post参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对Post字段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义Post大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301205,'URI溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30005,'中危','当URI参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对URI段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义URI大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301206,'Host溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30006,'中危','当Host参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对Host段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义Host大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301207,'Referer溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30007,'中危','当Referer参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对Referer段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义Referer大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301208,'Authorization溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30008,'中危','当Authorization参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对Authorization字段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义Authorization大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301209,'Poxy-Authorization溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30009,'中危','当Poxy-Authorization参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对Poxy-Authorization字段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义Poxy-Authorization大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (301210,'User-Agent溢出','NULL','NULL','OVERFLOW','block',1,1395124100,NULL,30010,'中危','当User-Agent参数过长超出服务器缓存接收的范围便会导致溢出，攻击者通常会在溢出部分添加自己的代码达到攻击目的','可根据自身对User-Agent字段的数据需求到waf界页面的安全管理的HTTP防溢出设置里自定义User-Agent大小，一般不超过2048','OVERFLOW');
INSERT INTO `t_rules` VALUES (900032,'检测http请求参数是否发生参数污染(Http Parameter Pollution)','ARGS \"^\"','检测http请求参数是否发生参数污染(Http Parameter Pollution)，一些参数会重复出现','OTHER','block',1,1452647413,NULL,90166,'低危','这个漏洞由S. di Paola 与L. Caret Toni在2009年的OWASP上首次公布。这也是一种注入型的漏洞，攻击者通过在HTTP请求中插入特定的参数来发起攻击。如果Web应用中存在这样的漏洞，可以被攻击者利用来进行客户端或者服务器端的攻击。','要防止这种漏洞，除了要做好对输入参数的格式验证外，另外还需要意识到HTTP协议是允许同名的参数的，在整个应用的处理过程中要意识到这一点从而根据业务的特征对这样的情况作正确的处理。','OTHER');
INSERT INTO `t_rules` VALUES (900033,'检测是否发生web攻击（Bayes Analysis)','TX:\'/^\\\\\\d.*WEB_ATTACK/\'','如果发生web攻击，则记录日志，并执行bayes_train_spam.lua脚本（Bayes Analysis)','OTHER','block',1,1452647413,NULL,90036,'低危','　　用户可能会执行与Web服务器权限外的任意系统命令','建议在web服务器对用户输入的数据进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (900034,'执行bayes_check_spam.lua脚本（Bayes Analysis)','SecRuleScript lua/bayes_check_spam.lua','执行bayes_check_spam.lua脚本，发生阻断（Bayes Analysis)','OTHER','block',1,1452647413,NULL,90037,'低危','','','OTHER');
INSERT INTO `t_rules` VALUES (900035,'检测异常分数是否为0（Bayes Analysis)','&TX:ANOMALY_SCORE \"@eq 0\" ','如果异常分数为0，则记录日志，并执行bayes_train_ham.lua脚本（Bayes Analysis)','OTHER','block',1,1452647413,NULL,90038,'低危','攻击者频繁的对服务器进行违规的操作，不加以措施应对，将会引起更为严重的后果。','建议web服务器设置实时黑名单机制，过滤高频违规操作的请求id。','OTHER');
INSERT INTO `t_rules` VALUES (900036,'检测异常分数是否大于0（IP Forensics)','TX:ANOMALY_SCORE \"@gt 0\"','如果异常分数大于0，则执行gather_ip_data.lua脚本，进行IP查找检测（IP Forensics)','OTHER','block',1,1452647413,NULL,90153,'低危','攻击者频繁的对服务器进行违规的操作，不加以措施应对，将会引起更为严重的后果。','建议web服务器设置实时黑名单机制，过滤高频违规操作的请求id。','OTHER');
INSERT INTO `t_rules` VALUES (900037,'检测hostname（IP Forensics）','TX:HOSTNAME \".*\"','检测hostname，并记录日志（IP Forensics）','OTHER','block',1,1452647413,NULL,90154,'低危','攻击者频繁的对服务器进行违规的操作，不加以措施应对，将会引起更为严重的后果。','建议web服务器记录下每次访问的用户的域名。','OTHER');
INSERT INTO `t_rules` VALUES (900038,'检测异常分数是否大于0（IP Forensics)','TX:ANOMALY_SCORE \"@gt 0\"','如果异常分数大于0，则记录日志，日志内容为ip的hostname（IP Forensics)','OTHER','block',1,1452647413,NULL,90151,'低危','攻击者频繁的对服务器进行违规的操作，不加以措施应对，将会引起更为严重的后果。','建议web服务器设置实时黑名单机制，过滤高频违规操作的请求id。','OTHER');
INSERT INTO `t_rules` VALUES (900039,'检测事务处理异常分数是否大于0（IP Forensics)','TX:ANOMALY_SCORE \"@gt 0\"','如果异常分数大于0，则记录日志，日志内容为GeoIP数据（IP Forensics)','OTHER','block',1,1452647413,NULL,90152,'低危','攻击者频繁的对服务器进行违规的操作，不加以措施应对，将会引起更为严重的后果。','建议web服务器设置实时黑名单机制，过滤高频违规操作的请求id。','OTHER');
INSERT INTO `t_rules` VALUES (900040,'检测请求方法是GET或HEAD的请求是否有参数及以文件扩展名结束(Ignore Static)','REQUEST_METHOD \"^(?:GET|HEAD)$\"','如果请求方式是GET或HEAD，并且该请求没有带参数同时是以静态内容文件扩展名结尾的，则跳过该请求的检测(Ignore Static)','OTHER','block',1,1452647413,NULL,90056,'低危','攻击者会利用媒体文件以外的一切文件上传到服务器，实施攻击。','','OTHER');
INSERT INTO `t_rules` VALUES (900041,'初始化动作为允许访问，跳过静态内容检测规则(Ignore Static)','SecAction \"phase:2,id:\'900041\',t:none,nolog,pass,skipAfter:END_STATIC_CONTENT_CHECK\"','初始化动作为允许访问，跳过静态内容检测规则(Ignore Static','OTHER','block',1,1452647413,NULL,90055,'低危','攻击者会利用媒体文件以外的一切文件上传到服务器，实施攻击。','','OTHER');
INSERT INTO `t_rules` VALUES (900042,'检测请求文件名（以jpeg、png、gif及ico扩展名结尾的图片文件）(Ignore Static)','REQUEST_FILENAME \"\\.(?:(?:jpe?|pn)g|gif|ico)$\"','如果请求文件名是以jpeg、png、gif及ico扩展名结尾的图片文件，则允许访问(Ignore Static)','OTHER','block',1,1452647413,NULL,90058,'低危','攻击者会利用媒体文件以外的一切文件上传到服务器，实施攻击。','','OTHER');
INSERT INTO `t_rules` VALUES (900043,'检测请求文件名（以doc、pdf、txt及xls扩展名结尾的文本文件）(Ignore Static)','REQUEST_FILENAME \"\\.(?:doc|pdf|txt|xls)$\"','如果请求文件名是以doc、pdf、txt及xls扩展名结尾的文本文件，则允许访问并设置相关参数(Ignore Static)','OTHER','block',1,1452647413,NULL,90057,'低危','攻击者会利用媒体文件以外的一切文件上传到服务器，实施攻击。','','OTHER');
INSERT INTO `t_rules` VALUES (900044,'检测anomaly score数值(Header Tagging)','TX:ANOMALY_SCORE \"@eq 0\"','如果anomaly score数值为0，则跳过请求头标识规则(Header Tagging)','OTHER','block',1,1452647413,NULL,90006,'低危','攻击者频繁的对服务器进行违规的操作，不加以措施应对，将会引起更为严重的后果。','建议web服务器设置实时黑名单机制，过滤高频违规操作的请求id。','OTHER');
INSERT INTO `t_rules` VALUES (900045,'检测请求头部分是否匹配发出异常事件规则(Header Tagging)','TX:/^\\d/ \".\" ','检测请求头部分是否匹配发出异常事件规则，若符合规则，则记录相应的异常记录值(Header Tagging)','OTHER','block',1,1452647413,NULL,90005,'低危','攻击者会利用使响应头缺失 Cache-Control头的请求访问服务器。','建议web服务器把响应头缺失 Cache-Control头的应答过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (900046,'检测全局参数cache-control值以及响应头部Cache-Control字段(Application Defects)','GLOBAL:CHECK_CACHE_CONTROL \"@le 10\"','如果全局参数cache-control值少于等于10，则记录日志，如果响应头部的Cache-Control字段没有包含no-store，则设置相应的缓存参数值(Application Defects)','OTHER','block',1,1452647413,NULL,90143,'低危','攻击者会利用使响应头缺失 Cache-Control头的请求访问服务器。','建议web服务器把响应头缺失 Cache-Control头的应答过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (900047,'初始化XSS攻击防护动作为“继续处理”，并设置相关参数(Application Defects)','SecAction \"phase:1,id:\'900047\',nolog,pass,initcol:global=xss_list\"','初始化XSS攻击防护动作为“继续处理”，并设置相关参数(Application Defects)','OTHER','block',1,1452647413,NULL,90123,'低危','','','OTHER');
INSERT INTO `t_rules` VALUES (900048,'检测请求体中是否包含恶意的Meta-Characters(Application Defects)','&ARGS \"@gt 0\"','如果请求体中含有恶意的Meta-Characters，则禁止访问，返回403错误，并记录日志(Application Defects)','OTHER','block',1,1452647413,NULL,90144,'低危','攻击者会利用请求中带有恶意的没有编码说明的元字符的请求访问服务器。','建议web服务器带有恶意的没有编码说明的元字符的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (910006,'检测请求头中User-Agent的内容(Google爬虫)（Marketing)','(?:(?:gsa-crawler \\(enterprise; s4-e9lj2b82fjjaa; me\\@mycompany\\.com|adsbot-google \\(\\+http:\\/\\/www\\.google\\.com\\/adsbot\\.html)\\)|\\b(?:google(?:-sitemaps|bot)|mediapartners-google)\\b)\" \\','如果请求头中User-Agent的内容符合google爬虫行为，则阻断（Marketing）','OTHER','block',1,1452647413,NULL,90065,'低危','攻击者会使用GOOGLE爬虫访问服务器。','建议web服务器把请求user-agent头内容匹配(?:(?:gsa-crawler \\(enterprise; s4-e9lj2b82fjjaa; me\\@mycompany\\.com|adsbot-google \\(\\+http:\\/\\/www\\.google\\.com\\/adsbot\\.html)\\)|\\b(?:google(?:-sitemaps|bot)|mediapartners-google)\\b)正则表达式的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (910007,'检测请求头中User-Agent的内容(Yahoo爬虫)（Marketing)','\\byahoo(?:-(?:mmcrawler|blogs)|! slurp)\\b','如果请求头中User-Agent的内容符合yahoo爬虫行为，则阻断（Marketing）','OTHER','block',1,1452647413,NULL,90066,'低危','攻击者会使用YAHOO爬虫访问服务器。','建议web服务器把请求user-agent头内容匹配\\byahoo(?:-(?:mmcrawler|blogs)|! slurp)\\b正则表达式的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (910008,'检测请求头中User-Agent的内容(Msn爬虫)（Marketing)','msn(?:bot|ptc)','如果请求头中User-Agent的内容符合Msn爬虫行为，则阻断（Marketing）','OTHER','block',1,1452647413,NULL,90067,'低危','攻击者会使用MSN爬虫访问服务器。','建议web服务器把请求user-agent头内容匹配msn(?:bot|ptc)正则表达式的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (920005,'根据用户输入数据（日志及审查），检测已知信用卡类型（MasterCard信用卡号）（CC_Known)','?:^|[^\\d])(5[1-5]\\d{2}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4})(?:[^\\d]|$','从用户输入数据检测到MasterCard信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90076,'低危','如果发生银行卡卡号密码盗窃行为，会存在GSA SmartPay,MasterCard,Visa,American Express,Diner Club,Discover,JCB等信用卡卡号信息的输入处理，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对请求包参数中带有匹配(?:^|[^\\d])(5[1-5]\\d{2}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4})(?:[^\\d]|$)正则表达式的请求谨慎处理。（MasterCard信用卡号码）','OTHER');
INSERT INTO `t_rules` VALUES (920006,'根据用户输出数据（响应体及响应头），检测已知信用卡类型（MasterCard信用卡号）（CC_Known)','(?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(5[1-5]\\d{2}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4})(?:[^\\d]|$)','从网页到用户的输出数据检测到MasterCard信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90082,'高危','响应头和响应体中带有MasterCard信用卡的号码，攻击者企图在服务器上窃取该信用卡相关资料。','建议对响应包中出现匹配(?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(5[1-5]\\d{2}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4})(?:[^\\d]|$)正则表达式的应答进行限制。（MasterCard）','OTHER');
INSERT INTO `t_rules` VALUES (920007,'根据用户输入数据（日志及审查），检测已知信用卡类型（Visa信用卡号）（CC_Known)','?:^|[^\\d])(4\\d{3}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d(?:\\d{3})??)(?:[^\\d]|$)','从用户输入数据检测到Visa信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90074,'低危','如果发生银行卡卡号密码盗窃行为，会存在GSA SmartPay,MasterCard,Visa,American Express,Diner Club,Discover,JCB等信用卡卡号信息的输入处理，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对请求包参数中带有匹配(?:^|[^\\d])(4\\d{3}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d(?:\\d{3})??)(?:[^\\d]|$)正则表达式的请求谨慎处理。（Visa信用卡号码）','OTHER');
INSERT INTO `t_rules` VALUES (920008,'根据用户输出数据（响应体及响应头），检测信用卡类型（Visa信用卡号）（CC_Known)','?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(4\\d{3}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d(?:\\d{3})??)(?:[^\\d]|$','从网页到用户的输出数据检测到Visa信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90077,'高危','响应头和响应体中带有Visa信用卡的号码，攻击者企图在服务器上窃取该信用卡相关资料。','建议对响应包中出现匹配(?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(4\\d{3}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d(?:\\d{3})??)(?:[^\\d]|$)正则表达式的应答进行限制。（Visa）','OTHER');
INSERT INTO `t_rules` VALUES (920009,'根据用户输入数据（日志及审查），检测已知信用卡类型（American Express信用卡号）（CC_Known)','?:^|[^\\d])(3[47]\\d{2}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$)','从用户输入数据检测到American Express信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90072,'低危','如果发生银行卡卡号密码盗窃行为，会存在GSA SmartPay,MasterCard,Visa,American Express,Diner Club,Discover,JCB等信用卡卡号信息的输入处理，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对请求包参数中带有匹配(?:^|[^\\d])(3[47]\\d{2}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$)正则表达式的请求谨慎处理。（American Express信用卡号码）','OTHER');
INSERT INTO `t_rules` VALUES (920010,'根据用户输出数据（响应体及响应头），检测已知信用卡类型（American Express信用卡号）（CC_Known)','?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(3[47]\\d{2}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$)','从网页到用户的输出数据检测到American Express信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90068,'高危','响应头和响应体中带有American Express信用卡的号码，攻击者企图在服务器上窃取该信用卡相关资料。','建议对响应包中出现匹配 (?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(3[47]\\d{2}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$)正则表达式的应答进行限制。（American Express）','OTHER');
INSERT INTO `t_rules` VALUES (920011,'根据用户输入数据（日志及审查），检测已知信用卡类型（Diners Club信用卡号）（CC_Known)','?:^|[^\\d])((?:30[0-5]|3[68]\\d)\\d\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{2})(?:[^\\d]|$)','从用户输入数据检测到Diners Club信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90069,'低危','如果发生银行卡卡号密码盗窃行为，会存在GSA SmartPay,MasterCard,Visa,American Express,Diner Club,Discover,JCB等信用卡卡号信息的输入处理，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对请求包参数中带有匹配(?:^|[^\\d])((?:30[0-5]|3[68]\\d)\\d\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{2})(?:[^\\d]|$)正则表达式的请求谨慎处理。（Diners Club信用卡号码）','OTHER');
INSERT INTO `t_rules` VALUES (920012,'根据用户输出数据（响应体及响应头），检测已知信用卡类型（Diners Club信用卡号）（CC_Known)','?:^|[^\\d])(?<!google_ad_client = \\\"pub-)((?:30[0-5]|3[68]\\d)\\d\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{2})(?:[^\\d]|$','从网页到用户的输出数据检测到Diners Club信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90070,'高危','响应头和响应体中带有Diners Club信用卡的号码，攻击者企图在服务器上窃取该信用卡相关资料。','建议对响应包中出现匹配(?:^|[^\\d])(?<!google_ad_client = \\\"pub-)((?:30[0-5]|3[68]\\d)\\d\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{2})(?:[^\\d]|$)正则表达式的应答进行限制。（Diners Club）','OTHER');
INSERT INTO `t_rules` VALUES (920015,'根据用户输入数据（日志及审查），检测已知信用卡类型（Discover信用卡号）（CC_Known)','?:^|[^\\d])(6(?:011|5\\d{2})\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4})(?:[^\\d]|$','从用户输入数据检测到Discover信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90071,'低危','如果发生银行卡卡号密码盗窃行为，会存在GSA SmartPay,MasterCard,Visa,American Express,Diner Club,Discover,JCB等信用卡卡号信息的输入处理，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对请求包参数中带有匹配(?:^|[^\\d])(6(?:011|5\\d{2})\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4})(?:[^\\d]|$)正则表达式的请求谨慎处理。（Discover信用卡号码）','OTHER');
INSERT INTO `t_rules` VALUES (920016,'根据用户输出数据（响应体及响应头），检测已知信用卡类型（Discover信用卡号）（CC_Known)','?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(6(?:011|5\\d{2})\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4})(?:[^\\d]|$','从网页到用户的输出数据检测到Discover信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90078,'高危','响应头和响应体中带有Discover信用卡的号码，攻击者企图在服务器上窃取该信用卡相关资料。','建议对响应包中出现匹配(?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(6(?:011|5\\d{2})\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4})(?:[^\\d]|$)正则表达式的应答进行限制。（Discover）','OTHER');
INSERT INTO `t_rules` VALUES (920017,'根据用户输入数据（日志及审查），检测已知信用卡类型（JCB信用卡号）（CC_Known)','?:^|[^\\d])(3\\d{3}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4}|(?:1800|21(?:31|00))\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$','从用户输入数据检测到JCB信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90073,'低危','如果发生银行卡卡号密码盗窃行为，会存在GSA SmartPay,MasterCard,Visa,American Express,Diner Club,Discover,JCB等信用卡卡号信息的输入处理，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对请求包参数中带有匹配(?:^|[^\\d])(3\\d{3}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4}|(?:1800|21(?:31|00))\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$)正则表达式的请求谨慎处理。（JCB信用卡号码）','OTHER');
INSERT INTO `t_rules` VALUES (920018,'根据用户输出数据（响应体及响应头），检测已知信用卡类型（JCB信用卡号）（CC_Known)','?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(3\\d{3}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4}|(?:1800|21(?:31|00))\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$','从网页到用户的输出数据检测到JCB信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90079,'高危','响应头和响应体中带有JCB信用卡的号码，攻击者企图在服务器上窃取该信用卡相关资料。','建议对响应包中出现匹配(?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(3\\d{3}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4}|(?:1800|21(?:31|00))\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$)正则表达式的应答进行限制。（JCB）','OTHER');
INSERT INTO `t_rules` VALUES (920019,'根据用户输入数据（日志及审查），检测已知信用卡类型（GSA SmartPay信用卡号）（CC_Known)','?:^|[^\\d])((?:5568|4(?:486|716))\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4}|8699\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$','从用户输入数据检测到GSA SmartPay信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90075,'低危','如果发生银行卡卡号密码盗窃行为，会存在GSA SmartPay,MasterCard,Visa,American Express,Diner Club,Discover,JCB等信用卡卡号信息的输入处理，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对请求包参数中带有匹配(?:^|[^\\d])((?:5568|4(?:486|716))\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4}|8699\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$)正则表达式的请求谨慎处理。（GSA SmartPay信用卡号码）','OTHER');
INSERT INTO `t_rules` VALUES (920020,'根据用户输出数据（响应体及响应头），检测已知信用卡类型（GSA SmartPay信用卡号）（CC_Known)','?:^|[^\\d])(?<!google_ad_client = \\\"pub-)((?:5568|4(?:486|716))\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4}|8699\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$','从网页到用户的输出数据检测到GSA SmartPay信用卡号，记录日志（CC_Known)','OTHER','block',1,1452647413,NULL,90085,'高危','响应头和响应体中带有GSA SmartPay信用卡的号码，攻击者企图在服务器上窃取该信用卡相关资料。','建议对响应包中出现匹配(?:^|[^\\d])(?<!google_ad_client = \\\"pub-)((?:5568|4(?:486|716))\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{4}|8699\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{3})(?:[^\\d]|$)正则表达式的应答进行限制。（GSA SmartPay）','OTHER');
INSERT INTO `t_rules` VALUES (920021,'检测信用卡轨迹数据1是否泄漏（CC Track Pan）','\\%[Bb][3456][0-9]{3,3}[\\x20\\-]{0,3}[0-9]{4,6}[\\x20\\-]{0,3}[0-9]{2,5}[\\x20\\-]{0,3}[0-9]{0,4}\\^[^\\^]+\\^[0-9]+\\?','从响应体中检测到信用卡轨迹数据1发生泄漏，则阻断（CC_Track_Pan）','OTHER','block',1,1452647413,NULL,90167,'高危','攻击者可对信用卡的数据进行追踪，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对含有匹配\\%[Bb][3456][0-9]{3,3}[\\x20\\-]{0,3}[0-9]{4,6}[\\x20\\-]{0,3}[0-9]{2,5}[\\x20\\-]{0,3}[0-9]{0,4}\\^[^\\^]+\\^[0-9]+\\?正则表达式的响应包进行限制。','OTHER');
INSERT INTO `t_rules` VALUES (920022,'检测信用卡轨迹数据2是否泄漏（CC Track Pan）','\\;[3456][0-9]{3,3}[\\x20\\-]{0,3}[0-9]{4,6}[\\x20\\-]{0,3}[0-9]{2,5}[\\x20\\-]{0,3}[0-9]{0,4}[=Dd][0-9]+\\?','从响应体中检测到信用卡轨迹数据2发生泄漏，则阻断（CC_Track_Pan）','OTHER','block',1,1452647413,NULL,90169,'高危','攻击者可对信用卡的数据进行追踪，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对含有匹配\\;[3456][0-9]{3,3}[\\x20\\-]{0,3}[0-9]{4,6}[\\x20\\-]{0,3}[0-9]{2,5}[\\x20\\-]{0,3}[0-9]{0,4}[=Dd][0-9]+\\?正则表达式的响应包进行限制。','OTHER');
INSERT INTO `t_rules` VALUES (920023,'检测信用卡PAN数据是否泄漏（CC Track Pan）','[^0-9][3456][0-9]{3,3}[\\x20\\-]{0,3}[0-9]{4,6}[\\x20\\-]{0,3}[0-9]{2,5}[\\x20\\-]{0,3}[0-9]{0,4}[^0-9]','从响应体中检测到信用卡PAN数据发生泄漏，则阻断（CC_Track_Pan）','OTHER','block',1,1452647413,NULL,90168,'高危','攻击者可对信用卡的数据进行追踪，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','建议对含有匹配[^0-9][3456][0-9]{3,3}[\\x20\\-]{0,3}[0-9]{4,6}[\\x20\\-]{0,3}[0-9]{2,5}[\\x20\\-]{0,3}[0-9]{0,4}[^0-9]正则表达式的响应包进行限制。','OTHER');
INSERT INTO `t_rules` VALUES (950000,'SESSION加固(OWASP TOP 10)','jsessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession','检测可能的SESSION加固攻击，当来源为空时通过在http请求中检测jsessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession等来实现','GENERIC','block',0,1452647413,NULL,3016,'高危','利用请求参数名字中包含如jsessionid aspsessionid asp.net_sessionid phpsession phpsessid，然后请求头中排除Referer参数。可实施会话劫持攻击','建议web服务器把请求参数名为sessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession等单词的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950001,'SQL注入检测之一(OWASP TOP 10)','(?i:(?:(?:s(?:t(?:d(?:dev(_pop|_samp)?)?|r(?:_to_date|cmp))|u(?:b(?:str(?:ing(_index)?)?|(?:dat|tim)e)|m)|e(?:c(?:_to_time|ond)|ssion_user)|ys(?:tem_user|date)|ha(1|2)?|oundex|chema|ig?n|pace|qrt)|i(?:s(null|_(free_lock|ipv4_compat|ipv4_mapped|ipv4|ipv6|n','OWASP排名前10的SQL注入检测','SQLI','block',0,1395124100,NULL,1024,'高危','在cookies和请求参数和xml中利用 stddev_pop|ubstring_index|date|xp_ntsec_enumdemains|filelist|ercibility|butl_inaddr等字符，攻击者可尝试SQL注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有stddev_pop|ubstring_index|date|xp_ntsec_enumdemains|filelist|ercibility|butl_inaddr等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (950002,'系统命令访问(OWASP TOP 10)','\\b(?:(?:n(?:map|et|c)|w(?:guest|sh)|telnet|rcmd|ftp)\\.exe\\b|cmd(?:(?:32)?\\.exe\\b|\\b\\W*?\\/c))','该规则检测以下可能的系统命令访问：nmap net nc telnet ftp cmd32.exe','GENERIC','block',0,1452647413,NULL,3018,'高危','在cookies和请求参数和xml中利用(nmap|wguest|ftp|rcmd).exe，或者cmd.exe等字符串，可实施文件注入','建议web服务器把参数名，参数值和cookies和XML中包含匹配\\b(?:(?:n(?:map|et|c)|w(?:guest|sh)|telnet|rcmd|ftp)\\.exe\\b|cmd(?:(?:32)?\\.exe\\b|\\b\\W*?\\/c))正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950003,'SESSION加固(OWASP TOP 10)','jsessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession','检测可能的SESSION加固攻击，当来源为外站时通过在http请求中检测jsessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession等来实现','GENERIC','block',0,1452647413,NULL,3015,'高危','在请求参数名字中利用如jsessionid aspsessionid asp.net_sessionid phpsession phpsessid，然后在请求头中利用Referer参数为如https://attack.com。可实施会话劫持攻击','建议web服务器把请求参数名为sessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession等单词的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950005,'远程文件访问(OWASP TOP 10)','(?:\\b(?:\\.(?:ht(?:access|passwd|group)|www_?acl)|global\\.asa|httpd\\.conf|boot\\.ini)\\b|\\/etc\\/)','该规则检测COOKIE或url参数中的可能文件注入，主要通过以下关键词检测实现：httpd.conf boot.ini /etc/ .htaccess .htpasswd .htgroup','GENERIC','block',0,1452647413,NULL,3017,'高危','在cookies和请求参数和xml中利用global.asa|httpd.conf|boot.ini等字符串，可实施文件注入','建议web服务器把参数名，参数值和cookies和XML中包含匹配(?:\\b(?:\\.(?:ht(?:access|passwd|group)|www_?acl)|global\\.asa|httpd\\.conf|boot\\.ini)\\b|\\/etc\\/)正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950006,'系统命令注入(OWASP TOP 10)','(?:\\b(?:(?:n(?:et(?:\\b\\W+?\\blocalgroup|\\.exe)|(?:map|c)\\.exe)|t(?:racer(?:oute|t)|elnet\\.exe|clsh8?|ftp)|(?:w(?:guest|sh)|rcmd|ftp)\\.exe|echo\\b\\W*?\\by+)\\b|c(?:md(?:(?:\\.exe|32)\\b|\\b\\W*?\\/c)|d(?:\\b\\W*?[\\\\/]|\\W*?\\.\\.)|hmod.{0,40}?\\+.{0,3}x))|[\\;\\|\\`]\\W*?\\b(','该规则检测可能的系统命令注入：net.ext nmap.exe nc.exe traceroute tracert telnet.exe tclsh tftp ftp.exe echo cmd cd chmod等','GENERIC','block',0,1452647413,NULL,3019,'高危','攻击者可以通过在cookies和请求参数和xml中包含g++|gcc|echo|kill|nmap等字符串实施命令攻击','建议web服务器把参数名，参数值和cookies和XML中包含匹配(?:\\b(?:(?:n(?:et(?:\\b\\W+?\\blocalgroup|\\.exe)|(?:map|c)\\.exe)|t(?:racer(?:oute|t)|elnet\\.exe|clsh8?|ftp)|(?:w(?:guest|sh)|rcmd|ftp)\\.exe|echo\\b\\W*?\\by+)\\b|c(?:md(?:(?:\\.exe|32)\\b|\\b\\W*?\\/c)|d(?:\\b\\W*?[\\\\/]|\\W*?\\.\\.)|hmod.{','GENERIC');
INSERT INTO `t_rules` VALUES (950007,'SQL盲注检测(OWASP TOP 10)','(?i:(?:\\b(?:(?:s(?:ys\\.(?:user_(?:(?:t(?:ab(?:_column|le)|rigger)|object|view)s|c(?:onstraints|atalog))|all_tables|tab)|elect\\b.{0,40}\\b(?:substring|users?|ascii))|m(?:sys(?:(?:queri|ac)e|relationship|column|object)s|ysql\\.(db|user))|c(?:onstraint_type|ha','OWASP排名前10的SQL盲注检测','SQLI','block',0,1395124100,NULL,1023,'高危','在cookies和请求参数和xml中利用sys.user_tab_column|table_name|extpos&%(等字符，攻击者可尝试使用sheep()或者benchmark（）函数进行盲注测试。一旦成功将会进一步的攻击，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有sys.user_tab_column|table_name|extpos&%(等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (950008,'Coldfusion注入(OWASP TOP 10)','\\bcf(?:usion_(?:d(?:bconnections_flush|ecrypt)|set(?:tings_refresh|odbcini)|getodbc(?:dsn|ini)|verifymail|encrypt)|_(?:(?:iscoldfusiondatasourc|getdatasourceusernam)e|setdatasource(?:password|username))|newinternal(?:adminsecurit|registr)y|admin_registry_','该规则会检测用户输入中是否会出现一些未定义的Coldfusion管理函数名称，通过阻断这样的输入，来阻断可能的Coldfusion注入攻击','GENERIC','block',0,1452647413,NULL,3002,'高危','在cookies和请求参数和xml中利用cfusion_dbconnection_flush|getodbcdsn等字符串，就会存在非法输入的数据源管理函数','建议web服务器把参数名，参数值和cookies和XML中包含匹配\\bcf(?:usion_(?:d(?:bconnections_flush|ecrypt)|set(?:tings_refresh|odbcini)|getodbc(?:dsn|ini)|verifymail|encrypt)|_(?:(?:iscoldfusiondatasourc|getdatasourceusernam)e|setdatasource(?:password|username))|newinternal(?:admin','GENERIC');
INSERT INTO `t_rules` VALUES (950009,'SESSION加固(OWASP TOP 10)','(?i)(?:\\.cookie\\b.*?;\\W*?(?:expires|domain)\\W*?=|\\bhttp-equiv\\W+set-cookie\\b)','检测可能的SESSION加固攻击,通过在http请求中检测cookie;expires=;domain=;set cookie;http-equiv等来实现','GENERIC','block',0,1452647413,NULL,3014,'高危','在请求参数名字中利用如jsessionid aspsessionid asp.net_sessionid phpsession phpsessid，然后在请求头中利用Referer参数为如https://attack.com。可实施会话劫持攻击','建议web服务器把请求参数名为sessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession等单词的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950010,'LDAP注入(OWASP TOP 10)','(?:\\((?:\\W*?(?:objectc(?:ategory|lass)|homedirectory|[gu]idnumber|cn)\\b\\W*?=|[^\\w\\x80-\\xFF]*?[\\!\\&\\|][^\\w\\x80-\\xFF]*?\\()|\\)[^\\w\\x80-\\xFF]*?\\([^\\w\\x80-\\xFF]*?[\\!\\&\\|])','该规则通过查找常用的LDAP数据结构内容来达到防止LDAP注入,如：objectcategory = homedirectory =等','GENERIC','block',0,1452647413,NULL,3003,'高危','攻击者可以通过在cookies和请求参数和xml中包含了如(homedirectory=[a\\x80][&]等字符实施常见的LDAP数据注入并实施攻击','建议web服务器把参数名，参数值和cookies和XML中包含匹配(?:\\((?:\\W*?(?:objectc(?:ategory|lass)|homedirectory|[gu]idnumber|cn)\\b\\W*?=|[^\\w\\x80-\\xFF]*?[\\!\\&\\|][^\\w\\x80-\\xFF]*?\\()|\\)[^\\w\\x80-\\xFF]*?\\([^\\w\\x80-\\xFF]*?[\\!\\&\\|])正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950011,'SSI注入(OWASP TOP 10)','<!--\\W*?#\\W*?(?:e(?:cho|xec)|printenv|include|cmd)','该规则检测常见的服务器站点包含格式的数据。如：<!--#echo <!--#exec <!--#printenv <!--#include <!--#cmd','GENERIC','block',0,1452647413,NULL,3004,'高危','攻击者可以通过在cookies和请求参数和xml中包含了如<!--#echo|<!--exec<!--cmd等字符实施格式化数据输入',' 检查用户输入中，是否不包含SSI相关的危险关键字。如表达式<!--\\W*?#\\W*?(?:e(?:cho|xec)|printenv|include|cmd)','GENERIC');
INSERT INTO `t_rules` VALUES (950012,'http请求走私(OWASP TOP 10)',',','该规则探测在http头Content-Length, Transfer-Encoding中的逗号(,),比如：Content-Length: 0, 44的意思就是有两个Content-Length,一个值是0，一个是44，apache处理这样的头就好像处理多个Cookie一样','GENERIC','block',0,1452647413,NULL,3007,'高危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','http规范中规定http请求中必须包含Content-Length、Transfer-Encoding其中一个','GENERIC');
INSERT INTO `t_rules` VALUES (950018,'UPDF XSS','http:\\/\\/[\\w\\.]+?\\/.*?\\.pdf\\b[^\\x0d\\x0a]*#','该规则会寻找包含在QUERY_STRING中的＃片段内容','GENERIC','block',0,1452647413,NULL,3005,'高危','用户点击一个具有updf xss负载的链接就会形成一个正常的请求去一个网页下载pdf文件,这个基于dom的跨站负载会一直等待是在受害者的浏览器把pdf文件下载完，然后Adobe插件会在本地url的片段执行一个json脚本。','建议web服务器把参数名，参数值和cookies和XML中包含匹配http:\\/\\/[\\w\\.]+?\\/.*?\\.pdf\\b[^\\x0d\\x0a]*#)正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950019,'邮件命令注入','[\\n\\r]\\s*\\b(?:to|b?cc)\\b\\s*:.*?\\@','该规则会检测用户输入数据中的邮件命令注入,如：to:111@bluedon.cn 或 cc:111@bluedon.cn 或 bcc:111@bluedon.cn等','GENERIC','block',0,1452647413,NULL,3006,'高危','邮件服务器注射技术是通过一个对用户提供的数据没有严格检查的webmail应用程序将IMAP命令或者SMTP命令注射到邮件服务器。当通过webmail应用程序使用的后台邮件服务器无法直接经由Internet访问时，邮件服务器注射技术格外有用。','','GENERIC');
INSERT INTO `t_rules` VALUES (950020,'检测请求数据的参数及参数名称是否包含多个链接（Comment Spam）','(http:\\/.*?){4}','检测请求数据的参数及参数名称，如果一个参数包含太多链接，则阻断（Comment Spam）','OTHER','block',1,1452647413,NULL,90163,'高危','垃圾评论是一种攻击，对象是对博客、论坛、留言板等会接受并显示游客提供的超级链接的交互网页。\n这些垃圾评论制造者会专门发送一些自动的、随意的评论，并会携带一个链接到攻击者的站点，然后这些链接就会被人工的提高了在网站的搜索引擎中的排名，从而在网站的搜索结果中更加明显','建议使用第三方反垃圾系统。垃圾评论 90% 以上都是由机器人产生的，因此使用验证码也可以过滤掉大部分的垃圾评论。','OTHER');
INSERT INTO `t_rules` VALUES (950103,'检测请求数据判断是否发生路径遍历攻击（Tight Security）','(?i)(?:\\x5c|(?:%(?:2(?:5(?:2f|5c)|%46|f)|c(?:0%(?:9v|af)|1%1c)|u(?:221[56]|002f)|%32(?:%46|F)|e0%80%af|1u|5c)|\\/))(?:%(?:2(?:(?:52)?e|%45)|(?:e0%8|c)0%ae|u(?:002e|2024)|%32(?:%45|E))|\\.){2}(?:\\x5c|(?:%(?:2(?:5(?:2f|5c)|%46|f)|c(?:0%(?:9v|af)|1%1c)|u(?:221','检测请求数据判断是否发生路径遍历攻击，如果发生攻击，则阻断请求（Tight Security）','OTHER','block',1,1452647413,NULL,90049,'中危','攻击者通过目录遍历攻击可以获取系统文件及服务器的配置文件等等。一般来说，他们利用服务器API、文件标准权限进行攻击','　1、净化数据：对用户传过来的文件名参数进行硬编码或统一编码，对文件类型进行白名单控制，对包含恶意字符或者空字符的参数进行拒绝，　2、web应用程序可以使用chrooted环境包含被访问的web目录，或者使用绝对路径+参数来访问文件目录，时使其即使越权也在访问目录之内。www目录就是一个chroot应用。','OTHER');
INSERT INTO `t_rules` VALUES (950107,'URI的URL编码校验','\\%((?!$|\\W)|[0-9a-fA-F]{2}|u[0-9a-fA-F]{4})','该规则检测URI的内容是否有非URL编码的内容出现，如果有则认为可能有攻击','PROTOCOL','block',0,1395124100,NULL,4016,'中危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议对请求体的编码进行检测，如果是特殊编码，则拒绝请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (950108,'请求Body的URL编码校验','\\%((?!$|\\W)|[0-9a-fA-F]{2}|u[0-9a-fA-F]{4})','该规则当请求类型是application\\/x-www-form-urlencoded时，检测请求体的内容是否都是有效的URL编码','PROTOCOL','block',0,1395124100,NULL,4018,'中危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议对请求体的编码进行检测，如果是特殊编码，则拒绝请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (950109,'QUERY_STRING中的ARGS的URL编码校验','\\%((?!$|\\W)|[0-9a-fA-F]{2}|u[0-9a-fA-F]{4})','该规则检测请求串中的参数的内容，是否都是有效的URL编码，否则阻断','PROTOCOL','block',0,1395124100,NULL,4017,'中危','一些攻击会通过对url使用特殊编码进行绕过检测','建议在web服务器对请求中的URL的编码进行检测，不能识别的拒绝请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (950110,'通过x_key头访问后门(OWASP TOP 10)','x_(?:key|file)','该规则检测Http请求头中是否有x_key***,x_file***这样的头字段，如果存在则可能是攻击者试图访问后门程序，阻断','TROJANS','block',1,1395124100,NULL,5001,'高危','简单的后门可能只是建立一个新的账号，或者接管一个很少使用的账号;复杂的后门可能会绕过系统的安全认证而对系统有安全存取权','建议web服务器检测Http请求头中是否有x_key***,x_file***这样的头字段，如果存在则可能是攻击者试图访问后门程序','TROJANS');
INSERT INTO `t_rules` VALUES (950115,'使用AV扫描脚本或工具来检测上传文件是否包含病毒（AV Scanning）','@inspectFile /bin/runAV','使用AV扫描脚本或工具来检测上传文件是否包含病毒（AV Scanning）','OTHER','block',1,1452647413,NULL,90048,'高危','计算机病毒会感染、传播。1、攻击硬盘主引导扇区、Boot扇区、FAT表、文件目录，使磁盘上的信息丢失。 2、删除软盘、硬盘或网络上的可执行文件或数据文件，使文件丢失。 3、占用磁盘空间4、修改或破坏文件中的数据，使内容发生变化。5、抢占系统资源，使内存减少。 6、占用CPU运行时间，使运行效率降低。7、对整个磁盘或扇区进行格式化8、破坏计算机主板上BIOS内容，使计算机无法工作9、破坏屏幕正常显示，干扰用户的操作。等等','建议安装杀毒软件，对上传文件进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (950116,'禁止unicode全宽字符编码','\\%u[fF]{2}[0-9a-fA-F]{2}','该规则检测用户URI和请求体中是否有unicode全宽字符编码，如：%uffae，有的将被认为是可能的攻击，将阻断','PROTOCOL','block',0,1395124100,NULL,4020,'高危','攻击者利用扩展UNICODE全宽字符编码去替换一下特殊的字符，达到攻击的目的','建议在web服务器拒绝包含unicode全宽字符编码（如%uffae）的请求访问','PROTOCOL');
INSERT INTO `t_rules` VALUES (950117,'URL中有IP地址','^(?i)(?:ht|f)tps?:\\/\\/(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})','该规则检测URL中是否含有ip地址，来检测可能的RFI攻击','GENERIC','block',0,1452647413,NULL,3010,'高危','当参数中包含http://192.168.1.1,可以带有远程文件包含','建议web服务器把参数值中包含匹配^(?i)(?:ht|f)tps?:\\/\\/(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950118,'PHP的Include函数','(?i:(\\binclude\\s*\\([^)]*|mosConfig_absolute_path|_CONF\\[path\\]|_SERVER\\[DOCUMENT_ROOT\\]|GALLERY_BASEDIR|path\\[docroot\\]|appserv_root|config\\[root_dir\\])=(ht|f)tps?:\\/\\/)','该规则检测在http的query_string或请求体中是否有php的include()函数等,来检测可能的RFI攻击','GENERIC','block',0,1452647413,NULL,3011,'高危','在查询字符串和请求体参数中利用include ()|appserv_root|config[root_dir])=https://等字符串，可带有远程文件包含','建议web服务器把uri和请求体参数中如果含有匹配(?i:(\\binclude\\s*\\([^)]*|mosConfig_absolute_path|_CONF\\[path\\]|_SERVER\\[DOCUMENT_ROOT\\]|GALLERY_BASEDIR|path\\[docroot\\]|appserv_root|config\\[root_dir\\])=(ht|f)tps?:\\/\\/)正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950119,'以问号（？）结束RFI数据','^(?i)(?:ft|htt)ps?(.*?)\\?+$','该规则检测在http请求中，以?结束的RFI攻击数据，如：http://test.com?','GENERIC','block',0,1452647413,NULL,3012,'高危','在参数中包含如https:www.attack.com，可实施远程文件包含攻击','建议web服务器把参数值中包含匹配^(?i)(?:ft|htt)ps?(.*?)\\?+$正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950120,'RFI的主机名和web服务器的不一致','^(?:ht|f)tps?://(.*)$','当http请求中存在任何url格式的内容时，并且其中的主机和web服务器的不一致时，有可能存在RFI攻击。如http请求内容中有如下格式的东西：http://other.com','GENERIC','block',0,1452647413,NULL,3013,'高危','在参数中包含https://www.attack.com,可以远程文件包含','建议web服务器把参数值中包含匹配^(?:ht|f)tps?://(.*)$正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950801,'UTF8编码校验','@validateUtf8Encoding','当用户的网站是utf8编码的时候，该规则校验用户上传的信息是否符合Utf8编码','PROTOCOL','block',0,1395124100,NULL,4019,'高危','攻击者利用无效的UTF8编码进行攻击','建议在web服务器校验用户上传的信息是否符合Utf8编码','PROTOCOL');
INSERT INTO `t_rules` VALUES (950901,'永远为真条件表达式检测','(?i:([\\s\'\\\"`´’‘\\(\\)]*?)\\b([\\d\\w]++)([\\s\'\\\"`´’‘\\(\\)]*?)(?:(?:=|<=>|r?like|sounds\\s+like|regexp)([\\s\'\\\"`´’‘\\(\\)]*?)\\2\\b|(?:!=|<=|>=|<>|<|>|\\^|is\\s+not|not\\s+like|not\\s+regexp)([\\s\'\\\"`´’‘\\(\\)]*?)(?!\\2)([\\d\\w]+)\\b))','检测永远返回真的SQL条件语句，最常见的攻击手法如： 利用OR 1=1来返回所有记录','SQLI','block',0,1395124100,NULL,1005,'高危','在cookies和请求参数和xml中利用\\ 32342 =\\2\\\\2dcs等字符，攻击者可尝试使用永真式进行注入。一旦成功绕过防火墙，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有\\ 32342 =\\2\\\\2dcs等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (950907,'操作系统命令注入(OWASP TOP 10)','(?i:(?:[\\;\\|\\`]\\W*?\\bcc|\\b(wget|curl))\\b|\\/cc(?:[\\\'\\\"\\|\\;\\`\\-\\s]|$))','该规则会查找一些企图访问操作系统命令的尝试，比如：curl、wget、cc等，这些命令经常被攻击者用来从受害者网站向外发出网络链接来下载或编译安装恶意工具程序','GENERIC','block',0,1452647413,NULL,3001,'高危','在参数名、参数值和cookies和XML中利用wget、curl、cc之类的单词，可驱使感染的网页跟黑客建立一种连接，用于下载，编译，安装一些恶意的工具包。','建议web服务器把参数名，参数值和cookies和XML中包含匹配(?i:(?:[\\;\\|\\`]\\W*?\\bcc|\\b(wget|curl))\\b|\\/cc(?:[\\\'\\\"\\|\\;\\`\\-\\s]|$))正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950908,'SQL注入检测之六','(?i:\\b(?:coalesce\\b|root\\@))','SQL注入检测','SQLI','block',0,1395124100,NULL,1029,'高危','当cookies和请求参数和xml和请求头中出现如 coalesce|root@等字符时候，攻击者可尝试SQL注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有coalesce|root@等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (950910,'http响应分片(逗号的检测)','[\\n\\r](?:content-(type|length)|set-cookie|location):','该规则在http头中探测头中或cookie中的字段内容是否有：content-type: content-length: set-cookie: location:等，来防止用户来将自己输入的内容直接在应答中返回，达到http响应分片的目的','GENERIC','block',0,1452647413,NULL,3008,'高危','','','GENERIC');
INSERT INTO `t_rules` VALUES (950911,'http响应分片(可能出现的分片内容检测)','(?:\\bhttp\\/(?:0\\.9|1\\.[01])|<(?:html|meta)\\b)','该规则检测在http头或cookie中的字段内容是否含有：http/0.9 http/1.0 http/1.1 或者 <html <meta等，来检测可能的http响应分片攻击','GENERIC','block',0,1452647413,NULL,3009,'高危','寻找回车(CR)和换行(LF)字符如果在响应头和返回的数据中出现，可能会被代理服务器和视为两个独立的应答。','建议web服务器把参数名，参数值和cookies和XML中包含匹配(?:\\bhttp\\/(?:0\\.9|1\\.[01])|<(?:html|meta)\\b)正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (950921,'访问root.exe后门程序(OWASP TOP 10)','root\\.exe','该规则检测uri请求中的文件名，如果访问root.exe文件，则阻断','TROJANS','block',1,1395124100,NULL,5002,'高危','后门程序是隐藏在用户系统中向外发送信息,而且本身具有一定权限,以便远程机器对本机的控制','建议web服务器禁止访问root.exe后门程序','TROJANS');
INSERT INTO `t_rules` VALUES (950922,'通过响应判断后门反问(OWASP TOP 10)','(?:<title>[^<]*?(?:\\b(?:(?:c(?:ehennemden|gi-telnet)|gamma web shell)\\b|imhabirligi phpftp)|(?:r(?:emote explorer|57shell)|aventis klasvayv|zehir)\\b|\\.::(?:news remote php shell injection::\\.| rhtools\\b)|ph(?:p(?:(?: commander|-terminal)\\b|remoteview)|vay','该规则检测web应用程序给用户返回的响应，如果响应中含有：remote explorer,r57shell,gamma web shell, php commander,myshell,php konsole,c99shell等,如有则可能是后门访问的响应，阻断','TROJANS','block',1,1395124100,NULL,5003,'高危','简单的后门可能只是建立一个新的账号，或者接管一个很少使用的账号;复杂的后门可能会绕过系统的安全认证而对系统有安全存取权','建议web服务器不要返回含有：remote explorer,r57shell,gamma web shell, php commander,myshell,php konsole,c99shell等字符的响应消息','TROJANS');
INSERT INTO `t_rules` VALUES (950923,'检测请求数据的参数及参数名称是否在一个POST链接中包含2个请求方法（Comment Spam）','\\[url\\b','如果在一个POST链接中包含2个请求方法，则阻断请求（Comment Spam）','OTHER','block',1,1452647413,NULL,90157,'高危','垃圾评论是一种攻击，对象是对博客、论坛、留言板等会接受并显示游客提供的超级链接的交互网页。\n这些垃圾评论制造者会专门发送一些自动的、随意的评论，并会携带一个链接到攻击者的站点，然后这些链接就会被人工的提高了在网站的搜索引擎中的排名，从而在网站的搜索结果中更加明显','建议使用第三方反垃圾系统。垃圾评论 90% 以上都是由机器人产生的，因此使用验证码也可以过滤掉大部分的垃圾评论。','OTHER');
INSERT INTO `t_rules` VALUES (958000,'检测.addImport(OWASP TOP 10)','\\.addimport\\b',' 检测请求数据中的.addImport关键词','XSS','block',0,1395124100,NULL,8042,'高危','当cookies或请求参数或xml中出现如.addimport等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有.addimport等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958001,'检测document.cookie(OWASP TOP 10)','\\bdocument\\b\\s*\\.\\s*\\bcookie\\b',' 检测请求数据中的document.cookie关键词','XSS','block',0,1395124100,NULL,8034,'高危','','','XSS');
INSERT INTO `t_rules` VALUES (958002,'检测.execscript(OWASP TOP 10)','\\.execscript\\b',' 检测请求数据中的.execscript关键词','XSS','block',0,1395124100,NULL,8018,'高危','当cookies或请求参数或xml中出现如.execscript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有.execscript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958003,'检测.fromcharcode(OWASP TOP 10)','\\.fromcharcode\\b',' 检测请求数据中的.fromcharcode关键词','XSS','block',0,1395124100,NULL,8071,'高危','当cookies或请求参数或xml中出现如.fromcharcode等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有.fromcharcode等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958004,'检测.innerhtml(OWASP TOP 10)','\\.innerhtml\\b',' 检测请求数据中的.innerhtml关键词','XSS','block',0,1395124100,NULL,8057,'高危','当cookies或请求参数或xml中出现如.innerhtml等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有.innerhtml等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958005,'检测<![cdata[(OWASP TOP 10)','\\<\\!\\[cdata\\[',' 检测请求数据中的<![cdata[关键词','XSS','block',0,1395124100,NULL,8035,'高危','当cookies或请求参数或xml中出现如<![cdata[等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<![cdata[等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958006,'检测body标签的background(OWASP TOP 10)','<body\\b.*?\\bbackground\\b',' 检测body标签的background','XSS','block',0,1395124100,NULL,8030,'高危','当cookies或请求参数或xml中出现如<body background等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<body background等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958007,'检测boby标签的中的onload(OWASP TOP 10)','<body\\b.*?\\bonload\\b',' 检测请求数据boby标签的中的onload关键词','XSS','block',0,1395124100,NULL,8020,'高危','当cookies或请求参数或xml中出现如<body onload等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<body onload等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958008,'检测input中的type是否包含image(OWASP TOP 10)','<input\\b.*?\\btype\\b\\W*?\\bimage\\b',' 检测input中的type是否包含image','XSS','block',0,1395124100,NULL,8068,'高危','当cookies或请求参数或xml中出现如<input type$image等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<input type$image等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958009,'检测@import(OWASP TOP 10)','\\@import\\b',' 检测请求数据中的@import关键词','XSS','block',0,1395124100,NULL,8059,'高危','当cookies或请求参数或xml中出现如@import等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有@import等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958010,'检测activexobject(OWASP TOP 10)','\\bactivexobject\\b',' 检测请求数据中的activexobject关键词','XSS','block',0,1395124100,NULL,8038,'高危','当cookies或请求参数或xml中出现如activexobject等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有activexobject等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958011,'检测background-image(OWASP TOP 10)','\\bbackground-image:',' 检测请求数据中的background-image关键词','XSS','block',0,1395124100,NULL,8066,'高危','当cookies或请求参数或xml中出现如background-image:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有background-image:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958012,'检测copyparentfolder(OWASP TOP 10)','\\bcopyparentfolder\\b',' 检测请求数据中的copyparentfolder关键词','XSS','block',0,1395124100,NULL,8016,'高危','当cookies或请求参数或xml中出现如copyparentfolder等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有copyparentfolder等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958013,'检测createtextrange(OWASP TOP 10)','\\bcreatetextrange\\b',' 检测请求数据中的createtextrange关键词','XSS','block',0,1395124100,NULL,8014,'高危','当cookies或请求参数或xml中出现如createtextrange等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有createtextrange等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958016,'检测getparentfolder(OWASP TOP 10)','\\bgetparentfolder\\b',' 检测请求数据中的getparentfolder关键词，包括请求参数和cookie','XSS','block',0,1395124100,NULL,8005,'高危','当cookies或请求参数或xml中出现如getparentfolder等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有getspecialfolder等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958017,'检测getspecialfolder(OWASP TOP 10)','\\bgetspecialfolder\\b',' 检测请求数据中的getspecialfolder关键词','XSS','block',0,1395124100,NULL,8019,'高危','当cookies或请求参数或xml中出现如getspecialfolder等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有getspecialfolder等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958018,'检测href是否包含javascript代码(OWASP TOP 10)','\\bhref\\b\\W*?\\bjavascript:',' 检测href是否包含javascript代码','XSS','block',0,1395124100,NULL,8043,'高危','当cookies或请求参数或xml中出现如href &javascript:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有href &javascript:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958019,'检测href中中是否包含shell代码(OWASP TOP 10)','\\bhref\\b\\W*?\\bshell:','','XSS','block',0,1395124100,NULL,8013,'高危','当cookies或请求参数或xml中出现如href$shell:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有href$shell:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958020,'检测href中是否包含vbscript代码(OWASP TOP 10)','\\bhref\\b\\W*?\\bvbscript:',' 检测href中是否包含vbscript代码','XSS','block',0,1395124100,NULL,8055,'高危','当cookies或请求参数或xml中出现如href%vbscript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有href%vbscript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958022,'检测livescript(OWASP TOP 10)','\\blivescript:',' 检测请求数据中的livescript关键词','XSS','block',0,1395124100,NULL,8024,'高危','当cookies或请求参数或xml中出现如livescript:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有livescript:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958023,'检测lowsrc中是否包含javascript代码(OWASP TOP 10)','\\blowsrc\\b\\W*?\\bjavascript:',' 检测lowsrc中是否包含javascript代码','XSS','block',0,1395124100,NULL,8037,'高危','当cookies或请求参数或xml中出现如lowsrc &javascript:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有lowsrc &javascript:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958024,'检测src是否包含shell代码(OWASP TOP 10)','\\blowsrc\\b\\W*?\\bshell:',' 检测src是否包含shell代码','XSS','block',0,1395124100,NULL,8052,'高危','','','XSS');
INSERT INTO `t_rules` VALUES (958025,'检测lowsrc中是否包含vbscript代码(OWASP TOP 10)','\\blowsrc\\b\\W*?\\bvbscript:',' 检测lowsrc中是否包含vbscript代码','XSS','block',0,1395124100,NULL,8060,'高危','当cookies或请求参数或xml中出现如lowsrc#vbscript:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有lowsrc#vbscript:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958026,'检测mocha(OWASP TOP 10)','\\bmocha:',' 检测请求数据中的mocha:关键词','XSS','block',0,1395124100,NULL,8008,'高危','当cookies或请求参数或xml中出现如<attack:vmlframe+src+=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<attack:vmlframe+src+=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958027,'检测onabort(OWASP TOP 10)','\\bonabort\\b',' 检测请求数据中的onabort关键词','XSS','block',0,1395124100,NULL,8009,'高危','当cookies或请求参数或xml中出现如onabort等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onabort等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958028,'检测settimeout(OWASP TOP 10)','\\bsettimeout\\b\\W*?\\(',' 检测请求数据中的settimeout关键词','XSS','block',0,1395124100,NULL,8027,'高危','当cookies或请求参数或xml中出现如settimeout%(等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有settimeout%(等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958030,'检测src中是否是http(OWASP TOP 10)','\\bsrc\\b\\W*?\\bhttp:',' 检测src中是否是http','XSS','block',0,1395124100,NULL,8049,'高危','当cookies或请求参数或xml中出现如src http:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有src http:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958031,'检测src中是否包含javascript代码(OWASP TOP 10)','\\bsrc\\b\\W*?\\bjavascript:',' 检测src中是否包含javascript代码','XSS','block',0,1395124100,NULL,8029,'高危','当cookies或请求参数或xml中出现如src&javascript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有src&javascript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958032,'检测src shell:(OWASP TOP 10)','\\bsrc\\b\\W*?\\bshell:',' 检测请求数据中的src shell:关键词','XSS','block',0,1395124100,NULL,8007,'高危','当cookies或请求参数或xml中出现如src$shell：等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有src$shell：等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958033,'检测src中是否包含vbscript代码(OWASP TOP 10)','\\bsrc\\b\\W*?\\bvbscript:',' 检测src中是否包含vbscript代码','XSS','block',0,1395124100,NULL,8031,'高危','当cookies或请求参数或xml中出现如src#vbscript:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有src#vbscript:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958034,'检测css expression(expression可以包含js代码, )(OWASP TOP 10)','\\bstyle\\b\\W*\\=.*bexpression\\b\\W*\\(','expression可以包含js代码','XSS','block',0,1395124100,NULL,8012,'高危','当cookies或请求参数或xml中出现如style#=expression@(等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有style#=expression@(等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958036,'检测type中application是否包含x-javascript代码(OWASP TOP 10)','\\btype\\b\\W*?\\bapplication\\b\\W*?\\bx-javascript\\b',' 检测type中application是否包含x-javascript代码','XSS','block',0,1395124100,NULL,8041,'高危','当cookies或请求参数或xml中出现如type#application%x-javascript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有type#application%x-javascript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958037,'检测type中的application是否包含vbscript代码(OWASP TOP 10)','\\btype\\b\\W*?\\bapplication\\b\\W*?\\bx-vbscript\\b',' 检测type中的application是否包含vbscript代码','XSS','block',0,1395124100,NULL,8047,'高危','当cookies或请求参数或xml中出现如type@application%bx-vbscript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有type@application%bx-vbscript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958038,'检测type中text中是否包含ecmascript代码(OWASP TOP 10)','\\btype\\b\\W*?\\btext\\b\\W*?\\becmascript\\b',' 检测type中text中是否包含ecmascript代码','XSS','block',0,1395124100,NULL,8032,'高危','当cookies或请求参数或xml中出现如type#text%ecmascript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有type#text%ecmascript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958039,'检测type中的text是否包含javascript代码(OWASP TOP 10)','\\btype\\b\\W*?\\btext\\b\\W*?\\bjavascript\\b',' 检测type中的text是否包含javascript代码','XSS','block',0,1395124100,NULL,8070,'高危','当cookies或请求参数或xml中出现如type $text $javascript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有type $text $javascript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958040,'检测type的text中是否包含javascript代码(OWASP TOP 10)','\\btype\\b\\W*?\\btext\\b\\W*?\\bjscript\\b',' 检测type的text中是否包含javascript代码','XSS','block',0,1395124100,NULL,8045,'高危','当cookies或请求参数或xml中出现如type%text#jscript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有type%text#jscript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958041,'检测type中的text是否包含vbscript代码(OWASP TOP 10)','\\btype\\b\\W*?\\btext\\b\\W*?\\bvbscript\\b',' 检测type中的text是否包含vbscript代码','XSS','block',0,1395124100,NULL,8050,'高危','当cookies或请求参数或xml中出现如type$text#vbscript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有type$text#vbscript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958045,'检测url中是否包含javascript代码(OWASP TOP 10)','\\burl\\b\\W*?\\bjavascript:',' 检测url中是否包含javascript代码','XSS','block',0,1395124100,NULL,8056,'高危','当cookies或请求参数或xml中出现如url#javascript:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有url#javascript:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958046,'检测url中是否包含shell代码(OWASP TOP 10)','\\burl\\b\\W*?\\bshell:',' 检测url中是否包含shell代码','XSS','block',0,1395124100,NULL,8069,'高危','当cookies或请求参数或xml中出现如url$shell:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有url$shell:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958047,'检测url中是否包含vbscript代码(OWASP TOP 10)','\\burl\\b\\W*?\\bvbscript:','','XSS','block',0,1395124100,NULL,8021,'高危','当cookies或请求参数或xml中出现如url$vbscript:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有url$vbscript:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958049,'检测meta(OWASP TOP 10)','\\< ?meta\\b',' 检测请求数据中的meta关键词','XSS','block',0,1395124100,NULL,8048,'高危','当cookies或请求参数或xml中出现如<meta等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<meta等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958051,'检测script标签的开始(OWASP TOP 10)','\\< ?script\\b',' 检测请求数据中的<script关键词','XSS','block',0,1395124100,NULL,8062,'高危','当cookies或请求参数或xml中出现如alert %(等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有alert %(等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958052,'检测alert(OWASP TOP 10)','\\balert\\b\\W*?\\(',' 检测请求数据中的alert关键词','XSS','block',0,1395124100,NULL,8046,'高危','当cookies或请求参数或xml中出现如alert$(等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有alert$等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958054,'检测lowsrc http:(OWASP TOP 10)','\\blowsrc\\b\\W*?\\bhttp:',' 检测请求数据中的lowsrc http:关键词','XSS','block',0,1395124100,NULL,8010,'高危','当cookies或请求参数或xml中出现如lowsrc #http:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有lowsrc #http:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958056,'检测iframe中的src(OWASP TOP 10)','\\biframe\\b.{0,100}?\\bsrc\\b',' 检测iframe中的src','XSS','block',0,1395124100,NULL,8065,'高危','当cookies或请求参数或xml中出现如iframe src等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有iframe src等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958057,'检测iframe(OWASP TOP 10)','\\< ?iframe',' 检测请求数据中的iframe关键词','XSS','block',0,1395124100,NULL,8028,'高危','当cookies或请求参数或xml中出现如< iframe等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有< iframe等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958059,'检测asfunction(OWASP TOP 10)','\\basfunction:',' 检测请求数据中的asfunction关键词','XSS','block',0,1395124100,NULL,8053,'高危','当cookies或请求参数或xml中出现如asfunction:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有asfunction:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958230,'Range、Request-Range内容后字节要大于前字节','(\\d+)\\-(\\d+)\\,','该规则检测Range或Request-Range的内容是否接受字节大于起始字节,如：Range:bytes=455-255,这样的内容将会被阻断','PROTOCOL','block',0,1395124100,NULL,4013,'中危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议web服务器拒绝请求包中Range、Request-Range内容后字节要大于前字节的请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (958231,'Range、Request-Range定义子字节范围过多','^bytes=(\\d+)?\\-(\\d+)?\\,\\s?(\\d+)?\\-(\\d+)?\\,\\s?(\\d+)?\\-(\\d+)?\\,\\s?(\\d+)?\\-(\\d+)?\\,\\s?(\\d+)?\\-(\\d+)?\\,','该规则检测Range或Request-Range中定义的以逗号分割的子字节范围是否过多,如：Range:bytes=500-600,601-999,一般子范围不超过5个','PROTOCOL','block',0,1395124100,NULL,4014,'中危','自动程序和机器人进行大量访问，造成网站崩溃','建议拒绝Range、Request-Range字段中定义子字节范围过多的请求，一般不超过5个','PROTOCOL');
INSERT INTO `t_rules` VALUES (958291,'Range的字节范围不能从0开始','@beginsWith bytes=0-','该规则探测HTTP请求头中的Range字段的内容是否是以0开始的，比如Range:bytes=0-，一般浏览器都不会这么做，但很多机器人或爬虫程序可能会违背RFC这么干','PROTOCOL','block',0,1395124100,NULL,4012,'中危','自动程序和机器人进行大量访问，造成网站崩溃','建议web服务器拒绝请求头中Range字段的字节范围从0开始的请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (958295,'Connection中不能有冲突的内容','\\b(keep-alive|close),\\s?(keep-alive|close)\\b','该规则检测Connection中是的内容是否冲突，如：keep-alive,close并存将被阻断','PROTOCOL','block',0,1395124100,NULL,4015,'中危','Broken/Malicous经常会有重复或冲突的Connection, 自动程序或机器人通常不遵守http RFC规范','建议检测请求中的Connection字段keep-alive,close是否并存，是则拒绝请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (958297,'检测请求头中User-Agent字段内容（Comment Spam）','^(?:m(?:o(?:zilla\\/4\\.0\\+?\\(|vable type)|i(?:crosoft url|ssigua)|j12bot\\/v1\\.0\\.8|sie)|e(?:mail(?:collector| ?siphon)|collector)|(?:blogsearchbot-marti|super happy fu)n|i(?:nternet explorer|sc systems irc)|ja(?:karta commons|va(?:\\/| )1\\.)|c(?:ore-project','如果请求头中的User-Agent字段内容来自modsecurity_42_comment_spam.data文件中，则判断为垃圾评论内容，返回错误状态码404（Comment Spam）','OTHER','block',1,1452647413,NULL,90165,'高危','垃圾评论是一种攻击，对象是对博客、论坛、留言板等会接受并显示游客提供的超级链接的交互网页。\n这些垃圾评论制造者会专门发送一些自动的、随意的评论，并会携带一个链接到攻击者的站点，然后这些链接就会被人工的提高了在网站的搜索引擎中的排名，从而在网站的搜索结果中更加明显','建议使用第三方反垃圾系统。垃圾评论 90% 以上都是由机器人产生的，因此使用验证码也可以过滤掉大部分的垃圾评论。','OTHER');
INSERT INTO `t_rules` VALUES (958404,'检测onerror(OWASP TOP 10)','\\bonerror\\b\\W*?\\=',' 检测请求数据中的onerror关键词','XSS','block',0,1395124100,NULL,8036,'高危','当cookies或请求参数或xml中出现如onerror$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onerror$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958405,'检测onblur(OWASP TOP 10)','\\bonblur\\b\\W*?\\=',' 检测请求数据中的onblur关键词','XSS','block',0,1395124100,NULL,8025,'高危','当cookies或请求参数或xml中出现如onblur$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onblur$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958406,'检测onchange(OWASP TOP 10)','\\bonchange\\b\\W*?\\=',' 检测请求数据中的onchange关键词','XSS','block',0,1395124100,NULL,8044,'高危','当cookies或请求参数或xml中出现如onchange%=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有nchange%=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958407,'检测onclick(OWASP TOP 10)','\\bonclick\\b\\W*?\\=',' 检测请求数据中的onclick关键词','XSS','block',0,1395124100,NULL,8064,'高危','当cookies或请求参数或xml中出现如onclick&=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onclick&=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958408,'检测ondragdrop(OWASP TOP 10)','\\bondragdrop\\b\\W*?\\=',' 检测请求数据中的ondragdrop关键词','XSS','block',0,1395124100,NULL,8015,'高危','当cookies或请求参数或xml中出现如ondragdrop等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有ondragdrop等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958409,'检测onfocus(OWASP TOP 10)','\\bonfocus\\b\\W*?\\=',' 检测请求数据中的onfocus关键词','XSS','block',0,1395124100,NULL,8033,'高危','当cookies或请求参数或xml中出现如onfocus&=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onfocus&=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958410,'检测onkeydown(OWASP TOP 10)','\\bonkeydown\\b\\W*?\\=',' 检测请求数据中的onkeydown关键词','XSS','block',0,1395124100,NULL,8022,'高危','当cookies或请求参数或xml中出现如onkeydown$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onkeydown$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958411,'检测onkeypress(OWASP TOP 10)','\\bonkeypress\\b\\W*?\\=',' 检测请求数据中的onkeypress关键词','XSS','block',0,1395124100,NULL,8039,'高危','当cookies或请求参数或xml中出现如onkeypress$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onkeypress$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958412,'检测onkeyup(OWASP TOP 10)','\\bonkeyup\\b\\W*?\\=',' 检测请求数据中的onkeyup关键词','XSS','block',0,1395124100,NULL,8067,'高危','当cookies或请求参数或xml中出现如onkeyup&=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onkeyup&=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958413,'检测onload(OWASP TOP 10)','\\bonload\\b\\W*?\\=',' 检测请求数据中的onload关键词','XSS','block',0,1395124100,NULL,8061,'高危','当cookies或请求参数或xml中出现如onload#=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onload#=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958414,'检测onmousedown(OWASP TOP 10)','\\bonmousedown\\b\\W*?\\=',' 检测请求数据中的onmousedown关键词','XSS','block',0,1395124100,NULL,8006,'高危','当cookies或请求参数或xml中出现如onmousedown$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onmousedown$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958415,'检测onmousemove(OWASP TOP 10)','\\bonmousemove\\b\\W*?\\=',' 检测请求数据中的onmousemove关键词','XSS','block',0,1395124100,NULL,8023,'高危','当cookies或请求参数或xml中出现如onmousemove$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onmousemove$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958416,'检测onmouseout(OWASP TOP 10)','\\bonmouseout\\b\\W*?\\=',' 检测请求数据中的onmouseout关键词','XSS','block',0,1395124100,NULL,8051,'高危','当cookies或请求参数或xml中出现如onmouseout%=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onmouseout%=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958417,'检测onmouseover(OWASP TOP 10)','\\bonmouseover\\b\\W*?\\=',' 检测请求数据中的onmouseover关键词','XSS','block',0,1395124100,NULL,8054,'高危','当cookies或请求参数或xml中出现如onmouseover#=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onmouseover#=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958418,'检测onmouseup(OWASP TOP 10)','\\bonmouseup\\b\\W*?\\=',' 检测请求数据中的onmouseup关键词','XSS','block',0,1395124100,NULL,8011,'高危','当cookies或请求参数或xml中出现如onmouseup$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onmouseup$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958419,'检测onmove(OWASP TOP 10)','\\bonmove\\b\\W*?\\=',' 检测请求数据中的onmove关键词','XSS','block',0,1395124100,NULL,8026,'高危','当cookies或请求参数或xml中出现如onmove$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onmove$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958420,'检测onresize(OWASP TOP 10)','\\bonresize\\b\\W*?\\=',' 检测请求数据中的onresize关键词','XSS','block',0,1395124100,NULL,8063,'高危','当cookies或请求参数或xml中出现如onresize#=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onresize#=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958421,'检测onselect(OWASP TOP 10)','\\bonselect\\b\\W*?\\=',' 检测请求数据中的onselect关键词','XSS','block',0,1395124100,NULL,8058,'高危','当cookies或请求参数或xml中出现如onselect@=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onselect@=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958422,'检测onsubmit(OWASP TOP 10)','\\bonsubmit\\b\\W*?\\=',' 检测请求数据中的onsubmit关键词','XSS','block',0,1395124100,NULL,8040,'高危','当cookies或请求参数或xml中出现如onsubmit$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onsubmit$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958423,'检测onunload(OWASP TOP 10)','\\bonunload\\b\\W*?\\=',' 检测请求数据中的onunload关键词','XSS','block',0,1395124100,NULL,8017,'高危','当cookies或请求参数或xml中出现如onunload$=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有onunload$=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (958976,'在PHP中注入其他PHP代码(OWASP TOP 10)','(?i)(?:\\b(?:f(?:tp_(?:nb_)?f?(?:ge|pu)t|get(?:s?s|c)|scanf|write|open|read)|gz(?:(?:encod|writ)e|compress|open|read)|s(?:ession_start|candir)|read(?:(?:gz)?file|dir)|move_uploaded_file|(?:proc_|bz)open|call_user_func)|\\$_(?:(?:pos|ge)t|session))\\b','该规则检测尝试在http请求中输入php代码尝试注入到php中：$_post $_get $_session gzopen gzcompress session_start scandir','GENERIC','block',0,1452647413,NULL,3021,'高危','在cookies和请求参数和xml中利用ftp_nbfget|$_post|$_session等字符串，很有可能是受到了PHP注入攻击','建议web服务器把参数名，参数值和cookies和XML中包含匹配(?:\\b(?:f(?:tp_(?:nb_)?f?(?:ge|pu)t|get(?:s?s|c)|scanf|write|open|read)|gz(?:(?:encod|writ)e|compress|open|read)|s(?:ession_start|candir)|read(?:(?:gz)?file|dir)|move_uploaded_file|(?:proc_|bz)open|call_user_func)|\\$_(?:(?','GENERIC');
INSERT INTO `t_rules` VALUES (958977,'PHP注入攻击(OWASP TOP 10)','allow_url_include= safe_mode= suhosin.simulation= disable_functions= open_basedir= auto_prepend_file= php://input','该规则在http请求数据中检测以下关键词：allow_url_include= safe_mode= suhosin.simulation= disable_functions= open_basedir= auto_prepend_file= php://input','GENERIC','block',0,1452647413,NULL,3022,'高危','在查询字符串中借助allow_url_include= safe_mode= suhosin.simulation= disable_functions= open_basedir= auto_prepend_file= php://input等参数可实施PHP注入攻击','建议web服务器把含有allow_url_include= safe_mode= suhosin.simulation= disable_functions= open_basedir= auto_prepend_file= php://input等关键词的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (959070,'SQL注入检测之二(OWASP TOP 10)','\\b(?i:having)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')\\s*?[=<>]|(?i:\\bexecute(\\s{1,5}[\\w\\.$]{1,5}\\s{0,3})?\\()|\\bhaving\\b ?(?:\\d{1,10}|[\\\'\\\"][^=]{1,10}[\\\'\\\"]) ?[=<>]+|(?i:\\bcreate\\s+?table.{0,20}?\\()|(?i:\\blike\\W*?char\\W*?\\()|(?i:(?:(select(.*?)case|from(.*?)limit|orde','OWASP排名前10的SQL注入检测','SQLI','block',0,1395124100,NULL,1025,'高危','在cookies和请求参数和xml中利用 having  1234567|^^== =|execute    abc   (|exists select |selectatop等字符，攻击者可尝试SQL注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有 having  1234567|^^== =|execute    abc   (|exists select |selectatop等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (959071,'SQL注入检测之三(OWASP TOP 10)','(?i:\\bor\\b ?(?:\\d{1,10}|[\\\'\\\"][^=]{1,10}[\\\'\\\"]) ?[=<>]+|(?i:\'\\s+x?or\\s+.{1,20}[+\\-!<>=])|\\b(?i:x?or)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')|\\b(?i:x?or)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')\\s*?[=<>])','OWASP排名前10的SQL注入检测','SQLI','block',0,1395124100,NULL,1026,'高危','在cookies和请求参数和xml中利用 or 123434|\"+123abc\"=|xor   1234等字符，攻击者可尝试SQL注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有or 123434|\"+123abc\"=|xor   1234等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (959072,'SQL注入检测之四(OWASP TOP 10)','(?i)\\b(?i:and)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')\\s*?[=]|\\b(?i:and)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')\\s*?[<>]|\\band\\b ?(?:\\d{1,10}|[\\\'\\\"][^=]{1,10}[\\\'\\\"]) ?[=<>]+|\\b(?i:and)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')','OWASP排名前10的SQL注入检测','SQLI','block',0,1395124100,NULL,1027,'高危','在cookies和请求参数和xml中利用 and   12345|and 12344|^==^^|^^=   <等字符，攻击者可尝试SQL注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有 nd   12345|and 12344|^==^^|^^=   <等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (959073,'SQL注入检测之五(OWASP TOP 10)','(?i:(?:(?:s(?:t(?:d(?:dev(_pop|_samp)?)?|r(?:_to_date|cmp))|u(?:b(?:str(?:ing(_index)?)?|(?:dat|tim)e)|m)|e(?:c(?:_to_time|ond)|ssion_user)|ys(?:tem_user|date)|ha(1|2)?|oundex|chema|ig?n|pace|qrt)|i(?:s(null|_(free_lock|ipv4_compat|ipv4_mapped|ipv4|ipv6|n','OWASP排名前10的SQL注入检测','SQLI','block',0,1395124100,NULL,1028,'高危','在cookies和请求参数和xml中利用 stddev_samp|r_to_date|rcmp|ubstring_index|tractvalue|ncrypt等字符，攻击者可尝试SQL注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有stddev_samp|r_to_date|rcmp|ubstring_index|tractvalue|ncrypt等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (959151,'在PHP中注入XML的攻击(OWASP TOP 10)','<\\?(?!xml)','该规则检测尝试在php代码中注入xml代码的尝试：<?xml','GENERIC','block',0,1452647413,NULL,3020,'高危','在cookies和请求参数和xml中利用<\\(?!xml)等字符串，可实施php注入攻击','建议web服务器把参数名，参数值和cookies和XML中包含匹配<\\?(?!xml)正则表达式的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (960000,'多样化数据企图绕过检测(Protocol Violations)','[\'\\\";=]','检测文件或文件名是否包含有\' ;=meta-characters，若有该字符，则阻断访问(Protocol Violations)','PROTOCOL','block',0,1452647413,NULL,90115,'中危','如果攻击者上传文件的时候尝试绕过multipart/form-data，上传的文件的名字或者数据中会包含了\'\\\";=等字符。','建议web服务器对请求包进行检测，对于上传的文件的名字或者数据中包含了\'\\\";=等字符的请求拒绝访问。','PROTOCOL');
INSERT INTO `t_rules` VALUES (960001,'检测请求内容是否违反CSP（内容安全策略）（CSP Enforcement）','({\\\"csp-report\\\":.*blocked-uri\\\":\\\"(.*?)\\\".*violated-directive\\\":\\\"(.*)\\\")','检测请求体中的内容来判断是否违反CSP（内容安全策略）（CSP Enforcement）','OTHER','block',1,1452647413,NULL,90011,'高危','把CSP发送到服务器中的违规报告中请求体中的相关数据内容记录日志下来。','','OTHER');
INSERT INTO `t_rules` VALUES (960002,'检测请求是否来自FireFox浏览器（仅记录模式）（CSP Enforcement）','?i:mozilla.*firefox','根据请求头的User-Agent字段内容检测到该请求来自FireFox浏览器用户，则设置环境参数来通知Apache用哪个CSP头策略（仅记录模式）（CSP Enforcement）','OTHER','block',1,1452647413,NULL,90012,'高危','检测user-agent头，如果检测到时火狐的用户的话，服务器会根据CSP请求头写明的策略相对应的应答。','','OTHER');
INSERT INTO `t_rules` VALUES (960003,'检测请求是否来自FireFox浏览器（CSP Enforcement）','?i:mozilla.*firefox','根据请求头的User-Agent字段内容检测到该请求来自FireFox浏览器用户，则设置环境参数来通知Apache用哪个CSP头策略（CSP Enforcement）','OTHER','block',1,1452647413,NULL,90009,'高危','检测user-agent头，如果检测到时火狐的用户的话，服务器会根据CSP请求头写明的策略相对应的应答。','','OTHER');
INSERT INTO `t_rules` VALUES (960006,'请求头中的User-Agent的内容为空','^$','该规则检测http请求头中的User-Agent字段的内容是否为空，为空则阻断','PROTOCOL','block',1,1395124100,NULL,4506,'低危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议web服务器对请求包进行检测，对于User-Agent头内容为空的请求拒绝访问。','PROTOCOL');
INSERT INTO `t_rules` VALUES (960007,'请求头中Host内容为空','^$','该规则检测请求头中Host的内容是否未空，为空则阻断','PROTOCOL','block',1,1395124100,NULL,4502,'中危','请求中host的内容不能为空。','建议web服务器对请求包进行检测，对于host的内容为空的请求拒绝访问。','PROTOCOL');
INSERT INTO `t_rules` VALUES (960008,'请求头中缺少Host(OWASP TOP 10)','@eq 0','该规则检测用户上传的请求头中是否缺少Host字段，如果缺少，则阻断','PROTOCOL','block',1,1395124100,NULL,4501,'中危','请求中host的内容不能缺少。','建议web服务器对请求包进行检测，对于host的内容缺少的请求拒绝访问。','PROTOCOL');
INSERT INTO `t_rules` VALUES (960009,'请求头中缺少User-Agent头(OWASP TOP 10)','@eq 0','该规则检测http请求头中是否缺少User-Agent，如缺少将阻断','PROTOCOL','block',1,1395124100,NULL,4505,'低危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议web服务器对请求包进行检测，对于缺少User-Agent头的请求拒绝访问。','PROTOCOL');
INSERT INTO `t_rules` VALUES (960010,'检测请求方法及请求内容类型来判断是否符合http策略（Http Policy）','REQUEST_METHOD \"!^(?:GET|HEAD|PROPFIND|OPTIONS)$\"  REQUEST_HEADERS:Content-Type \"^([^;\\s]+)\"','如果请求方法及请求内容类型来判断不符合http策略，则阻断访问（Http Policy）','OTHER','block',1,1452647413,NULL,90088,'高危','当不明格式类型的请求发送到服务器，攻击者会在GET/HEAD/OPTION/PROPFIND等请求方式以外的请求中，不带有content type或者没有内容。','建议拒绝不明格式类型的请求的访问','OTHER');
INSERT INTO `t_rules` VALUES (960011,'Get或Head请求不能有请求体','^(?:GET|HEAD)$','按标准规范Get或Head请求可以有请求体，但在实际环境中很少使用这个特性，因为黑客可能利用该特性发送一些请求体到一些不知情的web应用程序，来达到攻击目的','PROTOCOL','block',0,1395124100,NULL,4007,'中危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议对get或head请求进行检测，是否有请求体，有则拒绝请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (960012,'Post请求都要求有Content-Length字段','^POST$','该规则检测到如果请求是Post，则要求在请求头中必须有Content-Length字段的内容','PROTOCOL','block',0,1395124100,NULL,4008,'中危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议对post请求进行检测，是否有Content-Length字段，没有则拒绝请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (960015,'请求头中缺少Accept(OWASP TOP 10)','@eq 0','该规则检测用户上传的请求头，看是否缺少Accetp头，当动作为非OPTIONS，而又缺少Accept头时将阻断','PROTOCOL','block',1,1395124100,NULL,4503,'低危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议web服务器拒绝请求头中缺少Accept的请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (960016,'Content-Length的内容只能数字','!^\\d+$','该规则检测http请求头中Content-Length字段的内容是否是数字，按RFC的要求必须是数字','PROTOCOL','block',0,1395124100,NULL,4006,'高危','请求的content length的内容只能是数字。','建议web服务器对content length字段的内容进行检测，出现数字以外的内容则拒绝访问','PROTOCOL');
INSERT INTO `t_rules` VALUES (960017,'Host的内容是IP地址(OWASP TOP 10)','^[\\d.:]+$','该规则检测Host的内容是否是数字和.组成的IP地址，或者再带上端口号，如：1.1.1.1：80,是则阻断，因为很多网络蠕虫或自动化程序都是通过IP段扫描来传播的','PROTOCOL','block',1,1395124100,NULL,4508,'中危','自动化大量的无效请求访问网站，使网站崩溃','建议web服务器拒绝Host的内容不是ip地址的请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (960018,'当开通严格限制后，将限制字符范围32-126','@validateByteRange 32-126','如果开通了严格限制模式，该规则检测用户的请求数据,包括请求参数、内容或请求头内容等必须是32-126内的可见字符','PROTOCOL','block',0,1395124100,NULL,4022,'低危','','','PROTOCOL');
INSERT INTO `t_rules` VALUES (960020,'HTTP/1.1要求Pragma和Cache-Control必须成对出现','@eq 1','RFC规范要求HTTP/1.1中当有Pragma字段的时候必须也有Cache-Control字段，否则本规则将阻断','PROTOCOL','block',0,1395124100,NULL,4011,'低危','影响网站的缓存，缓存的主要作用是防止用户频繁刷新列表，导致服务器数据负担。','建议在web服务器对请求包进行检测，是否HTTP/1.1，且参数Pragma跟Cache-Control','PROTOCOL');
INSERT INTO `t_rules` VALUES (960021,'请求头中的Accept的内容为空','^$','该规则检测当用户Http请求动作为非OPTIONS时，请求头中的Accetp的内容是否为空，为空则阻断','PROTOCOL','block',1,1395124100,NULL,4504,'低危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让敌人模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议web服务器拒绝请求头中的Accept的内容为空的请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (960022,'Expect只是HTTP/1.1的一个属性','@contains 100-continue','Expect只是HTTP/1.1的属性，所以该规则检测请求的http协议版本，如果是HTTP/1.0，但请求头中有Expect字段，该规则将阻断','PROTOCOL','block',0,1395124100,NULL,4010,'低危','自动程序和机器人进行大量访问，造成网站崩溃','建议检测出现Expect字段的请求是否HTTP/1.1版本，不是则拒绝请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (960024,'启发式检测(非单词字符检测）','\\W{4,}','该规则在http请求的参数中检测连续等于或超过4次的非单词字符的出现','GENERIC','block',0,1452647413,NULL,3023,'高危','攻击者可在参数中出现多重连续的非单词字符实施命令注入','建议web服务器把请求参数值为四个以上的非单词字符的请求过滤了。','GENERIC');
INSERT INTO `t_rules` VALUES (960032,'检测请求方法是否符合http策略（Http Policy）','!@within %{tx.allowed_methods}','如果请求方法在http策略中受限，则阻断访问（Http Policy）','OTHER','block',1,1452647413,NULL,90086,'高危','put、delete、post、options、patch等等这些请求能对服务器进行增删改。','建议如果不需要接收以下put、delete、post、options、patch请求方法，请作出相关限制，如拒绝访问','OTHER');
INSERT INTO `t_rules` VALUES (960034,'检测http版本是否符合http策略（Http Policy）','!@within %{tx.allowed_http_versions}','如果请求数据的http协议版本在http策略中受限，则阻断访问（Http Policy）','OTHER','block',1,1452647413,NULL,90089,'高危','攻击者会尝试使用除了HTTP/0.9,HTTP/1.0，HTTP/1.1以外的协议。','建议拒绝HTTP/0.9,HTTP/1.0，HTTP/1.1以外的协议进行访问','OTHER');
INSERT INTO `t_rules` VALUES (960035,'检测请求数据中的文件扩展名是否符合http策略（Http Policy）','\\.(.*)$\" \"chain,capture,setvar:tx.extension=.%{tx.1}','如果请求数据中URL的文件扩展名在http策略受限，则阻断访问（Http Policy）','OTHER','block',1,1452647413,NULL,90090,'高危','攻击者会在请求uri中的，带有如.asa/ .asax/ .ascx/ .axd/ .backup/ .bak/ .bat/ .cdx/ .cer/ .cfg/ .cmd/ .com/ .config/ .conf/ .cs/ .csproj/ .csr/ .dat/ .db/ .dbf/ .dll/ .dos/ .htr/ .htw/ .ida/ .idc/ .idq/ .inc/ .ini/ .key/ .licx/ .lnk/ .log/ .mdb/ .old/ .pass/ .pdb/ .pol/','建议对于uri中带有如.asa/ .asax/ .ascx/ .axd/ .backup/ .bak/ .bat/ .cdx/ .cer/ .cfg/ .cmd/ .com/ .config/ .conf/ .cs/ .csproj/ .csr/ .dat/ .db/ .dbf/ .dll/ .dos/ .htr/ .htw/ .ida/ .idc/ .idq/ .inc/ .ini/ .key/ .licx/ .lnk/ .log/ .mdb/ .old/ .pass/ .pdb/ .pol/ .pri','OTHER');
INSERT INTO `t_rules` VALUES (960038,'检测请求数据中的http头部是否符合http策略（Http Policy）','^(.*)$','如果请求数据中http头部在http策略中受限，则阻断访问（Http Policy）','OTHER','block',1,1452647413,NULL,90087,'中危','攻击者常常会在请求中请求头包含如Proxy-Connection、Lock-Token、Content-Range、Translate、via、if等名字。','建议web服务器拒绝请求头包含如Proxy-Connection、Lock-Token、Content-Range、Translate、via、if等名字的请求访问','OTHER');
INSERT INTO `t_rules` VALUES (960208,'检测请求参数的值长度是否过长(Request Limits)','&TX:ARG_LENGTH \"@eq 1\"','如果请求参数的值长度过长，则阻断访问(Request Limits)','OTHER','block',1,1452647413,NULL,90064,'中危','如果请求参数的单个参数值过长，会造成溢出攻击。','建议web服务器限制请求参数值的长度，一般不超过400kb','OTHER');
INSERT INTO `t_rules` VALUES (960209,'检测请求参数名的长度是否过长(Request Limits)','&TX:ARG_NAME_LENGTH \"@eq 1\"','如果请求参数名的长度过长，则阻断访问(Request Limits)','OTHER','block',1,1452647413,NULL,90063,'中危','如果请求参数的参数名过长，会造成溢出攻击。','建议web服务器限制请求参数名的长度，一般不超过100kb','OTHER');
INSERT INTO `t_rules` VALUES (960335,'检测请求参数的个数是否超过限制(Request Limits)','&TX:MAX_NUM_ARGS \"@eq 1\"','如果请求参数的个数超过限制，则阻断访问(Request Limits)','OTHER','block',1,1452647413,NULL,90059,'中危','如果请求参数的参数的个数过多，会造成溢出攻击。','建议web服务器限制请求参数的个数，一般不超过255','OTHER');
INSERT INTO `t_rules` VALUES (960341,'检测请求参数的总长度是否超过限制(Request Limits)','&TX:TOTAL_ARG_LENGTH \"@eq 1\"','如果请求参数的总长度超过限制，则阻断访问(Request Limits)','OTHER','block',1,1452647413,NULL,90060,'中危','如果请求参数的参数值总长度过长，会造成溢出攻击。','建议web服务器限制请求参数值总长度，一般不超过64000','OTHER');
INSERT INTO `t_rules` VALUES (960342,'检测上传数据中单个文件的长度是否超过限制(Request Limits)','&TX:MAX_FILE_SIZE \"@eq 1\"','如果上传数据中单个文件的长度超过限制，则阻断访问(Request Limits)','OTHER','block',1,1452647413,NULL,90061,'中危','上传文件过大会占用资源，通过大量上传大文件会使得服务器内存饱满','建议web服务器限制上传数据当个文件的大小，一般不超过1048576','OTHER');
INSERT INTO `t_rules` VALUES (960343,'检测上传数据中所有文件的总长度是否超过限制(Request Limits)','&TX:COMBINED_FILE_SIZES \"@eq 1\"','如果上传数据中所有文件的总长度超过限制，则阻断访问(Request Limits)','OTHER','block',1,1452647413,NULL,90062,'中危','如果上传文件的总大小超出了允许的最大值，会造成溢出攻击。','建议限制客户上传的文件的大小','OTHER');
INSERT INTO `t_rules` VALUES (960901,'限制请求的参数或内容必须为可打印字符1-255','@validateByteRange 1-255','该规则检测用户的请求数据,包括请求参数、内容或请求头内容等必须是1-255内的可见字符','PROTOCOL','block',0,1395124100,NULL,4021,'中危','攻击者通过注入不可打印的字符进行sql注入或xss注入','建议在web服务器对请求包中包含非1-255的可打印字符的请求进行过滤','PROTOCOL');
INSERT INTO `t_rules` VALUES (960902,'拒绝请求字段Content-Encoding的内容为Identity','^Identity$','identity编码只能用在Accept-Encoding头中，而不能用在Content-Encoding中,如果使用了，该规则将阻断','PROTOCOL','block',0,1395124100,NULL,4009,'中危','攻击者伪造身份编码进行会话劫劫持','建议web服务器拒绝请求字段Content-Encoding的内容为Identity的请求','PROTOCOL');
INSERT INTO `t_rules` VALUES (960904,'有请求内容的请求头中缺少Content-Type','@eq 0','该规则检测当请求头中的Content-Length存在，并且内容不为零的时候，是否在请求头中有Content-Type字段，如没，则web应用程序不知道怎么解析请求数据，阻断','PROTOCOL','block',1,1395124100,NULL,4507,'中危','如果一个请求带有请求体，就不能缺失了content type。','建议web服务器对请求包进行检测，对于带请求体却缺少content type字段的请求拒绝访问。','PROTOCOL');
INSERT INTO `t_rules` VALUES (960911,'URI请求格式验证','!^(?i:(?:[a-z]{3,10}\\s+(?:\\w{3,7}?://[\\w\\-\\./]*(?::\\d+)?)?/[^?#]*(?:\\?[^#\\s]*)?(?:#[\\S]*)?|connect (?:\\d{1,3}\\.){3}\\d{1,3}\\.?(?::\\d+)?|options \\*)\\s+[\\w\\./]+|get /[^?#]*(?:\\?[^#\\s]*)?(?:#[\\S]*)?)$','该规则规定了RFC规范的URI格式：\"http:\" \"//\" host [ \":\" port ] [ abs_path [ \"?\" query ]] ,并同时规定了CONNECT、OPTIONS、GET请求时的正确格式','PROTOCOL','block',0,1395124100,NULL,4001,'中危','攻击者通过破坏通信协议进行攻击。这种类型的攻击可以让攻击者模仿他人,发现敏感信息,控制会议的结果,或执行其他攻击','建议web服务器对URI的请求格式进行验证，请求格式如\"http:\" \"//\" host [ \":\" port ] [ abs_path [ \"?\" query ]] \n#','PROTOCOL');
INSERT INTO `t_rules` VALUES (960912,'请求 Body是否正确','!@eq 0','该规则确定用户的请求体是否被正确的处理了，如果有错误将被阻断','PROTOCOL','block',0,1395124100,NULL,4003,'中危','','','PROTOCOL');
INSERT INTO `t_rules` VALUES (960914,'严格的Multipart数据解析检查','!@eq 0','该规则严格检查用户提交的窗体数据（multipart/form-data）,如果该规则对您的环境太严格，可以停用或修改规则动作为仅记录','PROTOCOL','block',0,1395124100,NULL,4004,'中危','PHP解析multipart/form-datahttp请求的body part请求头时，重复拷贝字符串导致DOS。远程攻击者通过发送恶意构造的multipart/form-data请求，导致服务器CPU资源被耗尽，从而远程DOS服务器','建议在web服务器上设置Multipart白名单','PROTOCOL');
INSERT INTO `t_rules` VALUES (960915,'未匹配的Multipart Boundary检查','!@eq 0','该规则探测Multipart解析器探测到的可能的未匹配boundary','PROTOCOL','block',0,1395124100,NULL,4005,'中危','PHP解析multipart/form-datahttp请求的body part请求头时，重复拷贝字符串导致DOS。远程攻击者通过发送恶意构造的multipart/form-data请求，导致服务器CPU资源被耗尽，从而远程DOS服务器','建议在web服务器上设置Multipart白名单','PROTOCOL');
INSERT INTO `t_rules` VALUES (970002,'统计页面信息泄漏','\\b(?:Th(?:is (?:summary was generated by.{0,100}?(?:w(?:ebcruncher|wwstat)|analog|Jware)|analysis was produced by.{0,100}?(?:calamaris|EasyStat|analog)|report was generated by WebLog)|ese statistics were produced by (?:getstats|PeLAB))|[gG]enerated by.{0,','该规则检测服务器响应页面中是否会泄漏统计页面中包含一些信息。如：This summary was generated by ***(wwwstat)','LEAKAGE','block',1,1395124100,NULL,6016,'中危','当发生了信息泄露，响应体中会出现this summary was generated by| webcruncher was produced by |report was generated by weblog|statistics were prodeced等字符。信息泄露会暴露服务器的敏感信息，使攻击者能够通过泄露的信息进行进一步入侵。\n','建议对含有This is summary was generated by...|... was generated by WebLog |...was produced by等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970003,'数据库错误信息泄漏(OWASP TOP 10)','(?:\\b(?:(?:s(?:elect list because it is not contained in (?:an aggregate function and there is no|either an aggregate function or the) GROUP BY clause|upplied argument is not a valid (?:PostgreSQL result|O(?:racle|DBC)|M(?:S |y)SQL))|S(?:yntax error conve','该规则检测服务器响应页面中是否会泄漏数据库的一些错误信息。如：SQL Server does not exist or access denied,PostgreSQL *** ERROR','LEAKAGE','block',1,1395124100,NULL,6017,'高危','当发生了信息泄露，响应体中会出现select list because it is not contained in anagregate function and there is no| GROUP BY upplied argument is not a valid |does not match with a table name or alias name used in the query等字符。数据库信息泄露会让攻击者知道数据库类型甚至分析出数据库存在的漏洞，会降低攻击难度。','建议对含有select list because it is not contained in anagregate function and there is no| GROUP BY upplied argument is not a valid |does not match with a table name or alias name used in the query等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970004,'IIS错误信息泄漏(OWASP TOP 10)','(?:\\b(?:A(?:DODB\\.Command\\b.{0,100}?\\b(?:Application uses a value of the wrong type for the current operation\\b|error\')| trappable error occurred in an external object\\. The script cannot continue running\\b)|Microsoft VBScript (?:compilation (?:\\(0x8|erro','该规则检测服务器响应页面，看在IIS错误信息页面中是否会泄漏信息。如泄漏.net版本信息：Microsoft .NET Framework Version:***','LEAKAGE','block',1,1395124100,NULL,6018,'中危','当发生了IIS错误信息泄露，响应体中会出现ADODB.Command  |Application uses a value of the wrong type for the current operation |trappable error occurred in an external object 等字符。信息泄露会暴露服务器的敏感信息，使攻击者能够通过泄露的信息进行进一步入侵；','建议对含有ADODB.Command  |Application uses a value of the wrong type for the current operation |trappable error occurred in an external object等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970007,'Zope web服务器信息泄漏(OWASP TOP 10)','<h2>Site Error<\\/h2>.{0,20}<p>An error was encountered while publishing this resource\\.','该规则检测服务器响应页面是否泄漏Zope服务器的相关信息，如：Site Error   An error was encountered while publishing this resource ***','LEAKAGE','block',1,1395124100,NULL,6001,'中危','当发生了zope服务器的信息泄露，响应体中会出现<h2>Site Error</h2>  |  <p>An error was encountered while publishing this resource.等字符。这可能使得攻击者了解远程系统/服务器类型以便进行下一步的攻击。','建议对含有ADODB.Command  |Application uses a value of the wrong type for the current operation |trappable error occurred in an external object等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970008,'Cold Fusion信息泄漏(OWASP TOP 10)','\\bThe error occurred in\\b.{0,100}: line\\b.{0,1000}\\bColdFusion\\b.*?\\bStack Trace \\(click to expand\\)','该规则检测服务器响应页面是否会泄漏Cold Fusion的相关信息，如：The error occurred in *** : line *** ColdFusion','LEAKAGE','block',1,1395124100,NULL,6002,'中危','当发生了ColdFusion 服务器的信息泄露，响应体中会出现The error occurred in | line |ColdFusion Srack Trace (click to expand)等字符。这可能使得攻击者了解远程系统/服务器类型以便进行下一步的攻击。','建议对含有The error occurred in | line |ColdFusion Srack Trace (click to expand)等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970009,'PHP信息泄漏(OWASP TOP 10)','<b>Warning<\\/b>.{0,100}?:.{0,1000}?\\bon line\\b','该规则检测服务器响应页面是否会泄漏PHP的相关信息，如：Warning *** :on line','LEAKAGE','block',1,1395124100,NULL,6003,'中危','当发生了PHP信息泄露，响应体中会出现<b>Warning</b> :   on line等字符。信息泄露会暴露服务器的敏感信息，使攻击者能够通过泄露的信息进行进一步入侵。','建议对含有<b>Warning</b> :   on line等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970010,'ISA服务器信息泄漏(OWASP TOP 10)','\\b403 Forbidden\\b.*?\\bInternet Security and Acceleration Server\\b\\','该规则检测服务器响应页面是否会泄漏ISA服务器相关的信息，如：403 Forbidden *** Internet Security and Acceleration Server','LEAKAGE','block',1,1395124100,NULL,6004,'中危','当发生了ISA服务器信息泄露，响应体中会出现403 Forbidden Internet Security and Acceleration Server等字符。这可能使得攻击者了解远程系统/服务器类型以便进行下一步的攻击。','建议对含有403 Forbidden Internet Security and Acceleration Server等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970011,'文件或目录名信息泄漏(OWASP TOP 10)','href\\s?=[\\s\\\"\\\']*[A-Za-z]\\:\\x5c([^\\\"\\\']+)','该规则检测服务器响应页面内容是否泄漏文件或目录信息。如：herf = 文件路径','LEAKAGE','block',1,1395124100,NULL,6012,'中危','当发生了网站目录结构信息泄露，响应体中会出现href =\" A :\\x5c\"等字符。这种攻击会让攻击者很容易的发现服务器上的敏感文件。','建议对含有href =\" A :\\x5c\"等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970012,'微软Office文档属性信息泄漏(OWASP TOP 10)','<o:documentproperties>','该规则检测服务器响应页面是否泄漏微软Office文档的属性信息，如：通过<o:documentproperties>泄漏','LEAKAGE','block',1,1395124100,NULL,6005,'中危','当发生了微软offic文档的内容/属性信息泄露，响应体中会出现<o:documentproperties>。导致了重要的信息（如账号密码、源码、系统用户）的泄漏，进而扩大了威胁。','建议对含有<o:documentproperties>等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970013,'目录列表泄漏(OWASP TOP 10)','(?:<(?:TITLE>Index of.*?<H|title>Index of.*?<h)1>Index of|>\\[To Parent Directory\\]<\\/[Aa]><br>)','该规则检测服务器响应页面中是否泄漏服务端的目录列表。一般目录列表页面可能包含以下信息：[To Parent Directory], 标题一般是Index of等','LEAKAGE','block',1,1395124100,NULL,6020,'中危','当发生了目录列表信息泄露，响应体中会出现<TITLE>Index of <title>Index of <h1>Index of|[To parent Directory]</a><br>等字符。这种攻击会让攻击者很容易的发现服务器上的敏感文件。','建议对含有<o:documentproperties>等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970014,'ASP/JSP源代码泄漏(OWASP TOP 10)','(?:\\b(?:(?:s(?:erver\\.(?:(?:(?:htm|ur)lencod|execut)e|createobject|mappath)|cripting\\.filesystemobject)|(?:response\\.(?:binary)?writ|vbscript\\.encod)e|wscript\\.(?:network|shell))\\b|javax\\.servlet)|\\.(?:(?:(?:createtex|ge)t|loadfrom)file|addheader)\\b|<jsp:','该规则检测服务器响应页面内容是否有JSP/ASP源代码泄漏。如：server.htmlencode,server.execute,<jsp:***等','LEAKAGE','block',1,1395124100,NULL,6013,'中危','当发生了ASP/JSP源代码泄漏，响应体中会出现server.htmlencode.filesystemobject|.createtext file <jsp:等字符。如果发生了源码泄露，可能会让攻击者从源码中分析出更多其它的漏洞，如SQL注入，文件上传，代码执行等。','建议对含有<o:documentproperties>等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970015,'PHP源代码泄漏(OWASP TOP 10)','(?:\\b(?:f(?:tp_(?:nb_)?f?(?:ge|pu)t|get(?:s?s|c)|scanf|write|open|read)|gz(?:(?:encod|writ)e|compress|open|read)|s(?:ession_start|candir)|read(?:(?:gz)?file|dir)|move_uploaded_file|(?:proc_|bz)open|call_user_func)|\\$_(?:(?:pos|ge)t|session))\\b','该规则检测服务器响应页面内容是否有PHP源代码泄漏。如：fgets ***,fget ***, readdir ***,$_post, $_get, $_session','LEAKAGE','block',1,1395124100,NULL,6014,'中危','当发生了PHP源代码泄露，响应体中会出现ftp_nb_fget|getsread|readgzfile|move_uploaded_file|bzopen等字符。如果发生了源码泄露，可能会让攻击者从源码中分析出更多其它的漏洞，如SQL注入，文件上传，代码执行等。','建议对含有<o:documentproperties>等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970016,'Cold Fusion源代码泄漏(OWASP TOP 10)','<cf','该规则检测服务器响应页面内容是否有Cold Fusion的源代码泄漏，如：<cf***','LEAKAGE','block',1,1395124100,NULL,6007,'中危','如果当发生了源码泄露，响应体中出现了如<cf等字符，很大可能是发生了ColdFusion的源代码泄露了。攻击者从源码中分析出更多其它的漏洞，如SQL注入，文件上传，代码执行等。','建议对含有<cf等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970018,'IIS缺省安装目录泄漏','[a-z]:\\\\\\\\inetpub\\b','该规则检测服务器响应页面内容是否泄漏了IIS安装在缺省安装目录，如：c:\\inetpub','LEAKAGE','block',1,1395124100,NULL,6008,'中危','如果当发生了IIS缺省安装目录信息泄露，响应体中出现了如a:\\\\inetpub等字符，使攻击者能够通过泄露的信息进行进一步入侵；','建议对含有a:\\\\inetpub等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970021,'WebLogic信息泄漏','<title>JSP compile error<\\/title>','该规则检测当服务器返回状态码为500的时候，响应页面是否泄漏WebLogic的信息，如：<title>JSP compile error</title>','LEAKAGE','block',1,1395124100,NULL,6011,'中危','当发生了Weblogic服务器的信息泄露，响应体中会出现<title>JSP compile error</title>，并且服务器应答状态是500。使得攻击者了解远程系统/服务器类型以便进行下一步的攻击。','建议对含有<title>JSP compile error</title>等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970118,'Web应用程序不可用信息泄漏(OWASP TOP 10)','(?:Microsoft OLE DB Provider for SQL Server(?:<\\/font>.{1,20}?error \'800(?:04005|40e31)\'.{1,40}?Timeout expired| \\(0x80040e31\\)<br>Timeout expired<br>)|<h1>internal server error<\\/h1>.*?<h2>part of the server has crashed or it has a configuration error\\.<','该规则检测服务器响应页面内容是否泄漏了相关的web应用程序信息。如：Microsoft OLE DB Provider for SQL Server (0x80040e31) Timeout expired','LEAKAGE','block',1,1395124100,NULL,6010,'中危','攻击者正使用自动化客户端或者自动化扫描工具对服务器操作的话，响应体出现了服务端数据库连接失败的提示。一旦让攻击者找到后台的弱点，将会进行下一步的攻击。','建议对含有Microsoft OLE DB Provider for SQL Server|part of the server has crashed or it has a configuration error|cannot connect to the server: timed out等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970901,'Web应用程序不可用，5XX错误(OWASP TOP 10)','^5\\d{2}$','该规则检测服务器返回的状态码，如果是5XX错误码，则表示web应用程序不可用，该规则将阻止5XX错误。','LEAKAGE','block',1,1395124100,NULL,6009,'中危','如果响应状态是5字头，这类状态码代表了服务器在处理请求的过程中有错误或者异常状态发生，也有可能是服务器意识到以当前的软硬件资源无法完成对请求的处理。除非这是一个HEAD 请求，否则服务器应当包含一个解释当前错误状态以及这个状况是临时的还是永久的解释信息实体。浏览器应当向用户展示任何在当前响应中被包含的实体。','建议对响应状态是5字头的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970902,'xml中的PHP源代码泄漏(OWASP TOP 10)','<\\?(?!xml)','该规则检测服务器响应页面中的xml内容中是否有PHP源代码泄漏。','LEAKAGE','block',1,1395124100,NULL,6015,'中危','如果xml中的PHP源码泄露，应答体中会出现<?xml，并且没有 interplay|hdr|movi|gif|%pdf等字符。攻击者从源码中分析出更多其它的漏洞，如SQL注入，文件上传，代码执行等。','建议对含有<?xml，并且没有 interplay|hdr|movi|gif|%pdf等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970903,'ASP/JSP源代码泄漏(OWASP TOP 10)','\\<\\%','该规则检测服务器响应页面内容是否有ASP/JSP的源代码泄漏，如：<%***','LEAKAGE','block',1,1395124100,NULL,6006,'中危','如果当发生了ASP/JSP源代码泄漏，响应体中会出现\\<\\%，并且没有出现如 interplay|mthd|exif|.ra|riff等字符。发生了源码泄露，让攻击者从源码中分析出更多其它的漏洞，如SQL注入，文件上传，代码执行等。','建议对含有\\<\\%，并且没有出现如 interplay|mthd|exif|.ra|riff等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (970904,'IIS的404错误页面泄漏信息(OWASP TOP 10)','\\bServer Error in.{0,50}?\\bApplication\\b','该规则检测IIS的404错误页面，看是否泄漏信息。如泄漏web应用程序相关的信息：Server Error in *** Application','LEAKAGE','block',1,1395124100,NULL,6019,'中危','如果发生了IIS的错误信息泄露，响应状态将不是404，并且响应体中会出现如Server Error in  | Application等字符。信息泄露会暴露服务器的敏感信息，使攻击者能够通过泄露的信息进行进一步入侵','建议对含有Server Error in  | Application等字符的响应包进行限制。','LEAKAGE');
INSERT INTO `t_rules` VALUES (973300,'xss常规异常检测(OWASP TOP 10)','<(a|abbr|acronym|address|applet|area|audioscope|b|base|basefront|bdo|bgsound|big|blackface|blink|blockquote|body|bq|br|button|caption|center|cite|code|col|colgroup|comment|dd|del|dfn|dir|div|dl|dt|em|embed|fieldset|fn|font|form|frame|frameset|h1|head|hr|h',' 通过在请求内容中检测address、applet、area、audioscope、basefront等关键词来检测可能的xss攻击','XSS','block',0,1395124100,NULL,8072,'高危','当cookies或请求参数或xml中出现如<abbr%|<fieldset$|<shadow#等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<abbr%|<fieldset$|<shadow#等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973301,'检测allowscriptaccess、rel=(OWASP TOP 10)','\\ballowscriptaccess\\b|\\brel\\b\\W*?=',' 通过在请求内容中检测allowscriptaccess、 rel=来检测XSS攻击','XSS','block',0,1395124100,NULL,8073,'高危','当cookies或请求参数或xml中出现如allowscriptaccess|rel%=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有allowscriptaccess|rel%=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973302,'检测application/x-shockwave-flash|image/svg+xml(OWASP TOP 10)','.+application/x-shockwave-flash|image/svg\\+xml|text/(css|html|ecmascript|javascript|vbscript|x-(javascript|scriptlet|vbscript)).+',' 通过在请求内容中检测application/x-shockwave-flash、image/svg+xml、text/css、text/javascript等来检测XSS攻击','XSS','block',0,1395124100,NULL,8074,'高危','当cookies或请求参数或xml中出现如application/x-shockwave-flash|image/svg+xml|text/ecmascript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有application/x-shockwave-flash|image/svg+xml|text/ecmascript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973303,'检测各个事件(OWASP TOP 10)','\\bon(abort|blur|change|click|dblclick|dragdrop|error|focus|keydown|keypress|keyup|load|mousedown|mousemove|mouseout|mouseover|mouseup|move|readystatechange|reset|resize|select|submit|unload)\\b\\W*?=',' 通过在请求内容中检测事件处理的名字，来检测xss攻击，如：<body onload=...>    <img src=x onerror=...>等','XSS','block',0,1395124100,NULL,8075,'高危','当cookies或请求参数或xml中出现如inabort#=|onmouseout#=|onfocus%=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有inabort#=|onmouseout#=|onfocus%=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973304,'利用通用URI属性来进行XSS攻击(OWASP TOP 10)','\\b(background|dynsrc|href|lowsrc|src)\\b\\W*?=',' 检测利用通用URI属性来上传数据进行XSS攻击，如：<a href=\"javascript:...\">Link</a> ，<img src=javascript:...>等','XSS','block',0,1395124100,NULL,8076,'高危','当cookies或请求参数或xml中出现如background$=|lowsrc%|dynsrc#等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有background$=|lowsrc%|dynsrc#等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973305,'变种的（隐蔽的）利用通用URI属性来进行XSS攻击(OWASP TOP 10)','(asfunction|javascript|vbscript|data|mocha|livescript):',' 检测一些隐藏的利用通用URI属性来上传数据进行XSS攻击，如：<img src=jaVaScrIpt:...>， <img src=\"jaa&#09;ascript:...\">等','XSS','block',0,1395124100,NULL,8077,'高危','当cookies或请求参数或xml中出现如asfunction:|javascript:|vbscript:|livescript:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有asfunction:|javascript:|vbscript:|livescript:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973306,'通过style属性来进行的XSS攻击(OWASP TOP 10)','\\bstyle\\b\\W*?=',' 检测通过利用style属性来进行的XSS攻击，比较典型的如：<div style=\"background-image: url(javascript:...)\">','XSS','block',0,1395124100,NULL,8078,'高危','当cookies或请求参数或xml中出现如style #=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有style #=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973307,'javascript片段检测(OWASP TOP 10)','(fromcharcode|alert|eval)\\s*\\(',' 通过检测javascript程序片段来检测XSS攻击，比如如下片段：alert(String.fromCharCode(88,83,83) window.execScript(\"alert(\'test\');\", \"JavaScript\");...','XSS','block',0,1395124100,NULL,8079,'高危','当cookies或请求参数或xml中出现如formcharcode (|alert (|eval (等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有formcharcode (|alert (|eval (等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973308,'css攻击片段检测(OWASP TOP 10)','background\\b\\W*?:\\W*?url|background-image\\b\\W*?:|behavior\\b\\W*?:\\W*?url|-moz-binding\\b|@import\\b|expression\\b\\W*?\\(',' 检测CSS中的XSS攻击片段。如：<div style=\"background-image: url(javascript:...)\">等。','XSS','block',0,1395124100,NULL,8080,'高危','当cookies或请求参数或xml中出现如background #url|background-image@|behavior $：#url等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有background #url|background-image@|behavior $：#url等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973309,'检测<![CDATA[中的可疑行为(OWASP TOP 10)','<!\\[cdata\\[|\\]\\]>','检测<![CDATA[中的可能XSS攻击，如：<C><![CDATA[<IMG SRC=\"javas]]><![CDATA[cript:alert(\'XSS\');\">]]></C>','XSS','block',0,1395124100,NULL,8081,'高危','当cookies或请求参数或xml中出现如<![cdata[|]]等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<![cdata[|]]等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973310,'检测包含xss的javascript代码或标签等(OWASP TOP 10)','[/\'\\\"<]xss[/\'\\\">]',' 检测包含xss的javascript代码或标签等，如：alert(/xss/)','XSS','block',0,1395124100,NULL,8082,'高危','当cookies或请求参数或xml中出现如<xss>|\\xss/|\"xss\"等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<xss>|\\xss/|\"xss\"等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973311,'检测(88,83,83)(OWASP TOP 10)','(88,83,83)',' 检测(88,83,83)，如：String.fromCharCode(88,83,83)','XSS','block',0,1395124100,NULL,8083,'高危','当cookies或请求参数或xml中出现如88,83,83等字符的时候，需要注意是否受到了XSS攻击，攻击者会执行String.fromCharCode(88,83,83)，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有88,83,83等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973312,'检测可疑符号及xss标签(OWASP TOP 10)','\';!--\\\"<xss>=&{}',' 检测可疑符号及xss标签，如：\'\';!--\"<XSS>=&{()}','XSS','block',0,1395124100,NULL,8084,'高危','xss攻击危害：1、盗取各类用户帐号，如机器登录帐号、用户网银帐号、各类管理员帐号2、控制企业数据，包括读取、篡改、添加、删除企业敏感数据的能力3、盗窃企业重要的具有商业价值的资料4、非法转账5、强制发送电子邮件6、网站挂马7、控制受害者机器向其它网站发起攻击','xss攻击危害：1、盗取各类用户帐号，如机器登录帐号、用户网银帐号、各类管理员帐号2、控制企业数据，包括读取、篡改、添加、删除企业敏感数据的能力3、盗窃企业重要的具有商业价值的资料4、非法转账5、强制发送电子邮件6、网站挂马7、控制受害者机器向其它网站发起攻击','XSS');
INSERT INTO `t_rules` VALUES (973313,'检测&{(OWASP TOP 10)','&{',' 检测&{，如：&{alert(\'xss\')}，这个在Netscape 4中会执行','XSS','block',0,1395124100,NULL,8085,'高危','当cookies或请求参数或xml中出现如&{等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有&{等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973314,'利用<!(doctype|entity)标签的XSS(OWASP TOP 10)','<!(doctype|entity)',' 检测可能的利用<!(doctype，<!ENTITY进行的XSS，如：<!DOCTYPE html [  <!ENTITY inject \"&#60;script&#62;alert(1)&#60;/script&#62;\"> ]>','XSS','block',0,1395124100,NULL,8086,'高危','当cookies或请求参数或xml中出现如<!(doctype等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<!(doctype等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973315,'针对IE的XSS过滤2(OWASP TOP 10)','(?i:<style.*?>.*?((@[i\\\\\\\\])|(([:=]|(&#x?0*((58)|(3A)|(61)|(3D));?)).*?([(\\\\\\\\]|(&#x?0*((40)|(28)|(92)|(5C));?)))))',' 检测针对IE的如下内容，如： <style ...>@i...','XSS','block',0,1395124100,NULL,8088,'高危','当cookies或请求参数或xml中出现如<style>@i|&#x058;\\\\等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<style>@i|&#x058;\\\\等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973316,'针对IE的XSS过滤24(OWASP TOP 10)','(?i:[ /+\\t\\\"\\\'`]style[ /+\\t]*?=.*([:=]|(&#x?0*((58)|(3A)|(61)|(3D));?)).*?([(\\\\\\\\]|(&#x?0*((40)|(28)|(92)|(5C));?)))',' 测针对IE的特殊编码内容，如： style=...&#x0058;...&#x0040;','XSS','block',0,1395124100,NULL,8110,'高危','当cookies或请求参数或xml中出现如\"style+=|&#x05C；等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有\"style+=|&#x05C；等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973317,'针对IE的XSS过滤15(OWASP TOP 10)','(?i:<OBJECT[ /+\\t].*?((type)|(codetype)|(classid)|(code)|(data))[ /+\\t]*=)',' 检测针对IE的如下内容，如： <OBJECT type = ...','XSS','block',0,1395124100,NULL,8101,'高危','当cookies或请求参数或xml中出现如<OBJECT+typt/=|<OBJECT+codetype+=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<OBJECT+typt/=|<OBJECT+codetype+=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973318,'针对IE的XSS过滤14(OWASP TOP 10)','(?i:<APPLET[ /+\\t>])',' 检测针对IE的如下内容，如： <APPLET> ...','XSS','block',0,1395124100,NULL,8100,'高危','当cookies或请求参数或xml中出现如<APPLET+等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<APPLET+等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973319,'检测datasrc','(?i:[ /+\\t\\\"\\\'`]datasrc[ +\\t]*?=.)','','XSS','block',0,1395124100,NULL,8112,'高危','当cookies或请求参数或xml中出现如+datasrc\\t=1等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有+datasrc\\t=1等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973320,'针对IE的XSS过滤13(OWASP TOP 10)','(?i:<BASE[ /+\\t].*?href[ /+\\t]*=)',' 检测针对IE的如下内容，如： <BASE href = ...','XSS','block',0,1395124100,NULL,8099,'高危','当cookies或请求参数或xml中出现如<BASE+href+=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<BASE+href+=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973321,'针对IE的XSS过滤12(OWASP TOP 10)','(?i:<LINK[ /+\\t].*?href[ /+\\t]*=)',' 检测针对IE的如下内容，如： <LINK href = ...','XSS','block',0,1395124100,NULL,8098,'高危','当cookies或请求参数或xml中出现如<LINK+href+=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<LINK+href+=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973322,'针对IE的XSS过滤10(OWASP TOP 10)','(?i:<META[ /+\\t].*?http-equiv[ /+\\t]*=[ /+\\t]*[\\\"\\\'`]?(((c|(&#x?0*((67)|(43)|(99)|(63));?)))|((r|(&#x?0*((82)|(52)|(114)|(72));?)))|((s|(&#x?0*((83)|(53)|(115)|(73));?)))))',' 检测针对IE的如下内容，如： <META http-equiv = ...','XSS','block',0,1395124100,NULL,8096,'高危','当cookies或请求参数或xml中出现如<META+ http-equiv+\\t\"&#x063;|<META+ http-equiv+\\t\"&#x073;等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<META+ http-equiv+\\t\"&#x063;|<META+ http-equiv+\\t\"&#x073;等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973323,'针对IE的XSS过滤9(OWASP TOP 10)','(?i:<[?]?import[ /+\\t].*?implementation[ /+\\t]*=)',' 检测针对IE的如下内容，如： <import implementation= <EMBED src=....','XSS','block',0,1395124100,NULL,8095,'高危','当cookies或请求参数或xml中出现如<?import+implementation+=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<?import+implementation+=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973324,'针对IE的XSS过滤8(OWASP TOP 10)','(?i:<EMBED[ /+\\t].*?((src)|(type)).*?=)',' 检测针对IE的如下内容，如： <EMBED src=....','XSS','block',0,1395124100,NULL,8094,'高危','当cookies或请求参数或xml中出现如<EMBED+type=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含<EMBED+type=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973325,'针对IE的XSS过滤25(OWASP TOP 10)','(?i:[ /+\\t\\\"\\\'`]on\\[a-z]\\[a-z]\\[a-z]+?[ +\\t]*?=.)','检测针对IE的内容，如： /on...] =...','XSS','block',0,1395124100,NULL,8111,'高危','xss攻击危害：1、盗取各类用户帐号，如机器登录帐号、用户网银帐号、各类管理员帐号2、控制企业数据，包括读取、篡改、添加、删除企业敏感数据的能力3、盗窃企业重要的具有商业价值的资料4、非法转账5、强制发送电子邮件6、网站挂马7、控制受害者机器向其它网站发起攻击','对所有用户提交内容进行可靠的输入验证，包括对URL、查询关键字、HTTP头、POST数据等，仅接受指定长度范围内、采用适当格式、采用所预期的字符的内容提交，对其他的一律过滤。实现Session标记(session tokens)、CAPTCHA系统或者HTTP引用头检查，以防功能被第三方网站所执行。','XSS');
INSERT INTO `t_rules` VALUES (973326,'针对IE的XSS过滤5(OWASP TOP 10)','(?i:<.*[:]vmlframe.*?[ /+\\t]*?src[ /+\\t]*=)',' 检测针对IE的如下内容，如： <:vmlframe src=....','XSS','block',0,1395124100,NULL,8091,'高危','当cookies或请求参数或xml中出现如<attack:vmlframe+src+=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<attack:vmlframe+src+=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973327,'针对IE的XSS过滤4(OWASP TOP 10)','(?i:<[i]?frame.*?[ /+\\t]*?src[ /+\\t]*=)',' 检测针对IE的如下内容，如： <iframe src=....','XSS','block',0,1395124100,NULL,8090,'高危','当cookies或请求参数或xml中出现如<iframe +src +=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<iframe +src +=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973328,'针对IE的XSS过滤23(OWASP TOP 10)','(?i:<isindex[ /+\\t>])',' 检测针对IE的内容，如： <isindex>...','XSS','block',0,1395124100,NULL,8109,'高危','当cookies或请求参数或xml中出现如<isindex+等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<isindex+等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973329,'针对IE的XSS过滤22(OWASP TOP 10)','(?i:<form.*?>)',' 检测针对IE的内容，如： <form...>','XSS','block',0,1395124100,NULL,8108,'高危','当cookies或请求参数或xml中出现如<form>等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<form>等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973330,'针对IE的XSS过滤3(OWASP TOP 10)','(?i:<script.*?[ /+\\t]*?((src)|(xlink:href)|(href))[ /+\\t]*=)',' 检测针对IE的如下内容，如： <script src=....','XSS','block',0,1395124100,NULL,8089,'高危','当cookies或请求参数或xml中出现如<scripttest+src|xlink:href|href/=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<scripttest+src|xlink:href|href/=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973331,'针对IE的XSS过滤1(OWASP TOP 10)','(?i:<script.*?>)',' 检测针对IE的如下内容，如： <script ...>...','XSS','block',0,1395124100,NULL,8087,'高危','当cookies或请求参数或xml中出现如<scriptattack>等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<scriptattack>等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973332,'针对IE的XSS过滤21(OWASP TOP 10)','(?i:[\\\"\\\'][ ]*(([^a-z0-9~\\_:\\\' ])|(in)).*?(((l|(\\\\\\\\u006C))(o|(\\\\\\\\u006F))(c|(\\\\\\\\u0063))(a|(\\\\\\\\u0061))(t|(\\\\\\\\u0074))(i|(\\\\\\\\u0069))(o|(\\\\\\\\u006F))(n|(\\\\\\\\u006E)))|((n|(\\\\\\\\u006E))(a|(\\\\\\\\u0061))(m|(\\\\\\\\u006D))(e|(\\\\\\\\u0065)))|((o|(\\\\\\\\u006F))(n|(\\\\\\\\u0',' 检测针对IE的特殊编码内容，如： \" in ... \\\\u006C\\\\u006F...','XSS','block',0,1395124100,NULL,8107,'高危','当cookies或请求参数或xml中出现如\"%\\\\u006C=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有\"%\\\\u006C=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973333,'针对IE的XSS过滤19(OWASP TOP 10)','(?i:[\\\"\\\'][ ]*(([^a-z0-9~\\_:\\\' ])|(in)).+?[.].+?=)',' 检测针对IE的内容，如： \" in . ... =','XSS','block',0,1395124100,NULL,8105,'高危','当cookies或请求参数或xml中出现如\"#|in.=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有\"#|in.=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973334,'针对IE的XSS过滤18(OWASP TOP 10)','(?i:[\\\"\\\'].*?\\)[ ]*(([^a-z0-9~\\_:\\\' ])|(in)).+?\\',' 检测针对IE的内容，如： \"...) in ...(...','XSS','block',0,1395124100,NULL,8104,'高危','当cookies或请求参数或xml中出现如\") #|in (等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有\") #|in (等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973335,'针对IE的XSS过滤17(OWASP TOP 10)','(?i:[\\\"\\\'][ ]*(([^a-z0-9~\\_:\\\' ])|(in)).+?\\(.*?\\))',' 检测针对IE的内容，如： \" in ...(...)','XSS','block',0,1395124100,NULL,8103,'高危','当cookies或请求参数或xml中出现如\"%|in(attack)等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有\"%|in(attack)等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973336,'基于script标签的XSS过滤(OWASP TOP 10)','(?i)(<script[^>]*>[\\s\\S]*?<\\/script[^>]*>|<script[^>]*>[\\s\\S]*?<\\/script[[\\s\\S]]*[\\s\\S]|<script[^>]*>[\\s\\S]*?<\\/script[\\s]*[\\s]|<script[^>]*>[\\s\\S]*?<\\/script|<script[^>]*>[\\s\\S]*?)','script标签的过滤，如：<script> alert(1)</script>','XSS','pass',0,1395124100,NULL,8000,'高危','当请求参数值中出现如<script> </script>|</script>|</script等脚本标签的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<script> </script>|</script>|</script等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973337,'基于事件处理的XSS过滤(OWASP TOP 10)','(?i)([\\s\\\"\'`;\\/0-9\\=]+on\\w+\\s*=)','基于onload,onerror事件等的XSS,如： <body onload=\"alert(1)\">','XSS','pass',0,1395124100,NULL,8001,'高危','当请求参数值中出现如<body onload=\"alert(1)\">等字符的时候，属于事件处理函数，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<body onload=\"alert(1)\">等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973338,'基于javascript uri的XSS过滤(OWASP TOP 10)','(?i)((?:=|U\\s*R\\s*L\\s*\\\\s*[^>]*\\s*S\\s*C\\s*R\\s*I\\s*P\\s*T\\s*:|&colon;|[\\s\\S]allowscriptaccess[\\s\\S]|[\\s\\S]src[\\s\\S]|[\\s\\S]data:text\\/html[\\s\\S]|[\\s\\S]xlink:href[\\s\\S]|[\\s\\S]base64[\\s\\S]|[\\s\\S]xmlns[\\s\\S]|[\\s\\S]xhtml[\\s\\S]|[\\s\\S]style[\\s\\S]|<style[^>]*>[\\s\\S',' 基于javascript uri的XSS攻击，如：<p style=\"background:url(javascript:alert(1))\">','XSS','pass',0,1395124100,NULL,8002,'高危','当请求参数值中出现如<p style=\"background:url(javascript:alert(1))\">等字符的时候，很大可能是攻击者尝试利用Javascript URI作为载体实行XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用或者获取cookie并利用。','建议在web服务器添加对含有<p style=\"background:url(javascript:alert(1))\">等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973344,'针对IE的XSS过滤20(OWASP TOP 10)','(?i:[\\\"\\\'][ ]*(([^a-z0-9~\\_:\\\' ])|(in)).+?[\\[].*?[\\]].*?=)',' 检测针对IE的内容，如： \" in ... [...]...=','XSS','block',0,1395124100,NULL,8106,'高危','当cookies或请求参数或xml中出现如\"$[test]=|in[attack]等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有\"$[test]=|in[attack]等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973345,'针对IE的XSS过滤7(OWASP TOP 10)','(?i:(v|(&#x?0*((86)|(56)|(118)|(76));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(b|(&#x?0*((66)|(42)|(98)|(62));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(s|(&#x?0*((83)|(53)|(115)|(73));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|',' 检测针对IE内容编码，如：&#x0086、&#x0056;等','XSS','block',0,1395124100,NULL,8093,'高危','当cookies或请求参数或xml中出现如v\\t&#x066;\\tstab;&#x?099;&#x?0D;&#x?082;等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有v\\t&#x066;\\tstab;&#x?099;&#x?0D;&#x?082;等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973346,'针对IE的XSS过滤6(OWASP TOP 10)','(?i:(j|(&#x?0*((74)|(4A)|(106)|(6A));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(a|(&#x?0*((65)|(41)|(97)|(61));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(v|(&#x?0*((86)|(56)|(118)|(76));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|',' 检测针对IE内容编码，如：&#x0074、&#x004A;等','XSS','block',0,1395124100,NULL,8092,'高危','当cookies或请求参数或xml中出现如src&javascript等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有src&javascript等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973347,'针对IE的XSS过滤16(OWASP TOP 10)','(?i:[\\\"\\\'].*?[,].*(((v|(\\\\\\\\u0076)|(\\\\166)|(\\\\x76))[^a-z0-9]*(a|(\\\\\\\\u0061)|(\\\\141)|(\\\\x61))[^a-z0-9]*(l|(\\\\\\\\u006C)|(\\\\154)|(\\\\x6C))[^a-z0-9]*(u|(\\\\\\\\u0075)|(\\\\165)|(\\\\x75))[^a-z0-9]*(e|(\\\\\\\\u0065)|(\\\\145)|(\\\\x65))[^a-z0-9]*(O|(\\\\\\\\u004F)|(\\\\117)|(\\\\x4F)',' 检测针对IE的特殊编码内容，如： \\\\u0074 \\\\u0076等。','XSS','block',0,1395124100,NULL,8102,'高危','当cookies或请求参数或xml中出现如\\\\u0076%\\\\u0061#l^u@\\\\x65\\\\u004F%\\\\u0066#l^u@\\\\x53:等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有\\\\u0076%\\\\u0061#l^u@\\\\x65\\\\u004F%\\\\u0066#l^u@\\\\x53:等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (973348,'针对IE的XSS过滤11(OWASP TOP 10)','(?i:<META[ /+\\t].*?charset[ /+\\t]*=)',' 检测针对IE的如下内容，如： <META charset = ...','XSS','block',0,1395124100,NULL,8097,'高危','当cookies或请求参数或xml中出现如<META+charset+=等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器添加对含有<META+charset+=等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (981000,'检测响应体是否有恶意的Iframe标识注入1（OutBound）','RESPONSE_BODY \"<\\W*iframe[^>]+?\\b(?:width|height)\\b\\W*?=\\W*?[\\\"\']?[^\\\"\'1-9]*?(?:(?:20|1?\\d(?:\\.\\d*)?)(?![\\d%.])|[0-3](?:\\.\\d*)?%)\"','如果响应体含有恶意的Iframe标识注入，则阻断访问1（OutBound）','OTHER','block',1,1452647413,NULL,90046,'高危','当cookies或请求参数或xml中出现如Iframe等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器对含有iframe的信息进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981001,'检测响应体是否有恶意的Iframe标识注入2（OutBound）','RESPONSE_BODY \"<\\W*iframe[^>]+?\\bstyle\\W*?=\\W*?[\\\"\']?\\W*?\\bdisplay\\b\\W*?:\\W*?\\bnone\\b\"','如果响应体含有恶意的Iframe标识注入，则阻断访问2（OutBound）','OTHER','block',1,1452647413,NULL,90047,'高危','当cookies或请求参数或xml中出现如Iframe等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器对含有iframe的信息进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981003,'检测响应体是否有恶意的Iframe标识注入3（OutBound）','RESPONSE_BODY \"(?i:<\\s*IFRAME\\s*?[^>]*?src=\\\"javascript:)\"','如果响应体含有恶意的Iframe标识注入，则阻断访问3（OutBound）','OTHER','block',1,1452647413,NULL,90045,'高危','当cookies或请求参数或xml中出现如Iframe等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器对含有iframe的信息进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981004,'检测响应体是否有恶意JS注入1（OutBound）','RESPONSE_BODY \"(?i)(String\\.fromCharCode\\(.*?){4,}\"','如果响应体含有恶意的Javascript注入，则阻断访问1（OutBound）','OTHER','block',1,1452647413,NULL,90043,'高危','攻击者会通过在网站中注入 JavaScript 进行破坏活动。使用 JavaScript 注入攻击可以执行跨站脚本 (XSS) 攻击。在跨站脚本攻击中，可以窃取保密的用户信息并将信息发送到另一个网站','建议在web服务器对响应体中包含String.fromCharCode的信息进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981005,'检测响应体是否有恶意JS注入2（OutBound）','RESPONSE_BODY \"(?i)(eval\\(.{0,15}unescape\\()\"','如果响应体含有恶意的Javascript注入，则阻断访问2（OutBound）','OTHER','block',1,1452647413,NULL,90044,'高危','攻击者会通过在网站中注入 JavaScript 进行破坏活动。使用 JavaScript 注入攻击可以执行跨站脚本 (XSS) 攻击。在跨站脚本攻击中，可以窃取保密的用户信息并将信息发送到另一个网站','建议在web服务器对响应体中包含eval(unescape（的信息进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981006,'检测响应体是否有恶意JS注入3（OutBound）','RESPONSE_BODY \"(?i)(var[^=]+=\\s*unescape\\s*;)\"','如果响应体含有恶意的Javascript注入，则阻断访问3（OutBound）','OTHER','block',1,1452647413,NULL,90041,'高危','攻击者会通过在网站中注入 JavaScript 进行破坏活动。使用 JavaScript 注入攻击可以执行跨站脚本 (XSS) 攻击。在跨站脚本攻击中，可以窃取保密的用户信息并将信息发送到另一个网站','建议在web服务器对响应体中包含var[^=]+= unescape的信息进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981007,'检测响应体是否有恶意JS注入4（OutBound）','RESPONSE_BODY \"(?i:%u0c0c%u0c0c|%u9090%u9090|%u4141%u4141)\"','如果响应体含有恶意的Javascript注入，则阻断访问4（OutBound）','OTHER','block',1,1452647413,NULL,90042,'高危','攻击者会通过在网站中注入 JavaScript 进行破坏活动。使用 JavaScript 注入攻击可以执行跨站脚本 (XSS) 攻击。在跨站脚本攻击中，可以窃取保密的用户信息并将信息发送到另一个网站','建议在web服务器对响应体中包含%u0c0c%u0c0c、%u9090%u909、|%u4141%u4141的信息进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981018,'检测异常分数是否为0（XSS Attacks)','@eq 0','','XSS','pass',0,1395124100,NULL,8004,'高危','当检测到PM_XSS_SCORE为0，将会跳过一部分的关于XSS攻击的检测，为waf提高了工作的性能。','建议在web服务器添加对含有alert$等敏感字符的数据进行过滤','XSS');
INSERT INTO `t_rules` VALUES (981020,'检测Apache SSL pinger异常（Common Exceptions）','REQUEST_LINE \"^GET /$\"\nREMOTE_ADDR \"^(127\\.0\\.0\\.|\\:\\:)1$\"\nSecRule TX:\'/PROTOCOL_VIOLATION\\\\\\/MISSING_HEADER/\' \".*\"\nTX:\'/MISSING_HEADER_/\' \"TX\\:(.*)\"\nREMOTE_ADDR \"^(127\\.0\\.0\\.|\\:\\:)1$\"\nTX:\'/PROTOCOL_VIOLATION\\\\\\/MISSING_HEADER/\' \".*\" \nTX:\'/MISSING_HEADER','检测Apache SSL pinger异常（Common Exceptions）','OTHER','block',1,1452647413,NULL,90102,'高危','','','OTHER');
INSERT INTO `t_rules` VALUES (981021,'检测Apache internal dummy connection异常（Common Exceptions）','REQUEST_LINE \"^(GET /|OPTIONS \\*) HTTP/1.0$\"\nSecRule REMOTE_ADDR \"^(127\\.0\\.0\\.|\\:\\:)1$\"\nREQUEST_HEADERS:User-Agent \"^.*\\(internal dummy connection\\)$\"\n TX:\'/PROTOCOL_VIOLATION\\\\\\/MISSING_HEADER/\' \".*\" \nTX:\'/MISSING_HEADER_/\' \"TX\\:(.*)\"\nREMOTE_ADDR \"^(127','检测Apache internal dummy connection异常（Common Exceptions）','OTHER','block',1,1452647413,NULL,90103,'高危','','','OTHER');
INSERT INTO `t_rules` VALUES (981022,'检测Adobe Flash Player异常（Common Exceptions）','REQUEST_METHOD \"@streq POST\"\nREQUEST_HEADERS:User-Agent \"@contains Adobe Flash Player\"\nREQUEST_HEADERS:X-Flash-Version \".*\"\nREQUEST_HEADERS:Content-Type \"@contains application/x-amf\" \nTX:\'/PROTOCOL_VIOLATION\\\\\\/MISSING_HEADER/\' \".*\"\nTX:\'/MISSING_HEADER_/\'','检测Adobe Flash Player异常（Common Exceptions）','OTHER','block',1,1452647413,NULL,90104,'高危','','','OTHER');
INSERT INTO `t_rules` VALUES (981036,'检测是否发生了Brute Force Attack 阻断（Brute Force）','IP:BRUTE_FORCE_BLOCK \"@eq 1\"','如果发生了Brute Force Attack 阻断，则累计阻断次数，并记录日志（Brute Force）','CC','block',1,1452647413,NULL,0,'高危','攻击者通过短时间内频繁的请求或登录，系统地组合所有可能性（例如登录时用到的账户名、密码），尝试所有的可能性破解用户的账户名、密码等敏感信息。攻击者会经常使用自动化脚本组合出正确的用户名和密码。','建议设立密码验证机制：都会设下试误的可容许次数以应对使用密码穷举法的破解者。当试误次数达到可容许次数时，密码验证系统会自动拒绝继续验证，甚至可以自动启动入侵警报机制。','OTHER');
INSERT INTO `t_rules` VALUES (981037,'检测是否发生了Brute Force Attack 阻断（无日志）（Brute Force）','&IP:BRUTE_FORCE_BLOCK_FLAG \"@eq 0\"','如果发生了Brute Force Attack 阻断，则累计阻断次数，但不记录日志（Brute Force）','CC','block',1,1452647413,NULL,0,'中危','攻击者通过短时间内频繁的请求或登录，系统地组合所有可能性（例如登录时用到的账户名、密码），尝试所有的可能性破解用户的账户名、密码等敏感信息。攻击者会经常使用自动化脚本组合出正确的用户名和密码。','建议设立密码验证机制：都会设下试误的可容许次数以应对使用密码穷举法的破解者。当试误次数达到可容许次数时，密码验证系统会自动拒绝继续验证，甚至可以自动启动入侵警报机制。','OTHER');
INSERT INTO `t_rules` VALUES (981038,'检测用户是否在10个Brute Force Protection配置文件中定义了一些URL（Brute Force）','&TX:BRUTE_FORCE_PROTECTED_URLS \"@eq 0\"','如果用户没有在10个Brute Force Protection配置文件中定义了任何URL，则跳过Brute Force Protection规则检测（Brute Force）','CC','block',1,1452647413,NULL,0,'低危','攻击者通过短时间内频繁的请求或登录，系统地组合所有可能性（例如登录时用到的账户名、密码），尝试所有的可能性破解用户的账户名、密码等敏感信息。攻击者会经常使用自动化脚本组合出正确的用户名和密码。','建议设立密码验证机制：都会设下试误的可容许次数以应对使用密码穷举法的破解者。当试误次数达到可容许次数时，密码验证系统会自动拒绝继续验证，甚至可以自动启动入侵警报机制。','OTHER');
INSERT INTO `t_rules` VALUES (981039,'获取Brute Force Protection文件名（Brute Force）','REQUEST_FILENAME \".*\"','获取Brute Force Protection文件名（Brute Force）','CC','block',1,1452647413,NULL,0,'低危','攻击者通过短时间内频繁的请求或登录，系统地组合所有可能性（例如登录时用到的账户名、密码），尝试所有的可能性破解用户的账户名、密码等敏感信息。攻击者会经常使用自动化脚本组合出正确的用户名和密码。','建议设立密码验证机制：都会设下试误的可容许次数以应对使用密码穷举法的破解者。当试误次数达到可容许次数时，密码验证系统会自动拒绝继续验证，甚至可以自动启动入侵警报机制。','OTHER');
INSERT INTO `t_rules` VALUES (981040,'检测当前IP地址是否因为高请求而被阻断（Brute Force Protection）（Brute Force）','IP:BRUTE_FORCE_BLOCK \"@eq 1\" ','如果当前IP地址因为高请求而被阻断，则跳过Brute Force Protection检测（Brute Force）','CC','block',1,1452647413,NULL,0,'低危','攻击者通过短时间内频繁的请求或登录，系统地组合所有可能性（例如登录时用到的账户名、密码），尝试所有的可能性破解用户的账户名、密码等敏感信息。攻击者会经常使用自动化脚本组合出正确的用户名和密码。','建议设立密码验证机制：都会设下试误的可容许次数以应对使用密码穷举法的破解者。当试误次数达到可容许次数时，密码验证系统会自动拒绝继续验证，甚至可以自动启动入侵警报机制。','OTHER');
INSERT INTO `t_rules` VALUES (981041,'初始化行为，不断累计Brute Force Protection请求源的个数（Brute Force）','SecAction \"phase:5,id:\'981041\',t:none,nolog,pass,setvar:ip.brute_force_counter=+1\"','初始化行为，累计Brute Force Protection请求源的个数（Brute Force）','CC','block',1,1452647413,NULL,0,'低危','','','OTHER');
INSERT INTO `t_rules` VALUES (981042,'检测Brute Force请求数值（Brute Force）','IP:BRUTE_FORCE_COUNTER \"@gt 0\"','如果Brute Force请求数值在5分钟内大于或等于50，则设置burst数值（Brute Force）','CC','block',1,1452647413,NULL,0,'中危','攻击者通过短时间内频繁的请求或登录，系统地组合所有可能性（例如登录时用到的账户名、密码），尝试所有的可能性破解用户的账户名、密码等敏感信息。攻击者会经常使用自动化脚本组合出正确的用户名和密码。','建议设立密码验证机制：都会设下试误的可容许次数以应对使用密码穷举法的破解者。当试误次数达到可容许次数时，密码验证系统会自动拒绝继续验证，甚至可以自动启动入侵警报机制。','OTHER');
INSERT INTO `t_rules` VALUES (981043,'检测Burst数值（Brute Force）','&IP:BRUTE_FORCE_COUNTER_FLAG \"@eq 0\"','如果Burst数值大于或等于2，则设置IP阻断数值为每5分钟阻断一次并发出告警（Brute Force）','CC','block',1,1452647413,NULL,0,'中危','攻击者通过短时间内频繁的请求或登录，系统地组合所有可能性（例如登录时用到的账户名、密码），尝试所有的可能性破解用户的账户名、密码等敏感信息。攻击者会经常使用自动化脚本组合出正确的用户名和密码。','建议设立密码验证机制：都会设下试误的可容许次数以应对使用密码穷举法的破解者。当试误次数达到可容许次数时，密码验证系统会自动拒绝继续验证，甚至可以自动启动入侵警报机制。','OTHER');
INSERT INTO `t_rules` VALUES (981044,'检测是否有IP地址被阻断了(Dos Protection)','IP:DOS_BLOCK \"@eq 1\"','如果有IP地址被阻断了（Dos Block），则累计阻断数值，并记录日志(Dos Protection)','CC','block',1,1452647413,NULL,0,'高危','DoS攻击是指故意的攻击网络协议实现的缺陷或直接通过野蛮手段残忍地耗尽被攻击对象的资源，目的是让目标计算机或网络无法提供正常的服务或资源访问，使目标系统服务系统停止响应甚至崩溃，而在此攻击中并不包括侵入目标服务器或目标网络设备。这些服务资源包括网络带宽，文件系统空间容量，开放的进程或者允许的连接。这种攻击会导致资源的匮乏，无论计算机的处理速度多快、内存容量多大、网络带宽的速度多快都无法避免这种攻击带来的后果','建议网络管理员要积极谨慎地维护系统，确保无安全隐患和漏洞。同时强烈建议网络管理员应当定期查看安全设备的日志，及时发现对系统的安全威胁行为。','OTHER');
INSERT INTO `t_rules` VALUES (981045,'检测是否有IP地址被阻断了,无日志(Dos Protection)','IP:DOS_BLOCK \"@eq 1\"','如果有IP地址被阻断了（Dos Block），则累计阻断数值，无日志记录(Dos Protection)','CC','block',1,1452647413,NULL,0,'高危','DoS攻击是指故意的攻击网络协议实现的缺陷或直接通过野蛮手段残忍地耗尽被攻击对象的资源，目的是让目标计算机或网络无法提供正常的服务或资源访问，使目标系统服务系统停止响应甚至崩溃，而在此攻击中并不包括侵入目标服务器或目标网络设备。这些服务资源包括网络带宽，文件系统空间容量，开放的进程或者允许的连接。这种攻击会导致资源的匮乏，无论计算机的处理速度多快、内存容量多大、网络带宽的速度多快都无法避免这种攻击带来的后果','建议网络管理员要积极谨慎地维护系统，确保无安全隐患和漏洞。同时强烈建议网络管理员应当定期查看安全设备的日志，及时发现对系统的安全威胁行为。','OTHER');
INSERT INTO `t_rules` VALUES (981046,'检测当前IP地址是否因为高请求而被阻断(Dos Protection)','IP:DOS_BLOCK \"@eq 1\"','如果当前IP地址因为高请求而被阻断，则跳过Dos Protection规则检测(Dos Protection)','CC','block',1,1452647413,NULL,0,'低危','DoS攻击是指故意的攻击网络协议实现的缺陷或直接通过野蛮手段残忍地耗尽被攻击对象的资源，目的是让目标计算机或网络无法提供正常的服务或资源访问，使目标系统服务系统停止响应甚至崩溃，而在此攻击中并不包括侵入目标服务器或目标网络设备。这些服务资源包括网络带宽，文件系统空间容量，开放的进程或者允许的连接。这种攻击会导致资源的匮乏，无论计算机的处理速度多快、内存容量多大、网络带宽的速度多快都无法避免这种攻击带来的后果','建议网络管理员要积极谨慎地维护系统，确保无安全隐患和漏洞。同时强烈建议网络管理员应当定期查看安全设备的日志，及时发现对系统的安全威胁行为。','OTHER');
INSERT INTO `t_rules` VALUES (981047,'根据网页名称判断是否为动态网页来源然后累计Dos攻击请求数（Brute Force）','REQUEST_BASENAME \"!\\.(jpe?g|png|gif|js|css|ico)$\"','根据网页名称判断是否为动态网页来源然后累计Dos攻击请求数(Dos Protection)','CC','block',1,1452647413,NULL,0,'低危','DoS攻击是指故意的攻击网络协议实现的缺陷或直接通过野蛮手段残忍地耗尽被攻击对象的资源，目的是让目标计算机或网络无法提供正常的服务或资源访问，使目标系统服务系统停止响应甚至崩溃，而在此攻击中并不包括侵入目标服务器或目标网络设备。这些服务资源包括网络带宽，文件系统空间容量，开放的进程或者允许的连接。这种攻击会导致资源的匮乏，无论计算机的处理速度多快、内存容量多大、网络带宽的速度多快都无法避免这种攻击带来的后果','建议网络管理员要积极谨慎地维护系统，确保无安全隐患和漏洞。同时强烈建议网络管理员应当定期查看安全设备的日志，及时发现对系统的安全威胁行为。','OTHER');
INSERT INTO `t_rules` VALUES (981048,'检测Dos攻击请求数是否大于0(Dos Protection)','IP:DOS_COUNTER \"@gt 0\"','检测Dos攻击请求数是否大于0(Dos Protection)','CC','block',1,1452647413,NULL,0,'低危','DoS攻击是指故意的攻击网络协议实现的缺陷或直接通过野蛮手段残忍地耗尽被攻击对象的资源，目的是让目标计算机或网络无法提供正常的服务或资源访问，使目标系统服务系统停止响应甚至崩溃，而在此攻击中并不包括侵入目标服务器或目标网络设备。这些服务资源包括网络带宽，文件系统空间容量，开放的进程或者允许的连接。这种攻击会导致资源的匮乏，无论计算机的处理速度多快、内存容量多大、网络带宽的速度多快都无法避免这种攻击带来的后果','建议网络管理员要积极谨慎地维护系统，确保无安全隐患和漏洞。同时强烈建议网络管理员应当定期查看安全设备的日志，及时发现对系统的安全威胁行为。','OTHER');
INSERT INTO `t_rules` VALUES (981049,'检测Dos攻击请求数是否大于或等于用户设置的请求数(Dos Protection)','IP:DOS_COUNTER \"@ge %{tx.dos_counter_threshold}\"','如果Dos攻击请求数大于或等于用户设置的请求数，则设置burst数值(Dos Protection)','CC','block',1,1452647413,NULL,0,'中危','DoS攻击是指故意的攻击网络协议实现的缺陷或直接通过野蛮手段残忍地耗尽被攻击对象的资源，目的是让目标计算机或网络无法提供正常的服务或资源访问，使目标系统服务系统停止响应甚至崩溃，而在此攻击中并不包括侵入目标服务器或目标网络设备。这些服务资源包括网络带宽，文件系统空间容量，开放的进程或者允许的连接。这种攻击会导致资源的匮乏，无论计算机的处理速度多快、内存容量多大、网络带宽的速度多快都无法避免这种攻击带来的后果','建议网络管理员要积极谨慎地维护系统，确保无安全隐患和漏洞。同时强烈建议网络管理员应当定期查看安全设备的日志，及时发现对系统的安全威胁行为。','OTHER');
INSERT INTO `t_rules` VALUES (981050,'检测公开的代理服务器是否被滥用或捆绑（Proxy Abuse）','GEO:COUNTRY_CODE \"!@streq %{tx.geo_x-forwarded-for}\"','如果检测到公开代理服务器被滥用，则阻断访问（Proxy Abuse）','OTHER','block',1,1452647413,NULL,90050,'低危','开放代理滥用','建议web服务器中X-Forwarded-For的地址和请求域名地址处于不同地理位置的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981051,'检测Apache返回的HTTP响应状态码(Slow Dos Protection)','RESPONSE_STATUS \"@streq 408\"','检测Apache返回的HTTP响应状态码是否为408，若为true，则累加ip的slow_dos_counter值(Slow Dos Protection)','OTHER','block',1,1452647413,NULL,90003,'低危','慢攻击的原理就是设法让服务器等待，当服务器在保持连接等待时，消耗了服务器的资源。','建议把服务器连接等待的时间减短。','OTHER');
INSERT INTO `t_rules` VALUES (981052,'检测slow_dos_counter的数值(Slow Dos Protection)','IP:SLOW_DOS_COUNTER \"@gt 5\"','检测slow_dos_counter的值是否大于5，若符合规则，则drop掉数据包(Slow Dos Protection)','OTHER','block',1,1452647413,NULL,90004,'高危','慢攻击的原理就是设法让服务器等待，当服务器在保持连接等待时，消耗了服务器的资源。','建议把服务器连接等待的时间减短。','OTHER');
INSERT INTO `t_rules` VALUES (981053,'检测请求content-type是否为xml（XML ENABLER）','REQUEST_HEADERS:Content-Type \"text/xml\"','如果请求content-type是否为xml，则触发一个xml解析器','OTHER','block',1,1452647413,NULL,90013,'高危','','','OTHER');
INSERT INTO `t_rules` VALUES (981054,'检测提交的会话ID是否有效（Session Hijacking）','REQUEST_COOKIES:\'/(j?sessionid|(php)?sessid|(asp|jserv|jw)?session[-_]?(id)?|cf(id|token)|sid)/\' \".*\"','如果提交的会话ID无效，则阻断访问（Session Hijacking）','OTHER','block',1,1452647413,NULL,90173,'高危','在请求包发送到服务器的如jsessionid|phpsessid|aspsession-id|cftoken等表示session等参数的唯一ID如果是新的，可劫持会话','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981055,'检测提交的会话ID是否有效（Session Hijacking）','&REQUEST_COOKIES:\'/(j?sessionid|(php)?sessid|(asp|jserv|jw)?session[-_]?(id)?|cf(id|token)|sid)/\' \"@eq 0\"','如果提交的会话ID有效，则跳过会话ID检测规则（Session Hijacking）','OTHER','block',1,1452647413,NULL,90172,'中危','在请求包发送到服务器的如jsessionid|phpsessid|aspsession-id|cftoken等表示session等参数的唯一ID如果是新的，可劫持会话','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981056,'初始化会话ID（Session Hijacking）','SecAction \"phase:1,id:\'981056\',t:none,nolog,pass,setuid:%{session.username},setvar:session.sessionid=%{tx.sessionid}\"','初始化会话ID','OTHER','block',1,1452647413,NULL,90175,'中危','','','OTHER');
INSERT INTO `t_rules` VALUES (981057,'检测会话启动时的请求数据，获取ip hash参数值（Session Hijacking）','REMOTE_ADDR \"^(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.)\" ','检测REMOTE_ADDR及TX:1内容，如果匹配规则，则赋值ip hash参数值（Session Hijacking）','OTHER','block',1,1452647413,NULL,90174,'中危','在请求包发送到服务器的如jsessionid|phpsessid|aspsession-id|cftoken等表示session等参数的唯一ID如果是新的，可劫持会话','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981058,'检测会话启动时的请求数据，获取ua hash参数值（Session Hijacking）','REQUEST_HEADERS:User-Agent \".*\"','检测请求头的User-Agent字段内容，如果匹配规则，则赋值ua hash参数值（Session Hijacking）','OTHER','block',1,1452647413,NULL,90177,'中危','在请求包发送到服务器的如jsessionid|phpsessid|aspsession-id|cftoken等表示session等参数的唯一ID如果是新的，可劫持会话','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981059,'检测会话的IP地址是否匹配（Session Hijacking）','TX:IP_HASH \"!@streq %{SESSION.IP_HASH}\"','如果会话的IP地址不匹配，则阻断访问（Session Hijacking）','OTHER','block',1,1452647413,NULL,90176,'高危','把请求包的ip hash 值和在session 集上面保存好的ip hash 的值改变了，可造成会话劫持','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981060,'检测会话的User-Agent是否匹配（Session Hijacking）','TX:UA_HASH \"!@streq %{SESSION.UA_HASH}\"','如果会话的User-Agent不匹配，则阻断访问（Session Hijacking）','OTHER','block',1,1452647413,NULL,90178,'高危','把请求包的ua hash 值和在session 集上面保存好的ip hash 的值改变了，可造成会话劫持','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981061,'检测会话连接时出现的异常个数（Session Hijacking）','TX:STICKY_SESSION_ANOMALY \"@eq 2\"','如果会话的IP地址和User-Agent都不匹配，则阻断访问（Session Hijacking）','OTHER','block',1,1452647413,NULL,90179,'高危','改变了请求中的ua hash和ip hash，将引起会话劫持。','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981062,'检测响应头的Set-Cookie字段（Session Hijacking）','RESPONSE_HEADERS:/Set-Cookie2?/ \"(?i:(j?sessionid|(php)?sessid|(asp|jserv|jw)?session[-_]?(id)?|cf(id|token)|sid).*?=([^\\s].*?)\\;\\s?)\"','检测响应头的Set-Cookie字段数据，设置相关参数：会话ID、IP地址、User-Agent等（Session Hijacking）','OTHER','block',1,1452647413,NULL,90180,'中危','改变了请求中的ua hash和ip hash，将引起会话劫持。','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981063,'检测响应数据中的会话IP地址，获取ip hash参数值（Session Hijacking）','REMOTE_ADDR \"^(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.)\" ','检测响应数据中的会话IP地址，如果匹配规则，则赋值ip hash参数值（Session Hijacking）','OTHER','block',1,1452647413,NULL,90181,'中危','改变了请求中的ua hash和ip hash，将引起会话劫持。','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981064,'检测响应数据中的会话User-Agent地址，获取ua hash参数值（Session Hijacking）','REQUEST_HEADERS:User-Agent \".*\"','检测响应数据中的会话User-Agent地址，如果匹配规则，则赋值ua hash参数值（Session Hijacking）','OTHER','block',1,1452647413,NULL,90171,'低危','改变了请求中的ua hash和ip hash，将引起会话劫持','预防措施包括限制入网的连接和设置你的网络拒绝假冒本地地址从互联网上发来的数据包。\n加密也是有帮助的。如果你必须要允许来自可信赖的主机的外部连接，你可以使用Kerberos或者IPsec工具。使用更安全的协议，FTP和Telnet协议是最容易受到攻击的。SSH是一种很好的替代方法。SSH在本地和远程主机之间建立一个加密的频道。同时，有些网站也用Https代替Http协议。Https在本地和远程主机之间建立一个加密的频道。通过使用IDS或者IPS系统能够改善检测。交换机、SSH等协议和更随机的初始序列号的使用','OTHER');
INSERT INTO `t_rules` VALUES (981078,'检测请求输出数据中的请求参数（CC Known）','ARGS \"@verifyCC (?:^|[^\\d])(\\d{4}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{1,4})(?:[^\\d]|$)\"','检测请求输出数据中的请求参数，若匹配规则，则跳过输入数据CC部分的检测规则，继续处理（CC Known）','OTHER','block',1,1452647413,NULL,90081,'低危','如果发生银行卡卡号密码盗窃行为，会存在GSA SmartPay,MasterCard,Visa,American Express,Diner Club,Discover,JCB等信用卡卡号信息的输入处理，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','','OTHER');
INSERT INTO `t_rules` VALUES (981079,'初始化CC访问请求数据的默认行为是\"继续处理\"（CC Known）','SecAction \"phase:2,id:\'981079\',t:none,pass,nolog,skipAfter:END_KNOWN_CC_INBOUND_CHECK\"','初始化CC访问请求数据的默认行为是“继续处理”,无日志记录，默认跳过END_KNOWN_CC_INBOUND_CHECK规则（CC Known）','OTHER','block',1,1452647413,NULL,90080,'低危','','','OTHER');
INSERT INTO `t_rules` VALUES (981080,'检测CC响应数据中的参数（CC Known）','RESPONSE_BODY|RESPONSE_HEADERS:Location \"@verifyCC (?:^|[^\\d])(?<!google_ad_client = \\\"pub-)(\\d{4}\\-?\\d{4}\\-?\\d{2}\\-?\\d{2}\\-?\\d{1,4})(?:[^\\d]|$)\"','检测CC响应数据中的参数，若匹配规则，则跳过响应数据中CC部分的检测规则，继续处理（CC Known）','OTHER','block',1,1452647413,NULL,90083,'低危','如果发生银行卡卡号密码盗窃行为，会存在GSA SmartPay,MasterCard,Visa,American Express,Diner Club,Discover,JCB等信用卡卡号信息的输入处理，如果攻击者窃取了这些数据是非常的危险的，甚至会利用一系列信息进行欺诈。','','OTHER');
INSERT INTO `t_rules` VALUES (981081,'初始化CC响应数据的默认行为是\"继续处理\"（CC Known）','SecAction \"phase:4,id:\'981081\',t:none,pass,nolog,skipAfter:END_KNOWN_CC_OUTBOUND_CHECK\"','初始化CC访问响应数据的默认行为是“继续处理”,无日志记录，默认跳过END_KNOWN_CC_OUTBOUND_CHECK规则（CC Known）','OTHER','block',1,1452647413,NULL,90084,'低危','','','OTHER');
INSERT INTO `t_rules` VALUES (981082,'初始化资源收集的默认行为是\"继续处理\"（AppSensor Detection）','SecAction \"phase:1,id:\'981082\',t:none,nolog,pass,initcol:resource=%{request_headers.host}_%{request_filename},setvar:resource.min_pattern_threshold=50,setvar:resource.min_traffic_threshold=100\"','初始化资源收集的默认行为是\"继续处理\"，无日志记录，初始化相关参数（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90120,'低危','','','OTHER');
INSERT INTO `t_rules` VALUES (981085,'检测esource.enforce_profile的参数是否为0（AppSensor Detection）','&RESOURCE:ENFORCE_RE_PROFILE \"@eq 0\"','如果esource.enforce_profile参数为0，则跳过profile enforcement规则检测（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90033,'低危','攻击者利用请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981086,'检测esource.enforce_profile的参数是否为1（AppSensor Detection）','&RESOURCE:ENFORCE_RE_PROFILE \"@eq 1\"','如果esource.enforce_profile参数为1，则执行对应文件appsensor_request_exception_enforce.lua（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90031,'低危','攻击者利用请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981087,'检测是否调用了不支持的http请求方法（AppSensor Detection）','REQUEST_METHOD \"!@within HEAD GET POST PUT DELETE TRACE OPTIONS CONNECT\"','如果调用了不支持的http请求方法，则阻断，并记录（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90032,'低危','攻击者会利用HEAD GET POST PUT DELETE TRACE OPTIONS CONNECT等正常请求方式意外的方式访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981088,'检测请求方法是否不合规范（AppSensor Detection）','TX:REQUEST_METHOD_VIOLATION \"@eq 1\"','如果存在不合规范的请求方法，则阻断访问，并设置相关参数（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90034,'低危','攻击者会利用HEAD GET POST PUT DELETE TRACE OPTIONS CONNECT等正常请求方式意外的方式访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981089,'检测请求中是否缺少参数（AppSensor Detection）','TX:MIN_NUM_ARGS_VIOLATION \"@eq 1\"','如果请求中缺少参数，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90035,'低危','攻击者会利用请求参数缺失的请求访问网站。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981090,'检测请求中是否有额外参数（AppSensor Detection）','TX:MAX_NUM_ARGS_VIOLATION \"@eq 1\"','如果请求中有额外参数，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90020,'低危','攻击者会利用请求参数缺失的请求访问网站。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981091,'检测请求参数的名称（AppSensor Detection）','TX:ARGS_NAMES_VIOLATION \".*\"','如果请求参数的名称违反规定，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90019,'低危','攻击者会利用无效的参数名访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981092,'检测请求参数的长度是否比正常范围小（AppSensor Detection）','TX:/^ARGS.*_MIN_LENGTH_VIOLATION/ \".*\" ','如果请求参数的长度比正常范围小，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90022,'低危','攻击者会利用参数的值的过小字节长度违例的请求，访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981093,'检测请求参数的长度是否比正常范围大（AppSensor Detection）','TX:/^ARGS.*_MAX_LENGTH_VIOLATION/ \".*\"','如果请求参数的长度比正常范围大，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90021,'低危','攻击者会利用参数的值的过大字节长度违例的请求，访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981094,'检测请求参数中是否包含意料之外的Digits字符（AppSensor Detection）','TX:/^ARGS.*_digits_violation/ \".*\"','如果请求参数中包含意料之外的Digits字符，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90016,'低危','攻击者利用参数包含了违规的数字访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981095,'检测请求参数中是否包含意料之外的Alpha字符（AppSensor Detection）','TX:/^ARGS.*_alpha_violation/ \".*\"','如果请求参数中包含意料之外的Alpha字符，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90015,'低危','攻击者利用参数包含了违规的字母访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981096,'检测请求参数中是否包含意料之外的AlphaNumeric字符（AppSensor Detection）','TX:/^ARGS.*_alphanumeric_violation/ \".*\"','如果请求参数中包含意料之外的AlphaNumeric字符，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90018,'低危','攻击者利用参数包含了违规的字母或数字访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981097,'检测请求参数中是否包含意料之外的Email字符（AppSensor Detection）','TX:/^ARGS.*_email_violation/ \".*\"','如果请求参数中包含意料之外的Email字符，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90017,'低危','攻击者利用无效的邮箱访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981098,'初始化配置文件分析阶段访问行为默认了\"仅检测\"（AppSensor Detection）','SecAction \"phase:5,id:\'981098\',t:none,nolog,pass,ctl:ruleEngine=DetectionOnly\"','初始化配置文件分析阶段访问行为默认了\"仅检测\"，无日志记录（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90024,'低危','','','OTHER');
INSERT INTO `t_rules` VALUES (981099,'检测请求状态码是不是404（AppSensor Detection）','RESPONSE_STATUS \"^404$\"','如果请求状态码是404，则设置resource.KEY值为FLASE，并跳过profile analysis规则检测（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90023,'低危','攻击者会利用爬虫、扫描工具访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981100,'检测请求状态码是否以4或5开头的（AppSensor Detection）','RESPONSE_STATUS \"^(5|4)\"','如果请求状态码是以4或5开头的，则跳过profile analysis规则检测（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90030,'低危','攻击者会利用爬虫、扫描工具访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981101,'检测请求中的ANOMALY_SCORE的数值是否不为0（AppSensor Detection）','TX:ANOMALY_SCORE \"!@eq 0\" ','如果请求中的ANOMALY_SCORE的数值不为0，则跳过profile analysis规则检测（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90029,'低危','攻击者访问服务器会带有一系列的违规行为。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981102,'检测请求源中的ENFORCE_RE_PROFILE是否为1（AppSensor Detection）','&RESOURCE:ENFORCE_RE_PROFILE \"@eq 1\" ','如果请求源中的ENFORCE_RE_PROFILE为1，则跳过profile analysis规则检测（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90028,'低危','攻击者利用请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981103,'检测请求参数中是否包含意料之外的Path字符类（AppSensor Detection）','TX:/^ARGS.*_path_violation/ \".*\"','如果请求参数中包含意料之外的Path字符，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90027,'低危','攻击者利用无效的路径，访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981104,'检测请求参数中是否包含意料之外的URL字符类（AppSensor Detection）','TX:/^ARGS.*_url_violation/ \".*\"','如果请求参数中包含意料之外的URL字符，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90026,'低危','攻击者利用无效的URL，访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981105,'检测请求参数中是否包含意料之外的SafeText字符类（AppSensor Detection）','TX:/^ARGS.*_safetext_violation/ \".*\"','如果请求参数中包含意料之外的SafeText字符，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90025,'低危','攻击者利用错误的文本访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981110,'检测请求参数中是否包含意料之外的Flag字符类（AppSensor Detection）','TX:/^ARGS.*_flag_violation/ \".*\"','如果请求参数中包含意料之外的Flag字符，则阻断访问（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90014,'低危','攻击者利用参数包含了违规的字符访问服务器。','建议web服务器对请求方法，参数个数，参数名字，参数长度，参数字符等常见的属性违例的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981131,'检测AppSensor里的DEBUG参数（AppSensor Detection）','ARGS:DEBUG \"!@streq false\" ','如果AppSensor里的DEBUG参数不为false，则阻断，并记录（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90008,'低危','黑客对蜜罐设置的陷阱的隐藏参数篡改。','建议在web服务器对debug参数的内容进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981132,'在stream_output_body中添加一个假的\"debug\"参数（AppSensor Detection）','STREAM_OUTPUT_BODY \"@rsub s/<\\/form>/<input type=\\\"hidden\\\" name=\\\"debug\\\" value=\\\"false\\\"><\\/form>/\" ','在stream_output_body中添加一个假的\"debug\"参数（AppSensor Detection）','OTHER','block',1,1452647413,NULL,90007,'低危','黑客对蜜罐设置的陷阱的隐藏参数篡改。','建议在web服务器对debug参数的内容进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981133,'检测请求内容是否符合通用攻击规则（Generic Attacks）','REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/|REQUEST_COOKIES_NAMES|ARGS_NAMES|ARGS|XML:/* \"@pmFromFile modsecurity_40_generic_attacks.data\" ','如果请求内容符合通用攻击规则，则累计pm_score数值（Generic Attacks）','GENERIC','block',0,1452647413,NULL,90156,'低危','攻击者通过通用的攻击方式对服务器进行试探','建议在web服务器对这种试探次数进行累计','GENERIC');
INSERT INTO `t_rules` VALUES (981134,'检测参数pm_score值是否为0（Generic Attacks)','TX:PM_SCORE \"@eq 0\"','如果参数pm_score值为0，则跳过END_PM_CHECK规则，无日志记录（Generic Attacks)','GENERIC','block',0,1452647413,NULL,90155,'低危','攻击者通过通用的攻击方式对服务器进行试探','建议在web服务器对这种试探次数进行累计','GENERIC');
INSERT INTO `t_rules` VALUES (981136,'常规异常检测','@pm jscript onsubmit copyparentfolder document javascript meta onchange onmove onkeydown onkeyup activexobject onerror onmouseup ecmascript bexpression onmouseover vbscript: <![cdata[ http: .innerhtml settimeout shell: onabort asfunction: onkeypress onmou','','XSS','pass',0,1395124100,NULL,8003,'高危','当cookies或请求参数或xml中出现如 jscript onsubmit copyparentfolder document javascript meta onchange onmove onkeydown onkeyup activexobject onerror onmouseup ecmascript bexpression onmouseover vbscript: <![cdata[ http: .innerhtml settimeout shell: onabort asfunction','建议在web服务器添加对含有jscript onsubmit copyparentfolder document javascript meta onchange onmove onkeydown onkeyup activexobject onerror onmouseup ecmascript bexpression onmouseover vbscript: <![cdata[ http: .innerhtml settimeout shell: onabort asfunction: onkeyp','XSS');
INSERT INTO `t_rules` VALUES (981137,'检测是否启用预先黑名单检测（Comment Spam）','IP:PREVIOUS_RBL_CHECK \"@eq 1\"','如果启用了预先黑名单检测，则跳过黑名单查找规则END_RBL_LOOKUP（Comment Spam）','OTHER','pass',1,1452647413,NULL,90162,'低危','垃圾评论是一种攻击，对象是对博客、论坛、留言板等会接受并显示游客提供的超级链接的交互网页。\n这些垃圾评论制造者会专门发送一些自动的、随意的评论，并会携带一个链接到攻击者的站点，然后这些链接就会被人工的提高了在网站的搜索引擎中的排名，从而在网站的搜索结果中更加明显','建议使用第三方反垃圾系统。垃圾评论 90% 以上都是由机器人产生的，因此使用验证码也可以过滤掉大部分的垃圾评论。','OTHER');
INSERT INTO `t_rules` VALUES (981138,'检测垃圾评论数据来源是否符合预先黑名单（Comment Spam）','REMOTE_ADDR \"@rbl sbl-xbl.spamhaus.org\"','如果垃圾评论URL来源处于预先的黑名单，则跳过黑名单检测规则END_RBL_CHECK，并记录日志（Comment Spam）','OTHER','pass',1,1452647413,NULL,90160,'高危','垃圾评论是一种攻击，对象是对博客、论坛、留言板等会接受并显示游客提供的超级链接的交互网页。\n这些垃圾评论制造者会专门发送一些自动的、随意的评论，并会携带一个链接到攻击者的站点，然后这些链接就会被人工的提高了在网站的搜索引擎中的排名，从而在网站的搜索结果中更加明显','建议使用第三方反垃圾系统。垃圾评论 90% 以上都是由机器人产生的，因此使用验证码也可以过滤掉大部分的垃圾评论。','OTHER');
INSERT INTO `t_rules` VALUES (981139,'设置默认的预先黑名单参数值（Comment Spam）','SecAction \"phase:1,id:\'981139\',t:none,nolog,pass,setvar:ip.previous_rbl_check=1,expirevar:ip.previous_rbl_check=86400\"','设置默认的预先黑名单参数值（Comment Spam）','OTHER','pass',1,1452647413,NULL,90161,'高危','','','OTHER');
INSERT INTO `t_rules` VALUES (981140,'检测是否有黑名单中的请求来源（Comment Spam）','IP:SPAMMER \"@eq 1\"','如果有黑名单中的请求来源，则设置相关数值（Comment Spam)','OTHER','pass',1,1452647413,NULL,90164,'高危','垃圾评论是一种攻击，对象是对博客、论坛、留言板等会接受并显示游客提供的超级链接的交互网页。\n这些垃圾评论制造者会专门发送一些自动的、随意的评论，并会携带一个链接到攻击者的站点，然后这些链接就会被人工的提高了在网站的搜索引擎中的排名，从而在网站的搜索结果中更加明显','建议使用第三方反垃圾系统。垃圾评论 90% 以上都是由机器人产生的，因此使用验证码也可以过滤掉大部分的垃圾评论。','OTHER');
INSERT INTO `t_rules` VALUES (981142,'检测请求是否为CSP Violation Report Request（CSP Enforcement）','REQUEST_FILENAME \"@streq %{tx.csp_report_uri}\" ','如果请求为CSP Violation Report Request，则打开功能：forceRequestBodyVariable（CSP Enforcement）','OTHER','block',1,1452647413,NULL,90010,'高危','如果请求是CSP Violation Report，waf会启动请求体检测。因为content-type是json的话，请求体的检测默认是关闭的。','','OTHER');
INSERT INTO `t_rules` VALUES (981143,'检测是否缺少CSRF Token(CSRF Protection)','&ARGS:CSRF_TOKEN \"!@eq 1\"','如果缺少CSRF Token，则阻断访问(CSRF Protection)','OTHER','block',1,1452647413,NULL,90110,'低危','攻击者盗用了你的身份，以你的名义发送恶意请求。CSRF能够做的事情包括：以你名义发送邮件，发消息，盗取你的账号，甚至于购买商品，虚拟货币转账......造成的问题包括：个人隐私泄露以及财产安全。','','OTHER');
INSERT INTO `t_rules` VALUES (981144,'检测是否Token是否有效(CSRF Protection)','ARGS:CSRF_TOKEN \"!@streq %{SESSION.CSRF_TOKEN}\"','如果Token无效，则阻断访问(CSRF Protection)','OTHER','block',1,1452647413,NULL,90112,'低危','攻击者盗用了你的身份，以你的名义发送恶意请求。CSRF能够做的事情包括：以你名义发送邮件，发消息，盗取你的账号，甚至于购买商品，虚拟货币转账......造成的问题包括：个人隐私泄露以及财产安全。','','OTHER');
INSERT INTO `t_rules` VALUES (981145,'检测是否需要内容注入到CSRF Token(CSRF Protection)','&SESSION:CSRF_TOKEN \"@eq 1\"','如果需要，则附加相关内容到CSRF Token(CSRF Protection)','OTHER','block',1,1452647413,NULL,90111,'低危','攻击者盗用了你的身份，以你的名义发送恶意请求。CSRF能够做的事情包括：以你名义发送邮件，发消息，盗取你的账号，甚至于购买商品，虚拟货币转账......造成的问题包括：个人隐私泄露以及财产安全。','','OTHER');
INSERT INTO `t_rules` VALUES (981172,'SQL注入字符的异常使用检测','([\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\+\\=\\{\\}\\[\\]\\|\\:\\;\\\"\\\'\\´\\’\\‘\\`\\<\\>].*?){8,}([\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\+\\=\\{\\}\\[\\]\\|\\:\\;\\\"\\\'\\´\\’\\‘\\`\\<\\>].*?){8,}','通过探测在COOKIE中出现:#*%$!等字符的次数来判断是否存在注入风险','SQLI','block',0,1395124100,NULL,1030,'低危','在cookies和请求参数和xml中利用~!@#$%^&*()-+={}|\"\'[]等字符多于8次，攻击者可尝试利用字符实施SQL注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有~!@#$%^&*()-+={}|\"\'[]等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981173,'SQL注入字符的异常使用检测','([\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\+\\=\\{\\}\\[\\]\\|\\:\\;\\\"\\\'\\´\\’\\‘\\`\\<\\>].*?){4,}','通过探测URL参数中传递的值是否出现：#*%!等字符超出预期次数，来判断注入风险','SQLI','block',0,1395124100,NULL,1031,'低危','当请求参数和xml中如!~#$%{}:;\'><&=+等字符多次出现，攻击者可尝试利用敏感的字符绕过防火墙，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有多个 !~#$%{}:;\'><&=+ 字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981175,'检测入站数据是否有以开源漏洞数据库（OSVDB）中标记的资源为目标的攻击（Inbound Blocking）','TX:ANOMALY_SCORE \"@gt 0\" \nRESOURCE:OSVDB_VULNERABLE \"@eq 1\"\nTX:ANOMALY_SCORE_BLOCKING \"@streq on\"\n','如果有入站攻击，则拒绝访问，并记录日志（Inbound Blocking）','OTHER','deny',1,1452647413,NULL,90122,'低危','攻击者以开源漏洞数据库中标记的资源为目标攻击，能快速的找到目标所存在的漏洞','建议在web服务器限制访问开源漏洞数据库中标记的资源的请求的次数','OTHER');
INSERT INTO `t_rules` VALUES (981176,'检测入站数据异常分数是否溢出（Inbound Blocking）','TX:ANOMALY_SCORE \"@gt 0\"','如果异常分数溢出，则拒绝访问，并记录日志（Inbound Blocking）','OTHER','block',1,1452647413,NULL,90121,'低危','攻击者使用多次异常的数据对服务器进行试探，通过响应信息得到服务器的敏感信息','建议在web服务器限制异常访问的次数','OTHER');
INSERT INTO `t_rules` VALUES (981177,'检测出站数据是否有Iframe注入攻击（OutBound）','RESPONSE_BODY \"!@pm iframe\"','检测响应体数据是否含有iframe短语，如果没有，则跳过Iframe规则检测（OutBound）','OTHER','block',1,1452647413,NULL,90039,'低危','当cookies或请求参数或xml中出现如Iframe等字符的时候，需要注意是否受到了XSS攻击，作为一种经常出现在web应用中最主流的攻击方式，攻击者可利用此攻击将恶意代码植入到提供给其他用户使用的页面中，甚至可化身为网络钓鱼攻击或者获取cookie并利用。','建议在web服务器对含有iframe的信息进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (981178,'检测出站数据是否有modsecurity_50_outbound.data文件中列出的短语（OutBound）',' !@pmFromFile modsecurity_50_outbound.data','如果响应体数据没有modsecurity_50_outbound.data文件中列出的短语，则跳过OutBound规则检测(OutBound)','OTHER','block',1,1452647413,NULL,90040,'低危','攻击者可以通过服务器返回的信息，进一步获取敏感信息','建议在web服务器对返回信息进行过滤，控制服务器返回的内容','OTHER');
INSERT INTO `t_rules` VALUES (981180,'检测XSS数据是否在全局变量列表里（Application Defects）','GLOBAL:\'/XSS_LIST_.*/\' \"@streq %{tx.inbound_meta-characters}\"','如果XSS数据已经在全局变量列表里，则跳过规则（Application Defects）','OTHER','block',1,1452647413,NULL,90149,'低危','攻击者向有XSS漏洞的网站中输入(传入)恶意的HTML代码，当其它用户浏览该网站时，这段HTML代码会自动执行，从而达到攻击的目的。如，盗取用户Cookie、破坏页面结构、重定向到其它网站等。','建议在web服务器对用户的输入进行处理，只允许输入合法的值，其它值一概过滤掉，对标签进行转换','OTHER');
INSERT INTO `t_rules` VALUES (981181,'检测请求数据中的INBOUND_META-CHARACTERS是否匹配规则（Application Defects）','TX:INBOUND_META-CHARACTERS \".*\"','如果匹配，则设置global的XSS列表参数（Application Defects）','OTHER','block',1,1452647413,NULL,90148,'低危','攻击者向有XSS漏洞的网站中输入(传入)恶意的HTML代码，当其它用户浏览该网站时，这段HTML代码会自动执行，从而达到攻击的目的。如，盗取用户Cookie、破坏页面结构、重定向到其它网站等。','建议在web服务器对用户的输入进行处理，只允许输入合法的值，其它值一概过滤掉，对标签进行转换','OTHER');
INSERT INTO `t_rules` VALUES (981182,'检测响应数据中是否包含已知的恶意字符（Application Defects）','GLOBAL:\'/XSS_LIST_.*/\' \"@within %{response_body}\" ','检测响应数据中是否包含已知的恶意字符，如果有，则记录日志（Application Defects）','OTHER','block',1,1452647413,NULL,90147,'低危','攻击者会利用请求中带有恶意的没有编码说明的元字符的请求访问服务器。','建议web服务器带有恶意的没有编码说明的元字符的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981184,'检测响应数据中是否缺少Cookie\'s HttpOnly标志（Application Defects）','RESPONSE_HEADERS:/Set-Cookie2?/ \"(.*?)=(?i)(?!.*httponly.*)(.*$)\"','如果响应数据中缺少Cookie\'s HttpOnly标志，则记录日志（Application Defects）','OTHER','block',1,1452647413,NULL,90146,'低危','攻击者会使用缺少http cookie是唯一的标志的请求访问服务器。','建议web服务器把http cookie不是唯一的标志的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981185,'检测响应数据中是否缺少Cookie\'s Secure标志（Application Defects）','RESPONSE_HEADERS:/Set-Cookie2?/ \"(.*?)=(?i)(?!.*secure.*)(.*$)\"','如果响应数据中缺少Cookie\'s Secure标志，则记录日志（Application Defects）','OTHER','block',1,1452647413,NULL,90145,'低危','攻击者会使用缺少http cookie安全的的标志的请求访问服务器。','建议web服务器把没有http cookie安全的的标志的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981187,'通过profile_page_scripts.lua脚本检测响应数据是否匹配规则（Response Profiling）','SecRuleScript profile_page_scripts.lua \"phase:4,id:\'981187\',t:none,nolog,pass\"','通过profile_page_scripts.lua脚本检测响应数据是否匹配规则（Response Profiling）','OTHER','block',1,1452647413,NULL,90101,'低危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981188,'检测资源集合中的参数是否包含有profile page的组成因素(niframes、nscripts、nlinks、nimages）（Response Profiling）','&RESOURCE:\'/(niframes|nscripts|nlinks|nimages)/\' \"@eq 0\"','如果资源集合中的参数没有profile page的组成因素，则跳过Profile Page规则检测（Response Profiling）','OTHER','pass',1,1452647413,NULL,90100,'中危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981189,'检测资源集合中是否包含有事务集合参数NIFRAMES（Response Profiling）','TX:NIFRAMES \"@eq %{resource.niframes}','如果资源集合中包含有事务集合参数NIFRAMES，则累计资源可信参数resource.profile_confidence_counter（Response Profiling）','OTHER','pass',1,1452647413,NULL,90099,'中危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981190,'检测资源集合中是否包含有事务集合参数NSCRIPTS（Response Profiling）','TX:NSCRIPTS \"@eq %{resource.nscripts}\"','如果资源集合中包含有事务集合参数NSCRIPTS，则累计资源可信参数resource.profile_confidence_counter（Response Profiling）','OTHER','pass',1,1452647413,NULL,90093,'中危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981191,'检测资源集合中是否包含有事务集合参数NLINKS（Response Profiling）','TX:NLINKS \"@eq %{resource.nlinks}\" ','如果资源集合中包含有事务集合参数NLINKS，则累计资源可信参数resource.profile_confidence_counter（Response Profiling）','OTHER','pass',1,1452647413,NULL,90094,'中危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981192,'检测资源集合中是否包含有事务集合参数NIMAGES（Response Profiling）','TX:NIMAGES \"@eq %{resource.nimages}\"','如果资源集合中包含有事务集合参数NIMAGES，则累计资源可信参数resource.profile_confidence_counter（Response Profiling）','OTHER','pass',1,1452647413,NULL,90095,'中危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981193,'检测资源集合中的PROFILE_CONFIDENCE_COUNTER数值是否少于等于40（Response Profiling）','RESOURCE:PROFILE_CONFIDENCE_COUNTER \"@lt 40\"','如果资源集合中的PROFILE_CONFIDENCE_COUNTER数值少于等于40，则跳过Profile Page 规则检测（Response Profiling）','OTHER','pass',1,1452647413,NULL,90096,'低危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981194,'检测页面的IFRAMES参数值是否改变（Response Profiling）','TX:NIFRAMES \"!@eq %{resource.niframes}\"','如果页面的IFRAMES参数值发生改变，则阻断访问，并累计相关异常分数（Response Profiling）','OTHER','block',1,1452647413,NULL,90097,'高危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981195,'检测页面的NSCRIPTS参数值是否改变（Response Profiling）','TX:NSCRIPTS \"!@eq %{resource.nscripts}\"','如果页面的NSCRIPTS参数值发生改变，则阻断访问，并累计相关异常分数（Response Profiling）','OTHER','block',1,1452647413,NULL,90098,'高危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981196,'检测页面的NLINKS参数值是否改变（Response Profiling）','TX:NLINKS \"!@eq %{resource.nlinks}\" ','如果页面的NLINKS参数值发生改变，则阻断访问，并累计相关异常分数（Response Profiling）','OTHER','block',1,1452647413,NULL,90091,'高危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981197,'检测页面的NIMAGES参数值是否改变（Response Profiling）','TX:NIMAGES \"!@eq %{resource.nimages}\"','如果页面的NIMAGES参数值发生改变，则阻断访问，并累计相关异常分数（Response Profiling）','OTHER','block',1,1452647413,NULL,90092,'高危','利用<script|<iframe|a href|<img等网页的字符、标签的改动，攻击者可恶意的篡改了服务器网页的内容','建议定时对网页、数据库等重要文件经常备份，日常需要多维护。一旦发现入侵，及时还原备份信息。','OTHER');
INSERT INTO `t_rules` VALUES (981198,'检测http状态码及开源漏洞数据库(OSVDB）参数状态（Pvi Checks）','&RESOURCE:OSVDB_CHECK \"@eq 0\" RESPONSE_STATUS \"@streq 200\"','如果OSVDB的参数OSVDB_CHECK为0且响应状态码为200，则执行osvdb.lua脚本进行规则匹配检测（Pvi Checks）','OTHER','pass',1,1452647413,NULL,90051,'高危','当检测到OSVDB_CHECK为0，返回状体是200，将会启动一些相关的检测脚本。','缺少了一个vulnerabilities.txt','OTHER');
INSERT INTO `t_rules` VALUES (981199,'检测事务集合参数OSVDB_MSG（Pvi Checks）','X:OSVDB_MSG \"!^$\"','如果事务集合参数OSVDB_MSG匹配规则，则表示检测到漏洞，记录日志信息（Pvi Checks）','OTHER','pass',1,1452647413,NULL,90052,'高危','当检测到OSVDB_MSG不为空。','','OTHER');
INSERT INTO `t_rules` VALUES (981200,'检测输出数据的异常分数及异常分数阻断标志参数(Outbound Blocking)','TX:OUTBOUND_ANOMALY_SCORE \"@ge %{tx.outbound_anomaly_score_level}\"   TX:ANOMALY_SCORE_BLOCKING \"@streq on\" ','如果输出数据的异常分数大于或等于设定的异常分数水平并且开启了异常分数阻断标志，则拒绝访问，并记录日志(Outbound Blocking)','OTHER','pass',1,1452647413,NULL,90170,'低危','攻击者通过足够多的服务器反馈的信息能获得服务器的一些敏感信息','建议在web服务器限制异常信息反馈的次数','OTHER');
INSERT INTO `t_rules` VALUES (981201,'检测关联成功的攻击(Correlation)','TX:\'/LEAKAGE\\\\\\/ERRORS/\' \"@ge 1\"','如果事务集合中以LEAKAGE及ERRORS开头的参数值大于或等于1，则跳过Correlated Attack 规则检测(Correlation)','OTHER','pass',1,1452647413,NULL,90107,'低危','信息泄露会暴露了服务器的敏感信息，使攻击者能够通过泄露的信息进行进一步入侵。','做好对服务器的信息的加密、保护。','OTHER');
INSERT INTO `t_rules` VALUES (981202,'检测关联尝试的攻击(Correlation)',' &TX:\'/AVAILABILITY\\\\\\/APP_NOT_AVAIL/\' \"@ge 1\"','如果事务集合中以AVAILABILITY及APP_NOT_AVAIL开头的参数值大于或等于1，则跳过Correlated Attack 规则检测(Correlation)','OTHER','pass',1,1452647413,NULL,90108,'低危','信息泄露会暴露了服务器的敏感信息，使攻击者能够通过泄露的信息进行进一步入侵。','做好对服务器的信息的加密、保护。','OTHER');
INSERT INTO `t_rules` VALUES (981203,'检测入站数据的异常总分数1(Correlation)','TX:INBOUND_ANOMALY_SCORE \"@gt 0\" ','如果入站数据异常总分数大于0且少于设置的异常分数水平，则跳过Correlated Attack 规则检测(Correlation)','OTHER','pass',1,1452647413,NULL,90109,'低危','攻击者频繁的对服务器进行违规的操作，不加以措施应对，将会引起更为严重的后果。','建议web服务器设置实时黑名单机制，过滤高频违规操作的请求id。','OTHER');
INSERT INTO `t_rules` VALUES (981204,'检测入站数据的异常总分数2(Correlation)','TX:INBOUND_ANOMALY_SCORE \"@ge %{tx.inbound_anomaly_score_level}\" ','如果入站数据异常总分数大于或等于设置的异常分数水平，则跳过Correlated Attack 规则检测(Correlation)','OTHER','pass',1,1452647413,NULL,90105,'低危','攻击者频繁的对服务器进行违规的操作，不加以措施应对，将会引起更为严重的后果。','建议web服务器设置实时黑名单机制，过滤高频违规操作的请求id。','OTHER');
INSERT INTO `t_rules` VALUES (981205,'检测出站数据的异常总分数(Correlation)','TX:OUTBOUND_ANOMALY_SCORE \"@ge %{tx.outbound_anomaly_score_level}\"','如果出站数据异常总分数大于或等于设置的异常分数水平，则跳过Correlated Attack 规则检测(Correlation)','OTHER','pass',1,1452647413,NULL,90106,'低危','攻击者让服务器频繁的发送出去敏感的信息，是非常危险的。','做好对服务器的信息的加密、保护。','OTHER');
INSERT INTO `t_rules` VALUES (981219,'检测GLOBAL集合的参数MISSING_CHARSET是否为0 （Response Profiling）','&GLOBAL:MISSING_CHARSET \"@eq 0\" ','如果GLOBAL集合的参数MISSING_CHARSET为0 ，则设置参数global.missing_charset=0（Response Profiling）','OTHER','pass',1,1452647413,NULL,90124,'低危','攻击者会利用缺少Content-Type或者使HTML没有元标签的请求访问服务器。','建议web服务器对确实或没有明确指明字符编码的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981220,'检测正常返回的xml类型响应数据是否缺少字符集（Application Defects）','GLOBAL:MISSING_CHARSET \"@le 10\"','MISSING_CHARSET少于等于10，说明正常返回的xml类型响应数据缺少字符（Application Defects）','OTHER','pass',1,1452647413,NULL,90140,'低危','攻击者会利用缺少Content-Type或者使HTML没有元标签的请求访问服务器。','建议web服务器对确实或没有明确指明字符编码的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981221,'检测GLOBAL集合的参数CHARSET_NOT_UTF8是否为0（Application Defects）','&GLOBAL:CHARSET_NOT_UTF8 \"@eq 0\" ','如果GLOBAL集合的参数CHARSET_NOT_UTF8为0 ，则设置参数global.charset_not_utf8=0（Application Defects）','OTHER','pass',1,1452647413,NULL,90141,'低危','攻击者会利用Content-Type或者使HTML元标签的不指明使用了UTF-8编码的请求访问服务器。','建议web服务器对确实或没有明确指明字符编码的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981222,'检测正常返回的Html/xml类型响应数据是否明确设置UTF-8（Application Defects）','GLOBAL:CHARSET_NOT_UTF8 \"@le 10\"','CHARSET_NOT_UTF8少于等于10，说明正常返回的Html/xml类型响应数据没有明确设置UTF-8（Application Defects）','OTHER','pass',1,1452647413,NULL,90138,'低危','攻击者会利用Content-Type或者HTML元标签的不指明使用了UTF-8编码的请求访问服务器。','建议web服务器对确实或没有明确指明字符编码的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981223,'检测GLOBAL集合的参数CHARSET_MISMATCH是否为0 （Application Defects）','&GLOBAL:CHARSET_MISMATCH \"@eq 0\"','如果GLOBAL集合的参数CHARSET_MISMATCH为0 ，则设置参数global.charset_mismatch=0（Application Defects）','OTHER','pass',1,1452647413,NULL,90139,'低危','攻击者会使Content-Type和HTML元标签的指明编码不一样的请求访问服务器。','建议web服务器对Content-Type和HTML元标签的指明编码不一样的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981224,'检测正常返回的Html/xml类型响应数据的头部字符集和Html/xml响应体字符集是否一致（Application Defects）','GLOBAL:CHARSET_MISMATCH \"@le 10\"','CHARSET_MISMATCH少于等于10，说明正常返回的Html/xml类型响应数据的头部字符集和Html/xml响应体字符集不一致（Application Defects）','OTHER','pass',1,1452647413,NULL,90142,'低危','攻击者会使Content-Type和HTML元标签的指明编码不一样的请求访问服务器。','建议web服务器对Content-Type和HTML元标签的指明编码不一样的请求过滤。','OTHER');
INSERT INTO `t_rules` VALUES (981227,'multipart/form-data内容逃避','[\'\\\";=]','该规则检测在请求中利用Content-Disposition:头来偷传multipart/form-data的情况，比如：Content-Disposition: form-data; name=\"fileRap\"; filename=\"file=.txt\"','PROTOCOL','block',0,1395124100,NULL,4002,'低危','攻击者可以使用multipart/form-data 格式发送payload。对于应用来说，和使用 application/x-www-form-urlencoded 获取到的数据是一致的','','PROTOCOL');
INSERT INTO `t_rules` VALUES (981231,'探测SQL注释符号','(/\\*!?|\\*/|[\';]--|--[\\s\\r\\n\\v\\f]|(?:--[^-]*?-)|([^\\-&])#.*?[\\s\\r\\n\\v\\f]|;?\\\\x00)','探测常见的SQL脚本中的注释字符，如-- /**/等','SQLI','block',0,1395124100,NULL,1001,'低危','在cookies和请求参数和xml中利用 exec xp_cmdshell|\\ ?! \\|from%$information_schema#|union select@等字符，这些字符是SQL的注释符号，攻击者可以注释掉一些sql语句，然后让其只执行攻击语句而达到入侵目的。一旦入侵成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有exec xp_cmdshell|\\ ?! \\|from%$information_schema#|union select@等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981235,'检测全局集合中的MISSING_HTTPONLY参数值是否为0（Application Defects）','&GLOBAL:MISSING_HTTPONLY \"@eq 0\"','如果MISSING_HTTPONLY参数值为0，则设置参数global.missing_httponly=0（Application Defects）','OTHER','block',1,1452647413,NULL,90125,'低危','攻击者会使用缺少http cookie是唯一的标志的请求访问服务器。','建议web服务器把http cookie不是唯一的标志的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981236,'检测全局集合中的MISSING_SECURE参数值是否为0（Application Defects）','&GLOBAL:MISSING_SECURE \"@eq 0\"','如果MISSING_SECURE参数值为0，则设置参数global.missing_secure=0（Application Defects）','OTHER','block',1,1452647413,NULL,90127,'低危','攻击者会使用缺少http cookie是安全的的标志的请求访问服务器。','建议web服务器把没有http cookie安全的的标志的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981237,'检测全局集合中的LOOSE_DOMAIN_SCOPE参数值是否为0（Application Defects）','&GLOBAL:LOOSE_DOMAIN_SCOPE \"@eq 0\"','如果LOOSE_DOMAIN_SCOPE参数值为0，则设置参数global.loose_domain_scope=0（Application Defects）','OTHER','block',1,1452647413,NULL,90126,'低危','攻击者会使用域名和cookie的标志不同的请求访问服务器。','建议web服务器把使用域名和cookie标志不同的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981238,'检测cookies内容（Application Defects）','GLOBAL:LOOSE_DOMAIN_SCOPE \"@le 10\"','检测cookies内容（Application Defects）','OTHER','block',1,1452647413,NULL,90129,'低危','攻击者会使用域名和cookie的标志不同的请求访问服务器。','建议web服务器把使用域名和cookie标志不同的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981239,'检测全局集合中的CHECK_CACHE_CONTROL参数值是否为0（Application Defects）','&GLOBAL:CHECK_CACHE_CONTROL \"@eq 0\"','如果CHECK_CACHE_CONTROL参数值为0，则设置参数global.check_cache_control=0（Application Defects）','OTHER','block',1,1452647413,NULL,90128,'低危','攻击者会利用使响应头缺失 Cache-Control头的请求访问服务器。','建议web服务器把响应头缺失 Cache-Control头的应答过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981240,'使用SQL注释符号，char函数，或其他条件语句等的注入','(?i:(?:\\)\\s*?when\\s*?\\d+\\s*?then)|(?:[\\\"\'`´’‘]\\s*?(?:#|--|{))|(?:\\/\\*!\\s?\\d+)|(?:ch(?:a)?r\\s*?\\(\\s*?\\d)|(?:(?:(n?and|x?x?or|div|like|between|and|not)\\s+|\\|\\||\\&\\&)\\s*?\\w+\\())','探测利用SQL注释符号-- /* #等，或者利用char(数字)函数等伪装的注入，并且检测其他between and ,like，|| &&等组成的条件语句','SQLI','block',0,1395124100,NULL,1046,'低危','在cookies和请求参数和xml中利用)  when  1244  then|\\  #|char   (  234等字符，攻击者可尝试使用注释条件语句或者char函数进行注入。一旦成功绕过防火墙，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有)  when  1244  then|\\  #|char   (  234等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981241,'sql语句条件注入检测','(?i:(?:[\\s()]case\\s*?\\()|(?:\\)\\s*?like\\s*?\\()|(?:having\\s*?[^\\s]+\\s*?[^\\w\\s])|(?:if\\s?\\([\\d\\w]\\s*?[=<>~]))','检测sql语句查询条件语句拼装注入，如like,having等','SQLI','block',0,1395124100,NULL,1039,'低危','在cookies和请求参数和xml中利用(case (|)like (|if (3 =等字符时候，攻击者可尝试数据库的条件语句注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有[$between]|[$size]|[$exists]等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981242,'经典sql注入探测之一','(?i:(?:[\\\"\'`´’‘]\\s*?(x?or|div|like|between|and)\\s*?[\\\"\'`´’‘]?\\d)|(?:\\\\\\\\x(?:23|27|3d))|(?:^.?[\\\"\'`´’‘]$)|(?:(?:^[\\\"\'`´’‘\\\\\\\\]*?(?:[\\d\\\"\'`´’‘]+|[^\\\"\'`´’‘]+[\\\"\'`´’‘]))+\\s*?(?:n?and|x?x?or|div|like|between|and|not|\\|\\||\\&\\&)\\s*?[\\w\\\"\'`´’‘][+&!@(),.-])|(?:[^\\','攻击者在找到注入点后往往会尝试从information_schema.table_name来获取数据库的元数据信息','SQLI','block',0,1395124100,NULL,1049,'低危','在cookies和请求参数和xml中利用\\ xor \\2|\\\\x23|dinformation_schema等字符，攻击者可实行SQL注入点的探测，一旦漏洞被发现，就可实现SQL注入的攻击，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对包含and...、or...、between...、div...、like...、not...、information_schema、table_name内容的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981243,'经典sql注入探测之二','(?i:(?:[\\\"\'`´’‘]\\s*?\\*.+(?:x?or|div|like|between|and|id)\\W*?[\\\"\'`´’‘]\\d)|(?:\\^[\\\"\'`´’‘])|(?:^[\\w\\s\\\"\'`´’‘-]+(?<=and\\s)(?<=or|xor|div|like|between|and\\s)(?<=xor\\s)(?<=nand\\s)(?<=not\\s)(?<=\\|\\|)(?<=\\&\\&)\\w+\\()|(?:[\\\"\'`´’‘][\\s\\d]*?[^\\w\\s]+\\W*?\\d\\W*?.*?[\\\"\'`´','探测一些攻击者在攻击开始阶段尝试对数据库执行多种不同的查询操作，每次传送不同的查询条件，根据反馈结果来猜测数据库注入点和数据库结构的操作','SQLI','block',0,1395124100,NULL,1053,'低危','在cookies和请求参数和xml中利用\\ \\ like \\ |<-^\\^|\\^\\等字符，攻击者可实行SQL注入点的探测，一旦漏洞被发现，就可实现SQL注入的攻击，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有<=and...、<=or...、<=between...、<=div...、<=like...、<=not...内容的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981244,'SQL基础认证BYPASS之一','(?i:(?i:\\d[\\\"\'`´’‘]\\s+[\\\"\'`´’‘]\\s+\\d)|(?:^admin\\s*?[\\\"\'`´’‘]|(\\/\\*)+[\\\"\'`´’‘]+\\s?(?:--|#|\\/\\*|{)?)|(?:[\\\"\'`´’‘]\\s*?\\b(x?or|div|like|between|and)\\b\\s*?[+<>=(),-]\\s*?[\\d\\\"\'`´’‘])|(?:[\\\"\'`´’‘]\\s*?[^\\w\\s]?=\\s*?[\\\"\'`´’‘])|(?:[\\\"\'`´’‘]\\W*?[+=]+\\W*?[\\\"\'`´’‘])|(?','探测企图绕过SQL基础认证的尝试','SQLI','block',0,1395124100,NULL,1033,'低危','在cookies和请求参数和xml中利用^admin \\|\" between = \"|where - = 等字符，攻击者可实行SQL认证绕过尝试，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有^admin \\|\" between = \"|where - = 等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981245,'SQL基础认证BYPASS之二','(?i:(?:union\\s*?(?:all|distinct|[(!@]*?)?\\s*?[([]*?\\s*?select\\s+)|(?:\\w+\\s+like\\s+[\\\"\'`´’‘])|(?:like\\s*?[\\\"\'`´’‘]\\%)|(?:[\\\"\'`´’‘]\\s*?like\\W*?[\\\"\'`´’‘\\d])|(?:[\\\"\'`´’‘]\\s*?(?:n?and|x?x?or|div|like|between|and|not |\\|\\||\\&\\&)\\s+[\\s\\w]+=\\s*?\\w+\\s*?having\\s+)|','探测企图绕过SQL基础认证的尝试','SQLI','block',0,1395124100,NULL,1042,'低危','在cookies和请求参数和xml中利用union all|a like \\|nand a+= a having 等字符，攻击者可实行SQL认证绕过尝试，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有union all|a like \\|nand a+= a having 等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981246,'SQL基础认证BYPASS之三','(?i:(?:in\\s*?\\(+\\s*?select)|(?:(?:n?and|x?x?or|div|like|between|and|not |\\|\\||\\&\\&)\\s+[\\s\\w+]+(?:regexp\\s*?\\(|sounds\\s+like\\s*?[\\\"\'`´’‘]|[=\\d]+x))|([\\\"\'`´’‘]\\s*?\\d\\s*?(?:--|#))|(?:[\\\"\'`´’‘][\\%&<>^=]+\\d\\s*?(=|x?or|div|like|between|and))|(?:[\\\"\'`´’‘]\\W+[\\w+','探测企图绕过SQL基础认证的尝试','SQLI','block',0,1395124100,NULL,1050,'低危','在cookies和请求参数和xml中利用union in ( select|\\\\a =|=x等字符，攻击者可实行SQL认证绕过尝试，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有union in ( select|\\\\a =|=x等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981247,'串联的基本SQL注入，和SQLLFI尝试','(?i:(?:[\\d\\W]\\s+as\\s*?[\\\"\'`´’‘\\w]+\\s*?from)|(?:^[\\W\\d]+\\s*?(?:union|select|create|rename|truncate|load|alter|delete|update|insert|desc))|(?:(?:select|create|rename|truncate|load|alter|delete|update|insert|desc)\\s+(?:(?:group_)concat|char|load_file)\\s?\\(?)','探测一些基本的select、create、rename、alter、update、delete等基本sql语句的串连操作，以及通过load_file等进行的LFI尝试','SQLI','block',0,1395124100,NULL,1052,'低危','在cookies和请求参数和xml中利用2   as  \\\"   from|3  select|(load_file (等字符，攻击者可用串联的基本的SQL注入方法，然后把本地文件包含，从而进一步的实行攻击，此漏洞已经在2015-05-27于WooYun平台公开。属于高危漏洞。','建议在web服务器添加对含有2   as  \\\"   from|3  select|(load_file (等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981248,'链式SQL注入检测之一','(?i:(?:@.+=\\s*?\\(\\s*?select)|(?:\\d+\\s*?(x?or|div|like|between|and)\\s*?\\d+\\s*?[\\-+])|(?:\\/\\w+;?\\s+(?:having|and|x?or|div|like|between|and|select)\\W)|(?:\\d\\s+group\\s+by.+\\()|(?:(?:;|#|--)\\s*?(?:drop|alter))|(?:(?:;|#|--)\\s*?(?:update|insert)\\s*?\\w{2,})|(?:[','探测通过--#等注释符号或;等符号拼装成的链式SQL注入检测','SQLI','block',0,1395124100,NULL,1036,'低危','在cookies和请求参数和xml中利用 nand（a)+= 123=|/anc/ between &|@+= ( select等字符，攻击者可尝试SQL链式注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有nand（a)+= 123=|/anc/ between &|@+= ( select等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981249,'链式SQL注入检测之二','(?i:(?:[\\\"\'`´’‘]\\s+and\\s*?=\\W)|(?:\\(\\s*?select\\s*?\\w+\\s*?\\()|(?:\\*\\/from)|(?:\\+\\s*?\\d+\\s*?\\+\\s*?@)|(?:\\w[\\\"\'`´’‘]\\s*?(?:[-+=|@]+\\s*?)+[\\d(])|(?:coalesce\\s*?\\(|@@\\w+\\s*?[^\\w\\s])|(?:\\W!+[\\\"\'`´’‘]\\w)|(?:[\\\"\'`´’‘];\\s*?(?:if|while|begin))|(?:[\\\"\'`´’‘][\\s\\d]+=\\','探测复杂的SQL查询语句，这些语句往往通过; () 或其他 if then when case等组成复杂的SQL语句查询','SQLI','block',0,1395124100,NULL,1047,'低危','在cookies和请求参数和xml中利用\\ and =$|(   select 123abc (|@@anc  %等字符，攻击者可尝试SQL链式注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有\\ and =$|(   select 123abc (|@@anc  %等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981250,'benchmark和sleep函数注入检测','(?i:(?:(select|;)\\s+(?:benchmark|if|sleep)\\s*?\\(\\s*?\\(?\\s*?\\w+))','探测在sql语句包括条件查询中的benchmark和sleep函数注入尝试','SQLI','block',0,1395124100,NULL,1038,'低危','在cookies和请求参数和xml中利用)  select   benchmark (  (  123|select  sleep   (   (   123等字符，攻击者可尝试使用sheep()或者benchmark（）函数带条件的查询注入。一旦成功将会进一步的攻击，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有)  select   benchmark (  (  123|select  sleep   (   (   123等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981251,'MySQL UDF注入，及其他的改变数据/结构的操作','(?i:(?:create\\s+function\\s+\\w+\\s+returns)|(?:;\\s*?(?:select|create|rename|truncate|load|alter|delete|update|insert|desc)\\s*?[\\[(]?\\w{2,}))','探测创建函数create function returns等操作，或其他的create rename truncate alter update delete insert desc等企图改变数据结构或改变数据内容的操作','SQLI','block',0,1395124100,NULL,1051,'低危','在cookies和请求参数和xml中利用create  function  1233  returns|;  rename [234|;  alter \\1234等字符，攻击者可尝试MySql UDF注入及其他改变数据和数据结构的操作。一旦成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有create  function  1233  returns|;  rename [234|;  alter \\1234等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981252,'MySQL字符集转换和MSSQL DOS攻击检测','(?i:(?:alter\\s*?\\w+.*?character\\s+set\\s+\\w+)|([\\\"\'`´’‘];\\s*?waitfor\\s+time\\s+[\\\"\'`´’‘])|(?:[\\\"\'`´’‘];.*?:\\s*?goto))','检测通过alter character set修改MySQL字符集，通过waitfor time等操作进行MSSQL DOS攻击的尝试','SQLI','block',0,1395124100,NULL,1040,'低危','在cookiealter character set waitfor time \"\"\'\'goto等字符时候，攻击者可尝试数据库的条件语句注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。 ','建议在web服务器添加对含有cookiealter character set waitfor time \"\"\'\'goto等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981253,'针对MySQL和PostgreSQL的存储过程及函数注入','(?i:(?:procedure\\s+analyse\\s*?\\()|(?:;\\s*?(declare|open)\\s+[\\w-]+)|(?:create\\s+(procedure|function)\\s*?\\w+\\s*?\\(\\s*?\\)\\s*?-)|(?:declare[^\\w]+[@#]\\s*?\\w+)|(exec\\s*?\\(\\s*?@))','通过探测 create procedure function declare @ # exec等来确定针对MySQL和PostgreSQL的存储过程和函数注入攻击','SQLI','block',0,1395124100,NULL,1048,'低危','在cookies和请求参数和xml中利用procedeure analyse (|; open -adc-|create procedure等字符，攻击者可对PostgreSQL和mysql等数据库的存储操作。一旦成功，攻击者可获取重要信息及机密文件。  ','建议在web服务器添加对含有procedeure analyse (|; open -adc-|create procedure等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981254,'针对Postgres的pg_sleep注入, 以及waitfor delay攻击，还有试图关闭数据库（shutdown）','(?i:(?:select\\s*?pg_sleep)|(?:waitfor\\s*?delay\\s?[\\\"\'`´’‘]+\\s?\\d)|(?:;\\s*?shutdown\\s*?(?:;|--|#|\\/\\*|{)))','探测针对Postgres的pg_sleep注入, 以及waitfor delay攻击，还有试图通过shutdown指令关闭数据库的操作','SQLI','block',0,1395124100,NULL,1044,'低危','在cookies和请求参数和xml中利用select  pg_sleep|waitfor delay \\ 3|;  shutdown --等字符，攻击者可尝试Postgres和pg_sleep注入延迟攻击并尝试把数据库关掉 。一旦成功，攻击者可以破坏服务器的数据库正常的运行。  ','建议在web服务器添加对含有select  pg_sleep|waitfor delay \\ 3|;  shutdown --等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981255,'MSSQL代码执行及信息收集检测','(?i:(?:\\sexec\\s+xp_cmdshell)|(?:[\\\"\'`´’‘]\\s*?!\\s*?[\\\"\'`´’‘\\w])|(?:from\\W+information_schema\\W)|(?:(?:(?:current_)?user|database|schema|connection_id)\\s*?\\([^\\)]*?)|(?:[\\\"\'`´’‘];?\\s*?(?:select|union|having)\\s*?[^\\s])|(?:\\wiif\\s*?\\()|(?:exec\\s+master\\.)|(?:','探测攻击者企图执行MSSQL数据库代码，及收集数据库信息的企图','SQLI','block',0,1395124100,NULL,1034,'低危','在cookies和请求参数和xml中利用 exec xp_cmdshell|\\ ?! \\|from%$information_schema#|union select@等字符，攻击者可实行数据库的代码执行和数据的收集，一旦成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有 exec xp_cmdshell|\\ ?! \\|from%$information_schema#|union select@等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981256,'MATCH AGAINST, MERGE, EXECUTE IMMEDIATE和HAVING等注入','(?i:(?:merge.*?using\\s*?\\()|(execute\\s*?immediate\\s*?[\\\"\'`´’‘])|(?:\\W+\\d*?\\s*?having\\s*?[^\\s\\-])|(?:match\\s*?[\\w(),+-]+\\s*?against\\s*?\\())','检测用户提交的内容中的MATCH AGAINST, MERGE, EXECUTE IMMEDIATE，HAVING等关键词的注入','SQLI','block',0,1395124100,NULL,1041,'低危','在cookies和请求参数和xml中利用merge using (}execute immediate \\|match +() against (等字符，攻击者可尝试实施MATCH AGAINST, MERGE, EXECUTE IMMEDIATE和HAVING等注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有merge using (}execute immediate \\|match +() against (等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981257,'MySQL数据库检测','(?i:(?:,.*?[)\\da-f\\\"\'`´’‘][\\\"\'`´’‘](?:[\\\"\'`´’‘].*?[\\\"\'`´’‘]|\\Z|[^\\\"\'`´’‘]+))|(?:\\Wselect.+\\W*?from)|((?:select|create|rename|truncate|load|alter|delete|update|insert|desc)\\s*?\\(\\s*?space\\s*?\\())','探测mysql数据库的注释区间混淆和反单引号中断的检测','SQLI','block',0,1395124100,NULL,1035,'低危','在cookies和请求参数和xml中利用#select%from|rename ( space (|,3\\\"\\等字符，攻击者可尝试使用注释来冒充注入的数据中的空格（准空格分隔符），从而尝试绕过防火墙，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有#select%from|rename ( space (|,3\\\"\\等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981260,'十六进制SQL规避方法','(?i:(?:\\A|[^\\d])0x[a-f\\d]{3,}[a-f\\d]*)+','很多SQL注入为了逃避检测，往往将攻击内容进行十六进制编码','SQLI','block',0,1395124100,NULL,1002,'高危','在cookies和请求参数和xml中利用\\A|a0x12afca0x1qqcb等字符，攻击者可尝试使用16进制编码进行注入。一旦成功绕过防火墙，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有\\A|a0x12afca0x1qqcb等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981270,'针对MongoDB的基本SQL注入','(?i:(?:\\[\\$(?:ne|eq|lte?|gte?|n?in|mod|all|size|exists|type|slice|x?or|div|like|between|and)\\]))','探测针对MongoDB的基本sql 注入，主要关键词有：[$eq][$all][$like][$between][$and]等','SQLI','block',0,1395124100,NULL,1045,'高危','在cookies和请求参数和xml中利用[$between]|[$size]|[$exists]等字符时候，攻击者可尝试对MongoDB进行注入。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有[$between]|[$size]|[$exists]等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981272,'探测盲注测试','(?i:(sleep\\((\\s*?)(\\d*?)(\\s*?)\\)|benchmark\\((.*?)\\,(.*?)\\)))','探测通过利用sleep() or benchmark()等函数进行的盲注测试','SQLI','block',0,1395124100,NULL,1032,'高危','在cookies和请求参数和xml中利用)  sheep(   1234|benchmark(attack,123)等字符，攻击者可尝试使用sheep()或者benchmark（）函数进行盲注测试。一旦成功将会进一步的攻击，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有)  sheep(   1234|benchmark(attack,123)等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981276,'基本SQL注入，在攻击MySQL,ORACLE或其他数据库时通常会出现的字符串','(?i:(?:(union(.*?)select(.*?)from)))','基本SQL注入，在攻击MySQL,ORACLE或其他数据库时通常会出现的字符串，通常是 union select from这样的形式','SQLI','block',0,1395124100,NULL,1043,'高危','在cookies和请求参数和xml中利用union select form等字符，攻击者可对oracle和mysql等数据库的常用的注入攻击。一旦成功注入，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有union select form等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981277,'整数溢出攻击检测','(?i:(?:^(-0000023456|4294967295|4294967296|2147483648|2147483647|0000012345|-2147483648|-2147483649|0000023456|2.2.80738585072007e-308|1e309)$))','探测整数溢出攻击，比如skipfish中的魔数：2.2.80738585072007e-308','SQLI','block',0,1395124100,NULL,1037,'高危','在cookies和请求参数和xml中利用-0000023456或者4294967285或者1e309或者2147483647等字符时候，攻击者可尝试整数溢出攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有-0000023456或者4294967285或者1e309或者2147483647等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981300,'检测请求数据中的内容是否与现有的关键词匹配','REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/|REQUEST_COOKIES_NAMES|ARGS_NAMES|ARGS|XML:/* \"@pm select show top distinct from dual where group by order having limit offset union rownum as (case\" ','如果有关键词匹配，则设置tx.sqli_select_statement参数值','SQLI','pass',0,1452647413,NULL,90113,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981301,'select关键词检测','select','SQL关键词检测，当检测到select后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1007,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符，攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981302,'show关键词检测','show','SQL关键词检测，当检测到show后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1008,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符，攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981303,'top关键词检测','top','SQL关键词检测，当检测到top后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1009,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符，攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981304,'distinct关键词检测','distinct','SQL关键词检测，当检测到distinct后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1010,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981305,'from关键词检测','from','SQL关键词检测，当检测到from后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1011,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981306,'dual关键词检测','dual','SQL关键词检测，当检测到dual后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1012,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981307,'where关键词检测','where','SQL关键词检测，当检测到where后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1013,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981308,'group by关键词检测','group by','SQL关键词检测，当检测到group by后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1014,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981309,'order by关键词检测','order by','SQL关键词检测，当检测到order by后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1015,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981310,'having关键词检测','having','SQL关键词检测，当检测到having后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1016,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981311,'limit关键词检测','limit','SQL关键词检测，当检测到limit后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1017,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981312,'offset关键词检测','offset','SQL关键词检测，当检测到offset后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1018,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981313,'union关键词检测','union','SQL关键词检测，当检测到union后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1019,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981314,'union all关键词检测','union all','SQL关键词检测，当检测到union all后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1020,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981315,'rownum as关键词检测','rownum as','SQL关键词检测，当检测到rownum as后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1021,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981316,'(case关键词检测','(case','SQL关键词检测，当检测到(case后积分+1,默认当积分>3后阻断攻击','SQLI','pass',0,1395124100,NULL,1022,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981317,'检测SQL关键词的总数','TX:SQLI_SELECT_STATEMENT_COUNT \"@ge 3\"','如果检测到SQL关键词总数大与等于3，则阻断访问','SQLI','block',0,1452647413,NULL,90114,'高危','在请求中利用(case|rownum as|union all|offset|limit|having|where|dual等敏感字符，攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有(case|rownum as|union all|offset|limit|having|where|dual等敏感字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981318,'SQL常用注入测试','(^[\\\"\'`´’‘;]+|[\\\"\'`´’‘;]+$)','识别常见的初始SQL注入探测请求，攻击者尝试在正常的输入位置插入/追加引号字符等，看看web应用程序/数据库如何响应。','SQLI','block',0,1395124100,NULL,1003,'高危','在cookies和请求参数和xml中利用以\\\"\'`;等字符开头或以\\\";\'等字符结尾，攻击者可尝试用简单、常用的注入方法测试服务器，从而进一步的实行攻击，此时防火墙除了把请求拦截意外，还会设置异常分值，准备好应对攻击者可进一步的攻击。','建议在web服务器添加对以\\\"\'`;等字符开头或以\\\";\'等字符结尾的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981319,'SQL常见操作符检测','(?i:(\\!\\=|\\&\\&|\\|\\||>>|<<|>=|<=|<>|<=>|xor|rlike|regexp|isnull)|(?:not\\s+between\\s+0\\s+and)|(?:is\\s+null)|(like\\s+null)|(?:(?:^|\\W)in[+\\s]*\\([\\s\\d\\\"]+[^()]*\\))|(?:xor|<>|rlike(?:\\s+binary)?)|(?:regexp\\s+binary))','通过检测SQL语句中的常见操作符来判断SQL注入攻击，如常见的：xor|rlike|regexp|isnullnot|between|and|like|in等','SQLI','block',0,1395124100,NULL,1004,'高危','在cookies和请求参数和xml中利用！=|&&|>>|<<|<=|rlike|isnull等字符，攻击者可尝试用SQL的操作符进行攻击试探，从而进一步的实行攻击。','建议在web服务器添加对含有=|&&|>>|<<|<=|rlike|isnull等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981320,'数据库名字探测','(?i:(?:m(?:s(?:ysaccessobjects|ysaces|ysobjects|ysqueries|ysrelationships|ysaccessstorage|ysaccessxml|ysmodules|ysmodules2|db)|aster\\.\\.sysdatabases|ysql\\.db)|s(?:ys(?:\\.database_name|aux)|chema(?:\\W*\\(|_name)|qlite(_temp)?_master)|d(?:atabas|b_nam)e\\W*\\(','检测输入中是否出现一些数据库系统中常见的数据库名，如：master、sysobjects等','SQLI','block',0,1395124100,NULL,1006,'高危','在cookies和请求参数和xml中利用 msysaccessobjects|mysrelationships|sys darabase_name|sysaux等字符，攻击者可尝试查找数据库的名字。一旦成功便可以对数据库实行进一步的攻击，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。  ','建议在web服务器添加对含有msysaccessobjects|mysrelationships|sys darabase_name|sysaux等字符的数据进行过滤','SQLI');
INSERT INTO `t_rules` VALUES (981400,'检测全局集合参数CONTENT_TYPE_HEADER_EXISTS的值（Application Defects）','&GLOBAL:CONTENT_TYPE_HEADER_EXISTS \"@eq 0\"','如果全局集合参数CONTENT_TYPE_HEADER_EXISTS的值为0 ，则设置参数global.content_type_header_exists=0（Application Defects）','OTHER','block',1,1452647413,NULL,90132,'低危','攻击者会利用使响应头缺失 content-type头的请求访问服务器。','建议web服务器把响应头缺失content-type头的应答过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981401,'检测http响应头是否含有Content-Type字段内容（Application Defects）','GLOBAL:CONTENT_TYPE_HEADER_EXISTS \"@le 10\"','CONTENT_TYPE_HEADER_EXISTS参数值少于或等于10，说明http响应头没有Content-Type字段或者该字段内容为空（Application Defects）','OTHER','block',1,1452647413,NULL,90133,'低危','浏览器是根据Content-Type字段的内容来判断怎么处理响应信息，如果Content-Type字段内容为空，浏览器会强迫性的嗅探信息内容进行决断。强迫浏览器进入这种状态是不可取的,因为它会导致可利用的条件。','建议web服务器在响应信息中添加Content-Type字段内容','OTHER');
INSERT INTO `t_rules` VALUES (981402,'检测全局集合参数X_XSS_PROTECTION_DISABLED的值（Application Defects）','&GLOBAL:X_XSS_PROTECTION_DISABLED \"@eq 0\"','如果全局集合参数CONTENT_TYPE_HEADER_EXISTS的值为0 ，则设置参数global.x_xss_protection_disabled=0（Application Defects）','OTHER','block',1,1452647413,NULL,90130,'低危','IE8浏览器中XSS防护过滤器没使能是很危险的。','建议web服务器把IE8浏览器中XSS防护过滤器没使能的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981403,'检测IE浏览器的XSS防护过滤功能是否启用（Application Defects）','GLOBAL:X_XSS_PROTECTION_DISABLED \"@le 10\"','X_XSS_PROTECTION_DISABLED参数值少于或等于10，说明IE浏览器的XSS防护过滤功能没有启用（Application Defects）','OTHER','block',1,1452647413,NULL,90131,'低危','IE8浏览器中XSS防护过滤器没使能是很危险的。','建议web服务器把IE8浏览器中XSS防护过滤器没使能的请求过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981404,'检测全局集合参数X_FRAME_OPTIONS的值（Application Defects）','&GLOBAL:X_FRAME_OPTIONS \"@eq 0\"','如果全局集合参数X_FRAME_OPTIONS的值为0 ，则设置参数global.x_frame_options=0（Application Defects）','OTHER','block',1,1452647413,NULL,90136,'低危','攻击者会利用使响应头缺失 FRAME-OPTIONS头或者被设置成deny的请求访问服务器。','建议web服务器响应头缺失 FRAME-OPTIONS头或者被设置成deny的响应体过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981405,'检测http响应头是否含有X-FRAME-OPTIONS字段内容（Application Defects）','GLOBAL:X_FRAME_OPTIONS \"@le 10\"','X_FRAME_OPTIONS参数值少于或等于10，说明http响应头没有X-FRAME-OPTIONS字段或者该字段内容为空（Application Defects）','OTHER','block',1,1452647413,NULL,90137,'低危','攻击者会利用使响应头缺失 FRAME-OPTIONS头或者被设置成deny的请求访问服务器。','建议web服务器响应头缺失 FRAME-OPTIONS头或者被设置成deny的响应体过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981406,'检测全局集合参数X_CONTENT_TYPE_OPTIONS的值（Application Defects）','&GLOBAL:X_CONTENT_TYPE_OPTIONS \"@eq 0\"','如果全局集合参数X_CONTENT_TYPE_OPTIONS的值为0 ，则设置参数global.x_content_type_options=0（Application Defects）','OTHER','block',1,1452647413,NULL,90134,'低危','攻击者会利用使响应头缺失 content-type头或者X-Content-Type-Options同样缺失或被设置成\'nosniff\'的请求访问服务器。','建议web服务器缺失 content-type头或者X-Content-Type-Options同样缺失或被设置成\'nosniff\'的响应体过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (981407,'检测http响应头的Content-Type字段内容及X_CONTENT_TYPE_OPTIONS是否缺少（Application Defects）','&RESPONSE_HEADERS:Content-Type|RESPONSE_HEADERS:Content-Type \"^0$|^$\"','如果匹配规则，则说明响应头部缺少Content-Type字段并且缺少X-Content-Type-Options字段或该字段没有设置成nosniff（Application Defects）','OTHER','block',1,1452647413,NULL,90135,'低危','攻击者会利用使响应头缺失 content-type头或者X-Content-Type-Options同样缺失或被设置成\'nosniff\'的请求访问服务器。','建议web服务器缺失 content-type头或者X-Content-Type-Options同样缺失或被设置成\'nosniff\'的响应体过滤了。','OTHER');
INSERT INTO `t_rules` VALUES (990002,'检测请求头中的User-Agent字段内容1(Bat Robots)','REQUEST_HEADERS:User-Agent \"@pmFromFile modsecurity_35_scanners.data\"','检测请求头中的User-Agent字段内容是否与modsecurity_35_scanners.data列表的短语匹配,如果匹配，则阻断访问，并设置相关参数值(Bat Robots)','OTHER','block',1,1452647413,NULL,90118,'高危','如果攻击者利用安全漏洞扫描工具浏览网页，请求的user agent中会包含了某些如arachni、absinthe、nikto等字段，当给工具找到了网页上面的漏洞，会进一步的实施攻击。','建议在web服务器对请求头中的User-Agent字段进行检测，是否包含了某些如arachni、absinthe、nikto等字段，是则进行阻拦','OTHER');
INSERT INTO `t_rules` VALUES (990012,'检测请求头中的User-Agent字段内容2(Bat Robots)','REQUEST_HEADERS:User-Agent \"@pmFromFile modsecurity_35_bad_robots.data\"','检测请求头中的User-Agent字段内容是否与modsecurity_35_bad_robots.data列表的短语匹配,如果匹配，则阻断访问，并设置相关参数值(Bat Robots)','OTHER','block',1,1452647413,NULL,90116,'中危','如果请求是网络蠕虫，请求的user agent 中会包含了某些如missigua、floodgate、webaltbot等字段，并且有contentsmartz|errypicker|emailextract|harvest等字段，，它会扫描和攻击网络上存在系统漏洞。','建议在web服务器对请求头中的User-Agent字段进行检测，识别是否bad_robot，如已知的有wisenutbot、prowebwalker等，可在网上查找','OTHER');
INSERT INTO `t_rules` VALUES (990901,'检测请求头名称(Bat Robots)','REQUEST_HEADERS_NAMES \"\\bacunetix-product\\b\"','如果匹配，则阻断访问，并设置相关参数值(Bat Robots)','OTHER','block',1,1452647413,NULL,90117,'高危','攻击者利用安全漏洞扫描工具浏览网页，会在请求头中包含了acunetix-product，该工具会找到网页上面的漏洞，进而进一步的攻击。','建议web服务器拒绝请求头中包含了acunetix-product的请求访问','OTHER');
INSERT INTO `t_rules` VALUES (990902,'检测请求文件名(Bat Robots)','REQUEST_FILENAME \"@pm nessustest appscan_fingerprint\"','如果请求文件名是nessustest或appscan_fingerprint，则阻断访问，并设置相关参数值(Bat Robots)','OTHER','block',1,1452647413,NULL,90119,'高危','攻击者利用安全漏洞扫描工具浏览网页，请求uri中文件名字会是nessustest 或者appscan_fingerprint，该工具会找到网页上面的漏洞，进而进一步的攻击。','建议web服务器拒绝请求uri中文件名字会是nessustes的请求访问','OTHER');
INSERT INTO `t_rules` VALUES (999003,'检测XSS是否攻击已知的XSS弱点参数(Scanner Integration)','TX:/XSS-ARGS:/ \".*\"','如果匹配规则，说明XSS攻击已知的弱点参数(Scanner Integration)','OTHER','block',1,1452647413,NULL,90001,'高危','攻击者如果对已知的弱点参数实行了攻击，此规则会记录下来。','','OTHER');
INSERT INTO `t_rules` VALUES (999004,'检测SQL是否攻击已知的SQL弱点参数(Scanner Integration)','TX:/SQL_INJECTION-ARGS:/ \".*\"','如果匹配规则，说明SQL攻击已知的弱点参数(Scanner Integration)','OTHER','block',1,1452647413,NULL,90002,'高危','在请求中利用select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符攻击者可进行SQL注入攻击。一旦注入成功，攻击者可获取数据库的管理用户权限，然后将数据库管理用户权限提升至操作系统管理用户权限，控制服务器操作系统，获取重要信息及机密文件。','建议在web服务器添加对含有select show top distinct from dual where group by order having limit offset union rownum as (case等敏感字符的数据进行过滤','OTHER');
INSERT INTO `t_rules` VALUES (999005,'检测请求文件类型是否是html（Ignore Static）','REQUEST_FILENAME \"\\.(?:(?:cs|j)s|html?)$\"','如果匹配规则，则说明是html文件（Ignore Static）','OTHER','block',1,1452647413,NULL,90054,'低危','攻击者会利用媒体文件以外的一切文件上传到服务器，实施攻击。','','OTHER');
INSERT INTO `t_rules` VALUES (999006,'检测请求文件类型是否是Media（Ignore Static）','REQUEST_FILENAME \"\\.(?:mp(?:e?g|3)|avi|flv|swf|wma)$\"','如果匹配规则，则说明是Media文件（Ignore Static）','OTHER','block',1,1452647413,NULL,90053,'低危','攻击者会利用媒体文件以外的一切文件上传到服务器，实施攻击。','','OTHER');
INSERT INTO `t_rules` VALUES (999008,'检测是否要跳过关于没有参数的文本内容请求数据的检查（Skip Outbound Checks）','TX:text_file_extension \"@eq 1\" TX:no_parameters \"@eq 1\"','如果匹配规则，则跳过关于没有参数的文本内容请求数据的检查（Skip Outbound Checks）','OTHER','block',1,1452647413,NULL,90150,'低危','','','OTHER');
INSERT INTO `t_rules` VALUES (999010,'检测请求参数或参数名是否有http（Comment Spam）','ARGS|ARGS_NAMES \"\\bhttp:\" ','如果请求参数或参数名中有http，则跳过下一个规则（Comment Spam）','OTHER','block',1,1452647413,NULL,90158,'低危','垃圾评论是一种攻击，对象是对博客、论坛、留言板等会接受并显示游客提供的超级链接的交互网页。\n这些垃圾评论制造者会专门发送一些自动的、随意的评论，并会携带一个链接到攻击者的站点，然后这些链接就会被人工的提高了在网站的搜索引擎中的排名，从而在网站的搜索结果中更加明显','建议使用第三方反垃圾系统。垃圾评论 90% 以上都是由机器人产生的，因此使用验证码也可以过滤掉大部分的垃圾评论。','OTHER');
INSERT INTO `t_rules` VALUES (999011,'初始化CommentSpam处理行为是“继续处理”（Comment Spam）','SecAction phase:2,id:\'999011\',rev:\'2.2.9\',pass,nolog,skipAfter:END_COMMENT_SPAM','初始化Comment Spam处理行为是“继续处理”，并跳过Comment Spam检测规则（Comment Spam）','OTHER','block',1,1452647413,NULL,90159,'低危','','','OTHER');
INSERT INTO `t_rules` VALUES (1703071,'检测Content-Type长度异常','SecRule? REQUEST_HEADERS:Content-Type \"@gt 100\" \"phase:1,t:none,t:length,deny,msg:\'Request content type is too long\',rev:\'2\',ver:\'OWASP_CRS/2.2.9\',maturity:    \'9\',accuracy:\'9\',id:\'1703071\',tag:\'Apache Struts2/S2-045\',severity:\'2\',logdata:\'%{matched_var}\'\"','攻击者可在上传文件时通过修改HTTP请求头中的Content-Type值来触发该漏洞，进而执行系统命令','GENERIC','block',1,1488934563,NULL,9098,'高危','Apache Structs2的Jakarta Multipart parser插件存在远程代码执行漏洞，漏洞编号为CVE-2    017-5638。攻击者可以在使用该插件上传文件时，修改HTTP请求头中的Content-Type值来触发该漏洞，导致远程执行代码。','修复Jakarta文件上传插件或者是存在漏洞的Struts 2版本请升级至St    ruts2安全版本','GENERIC');
/*!40000 ALTER TABLE `t_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_ruleset`
--

DROP TABLE IF EXISTS `t_ruleset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ruleset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `modelname` varchar(50) NOT NULL,
  `selectedfiles` varchar(1024) DEFAULT NULL,
  `ischecked` tinyint(4) DEFAULT NULL,
  `isdefault` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_ruleset`
--

LOCK TABLES `t_ruleset` WRITE;
/*!40000 ALTER TABLE `t_ruleset` DISABLE KEYS */;
INSERT INTO `t_ruleset` VALUES (1,'基本防护(内置)','1,4,7,6,8',0,1);
INSERT INTO `t_ruleset` VALUES (2,'中级防护(内置)','1,2,3,4,5,6,7,8,9,10,11,12,14,15',0,1);
INSERT INTO `t_ruleset` VALUES (3,'高级防护(内置)','1,2,3,4,5,6,7,8,9,10,11,12,14,15,18,24',1,1);
/*!40000 ALTER TABLE `t_ruleset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_scantask`
--

DROP TABLE IF EXISTS `t_scantask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_scantask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL COMMENT '任务名称',
  `url` varchar(255) DEFAULT NULL COMMENT '扫描地址',
  `starttime` int(11) DEFAULT NULL COMMENT '开始时间',
  `endtime` int(11) DEFAULT NULL COMMENT '完成时间',
  `status` tinyint(3) DEFAULT NULL COMMENT '0=>''未扫描'', 1=>''扫描中'', 2=>''已完成'', 3=>''已停止'', 4=>''扫描失败''',
  `result` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=32 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_scantask`
--

LOCK TABLES `t_scantask` WRITE;
/*!40000 ALTER TABLE `t_scantask` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_scantask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_scanvirus_setting`
--

DROP TABLE IF EXISTS `t_scanvirus_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_scanvirus_setting` (
  `is_use` tinyint(4) DEFAULT '0' COMMENT '是否开启木马扫描',
  `extend_name` varchar(2048) DEFAULT '' COMMENT '扩展名'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_scanvirus_setting`
--

LOCK TABLES `t_scanvirus_setting` WRITE;
/*!40000 ALTER TABLE `t_scanvirus_setting` DISABLE KEYS */;
INSERT INTO `t_scanvirus_setting` VALUES (1,'txt|exe|doc');
/*!40000 ALTER TABLE `t_scanvirus_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_securityset`
--

DROP TABLE IF EXISTS `t_securityset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_securityset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_ssl` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  `ssl_path` varchar(255) DEFAULT '' COMMENT 'ssl file path',
  `header_hide_list` varchar(512) DEFAULT 'Server|X-Powered-By' COMMENT '服务器信息隐藏hide header information',
  `spider_list` varchar(2048) DEFAULT '' COMMENT '爬虫防护设置爬虫类型spider list',
  `hostlinking_list` varchar(512) DEFAULT '' COMMENT '防盗链设置文件类型host linking list',
  `is_sensitive` tinyint(3) DEFAULT '0' COMMENT '敏感词过滤开启状态0disable 1enable',
  `sensitive_words` text COMMENT '敏感词内容sensitive works',
  `is_selfstudy` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  `is_autodefence` tinyint(3) DEFAULT '0' COMMENT '智能阻断状态0disable 1enable',
  `autodefence_cycle` int(11) DEFAULT '300' COMMENT '智能阻断-统计周期autodefence cycle',
  `autodefence_count` int(11) DEFAULT '10' COMMENT '智能阻断-入侵次数aotodefence count',
  `autodefence_second` int(11) DEFAULT '3600' COMMENT '智能阻断-基准阻断时间aotodefence second',
  `is_bypass` tinyint(3) DEFAULT '0' COMMENT 'Bypass设置启用0disable 1enable',
  `is_autodiskclean` tinyint(3) DEFAULT '0' COMMENT '是否开启自动清理 0disable 1enable',
  `autodiskclean` tinyint(3) DEFAULT '70' COMMENT '磁盘阀值percent',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='security setting';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_securityset`
--

LOCK TABLES `t_securityset` WRITE;
/*!40000 ALTER TABLE `t_securityset` DISABLE KEYS */;
INSERT INTO `t_securityset` VALUES (1,0,'','','Googlebot|Adsbot|baiduspider|YodaoBot|360Spider','',0,'法轮功|李洪志|大纪元|真善忍|新唐人|毛一鲜|黎阳平|张小平|戴海静|赵紫阳|胡耀邦|六四事件|退党|天葬|禁书|枪决现场|疆独|藏独|反共|中共|达赖|班禅|东突|台独|台海|肉棍|淫靡|淫水|迷药|迷昏药|色情服务|成人片|三级片|激情小电影|黄色小电影|色情小电影|援交|打炮|口活|吹萧|打飞机|冰火|毒龙|全身漫游|休闲按摩|丝袜美女|推油|毛片|淫荡|骚妇|熟女|成人电影|换妻|丝袜美足|走光|摇头丸|海洛因|白面|迷幻醉|春药|催情|三唑仑|麻醉乙醚|遗忘药|佳境安定片|蒙汗药粉|麻醉药|买卖枪支|出售枪支|投毒杀人|手机复制|麻醉钢枪|枪支弹药|鬼村|雷管|古方迷香|强效忆药|迷奸药|代考|考研枪手|套牌|刻章|办证|证件集团|办理证件|窃听器|汽车解码器|汽车拦截器|开锁枪|侦探设备|远程偷拍|电表反转调效器|特码|翻牌|办理文凭|代开发票|监听王|透视眼镜|黑钱|毒品|洗钱|帮派',0,0,300,10,600,0,1,60);
/*!40000 ALTER TABLE `t_securityset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_selfstudy_ip_white`
--

DROP TABLE IF EXISTS `t_selfstudy_ip_white`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_selfstudy_ip_white` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_use` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  `ip` varchar(15) DEFAULT '' COMMENT 'ip',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_selfstudy_ip_white`
--

LOCK TABLES `t_selfstudy_ip_white` WRITE;
/*!40000 ALTER TABLE `t_selfstudy_ip_white` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_selfstudy_ip_white` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_selfstudy_result`
--

DROP TABLE IF EXISTS `t_selfstudy_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_selfstudy_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri_max` int(11) DEFAULT '0' COMMENT 'max length of uri',
  `arg_name_max` int(11) DEFAULT '0' COMMENT 'max length of arg name',
  `arg_content_max` int(11) DEFAULT '0' COMMENT 'max length of arg',
  `arg_count_max` int(11) DEFAULT '0' COMMENT 'max number of arg',
  `cookie_max` int(11) DEFAULT '0' COMMENT 'max length of cookie string',
  `cookie_name_max` int(11) DEFAULT '0' COMMENT 'max length of cookie name',
  `cookie_content_max` int(11) DEFAULT '0' COMMENT 'max length of cookie',
  `cookie_count_max` int(11) DEFAULT '0' COMMENT 'max number of cookie',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_selfstudy_result`
--

LOCK TABLES `t_selfstudy_result` WRITE;
/*!40000 ALTER TABLE `t_selfstudy_result` DISABLE KEYS */;
INSERT INTO `t_selfstudy_result` VALUES (1,200,18,75,7,478,15,192,11);
/*!40000 ALTER TABLE `t_selfstudy_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_selfstudy_setting`
--

DROP TABLE IF EXISTS `t_selfstudy_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_selfstudy_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_use` tinyint(3) DEFAULT '0' COMMENT '启用自学习0disable 1enable',
  `is_ip_white` tinyint(3) DEFAULT '0' COMMENT '启用访问白名单0disable 1enable',
  `is_ip_black` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  `is_domain_black` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  `is_use_result` tinyint(3) DEFAULT '0' COMMENT '是否应用学习结果0disable 1enable',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_selfstudy_setting`
--

LOCK TABLES `t_selfstudy_setting` WRITE;
/*!40000 ALTER TABLE `t_selfstudy_setting` DISABLE KEYS */;
INSERT INTO `t_selfstudy_setting` VALUES (1,0,0,0,0,0);
/*!40000 ALTER TABLE `t_selfstudy_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_selfstudyrule`
--

DROP TABLE IF EXISTS `t_selfstudyrule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_selfstudyrule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruleid` int(11) NOT NULL COMMENT 'hit rule id',
  `realruleid` int(11) NOT NULL COMMENT 'hit rule realid',
  `is_use` tinyint(4) DEFAULT '1' COMMENT '0disable 1enable',
  `uri` varchar(255) DEFAULT NULL COMMENT 'uri',
  `host` varchar(255) DEFAULT NULL COMMENT 'host',
  `sourceip` varchar(15) DEFAULT NULL COMMENT 'sourceip',
  `sourceport` varchar(5) DEFAULT NULL COMMENT 'sourceport',
  PRIMARY KEY (`id`),
  UNIQUE KEY `realruleid` (`realruleid`,`uri`,`host`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='self study rule';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_selfstudyrule`
--

LOCK TABLES `t_selfstudyrule` WRITE;
/*!40000 ALTER TABLE `t_selfstudyrule` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_selfstudyrule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_sessions`
--

DROP TABLE IF EXISTS `t_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sessions` (
  `username` varchar(16) NOT NULL,
  `dateline` int(11) NOT NULL,
  `role` tinyint(4) NOT NULL,
  `exptime` int(11) NOT NULL,
  PRIMARY KEY (`username`)
) ENGINE=MEMORY DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_sessions`
--

LOCK TABLES `t_sessions` WRITE;
/*!40000 ALTER TABLE `t_sessions` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_severity`
--

DROP TABLE IF EXISTS `t_severity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_severity` (
  `severity` tinyint(4) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `desc` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`severity`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='告警等级';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_severity`
--

LOCK TABLES `t_severity` WRITE;
/*!40000 ALTER TABLE `t_severity` DISABLE KEYS */;
INSERT INTO `t_severity` VALUES (0,'EMERGENCY','紧急');
INSERT INTO `t_severity` VALUES (1,'ALERT','警报');
INSERT INTO `t_severity` VALUES (2,'CRITICAL','严重');
INSERT INTO `t_severity` VALUES (3,'ERROR','错误');
INSERT INTO `t_severity` VALUES (4,'WARNING','警告');
INSERT INTO `t_severity` VALUES (5,'NOTICE','通知');
INSERT INTO `t_severity` VALUES (6,'INFO','信息');
INSERT INTO `t_severity` VALUES (7,'DEBUG','调试');
/*!40000 ALTER TABLE `t_severity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_sitestatus`
--

DROP TABLE IF EXISTS `t_sitestatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(1024) DEFAULT NULL COMMENT '监控目标URL',
  `time` int(11) DEFAULT NULL COMMENT '最近执行时间',
  `status` tinyint(3) DEFAULT '0' COMMENT '是否启用0:disable 1:enable',
  `result` tinyint(3) DEFAULT '0' COMMENT '状态0:unnormal 1:normal',
  `desc` varchar(512) DEFAULT '',
  `protype` varchar(255) DEFAULT NULL,
  `freq` int(11) DEFAULT NULL,
  `responsetime` float DEFAULT NULL COMMENT '响应时间',
  `type` tinyint(4) DEFAULT '0',
  `rate` int(10) DEFAULT NULL COMMENT '监控频率',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=47 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_sitestatus`
--

LOCK TABLES `t_sitestatus` WRITE;
/*!40000 ALTER TABLE `t_sitestatus` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_sitestatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_sitestatus_all`
--

DROP TABLE IF EXISTS `t_sitestatus_all`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_all` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(1024) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `status` tinyint(4) DEFAULT '0' COMMENT '0:disable 1:enable',
  `result` tinyint(4) DEFAULT '0' COMMENT '0:unnormal 1:normal',
  `desc` varchar(512) COLLATE utf8_unicode_ci DEFAULT '',
  `protype` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `freq` int(11) DEFAULT NULL,
  `responsetime` float DEFAULT NULL,
  `type` tinyint(4) DEFAULT '0',
  `rate` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MRG_MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci INSERT_METHOD=LAST UNION=(`logs`.`t_sitestatus_20171214`);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_snat`
--

DROP TABLE IF EXISTS `t_snat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_snat` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `sourceAddress` varchar(512) DEFAULT NULL COMMENT '来源地址',
  `sourceNetmask` varchar(255) DEFAULT NULL COMMENT '来源掩码位数',
  `sourceAddresstype` varchar(255) DEFAULT NULL COMMENT '来源地址类型，1：单ip，2：ip段',
  `targetAddress` varchar(512) DEFAULT NULL COMMENT '目的地址',
  `targetNetmask` varchar(255) DEFAULT NULL COMMENT '目的掩码位数',
  `targetAddresstype` varchar(255) DEFAULT NULL COMMENT '目的地址类型，1：单ip，2：ip段',
  `converType` tinyint(2) DEFAULT NULL COMMENT '转换类型，1为指定IP，2为地址池，3为流出网口',
  `converTypeValue` varchar(128) DEFAULT NULL COMMENT '转换类型值',
  `sort` int(11) DEFAULT NULL COMMENT '排序',
  `isLog` tinyint(2) DEFAULT '1' COMMENT '是否记录日志，0否，1是',
  `status` tinyint(2) DEFAULT NULL COMMENT '状态：1：启用 0：不启用',
  `snatName` varchar(128) DEFAULT NULL COMMENT '名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_snat`
--

LOCK TABLES `t_snat` WRITE;
/*!40000 ALTER TABLE `t_snat` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_snat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_snmp_up`
--

DROP TABLE IF EXISTS `t_snmp_up`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_snmp_up` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_use` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  `version` varchar(16) DEFAULT '' COMMENT 'version',
  `ip` varchar(32) DEFAULT '' COMMENT 'ip',
  `port` varchar(16) DEFAULT '' COMMENT 'port',
  `community` varchar(32) DEFAULT '' COMMENT 'community',
  `version2` varchar(16) DEFAULT '' COMMENT 'version',
  `ip2` varchar(32) DEFAULT '' COMMENT 'ip',
  `port2` varchar(16) DEFAULT '' COMMENT 'port',
  `community2` varchar(32) DEFAULT '' COMMENT 'community',
  `version3` varchar(16) DEFAULT '' COMMENT 'version',
  `ip3` varchar(32) DEFAULT '' COMMENT 'ip',
  `port3` varchar(16) DEFAULT '' COMMENT 'port',
  `community3` varchar(32) DEFAULT '' COMMENT 'community',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='snmp trap upstream setting';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_snmp_up`
--

LOCK TABLES `t_snmp_up` WRITE;
/*!40000 ALTER TABLE `t_snmp_up` DISABLE KEYS */;
INSERT INTO `t_snmp_up` VALUES (1,0,'','','','','','','','','','','','');
/*!40000 ALTER TABLE `t_snmp_up` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_spiders`
--

DROP TABLE IF EXISTS `t_spiders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_spiders` (
  `id` smallint(6) NOT NULL,
  `type` varchar(255) NOT NULL COMMENT 'spider category',
  `name` varchar(255) NOT NULL COMMENT 'spider''s name',
  `feature` varchar(45) NOT NULL COMMENT 'spider''s http head feature',
  `ips` varchar(255) DEFAULT NULL COMMENT 'the spider''s ip, Multiple ip separated by ''|'',  example:1.1.1.1|2.2.2.2',
  `status` tinyint(4) DEFAULT '1' COMMENT '0disable 1enable',
  `update_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_spiders`
--

LOCK TABLES `t_spiders` WRITE;
/*!40000 ALTER TABLE `t_spiders` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_spiders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_staticroute`
--

DROP TABLE IF EXISTS `t_staticroute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_staticroute` (
  `nic` varchar(45) DEFAULT NULL,
  `isdefault` tinyint(4) DEFAULT NULL COMMENT '1 default  route set 0 not default',
  `dest` varchar(45) DEFAULT NULL COMMENT 'dest ip',
  `mask` varchar(45) DEFAULT NULL,
  `gateway` varchar(45) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='the static route info';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_staticroute`
--

LOCK TABLES `t_staticroute` WRITE;
/*!40000 ALTER TABLE `t_staticroute` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_staticroute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_sysinfo`
--

DROP TABLE IF EXISTS `t_sysinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sysinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` int(11) DEFAULT NULL,
  `cpu_ratio` tinyint(4) DEFAULT NULL COMMENT 'cpu used ratio',
  `total_mem` int(11) DEFAULT NULL COMMENT 'total memory',
  `used_mem` int(11) DEFAULT NULL COMMENT 'used memory',
  `total_disk` int(11) DEFAULT NULL COMMENT 'total disk space',
  `used_disk` int(11) DEFAULT NULL COMMENT 'used disk space',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='system info';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_sysinfo`
--

LOCK TABLES `t_sysinfo` WRITE;
/*!40000 ALTER TABLE `t_sysinfo` DISABLE KEYS */;
INSERT INTO `t_sysinfo` VALUES (1,1509865123,10,15817,7369,938628,23441);
/*!40000 ALTER TABLE `t_sysinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_syslog_up`
--

DROP TABLE IF EXISTS `t_syslog_up`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_syslog_up` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_use` tinyint(4) DEFAULT '0' COMMENT '0disable 1enable',
  `ip` varchar(32) DEFAULT '' COMMENT 'ip',
  `port` varchar(16) DEFAULT '' COMMENT 'port',
  `method` varchar(32) DEFAULT '' COMMENT 'method',
  `ip2` varchar(32) DEFAULT '' COMMENT 'ip',
  `port2` varchar(16) DEFAULT '' COMMENT 'port',
  `method2` varchar(32) DEFAULT '' COMMENT 'method',
  `ip3` varchar(32) DEFAULT '' COMMENT 'ip',
  `port3` varchar(16) DEFAULT '' COMMENT 'port',
  `method3` varchar(32) DEFAULT '' COMMENT 'method',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='syslog upstream setting';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_syslog_up`
--

LOCK TABLES `t_syslog_up` WRITE;
/*!40000 ALTER TABLE `t_syslog_up` DISABLE KEYS */;
INSERT INTO `t_syslog_up` VALUES (1,0,'','','','','','','','','');
/*!40000 ALTER TABLE `t_syslog_up` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_urlgroup`
--

DROP TABLE IF EXISTS `t_urlgroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_urlgroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sURLGroupName` varchar(32) DEFAULT NULL COMMENT 'URL组名称',
  `sGroupDesc` varchar(32) DEFAULT NULL COMMENT 'URL组描述',
  `sURL` text COMMENT 'URL',
  `iType` tinyint(1) DEFAULT '1' COMMENT '类型，1为内置，2为自定义',
  `sDomainKey` varchar(128) DEFAULT NULL COMMENT '域名关键字',
  `sURLGNameFirstWord` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=74 DEFAULT CHARSET=utf8 COMMENT='URL类型组';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_urlgroup`
--

LOCK TABLES `t_urlgroup` WRITE;
/*!40000 ALTER TABLE `t_urlgroup` DISABLE KEYS */;
INSERT INTO `t_urlgroup` VALUES (2,'被感染的网站','被病毒或木马感染的站点','/usr/local/bdwaf/conf/URLs/被感染的网站.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (3,'仇恨和偏执','描述敌意或基于种族、宗教、国籍等包含仇恨与偏执情绪内容的站点','/usr/local/bdwaf/conf/URLs/仇恨和偏执.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (4,'低俗','内容低级趣味、毫无营养价值的站点','/usr/local/bdwaf/conf/URLs/低俗.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (5,'点对点网络','通过分发软件来简化直接交换用户之间的文件的站点','/usr/local/bdwaf/conf/URLs/点对点网络.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (6,'电子邮件','提供基于 Web 的电子邮件服务和邮件列表服务的站点','/usr/local/bdwaf/conf/URLs/电子邮件.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (7,'赌博','用户可在其中下注或参与赌池活动，或接收此类活动的信息、培训的站点','/usr/local/bdwaf/conf/URLs/赌博.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (8,'儿童色情','包括未成年人参与明显性行为的可视描绘内容的站点','/usr/local/bdwaf/conf/URLs/儿童色情.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (9,'翻译','可让您翻译文本（单词、短语、网页、各种语言之间的文本）的站点','/usr/local/bdwaf/conf/URLs/翻译.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (10,'犯罪活动','推崇或宣扬违法犯罪活动的站点','/usr/local/bdwaf/conf/URLs/犯罪活动.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (11,'饭店与餐饮','提供餐馆信息、外卖派送等服务的站点','/usr/local/bdwaf/conf/URLs/饭店与餐饮.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (12,'房地产','提供房地产或不动产租借、购买或销售相关信息的站点','/usr/local/bdwaf/conf/URLs/房地产.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (13,'非法软件','提供盗版软件信息及下载服务的站点','/usr/local/bdwaf/conf/URLs/非法软件.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (14,'非营利组织和非政府组织','提供非营利组织和非政府组织的新闻、信息及活动等内容的站点','/usr/local/bdwaf/conf/URLs/非营利组织和非政府组织.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (15,'个人网站','主要提供个人网页和博客访问权的站点','/usr/local/bdwaf/conf/URLs/个人网站.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (16,'购物','提供货物或服务购买方式或投放相关广告的站点','/usr/local/bdwaf/conf/URLs/购物.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (17,'广告及弹窗','提供在线广告或横幅的站点','/usr/local/bdwaf/conf/URLs/广告及弹窗.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (18,'贺卡','帮助发送通常用于庆祝某事件或重要时刻的电子贺卡、动画卡的站点','/usr/local/bdwaf/conf/URLs/贺卡.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (19,'黑客','分发、促销或提供黑客工具和/或信息的站点','/usr/local/bdwaf/conf/URLs/黑客.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (20,'即时通讯','提供聊天、短信 (SMS) 或即时消息功能或客户端下载的站点','/usr/local/bdwaf/conf/URLs/即时通讯.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (21,'计算机技术','主办计算机、技术、Internet 和技术相关组织或公司的站点','/usr/local/bdwaf/conf/URLs/计算机技术.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (22,'僵尸网络','僵尸网络发送数据使用的目标站点，或接收命令和控制指令使用的源站点','/usr/local/bdwaf/conf/URLs/僵尸网络.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (23,'教育','提供教育信息、远程学习或职业学校信息或学习计划的站点','/usr/local/bdwaf/conf/URLs/教育.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (24,'金融','提供银行服务或其他类型的金融信息或投放相关广告的站点','/usr/local/bdwaf/conf/URLs/金融.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (25,'垃圾网站','正在构建、暂停域、搜索诱售机会或其他形式的通常没有有用价值的站点','/usr/local/bdwaf/conf/URLs/垃圾网站.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (26,'流媒体及下载','提供电视、电影、网络摄像机或其他视频内容数据流或相关下载的站点','/usr/local/bdwaf/conf/URLs/流媒体及下载.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (27,'论坛与新闻组','主要为以下对象提供访问权的站点：新闻组、消息或布告栏系统','/usr/local/bdwaf/conf/URLs/论坛与新闻组.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (28,'裸体','包含人体裸体或半裸描绘内容的站点','/usr/local/bdwaf/conf/URLs/裸体.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (29,'旅游','促销或提供机会实现旅游计划的站点','/usr/local/bdwaf/conf/URLs/旅游.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (30,'匿名网站','具有非恶意、非唐突内容资源，不可通过浏览器直接查看的站点','/usr/local/bdwaf/conf/URLs/匿名网站.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (31,'普通网站','需要禁止访问，但又不归入其他分类的网站','/usr/local/bdwaf/conf/URLs/普通网站.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (32,'求职','提供求职帮助以及查找预期雇主的工具的站点','/usr/local/bdwaf/conf/URLs/求职.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (33,'软件下载','致力于各种类型计算机或移动设备的软件电子下载（收费或免费）的站点','/usr/local/bdwaf/conf/URLs/软件下载.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (34,'色情','包含旨在激发性欲或淫欲的明显性材料的站点','/usr/local/bdwaf/conf/URLs/色情.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (35,'商业','专注于商行、商业信息、经济、营销、商业管理和创业的站点','/usr/local/bdwaf/conf/URLs/商业.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (36,'社交网络','让用户与他人建立联系以形成在线团体的站点','/usr/local/bdwaf/conf/URLs/社交网络.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (37,'时装与美容','提供服饰搭配、美容知识等方面内容的站点','/usr/local/bdwaf/conf/URLs/时装与美容.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (38,'搜索引擎和门户网站','支持搜索 Internet、索引和目录的站点','/usr/local/bdwaf/conf/URLs/搜索引擎和门户网站.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (39,'体育','提供体育赛事信息、运动员信息、运动知识等体育运动相关知识的站点','/usr/local/bdwaf/conf/URLs/体育.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (40,'停放域名','使用域名停放服务的站点','/usr/local/bdwaf/conf/URLs/停放域名.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (41,'图片共享','可让您共享图片共享，但具有以下低风险的站点：包括有伤风化的内容','/usr/local/bdwaf/conf/URLs/图片共享.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (42,'网络钓鱼与欺诈','针对显示为合法银行或零售商，意图以欺诈方式捕获敏感数据设计的站点','/usr/local/bdwaf/conf/URLs/网络钓鱼与欺诈.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (43,'网络故障','提供网络故障信息、原因分析、解决办法等内容的站点','/usr/local/bdwaf/conf/URLs/网络故障.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (44,'网络聊天室','提供多人通过文字与符号进行实时交谈、聊天的场所','/usr/local/bdwaf/conf/URLs/网络聊天室.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (45,'违禁药物','提供、销售等方式提倡非法使用、制造或分发毒品及其他违禁药物的站点','/usr/local/bdwaf/conf/URLs/违禁药物.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (46,'武器','销售、评论或介绍武器（如枪、刀或武术兵器）的站点','/usr/local/bdwaf/conf/URLs/武器.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (47,'恶意软件','承载或分发恶意软件的站点','/usr/local/bdwaf/conf/URLs/恶意软件.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (48,'邪教','邪教分子用来制造、散布歪理邪说等手段蛊惑、蒙骗他人的站点','/usr/local/bdwaf/conf/URLs/邪教.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (49,'新闻','主要报告有关每天最新事件或当前问题的信息或评论的站点','/usr/local/bdwaf/conf/URLs/新闻.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (50,'信息安全','提供信息安全相关方面的文章、视频、软件等内容的站点','/usr/local/bdwaf/conf/URLs/信息安全.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (51,'性教育','提供有关生殖、性发育、安全性行为、性特征、改善性行为等信息的站点','/usr/local/bdwaf/conf/URLs/性教育.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (52,'休闲娱乐','提供休闲娱乐信息的站点','/usr/local/bdwaf/conf/URLs/休闲娱乐.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (53,'学校作弊','关于在学校里作弊行为相关的站点，如销售作弊工具、提供作弊信息','/usr/local/bdwaf/conf/URLs/学校作弊.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (54,'烟酒','供应销售、促销、推崇、评论或以任何方式提倡使用或制作烟酒的站点','/usr/local/bdwaf/conf/URLs/烟酒.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (55,'医药卫生','提供医疗卫生信息的站点，如医院资讯、医学知识、医疗新闻等信息','/usr/local/bdwaf/conf/URLs/医药卫生.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (56,'艺术','培养和促进艺术文化理解(如绘画、音乐、舞蹈、雕塑等)的站点','/usr/local/bdwaf/conf/URLs/艺术.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (57,'游戏','支持玩耍或下载视频游戏、计算机游戏或电子游戏的站点','/usr/local/bdwaf/conf/URLs/游戏.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (58,'娱乐','针对大众娱乐媒体（如电影、电视、娱乐杂志等）提供信息或促销的站点','/usr/local/bdwaf/conf/URLs/娱乐.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (59,'约会和交友','提供陌生人之间认识、互相交流场所的站点','/usr/local/bdwaf/conf/URLs/约会和交友.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (60,'运输','提供关于运输行业、交通方面信息等内容的站点','/usr/local/bdwaf/conf/URLs/运输.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (61,'政府机构','提供政府机构信息及新闻活动等方面知识的站点','/usr/local/bdwaf/conf/URLs/政府机构.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (62,'政治','由政党或任何促进公共政策、民意、社会实践等组织赞助的站点','/usr/local/bdwaf/conf/URLs/政治.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (63,'专用网络','指遵守RFC1918和RFC4193规范，使用私有IP地址的网络','/usr/local/bdwaf/conf/URLs/专用网络.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (64,'宗教','推广传统组织宗教信仰、习惯、仪式以及直接相关主题的站点','/usr/local/bdwaf/conf/URLs/宗教.txt',1,NULL,NULL);
INSERT INTO `t_urlgroup` VALUES (73,'URL','111','www.sss.com,www.ccc.com,www.666.com',2,NULL,NULL);
/*!40000 ALTER TABLE `t_urlgroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_urltrait`
--

DROP TABLE IF EXISTS `t_urltrait`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_urltrait` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) DEFAULT NULL,
  `method` varchar(8) DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  `trait` text NOT NULL,
  `urlStr` varchar(2048) NOT NULL,
  `port` int(11) DEFAULT NULL COMMENT '被访问的端口',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16868 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_urltrait`
--

LOCK TABLES `t_urltrait` WRITE;
/*!40000 ALTER TABLE `t_urltrait` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_urltrait` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_urltraitsupport`
--

DROP TABLE IF EXISTS `t_urltraitsupport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_urltraitsupport` (
  `lastPos` bigint(255) DEFAULT NULL,
  `fileSize` bigint(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_urltraitsupport`
--

LOCK TABLES `t_urltraitsupport` WRITE;
/*!40000 ALTER TABLE `t_urltraitsupport` DISABLE KEYS */;
INSERT INTO `t_urltraitsupport` VALUES (406427178,406427178);
/*!40000 ALTER TABLE `t_urltraitsupport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_user`
--

DROP TABLE IF EXISTS `t_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(16) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(32) NOT NULL,
  `createtime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `role` tinyint(4) NOT NULL COMMENT '1system manager, 2safe manager, 3safe auditer',
  `errors` tinyint(4) DEFAULT NULL,
  `locktime` int(11) DEFAULT NULL,
  `name` varchar(20) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `status` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_user`
--

LOCK TABLES `t_user` WRITE;
/*!40000 ALTER TABLE `t_user` DISABLE KEYS */;
INSERT INTO `t_user` VALUES (1,'root','admin@163.com','ab45b530205df9d2a92f612693849c25','2014-03-10 06:55:38',0,0,0,'','',1);
INSERT INTO `t_user` VALUES (2,'admin','','86f3059b228c8acf99e69734b6bb32cc','2014-03-10 06:55:38',1,0,0,'','',1);
INSERT INTO `t_user` VALUES (3,'secure','','83aa1716e6ebe3c70a87e92b35d96594','2014-03-10 06:55:38',2,0,0,'','',1);
INSERT INTO `t_user` VALUES (4,'audit','','650e61f36277d0a6466299ffe82b9d34','2014-03-10 06:55:38',3,0,0,'','',1);
/*!40000 ALTER TABLE `t_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_userconfig`
--

DROP TABLE IF EXISTS `t_userconfig`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_userconfig` (
  `maxError` tinyint(3) NOT NULL,
  `lockTime` tinyint(5) NOT NULL,
  PRIMARY KEY (`maxError`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_userconfig`
--

LOCK TABLES `t_userconfig` WRITE;
/*!40000 ALTER TABLE `t_userconfig` DISABLE KEYS */;
INSERT INTO `t_userconfig` VALUES (5,15);
/*!40000 ALTER TABLE `t_userconfig` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_userrole`
--

DROP TABLE IF EXISTS `t_userrole`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_userrole` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `roles` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_userrole`
--

LOCK TABLES `t_userrole` WRITE;
/*!40000 ALTER TABLE `t_userrole` DISABLE KEYS */;
INSERT INTO `t_userrole` VALUES (1,'系统管理员','');
INSERT INTO `t_userrole` VALUES (2,'安全管理员','');
INSERT INTO `t_userrole` VALUES (3,'安全审计员','');
/*!40000 ALTER TABLE `t_userrole` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_vlan`
--

DROP TABLE IF EXISTS `t_vlan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_vlan` (
  `nets` varchar(256) DEFAULT NULL,
  `ip` varchar(256) DEFAULT NULL,
  `vlan_id` varchar(256) DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_vlan`
--

LOCK TABLES `t_vlan` WRITE;
/*!40000 ALTER TABLE `t_vlan` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_vlan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_wafssh`
--

DROP TABLE IF EXISTS `t_wafssh`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_wafssh` (
  `wafssh` enum('On','Off') COLLATE utf8_unicode_ci DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_wafssh`
--

LOCK TABLES `t_wafssh` WRITE;
/*!40000 ALTER TABLE `t_wafssh` DISABLE KEYS */;
INSERT INTO `t_wafssh` VALUES ('Off',1);
/*!40000 ALTER TABLE `t_wafssh` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_web_connections_all`
--

DROP TABLE IF EXISTS `t_web_connections_all`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_all` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MRG_MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci INSERT_METHOD=LAST UNION=(`logs`.`t_web_connections_20171122`,`logs`.`t_web_connections_20171123`);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_webguard`
--

DROP TABLE IF EXISTS `t_webguard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_webguard` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(1024) DEFAULT NULL,
  `username` varchar(45) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_webguard`
--

LOCK TABLES `t_webguard` WRITE;
/*!40000 ALTER TABLE `t_webguard` DISABLE KEYS */;
INSERT INTO `t_webguard` VALUES (1,'http://',NULL,NULL);
/*!40000 ALTER TABLE `t_webguard` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_webserver_outbound`
--

DROP TABLE IF EXISTS `t_webserver_outbound`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_webserver_outbound` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_use` tinyint(3) DEFAULT '0' COMMENT '0disable 1enable  0是白名单，1是黑',
  `sip` varchar(15) DEFAULT '' COMMENT 'source ip源IP',
  `dip` varchar(15) DEFAULT '' COMMENT 'dest ip目标IP',
  `dport` varchar(5) DEFAULT '' COMMENT 'dest port目标端口',
  PRIMARY KEY (`id`),
  UNIQUE KEY `sip` (`sip`,`dip`,`dport`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_webserver_outbound`
--

LOCK TABLES `t_webserver_outbound` WRITE;
/*!40000 ALTER TABLE `t_webserver_outbound` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_webserver_outbound` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_webserver_outbound_port`
--

DROP TABLE IF EXISTS `t_webserver_outbound_port`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_webserver_outbound_port` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_use` tinyint(3) DEFAULT '0' COMMENT '启用状态0disable 1enable',
  `dports` varchar(1024) DEFAULT '' COMMENT '检测端口dest port',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_webserver_outbound_port`
--

LOCK TABLES `t_webserver_outbound_port` WRITE;
/*!40000 ALTER TABLE `t_webserver_outbound_port` DISABLE KEYS */;
INSERT INTO `t_webserver_outbound_port` VALUES (1,1,'80|443|8080');
/*!40000 ALTER TABLE `t_webserver_outbound_port` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_website`
--

DROP TABLE IF EXISTS `t_website`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_website` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `sGroupName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '站点host',
  `sWebSiteIP` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '站点ip',
  `iWebSitePort` int(11) DEFAULT NULL COMMENT '站点端口',
  `sWebSiteProtocol` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '协议',
  `iWebSiteGroupId` int(11) DEFAULT NULL COMMENT 't_website_group的id',
  `ruleModelId` int(11) DEFAULT NULL COMMENT '策略模板Id',
  `selfRuleModelId` int(11) DEFAULT NULL COMMENT '自己特殊的策略模板Id',
  `daymaxtraffic` varchar(1024) COLLATE utf8_unicode_ci DEFAULT '' COMMENT '24小时每小时最大流量模型，json格式',
  `dayipmaxvisit` varchar(1024) COLLATE utf8_unicode_ci DEFAULT '' COMMENT '24小时每小时单ip最大访问数，json格式',
  `modelingstartdate` date DEFAULT NULL COMMENT '24小时建模开始日期',
  `modelingperiod` int(11) DEFAULT NULL COMMENT '建模的时间周期，以天为单位',
  `modelingendday` date DEFAULT NULL COMMENT '建模结束时间',
  `mstatus` tinyint(1) DEFAULT '0' COMMENT '建模状态: 0未建模 1学习中 2学习完成 3已放弃 4未开启',
  `studyTime` smallint(6) DEFAULT '0' COMMENT '学习时间（天）',
  `beginTime` datetime DEFAULT NULL COMMENT '学习开始时间',
  `endTime` datetime DEFAULT NULL COMMENT '学习结束时间',
  `remarks` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '动态建模备注',
  `isproxy` tinyint(1) DEFAULT '0' COMMENT '是否是反向代理的点:1是0不是',
  `ddosfencetype` varchar(8) COLLATE utf8_unicode_ci DEFAULT 'waf' COMMENT 'ddos攻击防护类型: waf:本机防御  cloudfence:云防线防护',
  `hatype` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '负载均衡方式HA Algorithm:1poll, 2IP hash, 3weight',
  `type` tinyint(3) DEFAULT '1' COMMENT '类型1:website 2:porxy',
  `cache` tinyint(3) DEFAULT '0' COMMENT '开启缓存0:no cache 1:cache',
  `helthcheck` tinyint(3) DEFAULT '0' COMMENT '启用健康检查0 no check, 1 check',
  `ssl_path1` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '证书公钥ssl file path1',
  `ssl_path2` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '证书密钥ssl file path2',
  `porxy_remark` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '反向代理说明proxy remark information',
  `modsec_status` varchar(16) COLLATE utf8_unicode_ci DEFAULT 'on' COMMENT 'DetectionOnly, on, off',
  `modsec_requestbody_access_switch` tinyint(4) DEFAULT '1' COMMENT '0:off 1:on',
  PRIMARY KEY (`id`),
  UNIQUE KEY `sWebSiteName` (`sWebSiteName`,`iWebSitePort`),
  KEY `group_model_id` (`ruleModelId`),
  KEY `self_model_id` (`selfRuleModelId`),
  KEY `group_id` (`iWebSiteGroupId`),
  CONSTRAINT `group_id` FOREIGN KEY (`iWebSiteGroupId`) REFERENCES `t_website_group` (`id`),
  CONSTRAINT `group_model_id` FOREIGN KEY (`ruleModelId`) REFERENCES `t_rule_model` (`id`),
  CONSTRAINT `self_model_id` FOREIGN KEY (`selfRuleModelId`) REFERENCES `t_rule_model` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='站点';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_website`
--

LOCK TABLES `t_website` WRITE;
/*!40000 ALTER TABLE `t_website` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_website` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_website_group`
--

DROP TABLE IF EXISTS `t_website_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_website_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `groupName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '站点组名称',
  `ruleModelId` int(11) DEFAULT NULL COMMENT '策略模板Id',
  `explanation` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '说明',
  PRIMARY KEY (`id`),
  KEY `groupRuleModelId` (`ruleModelId`),
  CONSTRAINT `groupRuleModelId` FOREIGN KEY (`ruleModelId`) REFERENCES `t_rule_model` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='站点组';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_website_group`
--

LOCK TABLES `t_website_group` WRITE;
/*!40000 ALTER TABLE `t_website_group` DISABLE KEYS */;
INSERT INTO `t_website_group` VALUES (1,'未分类站点',2,'站点组');
/*!40000 ALTER TABLE `t_website_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_website_nginx`
--

DROP TABLE IF EXISTS `t_website_nginx`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_website_nginx` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nginxsizes` bigint(20) DEFAULT NULL COMMENT 'nginx log',
  `hournginxsize` bigint(20) DEFAULT '0' COMMENT '以小时为单位，记录access log日志大小',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_website_nginx`
--

LOCK TABLES `t_website_nginx` WRITE;
/*!40000 ALTER TABLE `t_website_nginx` DISABLE KEYS */;
INSERT INTO `t_website_nginx` VALUES (1,314418,406427178);
/*!40000 ALTER TABLE `t_website_nginx` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_website_servers`
--

DROP TABLE IF EXISTS `t_website_servers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_website_servers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'ip地址',
  `port` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '端口',
  `protocol` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '协议:http/https',
  `os` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '操作系统',
  `db` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '数据库',
  `webServer` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'web服务器，如：nginx',
  `developmentLanguage` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '开发语言',
  `remark` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '备注',
  `createTime` datetime DEFAULT NULL COMMENT '创建时间',
  `refreshTime` datetime DEFAULT NULL COMMENT '更新时间',
  `webSiteId` int(255) NOT NULL DEFAULT '0' COMMENT 't_website的id',
  `type` tinyint(4) DEFAULT '1' COMMENT '1:website  2:porxy',
  `weight` tinyint(3) DEFAULT '1' COMMENT '权重proxy weight',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='站点服务器';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_website_servers`
--

LOCK TABLES `t_website_servers` WRITE;
/*!40000 ALTER TABLE `t_website_servers` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_website_servers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-03-09 10:35:55
