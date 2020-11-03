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
    <title>语言包上传</title>
</head>
<body>
<form action="" method=post enctype="multipart/form-data">
    <label>语言:</label>
    <select name=lang id=lang>
        <?php
        foreach($lang as $k => $v){
            echo "<option value='{$k}'>{$v['name']}</option>";
        }
        ?>
    </select><br><br>
    <label>文件:</label>
    <input type="file" name="UploadSingleFile[file]" ><br><br>
    <input type="submit" value="提交">
</form>
</body>
</html>