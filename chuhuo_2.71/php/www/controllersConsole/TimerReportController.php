<?php
namespace app\controllersConsole;

use app\logic\waf\report\ReportAttack;
use app\logic\waf\report\ReportVisit;
use app\models\CycleReport;
use Yii;
use yii\console\Controller;
use app\models\ReportManage;
use app\logic\waf\common\MySendMail;

/**
 * /Data/apps/wwwroot/waf/www/yii timer-report/do 执行的路径
 * /usr/local/bluedon/bdwafd/report_task.py   python自动执行脚本
 *
 * 定时报表
 * Class TimerReportController
 * @package console\controllers
 */
class TimerReportController extends Controller
{
    public function init()
    {
        parent::init();
        ignore_user_abort(TRUE);
        // TODO 注意如果数据过大， 内存限制就必须大一点，如主机内存为32G，可以限制为8G
        @ini_set("memory_limit", "8192M");
        Yii::$app->sysInit->init();
    }

    private function getT($key)
    {
        return Yii::$app->sysLanguage->getTranslateBySymbol($key);
    }

    /**
     * 执行定时任务
     * cycle: 1每天 2每周 3每月
     * @throws \Exception
     * @throws \yii\base\ExitException
     */
    public function actionDo()
    {
        $day = date('d');//当前天数
        $week = date('w');//星期几

        //每天报表 0点到4点执行 生成昨天数据
        $day_task = CycleReport::find()->where(['cycle' => 1])->asArray()->all();
        Yii::warning($day_task, "TimerReport_do_".__LINE__);
        if( count($day_task) > 0 )
        {
            $last_day = date("Y-m-d", strtotime("-1 day"));
            foreach ( $day_task as $task )
            {
                if( $task['type'] == 1 )
                {
                    $rst = $this->createAttackReport($last_day, $last_day, $task);
                    print_r($rst);
                }

                if( $task['type'] == 2 )
                {
                    // 访问流量报表只能统计整个月的数据
                    $start_day = date('Y-m-01');
                    Yii::warning([$start_day, $last_day, $task['format']], "TimerReport_do_".__LINE__);

                    $rst = $this->createVisitReport($start_day, $last_day, $task);

                    Yii::warning($rst, "TimerReport_do_".__LINE__);
                    print_r($rst);
                }

            }
        }

        //每周报表 星期一执行 生成上周数据
        $week_task = CycleReport::find()->where(['cycle' => 2])->groupBy('format')->asArray()->all();
        if ($week == 1 && count($week_task) > 0)
        {
            $last_monday = date("Y-m-d", strtotime("last Monday"));
            $last_sunday = date("Y-m-d", strtotime("last Sunday"));
            foreach ( $week_task as $task )
            {
                if( $task['type'] == 1 )
                {
                    $rst = $this->createAttackReport($last_monday, $last_sunday, $task);
                    print_r($rst);
                }

                if( $task['type'] == 2 )
                {
                    $rst = $this->createVisitReport($last_monday, $last_sunday, $task);
                    print_r($rst);
                }
            }
        }

        //每月报表 1号执行 生成上月数据
        $month_task = CycleReport::find()->where(['cycle' => 3])->groupBy('format')->asArray()->all();
        if ($day == '01' && count($month_task) > 0)
        {
            $last_month_start = date("Y-m-01", strtotime("last month"));
            $last_month_end = date('Y-m-t', strtotime($last_month_start));
            foreach ($month_task as $task)
            {
                if( $task['type'] == 1 )
                {
                    $rst = $this->createAttackReport($last_month_start, $last_month_end, $task);
                    print_r($rst);
                }

                if( $task['type'] == 2 )
                {
                    $rst = $this->createVisitReport($last_month_start, $last_month_end, $task);
                    print_r($rst);
                }
            }
        }

        echo 'do over'.date('Y-m-d H:i:s');
    }

