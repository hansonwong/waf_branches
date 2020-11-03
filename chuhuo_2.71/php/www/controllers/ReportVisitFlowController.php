<?php
namespace app\controllers;

use app\logic\BaseController;
use app\logic\waf\report\ReportVisit;
use app\modelLogs\General;
use app\models\ReportManage;
use Yii;

/**
 * 访问流量报表
 * Class ReportVisitFlowController
 * @package app\controllers
 */
class ReportVisitFlowController extends BaseController
{
    public $translate;

    public function init()
    {
        parent::init();
        ignore_user_abort(TRUE);
        @set_time_limit(3000);
        @ini_set("memory_limit", "1000M");
        $this->translate = Yii::$app->sysLanguage;
    }

    public function actionIndex()
    {
        $data = ['current_date' => date('Y-m')];
        return $this->render('index', $data);
    }

    /**
     * 报表预览/生成
     * 不支持报表日期到天数，只支持到月份, 如：2018-01
     * @throws \Exception
     * @throws \yii\base\ExitException
     * @throws \yii\base\InvalidConfigException
     */
    public function actionPreviewCreate()
    {
        //参数
        $params = Yii::$app->request->getBodyParams();

        // 报表日期开始时间   2018-02
        $reportDate = isset($params['reportDate']) ? $params['reportDate'] : '';
        // 报表 提交类型
        $action = $params['submitType'] ? $params['submitType'] : 'preview';

        // 判断报表类型
        $extension = $params['fileType'];
        if( !in_array($extension, ['html', 'pdf']) )
        {
            Yii::$app->response->format = 'json';
            $info = $this->translate->getTranslateBySymbol('invalidParameter');
            Yii::$app->response->data = ['code' => 'F', 'info' => $info];
            Yii::$app->end();
        }

        // 创建的目录名称 2018-02_(2018-02-08)   报表日期2018-02, 创建日期2018-02-08
        $date = $reportDate.'_['.date('Y-m-d').']';

        // 创建目录
        $directoryArr = [];
        // /var/wafDownload/report/immediately/
        $report_real_path = Yii::$app->sysPath->wafReportPath['immediatelyPath'];
        $directoryArr[] = $report_real_path;

        // /var/wafDownload/report/immediately/report_visit_html_2018-02_(2018-02-08)/
        $report_directory = "{$report_real_path}report_visit_html_{$date}/"; // 不管是生成pdf文件，先生成html,再转
        $directoryArr[] = $report_directory;
        Yii::$app->wafHelper->mkDir($directoryArr);

        $start_date = $reportDate.'-01';
        // 获取月份最后一天|当前时间
        $end_date = date('Y-m', strtotime($reportDate))==date('Y-m')?date('Y-m-d'):date('Y-m-t', strtotime($reportDate));

        //预览
        if( $action == 'preview' )
        {
           return $this->preview($start_date, $end_date, $params, $report_directory);
        }

        //创建
        if( $action == 'create' )
        {
            $this->create($start_date, $end_date, $params, $report_directory, $date);
        }
    }

    /**
     * 预览
     * 报表日期只支持年月，不支持日
     * @param string $start_date 2018-02-01
     * @param string $end_date 2018-02-28
     * @param $params
     * @param string $report_directory /var/wafDownload/report/immediately/report_visit_html_2018-01/
     *                                 /var/wafDownload/report/immediately/report_visit_html_2018-01_2018-02/
     * @return mixed
     * @throws \yii\base\ExitException
     */
    private function preview($start_date, $end_date, $params, $report_directory)
    {
        $reportVisit = new ReportVisit();
        // 报表日期
        $reportDate = date('Y-m', strtotime($start_date));

        // 根据日期获取主机列表的查询条件
        $whereStr= $reportVisit->getGeneralWhere($reportDate);
        //主机列表
        $domain_data = General::find()->where($whereStr)->distinct()->asArray()->all();
        $domain_list = array_column($domain_data, 'domain');
        unset($domain_data);

        //文件已存在，直接渲染
        $current_domain = isset($params['domain_name']) ? $params['domain_name'] : current($domain_list);
        $exist_report_file = $report_directory . 'visit-' . $current_domain . '.html';

        //上次创建时间，超过一小时，重新生成
        if( file_exists($exist_report_file) )
        {
            $last_modify = time() - filemtime($exist_report_file);
            // 判断有生成的文件，并且生成的时间少于3600秒， 就直接返回这个文件
            if( $last_modify < 3600 )
            {
                $render_page = $this->renderFile($exist_report_file);

                return $this->replacePageAsset($render_page);
            }
        }

        //生成
        $visit_data = $reportVisit->reportCalculate($start_date, $end_date);
        if( isset($params['report_desc']) )
        {
            $visit_data['desc'] = $params['report_desc'];
        }

        //每个主机一个文件
        $render_page = '';
        foreach ( $visit_data['list'] as $domain => $item )
        {
            $visit_data['domain_host'] = $domain;
            $visit_data['current_domain'] = $item;
            $visit_data['reportDate'] = $reportDate;

            $current_render_page = $this->renderPartial('preview', $visit_data);
            $report_file = "{$report_directory}visit-{$domain}.html";
            if( !$render_page )
            {
                $render_page = $current_render_page;
            }

            file_put_contents($report_file, $current_render_page);
        }

        return $this->replacePageAsset($render_page);
    }

