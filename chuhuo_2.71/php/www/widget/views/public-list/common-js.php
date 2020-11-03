<?php
use \yii\helpers\Url;
$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}assets/waf/";?>

<script src="<?=$staticResourcePrefix?>js/lib/jquery.min.js" type="text/javascript"></script>
<!--[if lt IE 7]>
<script src="<?=$staticResourcePrefix?>js/lib/jqueryie6.min.js" type="text/javascript"></script>
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

<!--grid-->
<link href="<?=$staticResourcePrefix?>js/lib/ligerUI/css/ligerui-all.css" rel="stylesheet" type="text/css"/>
<script src="<?=$staticResourcePrefix?>js/lib/ligerUI/js/base.js" type="text/javascript"></script>
<script src="<?=$staticResourcePrefix?>js/lib/ligerUI/js/ligerGrid.js" type="text/javascript"></script>
<script src="<?=$staticResourcePrefix?>js/lib/ligerUI/js/GridList.js" type="text/javascript"></script>
<script src="<?=$staticResourcePrefix?>js/bd/grid.js" type="text/javascript"></script>
<!--dialog-->
<link href="<?=$staticResourcePrefix?>js/lib/dialog/dialog.css" rel="stylesheet" type="text/css">
<script type="text/javascript" src="<?=$staticResourcePrefix?>js/lib/dialog/jquery.artDialog.source.js"></script>
<script type="text/javascript" src="<?=$staticResourcePrefix?>js/lib/dialog/iframeTools.source.js"></script>

<!--弹出框封装和日历的扩展-->
<script type="text/javascript" src="<?=$staticResourcePrefix?>js/lib/unit.js"></script>

<script src="<?=$staticResourcePrefix?>js/lib/My97DatePicker/WdatePicker.js"></script>

<script src="<?=$urlPrefix?>assets/js/cookies.js"></script>
<script src="<?=$urlPrefix?>assets/js/common.js"></script>
<script src="<?=$urlPrefix?>assets/js/form.js"></script>