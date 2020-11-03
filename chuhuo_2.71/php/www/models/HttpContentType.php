<?php
namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;

class HttpContentType extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => Yii::$app->sysLanguage->getTranslateBySymbol('allowHttpRequestContent').'('.Yii::$app->sysLanguage->getTranslateBySymbol('openLater').', '.Yii::$app->sysLanguage->getTranslateBySymbol('denyHttpRequestContent').')',
            'extension' => 'httpRequestContent',
            'extensionHidden' => 'httpRequestContent',
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
                    SelectList::httpRequestType('checkbox'),
                    ['labelWidth' => '260px', 'rowStyle' => 2]
                ),
            ],
            'customStr' => false,
        ];
        return $field;
    }

    /**
     * 更新HttpRequestType
     * @param $values
     */
    public static function updateSetting($values){
        \app\models\HttpRequestType::updateAll(['status' => 0]);
        foreach ($values as $id){
            $temp = \app\models\HttpRequestType::findOne($id);
            $temp->status = 1;
            $temp->save();
        }
        Yii::$app->wafHelper->pipe("CMD_NGINX");
    }
}
