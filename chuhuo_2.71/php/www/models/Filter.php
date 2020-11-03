<?php
namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;

class Filter extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => Yii::$app->sysLanguage->getTranslateBySymbol('httpRequestActionConfig').'('.Yii::$app->sysLanguage->getTranslateBySymbol('openLater').', '.Yii::$app->sysLanguage->getTranslateBySymbol('allowHttpRequest').')',
            'extension' => 'httpRequestAction',
            'extensionHidden' => 'httpRequestAction',
        ];
    }

    public function rulesSource()
    {
        return [
            [['extension'], function($attribute, $params){
                $post = Yii::$app->request->post($this->modelName);
                $value = $this->$attribute;
                if(!isset($post[$attribute])) $value = [];
                self::updateSetting($value);
                $this->$attribute = $value;
            }, 'skipOnEmpty'=>false],
            [['extension', 'extensionHidden'], 'safe'],
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'extensionHidden' => ['showType' => 'hidden'],
                'extension' => array_merge(
                    SelectList::httpTypeSet('checkbox'),
                    ['labelWidth' => '150px', 'rowStyle' => 2]
                ),
            ],
            'customStr' => false,
        ];
        return $field;
    }

    /**
     * 更新HttpTypeSet
     * @param $values
     */
    public static function updateSetting($values){
        \app\models\HttpTypeSet::updateAll(['selected' => 0]);
        foreach ($values as $id){
            $temp = \app\models\HttpTypeSet::findOne($id);
            $temp->selected = 1;
            $temp->save();
        }
        Yii::$app->wafHelper->pipe("CMD_NGINX");
    }
}
