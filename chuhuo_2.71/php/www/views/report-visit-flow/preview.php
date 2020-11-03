<?php

/* @var $this \yii\web\View */
/* @var $content string */

use yii\helpers\Html;
$translate = Yii::$app->sysLanguage;
?>

<!DOCTYPE html>
<html>
<head>
    <title><?=$translate->getTranslateBySymbol('bluedonWebAppDefendSystemVisitReport')?></title>
    <meta charset="utf-8">
    <meta name="renderer" content="webkit">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">
    <?= Html::csrfMetaTags() ?>
    <link rel="stylesheet" type="text/css" href="../plugins/waf_report.css"/>
    <script src="../plugins/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript">
        //切换主机
        function switchDomain() {
            $("#switch_domain").submit();
        }
    </script>
</head>
<body>
<!--chart_wrap start -->
<div class="chart_wrap">
    <div class="chart_header">
        <h1 class="title"><?=$translate->getTranslateBySymbol('bluedonWebAppDefendSystemVisitReport')?></h1>
        <div class="basemsg_table">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
                <tbody>
                <tr class="item">
                    <td><?=$translate->getTranslateBySymbol('productModel')?>：<?= $device_model ?></td>
                    <td><?=$translate->getTranslateBySymbol('statisticalTimePeriod')?>：<?= $data_section ?></td>
                    <td><?=$translate->getTranslateBySymbol('reportGenerationTime')?>：<?= $create_time ?></td>
                </tr>
                <tr class="item">
                    <td><?=$translate->getTranslateBySymbol('managementInterfaceAddress')?>：<?= $device_ip ?></td>
                    <td><?=$translate->getTranslateBySymbol('protectionWebsite')?>：<?= $domain_host ?></td>
                    <td><?=$translate->getTranslateBySymbol('explain')?>：<?= $desc ?></td>
                </tr>
                </tbody>
            </table>
        </div>
        <form id="switch_domain" method="post">
            <input type="hidden" name="_csrf" id="_csrf" value=""/>
            <input name="fileType" type="hidden" value="html">
            <input name="reportDate" type="hidden" value="<?=$reportDate?>">
        <select name="domain_name" id="" class="domain_select" onchange="switchDomain()">
            <?php foreach ($domain_list as $domain): ?>
                <option value="<?= $domain ?>" <?php if($domain==$domain_host)echo 'selected=selected';?>><?= $domain ?></option>
            <?php endforeach; ?>
        </select>
        </form>
        <!--<button class="btn_down">下载</button>-->
    </div>
    <!-- main start -->
    <div class="chart_main clearfix">
        <!-- 安全统计分析 start-->
        <div class="chart_box box_h1  clearfix">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('safetyStatisticalAnalysis')?></h2>
            <div id="aqtjChartBar" class="chart"></div>
        </div>
        <!-- 安全统计分析 end-->

        <!-- 综合分析(按月) start-->
        <div class="chart_box" style="display: none">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('comprehensiveAnalysis(monthly)')?></h2>
            <div id="zhfxmonthChartLine" class="chart"></div>
        </div>
        <!-- 综合分析(按月) end-->

        <!-- 综合分析(按天) start-->
        <div class="chart_box" style="display: none">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('comprehensiveAnalysis(dayly)')?></h2>
            <div id="zhfxdayChartLine" class="chart"></div>
        </div>
        <!-- 综合分析(按天) end-->

        <!-- 用户在您网站停留的时间 start-->
        <div class="chart_box box_h1 clearfix" style="display: none">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('theTimeUserStaysOnYourWebsite')?></h2>
            <div id="yhtlsjChartBar" class="chart"></div>
        </div>
        <!-- 用户在您网站停留的时间 end-->

        <!-- 爬虫分析 start-->
        <div class="chart_box box_h1 clearfix" style="display: none">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('reptilianAnalysis')?></h2>
            <div id="pcfxChartBar" class="chart"></div>
        </div>
        <!-- 爬虫分析 end-->

        <!-- 网站流量(按天) start-->
        <div class="chart_box box_h1 clearfix">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('websiteTraffic(day)')?></h2>
            <div id="wzllChartLine" class="chart"></div>
        </div>
        <!-- 网站流量(按天) end-->

        <!-- 网络流量 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('websiteTraffic')?></h2>
            <div class="list-content">
                <div class="list-conhead">
                    <table border="0" class="table-head" cellspacing="0" cellpadding="0">
                        <tr>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('networkInterface')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('mode')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('status')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('receiveDataPacket')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('sendDataPacket')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('receiveByte')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('sendDataPacket')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('receivedErrorPackets')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('sentErrorPackets')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('receiveLoss')?></td>
                            <td style="width:9%"><?=$translate->getTranslateBySymbol('sendLoss')?></td>
                        </tr>
                    </table>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con" cellspacing="0" cellpadding="0">
                        <?php
                        if ($current_domain['network_flow']):
                            foreach ($current_domain['network_flow'] as $row): ?>
                                <tr>
                                    <td style="width:9%"><?= $row['port'] ?></td>
                                    <td style="width:9%"><?= $row['model'] ?></td>
                                    <td style="width:9%"><?= $row['status'] ?></td>
                                    <td style="width:9%"><?= $row['receive_pack'] ?></td>
                                    <td style="width:9%"><?= $row['send_pack'] ?></td>
                                    <td style="width:9%"><?= $row['receive_byte'] ?></td>
                                    <td style="width:9%"><?= $row['send_byte'] ?></td>
                                    <td style="width:9%"><?= $row['receive_error'] ?></td>
                                    <td style="width:9%"><?= $row['send_error'] ?></td>
                                    <td style="width:9%"><?= $row['receive_lost'] ?></td>
                                    <td style="width:9%"><?= $row['send_lost'] ?></td>
                                </tr>
                            <?php endforeach;endif; ?>

                    </table>
                </div>
            </div>
        </div>
        <!-- 网络流量 end-->

        <!-- 网站入口页面(被访问次数-TOP10) start-->
        <div class="chart_box">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('websiteEntrancePageVisistTimes')?> TOP10</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:79%"><?=$translate->getTranslateBySymbol('byVisitingThePage')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('frequency')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('100Percent')?>(%)</li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php $total = 0; ?>
                        <?php if( !empty($website_in[$domain_host]) ): ?>
                            <?php foreach ($website_in[$domain_host] as $row):?>
                                <tr>
                                    <td style="width:77%"><?= htmlspecialchars($row['url']) ?></td>
                                    <td style="width:10%"><?= $row['number'] ?></td>
                                    <td style="width:10%"><?= $row['percent'] ?></td>
                                </tr>
                                <?php $total += $row['number']; ?>
                            <?php endforeach; ?>
                        <?php endif; ?>
                        <tr>
                            <td class="t_c"></td>
                            <td></td>
                            <td class="t_r"><?=$translate->getTranslateBySymbol('total')?>：<?= $total ?></td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
        <!-- 网站入口页面(被访问次数-TOP10) end-->

        <!-- 网站出口页面(被访问次数-TOP10) start-->
        <div class="chart_box">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('websiteExportPageVisistTimes')?> TOP10</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:79%"><?=$translate->getTranslateBySymbol('byVisitingThePage')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('frequency')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('100Percent')?>(%)</li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php if ($website_out[$domain_host]): ?>
                            <?php foreach ($website_out[$domain_host] as $row):?>
                                <tr>
                                    <td style="width:77%"><?= htmlspecialchars($row['url']) ?></td>
                                    <td style="width:10%"><?= $row['number'] ?></td>
                                    <td style="width:10%"><?= $row['percent'] ?></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 网站出口页面(被访问次数-TOP10) end-->

        <!-- 页面访问排名-TOP10 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('pageAccessRankings')?> TOP10</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:79%"><?=$translate->getTranslateBySymbol('byVisitingThePage')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('frequency')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('100Percent')?>(%)</li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php if ($website_top[$domain_host]): ?>
                            <?php foreach ($website_top[$domain_host] as $row):?>
                                <tr>
                                    <td style="width:77%"><?= htmlspecialchars($row['url']) ?></td>
                                    <td style="width:10%"><?= $row['number'] ?></td>
                                    <td style="width:10%"><?= $row['percent'] ?></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 页面访问排名-TOP10 end-->

        <!-- 错误码排名-TOP10 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('errorCodeRanking')?> TOP10</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:79%"><?=$translate->getTranslateBySymbol('errorCode')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('frequency')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('100Percent')?>(%)</li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php
                        if ($errors_top10[$domain_host]):
                            foreach ($errors_top10[$domain_host] as $row):?>
                                <tr>
                                    <td style="width:77%"><?= $row['code'] ?></td>
                                    <td style="width:10%"><?= $row['number'] ?></td>
                                    <td style="width:10%"><?= $row['percent'] ?></td>
                                </tr>
                                <?php
                            endforeach;
                        endif;
                        ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 错误码排名-TOP10 end-->

        <!-- 从搜索引擎进入我的网站-TOP10 start-->
        <div class="chart_box" style="display: none">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('fromTheSearchEngineToMyWebsite')?> TOP10</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:79%"><?=$translate->getTranslateBySymbol('searchEngine')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('frequency')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('100Percent')?>(%)</li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php
                        if ($engine_top10[$domain_host]):
                            foreach ($engine_top10[$domain_host] as $row):?>
                                <tr>
                                    <td style="width:77%"><?= $row['engine'] ?></td>
                                    <td style="width:10%"><?= $row['number'] ?></td>
                                    <td style="width:10%"><?= $row['percent'] ?></td>
                                </tr>
                                <?php
                            endforeach;
                        endif;
                        ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 从搜索引擎进入我的网站-TOP10 end-->

        <!-- 从别的网站进入我的网站-TOP10 start-->
        <div class="chart_box" style="display: none">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('accessMyWebsiteFromOtherWebsites')?> TOP10</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:79%">URL</li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('frequency')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('100Percent')?>(%)</li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php
                        if ($sites_top10[$domain_host]):
                            foreach ($sites_top10[$domain_host] as $row):?>
                                <tr>
                                    <td style="width:77%"><?= $row['url'] ?></td>
                                    <td style="width:10%"><?= $row['number'] ?></td>
                                    <td style="width:10%"><?= $row['percent'] ?></td>
                                </tr>
                                <?php
                            endforeach;
                        endif;
                        ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 从别的网站进入我的网站-TOP10 end-->

        <!-- 搜索关键字-TOP10 start-->
        <div class="chart_box" style="display: none">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('searchKeywords')?> TOP10</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:79%"><?=$translate->getTranslateBySymbol('keywords')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('frequency')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('100Percent')?>(%)</li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php
                        if ($keyword_top10[$domain_host]):
                            foreach ($keyword_top10[$domain_host] as $row):?>
                                <tr>
                                    <td style="width:77%"><?= $row['word'] ?></td>
                                    <td style="width:10%"><?= $row['number'] ?></td>
                                    <td style="width:10%"><?= $row['percent'] ?></td>
                                </tr>
                                <?php
                            endforeach;
                        endif;
                        ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 搜索关键字-TOP10 end-->

        <!-- 用户都用什么样的操作系统？ start-->
        <div class="chart_box" style="display: none">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('whatKindOfOperatingSystemIsUsedByUser')?></h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:79%"><?=$translate->getTranslateBySymbol('system')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('frequency')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('100Percent')?>(%)</li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php
                        if ($operation_system_top10[$domain_host]):
                            foreach ($operation_system_top10[$domain_host] as $row):?>
                                <tr>
                                    <td style="width:77%"><?= $row['name'] ?></td>
                                    <td style="width:10%"><?= $row['number'] ?></td>
                                    <td style="width:10%"><?= $row['percent'] ?></td>
                                </tr>
                                <?php
                            endforeach;
                        endif;
                        ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 用户都用什么样的操作系统？ end-->

        <!-- 用户都用什么样的浏览器？ start-->
        <div class="chart_box" style="display: none">
            <h2 class="chart_title"><?=$translate->getTranslateBySymbol('whatKindOfBrowsersDoUsersUse')?></h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:79%"><?=$translate->getTranslateBySymbol('browser')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('frequency')?></li>
                        <li style="width:10%"><?=$translate->getTranslateBySymbol('100Percent')?>(%)</li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php
                        if ($browser_top[$domain_host]):
                            foreach ($browser_top[$domain_host] as $row):?>
                                <tr>
                                    <td style="width:77%"><?= $row['name'] ?></td>
                                    <td style="width:10%"><?= $row['number'] ?></td>
                                    <td style="width:10%"><?= $row['percent'] ?></td>
                                </tr>
                                <?php
                            endforeach;
                        endif;
                        ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 用户都用什么样的浏览器？ end-->

    </div>
    <!-- chart_main end -->
