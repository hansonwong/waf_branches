<?php
$config = [
    'language' => 'zh-CN',// 设置目标语言为中文
    'sourceLanguage' => 'zh-CN',// 设置源语言为中文
    'components' => [
        'assetManager' => [
            'linkAssets' => true,
            'bundles' => [
                'yii\validators\ValidationAsset' => [
                    //'js' => [],  // 去除 yii.validation.js
                    'sourcePath' => null,  // 防止在 frontend/web/asset 下生产文件
                ],
                'yii\web\JqueryAsset' => [
                    'js' => [],  // 去除 jquery.js
                    'sourcePath' => null,  // 防止在 frontend/web/asset 下生产文件
                ],
            ],
        ],
        //系统初始化
        'sysInit' => [
            'class' => 'app\logic\sys\SysInit',
        ],
        //系统调试
        'sysDebug' => [
            'class' => 'app\logic\sys\SysDebug',
        ],
        //系统登录数据
        'sysLogin' => [
            'class' => 'app\logic\sys\SysLogin',
        ],
        //系统信息
        'sysInfo' => [
            'class' => 'app\logic\sys\SysInfo',
        ],
        //输出JSON字符串
        'sysJsonMsg' => [
            'class' => 'app\logic\sys\SysJsonMsg',
        ],
        //系统路径
        'sysPath' => [
            'class' => 'app\logic\sys\SysPath',
        ],
        //系统参数
        'sysParams' => [
            'class' => 'app\logic\sys\SysParams',
        ],
        //系统语言
        'sysLanguage' => [
            'class' => 'app\logic\sys\SysLanguage',
        ],
        //系统操作日志
        'logCommon' => [
            'class' => 'app\logic\sys\LogCommon',
        ],
        //WAF规则翻译
        'wafRules' => [
            'class' => 'app\logic\waf\wafRules\Language',
        ],
        //waf帮助类
        'wafHelper' => [
            'class' => 'app\logic\waf\helpers\WafHelper',
        ],
        'i18n' => [
            'translations' => [
                'app*' => [
                    'class' => 'yii\i18n\PhpMessageSource',
                    //'basePath' => '@app/messages',
                    'sourceLanguage' => 'zh-CN',
                    'fileMap' => [
                        'app' => 'app.php',
                        'app/error' => 'error.php',
                    ],
                ],
                'wafRules' => [
                    'class' => 'yii\i18n\PhpMessageSource',
                    //'basePath' => '@app/messages',
                    'sourceLanguage' => 'zh-CN-id',
                    'fileMap' => [
                        'app' => 'wafRules.php',
                        'app/error' => 'error.php',
                    ],
                ],
            ],
        ],
        #clickhouse数据库
        'clickhouse' => [
            'class' => 'kak\clickhouse\Connection',
            'dsn' => 'localhost', //$_SERVER['SERVER_ADDR'],
            'port' => '8123',
            'database' => 'default',  // use other database name
            'username' => 'default',
            'password' => 'wafabc123',
            'enableSchemaCache' => true,
            'schemaCache' => 'cache',
            'schemaCacheDuration' => 86400
        ],
        'mailer' => [
            'class' => 'yii\swiftmailer\Mailer',
            'useFileTransport' =>false,//这句一定有，false发送邮件，true只是生成邮件在runtime文件夹下，不发邮件
        ],
    ],
    'aliases' => [],
];
if (YII_ENV_DEV) {
    // configuration adjustments for 'dev' environment
    $config['bootstrap'][] = 'debug';
    $config['modules']['debug'] = [
        'class' => 'yii\debug\Module',
    ];
    $config['bootstrap'][] = 'gii';
    $config['modules']['gii'] = [
        'class' => 'yii\gii\Module',
        'allowedIPs' => ['127.0.0.1',]
    ];
}
return $config;
