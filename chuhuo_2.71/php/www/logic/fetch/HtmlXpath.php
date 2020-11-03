<?php
namespace app\logic\fetch;

class HtmlXpath{
	public static function getXpathObj($config){
		$html = Curl::get($config);
		$doc = new \DOMDocument();
		$doc->strictErrorChecking = false;
		$doc->loadHtml($html);
		return $xpath = new \DOMXpath($doc);
	}

	public static function getElementsCount($xpath, $path){
		$elements = $xpath->query($path);
		$i = 0;
		if (!is_null($elements)) {
			foreach ($elements as $element) {
				++$i;
			}
		}
		return $i;
	}

	public static function getElement($xpath, $path){
		$elements = $xpath->query($path);
		foreach ($elements as $element) {
			return $element;
		}
	}

	public static function getElementUrl($xpath, $pa){
		$element = self::getElement($xpath, $pa);
		$elementAttr = $element->attributes;
		foreach ($elementAttr as $attr){
			if('href' == $attr->name){
				return ['title' => $element->nodeValue, 'url' => $attr->value];
			} else continue;
		}
		return false;
	}

	public static function getElementAttrs($xpath, $pa){
		$element = self::getElement($xpath, $pa);
		$elementAttr = $element->attributes;
		$data = [];
		foreach ($elementAttr as $attr){
			$data[$attr->name] = $attr->value;
		}
		return $data;
	}
}
?>