<?php

namespace app\models;

use Yii;

use app\widget\AdminListConfig;

/**
 * This is the model class for table "t_ha_setting".
 *
 * @property integer $id
 * @property integer $is_use
 * @property string $interface
 * @property integer $vhid
 * @property string $password
 * @property string $state
 * @property string $ip
 * @property string $database_ip
 * @property string $database_port
 * @property integer $is_setting
 * @property integer $server_id
 * @property integer $offset_id
 * @property integer $had_sync
 * @property integer $priority
 * @property string $bridge
 * @property integer $is_port_aggregation
 * @property integer $database_sync_status
 */
class HaSetting extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_ha_setting';
    }

    /**
     * @inheritdoc
     */
    public function rulesSource()
    {
        return [
            [['is_use', 'vhid', 'is_setting', 'server_id', 'offset_id', 'had_sync', 'priority', 'is_port_aggregation', 'database_sync_status'], 'integer'],
            [['interface'], 'string', 'max' => 6],
            [['password', 'ip', 'database_ip'], 'string', 'max' => 16],
            [['state'], 'string', 'max' => 7],
            [['priority'], 'compare', 'compareValue' => 1, 'operator' => '>=', 'message' => '优先级范围为0-255'],
            [['priority'], 'compare', 'compareValue' => 255, 'operator' => '<=', 'message' => '优先级范围为0-255'],
            [['bridge'], 'string', 'max' => 45],
            [['database_sync_status','is_port_aggregation','is_use'], 'in', 'range' => [0,1]],
        //[[ 'password'], 'required','message' => 'pwd为空'],
            [['interface'], 'required', 'message' => '请选择监控接口'],
            [['ip'], 'required', 'message' => '选中的接口没有设置IP地址'],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'id' => Yii::t('app', 'ID'),
            'is_use' => Yii::t('app','Is Use'),
            'interface' => Yii::t('app','Interface'),
            'vhid' => Yii::t('app','Vhid'),
            'password' => Yii::t('app','Password'),
            'state' => Yii::t('app','State'),
            'ip' => Yii::t('app','Ip'),
            'database_ip' => Yii::t('app','Database Ip'),
            'database_port' => Yii::t('app','Database Port'),
            'is_setting' => Yii::t('app','Is Setting'),
            'server_id' => Yii::t('app','Server ID'),
            'offset_id' => Yii::t('app', 'Offset ID'),
            'had_sync' => Yii::t('app','Had Sync'),
            'priority' => Yii::t('app','Priority'),
            'bridge' => Yii::t('app','Bridge'),
            'is_port_aggregation' => Yii::t('app','Is Port Aggregation'),
            'database_sync_status' => Yii::t('app','Database Sync Status'),
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
