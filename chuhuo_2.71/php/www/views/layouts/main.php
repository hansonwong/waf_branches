<?php

/* @var $this \yii\web\View */
/* @var $content string */

use yii\helpers\Html;
use app\assets\AppAsset;
use \yii\helpers\Url;

AppAsset::register($this);

$urlPrefix = Yii::$app->sysPath->resourcePath;
?>
<?php $this->beginPage() ?>
<!DOCTYPE html>
<html lang="<?= Yii::$app->language ?>">
<head>
    <meta charset="<?= Yii::$app->charset ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?= Html::csrfMetaTags() ?>
    <title><?= Html::encode($this->title) ?></title>
    <?php $this->head() ?>
    <!--[if lt IE 7]>
    <script src="<?=$urlPrefix?>assets/waf/js/lib/jqueryie6.min.js" type="text/javascript"></script>
    <![endif]-->

    <!--翻译插件-->
    <script src="<?=$urlPrefix?>assets/js/translation.js"></script>
    <!--<script src="<?/*=Url::to(['language/lang-source-for-js', 'tpl' => 't'])*/?>"></script>-->
    <script>
        $(function(){
            //初始化语言翻译
            translation.init('<?=Url::to(['language/lang-source-for-js', 'tpl' => 'json'])?>');
        });
    </script>
    <!--翻译属性-->
    <!--<script src="<?/*=$staticResourcePrefix*/?>js/lib/baseLanguage.js" type="text/javascript"></script>-->
    <script src="<?=Url::to(['language/lang-source-for-js', 'tpl' => 'b'])?>" type="text/javascript"></script>
</head>
<body>
<?php $this->beginBody() ?>
<?= $content ?>
<?php $this->endBody() ?>
</body>
</html>
<?php $this->endPage() ?>
