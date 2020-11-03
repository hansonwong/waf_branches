//检测登录超时对象
var checkLoginTimeOut = {
    expireTime: null,
    init: function (url) {
        this.checkUrl = url;
        this.check();
        setInterval(this.check, 60000);
        setInterval(this.checkExpireTime, 1000);
    },
    checkUrl: '',
    check: function (async) {
        async = async || true;
        var obj = checkLoginTimeOut;
        $.ajax({
            url: obj.checkUrl,
            type: 'GET',
            data: {},
            dataType: 'json',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: async,//同步：false,异步：true,默认true
            success: function (data) {
                obj.logoutCheck(data);
                obj.expireTime = data.expireTimestamp - data.timestamp;
            },
        });
    },
    checkExpireTime: function () {
        var obj = checkLoginTimeOut;
        if (null == obj.expireTime) return;
        obj.expireTime--;
        if (-2 == obj.expireTime) obj.check(false);
        if (-4 == obj.expireTime){
            obj.logout(false);
            obj.logoutCheck({isLogin: false, msg: top.translation.t('loginTimeout')});
        }
    },
    /**
     * ajax请求时登录超时时注销
     * @param data
     */
    logoutUrl: null,
    logoutCheck: function (data) {
        if (false === data.isLogin) {
            $.Layer.alert(
                {
                    msg: top.translation.t('loginTimeout'),
                    fn: function () {
                        top.location.href = '/';
                    }
                }
            );
        }
    },
    logout: function (jump) {
        var obj = checkLoginTimeOut;
        $.ajax({
            url: obj.logoutUrl[0],
            type: 'GET',
            data: {},
            dataType: 'json',
            timeout: 10000,
            cache: false,
            async: false,
            success: function (data) {
            },
        });
        $.ajax({
            url: obj.logoutUrl[1],
            type: 'GET',
            data: {},
            dataType: 'json',
            timeout: 10000,
            cache: false,
            async: false,
            success: function (data) {
            },
        });
        if (jump) top.location.href='/';
    },
};