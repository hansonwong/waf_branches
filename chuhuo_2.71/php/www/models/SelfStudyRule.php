<?php

namespace app\models;

use Yii;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
use app\widget\AdminListConfig;
/**
 * This is the model class for table "t_selfstudyrule".
 *
 * @property integer $id
 * @property integer $ruleid
 * @property integer $realruleid
 * @property integer $is_use
 * @property string $uri
 * @property string $host
 * @property string $sourceip
 * @property string $sourceport
 */
class SelfStudyRule extends BaseModel
{
    public $sendPipe = true;
    public static function tableName()
    {
        return 't_selfstudyrule';
    }

    public function rulesSource()
    {
        return [
            [['realruleid', 'uri', 'host'], 'required'],
            [['ruleid', 'realruleid', 'is_use'], 'integer'],
            [['ruleid'], 'default', 'value' => 0],
            [['uri', 'host'], 'string', 'max' => 255],
            [['sourceip'], 'string', 'max' => 15],
            [['sourceport'], 'string', 'max' => 5],
            [['realruleid', 'uri', 'host'], 'unique', 'targetAttribute' => ['realruleid', 'uri', 'host']],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'ruleid' => '规则ID',
            'realruleid' => '规则ID',
            'is_use' => '启用状态',
            'uri' => 'uri',
            'host' => '目标主机',
            'sourceip' => '源IP',
            'sourceport' => '源端口',
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
            '=' => ['realruleid', 'host', 'is_use',],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => [
                'realruleid', 'host',
                'is_use' => SelectList::enable('select'),
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
            'field' => [
                'realruleid',
                'is_use' => ['type' => 'callback', 'val' => function($obj, $val){
                    $class = (1 == $val) ? 'bt_qyan' : 'bt_tyan';
                    $str =  (1 == $val) ? 'enable' : 'stopUse';
                    $status = 1 == $val ? 0 : 1;
                    $str = Yii::$app->sysLanguage->getTranslateBySymbol($str);
                    return "<input type=button class='qt {$class}' onclick='statusChange({$obj['id']}, {$status});' title='{$str}'>";
                }],
                'host', 'uri'
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php'),
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        #获取继承模板配置
        $groupModelIdConfig = SelectList::ruleModelGroup('select');
        #unset继承模板配置中当前id
        if(null !== $this->id) unset($groupModelIdConfig['data'][$this->id]);

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'id' => ['showType' => 'hidden'],
                'ruleid' => ['showType' => 'hidden'],
                'is_use' => SelectList::enable('radio'),
                'sourceip' => ['showType' => 'hidden'],
                'sourceport' => ['showType' => 'hidden'],
            ],
            'customStr' => \Yii::$app->view->renderFile('@app/views/misdeclaration-defend/edit-component.php'),
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
                $obj->is_use = $status;
                $obj->save(false);
            }
        }
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }
}
