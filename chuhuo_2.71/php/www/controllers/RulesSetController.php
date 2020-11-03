<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\logic\waf\common\WafRuleModel;

/**
 * 安全管理 - 规则配置 - 自定义规则模板
 */
class RulesSetController extends BaseController
{
    public $model = '\\app\\models\\RuleModel';

    public function actionIndex()
    {
        // 返回内置规则头部数据
        if( Yii::$app->request->get('op')=='headerRule' ) return WafRuleModel::GridHeaderRule_G();

        // 返回内置规则头部数据
        if( Yii::$app->request->get('op')=='bodyRule' ) return WafRuleModel::GridBodyRule_G(true);

        return parent::actionIndex();
    }

    public function actionDelete()
    {
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];

        \app\logic\waf\common\WafRuleModel::beforeRuleModelDelete($id);
        $result = parent::actionDelete();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        return $result;
    }
}
