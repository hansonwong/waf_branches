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
-- Table structure for table `t_intelligent_Trojan_horse_set`
--

DROP TABLE IF EXISTS `t_intelligent_Trojan_horse_set`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_intelligent_Trojan_horse_set` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` tinyint(3) NOT NULL DEFAULT '0' COMMENT '启用状态：0未启用，1启用 (是否启用上传文件分析)',
  `interceptedFileSuffix` varchar(512) NOT NULL DEFAULT '' COMMENT '拦截的文件后缀(自定义指定拦截的文件后缀(如JPG、PNG))',
  `fileSize` int(11) NOT NULL DEFAULT '0' COMMENT '上传文件大小最大值(设置最大的文件分析大小(默认5M))',
  `addTime` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '入库时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='智能木马检测 功能开关表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_intelligent_Trojan_horse_set`
--

LOCK TABLES `t_intelligent_Trojan_horse_set` WRITE;
/*!40000 ALTER TABLE `t_intelligent_Trojan_horse_set` DISABLE KEYS */;
INSERT INTO `t_intelligent_Trojan_horse_set` VALUES (1,1,'jpg|png|py|dot',5,1520844091);
/*!40000 ALTER TABLE `t_intelligent_Trojan_horse_set` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-23 16:50:04
