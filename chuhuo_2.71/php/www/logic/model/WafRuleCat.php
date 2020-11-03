<?php
namespace app\logic\waf\models;

use Yii;
use app\models\RuleCat;

class WafRuleCat extends RuleCat
{
    /**
     * 攻击类别
     * @param bool $isOrder
     * @return array|\yii\db\ActiveRecord[]
     */
    public static function getRuleCatArr($isOrder=true)
    {
        $RuleCatModel = RuleCat::find()->asArray()->all();

        if( $isOrder==false )  return $RuleCatModel;

        $arr = array_column($RuleCatModel, 'desc', 'name');
        $arr['B&W'] = '访问控制';
        foreach($arr as $k => $v){
            $arr[$k] = Yii::$app->sysLanguage->getTranslate($v);
        }
        return $arr;
    }
}