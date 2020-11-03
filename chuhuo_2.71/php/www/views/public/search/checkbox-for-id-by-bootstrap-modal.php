<script>
	$(function(){
		$('#<?=$config['field']?>').focus(function(){
			$('#<?=$config['field']?>_select').modal('toggle');
		});
	});

	function <?=$config['field']?>_search(){
		var htmlTpl = $('#<?=$config['field']?>_button').html();
		$.ajax({
			url: '/<?=$config['url']?>',
			type: 'POST',
			data: {
				_csrf	: $('meta[name=csrf-token]').attr('content'),
				<?php if(isset($config['conditionFields'])):
				$conditionFields = $config['conditionFields'];
				foreach ($conditionFields as $conditionField):
					echo "{$conditionField}:$('#{$conditionField}').val(),";
				endforeach;endif;?>
			},
			dataType: 'json',
			timeout: 10000,//1000毫秒后超时
			cache: false,//不缓存数据
			async: false,//同步：false,异步：true,默认true
			success: function(data){
				var html = '';
				for(var i = 0; i < data.length; i++){
					html += substitute(htmlTpl, data[i]);
				}
				$('#<?=$config['field']?>_area').html(html);
			},//请求成功后执行
		});
	}
	function <?php echo $config['field'];?>_set(){
		var value = '';
		$('input[name="<?="{$config['field']}_set"?>"]:checked').each(function(){
			value += this.value + '<?="{$config['split']}"?>';
		});
		value = value.slice(0,-1);
		var obj = $('#<?=$config['field']?>');
		var vueModel = obj.attr('vue-model');
		eval('formData.' + vueModel + ' = value;');
	}
</script>

<div id="<?=$config['field']?>_select" data-width="90%" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
	<div class="modal-header">
		<h5><?=$config['label']?></h5><a class="close" data-dismiss="modal" aria-hidden="true" href="javascript:void();">×</a>
	</div>
	<div class="modal-body">
		<div class="row cl mt-10">
			<label class="form-label col-xs-2 col-sm-2"><?=$config['label']?>：</label>
			<div class="formControls col-xs-10 col-sm-10" id="<?=$config['field']?>_area"></div>
		</div>
	</div>
	<div class="modal-footer">
		<button class="btn btn-primary" onclick="<?=$config['field']?>_search();"><?=Yii::$app->sysLanguage->getTranslateBySymbol('search')?></button>
		<button class="btn btn-primary" onclick="<?=$config['field']?>_set();" data-dismiss="modal" aria-hidden="true"><?=Yii::$app->sysLanguage->getTranslateBySymbol('done')?></button>
		<button class="btn" data-dismiss="modal" aria-hidden="true"><?=Yii::$app->sysLanguage->getTranslateBySymbol('close')?></button>
	</div>
</div>

<?php $data = explode(':', $config['data']);
$dataKey = explode(',', $data[0]);
$dataVal = explode(',', $data[1]);
$dataK = $dataV = '';
foreach ($dataKey as $item){
	$dataK .= "{{$item}}";
}
foreach ($dataVal as $item){
	$dataV .= "{{$item}}";
}
?>
<script type="tpl" id="<?=$config['field']?>_button">
	<?="<label><input type='checkbox' name='{$config['field']}_set' value='{$dataK}'>{$dataV}</label>&nbsp;&nbsp;"?>
</script>
<style>#<?=$config['field']?>_area label{display:inline-block;}</style>