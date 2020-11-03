<?php

namespace app\controllersConsole;
use Yii;
use yii\console\Controller;

class TestController extends Controller
{
    public $a, $b, $c;

    public function options($action)
    {
        return ['a', 'b', 'c'];
    }

    public function actionIndex($a, $b, $c)
    {
        echo $a . $b . $c . '7777';
        $a = \app\logic\waf\report\Timer::a();
        echo $a;
        echo 'kkk';
    }

    public function actionIndexBox($a, $b, $c)
    {
        echo $a . $b . $c . 'ttt';
        $a = \app\logic\waf\report\Timer::a();
        echo $a;
        echo 'kkk';
    }
}