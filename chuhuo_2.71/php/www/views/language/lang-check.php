<!doctype html>
<?php
use \yii\helpers\Url;
$lang = Yii::$app->sysLanguage->getList();
?>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>语言检测</title>
</head>
<body>
<form action="" method=post enctype="multipart/form-data">
    <label>模式:</label>
    <select name=init id=lang>
        <option value='0'>删除所有数据</option>
        <option value='1'>重置所有翻译</option>
        <option value='2'>清除不存在的翻译</option>
    </select><br><br>
    <input type="submit" value="提交">
</form>
</body>
</html>