// JavaScript Document
        // 使用
require(
	[
		'echarts',
		'echarts/chart/bar' // 使用柱状图就加载bar模块，按需加载
	],
	function (ec) {
		// 基于准备好的dom，初始化echarts图表
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
		formatter: function (params,ticket,callback) {
           
          //console.log(params);
          	var res = '<b>设备编号：</b>' + params[0].data.sbid;
				res += '<br/><b>所属单位：</b>' + params[0].data.dw;
				res += '<br/><b>用户名：</b>' + params[0].data.un;
				res += '<br/><b>所属部门：</b>' + params[0].data.bm;
				res += '<br/><b>终端名称：</b>' + params[0].data.zz;
				res += '<br/><b>IP外联IP数：</b>' + params[0].data.value;
				res += '<br/><b>总流量：</b>' + params[0].data.zll;
				res += '<br/><b>是否在线：</b>' + params[0].data.sfzx;
          
           
            setTimeout(function (){
                // 仅为了模拟异步回调
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
            data: ['172.16.1.51', '172.16.1.52', '172.16.1.53','172.16.1.54','172.16.1.55','172.16.1.56','172.16.1.57','172.16.1.58','172.16.1.59','172.16.1.60']
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
                        var colorList = [
                          '#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa'
                        ];
                        return colorList[params.dataIndex]
                    }
                }
            },
			 data:[
                {value:200, sbid:'编号1',dw:'单位1',un:'李三',bm:'技术规划部',zz:'JG-XXXX',ipdz:'172.168.2.53',zll:'1204M',sfzx:'在线'},
				{value:332, sbid:'编号2',dw:'单位2',un:'李旺',bm:'开发部',zz:'JG-XXX1',ipdz:'172.168.2.53',zll:'1204M',sfzx:'在线'},
				{value:301, sbid:'编号3',dw:'单位3',un:'李财',bm:'生产部',zz:'JG-XXX2',ipdz:'172.168.2.53',zll:'1204M',sfzx:'在线'},
				{value:334, sbid:'编号4',dw:'单位4',un:'李定',bm:'行政部',zz:'JG-XXX3',ipdz:'172.168.2.53',zll:'1204M',sfzx:'在线'},
				{value:390, sbid:'编号5',dw:'单位5',un:'李八',bm:'人事部',zz:'JG-XXX4',ipdz:'172.168.2.53',zll:'1204M',sfzx:'在线'},
				{value:330, sbid:'编号6',dw:'单位6',un:'李二',bm:'UE部',zz:'JG-XXX5',ipdz:'172.168.2.53',zll:'1204M',sfzx:'离线'},
				{value:320, sbid:'编号7',dw:'单位7',un:'李九',bm:'研发部',zz:'JG-XXX6',ipdz:'172.168.2.53',zll:'1204M',sfzx:'在线'},
				{value:390, sbid:'编号8',dw:'单位8',un:'李八',bm:'人事部',zz:'JG-XXX4',ipdz:'172.168.2.53',zll:'1204M',sfzx:'在线'},
				{value:330, sbid:'编号9',dw:'单位9',un:'李二',bm:'UE部',zz:'JG-XXX5',ipdz:'172.168.2.53',zll:'1204M',sfzx:'离线'},
				{value:320, sbid:'编号10',dw:'单位10',un:'李九',bm:'研发部',zz:'JG-XXX6',ipdz:'172.168.2.53',zll:'1204M',sfzx:'在线'}
            ]
          
            
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
            data: ['境内邮件', '境外邮件', '博客','微博','网络论坛','境外发贴','新闻组','其它']
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
                        var colorList = [
                          '#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa','#87cefa'
                        ];
                        return colorList[params.dataIndex]
                    }
                }
            },
            data: [100,10,150,120,200,50,82,98]
          
            
        }
    ]
};
var ecConfig = require('echarts/config');
function eConsole(param) {
  switch (param.dataIndex) {
	 
            case 0:    //柱子1
              var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});

                break;
            case 1:  //柱子2
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 2:  //柱子3
               var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 3:    //柱子4
              var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});

                break;
            case 4:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 5:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 6:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 7:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
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
function eConsole(param) {
  switch (param.dataIndex) {
	 
            case 0:    //柱子1
              var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});

                break;
            case 1:  //柱子2
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 2:  //柱子3
               var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 3:    //柱子4
              var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});

                break;
            case 4:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 5:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_zjxw.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 6:  //柱子5
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
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


					                            
			myChartBar2.on(ecConfig.EVENT.CLICK, eConsole);
			myChartBar3.on(ecConfig.EVENT.CLICK, eConsole);
			// 为echarts对象加载数据 
			myChartBar1.setOption(option1);
			myChartBar2.setOption(option2);
			myChartBar3.setOption(option3);


			
    }
   );
   
		
		
