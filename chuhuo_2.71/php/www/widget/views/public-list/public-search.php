<?php
use \yii\helpers\Url;
use \app\logic\sys\SysAuthority;

$controllerId = Yii::$app->controller->id;
$translation = Yii::$app->sysLanguage;
$urlPrefix = Yii::$app->sysPath->resourcePath;
$get = Yii::$app->request->get();
$holdModelArgs = Yii::$app->sysParams->getParamsChild(['holdArgs', 'model']);
$holdCommonArgs = Yii::$app->sysParams->getParamsChild(['holdArgs', 'common']);
$holdModelArgsVal = $get[$holdModelArgs] = (isset($get[$holdModelArgs])) ? $get[$holdModelArgs] : '';
$holdCommonArgsVal = $get[$holdCommonArgs] = (isset($get[$holdCommonArgs])) ? $get[$holdCommonArgs] : '';
?>
<style>
#keyword_box .btn{
    margin: -2px 0px 0px 5px;
}
</style>
<div class="keyword_box pad_top" id="keyword_box" style="display:none">
    <span class="up" ></span>
    <span class="close"  ></span>
    <form id="search_form" method="post" onsubmit="if(event.keyCode==13){return false;}"
        <?="{$holdModelArgs}=\"{$holdModelArgsVal}\""?>
        <?="{$holdCommonArgs}=\"{$holdCommonArgsVal}\""?>
          action="<?=$urlPrefix.Yii::$app->requestedRoute?>">
        <input type="hidden" name="_csrf" value="<?=Yii::$app->request->csrfToken?>"/>
        <input type="hidden" name="<?=$holdModelArgs?>" value="<?=$holdModelArgsVal?>">
        <input type="hidden" name="<?=$holdCommonArgs?>" value="<?=$holdCommonArgsVal?>">
        <ul>
            <?php
            $model = $search['model'];#模型对象
            $titles = $model->attributeLabels();#标签列表
            $skey = $search['key'];#父KEY
            $searchIdPrefix = 'search-';#搜索ID前缀
            foreach($search['field'] as $key => $val){
                if(!isset($get[$skey][$key])) $get[$skey][$key] = '';
                $mval = $model[$key];
                $name = $skey.'['.$key.']';
                $nameVueKey = "{$skey}.{$key}";
                $nameVue = "{$skey}[\"{$key}\"]";

                $titleVal = $titles[$key];
                echo "<li><label>{$titleVal}:</label>";
                switch($val['type']){
                    case 'text' : echo "<input type='text' class='text'
            placeholder='{$titleVal}' id='{$searchIdPrefix}{$key}' name='{$name}' vue-key='{$nameVueKey}' v-model='{$nameVue}'>";
                        break;

                    case 'select' : echo "<select class='text' name='{$name}' vue-key='{$nameVueKey}' id='{$searchIdPrefix}{$key}' v-model='{$nameVue}'>";
                        echo "<option value=''></option>";
                        foreach($val['data'] as $k => $v){
                            echo "<option value='{$k}'>{$v}</option>";
                        }
                        echo "</select>";
                        /*echo "<script>$(function(){$('#{$key}').val('{$mval}');});</script>";*/
                        break;
                    case 'between':
                        echo <<<ECHO
                        <input type='text' class='text' placeholder='{$titleVal}' id='{$searchIdPrefix}{$key}Start' name='{$name}[]'>
                        <input type='text' class='text' placeholder='{$titleVal}' id='{$searchIdPrefix}{$key}End' name='{$name}[]'>
ECHO;
                        break;
                    case 'betweenDateTime':
                        $timeStart = $translation->getTranslateBySymbol('timeStart');
                        $timeStop = $translation->getTranslateBySymbol('timeStop');

                        echo <<<ECHO
        <label>({$timeStart})</label><input type='text' class='text'
            placeholder='{$titleVal}' id='{$searchIdPrefix}{$key}StartDate' name='{$name}[]'
            onFocus="var endDate=\$dp.$('{$searchIdPrefix}{$key}EndDate');WdatePicker({onpicked:function(){endDate.focus();},
                   maxDate:'#F{\$dp.\$D(\'{$searchIdPrefix}{$key}EndDate\')}',maxDate:'%y-%M-%d',dateFmt:'{$val['format']}'})"
            >
        <label>({$timeStop})</label><input type='text' class='text'
            placeholder='{$titleVal}' id='{$searchIdPrefix}{$key}EndDate' name='{$name}[]'
            onFocus="WdatePicker({minDate:'#F{\$dp.\$D(\'{$searchIdPrefix}{$key}StartDate\')}',maxDate:'%y-%M-%d',dateFmt:'{$val['format']}'})"
            >
