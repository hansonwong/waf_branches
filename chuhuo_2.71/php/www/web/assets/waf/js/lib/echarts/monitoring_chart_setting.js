            var TimeDistributeChart = echarts.init(document.getElementById('TimeDistribute'));
            var responseTimeChart = echarts.init(document.getElementById('responseTime')); 
            var urlstatusChart = echarts.init(document.getElementById('urlstatus'));  
            var dataAll = [
                [
                    [0, 5.68]
                ]
            ];
            var TimeDistributeOption = {
                //color: ['#61a0a8'],
                title: {
                    show:false,
                    text: '响应时间分布',
                    left: 'center',
                    y:35,
                    textStyle:{
                        color:"#5c8de5",
                        fontWeight:"bold",
                        fontSize:16
                    },
                },
                tooltip : {
                    trigger: 'axis',
                    axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                        type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '10%',
                    containLabel: true,
                    height: '68%'
                },
                xAxis : [
                    {
                        type : 'category',
                        data : ['0ms~100ms','100ms~500ms',"500ms~1000ms","1s~10s","10s~30s","30s~60s","60s~180s","300s以上"],
                        axisTick: {
                            alignWithLabel: true
                        },
                        axisLine:{lineStyle:{color:"#888"}},
                    }
                ],
                yAxis : [
                    {
                        type : 'value',
                        max:120,
                        axisLine:{lineStyle:{color:"#888"}},
                    }
                ],
                series : [
                    {
                        name:'直接访问',
                        type:'bar',
                        barWidth: '60%',
                        data:[10, 52,20,60,100,50,120]
                    }
                ]
            };

            var responseTimeOption = {
                title: {
                    show:false,
                    text: '响应时间',
                    x: 'center',
                    y: 0,
                    textStyle:{
                        color:"#5c8de5",
                        fontWeight:"bold",
                        fontSize:16
                    },
                },
                grid: [
                    {x: '7%', y: '20%', width: '90%', height: '40%'},
                ],
                tooltip: {
                    show:false
                },
                xAxis: [
                    {gridIndex: 0,splitLine:{show:true},type:"category",axisLabel:{interval:0,rotate:70},data:[   '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00'],axisLine:{lineStyle:{color:"#888"}}}

                ],
                yAxis: [
                    {gridIndex: 0, min:0, max: 60,interval:20,axisLine:{lineStyle:{color:"#888"}}},
                ],
                series: [
                    {
                        name: 'I',
                        type: 'scatter',
                        xAxisIndex: 0,
                        yAxisIndex: 0,
                        data: dataAll[0],
                    }
                ]
            };

            var urlstatusOption = {
                textStyle:{color:"#888"},
                title: {
                    show:false,
                    text: '监控目标URL状态',
                    left: 'center',
                    textStyle:{
                        color:"#5c8de5",
                        fontWeight:"bold",
                        fontSize:16
                    },
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b} : {c}'
                },
                xAxis: {
                    type: 'category',
                    name: 'x',
                    axisLine:{lineStyle:{color:"#888"}},
                    splitLine: {show: false},
                    data: ['01', '02', '03', '04', '05', '06', '07', '08', '09','10','11','12','13','14','15','16','17','18','19','20']
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                yAxis: {
                    name: 'y',
                    type: 'value',
                    axisLine:{lineStyle:{color:"#888"}},
                    axisLabel: {
                        formatter: '{value} %'
                    },
                    max:100
                },
                series: [
                    {
                        name: '3的指数',
                        type: 'line',
                        data: [0,10,20,30,40,20,60,80],
                        symbol:"rect"
                    }
                ]
            };

            TimeDistributeChart.setOption(TimeDistributeOption);
            responseTimeChart.setOption(responseTimeOption);
            urlstatusChart.setOption(urlstatusOption);




