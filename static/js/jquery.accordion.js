jQuery(document).ready(function($) {

    // Set accordion variable
    var accordion = $('.accordion');

    // Sets the first accordion tab to active
    accordion.find('.accordion__tab-title').first().addClass('active');

    accordion.on('click', '.accordion__tab-title', function(event) {
        event.preventDefault();

        // Find and 'active' class in the accordion and removes it
        accordion.find('.active').removeClass('active');

        // Sets active class to clicked tab title
        $(this).addClass('active');
    });
});
