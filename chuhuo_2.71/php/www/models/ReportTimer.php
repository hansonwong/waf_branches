<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;

/**
 * This is the model class for table "t_cyclereport".
 *
 * @property integer $id
 * @property string $name
 * @property integer $type
 * @property string $desc
 * @property integer $cycle
 * @property integer $sendmail
 * @property string $format
 */
class ReportTimer extends \app\logic\model\BaseModel
{
    public static function tableName()
    {
        return 't_cyclereport';
    }

    public function rulesSource()
    {
        return [
            ['type', 'default', 'value' => 1],
            [['type', 'cycle', 'format'], 'required'],
            [['type', 'cycle', 'sendmail'], 'integer'],
            [['cycle'], function($attribute, $params){
                if(2 == $this->$attribute && 2 == $this->type){
                    $tips = Yii::$app->sysLanguage->getTranslateBySymbol('reportVisitFlowForCycleTips');
                    $this->addError($attribute, $tips);
                }
            }],
            [['name'], 'string', 'max' => 100],
            [['desc'], 'string', 'max' => 255],
            [['format'], 'string', 'max' => 10],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'name' => '标题',
            'type' => '报表类型',
            'desc' => '说明',
            'cycle' => '周期',
            'sendmail' => '邮件通知',
            'format' => '文件格式',
        ];
    }

    public function returnType($type)
    {
        $arr = [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('reportAttack'),
            #'2' => Yii::$app->sysLanguage->getTranslateBySymbol('reportVisitFlow')
        ];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function returnCycle($type)
    {
        $arr = [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('everyDay'),
            '2' => Yii::$app->sysLanguage->getTranslateBySymbol('everyWeekly'),
            '3' => Yii::$app->sysLanguage->getTranslateBySymbol('everyMonth')
        ];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function returnSendmail($type)
    {
        $arr = [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('enable'),
            '0' => Yii::$app->sysLanguage->getTranslateBySymbol('disable')
        ];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function returnFormat($type)
    {
        $arr = [
            'html' => 'html',
            'pdf' => 'pdf',
            #'doc' => 'doc',
        ];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function ListTable()
    {
        return [
            'field' => [
                'type' => ['float' => 'c', 'type' => 'switch', 'val' => $this->returnType('switch')],
                'cycle' => ['float' => 'c', 'type' => 'switch', 'val' => $this->returnCycle('switch')],
                'sendmail' => ['float' => 'c', 'type' => 'switch', 'val' => $this->returnSendmail('switch')],
                'desc',
                'format' => ['float' => 'c', 'type' => 'switch', 'val' => $this->returnFormat('switch')],
            ],
            'model' => $this,
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'id' => ['showType' => 'hidden'],
                'type' => $this->returnType('radio'),
                'cycle' => $this->returnCycle('select'),
                'sendmail' => $this->returnSendmail('select'),
                'format' => $this->returnFormat('select'),
            ],
            'customStr' => false,
        ];
        switch ($type) {
            case 'create' :
                break;
            case 'update' :
                break;
            default :
                ;
        }
        return $field;
    }
}
