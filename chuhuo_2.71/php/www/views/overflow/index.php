<?php
use \yii\helpers\Url;
use yii\helpers\Html;
?>
<style type="text/css">
    html{overflow-y:auto;}
</style>
<div class="openWin" >
<form action="" method="post" id="form_id">
    <!--防溢出设置(超出指定范围的将被禁止)-->
  <h1><?=Yii::$app->sysLanguage->getTranslateBySymbol('overflowConfig')?>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('beyondSpecifiedScopeWillBeProhibited')?>)</h1>
  <div class="jbxx sj">
    <table width="80%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
          <tr>
              <td width="180" class="t_r"><span class="red">*</span>Accept <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="Accept" type="text" value="<?=$model['Accept']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>  
          <tr>
              <td class="t_r"><span class="red">*</span>Accept-Charset <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="Accept-Charset" type="text" value="<?=$model['Accept-Charset']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>            
          <tr>
              <td class="t_r"><span class="red">*</span>Accept-Encoding <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="Accept-Encoding" type="text" value="<?=$model['Accept-Encoding']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>  
          <tr>
              <td class="t_r"><span class="red">*</span>Cookie <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="Cookie" type="text" value="<?=$model['Cookie']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>
          <tr>
              <td class="t_r"><span class="red">*</span>Post <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="Post" type="text" value="<?=$model['Post']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>  
          <tr>
              <td class="t_r"><span class="red">*</span>URI <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="URI" type="text" value="<?=$model['URI']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>            
          <tr>
              <td class="t_r"><span class="red">*</span>Host <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="Host" type="text" value="<?=$model['Host']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>  
          <tr>
              <td class="t_r"><span class="red">*</span>Referer <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="Referer" type="text" value="<?=$model['Referer']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>
          <tr>
              <td class="t_r"><span class="red">*</span>Authorization <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="Authorization" type="text" value="<?=$model['Authorization']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>            
          <tr>
              <td class="t_r"><span class="red">*</span>Poxy-Authorization <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="Poxy-Authorization" type="text" value="<?=$model['Poxy-Authorization']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>  
          <tr>
              <td class="t_r"><span class="red">*</span>User-Agent <?=Yii::$app->sysLanguage->getTranslateBySymbol('length')?>:</td>
              <td >
               <input name="User-Agent" type="text" value="<?=$model['User-Agent']?>" class="validate[required,custom[integer],min[0],max[2147483647]] text"/>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('bytes')?>)
            </td>
          </tr>
          <tr>
              <td class="t_r"></td>
              <td >
                <span class="red"><?=Yii::$app->sysLanguage->getTranslateBySymbol('overflowConfigTips')?></span>
              </td>
          </tr>          
          <tr>
              <td class="t_r"></td>
              <td >
                <input type="button" name="" onclick="return doSubmit();" id="btnOk" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('done')?>" class="btn_ty"/>
                <input type="button" name="" onclick="return recover();"  value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('reduction')?>" class="btn_ty"/> 
            </td>
          </tr>                                 
     </table>
  </div>
</form>
</div>
  
<script>
jQuery(document).ready(function(){
});
</script>
<script type="text/javascript">
	function doSubmit()
	{
		var accept = $('input[name="Accept"]').val();
		var acceptCharset = $('input[name="Accept-Charset"]').val();
		var acceptEncoding = $('input[name="Accept-Encoding"]').val();
		var cookie = $('input[name="Cookie"]').val();
		var post = $('input[name="Post"]').val();
		var uri = $('input[name="URI"]').val();
		var host = $('input[name="Host"]').val();
		var referer = $('input[name="Referer"]').val();
		var authorization = $('input[name="Authorization"]').val();
		var poxyAuthorization = $('input[name="Poxy-Authorization"]').val();
		var userAgent = $('input[name="User-Agent"]').val();
		
		var _csrf = $('meta[name=csrf-token]').attr('content');

		$.ajax({
			url: "<?php echo Url::to(['config']);?>"+"&id=1",
            type: 'POST',
			dataType: "json",
			data:{
				'_csrf':_csrf,
				'Accept':accept,
				'Accept-Charset':acceptCharset,
				'Accept-Encoding':acceptEncoding,
				'Cookie':cookie,
				'Post':post,
				'URI':uri,
				'Host':host,
				'Referer':referer,
				'Authorization':authorization,
				'Poxy-Authorization':poxyAuthorization,
				'User-Agent':userAgent
			},
			cache: false,
            timeout: 30000,
			success: function(data){
				if(data.code === 'T')
				{
					art.dialog({icon: 'succeed', content: data['info'],	time: 1});
				}else{
					art.dialog({icon: 'error', content: data['info'], time: 2});
				}
            }
		});
	}
    
    function recover(){
		$('input[name="Accept"]').val(2048);
		$('input[name="Accept-Charset"]').val(2048);
		$('input[name="Accept-Encoding"]').val(2048);
		$('input[name="Cookie"]').val(32767);
		$('input[name="Post"]').val(2048);
		$('input[name="URI"]').val(2048);
		$('input[name="Host"]').val(2048);
		$('input[name="Referer"]').val(2048);
		$('input[name="Authorization"]').val(2048);
		$('input[name="Poxy-Authorization"]').val(2048);
		$('input[name="User-Agent"]').val(2048);
    }
</script>
