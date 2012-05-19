$(document).ready(function () {

    // click to play a recently added episode

    $(document).on('click', '#recent_episodes .play', function(e) {
        e.preventDefault();
        $.mobile.showPageLoadingMsg();
        $.get('/xhr/play/video/episode/' + $(this).data('episodeid'), function () {
            $.mobile.hidePageLoadingMsg();
        });
    });

    // playback controls

    $(document).on('click', '#header_controls .control', function(e) {
        e.preventDefault();
        $.mobile.showPageLoadingMsg();
        $.get('/xhr/controls/' + $(this).data('command'), function () {
            $.mobile.hidePageLoadingMsg();
        });
    });

});
