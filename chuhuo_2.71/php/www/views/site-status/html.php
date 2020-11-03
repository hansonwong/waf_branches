<?php
use \yii\helpers\Url;
?>
<script>
    hListTabelConfig.detail = {
        height: 'auto', onShowDetail: function (r, p) {
            var id = r.primaryKey;
            $.ajax({
                url: '<?php echo Url::to(['index', 'op'=>'detail']);?>',
                type: 'POST',
                dataType: "json",
                data:{'_csrf':$('[name=_csrf]').val(), 'id':id},
                cache: false,
                timeout: 30000,
                success: function(d){
                    var el = '<table cellpadding="0" cellspacing="0" style="width:95%;" class="detailtd">' +
                        '<tr>' +
                        '<td align="right" class="dtd" width="120">' +
                        '<?= Yii::$app->sysLanguage->getTranslateBySymbol("remarks")?>：' + ////备注
                        '</td>' +
                        '<td>' + d.desc + '</td>' +
                        '</tr>' +
                        '</table>';
                    $(p).append($(el).css('margin', '20px auto'));
                }
            });
        }
    };
</script>