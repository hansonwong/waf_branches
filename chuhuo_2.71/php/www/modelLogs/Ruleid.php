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
class Ruleid extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_ruleid';
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
            [['logdate', 'ruleid'], 'required'],
            [['logdate'], 'safe'],
            [['ruleid', 'Hits'], 'integer'],
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
            'ruleid' => Yii::t('app', 'Ruleid'),
            'Hits' => Yii::t('app', 'Hits'),
        ];
    }
}
