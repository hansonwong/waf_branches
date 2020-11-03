<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\models\WebServerOutBound;
use app\widget\AdminListConfig;
use yii\data\Pagination;
/**
 * 安全管理 -非法外联检测
 */
class OutLinkController extends BaseController
{
    public $model = '\\app\\models\\WebServerOutBound';

    public function actionDelete()
    {
        $result = parent::actionDelete();
        Yii::$app->wafHelper->pipe('CMD_WEBOUTRULE');
        return $result;
    }
}
