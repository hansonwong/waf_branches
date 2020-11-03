<?php
namespace app\controllers;

use Yii;
use app\widget\AdminListConfig;
use app\logic\BaseController;

class SysWebAppMonitoringController extends BaseController
{
    public $layout = 'chart-main';

    public function actionIndex()
	{
        $get = Yii::$app->request->get();
        $sql = "select sWebSiteName from t_website";
        $webSize = Yii::$app->db->createCommand($sql)->query()->readAll();
        $tpl = "/chart-main/sys-web-app-monitoring/".(isset($get['type']) ? 'index-history' : 'index');
        return $this->render($tpl, [
            'webSize' => $webSize
        ]);
	}

	public function getRender(){
        if(Yii::$app->request->isGet){
            $action = Yii::$app->controller->action->id;
            $get = Yii::$app->request->get();
            $tpl = $action.(('history' == $get['type'])? '-history' : '');

            return $this->render("/chart-main/sys-web-app-monitoring/{$tpl}");
        } else return false;
    }

    public function getTableName(){
        $d = date('Ymd',time());
        $table = "t_web_connections_{$d}";
        $sql = "show tables from logs like '{$table}'";
        $tableArr = Yii::$app->db->createCommand($sql)->query()->read();

        return $tableArr ? $table : false;
    }

