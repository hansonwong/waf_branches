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
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='IP过滤设置';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_ip_filter_set`
--

LOCK TABLES `t_ip_filter_set` WRITE;
/*!40000 ALTER TABLE `t_ip_filter_set` DISABLE KEYS */;
INSERT INTO `t_ip_filter_set` VALUES (55,'192.168.16.10','',0,1516324130),(56,'192.168.3.192','192.168.3.210',0,1516324130),(57,'172.168.3.3','',0,1516324130);
/*!40000 ALTER TABLE `t_ip_filter_set` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-23 16:50:28
