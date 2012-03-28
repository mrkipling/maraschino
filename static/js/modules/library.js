// browse library

$(document).on('click', '#library li.get', function() {
  var url = '/xhr/library';
  var commands = $(this).data('command').split('/');

  for (var i=0; i < commands.length; i++) {
    url += '/' + commands[i];
  }

  add_loading_gif(this);

  $.get(url, function(data) {
    $('#library').replaceWith(data);
  });
});

// Filter function

$(document).on('change keydown keyup search', '#library .filter', function(e){
  var filter = $(this).val().toLowerCase();
  $('#library ul li').filter(function(index) {
    return $(this).text().toLowerCase().indexOf(filter) < 0;
  }).css('display', 'none');
  $('#library ul li').filter(function(index) {
    return $(this).text().toLowerCase().indexOf(filter) >= 0;
  }).css('display', '');
  if(e.which == 13){
    $('#library ul li:visible:first').click();
  }
});

$(document).on('click', '#library .filter', function(){
  var filter = $(this).val();
  if(filter === 'Filter'){
    $(this).css('color', '#67C0F8').attr('value', '');
  }
});


// update video library control

$(document).on('click', '#library #video-update', function() {
  $.get('/xhr/controls/update_video');
});

// clean video library control

$(document).on('click', '#library #video-clean', function() {
  $.get('/xhr/controls/clean_video');
});

// update music library control

$(document).on('click', '#library #audio-update', function() {
  $.get('/xhr/controls/update_audio');
});

// clean music library control

$(document).on('click', '#library #audio-clean', function() {
  $.get('/xhr/controls/clean_audio');
});

// xbmc poweron

$(document).on('click', '#library #poweron', function() {
  $.get('/xhr/controls/poweron');
});

// xbmc poweroff

$(document).on('click', '#library #poweroff', function() {
  $.get('/xhr/controls/poweroff');
});

// xbmc reboot

$(document).on('click', '#library #reboot', function() {
  $.get('/xhr/controls/reboot');
});

// xbmc suspend

$(document).on('click', '#library #suspend', function() {
  $.get('/xhr/controls/suspend');
});

$(document).on('click', '#library li.play_episode', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/play_video/episode/' + $(this).data('episodeid'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library li.play_movie', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/play_video/movie/' + $(this).data('movieid'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library li.play_song', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/play_audio/song/' + $(this).data('songid'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library li.enqueue_tvshow', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/enqueue_tvshow/' + $(this).data('tvshowid'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library li.enqueue_season', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/enqueue_season/' + $(this).data('tvshowid') + '/' + $(this).data('season'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library li.enqueue_episode', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/enqueue_video/episode/' + $(this).data('episodeid'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library li.enqueue_movie', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/enqueue_video/movie/' + $(this).data('movieid'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library li.enqueue_artist', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/enqueue_audio/artist/' + $(this).data('artistid'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library li.enqueue_album', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/enqueue_audio/album/' + $(this).data('albumid'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library li.enqueue_song', function() {
  var li = this;
  add_loading_gif(li);

  $.get('/xhr/enqueue_audio/song/' + $(this).data('songid'), function() {
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library .toggle', function() {
  var li = '#library li';
  var type = $(li).attr('media-type');

    if ($('li').hasClass('play_'+type)) {
      $('li').toggleClass('enqueue_'+type);
      $('li').toggleClass('play_'+type);
      $(this).toggleClass('active');
    }

    else if ($('li').hasClass('get')) {
      $('li').toggleClass('enqueue_'+type);
      $('li').toggleClass('get');
      $(this).toggleClass('active');
    }
});

$(document).on('click', '#library .back', function() {
  var url = '/xhr/library';
  var command = $('#library li:first-child').eq(0).data('command');

  if (command) {
    var commands = command.split('/');
    commands.pop();
    commands.pop();

    for (var i=0; i < commands.length; i++) {
      url += '/' + commands[i];
    }
  }

  $(this).addClass('xhrloading');

  $.get(url, function(data) {
    $('#library').replaceWith(data);
  });
});

$(document).on('click', '#library li.dir', function() {
  var path = $(this).data('path');

  add_loading_gif(this);
  $.post('/xhr/library/files/' + $(this).data('file_type') + '/dir/',{path: encodeURI(path)}, function(data){
    $('#library').replaceWith(data);
  });
});

$(document).on('click', '#library li.play_file', function() {
  var li = this;
  var file = $(this).data('path');

  add_loading_gif(li);
  $.post('/xhr/play_file/' + $(this).data('file_type') + '/',{file: encodeURI(file)}, function(data){
    remove_loading_gif(li);
  });
});

$(document).on('click', '#library #resume_button', function() {
  var type = $(this).attr('media-type');

  $.get('/xhr/resume_video/' + type + '/' + $(this).data('id'));
});
