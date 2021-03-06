<?php

namespace app\logic\waf\helpers;

class WafRegexp {
    /**
     * 验证真实姓名
     */
    public static $realname = '/^[A-Za-z0-9\\u4e00-\\u9fa5]+$/';
    /**
     * 浮点数
     */
    public static $decmal = "/^([+-]?)\\d*\\.\\d+$/";
    /**
     * 正浮点数
     */
    public static $decmal1 = "/^[1-9]\\d*.\\d*|0.\\d*[1-9]\\d*$/";
    /**
     * 负浮点数
     */
    public static $decmal2 = "/^-([1-9]\\d*.\\d*|0.\\d*[1-9]\\d*)$/";
    /**
     * 浮点数
     */
    public static $decmal3 = "/^-?([1-9]\\d*.\\d*|0.\\d*[1-9]\\d*|0?.0+|0)$/";
    /**
     * 非负浮点数（正浮点数 + 0）
     */
    public static $decmal4 = "/^[1-9]\\d*.\\d*|0.\\d*[1-9]\\d*|0?.0+|0$";
    /**
     * 非正浮点数（负浮点数 + 0）
     */
    public static $decmal5 = "/^(-([1-9]\\d*.\\d*|0.\\d*[1-9]\\d*))|0?.0+|0$/";
    /**
     * 整数
     */
    public static $intege = "/^-?[1-9]\\d*$/";
    /**
     * 正整数
     */
    public static $intege1 = "/^[1-9]\\d*$/";
    /*
     * 负整数
     */
    public static $intege2 = "/^-[1-9]\\d*$/";
    /**
     * 数字
     */
    public static $num = "/^([+-]?)\\d*\\.?\\d+$/";
    /**
     * 正数（正整数 + 0）
     */
    public static $num1 = "/^[1-9]\\d*|0$/";
    /**
     * 负数（负整数 + 0）
     */
    public static $num2 = "/^-[1-9]\\d*|0$/";
    /**
     * 仅ACSII字符
     */
    public static $ascii = "/^[\\x00-\\xFF]+$/";
    /**
     * 仅中文
     */
    public static $chinese = "/^[\\u4e00-\\u9fa5]+$/";
    /**
     * 颜色
     */
    public static $color = "/^[a-fA-F0-9]{6}$/";
    /**
     * 日期
     */
    public static $date = "/^\\d{4}(\\-|\\/|\.)\\d{1,2}\\1\\d{1,2}$/";
    /**
     * 邮件
     */
    public static $email = "/^\\w+((-\\w+)|(\\.\\w+))*\\@[A-Za-z0-9]+((\\.|-)[A-Za-z0-9]+)*\\.[A-Za-z0-9]+$/";
    /**
     * 身份证
     */
    public static $idcard = "/^[1-9]([0-9]{14}|[0-9]{17})$/";
    /**
     * ip地址
     */
     public static $ip4 = "/^(25[0-5]|2[0-4]\\d|[0-1]\\d{2}|[1-9]?\\d)\\.(25[0-5]|2[0-4]\\d|[0-1]\\d{2}|[1-9]?\\d)\\.(25[0-5]|2[0-4]\\d|[0-1]\\d{2}|[1-9]?\\d)\\.(25[0-5]|2[0-4]\\d|[0-1]\\d{2}|[1-9]?\\d)$/";
     public static $ip4Range = "/^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|0?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|0?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|0?[0-9]?[0-9])\\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|0?[0-9]?[0-9])(?:\\/(3[0-2]|[12]?\\d))?$/";
    /*
     * 匹配X.X.X.X/24或者X.X.X.X
     */
     public  static $ip4andrag = "/^((0|1[0-9]{0,2}|2[0-9]{0,1}|2[0-4][0-9]|25[0-5]|[3-9][0-9]{0,1})\.){3}(0|1[0-9]{0,2}|2[0-9]{0,1}|2[0-4][0-9]|25[0-5]|[3-9][0-9]{0,1})(?(\/)\/([0-9]|[1-2][0-9]|3[0-2])|)$/";
   ///([a-fA-F0-9]{2}[:|\-]?){6}/
     public static $mac = "/^([0-9a-fA-F][0-9a-fA-F][:-]){5}([0-9a-fA-F][0-9a-fA-F])$/";

    /**
     * （1-65535）
     * 端口号正则
     * @var string
     */
     public static $port = " /^([0-9]|[1-9]\\d|[1-9]\\d{2}|[1-9]\\d{3}|[1-5]\\d{4}|6[0-4]\\d{3}|65[0-4]\\d{2}|655[0-2]\\d|6553[0-5])$/";

    //ipv6地址的正则
    public static $ip6 = "/^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$/";

