-- MySQL dump 10.13  Distrib 5.6.30, for Linux (x86_64)
--
-- Host: localhost    Database: logs
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
-- Table structure for table `browser`
--

DROP TABLE IF EXISTS `browser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `browser` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(25) COLLATE utf8_unicode_ci NOT NULL,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM AUTO_INCREMENT=977 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `daily`
--

DROP TABLE IF EXISTS `daily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `daily` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `day` varchar(8) COLLATE utf8_unicode_ci NOT NULL,
  `visits` mediumint(8) unsigned NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `day` (`day`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM AUTO_INCREMENT=109796 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain`
--

DROP TABLE IF EXISTS `domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `code` varchar(8) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=894 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `errors`
--

DROP TABLE IF EXISTS `errors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `errors` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `code` varchar(4) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=6865 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `errors404`
--

DROP TABLE IF EXISTS `errors404`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `errors404` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `referer` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=81896 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `filetypes`
--

DROP TABLE IF EXISTS `filetypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `filetypes` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `type` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `bwwithoutcompress` bigint(20) unsigned NOT NULL,
  `bwaftercompress` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1356 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `general`
--

DROP TABLE IF EXISTS `general`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `general` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `visits` mediumint(8) unsigned NOT NULL,
  `visits_unique` mediumint(8) unsigned NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `pages_nv` mediumint(8) unsigned NOT NULL,
  `hits_nv` mediumint(8) unsigned NOT NULL,
  `bandwidth_nv` bigint(20) unsigned NOT NULL,
  `hosts_known` mediumint(8) unsigned NOT NULL,
  `hosts_unknown` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `year_monthed_2` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `domain_2` (`domain`),
  KEY `year_monthed_3` (`year_monthed`)
) ENGINE=MyISAM AUTO_INCREMENT=39 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hours`
--

DROP TABLE IF EXISTS `hours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hours` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `hour` tinyint(3) unsigned NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `domain` (`domain`),
  KEY `year_monthed` (`year_monthed`),
  KEY `year_monthed_2` (`year_monthed`)
) ENGINE=MyISAM AUTO_INCREMENT=143041 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `misc`
--

DROP TABLE IF EXISTS `misc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `misc` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `text` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=59601 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `origin`
--

DROP TABLE IF EXISTS `origin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `origin` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `fromed` varchar(5) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=35761 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `os`
--

DROP TABLE IF EXISTS `os`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `os` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(25) COLLATE utf8_unicode_ci NOT NULL,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM AUTO_INCREMENT=909 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pageref`
--

DROP TABLE IF EXISTS `pageref`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pageref` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `hits` (`hits`)
) ENGINE=MyISAM AUTO_INCREMENT=966 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201101`
--

DROP TABLE IF EXISTS `pages_201101`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201101` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201104`
--

DROP TABLE IF EXISTS `pages_201104`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201104` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201502`
--

DROP TABLE IF EXISTS `pages_201502`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201502` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201503`
--

DROP TABLE IF EXISTS `pages_201503`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201503` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201504`
--

DROP TABLE IF EXISTS `pages_201504`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201504` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201506`
--

DROP TABLE IF EXISTS `pages_201506`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201506` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201507`
--

DROP TABLE IF EXISTS `pages_201507`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201507` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201508`
--

DROP TABLE IF EXISTS `pages_201508`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201508` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201509`
--

DROP TABLE IF EXISTS `pages_201509`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201509` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=55 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201511`
--

DROP TABLE IF EXISTS `pages_201511`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201511` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201512`
--

DROP TABLE IF EXISTS `pages_201512`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201512` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201601`
--

DROP TABLE IF EXISTS `pages_201601`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201601` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=136 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201604`
--

DROP TABLE IF EXISTS `pages_201604`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201604` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201605`
--

DROP TABLE IF EXISTS `pages_201605`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201605` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201606`
--

DROP TABLE IF EXISTS `pages_201606`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201606` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201607`
--

