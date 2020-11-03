<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;

/**
 * 拦截方式 表
 * This is the model class for table "t_actioncat".
 *
 * @property integer $action_id
 * @property string $name
 * @property string $desc
 */
class ActionCat extends BaseModel
{
    public static function tableName()
    {
        return 't_actioncat';
    }

    public function rules()
    {
        return [
            [['action_id', 'name', 'desc'], 'required'],
            [['action_id'], 'integer'],
            [['name'], 'string', 'max' => 45],
            [['desc'], 'string', 'max' => 255],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'action_id' => 'Action ID',
            'name' => 'Name',
            'desc' => 'Desc',
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [],
            'customStr' => false,
        ];
        switch ($type) {
            case 'create' :
                break;
            case 'update' :
                break;
            default :
                ;
        }
        return $field;
    }
}
