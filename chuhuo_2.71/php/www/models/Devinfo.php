<?php

namespace app\models;

use Yii;

/**
 * This is the model class for table "t_devinfo".
 *
 * @property string $model
 * @property string $sys_ver
 * @property string $rule_ver
 * @property string $serial_num
 */
class Devinfo extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_devinfo';
    }

    /**
     * @inheritdoc
     */
    public function rules()
    {
        return [
            [['model', 'sys_ver', 'rule_ver', 'serial_num'], 'required'],
            [['model', 'sys_ver', 'rule_ver'], 'string', 'max' => 20],
            [['serial_num'], 'string', 'max' => 30],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'model' => Yii::t('app', 'product model'),
            'sys_ver' => Yii::t('app', 'system version'),
            'rule_ver' => Yii::t('app', 'rules version'),
            'serial_num' => Yii::t('app', 'product serial number'),
        ];
    }
}
