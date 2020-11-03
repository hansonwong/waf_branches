<?php
namespace app\logic\model;

use Yii;
use yii\db\Connection;
use app\models\FetchTask;
use app\models\FetchTaskItem;
use app\logic\sys\SysParams;
class AutoModelLogic{
	public static function getDbLink($dbInfo){
		$dbName = ('' != $dbInfo->db) ? "dbname={$dbInfo->db}" : '';
		return new Connection([
			'dsn' => "mysql:host={$dbInfo->host};{$dbName}",
			'username' => $dbInfo->user,
			'password' => $dbInfo->pwd,
			'charset' => 'utf8',
		]);
	}

	//获取表字段结构
	public static function getTableStructure(&$db, $tbName){
		$result = $db->createCommand("DESC `{$tbName}`;")->query();
		$field = [];
		foreach ($result as $item) $field[] = $item;
		return $field;
	}

	public static function getTableCreateSql(&$db, $tbName){
		$result = $db->createCommand("show create table `{$tbName}`;")->query();
		foreach ($result as $item){
			$sql = isset($item['Create Table']) ? $item['Create Table'] : '';
			$sql .= ';';
			return str_replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", $sql);
		}
		return '';
	}

	public static function isTableExist(&$db, $tbName){
		$result =  $db->createCommand("SHOW TABLES LIKE '{$tbName}';")->query();
		foreach ($result as $item) return true;
		return false;
	}

	public static function configTable(){
		$get = Yii::$app->request->get();
		$dbId = SysParams::getParamsChild(['tableAutoConfig', 'configTable', 'dbId']);
		$tbId = SysParams::getParamsChild(['tableAutoConfig', 'configTable', 'tbId']);

		if(isset($get[$dbId])){
			$dbInfo = FetchTask::findOne($get[$dbId]);
			$tables = $dbInfo->tables;
			$tablesExist = [];
			foreach($tables as $item) $tablesExist[] = $item->tb;
			$db = self::getDbLink($dbInfo);
			$tables = $db->createCommand("show tables")->query();
			$tableItemKey = "Tables_in_{$dbInfo->db}";

			$tablesCreate = [];
			foreach ($tables as $item) $tablesCreate[$item[$tableItemKey]] = $item[$tableItemKey];
			foreach ($tablesExist as $item) unset($tablesCreate[array_search($item, $tablesCreate)]);
			foreach($tablesCreate as $key => $val){
				$tablesCreate[$key] = [
					'create' => self::getTableCreateSql($db, $val),
					'fieldType' => self::getTableStructure($db, $val),
				];
			}
			$result = self::createTableConfig($tablesCreate);
			$FetchTaskItem = new FetchTaskItem();

			$transaction = Yii::$app->db->beginTransaction();
			try {
				foreach ($result as $item){
					$FetchTaskItem->isNewRecord = true;
					$FetchTaskItem->task_id = $dbInfo->id;
					$FetchTaskItem->setAttributes($item);
					$FetchTaskItem->save(false);
					$FetchTaskItem->id=0;
				}
				$transaction->commit();
			} catch(Exception $e) {
				$transaction->rollBack();
			}
		}
		if(isset($get[$tbId])){
			$tb = FetchTaskItem::findOne($get[$tbId]);
			$dbInfo = $tb->dbInfo;
			$db = self::getDbLink($dbInfo);
			$tablesCreate[$tb->tb] = [
				'create' => self::getTableCreateSql($db, $tb->tb),
				'fieldType' => self::getTableStructure($db, $tb->tb),
			];
			$config = self::createTableConfig($tablesCreate);
			$tb->setAttributes($config[0]);
			$tb->save(false);
		}
	}

