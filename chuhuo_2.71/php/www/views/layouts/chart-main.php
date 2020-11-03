<?php
use yii\helpers\Html;
use yii\bootstrap\Nav;
use yii\bootstrap\NavBar;
use yii\widgets\Breadcrumbs;
use frontend\assets\AppAsset;
use common\widgets\Alert;
use app\widget\AdminList;

AppAsset::register($this);

$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}assets/waf/";
?>
<?php $this->beginPage() ?>
<!DOCTYPE html>
<html lang="<?= Yii::$app->language ?>">
<head>
    <?=AdminList::widget(['type' => 'common-css'])?>
    <?=AdminList::widget(['type' => 'common-js'])?>

    <!--日历-->
    <script language="javascript" type="text/javascript" src="<?=$staticResourcePrefix?>js/lib/My97DatePicker/WdatePicker.js"></script>

    <!--报表-->
    <!--<script src="<?/*=$staticResourcePrefix*/?>js/lib/echarts/echarts-all.js"></script>-->
    <script src="<?=$urlPrefix?>assets/js/echarts/echarts.min.js"></script>

    <style type="text/css">
        html{overflow-y:auto;}
    </style>
    </head>
<body>
<script>
    var chart;
    $(function(){
        //echarts自适应
        window.addEventListener("resize", function () {
            try{
                if("function" == typeof(chart.resize)) chart.resize();
            } catch (error) {}
        });
    });
</script>
<?php $this->beginBody();?>
<?=$content?>
<?php $this->endBody();?>
</body>
</html>
<?php $this->endPage();?>
