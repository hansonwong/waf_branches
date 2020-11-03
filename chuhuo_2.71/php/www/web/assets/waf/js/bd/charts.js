;(function($){  //避免全局依赖,避免第三方破坏
    /*采用对象化进行封接*/
    Array.prototype.max = function(){//调用数中带有较大的值的那个数。JS默认设置
        return Math.max.apply({},this)
    }
    Array.prototype.min = function(){//调用数中带有较小的值的那个数。JS默认设置
        return Math.min.apply({},this)
    }

    $.fn.BDChats = function(opt){
        var option = $.extend({}, $.fn.BDChats.defaults,opt),me=this;
		
        if(!option.url && !option.hParams){
            alert("请配置加载图表数据请求地址");
            return false;
        }
        /*调用扩展方法*/
		//刷新按钮事件
        var reload  = function(url,hParams){
            var charts =this;
            if(typeof url  ==  "object"){
                charts.setOption($.extend(true,option,{series:data}));
            }else{
                $.post(url,hParams||{},function(data){
                    charts.setOption($.extend(true,option,{series:data}));
                },"json");
            }
        };
        var w = option.iWidth || 780;
        var h = option.iHeight || 600;
        $(me).css('height',h);
        $(me).css('width',w);

        function __init__(data){
            return me.each(function() {//因为对象化可能有0个以上的实例
                $this = $(this); //转化为jQuery对象
                var charts = echarts.init(this);
                option.loading && charts.showLoading({
                    text : "图表数据正在努力加载..."
                });

				//console.log(charts);
                //报表自适应
                if(data.length >0){
                    $(window).resize(function(){
                        ;charts._zr !== null && charts.resize()
                    });
                    charts.setOption($.extend(true,option,{series:data}));
                } else{
                    $(window).resize(function(){
                        ;charts._zr !== null && charts.resize()

                    });
                    charts.setOption(option);
                }
                //窗口伸缩结束
                 xi = data.max()/138;
                for(var i = 0; i < data.length; i++){
                    if(data[i] < xi && data[i] != 0){
                        data[i] = xi
                    }
                }


				if(option.openUrl){
					var ecConfig = require('echarts/config'); 
					charts.on(ecConfig.EVENT.CLICK, option.optUrl);
				}
				if(option.isWorld){
					charts.addMarkPoint(0,option.addWorldmark);
				}
                option.loading && charts.hideLoading();
                /*扩展方法*/
                $.extend(charts,{
                    reload : reload
                });
                /*注册事件*/
                setTimeout(function(){$this.trigger('afterrender',[charts,$this,option])},500);

            });
        }
        if(option.noAjax){
            return  __init__([]);


        }else{
            $.post(option.url,option.hParams||{},function(data){

               return  __init__(data);

            },"json");
        }


    };
    /*opt 配置参数可以使用第三方的API，因为是继承第三方的插件，还是自定义配置参数*/
    /*http://echarts.baidu.com/echarts2/doc/option.html#title~ API*/
    /*默认配置参数*/
    $.fn.BDChats.defaults = {
       iWidth:'98%',
       iHeight:240,
        noAjax:false, //使用后台请求数据
        loading : true, //加载层
        hParams :{} //提交的参数

    };
    /*调用*/
    /*
     $('.charts').BDChats({

     }).on('afterrender',function(e,charts,el){
         var a = charts.getDatas(); //调用扩展方法
         console.log(a);
     });
     */

})(jQuery);