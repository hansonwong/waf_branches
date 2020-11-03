<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "t_countsety".
 *
 * @property integer $id
 * @property string $logdate
 * @property integer $emergency
 * @property integer $alert
 * @property integer $critical
 * @property integer $error
 * @property integer $warning
 * @property integer $notice
 * @property integer $info
 * @property integer $debug
 */
class Countsety extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_countsety';
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
        return [
            [['logdate'], 'required'],
            [['logdate'], 'safe'],
            [['emergency', 'alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug'], 'integer'],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => Yii::t('app', 'ID'),
            'logdate' => Yii::t('app', 'Logdate'),
            'emergency' => Yii::t('app', 'Emergency'),
            'alert' => Yii::t('app', 'Alert'),
            'critical' => Yii::t('app', 'Critical'),
            'error' => Yii::t('app', 'Error'),
            'warning' => Yii::t('app', 'Warning'),
            'notice' => Yii::t('app', 'Notice'),
            'info' => Yii::t('app', 'Info'),
            'debug' => Yii::t('app', 'Debug'),
        ];
    }
}
