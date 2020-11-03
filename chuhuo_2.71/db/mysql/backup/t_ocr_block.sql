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
-- Table structure for table `t_ocr_block`
--

DROP TABLE IF EXISTS `t_ocr_block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_ocr_block` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1-on,0-off',
  `urls` varchar(2048) DEFAULT '' COMMENT '就是需要拦截的 url 每个url用 | 分开',
  `exts` varchar(500) DEFAULT 'gif|jpg|png|bmp' COMMENT '扩展名exts 默认 '''', |分隔',
  `words` text NOT NULL COMMENT '需要拦截的词 split by |',
  `website_id` int(11) NOT NULL DEFAULT '0' COMMENT 'waf2.6.1 t_websit 默认 0',
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
INSERT INTO `t_ocr_block` VALUES (1,1,'','gif|jpg|png|bmp|bmm','法轮功|李洪志|大纪元|真善忍|新唐人|毛一鲜|黎阳平|张小平|戴海静|赵紫阳|胡耀邦|六四事件|退党|天葬|禁书|枪决现场|疆独|藏独|反共|中共|达赖|班禅|东突|台独|台海|肉棍|淫靡|淫水|迷药|迷昏药|色情服务|成人片|三级片|激情小电影|黄色小电影|色情小电影|援交|打炮|口活|吹萧|打飞机|冰火|毒龙|全身漫游|休闲按摩|丝袜美女|推油|毛片|淫荡|骚妇|熟女|成人电影|换妻|丝袜美足|走光|摇头丸|海洛因|白面|迷幻醉|春药|催情|三唑仑|麻醉乙醚|遗忘药|佳境安定片|蒙汗药粉|麻醉药|买卖枪支|出售枪支|投毒杀人|手机复制|麻醉钢枪|枪支弹药|鬼村|雷管|古方迷香|强效忆药|迷奸药|代考|考研枪手|套牌|刻章|办证|证件集团|办理证件|窃听器|汽车解码器|汽车拦截器|开锁枪|侦探设备|远程偷拍|电表反转调效器|特码|翻牌|办理文凭|代开发票|监听王|透视眼镜|全选|全不选|名字|个人护理|登录|can|红军',12,'2018-01-25 14:26:50');
/*!40000 ALTER TABLE `t_ocr_block` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-23 16:51:35