DROP TABLE IF EXISTS `pages_201607`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201607` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201608`
--

DROP TABLE IF EXISTS `pages_201608`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201608` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201609`
--

DROP TABLE IF EXISTS `pages_201609`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201609` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201610`
--

DROP TABLE IF EXISTS `pages_201610`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201610` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201611`
--

DROP TABLE IF EXISTS `pages_201611`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201611` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201612`
--

DROP TABLE IF EXISTS `pages_201612`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201612` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201701`
--

DROP TABLE IF EXISTS `pages_201701`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201701` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201702`
--

DROP TABLE IF EXISTS `pages_201702`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201702` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=91 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201703`
--

DROP TABLE IF EXISTS `pages_201703`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201703` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201704`
--

DROP TABLE IF EXISTS `pages_201704`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201704` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=688 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201705`
--

DROP TABLE IF EXISTS `pages_201705`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201705` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=511 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201706`
--

DROP TABLE IF EXISTS `pages_201706`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201706` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201707`
--

DROP TABLE IF EXISTS `pages_201707`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201707` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=63 DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201708`
--

DROP TABLE IF EXISTS `pages_201708`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201708` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201710`
--

DROP TABLE IF EXISTS `pages_201710`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201710` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pages_201711`
--

DROP TABLE IF EXISTS `pages_201711`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pages_201711` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `robot`
--

DROP TABLE IF EXISTS `robot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `robot` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `hitsrobots` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `hits` (`hits`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `screen`
--

DROP TABLE IF EXISTS `screen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `screen` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `size` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `searchkeywords`
--

DROP TABLE IF EXISTS `searchkeywords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `searchkeywords` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `words` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `searchref`
--

DROP TABLE IF EXISTS `searchref`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `searchref` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `engine` varchar(25) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `domain` (`domain`),
  KEY `year_monthed` (`year_monthed`),
  KEY `hits` (`hits`)
) ENGINE=MyISAM AUTO_INCREMENT=68 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `searchwords`
--

DROP TABLE IF EXISTS `searchwords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `searchwords` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `words` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `session`
--

DROP TABLE IF EXISTS `session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `ranged` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `visits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_alertlogs`
--

DROP TABLE IF EXISTS `t_alertlogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_alertlogs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `AuditLogUniqueID` varchar(24) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `LogDateTime` datetime NOT NULL DEFAULT '1971-10-01 00:00:00' COMMENT '攻击时间',
  `CountryCode` varchar(3) DEFAULT NULL,
  `RegionCode` varchar(8) DEFAULT NULL,
  `City` varchar(32) DEFAULT NULL,
  `SourceIP` varchar(15) NOT NULL DEFAULT '' COMMENT '源IP',
  `SourcePort` varchar(8) DEFAULT NULL COMMENT '源端口',
  `DestinationIP` varchar(15) NOT NULL DEFAULT '' COMMENT '目标IP',
  `DestinationPort` varchar(8) DEFAULT NULL COMMENT '目标端口',
  `Referer` varchar(255) DEFAULT NULL,
  `UserAgent` varchar(255) DEFAULT NULL,
  `HttpMethod` varchar(10) DEFAULT NULL COMMENT 'HTTP请求方式',
  `Url` varchar(512) DEFAULT NULL,
  `HttpProtocol` varchar(16) DEFAULT NULL,
  `Host` varchar(255) DEFAULT NULL COMMENT 'URL地址',
  `RequestContentType` varchar(255) DEFAULT NULL,
  `ResponseContentType` varchar(255) DEFAULT NULL,
  `HttpStatusCode` varchar(4) DEFAULT NULL,
  `GeneralMsg` varchar(512) DEFAULT NULL,
  `Rulefile` varchar(255) NOT NULL,
  `RuleID` varchar(6) DEFAULT NULL,
  `MatchData` varchar(255) DEFAULT NULL,
  `Rev` varchar(128) DEFAULT NULL,
  `Msg` varchar(128) DEFAULT NULL,
  `Severity` varchar(16) DEFAULT NULL COMMENT '危害等级',
  `Tag` varchar(64) DEFAULT NULL,
  `Status` varchar(8) DEFAULT NULL COMMENT '拦截方式',
  `LogSource` varchar(8) NOT NULL DEFAULT '' COMMENT '日志来源 bridge:透明桥日志 proxy:反向代理日志',
  PRIMARY KEY (`id`),
  KEY `SourceIP` (`SourceIP`),
  KEY `LogDateTime` (`LogDateTime`),
  KEY `DestinationIP` (`DestinationIP`),
  KEY `HttpMethod` (`HttpMethod`),
  KEY `Host` (`Host`),
  KEY `Url` (`Url`(333)),
  KEY `DestinationPort` (`DestinationPort`),
  KEY `RuleID` (`RuleID`),
  KEY `Severity` (`Severity`),
  KEY `Status` (`Status`)
) ENGINE=MyISAM AUTO_INCREMENT=766810 DEFAULT CHARSET=utf8 COMMENT='入侵日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_alertreport`
--

