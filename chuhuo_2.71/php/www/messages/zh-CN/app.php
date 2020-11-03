<?php
$dir = explode('/', __DIR__);
return \Yii::$app->sysLanguage->getAllTranslateCache(end($dir));