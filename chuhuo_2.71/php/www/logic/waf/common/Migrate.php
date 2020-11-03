<?php

namespace app\logic\waf\common;

use Yii;
use app\models\Devinfo;
use yii\data\Pagination;
use yii\helpers\ArrayHelper;
/**
 * 系统升级
 * Class UpgradeLogs
 * @package app\logic\waf\common
 */
class Migrate extends \app\models\Migrate
{
    // 动作: migrate升级,rollback回退
    private static $aAction;

    //TODO 恢复的执行脚本 暂时未用到 无此脚本
    private static $backup_file = '/home/bluedon/restore_system.sh';

    //升级的进度条
    private static $updateSysStatus = '/tmp/updateSysStatus.json';

    //这个是python执行完shell后的状态
    private static $updateShellStatus = '/tmp/updateShellStatus.json';

    //恢复的进度条
    private static $returnSysStatus = '/tmp/returnSysStatus.json';

    // 将文件名和密码保存到tmp目录下
    private static $updateSystemData = "/tmp/updateSystemData";

    //系统恢复密码
    private static $sReturnPass = 'bluedon';

    // 是否写日志开关， true记录日志， false不记录日志
    private static $log = true;

    /*
     * 记录版本信息
     * /etc/waf_version/waf_version.conf
    bdwaf                svn-Rev2258
    bluedon(PYTHON)      svn-Rev2405
    ng_platfrom          svn-Rev2331
    nginx_src            svn-Rev2252
    PHP                  svn-Rev2401
    */
    private static $wafVersion = '/etc/waf_version/waf_version.conf';

    /**
     * 写入日志数据
     * @param $data
     * @return bool|int
     */
    public static function writeLog($data)
    {
        if( self::$log===false ) return true;

        $sLogFile = "/Data/apps/wwwroot/waf/cache/update_system.log";

        file_put_contents($sLogFile, "\r\n", FILE_APPEND);

        return file_put_contents($sLogFile, var_export($data,TRUE), FILE_APPEND);
    }

    /**
     * 升级记录头部
     * @return string
     */
    public static function getUpdateHeaderTitle()
    {
        $aData = [
            ['sTitle' => 'id','data' => 'id','bVisible' => false ],
            ['sTitle' => Yii::$app->sysLanguage->getTranslateBySymbol("versionNumber"),'data' => 'sVersionNum'], // 版本号
            ['sTitle' => Yii::$app->sysLanguage->getTranslateBySymbol("executionAction"),'data' => 'sAction','sClass'=>'sAction'], //动作
            ['sTitle' => Yii::$app->sysLanguage->getTranslateBySymbol("description"),'data' => 'sDesc'], //描述
            ['sTitle' => Yii::$app->sysLanguage->getTranslateBySymbol("time"),'data' => 'sTime'], //时间
        ];
        return json_encode($aData);
    }

    /**
     * 升级记录数据
     * @return string
     */
    public static function getUpdateLog()
    {
        // 排序
        $sortName = Yii::$app->request->post('sortname','id');
        $sortOrder = Yii::$app->request->post('sortorder','DESC');
        $orderBy = "{$sortName} {$sortOrder}";

        // 处理页面数问题
        $pagination = self::getPagination();

        // 用于国际会处理中文
        self::$aAction = [
            'migrate' => Yii::$app->sysLanguage->getTranslateBySymbol("upgrade"),  //upgrade 升级
            'rollback' => '回退',  //回退
        ];

        $list = [];
        // 查询字段
        $select = "*";
        $model =  self::find()->where("iStatus=2")->select($select)->orderBy($orderBy)->offset($pagination->offset)->limit($pagination->limit)->asArray()->all();
        foreach( $model as $v )
        {
            // 整理输出数据
            $list[] = [
                "id" => $v['id'],
                "sVersionNum" => $v['sVersionNum'],
                "sAction" => self::$aAction[$v['sAction']],
                "sDesc" => $v['sDesc'],
                "sTime" => $v['sTime'],
            ];
        }

        $aData = [
            'data' => $list,
            'total' => $pagination->totalCount,
            'page' => $pagination->offset+1,
            'pagesize' => $pagination->pageSize,
        ];

        return json_encode($aData);
    }

