
DROP DATABASE IF EXISTS `waf_hw`;
CREATE DATABASE waf_hw;


USE waf_hw;
SET FOREIGN_KEY_CHECKS=0;

DELIMITER //

drop procedure if exists createIpMostWeakTable//

create procedure createIpMostWeakTable(IN `task_id` int)
begin
	declare hostmsg_table varchar(20);
	declare vul_details_table varchar(20);
	declare scan_result_table varchar(20);
	declare weak_pwd_details_table varchar(30);
	declare union_sql_str varchar(65530);
	set hostmsg_table = concat("hostmsg_",task_id);
	set vul_details_table = concat("vul_details_",task_id);
	set scan_result_table = concat("scan_result_",task_id);
	set weak_pwd_details_table = concat("weak_pwd_details_",task_id);
        set union_sql_str = "drop table if exists tmp_iplist";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = concat("create temporary table tmp_iplist select  ip,risk_factor as level from ",vul_details_table," union all select ip,level from ",scan_result_table," union all select ip,'HIGH' as level from ",weak_pwd_details_table);
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "drop table if exists tmp_ipmostweak";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = concat("create temporary table tmp_ipmostweak select ip,count(*) as c from tmp_iplist where level='C' or level='H' or level='HIGH' group by ip");
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	
	#select count(*) as c from tmp_ipmostweak;
	#select count(*) as c,ip from tmp_iplist group by ip;
end;
//

drop procedure if exists createIpRiskTable//

create procedure createIpRiskTable(IN  `task_id` int,IN `ip_id` text)
begin
	declare done int default 0;
	declare hostmsg_table varchar(30);
	declare task_summary_table varchar(30);
	declare vul_details_table varchar(30);
	declare scan_result_table varchar(30);
	declare weak_pwd_details_table varchar(30);
	declare union_sql_str varchar(65530);
	declare c_str varchar(10);
	declare level_str varchar(10);
	declare ip_str varchar(32);
	declare curl cursor for select tv.c as c,tv.level as level,tv.ip as ip from tmp_vullist tv,tmp_iplist ti where tv.ip=ti.ip;
	declare continue handler for sqlstate '02000' set done = 1;
	set hostmsg_table = concat("hostmsg_",task_id);
	set vul_details_table = concat("vul_details_",task_id);
	set scan_result_table = concat("scan_result_",task_id);
	set weak_pwd_details_table = concat("weak_pwd_details_",task_id);
        set task_summary_table = concat("task_summary_",task_id);
	set union_sql_str = "drop table if exists tmp_iplist";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "drop table if exists tmp_vullist";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "create temporary table tmp_iplist(ip varchar(45) default NULL,os varchar(500) default NULL,high int(11) default 0,med int(11) default 0,low int(11) default 0,none int(11) default 0,PRIMARY KEY  (`ip`))ENGINE=InnoDB default charset=utf8";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	if ip_id = '' then
		set union_sql_str = concat("insert into tmp_iplist(ip,os) select t.ip,h.running_os from ",task_summary_table," t,",hostmsg_table," h where t.ip=h.ip and t.total_weak>0");
	else
		set union_sql_str = concat("insert into tmp_iplist(ip,os) select t.ip,h.running_os from ",task_summary_table," t,",hostmsg_table," h where t.ip=h.ip and t.total_weak>0 and t.id in (",ip_id,")");
	end if;
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "create temporary table tmp_vullist(`c` int(11) default 0,`level` varchar(32) default NULL,`ip` varchar(45) default NULL)ENGINE=InnoDB default charset=utf8";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = concat("insert into tmp_vullist(`c`,`level`,`ip`) select count(*) as c,risk_factor as level,ip from ",vul_details_table," group by concat(risk_factor,ip) union all select count(*) as c,level,ip from ",scan_result_table," group by concat(level,ip) union all select count(*) as c ,'HIGH' as level,ip from ",weak_pwd_details_table," group by ip");
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	open curl;
	repeat
		fetch curl into c_str,level_str,ip_str;
		if  level_str = 'C' or  level_str = 'H' or  level_str = 'M' or  level_str = 'L' or  level_str = 'I' or  level_str = 'HIGH' or  level_str = 'MED' or  level_str = 'LOW' then
			if level_str = 'C' or level_str = 'H' or level_str = 'HIGH' then
				set union_sql_str = concat("update tmp_iplist set high = high + ",c_str," where ip=?");
			elseif level_str = 'M' or level_str = 'MED' then
				set union_sql_str = concat("update tmp_iplist set med = med + ",c_str," where ip=?");
			elseif level_str = 'L' or level_str = 'LOW' then
				set union_sql_str = concat("update tmp_iplist set low = low + ",c_str," where ip=?");
			else
				set union_sql_str = concat("update tmp_iplist set none = none + ",c_str," where ip=?");
			end if;
			if not done then
				set @E = union_sql_str;
				set @aaa = ip_str;
				prepare sql_str from @E;
				execute sql_str using @aaa;
				deallocate prepare sql_str;
			end if;
		end if;
	until done
	end repeat;
	close curl;
	
	#select * from tmp_iplist;
