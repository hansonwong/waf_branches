<?php
namespace app\logic\waf\models;

use Yii;

class SelectList
{
    /**
     * 拦截方式
     * @param bool $isOrder
     * @return array|mixed ['allow'=>'允许访问', 'block'=>'默认动作' ]
     */
    public static function actionCatArr($isOrder=true)
    {
        $ActionCatModel = \app\models\ActionCat::find()->asArray()->all();
        if( $isOrder==false ) return $ActionCatModel;

        $arr = array_column($ActionCatModel, 'desc', 'name');
        foreach($arr as $k => $v){
            $arr[$k] = Yii::$app->sysLanguage->getTranslate($v);
        }

        return $arr;
    }

    /**
     * HTTP请求类型
     * @param int $id
     * @return array|\yii\db\ActiveRecord[]
     */
    public static function httpTypeSetArr($id=6)
    {
        $arr = \app\models\HttpTypeSet::find()->where("id<={$id}")->asArray()->all();
        $result = ['*' => Yii::$app->sysLanguage->getTranslateBySymbol('all')];
        foreach($arr as $item) $result[$item['name']] = $item['name'];
        return $result;
    }

    /**
     * 攻击类别
     * @param bool $isOrder
     * @return array|\yii\db\ActiveRecord[]
     */
    public static function ruleCatArr($isOrder=true)
    {
        $data = \app\models\RuleCat::find()->asArray()->all();
        if( $isOrder==false )  return $data;

        $arr = array_column($data, 'desc', 'name');
        $arr['B&W'] = '访问控制';
        foreach($arr as $k => $v){
            $arr[$k] = Yii::$app->sysLanguage->getTranslate($v);
        }
        return $arr;
    }

    /**
     * 危害等级
     * @param bool $isOrder
     * @param bool $isName
     * @return array|\yii\db\ActiveRecord[]
     */
    public static function severityArr($isOrder=true, $isName=false)
    {
        $SeverityModel = \app\models\Severity::find()->asArray()->all();
        if( $isOrder==false ) return $SeverityModel;

        $arr = null;
        if( $isName==false ) $arr = array_column($SeverityModel, 'desc', 'severity');

        if(null == $arr) $arr = array_column($SeverityModel, 'desc', 'name');

        foreach ($arr as $k => $v) $arr[$k] = Yii::$app->sysLanguage->getTranslate($v);
        return $arr;
    }

    /**
     * 获取内置规则Warn危害级别数组
     * @return array Array ( [中危] => 中危 [低危] => 低危 [高危] => 高危 )
     */
    public static function ruleWarn()
    {
        $WarnArr = \app\models\Rules::find()->select(['warn'])->distinct()->asArray()->all();

        $arr = array_column($WarnArr, 'warn', 'warn');
        foreach( $arr as $k => $v )
        {
            $arr[$k] = Yii::$app->sysLanguage->getTranslate($v);
        }
        return $arr;
    }

    //启用 禁止
    public static function enable(){
        return [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('enable'),
            '0' => Yii::$app->sysLanguage->getTranslateBySymbol('disable')
        ];
    }

    //放行 拦截
    public static function passAndIntercept()
    {
        return [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('intercept'),
            '0' => Yii::$app->sysLanguage->getTranslateBySymbol('pass')
        ];
    }

    //黑白名单
    public static function blackWhiteEnable()
    {
        return [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('blackList'),
            '0' => Yii::$app->sysLanguage->getTranslateBySymbol('whiteList')
        ];
    }

    //用户组
    public static function systemUserGroup(){
        $condition = (!Yii::$app->sysLogin->isSuperAdmin()) ? ['!=', 'id', 1] : [];
        $arr = \app\models\SysUserGroup::find()->where($condition)->all();
        $result = [];
        foreach ($arr as $item) $result[$item->id] = Yii::$app->sysLanguage->getTranslate($item->group_name);
        return $result;
    }

    //防火墙角色
    public static function systemFirewallUserRole()
    {
        return Yii::$app->sysParams->getParamsChild(['systemFirewall', 'adminRole']);
    }

    //字符串表达式匹配模式
    public static function matchingAlgorithmForStr(){
        return [
            '0' => Yii::$app->sysLanguage->getTranslateBySymbol('matchString'),
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('matchRegularExpression'),
        ];
    }

    //规则模板
    public static function rulesSet(){
        $RuleModel = \app\models\RuleModel::find()->asArray()->all();
        $arr = array_column($RuleModel, 'name', 'id');

        $htmlSafe = new \yii\helpers\Html;
        foreach ($arr as $k => $v) $arr[$k] = Yii::$app->sysLanguage->getTranslate($htmlSafe->encode($v));
        return $arr;
    }

    //规则模板模板类型
    public static function ruleModelTplType(){
        return [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('siteGroupTemplate'),
            '2' => Yii::$app->sysLanguage->getTranslateBySymbol('webSiteTemplate')
        ];
    }

    //规则模板继承模板,$kv=true表示返回键值对
    public static function ruleModelGroup($kv = true){
        $arr = \app\models\RuleModel::find()->where("isNULL(groupModelId)")->indexBy('id')->asArray()->all();
        foreach ($arr as $k => $v) $arr[$k]['name'] = Yii::$app->sysLanguage->getTranslate($v);
        return $kv ? array_column($arr, 'name', 'id') : $arr;
    }

    //系统语言
    public static function systemDefaultLanguage()
    {
        $arr = [];
        foreach(Yii::$app->sysLanguage->getList() as $k => $v) $arr[$k] = $v['name'];
        return $arr;
    }

    //文件扩展名
    public static function fileExtension()
    {
        $model = new \app\models\FileExtensionForConfigList();
        $extension = json_decode($model->extension, true);
        $arr = [];
        foreach ($extension as $item) $arr[$item] = $item;
        return $arr;

        $arr = \app\models\RestrictText::find()->asArray()->all();
        return array_column($arr, 'name', 'id');
    }

    //HTTP请求动作
    public static function httpTypeSet()
    {
        $arr = \app\models\HttpTypeSet::find()->asArray()->all();
        return array_column($arr, 'name', 'id');
    }

    //HTTP请求内容
    public static function httpRequestType()
    {
        $arr = \app\models\HttpRequestType::find()->asArray()->all();
        return array_column($arr, 'name', 'id');
    }

    //HTTP请求内容
    public static function restrictHeaders()
    {
        $arr = \app\models\RestrictHeaders::find()->asArray()->all();
        return array_column($arr, 'name', 'id');
    }

    //HTTP协议版本
    public static function httpVersion()
    {
        $arr = \app\models\HttpVersion::find()->asArray()->all();
        return array_column($arr, 'name', 'id');
    }


}