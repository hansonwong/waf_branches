<?php
use \yii\helpers\Url;
use yii\helpers\Html;
?>
<div class="openWin" >
<form action="" method="post" id="form_id">
    <!--授权信息-->
  <h1><?=Yii::$app->sysLanguage->getTranslateBySymbol('authorizationInformation') ?></h1>
  <div class="jbxx sj">
    <table width="80%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
      <tr>
          <!--授权序列号-->
        <td width="120" class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('authorizationSequenceNumber') ?>：</td>
        <td ><?=$model['sn']?></td>
      </tr>
      <tr>
          <!--有效期-->
          <td class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('termOfValidity') ?>：</td>
          <td ><?=date('Y-m-d H:i:s',$model['validate'])?></td>
      </tr>
      <tr>
          <!--公司名称-->
        <td class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('corporateName') ?>：</td>
        <td ><?=$model['company']?></td>
      </tr>
      <tr>
          <!--公司地址-->
          <td class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('companyAddress') ?>：</td>
          <td ><?=$model['address']?></td>
      </tr>
      <tr>
          <!--电子邮箱-->
        <td class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('email') ?>：</td>
        <td ><?=$model['email']?></td>
      </tr>
      <tr>
          <!--联系电话-->
          <td class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('phone') ?>：</td>
          <td ><?=$model['telephone']?></td>
      </tr>                                    
     </table>
  </div>
</form>


<form action="" method="post" id="form_id">
    <!--许可证文件-->
<h1><?=Yii::$app->sysLanguage->getTranslateBySymbol('licenseDocument') ?></h1>
<div class="jbxx  sj">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
    <tr>
        <!--选择有效期内的许可证文件-->
      <td><span class="red">*<?=Yii::$app->sysLanguage->getTranslateBySymbol('selectTheValidityPeriodOfTheLicenseFile') ?></span></td>
    <tr>
    </tr>      
      <td>
        <input name="txt2" type="text" class="input_text_wid" id="txt2" />
          <!--选择文件-->
        <input type="button" class="btn_ty"  value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('chooseFile') ?>" />
        <input class="input_file" size="30" name="license_file" type="file" onchange="txt2.value=this.value" />
      </td>
    <tr>
    </tr>
      <!--上传-->
      <td><input name="input" type="button" onclick="return doSubmit();" class="btn_ty" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('upload') ?>" /></td>
    </tr>
  </table>
</div>
</form>
</div>
<script type="text/javascript">
	function doSubmit()
	{
		var _csrf = $('meta[name=csrf-token]').attr('content');

        var form_data = new FormData();
        form_data.append('_csrf',_csrf);
        form_data.append('file',$('input[name="license_file"]')[0].files[0]);
		
		$.ajax({
			url: '<?php echo Url::to(['config']);?>',
			type: 'POST',
			data: form_data, 
			cache: false,
            processData: false,
            contentType: false,
			timeout: 30000,
			success: function(data){
				var _data = JSON.parse(data);
				if(_data.code === 'T')
				{
					art.dialog({icon: 'succeed',content: _data['info'],	time: 1	});
				}else{
					art.dialog({icon: 'error',	content: _data['info'],	time: 2	});
				}
			}
		});
	}
</script>