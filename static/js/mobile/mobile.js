$(document).ready(function () {

    // click to play a recently added episode

    $(document).on('click', '#recent_episodes .play, #season .play', function(e) {
        e.preventDefault();
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/xhr/play/video/episode/' + $(this).data('episodeid'), function () {
            $.mobile.hidePageLoadingMsg();
        });
    });

    // click to play a recently added movies and movie library

    $(document).on('click', '#recent_movies .play, #movie_library .play', function(e) {
        e.preventDefault();
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/xhr/play/video/movie/' + $(this).data('movieid'), function () {
            $.mobile.hidePageLoadingMsg();
        });
    });

    // click to play a recently added albums

    $(document).on('click', '#recent_albums .play', function(e) {
        e.preventDefault();
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/xhr/play/audio/album/' + $(this).data('albumid'), function () {
            $.mobile.hidePageLoadingMsg();
        });
    });

    // notification read click

    $(document).on('click', '#couchpotato li#notification.new', function(e) {
        $.get(WEBROOT + '/xhr/couchpotato/notification/read/' + $(this).data('id'), function(data) {
            if(data.success){
                $(this).attr('data-theme', 'c').removeClass('ui-body-e').addClass('ui-body-c');
                $('#unread').text($('#unread').text()-1);
            } else {
                alert('Failed to mark notification as read');
            }
        });
    });

    // search movies

    $(document).on('keypress', '#couchpotato input#search', function(e) {
        if (e.which == 13) {
            document.location.href = WEBROOT + '/mobile/couchpotato/search/' + $(this).val();
        }
    });


    // playback controls

    $(document).on('click', '#header_controls .control', function(e) {
        e.preventDefault();
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/xhr/controls/' + $(this).data('command'), function () {
            $.mobile.hidePageLoadingMsg();
        });
    });

});
