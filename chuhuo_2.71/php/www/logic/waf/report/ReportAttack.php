<?php
namespace app\logic\waf\report;

use app\modelFirewall\TbNetPort;
use app\modelLogs\AlertLogs;
use app\logic\waf\helpers\WafModels;
use app\modelLogs\WeboutLogs;
use app\models\BaseAccessCtrl;
use app\models\RulesCustom;
use app\models\Devinfo;
use app\models\RuleCat;
use app\models\Rules;
use function GuzzleHttp\Psr7\str;
use Yii;

class ReportAttack
{

    private $translate;

    public function __construct()
    {
        $this->translate = Yii::$app->sysLanguage;
    }

    /**
     * 报表计算
     * @param string $start_date 开始日期
     * @param string $end_date 结束日期
     * @return array
     * @throws \yii\base\ExitException
     */
    public function reportCalculate($start_date = '', $end_date = '')
    {
        //参数验证
        if ( empty(trim($start_date)) || empty(trim($end_date)) )
        {
            Yii::$app->response->format = 'json';
            Yii::$app->response->data = ['code' => 'F', 'info' => $this->translate->getTranslateBySymbol('selectTheQueryDate')];
            Yii::$app->end();
        }

        //日期格式化
        $start_date = date_create(trim($start_date));
        $start_date = date_format($start_date, 'Y-m-d');
        $end_date = date_create(trim($end_date));
        $end_date = date_format($end_date, 'Y-m-d');

        $attack_data = [];
        //报表概要信息
        $attack_data['data_section'] = $start_date . $this->translate->getTranslateBySymbol('to') . $end_date;
        $attack_data['create_time'] = date('Y-m-d H:i:s');
        $attack_data['device_model'] = Devinfo::find()->one()->getAttribute('model');
        $attack_data['device_ip'] = TbNetPort::findOne(['sPortName' => 'enp8s0'])->sIPV4Address;
        $attack_data['desc'] = $this->translate->getTranslateBySymbol('reportAttack');

        //攻击类型
        $attack_type_list = $this->getAttackType();

        //所有规则
        $all_rules = $this->getAllRules($attack_type_list);

        //表数据量较大，避免重复查询影响效率，先查出该时间段的攻击日志
        $start_dt = date('Y-m-d 00:00:00', strtotime($start_date));
        $end_dt = date('Y-m-d 00:00:00', strtotime("+1 day", strtotime($end_date)));
        $alert_logs_list = AlertLogs::find()
            ->select('LogDateTime,SourceIP,Url,Host,RuleID,AttackType,Severity')
            ->where(['between', "LogDateTime", $start_dt, $end_dt])
            ->orderBy('LogDateTime ASC')->asArray()->all();

        //组织数据
        $alert_logs = ['days' => [], 'hours' => [], 'debug' => [],
            'info' => [], 'notice' => [], 'warning' => [], 'error' => [],
            'critical' => [], 'alert' => [], 'emergency' => [], 'rule_type' => []];

        foreach ($alert_logs_list as &$log)
        {
            if ( strlen($log['AttackType'])<1 ) continue;

            $log['rule_type_desc'] = $attack_type_list[$log['AttackType']]['desc'];

            $log_date = date("Y-m-d", strtotime($log['LogDateTime']));
            $alert_logs['days'][$log_date][] = $log;    //按日期分组

            $log_hour = date("H", strtotime($log['LogDateTime']));
            $alert_logs['hours'][$log_hour][] = $log;    //按小时分组

            $alert_logs[strtolower($log['Severity'])][] = $log;    //按安全级别分

            $alert_logs['rule_type'][$log['AttackType']][] = $log;    //按类型分组

            $alert_logs[$log['AttackType']]['ip'][$log['SourceIP']][] = $log;    //按类型-IP分组
            $alert_logs[$log['AttackType']]['host'][$log['Host']][] = $log;    //按类型-Host分组
            $alert_logs[$log['AttackType']]['url'][$log['Url']][] = $log;    //按类型-Url分组

            $alert_logs[$log['SourceIP']][$log['AttackType']][] = $log;    //按IP-类型分组
            $alert_logs[$log['Host']][$log['AttackType']][] = $log;    //按Host-类型分组
            $alert_logs[$log['Url']][$log['AttackType']][] = $log;    //按Url-类型分组
        }

        //入侵数量统计---------------------
        $attack_num_total = sizeof($alert_logs_list);  //攻击总数
        $attack_data['attack_num_total'] = $attack_num_total;
        unset($alert_logs_list);

        //安全级别
        $attack_data['attack_num_level'] = [
            'tips' => array_sum([sizeof($alert_logs['debug']), sizeof($alert_logs['info']), sizeof($alert_logs['notice'])]),
            'warning' => sizeof($alert_logs['warning']), 'error' => sizeof($alert_logs['error']),
            'critical' => sizeof($alert_logs['critical']), 'alert' => sizeof($alert_logs['alert']),
            'emergency' => sizeof($alert_logs['emergency']),
        ];

        //入侵趋势---------------------
        $attack_data['attack_date_trend'] = [];
        $attack_data['attack_date_trend_list'] = [];
        foreach ($alert_logs['days'] as $date => $logs) {
            $attack_data['attack_date_trend'][] = sizeof($logs);
            $trend_item = [];
            //事件次数
            $trend_item['alert_count'] = sizeof($logs);
            //百分百
            $percent = $attack_num_total == 0 ? 0 : round(sizeof($logs) / $attack_num_total * 100, 2);
            $trend_item['alert_percent'] = $percent . '%';
            //日期
            $trend_item['alert_date'] = $date;

            //描述
            $trend_item['alert_desc'] = '';
            $item_list = [];
            foreach ($logs as $log)
            {
                $item_list[$log['AttackType']]['num'] += 1;
                $item_list[$log['AttackType']]['desc'] = $log['rule_type_desc'];
            }

            if (sizeof($item_list) > 0)
            {
                foreach ($item_list as $id => $item)
                {
                    // 如果没有攻击类型直接用英文的
                    $desc = strlen($item['desc'])<1?$id:$item['desc'];
                    $trend_item['alert_desc'] .= $desc . '(' . $item['num'] . ')';
                }
            }

            $attack_data['attack_date_trend_list'][] = $trend_item;
        }

        //入侵趋势图(24小时时间段)---------------------
        for ($h = 0; $h < 24; $h++) {
            $hour_trend_item = [];
            $h = date(str_pad($h, 2, "0", STR_PAD_LEFT));
            //时间段
            $end_hour = ($h + 1) >= 24 ? 0 : $h + 1;
            $end_hour = date(str_pad($end_hour, 2, "0", STR_PAD_LEFT));
            $hour_range = $h . ':00-' . $end_hour . ':00';
            $hour_trend_item['alert_time'] = $hour_range;
            //事件次数
            $hour_trend_count = isset($alert_logs['hours'][$h]) ? sizeof($alert_logs['hours'][$h]) : 0;
            $attack_data['attack_hour_trend'][$hour_range] = $hour_trend_count;
            $hour_trend_item['alert_count'] = $hour_trend_count;
            //百分百
            $percent = $attack_num_total == 0 ? 0 : round($hour_trend_count / $attack_num_total * 100, 2);
            $hour_trend_item['alert_percent'] = $percent . '%';

            //描述
            $hour_trend_item['alert_desc'] = '';
            $item_list = [];
            $alert_current_logs = isset($alert_logs['hours'][$h]) ? $alert_logs['hours'][$h] : [];
            foreach ($alert_current_logs as $log) {
                $item_list[$log['AttackType']]['num'] += 1;
                $item_list[$log['AttackType']]['desc'] = $log['rule_type_desc'];
            }
            if (sizeof($item_list) > 0) {
                foreach ($item_list as $id => $item) {
                    // 如果没有攻击类型直接用英文的
                    $desc = strlen($item['desc'])<1?$id:$item['desc'];
                    $hour_trend_item['alert_desc'] .= $desc . '(' . $item['num'] . ')';
                }
            }

            $attack_data['attack_hour_trend_list'][] = $hour_trend_item;
        }

        //入侵类别统计,入侵类别对比---------------------
        $attack_data['attack_list_type'] = [];
        foreach ($attack_type_list as $type) {
            $item_type = ['name' => $type['name'], 'attack_type_count' => 0, 'desc' => $type['desc']];
            $item_type['attack_type_count'] = isset($alert_logs['rule_type'][$type['name']]) ? sizeof($alert_logs['rule_type'][$type['name']]) : 0;
            $percent = $attack_num_total == 0 ? 0 : number_format($item_type['attack_type_count'] / $attack_num_total, 4) * 100;
            $item_type['attack_type_percent'] = $percent;
            $attack_data['attack_list_type'][] = $item_type;
        }

        //分别计算按IP、Host、Url来统计的结果---------------------
        $attack_section = ['ip' => 'SourceIP', 'host' => 'Host', 'url' => 'Url'];
        foreach ($attack_section as $key => $section) {
            //攻击类型按被攻击的section统计
            $attack_data["attack_type_{$key}"] = [];
            foreach ($attack_type_list as $type) {
                //总数
                $attack_current_type_total = isset($alert_logs['rule_type'][$type['name']]) ? sizeof($alert_logs['rule_type'][$type['name']]) : 0;
                if ($attack_current_type_total == 0) continue;
                //每个section的数量
                $attack_current_section = $alert_logs[$type['name']][$key];

                $attack_data["attack_type_{$key}"][$type['name']]['total'] = $attack_current_type_total;
                $attack_data["attack_type_{$key}"][$type['name']]['desc'] = $type['desc'];
                $attack_data["attack_type_{$key}"][$type['name']]['list'] = [];
                foreach ($attack_current_section as $name => $attack) {
                    $item_attack_ip = [];
                    $item_attack_ip["attack_{$key}"] = $name;
                    $item_attack_ip["attack_count"] = sizeof($attack);
                    $percent = $attack_current_type_total == 0 ? 0 : round(sizeof($attack) / $attack_current_type_total * 100, 2);
                    $item_attack_ip['attack_percent'] = $percent . '%';
                    $attack_data["attack_type_{$key}"][$type['name']]['list'][] = $item_attack_ip;
                }
            }

            //被攻击的section按攻击类型统计TOP50
            $attack_type_top50 = AlertLogs::find()->select("{$section},COUNT(*) AS total")
                ->where(['between', "LogDateTime", $start_dt, $end_dt])
                ->groupBy($section)->orderBy('total DESC')
                ->limit(50)->asArray()->all();
            $attack_data["attack_type_{$key}_top50"] = [];
            foreach ($attack_type_top50 as $attack) {
                $item_list = [];
                $item_list[$key] = $attack[$section];
                $item_list['total'] = $attack['total'];
                $item_list['list'] = [];
                //每个section下每种类型攻击的数量
                foreach ($attack_type_list as $type) {
                    $item = [];
                    $item['desc'] = $type['desc'];
                    $item_count = sizeof($alert_logs[$attack[$section]][$type['name']]);
                    if ($item_count == 0) continue;
                    $item['attack_count'] = $item_count;
                    $percent = $attack['total'] == 0 ? 0 : round(intval($item_count) / $attack['total'] * 100, 2);
                    $item['attack_percent'] = $percent . '%';
                    $item_list['list'][] = $item;
                }
                $attack_data["attack_type_{$key}_top50"][] = $item_list;
            }
        }

        //入侵类来源地址统计 TOP50---------------------
        $attack_ip_top50 = AlertLogs::find()
            ->select('*,COUNT(*) as total')
            ->where(['between', "LogDateTime", $start_dt, $end_dt])
            ->groupBy('SourceIP')->orderBy('total DESC')->limit(50)
            ->asArray()->all();

        $attack_data['attack_source_ip_top50'] = [];
        foreach ($attack_ip_top50 as $source) {
            $item = [];
            $item['attack_source_count'] = $source['total'];
            $item['attack_source_ip'] = $source['SourceIP'];
            $item['attack_source_location'] = WafModels::getCountry($source['CountryCode'], $source['RegionCode'], $source['City']);
            $attack_data['attack_source_ip_top50'][] = $item;
        }

        //被攻击主机统计TOP50---------------------
        $attack_data['attack_host_top50'] = AlertLogs::find()
            ->select('Host AS attack_host,COUNT(*) as total')
            ->where(['between', "LogDateTime", $start_dt, $end_dt])
            ->groupBy('Host')->orderBy('total DESC')->limit(50)
            ->asArray()->all();

        //被攻击URL统计TOP50 Host+Uri---------------------
        $attack_data['attack_host_url_top50'] = AlertLogs::find()
            ->select('Host AS attack_host,Uri AS attack_url,COUNT(*) as total')
            ->where(['between', "LogDateTime", $start_dt, $end_dt])
            ->groupBy('Host,Uri')->orderBy('total DESC')->limit(50)
            ->asArray()->all();

        //被攻击URL统计(含参数)TOP50 Host+Uri+QueryString---------------------
        $attack_data['attack_host_url_query_top50'] = AlertLogs::find()
            ->select('Host AS attack_host,Uri AS attack_url,QueryString AS attack_query,COUNT(*) as total')
            ->where(['between', "LogDateTime", $start_dt, $end_dt])
            ->groupBy('Host,Uri,QueryString')->orderBy('total DESC')->limit(50)
            ->asArray()->all();

        //非法外联TOP50---------------------
        $date_between = ['between', 'dt', $start_date, $end_date];
        $attack_out_links = WeboutLogs::find()
            ->select('*,COUNT(*) as total')
            ->where($date_between)
            ->groupBy('sip,dip')->orderBy('total DESC')->limit(50)
            ->asArray()->all();
        $attack_data['attack_out_links'] = [];
        foreach ($attack_out_links as $attack) {
            $item = [];
            $item['total'] = $attack['total'];
            $item['source_ip'] = $attack['sip'];
            $item['destination_ip'] = $attack['dip'];
            $item['location'] = WafModels::getCountry($attack['CountryCode'], $attack['RegionCode'], $attack['City']);
            $attack_data['attack_out_links'][] = $item;
        }

        return $attack_data;
    }

