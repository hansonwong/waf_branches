<?php
namespace console\controllers;//\script;
use Yii;
use yii\console\Controller;
/*use fec\helpers\CDate;
use fec\helpers\CConfig;
use appadmin\code\Website\models\WebsiteBaseInfo;*/
class TestController extends Controller
{
        public $_mongodbdb;
        public function actionGetbegindate(){
                echo '2015-05-20';
        }
        public function actionCreatecollindexer(){
                echo 'create Coll index success';
        }
        public function actionMy($param1,$param2=''){
                echo "param1:".$param1;
                echo "param2:".$param2;
        }

        public function actionIndex($a, $b, $c){
                echo $a.$b.$c.'7777';
        }
}