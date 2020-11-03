;
(function ($) {
    $.PhpUrl = function (sStr) {

        if (window != top) {
            return "../" + sStr;
        } else {
            return "./" + sStr;
        }

    }
    $.download = function (url, data, method) {
        // 获取url和data
        if (url && data) {
            // data 是 string 或者 array/object
            data = typeof data == 'string' ? data : jQuery.param(data);
            // 把参数组装成 form的  input
            var inputs = '';
            jQuery.each(data.split('&'), function () {
                var pair = this.split('=');
                inputs += '<input type="hidden" name="' + pair[0] + '" value="' + pair[1] + '" />';
            });
            // request发送请求
            jQuery('<form action="' + url + '" method="' + (method || 'post') + '">' + inputs + '</form>')
                .appendTo('body').submit().remove();
        };
    };
    $.printGrid = function(){
        $('.l-grid').height(1200);
        $('.l-grid-body').height(1200);
        $('.l-grid-body').css('overflow','hidden');
        $( '.l-panel-bwarp' ).printArea( {
            popTitle:'',
            extraCss:'' } );

        $('.l-grid').height('auto');
        $('.l-grid-body').height('auto');
        $('.l-grid-body').css('overflow','auto');
        $('.l-grid-body').css('overflow-x','hidden');
    }
    $.obj2string =function(o){
        var r=[];
        if(typeof o=="string"){
            return "\""+o.replace(/([\'\"\\])/g,"\\$1").replace(/(\n)/g,"\\n").replace(/(\r)/g,"\\r").replace(/(\t)/g,"\\t")+"\"";
        }
        if(typeof o=="object"){
            if(!o.sort){
                for(var i in o){
                    r.push(i+":"+ $.obj2string(o[i]));
                }
                if(!!document.all&&!/^\n?function\s*toString\(\)\s*\{\n?\s*\[native code\]\n?\s*\}\n?\s*$/.test(o.toString)){
                    r.push("toString:"+o.toString.toString());
                }
                r="{"+r.join()+"}";
            }else{
                for(var i=0;i<o.length;i++){
                    r.push($.obj2string(o[i]))
                }
                r="["+r.join()+"]";
            }
            return r;
        }
        return o.toString();
    }
    $.format = function (source, params) {
        if (arguments.length == 1)
            return function () {
                var args = $.makeArray(arguments);
                args.unshift(source);
                return $.format.apply(this, args);
            };
        if (arguments.length > 2 && params.constructor != Array) {
            params = $.makeArray(arguments).slice(1);
        }
        if (params.constructor != Array) {
            params = [params];
        }
        $.each(params, function (i, n) {
            source = source.replace(new RegExp("\\{" + i + "\\}", "g"), n);
        });
        return source;
    };
    function getParentWin() {
        /*var $doc;
        if (window.location != window.parent.location) {
            $doc = window.parent.jQuery.noConflict();
        } else {
            // <SPAN style="COLOR: #ff0000">页面单独打开</SPAN>
            $doc = jQuery.noConflict();
        }
		console.log($doc)
        return 600*/
    }

    var $doc = getParentWin();
    $.Layer = function (opt) {
        var html = $(opt.el);
        var el = html;//$doc(html);
        var opt = $.extend({
            autoOpen: false,
            modal: true,
            resizable: false,
            minHeight: 200,
            show: {
                effect: "fade",
                duration: 500
            },
            hide: {
                effect: "scale",
                duration: 300
            },
            buttons: {
                '确定': function (e) {
                    el.trigger('ok');
                    e.stopPropagation();
                },
                '关闭': function (e) {
                    el.dialog("close");
                    el.trigger('close');
                    e.stopPropagation();
                }
            }
        }, opt);
        return el.dialog(opt);
    }

    $.Layer.alert = function (opt) {
        return $.dialog.alert(opt.msg, function () {
            opt.fn && opt.fn.call();
        });
    }
    $.Layer.confirm = function (opt) {
        return $.dialog.confirm(opt.msg, function () {
            opt.fn && opt.fn.call();
        }, function () {
            opt.fn2 && opt.fn2.call();
        });
    }

    /*------- (2017-7-12) ---------*/
    $.Layer.notice = function(opt){
        var opt = $.extend({
            icon: 'warning',
            content: '',
            time: 5
        }, opt);
        return art.dialog.notice(opt);
    }
    /*------- (2017-7-12) ---------*/

    $.Layer.iframe = function (opt) {
        var opt = $.extend({
            lock: true,
            width: 'auto', height: 'auto',
            button: [{
                name: '提交',
                callback: function () {
                    $d.DOM.wrap.trigger('ok');
                    return false;
                },
                disabled: false,
                className: 'bt_sub',
                focus: true
            }],
            cancel: function () {
            }

        }, opt);
        if ($.dialog.top != window) {
            opt.url = opt.url.replace('..', '.');
        }
        var $d = $.dialog.open(opt.url, opt);
        top.getDialog = function () {
            return $d;
        }
        return $d;
    }
    /** * 对Date的扩展，将 Date 转化为指定格式的String * 月(M)、日(d)、12小时(h)、24小时(H)、分(m)、秒(s)、周(E)、季度(q)
     可以用 1-2 个占位符 * 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字) * eg: * (new
     Date()).pattern("yyyy-MM-dd hh:mm:ss.S")==> 2006-07-02 08:09:04.423
     * (new Date()).pattern("yyyy-MM-dd E HH:mm:ss") ==> 2009-03-10 二 20:09:04
     * (new Date()).pattern("yyyy-MM-dd EE hh:mm:ss") ==> 2009-03-10 周二 08:09:04
     * (new Date()).pattern("yyyy-MM-dd EEE hh:mm:ss") ==> 2009-03-10 星期二 08:09:04
     * (new Date()).pattern("yyyy-M-d h:m:s.S") ==> 2006-7-2 8:9:4.18
     */
    Date.prototype.pattern = function (fmt) {
        var o = {
            "M+": this.getMonth() + 1, //月份
            "d+": this.getDate(), //日
            "h+": this.getHours() % 12 == 0 ? 12 : this.getHours() % 12, //小时
            "H+": this.getHours(), //小时
            "m+": this.getMinutes(), //分
            "s+": this.getSeconds(), //秒
            "q+": Math.floor((this.getMonth() + 3) / 3), //季度
            "S": this.getMilliseconds() //毫秒
        };
        var week = {
            "0": "/u65e5",
            "1": "/u4e00",
            "2": "/u4e8c",
            "3": "/u4e09",
            "4": "/u56db",
            "5": "/u4e94",
            "6": "/u516d"
        };
        if (/(y+)/.test(fmt)) {
            fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
        }
        if (/(E+)/.test(fmt)) {
            fmt = fmt.replace(RegExp.$1, ((RegExp.$1.length > 1) ? (RegExp.$1.length > 2 ? "/u661f/u671f" : "/u5468") : "") + week[this.getDay() + ""]);
        }
        for (var k in o) {
            if (new RegExp("(" + k + ")").test(fmt)) {
                fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
            }
        }
        return fmt;
    }


//全局的ajax访问，处理ajax清求时sesion超时
    $.ajaxSetup({
        contentType: "application/x-www-form-urlencoded;charset=utf-8",
        complete: function (XMLHttpRequest, textStatus) {
            if (textStatus == 'parsererror' && XMLHttpRequest.responseText == 'sFLgSessionTimeOut') {
                //如果超时就处理 ，指定要跳转的页面
                if (window != top) {
                    top.location.href = "/"; //session超时跳转
                }
            }
        }
    });
})(jQuery);
//格式化时间戳
function formatDate(value) {
    var d = new Date(parseInt(value)*1000);
    var year=d.getFullYear();
    var month=(d.getMonth()+1)<10?'0'+(d.getMonth()+1):(d.getMonth()+1);
    var day=d.getDate()<10?'0'+d.getDate():d.getDate();
    var hour=d.getHours()<10?'0'+d.getHours():d.getHours();
    var minute=d.getMinutes()<10?'0'+d.getMinutes():d.getMinutes();
    var second=d.getSeconds()<10?'0'+d.getSeconds():d.getSeconds();
    return year+"-"+month+"-"+day+" "+hour+":"+minute+":"+second;
}