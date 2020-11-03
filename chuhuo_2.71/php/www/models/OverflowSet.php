<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;

/**
 * This is the model class for table "t_overflowset".
 *
 * @property integer $id
 * @property string $name
 * @property integer $value
 * @property integer $status
 * @property string $secname
 */
class OverflowSet extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_overflowset';
    }

    /**
     * @inheritdoc
     */
    public function rulesSource()
    {
        return [
            [['id', 'value', 'status'], 'integer'],
            [['name', 'value'], 'required'],
            [['name'], 'string', 'max' => 45],
            [['secname'], 'string', 'max' => 100],
            ['status', 'in', 'range' => [0, 1]],
            ['value', 'integer', 'min'=>1, 'max'=>2147483647]
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'name' => '设置名称',
            'value' => '设置值',
            'status' => '状态',
            'secname' => Yii::t('app', 'Secname'),
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
