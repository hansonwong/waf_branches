<div>
    <div class="index_box"  style="width:99.5%">
        <h3 class="m_title"><?=Yii::$app->sysLanguage->getTranslateBySymbol('productInfo')?></h3>
        <div class="indexLists">
            <ul class="ulInfo">
                <li class="start">
                    <i class="icon1"></i>
                    <div>
                        <p class="p1"><?=Yii::$app->sysLanguage->getTranslateBySymbol('productModel')?></p>
                        <p class="p2"><?=$devInfo['model']?></p>
                    </div>
                </li>
                <li>
                    <i class="icon2"></i>
                    <div>
                        <p class="p1"><?=Yii::$app->sysLanguage->getTranslateBySymbol('systemVersion')?></p>
                        <p class="p2"><?=$devInfo['sys_ver']?></p>
                    </div>
                </li>
                <li>
                    <i class="icon3"></i>
                    <div>
                        <p class="p1"><?=Yii::$app->sysLanguage->getTranslateBySymbol('ruleVersion')?></p>
                        <p class="p2"><?=$devInfo['rule_ver']?></p>
                    </div>
                </li>
                <li class="last">
                    <i class="icon4"></i>
                    <div>
                        <p class="p1"><?=Yii::$app->sysLanguage->getTranslateBySymbol('productID')?></p>
                        <p class="p2"><?=$devInfo['serial_num']?></p>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</div>