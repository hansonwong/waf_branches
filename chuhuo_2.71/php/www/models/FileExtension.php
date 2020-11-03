<?php
namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;

class FileExtension extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function attributeLabelsSource()
    {
        $url = \yii\helpers\Url::to(['', 'op' => 'config-list']);
        $button = Yii::$app->sysLanguage->getTranslateBySymbol('fileExtensionListAdmin');
        $button = "&nbsp;&nbsp;&nbsp;<a class='btn_ty' href='{$url}'>{$button}</a>";
        return [
            'headTitle1' => Yii::$app->sysLanguage->getTranslateBySymbol('denyRequestFileExtensionConfig').
                ' ('.Yii::$app->sysLanguage->getTranslateBySymbol('openLater').','.
                Yii::$app->sysLanguage->getTranslateBySymbol('denyRequestFileExtension').')'.$button,
            'extensionHidden' => 'fileExtension',
            'extension' => 'fileExtension',
        ];
    }

    public function rulesSource()
	{
		return [
            /*[['extension'], function($attribute, $params){
                $post = Yii::$app->request->post($this->modelName);
                $value = $this->$attribute;
                if(!isset($post[$attribute])) $value = [];
                self::updateSetting($value);
                $this->$attribute = $value;
            }, 'skipOnEmpty'=>false],*/
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
                    SelectList::fileExtension('checkbox'),
                    ['labelWidth' => '150px', 'rowStyle' => 2]
                ),
            ],
            'customStr' => false,
        ];
        return $field;
    }

    public function afterSave()
    {
        Yii::$app->wafHelper->pipe("CMD_NGINX");
        return parent::afterSave();
    }

    /**
     * 更新文件扩展名过滤设置
     * @param $values
     */
    public static function updateSetting($values){
        \app\models\RestrictText::updateAll(['status' => 0]);
        foreach ($values as $id){
            $temp = \app\models\RestrictText::findOne($id);
            $temp->status = 1;
            $temp->save();
        }
        Yii::$app->wafHelper->pipe("CMD_NGINX");
    }
}
