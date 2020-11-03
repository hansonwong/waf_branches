<?php

/**
 * User: magee
 * Date: 15-11-18
 * Time: 下午3:48
 * @since 1.0
 * @id: NetworkController.php
 * 描述：网络设置
 * 修改功能描述：
 */
class NetworkController extends MqController
{
	private $network_port_file				= "/etc/network_config/mgt_nic.txt";

	//网络接口头部
	public function actionGetHeaderTitleNetPort(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang','接口名称'),'data'=>'sLan','width'=>'15%'),
				// array('sTitle'=>'接口','data'=>'sPortName','width'=>'15%'),
				array('sTitle'=>Yii::t('lang','IPV4地址/掩码'),'data'=>'sIPV4Address','width'=>'25%'),
            	array('sTitle'=>Yii::t('lang','IPV6地址/掩码'),'data'=>'sIPV6Address','width'=>'15%'),
				array('sTitle'=>Yii::t('lang','工作模式'),'data'=>'sWorkMode','sClass'=>'sWorkMode'),
				array('sTitle'=>Yii::t('lang','是否启用'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>2),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//网络接口列表
	public function actionNetPort(){
		if(Yii::app()->request->isPostRequest){

			$param['hModel'] 				= new TbNetPort();
			$c=new CDBCriteria();
			$c->order=" locate(sPortName,'enp1s0,enp2s0,enp3s0,enp4s0,enp5s0,enp6s0,enp7s0,enp8s0,enp9s0,enp10s0, enp11s0, enp12s0,enp13s0,enp14s0,vEth0,vEth1,vEth2,vEth3,vEth4,vEth5,vEth6,vEth7,vEth8,vEth9,vEth10,vEth11,vEth12,vEth13,vEth14,vEth15,vEth16,vEth17,vEth18,vEth19,vEth20,vEth21,vEth22,vEth23,vEth24,vEth25,,vEth26,vEth27,vEth28,vEth29,vEth30,vEth31,vEth32,vEth33,vEth34,vEth35,vEth36,vEth37,vEth38,vEth39,vEth40,vEth41,vEth42,vEth43,vEth44,vEth45,vEth46,vEth47,vEth48,vEth49,vEth50')  ASC";
			$param['criteria']				= $c;
			$param['returnData'] 			= 2;
			DBHelper::saveCommand("CMD_NIC_FLUSH");
			$netport_data   				= DBHelper::getDataList($param);
			//判断网口是否是管理口
			$re 							= file_get_contents($this->network_port_file);
			$enPort 						= array_keys(json_decode($re,true));	//获取所有键名   该数组为所有管理口的名称
			if(!empty($enPort) && !empty($netport_data)){
				$netport_new_data			= array();
				foreach($netport_data['data'] as $value){
					//网口名称为ip6tnl0时不显示
					if($value['sPortName']=='ip6tnl0'){
						continue;
					}
					//增加一列数据  is_enPort=1 代表管理口
					if(in_array($value['sPortName'],$enPort)){
						$value['is_enPort'] = 1;
					}else{
						$value['is_enPort'] = 0;
					}
					$isVirth 				= $this->CheckVirthNet($value['sPortName']);
					//如果为虚拟口则为1   否则为0
					if($isVirth){
						$value['is_virth']  = 1;
					}else{
						$value['is_virth']  = 0;
					}
					$isBridge				= $this->CheckBridgeNet($value['sPortName']);
					if($isBridge){
						$value['is_bridge'] = 1;
					}else{
						$value['is_bridge'] = 0;
					}
					$value['oldWorkMode'] 	= $value['sWorkMode'];
                    $value['iSshStatus']	= $this->checkSshStatus();
					array_push($netport_new_data,$value);
					unset($value);
				}
				$netport_data['data'] 	 	= $netport_new_data;
			}
			//判断是否启用HA 并且网口是否被占用  如被占用  该网口不允许编辑
			$config							= new TbConfig();
			$info							= $config->find("sName='HaSetting'");
			if(!empty($info['sValue']) && !empty($netport_data)){
				$setting 					= CJSON::decode($info['sValue']);
				if($setting['iTurn'] == "start"){
					$ha_model				= new TbDoubleHot();
					$c						= new CDbCriteria();
					$c->addCondition("iStatus = 1 ");
					$c->select				= "sNetCardName";
					$ha_array 				= $ha_model->findAll($c);
					//$port_array  HA网口存的数组 如 vEth0 vEth1
					$port_array 			= array();
					$netport_new_data		= array();
					foreach($ha_array as $item){
						array_push($port_array,$item->sNetCardName);
						unset($item);
					}
					foreach($netport_data['data'] as $value){
						//增加一列数据  haLock=1 代表HA锁定  不允许编辑
						if(in_array($value['sPortName'],$port_array)){
							$value['haLock'] = 1;
						}else{
							$value['haLock'] = 0;
						}
						$value['oldWorkMode'] =$value['sWorkMode'];
						array_push($netport_new_data,$value);
						unset($value);
					}
					$netport_data['data'] 	 = $netport_new_data;
				}
			}
			$this->showMessage(true,'操作成功',$netport_data);
		}else{
			$this->render('net_port');
		}
	}
	//判断是否ipv6隧道、nat64、pppoe、sslvpn的虚拟网口   如果为虚拟口则为true   否则为false
	public function CheckVirthNet($sPortName){
		//ipv6隧道
		if(strpos($sPortName,'GRE-')	!==false) return true;
		if(strpos($sPortName,'4over6-') !==false) return true;
		if(strpos($sPortName,'6to4-')	!==false) return true;
		if(strpos($sPortName,'ISATAP-') !==false) return true;
		//nat64
		if($sPortName=='nat64') 	return true;
		//ssl vpn
		if($sPortName=='tun0') 		return true;
		//pppoe
		if(strpos($sPortName,'ppp')!==false) return true;
		return false;
	}

	//判断是否bridge 桥设备   如果为桥设备则为true   否则为false
	public function CheckBridgeNet($sPortName){
		//ipv6隧道
		if(strpos($sPortName,'bridge')	!==false) return true;
		return false;
	}
	//编辑网络接口
	public function actionNetPortSave()
	{
		$aPost=(array)$this->getParam();
		if(Yii::app()->request->isPostRequest) {
			$tis_id                 = $aPost['tis_id'];unset($aPost['tis_id']);
			$param['hModel'] = new TbNetPort();
			//$param['hModel']->updateAll(array("sWorkMode"=>''),"sWorkMode='mirror'");
			$aData=array();
			// if(empty($aPost['iByManagement']))$aData['iByManagement']=0;
			if(empty($aPost['iWeb']))$aData['iWeb']=0;
			if(empty($aPost['iSSH']))$aData['iSSH']=0;
			if(empty($aPost['iAllowPing']))$aData['iAllowPing']=0;
			if(empty($aPost['iAllowTraceRoute']))$aData['iAllowTraceRoute']=0;
			if(empty($aPost['iAllowFlow']))$aData['iAllowFlow']=0;
			if(!isset($aPost['iStatus']))$aData['iStatus']=0;
			if(empty($aPost['iAllowLog']))$aData['iAllowLog']=0;

			//判断管理口IP地址是否为空
			if(!empty($aPost['iAllowLog'])){
				if(empty($aPost['iAllowPing'])&&empty($aPost['iWeb'])&&empty($aPost['iSSH']) && $aPost['is_enPort']!=1){
					// $this->showMessage(false,"选择日志必须选择'用于管理'或者'允许ping'");
					//$this->showMessage(false,"选择日志必须选择'WEBUI'或者'SSH'或'允许ping'");
					$this->showMessage(false,Yii::t('lang','选择日志必须选择')."'WEBUI'".Yii::t('lang','或')."'SSH'".Yii::t('lang','或')."'".Yii::t('lang','允许')."ping'");
				}
			}
			if($aPost['is_enPort'] == 1){
				// $aData['iByManagement']=1;
                $aData['iStatus']=1;
				$aData['iWeb']=1;
				$aData['iAllowPing']=1;
				//$aData['iSSH']=1;
				//$aData['iAllowTraceRoute']=1;
				if($aPost['sWorkMode']==='route' && empty($aPost['sIPV4Address'])) $this->showMessage(false,Yii::t('lang', '管理口IPV4地址不能为空'));
			}
			//校验IPV4地址  格式化IPV4地址
			if(isset($aPost['sIPV4Address']) && !empty($aPost['sIPV4Address'])){
				$targrt_ip =nl2br($aPost['sIPV4Address']);
				$targrt_ip = str_replace("<br />","",$targrt_ip);
				$aIPS=explode("\r\n",$targrt_ip);
				if(!empty($aIPS)){
					$aIPS = array_filter($aIPS);
					$aIPS = array_unique($aIPS);
				}
				$aData['sIPV4Address']=implode(",",$aIPS);
				foreach($aIPS as $k=>$v){
					if(!empty($v)){
						$vals = explode("/",$v);
						if(isset($vals[1]) && empty($vals[1])){
							$this->showMessage(false,$vals[0].Yii::t('lang','的掩码不能为空'));
						}else{
							if(!preg_match(Regexp::$ip4,$vals[0])){
								$this->showMessage(false,$vals[0]. Yii::t('lang', 'ip地址格式错误,不是正确的IPV4地址'));
							}
							$fipnum = explode(".",$vals[1]);
							if(count($fipnum)==4){
								$netmask =$this->getDecIp($vals[1]);
								if(!in_array($netmask,Yii::app()->params['CIDRDEC'])){
									$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
								}
							}else if(count($fipnum) ==1){
								if(is_numeric($fipnum[0])){
									if($fipnum[0]<0 || $fipnum[0]>32){
										$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
									}
								}else{
									$this->showMessage(false,$vals[0]. Yii::t('lang', 'ip地址格式错误,不是正确的IPV4地址'));
								}
							}else{
								$this->showMessage(false,$vals[0]. Yii::t('lang', 'ip地址格式错误,不是正确的IPV4地址'));
							}
						}
					}
				}
			}else{
				$aData['sIPV4Address']="";
			}
			//校验IPV6地址  格式化IPV6地址
			if(isset($aPost['sIPV6Address']) && !empty($aPost['sIPV6Address'])){
				$targrt_ip =nl2br($aPost['sIPV6Address']);
				$targrt_ip = str_replace("<br />","",$targrt_ip);
				$aIPS=explode("\r\n",$targrt_ip);
				if(!empty($aIPS) && is_array($aIPS)){
					foreach($aIPS as $item){
						if(!$this->CheckIPV6($item,2)){
							$this->showMessage(false,$item.' IPV6/前缀长度 输入有误');
						}
						unset($item);
					}
				}
				$aIPS = array_filter($aIPS);
				$aData['sIPV6Address']=implode(",",$aIPS);
			}else{
				$aData['sIPV6Address']="";
			}
			//检查不同网口不能存在相同IPV4的网段
			$this->vailSameNetWork($aData['sIPV4Address'],intval($aPost['id']));
			//检查不同网口不能存在相同IPV6的地址
			$this->vailSameNetWork($aData['sIPV6Address'],intval($aPost['id']),'find','sIPV6Address',$aPost['sPortName']);
			$param['other'] 		= "ip";
			$param['extData']		= $aData;
			$param['sCommand']		= "CMD_CONIFG_INTERFACE|edit";
			$param['sendOldData']	= false;
			$param['sLogDesc']		= '编辑网络接口成功';
			$param['returnData']	= 2;
			//判断是否聚合的接口  如果是同时修改聚合表中的数据
			if(strrpos($aPost['sPortName'],'bond') !== false){
				$PortAggre_model 	= new TbPortAggregation();
				$res = $PortAggre_model->find('sBridgeName=:sBridgeName',array(':sBridgeName'=>$aPost['sPortName']));
				if(!empty($res)){
					DBHelper::saveCommand("CMD_IFACE_AGGRE|del|".CJSON::encode($res));
					$res->sIPV4 	= $aData['sIPV4Address'];
					$res->sIPV6 	= $aData['sIPV6Address'];
					$res->save();
					DBHelper::saveCommand("CMD_IFACE_AGGRE|add|".CJSON::encode($res));
				}
			}
			//判断是否桥设备的接口  如果是同时修改桥设备表中的数据
			if(strrpos($aPost['sPortName'],'bridge') !== false){
				$model 						= new TbBridgeDevice();
				$res 						= $model->find('sBridgeName=:sBridgeName',array(':sBridgeName'=>$aPost['sPortName']));
				if(!empty($res)){
					DBHelper::saveCommand("CMD_BRIDGE_CONFIG|del|".CJSON::encode($res));
					$res->sIPV4 			= $aData['sIPV4Address'];
					$res->sIPV6 			= $aData['sIPV6Address'];
					// $res->iByManagement 	= empty($aPost['iByManagement']) 	? 0 : intval($aPost['iByManagement']);
					$res->iWeb             = empty($aPost['iWeb']) 	? 0 : intval($aPost['iWeb']);
					$res->iSSH             = empty($aPost['iSSH']) 	? 0 : intval($aPost['iSSH']);
					$res->iAllowPing       = empty($aPost['iAllowPing'])		? 0 : intval($aPost['iAllowPing']);
					$res->iAllowTraceRoute = empty($aPost['iAllowTraceRoute'])	? 0 : intval($aPost['iAllowTraceRoute']);
					$res->save();
					DBHelper::saveCommand("CMD_BRIDGE_CONFIG|add|".CJSON::encode($res));
				}

			}
			//判断是否VLAN的接口  如果是同时修改VLAN表中的数据
			if(strrpos($aPost['sPortName'],'.') !== false){
				$portName 			= explode('.',$aPost['sPortName']);
				if(count($portName) ==2){
					$model 				= new TbVlanDevice();
					$res 				= $model->find('sBindPort=:sBindPort',array(':sBindPort'=>$portName[0]));
					//VLAN的ID以及地址
					$old_sBindVlan 		= $res->sBindVlan;
					$old_sBindVlan_arr 	= explode('#',$old_sBindVlan);
					//编辑数据
					foreach($old_sBindVlan_arr as $key => $value){
						if(substr($value,0,strlen($portName[1])) == $portName[1]){
							$old_sBindVlan_arr[$key] = $portName[1].','.$aData['sIPV4Address'];
						}
					}
					$new_sBindVlan     	= implode('#',$old_sBindVlan_arr);
					//保存
					if(!empty($res)){
						DBHelper::saveCommand("CMD_VLAN|del|".CJSON::encode($res));
						$res->sBindVlan = $new_sBindVlan;
						$res->save();
						DBHelper::saveCommand("CMD_VLAN|add|".CJSON::encode($res));
					}
				}
			}
			//保存
			$aJson 					= DBHelper::saveData($param);
            //判断网口是否存在关联
            if(!empty($tis_id)){
                $this->RelationCommand_NetPort($tis_id);
            }
			echo CJSON::encode($aJson);
			Yii::app()->end();
		}else{
            $viewData           = array();
			$model              = new TbNetPort();
			$port               = $model->count("sWorkMode='mirror'");
            $viewData['port']   = $port;
			if($port>0){
				$res            = $model->find("sWorkMode ='mirror'");
				$msPortName     = $res->sPortName;
                $viewData['msPortName']   = $msPortName;
			}
			if(!empty($aPost['tis_id'])){
				$viewData['tis_id']   = $aPost['tis_id'];
			}else{
				$viewData['tis_id']   = '';
			}
			$this->render('netport_save',$viewData);
		}
	}

	/*
     *  统一配置方法  编辑有关联的定义对象  重新配置策略等
     */
	private function RelationCommand_NetPort($tis_id){
		if(!empty($tis_id) && strpos($tis_id,'|')!=false){
			//Searity,1,2,3|HA,9|Bridge,1|
			$tis_arr            = explode('|',$tis_id);
			$tis_arr            = array_filter($tis_arr);
			foreach($tis_arr as $item){
				$value_arr  = array();
				$first_val  = '';
				$value_arr  = explode(',',$item);
				if(!empty($value_arr))  $first_val  = array_shift($value_arr);
                //1.如果引用了HA
                if($first_val == 'HA'){
                    $command ="CMD_HOT_STANDBY";
                    DBHelper::saveCommand($command);
                    continue;
                }
                //2.如果引用了桥设备 Bridge
                if($first_val == 'Bridge'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbBridgeDevice::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_BRIDGE_CONFIG|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_BRIDGE_CONFIG|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_NIC_FLUSH";
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //3、如果引用了 网络设置-虚拟线
                if($first_val == 'Virtual'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbVirtualLine::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_SET_VIRTUAL_LINE|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_SET_VIRTUAL_LINE|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //4、判断是否被 流量管理-虚拟线路 引用
                if($first_val == 'FlowVirtual'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbFlowVirtualLine::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_VIRTUAL_LINE|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_VIRTUAL_LINE|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //5、判断是否被 冗余网口 引用
                if($first_val == 'PortAggregation'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbPortAggregation::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_IFACE_AGGRE|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_IFACE_AGGRE|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //6、判断是否被 镜像模式 引用
                if($first_val == 'Mirror'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbPortMirror::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_MIRROR|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_MIRROR|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //7、判断是否被 静态路由 引用
                if($first_val == 'StaticRoute'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbStaticRoute::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_STATICROUTE|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_STATICROUTE|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //8、判断是否被 策略路由 引用
                if($first_val == 'StrategyRoute'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbStrategyRoute::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_STATEGY_ROUTING|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_STATEGY_ROUTING|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //9、判断是否被 ISP路由 引用
                if($first_val == 'ISP'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbIspRoute::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_ISP_CONFIG|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_ISP_CONFIG|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //10、判断是否被 动态路由OSPF 引用 TbDynamicRoutePort
                if($first_val == 'OSPF'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbDynamicRoutePort::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_DYNAMICROUTING_OSPF|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_DYNAMICROUTING_OSPF|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //11、判断是否被 动态路由RIP 引用 TbDynamicRouteRipPort
                if($first_val == 'RIP'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbDynamicRouteRipPort::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_DYNAMICROUTING_RIP|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_DYNAMICROUTING_RIP|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //12、判断是否被 动态路由BGP 引用 TbDynamicRouteBgpPort
                if($first_val == 'BGP'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbDynamicRouteBgpPort::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_DYNAMICROUTING_BGP|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_DYNAMICROUTING_BGP|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //13、判断是否被 虚拟防火墙 引用 m_tbvirtualfw
                if($first_val == 'BGP'){
                    while($id = array_shift($value_arr)){
                        //发送管道命令
                        $result  = TbVirtualfw::model()->find('id=:id',array(':id'=>$id));
                        $command ="CMD_VIRTUAL_FW|del|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                        $command ="CMD_VIRTUAL_FW|add|".CJSON::encode($result);
                        DBHelper::saveCommand($command);
                    }
                    continue;
                }
                //14.如果引用了安全策略
                if($first_val == 'Searity'){
                    //只需要发送一条管道命令
                    $sCommand                                   = "CMD_SAFE_STRATEGY";
                    DBHelper::saveCommand($sCommand);
                    continue;
                }
				unset($item);unset($id);
			}
		}
	}
	/*
	 * @param  $sIPV4Address   string  一个或者多个IP地址的字符串  例:1.1.1.1/24,2.2.2.2/24
	 * @param  $data   		   mix(integer/string)整型或者是字符串   integer代表ID   string时代表sPortName或者多个sPortName的字符串(,隔开)
	 * @param  $tag			   string  一个标示 默认为find 当$tag=notIn时,代表使用addNotInCondition进行查询
	 * return  alert ·		   网口被占用时直接提示用户
	 */
	private function vailSameNetWork($sIPAddress,$data=0,$tag ='find',$type="sIPV4Address",$sPortName=''){
		if(!empty($sIPAddress)) {
			$hNetPort 			= new TbNetPort();
			$aNetPort 			= array();
			$hData				= array();
			$data				= is_numeric($data) ? intval($data) : $data;
			if(gettype($data)=='integer' && $tag=='find'){
				$hData 			= $hNetPort->findAll("id !=:id",array(':id'=>$data));
			}elseif(gettype($data) == 'string' && $tag=='find'){
				$hData 			= $hNetPort->findAll("sPortName<>:sPortName",array(':sPortName'=>$data));
			}elseif(gettype($data) == 'string' && $tag=='notIn'){
				$NotIn_criteria = new CDbCriteria;
				$NotIn_criteria->addNotInCondition('sPortName', explode(",", $data));
				$hData 			= $hNetPort->findAll($NotIn_criteria);
			}
			$hData 				= empty($hData) ? array() : $hData;
			if($type=="sIPV4Address"){
				foreach ($hData as $item) {
					!empty($item['sIPV4Address']) && array_push($aNetPort, $item['sIPV4Address']);
				}
				$sNetPort 			= implode(',', $aNetPort);
				$aNetPort 			= explode(',', $sNetPort);
				$aIPV4Address 		= explode(',', $sIPAddress);
				$vs = "";
				foreach($aIPV4Address as $k){
					foreach ($aNetPort as $item) {
						/*$rs = $this->isNetSome(trim($item," "),trim($k," "));
                        if($rs){
                            $this->showMessage(false,$k.' 与网口配置中'.$item.'同一网段');
                        }*/
						if(empty($item)) continue;
						$rs = $this->checkSameNet(trim($item," "),trim($k," "));
						if($rs===false){
							$this->showMessage(false,$k.' '.Yii::t('lang','与网口配置中').' '.$item.Yii::t('lang','同一网段'));
						}elseif($rs===0){
							$this->showMessage(false,$k.' '.Yii::t('lang','IP地址存在错误'));
						}
					}
				}
			}elseif($type=="sIPV6Address"){
				$aIPV6Address 		= explode(',', $sIPAddress);
                $result             = array();
                $aNetPortList       = TbNetPort::model()->sLanList();
                while($tmp_one = array_shift($aIPV6Address)){
                    $conflict       = $this->isNetPortIpv6AddrConflict($tmp_one,$sPortName);
                    if($conflict!==true){
                        $tmp        = explode(',',$conflict);
                        $tmp[1]     = $aNetPortList[$tmp[1]];
                        count($tmp)>1 && array_push($result, $tmp[1].'  '.$tmp[0]);
                    }
                }
				if(!empty($result)){
					$sSameIPV6 		= implode('<br>',array_unique($result));
					$this->showMessage(false,Yii::t('lang','与网口配置中地址发生冲突')." ".$sSameIPV6);
				}

			}
		}
	}
	//端口镜像头部-----------------------------------------------------
	public function actionGetHeaderTitlePortMirror(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				//array('sTitle'=>'观察口','data'=>'sCheckPort'),
				array('sTitle'=>Yii::t('lang','观察口'),'data'=>'sCheckPortLan'),
				array('sTitle'=>Yii::t('lang','镜像源'),'data'=>'sMirrorSource','sClass'=>'sMirrorSource','width'=>'600'),
				array('sTitle'=>Yii::t('lang','是否启用'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//端口镜像列表
	public function actionPortMirror(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] 	 	= new TbPortMirror();
			$param['returnData'] 	= 2;
			$result 				= DBHelper::getDataList($param);
			$tmp 					= array();
			$tmp2					= array();
			//将网口转化为sLan名称
			$aNetToLan = TbNetPort::model()->sLanList();
			//$aLanToNet = array_flip($aNetToLan);
			foreach($result['data'] as $item){
				$sCheckPort				= $item['sCheckPort'];
				$item['sCheckPortLan'] 	= $aNetToLan[$sCheckPort];

				$sMirrorSource 			= json_decode($item['sMirrorSource'],true);
				if(!empty($sMirrorSource)){
					foreach($sMirrorSource as $value){
						$value['sLan']	= $aNetToLan[$value['sPort']];
						array_push($tmp2,$value);unset($value);
					}
					$sMirrorSource		= $tmp2;
				}
				$item['sMirrorSource']	= json_encode($sMirrorSource);
				array_push($tmp,$item);
			}
			$result['data']				= $tmp;
			$this->showMessage(true,Yii::t('lang','操作成功'),$result);
		}else{
			$this->render('port_mirror');
		}
	}
	//编辑端口镜像
	public function actionPortMirrorSave()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbPortMirror();
		if(Yii::app()->request->isPostRequest) {
			$aData=array();
			if(isset($aPost['sPort'])) {
				$aItem=array();
				foreach ($aPost['sPort'] as $k => $v) {
					$aFiveGroup=array('sProtocol'=>$aPost['sProtocol'][$k],'sSourceIP'=>$aPost['sSourceIP'][$k],'sTargetIP'=>$aPost['sTargetIP'][$k],'sSourcePort'=>$aPost['sSourcePort'][$k],'sTargetPort'=>$aPost['sTargetPort'][$k]);
					$aItem[] = array('sPort'=>$v,'sDirection'=>$aPost['sDirection'][$k],'sRule'=>$aPost['sRule'][$k],'sFiveGroup'=>$aFiveGroup);
				}
				$aData['sMirrorSource']=CJSON::encode($aItem);
			}
			$param['extData']=$aData;
			$param['sCommand']=!empty($aPost['id'])?"CMD_MIRROR|edit":"CMD_MIRROR|add";
			$param['sLogDesc']='编辑端口镜像成功';
			DBHelper::saveData($param);
		}else{
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			$c2 = new CDbCriteria();
			$c->addCondition("sWorkMode='mirror'");
			$viewData['netPortList']=$netPortModel->findAll($c);
			$data = $netPortModel->find($c);
			$sPortName = $data->sPortName;
			$condition = "sPortName !='".$sPortName."'";
			$c2->addCondition($condition);
			$viewData['netPortAll']=$netPortModel->findAll($c2);
			$this->render('port_mirror_save',$viewData);
		}
	}
	//虚拟线头部-----------------------------------------------------
	public function actionGetHeaderTitleVirtualLine(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				//array('sTitle'=>'虚拟网线接口一','data'=>'sVirtualPortOne'),
				//array('sTitle'=>'虚拟网线接口二','data'=>'sVirtualPortTwo'),
				array('sTitle'=>Yii::t('lang','虚拟网线接口一'),'data'=>'sVirtualPortOneLan','width'=>'25%'),
				array('sTitle'=>Yii::t('lang','虚拟网线接口二'),'data'=>'sVirtualPortTwoLan','width'=>'25%'),
				array('sTitle'=>Yii::t('lang','描述'),'data'=>'sDesc'),
				array('sTitle'=>Yii::t('lang','是否启用'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//虚拟线列表
	public function actionVirtualLine(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] 		= new TbVirtualLine();
			$param['returnData'] 	= 2;
			$result 		 		= DBHelper::getDataList($param);
			$result['data']			= TbNetPort::model()->setLanListMulti($result['data'],'sVirtualPortOne,sVirtualPortTwo','Lan');
			$this->showMessage(true,'success',$result);
		}else{
			$this->render('virtual_line');
		}
	}
	//编辑虚拟线
	public function actionVirtualLineSave()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbVirtualLine();
		if(Yii::app()->request->isPostRequest) {
			if(!empty($aPost['sVirtualPortOne']) && !empty($aPost['sVirtualPortTwo'])){
				if($aPost['sVirtualPortOne'] == $aPost['sVirtualPortTwo']){
					$aJson['success'] = false;
					$aJson['msg'] = Yii::t('lang','两个接口不能一样');
					echo CJSON::encode($aJson);
					exit();
				}
			}
			$aData=array();
			if(empty($aPost['iStatus']))$aData['iStatus']=1;
			$param['extData']=$aData;
			$param['sCommand']=!empty($aPost['id'])?"CMD_SET_VIRTUAL_LINE|edit":"CMD_SET_VIRTUAL_LINE|add";
			$param['sLogDesc']='编辑虚拟线成功';
			DBHelper::saveData($param);
		}else{
			//已使用的网口
			$condit=new CDbCriteria();
			if(!empty($aPost['mid'])){
				//$condit->addCondition("id<>".$aPost['mid']);
				$condit->addCondition("id<>:id");
				$condit->params[':id'] = $aPost['mid'];
			}
			$exitsPort=$param['hModel']->findAll($condit);
			$exist=array();
			foreach($exitsPort as $port){
				$exist[]=$port['sVirtualPortOne'];
				$exist[]=$port['sVirtualPortTwo'];
			}
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			$c->addCondition("sWorkMode='virtual'");
			$c->addNotInCondition("sPortName",$exist);
			$viewData['netPortList']=$netPortModel->findAll($c);

			$this->render('virtualline_save',$viewData);
		}
	}
	//桥设备头部-----------------------------------------------------
	public function actionGetHeaderTitleBridgeDevice(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang','设备名称'),'data'=>'sBridgeName'),
				array('sTitle'=>Yii::t('lang','IP地址/掩码'),'data'=>'sIPV4','sClass'=>'sIPV4'),
				array('sTitle'=>Yii::t('lang','绑定接口列表'),'data'=>'sBindDevicesLan'),
				array('sTitle'=>Yii::t('lang','是否启用'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//桥设备列表
	public function actionBridgeDevice(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbBridgeDevice();
			$param['returnData'] = 2;
			$dataList = DBHelper::getDataList($param);

			$NetPortModel = new TbNetPort();
			$sLan = $NetPortModel->sLanList();
			foreach($dataList['data'] as $key=>$item){
				$sBindDevices = explode(',',$item['sBindDevices']);
				$sBindDevices = array_flip($sBindDevices);
				$sBindDevicesLan = array_intersect_key( $sLan , $sBindDevices);
				$dataList['data'][$key]['sBindDevicesLan'] = implode(',',$sBindDevicesLan);
			}
			echo CJSON::encode($dataList);
			Yii::app()->end();

		}else{
			$this->render('bridge_device');
		}
	}
	//编辑桥设备
	public function actionBridgeDeviceSave()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbBridgeDevice();
		if(Yii::app()->request->isPostRequest) {
			$aPost['sIPV4']					= trim($aPost['sIPV4']);
			$aPost['sIPV6']					= trim($aPost['sIPV6']);
			$aPost['id']					= intval($aPost['id']);
			$sPortName       				= trim('bridge'.$aPost['sBridgeName']);
			if(empty($aPost['sIPV4']) && empty($aPost['sIPV6'])){
				if($aPost['iSSH'] || $aPost['iWeb'] || $aPost['iAllowPing'] || $aPost['iAllowTraceRoute']){
					$this->showMessage(false,Yii::t('lang','请填写IP地址或者请勿勾选WEBUI、SSH、允许PING、允许Traceroute').'');
				}
			}
			//判断设备是否同名
			if(empty($aPost['id'])){
				if($param['hModel']->findByAttributes(array('sBridgeName'=>$sPortName)))
					$this->showMessage(false,Yii::t('lang','设备名称已存在,请重新填写'));
			}else{
				if($param['hModel']->findByAttributes(array('sBridgeName'=>$sPortName),"id<>:id",array(":id"=>$aPost['id']))){
					$this->showMessage(false,Yii::t('lang','设备名称已存在,请重新填写'));
				}
			}
			/*if(!empty($aPost['sIPV4'])){
				if(!$this->CheckIPV4($aPost['sIPV4'],1)){
					$this->showMessage(false,'IPV4地址输入有误');
				}

			}
			if(!empty($aPost['sIPV6'])){
				if(!$this->CheckIPV6($aPost['sIPV6'],1)) $this->showMessage(false,'IPV6地址输入有误,请重新输入');
			}*/
			$portSize=explode(",",$aPost['sBindDevices']);
			if(count($portSize)<2){
				$aJson['success']=false;
				$aJson['msg']=Yii::t('lang','所选网口数必须为两个以上（含两个）');
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			$aData=array();
			//判断IP地址输入是否正确  并将以','隔开存进数据库
			if(isset($aPost['sIPV4']) && !empty($aPost['sIPV4'])){
				//$limit_long		= strlen($aPost['sIPV4']);
				//if($limit_long>500) $this->showMessage(false,'输入的IP地址数超过限制');
				$targrt_ip 		= nl2br($aPost['sIPV4']);
				$targrt_ip 		= str_replace("<br />","",$targrt_ip);
				$aIPS			= explode("\r\n",$targrt_ip);
				$aIPS 			= array_filter($aIPS);
				$aData['sIPV4']	= implode(",",$aIPS);
				foreach($aIPS as $k=>$v){
					if(!empty($v)){
						$vals = explode("/",$v);
						if(isset($vals[1]) && empty($vals[1])){
							$this->showMessage(false,$vals[0].' '.Yii::t('lang','的掩码不能为空'));
						}else{
							if(!preg_match(Regexp::$ip4,$vals[0])){
								$this->showMessage(false,$vals[0].' '.Yii::t('lang','IPV4格式错误'));
							}
							$fipnum = explode(".",$vals[1]);
							if(count($fipnum)==4){
								$netmask =$this->getDecIp($vals[1]);
								if(!in_array($netmask,Yii::app()->params['CIDRDEC'])){
									$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
								}
							}else if(count($fipnum) ==1){
								if(is_numeric($fipnum[0])){
									if($fipnum[0]<0 || $fipnum[0]>32){
										$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
									}
								}else{
									$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
								}
							}else{
								$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
							}
							//校验是否网段
							$addr_ip                            = $vals[0];
							$addr_mask                          = $vals[1];
							//判断掩码是否为数值 例/24  如果为false则为数值
							$pos                                = strpos($addr_mask,'.');
							if($pos == false){
								$addr_mask_num                  = intval($addr_mask);
								$addr_mask                      = '';
								$addr_mask                      = str_pad($addr_mask,$addr_mask_num,'1');
								$addr_mask                      = str_pad($addr_mask,32,'0');
								$addr_mask                      = bindec($addr_mask);
								$addr_mask_int                  = $addr_mask;
								//将/24转为 255.255.255.0
								//$addr_mask                      = long2ip($addr_mask);
							}else{
								$addr_mask_int                  = ip2long($addr_mask);
							}
							//判断掩码是否合法
							if(($addr_mask_int|($addr_mask_int-1)) != 0xFFFFFFFF){
								$this->showMessage(false,''.Yii::t('lang','掩码输入有误'));
							}
							//将IP地址转为10进制数
							$addr_ip_int                        = ip2long($addr_ip);
							//取反，此处得到的是补码
							$_addr_mask_int                     = ~$addr_mask_int;
							//进行 "与" 运算   如果得到的是0代表网段/MASK填写正确   如果不为0则代表不正确
							$mask_correct                       = $_addr_mask_int & $addr_ip_int;
							if($mask_correct ==0) $this->showMessage(false,$vals[0].' '.Yii::t('lang','请输入正确的IP地址'));
						}

					}
					unset($k);unset($v);
				}
			}else{
				$aData['sIPV4']="";
			}
			//判断是否同一网段
			if(empty($aPost['id'])){
				if(!empty($aData['sIPV4'])){
					$this->vailSameNetWork($aData['sIPV4'],$sPortName);
				}
			}else{
				if(!empty($aData['sIPV4'])){
					$oldNetportName 			= TbBridgeDevice::model()->find("id=:id",array(":id"=>$aPost['id']))->sBridgeName;
					$netportId 					= TbNetPort::model()->find("sPortName=:sPortName",array(':sPortName'=>$oldNetportName))->id;
					$this->vailSameNetWork($aData['sIPV4'],intval($netportId));
				}
			}

			//判断IPV6地址输入是否正确  并将以','隔开存进数据库
			if(isset($aPost['sIPV6']) && !empty($aPost['sIPV6'])){

				//$limit_long		= strlen($aPost['sIPV6']);
				//if($limit_long>500) $this->showMessage(false,'输入的IP地址数超过限制');
				$targrt_ip 		= nl2br($aPost['sIPV6']);
				$targrt_ip 		= str_replace("<br />","",$targrt_ip);
				$aIPS			= explode("\r\n",$targrt_ip);
				$aIPS 			= array_filter($aIPS);
				$aData['sIPV6'] = implode(",",$aIPS);
				foreach($aIPS as $k=>$v){
					if(!empty($v)){
						if(!$this->CheckIPV6($v,2)){
							$this->showMessage(false,$v.' '.Yii::t('lang','IPV6格式输入有误'));
						}
					}
					unset($k);unset($v);
				}
			}else{
				$aData['sIPV6']	= "";
			}

			if(empty($aPost['iStatus']))$aData['iStatus']=1;
			// if(empty($aPost['iByManagement']))$aData['iByManagement']=0;
			if(empty($aPost['iWeb']))$aData['iWeb']=0;
			if(empty($aPost['iSSH']))$aData['iSSH']=0;
			if(empty($aPost['iAllowPing']))$aData['iAllowPing']=0;
			if(empty($aPost['iAllowTraceRoute']))$aData['iAllowTraceRoute']=0;
			if(empty($aPost['iAllowLog']))$aData['iAllowLog']=0;
			$aData['sBridgeName']="bridge".$aPost['sBridgeName'];
			$param['extData']=$aData;
			$param['sCommand']=!empty($aPost['id'])?"CMD_BRIDGE_CONFIG|edit":"CMD_BRIDGE_CONFIG|add";
			$param['sLogDesc']='编辑桥设备成功';
			$param['returnData']=2;
			$aJson 				= DBHelper::saveData($param);
			//更新网口配置表
			$sPortName       					= trim('bridge'.$aPost['sBridgeName']);
			$attributes                         = array();
			// $attributes['iByManagement']        = empty($aPost['iByManagement']) 	? 0 :intval($aPost['iByManagement']);
			$attributes['iWeb']             = empty($aPost['iWeb']) 	? 0 :intval($aPost['iWeb']);
			$attributes['iSSH']             = empty($aPost['iSSH']) 	? 0 :intval($aPost['iSSH']);
			$attributes['iAllowPing']       = empty($aPost['iAllowPing']) 	 	? 0 :intval($aPost['iAllowPing']);
			$attributes['iAllowTraceRoute'] = empty($aPost['iAllowTraceRoute']) ? 0 :intval($aPost['iAllowTraceRoute']);
			TbNetPort::model()->updateAll($attributes,"sPortName=:sPortName",array(':sPortName'=>$sPortName));
			DBHelper::saveCommand("CMD_NIC_FLUSH");
			$this->showMessage(true,'',$aJson);
		}else{
			//已使用的网口
			$condit=new CDbCriteria();
			$condit->select="sBindDevices";
			$exitsPort=$param['hModel']->findAll($condit);
			$sNameStr='';
			foreach($exitsPort as $port){
				$sNameStr.=$port['sBindDevices'].',';
			}
			if($sNameStr)$sNameStr=substr($sNameStr,0,-1);
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			$c->addCondition("sWorkMode='bridge'");
			$c->addCondition("iStatus=1");
			$c->addNotInCondition("sPortName",explode(',',$sNameStr));
			$viewData['netPortList']=$netPortModel->findAll($c);
			$this->render('bridgedevice_save',$viewData);
		}
	}

	//拨号设备头部-----------------------------------------------------
	public function actionGetHeaderTitleDialDevice(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang','拨号设备名称'),'data'=>'sDialname','minWidth'=>'120'),
				array('sTitle'=>Yii::t('lang','获取的IP地址和掩码'),'data'=>'sIP','minWidth'=>'150'),
				//array('sTitle'=>'绑定设备','data'=>'sBindPort'),
				array('sTitle'=>Yii::t('lang','绑定设备'),'data'=>'sBindPortLan'),
				array('sTitle'=>Yii::t('lang','是否启用'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//拨号设备列表
	public function actionDialDevice(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbDialDevice();
			$param['returnData'] = 2;
			$dataList = DBHelper::getDataList($param);

			$NetPortModel = new TbNetPort();
			$dataList['data'] = $NetPortModel->setLanList($dataList['data'] , 'sBindPort' , 'sBindPortLan');

			echo CJSON::encode($dataList);
			Yii::app()->end();

		}else{
			$this->render('dial_device');
		}
	}
	//编辑拨号设备
	public function actionDialDeviceSave()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbDialDevice();
		if(Yii::app()->request->isPostRequest) {

			$aData=array();
			//if(empty($aPost['iStatus']))$aData['iStatus']=1;
			$aData['iStatus'] = empty($aPost['iStatus']) ? 0 :1;
			if(empty($aPost['iByManagement']))$aData['iByManagement']=0;
			if(empty($aPost['iAllowPing']))$aData['iAllowPing']=0;
			if(empty($aPost['iAllowTraceRoute']))$aData['iAllowTraceRoute']=0;
			$param['extData']=$aData;
			$c=new CDbCriteria();
			$c->addCondition("sUserName=:sUserName");
			//$c->addCondition("sUserName='".$aPost['sUserName']."'");
			$c->params[':sUserName'] = $aPost['sUserName'];
			if(!empty($aPost['id'])){
				$before=$param['hModel']->findByPk($aPost['id']);
				$befName=$before['sUserName'];
				$param['sCommand']="CMD_DIAL|edit|".$befName.','.$aPost['sUserName'];
				//$c->addCondition("id<>".$aPost['id']);
				$c->addCondition("id<>:id");
				$c->params[':id'] = $aPost['id'];
			}else{
				$param['sCommand']="CMD_DIAL|add|".$aPost['sUserName'];
			}
			$exist=$param['hModel']->find($c);
			//使用已存在用户名
			if($exist){
				$aJson['success']=false;
				$aJson['msg']=Yii::t('lang','用户名已存在，请重新填写');
				echo CJSON::encode($aJson);
				Yii::app()->end();
				exit;
			}
			$param['sLogDesc']='编辑拨号设备成功';
			DBHelper::saveData($param);
		}else{
			//已使用的网口
			$condit=new CDbCriteria();
			$condit->select="sBindPort";
			if(!empty($aPost['mid'])){
				//$condit->addCondition("id<>".$aPost['mid']);
				$condit->addCondition("id<>:id");
				$condit->params[':id'] = $aPost['mid'];
			}
			$exitsPort=$param['hModel']->findAll($condit);
			$exist=array();
			foreach($exitsPort as $port){
				$exist[]=$port['sBindPort'];
			}
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			//$c->addCondition("sWorkMode='route'");
			$c->addCondition("iStatus=1");
			$c->addNotInCondition("sPortName",$exist);
			$viewData['netPortList']=$netPortModel->findAll($c);

			$this->render('dialdevice_save',$viewData);
		}
	}
	//端口聚合头部-----------------------------------------------------
	public function actionGetHeaderTitlePortAggregation(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang','设备名称'),'data'=>'sBridgeName'),
				array('sTitle'=>Yii::t('lang','IP地址/掩码'),'data'=>'sIPV4','sClass'=>'sIPV4'),
			/*array('sTitle'=>'网关','data'=>'sIPV4Gw','width'=>'120px'),
            array('sTitle'=>'工作模式','data'=>'sWorkMode'),
            array('sTitle'=>'IP地址获取','data'=>'sGetIP','minWidth'=>'120'),*/
				array('sTitle'=>Yii::t('lang','绑定接口列表'),'data'=>'sBindDevices','minWidth'=>'220'),
				array('sTitle'=>Yii::t('lang','是否启用'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//端口聚合列表
	public function actionPortAggregation(){



		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbPortAggregation();
			$param['returnData'] = 2;
			$dataList = DBHelper::getDataList($param);
			$dataList['data'] = CJSON::decode(CJSON::encode($dataList['data']));

			//获取sPortName的sLan名称
			$netPortModel = new TbNetPort();
			$dataList['data'] = $netPortModel->setLanList($dataList['data'], 'sBindDevices' , 'sBindDevices');

			echo CJSON::encode($dataList);
			Yii::app()->end();
		}else{

			$this->render('port_aggregation');
		}
	}
	//编辑端口聚合
	public function actionPortAggregationSave()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbPortAggregation();
		if(Yii::app()->request->isPostRequest) {
			//对001这种数字进行判断并返回提示
			if(strlen($aPost['sBridgeName'])>1){
				if(!preg_match("/^[1-9]\d*$/",$aPost['sBridgeName'])){
					$this->showMessage(false,Yii::t('lang', Yii::t('lang','名称请输入一个正整数')));
				}
				$num=(int)trim($aPost['sBridgeName'])<10?str_ireplace("0","",trim($aPost['sBridgeName'])):trim($aPost['sBridgeName']);
			}else{
				$num = $aPost['sBridgeName'];
			}
			//检测重名
			$name = "bond" . trim($num);
			if(empty($aPost['id'])) {
				$exist = $param['hModel']->count("sBridgeName=:sBridgeName",array(':sBridgeName'=>$name));
				if($exist>0) {
					$this->showMessage(false,Yii::t('lang', Yii::t('lang','名称已存在，请重新填写')));
				}
			}else{
				$aPost['id']		 		= intval($aPost['id']);
				$exist = $param['hModel']->count("sBridgeName=:sBridgeName AND id<>:id",array(':sBridgeName'=>$name,':id'=>$aPost['id']));
				if ($exist>0) {
					$this->showMessage(false,Yii::t('lang', Yii::t('lang','名称已存在，请重新填写')));
				}
			}
			//检测选择网口的数量
			$portSize=explode(",",$aPost['sBindDevices']);
			if(count($portSize)<2){
				$aJson['success']=false;
				$aJson['msg']=Yii::t('lang','所选网口数必须为两个以上（含两个）');
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			$aData=array();
			//判断IP地址输入是否正确  并将以','隔开存进数据库
			if(isset($aPost['sIPV4']) && !empty($aPost['sIPV4'])){
				//$limit_long		= strlen($aPost['sIPV4']);
				//if($limit_long>500) $this->showMessage(false,'输入的IP地址数超过限制');
				$targrt_ip 		= nl2br($aPost['sIPV4']);
				$targrt_ip 		= str_replace("<br />","",$targrt_ip);
				$aIPS			= explode("\r\n",$targrt_ip);
				$aIPS 			= array_filter($aIPS);
				$aData['sIPV4']	= implode(",",$aIPS);
				foreach($aIPS as $k=>$v){
					if(!empty($v)){
						$vals = explode("/",$v);
						if(isset($vals[1]) && empty($vals[1])){
							$this->showMessage(false,$vals[0].' '.Yii::t('lang','的掩码不能为空'));
						}else{
							if(!preg_match(Regexp::$ip4,$vals[0])){
								$this->showMessage(false,$vals[0].Yii::t('lang', 'IPV4格式错误'));
							}
							$fipnum = explode(".",$vals[1]);
							if(count($fipnum)==4){
								$netmask =$this->getDecIp($vals[1]);
								if(!in_array($netmask,Yii::app()->params['CIDRDEC'])){
									$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
								}
							}else if(count($fipnum) ==1){
								if(is_numeric($fipnum[0])){
									if($fipnum[0]<0 || $fipnum[0]>32){
										$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
									}
								}else{
									$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
								}
							}else{
								$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
							}
							//校验是否网段
							$addr_ip                            = $vals[0];
							$addr_mask                          = $vals[1];
							//判断掩码是否为数值 例/24  如果为false则为数值
							$pos                                = strpos($addr_mask,'.');
							if($pos == false){
								$addr_mask_num                  = intval($addr_mask);
								$addr_mask                      = '';
								$addr_mask                      = str_pad($addr_mask,$addr_mask_num,'1');
								$addr_mask                      = str_pad($addr_mask,32,'0');
								$addr_mask                      = bindec($addr_mask);
								$addr_mask_int                  = $addr_mask;
								//将/24转为 255.255.255.0
								//$addr_mask                      = long2ip($addr_mask);
							}else{
								$addr_mask_int                  = ip2long($addr_mask);
							}
							//判断掩码是否合法
							if(($addr_mask_int|($addr_mask_int-1)) != 0xFFFFFFFF){
								$this->showMessage(false, Yii::t('lang', '掩码输入有误'));
							}
							//将IP地址转为10进制数
							$addr_ip_int                        = ip2long($addr_ip);
							//取反，此处得到的是补码
							$_addr_mask_int                     = ~$addr_mask_int;
							//进行 "与" 运算   如果得到的是0代表网段/MASK填写正确   如果不为0则代表不正确
							$mask_correct                       = $_addr_mask_int & $addr_ip_int;
							if($mask_correct ==0) $this->showMessage(false,$vals[0]. Yii::t('lang', '请输入正确的IP地址'));
						}

					}
					unset($k);unset($v);
				}
			}else{
				$aData['sIPV4']="";
			}
			//判断是否同一个网段
			if(empty($aPost['id'])) {
				if(!empty($aData['sIPV4'])){
					$this->vailSameNetWork($aData['sIPV4'],$name);
				}
			}else{
				if(!empty($aData['sIPV4'])){
					$oldNetportName 			= TbPortAggregation::model()->find("id=:id",array(":id"=>$aPost['id']))->sBridgeName;
					$netportId 					= TbNetPort::model()->find("sPortName=:sPortName",array(':sPortName'=>$oldNetportName))->id;
					$this->vailSameNetWork($aData['sIPV4'],intval($netportId));
				}
			}

			//判断IPV6地址输入是否正确  并将以','隔开存进数据库
			if(isset($aPost['sIPV6']) && !empty($aPost['sIPV6'])){
				//$limit_long		= strlen($aPost['sIPV6']);
				//if($limit_long>500) $this->showMessage(false,'输入的IP地址数超过限制');
				$targrt_ip 		= nl2br($aPost['sIPV6']);
				$targrt_ip 		= str_replace("<br />","",$targrt_ip);
				$aIPS			= explode("\r\n",$targrt_ip);
				$aIPS 			= array_filter($aIPS);
				$aData['sIPV6'] = implode(",",$aIPS);
				foreach($aIPS as $k=>$v){
					if(!empty($v)){
						if(!$this->CheckIPV6($v,2)){
							$this->showMessage(false,$v.' '.Yii::t('lang','IPV6格式输入有误'));
						}
					}
					unset($k);unset($v);
				}
			}else{
				$aData['sIPV6']	= "";
			}
			if(empty($aPost['iStatus']))$aData['iStatus']=1;
			if(empty($aPost['iByManagement']))$aData['iByManagement']=0;
			if(empty($aPost['iAllowPing']))$aData['iAllowPing']=0;
			if(empty($aPost['iAllowTraceRoute']))$aData['iAllowTraceRoute']=0;
			$aData['sBridgeName']="bond".$num;
			$param['extData']=$aData;
			$param['sCommand']=!empty($aPost['id'])?"CMD_IFACE_AGGRE|edit":"CMD_IFACE_AGGRE|add";
			$param['sLogDesc']='编辑端口聚合成功';
			$param['returnData']=2;
			$aJson 				= DBHelper::saveData($param);
			DBHelper::saveCommand('CMD_NIC_FLUSH');
			$this->showMessage(true,Yii::t('lang','操作成功'),$aJson);

		}else{
			//已使用的网口
			$condit=new CDbCriteria();
			$condit->select="sBindDevices";
			$exitsPort=$param['hModel']->findAll($condit);
			$sNameStr='';
			foreach($exitsPort as $port){
				$sNameStr.=$port['sBindDevices'].',';
			}
			if($sNameStr)$sNameStr=substr($sNameStr,0,-1);

			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			$c->addCondition("sWorkMode='redundancy'");
			$c->addCondition("iStatus=1");
			$c->addNotInCondition("sPortName",explode(',',$sNameStr));
			$viewData['netPortList']=$netPortModel->findAll($c);

			//已使用sLan名称
			$sNameArr = explode(',' , $sNameStr);
			$sql = 'select sPortName,sLan from m_tbnetport where sPortName in ("'.implode('","' , $sNameArr).'")';
			$sNamesLan = Yii::app()->db->createCommand($sql)->queryAll(true);
			foreach($sNamesLan as $val){
				$sLan[$val['sPortName']] = $val['sLan'];
			}

            //获取sPortName的sLan名称
            $netPortModel = new TbNetPort();
            $sLan = $netPortModel->sLanList();
            $viewData['sLan'] = $sLan;
            $viewData['sLan_flip'] 	= CJSON::encode(array_flip($sLan));

			$this->render('port_aggregation_save',$viewData);
		}
	}
	//vlan设备头部-----------------------------------------------------
	public function actionGetHeaderTitleVlanDevice(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang','设备名称'),'data'=>'sVlanName'),
				array('sTitle'=>Yii::t('lang','绑定设备'),'data'=>'sBindsLan'),
				array('sTitle'=>'VLAN ID','data'=>'sBindVlan','sClass'=>'sBindVlan','width'=>'30%'),
				array('sTitle'=>Yii::t('lang','是否启用'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//vlan设备列表
	public function actionVlanDevice(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbVlanDevice();
			$param['returnData'] = 2;
			$dataList = DBHelper::getDataList($param);

			//sLan绑定设备名称处理
			$NetPortModel = new TbNetPort();
			$dataList['data'] = $NetPortModel->setLanList($dataList['data'] , 'sBindPort' , 'sBindsLan');
			echo CJSON::encode($dataList);
			Yii::app()->end();
		}else{
			$this->render('vlan_device');
		}
	}
	//编辑vlan设备
	public function actionVlanDeviceSave()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbVlanDevice();
		if(Yii::app()->request->isPostRequest) {
			$aPost['id']				= intval($aPost['id']);
			$aPost['sVlanName']			= trim($aPost['sVlanName']);
			$aData						= array('sBindVlan'=>'');
			$Vlan_E_String				= '';
			if(empty($aPost['iStatus']))$aData['iStatus']=0;
			//判断设备是否同名
			if(empty($aPost['id'])){
				if($param['hModel']->findByAttributes(array('sVlanName'=>$aPost['sVlanName'])))
					$this->showMessage(false,Yii::t('lang','设备名称已存在,请重新填写'));
			}else{
				if($param['hModel']->findByAttributes(array('sVlanName'=>$aPost['sVlanName']),"id<>:id",array(":id"=>$aPost['id']))){
					$this->showMessage(false,Yii::t('lang','设备名称已存在,请重新填写'));
				}
				$oldNetportName 			= TbVlanDevice::model()->find("id=:id",array(":id"=>$aPost['id']))->sBindVlan;
				$oldVlan_ID					= array();
				//获取此ID原本的vlan id
				if(!empty($oldNetportName)){
					$oldNetportName				= explode('#',$oldNetportName);
					while($res = array_shift($oldNetportName)){
						array_push($oldVlan_ID,$aPost['sBindPort'].'.'.array_shift(explode(',',$res)));
					}
				}
			}
			if(!empty($aPost['sBindVlan_S'])) {
				foreach ($aPost['sBindVlan_S'] as $key => $item) {
					$sBindVlan_E 		= $aPost['sBindVlan_E'][$key];
					//判断IP地址输入是否正确  并将以','隔开存进数据库
					if(isset($sBindVlan_E) && !empty($sBindVlan_E)){
						//$limit_long		= strlen($sBindVlan_E);
						//if($limit_long>500) $this->showMessage(false,'输入的IP地址数超过限制');
						$targrt_ip 		= nl2br($sBindVlan_E);
						$targrt_ip 		= str_replace("<br />","",$targrt_ip);
						$aIPS			= explode("\r\n",$targrt_ip);
						$aIPS 			= array_unique(array_filter($aIPS));
						$ip_string		= implode(",",$aIPS);
						$Vlan_E_String .= $ip_string.',';
						foreach($aIPS as $k=>$v){
							if(!empty($v)){
								$vals = explode("/",$v);
								if(isset($vals[1]) && empty($vals[1])){
									$this->showMessage(false,$vals[0].' '.Yii::t('lang','的掩码不能为空'));
								}else{
									if(!preg_match(Regexp::$ip4,$vals[0])){
										$this->showMessage(false,$vals[0].' '.Yii::t('lang','IPV4格式错误'));
									}
									$fipnum = explode(".",$vals[1]);
									if(count($fipnum)==4){
										$netmask =$this->getDecIp($vals[1]);
										if(!in_array($netmask,Yii::app()->params['CIDRDEC'])){
											$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
										}
									}else if(count($fipnum) ==1){
										if(is_numeric($fipnum[0])){
											if($fipnum[0]<0 || $fipnum[0]>32){
												$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
											}
										}else{
											$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
										}
									}else{
										$this->showMessage(false,$vals[0].Yii::t('lang', '的掩码输入有误'));
									}
									//校验是否网段
									$addr_ip                            = $vals[0];
									$addr_mask                          = $vals[1];
									//判断掩码是否为数值 例/24  如果为false则为数值
									$pos                                = strpos($addr_mask,'.');
									if($pos == false){
										$addr_mask_num                  = intval($addr_mask);
										$addr_mask                      = '';
										$addr_mask                      = str_pad($addr_mask,$addr_mask_num,'1');
										$addr_mask                      = str_pad($addr_mask,32,'0');
										$addr_mask                      = bindec($addr_mask);
										$addr_mask_int                  = $addr_mask;
										//将/24转为 255.255.255.0
										//$addr_mask                      = long2ip($addr_mask);
									}else{
										$addr_mask_int                  = ip2long($addr_mask);
									}
									//判断掩码是否合法
									if(($addr_mask_int|($addr_mask_int-1)) != 0xFFFFFFFF){
										$this->showMessage(false,''.Yii::t('lang','掩码输入有误'));
									}
									//将IP地址转为10进制数
									$addr_ip_int                        = ip2long($addr_ip);
									//取反，此处得到的是补码
									$_addr_mask_int                     = ~$addr_mask_int;
									//进行 "与" 运算   如果得到的是0代表网段/MASK填写正确   如果不为0则代表不正确
									$mask_correct                       = $_addr_mask_int & $addr_ip_int;
									if($mask_correct ==0) $this->showMessage(false,$vals[0].' '.Yii::t('lang','请输入正确的IP地址'));
								}

							}
							unset($k);unset($v);
						}
					}else{
						$ip_string="";
					}
					$aData['sBindVlan'] .= $item . "," . $ip_string."#";
					unset($key);unset($item);
				}

				if($aData['sBindVlan'])$aData['sBindVlan']=substr($aData['sBindVlan'],0,-1);
			}
			$Vlan_E_String								  = substr($Vlan_E_String,0,-1);
			//判断是否同一网段
			if(empty($aPost['id'])){
				if(!empty($Vlan_E_String)){
					$this->vailSameNetWork($Vlan_E_String);
				}
			}else{
				if(!empty($Vlan_E_String)){
					$this->vailSameNetWork($Vlan_E_String,implode(',',$oldVlan_ID),'notIn');
				}
			}
			$param['extData']=$aData;
			$param['sCommand']=!empty($aPost['id'])?"CMD_VLAN|edit":"CMD_VLAN|add";
			$param['sLogDesc']='编辑vlan设备成功';
			$param['returnData']=2;
			$aJson 				= DBHelper::saveData($param);
			DBHelper::saveCommand("CMD_NIC_FLUSH");
			$this->showMessage(true,'',$aJson);
		}else{
			//已使用的网口
			$condit=new CDbCriteria();
			$condit->select="sBindPort";
			if(!empty($aPost['mid'])){
				//$condit->addCondition("id<>".$aPost['mid']);
				$condit->addCondition("id<>:id");
				$condit->params[':id'] = $aPost['mid'];
			}
			$exitsPort=$param['hModel']->findAll($condit);
			$exist=array();
			foreach($exitsPort as $port){
				$exist[]=$port['sBindPort'];
			}
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			// $c->addCondition("sWorkMode='virtual'");
			$c->addNotInCondition("sPortName",$exist);
            $c->addSearchCondition("sPortName",'.', true ,'AND' , 'NOT LIKE');
            $netPortList = $netPortModel->findAll($c);
            $viewData['netPortList'] = $netPortList;
			$this->render('vlandevice_save',$viewData);
		}
	}
	//静态路由头部-----------------------------------------------------
	public function actionGetHeaderTitleStaticRoute(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang', '名称'),'data'=>'sName'),
				array('sTitle'=>Yii::t('lang', '目的地址'),'data'=>'sTargetAddress'),
				array('sTitle'=>Yii::t('lang', '子网掩码'),'data'=>'sMask'),
				array('sTitle'=>Yii::t('lang', '下一跳地址'),'data'=>'sNextJumpIP'),
				array('sTitle'=>Yii::t('lang', '接口'),'data'=>'sLan'),
				array('sTitle'=>Yii::t('lang', '是否启用'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
                array('data'=>null,'bVisible' => false,'sClass'=>'btn_import','sType'=>1),
                array('data'=>null,'bVisible' => false,'sClass'=>'btn_exp','sType'=>1),
        );
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//静态罗IPV6
	public function actionGetHeaderTitleStaticRouteIpv6(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang', '名称'),'data'=>'sName'),
				array('sTitle'=>Yii::t('lang', '目的地址'),'data'=>'sTargetAddress'),
				array('sTitle'=>Yii::t('lang', '掩码位数'),'data'=>'sMask'),
				array('sTitle'=>Yii::t('lang', '下一跳地址'),'data'=>'sNextJumpIP'),
				array('sTitle'=>Yii::t('lang', '接口'),'data'=>'sLan'),
				array('sTitle'=>Yii::t('lang', '是否启用'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//静态路由列表
	public function actionStaticRoute(){
		$this->render("static_route");
	}
	public function actionStaticRouteIPV4(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbStaticRoute();
			$c = new CDbCriteria();
			$c->addCondition("sIPV='ipv4'");
			$param['criteria']=$c;
			$param['returnData']=2;
			$dataList = DBHelper::getDataList($param);

			$NetPortModel = new TbNetPort();
			$dataList['data'] = $NetPortModel->setLanList($dataList['data'] , 'sPort');

			echo CJSON::encode($dataList);
			Yii::app()->end();
		}else{
			$this->render('static_route_ipv4');
		}
	}

	//静态路由iPv4导入
	public function actionStaticRouteIPV4_import(){
		if(Yii::app()->request->isPostRequest){

			set_time_limit(0);
			error_reporting(0);
			$aPost									= (array)$this->getParam();
			$attach                                 = CUploadedFile::getInstanceByName('recovery_file');
			$sFileName								= $this->upload_user_filter($attach);
			$aData									= $this->staticRoute_gcvs($sFileName,Yii::t('lang', '名称'));
			$error                                  = array();//专门存错误信息的数组
			$total                                  = count($aData['sTargetAddress']);
			while($sTargetAddress = array_shift($aData['sTargetAddress'])){
						$array						= array();
						$array['sTargetAddress']	= $sTargetAddress;
						$array['sName']				= array_shift($aData['sName']);
						$array['sMask']				= array_shift($aData['sMask']);
						$array['sNextJumpIP']		= array_shift($aData['sNextJumpIP']);
						$array['sPort']				= array_shift($aData['sPort']);
						$array['sIPV']				= array_shift($aData['sIPV']);
						$array['iStatus']			= array_shift($aData['iStatus']);
						$sMask						= $array['sMask'];

						//名称是否存在
						$result                     = TbStaticRoute::model()->count('sName=:sName',array(':sName'=>$array['sName']));
						if($result){
							array_push($error,Yii::t('lang', '名称')."：{$array['sName']} ".Yii::t('lang', '已经存在'));
							continue;
						}

				      	//判断是否静态路由是否存在
				      	$result                     = TbStaticRoute::model()->sameStatic($sTargetAddress,$array['sMask']);
					  	if($result){
								array_push($error,Yii::t('lang', '目的地址').": ".$sTargetAddress.Yii::t('lang', '掩码') .":".$sMask.' '.Yii::t('lang', '该静态路由已经存在'));
								continue;
					  	}
						if(!empty($sTargetAddress)){
							$res = preg_match(Regexp::$ipv4,$sTargetAddress);
							if(!$res){
								array_push($error,Yii::t('lang', '目的地址').": ".$sTargetAddress." ".Yii::t('lang', '该静态路由IP地址输入有误'));
								continue;
							}
						}else{
							array_push($error,Yii::t('lang', '目的地址').": ". $sTargetAddress.Yii::t('lang', '掩码').":".$sMask.' '.Yii::t('lang', 'IP地址不能为空'));
							continue;
						}
					  	//转换掩码，并且判断掩码是否正确
						$array['sMask']				= $this->getNetMask($array['sMask']);
					  	if($array['sMask']==false){
							  array_push($error,Yii::t('lang', '掩码').":".$sMask.' '.Yii::t('lang', '掩码输入错误'));
							  continue;
					  	}
						if(!in_array($array['sMask'],Yii::app()->params['CIDR'])) {
								array_push($error,Yii::t('lang', '掩码').":".$sMask.' '.Yii::t('lang', '掩码输入错误'));
								continue;
						}

						//下一跳IP地址输入有误
						if(!empty($array['sNextJumpIP'])){
							$res = preg_match(Regexp::$ipv4,$array['sNextJumpIP']);
							if(!$res){
								array_push($error,Yii::t('lang', '下一跳').":".$array['sNextJumpIP'].' '.Yii::t('lang', '下一跳IP地址输入有误'));
								continue;
							}
						}
						$model 						= new TbStaticRoute();
						foreach($array as $key=>$value){
							$model->$key            = $value;
							unset($key);unset($value);
						}
						$result 					= $model->save();
						$array['id']                = $model->getAttribute('id');
						if(!$result){
							array_push($error,Yii::t('lang', '目的地址').":". $sTargetAddress .Yii::t('lang', '掩码').":".$sMask.' '.Yii::t('lang', '该静态路由添加失败'));
							continue;
						}
						//保存日志
						$pData                      = new stdClass();
						$pData->sDesc               = '操作成功';
						$pData->sRs                 = '新增静态路由';
						DBHelper::saveOperationLog($pData);
						//发送管道
						$sCommand					= "CMD_STATICROUTE|add|".CJSON::encode($array);
						DBHelper::saveCommand($sCommand);
			}
			if(!empty($error)){
				$fail_count                         = count($error);
				$succ_count                         = $total-$fail_count;
				$tips                               = Yii::t('lang', '导入成功')." $succ_count ".Yii::t('lang', '条').",".Yii::t('lang', '失败').$fail_count.Yii::t('lang', '条').'<br>';
				$tips                              .= implode('<br>',$error);
			}else{
				$tips                               = Yii::t('lang', '导入成功');
			}
			$this->showMessage(true,$tips);
		}else{
			$viewData       = array();
			$this->render('static_route_ipv4_import');
		}

	}

	//静态路由iPv4导出
	public function actionStaticRouteIPV4_EXPORT($sIPV='ipv4'){
		if(Yii::app()->request->isPostRequest) {
			$aPost=(array)$this->getParam();
			$path = "/tmp/static_route_ipv4".time().".csv";
			if(file_exists($path)) @unlink($path);
			if(Yii::app()->language == 'zh_cn'){
				$eSql = " SELECT sName,sTargetAddress,sMask,sNextJumpIP,(CASE WHEN sPort!='' THEN (select sLan from m_tbnetport where sPortName=sPort) ELSE '' END) as sPort,(CASE WHEN iStatus = 1 THEN '启用' ELSE '禁用' END) AS iStatus,(CASE WHEN sIPV = 'ipv4' THEN 'ipv4' ELSE 'ipv6' END) AS sIPV FROM m_tbstaticroute WHERE sIPV='".$sIPV."'";
			}else{
				$eSql = " SELECT sName,sTargetAddress,sMask,sNextJumpIP,(CASE WHEN sPort!='' THEN (select sLan from m_tbnetport where sPortName=sPort) ELSE '' END) as sPort,(CASE WHEN iStatus = 1 THEN 'Enabled' ELSE 'Disabled' END) AS iStatus,(CASE WHEN sIPV = 'ipv4' THEN 'ipv4' ELSE 'ipv6' END) AS sIPV FROM m_tbstaticroute WHERE sIPV='".$sIPV."'";
			}
			$sql = $eSql . " into outfile '$path'
            CHARACTER SET gbk
            fields terminated by ','
            optionally enclosed by '' escaped by ''
            lines terminated by '\r\n'";
			Yii::app()->db->createCommand($sql)->execute();
			//$title = @mb_convert_encoding("名称,目的地址 ,子网掩码,下一跳地址,接口,是否启用,IP类型\r\n", "gbk", "UTF-8");
			$title = @mb_convert_encoding(Yii::t('lang','名称').','.Yii::t('lang','目的地址').','.Yii::t('lang','子网掩码').','.Yii::t('lang','下一跳地址').','.Yii::t('lang','接口').','.Yii::t('lang','是否启用').','.Yii::t('lang','IP类型')."\r\n", "gbk", "UTF-8");
			file_put_contents($path ,  $title . file_get_contents($path));
			$this->downloadFile("ipv4 ".Yii::t('lang','静态路由')."_" . date("Ymds") . ".csv", $path);
exit;
			//$shell = "cat - 1 <<< '\"目的地址\",\"子网掩码\",\"下一跳地址\",\"接口\",\"是否启用(0表示禁用,1表示启用)\"' >$path && mv -f  $path 1";
			$header = "/tmp/".time();
			$shell = $this->render('static_route_shell',array('header'=>$header,'path'=>$path),true);
			$tmp_sh_url = $header.".tmp.sh";
			file_put_contents($tmp_sh_url,$shell);
			$shell = "/bin/sh ".$tmp_sh_url;
			$this->shellResult($shell);
			$this->downloadFile(Yii::t('lang','ipv4静态路由')."" . date("Ymds") . ".csv", $header);
			//下载完成后删除服务器的文件
			@unlink($tmp_sh_url);@unlink($header);
			$shell= "/usr/bin/sudo /usr/bin/rm -rf ".$path;
			system($shell);

		}
	}

	//策略路由导出
	public function actionStrategyRouteIPV4_Export(){
		$hPost=(array)$this->getParam();
		$path = "/tmp/".time();
        if(Yii::app()->language == 'zh_cn'){
            $sql = "SELECT sRouteName, IF (RouteModel = 1, '是', '否') AS RouteModel, sPriority, ( SELECT sLan FROM m_tbnetport WHERE `sPortName` = `m_tbstrategyroute`.iIfaceID ) AS sLan, sJumpName, ( SELECT IFNULL( GROUP_CONCAT(sAddressname), '' ) FROM m_tbaddress_list WHERE id = iSourceIPID ) AS iSourceIPName, ( SELECT IFNULL( GROUP_CONCAT(sAddressname), '' ) FROM m_tbaddress_list WHERE id = iTargetIPID ) AS iTargetIPName,IF (iStatus = 1, '是', '否') AS RouteModel,sDesc FROM m_tbstrategyroute";
        }else{
            $sql = "SELECT sRouteName, IF (RouteModel = 1, 'Yes', 'No') AS RouteModel, sPriority, ( SELECT sLan FROM m_tbnetport WHERE `sPortName` = `m_tbstrategyroute`.iIfaceID ) AS sLan, sJumpName, ( SELECT IFNULL( GROUP_CONCAT(sAddressname), '' ) FROM m_tbaddress_list WHERE id = iSourceIPID ) AS iSourceIPName, ( SELECT IFNULL( GROUP_CONCAT(sAddressname), '' ) FROM m_tbaddress_list WHERE id = iTargetIPID ) AS iTargetIPName,IF (iStatus = 1, 'Yes', 'No') AS RouteModel,sDesc FROM m_tbstrategyroute";
        }
        $sql =$sql. " into outfile '$path'
            CHARACTER SET gbk
            fields terminated by ','
            optionally enclosed by '' escaped by ''
            lines terminated by '\r\n';";
		Yii::app()->getComponent('db')->createCommand($sql)->execute();

		//写入标题头
		$title = @mb_convert_encoding(Yii::t('lang', "*策略路由名称,*是否主路由,*优先级,接口,下一跳,源IP名称,目的IP名称,是否启用,描述")."\r\n", "GB2312", "UTF-8");
		file_put_contents($path ,  $title . file_get_contents($path));

		$this->downloadFile("StrategyRouteIPV4_".date("Ymds").".csv",$path);
	}

	//策略路由导入
	public function actionStrategyRouteIPV4_Import(){

		if(Yii::app()->request->isPostRequest){
			set_time_limit(0);
			error_reporting(0);
			$attach                                 = CUploadedFile::getInstanceByName('recovery_file');
			$sFileName                              = $this->_uploadFilter($attach);
			$aData                                  = $this->_getCsv($sFileName,'*'.Yii::t('lang', '策略路由名称'));
			$error                                  = array();//专门存错误信息的数组
			$total                                  = count($aData);
			// $command =  Yii::app()->getComponent('db');
			$GLOBALS['NOT_ENCRYPT_PASS']            = 1;

			while($row = array_shift($aData)){
				//获取EXCEL的内容
				$array                = array();
				$array['sRouteName']  = $row[0];
				$array['RouteModel']  = $row[1]==Yii::t('lang', '是')?1:0;
				$array['sPriority']   = intval($row[2])>1?$row[2]:0;
				$array['sJumpName']   = $row[4];
				$array['iStatus']     = $row[7]==Yii::t('lang', '是')?1:0;
				$array['sDesc']       = $row[8];
				$array['iIfaceJump1'] = 1;
				$array['iIfaceJump2'] = 1;
				$array['sIPV']        = 'ipv4';

				//接口
				$sLan                = $row[3];

				//源IP、目的IP
				$iSourceIPName       = trim($row[5]);
				$iTargetIPName       = trim($row[6]);

				//名称检测
				if(empty($array['sRouteName'])){
					array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '名称不能为空'));
					continue;
				}else{
					$check_name = TbStrategyRoute::model()->count("sRouteName=:sRouteName",array(':sRouteName'=>$array['sRouteName']));
					if($check_name>0){
						array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '名称已经存在'));
						continue;
					}
				}

				//优先级检测
				if(empty($array['sPriority'])){
					array_push($error, $array['sPriority'] .' '.Yii::t('lang', '名称不能为空'));
					continue;
				}else{
					$check_name = TbStrategyRoute::model()->count("sPriority=:sPriority",array(':sPriority'=>$array['sPriority']));
					if($check_name>0){
						array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '优先级').' '. $array['sPriority'] .' '.Yii::t('lang', '已经存在'));
						continue;
					}
				}

				//接口
				if(empty($sLan)){
					array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '接口不能为空'));
					continue;
				}else{
					$check_netport = TbNetPort::model()->find("sLan=:sLan",array(':sLan'=>$sLan));
					if($check_netport){
						$check_netport = CJSON::decode(CJSON::encode($check_netport));
						$array['iIfaceID'] = $check_netport['sPortName'];
						$array['sIfaceName'] = $check_netport['sPortName'];
					}else{
						array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '接口名称').' ' . $sLan . ' '.Yii::t('lang', '错误'));
						continue;
					}
				}

				//下一跳
				if(!empty($array['sJumpName'])){
					if($array['sJumpName' == '0.0.0.0']){
						array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '下一跳地址不能为0.0.0.0'));
						continue;
					}

					if(!filter_var($array['sJumpName'],FILTER_VALIDATE_IP, FILTER_FLAG_IPV4) ) {
						array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '下一跳地址').' '. $array['sJumpName'] .' '.Yii::t('lang', '输入有误'));
						continue;
					}
				}else{
					array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '下一跳地址不能为空'));
					continue;
				}

				//源IP名称 检测
				if(!empty($iSourceIPName)){
					$check_ip = TbaddressList::model()->find("sAddressname=:sAddressname" , array(":sAddressname"=>$iSourceIPName));
					if($check_ip){
						$check_ip = CJSON::decode(CJSON::encode($check_ip));
						$array['iSourceIPID']   = $check_ip['id'];
						$array['sSourceIPAddr'] = $check_ip['sAddress'];
					}else{
						array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '源目的地址').' '. $iSourceIPName . ' '.Yii::t('lang', '输入有误'));
						continue;
					}
				}

				//目的IP名称 检测
				if(!empty($iTargetIPName)){
					$check_ip = TbaddressList::model()->find("sAddressname=:sAddressname" , array(":sAddressname"=>$iTargetIPName));
					if($check_ip){
						$check_ip = CJSON::decode(CJSON::encode($check_ip));
						$array['iTargetIPID']   = $check_ip['id'];
						$array['sTargetIPAddr'] = $check_ip['sAddress'];
					}else{
						array_push($error, $array['sRouteName'] .' '.Yii::t('lang', '源目的地址').' '. $iTargetIPName . ' '.Yii::t('lang', '输入有误'));
						continue;
					}
				}

				$param['sLogDesc']                      = "导入策略路由";
				$param['aPost']                         = $array;
				$param['sCommand']                      = "CMD_STATEGY_ROUTING|add";
				$param['returnData']                    = 2;
				$param['hModel']                        = new TbStrategyRoute();
				DBHelper::saveData($param);
			}
			if(!empty($error)){
				$fail_count                             = count($error);
				$succ_count                             = $total-$fail_count;
				$tips                                   = Yii::t('lang', '导入成功')." $succ_count ".Yii::t('lang', '条').",".Yii::t('lang', '失败').$fail_count.Yii::t('lang', '条').'<br>';
				$tips                                  .= implode('<br>',$error);
			}else{
				$tips                                   = Yii::t('lang', '导入成功');
			}
			$this->showMessage(true,$tips);
		} else {
			$data['save_path'] = 'Network/StrategyRouteIPV4_Import';
			$data['message'] = Yii::t('lang', '导入文件必须是CSV文件,*号表示必填项');
			$this->render('../public/import',$data);
		}

	}


	//ISP路由导出
	public function actionIspRouteIPV4_Export(){
		$hPost=(array)$this->getParam();
		$path = "/tmp/".time();
		if(Yii::app()->language == 'zh_cn'){
            $sql = "SELECT ( CASE sBelongISP WHEN 'telecom' THEN '电信' WHEN 'unicom' THEN '联通' WHEN 'mobile' THEN '移动' END ) AS sBelongISP, sNextJump, ( SELECT sLan FROM m_tbnetport WHERE sPortName = sOutPort ) AS sLan, sMetric, IF (iStatus, '是', '否') AS iStatus FROM m_tbisproute";
		}else{
            $sql = "SELECT ( CASE sBelongISP WHEN 'telecom' THEN 'China Telecom' WHEN 'unicom' THEN 'China Unicom' WHEN 'mobile' THEN 'China Mobile' END ) AS sBelongISP, sNextJump, ( SELECT sLan FROM m_tbnetport WHERE sPortName = sOutPort ) AS sLan, sMetric, IF (iStatus, 'Yes', 'No') AS iStatus FROM m_tbisproute";
		}

		$sql =$sql. " into outfile '$path'
            CHARACTER SET gbk
            fields terminated by ','
            optionally enclosed by '' escaped by ''
            lines terminated by '\r\n';";
		Yii::app()->getComponent('db')->createCommand($sql)->execute();

		//写入标题头
		$title = @mb_convert_encoding(Yii::t('lang', "*所属ISP(电信/移动/联通),下一跳,流出网口,metric,是否启用")."\r\n", "GB2312", "UTF-8");
		file_put_contents($path ,  $title . file_get_contents($path));

		$this->downloadFile("IspRouteIPV4_".date("Ymds").".csv",$path);
	}

	//ISP路由导入
	public function actionIspRouteIPV4_Import(){

		if(Yii::app()->request->isPostRequest){
			set_time_limit(0);
			error_reporting(0);
			$attach                                 = CUploadedFile::getInstanceByName('recovery_file');
			$sFileName                              = $this->_uploadFilter($attach);
			$aData                                  = $this->_getCsv($sFileName,Yii::t('lang', "*所属ISP(电信/移动/联通)"));
			$error                                  = array();//专门存错误信息的数组
			$total                                  = count($aData);
			// $command =  Yii::app()->getComponent('db');
			$GLOBALS['NOT_ENCRYPT_PASS']            = 1;
			$sBelongISP = [Yii::t('lang', '电信')=>"telecom", Yii::t('lang', '移动')=>"mobile", Yii::t('lang', '联通')=>"unicom"];

			while($row = array_shift($aData)){
				//获取EXCEL的内容
				$array                = array();
				$array['sBelongISP']  = $row[0];
				$array['sNextJump']   = $row[1];
				// $array['sOutPort'] = $row[2];
				$array['sMetric']     = $row[3];
				$array['iStatus']     = $row[4]==Yii::t('lang', '是')?1:0;
				$array['sIPV']        = 'ipv4';
				//网口
				$sLan                 = $row[2];

				//所属ISP
				if(!in_array($array['sBelongISP'], array_keys($sBelongISP))){
					array_push($error, $array['sBelongISP'] .' '.Yii::t('lang', '所属ISP错误，请填写').'(' . implode('/' , array_keys($sBelongISP)). ')');
					continue;
				}else{
					$array['sBelongISP'] = $sBelongISP[$array['sBelongISP']];
				}

				if(empty($array['sOutPort']) && empty($sLan)){
					array_push($error, $array['sBelongISP'] .' '.Yii::t('lang', '下一跳和流出网口必须至少填写一个'));
					continue;
				}

				//下一跳
				if(!empty($array['sNextJump'])){
					if(!filter_var($array['sNextJump'],FILTER_VALIDATE_IP, FILTER_FLAG_IPV4) ) {
						array_push($error, $array['sBelongISP'] .' '.Yii::t('lang', '下一跳地址').' '. $array['sNextJump'] .' '.Yii::t('lang', '输入有误'));
						continue;
					}
				}

				//网口检测
				if(!empty($sLan)){
					$check_netport = TbNetPort::model()->find("sLan=:sLan" , [":sLan"=>$sLan]);
					if($check_netport){
						$check_netport = CJSON::decode(CJSON::encode($check_netport));
						$array['iPortType'] = 1;
						$array['sOutPort']  = $check_netport['sPortName'];
					}else{
						array_push($error, $array['sBelongISP'] .' '.Yii::t('lang', '网口').' '. $sLan .' '.Yii::t('lang', '输入有误'));
						continue;
					}
				}

				$param['sLogDesc']                      = "导入ISP路由";
				$param['aPost']                         = $array;
				$param['sCommand']                      = "CMD_ISP_CONFIG|add";
				$param['returnData']                    = 2;
				$param['hModel']                        = new TbIspRoute();
				DBHelper::saveData($param);
			}
			if(!empty($error)){
				$fail_count                             = count($error);
				$succ_count                             = $total-$fail_count;
				$tips                                   = Yii::t('lang', '导入成功')." $succ_count ".Yii::t('lang', '条').",".Yii::t('lang', '失败').$fail_count.Yii::t('lang', '条').'<br>';
				$tips                                  .= implode('<br>',$error);
			}else{
				$tips                                   = Yii::t('lang', '导入成功');
			}
			$this->showMessage(true,$tips);
		} else {
			$data['save_path'] = 'Network/IspRouteIPV4_Import';
			$data['message'] = Yii::t('lang', '导入文件必须是CSV文件,*号表示必填项');
			$this->render('../public/import',$data);
		}

	}

	/*
	 * 静态路由导出模板
	 */
	public function actionStatic_route_Ipv4_Import_tpl(){
		if(Yii::app()->language == 'zh_cn'){
			$filename		= 'static_route_tpl.csv';
		}else{
			$filename		= 'static_route_tpl_en.csv';
		}
		$sPath          = Yii::getPathOfAlias('root').'/data/static_route/';
		$file_url       = $sPath.$filename;
		if(!is_file($file_url)){
			$this->showMessage(false,$file_url.Yii::t('lang','文件不存在'));
		}
		//记录日志
		$pData                     	 				= new stdClass();
		$pData->sDesc       						= '静态路由下载导入用户模板';
		$pData->sRs                 				= '操作成功';
		$this->saveOperationLog($pData);
		$this->downloadFile($filename,$file_url);
	}

	/**
	 * 获取Excel信息
	 */
	private function staticRoute_gcvs($file_path,$tag="")
	{
		if (!is_file($file_path)) $this->showMessage(false, Yii::t('lang','文件不存在'));


		$handle 		= fopen($file_path, "r");
		//先执行一次，过滤第一行      进行判断
		$result 		= fgetcsv($handle, 10000);
		$str 			= trim(@mb_convert_encoding($result[0], "UTF-8", "GBK,GB2312,ASCII,BIG5"));
		$user_sum 		= array();
		//网口转换
		$aLan			= TbNetPort::model()->sLanList(true);
		if ($str == $tag) {
			while ($row = fgetcsv($handle, 10000)) {
				if (empty(trim($row[0]))) continue;
				foreach($row as $key=>$value){
					$row[$key]                          = trim(@mb_convert_encoding($row[$key], "UTF-8", "UTF-8,GBK,GB2312,ASCII,BIG5"));
				}
				$user_sum['sName'][] 				= trim($row[0]);
				$user_sum['sTargetAddress'][] 		= trim($row[1]);
				$user_sum['sMask'][] 				= trim($row[2]);
				$user_sum['sNextJumpIP'][] 			= trim($row[3]);
				$user_sum['sPort'][] 				= $aLan[$row[4]];
				$user_sum['iStatus'][] 				= trim($row[5])=="启用"?1:0;
				$user_sum['sIPV'][] 				= trim($row[6])=="ipv6"?"ipv6":"ipv4";
			}
			return $user_sum;
		} else {
			$this->showMessage(false, Yii::t('lang','上传文件出错'));
		}

	}

	/*
     * 生成EXCEL
     */
	private function createOutExcel_StaticRouteIPV4($users_info){
		$excel = new Excel();
		//设置格式
		$excel->setStyle(array('id'=>'s_title','Font'=>array('FontName'=>'宋体','Size'=>'12','Bold'=>'1')));
		$data = array();
		//标题
		//$excel_data[0][] = array('styleid'=>'s_title','data'=>Yii::t('lang','序号'));
		$excel_data[0][] = array('styleid'=>'s_title','data'=>Yii::t('lang','目的地址'));
		$excel_data[0][] = array('styleid'=>'s_title','data'=>Yii::t('lang','子网掩码'));
		$excel_data[0][] = array('styleid'=>'s_title','data'=>Yii::t('lang','下一跳地址'));
		$excel_data[0][] = array('styleid'=>'s_title','data'=>Yii::t('lang','接口'));
		$excel_data[0][] = array('styleid'=>'s_title','data'=>Yii::t('lang','是否启用'));
		foreach($users_info as $k=>$item){
			$tmp   = array();
			//$tmp[] = array('data'=>$k+1);
			$tmp[] = array('data'=>$item['sTargetAddress']);
			$tmp[] = array('data'=>$item['sMask']);
			$tmp[] = array('data'=>$item['sNextJumpIP']);
			$tmp[] = array('data'=>$item['sPort']);
			//$tmp[] = array('data'=>$item['iStatus']);
			if($item['iStatus']=="1"){
				$tmp[] = array('data'=>''.Yii::t('lang','启用'));
			}else{
				$tmp[] = array('data'=>''.Yii::t('lang','禁用'));
			}
			$excel_data[] = $tmp;
			unset($item);unset($k);
		}
		$excel_data = $excel->charset($excel_data,'UTF-8');
		$excel->addArray($excel_data);
		$excel->addWorksheet($excel->charset('static_route_ipv4'));
		$excel->generateXML($excel->charset('static_route_ipv4','UTF-8').date('Y-m-d-H',time()));
	}

	//过滤上传文件的参数
	private function upload_user_filter($attach){
		if(empty($attach))                                  $this->showMessage(false,Yii::t('lang','上传文件不能为空'));
		if ($attach->size > 2048*1024)                      $this->showMessage(false,Yii::t('lang','上传文件不能大于2M'));
		//if($this->get_extension_1($attach->name) !='csv')   $this->showMessage(false,'请选上传CSV格式文件');
		if ($attach->getError())                            $this->showMessage(false,Yii::t('lang','上传文件失败,请稍等再上传'));
		$sFileName                              = "/tmp/import_user_" . time();
		if(!$attach->saveAs($sFileName))                    $this->showMessage(false,Yii::t('lang','上传文件失败,请稍等再上传'));
		return $sFileName;
	}

	/**************判断文件后缀******************/
	//第1种方法：
	private function get_extension_1($file){
		return substr(strrchr($file, '.'), 1);
	}

	public function actionStaticRouteIPV6(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbStaticRoute();
			$c = new CDbCriteria();
			$c->addCondition("sIPV='ipv6'");
			$param['criteria']=$c;
			$param['returnData'] 	= 2;
			$result 		 		= DBHelper::getDataList($param);
			$result['data'] 		= TbNetPort::model()->setLanList($result['data'],'sPort');
			$this->showMessage(true,'success',$result);
		}else{
			$this->render('static_route_ipv6');
		}
	}
	//编辑静态路由
	public function actionStaticRouteSaveIPV4()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbStaticRoute();
		if(Yii::app()->request->isPostRequest) {
			if(empty($aPost['sName'])){
				$this->showMessage(false,Yii::t('lang','名称不能为空'));
			}
			if(empty($aPost['sNextJumpIP'])&& empty($aPost['sPort'])){
				$this->showMessage(false,Yii::t('lang','下一跳IP地址和接口不能全为空，两者选其一'));
			}
			if(!empty($aPost['sTargetAddress'])){
				$res = preg_match(Regexp::$ipv4,$aPost['sTargetAddress']);
				if(!$res) $this->showMessage(false,Yii::t('lang','IP地址输入有误'));
			}else{
				$this->showMessage(false,Yii::t('lang','IP地址不能为空'));
			}
			if(!empty($aPost['sMask'])){
					$res = preg_match(Regexp::$all_mask,$aPost['sMask']);
					if(!$res) $this->showMessage(false,Yii::t('lang','掩码输入有误'));
			}else{
				$this->showMessage(false,Yii::t('lang','掩码不能为空'));
			}
			if(!empty($aPost['sNextJumpIP'])){
				$res = preg_match(Regexp::$ipv4,$aPost['sNextJumpIP']);
				if(!$res) $this->showMessage(false,Yii::t('lang','下一跳IP地址输入有误').''.Yii::t('lang',''));
			}

			//掩码统一转换为 IP地址的形式
			//判断掩码是否为数值 例/24  如果为false则为数值
			$pos                                = strpos($aPost['sMask'],'.');
			if($pos == false){
				$addr_mask_num                  = intval($aPost['sMask']);
				$addr_mask                      = '';
				$addr_mask                      = str_pad($addr_mask,$addr_mask_num,'1');
				$addr_mask                      = str_pad($addr_mask,32,'0');
				$addr_mask                      = bindec($addr_mask);
				$addr_mask_int                  = $addr_mask;
				//将/24转为 255.255.255.0
				$addr_mask                      = long2ip($addr_mask);
				$aPost['sMask']					= $addr_mask;
			}
			$res = $this->CheckIpAndMask($aPost['sTargetAddress'],$aPost['sMask']);
			if(!$res){
				$aJson['success'] = false;
				$aJson['msg'] = Yii::t('lang','目的地址和子网掩码不一致')."。";
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}

			//检测 名称 目的地址、子网掩码、下一跳地址 不能完全相同
			$result 					= $param['hModel']->checkSameName($aPost);
			if($result){
				if($result['sName'] == $aPost['sName']){
					$this->showMessage(false,Yii::t('lang','名称').'：'.$aPost['sName'].''.Yii::t('lang','已存在'));
				} else {
					$this->showMessage(false,Yii::t('lang','目的地址').': '.$aPost['sTargetAddress'].Yii::t('lang','掩码').' :'.$aPost['sMask'].' 该静态路由已经存在');
				}
			}

			$aData=array();
			if(empty($aPost['iStatus']))$aData['iStatus']=0;
			$param['extData']		= $aData;
			$param['sCommand']		= !empty($aPost['id'])?"CMD_STATICROUTE|edit":"CMD_STATICROUTE|add";
			$param['sLogDesc']		= '编辑ipv4静态路由成功';
			$param['aPost']			= $aPost;
			DBHelper::saveData($param);
		}else{
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			$c->addCondition("sWorkMode='route'");
			$c->addCondition("sWorkMode='nat'","OR");
			$c->addCondition("iStatus= 1");
			$brModel = new TbBridgeDevice();
			$bc=new CDbCriteria();
			$bc->addCondition("iStatus = 1");
			$viewData['netPortList']=$netPortModel->findAll($c);
			//掩码
			$viewData['netMask'] = Yii::app()->params['CIDR'];

			$this->render('static_route_save_ipv4',$viewData);
		}
	}

	//判断IP地址和掩码是否一致
	public function CheckIpAndMask($ipaddress ,$netmask){

		$wIparr = explode('.',$ipaddress);
		$wipstr = ($wIparr[0]<<24)+($wIparr[1]<<16)+($wIparr[2]<<8)+$wIparr[3];
		$wMaskarr = explode('.',$netmask);
		$wMaskstr = ($wMaskarr[0]<<24)+($wMaskarr[1]<<16)+($wMaskarr[2]<<8)+$wMaskarr[3];
		if(($wipstr&$wMaskstr) !=$wipstr){
			return false;
		}else{
			return true;
		}
	}
	public function actionStaticRouteSaveIPV6()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbStaticRoute();
		if(Yii::app()->request->isPostRequest) {
			if(!$this->CheckIPV6($aPost['sTargetAddress'],1)) $this->showMessage(false,Yii::t('lang','目的地址输入有误'));
			if(!empty($aPost['sNextJumpIP'])){
				if(!$this->CheckIPV6($aPost['sNextJumpIP'],1)) $this->showMessage(false,Yii::t('lang','下一跳IP地址输入有误'));
			}
			//检测 名称 目的地址、子网掩码、下一跳地址 不能完全相同
			$result 					= $param['hModel']->checkSameName($aPost);
			if($result){
				if($result['sName'] == $aPost['sName']){
					$this->showMessage(false,Yii::t('lang','名称').'：'.$aPost['sName'].''.Yii::t('lang','已存在'));
				} else {
					$this->showMessage(false,Yii::t('lang','目的地址').': '.$aPost['sTargetAddress'].Yii::t('lang','掩码').' :'.$aPost['sMask'].' '.Yii::t('lang','该静态路由已经存在'));
				}
			}

			$aData=array();
			if(empty($aPost['iStatus']))$aData['iStatus']=0;
			$param['extData']=$aData;
			$param['sCommand']=!empty($aPost['id'])?"CMD_STATICROUTE|edit":"CMD_STATICROUTE|add";
			$param['sLogDesc']='编辑ipv6静态路由成功';
			DBHelper::saveData($param);
		}else{
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			$c->addCondition("sWorkMode='route'");
			$c->addCondition("sWorkMode='nat'","OR");
			$viewData['netPortList']=$netPortModel->findAll($c);
			$this->render('static_route_save_ipv6',$viewData);
		}
	}
	//策略路由头部-----------------------------------------------------
	public function actionGetHeaderTitleStrategyRoute(){
		$aPost= (array)$this->getParam();
		$aData=array(
				array('sTitle'=>'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang', '策略路由'),'data'=>'sRouteName'),
				array('sTitle'=>Yii::t('lang', '源IP段'),'data'=>'sSourceIPAddr'),
				array('sTitle'=>Yii::t('lang', '目的IP段'),'data'=>'sTargetIPAddr','minWidth'=>'160'),
				//array('sTitle'=>'协议(端口)/应用','data'=>'sProtocol','sClass'=>'sProtocol','minWidth'=>'150'),
				array('sTitle'=>Yii::t('lang', '下一跳/接口'),'data'=>'sJumpName','sClass'=>'sJumpName','minWidth'=>'120'),
				array('sTitle'=>Yii::t('lang', '是否启用'),'data'=>'iStatus','sClass'=>'iStatus','width'=>'80'),
				array('sTitle'=>Yii::t('lang', '优先级'),'data'=>'sPriority','width'=>'100'),
				'RouteModel'=>array('sTitle'=>Yii::t('lang', '主备路由模式'),'data'=>'RouteModel','sClass'=>'RouteModel','width'=>'200'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
				'btn_import' => array('data'=>null,'bVisible' => false,'sClass'=>'btn_import','sType'=>1),
				'btn_exp' => array('data'=>null,'bVisible' => false,'sClass'=>'btn_exp','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'c_b btn_qy','sValue'=>Yii::t('lang', '启用自动选路'),'bAuth'=>true,'sType'=>3),
				array('data'=>null,'bVisible' => false,'sClass'=>'c_o btn_jy','sValue'=>Yii::t('lang', '关闭自动选路'),'bAuth'=>true,'sType'=>3),
		);
		if(isset($aPost['RouteModel'])&&$aPost['RouteModel']=='0'){
			unset($aData['RouteModel']);
		}
		if (isset($aPost['sIPV']) && $aPost['sIPV'] == 'ipv6') {
			unset($aData['btn_import']);
			unset($aData['btn_exp']);
		}
		$aData = array_values($aData);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//策略路由列表
	public function actionStrategyRoute(){
		$this->render("strategy_route");
	}
	public function actionStrategyRouteIPV4(){
		if(Yii::app()->request->isPostRequest){
			$hPost = (array)$this->getParam();
			$iModel = new TbStrategyRoute();
			$param['hModel'] = new TbStrategyRoute();
			$c = new CDbCriteria();
			$c->addCondition("sIPV='ipv4'");
			$param['criteria']=$c;
			$param['returnData']=2;
			$dataList = DBHelper::getDataList($param);

			$NetPortModel = new TbNetPort();
			$dataList['data'] = $NetPortModel->setLanList($dataList['data'] , 'iIfaceID' , 'sIfaceName');

			echo CJSON::encode($dataList);
			Yii::app()->end();

		}else{
            $config=new TbConfig();
            $info=$config->find("sName='AutoSelect'");
            $data['setting']=CJSON::decode($info['sValue']);
			$this->render('strategy_route_ipv4',$data);
		}
	}
        /* 点击开启关闭 自动选路
         * 判断是否允许开启自动选路
         * 条件:1.所有同源IP中只有一条主路由 2.该路由的优先级是该同源IP中最高 3.优先级越高数值越小
         *
         */
    public function actionEnableAutoSelect(){
        $aPost                              = (array)$this->getParam();
        //启用启动选路
        if($aPost['iTurnOn']==1){
            $hModel                         = new TbStrategyRoute();
			$sIPV							= !empty($aPost['sIPV']) ? $aPost['sIPV'] : 'ipv4';
            $c                              = new CDbCriteria();
            $c->group                       = 'iSourceIPID,iTargetIPID';
            //$c->select              = array('iSourceIPID');
            $_SiD                           = $hModel->findAll($c);
            $error                          = array();
            $error_tis                      = '';
            while($item = array_shift($_SiD)){
                $iSourceIPID                = $item->iSourceIPID;
                $iTargetIPID                = $item->iTargetIPID;
                $same_num                   = TbStrategyRoute::model()->count("iSourceIPID=:iSourceIPID AND iTargetIPID=:iTargetIPID AND RouteModel=1 AND sIPV=:sIPV",array(':iSourceIPID'=>$iSourceIPID,':iTargetIPID'=>$iTargetIPID,':sIPV'=>$sIPV));
				if($same_num>1){
                    //出现重复主路由的同源IP
                    $error['same'][$iSourceIPID.'_'.$iTargetIPID]    = $same_num;
                }
                $SQL                        = "SELECT (SELECT MIN(sPriority) A FROM `m_tbstrategyroute` WHERE  iSourceIPID=:iSourceIPID AND iTargetIPID=:iTargetIPID AND sIPV=:sIPV) = (SELECT MIN(sPriority)  B FROM `m_tbstrategyroute` WHERE RouteModel =1 AND iSourceIPID=:iSourceIPID AND iTargetIPID=:iTargetIPID AND sIPV=:sIPV) AS C";
                $res                        = Yii::app()->db->createCommand($SQL)->queryRow(true,array(':iSourceIPID'=>$iSourceIPID,':iTargetIPID'=>$iTargetIPID,':sIPV'=>$sIPV));
				//出现主路由的优先级不是最高的同源IP
                if($res['C'] === '0'){
                    $error['master'][$iSourceIPID.'_'.$iTargetIPID]            = $res['C'];
                }
                unset($item);unset($res);unset($iSourceIPID);unset($iTargetIPID);
            }
			//组织错误信息提示用户   同源IP、同目的判断
			if(!empty($error)){
				if(!empty($error['same'])){
					$same_tis                           = '';
					foreach($error['same'] as $key => $value){
						$same_name               = '';
						$tmp_arr				 = explode('_',$key);
						$iSourceIPID			 = intval($tmp_arr[0]);
						$iTargetIPID			 = intval($tmp_arr[1]);
						$res                 	 = TbStrategyRoute::model()->findAll("iSourceIPID=:iSourceIPID AND iTargetIPID=:iTargetIPID AND sIPV=:sIPV AND RouteModel=1",array(':iSourceIPID'=>$iSourceIPID,':iTargetIPID'=>$iTargetIPID,':sIPV'=>$sIPV));
						while($tmp = array_shift($res)){
							$same_name           .= $tmp->sRouteName.',';
							unset($tmp);
						}
						$same_name               = substr($same_name,0,strlen($same_name)-1);
						$same_tis               .= $same_name.''.Yii::t('lang','有且仅有一个主路由').'<br>';
						unset($key);unset($value);unset($same_name);unset($iSourceIPID);unset($iTargetIPID);
					}
					$error_tis                     .= $same_tis;
				}

				if(!empty($error['master'])){
					$master_tis                     = '';
					$master_array                   = array();
					$dev_array                      = array();
					foreach($error['master'] as $key => $value){
						$tmp_arr				 	= explode('_',$key);
						$iSourceIPID			 	= intval($tmp_arr[0]);
						$iTargetIPID			 	= intval($tmp_arr[1]);
						$res                        = TbStrategyRoute::model()->findAll("iSourceIPID=:iSourceIPID AND iTargetIPID=:iTargetIPID AND sIPV=:sIPV",array(':iSourceIPID'=>$iSourceIPID,'iTargetIPID'=>$iTargetIPID,':sIPV'=>$sIPV));
						while($tmp = array_shift($res)){
							//判断主从
							if($tmp->RouteModel){
								$master_array[$tmp->sPriority] = $tmp->sRouteName;
							}else{
								array_push($dev_array,$tmp->sRouteName);
							}
							unset($tmp);
						}
						//如果主路由为空  不检测
						if(empty($master_array)) continue;
						//如果存在多个主路由  取出主路由中优先级最高的一个  其余的合并的从路由的数组中  进行提示
						if(count($master_array)>1){
							ksort($master_array);
							$master                 = array_shift($master_array);
							$dev_array              = array_merge($dev_array,$master_array);
						}
						if(empty($master)){
							$master                 = implode(',',$master_array);
						}
						$dev                        = implode(',',$dev_array);
						$master_tis                .= '<font color="#ff0000">'.$master.'</font>'.'优先级必须高于'.$dev.'<br/>';
						unset($key);unset($value);unset($master_name);unset($iSourceIPID);unset($iTargetIPID);
					}
					$error_tis                     .= $master_tis;
				}
			}


            //组织错误信息提示用户  仅有同源IP的判断
			/*while($item = array_shift($_SiD)){
				$iSourceIPID                = $item->iSourceIPID;
				$same_num                   = TbStrategyRoute::model()->count("iSourceIPID=:iSourceIPID AND RouteModel=1",array(':iSourceIPID'=>$iSourceIPID));
				if($same_num>1){
					//出现重复主路由的同源IP
					$error['same'][$iSourceIPID]    = $same_num;
				}
				$SQL                        = "SELECT (SELECT MIN(sPriority) A FROM `m_tbstrategyroute` WHERE  iSourceIPID=:iSourceIPID) = (SELECT MIN(sPriority)  B FROM `m_tbstrategyroute` WHERE RouteModel =1 AND iSourceIPID=:iSourceIPID) AS C";
				$res                        = Yii::app()->db->createCommand($SQL)->queryRow(true,array(':iSourceIPID'=>$iSourceIPID));
				//出现主路由的优先级不是最高的同源IP
				if($res['C'] === '0'){
					$error['master'][$iSourceIPID]            = $res['C'];
				}
				unset($item);unset($res);
			}
			//组织错误信息提示用户
			if(!empty($error)){
				if(!empty($error['same'])){
					$same_tis                           = '';
					foreach($error['same'] as $key => $value){
						$same_name               = '';
						$res                 = TbStrategyRoute::model()->findAll("iSourceIPID=:iSourceIPID AND RouteModel=1",array(':iSourceIPID'=>$key));
						while($tmp = array_shift($res)){
							$same_name           .= $tmp->sRouteName.',';
							unset($tmp);
						}
						$same_name               = substr($same_name,0,strlen($same_name)-1);
						$same_tis               .= $same_name.'出现重复主路由的同源IP'.'<br/>';
						unset($key);unset($value);unset($same_name);
					}
					$error_tis                     .= $same_tis;
				}

				if(!empty($error['master'])){
					$master_tis                     = '';
					$master_array                   = array();
					$dev_array                      = array();
					foreach($error['master'] as $key => $value){
						$res                        = TbStrategyRoute::model()->findAll("iSourceIPID=:iSourceIPID",array(':iSourceIPID'=>$key));
						while($tmp = array_shift($res)){
							//判断主从
							if($tmp->RouteModel){
								$master_array[$tmp->sPriority] = $tmp->sRouteName;
							}else{
								array_push($dev_array,$tmp->sRouteName);
							}
							unset($tmp);
						}
						//如果主路由为空  不检测
						if(empty($master_array)) continue;
						//如果存在多个主路由  取出主路由中优先级最高的一个  其余的合并的从路由的数组中  进行提示
						if(count($master_array)>1){
							ksort($master_array);
							$master                 = array_shift($master_array);
							$dev_array              = array_merge($dev_array,$master_array);
						}
						if(empty($master)){
							$master                 = implode(',',$master_array);
						}
						$dev                        = implode(',',$dev_array);
						$master_tis                .= '<font color="#ff0000">'.$master.'</font>'.'优先级必须高于'.$dev.'<br/>';
						unset($key);unset($value);unset($master_name);
					}
					$error_tis                     .= $master_tis;
				}
			}*/
            if(!empty($error_tis)){
                $this->showMessage(false,$error_tis);
            }
        }

        $config=new TbConfig();
        $config->sName="AutoSelect";
        $config->sValue=CJSON::encode($aPost);
        $config->sMark="策略路由自动选路";
        $config->sCommand="CMD_BEST_ROUTING";
        DBHelper::saveConfig($config,'设置成功',1,true,'保存策略路由自动选路配置',$isLog=true);
    }

	public function actionStrategyRouteIPV6(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbStrategyRoute();
			$c = new CDbCriteria();
			$c->addCondition("sIPV='ipv6'");
			$param['criteria']=$c;
			DBHelper::getDataList($param);
		}else{
			$this->render('strategy_route_ipv6');
		}
	}
	//编辑策略路由
	public function actionStrategyRouteSaveIPV4()
	{
		if(Yii::app()->request->isPostRequest) {
			$aPost=(array)$this->getParam();
			//判断下一跳和接口
			if(!isset($aPost['iIfaceID'])||empty($aPost['iIfaceID'])){
				$this->showMessage(false,''.Yii::t('lang','接口不能为空'));
			}
			if(substr($aPost['iIfaceID'],0,3)=='ppp'){
				$aPost['iIfaceJump2']			= 0;
				$aPost['sJumpName']				= '';
			}else{
				$aPost['iIfaceJump2']			= 1;
				$aPost['sJumpName']				= trim($aPost['sJumpName']);
				if(empty($aPost['sJumpName'])){
					$this->showMessage(false,''.Yii::t('lang','下一跳不能为空'));
				}
				if(preg_match(Regexp::$ipv4,$aPost['sJumpName'])==false){
					$this->showMessage(false,''.Yii::t('lang','下一跳地址输入错误'));
				}
                if($aPost['sJumpName']=='0.0.0.0'){
                    $this->showMessage(false,''.Yii::t('lang','下一跳地址不能为0.0.0.0'));
                }
			}
			/*if(!isset($aPost['iIfaceJump1']) && !isset($aPost['iIfaceJump2'])){
				$aJson['success'] =false;
				$aJson['msg'] ="接口和下一跳不能全为空，两者选其一或者都选";
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(empty($aPost['iIfaceID']) && isset($aPost['iIfaceJump1'])){
				$aJson['success'] =false;
				$aJson['msg'] ="接口不能为空";
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(empty($aPost['sJumpName']) && isset($aPost['iIfaceJump2'])){
				$aJson['success'] =false;
				$aJson['msg'] ="下一跳不能为空";
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(!empty($aPost['iIfaceID']) && !isset($aPost['iIfaceJump1'])){
				$aJson['success'] =false;
				$aJson['msg'] ="请在接口前打勾";
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(empty($aPost['sJumpName']) && isset($aPost['iIfaceJump2'])){
				$aJson['success'] =false;
				$aJson['msg'] ="请在下一跳前打勾";
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}*/
			//判断协议和应用
			if(isset($aPost['iProtocolApp'])){
				if($aPost['iProtocolApp'] ==1){
					if(isset($aPost['sProtocol']) && empty($aPost['sProtocol'])){
						$aJson['success'] =false;
						$aJson['msg'] =Yii::t('lang','请选择一个协议');
						echo CJSON::encode($aJson);
						Yii::app()->end();
					}else{
						/*if($aPost['sProtocol'] =='TCP'|| $aPost['sProtocol'] =='UDP'){
							if(empty($aPost['iSourcePort']) && empty($aPost['iTargetPort'])){
								$aJson['success'] =false;
								$aJson['msg'] ="源端口和目的端口不能全为空";
								echo CJSON::encode($aJson);
								Yii::app()->end();
							}
						}*/
						if($aPost['sProtocol'] =='ICMP'){
							if(!empty($aPost['iSourcePort']) || !empty($aPost['iTargetPort'])){
								$aJson['success'] =false;
								$aJson['msg'] ="".Yii::t('lang','源端口和目的端口不能填');
								echo CJSON::encode($aJson);
								Yii::app()->end();
							}
						}
					}
				}
				if($aPost['iProtocolApp'] == 2){
					if(isset($aPost['iApplicationID'])&& strlen($aPost['iApplicationID'])<=0){
						$aJson['success'] =false;
						$aJson['msg'] ="".Yii::t('lang','请选择一个应用');
						echo CJSON::encode($aJson);
						Yii::app()->end();
					}
				}

			}

			$iModel = new TbStrategyRoute();
			$ic = new CDbCriteria();

			$checkName = $iModel->find("sRouteName=:sRouteName AND id!=:id" , array(':sRouteName'=>$aPost['sRouteName'] , ':id'=>$aPost['id']));
            if($checkName){
                $this->showMessage(false,Yii::t('lang','名称')."{$aPost['sRouteName']}".Yii::t('lang','已存在，请更换'));
            }

			if(isset($aPost['sPriority'])&&!empty($aPost['sPriority'])){
				if(isset($aPost['id'])&&!empty($aPost['id'])){
					$ic->condition=" sPriority = :sPriority and id <>:id and sIPV ='ipv4'";
					//$ic->condition=" sPriority = ".$aPost['sPriority']." and id <>".$aPost['id']." and sIPV ='ipv4'";
					$ic->params	  = array(':sPriority'=>$aPost['sPriority'],':id'=>$aPost['id']);
					$levelcount = $iModel->count($ic);
				}else{
					$ic->condition=" sPriority = ".$aPost['sPriority']." and sIPV ='ipv4'";
					//$ic->condition=" sPriority = ".$aPost['sPriority']." and sIPV ='ipv4'";
					$ic->params	  = array(':sPriority'=>$aPost['sPriority']);
					$levelcount = $iModel->count($ic);
				}
				if($levelcount>0){
					$aJson['msg'] = "".Yii::t('lang','该优先级已经存在，请更换');
					$aJson ['success'] = false;
					echo CJSON::encode($aJson);
					Yii::app()->end();
				}
			}
			//统计m_tbdefined_application表应用的使用数量
			/*if($aPost['iStatis'] ==1){
                if($aPost['iProtocolApp'] ==2){
                    if(!empty($aPost['iApplicationID'])){
                        $sql = "Update m_tbdefined_application Set sCount = sCount+1 where iMark =".$aPost['iApplicationID'];
                        Yii::app()->db->createCommand($sql)->execute();
                    }
                }
            }

            if(!empty($aPost['id'])){
                if($aPost['iOldProtocolApp'] ==2){
                    if(!empty($aPost['iOldApplicationID'])){
                        $sql = "Update m_tbdefined_application Set sCount = sCount-1 where iMark =".$aPost['iOldApplicationID'];
                        Yii::app()->db->createCommand($sql)->execute();
                    }
                }
            }*/
            $aPost['sIfaceName'] = $aPost['iIfaceID'];
			$param['extData'] = $aPost;
			$param['hModel'] = new TbStrategyRoute();
			$param['sCommand']=!empty($aPost['id'])?"CMD_STATEGY_ROUTING|edit":"CMD_STATEGY_ROUTING|add";
			$param['sLogDesc']='编辑ipv4策略路由成功';
			DBHelper::saveData($param);
		}else{
			//ip地址
			$hIP=new TbaddressList();
			$aipc = new CDbCriteria();
			$aipc ->condition =" sIPV ='ipv4'";
			$aIPList=$hIP->findAll($aipc);
			$viewData['aIPList']=$aIPList;

			//应用
			$hModel=new TbDefinedApplication();
			$hC = new CDbCriteria();
			$hC->order = " sAppName ASC";
			$viewData['aApplications'] = $hModel->findAll($hC);
			/*//接口（聚合设备）
			$Model=new TbPortAggregation();
			$aAggregationList=$Model->findAll();
			$viewData['aAggregationList']=$aAggregationList;*/
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			$c->addCondition("sWorkMode='route'");
			$c->addCondition("sWorkMode='nat'" ,'OR');
			$viewData['netPortList']=$netPortModel->findAll($c);

			$this->render('strategy_route_save_ipv4',$viewData);
		}
	}
	public function actionStrategyRouteSaveIPV6()
	{
		if(Yii::app()->request->isPostRequest) {
			$aPost=(array)$this->getParam();
			//判断下一跳和接口
			if(!isset($aPost['iIfaceJump1']) && !isset($aPost['iIfaceJump2'])){
				$aJson['success'] =false;
				$aJson['msg'] =Yii::t('lang','接口和下一跳不能全为空，两者选其一或者都选');
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(empty($aPost['iIfaceID']) && isset($aPost['iIfaceJump1'])){
				$aJson['success'] =false;
				$aJson['msg'] =Yii::t('lang','接口不能为空');
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(empty($aPost['sJumpName']) && isset($aPost['iIfaceJump2'])){
				$aJson['success'] =false;
				$aJson['msg'] =Yii::t('lang','下一跳不能为空');
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(!empty($aPost['iIfaceID']) && !isset($aPost['iIfaceJump1'])){
				$aJson['success'] =false;
				$aJson['msg'] =Yii::t('lang','请在接口前打勾');
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(empty($aPost['sJumpName']) && isset($aPost['iIfaceJump2'])){
				$aJson['success'] =false;
				$aJson['msg'] =Yii::t('lang','请在接口前打勾');
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(!empty($aPost['sJumpName'])){
				$rs = $this->CheckIPV6($aPost['sJumpName'],1);
				if(!$rs){
					$aJson['success'] =false;
					$aJson['msg'] =Yii::t('lang','下一跳地址不是IPV6格式');
					echo CJSON::encode($aJson);
					Yii::app()->end();
				}
			}

			//判断协议和应用

			if(isset($aPost['iProtocolApp'])){
				if($aPost['iProtocolApp'] ==1){
					if(isset($aPost['sProtocol']) && empty($aPost['sProtocol'])){
						$aJson['success'] =false;
						$aJson['msg'] =Yii::t('lang','请选择一个协议');
						echo CJSON::encode($aJson);
						Yii::app()->end();
					}else{
						/*if($aPost['sProtocol'] =='TCP'|| $aPost['sProtocol'] =='UDP'){
							if(empty($aPost['iSourcePort']) && empty($aPost['iTargetPort'])){
								$aJson['success'] =false;
								$aJson['msg'] ="源端口和目的端口不能全为空";
								echo CJSON::encode($aJson);
								Yii::app()->end();
							}
						}*/
						if($aPost['sProtocol'] =='ICMPV6'){
							if(!empty($aPost['iSourcePort']) || !empty($aPost['iTargetPort'])){
								$aJson['success'] =false;
								$aJson['msg'] =Yii::t('lang','源端口和目的端口不能填');
								echo CJSON::encode($aJson);
								Yii::app()->end();
							}
						}
					}
				}
				if($aPost['iProtocolApp'] == 2){
					if(empty($aPost['iApplicationID'])){
						$aJson['success'] =false;
						$aJson['msg'] =Yii::t('lang','请选择一个应用');
						echo CJSON::encode($aJson);
						Yii::app()->end();
					}
				}
			}
			//判断优先级
			$iModel = new TbStrategyRoute();
			$ic = new CDbCriteria();
			if(isset($aPost['sPriority'])&&!empty($aPost['sPriority'])){
				if(isset($aPost['id'])&&!empty($aPost['id'])){
					$ic->condition=" sPriority = :sPriority and id <>:id and sIPV ='ipv6'";
					$ic->params=array(':sPriority'=>$aPost['sPriority'],':id'=>$aPost['id']);
					$levelcount = $iModel->count($ic);
				}else{
					$ic->condition=" sPriority = :sPriority and sIPV ='ipv6'";
					$ic->params=array(':sPriority'=>$aPost['sPriority']);
					$levelcount = $iModel->count($ic);
				}
				if($levelcount>0){
					$aJson['msg'] = Yii::t('lang','该优先级已经存在，请更换！');
					$aJson ['success'] = false;
					echo CJSON::encode($aJson);
					Yii::app()->end();
				}
			}
			$param['extData'] = $aPost;
			$param['hModel'] = new TbStrategyRoute();
			$param['sCommand']=!empty($aPost['id'])?"CMD_STATEGY_ROUTING|edit":"CMD_STATEGY_ROUTING|add";
			$param['sLogDesc']='编辑ipv6策略路由成功';
			DBHelper::saveData($param);
		}else{
			//ip地址
			$hIP=new TbaddressList();
			$aipc = new CDbCriteria();
			$aipc ->condition =" sIPV = 'ipv6' ";
			$aIPList=$hIP->findAll($aipc);
			$viewData['aIPList']=$aIPList;
			//应用
			$hModel=new TbDefinedApplication();
			$hC = new CDbCriteria();
			$hC->order = " sAppName ASC";
			$viewData['aApplications'] = $hModel->findAll($hC);
			/*//接口（聚合设备）
			$Model=new TbPortAggregation();
			$aAggregationList=$Model->findAll();
			$viewData['aAggregationList']=$aAggregationList;*/
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			$c->addCondition("sWorkMode='route'");
			$c->addCondition("sWorkMode='nat'" ,'OR');
			$viewData['netPortList']=$netPortModel->findAll($c);
			$this->render('strategy_route_save_ipv6',$viewData);
		}
	}
	//iSP路由头部-----------------------------------------------------
	public function actionGetHeaderTitleIspRoute(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle' =>Yii::t('lang', '所属ISP'),'data'=>'sBelongISP', 'sClass'=>'sBelongISP'),
				array('sTitle' =>Yii::t('lang', '下一跳地址'),'data'=>'sNextJump'),
				array('sTitle' =>Yii::t('lang', '流出网口'),'data'=>'sLan'),
				array('sTitle' =>Yii::t('lang', 'metric'),'data'=>'sMetric'),
				array('sTitle' =>Yii::t('lang', '状态'),'data'=>'iStatus','sClass'=>'iStatus'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//iSP路由列表
	public function actionIspRoute(){
		$this->render("isp_route");
	}
	public function actionIspRouteIPV4(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbIspRoute();
			$c = new CDbCriteria();
			$c->addCondition("sIPV='ipv4'");
			$param['criteria']=$c;
			$param['returnData'] = 2;
			$dataList = DBHelper::getDataList($param);

			$NetPortModel = new TbNetPort();
			$dataList['data'] = $NetPortModel->setLanList($dataList['data'] , 'sOutPort');

			echo CJSON::encode($dataList);
			Yii::app()->end();


		}else{
			$this->render('isp_route_ipv4');
		}
	}
	public function actionIspRouteIPV6(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbIspRoute();
			$c = new CDbCriteria();
			$c->addCondition("sIPV='ipv6'");
			$param['criteria']=$c;
			$param['returnData'] = 2;
			$dataList = DBHelper::getDataList($param);
			$NetPortModel = new TbNetPort();
			$dataList['data'] = $NetPortModel->setLanList($dataList['data'] , 'sOutPort');
			echo CJSON::encode($dataList);
			Yii::app()->end();
		}else{
			$this->render('isp_route_ipv6');
		}
	}
	//编辑iSP路由
	public function actionIspRouteSaveIPV4()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbIspRoute();
		if(Yii::app()->request->isPostRequest) {
			$param['sLogDesc']='编辑ipv4iSP路由成功';
			if(!empty($aPost['id'])){
				$oldData=$param['hModel']->find("id=:id",array(':id'=>$aPost['id']));
				$param['returnData']=2;
				$aJson=DBHelper::saveData($param);
				$newData=$param['hModel']->find("id=:id",array(':id'=>$aPost['id']));

				//send old data
				$sCommand="CMD_ISP_CONFIG|del|".CJSON::encode($oldData);
				DBHelper::saveCommand($sCommand);
				//send new data
				$sCommand="CMD_ISP_CONFIG|add|".CJSON::encode($newData);
				DBHelper::saveCommand($sCommand);
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}else{
				$param['sCommand']="CMD_ISP_CONFIG|add|".CJSON::encode($aPost);
				DBHelper::saveData($param);
			}
		}else{
			//已使用的网口
			/*$condit=new CDbCriteria();
			$condit->select="sOutPort";
			$condit->addCondition("sIPV='ipv4'");
			if(!empty($aPost['mid']))$condit->addCondition("id<>".$aPost['mid']);
			$exitsPort=$param['hModel']->findAll($condit);
			$exist=array();
			foreach($exitsPort as $port){
				$exist[]=$port['sOutPort'];
			}*/
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			//$c->addCondition("sWorkMode='route'");
//			$c->addNotInCondition("sPortName",$exist);
			$viewData['netPortList']=$netPortModel->findAll($c);
			//接口（聚合设备）
			/*$Model=new TbPortAggregation();
			$aAggregationList=$Model->findAll();
			$viewData['aAggregationList']=$aAggregationList;*/
			//isp地址
			$Model=new TbAddressISP();
			$aList=$Model->findAll("sIPV='ipv4'");
			$viewData['aIspList']=$aList;
			$this->render('isp_route_save_ipv4',$viewData);
		}
	}
	public function actionIspRouteSaveIPV6()
	{
		$aPost=(array)$this->getParam();
		$param['hModel'] = new TbIspRoute();
		if(Yii::app()->request->isPostRequest) {
			$param['sLogDesc']='编辑ipv6iSP路由成功';
			if(!empty($aPost['id'])){
				$oldData=$param['hModel']->find("id=:id",array(':id'=>$aPost['id']));
				$param['returnData']=2;
				$aJson=DBHelper::saveData($param);
				$newData=$param['hModel']->find("id=:id",array(':id'=>$aPost['id']));
				//send old data
				$sCommand="CMD_ISP_CONFIG|update_old|".CJSON::encode($oldData);
				DBHelper::saveCommand($sCommand);
				//send new data
				$sCommand="CMD_ISP_CONFIG|update_new|".CJSON::encode($newData);
				DBHelper::saveCommand($sCommand);
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}else{
				$param['sCommand']="CMD_ISP_CONFIG|add";
				DBHelper::saveData($param);
			}
		}else{
			//已使用的网口
			/*$condit=new CDbCriteria();
			$condit->select="sOutPort";
			$condit->addCondition("sIPV='ipv6'");
			if(!empty($aPost['mid']))$condit->addCondition("id<>".$aPost['mid']);
			$exitsPort=$param['hModel']->findAll($condit);
			$exist=array();
			foreach($exitsPort as $port){
				$exist[]=$port['sOutPort'];
			}*/
			//网口
			$netPortModel=new TbNetPort();
			$c=new CDbCriteria();
			//$c->addCondition("sWorkMode='route' and sIPV6Address!=''");
			//$c->addCondition("sWorkMode='nat'","OR");
//			$c->addNotInCondition("sPortName",$exist);
			$viewData['netPortList']=$netPortModel->findAll($c);
			//接口（聚合设备）
			/*$Model=new TbPortAggregation();
			$aAggregationList=$Model->findAll();
			$viewData['aAggregationList']=$aAggregationList;*/
			//isp地址
			$Model=new TbAddressISP();
			$aList=$Model->findAll("sIPV='ipv6'");
			$viewData['aIspList']=$aList;
			$this->render('isp_route_save_ipv6',$viewData);
		}
	}
	//动态路由=================================
	public function actionDynamicRoute(){
		$this->render('dynamic_route');
	}
	public function actionDynamicRouteOSPF_V(){
		$config=new TbConfig();
		$info=$config->find("sName='OSPFSet'");
		$data['setting']=CJSON::decode($info['sValue']);
		$this->render('dynamic_route_ospf_v',$data);
	}
	//OSPF V2   IPV4
	public function actionDynamicRouteOSPF(){
		$config=new TbConfig();
		$info=$config->find("sName='OSPFSet'");
		$data['setting']=CJSON::decode($info['sValue']);
		$this->render('dynamic_route_ospf',$data);
	}
	//OSPF V3   IPV6
	public function actionDynamicRouteOSPF_V3(){
		$config=new TbConfig();
		$info=$config->find("sName='OSPFSetV3'");
		$data['setting']=CJSON::decode($info['sValue']);
		$this->render('dynamic_route_ospf_v3',$data);
	}
	public function actionDynamicRouteRIP(){
		$config=new TbConfig();
		$info=$config->find("sName='RIPSet'");
		$data['setting']=CJSON::decode($info['sValue']);
		$this->render('dynamic_route_rip',$data);
	}
	public function actionDynamicRouteBGP(){
		$config=new TbConfig();
		$info=$config->find("sName='BGPSetting'");
		$data['setting']=CJSON::decode($info['sValue']);
		$this->render('dynamic_route_bgp',$data);
	}
	public function actionOSPFSet()
	{
		$aPost=(array)$this->getParam();
		$config=new TbConfig();
		if(empty($aPost['sOSPFRouterID'])) $this->showMessage(false,Yii::t('lang','路由器ID不能为空'));
		if(empty($aPost['sOSPFRouterON']))$aPost['sOSPFRouterON']='0';
		if(empty($aPost['sOSPFLinkPointer']))$aPost['sOSPFLinkPointer']='0';
		if(empty($aPost['sOSPFRIP']))$aPost['sOSPFRIP']='0';
		if(empty($aPost['sOSPFStatic']))$aPost['sOSPFStatic']='0';
		if(empty($aPost['sOSPFDefaultRouter']))$aPost['sOSPFDefaultRouter']='0';
		if(empty($aPost['sOSPFBGP']))$aPost['sOSPFBGP']='0';

		//验证ID
		$res =$config->find("sName='OSPFSetV3'");
		$result = CJSON::decode($res->attributes['sValue']);
		if($result['sOSPFRouterID'] == $aPost['sOSPFRouterID']){
			$aJson['success'] = false;
			$aJson['msg'] = Yii::t('lang','已存在路由ID');
			echo CJSON::encode($aJson);
			Yii::app()->end();
		}

		$config->sName="OSPFSet";
		$config->sValue=CJSON::encode($aPost);
		$config->sMark="OSPF设置";
		$aJson=DBHelper::saveConfig($config,'设置成功',2);
		//$aJson=DBHelper::saveConfig($config,'设置成功！','保存配置',2);
		$cmd="CMD_DYNAMICROUTING_OSPF";
		DBHelper::saveCommand($cmd);
		echo CJSON::encode($aJson);
		Yii::app()->end();
	}
	//动态路由--各区头部-----------------------------------------------------
	public function actionGetHeaderTitleDynamicRouteArea(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang', '区域'),'data'=>'sAreaIP'),
				array('sTitle'=>Yii::t('lang', '类型'),'data'=>'sType'),
				array('sTitle'=>Yii::t('lang', '认证'),'data'=>'sAuthentication'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//动态路由--各区列表
	public function actionDynamicRouteArea(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbDynamicRouteArea();
			DBHelper::getDataList($param);
		}else{
			$this->render('dynamic_route_area');
		}
	}
	//编辑动态路由--各区
	public function actionDynamicRouteAreaSave()
	{
		if(Yii::app()->request->isPostRequest) {
			$aPost=(array)$this->getParam();
			$param['hModel'] = new TbDynamicRouteArea();
			$param['sLogDesc']='编辑动态路由--各区成功';
			$param['returnData']=2;

			$checkName = $param['hModel']->find("sAreaIP=:sAreaIP AND id!=:id" , array(':sAreaIP'=>$aPost['sAreaIP'] , ':id'=>$aPost['id']));
            if($checkName){
                $this->showMessage(false,Yii::t('lang','区域')."{$aPost['sAreaIP']}".Yii::t('lang','已存在，请更换'));
            }

			$aJson=DBHelper::saveData($param);
			$cmd="CMD_DYNAMICROUTING_OSPF";
			DBHelper::saveCommand($cmd);
			echo CJSON::encode($aJson);
			Yii::app()->end();
		}else{
			$this->render('dynamic_route_area_save');
		}
	}
	//动态路由--各网络头部-----------------------------------------------------
	public function actionGetHeaderTitleDynamicRouteNet(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang', '网络'),'data'=>'sIP'),
				array('sTitle'=>Yii::t('lang', '区域'),'data'=>'rArea','sClass'=>'rArea'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//动态路由--各网络列表
	public function actionDynamicRouteNet(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbDynamicRouteNet();
			$c=new CDBCriteria();
			$c->with=array('rArea');
			$param['criteria']=$c;
			DBHelper::getDataList($param);
		}else{
			$this->render('dynamic_route_net');
		}
	}
	//编辑动态路由--各网络
	public function actionDynamicRouteNetSave()
	{
		if(Yii::app()->request->isPostRequest) {
			$aPost=(array)$this->getParam();
			if(!preg_match(Regexp::$ospf_preg,$aPost['sIP'])) $this->showMessage(false,Yii::t('lang','IP/掩码格式有误'));
			$param['hModel'] = new TbDynamicRouteNet();
			$param['sLogDesc']='编辑动态路由--各网络成功';
			$param['returnData']=2;
			$aJson=DBHelper::saveData($param);
			$cmd="CMD_DYNAMICROUTING_OSPF";
			DBHelper::saveCommand($cmd);
			echo CJSON::encode($aJson);
			Yii::app()->end();
		}else{
			$hModel=new TbDynamicRouteArea();
			$data['areaList']=$hModel->findAll();
			$this->render('dynamic_route_net_save',$data);
		}
	}
	//动态路由--各端口头部-----------------------------------------------------
	public function actionGetHeaderTitleDynamicRoutePort(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle' =>Yii::t('lang', '接口'),'data'=>'sLan'),
				array('sTitle' =>Yii::t('lang', 'IP/掩码'),'data'=>'sIP'),
				array('sTitle' =>Yii::t('lang', '认证'),'data'=>'sAuthentication'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//动态路由--各端口列表
	public function actionDynamicRoutePort(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbDynamicRoutePort();
			$param['returnData'] = 2;
			$dataList = DBHelper::getDataList($param);
			$NetPortModel = new TbNetPort();
			$dataList['data'] = $NetPortModel->setLanList($dataList['data'] , 'sPort');
			echo CJSON::encode($dataList);
			Yii::app()->end();
		}else{
			$this->render('dynamic_route_port');
		}
	}
	//编辑动态路由--各端口
	public function actionDynamicRoutePortSave()
	{
		if(Yii::app()->request->isPostRequest) {
			$aPost=(array)$this->getParam();
			$param['hModel'] = new TbDynamicRoutePort();
			$param['sCommand']=!empty($aPost['id'])?"CMD_DYNAMICROUTING_OSPF|edit":"CMD_DYNAMICROUTING_OSPF|add";
			$param['sLogDesc']='编辑动态路由--各端口成功';
			DBHelper::saveData($param);
		}else{
			$hModel	= new TbNetPort();
			$c 		= new CDbCriteria();
			//开启的端口  工作模式为路由模式
			$c->addCondition('iStatus=1');
			$c->addCondition("sWorkMode='route' OR sWorkMode='nat'");
			$data['portList']=$hModel->findAll($c);
			$this->render('dynamic_route_port_save',$data);
		}
	}

	//动态路由V3界面
	public function actionOSPFSet_v3()
	{
		$aPost=(array)$this->getParam();
		$config=new TbConfig();
		if(empty($aPost['sOSPFRouterID'])) $this->showMessage(false,Yii::t('lang','路由器ID不能为空'));
		if(empty($aPost['sOSPFRouterON']))$aPost['sOSPFRouterON']='0';
		if(empty($aPost['sOSPFLinkPointer']))$aPost['sOSPFLinkPointer']='0';
		if(empty($aPost['sOSPFRIP']))$aPost['sOSPFRIP']='0';
		if(empty($aPost['sOSPFStatic']))$aPost['sOSPFStatic']='0';
		if(empty($aPost['sOSPFDefaultRouter']))$aPost['sOSPFDefaultRouter']='0';
		if(empty($aPost['sOSPFBGP']))$aPost['sOSPFBGP']='0';

		//验证ID
		$res =$config->find("sName='OSPFSet'");
		$result = CJSON::decode($res->attributes['sValue']);
		if($result['sOSPFRouterID'] == $aPost['sOSPFRouterID']){
			$aJson['success'] = false;
			$aJson['msg'] = Yii::t('lang','已存在路由ID');
			echo CJSON::encode($aJson);
			Yii::app()->end();
		}

		$config->sName="OSPFSetV3";
		$config->sValue=CJSON::encode($aPost);
		$config->sMark='OSPF设置';
		$aJson=DBHelper::saveConfig($config,'设置成功',2);
		//$aJson=DBHelper::saveConfig($config,'设置成功！','保存配置',2);
		$cmd="CMD_DYNAMICROUTING_OSPF_V3";
		DBHelper::saveCommand($cmd);
		echo CJSON::encode($aJson);
		Yii::app()->end();
	}

	public function actionGetDynamicOSPF_V3_INTERFACE(){
		$aData=array(
			array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
			array('sTitle'=>Yii::t('lang', '接口名称'),'data'=>'sLan'),
			array('sTitle'=>Yii::t('lang', '网络地址'),'data'=>'sIP'),
			array('sTitle'=>Yii::t('lang', 'iCost'),'data'=>'iCost'),
			array('sTitle'=>Yii::t('lang', 'Hello间隔'),'data'=>'iHelloDiff'),
			array('sTitle'=>Yii::t('lang', 'Dead间隔'),'data'=>'iDeadDiff'),
			array('sTitle'=>Yii::t('lang', '重传间隔'),'data'=>'iResendDiff'),
			//array('sTitle'=>'状态','data'=>'iStatus'),
			array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
			array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}

	//动态路由OSPF V3 --接口列表
	public function actionDynamicOSPF_V3_INTERFACE(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] 				= new TbdynamicrouteOspfV3();
			$param['returnData'] 			= 2;
			$dataList 						= DBHelper::getDataList($param);
			$NetPortModel 					= new TbNetPort();
			$dataList['data'] 				= $NetPortModel->setLanList($dataList['data'] , 'sPort');
			echo CJSON::encode($dataList);
			Yii::app()->end();
		}else{
			$config							= new TbConfig();
			$info							= $config->find("sName='OSPFSetV3'");
			$data['setting']				= CJSON::decode($info['sValue']);
			$viewData						= array();
			if(isset($data['setting']['sOSPFRouterON'])&&$data['setting']['sOSPFRouterON']=="1"){
				$viewData['sOSPFRouterON'] 	= 1;
			}else{
				$viewData['sOSPFRouterON'] 	= 0;
			}
			$this->render('dynamic_route_ospf_interface_v3',$viewData);
		}
	}

	//动态路由OSPF V3 --接口保存
	public function actionDynamicOSPF_V3_INTERFACE_Save(){
		$aPost=(array)$this->getParam();
		if(Yii::app()->request->isPostRequest) {
			$extData				= array();
			$extData['iCost']		= empty($aPost['iCost']) 		? 	1 : intval($aPost['iCost']) ;
			$extData['iHelloDiff']	= empty($aPost['iHelloDiff']) 	? 	1 : intval($aPost['iHelloDiff']) ;
			$extData['iDeadDiff']	= empty($aPost['iDeadDiff']) 	? 	1 : intval($aPost['iDeadDiff']) ;
			$extData['iResendDiff']	= empty($aPost['iResendDiff']) 	? 	1 : intval($aPost['iResendDiff']) ;
			$extData['iStatus']		= empty($aPost['iStatus']) 		? 	1 : intval($aPost['iStatus']) ;
			$param['hModel'] 		= new TbdynamicrouteOspfV3();
			//$param['sCommand']		= !empty($aPost['id'])?"CMD_DYNAMICROUTING_OSPF_V3|edit":"CMD_DYNAMICROUTING_OSPF_V3|add";
			$param['sLogDesc']		= '编辑动态路由--接口定义成功';
			DBHelper::saveData($param);
		}else{
			$hModel					= new TbNetPort();
			$c 						= new CDbCriteria();
			//查询已经存在于OPSF_V3里的网口  下拉菜单不需要此网口
			$sNot 					= TbdynamicrouteOspfV3::model()->getOSPF_V3_NetPort(0);
			//判断是否编辑
			if(!empty($aPost['sPort'])){
				$sNot 				= array_diff($sNot,array($aPost['sPort']));
			}
			$c->addNotInCondition("sPortName",$sNot);
			//开启的端口   工作模式为路由模式
			$c->addCondition('iStatus=1');
			$c->addCondition("sIPV6Address<>''");
			$c->addCondition("sWorkMode='route' OR sWorkMode='nat'");
			$data['portList']=$hModel->findAll($c);
			//判断是否虚拟网口
			if(!empty($data['portList'])){
				$tmp 				=  array();
				foreach($data['portList'] as $item){
					if($this->CheckVirthNet($item['sPortName'])){
							continue;
					}
					array_push($tmp,$item);
				}
				$data['portList']		= $tmp;
			}
			$this->render('dynamic_ospf_v3_interface_save',$data);
		}
	}
	//rip路由配置
	public function actionRIPSet()
	{
		$aPost=(array)$this->getParam();
		$config=new TbConfig();
		if(empty($aPost['sRIPRouterON']))$aPost['sRIPRouterON']='0';
		$config->sName="RIPSet";
		$config->sValue=CJSON::encode($aPost);
		$config->sMark="rip路由配置";
		$config->sCommand="CMD_DYNAMICROUTING_RIP";
		DBHelper::saveConfig($config,'设置成功',1,false);
		//DBHelper::saveConfig($config,'设置成功！','保存配置',1,false);
	}
	//动态路由--RIP网络头部-----------------------------------------------------
	public function actionGetHeaderTitleDynamicRouteRipNet(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang', 'IP/掩码'),'data'=>'sIP'),
			/*array('sTitle'=>'掩码','data'=>'sMask'),*/
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//动态路由--RIP网络列表
	public function actionDynamicRouteRipNet(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbDynamicRouteRipNet();
			DBHelper::getDataList($param);
		}else{
			$this->render('dynamic_route_rip_net');
		}
	}
	//编辑动态路由--RIP网络
	public function actionDynamicRouteRipNetSave()
	{
		if(Yii::app()->request->isPostRequest) {

			$aPost=(array)$this->getParam();
			if(!preg_match(Regexp::$ospf_preg,$aPost['sIP'])) $this->showMessage(false,Yii::t('lang','IP/掩码格式有误'));
			$param['hModel'] = new TbDynamicRouteRipNet();
			$param['sLogDesc']='编辑动态路由--RIP网络成功';
			$param['returnData']=2;
			$aJson=DBHelper::saveData($param);
			$cmd="CMD_DYNAMICROUTING_RIP";
			DBHelper::saveCommand($cmd);
			echo CJSON::encode($aJson);
			Yii::app()->end();
		}else{
			$this->render('dynamic_route_rip_net_save');
		}
	}
	//动态路由--RIP端口头部-----------------------------------------------------
	public function actionGetHeaderTitleDynamicRouteRipPort(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				//array('sTitle'=>Yii::t('lang', '端口名称'),'data'=>'sName'),
				array('sTitle'=>Yii::t('lang', '端口名称'),'data'=>'sLan'),
				//array('sTitle'=>Yii::t('lang', '发送控制'),'data'=>'sSendControl'),
				//array('sTitle'=>Yii::t('lang', '接收控制'),'data'=>'sReceiveControl'),
				array('sTitle'=>Yii::t('lang', '认证方式'),'data'=>'sAuthentication'),
				array('sTitle'=>Yii::t('lang', '认证模式'),'data'=>'sAuthenticationMode'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//动态路由--RIP端口列表
	public function actionDynamicRouteRipPort(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] 		= new TbDynamicRouteRipPort();
			$param['returnData'] 	= 2;
			$result 				= array();
			$result 				= DBHelper::getDataList($param);
			$result['data'] 		= TbNetPort::model()->setLanList($result['data'],'sName');
			$this->showMessage(true,'success',$result);

		}else{
			$this->render('dynamic_route_rip_port');
		}
	}
	//编辑动态路由--RIP端口
	public function actionDynamicRouteRipPortSave()
	{
			$aPost=(array)$this->getParam();
		if(Yii::app()->request->isPostRequest) {
			$param['hModel'] = new TbDynamicRouteRipPort();
			$param['sLogDesc']='编辑动态路由--RIP端口成功';
			$param['sCommand']=!empty($aPost['id'])?"CMD_DYNAMICROUTING_RIP|edit":"CMD_DYNAMICROUTING_RIP|add";
			if(empty($aPost['sAuthenticationMode'])) $aPost['sAuthenticationMode'] 	= '';
			if(empty($aPost['sSingleSecret'])) 		 $aPost['sSingleSecret'] 		= '';
			if(empty($aPost['sChainName'])) 		 $aPost['sChainName'] 			= '';
			$aData=array('sChainGroup'=>array());
			if(!empty($aPost['iSecretID'])) {
				foreach ($aPost['iSecretID'] as $k => $v) {
					if(!empty($aPost['iSecretID'][$k])) {
						$aData['sChainGroup'][] =array('id'=>$aPost['iSecretID'][$k],'value'=>$aPost['iSecretValue'][$k]);
					}
				}
				$aData['sChainGroup']=CJSON::encode($aData['sChainGroup']);
			}
			if(count($aData['sChainGroup'])>0)$param['extData']=$aData;
			$param['aPost']	= $aPost;
			DBHelper::saveData($param);
		}else{
			$hModel		= new TbNetPort();
			$c 			= new CDbCriteria();
			$rip_port 	= $hModel->getRipNetport($aPost['id']);
			//开启的端口  工作模式为路由模式
			$c->addCondition('iStatus=1');
			$c->addCondition("sWorkMode='route' OR sWorkMode='nat'");
			$c->addNotInCondition('sPortName', explode(",", $rip_port));
			$data['portList']=$hModel->findAll($c);
			$this->render('dynamic_route_rip_port_save',$data);
		}
	}
	//动态路由--BGP邻居头部-----------------------------------------------------
	public function actionGetHeaderTitleDynamicRouteBgpNeighbor(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang', 'IP'),'data'=>'sIP'),
				array('sTitle'=>Yii::t('lang', '远程AS'),'data'=>'sRemoteAS'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//动态路由--BGP邻居列表
	public function actionDynamicRouteBgpNeighbor(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbDynamicRouteBgpNeighbor();
			DBHelper::getDataList($param);
		}else{
			$this->render('dynamic_route_bgp_neighbor');
		}
	}
	//编辑动态路由--BGP邻居
	public function actionDynamicRouteBgpNeighborSave()
	{
		if(Yii::app()->request->isPostRequest) {
			$aPost=(array)$this->getParam();
			$param['hModel'] = new TbDynamicRouteBgpNeighbor();
			$param['sLogDesc']='编辑动态路由--BGP邻居成功';
			$param['returnData']=2;
			$aJson=DBHelper::saveData($param);
			$cmd="CMD_DYNAMICROUTING_BGP";
			DBHelper::saveCommand($cmd);
			echo CJSON::encode($aJson);
			Yii::app()->end();
		}else{
			$this->render('dynamic_route_bgp_neighbor_save');
		}
	}
	//动态路由--BGP网络头部-----------------------------------------------------
	public function actionGetHeaderTitleDynamicRouteBgpNet(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				array('sTitle'=>Yii::t('lang', 'IP/掩码'),'data'=>'sIP'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//动态路由--BGP网络列表
	public function actionDynamicRouteBgpNet(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbDynamicRouteBgpNet();
			DBHelper::getDataList($param);
		}else{
			$this->render('dynamic_route_bgp_net');
		}
	}
	//编辑动态路由--BGP网络
	public function actionDynamicRouteBgpNetSave()
	{
		if(Yii::app()->request->isPostRequest) {
			$aPost=(array)$this->getParam();
			if(!preg_match(Regexp::$ospf_preg,$aPost['sIP'])) $this->showMessage(false,Yii::t('lang','IP/掩码格式有误'));
			$param['hModel'] = new TbDynamicRouteBgpNet();
			$param['sLogDesc']='编辑动态路由--BGP网络成功';
			$param['returnData']=2;
			$aJson=DBHelper::saveData($param);
			$cmd="CMD_DYNAMICROUTING_BGP";
			DBHelper::saveCommand($cmd);
			echo CJSON::encode($aJson);
			Yii::app()->end();
		}else{
			$hModel=new TbNetPort();
			$data['portList']=$hModel->findAll();
			$this->render('dynamic_route_bgp_net_save',$data);
		}
	}
	//动态路由--BGP端口头部-----------------------------------------------------
	public function actionGetHeaderTitleDynamicRouteBgpPort(){
		$aData=array(
				array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
				//array('sTitle'=>'名称','data'=>'sPort'),
				array('sTitle'=>Yii::t('lang', '名称'),'data'=>'sLan'),
				array('sTitle'=>Yii::t('lang', 'IP/掩码'),'data'=>'sIP'),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
				array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	//动态路由--BGP端口列表
	public function actionDynamicRouteBgpPort(){
		if(Yii::app()->request->isPostRequest){
			$param['hModel'] = new TbDynamicRouteBgpPort();
			$param['returnData'] 	= 2;
			$result 		 		= DBHelper::getDataList($param);
			$result['data'] 		= TbNetPort::model()->setLanList($result['data'],'sPort');
			$this->showMessage(true,'success',$result);
		}else{
			$this->render('dynamic_route_bgp_port');
		}
	}
	//编辑动态路由--BGP端口
	public function actionDynamicRouteBgpPortSave()
	{
		$aPost=(array)$this->getParam();
		if(Yii::app()->request->isPostRequest) {
			$param['hModel'] = new TbDynamicRouteBgpPort();
			$param['sLogDesc']='编辑动态路由--BGP端口成功';
			$param['sCommand']=!empty($aPost['id'])?"CMD_DYNAMICROUTING_BGP|edit":"CMD_DYNAMICROUTING_BGP|add";
			DBHelper::saveData($param);
		}else{
			$hModel 	= new TbNetPort();
			$bgp_port 	= $hModel->getBgpNetport($aPost['id']);
			$c 			= new CDbCriteria();
			$c->select  = "sPortName,sLan";
			//开启的端口  工作模式为路由模式
			$c->addCondition('iStatus=1');
			$c->addCondition("sWorkMode='route' OR sWorkMode='nat'");
			$c->addNotInCondition('sPortName', explode(",", $bgp_port));
			$data['portList'] = $hModel->findAll($c);
			$this->render('dynamic_route_bgp_port_save',$data);
		}
	}
	/**
	 * 删除数据，统一函数
	 */
	public function actionDelData(){
		$hPost=$this->getParam();
		$param['hModel']=new stdClass();
		switch($hPost->act) {
			case 'virtualLine':	//虚拟线
				$param['hModel'] = new TbVirtualLine();
				$param['sLogDesc']='删除虚拟线成功';
				$param['sCommand']="CMD_SET_VIRTUAL_LINE|del";
				break;
			case 'PortMirror':	//端口镜像
				$param['hModel'] = new TbPortMirror();
				$param['sLogDesc']='删除端口镜像成功';
				$param['sCommand']="CMD_MIRROR|del";
				break;
			case 'bridgeDevice':	//桥设备
				$param['hModel'] = new TbBridgeDevice();
				$param['sLogDesc']='删除桥设备成功';
				$param['sCommand']="CMD_BRIDGE_CONFIG|del";
				break;
			case 'dialDevice':	//拨号设备
				$param['hModel'] = new TbDialDevice();
				$param['sLogDesc']='删除拨号设备成功';
				$param['sCommand']="CMD_DIAL|del";
				break;
			case 'portAggregation':	//端口聚合
				$param['hModel'] = new TbPortAggregation();
				$param['sLogDesc']='删除端口聚合成功';
				$param['sCommand']="CMD_IFACE_AGGRE|del";
				break;
			case 'vlanDevice':	//vlan设备
				$param['hModel'] = new TbVlanDevice();
				$param['sCommand']="CMD_VLAN|del";
				$param['sLogDesc']='删除vlan设备成功';
				break;
			case 'staticRoute':	//静态路由
				$param['hModel'] = new TbStaticRoute();
				$param['sLogDesc']='删除静态路由成功';
				$param['sCommand']="CMD_STATICROUTE|del";
				break;
			case 'strategyRoute':	//策略路由
				/*$gPost = (array)$this->getParam();
                $aid=explode(",",$gPost['aId']);
                foreach($aid as $k =>$v){
                    $gModel = new TbStrategyRoute();
                    $gres = $gModel->findAll('id ='.$v);
                    foreach($gres as $key =>$val){
                        if($val['iStatus'] ==1){
                            if($val['iProtocolApp'] ==2){
                                $sql = "Update m_tbdefined_application Set sCount= sCount-1 WHERE  iMark =".$val['iApplicationID'];
                                Yii::app()->db->createCommand($sql)->execute();
                            }
                        }

                    }
                }*/
				$param['hModel'] = new TbStrategyRoute();
				$param['sLogDesc']='删除策略路由成功';
				$param['sCommand']="CMD_STATEGY_ROUTING|del";
				break;
			case 'ispRoute':	//isp路由
				$param['hModel'] = new TbIspRoute();
				$param['sLogDesc']='删除isp路由成功';
				$param['sCommand']="CMD_ISP_CONFIG|del";
				break;
			case 'dynamicRouteArea':	//动态路由-区
				$param['hModel'] = new TbDynamicRouteArea();
				$param['sLogDesc']='删除动态路由（各区）成功';
				$param['returnData']=2;
				break;
			case 'dynamicRouteNet':	//动态路由-网络
				$param['hModel'] = new TbDynamicRouteNet();
				$param['sLogDesc']='删除动态路由（各网络）成功';
				$param['returnData']=2;
				break;
			case 'dynamicRoutePort':	//动态路由-接口
				$param['hModel'] = new TbDynamicRoutePort();
				$param['sLogDesc']='删除动态路由（各接口）成功';
				$param['sCommand']="CMD_DYNAMICROUTING_OSPF|del";
				break;
			case 'dynamicRouteRipNet':	//动态路由-rip网络
				$param['hModel'] = new TbDynamicRouteRipNet();
				$param['sLogDesc']='删除动态rip路由（各网络）成功';
				$param['returnData']=2;
				break;
			case 'dynamicRouteRipPort':	//动态路由-rip接口
				$param['hModel'] = new TbDynamicRouteRipPort();
				$param['sLogDesc']='删除动态rip路由（各接口）成功';
				$param['sCommand']="CMD_DYNAMICROUTING_RIP|del";
				break;
			case 'dynamicRouteBgpNet':	//动态路由-bgp网络
				$param['hModel'] = new TbDynamicRouteBgpNet();
				$param['sLogDesc']='删除动态路由bgp网络成功';
				$param['returnData']=2;
				break;
			case 'dynamicRouteBgpNeighbor':	//动态路由-bgp邻居
				$param['hModel'] = new TbDynamicRouteBgpNeighbor();
				$param['sLogDesc']='删除动态路由bgp邻居成功';
				$param['returnData']=2;
				break;
			case 'dynamicRouteBgpPort':	//动态路由-bgp端口
				$param['hModel'] = new TbDynamicRouteBgpPort();
				$param['sLogDesc']='删除动态路由bgp端口成功';
				$param['sCommand']="CMD_DYNAMICROUTING_BGP|del";
				break;
			case 'dynamicrouteOspfV3':	//动态路由-bgp端口
				$param['hModel'] = new TbdynamicrouteOspfV3();
				$param['sLogDesc']='删除动态路由OSPF_V3接口成功';
				//$param['sCommand']="CMD_DYNAMICROUTING_OSPF_V3|del";
				break;
			default:
				$aJson ['success'] = false;
				$aJson ['msg'] = Yii::t('lang','操作失败').$hPost->act;
				echo CJSON::encode($aJson);
				Yii::app()->end();
		}
		$rs=DBHelper::delData($param);
		//保存数据后才发命令
		$ospf=array('dynamicRouteArea','dynamicRouteNet');
		$rip=array('dynamicRouteRipNet');
		$bgp=array('dynamicRouteBgpNet','dynamicRouteBgpNeighbor');
		if(in_array($hPost->act,$ospf)){
			$cmd="CMD_DYNAMICROUTING_OSPF";
			DBHelper::saveCommand($cmd);
			echo CJSON::encode($rs);
			Yii::app()->end();
		}else if(in_array($hPost->act,$rip)){
			$cmd="CMD_DYNAMICROUTING_RIP";
			DBHelper::saveCommand($cmd);
			echo CJSON::encode($rs);
			Yii::app()->end();
		}else if(in_array($hPost->act,$bgp)){
			$cmd="CMD_DYNAMICROUTING_BGP";
			DBHelper::saveCommand($cmd);
			echo CJSON::encode($rs);
			Yii::app()->end();
		}
	}

	/**
	 * 手动解锁，统一函数
	 */
	public  function actionHandUnlock(){
		$hPost=$this->getParam();
		$param['hModel']=new stdClass();
		switch($hPost->act) {
			case 'netPort':	//网口配置
				$param['hModel'] = new TbNetPort();
				$param['sCommand']="CMD_CONIFG_INTERFACE|enable";
				break;
			case 'PortMirror':	//端口镜像
				$param['hModel'] = new TbPortMirror();
				$param['sCommand']="CMD_MIRROR|enable";
				break;
			case 'virtualLine':	//虚拟线
				$param['hModel'] = new TbVirtualLine();
				$param['sCommand']="CMD_SET_VIRTUAL_LINE|enable";
				break;
			case 'bridgeDevice':	//桥设备
				$param['hModel'] = new TbBridgeDevice();
				$param['sCommand']="CMD_BRIDGE_CONFIG|enable";
				break;
			case 'dialDevice':	//拨号设备
				$param['hModel'] = new TbDialDevice();
				$param['sCommand']="CMD_DIAL|enable";
				break;
			case 'portAggregation':	//端口聚合
				$param['hModel'] = new TbPortAggregation();
				$param['sCommand']="CMD_IFACE_AGGRE|enable";
				break;
			case 'vlanDevice':	//vlan设备
				$param['hModel'] = new TbVlanDevice();
				$param['sCommand']="CMD_VLAN|enable";
				break;
			case 'staticRoute':	//静态路由
				$param['hModel'] = new TbStaticRoute();
				$param['sCommand']="CMD_STATICROUTE|enable";
				break;
			case 'strategyRoute':	//策略路由
				$param['hModel'] = new TbStrategyRoute();
				$param['sCommand']="CMD_STATEGY_ROUTING|enable";
				break;
			case 'ispRoute':	//isp路由
				$param['hModel'] = new TbIspRoute();
				$oldData=$param['hModel']->find("id=:id",array(':id'=>$hPost->id));
				$param['returnData']=2;
				$aJson=DBHelper::HandUnlock($param);
				$newData=$param['hModel']->find("id=:id",array(':id'=>$hPost->id));
				$sCommand="CMD_ISP_CONFIG|del|".CJSON::encode($oldData);
				DBHelper::saveCommand($sCommand);
				$sCommand="CMD_ISP_CONFIG|add|".CJSON::encode($newData);
				DBHelper::saveCommand($sCommand);
				echo CJSON::encode($aJson);
				Yii::app()->end();
				break;
		}
		DBHelper::HandUnlock($param);
	}

	//DHCP配置--------------------------------------------
	public function actionDHCP()
	{
		$this->render('dhcp_setting');
	}

	public function actionDhcpIPV4(){
        $aPost=(array)$this->getParam();

        $dModel = new Tbdhcpfour();
		//单次时间计划
		$hModel=new TbTimePlanSingle();
		$data['planList']=$hModel->findAll();
		//网络端口
		$hPort=new TbNetPort();
		$data['netPort']=$hPort->findAll(array(
			'condition' => '`iStatus`=1 and `sIPV4Address`<>""'
		));
		$arr = json_decode(CJSON::encode($data['netPort']),TRUE);
		if(Yii::app()->request->isPostRequest){
			foreach($arr as $v){
				if($aPost['pn']===$v['sPortName']){
					$v['sIPV4Address']=explode(',',$v['sIPV4Address']);
					echo json_encode($v['sIPV4Address']);die;
				}
			}
		}else{
			$sValue=$dModel->find("id=:id",array(":id"=>$aPost['id']));
			foreach($arr as $v){
				if($sValue->sDhcpName===$v['sPortName']){
					$sValue->sDhcpServerIPs=explode(',',$v['sIPV4Address']);

				}
			}
		}
		$data['setting']=$sValue;
		$this->render('dhcp_ipv4',$data);
	}

	public function actionIPV4Info(){
        $aPost=(array)$this->getParam();
        if(Yii::app()->request->isPostRequest){
            if($aPost['ip']!=''){
                $ip=explode("/",$aPost['ip']);
                $str="";
                for($i=0;$i<32;$i++){
                    if($i<intval($ip[1])){
                        $str.="1";
                    }else{
                        $str.="0";
                    }
                    if(strlen($str)%8==0){
                        $mask[]=bindec(intval(substr($str,$i-7,8)));
                    }
                }
                $data['sDhcpServerMask']=implode('.',$mask);
                $sum=pow(2,intval(32-$ip[1]));
                $ips=explode('.',$ip[0]);
                for($j=0;$j*$sum<256;$j++){
                    if(intval($ips[3])>$j*$sum&&intval($ips[3])<($j+1)*$sum){
                        $ips[3]=$j*$sum;
                        //$data['sDhcpGateWay']=implode('.',$ips);
                        $ips[3]=$j*$sum+1;
                        $data['sDhcpIPStart']=implode('.',$ips);
                        $ips[3]=($j+1)*$sum-2;
                        $data['sDhcpIPEnd']=implode('.',$ips);
                        break;
                    }else{
                        //$data['sDhcpGateWay']	= '';
                        $data['sDhcpIPStart']	= '';
                        $data['sDhcpIPEnd']		= '';
                    }
                }
				//网关的IP应该为服务器的IP  并非网段地址
				$data['sDhcpGateWay']			= $ip[0];
                echo json_encode($data);die;
            }
        }
    }

	public function actionGetHeaderTitleDhcp4(){
		$aData=array(
			array('sTitle' => 'ID','data'=>'id', 'bVisible'=>false),
			array('sTitle'=>Yii::t('lang','网口名称'),'data'=>'sPortNameLan'),
			array('sTitle'=>Yii::t('lang','IP地址'),'data'=>'sDhcpServerIP'),
			array('sTitle'=>Yii::t('lang','掩码'),'data'=>'sDhcpServerMask'),
			array('sTitle'=>Yii::t('lang','网关'),'data'=>'sDhcpGateWay'),
			array('sTitle'=>Yii::t('lang','DNS服务器'),'data'=>'sDhcpDNSIP'),
			array('sTitle'=>Yii::t('lang','DNS备用服务器'),'data'=>'sDhcpBackupDNSIP','width'=>120),
			array('sTitle'=>Yii::t('lang','IP地址开始'),'data'=>'sDhcpIPStart'),
			array('sTitle'=>Yii::t('lang','IP地址结束'),'data'=>'sDhcpIPEnd'),
			array('sTitle'=>Yii::t('lang','租约'),'data'=>'iDhcpLease','sClass'=>'iDhcpLease','width'=>60),
			array('sTitle'=>Yii::t('lang','租约计划'),'data'=>'sDhcpLeasePlan','sClass'=>'sDhcpLeasePlan'),
			array('sTitle'=>Yii::t('lang','启动'),'data'=>'iDhcpServerOn','sClass'=>'iDhcpServerOn'),
			array('data'=>null,'bVisible' => false,'sClass'=>'btn_edit','sType'=>1),
			array('data'=>null,'bVisible' => false,'sClass'=>'btn_del'),
		);
		echo CJSON::encode($aData);
		Yii::app()->end();
	}
	public function actionIndexListDataDhcp4(){

		$param['hModel'] = new Tbdhcpfour();
		$param['returnData'] = 2;
		$dataList = DBHelper::getDataList($param);

		$NetPortModel = new TbNetPort();
		$sLan = $NetPortModel->sLanList();
		foreach($dataList['data'] as $key=>$item){
			$sDhcpName = explode(',',$item['sDhcpName']);
			$sDhcpName = array_flip($sDhcpName);
			$sDhcpNameLan = array_intersect_key( $sLan , $sDhcpName);
			$dataList['data'][$key]['sPortNameLan'] = implode(',',$sDhcpNameLan);
		}
		echo CJSON::encode($dataList);
		Yii::app()->end();

	}

	public function  actionHandUnlockIPV4(){
		$aPost = $this->getParam();
		$hModel=new Tbdhcpfour();
		$param['hModel'] = new Tbdhcpfour();
		$param['lockField'] = 'iDhcpServerOn';
		$param['sCommand'] = "CMD_DHCP";
		DBHelper::HandUnlock($param);

	}

	//DHCP服务器
	public function actionDhcp4Save()
	{
		if(Yii::app()->request->isPostRequest){
			$hModel = new Tbdhcpfour();
			$aPost =(array)$this->getParam();
			if(!isset($aPost['iDhcpServerOn'])||empty($aPost['iDhcpServerOn'])){
				$aPost['iDhcpServerOn'] = '0';
			}else{
				$aPost['iDhcpServerOn'] = '1';
			}
			if(!empty($aPost['sDhcpName'])){
				$c = new CDbCriteria();
				$condition = "";
				if(!empty($aPost['id'])){
					$condition = " AND id !=".$aPost['id'];
				}
				$c->condition = " sDhcpName = '".$aPost['sDhcpName']."'".$condition;
				$count= $hModel->count($c);
				if($count>0){
					$this->showMessage(false,Yii::t('lang', '不能添加相同网口的DHCP服务器'));
				}
				;
			}
			//如果无限制的时候，把sDhcpLeasePlan设置为空
			if($aPost['iDhcpLease']==1){
				$aPost['sDhcpLeasePlan'] ="";
			}else{
				if(empty($aPost['sDhcpLeasePlan'])){
					$this->showMessage(false,Yii::t('lang', '租约选择‘有限制’,租约计划不能选择无'));
				}
			}
			$c = new CDbCriteria();
			if(!empty($aPost)){
				if(!empty($aPost['id'])){
					$c->condition = "id != ".$aPost['id'];
				}
				$aData = $hModel ->findAll($c);
				$mask =$this->mask2cidr($aPost['sDhcpServerMask']);
				$sip1 = $aPost['sDhcpServerIP']."/".$mask;
				foreach($aData as $key =>$val){
					$mask2 =$this->mask2cidr($val->sDhcpServerMask);
					$sip2 = $val->sDhcpServerIP."/".$mask;
					$res = $this->isNetSome($sip1,$sip2);
					if($res){
						$aJson['success'] = false;
						$aJson['msg'] = $sip1.Yii::t('lang', '和').$sip2.Yii::t('lang', '已重复');
						echo CJSON::encode($aJson);
						Yii::app()->end();
					}
				}
			}
			$param['extData'] = $aPost;
			$param['hModel'] = new Tbdhcpfour();
			$param['sLogDesc'] = '编辑DHCP IPV4成功';
			$param['sCommand'] = "CMD_DHCP|add";
			DBHelper::saveData($param);

		}else{
			$aPost=(array)$this->getParam();
			$dModel =new Tbdhcpfour();
			//单次时间计划
			$hModel=new TbTimePlanSingle();
			$data['planList']=$hModel->findAll();
			//网络端口
			$hPort=new TbNetPort();
			$data['netPort']=$hPort->findAll(array(
				'condition' => '`iStatus`=1 and `sIPV4Address`<>""'
			));
			$arr = json_decode(CJSON::encode($data['netPort']),TRUE);
			/*if(Yii::app()->request->isPostRequest){
				foreach($arr as $v){
					if($aPost['pn']===$v['sPortName']){
						$v['sIPV4Address']=explode(',',$v['sIPV4Address']);
						echo json_encode($v['sIPV4Address']);die;
					}
				}
			}else{
				$sValue=$dModel->find("id=:id",array(":id"=>$aPost['id']));
				foreach($arr as $v){
					if($sValue->sDhcpName===$v['sPortName']){
						$sValue->sDhcpServerIPs=explode(',',$v['sIPV4Address']);

					}
				}
			}*/
			$sValue=$dModel->find("id=:id",array(":id"=>$aPost['id']));
			foreach($arr as $v){
				if($sValue->sDhcpName===$v['sPortName']){
					$sValue->sDhcpServerIPs=explode(',',$v['sIPV4Address']);

				}
			}

			$data['setting']=$sValue;
			$this->render('dhcp_ipv4_save',$data);
		}


	}
	public function actionDelDataDhcpipv4()
	{
		$hPost = $this->getParam();
		$aJson = array();
		$hModel = new Tbdhcpfour();
		$criteria = new CDbCriteria;
		$criteria->addInCondition('id', explode(",", $hPost->sId));
		$rs = $hModel::model()->deleteAll($criteria);
		if ($rs) {
			$aJson ['success'] = true;
			$aJson ['msg'] = Yii::t('lang', '操作成功');
			/***
			 * 操作日志
			 */
			$sDesc = '删除用户成功';
			$pData = new stdClass();
			$pData->sDesc = $sDesc;
			$this->saveOperationLog($pData);
			$sCmd = "CMD_DHCP|del";
			DBHelper::saveCommand($sCmd);
		} else {
			$aJson['debug_erro'] = $hModel->errors;
			$aJson ['success'] = false;
			$aJson ['msg'] = Yii::t('lang', '操作失败');
		}
		echo CJSON::encode($aJson);
		Yii::app()->end();
	}

	public function actionDhcpIPV4Backup(){
        $aPost=(array)$this->getParam();
        $config=new TbConfig();
        if(Yii::app()->request->isPostRequest){
            $append=$config->find("sName='DHCPException'");
            $appendData=CJSON::decode($append->attributes['sValue']);
            $appendData=array("sDhcpExceptIPStart"=>$appendData['sDhcpExceptIPStart'],
                "sDhcpExceptIPEnd"=>$appendData['sDhcpExceptIPEnd']);
            $aPost=array_merge($aPost,$appendData);
            $aPost['sIPV'] ='ipv4';
            if(empty($aPost['iDhcpServerOn']))$aPost['iDhcpServerOn']=0;
            $config->sName="DHCPServer";
            $config->sValue=CJSON::encode($aPost);
            $config->sMark='DHCP服务器';
            $config->sCommand="CMD_DHCP";
            DBHelper::saveConfig($config,'设置成功',1,true,'保存DHCP服务器配置',$isLog=true);
        }
    }
	//DHCP排除范围
	public function actionDhcpIPV4Exclude()
	{
		$aPost=(array)$this->getParam();
		$config=new TbConfig();
		if(Yii::app()->request->isPostRequest){
			$append=$config->find("sName='DHCPServer'");
			$appendData=CJSON::decode($append->attributes['sValue']);
			$aPost=array_merge($appendData,$aPost);
			$aPost['sIPV'] ='ipv4';
			$config->sName="DHCPException";
			$config->sValue=CJSON::encode($aPost);
			$config->sMark="DHCP排除范围";
			$config->sCommand="CMD_DHCP";
			DBHelper::saveConfig($config,'设置成功',1,true,'保存DHCP排除范围配置',$isLog=true);
		}else{
			$info=$config->find("sName='DHCPException'");
			$data['setting']=CJSON::decode($info['sValue']);
			$this->render('dhcp_ipv4_exclude',$data);
		}
	}
	public function actionDhcpIPV6Backup()
    {
        $aPost = (array)$this->getParam();
        $config = new TbConfig();
        if (Yii::app()->request->isPostRequest) {
            $append = $config->find("sName='DHCPExceptionIPV6'");
            $appendData = CJSON::decode($append->attributes['sValue']);
            $appendData = array("sDhcpExceptIPStart" => $appendData['sDhcpExceptIPStart'],
                "sDhcpExceptIPEnd" => $appendData['sDhcpExceptIPEnd']);
            $aPost = array_merge($aPost, $appendData);
            $aPost['sIPV'] = 'ipv6';
            if (empty($aPost['iDhcpServerOn'])) $aPost['iDhcpServerOn'] = 0;
            $config->sName = "DHCPServerIPV6";
            $config->sValue = CJSON::encode($aPost);
            $config->sMark = 'DHCP服务器';
            $config->sCommand = "CMD_DHCP";
            DBHelper::saveConfig($config,'设置成功',1,true,'保存DHCP服务器配置',$isLog=true);

        }
    }
	//DHCP服务器
	public function actionDhcpIPV6()
	{
		$aPost=(array)$this->getParam();
		$config=new TbConfig();
        //单次时间计划
        $hModel=new TbTimePlanSingle();
        $data['planList']=$hModel->findAll();
        //网络端口
        $hPort=new TbNetPort();
        $data['netPort']=$hPort->findAll(array(
            'condition' => '`iStatus`=1 and `sIPV6Address`<>""'
        ));
        if(Yii::app()->request->isPostRequest){

            $arr = json_decode(CJSON::encode($data['netPort']),TRUE);
            foreach($arr as $v){
                if($aPost['pn']===$v['sPortName']){
                    $v['sIPV6Address']=explode(',',$v['sIPV6Address']);
                    echo json_encode($v['sIPV6Address']);die;
                }
            }
        }else{
            $info=$config->find("sName='DHCPServerIPV6'");
        }
        $data['setting']=CJSON::decode($info['sValue']);
        $this->render('dhcp_ipv6',$data);
	}

    public function actionIPV6Info(){
        $aPost=(array)$this->getParam();
        if(Yii::app()->request->isPostRequest){
            if($aPost['ip']!=''){
                $ip=explode("/",$aPost['ip']);
                $data["sDhcpServerMask"]=intval($ip[1]);
                echo json_encode($data);die;
            }
        }
    }
	//DHCP排除范围
	public function actionDhcpIPV6Exclude()
	{
		$aPost=(array)$this->getParam();
		$config=new TbConfig();
		if(Yii::app()->request->isPostRequest){
			$append=$config->find("sName='DHCPServerIPV6'");
			$appendData=CJSON::decode($append->attributes['sValue']);
			$aPost=array_merge($appendData,$aPost);
			$aPost['sIPV'] ='ipv6';
			$config->sName="DHCPExceptionIPV6";
			$config->sValue=CJSON::encode($aPost);
			$config->sMark='DHCP排除范围';
			$config->sCommand="CMD_DHCP";
			DBHelper::saveConfig($config,'设置成功',1,true,'保存DHCP排除范围配置',$isLog=true);
		}else{
			$info=$config->find("sName='DHCPExceptionIPV6'");
			$data['setting']=CJSON::decode($info['sValue']);
			$this->render('dhcp_ipv6_exclude',$data);
		}
	}


	//DNS配置
	public function actionDNSSetting()
	{
		$this->render('dns_setting');
	}
	public function actionDNSSettingIPV4()
	{
		$aPost=(array)$this->getParam();
		$config=new TbConfig();
		if(Yii::app()->request->isPostRequest){
			if(empty($aPost['iTurnOnDNS']))$aPost['iTurnOnDNS']='0';
			//old data
			if(isset($aPost['iTurnOnDNS'])&& $aPost['iTurnOnDNS'] ==1&&empty($aPost['sDNSServerOne'])&& empty($aPost['sDNSServerTwo'])){
				$aJson['success'] = false;
				$aJson['msg']=Yii::t('lang','DNS服务器1和DNS服务器2不能都为空');
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
			if(!empty($aPost['sDNSServerOne'])&&!empty($aPost['sDNSServerOne'])){
				if($aPost['sDNSServerOne'] ==$aPost['sDNSServerTwo']){
					$aJson['success'] = false;
					$aJson['msg']=Yii::t('lang','DNS服务器1和DNS服务器2不能一样');
					echo CJSON::encode($aJson);
					Yii::app()->end();
				}
			}
			$info=$config->find("sName='DNSSettingIPV4'");
			$config->sName="DNSSettingIPV4";
			$config->sValue=CJSON::encode($aPost);
			$config->sMark='DNSIPV4配置';
			$config->sCommand="CMD_DNS|iptables|".$info['sValue'];
			DBHelper::saveConfig($config,'设置成功',1,true,'保存DNSIPV4配置配置',$isLog=true);
		}else{
			$info=$config->find("sName='DNSSettingIPV4'");
			$data['setting']=CJSON::decode($info['sValue']);
			$this->render('dns_setting_ipv4',$data);
		}
	}

	public function actionDNSSettingIPV6()
	{
		$aPost=(array)$this->getParam();
		$config=new TbConfig();
		if(Yii::app()->request->isPostRequest){
			if(empty($aPost['iTurnOnDNS']))$aPost['iTurnOnDNS']='0';
			if(isset($aPost['iTurnOnDNS'])&& $aPost['iTurnOnDNS'] ==1){
				if(empty($aPost['sDNSServerOne'])&& empty($aPost['sDNSServerTwo'])){
					$aJson['success'] = false;
					$aJson['msg']=Yii::t('lang','DNS服务器1和DNS服务器2不能都为空');
					echo CJSON::encode($aJson);
					Yii::app()->end();
				}
			}
			if(!empty($aPost['sDNSServerOne'])&&!empty($aPost['sDNSServerOne'])){
				if($aPost['sDNSServerOne'] ==$aPost['sDNSServerTwo']){
					$aJson['success'] = false;
					$aJson['msg']=Yii::t('lang','DNS服务器1和DNS服务器2不能一样');
					echo CJSON::encode($aJson);
					Yii::app()->end();
				}
			}

			if(!empty($aPost['sDNSServerOne'])){
				$rs = $this->CheckIPV6($aPost['sDNSServerOne'],1);
				if(!$rs){
					$aJson['success'] = false;
					$aJson['msg']=Yii::t('lang','DNS服务器1不是正确的IPV6地址格式');
					echo CJSON::encode($aJson);
					Yii::app()->end();
				}
			}
			if(!empty($aPost['sDNSServerTwo'])){
				$rs = $this->CheckIPV6($aPost['sDNSServerTwo'],1);
				if(!$rs){
					$aJson['success'] = false;
					$aJson['msg']=Yii::t('lang','DNS服务器2不是正确的IPV6地址格式');
					echo CJSON::encode($aJson);
					Yii::app()->end();
				}
			}
			$info=$config->find("sName='DNSSettingIPV6'");
			$config->sName="DNSSettingIPV6";
			$config->sValue=CJSON::encode($aPost);
			$config->sMark='DNSIPV6配置';
			$config->sCommand="CMD_DNS|ip6tables|".$info['sValue'];
			DBHelper::saveConfig($config,'设置成功',1,true,'保存DNSIPV6配置',$isLog=true);
		}else{
			$info=$config->find("sName='DNSSettingIPV6'");
			$data['setting']=CJSON::decode($info['sValue']);
			$this->render('dns_setting_ipv6',$data);
		}
	}
	//RIP高级选项
	public function actionRipAdvancedOption()
	{
		$aPost=(array)$this->getParam();

		/*if(!isset($aPost['iRipDirectRouter'])){
			$aPost['iRipDirectRouter']='0';
		}else{
			if(empty($aPost['sRipDirectRouterMetric'])){
				$aJson ['success'] = false;
				$aJson ['msg'] = '直连路由不能为空！！！';
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
		}
		if(!isset($aPost['iRipStaticRouter'])){
			$aPost['iRipStaticRouter']='0';
		}else{
			if(empty($aPost['sRipStaticRouterMetric'])){
				$aJson ['success'] = false;
				$aJson ['msg'] = '静态路由不能为空！！！';
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
		}
		if(!isset($aPost['iRipCoreRouter'])){
			$aPost['iRipCoreRouter']='0';
		}else{
			if(empty($aPost['sRipCoreRouter'])){
				$aJson ['success'] = false;
				$aJson ['msg'] = '内核路由不能为空！！！';
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
		}
		if(!isset($aPost['iRipOSPF'])){
			$aPost['iRipOSPF']='0';
		}else{
			if(empty($aPost['sRipOSPFMetric'])){
				$aJson ['success'] = false;
				$aJson ['msg'] = 'OSPF不能为空！！！';
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
		}
		if(!isset($aPost['iRipBGP'])){
			$aPost['iRipBGP']='0';
		}else{
			if(empty($aPost['sRipBGPMetric'])){
				$aJson ['success'] = false;
				$aJson ['msg'] = 'BGP不能为空！！！';
				echo CJSON::encode($aJson);
				Yii::app()->end();
			}
		}*/
		$config=new TbConfig();
		if(Yii::app()->request->isPostRequest){
			if(!isset($aPost['iTurnOnDefaultRouter']))$aPost['iTurnOnDefaultRouter']='0';
			if(!isset($aPost['iRipDirectRouter']))$aPost['iRipDirectRouter']='0';
			if(!isset($aPost['iRipStaticRouter']))$aPost['iRipStaticRouter']='0';
			if(!isset($aPost['iRipCoreRouter']))$aPost['iRipCoreRouter']='0';
			if(!isset($aPost['iRipOSPF']))$aPost['iRipOSPF']='0';
			if(!isset($aPost['iRipBGP']))$aPost['iRipBGP']='0';
			if(!isset($aPost['iTimerDefault']))$aPost['iTimerDefault']='0';
			if(empty(trim($aPost['sRipDirectRouterMetric'])))$aPost['sRipDirectRouterMetric']='1';
			if(empty(trim($aPost['sRipOSPFMetric'])))$aPost['sRipOSPFMetric']='1';
			if(empty(trim($aPost['sRipStaticRouterMetric'])))$aPost['sRipStaticRouterMetric']='1';
			if(empty(trim($aPost['sRipBGPMetric'])))$aPost['sRipBGPMetric']='1';
			if(empty(trim($aPost['sRipCoreRouter'])))$aPost['sRipCoreRouter']='1';
			$config->sName="RipAdvancedOption";
			$config->sValue=CJSON::encode($aPost);
			$config->sMark='RIP高级选项';
			$config->sCommand="CMD_DYNAMICROUTING_RIP";
			DBHelper::saveConfig($config,'设置成功',1,false,'保存RIP高级选项配置',$isLog=true);
			//DBHelper::saveConfig($config,'设置成功！','保存配置',1,false);
		}else{
			$info=$config->find("sName='RipAdvancedOption'");
			$data['setting']=CJSON::decode($info['sValue']);
			$this->render('advanced_option',$data);
		}
	}
	//bgp设置
	public function actionBGPSetting()
	{
		$aPost=(array)$this->getParam();
		$config=new TbConfig();
		if(empty($aPost['iTurnOnBGP']))$aPost['iTurnOnBGP']='0';
		if(!isset($aPost['sLinkPointer']))$aPost['sLinkPointer']='0';
		if(!isset($aPost['sRIP']))$aPost['sRIP']='0';
		if(!isset($aPost['sOSPF']))$aPost['sOSPF']='0';
		if(!isset($aPost['sStatic']))$aPost['sStatic']='0';
		$config->sName="BGPSetting";
		$config->sValue=CJSON::encode($aPost);
		$config->sMark="bgp设置";
		$config->sCommand="CMD_DYNAMICROUTING_BGP";
		//DBHelper::saveConfig($config,'设置成功！','保存配置',1,false);
		DBHelper::saveConfig($config,'设置成功',1,false,'保存bgp设置配置',$isLog=true);
	}


	//查找相关网口IP
	public  function actionSelectNpip(){
		$aPost = (array)$this->getParam();
		if(Yii::app()->request->isPostRequest){
			$hModel = new TbNetPort();
			$cdb = new CDbCriteria();
			$cdb->condition ="sPortName=:sPortName";
			$cdb->params=array(':sPortName'=>$aPost['netportname']);
			$result = $hModel->findAll($cdb);
			$aItem = array();
			foreach($result as $k=>$v){
				$aItem['ipaddress']		= $v->sIPV4Address;
				$aItem['ipaddress_v6']	= $v->sIPV6Address;
			}
			echo CJSON::encode($aItem);
			Yii::app()->end();
		}
	}
}