<?php

namespace app\controllersConsole;
use Yii;
use yii\console\Controller;

class SysUserController extends Controller
{
    public function actionUpdateUserPwd($user, $pwd){
        $result = \app\logic\firewall\FirewallUser::updateUserPwd($user, $pwd);
        echo $result ? 'OK' : 'FAILURE';
    }

    public function actionUpdateAllUserPwd(){
        \app\logic\firewall\FirewallUser::syncWafAndFirewallUser();
    }

    public function actionSetConfig(){
        echo '$dbUser = ';
        $dbUser = trim(fgets(STDIN));
        echo '$dbPwd = ';
        $dbPwd = trim(fgets(STDIN));
        echo '$dbIp = ';
        $dbIp = trim(fgets(STDIN));

        $db = [];
        $dbI = 0;
        while(1){
            ++$dbI;
            echo "\n\nenter mysql db {$dbI}:\n";
            echo "Use default user/password/ip? type y,Y or 'enter' and type n will setting other\n";
            echo "type ok: finish\n";
            echo "y,Y,'enter',n:";
            $default = trim(fgets(STDIN));
            if('ok' == $default) break;

            $dbItem = [];
            if(in_array($default, ['', 'y', 'Y'])){
                $dbItem['host'] = $dbIp;
                $dbItem['user'] = $dbUser;
                $dbItem['pwd'] = $dbPwd;
            } else {
                echo 'user = ';
                $dbItem['user'] = trim(fgets(STDIN));
                echo 'pwd = ';
                $dbItem['pwd'] = trim(fgets(STDIN));
                echo 'host = ';
                $dbItem['host'] = trim(fgets(STDIN));
            }

            echo "dbName:";$dbItem['dbName'] = trim(fgets(STDIN));
            echo "yiiKey:";$dbItem['yiiKey'] = trim(fgets(STDIN));
            echo "port:";$dbItem['port'] = trim(fgets(STDIN));

            $db[] = $dbItem;
        }

        $config['mysql'] = $db;
        $projectDir = Yii::$app->sysParams->getParamsChild(['projectDir']);
        $file = realpath("{$projectDir}/../cache").'/interfaceConfig.json';
        file_put_contents($file,json_encode($config));
        echo "OK\n";
    }
}