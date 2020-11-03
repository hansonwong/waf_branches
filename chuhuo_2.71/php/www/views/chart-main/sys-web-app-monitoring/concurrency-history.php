<?php
use \yii\helpers\Url;
?>
<div class="all" >
    <div class="index_box">
        <h3 class="m_title"><?=Yii::$app->sysLanguage->getTranslateBySymbol('concurrentConnections')?></h3>
        <div class="chart_box">
            <div id="chart_canvas" class="chart"></div>
        </div>
    </div>
</div>

<script>
    var chart = null;
    var date = [], data = [];
    $(function(){
        chart = echarts.init(document.getElementById('chart_canvas'));

        var chartOption = {
            tooltip : {
                trigger: 'axis',
                formatter: function(params) {
                    return params[0].name + '<br/>'
                        + params[0].seriesName + ' : ' + params[0].value + '<?=Yii::$app->sysLanguage->getTranslateBySymbol('kbSeconds')?><br/>';
                    //+ params[1].seriesName + ' : ' + params[1].value + 'KB/秒';
                }
            },
            calculable : true,

            xAxis : [
                {
                    type : 'category',
                    name:'/m',
                    boundaryGap : false,
                    //axisLine: {onZero: false},
                    data : []
                }
            ],
            yAxis : [
                {
                    type : 'value',
                    name:'<?=Yii::$app->sysLanguage->getTranslateBySymbol('kbSeconds')?>'
                }
            ],

            series : [
                {
                    name:'<?=Yii::$app->sysLanguage->getTranslateBySymbol('flow')?>',
                    type:'line',
                    symbolSize: function (value){
                        return Math.round(value[2]/10) + 2;
                    },
                    data:[]
                }
            ]
        };


        // 为echarts对象加载数据
        chart.setOption(chartOption);

        //报表自适应
        window.addEventListener("resize", function () {
            chart.resize();
        });
    });

    function getData(){
        $.ajax({
            url: '<?=Url::to([''])?>',
            type: 'POST',
            data: $.extend(
                {},
                formTransformForObj('#search', window.parent.document),
                {
                    type: 'all',
                    _csrf : $('meta[name=csrf-token]').attr('content')
                }
            ),
            dataType: 'json',
            timeout: 1000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                if(true === data.success){
                    putDataOnce(data.data);
                    setData();
                } else {
                    $.Layer.confirm({
                        title: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('systemFriendlyTips')?>', msg:'<span class=red>' + data.msg + '</span>'
                    });
                }
            },
        });
    }

    function putDataOnce(obj){
        date = obj.date;
        data = obj.data;
    }

    function setData(){
        chart.setOption({
            xAxis: {
                data: date
            },
            series: [{
                name:'<?=Yii::$app->sysLanguage->getTranslateBySymbol('flow')?>',
                data: data
            }]
        });
    }
</script>