    /**
     * 替换页面资源路径
     * @param $render_page string 页面内容
     * @return mixed
     */
    private function replacePageAsset($render_page)
    {
        $asset = Yii::$app->sysPath->resourcePath . "assets/waf/";
        $render_page = str_replace("../plugins/waf_report.css", $asset . "skin/blue/style/waf_report.css", $render_page);
        $render_page = str_replace("../plugins/jquery.min.js", $asset . "js/lib/jquery.min.js", $render_page);
        $render_page = str_replace("../plugins/echarts-all.js", $asset . "js/lib/echarts/echarts-all.js", $render_page);
        return $render_page;
    }

    /**
     * 创建
     * @param string $start_date 2018-02-01
     * @param string $end_date 2018-02-28
     * @param $params
     * @param string $report_directory /var/wafDownload/report/immediately/report_visit_html_2018-01/
     *                                 /var/wafDownload/report/immediately/report_visit_html_2018-01_2018-02/
     * @param string $date 2018-02_(2018-02-08)
     * @throws \Exception
     * @throws \yii\base\ExitException
     */
    private function create($start_date, $end_date, $params, $report_directory, $date)
    {
        // /var/wafDownload/report/immediately/
        $report_real_path = Yii::$app->sysPath->wafReportPath['immediatelyPath'];
        // /wafDownload/report/immediately/
        $report_web_path = Yii::$app->sysPath->wafReportPath['immediatelyPathDown'];

        $extension = strtolower(trim($params['fileType']));
        $report_web_down_file = "report_visit_{$extension}_{$date}.zip";
        $report_web_down_link = $report_web_path . $report_web_down_file;

        //zip已存在报告，直接返回
        $report_exist = $report_real_path . $report_web_down_file;
        if( file_exists($report_exist) )
        {
            //上次创建时间，超过一小时，重新生成
            $last_modify = time() - filemtime($report_exist);
            if( $last_modify < 3600 )
            {
                Yii::$app->response->format = 'json';
                Yii::$app->response->data = ['info' => $this->translate->getTranslateBySymbol('reportHasBeenGenerated'), 'file_path' => $report_web_down_link];
                Yii::$app->end();
            }
        }

        // report_visit_html_{$date}/"
        $directory_name = "report_visit_html_{$date}/";
        $report_pdf_directory = '';
        if( $extension=='pdf' )
        {
            $directory_name = "report_visit_pdf_{$date}/";
            $report_pdf_directory = $report_real_path . $directory_name;

            //如果是pdf类型，就创建目录
            $directoryArr = [];
            $directoryArr[] = $report_pdf_directory;
            Yii::$app->wafHelper->mkDir($directoryArr);
        }

        //生成文件
        $reportVisit = new ReportVisit();
        $visit_data = $reportVisit->reportCalculate($start_date, $end_date);
        if (isset($params['report_desc']))
        {
            $visit_data['desc'] = $params['report_desc'];
        }

        //每个主机一个文件
        foreach ( $visit_data['list'] as $domain => $item )
        {
            $visit_data['domain_host'] = $domain;
            $visit_data['current_domain'] = $item;
            $current_render_page = $this->renderPartial('preview', $visit_data);

            //生成html
            $current_html_file = "{$report_directory}visit-{$domain}.html";
            file_put_contents($current_html_file, $current_render_page);

            //html转pdf
            if( $extension == 'pdf' )
            {
                $current_pdf_file = "{$report_pdf_directory}visit-{$domain}.pdf";
                $command = "/Data/apps/wkhtmltox/bin/wkhtmltopdf {$current_html_file} {$current_pdf_file}";
                shell_exec($command);
            }
        }

        //打包
        $include_plugin = "plugins/";
        if( $extension == 'pdf' )
        {
            $include_plugin = '';

        }

        $command = "cd {$report_real_path} && zip -r {$report_web_down_file} {$directory_name} {$include_plugin}";
        shell_exec($command);

        //保存数据库记录
        $report_data_exist = ReportManage::findOne(['path' => $report_web_down_file]);
        if( !$report_data_exist )
        {
            $reportManage = new ReportManage();
            $reportManage->name = $start_date . $this->translate->getTranslateBySymbol('to') . $end_date . $this->translate->getTranslateBySymbol('reportVisitFlow');
            $reportManage->type = 2;
            $reportManage->desc = isset($visit_data['desc']) ? $visit_data['desc'] : $this->translate->getTranslateBySymbol('reportVisitFlow');
            $reportManage->time = time();
            $reportManage->path = $report_web_down_file;
            $reportManage->timetype = 1;
            $reportManage->format = $extension;
            $reportManage->insert();
        }

        Yii::$app->response->format = 'json';
        Yii::$app->response->data = ['info' => $this->translate->getTranslateBySymbol('reportHasBeenGenerated'), 'file_path' => $report_web_down_link];
        Yii::$app->end();
    }
}
