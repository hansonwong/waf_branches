<!DOCTYPE HTML>
<?php
use app\widget\AdminList;
use \yii\helpers\Url;
$urlPrefix = Yii::$app->sysPath->resourcePath;?>
<html>
<head>
    <?=AdminList::widget(['type' => 'common-css'])?>
    <?=AdminList::widget(['type' => 'common-js'])?>
	<script src="<?=$urlPrefix?>assets/js/vue/vue.js"></script>
</head>
<body>
<?=$customStr['header'] ?? ''?>
<div class="list_page">
<?php
$searchForm = $search ? AdminList::widget(['type' => 'search', 'config' => ['search' => $search]]) : '';
echo AdminList::widget(['type' => 'table', 'config' => ['table' => $table, 'searchForm' => $searchForm]]);
?>
<!--<style>.l-grid-row-cell-inner{margin-left:10px;}</style>-->
</div>
<?=$customStr['footer'] ?? ''?>
<?php $this->endBody();?>
</body>
</html>