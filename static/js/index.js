$(document).ready(function() {

  $.get('/xhr/recently_added', function(data) {
    var module = $(data).hide();
    $('#recently_added_placeholder').replaceWith(module);
    $('#recently_added').fadeIn(200);
  });

  function get_currently_playing() {
    $.get('/xhr/currently_playing', function(data) {

      if (data.playing === false) {
        $('#currently_playing').fadeOut(200, function() {
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

  get_currently_playing();

});