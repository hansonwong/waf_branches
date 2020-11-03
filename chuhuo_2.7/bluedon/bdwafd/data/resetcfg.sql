
set names utf8;

-- -------------------------------- 安全管理 ----------------------------------
-- 只能阻断设置
UPDATE waf.t_securityset SET is_autodefence=0,autodefence_cycle=300,autodefence_count=10,autodefence_second=3600 WHERE id=1;

-- 自学习设置
DELETE FROM waf.t_selfstudy_setting;
INSERT INTO waf.t_selfstudy_setting SET is_use=0,is_ip_white=0,is_use_result=0,id=0;

-- 自学习访问白名单
TRUNCATE TABLE waf.t_selfstudy_ip_white;

-- 自学习结果
UPDATE waf.t_selfstudy_result SET uri_max=0,arg_name_max=0,arg_content_max=0,arg_count_max=0,cookie_max=0,cookie_name_max=0,cookie_content_max=0,cookie_count_max=0  WHERE id=1;

-- 非法外联检测
TRUNCATE TABLE waf.t_webserver_outbound;

-- 非法外联设置
UPDATE waf.t_webserver_outbound_port SET is_use=1,dports='80|443'  WHERE id=1;

-- 可用性监测
TRUNCATE TABLE waf.t_sitestatus;

-- 漏洞扫描
TRUNCATE TABLE waf.t_scantask;

-- 网页防篡改
TRUNCATE TABLE waf.t_webguard;
INSERT INTO waf.`t_webguard` VALUES ('1', 'http://', null, null);


-- HTTP防溢出设置
TRUNCATE TABLE waf.t_overflowset;
INSERT INTO waf.`t_overflowset` VALUES ('300200', 'Accept', '2048', '1', 'REQUEST_HEADERS:Accept');
INSERT INTO waf.`t_overflowset` VALUES ('300201', 'Accept-Charset', '2048', '1', 'REQUEST_HEADERS:Accept-Charset');
INSERT INTO waf.`t_overflowset` VALUES ('300202', 'Accept-Encoding', '2048', '1', 'REQUEST_HEADERS:Accept-Encoding');
INSERT INTO waf.`t_overflowset` VALUES ('300203', 'Cookie', '32767', '1', 'REQUEST_HEADERS:Cookie');
INSERT INTO waf.`t_overflowset` VALUES ('300204', 'Post', '2048', '1', 'REQUEST_BODY');
INSERT INTO waf.`t_overflowset` VALUES ('300205', 'URI', '2048', '1', 'REQUEST_URI');
INSERT INTO waf.`t_overflowset` VALUES ('300206', 'Host', '2048', '1', 'REQUEST_HEADERS:Host');
INSERT INTO waf.`t_overflowset` VALUES ('300207', 'Referer', '2048', '1', 'REQUEST_HEADERS:Referer');
INSERT INTO waf.`t_overflowset` VALUES ('300208', 'Authorization', '2048', '1', 'REQUEST_HEADERS:Authorization');
INSERT INTO waf.`t_overflowset` VALUES ('300209', 'Poxy-Authorization', '2048', '1', 'REQUEST_HEADERS:Poxy-Authorization');
INSERT INTO waf.`t_overflowset` VALUES ('300210', 'User-Agent', '2048', '1', 'REQUEST_HEADERS:User-Agent');

