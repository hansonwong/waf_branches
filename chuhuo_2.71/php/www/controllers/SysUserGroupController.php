<?php
namespace app\controllers;

use app\logic\sys\SysAuthority;

class SysUserGroupController extends \app\logic\BaseController
{
	/**
	 * 显示当前组权限配置
	 * @param $id 组ID
	 * @return string
	 */
	public function actionAuthority($id){
		$model = self::findModel('new', $this->model);
		return $this->renderPartial('/sys-user-menu/group-set', [
            'model' => $model,
            'menu' => \app\logic\sys\SysMenu::getList(),
            'authority' => \app\logic\sys\SysAuthority::getListConfig($id),
            'groupId' => $id,
        ]);
	}

	/**
	 * 修改配置状态
	 * @param $id 对应权限表配置ID
	 */
	public function actionAuthorityModify($id){
		SysAuthority::updateAuthority($id);
	}
}
