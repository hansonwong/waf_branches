<?php

use \yii\helpers\Url;
use yii\helpers\Html;

?>
<div class="openWin">
    <!--文件分析结果-展示-->
    <h1 style="text-align:center"><?= Yii::$app->sysLanguage->getTranslateBySymbol('fileAnalysisResultsShow') ?></h1>
    <form action="" method="post" id="form_id">
        <div class="jbxx sj" style="height:448px;margin-top:0; overflow: auto;">
            <!--关闭-->
            <button type="button" class="btn_close" title="<?= Yii::$app->sysLanguage->getTranslateBySymbol('close') ?>"
                    value="<?= Yii::$app->sysLanguage->getTranslateBySymbol('close') ?>"></button>
            <table width="80%" border="0" cellspacing="0" cellpadding="0" class="date_add_table">
                <?php if( !empty($list) ): ?>
                    <?php foreach ($list as $temp) {
                        foreach ($temp as $k => $v) { ?>
                            <tr>
                                <td><?= $k ?></td>
                                <td><?= $v ?></td>
                            </tr>
                        <?php }
                    } ?>
                <?php else:?>
                    <tr><td><?= Yii::$app->sysLanguage->getTranslateBySymbol('emptyData') ?></td></tr>
                <?php endif ?>
            </table>
        </div>
    </form>
</div>
<script type="text/javascript">
    var dialog = top.getDialog();
    $('.btn_close').on('click', function (event) {
        event.preventDefault();
        dialog.close()
    });
</script>