<?php
namespace app\logic;

use Yii;
use \yii\helpers\Url;
use app\widget\AdminListConfig;
use app\logic\sys\SysAuthority;

class BaseController extends \yii\web\Controller
{
	public
        $translate = null,//提供翻译的对象
        $modelPrimaryNameSpace = '\\app\\models\\',//默认数据模型命名空间
        $model = null,//自动绑定数据模型
        $tabList = null,//选项卡页面配置
        $actionResult = true,//运行后结果是否成功
        $actionResultLog = true;//运行后结果是否记录日志

	public function __construct($id, \yii\base\Module $module, array $config = [])
	{
	    Yii::$app->sysInit->init();
		parent::__construct($id, $module, $config);
		$className = explode("\\", get_class($this));
		$modelName = end($className);

		if (null == $this->model)
			$this->model = $this->modelPrimaryNameSpace . str_replace('Controller', '', $modelName);

        $this->translate = Yii::$app->sysLanguage;
	}

	/**
	 * 控制器运行前执行
	 * @param \yii\base\Action $action
	 * @return bool
	 * @throws \yii\web\BadRequestHttpException
	 */
	public function beforeAction($action)
	{
        parent::beforeAction($action);
		return SysAuthority::isPassForController($this, $action);#返回是否有权限执行
	}

    /**
     * 控制器运行后执行
     * @param \yii\base\Action $action
     * @param mixed $result
     * @return mixed
     */
	public function afterAction($action, $result)
    {
        Yii::$app->logCommon->insertFirewallOperationLogForBaseController($this);
        return parent::afterAction($action, $result); // TODO: Change the autogenerated stub
    }

    /**
	 * 显示列表
	 * @return mixed
	 */
	public function actionIndex()
	{
        return AdminListConfig::showList($this, false, '');
	}

	/**
	 * 显示单条数据记录
	 * @param $id 数据ID
	 * @return mixed
	 */
	public function actionView($id)
	{
		return AdminListConfig::showAndSaveUpdate($this, false, $id, false, false);
	}

	/**
	 * 显示添加界面/插入数据记录
	 * @return mixed
	 */
	public function actionCreate()
	{
		$result = AdminListConfig::showAndSaveCreate($this, 'create', false, false, true);
		if (!is_array($result)) return $result;
	}

	/**
	 * 显示添加界面/插入数据记录,并把请求参数载入到Model
	 * @return mixed
	 */
	public function CreateLoadParam()
	{
		$result = AdminListConfig::showAndSaveCreate($this, 'create', true, false, true);
		if (!is_array($result)) return $result;
	}

	/**
	 * 显示更新界面/更新数据记录
	 * @param $id 数据ID
	 * @return mixed
	 */
	public function actionUpdate($id)
	{
		$result = AdminListConfig::showAndSaveUpdate($this, 'update', $id, false, true);
		if (!is_array($result)) return $result;
	}

    /**
     * 更新状态 0 1
     */
    public function actionUpdateStatus(){
        ($this->model)::updateStatus();
    }

    /**
     * 通用配置界面/保存配置
     */
	public function actionConfig(){
        $result = AdminListConfig::showAndSaveConfig($this, false, false, true);
        if (!is_array($result)) return $result;
    }

    #选项卡页面
    public function actionTabList($tab = null){
	    $tab = $tab ? [] : ($this->tabList ? $this->tabList : []);
        return $this->renderPartial('/public/tab-page', ['tab' => $tab ]);
    }

	/**
	 * 删除/批量删除数据记录
	 */
	public function actionDelete()
	{
		AdminListConfig::RecordDelete($this);
	}

    /**
     * 清空所有数据
     */
	public function actionEmptyData(){
        AdminListConfig::emptyData($this);
    }

    /**
     * 根据搜索条件清空数据
     */
    public function actionEmptyDataForCondition(){
        AdminListConfig::emptyDataForCondition($this);
    }

    public function actionExportData(){
        AdminListConfig::exportDataForCondition($this);
    }

	/**
	 * 返回数据Model
	 * @param $id 字符串或数据ID
	 * @param $modelName Model命名空间
	 * @return mixed
	 */
	public static function findModel($id, $modelName)
	{
		return AdminListConfig::findModel($id, $modelName);
	}
}
