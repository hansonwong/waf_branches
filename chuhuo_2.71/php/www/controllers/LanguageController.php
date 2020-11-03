<?php
namespace app\controllers;

use Yii;

class LanguageController extends \app\logic\BaseController
{
	public $enableCsrfValidation = false;

	//设置系统语言
	public function actionLanguageSet($lang){
	    Yii::$app->sysLanguage->setLanguageBySession($lang);
        header('Location: /');
    }

    //语言包导出
    public function actionLangExport(){
        if(Yii::$app->request->isGet){
            return $this->renderPartial('lang-export');
        } else {
            $post = Yii::$app->request->post();
            Yii::$app->sysLanguage->langExport($post['lang']);
        }
    }

    //语言包导入
    public function actionLangImport(){
        if(Yii::$app->request->isGet){
            return $this->renderPartial('lang-import');
        } else {
            $post = Yii::$app->request->post();
            Yii::$app->sysLanguage->langImport($post['lang']);
        }
    }

    //检查语言包
    public function actionLanguageCheck(){
        if(Yii::$app->request->isGet){
            return $this->renderPartial('lang-check');
        } else {
            $post = Yii::$app->request->post();
            Yii::$app->sysLanguage->checkAllTranslate($post['init']);
        }
        return 'OK';
    }

    public function actionLangNewWordCheck(){
        $wordsArr = $wordsUnique = [];
        if(Yii::$app->request->isPost){
            $words = Yii::$app->request->post('words');
            $words = str_replace("\r", '', $words);

            $wordsArr = explode("\n", $words);
            $wordsUnique = Yii::$app->sysLanguage->checkNewWordUnique($wordsArr);
        }
        return $this->renderPartial('lang-new-word-check', [
            'wordsArr' => $wordsArr,
            'wordsUnique' => $wordsUnique,
        ]);
    }

    //查看语言代号
    public function actionLangSourceSymbol(){
        if (!YII_ENV_DEV) return;
        $arr = Yii::$app->sysLanguage->getTranslateSymbol();
        echo '<meta charset="UTF-8"/>';
        echo '<table border="1" style="border: 1px solid #000;">';
        foreach ($arr as $k => $v) echo "<tr><td>{$k}</td><td>{$v}</td></tr>";
        echo '</table>';
    }

    public function actionLangSourceForJs(){
        switch(Yii::$app->request->get('tpl')){
            case 'json':
                $arr = Yii::$app->sysLanguage->getTranslateSymbolForCurrentLang();
                Yii::$app->sysJsonMsg->data(true, $arr);
                break;
            case 't':
                header('Content-type: text/javascript');
                echo $this->renderPartial('translation/translation.js.php', []);
                break;
            case 'b':
                header('Content-type: text/javascript');
                echo $this->renderPartial('translation/baseLanguage.js.php', []);
                break;
        }
    }

    public function actionWafRulesExport(){
        if(Yii::$app->request->isGet){
            return $this->renderPartial('lang-export');
        } else {
            $post = Yii::$app->request->post();
            \app\logic\waf\wafRules\Language::export($post['lang']);
        }
    }

    public function actionWafRulesImport(){
        if(Yii::$app->request->isGet){
            return $this->renderPartial('lang-import');
        } else {
            $post = Yii::$app->request->post();
            \app\logic\waf\wafRules\Language::import($post['lang']);
            return 'OK';
        }
    }

    public function actionCreateLanguageBaseFile(){
        Yii::$app->sysLanguage->createLanguageBaseFile();
        return 'OK';
    }
}
