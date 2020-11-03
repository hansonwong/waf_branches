<?php use yii\helpers\Html;
$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}assets/waf/";?>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<meta name="renderer" content="webkit|ie-comp|ie-stand">
<!--<meta name="viewport" content="width=device-width,initial-scale=1,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no" />-->
<meta http-equiv="Cache-Control" content="no-siteapp" />
<?=Html::csrfMetaTags()?>

<!--可以在收藏夹中显示出图标-->
<link rel="Bookmark" href="<?=$urlPrefix?>favicon.ico" type="image/x-icon"/>
<!--可以在地址栏中显示出图标-->
<link rel="shortcut icon" href="<?=$urlPrefix?>favicon.ico" type="image/x-icon"/>
<link rel="icon" href="<?=$urlPrefix?>favicon.ico" type="image/x-icon"/>

<!--公共-->
<link href="<?=$staticResourcePrefix?>skin/blue/style/public.css" rel="stylesheet" type="text/css">
<link href="<?=$staticResourcePrefix?>skin/blue/style/style.css" rel="stylesheet" type="text/css">
<link href="<?=$staticResourcePrefix?>skin/blue/style/style_waf.css" rel="stylesheet" type="text/css">
