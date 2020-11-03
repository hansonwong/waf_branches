<?php
use \yii\helpers\Url;
?>
<div>
    <div class="index_box"  style="width:99.5%">
        <h3 class="m_title"><?=Yii::$app->sysLanguage->getTranslateBySymbol('comprehensiveAnalysis(dayly)')?></h3>
        <div class="chart_box">
            <div id="chart_canvas" class="chart"></div>
        </div>
    </div>
</div>

<script>
    $(function(){
        getData();
    });

    function getData(){
        $.ajax({
            url: '<?=Url::to([''])?>',
            type: 'POST',
            data: {
                    _csrf : $('meta[name=csrf-token]').attr('content')
                },
            dataType: 'json',
            timeout: 20000,//1000毫秒后超时
            cache: false,//不缓存数据
            //async: false,//同步：false,异步：true,默认true
            success: function(data){
                setData(data.data);
            },
        });
    }

    function setData(data){
        chart = echarts.init(document.getElementById('chart_canvas'));
        chart.showLoading({
            text: '',
            effect: 'whirling',
        });

        var legend = [];
        for(var i in data.data){
            var item = data.data[i];
            item.type = 'line';
            legend.push(item.name);
        }

        var chartOption = {
            // 默认色板
            color: [
                '#2ec7c9','#b6a2de','#5ab1ef','#ffb980','#d87a80',
                '#8d98b3','#e5cf0d','#97b552','#95706d','#dc69aa',
                '#07a2a4','#9a7fd1','#588dd5','#f5994e','#c05050',
                '#59678c','#c9ab00','#7eb00a','#6f5553','#c14089'
            ],
            title: {
                show: false,
                text: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('comprehensiveAnalysis(dayly)')?>'
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: legend
            },
            grid: {
                left: '3%',
                right: '8%',
                bottom: '3%',
                containLabel: true
            },
            /*toolbox: {
                feature: {
                    saveAsImage: {}
                }
            },*/
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: data.date
            },
            yAxis: {
                type: 'value'
            },
            series: data.data
        };


        // 为echarts对象加载数据
        chart.setOption(chartOption);
        chart.hideLoading();
    }
</script>