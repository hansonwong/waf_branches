<?php
namespace app\logic\waf\wafRules;

use Yii;
use app\logic\model\UploadSingleFile;
use app\models\Rules;
use app\logic\common\CvsHelper;

class Language
{
    public static $translateFiled = ['name', 'desc', 'harm_desc', 'suggest'];

    /**
     * 按目标语言导出规则包
     * @param $lang
     */
    public static function export($lang){
        Yii::$app->language = $lang;

        $rules = Rules::find()->indexBy('realid')->asArray()->all();
        $CvsHepler = new CvsHelper();
        $CvsHepler->exportFileName("wafRules.{$lang}");
        $CvsHepler->exportHead(['id', '中文', $lang]);

        foreach ($rules as $k => $v){
            foreach(self::$translateFiled as $field){
                $id = "{$k}{$field}";
                $zh = 'NULL' != $v[$field] ? $v[$field] : '';

                $translate = Yii::t('wafRules', $id);
                $translate = $id == $translate ? $zh : $translate;
                $data = [$id, $zh, $translate];
                $CvsHepler->exportBodyItem($data);
            }
        }
    }

    /**
     * 按目标语言导入规则包
     * @param $lang
     */
    public static function import($lang){
        $path = Yii::$app->sysPath->cachePath;
        $file = "{$path}{$lang}.csv";
        $model = new UploadSingleFile(['key' => 'file', 'path' => $file]);

        if (!$model->instanceSave()) return;

        $path = Yii::$app->sysPath->projectRootPath;
        $CvsHepler = new CvsHelper();
        $items = $CvsHepler->importAndGetData($file);
        $data = array_column($items, 2, 0);
        file_put_contents("{$path}messages/{$lang}/wafRules.serialize", serialize($data));
    }

    /**
     * 临时使用:按规则字段行排序分别设置每个规则对应字段的翻译并导出为语言包
     */
    public static function modifyTranslate(){
        $path = Yii::$app->sysPath->cachePath;
        $file = "{$path}rules.csv";
        $CvsHepler = new CvsHelper();
        $items = $CvsHepler->importAndGetData($file);
        $rulesTranslate = [];
        foreach ($items as $item){
            $rulesTranslate[$item[0]] = ['name' => $item[1]];
        }


        $rules = Rules::find()->indexBy('realid')->asArray()->all();
        $CvsHepler->exportFileName("wafRules");
        $CvsHepler->exportHead(['id', '中文', 'english']);

        foreach ($rules as $k => $v){
            foreach(self::$translateFiled as $field){
                $id = "{$k}{$field}";
                $zh = 'NULL' != $v[$field] ? $v[$field] : '';
                $data = [$id, $zh, $rulesTranslate[$k][$field] ?? Yii::t('wafRules', $id)];
                $CvsHepler->exportBodyItem($data);
            }
        }
    }

    public static function getTranslation($id){
        return Yii::t('wafRules', $id);
    }
}