ECHO;
                        break;
                    default : echo "<input type='text' class='text'
            placeholder='{$titleVal}' id='{$searchIdPrefix}{$key}' name='{$name}' vue-key='{$nameVueKey}' v-model='{$nameVue}'>";
                }
                echo "</li>";
            }
            ?>

            <li><button type="button" onclick="search_form_submit();" class="btn c_o bpad"><?=$translation->getTranslateBySymbol('search')?></button></li>
            <?php if(SysAuthority::singleAuthorityForCurrentUser("{$controllerId}/export-data")){?>
            <li><button type="button" onclick="search_form_export();" class="btn c_o bpad"><?=$translation->getTranslateBySymbol('export')?></button></li>
            <?php }
            if(SysAuthority::singleAuthorityForCurrentUser("{$controllerId}/empty-data-for-condition")){?>
            <li><button type="button" onclick="search_form_empty_data();" class="btn c_o btn_del"><?=$translation->getTranslateBySymbol('emptyDataForSearchCondition')?></button></li>
            <?php }?>
            <li><button type="button" class="btn c_o bpad" onclick="search_empty();"><?=$translation->getTranslateBySymbol('emptySearchCondition')?></button></li>
        </ul>
    </form>
</div>

<script>
    var getArgs = <?=json_encode($get)?>;

    //清空搜索框
    function search_empty(){
        var <?=$holdModelArgs?>Str = $('#search_form').attr('<?=$holdModelArgs?>');
        var <?=$holdModelArgs?> = <?=$holdModelArgs?>Str.split(",");

        $('#search_form .text').each(function(){
            var obj = $(this);
            var id = obj.attr('id');
            if(-1 == $.inArray(id, <?=$holdModelArgs?>)){
                try{
                    obj.val('');
                    var vueKey = obj.attr('vue-key');
                    vueKey = vueKey.split('.');
                    formData[vueKey[0]][vueKey[1]] = '';
                } catch(e){}
            }
        });

        search_form_submit();
    }

    //搜索
    function search_form_submit(){
        var <?=$holdCommonArgs?>Str = $('#search_form').attr('<?=$holdCommonArgs?>');
        var <?=$holdCommonArgs?> = <?=$holdCommonArgs?>Str.split(",");

        if(0 != <?=$holdCommonArgs?>.length){
            for(var i = 0; i < <?=$holdCommonArgs?>.length; i++){
                var key = <?=$holdCommonArgs?>[i];
                var val = getArgs[key];
                $('#search_form').append('<input type=hidden name="' + key + '" value="' + val + '">');
            }
        }

        searchByLigerUi();//使用搜索ligerui
        //$('#search_form').submit();
    }

    //删除搜索符合的数据
    function search_form_empty_data(){
        $.Layer.confirm({
            title: top.translation.t('systemFriendlyTips'), msg:'<span class=red>' + top.translation.t('emptyWillNotBeRestored') + '</span>', fn: function () {
                $.ajax({
                    url: '<?=Url::to(['empty-data-for-condition'])?>',
                    type: 'POST',
                    data: $("#search_form").serialize(),
                    dataType: 'json',
                    timeout: 5000,
                    cache: false,
                    async: false,
                    success: function (data) {
                        switch(data.success){
                            case true:
                                search_empty();
                                break;
                            case false:
                                $.Layer.alert({msg: data.msg,});
                                break;
                        }

                    },
                });
            }
        });
    }

    //导出符合搜索条件的数据
    function search_form_export(){
        var obj = $('#search_form');
        obj.attr('action', '<?=Url::to(['export-data'])?>');
        obj.submit();
    }

    var formData;//vue表单对象
    $(function(){
        formData = new Vue({
            el: '#search_form',
            data: getArgs,
        });
        $('#search_form input[type=text]')
            .hover(function(){$(this).attr('title', $(this).val());}, '')
            .keyup(function(){$(this).attr('title', $(this).val());})
            .bind("contextmenu",function(){this.value='';return false;});

        $('#search_form select')
            .hover(function(){var val = $(this).find('[value=' + $(this).val() + ']').text();$(this).attr('title', val);}, '')
            .bind("contextmenu",function(){this.value='';return false;});
    });

    //适配liger-ui搜索
    function searchByLigerUi() {
        var data = $("#search_form").serializeArray();
        $.grid.options.parms = data;
        $.grid.loadData(true);
    }

    //精确搜索按钮显示?
    $(function(){
        var queryAccurate = $('#queryAccurate');
        if(0 < <?=count($search['field'])?>) queryAccurate.show();
        else queryAccurate.hide();
    });
</script>
<?=$search['customStr']?>