    /**
     * @return array|\yii\db\ActiveRecord[]
     * [
    'ACCESSCTRL' => ['id' => 9, 'name' => 'ACCESSCTRL', 'desc' => '访问控制'],
    'CC' => ['id' => 10, 'name' => 'CC', 'desc' => 'CC攻击'],
    'CUSTOM' => ['id' => 14, 'name' => 'CUSTOM', 'desc' => '自定义'],
    'GENERIC' => ['id' => 3, 'name' => 'GENERIC', 'desc' => '通用攻击'],
    'LEAKAGE' => ['id' => 6, 'name' => 'LEAKAGE', 'desc' => '信息泄漏'],
    'OTHER' => ['id' => 7, 'name' => 'OTHER',  'desc' => '其他攻击'],
    'OVERFLOW' => ['id' => 8, 'name' => 'OVERFLOW', 'desc' => '溢出攻击'],
    'PROTOCOL' => ['id' => 4, 'name' => 'PROTOCOL', 'desc' => 'HTTP保护'],
    'SQLI' => ['id' => 1, 'name' => 'SQLI',  'desc' => 'SQL注入'],
    'TROJANS' => ['id' => 5, 'name' => 'TROJANS', 'desc' => '木马病毒'],
    'XSS' => ['id' => 2, 'name' => 'XSS', 'desc' => '跨站脚本'],
    'B&W' => ['id' => 9, 'name' => 'ACCESSCTRL', 'desc' => '访问控制']
    ]
     */
    public function getAttackType()
    {
        //攻击类型
        $attack_type_list = RuleCat::find()->indexBy('name')->asArray()->all();
        foreach ( $attack_type_list as $key=>$type )
        {
            $attack_type_list[$key]['desc'] = Yii::$app->sysLanguage->getTranslate($type['desc']);
        }

        // B&W是属于访问控制类型
        $attack_type_list['B&W'] =  $attack_type_list['ACCESSCTRL'];

        return $attack_type_list;
    }

