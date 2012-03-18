// view more recently added episodes

$(document).on('click', '#recently_added .view_older', function() {
  get_module('recently_added', {
    params: [$('#recently_added').data('episode_offset') + $('#recently_added .episodes > li').length]
  });
  return false;
});

$(document).on('click', '#recently_added .view_newer', function() {
  get_module('recently_added', {
    params: [$('#recently_added').data('episode_offset') - $('#recently_added .episodes > li').length]
  });
  return false;
});

// view more recently added movies

$(document).on('click', '#recently_added_movies .view_older', function() {
  get_module('recently_added_movies', {
    params: [$('#recently_added_movies').data('movie_offset') + $('#recently_added_movies .movies > li').length]
  });
  return false;
});

$(document).on('click', '#recently_added_movies .view_newer', function() {
  get_module('recently_added_movies', {
    params: [$('#recently_added_movies').data('movie_offset') - $('#recently_added_movies .movies > li'). length]
  });
  return false;
});

// view more recently added albums

$(document).on('click', '#recently_added_albums .view_older', function() {
  get_module('recently_added_albums', {
    params: [$('#recently_added_albums').data('album_offset') + $('#recently_added_albums .albums > li').length]
  });
  return false;
});

$(document).on('click', '#recently_added_albums .view_newer', function() {
  get_module('recently_added_albums', {
    params: [$('#recently_added_albums').data('album_offset') - $('#recently_added_albums .albums > li').length]
  });
  return false;
});

// play recently added episodes when clicking on them

$(document).on('click', '#recently_added .episodes li', function() {
  $.get('/xhr/play_video/episode/' + $(this).data('episodeid'));
});

// play recently added movies when clicking on them

$(document).on('click', '#recently_added_movies li', function() {
  $.get('/xhr/play_video/movie/' + $(this).data('movieid'));
});

// play recently added albums when clicking on them

$(document).on('click', '#recently_added_albums li', function() {
  $.get('/xhr/play_audio/album/' + $(this).data('albumid'));
});