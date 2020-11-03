<!DOCTYPE HTML>
<html>
<head>
<?php use app\widget\AdminList;
$urlPrefix = Yii::$app->sysPath->resourcePath;?>
<?=AdminList::widget(['type' => 'common-css'])?>
<?=AdminList::widget(['type' => 'common-js'])?>
<!--<script src="/assets/js/stickUp.min.js"></script>-->
<script src="<?=$urlPrefix?>assets/js/vue/vue.js"></script>
<style>html{overflow-y:auto;}</style>
</head>
<body style="display: none">
<?=AdminList::widget(['type' => 'list&config-edit', 'config' => ['model' => $model]])?>
<script>
var dialog = null;//父层弹框对象
function initDialog(){
    try{
        var dialog = top.getDialog();
        dialog.DOM.wrap.on('ok', function (e) {
            e.preventDefault();
            formSubmit();
        });
        return dialog;
    } catch (e){return null;}
}

//提交成功后处理
function submitSuccess(data){
    resetErrorInfo();
    switch(data.success){
        case true:
            if(dialog.hGrid) dialog.hGrid.reload();//刷新父层表单数据
            dialog.close();//关闭父层弹框
            break;
        case false:
            errorFieldInfo(data.errorFieldMsg);
            break;
        default: $.Layer.alert({msg:data.msg});
    }
}

$(function(){
    $('#submitArea').css('display', 'none');
    dialog = initDialog();
});
</script>
<?php if($allowUpdate){}
if(isset($custom['custom'])) echo $custom['custom'];?>
</body>
</html>