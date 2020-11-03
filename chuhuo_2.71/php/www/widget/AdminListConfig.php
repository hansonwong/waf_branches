<?php
namespace app\widget;

use Yii;
use yii\data\ActiveDataProvider;
class AdminListConfig
{
    /**
     * @param $query
     * @return ActiveDataProvider
     */
	public static function getActiveDataProviderSetting(array $query){
        $query['noOrderField'] = $query['noOrderField'] ?? [];#不参与排序的字段
        $query['order'] = $query['order'] ?? ['id' => SORT_DESC,];#默认排序的字段
        $query['allData'] = $query['allData'] ?? false;

	    $post = Yii::$app->request->post();

		$pageSize = $query['pagesize'] ?? $post['pagesize'] ?? 20;#页大小
		$page = intval($query['page'] ?? $post['page'] ?? 0);#第几页
		$page = (0 == $page) ? 0 : --$page;#从0页开始,0即为第一页

		if('0' == $pageSize){
            $pageSize = 20;#默认20条为一页
        } elseif($query['allData']) $pageSize = ($query['query'])->count();#获取所有符合查询条件的数据总数

        #设置查询条件
        $setting = [
            'query' => $query['query'],
            'pagination' => [
                'page' => $page,
                'pageSize' => $pageSize,
            ],
        ];

        $sortName = $post['sortname'] ?? null;#排序字段
        #设置排序
        if(null !== $sortName && 'tableOperation' != $sortName){
            if(!in_array($sortName, $query['noOrderField'])){
                $setting['sort']['defaultOrder'] = [
                    $sortName => ($post['sortorder'] == 'asc') ? SORT_ASC : SORT_DESC,
                ];
            }
        } else {
            $setting['sort']['defaultOrder'] = $query['order'];
        }

		return new ActiveDataProvider($setting);
	}

	/**
	 * 用于输出列表
	 * @param $controller 控制器this
	 * @param $scenario 场景
	 * @param $customStr 直接输出到页面的字符串
	 * @return mixed
	 */
	public static function showList($controller, $scenario, $customStr)
	{
        $model = $controller->findModel('search', $controller->model);#搜索模型
        if ($scenario) $model->setScenario($scenario);#设置场景

        $tableConfig = self::setTable($model->ListTable());#表格显示配置
        if(Yii::$app->request->isGet){
            return $controller->renderPartial('/public/list', [
                'search' => self::setSearch($model->ListSearch()),#搜索字段配置数组
                'table' => $tableConfig,
                'customStr' => $customStr,//直接输出到页面的字符串
            ]);
        } else {
            $dataProvider =#查询对象
                self::getActiveDataProviderSetting($model->search(Yii::$app->request->post()));
            $pagination = $dataProvider->getPagination();//分页信息
            $result = [
                'data' => self::getTableBody($dataProvider->getModels(), $tableConfig['cols'], $tableConfig['operation']),#列表数据
                'page' => $pagination->getPage(),#页码,0开始
                'pagesize' => $pagination->getPageSize(),
                'total' => $pagination->totalCount,#总数
            ];
            return json_encode($result);
        }
	}

	/**
	 * 插入记录/显示表单
	 * @param $controller 控制器this
	 * @param $scenario 场景
	 * @param $loadParam 是否加载参数到model
	 * @param $customStr 自定义字符串数组
	 * @param $allowUpdate 是否允许提交
	 * @return mixed
	 */
	public static function showAndSaveCreate($controller, $scenario, $loadParam, $customStr, $allowUpdate)
	{
		$model = $controller->findModel('new', $controller->model);
		if ($scenario) $model->setScenario($scenario);
        if (Yii::$app->request->isPost) {
            if ($model->load(Yii::$app->request->post()) && $model->save(false)) {
                Yii::$app->sysJsonMsg->msg(true, Yii::$app->sysLanguage->getTranslateBySymbol('insertSuccess'), false);
                return ['model' => $model];
		    }
		} else {
			if ($loadParam) $model->load(Yii::$app->request->queryParams);
			return $controller->renderPartial('/public/list-edit', [
                'model' => $model, 'custom' => $customStr, 'allowUpdate' => $allowUpdate
            ]);
		}
	}

