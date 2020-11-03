<?php
use \yii\helpers\Url;
?>
<script>
    hListTabelConfig.detail = {
        height: 'auto', onShowDetail: function (r, p) {
            console.info(r, p);
            var id = r.primaryKey;
            $.ajax({
                url: '<?php echo Url::to(['index', 'op' => 'detail']);?>',
                type: 'POST',
                dataType: "json",
                data:{'_csrf':$('[name=_csrf]').val(), 'id':id},
                cache: false,
                timeout: 30000,
                success: function(d){
                    var el = '<table cellpadding="0" cellspacing="0" style="width:95%;" class="detailtd">' +
                        '<tr>' +
                        '<td align="right" class="dtd" width="120">' +
                        '<?=Yii::$app->sysLanguage->getTranslateBySymbol("ruleModule") ?>：' +  //规则模块
                        '</td>' +
                        '<td>' + d.ruleCatName + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        '<?=Yii::$app->sysLanguage->getTranslateBySymbol("rulesName") ?>：' +  //规则名称
                        '</td>' +
                        '<td>' + d.name + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        '<?=Yii::$app->sysLanguage->getTranslateBySymbol("generalInformation") ?>：' +  //一般信息
                        '</td>' +
                        '<td>' + d.Msg + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        '<?=Yii::$app->sysLanguage->getTranslateBySymbol("matchingContent") ?>：' + //匹配内容
                        '</td>' +
                        '<td>' + d.MatchData + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        '<?=Yii::$app->sysLanguage->getTranslateBySymbol("ruleId") ?>：' +  //规则ID
                        '</td>' +
                        '<td>' + d.RuleID + '</td>' +
                        '</tr>' +
                        '</table>';
                    $(p).append($(el).css('margin', '20px auto'));
                }
            });
        }
    };
</script>