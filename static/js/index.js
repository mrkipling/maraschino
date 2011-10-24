$(document).ready(function() {

  $.get('/xhr/recently_added', function(data) {
    $('#recently_added_placeholder').replaceWith(data);
  });

});