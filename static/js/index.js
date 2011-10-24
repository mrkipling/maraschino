$(document).ready(function() {

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

  get_recently_added();
  get_currently_playing();

});