var translation = {
    url: null,
    init: function (url) {
        if (typeof(top.translation) == Object && undefined != top.translation.translationLib.length) return;

        if (url) this.url = url;
        $.ajax({
            url: this.url,
            type: 'GET',
            data: {},
            dataType: 'json',
            timeout: 10000,
            cache: false,
            async: false,
            success: function (data) {
                var obj = translation;
                obj.translationLib = data.data;
            },
        });
        top.translation = this;
    },
    translationLib: {},
    t: function (key) {
        try {
            return this.translationLib[key];
        } catch (e) {
            return key;
        }
    }
};