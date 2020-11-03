<?php

namespace app\models;

use Yii;

/**
 * This is the model class for table "t_sitestatus_all".
 *
 * @property integer $id
 * @property string $url
 * @property integer $time
 * @property integer $status
 * @property integer $result
 * @property string $desc
 * @property string $protype
 * @property integer $freq
 * @property double $responsetime
 * @property integer $type
 * @property integer $rate
 */
class SiteStatusAll extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_sitestatus_all';
    }

    /**
     * @inheritdoc
     */
    public function rulesSource()
    {
        return [
            [['time', 'status', 'result', 'freq', 'type', 'rate'], 'integer'],
            [['responsetime'], 'number'],
            [['url'], 'string', 'max' => 1024],
            [['desc', 'protype'], 'string', 'max' => 255],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => Yii::t('app', 'ID'),
            'url' => Yii::t('app', 'Url'),
            'time' => Yii::t('app', 'Time'),
            'status' =>Yii::t('app',  'Status'),
            'result' => Yii::t('app', 'Result'),
            'desc' => Yii::t('app', 'Desc'),
            'protype' => Yii::t('app', 'Protype'),
            'freq' => Yii::t('app', 'Freq'),
            'responsetime' => Yii::t('app', 'Responsetime'),
            'type' => Yii::t('app', 'Type'),
            'rate' => Yii::t('app', 'Rate'),
        ];
    }
}
