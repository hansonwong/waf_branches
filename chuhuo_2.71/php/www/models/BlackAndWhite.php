<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\validator\IpValidator;
/**
 * This is the model class for table "t_blackandwhite".
 *
 * @property integer $id
 * @property string $ips
 * @property string $type
 * @property integer $status
 * @property integer $iptype
 */
class BlackAndWhite extends BaseModel
{
    public static function tableName()
    {
        return 't_blackandwhite';
    }

    public function rulesSource()
    {
        return [
            [['status', 'iptype'], 'integer'],
            ['iptype', 'in', 'range' => [1, 2, 3]],
            [['ips'], 'string', 'max' => 255],
            [['type'], 'string', 'max' => 8],
            [['ips'], 'unique', 'message' => Yii::$app->sysLanguage->getTranslateBySymbol('ipOrIpSegmentAlreadyExists')],
            ['ips', 'validateIps', 'skipOnEmpty' => false, 'skipOnError' => false],
        ];
    }

    public function validateIps($attribute, $params)
    {
        $value = $this->$attribute;
        switch($this->iptype){
            case 1:
                if(!IpValidator::validateIp($value))
                    $this->addError($attribute, Yii::$app->sysLanguage->getTranslateBySymbol('ipAddressIsNotLegal'));
                break;
            case 2:
                if(!IpValidator::validateIpIntervalFor4($value))
                    $this->addError($attribute, Yii::$app->sysLanguage->getTranslateBySymbol('ipIntervalIsNotLegal'));
                break;
            case 3:
                if(!IpValidator::validateIpWithMask($value))
                    $this->addError($attribute, Yii::$app->sysLanguage->getTranslateBySymbol('ipWithMaskIsNotLegal'));
                break;
        }
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'iptype' => 'IP类型',
            'ips' => 'IP或IP段',
            'type' => '类型',
            'status' => '状态',
        ];
    }

    public function afterSave($insert, $changedAttributes)
    {
        if($insert) Yii::$app->wafHelper->pipe("CMD_BAW|{$this->id}|I");
        else {
            $type = $changedAttributes['type'] ?? $this->type;
            $ips = $changedAttributes['ips'] ?? $this->ips;
            Yii::$app->wafHelper->pipe("CMD_BAW|{$this->id}|U|{$type},{$ips}");
        }
        parent::afterSave($insert, $changedAttributes);
    }

    public function returnType($type)
    {
        $arr = ['black' => Yii::$app->sysLanguage->getTranslateBySymbol('blackList'), 'white' => Yii::$app->sysLanguage->getTranslateBySymbol('whiteList')];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function returnIpType($type)
    {
        $arr = ['1' => 'IP',
            '2' => Yii::$app->sysLanguage->getTranslateBySymbol('IpInterval'),
            '3' => Yii::$app->sysLanguage->getTranslateBySymbol('IpWithSubnetMask')];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['iptype', 'type',],
            '~' => ['ips',],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => [
                'ips',
                'iptype' => $this->returnIpType('select'),
                'type' => $this->returnType('select'),
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        return [
            'field' => [
                'ips',
                'iptype' => ['float' => 'c', 'type' => 'switch', 'val' => $this->returnIpType('switch')],
                'type' => ['float' => 'c', 'type' => 'switch', 'val' => $this->returnType('switch')],
            ],
            'model' => $this
        ];
    }

    /**
     * 字段修改、添加配置
     * @return array
     */
    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'id' => ['showType' => 'hidden'],
                'status' => ['showType' => 'notShow'],
                'type' => $this->returnType('select'),
                'iptype' => $this->returnIpType('select'),
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
