<?php

use \yii\helpers\Url;
use yii\helpers\Html;
use yii\widgets\ActiveForm;

?>
<style>
.seaBox {
    display: none;
}
</style>
<div class="openWin">
    <form action="" method="post" id="form_id">
        <h1><?= Yii::$app->sysLanguage->getTranslateBySymbol('rulesUpgrade') ?></h1>
        <div class="jbxx  sj">
            <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                <tr>
                    <td>*<?= Yii::$app->sysLanguage->getTranslateBySymbol('rulesUpgrade') ?>
                        ,<?= Yii::$app->sysLanguage->getTranslateBySymbol('chooseUpgradeFile') ?></td>
                <tr>
                </tr>
                <td>
                    <input name="txt2" type="text" class="input_text_wid" id="txt2"/>
                    <input type="button" class="btn_ty"
                           value="<?= Yii::$app->sysLanguage->getTranslateBySymbol('chooseFile') ?>"/>
                    <input class="input_file" name="rules_file" id="rules_file" size="30" type="file"
                           onchange="txt2.value=this.value"/>
                </td>
                <tr>
                </tr>
                <td><input name="input" type="button" onclick="return doSubmit();" class="btn_ty"
                           value="<?= Yii::$app->sysLanguage->getTranslateBySymbol('upgrade') ?>"/></td>
                </tr>
            </table>
        </div>
    </form>
    <div id="maingrid" class="list"></div>
</div>
<script type="text/javascript">
    (function ($) {  //避免全局依赖,避免第三方破坏
        $(document).ready(function () {
            var _csrf = $('meta[name=csrf-token]').attr('content');
            /*调用*/
            var GridTable = $.BDGrid({
                _csrf: _csrf,
                sColumnsUrl: "<?=Url::to(['config', 'op' => 'header']);?>",
                ajax: {
                    url: "<?=Url::to(['config', 'op' => 'body']);?>",
                    type: 'POST',
                    parms: {_csrf:_csrf} // yii2需要传的参数
                },
                el: '#maingrid',
                dataAction: 'server',
                showSitting: false,//是否需要操作列
                showEdit: false,
                showView: false,
                showDel: false,
                showLock: false,//是否需要解锁和锁定状态栏
                isSelectR: true,//复选按钮是否选中
                showOpen:false,//是否需要启停状态栏
                showSetting:true, //是否显示配置按钮
                allowHideColumn: false, //是否显示'切换列层'按钮
                root: 'data',//数据
                pageParmName:'page',//页码
                pagesizeParmName:'pagesize',//页数据量
                record: 'total',//总数
                width: '99.8%',
                height: '99.8%',
                pageSize: 20,
                pageSizeOptions: [10, 20, 30, 40, 50, 100],
                showRuning: false,
                checkbox: false,
                columnDefs: [
                ]
            });

        });
    })(jQuery);

    function doSubmit() {
        var form_data = new FormData();

        var _csrf = $('meta[name=csrf-token]').attr('content');
        form_data.append('_csrf', _csrf);
        form_data.append('file', $('input[name="rules_file"]')[0].files[0]);

        $.ajax({
            url: '<?php echo Url::to(['config']);?>',
            type: 'POST',
            data: form_data,
            cache: false,
            processData: false,
            contentType: false,
            timeout: 30000,
            success: function (data) {
                $.grid.reload();
                if (data.code === 'T') {
                    var timerId = setInterval(function () {
                        var checkData = JSON.parse(checkUpgradeStatus(data.id).responseText);
                        if (checkData.code === 'T' && checkData.iUpdateResult !== 0) {
                            clearInterval(timerId);

                            $.grid.reload();
                            if (checkData.iUpdateResult === 1) {
                                art.dialog({icon: 'succeed', content: checkData.info, time: 1});
                            }
                            else {
                                art.dialog({icon: 'error', content: checkData.info, time: 2});
                            }
                        }
                    }, 2000);
                }
                else {
                    art.dialog({icon: 'error', content: data.info, time: 2});
                }
            }
        });
    }

    function checkUpgradeStatus(id) {
        var _csrf = $('meta[name=csrf-token]').attr('content');
        return $.ajax({
            url: "<?php echo Url::to(['config']);?>" + "&op=check",
            type: 'POST',
            dataType: "json",
            data: {'_csrf': _csrf, 'id': id},
            cache: false,
            timeout: 300,
            async: false,
            error: function () {
            },
            success: function (data) {
                return data;
            }
        });
    }
</script>
						
