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

      //////////////////
     //  Headphones  //
    //////////////////

    $(document).on('keypress', '#headphones input#search', function(e) {
        if (e.which == 13) {
            $.mobile.showPageLoadingMsg();

            var media = $(this).data('media');
            document.location.href = WEBROOT + '/mobile/headphones/search/' + media + '/' + $(this).val();
        }
    });

    $(document).on('click', '#headphones #results li', function() {
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/mobile/headphones/artist/action/' + $(this).data('id') + '/add/', function(data) {
            if (data.status) {
                alert('Artist is being added.');
            }
            else {
                alert('Failed to add artist.');
            }
            $.mobile.hidePageLoadingMsg();
        });
    });

    $(document).on('click', '#headphones #control a', function() {
        var artistid = $('#headphones #control').data('id');
        var action = $(this).data('action');
        var button = $(this);

        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/mobile/headphones/artist/action/' + artistid + '/' + action, function(data) {
            if (data.status) {
                if (action == 'refresh') {
                    alert('Refreshing artist.');
                }
                else if (action == 'remove') {
                    document.location.href = WEBROOT + '/mobile/headphones/all/';
                }
                else {
                    document.location.href = WEBROOT + '/mobile/headphones/artist/' + artistid;
                }
            }
            else {
                alert('Failed to '+ action +' artist.');
            }
            $.mobile.hidePageLoadingMsg();
        });
    });

    $(document).on('change', '#headphones #album_status select', function() {
        $.mobile.showPageLoadingMsg();
        $.get(WEBROOT + '/mobile/headphones/album/' + $(this).data('id') + '/' + $(this).val(), function(data) {
            if (data.status) {
                alert('Album status changed.');
            }
            else {
                alert('Failed to change album status.');
            }
            $.mobile.hidePageLoadingMsg();
        });
    });

      ////////////////
     //  SabNZBd+  //
    ////////////////

    $(document).on('click', '#sabnzbd_navbar #action,' + // resume/pause queue
        '#sabnzbd_item #sabnzbd_item_navbar #action,' + // resume/pause item
        '#sabnzbd_item #delete,' + // delete item
        '#sabnzbd_history #retry,' + //retry history item
        '#sabnzbd_history #delete,', // delete history item
        function() {
        $.mobile.showPageLoadingMsg();
        $.get($(this).data('url'), function(data) {
            if(data.status){
                $.get(window.location.reload());
            }
        });
    });

    $(document).on('click', '#sabnzbd_navbar #speed', function() {
          $('.speed_popup').simpledialog2();
    });
    
    $(document).on('click', '#speed_popup li', function() {
        $.mobile.showPageLoadingMsg();
        $.get($(this).data('url'), function(data) {
            if(data.status){
                $.get(window.location.reload());
            }
        });
    });

    $(document).on('click keypress', '#speed_popup li input', function(e) {
        e.stopPropagation();
        if(e.which == 13){
            $.mobile.showPageLoadingMsg();
            var speed = $(this).val();
            $.get(WEBROOT + '/xhr/sabnzbd/speedlimit/' + speed, function(data) {
                if(data.status){
                    $.get(window.location.reload());
                }
            });
        }
    });

    $('#sabnzbd li').swipeDelete({
        direction: 'swiperight', // standard jquery mobile event name
        btnLabel: 'Delete',
        btnTheme: 'r',
        btnClass: 'aSwipeBtn',
        click: function(e){
            e.preventDefault();
            $.mobile.showPageLoadingMsg();
            var li = $(this).parents('li');
            $.get(li.data('delete-url'), function(data) {
                $.mobile.hidePageLoadingMsg();
                if(data.status){
                    li.remove();
                }
            });
        }
    });
});
