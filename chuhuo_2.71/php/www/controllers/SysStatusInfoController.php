<?php

namespace app\controllers;

use Yii;
use app\widget\AdminListConfig;
use app\logic\BaseController;
use app\logic\waf\models\SelectList;
use app\logic\waf\models\AlertLogsCH;

class SysStatusInfoController extends BaseController
{
    public $layout = 'chart-main';

    public function actionIndex()
    {
        if (Yii::$app->request->isGet) {
            return $this->render('/chart-main/sys-status-info/index', [
                'userConfig' => $this->indexChartSet('get'),
            ]);
        }
    }

    public function actionUserConfigSave($userConfig)
    {
        $this->indexChartSet('set', $userConfig);
        Yii::$app->sysJsonMsg->msg(true, '');
    }

    public function indexChartSet($type, $userConfig = '')
    {
        $cachePath = Yii::$app->sysPath->cachePath;
        $file = "{$cachePath}indexChartSet.serialize";
        if (!is_file($file)) file_put_contents($file, '');

        switch ($type) {
            case 'get':
                return file_get_contents($file);
                break;
            case 'set':
                file_put_contents($file, $userConfig);
                return true;
                break;
            default:
                return false;
        }
    }

    public function getRender()
    {
        if (Yii::$app->request->isGet) {
            $action = Yii::$app->controller->action->id;
            return $this->render("/chart-main/sys-status-info/{$action}", []);
        } else return false;
    }

    /**
     * 网站访问分析(当月)
     * @return bool|string
     * @throws \yii\db\Exception
     */
    public function actionGetWebVisitInfo()
    {
        $result = $this->getRender();
        if(!(false === $result)) return $result;

        $db = Yii::$app->db;

        $time = time();
        $ym = date('Ym', $time);
        $yymm = date('Y-m', $time);
        $tableal = 't_alertlogs';
        $tableru = 't_ruleid';

        $exist   = $db->createCommand("SHOW TABLES FROM logs LIKE '%{$tableal}%'")->query()->read();
        $rows = $db->createCommand("SELECT SUM(pages) AS p,SUM(pages_nv) AS pn FROM logs.general WHERE year_monthed='{$ym}'")->query()->read();
        $rnum = 0;
        if ($exist)
        {
            $rnum = $db->createCommand("SELECT SUM(hits) AS num FROM logs.$tableru WHERE DATE_FORMAT(`logdate`,'%Y-%m')='$yymm'")->query()->read();
            $rnum = $rnum ? intval($rnum['num']) : 0;
        }

        $data = [];
        $pv1 = intval($rows['p']);
        $pv2 = intval($rows['pn']);
        $pv3 = $rnum;

        $data[] = array('name' => $this->translate->getTranslateBySymbol('normalAccess'), 'value' => $pv1 ? $pv1 : 0);
        $data[] = array('name' => $this->translate->getTranslateBySymbol('fromReptiles'), 'value' => $pv2 ? $pv2 : 0);
        $data[] = array('name' => $this->translate->getTranslateBySymbol('fromThreat'), 'value' => $pv3 ? $pv3 : 0);

        Yii::$app->sysJsonMsg->data(true, $data);
    }

    /**
     * 入侵数量统计(当月)
     * @return array|bool|string
     * @throws \yii\db\Exception
     */
    public function actionGetInvadeInfoCount()
    {
        $result = $this->getRender();
        if(!(false === $result)) return $result;

        $result = $this->getInvadeInfo2('count');
        Yii::$app->sysJsonMsg->data(true, $result);
    }

    /**
     * 入侵类别统计(当月)
     * @return array|bool|string
     * @throws \yii\db\Exception
     */
    public function actionGetInvadeInfoSort()
    {
        $result = $this->getRender();
        if(!(false === $result)) return $result;

        $result = $this->getInvadeInfo2('sort');
        Yii::$app->sysJsonMsg->data(true, $result);
    }