    /**
     * 升级系统
     * @throws \yii\base\ExitException
     */
    public static function UpdateSys()
    {
        set_time_limit(0);

        $aData = ['code'=>'F', 'info'=>'', 'pre_name'=>''];

        $aPost = (array)Yii::$app->wafHelper->getParam();

        // 验证密码
        $sPass = Yii::$app->wafHelper->authcode($aPost['sPass'], 'DECODE', 'bluedon_edu');

        // 获取预设上传的目录  /var/wafDownload/migrate/up/
        $sUpPath = ArrayHelper::getValue(Yii::$app->sysPath->systemUpgradePath, 'realPath.up');

        // 移植防火墙版本过来，上传的key不一样
        $_FILES['file'] = $_FILES['recovery_file'];
        // 使用回上传的文件
        $fileName = $_FILES['file']['name'];
        $sFile = $sUpPath.'/'.$fileName;

        // 上传文件处理  VPN_PHP7977_SQL3914_PY3920_FROM_PHP6080_SQL2926_PY3045.tar.gz
        $rst =Yii::$app->wafHelper->upFile($sFile, ['gz'], 100);
        self::writeLog([__line__."--up file result", $rst]);
        if( $rst['code'] != 'T' )
        {
            $aData['info'] = $rst['info'];
            echo json_encode($aData);
            Yii::$app->end();
        }

        // VPN_PHP7977_SQL3914_PY3920_FROM_PHP6080_SQL2926_PY3045
        $pre_name  = substr($fileName,0,strlen($fileName)-7);
        //将文件名和密码保存到tmp目录下 /tmp/updateSystemData
        $rst = file_put_contents(self::$updateSystemData,json_encode(array('sPass'=>$sPass,'pre_name'=>$pre_name)));
        self::writeLog([__line__."--将文件名和密码保存到tmp目录下 /tmp/updateSystemData", $rst]);

        //解压文件
        $sShell = "/usr/bin/sudo /usr/bin/tar -zxf"." ".$sFile." -C /tmp";
        exec($sShell,$mdata, $return_var);
        self::writeLog([__line__."--tar files result", $sShell, $return_var]);

        //创建进度文件 将进度文件置空
        //  '/tmp/updateSysStatus.json';
        $sShell = "/usr/bin/sudo /usr/bin/touch ".self::$updateSysStatus;
        exec($sShell,$mdata, $return_var);
        self::writeLog([__line__."--create file, and empty files result", $sShell, $return_var]);

        // 修改文件权限
        $sShell = "/usr/bin/sudo /usr/bin/chmod -R 777 ".self::$updateSysStatus;
        exec($sShell,$mdata, $return_var);
        self::writeLog([__line__."--chmod files result", $sShell, $return_var]);

        // /tmp/updateSysStatus.json 写入state为0
        $rst = self::editStatus(0, 'migrate');
        self::writeLog([__line__."--UpdateSys write file state =0", $rst]);

        if( $rst===false )
        {
            $aData['info'] = '初始化升级数据失败';
            echo json_encode($aData);

            self::writeLog([__line__."--升级系统UpdateSys", $aData]);
            Yii::$app->end();
        }

        $aData['code'] = 'T';
        $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("uploadSuccessfully"); // 上传成功
        $aData['pre_name'] = $pre_name;
        echo json_encode($aData);
        Yii::$app->end();
    }

    /**
     * 执行升级脚本
     * @throws \yii\base\ExitException
     */
    public static function executeUpdate()
    {
        $aData = ['code'=>'F', 'info'=>'', 'pre_name'=>''];

        //  "/tmp/updateSystemData";
        if( !file_exists(self::$updateSystemData) )
        {
            $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("fileDoesNotExist"); //'文件不存在';
            echo json_encode($aData);

            self::writeLog([__line__."--执行升级脚本executeUpdate", $aData]);
            Yii::$app->end();
        }

        $updateSystemData = json_decode(file_get_contents(self::$updateSystemData),true);
        $pre_name = $updateSystemData['pre_name'];
        $sPass = $updateSystemData['sPass'];

        //执行升级脚本 /usr/bin/sudo /usr/bin/sh /tmp/WAF_PHP2481_SQL2470_PY2477_FROM_PHP2480_SQL2469_PY2476/update_wizard.sh packdir=/tmp/WAF_PHP2481_SQL2470_PY2477_FROM_PHP2480_SQL2469_PY2476
        $sShell = "echo '".$sPass."'| /usr/bin/sudo /usr/bin/sh ".'/tmp/'.$pre_name.'/update_wizard.sh '.'packdir=/tmp/'.$pre_name ;
        //exec($sShell,$mdata, $return_var);

        pclose(popen($sShell.' > /dev/null &', 'r'));

        self::writeLog([__line__."--执行 update_wizard.sh", $sShell]);

        $aData['code'] = 'T';
        $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("success"); //'成功';
        echo json_encode($aData);
        Yii::$app->end();
    }

    /**
     * 升级 进度条
     * @param object $c 传控制器
     * @return mixed
     */
    public static function Loading($c)
    {
        $aPost  = (array)Yii::$app->wafHelper->getParam();

        $viewData = [];
        if( !empty($aPost['pre_name']))
        {
            $viewData['pre_name']   = $aPost['pre_name'];
        }

        return $c->render('maintenance_loading',$viewData);
    }

