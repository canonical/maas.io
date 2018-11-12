var origin = window.location.href;
var site = 'maas.io';

addGAEvents('#navigation a', 'nav-0');
addGAEvents('.p-footer a', 'nav-footer-0');
addGAEvents('#main-content', 'content');

function addGAEvents(target, category){
  var t = document.querySelectorAll(target);
  if (t.length >= 1) {
    if (category.startsWith('nav-')){
      t.forEach(function(e) {
        e.addEventListener('click', function(){
          sendEvent(category, origin, e.href, e.text);
        });
      });
    } else {
      // Get form submit events
      t[0].querySelectorAll('form').forEach(function(e) {
        var button = e.querySelector('.p-button--positive');
        if (button) {
          button.addEventListener('click', function(){
            sendEvent('content-cta-0', origin, e.returnURL.value, button.innerText);
          });
        }
      });
      // Get link click events
      t[0].querySelectorAll('a').forEach(function(e) {
        if (e.className.includes('p-button--positive')) {
          category = 'content-cta-0';
        } else if (e.className.includes('p-button')) {
          category = 'content-cta-1';
        } else {
          category = 'content-link';
        }
        e.addEventListener('click', function(){
          sendEvent(category, origin, e.href, e.text);
        });
      });
    }
  }
}

function sendEvent(category, origin, destination, label){
    if (dataLayer){
      dataLayer.push({
          'event' : 'GAEvent',
          'eventCategory' : `${site}-${category}`,
          'eventAction' : `from:${origin} to:${destination}`,
          'eventLabel' : label,
          'eventValue' : undefined
      });
    }
  }
