<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "general".
 *
 * @property integer $id
 * @property string $year_monthed
 * @property integer $visits
 * @property integer $visits_unique
 * @property integer $pages
 * @property integer $hits
 * @property string $bandwidth
 * @property integer $pages_nv
 * @property integer $hits_nv
 * @property string $bandwidth_nv
 * @property integer $hosts_known
 * @property integer $hosts_unknown
 * @property string $domain
 */
class General extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'general';
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
            [['year_monthed', 'visits', 'visits_unique', 'pages', 'hits', 'bandwidth', 'pages_nv', 'hits_nv', 'bandwidth_nv', 'hosts_known', 'hosts_unknown', 'domain'], 'required'],
            [['visits', 'visits_unique', 'pages', 'hits', 'bandwidth', 'pages_nv', 'hits_nv', 'bandwidth_nv', 'hosts_known', 'hosts_unknown'], 'integer'],
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
            'year_monthed' => Yii::t('app', 'Year Monthed'),
            'visits' => Yii::t('app', 'Visits'),
            'visits_unique' => Yii::t('app', 'Visits Unique'),
            'pages' => Yii::t('app', 'Pages'),
            'hits' => Yii::t('app', 'Hits'),
            'bandwidth' => Yii::t('app', 'Bandwidth'),
            'pages_nv' => Yii::t('app', 'Pages Nv'),
            'hits_nv' => Yii::t('app', 'Hits Nv'),
            'bandwidth_nv' => Yii::t('app', 'Bandwidth Nv'),
            'hosts_known' => Yii::t('app', 'Hosts Known'),
            'hosts_unknown' => Yii::t('app', 'Hosts Unknown'),
            'domain' => Yii::t('app', 'Domain'),
        ];
    }
}
