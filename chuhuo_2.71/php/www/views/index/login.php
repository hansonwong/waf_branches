<!DOCTYPE html>
<?php
use \yii\helpers\Url;
use app\widget\AdminList;
use yii\captcha\Captcha;
$systemInfo = Yii::$app->sysInfo;
$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}assets/waf/";
?>
<html>
<head>
    <title><?=Yii::$app->sysLanguage->getTranslateBySymbol('login').
        ' - '. $systemInfo->projectName?></title>
    <?=AdminList::widget(['type' => 'common-css'])?>

    <!--<script src="<?/*=$urlPrefix*/?>assets/js/translation.js"></script>-->
    <script src="<?=Url::to(['language/lang-source-for-js', 'tpl' => 't'])?>"  type="text/javascript"></script>

    <?=AdminList::widget(['type' => 'common-js'])?>
    <!--[if lte ie 9]>
    <script src="<?php echo $staticResourcePrefix;?>js/lib/jquery.JPlaceholder.js"></script>
    <![endif]-->

    <script src="<?=$urlPrefix?>assets/js/pwd.js"></script>

    <script src="<?=$urlPrefix?>assets/js/checkLoginTimeOut.js"></script>
    <?php echo $this->renderFile('@app/views/index/renderFunction.php', []); ?>
</head>

<body class="log" style="height: 3000px;">
<div class="login">
    <?php echo $this->renderFile('@app/views/index/changeLanguage.php', []); ?>
    <!--<div class="logoimg"></div>-->
    <div class="loginhd clearfix">
        <img class="logo" src="<?=$staticResourcePrefix?>skin/blue/images/custom/logo.png" alt="logo" />
        <h1 class="login_title"><?=$systemInfo->projectName?></h1>
    </div>
    <div class="logomin"></div>
    <div class="login_nr">
        <div class="logo_b"><div class="img"></div></div>
        <div class="login_text">
            <form method="post" action="/" id="login" onsubmit="login();return false;"/>
            <input type="hidden" name="_csrf" value=""/>
            <input type="hidden" name="pwd" value=""/>
            <p><input type="text" class="log_name" name="name" placeholder="<?php echo Yii::$app->sysLanguage->getTranslateBySymbol('userName');?>" /></p>
            <p><input type="password" class="log_pwd" id="pwd" placeholder="<?php echo Yii::$app->sysLanguage->getTranslateBySymbol('password');?>" autocomplete="new-password"/></p>
            <p>
                <input type="text" class="log_yzm" name="cap" placeholder="<?php echo Yii::$app->sysLanguage->getTranslateBySymbol('verificationCode');?>"  />
                <?=Captcha::widget(['name'=>'captchaimg','captchaAction'=>'index/captcha','imageOptions'=>['id'=>'captchaimg', 'title'=> Yii::$app->sysLanguage->getTranslateBySymbol('replacePic'), 'alt' => Yii::$app->sysLanguage->getTranslateBySymbol('replacePic'), 'style'=>'cursor:pointer;', 'onclick' => 'refreshCaptcha();'],'template'=>'{image}'])?>
            </p>
            <p>
                <input type="submit" class="log_btn" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('login')?>" />
                <span style="display:none;" id="logininfo"></span>
            </p>
            </form>
        </div>
    </div>
    <p class="banquan"><?=$systemInfo->copyRight?></p>
</div>
</body>
<script>
    $(function(){
        //translation.init('<?=Url::to(['language/lang-source-for-js'])?>');
        clear_cookie();//清除cookie
        checkLoginTimeOut.logout(false);
        refreshCaptcha();
    });
    function refreshCaptcha(){
        $.ajax({
            url: '<?=Url::to(['captcha'])?>&refresh='+Math.random(),
            type: 'POST',
            data: {},
            dataType: 'json',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                $('#captchaimg').attr('src', data.url);
            },
        });
    }
    function login(){
        $('[name="pwd"]').val(authcode(
            $('#pwd').val(), 'ENCODE'
        ));
        $('[name=_csrf]').val($('meta[name=csrf-token]').attr('content'));
        $.ajax({
            url: '<?=Url::to(['login-check'])?>',
            type: 'POST',
            data: $('#login').serialize(),
            dataType: 'json',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                switch(data.success){
                    case true:
                        if(loginCheck(data.data.verify)) window.location.href = '/';
                        else checkLoginTimeOut.logout(false);
                        break;
                    case false:
                        $('#pwd').val('');
                        $('[name="cap"]').val('');
                        refreshCaptcha();
                        alert(data.msg);
                        break;
                    default:;
                }
            },
        });
    }
    function loginCheck(verify){
        var enable = <?=$enableFirewall ? 'true' : 'false'?>;
        if(!enable) return true;

        var sym = false;
        $.ajax({
            url: '/Site/LoginSystemWaf',
            type: 'POST',
            data: verify,
            dataType: 'json',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                switch(data.code){
                    case 'T':
                        sym = true;
                        break;
                    case 'F':
                        alert(data.info);
                        sym = false;
                        break;
                }
            },
        });
        return sym;
    }
</script>
</html>
