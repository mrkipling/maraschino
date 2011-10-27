$(document).ready(function() {

  // get/poll module

  function get_module(module, poll) {
    $.get('/xhr/' + module, function(data) {
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
        $('.placeholder[data-module=' + module + ']').replaceWith(new_module);
        $('.module[data-module=' + module + ']').fadeIn(200);
      }
    });

    // poll
    if (poll !== 'None') {
      setTimeout(function() { get_module(module, poll) }, poll * 1000);
    }
  }

  // initialise modules on page load

  $('.placeholder').each(function() {
    var delay = $(this).data('delay');
    if (delay === undefined) {
      get_module($(this).data('module'), $(this).data('poll'));
    } else {
      var module = $(this).data('module');
      var poll = $(this).data('poll');
      setTimeout(function() { get_module(module, poll) }, delay * 1000);
    }
  });

  // currently playing

  function get_currently_playing() {
    $.get('/xhr/currently_playing', function(data) {

      if (data.playing === false) {

        // hide currently playing
        $('#currently_playing').slideUp(200, function() {
          $(this).remove();
        });

        // hide synopsis module if visible
        $('#synopsis.module').fadeOut(200, function() {
          $(this).replaceWith('<div id="synopsis"></div>');
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
        var synopsis_module = $('#synopsis');
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

        }

      }
    });

    setTimeout(get_currently_playing, 5000);
  }

  if ($('body').data('show_currently_playing') === 'True') {
    get_currently_playing();
  }

  // play recently added episodes when clicking on them

  $('#recently_added li').live('click', function() {
    $.get('/xhr/play_episode/' + $(this).data('episodeid'));
  });

  // generic expand truncated text

  $('.expand').live('click', function() {
    var parent = $(this).parent();
    parent.find('.truncated').hide();
    parent.find('.expanded').show();
    $(this).hide();
    return false;
  });

});