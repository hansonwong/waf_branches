//框架翻译KEY
var baseLanguage = {
//覆盖KEY值即可更改框架显示相关内容
    override: function () {
        var group = ['base', 'common'];
        for (var g in group) {
            var groupItem = this.overrideKey[group[g]];
            for (var item in groupItem) {
                this[group[g]][item] = top.translation.t(groupItem[item]);
            }
        }
    },
    overrideKey: {},

    overrideBySystem: function () {
        var group = ['base', 'common'];
        for (var g in group) {
            var groupItem = this.overrideBySystemKey[group[g]];
            for (var item in groupItem) {
                this[group[g]][item] = groupItem[item];
            }
        }
    },
    overrideBySystemKey: {},
}

baseLanguage.base = {
    china: '中文',
    english: '英文',
    /* unit.js */
    commit: '提交2',
    /* website_grid_gjd */
    websitegroup_add: '添加站点组',
    websitegroup_edit: '修改站点组',
    confirm: '请选择某一行数据？',
    watch: '查看',
    setting: '配置策略',
    setoption: '配置',
    /* sitestatus_grid.js */
    stop: '停用',
    open: '启用',
    add: '添加',
    report: '查看报告',
    checkout: '查询',
    /* rules_grid.js */
    website_edit: '编辑',
    detailRule: '规则模块',
    detailNames: '规则名称：',
    detailInfo: '一般信息：',
    detailContent: '匹配内容：',
    detailRuleId: '规则ID：',
    /* invadelogs_grid.js */
    confirmTitle: '系统友情提示',
    optionCtrol: '清空操作将对目前查询条件所列数据进行清空，清空后将不能恢复,确认?',
    confirmLog: '提示:  将根据当前条件导出日志,最多导出最新的50000条记录.',
    /* ligerDialog.js */
    titleMessage: '提示',
    yes: '是',
    no: '否',
    waittingMessage: '正在等待中,请稍候...',
    /* GridList.js */
    deletes: '删除',
    pushAdd: '增加',
    options: '操作', // grid.js
    /* grid.js */
    opAddress: '请配置表格信息请求地址',
    unlockout: '解锁',
    lockout: '锁定',
    status: '状态',
    unStop: '未启用',
    disOpen: '是否启用',
    memoryUse: '内存利用率(%)',
    cpuUse: 'cpu(%)',
    distStatus: '磁盘状态',
    portStatus: '通信口状态',
    normal: '正常',
    offline: '离线',
    errErr: '异常',
    norFlux: '当前流量(MB)',
    topLine: '上行:',
    botLine: '下行:',
    download: '下载',
    stopEnd: '停止',
    start: '启动',
    exploring: '扫描',
    addDistort: '加入防误报',
    stopRules: '停用对应规则',
    return: '返回',
    /* custom_grid.js */
    customRule: '添加自定义规则',
    /* errorlist_grid.js */
    watchRules: '查看报告',
    /* ligerGrid.js */
    highCheckout: '高级查询',
    /* ligerGrid_sel.js */
    groupColumnDisplay: '分组',
    /* ipvisit_grid.js */
    ipList: '添加IP黑白名单',

// 表格分页提示 start
    errorMessage: '发生错误',
    pageFrom: '显示从',
    pageTo: '到',
    count: '共 ',
    item: ' 条. 每页显示 : ',
// pageStatMessage: '{from}{to}{total}{pagesize}',
    pageMessage: '共 {total} 条记录, 每页显示 {pagesize} 条',
    pageTextMessage: 'Page',
    loadingMessage: '加载中...',
    findTextMessage: '查找',
    noRecordMessage: '没有符合条件的记录存在',
    isContinueByDataChanged: '数据已经改变,如果继续将丢失数据,是否继续?',
    cancelMessage: '取消1',
    saveMessage: '保存',
    applyMessage: '应用',
    draggingMessage: '行',
// 表格分页提示 end

    /* base.js */
    managerIsExist: '管理器id已经存在',
    /* logs_bdblockedlog.html */
    sysConfirm: '系统友情提示',
    clearMsg: '清空操作将对目前查询条件所列数据进行清空，清空后将不能恢复,确认?',
    ConfirmMsg: '提示:  将根据当前条件导出日志,最多导出最新的50000条记录.',
    /* outlinklogs_grid.js */
    intercept: '拦截',
    pantograph: '放行',
    hight: '高',
    droop: '低',
    /* flaw_grid.js */
    opendevice: '开启实验设备',
    resetdevice: '开启实验设备',
    initdevice: '初始化实验设备',
    closedevice: '关闭实验设备',
    oplogindevice: '新窗口打开并登录实验设备',
    backups: '备份',
    restore: '还原',
    looksin: '扫描中',
    offstocks: '已完成',
    offstops: '已停止',
    /* website_grid_fwq.js */
    websiteserver_add: '添加服务器',
    websiteserver_edit: '',
};

