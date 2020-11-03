<?php
require 'exit.php';
echo "<meta charset='UTF-8'>";
echo "<style>table{margin-bottom:50px;width:100%; float:left;table-layout: fixed;}
table,table tr th, table tr td { border:1px solid #0094ff;word-wrap: break-word;}
</style>";

function getAllTableName($db, $dbName){
    $db->exec("use {$dbName}");
    $table_result = $db->prepare("show tables;");
    $table_result->execute();

//取得所有的表名
    $arr = [];
    while($row = $table_result->fetch(PDO::FETCH_NUM)) $arr[] = $row[0];
    return $arr;
}

function compareTable($t1, $t2){
    $t1Key = array_keys($t1);
    $t2Key = array_keys($t2);

    $t12KeyExist = array_intersect($t1Key, $t2Key);
    $t1KeyHave = array_diff($t1Key, $t2Key);
    $t2KeyHave = array_diff($t2Key, $t1Key);

    $t1NotSame = $t2NotSame = [];
    foreach ($t12KeyExist as $field){
        if(md5(serialize($t1[$field])) != md5(serialize($t2[$field]))){
            $t1NotSame[] = $t1[$field];
            $t2NotSame[] = $t2[$field];
        }
    }

    $t1Have = [];
    foreach ($t1KeyHave as $field) $t1Have[] = $t1[$field];

    $t2Have = [];
    foreach ($t2KeyHave as $field) $t2Have[] = $t2[$field];

    $result[0] = ['diff' => $t1NotSame, 'have' => $t1Have];
    $result[1] = ['diff' => $t2NotSame, 'have' => $t2Have];
    return $result;
}

function getTableDesc($db, $dbName, $table){
    $db->exec("use {$dbName}");
    $table_result = $db->prepare("desc {$table};");
    $table_result->execute();

//取得所有的表名
    $arr = [];
    while($row = $table_result->fetch(PDO::FETCH_ASSOC)) $arr[] = $row;
    $field = [];
    foreach($arr as $item) $field[$item['Field']] = $item;
    return $field;
}

$db = [];
for($i = 0; $i < 2; $i++){
    $db[$i]['host'] = [
        'host' => $_POST['host'][$i],
        'db' => $_POST['db'][$i],
        'port' => $_POST['port'][$i],
        'user' => $_POST['user'][$i],
        'pwd' => $_POST['pwd'][$i],
    ];
}
try{
    foreach ($db as $dbKey => $dbItem){
        $host = $dbItem['host'];
        $db[$dbKey]['db'] = new PDO("mysql:host={$host['host']};dbname={$host['db']};port={$host['post']}", $host['user'], $host['pwd']);
        $dbObj = $db[$dbKey]['db'];
        $dbObj->exec("set names utf8");
        $db[$dbKey]['table'] = getAllTableName($dbObj, $dbItem['host']['db']);
    }
}catch(PDOException $e){
    echo $e->getMessage();
}

//获取所有表
$allTables = [];
foreach ($db as $dbKey => $dbItem) {
    $db[$dbKey]['table'] = getAllTableName($dbItem['db'], $dbItem['host']['db']);
    $allTables = array_merge($allTables, $db[$dbKey]['table']);
}
$allTables = array_unique($allTables);
echo "<table><tr><td>所有表</td></tr>";
foreach($allTables as $item) echo "<tr><td>{$item}</td></tr>";
echo "</table>";

//各库不存在的表
foreach ($db as $dbKey => $dbItem) {
    $db[$dbKey]['tableLost'] = array_diff($allTables, $db[$dbKey]['table']);
    echo "<table><tr><td>
        {$db[$dbKey]['host']['host']}:
        {$db[$dbKey]['host']['db']}:
        {$db[$dbKey]['host']['port']}
        不存在的表</td></tr>";
    foreach($db[$dbKey]['tableLost'] as $item) echo "<tr><td>{$item}</td></tr>";
    echo "</table>";
}

//各库存在的表
$allDbTablesBothExist = [];
$allDbTablesBothNotExist = [];
foreach ($db as $dbKey => $dbItem) {
    $allDbTablesBothNotExist = array_merge($allDbTablesBothNotExist, $db[$dbKey]['tableLost']);
}
$allDbTablesBothExist = array_diff($allTables, $allDbTablesBothNotExist);
echo "<table><tr><td style='width:180px;'>都存在的表</td>";
foreach ($db as $dbKey => $dbItem) {
    echo "<td>
        {$db[$dbKey]['host']['host']}:
        {$db[$dbKey]['host']['db']}:
        {$db[$dbKey]['host']['port']}
        </td>";
}
echo "</tr>";
foreach($allDbTablesBothExist as $item){
    echo "<tr><td>{$item}</td>";

    $desc = [];
    foreach ($db as $dbKey => $dbItem){
        $desc[] = getTableDesc($dbItem['db'], $dbItem['host']['db'], $item);
    }

    $result = compareTable($desc[0], $desc[1]);

    foreach($result as $item){
        echo "<td>";
        echo "不相同<br><br>";
        foreach($item['diff'] as $diff){
            echo json_encode($diff);
            echo "<br><br>";
        }
        echo "独有<br><br>";
        foreach($item['have'] as $have){
            echo json_encode($have);
            echo "<br><br>";
        }
        echo "</td>";
    }
    echo "</tr>";
}
echo "</table>";