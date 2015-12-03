$(document).ready(function(){

    // Find docnav and rename to docs menu
    $('.docnav').addClass('docs-menu').removeClass('docnav');

    // Set menu variable
    var self = $(this),
        menu = $('.docs-menu');

    // Wrap all inner content in a UL
    menu.wrapInner('<ul />');

    // Replace all h3s with h4s
    menu.find('h3').replaceWith(function() {
        return '<h4>' + $(this).text() + '</h4>';
    });

    // Finds h4s replaces markup and also wraps each section
    menu.find('h4').each(function() {
        $(this).addClass('header toggle-target')
            .next('ul').hide()
            .andSelf().wrapAll('<li class="section collapsed" />');
    });

    // Toggle section, opens or closes each section of links in the
    // documentation
    $('.toggle-target').on('click', function(event) {
        event.preventDefault();
        var parent = $(this).parent();

        if (parent.hasClass('collapsed')) {
            parent.find('ul').show();
            parent.addClass('expanded');
            parent.removeClass('collapsed');
        } else {
            parent.find('ul').hide();
            parent.addClass('collapsed');
            parent.removeClass('expanded');
        }
    });

    // Current path URL name
    var current = window.location.pathname;

    // Set active and selected class based on the current URL
    $('.section a[href="' + current + '"]').addClass('selected').closest('.section').addClass('active');

    // Make the section active onload if it has the class of active
    $('.section').each(function() {
        var self = $(this);

        if (self.hasClass('active')) {
            self.find('ul').show();
            self.addClass('expanded');
            self.removeClass('collapsed');
        }
    });
});
