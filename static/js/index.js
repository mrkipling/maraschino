$(document).ready(function() {

  // get/poll module

  function get_module(module, customsettings) {
    var settings = {
      poll: 'None',
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
    if (settings.poll !== 'None') {
      setTimeout(function() {
        get_module(module, {
          poll: settings.poll
        })
      }, settings.poll * 1000);
    }
  }

  // initialise modules on page load

  $('.placeholder').each(function() {
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
          $(this).replaceWith('<div id="synopsis_inactive"></div>');
        });

        // hide trakt module if visible
        $('#trakt').fadeOut(200, function() {
          $(this).replaceWith('<div id="trakt_inactive"></div>');
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
            var module = $('<div id="synopsis" class="module generic"><h2></h2><div class="inner"><p></p></div></div>');
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
                $(this).replaceWith('<div id="synopsis"></div>');
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

  if ($('body').data('show_currently_playing') === 'True') {
    get_currently_playing();
  }

  // play/pause control

  $('#currently_playing .controls .play_pause').live('click', function() {
    $.get('/xhr/controls/play_pause');
  });

  // stop control

  $('#currently_playing .controls .stop').live('click', function() {
    $.get('/xhr/controls/stop');
  });

  // click show name to view in media library module

  $('#currently_playing .item_info .show').live('click', function() {
    invoke_library('/xhr/library/shows/' + $(this).data('show'));
  });

  // click show season to view in media library module

  $('#currently_playing .item_info .season').live('click', function() {
    invoke_library('/xhr/library/shows/' + $(this).parent().find('.show').data('show') + '/' + $(this).data('season'));
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

  // post trakt shout

  $('#add_shout .submit').live('click', function() {
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

  $('#recently_added .view_older').live('click', function() {
    get_module('recently_added', {
      params: [$('#recently_added').data('offset') + $('#recently_added .episodes > li').length]
    });
    return false;
  });

  $('#recently_added .view_newer').live('click', function() {
    get_module('recently_added', {
      params: [$('#recently_added').data('offset') - $('#recently_added .episodes > li').length]
    });
    return false;
  });

  // play recently added episodes when clicking on them

  $('#recently_added li').live('click', function() {
    $.get('/xhr/play_episode/' + $(this).data('episodeid'));
  });

  // browse library

  $('#library li.get').live('click', function() {
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

  $('#library li.play_episode').live('click', function() {
    var li = this;
    add_loading_gif(li);

    $.get('/xhr/play_episode/' + $(this).data('episodeid'), function() {
      remove_loading_gif(li);
    });
  });

  $('#library li.play_movie').live('click', function() {
    var li = this;
    add_loading_gif(li);

    $.get('/xhr/play_movie/' + $(this).data('movieid'), function() {
      remove_loading_gif(li);
    });
  });

  $('#library .back').live('click', function() {
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

  function add_loading_gif(element) {
    $(element).append('<img src="/static/images/xhrloading.gif" class="xhrloading" width="18" height="15" alt="Loading...">');
  }

  function remove_loading_gif(element) {
    $(element).find('.xhrloading').remove();
  }

  // generic expand truncated text

  $('.expand').live('click', function() {
    var parent = $(this).parent();
    parent.find('.truncated').hide();
    parent.find('.expanded').show();
    $(this).hide();
    return false;
  });

  // settings mode

  $('#settings_icon').live('click', function() {
    $('body').toggleClass('f_settings_mode');
  });

  // add module

  $('.add_module').live('click', function() {
    var column = $(this).closest('.col').attr('id');
    $.get('/xhr/add_module_dialog', function(data) {
      var popup = $(data);
      $('body').append(popup);
      popup.data('col', column.replace('col', ''));
      popup.showPopup({ dispose: true });
    });
  });

  $('#add_module_dialog #select_module').live('change', function() {
    var module_description = $('#add_module_dialog .description');
    if (module_description.length === 0) {
      $('#add_module_dialog #select_module').after('<p class="description">');
      module_description = $('#add_module_dialog .description');
    }
    module_description.text($(this).find(':selected').data('description'));
  });

  $('#add_module_dialog .submit').live('click', function() {
    var module_id = $('#add_module_dialog #select_module :selected').val();
    var column = $('#add_module_dialog').data('col');
    var position = $('#col' + column).find('.module, .placeholder').length + 1;

    $.post('/xhr/add_module', {
      module_id: module_id,
      column: column,
      position: position
    }, function(data) {
      console.info(data.status);
      $('#add_module_dialog').fadeOut(300, function() {
        $(this).find('.close').click();
      });
    });
  });

});