<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class HostLinkProtection extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['fileType'], 'safe'],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => Yii::$app->sysLanguage->getTranslateBySymbol('openLater').', '.Yii::$app->sysLanguage->getTranslateBySymbol('hotLinkProtectionFileType'),
            'fileType' => 'fileType',
        ];
    }

    public function ListField()
    {
        $fileType = [
            'png', 'bmp', 'jpg', 'raw',
            'tif', 'gif', 'pcx', 'tga',
            'exif', 'fpx', 'svg', 'psd',
            'cdr', 'pcd', 'dxf', 'ufo',
            'eps', 'ai',
        ];
        $fileTypes = [];
        foreach($fileType as $item){
            $fileTypes[$item] = $item;
        }

        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'fileType' => [
                    'type' => 'checkbox',
                    'data' => $fileTypes,
                    'labelWidth' => '100px',
                    'rowStyle' => 2
                ],
            ],
        ];
        return $field;
    }

    public function save(){
        $result = parent::save();
        Yii::$app->wafHelper->pipe("CMD_NGINX");
        return $result;
    }
}
