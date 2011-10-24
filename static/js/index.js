$(document).ready(function() {

  /* active modules */

  var active_modules = [];

  $('.placeholder').each(function() {
    active_modules.push($(this).data('module'));
  });

  function module_is_active(module) {
    for (var i=0; i < active_modules.length; i++) {
      if (active_modules[i] === module) {
        return true;
      }
    }
    return false;
  }

  /* applications */

  function get_applications() {
    $.get('/xhr/applications', function(data) {
      var applications_module = $('#applications');

      if (applications_module.length > 0) {
        applications_module.replaceWith(data);

      } else {
        var module = $(data).hide();
        $('#applications_placeholder').replaceWith(module);
        $('#applications').fadeIn(200);
      }
    });
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

    setTimeout(get_recently_added, 300000);
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

    setTimeout(get_sabnzbd, 5000);
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

    setTimeout(get_currently_playing, 5000);
  }

  /* load active XHR modules */

  if (module_is_active('applications')) {
    get_applications();
  }

  if (module_is_active('recently_added')) {
    get_recently_added();
  }

  if (module_is_active('sabnzbd')) {
    get_sabnzbd();
  }

  if ($('body').data('show_currently_playing') == 'True') {
    get_currently_playing();
  }

});