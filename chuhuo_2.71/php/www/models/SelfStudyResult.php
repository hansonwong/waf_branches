<?php

namespace app\models;

use Yii;

class SelfStudyResult extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['uriMax', 'argNameMax', 'argContentMax', 'argCountMax', 'cookieMax', 'cookieNameMax', 'cookieContentMax', 'cookieCountMax'], 'integer'],
            [['uriMax', 'argNameMax', 'argContentMax', 'argCountMax', 'cookieMax', 'cookieNameMax', 'cookieContentMax', 'cookieCountMax'], 'required'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'selfStudyResult',
            'uriMax' => 'URI'.Yii::$app->sysLanguage->getTranslateBySymbol('maxLength'),
            'argNameMax' => 'URI'.Yii::$app->sysLanguage->getTranslateBySymbol('maxLengthForAttrName'),
            'argContentMax' => 'URI '.Yii::$app->sysLanguage->getTranslateBySymbol('maxLengthForAttr'),
            'argCountMax' => 'URI '.Yii::$app->sysLanguage->getTranslateBySymbol('maxCountForAttr'),
            'cookieMax' => 'COOKIE '.Yii::$app->sysLanguage->getTranslateBySymbol('maxLength'),
            'cookieNameMax' => 'COOKIE '.Yii::$app->sysLanguage->getTranslateBySymbol('maxLengthForAttrName'),
            'cookieContentMax' => 'COOKIE '.Yii::$app->sysLanguage->getTranslateBySymbol('maxLengthForContent'),
            'cookieCountMax' => 'COOKIE '.Yii::$app->sysLanguage->getTranslateBySymbol('maxCount'),
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
        ];
        return $field;
    }

    public function afterSave(){
        Yii::$app->wafHelper->pipe('CMD_NGINX');
    }
}