</div><!-- chart_wrap end -->

<!-- 引入 ECharts 文件 -->
<script type="text/javascript" src="../plugins/echarts-all.js"></script>
<script type="text/javascript">
    $(function () {
        $(document).ready(function () {
            var _csrf = $('meta[name=csrf-token]').attr('content');
            $('#_csrf').val(_csrf);

            aqtjChartBar();
            zhfxmonthChartLine();
            zhfxdayChartLine();
            yhtlsjChartBar();
            pcfxChartBar();
            wzllChartLine();

        });
    });

    //安全统计分析
    function aqtjChartBar() {
        aqtjChartBarInstance = echarts.init(document.getElementById('aqtjChartBar'));
        aqtjChartBarOption = {
            color: ["#3eb7fe", "#a667dc", "#ff7143"],
            title: {
                text: '<?=$translate->getTranslateBySymbol('total')?> PV：<?=$current_domain['security_total']?>',
                x: 'center',
                textStyle: {
                    fontSize: 14,
                    color: '#555'
                }
            },
            grid:{
                x2:'350px'
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            calculable: true,
            xAxis: [
                {
                    type: 'category',
                    splitLine: {show: false},
                    axisLabel: {
                        //rotate:'45',
                        textStyle: {
                            fontSize: '14',
                            color: '#555'
                        }
                    },
                    axisLine: {
                        lineStyle: {
                            type: 'solid',
                            color: '#eee',//左边线的颜色
                            width: '1'//坐标线的宽度
                        }
                    },
                    axisTick: {
                        lineStyle: {
                            color: "#555"
                        }, show: false
                    },
                    data: ['<?=$translate->getTranslateBySymbol('normalAccess')?>',
                        '<?=$translate->getTranslateBySymbol('fromReptiles')?>',
                        '<?=$translate->getTranslateBySymbol('fromThreat')?>']
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    axisLabel: {
                        textStyle: {
                            fontSize: '14',
                            color: '#555'
                        }
                    },
                    axisLine: {
                        lineStyle: {
                            type: 'solid',
                            color: '#eee',//左边线的颜色
                            width: '1'//坐标线的宽度
                        }
                    },
                    axisTick: {
                        lineStyle: {
                            color: "#eee"
                        }, show: false
                    }
                }
            ],
            series: [
                {
                    name: '<?=$translate->getTranslateBySymbol('safetyStatisticalAnalysis')?>',
                    type: 'bar',
                    barWidth: '60',
                    itemStyle: {
                        normal: {
                            color: function (params) {
                                // build a color map as your need.
                                var colorList = [
                                    "#3eb7fe", "#a667dc", "#ff7143"
                                ];
                                return colorList[params.dataIndex]
                            },
                            label: {show: true, position: 'top'}
                        }
                    },
                    data: [
                        <?=$current_domain['security_normal']?>,
                        <?=$current_domain['security_crawler']?>,
                        <?=$current_domain['security_thread']?>
                    ]
                },
                {
                    name: '<?=$translate->getTranslateBySymbol('safetyStatisticalAnalysis')?>',
                    type: 'pie',
                    tooltip: {
                        trigger: 'item',
                        formatter: '{a} <br/>{b} : {c} ({d}%)'
                    },
                    center: ['80%', '30%'],
                    radius: [0, 50],
                    calculable: false,
                    itemStyle: {
                        normal: {
                            label: {
                                show: true,
                                formatter: '{b} :{d}%'
                            },
                            labelLine: {length: 20}
                        }
                    },
                    data: [
                        {value: <?=$current_domain['security_normal']?>, name: '<?=$translate->getTranslateBySymbol('normalAccess')?>'},
                        {value: <?=$current_domain['security_crawler']?>, name: '<?=$translate->getTranslateBySymbol('fromReptiles')?>'},
                        {value: <?=$current_domain['security_thread']?>, name: '<?=$translate->getTranslateBySymbol('fromThreat')?>'}
                    ]
                }
            ]
        };

        aqtjChartBarInstance.setOption(aqtjChartBarOption);
    }

    //综合分析(按月)
    <?php
    $combine_month = ['visits' => [], 'visits_unique' => [], 'pages' => [], 'files' => []];
    if ($current_domain['combine_analysis_month']) {
        foreach ($current_domain['combine_analysis_month'] as $row) {
            $combine_month['visits'][] = $row['visits'];
            $combine_month['visits_unique'][] = $row['visits_unique'];
            $combine_month['pages'][] = $row['pages'];
            $combine_month['files'][] = $row['files'];
        }
    }
    ?>
    function zhfxmonthChartLine() {
        var zhfxmonthChartLineInstance = echarts.init(document.getElementById('zhfxmonthChartLine'));
        zhfxmonthChartLineOption = {
            color: ["#03bdd6", "#89c24d", "#3eb7fe", "#a667dc", "#ffc700", "#ff7143", "#ffecb3"],
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                x: '8%',
                x2: '4%',
                y2: 50,
                y: '10%',
                containLabel: true
            },
            legend: {
                data: ['<?=$translate->getTranslateBySymbol('accessTimes')?>',
                    '<?=$translate->getTranslateBySymbol('visitorsCount')?>',
                    '<?=$translate->getTranslateBySymbol('pageCount')?>',
                    '<?=$translate->getTranslateBySymbol('fileCount')?>']
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                name: '<?=$translate->getTranslateBySymbol('month')?>',
                nameTextStyle: {
                    fontSize: 14,
                    color: '#555'
                },
                data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                axisLabel: {
                    textStyle: {
                        fontSize: 14,
                        color: '#555'
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid',
                        color: '#eee',//左边线的颜色
                        width: '1'//坐标线的宽度
                    }
                },
                axisTick: {
                    lineStyle: {
                        color: "#555"
                    }, show: false
                },
                splitLine: {show: false}
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    textStyle: {
                        fontSize: '14',
                        color: '#555'
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid',
                        color: '#eee',//左边线的颜色
                        width: '1'//坐标线的宽度
                    }
                },
                axisTick: {
                    lineStyle: {
                        color: "#555"
                    }
                }
            },
            series: [
                {
                    name: '<?=$translate->getTranslateBySymbol('accessTimes')?>',
                    type: 'line',
                    data: [<?=implode(',', $combine_month['visits'])?>]
                },
                {
                    name: '<?=$translate->getTranslateBySymbol('visitorsCount')?>',
                    type: 'line',
                    data: [<?=implode(',', $combine_month['visits_unique'])?>]
                },
                {
                    name: '<?=$translate->getTranslateBySymbol('pageCount')?>',
                    type: 'line',
                    data: [<?=implode(',', $combine_month['pages'])?>]
                },
                {
                    name: '<?=$translate->getTranslateBySymbol('fileCount')?>',
                    type: 'line',
                    data: [<?=implode(',', $combine_month['files'])?>]
                }
            ]
        };

        zhfxmonthChartLineInstance.setOption(zhfxmonthChartLineOption);
    }
    //综合分析(按天)
    <?php
    $combine_day = ['days' => [], 'visits' => [], 'pages' => [], 'files' => [], 'bandwidth' => []];
    $index = 1;
    if ($current_domain['combine_analysis_day']) {
        foreach ($current_domain['combine_analysis_day'] as $row) {
            $combine_day['days'][] = $index;
            $index++;
            $combine_day['visits'][] = $row['visits'];
            $combine_day['pages'][] = $row['pages'];
            $combine_day['files'][] = $row['files'];
            $combine_day['bandwidth'][] = $row['bandwidth'];
        }
    }
    ?>
    function zhfxdayChartLine() {
        var zhfxdayChartLineInstance = echarts.init(document.getElementById('zhfxdayChartLine'));
        zhfxdayChartLineOption = {
            color: ["#03bdd6", "#89c24d", "#3eb7fe", "#a667dc", "#ffc700", "#ff7143", "#ffecb3"],
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                x: '8%',
                x2: '4%',
                y2: 50,
                y: '10%',
                containLabel: true
            },
            legend: {
                data: ['<?=$translate->getTranslateBySymbol('flowNumber')?>',
                    '<?=$translate->getTranslateBySymbol('pageCount')?>',
                    '<?=$translate->getTranslateBySymbol('fileCount')?>']
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                name: '<?=$translate->getTranslateBySymbol('day')?>',
                nameTextStyle: {
                    fontSize: 14,
                    color: '#555'
                },
                data: [<?="'" . implode("','", $combine_day['days']) . "'"?>],
                axisLabel: {
                    textStyle: {
                        fontSize: 14,
                        color: '#555'
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid',
                        color: '#eee',//左边线的颜色
                        width: '1'//坐标线的宽度
                    }
                },
                axisTick: {
                    lineStyle: {
                        color: "#555"
                    }, show: false
                },
                splitLine: {show: false}
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    textStyle: {
                        fontSize: '14',
                        color: '#555'
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid',
                        color: '#eee',//左边线的颜色
                        width: '1'//坐标线的宽度
                    }
                },
                axisTick: {
                    lineStyle: {
                        color: "#555"
                    }
                }
            },
            series: [
                {
                    name: '<?=$translate->getTranslateBySymbol('flowNumber')?>',
                    type: 'line',
                    data: [<?=implode(',', $combine_day['visits'])?>]
                },
                {
                    name: '<?=$translate->getTranslateBySymbol('pageCount')?>',
                    type: 'line',
                    data: [<?=implode(',', $combine_day['pages'])?>]
                },
                {
                    name: '<?=$translate->getTranslateBySymbol('fileCount')?>',
                    type: 'line',
                    data: [<?=implode(',', $combine_day['files'])?>]
                }
            ]
        };

        zhfxdayChartLineInstance.setOption(zhfxdayChartLineOption);
    }
    //用户在您网站停留的时间
    <?php
    $stay_times = ['ranged' => [], 'visits' => []];
    if ($current_domain['user_stay_time']) {
        foreach ($current_domain['user_stay_time'] as $row) {
            $stay_times['ranged'][] = $row['ranged'];
            $stay_times['visits'][] = $row['visits'];
        }
    }
    ?>
    function yhtlsjChartBar() {
        var yhtlsjChartBarInstance = echarts.init(document.getElementById('yhtlsjChartBar'));
        yhtlsjChartBarOption = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            grid: {
                x: '8%',
                x2: '4%',
                y2: 50,
                y: '10%',
                borderWidth: 0
            },
            calculable: true,
            xAxis: [
                {
                    type: 'value',
                    boundaryGap: [0, 0.01],
                    axisLine: {
                        lineStyle: {
                            color: '#eee',
                        }
                    },
                    axisTick: {
                        lineStyle: {
                            color: '#eee'
                        }
                    },
                    axisLabel: {
                        textStyle: {
                            fontSize: 12,
                            color: '#555'
                        }
                    },
                    splitLine: {
                        show: false
                    },
                    splitArea: {
                        show: false
                    }
                }
            ],
            yAxis: [
                {
                    type: 'category',
                    axisLine: {
                        lineStyle: {
                            color: '#eee',
                        }
                    },
                    axisTick: {
                        lineStyle: {
                            color: '#eee'
                        }
                    },
                    axisLabel: {
                        textStyle: {
                            fontSize: 12,
                            color: '#555'
                        }
                    },
                    splitLine: {
                        show: false
                    },
                    splitArea: {
                        show: false
                    },
                    data: [<?="'" . implode("','", $stay_times['ranged']) . "'"?>]
                }
            ],
            series: [
                {
                    name: '<?=$translate->getTranslateBySymbol('userRetentionTime')?>',
                    type: 'bar',
                    barMaxWidth: 16,
                    itemStyle: {
                        normal: {
                            color: function (params) {
                                // build a color map as your need.
                                var colorList = [
                                    "#03bdd6", "#89c24d", "#3eb7fe", "#a667dc", "#ffc700", "#ff7143", "#ffecb3"
                                ];
                                return colorList[params.dataIndex]
                            },
                            label: {show: true, position: 'right'}
                        }
                    },
                    data: [<?=implode(',', $stay_times['visits'])?>]
                }
            ]
        };

        yhtlsjChartBarInstance.setOption(yhtlsjChartBarOption);
    }

    //爬虫分析
    <?php
    $robot_analysis = ['name' => [], 'hits' => []];
    if ($current_domain['robot_analysis']) {
        foreach ($current_domain['robot_analysis'] as $row) {
            $robot_analysis['name'][] = $row['name'];
            $robot_analysis['hits'][] = $row['hits'];
        }
    }
    ?>
    function pcfxChartBar() {
        var pcfxChartBarInstance = echarts.init(document.getElementById('pcfxChartBar'));
        pcfxChartBarOption = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            grid: {
                x: '8%',
                x2: '4%',
                y2: 50,
                y: '10%',
                borderWidth: 0
            },
            calculable: true,
            xAxis: [
                {
                    type: 'value',
                    boundaryGap: [0, 0.01],
                    axisLine: {
                        lineStyle: {
                            color: '#eee',
                        }
                    },
                    axisTick: {
                        lineStyle: {
                            color: '#eee'
                        }
                    },
                    axisLabel: {
                        textStyle: {
                            fontSize: 12,
                            color: '#555'
                        }
                    },
                    splitLine: {
                        show: false
                    },
                    splitArea: {
                        show: false
                    }
                }
            ],
            yAxis: [
                {
                    type: 'category',
                    axisLine: {
                        lineStyle: {
                            color: '#eee',
                        }
                    },
                    axisTick: {
                        lineStyle: {
                            color: '#eee'
                        }
                    },
                    axisLabel: {
                        textStyle: {
                            fontSize: 12,
                            color: '#555'
                        }
                    },
                    splitLine: {
                        show: false
                    },
                    splitArea: {
                        show: false
                    },
                    data: [<?="'" . implode("','", $robot_analysis['name']) . "'"?>]
                }
            ],
            series: [
                {
                    name: '<?=$translate->getTranslateBySymbol('reptiles')?>',
                    type: 'bar',
                    barMaxWidth: 60,
                    itemStyle: {
                        normal: {
                            color: function (params) {
                                // build a color map as your need.
                                var colorList = [
                                    "#3eb7fe", "#89c24d", "#a667dc", "#ffc700", "#ff7143", "#03bdd6"
                                ];
                                return colorList[params.dataIndex]
                            },
                            label: {show: true, position: 'right'}
                        }
                    },
                    data: [<?=implode(',', $robot_analysis['hits'])?>]
                }
            ]
        };

        pcfxChartBarInstance.setOption(pcfxChartBarOption);
    }

    //网站流量(按天)
    function wzllChartLine() {
        var wzllChartLineInstance = echarts.init(document.getElementById('wzllChartLine'));
        wzllChartLineOption = {
            color: ["#3eb7fe"],
            tooltip: {
                trigger: 'axis',
                formatter: "{b}日 流量约: <br/>{c}K"
            },
            grid: {
                x: '8%',
                x2: '4%',
                y2: 50,
                y: '10%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                name: '<?=$translate->getTranslateBySymbol('day')?>',
                nameTextStyle: {
                    fontSize: 14,
                    color: '#555'
                },
                data: [<?="'" . implode("','", $combine_day['days']) . "'"?>],
                axisLabel: {
                    textStyle: {
                        fontSize: '14',
                        color: '#555'
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid',
                        color: '#eee',//左边线的颜色
                        width: '1'//坐标线的宽度
                    }
                },
                axisTick: {
                    lineStyle: {
                        color: "#555"
                    }, show: false
                },
                splitLine: {show: false}
            },
            yAxis: {
                type: 'value',
                name: '<?=$translate->getTranslateBySymbol('flow')?>(K)',
                nameTextStyle: {
                    fontSize: 14,
                    color: '#555'
                },
                axisLabel: {
                    textStyle: {
                        fontSize: '14',
                        color: '#555'
                    }
                },
                axisLine: {
                    lineStyle: {
                        type: 'solid',
                        color: '#eee',//左边线的颜色
                        width: '1'//坐标线的宽度
                    }
                },
                axisTick: {
                    lineStyle: {
                        color: "#555"
                    }
                }
            },
            series: [
                {
                    name: '流量约',
                    type: 'line',
                    itemStyle: {
                        normal: {
                            label: {show: true, position: 'top'}
                        }
                    },
                    data: [<?=implode(',', $combine_day['bandwidth'])?>]
                }
            ]
        };

        wzllChartLineInstance.setOption(wzllChartLineOption);
    }

</script>
</body>
</html>