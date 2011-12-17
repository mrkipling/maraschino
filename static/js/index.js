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

  // update video library control

  $('#library #video-update').live('click', function() {
    $.get('/xhr/controls/update_video');
  });

  // clean video library control

  $('#library #video-clean').live('click', function() {
    $.get('/xhr/controls/clean_video');
  });

  // xbmc poweron

  $('#library #poweron').live('click', function() {
    $.get('/xhr/controls/poweron');
  });

  // xbmc poweroff

  $('#library #poweroff').live('click', function() {
    $.get('/xhr/controls/poweroff');
  });

  // xbmc reboot

  $('#library #eboot').live('click', function() {
    $.get('/xhr/controls/reboot');
  });

  // xbmc suspend

  $('#library #suspend').live('click', function() {
    $.get('/xhr/controls/suspend');
  });

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
      params: [$('#recently_added').data('episode_offset') + $('#recently_added .episodes > li').length]
    });
    return false;
  });

  $('#recently_added .view_newer').live('click', function() {
    get_module('recently_added', {
      params: [$('#recently_added').data('episode_offset') - $('#recently_added .episodes > li').length]
    });
    return false;
  });

  // view more recently added movies

  $('#recently_added_movies .view_older').live('click', function() {
    get_module('recently_added_movies', {
      params: [$('#recently_added_movies').data('movie_offset') + $('#recently_added_movies .movies > li').length]
    });
    return false;
  });

  $('#recently_added_movies .view_newer').live('click', function() {
    get_module('recently_added_movies', {
      params: [$('#recently_added_movies').data('movie_offset') - $('#recently_added_movies .movies > li'). length]
    });
    return false;
  });

  // play recently added episodes when clicking on them

  $('#recently_added .episodes li').live('click', function() {
    $.get('/xhr/play_video/episode/' + $(this).data('episodeid'));
  });

  // play recently added episodes when clicking on them

  $('#recently_added .movies li').live('click', function() {
    $.get('/xhr/play_video/movie/' + $(this).data('movieid'));
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

    $.get('/xhr/play_video/episode/' + $(this).data('episodeid'), function() {
      remove_loading_gif(li);
    });
  });

  $('#library li.play_movie').live('click', function() {
    var li = this;
    add_loading_gif(li);

    $.get('/xhr/play_video/movie/' + $(this).data('movieid'), function() {
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





  /*** SICKBEARD ***/

  // Search Episode Functionality on Magnifying Glass png

  $('#sickbeard div.options img.search').live('click', function(){
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
	alert('Could not reach Sick-Beard.');
      });
  });

  // Air time on hover

  $('#sickbeard .coming_ep').live('hover', function(){
    var id = ($(this).attr('id'));
    $('#sickbeard #'+id+' .details').toggle(200);
  });

  // Plot display function

  $('#sickbeard .coming_ep .details .plot-title').live('mouseenter', function(){
    $(this).toggle();
    var id = $(this).closest('div.coming_ep').attr('id');
    $('#sickbeard #'+id+' .details .plot').toggle();
  });

  // Plot hide function

  $('#sickbeard .coming_ep .details .plot').live('mouseleave', function(){
    var id = $(this).closest('div.coming_ep').attr('id');
    $('#sickbeard #'+id+' .details .plot-title').toggle();
    $('#sickbeard #'+id+' .details .plot').toggle();
  });

  // Toggle missed episodes

  $('#sickbeard #missed').live('click', function(){
    $('#sickbeard .missed').toggle();
  });

  // All Shows menu

  $('body').delegate('#sickbeard .menu .all', 'click', function(){
    $.get('/sickbeard/get_all', function(data){
      var content = $(data);
      $('#sickbeard #content').html(content.find('#content').html());
    });
  });

  // Coming episodes Menu

  $('body').delegate('#sickbeard .menu .upcoming', 'click', function(){
    $.get('/xhr/sickbeard', function(data){
      var content = $(data);
      $('#sickbeard #content').html(content.find('#content').html());
    });
  });

  // History menu

  $('#sickbeard .menu .history').live('click', function(){
    $.get('/sickbeard/history/30', function(data){
      $('#sickbeard').html($(data).html());
    });
  });

  $('#sickbeard .history ul.toggle').live('click', function(){
    $('#sickbeard .history .Snatched').toggle();
  });

  // Show Menu

  $('body').delegate('#sickbeard .menu-icon', 'click', function(){
    $('#sickbeard .menu').toggle(200);
  });

  // Show info

  $('body').delegate('#sickbeard #sickbeard-list ul', 'click', function(){
    var id = $(this).attr('id');
    $.get('/sickbeard/get_show_info/'+id, function(data){
      $('#sickbeard #content').html($(data).find('#content').html());
    });
  });

  // History Extra Details

  $('#sickbeard .history ul').live({
    mouseenter: function(){
      var id = $(this).attr('id');
      $('#sickbeard .history #'+id+' .extra-info').toggle();
    },
    mouseleave: function(){
      var id = $(this).attr('id');
      $('#sickbeard .history #'+id+' .extra-info').toggle();
    }
  });

  // Episode list back button functionality

  $('body').delegate('#sickbeard #content >#show .sb-back', 'click', function(){
    $.get('/sickbeard/get_all', function(data){
      var content = $(data);
      $('#sickbeard #content').html(content.find('#content').html());
    });
  });

  // Season info

  $('#sickbeard #content >#show ul.seasons li').live('click', function(){
    $.get('/sickbeard/get_season/'+$(this).attr('tvdbid')+'/'+$(this).attr('season'), function(data){
      $('#sickbeard').html($(data).html());
      $('#sickbeard .episode-list .tablesorter').tablesorter({sortList: [[0,0]]});
    });
  });

  // Going into episode info

  $('#sickbeard .episode-list #season tbody tr').live('click', function(){
    $.get('/sickbeard/get_ep_info/'+$(this).attr('link'), function(data){
      $('#sickbeard').html($(data).html());
    });
  });

  // Episode info back button functionality

  $('body').delegate('#sickbeard .episode-info .back', 'click', function(){
    $.get('/sickbeard/get_season/'+$(this).attr('tvdbid')+'/'+$(this).attr('season'), function(data){
      $('#sickbeard').html($(data).html());
      $('#sickbeard .episode-list .tablesorter').tablesorter({sortList: [[0,0]]});
    });
  });

  // Back Button Episode List

  $('#sickbeard .episode-list >.back').live('click', function(){
    $.get('/sickbeard/get_show_info/'+$(this).attr('tvdbid'), function(data){
      $('#sickbeard').html($(data).html());
    });
  });

  /******  END SICKBEARD Functions  *******/





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

  // sortable modules

  $('ul.modules').sortable({
    connectWith: 'ul.modules',
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

  $('#settings_icon').live('click', function() {
    $('body').toggleClass('f_settings_mode');
    $('body').toggleClass('f_operation_mode');
    $('#tutorial').remove();

    if ($('body').hasClass('f_settings_mode')) {
      $('ul.modules').sortable({ disabled: false });
      $.get('/xhr/server_settings_dialog', function(data) {
        var existing_server_settings = $('#server_settings').closest('li');

        if (existing_server_settings.length === 0) {
          var existing_server_settings = $('#col1 ul.modules').prepend('<li>').find('> li:first-child');
        }

        existing_server_settings.empty().append(data);
      });

    } else {
      $('ul.modules').sortable({ disabled: true });
      $('.edit_settings .choices .cancel').click();
      $('#server_settings').closest('li').remove();
    }
  });

  // add module

  $('.add_module').live('click', function() {
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
      $('#col' + column).find('ul.modules').append('<li>' + data + '</li>');
      init_modules();
      $('#add_module_dialog').fadeOut(300, function() {
        $(this).find('.close').click();
      });
    });
  });

  // remove module

  $('.module_remove').live('click', function() {
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

  $('.module_settings').live('click', function() {
    var module = $(this).closest('.module, .inactive_module, .placeholder');

    $.get('/xhr/module_settings_dialog/' + module.data('module'), function(data) {
      module.replaceWith(data);
    });
  });

  // save settings

  $('.edit_settings .choices .save').live('click', function() {
    var module = $(this).closest('.module, .inactive_module, .placeholder');
    var module_name = module.data('module');
    var settings = module.find('form').serializeArray();

    $.post('/xhr/module_settings_save/' + module_name,
      { settings: JSON.stringify(settings) },
      function(data) {
        module.replaceWith(data);
        init_modules();

        if (module_name == 'server_settings') {
          get_module('recently_added');
        }
      }
    );
  });

  // cancel settings

  $('.edit_settings .choices .cancel').live('click', function() {
    var module = $(this).closest('.module, .inactive_module, .placeholder');

    $.get('/xhr/module_settings_cancel/' + module.data('module'), function(data) {
      module.replaceWith(data);
      init_modules();
    });
  });

  // add/edit application

  $('#add_application').live('click', function() {
    $.get('/xhr/add_application_dialog', function(data) {
      var popup = $(data);
      $('body').append(popup);
      popup.showPopup({ dispose: true });
    });
  });

  $('.f_settings_mode #applications li a').live('click', function() {
    $.get('/xhr/edit_application_dialog/' + $(this).data('id'), function(data) {
      var popup = $(data);
      $('body').append(popup);
      popup.showPopup({ dispose: true });
    });
    return false;
  });

  $('#add_edit_application_dialog .choices .save').live('click', function() {
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

  $('#add_edit_application_dialog .choices .delete').live('click', function() {
    var application_id = $('#add_edit_application_dialog input[name=application_id]').val();
    $.post('/xhr/delete_application/' + application_id, {}, function(data) {
      if (!data.status) {
        $('#applications').replaceWith(data);
        $('#add_edit_application_dialog .close').click();
      }
    });
  });

  // add/edit disk

  $('#add_disk').live('click', function() {
    $.get('/xhr/add_disk_dialog', function(data) {
      var popup = $(data);
      $('body').append(popup);
      popup.showPopup({ dispose: true });
    });
  });

  $('.f_settings_mode #diskspace li').live('click', function() {
    $.get('/xhr/edit_disk_dialog/' + $(this).data('id'), function(data) {
      var popup = $(data);
      $('body').append(popup);
      popup.showPopup({ dispose: true });
    });
    return false;
  });

  $('#add_edit_disk_dialog .choices .save').live('click', function() {
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

  $('#add_edit_disk_dialog .choices .delete').live('click', function() {
    var disk_id = $('#add_edit_disk_dialog input[name=disk_id]').val();
    $.post('/xhr/delete_disk/' + disk_id, {}, function(data) {
      if (!data.status) {
        $('#diskspace').replaceWith(data);
        $('#add_edit_disk_dialog .close').click();
      }
    });
  });

});
