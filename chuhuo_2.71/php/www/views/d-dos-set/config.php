<script>
    function setRecommendValue(){
        var w = parseInt(vueData.val.bankWidth);
        if(w > 1024 || w < 1 || !w)
        {
            art.dialog({icon: 'error', content:"<?=Yii::$app->sysLanguage->getTranslateBySymbol('networkFlowSelectTips')?>", time: 2});
            return;
        }

        var noSet = ['ddosEnable', 'udpEnable', 'icmpEnable', 'bankWidth'];
        var setVal = function(w){
            var val = w*30;
            if(val < 300) val = 300;
            else if(val > 10000) val = 10000;
            return val;
        }
        var val = setVal(w);
        for(var item in vueData.val){
            if(-1 == noSet.indexOf(item)){
                vueData.val[item] = val;
                $(`#field-${item}`).val(val);
            }
        }
    }

    function resetValue(){
        vueData.val.bankWidth = 1024;
        $(`#field-bankWidth`).val(1024);

        var noSet = ['ddosEnable', 'udpEnable', 'icmpEnable', 'bankWidth'];
        var val = 10000;
        for(var item in vueData.val){
            if(-1 == noSet.indexOf(item)){
                vueData.val[item] = val;
                $(`#field-${item}`).val(val);
            }
        }
    }
</script>