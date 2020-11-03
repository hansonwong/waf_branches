<?php
use yii\helpers\Html;
$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}/assets/waf/";
?>
<html>
<head>
</head>
<body>
<div class="openWin" style="width: 900px; height: 600px; overflow: auto;">
    <form action="" method="POST" id="form_id">
        <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
            <input type="hidden" name="_csrf" id="_csrf" value="" />
            <input type="hidden" name="id" id="id" value="<?=$model->id ?>" />
            <tr>
                <!--时间范围-->
                <td width="100" class="t_r"><span class="red">*</span><?=Yii::$app->sysLanguage->getTranslateBySymbol('timeFrame')?>：</td>
                <td colspan="3">
                    <!--开始时间-->
                    <input type="text" name="startDate" id="startDate" class="text date_plug validate[required]"  onFocus="var endDate=$dp.$('endDate');WdatePicker({onpicked:function(){endDate.focus();},maxDate:'#F{$dp.$D(\'endDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStart')?>">
                    <!--至-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('to')?></label>
                    <!--结束时间-->
                    <input type="text" name="endDate" id="endDate" class="text date_plug validate[required]"  onFocus="WdatePicker({minDate:'#F{$dp.$D(\'startDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})"  placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStop')?>">
                    <input name="submit" type="submit" class="btn_ty" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('query')?>">
                </td>
            </tr>
        </table>
    </form>
    <div class="report_wrap">
        <div class="chart_row">
            <!--响应时间分布-->
            <h3 class="title_h3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('responseTimeDistribution')?></h3>
            <div id="TimeDistribute" class="chart"></div>
        </div>
        <div class="chart_row">
            <!--响应时间（毫秒）-->
            <h3 class="title_h3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('responseTime(MS)')?></h3>
            <div id="responseTime" class="chart"></div>
        </div>
        <div class="chart_row">
            <!--监控目标URL状态-->
            <h3 class="title_h3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('monitoringTargetUrlState')?></h3>
            <div id="urlstatus" class="chart"></div>
        </div>
    </div>
</div>
</body>
<!-- 引入 ECharts 文件 -->
<script type="text/javascript" src="<?=$staticResourcePrefix?>/js/lib/echarts/echarts-all.js"></script>

