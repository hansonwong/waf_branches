<?php
namespace app\logic\sys;

use Yii;
use \yii\helpers\Url;
use app\models\SysUserAuthority;
use app\models\SysUserMenu;
use app\models\SysUserGroup;

class SysAuthority
{
	/**
	 * 递归判断权限，形成最终权限数组
	 * @param $Authority 用户所有权限配置数组
	 * @param $SysUserMenu 系统菜单配置数组
	 * @param $parent 父ID
	 * @param $parentArr 已授权的配置数组
	 */
	public static function getAuthority(&$Authority, &$SysUserMenu, $parent, &$parentArr){
		$parentArrId = [];
		foreach($SysUserMenu as $k => $v){
			if($parent == $v['parent_id'] && 1 == $Authority[$k]['enable']){
				if(!isset($parentArr["a{$k}"])){
					$parentArr["a{$k}"] = $v;
					$parentArrId[] = $k;
				}
				unset($SysUserMenu[$k]);
				unset($Authority[$k]);
			}
		}

		foreach($parentArrId as $item){
			self::getAuthority($Authority, $SysUserMenu, $item, $parentArr);
		}
	}

    /**
     * 获取用户授权列表
     * @return array|\yii\db\ActiveRecord[]
     */
	public static function getAuthorityByUser($userName = ''){
	    $user = ('' == $userName) ? Yii::$app->sysLogin->getUser() : \app\models\SysUser::findOne(['name' => $userName]);
        return self::getList($user->group_id);
    }
	/**
	 * 获取角色所有权限信息,用于后台使用的权限检测
	 * @param $groupId 组ID
	 * @return array|\yii\db\ActiveRecord[] 返回以URL为KEY的数组
	 */
	public static function getList($groupId){
		$cache = Yii::$app->cache;
		$AuthorityArr = $cache->get('AuthorityArr'.$groupId);
		if(false === $AuthorityArr){
			$Authority = self::getListConfig($groupId);
            $SysUserMenu = SysMenu::getListEnable();

			$AuthorityArr = [];
			$AuthorityTmp = [];
			self::getAuthority($Authority, $SysUserMenu, 0, $AuthorityTmp);
			foreach($AuthorityTmp as $item){
				$AuthorityArr[$item['url']] = true;
			}
			$cache->set('AuthorityArr'.$groupId, $AuthorityArr, 600);
		}

		return $AuthorityArr;
	}

	/**
	 * 获取角色所有权限配置,用于管理后台对应角色的配置
	 * @param $groupId 组ID
	 * @return array|\yii\db\ActiveRecord[]
	 */
	public static function getListConfig($groupId){
		$Authority = SysUserAuthority::find()->where(['group_id' => $groupId])->indexBy('sys_menu_id')->asArray()->all();
		return $Authority;
	}

	/**
	 * 用于显示界面一二级管理菜单
	 * @param $groupId 角色ID
	 * @return mixed
	 */
	public static function getMenu($groupId){
		$AuthorityArr = self::getList($groupId);

        $menu = SysMenu::getListEnableShow();

		$topMenu = [];
		foreach($menu as $k => $v){
			if(0 == $v['parent_id']){
                if(self::singleAuthority($AuthorityArr, $v['url'])){
                    if( '/' != substr($v['url'],0,1) &&
                        'http://' != substr($v['url'],0,7) &&
                        'https://' != substr($v['url'],0,8)
                    ) $v['url'] = Url::to([$v['url']]);
                    $topMenu[] = $v;
                }
                unset($menu[$k]);
			}
		}

		foreach($topMenu as $key => $val){
            $secondMenu = [];
            foreach($menu as $k => $v){
                if($val['id'] == $v['parent_id']){
                    if(self::singleAuthority($AuthorityArr, $v['url'])){
                        if( '/' != substr($v['url'],0,1) &&
                            'http://' != substr($v['url'],0,7) &&
                            'https://' != substr($v['url'],0,8)
                        ) $v['url'] = Url::to([$v['url']]);
                        if(1 == $val['display_child']) $secondMenu[] = $v;
                    }
                    unset($menu[$k]);
                }
            }
            $topMenu[$key]['menu'] = $secondMenu;
		}

		foreach($topMenu as $key => $val){
            $secondMenu = $topMenu[$key]['menu'];
            foreach($secondMenu as $k => $v){
                $thirdMenuItem = [];
                foreach($menu as $ki => $vi){
                    if($v['id'] == $vi['parent_id']){
                        if(self::singleAuthority($AuthorityArr, $vi['url'])){
                            if( '/' != substr($vi['url'],0,1) &&
                                'http://' != substr($vi['url'],0,7) &&
                                'https://' != substr($vi['url'],0,8)
                            ) $vi['url'] = Url::to([$vi['url']]);
                            if(1 == $v['display_child']) $thirdMenuItem[] = $vi;
                        }
                        unset($menu[$ki]);
                    }
                }
                $secondMenu[$k]['menu'] = $thirdMenuItem;
            }
            $topMenu[$key]['menu'] = $secondMenu;
        }
		return $topMenu;
	}

