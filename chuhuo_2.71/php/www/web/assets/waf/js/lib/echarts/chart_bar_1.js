// JavaScript Document
var xAxisData = new Array();
var seriesColor = new Array();
var seriesData = new Array();

var BARxAxis = new Array();
var serColor = new Array();
var seriesData1 = new Array();
var titleBar1 =  new Array();
var UrlBar1 =  new Array();

$.ajaxSettings.async = false;
$.getJSON("../js/data/bar1.json", function (jsonArray) { 
	for(var key in jsonArray.serData){
		seriesData[key] = jsonArray.serData[key];
		xAxisData[key] = seriesData[key].ipdz;
		seriesColor[key] = seriesData[key].color;
	};
});  
$.getJSON("../js/data/bar2.json", function (jsonBar) { 
	for(var x in jsonBar.serData){
		seriesData1[x] = jsonBar.serData[x].value;
		BARxAxis[x] = jsonBar.serData[x].axis;
		serColor[x] = jsonBar.serData[x].color;
		titleBar1[x] = jsonBar.serData[x].title;
		UrlBar1[x] = jsonBar.serData[x].url;
	};
}); 

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
		'echarts/chart/bar' // 使用柱状图就加载bar模块，按需加载
	],
function (ec) {
	// 基于准备好的dom，初始化echarts图表
	var m = document.getElementById('chart_bar1')
	var myChartBar1 = ec.init(document.getElementById('chart_bar1'));
	var myChartBar2 = ec.init(document.getElementById('chart_bar2'));
	var myChartBar3 = ec.init(document.getElementById('chart_bar3'));
	if (typeof window.addEventListener != "undefined") { 
	window.addEventListener('resize',function(){myChartBar1.resize();},false); 
	} else { 
	window.attachEvent("onresize",function(){myChartBar1.resize();}); 
	} 
	if (typeof window.addEventListener != "undefined") { 
	window.addEventListener('resize',function(){myChartBar2.resize();},false); 
	} else { 
	window.attachEvent("onresize",function(){myChartBar2.resize();}); 
	} 
	if (typeof window.addEventListener != "undefined") { 
	window.addEventListener('resize',function(){myChartBar3.resize();},false); 
	} else { 
	window.attachEvent("onresize",function(){myChartBar3.resize();}); 
} 

//活跃主机统计
option1 = {
   
    tooltip: {
		show: true,
        trigger: 'axis',
		formatter: function(params,ticket,callback){
			var res = '<b>设备编号：</b>' + params[0].data.sbid;
				res += '<br/><b>所属单位：</b>' + params[0].data.dw;
				res += '<br/><b>用户名：</b>' + params[0].data.un;
				res += '<br/><b>所属部门：</b>' + params[0].data.bm;
				res += '<br/><b>终端名称：</b>' + params[0].data.zz;
				res += '<br/><b>IP外联IP数：</b>' + params[0].data.value;
				res += '<br/><b>总流量：</b>' + params[0].data.zll;
				res += '<br/><b>是否在线：</b>' + params[0].data.sfzx;
			setTimeout(function (){
				callback(ticket, res);
			}, 800)
			return 'loading';	
		}
	   },
  
    calculable: true,
    grid:{
			x:40,
			y:40,
			x2:30,
			y2:30,
			borderColor: '#fafafa'
		},
    xAxis: [
        {
            type: 'category',
            data: xAxisData
        }
    ],
    yAxis: [
        {
            type: 'value',
			name:'按外联IP数'
        }
    ],
	
    series: [
        {
            name: '活跃主机统计',
            type: 'bar',
            itemStyle: {
                normal: {   
                    //label: {
//                        show: true,
//                        position: 'top',
//                        formatter: '{b}\n{c}'
//                    },
				color: function(params) {
                        // build a color map as your need.
                        var colorList = seriesColor;
						//alert(params.dataIndex);
                        return colorList[params.dataIndex]
                    }
                }
            },
			 data:seriesData
        }
    ]
};
//言论型涉密事件统计                                        
option2 = {
   
    tooltip: {
        trigger: 'item'
    },
  
    calculable: true,
    grid:{
			x:40,
			y:40,
			x2:30,
			y2:30,
			borderColor: '#fafafa'
		},
    xAxis: [
        {
            type: 'category',
            data: BARxAxis
        }
    ],
    yAxis: [
        {
            type: 'value'
        }
    ],
    series: [
        {
            name: '言论型涉密事件统计',
            type: 'bar',
            itemStyle: {
                normal: {   
                    //label: {
//                        show: true,
//                        position: 'top',
//                        formatter: '{b}\n{c}'
//                    },
					 color: function(params) {
                        // build a color map as your need.
                        var colorList =serColor;
                        return colorList[params.dataIndex]
                    }
                }
            },
            data: seriesData1
  
        }
    ]
};
var ecConfig = require('echarts/config');
function eConsole(param) {
  var n = param.dataIndex;
  var dialog = $.Layer.iframe(
		{
			title: titleBar1[n],
			url:UrlBar1[n],
			width: 900,
			height: 550,
			button:false
		});
}

//文件型涉密事件统计                                        
option3 = {
   
    tooltip: {
        trigger: 'item'
    },
  
    calculable: true,
    grid:{
			x:40,
			y:40,
			x2:30,
			y2:30,
			borderColor: '#fafafa'
		},
    xAxis: [
        {
            type: 'category',
            data: ['境内邮件', '境外邮件', '即时通信','网盘','FTP','HTTP上传','其它']
        }
    ],
    yAxis: [
        {
            type: 'value'
        }
    ],
    series: [
        {
            name: '文件型涉密事件统计',
            type: 'bar',
            itemStyle: {
                normal: {   
                    //label: {
//                        show: true,
//                        position: 'top',
//                        formatter: '{b}\n{c}'
//                    },
					 color: function(params) {
                        // build a color map as your need.
                        var colorList = [
                          '#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa'
                        ];
                        return colorList[params.dataIndex]
                    }
                }
            },
            data: [100,10,150,120,200,50,82]
          
            
        }
    ]
};
var ecConfig = require('echarts/config');
function eConsole1(param) {
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
            case 1:  //柱子2
                var dialog = $.Layer.iframe(
				{
					title: '查看详情1',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 2:  //柱子3
               var dialog = $.Layer.iframe(
				{
					title: '查看详情1',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 3:    //柱子4
              var dialog = $.Layer.iframe(
				{
					title: '查看详1情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});

                break;
            case 4:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看详1情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 5:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看1详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 6:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看1详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            default:
                break;
               
        }


}


			
			myChartBar1.on(ecConfig.EVENT.CLICK, eConsole);		                            
			myChartBar2.on(ecConfig.EVENT.CLICK, eConsole);
			myChartBar3.on(ecConfig.EVENT.CLICK, eConsole1);
			// 为echarts对象加载数据 
			myChartBar1.setOption(option1);
			myChartBar2.setOption(option2);
			myChartBar3.setOption(option3);


			
    }
   );
   
		
		
