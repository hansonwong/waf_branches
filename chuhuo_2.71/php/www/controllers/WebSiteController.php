<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

#安全管理 - 配置管理 - 站点组管理
class WebSiteController extends BaseController{
    public $model = '\\app\\models\\WebSiteByGroup';

    public function actionDelete()
    {
        $query = Yii::$app->request->bodyParams;
        ($this->model)::checkBeforeDelete($query['id']);
        parent::actionDelete();
        \app\models\WebSiteServers::deleteAll(['webSiteId' => $query['id']]);
        Yii::$app->wafHelper->pipe('CMD_NGINX');
    }
}
