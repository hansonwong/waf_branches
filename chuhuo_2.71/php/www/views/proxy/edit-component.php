<script>
    $(function(){
        showSslPathInit();
    });

    //初始化证书是否显示
    function showSslPathInit() {
        vueData.toggle.ssl_path1 = vueData.toggle.ssl_path2 = vueData.val.sWebSiteProtocol == 'https';
    }

    // 是否显示所属站点组模板
    function showSslPath(obj) {
        vueData.toggle.ssl_path1 = vueData.toggle.ssl_path2 = $(obj).val() == 'https';
    }

    // 移除服务器节点
    function delip(obj) {
        $(obj).parent().parent().remove();

        // 判断 ipmast 有没有数据， 如果有的话，就显示权重输入
        var ipmastArr = $('.ipmast');
        if( ipmastArr.length<1 )
        {
            $('#ipqz').show();
            $('#ipqz_text').text('').hide();
        }
    }

    /*添加IP地址及端口*/
    function addServerIpMask() {

        var ipadd = $('#ipadd').val(); // IP地址
        var ipport = $('#ipport').val(); //端口
        var ipqz = $('#ipqz').val(); // 权重

        var server_error_msg_ele = $('#server_error_msg');
        if (ipadd === '' || ipport === '' || ipqz === '') {
            // IP地址、端口、权重不能为空
            server_error_msg_ele.html("<?=Yii::$app->sysLanguage->getTranslateBySymbol('proxyIpPortWeightTips') ?>");
            return false;
        }
        server_error_msg_ele.html('');

        var ipmast = ipadd + ':' + ipport + ':' + ipqz;
        var html = `<tr class="listItem">
            <td width="10%">${ipadd}</td>
            <td width="10%">${ipport}</td>
            <td>${ipqz}</td>
            <td width="15%" align="center">
            <a href="javascript:void(0);" onclick="delip(this);" class="btn btn_del">
            <?=Yii::$app->sysLanguage->getTranslateBySymbol("delete") ?>
            </a></td>
            <input type="hidden" class="ipmast" name="WebSite[WebSiteServers][]" value="${ipmast}"/>
            </tr>`;
        $('#idtdKeyList').append(html);

        $('#ipadd').val('');
        $('#ipport').val('');
    }
</script>
<style>
    .server_table .tdbg {
        background: #f0f7fd;
        height: 20px;
        text-align: center;
        line-height: 20px;
        border-bottom: 1px solid #c4d0dc;
        font-weight: bold;
    }

    .server_table td {
        background: #fff;
        line-height: 15px;
        height: 15px;
        text-align: center;
    }

    .date_add_table td .btn {
        font-size: 14px;
    }
</style>