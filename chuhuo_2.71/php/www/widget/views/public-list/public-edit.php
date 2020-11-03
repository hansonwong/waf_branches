<?php
use app\widget\AdminListConfig;
$urlPrefix = Yii::$app->sysPath->resourcePath;#静态资源路径
$fieldConfig = AdminListConfig::setField($model->ListField());#字段配置(标签/输入框)
$fieldKeyParent = $fieldConfig['fieldKey'];#模型的数组KEY
$fields = $fieldConfig['field'];#字段数组
$fieldType = $fieldConfig['fieldType'];#字段前端组件配置
$customButton = $fieldConfig['button'];
$customStr = $fieldConfig['customStr'];#自定义字符串
$submitArea = $fieldConfig['submitArea'];#是否显示提交区域
$submitUrl = $fieldConfig['submitUrl'];#提交URL

#自定义字符串变量为数组情况下判断有无head key设置,有则输出head值
if(is_array($customStr) && isset($customStr['head'])) echo $customStr['head'];

#vue绑定标签/值/提示/提示PS/错误信息/显示等内容
$vueLabel = $vueVal = $vueTips = $vueTipsPs = $vueErrorInfo = $vueBlockToggle = [];
#$output储存html,$outputScript储存js
$output = $outputScript = '';
$fieldIdPrefix = 'field-';#字段ID前缀
foreach ($fields as $fieldKey => $fieldVal) {
    $fieldTitle = $fieldVal;#字段标签
    $fieldId = "{$fieldIdPrefix}{$fieldKey}";#字段ID
    $typeConfig = $fieldType[$fieldKey] ?? [];#字段配置

    #是否有小标题,有则显示并跳过本次循环
    if(false !== strpos($fieldKey, 'headTitle')){
        $output .= "<tr><td colspan='3'><h1>{$fieldTitle}</h1></td></tr>";
        continue;
    }

    #是否有自定义域
    if(false !== strpos($fieldKey, 'customHtml')){
        $render = $typeConfig['render'] ?? null;
        $html = $render($model);
        $output .= "<tr><td colspan='3'>{$html}</td></tr>";
        continue;
    }

    $fieldTips = '';#字段提示
    $fieldTipsPs = '';#字段PS提示
    $fieldParentKey = true;#是否允许post字段的在特定key数组中
    $fieldValue = true;#是否赋值模型中的数据

    $fieldTips = $typeConfig['tips'] ?? false;
    if(!$fieldTips){
        if(isset($typeConfig['tipsTKey'])){
            $fieldTips = Yii::$app->sysLanguage->getTranslateBySymbol($typeConfig['tipsTKey']);
        } else $fieldTips = '';
    }

    $fieldTipsPs = $typeConfig['tipsPs'] ?? false;
    if(!$fieldTipsPs){
        if(isset($typeConfig['tipsPsTKey'])){
            foreach ($typeConfig['tipsPsTKey'] as $tipsPsTKey){
                $fieldTipsPs .= Yii::$app->sysLanguage->getTranslateBySymbol($tipsPsTKey).'<br>';
            }
        } else $fieldTipsPs = '';
    }

    $fieldParentKey = $typeConfig['parentKey'] ?? true;
    $fieldValue = $typeConfig['valueByModel'] ?? true;

    $fieldAliase = $typeConfig['aliase'] ?? $fieldKey;#字段提交别名
    #字段的post key
    $fieldName = ($fieldParentKey) ? "{$fieldKeyParent}[{$fieldAliase}]" : $fieldAliase;


    #是否为字段设置默认值
    if (isset($typeConfig['default'])) {
        #如果配置项为数组则做特殊处理,否则直接赋值
        if (is_array($typeConfig['default'])) {
            switch ($typeConfig['default']['type']) {
                case 'custom' :#自定义数据处理
                    $value = AdminListConfig::returnConversionValue($model->$fieldKey, $typeConfig['default']['valType']);
                    break;
                case 'callback' :#回调
                    $callback = $typeConfig['default']['val'];
                    $value = $callback($model, $model->$fieldKey);
                    break;
                default :
                    $value = $model->$fieldKey;
            }
        } else $value = $typeConfig['default'];
    } elseif ($fieldValue) {#未设置默认则从模型中取值
        $value = $model->$fieldKey;
    } else $value = '';#不设置默认也不需要从模型中取值则设置为空字符串

    #输入组件属性
    $inputProperty = $typeConfig['inputProperty'] ?? '';

    #显示方式
    $outputTableRow = true;#是否输出table行
    $outputTableRowHtml = '';#输出table行html
    $outputFieldDisableStr = '';#是否让字段处于disable状态
    if (isset($typeConfig['showType'])) {
        switch($typeConfig['showType']){
            case 'notShow':#不显示字段,包括hidden字段也不存在
                $outputTableRow = false;
                continue;
                break;
            case 'show':#显示字段,hidden字段不存在
                $fieldName = '';
                $outputFieldDisableStr = 'disabled';
                break;
            case 'hidden':#不显示字段,hidden字段存在
                $output .= "<input type=hidden
                    name='{$fieldName}'
                    id='{$fieldId}'
                    v-model='val.{$fieldKey}'
                    value=''
                    {$inputProperty}/>";
                $outputTableRow = false;
                break;
            case 'disable':#字段显示,但不可通过输入框直接修改,hidden字段存在
                $outputFieldDisableStr = 'disabled';
                $outputTableRowHtml .= "<input type=hidden
                    name='{$fieldName}'
                    id='{$fieldId}'
                    v-model='val.{$fieldKey}'
                    value=''
                    {$inputProperty}/>";
                break;
            default:;
        }
    }

    #是否输出table行
    if ($outputTableRow) {
        $rowStyle = $typeConfig['rowStyle'] ?? 3;
        if (!isset($typeConfig['type'])) $typeConfig['type'] = ' ';
        switch ($typeConfig['type']) {
            case 'select' :
                $outputTableRowHtml .= "<select id='{$fieldId}'
                    class='text'
                    name='{$fieldName}'
                    v-model='val.{$fieldKey}'
                    {$outputFieldDisableStr}
                    {$inputProperty}>";
                foreach ($typeConfig['data'] as $k => $v) {
                    $outputTableRowHtml .= "<option value='{$k}'>{$v}</option>";
                }
                $outputTableRowHtml .= "</select>";
                break;

            case 'textarea' :
                $enableMd = $typeConfig['md'] ?? false;
                $outputTableRowHtml .= "<textarea
                    class='text'
                    id='{$fieldId}'
                    name='{$fieldName}'
                    v-model='val.{$fieldKey}'
                    style='height:{$typeConfig['height']};resize: vertical;'
                    class='textarea'
                    dragonfly='true'
                    onkeydown='editTab(this);'
                    onKeyUp='if(false && {$typeConfig['length']})textarealength(this,{$typeConfig['length']});'
                    {$outputFieldDisableStr}
                    {$inputProperty}></textarea>";
                if($enableMd) $outputTableRowHtml .= "<br><br><button type=button onclick='textareaForMd($(&quot;#{$fieldId}&quot;));'>MD</button>";
                break;

            case 'textarea-editor' :
                $outputTableRowHtml .= "<textarea style='width:98%;' id='{$fieldId}' name='{$fieldName}' v-model='val.{$fieldKey}' {$outputFieldDisableStr} {$inputProperty}></textarea>";
                $outputScript .= "<script>\$(function(){UE.getEditor('{$fieldId}');});</script>";
                break;

            case 'timepicker' :
                $outputTableRowHtml .= "<input type=text
                    class='text'
                    value=''
                    id='{$fieldId}'
                    name='{$fieldName}'
                    v-model='val.{$fieldKey}'
                    {$outputFieldDisableStr}
                    {$inputProperty}
                    onFocus='WdatePicker({dateFmt:&quot;{$typeConfig['format']}&quot;});'
                    onblur='formData.val.{$fieldKey} = this.value'>";
                break;

            case 'radio' :
                foreach ($typeConfig['data'] as $k => $v) {
                    $outputTableRowHtml .=
                        "<label class='inputRadio' title='{$v}'>
						<input type=radio
						    name='{$fieldName}'
						    v-model='val.{$fieldKey}'
						    value='{$k}'
						    id='{$fieldId}-{$k}'
						    {$outputFieldDisableStr}
						    {$inputProperty}>
						{$v}
						</label>";
                }
                break;

            case 'checkbox' ://对数据模型进行选择
                $selectStr = Yii::$app->sysLanguage->getTranslateBySymbol('selectAll');
                $selectStr .= '/'.Yii::$app->sysLanguage->getTranslateBySymbol('unSelectAll');
                $selectReverseStr = Yii::$app->sysLanguage->getTranslateBySymbol('selectReverse');
                $outputTableRowHtml .= "
                    <div style='clear: both;padding-top: 5px;height: 0px;'>
                    <label>
                        <input type='checkbox'
                            onclick='checkboxStatusChange(this, \"{$fieldName}\", \"{$fieldKey}\");'
                            check=all>{$selectStr}
                    </label>&nbsp;&nbsp;
                    <label><input type='checkbox'
                        onclick='checkboxStatusChange(this, \"{$fieldName}\", \"{$fieldKey}\");'
                        check=reverse>{$selectReverseStr}
                    </label>
                    </div><br><br>";

                if(isset($typeConfig['valSplit'])){
                    $value_arr = explode($typeConfig['valSplit'], $value);
                } else {
                    $value_arr = is_string($value) ? json_decode($value, true) : $value;
                    $value_arr = is_array($value_arr) ? $value_arr : [];
                }

                $value = [];
                $labelWidth = $typeConfig['labelWidth'] ?? '23%';
                foreach ($typeConfig['data'] as $k => $v) {
                    $sym = false;
                    foreach ($value_arr as $value_arr_item) {
                        if ($value_arr_item == $k) {
                            $sym = true;
                            break;
                        }
                    }
                    $value[$k] = $sym;
                    $outputTableRowHtml .= "
                        <label class='inputCheckbox'
                            style='width:$labelWidth;'
                            title='{$v}'>
                            <input type=checkbox
                                name='{$fieldName}[]'
                                v-model='val.{$fieldKey}[\"{$k}\"]'
                                value='{$k}'
                                id='{$fieldId}-{$k}'
                                {$outputFieldDisableStr}
                                {$inputProperty}>
                                {$v}
                        </label>";
                }
                break;

            case 'password' :
                $outputTableRowHtml .= "<input type=password
                    class='text'
                    value=''
                    id='{$fieldId}'
                    name='{$fieldName}'
                    v-model='val.{$fieldKey}'
                    {$outputFieldDisableStr}
                    {$inputProperty}>";
                break;
            case 'fileWithVal':
                $browseButton = Yii::$app->sysLanguage->getTranslateBySymbol('browse');
                $outputTableRowHtml .= "<input type='text' class='input_text text'
                    value=''
                    id='{$fieldId}'
                    name='{$fieldName}'
                    v-model='val.{$fieldKey}'
                    {$outputFieldDisableStr}
                    {$inputProperty}/>
                    <input type='button' class='btn_ty' value='{$browseButton}' style='width:50px; float: right; margin: -25px -5px 0 0;'/>
                    <input name='UploadSingleFile[{$fieldKey}]' class='input_file' style='width:50px; margin-left: -55px; position: absolute;' type='file'
                           onchange='$(&quot;#{$fieldId}&quot;).val(this.value);vueData.val.{$fieldKey}=this.value'/>";
                break;
            case 'file' :

                break;

            case 'multipleVal' :
                $addStr = Yii::$app->sysLanguage->getTranslateBySymbol('add');
                $sensitiveWordSplitTips = Yii::$app->sysLanguage->getTranslateBySymbol('sensitiveWordSplitTips');
                $multipleValPutButtonId = "{$fieldId}PutButton";
                $multipleValPutInputId = "{$fieldId}Put";
                $outputTableRowHtml .= "<input type=hidden
                        idAliase='{$fieldId}'
                        nameAliase='{$fieldName}'
                        v-model='val.{$fieldKey}'
                        {$inputProperty}>
                    <input type=text class='text' style='max-width:50%;' placeholder='{$sensitiveWordSplitTips}' id='{$multipleValPutInputId}'>
                    <button type=button
                        id='{$multipleValPutButtonId}'
                        style='margin-left: -0px;'
                        class='btn_ty'
                        process='put'
                        onclick='vueDataMultipleValPutPop(this, \"{$fieldKey}\", $(\"#{$multipleValPutInputId}\").val())'>
                        {$addStr}</button>
                    <div class='mgclist-wrap' style='margin-top: 20px; height:{$typeConfig['height']};'>
                    <ul class='mgclist-box'>
			        <li class='mgclist-item' v-for='(value, key) in val.{$fieldKey}'>
                        <span class='mgclist-inner'>
                            {{ value }}
                            <input type=hidden name='{$fieldName}[]' v-bind:value='value' {$inputProperty}>
                            <i class='icon_x'
                                process='pop'
                                onclick='vueDataMultipleValPutPop(this, \"{$fieldKey}\", $(this).attr(\"value\"));'
                                v-bind:value='key'></i>
                        </span>
                    </li>
                    <input v-if='val.{$fieldKey}.length == 0' type=hidden
                        id='{$fieldId}'
                        name='{$fieldName}'
                        {$inputProperty}>
                    </ul>
                    </div>";
                $outputScript .= "<script>\$(function(){
                    var obj = $('#{$multipleValPutButtonId}');
                    var paddingWidth = parseInt(obj.css('padding-left'));
                    paddingWidth += parseInt(obj.css('padding-right'));
                    obj.css('margin-left', '-' + (obj.width() + paddingWidth + 2) + 'px');
                });</script>";

                break;

            default :
                $outputTableRowHtml .= "<input type=text
                    class='text'
                    value=''
                    id='{$fieldId}'
                    name='{$fieldName}'
                    v-model='val.{$fieldKey}'
                    {$outputFieldDisableStr}
                    {$inputProperty}>";
        }

        $fieldIdBlock = "{$fieldId}-parent";
        switch($rowStyle){
            case 2:
                $output .= "<tr id='{$fieldIdBlock}' v-if='toggle.{$fieldKey}'>
                    <td class='t_r'
                        style='width: 20%;'
                        v-bind:title='label.{$fieldKey}'>
                        {{ label.{$fieldKey} }}
                    </td>
                    <td colspan='2'>
                        <div class='fieldInput'>{$outputTableRowHtml}</div><br>
                        <div class='fieldTips'
                            v-bind:title='tips.{$fieldKey}'>
                            &nbsp;&nbsp;{{ tips.{$fieldKey} }}
                        </div><br>
                        <div class='red errorInfo'>{{ errorInfo.{$fieldKey} }}</div>
                        <div class='tipsPs' v-html='tipsPs.{$fieldKey}'></div>
                    </td>
                </tr>";
                break;
            case 3:
                $output .= "<tr id='{$fieldIdBlock}' v-if='toggle.{$fieldKey}'>
                    <td class='t_r'
                        style='width: 20%;'
                        v-bind:title='label.{$fieldKey}'>
                        {{ label.{$fieldKey} }}
                    </td>
                    <td style='width: 40%;'>
                        <div class='fieldInput'>{$outputTableRowHtml}</div><br>
                        <div class='red errorInfo'>{{ errorInfo.{$fieldKey} }}</div>
                        <div class='tipsPs' v-html='tipsPs.{$fieldKey}'></div>
                    </td>
                    <td style='width: 40%;'>
                        <div class='fieldTips'
                            v-bind:title='tips.{$fieldKey}'>
                            &nbsp;&nbsp;{{ tips.{$fieldKey} }}
                        </div>
                    </td>
                </tr>";
                break;
        }
        $output .= "<input v-else type=hidden
                    name='{$fieldName}'
                    id='{$fieldId}'
                    v-model='val.{$fieldKey}'
                    value=''
                    {$inputProperty}/>";

    }

    $vueVal[$fieldKey] = $value;
    $vueLabel[$fieldKey] = $fieldTitle;
    $vueTips[$fieldKey] = $fieldTips;
    $vueTipsPs[$fieldKey] = $fieldTipsPs;
    $vueErrorInfo[$fieldKey] = '';
    $vueBlockToggle[$fieldKey] = true;

}
$vue = [
    'toggle' => $vueBlockToggle,#是否显示
    'label' => $vueLabel,#标签
    'val' => $vueVal,#值
    'tips' => $vueTips,#提示
    'tipsPs' => $vueTipsPs,#提示PS
    'errorInfo' => $vueErrorInfo,#错误信息
];
?>
<div class="openWin">
    <style>
        #form-admin td.t_r{width:20%; cursor: pointer;}
        #form-admin .inputRadio{width: 23%;padding:0 1% 0 1%;height:24px;line-height:24px;overflow:hidden;text-overflow:ellipsis;}
        #form-admin .inputCheckbox{width: 23%;padding:0 1% 0 1%;height:24px;line-height:24px;overflow:hidden;text-overflow:ellipsis;}
        #form-admin .fieldInput{width:100%;}
        #form-admin .text{float:left;width:100%;}
        #form-admin .errorInfo{clear: both;width:100%;}
        #form-admin .tipsPs{clear: both;width:100%;font-weight:bold;}
        #form-admin label{float:left;}
        #form-admin .fieldTips{float:left;cursor:pointer;width:100%;height:24px;line-height:24px;overflow:hidden;text-overflow:ellipsis;white-space:norwap;}
    </style>
    <form class="form form-horizontal" id="form-admin" method="post" enctype="multipart/form-data" target="uploadField" onsubmit="if(event.keyCode==13){return false;}">
        <input type="hidden" name="_csrf" value="<?=Yii::$app->request->csrfToken?>"/>
        <div class="jbxx sj" style="padding: 0px;">
            <table width="80%" border="0" cellspacing="0" cellpadding="0" class="date_add_table">
                <?=$output?>
                <tr id="submitArea">
                    <td>&nbsp;</td>
                    <td>
                        <?php
                        $submitStr = Yii::$app->sysLanguage->getTranslateBySymbol('submit');
                        $refreshStr = Yii::$app->sysLanguage->getTranslateBySymbol('refresh');
                        ?>
                        <input type="button" class="btn_ty" onclick="formSubmit();" id="FormSubmitButton" value="<?=$submitStr?>" />
                        <input type="button" class="btn_ty" onclick="location.replace(location.href);" id="FormReload" value="<?=$refreshStr?>" />
                        <?php
                        foreach ($customButton['submit'] as $item){
                            echo "<input type=button class='btn_ty' {$item['attrs']} value='{$item['text']}' />";
                        }
                        ?>
                    </td>
                </tr>
            </table>
        </div>
    </form>