end;
//

drop procedure if exists createNetRiskDisTable//

create procedure createNetRiskDisTable(IN task_id int)
begin
	declare hostmsg_table varchar(20);
	declare vul_details_table varchar(20);
	declare scan_result_table varchar(20);
	declare weak_pwd_details_table varchar(30);
	declare union_sql_str varchar(65530);
	set hostmsg_table = concat("hostmsg_",task_id);
	set vul_details_table = concat("vul_details_",task_id);
	set scan_result_table = concat("scan_result_",task_id);
	set weak_pwd_details_table = concat("weak_pwd_details_",task_id);
        set union_sql_str = "drop table if exists tmp_iplist";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = concat("create temporary table tmp_iplist select  ip,risk_factor as level from ",vul_details_table," union all select ip,level from ",scan_result_table," union all select ip,'HIGH' as level from ",weak_pwd_details_table);
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "drop table if exists netriskdis";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "create temporary table netriskdis select ip,level from tmp_iplist order by FIELD(level,'C','H','HIGH','M','MED','L','LOW','I')";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "drop table if exists netriskdis2";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "create temporary table netriskdis2 select * from netriskdis group by ip";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str; 
	set union_sql_str = "update netriskdis2 set level='HIGH' where level='C' or level='H'";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "update netriskdis2 set level='MED' where level='M'";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "update netriskdis2 set level='LOW' where level='L'";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "update netriskdis2 set level='NONE' where level='I'";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;

	#select level,count(*) as c from netriskdis2 group by level;
end;
//

drop procedure if exists createVultypeTable//

create procedure createVultypeTable(IN task_id int,IN ip_id text)
begin
	declare hostmsg_table varchar(20);
	declare vul_details_table varchar(20);
	declare scan_result_table varchar(20);
	declare weak_pwd_details_table varchar(30);
	declare union_sql_str varchar(65530);
	set hostmsg_table = concat("hostmsg_",task_id);
	set vul_details_table = concat("vul_details_",task_id);
	set scan_result_table = concat("scan_result_",task_id);
	set weak_pwd_details_table = concat("weak_pwd_details_",task_id);
    set union_sql_str = "drop table if exists tmp_vulall";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	if ip_id = '' then
		set union_sql_str = concat("create temporary table tmp_vulall select  family as vulname,risk_factor as level,count(*) as c from ",vul_details_table," group by concat(vulname,level) union all select vul_type as vulname,level,count(*) as c from ",scan_result_table," group by concat(vulname,level) union all select type as vulname,'HIGH' as level,count(*) as c from ",weak_pwd_details_table," group by concat(vulname,level)");
	else
		set union_sql_str = concat("create temporary table tmp_vulall select  family as vulname,risk_factor as level,count(*) as c from ",vul_details_table," v,",hostmsg_table," t where v.ip=t.ip and t.id in (",ip_id,") group by concat(vulname,level) union all select vul_type as vulname,level,count(*) as c from ",scan_result_table," s,",hostmsg_table," t where s.ip=t.ip and t.id in (",ip_id,") group by concat(vulname,level) union all select type as vulname,'HIGH' as level,count(*) as c from ",weak_pwd_details_table," w,",hostmsg_table," t where w.ip=t.ip and t.id in (",ip_id,") group by concat(vulname,level)");
	end if;
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "drop table if exists tmp_vulall2";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	set union_sql_str = concat("create temporary table tmp_vulall2 select * from tmp_vulall");
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	set union_sql_str = "drop table if exists tmp_vulall3";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	set union_sql_str = concat("create temporary table tmp_vulall3 select * from tmp_vulall");
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	set union_sql_str = "drop table if exists tmp_vulall4";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	set union_sql_str = concat("create temporary table tmp_vulall4 select * from tmp_vulall");
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	set union_sql_str = "drop table if exists tmp_vultype";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	set union_sql_str = "create temporary table tmp_vultype select vulname,sum(c) as total,(select sum(c) from tmp_vulall2 where vulname=t.vulname and (level='C' or level='H' or level='HIGH')) as high,(select sum(c) from tmp_vulall3 where vulname=t.vulname and (level='M' or level='MED')) as med,(select sum(c) from tmp_vulall4 where vulname=t.vulname and (level='L' or level='LOW' or level='I')) as low from tmp_vulall t group by vulname ";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	
	#select * from tmp_vultype order by high desc,med desc,low desc;
