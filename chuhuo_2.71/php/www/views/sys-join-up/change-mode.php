<?php use \yii\helpers\Url;?>
<div class="openWin">
    <form action="" method="post" id="change-mode">
        <h1><?=Yii::$app->sysLanguage->getTranslateBySymbol('sysJoinUpControlConfigSwitch')?></h1>
        <div class="jbxx sj">
            <table width="80%" border="0" cellspacing="0" cellpadding="0" class="date_add_table">
                <tr>
                    <td width="120" class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('sysJoinUpControlConfigSwitch')?>: </td>
                    <td>
                        <input type="button" class="qt mt0">
                        <font color="red">(<?=Yii::$app->sysLanguage->getTranslateBySymbol('sysJoinUpControlConfigSwitchTips')?>)</font>
                    </td>
                </tr>
                <tr id="selIPSetting" style="display:none;">
                    <td width="120" class="t_r"><?=Yii::$app->sysLanguage->getTranslateBySymbol('mode')?>: </td>
                    <td>
                        <label style="display: none;"><input type="radio" name="mode" value="Off"></label>
                        <label><input name="mode" type="radio" value="white" onclick="submitChangeMode();"/>&nbsp;<?=Yii::$app->sysLanguage->getTranslateBySymbol('whiteList')?></label>
                        <label><input name="mode" type="radio" value="black" onclick="submitChangeMode();"/>&nbsp;<?=Yii::$app->sysLanguage->getTranslateBySymbol('blackList')?></label>
                    </td>
                </tr>
            </table>
        </div>
    </form>
</div>
<script>
    var modeSwitch = '<?=$config['blackAndWhite']?>';
    var modeSwitchTitleOpen = '<?=Yii::$app->sysLanguage->getTranslateBySymbol('enable')?>';
    var modeSwitchTitleClose = '<?=Yii::$app->sysLanguage->getTranslateBySymbol('close')?>';
    $(function(){
        $("input[name=mode][value='" + modeSwitch + "']").prop('checked', true);

        // 列表操作懒启用、停用
        $('.openWin').on('click', '.qt', function(event) {
            if($(this).hasClass('bt_qyan')){
                $(this).addClass('bt_tyan').removeClass('bt_qyan');
                $(this).attr('title', modeSwitchTitleClose);
                $('#selIPSetting').hide();
                $("input[name=mode][value='Off']").prop('checked', true);
                submitChangeMode();
            }else{
                $(this).addClass('bt_qyan').removeClass('bt_tyan');
                $(this).attr('title', modeSwitchTitleOpen);
                $('#selIPSetting').show();
                $("input[name=mode][value=Off]").prop('checked', false);
            }
        });
        initForm();
    });
    //初始化表单
    function initForm(){
        var obj = $('.qt');
        obj.attr('title', ('Off' == modeSwitch) ? modeSwitchTitleClose : modeSwitchTitleOpen);
        if('Off' == modeSwitch){
            obj.addClass('bt_tyan').removeClass('bt_qyan');
            $('#selIPSetting').hide();
        } else {
            obj.addClass('bt_qyan').removeClass('bt_tyan');
            $('#selIPSetting').show();
        }
    }
    function submitChangeMode(){
        $.ajax({
            url: '<?=Url::to(['change-mode'])?>',
            type: 'GET',
            data: $('#change-mode').serialize(),
            dataType: 'json',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                $.Layer.alert({msg:data.msg});
            },
        });
    }
</script>
