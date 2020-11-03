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
<body style="display: none;">
<?=AdminList::widget(['type' => 'list&config-edit', 'config' => ['model' => $model]])?>
<?php if($allowUpdate):?>
<script>
//提交成功后处理
function submitSuccess(data){
    resetErrorInfo();
    switch(data.success){
        case true:
            $.Layer.alert({msg:data.msg});
            break;
        case false:
            errorFieldInfo(data.errorFieldMsg);
            break;
        default: $.Layer.alert({msg:data.msg});
    }
}
</script>
<?php endif;
if(isset($custom['custom'])) echo $custom['custom'];?>
<script>
    $(function(){

    });
</script>
</body>
</html>