	/**
	 * 更新记录/显示表单
	 * @param $controller 控制器this
	 * @param $scenario 场景
	 * @param $id 数据ID
	 * @param $customStr 自定义字符串数组
	 * @param $allowUpdate 是否允许提交
	 * @return mixed
	 */
	public static function showAndSaveUpdate($controller, $scenario, $id, $customStr, $allowUpdate)
	{
		$model = $controller->findModel($id, $controller->model);
		if ($scenario) $model->setScenario($scenario);
		if (Yii::$app->request->isPost) {
		    if($model->load(Yii::$app->request->post()) && $model->save(false)){
                Yii::$app->sysJsonMsg->msg(true, Yii::$app->sysLanguage->getTranslateBySymbol('modifySuccess'), false);
                return ['model' => $model];
            }
		} else {
			return $controller->renderPartial('/public/list-edit', [
                'model' => $model, 'custom' => $customStr, 'allowUpdate' => $allowUpdate
            ]);
		}
	}

    /**
     * 更新配置/显示表单
     * @param $controller
     * @param $scenario
     * @param $customStr
     * @param $allowUpdate
     * @return array
     */
    public static function showAndSaveConfig($controller, $scenario, $customStr, $allowUpdate){
        $model = $controller->findModel('config', $controller->model);
        if ($scenario) $model->setScenario($scenario);
        if (Yii::$app->request->isPost) {
            if($model->load(Yii::$app->request->post()) && $model->save()){
                Yii::$app->sysJsonMsg->msg(true, Yii::$app->sysLanguage->getTranslateBySymbol('modifySuccess'), false);
                return ['model' => $model];
            }
        } else {
            return $controller->renderPartial('/public/config-edit', [
                'model' => $model, 'custom' => $customStr, 'allowUpdate' => $allowUpdate
            ]);
        }
    }

	/**
	 * 插入或更新时选择字段配置
	 * @param $type 场景类型
	 * @param $model 模型
	 * @return string
	 */
	public static function ListFieldScenarios($type, $model)
	{
		switch ($type) {
			case 'common' ://普通
				return ($model->isNewRecord) ? 'create' : 'update';
				break;
			case 'action' ://按动作名
				return Yii::$app->controller->action->id;
			default :
				;
		}
	}

	/**
	 * 用于删除、批量删除记录
	 * @param $controller 控制器this
	 */
	public static function RecordDelete($controller)
	{
		$model = $controller->findModel('new', $controller->model);
		$query = Yii::$app->request->bodyParams;

		$id = $query['id'];
		if(!is_array($id)) return false;
		foreach ($id as $item) {
			if ('' != $item) {
				$model->findOne($item)->delete();
			}
		}
        Yii::$app->sysJsonMsg->msg(true, '', false);
	}

    /**
     * 清空表数据
     * @param $controller
     */
	public static function emptyData($controller){
        ($controller->model)::deleteAll();
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }

    /**
     * 根据条件删除数据
     * @param $controller
     */
    public static function emptyDataForCondition($controller){
        $pageSize = 2000;#数据分批获取数量

        #获取分页信息
        $table = new $controller->model;#数据模型对象
        $dataProvider = self::getActiveDataProviderSetting(
            array_merge(
                $table->search(Yii::$app->request->post()),
                ['pagesize' => $pageSize, 'page' => 0]
            )
        );
        $pagination = $dataProvider->getPagination();
        $dataProvider->getModels();
        $pageCount = $pagination->getPageCount();
        #获取分页信息END

        #获取所有数据
        for($i = 0; $i < $pageCount; $i++){
            $dataProvider = AdminListConfig::getActiveDataProviderSetting(
                array_merge(
                    $table->search(Yii::$app->request->post()),
                    ['pagesize' => $pageSize, 'page' => 0]
                )
            );
            $dataList = $dataProvider->getModels();

            foreach($dataList as $item){
                $item->delete();
            }
        }

        Yii::$app->sysJsonMsg->msg(true, '', false);
    }

