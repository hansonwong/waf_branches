<?php

namespace app\models;

use Yii;
use app\logic\model\BaseModel;
/**
 * This is the model class for table "t_httptypeset".
 *
 * @property integer $id
 * @property string $name
 * @property string $desc
 * @property integer $selected
 */
class HttpTypeSet extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_httptypeset';
    }

    /**
     * @inheritdoc
     */
    public function rulesSource()
    {
        return [
            [['id', 'name'], 'required'],
            [['id', 'selected'], 'integer'],
            [['name', 'desc'], 'string', 'max' => 45],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'name' => 'HTTP请求动作名称',
            'desc' => '说明',
            'selected' => '启用选择',
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
