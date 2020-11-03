<?php
namespace app\logic\fetch;

class Curl{
	public static function setConfig(&$config){
		if(!isset($config['header_response_out'])) $config['header_response_out'] = false;
		if(!isset($config['user_agent'])) $config['user_agent'] = false;
		if(!isset($config['referer'])) $config['referer'] = false;
		if(!isset($config['header_out'])) $config['header_out'] = false;
		if(!isset($config['header_send'])) $config['header_send'] = false;
		if(!isset($config['post'])) $config['post'] = false;
		if(!isset($config['cookie_file'])) $config['cookie_file'] = false;
		if(!isset($config['cookie'])) $config['cookie'] = false;
		if(!isset($config['header_request_get'])) $config['header_request_get'] = false;
		if(!isset($config['http_code'])) $config['http_code'] = false;
	}

	public static function get($config)
	{
		if($config['get']) return file_get_contents($config['url']);
		$ssl = (substr($config['url'], 0, 8) == "https://") ? TRUE : FALSE;
		$ssl = false;

		self::setConfig($config);
		$ch = curl_init();
		//获取响应头，响应头包含在输出中
		if($config['header_response_out']){
			curl_setopt($ch, CURLOPT_HEADER, 1);
			curl_setopt($ch, CURLOPT_NOBODY, true);
		}

		if($config['user_agent']) curl_setopt($ch, CURLOPT_USERAGENT, $config['user_agent']);

		//发送请求头
		if($config['header_send']) curl_setopt($ch, CURLOPT_HTTPHEADER, $config['header_send']);
		//获取请求头:true/false,true为获取
		curl_setopt($ch, CURLINFO_HEADER_OUT, $config['header_out']);

		if($config['post']){
			curl_setopt($ch, CURLOPT_POST, 1);//post提交方式
			curl_setopt($ch, CURLOPT_POSTFIELDS, $config['post']);
		}

		curl_setopt($ch, CURLOPT_URL, $config['url']);

		if ($config['referer']) curl_setopt($ch, CURLOPT_REFERER, $config['referer']);//构造来路
		if ($ssl) {
			curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
			curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
			curl_setopt($ch, CURLOPT_CAINFO, $_SERVER['DOCUMENT_ROOT'] . '/cacert.pem');
			//$cookie_jar = 'E:\wamp\virtualhosts\nh.com\shanbay.cookie';//存放COOKIE的文件
			if ($config['cookie_file']) {
				$data = array(
					'username' => 'ssss',
					'password' => 'ssss',
					'token' => 'ssss',
				);
				curl_setopt($ch, CURLOPT_POSTFIELDS, $data);

				curl_setopt($ch, CURLOPT_COOKIEFILE, $config['cookie_file']);//发送cookie文件
				curl_setopt($ch, CURLOPT_COOKIEJAR, $config['cookie_file']);  //保存cookie信息
			}
		} else {
			if ($config['cookie']) curl_setopt($ch, CURLOPT_COOKIE, $config['cookie']);
			if($config['cookie_file']){
				curl_setopt($ch, CURLOPT_COOKIEFILE, $config['cookie_file']);//发送cookie文件
				curl_setopt($ch, CURLOPT_COOKIEJAR, $config['cookie_file']);  //保存cookie信息
			}
			curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
			curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
		}
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

		$out = curl_exec($ch);
		if ($out === false) {
			//var_dump(curl_error($ch));  //查看报错信息
			curl_close($ch);
			return false;
		}
		//获取请求头
		if($config['header_request_get']){
			$curlinfo = curl_getinfo($ch);
			$headerinfo = $curlinfo['request_header'];
			curl_close($ch);
			return $headerinfo;
		}

		//获取响应头
		if($config['header_response_out']){
			$headerSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
			curl_close($ch);
			return substr($out, 0, $headerSize);
		}

		//获取状态码
		if($config['http_code']){
			curl_exec($ch);
			return curl_getinfo($ch,CURLINFO_HTTP_CODE);
		}

		curl_close($ch);
		return $out;
	}

	public static function htmlTrim($html)
	{
		$html = str_replace("\r\n", '', $html);
		$html = str_replace("\n", '', $html);
		return $html;
	}

	public static function get_rand_ip()
	{
		$ip = '';
		for ($i = 0; $i < 4; $i++) {
			$ip .= rand(50, 255) . '.';
		}
		$ip = substr($ip, 0, -1);
		return $ip;
	}
}
?>