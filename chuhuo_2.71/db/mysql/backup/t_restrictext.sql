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
INSERT INTO `t_restrictext` VALUES (1,'.asa',0),(2,'.asax',0),(3,'.ascx',0),(4,'.axd',0),(5,'.backup',0),(6,'.bak',0),(7,'.bat',0),(8,'.cdx',0),(9,'.cer',0),(10,'.cfg',0),(11,'.cmd',0),(12,'.com',0),(13,'.config',0),(14,'.conf',0),(15,'.cs',0),(16,'.csproj',0),(17,'.csr',0),(18,'.dat',0),(19,'.db',0),(20,'.dbf',0),(21,'.dll',0),(22,'.dos',0),(23,'.htr',0),(24,'.htw',0),(25,'.ids',0),(26,'.idc',0),(27,'.idq',0),(28,'.inc',0),(29,'.ini',0),(30,'.key',0),(31,'.licx',0),(32,'.lnk',0),(33,'.log',0),(34,'.mdb',0),(35,'.old',0),(36,'.pass',0),(37,'.pdb',0),(38,'.pol',0),(39,'.printer',0),(40,'.pwd',0),(41,'.resources',0),(42,'.resx',0),(43,'.sql',0),(44,'.sys',0),(45,'.vb',0),(46,'.vbs',0),(47,'.vbproj',0),(48,'.vsdisco',0),(49,'.webinfo',0),(50,'.xsd',0),(51,'.xsx',0);
/*!40000 ALTER TABLE `t_restrictext` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-23 16:49:37