DROP TABLE IF EXISTS `t_alertreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_alertreport` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `LogDateTime` datetime DEFAULT NULL,
  `Url` varchar(512) CHARACTER SET utf8 DEFAULT NULL,
  `Host` varchar(255) CHARACTER SET utf8 DEFAULT NULL,
  `TypeName` varchar(45) CHARACTER SET utf8 DEFAULT NULL,
  `SourceIP` varchar(15) CHARACTER SET utf8 NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_areas`
--

DROP TABLE IF EXISTS `t_areas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_areas` (
  `Code` varchar(2) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `Province` varchar(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `Area` varchar(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `Desc` varchar(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`Code`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_auditlog`
--

DROP TABLE IF EXISTS `t_auditlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_auditlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` int(11) NOT NULL,
  `username` varchar(16) DEFAULT NULL,
  `level1` varchar(10) DEFAULT NULL,
  `level2` varchar(10) DEFAULT NULL,
  `level3` varchar(10) DEFAULT NULL,
  `desc` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=514 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_bdblockedlogs`
--

DROP TABLE IF EXISTS `t_bdblockedlogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_bdblockedlogs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logtime` int(10) NOT NULL,
  `srcip` varchar(15) NOT NULL,
  `host` varchar(255) NOT NULL,
  `bdtime` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=766599 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_cclogs`
--

DROP TABLE IF EXISTS `t_cclogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_cclogs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `AuditLogUniqueID` varchar(24) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `LogDateTime` datetime NOT NULL,
  `CountryCode` varchar(3) DEFAULT NULL,
  `RegionCode` varchar(8) DEFAULT NULL,
  `City` varchar(32) DEFAULT NULL,
  `SourceIP` varchar(15) NOT NULL,
  `SourcePort` varchar(8) DEFAULT NULL,
  `DestinationIP` varchar(15) NOT NULL,
  `DestinationPort` varchar(8) DEFAULT NULL,
  `Referer` varchar(255) DEFAULT NULL,
  `UserAgent` varchar(255) DEFAULT NULL,
  `HttpMethod` varchar(8) DEFAULT NULL,
  `Url` varchar(512) DEFAULT NULL,
  `HttpProtocol` varchar(16) DEFAULT NULL,
  `Host` varchar(255) DEFAULT NULL,
  `RequestContentType` varchar(255) DEFAULT NULL,
  `ResponseContentType` varchar(255) DEFAULT NULL,
  `HttpStatusCode` varchar(4) DEFAULT NULL,
  `GeneralMsg` varchar(512) DEFAULT NULL,
  `Rulefile` varchar(255) NOT NULL,
  `RuleID` varchar(6) DEFAULT NULL,
  `MatchData` varchar(255) DEFAULT NULL,
  `Rev` varchar(128) DEFAULT NULL,
  `Msg` varchar(128) DEFAULT NULL,
  `Severity` varchar(16) DEFAULT NULL,
  `Tag` varchar(64) DEFAULT NULL,
  `Status` varchar(8) DEFAULT NULL,
  `LogSource` varchar(8) NOT NULL DEFAULT '' COMMENT '日志来源 bridge:透明桥日志 proxy:反向代理日志',
  PRIMARY KEY (`id`),
  KEY `SourceIP` (`SourceIP`),
  KEY `LogDateTime` (`LogDateTime`),
  KEY `DestinationIP` (`DestinationIP`),
  KEY `HttpMethod` (`HttpMethod`),
  KEY `Host` (`Host`),
  KEY `Url` (`Url`(333)),
  KEY `DestinationPort` (`DestinationPort`),
  KEY `RuleID` (`RuleID`),
  KEY `Severity` (`Severity`),
  KEY `Status` (`Status`)
) ENGINE=MyISAM AUTO_INCREMENT=507 DEFAULT CHARSET=utf8 COMMENT='alert logs';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_countrycode`
--