</div>
<script>
    //对输入框类型为multipleVal的值进行处理(添加/删除)
    function vueDataMultipleValPutPop(obj, key, val){
        var process = $(obj).attr('process');
        if('put' == process){
            var vals = val.split('|');
            for(var valKey in vals){
                var valItem = vals[valKey];
                var sym = true;
                if(Array != vueData['val'][key].constructor) vueData['val'][key] = [];
                for(var item in vueData['val'][key]){
                    var str = vueData['val'][key][item];
                    if(str == valItem){
                        sym = false;
                        break;
                    }
                }
                if(sym) vueData['val'][key] = vueData['val'][key].concat(valItem);
            }
            $('#<?=$fieldIdPrefix?>' + key + 'Put').val('');
        } else {
            vueData['val'][key].splice(val, 1);
        }
    }

    //checkbox状态的更改(全选/全不选/反选)
    function checkboxStatusChange(obj, namePrefix, key){
        var obj = $(obj);
        var status = obj.context.checked;
        obj.parent().siblings().children().attr('checked', false);

        var type = obj.attr('check')
        var input = $('[name*="' + namePrefix + '"]');

        input.each(function (index, ele) {
            if('reverse' == type){
                vueData.val[key][$(this).val()] = vueData.val[key][$(this).val()] ? false : true;
                return;
            }
            vueData.val[key][$(this).val()] = status;
        });
    }
