create table m_tbtserules
(
    tseid   int(11) not null AUTO_INCREMENT,
    tsename varchar(255) COMMENT '����',
    srcip   varchar(255) COMMENT 'ԴIP',
    dstip   varchar(255) COMMENT 'Ŀ��IP',
    tsetype int(11) COMMENT '����',
    tsetime datetime COMMENT 'ʱ��',
    rejectime int(11) COMMENT '���ʱ��',
    memo varchar(255) COMMENT '��ע',
    PRIMARY KEY (tseid)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='�����ݽ������';
