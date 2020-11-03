<?php

namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\modelFirewall\TbBridgeDevice;
use app\modelFirewall\TbNetPort;
use app\widget\AdminListConfig;
use app\logic\waf\helpers\WafHelper;
use app\logic\waf\helpers\WafRegexp;
use yii\data\Pagination;

/**
 * 网络配置 - 透明代理
 * 由于新增加了 “透明代理” 的模式
 * Class TProxyController
 * @package app\controllers
 */
class TProxyController extends BaseController
{
    /**
     * 桥设备头部
     * @return string
     */
    private function GridHeader()
    {
        $aData = [
            ['sTitle' => 'ID', 'data' => 'id', 'bVisible' => false],
            ['sTitle' => $this->translate->getTranslateBySymbol('deviceName'), 'data' => 'sBridgeName'], // 设备名称
            ['sTitle' => $this->translate->getTranslateBySymbol('ip/mask'), 'data' => 'sIPV4', 'sClass' => 'sIPV4'], // IP地址/掩码
            ['sTitle' => $this->translate->getTranslateBySymbol('bindingInterfaceList'), 'data' => 'sBindDevicesLan'], // 绑定接口列表
            ['sTitle' => $this->translate->getTranslateBySymbol('isItEnabled'), 'data' => 'iStatus', 'sClass' => 'iStatus'], // 是否启用
            ["sClass"=>"btn_edit","bVisible"=>false,"data"=>""],
            ["sClass"=>"btn_del","bVisible"=>false,"data"=>""]
        ];
        return json_encode($aData);
    }

    /**
     *{
     *"data":[
     *{"name":"www.ddjian.me","grade":"1","beizhu":"ddjian.me","way":"拒绝访问","serverSelect":"1"},
     *{"name":"www.ddjian.me","grade":"1","beizhu":"ddjian.me","way":"拒绝访问","serverSelect":"1"}
     *],
     *"Total":"2"
     *}
     * @return string
     */
    private function GridBody()
    {
        // 接收的页数
        $page = intval(Yii::$app->request->post('page',0));
        $page = $page>0?$page-1:$page;
        $pageSize = intval(Yii::$app->request->post('pagesize',20));

        // 排序
        $sortName = Yii::$app->request->post('sortname','id');
        $sortOrder = Yii::$app->request->post('sortorder','DESC');
        $orderBy = "{$sortName} {$sortOrder}";
        if( strlen($orderBy)<1 )
        {
            $orderBy = "id DESC";
        }

        // 筛选 透明代理 的条件
        $where = ['bridgeType' => 'tproxy'];

        $pagination = new Pagination(['totalCount' => TbBridgeDevice::find()->where($where)->count()]);
        $pagination->page = $page;
        $pagination->pageSize = $pageSize;

        $list = [];
        // 查询字段
        $select = "*";
        $model =  TbBridgeDevice::find()->select($select)->where($where)->orderBy($orderBy)->offset($pagination->offset)->limit($pagination->limit)->asArray()->all();
        foreach( $model as $v )
        {
            // 整理输出数据
            $list[] = [
                "id" => $v['id'],
                "sBridgeName" => $v['sBridgeName'],
                "sIPV4" => $v['sIPV4'],
                "sBindDevicesLan" => $v['sBindDevices'],
                "iStatus" => $v['iStatus'] == 1?1:2,
            ];
        }

        $data = [
            'data' => $list,
            'total' => $pagination->totalCount,
            'page' => $pagination->offset+1,
            'pagesize' => $pageSize,
        ];
        return json_encode($data);
    }

    /**
     * 桥设备列表
     * @return string
     */
    public function actionIndex()
    {
        // 返回模板
        if( Yii::$app->request->isGet )
        {
            $model = '';
            return $this->render('index', [
                'model' => $model,
            ]);
        }

        // 返回头部数据
        if( Yii::$app->request->get('op')=='header' ) return $this->GridHeader();

        // 返回表格数据
        return $this->GridBody();
    }