    /**
     * 生成攻击报表
     * @param $start_date
     * @param $end_date
     * @param $task
     * @return array
     * @throws \Exception
     */
    public function createAttackReport($start_date, $end_date, $task)
    {

        $data = ['code'=> false, 'info'=> ''];

        if( !in_array($task['format'], ['html', 'doc', 'pdf']) )
        {
            $data['info'] = $this->getT('invalidParameter');
            return $data;
        }

        $reportAttack = new ReportAttack();

        //输出文件
        $report_real_path = Yii::$app->sysPath->wafReportPath['timerPath'];
        echo "timerPath:{$report_real_path}\r\n";
        if( !is_dir($report_real_path) )
        {
            if( mkdir($report_real_path, 0755, true)==FALSE )
            {
                $data['info'] = "Directory creation failure, {$report_real_path}";
                return $data;
            }
        }

        $file_name = "report_attack_{$start_date}_{$end_date}";
        $report_file = $report_real_path . $file_name;

        //下载地址
        $down_extensions_list = ['html' => '.zip', 'doc' => '.doc', 'pdf' => '.pdf'];
        $down_extensions = $down_extensions_list[$task['format']];

        //  /var/wafDownload/report/immediately/report_attack_201801_201801.zip
        $report_exist = $report_file . $down_extensions;
        //已存在报告，直接返回
        if( file_exists($report_exist) )
        {
            //上次创建时间，超过一小时，重新生成
            $last_modify = time() - filemtime($report_exist);
            if( $last_modify < 3600 )
            {
                $data['info'] = $this->getT('reportHasBeenGenerated');
                return $data;
            }
        }

        // /var/wafDownload/report/immediately/report_attack_201801_201801.html
        $report_create_file = $report_file . ($task['format'] == 'doc' ? '.doc' : '.html');
        Yii::warning($report_create_file, "TimerReport_createAttack_".__LINE__);
        //不存在，生成
        if( !is_file($report_create_file) )
        {
            $attack_data = $reportAttack->reportCalculate($start_date, $end_date);
            Yii::$app->setBasePath(Yii::getAlias("@app"));
            $render_page = $this->renderPartial('/report-attack/preview', $attack_data);

            if( file_put_contents($report_create_file, $render_page) == FALSE )
            {
                $data['info'] = $report_create_file.' '.$this->getT('writeFailure');
                return $data;
            }
        }

        if( $task['format'] == 'html' )
        {
            //打包
            $command = "cd {$report_real_path} && zip -r {$report_file}.zip {$file_name}.html plugins";
            Yii::warning($command, "TimerReport_createAttack_".__LINE__);
            echo "html zip command: {$command}\r\n";
            shell_exec($command);
        }

        if( $task['format'] == 'pdf' )
        {
            //html转pdf
            $command = "/Data/apps/wkhtmltox/bin/wkhtmltopdf {$report_create_file} {$report_file}.pdf";
            echo "html to pdf command: {$command}\r\n";
            shell_exec($command);
        }

        //保存数据库记录
        $report_data_exist = ReportManage::findOne(['path' => $file_name . $down_extensions, 'timeType' => 2]);
        if( !$report_data_exist )
        {
            $name = $start_date . $this->getT('to') . $end_date . $this->getT('reportAttack');
            $reportManage = new ReportManage();
            $reportManage->name = $name;
            $reportManage->type = 1;
            $reportManage->desc = $this->getT('reportAttack');
            $reportManage->time = time();
            $reportManage->path = $file_name . $down_extensions;
            $reportManage->timetype = 2;
            $reportManage->format = $task['format'];
            $reportManage->insert();
            Yii::warning($reportManage, "TimerReport_createAttack_".__LINE__);

            // 发送邮件
            if( $task['sendmail'] === 1 )
            {
                $id = $reportManage->attributes['id'];
                // 获取下载的路径
                $downLoadPath = $reportManage->getReportFile($id, true);
                $attachment =[];
                $attachment[] = $downLoadPath;
                $rst = $this->sendMail($name, $attachment);
                print_r($rst);
            }
        }

        $data['code'] = true;
        $data['info'] = $this->getT('reportHasBeenGenerated');
        return $data;
    }

