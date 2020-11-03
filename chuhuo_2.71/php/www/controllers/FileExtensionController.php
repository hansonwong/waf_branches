<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\widget\AdminListConfig;
use app\models\RestrictText;

/**
 * 安全管理 - 高级设置 - 文件扩展名过滤
 */
class FileExtensionController extends BaseController
{
    public function actionConfig()
    {
        if(Yii::$app->request->get('op')=='config-list') $this->model = "{$this->model}ForConfigList";
        return parent::actionConfig();
    }
}