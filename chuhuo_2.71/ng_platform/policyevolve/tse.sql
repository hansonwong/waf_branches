create table m_tbtserules
(
    tseid   int(11) not null AUTO_INCREMENT,
    tsename varchar(255) COMMENT '名称',
    srcip   varchar(255) COMMENT '源IP',
    dstip   varchar(255) COMMENT '目的IP',
    tsetype int(11) COMMENT '类型',
    tsetime datetime COMMENT '时间',
    rejectime int(11) COMMENT '阻断时长',
    memo varchar(255) COMMENT '备注',
    PRIMARY KEY (tseid)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='策略演进规则表';