    public function getInvadeInfo($type)
    {
        $db = Yii::$app->db;

        $time = time();
        $ym = date('Ym', $time);
        $ymd = date('Y-m-d', $time);
        $yymm = date('Y-m', $time);
        $tableal = 't_alertlogs';
        $tablese = 't_countsety';
        $tableru = 't_ruleid';
        $tableout = 't_weboutlogs';
        $tabledos = 't_ddoslogs';
        $bdblockedlogs_db = 't_bdblockedlogs';

        $data1 = array();   //入侵数量统计（当月）
        $data2 = array();   //入侵类别统计（当月）
        $other   = $rsnum = 0;

        //获取json文件并解释为数组
        $cacheSort = Yii::$app->sysPath->cachePath;
        $cacheSort = file_get_contents($cacheSort.'invadeinfo.json');
        $cacheSort = json_decode($cacheSort, true);

        //入侵类别统计（当月）
        if('sort' == $type){
            $cacheMaxId = $cacheSort['last_ids'];#其他表最大ID值
            $maxId = $cacheMaxId['t_alertlogs'];#表t_alertlogs最大ID值

            $cacheSort = $cacheSort['counts'];

            //$dayInMonthFirst = "{$yymm}-1";
            //$dayInMonthLast = date('Y-m-t');
            $cats    = $db->createCommand("SELECT `id`,`name`,`desc` FROM waf.t_rulecat WHERE 1 ORDER BY id ASC")->queryAll();
            $otherCa = Yii::$app->db->createCommand("select AttackType, count(*) as c from logs.t_alertlogs where id > {$maxId} group by AttackType")->queryAll();
            $otherCa = array_column($otherCa, 'c', 'AttackType');
            foreach($cats as $k=>$v){//根据类别读取realid
                #原始方法
                #$num = $db->createCommand("SELECT SUM(hits) AS num FROM logs.$tableru WHERE DATE_FORMAT(`logdate`,'%Y-%m')='$yymm' AND ruleid IN (SELECT realid FROM waf.t_rules WHERE type='$v[name]' UNION SELECT realid FROM waf.t_baseaccessctrl WHERE type='$v[name]')")->query()->read();
                #$num = $db->createCommand("SELECT SUM(hits) AS num FROM logs.$tableru WHERE DATE_FORMAT(`logdate`,'%Y-%m')='$yymm'")->query()->read();
                #$num = $num ? intval($num['num']) : 0;

                //$alertLogs = \app\modelLogs\AlertLogs::find();
                #根据类别realid作为条件
                #$realIdArr = \app\logic\waf\helpers\WafModels::getRealIdBytype($v[name]);
                #if( !empty($realIdArr) ) $alertLogs->where(['RuleID' => $realIdArr]);
                #根据原表AttackType字段值为条件
                //$alertLogs->where(['AttackType' => $v[name]]);
                //$num = $alertLogs->andWhere(['>=', 'LogDateTime', $dayInMonthFirst])->andWhere(['<=', 'LogDateTime', $dayInMonthLast])->count();

                $data2['name'][] = $this->translate->getTranslate($v['desc']);
                //$data2['val'][]  = $num;
                $data2['val'][] = $cacheSort[$v[name]] + ($otherCa[$v[name]] ?? 0);
            }
            /*$outlog = $db->createCommand("SELECT COUNT(*) AS num FROM logs.$tableout WHERE DATE_FORMAT(`dt`,'%Y-%m')='$yymm'")->query()->read();
            $ddoslog = $db->createCommand("SELECT COUNT(*) AS num FROM logs.$tabledos WHERE DATE_FORMAT(FROM_UNIXTIME(`logtime`),'%Y-%m')='$yymm'")->query()->read();
            $custom = $db->createCommand("SELECT SUM(hits) AS num FROM logs.$tableru WHERE DATE_FORMAT(`logdate`,'%Y-%m')='$yymm' AND ruleid NOT IN (SELECT realid FROM waf.t_rules UNION SELECT realid FROM waf.t_baseaccessctrl)")->query()->read();

            //智能阻断
            $sql = "SELECT COUNT(*) as num FROM logs.{$bdblockedlogs_db} WHERE DATE_FORMAT(FROM_UNIXTIME(`logtime`),'%Y-%m')='$yymm'";
            $bdblockedlogs_sum = $db->createCommand($sql)->query()->read();

            $custom = $custom ? intval($custom['num']) : 0;
            $outlog = $outlog ? intval($outlog['num']) : 0;
            $ddoslog = $ddoslog ? intval($ddoslog['num']) : 0;
            $bdblockedlogs_val= $bdblockedlogs_sum['num']?intval($bdblockedlogs_sum['c']):0;*/


            $data2['name'][] = $this->translate->getTranslateBySymbol('dDosAttack');
            $maxId = $cacheMaxId['t_ddoslogs'];
            $ddoslog = $db->createCommand("SELECT COUNT(*) AS num FROM logs.$tabledos WHERE id > {$maxId} AND DATE_FORMAT(FROM_UNIXTIME(`logtime`),'%Y-%m')='$yymm'")->query()->read();
            //$data2['val'][]  = $ddoslog;
            $data2['val'][]  = $cacheSort['DDOS'] + ($ddoslog['num'] ?? 0);

            $data2['name'][] = $this->translate->getTranslateBySymbol('illegalOutLink');
            $maxId = $cacheMaxId['t_weboutlogs'];
            $outlog = $db->createCommand("SELECT COUNT(*) AS num FROM logs.$tableout WHERE id > {$maxId} AND DATE_FORMAT(`dt`,'%Y-%m')='$yymm'")->query()->read();
            //$data2['val'][]  = $outlog;
            $data2['val'][]  = $cacheSort['WEBOUT'] + ($outlog['num'] ?? 0);

            $data2['name'][] = $this->translate->getTranslateBySymbol('smartBlock');
            $maxId = $cacheMaxId['t_bdblockedlogs'];
            $sql = "SELECT COUNT(*) as num FROM logs.{$bdblockedlogs_db} WHERE id > {$maxId} AND DATE_FORMAT(FROM_UNIXTIME(`logtime`),'%Y-%m')='$yymm'";
            $bdblockedlogsSum = $db->createCommand($sql)->query()->read();
            //$data2['val'][]  = $bdblockedlogs_val;
            $data2['val'][]  = $cacheSort['SMARTBLOCK'] + ($bdblockedlogsSum['num'] ?? 0);

            $data2['name'][] = $this->translate->getTranslateBySymbol('undefinition');
            $maxId = $cacheMaxId['t_ruleid'];
            $custom = $db->createCommand("SELECT count(*) AS num FROM logs.t_alertlogs WHERE id > {$maxId} AND DATE_FORMAT(`LogDateTime`,'%Y-%m')='$yymm' AND AttackType='None'")->query()->read();
            //$data2['val'][]  = $custom;
            $data2['val'][]  = $cacheSort['UNDEFINED'] + ($custom['num'] ?? 0);
            return $data2;
        }

        //入侵数量统计（当月）
        if('count' == $type){
            //原有统计方式
            /*$sety  = $db->createCommand("SELECT sum(emergency) as emergency,sum(alert) as alert,sum(critical) as critical,sum(error) as error,sum(warning) as warning FROM logs.$tablese WHERE DATE_FORMAT(`logdate`,'%Y-%m')='$yymm'")->query()->read();
            $i1    =  intval($sety['emergency']);
            $i2    =  intval($sety['alert']);
            $i3    =  intval($sety['critical']);
            $i4    =  intval($sety['error']);
            $i5    =  intval($sety['warning']);
            $total = $i1+$i2+$i3+$i4+$i5;
            if($total>0){
                $data1[] = array('name'=> $this->translate->getTranslateBySymbol('urgent'), 'value'=> $i1 ? $i1 : 0);
                $data1[] = array('name'=> $this->translate->getTranslateBySymbol('alert'), 'value'=> $i2 ? $i2 : 0);
                $data1[] = array('name'=> $this->translate->getTranslateBySymbol('serious'), 'value'=> $i3 ? $i3 : 0);
                $data1[] = array('name'=> $this->translate->getTranslateBySymbol('error'), 'value'=> $i4 ? $i4 : 0);
                $data1[] = array('name'=> $this->translate->getTranslateBySymbol('warn'), 'value'=> $i5 ? $i5 : 0);
            }*/

            $cacheSort = $cacheSort['countsety'];
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('urgent'), 'value'=> $cacheSort['EMERG']);
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('alert'), 'value'=> $cacheSort['ALERT']);
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('serious'), 'value'=> $cacheSort['CRITI']);
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('error'), 'value'=> $cacheSort['ERROR']);
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('warn'), 'value'=> $cacheSort['WARN']);

            return $data1;
        }
    }

    /**
     * 入侵数量统计（当月）与 入侵类别统计（当月）
     * @param $type
     * @return array
     * @throws \yii\db\Exception
     */
    public function getInvadeInfo2($type)
    {
        $yymm = date('Y-m', time());

        $data1 = array();   //入侵数量统计（当月）
        $data2 = array();   //入侵类别统计（当月）

        //获取python预统计数据
        $cacheSort = $this->getPreCountData();

        //入侵类别统计（当月）
        if('sort' == $type)
        {
            $cacheMaxId = $cacheSort['last_ids'];#其他表最大ID值
            $cacheSort = $cacheSort['counts'];

            // 攻击类别
            $ruleCatArr = SelectList::ruleCatArr(false);
            // 统计攻击类型数据
            $otherCa = $this->getCountInvadeData($cacheMaxId['t_alertlogs']);
            foreach( $ruleCatArr as $k=>$v )
            {
                //根据类别读取realid
                $data2['name'][] = $this->translate->getTranslate($v['desc']);
                $data2['val'][] = $cacheSort[$v[name]] + ($otherCa[$v[name]] ?? 0);
            }

            // DDOS攻击数据
            $data2['name'][] = $this->translate->getTranslateBySymbol('dDosAttack');
            $ddoslog = $this->getCountDdosData($cacheMaxId['t_ddoslogs'], $yymm);
            $data2['val'][]  = $cacheSort['DDOS'] + ($ddoslog['num'] ?? 0);

            // 非法外联数据
            $data2['name'][] = $this->translate->getTranslateBySymbol('illegalOutLink');
            $outlog = $this->getCountWebOutLogsData($cacheMaxId['t_weboutlogs'], $yymm);
            $data2['val'][]  = $cacheSort['WEBOUT'] + ($outlog['num'] ?? 0);

            // 智能阻断
            $data2['name'][] = $this->translate->getTranslateBySymbol('smartBlock');
            $bdblockedlogsSum = $this->getCountBdBlockedLogs($cacheMaxId['t_bdblockedlogs'], $yymm);
            $data2['val'][]  = $cacheSort['SMARTBLOCK'] + ($bdblockedlogsSum['num'] ?? 0);

            return $data2;
        }

        //入侵数量统计（当月）
        if('count' == $type)
        {
            $cacheSort = $cacheSort['countsety'];
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('urgent'), 'value'=> $cacheSort['EMERG']);
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('alert'), 'value'=> $cacheSort['ALERT']);
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('serious'), 'value'=> $cacheSort['CRITI']);
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('error'), 'value'=> $cacheSort['ERROR']);
            $data1[] = array('name'=> $this->translate->getTranslateBySymbol('warn'), 'value'=> $cacheSort['WARN']);

            return $data1;
        }
    }

    /**
     * 产品信息
     * @return string
     * @throws \yii\db\Exception
     */
    public function actionGetProductInfo()
    {
        $devInfo = Yii::$app->db->createCommand("SELECT * FROM t_devinfo WHERE 1 LIMIT 1")->query()->read();

        $action = Yii::$app->controller->action->id;
        return $this->render("/chart-main/sys-status-info/{$action}", ['devInfo' => $devInfo]);
    }

    public function actionGetComprehensiveAnalysisDay()
    {
        $result = $this->getRender();
        if(!(false === $result)) return $result;

        $result = $this->getComprehensiveAnalysis();
        Yii::$app->sysJsonMsg->data(true, $result['day']);
    }

    public function actionGetComprehensiveAnalysisMonth()
    {
        $result = $this->getRender();
        if(!(false === $result)) return $result;

        $result = $this->getComprehensiveAnalysis();
        Yii::$app->sysJsonMsg->data(true, $result['month']);
    }

    public function getComprehensiveAnalysis()
    {
        /**============ 综合分析(当月//按天) ==============*/
        $days = array();    //横轴时间，单位：天，当月目前的天数
        $nowtime = time();
        $year =date('Y',$nowtime);//当前年份
        $month =date('m',$nowtime);//当前月份
        $dd = intval(date('j',$nowtime));//当前小时数
        $sql  = "SELECT `day`,visits,pages,hits,bandwidth FROM logs.daily WHERE left(`day`,6)='{$year}{$month}' ORDER BY `day` ASC";
        $rows = Yii::$app->db->createCommand($sql)->queryAll();
        $visit = $page = $filed = array();  //竖轴数据
        $rs_days = array();
        foreach ($rows as $k=>$v){
            if(isset($rs_days[$v['day']])) {
                $rs_days[$v['day']]['visits'] += $v['visits'];
                $rs_days[$v['day']]['pages'] += $v['pages'];
                $rs_days[$v['day']]['hits'] += $v['hits'];
            }else{
                $rs_days[$v['day']]['visits'] = $v['visits'];
                $rs_days[$v['day']]['pages'] = $v['pages'];
                $rs_days[$v['day']]['hits'] = $v['hits'];
            }
        }
        for($i=1; $i<=$dd;$i++){
            $days[] = $i;
            $k      = $year.$month.str_pad($i, 2, '0', STR_PAD_LEFT);
            if($rs_days[$k]){
                $visit[$i]  = $rs_days[$k]['visits'];
                $page[$i]   = $rs_days[$k]['pages'];
                $filed[$i]  = $rs_days[$k]['hits'];
            }else{
                $visit[$i]  = 0;
                $page[$i]   = 0;
                $filed[$i]  = 0;
            }
        }
        $visit = array_values($visit);
        $page = array_values($page);
        $filed = array_values($filed);
        /**============ 综合分析(当年//按月) ==============*/
        $months = array();    //横轴时间，单位：天，当月目前的天数
        $year =date('Y',$nowtime);//当前年份
        $month =date('m',$nowtime);//当前月份
        $sql  = "SELECT `year_monthed`,visits,visits_unique,pages,hits FROM logs.general WHERE left(`year_monthed`,4)='{$year}' ORDER BY `year_monthed` ASC";
        $rows = Yii::$app->db->createCommand($sql)->queryAll();
        $visits = $visits_unique = $pages = $files = array();  //竖轴数据
        $rs_months = array();
        foreach ($rows as $k=>$v){
            if(isset($rs_months[$v['year_monthed']])) {
                $rs_months[$v['year_monthed']]['visits'] += $v['visits'];
                $rs_months[$v['year_monthed']]['visits_unique'] += $v['visits_unique'];
                $rs_months[$v['year_monthed']]['pages'] += $v['pages'];
                $rs_months[$v['year_monthed']]['hits'] += $v['hits'];
            }else{
                $rs_months[$v['year_monthed']]['visits'] = $v['visits'];
                $rs_months[$v['year_monthed']]['visits_unique'] = $v['visits_unique'];
                $rs_months[$v['year_monthed']]['pages'] = $v['pages'];
                $rs_months[$v['year_monthed']]['hits'] = $v['hits'];
            }
        }
        for($i=1; $i<=intval($month);$i++){
            $months[] = $i;
            $k        = $year.str_pad($i, 2, '0', STR_PAD_LEFT);
            if($rs_months[$k]){
                $visits[$i]  = $rs_months[$k]['visits'];
                $visits_unique[$i]  = $rs_months[$k]['visits_unique'];
                $pages[$i]   = $rs_months[$k]['pages'];
                $files[$i]  = $rs_months[$k]['hits'];
            }else{
                $visits[$i]  = 0;
                $visits_unique[$i]  = 0;
                $pages[$i]   = 0;
                $files[$i]  = 0;
            }
        }
        $visits = array_values($visits);
        $visits_unique = array_values($visits_unique);
        $pages = array_values($pages);
        $files = array_values($files);

        $dataDay['date'] = $days;//综合分析(当月//按天)，横轴时间，单位：天，当月目前的天数
        /*$dataDay['visit'] = $visit;//综合分析(当月//按天)，浏览数
        $dataDay['page'] = $page;//综合分析(当月//按天)，页面数
        $dataDay['filed'] = $filed;//综合分析(当月//按天)，文件数*/

        $dataDay['data'] = [
            ['name' => $this->translate->getTranslateBySymbol('browseCount'), 'data' => $visit],
            ['name' => $this->translate->getTranslateBySymbol('pageCount'), 'data' => $page],
            ['name' => $this->translate->getTranslateBySymbol('fileCount'), 'data' => $filed],
        ];

        /*$dataMonth['months'] = $months;//综合分析(当年//按月)，横轴时间，单位：月，当年目前的月份
        $dataMonth['visits'] = $visits;//综合分析(当年//按月)，访问次数
        $dataMonth['visits_unique'] = $visits_unique;//综合分析(当年//按月)，访问人数
        $dataMonth['pages'] = $pages;//综合分析(当年//按月)，页面数
        $dataMonth['files'] = $files;//综合分析(当年//按月)，文件数*/

        $dataMonth['date'] = $months;

        $dataMonth['data'] = [
            ['name' => $this->translate->getTranslateBySymbol('browseCount'), 'data' => $visits],
            ['name' => $this->translate->getTranslateBySymbol('visitorsCount'), 'data' => $visits_unique],
            ['name' => $this->translate->getTranslateBySymbol('pageCount'), 'data' => $pages],
            ['name' => $this->translate->getTranslateBySymbol('fileCount'), 'data' => $files],
        ];

        return ['day' => $dataDay, 'month' => $dataMonth];
    }

    /**
     * 实时流量
     * @return string
     */
    public function actionSystemTraffic()
    {
        $action = Yii::$app->controller->action->id;
        $netport = array_column(
            \app\modelFirewall\Netport::find()->where(['like', 'sLan', 'Lan'])->asArray()->all(),
            'sLan',
            'sPortName');
        return $this->renderPartial("/chart-main/sys-status-info/{$action}", ['netport' => $netport]);
    }

    /**
     * 系统资源占用
     * @return string
     */
    public function actionSystemUse()
    {
        $action = Yii::$app->controller->action->id;
        return $this->renderPartial("/chart-main/sys-status-info/{$action}", []);
    }

    /**
     * 获取python预统计数据
     * @return array
     */
    private function getPreCountData()
    {
        $filename = Yii::$app->sysPath->cachePath.'invadeinfo.json';
        if( !file_exists($filename) )
        {
            return $this->getDefaultCountDataJson();
        }

        //获取json文件并解释为数组
        $cacheSort = file_get_contents($filename);
        $cacheSort = json_decode($cacheSort, true);

        return $cacheSort;
    }

    /**
     * python预设的预统计数据
     * @return mixed
     */
    private function getDefaultCountDataJson()
    {
        $preData = '{"counts": {"SMARTBLOCK": 0, "XSS": 0, "ACCESSCTRL": 0, "PROTOCOL": 0, "UNDEFINED": 0, "GENERIC": 0, "WEBOUT": 0, "CUSTOM": 0, "CC": 0, "SQLI": 0, "DDOS": 0, "OTHER": 0, "TROJANS": 0, "OVERFLOW": 0, "LEAKAGE": 0}, "last_ids": {"t_alertlogs": 0, "t_weboutlogs": 0, "t_cclogs": 0, "t_bdblockedlogs": 0, "t_countsety": 0, "t_ddoslogs": 0, "t_ruleid": 0}, "last_runtime": "2018-03-01 00:00:03", "countsety": {"CRITI": 0, "WARN": 0, "EMERG": 0, "ERROR": 0, "ALERT": 0}}';
        return json_decode($preData, true);
    }

    /**
     * 统计攻击类型数据
     * @param $maxId
     * @return array
     * @throws \yii\db\Exception
     */
    private function getCountInvadeData($maxId)
    {
        $sql = "select AttackType, count(*) as c from logs.t_alertlogs where id > {$maxId} group by AttackType";
        $otherCa = Yii::$app->db->createCommand($sql)->queryAll();
        if( empty($otherCa) ) return $otherCa;

        $otherCa = array_column($otherCa, 'c', 'AttackType');
        if( isset($otherCa['B&W']) )
        {
            $otherCa['ACCESSCTRL'] += $otherCa['B&W'];
            unset($otherCa['B&W']);
        }

        return $otherCa;
    }

    /**
     * 统计ddos的数据
     * @param $maxId
     * @param $yymm
     * @return array
     * @throws \yii\db\Exception
     */
    private function getCountDdosData($maxId, $yymm)
    {
        $tabledos = 't_ddoslogs';
        $sql = "SELECT COUNT(*) AS num FROM logs.$tabledos WHERE id > {$maxId} AND DATE_FORMAT(FROM_UNIXTIME(`logtime`),'%Y-%m')='$yymm'";
        $ddoslog = Yii::$app->db->createCommand($sql)->query()->read();

        return $ddoslog;
    }

    /**
     * 统计非法外联数据
     * @param $maxId
     * @param $yymm
     * @return array
     * @throws \yii\db\Exception
     */
    private function getCountWebOutLogsData($maxId, $yymm)
    {
        $tableout = 't_weboutlogs';
        $sql = "SELECT COUNT(*) AS num FROM logs.$tableout WHERE id > {$maxId} AND DATE_FORMAT(`dt`,'%Y-%m')='$yymm'";
        $outlog = Yii::$app->db->createCommand($sql)->query()->read();

        return $outlog;
    }

    /**
     * 智能阻断数据
     * @param $maxId
     * @param $yymm
     * @return array
     * @throws \yii\db\Exception
     */
    private function getCountBdBlockedLogs($maxId, $yymm)
    {
        $bdblockedlogs_db = 't_bdblockedlogs';
        $sql = "SELECT COUNT(*) as num FROM logs.{$bdblockedlogs_db} WHERE id > {$maxId} AND DATE_FORMAT(FROM_UNIXTIME(`logtime`),'%Y-%m')='$yymm'";
        $bdblockedlogsSum = Yii::$app->db->createCommand($sql)->query()->read();

        return $bdblockedlogsSum;
    }
}
