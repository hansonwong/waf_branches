<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "t_counturi".
 *
 * @property integer $id
 * @property string $logdate
 * @property string $Uri
 * @property string $QueryString
 * @property string $Host
 * @property integer $Hits
 * @property string $urlmd5
 */
class Counturi extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_counturi';
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
            [['Hits'], 'integer'],
            [['Uri', 'QueryString'], 'string', 'max' => 512],
            [['Host'], 'string', 'max' => 255],
            [['urlmd5'], 'string', 'max' => 32],
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
            'Uri' => Yii::t('app', 'Uri'),
            'QueryString' => Yii::t('app', 'Query String'),
            'Host' => Yii::t('app', 'Host'),
            'Hits' => Yii::t('app', 'Hits'),
            'urlmd5' => Yii::t('app', 'Urlmd5'),
        ];
    }
}
