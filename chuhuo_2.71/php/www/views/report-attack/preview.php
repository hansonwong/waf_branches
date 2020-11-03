<!DOCTYPE html>
<?php
$translate = Yii::$app->sysLanguage;
?>
<html>
<head>
    <title><?= $translate->getTranslateBySymbol('bluedonWebAppDefendSystemAttackReport') ?></title>
    <meta charset="utf-8">
    <meta name="renderer" content="webkit">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">
    <link rel="stylesheet" type="text/css" href="./plugins/waf_report.css"/>
    <script src="./plugins/jquery.min.js" type="text/javascript"></script>
</head>
<body>
<!--chart_wrap start -->
<div class="chart_wrap">
    <div class="chart_header">
        <h1 class="title"><?= $translate->getTranslateBySymbol('bluedonWebAppDefendSystemAttackReport') ?></h1>
        <div class="basemsg_table">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
                <tbody>
                <tr class="item">
                    <td><?= $translate->getTranslateBySymbol('productModel') ?>：<?= $device_model ?></td>
                    <td><?= $translate->getTranslateBySymbol('statisticalTimePeriod') ?>：<?= $data_section ?></td>
                    <td><?= $translate->getTranslateBySymbol('reportGenerationTime') ?>：<?= $create_time ?></td>
                </tr>
                <tr class="item">
                    <td><?= $translate->getTranslateBySymbol('managementInterfaceAddress') ?>：<?= $device_ip ?></td>
                    <td><?= $translate->getTranslateBySymbol('reportContent:invadeReportStatistics') ?></td>
                    <td><?= $translate->getTranslateBySymbol('explain') ?>：<?= $desc ?></td>
                </tr>
                </tbody>
            </table>
        </div>
        <!--<button class="btn_down">下载</button>-->
    </div>
    <!-- main start -->
    <div class="chart_main clearfix">
        <!-- 入侵数量统计图 start-->
        <div class="chart_box box_h1  clearfix">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('invadeCountStatisticsMapTotal') ?>
                : <?= $attack_num_total ?></h2>
            <div id="rqslChartBar" class="chart"></div>
        </div>
        <!-- 入侵数量统计图 end-->

        <!-- 入侵趋势图 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('invadeTrendMap') ?></h2>
            <div id="rqqsChartLine" class="chart"></div>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:8%"><?= $translate->getTranslateBySymbol('day') ?></li>
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('date') ?></li>
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('eventTimes') ?></li>
                        <li style="width:10%" class="fold"><?= $translate->getTranslateBySymbol('100Percent') ?></li>
                        <li style="width:60%"><?= $translate->getTranslateBySymbol('attackType') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_date_trend_list as $key => $row): ?>
                            <tr>
                                <td style="width:8%"><?= $key + 1 ?></td>
                                <td style="width:10%"><?= $row['alert_date'] ?></td>
                                <td style="width:10%"><?= $row['alert_count'] ?></td>
                                <td style="width:10%"><?= $row['alert_percent'] ?></td>
                                <td style="width:60%"><?= $row['alert_desc'] ?></td>
                            </tr>
                        <?php endforeach; ?>

                    </table>
                </div>
            </div>
        </div>
        <!-- 入侵趋势图 end-->

        <!-- 入侵趋势图(24小时时间段) start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('invadeTrendMap(24hourPeriod)') ?></h2>
            <div id="rqqstimeChartLine" class="chart"></div>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:15%"><?= $translate->getTranslateBySymbol('time(hour)') ?></li>
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('eventTimes') ?></li>
                        <li style="width:10%" class="fold"><?= $translate->getTranslateBySymbol('100Percent') ?></li>
                        <li style="width:63%"><?= $translate->getTranslateBySymbol('attackType') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_hour_trend_list as $key => $row): ?>
                            <tr>
                                <td style="width:15%"><?= $row['alert_time'] ?></td>
                                <td style="width:10%"><?= $row['alert_count'] ?></td>
                                <td style="width:10%"><?= $row['alert_percent'] ?></td>
                                <td style="width:63%"><?= $row['alert_desc'] ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 入侵趋势图(24小时时间段) end-->

        <!-- 入侵类别统计图 start-->
        <div class="chart_box box_h1  clearfix">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('invadeClassStatisticalGraph') ?></h2>
            <div id="rqlbChartBar" class="chart"></div>
        </div>
        <!-- 入侵类别统计图 end-->

        <!-- 入侵类别对比图 start-->
        <div class="chart_box box_h1  clearfix">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('invadeClassCompareGraph') ?></h2>
            <div id="rqlbChartPie" class="chart"></div>
        </div>
        <!-- 入侵类别对比图 end-->

        <!-- 入侵类来源地址统计 TOP50 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('invadeClassSourceAddressStatistics') ?>
                TOP50</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('serialNumber') ?></li>
                        <li style="width:25%"><?= $translate->getTranslateBySymbol('ipAddress') ?></li>
                        <li style="width:49%"><?= $translate->getTranslateBySymbol('geographicalPosition') ?></li>
                        <li style="width:15%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_source_ip_top50 as $key => $row): ?>
                            <tr>
                                <td style="width:10%"><?= $key + 1 ?></td>
                                <td style="width:25%"><?= $row['attack_source_ip'] ?></td>
                                <td style="width:48%"><?= $row['attack_source_location'] ?></td>
                                <td style="width:15%"><?= $row['attack_source_count'] ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 入侵类来源地址统计 TOP50 end-->

        <!-- 攻击事件的入侵类来源统计 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('invadeClassSourceStatisticsForAttackEvents') ?></h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:74%"><?= $translate->getTranslateBySymbol('sourceIpAddress') ?></li>
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('proportion') ?></li>
                        <li style="width:15%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_type_ip as $item): ?>
                            <tr>
                                <td class="t_c"><?= $item['desc'] ?></td>
                                <td></td>
                                <td class="t_r"><?= $translate->getTranslateBySymbol('total') ?>
                                    ：<?= $item['total'] ?></td>
                            </tr>
                            <?php foreach ($item['list'] as $key => $row): ?>
                                <tr>
                                    <td style="width:73%"><?= $row['attack_ip'] ?></td>
                                    <td style="width:10%"><?= $row['attack_percent'] ?></td>
                                    <td style="width:15%"><?= $row['attack_count'] ?></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endforeach; ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 攻击事件的入侵类来源统计 end-->

        <!-- 入侵类来源的攻击事件统计TOP50 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('attackEventStatisticsFromIntrusionSources') ?>
                TOP50</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:74%"><?= $translate->getTranslateBySymbol('attackType') ?></li>
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('proportion') ?></li>
                        <li style="width:15%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_type_ip_top50 as $item): ?>
                            <tr>
                                <td class="t_c"><?= $item['ip'] ?></td>
                                <td></td>
                                <td class="t_r"><?= $translate->getTranslateBySymbol('total') ?>
                                    ：<?= $item['total'] ?></td>
                            </tr>
                            <?php foreach ($item['list'] as $key => $row): ?>
                                <tr>
                                    <td style="width:73%"><?= $row['desc'] ?></td>
                                    <td style="width:10%"><?= $row['attack_percent'] ?></td>
                                    <td style="width:15%"><?= $row['attack_count'] ?></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endforeach; ?>

                    </table>
                </div>
            </div>
        </div>
        <!-- 入侵类来源的攻击事件统计TOP50 end-->

        <!-- 攻击类型按被攻击主机统计 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('attackTypesAreCountedByTheAttackedHost') ?></h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:74%"><?= $translate->getTranslateBySymbol('url/ipAddress') ?></li>
                        <li style="width:10%" class="fold"><?= $translate->getTranslateBySymbol('proportion') ?></li>
                        <li style="width:15%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_type_host as $item): ?>
                            <tr>
                                <td class="t_c"><?= $item['desc'] ?></td>
                                <td></td>
                                <td class="t_r"><?= $translate->getTranslateBySymbol('total') ?>
                                    ：<?= $item['total'] ?></td>
                            </tr>
                            <?php foreach ($item['list'] as $key => $row): ?>
                                <tr>
                                    <td style="width:73%"><?= $row['attack_host'] ?></td>
                                    <td style="width:10%"><?= $row['attack_percent'] ?></td>
                                    <td style="width:15%"><?= $row['attack_count'] ?></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endforeach; ?>

                    </table>
                </div>
            </div>
        </div>
        <!-- 攻击类型按被攻击主机统计 end-->

        <!-- 被攻击主机的攻击类型统计 TOP50 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('attackTypeStatisticsOfTheAttackedHost') ?>
                TOP50</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:74%"><?= $translate->getTranslateBySymbol('attackType') ?></li>
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('proportion') ?></li>
                        <li style="width:15%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_type_host_top50 as $item): ?>
                            <tr>
                                <td class="t_c"><?= $item['host'] ?></td>
                                <td></td>
                                <td class="t_r"><?= $translate->getTranslateBySymbol('total') ?>
                                    ：<?= $item['total'] ?></td>
                            </tr>
                            <?php foreach ($item['list'] as $key => $row): ?>
                                <tr>
                                    <td style="width:73%"><?= $row['desc'] ?></td>
                                    <td style="width:10%"><?= $row['attack_percent'] ?></td>
                                    <td style="width:15%"><?= $row['attack_count'] ?></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endforeach; ?>

                    </table>
                </div>
            </div>
        </div>
        <!-- 被攻击主机的攻击类型统计 TOP50 end-->

        <!-- 攻击类型按被攻击URL的统计 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('attackTypeAccordingToTheStatisticsOfTheAttackedUrl') ?></h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:74%">URL</li>
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('proportion') ?></li>
                        <li style="width:15%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_type_url as $item): ?>
                            <tr>
                                <td class="t_c"><?= $item['desc'] ?></td>
                                <td></td>
                                <td class="t_r"><?= $translate->getTranslateBySymbol('total') ?>
                                    ：<?= $item['total'] ?></td>
                            </tr>
                            <?php foreach ($item['list'] as $key => $row): ?>
                                <tr>
                                    <td style="width:73%"><?= htmlspecialchars($row['attack_url']) ?></td>
                                    <td style="width:10%"><?= $row['attack_percent'] ?></td>
                                    <td style="width:15%"><?= $row['attack_count'] ?></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endforeach; ?>

                    </table>
                </div>
            </div>
        </div>
        <!-- 攻击类型按被攻击URL的统计 end-->

        <!-- 被攻击URL的攻击类型统计 TOP50 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('attackTypeStatisticsOfAttackedUrl') ?>
                TOP50</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:74%"><?= $translate->getTranslateBySymbol('attackType') ?></li>
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('proportion') ?></li>
                        <li style="width:15%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_type_url_top50 as $item): ?>
                            <tr>
                                <td class="t_c"><?= htmlspecialchars($item['url']) ?></td>
                                <td></td>
                                <td class="t_r"><?= $translate->getTranslateBySymbol('total') ?>
                                    ：<?= $item['total'] ?></td>
                            </tr>
                            <?php foreach ($item['list'] as $key => $row): ?>
                                <tr>
                                    <td style="width:73%"><?= $row['desc'] ?></td>
                                    <td style="width:10%"><?= $row['attack_percent'] ?></td>
                                    <td style="width:15%"><?= $row['attack_count'] ?></td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endforeach; ?>

                    </table>
                </div>
            </div>
        </div>
        <!-- 被攻击URL的攻击类型统计 TOP50 end-->

        <!-- 被攻击主机统计 TOP50 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('attackHostStatistics') ?> TOP50</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('serialNumber') ?></li>
                        <li style="width:74%"><?= $translate->getTranslateBySymbol('url/ipAddress') ?></li>
                        <li style="width:15%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_host_top50 as $key => $row): ?>
                            <tr>
                                <td style="width:10%"><?= $key + 1 ?></td>
                                <td style="width:73%"><?= $row['attack_host'] ?></td>
                                <td style="width:15%"><?= $row['total'] ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 被攻击主机统计 TOP50 end-->

        <!-- 被攻击URL统计 TOP50 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('attackUrlStatistics') ?> TOP50</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('serialNumber') ?></li>
                        <li style="width:74%">URL</li>
                        <!--<li style="width:20%" class="fold">(攻击类别)百分比</li>-->
                        <li style="width:17%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_host_url_top50 as $key => $row): ?>
                            <tr>
                                <td style="width:10%"><?= $key + 1 ?></td>
                                <td style="width:73%"><?= htmlspecialchars($row['attack_url']) ?></td>
                                <td style="width:15%"><?= $row['total'] ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </table>
                </div>
            </div>
        </div>
        <!-- 被攻击URL统计 TOP50 end-->

        <!-- 被攻击URL统计(含参数) TOP50 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('attackedUrlStatistics(including parameters)') ?>
                TOP50</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('serialNumber') ?></li>
                        <li style="width:74%">URL</li>
                        <!--<li style="width:20%" class="fold">(攻击类别)百分比</li>-->
                        <li style="width:17%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_host_url_top50 as $key => $row): ?>
                            <tr>
                                <td style="width:10%"><?= $key + 1 ?></td>
                                <td style="width:73%"><?= htmlspecialchars($row['attack_host'] . $row['attack_url'] . $row['attack_query']) ?></td>
                                <td style="width:15%"><?= $row['total'] ?></td>
                            </tr>
                        <?php endforeach; ?>

                    </table>
                </div>
            </div>
        </div>
        <!-- 被攻击URL统计(含参数) TOP50 end-->

        <!-- 非法外联 TOP50 start-->
        <div class="chart_box">
            <h2 class="chart_title"><?= $translate->getTranslateBySymbol('illegalOutLink') ?> TOP50</h2>
            <div class="list-content">
                <div class="list-conhead">
                    <ul class="list-ul">
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('serialNumber') ?></li>
                        <li style="width:30%"><?= $translate->getTranslateBySymbol('sourceIpAddress') ?></li>
                        <li style="width:30%"><?= $translate->getTranslateBySymbol('targetIp') ?></li>
                        <li style="width:20%"><?= $translate->getTranslateBySymbol('geographicalPosition') ?></li>
                        <li style="width:10%"><?= $translate->getTranslateBySymbol('frequency') ?></li>
                    </ul>
                </div>
                <div class="list-conbody">
                    <table width="100%" class="table-con">
                        <?php foreach ($attack_out_links as $key => $row): ?>
                            <tr>
                                <td style="width:10%"><?= $key + 1 ?></td>
                                <td style="width:30%"><?= $row['source_ip'] ?></td>
                                <td style="width:30%"><?= $row['destination_ip'] ?></td>
                                <td style="width:20%"><?= $row['location'] ?></td>
                                <td style="width:10%"><?= $row['total'] ?></td>
                            </tr>
                        <?php endforeach; ?>

                    </table>
                </div>
            </div>
        </div>
        <!-- 非法外联 TOP50 end-->

    </div>
    <!-- chart_main end -->