    /**
     * @param $attack_type_list
     * @return array|\yii\db\ActiveRecord[]
     * Array
        ([301200] => Array(
            [realid] => 301200
            [type] => OVERFLOW
            [desc] => 溢出攻击
        )
        [301201] => Array(
            [realid] => 301201
            [type] => OVERFLOW
            [desc] => 溢出攻击
        )
     */
    public function getAllRules($attack_type_list)
    {
        $all_rules = Rules::find()->select(['realid', 'type'])
            ->union(RulesCustom::find()->select(['realid', 'type']))
            ->union(BaseAccessCtrl::find()->select(['realid', 'type']))
            ->indexBy('realid')
            ->asArray()->all();
        //附加规则类型名称
        foreach ($all_rules as &$rule)
        {
            $rule['desc'] = isset($attack_type_list[$rule['type']]) ? $attack_type_list[$rule['type']]['desc'] : '';
        }

        return $all_rules;
    }

    //获取当月的最大天数
    public function getLastDay($year, $month)
    {
        switch ($month) {
            case 4 :
            case 6 :
            case 9 :
            case 11 :
                $days = 30;
                break;
            case 2 :
                if ($year % 4 == 0) {
                    if ($year % 100 == 0) {
                        $days = $year % 400 == 0 ? 29 : 28;
                    } else {
                        $days = 29;
                    }
                } else {
                    $days = 28;
                }
                break;

            default :
                $days = 31;
                break;
        }
        return $days;
    }
}