    /**
     * 获取系统升级时,升级的进度
     * @throws \yii\base\ExitException
     */
    public static function getUpdateSysStatus()
    {
        $aData = ['code'=>'F', 'info'=>'', 'pre_name'=>''];

        $aPost  = (array)Yii::$app->wafHelper->getParam();
        if( empty($aPost['pre_name']) )
        {
            $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("parameterError"); //'参数错误';
            echo json_encode($aData);

            self::writeLog([__line__."--获取系统升级getUpdateSysStatus", $aData]);
            Yii::$app->end();
        }

        // "/tmp/updateSysStatus.json";
        if( !file_exists(self::$updateSysStatus) )
        {
            $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("fileDoesNotExist"); //'文件不存在';
            echo json_encode($aData);

            self::writeLog([__line__."--获取系统升级getUpdateSysStatus", $aData]);
            Yii::$app->end();
        }

        // 数据为{"state": "1"} 0代表5% 1代表25%  2代表50%  3代表75%   4代表100%
        $result = json_decode(file_get_contents(self::$updateSysStatus),true);
        if( empty($result) )
        {
            $aData['info'] = '数据为空';
            echo json_encode($aData);

            self::writeLog([__line__."--获取系统升级getUpdateSysStatus", $aData]);
            Yii::$app->end();
        }
        $aData['state'] = $result['state'];

        //判断是否存在已经升级结束的文件
        $fUpdate_status = "/tmp/".$aPost['pre_name'].'/update_status';
        if( !file_exists($fUpdate_status) && intval($result['state'])<1 )
        {
            $aData['info'] = '升级文件错误';
            echo json_encode($aData);

            self::writeLog([__line__."--获取系统升级getUpdateSysStatus", $aData]);
            Yii::$app->end();
        }

        $status = 'update_in_progress';
        if( file_exists($fUpdate_status) )
        {
            $status = trim(file_get_contents($fUpdate_status));
            if( empty($status) && $result['state']<1  )
            {
                $aData['info'] = '升级状态错误';
                echo json_encode($aData);

                self::writeLog([__line__."--获取系统升级getUpdateSysStatus", $aData]);
                Yii::$app->end();
            }
        }

        if( $status=='success' && intval($result['state'])===4 )
        {
            $aData['complete'] = true;

            // 删除 runtime目录
            $sShell = "/usr/bin/sudo /usr/bin/rm -rf /Data/apps/wwwroot/waf/cache/runtime/";
            exec($sShell,$mdata, $return_var);
            self::writeLog([__line__."--删除runtime目录", $return_var]);
        }
        else
        {
            $status = self::getTips($status);
            $aData['complete'] = $status;
        }

        $aData['code'] = 'T';
        $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("success");//''成功';
        echo json_encode($aData);

        Yii::$app->end();
    }

    /**
     * 系统还原
     * @throws \yii\base\ExitException
     * @throws \yii\db\Exception
     */
    public static function returnSystem()
    {
        $aData = ['code'=>'F', 'info'=>''];

        $aPost  = (array)Yii::$app->wafHelper->getParam();

        // 验证密码
        $sPass = Yii::$app->wafHelper->authcode($aPost['sPass'], 'DECODE', 'bluedon_edu');

        //判断还原密码是否正确
        if( $sPass !== self::$sReturnPass )
        {
            $aData['info'] = '密码输入错误';
            echo json_encode($aData);

            self::writeLog([__line__."--系统还原returnSystem", $aData]);
            Yii::$app->end();
        }

        //判断是否允许还原
        if( empty(Yii::$app->db->createCommand("SHOW TABLES LIKE 't_migrate'")->queryAll()) )
        {
            $aData['info'] = '用户并未执行系统升级，不能进行还原操作';
            echo json_encode($aData);

            self::writeLog([__line__."--系统还原returnSystem", $aData]);
            Yii::$app->end();
        }

        $sSql = "SELECT COUNT(*) AS total FROM `t_migrate`;";
        $count = Yii::$app->db->createCommand($sSql)->queryAll();
        if( intval($count[0]['total'])<1 )
        {
            $aData['info'] = '没有上一版本系统还原数据';
            echo json_encode($aData);

            self::writeLog([__line__."--系统还原returnSystem", $aData]);
            Yii::$app->end();
        }

        $aData['code'] = 'T';
        $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("success");//''成功';
        echo json_encode($aData);
        Yii::$app->end();
    }

    /**
     * 执行还原
     * @throws \yii\base\ExitException
     * @throws \yii\db\Exception
     */
    public static function executeReturn()
    {
        $aData = ['code'=>'F', 'info'=>''];

        if( self::checkTableExist('t_migrate_yii')===false )
        {
            $aData['info'] = '未进行过版本升级记录';
            echo json_encode($aData);

            self::writeLog([__line__."--t_migrate_yii表不存在", $aData]);
            Yii::$app->end();
        }

        $sSql = "SELECT count(*) FROM `t_migrate_yii` WHERE version='m000000_000000_base';";
        $count = Yii::$app->db->createCommand($sSql)->execute();
        if( $count<1 )
        {
            $aData['info'] = '未进行过版本升级记录';
            echo json_encode($aData);

            self::writeLog([__line__."--t_migrate_yii不存在基础升级数据m000000_000000_base", $sSql]);
            Yii::$app->end();
        }

        //将进度文件置空  // '/tmp/returnSysStatus.json';
        $sShell     = "/usr/bin/sudo /usr/bin/echo '' > ".self::$returnSysStatus;
        exec($sShell,$mdata, $return_var);
        self::writeLog([__line__."--将进度文件置空/tmp/returnSysStatus.json", $sShell, $return_var]);

        $sShell = "/usr/bin/sudo /usr/bin/chmod -R 777 ".self::$returnSysStatus;
        exec($sShell,$mdata, $return_var);
        self::writeLog([__line__."--修改权限，/tmp/returnSysStatus.json 777", $sShell, $return_var]);

        // 初始化还原进度文件 '/tmp/returnSysStatus.json' 写入state为0
        $rst = self::editStatus(0, 'rollback');
        self::writeLog([__line__."--写入/tmp/returnSysStatus.json state为0", "写入文件结果{$rst}"]);

        //执行还原
        $sShell = "/usr/bin/sudo /usr/bin/nohup /usr/bin/php /Data/apps/wwwroot/waf/www/yii migrate/down --interactive=0 --migrationPath=/Data/apps/wwwroot/waf/www/migrate > /dev/null 2>&1 &";
        system($sShell, $return_var);

        self::writeLog([__line__."--执行还原", $sShell, $return_var]);

        //TODO 执行恢复脚本 暂时未用
        //$sShell = "/usr/bin/sudo /usr/bin/sh ".self::$backup_file;
        //exec($sShell,$mdata, $return_var);
        //self::writeLog([__line__."执行恢复脚本", $sShell, $return_var]);

        $aData['code'] = 'T';
        $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("success");//''成功';
        echo json_encode($aData);
        Yii::$app->end();
    }

