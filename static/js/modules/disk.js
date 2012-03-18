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
