// JavaScript Document
        // 使用
        require(
            [
                'echarts',
				'echarts/chart/gauge' // 使用仪表盘就加载gauge模块，按需加载
            ],
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
				var myChart_cpu = ec.init(document.getElementById('chart_cpu')); 
				var myChart_nc = ec.init(document.getElementById('chart_nc')); 
				if (typeof window.addEventListener != "undefined") { 
				window.addEventListener('resize',function(){myChart_cpu.resize();},false); 
				} else { 
				window.attachEvent("onresize",function(){myChart_cpu.resize();}); 
				} 
				if (typeof window.addEventListener != "undefined") { 
				window.addEventListener('resize',function(){myChart_nc.resize();},false); 
				} else { 
				window.attachEvent("onresize",function(){myChart_nc.resize();}); 
				} 

//CPU				
  option_cpu = {
    tooltip : {
        formatter: "{a} <br/>{b} : {c}%"
    },
    
    series : [
        {
            name:'CPU利用率',
            type:'gauge',
			radius :[0,'100%'],
            detail : {formatter:'{value}%'},
            data:[{value: 30, name: 'CPU'}],
			axisLine:{show: true,
   				 lineStyle: {
       				 color: [
							[0.2, '#228b22'],
							[0.8, '#48b'],
							[1, '#ff4500']
        				], 
       				 width: 13
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

//内存				
  option_nc = {
    tooltip : {
        formatter: "{a} <br/>{b} : {c}%"
    },
    
    series : [
        {
            name:'内存利用率',
            type:'gauge',
			radius :[0,'100%'],
            detail : {formatter:'{value}%'},
            data:[{value: 50, name: '内存'}],
			axisLine:{show: true,
   				 lineStyle: {
       				 color: [
							[0.2, '#228b22'],
							[0.8, '#48b'],
							[1, '#ff4500']
        				], 
       				 width: 13
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
clearInterval(timeTicket);
var timeTicket = setInterval(function (){
    option_cpu.series[0].data[0].value = (Math.random()*100).toFixed(2) - 0;
    myChart_cpu.setOption(option_cpu, true);
    option_nc.series[0].data[0].value = (Math.random()*100).toFixed(2) - 0;
    myChart_nc.setOption(option_nc, true);	
},2000);

																													
				myChart_cpu.setOption(option_cpu); 
				myChart_nc.setOption(option_nc); 
			
 });
		
		
		
