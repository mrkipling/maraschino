$(document).ready(function () {

      ////////////
     //  XBMC  //
    ////////////

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

    // playback controls

    $(document).on('click', '#header_controls .control', function(e) {
        e.preventDefault();
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/xhr/controls/' + $(this).data('command'), function () {
            $.mobile.hidePageLoadingMsg();
        });
    });


      ///////////////////
     //  CouchPotato  //
    ///////////////////

    // notification read click

    $(document).on('click', '#couchpotato li#notification.new', function() {
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
            $.mobile.showPageLoadingMsg();
            document.location.href = WEBROOT + '/mobile/couchpotato/search/' + $(this).val();
        }
    });

    // add movies

    $(document).on('click', '#couchpotato #results li', function() {
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/xhr/couchpotato/add_movie/' + $(this).data('id') + '/' +  $(this).data('title'), function(data) {
            if(data.success){
                alert('Movie successfully added to CouchPotato');
            } else {
                alert('Failed to add movie');
            }
            $.mobile.hidePageLoadingMsg();
        });
    });

      /////////////////
     //  SickBeard  //
    /////////////////

    // search shows

    $(document).on('keypress', '#sickbeard input#search', function(e) {
        if (e.which == 13) {
            $.mobile.showPageLoadingMsg();
            document.location.href = WEBROOT + '/mobile/sickbeard/search/' + $(this).val();
        }
    });

    // add shows

    $(document).on('click', '#sickbeard #results li', function() {
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/sickbeard/add_show/' + $(this).data('id'), function(data) {
            alert(data);
            $.mobile.hidePageLoadingMsg();
        });
    });

    // delete, update, refresh show

    $(document).on('click', '#sickbeard.show #control a', function() {
        $.mobile.showPageLoadingMsg();
        action = $(this).attr('id');
        $.get(WEBROOT + '/sickbeard/' + action + '_show/' + $(this).data('id'), function(data) {
            alert(data);
            $.mobile.hidePageLoadingMsg();
        });
    });

    $(document).on('click', '#sickbeard.episode #control a#search', function() {
        $.mobile.showPageLoadingMsg();
        $.get($(this).data('url'), function(data) {
            alert(data);
            $.mobile.hidePageLoadingMsg();
        });
    });

      ////////////////
     //  SabNZBd+  //
    ////////////////

    // resume/pause queue

    $(document).on('click', '#sabnzbd_navbar #action', function(e) {
        $.mobile.showPageLoadingMsg();
        $.get($(this).data('url'), function(data) {
            if(data.status){
                $.get(window.location.reload());
            }
        });
    });

});
