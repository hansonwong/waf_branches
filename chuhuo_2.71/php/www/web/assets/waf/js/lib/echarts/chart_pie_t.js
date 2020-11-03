// JavaScript Document
// 路径配置
require.config({
	paths: {
		echarts: '../js/lib/echarts'
	}
});
// 使用
require(
[
	'echarts',
	'echarts/chart/pie' // 使用柱状图就加载bar模块，按需加载
],
function (ec) {
	// 基于准备好的dom，初始化echarts图表
	var myChartPie2 = ec.init(document.getElementById('chart_pie2')); 
	if (typeof window.addEventListener != "undefined") { 
	window.addEventListener('resize',function(){myChartPie2.resize();},false); 
	} else { 
	window.attachEvent("onresize",function(){myChartPie2.resize();}); 

} 

option2 = {
   
    tooltip : {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    calculable : true,
    series : [
        {
			name:'访问类型统计',
			type:'pie',
			radius :['0','75%'],
			center: ['50%', '50%'],
			data:[
				{value:205, name:'电子邮件'},
				{value:11, name:'电子邮件1'},
				{value:22, name:'电子邮2件'},
			]
        }
    ]
}; 
var m = option2.series[0].data.length; 

var ecConfig = require('echarts/config');
function eConsole(param) {
	//console.log(param[0].data);
  switch (param.dataIndex) {
            case 0:    //柱子1
              var dialog = $.Layer.iframe(
				{
					title: '查看详情1',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});

                break;
			case 1:    //柱子2
              var dialog = $.Layer.iframe(
				{
					title: '查看详情1',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});

                break;
			case 2:    //柱子3
              var dialog = $.Layer.iframe(
				{
					title: '查看详情1',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});

                break;
               
        }


};

                           
			myChartPie2.on(ecConfig.EVENT.CLICK, eConsole);
			// 为echarts对象加载数据
			myChartPie2.setOption(option2); 
			
            }
			
        );		
		