DROP TABLE IF EXISTS `t_countrycode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_countrycode` (
  `CountryCode` varchar(3) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '国家代码',
  `EnCountry` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '英文名称',
  `CnCountry` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '中文名称',
  `Continent` varchar(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '大陆/洲',
  PRIMARY KEY (`CountryCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='国家代码/名称';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_countsety`
--

DROP TABLE IF EXISTS `t_countsety`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_countsety` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logdate` date NOT NULL,
  `emergency` int(10) unsigned DEFAULT '0',
  `alert` int(10) unsigned DEFAULT '0',
  `critical` int(10) unsigned DEFAULT '0',
  `error` int(10) unsigned DEFAULT '0',
  `warning` int(10) unsigned DEFAULT '0',
  `notice` int(10) unsigned DEFAULT '0',
  `info` int(10) unsigned DEFAULT '0',
  `debug` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `logdate` (`logdate`)
) ENGINE=MyISAM AUTO_INCREMENT=28 DEFAULT CHARSET=utf8 COMMENT='count severity';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_counturi`
--

DROP TABLE IF EXISTS `t_counturi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_counturi` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logdate` date NOT NULL,
  `Uri` varchar(512) DEFAULT NULL,
  `QueryString` varchar(512) DEFAULT NULL,
  `Host` varchar(255) DEFAULT NULL,
  `Hits` int(10) DEFAULT '1',
  `urlmd5` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `QueryString` (`QueryString`(333)),
  KEY `Uri` (`Uri`(333)),
  KEY `Host` (`Host`),
  KEY `logdate` (`logdate`),
  KEY `urlmd5` (`urlmd5`),
  KEY `Hits` (`Hits`)
) ENGINE=MyISAM AUTO_INCREMENT=240 DEFAULT CHARSET=utf8 COMMENT='count uri times';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_ddoslogs`
--

DROP TABLE IF EXISTS `t_ddoslogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ddoslogs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logtime` int(10) NOT NULL DEFAULT '0' COMMENT '攻击时间',
  `srcip` varchar(15) NOT NULL DEFAULT '' COMMENT '源IP地址',
  `CountryCode` varchar(3) DEFAULT NULL COMMENT '地理位置',
  `RegionCode` varchar(8) DEFAULT NULL COMMENT '地理位置',
  `City` varchar(32) DEFAULT NULL COMMENT '地理位置',
  `dstip` varchar(15) NOT NULL DEFAULT '' COMMENT '目标IP地址',
  `dstport` varchar(6) DEFAULT NULL COMMENT '目标端口',
  `protocol` varchar(8) DEFAULT NULL COMMENT '协议',
  `desc` varchar(64) DEFAULT NULL COMMENT '描述',
  PRIMARY KEY (`id`),
  KEY `logtime` (`logtime`),
  KEY `protocol` (`protocol`),
  KEY `dstport` (`dstport`),
  KEY `dstip` (`dstip`),
  KEY `srcip` (`srcip`)
) ENGINE=MyISAM AUTO_INCREMENT=3623 DEFAULT CHARSET=utf8 COMMENT='ddos logs';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_fileseat`
--

DROP TABLE IF EXISTS `t_fileseat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_fileseat` (
  `logid` int(10) unsigned NOT NULL DEFAULT '0',
  `StdDir` varchar(50) NOT NULL,
  `Sdate` varchar(10) NOT NULL,
  `Stime` varchar(16) NOT NULL,
  PRIMARY KEY (`logid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='last time reading position';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_queue`
--

DROP TABLE IF EXISTS `t_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_queue` (
  `filepath` varchar(100) NOT NULL,
  PRIMARY KEY (`filepath`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_ruleid`
--

DROP TABLE IF EXISTS `t_ruleid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ruleid` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logdate` date NOT NULL,
  `ruleid` int(10) unsigned NOT NULL,
  `Hits` int(10) unsigned DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `logdate` (`logdate`),
  KEY `ruleid` (`ruleid`),
  KEY `Hits` (`Hits`)
) ENGINE=MyISAM AUTO_INCREMENT=194 DEFAULT CHARSET=utf8 COMMENT='count rule id';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171025`
--

DROP TABLE IF EXISTS `t_sitestatus_20171025`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171025` (
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
) ENGINE=MyISAM AUTO_INCREMENT=2014 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171026`
--

DROP TABLE IF EXISTS `t_sitestatus_20171026`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171026` (
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
) ENGINE=MyISAM AUTO_INCREMENT=2014 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171027`
--

DROP TABLE IF EXISTS `t_sitestatus_20171027`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171027` (
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
) ENGINE=MyISAM AUTO_INCREMENT=707 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171030`
--

DROP TABLE IF EXISTS `t_sitestatus_20171030`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171030` (
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
) ENGINE=MyISAM AUTO_INCREMENT=323 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171031`
--

DROP TABLE IF EXISTS `t_sitestatus_20171031`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171031` (
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
) ENGINE=MyISAM AUTO_INCREMENT=736 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171101`
--

DROP TABLE IF EXISTS `t_sitestatus_20171101`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171101` (
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
) ENGINE=MyISAM AUTO_INCREMENT=1003 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171102`
--

DROP TABLE IF EXISTS `t_sitestatus_20171102`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171102` (
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
) ENGINE=MyISAM AUTO_INCREMENT=1896 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171103`
--

DROP TABLE IF EXISTS `t_sitestatus_20171103`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171103` (
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
) ENGINE=MyISAM AUTO_INCREMENT=2005 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171104`
--

DROP TABLE IF EXISTS `t_sitestatus_20171104`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171104` (
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
) ENGINE=MyISAM AUTO_INCREMENT=2011 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171105`
--

DROP TABLE IF EXISTS `t_sitestatus_20171105`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171105` (
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
) ENGINE=MyISAM AUTO_INCREMENT=1994 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171106`
--

DROP TABLE IF EXISTS `t_sitestatus_20171106`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171106` (
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
) ENGINE=MyISAM AUTO_INCREMENT=1908 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171107`
--

DROP TABLE IF EXISTS `t_sitestatus_20171107`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171107` (
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
) ENGINE=MyISAM AUTO_INCREMENT=2920 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171108`
--

DROP TABLE IF EXISTS `t_sitestatus_20171108`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171108` (
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
) ENGINE=MyISAM AUTO_INCREMENT=14521 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171109`
--

DROP TABLE IF EXISTS `t_sitestatus_20171109`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171109` (
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
) ENGINE=MyISAM AUTO_INCREMENT=89279 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171110`
--

DROP TABLE IF EXISTS `t_sitestatus_20171110`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171110` (
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
) ENGINE=MyISAM AUTO_INCREMENT=57449 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171111`
--

DROP TABLE IF EXISTS `t_sitestatus_20171111`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171111` (
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
) ENGINE=MyISAM AUTO_INCREMENT=83821 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171112`
--

DROP TABLE IF EXISTS `t_sitestatus_20171112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171112` (
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
) ENGINE=MyISAM AUTO_INCREMENT=83783 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171113`
--

DROP TABLE IF EXISTS `t_sitestatus_20171113`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171113` (
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
) ENGINE=MyISAM AUTO_INCREMENT=98853 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171114`
--

DROP TABLE IF EXISTS `t_sitestatus_20171114`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171114` (
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
) ENGINE=MyISAM AUTO_INCREMENT=129972 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171115`
--

DROP TABLE IF EXISTS `t_sitestatus_20171115`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171115` (
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
) ENGINE=MyISAM AUTO_INCREMENT=67042 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171116`
--

DROP TABLE IF EXISTS `t_sitestatus_20171116`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171116` (
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
) ENGINE=MyISAM AUTO_INCREMENT=49054 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171117`
--

DROP TABLE IF EXISTS `t_sitestatus_20171117`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171117` (
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
) ENGINE=MyISAM AUTO_INCREMENT=56618 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171118`
--

DROP TABLE IF EXISTS `t_sitestatus_20171118`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171118` (
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
) ENGINE=MyISAM AUTO_INCREMENT=71870 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171119`
--

DROP TABLE IF EXISTS `t_sitestatus_20171119`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171119` (
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
) ENGINE=MyISAM AUTO_INCREMENT=73247 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171120`
--

DROP TABLE IF EXISTS `t_sitestatus_20171120`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171120` (
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
) ENGINE=MyISAM AUTO_INCREMENT=66348 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171121`
--

DROP TABLE IF EXISTS `t_sitestatus_20171121`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171121` (
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
) ENGINE=MyISAM AUTO_INCREMENT=43154 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171122`
--

DROP TABLE IF EXISTS `t_sitestatus_20171122`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171122` (
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
) ENGINE=MyISAM AUTO_INCREMENT=61938 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sitestatus_20171123`
--

DROP TABLE IF EXISTS `t_sitestatus_20171123`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sitestatus_20171123` (
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
) ENGINE=MyISAM AUTO_INCREMENT=62289 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

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
  `desc` varchar(255) COLLATE utf8_unicode_ci DEFAULT '',
  `protype` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `freq` int(11) DEFAULT NULL,
  `responsetime` float DEFAULT NULL,
  `type` tinyint(4) DEFAULT '0',
  `rate` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sourceip`
--

DROP TABLE IF EXISTS `t_sourceip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sourceip` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logdate` date NOT NULL,
  `CountryCode` varchar(3) DEFAULT NULL,
  `RegionCode` varchar(8) DEFAULT NULL,
  `City` varchar(32) DEFAULT NULL,
  `SourceIP` varchar(15) NOT NULL,
  `Hits` int(10) unsigned DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `logdate` (`logdate`),
  KEY `SourceIP` (`SourceIP`),
  KEY `Hits` (`Hits`)
) ENGINE=MyISAM AUTO_INCREMENT=35 DEFAULT CHARSET=utf8 COMMENT='count sourceip';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_sourceip_bak`
--

DROP TABLE IF EXISTS `t_sourceip_bak`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sourceip_bak` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logdate` date NOT NULL,
  `CountryCode` varchar(3) DEFAULT NULL,
  `RegionCode` varchar(8) DEFAULT NULL,
  `City` varchar(32) DEFAULT NULL,
  `SourceIP` varchar(15) NOT NULL,
  `Hits` int(10) unsigned DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `logdate` (`logdate`),
  KEY `SourceIP` (`SourceIP`),
  KEY `Hits` (`Hits`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='count sourceip';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_syslogs`
--

DROP TABLE IF EXISTS `t_syslogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_syslogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` datetime NOT NULL,
  `program` varchar(32) DEFAULT NULL COMMENT 'event type',
  `Severity` varchar(16) DEFAULT NULL,
  `desc` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_syslogs_bak`
--

DROP TABLE IF EXISTS `t_syslogs_bak`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_syslogs_bak` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` datetime NOT NULL,
  `program` varchar(32) DEFAULT NULL COMMENT 'event type',
  `Severity` varchar(16) DEFAULT NULL,
  `desc` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_uploadedfilelogs`
--

DROP TABLE IF EXISTS `t_uploadedfilelogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_uploadedfilelogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reporttime` int(11) NOT NULL DEFAULT '0' COMMENT '报告时间',
  `url` varchar(64) NOT NULL DEFAULT '' COMMENT '站点URL',
  `filename` varchar(64) NOT NULL DEFAULT '' COMMENT '文件名',
  `uploadtime` int(11) NOT NULL DEFAULT '0' COMMENT '上传时间',
  `type` int(11) NOT NULL DEFAULT '0' COMMENT '是否是病毒 1 是 0不是',
  `rating` varchar(10) NOT NULL DEFAULT '' COMMENT '严重等级',
  `result` text COMMENT '检查结果',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2391 DEFAULT CHARSET=utf8 COMMENT='异常上传文件日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_web_connections_20160921`
--

DROP TABLE IF EXISTS `t_web_connections_20160921`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_20160921` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=16454 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_web_connections_20160927`
--

DROP TABLE IF EXISTS `t_web_connections_20160927`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_20160927` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10599 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_web_connections_20161011`
--

DROP TABLE IF EXISTS `t_web_connections_20161011`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_20161011` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=14449 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_web_connections_20161012`
--

DROP TABLE IF EXISTS `t_web_connections_20161012`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_20161012` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10459 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_web_connections_20161024`
--

DROP TABLE IF EXISTS `t_web_connections_20161024`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_20161024` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15504 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_web_connections_20161025`
--

DROP TABLE IF EXISTS `t_web_connections_20161025`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_20161025` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=24094 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_web_connections_20161026`
--

DROP TABLE IF EXISTS `t_web_connections_20161026`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_20161026` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15964 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_web_connections_20171122`
--

DROP TABLE IF EXISTS `t_web_connections_20171122`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_20171122` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=45398 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_web_connections_20171123`
--

DROP TABLE IF EXISTS `t_web_connections_20171123`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_web_connections_20171123` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `iNewConnections` int(11) DEFAULT NULL COMMENT '新建连接数',
  `iConConnections` int(11) DEFAULT NULL COMMENT '当前并发连接数',
  `iTransactions` int(11) DEFAULT NULL COMMENT '已处理事务数',
  `iTime` int(11) DEFAULT NULL COMMENT '当前时间',
  `siteflow` float DEFAULT NULL COMMENT '流量',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=33460 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_weboutlogs`
--

DROP TABLE IF EXISTS `t_weboutlogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_weboutlogs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dt` datetime DEFAULT NULL,
  `sip` varchar(15) DEFAULT '' COMMENT 'source ip',
  `dip` varchar(15) DEFAULT '' COMMENT 'dest ip',
  `CountryCode` varchar(3) DEFAULT NULL,
  `RegionCode` varchar(8) DEFAULT NULL,
  `City` varchar(32) DEFAULT NULL,
  `sport` varchar(5) DEFAULT '' COMMENT 'source port',
  `dport` varchar(5) DEFAULT '' COMMENT 'dest port',
  `action` tinyint(4) DEFAULT '0' COMMENT '0 1',
  `number` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `number` (`number`)
) ENGINE=InnoDB AUTO_INCREMENT=35209 DEFAULT CHARSET=utf8 COMMENT='非法外联';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_weboutlogs_bak`
--

DROP TABLE IF EXISTS `t_weboutlogs_bak`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_weboutlogs_bak` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dt` datetime DEFAULT NULL,
  `sip` varchar(15) DEFAULT '' COMMENT 'source ip',
  `dip` varchar(15) DEFAULT '' COMMENT 'dest ip',
  `CountryCode` varchar(3) DEFAULT NULL,
  `RegionCode` varchar(8) DEFAULT NULL,
  `City` varchar(32) DEFAULT NULL,
  `sport` varchar(5) DEFAULT '' COMMENT 'source port',
  `dport` varchar(5) DEFAULT '' COMMENT 'dest port',
  `action` tinyint(4) DEFAULT '0' COMMENT '0 1',
  `number` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `number` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unkbrowser`
--

DROP TABLE IF EXISTS `unkbrowser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unkbrowser` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `agent` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `lastvisit` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unkos`
--

DROP TABLE IF EXISTS `unkos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unkos` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `agent` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `lastvisit` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201101`
--

DROP TABLE IF EXISTS `visitors_201101`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201101` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201104`
--

DROP TABLE IF EXISTS `visitors_201104`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201104` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201502`
--

DROP TABLE IF EXISTS `visitors_201502`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201502` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201503`
--

DROP TABLE IF EXISTS `visitors_201503`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201503` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201504`
--

DROP TABLE IF EXISTS `visitors_201504`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201504` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201506`
--

DROP TABLE IF EXISTS `visitors_201506`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201506` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201507`
--

DROP TABLE IF EXISTS `visitors_201507`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201507` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201508`
--

DROP TABLE IF EXISTS `visitors_201508`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201508` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201509`
--

DROP TABLE IF EXISTS `visitors_201509`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201509` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201511`
--

DROP TABLE IF EXISTS `visitors_201511`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201511` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201512`
--

DROP TABLE IF EXISTS `visitors_201512`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201512` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201601`
--

DROP TABLE IF EXISTS `visitors_201601`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201601` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=98 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201604`
--

DROP TABLE IF EXISTS `visitors_201604`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201604` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201605`
--

DROP TABLE IF EXISTS `visitors_201605`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201605` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201606`
--

DROP TABLE IF EXISTS `visitors_201606`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201606` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201607`
--

DROP TABLE IF EXISTS `visitors_201607`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201607` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201608`
--

DROP TABLE IF EXISTS `visitors_201608`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201608` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201609`
--

DROP TABLE IF EXISTS `visitors_201609`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201609` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201610`
--

DROP TABLE IF EXISTS `visitors_201610`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201610` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201611`
--

DROP TABLE IF EXISTS `visitors_201611`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201611` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201612`
--

DROP TABLE IF EXISTS `visitors_201612`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201612` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201701`
--

DROP TABLE IF EXISTS `visitors_201701`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201701` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201702`
--

DROP TABLE IF EXISTS `visitors_201702`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201702` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=69 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201703`
--

DROP TABLE IF EXISTS `visitors_201703`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201703` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201704`
--

DROP TABLE IF EXISTS `visitors_201704`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201704` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=431 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201705`
--

DROP TABLE IF EXISTS `visitors_201705`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201705` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=271 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201706`
--

DROP TABLE IF EXISTS `visitors_201706`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201706` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201707`
--

DROP TABLE IF EXISTS `visitors_201707`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201707` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=27 DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201708`
--

DROP TABLE IF EXISTS `visitors_201708`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201708` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201710`
--

DROP TABLE IF EXISTS `visitors_201710`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201710` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `visitors_201711`
--

DROP TABLE IF EXISTS `visitors_201711`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visitors_201711` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `webagent`
--

DROP TABLE IF EXISTS `webagent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `webagent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `miss` int(10) unsigned NOT NULL,
  `hit` int(10) unsigned NOT NULL,
  `bandwidth_miss` bigint(20) unsigned NOT NULL,
  `bandwidth_hit` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=830 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `webvisit`
--

DROP TABLE IF EXISTS `webvisit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `webvisit` (
  `visits` int(10) unsigned NOT NULL,
  `visits_unique` int(10) unsigned NOT NULL,
  `pages` int(10) unsigned NOT NULL,
  `attack` int(10) unsigned NOT NULL,
  `hit_times` int(10) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `worms`
--

DROP TABLE IF EXISTS `worms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `worms` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `text` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-11-23 15:58:42
