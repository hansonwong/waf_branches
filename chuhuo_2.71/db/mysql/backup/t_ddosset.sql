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
INSERT INTO `t_ddosset` VALUES (1,1024,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,10000,1,0,0);
/*!40000 ALTER TABLE `t_ddosset` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-23 16:49:10
