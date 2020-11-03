<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;

/**
 * This is the model class for table "t_severity".
 *
 * @property integer $severity
 * @property string $name
 * @property string $desc
 */
class Severity extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_severity';
    }

    /**
     * @inheritdoc
     */
    public function rules()
    {
        return [
            [['severity'], 'required'],
            [['severity'], 'integer'],
            [['name', 'desc'], 'string', 'max' => 45],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'severity' => 'Severity',
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
            'fieldType' => [
                'id' => ['showType' => 'hidden'],
            ],
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
