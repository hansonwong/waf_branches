<?php

namespace app\modelLogs;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;

/**
 * This is the model class for table "t_countrycode".
 *
 * @property string $CountryCode
 * @property string $EnCountry
 * @property string $CnCountry
 * @property string $Continent
 */
class CountryCode extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_countrycode';
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
            [['CountryCode', 'EnCountry', 'CnCountry', 'Continent'], 'required'],
            [['CountryCode'], 'string', 'max' => 3],
            [['EnCountry', 'CnCountry'], 'string', 'max' => 64],
            [['Continent'], 'string', 'max' => 16],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'CountryCode' => Yii::t('app', 'Country Code'),
            'EnCountry' => Yii::t('app', 'En Country'),
            'CnCountry' => Yii::t('app', 'Cn Country'),
            'Continent' => Yii::t('app', 'Continent'),
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
