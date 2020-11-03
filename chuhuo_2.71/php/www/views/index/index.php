<!DOCTYPE html>
<?php
use \yii\helpers\Url;
use app\widget\AdminList;
$systemInfo = Yii::$app->sysInfo;
$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}assets/waf/";
?>
<html>
<head>
    <?=AdminList::widget(['type' => 'common-css'])?>
    <?=AdminList::widget(['type' => 'common-js'])?>
    <script type="text/javascript" src="<?=$staticResourcePrefix?>js/lib/index.js"></script>
    <script type="text/javascript" src="<?=$staticResourcePrefix?>js/lib/tab.js"></script>
    <script type="text/javascript" src="<?=$staticResourcePrefix?>js/lib/fun.js"></script>

    <script src="<?=$urlPrefix?>assets/js/checkLoginTimeOut.js"></script>
    <title><?=$systemInfo->projectName?></title>
</head>
<body>
<div id="pagewidth">
    <!--header-->
    <div class="header">
        <div class="header_left float_l">
            <!--logo-->
            <img src="<?=$staticResourcePrefix?>skin/blue/images/custom/logo.png">
            <h1 class="header_title"><?=$systemInfo->projectName?></h1>
        </div>
        <!--header-right 告警 主页 用户信息-->
        <div class="float_r header_right">
            <div class="right_menu">
                <ul>
                    <li><?=Yii::$app->sysLanguage->getTranslateBySymbol('welcomeYou')?>！<font><?php //echo $adminInfo->sysUserGroup->group_name;?><!-- : --><?=$adminInfo->name?></font></li>
                    <li class="exit" onClick="checkLoginTimeOut.logout(true);" title="<?=Yii::$app->sysLanguage->getTranslateBySymbol('logout')?>"></li>
                </ul>
            </div>
            <?php echo $this->renderFile('@app/views/index/changeLanguage.php', []); ?>
        </div>
    </div>

    <!--left-->

    <div  class="menu" >
        <ul id="documents">
            <?php
            foreach($menu as $levelOne){
                $str = (0 == $levelOne['display_child']) ? "link='{$levelOne['url']}' target=right" : '';

                echo "<li><a {$str} title='{$levelOne['name']}'><span class='menu_icon {$levelOne['icon_class']}'></span><p>{$levelOne['name']}</p><span class='menu_s menu_small_icon'></span></a>";
                if(1 == $levelOne['display_child']){
                    echo "<ul>";
                    foreach($levelOne['menu'] as $levelTwo){
                        $str = (0 == $levelTwo['display_child']) ? "link='{$levelTwo['url']}' target=right" : '';
                        $strIcon = (1 == $levelTwo['display_child']) ? "<span class='menu_s menu_small_icon'></span>" : '';
                        echo "<li><a {$str} title='{$levelTwo['name']}'><span class='menu_sicon menu_small_icon'></span><p>{$levelTwo['name']}</p>{$strIcon}</a>";

                        if(1 == $levelTwo['display_child']){
                            echo "<ul>";
                            foreach($levelTwo['menu'] as $levelThree){
                                echo "<li><a link='{$levelThree['url']}' target=right title='{$levelThree['name']}'><span class='menu_sicon menu_small_icon'></span><p>{$levelThree['name']}</p></a></li>";
                            }
                            echo "</ul>";
                        }
                        echo "</li>";
                    }
                    echo "</ul>";
                }
                echo "</li>";
            }
            ?>
        </ul>
    </div>

    <!--left hidden-->
    <div class="left_h">
        <div class="l_icon hidden_i"></div>
    </div>
    <!--content-->
    <div class="content">
        <div class="l-tab-links-d">
            <div class="l-tab-links">
                <ul id="tabs">

                </ul>
            </div>
            <div class="t-tab-links">
                <!--<a link="<?php /*echo Url::to(['welcome']);*/?>">系统主页</a> <span> > <b></b></span>-->
            </div>
        </div>
        <div id="content" class="l-tab-content">
            <!--<iframe id="home_content" class="right" name="right" width="100%" height="100%" frameborder="0" scrolling="auto" src="<?php /*echo Url::to(['welcome']);*/?>"></iframe>-->
            <!-- Tab content goes here -->
        </div>

    </div>
    <!--footer-->
    <div class="footer"><?=$systemInfo->copyRight?></div>
</div>
</body>
<script>
    var welcomePageTitle = '<?=Yii::$app->sysLanguage->getTranslateBySymbol('systemHomePage')?>';
    var welcomePageUrl = '<?=Url::to(['sys-status-info/index'])?>';
    var isNeedResetPwd = <?=$isNeedResetPwd ? 'true' : 'false'?>;
    $(function(){
        isResetPwd();
        selectTab(1);
    });
</script>
<?=$this->renderFile('@app/views/index/renderFunction.php', [])?>
<script>checkLoginTimeOut.init("<?=Url::to(['site/check-login-timeout'])?>");</script>
</html>