    /**
     * 获取系统还原时,还原的进度
     * @throws \yii\base\ExitException
     */
    public static function getReturnSysStatus()
    {
        $aData = ['code'=>'F', 'info'=>''];

        // "/tmp/returnSysStatus.json";
        if( !file_exists(self::$returnSysStatus) )
        {
            $aData['info'] = '数据为空';
            echo json_encode($aData);

            self::writeLog([__line__."--获取系统还原时,还原的进度getReturnSysStatus", $aData]);
            Yii::$app->end();
        }

        //数据为{"state": "1"} 0代表5% 1代表25%  2代表50%  3代表75%   4代表100%
        $result = json_decode(file_get_contents(self::$returnSysStatus),true);
        if( empty($result) )
        {
            $aData['info'] = '还原文件错误';
            echo json_encode($aData);

            self::writeLog([__line__."--获取系统还原时,还原的进度getReturnSysStatus", $aData]);
            Yii::$app->end();
        }
        $aData['state'] = $result['state'];

        if( intval($result['state'])===4 )
        {
            // 删除 runtime目录
            $sShell = "/usr/bin/sudo /usr/bin/rm -rf /Data/apps/wwwroot/waf/cache/runtime/";
            exec($sShell);

            $aData['complete'] = true;
        }

        $aData['code'] = 'T';
        $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("success");//'成功';
        echo json_encode($aData);
        Yii::$app->end();
    }

    /**
     * 还原 进度条
     * @param object $c 控制器类
     * @return mixed
     */
    public static function returnLoading($c)
    {
        file_put_contents(self::$returnSysStatus,json_encode(array('state'=>'0')));
        $aPost = (array)Yii::$app->wafHelper->getParam();

        $viewData = array();
        if(!empty($aPost['pre_name']))
        {
            $viewData['pre_name']   = $aPost['pre_name'];
        }

       return $c->render('maintenance_return_loading',$viewData);
    }

    /*
     * 翻译错误信息为中文
     */
    private static function getTips($msg)
    {
        $tips                                       = array();
        $tips['success']                            = '升级成功';
        $tips['abort']                              = '异常终止';
        $tips['update_in_progress']                 = '升级正在进行';
        $tips['dev_depend_patch_fail']              = '设备依赖性检查失败';
        $tips['build_dpdk_fail']                    = '升级dpdk失败';
        $tips['build_dpdk_warper_fail']             = '升级dpdk warper失败';
        $tips['build_policy_evolve_fail']           = '升级策略自动演进失败';
        $tips['build_ips_fail']                     = '升级IPS失败';
        $tips['build_waf_fail']                     = '升级web应用防护失败';
        $tips['build_snort_fail']                   = '升级防扫描、反拍照失败';
        $tips['build_user_authen_fail']             = '升级用户认证失败';
        $tips['update_php_fail']                    = '升级PHP失败';
        $tips['update_python_fail']                 = '升级python失败';
        $tips['update_database_fail']               = '升级数据库失败';
        $tips['missing_dpdk']                       = 'dpdk缺失';
        $tips['missing_dpdk_warper']                = 'dpdk warper升级包缺失';
        $tips['missing_snort']                      = '防扫描升级包缺失';
        $tips['missing_daq']                        = '防扫描升级包缺失';
        $tips['missing_python']                     = 'python升级包缺失';
        $tips['missing_python_etc']                 = 'python配置文件缺失';
        $tips['install_pyinotify_fail']             = '安装python pyinotify模块失败';
        $tips['install_ipy_fail']                   = '安装python ipy模块失败';
        $tips['install_jinja_fail']                 = '安装python jinja模块失败';
        $tips['install_markupsafe_fail']            = '安装python markupsafe模块失败';
        $tips['install_mysqlpython_fail']           = '安装python mysqlpython模块失败';
        $tips['install_netaddr_fail']               = '安装python netaddr模块失败';
        $tips['install_psutil_fail']                = '安装python psutil模块失败';

        $tips['no_update_package']                  = '找不到升级包';
        $tips['md5_check_fail']                     = '升级包md5校验失败';
        $tips['unable_to_decrypt_package']          = '升级包解密失败';
        $tips['cannot_extract_update_tar_ball']     = '无法解压升级包';
        $tips['incorrect_version_number']           = '版本号错误';
        return isset($tips[$msg])?$tips[$msg] : $msg;
    }

    /**
     * 返回页数处理数据
     * @return object Pagination 返回对象
     */
    private static function getPagination()
    {
        // 接收的页数
        $page = intval(Yii::$app->request->post('page',0));
        $page = $page>0?$page-1:$page;
        $pageSize = intval(Yii::$app->request->post('pagesize',20));

        $pagination = new Pagination(['totalCount' => self::find()->count()]);
        $pagination->page = $page;
        $pagination->pageSize = $pageSize;

        return $pagination;
    }

