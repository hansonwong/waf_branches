<?php
namespace app\logic\waf\common;

use Yii;
use app\models\Rules;
use app\models\RulesCustom;
use app\models\RuleModel;
use app\logic\waf\models\SelectList;
use yii\helpers\Html;

class WafRuleModel
{
    /**
     * 更新数据库存的默认模板
     * 根据$status(0,1)状态，更新RuleModel数据库的rule字段，停用 0 规则ID入库，启用 1 删除规则ID
     * @param $status
     * @param $idArr
     * @return array
     */
    public static function updateRule($status, $idArr)
    {
        $data = ['code'=>'F', 'info'=>'未知'];
        if( !in_array($status, [0,1]) )
        {
            $data['info'] = 'status参数不对';
            return $data;
        }

        if( empty($idArr) )
        {
            $data['info'] = '更新的realid为空';
            return $data;
        }

        $ruleModel = RuleModel::find()->where("type=3 and isDefault=1")->asArray()->one();
        if( empty($ruleModel) )
        {
            $data['info'] = "找不到预设模板";
            return $data;
        }

        $rule_arr = json_decode($ruleModel['rule']);

        // 停用 0 规则ID入库
        $rule_id_arr = array();
        if( $status==0 )
        {
            // 合并 未被选中数据
            $rule_id_arr = array_merge($idArr, $rule_arr);
        }
        // 启用 1 删除规则ID
        if( $status==1 )
        {
            // 去掉 被启用的
            $rule_id_arr = array_diff($rule_arr, $idArr);
        }

        $rules = json_encode(array_values(array_unique($rule_id_arr)));

        if( RuleModel::updateAll(['rule'=>$rules], "id={$ruleModel['id']}") < 1 )
        {
            $data['info'] = "更新RuleModel的rule失败";
            return $data;
        }

        $data['code'] = "T";
        $data['info'] = "成功";

        return $data;
    }

