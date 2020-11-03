<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "robot".
 *
 * @property integer $id
 * @property string $year_monthed
 * @property string $name
 * @property integer $hits
 * @property string $bandwidth
 * @property string $lastvisit
 * @property integer $hitsrobots
 * @property string $domain
 */
class Robot extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'robot';
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
            [['year_monthed', 'name', 'hits', 'bandwidth', 'lastvisit', 'hitsrobots', 'domain'], 'required'],
            [['hits', 'bandwidth', 'hitsrobots'], 'integer'],
            [['year_monthed'], 'string', 'max' => 6],
            [['name'], 'string', 'max' => 30],
            [['lastvisit'], 'string', 'max' => 12],
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
            'name' => Yii::t('app', 'Name'),
            'hits' => Yii::t('app', 'Hits'),
            'bandwidth' => Yii::t('app', 'Bandwidth'),
            'lastvisit' => Yii::t('app', 'Lastvisit'),
            'hitsrobots' => Yii::t('app', 'Hitsrobots'),
            'domain' => Yii::t('app', 'Domain'),
        ];
    }
}