</script>
<script>
    //显示错误提示信息
    function errorFieldInfo(errors){
        for(var item in errors){
            var obj = errors[item];
            var str = '';
            for(var i in obj.info) str += obj.info[i] + ' | ';
            str = str.substring(0, str.length - 3);
            vueData.errorInfo[obj.id] = str;
        }
    }
    //重置错误提示
    function resetErrorInfo(){
        var info = vueData.errorInfo;
        for(var i in info){
            info[i] = '';
        }
    }

    //提交表单
    function formSubmit(){
        try{
            formSubmitBefore();//提交前执行预处理代码,此方法可能并不存在
        } catch(e){}
        var formSubmitLoading;
        var formData = new FormData($('#form-admin')[0]);
        $.ajax({
            url: '<?=$submitUrl?>',
            type: 'POST',
            data: formData,
            dataType: 'json',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            //async: false,//同步：false,异步：true,默认true
            contentType: false,
            processData: false,
            beforeSend: function(XHR){
                formSubmitLoading = art.dialog.tips2('loading...','loading.gif', 9999);
            },
            success: submitSuccess,
            complete: function(XHR, TS){
                formSubmitLoading.close();
            },
        });
    }
</script>
<script>
    var formData;
    var vueData = <?=json_encode($vue)?>;
    $(function () {
        formData = new Vue({
            el: '#form-admin',
            data: vueData,
        });

        <?php if(null !== $submitArea){?>
        $('#submitArea').css('display', <?=$submitArea ? 'true' : 'false'?> ? 'contents' : 'none');
        <?php }?>

        $('body').show();//加载完成后显示body
    });
</script>

<?=$outputScript?>
<?php
if(!is_array($customStr)) echo $customStr;
#自定义字符串变量为数组情况下判断有无foot key设置,有则输出foot值
if(is_array($customStr) && isset($customStr['foot'])) echo $customStr['foot'];
?>

