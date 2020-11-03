// JavaScript Document
        // 使用
        require(
            [
                'echarts',
                'echarts/chart/pie' // 使用柱状图就加载bar模块，按需加载
            ],
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
                var myChartPie1 = ec.init(document.getElementById('chart_pie1')); 
                var myChartPie2 = ec.init(document.getElementById('chart_pie2')); 
				if (typeof window.addEventListener != "undefined") { 
				window.addEventListener('resize',function(){myChartPie1.resize();},false); 
				} else { 
				window.attachEvent("onresize",function(){myChartPie1.resize();}); 
				};
				 
				if (typeof window.addEventListener != "undefined") { 
				window.addEventListener('resize',function(){myChartPie2.resize();},false); 
				} else { 
				window.attachEvent("onresize",function(){myChartPie2.resize();}); 

				} 
option1 = {
   
    tooltip : {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    calculable : true,
    series : [
        {
			name:'报警类型分布图',
			type:'pie',
			radius :['0','75%'],
			center: ['50%', '50%'],
			data:[
				{value:205, name:'攻击窃密警报'},
				{value:110, name:'敏感言论涉密警报'},
				{value:80, name:'敏感文件涉密警报'},
			]
        }
    ]
};       

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
				{value:110, name:'即时通信'},
				{value:205, name:'微博'},
				{value:110, name:'论坛'},
				{value:80, name:'网盘'},
				{value:80, name:'其他'}
			]
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
					url:'list_mgyl.html',
					width: 900,
					height: 550,
					button:false
				});

                break;
            case 1:  //柱子2
                var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_mgyl.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 2:  //柱子3
               var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_mgyl.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 3:  //柱子3
               var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_mgyl.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 4:  //柱子3
               var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_mgyl.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            case 5:  //柱子3
               var dialog = $.Layer.iframe(
				{
					title: '查看详情',
					url:'list_mgyl.html',
					width: 900,
					height: 550,
					button:false
				});
                break;
            default:
                break;
               
        }


};

                           
			myChartPie2.on(ecConfig.EVENT.CLICK, eConsole);
			// 为echarts对象加载数据
			myChartPie1.setOption(option1);  
			myChartPie2.setOption(option2); 
			
            }
			
        );		
		
