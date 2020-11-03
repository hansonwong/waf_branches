// JavaScript Document
       
        // 使用
        require(
            [
                'echarts',
                'echarts/chart/line' // 使用柱状图就加载bar模块，按需加载
            ],
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
                var myChartLine = ec.init(document.getElementById('chart_line')); 
				if (typeof window.addEventListener != "undefined") { 
				window.addEventListener('resize',function(){myChartLine.resize();},false); 
				} else { 
				window.attachEvent("onresize",function(){myChartLine.resize();}); 
				} 
	
option = {
    title : {
        text: '流量监控',
		textStyle :{fontSize:14,color:'#555'}
       
    },
    tooltip : {
        trigger: 'axis'
    },
    legend: {
        data:['流入','流出'],
		textStyle :{fontSize:12,color:'#555'}
    },
    calculable : true,
	grid:{
		x:40,
		y:40,
		x2:30,
		y2:30,
		borderColor: '#fafafa'
		},
    xAxis : [
        {
            type : 'category',
            boundaryGap : false,
           data : ['0','2','4','6','8','10','12','14','16','18','20','22','24']
        }
    ],
    yAxis : [
        {
            type : 'value'
        }
    ],
    series : [
        {
            name:'流入',
            type:'line',
            smooth:true,
            itemStyle: {normal: {areaStyle: {type: 'default'}}},
          data:[10, 12, 21, 54, 260, 830, 710, 50, 200, 600, 680, 700, 750]
        },
        {
            name:'流出',
            type:'line',
            smooth:true,
            itemStyle: {normal: {areaStyle: {type: 'default'}}},
            data:[30, 182, 434, 791, 390, 30, 10,182, 434, 791, 390, 30, 10]
        }
    ]
};
                            
			// 为echarts对象加载数据 
			myChartLine.setOption(option); 
            }
);
		
		
		
