<?php

namespace app\models;

use Yii;

/**
 * This is the model class for table "t_nicset".
 *
 * @property string $nic
 * @property string $ip
 * @property string $mask
 * @property string $gateway
 * @property integer $isstart
 * @property integer $islink
 * @property string $workmode
 * @property string $desc
 * @property string $brgname
 */
class Nicset extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_nicset';
    }

    /**
     * @inheritdoc
     */
    public function rules()
    {
        return [
            [['nic'], 'required'],
            [['isstart', 'islink'], 'integer'],
            [['nic', 'ip', 'mask', 'gateway', 'workmode', 'desc', 'brgname'], 'string', 'max' => 45],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'nic' => Yii::t('app', 'nic name'),
            'ip' => Yii::t('app', 'Ip'),
            'mask' => Yii::t('app', 'Mask'),
            'gateway' => Yii::t('app', 'Gateway'),
            'isstart' => Yii::t('app', '0disable 1enable'),
            'islink' => Yii::t('app', '0unlink 1linked'),
            'workmode' => Yii::t('app', 'Workmode'),
            'desc' => Yii::t('app', 'Desc'),
            'brgname' => Yii::t('app', 'Brgname'),
        ];
    }
}
