<?php

namespace app\logic\sys;


class SysDebug
{
    public $debugPath;//debug路径

    public function __construct()
    {
        $this->debugPath = Yii::$app->sysPath->systemDebugPath;
    }

    /**
     * 调试信息写入到文件
     * @param $fileName 文件名
     * @param $mode 写入模式
     */
    public function outputFile($fileName, $data, $mode = FILE_APPEND){
        file_put_contents("{$this->debugPath}{$fileName}", $data, $mode);
    }

}