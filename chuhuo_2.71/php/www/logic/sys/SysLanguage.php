<?php

namespace app\logic\sys;

use app\logic\waf\models\SelectList;
use Yii;
use app\models\SysLanguageSource;
use app\logic\model\UploadSingleFile;
use app\logic\common\FilePath;
use app\logic\common\CvsHelper;

class SysLanguage
{
    public $className = null;//本类的名称

    public static
        $defaultLanguage = 'zh-CN',//默认语言
        $langSymbolKey = 'lang';

    public function __construct()
    {
        $className = explode("\\", get_class($this));
        $this->className = end($className);
    }

    //初始化系统语言设置
    public function initLanguage(){
        $this->setLanguageBySession();
        $this->setLanguageByConsole();
    }

    //web环境下设置系统默认语言
    public function setLanguageBySession($lang = null)
    {
        if(isset(Yii::$app->session)) {
            $session = Yii::$app->session;
            if (!isset($session[$this->className])){
                $loginConfig = new SysLoginConfig();
                $session[$this->className] = $loginConfig->defaultLanguage() ?? self::$defaultLanguage;
            }
            if(null != $lang) $session[$this->className] = $lang;
            $this->setLanguage($session[$this->className]);
        }
    }

    //命令行环境下设置系统语言
    public function setLanguageByConsole(){
        if(!isset(Yii::$app->session)) {
            $loginConfig = new SysLoginConfig();
            $lang = $loginConfig->defaultLanguage() ?? self::$defaultLanguage;
            $this->setLanguage($lang);
        }
    }

    /**
     * 设置系统默认语言
     */
    public function setLanguageBySystemDefault(){
        $loginConfig = new SysLoginConfig();
        $this->setLanguage($loginConfig->defaultLanguage() ?? $this->defaultLanguage);
    }

    /**
     * 设置系统母语语言
     */
    public function setLanguageBySourceLanguage(){
        $this->setLanguage(Yii::$app->sourceLanguage);
    }

    //设置系统当前语言
    public function setLanguage($lang){
        Yii::$app->language = $lang;
    }

    //获取系统当前语言
    public function getLanguage(){
        return Yii::$app->language;
    }

    //获取语言列表
    public function getList()
    {
        $sysParams = Yii::$app->sysParams;
        return $sysParams->getParamsChild(['systemLanguage']);
    }

    //获取翻译
    public function getTranslate($content)
    {
        //用于调试时临时加入翻译源字符到数据库
        if (YII_ENV_DEV) {
            $check = Yii::$app->controller->module->requestedRoute;
            if('language/language-check' == $check){
                $data = ['title' => $content];
                $item = SysLanguageSource::findOne($data);
                if (null == $item) {
                    $SysLanguageSource = new SysLanguageSource();
                    $SysLanguageSource->setAttributes($data);
                    if($content) $SysLanguageSource->save();
                } else {
                    $item->is_use = '1';
                    $item->save(true);
                }
            }
        }
        return Yii::t('app', $content);
    }

    //获取属性翻译
    public function getTranslateByAttrs($attrs){
        foreach ($attrs as $k => $v) $attrs[$k] = $this->getTranslate($v);
        return $attrs;
    }

    //获取代号数组翻译
    public function getTranslateBySymbolAttrs($attrs){
        foreach ($attrs as $k => $v)
            $attrs[$k] = $this->getTranslate($this->getTranslateBySymbol($v));
        return $attrs;
    }

    /**
     * 根据标志值获取源字符串
     * @param $symbol
     * @return string
     */
    public function getTranslateBySymbol($key){
        $cache = Yii::$app->cache;
        if (false == $cache->get(self::$langSymbolKey.__FUNCTION__)) {
            $symbolArr = $this->getTranslateSymbol();
            $symbolArr[__FUNCTION__] = __FUNCTION__;
            $cache->multiSet($this->getTranslateBySymbolArr($symbolArr));
        }

        $val = $cache->get(self::$langSymbolKey."{$key}");
        return $this->getTranslate((false === $val) ? $key : $val);
    }

    /**
     * 设置系统默认语言环境,再根据标志值获取源字符串
     * @param $key
     * @return string
     */
    public function getTranslateBySymbolWithDefaultConfig($key){
        $this->setLanguageBySystemDefault();#设置系统默认语言
        $translate = $this->getTranslateBySymbol($key);
        $this->initLanguage();
        return $translate;
    }

    /**
     * 设置系统母语语言环境,再根据标志值获取源字符串
     * @param $key
     * @return string
     */
    public function getTranslateBySymbolWithSourceLanguage($key){
        $this->setLanguageBySourceLanguage();#设置系统母语
        $translate = $this->getTranslateBySymbol($key);
        $this->initLanguage();
        return $translate;
    }

