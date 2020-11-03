(function ($) {

    LayerAlert = function (opt) {
        $.Layer.alert(opt);
    }



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
      }, function () {
        opt.fn2 && opt.fn2.call();
      });
    }
    $.Layer.confirm = function (opt) {
        return $.dialog.confirm(opt.msg, function () {
            opt.fn && opt.fn.call();
        }, function () {
            opt.fn2 && opt.fn2.call();
        });
    }

    $.Layer.iframe = function (opt) {
        var opt = $.extend({
             lock: true,
            width: 'auto', height: 'auto',
            button: [{
                // name: '提交',
                name: baseLanguage.common.commit || baseLanguage.common.commit,
                callback: function () {
                    $d.DOM.wrap.trigger('ok');
                    return false;
                },
                disabled: false,
                className: 'bt_sub',
                focus: true
            }], cancel: function () {
            }
        }, opt);
        if($.dialog.top != window){
            opt.url = opt.url.replace('..','.');
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
})(jQuery);