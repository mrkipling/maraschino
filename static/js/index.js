$(document).ready(function() {
  // helper functions

  var settings_buttons = '<div class="module_settings"><span>Settings</span></div><div class="module_remove"><span>Remove</span></div>';

  function construct_inactive_module(name, title) {
    return '<div id="' + name + '_inactive" class="inactive_module" data-module="' + name + '">' + settings_buttons + '<h2>' + title + '</h2></div></div>';
  }

  function confirmation_dialog(customsettings) {
    var settings = {
      question: 'Are you sure?',
      confirm: function() {},
      cancel: function() {}
    };

    if (customsettings !== undefined) {
      $.extend(settings, customsettings);
    }

    var dialog = '<div id="confirmation_dialog" class="dialog"><h3>' + settings.question + '</h3><div class="choices"><div class="confirm">Yes</div><div class="cancel">No</div></div></div>';

    $('body').append(dialog);

    $('#confirmation_dialog').showPopup({
      dispose: true,
      on_confirm: settings.confirm,
      on_close: settings.cancel
    });
  }

  function validate_form(form) {
    var valid = true;
    var required = $(form).find('.required');

    required.each(function() {
      var formrow = $(this).closest('.formrow');

      if ($(this).val() == '') {
        valid = false;
        formrow.addClass('invalid');

      } else {
        formrow.removeClass('invalid');
      }
    });

    return valid;
  }

  function popup_message(message) {
    var popup = $('<div id="popup_message" class="dialog"><div class="close">x</div><p>' + message + '</p><div class="choices"><div class="cancel">OK</div></div></div>');
    $('body').append(popup);
    popup.showPopup({ dispose: true });
  };

  // get/poll module

  function get_module(module, customsettings) {
    var settings = {
      poll: 0,
      placeholder: $('.placeholder[data-module=' + module + ']'),
      params: []
    }

    if (customsettings !== undefined) {
      $.extend(settings, customsettings);
    }

    var url = '/xhr/' + module;

    for (var i=0; i < settings.params.length; i++) {
      url += '/' + settings.params[i];
    }

    $.get(url, function(data) {
      var module_ele = $('#' + module);

      // if module is already on page
      if (module_ele.length > 0) {

        // if module has been returned by the XHR view
        if ($(data).attr('id') === module) {
          module_ele.replaceWith(data);

        // else placeholder has been returned by the XHR view
        } else {
          module_ele.fadeOut(200, function() {
            $(this).replaceWith(data);
          });
        }

      // placeholder is on page
      } else {
        var new_module = $(data).hide();
        settings.placeholder.replaceWith(new_module);
        $('.module[data-module=' + module + ']').fadeIn(200);
      }
    });

    // poll
    if (settings.poll !== 0) {
      setTimeout(function() {
        get_module(module, {
          poll: settings.poll
        })
      }, settings.poll * 1000);
    }
  }

  // initialise modules on page load

  function init_modules() {
    $('.placeholder:not(.initialised)').each(function() {
      $(this).addClass('initialised');
      var delay = $(this).data('delay');
      if (delay === undefined) {
        get_module($(this).data('module'), {
          poll: $(this).data('poll')
        });
      } else {
        var module = $(this).data('module');
        var poll = $(this).data('poll');
        setTimeout(function() {
          get_module(module, {
            poll: poll
          });
        }, delay * 1000);
      }
    });
  }

  init_modules();

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

  // Settings tab
  $(document).on('click', '#server_settings .tab', function(){
    if($('#server_settings .inner').css('display') == 'none'){
      $('#server_settings .inner').slideDown();
    } else {
      $('#server_settings .inner').slideUp();
    }
  });

  if ($('body').data('show_currently_playing') === 'True') {
    get_currently_playing();
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

  function invoke_library(url) {
    $.get(url, function(data) {
      var library = $('#library');
      if (library.length > 0) {
        library.replaceWith(data);
      } else {
        $('#col1').append(data);
      }
    });
  }

  // Filter function

  $(document).on('change keydown keyup search', '#library .powerholder .filter', function(e){
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

  $(document).on('click', '#library .powerholder .filter', function(){
    var filter = $(this).val();
    if(filter === 'Filter'){
      $(this).css('color', 'black').attr('value', '');
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

  // post trakt shout

  $(document).on('click', '#add_shout .submit', function() {
    var add_shout = $('#add_shout');
    var textarea = add_shout.find('textarea');
    var submit_wrapper = add_shout.find('.submit_wrapper');

    if (textarea.val().length === 0) {
      var error_message = submit_wrapper.find('p');

      if (error_message.length === 0) {
        submit_wrapper.append('<p>');
        error_message = submit_wrapper.find('p');
      }

      error_message.text('You need to enter a shout.');
      return false;
    }

    var type = add_shout.data('type');

    var dict = {
      type: type,
      itemid: add_shout.data('itemid'),
      shout: textarea.val()
    };

    if (type === 'episode') {
      dict['season'] = add_shout.data('season');
      dict['episode'] = add_shout.data('episode');
    }

    submit_wrapper.addClass('xhrloading');

    $.post('/xhr/trakt/add_shout', dict, function(data) {
      submit_wrapper.removeClass('xhrloading');
      submit_wrapper.find('p').remove();
      textarea.val('');

      if (data.status === 'error') {
        submit_wrapper.append('<p>There was a problem submitting your shout.</p>');
        return false;
      }

      if ($(data).attr('id') === 'trakt') {
        $('#trakt').replaceWith(data);
      }
    });
  });

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

  // play recently added episodes when clicking on them

  $(document).on('click', '#recently_added .episodes li', function() {
    $.get('/xhr/play_video/episode/' + $(this).data('episodeid'));
  });

  // play recently added movies when clicking on them

  $(document).on('click', '#recently_added_movies li', function() {
    $.get('/xhr/play_video/movie/' + $(this).data('movieid'));
  });

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
    $('li').toggleClass('enqueue_'+type);
    $('li').toggleClass('play_'+type);
      if ($('li').hasClass('play_'+type)) {
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





  /*** SICKBEARD ***/

  // Search Episode Functionality on Magnifying Glass png

  $(document).on('click', '#sickbeard .coming_ep div.options img.search', function(){
    $(this).attr('src','/static/images/xhrloading.gif');
    var ep = $(this).attr('episode');
    var season = $(this).attr('season');
    var id = $(this).attr('id');
    $.get('/sickbeard/search_ep/'+id+'/'+season+'/'+ep)
    .success(function(data){
	  if(data){
	    $('#sickbeard #'+id+'_'+season+'_'+ep+' div.options img.search').attr('src','/static/images/yes.png');
	  } else {
	    $('#sickbeard #'+id+'_'+season+'_'+ep+' div.options img.search').attr('src','/static/images/no.png');
	  }
    })
    .error(function(){
	  popup_message('Could not reach Sick-Beard.');
    });
  });

  // Air time on hover

  $(document).on('hover', '#sickbeard .coming_ep', function(){
    var id = ($(this).attr('id'));
  });


  // Load show info from banner display

  $(document).on('click', '#sickbeard .coming_ep .options img.banner', function(){
    var tvdb = $(this).attr('id');
    $.get('/sickbeard/get_show_info/'+tvdb, function(data){
      $('#sickbeard').replaceWith(data);
    });
  });

  // Plot display function

  $(document).on('mouseenter', '#sickbeard .coming_ep .details .plot-title', function(){
    $(this).toggle();
    var id = $(this).closest('div.coming_ep').attr('id');
    $('#sickbeard #'+id+' .details .plot').toggle();
  });

  // Plot hide function

  $(document).on('mouseleave', '#sickbeard .coming_ep', function(){
    var id = $(this).attr('id');
    $('#sickbeard #'+id+' .details .plot-title').show();
    $('#sickbeard #'+id+' .details .plot').hide();
  });

  // Toggle missed episodes

  $(document).on('click', '#sickbeard #missed', function(){
    $('#sickbeard .missed').toggle();
  });

  // All Shows menu

  $(document).on('click', '#sickbeard .menu .all', function(){
    $.get('/sickbeard/get_all', function(data){
      $('#sickbeard').replaceWith(data);
    });
  });

  // Coming episodes Menu

  $(document).on('click', '#sickbeard .menu .upcoming', function(){
    $.get('/xhr/sickbeard', function(data){
      $('#sickbeard').replaceWith(data);
    });
  });

  // History menu

  $(document).on('click', '#sickbeard .menu .history', function(){
    $.get('/sickbeard/history/30', function(data){
      $('#sickbeard').html($(data).html());
    });
  });

  $(document).on('click', '#sickbeard .history ul.toggle', function(){
    $('#sickbeard .history .Snatched').toggle();
    $(this).toggleClass('active');
  });

  // Show Menu

  $(document).on( 'click', '#sickbeard .menu-icon', function(){
    $('#sickbeard .menu').fadeToggle(200);
  });

  // Show info

  $(document).on('click', '#sickbeard #sickbeard-list ul', function(){
    var id = $(this).attr('id');
    $.get('/sickbeard/get_show_info/'+id, function(data){
      $('#sickbeard').replaceWith(data);
    });
  });

  // Episode list back button functionality

  $(document).on('click', '#sb_content > #show .sb-back', function(){
    $.get('/sickbeard/get_all', function(data){
      $('#sickbeard').replaceWith(data);
    });
  });

  // Season info

  $(document).on('click', '#sb_content > #show ul.seasons li', function(){
    $.get('/sickbeard/get_season/'+$(this).attr('tvdbid')+'/'+$(this).attr('season'), function(data){
      $('#sickbeard').replaceWith(data);
      $('#sickbeard .episode-list .tablesorter').tablesorter({sortList: [[0,0]]});
    });
  });

  // Going into episode info

  $(document).on('click', '#sickbeard .episode-list #season tbody tr', function(){
    $.get('/sickbeard/get_ep_info/'+$(this).attr('link'), function(data){
      $('#sickbeard').replaceWith(data);
    });
  });

  // Episode info back button functionality

  $(document).on('click', '#sickbeard .episode-info .back', function(){
    $.get('/sickbeard/get_season/'+$(this).attr('tvdbid')+'/'+$(this).attr('season'), function(data){
      $('#sickbeard').replaceWith(data);
      $('#sickbeard .episode-list .tablesorter').tablesorter({sortList: [[0,0]]});
    });
  });

  // Back Button Episode List

  $(document).on('click', '#sickbeard .episode-list >.back', function(){
    $.get('/sickbeard/get_show_info/'+$(this).attr('tvdbid'), function(data){
      $('#sickbeard').replaceWith(data);
    });
  });

  // Show Banner manager display

  $(document).on('click', '#sickbeard #show .banner .options' , function(){
    $('#sickbeard #show .banner .manage').show();
  });

  // Hide Banner manager display

  $(document).on('click', '#sickbeard #show .banner .manage .close' , function(){
    $('#sickbeard #show .banner .manage').hide();
  });

  //Delete show function

  $(document).on('click', '#sickbeard #show .banner .manage .delete' , function(){
    var id = $('#sickbeard #show .banner .manage').attr('tvdbid')
    $.get('/sickbeard/delete_show/'+id)
    .success(function(data){
      popup_message(data);
    })
    .error(function(){
      popup_message('Could not reach Sickbeard.');
    });
  });

  //Refresh show function

  $(document).on('click', '#sickbeard #show .banner .manage .refresh' , function(){
    var id = $('#sickbeard #show .banner .manage').attr('tvdbid')
    $.get('/sickbeard/refresh_show/'+id)
    .success(function(data){
      popup_message(data);
    })
    .error(function(){
      popup_message('Could not reach Sickbeard.');
    });
  });

  //Update show function

  $(document).on('click', '#sickbeard #show .banner .manage .update' , function(){
    var id = $('#sickbeard #show .banner .manage').attr('tvdbid')
    $.get('/sickbeard/update_show/'+id)
    .success(function(data){
      popup_message(data);
    })
    .error(function(){
      popup_message('Could not reach Sickbeard.');
    });
  });

  // Shutoff function

  $(document).on('click', '#sickbeard div.powerholder .power', function(){
    $.get('/sickbeard/shutdown')
    .success(function(data){
      popup_message(data);
    })
    .error(function(){
      popup_message('Could not reach Sickbeard.');
    });
  });

  // Restart Function

  $(document).on('click', '#sickbeard div.powerholder .restart', function(){
    $.get('/sickbeard/restart')
    .success(function(data){
      popup_message(data);
    })
    .error(function(){
      popup_message('Could not reach Sickbeard.');
    });
  });

  // Log function

  $(document).on('click', '#sickbeard div.powerholder .log', function(){
    $.get('/sickbeard/log/error', function(data){
      $('#sickbeard').replaceWith(data);
    });
  });

  // Log info level change

  $(document).on('change', '#sickbeard #log .level', function(){
    var level = $('#sickbeard #log .level').attr('value');
    $.get('/sickbeard/log/'+level, function(data){
      $('#sickbeard').replaceWith(data);
    });
  });

  // Load search template

  $(document).on('click', '#sickbeard div.powerholder .add', function(){
    $.get('/sickbeard/search/')
    .success(function(data){
      $('#sickbeard').replaceWith(data);
    })
    .error(function(){
      popup_message('Could not reach Maraschino.');
    });
  });

  // Load search results

  $(document).on('keypress', '#sickbeard #search #value', function(e){
    if(e.which == 13){
      e.preventDefault();
      var name = $('#sickbeard #search #value').attr('value');
      var type = $('#sickbeard #search #tvdbid').attr('value');
      var lang = $('#sickbeard #search #lang').attr('value');
      params = ''
      if(name != ''){
        if(type == 'name'){
          params = 'name='+name;
        } else {
          params = 'tvdbid='+name;
        }
        if(lang != ''){
          params = params + '&lang='+lang;
        }
      }
      $.get('/sickbeard/search/?'+params)
      .success(function(data){
        $('#sickbeard').replaceWith(data);
      })
      .error(function(){
	popup_message('Could not reach Maraschino.');
      });
    }
  });

  // Add show function

  $(document).on('click', '#sickbeard #search #result tr', function(){
    $.get('/sickbeard/add_show/'+$(this).attr('tvdbid'))
    .success(function(data){
      popup_message(data);
    })
    .error(function(data){
      popup_message('Could not reach Maraschino.');
    });
  });

  // Magnifying Glass Episode INFO

  $(document).on('click', '#sickbeard .episode-info .status .search', function(){
    $(this).attr('src','/static/images/xhrloading.gif');
    var ep = $(this).attr('episode');
    var season = $(this).attr('season');
    var id = $(this).attr('id');
    $.get('/sickbeard/search_ep/'+id+'/'+season+'/'+ep)
    .success(function(data){
      if(data){
	$('#sickbeard .episode-info .status .search').attr('src','/static/images/yes.png');
      } else {
        $('#sickbeard .episode-info .status .search').attr('src','/static/images/no.png');
      }
    })
    .error(function(){
      popup_message('There was a problem with Sick-Beard.');
    });
  });

  // Episode set status info

  $(document).on('change', '#sickbeard .episode-info .status select', function(){
    var ep = $(this).attr('episode');
    var season = $(this).attr('season');
    var id = $(this).attr('id');
    var status = this.value;
    $.get('/sickbeard/set_ep_status/'+id+'/'+season+'/'+ep+'/'+status)
    .success(function(data){
      if (data.status !== 'success') {
        popup_message('An error ocurred: '+data);
      }
    })
    .error(function(){
      popup_message('There was a problem with Sick-Beard.');
    });
  });

  /******  END SICKBEARD Functions  *******/

  /*********** REMOTE *************/

  var remote = false;
  var remote_connected = false;
  var remote_connection;
  // Activates remote functions
  function send_key(key){
    $.get('/remote/'+key)
    .success(function(data){
      if(data.error){
        popup_message(data.error);
      }
    })
    .error(function(){
      popup_message('Could not reach Maraschino');
    });
  }

  $(document).on('click', '#remote_icon', function(){
    $(this).toggleClass('on');
    if(remote){
      remote = false;
      remote_connected = false;
      $.get('/remote/close');
      clearInterval(remote_connection);
    } else {
      remote = true;
      remote_connected = true;
      $.get('/remote/connect');
      remote_connection = setInterval(function(){$.get('/remote/ping');}, 59000);
    }
    if(remote){
      $(document).on('keydown', 'body' , function(e){
        e.preventDefault();
        var char = '';
        var keyCodeMap = {8:"backspace", 9:"tab", 13:"return", 16:"shift", 17:"ctrl", 18:"alt", 19:"pausebreak", 20:"capslock", 27:"escape", 32:"space",
            33:"pageup", 34:"pagedown", 35:"end", 36:"home", 37:"left", 38:"up", 39:"right", 40:"down", 43:"plus", 44:"printscreen", 45:"insert", 46:"delete",
            48:"0", 49:"1", 50:"2", 51:"3", 52:"4", 53:"5", 54:"6", 55:"7", 56:"8", 57:"9", 59:"semicolon", 61:"plus", 65:"a", 66:"b", 67:"c", 68:"d", 69:"e",
            70:"f", 71:"g", 72:"h", 73:"i", 74:"j", 75:"k", 76:"l", 77:"m", 78:"n", 79:"o", 80:"p", 81:"q", 82:"r", 83:"s", 84:"t", 85:"u", 86:"v", 87:"w",
            88:"x", 89:"y", 90:"z", 96:"0", 97:"1", 98:"2", 99:"3", 100:"4", 101:"5", 102:"6", 103:"7", 104:"8", 105:"9", 106: "*", 107:"plus", 109:"minus",
            110:"period", 111: "forwardslash", 112:"f1", 113:"f2", 114:"f3", 115:"f4", 116:"f5", 117:"f6", 118:"f7", 119:"f8", 120:"f9", 121:"f10", 122:"f11",
            123:"f12", 144:"numlock", 145:"scrolllock", 186:"semicolon", 187:"plus", 188:"comma", 189:"minus", 190:"period", 191:"forwardslash", 192:"tilde",
            219:"openbracket", 220:"backslash", 221:"closebracket", 222:"singlequote"};
        if (e.which == null){
          char= String.fromCharCode(e.keyCode);    // old IE
        } else {
          char = keyCodeMap[e.which];
        }
        send_key(char);
      });
    } else {
      $(document).off('keydown', 'body');
    }
  });
  /********* END REMOTE ***********/

  /********* START SABNZBD ***********/

  $(document).on('click', '#sabnzbd .inner #status', function(){
    var state = false;
    if($(this).attr('status').toLowerCase() === 'true'){
      //queue is paused
      state = 'resume';
    } else {
      state = 'pause';
    }
    $.get('/xhr/sabnzbd/queue/'+state+'/')
    .success(function(data){
      if(data.status === 'true'){
        get_module('sabnzbd');
      }
    })
    .error(function(){
      popup_message('Problem reaching Maraschino on /xhr/sabnzbd/queue/<var>/');
    });
  });

  $(document).on('keypress', '#sabnzbd .inner .speed input', function(e){
    if(e.which == 13){
      $.get('/xhr/sabnzbd/speedlimit/'+$(this).attr('value'))
      .success(function(data){
        if(data.status === 'true'){
          get_module('sabnzbd');
        }
      })
      .error(function(){
        popup_message('Problem reaching Maraschino on /xhr/sabnzbd/speedlimit/<var>/');
      });
    }
  });

  /********* END SABNZBD ***********/

  function add_loading_gif(element) {
    $(element).append('<img src="/static/images/xhrloading.gif" class="xhrloading" width="18" height="15" alt="Loading...">');
  }

  function remove_loading_gif(element) {
    $(element).find('.xhrloading').remove();
  }

  // generic expand truncated text

  $(document).on('click', '.expand', function() {
    var parent = $(this).parent();
    parent.find('.truncated').hide();
    parent.find('.expanded').show();
    $(this).hide();
    return false;
  });

  // sortable modules

  $('ul.modules').sortable({
    connectWith: 'ul.modules',
    opacity: 0.8,
    distance: 80,
    disabled: true,
    stop: function() {
      var modules = [];

      $('.module, .inactive_module, .placeholder').each(function() {
        var position = 0;
        var li = $(this).closest('li');
        var column_ele = $(this).closest('.col');
        var lis = column_ele.find('ul.modules > li');

        for (var i = 0; i < lis.length; i++) {
          if (lis[i] == li.get(0)) {
            position = i+1;
            break;
          }
        }

        modules.push({
          name: $(this).data('module'),
          column: column_ele.attr('id').replace('col', ''),
          position: position
        });
      });

      $.post('/xhr/rearrange_modules', { modules: JSON.stringify(modules) }, function() {});
    }
  });

  // settings mode

  $(document).on('click', '#settings_icon', function() {
    $('body').toggleClass('f_settings_mode');
    $('body').toggleClass('f_operation_mode');
    $('add_module').toggle();
    $('#tutorial').remove();

    if ($('body').hasClass('f_settings_mode')) {
      $('ul.modules').sortable({ disabled: false });

      $.get('/xhr/server_settings_dialog', function(data) {
        var existing_server_settings = $('#server_settings');

        if (existing_server_settings.length === 0) {
          $('body').append(data);
        } else {
          existing_server_settings.replaceWith(data);
        }
      });

    } else {
      $('ul.modules').sortable({ disabled: true });
      $('.edit_settings .choices .cancel').click();
      $('#server_settings').closest('li').remove();
    }
  });

  // add module

  $(document).on('click', '.add_module', function() {
    var column = $(this).closest('.col').attr('id');
    $.get('/xhr/add_module_dialog', function(data) {
      var existing_dialog = $('#add_module_dialog').length > 0;
      if (!existing_dialog) {
        var popup = $(data);
        $('body').append(popup);
        popup.data('col', column.replace('col', ''));
        popup.showPopup({ dispose: true });
      }
    });
  });

  $(document).on('change', '#add_module_dialog #select_module', function() {
    var module_description = $('#add_module_dialog .description');
    if (module_description.length === 0) {
      $('#add_module_dialog #select_module').after('<p class="description">');
      module_description = $('#add_module_dialog .description');
    }
    module_description.text($(this).find(':selected').data('description'));
  });

  $(document).on('click', '#add_module_dialog .submit', function() {
    var module_id = $('#add_module_dialog #select_module :selected').val();
    var column = $('#add_module_dialog').data('col');
    var position = $('#col' + column).find('.module, .placeholder').length + 1;

    $.post('/xhr/add_module', {
      module_id: module_id,
      column: column,
      position: position
    }, function(data) {
      $('#col' + column).find('ul.modules').append('<li>' + data + '</li>');
      init_modules();
      $('#add_module_dialog').fadeOut(300, function() {
        $(this).find('.close').click();
      });
    });
  });

  // remove module

  $(document).on('click', '.module_remove', function() {
    var button = $(this);

    confirmation_dialog({
      question: 'Are you sure that you want to remove this module?',
      confirm: function() {
        var module = button.closest('.module, .inactive_module, .placeholder');
        $.post('/xhr/remove_module/' + module.data('module'), {}, function() {
          module.fadeOut(300, function() {
            $(this).remove();
          });
        });
      }
    });
  });

  // module settings

  $(document).on('click', '.module_settings', function() {
    var module = $(this).closest('.module, .inactive_module, .placeholder');

    $.get('/xhr/module_settings_dialog/' + module.data('module'), function(data) {
      module.replaceWith(data);
    });
  });

  // save settings

  $(document).on('click', '.edit_settings .choices .save', function() {
    var module = $(this).closest('.module, .inactive_module, .placeholder, #server_settings');
    var module_name = module.data('module');
    var settings = module.find('form').serializeArray();

    $.post('/xhr/module_settings_save/' + module_name,
      { settings: JSON.stringify(settings) },
      function(data) {
        module.replaceWith(data);
        init_modules();

        if (module_name == 'server_settings') {
          get_module('recently_added');
          get_module('recently_added_movies');
        }
      }
    );
  });

  // cancel settings

  $(document).on('click', '.edit_settings .choices .cancel', function() {
    var module = $(this).closest('.module, .inactive_module, .placeholder');

    $.get('/xhr/module_settings_cancel/' + module.data('module'), function(data) {
      module.replaceWith(data);
      init_modules();
    });
  });

  // add/edit application

  $(document).on('click', '#add_application', function() {
    $.get('/xhr/add_application_dialog', function(data) {
      var popup = $(data);
      $('body').append(popup);
      popup.showPopup({ dispose: true });
    });
  });

  $(document).on('click', '.f_settings_mode #applications li a', function() {
    $.get('/xhr/edit_application_dialog/' + $(this).data('id'), function(data) {
      var popup = $(data);
      $('body').append(popup);
      popup.showPopup({ dispose: true });
    });
    return false;
  });

  $(document).on('click', '#add_edit_application_dialog .choices .save', function() {
    var form = $('#add_edit_application_dialog form');

    if (!validate_form(form)) {
      return false;
    }

    var settings = form.serialize();
    $.post('/xhr/add_edit_application', settings, function(data) {
      if (!data.status) {
        $('#applications').replaceWith(data);
        $('#add_edit_application_dialog .close').click();
      }
    });
  });

  $(document).on('click', '#add_edit_application_dialog .choices .delete', function() {
    var application_id = $('#add_edit_application_dialog input[name=application_id]').val();
    $.post('/xhr/delete_application/' + application_id, {}, function(data) {
      if (!data.status) {
        $('#applications').replaceWith(data);
        $('#add_edit_application_dialog .close').click();
      }
    });
  });

  // add/edit disk

  $(document).on('click', '#add_disk', function() {
    $.get('/xhr/add_disk_dialog', function(data) {
      var popup = $(data);
      $('body').append(popup);
      popup.showPopup({ dispose: true });
    });
  });

  $(document).on('click', '.f_settings_mode #diskspace li', function() {
    $.get('/xhr/edit_disk_dialog/' + $(this).data('id'), function(data) {
      var popup = $(data);
      $('body').append(popup);
      popup.showPopup({ dispose: true });
    });
    return false;
  });

  $(document).on('click', '#add_edit_disk_dialog .choices .save', function() {
    var form = $('#add_edit_disk_dialog form');

    if (!validate_form(form)) {
      return false;
    }

    var settings = form.serialize();
    $.post('/xhr/add_edit_disk', settings, function(data) {
      if (!data.status) {
        $('#diskspace').replaceWith(data);
        $('#add_edit_disk_dialog .close').click();

      } else {
        $('#add_edit_disk_dialog label[for=id_disk_path]').html('Path (required) <span class="invalid">(invalid)</span>');
      }
    });
  });

  $(document).on('click', '#add_edit_disk_dialog .choices .delete', function() {
    var disk_id = $('#add_edit_disk_dialog input[name=disk_id]').val();
    $.post('/xhr/delete_disk/' + disk_id, {}, function(data) {
      if (!data.status) {
        $('#diskspace').replaceWith(data);
        $('#add_edit_disk_dialog .close').click();
      }
    });
  });

});