    /**
     * 生成访问报表
     * @param string $start_date 2018-02-01
     * @param string $end_date 2018-02-08
     * @param $task
     * @return array
     * @throws \Exception
     * @throws \yii\base\ExitException
     */
    public function createVisitReport($start_date, $end_date, $task)
    {
        $data = ['code'=> false, 'info'=> ''];

        // 每天 每周 每月
        $cycleArr = [1=>$this->getT('everyDay'), 2=>$this->getT('everyWeekly'), 3=>$this->getT('everyMonth')];

        // 判断 文件格式 是否正确
        if( !in_array($task['format'], ['html', 'pdf']) )
        {
            $data['info'] = $this->getT('invalidParameter');
            return $data;
        }

        // 判断 目录 /var/wafDownload/report/timer/ 是否存在，不存在就创建
        $report_real_path = Yii::$app->sysPath->wafReportPath['timerPath'];
        if( !is_dir($report_real_path) )
        {
            if( mkdir($report_real_path, 0755, true)==FALSE )
            {
                $data['info'] = "Directory creation failure, {$report_real_path}";
                return $data;
            }
        }

        $date = "{$start_date}_{$end_date}";

        $report_web_down_file = "report_visit_cycle_{$task['cycle']}_{$task['format']}_{$date}".'.zip';

        Yii::warning($report_web_down_file, "TimerReport_createVisit_".__LINE__);

        $report_exist = $report_real_path . $report_web_down_file;

        //已存在报告，直接返回
        if( file_exists($report_exist) )
        {
            //上次创建时间，超过一小时，重新生成
            $last_modify = time() - filemtime($report_exist);
            if ($last_modify < 3600)
            {
                $data['info'] = $this->getT('reportHasBeenGenerated');
                return $data;
            }
        }

        //创建目录
        $directory_name = "report_visit_cycle_{$task['cycle']}_{$task['format']}_{$date}/";
        // /var/wafDownload/report/immediately/report_visit_html_2018-02-01_2018-02-08/,  这是按扩展名创建
        $report_directory = $report_real_path . $directory_name;
        if (!is_dir($report_directory)) mkdir($report_directory, 0755, true);

        Yii::warning($report_directory, "TimerReport_createVisit_".__LINE__);

        // /var/wafDownload/report/immediately/report_visit_html_20180201/  固定是html
        $html_directory = $report_real_path . "report_visit_cycle_{$task['cycle']}_html_{$date}/";
        if ( !is_dir($html_directory) )
        {
            if( mkdir($html_directory, 0755, true)==FALSE )
            {
                $data['info'] = "Directory creation failure, {$html_directory}";
                return $data;
            }
        }

        Yii::warning($html_directory, "TimerReport_createVisitReport_".__LINE__);

        //  设置基础目录 /Data/apps/wwwroot/waf/www
        Yii::$app->setBasePath(Yii::getAlias("@app"));

        // 生成文件
        $reportVisit = new ReportVisit();
        $visit_data = $reportVisit->reportCalculate($start_date, $end_date);

        //Yii::warning($visit_data, "TimerReport_createVisit_".__LINE__);

        //每个主机一个文件
        foreach ( $visit_data['list'] as $domain => $item )
        {
            $visit_data['domain_host'] = $domain;
            $visit_data['current_domain'] = $item;
            $current_render_page = $this->renderPartial('/report-visit-flow/preview', $visit_data);

            //生成html
            $current_html_file = $html_directory . 'visit-' . $domain . '.html';
            if( file_put_contents($current_html_file, $current_render_page) == FALSE )
            {
                $data['info'] = $current_html_file.' '.$this->getT('writeFailure');
                return $data;
            }

            //Yii::warning($current_html_file, "TimerReport_createVisit_".__LINE__);

            //html转pdf
            if ($task['format'] == 'pdf')
            {
                $current_pdf_file = $report_directory . 'visit-' . $domain . '.pdf';
                $command = "/Data/apps/wkhtmltox/bin/wkhtmltopdf {$current_html_file} {$current_pdf_file}";

                Yii::warning($command, "TimerReport_createVisit_".__LINE__);

                echo "html to pdf command: {$command}\r\n";
                shell_exec($command);
            }
        }

        //打包
        $include_plugin = $task['format'] == 'html' ? "plugins" : '';
        $command = "cd {$report_real_path} && zip -r {$report_web_down_file} {$directory_name} {$include_plugin}";

        Yii::warning($command, "TimerReport_createVisit_".__LINE__);

        echo "zip command: {$command}\r\n";
        shell_exec($command);

        //保存数据库记录
        $report_data_exist = ReportManage::findOne(['path' => $report_web_down_file, 'timeType' => 2]);
        if( !$report_data_exist )
        {
            $cycleStr = $task['cycle']==1?'':$cycleArr[$task['cycle']];
            $name = $start_date . $this->getT('to') . $end_date . $cycleStr.$this->getT('reportVisitFlow');
            $reportManage = new ReportManage();
            $reportManage->name = $name;
            $reportManage->type = 2;
            $reportManage->desc = $this->getT('reportVisitFlow');
            $reportManage->time = time();
            $reportManage->path = $report_web_down_file;
            $reportManage->timetype = 2;
            $reportManage->format = $task['format'];
            $reportManage->insert();

            Yii::warning($reportManage, "TimerReport_createVisit_".__LINE__);

            // 发送邮件
            if( $task['sendmail'] === 1 )
            {
                $id = $reportManage->attributes['id'];
                // 获取下载的路径
                $downLoadPath = $reportManage->getReportFile($id, true);
                $attachment =[];
                $attachment[] = $downLoadPath;
                $rst = $this->sendMail($name, $attachment);
                print_r($rst);
            }
        }

        $data['code'] = true;
        $data['info'] = $this->getT('reportHasBeenGenerated');
        return $data;
    }

    /**
     * @param $name
     * @param $attachment
     * @return array
     */
    private function sendMail($name, $attachment)
    {
        // 发送邮件
        $mail = new MySendMail;
        $rst = $mail->sendMail($name, $attachment);

        // 如果发送不成功保存日志
        if( $rst['code'] != true )
        {
            Yii::warning($rst, 'TimerReport_sendMail'.__LINE__);
        }

        return $rst;
    }
}