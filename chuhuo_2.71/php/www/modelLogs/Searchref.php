<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "searchref".
 *
 * @property integer $id
 * @property string $year_monthed
 * @property string $engine
 * @property integer $pages
 * @property integer $hits
 * @property string $domain
 */
class Searchref extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'searchref';
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
            [['year_monthed', 'engine', 'pages', 'hits', 'domain'], 'required'],
            [['pages', 'hits'], 'integer'],
            [['year_monthed'], 'string', 'max' => 6],
            [['engine'], 'string', 'max' => 25],
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
            'engine' => Yii::t('app', 'Engine'),
            'pages' => Yii::t('app', 'Pages'),
            'hits' => Yii::t('app', 'Hits'),
            'domain' => Yii::t('app', 'Domain'),
        ];
    }
}
