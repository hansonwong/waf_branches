//textarea允许输入tab键
function editTab(obj){
    if (event.keyCode == 9)
    {
        if(typeof(obj.selectionStart) == "number"){
            start = obj.selectionStart;
            end = obj.selectionEnd;

            var pre = obj.value.substr(0, start);
            var post = obj.value.substr(end);
            obj.value = pre + '\t' + post;
            obj.selectionStart = start + 1;
            obj.selectionEnd = end + 1;
            event.returnValue = false;
        }
    }
}