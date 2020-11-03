<!doctype html>
<?php use \yii\helpers\Url;?>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
</head>
<body>
<form action="" method="post">
    <textarea name="words" cols="" style="width: 50%;height: 300px;"></textarea><br>
    <input type="submit" value="check">
</form>
<table width="100%" border="1">
    <tr>
        <td width="50%">受检查字符</td>
        <td width="50%">不在列字符</td>
    </tr>
    <tr>
        <td>
            <?php foreach($wordsArr as $word) {
            echo "{$word}<br>";
            }?>
        </td>
        <td>
            <?php foreach($wordsUnique as $word) {
                echo "'' => '{$word}',<br>";
            }?>
        </td>
    </tr>
</table>
</body>
</html>