<?php

use \yii\helpers\Url;
use yii\helpers\Html;
use yii\widgets\ActiveForm;

$translate = Yii::$app->sysLanguage;
$urlPrefix = Yii::$app->sysPath->resourcePath;
?>
<link href="<?=$urlPrefix?>assets/waf/skin/blue/style/UpdateSys_style.css" rel="stylesheet">
<script src="<?=$urlPrefix?>assets/js/checkLoginTimeOut.js"></script>

<section class="container">
    <input type="hidden" name="pre_name" id="pre_name" value="<?= isset($pre_name) ? $pre_name : '' ?>">
    <input type="" class="radio" name="progress" value="five" id="five">
    <label for="five" class="label" style="color: black">5%</label>

    <input type="" class="radio" name="progress" value="twentyfive" id="twentyfive">
    <label for="twentyfive" class="label" style="color: black">25%</label>

    <input type="" class="radio" name="progress" value="fifty" id="fifty">
    <label for="fifty" class="label" style="color: black">50%</label>

    <input type="" class="radio" name="progress" value="seventyfive" id="seventyfive">
    <label for="seventyfive" class="label" style="color: black">75%</label>

    <input type="" class="radio" name="progress" value="onehundred" id="onehundred">
    <label for="onehundred" class="label" style="color: black">100%</label>
    <div class="progress">
        <div class="progress-bar"></div>
    </div>
    <div id="system_tips" style="text-align:center;margin:5px 0; font:normal 14px/24px 'MicroSoft YaHei';">
        系统升级中,请勿进行任何操作。。。
    </div>
</section>
<script type="text/javascript">
    var _csrf = $('meta[name=csrf-token]').attr('content');
    var t; // 定义定时器
    (function ($) {
        $(document).ready(function () {
            var pre_name = $("#pre_name").val();
            var executeUpdateRst = false;

            //执行更新的操作
            $.ajax({
                url: "<?=Url::to(['config', 'op' => 'executeUpdate']);?>" + '&pre_name=' + pre_name,
                type: 'POST',
                async: false,
                dataType: 'json',
                data: {_csrf: _csrf},
                success: function (data) {
                    if( data['code'] === 'T')
                    {
                        executeUpdateRst = true;
                        return;
                    }

                    $.Layer.alert({msg: data['info'] });
                }
            });

            // 如果执行更新操作成功，就轮询更新状态
            if( executeUpdateRst===true )
            {
                //进度条获取实时状态
                top.logout = 0;
                t = setInterval(function () {
                    getAlert(pre_name);
                }, 3000);
            }
        });
    })(jQuery);

    // 获取升级状态
    function getAlert(pre_name)
    {
        $.ajax({
            url: "<?=Url::to(['config', 'op' => 'getUpdateSysStatus']);?>" + '&pre_name=' + pre_name,
            type: 'POST',
            dataType: 'json',
            data: {_csrf: _csrf},
            success: function (d)
            {
                if( d.code === 'T' )
                {
                    $("input[name=progress]").removeAttr("checked").attr("type", '');

                    //判断是否已经结束
                    if( typeof d.complete === 'string' && d.complete.constructor === String && parseInt(d.state)<1 )
                    {
                        $("input[name=progress]").removeAttr("checked").attr("type", '');

                        $("#system_tips").html('升级失败,即将退出系统,错误信息：' + '<span style="color:red">' + d.complete + '</span>');

                        if (top.logout > 20)
                        {
                            logoutSystem();
                        }
                        top.logout = top.logout + 1;
                    }
                    else if ( d.complete === true )
                    {
                        $("#onehundred").attr("checked", "checked").attr("type", "radio").trigger('click');

                        $("#system_tips").html('升级即将完成,系统即将重启...');
                        if (top.logout > 3) {
                            restartSystem();
                        }
                        top.logout = top.logout + 1;
                    }
                    else
                    {
                        switch (d.state) {
                            case "0":
                                $("#five").attr("checked", "checked").attr("type", "radio").trigger('click');
                                break;
                            case "1":
                                $("#twentyfive").attr("checked", "checked").attr("type", "radio").trigger('click');
                                break;
                            case "2":
                                $("#fifty").attr("checked", "checked").attr("type", "radio").trigger('click');
                                break;
                            case "3":
                                $("#seventyfive").attr("checked", "checked").attr("type", "radio").trigger('click');
                                break;
                            case "4":
                                $("#onehundred").attr("checked", "checked").attr("type", "radio").trigger('click');

                                $("#system_tips").html('升级即将完成,系统即将重启...');
                                if( top.logout > 3 && d.complete === true)
                                {
                                    restartSystem();
                                }
                                top.logout = top.logout + 1;
                                break;
                        }
                    }
                }
                else
                {
                    //如果一直失败 强制退出系统
                    top.logout = top.logout + 1;
                    if ( top.logout > 100 )
                    {
                        $("input[name=progress]").removeAttr("checked").attr("type", '');
                        $("#system_tips").html('升级失败,即将退出系统');
                        logoutSystem();
                    }
                }
            }
        });
    }

    // 退出系统
    function restartSystem()
    {
        clearInterval(t);

        t = setInterval(function () {
            $.ajax({
                url: "<?=Url::to(['config', 'op' => 'restartSystem']);?>",
                type: 'POST',
                dataType: 'json',
                data: {_csrf: _csrf, sAction: 'migrate'},
                success: function (d) {
                    if( d.code === 'T' )
                    {
                        // 检查系统是否已重启成功
                        sysStatus();
                    }
                }
                });
        }, 3000);
    }

    // 检测系统是否已重启完成
    function sysStatus() {
        clearInterval(t);

        setTimeout( function(){
            // 睡眠5秒
        }, 8000 );//延迟

        t = setInterval(function () {
            $.ajax({
                url: "<?=Url::to(['config', 'op' => 'sysStatus']);?>",
                type: 'GET',
                dataType: 'json',
                data: {_csrf: _csrf},
                success: function (d) {
                    if( d.code === 'T' )
                    {
                        logoutSystem();
                    }
                }
            });
        }, 3000);
    }

    // 退出登陆
    function logoutSystem()
    {
        clearInterval(t);

        checkLoginTimeOut.logoutUrl = ['/Site/LogoutSys', '<?=Url::to(['logout'])?>'];
        checkLoginTimeOut.logout(true);
    }
</script>
