<?php
use \yii\helpers\Url;
?>
<div class="all" >
    <div class="index_box">
        <h3 class="m_title"><?=Yii::$app->sysLanguage->getTranslateBySymbol('newConnectCountAndFairCount')?></h3>
        <div class="chart_box">
            <div id="chart_canvas" class="chart"></div>
        </div>
    </div>
</div>

<script>
    var chart = null;
    var date = [],iNewConnections = [],iTransactions = [];
    var offset = 0;
    $(function(){
        chart = echarts.init(document.getElementById('chart_canvas'));

        var chartOption = {
            tooltip : {
                trigger: 'axis',
                formatter: function(params) {
                    return params[0].name + '<br/>'
                        + params[0].seriesName + ' : ' + params[0].value + '<?=Yii::$app->sysLanguage->getTranslateBySymbol('kbSeconds')?><br/>'
                        + params[1].seriesName + ' : ' + params[1].value + '<?=Yii::$app->sysLanguage->getTranslateBySymbol('kbSeconds')?>';
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
                    name:'<?=Yii::$app->sysLanguage->getTranslateBySymbol('connectCount')?>',
                    type:'line',
                    symbolSize: function (value){
                        return Math.round(value[2]/10) + 2;
                    },
                    data:[]
                },
                {
                    name:'<?=Yii::$app->sysLanguage->getTranslateBySymbol('fairCount')?>',
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

        getData();
    });

    function getData(){
        $.ajax({
            url: '<?=Url::to([''])?>',
            type: 'POST',
            data: $.extend(
                    {},
                formTransformForObj('#search', window.parent.document),
                    {
                        type: 'single',
                        offset: offset,
                        _csrf : $('meta[name=csrf-token]').attr('content')
                    }
                ),
            dataType: 'json',
            timeout: 1000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                if(true === data.success){
                    putData(data.data);
                    setData();
                    offset++;
                }

                setTimeout('getData()', 1000);
            },//请求成功后执行
            error:function(data){
                setTimeout('getData()', 1000);
            }
        });
    }

    function putData(obj){
        date.push(obj.date);
        iNewConnections.push(obj.iNewConnections);
        iTransactions.push(obj.iTransactions);
        if (date.length > 100) {
            date.shift();
            iNewConnections.shift();
            iTransactions.shift();
        }
    }

    function initChartData(){
        offset = 0;
        date = iNewConnections = iTransactions = [];
        setData();
    }

    function setData(){
        chart.setOption({
            xAxis: {
                data: date
            },
            series: [
                {
                    name:'<?=Yii::$app->sysLanguage->getTranslateBySymbol('connectCount')?>',
                    data: iNewConnections
                },
                {
                    name:'<?=Yii::$app->sysLanguage->getTranslateBySymbol('fairCount')?>',
                    data: iTransactions
                }
            ]
        });
    }
</script>