/*
 * jQuery placeholder, fix for IE6,7,8,9
 * @author JENA
 * @since 20131115.1504
 * @website ishere.cn
 */
var JPlaceHolder = {
    //ºÏ≤‚
    _check : function(){
        return 'placeholder' in document.createElement('input');
    },
    //≥ı ºªØ
    init : function(){
        if(!this._check()){
            this.fix();
        }
    },
    //–ﬁ∏¥
    fix : function(){
        jQuery(':input[placeholder]').each(function(index, element) {
            var self = $(this), txt = self.attr('placeholder');
            self.wrap($('<div></div>').css({position:'relative', zoom:'1', border:'none', background:'none', padding:'none', margin:'none'}));
            var pos = self.position(), h = self.outerHeight(true), paddingleft = self.css('padding-left');
            var holder = $('<font></font>').text(txt).css({position:'absolute', left:pos.left, top:pos.top, height:h, lineHeight:'38px', paddingLeft:paddingleft, color:'#aaa', fontSize:'16px'}).appendTo(self.parent());
            self.focusin(function(e) {
                holder.hide();
            }).focusout(function(e) {
                if(!self.val()){
                    holder.show();
                }
            });
            holder.click(function(e) {
                holder.hide();
                self.focus();
            });
        });
    }
};
//÷¥––
jQuery(function(){
    JPlaceHolder.init();    
});
