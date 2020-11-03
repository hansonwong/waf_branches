            var TimeDistributeChart = echarts.init(document.getElementById('TimeDistribute'));
            var responseTimeChart = echarts.init(document.getElementById('responseTime')); 
            var urlstatusChart = echarts.init(document.getElementById('urlstatus'));  

            var TimeDistributeOption = {
                tooltip : {
                    trigger: 'axis',
                    axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                        type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                    }
                },
                grid: {
                    x: '10%',
                    x2: '10%',
                    y: '10%',
                    y2: '30%',
                    containLabel: true
                },                 
                xAxis : [
                    {
                        type : 'category',
                        data : ['0ms~100ms','100ms~500ms',"500ms~1000ms","1s~10s","10s~30s","30s~60s","60s~180s","300s以上"]
                    }
                ],
                yAxis : [
                    {
                        type : 'value'
                    }
                ],
                series : [
                    {
                        name:'总数',
                        type:'bar',
                        data:[10, 52,20,60,100,50,120]
                    }
                ]
            };

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
                        splitLine:{show:false},
                        type:"category",
                        axisLabel:{interval:0,rotate:70},
                        data:[   '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00','00:00-01:00', '00:00-01:00']
                    }

                ],
                yAxis: {
                    name: '时间',
                    type: 'value',
                    axisLabel: {
                        formatter: '{value} ms'
                    }
                },
                series: [
                    {
                        name: '响应时间',
                        type: 'line',
                        data:[120, 132, 101, 134, 90, 230, 210]
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
                    splitLine: {show: false},
                    data: ['01', '02', '03', '04', '05', '06', '07', '08', '09','10','11','12','13','14','15','16','17','18','19','20']
                },
                grid: {
                    x: '10%',
                    x2: '10%',
                    y: '10%',
                    y2: '30%',
                    containLabel: true
                }, 
                yAxis: {
                    name: 'y',
                    type: 'value',
                    axisLabel: {
                        formatter: '{value}'
                    }
                },
                series: [
                    {
                        name: '正常',
                        type: 'line',
                        data: [0,10,20,30,40,20,60,80],
                    },
                    {
                        name: '不可用',
                        type: 'line',
                        data: [10,20,40,70,80,60,40,10],
                    }                    
                ]
            };

            TimeDistributeChart.setOption(TimeDistributeOption);
            responseTimeChart.setOption(responseTimeOption);
            urlstatusChart.setOption(urlstatusOption);




