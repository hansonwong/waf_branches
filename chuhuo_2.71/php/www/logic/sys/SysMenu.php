<?php
namespace app\logic\sys;

use Yii;
use app\models\SysUserMenu;
use app\models\SysUserMenuEnable;
use app\models\SysUserAuthority;
use app\models\SysUserGroup;
use app\widget\AdminListConfig;
use app\logic\sys\SysAuthority;

class SysMenu
{
	/**
	 * 获取所有菜单信息,用于显示界面菜单树形结构关系
	 * @return array|\yii\db\ActiveRecord[]
	 */
	public static function getList(){
	    $menu = SysUserMenu::find()->with('enable')->indexBy('id')->asArray()->orderBy('sort asc')->all();
        $sysLanguage = Yii::$app->sysLanguage;
        foreach($menu as $k => $v){
            $v['name'] = $sysLanguage->getTranslate($v['name']);
            $v['enable'] = $v['enable']['enable'];
            $menu[$k] = $v;
        }
        return $menu;
	}

    /**
     * 获取所有可用菜单信息(可用,隐藏)
     * @return array|\yii\db\ActiveRecord[]
     */
    public static function getListEnable(){
        $menu = self::getList();
        $menuNew = [];
        foreach($menu as $k => $v){
            if(in_array($v['enable'], [1, 2]))
                $menuNew[$k] = $v;
        }
        return $menuNew;
    }

    /**
     * 获取所有可显示菜单信息
     * @return array|\yii\db\ActiveRecord[]
     */
    public static function getListEnableShow(){
        $menu = self::getList();
        $menuNew = [];
        foreach($menu as $k => $v){
            if(1 == $v['enable'])
                $menuNew[$k] = $v;
        }
        return $menuNew;
    }

    /**
     * 获取单项菜单信息
     * @param $id
     * @return array|null|\yii\db\ActiveRecord
     */
	public static function getSingle($id){
	    $result = SysUserMenu::find()->with('enable')->where(['id' => $id])->asArray()->one();
	    $result['enable'] = $result['enable']['enable'];
		return $result;
	}

	public static function saveSingle($menu){
	    $model = SysUserMenuEnable::findOne($menu->id);

        if(null == $model){
            $model = new SysUserMenuEnable();
            /*$item['id'] = $menu->id;
            $item['enable'] = $menu->enable;
            $model->isNewRecord = true;
            $model->setAttributes($item);*/
            $model->id = $menu->id;
        }
        $model->enable = $menu->enable;
        $model->save();
    }

	/**
	 * 用于删除菜单时处理的逻辑
	 * @param $id ID
	 * @return bool
	 * @throws \Exception
	 */
	public static function delete($id){
		$countRe = SysUserMenu::find()->where(['parent_id' => $id])->count();
		if(0 < $countRe) Yii::$app->sysJsonMsg->msg(false, '请先删除子菜单才能删除此大类');

        if(SysUserMenu::findOne($id)->delete()){
            Yii::$app->sysJsonMsg->msg(true, '删除成功', false);
			return true;
		} else {
            Yii::$app->sysJsonMsg->msg(true, '删除失败', false);
			return false;
		}
	}
}