    /**
     * 根据翻译key获取指定的语言翻译
     * @param $key 翻译key
     * @param $lang 语言
     * @return string
     */
    public function getTranslateBySymbolWithAssignLanguage($key, $lang){
        $this->setLanguage($lang);
        $translate = $this->getTranslateBySymbol($key);
        $this->initLanguage();
        return $translate;
    }

    /**
     * 获取所有翻译代号键值对
     * @return array
     */
    public function getTranslateSymbol(){
        $filePath = realpath(__DIR__.'/language');
        FilePath::getAllFilesPath($filePath, $files);
        $symbolArr = [];
        foreach ($files as $item) $symbolArr = array_merge($symbolArr, require($item));
        return $symbolArr;
    }

    /**
     * 获取所有翻译代号键值对(对应当前语言)
     * @return array
     */
    public function getTranslateSymbolForCurrentLang(){
        $arrSymbol = $this->getTranslateSymbol();
        foreach ($arrSymbol as $k => $v) $arrSymbol[$k] = $this->getTranslate($v);
        return $arrSymbol;
    }

    /**
     * 为源字符文件设置KEY
     * @param $prefix
     * @param $langArr
     * @return array
     */
    public function getTranslateBySymbolArr($langArr){
        $langArrResult = [];
        $prefix = self::$langSymbolKey;
        foreach($langArr as $k => $v) $langArrResult["{$prefix}{$k}"] = $v;
        return $langArrResult;
    }

    /**
     * 获取所有目标语言数据
     * @param $lang 目标语言
     */
    public function getAllTranslate($lang)
    {
        $langList = $this->getList();
        $langModel = $langList[$lang]['model'];
        $model = $langModel::find()->with('id0')->asArray()->all();
        $translateArr = [];
        foreach ($model as $item) $translateArr[$item['id0']['title']] = $item['title'];
        return $translateArr;
    }

    /**
     * 获取一种语言缓存
     * @param $lang
     * @return array|mixed
     */
    public function getAllTranslateCache($lang)
    {
        $langKey = self::$langSymbolKey."{$lang}";

        $cache = Yii::$app->cache;
        $allTranslate = $cache->get($langKey);
        if (false === $allTranslate) {
            $allTranslate = $this->getAllTranslate($lang);
            $cache->set($langKey, $allTranslate, 3600);
            $allTranslate = $cache->get($langKey);
        }

        //用于调试时临时加入翻译源字符到数据库
        //if (YII_ENV_DEV) $allTranslate = $this->getAllTranslate($lang);
        return $allTranslate;
    }

    /**
     * 导出语言包
     * @param $lang 选择导出的语言包
     */
    public function langExport($lang)
    {
        if (!YII_ENV_DEV) return;
        $language = $this->getList();
        $language = isset($language[$lang]) ? $language[$lang] : null;
        if($language) Yii::$app->language = $lang;

        $items = SysLanguageSource::find()->asArray()->orderBy(['id' => 'asc'])->all();

        $CvsHepler = new CvsHelper();
        $CvsHepler->exportFileName($language['name']);
        $CvsHepler->exportHead(['id', '中文', $lang]);

        foreach($items as $item){
            $translation = $language ? $this->getTranslate($item['title']) : '';
            $CvsHepler->exportBodyItem([$item['id'], $item['title'], $translation]);
        }
    }

    /**
     * @param $lang 选择导入的语言包
     */
    public function langImport($lang)
    {
        if (!YII_ENV_DEV) return;
        $path = Yii::$app->sysPath->cachePath;
        $file = "{$path}{$lang}.csv";
        $model = new UploadSingleFile(['key' => 'file', 'path' => $file]);

        if ($model->instanceSave()) {
            $CvsHepler = new CvsHelper();
            $items = $CvsHepler->importAndGetData($file);

            $langItem = $this->getList();
            $langModel = $langItem[$lang]['model'];

            $transaction = Yii::$app->db->beginTransaction();
            try {
                $langModel::deleteAll();
                $langModel = new $langModel();
                foreach ($items as $data){
                    if(!$data[2]) continue;
                    $langModel->isNewRecord = true;
                    $langModel->setAttributes(['id' => $data[0], 'title' => $data[2]]);
                    $langModel->save();
                }
                $transaction->commit();
            } catch (Exception $e) {
                $transaction->rollBack();
            }
            $success = true;
        } else {
            $success = false;
        }
        Yii::$app->sysJsonMsg->msg(
            $success,
            $this->getTranslateBySymbol($success ? 'uploadSuccessfully' : 'fileUploadFailed')
        );
    }

