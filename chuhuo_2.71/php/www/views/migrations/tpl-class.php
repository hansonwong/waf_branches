<?php
/**
 * This view is used by console/controllers/MigrateController.php
 * The following variables are available in this view:
 */
/* @var $className string the new migration class name without namespace */
/* @var $namespace string the new migration class namespace */

echo "<?php\n";
if (!empty($namespace)) {
    echo "\nnamespace {$namespace};\n";
}
?>

use yii\db\Migration;
use app\logic\waf\common\Migrate;
################waf################
class <?= $className ?> extends Migration
{
    /*
    * 文件路径
    * 为了更灵活操作，将配置文件信息移植升级文件中
    */
    public $aFileUrl = [
        'PHP' => [
            //php更新包目录
            'sUpdateDir' => "/var/www/migrate/update_php/",
            //php主目录
            'sLocalDir' => "/Data/apps/wwwroot/waf/www",
            //PHP备份包文件名称
            'sFilenames' => __CLASS__ . "_PHP.tar.gz",
        ],
        'PYTHON' => [
            //python更新包目录
            'sUpdateDir' => "/var/www/migrate/update_python/",
            //python主目录
            'sLocalDir' => "/usr/local/bluedon",
            //PYTHON备份包文件名称
            'sFilenames' => __CLASS__ . "_PYTHON.tar.gz",
        ],
        'SHELL' => [
            // /var/www/migrate/update_shell
            'sUpdateFile' => "/var/www/migrate/update_shell/",
        ],
        //备份包目录
        'sBakDir' => "/var/wafDownload/migrate/bak/"
        ];

    //版本信息
    public $aVersion = [
        "migrate" => [
        'sVersion' => '2.7.0.1',    //TODO 修改升级版本
        'PHP' => 'PHP2481',         //TODO PHP修改升级版本
        'MYSQL' => 'MYSQL2470',     //TODO MYSQL修改升级版本
        'PYTHON' => 'PYTHON2477',   //TODO PYTHON修改升级版本
        ],
        "rollback" => [
            'sVersion' => '2.7',        //TODO 修改回退版本
            'PHP' => 'PHP2480',         //TODO PHP回退升级版本
            'MYSQL' => 'MYSQL2469',     //TODO MYSQL回退升级版本
            'PYTHON' => 'PYTHON2476',   //TODO PYTHON回退升级版本
        ],
        'project' => [
            'name' => 'BD-WAF'
        ]
    ];
    //错误信息
    private static $aMysqlFailedMsg = [];
    private static $aPHPFailedMsg = [];
    private static $aPythonFailedMsg = [];

    public function init()
    {
        parent::init();

        ignore_user_abort(TRUE);
        set_time_limit(0);
    }

    public function up()
    {
        // 合法性判断
        $rst = Migrate::checkLegal($this->aVersion);

        Migrate::writeLog([__line__, "--migrate up 合法性判断结果：{$rst}"]);

        //Your database migrate is written here


        Migrate::follow_up(__CLASS__, $this->aFileUrl, $this->aVersion, self::$aPHPFailedMsg, self::$aPythonFailedMsg, self::$aMysqlFailedMsg);
    }

    public function down()
    {
        //Your database rollback is written here

        Migrate::follow_down(__CLASS__, $this->aFileUrl, $this->aVersion, self::$aPHPFailedMsg, self::$aPythonFailedMsg, self::$aMysqlFailedMsg);
    }
}
