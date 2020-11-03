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
INSERT INTO `t_selfstudy_result` VALUES (1,50,6,13,2,172,10,166,2);
/*!40000 ALTER TABLE `t_selfstudy_result` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-23 16:52:21
