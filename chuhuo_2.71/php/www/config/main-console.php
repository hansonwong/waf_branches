<?php
$params = array_merge(
    require('params.php'),
    require('params-local.php')
);

return [
    'basePath' => dirname(__DIR__),
    'vendorPath' => $frameworkDir . '/vendor/',
    'runtimePath' => $runtimeDir,
    'controllerNamespace' => 'app\\controllersConsole',
    'aliases' => [
        '@app' => $projectDir,
    ],

    'id' => 'app-console',
    'bootstrap' => ['log'],
    'controllerMap' => [
        'fixture' => [
            'class' => 'yii\console\controllers\FixtureController',
            'namespace' => 'common\fixtures',
          ],
        'migrate' => [
            'class' => 'yii\console\controllers\MigrateController',
            'migrationTable' => 't_migrate_yii',
            'migrationPath' => '@app/migrations',
            'templateFile' => '@app/views/migrations/tpl-class.php',
        ],
    ],
    'components' => [
        'log' => [
            'targets' => [
                [
                    'class' => 'yii\log\FileTarget',
                    'levels' => ['error', 'warning'],
                ],
            ],
        ],
    ],
    'params' => $params,
];