end;
//

drop procedure if exists createVulDisTable//

create procedure createVulDisTable(IN task_id int,IN ip_id text)
begin
	declare host_vul_table varchar(30);
	declare web_vul_table varchar(30);
	declare vul_details_table varchar(30);
	declare scan_result_table varchar(30);
	declare task_summary_table varchar(30);
	declare union_sql_str varchar(65530);
	set host_vul_table = concat("host_vul_",task_id);
	set web_vul_table = concat("web_vul_",task_id);
	set vul_details_table = concat("vul_details_",task_id);
	set scan_result_table = concat("scan_result_",task_id);
	set task_summary_table = concat("task_summary_",task_id);
	set union_sql_str = "drop table if exists tmp_vuldis";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	if ip_id = '' then
		set union_sql_str = concat("create temporary table tmp_vuldis select vul_name as vulname,proto,port,risk_factor as level,ip_list as list from ",host_vul_table," union all select vul_name as vulname,'' as proto,'' as port,risk_factor as level,domain_list as list from ",web_vul_table);
	else
		set union_sql_str = concat("create temporary table tmp_vuldis select count(*) as c, v.vul_name as vulname,v.proto as proto,v.port as port,v.risk_factor as level from ",vul_details_table," v,",task_summary_table," t where v.ip=t.ip and t.id in (",ip_id,") group by concat(v.vul_name,v.proto,v.port) union all select count(*) as c, s.vul_type as vulname,'' as proto,'' as port,s.level as level from ",scan_result_table," s,",task_summary_table," t where s.ip=t.ip and t.id in (",ip_id,") group by vulname");
	end if;
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;

	#select * from tmp_vuldis order by FIELD(level,'C','H','HIGH','M','MED','L','LOW','I');
end;
//


drop procedure if exists create_host_policy//

create procedure create_host_policy()
begin
	declare done int default 0;
	declare union_sql_str varchar(65530);
  declare policy_id_int int(10);
  declare family_int int(10);
	declare vul_id_int int(10);
  declare curl cursor for select 1 as policy_id,family,vul_id from host_family_ref union all select 2 as policy_id,h.family as family,h.vul_id as vul_id from host_family_ref h,vul_info v where h.vul_id=v.vul_id and (v.risk_factor='C' or v.risk_factor='H');
	declare continue handler for sqlstate '02000' set done = 1;

	set union_sql_str = "delete from host_policy_ref where policy_id = 1 or policy_id = 2";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;

	open curl;
	repeat
		fetch curl into policy_id_int,family_int,vul_id_int;
		set union_sql_str = concat("insert into host_policy_ref (policy_id,family_id,vul_id) values (",policy_id_int,",",family_int,",",vul_id_int,")");
		if not done then
			set @E = union_sql_str;
			prepare sql_str from @E;
			execute sql_str;
			deallocate prepare sql_str;
		end if;
	until done
	end repeat;
	close curl;

end;
//


drop procedure if exists create_web_family_ref//

create procedure create_web_family_ref()
begin
	declare done int default 0;
	declare union_sql_str varchar(65530);
    declare vul_id_int int(11);
    declare curl cursor for select vul_id from web_vul_list;
	declare continue handler for sqlstate '02000' set done = 1;
	
	set union_sql_str = "truncate table web_family_ref";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;
	
	open curl;
	repeat
		fetch curl into vul_id_int;
    set union_sql_str = concat("insert into web_family_ref (module,family,vul_id) values ((select f.id from web_family_list f,web_vul_list w where f.desc=w.module and w.vul_id='",vul_id_int,"'),(select f.id from web_family_list f,web_vul_list w where f.desc=w.family and w.vul_id='",vul_id_int,"'),",vul_id_int,")");
		if not done then
			set @E = union_sql_str;
			prepare sql_str from @E;
			execute sql_str;
			deallocate prepare sql_str;
		end if;
	until done
	end repeat;
	close curl;
