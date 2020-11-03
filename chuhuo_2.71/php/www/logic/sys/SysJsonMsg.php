<?php
namespace app\logic\sys;

use Yii;

class SysJsonMsg{

    /**
     * 登录超时
     * @param bool $exit
     */
    public static function loginTimeout($exit = true){
        echo json_encode(['isLogin' => false]);
        if ($exit) Yii::$app->end();
    }

    /**
     * 获取登录超时时间
     * @param bool $exit
     */
    public static function loginExpireTime($exit = true){
        $model = new \app\logic\sys\SysLoginConfig();
        echo json_encode(['expireTimestamp' => $model->loginExpireTime(), 'timestamp' => time()]);
        if ($exit) Yii::$app->end();
    }

    /**
     * @param $success 成功状态
     * @param $msg 提示信息
     * @param $exit 是否退出
     */
    public static function msg($success, $msg, $exit = true)
    {
        echo json_encode(['success' => $success, 'msg' => $msg]);
        if ($exit) Yii::$app->end();
    }


    /**
     * 用于返回数据
     * @param $success
     * @param $data
     * @param bool $exit
     */
    public static function data($success, $data, $exit = true){
        echo json_encode(['success' => $success, 'data' => $data]);
        if ($exit) Yii::$app->end();
    }

    /**
     * 用于返回字段错误信息
     * @param $success 成功状态
     * @param $error 错误信息
     * @param $exit 是否退出
     */
    public static function errorFieldMsg($success, $error, $exit = true){
        $errorArr = [];
        foreach ($error as $k => $v) {
            $errorArr[] = [
                'id' => $k,
                'info' => $v,
            ];
        }

        echo json_encode(['success' => $success, 'errorFieldMsg' => $errorArr]);
        if ($exit) Yii::$app->end();
    }
}