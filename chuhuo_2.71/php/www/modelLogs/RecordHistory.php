<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "t_ruleid".
 *
 * @property integer $id
 * @property string $logdate
 * @property integer $ruleid
 * @property integer $Hits
 */
class RecordHistory extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_record_history';
    }

    /**
     * @return \yii\db\Connection the database connection used by this AR class.
     */
    public static function getDb()
    {
        return Yii::$app->get('dbLogs');
    }

    /**
     * @inheritdoc
     */
    public function rules()
    {
        return [];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => Yii::t('app', 'ID'),
            'url' => Yii::t('app', 'url'),
            'time' => Yii::t('app', 'time'),
            'status' => Yii::t('app', 'status'),
            'result' => Yii::t('app', 'result'),
            'desc' => Yii::t('app', 'desc'),
            'protype' => Yii::t('app', 'protype'),
            'freq' => Yii::t('app', 'freq'),
            'responsetime' => Yii::t('app', 'responsetime'),
            'type' => Yii::t('app', 'type'),
            'rate' => Yii::t('app', 'rate'),
        ];
    }
}
