<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "os".
 *
 * @property integer $id
 * @property string $name
 * @property string $year_monthed
 * @property integer $hits
 * @property string $domain
 */
class Os extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'os';
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
            [['name', 'year_monthed', 'hits', 'domain'], 'required'],
            [['hits'], 'integer'],
            [['name'], 'string', 'max' => 25],
            [['year_monthed'], 'string', 'max' => 6],
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
            'name' => Yii::t('app', 'Name'),
            'year_monthed' => Yii::t('app', 'Year Monthed'),
            'hits' => Yii::t('app', 'Hits'),
            'domain' => Yii::t('app', 'Domain'),
        ];
    }
}
