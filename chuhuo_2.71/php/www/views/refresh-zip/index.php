<?php
use \yii\helpers\Url;
use yii\helpers\Html;
$translate = Yii::$app->sysLanguage;
$downloadPath = Yii::$app->sysPath->downloadPath;
$downPath = $downloadPath['downPath'];
?>
<div class="openWin" >
<form action="" method="post" id="form_id">
  <h1><?=$translate->getTranslateBySymbol('meetEmergenciesSupport')?></h1>
  <div class="jbxx sj">
    <table width="80%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
      <tr>
        <td ><?=$translate->getTranslateBySymbol('supportPackageTips')?></td>
      </tr>                
      <tr>        
        <td ><?=$translate->getTranslateBySymbol('supportPackageDownloadTips')?></td>
      </tr>                
      <tr>        
        <td >
            <div style="width:100%;  text-indent:50px; vertical-align:middle;"><span id="msg" class="red" ></span></div>
        	<input id="subcss" name="button" type="button" onclick="return doSubmit(0);" class="btn_ty" value="<?=$translate->getTranslateBySymbol('supportPackageCreate')?>" />
        </td>
      </tr>          
     </table>
  </div>
</form>
</div>

<script type="text/javascript">
    function doSubmit()
    {
        $('#msg').html('<?=$translate->getTranslateBySymbol('supportPackageCreateWaitingTips')?>...');
        var _csrf = $('meta[name=csrf-token]').attr('content');
        $.ajax({
            url: '<?php echo Url::to(['config']);?>'+'&id=1',
            type: 'POST',
            dataType: "json",
            data:{'_csrf':_csrf},
            cache: false,
            timeout: 30000,
            success: function(data){
                    $('#msg').html('<a href="<?=$downPath?>/sysinfo.data"  class="red"> <?=$translate->getTranslateBySymbol('download')?></a>');
                $("#subcss").hide();
            }
        });
    }
</script>

