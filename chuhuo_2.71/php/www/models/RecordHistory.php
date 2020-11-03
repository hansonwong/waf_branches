<?php

namespace app\models;

use Yii;

/**
 * This is the model class for table "t_record_history".
 *
 * @property integer $id
 * @property string $new_table_name
 * @property integer $start_time
 * @property integer $end_time
 * @property string $ori_table_name
 */
class RecordHistory extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_record_history';
    }

    /**
     * @inheritdoc
     */
    public function rulesSource()
    {
        return [
            [['start_time', 'end_time'], 'integer'],
            [['new_table_name', 'ori_table_name'], 'string', 'max' => 255],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => Yii::t('app', 'ID'),
            'new_table_name' => Yii::t('app', 'New Table Name'),
            'start_time' => Yii::t('app', 'Start Time'),
            'end_time' => Yii::t('app', 'End Time'),
            'ori_table_name' => Yii::t('app', 'Ori Table Name'),
        ];
    }
}
