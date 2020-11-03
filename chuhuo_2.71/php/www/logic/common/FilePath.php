<?php
namespace app\logic\common;

class FilePath{

    /**
     * 递归获取路径下所有文件路径
     * @param $path 路径
     * @param $arr 储存文件路径数组
     */
    public static function getAllFilesPath($path, &$arr){
        $list = scandir($path);
        foreach ($list as $item){
            if(in_array($item, ['.', '..'])) continue;

            $str = "{$path}/{$item}";
            if(is_dir($str)) self::getAllFilesPath($str, $arr);
            else $arr[] = $str;
        }
    }
}