    /**
     * 创建语言库文件
     */
    public function createLanguageBaseFile(){
        $appFile = <<<app
<?php
\$dir = explode('/', __DIR__);
return \Yii::\$app->sysLanguage->getAllTranslateCache(end(\$dir));
app;
        $wafRules = <<<app
<?php
return unserialize(file_get_contents(__DIR__.'/wafRules.serialize'));
app;
        $files['app.php'] = $appFile;
        $files['wafRules.php'] = $wafRules;
        $files['wafRules.serialize'] = '';

        $path = Yii::$app->sysPath->projectRootPath;
        foreach ($this->getList() as $k => $v){
            $langDir = "{$path}messages/{$k}/";
            if(@mkdir($langDir)){
                foreach ($files as $fileName => $content) file_put_contents("{$langDir}{$fileName}", $content);
            }
        }
    }


    /**
     * 检测翻译字符串唯一
     * @param $words
     * @return array
     */
    public function checkNewWordUnique($words){
        $wordsSource = $this->getTranslateSymbol();
        $unique = [];
        $words = array_unique($words);
        foreach($words as $word){
            $word = trim($word);
            if( !in_array($word, $wordsSource) ) $unique[] = $word;
        }
        return $unique;
    }

    /**
     * 检查所有翻译
     * @param $init 是否初始化表,0 删除所有数据, 1 重置所有翻译, 2 不清空,但会清除不在列的翻译, -1 删除所有is_use状态为0的数据
     */
    public function checkAllTranslate($init)
    {
        if (!YII_ENV_DEV) return;
        set_time_limit(100);
        $this->setLanguage($this->defaultLanguage);
        Yii::$app->cache->flush();

        $transaction = Yii::$app->db->beginTransaction();
        try {
            $this->initAllTranslate($init);
            $this->checkOtherTranslation();//检查其他翻译
            \app\logic\sys\SysMenu::getList();//检查所有菜单
            $this->checkAllModel();//检查所有模型
            $this->checkAllSymbol();//检查所有标志值
            $this->initAllTranslate(-1);

            $transaction->commit();
        } catch (Exception $e) {
            $transaction->rollBack();
        }
    }

    /**
     * 初始化翻译数据
     */
    protected function initAllTranslate($init)
    {
        if(2 == $init){//设置所有翻译字符初始值
            SysLanguageSource::updateAll(['is_use' => 0]);
            return;
        }
        if(-1 == $init){//删除所有不使用的翻译字符
            SysLanguageSource::deleteAll(['is_use' => 0]);
            return;
        }

        $db = Yii::$app->db;
        $list = $this->getList();


        $createTableSql = '';
        foreach ($list as $k => $v) {
            $model = $v['model'];
            $model = new $model();
            $createTableSql .= $model->getCreateTableSql();
        }

        $list = array_reverse($list);
        $dropTableStr = '';
        foreach ($list as $k => $v) {
            $model = $v['model'];
            $model = new $model();
            $tableName = $model->tableName();
            $dropTableStr .= "drop table {$tableName};";
        }

        $db->createCommand($dropTableStr)->query();
        $db->createCommand($createTableSql)->query();
        if(0 == $init) Yii::$app->end();
    }

    /**
     * 检查其他翻译
     */
    protected function checkOtherTranslation(){
        \app\logic\waf\models\SelectList::systemUserGroup();//系统用户组别
        \app\logic\waf\models\SelectList::severityArr();//危害等级
        \app\logic\waf\models\SelectList::ruleCatArr();//入侵分类
        \app\logic\waf\models\SelectList::actionCatArr();//WAF动作分类
        \app\logic\waf\models\SelectList::ruleWarn();//告警等级
    }

    /**
     * 检查所有翻译代号
     */
    protected function checkAllSymbol(){
        $langArr = $this->getTranslateSymbol();
        foreach($langArr as $v) $this->getTranslate($v);
    }

    /**
     * 检查所有model
     */
    protected function checkAllModel()
    {
        $nameSpaceAndPath = [
            '\\app\\models\\' => '/../../models',
            '\\app\\modelLogs\\' => '/../../modelLogs',
            '\\app\\modelFirewall\\' => '/../../modelFirewall',
            '\\app\\modelFirewallLogs\\' => '/../../modelFirewallLogs'
        ];

        foreach ($nameSpaceAndPath as $k => $v) {
            $nameSpace = $k;
            $filePath = realpath(__DIR__ . $v);
            $arr = [];
            FilePath::getAllFilesPath($filePath, $arr);
            foreach ($arr as $item) {
                $info = pathinfo($item, PATHINFO_BASENAME);
                $info = str_replace('.php', '', $info);
                $modelName = "{$nameSpace}{$info}";
                try{
                    $model = new $modelName();
                    $model->attributeLabels();
                } catch (Exception $e) {
                    print $e->getMessage();
                    exit();
                }
            }
        }
    }

    public function JsonVsprintfSet(string $key, array $data){
        return json_encode(['key' => $key, 'data' => $data]);
    }

    public function JsonVsprintfGet(string $json){
        $json = json_decode($json, true);
        $lang = self::getTranslate($json['key']);#获取到对应翻译
        return vsprintf($lang, $json['data']);
    }
}