    public static function exportDataForCondition($controller){
        ($controller->model)::export();
    }

	/**
	 * 返回Model
	 * @param $modelName Model名(包括命名空间)
	 * @param $id 数据ID或字符串
	 * @return mixed
	 * @throws \yii\web\NotFoundHttpException
	 */
	public static function findModel($id, $modelName)
	{
	    $model = null;
	    $noScenario = ['', 'new', 'config', 'search'];
		switch ($id) {
			case 'new' :
                $model = new $modelName();
				break;
			case 'search' :
                $model = new $modelName();
				break;
            case 'config' :
                $model = new $modelName();
                break;
			default :
				$model = (new $modelName())->findOne($id);
				if ($model === null) throw new \yii\web\NotFoundHttpException('The requested page does not exist.');
		}
		if(!in_array($id, $noScenario)) $model->setScenario($id);#如果还在列表中,则设置场景
        return $model;
	}

	/**
	 * 设置搜索条件
	 * @param $searchAttrs 搜索设置
	 * @param $searchKey 搜索数组键
	 * @param $model 模型
	 * @param $customStr 自定义字符串
	 * @return array
	 */
	public static function setSearch($config)
	{
        $searchAttrs = $config['field'] ?? [];
        $searchKey = $config['key'] ?? false;
        $model = $config['model'] ?? null;
        $customStr = $config['customStr'] ?? false;

		$searchField = array();
		foreach ($searchAttrs as $key => $value) {
			if (is_array($value)) $searchField[$key] = $value;
			else $searchField[$value] = ['type' => 'text'];
		}
		$search = array(
			'field' => $searchField,//搜索字段
			'key' => $searchKey,//搜索模型KEY
			'model' => $model,//搜索模型
			'customStr' => $customStr,//自定义字符串
		);
		return $search;
	}

