<!DOCTYPE HTML>
<html>
<head>
<?php
use \yii\helpers\Url;
use app\widget\AdminList;?>
<?=AdminList::widget(['type' => 'common-css'])?>
<?=AdminList::widget(['type' => 'common-js'])?>
</head>
<body>
<div class="page-container">
	<a href="javascript:;" onclick="CleanCache(this);" data="all" class="btn c_g btn_add"><?=Yii::$app->sysLanguage->getTranslateBySymbol('clearAllCache')?></a>
	<a href="javascript:;" onclick="CleanCache(this);" data="proMenu" class="btn c_g btn_add"><?=Yii::$app->sysLanguage->getTranslateBySymbol('clearSysMenuCache')?></a>
</div>


<script>
	function CleanCache(obj){
		var jobj = $(obj);
		$.ajax({
			url: '<?=Url::to(['clean-cache'])?>',
			type: 'POST',
			data: {
				data      : jobj.attr('data'),
				_csrf   : $('meta[name=csrf-token]').attr('content'),
			},
			dataType: 'json',
			timeout: 5000,
			cache: false,
			async: false,
			success: function(data){
				if(true === data.success) alert('<?=Yii::$app->sysLanguage->getTranslateBySymbol('clearCacheSuccess')?>');
			},
		});
	}
</script>

<?php $this->endBody(); ?>
</body>
</html>