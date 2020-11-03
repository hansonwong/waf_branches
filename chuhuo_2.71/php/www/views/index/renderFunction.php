<?php
use \yii\helpers\Url;
?>
<script>
checkLoginTimeOut.logoutUrl = ['/Site/LogoutSys', '<?=Url::to(['logout'])?>'];
//判断是否要修改密码
function isResetPwd(){
    if(isNeedResetPwd){
        $.Layer.iframe(
            {
                title: top.translation.t('modifyPwd'),
                url: '<?=Url::to(['sys-user-for-role/change-self-pwd'])?>',
                width: 500,
                height: 300,
            });
    }
}
</script>