	/**
	 * 设置表格显示
	 * @param $public_button 公共按钮设置
	 * @param $cols 显示列并设置
	 * @param $operation 可用操作
	 * @param $data 数据对象dataProvider
	 * @param $model 模型
	 * @return array
	 */
	public static function setTable($config)
	{
        $public_button = $config['publicButton'] ?? [];
        $cols = $config['field'] ?? [];
        $operation = $config['recordOperation'] ?? [];
        $model = $config['model'] ?? null;
        $customStr = $config['customStr'] ?? '';

        #按钮翻译
        $createButtonText = Yii::$app->sysLanguage->getTranslateBySymbol('add');
        $deleteButtonText = Yii::$app->sysLanguage->getTranslateBySymbol('delete');
        $viewButtonText = Yii::$app->sysLanguage->getTranslateBySymbol('see');
        $modifyButtonText = Yii::$app->sysLanguage->getTranslateBySymbol('modify');
        $refreshButtonText = Yii::$app->sysLanguage->getTranslateBySymbol('refresh');
        $emptyButtonText = Yii::$app->sysLanguage->getTranslateBySymbol('empty');


		$SysAuthority = new \app\logic\sys\SysAuthority();
		$Authority = $SysAuthority->getAuthorityByUser();
		$controllerId = Yii::$app->controller->id;

		$frameSize = Yii::$app->sysParams->getParams('hui-frame-size');
		//公共按钮配置
		$public_button_default = [
            ['button' => "<button onclick=\"location.reload();\" class='btn c_b btn_ref'>{$refreshButtonText}</button>", 'authorityPass' => true],
			'delete' => "<button onclick=\"dataDelete('', '');\" class='btn c_o btn_del'>{$deleteButtonText}</button>",
			'create' => "<button id='data_add' onclick=\"dataEdit('{$createButtonText}','', '{$frameSize['width']}', '{$frameSize['height']}')\" class='btn c_g btn_add'>{$createButtonText}</button>",
            'empty-data' => "<button id='' onclick=\"dataEmpty()\" class='btn c_o btn_clear'>{$emptyButtonText}</button>",
		];
		$public_button_default = array_merge($public_button_default, $public_button);
		foreach ($public_button_default as $key => $val) {
            $public_button_config = $public_button_default[$key];
			if (false === $public_button_default[$key]) {
				unset($public_button_default[$key]);
				continue;
			} else {
				if (isset($public_button_config['authorityPass'])) {
					if (!$public_button_config['authorityPass']) {
						unset($public_button_default[$key]);
						continue;
					}
				} else {
					if (isset($public_button_config['authority'])) {
						if (!$SysAuthority->singleAuthority($Authority, $public_button_config['authority'])) {
							unset($public_button_default[$key]);
							continue;
						}
					} else if (!$SysAuthority->singleAuthority($Authority, $controllerId . '/' . $key)) {
						unset($public_button_default[$key]);
						continue;
					}
				}
			}

			if (is_array($public_button_default[$key]))
			    $public_button_default[$key] = $public_button_config['button'];
		}

		#显示列配置
		$table_cols = array();
		$table_cols_default = ['display' => true, 'float' => 'c', 'sort' => false];
		foreach ($cols as $key => $value) {
			if (is_array($value)) {
				foreach ($table_cols_default as $k => $v) {
					if (!isset($value[$k])) $value[$k] = $v;
				}
				$table_cols[$key] = $value;
			} else {
				$table_cols[$value] = $table_cols_default;
			}
		}


		$table_operation = [];#记录操作按钮
        #默认记录操作按钮
        $table_operation_default = [
            'view' => ['class' => 'bt_view', 'title' => $viewButtonText, 'url' => "javascript:dataView(\"{$viewButtonText}\", \"%s\", \"{$frameSize['width']}\", \"{$frameSize['height']}\");"],
            'update' => ['class' => 'bt_edit', 'title' => $modifyButtonText, 'url' => "javascript:dataEdit(\"{$modifyButtonText}\", \"%s\", \"{$frameSize['width']}\", \"{$frameSize['height']}\");"],
            'delete' => ['class' => 'bt_del', 'title' => $deleteButtonText, 'url' => 'javascript:dataDelete(this, "%s");'],
        ];

        if(false !== $operation)$table_operation_default = array_merge($table_operation_default, $operation);
        #生成具有权限的操作按钮数组
		foreach ($table_operation_default as $key => $value) {
		    if(false == $value) continue;

            $sym = $SysAuthority->singleAuthority($Authority, $value['authority'] ?? "{$controllerId}/{$key}");
            if($sym || ($value['authorityPass'] ?? false)){
                if(!isset($value['title'])) $value['title'] = 'null';
                if(!isset($value['url'])) $value['url'] = 'null';
                if(!isset($value['type'])) $value['type'] = 'null';
                if(!isset($value['class'])) $value['class'] = '';
                if(!isset($value['returnAllow'])) $value['returnAllow'] = '';

                $table_operation[] = $value;
            }
		}
		if(false === $operation) $table_operation = $operation;#$operation === false 不显示操作列

		return [
			'publicButton' => $public_button_default,
			'cols' => $table_cols,
			'operation' => $table_operation,
			'model' => $model,
            'customStr' => $customStr,#自定义字符串
		];
	}

	/**
	 * 配置字段，用于添加、修改
	 * @param $fieldKey 配置数组键
	 * @param $field 字段
	 * @param $fieldType 字段类型
	 * @param $customStr 自定义字符串
	 * @return array
	 */
	public static function setField($config)
	{
		if(!isset($config['fieldKey'])) $config['fieldKey'] = [];
		if(!isset($config['field'])) $config['field'] = [];
		if(!isset($config['fieldType'])) $config['fieldType'] = [];
		if(!isset($config['submitArea'])) $config['submitArea'] = null;
        if(!isset($config['submitUrl'])) $config['submitUrl'] = '';
		if(!isset($config['customStr'])) $config['customStr'] = false;
		if(!isset($config['button'])) $config['button'] = ['submit' => []];

		return $config;
	}

