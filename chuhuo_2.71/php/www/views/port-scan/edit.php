<?php
use \yii\helpers\Url;
?>
<script>
    //提交表单
    function formSubmitForList(){
        $.ajax({
            url: '',
            type: 'POST',
            data: $('#form-admin').serialize(),
            dataType: 'json',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                resetErrorInfo();
                switch(data.success){
                    case true:
                        $.Layer.alert({msg:data.msg});
                        dialog.close();//关闭父层弹框
                        break;
                    case false:
                        errorFieldInfo(data.errorFieldMsg);
                        break;
                    default: $.Layer.alert({msg:data.msg});
                }
            },
        });
    }

    var dialog = null;//父层弹框对象
    function initDialog(){
        var dialog = top.getDialog();
        dialog.DOM.wrap.on('ok', function (e) {
            e.preventDefault();
            formSubmitForList();
        });
        return dialog;
    }
    $(function(){
        dialog = initDialog();
    });
</script>
