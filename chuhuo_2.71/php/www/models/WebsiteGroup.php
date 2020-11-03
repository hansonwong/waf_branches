<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
/**
 * This is the model class for table "t_website_group".
 *
 * @property integer $id
 * @property string $groupName
 * @property integer $ruleModelId
 * @property string $explanation
 *
 * @property Website[] $tWebsites
 * @property RuleModel $ruleModel
 */
class WebsiteGroup extends BaseModel
{
    public static function tableName()
    {
        return 't_website_group';
    }

    public function rulesSource()
    {
        return [
            [['ruleModelId'], 'integer'],
            [['groupName', 'explanation'], 'string', 'max' => 255],
            [['groupName'],'required'],
            [['groupName'],'unique'],
            [['ruleModelId'], 'exist', 'skipOnError' => true, 'targetClass' => RuleModel::className(), 'targetAttribute' => ['ruleModelId' => 'id']],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'groupName' => '站点组名称',
            'ruleModelId' => '策略模板ID',
            'explanation' => '说明',

            'numberOfWebsize' => Yii::$app->sysLanguage->getTranslateBySymbol('numberOfWebsize'),
            'numberOfServers' => Yii::$app->sysLanguage->getTranslateBySymbol('numberOfServers')
        ];
    }

    public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);
        // 更新WebSite表
        WebSite::updateAll(['ruleModelId'=>$this->ruleModelId, 'selfRuleModelId'=>NULL], ['iWebSiteGroupId' => $this->id]);
        // 更新RuleModel表
        RuleModel::updateAll(['ischecked'=>1], ['id' => $this->ruleModelId]);

        Yii::$app->wafHelper->pipe('CMD_NGINX');
    }

    public function ListTable()
    {
        return [
            'field' => [
                'groupName',
                'ruleModelId' => ['type' => 'foreignKey', 'val' => 'ruleModel:name'],
                'numberOfWebsize' => ['type' => 'callback', 'val' => function($obj, $val){
                    return count($val);
                }],
                'numberOfServers',
                'explanation',
            ],
            'model' => $this,
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $fieldType = [
            'id' => ['showType' => 'hidden'],
            'numberOfWebsize' => ['showType' => 'notShow'],
            'numberOfServers' => ['showType' => 'notShow'],
            'ruleModelId' => $this->returnRuleModelId('select'),
        ];
        switch ($type) {
            case 'create' :
                break;
            case 'update' :
                break;
            default :
                ;
        }
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => $fieldType,
            'customStr' => false,
        ];
        return $field;
    }

    public function getWebsites()
    {
        return $this->hasMany(Website::className(), ['iWebSiteGroupId' => 'id']);
    }

    public function getRuleModel()
    {
        return $this->hasOne(RuleModel::className(), ['id' => 'ruleModelId']);
    }

    public function getNumberOfWebsize(){
        return WebSite::find()->select('id')->where(['iWebSiteGroupId'=> $this->id])->asArray()->all();
    }

    public function getNumberOfServers(){
        if(0 == count($this->numberOfWebsize)) return 0;
        $WebSiteIdArr = array_column($this->numberOfWebsize,'id');
        return WebSiteServers::find()->where(['webSiteId' => $WebSiteIdArr])->count();
    }

    public function returnRuleModelId($type){
        $arr = RuleModel::find()->select(['id','name','remark'])->where(['type' => [1, 3]])->asArray()->all();
        $arr = array_column($arr, 'name', 'id');
        return AdminListConfig::returnSelect($type, $arr);
    }

    //检测有没有子站点
    public static function checkBeforeDelete($idArr){
        $count = WebSite::find()->where(['iWebSiteGroupId' => $idArr])->count();
        if(0 < $count) Yii::$app->sysJsonMsg->msg(false, Yii::$app->sysLanguage->getTranslateBySymbol('selectedSiteGroupThereIsACorrespondingSite'));
    }
}
