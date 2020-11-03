<?php
use yii\helpers\Url;
$translate = Yii::$app->sysLanguage;
?>

<div class="openWin">
    <form action="<?= Url::to(['preview-create']) ?>" method="post" id="form_id" target="_blank">
        <input type="hidden" name="_csrf" id="_csrf" value=""/>
        <h1><?=$translate->getTranslateBySymbol('generatingInstantReportsBrowerTips')?></h1>
        <div class="jbxx sj">
            <table width="80%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                <tr>
                    <td class="t_r" width="120"><?=$translate->getTranslateBySymbol('reportDate')?>：</td>
                    <td>
                        <input type="text" name="startDate" id="startDate" value="<?= $current_date ?>"
                               class="text date_plug  validate[required]"
                               onFocus="var endDate=$dp.$('endDate');WdatePicker({onpicked:function(){endDate.focus();},maxDate:'#F{$dp.$D(\'endDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd'})"
                               placeholder="<?=$translate->getTranslateBySymbol('timeStart')?>">
                        <label><?=$translate->getTranslateBySymbol('to')?></label><input type="text" name="endDate" value="<?= $current_date ?>" id="endDate"
                                               class="text date_plug validate[required]"
                                               onFocus="WdatePicker({minDate:'#F{$dp.$D(\'startDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd'})"
                                               placeholder="<?=$translate->getTranslateBySymbol('timeStop')?>">
                    </td>
                </tr>

                <tr>
                    <td class="t_r"><?=$translate->getTranslateBySymbol('downloadReports')?>：</td>
                    <td>
                        <label><input name="fileType" type="radio" value="html" checked="checked"/> <?=$translate->getTranslateBySymbol('htmlFormat')?></label>
                        <label><input name="fileType" type="radio" value="pdf"/>&nbsp;<?=$translate->getTranslateBySymbol('pdfFormat')?></label>
                        <!--<label><input name="fileType" type="radio" value="doc"/>&nbsp;<?/*=$translate->getTranslateBySymbol('docFormat')*/?></label>-->
                    </td>
                </tr>
                <tr>
                    <td class="t_r"></td>
                    <td>
                        <input id="submitType" name="submitType" type="hidden" value="">
                        <input name="button" type="button" class="btn_ty btn_preview" value="<?=$translate->getTranslateBySymbol('previewReport')?>"/>
                        <input name="button" type="button" class="btn_ty btn_create" value="<?=$translate->getTranslateBySymbol('generatingReport')?>"/>
                        <span class="red" id="sMsg">&nbsp;</span>
                        <a href="#" style="display: none" id="downloadLink" class="red a_link" target="_blank" url=""><?=$translate->getTranslateBySymbol('downloadReports')?></a>
                    </td>
                </tr>
            </table>
        </div>
    </form>
</div>
<div class="report_wrap bd_t">

</div>

<script type="text/javascript">
    ;
    (function ($) {
        $(function () {
            var _csrf = $('meta[name=csrf-token]').attr('content');
            $('#_csrf').val(_csrf);

            $(".btn_preview").on('click', function () {
                $("#submitType").val('preview');
                $("#form_id").submit();
            });

            $(".btn_create").on('click', function () {
                $("#submitType").val('create');
                $("#sMsg").html("<?=$translate->getTranslateBySymbol('inReportGenerationPleaseLater')?>").show();
                $.post($("#form_id").attr('action'),$("#form_id").serialize(),function (json) {
                    $("#sMsg").hide();
                    $("#downloadLink").attr('href', json.file_path).show();
                    $.Layer.alert({title: '<?=$translate->getTranslateBySymbol('prompt')?>', msg: json.info});
                },'json');
            });


            $("#form_id").validationEngine({
                promptPosition: 'centerRight: 0, -4', scroll: false, binded: false, 'custom_error_messages': {
                    // Custom Error Messages for Validation Types
                    'required': {
                        'message': '* <?=$translate->getTranslateBySymbol('validateRequired')?>'
                    },
                    'custom': {
                        'message': '* <?=$translate->getTranslateBySymbol('enterAPositiveInteger')?>'
                    },
                    'min': {
                        'message': '* <?=$translate->getTranslateBySymbol('fillInAccordingToTheRequirement')?>'
                    }
                },
                ajaxFormValidationMethod: 'post',
                //指定使用Ajax模式提交表单处理
                ajaxFormValidation: false,
            });

        });

    })(jQuery);

</script>