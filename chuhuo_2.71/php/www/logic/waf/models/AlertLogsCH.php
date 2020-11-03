<?php

namespace app\logic\waf\models;

use yii\base\Model;

class AlertLogsCH extends Model
{
    public $client;

    /**
     * @return string
     */
    public function tableName()
    {
        return 't_alertlogs';
    }


    public function init()
    {
        parent::init();

        $this->client = \Yii::$app->clickhouse;
    }

    /**
     * @param $sql
     * @return mixed
     */
    private function exec($sql)
    {
        $command = $this->client->createCommand($sql);
        return $command->queryAll();
    }

    /**
     * 获取数据库表列表
     * @param bool $_is_count
     * @param string $whereStr
     * @param string $selectStr
     * @param string $orderByStr
     * @param string $limitStr
     * @param string $groupBy
     * @return mixed
     */
    public function getListByWhere($_is_count=false, $whereStr="", $selectStr="*", $orderByStr="LogDateTime DESC", $limitStr="0,20", $groupBy="")
    {
        if( $_is_count===true )
        {
            $selectStr = "count(*)";
        }

        $sql = "SELECT {$selectStr} FROM {$this->tableName()} ";
        if( strlen($whereStr)>0 )
        {
            $sql .= "WHERE {$whereStr} ";
        }

        if( $_is_count===true )
        {
            $result  = $this->exec($sql);
            return empty($result)?0:$result[0]['count()'];
        }

        if( strlen($groupBy)>0 )
        {
            $sql .= "GROUP BY {$groupBy} ";
        }

        if( strlen($orderByStr)>0 )
        {
            $sql .= "ORDER BY {$orderByStr} ";
        }
        if( strlen($limitStr)>0 )
        {
            $sql .= "LIMIT {$limitStr}";
        }

        //\Yii::warning($sql, 'alert_test');

        return $this->exec($sql);
    }

    /**
     * 获取单条表数据
     * @param integer $id
     * @return mixed
     */
    public function getInfoById($id)
    {
        if( strlen($id)<1 ) return [];

        $sql = "SELECT * FROM {$this->tableName()} WHERE id={$id}";
        $result  = $this->exec($sql);

        return $result[0];
    }

    /**
     * 删除表
     * @return mixed
     */
    public function dropTable()
    {
        $sql = "DROP TABLE `default`.{$this->tableName()}";

        //\Yii::warning($sql, 'alert_test1');
        $command = $this->client->createCommand($sql);
        return $command->execute();
    }

    /**
     * 创建表
     * @return mixed
     */
    public function createTable()
    {
        $sql = "CREATE TABLE {$this->tableName()} (                 
                id UInt64,   
                AuditLogUniqueID String,  
                LogDateTime DateTime,  
                CountryCode String,  
                RegionCode String,  
                City String,  
                SourceIP String,  
                SourcePort String,  
                DestinationIP String,  
                DestinationPort String,  
                Referer String,  
                UserAgent String,  
                HttpMethod String,  
                Url String,  
                HttpProtocol String,  
                Host String,  
                RequestContentType String,  
                ResponseContentType String,  
                HttpStatusCode String,  
                GeneralMsg String,  
                Rulefile String,  
                RuleID String,  
                MatchData String,  
                Rev String,  
                Msg String,  
                Severity String,  
                Tag String,  
                Status String,  
                LogSource String,  
                AttackType String,  
                Uri String,  
                QueryString String,  
                date Date) ENGINE = MergeTree(date, (id, LogDateTime), 8149)";

        $command = $this->client->createCommand($sql);
        return $command->execute();
    }
}