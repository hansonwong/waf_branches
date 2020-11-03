<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

#安全管理 - 配置管理 - 站点组管理
class WebSiteServersController extends BaseController{
    public function actionDelete()
    {
        parent::actionDelete();
        ($this->model)::writeServersIpToFile();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
    }
}
