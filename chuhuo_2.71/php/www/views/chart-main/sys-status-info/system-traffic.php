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
<style>
    .report_search {
        float: left;
        position: absolute;
        z-index: 9;
        width: 200px;
        padding: 10px 0px 0px 20px;
    }
    .report_search label {
        float: left;
        line-height: 24px;
        padding: 0px 5px 0px 10px;
    }
    .line_icon {
        padding: 10px 20px 0px 10px;
    }
    .line_icon img {
        padding: 10px 5px 0px 0px;
    }
    .line_icon span {
        padding: 5px;
    }
</style>
<body>

<!-- report 系统资源占用 -->
<div class="index_box" style="width:99.5%;height:356px;">
    <h3 class="m_title"><?=Yii::$app->sysLanguage->getTranslateBySymbol('realTimeTraffic')?></h3>
    <div class="chart_box hauto" >
        <div class="float_r line_icon">
            <img src="<?=$staticResourcePrefix?>skin/blue/images/public/line_blue.jpg" alt="上行速率"/><?=Yii::$app->sysLanguage->getTranslateBySymbol('flowUp')?>:<span class="blue" id="flowOut"></span>
            <img src="<?=$staticResourcePrefix?>skin/blue/images/public/line_pur.jpg" alt="下行速率"/><?=Yii::$app->sysLanguage->getTranslateBySymbol('flowDown')?>:<span class="pur" id="flowIn"></span>
        </div>
        <div class="report_search">
            <div class="xlk">
                <span class="seltime fswz f1" id="flowCurrent">ALL</span>
                <input type="hidden" name="net_port" value="">
                <span class="xlk-icon fs-icon fsi1">
				  <span class="arrow-down"></span>
			  </span>
            </div>
            <div class="xlsj fs fs1" style="left: 0px; top: 5px; display: none;">
                <ul>
                    <li><option value="GLOBAL" show="ALL">ALL</option></li>
                    <?php
                    foreach ($netport as $k => $v) {
                        echo "<li><option value='{$k}' show='{$v}'>{$v}</option></li>";
                    }
                    ?>
                </ul>
            </div>
        </div>
        <div id="chart" class="chart"></div>
    </div>
</div>

<!--报表-->
<script src="<?=$urlPrefix?>assets/js/echarts/echarts.min.js"></script>
<script>
    var date = [];
    var data = [0];
    var data2 = [0];

    function addData() {
        var nowTime = new Date();
        var now = [nowTime.getHours(), nowTime.getMinutes(), nowTime.getSeconds()].join(':');

        $.ajax({
            url: '/System/GetStatistic',
            type: 'POST',
            data: {},
            dataType: 'json',
            timeout: 5000,
            cache: false,//不缓存数据
            async: true,//同步：false,异步：true,默认true
            success: function(result){
                var flowCurrent = $('#flowCurrent').text();
                var netCard = $('[show="' + flowCurrent + '"]').attr('value');

                var flowOutput = flowInput = 0;
                try {
                    flowOutput = result.interface[netCard]['OUT'];
                    flowInput = result.interface[netCard]['IN'];
                } catch (e){
                    flowOutput = 0;
                    flowInput = 0;
                }

                $('#flowOut').text(flowOutput + 'Mbps');
                $('#flowIn').text(flowInput + 'Mbps');
                data.push(flowOutput);
                data2.push(flowInput);
                date.push(now);
                if (date.length > 60) {
                    date.shift();
                    data.shift();
                    data2.shift();
                }
            },
        });
    }

    var option = {
        color: ['#23c4c6','#b8a4df'],
        calculable : true,
        grid:{
            left:60,
            top:40,
            right:30,
            bottom:60,
            borderColor: '#fafafa'
        },

        tooltip : {
            trigger: 'axis',
            formatter: function(params) {
                return params[0].name + '<br/>'
                    + params[0].seriesName + ' : ' + params[0].value + 'Mbps<br/>'
                    + params[1].seriesName + ' : ' + params[1].value + 'Mbps';
            }
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: date,
            axisLine: {onZero: false},
            splitLine : {show : true},
        },
        yAxis: {
            boundaryGap: [0, '10%'],
            type: 'value',
            name:'Mbps'
        },
        series: [
            {
                name: top.translation.t('flowUp'),
                type:'line',
                smooth:true,
                symbol: 'none',
                //stack: 'a',
                showSymbol: true,
                hoverAnimation: true,
                /*areaStyle: {
                    normal: {}
                },*/
                data: data
            },{
                name: top.translation.t('flowDown'),
                type:'line',
                smooth:true,
                symbol: 'none',
                //stack: 'b',
                showSymbol: true,
                hoverAnimation: true,
                /*areaStyle: {
                    normal: {}
                },*/
                data: data2
            }
        ]
    };

    var myChart = echarts.init(document.getElementById('chart'));
    myChart.setOption(option);
    setInterval(function () {
        addData();
        myChart.setOption({
            xAxis: {
                data: date
            },
            series: [{
                name: top.translation.t('flowUp'),
                data: data
            },{
                name: top.translation.t('flowDown'),
                data: data2
            }]
        });
    }, 1000);
</script>
</body>
</html>