<script type="text/javascript">

    //获取当前的时间，格式YYYY-MM-DD HH:MM:SS
    function getNowFormatDate() {
        var date = new Date();
        var seperator1 = "-";
        var seperator2 = ":";
        var month = date.getMonth() + 1;
        var strDate = date.getDate();
        if (month >= 1 && month <= 9) {
            month = "0" + month;
        }
        if (strDate >= 0 && strDate <= 9) {
            strDate = "0" + strDate;
        }
        var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate
            + " " + date.getHours() + seperator2 + date.getMinutes()
            + seperator2 + date.getSeconds();
        return currentdate;
    }


    //获取iHour小时之前的时间，格式YYYY-MM-DD HH:MM:SS
    function getLastFormatDate(iHour) {
        var date = new Date();
        var seperator1 = "-";
        var seperator2 = ":";
        var month = date.getMonth() + 1;
        var strDate = date.getDate();
        var hour = date.getHours();
        var minute = date.getMinutes();
        if (hour < iHour){
            //暂时不作跨日处理，
            hour=0;
            minute = "0" ;
        }
        else{
            hour = hour -iHour;
        }

        if (month >= 1 && month <= 9) {
            month = "0" + month;
        }
        if (strDate >= 0 && strDate <= 9) {
            strDate = "0" + strDate;
        }
        var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate
            + " " + hour + seperator2 + minute
            + seperator2 + date.getSeconds();
        return currentdate;
    }

    function reloadTimeDistributeChart(showData){
        var TimeDistributeChart = echarts.init(document.getElementById('TimeDistribute'));
        var TimeDistributeOption = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            grid: {
                x: '10%',
                x2: '10%',
                y: '10%',
                y2: '30%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    axisLabel:{interval:0,rotate:70},
                    data: showData['time']
                    //data:["0ms~100ms","100ms~500ms","500ms~1000ms","1s~10s","10s~30s","30s~60s","60s~180s","180s~300s","300s\u4ee5\u4e0a"]
                    //data :['0ms~100ms','100ms~500ms',"500ms~1000ms","1s~10s","10s~30s","30s~60s","60s~180s","300s以上"]
                }
            ],
            yAxis: [
                {
                    type: 'value'
                }
            ],
            series: [
                {
                    name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("totalCount") ?>', //'总数',
                    type: 'bar',
                    data: showData['tdData']
                    //data: [0,0,0,0,0,0,0,0,0]
                    //data :[10, 52,20,60,100,50,120]
                }
            ]
        };
        TimeDistributeChart.setOption(TimeDistributeOption);

    }

    function reloadResponseTimeChart(showData){
        var responseTimeChart = echarts.init(document.getElementById('responseTime'));
        var responseTimeOption = {
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                x: '10%',
                x2: '10%',
                y: '10%',
                y2: '30%',
                containLabel: true
            },
            xAxis: [
                {
                    gridIndex: 0,
                    splitLine: {show: false},
                    type: "category",
                    axisLabel: {interval: 'auto', rotate: 70},
                    data: showData['time']
                }

            ],
            yAxis: {
                name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("time") ?>',  //时间
                type: 'value',
                axisLabel: {
                    formatter: '{value} ms'
                }
            },
            series: [
                {
                    name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("responseTime") ?>',  //响应时间
                    type: 'line',
                    data:showData['rtData']
                }
            ]
        };
        responseTimeChart.setOption(responseTimeOption);

    }

    function reloadUrlstatusChart(showData){
        var urlstatusChart = echarts.init(document.getElementById('urlstatus'));
        var urlstatusOption = {
            color:['#2f7ed8'],
            textStyle: {color: "#888"},
            title: {
                show: false,
                text: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("monitoringTargetUrlState") ?>',  //监控目标URL状态
                left: 'center',
                textStyle: {
                    color: "#5c8de5",
                    fontWeight: "bold",
                    fontSize: 16
                },
            },
            tooltip: {
                trigger: 'axis',
                formatter: function( params ) {
                    if(params[0].data ==0){
                        return params[0].name + "</br>"+ "<?=Yii::$app->sysLanguage->getTranslateBySymbol('status') ?>：<?=Yii::$app->sysLanguage->getTranslateBySymbol('stopUse') ?>";  //状态：不可用
                    }else if (params[0].data ==1) {
                        return params[0].name + "</br>" + "<?=Yii::$app->sysLanguage->getTranslateBySymbol('status') ?>：<?=Yii::$app->sysLanguage->getTranslateBySymbol('normal') ?>";  //状态：正常
                    }else{
                        return params[0].name + "</br>" + "<?=Yii::$app->sysLanguage->getTranslateBySymbol('status') ?>：";  //状态
                    }
                }
            },
            xAxis: {
                type: 'category',
                name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("time") ?>',  //时间
                axisLabel: {interval: 'auto', rotate: 70},
                splitLine: {show: false},
                data:showData['time']
            },
            grid: {
                x: '10%',
                x2: '10%',
                y: '10%',
                y2: '30%',
                containLabel: true
            },
            yAxis: {
                name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("status") ?>',  //状态
                type: 'value',
                axisLabel: {
                    formatter: function (value) {
                        var texts = [];
                        if(value==0){
                            texts.push('<?=Yii::$app->sysLanguage->getTranslateBySymbol("stopUse") ?>');  //停用
                        }
                        else if (value ==1) {
                            texts.push('<?=Yii::$app->sysLanguage->getTranslateBySymbol("normal") ?>');  //正常
                        }
                        else{
                            texts.push('');
                        }
                        return texts;
                    }
                }
            },
            series: [
                {
                    name: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("status") ?>',  //状态
                    type: 'line',
                    data: showData['statusData']['normalData'],
                    symbolSize : 3

                }
            ]
        };
        urlstatusChart.setOption(urlstatusOption);
    }

    (function ($) {
        var _csrf = $('meta[name=csrf-token]').attr('content');
        $('#_csrf').val(_csrf);

        $('.list_page').on('click', 'input.btn_ty', function () {
            e.preventDefault();
            $("#form_id").submit();
        });

        // 提交与检验数据
        $("#form_id").validationEngine({
            promptPosition:'centerRight: 0, -4',scroll: false , binded: false ,'custom_error_messages': {
                'required': {
                    'message': '* <?=Yii::$app->sysLanguage->getTranslateBySymbol('requiredItem')?>！'
                },
                'min': {
                    'message': '* <?=Yii::$app->sysLanguage->getTranslateBySymbol('smartBlockConfigTips')?>！'
                }
            },
            ajaxFormValidationMethod: 'post',
            //指定使用Ajax模式提交表单处理
            ajaxFormValidation: true,
            onAjaxFormComplete: function(status, form, json, options){
                if(json.code === 'T')
                {
                    reloadTimeDistributeChart(json.td);
                    reloadResponseTimeChart(json.rt);
                    reloadUrlstatusChart(json.status);
                }
            }
        });
    })(jQuery);

    //初始化
    $('#startDate').val(getLastFormatDate(1));
    $('#endDate').val(getNowFormatDate());

    //默认显示前1小时的统计结果
    $("#form_id").submit();
    //reloadTimeDistributeChart([1]);
</script>
</html>