<?php
namespace app\logic\fetch;

class Regular{
	public function get($config, $reg){
		$html = Curl::get($config);
		$html = Curl::htmlTrim($html);

		preg_match_all($reg, $html, $matches);
		$html = $matches[1][0];
	}
}
?>