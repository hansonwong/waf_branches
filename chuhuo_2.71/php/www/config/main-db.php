<?php
$dbs = [];

#mysql组件
foreach ($mysql as $dbk => $dbv){
    $dbs[$dbv['yiiKey']] = [
        'class' => 'yii\db\Connection',
        'dsn' => "mysql:host={$dbv['host']};dbname={$dbv['dbName']};port={$dbv['port']}",
        'username' => $dbv['user'],
        'password' => $dbv['pwd'],
        'charset' => 'utf8',
    ];
}
return ['components' => $dbs,];