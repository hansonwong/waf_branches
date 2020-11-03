<?php

namespace app\controllersConsole;
use Yii;
use yii\console\Controller;

class SysInitController extends Controller
{
    public function actionSyncFirewallTranslation(){
        $r = \app\modelFirewall\Language::syncFirewallTranslation();
        echo $r ? 'ok' : 'faild';
    }
}