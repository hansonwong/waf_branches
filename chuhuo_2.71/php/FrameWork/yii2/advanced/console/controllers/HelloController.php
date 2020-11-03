<?php
namespace console\controllers;
use Yii;
use yii\console\Controller;
use aaa\a;

class HelloController extends Controller
{

        public function actionIndex($a, $b, $c){
                echo $a.$b.$c.'555555555';
                $a = new a();
                $a->test();
        }

        public function actionB(){
                echo 'ttt';
        }
}