    /**
     * "CMD_BRIDGE_CONFIG|del";
     * 删除
     * @throws \yii\base\ExitException
     */
    public function actionDelete()
    {
        $id_arr = Yii::$app->request->post('id_arr');
        $id_arr = json_decode($id_arr);
        if( empty($id_arr) )
        {
            $info = $this->translate->getTranslateBySymbol('thereIsNoSelectionOfDataToDelete');// '没有选择需要删除的数据';
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        // 过滤非数字的内容
        $id_arr = array_filter($id_arr, 'is_numeric');
        $id_str = implode(",", $id_arr);
        $sBridgeNameList = TbBridgeDevice::find()->where("id in ({$id_str})")->asArray()->all();
        foreach( $sBridgeNameList as $v )
        {
            if( TbBridgeDevice::deleteAll("id={$v['id']}") === false )
            {
                $info = $this->translate->getTranslateBySymbol('deleteFailed');// '删除失败';
                AdminListConfig::returnSuccessFieldJson('F', $info, true);
            }

            // 网口配置数据不用手动去删除，发出删除管道就已清除数据的

            // 转换json数据
            $data = Yii::$app->wafHelper->fireConvertData($v);
            // 防火墙的管道命令,需要附加json数据过去
            $sCommand = "CMD_BRIDGE_CONFIG|del|".$data;
            //写入命名管道
            Yii::$app->wafHelper->firePipe($sCommand);
        }

        $info = $this->translate->getTranslateBySymbol('operationSuccess');// '操作成功';
        AdminListConfig::returnSuccessFieldJson('T', $info, true);
    }

    /**
     * 添加
     * @return string
     * @throws \yii\base\ExitException
     */
    public function actionCreate()
    {
        $model = new TbBridgeDevice;

        //判断是不是Ajax提交
        if (Yii::$app->request->isAjax)
        {
            $model->load(Yii::$app->request->post());
            // 初始化一些值
            $model->sBridgeName = "bridge".$model->sBridgeName; //桥设备名称
            $model->bridgeType = "tproxy"; //桥的类型
            if( empty($model->iStatus) ) $model->iStatus = 1; // 是否启用，0否，1是
            if( empty($model->iWeb) ) $model->iWeb = 0; // 是否WEBUI，0否，1是
            if( empty($model->iSSH) ) $model->iSSH = 0; // 是否SSH，0否，1是
            if( empty($model->iAllowPing) ) $model->iAllowPing = 0; // 是否允许ping，0否，1是
            if( empty($model->iAllowTraceRoute) ) $model->iAllowTraceRoute = 0; // 是否允许traceroute，0否，1是
            if( empty($model->iAllowLog) ) $model->iAllowLog = 0; // 是启用日志，0否，1是

            // 判断如果不输入 ipv6或者ipv6, 不能勾选WEBUI、SSH、允许PING、允许Traceroute'
            if( empty($model->sIPV4) && empty($model->sIPV6) )
            {
                if( $model->iSSH || $model->iWeb || $model->iAllowPing || $model->iAllowTraceRoute )
                {
                    $info = $this->translate->getTranslateBySymbol('proxyTypeIpOrDoNotSelectTips');//'请填写IP地址或者请勿勾选WEBUI、SSH、允许PING、允许Traceroute';
                    AdminListConfig::returnSuccessFieldJson('F', $info, true);
                }
            }

            // 所选网口数必须为两个以上
            $portSize = explode(",", $model->sBindDevices);
            if( count($portSize) < 2 )
            {
                $info = $this->translate->getTranslateBySymbol('selectNetworkCountTips(two)');// "所选网口数必须为两个以上（含两个）！";
                AdminListConfig::returnSuccessFieldJson('F', $info, true);
            }

            //判断IP地址输入是否正确  并将以','隔开存进数据库
            if( !empty($model->sIPV4) )
            {
                $rst = $this->checkIpv4($model->sIPV4);
                if( $rst['code'] != 'T' )
                {
                    AdminListConfig::returnSuccessFieldJson('F', $rst['info'], true);
                }

                $model->sIPV4 = $rst['sIPV4'];
            }

            //判断IPV6地址输入是否正确  并将以','隔开存进数据库
            if( !empty($model->sIPV6) )
            {
                $rst = $this->checkIpv6($model->sIPV6);
                if( $rst['code'] != 'T' )
                {
                    AdminListConfig::returnSuccessFieldJson('F', $rst['info'], true);
                }
                $model->sIPV6 = $rst['sIPV6'];
            }

            if( !$model->save() )
            {
                //获取取检验错误信息
                $info = Yii::$app->wafHelper->getModelErrors($model);
                AdminListConfig::returnSuccessFieldJson('F', $info, true);
            }

            // 查询出入库的数据, 并把查询出来的数据转成json数据传到管道上
            $id = $model->getAttribute('id');
            $newModel = TbBridgeDevice::find()->where(['id'=> $id])->asArray()->one();
            $data = Yii::$app->wafHelper->fireConvertData($newModel);

            // 防火墙的管道命令,需要附加json数据过去
            $sCommand = "CMD_BRIDGE_CONFIG|add|".$data;
            //写入命名管道
            Yii::$app->wafHelper->firePipe($sCommand);

            //更新网口配置表
            $TbNetPortModel = new TbNetPort;
            $TbNetPortModel->sPortName = $model->sBridgeName;
            $TbNetPortModel->sWorkMode = 'bridge';
            $TbNetPortModel->iStatus = '1';
            $TbNetPortModel->sLan = $model->sBridgeName;
            $TbNetPortModel->iWeb = $model->iWeb;
            $TbNetPortModel->iSSH = $model->iSSH;
            $TbNetPortModel->iAllowPing = $model->iAllowPing;
            $TbNetPortModel->iAllowTraceRoute = $model->iAllowTraceRoute;
            $TbNetPortModel->sIPV4Address = isset($model->sIPV4)?$model->sIPV4:'';
            $TbNetPortModel->sIPV6Address = isset($model->sIPV6)?$model->sIPV6:'';
            if( !$TbNetPortModel->save() )
            {
                //获取取检验错误信息
                $info = Yii::$app->wafHelper->getModelErrors($TbNetPortModel);
                AdminListConfig::returnSuccessFieldJson('F', $info, true);
            }

            // 防火墙的管道命令
            // 此管道刷新了网口配置新建的透明代理数据
            $sCommand = "CMD_NIC_FLUSH";
            //写入命名管道
            Yii::$app->wafHelper->firePipe($sCommand);

            $info = $this->translate->getTranslateBySymbol('operationSuccess');// '操作成功';
            AdminListConfig::returnSuccessFieldJson('T', $info,true);
        }
        else
        {
            //桥设置表TbBridgeDevice，已使用的网口
            $TbBridgeDeviceModel = TbBridgeDevice::find()
                                                 ->select("group_concat(sBindDevices) as sBindDevices")
                                                 ->asArray()
                                                 ->all();
            // vEth0,vEth1,bond0,vEth2
            $sBindDevices = explode(",", $TbBridgeDeviceModel[0]['sBindDevices']);

            //查出 网口配置表Tbnetport，可用的网口
            $where = "sWorkMode='bridge' AND iStatus=1 ";
            // 用not in好像不行，只能改用这个
            if( !empty($sBindDevices) )
            {
                foreach( $sBindDevices as $v )
                {
                    $where .= "AND sPortName <>'{$v}' ";
                }
            }

            $netPortModel = TbNetPort::find()->where($where)->asArray()->all();

            $model->sBindDevices = [];
            return $this->render('save', [
                'model' => $model,
                'netPortModel' => $netPortModel,
            ]);
        }
    }

    /**
     * 更新启用状态
     * @throws \yii\base\ExitException
     */
    private function UpdateStatus()
    {
        // 接收数据格式 ["981036"]或者["981036"，"981038"]
        $idArr = Yii::$app->request->post('idArr');

        $idArr = json_decode($idArr);
        $idArr = array_filter($idArr, 'is_numeric'); // 返回只有数值的
        if( empty($idArr) )
        {
            $info = $this->translate->getTranslateBySymbol('thereIsNoSelectionOfDataToDelete');// '没有选择需要删除的数据';
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        // 接收数据格式 0或者1
        $status = Yii::$app->request->post('status');
        if( !in_array($status, [0,1]) )
        {
            $info = $this->translate->getTranslateBySymbol('theDisableParameterIsNotCorrect');//启用停用的参数错误
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        $idStr = implode(",", $idArr);
        $sBridgeNameList = TbBridgeDevice::find()->where("id in ({$idStr})")->asArray()->all();
        foreach( $sBridgeNameList as $v )
        {
            if( TbBridgeDevice::updateAll(['iStatus'=>$status], "id={$v['id']}") < 1 )
            {
                $info = $this->translate->getTranslateBySymbol('updateFailed');// '更新失败';
                AdminListConfig::returnSuccessFieldJson('F', $info, true);
            }

            // 重新获取数据
            $newMode = TbBridgeDevice::findOne($v['id'])->toArray();
            $data = Yii::$app->wafHelper->fireConvertData($newMode);
            // 防火墙的管道命令,需要附加json数据过去
            $sCommand="CMD_BRIDGE_CONFIG|enable|".$data;
            //写入命名管道
            Yii::$app->wafHelper->firePipe($sCommand);
        }

        $info = $this->translate->getTranslateBySymbol('operationSuccess');// '操作成功';
        AdminListConfig::returnSuccessFieldJson('T', $info, true);
    }

    /**
     * 编辑
     * @param int $id
     * @return mixed|string
     * @throws \yii\base\ExitException
     */
    public function actionUpdate($id=0)
    {
        // 更新启用状态
        if( Yii::$app->request->get('op')=='status' )
        {
            $this->UpdateStatus();
        }

        $model = TbBridgeDevice::findOne($id);
        //判断是不是Ajax提交
        if (Yii::$app->request->isAjax)
        {
            // 模型转换成数组形式，用于删除旧管道的
            $modelArr = $model->toArray();

            $post = Yii::$app->request->post('TbBridgeDevice');
            $model->load(Yii::$app->request->post());
            // 初始化一些值
            $model->sBridgeName = "bridge".$model->sBridgeName; //桥设备名称
            $model->bridgeType = "tproxy"; //桥的类型
            if( empty($model->iStatus) ) $model->iStatus = 1; // 是否启用，0否，1是

            if( empty($post['iWeb']) ) $model->iWeb = 0; // 是否WEBUI，0否，1是
            if( empty($post['iSSH']) ) $model->iSSH = 0; // 是否SSH，0否，1是
            if( empty($post['iAllowPing']) ) $model->iAllowPing = 0; // 是否允许ping，0否，1是
            if( empty($post['iAllowTraceRoute']) ) $model->iAllowTraceRoute = 0; // 是否允许traceroute，0否，1是
            if( empty($post['iAllowLog']) ) $model->iAllowLog = 0; // 是启用日志，0否，1是

            // 判断如果不输入 ipv6或者ipv6, 不能勾选WEBUI、SSH、允许PING、允许Traceroute'
            if( empty($model->sIPV4) && empty($model->sIPV6) )
            {
                if( $model->iSSH || $model->iWeb || $model->iAllowPing || $model->iAllowTraceRoute )
                {
                    $info = $this->translate->getTranslateBySymbol('proxyTypeIpOrDoNotSelectTips');// '请填写IP地址或者请勿勾选WEBUI、SSH、允许PING、允许Traceroute';
                    AdminListConfig::returnSuccessFieldJson('F', $info, true);
                }
            }

            // 所选网口数必须为两个以上
            $portSize = explode(",", $model->sBindDevices);
            if( count($portSize) < 2 )
            {
                $info = $this->translate->getTranslateBySymbol('selectNetworkCountTips(two)');// "所选网口数必须为两个以上（含两个）！";
                AdminListConfig::returnSuccessFieldJson('F', $info, true);
            }

            //判断IP地址输入是否正确  并将以','隔开存进数据库
            if( !empty($model->sIPV4) )
            {
                $rst = $this->checkIpv4($model->sIPV4);
                if( $rst['code'] != 'T' )
                {
                    AdminListConfig::returnSuccessFieldJson('F', $rst['info'], true);
                }

                $model->sIPV4 = $rst['sIPV4'];
            }

            //判断IPV6地址输入是否正确  并将以','隔开存进数据库
            if( !empty($model->sIPV6) )
            {
                $rst = $this->checkIpv6($model->sIPV6);
                if( $rst['code'] != 'T' )
                {
                    AdminListConfig::returnSuccessFieldJson('F', $rst['info'], true);
                }
                $model->sIPV6 = $rst['sIPV6'];
            }

            //先执行一次管道命令删除数据
            $data = Yii::$app->wafHelper->fireConvertData($modelArr);
            // 防火墙的管道命令,需要附加json数据过去
            $sCommand = "CMD_BRIDGE_CONFIG|del|".$data;
            //写入命名管道
            Yii::$app->wafHelper->firePipe($sCommand);

            // 保存数据
           if( !$model->save() )
            {
                //获取取检验错误信息
                $info = Yii::$app->wafHelper->getModelErrors($model);
                AdminListConfig::returnSuccessFieldJson('F', $info, true);
            }

            // 查询出入库的数据, 并把查询出来的数据转成json数据传到管道上
            $id = $model->getAttribute('id');
            $newModel = TbBridgeDevice::find()->where(['id'=> $id])->asArray()->one();
            $data = Yii::$app->wafHelper->fireConvertData($newModel);

            // 防火墙的管道命令,需要附加json数据过去
            $sCommand = "CMD_BRIDGE_CONFIG|add|".$data;
            //写入命名管道
            Yii::$app->wafHelper->firePipe($sCommand);

            //更新网口配置表
            $TbNetPortModel = TbNetPort::find()->where("sPortName='{$modelArr['sBridgeName']}'")->one();
            $TbNetPortModel->sPortName = $model->sBridgeName;
            $TbNetPortModel->sWorkMode = 'bridge';
            $TbNetPortModel->iStatus = '1';
            $TbNetPortModel->sLan = $model->sBridgeName;
            $TbNetPortModel->iWeb = $model->iWeb;
            $TbNetPortModel->iSSH = $model->iSSH;
            $TbNetPortModel->iAllowPing = $model->iAllowPing;
            $TbNetPortModel->iAllowTraceRoute = $model->iAllowTraceRoute;
            $TbNetPortModel->sIPV4Address = isset($model->sIPV4)?$model->sIPV4:'';
            $TbNetPortModel->sIPV6Address = isset($model->sIPV6)?$model->sIPV6:'';
            if( !$TbNetPortModel->save() )
            {
                //获取取检验错误信息
                $info = Yii::$app->wafHelper->getModelErrors($TbNetPortModel);
                AdminListConfig::returnSuccessFieldJson('F', $info, true);
            }

            // 防火墙的管道命令
            // 此管道刷新了网口配置新建的透明代理数据
            $sCommand = "CMD_NIC_FLUSH";
            //写入命名管道
            Yii::$app->wafHelper->firePipe($sCommand);

            $info = $this->translate->getTranslateBySymbol('operationSuccess');// '操作成功';
            AdminListConfig::returnSuccessFieldJson('T', $info,true);
        }
        else
        {
            //桥设置表TbBridgeDevice，已使用的网口
            $TbBridgeDeviceModel = TbBridgeDevice::find()
                ->select("group_concat(sBindDevices) as sBindDevices")
                ->asArray()
                ->all();
            // vEth0,vEth1,bond0,vEth2
            $sBindDevices = explode(",", $TbBridgeDeviceModel[0]['sBindDevices']);

            //查出 网口配置表Tbnetport，可用的网口
            $where = "sWorkMode='bridge' AND iStatus=1 AND sPortName<>'{$model->sBridgeName}'";
            // 用not in好像不行，只能改用这个
            if( !empty($sBindDevices) )
            {
                foreach( $sBindDevices as $v )
                {
                    $where .= "AND sPortName <>'{$v}' ";
                }
            }
            $netPortModel = TbNetPort::find()->where($where)->asArray()->all();

            // 调整model数据
            $model->sBridgeName = str_replace('bridge', '', $model->sBridgeName);
            $model->sBindDevices = explode(",", $model->sBindDevices);

            return $this->render('save', [
                'model' => $model,
                'netPortModel' => $netPortModel,
            ]);
        }
    }

    /**
     * 检查传递过来的ipv4是否正确
     * @param $ipv4
     * @return array
     */
    public function checkIpv4($ipv4)
    {
        $result = ['code'=>'F', 'info'=>'', 'sIPV4'=>''];

        // 在字符串 string 所有新行之前插入 '<br />' 或 '<br>'，并返回
        $targrt_ip = nl2br($ipv4);
        // 替换掉 <br />
        $targrt_ip = str_replace("<br />", "", $targrt_ip);

        $aIPS = explode("\r\n", $targrt_ip);
        $aIPS = array_filter($aIPS);
        if( empty($aIPS) )
        {
            $result['info'] = $this->translate->getTranslateBySymbol('emptyData'); //'空数据';
            return $result;
        }

        $result['sIPV4'] = implode(",", $aIPS);

        foreach( $aIPS as $k => $v )
        {
            if( empty($v) ) continue;

            $vals = explode("/", $v);
            if( isset($vals[1]) && empty($vals[1]) )
            {
                $result['info'] = $vals[1].$this->translate->getTranslateBySymbol('maskFormatError'); //掩码格式错误;
                return $result;
            }

            if (!preg_match(WafRegexp::$ip4, $vals[0]))
            {
                $result['info'] = $this->translate->getTranslateBySymbol('ipV4FormatError'); //"IPV4格式错误";
                return $result;
            }

            $fipnum = explode(".", $vals[1]);
            if( count($fipnum) != 4 && count($fipnum) != 1 )
            {
                $result['info'] = $this->translate->getTranslateBySymbol('maskFormatError'); //掩码格式错误;
                return $result;
            }

            // 判断掩码对不对
            if( count($fipnum) == 4 )
            {
                $netmask = WafHelper::getDecIp($vals[1]);
                if (!in_array($netmask, WafRegexp::$CIDRDEC))
                {
                    $result['info'] = $vals[0] . $this->translate->getTranslateBySymbol('maskFormatError'); //掩码格式错误;
                    return $result;
                }
            }

            // 判断只有一位的掩码
            if( count($fipnum) == 1 )
            {
                if( !is_numeric($fipnum[0]) || intval($fipnum[0])<0 || intval($fipnum[0])>32 )
                {
                    $result['info'] = $vals[0] . $this->translate->getTranslateBySymbol('maskFormatError'); //掩码格式错误;
                    return $result;
                }
            }

            //校验是否网段
            $addr_ip = $vals[0];
            $addr_mask = $vals[1];
            //判断掩码是否为数值 例/24  如果为false则为数值
            $pos = strpos($addr_mask, '.');
            if ($pos == false)
            {
                $addr_mask_num = intval($addr_mask);
                $addr_mask = '';
                $addr_mask = str_pad($addr_mask, $addr_mask_num, '1');
                $addr_mask = str_pad($addr_mask, 32, '0');
                $addr_mask = bindec($addr_mask);
                $addr_mask_int = $addr_mask;
                //将/24转为 255.255.255.0
                //$addr_mask                      = long2ip($addr_mask);
            }
            else
            {
                $addr_mask_int = ip2long($addr_mask);
            }

            //判断掩码是否合法
            if (($addr_mask_int | ($addr_mask_int - 1)) != 0xFFFFFFFF)
            {
                $result['info'] = $this->translate->getTranslateBySymbol('maskFormatError'); //掩码格式错误;
                return $result;
            }

            //将IP地址转为10进制数
            $addr_ip_int = ip2long($addr_ip);

            //取反，此处得到的是补码
            $_addr_mask_int = ~$addr_mask_int;

            //进行 "与" 运算   如果得到的是0代表网段/MASK填写正确   如果不为0则代表不正确
            $mask_correct = $_addr_mask_int & $addr_ip_int;
            if ($mask_correct == 0)
            {
                $result['info'] =  $vals[0] . $this->translate->getTranslateBySymbol('typeTrueIpAddr'); //' 请输入正确的IP地址';
                return $result;
            }
        }

        $result['code'] = 'T';
        $result['info'] = $this->translate->getTranslateBySymbol('success'); //'成功';
        return $result;
    }

    /**
     * 检查传过来的ipv6是否正确
     * @param $ipv6
     * @return array
     */
    public function checkIpv6($ipv6)
    {
        $result = ['code'=>'F', 'info'=>'', 'sIPV6'=>''];

        $targrt_ip = nl2br($ipv6);
        $targrt_ip = str_replace("<br />", "", $targrt_ip);
        $aIPS = explode("\r\n", $targrt_ip);
        $aIPS = array_filter($aIPS);

        $result['sIPV6'] = implode(",", $aIPS);
        foreach ($aIPS as $k => $v)
        {
            if (empty($v)) continue;

            if( !WafHelper::CheckIPV6($v, 2) )
            {
                $result['info'] =  $v.$this->translate->getTranslateBySymbol('ipV6FormatError'); //' IPV6格式错误';
                return $result;
            }
        }

        $result['code'] = 'T';
        $result['info'] = $this->translate->getTranslateBySymbol('success'); //'成功';
        return $result;
    }
}
