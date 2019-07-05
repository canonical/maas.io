$(document).ready(function(){
    $('.p-code-copyable').each(function() {
      var self = $(this),
          copyButton = self.find('.p-code-copyable__action'),
          commandInput = self.find('.p-code-copyable__input');

      if (copyButton && commandInput) {
        copyButton.on('click', function(e) {
          e.preventDefault;
          commandInput.select();

          try {
              var successful = document.execCommand('copy');
              _gaq.push(['_trackEvent', 'Copy to clipboard', commandInput.get('value'), document.URL]);
              _this.addClass('is-copied');
              setTimeout(function(e) {
                  _this.removeClass('is-copied');
              }, 300);
          } catch(err) {
              console.log('Unable to copy');
          }
        });
      }

      if (commandInput) {
          commandInput.on('click', function(e) {
              this.select();
          });
      }
    });
});
