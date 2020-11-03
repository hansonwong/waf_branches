<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "pages_201101".
 *
 * @property integer $id
 * @property string $year_monthed
 * @property string $url
 * @property integer $pages
 * @property string $bandwidth
 * @property integer $entry
 * @property integer $exited
 * @property string $domain
 */
class PagesModel extends \app\logic\model\BaseModel
{
    public static $table_name;

    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        if (!self::$table_name) self::$table_name = date("Ym");
        return 'pages_' . self::$table_name;
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
            [['year_monthed', 'url', 'pages', 'bandwidth', 'entry', 'exited', 'domain'], 'required'],
            [['pages', 'bandwidth', 'entry', 'exited'], 'integer'],
            [['year_monthed'], 'string', 'max' => 6],
            [['url'], 'string', 'max' => 100],
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
            'url' => Yii::t('app', 'Url'),
            'pages' => Yii::t('app', 'Pages'),
            'bandwidth' => Yii::t('app', 'Bandwidth'),
            'entry' => Yii::t('app', 'Entry'),
            'exited' => Yii::t('app', 'Exited'),
            'domain' => Yii::t('app', 'Domain'),
        ];
    }
}
