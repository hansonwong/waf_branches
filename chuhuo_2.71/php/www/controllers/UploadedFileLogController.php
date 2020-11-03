<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\modelLogs\Viruslogs;

/**
 * 日志管理 - 智能上传文件日志
 */
class UploadedFileLogController extends BaseController
{
    public $model = '\\app\\modelLogs\\UploadedFileLogs';

    /**
     * 查看
     * @param \app\logic\数据ID $id
     * @return mixed|string
     */
	public function actionView($id)
	{
		$model = Viruslogs::find()->where(['uploadFileID'=> $id])->one();
		$result = $model['result'];
		$result = json_decode($result, true);

		$list = [];
		if( !empty($result) )
        {
            foreach($result as $temp)
            {
                foreach($temp as $k=>$v){
                    $list[] = [$k => $v];
                }
            }
        }

		return $this->render('report',[
		    'list'=>$list,
            'downPath' => substr($model['downloadPath'],5)
        ]);
	}
}