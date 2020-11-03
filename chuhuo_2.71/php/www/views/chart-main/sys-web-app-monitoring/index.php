<?php
use \yii\helpers\Url;
?>
<style type="text/css">
    .all{min-width: 940px;}
</style>
<div class="all">
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
            <div class="search_box">
                <form action="" method="post">
                    <a type="button" class="btn btn_sea" href="<?=Url::to(['', 'type' => 'history'])?>"><?=Yii::$app->sysLanguage->getTranslateBySymbol('historicalDataQuery')?></a>
                </form>
            </div>
        </div>
    </form>

    <iframe src="<?=Url::to(['net-flow', 'type' => ''])?>" frameborder="0" width="100%" height="420px;"></iframe>
    <iframe src="<?=Url::to(['concurrency', 'type' => ''])?>" frameborder="0" width="100%" height="420px;"></iframe>
    <iframe src="<?=Url::to(['connect', 'type' => ''])?>" frameborder="0" width="100%" height="420px;"></iframe>
</div>
