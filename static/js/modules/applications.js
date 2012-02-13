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