    /**
     * 获取表格头部
     * @param $model
     * @param $cols
     * @return array
     */
	public static function getTableHeader($model, $cols, $operation){
        $header = [];
        $titles = $model->attributeLabels();
        foreach ($cols as $key => $val) {
            if(!$val['display']) continue;

            $item = [];
            $item['display'] = $val['colName'] ?? $titles[$key];
            $item['name'] = $key;
            switch($val['float']){
                case 'l': $align = 'left';break;
                case 'r': $align = 'right';break;
                case 'c': $align = 'center';break;
                default: $align = 'center';
            }
            $item['align'] = $align;
            $header[] = $item;
        }
        if($operation)
            $header[] = ['display' => Yii::$app->sysLanguage->getTranslateBySymbol('operation'), 'name' => 'tableOperation'];
        return $header;
    }

    /**
     * 获取表格列表数据
     * @param $dataList
     * @param $cols
     * @param $operation
     * @return array
     */
    public static function getTableBody($dataList, $cols, $operation){
        $htmlSafe = new \yii\helpers\Html;
        $tableData = [];
        if (!empty($dataList)) {
            foreach ($dataList as $data) {
                $tableItem = [];
                $tableItem['primaryKey'] = $data->getPrimaryKey();
                foreach ($cols as $key => $item) {
                    if (!empty($item['type'])) {
                        switch ($item['type']) {
                            //用于外键查询
                            case 'foreignKey' :
                                $kv = explode(':', $item['val']);
                                $kvKey = $kv[0];
                                $kvVal = $kv[1];
                                $tableItem[$key] = (isset($data->$kvKey->$kvVal)) ? $data->$kvKey->$kvVal : '';
                                break;
                            case 'foreignKeyAuto' :
                                $kv = explode(':', $item['val']);
                                $kvKey = $kv[0];
                                $kvVal = $kv[1];
                                $result = $data->getMagicModel($kvKey);
                                $tableItem[$key] = $result->$kvVal;
                                break;
                            //用于外键查询,$kvVal是数组
                            case 'foreignArr' :
                                $kv = explode(':', $item['val']);
                                $kvKey = $kv[0];
                                $kvVal = $kv[1];
                                $resultVal = isset($data->$kvKey) ? $data->$kvKey : [];
                                $tableItem[$key] = (isset($resultVal[$kvVal])) ? $resultVal[$kvVal] : '';
                                break;
                            case 'foreignVal' :
                                $kvVal = $item['val'];
                                $tableItem[$key] = isset($data->$kvVal) ? $data->$kvVal : '';
                                break;
                            case 'switch' :
                                $tableItem[$key] = (isset($item['val'][$data[$key]])) ? $item['val'][$data[$key]] : '';
                                break;
                            case 'custom' :
                                $tableItem[$key] = AdminListConfig::returnConversionValue($data[$key], $item['valType']);
                                break;
                            case 'callback' :
                                $fun = $item['val'];
                                $tableItem[$key] = $fun($data, $data[$key]);
                                break;
                            case 'img' :
                                $tableItem[$key] = "<img width=70 src='{$data[$key]}'/>";
                                break;
                            default :
                                $tableItem[$key] = $htmlSafe->encode($data[$key]);
                        }
                    } else {
                        $tableItem[$key] = $htmlSafe->encode($data[$key]);
                    }
                }

                #操作列
                $operationArr = $operation ? $operation : [];#$operation == false不显示操作列
                $tableItem['tableOperation'] = '';
                foreach ($operationArr as $key => $item) {
                    #判断是否显示
                    if($fun = $item['returnAllow'] ?? false){
                        if(!$fun($data)) continue;
                    }

                    if (is_array($item['url'])) {
                        $urlArr = $item['url'];
                        $phpcode = '$url = sprintf($urlArr[0],';
                        for ($i = 1; $i < count($urlArr); $i++) {
                            $phpcode .= '$data["' . $urlArr[$i] . '"],';
                        }
                        $phpcode = trim($phpcode, ',');
                        $phpcode .= ');';
                        eval($phpcode);
                    } else {
                        $url = $item['url'];
                        $url = is_string($url) ?
                            sprintf($item['url'], $data->getPrimaryKey()) :
                            $url($data);
                    }

                    $blank = '';
                    switch ($item['type'] ?? '') {
                        case 'box' :
                            $FrameSize = Yii::$app->sysParams->getParams('hui-frame-size');;
                            $url = "javascript:dataBox(\"{$item['title']}\", \"{$url}\", \"{$FrameSize['width']}\", \"{$FrameSize['height']}\");";
                            break;
                        case 'blank' :
                            $blank = 'target=_blank';
                            break;
                        case 'js':
                            $url = "javascript:{$url}";
                        default :
                            ;
                    }
                    $class = $item['class'];
                    $title = $class ? '&nbsp;&nbsp;&nbsp;&nbsp;' : $item['title'];
                    $tableItem['tableOperation'] .= "<a class='{$class}' title='{$item['title']}' href='{$url}' {$blank}>{$title}</a>&nbsp;&nbsp;&nbsp;";
                }
                $tableData[] = $tableItem;
            }
        }
        return $tableData;
    }

