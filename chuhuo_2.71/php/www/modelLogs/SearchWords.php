<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "searchwords".
 *
 * @property integer $id
 * @property string $year_monthed
 * @property string $words
 * @property integer $hits
 * @property string $domain
 */
class SearchWords extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'searchwords';
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
            [['year_monthed', 'words', 'hits', 'domain'], 'required'],
            [['hits'], 'integer'],
            [['year_monthed'], 'string', 'max' => 6],
            [['words'], 'string', 'max' => 250],
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
            'words' => Yii::t('app', 'Words'),
            'hits' => Yii::t('app', 'Hits'),
            'domain' => Yii::t('app', 'Domain'),
        ];
    }
}
