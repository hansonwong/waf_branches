<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "errors".
 *
 * @property integer $id
 * @property string $year_monthed
 * @property string $code
 * @property integer $hits
 * @property string $bandwidth
 * @property string $domain
 */
class Errors extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'errors';
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
            [['year_monthed', 'code', 'hits', 'bandwidth', 'domain'], 'required'],
            [['hits', 'bandwidth'], 'integer'],
            [['year_monthed'], 'string', 'max' => 6],
            [['code'], 'string', 'max' => 4],
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
            'code' => Yii::t('app', 'Code'),
            'hits' => Yii::t('app', 'Hits'),
            'bandwidth' => Yii::t('app', 'Bandwidth'),
            'domain' => Yii::t('app', 'Domain'),
        ];
    }
}
