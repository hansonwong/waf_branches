<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

/**
 * 内置规则
 * This is the model class for table "t_rules".
 *
 * @property integer $id
 * @property integer $realid
 * @property string $name
 * @property string $content
 * @property string $desc
 * @property string $type
 * @property string $action
 * @property integer $status
 * @property integer $update_time
 * @property integer $redirect_id
 */
class Rules extends BaseModel
{
    public static function tableName()
    {
        return 't_rules';
    }

    public function rulesSource()
    {
        return [
            [['id','realid', 'status', 'update_time', 'redirect_id'], 'integer'],
            [['realid'], 'required'],
            [['name'], 'string', 'max' => 255],
            [['content', 'desc'], 'string', 'max' => 1024],
            [['type', 'action'], 'string', 'max' => 45],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'realid' => '规则ID',
            'name' => '规则名称',
            'content' => '规则说明',
            'desc' => '备注',
            'type' => '攻击类别',
            'action' => '拦截方式',
            'status' => '启用状态',
            'update_time' => '更新时间',
            'redirect_id' => 'Redirect ID',
            'warn' => '危害级别',
            'harm_desc' => '危害描述',
            'suggest' => '解决建议',
        ];
    }

    /**
     * 获取 拦截方式
     * @return \yii\db\ActiveQuery
     */
    public function getActionCat()
    {
        return $this->hasOne(ActionCat::className(), ['action' => 'name']);
    }

    /**
     * 获取 攻击类别
     * @return \yii\db\ActiveQuery
     */
    public function getRuleCat()
    {
        return $this->hasOne(RuleCat::className(), ['type' => 'name']);
    }

    public function getTypeName(){
        return $this->type;
    }

    //获取类型分组和每组数量
    public static function getTypeNameCacheArr(){
        $RulesModel = self::find()->select(['type', 'count(*) as c'])->groupBy(['type'])->asArray()->all();
        return array_column($RulesModel,'c','type');
    }

    public static $getTypeNameGroupNameStrArr = null;
    public static function getTypeNameGroupName($val){
        if(null === self::$getTypeNameGroupNameStrArr){
            $str = Yii::$app->sysLanguage->getTranslateBySymbol('ruleSet');#个规则集
            $RuleCatArr = SL::ruleCatArr();
            $RulesModelArr = self::getTypeNameCacheArr();
            $strArr = [];
            foreach($RulesModelArr as $k => $v){
                $strArr[$k] = "{$RuleCatArr[$k]} ({$v}{$str})";
            }
            self::$getTypeNameGroupNameStrArr = $strArr;
        }

        return self::$getTypeNameGroupNameStrArr[$val];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['realid',],
            '~' => ['name',],
        ]);
        return ['query' => $query, 'allData' => true];
    }

    /**
     * 搜索配置
     * @return array
     */
    public function ListSearch()
    {
        return [
            'field' => ['realid', 'name'],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        $enable = Yii::$app->sysLanguage->getTranslateBySymbol('enable');
        $stopUse = Yii::$app->sysLanguage->getTranslateBySymbol('stopUse');
        $ruleModel = RuleModel::find()->select(['id', 'type', 'name'])->where(['type' => 3, 'isDefault' => 1])->one();

        return [
            'publicButton' => [
                ['button' => "<input type=button class='btn c_b btn_open' value='{$enable}' onclick='statusChange(0, 1);'>", 'authorityPass' => true],
                ['button' => "<input type=button class='btn c_o btn_stop' value='{$stopUse}' onclick='statusChange(0, 0);'>", 'authorityPass' => true],
                ['button' =>
                    '<span style="padding-left: 25px; font-weight: bold;">'.
                    Yii::$app->sysLanguage->getTranslateBySymbol('currentDefaultRuleTemplateName').': '.Yii::$app->sysLanguage->getTranslate($ruleModel->name).
                    '</span>', 'authorityPass' => true],
            ],
            'field' => [
                'realid',
                'name' => ['type' => 'callback', 'val' => function($obj, $val){
                    return Yii::$app->wafRules->getTranslation($val);
                }],
                'action' => ['type' => 'switch', 'val' => SelectList::wafActionCatArr('switch')],
                'warn' => ['type' => 'switch', 'val' => SelectList::ruleWarn('switch')],
                'type' => ['type' => 'switch', 'val' => SelectList::wafRuleCatArr('switch')],
                'status' => ['type' => 'callback', 'val' => function($obj, $val){
                    $class = (1 == $val) ? 'bt_qyan' : 'bt_tyan';
                    $str =  (1 == $val) ? 'enable' : 'stopUse';
                    $status = 1 == $val ? 0 : 1;
                    $str = Yii::$app->sysLanguage->getTranslateBySymbol($str);
                    return "<input type=button class='qt {$class}' onclick='statusChange({$obj->primaryKey}, {$status});' title='{$str}'>";
                }],
                'typeName' => ['display' => false, 'type' => 'callback', 'val' => function($obj, $val){
                    return self::getTypeNameGroupName($val);
                }],
            ],
            'recordOperation' => false,
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php',[
                    'config' => ['url' => 'update']
                ]).\Yii::$app->view->renderFile('@app/views/rules/html.php'),
        ];
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
                $obj->status = $status;
                $obj->save(false);
            }
        }
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }

    public static function getDetail(){
        $realid = Yii::$app->request->post('id');
        $model = self::find()->where(['realid'=>$realid])->asArray()->one();

        // 拦截方式
        $actionCatArr = SL::actionCatArr();

        // 攻击类别
        $ruleCatArr = SL::ruleCatArr();

        $ruleWarn = SL::ruleWarn();

        $model['actionCatName'] = $actionCatArr[$model['action']];
        $model['ruleCatName'] = $ruleCatArr[$model['type']];
        $model['statusStr'] = $model['status'] == 1 ? Yii::$app->sysLanguage->getTranslateBySymbol('enable'): Yii::$app->sysLanguage->getTranslateBySymbol('stopUse');   //'启用':'停用';

        $model['content'] = trim($model['content'])=='NULL'?'':$model['content'];
        #$model['desc'] = trim($model['desc'])=='NULL'?'':$model['desc'];

        $model['warn'] = $ruleWarn[$model['warn']];

        $model['desc'] = Yii::$app->wafRules->getTranslation("{$realid}desc");
        $model['name'] = Yii::$app->wafRules->getTranslation("{$realid}name");
        $model['harm_desc'] = Yii::$app->wafRules->getTranslation("{$realid}harm_desc");
        $model['suggest'] = Yii::$app->wafRules->getTranslation("{$realid}suggest");

        return json_encode($model);
    }
}