    /**
     * 根据$route所需要的地方返回列表头名字
     *[
     *{"sTitle":"规则ID","data":"rulesID"},
     *{"sTitle":"规则名称","data":"rulesName","sClass":"rulesName"},
     *{"sTitle":"备注","data":"beizhu","width":280},
     *]
     * @return string
     */
    public static function GridHeaderRule_G()
    {
        $title = [
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('ruleId'),"data"=>"realid", 'width'=>100], //规则ID
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('rulesName'),"data"=>"name","sClass"=>"rulesName", "align"=> 'left'], //规则名称
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('category'),"data"=>"ruleCatName", 'width'=>120], //类别
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('interceptionMode'),"data"=>"actionCatName", 'width'=>100], //拦截方式
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('remarks'),"data"=>"desc"], //备注
        ];

        return json_encode($title);
    }

    /**
     * @param bool $_is_user_defined
    {
    "data":[
    {"rulesID":"2005190","way":"默认动作","grade":"高危","beizhu":"检测请求行中是否包含/models/category.php并且catid 参数中是否带有 SQL语句（select from）如果是，则判断为 Joomla! SQL注入尝试。将会阻断并设置相关参数","type":"CM漏洞攻击","serverSelect":"1","time":"2016-01-30 10:00:00","rulesName":"Joomla! SQL注入尝试（1）","sTypeName":"CMS漏洞攻击 (387个规则集)"},
    {"rulesID":"2005190","way":"默认动作","grade":"高危","beizhu":"站点组","type":"CM漏洞攻击","serverSelect":"1","time":"2016-01-30 10:00:00","rulesName":"规则名称3","sTypeName":"组3"}
    ],
    "Total":"16"
    }
     * @return string
     */
    public static function GridBodyRule_G($_is_user_defined=false)
    {
        // 搜索
        $key = trim(Yii::$app->request->post('key',''));
        $content = trim(Yii::$app->request->post('content',''));

        // 排序
        $sortName = Yii::$app->request->post('sortname','type');
        $sortOrder = Yii::$app->request->post('sortorder','ASC');
        $orderBy = "{$sortName} {$sortOrder}";
        if( strlen($orderBy)<1 )
        {
            $orderBy = "type ASC";
        }

        // 整合搜索条件
        $whereStr = '1 ';
        $isWhere = 0;
        if( $key == 'realid' && strlen($content)>0 )
        {
            $whereStr .= "AND realid={$content}";
            $isWhere = 1;
        }
        if( $key == 'name' && strlen($content)>0 )
        {
            $whereStr .= "AND name LIKE '%{$content}%'";
            $isWhere = 1;
        }

        $RulesModel = Rules::find()->select(['type', 'count(*) as c'])->groupBy(['type'])->asArray()->all();
        $RulesModelArr = array_column($RulesModel,'c','type');
        unset($RulesModel);

        // 拦截方式
        $ActionCatArr = SelectList::actionCatArr();

        // 攻击类别
        $RuleCatArr = SelectList::ruleCatArr();

        // 个规则集
        $ruleSetL = Yii::$app->sysLanguage->getTranslateBySymbol('ruleSet');

        $list = [];
        // 查询字段
        $select = "realid,name,type,status,action,desc";
        $model =  Rules::find()->select($select)->where($whereStr)->orderBy($orderBy)->asArray()->all();
        foreach( $model as $v )
        {
            // 整理输出数据
            $list[] = [
                "realid" => $v['realid'],
                "name" => $v['name'],
                "actionCatName" => $ActionCatArr[$v['action']],
                "ruleCatName" => $RuleCatArr[$v['type']],
                "desc" => htmlspecialchars($v['desc']),
                "sTypeName" => "{$RuleCatArr[$v['type']]} ({$RulesModelArr[$v['type']]}{$ruleSetL})", //个规则集
                "isWhere" => $isWhere // 为了区别搜索时，不收缩显示
            ];
        }

        // 追加上自定义规则
        if( $_is_user_defined===true && $isWhere==0 )
        {
            $selectArr = ['realid', 'name', 'type', 'action', 'desc'];
            $customRulesModel = RulesCustom::find()->select($selectArr)->asArray()->all();
            $customRulesModel_count = count($customRulesModel);
            foreach( $customRulesModel as $v )
            {
                // 整理输出数据
                $list[] = [
                    "realid" => $v['realid'],
                    "name" => Html::encode($v['name']),
                    "actionCatName" => $ActionCatArr[$v['action']],
                    "ruleCatName" => $RuleCatArr[$v['type']],
                    "desc" => htmlspecialchars($v['desc']),
                    "sTypeName" => "{$RuleCatArr[$v['type']]} ({$customRulesModel_count}{$ruleSetL})", //个规则集
                    "isWhere" => $isWhere // 为了区别搜索时，不收缩显示
                ];
            }
        }

        $data = [
            'data'=>$list,
            'total' => Rules::find()->where($whereStr)->count(),
            "isWhere" => $isWhere // 为了区别搜索时，不收缩显示
        ];

        return json_encode($data);
    }

    public static function beforeRuleModelDelete($idArr){
        if(!is_array($idArr)) return false;
        $idArr = implode(",", $idArr);
        // 计算有没有正在使用的模板
        $WebSiteCount = \app\models\WebSite::find()->where("ruleModelId IN ({$idArr}) OR selfRuleModelId IN ({$idArr})")->count();
        $WebsiteGroupCount = \app\models\WebsiteGroup::find()->where("ruleModelId IN ({$idArr})")->count();
        $ruleCustomDefendPolicyCount = \app\models\RuleCustomDefendPolicy::find()->where("rule IN ({$idArr})")->count();
        if( $WebSiteCount>0 || $WebsiteGroupCount>0 || $ruleCustomDefendPolicyCount>0 )
        {
            $info = Yii::$app->sysLanguage->getTranslateBySymbol('canNotDeleteUsingTemplate'); //'不能删除正在使用的模板！';
            Yii::$app->sysJsonMsg->msg(false, $info);
        }
    }


    /**
     * 根据自定义规则，删除时，也删除规则模板里的rule里的realid
     * @param int $realid
     * @return bool
     */
    public static function updateRuleByCustomRulesDelete($realid)
    {
        if( intval($realid)<1 ) return false;

        $models = RuleModel::find()->select(['id'])->asArray()->all();
        if( empty($models) )
        {
            return true;
        }

        foreach( $models as $v )
        {
            $model =RuleModel::findOne($v['id']);
            $ruleArr = json_decode($model->rule, true);
            if( empty($ruleArr) ) continue;

            $_ruleArr =  array_filter($ruleArr, function ($element) use ($realid) { return ($element != $realid); } );
            $model->rule = json_encode($_ruleArr);
            $model->save();
        }

        return true;
    }
}