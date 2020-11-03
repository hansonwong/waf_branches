<?php
//CC防护设置 CcSetController
return [
    'sourceIpDefendCc' => '来源IP防CC',
    'sourceIpAddrVisitRateLimiting' => '来源IP地址访问速率限制',
    'requestCountUpperLimitTips' => '启用后,来源IP地址的访问次数超过设定上限的.禁止该IP地址的任何后续访问',
    'requestCountUpperLimit' => '请求次数上限',
    'blockVisitTime' => '阻止访问时间',
    'destinationUriVisitRateLimiting' => '目的URI访问速率限制',
    'destinationUriVisitRateLimitingTips' => '启用后,来源IP对目的URI的访问次数超过设定上限的.禁止该IP地址的任何后续访问',
    'destinationUriList' => '目的URI列表',
    'destinationUriListTips' => '每行一条URI,可输入多行并确保uri正确. 例: /test.php（不用输入参数部分）',
    'sourceIpDefendCcTips' => '请填写 "来源IP防CC" 的相关参数',
    'destinationUriDefendCcTips' => '请填写 "特定URL防CC" 的相关参数',
    'givenUriDefendCc' => '特定URI防CC',
    'times' => '次',
];