baseLanguage.common = {
    /* jquery.artDialog.source.js */
    message: '消息',
    okVal: '确定',
    cancelVal: '取消',
    downloadSucess: '下载成功',
    mustWrite: '* 该项必须填写！',
    commit: '提交',

    /* fun.js */
    confirmSel: '请选择数据？',
    confirmDel: '是否要删除数据？',
    alert: 'alert bug 展示，不删除数据',

    /* jquery.validationEngine.js */
    requiredMsg: '* 该项必须填写！',
    custommessage: '* 请输入正整数！',
    minmessage: '* 请按需求填写！',

    /* tab.js */
    getFullYear: '年',
    getMonth: '月',
    getDate: '日',
    getHours: '时',
    getMinutes: '分',
    getSeconds: '秒',
    addTab: '系统主页',
    tabShow: 'TAB显示',
//cancelVal: '取消4',

    /* jquery.validationEngine-zh_CN.js */
    regexalertText: '* 此处不可空白',
    regexalertTextCheckboxMultiple: '* 请选择一个项目',
    regexalertTextCheckboxe: '* 您必须钩选此栏',
    regexalertTextDateRange: '* 日期范围不可空白',
    dateRangealertText: '* 无效的 ',
    dateRangealertText2: ' 日期范围',
    dateTimeRangealertText2: '时间范围',
    minSizealertText: '* 最少 ',
    minSizealertText2: ' 个字符',
    maxSizealertText: '* 最多 ',
    maxSizealertText2: ' 个字符',
    groupRequiredalertText: '* 你必需选填其中一个栏位',
    minalertText: '* 最小值為 ',
    maxalertText: '* 最大值为 ',
    pastalertText: '* 日期必需早于 ',
    futurealertText: '* 日期必需晚于 ',
    maxCheckboxalertText: '* 最多选取 ',
    maxCheckboxalertText2: ' 个项目',
    minCheckboxalertText: '* 请选择 ',
    minCheckboxalertText2: ' 个项目',
    equalsalertText: '* 请输入与上面相同的密码',
    creditCardalertText: '* 无效的信用卡号码',
    phonealertText: '* 无效的电话号码',
    emailalertText: '* 邮件地址无效',
    integeralertText: '* 不是有效的整数',
    numberalertText: '* 无效的数字',
    datealertText: '* 无效的日期，格式必需为 YYYY-MM-DD',
    ipv4alertText: '* 无效的 IP 地址',
    onlyNumberSp: '* 只能填数字',
    onlyLetterSp: '* 只接受英文字母大小写',
    onlyLetterNumber: '* 不接受特殊字符',
    ajaxUserCallalertText: '* 此名称已被其他人使用',
    ajaxUserCallalertTextLoad: '* 正在确认名称是否有其他人使用，请稍等。',
    ajaxUserCallPhpalertTextOk: '* 此帐号名称可以使用',
    ajaxUserCallPhpalertText: '* 此名称已被其他人使用',
    ajaxUserCallPhpalertTextLoad: '* 正在确认帐号名称是否有其他人使用，请稍等。',
    ajaxNameCallalertText: '* 此名称可以使用',
    ajaxNameCallalertTextOk: '* 此名称已被其他人使用',
    ajaxNameCallalertTextLoad: '* 正在确认名称是否有其他人使用，请稍等。',
    ajaxNameCallPhpalertText: '* 此名称已被其他人使用',
    ajaxNameCallPhpalertTextLoad: '* 正在确认名称是否有其他人使用，请稍等。',
    validate2fieldsalertText: '* 请输入 HELLO',
    dateFormatalertText: '* 无效的日期格式',
    dateTimeFormatalertText: '* 无效的日期或时间格式',
    dateTimeFormatalertText2: '可接受的格式： ',
    dateTimeFormatalertText3: 'mm/dd/yyyy hh:mm:ss AM|PM 或 ',

    requiredmessage: '* 该项必须填写！',

    error_msg: 'IP地址、端口、权重不能为空',
    deletes: '删除',

    confirmDownMsg: '您确定要下载报表？',
    dialogcontent: '文件不存在',
    minmessage: '* 请输入大于0的正整数！',
    maxmessage: '* 请输入小于2147483647的正整数！',
    confirmFriend: '系统友情提示',

    resConfigTrue: '恢复默认配置后系统将重启，确认？',
    writeMin255: '* 请输入小于255的正整数！',
};

baseLanguage.overrideKey.base = {};
baseLanguage.overrideKey.common = {};

<?php
$baseLanguage['base'] = [
    'pageMessage' => 'ligerUiPageMessage',
    'website_edit' => 'update',
    'watch' => 'see',
    'setoption' => 'config',
];
$baseLanguage['common'] = [
    'message' => 'info',
    'okVal' => 'done',
    'cancelVal' => 'cancel',
    'commit' => 'submit',
];

foreach ($baseLanguage as $k => $v){
    foreach ($baseLanguage[$k] as $key => $val){
        $baseLanguage[$k][$key] = Yii::$app->sysLanguage->getTranslateBySymbol($val);
    }
}
?>
<?='baseLanguage.overrideBySystemKey = '.json_encode($baseLanguage).';'?>
baseLanguage.overrideBySystem();


