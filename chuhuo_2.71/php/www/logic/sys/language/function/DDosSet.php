<?php
//DDOS防护设置 DDosSetController
return [
    'dDosDefendConfig' => 'DDOS防护设置',
    'dDosDefend' => 'DDOS防护',
    'dDosDefendEnable' => '开启DDOS云防护',
    'networkFlowSelect' => '网络流量选择',
    'recommendThreshold' => '推荐阈值',
    'recommendThresholdTips' => '系统根据选择的网络流量,推荐合理的阀值范围',
    'totalFlowThresholdTrigger' => '总流量触发阀值',
    'dataPackage/second' => '数据包/秒',
    'totalFlowThreshold/singleIP' => '总流量阀值/单IP',
    'packageThresholdTrigger' => '包触发阀值',
    'packageThreshold/singleIP' => '包阀值/单IP',
    'SYN FloodThresholdTrigger' => 'SYN Flood触发阀值',
    'SYN FloodThreshold/singleIP' => 'SYN Flood阀值/单IP',
    'otherTCP FloodThresholdTrigger' => '其它TCP Flood触发阀值',
    'otherTCP FloodThreshold/singleIP' => '其它TCP Flood阀值/单IP',
    'allUdpProtocolCommunicationDisableTips' => '禁止所有UDP协议的通信. (启用后所有使用UDP协议的通信将被禁止,包括使用UDP协议的DNS解释服务',
    'allIcmpProtocolCommunicationDisableTips' => '禁止所有ICMP协议的通信. (启用后所有使用ICMP协议的通信将被禁止,包括使用ICMP协议的PING请求',
    'dDosDefendConfigTips' => '以上所有项请填写大于0的正整数,各项阀值建议不小于',
    'networkFlowSelectTips' => '网络流量请填写1-1024以内的数值',
];