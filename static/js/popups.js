/*global
  jQuery
  $
*/

// blank screen

jQuery.blankScreen = function(settings)
{
  var blank_screen = {
    clear: false,
    color: '#000',
    opacity: 0.75
  };

  if (settings !== undefined) { jQuery.extend(blank_screen, settings); }

  if (blank_screen.clear) {
    jQuery('#dimmer').remove();
  } else {
    var dimmer = jQuery('#dimmer').eq(0);
    if (dimmer.length === 0) {
      dimmer = $('<div id="dimmer"></div>');
    }
    dimmer.css({
      'top': '0',
      'right': '0',
      'bottom': '0',
      'left': '0',
      'z-index': '1000',
      'position': 'fixed',
      'background-color': blank_screen.color,
      'opacity': blank_screen.opacity,
      'filter': 'alpha(opacity=' + blank_screen.opacity * 100 + ')'
    });
    jQuery('body').append(dimmer);
  }
};

// show popup

jQuery.fn.showPopup = function(settings)
{
  var popup = this.eq(0);

  var pop = {
    blank_screen: true,
    dispose: false,

    done: function () {
      if (pop.blank_screen) { jQuery.blankScreen({ 'clear': true }); }
      if (pop.dispose) {
        popup.remove();
      } else {
        popup.hide();
      }
    },

    close_selector: '.title .close, .choices .cancel',
    on_close: function() {},
    close: function() {
      pop.done();
      pop.on_close();
      return false;
    },

    confirm_selector: '.choices .confirm',
    on_confirm: function () {},
    confirm: function() {
      pop.done();
      pop.on_confirm();
      return false;
    }
  };

  if (settings !== undefined) { jQuery.extend(pop, settings); }

  popup.find('> .close').click(function() {
    $(this).parent().closePopup();
  });

  if (pop.blank_screen) { jQuery.blankScreen(); }
  popup.show();

  popup.css({
    'position': 'absolute',
    'z-index': '1001',
    'left': Math.ceil((jQuery("body").eq(0).width() / 2) - (popup.width() / 2))
  });
  popup.centerVertically();

  if (!pop.dispose) { popup.get(0).style.display = ''; }

  popup.unbind('click.auto_popup').bind('click.auto_popup', function (e) {
    var el = $(e.target);
    if (el.is(pop.close_selector)) {
      pop.close();
      return false;
    } else if (el.is(pop.confirm_selector)) {
      pop.confirm();
      return false;
    }
  });

  popup.data('popup_info', pop);
  return popup;
};

// close popup

jQuery.fn.closePopup = function()
{
  if (this.length === 0) {
    return this;
  }

  var popup = this.eq(0);
  var pop = popup.data('popup_info');

  if (pop === undefined) {
    throw {
      name: 'ValueError',
      message: popup + ' is not a popup (it did not have showPopup called on it).'
    };
  }

  pop.close();

  if (popup.hasClass('dispose')) {
    popup.remove();
  }

  return popup;
};

// center on

jQuery.fn.centerOn = function (x, y) {
  var me = $(this);
  var args = {};
  if (x !== null && typeof x !== 'undefined') {
    args.left = x - (me.width() / 2);
  }
  if (y !== null && typeof y !== 'undefined') {
    args.top = y - (me.height() / 2);
  }
  me.css(args);
  return me;
};

// center vertically

jQuery.fn.centerVertically = function() {
  return $(this).centerOn(null, (jQuery(window).height() / 2) + $(window).scrollTop());
};