<?php
namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;

class FileExtensionForConfigList extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function attributeLabelsSource()
    {
        $url = \yii\helpers\Url::to(['']);
        $button = Yii::$app->sysLanguage->getTranslateBySymbol('return');
        $button = "&nbsp;&nbsp;&nbsp;<a class='btn_ty' href='{$url}'>{$button}</a>";
        return [
            'headTitle1' => $button,
            'extensionHidden' => 'fileExtension',
            'extension' => 'fileExtension',
        ];
    }

    public function rulesSource()
	{
		return [
            [['extension'], 'string'],
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
                'extension' => ['type' => 'multipleVal',],
            ],
            'customStr' => false,
        ];
        return $field;
    }
}
