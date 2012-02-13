$(document).ready(function() {

  init_modules();

  // Settings tab
  $(document).on('click', '#server_settings .tab', function(){
    if($('#server_settings .inner').css('display') == 'none'){
      $('#server_settings .inner').slideDown();
    } else {
      $('#server_settings .inner').slideUp();
    }
  });

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
          get_module('recently_added_albums');
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
});


//// END DOCUMENT READY \\\\
// anything below this can be classified as a "global" function and can be acessed by the other js files \\
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

function add_loading_gif(element) {
  $(element).append('<img src="/static/images/xhrloading.gif" class="xhrloading" width="18" height="15" alt="Loading...">');
}

function remove_loading_gif(element) {
  $(element).find('.xhrloading').remove();
}
