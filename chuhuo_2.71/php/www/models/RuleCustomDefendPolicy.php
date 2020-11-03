<?php

namespace app\models;

use Yii;
use \yii\helpers\Url;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;

/**
 * This is the model class for table "rule_custom_defend_policy".
 *
 * @property integer $id
 * @property string $name
 * @property string $rule
 * @property string $status
 * @property string $source_ip
 * @property string $destination_ip
 * @property string $destination_url
 */
class RuleCustomDefendPolicy extends BaseModel
{
    public $sendPipe = true;

    public static function tableName()
    {
        return 'rule_custom_defend_policy';
    }

    public function rulesSource()
    {
        return [
            [['name', 'status', 'rule'], 'required'],
            [['name'], 'unique'],
            [['status'], 'default', 'value' => 1],
            [['destination_url'], 'url'],
            [['rule'], 'integer'],
            [['name'], 'string', 'max' => 100],
            [['status'], 'in', 'range' => [0, 1]],
            [['destination_url'], 'string', 'max' => 255],
            [['destination_url'], 'filter', 'filter' => function($value){
                return rtrim($value, '/');
            }],
            [['source_ip', 'destination_ip'], \app\logic\validator\IpValidator::className(), 'type' => 'mix', 'typeMix' => ['ip', 'ipIntervalFor4', 'ipWithMask'], 'skipOnEmpty' => false, 'skipOnError' => false],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'name' => '策略名',
            'rule' => '规则模板',
            'status' => '启用',
            'source_ip' => '来源IP',
            'destination_ip' => '目标IP',
            'destination_url' => '目标Url',
        ];
    }

    public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);
        if($this->sendPipe) Yii::$app->wafHelper->pipe('CMD_NGINX');
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['status',],
            '~' => ['name', 'source_ip', 'destination_ip', 'destination_url'],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => [
                'name', 'status' => SelectList::enable('select'),
                'source_ip', 'destination_ip', 'destination_url',
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        $enable = Yii::$app->sysLanguage->getTranslateBySymbol('enable');
        $stopUse = Yii::$app->sysLanguage->getTranslateBySymbol('stopUse');

        return [
            'publicButton' => [
                ['button' => "<input type=button class='btn c_b btn_open' value='{$enable}' onclick='statusChange(0, 1);'>", 'authorityPass' => true],
                ['button' => "<input type=button class='btn c_o btn_stop' value='{$stopUse}' onclick='statusChange(0, 0);'>", 'authorityPass' => true],
            ],
            'field' => ['name',
                'rule' => ['type' => 'switch', 'val' => SelectList::rulesSet('switch')],
                'source_ip', 'destination_ip', 'destination_url',
                'status' => ['type' => 'callback', 'val' => function($obj, $val){
                    $class = (1 == $val) ? 'bt_qyan' : 'bt_tyan';
                    $str =  (1 == $val) ? 'enable' : 'stopUse';
                    $status = 1 == $val ? 0 : 1;
                    $str = Yii::$app->sysLanguage->getTranslateBySymbol($str);
                    return "<input type=button class='qt {$class}' onclick='statusChange({$obj['id']}, {$status});' title='{$str}'>";
                }],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php'),
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        #$js = \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/edit-component.php');
        $fieldType = [
            'id' => ['showType' => 'hidden'],
            'status' => SelectList::enable('select'),
            'rule' => SelectList::rulesSet('select'),
            'source_ip' => [
                #'type' => 'select',#input输入组件类型
                #'default' => '1223',#字段默认值
                #'default' => ['type' => 'custom', 'valType' => 'datetime'],#字段默认值
                #'showType' => 'disable',#字段显示方式(notShow[不显示无hidden],show[显示无hidden],hidden[不显示有hidden],disable[显示但不可改,有hidden])
                #'tips' => '注意XXX',#提示信息
                'tipsTKey' => 'ruleCustomDefendPolicyIpLimitTips',#提示信息(自动翻译key)
                #'parentKey' => false,#不使用父KEY(model名称),默认true
                #'valueByModel' => false,#不使用model的字段值,默认true
            ],
            'destination_ip' => [
                #'type' => 'select',#input输入组件类型
                #'default' => '1223',#字段默认值
                #'default' => ['type' => 'custom', 'valType' => 'datetime'],#字段默认值
                #'showType' => 'disable',#字段显示方式(notShow[不显示无hidden],show[显示无hidden],hidden[不显示有hidden],disable[显示但不可改,有hidden])
                #'tips' => '注意XXX',#提示信息
                'tipsTKey' => 'ruleCustomDefendPolicyIpLimitTips',#提示信息(自动翻译key)
                #'parentKey' => false,#不使用父KEY(model名称),默认御前
                #'valueByModel' => false,#不使用model的字段值,默认true
                #'rowStyle' => 2,#2列样式,默认3列样式
            ],
            /*'xxx' => [
                'type' => 'multipleVal', 'length' => 0,
                'height' => '100px',
                'default' => ['type'=> 'custom', 'valType' => 'json_decode',],
                'rowStyle' => 2,
            ],*/
        ];
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => $fieldType,
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

    public static function updateStatus(){
        $model = new self;
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];
        $status = $query['status'];
        if(!is_array($id)) return false;
        foreach ($id as $item) {
            if ('' != $item) {
                $obj = $model->findOne($item);
                $obj->sendPipe = false;
                $obj->status = $status;
                $obj->save(false);
            }
        }
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }
}