</div><!-- chart_wrap end -->

<!-- 引入 ECharts 文件 -->
<script type="text/javascript" src="./plugins/echarts-all.js"></script>
<script type="text/javascript">
    $(function () {
        $(document).ready(function () {
            rqslChartBar();
            rqqsChartLine();
            rqqstimeChartLine();
            rqlbChartBar();
            rqlbChartPie();
        });
    });

    //入侵数量统计图
    function rqslChartBar() {
        var rqslChartBar = echarts.init(document.getElementById('rqslChartBar'));
        rqslChartBarOption = {
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
                    data: ['<?=$translate->getTranslateBySymbol('prompt')?>',
                        '<?=$translate->getTranslateBySymbol('warn')?>',
                        '<?=$translate->getTranslateBySymbol('error')?>',
                        '<?=$translate->getTranslateBySymbol('serious')?>',
                        '<?=$translate->getTranslateBySymbol('alert')?>',
                        '<?=$translate->getTranslateBySymbol('urgent')?>']
                }
            ],
            series: [
                {
                    name: '<?=$translate->getTranslateBySymbol('invadeCountStatistics')?>',
                    type: 'bar',
                    barMaxWidth: 30,
                    itemStyle: {
                        normal: {
                            color: function (params) {
                                // build a color map as your need.
                                var colorList = [
                                    "#89c24d", "#3eb7fe", "#a667dc", "#ffc700", "#ff7143", "#03bdd6"
                                ];
                                return colorList[params.dataIndex]
                            },
                            label: {show: true, position: 'right'}
                        }
                    },
                    data: [<?=implode(',', $attack_num_level)?>]
                }
            ]
        };
        rqslChartBar.setOption(rqslChartBarOption);
    }

    //入侵趋势图
    function rqqsChartLine() {
        var rqqsChartLine = echarts.init(document.getElementById('rqqsChartLine'));
        rqqsChartLineOption = {
            color: ["#3eb7fe"],
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
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: [
                    <?php
                    //趋势日期
                    $tread_date = '';
                    foreach ($attack_date_trend_list as $row) {
                        $item = explode('-', $row['alert_date']);
                        $tread_date .= "'$item[1]/$item[2]',";
                    }
                    $tread_date = substr($tread_date, 0, -1);
                    echo $tread_date;
                    ?>
                ],
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
                    name: '<?=$translate->getTranslateBySymbol('invadeTrend')?>',
                    type: 'line',
                    itemStyle: {
                        normal: {
                            label: {show: true, position: 'top'}
                        }
                    },
                    data: [<?=implode(',', $attack_date_trend)?>]
                }
            ]
        };
        rqqsChartLine.setOption(rqqsChartLineOption);
    }

    //入侵趋势图(24小时时间段)
    function rqqstimeChartLine() {
        var rqqstimeChartLine = echarts.init(document.getElementById('rqqstimeChartLine'));
        rqqstimeChartLineOption = {
            color: ["#3eb7fe"],
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                x: '8%',
                x2: '4%',
                y2: 100,
                y: '10%'
            },
            calculable: true,
            xAxis: [
                {
                    type: 'category',
                    axisLabel: {
                        rotate: '45',
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
                    splitLine: {show: false},
                    data: [<?="'" . implode("','", array_keys($attack_hour_trend)) . "'"?>]
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
                            color: "#555"
                        }, show: false
                    }
                }
            ],
            series: [
                {
                    name: 'Attack',
                    type: 'bar',
                    itemStyle: {
                        normal: {
                            color: '#ff7143',
                            label: {
                                show: true, position: 'top'
                            }
                        }
                    },
                    data: [<?=implode(',', $attack_hour_trend)?>]
                }
            ]
        };
        rqqstimeChartLine.setOption(rqqstimeChartLineOption);
    }

    //入侵类别统计图
    <?php
    $chart_type = [];
    $chart_type_pie = [];
    foreach ($attack_list_type as $row) {
        $chart_type[$row['desc']] = $row['attack_type_count'];
        $chart_type_pie[] = ['value' => $row['attack_type_count'], 'name' => $row['desc']];
    }
    $chart_type_pie = json_encode($chart_type_pie, JSON_UNESCAPED_UNICODE);
    ?>
    function rqlbChartBar() {
        var rqlbChartBar = echarts.init(document.getElementById('rqlbChartBar'));
        rqlbChartBarOption = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                },
                formatter: "{b}\n{c}"
            },
            grid: {
                x: '8%',
                x2: '4%',
                y2: 100,
                y: '10%'
                //containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    show: true,
                    data: [<?="'" . implode("','", array_keys($chart_type)) . "'"?>],
                    axisLabel: {
                        rotate: '45',
                        interval: 0,
                        margin: 10,
                        textStyle: {
                            fontSize: 12,
                            color: '#555'
                        }
                    },
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
                    type: 'value',
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
                    }
                }
            ],
            series: [
                {
                    name: '<?=$translate->getTranslateBySymbol('invadeClassStatistical')?>',
                    type: 'bar',
                    data: [<?=implode(',', $chart_type)?>],
                    barWidth: '30',
                    itemStyle: {
                        normal: {
                            color: function (params) {
                                // build a color map as your need.
                                var colorList = [
                                    "#03bdd6", "#89c24d", "#3eb7fe", "#a667dc", "#ffc700", "#ff7143", "#ffecb3", "#03bdd6", "#89c24d", "#3eb7fe", "#a667dc", "#ffc700", "#ff7143", "#ffecb3"
                                ];
                                return colorList[params.dataIndex]
                            },
                            label: {show: true, position: 'top'}
                        }
                    }

                }
            ]
        };
        rqlbChartBar.setOption(rqlbChartBarOption);
    }

    //入侵类别对比图
    function rqlbChartPie() {
        var rqlbChartPie = echarts.init(document.getElementById('rqlbChartPie'));

        rqlbChartPieOption = {
            //color:[ "#03bdd6","#89c24d","#3eb7fe","#a667dc","#ffc700","#ff7143","#ffecb3"],
            tooltip: {
                trigger: 'item',
                formatter: "{a} <br/>{b}: {c} ({d}%)"
            },
            animation: false,
            legend: {
                orient: 'vertical',
                x: 'right',
                textStyle: {
                    fontSize: 14,
                    fontWeight: 'normal',
                    color: '#95a4b1'
                },
                icon: 'circle',
                data: [<?="'" . implode("','", array_keys($chart_type)) . "'"?>]
            },
            series: [
                {
                    name: '<?=$translate->getTranslateBySymbol('invadeClassCompare')?>',
                    type: 'pie',
                    radius: ['30%', '45%'],
                    itemStyle: {
                        normal: {
                            label: {
                                show: true,
                                formatter: '{b} : {c} ({d}%)'
                            },
                            labelLine: {show: true}
                        }
                    },
                    data:
                    <?=$chart_type_pie;?>

                }
            ]
        };
        rqlbChartPie.setOption(rqlbChartPieOption);
    }
</script>
</body>
</html>