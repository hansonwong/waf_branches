<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
/**
 * This is the model class for table "t_rule_model".
 *
 * @property integer $id
 * @property string $rule
 * @property integer $type
 * @property integer $groupModelId
 * @property string $different
 * @property string $name
 * @property string $remark
 * @property integer $ischecked
 *
 * @property RuleModel $groupModel
 * @property RuleModel[] $ruleModels
 * @property Website[] $tWebsites
 * @property Website[] $tWebsites0
 * @property WebsiteGroup[] $tWebsiteGroups
 */
class RulesDefault extends RuleModel
{
    public $updateEvent = true;

    public function rulesSource()
    {
        return [
            [['rule'], function($attribute, $params){
                $ruleUnChecked = json_decode($this->$attribute,true);
                $this->$attribute = json_encode(array_values(array_unique($ruleUnChecked)));
            }, 'skipOnEmpty' => false],
            [['rule'], 'string'],
        ];
    }

    public function afterSave($insert, $changedAttributes)
    {
        if($this->updateEvent) self::syncRulesStatus();
        parent::afterSave($insert, $changedAttributes);
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => [['type' => 3],],
            '~' => ['name',],
        ]);
        return ['query' => $query];
    }

    public function ListTable()
    {
        $reset = Yii::$app->sysLanguage->getTranslateBySymbol('reset');

        return [
            'publicButton' => [
                ['button' => "<input type=button class='btn c_o btn_del' value='{$reset}' onclick='ruleReset(0, 1);'>", 'authorityPass' => true],
                ['button' =>
                    '<span style="padding-left: 25px; font-weight: bold;">'.
                    Yii::$app->sysLanguage->getTranslateBySymbol('defaultTemplateTips').
                    '</span>', 'authorityPass' => true],
            ],
            'field' => [
                'name' => ['type' => 'callback', 'val' => function($obj, $val){
                    return Yii::$app->sysLanguage->getTranslate($val);
                }],
                'type' => ['type' => 'callback', 'val' => function($obj, $val){
                    return $val == 3 ?
                        Yii::$app->sysLanguage->getTranslateBySymbol('siteGroupTemplate'):
                        Yii::$app->sysLanguage->getTranslateBySymbol('undefinition');
                }],
                'remark' => ['type' => 'callback', 'val' => function($obj, $val){
                    return Yii::$app->sysLanguage->getTranslate($val);
                }],
                'isDefault' => ['type' => 'callback', 'val' => function($obj, $val){
                    $class = (1 == $val) ? 'bt_qyan' : 'bt_tyan';
                    $str =  (1 == $val) ? 'enable' : 'stopUse';
                    $status = 1 == $val ? 0 : 1;
                    $str = Yii::$app->sysLanguage->getTranslateBySymbol($str);
                    return "<input type=button class='qt {$class}' onclick='statusChange({$obj->primaryKey}, {$status});' title='{$str}'>";
                }],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php').
                \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php', [
                    'config' => ['url' => 'reset', 'jsFuntionName' => 'ruleReset']
                ]),
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

        #获取继承模板配置
        $groupModelIdConfig = SelectList::ruleModelGroup('select');
        #unset继承模板配置中当前id
        if(null !== $this->id) unset($groupModelIdConfig['data'][$this->id]);

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'name' => [
                    'showType' => 'show',
                    'default' => [
                        'type' => 'callback',
                        'val' => function($obj, $val){
                            return Yii::$app->sysLanguage->getTranslate($val);
                        }
                    ],
                ],
                'remark' => [
                    'showType' => 'show',
                    'default' => [
                        'type' => 'callback',
                        'val' => function($obj, $val){
                            return Yii::$app->sysLanguage->getTranslate($val);
                        }
                    ],
                ],
                'id' => ['showType' => 'hidden'],
                'rule' => [
                    'showType' => 'hidden',
                    'default' => [
                        'type' => 'callback',
                        'val' => function($obj, $val){
                            if( $obj->groupModelId )
                            {
                                $ruleArr = json_decode($obj->rule, true);

                                $ruleGroup = RuleModel::findOne($obj->groupModelId);
                                $ruleGroupArr = json_decode($ruleGroup->rule, true);

                                $ruleUnChecked = array_unique(array_merge($ruleArr, $ruleGroupArr));
                                sort($ruleUnChecked);

                                // 当前模板跟继承模板被选中部分
                                $differentArr = [];
                                if( strlen($obj->different)>0 )
                                    $differentArr = json_decode($obj->different, true);

                                // 计算未选中与被选中的差集
                                return json_encode(array_values(array_diff($ruleUnChecked, $differentArr)));
                            }
                            return $val;
                        }
                    ],
                ],
                'ruleDefault' => ['showType' => 'hidden'],
                'different' => ['showType' => 'hidden'],
                'ischecked' => ['showType' => 'hidden'],
                'type' => ['showType' => 'hidden'],
                'groupModelId' => ['showType' => 'hidden'],
            ],
            'customStr' => \Yii::$app->view->renderFile('@app/views/rules-set/edit-component.php'),
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

    //更新状态
    public static function updateStatus(){
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];
        $status = $query['status'];

        self::updateAll(['isDefault'=> 0], ['type' => 3]);
        self::updateAll(['isDefault'=>$status], ['id' => $id]);
        self::syncRulesStatus();

        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }

    //重置
    public static function reset(){
        $model = new self;
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];
        if(!is_array($id)) return false;
        foreach ($id as $item) {
            if ('' != $item) {
                $obj = $model->findOne($item);
                $obj->rule = $obj->ruleDefault;
                $obj->updateEvent = false;
                $obj->save(false);
            }
        }

        self::syncRulesStatus();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }

    // 同步当前模板到内置规则库去
    public static function syncRulesStatus()
    {
        $ruleModel = self::find()->select(['id'])->where(['type' => 3, 'isDefault' => 1])->one();
        $model = self::findOne($ruleModel->id);
        $ruleArr = json_decode($model->rule,true);
        if( empty($ruleArr) ) return true;

        // 判断是不是所有都是数字型
        foreach( $ruleArr as $v ) {
            if( !ctype_digit($v) ) return false;
        }
        // 把内置规则库， 全部更新为启用
        Rules::updateAll(['status'=> 1], ['status'=> 0]);
        // 把当前预设规则模板没有被启用的rule的id,更新内置规则为0， 未启用
        Rules::updateAll(['status'=> 0], ['realid' => $ruleArr]);

        return true;
    }
}
