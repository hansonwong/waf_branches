<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "t_sourceip".
 *
 * @property integer $id
 * @property string $logdate
 * @property string $CountryCode
 * @property string $RegionCode
 * @property string $City
 * @property string $SourceIP
 * @property integer $Hits
 */
class Sourceip extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_sourceip';
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
            [['logdate', 'SourceIP'], 'required'],
            [['logdate'], 'safe'],
            [['Hits'], 'integer'],
            [['CountryCode'], 'string', 'max' => 3],
            [['RegionCode'], 'string', 'max' => 8],
            [['City'], 'string', 'max' => 32],
            [['SourceIP'], 'string', 'max' => 15],
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
            'CountryCode' => Yii::t('app', 'Country Code'),
            'RegionCode' => Yii::t('app', 'Region Code'),
            'City' => Yii::t('app', 'City'),
            'SourceIP' => Yii::t('app', 'Source Ip'),
            'Hits' => Yii::t('app', 'Hits'),
        ];
    }
}
