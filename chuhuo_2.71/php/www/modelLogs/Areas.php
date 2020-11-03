<?php

namespace app\modelLogs;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;

/**
 * This is the model class for table "t_areas".
 *
 * @property string $Code
 * @property string $Province
 * @property string $Area
 * @property string $Desc
 */
class Areas extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_areas';
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
            [['Code', 'Province', 'Area', 'Desc'], 'required'],
            [['Code'], 'string', 'max' => 2],
            [['Province'], 'string', 'max' => 16],
            [['Area', 'Desc'], 'string', 'max' => 32],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'Code' => 'Code',
            'Province' => 'Province',
            'Area' => 'Area',
            'Desc' => 'Desc',
        ];
    }

    /**
     * 字段修改、添加配置
     * @return array
     */
    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->model_name;

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
