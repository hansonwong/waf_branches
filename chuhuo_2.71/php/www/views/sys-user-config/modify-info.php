<!DOCTYPE HTML>
<html>
<head>
<?php
use app\widget\AdminList;
$urlPrefix = Yii::$app->sysPath->resourcePath;
?>
<?=AdminList::widget(['type' => 'common-css'])?>
<?=AdminList::widget(['type' => 'common-js'])?>
</head>
<body>

<div class="openWin">
    <form id="configForm" onsubmit="return false;">
        <input type="hidden" name="_csrf"/>
        <div class="jbxx sj">
            <table width="80%" border="0" cellspacing="0" cellpadding="0" class="date_add_table">
                <tr>
                    <td width="160" class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('oldPwd')?>:</td>
                    <td>
                        <input type="password" class="text" id="pwd" name="pwd">
                    </td>
                </tr>

                <tr>
                    <td class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('newPwd')?>:</td>
                    <td>
                        <input type="password" class="text" name="pwdN[]">
                    </td>
                </tr>

                <tr>
                    <td class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('newPwdConfirm')?>:</td>
                    <td>
                        <input type="password" class="text" name="pwdN[]">
                    </td>
                </tr>

                <tr>
                    <td>&nbsp;</td>
                    <td>
                        <input type="submit" class="btn_ty" onclick="formSubmit();" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('done')?>" />
                    </td>
                </tr>
            </table>
        </div>
    </form>
</div>

<script>
$(function(){
	$('[name=_csrf]').val($('meta[name=csrf-token]').attr('content'));
});

function formSubmit(){
	$.ajax({
		url: '',
		type: 'POST',
		data: $('#configForm').serialize(),
		dataType: 'json',
		timeout: 10000,//1000毫秒后超时
		cache: false,//不缓存数据
		async: false,//同步：false,异步：true,默认true
		success: function(data){
			if(true === data.success) location.reload();
			else $.Layer.alert({msg:data.msg});
		},
	});
}
</script>
</body>
</html>