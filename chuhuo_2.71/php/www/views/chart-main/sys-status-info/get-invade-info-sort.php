<?php
use \yii\helpers\Url;
?>
<div>
    <div class="index_box"  style="width:99.5%">
        <h3 class="m_title"><?=Yii::$app->sysLanguage->getTranslateBySymbol('statisticsOfInvasionCategories(month)')?></h3>
        <div class="chart_box">
            <div id="chart_canvas" class="chart"></div>
        </div>
    </div>
</div>

<script>
    $(function(){
        chart = echarts.init(document.getElementById('chart_canvas'));
        chart.showLoading({
            text: '',
            effect: 'whirling',
        });

        setTimeout(getData, 2000);
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


        var chartOption = option = {
            // 默认色板
            color: [
                '#2ec7c9','#b6a2de','#5ab1ef','#ffb980','#d87a80',
                '#8d98b3','#e5cf0d','#97b552','#95706d','#dc69aa',
                '#07a2a4','#9a7fd1','#588dd5','#f5994e','#c05050',
                '#59678c','#c9ab00','#7eb00a','#6f5553','#c14089'
            ],
            title: {
                show: false,
                text: '<?=Yii::$app->sysLanguage->getTranslateBySymbol('statisticsOfInvasionCategories(month)')?>'
            },
            //color: ['#3398DB'],
            tooltip : {
                trigger: 'axis',
                axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                    type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            grid: {
                top:'5%',
                left: '3%',
                right: '4%',
                bottom: 60,
                containLabel: true
            },
            xAxis : [
                {
                    type : 'category',
                    data : data.name,
                    axisTick: {
                        alignWithLabel: true
                    },
                    axisLabel: {
                        interval:0,
                        rotate:45,
                        textStyle:{
                            fontSize:12,
                            //color:'#ccc'
                        }
                    }

                }
            ],
            yAxis : [
                {
                    type : 'value'
                }
            ],
            series : [
                {
                    name:'<?=Yii::$app->sysLanguage->getTranslateBySymbol('statisticsOfInvasionCategories(month)')?>',
                    type:'bar',
                    barWidth: '60%',
                    itemStyle: {
                        normal: {
                            color: function(params) {
                                // build a color map as your need.
                                var colorList = [
                                    '#2ec7c9','#b6a2de','#5ab1ef','#ffb980','#d87a80',
                                    '#8d98b3','#e5cf0d','#97b552','#95706d','#dc69aa',
                                    '#07a2a4','#9a7fd1','#588dd5','#f5994e','#c05050',
                                    '#59678c','#c9ab00','#7eb00a','#6f5553','#c14089'
                                ];
                                return colorList[params.dataIndex]
                            },
                            //label : {show: true, position: 'right'}
                        }
                    },
                    data: data.val,
                }
            ]
        };


        // 为echarts对象加载数据
        chart.setOption(chartOption);
        chart.hideLoading();
    }
</script>