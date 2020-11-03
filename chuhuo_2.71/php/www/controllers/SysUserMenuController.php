<?php
namespace app\controllers;

use Yii;
use app\logic\sys\SysMenu;

class SysUserMenuController extends \app\logic\BaseController
{
    //显示菜单树
    public function actionIndex(){
        $model = self::findModel('new', $this->model);
        return $this->renderPartial('index', ['model' => $model, 'data' => SysMenu::getList()]);
    }

    //输出一项菜单信息(JSON)
    public function actionOne(){
        $id = intval($_POST['id']);
        $data = SysMenu::getSingle($id);
        Yii::$app->sysJsonMsg->data($data ? true : false, $data);
    }

    public function actionDelete(){
        $id = intval($_POST['id']);
        SysMenu::delete($id);
    }
}
