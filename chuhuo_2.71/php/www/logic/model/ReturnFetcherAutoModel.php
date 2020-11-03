<?php
namespace app\logic\model;

class ReturnFetcherAutoModel{
	public static $filePosition = 0, $fileName = 'Model%s', $filePath = 'duplicateFetcherAutoModel';

	public static function getFileCount(){

	}

	public static function getDir(){
		return __DIR__;
	}

	public static function getModel(){
		$namespace = "\\app\\logic\\model\\".self::$filePath."\\";
		$modelName = sprintf(self::$fileName, self::$filePosition++);

		$file = self::getDir().'/'.self::$filePath.'/'.$modelName.'.php';
		self::createFile($file, $modelName);
		return $namespace.$modelName;
	}

	public static function createFile($file, $modelName){
		if(file_exists($file)) return;
		$fileTpl = file_get_contents(FetcherAutoModel::getFilePath());
		$fileTpl = str_replace('namespace app\\logic\\model', 'namespace app\\logic\\model\\'.self::$filePath, $fileTpl);
		$fileTpl = str_replace('class FetcherAutoModel', "class {$modelName}", $fileTpl);

		$fileObj = fopen($file, "w");
		fwrite($fileObj, $fileTpl);
		fclose($fileObj);
	}
}
?>