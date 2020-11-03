<?php
use \yii\helpers\Url;
use app\widget\AdminList;
$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}assets/waf/";
?>
<!DOCTYPE HTML>
<html>
<head>
    <?=AdminList::widget(['type' => 'common-css'])?>
    <?=AdminList::widget(['type' => 'common-js'])?>
    <script type="text/javascript" src="<?=$staticResourcePrefix?>js/lib/index.js"></script>
</head>
<body>

<!-- report 系统资源占用 -->
<div class="index_box" style="width:99.5%;height:356px;">
    <h3 class="m_title"><?=Yii::$app->sysLanguage->getTranslateBySymbol('systemResourceOccupation')?></h3>
    <div class="chart_box_w3">
        <div id="chart_nc" class="chart"></div>
        <h5 class="chart_tit"><b><?=Yii::$app->sysLanguage->getTranslateBySymbol('RAM')?></b></h5>
    </div>
    <div class="chart_box_w3">
        <div id="chart_cpu" class="chart"></div>
        <h5 class="chart_tit"><b>CPU</b></h5>
    </div>
    <div class="chart_box_w3">
        <div id="chart_cp" class="chart"></div>
        <h5 class="chart_tit"><b><?=Yii::$app->sysLanguage->getTranslateBySymbol('disk')?></b></h5>
    </div>
    <div class="clearfix"></div>
</div>



<!--报表-->
<!--<script src="<?/*=$staticResourcePrefix*/?>js/lib/echarts/echarts.js"></script>-->
<script src="<?=$urlPrefix?>assets/js/echarts/echarts.min.js"></script>
<script>
    var myChart_cpu, myChart_nc, myChart_cp;
    var option_cpu, option_nc, option_cp;
    $(function(){

        myChart_cpu = echarts.init(document.getElementById('chart_cpu'));
        myChart_nc = echarts.init(document.getElementById('chart_nc'));
        myChart_cp = echarts.init(document.getElementById('chart_cp'));


//CPU
        option_cpu = {
            tooltip : {
                formatter: "{a} <br/>{b} : {c}%"
            },
            series : [
                {
                    name:'CPU利用率',
                    type:'gauge',
                    radius: '100%',
                    center : ['50%', '70%'],
                    axisLine: {            // 坐标轴线
                        lineStyle: {       // 属性lineStyle控制线条样式
                            color: [[0.2, '#228b22'],[0.8, '#48b'],[1, '#ff4500']],
                            width: 10
                        }
                    },
                    axisLabel: {            // 坐标轴小标记
                        show: true,
                        formatter: null,
                        textStyle: {
                            color: 'auto',
                            fontFamily:'Arial'

                        }
                    },
                    axisTick: {            // 坐标轴小标记
                        show: true,
                        splitNumber: 5,
                        length :3,
                        lineStyle: {
                            color: '#ececec',
                            width: 1,
                            type: 'solid'
                        }
                    },
                    splitLine: {           // 分隔线
                        show: true,
                        length :7,
                        lineStyle: {
                            color: '#ececec',
                            width: 1,
                            type: 'solid'
                        }
                    },
                    pointer: {           // 分隔线
                        length : '75%',
                        width : 4,
                        color : 'auto'
                    },
                    title : {
                        show : true,
                        offsetCenter: [0, '-30%'],
                        textStyle: {
                            color: '#999'
                        }
                    },
                    detail : {
                        formatter:'{value}%',
                        textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                            color: 'auto',
                            fontSize:16
                        }
                    },
                    data:[{value: 30, name: 'CPU'}]
                }
            ]
        };

//内存
        option_nc = {
            tooltip : {
                formatter: "{a} <br/>{b} : {c}%"
            },

            series : [
                {
                    name:'内存利用率',
                    type:'gauge',
                    radius: '90%',
                    center : ['50%', '70%'],
                    detail : {formatter:'{value}%'},
                    data:[{value: 50, name: top.translation.t('RAM')}],
                    axisLine:{show: true,
                        lineStyle: {
                            color: [
                                [0.2, '#228b22'],
                                [0.8, '#48b'],
                                [1, '#ff4500']
                            ],
                            width: 10
                        }
                    },
                    axisTick :{
                        show: true,
                        splitNumber: 5,
                        length :3,
                        lineStyle: {
                            color: '#ececec',
                            width: 1,
                            type: 'solid'
                        }
                    } ,
                    axisLabel :{
                        show: true,
                        formatter: null,
                        textStyle: {
                            color: 'auto',
                            fontFamily:'Arial'

                        }
                    },
                    splitLine:{
                        show: true,
                        length :7,
                        lineStyle: {
                            color: '#ececec',
                            width: 1,
                            type: 'solid'
                        }

                    },
                    pointer :{
                        length : '75%',
                        width : 4,
                        color : 'auto'


                    },
                    title :{
                        show : true,
                        offsetCenter: [0, '-30%'],
                        textStyle: {
                            color: '#999'
                        }
                    },
                    detail : {
                        formatter:'{value}%',
                        textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                            color: 'auto',
                            fontSize:16
                        }
                    }
                }
            ]
        };
//磁盘
        option_cp = {
            tooltip : {
                formatter: "{a} <br/>{b} : {c}%"
            },

            series : [
                {
                    name:'磁盘',
                    type:'gauge',
                    radius: '90%',
                    center : ['50%', '70%'],
                    detail : {formatter:'{value}%'},
                    data:[{value: 50, name: top.translation.t('disk')}],
                    axisLine:{show: true,
                        lineStyle: {
                            color: [
                                [0.2, '#228b22'],
                                [0.8, '#48b'],
                                [1, '#ff4500']
                            ],
                            width: 10
                        },
                    },
                    axisTick :{
                        show: true,
                        splitNumber: 5,
                        length :3,
                        lineStyle: {
                            color: '#ececec',
                            width: 1,
                            type: 'solid'
                        }
                    } ,
                    axisLabel :{
                        show: true,
                        formatter: null,
                        textStyle: {
                            color: 'auto',
                            fontFamily:'Arial',

                        }
                    },
                    splitLine:{
                        show: true,
                        length :7,
                        lineStyle: {
                            color: '#ececec',
                            width: 1,
                            type: 'solid'
                        }

                    },
                    pointer :{
                        length : '75%',
                        width : 4,
                        color : 'auto'


                    },
                    title :{
                        show : true,
                        offsetCenter: [0, '-30%'],
                        textStyle: {
                            color: '#999',
                        }
                    },
                    detail : {
                        formatter:'{value}%',
                        textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                            color: 'auto',
                            fontSize:16
                        }
                    },
                }
            ]
        };
        setInterval(getData, 1000);
    });

    function getData(){
        $.ajax({
            url: '/System/Sysresource',
            type: 'POST',
            data: {},
            dataType: 'json',
            timeout: 5000,
            cache: false,//不缓存数据
            async: true,//同步：false,异步：true,默认true
            success: function(data){
                option_cpu.series[0].data[0].value = data.cpu.all;
                myChart_cpu.setOption(option_cpu, true);

                option_nc.series[0].data[0].value = data.mem;
                myChart_nc.setOption(option_nc, true);

                option_cp.series[0].data[0].value = data.disk;
                myChart_cp.setOption(option_cp, true);
            },
        });
    }
</script>
</body>
</html>
