var translation = {
    url: null,
    init: function(url){
        if(url) this.url = url;
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
    },
    translationLib: <?=json_encode(Yii::$app->sysLanguage->getTranslateSymbolForCurrentLang())?>,
    t: function(key){
        try{
            return this.translationLib[key];
        } catch (e){
            return key;
        }
    }
};