	/**
	 * 返回视图
	 * @param $path 视图路径
	 * @param $config 参数数组
	 * @return string
	 */
	public static function returnEmptyController($path, $config)
	{
		$Controller = new \yii\web\Controller('', null, []);
		return $Controller->renderPartial($path, $config);
	}

	/**
	 * 用于返回新弹框且带参的URL
	 * @return string
	 */
	public static function returnCreateUrl()
	{
		$get = Yii::$app->request->get();
		unset($get['r']);
		$pageUrl = '/' . Yii::$app->controller->id . '/create?' . http_build_query($get);
		$frameSize = Yii::$app->sysParams->getParams('hui-frame-size');
		$url = "dataBox('添加', '{$pageUrl}', '{$frameSize['width']}', '{$frameSize['height']}');";
		return $url;
	}

	/**
	 * 用于返回select下拉组件数组
	 * @param $type 类型
	 * @param $arr 原始数组k => v
	 * @param $keyTag 分割kv
	 * @return array
	 */
	public static function returnSelect($type, $arr, $keyTag = false)
	{
		switch ($type) {
			case 'select' :
				return ['type' => $type, 'data' => $arr];
				break;
			case 'checkbox' :
				return ['type' => $type, 'data' => $arr];
				break;
			case 'radio' :
				return ['type' => $type, 'data' => $arr];
				break;
			case 'switch' :
				return $arr;
				break;
            default: return $arr;
		}
	}

	/**
	 * 输出JSON提示
	 * @param $code 状态码
	 * @param $info 信息
	 * @param $exit 是否退出
	 * @throws \yii\base\ExitException
	 */
	public static function returnSuccessFieldJson($code, $info, $exit)
	{
		echo json_encode(['code' => $code, 'info' => $info]);
		if ($exit) Yii::$app->end();
	}

	/**
	 * 用于查询数字区间，返回数字查询数组
	 * @param $key 键名
	 * @param $val 值
	 * @return array|bool
	 */
	public static function FilterNum($key, $val)
	{
		if ('' == $val || is_numeric($val)) return [$key => $val];

		if (stristr($val, '<')) {
			$num = str_replace('<', '', $val);
			return ['<', $key, $num];
		}

		if (stristr($val, '>')) {
			$num = str_replace('>', '', $val);
			return ['>', $key, $num];
		}

		if (stristr($val, '~')) {
			$num = explode('~', $val);
			if (2 == count($num)) {
				if (is_numeric($num[0]) && is_numeric($num[1])) {
					if ($num[0] < $num[1]) {
						return ['between', $key, $num[0], $num[1]];
					} else {
						return ['between', $key, $num[1], $num[0]];
					}
				} else {
					return false;
				}
			} else {
				return false;
			}
		}
		return false;
	}

	public static function returnConversionValue($val, $type)
	{
		switch ($type) {
			case 'datetime' :
				return $val ? date('Y-m-d H:i:s', $val) : $val;
				break;
			case 'date' :
				return date('Y-m-d', $val);
				break;
			case 'time' :
				return date('H:i:s', $val);
				break;
			case 'timestamp' :
				return strtotime($val);
				break;
            case 'json_decode' :
                if('' == $val || null == $val) return [];
                $val = json_decode($val, true);
                return (null === $val) ? [] : $val;
                break;
			default :
				return $val;
		}
	}
}
?>