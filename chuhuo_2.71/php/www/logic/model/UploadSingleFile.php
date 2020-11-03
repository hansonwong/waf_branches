<?php
namespace app\logic\model;

use Yii;
use yii\base\Model;
use yii\web\UploadedFile;

class UploadSingleFile extends Model
{
    public function __set($name, $value) {
        $this->$name = $value;
    }

    public function __construct(array $field = [])
    {
        $this->field = $field;
        parent::__construct([]);
        $this->instanceLoad();
    }

    #自动组合验证规则
    public function rules()
    {
        $rule = [];
        $field = $this->field;
        $rule[] = array_merge([$field['key'], 'file'], $field['rule'] ?? []);
        return $rule;
    }

    #加载但文件上传实例
    public function instanceLoad(){
        $field = $this->field;
        $file = $field['key'];
        $this->$file = UploadedFile::getInstance($this, $file);
    }

    #验证并保存文件
    public function instanceSave(){
        if(!$this->validate()) return false;
        $field = $this->field;
        $file = $field['key'];
        if(isset($this->$file)) return $this->$file->saveAs($field['path']);
        return false;
    }

    #获取上传验证错误信息
    public function getErrorsInfoString(){
        if(0 == count($this->errors)) return true;
        $errors = ($this->errors)[($this->field)['key']];
        return implode('|', $errors);
    }

    public function getFileInfo(){
        $key = ($this->field)['key'];
        $fileObj = $this->$key;
        $info['name'] = $fileObj->name;
        $info['tempName'] = $fileObj->tempName;
        $info['type'] = $fileObj->type;
        $info['size'] = $fileObj->size;
        $info['error'] = $fileObj->error;
        if(null !== $fileObj->error) $info['extension'] = $fileObj->getExtension();
        return $info;
    }
}