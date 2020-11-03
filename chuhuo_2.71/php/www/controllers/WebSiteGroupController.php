<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

#安全管理 - 配置管理 - 站点组管理
class WebSiteGroupController extends BaseController
{
    public $model = '\\app\\models\\WebsiteGroup';

	public function actionAdminFrame()
    {
        $model = ($this->model)::find()->orderBy('id DESC')->asArray()->all();
        foreach ( $model as $k=>$v ) $model[$k]['webSite'] = \app\models\WebSite::find()->select('id,sWebSiteName')->where(['iWebSiteGroupId'=>$v['id']])->asArray()->all();

        return $this->render('index', ['model' => $model,]);
    }

    public function actionDelete()
    {
        $query = Yii::$app->request->bodyParams;
        ($this->model)::checkBeforeDelete($query['id']);
        parent::actionDelete();
    }
}