-- HTTP请求动作设置
TRUNCATE TABLE waf.t_httptypeset;
INSERT INTO waf.`t_httptypeset` VALUES ('1', 'GET', null, '1');
INSERT INTO waf.`t_httptypeset` VALUES ('2', 'POST', null, '1');
INSERT INTO waf.`t_httptypeset` VALUES ('3', 'HEAD', null, '1');
INSERT INTO waf.`t_httptypeset` VALUES ('4', 'OPTIONS', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('5', 'DELETE', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('6', 'SEARCH', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('7', 'PROPFIND', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('8', 'CHECKOUT', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('9', 'CHECHIN', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('10', 'MKCOL', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('11', 'PROPPATCH', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('12', 'SHOWMETHOD', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('13', 'TEXTSEARCH', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('15', 'COPY', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('16', 'LOCK', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('17', 'LINK', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('18', 'SPACEJUMP', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('19', 'PUT', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('20', 'CONNECT', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('21', 'MOVE', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('22', 'UNLOCK', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('23', 'UNLINK', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('24', 'TRACK', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('25', 'DEBUG', null, '0');
INSERT INTO waf.`t_httptypeset` VALUES ('26', 'UNKNOWN', null, '0');

-- 允许HTTP请求内容
TRUNCATE TABLE waf.t_httprequesttype;
INSERT INTO waf.`t_httprequesttype` VALUES ('1', 'application/x-www-form-urlencoded', '0');
INSERT INTO waf.`t_httprequesttype` VALUES ('2', 'multipart/form-data', '0');
INSERT INTO waf.`t_httprequesttype` VALUES ('3', 'text/xml', '0');
INSERT INTO waf.`t_httprequesttype` VALUES ('4', 'application/xml', '0');
INSERT INTO waf.`t_httprequesttype` VALUES ('5', 'application/x-amf', '0');
INSERT INTO waf.`t_httprequesttype` VALUES ('6', 'application/json', '0');

-- HTTP协议版本过滤
TRUNCATE TABLE waf.t_httpver;
INSERT INTO waf.`t_httpver` VALUES ('1', 'HTTP/1.0', '1');
INSERT INTO waf.`t_httpver` VALUES ('2', 'HTTP/1.1', '1');

-- HTTP头字段设置
TRUNCATE TABLE waf.t_restrictheaders;
INSERT INTO waf.`t_restrictheaders` VALUES ('1', 'Proxy-Connection', '0');
INSERT INTO waf.`t_restrictheaders` VALUES ('2', 'Lock-Token', '0');
INSERT INTO waf.`t_restrictheaders` VALUES ('3', 'Content-Range', '0');
INSERT INTO waf.`t_restrictheaders` VALUES ('4', 'Translate', '0');
INSERT INTO waf.`t_restrictheaders` VALUES ('5', 'via', '0');
INSERT INTO waf.`t_restrictheaders` VALUES ('6', 'if', '0');

-- 文件扩展名过滤
TRUNCATE TABLE waf.t_restrictext;
INSERT INTO waf.`t_restrictext` VALUES ('1', '.asa', '0');
INSERT INTO waf.`t_restrictext` VALUES ('2', '.asax', '0');
INSERT INTO waf.`t_restrictext` VALUES ('3', '.ascx', '0');
INSERT INTO waf.`t_restrictext` VALUES ('4', '.axd', '0');
INSERT INTO waf.`t_restrictext` VALUES ('5', '.backup', '0');
INSERT INTO waf.`t_restrictext` VALUES ('6', '.bak', '0');
INSERT INTO waf.`t_restrictext` VALUES ('7', '.bat', '0');
INSERT INTO waf.`t_restrictext` VALUES ('8', '.cdx', '0');
INSERT INTO waf.`t_restrictext` VALUES ('9', '.cer', '0');
INSERT INTO waf.`t_restrictext` VALUES ('10', '.cfg', '0');
INSERT INTO waf.`t_restrictext` VALUES ('11', '.cmd', '0');
INSERT INTO waf.`t_restrictext` VALUES ('12', '.com', '0');
INSERT INTO waf.`t_restrictext` VALUES ('13', '.config', '0');
INSERT INTO waf.`t_restrictext` VALUES ('14', '.conf', '0');
INSERT INTO waf.`t_restrictext` VALUES ('15', '.cs', '0');
INSERT INTO waf.`t_restrictext` VALUES ('16', '.csproj', '0');
INSERT INTO waf.`t_restrictext` VALUES ('17', '.csr', '0');
INSERT INTO waf.`t_restrictext` VALUES ('18', '.dat', '0');
INSERT INTO waf.`t_restrictext` VALUES ('19', '.db', '0');
INSERT INTO waf.`t_restrictext` VALUES ('20', '.dbf', '0');
INSERT INTO waf.`t_restrictext` VALUES ('21', '.dll', '0');
INSERT INTO waf.`t_restrictext` VALUES ('22', '.dos', '0');
INSERT INTO waf.`t_restrictext` VALUES ('23', '.htr', '0');
INSERT INTO waf.`t_restrictext` VALUES ('24', '.htw', '0');
INSERT INTO waf.`t_restrictext` VALUES ('25', '.ids', '0');
INSERT INTO waf.`t_restrictext` VALUES ('26', '.idc', '0');
INSERT INTO waf.`t_restrictext` VALUES ('27', '.idq', '0');
INSERT INTO waf.`t_restrictext` VALUES ('28', '.inc', '0');
INSERT INTO waf.`t_restrictext` VALUES ('29', '.ini', '0');
INSERT INTO waf.`t_restrictext` VALUES ('30', '.key', '0');
INSERT INTO waf.`t_restrictext` VALUES ('31', '.licx', '0');
INSERT INTO waf.`t_restrictext` VALUES ('32', '.lnk', '0');
INSERT INTO waf.`t_restrictext` VALUES ('33', '.log', '0');
INSERT INTO waf.`t_restrictext` VALUES ('34', '.mdb', '0');
INSERT INTO waf.`t_restrictext` VALUES ('35', '.old', '0');
INSERT INTO waf.`t_restrictext` VALUES ('36', '.pass', '0');
INSERT INTO waf.`t_restrictext` VALUES ('37', '.pdb', '0');
INSERT INTO waf.`t_restrictext` VALUES ('38', '.pol', '0');
INSERT INTO waf.`t_restrictext` VALUES ('39', '.printer', '0');
INSERT INTO waf.`t_restrictext` VALUES ('40', '.pwd', '0');
INSERT INTO waf.`t_restrictext` VALUES ('41', '.resources', '0');
INSERT INTO waf.`t_restrictext` VALUES ('42', '.resx', '0');
INSERT INTO waf.`t_restrictext` VALUES ('43', '.sql', '0');
INSERT INTO waf.`t_restrictext` VALUES ('44', '.sys', '0');
INSERT INTO waf.`t_restrictext` VALUES ('45', '.vb', '0');
INSERT INTO waf.`t_restrictext` VALUES ('46', '.vbs', '0');
INSERT INTO waf.`t_restrictext` VALUES ('47', '.vbproj', '0');
INSERT INTO waf.`t_restrictext` VALUES ('48', '.vsdisco', '0');
INSERT INTO waf.`t_restrictext` VALUES ('49', '.webinfo', '0');
INSERT INTO waf.`t_restrictext` VALUES ('50', '.xsd', '0');
INSERT INTO waf.`t_restrictext` VALUES ('51', '.xsx', '0');



-- 服务器信息隐藏
TRUNCATE TABLE waf.t_securityset;
INSERT INTO waf.`t_securityset` VALUES ('1', '0', '', '', 'Googlebot|Adsbot|baiduspider|Yahoo!|iaskspider|YodaoBot|msnbot|bingbot|Sosospider|Sosoblogspider|Sosoimagespider|360Spider|JikeSpider|ia_archiver|lanshanbot|Adminrtspider|HuaweiSymantecSpider|MJ12bot|YandexBot|Yeti|DoCoMo|HTTrack|Heritrix|Datapark|JSpider|python|curl|wget|lftp|BlackWidow|ChinaClaw|Custo|DISCo|eCatch|EirGrabber|EmailSiphon|EmailWolf|ExtractorPro|EyeNetIE|FlashGet|GetRight|GetWeb!|Go!Zilla|Go-Ahead-Got-It|GrabNet|Grafula|HMView|InterGET|JetCar|larbin|LeechFTP|Navroad|NearSite|NetAnts|NetSpider|NetZIP|Octopus|PageGrabber|pavuk|pcBrowser|RealDownload|ReGet|SiteSnagger|SmartDownload|SuperBot|SuperHTTP|Surfbot|tAkeOut|VoidEYE|WebAuto|WebCopier|WebFetch|WebLeacher|WebReaper|WebSauger|WebStripper|WebWhacker|WebZIP|Widow|WWWOFFLE|Zeus|lycos_spider_|Gaisbot|Search17Bot|crawler|MLBot|scooter|Gigabot|DotBot', '', '0', '法轮功|李洪志|大纪元|真善忍|新唐人|毛一鲜|黎阳平|张小平|戴海静|赵紫阳|胡耀邦|六四事件|退党|天葬|禁书|枪决现场|疆独|藏独|反共|中共|达赖|班禅|东突|台独|台海|肉棍|淫靡|淫水|迷药|迷昏药|色情服务|成人片|三级片|激情小电影|黄色小电影|色情小电影|援交|打炮|口活|吹萧|打飞机|冰火|毒龙|全身漫游|休闲按摩|丝袜美女|推油|毛片|淫荡|骚妇|熟女|成人电影|换妻|丝袜美足|走光|摇头丸|海洛因|白面|迷幻醉|春药|催情|三唑仑|麻醉乙醚|遗忘药|佳境安定片|蒙汗药粉|麻醉药|买卖枪支|出售枪支|投毒杀人|手机复制|麻醉钢枪|枪支弹药|鬼村|雷管|古方迷香|强效忆药|迷奸药|代考|考研枪手|套牌|刻章|办证|证件集团|办理证件|窃听器|汽车解码器|汽车拦截器|开锁枪|侦探设备|远程偷拍|电表反转调效器|特码|翻牌|办理文凭|代开发票|监听王|透视眼镜', '0', '0', '300', '10', '3600', '0', '1', '70');

-- 部署方式设置
TRUNCATE TABLE waf.t_baseconfig;
INSERT INTO waf.`t_baseconfig`(`wafengine`,`defaultaction`,`ports`,`deploy`) VALUES ('DetectionOnly', 'deny', '80|8080|443', 'reverseproxy');

-- 规则模板设置
TRUNCATE TABLE waf.t_ruleset;
INSERT INTO waf.`t_ruleset` VALUES ('1', '基本防护(内置)', '1,4,7,6,8', '1', '1');
INSERT INTO waf.`t_ruleset` VALUES ('2', '中级防护(内置)', '1,2,3,4,5,6,7,8,9,10,11,12,14,15', '0', '1');
INSERT INTO waf.`t_ruleset` VALUES ('3', '高级防护(内置)', '1,2,3,4,5,6,7,8,9,10,11,12,14,15,18,24', '0', '1');


-- DDOS防护设置
TRUNCATE TABLE waf.t_ddosset;
INSERT INTO waf.`t_ddosset` VALUES ('116', '1024', '10000', '10000', '10000', '10000', '10000', '10000', '10000', '10000', '10000', '10000', '10000', '10000', '10000', '10000', '0', '0', '0');

-- CC防护设置
TRUNCATE TABLE waf.t_ccset;
INSERT INTO waf.`t_ccset` VALUES ('6', '0', '10', '5', '60', '0', '0', '0', '', '0');

-- -------------------------------- 日志报表 ----------------------------------
-- 定期报表
DELETE FROM waf.t_cyclereport;
INSERT INTO waf.t_cyclereport SET `type`=2,`desc`='',`cycle`=1,`sendmail`=0,`format`='pdf';
INSERT INTO waf.t_cyclereport SET `type`=1,`desc`='',`cycle`=1,`sendmail`=0,`format`='pdf';

-- 报表管理
TRUNCATE TABLE waf.t_reportsmanage;

-- -------------------------------- 系统管理 ----------------------------------
-- 网络接口
TRUNCATE TABLE waf.t_nicset;
INSERT INTO waf.`t_nicset`(lan_port,lan_type,nic,ip,mask,gateway,isstart,islink,workmode,`desc`,brgname) VALUES ('eth0','default_admin','eth0', '192.168.0.1', '255.255.255.0', '', '1', '1', 'full', '', '');



-- 虚拟网桥
TRUNCATE TABLE waf.t_bridge;

-- 反向代理设置
TRUNCATE TABLE waf.t_reverporxy;

-- Bypass设置
UPDATE waf.t_securityset SET `is_bypass`=0 WHERE id=1;

-- SNMP Trap
UPDATE waf.t_snmp_up SET is_use=0, version='', ip='', port='', community='', ip2='', port2='', community2='', ip3='', port3='', community3='' WHERE id=1;

-- SYSLOG配置
UPDATE waf.t_syslog_up SET is_use=0, ip='', port='', method='', ip2='', port2='', method2='', ip3='', port3='', method3='' WHERE id=1;

-- HA参数设置
UPDATE waf.t_ha_setting SET `is_use`=0, `interface`='', `ip`='', `state`='backup',`vhid`=10,`password`='' WHERE id=1;
-- VLAN设置
TRUNCATE TABLE waf.t_vlan;
-- 通知设置
TRUNCATE TABLE waf.t_mailset;
-- 报警设置
UPDATE waf.t_mailalert SET `status`=0,`phone_status`=0,`now`=0,`interval`=24,`maxValue`=0,`cycle`=24;

-- 登录配置
TRUNCATE TABLE waf.t_userconfig;
INSERT INTO waf.`t_userconfig` VALUES ('5', '15');

-- 接入控制
TRUNCATE TABLE waf.t_blackandwhite;
