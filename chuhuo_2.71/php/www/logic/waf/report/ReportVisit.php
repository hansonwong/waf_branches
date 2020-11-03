<?php
namespace app\logic\waf\report;

use app\modelFirewall\TbNetPort;
use app\modelLogs\Browser;
use app\modelLogs\Counturi;
use app\modelLogs\Daily;
use app\modelLogs\Errors;
use app\modelLogs\General;
use app\modelLogs\Os;
use app\modelLogs\Pageref;
use app\modelLogs\PagesModel;
use app\modelLogs\Robot;
use app\modelLogs\Searchref;
use app\modelLogs\SearchWords;
use app\modelLogs\Session;
use app\models\NicsFlow;
use app\models\Devinfo;
use app\models\Nicset;
use Yii;

class ReportVisit
{
    private $translate;

    public function __construct()
    {
        $this->translate = Yii::$app->sysLanguage;
    }

    /**
     * 报表计算
     * @param string $start_date 开始日期 2018-02-01
     * @param string $end_date 结束日期 2018-02-08|2018-02-28
     * @return array 计算结果
     * @throws \yii\base\ExitException
     */
    public function reportCalculate($start_date = '', $end_date = '')
    {
        //参数验证
        if( empty(trim($start_date)) || empty(trim($end_date)) )
        {
            Yii::$app->response->format = 'json';
            Yii::$app->response->data = ['code' => 'F', 'info' => $this->translate->getTranslateBySymbol('selectTheQueryDate')];
            Yii::$app->end();
        }

        $visit_data = [];

        // 报表日期
        $reportDate = date('Y-m', strtotime($start_date));

        //日期格式化
        $start_date = date_create(trim($start_date));
        $start_date = date_format($start_date, 'Y-m-d');
        $end_date = date_create(trim($end_date));
        $end_date = date_format($end_date, 'Y-m-d');

        //年月日
        $end_year_month = date_format(date_create($end_date), 'Ym');
        $year = date_format(date_create($end_date), 'Y');
        $lastDay = date('d', strtotime($end_date)); // 获取当前日期最后一天

        //报表概要信息
        $visit_data['data_section'] = $start_date . '~' . $end_date;
        $visit_data['create_time'] = date('Y-m-d H:i:s');
        $visit_data['device_model'] = Devinfo::find()->one()->getAttribute('model');
        $visit_data['device_ip'] = TbNetPort::findOne(['sPortName' => 'enp8s0'])->sIPV4Address;
        $visit_data['desc'] = $this->translate->getTranslateBySymbol('reportVisitFlow');

        // 根据日期获取主机列表的查询条件
        //$whereStr= $this->getGeneralWhere($reportDate);
        //主机列表 避免重复查询影响效率，先查出所需数据
        $domain_year_month = General::findAll(['year_monthed' => $end_year_month]);    //当月主机数据
        //$domain_year_month = General::find()->where($whereStr)->distinct()->all();

        //访问威胁
        $thread_list = Counturi::find()->select("Host,SUM(Hits) AS total")
            ->where("DATE_FORMAT(`logdate`,'%Y%m')='{$end_year_month}'")
            ->groupBy('Host')->asArray()->all();
        $thread_visit = [];
        foreach( $thread_list as $thread )
        {
            $thread_visit[$thread['Host']] = $thread['total'];
        }

        //综合分析(按月)-------------------
        $domain_year = General::find()->where("left(`year_monthed`,4)='{$year}'")->all();
        $year_domain = [];
        foreach ($domain_year as $item) {
            $year_domain[$item->domain][$item->year_monthed]['visits'] = $item->visits;
            $year_domain[$item->domain][$item->year_monthed]['visits_unique'] = $item->visits_unique;
            $year_domain[$item->domain][$item->year_monthed]['pages'] = $item->pages + $item->pages_nv;
            $year_domain[$item->domain][$item->year_monthed]['files'] = $item->hits + $item->hits_nv;
        }
        //补齐月份
        foreach ($year_domain as $domain => $rows) {
            for ($i = 1; $i <= 12; $i++) {
                $m = $year . str_pad($i, 2, '0', STR_PAD_LEFT);
                if (!isset($year_domain[$domain][$m])) {
                    $year_domain[$domain][$m]['visits'] = 0;
                    $year_domain[$domain][$m]['visits_unique'] = 0;
                    $year_domain[$domain][$m]['pages'] = 0;
                    $year_domain[$domain][$m]['files'] = 0;
                }
            }
        }

        //综合分析(按天)  网站流量(按天)-------------------
        $daily_list = Daily::find()->where("left(`day`,6)='{$end_year_month}'")->orderBy('day')->all();
        $daily_day = [];
        foreach ($daily_list as $daily) {
            $day = substr($daily->day, -2, 2);
            $daily_day[$daily->domain][$day]['visits'] = $daily->visits;
            $daily_day[$daily->domain][$day]['pages'] = $daily->pages;
            $daily_day[$daily->domain][$day]['files'] = $daily->hits;
            $daily_day[$daily->domain][$day]['bandwidth'] = round($daily->bandwidth / 1024);
        }
        //补齐天数
        foreach ($daily_day as $domain => $rows) {
            for ($i = 1; $i <= $lastDay; $i++) {
                $i = str_pad($i, 2, '0', STR_PAD_LEFT);
                if (!isset($daily_day[$domain][$i])) {
                    $daily_day[$domain][$i]['visits'] = 0;
                    $daily_day[$domain][$i]['pages'] = 0;
                    $daily_day[$domain][$i]['files'] = 0;
                    $daily_day[$domain][$i]['bandwidth'] = 0;
                }
            }
        }

        //用户在您网站停留的时间-------------------
        $stay_list = Session::find()->where(['year_monthed' => $end_year_month])
            ->orderBy('domain ASC,ranged ASC')->all();
        $user_stay_list = [];
        foreach ($stay_list as $item) {
            $user_stay_list[$item->domain][] = ['visits' => $item->visits, 'ranged' => $item->ranged];
        }

        //爬虫分析-------------------
        $robot_list = Robot::find()->select("name,hits")->where(['year_monthed' => $end_year_month])
            ->orderBy('hits DESC')->indexBy('domain')->limit(7)->all();

        //网络流量-------------------
        //$max_time = NicsFlow::find()->max('time');
        $network_flow_list = NicsFlow::findAll(['time' => $reportDate]);

        $net_mode = array('half' => $this->translate->getTranslateBySymbol('halfDuplex'),
            'full' => $this->translate->getTranslateBySymbol('fullDuplex'),
            'auto' => $this->translate->getTranslateBySymbol('automatic'));
        $network_flow = [];
        foreach ($network_flow_list as $row) {
            $item = [];
            $item['port'] = $row->nic;
            $item['model'] = $net_mode[$row->mode];
            $item['status'] = $row->status == 1 ? $this->translate->getTranslateBySymbol('connected') : $this->translate->getTranslateBySymbol('unconnected');
            $item['receive_pack'] = $row->rcv_pks;
            $item['send_pack'] = $row->snd_pks;
            $item['receive_byte'] = $row->rcv_bytes;
            $item['send_byte'] = $row->snd_bytes;
            $item['receive_error'] = $row->rcv_errs;
            $item['send_error'] = $row->snd_errs;
            $item['receive_lost'] = $row->rcv_losts;
            $item['send_lost'] = $row->snd_losts;
            $network_flow[] = $item;
        }

        /**
         * 依次统计
         * 网站入口页面(被访问次数-TOP10)-------------------
         * 网站出口页面(被访问次数-TOP10)-------------------
         * 页面访问排名-TOP10-------------------
         */
        $pageModel = new PagesModel();
        $pageModel::$table_name = $end_year_month;
        $website_section = ['in' => 'entry', 'out' => 'exited', 'top' => 'pages'];
        foreach ($website_section as $key => $value)
        {
            $visit_data["website_{$key}"] = [];

            $website_list = $pageModel::find()->where(['>', $value, 0])->orderBy("domain ASC,{$value} DESC")->all();
            //获取前10条
            $website_top10 = $this->getTop10($website_list);
            //前10条总数
            $website_total = $this->getFieldTotal($website_top10, $value);
            //组织字段
            foreach ($website_top10 as $domain => $rows) {
                foreach ($rows as $row) {

                    $per = (round($row[$value] / $website_total[$domain], 2) * 100) . '%';

                    $item = [];
                    $item['url'] = 'http://' . $domain . $row->url;
                    $item['number'] = $row[$value];
                    $item['percent'] = $website_total[$domain] == 0 ? 0 : $per;
                    $visit_data["website_{$key}"][$domain][] = $item;
                }
            }
        }

        //错误码排名-TOP10-------------------
        $visit_data["errors_top10"] = [];
        $errors_list = Errors::find()
            ->andWhere(['>', 'hits', 0])
            ->andWhere(['year_monthed' => $end_year_month])
            ->orderBy("domain ASC,hits DESC")->all();
        //获取前10条
        $errors_top10 = $this->getTop10($errors_list);
        //前10条总数
        $errors_total = $this->getFieldTotal($errors_top10, 'hits');
        //组织字段
        foreach ($errors_top10 as $domain => $rows) {
            foreach ($rows as $row) {
                $item = [];
                $item['code'] = $row->code;
                $item['number'] = $row->hits;
                $item['percent'] = $errors_total[$domain] == 0 ? 0 : (round($row->hits / $errors_total[$domain], 2) * 100) . '%';
                $visit_data["errors_top10"][$domain][] = $item;
            }
        }

        //从搜索引擎进入我的网站-TOP10-------------------
        $visit_data["engine_top10"] = [];
        $engine_list = Searchref::find()
            ->andWhere(['>', 'pages', 0])
            ->andWhere(['year_monthed' => $end_year_month])
            ->orderBy("domain ASC,pages DESC")->all();
        //获取前10条
        $engine_top10 = $this->getTop10($engine_list);
        //前10条总数
        $engine_total = $this->getFieldTotal($engine_top10, 'pages');
        //组织字段
        foreach ($engine_top10 as $domain => $rows) {
            foreach ($rows as $row) {
                $item = [];
                $item['engine'] = $row->engine;
                $item['number'] = $row->pages;
                $item['percent'] = $engine_total[$domain] == 0 ? 0 : (round($row->pages / $engine_total[$domain], 2) * 100) . '%';
                $visit_data["engine_top10"][$domain][] = $item;
            }
        }

        //从别的网站进入我的网站-TOP10-------------------
        $visit_data["sites_top10"] = [];
        $sites_list = Pageref::find()
            ->andWhere(['>', 'pages', 0])
            ->andWhere(['year_monthed' => $end_year_month])
            ->orderBy("domain ASC,pages DESC")->all();
        //获取前10条
        $sites_top10 = $this->getTop10($sites_list);
        //前10条总数
        $sites_total = $this->getFieldTotal($sites_top10, 'pages');
        //组织字段
        foreach ($sites_top10 as $domain => $rows) {
            foreach ($rows as $row) {
                $item = [];
                $item['url'] = $row->url;
                $item['number'] = $row->pages;
                $item['percent'] = $sites_total[$domain] == 0 ? 0 : (round($row->pages / $sites_total[$domain], 2) * 100) . '%';
                $visit_data["sites_top10"][$domain][] = $item;
            }
        }

        //搜索关键字-TOP10-------------------
        $visit_data["keyword_top10"] = [];
        $keyword_list = SearchWords::find()
            ->andWhere(['>', 'hits', 0])
            ->andWhere(['year_monthed' => $end_year_month])
            ->orderBy("domain ASC,hits DESC")->all();
        //获取前10条
        $keyword_top10 = $this->getTop10($keyword_list);
        //前10条总数
        $keyword_total = $this->getFieldTotal($keyword_top10, 'hits');
        //组织字段
        foreach ($keyword_top10 as $domain => $rows) {
            foreach ($rows as $row) {
                $item = [];
                $item['word'] = $row->words;
                $item['number'] = $row->hits;
                $item['percent'] = $keyword_total[$domain] == 0 ? 0 : (round($row->hits / $keyword_total[$domain], 2) * 100) . '%';
                $visit_data["keyword_top10"][$domain][] = $item;
            }
        }

        //用户都用什么样的操作系统？-------------------
        $visit_data["operation_system_top10"] = [];
        $operation_system_list = Os::find()
            ->andWhere(['>', 'hits', 0])
            ->andWhere(['year_monthed' => $end_year_month])
            ->orderBy("domain ASC,hits DESC")->all();
        //获取前10条
        $operation_system_top10 = $this->getTop10($operation_system_list);
        //前10条总数
        $operation_system_total = $this->getFieldTotal($operation_system_top10, 'hits');
        //组织字段
        foreach ($operation_system_top10 as $domain => $rows) {
            foreach ($rows as $row) {
                $item = [];
                $item['name'] = $row->name;
                $item['number'] = $row->hits;
                $item['percent'] = $operation_system_total[$domain] == 0 ? 0 : (round($row->hits / $operation_system_total[$domain], 2) * 100) . '%';
                $visit_data["operation_system_top10"][$domain][] = $item;
            }
        }

        //用户都用什么样的浏览器？-------------------
        $visit_data["browser_top"] = [];
        $browser_list = Browser::findAll(['year_monthed' => $end_year_month]);
        $target_list = [];
        foreach ($browser_list as $row) {
            $target_list[$row->domain][] = $row;
        }
        //总数
        $browser_total = $this->getFieldTotal($target_list, 'hits');
        //组织字段
        foreach ($target_list as $domain => $rows) {
            foreach ($rows as $row) {
                $item = [];
                $item['name'] = $row->name;
                $item['number'] = $row->hits;
                $item['percent'] = $browser_total[$domain] == 0 ? 0 : (round($row->hits / $browser_total[$domain], 2) * 100) . '%';
                $visit_data["browser_top"][$domain][] = $item;
            }
        }

        //计算每个主机域名的数据----------------------------------------------
        $visit_data['domain_list'] = [];
        $visit_data['domain_name'] = '';
        $visit_data['list'] = [];
        if (sizeof($domain_year_month) == 0) {
            $general = new General();
            $general->domain = 'no_domain';
            $general->pages = 0;
            $general->pages_nv = 0;
            $domain_year_month[] = $general;
        }
        foreach ($domain_year_month as $row) {
            $visit_data['domain_list'][] = $row->domain;
            $visit_data['domain_name'] = $row->domain;
            $current_data = [];
            //安全统计分析
            $current_data['security_normal'] = $row->pages;
            $current_data['security_crawler'] = $row->pages_nv;
            $current_data['security_thread'] = isset($thread_visit[$row->domain]) ? $thread_visit[$row->domain] : 0;
            $current_data['security_total'] = $current_data['security_normal'] + $current_data['security_crawler'] + $current_data['security_thread'];
            //综合分析(按月)
            $current_data['combine_analysis_month'] = $year_domain[$row->domain];

            //综合分析(按天)
            $current_data['combine_analysis_day'] = isset($daily_day[$row->domain]) ? $daily_day[$row->domain] : [];

            //用户在您网站停留的时间
            $current_data['user_stay_time'] = isset($user_stay_list[$row->domain]) ? $user_stay_list[$row->domain] : [];

            //爬虫分析
            $current_data['robot_analysis'] = isset($robot_list[$row->domain]) ? $robot_list[$row->domain] : [];

            //网站流量(按天)
            $current_data['website_visit'] = isset($daily_day[$row->domain]) ? $daily_day[$row->domain] : [];

            //网络流量
            $current_data['network_flow'] = $network_flow;

            $visit_data['list'][$row->domain] = $current_data;
        }
        $visit_data['domain_host'] = current($visit_data['domain_list']);

        return $visit_data;
    }

    //获取前10条数据
    public function getTop10($source_list)
    {
        $target_list = [];
        foreach ( $source_list as $row )
        {
            if ( !isset($target_list[$row->domain]) )
            {
                $target_list[$row->domain][] = $row;
            }
            else
            {
                if ( sizeof($target_list[$row->domain]) < 10 )
                {
                    $target_list[$row->domain][] = $row;
                }
            }
        }
        return $target_list;
    }

    //计算指定字段的总数
    public function getFieldTotal($source_list, $field)
    {
        $target_total = [];
        foreach ($source_list as $domain => $rows) {
            foreach ($rows as $row) {
                $target_total[$domain] += $row->$field;
            }
        }
        return $target_total;
    }

    /**
     * 根据日期获取主机列表的查询条件
     * @param $start_date
     * @return string
     */
    public function getGeneralWhere($start_date)
    {
        // 201801
        $start_year_month = date_format(date_create($start_date), 'Ym');

        $whereStr = "year_monthed='{$start_year_month}'";

        return $whereStr;
    }
}