    public function getDataHistoryInit($startTime, $endTime){
        if('' == $startTime || '' == $endTime) return false;

        $sql = "select new_table_name from t_record_history where ori_table_name='t_web_connections' and start_time <= $endTime and end_time >= $startTime";
        $tables = Yii::$app->db->createCommand($sql)->queryAll();
        $sTable = array();
        foreach ($tables as $v) {
            array_push($sTable,'logs.'.$v['new_table_name']);
        }
        $sTable = implode(',',$sTable);
        $sSQL = "drop table if exists t_web_connections_all ";
        Yii::$app->db->createCommand($sSQL)->query();
        $sSQL = "create table `t_web_connections_all` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `sWebSiteName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
            `iNewConnections` int(11) DEFAULT NULL,
            `iConConnections` int(11) DEFAULT NULL,
            `iTransactions` int(11) DEFAULT NULL,
            `iTime` int(11) DEFAULT NULL,
            `siteflow` float DEFAULT NULL,
            PRIMARY KEY (`id`)
            ) ENGINE=MRG_MYISAM UNION=($sTable) INSERT_METHOD=LAST DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;";
        Yii::$app->db->createCommand($sSQL)->query();
        return true;
    }

	public function actionNetFlow(){
        $result = $this->getRender();
        if(!(false === $result)) return $result;

        $post = Yii::$app->request->post();

        $where = [];
        if('' != $post['webSize']) $where[] = "`sWebSiteName`='{$post['webSize']}'";
        if('' != $post['startDate'] && '' != $post['endDate']){
            $startDate = strtotime($post['startDate']);
            $endDate = strtotime($post['endDate']);
            $where[] = "`iTime`>='{$startDate}'";
            $where[] = "`iTime`<='{$endDate}'";
        }
        if(0 < count($where)) $where = 'where '.join(' and ', $where);
        else $where = '';

        switch($post['type'])
        {
            case 'all':
                $initResult = $this->getDataHistoryInit($startDate, $endDate);
                if(!$initResult) Yii::$app->sysJsonMsg->msg(false, $this->translate->getTranslateBySymbol('incorrectTimeParameter'));

                $sql = "SELECT sum(siteflow) as siteflow, iTime FROM t_web_connections_all {$where} group by iTime order by iTime asc";
                $arr = Yii::$app->db->createCommand($sql)->query()->readAll();
                $date = $data = [];
                foreach($arr as $item){
                    $date[] = date('Y-m-d H:i:s', $item['iTime']);
                    $data[] = $item['siteflow'];
                    //$data[] = rand(0, 10000);
                }
                Yii::$app->sysJsonMsg->data(true, ['date' => $date, 'data' => $data]);
                break;
            case 'single':
                $table = $this->getTableName();
                if(!$table) Yii::$app->sysJsonMsg->data(false, false);

                $offset = $post['offset'];
                $sql = "SELECT sum(siteflow) as siteflow, iTime FROM logs.{$table} {$where} group by iTime order by iTime asc limit {$offset}, 1";
                $arr = Yii::$app->db->createCommand($sql)->query()->read();
                if($arr){
                    $result = ['date' => date('Y-m-d H:i:s', $arr['iTime']), 'data' => $arr['siteflow']];
                    Yii::$app->sysJsonMsg->data(true, $result);
                }
                Yii::$app->sysJsonMsg->data(false, false);
                break;
        }
    }

    public function actionConcurrency(){
        $result = $this->getRender();
        if(!(false === $result)) return $result;

        $post = Yii::$app->request->post();

        $where = [];
        if('' != $post['webSize']) $where[] = "`sWebSiteName`='{$post['webSize']}'";
        if('' != $post['startDate'] && '' != $post['endDate']){
            $startDate = strtotime($post['startDate']);
            $endDate = strtotime($post['endDate']);
            $where[] = "`iTime`>='{$startDate}'";
            $where[] = "`iTime`<='{$endDate}'";
        }
        if(0 < count($where)) $where = 'where '.join(' and ', $where);
        else $where = '';

        switch($post['type'])
        {
            case 'all':
                $initResult = $this->getDataHistoryInit($startDate, $endDate);
                if(!$initResult) Yii::$app->sysJsonMsg->msg(false, $this->translate->getTranslateBySymbol('incorrectTimeParameter'));

                $sql = "SELECT sum(iConConnections) as iConConnections, iTime FROM t_web_connections_all {$where} group by iTime order by iTime asc";
                $arr = Yii::$app->db->createCommand($sql)->query()->readAll();
                $date = $data = [];
                foreach($arr as $item){
                    $date[] = date('Y-m-d H:i:s', $item['iTime']);
                    $data[] = $item['iConConnections'];
                    //$data[] = rand(0, 10000);
                }
                Yii::$app->sysJsonMsg->data(true, ['date' => $date, 'data' => $data]);
                break;
            case 'single':
                $table = $this->getTableName();
                if(!$table) Yii::$app->sysJsonMsg->data(false, false);

                $offset = $post['offset'];
                $sql = "SELECT sum(iConConnections) as iConConnections, iTime FROM logs.{$table} {$where} group by iTime order by iTime asc limit {$offset}, 1";
                $arr = Yii::$app->db->createCommand($sql)->query()->read();
                if($arr){
                    $data = ['date' => date('Y-m-d H:i:s', $arr['iTime']), 'data' => $arr['iConConnections']];
                    Yii::$app->sysJsonMsg->data(true, $data);
                }
                Yii::$app->sysJsonMsg->data(false, false);
                break;
        }
    }

    public function actionConnect(){
        $result = $this->getRender();
        if(!(false === $result)) return $result;

        $post = Yii::$app->request->post();

        $where = [];
        if('' != $post['webSize']) $where[] = "`sWebSiteName`='{$post['webSize']}'";
        if('' != $post['startDate'] && '' != $post['endDate']){
            $startDate = strtotime($post['startDate']);
            $endDate = strtotime($post['endDate']);
            $where[] = "`iTime`>='{$startDate}'";
            $where[] = "`iTime`<='{$endDate}'";
        }
        if(0 < count($where)) $where = 'where '.join(' and ', $where);
        else $where = '';

        switch($post['type'])
        {
            case 'all':
                $initResult = $this->getDataHistoryInit($startDate, $endDate);
                if(!$initResult) Yii::$app->sysJsonMsg->msg(false, $this->translate->getTranslateBySymbol('incorrectTimeParameter'));

                $sql = "SELECT sum(iNewConnections) as iNewConnections, sum(iTransactions) as iTransactions, iTime FROM t_web_connections_all {$where} group by iTime order by iTime asc";
                $arr = Yii::$app->db->createCommand($sql)->query()->readAll();
                $date = $iNewConnections = $iTransactions = [];
                foreach($arr as $item){
                    $date[] = date('Y-m-d H:i:s', $item['iTime']);
                    $iNewConnections[] = $item['iNewConnections'];
                    $iTransactions[] = $item['iTransactions'];
                    //$data[] = rand(0, 10000);
                }
                Yii::$app->sysJsonMsg->data(true, ['date' => $date, 'iNewConnections' => $iNewConnections, 'iTransactions' => $iTransactions]);
                break;
            case 'single':
                $table = $this->getTableName();
                if(!$table) Yii::$app->sysJsonMsg->data(false, false);

                $offset = $post['offset'];
                $sql = "SELECT sum(iNewConnections) as iNewConnections, sum(iTransactions) as iTransactions, iTime FROM logs.{$table} {$where} group by iTime order by iTime asc limit {$offset}, 1";
                $arr = Yii::$app->db->createCommand($sql)->query()->read();
                if($arr){
                    $data = [
                        'date' => date('Y-m-d H:i:s',$arr['iTime']),
                        'iNewConnections' => $arr['iNewConnections'],
                        'iTransactions' => $arr['iTransactions']
                    ];
                    Yii::$app->sysJsonMsg->data(true, $data);
                }
                Yii::$app->sysJsonMsg->data(false, false);
                break;
        }
    }
}