end;
//


drop procedure if exists create_web_policy//

create procedure create_web_policy()
begin
	declare done int default 0;
	declare union_sql_str varchar(65530);
    declare policy_id_int int(10);
    declare family_int int(10);
	declare vul_id_int int(10);  
    declare curl_fast cursor for select 1 as policy_id,family,vul_id from web_family_ref where vul_id not in (5,6,7,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,26,41,42,44,45,46,140,141,142,143);
	declare curl cursor for select 2 as policy_id,family,vul_id from web_family_ref;
    declare continue handler for sqlstate '02000' set done = 1;

    set union_sql_str = "delete from web_policy_ref where policy_id = 1";
    set @E = union_sql_str;
    prepare sql_str from @E;
    execute sql_str;
    deallocate prepare sql_str;

    open curl_fast;
    repeat
        fetch curl_fast into policy_id_int,family_int,vul_id_int;
        set union_sql_str = concat("insert into web_policy_ref (policy_id,family_id,vul_id) values (",policy_id_int,",",family_int,",",vul_id_int,")");
        if not done then
            set @E = union_sql_str;
            prepare sql_str from @E;
            execute sql_str;
            deallocate prepare sql_str;
        end if;
    until done
    end repeat;
    close curl_fast;

    set done = 0;
	set union_sql_str = "delete from web_policy_ref where policy_id = 2";
	set @E = union_sql_str;
	prepare sql_str from @E;
	execute sql_str;
	deallocate prepare sql_str;

	open curl;
	repeat
		fetch curl into policy_id_int,family_int,vul_id_int;
		set union_sql_str = concat("insert into web_policy_ref (policy_id,family_id,vul_id) values (",policy_id_int,",",family_int,",",vul_id_int,")");
		if not done then
			set @E = union_sql_str;
			prepare sql_str from @E;
			execute sql_str;
			deallocate prepare sql_str;
		end if;
	until done
	end repeat;
	close curl;
end;
//


DELIMITER ;



-- ----------------------------
-- Table structure for `failedlogins`
-- ----------------------------
DROP TABLE IF EXISTS `failedlogins`;
CREATE TABLE `failedlogins` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) NOT NULL,
  `ip` char(45) NOT NULL DEFAULT '',
  `count` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `lastupdate` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `api_auth`