    /**
     * 保存数据
     * @param $aData
     * @return bool
     */
    public function saveData($aData)
    {
        $primaryKey = static::primaryKey();
        $id = $aData[$primaryKey[0]];
        $model = $id ? self::findOne($id) : $this;

        if( $model->load($aData, '') && $model->save() )
        {
            return true;
        }

        $this->addErrors($model->getErrors());
        return false;
    }

    /**
     * 删除数据
     * @param array $aData
     * @return boolean
     */
    public function delData($aData)
    {
        $ids = explode(',', $aData['aId']);
        if( empty($ids) )
        {
            $this->addError('id', Yii::t('app', 'error_parameter'));
            return false;
        }

        if( self::deleteAll(['in', 'id', $ids]) )
        {
            return true;
        }

        return false;
    }

    /**
     * @param $sVersion string 版本信息 m180409_061307_WAF_PHP0001_SQL0001_PY0001_FROM_PHP0000_SQL0000_PY0000
     * @param $sAction string 动作  migrate | rollback
     * @param $iStatus int 0.回退 1.升级 2.界面显示的数据(0和1不作界面显示)
     * @param string $sDesc string 描述信息 PHP0001 || MYSQL0001 || PYTHON0001
     * @param string $sMark string 备注
     * @param string $sVersionNum
     * @param string $sOldVersionNum
     * @param string $sTime string 时间
     */
    public static function saveLog($sVersion, $sAction, $iStatus, $sDesc = '', $sMark = '', $sVersionNum = '', $sOldVersionNum = '', $sTime = '')
    {
        // 初始化时间配置
        Yii::$app->sysInit->init();

        $sTime = $sTime ? $sTime : date("Y-m-d H:i:s");
        if( empty($sMark) )
        {
            $sMark = '升级成功';
            if( $sAction === 'rollback' )
            {
                $sMark = '回退成功';
            }
        }

        $aDate = [
            "sVersion" => $sVersion,
            "sAction" => $sAction,
            "sVersionNum" => $sVersionNum,
            "sOldVersionNum" => $sOldVersionNum,
            "sDesc" => $sDesc,
            "iStatus" => intval($iStatus),
            "sMark" => $sMark,
            "sTime" => $sTime,
        ];

        //日志
        $migrate = new self();
        $migrate->isNewRecord = true;
        $migrate->setAttributes($aDate);
        $rst = $migrate->saveData($aDate);

        self::writeLog([__line__."--saveLog保存版本信息", "结果:{$rst}", $aDate]);
    }

    /**
     * 判断表是否存在
     * @param $tableName string 表名
     * @param string $db 数据库连接名称
     * @return bool
     */
    public static function checkTableExist($tableName, $db = 'db')
    {
        if( empty(Yii::$app->$db->createCommand("SHOW TABLES LIKE '{$tableName}'")->queryAll()) )
        {
            return false;
        }

        return true;
    }

    /**
     * 判断字段是否存在
     * @param $tableName string 表名
     * @param $column_name string 字段名
     * @param string $db 数据库连接名称
     * @return bool
     */
    public static function checkColumnExist($tableName, $column_name, $db = 'db')
    {
        if ( empty(Yii::$app->$db->createCommand("SELECT COLUMN_NAME FROM information_schema.columns WHERE COLUMN_NAME='{$column_name}' AND TABLE_NAME='{$tableName}'")->queryAll()))
        {
            return false;
        }

        return true;
    }

    /**
     * 判断文件夹是否为空
     * @param $sDir string 文件路径
     * @return bool
     */
    public static function checkNotEmptydir($sDir)
    {
        $result = array_diff(scandir($sDir), array('..', '.'));
        if( empty($result) )
        {
            return false;
        }

        return true;
    }

    /**
     *
     * @param $status string 状态 "0" "1" "2" "3" "4"
     * @param string $sAction
     */
    /**
     * 写进度文件
     * @param $status string 状态 "0" "1" "2" "3" "4"
     * @param string $sAction ['rollback','migrate']
     * @return bool|int
     */
    public static function editStatus($status, $sAction = 'rollback')
    {
        if( !in_array($sAction, ['rollback','migrate']) )
        {
            return false;
        }

        // /tmp/updateSysStatus.json
        $file = self::$updateSysStatus;
        if ($sAction === 'rollback')
        {
            // /tmp/returnSysStatus.json
            $file = self::$returnSysStatus;
        }

        return file_put_contents($file, json_encode(['state' => (string)$status]));
    }

