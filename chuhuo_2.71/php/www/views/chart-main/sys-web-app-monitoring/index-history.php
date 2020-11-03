<?php
use \yii\helpers\Url;
?>
<style type="text/css">
    .all{min-width: 940px;}
</style>
<div class="all" >
    <form action="" method="post" onsubmit="return false;" id="search">
        <div class="index_search">
            <div class="float_l">
                <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('webSite')?>:</label>
                <select class="text" name="webSize" onchange="initChartData();">
                    <option value=""><?=Yii::$app->sysLanguage->getTranslateBySymbol('all')?></option>
                    <?php foreach($webSize as $item){
                        echo "<option value=\"{$item['sWebSiteName']}\">{$item['sWebSiteName']}</option>";
                    }?>
                </select>
            </div>
            <div class="aearch_box timesel_box float_l">
                <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('selectTime')?>:</label>
                <input type="text" id="startDate" name="startDate" class="text date_plug date_pos validate[required]"  onFocus="var endDate=$dp.$('endDate');WdatePicker({onpicked:function(){endDate.focus();},maxDate:'#F{$dp.$D(\'endDate\')}',dateFmt:'yyyy-MM-dd HH:mm:ss'})" placeholder="开始时间">
                <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('to')?></label><input type="text" id="endDate" name="endDate" class="text date_plug date_pos validate[required]"  onFocus="WdatePicker({minDate:'#F{$dp.$D(\'startDate\')}',dateFmt:'yyyy-MM-dd HH:mm:ss'})"  placeholder="结束时间">
                <input class="btn btn_search" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('query')?>" type="button" onclick="getData();">
            </div>


            <div class="search_box">
                <form action="" method="post">
                    <a type="button" class="btn btn_sea" href="<?=Url::to(['', 'type' => ''])?>"><?=Yii::$app->sysLanguage->getTranslateBySymbol('realTimeMonitoring')?></a>
                </form>
            </div>
        </div>

    </form>
    <iframe src="<?=Url::to(['net-flow', 'type' => 'history'])?>" frameborder="0" width="100%" height="420px;"></iframe>
    <iframe src="<?=Url::to(['concurrency', 'type' => 'history'])?>" frameborder="0" width="100%" height="420px;"></iframe>
    <iframe src="<?=Url::to(['connect', 'type' => 'history'])?>" frameborder="0" width="100%" height="420px;"></iframe>
</div>
<script>
    function getData(init){
        $('iframe').each(function(){
            var obj = $(this)[0];
            var frameWindow = obj.contentWindow;
            if(init){
                obj.onload = function(){
                    //frameWindow.getData();
                };
            } else frameWindow.getData();
        });
    }
    getData(true);
</script>
