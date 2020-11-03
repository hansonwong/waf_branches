/**
 * 替换字符串中的字段.
 * @param {String} str 模版字符串
 * @param {Object} o json data
 * @param {RegExp} [regexp] 匹配字符串的正则表达式
 */

function substitute(str, o, regexp) {
    return str.replace(regexp || /\\?\{([^{}]+)\}/g, function (match, name) {
        return (o[name] === undefined) ? '' : o[name];
    });
}

/**
 * 获取url及url参数的方法
 * @param name
 * @returns {null}
 */
function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg);  //匹配目标参数
    if (r != null) return unescape(r[2]);
    return null; //返回参数值
}

/**
 * form表单转换为对象
 * @param id
 * @returns {{}}
 */
function formTransformForObj(id, frame) {
    frame = frame || window.document;
    var arr = $(id, frame).serializeArray();
    var obj = {};
    $(arr).each(function () {
        obj[this.name] = this.value;
    });
    return obj;
}

/**
 * 导出数据
 * @param url
 * @constructor
 */
function ExportData(url) {
    url = url + '?' + $('#search_form').serialize();
    location.href = url;
}
