<?php
require 'exit.php';

header("Content-type: text/html; charset=utf-8");
//配置数据库
$dbHost = $_POST['host'];
$dbName = $_POST['db'];
$dbPort = $_POST['port'];
$dbUser = $_POST['user'];
$dbPwd = $_POST['pwd'];
try{
    $db = new PDO("mysql:host={$dbHost};dbname={$dbName};port={$dbPort}", $dbUser, $dbPwd);
    $db->exec("set names utf8");
}catch(PDOException $e){
    echo $e->getMessage();
}

//其他配置
$sql = "show tables".($table != null ? ' like "%{$table}%"' : '');
$table_result = $db->prepare($sql);
$table_result->execute();

$no_show_table = array();    //不需要显示的表
$no_show_field = array();   //不需要显示的字段

//取得所有的表名
while($row = $table_result->fetch(1)){
    if(!in_array($row[0],$no_show_table)){
        $tables[]['TABLE_NAME'] = $row[0];
    }
}
//替换所以表的表前缀
if(@$_GET['prefix']){
    $prefix = 'czzj';
    foreach($tables as $key => $val){
        $tableName = $val['TABLE_NAME'];
        $string = explode('_',$tableName);
        if($string[0] != $prefix){
            $string[0] = $prefix;
            $newTableName = implode('_', $string);
            mysql_query('rename table '.$tableName.' TO '.$newTableName);
        }
    }
    echo "替换成功！";exit();
}

//循环取得所有表的备注及表中列消息
foreach ($tables as $k=>$v) {
    $sql  = 'SELECT * FROM ';
    $sql .= 'INFORMATION_SCHEMA.TABLES ';
    $sql .= 'WHERE ';
    $sql .= "table_name = '{$v['TABLE_NAME']}'  AND table_schema = '{$dbName}'";
    $table_result = $db->prepare($sql);
    $table_result->execute();

    while ($t = $table_result->fetch(2) ) {
        $tables[$k]['TABLE_COMMENT'] = $t['TABLE_COMMENT'];
        $tables[$k]['ENGINE'] = $t['ENGINE'];
    }

    $sql  = 'SELECT * FROM ';
    $sql .= 'INFORMATION_SCHEMA.COLUMNS ';
    $sql .= 'WHERE ';
    $sql .= "table_name = '{$v['TABLE_NAME']}' AND table_schema = '{$dbName}'";

    $fields = array();

    $field_result = $db->prepare($sql);
    $field_result->execute();

    while ($t = $field_result->fetch(2) ) {
        $fields[] = $t;
    }
    $tables[$k]['COLUMN'] = $fields;
}
?>
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>数据库数据字典</title>
    <style>
        body, td, th { font-family: "微软雅黑"; font-size: 14px; }
        .warp{margin:auto; width:900px;}
        .warp h3{margin:0px; padding:0px; line-height:30px; margin-top:10px;}
        table { border-collapse: collapse; border: 1px solid #CCC; background: #efefef; }
        table th { text-align: left; font-weight: bold; height: 26px; line-height: 26px; font-size: 14px; text-align:center; border: 1px solid #CCC; padding:5px;}
        table td { height: 20px; font-size: 14px; border: 1px solid #CCC; background-color: #fff; padding:5px;}
        .c1 { width: 120px; }
        .c2 { width: 120px; }
        .c3 { width: 150px; }
        .c4 { width: 80px; text-align:center;}
        .c5 { width: 80px; text-align:center;}
        .c6 { width: 270px; }
    </style>
</head>
<body>
<div class="warp">
    <h1 style="text-align:center;">数据库数据字典</h1>
    <?php
    //循环所有表
    foreach ($tables as $k=>$v) {
        echo "
    <h3>{$k}. {$v['TABLE_NAME']} ({$v['TABLE_COMMENT']})----{$v['ENGINE']}</h3>
    <table border=1 cellspacing=0 cellpadding=0 width='100%'><tbody>
        <!--<tr>
            <th>{$k}</th>
            <th colspan=5>{$v['TABLE_NAME']}({$v['TABLE_COMMENT']})</th>
        </tr>-->
        <tr>
            <th>字段名</th>
            <th>数据类型</th>
            <th>默认值</th>
            <th>允许非空</th>
            <th>自动递增</th>
            <th>备注</th>
        </tr>";

        foreach ($v['COLUMN'] as $f) {
            if(@!is_array($no_show_field[$v['TABLE_NAME']])){
                $no_show_field[$v['TABLE_NAME']] = array();
            }
            if(!in_array($f['COLUMN_NAME'],$no_show_field[$v['TABLE_NAME']])){
                echo "<tr>
                <td class=c1>{$f['COLUMN_NAME']}</td>
                <td class=c2>{$f['COLUMN_TYPE']}</td>
                <td class=c3>{$f['COLUMN_DEFAULT']}</td>
                <td class=c4>{$f['IS_NULLABLE']}</td>
                <td class=c5>".($f['EXTRA']=='auto_increment'?'是':'&nbsp;').
                    "</td>
                <td class=c6>{$f['COLUMN_COMMENT']}</td></tr>";
            }
        }
        echo "</tbody></table>";
    }
    ?>
</div>
</body>
</html>
