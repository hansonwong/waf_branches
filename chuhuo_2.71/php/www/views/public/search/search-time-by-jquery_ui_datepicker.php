<script>
	$(function(){
		<?php foreach($timeKey as $item){?>
		$('#<?=$item?>').datetimepicker({timeFormat: 'HH:mm:ss',dateFormat: 'yy-mm-dd'});
		$('#<?=$item?>').blur(function(){
			var obj = $(this);
			var value = obj.val();
			var vueModel = obj.attr('vue-model');
			eval('formData.' + vueModel + ' = value;');
		});
		<?php }?>
	});
</script>