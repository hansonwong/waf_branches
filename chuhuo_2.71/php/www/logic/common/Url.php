<?php

namespace app\logic\common;


class Url
{
    public static function getQueryParams($url){
        $url = parse_url($url);
        $query = [];
        parse_str($url['query'], $query);
        return $query;
    }
}