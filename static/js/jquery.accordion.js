$(document).ready(function(){

    // Set accordion variable
    var accordion = $('.accordion');

    accordion.on('click', '.accordion__tab-title', function(event) {
        event.preventDefault();

        // Find and 'active' class in the accordion and removes it
        accordion.find('.accordion__tab-title').removeClass('active');

        // Sets active class to clicked tab title
        $(this).addClass('active');
    });
});
