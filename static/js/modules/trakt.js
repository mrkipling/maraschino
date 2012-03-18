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
