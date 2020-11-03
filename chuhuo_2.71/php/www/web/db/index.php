<?php require 'exit.php';?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
</head>
<body>
数据库字典:<br>
<form method="post" target="_blank" action="db.php">
    host:<input type="text" name="host"><br>
    port:<input type="number" name="port"><br>
    user:<input type="text" name="user"><br>
    pwd:<input type="text" name="pwd"><br>
    db:<input type="text" name="db"><br>
    <input type="submit" value="VIEW">
</form>
<hr/>
数据库比较:<br>
<?php
$arr = ['host', 'port', 'user', 'pwd', 'db'];

?>
<form method="post" target="_blank" action="dbCompare.php">
    <table>
        <?php foreach ($arr as $item){
            echo "<tr>
                <td>{$item}</td>
                <td><input type='text' name='{$item}[]'></td>
                <td><input type='text' name='{$item}[]'></td>
                </tr>";
        }?>
    </table>
    <input type="submit" value="VIEW">
</form>


</body>
</html>