-- ----------------------------
DROP TABLE IF EXISTS `api_auth`;
CREATE TABLE `api_auth` (
  `id` smallint(6) NOT NULL auto_increment,
  `ip` char(80) default NULL,
  `api_id_list` char(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `firewall_vuls`
-- ----------------------------
DROP TABLE IF EXISTS `firewall_vuls`;
CREATE TABLE `firewall_vuls` (
  `id` int(11) NOT NULL auto_increment,
  `vuls` text character set utf8,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `adminlog`
-- ----------------------------
DROP TABLE IF EXISTS `adminlog`;
CREATE TABLE `adminlog` (
  `Id` bigint(11) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(256) CHARACTER SET utf8 DEFAULT NULL,
  `Ip` varchar(45) DEFAULT NULL,
  `LogTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Log` varchar(1024) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for `upgradelog`
-- ----------------------------
DROP TABLE IF EXISTS `upgradelog`;
CREATE TABLE `upgradelog` (
  `Id` bigint(11) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(256) CHARACTER SET utf8 DEFAULT NULL,
  `Ip` varchar(45) DEFAULT NULL,
  `LogTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Log` varchar(1024) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `syslog`
-- ----------------------------
DROP TABLE IF EXISTS `syslog`;
CREATE TABLE `syslog` (
  `Id` bigint(11) NOT NULL AUTO_INCREMENT,
  `LogTime` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `Log` varchar(1024) CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `license`
-- ----------------------------
DROP TABLE IF EXISTS `license`;
CREATE TABLE `license` (
  `Id` bigint(11) NOT NULL auto_increment,
  `Name` varchar(128) character set utf8 default NULL,
  `Value` varchar(1024) character set utf8 default NULL,
  PRIMARY KEY  (`Id`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Records of license
-- ----------------------------
INSERT INTO `license` VALUES ('1', 'license_stat', '0');
INSERT INTO `license` VALUES ('2', 'company', '');
INSERT INTO `license` VALUES ('3', 'license_type', '');
INSERT INTO `license` VALUES ('4', 'license_begin', '');
INSERT INTO `license` VALUES ('5', 'license_end', '');
INSERT INTO `license` VALUES ('6', 'model', '');
INSERT INTO `license` VALUES ('7', 'serial_num', '');
INSERT INTO `license` VALUES ('8', 'random', '');



-- ----------------------------
-- Table structure for `schedule`
-- ----------------------------
DROP TABLE IF EXISTS `schedule`;
CREATE TABLE `schedule` (
  `id` int(10) NOT NULL auto_increment,
  `name` varchar(128) default NULL,
  `desc` varchar(256) default NULL,
  `type` int(5) default NULL,
  `use_count` int(5) default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of schedule
-- ----------------------------
INSERT INTO `schedule` VALUES ('1', '全天', '每天，00:00 - 24:00', '0', '0');
INSERT INTO `schedule` VALUES ('2', '工作时间', '启动任务的时间为：工作日 08:00-17:00。', '1', '0');
INSERT INTO `schedule` VALUES ('3', '下班时间', '启动任务的时间为：工作日 00:00-08:00和17:00-24:00，周六和周日 00:00-24:00。', '1', '0');

-- ----------------------------
-- Table structure for `schedule_detail`
-- ----------------------------
DROP TABLE IF EXISTS `schedule_detail`;
CREATE TABLE `schedule_detail` (
  `id` int(10) NOT NULL auto_increment,
  `sid` int(10) default NULL,
  `day` int(3) default NULL,
  `start` varchar(10) default NULL,
  `end` varchar(10) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of schedule_detail
-- ----------------------------
INSERT INTO `schedule_detail` VALUES ('1', '1', '0', '00:00', '24:00');
INSERT INTO `schedule_detail` VALUES ('2', '2', '1', '08:00', '17:00');
INSERT INTO `schedule_detail` VALUES ('3', '2', '2', '08:00', '17:00');
INSERT INTO `schedule_detail` VALUES ('4', '2', '3', '08:00', '17:00');
INSERT INTO `schedule_detail` VALUES ('5', '2', '4', '08:00', '17:00');
INSERT INTO `schedule_detail` VALUES ('6', '2', '5', '08:00', '17:00');
INSERT INTO `schedule_detail` VALUES ('7', '2', '6', '00:00', '00:00');
INSERT INTO `schedule_detail` VALUES ('8', '2', '7', '00:00', '00:00');
INSERT INTO `schedule_detail` VALUES ('9', '3', '1', '00:00', '08:00');
INSERT INTO `schedule_detail` VALUES ('10', '3', '1', '17:00', '24:00');
INSERT INTO `schedule_detail` VALUES ('11', '3', '2', '00:00', '08:00');
INSERT INTO `schedule_detail` VALUES ('12', '3', '2', '17:00', '24:00');
INSERT INTO `schedule_detail` VALUES ('13', '3', '3', '00:00', '08:00');
INSERT INTO `schedule_detail` VALUES ('14', '3', '3', '17:00', '24:00');
INSERT INTO `schedule_detail` VALUES ('15', '3', '4', '00:00', '08:00');
INSERT INTO `schedule_detail` VALUES ('16', '3', '4', '17:00', '24:00');
INSERT INTO `schedule_detail` VALUES ('17', '3', '5', '00:00', '08:00');
INSERT INTO `schedule_detail` VALUES ('18', '3', '5', '17:00', '24:00');
INSERT INTO `schedule_detail` VALUES ('19', '3', '6', '00:00', '24:00');
INSERT INTO `schedule_detail` VALUES ('20', '3', '7', '00:00', '24:00');

-- ----------------------------
-- Table structure for `packetcapture`
-- ----------------------------
DROP TABLE IF EXISTS `packetcapture`;
CREATE TABLE `packetcapture` (
  `id` int(4) NOT NULL auto_increment,
  `interface` varchar(100) default NULL,
  `count` int(10) default NULL,
  `packet_len` int(10) default NULL,
  `file_name` varchar(100) default NULL,
  `finished` int(1) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for `report_list`
-- ----------------------------
DROP TABLE IF EXISTS `report_list`;
CREATE TABLE `report_list` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) default NULL,
  `desc` varchar(500) default NULL,
  `type` varchar(10) default NULL,
  `size` varchar(20) default NULL,
  `filename` varchar(255) default NULL,
  `create_time` timestamp NULL default NULL,
  `state` int(1) default NULL,
  `task_id` int(11) default NULL,
  `other` text,
  `user_id` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `user_vullist`
-- ----------------------------
DROP TABLE IF EXISTS `user_vullist`;
CREATE TABLE `user_vullist` (
  `Id` int(10) NOT NULL auto_increment,
  `UserId` int(10) default NULL,
  `VulList` varchar(500) default NULL,
  PRIMARY KEY  (`Id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for task_manage
-- ----------------------------
DROP TABLE IF EXISTS `task_manage`;
CREATE TABLE `task_manage` (
  `id` int(11) NOT NULL auto_increment,
  `task_name` varchar(256) default NULL,
  `target` text,
  `state` int(1) default NULL,
  `init_state` int(1) default NULL,
  `prescan_state` int(1) default NULL,
  `c` int(11) default NULL,
  `h` int(11) default NULL,
  `m` int(11) default NULL,
  `l` int(11) default NULL,
  `i` int(11) default NULL,
  `start_time` timestamp NULL default NULL,
  `end_time` timestamp NULL default NULL,
  `schedule` varchar(128) default NULL,
  `host_enable` int(1) default NULL,
  `enable_ddos` int(1) default NULL,
  `host_state` int(1) default NULL,
  `host_policy` int(11) default NULL,
  `host_max_script` int(11) default NULL,
  `host_thread` int(4) default NULL,
  `host_timeout` int(4) default '30',
  `web_enable` int(1) default NULL,
  `web_spider_enable` int(1) default NULL,
  `web_state` int(1) default NULL,
  `web_speed` int(1) default NULL,
  `web_minute_package_count` int(11) default NULL,
  `web_thread` int(4) default NULL,
  `web_policy` int(11) default NULL,
  `web_url_count` int(11) default NULL,
  `web_timeout` int(4) default NULL,
  `web_getdomain_timeout` int(4) default NULL,
  `web_getdomain_policy` int(1) default NULL,
  `web_getdomain_enable` int(1) default NULL,
  `web_getdomain_state` int(1) default NULL,
  `web_exp_try_times` int(11) default NULL,
  `web_exp_try_interval` int(11) default NULL,
  `spider_flag` int(1) default NULL,
  `weak_enable` int(1) default NULL,
  `weak_state` int(1) default NULL,
  `weak_thread` int(4) default NULL,
  `weak_policy` int(11) default NULL,
  `weak_timeout` int(4) default NULL,
  `port_enable` int(1) default NULL,
  `port_state` int(1) default NULL,
  `port_timeout` int(4) default NULL,
  `port_thread` int(4) default NULL,
  `port_policy` int(11) default NULL,
  `vpn_enable` int(1) default '0',
  `web_pause` int(1) default '0',
  `user_id` int(11) default NULL,
  `email` varchar(100) default NULL,
  `asset_scan_id` int(11) default '0',
  `as_id` int(11) default '0',
  `am_id` int(11) default '0',
  `scan_uuid` varchar(128) default '',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `nvscan_list`
-- ----------------------------
DROP TABLE IF EXISTS `nvscan_list`;
CREATE TABLE `nvscan_list` (
  `id` int(11) NOT NULL auto_increment,
  `scan_uuid` varchar(128) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for port_manage
-- ----------------------------
CREATE TABLE `port_manage` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) default NULL,
  `ports` mediumtext,
  `user_id` int(11) default NULL,
  `type` int(1) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
-- ----------------------------
-- Records 
-- ----------------------------
INSERT INTO `port_manage` VALUES ('1', '常用端口', '23,21,80,8080,3389,139,3306,135,1433,22,1,5,7,9,11,13,17,18,19,20,25,31,53,67,37,39,42,43,49,50,63,68,69,70,71,72,73,79,88,95,101,102,105,107,109,110,111,113,115,117', '2','0');
INSERT INTO `port_manage` VALUES ('2', '所有端口', '1-9999', '2','0');


-- ----------------------------
-- Table structure for `host_policy`
-- ----------------------------
DROP TABLE IF EXISTS `host_policy`;
CREATE TABLE `host_policy` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) default NULL,
  `user_id` int(11) default NULL,
  `nvscan_policy_id` int(11) default '-1',
  `enable_ddos` int(1) default '0',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
-- ----------------------------
-- Records of host_policy
-- ----------------------------
INSERT INTO `host_policy` VALUES ('1', '全部主机漏洞', '0' , '-1', '0');
INSERT INTO `host_policy` VALUES ('2', '主机高风险漏洞', '0', '-1', '0');


-- ----------------------------
-- Table structure for `host_policy_ref`
-- ----------------------------
DROP TABLE IF EXISTS `host_policy_ref`;
CREATE TABLE `host_policy_ref` (
  `id` int(11) NOT NULL auto_increment,
  `policy_id` int(11) default NULL,
  `family_id` int(11) default NULL,
  `vul_id` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `vul_id` (`vul_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for web_policy
-- ----------------------------
DROP TABLE IF EXISTS `web_policy`;
CREATE TABLE `web_policy` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(255) default NULL,
  `user_id` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
-- ----------------------------
-- Records of web_policy
-- ----------------------------
INSERT INTO `web_policy` VALUES ('1', '快速扫描Web漏洞', '0');
INSERT INTO `web_policy` VALUES ('2', '全部Web漏洞', '0');


-- ----------------------------
-- Table structure for `web_policy_ref`
-- ----------------------------
DROP TABLE IF EXISTS `web_policy_ref`;
CREATE TABLE `web_policy_ref` (
  `id` int(11) NOT NULL auto_increment,
  `policy_id` int(11) default NULL,
  `family_id` int(11) default NULL,
  `vul_id` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `vul_id` (`vul_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;



-- ----------------------------
-- Table structure for weak_policy
-- ----------------------------
CREATE TABLE `weak_policy` (
  `id` int(11) NOT NULL auto_increment,
  `vuls` varchar(512) default NULL,
  `name` varchar(512) default NULL,
  `type` int(1) default NULL,
  `user_id` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
-- ----------------------------
-- Records 
-- ----------------------------
INSERT INTO `weak_policy` VALUES ('1', '1|2|3|4|5|6|7|8|9', '全部弱密码漏洞', '0','2');


-- ----------------------------
-- Table structure for vul_stats
-- ----------------------------
CREATE TABLE `vul_stats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vul_name` varchar(100) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `c` int(11) DEFAULT NULL,
  `h` int(11) DEFAULT NULL,
  `m` int(11) DEFAULT NULL,
  `l` int(11) DEFAULT NULL,
  `i` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `cookie`
-- ----------------------------
CREATE TABLE `cookie` (
  `id` int(11) NOT NULL auto_increment,
  `domain` varchar(1024) character set utf8 default NULL,
  `url` varchar(1024) character set utf8 default NULL,
  `cookie` text,
  `update_time` timestamp NULL default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `weak_vul_list`
-- ----------------------------
DROP TABLE IF EXISTS `weak_vul_list`;
CREATE TABLE `weak_vul_list` (
  `id` int(11) NOT NULL auto_increment,
  `vul_id` int(11) default NULL,
  `vul_name` varchar(255) default NULL,
  `level` varchar(10) default NULL,
  `desc` text,
  `solu` text,
  `priority` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of weak_vul_list
-- ----------------------------
INSERT INTO `weak_vul_list` VALUES ('1', '1', 'FTP弱密码', 'H', null, null, '1');
INSERT INTO `weak_vul_list` VALUES ('2', '2', 'SSH弱密码', 'H', null, null, '2');
INSERT INTO `weak_vul_list` VALUES ('3', '3', 'Windows远程协助', 'H', null, null, '3');
INSERT INTO `weak_vul_list` VALUES ('4', '4', 'TELNET弱密码', 'H', null, null, '4');
INSERT INTO `weak_vul_list` VALUES ('5', '5', 'MSSQL弱密码', 'H', null, null, '5');
INSERT INTO `weak_vul_list` VALUES ('6', '6', 'MYSQL弱密码', 'H', null, null, '6');
INSERT INTO `weak_vul_list` VALUES ('7', '7', 'ORACLE弱密码', 'H', null, null, '7');
INSERT INTO `weak_vul_list` VALUES ('8', '8', 'SMB弱密码', 'H', null, null, '8');
INSERT INTO `weak_vul_list` VALUES ('9', '9', 'VNC弱密码', 'H', null, null, '9');


-- ----------------------------
-- Table structure for `am_category`
-- ----------------------------
DROP TABLE IF EXISTS `am_category`;
CREATE TABLE `am_category` (
  `AM_Id` int(11) NOT NULL auto_increment,
  `AM_PNode` int(11) NOT NULL,
  `AM_CateName` varchar(20) NOT NULL,
  `AM_Level` int(50) NOT NULL,
  `AM_User` varchar(255) default NULL,
  `AM_Tel` varchar(20) default NULL,
  `AM_Email` varchar(20) default NULL,
  `AM_Comment` text,
  `AM_IP` text,
  `AM_TaskId` text,
  `AM_TaskStartTime` text,
  PRIMARY KEY  (`AM_Id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of am_category
-- ----------------------------
INSERT INTO `am_category` VALUES ('1', '0', '资产树', '0', null, null, null, null, null, null, null);


-- ----------------------------
-- Table structure for `as_register`
-- ----------------------------
DROP TABLE IF EXISTS `as_register`;
CREATE TABLE `as_register` (
  `AS_Id` int(11) NOT NULL auto_increment,
  `AS_CateId` int(11) NOT NULL,
  `AS_TaskId` int(11) default NULL,
  `AS_Name` varchar(255) NOT NULL,
  `AS_Ip` text NOT NULL,
  `AS_Type` int(11) default NULL,
  `AS_Level` varchar(11) default NULL,
  `AS_Value` int(11) default NULL,
  `AS_Owner` varchar(255) default NULL,
  `AS_Comment` text,
  `AS_HighNum` int(11) default NULL,
  `AS_MidNum` int(11) default NULL,
  `AS_LowNum` int(11) default NULL,
  `AS_IsExitDomain` int(11) default NULL,
  `AS_IsSecDomain` int(11) default NULL,
  `AS_LastScanTime` varchar(20) default NULL,
  `checked` int(1) default '2',
  `state` int(1) default '0',
  PRIMARY KEY  (`AS_Id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `asset_scan`
-- ----------------------------
DROP TABLE IF EXISTS `asset_scan`;
CREATE TABLE `asset_scan` (
  `id` int(11) NOT NULL auto_increment,
  `task_name` varchar(256) default NULL,
  `target` text,
  `start_time` timestamp NULL default NULL,
  `end_time` timestamp NULL default NULL,
  `host_enable` int(1) default NULL,
  `enable_ddos` int(1) default NULL,
  `host_state` int(1) default NULL,
  `host_policy` int(11) default NULL,
  `host_max_script` int(11) default NULL,
  `host_thread` int(4) default NULL,
  `host_timeout` int(4) default '30',
  `web_enable` int(1) default NULL,
  `web_spider_enable` int(1) default NULL,
  `web_state` int(1) default NULL,
  `web_thread` int(4) default NULL,
  `web_policy` int(11) default NULL,
  `web_url_count` int(11) default NULL,
  `web_timeout` int(4) default NULL,
  `web_getdomain_timeout` int(4) default NULL,
  `web_getdomain_policy` int(1) default NULL,
  `web_getdomain_enable` int(1) default NULL,
  `web_getdomain_state` int(1) default NULL,
  `web_exp_try_times` int(11) default NULL,
  `web_exp_try_interval` int(11) default NULL,
  `weak_enable` int(1) default NULL,
  `weak_state` int(1) default NULL,
  `weak_thread` int(4) default NULL,
  `weak_policy` int(11) default NULL,
  `weak_timeout` int(4) default NULL,
  `port_enable` int(1) default NULL,
  `port_state` int(1) default NULL,
  `port_timeout` int(4) default NULL,
  `port_thread` int(4) default NULL,
  `port_policy` int(11) default NULL,
  `user_id` int(11) default NULL,
  `task_id` int(11) default NULL,
  `add_time` timestamp NULL default NULL,
  `as_id` int(11) default NULL,
  `am_id` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `assetlog`
-- ----------------------------
DROP TABLE IF EXISTS `assetlog`;
CREATE TABLE `assetlog` (
  `Id` int(11) NOT NULL auto_increment,
  `Depart` varchar(255) NOT NULL,
  `Log` varchar(255) NOT NULL,
  `Ip` varchar(45) NOT NULL,
  `LogTime` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `UserName` varchar(50) NOT NULL,
  `am_id` int(11) default '0',
  PRIMARY KEY  (`Id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for `site_library`
-- ----------------------------
DROP TABLE IF EXISTS `site_library`;
CREATE TABLE `site_library` (
  `id` int(11) NOT NULL auto_increment,
  `site` varchar(255) default NULL,
  `type` tinyint(4) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;




