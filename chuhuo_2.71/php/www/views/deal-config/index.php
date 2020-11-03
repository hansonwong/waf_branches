<?php

use \yii\helpers\Url;
use yii\helpers\Html;
$downloadPath = Yii::$app->sysPath->downloadPath;
$downPath = $downloadPath['downPath'];
?>
<div class="openWin">
<form action="" method="post" id="form_id">
<h1> <?=Yii::$app->sysLanguage->getTranslateBySymbol('recoverDefaultConfig')?></h1>
<div class="jbxx sj">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
    <tr>
      <td >* <?=Yii::$app->sysLanguage->getTranslateBySymbol('recoverDefaultConfigTips')?></td>
    <tr>
    </tr>
      <td><input name="input" type="button" id="btn_hfmrpz" class="btn_ty" value=" <?=Yii::$app->sysLanguage->getTranslateBySymbol('recoverDefaultConfig')?>" /></td>
    </tr>
  </table>
</div>
<h1><?=Yii::$app->sysLanguage->getTranslateBySymbol('importConfigFile')?></h1>
<div class="jbxx  sj">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
    <tr>
      <td >* <?=Yii::$app->sysLanguage->getTranslateBySymbol('recoverByConfigFileTips')?></td>
    <tr>
    </tr>
      <td>
        <input name="txt2" type="text" class="input_text_wid" id="txt2" />
        <input type="button" class="btn_ty" value=" <?=Yii::$app->sysLanguage->getTranslateBySymbol('chooseFile')?>" />
        <input class="input_file" name ="input_file" size="30" type="file" onchange="txt2.value=this.value" />
      </td>
    <tr>
    </tr>
      <td><input name="input" type="button" onclick="javascript:doClick(2);" class="btn_ty" value=" <?=Yii::$app->sysLanguage->getTranslateBySymbol('importConfig')?>" /></td>
    </tr>
  </table>
</div>

<h1> <?=Yii::$app->sysLanguage->getTranslateBySymbol('exportConfigFile')?></h1>
<div class="jbxx sj">
  <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
    <tr>
      <td >* <?=Yii::$app->sysLanguage->getTranslateBySymbol('backupDatabaseConfigTips')?>。</td>
    <tr>
    </tr>
      <td><input name="input" type="button" onclick="javascript:doClick(3);" class="btn_ty" value=" <?=Yii::$app->sysLanguage->getTranslateBySymbol('exportConfig')?>" /><span class="red" id="msg"></span></td>
    </tr>
  </table>
</div>
</form>
</div>

<script type="text/javascript">
	function doClick(nType)
    {
		if(nType){
			doSubmit(nType);
		}else{
		  return false;
		}
	}

    function doSubmit(nType)
    {
        var _csrf = $('meta[name=csrf-token]').attr('content');
        if(nType === 2)
        {
            var form_data = new FormData();
            form_data.append('_csrf',_csrf);
            form_data.append('file',$('input[name="input_file"]')[0].files[0]);

            $.ajax({
                url: '<?php echo Url::to(['config']);?>'+'&id='+nType,
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
                        art.dialog({icon: 'succeed', content: _data.info, time: 1});
                    }
                    else
                    {
                        art.dialog({icon: 'error', content: _data.info, time: 1});
                    }
                }
            });
        }
        else
        {
            if(nType === 3)
            {
                $('#msg').html(' <?=Yii::$app->sysLanguage->getTranslateBySymbol('configNowWaiting')?>...');
            }

            $.ajax({
                url: '<?php echo Url::to(['config']);?>'+'&id='+nType,
                type: 'POST',
                dataType: "json",
                data:{'_csrf':_csrf},
                cache: false,
                timeout: 30000,
                success: function(data) {
                    if (nType === 3)
                    {
                        if (data["code"] === 'T')
                        {
                            $('#msg').html('  <a href="<?=$downPath?>sysconfig.data" target="_blank"> <?=Yii::$app->sysLanguage->getTranslateBySymbol('download')?></a>');
                        }
                        else
                        {
                            $('#msg').html('');
                        }
                    }

                    if(data.code === 'T')
                    {
                        art.dialog({icon: 'succeed', content: data.info, time: 1});
                    }
                    else
                    {
                        art.dialog({icon: 'error', content: data.info, time: 1});
                    }
                }
            });
        }
    }

    ;(function ($) {
        $(function (){
            $("#form_id").validationEngine({
                promptPosition:'centerRight: 0, -4',scroll: false , binded: false ,'custom_error_messages': {
                    'required': {
                        'message': '*  <?=Yii::$app->sysLanguage->getTranslateBySymbol('requiredItem')?>！'
                    }
                }
            });

            $('.openWin').delegate('#btn_hfmrpz', 'click', function () {
                $.Layer.confirm({
                    title: ' <?=Yii::$app->sysLanguage->getTranslateBySymbol('systemFriendlyTips')?>',
                    msg:'<span class="red">'+' <?=Yii::$app->sysLanguage->getTranslateBySymbol('recoverDefaultConfigAndRebootSystem')?>？'+'</span>',
                    fn: function () {
                        doClick(1);
                    }
                });
            });

        });
    })(jQuery);
</script>

