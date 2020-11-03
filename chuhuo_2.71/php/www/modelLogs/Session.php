<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "session".
 *
 * @property integer $id
 * @property string $year_monthed
 * @property string $ranged
 * @property integer $visits
 * @property string $domain
 */
class Session extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'session';
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
            [['year_monthed', 'ranged', 'visits', 'domain'], 'required'],
            [['visits'], 'integer'],
            [['year_monthed'], 'string', 'max' => 6],
            [['ranged'], 'string', 'max' => 12],
            [['domain'], 'string', 'max' => 64],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => Yii::t('app', 'ID'),
            'year_monthed' => Yii::t('app', 'Year Monthed'),
            'ranged' => Yii::t('app', 'Ranged'),
            'visits' => Yii::t('app', 'Visits'),
            'domain' => Yii::t('app', 'Domain'),
        ];
    }
}
