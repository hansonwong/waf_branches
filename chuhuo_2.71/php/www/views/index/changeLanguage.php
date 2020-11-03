<?php
use \yii\helpers\Url;?>
<!-- 语言选择框 start-->
<div class="index_langersel_wrap">
    <div class="select_box">
        <div class="select_inner" style="cursor: pointer;">
            <span class="select_name SelNameRef">中文</span>
            <span class="select_icon SelIconRef"></span>
        </div>
        <div class="select_option SelOptionRef" style="display:none">
            <ul></ul>
        </div>
    </div>
</div>
<!-- 语言选择框 end-->
<script>
<?php
$sysLanguage = Yii::$app->sysLanguage->getLanguage();
$languageList = Yii::$app->sysLanguage->getList();
foreach ($languageList as $k => $v){
    unset($languageList[$k]['model']);
}
$languageList = json_encode($languageList);?>
//系统语言插件
var systemLanguageToggle = {
    sysLanguage: '<?=$sysLanguage?>',
    languageList: <?=$languageList?>,
    //设置语言初始化
    initLanguage: function(){
        this.toggleLanguage(this.sysLanguage, false);
    },
    //设置语言切换绑定
    initToggleButton: function(){
        var languageList = this.languageList
        for(var item in languageList){
            var obj = languageList[item];
            $(".SelOptionRef ul").append('<li lang="' + item + '">' + obj.name + '</li>');
        }

        $(".SelNameRef").html(languageList[this.sysLanguage]['name']);

        //语言选择框点击选中效果
        $(".SelIconRef,.SelNameRef").click(function(){
            $(".SelOptionRef").toggle();
        });

        $(".SelOptionRef ul li").click(function(){
            var obj = $(this);
            $(this).parent().parent().toggle();
            $(".SelNameRef").html(obj.text());

            systemLanguageToggle.toggleLanguage(obj.attr('lang'), true);
        });
    },
    toggleLanguage: function(lang, single){
        var langObj = this.languageList[lang];
        $.ajax({
            langConfig: {
                single: single,
                lang: lang,
            },
            url: langObj.firewallUrl,
            type: 'GET',
            data: {},
            dataType: 'text',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false
            success: function(data){
                if(this.langConfig.single) top.location.href = '<?=Url::to([Yii::$app->sysPath->routePass['language-set']])?>&lang=' + this.langConfig.lang;
            },
            error: function(data){
                if(this.langConfig.single) top.location.href = '<?=Url::to([Yii::$app->sysPath->routePass['language-set']])?>&lang=' + this.langConfig.lang;
            },
        });
    },
};

$(function(){
    systemLanguageToggle.initLanguage();
    systemLanguageToggle.initToggleButton();
});
</script>