<?php
use \yii\helpers\Url;
use \app\logic\sys\SysAuthority;
?>
<script type="text/javascript">
    var userConfig = '<?=$userConfig?>';

    var menuList = [
        {name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('quantitativeStatisticsOfInvasion(month)')?>', url:'<?=Url::to(['get-invade-info-count'])?>'},
        {name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('statisticsOfInvasionCategories(month)')?>', url:'<?=Url::to(['get-invade-info-sort'])?>'},
        //{name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('websiteAccessAnalysis(month)')?>', url:'<?=Url::to(['get-web-visit-info'])?>'},
        //{name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('comprehensiveAnalysis(dayly)')?>', url:'<?=Url::to(['get-comprehensive-analysis-day'])?>'},
        //{name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('comprehensiveAnalysis(monthly)')?>', url:'<?=Url::to(['get-comprehensive-analysis-month'])?>'},
        //{name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('realTimeTraffic')?>', url:'/systemwaf/traffic'},
        {name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('realTimeTraffic')?>', url:'<?=Url::to(['system-traffic'])?>'},
        //{name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('systemResourceOccupation')?>', url:'/systemwaf/use'},
        {name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('systemResourceOccupation')?>', url:'<?=Url::to(['system-use'])?>'},
        {name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('productInfo')?>', url:'<?=Url::to(['get-product-info'])?>'},
    ];

    function menuListDom(){
        var html = '';
        for(var i in menuList){
            var item = menuList[i];
            html += '<span url="' + item.url + '" title="' + item.name + '">' + item.name + '</span>';
        }
        $('.indexTopsTool').prepend(html);
    }

    function menuListDomInitStyle(){
        var userConfigItem = userConfig.split(',');
        var isSetConfig = true;
        if(userConfigItem.length != menuList.length) isSetConfig = false;

        $('.indexTopsTool>span').each(function(index,element){
            var obj = $(this);
            if(isSetConfig) obj.attr('class', (1 == userConfigItem[index]) ? 'on' : 'currr');
            else obj.attr('class', 'currr');
        });
    }

    function menuListConfigSave(){
        var userConfigItem = [];
        $('.indexTopsTool>span').each(function(index,element){
            var obj = $(this);
            userConfigItem.push((obj.hasClass('on')) ? 1 : 0);
        });
        $.ajax({
            url: '<?=Url::to(['user-config-save'])?>',
            type: 'GET',
            data: {
                userConfig	: userConfigItem.join(',')
            },
            dataType: 'json',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                location.reload();
            },//请求成功后执行
        });
    }

    function frameInit(){
        $('.indexTopsTool>span.on').each(function(index){
            var obj = $(this);
            var i = index + 1;
            var floatClass = (0 == i % 2) ? 'r' : 'l';
            $('#frameArea').append('<iframe scrolling=no src="' + obj.attr('url') + '" frameborder="0" width="49.5%;" height="370px;" class="float_' + floatClass + '"></iframe>')
        });
    }


    $(function () {
        menuListDom();menuListDomInitStyle();frameInit();

        $(document).ready(function () {
            $('.indexTops .btn1').click(function () {
                $('.indexTops .indexTopsTool').toggle();
            });
            $('.indexTopsTool span').click(function () {
                if ($(this).hasClass('on')) {
                    $(this).removeClass('on').addClass("currr");
                }
                else {
                    $(this).addClass('on').removeClass("currr");
                }
            });
        });
    });

    function sendSos(){
        $.ajax({
            url: '<?=Url::to(['helper/sos'])?>',
            type: 'GET',
            dataType: "json",
            data:{},
            cache: false,
            timeout: 10000,
            success: function(data){
                if(true === data.success){
                    $.Layer.confirm({
                        title: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('systemFriendlyTips')?>', msg:'<span class=red>' + data.msg + '</span>'
                    });
                }
            }
        });
    }
</script>


<div class="all">
    <!-- 首页功能定制 start-->
    <?php
    $route = 'sys-status-info/user-config-save';
    if(!SysAuthority::singleAuthorityByRoute($route)){?>
        <style>.indexTops{display: none;}</style>
    <?php }?>
    <div class="indexTops">
        <div class="btn1"><?/*=Yii::$app->sysLanguage->getTranslateBySymbol('homePageChartsConfig')*/?></div>
        <div class="btn2" id="postsos" onclick="sendSos();"><?=Yii::$app->sysLanguage->getTranslateBySymbol('technicalSupport')?></div>
        <div class="indexTopsTool" style="display: none;">
            <div class="clear"></div>
            <p><a class="btn" href="javascript:;" onclick="menuListConfigSave();"><?=Yii::$app->sysLanguage->getTranslateBySymbol('done')?></a></p>
        </div>
    </div>
    <!-- 首页功能定制 end-->
    <div id="frameArea"></div>
</div>