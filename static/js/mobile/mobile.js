$(document).ready(function () {

    // click to play a recently added episode

    $(document).on('click', '#recent_episodes .play', function(e) {
        e.preventDefault();
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/xhr/play/video/episode/' + $(this).data('episodeid'), function () {
            $.mobile.hidePageLoadingMsg();
        });
    });

    // click to play a recently added episode

    $(document).on('click', '#recent_movies .play', function(e) {
        e.preventDefault();
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/xhr/play/video/movie/' + $(this).data('movieid'), function () {
            $.mobile.hidePageLoadingMsg();
        });
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
