USE waf;

DROP TABLE IF EXISTS `t_ocr_block` ;


CREATE TABLE IF NOT EXISTS `t_ocr_block` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` TINYINT(1) NOT NULL DEFAULT '1' COMMENT '1-on,0-off',
  `urls` varchar(2048) DEFAULT '' COMMENT 'split by | ',
  `exts` varchar(500) DEFAULT 'gif|jpg|png|bmp' COMMENT 'split by | , 扩展名',
  `words` longtext NOT NULL COMMENT 'split by |',
  `website_id` int(11) NOT NULL DEFAULT '0' COMMENT 'waf2.6.1 t_websit',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `website_id` (`website_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

INSERT INTO `t_ocr_block`(`status`, `urls`, `website_id`, `words`) value(1, "/dashboard|/index.php|/dvwa/vulnerabilities|/test", 12, '法轮功|李洪志|大纪元|真善忍|新唐人|毛一鲜|黎阳平|张小平|戴海静|赵紫阳|胡耀邦|六四事件|退党|天葬|禁书|枪决现场|疆独|藏独|反共|中共|达赖|班禅|东突|台独|台海|肉棍|淫靡|淫水|迷药|迷昏药|色情服务|成人片|三级片|激情小电影|黄色小电影|色情小电影|援交|打炮|口活|吹萧|打飞机|冰火|毒龙|全身漫游|休闲按摩|丝袜美女|推油|毛片|淫荡|骚妇|熟女|成人电影|换妻|丝袜美足|走光|摇头丸|海洛因|白面|迷幻醉|春药|催情|三唑仑|麻醉乙醚|遗忘药|佳境安定片|蒙汗药粉|麻醉药|买卖枪支|出售枪支|投毒杀人|手机复制|麻醉钢枪|枪支弹药|鬼村|雷管|古方迷香|强效忆药|迷奸药|代考|考研枪手|套牌|刻章|办证|证件集团|办理证件|窃听器|汽车解码器|汽车拦截器|开锁枪|侦探设备|远程偷拍|电表反转调效器|特码|翻牌|办理文凭|代开发票|监听王|透视眼镜|全选|全不选|名字|个人护理|登录|can')

