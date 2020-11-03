<?php
namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;

class ProtocolVersion extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => Yii::$app->sysLanguage->getTranslateBySymbol('allowHttpProVersionConfig').'('.Yii::$app->sysLanguage->getTranslateBySymbol('openLater').', '.Yii::$app->sysLanguage->getTranslateBySymbol('allowHttpProVersionRequest').')',
            'extension' => 'httpProVersion',
            'extensionHidden' => '',
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
                    SelectList::httpVersion('checkbox'),
                    ['labelWidth' => '150px', 'rowStyle' => 2]
                ),
            ],
        ];
        return $field;
    }

    /**
     * 更新HttpRequestType
     * @param $values
     */
    public static function updateSetting($values){
        \app\models\HttpVersion::updateAll(['status' => 0]);
        foreach ($values as $id){
            $temp = \app\models\HttpVersion::findOne($id);
            $temp->status = 1;
            $temp->save();
        }
        Yii::$app->wafHelper->pipe("CMD_NGINX");
    }
}
