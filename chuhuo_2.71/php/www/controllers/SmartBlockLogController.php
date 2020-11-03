<?php

namespace app\controllers;

use Yii;
use app\logic\BaseController;
/**
 * 日志管理 -智能阻断日志
 */
class SmartBlockLogController extends BaseController
{
    public $model = '\\app\\modelLogs\\BdBlockedLogs';
}