    /**
     * 合法性判断
     * 1.与系统PHP版本进行校验
     * 2.项目名称校验
     * @param $aVersion array() 版本信息数组
     * @return bool|mixed
     */
    public static function checkLegal($aVersion)
    {
        $aData = ['code'=>'F', 'info'=>''];

        //1.与系统PHP版本进行校验
        if (!is_array($aVersion) || empty($aVersion['migrate']['PHP']) || empty($aVersion['project']['name']))
        {
            $aData['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("parameterError"); //'参数错误';

            self::writeLog([__line__."--合法性判断checkLegal", $aData]);
            return $aData;
        }

        // 'PHP0001',
        $sNewVersion = str_replace("PHP", "", $aVersion['migrate']['PHP']);

        // /etc/waf_version/waf_version.conf
        if( !file_exists(self::$wafVersion) )
        {
            self::writeLog([__line__."--waf_version.conf not exist", self::$wafVersion]);

            // 目录不存在创建目录
            if( !is_dir("/etc/waf_version") )
            {
                $rst = mkdir("/etc/waf_version");
                self::writeLog([__line__."--mkdir创建目录 /etc/waf_version", "结果:{$rst}"]);
            }
            $rst = copy("/var/wafDownload/migrate/waf_version.conf", self::$wafVersion);
            self::writeLog([__line__."--copy复制文件",self::$wafVersion, "结果:{$rst}"]);

            if( !file_exists(self::$wafVersion) )
            {
                return false;
            }
        }

        // /etc/waf_version/waf_version.conf
        $shell = "cat ".self::$wafVersion." | grep -i PHP | awk 'END {print $2}'";
        exec($shell, $data);

        // PHP           svn-Rev5131
        $sOldVersion = str_replace("svn-Rev", "", $data[0]);
        $sOldVersion = str_replace("PHP", "", $sOldVersion);

        if ($sNewVersion < $sOldVersion)
        {
            $aData['info'] = 'incorrect version number';

            self::writeLog([__line__."--合法性判断checkLegal", $aData]);
            return $aData;
        }

        //2.项目名称校验
        $result = Devinfo::find()->where(['like', 'model', $aVersion['project']['name']])->one();
        if( empty($result) )
        {
            $aData['info'] = 'incorrect project name';

            self::writeLog([__line__."--合法性判断checkLegal", $aData]);
            return $aData;
        }

        $aData['code'] = 'T';
        $aData['info'] = 'success';
        return $aData;
    }

    /**
     * 更新系统版本号
     * @param $sVersion
     * @param $aMysqlFailedMsg
     */
    public static function editTbSysteminfoVersion($sVersion,&$aMysqlFailedMsg)
    {
        $rst = Devinfo::updateAll(['sys_ver'=>$sVersion], ['model'=>'BD-WAF']);
        if( !$rst )
        {
            self::writeLog([__line__."--update Dev_info table-- failure", $rst]);
            array_push($aMysqlFailedMsg, 'table t_devinfo no exist');
            return;
        }

        self::writeLog([__line__."--update Dev_info table-- success", $rst]);
    }

    /**
     * PHP||PYTHON  升级
     * @param $aFileUrl array
     * @param $sLanguage string
     * @param $aFailedMsg array
     */
    public static function updateFile($aFileUrl,$sLanguage, &$aFailedMsg)
    {
        $sUpdateDir = $aFileUrl[$sLanguage]['sUpdateDir'];
        $sLocalDir = $aFileUrl[$sLanguage]['sLocalDir'];
        $sBakDir = $aFileUrl['sBakDir'];
        $sFilenames = $aFileUrl[$sLanguage]['sFilenames'];

        if( !is_dir($sUpdateDir) || !is_dir($sBakDir) )
        {
            array_push($aFailedMsg, $sUpdateDir . 'dir not found!');
        }

        //备份
        $sShell = "cd " . $sLocalDir . " && /usr/bin/sudo /usr/bin/tar zcf " . $sBakDir . $sFilenames . " " . '*';  // cd /usr/local/bluedon && /usr/bin/sudo /usr/bin/tar zcf /var/www/migrate/bak/m180206_030624_VPN_PHP7946_SQL3914_PY3920_FROM_PHP6080_SQL2926_PY3045_PYTHON.tar.gz *
        if( $sLanguage === "PHP" )
        {
            // 由于runtime目录已移走。打包不排除
            // cd /Data/apps/wwwroot/waf/www && /usr/bin/sudo /usr/bin/tar zcf /var/wafDownload/migrate/bak/m180409_061307_WAF_PHP2481_SQL2470_PY2477_FROM_PHP2480_SQL2469_PY2476_PHP.tar.gz * --exclude=migrate --exclude=runtime
            $sShell = "cd " . $sLocalDir . " && /usr/bin/sudo /usr/bin/tar zcf " . $sBakDir . $sFilenames . " " . '*';
        }
        exec($sShell, $mdata, $return_var);
        self::writeLog([__line__."bak {$sLanguage} files", $sShell, $return_var]);

        //升级
        if( self::checkNotEmptydir($sUpdateDir)===false )
        {
            array_push($aFailedMsg, $sUpdateDir . 'dir is empty!');
        }

        // /usr/bin/sudo /usr/bin/cp -rf /var/www/migrate/update_php/* /Data/apps/wwwroot/waf/www/
        $sShell = "/usr/bin/sudo /usr/bin/cp -rf " . $sUpdateDir . "* " . $sLocalDir . "/";
        exec($sShell, $mdata, $return_var);
        self::writeLog([__line__."update {$sLanguage} files", $sShell, $return_var]);

        //权限
        $sShell = "/usr/bin/sudo /usr/bin/chmod -R 777 " . $sLocalDir;
        if( $sLanguage === "PHP" )
        {
            // chown -R www:www *
            //$sShell = "/usr/bin/sudo /usr/bin/chmod -R 777 " . $sLocalDir. " && /usr/bin/sudo /usr/bin/chown -R www:www *";
            $sShell = "cd " . $sLocalDir. " && /usr/bin/sudo /usr/bin/chown -R www:www *";
        }
        exec($sShell, $mdata, $return_var);
        self::writeLog([__line__."chown www files", $sShell, $return_var]);

        echo "{$sLanguage} UPDATE SUCCESS!!! \n";
    }

    /**
     * PHP||PYTHON 回退
     * @param $aFileUrl array
     * @param $sLanguage string
     * @param $aFailedMsg
     */
    public static function rollbackFile($aFileUrl,$sLanguage, &$aFailedMsg)
    {
        $sLocalDir = $aFileUrl[$sLanguage]['sLocalDir'];
        $sBakDir = $aFileUrl['sBakDir'];
        $sFilenames = $aFileUrl[$sLanguage]['sFilenames'];

        if( !is_dir($sBakDir) || !is_file($sBakDir . $sFilenames) )
        {
            array_push($aFailedMsg, $sBakDir . $sFilenames . 'file not found!');
        }

        // 删除 /Data/apps/wwwroot/waf/www 目录
        $sShell = "/usr/bin/sudo /usr/bin/rm -rf {$sLocalDir}/*";
        exec($sShell, $mdata, $return_var);
        self::writeLog([__line__."--删除{$sLanguage}/*目录", $sShell, $return_var]);

        //恢复
        $sShell = "/usr/bin/sudo /usr/bin/tar zxf " . $sBakDir . $sFilenames . " -C " . $sLocalDir . "/";
        exec($sShell, $mdata, $return_var);
        self::writeLog([__line__."--{$sLanguage}回退", $sShell, $return_var]);

        // PYTHON目录只需要root权限， PHP目录只需要www权限  权限 chown -R root:root * || 修改权限  chown -R www:www *
        $sChowns = "chown -R root:root *";
        if( $sLanguage === "PHP" )
        {
            $sChowns = "chown -R www:www *";
        }

        // 修改权限  chown -R www:www *
        $sShell = "cd " . $sLocalDir. " && /usr/bin/sudo /usr/bin/{$sChowns}";
        exec($sShell, $mdata, $return_var);
        self::writeLog([__line__."--{$sLanguage}修改权限chown www files", $sShell, $return_var]);

        echo "{$sLanguage} ROLLBACK SUCCESS!!! \n";
    }

    /**
     * 编写版本信息 Update version information
     * @param $aVersion array
     * @param $sAction string
     * @return bool
     */
    public static function editFwVersion($aVersion, $sAction)
    {
        // 初始化时间配置
        Yii::$app->sysInit->init();

        if(empty($aVersion) || empty($sAction))  return false;

        $time = date("Y-m-d H:i:s");
        $php_version = str_replace("PHP","",$aVersion[$sAction]['PHP']);
        $python_version = str_replace("PYTHON","",$aVersion[$sAction]['PYTHON']);
        $mysql_version = str_replace("MYSQL","",$aVersion[$sAction]['MYSQL']);
        $log = <<<EOF
        
-----------------------------------------
{$time}
PHP               {$php_version}
bluedon(PYTHON)   {$python_version}
DATABASE          {$mysql_version}
EOF;
        $rst = file_put_contents(self::$wafVersion,$log,FILE_APPEND);
        self::writeLog([__line__."save waf_version.conf", $log, "result:{$rst}"]);

        return true;
    }

    /**
     * PHP 与 PYTHON更新，记录日志等
     * @param $parentClass
     * @param $aFileUrl
     * @param $aVersion
     * @param $aPHPFailedMsg
     * @param $aPythonFailedMsg
     * @param $aMysqlFailedMsg
     */
    public static function follow_up($parentClass, $aFileUrl, $aVersion, $aPHPFailedMsg, $aPythonFailedMsg, $aMysqlFailedMsg)
    {
        //版本信息修改
        self::editTbSysteminfoVersion($aVersion['migrate']['sVersion'], $aMysqlFailedMsg);
        echo "MYSQL UPDATE SUCCESS!!! \n";

        // PHP升级
        self::updateFile($aFileUrl, 'PHP', $aPHPFailedMsg);

        // PYTHON升级
        self::updateFile($aFileUrl, 'PYTHON', $aPythonFailedMsg);

        // 这是由python建立的一个shell文件，执行如一些shell与c的编译等
        $aShellFile = glob($aFileUrl['SHELL']['sUpdateFile']."*.tar");
        self::writeLog([__line__."--执行shell与c的编译:", $aShellFile]);

        // 有python处理包才发管道,定义一个状态/tmp/updateShellStatus.json，是否为state'=1，才执行重启
        if( !empty($aShellFile) )
        {
            $sShellFile = implode("|", $aShellFile);
            $pcmd = "CMD_SYS_UPDATE|{$sShellFile}";

            self::writeLog([__line__."--发出升级shell的管道", $pcmd, $sShellFile]);

            $result = file_put_contents(self::$updateShellStatus, json_encode(['state'=>0]));
            self::writeLog([__line__."--写入python要处理管道默认值为0，当修改1时，管道完成/tmp/updateShellStatus.json:", $result]);

            Yii::$app->wafHelper->pipe($pcmd);
        }
        else
        {
            $result = file_put_contents(self::$updateShellStatus, json_encode(['state'=>1]));
            self::writeLog([__line__."--由于没有shell包，直接修改为1，不用管道处理/tmp/updateShellStatus.json:", $result]);
        }

        //MYSQL记录日志
        self::saveLog($parentClass, 'migrate', 1, $aVersion['migrate']['MYSQL'], json_encode($aMysqlFailedMsg), $aVersion['migrate']['sVersion'], $aVersion['rollback']['sVersion']);

        //PHP记录日志
        self::saveLog($parentClass, 'migrate', 1, $aVersion['migrate']['PHP'], json_encode($aPHPFailedMsg), $aVersion['migrate']['sVersion'], $aVersion['rollback']['sVersion']);

        //Python记录日志
        self::saveLog($parentClass, 'migrate', 1, $aVersion['migrate']['PYTHON'], json_encode($aPythonFailedMsg), $aVersion['migrate']['sVersion'], $aVersion['rollback']['sVersion']);

        //总记录日志
        $aVersionTmp = $aVersion['migrate'];
        array_shift($aVersionTmp);
        self::saveLog($parentClass, 'migrate', 2, implode(',', $aVersionTmp), json_encode(array_merge($aMysqlFailedMsg, $aPHPFailedMsg, $aPythonFailedMsg)), $aVersion['migrate']['sVersion'], $aVersion['rollback']['sVersion']);

        //打印错误调试信息
        var_dump(array_merge($aMysqlFailedMsg, $aPHPFailedMsg, $aPythonFailedMsg));
        self::writeLog([__line__."打印错误调试信息\r\n", $aMysqlFailedMsg, $aPHPFailedMsg, $aPythonFailedMsg]);

        //编写系统版本信息
        self::editFwVersion($aVersion, 'migrate');
    }

    /**
     * PHP 与 PYTHON回退，记录日志等
     * @param $parentClass
     * @param $aFileUrl
     * @param $aVersion
     * @param $aPHPFailedMsg
     * @param $aPythonFailedMsg
     * @param $aMysqlFailedMsg
     */
    public static function follow_down($parentClass, $aFileUrl, $aVersion, $aPHPFailedMsg, $aPythonFailedMsg, $aMysqlFailedMsg)
    {
        //版本信息修改
        self::editTbSysteminfoVersion($aVersion['rollback']['sVersion'], $aMysqlFailedMsg);
        echo "MYSQL ROLLBACK SUCCESS!!! \n";

        //写进度文件
        self::editStatus(2);

        // PHP还原
        self::rollbackFile($aFileUrl, 'PHP', $aPHPFailedMsg);

        //写进度文件
        self::editStatus(3);

        //PYTHON还原
        self::rollbackFile($aFileUrl, 'PYTHON', $aPythonFailedMsg);

        //MYSQL记录日志
        self::saveLog($parentClass, 'rollback', 1, $aVersion['rollback']['MYSQL'], json_encode($aMysqlFailedMsg), $aVersion['rollback']['sVersion'], $aVersion['migrate']['sVersion']);

        //PHP记录日志
        self::saveLog($parentClass, 'rollback', 1, $aVersion['rollback']['PHP'], json_encode($aPHPFailedMsg), $aVersion['rollback']['sVersion'], $aVersion['migrate']['sVersion']);

        //Python记录日志
        self::saveLog($parentClass, 'rollback', 1, $aVersion['rollback']['PYTHON'], json_encode($aPythonFailedMsg), $aVersion['rollback']['sVersion'], $aVersion['migrate']['sVersion']);

        //总记录日志
        $aVersionTmp = $aVersion['rollback'];
        array_shift($aVersionTmp);
        self::saveLog($parentClass, 'rollback', 2, implode(',', $aVersionTmp), json_encode(array_merge($aMysqlFailedMsg, $aPHPFailedMsg, $aPythonFailedMsg)), $aVersion['rollback']['sVersion'], $aVersion['migrate']['sVersion']);

        //打印错误调试信息
        var_dump(array_merge($aMysqlFailedMsg, $aPHPFailedMsg, $aPythonFailedMsg));

        //写进度文件
        self::editStatus(4);

        //编写系统版本信息
        self::editFwVersion($aVersion, 'rollback');
    }

    /**
     * 检查php与python管道是否完成，然后重启系统
     * @throws \yii\base\ExitException
     */
    public static function restartSystem()
    {
        $aData = ['code'=>'F', 'info'=>'not yet'];

        $sAction = trim(Yii::$app->request->post('sAction'));

        // 数据为{"state": "1"} 0代表5% 1代表25%  2代表50%  3代表75%   4代表100%
        $aSysStatus = json_decode(file_get_contents(self::$updateSysStatus),true);
        self::writeLog([__line__."restartSystem系统重启php状态：", $aSysStatus]);

        // 数据为{"state": "1"} 1代表python管道已完成
        $aShellStatus = [];
        if( $sAction==='migrate' )
        {
            $aShellStatus = json_decode(file_get_contents(self::$updateShellStatus),true);
            self::writeLog([__line__."{$sAction}系统重启python状态：", $aShellStatus]);
        }
        if( $sAction==='rollback' )
        {
            $aShellStatus = ['state'=>1];
            self::writeLog([__line__."{$sAction}系统重启python状态：", $aShellStatus]);
        }

        if( intval($aSysStatus['state']) === 4 && intval($aShellStatus['state']) === 1 )
        {
            //exec('/usr/bin/sudo reboot');
            $sShell = '/usr/bin/sudo reboot';
            pclose(popen($sShell.' > /dev/null &', 'r'));
            self::writeLog([__line__."--执行重启系统"]);

            $aData['code'] = 'T';
            $aData['info'] = 'success';
        }

        echo json_encode($aData);
        Yii::$app->end();
    }
}