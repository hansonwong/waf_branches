<?php

namespace app\models;

use Yii;

/**
 * This is the model class for table "t_cyclereport".
 *
 * @property integer $id
 * @property string $name
 * @property integer $type
 * @property string $desc
 * @property integer $cycle
 * @property integer $sendmail
 * @property string $format
 */
class CycleReport extends \yii\db\ActiveRecord
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_cyclereport';
    }

    /**
     * @inheritdoc
     */
    public function rules()
    {
        return [
            [['type', 'cycle', 'sendmail'], 'integer'],
            [['name'], 'string', 'max' => 100],
            [['desc'], 'string', 'max' => 255],
            [['format'], 'string', 'max' => 10],
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
            'type' => Yii::t('app', '1IDS report, 2 flow report, 3 access report'),
            'desc' => Yii::t('app', 'Desc'),
            'cycle' => Yii::t('app', '1year, 2month 3week 4day'),
            'sendmail' => Yii::t('app', '0 no send mail, 1 send mail'),
            'format' => Yii::t('app', 'report output format :html、doc、pdf'),
        ];
    }
}