	public static function createTableConfig($tbConfig){
		$result = [];
		$field = function($field){
			$str = '';
			foreach ($field as $item) $str .= "{$item['Field']},";
			return rtrim($str,",");
		};
		$field_attribute_label = function ($tbConfig){
			$createSql = $tbConfig['create'];
			$str = "\$result = [\n";
			foreach ($tbConfig['fieldType'] as $field){
				preg_match_all("/`{$field['Field']}`.*COMMENT '(.*?)'/", $createSql, $matches);
				$comment = isset($matches[1][0]) ? $matches[1][0] : '';
				$str .= "	'{$field['Field']}' => '{$comment}',\n";
			}
			return $str.'];';
		};
		$field_rules = function($field){
			$type = [
				/*'required' => [],
				'unique' => [],*/
				'stringNum' => ['char', 'varchar'],
				'integer' => ['int', 'integer', 'tinyint', 'smallint', 'mediumint', 'bigint', 'timestamp', 'year'],
				'date' => ['date', 'time', 'datetime'],
				'string' => ['tinytext', 'text', 'mediumtext', 'longtext'],
				'double' => ['double', 'float', 'decimal', 'numeric'],
				'safe' => ['bit', 'real', 'tinyblob', 'blob', 'mediumblob', 'longblob', 'enum', 'set', 'binary', 'varbinary', 'point', 'linestring', 'polygon', 'geometry', 'multipoint', 'multilinestring', 'multipolygon', 'geometrycollection'],
			];
			$fieldSort = [];
			$fieldStringNum = [];
			foreach ($field as $item){
				$breakForType = false;
				foreach($type as $key => $val){
					$fieldType = $item['Type'];
					foreach ($val as $v){
						if(false !== strpos($fieldType, $v)){
							$fieldStr = "'{$item['Field']}'";
							$fieldSort[$key][] = $fieldStr;
							if('NO' == $item['Null'] && 'auto_increment' != $item['Extra'])
								$fieldSort['required'][] = $fieldStr;
							if('PRI' == $item['Key'] || 'UNI' == $item['Key'])
								$fieldSort['unique'][] = $fieldStr;

							if(false !== strpos($fieldType, 'char')){
								preg_match_all("/.*\((\d*?)\).*/", $fieldType, $matches);
								$fieldStringNum[$matches[1][0]][] = $fieldStr;
							}

							$breakForType = true;
							break;
						}
					}
					if($breakForType) break;
				}
			}
			$str = "\$result = [\n";
			foreach($fieldSort as $key => $val){
				$val = array_unique($val);
				switch($key){
					case 'stringNum':
						foreach($fieldStringNum as $num => $sArr){
							$sArr = array_unique($sArr);
							$str .= "	[[".implode(',', $sArr)."], 'string', 'max' => '{$num}'],\n";
						}
						break;
					default: $str .= "	[[".implode(',', $val)."], '{$key}'],\n";
				}
			}
			return $str.'];';
		};
		$title = function ($tbConfig){
			$createSql = $tbConfig['create'];
			preg_match_all("/.*COMMENT='(.*?)'.*/", $createSql, $matches);
			return isset($matches[1][0]) ? $matches[1][0] : '';
		};
		foreach ($tbConfig as $key => $val){
			$result[] = [
				'title' => $title($val),
				'tb' => $key,
				'tb_create' => $val['create'],
				'field' => $field($val['fieldType']),
				//'field_global_var' => '',
				'field_attribute_label' => $field_attribute_label($val),
				//'field_attribute_labels_config' => '',
				'field_rules' => $field_rules($val['fieldType']),
				/*'field_search' => '',
				'field_search_box' => '',
				'field_table' => '',
				'field_edit' => '',
				'field_data' => ''*/
			];
		}
		return $result;
	}

	public static function installBase($base, $table){
		$db = new Connection([
			'dsn' => "mysql:host={$base->host};",
			'username' => $base->user,
			'password' => $base->pwd,
			'charset' => 'utf8',
		]);
		$db->createCommand("CREATE DATABASE IF NOT EXISTS `{$base->db}` DEFAULT CHARSET utf8 COLLATE utf8_general_ci")->query();
		$db->createCommand("use `{$base->db}`")->query();
		foreach($table as $tb){
			$db->createCommand($tb->tb_create)->query();
		}
		echo "<script>alert('安装完毕！');parent.location.reload();</script>";
	}
}