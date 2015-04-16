$(document).ready(function(){
    if ($('.animate').inViewport()) {
        var self = $(this),
            animateType = self.attr('animation');

        console.log(animateType);
        self.addClass(animateType);
    }
});