        /**
     * 字母
     */
    public static $letter = "/^[A-Za-z]+$/";
    /**
     * 小写字母
     */
    public static $letter_l = "/^[a-z]+$/";
    /**
     * 大写字母
     */
    public static $letter_u = "/^[A-Z]+$/";
    /**
     * 手机
     */
    public static $mobile = '/^[1][3,4,5,7,8][0-9]{9}$/';
    //public static $mobile = '/(13|15)[0-9]{9}$/';
    /**
     * 电话号
     */
    public static $tel = "/(^(86)\-(0\d{2,3})\-(\d{7,8})\-(\d{1,4})$)|(^0(\d{2,3})\-(\d{7,8})$)|(^0(\d{2,3})\-(\d{7,8})\-(\d{1,4})$)|(^(86)\-(\d{3,4})\-(\d{7,8})$)/";
    /**
     * 非空
     */
    public static $notempty = "/^\\S+$/";
    /**
     * 密码
     */
    public static $password = "/^[A-Za-z0-9_-]+$/";
    /**
     * 图片
     */
    public static $picture = "(.*)\\.(jpg|bmp|gif|ico|pcx|jpeg|tif|png|raw|tga)$/";
    /*
     * QQ号码
     */
    public static $qq = "/^[1-9]*[1-9][0-9]*$/";
    /**
     * 压缩文件
     */
    public static $rar = "(.*)\\.(rar|zip|7zip|tgz)$/";
    /**
     * url
     */
    public static $url = "^http[s]? = \\/\\/([\\w-]+\\.)+[\\w-]+([\\w-./?%&=]*)?$/";
    /**
     * 用户名
     */
    public static $username = "/^[A-Za-z0-9_\\-\\u4e00-\\u9fa5]+$/";
    /**
     * 邮编
     */
    public static $zipcode      = "/^\\d{6}$/";

    public static  $urlall      ="^(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)?((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.[a-zA-Z]{2,4})(\:[0-9]+)?(/[^/][a-zA-Z0-9\.\,\?\'\\/\+&amp;%\$#\=~_\-@]*)*$";

    //ip地址/掩码  第一位与第四位不允许是 0或者255  掩码不允许大于31  格式为172.16.3.254/24
    public static $ip_v4_mask   = "/^([1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\.([1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\/(\d{1}|[0-2]{1}\d{1}|3[0-1])$/";

    //对应前端验证  zh_CN 的 ip_preg  a.b.c.d      0<a<255  0<=b<255  0<=c<255    0<d<255
    public static $ip_v4        = "/^([1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\.([1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])$/";

    //对应前端验证  zh_CN 的 $ipv4
    public static $ipv4         = "/^((([01]?[0-9]{1,2})|(2[0-4][0-9])|(25[0-5]))[.]){3}(([0-1]?[0-9]{1,2})|(2[0-4][0-9])|(25[0-5]))$/";

    //对应前端验证  zh_CN 的 $all_mask 验证是否符合255.255.255.0或者是1-31的数值
    public static $all_mask     = "/^(((\d{1,2}|1\d\d|2[0-4]\d|25[0-5])(\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])){3})|([0-9]|[1-2]\d{1}|3[0-2]))$/";

    //ospf IP/掩码
    public static $ospf_preg    = "/^(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\/(([1-9]|[1-2]\d{1}|3[0-2]))$/";

    //验证 IP/掩码  掩码支持  /24 /255.255.255.0两种形式
    public static $ip_block_preg= "/^([1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-4])\/(([0-9]|[1-2]\d{1}|3[0-2])|((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])))$/";

    /**
     * mac 地址 XX:XX:XX:XX:XX:XX
     * @var string
     */
    public static $mac_preg = "/^([0-9a-fA-F][0-9a-fA-F][:]){5}([0-9a-fA-F][0-9a-fA-F])$/";

        // 掩码
    public static $CIDR = [
                                0=>'0.0.0.0',
                                1=>'128.0.0.0',
                                2=>'192.0.0.0',
                                3=>'224.0.0.0',
                                4=>'240.0.0.0',
                                5=>'248.0.0.0',
                                6=>'252.0.0.0',
                                7=>'254.0.0.0',
                                8=>'255.0.0.0',
                                9=>'255.128.0.0',
                                10=>'255.192.0.0',
                                11=>'255.224.0.0',
                                12=>'255.240.0.0',
                                13=>'255.248.0.0',
                                14=>'255.252.0.0',
                                15=>'255.254.0.0',
                                16=>'255.255.0.0',
                                17=>'255.255.128.0',
                                18=>'255.255.192.0',
                                19=>'255.255.224.0',
                                20=>'255.255.240.0',
                                21=>'255.255.248.0',
                                22=>'255.255.252.0',
                                23=>'255.255.254.0',
                                24=>'255.255.255.0',
                                25=>'255.255.255.128',
                                26=>'255.255.255.192',
                                27=>'255.255.255.224',
                                28=>'255.255.255.240',
                                29=>'255.255.255.248',
                                30=>'255.255.255.252',
                                31=>'255.255.255.254',
                                32=>'255.255.255.255'
                        ];
    // 掩码 转10进制
    public static $CIDRDEC = [
                            0=>'0',
                            8=>'4228250625',
                            9=>'4236573825',
                            10=>'4240735425',
                            11=>'4242816225',
                            12=>'4243856625',
                            13=>'4244376825',
                            14=>'4244636925',
                            15=>'4244766975',
                            16=>'4244832000',
                            17=>'4244864640',
                            18=>'4244880960',
                            19=>'4244889120',
                            20=>'4244893200',
                            21=>'4244895240',
                            22=>'4244896260',
                            23=>'4244896770',
                            24=>'4244897025',
                            25=>'4244897153',
                            26=>'4244897217',
                            27=>'4244897249',
                            28=>'4244897265',
                            29=>'4244897273',
                            30=>'4244897277',
                            31=>'4244897279',
                            32=>'4244897280'
                            ];
}