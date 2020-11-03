<?php

namespace app\models;

use Yii;
use app\logic\model\BaseModel;
/**
 * This is the model class for table "t_restrictheaders".
 *
 * @property integer $id
 * @property string $name
 * @property integer $status
 */
class RestrictHeaders extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_restrictheaders';
    }

    /**
     * @inheritdoc
     */
    public function rulesSource()
    {
        return [
            [['id'], 'required'],
            [['id', 'status'], 'integer'],
            [['name'], 'string', 'max' => 45],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'name' => 'HTTP头字段名称',
            'status' => 'HTTP头字段状态',
        ];
    }

    /**
     * 字段修改、添加配置
     * @return array
     */
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
