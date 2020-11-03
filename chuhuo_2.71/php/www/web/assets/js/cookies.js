//还原cookie值
function get_escape_str(str){
	return decodeURIComponent(str);
}

//设置cookie值
function set_cookie(name, value, expires, path, domain, secure) {
	// set time, it's in milliseconds
	var today = new Date();
	today.setTime(today.getTime());

    if (expires) {
		expires = expires * 1000 * 60 * 60 * 24;//设置天数
        // expires = 1000 * expires;//设置秒数
	}
	var expires_date = new Date(today.getTime() + (expires));
	document.cookie = name + "=" + encodeURIComponent(value) + ((expires) ? ";expires=" + expires_date.toGMTString() : "") + ((path) ? ";path=" + path: "") + ((domain) ? ";domain=" + domain: "") + ((secure) ? ";secure": "");
}

//获取cookie值
function get_cookie(name) {
	var start = document.cookie.indexOf(name + "=");
	var len = start + name.length + 1;
	if ((!start) && (name != document.cookie.substring(0, name.length))) {
	return null;
}
	if (start == -1) return null;
	var end = document.cookie.indexOf(";", len);
	if (end == -1) end = document.cookie.length;
	return (document.cookie.substring(len, end));
}

//删除cookie
function remove_cookie(name){
	set_cookie(name, 1, -1);
}

//删除所有cookie
function clear_cookie(){
	var keys=document.cookie.match(/[^ =;]+(?=\=)/g);
	if (keys) {
		for (var i = keys.length; i--;){
			document.cookie=keys[i]+'=0;expires=' + new Date( 0).toUTCString();
		}
	}
}
