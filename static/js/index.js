$(document).ready(function() {

  /* get active modules */

  var modules = $('body').data('modules').split(',');

  function module_is_active(module) {
    for (var i in modules) {
      if (modules[i] === module) {
        return true;
      }
    }

    return false;
  }

  /* recently added */

  function get_recently_added() {
    $.get('/xhr/recently_added', function(data) {
      var recently_added_module = $('#recently_added');

      if (recently_added_module.length > 0) {
        recently_added_module.replaceWith(data);

      } else {
        var module = $(data).hide();
        $('#recently_added_placeholder').replaceWith(module);
        $('#recently_added').fadeIn(200);
      }
    });

    setTimeout(get_recently_added, 600000);
  }

  $('#recently_added li').live('click', function() {
    $.get('/xhr/play_episode/' + $(this).data('episodeid'));
  });

  /* SABnzbd+ */

  function get_sabnzbd() {
    $.get('/xhr/sabnzbd', function(data) {
      var sabnzbd_module = $('#sabnzbd');

      if (sabnzbd_module.length > 0) {
        if ($(data).attr('id') === 'sabnzbd') {
          sabnzbd_module.replaceWith(data);
        } else {
          sabnzbd_module.fadeOut(200, function() {
            $(this).replaceWith(data);
          });
        }

      } else {
        var module = $(data).hide();
        $('#sabnzbd_placeholder').replaceWith(module);
        $('#sabnzbd').fadeIn(200);
      }
    });

    setTimeout(get_sabnzbd, 10000);
  }

  /* currently playing */

  function get_currently_playing() {
    $.get('/xhr/currently_playing', function(data) {

      if (data.playing === false) {
        $('#currently_playing').slideUp(200, function() {
          $(this).remove();
        });

      } else {
        var currently_playing_module = $('#currently_playing');

        if (currently_playing_module.length > 0) {
          currently_playing_module.replaceWith(data);

        } else {
          var module = $(data).hide();
          $('body').append(module);
          $('#currently_playing').slideDown(200);
        }
      }
    });

    setTimeout(get_currently_playing, 10000);
  }

  /* load active XHR modules */

  if (module_is_active('recently_added')) {
    get_recently_added();
  }

  if (module_is_active('sabnzbd')) {
    get_sabnzbd();
  }

  if (module_is_active('currently_playing')) {
    get_currently_playing();
  }

});