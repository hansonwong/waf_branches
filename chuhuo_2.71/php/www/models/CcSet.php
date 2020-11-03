<?php

namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class CcSet extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['ccEnable', 'brouteEnable'], 'integer'],
            [['ccPeriod','broutePeriod'], 'integer', 'min'=>5, 'max'=>3600],
            [['ccTimes','brouteTimes'], 'integer', 'min'=>2, 'max'=>4000],
            [['ccBlockTime','brouteBlockTime'], 'integer', 'min'=>5, 'max'=>86400],
            [['brouteUris'], 'filter', 'filter' => function($value){
                return str_replace(["\r\n", "\r", "\n"], ';', $value);
            }],
            [['brouteUris'], 'string', 'max' => 2048],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'sourceIpDefendCc',
            'ccEnable' => '来源IP地址访问速率限制',
            'ccPeriod' => '统计周期',
            'ccTimes' => '请求次数上限',
            'ccBlockTime' => '阻止访问时间',

            'headTitle2' => 'givenUriDefendCc',
            'brouteEnable' => '目的URI访问速率限制',
            'broutePeriod' => '统计周期',
            'brouteTimes' => '请求次数上限',
            'brouteBlockTime' => '阻止访问时间',
            'brouteUris' => '目的URI列表',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'ccEnable' => array_merge(
                    SelectList::enable('radio'),
                    ['tipsPsTKey' => ['requestCountUpperLimitTips']]
                ),
                'ccPeriod' => ['tips' => Yii::$app->sysLanguage->getTranslateBySymbol('second').' ('.Yii::$app->sysLanguage->getTranslateBySymbol('defaultValue').': 15,'.Yii::$app->sysLanguage->getTranslateBySymbol('scope').': 5-3600)'],
                'ccTimes' => ['tips' => Yii::$app->sysLanguage->getTranslateBySymbol('times').' ('.Yii::$app->sysLanguage->getTranslateBySymbol('defaultValue').': 50,'.Yii::$app->sysLanguage->getTranslateBySymbol('scope').': 2-4000)'],
                'ccBlockTime' => ['tips' => Yii::$app->sysLanguage->getTranslateBySymbol('second').' ('.Yii::$app->sysLanguage->getTranslateBySymbol('defaultValue').': 20,'.Yii::$app->sysLanguage->getTranslateBySymbol('scope').': 5-86400)'],

                'brouteEnable' => array_merge(
                    SelectList::enable('radio'),
                    ['tipsPsTKey' => ['destinationUriVisitRateLimitingTips']]
                ),
                'broutePeriod' => ['tips' => Yii::$app->sysLanguage->getTranslateBySymbol('second').' ('.Yii::$app->sysLanguage->getTranslateBySymbol('defaultValue').': 15,'.Yii::$app->sysLanguage->getTranslateBySymbol('scope').': 5-3600)'],
                'brouteTimes' => ['tips' => Yii::$app->sysLanguage->getTranslateBySymbol('times').' ('.Yii::$app->sysLanguage->getTranslateBySymbol('defaultValue').': 50,'.Yii::$app->sysLanguage->getTranslateBySymbol('scope').': 2-4000)'],
                'brouteBlockTime' => ['tips' => Yii::$app->sysLanguage->getTranslateBySymbol('second').' ('.Yii::$app->sysLanguage->getTranslateBySymbol('defaultValue').': 20,'.Yii::$app->sysLanguage->getTranslateBySymbol('scope').': 5-86400)'],
                'brouteUris' => [
                    'type' => 'textarea',
                    'length' => 0,
                    'height' => '100px',
                    'default' => [
                        'type' => 'callback',
                        'val' => function($obj, $val){
                            return str_replace(';',"\n", $val);
                        }
                    ],
                    'tipsPsTKey' => ['destinationUriListTips'],
                ],
            ],
        ];
        return $field;
    }

    public function save(){
        $result = parent::save();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        return $result;
    }
}