	/**
	 * 获取角色对应访问路径权限是否足够
	 * @param $groupAuthority 角色权限配置数组
	 * @param $route 访问的路由
	 * @return bool
	 */
	public static function singleAuthority($groupAuthority, $route){
		return isset($groupAuthority[$route]) ? true : false;
	}


    /**
     * 检测当前用户是否有权限使用路由
     * @param $route 路由
     * @return bool
     */
	public static function singleAuthorityForCurrentUser($route){
        return isset((self::getAuthorityByUser())[$route]) ? true : false;
    }

	/**
	 * 获取角色对应访问路径权限是否足够,适用于控制器调用
	 * @param $action 控制器对象
     * @param string $userName 用户名
	 * @return bool
	 */
	public static function singleAuthorityByAction($action, $userName = ''){
		$url = $action->controller->module->requestedRoute;#当前访问路由
		return self::singleAuthority(self::getAuthorityByUser($userName), $url);#返回是否有权限true/false
	}

    /**
     * 获取角色对应访问路由权限是否足够
     * @param $url
     * @param string $userName
     * @return bool
     */
	public static function singleAuthorityByRoute($url, $userName = ''){
        return self::singleAuthority(self::getAuthorityByUser($userName), $url);
    }


	/**
	 * 修改角色相应操作权限是否可用
	 * @param $id 对应权限ID
	 * @return bool|int
	 */
	public static function updateAuthority($id){
        $post = Yii::$app->request->post();

		$model = SysUserAuthority::findOne([
		    'sys_menu_id' => $post['menuId'],
            'group_id' => $post['groupId'],
        ]);

		if(null == $model){
            $model = new SysUserAuthority();
            $item['group_id'] = $post['groupId'];
            $item['sys_menu_id'] = $post['menuId'];
            $item['enable'] = 0;
            $model->isNewRecord = true;
            $model->setAttributes($item);
        }
        $model->enable = (0 == $model->enable) ? 1 : 0;

        $resultData = [];
		if($result = $model->save(false)) {
            SysAuthority::deleteAuthorityCache($model->group_id);//删除单一缓存
            $resultData = ['sym' => $model->enable];
        }

        Yii::$app->sysJsonMsg->data($result, $resultData);
	}

	/**
	 * 删除权限缓存
	 * @param $id 删除一个或所有，all:删除所有，数字：删除单个
	 */
	public static function deleteAuthorityCache($id){
		$cache = Yii::$app->cache;
        if(is_numeric($id)) $cache->delete('AuthorityArr'.$id);
        else {
            $data = SysUserGroup::find()->asArray()->all();
            foreach($data as $item) $cache->delete('AuthorityArr'.$item['id']);
        }
	}

    /**
     * 验证是否有权限访问相应路由
     * @param $controller
     * @param $action
     * @return bool
     */
	public static function isPassForController($controller, $action){
	    $isLogin = Yii::$app->sysLogin->isLogin();#是否登录

        $route = $action->controller->module->requestedRoute;#获取当前路由
        $controllerId = $action->controller->id;#获取当前控制器ID
        if( in_array($controllerId, Yii::$app->sysPath->routePassController) ) return true;
        if( in_array($route, Yii::$app->sysPath->routePass) ) return true;

        if ($isLogin) {
            $allow = self::singleAuthorityByAction($action);
            if(!$allow){
                $info = Yii::$app->sysLanguage->getTranslateBySymbol('insufficientAuthority');
                if(Yii::$app->request->isAjax)
                    Yii::$app->sysJsonMsg->msg(false, $info, false);
                else echo "<script>alert('{$info}');</script>";
            }
            return $allow;
        }

        if(Yii::$app->request->isAjax) Yii::$app->sysJsonMsg->loginTimeout();
        else echo "<script>top.location.href='{$_SERVER['DOCUMENT_URI']}';</script>";
        return false;
    }
}