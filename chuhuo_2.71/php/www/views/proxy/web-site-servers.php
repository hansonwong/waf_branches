<table width="98%" border="0" align="center" cellpadding="0" cellspacing="0" class="server_table" id="idtdKeyList">
    <input type="hidden" id="web_add">
    <tbody>
    <tr>
        <!--IP地址-->
        <td width="18%" class="tdbg"><?= Yii::$app->sysLanguage->getTranslateBySymbol('ipAddress') ?></td>
        <!--端口-->
        <td width="10%" class="tdbg"><?= Yii::$app->sysLanguage->getTranslateBySymbol('port') ?></td>
        <!--权重-->
        <td width="10%" class="tdbg"><?= Yii::$app->sysLanguage->getTranslateBySymbol('weight') ?></td>
        <!--操作-->
        <td width="10%" class="tdbg"><?= Yii::$app->sysLanguage->getTranslateBySymbol('operation') ?></td>
    </tr>
    <?php foreach( $webSiteServers as $v ): ?>
        <tr class="listItem">
            <td width="10%"><?= $v['ip'] ?></td>
            <td width="10%"><?= $v['port'] ?></td>
            <td><?= $v['weight'] ?></td>
            <td width="15%" align="center">
                <!--删除-->
                <a href="javascript:void(0);" onclick="delip(this);"
                   class="btn btn_del"><?= Yii::$app->sysLanguage->getTranslateBySymbol('delete') ?></a>
            </td>
            <input type="hidden" class="ipmast" name="WebSite[WebSiteServers][]"
                   value="<?= $v['ip'] ?>:<?= $v['port'] ?>:<?= $v['weight'] ?>"/>
        </tr>
    <?php endforeach; ?>
    </tbody>
</table>
<table width="98%" border="0" align="center" cellpadding="0" cellspacing="0" class="server_table_add">
    <tbody>
    <tr>
        <td width="18%">
            <input id="ipadd" type="text" class="text text_wid15" style="text-align: center;" placeholder="<?= Yii::$app->sysLanguage->getTranslateBySymbol('ipAddress') ?>">
        </td>
        <td width="10%">
            <input type="text" id="ipport" maxlength="5" class="text" style="text-align: center;" placeholder="<?= Yii::$app->sysLanguage->getTranslateBySymbol('port') ?>">
        </td>
        <td width="10%">
            <input value="1" type="text" id="ipqz" class="text" style="text-align: center;" placeholder="<?= Yii::$app->sysLanguage->getTranslateBySymbol('weight') ?>">
            <span id="ipqz_text" style="display: none"></span>
        </td>
        <td width="10%" align="center">
            <!--添加-->
            <input name="but" type="button" class="btn_ty"
                   value="<?= Yii::$app->sysLanguage->getTranslateBySymbol('add') ?>"
                   onclick="addServerIpMask();">
        </td>
    </tr>
    </tbody>
</table>
<!-- 错误提示信息 -->
<p id="server_error_msg" class="red error_msg"></p>
