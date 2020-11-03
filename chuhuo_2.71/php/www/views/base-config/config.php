<script>
    //WAF引擎设置模式控制其他输入组件是否显示
    function showInitForWafEngine() {
        vueData.toggle.defaultAction = vueData.toggle.ports = vueData.val.wafEngine == 'On';
    }

    $(function(){
        showInitForWafEngine();
    });
</script>