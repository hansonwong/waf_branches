<?php

namespace app\models;

use Yii;
use app\logic\model\BaseModel;
/**
 * This is the model class for table "t_httpver".
 *
 * @property integer $id
 * @property string $name
 * @property integer $status
 */
class HttpVersion extends BaseModel
{
    public static function tableName()
    {
        return 't_httpver';
    }

    public function rulesSource()
    {
        return [
            [['id'], 'required'],
            [['id', 'status'], 'integer'],
            [['name'], 'string', 'max' => 45],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'name' => 'HTTP协议版本名称',
            'status' => 'HTTP协议版本状态',
        ];
    }
}
