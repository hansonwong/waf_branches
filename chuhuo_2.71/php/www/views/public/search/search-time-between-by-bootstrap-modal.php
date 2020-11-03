<div id="<?=$config['field']?>_select" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
	<div class="modal-header">
		<h5><?=$config['label']?></h5><a class="close" data-dismiss="modal" aria-hidden="true" href="javascript:void();">×</a>
	</div>
	<div class="modal-body">
		<div class="row cl">
			<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStart')?>：</label>
			<div class="formControls col-xs-8 col-sm-9">
				<input type=text class="input-text" id="<?=$config['field']?>_time_start">
			</div>
		</div>
		<div class="row cl mt-10">
			<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStop')?>：</label>
			<div class="formControls col-xs-8 col-sm-9">
				<input type=text class="input-text" id="<?=$config['field']?>_time_stop">
			</div>
		</div>
	</div>
	<div class="modal-footer">
		<button class="btn btn-primary" data-dismiss="modal" onclick="<?=$config['field']?>_set();" aria-hidden="true"><?=Yii::$app->sysLanguage->getTranslateBySymbol('done')?></button>
		<button class="btn" data-dismiss="modal" aria-hidden="true"><?=Yii::$app->sysLanguage->getTranslateBySymbol('close')?></button>
	</div>
</div>
<style>#<?=$config['field']?>_select .modal-body .row div{z-index:2000;}</style>
<script>
	$(function(){
		$('#<?=$config['field']?>').click(function(){
			$('#<?=$config['field']?>_select').modal('toggle');
		});

		$('#<?=$config['field']?>_time_start').datetimepicker({timeFormat: 'HH:mm:ss',dateFormat: 'yy-mm-dd'});
		$('#<?=$config['field']?>_time_stop').datetimepicker({timeFormat: 'HH:mm:ss',dateFormat: 'yy-mm-dd'});
	});
	function <?=$config['field']?>_set(){
		var val = $('#<?=$config['field']?>_time_start').val() + '~' + $('#<?=$config['field']?>_time_stop').val();

		var obj = $('#<?=$config['field']?>');
		var vueModel = obj.attr('vue-model');
		eval('formData.' + vueModel + ' = val;');
	}
</script>
