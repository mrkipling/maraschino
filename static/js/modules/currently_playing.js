if ($('body').data('show_currently_playing') === 'True') {
  get_currently_playing();
}

// currently playing

var currently_playing_id = null;

function get_currently_playing() {
  $.get('/xhr/currently_playing', function(data) {

    if (data.playing === false) {

      // hide currently playing
      $('#currently_playing').slideUp(200, function() {
        $(this).remove();
      });

      // hide synopsis module if visible
      $('#synopsis').fadeOut(200, function() {
        $(this).replaceWith(construct_inactive_module('synopsis', 'Synopsis'));
      });

      // hide trakt module if visible
      $('#trakt').fadeOut(200, function() {
        $(this).replaceWith(construct_inactive_module('trakt', 'trakt.tv'));
      });

      currently_playing_id = null;

    } else {
      var currently_playing_module = $('#currently_playing');

      if (currently_playing_module.length > 0) {
        currently_playing_module.replaceWith(data);

      } else {
        var module = $(data).hide();
        $('body').append(module);
        $('#currently_playing').slideDown(200);
      }

      // use fanart of currently playing item as background if enabled in settings

      if ($('body').data('fanart_backgrounds') === 'True') {
        var fanart_url = $('#currently_playing').data('fanart');
        if (fanart_url !== undefined) {
          var img = new Image();
          img.onload = function() {
            var fanart = $('#fanart');
            fanart.css('background-image', 'url(' + fanart_url + ')');
            if (!fanart.is(':visible')) {
              fanart.fadeIn(500);
            }
          };
          img.src = fanart_url;
        }
      }

      // synopsis

      // if synopsis module is enabled
      var synopsis_module = $('#synopsis, #synopsis_inactive');
      if (synopsis_module.length > 0) {

        // if currently playing item has a synopsis
        var synopsis = $('#currently_playing .synopsis');
        if (synopsis.length > 0) {
          var module = $('<div id="synopsis" class="module generic" data-module="synopsis">' + settings_buttons + '<h2></h2><div class="inner"><p></p></div></div>');
          module.find('h2').replaceWith(synopsis.find('h2'));
          module.find('p').replaceWith(synopsis.find('p'));

          // if already visible
          if (synopsis_module.hasClass('module')) {
            synopsis_module.replaceWith(module);

          // else if not visible
          } else {
            module.hide();
            synopsis_module.replaceWith(module);
            module.fadeIn(200);
          }

        // if no synopsis
        } else {

          // if visible
          if (synopsis_module.hasClass('module')) {
            synopsis_module.fadeOut(200, function() {
              $(this).replaceWith(construct_inactive_module('synopsis', 'Synopsis'));
            });
          }
        }

      } // if synopsis module is enabled

      // trakt

      if ($('#trakt, #trakt_inactive').length > 0 && currently_playing_id !== $(data).data('id')) {
        get_module('trakt', {
          placeholder: $('#trakt_inactive')
        });
      }

      currently_playing_id = $(data).data('id');
    }
  });

  setTimeout(get_currently_playing, 5000);
}

// play/pause control

$(document).on('click', '#currently_playing .controls .play_pause', function() {
  $.get('/xhr/controls/play_pause');
});

// stop control

$(document).on('click', '#currently_playing .controls .stop', function() {
  $.get('/xhr/controls/stop');
});

// click show name to view in media library module

$(document).on('click', '#currently_playing .item_info_show .show', function() {
  invoke_library('/xhr/library/shows/' + $(this).data('show'));
});

// click show season to view in media library module

$(document).on('click', '#currently_playing .item_info_show .season', function() {
  invoke_library('/xhr/library/shows/' + $(this).parent().find('.show').data('show') + '/' + $(this).data('season'));
});

// click artist name to view in media library module

$(document).on('click', '#currently_playing .item_info_artist .artist', function() {
  invoke_library('/xhr/library/artists/' + $(this).data('artist'));
});

// click show album to view in media library module

$(document).on('click', '#currently_playing .item_info_artist .album', function() {
  invoke_library('/xhr/library/artists/' + $(this).parent().find('.artist').data('artist') + '/' + $(this).data('album'));
});
