<?php
#$wafDownloadRealPath = realpath("{$projectDir}/../download/").'/';//日志物理根路径
$wafDownloadRealPath = "/var/wafDownload/";//日志物理根路径
$wafDownLoadPath = '/wafDownload/';//下载根路径
$wafCacheRealPath = realpath("{$projectDir}/../cache/").'/';//缓存物理根路径
//WAF日志路径配置
$wafReportRealPath = "{$wafDownloadRealPath}report/";
$wafReportDownPath = "{$wafDownLoadPath}report/";
$wafReportPath = [
    'realPath' => $wafReportRealPath,//日志物理根路径
    'immediatelyPath' => "{$wafReportRealPath}immediately/",//即时报表物理根路径
    'timerPath' => "{$wafReportRealPath}timer/",//定时报表物理根路径
    'cachePath' => "{$wafReportRealPath}cache/",//报表处理临时目录物理根路径
    //静态JS/CSS物理路径
    'staticResource' => [
        "{$wafReportRealPath}jquery.js",

    ],
    'immediatelyPathDown' => "{$wafReportDownPath}immediately/",//即时报表下载根路径
    'timerPathDown' => "{$wafReportDownPath}timer/",//定时报表下载根路径
];
//漏洞扫描结果目录配置
$wafLoopholeScanResultPath = [
    'realPath' => "{$wafDownloadRealPath}loopholeScanResult/",//物理路径
    'downPath' => "{$wafDownLoadPath}loopholeScanResult/",//下载路径
];
//支持下载的配置文件
$wafDownloadCachePath = [
    'realPath' => "{$wafDownloadRealPath}web/cache/",//物理路径
    'downPath' => "{$wafDownLoadPath}web/cache/",//下载路径
];
//系统升级迁移目录
$systemUpgradePath = [
    'realPath' => [
        'up' => "{$wafDownloadRealPath}migrate/up",
        'bak' => "{$wafDownloadRealPath}migrate/bak",
    ],
];

return [
    //系统版权信息
    'systemCopyRight' => [
        'copyRight' => 'companyCopyRight',
        'projectName' => 'companyProjectName',
    ],
    //系统session key
    'systemSessionKey' => 'PHPSESSID',
    //系统时区
    'systemTimezone' => 'Asia/Shanghai',
    //系统路径前缀数组
    'systemUrl' => [
        //路径前缀
        'prefix' => [
            'root' => '/', 'waf' => '/waf/'
        ],

        #免权限判断路由
        'routePass' => [
            'route' => [
                'language-set' => 'language/language-set',//设置系统语言
                'language/lang-source-for-js',//获取当前语言环境js翻译key->val对
            ],
            'controller' => [
                'index',
                'test' => 'test',
            ]
        ],

        #免登录超时判断路由
        'routePassForLoginTimeout' => [
            'routeException' => [
                'index/index',
            ],
            'route' => ['site/check-login-timeout'],
            'controller' => [
                'index', 'test'
            ]
        ],
    ],
    //防火墙项目配置
    'systemFirewall' => [
        'systemEnable' => true,
        'adminUser' => [
            'audit' => ['name' => '安全审计员', 'pwd' => 'Bluedon@2016'],
            'secadmin' => ['name' => '安全管理员', 'pwd' => 'Bluedon@2016'],
            'admin' => ['name' => '系统管理员', 'pwd' => 'Bluedon@2016'],
            'root' => ['name' => '超级管理员', 'pwd' => 'BluedonNGFW@2017'],
        ],
        'adminRole' => [
            '3' => '安全审计员',//安全审计员:3
            '2' => '安全管理员',//安全管理员:2
            '1' => '系统管理员',//系统管理员:1
            '0' => '超级管理员',//超级管理员:0
        ],
    ],
    //系统路径配置
    'systemPath' => [
        'projectRootPath' => "{$projectDir}/",//项目根路径
        'cachePath' => $wafCacheRealPath,//配置缓存
        'systemUpgradePath' => $systemUpgradePath,#系统升级迁移目录
        'downloadPath' => $wafDownloadCachePath,//web下载缓存
        'wafReportPath' => $wafReportPath,//WAF日志路径
        'loopholeScanResultPath' => $wafLoopholeScanResultPath,//漏洞扫描文件存放路径
        'debugLog' => realpath("{$projectDir}/../download/debug/").'/',//系统调试文件存放路径
    ],

    //系统语言配置
    'systemLanguage' => [
        'zh-CN' => [
            'name' => '中文',
            'firewallUrl' => '/Production/Language.htm5?hl=zh_cn&type=2',
            'model' => '\\app\\models\\SysLanguageSource'
        ],
        'en-US' => [
            'name' => 'english',
            'firewallUrl' => '/Production/Language.htm5?hl=en_us&type=2',
            'model' => '\\app\\models\\SysLanguageEnUs'
        ],
    ],
    //表单配置
    'commonSubmitConfig' => [
        'form' => [
            'id' => 'configForm',
        ],
    ]
];
