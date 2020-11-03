<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\model\BaseModel;
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
class RuleModel extends BaseModel
{
    public $sendPipe = true;

    public static function tableName()
    {
        return 't_rule_model';
    }

    public function rulesSource()
    {
        return [
            [['groupModelId'], function($attribute, $params){
                if($this->type == 2 && ('' == $this->$attribute || null == $this->$attribute))
                {
                    $tips = Yii::$app->sysLanguage->getTranslateBySymbol('templateTypeIsChosenAsSiteTemplateTips'); //'选择了模板类型为站点模板，但没有选择所属站点组模板';
                    $this->addError($attribute, $tips);
                }
            }, 'skipOnEmpty' => false],
            [['type'], function($attribute, $params){
                // 未选中的
                $ruleUnChecked = json_decode($this->rule,true);

                $different = [];
                // 站点模板，有继承处理
                if($this->$attribute == 2)
                {
                    if(!$this->groupModelId) return;
                    $RuleModel = RuleModel::findOne($this->groupModelId);
                    //var_dump($RuleModel);
                    $RuleModelRuleArr = json_decode($RuleModel->rule, true);

                    $different = [];
                    foreach( $RuleModelRuleArr as $v )
                    {
                        // 判断出当前模板与继承模板被，未被选中的又被选中的情况
                        if(!in_array($v, $ruleUnChecked)) array_push($different, $v);
                    }

                    $rule = [];
                    foreach( $ruleUnChecked as $v )
                    {
                        // 重新计算当前模板未被选中的有没有包含在继承模板中
                        if(!in_array($v, $RuleModelRuleArr)) array_push($rule, $v);
                    }

                    $ruleUnChecked = $rule;
                }

                $this->rule = json_encode($ruleUnChecked);
                $this->different = json_encode($different);

                //如果 模板类型 为站点组模板，就没有继承模板的
                if($this->$attribute == 1) $this->groupModelId = NULL;
            }, 'skipOnEmpty' => false],
            [['rule', 'different', 'ruleDefault'], 'string'],
            [['type', 'ischecked'], 'integer'],
            ['type', 'in', 'range' => [1, 2, 3]],
            [['groupModelId'],'match','pattern'=>'/NULL|\d/'],
            [['type', 'ischecked'], 'integer'],
            [['type', 'name'], 'required'],
            [['name'], 'string', 'max' => 100],
            ['name', 'unique'],
            [['remark'], 'string', 'max' => 355],
            [['groupModelId'], 'exist', 'skipOnError' => true, 'targetClass' => RuleModel::className(), 'targetAttribute' => ['groupModelId' => 'id']],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'rule' => '策略内容',
            'ruleDefault' => '预设策略',
            'type' => '模板类型',
            'groupModelId' => '继承模板',
            'different' => 'Different',
            'name' => '规则模板名称',
            'remark' => '备注',
            'ischecked' => '站点组启用状态',
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
            '=' => ['type',],
            '!=' => [['type' => 3]],
            '~' => ['name',],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => [
                'type' => SelectList::ruleModelTplType('select'),
                'name',
                ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        return [
            'publicButton' => [],
            'field' => [
                'name',
                #'groupModelId' => ['type' => 'foreignKey', 'val' => 'groupModel:name'],
                'groupModelId' => ['type' => 'callback', 'val' => function($obj, $val){
                    $model = $obj->groupModel;
                    return Yii::$app->sysLanguage->getTranslate($model->name);
                }],
                'type' => ['float' => 'c', 'type' => 'switch', 'val' => SelectList::ruleModelTplType('switch')],
                'remark',
                'ischecked' => ['float' => 'c', 'type' => 'switch', 'val' => SelectList::enable('switch')],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php').
                \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php', [
                    'config' => ['url' => 'reset', 'jsFuntionName' => 'ruleReset']
                ]),
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
                'type' => array_merge(
                    SelectList::ruleModelTplType('select'),
                    ['inputProperty' => 'onchange="showGroupModelId(this)"']
                ),
                'groupModelId' => array_merge(
                    $groupModelIdConfig,
                    [
                        'tipsTKey' => 'inheritanceTemplateByTemplateTypeTips',
                        'inputProperty' => 'onchange="changeGroupModelId(this)"'
                    ]
                ),
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

    public function getGroupModel()
    {
        return $this->hasOne(RuleModel::className(), ['id' => 'groupModelId']);
    }

    public function getRuleModels()
    {
        return $this->hasMany(RuleModel::className(), ['groupModelId' => 'id']);
    }

    public function getWebsites()
    {
        return $this->hasMany(Website::className(), ['ruleModelId' => 'id']);
    }

    public function getWebsites0()
    {
        return $this->hasMany(Website::className(), ['selfRuleModelId' => 'id']);
    }

    public function getWebsiteGroups()
    {
        return $this->hasMany(WebsiteGroup::className(), ['ruleModelId' => 'id']);
    }
}
