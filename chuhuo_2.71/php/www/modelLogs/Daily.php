<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "daily".
 *
 * @property integer $id
 * @property string $day
 * @property integer $visits
 * @property integer $pages
 * @property integer $hits
 * @property string $bandwidth
 * @property string $domain
 */
class Daily extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'daily';
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
            [['day', 'visits', 'pages', 'hits', 'bandwidth', 'domain'], 'required'],
            [['visits', 'pages', 'hits', 'bandwidth'], 'integer'],
            [['day'], 'string', 'max' => 8],
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
            'day' => Yii::t('app', 'Day'),
            'visits' => Yii::t('app', 'Visits'),
            'pages' => Yii::t('app', 'Pages'),
            'hits' => Yii::t('app', 'Hits'),
            'bandwidth' => Yii::t('app', 'Bandwidth'),
            'domain' => Yii::t('app', 'Domain'),
        ];
    }
}
