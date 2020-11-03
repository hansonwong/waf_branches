<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
/**
 * 攻击类别
 * This is the model class for table "t_rulecat".
 *
 * @property integer $id
 * @property string $name
 * @property string $desc
 */
class RuleCat extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_rulecat';
    }

    /**
     * @inheritdoc
     */
    public function rules()
    {
        return [
            [['id', 'name'], 'required'],
            [['id'], 'integer'],
            [['name'], 'string', 'max' => 45],
            [['desc'], 'string', 'max' => 255],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'name' => 'Name',
            'desc' => 'Desc',
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
