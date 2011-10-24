$(document).ready(function() {

  $.get('/xhr/recently_added', function(data) {
    var module = $(data).hide();
    $('#recently_added_placeholder').replaceWith(module);
    $('#recently_added').fadeIn(200);
  });

});