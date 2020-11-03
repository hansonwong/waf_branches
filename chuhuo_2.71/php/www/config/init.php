<?php

$projectDir = realpath(__DIR__."/../");#项目根路径

#配置
$config = json_decode(file_get_contents(realpath("{$projectDir}/../cache").'/interfaceConfig.json'), true);

$runtimeDir = realpath("{$projectDir}/../cache").'/runtime';#缓存路径
$frameworkDir = $config['frameworkDir'];#框架路径
$mysql = $config['mysql'];#mysql配置
